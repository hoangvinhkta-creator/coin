"""Tải OHLCV Binance Spot (ETHUSDT/BTCUSDT 1D, ETHUSDT 15m) — Impl Plan Phase 1.

Chạy trên máy có truy cập Binance (môi trường CI/agent có thể bị chặn — dùng synth để dev).
Raw parquet bất biến lưu vào data/raw/; lineage ghi ở data/raw/lineage.json.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
COLUMNS = ["open_time", "open", "high", "low", "close", "volume"]
LIMIT = 1000

INTERVAL_MS = {"1d": 86_400_000, "15m": 900_000}


def fetch_klines(symbol: str, interval: str, start: datetime, end: datetime,
                 session: requests.Session | None = None, pause: float = 0.15) -> pd.DataFrame:
    s = session or requests.Session()
    start_ms = int(start.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(end.replace(tzinfo=timezone.utc).timestamp() * 1000)
    rows: list[list] = []
    cur = start_ms
    while cur < end_ms:
        for attempt in range(5):
            try:
                r = s.get(BASE_URL, params={
                    "symbol": symbol, "interval": interval,
                    "startTime": cur, "endTime": end_ms, "limit": LIMIT,
                }, timeout=30)
                r.raise_for_status()
                batch = r.json()
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        if not batch:
            break
        rows.extend(batch)
        cur = batch[-1][0] + INTERVAL_MS[interval]
        time.sleep(pause)
    df = pd.DataFrame([[b[0], float(b[1]), float(b[2]), float(b[3]), float(b[4]), float(b[5])]
                       for b in rows], columns=COLUMNS)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)


def fetch_all(raw_dir: str | Path, start: str = "2018-01-01", end: str | None = None) -> dict:
    """Tải ETHUSDT 1D + BTCUSDT 1D (từ 2018 để đủ warm-up 365d) và ETHUSDT 15m (từ 2019)."""
    from .dataset import write_raw, build_lineage

    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end) if end else datetime.now(timezone.utc).replace(tzinfo=None)

    files = {}
    for symbol, interval, s0 in (
        ("ETHUSDT", "1d", start_dt),
        ("BTCUSDT", "1d", start_dt),
        ("ETHUSDT", "15m", datetime(2019, 1, 1)),
    ):
        df = fetch_klines(symbol, interval, s0, end_dt)
        files[f"{symbol}_{interval}"] = write_raw(df, raw, symbol, interval, source="binance-api")
    lineage = build_lineage(raw)
    return {"files": files, "dataset_hash": lineage["dataset_hash"]}
