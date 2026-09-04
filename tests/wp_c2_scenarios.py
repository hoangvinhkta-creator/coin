"""WP-C2 — kịch bản engine tất định dùng chung cho test Execution State.

Hai vai trò:

1. **Dựng đường chạy thật** cho từng Execution State thuộc phạm vi `ADR-001`
   (`WAIT`, `READY_TO_BUY`, `ACTION_PENDING`, `COOLDOWN`, `DATA_BLOCKED`) qua `run_engine`,
   không dựng trạng thái bằng tay.
2. **Khoá hành vi CŨ**: `invariant_payload()` chỉ đọc các trường `RunResult` đã tồn tại
   TRƯỚC WP-C2. Fingerprint của nó được chụp trên cây mã trước khi sửa và đóng băng trong
   `tests/test_wp_c2_execution_state.py`, nên bất kỳ thay đổi hành vi nào (vòng đời zone,
   thời điểm cooldown, chặn dữ liệu xấu) đều làm test đỏ.

Dataset builder dùng lại `wp_a3_harness.build_dataset` — không dựng builder thứ hai.
"""
from __future__ import annotations

import hashlib
import itertools
import json

import eth_dca_os.ladders as ladders_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from eth_dca_os.engine import _epoch_seconds, run_engine
from wp_a3_harness import build_dataset

#: Các trường `RunResult` đã tồn tại TRƯỚC WP-C2. Fingerprint chỉ tính trên tập này.
#:
#: `decision_log` ĐÃ RỜI tập này tại `WP-B3` (2026-09-04). Lý do canonical: `WP-B3` là gói
#: sở hữu `decision_log` và CỐ Ý thay đổi bề mặt đó (DM §11, đóng `F-024`/`F-033`), nên giữ
#: nó trong một fingerprint "hành vi không đổi" sẽ biến phép so thành phép so luôn đỏ —
#: không còn nói được điều gì về hành vi. Mọi trường CÒN LẠI giữ nguyên vai trò khoá hành
#: vi, và bốn giá trị trong `FROZEN_PRE_WP_C2_FINGERPRINTS` được CHỤP LẠI trên cây mã
#: TRƯỚC bản sửa WP-B3 (HEAD `04f77ac`) rồi mới áp bản sửa — nên đây vẫn là một phép so
#: TRƯỚC–SAU thật, không phải một giá trị chép từ kết quả sau khi sửa.
PRE_WP_C2_RESULT_FIELDS = (
    "purchases", "contributions", "counters", "monthly_deployments",
    "cash_samples", "opp_cap_samples", "regime_timeline",
)


def _quiet(n: int, **kw) -> list[dict]:
    """`n` ngày yên tĩnh: giá phẳng, oscore thấp, dữ liệu GOOD."""
    return [dict(kw) if i == 0 else {} for i in range(n)]


#: Mỗi kịch bản: (day_specs, exec_cfg, first_local_day).
#: `oscore` của một ngày có hiệu lực từ 07:00 local NGÀY ĐÓ (xem `build_dataset`).
SCENARIOS: dict[str, dict] = {
    # A — không có gì đáng làm: không ladder, không action, không cooldown, dữ liệu GOOD.
    "wait_only": {
        "day_specs": _quiet(6, price=100.0, oscore=20.0, return7=0.0),
        "exec_cfg": GATE1_LOW_FRICTION,
    },
    # B + C + D — vòng đời đầy đủ của một Smart zone dưới ma sát THẬT (gate3_realistic:
    # user_delay 4h + funding_delay 1h = 5h) nên ACTION_PENDING kéo dài 20 nến trước khi
    # tới hạn (READY_TO_BUY), rồi cooldown 48h sau khi fill.
    "smart_action_cycle": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0},                      # ladder Smart được tạo từ 07:00 Day 2
            {},                                    # S0 trigger -> action -> fill -> cooldown
            {},
            {},
            {},
        ],
        "exec_cfg": GATE3_REALISTIC,
    },
    # E — cửa sổ dữ liệu INVALID: ST §3 chặn mọi action Smart/Opportunity MỚI.
    "data_invalid_window": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0},
            {"dq": "INVALID"},
            {"dq": "INVALID"},
            {"dq": "GOOD", "oscore": 60.0},
            {},
        ],
        "exec_cfg": GATE1_LOW_FRICTION,
    },
    # G — CRASH -> RECOVERY -> NORMAL/STRESSED: chiều Market Regime biến thiên trong khi
    # chiều Execution State chạy độc lập (ST §16 "hai chiều độc lập").
    "crash_regime_cycle": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.00},
            {}, {}, {},
            {"oscore": 80.0, "return7": -0.16, "price": 90.0},   # vào CRASH
            {"oscore": 60.0, "return7": -0.05, "price": 88.0},
            {}, {},
            {"oscore": 50.0, "return7": -0.04, "price": 92.0},   # exit candidate -> RECOVERY
            {}, {},
            {"oscore": 40.0, "return7": -0.11, "price": 93.0},   # hết Recovery
            {}, {},
        ],
        "exec_cfg": GATE1_LOW_FRICTION,
    },
}


