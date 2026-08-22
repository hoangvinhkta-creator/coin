"""Block bootstrap — Backtest §13. Chẩn đoán bất định, KHÔNG thay gate cứng.

Xấp xỉ lightweight: bootstrap theo block các cặp purchase (V2, A) theo thời gian,
block dài ~30/60/90 ngày, tính phân phối tỷ số AE. Không shuffle daily return riêng lẻ.
"""
from __future__ import annotations

import numpy as np

from .config import deterministic_hash

BLOCK_LENGTHS_DAYS = (30, 60, 90)
DAY = 86400.0


def _blocks(purchases: list[dict], block_days: int) -> list[list[dict]]:
    if not purchases:
        return []
    blocks, cur = [], [purchases[0]]
    start = purchases[0]["ts"]
    for p in purchases[1:]:
        if p["ts"] - start <= block_days * DAY:
            cur.append(p)
        else:
            blocks.append(cur)
            cur = [p]
            start = p["ts"]
    blocks.append(cur)
    return blocks


def block_bootstrap_ae(v2_purchases: list[dict], a_purchases: list[dict],
                       n_sims: int = 1000, master_seed: int = 42) -> dict:
    """Phân phối AE bootstrap cho mỗi block length; trả CI 5–95% (DESCRIPTIVE)."""
    out = {}
    for bl in BLOCK_LENGTHS_DAYS:
        vb = _blocks(v2_purchases, bl)
        ab = _blocks(a_purchases, bl)
        n = min(len(vb), len(ab))
        if n == 0:
            out[bl] = {"p5": np.nan, "p50": np.nan, "p95": np.nan}
            continue
        aes = np.zeros(n_sims)
        for s in range(n_sims):
            rng = np.random.default_rng(deterministic_hash(master_seed, f"bootstrap_{bl}", s))
            idx = rng.integers(0, n, size=n)
            v2 = sum(p["eth"] for i in idx for p in vb[i])
            a = sum(p["eth"] for i in idx for p in ab[i])
            aes[s] = v2 / a * 100.0 if a > 0 else np.nan
        out[bl] = {"p5": float(np.nanpercentile(aes, 5)),
                   "p50": float(np.nanpercentile(aes, 50)),
                   "p95": float(np.nanpercentile(aes, 95)),
                   "label": "DESCRIPTIVE"}
    return out
