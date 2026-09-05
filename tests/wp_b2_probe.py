"""WP-B2 — dụng cụ QUAN SÁT cho bộ test requirement Backtest §21.

Gói WP-B2 **chỉ viết test**: không dòng nào trong `src/eth_dca_os/` được sửa. Nhưng phần
lớn câu trong §21 nói về những thứ engine KHÔNG trả ra ngoài (`RunResult` không mang pool,
ladder, hay trạng thái zone theo thời gian). Module này lấp đúng khoảng đó bằng cách QUAN
SÁT — không mô phỏng, không dựng trạng thái bằng tay:

1. `Pool` / `create_*_ladder` được patch trong namespace `eth_dca_os.engine` để giữ tham
   chiếu tới đúng những đối tượng engine thật đang dùng (cùng khuôn với
   `wp_a3_harness.instrument`).
2. `derive_execution_state` — hàm được engine gọi ĐÚNG MỘT LẦN mỗi nến ở bước 12b (§19) —
   được bọc lại để chụp một khung ảnh trạng thái mỗi nến. Bản bọc trả về ĐÚNG giá trị của
   hàm thật, nên hành vi engine không đổi; `test_b2_02c_probe_does_not_change_engine_behaviour` khoá
   điều đó bằng phép so bit-for-bit có/không instrumentation.

Lưới thời gian của các khung ảnh được dựng lại ĐỘC LẬP từ dataset (không hỏi engine), nên
mọi khẳng định "tại nến nào" đều kiểm chứng được thay vì tin lời engine — cùng cách
`wp_c2_scenarios.run_scenario_with_grid` đã làm.

Dataset builder dùng lại `wp_a3_harness.build_dataset` và bộ khoét lỗ hổng dữ liệu dùng lại
`wp_b3_scenarios._drop_candles`: KHÔNG dựng builder thứ hai (STATE_AUTHORITY — trùng nguồn
sự thật là một khiếm khuyết, không phải dự phòng).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import pandas as pd

import eth_dca_os.engine as engine_mod
import eth_dca_os.ladders as ladders_mod
from eth_dca_os.capital import Pool
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.engine import _epoch_seconds, run_engine
from eth_dca_os.ladders import (
    OPEN_ZONE_STATUSES,
    create_crash_ladder,
    create_opportunity_ladder,
    create_smart_ladder,
)
from wp_a3_harness import build_dataset
from wp_b3_scenarios import _drop_candles as drop_candles

#: Bản GỐC của những tên bị patch, chốt tại thời điểm import — KHÔNG đọc lại từ module
#: khi instrument. Hai lần `run_case` trong cùng một test dùng chung một `monkeypatch`, nên
#: đọc lại sẽ bọc chồng lên bản bọc của lần trước và bộ đếm nến của lần trước vẫn chạy tiếp.
_REAL_DERIVE = engine_mod.derive_execution_state

DAY = 86400.0
TZ = 7 * 3600           # Asia/Ho_Chi_Minh, không DST
CANDLE = 900.0

__all__ = [
    "Probe", "Frame", "run_case", "drop_candles", "build_dataset", "financial_payload",
    "FixedRng", "local_parts", "local_ts", "local_key", "DAY", "TZ", "CANDLE",
]


def local_ts(ts: float) -> pd.Timestamp:
    """`pandas.Timestamp` theo giờ local Asia/Ho_Chi_Minh của một epoch giây."""
    return pd.Timestamp(ts + TZ, unit="s")


def local_parts(ts: float):
    """(ngày trong tháng, giờ, phút) theo giờ local Asia/Ho_Chi_Minh của một epoch giây."""
    lts = local_ts(ts)
    return lts.day, lts.hour, lts.minute


def local_key(ts: float) -> str:
    """Mốc local đầy đủ 'YYYY-MM-DD HH:MM' — dùng khi kịch bản trải nhiều tháng và
    `local_parts` (chỉ có ngày/giờ/phút) không còn định danh duy nhất một nến."""
    return local_ts(ts).strftime("%Y-%m-%d %H:%M")


@dataclass
class Frame:
    """Khung ảnh trạng thái tại bước 12b của MỘT nến."""
    ts: float
    pools: dict                      # tên pool -> (available, reserved, deployed)
    zones: tuple                     # (ladder_id, ladder_type, ladder_status, zone_id,
                                     #  zone_index, status, reserved_vnd, pool, target_price)
    ladder_snapshots: tuple          # (ladder_id, type, eligible_capital_vnd)
    inputs: dict                     # bốn dữ kiện đưa vào derive_execution_state
    state: str

    @property
    def total_reserved(self) -> float:
        return sum(r for _, r, _ in self.pools.values())

    @property
    def open_zone_reserved(self) -> float:
        return sum(z[6] for z in self.zones if z[5] in OPEN_ZONE_STATUSES)

    def zone(self, zone_id: int):
        for z in self.zones:
            if z[3] == zone_id:
                return z
        return None


@dataclass
class Probe:
    pools: list = field(default_factory=list)
    ladders: list = field(default_factory=list)
    frames: list = field(default_factory=list)
    grid: list = field(default_factory=list)
    candles: dict = field(default_factory=dict)   # ts/open/high/low/close của cửa sổ chạy

    # -------------------------------------------------------------- nến

    def candle(self, ts: float) -> dict:
        """OHLC của nến tại `ts` — đọc từ DATASET, không hỏi engine."""
        k = self.grid.index(ts)
        return {name: float(self.candles[name][k]) for name in ("open", "high", "low", "close")}

    def pierced_zones(self, ts: float) -> set:
        """Tập `zone_id` mà LUẬT §5 nói là bị xuyên tại nến `ts`, tính ĐỘC LẬP với engine.

        Backtest §5: `Smart trigger: LOW[T] <= zone_price`;
        `Opportunity trigger: CLOSE[T] <= zone_price`. Crash ladder đi cùng luật LOW của
        Smart (ST §14 — zone Crash là zone giá, xác nhận bằng LOW).
        """
        c = self.candle(ts)
        f = self.frame_at(ts)
        out = set()
        for (lad_id, lad_type, lad_status, zid, zidx, status, reserved, pool, target) in f.zones:
            if lad_status not in ("ACTIVE", "SUSPENDED") or reserved <= 1e-12:
                continue
            if status != "ACTIVE" and not (lad_type == "CRASH" and status == "SUSPENDED"):
                continue
            price = c["low"] if lad_type in ("SMART", "CRASH") else c["close"]
            if price <= target:
                out.add(zid)
        return out

    # -------------------------------------------------------------- truy vấn

    def pool(self, name: str) -> Pool:
        for p in self.pools:
            if p.name == name:
                return p
        raise KeyError(name)

    def by_type(self, ladder_type: str):
        return [l for l in self.ladders if l.type == ladder_type]

    def frame_at(self, ts: float) -> Frame:
        for f in self.frames:
            if f.ts == ts:
                return f
        raise KeyError(ts)

    def frame_index(self, ts: float) -> int:
        for i, f in enumerate(self.frames):
            if f.ts == ts:
                return i
        raise KeyError(ts)

    def ledger(self, pool_name: str, entry_type: str | None = None,
               reason: str | None = None):
        return [e for e in self.pool(pool_name).ledger
                if entry_type in (None, e["entry_type"])
                and reason in (None, e["reason_code"])]

    # -------------------------------------------------------------- chụp ảnh

    def _snapshot(self, ts: float, inputs: dict, state) -> Frame:
        pools = {p.name: (p.available, p.reserved, p.deployed) for p in self.pools}
        zones = tuple(
            (l.ladder_id, l.type, l.status, z.zone_id, z.zone_index, z.status,
             z.reserved_vnd, z.pool, z.target_price)
            for l in self.ladders for z in l.zones)
        snaps = tuple((l.ladder_id, l.type, l.eligible_capital_vnd) for l in self.ladders)
        return Frame(ts=ts, pools=pools, zones=zones, ladder_snapshots=snaps,
                     inputs=dict(inputs), state=str(state))


def instrument(mp, grid: list) -> Probe:
    """Patch namespace engine để chụp Pool / Ladder / trạng thái từng nến. Hành vi KHÔNG đổi."""
    probe = Probe(grid=list(grid))

    class RecordingPool(Pool):
        def __init__(self, name: str, *a, **kw):
            super().__init__(name, *a, **kw)
            probe.pools.append(self)

    def _wrap(fn):
        def inner(*a, **kw):
            lad = fn(*a, **kw)
            probe.ladders.append(lad)
            return lad
        return inner

    counter = itertools.count()

    def probing_derive(**kw):
        out = _REAL_DERIVE(**kw)
        k = next(counter)
        # Lưới được dựng ĐỘC LẬP từ dataset; nếu engine duyệt nhiều nến hơn lưới thì
        # giả định "một lần gọi mỗi nến" đã sai và test phải đỏ ngay tại đây.
        assert k < len(probe.grid), "derive_execution_state được gọi nhiều hơn số nến"
        probe.frames.append(probe._snapshot(probe.grid[k], kw, out))
        return out

    mp.setattr(engine_mod, "Pool", RecordingPool)
    mp.setattr(engine_mod, "create_crash_ladder", _wrap(create_crash_ladder))
    mp.setattr(engine_mod, "create_smart_ladder", _wrap(create_smart_ladder))
    mp.setattr(engine_mod, "create_opportunity_ladder", _wrap(create_opportunity_ladder))
    mp.setattr(engine_mod, "derive_execution_state", probing_derive)
    return probe


def _grid(dataset, start, end) -> list:
    ts = _epoch_seconds(dataset["ETHUSDT_15m"]["open_time"])
    sel = ts[(ts >= start.timestamp()) & (ts < end.timestamp())]
    return [float(x) for x in sel]


def run_case(day_specs, mp, *, strategy_cfg=None, exec_cfg=None, contribution=100.0,
             first_local_day: str = "2023-03-01", drop=None, behavioral_rng=None,
             probe: bool = True):
    """Chạy `run_engine` THẬT trên kịch bản `day_specs`. Trả `(RunResult, Probe|None)`.

    Bộ đếm `_ladder_seq`/`_zone_seq` là biến cấp module nên được reset trước mỗi lần chạy:
    không reset thì `zone_id` phụ thuộc THỨ TỰ chạy và mọi phép so mất tính tất định.
    """
    mp.setattr(ladders_mod, "_ladder_seq", itertools.count(1))
    mp.setattr(ladders_mod, "_zone_seq", itertools.count(1))
    ds, scores, start, end = build_dataset(day_specs, first_local_day=first_local_day)
    if drop:
        ds = drop_candles(ds, drop)
    grid = _grid(ds, start, end)
    if probe:
        p = instrument(mp, grid)
    else:
        # Trả mọi tên đã patch về BẢN GỐC: một `monkeypatch` được dùng lại giữa hai lần
        # `run_case` trong cùng test, nên "không instrument" phải là một hành động, không
        # phải sự vắng mặt của hành động.
        p = None
        mp.setattr(engine_mod, "Pool", Pool)
        mp.setattr(engine_mod, "create_crash_ladder", create_crash_ladder)
        mp.setattr(engine_mod, "create_smart_ladder", create_smart_ladder)
        mp.setattr(engine_mod, "create_opportunity_ladder", create_opportunity_ladder)
        mp.setattr(engine_mod, "derive_execution_state", _REAL_DERIVE)
    if p is not None:
        e15 = ds["ETHUSDT_15m"]
        ts_all = _epoch_seconds(e15["open_time"])
        m = (ts_all >= start.timestamp()) & (ts_all < end.timestamp())
        p.candles = {name: e15[name].to_numpy(float)[m]
                     for name in ("open", "high", "low", "close")}
        p.candles["ts"] = ts_all[m]
    res = run_engine(ds, scores, strategy_cfg or BASELINE_STRATEGY,
                     exec_cfg or GATE1_LOW_FRICTION, start, end,
                     contribution=contribution, behavioral_rng=behavioral_rng)
    if p is not None:
        assert len(p.frames) == len(p.grid), (
            f"số khung ảnh {len(p.frames)} != số nến {len(p.grid)}")
    return res, p


def financial_payload(res) -> dict:
    """Toàn bộ đầu ra TÀI CHÍNH/CHIẾN LƯỢC của một run — dùng cho phép so bất biến.

    Cố ý KHÔNG gồm `decision_log` (bề mặt audit của WP-B3) và `execution_state_timeline`
    (bề mặt đặt tên của WP-C2): hai thứ đó là quan sát, không phải kết quả tài chính.
    """
    return {
        "purchases": res.purchases,
        "contributions": res.contributions,
        "counters": res.counters,
        "monthly_deployments": res.monthly_deployments,
        "cash_samples": res.cash_samples,
        "opp_cap_samples": res.opp_cap_samples,
        "eth_total": res.eth_total,
        "contributed_total": res.contributed_total,
    }


class FixedRng:
    """RNG tất định thay cho `numpy.random.Generator` trong `behavioral_delay_seconds`.

    `run_engine` nhận `behavioral_rng` như một tham số công khai, nên đây là đường vào
    SẴN CÓ của production code, không phải một cửa hậu dựng riêng cho test. Chỉ hai
    phương thức được `execution.behavioral_delay_seconds` dùng tới: `random()` và
    `uniform()`.
    """

    def __init__(self, u: float, uniform_at: str = "low"):
        self._u = float(u)
        self._uniform_at = uniform_at

    def random(self) -> float:
        return self._u

    def uniform(self, lo: float, hi: float) -> float:
        return float(lo) if self._uniform_at == "low" else float(hi)

