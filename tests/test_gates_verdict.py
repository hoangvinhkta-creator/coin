"""Gate thresholds, FS, verdict cap tự động (Backtest §7, §9.2, §10.2, §17; Impl Plan §5–6)."""
import pytest

from eth_dca_os.failure_signals import evaluate_failure_signals
from eth_dca_os.gates import evaluate_gate1, evaluate_gate2, evaluate_gate3, evaluate_oos
from eth_dca_os.verdict import decide_verdict

GOOD_WINDOWS = {"W1": 104.0, "W2": 103.0, "W3": 105.0, "W4": 102.0, "W5": 106.0,
                "W6": 103.0, "W7": 104.0, "W8": 102.0, "W9": 103.0}


def _wm(aes):
    from eth_dca_os.windows import anchor_set_medians, pooled_median, primary_median
    return {"ae_by_window": aes, "anchor_set_medians": anchor_set_medians(aes),
            "primary_median": primary_median(aes),
            "pooled_median_descriptive": pooled_median(aes)}


def test_gate1_pass_and_fail():
    g = evaluate_gate1(_wm(GOOD_WINDOWS))
    assert g["pass"]
    # PrimaryMedian dưới 102 -> fail
    bad = dict(GOOD_WINDOWS, W1=99.0, W2=99.5, W3=100.0, W6=99.0, W7=99.0, W8=99.0, W9=99.0)
    assert not evaluate_gate1(_wm(bad))["pass"]
    # worst window delta < -5 -> fail dù median cao
    bad2 = dict(GOOD_WINDOWS, W4=94.0)
    assert not evaluate_gate1(_wm(bad2))["pass"]
    # một anchor set toàn bộ dưới 100 -> fail (anchor +6: W4, W5)
    bad3 = dict(GOOD_WINDOWS, W4=98.0, W5=99.0)
    assert not evaluate_gate1(_wm(bad3))["pass"]


def test_gate2_pre_oos_only():
    ok = {"gate1": {"pass": True}, "oos_ae": 101.0}
    ko = {"gate1": {"pass": False}, "oos_ae": 101.0}
    oos_bad = {"gate1": {"pass": True}, "oos_ae": 95.0}
    results = [ok] * 80 + [ko] * 20
    g2 = evaluate_gate2(results)
    assert g2["pass"] and g2["strong"]
    assert g2["denominator"] == 100
    # OOS không phải ngưỡng cứng: pre-OOS pass share không đổi khi OOS xấu
    results2 = [dict(ok, oos_ae=90.0)] * 80 + [ko] * 20
    g2b = evaluate_gate2(results2)
    assert g2b["pass"] == g2["pass"]
    assert g2b["fs10_triggered"] is True   # OOS pass share 0 < 50%


def test_gate3_thresholds():
    g3 = evaluate_gate3(0.02, 103.0, 0.75)
    assert g3["pass"] and g3["strong"]
    assert not evaluate_gate3(-0.01, 103.0, 0.75)["pass"]
    assert not evaluate_gate3(0.02, 99.0, 0.75)["pass"]
    assert not evaluate_gate3(0.02, 103.0, 0.55)["pass"]


def test_failure_signal_cap_blocks_build():
    gate1 = {"pass": True, "strong": False}
    oos = {"pass": True, "ae": 101.0}
    gate2 = {"pass": True}
    gate3 = {"pass": True}
    fs_none = evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, oos_ae=101.0,
                                       shortfall_pp=1.0, gate2_oos_pass_share=0.8)
    v = decide_verdict(gate1, oos, gate2, gate3, fs_none)
    assert v["verdict"] == "BUILD_WITH_MODIFICATIONS" or v["verdict"] == "BUILD"
    # FS-09 TRUE -> cap
    fs_bad = evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, oos_ae=101.0,
                                      shortfall_pp=4.0, gate2_oos_pass_share=0.8)
    assert fs_bad["signals"]["FS-09"] is True
    v2 = decide_verdict(gate1, oos, gate2, gate3, fs_bad)
    assert v2["verdict"] == "BUILD_WITH_MODIFICATIONS"
    assert not v2["can_proceed_to_app"]


def test_verdict_mapping():
    fs_clear = evaluate_failure_signals(gate1_windows=GOOD_WINDOWS, oos_ae=101.0,
                                        shortfall_pp=1.0, gate2_oos_pass_share=0.8,
                                        vif_any_severe=False, corr_high_redundancy=False,
                                        score_bimodal=False, adjacent_config_flip=False,
                                        avg_cash_ratio=0.1, gate1_primary_ae=104.0,
                                        v2_eth=10.0, random_timing_p95=9.0,
                                        random_anchor_p95=9.5,
                                        opportunity_cap_hit_share=0.1,
                                        concentration={"ae_ex_month": 101.0, "ae_ex_quarter": 100.5},
                                        regime_advantage_share=0.4)
    assert fs_clear["any_true"] is False and not fs_clear["unknown"]
    g_ok = {"pass": True}
    v = decide_verdict(g_ok, {"pass": True}, g_ok, g_ok, fs_clear)
    assert v["verdict"] == "BUILD" and v["can_proceed_to_app"]
    assert decide_verdict({"pass": False}, {"pass": True}, g_ok, g_ok,
                          fs_clear)["verdict"] == "DO_NOT_BUILD"
    assert decide_verdict(g_ok, {"pass": False}, g_ok, g_ok,
                          fs_clear)["verdict"] == "DO_NOT_BUILD"
    assert decide_verdict(g_ok, {"pass": True}, {"pass": False}, g_ok,
                          fs_clear)["verdict"] == "INCONCLUSIVE"
    assert decide_verdict(g_ok, {"pass": True}, g_ok, {"pass": False},
                          fs_clear)["verdict"] == "INCONCLUSIVE"


def test_fs08_random_control():
    # E2-B1-F01: chỉ MỘT control (thiếu Control G) -> UNKNOWN, không phải suy ra TRUE bằng
    # cách coi control vắng mặt là "V2 tự động beat". Trước bản sửa, ca này ra `True`.
    fs = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=11.0)
    assert fs["signals"]["FS-08"] is None
    assert "FS-08" in fs["unknown"]
    # Đủ cả hai control, V2 thua F -> TRUE.
    fs_lose_f = evaluate_failure_signals(v2_eth=10.0, random_timing_p95=11.0, random_anchor_p95=9.0)
    assert fs_lose_f["signals"]["FS-08"] is True
    # Đủ cả hai control, V2 thắng cả hai -> FALSE.
    fs2 = evaluate_failure_signals(v2_eth=12.0, random_timing_p95=11.0, random_anchor_p95=11.5)
    assert fs2["signals"]["FS-08"] is False
