"""WP-B1 — regression tests for the fresh Independent E2 findings
(docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-fail.md):

E2-B1-F01: FS-08 must be UNKNOWN, never FALSE, whenever v2_eth / Control F P95 /
Control G P95 is missing or invalid — a missing control must not be treated as an
automatic "V2 beats it".

E2-B1-F02: non-official / unresolved-official evidence must never be able to produce
verdict=BUILD with can_proceed_to_app=true. `can_proceed_to_app` is the single key
T-07/T-11 read (docs/CONVENTIONS.md #21(a)).

Both repairs are narrowly scoped inside CAP-VERDICT/WP-B1 (failure_signals.py, pipeline.py).
No engine/strategy/gate/threshold change. No T-06 rerun.
"""
import math

import pytest

from eth_dca_os.failure_signals import evaluate_failure_signals
from eth_dca_os.pipeline import run_verdict
from eth_dca_os.reporting import ProvenanceUnresolvedError
import eth_dca_os.reporting as reporting

GOOD_WINDOWS = {"W1": 104.0, "W2": 103.0, "W3": 105.0, "W4": 102.0, "W5": 106.0,
                "W6": 103.0, "W7": 104.0, "W8": 102.0, "W9": 103.0}


# =========================================================== E2-B1-F01: FS-08 fail-closed

@pytest.mark.parametrize("v2_eth,f_p95,g_p95,expected", [
    (12.0, 11.0, 11.5, False),   # 1. both present, V2 beats both -> FALSE
    (10.0, 11.0, 9.0, True),     # 2. both present, V2 loses to F -> TRUE
    (11.0, 9.0, 11.5, True),     # 3. both present, V2 loses to G -> TRUE
])
def test_fs08_both_controls_present_computes_normally(v2_eth, f_p95, g_p95, expected):
    fs = evaluate_failure_signals(v2_eth=v2_eth, random_timing_p95=f_p95,
                                  random_anchor_p95=g_p95)
    assert fs["signals"]["FS-08"] is expected


def test_fs08_control_f_missing_is_unknown_even_if_v2_beats_g():
    # 4. F missing, G present, V2 beats G -> UNKNOWN (không phải FALSE do "F tự beat")
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=None, random_anchor_p95=9.5)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_control_g_missing_is_unknown_even_if_v2_beats_f():
    # 5. G missing, F present, V2 beats F -> UNKNOWN
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=9.0, random_anchor_p95=None)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_both_controls_missing_is_unknown():
    # 6. both missing -> UNKNOWN
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=None, random_anchor_p95=None)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_invalid_control_f_p95_is_unknown():
    # 7. invalid (NaN) F -> fail closed, UNKNOWN
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=float("nan"),
                                  random_anchor_p95=9.5)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_invalid_control_g_p95_is_unknown():
    # 8. invalid (NaN) G -> fail closed, UNKNOWN
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=9.0,
                                  random_anchor_p95=float("nan"))
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]


def test_fs08_missing_v2_eth_is_unknown_regardless_of_controls():
    fs = evaluate_failure_signals(v2_eth=None, random_timing_p95=9.0, random_anchor_p95=9.5)
    assert fs["signals"]["FS-08"] is None


def test_fs08_unknown_control_blocks_build_end_to_end():
    """Production-reachable regression: exactly the E2-B1-F01 counterexample
    (v2_eth=10, F missing, G=9.5 which V2 beats) must no longer produce BUILD."""
    from eth_dca_os.verdict import decide_verdict
    fs = evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, concentration={"ae_ex_month": 101.0,
                                  "ae_ex_quarter": 100.5}, opportunity_cap_hit_share=0.1,
                                  regime_advantage_share=0.4, adjacent_config_flip=False,
                                  vif_any_severe=False, corr_high_redundancy=False,
                                  score_bimodal=False, avg_cash_ratio=0.1, gate1_primary_ae=104.0,
                                  shortfall_pp=1.0, gate2_oos_pass_share=0.8, oos_ae=101.0,
                                  v2_eth=10.0, random_timing_p95=None, random_anchor_p95=9.5)
    assert fs["signals"]["FS-08"] is None
    g_ok = {"pass": True}
    v = decide_verdict(g_ok, {"pass": True}, g_ok, g_ok, fs)
    assert v["verdict"] != "BUILD"
    assert v["can_proceed_to_app"] is False


# =========================================================== E2-B1-F02: officiality fail-closed

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


