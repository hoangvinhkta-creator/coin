"""Xuất seed cho app theo dõi trên web — `ethdca export-live`.

App web không gọi được Binance (CSP của trang chặn host ngoài), nên nó cần một file
seed do engine Python thật sinh ra: lịch sử daily đủ để tính mọi indicator bắt buộc,
cộng OSCORE do Python tính cho một số ngày gần nhất.

Số Python đó KHÔNG phải để hiển thị — app tự tính lại bằng JS rồi đối chiếu. Nếu lệch
quá dung sai, app phải cảnh báo: đó là cách duy nhất phát hiện hai bản cài đặt trôi khỏi
nhau, vì Impl Plan §1 yêu cầu live và backtest dùng chung một core strategy function mà
một trang tĩnh thì không chạy được Python.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from . import STRATEGY_VERSION
from .config import BASELINE_STRATEGY
from .data.dataset import load_dataset
from .indicators import compute_daily_indicators
from .score import compute_scores

# 365 ngày warm-up cho High365/Percentile365, cộng biên để RSI/ADR ổn định.
HISTORY_DAYS = 420
# Số ngày cuối kèm score Python để app đối chiếu.
PARITY_DAYS = 40


def _clean(x):
    if x is None:
        return None
    if isinstance(x, (np.floating, float)):
        f = float(x)
        return None if f != f else round(f, 10)
    if isinstance(x, (np.integer, int)):
        return int(x)
    return x


def build_seed(raw_dir: str | Path, history_days: int = HISTORY_DAYS,
               parity_days: int = PARITY_DAYS) -> dict:
    ds = load_dataset(raw_dir)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = compute_scores(ind, BASELINE_STRATEGY.score_weights)

    eth = ds["ETHUSDT_1d"].set_index(
        pd.to_datetime(ds["ETHUSDT_1d"]["open_time"], utc=True).dt.normalize())
    tail = ind.index[-history_days:]

    history = []
    for day in tail:
        history.append({
            "d": day.strftime("%Y-%m-%d"),
            "e": _clean(ind.loc[day, "close"]),
            "b": _clean(ind.loc[day, "btc_close"]),
            "v": _clean(eth.loc[day, "volume"]) if day in eth.index else None,
        })

    parity = []
    for day in ind.index[-parity_days:]:
        row = scores.loc[day]
        parity.append({
            "d": day.strftime("%Y-%m-%d"),
            "oscore": _clean(row["oscore"]),
            "pl": _clean(row["price_location_score"]),
            "ms": _clean(row["market_stress_score"]),
            "rv": _clean(row["relative_value_score"]),
            "dq": str(row["data_quality"]),
        })

    cfg = asdict(BASELINE_STRATEGY)
    cfg["score_weights"] = list(BASELINE_STRATEGY.score_weights)

    return {
        "schema": "ethdca.live_seed/1",
        "strategy_version": STRATEGY_VERSION,
        "strategy_config_hash": BASELINE_STRATEGY.hash,
        "dataset_hash": ds["lineage"]["dataset_hash"],
        "config": cfg,
        "history": history,
        "parity": parity,
    }


def write_seed(out_dir: str | Path, raw_dir: str | Path, **kw) -> Path:
    seed = build_seed(raw_dir, **kw)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "live_seed.json"
    path.write_text(json.dumps(seed, ensure_ascii=False, separators=(",", ":")))
    return path
