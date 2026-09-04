"""WP-B1 -- regression tests for the SECOND fresh Independent E2 findings
(docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-after-repair-fail.md, review E2-WP-B1-003):

E2-B1-F01 (still open after first repair): `_numeric_and_finite()` accepted `+inf`/`-inf`
(and Python `bool`) as valid evidence for FS-08, letting an infinite/boolean P95 or v2_eth
produce a known FALSE/TRUE instead of UNKNOWN.

E2-B1-F02 (still open after first repair): non-official evidence was correctly blocked from
`can_proceed_to_app=true`, but the persisted/returned verdict LABEL still read "BUILD" --
canonical interpretation A (frozen CHECK-B1-01/07/09, reconstructed by the fresh E2) requires
BOTH `verdict != BUILD` AND `can_proceed_to_app=false` for non-official evidence.

Both repairs stay inside CAP-VERDICT/WP-B1 (failure_signals.py, pipeline.py). No engine/
strategy/gate/threshold change. No T-06 rerun. No re-run of the validated post-F-017 1000-sim
replay (that evidence used complete, finite, official inputs and is untouched by these two
fixes, which only change behavior for missing/invalid/non-official evidence).
"""
import math

import numpy as np
import pytest

from eth_dca_os.failure_signals import _numeric_and_finite, evaluate_failure_signals
from eth_dca_os.pipeline import run_verdict
from eth_dca_os.reporting import ProvenanceUnresolvedError
import eth_dca_os.reporting as reporting

GOOD_WINDOWS = {"W1": 104.0, "W2": 103.0, "W3": 105.0, "W4": 102.0, "W5": 106.0,
                "W6": 103.0, "W7": 104.0, "W8": 102.0, "W9": 103.0}


# =========================================================== E2-B1-F01 v2: true finite validation

@pytest.mark.parametrize("value", [10.0, 0, -5, 1e300, np.float64(3.14), np.int64(7)])
def test_numeric_and_finite_accepts_ordinary_and_numpy_numbers(value):
    assert _numeric_and_finite(value) is True


@pytest.mark.parametrize("value", [
    None, float("nan"), float("inf"), float("-inf"),
    np.float64("nan"), np.float64("inf"), np.float64("-inf"),
    True, False, np.bool_(True), np.bool_(False),
    "10.0", "abc", object(),
])
def test_numeric_and_finite_rejects_invalid_evidence(value):
    assert _numeric_and_finite(value) is False


@pytest.mark.parametrize("v2_eth,f_p95,g_p95", [
    (10.0, None, 9.5), (10.0, 9.0, None), (10.0, None, None),   # missing (retained from repair 1)
    (None, 9.0, 9.5),
    (float("nan"), 9.0, 9.5), (10.0, float("nan"), 9.5), (10.0, 9.0, float("nan")),
    (float("inf"), 9.0, 9.5), (float("-inf"), 9.0, 9.5),
    (10.0, float("inf"), 9.5), (10.0, float("-inf"), 9.5),
    (10.0, 9.0, float("inf")), (10.0, 9.0, float("-inf")),
    (10.0, "10.0", 9.5),
    (10.0, "not-a-number", 9.5),
    (10.0, object(), 9.5),
    (10.0, True, 9.5),
    (10.0, np.bool_(True), 9.5),
])
def test_fs08_unknown_for_every_invalid_or_incomplete_input(v2_eth, f_p95, g_p95):
    fs = evaluate_failure_signals(v2_eth=v2_eth, random_timing_p95=f_p95, random_anchor_p95=g_p95)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_valid_complete_finite_inputs_still_compute_normally():
    """The already-validated post-F-017 complete-input formula is untouched by this repair."""
    fs = evaluate_failure_signals(v2_eth=14.910758150139896, random_timing_p95=14.887400583487747,
                                  random_anchor_p95=14.813546903782814)
    assert fs["signals"]["FS-08"] is False   # v2_eth beats both P95 -> matches owner replay


def test_fs08_infinity_cannot_leak_build_end_to_end():
    """Production-reachable regression for the E2-B1-F01 v2 counterexample: F=-inf with V2
    beating G must not silently resolve to a known FS-08 and must not allow BUILD."""
    from eth_dca_os.verdict import decide_verdict
    fs = evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, concentration={"ae_ex_month": 101.0,
                                  "ae_ex_quarter": 100.5}, opportunity_cap_hit_share=0.1,
                                  regime_advantage_share=0.4, adjacent_config_flip=False,
                                  vif_any_severe=False, corr_high_redundancy=False,
                                  score_bimodal=False, avg_cash_ratio=0.1, gate1_primary_ae=104.0,
                                  shortfall_pp=1.0, gate2_oos_pass_share=0.8, oos_ae=101.0,
                                  v2_eth=10.0, random_timing_p95=float("-inf"),
                                  random_anchor_p95=9.5)
    assert fs["signals"]["FS-08"] is None
    g_ok = {"pass": True}
    v = decide_verdict(g_ok, {"pass": True}, g_ok, g_ok, fs)
    assert v["verdict"] != "BUILD"
    assert v["can_proceed_to_app"] is False


