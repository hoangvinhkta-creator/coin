"""Daily indicators — precompute MỘT LẦN và cache (Impl Plan §4).

Mọi giá trị của ngày D chỉ dùng dữ liệu tới hết nến daily D (no lookahead);
việc "chỉ áp dụng sau khi nến D đóng" do engine đảm nhiệm (Backtest §2).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def wilder_rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.full_like(close, np.nan)
    avg_loss = np.full_like(close, np.nan)
    if len(close) <= period:
        return np.full_like(close, np.nan)
    avg_gain[period] = gain[1:period + 1].mean()
    avg_loss[period] = loss[1:period + 1].mean()
    for i in range(period + 1, len(close)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i]) / period
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i]) / period
    rs = avg_gain / np.where(avg_loss == 0, np.nan, avg_loss)
    rsi = 100 - 100 / (1 + rs)
    rsi = np.where(np.isnan(rsi) & (avg_loss == 0) & ~np.isnan(avg_gain), 100.0, rsi)
    return rsi


def _rolling_percentile_of_last(values: np.ndarray, window: int) -> np.ndarray:
    """Tỷ lệ 0–1 các giá trị trong `window` gần nhất THẤP HƠN giá trị hiện tại."""
    n = len(values)
    out = np.full(n, np.nan)
    for i in range(window - 1, n):
        w = values[i - window + 1: i + 1]
        out[i] = np.count_nonzero(w < values[i]) / window
    return out


def compute_daily_indicators(eth1d: pd.DataFrame, btc1d: pd.DataFrame) -> pd.DataFrame:
    """Trả về DataFrame indexed theo ngày UTC với mọi indicator bắt buộc."""
    eth = eth1d.set_index(pd.to_datetime(eth1d["open_time"], utc=True).dt.normalize())
    btc = btc1d.set_index(pd.to_datetime(btc1d["open_time"], utc=True).dt.normalize())
    df = pd.DataFrame(index=eth.index)
    close = eth["close"].to_numpy(float)
    df["close"] = close
    df["btc_close"] = btc["close"].reindex(eth.index).to_numpy(float)

    s_close = eth["close"]
    df["high365"] = s_close.rolling(365, min_periods=365).max().to_numpy()
    df["dd365"] = close / df["high365"].to_numpy() - 1
    df["ma200"] = s_close.rolling(200, min_periods=200).mean().to_numpy()
    df["ma_ratio"] = close / df["ma200"].to_numpy()
    df["ma200_slope"] = pd.Series(df["ma200"].to_numpy(), index=df.index).diff().to_numpy()
    df["percentile365"] = _rolling_percentile_of_last(close, 365)

    df["rsi14"] = wilder_rsi(close, 14)
    df["return7"] = close / np.roll(close, 7) - 1
    df.iloc[:7, df.columns.get_loc("return7")] = np.nan
    vol = eth["volume"]
    df["vol7"] = vol.rolling(7, min_periods=7).mean().to_numpy()
    df["vol90"] = vol.rolling(90, min_periods=90).mean().to_numpy()
    df["volume_ratio"] = df["vol7"] / df["vol90"]
    # Diagnostic volume z-score 365 ngày (Strategy §2.4) — không dùng cho production factor
    vmean = vol.rolling(365, min_periods=365).mean()
    vstd = vol.rolling(365, min_periods=365).std()
    df["volume_z365"] = ((vol - vmean) / vstd).to_numpy()

    daily_ret = pd.Series(close, index=df.index).pct_change()
    df["adr30"] = daily_ret.abs().rolling(30, min_periods=30).mean().to_numpy()

    ethbtc = close / df["btc_close"].to_numpy()
    df["ethbtc"] = ethbtc
    df["ethbtc_return30"] = ethbtc / np.roll(ethbtc, 30) - 1
    df.iloc[:30, df.columns.get_loc("ethbtc_return30")] = np.nan
    df["ethbtc_percentile180"] = _rolling_percentile_of_last(ethbtc, 180)
    return df
