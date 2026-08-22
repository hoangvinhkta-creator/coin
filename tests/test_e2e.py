"""E2E smoke: synth -> freeze -> gate1 -> gate2/3 (dev-limit) -> controls -> verdict.

Chạy trên synthetic data — chỉ kiểm cơ chế end-to-end và reproducibility,
KHÔNG phải official numbers.
"""
import json

import pytest

from eth_dca_os.data.synth import generate
from eth_dca_os.manifests import freeze_manifests
from eth_dca_os.pipeline import Prepared, run_controls, run_gate1, run_gate2, run_gate3, run_verdict


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    root = tmp_path_factory.mktemp("e2e")
    raw = root / "raw"
    out = root / "results"
    generate(raw, start="2018-01-01", end="2026-06-30")
    return raw, out


def test_full_pipeline_smoke(env):
    raw, out = env
    freeze_meta = freeze_manifests(out / "manifests")
    assert freeze_meta["gate2"]["denominator"] == 219
    assert freeze_meta["gate3"]["size"] == 114

    prep = Prepared(raw)
    g1 = run_gate1(prep, out)
    assert len(g1["window_metrics"]["ae_by_window"]) == 9
    assert g1["oos"]["oos_months"] >= 17
    assert isinstance(g1["gate1"]["pass"], bool)

    g2 = run_gate2(prep, out, limit=3)
    assert g2["official"] is False
    assert g2["expected_denominator"] == 219
    assert len(g2["per_config"]) == 3

    g3 = run_gate3(prep, out, limit=2)
    assert g3["official"] is False
    assert g3["expected_manifest_size"] == 114
    assert "net_edge_primary_median" in g3["realistic"]
    attr = g3["shortfall_attribution"]
    assert set(attr) >= {"manual_delay_pp", "funding_pp", "fee_slippage_pp"}

    ctl = run_controls(prep, out, g1["_full_run_monthly_deployments"],
                       g1["_full_run_eth"], n_sims=30)
    assert "p95" in ctl["random_timing"]

    v = run_verdict(g1, g2, g3, ctl, out, prep.dataset_hash)
    assert v["verdict"]["verdict"] in ("BUILD", "BUILD_WITH_MODIFICATIONS",
                                       "INCONCLUSIVE", "DO_NOT_BUILD")
    assert v["official"] is False and "warning" in v

    # backtest_runs record ghi đủ hash + seed
    runs = [json.loads(l) for l in (out / "backtest_runs.jsonl").read_text().splitlines()]
    assert len(runs) >= 4
    for r in runs:
        assert r["dataset_hash"] and r["strategy_config_hash"] and r["master_seed"] == 42


def test_gate1_reproducible(env):
    raw, out = env
    prep1, prep2 = Prepared(raw), Prepared(raw)
    a = run_gate1(prep1, out)
    b = run_gate1(prep2, out)
    assert a["window_metrics"]["ae_by_window"] == b["window_metrics"]["ae_by_window"]
    assert a["window_metrics"]["primary_median"] == b["window_metrics"]["primary_median"]
