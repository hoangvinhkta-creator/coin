"""Reporting & reproducibility records — Backtest §16, §20; Data Model §12."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from . import BACKTEST_SPEC_VERSION, MASTER_SEED, STRATEGY_VERSION


def _jsonable(x):
    import numpy as np
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, float) and x != x:
        return None
    return x


def save_run(out_dir: str | Path, run_type: str, payload: dict, *,
             strategy_config_hash: str, execution_config_hash: str,
             dataset_hash: str, manifest_hash: str | None = None,
             start_date=None, end_date=None, verdict=None) -> dict:
    """Ghi backtest_runs record + metrics JSON (Data Model §12, Backtest §20)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = f"{run_type.lower()}_{uuid.uuid4().hex[:12]}"
    metrics_path = out / f"{run_id}_metrics.json"
    metrics_path.write_text(json.dumps(_jsonable(payload), indent=1, ensure_ascii=False))
    record = {
        "run_id": run_id,
        "strategy_version": STRATEGY_VERSION,
        "backtest_spec_version": BACKTEST_SPEC_VERSION,
        "strategy_config_hash": strategy_config_hash,
        "execution_config_hash": execution_config_hash,
        "sensitivity_manifest_hash": manifest_hash,
        "dataset_hash": dataset_hash,
        "start_date": str(start_date), "end_date": str(end_date),
        "master_seed": MASTER_SEED,
        "run_type": run_type,
        "metrics_path": str(metrics_path),
        "verdict": verdict,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    runs_file = out / "backtest_runs.jsonl"
    with open(runs_file, "a") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def print_gate1_report(g1_payload: dict) -> str:
    lines = ["=== GATE 1 — structural value ==="]
    wm = g1_payload["window_metrics"]
    lines.append(f"{'Window':<6} {'AE %':>8}")
    for k, v in wm["ae_by_window"].items():
        lines.append(f"{k:<6} {v:>8.2f}")
    for off, v in wm["anchor_set_medians"].items():
        lines.append(f"AnchorSetMedian +{off}M: {v:.2f}")
    lines.append(f"PrimaryMedian: {wm['primary_median']:.2f}")
    lines.append(f"PooledMedian (DESCRIPTIVE): {wm['pooled_median_descriptive']:.2f}")
    g = g1_payload["gate1"]
    lines.append(f"Gate 1: {'PASS' if g['pass'] else 'FAIL'}"
                 f"{' (STRONG)' if g.get('strong') else ''}")
    o = g1_payload["oos"]
    flag = " [SHORT_OOS]" if o.get("short_oos") else ""
    lines.append(f"OOS: AE {o['ae']:.2f} | {o['oos_months']} tháng{flag} | "
                 f"{'PASS' if o['ae'] >= 100 else 'FAIL'}")
    return "\n".join(lines)
