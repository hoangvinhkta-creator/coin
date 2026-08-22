"""Backtest §21.4: equal contribution, Benchmark C cycle [F4], D cap 6C, F/G seeded."""
import numpy as np
import pandas as pd
import pytest

from eth_dca_os.benchmarks import (
    random_anchor_control,
    random_timing_control,
    run_benchmark_A,
    run_benchmark_B,
    run_benchmark_C,
    run_benchmark_D,
)
from eth_dca_os.data.dataset import load_dataset
from eth_dca_os.data.synth import generate
from eth_dca_os.indicators import compute_daily_indicators


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    d = tmp_path_factory.mktemp("raw")
    generate(d, start="2018-01-01", end="2022-12-31")
    ds = load_dataset(d)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    return ds, ind


START, END = pd.Timestamp("2019-06-01"), pd.Timestamp("2022-06-01")


def test_equal_external_contribution(data):
    ds, ind = data
    a = run_benchmark_A(ds, START, END)
    b = run_benchmark_B(ds, START, END)
    c = run_benchmark_C(ds, ind, START, END)
    dd = run_benchmark_D(ds, ind, START, END)
    assert a["contributed"] == b["contributed"] == c["contributed"] == dd["contributed"]
    # bảo toàn: C tiêu <= contributed (reserve còn lại không âm)
    spent_c = sum(p["nominal"] for p in c["purchases"])
    assert spent_c + c["final_reserve"] == pytest.approx(c["contributed"])
    assert c["final_reserve"] >= 0
    # D: bảo toàn với reserve cap
    spent_d = sum(p["nominal"] for p in dd["purchases"])
    assert spent_d + dd["final_reserve"] == pytest.approx(dd["contributed"])
    assert dd["final_reserve"] <= 6 * 100.0 + 1e-9  # cap 6C


def test_benchmark_a_buys_day3(data):
    ds, _ = data
    a = run_benchmark_A(ds, START, END)
    for p in a["purchases"]:
        local = pd.Timestamp(p["ts"] + 7 * 3600, unit="s")
        assert (local.day, local.hour) >= (3, 12) and local.day >= 3


def test_benchmark_b_max4_mondays(data):
    ds, _ = data
    b = run_benchmark_B(ds, START, END)
    per_month = {}
    for p in b["purchases"]:
        per_month[p["month"]] = per_month.get(p["month"], 0) + 1
        local = pd.Timestamp(p["ts"] + 7 * 3600, unit="s")
        assert local.dayofweek == 0
    assert max(per_month.values()) <= 4


def test_random_controls_reproducible(data):
    ds, _ = data
    deployments = {"2019-07": 100.0, "2019-08": 80.0, "2020-03": 120.0}
    f1 = random_timing_control(ds, deployments, START, END, n_sims=50)
    f2 = random_timing_control(ds, deployments, START, END, n_sims=50)
    assert np.array_equal(f1["eth_distribution"], f2["eth_distribution"])
    g1 = random_anchor_control(ds, deployments, START, END, n_sims=50)
    g2 = random_anchor_control(ds, deployments, START, END, n_sims=50)
    assert np.array_equal(g1["eth_distribution"], g2["eth_distribution"])
    assert f1["p95"] >= f1["p50"]
