"""WP-A1/S008 — Official Eligibility Contract (đóng băng tại PRE-S008, commit bd7c5ff).

Bất biến trung tâm là một CHUỖI DẪN XUẤT, không phải một danh sách trường:

    dataset lineage -> verified source + phủ đủ REQUIRED_SERIES -> official eligibility

Suite này thi hành bảng contract 20 case trong
`docs/decisions/PRE-S008-WP-A1-decision-pack.md` §10. Mỗi case khẳng định CẢ hai thứ:
cờ `official` VÀ reason code — reason code phải phân biệt được nguyên nhân, nếu không thì
một cổng "luôn từ chối" cũng sẽ qua được toàn bộ phần negative.

Vì thế `test_ec_12/20` (positive control) là phần không thể thiếu: nó chạy trên fixture có
dữ liệu thật, checksum tính thật, không mock verifier/loader/eligibility, và bắt buộc cho
`official=True`. Ép `official_eligibility` trả False vĩnh viễn phải làm nó đỏ (MUTATION-6).
"""
from __future__ import annotations

import json
import shutil

import pandas as pd
import pytest

from eth_dca_os import MASTER_SEED
from eth_dca_os.data.dataset import (
    REAL_SOURCES,
    REQUIRED_SERIES,
    SOURCE_BULK_ARCHIVE,
    SOURCE_SYNTHETIC,
    SOURCE_UNKNOWN,
    build_lineage,
    load_dataset,
    official_eligibility,
)
from eth_dca_os.data.synth import generate
from eth_dca_os.pipeline import Prepared, run_gate1, run_gate2


# --------------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def real_like_raw(tmp_path_factory):
    """Fixture 'verified real-like' — positive control gốc của toàn bộ suite.

    Dữ liệu THẬT trên đĩa (parquet do `synth` sinh), đủ 3/3 REQUIRED_SERIES, mỗi series
    `row_count > 0`, checksum do `build_lineage` TÍNH từ chính các file đó. Chỉ NHÃN nguồn
    là do fixture đặt — nhãn là dữ liệu, không phải mock. Không patch verifier, loader hay
    eligibility ở bất kỳ đâu trong file này.

    Giới hạn phải nói thẳng: fixture chứng minh cổng MỞ ĐƯỢC khi nhãn hợp lệ và checksum
    khớp; nó không chứng minh dữ liệu thật sự của Binance. Phân biệt điều đó cần đối chiếu
    `ethdca freeze` hai máy theo DEC-003, nằm ngoài khả năng của mã (docs/CONVENTIONS.md).
    """
    raw = tmp_path_factory.mktemp("ec_real_like")
    generate(raw, start="2022-01-01", end="2025-06-30", seed=MASTER_SEED)
    build_lineage(raw, SOURCE_BULK_ARCHIVE)
    return raw


def _fresh(real_like_raw, tmp_path):
    dst = tmp_path / "raw"
    shutil.copytree(real_like_raw, dst)
    return dst


def _lineage(raw):
    return json.loads((raw / "lineage.json").read_text())


def _put(raw, lineage):
    (raw / "lineage.json").write_text(json.dumps(lineage, indent=1))


def _drop(raw, key):
    lin = _lineage(raw)
    lin["files"] = [e for e in lin["files"] if f"{e['symbol']}_{e['interval']}" != key]
    _put(raw, lin)
    return lin


# ===== CASE 12 & 20 — POSITIVE CONTROL (liveness: cổng phải MỞ được)

def test_ec_12_positive_control_eligibility(real_like_raw):
    ok, reason = official_eligibility(real_like_raw, _lineage(real_like_raw))
    assert ok is True, f"positive control bị từ chối: {reason}"
    assert reason == "verified"


def test_ec_20_positive_control_gate_level(real_like_raw, tmp_path):
    """Chạy pipeline THẬT, không `--dev-limit`: lineage đủ tư cách phải cho official=True.

    Đây là nửa 'liveness' của yêu cầu hai chiều. Không có nó, một implementation trả False
    vĩnh viễn vẫn qua được mọi case fail-closed bên dưới.
    """
    prep = Prepared(real_like_raw)
    assert prep.official_eligible is True, prep.official_reason

    payload = run_gate1(prep, tmp_path / "out")
    assert payload["dev_limit"] is None
    assert payload["official"] is True, payload["official_reason"]
    assert payload["run_record"]["official"] is True
    assert payload["run_record"]["data_source"] == SOURCE_BULK_ARCHIVE


