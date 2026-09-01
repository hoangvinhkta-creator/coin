"""WP-A4 / CHECK-A4-10 — độ phủ phải đối chiếu với KHOẢNG THỜI GIAN ĐƯỢC YÊU CẦU.

Check này do chủ dự án phê duyệt ngày 2026-09-01 (`OD-A4-01`) và đóng `F-E2A1R3-05`.

Bất biến trung tâm là một phép SO SÁNH, không phải một trường:

    khoảng được yêu cầu (start/end)  vs  khoảng thực sự fetch được
        -> gap/coverage semantics
        -> official eligibility

Trước sửa, `gap_report` chỉ đo lỗ hổng GIỮA nến đầu và nến cuối QUAN SÁT ĐƯỢC. Một lần
fetch chỉ lấy được 8,5% khoảng được yêu cầu vì thế tự khai `missing_count = 0` và đi qua
`official_eligibility` với `(True, 'verified')` — dataset cắt cụt vẫn đủ tư cách official.

Toàn bộ counterexample trong file này đi theo ĐƯỜNG SẢN XUẤT BÌNH THƯỜNG
(`fetch_all` → `build_lineage` → `official_eligibility` → `Prepared`), chỉ lớp HTTP được
thay bằng stub. Không sửa tay `lineage.json`, không mock eligibility, không dựng input thù
địch — theo `PROJECT/PRODUCTION_PATHS.md` §3 nguồn 1 + 2.
"""
from __future__ import annotations

import json
import shutil

import pandas as pd
import pytest

from eth_dca_os import MASTER_SEED
from eth_dca_os.data import fetch as fetch_mod
from eth_dca_os.data.dataset import (
    MAX_MISSING_RATIO,
    SOURCE_BULK_ARCHIVE,
    build_lineage,
    gap_report,
    official_eligibility,
)
from eth_dca_os.data.synth import generate
from eth_dca_os.pipeline import Prepared
from wp_a4_fetch_stub import BinanceStubSession


def _fetch(tmp_path, stub, monkeypatch, start, end, name="raw"):
    """Chạy ĐÚNG `fetch_all` production, chỉ thay lớp HTTP."""
    monkeypatch.setattr(fetch_mod.requests, "Session", lambda: stub)
    raw = tmp_path / name
    fetch_mod.fetch_all(raw, start=start, end=end)
    return raw, json.loads((raw / "lineage.json").read_text())


def _entry(lineage, key):
    return next(e for e in lineage["files"] if f"{e['symbol']}_{e['interval']}" == key)


# --------------------------------------------------------------- CASE A / F

def test_case_a_full_requested_range_is_eligible(tmp_path, monkeypatch):
    """CASE A — fetch phủ đủ khoảng được yêu cầu => PASS.

    Đây cũng là positive control của toàn bộ file: nếu thiếu nó, một cổng "luôn từ chối"
    sẽ qua được mọi case còn lại. Cổng phải MỞ ĐƯỢC trên đường sản xuất bình thường.
    """
    stub = BinanceStubSession(archive_through=(2020, 4))
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2020-04-01")

    for key in ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m"):
        e = _entry(lineage, key)
        assert e["missing_count"] == 0, (key, e)
        assert e["requested_start"] and e["requested_end"], key

    assert official_eligibility(raw, lineage) == (True, "verified")


def test_case_f_complete_dataset_no_regression(tmp_path):
    """CASE F — dataset đầy đủ vẫn đi qua như trước, không regression.

    Dùng đúng đường positive control mà contract WP-A1 đã đóng băng dùng: dữ liệu thật
    trên đĩa, checksum tính thật, chỉ NHÃN nguồn do fixture đặt.
    """
    raw = tmp_path / "raw"
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    lineage = build_lineage(raw, SOURCE_BULK_ARCHIVE)

    for key in ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m"):
        assert _entry(lineage, key)["missing_count"] == 0, key
    assert official_eligibility(raw, lineage) == (True, "verified")


# ------------------------------------------------------- CASE B / C / D / E

def test_case_b_truncated_beginning_fails(tmp_path, monkeypatch):
    """CASE B — thiếu phần ĐẦU khoảng yêu cầu => FAIL completeness.

    Kịch bản thật: archive chưa có tháng 01, REST chỉ phục vụ được từ tháng 02.
    """
    stub = BinanceStubSession(archive_from=(2020, 2), archive_through=(2020, 4),
                              rest_window=("2020-02-01", "2020-04-01"))
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2020-04-01")

    e = _entry(lineage, "ETHUSDT_1d")
    assert e["missing_head"] > 0, e
    assert e["missing_count"] == e["expected_count"] - e["row_count"]
    ok, reason = official_eligibility(raw, lineage)
    assert ok is False and reason.startswith("incomplete_coverage:ETHUSDT_1d"), reason


