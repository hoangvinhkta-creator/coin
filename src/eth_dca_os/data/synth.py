"""Synthetic dataset generator — deterministic, seeded.

Dùng để dev/test end-to-end khi không truy cập được Binance (proxy chặn).
KHÔNG BAO GIỜ dùng cho official run: official numbers phải chạy trên dữ liệu
Binance thật qua `ethdca fetch` (Backtest §2).

ETH 15m là chuỗi gốc; ETH 1D được tổng hợp từ 15m nên hai khung luôn nhất quán.
Chuỗi có chu kỳ tăng/giảm và jump shock để tạo drawdown, crash và recovery.
Một gap 15m nhỏ được chèn có chủ đích để test xử lý data gap (Backtest §18).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .dataset import SOURCE_SYNTHETIC, build_lineage

SYNTH_SEED = 20260822


def generate(raw_dir: str | Path, start: str = "2018-01-01", end: str = "2026-06-30",
             seed: int = SYNTH_SEED) -> dict:
    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    idx15 = pd.date_range(start=start, end=end, freq="15min", tz="UTC", inclusive="left")
    n = len(idx15)
    steps_per_year = 365 * 96

    t = np.arange(n) / steps_per_year
    # Drift: chu kỳ ~4 năm + chu kỳ ~1.3 năm, quanh trend nhẹ dương
    drift = (0.20 + 1.1 * np.sin(2 * np.pi * t / 3.9 + 0.7)
             + 0.5 * np.sin(2 * np.pi * t / 1.3)) / steps_per_year
    vol = (0.75 + 0.35 * np.sin(2 * np.pi * t / 2.1 + 1.3)) / np.sqrt(steps_per_year)
    shocks = np.zeros(n)
    # Jump shocks: trung bình ~6 cú/năm, thiên về âm — tạo điều kiện crash
    n_jumps = int(6 * (n / steps_per_year))
    jump_pos = rng.choice(n, size=n_jumps, replace=False)
    shocks[jump_pos] = rng.normal(-0.02, 0.03, size=n_jumps)
    ret = drift + vol * rng.standard_normal(n) + shocks
    log_price = np.log(130.0) + np.cumsum(ret)
    close = np.exp(log_price)

    open_ = np.empty(n)
    open_[0] = close[0]
    open_[1:] = close[:-1]
    wick = np.abs(rng.normal(0, 0.0012, size=n))
    high = np.maximum(open_, close) * (1 + wick)
    low = np.minimum(open_, close) * (1 - wick)
    base_vol = 900.0 * (1 + 0.5 * np.sin(2 * np.pi * t / 1.7))
    volume = base_vol * np.exp(rng.normal(0, 0.35, size=n)) * (1 + 25 * np.abs(ret))

    eth15 = pd.DataFrame({"open_time": idx15, "open": open_, "high": high,
                          "low": low, "close": close, "volume": volume})

    # ETH 1D tổng hợp từ 15m (ngày UTC)
    g = eth15.set_index("open_time").groupby(pd.Grouper(freq="1D"))
    eth1d = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
        "volume": g["volume"].sum(),
    }).dropna().reset_index().rename(columns={"open_time": "open_time"})

    # BTC 1D: tương quan với ETH nhưng biên độ thấp hơn — tạo biến động ETHBTC
    d_ret = np.diff(np.log(eth1d["close"].to_numpy()), prepend=np.log(eth1d["close"].iloc[0]))
    m = len(eth1d)
    td = np.arange(m) / 365.0
    btc_ret = (0.25 / 365.0
               + 0.55 * d_ret
               + (0.45 / np.sqrt(365.0)) * rng.standard_normal(m)
               + (0.10 / 365.0) * np.sin(2 * np.pi * td / 2.7))
    btc_close = 6000.0 * np.exp(np.cumsum(btc_ret))
    btc_open = np.empty(m)
    btc_open[0] = btc_close[0]
    btc_open[1:] = btc_close[:-1]
    bwick = np.abs(rng.normal(0, 0.004, size=m))
    btc1d = pd.DataFrame({
        "open_time": eth1d["open_time"], "open": btc_open,
        "high": np.maximum(btc_open, btc_close) * (1 + bwick),
        "low": np.minimum(btc_open, btc_close) * (1 - bwick),
        "close": btc_close,
        "volume": 300.0 * np.exp(rng.normal(0, 0.3, size=m)),
    })

    # Cắt 15m về từ 2019 (execution data theo Backtest §2) và chèn 1 gap nhỏ có chủ đích
    eth15 = eth15[eth15["open_time"] >= pd.Timestamp("2019-01-01", tz="UTC")].reset_index(drop=True)
    gap_day = pd.Timestamp("2020-03-15", tz="UTC")
    gap_mask = (eth15["open_time"] >= gap_day + pd.Timedelta(hours=3)) & \
               (eth15["open_time"] < gap_day + pd.Timedelta(hours=4))
    eth15 = eth15[~gap_mask].reset_index(drop=True)

    eth1d.to_parquet(raw / "ETHUSDT_1d.parquet", index=False)
    btc1d.to_parquet(raw / "BTCUSDT_1d.parquet", index=False)
    eth15.to_parquet(raw / "ETHUSDT_15m.parquet", index=False)
    # WP-A1/A1.1: nguồn được khai báo tại nơi dataset được tạo. Dữ liệu tổng hợp KHÔNG BAO
    # GIỜ đủ điều kiện official (DEC-003) — `official_eligibility` chặn nhờ nhãn này.
    lineage = build_lineage(raw, SOURCE_SYNTHETIC)
    return {"rows_15m": len(eth15), "rows_1d": len(eth1d),
            "dataset_hash": lineage["dataset_hash"]}
