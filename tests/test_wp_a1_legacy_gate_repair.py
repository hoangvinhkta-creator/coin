"""WP-A1 — repair cycle cuối (OWNER_EXTENSION `DEC-027`): đóng hai hạng mục
`LEGACY_GATE_DISPOSITION_REQUIRED` cần production code.

- **B.1 / `F-E2A1-03`** — provenance suy biến IM LẶNG ngoài editable install: run record ghi
  `code_commit='unknown'` và `dependency_lock_hash='no-lockfile'` mà không ai được báo. Các
  con số của run vẫn đúng; thứ mất đi là khả năng chứng minh *về sau* mã nào sinh ra chúng.
  Master Index §6 cấm chạy lại official run, nên nếu `T-06` chạy trong tình trạng này thì
  provenance mất **VĨNH VIỄN** — đó là lý do nó không được đẩy xuống hardening im lặng.

- **B.2 / `F-E2A1R3-03`** — contract case 13 (PRE-S008, FROZEN 2026-08-25) chưa được thi
  hành: `dev_limit != None` phải cho `official=False` kèm `official_reason='dev_limit_set'`
  tại `pipeline.run_gate1/2/3`. Hôm nay cờ `official` đúng nhưng lý do bị `'verified'` che
  mất nguyên nhân, và mã `dev_limit_set` không tồn tại trong `src/`.

Nguyên tắc của bộ test này: mỗi ca phải **thất bại trước khi sửa**. Ca B.1 dựng lại đúng
điều kiện mà reviewer E2 đã dùng (môi trường không phân giải được provenance) bằng cách
patch chính hai hàm phân giải, thay vì mô tả bằng lời.
"""
from __future__ import annotations

import json
import shutil

import pytest

import eth_dca_os.reporting as reporting_mod
from eth_dca_os.data.dataset import SOURCE_BULK_ARCHIVE, build_lineage
from eth_dca_os.data.synth import generate
from eth_dca_os.pipeline import Prepared, run_gate1, run_gate2, run_gate3
from eth_dca_os.reporting import save_run


def _unresolved_error():
    """Lấy lớp lỗi provenance ở thời điểm CHẠY, không phải thời điểm import.

    Trước khi B.1 được sửa, lớp này chưa tồn tại — nhập ở đầu module sẽ làm cả file lỗi
    collection và che mất kết quả đỏ của B.2. Ca đỏ đúng nghĩa là "gọi `save_run` không nổ",
    không phải "không import được".
    """
    return getattr(reporting_mod, "ProvenanceUnresolvedError", None) or RuntimeError


@pytest.fixture(scope="module")
def synth_raw(tmp_path_factory):
    raw = tmp_path_factory.mktemp("wp_a1_repair") / "raw"
    generate(raw, start="2018-01-01", end="2020-06-30")
    return raw


@pytest.fixture
def eligible_raw(tmp_path, synth_raw):
    """Dataset ĐỦ TƯ CÁCH official (positive-control lineage) — điều kiện của case 13.

    Case 13 nói "như (12) nhưng `dev_limit != None`", mà (12) là ca dataset hợp lệ. Nếu
    dataset tự nó đã không đủ tư cách thì đang kiểm một ca khác, không phải case 13.
    """
    raw = tmp_path / "raw"
    shutil.copytree(synth_raw, raw)
    build_lineage(raw, SOURCE_BULK_ARCHIVE)
    return raw


def _save_kwargs(**over):
    kw = dict(strategy_config_hash="s", execution_config_hash="e", dataset_hash="d",
              data_source=SOURCE_BULK_ARCHIVE, official=True)
    kw.update(over)
    return kw


# ============================================================ B.1 / F-E2A1-03


def test_a1r_b1_official_run_refuses_unresolved_code_commit(tmp_path, monkeypatch):
    """Không phân giải được git SHA + run được ghi official -> PHẢI nổ, không ghi im lặng.

    Đây là ca của reviewer E2: môi trường clean/non-editable. Trước khi sửa, `save_run` ghi
    `code_commit='unknown'` rồi trả về bình thường.
    """
    monkeypatch.setattr(reporting_mod, "_get_code_commit", lambda: "unknown")
    with pytest.raises(_unresolved_error()) as exc:
        save_run(tmp_path, "GATE1", {"x": 1}, **_save_kwargs())
    assert "code_commit" in str(exc.value)


def test_a1r_b1_official_run_refuses_missing_lockfile(tmp_path, monkeypatch):
    """Không tìm được lockfile + run official -> PHẢI nổ."""
    monkeypatch.setattr(reporting_mod, "lockfile_path", lambda: None)
    with pytest.raises(_unresolved_error()) as exc:
        save_run(tmp_path, "GATE1", {"x": 1}, **_save_kwargs())
    assert "dependency_lock_hash" in str(exc.value)


def test_a1r_b1_nothing_is_written_when_provenance_unresolved(tmp_path, monkeypatch):
    """Quan trọng nhất: KHÔNG artifact nào được ghi ra khi từ chối.

    Nếu record hoặc metrics file đã kịp ghi rồi mới nổ thì một official run thiếu
    provenance vẫn nằm lại trên đĩa — đúng thứ Master Index §6 làm cho không sửa được.
    """
    monkeypatch.setattr(reporting_mod, "_get_code_commit", lambda: "unknown")
    out = tmp_path / "results"
    with pytest.raises(_unresolved_error()):
        save_run(out, "GATE1", {"x": 1}, **_save_kwargs())
    assert not (out / "backtest_runs.jsonl").exists(), "record đã bị ghi trước khi từ chối"
    assert not list(out.glob("*_metrics.json")), "metrics đã bị ghi trước khi từ chối"