def test_case_c_truncated_ending_fails(tmp_path, monkeypatch):
    """CASE C — thiếu phần ĐUÔI khoảng yêu cầu => FAIL completeness.

    Kịch bản thật nhất của T-06: archive luôn trễ, REST bị chặn (BLK-001).
    """
    stub = BinanceStubSession(archive_through=(2020, 2))
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2020-04-01")

    e = _entry(lineage, "ETHUSDT_1d")
    assert e["missing_tail"] > 0, e
    assert e["missing_head"] == 0, e
    ok, reason = official_eligibility(raw, lineage)
    assert ok is False and reason.startswith("incomplete_coverage:ETHUSDT_1d"), reason


def test_case_d_large_internal_gap_fails(tmp_path, monkeypatch):
    """CASE D — gap NỘI BỘ lớn => FAIL completeness.

    Hai đầu phủ đủ, nên case này chứng minh việc siết không chỉ là kiểm biên: phần giữa
    bị khoét 20 ngày vẫn phải bị từ chối.
    """
    stub = BinanceStubSession(archive_through=(2020, 4),
                              omit=[("2020-02-05", "2020-02-25")])
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2020-04-01")

    e = _entry(lineage, "ETHUSDT_1d")
    assert e["missing_head"] == 0 and e["missing_tail"] == 0, e
    assert e["missing_internal"] == 20, e
    ok, reason = official_eligibility(raw, lineage)
    assert ok is False and reason.startswith("incomplete_coverage:ETHUSDT_1d"), reason


def test_case_e_eight_percent_coverage_fails(tmp_path, monkeypatch):
    """CASE E — dữ liệu quan sát được LIÊN TỤC nhưng chỉ phủ ~8% khoảng yêu cầu => FAIL.

    Đây là counterexample nguyên bản của `F-E2A1R3-05`. Trước sửa: `missing_count = 0`
    cho cả ba series và `official_eligibility -> (True, 'verified')`.
    """
    stub = BinanceStubSession(archive_through=(2020, 1))
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2021-01-01")

    e = _entry(lineage, "ETHUSDT_1d")
    assert e["row_count"] == 31 and e["expected_count"] == 366, e
    assert e["row_count"] / e["expected_count"] < 0.09, "phải là ca ~8% coverage"
    # Dữ liệu quan sát được TỰ LIÊN TỤC: không một gap nội bộ nào.
    assert e["missing_internal"] == 0, e
    assert e["missing_count"] == 335, e

    ok, reason = official_eligibility(raw, lineage)
    assert ok is False and reason.startswith("incomplete_coverage:ETHUSDT_1d"), reason
    assert "31/366" in reason, "lý do phải mang theo SỐ ĐO, không chỉ phán quyết"


# ---------------------------------------------- hệ quả ở tầng quyết định

def test_truncated_dataset_cannot_become_an_official_run(tmp_path, monkeypatch):
    """Dataset cắt cụt không đi tiếp được như dataset official để tạo quyết định.

    Chứng minh ở tầng `Prepared` — nơi DUY NHẤT mọi gate lấy cờ `official` (WP-A1/A1.2),
    nên chặn ở đây là chặn cho toàn bộ Gate 1/2/3 và verdict.
    """
    stub = BinanceStubSession(archive_through=(2021, 6))
    raw, _ = _fetch(tmp_path, stub, monkeypatch, "2018-01-01", "2026-06-30")

    prep = Prepared(raw)
    assert prep.official_eligible is False
    assert prep.official_reason.startswith("incomplete_coverage:"), prep.official_reason


# ------------------------------------------------ ngữ nghĩa gap_report

def test_gap_report_anchors_to_requested_range_not_observed_window():
    """Cùng một DataFrame: neo vào khoảng quan sát được nói 0 thiếu, neo vào khoảng yêu
    cầu nói đúng phần thiếu. Đây chính là root cause của F-E2A1R3-05."""
    df = pd.DataFrame({"open_time": pd.date_range("2020-01-01", periods=31,
                                                  freq="1D", tz="UTC")})

    legacy = gap_report(df, "1d")
    assert legacy["missing"] == 0, "hành vi cũ được giữ nguyên khi không khai khoảng"

    anchored = gap_report(df, "1d", "2020-01-01", "2021-01-01")
    assert anchored["expected"] == 366
    assert anchored["missing"] == 335
    assert (anchored["missing_head"], anchored["missing_internal"],
            anchored["missing_tail"]) == (0, 0, 335)


def test_gap_report_splits_head_internal_tail():
    """Một lần từ chối phải nói được THIẾU Ở ĐÂU, không chỉ thiếu bao nhiêu."""
    days = ([pd.Timestamp("2020-01-05", tz="UTC") + pd.Timedelta(days=i) for i in range(5)]
            + [pd.Timestamp("2020-01-20", tz="UTC") + pd.Timedelta(days=i) for i in range(5)])
    rep = gap_report(pd.DataFrame({"open_time": days}), "1d", "2020-01-01", "2020-02-01")
    assert rep["expected"] == 31
    assert rep["missing_head"] == 4          # 01-01..01-04
    assert rep["missing_internal"] == 10     # 01-10..01-19
    assert rep["missing_tail"] == 7          # 01-25..01-31
    assert rep["missing"] == 21 == rep["missing_head"] + rep["missing_internal"] + rep["missing_tail"]


