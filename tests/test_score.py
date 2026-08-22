"""Backtest §21.1: clamp biên, ScoreMultiplier piecewise, Opp ladder weights, DEGRADED, no-lookahead."""
import numpy as np
import pandas as pd
import pytest

from eth_dca_os.score import (
    compute_scores,
    factor_scores,
    opportunity_ladder_weights,
    opportunity_unlock,
    score_multiplier,
    smart_unlock,
    sub_factors,
)


def _ind_row(**kw):
    base = dict(dd365=-0.30, ma_ratio=0.90, percentile365=0.20, rsi14=40.0,
                return7=-0.10, volume_ratio=1.5, ethbtc_return30=-0.10,
                ethbtc_percentile180=0.30)
    base.update(kw)
    return pd.DataFrame([base])


def test_subfactor_clamp_bounds():
    # D: -DD365=0.05 -> 0; 0.60 -> 1
    sf = sub_factors(_ind_row(dd365=-0.05))
    assert sf["D"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    sf = sub_factors(_ind_row(dd365=-0.60))
    assert sf["D"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    sf = sub_factors(_ind_row(dd365=-0.90))
    assert sf["D"].iloc[0] == pytest.approx(1.0, abs=1e-9)  # clamp trên
    # M: ma_ratio 1.05 -> 0; 0.65 -> 1
    assert sub_factors(_ind_row(ma_ratio=1.05))["M"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(ma_ratio=0.65))["M"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # P: percentile 0.90 -> 0; 0.10 -> 1
    assert sub_factors(_ind_row(percentile365=0.90))["P"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(percentile365=0.10))["P"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # R: RSI 55 -> 0; 25 -> 1
    assert sub_factors(_ind_row(rsi14=55))["R"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(rsi14=25))["R"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # S7: return7 -0.02 -> 0; -0.20 -> 1
    assert sub_factors(_ind_row(return7=-0.02))["S7"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(return7=-0.20))["S7"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # V: return7 >= 0 -> 0 bất kể VR; VR 1 -> 0; VR 2.5 -> 1
    assert sub_factors(_ind_row(return7=0.05, volume_ratio=3.0))["V"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(volume_ratio=1.0))["V"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(volume_ratio=2.5))["V"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # W: R30 -0.02 -> 0; -0.20 -> 1
    assert sub_factors(_ind_row(ethbtc_return30=-0.02))["W"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(ethbtc_return30=-0.20))["W"].iloc[0] == pytest.approx(1.0, abs=1e-9)
    # RP: pct180 0.70 -> 0; 0.10 -> 1
    assert sub_factors(_ind_row(ethbtc_percentile180=0.70))["RP"].iloc[0] == pytest.approx(0.0, abs=1e-9)
    assert sub_factors(_ind_row(ethbtc_percentile180=0.10))["RP"].iloc[0] == pytest.approx(1.0, abs=1e-9)


def test_score_multiplier_piecewise():
    for a, m in [(40, 0.80), (60, 0.90), (70, 1.00), (80, 1.15), (90, 1.30)]:
        assert score_multiplier(a) == pytest.approx(m)
    # clamp ngoài hai đầu
    assert score_multiplier(10) == pytest.approx(0.80)
    assert score_multiplier(99) == pytest.approx(1.30)
    # nội suy giữa anchor
    assert score_multiplier(50) == pytest.approx(0.85)
    assert score_multiplier(65) == pytest.approx(0.95)
    assert score_multiplier(75) == pytest.approx(1.075)
    assert score_multiplier(85) == pytest.approx(1.225)


def test_opportunity_ladder_weights():
    for os_ in np.linspace(0, 100, 201):
        w = opportunity_ladder_weights(os_)
        assert sum(w) == pytest.approx(1.0)
    assert opportunity_ladder_weights(70) == pytest.approx([0.0, 0.15, 0.20, 0.25, 0.40])
    assert opportunity_ladder_weights(60) == pytest.approx([0.0, 0.15, 0.20, 0.25, 0.40])
    assert opportunity_ladder_weights(75) == pytest.approx([0.05, 0.15, 0.20, 0.25, 0.35])
    assert opportunity_ladder_weights(80) == pytest.approx([0.10, 0.15, 0.20, 0.25, 0.30])
    assert opportunity_ladder_weights(95) == pytest.approx([0.10, 0.15, 0.20, 0.25, 0.30])


def test_degraded_no_rescale():
    ind = _ind_row(volume_ratio=np.nan)  # V thiếu
    sf = sub_factors(ind)
    assert np.isnan(sf["V"].iloc[0])
    fs = factor_scores(sf)
    # Market stress chỉ còn R và S7 đóng góp; V = 0, KHÔNG rescale
    r = sf["R"].iloc[0]
    s7 = sf["S7"].iloc[0]
    assert fs["market_stress_score"].iloc[0] == pytest.approx(30 * (0.5 * r + 0.3 * s7))
    assert fs["data_quality"].iloc[0] == "DEGRADED"
    # so với GOOD cùng input: score DEGRADED phải <= GOOD (không bao giờ đẩy lên)
    good = factor_scores(sub_factors(_ind_row()))
    assert fs["oscore"].iloc[0] <= good["oscore"].iloc[0]


def test_invalid_when_all_missing():
    ind = _ind_row(**{k: np.nan for k in ("dd365", "ma_ratio", "percentile365", "rsi14",
                                          "return7", "volume_ratio", "ethbtc_return30",
                                          "ethbtc_percentile180")})
    fs = factor_scores(sub_factors(ind))
    assert np.isnan(fs["oscore"].iloc[0])
    assert fs["data_quality"].iloc[0] == "INVALID"


def test_unlocks():
    assert smart_unlock(35) == 0.0
    assert smart_unlock(70) == 1.0
    assert smart_unlock(52.5) == pytest.approx(0.5)
    assert opportunity_unlock(65) == 0.0
    assert opportunity_unlock(95) == pytest.approx(0.60)
    assert opportunity_unlock(80) == pytest.approx(0.30)


def test_no_lookahead_indicators():
    """Indicator của ngày D không đổi khi thay dữ liệu sau ngày D."""
    from eth_dca_os.indicators import compute_daily_indicators
    rng = np.random.default_rng(7)
    n = 500
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    eth = pd.DataFrame({"open_time": idx, "open": close, "high": close * 1.01,
                        "low": close * 0.99, "close": close,
                        "volume": rng.uniform(100, 200, n)})
    btc = eth.copy()
    btc["close"] = close * 30
    ind_full = compute_daily_indicators(eth, btc)
    cut = 450
    ind_cut = compute_daily_indicators(eth.iloc[:cut], btc.iloc[:cut])
    check_day = ind_cut.index[cut - 1]
    for col in ("dd365", "ma200", "rsi14", "return7", "volume_ratio", "adr30"):
        a, b = ind_full.loc[check_day, col], ind_cut.loc[check_day, col]
        if np.isnan(a) and np.isnan(b):
            continue
        assert a == pytest.approx(b), col
