"""Fetch layer: enumeration tháng, URL archive, parse CSV, verify checksum.

Không gọi mạng — dùng session giả để kiểm đúng hành vi hai kênh (archive + REST).
"""
import hashlib
import io
import zipfile
from datetime import datetime

import pandas as pd
import pytest

from eth_dca_os.data.fetch import (
    archive_urls,
    fetch_month_archive,
    months_between,
)


def test_months_between_inclusive():
    ms = months_between(datetime(2023, 11, 1), datetime(2024, 2, 15))
    assert ms == [(2023, 11), (2023, 12), (2024, 1), (2024, 2)]
    assert months_between(datetime(2024, 5, 1), datetime(2024, 5, 31)) == [(2024, 5)]


def test_archive_urls():
    zip_url, sum_url = archive_urls("ETHUSDT", "15m", 2023, 1)
    assert zip_url == ("https://data.binance.vision/data/spot/monthly/klines/"
                       "ETHUSDT/15m/ETHUSDT-15m-2023-01.zip")
    assert sum_url == zip_url + ".CHECKSUM"


def _zip_payload(rows: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("ETHUSDT-15m-2023-01.csv", rows)
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, content=b"", status_code=200, text=""):
        self.content = content
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class _FakeSession:
    def __init__(self, mapping):
        self.mapping = mapping

    def get(self, url, **kw):
        return self.mapping.get(url, _FakeResponse(status_code=404))


ROWS = ("1672531200000,1196.1,1200.0,1195.0,1199.5,1234.5,1672532099999,0,0,0,0,0\n"
        "1672532100000,1199.5,1205.0,1198.0,1204.0,2345.6,1672532999999,0,0,0,0,0\n")


def test_fetch_month_archive_parses_and_verifies():
    payload = _zip_payload(ROWS)
    zip_url, sum_url = archive_urls("ETHUSDT", "15m", 2023, 1)
    digest = hashlib.sha256(payload).hexdigest()
    session = _FakeSession({
        zip_url: _FakeResponse(content=payload),
        sum_url: _FakeResponse(text=f"{digest}  ETHUSDT-15m-2023-01.zip"),
    })
    df = fetch_month_archive("ETHUSDT", "15m", 2023, 1, session)
    assert list(df.columns) == ["open_time", "open", "high", "low", "close", "volume"]
    assert len(df) == 2
    assert df["open_time"].iloc[0] == pd.Timestamp("2023-01-01 00:00:00", tz="UTC")
    assert df["close"].iloc[1] == pytest.approx(1204.0)


def test_fetch_month_archive_rejects_bad_checksum():
    payload = _zip_payload(ROWS)
    zip_url, sum_url = archive_urls("ETHUSDT", "15m", 2023, 1)
    session = _FakeSession({
        zip_url: _FakeResponse(content=payload),
        sum_url: _FakeResponse(text="0" * 64 + "  ETHUSDT-15m-2023-01.zip"),
    })
    with pytest.raises(ValueError, match="checksum mismatch"):
        fetch_month_archive("ETHUSDT", "15m", 2023, 1, session)


def test_fetch_month_archive_missing_month_returns_none():
    session = _FakeSession({})   # mọi URL trả 404
    assert fetch_month_archive("ETHUSDT", "15m", 2099, 1, session) is None