# ===== CASE 1-2 — nguồn không thật

def test_ec_01_synthetic_not_official(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    ok, reason = official_eligibility(raw, build_lineage(raw, SOURCE_SYNTHETIC))
    assert ok is False
    assert reason.startswith("source_not_real:") and SOURCE_SYNTHETIC in reason


def test_ec_02_unknown_source_not_official(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    ok, reason = official_eligibility(raw, build_lineage(raw, SOURCE_UNKNOWN))
    assert ok is False
    assert reason.startswith("source_not_real:") and SOURCE_UNKNOWN in reason


# ===== CASE 3 — series canonical rỗng (F-E2A1-01)

def test_ec_03_empty_canonical_series_not_official(real_like_raw, tmp_path):
    """Series canonical 0 dòng KHÔNG BAO GIỜ đủ tư cách, kể cả khi nhãn và hash đều hợp lệ.

    Trước S008 trường hợp này cho `(True, 'verified')`: `fetch_all` gán `binance_rest` cho
    một series mà không cơ chế nào đóng góp, rồi eligibility không hề nhìn `row_count`.
    """
    raw = _fresh(real_like_raw, tmp_path)
    p = raw / "ETHUSDT_15m.parquet"
    pd.read_parquet(p).iloc[0:0].to_parquet(p, index=False)
    lin = build_lineage(raw, SOURCE_BULK_ARCHIVE)

    rows = {f"{e['symbol']}_{e['interval']}": e["row_count"] for e in lin["files"]}
    assert rows["ETHUSDT_15m"] == 0, "precondition hỏng: series chưa thật sự rỗng"

    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "empty_series:ETHUSDT_15m"


# ===== CASE 4,7,8,18,19 — coverage invariant hai chiều (F-E2A1-02)

def test_ec_04_missing_required_series(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _drop(raw, "BTCUSDT_1d")
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "missing_required_series:BTCUSDT_1d"


def test_ec_07_lineage_only_series(real_like_raw, tmp_path):
    """Lineage khai series mà loader không bao giờ nạp -> FAIL CLOSED (RULE-4)."""
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    extra = dict(lin["files"][0])
    extra["symbol"] = "DOGEUSDT"
    lin["files"].append(extra)
    _put(raw, lin)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "unexpected_series:DOGEUSDT_1d"


def test_ec_08_loader_only_series(real_like_raw, tmp_path):
    """Loader nạp series mà lineage không khai -> FAIL CLOSED, chiều ngược của case 7."""
    raw = _fresh(real_like_raw, tmp_path)
    lin = _drop(raw, "ETHUSDT_15m")
    assert (raw / "ETHUSDT_15m.parquet").exists(), "precondition: loader vẫn nạp series này"
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "missing_required_series:ETHUSDT_15m"


def test_ec_05_extra_series_on_disk(real_like_raw, tmp_path):
    """Series thừa CÓ THẬT trên đĩa: lineage tự nhất quán về hash nhưng vẫn phải FAIL.

    Đây là biến thể nguy hiểm hơn case 7 — trước S008 nó cho `(True, 'verified')` vì mọi
    checksum đều khớp.
    """
    raw = _fresh(real_like_raw, tmp_path)
    shutil.copy(raw / "ETHUSDT_1d.parquet", raw / "DOGEUSDT_1d.parquet")
    lin = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "unexpected_series:DOGEUSDT_1d"


def test_ec_18_partial_coverage_one_of_three(real_like_raw, tmp_path):
    """Chỉ 1/3 series, lineage dựng lại nên hash HOÀN TOÀN nhất quán -> vẫn phải FAIL."""
    raw = tmp_path / "partial"
    raw.mkdir()
    shutil.copy(real_like_raw / "ETHUSDT_1d.parquet", raw)
    lin = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    assert len(lin["files"]) == 1
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "missing_required_series:BTCUSDT_1d"


def test_ec_19_partial_coverage_two_of_three(real_like_raw, tmp_path):
    raw = tmp_path / "partial2"
    raw.mkdir()
    for key in ("ETHUSDT_1d", "BTCUSDT_1d"):
        shutil.copy(real_like_raw / f"{key}.parquet", raw)
    lin = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "missing_required_series:ETHUSDT_15m"


# ===== CASE 6 — trùng lặp

def test_ec_06_duplicate_series(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    lin["files"].append(dict(lin["files"][0]))
    _put(raw, lin)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason.startswith("duplicate_series:")


# ===== CASE 9,10,11 — checksum

def test_ec_09_checksum_missing(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    lin["files"][0].pop("file_hash")
    _put(raw, lin)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason.startswith("checksum_missing:")


def test_ec_10_dataset_hash_mismatch(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    lin["dataset_hash"] = "0" * 64
    _put(raw, lin)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason == "dataset_hash_mismatch"


def test_ec_11_tampered_checksum(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    lin["files"][0]["file_hash"] = "0" * 64
    _put(raw, lin)
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason.startswith("file_hash_mismatch:")


def test_ec_11b_file_removed_after_lineage(real_like_raw, tmp_path):
    raw = _fresh(real_like_raw, tmp_path)
    lin = _lineage(raw)
    (raw / "ETHUSDT_1d.parquet").unlink()
    ok, reason = official_eligibility(raw, lin)
    assert ok is False
    assert reason.startswith("missing_file:")


# ===== CASE 14,15 — lineage dị dạng / thiếu

@pytest.mark.parametrize("bad", [["x"], "chuỗi", 42, {"files": "không-phải-list"},
                                 {"files": [["không-phải-dict"]]}, {}])
def test_ec_14_malformed_lineage(real_like_raw, bad):
    ok, reason = official_eligibility(real_like_raw, bad)
    assert ok is False
    assert reason == "lineage_malformed"


def test_ec_15_missing_lineage(real_like_raw):
    ok, reason = official_eligibility(real_like_raw, None)
    assert ok is False
    assert reason == "lineage_missing"


# ===== CASE 13,16 — dev_limit luôn phi official (RULE-11)

def test_ec_13_verified_plus_dev_limit_is_not_official(real_like_raw, tmp_path):
    """Lineage đủ tư cách + `--dev-limit` -> vẫn NON-OFFICIAL.

    Khẳng định `prep.official_eligible is True` ngay trước đó là phần thiết yếu: nếu thiếu,
    test vẫn xanh trên một implementation từ chối mọi thứ, và khi đó nó không chứng minh
    được rằng chính `dev_limit` là nguyên nhân.
    """
    prep = Prepared(real_like_raw)
    assert prep.official_eligible is True, prep.official_reason
    payload = run_gate2(prep, tmp_path / "out", limit=1)
    assert payload["official"] is False


# ===== CASE 17 — CLI / ENV không ép được

def test_ec_17_no_cli_or_env_override_path():
    """Không cờ CLI, không biến môi trường, không tham số nào đi vào phép dẫn xuất."""
    import inspect

    import eth_dca_os.cli as cli_mod
    import eth_dca_os.reporting as reporting_mod

    src = inspect.getsource(cli_mod)
    for forbidden in ("--official", "--force-official", "--source", "--real-data"):
        assert forbidden not in src, f"CLI lộ cờ ép official: {forbidden}"
    assert "environ" not in src and "getenv" not in src

    assert list(inspect.signature(official_eligibility).parameters) == ["raw_dir", "lineage"]
    assert not hasattr(reporting_mod, "official_eligibility"), \
        "nơi ghi record không được nhìn thấy phép dẫn xuất"


# ===== Bất biến nền của contract

def test_required_series_is_the_single_canonical_definition(real_like_raw):
    """`load_dataset` và `official_eligibility` phải dùng CÙNG một định nghĩa canonical."""
    assert REQUIRED_SERIES == ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m")
    loaded = load_dataset(real_like_raw)
    assert set(REQUIRED_SERIES) <= set(loaded), "loader không nạp đúng tập canonical"

    import inspect

    from eth_dca_os.data import dataset as ds
    body = inspect.getsource(ds.load_dataset)
    assert "REQUIRED_SERIES" in body, "load_dataset khai lại tập series thay vì dùng hằng số"


def test_real_sources_exclude_synthetic_and_unknown():
    assert SOURCE_SYNTHETIC not in REAL_SOURCES
    assert SOURCE_UNKNOWN not in REAL_SOURCES
    assert REAL_SOURCES == frozenset({"binance_bulk_archive", "binance_rest"})
