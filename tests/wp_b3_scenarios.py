"""WP-B3 — kịch bản engine tất định để chứng minh audit trail có ĐƯỜNG SINH THẬT.

Nguyên tắc giống `tests/wp_c2_scenarios.py` và không dựng builder thứ hai: dataset đến từ
`wp_a3_harness.build_dataset`, mọi bản ghi `decision_log` được sinh bởi `run_engine` THẬT,
không bản ghi nào được dựng bằng tay.

Bốn kịch bản của `WP-C2` (`wait_only`, `smart_action_cycle`, `data_invalid_window`,
`crash_regime_cycle`) KHÔNG bị đụng tới — chúng đang khoá fingerprint hành vi của một gói
đã `DONE`. Module này chỉ THÊM những kịch bản mà bốn kịch bản đó không phủ: các loại sự
kiện ST §20 còn lại (`MAX_ZONES_BLOCK`, `ACTION_MISSED`, `ACTION_TTL_EXPIRED`,
`MONTH_END_BASE`, `DATA_DEGRADED`) và nhãn ST §9 `EXECUTED_EARLY`.
"""
from __future__ import annotations

import itertools

import pandas as pd

import eth_dca_os.ladders as ladders_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, ExecutionConfig
from eth_dca_os.engine import TZ_OFFSET, run_engine
from wp_a3_harness import build_dataset

DAY = 86400.0
NOON = 12 * 3600

#: Ma sát ĐÚNG bằng một điểm trong lưới Gate 3 đã đóng băng (`manifests.GATE3_GRID`):
#: `user_delay = 12h`, `funding_delay = 4h`, `ON_DEMAND`, `action_ttl = 12h`. Tổng delay
#: 16h > TTL 12h nên action hết hạn trước khi tới lượt fill -> `ACTION_MISSED`. Đây là một
#: cấu hình PRODUCTION thật, không phải cấu hình bịa để lấy độ phủ.
GATE3_SLOW_FUNDING = ExecutionConfig(
    user_delay_seconds=12 * 3600, funding_policy="ON_DEMAND",
    funding_delay_seconds=4 * 3600, config_name="gate3_grid_slow_funding",
)

#: TTL LỆCH LƯỚI nến 15m (12h + 100s). Chỉ khi TTL không phải bội số của 900s thì nhánh
#: `ACTION_TTL_EXPIRED` mới tới lượt chạy — xem `docs/CONVENTIONS.md` #23(e) và
#: `PROJECT/HARDENING_BACKLOG.md` H-36. Cấu hình hợp lệ theo `ExecutionConfig`.
OFF_GRID_TTL = ExecutionConfig(
    user_delay_seconds=43000, funding_policy="ON_DEMAND", funding_delay_seconds=1000,
    action_ttl_seconds=12 * 3600 + 100, config_name="off_grid_ttl",
)


def _month(specs: list[dict], n_days: int) -> list[dict]:
    """Kéo dài kịch bản tới `n_days` ngày local bằng những ngày yên tĩnh."""
    return specs + [{} for _ in range(max(0, n_days - len(specs)))]


