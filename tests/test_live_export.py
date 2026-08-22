"""Seed cho app theo dõi — `ethdca export-live`.

Seed là hợp đồng dữ liệu giữa engine Python và bản cài đặt JS trong app web:
nếu shape đổi mà app không đổi theo, app im lặng hiển thị sai. Test khoá shape lại.
"""
import json
import subprocess
import sys

import pytest

from eth_dca_os.config import BASELINE_STRATEGY
from eth_dca_os.data.synth import generate
from eth_dca_os.live_export import build_seed, write_seed


@pytest.fixture(scope="module")
def raw(tmp_path_factory):
    d = tmp_path_factory.mktemp("raw")
    generate(d, start="2018-01-01", end="2021-06-30")
    return d


def test_seed_shape(raw):
    seed = build_seed(raw, history_days=420, parity_days=40)
    assert seed["schema"] == "ethdca.live_seed/1"
    assert seed["strategy_config_hash"] == BASELINE_STRATEGY.hash
    assert seed["dataset_hash"]
    assert len(seed["history"]) == 420
    assert len(seed["parity"]) == 40

    # history: khoá ngắn, đủ để JS tính lại mọi indicator
    for row in seed["history"][:5] + seed["history"][-5:]:
        assert set(row) == {"d", "e", "b", "v"}
        assert len(row["d"]) == 10 and row["d"][4] == "-"
        assert row["e"] > 0 and row["b"] > 0

    # history phải sắp tăng dần và không trùng ngày
    days = [r["d"] for r in seed["history"]]
    assert days == sorted(days)
    assert len(set(days)) == len(days)

    # parity: score do Python tính, dùng để app đối chiếu
    for row in seed["parity"]:
        assert set(row) == {"d", "oscore", "pl", "ms", "rv", "dq"}
        assert row["dq"] in ("GOOD", "DEGRADED", "INVALID")

    # parity nằm trong khoảng history (app cần tính lại được các ngày đó)
    assert set(r["d"] for r in seed["parity"]) <= set(days)


def test_seed_config_matches_baseline(raw):
    """App dùng config trong seed để tính unlock và spacing — phải là baseline thật."""
    seed = build_seed(raw, history_days=400, parity_days=10)
    c = seed["config"]
    assert c["base_pct"] == BASELINE_STRATEGY.base_pct
    assert c["smart_spacing_factor"] == BASELINE_STRATEGY.smart_spacing_factor
    assert c["smart_spacing_min"] == BASELINE_STRATEGY.smart_spacing_min
    assert c["smart_spacing_max"] == BASELINE_STRATEGY.smart_spacing_max
    assert c["opportunity_cap_months"] == BASELINE_STRATEGY.opportunity_cap_months
    assert c["score_weights"] == list(BASELINE_STRATEGY.score_weights)


def test_seed_parity_matches_engine(raw):
    """OSCORE trong parity phải bằng đúng score engine tính — không phải số cũ."""
    import pandas as pd
    from eth_dca_os.data.dataset import load_dataset
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores

    seed = build_seed(raw, history_days=420, parity_days=15)
    ds = load_dataset(raw)
    sc = compute_scores(compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"]),
                        BASELINE_STRATEGY.score_weights)
    for row in seed["parity"]:
        day = pd.Timestamp(row["d"], tz="UTC")
        assert row["oscore"] == pytest.approx(float(sc.loc[day, "oscore"]), abs=1e-9)
        assert row["pl"] == pytest.approx(float(sc.loc[day, "price_location_score"]), abs=1e-9)


def test_write_and_cli(raw, tmp_path):
    path = write_seed(tmp_path, raw, history_days=400, parity_days=20)
    assert path.name == "live_seed.json"
    data = json.loads(path.read_text())
    assert len(data["history"]) == 400

    r = subprocess.run(
        [sys.executable, "-m", "eth_dca_os.cli", "--raw-dir", str(raw),
         "--out-dir", str(tmp_path / "cli"), "export-live",
         "--history-days", "380", "--parity-days", "12"],
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    out = json.loads((tmp_path / "cli" / "live_seed.json").read_text())
    assert len(out["history"]) == 380 and len(out["parity"]) == 12