def test_a1r_b1_non_official_run_still_records_degraded_state(tmp_path, monkeypatch):
    """Run KHÔNG official vẫn chạy được trong môi trường thiếu provenance — nhưng trạng
    thái suy biến phải HIỆN RÕ trên record, không bị che.

    Đây là ranh giới của bản sửa: fail-loud áp cho đường official/provenance-sensitive,
    không biến mọi run dev trong môi trường không có git thành lỗi cứng.
    """
    monkeypatch.setattr(reporting_mod, "_get_code_commit", lambda: "unknown")
    rec = save_run(tmp_path, "GATE1", {"x": 1}, **_save_kwargs(official=False))
    assert rec["official"] is False
    assert rec["code_commit"] == "unknown"
    assert rec["provenance_resolved"] is False
    assert "code_commit" in rec["provenance_unresolved"]


def test_a1r_b1_official_run_with_resolvable_provenance_still_works(tmp_path):
    """Đối chứng dương: môi trường bình thường thì official run vẫn ghi được như cũ.

    Không có ca này thì một bản sửa "luôn luôn nổ" cũng làm ba test trên xanh.
    """
    rec = save_run(tmp_path, "GATE1", {"x": 1}, **_save_kwargs())
    assert rec["official"] is True
    assert rec["code_commit"] != "unknown"
    assert rec["dependency_lock_hash"] != "no-lockfile"
    assert rec["provenance_resolved"] is True
    assert rec["provenance_unresolved"] == []
    assert (tmp_path / "backtest_runs.jsonl").exists()


# ======================================================= B.2 / F-E2A1R3-03 (case 13)


def test_a1r_b2_gate1_dev_limit_sets_canonical_reason(tmp_path, eligible_raw):
    """Contract case 13 tại `run_gate1`: official=False kèm reason `dev_limit_set`."""
    prep = Prepared(eligible_raw)
    assert prep.official_eligible is True, prep.official_reason   # tiền đề của case 13
    payload = run_gate1(prep, tmp_path, dev_limit=5)
    assert payload["official"] is False
    assert payload["official_reason"] == "dev_limit_set", (
        "nguyên nhân `dev_limit` bị che mất — đúng nội dung F-E2A1R3-03")


def test_a1r_b2_gate2_dev_limit_sets_canonical_reason(tmp_path, eligible_raw):
    prep = Prepared(eligible_raw)
    assert prep.official_eligible is True, prep.official_reason
    payload = run_gate2(prep, tmp_path, limit=2)
    assert payload["official"] is False
    assert payload["official_reason"] == "dev_limit_set"


def test_a1r_b2_gate3_dev_limit_sets_canonical_reason(tmp_path, eligible_raw):
    prep = Prepared(eligible_raw)
    assert prep.official_eligible is True, prep.official_reason
    payload = run_gate3(prep, tmp_path, limit=2)
    assert payload["official"] is False
    assert payload["official_reason"] == "dev_limit_set"


def test_a1r_b2_reason_written_into_run_record(tmp_path, eligible_raw):
    """Lý do phải đi tới ARTIFACT, không chỉ nằm trong payload trong bộ nhớ.

    `official_reason` của record là thứ người đọc về sau nhìn thấy; nếu nó vẫn là
    `'verified'` thì finding chưa đóng dù payload đã đúng.
    """
    prep = Prepared(eligible_raw)
    run_gate1(prep, tmp_path, dev_limit=5)
    metrics = json.loads(next(tmp_path.glob("gate1_*_metrics.json")).read_text())
    assert metrics["official"] is False
    assert metrics["official_reason"] == "dev_limit_set"


def test_a1r_b2_no_dev_limit_keeps_dataset_reason(tmp_path, eligible_raw):
    """Đối chứng: KHÔNG có dev_limit thì lý do vẫn là lý do của dataset (`verified`).

    Ca này chặn một bản sửa lười gán cứng `dev_limit_set` cho mọi trường hợp.
    """
    prep = Prepared(eligible_raw)
    payload = run_gate1(prep, tmp_path)
    assert payload["official"] is True
    assert payload["official_reason"] == "verified"


def test_a1r_b2_ineligible_dataset_keeps_its_own_reason(tmp_path, synth_raw):
    """Dataset KHÔNG đủ tư cách + dev_limit: giữ lý do GỐC của dataset.

    Hợp đồng chỉ định nghĩa case 13 trên nền dataset hợp lệ. Với dataset đã không hợp lệ,
    nguyên nhân gốc (nguồn synthetic) quan trọng hơn và không được `dev_limit_set` che —
    nếu không thì bản sửa này lặp lại đúng lỗi mà nó đang đi đóng, chỉ đổi chiều.
    """
    prep = Prepared(synth_raw)
    assert prep.official_eligible is False
    payload = run_gate1(prep, tmp_path, dev_limit=5)
    assert payload["official"] is False
    assert payload["official_reason"].startswith("source_not_real")


def test_a1r_b2_dev_limit_set_is_not_a_valid_source_or_eligibility_code(tmp_path,
                                                                       eligible_raw):
    """`dev_limit_set` là lý do của TẦNG PIPELINE, không phải của `official_eligibility`.

    Hợp đồng ghi enforcement point là `pipeline.run_gate1/2/3`. Nếu ai đó cài nó vào
    `official_eligibility` thì dataset sẽ bị coi là không hợp lệ ngay cả khi không chạy
    dev — sai tầng, và ca này bắt được.
    """
    from eth_dca_os.data.dataset import official_eligibility
    ok, reason = official_eligibility(eligible_raw, Prepared(eligible_raw).lineage)
    assert ok is True and reason == "verified"
