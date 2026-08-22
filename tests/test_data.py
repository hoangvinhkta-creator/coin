"""Data layer: synth deterministic, lineage/hash, gap report, diagnostics smoke."""
import numpy as np
import pandas as pd
import pytest

from eth_dca_os.data.dataset import gap_report, load_dataset
from eth_dca_os.data.synth import generate


@pytest.fixture(scope="module")
def synth_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("raw")
    meta = generate(d, start="2018-01-01", end="2021-12-31")
    return d, meta


def test_synth_deterministic(tmp_path, synth_dir):
    d1, meta1 = synth_dir
    meta2 = generate(tmp_path / "raw2", start="2018-01-01", end="2021-12-31")
    assert meta1["dataset_hash"] == meta2["dataset_hash"]


def test_synth_consistency(synth_dir):
    d, meta = synth_dir
    ds = load_dataset(d)
    eth1d, eth15 = ds["ETHUSDT_1d"], ds["ETHUSDT_15m"]
    # 1D được tổng hợp từ 15m: close ngày = close nến 15m cuối của ngày đó
    day = pd.Timestamp("2019-06-10", tz="UTC")
    day15 = eth15[(eth15["open_time"] >= day) & (eth15["open_time"] < day + pd.Timedelta(days=1))]
    row1d = eth1d[eth1d["open_time"] == day].iloc[0]
    assert row1d["close"] == pytest.approx(day15["close"].iloc[-1])
    assert row1d["high"] == pytest.approx(day15["high"].max())
    assert len(day15) == 96


def test_gap_report_detects_intentional_gap(synth_dir):
    d, _ = synth_dir
    ds = load_dataset(d)
    rep = gap_report(ds["ETHUSDT_15m"], "15m")
    assert rep["missing"] >= 4  # gap chèn chủ đích 2020-03-15
    assert rep["longest_gap"] >= 4
    assert any(g["after"].startswith("2020-03-15") for g in rep["gaps"])


def test_indicators_and_diagnostics_smoke(synth_dir):
    from eth_dca_os.diagnostics import run_all
    from eth_dca_os.indicators import compute_daily_indicators

    d, _ = synth_dir
    ds = load_dataset(d)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    assert {"dd365", "ma200", "rsi14", "adr30", "ethbtc_percentile180"} <= set(ind.columns)
    # sau warm-up 365 ngày phải có giá trị hợp lệ
    valid = ind.dropna(subset=["dd365", "ma200", "rsi14", "percentile365"])
    assert len(valid) > 300
    diag = run_all(ind)
    assert "vif" in diag and "score_distribution" in diag
    assert 0 <= diag["score_distribution"]["top2_bucket_share"] <= 1