# =========================================================== E2-B1-F02 v2: verdict label must
# =========================================================== also fail closed (canonical A)

def _clean_g1(official: bool):
    return {"diagnostics": {"vif": {"any_severe": False},
                            "redundancy_flags": {"x_high_redundancy": False},
                            "score_distribution": {"bimodal_fs05": False}},
            "window_metrics": {"ae_by_window": dict(GOOD_WINDOWS), "primary_median": 104.0},
            "concentration": {"ae_ex_month": 101.0, "ae_ex_quarter": 100.5},
            "opportunity_cap_hit": {"share": 0.1}, "regime_advantage": {"share": 0.4},
            "cash_ratio": {"avg": 0.1}, "oos": {"ae": 101.0, "pass": True},
            "gate1": {"pass": True}, "official": official}


def _clean_g2(official: bool):
    per_config = [
        {"config_name": "baseline", "gate1": {"pass": True}, "oos_ae": 101.0},
        {"config_name": "ofat_base_pct=0.5", "gate1": {"pass": True}, "oos_ae": 101.0},
    ]
    return {"per_config": per_config,
            "gate2": {"pass": True, "oos_pass_share_reported_separately": 0.8},
            "official": official, "official_reason": "verified" if official else "dev_limit_set"}


def _clean_g3(official: bool):
    return {"gate3": {"pass": True}, "realistic": {"primary_median_ae": 103.0},
            "official": official}


def _clean_controls(official: bool):
    return {"v2_eth": 10.0, "random_timing": {"p95": 9.0}, "random_anchor": {"p95": 9.5},
            "official": official}


@pytest.mark.parametrize("label,flags", [
    ("gate1_false", (False, True, True, True)),
    ("gate2_false", (True, False, True, True)),
    ("gate3_false", (True, True, False, True)),
    ("controls_false", (True, True, True, False)),
    ("gate1_and_controls_false", (False, True, True, False)),
    ("all_false", (False, False, False, False)),
])
def test_officiality_matrix_verdict_label_never_build(tmp_path, label, flags):
    """B-G: exactly the fresh-E2 counterexample table -- every non-official combination must
    downgrade BOTH the verdict label and can_proceed_to_app, and this must be true of the
    PERSISTED record, not just the in-memory return value."""
    g1_off, g2_off, g3_off, ctl_off = flags
    payload = run_verdict(_clean_g1(g1_off), _clean_g2(g2_off), _clean_g3(g3_off),
                          _clean_controls(ctl_off), tmp_path / label, dataset_hash="dummy")
    assert payload["official"] is False
    assert payload["verdict"]["verdict"] != "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is False

    # persisted record must not retain BUILD either (E2-B1-F02's original counterexample was
    # specifically that save_run(..., verdict=v["verdict"]) persisted "BUILD").
    runs_file = (tmp_path / label) / "backtest_runs.jsonl"
    lines = runs_file.read_text().splitlines()
    import json
    assert json.loads(lines[-1])["verdict"] != "BUILD"


def test_officiality_all_official_still_persists_build(tmp_path):
    payload = run_verdict(_clean_g1(True), _clean_g2(True), _clean_g3(True),
                          _clean_controls(True), tmp_path, dataset_hash="dummy")
    assert payload["official"] is True
    assert payload["verdict"]["verdict"] == "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is True
    import json
    runs_file = tmp_path / "backtest_runs.jsonl"
    assert json.loads(runs_file.read_text().splitlines()[-1])["verdict"] == "BUILD"


def test_unresolved_provenance_still_fails_loud_no_build_payload_escapes(tmp_path, monkeypatch):
    """H: unresolved required provenance must still refuse to return any payload (pre-existing
    WP-A1 fail-loud mechanism, unaffected by this repair)."""
    monkeypatch.setattr(reporting, "_get_code_commit", lambda: "unknown")
    with pytest.raises(ProvenanceUnresolvedError):
        run_verdict(_clean_g1(True), _clean_g2(True), _clean_g3(True),
                   _clean_controls(True), tmp_path, dataset_hash="dummy")


# =========================================================== Retained: post-F-017 evidence
# =========================================================== unchanged by either repair

def test_post_f017_owner_replay_values_unchanged_by_this_repair():
    fs = evaluate_failure_signals(v2_eth=14.910758150139896, random_timing_p95=14.887400583487747,
                                  random_anchor_p95=14.813546903782814)
    assert fs["signals"]["FS-08"] is False
