"""WP-C2 — bằng chứng PRODUCTION REACHABILITY cho chiều Execution State (CHECK-C2-02/03/05).

Unit test một mình không đủ: gói này phải chứng minh Execution State được sinh ra trên
ĐƯỜNG CHẠY THẬT, ở quy mô thật, chứ không phải được dựng bằng tay trong test.

Công cụ chạy ba lát cắt, tất cả qua đúng hàm production:

1. `metrics.window_metrics` — hàm mà `pipeline.run_gate1` gọi để chạy chín window 24 tháng.
2. `engine.run_engine` toàn kỳ 2019-01-01 → OOS end, cả hai execution config đã commit.
3. Lát 2 lặp lại trên dataset bị **xoá MỘT hàng daily** — cùng thủ thuật `--drop-daily` mà
   `tests/wp_a6_impact_tool.py` dùng để dựng cửa sổ `data_quality = INVALID` dài ~31 ngày
   (do `adr30`) trên dữ liệu thật. Đây là cách quan sát `DATA_BLOCKED` ở quy mô sản xuất.

Với mỗi lát, công cụ báo: số nến, số mốc đổi trạng thái, số bản ghi `market_snapshots`, tập
trạng thái quan sát được, số bản ghi có `execution_state` NULL, và số lần `FUNDING_REQUIRED`
xuất hiện (phải luôn bằng 0 theo `ADR-001`).

Dùng:

    python tests/wp_c2_reachability_tool.py --raw <raw_dir> [--out <file.json>]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from eth_dca_os.data.dataset import load_dataset
from eth_dca_os.data.synth import generate
from eth_dca_os.engine import ExecutionState, run_engine
from eth_dca_os.indicators import compute_daily_indicators
from eth_dca_os.metrics import window_metrics
from eth_dca_os.score import compute_scores

#: Hàng daily bị xoá để dựng cửa sổ INVALID — cùng ngày WP-A6 đã dùng (CONVENTIONS #19).
DROP_DAILY = "2020-06-15"


def _scores(ds):
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    sc = pd.concat([ind, compute_scores(ind)], axis=1)
    return sc.loc[:, ~sc.columns.duplicated()]


def _drop_daily_row(ds, day: str):
    d0 = pd.Timestamp(day, tz="UTC")
    out = dict(ds)
    for k in ("ETHUSDT_1d", "BTCUSDT_1d"):
        df = out[k]
        out[k] = df[df["open_time"] != d0].reset_index(drop=True)
    return out


def observe(label: str, res) -> dict:
    """Rút bằng chứng từ MỘT `RunResult` thật."""
    tl = res.execution_state_timeline
    snaps = res.market_snapshots
    null_states = sum(1 for m in snaps if m.get("execution_state") is None)
    return {
        "run": label,
        "transitions": len(tl),
        "snapshots": len(snaps),
        "purchases": len(res.purchases),
        "states_observed": sorted({str(s) for _, s in tl}),
        "snapshot_states": sorted({str(m["execution_state"]) for m in snaps}),
        "execution_state_null_count": null_states,
        "funding_required_count": sum(
            1 for _, s in tl if s == ExecutionState.FUNDING_REQUIRED),
        "regimes_observed": sorted({m["market_regime"] for m in snaps}),
        "data_quality_observed": sorted({m["data_quality"] for m in snaps}),
    }


def collect(raw_dir: Path) -> dict:
    ds = load_dataset(raw_dir)
    scores = _scores(ds)
    oos_end = pd.Timestamp(ds["ETHUSDT_1d"]["open_time"].max()).tz_localize(None).normalize()

    rows: list[dict] = []

    # Lát 1 — chín window 24 tháng, qua đúng hàm mà Gate 1 gọi.
    wm = window_metrics(ds, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION)
    for wid, w in sorted(wm["windows"].items()):
        rows.append(observe(f"window_metrics/{wid}/gate1_low_friction", w["result"]))

    # Lát 2 — toàn kỳ, cả hai execution config đã commit ở Phase 0.
    for name, ec in (("gate1_low_friction", GATE1_LOW_FRICTION),
                     ("gate3_realistic", GATE3_REALISTIC)):
        res = run_engine(ds, scores, BASELINE_STRATEGY, ec,
                         pd.Timestamp("2019-01-01"), oos_end)
        rows.append(observe(f"full_period/{name}", res))

    # Lát 3 — cùng đường chạy, dataset thiếu MỘT hàng daily -> cửa sổ INVALID thật.
    ds_gap = _drop_daily_row(ds, DROP_DAILY)
    scores_gap = _scores(ds_gap)
    for name, ec in (("gate1_low_friction", GATE1_LOW_FRICTION),
                     ("gate3_realistic", GATE3_REALISTIC)):
        res = run_engine(ds_gap, scores_gap, BASELINE_STRATEGY, ec,
                         pd.Timestamp("2019-01-01"), oos_end)
        rows.append(observe(f"full_period_drop_daily_{DROP_DAILY}/{name}", res))

    union = sorted({s for r in rows for s in r["states_observed"]})
    return {
        "runs": rows,
        "states_observed_union": union,
        "states_never_observed": sorted(
            {s.value for s in ExecutionState} - set(union)),
        "total_snapshots": sum(r["snapshots"] for r in rows),
        "total_null_execution_state": sum(r["execution_state_null_count"] for r in rows),
        "total_funding_required": sum(r["funding_required_count"] for r in rows),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    raw = Path(a.raw)
    if not any(raw.glob("*.parquet")):
        generate(raw)
    payload = collect(raw)

    for r in payload["runs"]:
        print(f"{r['run']:<52} transitions={r['transitions']:>5} "
              f"snapshots={r['snapshots']:>5} null={r['execution_state_null_count']} "
              f"FUNDING_REQUIRED={r['funding_required_count']} "
              f"states={','.join(r['states_observed'])}")
    print()
    print(f"states_observed_union       = {payload['states_observed_union']}")
    print(f"states_never_observed       = {payload['states_never_observed']}")
    print(f"total_snapshots             = {payload['total_snapshots']}")
    print(f"total_null_execution_state  = {payload['total_null_execution_state']}")
    print(f"total_funding_required      = {payload['total_funding_required']}")
    if a.out:
        Path(a.out).write_text(json.dumps(payload, indent=1, ensure_ascii=False))
        print(f"payload_written             = {a.out}")


if __name__ == "__main__":
    main()
