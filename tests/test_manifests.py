"""Backtest §21.4: manifest tất định Gate 2 (19/1/18/200/219) và Gate 3 (114, không BULK+delay>0)."""
import json

from eth_dca_os.manifests import (
    freeze_manifests,
    generate_gate2_manifest,
    generate_gate3_manifest,
)


def test_gate2_counts():
    g2 = generate_gate2_manifest()
    assert len(g2["ofat"]) + len(g2["rejected_ofat"]) == 19
    assert len(g2["rejected_ofat"]) == 1
    rej = g2["rejected_ofat"][0]
    assert rej["dim"] == "base_pct" and rej["level"] == 0.70
    assert len(g2["ofat"]) == 18
    assert len(g2["interaction"]) == 200
    assert g2["denominator"] == 219


def test_gate2_unique_and_valid():
    g2 = generate_gate2_manifest()
    all_cfgs = [g2["baseline"]] + g2["ofat"] + g2["interaction"]
    keys = {c.key() for c in all_cfgs}
    assert len(keys) == len(all_cfgs)  # không trùng lặp
    for c in all_cfgs:
        assert c.smart_pct >= 0.15 - 1e-12
        assert abs(c.base_pct + c.smart_pct + c.opportunity_pct - 1.0) < 1e-9


def test_gate2_reproducible():
    a = generate_gate2_manifest()
    b = generate_gate2_manifest()
    assert [c.key() for c in a["interaction"]] == [c.key() for c in b["interaction"]]


def test_gate3_counts_and_constraint():
    g3 = generate_gate3_manifest()
    assert len(g3["deterministic"]) == 14
    assert len(g3["sampled"]) == 100
    assert g3["size"] == 114
    keys = {c.key() for c in g3["manifest"]}
    assert len(keys) == 114
    for c in g3["manifest"]:
        if c.funding_policy == "BULK_MONTHLY":
            assert c.funding_delay_seconds == 0


def test_freeze_reproducible_hash(tmp_path):
    m1 = freeze_manifests(tmp_path / "a")
    m2 = freeze_manifests(tmp_path / "b")
    assert m1["gate2"]["manifest_hash"] == m2["gate2"]["manifest_hash"]
    assert m1["gate3"]["manifest_hash"] == m2["gate3"]["manifest_hash"]
    data = json.loads((tmp_path / "a" / "gate2_manifest.json").read_text())
    assert data["meta"]["denominator"] == 219
    assert len(data["configs"]) == 219
