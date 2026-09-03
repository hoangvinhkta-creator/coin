"""WP-B1 — Verdict policy correctness (CHECK-B1-07 stopping rule integrity + boundary cases
required by the WP-B1 session brief): precedence, fail-closed, numpy/bool equivalence at the
GATE level (H-26 family), determinism, can_proceed_to_app, reasons content.

Không đổi ngưỡng nào. Không chạm `gates.py`/`engine.py` — chỉ dùng chúng làm input thật cho
`verdict.py`/`failure_signals.py` (đúng ranh giới Scope của WP-B1).
"""
import copy

import numpy as np
import pytest

from eth_dca_os.failure_signals import evaluate_failure_signals
from eth_dca_os.gates import evaluate_gate1, evaluate_gate2, evaluate_gate3, evaluate_oos
from eth_dca_os.verdict import decide_verdict
from eth_dca_os.windows import anchor_set_medians, pooled_median, primary_median

GOOD_WINDOWS = {"W1": 104.0, "W2": 103.0, "W3": 105.0, "W4": 102.0, "W5": 106.0,
                "W6": 103.0, "W7": 104.0, "W8": 102.0, "W9": 103.0}


def _wm(aes):
    return {"ae_by_window": aes, "anchor_set_medians": anchor_set_medians(aes),
            "primary_median": primary_median(aes),
            "pooled_median_descriptive": pooled_median(aes)}


def _clear_fs():
    return evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, oos_ae=101.0,
                                    shortfall_pp=1.0, gate2_oos_pass_share=0.8,
                                    vif_any_severe=False, corr_high_redundancy=False,
                                    score_bimodal=False, adjacent_config_flip=False,
                                    avg_cash_ratio=0.1, gate1_primary_ae=104.0,
                                    v2_eth=10.0, random_timing_p95=9.0,
                                    random_anchor_p95=9.5,
                                    opportunity_cap_hit_share=0.1,
                                    concentration={"ae_ex_month": 101.0, "ae_ex_quarter": 100.5},
                                    regime_advantage_share=0.4)


# ---------------------------------------------------------------- precedence (E. + C.)

def test_gate1_and_oos_fail_precedence_over_gate2_gate3():
    """Cả bốn gate đều FAIL đồng thời cùng FS TRUE: verdict phải là DO_NOT_BUILD DUY NHẤT,
    và reasons chỉ được nhắc Gate 1 / OOS — không được rò rỉ lý do Gate 2/3 hay Failure
    Signal (precedence dừng lại ở nhánh cứng đầu tiên, BT §7/§8 là điều kiện cứng nhất)."""
    fs_true = dict(_clear_fs())
    fs_true["signals"] = dict(fs_true["signals"], **{"FS-09": True})
    fs_true["any_true"] = True
    v = decide_verdict({"pass": False}, {"pass": False}, {"pass": False}, {"pass": False},
                       fs_true)
    assert v["verdict"] == "DO_NOT_BUILD"
    assert not v["can_proceed_to_app"]
    assert any("Gate 1" in r for r in v["reasons"])
    assert any("OOS" in r for r in v["reasons"])
    assert not any("Gate 2" in r or "Gate 3" in r for r in v["reasons"])


def test_gate1_fail_alone_and_oos_fail_alone_both_do_not_build():
    fs_clear = _clear_fs()
    v1 = decide_verdict({"pass": False}, {"pass": True}, {"pass": True}, {"pass": True},
                        fs_clear)
    assert v1["verdict"] == "DO_NOT_BUILD" and not v1["can_proceed_to_app"]
    assert v1["reasons"] == ["Gate 1 FAIL"]
    v2 = decide_verdict({"pass": True}, {"pass": False}, {"pass": True}, {"pass": True},
                        fs_clear)
    assert v2["verdict"] == "DO_NOT_BUILD" and not v2["can_proceed_to_app"]
    assert v2["reasons"] == ["OOS hard condition FAIL"]


def test_gate2_and_gate3_fail_together_is_inconclusive_not_do_not_build():
    """Gate 1/OOS PASS nhưng Gate 2 VÀ Gate 3 đều FAIL: verdict INCONCLUSIVE (không phải
    DO_NOT_BUILD) — Gate 2/3 không phải điều kiện cứng theo BT §9.2/§10.2, và reasons phải
    liệt kê CẢ HAI, không chỉ một."""
    fs_clear = _clear_fs()
    v = decide_verdict({"pass": True}, {"pass": True}, {"pass": False}, {"pass": False},
                       fs_clear)
    assert v["verdict"] == "INCONCLUSIVE"
    assert not v["can_proceed_to_app"]
    assert any("Gate 2" in r for r in v["reasons"])
    assert any("Gate 3" in r for r in v["reasons"])