def run_scenario(name: str):
    """Chạy `run_engine` thật trên kịch bản `name`. Trả về `RunResult`.

    `_ladder_seq` / `_zone_seq` là bộ đếm cấp module nên được reset trước mỗi lần chạy:
    không reset thì `zone_id` / `ladder_id` trong `decision_log` khác nhau tuỳ THỨ TỰ chạy
    và mọi phép so bản ghi mất tính tất định.
    """
    spec = SCENARIOS[name]
    ladders_mod._ladder_seq = itertools.count(1)
    ladders_mod._zone_seq = itertools.count(1)
    ds, scores, start, end = build_dataset(
        spec["day_specs"], first_local_day=spec.get("first_local_day", "2023-03-01"))
    return run_engine(ds, scores, BASELINE_STRATEGY, spec["exec_cfg"], start, end,
                      contribution=100.0)


def run_scenario_with_grid(name: str):
    """Như `run_scenario`, kèm lưới timestamp của ĐÚNG các nến engine đã duyệt.

    Lưới được dựng lại ĐỘC LẬP từ dataset (không hỏi engine), nên nó kiểm chứng được
    `execution_state_timeline` thay vì tin lời engine.
    """
    spec = SCENARIOS[name]
    ladders_mod._ladder_seq = itertools.count(1)
    ladders_mod._zone_seq = itertools.count(1)
    ds, scores, start, end = build_dataset(
        spec["day_specs"], first_local_day=spec.get("first_local_day", "2023-03-01"))
    res = run_engine(ds, scores, BASELINE_STRATEGY, spec["exec_cfg"], start, end,
                     contribution=100.0)
    ts = _epoch_seconds(ds["ETHUSDT_15m"]["open_time"])
    grid = ts[(ts >= start.timestamp()) & (ts < end.timestamp())]
    return res, [float(x) for x in grid], start


def states_by_candle(res, grid: list[float]) -> list[tuple[float, str]]:
    """Tái dựng trạng thái của TỪNG nến từ `execution_state_timeline` (ghi-khi-đổi).

    Đây chính là phép đọc "trạng thái tại từng thời điểm" mà `CHECK-C2-02` đòi hỏi: mốc
    gần nhất `<=` thời điểm cần hỏi.
    """
    tl = res.execution_state_timeline
    out, k = [], 0
    for ts in grid:
        while k + 1 < len(tl) and tl[k + 1][0] <= ts:
            k += 1
        out.append((ts, str(tl[k][1])))
    return out


def invariant_payload(res) -> dict:
    """Toàn bộ đầu ra ngữ nghĩa của `RunResult` NHƯ NÓ ĐÃ CÓ trước WP-C2."""
    payload = {name: getattr(res, name) for name in PRE_WP_C2_RESULT_FIELDS}
    payload["eth_total"] = res.eth_total
    payload["contributed_total"] = res.contributed_total
    return payload


def _canonical(obj) -> str:
    def default(o):
        try:
            import numpy as np
        except ImportError:  # pragma: no cover
            raise TypeError(o)
        if isinstance(o, (np.floating, np.integer, np.bool_)):
            return o.item()
        raise TypeError(f"không serialize được: {type(o)!r}")

    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), default=default)


def fingerprint(res) -> str:
    """sha256 của payload bất biến — so được giữa hai phía của một thay đổi."""
    return hashlib.sha256(_canonical(invariant_payload(res)).encode()).hexdigest()


def all_fingerprints() -> dict[str, str]:
    return {name: fingerprint(run_scenario(name)) for name in SCENARIOS}


if __name__ == "__main__":
    for k, v in all_fingerprints().items():
        print(f"{k} = {v}")
