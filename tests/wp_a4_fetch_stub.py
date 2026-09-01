"""Stub I/O Binance cho WP-A4 — thay ĐÚNG lớp HTTP, không thay gì khác.

Nguồn counterexample canonical 1 + 2 theo `PROJECT/PRODUCTION_PATHS.md` §3: stub dựng
trên mã production thật (`fetch_all` → `fetch_series` → `fetch_month_archive` /
`fetch_klines` → `build_lineage` → `official_eligibility`) và tham số production thật.
KHÔNG mock eligibility, loader, verifier hay gap logic — nếu mock, counterexample sẽ
chứng minh về chính cái mock chứ không về hệ thống.

Mô hình hoá đúng hai giới hạn có thật của T-06:
  - `data.binance.vision` chỉ có file tới một tháng nào đó (archive luôn trễ so với hiện
    tại), tháng chưa có trả 404;
  - `api.binance.com` có thể bị chặn/rate-limit và trả về rỗng (BLK-001).
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import datetime, timezone

import pandas as pd

INTERVAL_MS = {"1d": 86_400_000, "15m": 900_000}
REST_LIMIT = 1000


def _ms(value) -> int:
    return int(pd.Timestamp(value).tz_localize("UTC").timestamp() * 1000)


def _month_bounds(year: int, month: int) -> tuple[int, int]:
    a = datetime(year, month, 1, tzinfo=timezone.utc)
    b = (datetime(year + 1, 1, 1, tzinfo=timezone.utc) if month == 12
         else datetime(year, month + 1, 1, tzinfo=timezone.utc))
    return int(a.timestamp() * 1000), int(b.timestamp() * 1000)


def _candles(symbol: str, interval: str, lo_ms: int, hi_ms: int,
             omit: tuple = ()) -> list[list]:
    """Nến tất định trong [lo, hi). Giá không ngẫu nhiên: stub là kênh vận chuyển."""
    step = INTERVAL_MS[interval]
    base = 130.0 if symbol.startswith("ETH") else 6000.0
    cut = [(_ms(a), _ms(b)) for a, b in omit]
    out = []
    t = lo_ms - (lo_ms % step)
    if t < lo_ms:
        t += step
    while t < hi_ms:
        if not any(a <= t < b for a, b in cut):
            px = base * (1.0 + 0.00001 * ((t // step) % 997))
            out.append([t, px, px * 1.001, px * 0.999, px, 1000.0])
        t += step
    return out


class _Resp:
    def __init__(self, status_code: int, content: bytes = b"", payload=None, text: str = ""):
        self.status_code = status_code
        self.content = content
        self.text = text
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class BinanceStubSession:
    """Sàn giả lập với độ sẵn có dữ liệu KHAI BÁO ĐƯỢC.

    archive_from / archive_through — biên (năm, tháng) mà bulk archive thực sự có file.
    rest_window                    — khoảng REST phục vụ; None nghĩa là REST bị chặn.
    omit                           — các khoảng thời gian bị khoét khỏi MỌI kênh, dùng
                                     dựng gap nội bộ (bảo trì sàn).
    """

    def __init__(self, archive_from=None, archive_through=None,
                 rest_window=None, omit=()):
        self.archive_from = archive_from
        self.archive_through = archive_through
        self.rest_window = rest_window
        self.omit = tuple(omit)
        self.calls: list[str] = []
        # ZIP phải TẤT ĐỊNH: `fetch_month_archive` tải file rồi tải CHECKSUM và so sánh.
        # Sinh lại ZIP cho lần gọi thứ hai sẽ nhúng timestamp khác và checksum lệch —
        # một stub không tất định biến test thành trò tung đồng xu.
        self._zips: dict[str, bytes] = {}

    def _archive_has(self, year: int, month: int) -> bool:
        if self.archive_from is not None and (year, month) < self.archive_from:
            return False
        if self.archive_through is not None and (year, month) > self.archive_through:
            return False
        return True

    # --- bề mặt requests.Session mà fetch.py dùng -------------------------
    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        if url.startswith("https://api.binance.com"):
            return _Resp(200, payload=self._rest(params or {}))
        if url.endswith(".CHECKSUM"):
            zip_resp = self.get(url[: -len(".CHECKSUM")])
            if zip_resp.status_code != 200:
                return _Resp(404)
            return _Resp(200, text=hashlib.sha256(zip_resp.content).hexdigest() + "  x.zip")
        return self._archive(url)

    def _archive(self, url):
        stem = url.rsplit("/", 1)[-1][: -len(".zip")]
        symbol, interval, ym = stem.split("-", 2)
        year, month = (int(x) for x in ym.split("-"))
        if not self._archive_has(year, month):
            return _Resp(404)
        lo, hi = _month_bounds(year, month)
        if stem not in self._zips:
            rows = _candles(symbol, interval, lo, hi, self.omit)
            if not rows:
                return _Resp(404)  # tháng rỗng hoàn toàn = file không tồn tại
            csv = "\n".join(",".join(str(c) for c in r) for r in rows).encode()
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                info = zipfile.ZipInfo(f"{stem}.csv", date_time=(1980, 1, 1, 0, 0, 0))
                zf.writestr(info, csv)
            self._zips[stem] = buf.getvalue()
        return _Resp(200, content=self._zips[stem])

    def _rest(self, params):
        if self.rest_window is None:
            return []
        symbol, interval = params["symbol"], params["interval"]
        lo = max(int(params["startTime"]), _ms(self.rest_window[0]))
        hi = min(int(params["endTime"]), _ms(self.rest_window[1]))
        if hi <= lo:
            return []
        rows = _candles(symbol, interval, lo, hi, self.omit)[:REST_LIMIT]
        return [[r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5])] for r in rows]