# ---------------------------------------------------------------- can_proceed_to_app (G.)

@pytest.mark.parametrize("gate1_pass,oos_pass,gate2_pass,gate3_pass,fs_any_true", [
    (True, True, True, True, False),
    (True, True, True, True, True),
    (False, True, True, True, False),
    (True, False, True, True, False),
    (True, True, False, True, False),
    (True, True, True, False, False),
])
def test_can_proceed_to_app_iff_verdict_is_build(gate1_pass, oos_pass, gate2_pass, gate3_pass,
                                                 fs_any_true):
    fs = dict(_clear_fs())
    fs["any_true"] = fs_any_true
    v = decide_verdict({"pass": gate1_pass}, {"pass": oos_pass}, {"pass": gate2_pass},
                       {"pass": gate3_pass}, fs)
    assert v["can_proceed_to_app"] == (v["verdict"] == "BUILD")
    if not (gate1_pass and oos_pass and gate2_pass and gate3_pass and not fs_any_true):
        assert v["verdict"] != "BUILD"


# ---------------------------------------------------------------- numpy/bool equivalence (F.)
# H-26: evaluate_gate1/evaluate_oos so sánh trực tiếp trên input số (numpy.float64 trong
# pipeline thật), nên "pass" có thể ra numpy.bool_ chứ không phải bool thuần Python.
# verdict.py đọc bằng truthiness (`not gate1["pass"]`), không bằng `is True/False`, nên phải
# an toàn — đây là bằng chứng thực thi, không phải suy luận.

def test_gate1_and_oos_pass_flag_numpy_bool_still_read_correctly_by_verdict():
    wm_numpy = _wm({k: np.float64(v) for k, v in GOOD_WINDOWS.items()})
    g1 = evaluate_gate1(wm_numpy)
    assert type(g1["checks"]["primary_median"]["pass"]).__name__ in ("bool_", "bool")
    oos = evaluate_oos({"ae": np.float64(101.0), "oos_months": 20, "short_oos": False})
    assert type(oos["pass"]).__name__ in ("bool_", "bool")
    # dù kiểu là numpy.bool_, verdict vẫn phải đọc đúng PASS -> không rơi vào nhánh DO_NOT_BUILD
    fs_clear = _clear_fs()
    v = decide_verdict(g1, oos, {"pass": True}, {"pass": True}, fs_clear)
    assert v["verdict"] != "DO_NOT_BUILD"

    oos_fail = evaluate_oos({"ae": np.float64(90.0), "oos_months": 20, "short_oos": False})
    assert oos_fail["pass"] == False  # noqa: E712 -- cố ý so sánh, không phải `is`
    v2 = decide_verdict(g1, oos_fail, {"pass": True}, {"pass": True}, fs_clear)
    assert v2["verdict"] == "DO_NOT_BUILD"
    assert any("OOS" in r for r in v2["reasons"])


# ---------------------------------------------------------------- determinism (H.)

def test_decide_verdict_deterministic_same_canonical_input():
    fs_clear = _clear_fs()
    g_ok = {"pass": True}
    args = (dict(g_ok), {"pass": True}, dict(g_ok), dict(g_ok), copy.deepcopy(fs_clear))
    v1 = decide_verdict(*args)
    v2 = decide_verdict(*copy.deepcopy(args))
    assert v1 == v2


def test_evaluate_failure_signals_deterministic_same_input():
    kwargs = dict(gate1_windows=GOOD_WINDOWS, oos_ae=101.0, shortfall_pp=1.0,
                  gate2_oos_pass_share=0.8, vif_any_severe=False, corr_high_redundancy=False,
                  score_bimodal=False, adjacent_config_flip=False, avg_cash_ratio=0.1,
                  gate1_primary_ae=104.0, v2_eth=10.0, random_timing_p95=9.0,
                  random_anchor_p95=9.5, opportunity_cap_hit_share=0.1,
                  concentration={"ae_ex_month": 101.0, "ae_ex_quarter": 100.5},
                  regime_advantage_share=0.4)
    fs1 = evaluate_failure_signals(**kwargs)
    fs2 = evaluate_failure_signals(**kwargs)
    assert fs1 == fs2
