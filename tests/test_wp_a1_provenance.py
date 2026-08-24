"""WP-A1 — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức.

Đóng F-005, F-007, F-009, F-010, F-011; giảm thiểu RSK-006, RSK-008.

Bất biến trung tâm của gói này là một CHUỖI DẪN XUẤT, không phải một danh sách trường:

    dataset lineage -> verified source -> official eligibility

Không được tồn tại đường nào (flag, biến môi trường, tham số, hay việc THIẾU thông tin)
biến dữ liệu tổng hợp hoặc dữ liệu không rõ nguồn thành `official: true` (DEC-003).

Ghi chú test-design: bản test đầu của WP-A1 PASS giả vì bọc assertion trong `if` —
`if lineage_source == "synthetic": assert ...` không bao giờ chạy khi source là `unknown`,
và `if hasattr(cfg, "created_at")` không bao giờ chạy khi field chưa tồn tại. Mọi assertion
ở đây vì thế phải là assertion CỨNG, không điều kiện.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

import eth_dca_os.cli as cli_mod
from eth_dca_os import MASTER_SEED
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.data.dataset import (
    REAL_SOURCES,
    SOURCE_BULK_ARCHIVE,
    SOURCE_SYNTHETIC,
    SOURCE_UNKNOWN,
    build_lineage,
    official_eligibility,
)
from eth_dca_os.data.synth import generate
from eth_dca_os.manifests import _cfg_row, manifest_hash
from eth_dca_os.pipeline import Prepared, run_gate1, run_gate2, run_gate3
from eth_dca_os.reporting import lockfile_path

REPO_ROOT = Path(__file__).resolve().parents[1]

PROVENANCE_FIELDS = (
    "python_version",
    "dependency_lock_hash",
    "code_commit",
    "dataset_hash",
    "strategy_config_hash",
    "execution_config_hash",
    "sensitivity_manifest_hash",
    "master_seed",
    "simulation_seed",
)


# --------------------------------------------------------------------- fixtures
# Một dataset tổng hợp và một run Gate 1 dùng chung cho cả module: run_gate1 official
# chạy 1000 mô phỏng bootstrap, dựng lại cho từng test sẽ tốn hàng phút mà không thêm
# thông tin nào — các test dưới đây đọc CÙNG một run.

@pytest.fixture(scope="module")
def synth_raw(tmp_path_factory) -> Path:
    raw = tmp_path_factory.mktemp("wp_a1_raw")
    generate(raw, start="2020-01-01", end="2023-12-31", seed=MASTER_SEED)
    return raw


@pytest.fixture(scope="module")
def gate1_official(synth_raw, tmp_path_factory):
    """Kịch bản chính xác của F-005: `ethdca synth` rồi `run` KHÔNG có `--dev-limit`."""
    out = tmp_path_factory.mktemp("wp_a1_out")
    payload = run_gate1(Prepared(synth_raw), out)
    return payload, out


def _records(out_dir: Path, run_type: str) -> list[dict]:
    lines = (Path(out_dir) / "backtest_runs.jsonl").read_text().splitlines()
    return [r for r in (json.loads(x) for x in lines) if r["run_type"] == run_type]


# ============ CHECK-A1-01 — Run record chứa đủ 8 nhóm trường provenance bắt buộc

def test_a1_01_run_record_has_all_provenance_fields(gate1_official):
    payload, _ = gate1_official
    rec = payload["run_record"]

    missing = [f for f in PROVENANCE_FIELDS if f not in rec]
    assert not missing, f"run_record thiếu trường provenance: {missing}"

    empty = [f for f in PROVENANCE_FIELDS if rec[f] is None or not str(rec[f]).strip()]
    assert not empty, f"trường provenance rỗng: {empty}"

    # Record phải tự trả lời "dữ liệu đến từ đâu" và "có phải official không"
    assert rec["data_source"] == SOURCE_SYNTHETIC
    assert rec["official"] is False

    assert rec["dependency_lock_hash"] != "no-lockfile", "lockfile không tìm thấy (F-007)"
    assert rec["code_commit"] != "unknown", "không xác định được git SHA (F-010)"


# ============ CHECK-A1-02 — sensitivity_manifest_hash được ghi cho GATE2 và GATE3

def test_a1_02_manifest_hash_gate1(gate1_official):
    payload, _ = gate1_official
    mh = payload["run_record"]["sensitivity_manifest_hash"]
    assert mh and len(mh) == 64, f"không phải SHA256 hex: {mh!r}"


def test_a1_02_manifest_hash_gate2_gate3(synth_raw, tmp_path):
    """Record GATE2/GATE3 phải mang hash TRÙNG manifest thực sự được dùng (đóng F-009).

    `limit=1` chỉ để giữ test nhanh; hash phải khớp manifest đã cắt đúng như đã chạy.
    """
    prep = Prepared(synth_raw)
    run_gate2(prep, tmp_path, limit=1)
    run_gate3(prep, tmp_path, limit=1)

    from eth_dca_os.manifests import generate_gate2_manifest, generate_gate3_manifest
    g2 = generate_gate2_manifest()
    g2_cfgs = ([g2["baseline"]] + g2["ofat"] + g2["interaction"])[:1]
    g3_cfgs = generate_gate3_manifest()["manifest"][:1]

    g2_rec = _records(tmp_path, "GATE2")[-1]
    g3_rec = _records(tmp_path, "GATE3")[-1]

    assert g2_rec["sensitivity_manifest_hash"] == manifest_hash([_cfg_row(c) for c in g2_cfgs])
    assert g3_rec["sensitivity_manifest_hash"] == manifest_hash([_cfg_row(c) for c in g3_cfgs])


# ============ CHECK-A1-03 — simulation_seed và code_commit đúng giá trị

def test_a1_03_simulation_seed_and_code_commit(gate1_official):
    payload, _ = gate1_official
    rec = payload["run_record"]

    assert isinstance(rec["simulation_seed"], int), "simulation_seed phải là số (F-010)"

    git_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    assert rec["code_commit"] == git_head, \
        f"code_commit {rec['code_commit']} != git HEAD {git_head}"


def test_a1_03_simulation_seed_is_derived_not_constant():
    """Seed phải dẫn xuất từ config, nếu không nó không chứng minh được gì (F-010)."""
    from eth_dca_os.config import deterministic_hash
    a = deterministic_hash(MASTER_SEED, BASELINE_STRATEGY.hash, GATE1_LOW_FRICTION.hash)
    b = deterministic_hash(MASTER_SEED, BASELINE_STRATEGY.hash, GATE1_LOW_FRICTION.hash)
    c = deterministic_hash(MASTER_SEED, BASELINE_STRATEGY.with_(base_pct=0.55,
                                                                opportunity_pct=0.15).hash,
                           GATE1_LOW_FRICTION.hash)
    assert a == b, "seed không deterministic"
    assert a != c, "seed không đổi theo config => không dẫn xuất từ config"
    assert a != MASTER_SEED, "simulation_seed chỉ là master_seed"


# ============ CHECK-A1-04 — created_at ở cả hai config, KHÔNG đổi hash

def test_a1_04_created_at_in_configs():
    for cfg in (BASELINE_STRATEGY, GATE1_LOW_FRICTION):
        created = getattr(cfg, "created_at", None)
        assert created, f"{type(cfg).__name__} thiếu created_at (F-011)"
        assert "T" in created and created.endswith("Z"), f"không phải ISO8601 UTC: {created}"


def test_a1_04_created_at_does_not_affect_any_hash():
    """CHECK-A1-04: thêm created_at KHÔNG được đổi hash config, key() hay hash manifest.

    Giá trị đối chiếu lấy từ commit d72fbc4 (trước khi thêm created_at) — nếu created_at
    lọt vào bất kỳ đường serialize nào, hash config sẽ đổi theo thời điểm chạy và manifest
    đóng băng hết tái lập.
    """
    assert BASELINE_STRATEGY.hash == \
        "f782f99077fe57693c1a7de0583f087464174a12f00c1a56479823af17501b7b"
    assert GATE1_LOW_FRICTION.hash == \
        "5888866fa8ce62bebd485df17247d654804d9462121ce935243636f4c55c6ec9"

    assert "created_at" not in _cfg_row(BASELINE_STRATEGY), \
        "created_at lọt vào manifest row => hash manifest phụ thuộc thời gian"

    # key() dùng khử trùng lặp manifest: hai instance cùng cấu hình phải trùng key dù
    # được tạo ở hai thời điểm khác nhau, nếu không manifest sẽ phình theo thời gian.
    from eth_dca_os.config import ExecutionConfig, StrategyConfig
    assert StrategyConfig().key() == StrategyConfig().key()
    assert ExecutionConfig().key() == ExecutionConfig().key()

    from eth_dca_os.manifests import generate_gate2_manifest, generate_gate3_manifest
    assert generate_gate2_manifest()["denominator"] == 219
    assert generate_gate3_manifest()["size"] == 114


# ============ CHECK-A1-05 — lineage phân biệt được ba nguồn dữ liệu

def test_a1_05_synth_lineage_source_is_synthetic(synth_raw):
    """Assertion CỨNG: `ethdca synth` phải ghi source='synthetic' cho TỪNG series."""
    lineage = json.loads((synth_raw / "lineage.json").read_text())

    assert lineage["source"] == SOURCE_SYNTHETIC, \
        f"lineage.source = {lineage['source']!r}, phải là {SOURCE_SYNTHETIC!r} (F-005)"
    assert lineage["files"], "lineage không có file nào"
    for entry in lineage["files"]:
        key = f"{entry['symbol']}_{entry['interval']}"
        assert entry["source"] == SOURCE_SYNTHETIC, f"{key}: source = {entry['source']!r}"


def test_a1_05_no_hardcoded_source_string_remains():
    """Chuỗi cố định 'see fetch/synth' không được còn ở bất kỳ đâu trong src/ (F-005)."""
    hits = [p for p in (REPO_ROOT / "src").rglob("*.py")
            if "see fetch/synth" in p.read_text(encoding="utf-8")]
    assert not hits, f"vẫn còn chuỗi source cố định tại: {hits}"


def test_a1_05_build_lineage_rejects_unknown_taxonomy(tmp_path, synth_raw):
    """Nguồn ngoài taxonomy phải bị từ chối ngay khi tạo, không âm thầm ghi vào lineage."""
    import shutil
    raw = tmp_path / "raw"
    shutil.copytree(synth_raw, raw)
    with pytest.raises(ValueError, match="source không hợp lệ"):
        build_lineage(raw, "binance-archive+api")


# ============ CHECK-A1-06 — Dữ liệu tổng hợp không thể tạo ra official: true

def test_a1_06_synthetic_cannot_be_official(gate1_official):
    """Kịch bản F-005: synth + run KHÔNG dev-limit. Trước WP-A1 cho official=True."""
    payload, out = gate1_official

    assert payload["official"] is False, \
        f"dữ liệu synthetic vẫn official=True (F-005); lý do={payload.get('official_reason')!r}"
    assert payload["dev_limit"] is None, "test này phải chạy ở đường official (không dev-limit)"
    assert payload["lineage"]["source"] == SOURCE_SYNTHETIC

    rec = _records(out, "GATE1")[-1]
    assert rec["official"] is False, "run record vẫn ghi official=True cho dữ liệu synthetic"


def test_a1_06_synthetic_not_official_in_gate2_gate3(synth_raw, tmp_path):
    """Cùng bất biến ở Gate 2/Gate 3 — không gate nào có đường dẫn xuất riêng."""
    prep = Prepared(synth_raw)
    assert run_gate2(prep, tmp_path, limit=1)["official"] is False
    assert run_gate3(prep, tmp_path, limit=1)["official"] is False


# ============ CHECK-A1-07 — official không giả mạo được

def test_a1_07_unknown_source_is_not_official(tmp_path, synth_raw):
    """Fail-closed: KHÔNG BIẾT nguồn cũng không phải official, ngang với synthetic."""
    import shutil
    raw = tmp_path / "raw"
    shutil.copytree(synth_raw, raw)
    lineage = build_lineage(raw, SOURCE_UNKNOWN)
    ok, reason = official_eligibility(raw, lineage)
    assert ok is False and "source_not_real" in reason, reason


def test_a1_07_missing_lineage_is_not_official(synth_raw):
    """Thiếu lineage hoàn toàn => không official (không được coi 'không có tin xấu' là tốt)."""
    assert official_eligibility(synth_raw, None)[0] is False
    assert official_eligibility(synth_raw, {})[0] is False
    assert official_eligibility(synth_raw, {"files": []})[0] is False


def test_a1_07_tampered_dataset_is_not_official(tmp_path, synth_raw):
    """Lineage khai nguồn thật nhưng checksum không khớp file trên đĩa => không official."""
    import shutil
    raw = tmp_path / "raw"
    shutil.copytree(synth_raw, raw)
    lineage = build_lineage(raw, SOURCE_BULK_ARCHIVE)
    assert official_eligibility(raw, lineage)[0] is True, "positive control phải đủ điều kiện"

    forged = json.loads(json.dumps(lineage))
    forged["files"][0]["file_hash"] = "0" * 64
    ok, reason = official_eligibility(raw, forged)
    assert ok is False and reason.startswith("file_hash_mismatch"), reason

    swapped = json.loads(json.dumps(lineage))
    swapped["dataset_hash"] = "0" * 64
    ok, reason = official_eligibility(raw, swapped)
    assert ok is False and reason == "dataset_hash_mismatch", reason

    missing = json.loads(json.dumps(lineage))
    (raw / f"{missing['files'][0]['symbol']}_{missing['files'][0]['interval']}.parquet").unlink()
    ok, reason = official_eligibility(raw, missing)
    assert ok is False and reason.startswith("missing_file"), reason


def test_a1_07_dev_limit_still_forces_non_official(tmp_path, synth_raw):
    """Ngay cả lineage đủ tư cách, `--dev-limit` vẫn phải cho run non-official."""
    import shutil
    raw = tmp_path / "raw"
    shutil.copytree(synth_raw, raw)
    build_lineage(raw, SOURCE_BULK_ARCHIVE)          # positive-control lineage
    prep = Prepared(raw)
    assert prep.official_eligible is True, prep.official_reason
    assert run_gate2(prep, tmp_path, limit=1)["official"] is False


def test_a1_07_no_cli_or_env_surface_can_force_official():
    """Không flag CLI, biến môi trường, hay tham số nào đi vào phép dẫn xuất official."""
    parser_src = inspect.getsource(cli_mod)
    for forbidden in ("--official", "--force-official", "--source", "--real-data"):
        assert forbidden not in parser_src, f"CLI lộ flag ép official: {forbidden}"
    assert "environ" not in parser_src and "getenv" not in parser_src, \
        "CLI đọc biến môi trường — có thể thành đường ép official"

    params = list(inspect.signature(official_eligibility).parameters)
    assert params == ["raw_dir", "lineage"], \
        f"official_eligibility nhận thêm tham số ngoài lineage: {params}"

    # Nơi GHI record không được có khả năng tự quyết định official: `reporting` thậm chí
    # không nhìn thấy phép dẫn xuất, nên chỉ ghi lại giá trị pipeline đã tính.
    import eth_dca_os.reporting as reporting_mod
    assert not hasattr(reporting_mod, "official_eligibility"), \
        "reporting import phép dẫn xuất official — record có thể tự nhận official"
    assert "official" in inspect.signature(reporting_mod.save_run).parameters


def test_a1_07_real_sources_are_exactly_the_binance_ones():
    """Chỉ dữ liệu Binance thật đủ tư cách; synthetic/unknown tuyệt đối không (DEC-003)."""
    assert SOURCE_SYNTHETIC not in REAL_SOURCES
    assert SOURCE_UNKNOWN not in REAL_SOURCES
    assert REAL_SOURCES == frozenset({"binance_bulk_archive", "binance_rest"})


# ============ CHECK-A1-08 — Dependency được ghim, hash lockfile khớp record

def test_a1_08_lockfile_and_hash(gate1_official):
    lock = lockfile_path()
    assert lock is not None and lock.exists(), "không tìm thấy lockfile ghim dependency (F-007)"

    body = lock.read_text(encoding="utf-8")
    pinned = [ln.strip() for ln in body.splitlines()
              if ln.strip() and not ln.strip().startswith("#")]
    assert pinned, "lockfile rỗng"
    for line in pinned:
        assert "==" in line, f"dependency không ghim phiên bản chính xác: {line!r}"

    expected = hashlib.sha256(lock.read_bytes()).hexdigest()
    assert gate1_official[0]["run_record"]["dependency_lock_hash"] == expected


def test_a1_08_lockfile_matches_installed_environment():
    """Lockfile phải MÔ TẢ ĐÚNG môi trường đã chạy, không chỉ có dạng `pkg==x.y.z`.

    Bản lockfile đầu của WP-A1 được viết tay và 9/15 dòng sai phiên bản thật (kể cả hai gói
    không hề được cài). Một `dependency_lock_hash` như vậy "chứng minh" một môi trường chưa
    từng tồn tại — đúng thất bại RSK-006 mà gói này phải chặn. Test này khép đường đó lại.
    """
    import importlib.metadata as md

    lock = lockfile_path()
    assert lock is not None
    pinned = {}
    for line in lock.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            name, version = line.split("==", 1)
            pinned[name.lower().replace("_", "-")] = version
    assert pinned, "lockfile không ghim gói nào"

    wrong, absent = [], []
    for name, version in sorted(pinned.items()):
        try:
            installed = md.version(name)
        except md.PackageNotFoundError:
            absent.append(name)
            continue
        if installed != version:
            wrong.append(f"{name}: lock={version} nhưng đã cài={installed}")

    assert not absent, f"lockfile ghim gói KHÔNG được cài: {absent}"
    assert not wrong, "lockfile lệch môi trường thật:\n  " + "\n  ".join(wrong)


# ============ CHECK-A1-09 — Tái lập run cho kết quả trùng khớp ở mức metric

def test_a1_09_reproducibility_same_seed_same_metrics(synth_raw, tmp_path):
    """BT §20 'bit-for-bit ở mức metric': cùng dataset/config/seed => cùng số liệu."""
    a = run_gate1(Prepared(synth_raw), tmp_path / "r1")
    b = run_gate1(Prepared(synth_raw), tmp_path / "r2")

    assert a["window_metrics"]["ae_by_window"] == b["window_metrics"]["ae_by_window"]
    assert a["window_metrics"]["primary_median"] == b["window_metrics"]["primary_median"]
    assert a["bootstrap_descriptive"] == b["bootstrap_descriptive"], "bootstrap không tái lập"
    assert a["oos"] == b["oos"]

    ra, rb = a["run_record"], b["run_record"]
    for f in ("dataset_hash", "strategy_config_hash", "execution_config_hash",
              "sensitivity_manifest_hash", "simulation_seed", "code_commit",
              "dependency_lock_hash", "python_version", "data_source"):
        assert ra[f] == rb[f], f"{f} không tái lập: {ra[f]!r} != {rb[f]!r}"


# ============ CHECK-A1-10 — python_version khớp interpreter đang chạy

def test_a1_10_python_version_matches_interpreter(gate1_official):
    expected = (f"{sys.version_info.major}.{sys.version_info.minor}"
                f".{sys.version_info.micro}")
    assert gate1_official[0]["run_record"]["python_version"] == expected
