"""Tải OHLCV Binance Spot (ETHUSDT/BTCUSDT 1D, ETHUSDT 15m) — Impl Plan Phase 1.

Hai kênh, theo đúng docs/DATA_SOURCES.md:
  - Bulk archive data.binance.vision: ZIP theo tháng + CHECKSUM SHA256. Dùng cho phần
    lịch sử (~268k nến 15m) — miễn phí, không key, không rate limit đáng kể.
  - REST /api/v3/klines: chỉ để bù tháng hiện tại chưa có trong archive. Weight 2/request,
    giới hạn 6000 weight/phút theo IP; market data không cần API key.

Chạy trên máy có truy cập Binance (môi trường CI/agent có thể bị chặn — dùng synth để dev).
Raw parquet bất biến lưu vào data/raw/; lineage ghi ở data/raw/lineage.json.
"""
from __future__ import annotations

import hashlib
import io
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from .dataset import SOURCE_BULK_ARCHIVE, SOURCE_REST

BASE_URL = "https://api.binance.com/api/v3/klines"
ARCHIVE_URL = "https://data.binance.vision/data/spot/monthly/klines"
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


def months_between(start: datetime, end: datetime) -> list[tuple[int, int]]:
    """Danh sách (year, month) đầy đủ từ start tới end, bao gồm cả tháng của end."""
    out, y, m = [], start.year, start.month
    while (y, m) <= (end.year, end.month):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def archive_urls(symbol: str, interval: str, year: int, month: int) -> tuple[str, str]:
    stem = f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"
    base = f"{ARCHIVE_URL}/{symbol}/{interval}/{stem}"
    return base, base + ".CHECKSUM"


def _parse_archive_csv(data: bytes) -> pd.DataFrame:
    """CSV của archive không có header; sáu cột đầu trùng thứ tự với REST klines."""
    df = pd.read_csv(io.BytesIO(data), header=None, usecols=[0, 1, 2, 3, 4, 5],
                     names=COLUMNS)
    # Binance đổi đơn vị open_time từ ms sang µs ở một số tháng gần đây.
    unit = "us" if df["open_time"].iloc[0] > 1e15 else "ms"
    df["open_time"] = pd.to_datetime(df["open_time"], unit=unit, utc=True)
    return df


def fetch_month_archive(symbol: str, interval: str, year: int, month: int,
                        session: requests.Session | None = None,
                        verify_checksum: bool = True) -> pd.DataFrame | None:
    """Tải một tháng từ data.binance.vision và verify SHA256. None nếu tháng chưa tồn tại."""
    s = session or requests.Session()
    zip_url, sum_url = archive_urls(symbol, interval, year, month)
    r = s.get(zip_url, timeout=120)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    if verify_checksum:
        cs = s.get(sum_url, timeout=30)
        if cs.status_code == 200:
            expected = cs.text.split()[0].strip()
            actual = hashlib.sha256(r.content).hexdigest()
            if actual != expected:
                raise ValueError(
                    f"checksum mismatch cho {zip_url}: {actual} != {expected}")
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        name = zf.namelist()[0]
        return _parse_archive_csv(zf.read(name))


def fetch_series(symbol: str, interval: str, start: datetime, end: datetime,
                 session: requests.Session | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Bulk archive cho các tháng đã hoàn tất, REST cho phần đuôi còn thiếu.

    WP-A1/A1.1: trả kèm danh sách cơ chế THỰC SỰ đã đóng góp cho series này, để lineage
    ghi được nguồn thật thay vì một chuỗi cố định. Thứ tự phản ánh mức đóng góp: archive
    trước (các tháng đủ), REST sau (phần đuôi chưa lên archive).
    """
    s = session or requests.Session()
    frames = []
    used: list[str] = []
    for year, month in months_between(start, end):
        df = fetch_month_archive(symbol, interval, year, month, s)
        if df is None:
            break  # tháng chưa có trong archive -> phần còn lại lấy qua REST
        frames.append(df)
    if frames:
        used.append(SOURCE_BULK_ARCHIVE)
    have_until = frames[-1]["open_time"].max() if frames else None
    rest_from = (have_until.to_pydatetime().replace(tzinfo=None)
                 + pd.Timedelta(INTERVAL_MS[interval], unit="ms").to_pytimedelta()
                 ) if have_until is not None else start
    if rest_from < end:
        tail = fetch_klines(symbol, interval, rest_from, end, s)
        if len(tail):
            frames.append(tail)
            used.append(SOURCE_REST)
    if not frames:
        return pd.DataFrame(columns=COLUMNS), used
    out = pd.concat(frames, ignore_index=True)
    out = out[(out["open_time"] >= pd.Timestamp(start, tz="UTC"))
              & (out["open_time"] < pd.Timestamp(end, tz="UTC"))]
    return (out.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True),
            used)


def fetch_all(raw_dir: str | Path, start: str = "2018-01-01", end: str | None = None) -> dict:
    """Tải ETHUSDT 1D + BTCUSDT 1D (từ 2018 để đủ warm-up 365d) và ETHUSDT 15m (từ 2019)."""
    from .dataset import build_lineage, write_raw

    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end) if end else datetime.now(timezone.utc).replace(tzinfo=None)

    session = requests.Session()
    files, sources, details = {}, {}, {}
    for symbol, interval, s0 in (
        ("ETHUSDT", "1d", start_dt),
        ("BTCUSDT", "1d", start_dt),
        ("ETHUSDT", "15m", datetime(2019, 1, 1)),
    ):
        key = f"{symbol}_{interval}"
        df, used = fetch_series(symbol, interval, s0, end_dt, session)
        # WP-A1/A1.1: nhãn canonical là cơ chế CHÍNH của series; khi series được lắp từ cả
        # archive lẫn REST, thành phần đầy đủ nằm ở `source_detail` (docs/CONVENTIONS.md).
        sources[key] = used[0] if used else SOURCE_REST
        details[key] = used
        files[key] = write_raw(df, raw, symbol, interval, source=sources[key])
    lineage = build_lineage(raw, sources, source_detail=details)
    return {"files": files, "dataset_hash": lineage["dataset_hash"],
            "sources": sources, "source_detail": details}
