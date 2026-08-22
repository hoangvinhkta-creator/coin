"""Manifest generators — Backtest §9.1 (Gate 2) và §10.1 (Gate 3).

Khóa cứng, seeded, đóng băng ra CSV/JSON + hash TRƯỚC official run.
Denominator được TÍNH từ manifest thực tế, không hard-code (Backtest §9.1).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from . import MASTER_SEED, GATE3_SAMPLING_SEED
from .config import (
    BASELINE_STRATEGY,
    GATE3_REALISTIC,
    SCORE_WEIGHT_TUPLES,
    ExecutionConfig,
    StrategyConfig,
)

# ---------------------------------------------------------------- Gate 2 grid
GATE2_GRID: dict[str, list] = {
    "base_pct": [0.50, 0.60, 0.70],
    "opportunity_pct": [0.10, 0.20, 0.30],
    "opportunity_cap_months": [2, 3, 4, 6],
    "cooldown_hours": [24, 48, 72],
    "cooldown_override_pct": [0.05, 0.07, 0.10],
    "smart_spacing_factor": [1.5, 2.0, 2.5],
    "score_weights": [list(t) for t in SCORE_WEIGHT_TUPLES],
    "smart_unlock_mode": ["HWM", "NO_HWM", "DECAY_HWM"],
}
N_INTERACTION = 200

# ---------------------------------------------------------------- Gate 3 grid
GATE3_GRID: dict[str, list] = {
    "user_delay_seconds": [15 * 60, 3600, 4 * 3600, 12 * 3600],
    "funding_policy": ["ON_DEMAND", "BULK_MONTHLY"],
    "funding_delay_seconds": [0, 15 * 60, 3600, 4 * 3600],
    "spot_fee_rate": [0.0, 0.0005, 0.001, 0.002],
    "slippage_bps": [0.0, 5.0, 10.0, 20.0],
}
N_FRICTION = 100


def _smart_ok(base: float, opp: float) -> bool:
    return (1.0 - base - opp) >= 0.15 - 1e-12


def _try_build(baseline: StrategyConfig, **kw):
    try:
        return baseline.with_(**kw)
    except ValueError:
        return None


def generate_gate2_manifest(baseline: StrategyConfig = BASELINE_STRATEGY) -> dict:
    """Trả về dict: baseline, ofat (18), interaction (200), rejected_ofat metadata."""
    # 1) OFAT candidates
    ofat, rejected = [], []
    for dim, levels in GATE2_GRID.items():
        base_val = getattr(baseline, dim)
        if dim == "score_weights":
            base_val = list(baseline.score_weights)
        for lv in levels:
            if lv == base_val:
                continue
            kw = {dim: tuple(lv) if dim == "score_weights" else lv}
            cfg = _try_build(baseline, config_name=f"ofat_{dim}={lv}", **kw)
            if cfg is None:
                rejected.append({"dim": dim, "level": lv, "reason": "smart_pct < 0.15"})
            else:
                ofat.append(cfg)

    # 2) Interaction: constrained stratified LHS-style sampling, master_seed = 42.
    rng = np.random.default_rng(MASTER_SEED)
    dims = list(GATE2_GRID.keys())

    def balanced_column(levels: list, n: int) -> list:
        reps = n // len(levels)
        col = list(levels) * reps
        extra = rng.choice(len(levels), size=n - len(col), replace=False) if n - len(col) else []
        col += [levels[int(i)] for i in extra]
        rng.shuffle(col)
        return col

    seen = {baseline.key()} | {c.key() for c in ofat}
    interaction: list[StrategyConfig] = []

    def add_candidate(vals: dict) -> None:
        kw = dict(vals)
        kw["score_weights"] = tuple(kw["score_weights"])
        cfg = _try_build(baseline, config_name=f"lhs_{len(interaction):03d}", **kw)
        if cfg is None:
            return
        k = cfg.key()
        if k in seen:
            return
        seen.add(k)
        interaction.append(cfg)

    # Stratified batch: mỗi chiều cân bằng qua các level; cặp base/opp rejection-sampled.
    cols = {d: balanced_column(GATE2_GRID[d], N_INTERACTION) for d in dims}
    for i in range(N_INTERACTION):
        vals = {d: cols[d][i] for d in dims}
        while not _smart_ok(vals["base_pct"], vals["opportunity_pct"]):
            vals["base_pct"] = GATE2_GRID["base_pct"][int(rng.integers(3))]
            vals["opportunity_pct"] = GATE2_GRID["opportunity_pct"][int(rng.integers(3))]
        add_candidate(vals)

    # Nếu sau khử trùng lặp còn dưới 200: sinh tất định tiếp trên cùng luồng RNG.
    while len(interaction) < N_INTERACTION:
        vals = {d: GATE2_GRID[d][int(rng.integers(len(GATE2_GRID[d])))] for d in dims}
        if not _smart_ok(vals["base_pct"], vals["opportunity_pct"]):
            continue
        add_candidate(vals)

    return {
        "baseline": baseline,
        "ofat": ofat,
        "interaction": interaction,
        "rejected_ofat": rejected,
        "denominator": 1 + len(ofat) + len(interaction),
    }


def generate_gate3_manifest(realistic: ExecutionConfig = GATE3_REALISTIC) -> dict:
    """14 config tất định (baseline + OFAT) + đúng 100 config stratified, seed 43."""
    ofat: list[ExecutionConfig] = []

    def variant(name, **kw):
        base = {
            "user_delay_seconds": realistic.user_delay_seconds,
            "funding_policy": realistic.funding_policy,
            "funding_delay_seconds": realistic.funding_delay_seconds,
            "spot_fee_rate": realistic.spot_fee_rate,
            "slippage_bps": realistic.slippage_bps,
            "action_ttl_seconds": realistic.action_ttl_seconds,
            "behavioral_model": realistic.behavioral_model,
            "p2p_unavailable_in_crash": realistic.p2p_unavailable_in_crash,
        }
        base.update(kw)
        return ExecutionConfig(config_name=name, **base)

    for v in GATE3_GRID["user_delay_seconds"]:
        if v != realistic.user_delay_seconds:
            ofat.append(variant(f"ofat_user_delay={v}", user_delay_seconds=v))
    for v in GATE3_GRID["funding_delay_seconds"]:
        if v != realistic.funding_delay_seconds:
            ofat.append(variant(f"ofat_funding_delay={v}", funding_delay_seconds=v))
    for v in GATE3_GRID["spot_fee_rate"]:
        if v != realistic.spot_fee_rate:
            ofat.append(variant(f"ofat_spot_fee={v}", spot_fee_rate=v))
    for v in GATE3_GRID["slippage_bps"]:
        if v != realistic.slippage_bps:
            ofat.append(variant(f"ofat_slippage={v}", slippage_bps=v))
    # funding policy đổi MỘT lần dưới dạng cặp ghép (BULK_MONTHLY, funding_delay=0)
    ofat.append(variant("ofat_policy=BULK_MONTHLY", funding_policy="BULK_MONTHLY",
                        funding_delay_seconds=0))

    deterministic = [realistic] + ofat  # kỳ vọng 14

    rng = np.random.default_rng(GATE3_SAMPLING_SEED)
    seen = {c.key() for c in deterministic}
    sampled: list[ExecutionConfig] = []

    def balanced_column(levels: list, n: int) -> list:
        reps = n // len(levels)
        col = list(levels) * reps
        extra = rng.choice(len(levels), size=n - len(col), replace=False) if n - len(col) else []
        col += [levels[int(i)] for i in extra]
        rng.shuffle(col)
        return col

    cols = {
        "user_delay_seconds": balanced_column(GATE3_GRID["user_delay_seconds"], N_FRICTION),
        "funding_policy": balanced_column(GATE3_GRID["funding_policy"], N_FRICTION),
        "funding_delay_seconds": balanced_column(GATE3_GRID["funding_delay_seconds"], N_FRICTION),
        "spot_fee_rate": balanced_column(GATE3_GRID["spot_fee_rate"], N_FRICTION),
        "slippage_bps": balanced_column(GATE3_GRID["slippage_bps"], N_FRICTION),
    }

    def add(vals):
        if vals["funding_policy"] == "BULK_MONTHLY":
            vals["funding_delay_seconds"] = 0  # ép ràng buộc, không config BULK + delay > 0
        cfg = ExecutionConfig(config_name=f"friction_{len(sampled):03d}", **vals)
        k = cfg.key()
        if k in seen:
            return
        seen.add(k)
        sampled.append(cfg)

    for i in range(N_FRICTION):
        add({d: cols[d][i] for d in cols})

    while len(sampled) < N_FRICTION:
        vals = {d: GATE3_GRID[d][int(rng.integers(len(GATE3_GRID[d])))] for d in GATE3_GRID}
        add(vals)

    return {
        "realistic": realistic,
        "deterministic": deterministic,
        "sampled": sampled,
        "manifest": deterministic + sampled,
        "size": len(deterministic) + len(sampled),
    }


# ------------------------------------------------------------------- freezing

def _cfg_row(cfg) -> dict:
    d = asdict(cfg)
    if "score_weights" in d:
        d["score_weights"] = list(cfg.score_weights)
    d["hash"] = cfg.hash
    return d


def manifest_hash(rows: list[dict]) -> str:
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def freeze_manifests(out_dir: str | Path) -> dict:
    """Sinh, đóng băng ra JSON/CSV có thứ tự và trả về metadata + hash (Impl Plan §2)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    g2 = generate_gate2_manifest()
    g2_rows = [_cfg_row(g2["baseline"])] + [_cfg_row(c) for c in g2["ofat"]] + [
        _cfg_row(c) for c in g2["interaction"]
    ]
    g2_hash = manifest_hash(g2_rows)
    g2_meta = {
        "gate": 2,
        "master_seed": MASTER_SEED,
        "ofat_candidates": len(g2["ofat"]) + len(g2["rejected_ofat"]),
        "ofat_valid": len(g2["ofat"]),
        "rejected_ofat": g2["rejected_ofat"],
        "interaction": len(g2["interaction"]),
        "denominator": g2["denominator"],
        "manifest_hash": g2_hash,
    }
    (out / "gate2_manifest.json").write_text(
        json.dumps({"meta": g2_meta, "configs": g2_rows}, indent=1, ensure_ascii=False))

    g3 = generate_gate3_manifest()
    g3_rows = [_cfg_row(c) for c in g3["manifest"]]
    g3_hash = manifest_hash(g3_rows)
    g3_meta = {
        "gate": 3,
        "seed": GATE3_SAMPLING_SEED,
        "deterministic": len(g3["deterministic"]),
        "sampled": len(g3["sampled"]),
        "size": g3["size"],
        "manifest_hash": g3_hash,
    }
    (out / "gate3_manifest.json").write_text(
        json.dumps({"meta": g3_meta, "configs": g3_rows}, indent=1, ensure_ascii=False))

    # CSV bản phẳng (đóng băng có thứ tự)
    import csv

    for name, rows in (("gate2_manifest.csv", g2_rows), ("gate3_manifest.csv", g3_rows)):
        with open(out / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                r = dict(r)
                if isinstance(r.get("score_weights"), list):
                    r["score_weights"] = "/".join(map(str, r["score_weights"]))
                w.writerow(r)

    return {"gate2": g2_meta, "gate3": g3_meta}