def test_official_valid_evidence_preserves_build_and_can_proceed(tmp_path):
    # 9. valid official evidence + otherwise BUILD-eligible -> BUILD, can_proceed_to_app=True
    payload = run_verdict(_clean_g1(True), _clean_g2(True), _clean_g3(True),
                          _clean_controls(True), tmp_path, dataset_hash="dummy")
    assert payload["official"] is True
    assert payload["verdict"]["verdict"] == "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is True
    assert "warning" not in payload


def test_non_official_evidence_cannot_reach_can_proceed_true(tmp_path):
    # 10. non-official evidence + otherwise BUILD-eligible -> can_proceed_to_app=False AND
    # verdict != BUILD (canonical interpretation A, E2-WP-B1-003 -- fixed in repair v2).
    payload = run_verdict(_clean_g1(False), _clean_g2(False), _clean_g3(False),
                          _clean_controls(False), tmp_path, dataset_hash="dummy")
    assert payload["official"] is False
    assert payload["verdict"]["verdict"] != "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is False
    assert "warning" in payload


@pytest.mark.parametrize("official_flags", [
    (False, True, True, True),   # Gate 1 not official
    (True, False, True, True),   # Gate 2 not official
    (True, True, False, True),   # Gate 3 not official
    (True, True, True, False),   # Controls not official
])
def test_can_proceed_false_whenever_any_single_component_not_official(tmp_path, official_flags):
    # 12. can_proceed_to_app=false AND verdict != BUILD whenever official eligibility fails,
    # for EACH component individually.
    g1_off, g2_off, g3_off, ctl_off = official_flags
    payload = run_verdict(_clean_g1(g1_off), _clean_g2(g2_off), _clean_g3(g3_off),
                          _clean_controls(ctl_off), tmp_path, dataset_hash="dummy")
    assert payload["official"] is False
    assert payload["verdict"]["verdict"] != "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is False


def test_unresolved_provenance_cannot_leak_can_proceed_true(tmp_path, monkeypatch):
    # 11. unresolved required provenance/officiality + otherwise BUILD-eligible ->
    # save_run() must refuse (fail loudly, pre-existing WP-A1 mechanism) rather than let a
    # payload with can_proceed_to_app leak out.
    monkeypatch.setattr(reporting, "_get_code_commit", lambda: "unknown")
    with pytest.raises(ProvenanceUnresolvedError):
        run_verdict(_clean_g1(True), _clean_g2(True), _clean_g3(True),
                   _clean_controls(True), tmp_path, dataset_hash="dummy")


def test_controls_none_cannot_reach_can_proceed_true(tmp_path):
    """`controls=None` (Controls never run) must be treated as non-official -- must not
    crash and must not allow can_proceed_to_app=true (or verdict=BUILD)."""
    payload = run_verdict(_clean_g1(True), _clean_g2(True), _clean_g3(True), None, tmp_path,
                          dataset_hash="dummy")
    assert payload["official"] is False
    assert payload["verdict"]["verdict"] != "BUILD"
    assert payload["verdict"]["can_proceed_to_app"] is False


# =========================================================== Retained adversarial coverage

def test_fs08_ties_go_to_true_strict_comparison_unchanged():
    """Comparison direction/strictness unchanged by this repair: a tie (v2_eth == p95)
    does not beat the control (strict `>`), so FS-08 stays TRUE."""
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=10.0, random_anchor_p95=9.0)
    assert fs["signals"]["FS-08"] is True


def test_fs02_fs12_exact_boundary_and_one_ulp():
    at_boundary = evaluate_failure_signals(opportunity_cap_hit_share=0.5,
                                           regime_advantage_share=0.80)
    assert at_boundary["signals"]["FS-02"] is False
    assert at_boundary["signals"]["FS-12"] is False
    above = evaluate_failure_signals(opportunity_cap_hit_share=math.nextafter(0.5, 1.0),
                                     regime_advantage_share=math.nextafter(0.80, 1.0))
    assert above["signals"]["FS-02"] is True
    assert above["signals"]["FS-12"] is True


def test_fs07_exact_boundary_requires_both_sides_strict():
    at_boundary = evaluate_failure_signals(avg_cash_ratio=0.30, gate1_primary_ae=102.0)
    assert at_boundary["signals"]["FS-07"] is False
    just_over = evaluate_failure_signals(avg_cash_ratio=math.nextafter(0.30, 1.0),
                                         gate1_primary_ae=math.nextafter(102.0, 0.0))
    assert just_over["signals"]["FS-07"] is True
