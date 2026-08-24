"""Dataset validate, gap detection, hash và lineage — Data Model §13, Backtest §18, §20."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

EXPECTED_FREQ = {"1d": pd.Timedelta(days=1), "15m": pd.Timedelta(minutes=15)}


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_raw(df: pd.DataFrame, raw_dir: Path, symbol: str, interval: str, source: str) -> str:
    path = raw_dir / f"{symbol}_{interval}.parquet"
    df.to_parquet(path, index=False)
    return str(path)


def gap_report(df: pd.DataFrame, interval: str) -> dict:
    """Số nến kỳ vọng/thiếu, tỷ lệ, gap dài nhất và danh sách gap theo ngày (Backtest §18)."""
    ts = pd.to_datetime(df["open_time"], utc=True).sort_values()
    freq = EXPECTED_FREQ[interval]
    if len(ts) < 2:
        return {"expected": len(ts), "missing": 0, "missing_ratio": 0.0,
                "longest_gap": 0, "gaps": []}
    expected = int((ts.iloc[-1] - ts.iloc[0]) / freq) + 1
    missing = expected - len(ts)
    diffs = ts.diff().iloc[1:]
    gaps = []
    for t, d in zip(ts.iloc[1:], diffs):
        n = int(d / freq) - 1
        if n > 0:
            gaps.append({"after": str(t - d), "missing_candles": n})
    longest = max((g["missing_candles"] for g in gaps), default=0)
    return {"expected": expected, "missing": missing,
            "missing_ratio": missing / expected if expected else 0.0,
            "longest_gap": longest, "gaps": gaps}


def build_lineage(raw_dir: str | Path, source: str = "unknown") -> dict:
    """Ghi lineage.json: symbol, interval, source, khoảng thời gian, row/missing count, hash.

    WP-A1/F-005: source phải là một trong 'binance_bulk_archive', 'binance_rest', 'synthetic',
    không phải chuỗi cố định 'see fetch/synth'.
    """
    raw = Path(raw_dir)
    entries = []
    for p in sorted(raw.glob("*.parquet")):
        df = pd.read_parquet(p)
        symbol, interval = p.stem.rsplit("_", 1)
        rep = gap_report(df, interval)
        entries.append({
            "symbol": symbol, "interval": interval, "source": source,
            "first_timestamp": str(df["open_time"].min()),
            "last_timestamp": str(df["open_time"].max()),
            "row_count": int(len(df)),
            "missing_count": int(rep["missing"]),
            "file_hash": file_sha256(p),
        })
    dataset_hash = hashlib.sha256(
        json.dumps([e["file_hash"] for e in entries]).encode()).hexdigest()
    lineage = {"files": entries, "dataset_hash": dataset_hash, "source": source}
    (raw / "lineage.json").write_text(json.dumps(lineage, indent=1))
    return lineage


def load_dataset(raw_dir: str | Path) -> dict:
    """Đọc raw parquet thành dict các DataFrame chuẩn hóa (UTC, sorted)."""
    raw = Path(raw_dir)
    out = {}
    for key in ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m"):
        p = raw / f"{key}.parquet"
        if not p.exists():
            raise FileNotFoundError(f"missing {p}; run `ethdca fetch` or `ethdca synth`")
        df = pd.read_parquet(p)
        df["open_time"] = pd.to_datetime(df["open_time"], utc=True)
        out[key] = df.sort_values("open_time").reset_index(drop=True)
    lineage_path = raw / "lineage.json"
    out["lineage"] = json.loads(lineage_path.read_text()) if lineage_path.exists() else build_lineage(raw)
    return out
