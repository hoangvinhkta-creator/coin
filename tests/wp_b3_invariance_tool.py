"""WP-B3 — công cụ đo BẤT BIẾN tài chính/chiến lược (CHECK-B3-07) và quan sát audit trail.

Cùng họ với `tests/wp_c2_invariance_tool.py` (và `wp_a3_impact_tool.py` /
`wp_a6_impact_tool.py`): MỘT công cụ chạy được ở CẢ HAI phía của một thay đổi, ghi ra một
payload JSON chuẩn tắc để so **bit-for-bit**.

Khác biệt DUY NHẤT so với công cụ của WP-C2, và là khác biệt có chủ ý:

- `decision_log` **rời khỏi** khối bất biến. Đó chính là bề mặt WP-B3 cố ý thay đổi; giữ
  nó trong khối bất biến sẽ biến phép đo thành một phép so luôn đỏ, không nói được điều gì.
- `execution_state_timeline` và `market_snapshots` (WP-C2, đã `DONE`) **đi vào** khối bất
  biến. WP-B3 tiêu thụ hợp đồng WP-C2 chứ không được đổi nó, nên hai trường này phải trùng
  khớp tuyệt đối trước–sau.

Kết quả: khối `invariance` chứa ĐÚNG mọi đầu ra tài chính/chiến lược mà WP-B3 không được
phép chạm — purchase, contribution/deployment, vốn/cash, opportunity fund, regime, hành vi
execution, metric Gate 1/2/3, controls và verdict — cộng thêm toàn bộ đầu ra của WP-C2.

Dùng:

    python tests/wp_b3_invariance_tool.py --raw <raw_dir> --out <file.json> \
        [--gate2-limit N] [--gate3-limit N] [--controls-sims N]

Nếu `--raw` chưa có dataset thì công cụ tự sinh synthetic dataset (seed cố định
`synth.SYNTH_SEED`) — cùng một thư mục raw phải được dùng lại cho cả hai phía.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import pandas as pd

from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from eth_dca_os.data.synth import generate
from eth_dca_os.engine import run_engine
from eth_dca_os.manifests import freeze_manifests
from eth_dca_os.pipeline import (
    Prepared,
    run_controls,
    run_gate1,
    run_gate2,
    run_gate3,
    run_verdict,
)
from eth_dca_os.reporting import _jsonable

#: Metadata không mang ngữ nghĩa chiến lược/backtest — đổi ở mọi lần chạy dù mã không đổi.
NON_SEMANTIC_RUN_RECORD_KEYS = ("run_id", "created_at", "metrics_path", "code_commit")

#: Trường `RunResult` PHẢI trùng khớp bit-for-bit trước–sau WP-B3.
#: Gồm toàn bộ đầu ra tài chính/chiến lược có từ trước, CỘNG hai trường của WP-C2.
INVARIANT_RESULT_FIELDS = (
    "purchases", "contributions", "counters", "monthly_deployments",
    "cash_samples", "opp_cap_samples", "regime_timeline",
    "execution_state_timeline", "market_snapshots",
)

#: Trường WP-B3 CỐ Ý đổi — nằm NGOÀI phép so bất biến.
WP_B3_OBSERVABILITY_FIELDS = ("decision_log",)


def _strip_run_record(payload):
    """Loại metadata không ngữ nghĩa khỏi mọi `run_record` lồng trong payload."""
    if isinstance(payload, dict):
        return {k: (_strip_run_record(v) if k != "run_record"
                    else {kk: vv for kk, vv in v.items()
                          if kk not in NON_SEMANTIC_RUN_RECORD_KEYS})
                for k, v in payload.items()}
    if isinstance(payload, list):
        return [_strip_run_record(v) for v in payload]
    return payload


def _result_invariant(res) -> dict:
    """Mọi đầu ra ngữ nghĩa của `RunResult` mà WP-B3 KHÔNG được đổi."""
    out = {name: getattr(res, name) for name in INVARIANT_RESULT_FIELDS
           if hasattr(res, name)}
    out["eth_total"] = res.eth_total
    out["contributed_total"] = res.contributed_total
    return out


def _result_observability(res) -> dict:
    """Bề mặt audit trail — rỗng (hoặc thưa) khi chạy trên cây mã trước WP-B3."""
    return {name: getattr(res, name) for name in WP_B3_OBSERVABILITY_FIELDS
            if hasattr(res, name)}


def collect(raw_dir: Path, out_dir: Path, *, gate2_limit: int | None,
            gate3_limit: int | None, controls_sims: int) -> dict:
    prep = Prepared(raw_dir)
    freeze_manifests(out_dir / "manifests")

    t0 = time.perf_counter()
    g1 = run_gate1(prep, out_dir)
    g2 = run_gate2(prep, out_dir, limit=gate2_limit)
    g3 = run_gate3(prep, out_dir, limit=gate3_limit)
    ctl = run_controls(prep, out_dir, g1["_full_run_monthly_tranches"],
                       g1["_full_run_eth"], n_sims=controls_sims)
    vd = run_verdict(g1, g2, g3, ctl, out_dir, prep.dataset_hash)
    gates_seconds = time.perf_counter() - t0

    # Engine toàn kỳ ở CẢ HAI execution config — bản ghi chi tiết nhất (từng purchase,
    # từng sample ledger), nên là phép thử nhạy nhất cho "hành vi không đổi".
    scores = prep.scores(BASELINE_STRATEGY.score_weights)
    full_runs, full_obs, full_seconds = {}, {}, {}
    for name, exec_cfg in (("gate1_low_friction", GATE1_LOW_FRICTION),
                           ("gate3_realistic", GATE3_REALISTIC)):
        t1 = time.perf_counter()
        res = run_engine(prep.dataset, scores, BASELINE_STRATEGY, exec_cfg,
                         pd.Timestamp("2019-01-01"), prep.oos_end())
        full_seconds[name] = time.perf_counter() - t1
        full_runs[name] = _result_invariant(res)
        full_obs[name] = _result_observability(res)

    invariance = {
        "dataset_hash": prep.dataset_hash,
        "strategy_config_hash": BASELINE_STRATEGY.hash,
        "execution_config_hash": {"gate1_low_friction": GATE1_LOW_FRICTION.hash,
                                  "gate3_realistic": GATE3_REALISTIC.hash},
        "gate1": {k: v for k, v in g1.items() if not k.startswith("_")},
        "gate1_full_run_monthly_tranches": g1["_full_run_monthly_tranches"],
        "gate1_full_run_eth": g1["_full_run_eth"],
        "gate2": g2,
        "gate3": g3,
        "controls": ctl,
        "verdict": vd,
        "full_period_runs": full_runs,
    }
    return {"invariance": _strip_run_record(invariance),
            "wp_b3_observability": {"full_period_runs": full_obs},
            "timing": {"gates_seconds": gates_seconds, "full_run_seconds": full_seconds}}


def canonical(payload) -> str:
    """Chuỗi JSON chuẩn tắc — `repr` float của Python round-trip đúng bit."""
    return json.dumps(_jsonable(payload), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--results-dir", default=None,
                    help="thư mục ghi metrics/run record (mặc định: cạnh --out)")
    ap.add_argument("--gate2-limit", type=int, default=6)
    ap.add_argument("--gate3-limit", type=int, default=6)
    ap.add_argument("--controls-sims", type=int, default=200)
    a = ap.parse_args(argv)

    raw = Path(a.raw)
    if not any(raw.glob("*.parquet")):
        generate(raw)
    out_json = Path(a.out)
    results = Path(a.results_dir) if a.results_dir else out_json.parent / "results"

    payload = collect(raw, results, gate2_limit=a.gate2_limit,
                      gate3_limit=a.gate3_limit, controls_sims=a.controls_sims)
    text = canonical(payload)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(text)

    inv = canonical(payload["invariance"])
    print(f"invariance_sha256 = {hashlib.sha256(inv.encode()).hexdigest()}")
    print(f"invariance_bytes  = {len(inv)}")
    print(f"payload_written   = {out_json}")
    print(f"gates_seconds     = {payload['timing']['gates_seconds']:.1f}")
    for name, secs in payload["timing"]["full_run_seconds"].items():
        print(f"full_run_seconds[{name}] = {secs:.2f}")
    for name, block in payload["wp_b3_observability"]["full_period_runs"].items():
        log = block.get("decision_log") or []
        codes = sorted({d.get("reason_code") for d in log})
        print(f"decision_log[{name}] rows={len(log)} distinct_reason_codes={len(codes)}")
        print(f"    codes={codes}")


if __name__ == "__main__":
    main()
