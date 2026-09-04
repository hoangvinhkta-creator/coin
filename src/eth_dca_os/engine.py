"""Simulation engine — vòng lặp 15m theo ĐÚNG processing order 18 bước (Backtest §19).

Đơn vị danh nghĩa 1 USDT = 1 đơn vị (Backtest §2.1 [F6]). Các quy ước triển khai
cho những điểm spec để ngỏ: docs/CONVENTIONS.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
import pandas as pd

from .capital import (
    BASE_SCHEDULE,
    BaseScheduleState,
    MonthlyCapital,
    OpportunityHysteresis,
    Pool,
    SmartUnlockState,
    apply_monthly_contribution,
    opportunity_reservable,
    smart_reservable,
)
from .execution import MISSED, apply_fill, behavioral_delay_seconds, total_delay_seconds
from .ladders import (
    Ladder,
    create_crash_ladder,
    create_opportunity_ladder,
    create_smart_ladder,
    opportunity_spacing,
    smart_spacing,
    update_bullish_invalidation,
)
from .regime import RegimeTracker
from .score import opportunity_unlock, smart_unlock

TZ_OFFSET = 7 * 3600  # Asia/Ho_Chi_Minh, không DST
NOON = 12 * 3600
DAY = 86400.0
CANDLE = 900.0                  # một nến execution 15m, tính bằng giây

# Thứ tự pool §15.1 [F2]: Base -> Smart -> Opportunity
_POOL_RANK = {"BASE": 0, "SMART": 1, "OPPORTUNITY": 2}


# ------------------------------------------------------------- Execution State (WP-C2)

class ExecutionState(StrEnum):
    """Sáu Execution State canonical của Strategy §16/§19 — MỘT chiều duy nhất.

    Đây là VỐN TỪ VỰNG, không phải một máy trạng thái mới: engine không thêm biến trạng
    thái nào, không đổi một nhánh execution nào. Chiều này được DẪN XUẤT từ các nguồn sự
    thật đã có (`Zone.status`, `in_cooldown`, `data_quality`) tại một điểm đo cố định
    trong chu kỳ 15m — xem `derive_execution_state` và `docs/CONVENTIONS.md` #22.

    Chiều này ĐỘC LẬP với Market Regime (`NORMAL/STRESSED/CRASH/RECOVERY`, thuộc WP-A3):
    ST §16 đòi hai chiều "phải được lưu riêng", nên không giá trị nào ở đây mang nhãn
    regime và không nhánh regime nào đọc giá trị ở đây.

    `StrEnum` để giá trị VỪA là hằng có kiểu (không gõ nhầm được) VỪA là `str` thuần khi
    serialize — `WP-B3` tiêu thụ trực tiếp cho `previous_state`/`new_state` (DM §11) mà
    không phải định nghĩa một enum thứ hai.
    """

    WAIT = "WAIT"
    FUNDING_REQUIRED = "FUNDING_REQUIRED"
    READY_TO_BUY = "READY_TO_BUY"
    ACTION_PENDING = "ACTION_PENDING"
    COOLDOWN = "COOLDOWN"
    DATA_BLOCKED = "DATA_BLOCKED"


#: `ADR-001` (Accepted 2026-09-04, `DEC-035`): ở TẦNG BACKTEST `FUNDING_REQUIRED` là
#: `NOT_APPLICABLE` — engine KHÔNG mô hình hoá số dư USDT treasury, và `funding_delay` là
#: hàm tất định của `funding_policy` (`docs/CONVENTIONS.md` #8), nên không tồn tại nhánh
#: "treasury có đủ không" để trạng thái này phát sinh. Trạng thái vẫn nằm trong enum vì
#: Product Spec §6/§7/§11 bắt buộc nó ở TẦNG APP — tuyên bố NOT_APPLICABLE là tường minh,
#: không phải vắng mặt im lặng (`CHECK-C2-03`).
BACKTEST_NOT_APPLICABLE_STATES = (ExecutionState.FUNDING_REQUIRED,)


def derive_execution_state(*, action_due: bool, action_open: bool, data_invalid: bool,
                           cooldown_blocking: bool) -> ExecutionState:
    """Hợp nhất bốn dữ kiện ĐÃ CÓ của một nến thành đúng một Execution State.

    Bốn đầu vào đều là quan sát, không phải trạng thái mới:

    - `action_due`      — bước 12 xác định có action tới hạn và còn TTL (`ts >= execute_at`);
    - `action_open`     — còn zone `ACTION_PENDING` chưa tới hạn và chưa hết TTL;
    - `data_invalid`    — `data_quality == "INVALID"` của bước 8 (ST §3);
    - `cooldown_blocking` — bước 11: đang trong cooldown và override KHÔNG kích hoạt.

    Thứ tự ưu tiên lấy ĐÚNG theo hành vi engine, không phải theo thẩm mỹ:

    1. `READY_TO_BUY` / 2. `ACTION_PENDING` — hai trạng thái này mô tả một action ĐÃ TỒN
       TẠI. Bước 12 và 16–17 KHÔNG đọc `dq` cũng không đọc `in_cooldown`, nên một action
       đã tạo vẫn fill kể cả khi dữ liệu INVALID hoặc đang cooldown; vì vậy khi có action
       mở thì chính nó LÀ trạng thái thực thi.
    3. `DATA_BLOCKED` / 4. `COOLDOWN` — hai trạng thái này mô tả vì sao không tạo được
       action MỚI. Bước 14c kiểm `dq != "INVALID"` TRƯỚC rồi mới kiểm cooldown, nên
       DATA_BLOCKED đứng trước COOLDOWN — đây là thứ tự của chính engine.
    5. `WAIT` — không có điều kiện thực thi nào đang hiệu lực.

    Hàm thuần: không đọc và không ghi state nào của engine, nên không thể đổi hành vi.
    """
    if action_due:
        return ExecutionState.READY_TO_BUY
    if action_open:
        return ExecutionState.ACTION_PENDING
    if data_invalid:
        return ExecutionState.DATA_BLOCKED
    if cooldown_blocking:
        return ExecutionState.COOLDOWN
    return ExecutionState.WAIT


# --------------------------------------------------- Audit trail / decision_log (WP-B3)

#: Ánh xạ TẤT ĐỊNH `reason_code` (Strategy §20) -> `trigger_type` (Data Model §11).
#: Đây là một BẢNG TRA, không phải một lớp chính sách mới: mỗi mã ST §20 thuộc đúng một
#: nhóm nguyên nhân trong bảy giá trị DM §11 cho phép. `WP-B3` KHÔNG phát minh mã mới —
#: `test_b3_03_reason_code_catalogue_matches_the_spec_text` đối chiếu tập khoá của bảng
#: này với chính văn bản `docs/spec/02_STRATEGY_SPEC_V2_1_5.md` §20.
TRIGGER_TYPE_BY_REASON: dict[str, str] = {
    **{c: "base" for c in ("BASE_SCHEDULE", "BASE_ADVANCE_SCORE")},
    **{c: "month_end" for c in ("MONTH_END_BASE", "MONTH_END_SMART",
                                "CAP_OVERFLOW_TO_SMART")},
    **{c: "zone" for c in (*(f"SMART_ZONE_S{i}" for i in range(3)),
                           *(f"OPPORTUNITY_O{i}" for i in range(5)),
                           *(f"CRASH_ZONE_C{i}" for i in range(4)),
                           "DAILY_LIMIT_BLOCK", "MAX_ZONES_BLOCK", "PARTIAL_FILL",
                           "ACTION_TTL_EXPIRED", "ACTION_MISSED",
                           "BULLISH_INVALIDATION", "LADDER_EXPIRED",
                           "OPPORTUNITY_SUSPENDED")},
    **{c: "regime" for c in ("CRASH_ENTRY_7D", "CRASH_ENTRY_24H", "CRASH_EXIT",
                             "RECOVERY_END")},
    **{c: "cooldown" for c in ("COOLDOWN_START", "COOLDOWN_OVERRIDE")},
    **{c: "funding" for c in ("FUNDING_REQUIRED", "FUNDING_COMPLETE")},
    **{c: "data" for c in ("DATA_DEGRADED", "DATA_INVALID", "DELAYED_DATA_FILL")},
}

#: Danh mục reason code ST §20 — dẫn xuất từ đúng MỘT nguồn ở trên, không chép lại lần hai.
STRATEGY_REASON_CODES = tuple(TRIGGER_TYPE_BY_REASON)

#: Bảy `trigger_type` của DM §11 — không hơn.
TRIGGER_TYPES = ("zone", "base", "regime", "funding", "cooldown", "month_end", "data")

#: Trường của MỘT bản ghi `decision_log`, đúng theo Data Model §11 (`tags` là phần mở rộng
#: mang NHÃN của ST §9/BT §18 — xem `docs/CONVENTIONS.md` #23).
DECISION_LOG_FIELDS = (
    "decision_id", "timestamp_utc", "previous_state", "new_state",
    "market_regime", "data_quality", "trigger_type", "reason_code",
    "opportunity_score", "recommended_price", "recommended_vnd", "recommended_usdt_est",
    "zone_id", "ladder_id", "available_vnd", "reserved_vnd", "deployed_vnd",
    "strategy_config_hash", "execution_config_hash", "tags",
)

#: Trường mà DM §11 đánh dấu "Bắt buộc" / "Snapshot bắt buộc" — KHÔNG được null.
DECISION_LOG_NOT_NULL_FIELDS = (
    "decision_id", "timestamp_utc", "market_regime", "data_quality", "trigger_type",
    "reason_code", "available_vnd", "reserved_vnd", "deployed_vnd",
    "strategy_config_hash", "execution_config_hash",
)

#: Mã ST §20 mà TẦNG BACKTEST không bao giờ ghi, kèm lý do canonical (`CHECK-B3-03`).
#: Tuyên bố tường minh, không phải vắng mặt im lặng — cùng khuôn với
#: `BACKTEST_NOT_APPLICABLE_STATES` của WP-C2.
BACKTEST_NOT_EMITTED_REASONS = {
    "FUNDING_REQUIRED": "ADR-001 (DEC-035): engine không mô hình hoá số dư USDT treasury; "
                        "funding_delay là hàm tất định của funding_policy (CONVENTIONS #8). "
                        "Trạng thái/mã này chỉ tồn tại ở TẦNG APP (Product Spec §6/§7/§11).",
    "FUNDING_COMPLETE": "ADR-001 (DEC-035): mặt còn lại của FUNDING_REQUIRED — không có "
                        "nhánh funding động nào ở tầng backtest để hoàn tất.",
    "PARTIAL_FILL": "Engine backtest fill NGUYÊN ZONE (execution.apply_fill); partial fill "
                    "thuộc WP-C3 và chưa có hành vi để ghi.",
}

#: Mã ST §20 được ghi dưới dạng NHÃN trên bản ghi (`tags`) chứ không phải một `reason_code`
#: độc lập: nó là phẩm chất của một quyết định khác, không phải một sự kiện nghiệp vụ riêng.
REASON_CODES_RECORDED_AS_TAG = ("DELAYED_DATA_FILL",)

#: Nhãn audit dùng trên `decision_log.tags`. `EXECUTED_EARLY` là yêu cầu ST §9 ("phải đánh
#: dấu"), hai nhãn còn lại là nhãn chất lượng dữ liệu BT §18 đã có trên purchase record.
AUDIT_TAGS = ("EXECUTED_EARLY", "DELAYED_DATA_FILL", "EXECUTION_DATA_GAP")


def zone_reason_code(ladder_type: str, zone_index: int) -> str:
    """Mã reason ST §20 của một zone — CÙNG vốn từ vựng mà ledger `Pool._log` đang ghi."""
    return {"SMART": "SMART_ZONE_S", "OPPORTUNITY": "OPPORTUNITY_O",
            "CRASH": "CRASH_ZONE_C"}[ladder_type] + str(zone_index)


def zone_order_key(zone, ladder) -> tuple:
    """Khoá sắp thứ tự thực thi khi nhiều zone cùng trigger — Strategy §15.1 [F2].

    1. Giữa các pool: Base -> Smart -> Opportunity; Crash ladder xếp theo pool
       NGUỒN VỐN của nó (zone.pool phản ánh nguồn vốn thật — xem CONVENTIONS #16),
       và SAU các ladder Smart/Opportunity thường cùng pool.
    2. Trong cùng pool: ladder có created_at sớm hơn xử lý trước.
    3. Trong cùng ladder: zone_index tăng dần.
    max_zones_per_cycle áp SAU khi đã sắp thứ tự này.
    """
    return (_POOL_RANK.get(zone.pool, 3),
            1 if ladder.type == "CRASH" else 0,
            ladder.created_at,
            zone.zone_index)


@dataclass
class RunResult:
    purchases: list = field(default_factory=list)
    contributions: list = field(default_factory=list)
    counters: dict = field(default_factory=dict)
    monthly_deployments: dict = field(default_factory=dict)  # "YYYY-MM" -> nominal deployed
    cash_samples: list = field(default_factory=list)          # (ts, cash, eth)
    # WP-B3 (đóng F-024, F-033) — AUDIT TRAIL canonical theo Data Model §11. MỘT bản ghi
    # cho MỘT sự kiện nghiệp vụ thật của engine, mang đủ trường DM §11 (`DECISION_LOG_FIELDS`)
    # và CHỈ dùng reason code của ST §20. `previous_state`/`new_state` tiêu thụ trực tiếp
    # `ExecutionState` của WP-C2 — không có vốn từ vựng trạng thái thứ hai.
    # Đây là bề mặt QUAN SÁT: không nhánh execution nào đọc `decision_log`, nên gỡ bỏ toàn
    # bộ lớp ghi log không đổi một con số backtest nào (`CHECK-B3-07`).
    # Không còn cờ bật/tắt: audit trail của một official run không thể là tuỳ chọn
    # (`CHECK-B3-04`). Xem `docs/CONVENTIONS.md` #23.
    decision_log: list = field(default_factory=list)
    # WP-A5 (đo lường, KHÔNG đổi hành vi): hai chuỗi số liệu mà ba Failure Signal cần.
    # FS-02 (BT §17 "Opportunity reserve thường xuyên chạm cap và nằm im"): mẫu THEO NGÀY
    #   {ts, total, cap, available, at_cap, idle} — cùng nhịp với `cash_samples`.
    # FS-12 (BT §17 "lợi thế tập trung vào một crash/regime duy nhất"): mốc ĐỔI NHÃN regime
    #   (ts, label) theo BT §15 (regime labeling for analysis), để quy purchase của
    #   benchmark — vốn không mang nhãn regime — về đúng regime đang hiệu lực.
    opp_cap_samples: list = field(default_factory=list)
    regime_timeline: list = field(default_factory=list)        # (ts, label), chỉ ghi khi đổi
    # WP-C2 (đặt tên + lưu vết, KHÔNG đổi hành vi) — chiều Execution State (ST §16/§19).
    # `execution_state_timeline`: (ts, ExecutionState) ghi KHI ĐỔI, cùng khuôn với
    #   `regime_timeline`. Ghi khi đổi là KHÔNG mất mát ở độ phân giải nến: trạng thái tại
    #   một thời điểm bất kỳ = mốc gần nhất <= thời điểm đó. Đây cũng chính là hình dạng
    #   `previous_state`/`new_state` mà WP-B3 cần (DM §11) — WP-C2 chỉ cấp vốn từ vựng.
    # `market_snapshots`: một bản ghi mỗi accounting day (cùng nhịp, cùng vị trí với
    #   `cash_samples`) mang `execution_state` NOT NULL theo DM §4.
    execution_state_timeline: list = field(default_factory=list)
    market_snapshots: list = field(default_factory=list)

    @property
    def eth_total(self) -> float:
        return sum(p["eth"] for p in self.purchases)

    @property
    def contributed_total(self) -> float:
        return sum(c[1] for c in self.contributions)


def _epoch_seconds(series_or_index) -> np.ndarray:
    """Epoch seconds bất kể datetime64 unit (ns/us) của pandas."""
    vals = pd.DatetimeIndex(series_or_index)
    return ((vals - pd.Timestamp(0, tz=vals.tz)) / pd.Timedelta(seconds=1)).to_numpy(float)


def _prep_candles(eth15: pd.DataFrame, start_ts: float, end_ts: float) -> dict:
    ts = _epoch_seconds(eth15["open_time"])
    mask = (ts >= start_ts) & (ts < end_ts)
    idx0 = int(np.argmax(mask)) if mask.any() else 0
    arr = {k: eth15[k].to_numpy(float)[mask] for k in ("open", "high", "low", "close")}
    arr["ts"] = ts[mask]
    # WP-A4/A4.4 (đóng F-025) — Backtest §18: nến 15m thiếu thì KHÔNG interpolate OHLC để
    # trigger zone. Engine vốn đã không interpolate (nó chỉ duyệt các nến CÓ THẬT), nhưng
    # trước gói này không bản ghi nào cho biết mình nằm ngay sau một lỗ hổng. Đếm được
    # bao nhiêu gap mà không truy được bản ghi nào bị ảnh hưởng là đúng khiếm khuyết mà
    # §18 cấm. Tính trên chuỗi ĐẦY ĐỦ trước khi cắt cửa sổ để nến đầu cửa sổ không bị
    # gán nhãn oan.
    missing_before = np.zeros(len(ts), dtype=np.int64)
    if len(ts) > 1:
        missing_before[1:] = np.maximum(
            np.rint(np.diff(ts) / CANDLE).astype(np.int64) - 1, 0)
    arr["missing_before"] = missing_before[mask]
    # Return24H nội ngày: 96 nến 15m liền trước — cần lịch sử trước start
    full_close = eth15["close"].to_numpy(float)
    sel = np.nonzero(mask)[0]
    r24 = np.full(len(sel), np.nan)
    ok = sel >= 96
    r24[ok] = full_close[sel[ok]] / full_close[sel[ok] - 96] - 1
    arr["r24"] = r24
    return arr


def _daily_arrays(scores: pd.DataFrame) -> dict:
    day_ts = _epoch_seconds(scores.index)  # 00:00 UTC của ngày D
    return {
        "day_end_ts": day_ts + DAY,  # nến daily D đóng hoàn toàn tại thời điểm này
        "oscore": scores["oscore"].to_numpy(float),
        "dq": scores["data_quality"].to_numpy(object),
        "return7": scores["return7"].to_numpy(float),
        "adr30": scores["adr30"].to_numpy(float),
        "close": scores["close"].to_numpy(float),
    }


def run_engine(dataset: dict, scores_with_ind: pd.DataFrame, strategy_cfg, exec_cfg,
               start: pd.Timestamp, end: pd.Timestamp,
               contribution: float = 100.0,
               behavioral_rng: np.random.Generator | None = None) -> RunResult:
    """Chạy engine từ `start` tới `end` (state mới hoàn toàn — xem CONVENTIONS #12)."""
    cfg = strategy_cfg
    start_ts = start.tz_localize("UTC").timestamp() if start.tzinfo is None else start.timestamp()
    end_ts = end.tz_localize("UTC").timestamp() if end.tzinfo is None else end.timestamp()
    c = _prep_candles(dataset["ETHUSDT_15m"], start_ts, end_ts)
    d = _daily_arrays(scores_with_ind)
    n = len(c["ts"])
    res = RunResult()
    if n == 0:
        return res

    behavioral = exec_cfg.behavioral_model == "LOCAL_HOUR"
    if behavioral and behavioral_rng is None:
        behavioral_rng = np.random.default_rng(0)

    # WP-B3 — DM §11 đòi MỌI bản ghi decision tham chiếu hash của hai config snapshot
    # (DM §14 "mọi decision và run phải tham chiếu hash của chúng"). Tính ĐÚNG MỘT LẦN mỗi
    # run: `hash` là sha256 trên `asdict`, gọi lại mỗi bản ghi sẽ tốn vô ích.
    strategy_config_hash = cfg.hash
    execution_config_hash = exec_cfg.hash

    # ------------------------------------------------- state
    base_pool, smart_pool, opp_fund = Pool("BASE"), Pool("SMART"), Pool("OPPORTUNITY")
    mc = MonthlyCapital(base_pool, smart_pool, opp_fund,
                        monthly_opp_contribution=contribution * cfg.opportunity_pct,
                        opportunity_cap_months=cfg.opportunity_cap_months)
    su = SmartUnlockState(cfg.smart_unlock_mode, cfg.hwm_decay_step, cfg.hwm_decay_days)
    hyst = OpportunityHysteresis(cfg.opportunity_activate_score, cfg.opportunity_suspend_score)
    regime = RegimeTracker()
    base_state = BaseScheduleState()

    ladders: list[Ladder] = []
    reserve_map: dict[int, list] = {}     # zone_id -> [(pool, amount)]
    zone_meta: dict[int, dict] = {}       # zone_id -> {'recommended': px, 'behavioral_missed': bool}

    cur_month = None                      # (year, month) local
    cur_day_ord = None
    month_base_budget = 0.0
    month_smart_budget = 0.0
    smart_ladder_created_this_month = False
    day_flags: dict = {}                  # per-day: base noon fired, month-end fired
    daily_idx = -1
    oscore = np.nan
    dq = "INVALID"
    r7 = np.nan
    adr30 = np.nan
    last_good_opp_unlock = 0.0
    opp_used_today = 0.0
    cooldown_until = -np.inf
    last_exec_price = np.nan
    prev_state = "NORMAL"           # trạng thái NỀN trước đó ([F1]: execution không đọc nhãn)
    # WP-B3 — ngữ cảnh Execution State cho audit trail. `exec_state_now` là giá trị ĐÃ ĐO
    # gần nhất ở bước 12b (WP-C2); `state_reason` là dữ kiện ST §20 đã quyết định giá trị đó
    # (dùng làm lý do khi trạng thái đó CHẤM DỨT). Không phải nguồn sự thật mới: cả hai chỉ
    # phản chiếu `derive_execution_state`.
    exec_state_now = None
    state_reason = (None, None, None)     # (reason_code, zone_id, ladder_id)
    prev_dq = None                        # chất lượng dữ liệu của snapshot daily trước
    eth_total = 0.0
    counters = {
        "cooldown_override": {"NORMAL": 0, "STRESSED": 0, "CRASH": 0, "RECOVERY": 0},
        "triggered_actions": 0, "missed_actions": 0, "executed_actions": 0,
        "base_early": 0, "delayed_data_fill": 0, "execution_data_gap": 0,
    }
    # Nến đang xét có nằm ngay sau một lỗ hổng execution không (WP-A4/A4.4).
    gap_before_now = 0

    day_end = d["day_end_ts"]

    def log(ts, reason, *, zone_id=None, ladder_id=None, recommended_price=None,
            recommended_vnd=None, previous_state=None, new_state=None, tags=()):
        """Ghi MỘT bản ghi audit trail canonical theo Data Model §11 (WP-B3).

        Thuần QUAN SÁT: hàm chỉ ĐỌC trạng thái engine và append vào `res.decision_log`;
        không nhánh execution nào đọc lại danh sách đó. Ghi log KHÔNG có cờ bật/tắt —
        audit trail của một official run không thể là tuỳ chọn (`CHECK-B3-04`).

        `previous_state`/`new_state` mặc định là trạng thái ĐANG hiệu lực (`exec_state_now`,
        đo ở bước 12b theo WP-C2): một sự kiện không đổi trạng thái thì hai trường bằng nhau.
        Bản ghi chuyển trạng thái truyền hai giá trị khác nhau một cách tường minh.

        `recommended_vnd` = lượng vốn (đơn vị danh nghĩa) mà chính quyết định này cam kết,
        và `recommended_usdt_est` bằng nó vì backtest chạy 1 USDT = 1 đơn vị
        (BT §2.1 [F6], `docs/CONVENTIONS.md` #11).
        """
        if new_state is None:
            previous_state = new_state = exec_state_now
        res.decision_log.append({
            "decision_id": len(res.decision_log) + 1,
            "timestamp_utc": ts,
            "previous_state": previous_state,
            "new_state": new_state,
            "market_regime": regime.regime,
            "data_quality": dq,
            "trigger_type": TRIGGER_TYPE_BY_REASON[reason],
            "reason_code": reason,
            "opportunity_score": None if np.isnan(oscore) else float(oscore),
            "recommended_price": recommended_price,
            "recommended_vnd": recommended_vnd,
            "recommended_usdt_est": recommended_vnd,
            "zone_id": zone_id,
            "ladder_id": ladder_id,
            "available_vnd": base_pool.available + smart_pool.available + opp_fund.available,
            "reserved_vnd": base_pool.reserved + smart_pool.reserved + opp_fund.reserved,
            "deployed_vnd": base_pool.deployed + smart_pool.deployed + opp_fund.deployed,
            "strategy_config_hash": strategy_config_hash,
            "execution_config_hash": execution_config_hash,
            "tags": list(tags),
        })

    def state_entry_reason(state, due, opened):
        """Dữ kiện ST §20 quyết định `state`, theo ĐÚNG thứ tự ưu tiên CONVENTIONS #22(c).

        Không phát minh lý do: `READY_TO_BUY`/`ACTION_PENDING` được quyết bởi một action cụ
        thể nên mã của chúng là mã zone của action đó (`zone_order_key` — thứ tự canonical
        của chính engine, cùng khoá bước 15 dùng để sắp fill); hai trạng thái còn lại được
        quyết bởi một điều kiện có sẵn mã ST §20.
        """
        if state is ExecutionState.READY_TO_BUY and due:
            z, lad = min(due, key=lambda p: zone_order_key(p[0], p[1]))
            return zone_reason_code(lad.type, z.zone_index), z.zone_id, lad.ladder_id
        if state is ExecutionState.ACTION_PENDING and opened:
            z, lad = min(opened, key=lambda p: zone_order_key(p[0], p[1]))
            return zone_reason_code(lad.type, z.zone_index), z.zone_id, lad.ladder_id
        if state is ExecutionState.DATA_BLOCKED:
            return "DATA_INVALID", None, None
        if state is ExecutionState.COOLDOWN:
            return "COOLDOWN_START", None, None
        return (None, None, None)

    def record_purchase(ts, source, nominal, open_price, reason, recommended=None,
                        tags=(), zone_id=None, ladder_id=None, log_reason=None):
        """Ghi một purchase record. `tags` là nhãn chất lượng dữ liệu theo Backtest §18.

        WP-A4/A4.4 + A4.5 (đóng F-025, F-032): nhãn được gắn LÊN BẢN GHI, không chỉ cộng
        vào một bộ đếm tổng. Bộ đếm cho biết CÓ BAO NHIÊU bản ghi bị ảnh hưởng bởi lỗ
        hổng dữ liệu; chỉ nhãn trên bản ghi mới cho biết BẢN GHI NÀO — và sau official run
        thì câu hỏi cần trả lời là câu thứ hai.
        """
        nonlocal eth_total, cooldown_until, last_exec_price
        eth, eff = apply_fill(nominal, open_price, exec_cfg)
        eth_total += eth
        month_key = pd.Timestamp(ts + TZ_OFFSET, unit="s").strftime("%Y-%m")
        res.monthly_deployments[month_key] = res.monthly_deployments.get(month_key, 0.0) + nominal
        tag_list = list(tags)
        if gap_before_now > 0 and "EXECUTION_DATA_GAP" not in tag_list:
            # Nến này là nến hợp lệ ĐẦU TIÊN sau một lỗ hổng: mọi thứ xảy ra ở đây được
            # quyết trên dữ liệu không liên tục, nên bản ghi phải tự khai điều đó.
            tag_list.append("EXECUTION_DATA_GAP")
        # Bộ đếm được cộng TẠI ĐÂY, nơi bản ghi thật sự được ghi — không cộng ở chỗ gọi.
        # Cộng ở chỗ gọi thì một tranche bị bỏ qua vì `amt <= 0` vẫn làm bộ đếm tăng, và
        # bộ đếm lại nói về những bản ghi không tồn tại. Đó đúng là kiểu sai lệch mà F-032
        # phàn nàn, chỉ đổi chiều. Bất biến: bộ đếm == số bản ghi mang tag tương ứng.
        for tag, key in (("EXECUTION_DATA_GAP", "execution_data_gap"),
                         ("DELAYED_DATA_FILL", "delayed_data_fill")):
            if tag in tag_list:
                counters[key] += 1
        res.purchases.append({
            "ts": ts, "source": source, "nominal": nominal, "price": eff, "eth": eth,
            "reason": reason, "regime": regime.regime,
            "recommended_price": recommended,
            "shortfall_bps": ((eff / recommended - 1) * 1e4) if recommended else None,
            "tags": tag_list,
            "missing_candles_before": int(gap_before_now),
        })
        # WP-B3 — audit trail (DM §11): mỗi purchase LÀ một quyết định đã thực thi. Ghi
        # SAU khi purchase record và ledger đã xong, để snapshot available/reserved/deployed
        # phản ánh đúng trạng thái vốn ngay sau quyết định.
        audit_tags = list(tag_list)
        if reason == "BASE_ADVANCE_SCORE":
            # ST §9: tranche Base kéo sớm "phải đánh dấu EXECUTED_EARLY" (đóng F-033). Nhãn
            # nằm trên bản ghi audit — nơi DM §11 dành cho nhãn của một quyết định — chứ
            # KHÔNG trên `purchases[].tags`, vốn là danh mục nhãn chất lượng dữ liệu BT §18
            # và là đầu ra tài chính phải bất biến (`CHECK-B3-07`). Xem CONVENTIONS #23(d).
            audit_tags.append("EXECUTED_EARLY")
        log(ts, log_reason or reason, zone_id=zone_id, ladder_id=ladder_id,
            recommended_price=recommended, recommended_vnd=nominal, tags=audit_tags)
        if source in ("SMART", "OPPORTUNITY", "CRASH"):
            cooldown_until = ts + cfg.cooldown_hours * 3600.0
            last_exec_price = eff
            # Cooldown vừa MỞ — sự kiện ST §20 `COOLDOWN_START` có thật, trước nay không ghi.
            log(ts, "COOLDOWN_START", zone_id=zone_id, ladder_id=ladder_id)

    def zone_pools(z):
        return reserve_map.get(z.zone_id, [(z.pool, z.reserved_vnd)])

    def release_zone(z, ts, reason):
        for pool_name, amt in zone_pools(z):
            if amt > 0:
                _pool(pool_name).release(amt, reason, ts)
        reserve_map.pop(z.zone_id, None)
        z.reserved_vnd = 0.0

    def deploy_zone(z, ts, reason):
        for pool_name, amt in zone_pools(z):
            if amt > 0:
                _pool(pool_name).deploy_from_reserved(amt, reason, ts)
        reserve_map.pop(z.zone_id, None)

    def _pool(name: str) -> Pool:
        return {"BASE": base_pool, "SMART": smart_pool, "OPPORTUNITY": opp_fund}[name]

    def cancel_open_zones(lad, ts, reason):
        for z in lad.zones:
            if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING",
                            "PARTIALLY_FILLED"):
                if z.reserved_vnd > 0:
                    release_zone(z, ts, reason)
                z.status = "CANCELLED"

    def expire_smart_ladders(ts):
        for lad in ladders:
            if lad.type == "SMART" and lad.status == "ACTIVE":
                cancel_open_zones(lad, ts, "LADDER_EXPIRED")
                lad.status = "EXPIRED"
                log(ts, "LADDER_EXPIRED", ladder_id=lad.ladder_id)

    def settle_month_end_smart(ts, open_price):
        avail = smart_pool.available
        if avail <= 1e-9:
            return
        if not np.isnan(oscore) and oscore >= 45:
            if smart_pool.deploy_from_available(avail, "MONTH_END_SMART", ts):
                record_purchase(ts, "SMART", avail, open_price, "MONTH_END_SMART")
        else:
            buy = avail * 0.5
            to_opp = avail - buy
            headroom = max(0.0, mc.opportunity_cap - opp_fund.total)
            xfer = min(to_opp, headroom)
            if xfer > 0:
                smart_pool.transfer_available_to(opp_fund, xfer, "MONTH_END_SMART", ts)
            leftover = to_opp - xfer
            buy += leftover  # phần vượt cap được mua nốt (CONVENTIONS #7)
            if buy > 0 and smart_pool.deploy_from_available(buy, "MONTH_END_SMART", ts):
                record_purchase(ts, "SMART", buy, open_price, "MONTH_END_SMART")

    def execute_base_tranche(idx, ts, open_price, reason, tags=()):
        amt = min(base_state.tranche_amount(idx), base_pool.available)
        if amt <= 1e-9:
            base_state.executed.add(idx)
            return
        base_pool.deploy_from_available(amt, reason, ts)
        base_state.executed.add(idx)
        record_purchase(ts, "BASE", amt, open_price, reason, tags=tags)

    def create_action(z, lad, ts_close, close_price, local_hour):
        """TRIGGERED -> ACTION_PENDING với delay model (Backtest §5–§6)."""
        z.status = "ACTION_PENDING"
        z.triggered_at = ts_close
        z.action_expires_at = ts_close + exec_cfg.action_ttl_seconds
        zone_meta[z.zone_id] = {"recommended": close_price}
        counters["triggered_actions"] += 1
        if exec_cfg.p2p_unavailable_in_crash and regime.state == "CRASH" \
                and exec_cfg.funding_policy == "ON_DEMAND":
            z.execute_at = None  # funding không khả dụng suốt TTL -> MISSED
            return
        if behavioral:
            secs_to_7 = ((7 * 3600 - ((ts_close + TZ_OFFSET) % DAY)) % DAY)
            delay = behavioral_delay_seconds(local_hour, behavioral_rng, secs_to_7,
                                             exec_cfg.action_ttl_seconds)
            if delay == MISSED:
                z.execute_at = None
                return
            fd = 0.0 if exec_cfg.funding_policy == "BULK_MONTHLY" else exec_cfg.funding_delay_seconds
            z.execute_at = ts_close + delay + fd
        else:
            z.execute_at = ts_close + total_delay_seconds(exec_cfg)

    # ------------------------------------------------- main loop
    for i in range(n):
        ts = c["ts"][i]                              # 1. tiến đồng hồ (open time của nến)
        o, hi, lo, cl = c["open"][i], c["high"][i], c["low"][i], c["close"][i]
        gap_before_now = int(c["missing_before"][i])
        local = ts + TZ_OFFSET
        day_ord = int(local // DAY)
        lts = pd.Timestamp(local, unit="s")
        month_key = (lts.year, lts.month)
        acct_day = lts.day
        tod = local % DAY

        # 2–6. accounting month mới
        if month_key != cur_month:
            if cur_month is not None:
                expire_smart_ladders(ts)             # 3. Smart ladder hết hạn cuối tháng
                # đóng sổ: Base còn sót (gap) giải ngân ngay, Smart leftover theo policy
                for idx in base_state.pending():
                    # ST §9 [F3]: tranche Base chưa chạy được ở nến 12:00 của ngày trigger
                    # (nến đó nằm trong gap) được giải ngân tại nến hợp lệ đầu tiên sau đó.
                    # Tranche Base KHÔNG BAO GIỜ bị bỏ vì gap dữ liệu.
                    execute_base_tranche(idx, ts, o, "MONTH_END_BASE",
                                         tags=("DELAYED_DATA_FILL",))
                settle_month_end_smart(ts, o)
            cur_month = month_key
            # 3->4. đóng sổ tháng cũ / mở sổ tháng mới cho phạm vi unlock Smart theo
            # tháng (DM §5; WP-A7/F-035) — SAU settle Month-End, TRƯỚC contribution.
            smart_pool.open_accounting_month(ts)
            su.month_reset(ts)                       # 4. reset HWM theo mode
            br = apply_monthly_contribution(mc, contribution, cfg, ts)  # 5–6. contribution + cap
            res.contributions.append((ts, contribution))
            # WP-B3 — ST §20 `CAP_OVERFLOW_TO_SMART`: phần contribution vượt cap Opportunity
            # được chuyển sang Smart. Sự kiện có thật, trước nay chỉ nằm trong ledger pool.
            if br["opportunity_overflow_to_smart"] > 0:
                log(ts, "CAP_OVERFLOW_TO_SMART",
                    recommended_vnd=br["opportunity_overflow_to_smart"])
            month_base_budget = br["base"]
            month_smart_budget = br["smart"] + br["opportunity_overflow_to_smart"]
            base_state.month_reset(month_base_budget)
            smart_ladder_created_this_month = False
            day_flags = {}

        # 7. reset bộ đếm theo accounting day
        if day_ord != cur_day_ord:
            cur_day_ord = day_ord
            opp_used_today = 0.0
            day_flags[day_ord] = {"noon": False, "score_advanced": False}

        # 8. daily score mới nếu nến daily nguồn đã đóng (chỉ KÍCH HOẠT snapshot; bullish
        # invalidation trên daily close mới là việc của bước 18 — WP-A6/F-018)
        new_score = False
        daily_close = np.nan
        ndi = int(np.searchsorted(day_end, ts, side="right")) - 1
        if ndi > daily_idx and ndi >= 0:
            daily_idx = ndi
            oscore = d["oscore"][ndi]
            dq = d["dq"][ndi]
            r7 = d["return7"][ndi]
            adr30 = d["adr30"][ndi]
            daily_close = d["close"][ndi]
            new_score = True
            # WP-B3 — ST §20 `DATA_INVALID` / `DATA_DEGRADED`: nhãn chất lượng dữ liệu đổi là
            # một sự kiện thật của bước 8 (ST §3). `GOOD` không có mã trong ST §20 nên không
            # được ghi — xem CONVENTIONS #23(c) và `BACKTEST_NOT_EMITTED_REASONS`.
            if dq != prev_dq:
                if dq == "INVALID":
                    log(ts, "DATA_INVALID")
                elif dq == "DEGRADED":
                    log(ts, "DATA_DEGRADED")
                prev_dq = dq

        # unlocks hiện hành (DEGRADED không được đẩy Opp unlock lên — CONVENTIONS #9)
        s_unl = float(smart_unlock(oscore)) if not np.isnan(oscore) else 0.0
        o_unl = float(opportunity_unlock(oscore)) if not np.isnan(oscore) else 0.0
        if dq == "GOOD":
            last_good_opp_unlock = o_unl
        elif dq == "DEGRADED":
            o_unl = min(o_unl, last_good_opp_unlock)
        else:
            s_unl, o_unl = 0.0, 0.0
        eff_smart_unlock = su.effective_unlock(s_unl, ts)
        opp_active = hyst.update(oscore) if not np.isnan(oscore) else hyst.active

        # 9. Base schedule (12:00 local Day 3/13/23) + Base execute sớm + Month-End
        flags = day_flags.setdefault(day_ord, {"noon": False, "score_advanced": False})
        if not flags["noon"] and tod >= NOON:
            flags["noon"] = True
            delayed = tod > NOON + 900
            for k, (day_no, _) in enumerate(BASE_SCHEDULE):
                if acct_day == day_no and k in base_state.pending():
                    execute_base_tranche(k, ts, o, "BASE_SCHEDULE",
                                         tags=("DELAYED_DATA_FILL",) if delayed else ())
            if acct_day == 25 and base_pool.available > 1e-9:
                # Day 25–27: settle 50% phần Base còn lại (CONVENTIONS #7)
                amt = base_pool.available * 0.5
                if base_pool.deploy_from_available(amt, "MONTH_END_BASE", ts):
                    record_purchase(ts, "BASE", amt, o, "MONTH_END_BASE")
                    for k in base_state.pending():
                        base_state.executed.add(k)
            if acct_day == 28:
                if base_pool.available > 1e-9:
                    amt = base_pool.available
                    base_pool.deploy_from_available(amt, "MONTH_END_BASE", ts)
                    record_purchase(ts, "BASE", amt, o, "MONTH_END_BASE")
                expire_smart_ladders(ts)
                settle_month_end_smart(ts, o)
        if new_score and not np.isnan(oscore) and oscore >= 70 and not flags["score_advanced"]:
            nxt = base_state.next_pending()
            if nxt is not None:
                execute_base_tranche(nxt, ts, o, "BASE_ADVANCE_SCORE")
                counters["base_early"] += 1
            flags["score_advanced"] = True  # tối đa một tranche mỗi lần score mới active

        # 10. Market Regime + nhãn STRESSED. Mọi nhánh execution dưới đây so trên
        # regime.state (trạng thái nền); nhãn STRESSED chỉ dùng reporting ([F1] §17.3).
        # Tại crash entry: cancel Opportunity zone xung đột -> release -> snapshot [F5]
        # ngay ở đây (ST §14: "tại thời điểm vào CRASH", đo NGAY SAU cancel/release);
        # còn TẠO Crash ladder (reservation mới) là việc của bước 14 — WP-A6/F-018.
        # Suspension khi vào RECOVERY và cancel khi hết Recovery là việc của bước 18.
        prev_state = regime.state
        regime.update(ts, r7 if not np.isnan(r7) else None,
                      c["r24"][i] if not np.isnan(c["r24"][i]) else None,
                      None if np.isnan(oscore) else oscore)
        # WP-A5/A5.2 — ĐO LƯỜNG: mốc đổi nhãn regime cho FS-12. Chỉ ĐỌC `regime.regime`
        # (nhãn báo cáo BT §15/§17.3 [F1]) và append vào list; không nhánh execution nào
        # đọc `regime_timeline`, nên điểm thu thập này không đổi hành vi.
        if not res.regime_timeline or res.regime_timeline[-1][1] != regime.regime:
            res.regime_timeline.append((ts, regime.regime))
        # WP-B3 — ST §20: chuyển TRẠNG THÁI NỀN của regime (§17.1–§17.2) là sự kiện phải ghi.
        # Trước WP-B3 chỉ crash entry KÈM ladder mới được ghi (bước 14a), nên một lần vào
        # CRASH không tạo được ladder là hoàn toàn vô hình trong log.
        if regime.state != prev_state:
            log(ts, regime.last_entry_reason if regime.state == "CRASH"
                else "CRASH_EXIT" if regime.state == "RECOVERY" else "RECOVERY_END")
        crash_snapshot = None                        # (snapshot, opp_avail, smart_avail)
        if regime.state == "CRASH" and prev_state != "CRASH":
            for lad in ladders:
                if lad.type == "OPPORTUNITY" and lad.status == "ACTIVE":
                    cancel_open_zones(lad, ts, "CRASH_ENTRY")
                    lad.status = "CANCELLED"
            # [F5] ST §14: snapshot = Smart AVAILABLE + Opportunity AVAILABLE (đã unlock,
            # chưa nằm trong reservation nào) đo NGAY SAU cancel/release. KHÔNG áp daily
            # limit vào snapshot (F-021); daily limit cưỡng chế ở khâu triển khai — bước 14.
            if opp_active and o_unl > 0:
                opp_avail = min(opp_fund.available,
                                max(0.0, opp_fund.total * o_unl
                                    - opp_fund.reserved - opp_fund.deployed))
            else:
                opp_avail = 0.0
            smart_avail = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
            snapshot = opp_avail + smart_avail
            if snapshot > 1e-9 and not np.isnan(adr30):
                crash_snapshot = (snapshot, opp_avail, smart_avail)

        # 11. cooldown & override
        in_cooldown = ts < cooldown_until
        override_ok = (not np.isnan(last_exec_price)) and \
            (o <= last_exec_price * (1 - cfg.cooldown_override_pct))

        # 12. pending action tới hạn / TTL / MISSED — chỉ XÁC ĐỊNH action đủ điều kiện fill
        # và đánh dấu MISSED; fill/ledger/cooldown là các bước 15–17 (WP-A6/F-018)
        due_fills = []
        # WP-C2 chỉ cần ĐẾM; WP-B3 cần cả DANH TÍNH action đang mở để đặt được lý do ST §20
        # cho `ACTION_PENDING`. `bool(open_pairs)` ĐỒNG NHẤT với `open_actions > 0` cũ, nên
        # giá trị đưa vào `derive_execution_state` không đổi (hợp đồng WP-C2 giữ nguyên).
        open_pairs = []
        for lad in ladders:
            for z in lad.zones:
                if z.status != "ACTION_PENDING":
                    continue
                if z.execute_at is not None and ts >= z.execute_at:
                    if z.execute_at <= z.action_expires_at:
                        due_fills.append((z, lad))
                    else:
                        amt = z.reserved_vnd     # đọc TRƯỚC release (release đưa về 0)
                        release_zone(z, ts, "ACTION_TTL_EXPIRED")
                        z.status = "MISSED"
                        counters["missed_actions"] += 1
                        log(ts, "ACTION_TTL_EXPIRED", zone_id=z.zone_id,
                            ladder_id=lad.ladder_id, recommended_vnd=amt,
                            recommended_price=z.target_price)
                elif ts >= z.action_expires_at:
                    amt = z.reserved_vnd
                    release_zone(z, ts, "ACTION_MISSED")
                    z.status = "MISSED"
                    counters["missed_actions"] += 1
                    log(ts, "ACTION_MISSED", zone_id=z.zone_id, ladder_id=lad.ladder_id,
                        recommended_vnd=amt, recommended_price=z.target_price)
                else:
                    # Còn mở, chưa tới hạn (kể cả `execute_at is None` — action sẽ MISSED
                    # khi hết TTL nhưng TẠI ĐÂY nó vẫn là một action đang chờ).
                    open_pairs.append((z, lad))

        # 12b. WP-C2 — ĐẶT TÊN (không đổi hành vi): hợp nhất `data_quality` (bước 8),
        # `in_cooldown`/override (bước 11) và vòng đời `Zone` (bước 12) thành MỘT chiều
        # Execution State canonical. Điểm đo là ĐÂY vì đây là nơi cả bốn dữ kiện vừa đủ
        # và chưa bị các bước 13–18 của chính nến này làm nhoè: bước 12 vừa phân loại
        # xong action tới hạn (`READY_TO_BUY` sống đúng ở điều kiện `ts >= execute_at` mà
        # S001 chỉ ra), còn action MỚI của nến này chưa được tạo (bước 14c).
        # Chỉ ĐỌC; không nhánh execution nào đọc lại giá trị này — cùng khuôn quan sát mà
        # WP-A5 đã dùng cho `regime_timeline` / `opp_cap_samples`.
        exec_state = derive_execution_state(
            action_due=bool(due_fills),
            action_open=bool(open_pairs),
            data_invalid=dq == "INVALID",
            cooldown_blocking=in_cooldown and not override_ok)
        if not res.execution_state_timeline or res.execution_state_timeline[-1][1] != exec_state:
            res.execution_state_timeline.append((ts, exec_state))
            # WP-B3 — CÙNG MỘT giá trị, hình dạng thứ hai: bản ghi chuyển trạng thái theo
            # DM §11 ("audit trail của state và action"). Không có nguồn sự thật thứ hai —
            # cả hai hình dạng sinh ra trong đúng nhánh này, từ đúng `exec_state` của WP-C2.
            # Lý do: dữ kiện quyết định trạng thái MỚI; khi trạng thái mới là `WAIT` (không
            # điều kiện nào còn hiệu lực) thì lý do là dữ kiện vừa CHẤM DỨT — xem
            # CONVENTIONS #23(b). Lần đo ĐẦU TIÊN của run chỉ thiết lập trạng thái nền,
            # chưa phải một chuyển trạng thái, nên không sinh bản ghi.
            entry = state_entry_reason(exec_state, due_fills, open_pairs)
            reason, zid, lid = state_reason if exec_state is ExecutionState.WAIT else entry
            if exec_state_now is not None and reason is not None:
                log(ts, reason, zone_id=zid, ladder_id=lid,
                    previous_state=exec_state_now, new_state=exec_state)
            state_reason = entry
        exec_state_now = exec_state

        # 13. trigger Smart (LOW) / confirmation Opportunity (CLOSE) — sắp thứ tự §15.1 [F2].
        # Ladder tạo ở bước 14 của nến này KHÔNG tham gia trigger cùng nến (§19: 13 trước 14).
        candidates = []
        for lad in ladders:
            if lad.status not in ("ACTIVE", "SUSPENDED"):
                continue
            for z in lad.zones:
                trig_ok = z.status == "ACTIVE" or (
                    lad.type == "CRASH" and z.status == "SUSPENDED")
                if not trig_ok or z.reserved_vnd <= 1e-12:
                    continue
                if lad.type == "SMART" or lad.type == "CRASH":
                    hit = lo <= z.target_price
                else:  # OPPORTUNITY: confirmation bằng CLOSE
                    hit = cl <= z.target_price
                if hit:
                    z.status = "TRIGGERED"
            candidates.extend([z for z in lad.zones if z.status == "TRIGGERED"])

        # 14a. tạo reservation mới: Crash ladder từ snapshot bước 10 (ST §14 [F5])
        if crash_snapshot is not None:
            snapshot, opp_avail, smart_avail = crash_snapshot
            ssp = smart_spacing(adr30, oscore, cfg)
            osp = opportunity_spacing(ssp, cfg)
            lad = create_crash_ladder(o, osp, snapshot, oscore, ts)
            # reserve Opportunity trước, Smart sau (CONVENTIONS #5)
            for z in lad.zones:
                want = z.target_vnd
                parts = []
                take_opp = min(want, opp_avail)
                if take_opp > 0 and opp_fund.reserve(take_opp, "CRASH_ZONE", ts):
                    parts.append(("OPPORTUNITY", take_opp))
                    opp_avail -= take_opp
                    want -= take_opp
                take_smart = min(want, smart_avail)
                if take_smart > 0 and smart_pool.reserve(take_smart, "CRASH_ZONE", ts):
                    parts.append(("SMART", take_smart))
                    smart_avail -= take_smart
                    want -= take_smart
                z.reserved_vnd = sum(a for _, a in parts)
                z.target_vnd = z.reserved_vnd
                reserve_map[z.zone_id] = parts
            # F-030: pool label của Crash ladder = pool cấp ĐA SỐ tổng reserve
            # (tie-break §15.1 [F2] xếp theo pool nguồn vốn; hoà -> OPPORTUNITY,
            # xem CONVENTIONS #16). Label thống nhất cả ladder để zone_index giữ
            # đúng thứ tự trong cùng ladder.
            smart_funded = sum(a for z in lad.zones
                               for p, a in reserve_map.get(z.zone_id, [])
                               if p == "SMART")
            opp_funded = sum(a for z in lad.zones
                             for p, a in reserve_map.get(z.zone_id, [])
                             if p == "OPPORTUNITY")
            src_pool = "SMART" if smart_funded > opp_funded else "OPPORTUNITY"
            for z in lad.zones:
                z.pool = src_pool
            ladders.append(lad)
            # WP-B3 — mỗi Crash zone được reserve LÀ một recommendation ST §20 (`CRASH_ZONE_C*`),
            # mang giá mục tiêu và lượng vốn cam kết. Sự kiện REGIME vào CRASH đã được ghi
            # riêng ở bước 10: một sự kiện nghiệp vụ, một bản ghi.
            for z in lad.zones:
                if z.reserved_vnd > 0:
                    log(ts, zone_reason_code("CRASH", z.zone_index), zone_id=z.zone_id,
                        ladder_id=lad.ladder_id, recommended_price=z.target_price,
                        recommended_vnd=z.reserved_vnd)

        # 14b. tạo reservation mới: Smart / Opportunity ladder (CONVENTIONS #1, #2)
        if dq != "INVALID" and not np.isnan(oscore) and not np.isnan(adr30):
            ssp = smart_spacing(adr30, oscore, cfg)
            if (not smart_ladder_created_this_month and acct_day <= 24
                    and eff_smart_unlock > 0):
                unlocked = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
                if unlocked > 1e-9:
                    # cuối accounting month (giờ local) — F-028: trước đây dùng ts + 31 ngày
                    # cố định, sai nghĩa; expiry THẬT của Smart ladder không đọc field này
                    # (xem expire_smart_ladders, dựa trên phát hiện month rollover), nên đây
                    # chỉ là sửa dữ liệu cho đúng nghĩa, không đổi hành vi (WP-D1/F-028).
                    next_month_local = lts.replace(day=1) + pd.DateOffset(months=1)
                    month_end_ts = next_month_local.value / 1e9 - TZ_OFFSET
                    lad = create_smart_ladder(o, ssp, unlocked, oscore, ts, month_end_ts)
                    for z in lad.zones:
                        if smart_pool.reserve(z.target_vnd, f"SMART_ZONE_S{z.zone_index}", ts):
                            z.reserved_vnd = z.target_vnd
                            reserve_map[z.zone_id] = [("SMART", z.target_vnd)]
                        else:
                            z.status = "CANCELLED"
                    ladders.append(lad)
                    smart_ladder_created_this_month = True
                    for z in lad.zones:
                        if z.reserved_vnd > 0:
                            log(ts, zone_reason_code("SMART", z.zone_index),
                                zone_id=z.zone_id, ladder_id=lad.ladder_id,
                                recommended_price=z.target_price,
                                recommended_vnd=z.reserved_vnd)
            if opp_active and o_unl > 0 and not any(
                    l.type == "OPPORTUNITY" and l.status == "ACTIVE" for l in ladders):
                osp = opportunity_spacing(ssp, cfg)
                eligible = opportunity_reservable(opp_fund, o_unl, opp_active,
                                                  opp_used_today, cfg.opportunity_daily_limit_pct)
                if eligible > 1e-9:
                    lad = create_opportunity_ladder(o, osp, eligible, oscore, ts)
                    for z in lad.zones:
                        if z.target_vnd <= 1e-12:
                            continue
                        if opp_fund.reserve(z.target_vnd, f"OPPORTUNITY_O{z.zone_index}", ts):
                            z.reserved_vnd = z.target_vnd
                            reserve_map[z.zone_id] = [("OPPORTUNITY", z.target_vnd)]
                            opp_used_today += z.target_vnd
                        else:
                            z.status = "CANCELLED"
                    ladders.append(lad)
                    for z in lad.zones:
                        if z.reserved_vnd > 0:
                            log(ts, zone_reason_code("OPPORTUNITY", z.zone_index),
                                zone_id=z.zone_id, ladder_id=lad.ladder_id,
                                recommended_price=z.target_price,
                                recommended_vnd=z.reserved_vnd)

        # 14c. điều chỉnh reservation: TRIGGERED -> ACTION_PENDING theo thứ tự §15.1 [F2]
        # (zone_order_key), max_zones_per_cycle áp SAU khi sắp thứ tự; cooldown/override;
        # INVALID chặn action mới (ST §3). Zone TRIGGERED trong chu kỳ INVALID giữ trạng
        # thái và được xét lại ở chu kỳ hợp lệ kế tiếp — cùng cơ chế giữ-TRIGGERED của
        # max_zones (§15.1) và cooldown (CONVENTIONS #6); xem CONVENTIONS #19 (H-15).
        if candidates and dq != "INVALID":
            lad_by_id = {l.ladder_id: l for l in ladders}
            candidates.sort(key=lambda z: zone_order_key(z, lad_by_id[z.ladder_id]))
            created = 0
            override_counted_this_cycle = False
            ts_close = ts + 900.0
            local_hour = int(((ts_close + TZ_OFFSET) % DAY) // 3600)
            for k, z in enumerate(candidates):
                if created >= cfg.max_zones_per_cycle:
                    # WP-B3 — ST §20 `MAX_ZONES_BLOCK`: mọi candidate còn lại bị chặn bởi
                    # trần `max_zones_per_cycle` (§15.1). Ghi theo TỪNG zone, cùng khuôn với
                    # `DAILY_LIMIT_BLOCK` đã có, để biết zone NÀO bị chặn chứ không chỉ có
                    # bao nhiêu. Chỉ ghi — vòng lặp vẫn `break` y như trước.
                    for zz in candidates[k:]:
                        log(ts, "MAX_ZONES_BLOCK", zone_id=zz.zone_id,
                            ladder_id=zz.ladder_id, recommended_price=zz.target_price,
                            recommended_vnd=zz.reserved_vnd)
                    break
                if in_cooldown and not override_ok:
                    continue  # zone giữ TRIGGERED, xét lại cycle sau (CONVENTIONS #6)
                if lad_by_id[z.ladder_id].type == "CRASH":
                    # ST §14: "Toàn bộ daily limit ... vẫn áp dụng trong Crash" — cưỡng chế
                    # ở khâu triển khai trên PHẦN VỐN OPPORTUNITY của zone (CONVENTIONS #4).
                    # Zone bị chặn giữ TRIGGERED, xét lại cycle sau như max_zones (§15.1).
                    opp_part = sum(a for p, a in reserve_map.get(z.zone_id, [])
                                   if p == "OPPORTUNITY")
                    if opp_part > 1e-12:
                        headroom = max(0.0, opp_fund.total * cfg.opportunity_daily_limit_pct
                                       - opp_used_today)
                        if opp_part > headroom + 1e-9:
                            log(ts, "DAILY_LIMIT_BLOCK", zone_id=z.zone_id,
                                ladder_id=z.ladder_id, recommended_price=z.target_price,
                                recommended_vnd=z.reserved_vnd)
                            continue
                        opp_used_today += opp_part
                if in_cooldown and override_ok:
                    # đếm theo SỰ KIỆN override (một cycle), không theo zone được tạo action
                    # (WP-D1/F-031; BT §16/§21 dòng 301 — "tần suất cooldown override theo
                    # regime" là số liệu chẩn đoán, không phải input cho quyết định engine)
                    if not override_counted_this_cycle:
                        counters["cooldown_override"][regime.regime] += 1
                        override_counted_this_cycle = True
                    log(ts, "COOLDOWN_OVERRIDE", zone_id=z.zone_id,
                        ladder_id=z.ladder_id, recommended_price=z.target_price,
                        recommended_vnd=z.reserved_vnd)
                create_action(z, lad_by_id[z.ladder_id], ts_close, cl, local_hour)
                created += 1

        # 15. ưu tiên thực thi giữa các fill tới hạn: Base -> Smart -> Opportunity (§15.1
        # [F2], cùng khoá với bước 14). Mỗi zone tiêu đúng phần reserve của nó nên ưu tiên
        # chỉ quyết định THỨ TỰ ghi sổ/purchase trong nến, không quyết định lượng vốn.
        due_fills.sort(key=lambda zl: zone_order_key(zl[0], zl[1]))

        # 16–17. fill tại execution proxy (fee + slippage) rồi cập nhật ledger, portfolio và
        # cooldown — SAU khi trigger/action mới của nến đã được xử lý (bước 13–14). Cooldown
        # đọc ở bước 11 nên fill của nến này không chặn action tạo ở chính nến này (§19).
        for z, lad in due_fills:
            nominal = z.reserved_vnd
            deploy_zone(z, ts, f"{lad.type}_ZONE")
            z.status = "EXECUTED"
            z.executed_at = ts
            counters["executed_actions"] += 1
            src = "CRASH" if lad.type == "CRASH" else lad.type
            record_purchase(ts, src, nominal, o, f"{lad.type}_ZONE_{z.zone_index}",
                            recommended=zone_meta.get(z.zone_id, {}).get("recommended"),
                            zone_id=z.zone_id, ladder_id=lad.ladder_id,
                            log_reason=zone_reason_code(lad.type, z.zone_index))

        # 18. ladder completion / suspension / expiry / bullish invalidation
        # 18a. bullish invalidation trên daily close vừa kích hoạt ở bước 8 (ST §18.2). Ladder
        # tạo ở bước 14 của CHÍNH nến này chưa tồn tại khi daily close đó hoàn tất nên không
        # bị đếm — giữ đúng ngữ nghĩa "hai daily close hoàn chỉnh liên tiếp" sau khi tạo.
        if new_score:
            for lad in ladders:
                if lad.status == "ACTIVE" and lad.created_at < ts \
                        and update_bullish_invalidation(lad, daily_close):
                    cancel_open_zones(lad, ts, "BULLISH_INVALIDATION")
                    log(ts, "BULLISH_INVALIDATION", ladder_id=lad.ladder_id)
        # 18b. hysteresis Opportunity (ST §5): suspend / reactivate / cancel sau 7 ngày
        for lad in ladders:
            if lad.type == "OPPORTUNITY" and lad.status == "ACTIVE":
                for z in lad.zones:
                    if not opp_active and z.status == "ACTIVE":
                        z.status = "SUSPENDED"
                        z.suspended_at = ts
                    elif opp_active and z.status == "SUSPENDED":
                        z.status = "ACTIVE"
                        z.suspended_at = None
                    elif z.status == "SUSPENDED" and z.suspended_at is not None and \
                            ts - z.suspended_at > cfg.suspended_zone_hold_days * DAY:
                        amt = z.reserved_vnd
                        release_zone(z, ts, "OPPORTUNITY_SUSPENDED")
                        z.status = "CANCELLED"
                        log(ts, "OPPORTUNITY_SUSPENDED", zone_id=z.zone_id,
                            ladder_id=lad.ladder_id, recommended_price=z.target_price,
                            recommended_vnd=amt)
        # 18c. Crash ladder theo chuyển trạng thái nền của nến này (ST §18.3)
        if regime.state == "RECOVERY" and prev_state == "CRASH":
            for lad in ladders:
                if lad.type == "CRASH" and lad.status == "ACTIVE":
                    lad.status = "SUSPENDED"
                    for z in lad.zones:
                        if z.status == "ACTIVE":
                            z.status = "SUSPENDED"
                            z.suspended_at = ts
        if regime.state == "NORMAL" and prev_state == "RECOVERY":
            # ST §18.3: hết 72h Recovery -> CANCEL crash zone chưa hit + release reserve.
            # So trên TRẠNG THÁI NỀN nên chạy cho MỌI kết cục recovery-end, kể cả khi
            # nhãn báo cáo là STRESSED (F-001). Quét mọi crash ladder còn mở để các
            # ladder tồn đọng từ episode trước (re-entry) cũng được đóng.
            for lad in ladders:
                if lad.type == "CRASH" and lad.status in ("ACTIVE", "SUSPENDED"):
                    cancel_open_zones(lad, ts, "RECOVERY_END")
                    lad.status = "CANCELLED"
        # 18d. expiry Opportunity (90 ngày) và completion
        for lad in ladders:
            if lad.status == "ACTIVE" and lad.type == "OPPORTUNITY" and lad.expires_at \
                    and ts >= lad.expires_at:
                cancel_open_zones(lad, ts, "LADDER_EXPIRED")
                lad.status = "EXPIRED"
                log(ts, "LADDER_EXPIRED", ladder_id=lad.ladder_id)
            if lad.status == "ACTIVE" and all(
                    z.status in ("EXECUTED", "CANCELLED", "MISSED", "EXPIRED")
                    for z in lad.zones):
                lad.status = "COMPLETED"

        # snapshot cash ratio (mỗi ngày một lần, tại nến đầu ngày)
        if i == 0 or int((c["ts"][i - 1] + TZ_OFFSET) // DAY) != day_ord:
            cash = base_pool.total - base_pool.deployed + smart_pool.total \
                - smart_pool.deployed + opp_fund.total - opp_fund.deployed
            res.cash_samples.append((ts, cash, eth_total, o))
            # WP-A5/A5.1 — ĐO LƯỜNG cho FS-02, cùng nhịp và cùng vị trí với cash sample.
            # Chỉ ĐỌC property của pool và của MonthlyCapital; không gọi phương thức nào
            # có tác dụng phụ, nên không đổi hành vi. Ngữ nghĩa hai vế xem CONVENTIONS #20.
            cap = mc.opportunity_cap
            res.opp_cap_samples.append({
                "ts": ts,
                "total": opp_fund.total,
                "cap": cap,
                "available": opp_fund.available,
                "at_cap": cap > 0 and opp_fund.total >= cap - 1e-9,
                "idle": opp_fund.available > 1e-9,
            })
            # WP-C2/C2.4 — `market_snapshots` (DM §4). Cùng nhịp và cùng vị trí với
            # `cash_samples`: một bản ghi mỗi accounting day. Nhóm `state` của DM §4
            # (`market_regime`, `execution_state`, `data_quality`) LUÔN NOT NULL, và hai
            # chiều Regime/Execution nằm ở HAI trường riêng — ST §16 đòi "lưu riêng".
            # `execution_state` là giá trị đã đo ở bước 12b của CHÍNH nến này.
            # Phạm vi có chủ ý: WP-C2 là gói ĐẶT TÊN, nên bản ghi chỉ mang những nhóm
            # DM §4 mà engine đã có sẵn tại điểm này (identity/market/score/capital/state).
            # Ba nhóm indicator (price location, market stress, relative value) và
            # `btc_price` KHÔNG được sinh ở đây — chúng đòi kéo thêm cột chỉ báo vào
            # engine, việc đó nằm ngoài phạm vi đã đóng băng của gói này và được ghi
            # nhận tường minh trong `docs/CONVENTIONS.md` #22 thay vì bỏ trống im lặng.
            res.market_snapshots.append({
                "ts": ts,                                   # timestamp_utc (epoch giây)
                "accounting_date_local": lts.strftime("%Y-%m-%d"),
                "eth_price": o,
                "opportunity_score_raw": None if np.isnan(oscore) else float(oscore),
                "smart_unlock": eff_smart_unlock,
                "opportunity_unlock": o_unl,
                "smart_unlock_peak": su.peak,
                "opportunity_fund_balance_vnd": opp_fund.total,
                "opportunity_fund_available_vnd": opp_fund.available,
                "opportunity_fund_reserved_vnd": opp_fund.reserved,
                "market_regime": regime.regime,             # chiều 1 — WP-A3, nhãn §16
                "execution_state": exec_state,              # chiều 2 — WP-C2, NOT NULL
                "data_quality": dq,
            })

    res.counters = counters
    return res