#: Mỗi kịch bản: day_specs, exec_cfg, và (tuỳ chọn) `drop` — cửa sổ nến bị xoá khỏi chuỗi
#: 15m, mô phỏng lỗ hổng dữ liệu thật (BT §18).
SCENARIOS: dict[str, dict] = {
    # OSCORE 75 mở CẢ ladder Smart (3 zone) LẪN ladder Opportunity (5 zone) trong cùng một
    # nến; nến kế tiếp giá thủng 50 nên cả tám zone cùng TRIGGERED. `max_zones_per_cycle = 2`
    # (ST §15.1) nên đúng hai action được tạo, sáu zone còn lại bị chặn -> `MAX_ZONES_BLOCK`.
    "max_zones_block": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 75.0, "low_dip": 50.0},
            {}, {}, {}, {},
        ],
        "exec_cfg": GATE1_LOW_FRICTION,
    },
    # Ma sát Gate 3: tổng delay 16h > TTL 12h -> action hết hạn -> `ACTION_MISSED`.
    "action_missed": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0},
            {"low_dip": 90.0},
            {}, {}, {},
        ],
        "exec_cfg": GATE3_SLOW_FUNDING,
    },
    # TTL lệch lưới nến -> nhánh `ACTION_TTL_EXPIRED` mới tới lượt chạy.
    "action_ttl_expired": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0},
            {"low_dip": 90.0},
            {}, {}, {},
        ],
        "exec_cfg": OFF_GRID_TTL,
    },
    # Chất lượng dữ liệu tụt xuống DEGRADED -> `DATA_DEGRADED` (ST §3/§20).
    "data_degraded": {
        "day_specs": [
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0},
            {"dq": "DEGRADED"},
            {"dq": "GOOD"},
            {}, {},
        ],
        "exec_cfg": GATE1_LOW_FRICTION,
    },
    # OSCORE >= 70 khi snapshot daily mới active -> kéo sớm MỘT tranche Base
    # (`BASE_ADVANCE_SCORE` + nhãn ST §9 `EXECUTED_EARLY`), và ngày gốc KHÔNG lặp lại.
    "base_advance_early": {
        "day_specs": _month([
            {"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 75.0},           # 07:00 Day 2: kéo sớm tranche Day 3
        ], 6),
        "exec_cfg": GATE1_LOW_FRICTION,
    },
    # Lỗ hổng dữ liệu che 12:00 Day 13 (fill trễ trong ngày -> nhãn `DELAYED_DATA_FILL`) và
    # che toàn bộ nửa sau Day 23 (tranche Base cuối tháng không chạy được đúng ngày ->
    # settle Day 25 -> `MONTH_END_BASE`).
    "base_gap_month_end": {
        "day_specs": _month([{"price": 100.0, "oscore": 20.0, "return7": 0.0}], 27),
        "exec_cfg": GATE1_LOW_FRICTION,
        "drop": [("2023-03-13 12:00", "2023-03-13 12:59"),
                 ("2023-03-23 12:00", "2023-03-23 23:59")],
    },
}


def _drop_candles(dataset: dict, windows) -> dict:
    """Xoá các nến 15m nằm trong `windows` (giờ LOCAL) — mô phỏng lỗ hổng dữ liệu thật."""
    e15 = dataset["ETHUSDT_15m"]
    local = e15["open_time"] + pd.Timedelta(seconds=TZ_OFFSET)
    keep = pd.Series(True, index=e15.index)
    for lo, hi in windows:
        keep &= ~((local >= pd.Timestamp(lo, tz="UTC")) & (local <= pd.Timestamp(hi, tz="UTC")))
    out = dict(dataset)
    out["ETHUSDT_15m"] = e15[keep].reset_index(drop=True)
    return out


def run_scenario(name: str, contribution: float = 100.0):
    """Chạy `run_engine` THẬT trên kịch bản `name`; trả `RunResult`.

    Bộ đếm `zone_id`/`ladder_id` là biến cấp module của `ladders.py` nên được reset trước
    mỗi lần chạy — không reset thì hai lần chạy cùng kịch bản cho id khác nhau tuỳ THỨ TỰ
    chạy, và mọi phép so bản ghi mất tính tất định.
    """
    spec = SCENARIOS[name]
    ladders_mod._ladder_seq = itertools.count(1)
    ladders_mod._zone_seq = itertools.count(1)
    ds, scores, start, end = build_dataset(
        spec["day_specs"], first_local_day=spec.get("first_local_day", "2023-03-01"))
    if spec.get("drop"):
        ds = _drop_candles(ds, spec["drop"])
    return run_engine(ds, scores, BASELINE_STRATEGY, spec["exec_cfg"], start, end,
                      contribution=contribution)


def reason_counts(res) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in res.decision_log:
        out[d["reason_code"]] = out.get(d["reason_code"], 0) + 1
    return out


if __name__ == "__main__":
    for name in SCENARIOS:
        r = run_scenario(name)
        print(f"{name}: rows={len(r.decision_log)} {reason_counts(r)}")
