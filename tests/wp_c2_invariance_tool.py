"""WP-C2 — công cụ đo BẤT BIẾN backtest (CHECK-C2-06) và quan sát Execution State.

Cùng họ với `tests/wp_a3_impact_tool.py` và `tests/wp_a6_impact_tool.py`: một công cụ đo
chạy được ở CẢ HAI phía của một thay đổi (trước / sau), ghi ra một payload JSON chuẩn tắc
để so sánh **bit-for-bit**.

Payload có hai khối tách biệt:

- `invariance` — TOÀN BỘ đầu ra ngữ nghĩa mà engine/pipeline sinh ra TRƯỚC WP-C2. Khối này
  phải trùng khớp TUYỆT ĐỐI giữa hai lần chạy (cùng dataset, cùng config, cùng seed).
- `wp_c2_observability` — các trường do WP-C2 thêm (`market_snapshots`,
  `execution_state_counts`). Khối này CHỈ tồn tại ở lần chạy sau; nó nằm ngoài phép so
  bất biến theo đúng nghĩa "trường mới, không phải trường bị đổi".

Các trường metadata KHÔNG ngữ nghĩa bị loại tường minh khỏi `invariance` (xem
`NON_SEMANTIC_RUN_RECORD_KEYS`): `run_id` (uuid4), `created_at` (đồng hồ), `metrics_path`
(đường dẫn tmp), `code_commit` (SHA của chính commit đang đo). Không trường nào khác bị
loại — không "normalize" một khác biệt có nghĩa nào.

Dùng:

    python tests/wp_c2_invariance_tool.py --raw <raw_dir> --out <file.json> \
        [--gate2-limit N] [--gate3-limit N] [--controls-sims N]

Nếu `--raw` chưa có dataset thì công cụ tự sinh synthetic dataset (seed cố định
`synth.SYNTH_SEED`) — cùng một thư mục raw phải được dùng lại cho cả hai phía.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

#: Metadata không mang ngữ nghĩa chiến lược/backtest — thay đổi ở mọi lần chạy dù mã không
#: đổi, nên phải loại khỏi phép so bit-for-bit. Danh sách này là ĐẦY ĐỦ và tường minh.
NON_SEMANTIC_RUN_RECORD_KEYS = ("run_id", "created_at", "metrics_path", "code_commit")

#: Trường của `RunResult` do WP-C2 thêm — tách khỏi khối bất biến.
WP_C2_RESULT_FIELDS = ("market_snapshots", "execution_state_timeline")


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
    """Toàn bộ đầu ra ngữ nghĩa của `RunResult` NHƯ NÓ ĐÃ CÓ trước WP-C2."""
    return {
        "eth_total": res.eth_total,
        "contributed_total": res.contributed_total,
        "purchases": res.purchases,
        "contributions": res.contributions,
        "counters": res.counters,
        "monthly_deployments": res.monthly_deployments,
        "cash_samples": res.cash_samples,
        "decision_log": res.decision_log,
        "opp_cap_samples": res.opp_cap_samples,
        "regime_timeline": res.regime_timeline,
    }


def _result_observability(res) -> dict:
    """Trường do WP-C2 thêm; rỗng khi chạy trên cây mã trước WP-C2."""
    return {name: getattr(res, name) for name in WP_C2_RESULT_FIELDS
            if hasattr(res, name)}


def collect(raw_dir: Path, out_dir: Path, *, gate2_limit: int | None,
            gate3_limit: int | None, controls_sims: int) -> dict:
    prep = Prepared(raw_dir)
    freeze_manifests(out_dir / "manifests")

    g1 = run_gate1(prep, out_dir)
    g2 = run_gate2(prep, out_dir, limit=gate2_limit)
    g3 = run_gate3(prep, out_dir, limit=gate3_limit)
    ctl = run_controls(prep, out_dir, g1["_full_run_monthly_tranches"],
                       g1["_full_run_eth"], n_sims=controls_sims)
    vd = run_verdict(g1, g2, g3, ctl, out_dir, prep.dataset_hash)

    # Chạy engine toàn kỳ ở CẢ HAI execution config — đây là bản ghi chi tiết nhất
    # (từng purchase, từng ledger sample) nên là phép thử nhạy nhất cho "hành vi không đổi".
    scores = prep.scores(BASELINE_STRATEGY.score_weights)
    full_runs, full_obs = {}, {}
    for name, exec_cfg in (("gate1_low_friction", GATE1_LOW_FRICTION),
                           ("gate3_realistic", GATE3_REALISTIC)):
        res = run_engine(prep.dataset, scores, BASELINE_STRATEGY, exec_cfg,
                         pd.Timestamp("2019-01-01"), prep.oos_end())
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
            "wp_c2_observability": {"full_period_runs": full_obs}}


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
    obs = payload["wp_c2_observability"]["full_period_runs"]
    for name, block in obs.items():
        tl = block.get("execution_state_timeline") or []
        snaps = block.get("market_snapshots") or []
        print(f"observability[{name}] transitions={len(tl)} snapshots={len(snaps)} "
              f"states={sorted({str(s) for _, s in tl})} "
              f"snapshot_states={sorted({str(m['execution_state']) for m in snaps})}")


if __name__ == "__main__":
    main()
