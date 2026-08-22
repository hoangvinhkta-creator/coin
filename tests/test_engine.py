"""Backtest §21.2–21.3 (mức engine): Base schedule, trigger/confirm, delay, TTL, cooldown,
invariants ledger, reproducibility."""
import numpy as np
import pandas as pd
import pytest

from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, ExecutionConfig
from eth_dca_os.data.synth import generate
from eth_dca_os.data.dataset import load_dataset
from eth_dca_os.engine import run_engine
from eth_dca_os.indicators import compute_daily_indicators
from eth_dca_os.score import compute_scores


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    d = tmp_path_factory.mktemp("raw")
    generate(d, start="2018-01-01", end="2021-06-30")
    ds = load_dataset(d)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = pd.concat([ind, compute_scores(ind)], axis=1)
    scores = scores.loc[:, ~scores.columns.duplicated()]
    return ds, scores


def _run(prepared, exec_cfg=GATE1_LOW_FRICTION, cfg=BASELINE_STRATEGY,
         start="2019-06-01", end="2021-06-01", **kw):
    ds, scores = prepared
    return run_engine(ds, scores, cfg, exec_cfg,
                      pd.Timestamp(start), pd.Timestamp(end), **kw)


def test_engine_runs_and_buys(prepared):
    res = _run(prepared)
    assert res.eth_total > 0
    # 2019-06 .. 2021-06 theo local (+7): nến 2021-05-31 17:00 UTC đã thuộc tháng 6 local
    assert len(res.contributions) == 25
    assert res.contributed_total == pytest.approx(2500.0)
    # Base phải giải ngân đủ trong mỗi tháng: tổng BASE nominal = 24 * 50
    base_nominal = sum(p["nominal"] for p in res.purchases if p["source"] == "BASE")
    assert base_nominal == pytest.approx(24 * 50.0, rel=1e-6)


def test_conservation_no_negative(prepared):
    res = _run(prepared)
    # tổng nominal đã mua <= tổng contribution (bảo toàn vốn, không leverage)
    spent = sum(p["nominal"] for p in res.purchases)
    assert spent <= res.contributed_total + 1e-6
    # cash không âm tại mọi mẫu
    for ts, cash, eth, _price in res.cash_samples:
        assert cash >= -1e-6


def test_reproducible_bitforbit(prepared):
    r1 = _run(prepared)
    r2 = _run(prepared)
    assert r1.eth_total == r2.eth_total
    assert len(r1.purchases) == len(r2.purchases)
    for a, b in zip(r1.purchases, r2.purchases):
        assert a == b


def test_base_schedule_days(prepared):
    res = _run(prepared)
    # mọi lệnh BASE_SCHEDULE phải rơi vào ngày 3/13/23 (giờ local)
    for p in res.purchases:
        if p["reason"] == "BASE_SCHEDULE":
            local = pd.Timestamp(p["ts"] + 7 * 3600, unit="s")
            assert local.day in (3, 13, 23)
            assert local.hour == 12


def test_delay_changes_results(prepared):
    fast = _run(prepared, exec_cfg=GATE1_LOW_FRICTION)
    slow_cfg = ExecutionConfig(user_delay_seconds=12 * 3600, funding_policy="ON_DEMAND",
                               funding_delay_seconds=4 * 3600, spot_fee_rate=0.001,
                               slippage_bps=0.0, config_name="slow")
    slow = _run(prepared, exec_cfg=slow_cfg)
    # delay dài hơn -> kết quả khác (giá thực thi khác); fee/slippage giữ nguyên
    assert fast.eth_total != slow.eth_total


def test_fee_reduces_eth(prepared):
    nofee = _run(prepared, exec_cfg=ExecutionConfig(
        user_delay_seconds=15 * 60, funding_policy="BULK_MONTHLY", funding_delay_seconds=0,
        spot_fee_rate=0.0, slippage_bps=0.0, config_name="nofee"))
    fee = _run(prepared, exec_cfg=GATE1_LOW_FRICTION)  # 0.10% fee
    assert nofee.eth_total > fee.eth_total


def test_zone_purchases_have_recommended_price(prepared):
    res = _run(prepared)
    zone_buys = [p for p in res.purchases if p["source"] in ("SMART", "OPPORTUNITY", "CRASH")
                 and p["reason"] != "MONTH_END_SMART"]
    if zone_buys:  # tùy dữ liệu synthetic
        for p in zone_buys:
            assert p["recommended_price"] is not None
            assert p["shortfall_bps"] is not None


def test_behavioral_mode_runs(prepared):
    cfg = ExecutionConfig(user_delay_seconds=4 * 3600, funding_policy="ON_DEMAND",
                          funding_delay_seconds=3600, spot_fee_rate=0.001, slippage_bps=5.0,
                          behavioral_model="LOCAL_HOUR", config_name="behav")
    rng = np.random.default_rng(123)
    res = _run(prepared, exec_cfg=cfg, behavioral_rng=rng)
    assert res.eth_total > 0
    # cùng seed -> cùng kết quả
    res2 = _run(prepared, exec_cfg=cfg, behavioral_rng=np.random.default_rng(123))
    assert res2.eth_total == res.eth_total
