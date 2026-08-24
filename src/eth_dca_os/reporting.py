"""Reporting & reproducibility records — Backtest §16, §20; Data Model §12."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

from . import BACKTEST_SPEC_VERSION, MASTER_SEED, STRATEGY_VERSION


def _jsonable(x):
    import numpy as np
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, float) and x != x:
        return None
    return x


def _get_python_version() -> str:
    """Python version để tái lập môi trường (WP-A1/A1.4)."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


#: Gốc repo suy ra từ vị trí CHÍNH module này (src/eth_dca_os/reporting.py -> parents[2]).
#: Không hard-code đường dẫn tuyệt đối: official run bắt buộc chạy trên máy có mạng Binance
#: (DEC-003/BLK-001), nên một đường dẫn cứng sẽ âm thầm trả "unknown" đúng lần chạy quan
#: trọng nhất. Ready Gate cũng cấm để lộ đường dẫn tuyệt đối của máy chủ dự án.
_REPO_ROOT = Path(__file__).resolve().parents[2]

LOCKFILE_NAMES = ("pyproject.lock", "poetry.lock", "requirements.lock")


def _get_code_commit() -> str:
    """Git SHA để tái lập code (WP-A1/A1.4). Fail-closed: 'unknown' khi không xác định được."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def lockfile_path() -> Path | None:
    """Lockfile đang ghim dependency, hoặc None nếu chưa có (WP-A1/A1.6)."""
    for name in LOCKFILE_NAMES:
        candidate = _REPO_ROOT / name
        if candidate.exists():
            return candidate
    return None


def _get_dependency_lock_hash() -> str:
    """Hash của lockfile để tái lập dependency (WP-A1/A1.6)."""
    path = lockfile_path()
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else "no-lockfile"


def save_run(out_dir: str | Path, run_type: str, payload: dict, *,
             strategy_config_hash: str, execution_config_hash: str,
             dataset_hash: str, manifest_hash: str | None = None,
             start_date=None, end_date=None, verdict=None,
             simulation_seed: int | None = None,
             data_source: str | None = None, official: bool = False) -> dict:
    """Ghi backtest_runs record + metrics JSON (Data Model §12, Backtest §20).

    WP-A1: Thêm trường provenance để tái lập được run (A1.1–A1.6):
    - python_version, code_commit, dependency_lock_hash, simulation_seed

    `data_source` và `official` được TÍNH bởi pipeline từ lineage đã verify checksum
    (`data.dataset.official_eligibility`) rồi truyền xuống đây để ghi. `save_run` chỉ ghi
    lại, không tự suy luận và cũng không nhận giá trị từ CLI/env (WP-A1/A1.2, CHECK-A1-07).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = f"{run_type.lower()}_{uuid.uuid4().hex[:12]}"
    metrics_path = out / f"{run_id}_metrics.json"
    metrics_path.write_text(json.dumps(_jsonable(payload), indent=1, ensure_ascii=False))
    record = {
        "run_id": run_id,
        "strategy_version": STRATEGY_VERSION,
        "backtest_spec_version": BACKTEST_SPEC_VERSION,
        "strategy_config_hash": strategy_config_hash,
        "execution_config_hash": execution_config_hash,
        "sensitivity_manifest_hash": manifest_hash,
        "dataset_hash": dataset_hash,
        "start_date": str(start_date), "end_date": str(end_date),
        "master_seed": MASTER_SEED,
        "run_type": run_type,
        "metrics_path": str(metrics_path),
        "verdict": verdict,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # WP-A1 provenance fields (A1.4–A1.6)
        "python_version": _get_python_version(),
        "code_commit": _get_code_commit(),
        "dependency_lock_hash": _get_dependency_lock_hash(),
        "simulation_seed": simulation_seed if simulation_seed is not None else MASTER_SEED,
        # WP-A1/A1.1–A1.2: record tự trả lời "dữ liệu đến từ đâu" và "có official không"
        "data_source": data_source,
        "official": bool(official),
    }
    runs_file = out / "backtest_runs.jsonl"
    with open(runs_file, "a") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def write_report(out_dir: str | Path, results: dict, *, dataset_hash: str) -> Path:
    """Ghi results/report.json — payload đầy đủ cho viewer web và phân tích ngoài.

    Khác pipeline_state.json ở chỗ KHÔNG rút gọn list: state file chỉ để CLI đọc lại
    nhanh, còn file này giữ nguyên số liệu (reasons, per-window AE, failure signals...).
    Các khóa nội bộ bắt đầu bằng "_" và bảng per_config nặng bị loại.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "ethdca.report/1",
        "strategy_version": STRATEGY_VERSION,
        "backtest_spec_version": BACKTEST_SPEC_VERSION,
        "dataset_hash": dataset_hash,
        "master_seed": MASTER_SEED,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    for key in ("gate1", "gate2", "gate3", "controls", "verdict"):
        if key not in results:
            continue
        section = {k: v for k, v in results[key].items()
                   if not k.startswith("_") and k not in ("per_config", "run_record")}
        if key == "gate1":
            section["window_metrics"] = {k: v for k, v in section["window_metrics"].items()
                                         if k != "windows"}
        payload[key] = section
    path = out / "report.json"
    path.write_text(json.dumps(_jsonable(payload), indent=1, ensure_ascii=False))
    return path


def print_gate1_report(g1_payload: dict) -> str:
    lines = ["=== GATE 1 — structural value ==="]
    wm = g1_payload["window_metrics"]
    lines.append(f"{'Window':<6} {'AE %':>8}")
    for k, v in wm["ae_by_window"].items():
        lines.append(f"{k:<6} {v:>8.2f}")
    for off, v in wm["anchor_set_medians"].items():
        lines.append(f"AnchorSetMedian +{off}M: {v:.2f}")
    lines.append(f"PrimaryMedian: {wm['primary_median']:.2f}")
    lines.append(f"PooledMedian (DESCRIPTIVE): {wm['pooled_median_descriptive']:.2f}")
    g = g1_payload["gate1"]
    lines.append(f"Gate 1: {'PASS' if g['pass'] else 'FAIL'}"
                 f"{' (STRONG)' if g.get('strong') else ''}")
    o = g1_payload["oos"]
    flag = " [SHORT_OOS]" if o.get("short_oos") else ""
    lines.append(f"OOS: AE {o['ae']:.2f} | {o['oos_months']} tháng{flag} | "
                 f"{'PASS' if o['ae'] >= 100 else 'FAIL'}")
    return "\n".join(lines)
