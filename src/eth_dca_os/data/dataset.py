"""Dataset validate, gap detection, hash và lineage — Data Model §13, Backtest §18, §20."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

EXPECTED_FREQ = {"1d": pd.Timedelta(days=1), "15m": pd.Timedelta(minutes=15)}

#: Tỷ lệ nến thiếu tối đa mà một dataset vẫn còn đủ tư cách official — đo trên KHOẢNG
#: THỜI GIAN ĐƯỢC YÊU CẦU, không phải trên khoảng quan sát được (WP-A4, OD-A4-01).
#: Không thể đặt bằng 0: dữ liệu Binance thật có gap do bảo trì sàn, nên ngưỡng 0 sẽ từ
#: chối mọi dataset thật. Ngưỡng đặt thấp và cố định để mọi lần từ chối đều kèm số đo
#: (docs/CONVENTIONS.md); khi T-06 chạy trên dữ liệu thật, một lần từ chối là dữ kiện để
#: chủ dự án quyết định, không phải một hằng số để nới.
MAX_MISSING_RATIO = 0.01

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


def _as_utc(value) -> pd.Timestamp:
    t = pd.Timestamp(value)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def _slots(start: pd.Timestamp, end: pd.Timestamp, freq: pd.Timedelta) -> int:
    """Số nến kỳ vọng trong nửa khoảng [start, end) — làm tròn lên, 0 khi khoảng rỗng."""
    if end <= start:
        return 0
    return int(-(-(end - start) // freq))


def gap_report(df: pd.DataFrame, interval: str,
               requested_start=None, requested_end=None) -> dict:
    """Số nến kỳ vọng/thiếu, tỷ lệ, gap dài nhất và danh sách gap theo ngày (Backtest §18).

    Khi CẢ `requested_start` và `requested_end` được truyền, số nến kỳ vọng được neo vào
    **khoảng thời gian ĐƯỢC YÊU CẦU**, không phải vào khoảng quan sát được trong dữ liệu
    đã fetch (WP-A4 / OD-A4-01, đóng F-E2A1R3-05).

    Vì sao điều này bắt buộc: neo vào khoảng quan sát được khiến một lần fetch bị cắt cụt
    tự báo `missing = 0` — phần thiếu ở HAI ĐẦU là thứ mà chính dữ liệu ấy không thể tự
    khai. Một dataset chỉ phủ 8% khoảng được yêu cầu nhưng liên tục bên trong 8% đó vì thế
    từng đi qua như "không có lỗ hổng nào".

    Không truyền khoảng yêu cầu thì hàm giữ nguyên hành vi cũ (chỉ đo lỗ hổng GIỮA nến đầu
    và nến cuối quan sát được) — đủ cho chẩn đoán, KHÔNG đủ cho quyết định official.
    """
    ts = pd.to_datetime(df["open_time"], utc=True).sort_values()
    freq = EXPECTED_FREQ[interval]
    anchored = requested_start is not None and requested_end is not None

    if not anchored:
        if len(ts) < 2:
            return {"expected": len(ts), "missing": 0, "missing_ratio": 0.0,
                    "longest_gap": 0, "gaps": []}
        expected = int((ts.iloc[-1] - ts.iloc[0]) / freq) + 1
        observed = len(ts)
        req_start = req_end = None
    else:
        req_start, req_end = _as_utc(requested_start), _as_utc(requested_end)
        ts = ts[(ts >= req_start) & (ts < req_end)]
        expected = _slots(req_start, req_end, freq)
        observed = len(ts)

    gaps = []
    if len(ts) >= 2:
        diffs = ts.diff().iloc[1:]
        for t, d in zip(ts.iloc[1:], diffs):
            n = int(d / freq) - 1
            if n > 0:
                gaps.append({"after": str(t - d), "missing_candles": n})
    internal = sum(g["missing_candles"] for g in gaps)

    head = tail = 0
    if anchored:
        if observed:
            head = _slots(req_start, ts.iloc[0], freq)
            tail = _slots(ts.iloc[-1] + freq, req_end, freq)
        else:
            head = expected
    longest = max([g["missing_candles"] for g in gaps] + [head, tail], default=0)

    missing = expected - observed
    rep = {"expected": expected, "missing": missing,
           "missing_ratio": missing / expected if expected else 0.0,
           "longest_gap": longest, "gaps": gaps}
    if anchored:
        # Ba thành phần tách riêng để một lần từ chối nói được THIẾU Ở ĐÂU, không chỉ
        # thiếu bao nhiêu. `missing` vẫn là con số có thẩm quyền (kỳ vọng trừ quan sát).
        rep.update({"observed": observed, "missing_head": head,
                    "missing_internal": internal, "missing_tail": tail,
                    "requested_start": str(req_start), "requested_end": str(req_end)})
    return rep


def _dataset_hash(entries: list[dict]) -> str:
    """Hash tập dữ liệu từ danh sách file_hash — dùng chung khi ghi và khi verify."""
    return hashlib.sha256(
        json.dumps([e["file_hash"] for e in entries]).encode()).hexdigest()


def _declared_ranges(raw: Path) -> dict[str, tuple[str, str]]:
    """Khoảng yêu cầu đã khai trong `lineage.json` hiện có, nếu có.

    `build_lineage` dựng lại bản ghi TỪ FILE trên đĩa, mà file thì không mang thông tin
    "đã yêu cầu khoảng nào" — chỉ nơi sản xuất dataset biết điều đó. Vì vậy dựng lại mà
    không mang theo khai báo cũ là làm MẤT provenance, và mất provenance ở đây có nghĩa là
    mất luôn khả năng phát hiện cắt cụt (WP-A4). Khai báo truyền vào luôn thắng khai báo cũ.
    """
    path = raw / "lineage.json"
    if not path.exists():
        return {}
    try:
        prior = json.loads(path.read_text()).get("files") or []
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, AttributeError):
        return {}
    out = {}
    for e in prior:
        if not isinstance(e, dict):
            continue
        if e.get("requested_start") and e.get("requested_end"):
            out[f"{e.get('symbol')}_{e.get('interval')}"] = (e["requested_start"],
                                                             e["requested_end"])
    return out


def build_lineage(raw_dir: str | Path, source: str | Mapping[str, str],
                  source_detail: Mapping[str, list[str]] | None = None,
                  requested_range: Mapping[str, tuple] | None = None) -> dict:
    """Ghi lineage.json: symbol, interval, source, khoảng thời gian, row/missing count, hash.

    WP-A1/F-005: `source` phải là một trong `VALID_SOURCES` — không còn một chuỗi cố định
    dùng chung cho mọi nguồn. Truyền một chuỗi để áp cho mọi series, hoặc mapping
    `"<symbol>_<interval>" -> source` khi mỗi series có nguồn riêng (CHECK-A1-05 yêu cầu
    phân loại theo TỪNG series). `source` là tham số bắt buộc: nơi tạo dataset là nơi duy
    nhất biết dữ liệu đến từ đâu, nên không có giá trị mặc định để quên.

    `source_detail` ghi các cơ chế thực sự đã đóng góp cho một series khi nó được lắp từ
    nhiều cơ chế (bulk archive cho tháng đủ + REST cho phần đuôi) — xem docs/CONVENTIONS.md.

    `requested_range` là mapping `"<symbol>_<interval>" -> (start, end)` ghi lại KHOẢNG
    THỜI GIAN ĐÃ ĐƯỢC YÊU CẦU khi tạo dataset (WP-A4 / OD-A4-01). Đây là dữ kiện chỉ nơi
    sản xuất biết: `fetch_all` biết mình đã xin `start`/`end` nào, còn file parquet kết quả
    thì không. Thiếu nó, `missing_count` chỉ đo được lỗ hổng GIỮA nến đầu và nến cuối, nên
    một lần fetch bị cắt cụt tự khai `missing_count = 0` (F-E2A1R3-05). Series nào có khai
    báo thì `missing_count` được neo vào khoảng yêu cầu, và `official_eligibility` mới có
    cơ sở để từ chối dataset không phủ đủ.
    """
    raw = Path(raw_dir)
    prior = _declared_ranges(raw)
    entries = []
    for p in sorted(raw.glob("*.parquet")):
        key = p.stem
        src = source[key] if isinstance(source, Mapping) else source
        if src not in VALID_SOURCES:
            raise ValueError(f"source không hợp lệ cho {key}: {src!r}; "
                             f"phải thuộc {sorted(VALID_SOURCES)}")
        df = pd.read_parquet(p)
        symbol, interval = key.rsplit("_", 1)
        rng = (requested_range or {}).get(key) or prior.get(key)
        rep = (gap_report(df, interval, rng[0], rng[1]) if rng
               else gap_report(df, interval))
        entry = {
            "symbol": symbol, "interval": interval, "source": src,
            "first_timestamp": str(df["open_time"].min()),
            "last_timestamp": str(df["open_time"].max()),
            "row_count": int(len(df)),
            "missing_count": int(rep["missing"]),
            "file_hash": file_sha256(p),
        }
        if rng:
            entry["requested_start"] = str(rng[0])
            entry["requested_end"] = str(rng[1])
            entry["expected_count"] = int(rep["expected"])
            entry["missing_head"] = int(rep["missing_head"])
            entry["missing_internal"] = int(rep["missing_internal"])
            entry["missing_tail"] = int(rep["missing_tail"])
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

    WP-A4 / OD-A4-01 bổ sung một điều kiện nữa, và nó là điều kiện về ĐỘ PHỦ: mỗi series
    phải khai khoảng thời gian ĐƯỢC YÊU CẦU và phải phủ gần đủ khoảng đó. Trước đó,
    `missing_count` chỉ đo lỗ hổng GIỮA nến đầu và nến cuối quan sát được, nên một fetch
    bị cắt cụt — archive chỉ có tới 2020-01 trong khi yêu cầu cả năm 2020, REST bị chặn —
    khai `missing_count = 0` và đi qua cổng này với `(True, "verified")` dù thiếu ~92%
    khoảng được yêu cầu (F-E2A1R3-05). Dữ liệu bị cắt cụt không được đọc thành dữ liệu đủ,
    cũng như trước đây dữ liệu rỗng không được đọc thành "không có tin xấu".

    Thứ tự kiểm cố định để reason code tất định: dạng lineage → trùng lặp → thừa → thiếu
    → (theo thứ tự canonical) checksum → rỗng → nguồn → độ phủ → đối chiếu checksum với đĩa.
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

        # Độ phủ so với khoảng ĐƯỢC YÊU CẦU (WP-A4 / OD-A4-01, đóng F-E2A1R3-05).
        # Fail-closed khi không có khai báo: một dataset không nói được nó đã được yêu cầu
        # khoảng nào thì không thể chứng minh mình đủ, và "không chứng minh được" phải đọc
        # thành KHÔNG ĐỦ. Mọi dataset do `fetch_all`/`synth.generate` tạo đều có khai báo.
        if not e.get("requested_start") or not e.get("requested_end"):
            return False, f"coverage_undeclared:{key}"
        try:
            expected = int(e.get("expected_count"))
            missing = int(e.get("missing_count"))
        except (TypeError, ValueError):
            return False, "lineage_malformed"
        if expected <= 0 or missing < 0:
            return False, "lineage_malformed"
        if missing > expected * MAX_MISSING_RATIO:
            # Lý do mang theo SỐ ĐO, không chỉ mang theo phán quyết: một lần từ chối phải
            # đủ để người đọc biết thiếu bao nhiêu và ở đâu mà không cần mở lại dataset.
            return False, (f"incomplete_coverage:{key}={row_count}/{expected}"
                           f" head={int(e.get('missing_head', 0))}"
                           f" internal={int(e.get('missing_internal', 0))}"
                           f" tail={int(e.get('missing_tail', 0))}")

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