def test_gap_report_empty_series_against_requested_range():
    """Không một nến nào => thiếu TOÀN BỘ khoảng, không phải 'không có tin xấu'."""
    empty = pd.DataFrame({"open_time": pd.to_datetime([], utc=True)})
    rep = gap_report(empty, "1d", "2020-01-01", "2020-02-01")
    assert rep["expected"] == 31 and rep["missing"] == 31
    assert rep["missing_ratio"] == 1.0


def test_intentional_synth_gap_still_detected_and_tolerated(tmp_path):
    """Regression: gap 4 nến cố ý của synth vẫn bị PHÁT HIỆN, và vẫn dưới ngưỡng.

    Nếu ngưỡng bị siết tới mức 0, dữ liệu Binance thật (có gap bảo trì) sẽ không bao giờ
    official được — test này khoá cả hai phía của ngưỡng.
    """
    raw = tmp_path / "raw"
    generate(raw, start="2020-01-01", end="2021-01-01", seed=MASTER_SEED)
    lineage = json.loads((raw / "lineage.json").read_text())
    e = _entry(lineage, "ETHUSDT_15m")
    assert e["missing_count"] == 4, e
    assert 0 < e["missing_count"] <= e["expected_count"] * MAX_MISSING_RATIO


# ------------------------------------------------ fail-closed khi thiếu khai báo

def test_coverage_undeclared_is_fail_closed(tmp_path):
    """Lineage không khai được khoảng yêu cầu => KHÔNG official.

    "Không chứng minh được là đủ" phải đọc thành KHÔNG ĐỦ, cùng nguyên tắc đã dùng cho
    dữ liệu rỗng (F-E2A1-01) và cho lineage thiếu series (F-E2A1-02).
    """
    raw = tmp_path / "raw"
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    lineage = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    assert official_eligibility(raw, lineage)[0] is True, "positive control"

    stripped = json.loads(json.dumps(lineage))
    for e in stripped["files"]:
        e.pop("requested_start", None)
        e.pop("requested_end", None)
    ok, reason = official_eligibility(raw, stripped)
    assert ok is False and reason.startswith("coverage_undeclared:"), reason


def test_rebuild_does_not_drop_requested_range(tmp_path):
    """`build_lineage` dựng lại từ file trên đĩa KHÔNG được đánh rơi khai báo cũ.

    File parquet không mang thông tin "đã yêu cầu khoảng nào"; đánh rơi nó là mất khả
    năng phát hiện cắt cụt ở mọi lần dựng lại sau đó.
    """
    raw = tmp_path / "raw"
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    before = _entry(json.loads((raw / "lineage.json").read_text()), "ETHUSDT_1d")
    after = _entry(build_lineage(raw, SOURCE_BULK_ARCHIVE), "ETHUSDT_1d")
    assert (after["requested_start"], after["requested_end"]) == \
           (before["requested_start"], before["requested_end"])


def test_official_eligibility_signature_unchanged():
    """Khoảng yêu cầu phải đi qua LINEAGE, không qua tham số mới của cổng.

    Contract WP-A1 (`test_a1_07_no_cli_or_env_surface_can_force_official`) khoá chữ ký
    `official_eligibility(raw_dir, lineage)`; thêm tham số ở đây sẽ mở lại đúng bề mặt
    mà WP-A1 vừa đóng.
    """
    import inspect
    assert list(inspect.signature(official_eligibility).parameters) == ["raw_dir", "lineage"]


@pytest.mark.parametrize("field", ["expected_count", "missing_count"])
def test_malformed_coverage_fields_are_fail_closed(tmp_path, field):
    raw = tmp_path / "raw"
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    lineage = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    broken = json.loads(json.dumps(lineage))
    broken["files"][0][field] = "khong-phai-so"
    assert official_eligibility(raw, broken) == (False, "lineage_malformed")


def test_dataset_hash_is_unchanged_by_coverage_fields(tmp_path):
    """Trường độ phủ KHÔNG được làm đổi `dataset_hash` — nếu đổi, mọi run record cũ và
    `manifest_hash` sẽ trôi mà không có lý do nghiệp vụ nào."""
    raw = tmp_path / "raw"
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    lineage = json.loads((raw / "lineage.json").read_text())
    import hashlib as _h
    expected = _h.sha256(
        json.dumps([e["file_hash"] for e in lineage["files"]]).encode()).hexdigest()
    assert lineage["dataset_hash"] == expected


def test_stub_does_not_shadow_production_code(tmp_path, monkeypatch):
    """Counterexample phải đi qua mã production thật: stub chỉ thay `requests.Session`."""
    stub = BinanceStubSession(archive_through=(2020, 4))
    raw, lineage = _fetch(tmp_path, stub, monkeypatch, "2020-01-01", "2020-04-01")
    assert any("data.binance.vision" in c for c in stub.calls), "phải gọi đường archive thật"
    assert lineage["files"], "lineage phải do build_lineage thật sinh ra"
    assert (raw / "ETHUSDT_1d.parquet").exists()
