"""Dataset validate, gap detection, hash và lineage — Data Model §13, Backtest §18, §20."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

EXPECTED_FREQ = {"1d": pd.Timedelta(days=1), "15m": pd.Timedelta(minutes=15)}

# WP-A1/A1.1 — phân loại nguồn dữ liệu canonical (docs/CONVENTIONS.md).
SOURCE_BULK_ARCHIVE = "binance_bulk_archive"
SOURCE_REST = "binance_rest"
SOURCE_SYNTHETIC = "synthetic"
SOURCE_UNKNOWN = "unknown"

VALID_SOURCES = frozenset({SOURCE_BULK_ARCHIVE, SOURCE_REST, SOURCE_SYNTHETIC, SOURCE_UNKNOWN})
#: Chỉ dữ liệu Binance thật mới đủ điều kiện official (DEC-003, WP-A1/F-005).
REAL_SOURCES = frozenset({SOURCE_BULK_ARCHIVE, SOURCE_REST})

#: Ba series canonical tạo nên dataset — Backtest §2: indicator là ETHUSDT + BTCUSDT khung
#: 1D, execution là ETHUSDT khung 15m. Đây là NƠI DUY NHẤT khai tập này: `load_dataset` nạp
#: đúng nó và `official_eligibility` đòi lineage phủ đúng nó, nên hai bên không thể lệch nhau.
REQUIRED_SERIES = ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m")


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


def _dataset_hash(entries: list[dict]) -> str:
    """Hash tập dữ liệu từ danh sách file_hash — dùng chung khi ghi và khi verify."""
    return hashlib.sha256(
        json.dumps([e["file_hash"] for e in entries]).encode()).hexdigest()


def build_lineage(raw_dir: str | Path, source: str | Mapping[str, str],
                  source_detail: Mapping[str, list[str]] | None = None) -> dict:
    """Ghi lineage.json: symbol, interval, source, khoảng thời gian, row/missing count, hash.

    WP-A1/F-005: `source` phải là một trong `VALID_SOURCES` — không còn một chuỗi cố định
    dùng chung cho mọi nguồn. Truyền một chuỗi để áp cho mọi series, hoặc mapping
    `"<symbol>_<interval>" -> source` khi mỗi series có nguồn riêng (CHECK-A1-05 yêu cầu
    phân loại theo TỪNG series). `source` là tham số bắt buộc: nơi tạo dataset là nơi duy
    nhất biết dữ liệu đến từ đâu, nên không có giá trị mặc định để quên.

    `source_detail` ghi các cơ chế thực sự đã đóng góp cho một series khi nó được lắp từ
    nhiều cơ chế (bulk archive cho tháng đủ + REST cho phần đuôi) — xem docs/CONVENTIONS.md.
    """
    raw = Path(raw_dir)
    entries = []
    for p in sorted(raw.glob("*.parquet")):
        key = p.stem
        src = source[key] if isinstance(source, Mapping) else source
        if src not in VALID_SOURCES:
            raise ValueError(f"source không hợp lệ cho {key}: {src!r}; "
                             f"phải thuộc {sorted(VALID_SOURCES)}")
        df = pd.read_parquet(p)
        symbol, interval = key.rsplit("_", 1)
        rep = gap_report(df, interval)
        entry = {
            "symbol": symbol, "interval": interval, "source": src,
            "first_timestamp": str(df["open_time"].min()),
            "last_timestamp": str(df["open_time"].max()),
            "row_count": int(len(df)),
            "missing_count": int(rep["missing"]),
            "file_hash": file_sha256(p),
        }
        if source_detail and key in source_detail:
            entry["source_detail"] = list(source_detail[key])
        entries.append(entry)
    distinct = {e["source"] for e in entries}
    lineage = {"files": entries, "dataset_hash": _dataset_hash(entries),
               "source": distinct.pop() if len(distinct) == 1 else "mixed"}
    (raw / "lineage.json").write_text(json.dumps(lineage, indent=1))
    return lineage


def verify_lineage(raw_dir: str | Path, lineage: dict) -> tuple[bool, str]:
    """Đối chiếu lineage với file thật trên đĩa (WP-A1/A1.2).

    Fail-closed: thiếu file, sai `file_hash`, hoặc `dataset_hash` không tái lập được từ
    chính danh sách file_hash đều là FAIL. Đây là phần "đã verify checksum" mà CHECK-A1-07
    đòi hỏi trước khi một run được phép mang `official: true`.
    """
    raw = Path(raw_dir)
    entries = lineage.get("files") or []
    if not entries:
        return False, "lineage_no_files"
    for e in entries:
        p = raw / f"{e.get('symbol')}_{e.get('interval')}.parquet"
        if not p.exists():
            return False, f"missing_file:{p.name}"
        if file_sha256(p) != e.get("file_hash"):
            return False, f"file_hash_mismatch:{p.name}"
    if _dataset_hash(entries) != lineage.get("dataset_hash"):
        return False, "dataset_hash_mismatch"
    return True, "verified"


def official_eligibility(raw_dir: str | Path, lineage: dict | None) -> tuple[bool, str]:
    """Nguồn sự thật DUY NHẤT cho cờ `official` (WP-A1/A1.2, DEC-003, đóng F-005).

    `official` là HÀM DẪN XUẤT từ lineage đã verify checksum, không phải một trường ghi
    được: không có tham số, flag CLI hay biến môi trường nào đi vào đây. Fail-closed —
    mọi trạng thái không tự chứng minh được đều trả về False kèm lý do, và lý do đó được
    ghi vào run record.

    Đủ tư cách official đòi hỏi lineage PHỦ ĐÚNG tập canonical `REQUIRED_SERIES`, không
    thiếu và không thừa. Kiểm checksum thôi thì chưa đủ: một lineage chỉ khai một series,
    hoặc khai thêm series lạ, vẫn có thể tự nhất quán về hash. Trước WP-A1/S008 cả hai
    trường hợp đó đều cho `(True, "verified")` (F-E2A1-02), cũng như một series canonical
    rỗng hoàn toàn (F-E2A1-01) — thiếu dữ liệu không được đọc thành không có tin xấu.

    Thứ tự kiểm cố định để reason code tất định: dạng lineage → trùng lặp → thừa → thiếu
    → (theo thứ tự canonical) checksum → rỗng → nguồn → đối chiếu checksum với đĩa.
    """
    if lineage is None:
        return False, "lineage_missing"
    if not isinstance(lineage, dict):
        return False, "lineage_malformed"
    entries = lineage.get("files")
    if not isinstance(entries, list):
        return False, "lineage_malformed"

    by_key: dict[str, dict] = {}
    for e in entries:
        if not isinstance(e, dict):
            return False, "lineage_malformed"
        key = f"{e.get('symbol')}_{e.get('interval')}"
        if key in by_key:
            return False, f"duplicate_series:{key}"
        by_key[key] = e

    for key in sorted(by_key):
        if key not in REQUIRED_SERIES:
            return False, f"unexpected_series:{key}"
    for key in REQUIRED_SERIES:
        if key not in by_key:
            return False, f"missing_required_series:{key}"

    for key in REQUIRED_SERIES:
        e = by_key[key]
        if not e.get("file_hash"):
            return False, f"checksum_missing:{key}"
        try:
            row_count = int(e.get("row_count"))
        except (TypeError, ValueError):
            return False, "lineage_malformed"
        if row_count <= 0:
            return False, f"empty_series:{key}"
        src = e.get("source")
        if src not in REAL_SOURCES:
            return False, f"source_not_real:{key}={src!r}"

    return verify_lineage(raw_dir, lineage)


def load_dataset(raw_dir: str | Path) -> dict:
    """Đọc raw parquet thành dict các DataFrame chuẩn hóa (UTC, sorted)."""
    raw = Path(raw_dir)
    out = {}
    for key in REQUIRED_SERIES:
        p = raw / f"{key}.parquet"
        if not p.exists():
            raise FileNotFoundError(f"missing {p}; run `ethdca fetch` or `ethdca synth`")
        df = pd.read_parquet(p)
        df["open_time"] = pd.to_datetime(df["open_time"], utc=True)
        out[key] = df.sort_values("open_time").reset_index(drop=True)
    lineage_path = raw / "lineage.json"
    # Không có lineage.json => không biết dữ liệu từ đâu; dựng lại với SOURCE_UNKNOWN để
    # `official_eligibility` fail-closed thay vì đoán nguồn (WP-A1/A1.2).
    out["lineage"] = (json.loads(lineage_path.read_text()) if lineage_path.exists()
                      else build_lineage(raw, SOURCE_UNKNOWN))
    return out
