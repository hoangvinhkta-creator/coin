"""WP-B1 — lát cắt pre-T06 theo `DEC-026`: đóng `F-S015-01` và phần tương ứng của `CHECK-B1-01`.

Hai ngữ nghĩa bị hỏng tại CÙNG MỘT dòng `any_true = any(v is True ...)` trong
`failure_signals.py`, và `DEC-026` (3) cấm chỉ sửa một vế:

* (A) `numpy.bool_(True) is True` cho **False** — một Failure Signal TRUE mang kiểu numpy
  (`FS-11` từ `oos_ae` là ca thật của pipeline) vô hình với quy tắc chặn BT §17, và cũng
  **thiếu tên** trong câu lý do vì `verdict.py:29` dựng danh sách bằng cùng phép `is True`.
* (B) `None` (UNKNOWN) không kích hoạt cap — verdict `BUILD` phát ra trên bằng chứng chưa đủ.
  BT §17 liệt kê FS-01…FS-12 mà không đánh dấu mục nào tuỳ chọn, nên cả 12 là REQUIRED
  (`CHECK-B1-01`): test lặp cho **mỗi** vị trí, không chỉ một vị trí thuận tiện.

Ràng buộc của lát cắt: `verdict.py` KHÔNG đổi (không có authority mới). Vì vậy mọi test đi
qua `decide_verdict` thật, và điểm sửa duy nhất là nơi dựng dict signal trong
`failure_signals.py`. Bộ inputs "sạch" dùng lại đúng con số của
`tests/test_gates_verdict.py::test_verdict_mapping` để ca đối chứng (12/12 FALSE, 0 UNKNOWN
→ `BUILD`) không bị lát cắt làm hẹp đi.
"""
from __future__ import annotations

import subprocess

import numpy as np
import pytest

from eth_dca_os.failure_signals import evaluate_failure_signals
from eth_dca_os.verdict import decide_verdict

# SHA ngay TRƯỚC lát cắt DEC-026 (HEAD khi mở lát cắt; `src/` y hệt WP-A5 DONE `d4586b8`).
# `failure_signals.py` tại đó là bản mang khiếm khuyết F-S015-01 — dùng làm đối chứng
# "chỉ blocking semantics đổi" ở cuối file.
PRE_SLICE_SHA = "28b0255"

ALL_FS = [f"FS-{i:02d}" for i in range(1, 13)]
GOOD_WINDOWS = {"W1": 104.0, "W2": 103.0, "W3": 105.0, "W4": 102.0, "W5": 106.0,
                "W6": 103.0, "W7": 104.0, "W8": 102.0, "W9": 103.0}
GATES_ALL_PASS = ({"pass": True}, {"pass": True}, {"pass": True}, {"pass": True})


def _clear_inputs() -> dict:
    """Đủ input cho 12 signal, tất cả FALSE, không UNKNOWN (cùng số với test_verdict_mapping)."""
    return dict(gate1_windows=dict(GOOD_WINDOWS), oos_ae=101.0, shortfall_pp=1.0,
                gate2_oos_pass_share=0.8, vif_any_severe=False, corr_high_redundancy=False,
                score_bimodal=False, adjacent_config_flip=False, avg_cash_ratio=0.1,
                gate1_primary_ae=104.0, v2_eth=10.0, random_timing_p95=9.0,
                random_anchor_p95=9.5, opportunity_cap_hit_share=0.1,
                concentration={"ae_ex_month": 101.0, "ae_ex_quarter": 100.5},
                regime_advantage_share=0.4)


def _run(inputs: dict, gates=GATES_ALL_PASS):
    fs = evaluate_failure_signals(**inputs)
    return fs, decide_verdict(*gates, fs)


# ------------------------------------------------------------- ca đối chứng (không được hẹp đi)


def test_b1_01_control_all_false_all_known_is_build():
    """12/12 FALSE và 0 UNKNOWN thì `BUILD` vẫn phải ra — lát cắt không được chặn quá tay."""
    fs, v = _run(_clear_inputs())
    assert [k for k, x in fs["signals"].items() if x is not False] == []
    assert fs["unknown"] == [] and fs["any_true"] is False
    assert v["verdict"] == "BUILD" and v["can_proceed_to_app"] is True


# ---------------------------------------------------------------- (A) numpy TRUE không vô hình

# Với mỗi signal: override input bằng giá trị numpy sao cho signal đó TRUE về mặt logic.
NUMPY_TRUE_OVERRIDES = {
    "FS-01": dict(gate1_windows={w: np.float64(99.0) for w in GOOD_WINDOWS}),
    "FS-02": dict(opportunity_cap_hit_share=np.float64(0.9)),
    "FS-03": dict(concentration={"ae_ex_month": np.float64(95.0),
                                 "ae_ex_quarter": np.float64(101.0)}),
    "FS-04": dict(vif_any_severe=np.bool_(True)),
    "FS-05": dict(score_bimodal=np.bool_(True)),
    "FS-06": dict(adjacent_config_flip=np.bool_(True)),
    "FS-07": dict(avg_cash_ratio=np.float64(0.5), gate1_primary_ae=np.float64(101.0)),
    "FS-08": dict(v2_eth=np.float64(8.0), random_timing_p95=np.float64(9.0)),
    "FS-09": dict(shortfall_pp=np.float64(4.0)),
    "FS-10": dict(gate2_oos_pass_share=np.float64(0.2)),
    "FS-11": dict(oos_ae=np.float64(99.0)),   # ca THẬT của pipeline (F-S015-01)
    "FS-12": dict(regime_advantage_share=np.float64(0.95)),
}


@pytest.mark.parametrize("key", ALL_FS)
def test_b1_01_numpy_typed_true_signal_caps_build_and_is_named(key):
    """Đúng một signal TRUE, mang kiểu numpy → cap phải bật VÀ tên signal phải có trong lý do."""
    fs, v = _run({**_clear_inputs(), **NUMPY_TRUE_OVERRIDES[key]})
    sig = fs["signals"][key]
    assert sig, f"{key} phải TRUE về mặt logic — kiểm lại override"
    assert type(sig) is bool, f"{key} là {type(sig).__name__}, không phải bool thuần Python"
    assert sig is True
    assert fs["unknown"] == []
    assert fs["any_true"] is True, f"{key} TRUE nhưng cờ chặn không thấy (F-S015-01)"
    assert v["verdict"] == "BUILD_WITH_MODIFICATIONS"
    assert v["can_proceed_to_app"] is False
    # verdict.py:29 dựng danh sách tên bằng `x is True` — chuẩn hoá tại nguồn đóng cả chỗ này
    assert any(key in r for r in v["reasons"]), f"{key} thiếu tên trong lý do: {v['reasons']}"


def test_b1_01_numpy_typed_false_signals_stay_false_and_plain_bool():
    """Toàn bộ input numpy nhưng đều FALSE → 12 bool thuần Python, đều False, verdict `BUILD`.

    Chứng minh chuẩn hoá kiểu KHÔNG lật FALSE thành TRUE và không tạo UNKNOWN giả.
    """
    inputs = dict(gate1_windows={w: np.float64(x) for w, x in GOOD_WINDOWS.items()},
                  oos_ae=np.float64(101.0), shortfall_pp=np.float64(1.0),
                  gate2_oos_pass_share=np.float64(0.8), vif_any_severe=np.bool_(False),
                  corr_high_redundancy=np.bool_(False), score_bimodal=np.bool_(False),
                  adjacent_config_flip=np.bool_(False), avg_cash_ratio=np.float64(0.1),
                  gate1_primary_ae=np.float64(104.0), v2_eth=np.float64(10.0),
                  random_timing_p95=np.float64(9.0), random_anchor_p95=np.float64(9.5),
                  opportunity_cap_hit_share=np.float64(0.1),
                  concentration={"ae_ex_month": np.float64(101.0),
                                 "ae_ex_quarter": np.float64(100.5)},
                  regime_advantage_share=np.float64(0.4))
    fs, v = _run(inputs)
    for k, x in fs["signals"].items():
        assert type(x) is bool and x is False, f"{k}: {x!r} ({type(x).__name__})"
    assert fs["unknown"] == [] and fs["any_true"] is False
    assert v["verdict"] == "BUILD"


# ------------------------------------------------------ (B) UNKNOWN fail-closed, mỗi vị trí

# Với mỗi signal: xoá đúng input cần thiết để CHỈ signal đó thành None.
UNKNOWN_OVERRIDES = {
    "FS-01": dict(gate1_windows=None),
    "FS-02": dict(opportunity_cap_hit_share=None),
    "FS-03": dict(concentration=None),
    "FS-04": dict(vif_any_severe=None, corr_high_redundancy=None),
    "FS-05": dict(score_bimodal=None),
    "FS-06": dict(adjacent_config_flip=None),
    "FS-07": dict(avg_cash_ratio=None),
    "FS-08": dict(v2_eth=None),
    "FS-09": dict(shortfall_pp=None),
    "FS-10": dict(gate2_oos_pass_share=None),
    "FS-11": dict(oos_ae=None),
    "FS-12": dict(regime_advantage_share=None),
}


@pytest.mark.parametrize("key", ALL_FS)
def test_b1_01_exactly_one_unknown_signal_blocks_build(key):
    """CHECK-B1-01, chữ nguyên văn: đúng một signal `None` → verdict KHÔNG phải `BUILD`,
    `can_proceed_to_app` là `false`. Lặp cho mỗi vị trí trong 12."""
    fs, v = _run({**_clear_inputs(), **UNKNOWN_OVERRIDES[key]})
    assert fs["signals"][key] is None
    assert fs["unknown"] == [key], "override làm hơn một signal UNKNOWN — ca kiểm mất tính cô lập"
    assert all(fs["signals"][k] is False for k in ALL_FS if k != key)
    assert fs["any_true"] is True, f"{key} UNKNOWN nhưng cap không bật — BUILD sẽ lọt"
    assert v["verdict"] != "BUILD"
    assert v["can_proceed_to_app"] is False
    assert any(key in r and "chưa đánh giá" in r for r in v["reasons"]), v["reasons"]


def test_b1_01_all_twelve_unknown_blocks_build():
    """Không input nào (ca trước WP-A2/WP-A5 từng gặp) → cap bật, không `BUILD`."""
    fs, v = _run({})
    assert fs["unknown"] == ALL_FS and fs["any_true"] is True
    assert v["verdict"] != "BUILD" and v["can_proceed_to_app"] is False


# ------------------------------------------------ nguyên nhân cap ở dạng máy đọc được


def test_b1_01_cap_cause_is_machine_readable():
    """`verdict.py` (không đổi) chỉ in tên các signal `is True`; khi cap bật vì UNKNOWN câu
    lý do đó rỗng. Nguồn sự thật máy đọc được phải nằm ngay trong output của
    `failure_signals.py`: `true` = danh sách TRUE, `cap_cause` = vì sao cap bật."""
    fs, _ = _run(_clear_inputs())
    assert fs["true"] == [] and fs["cap_cause"] is None
    fs, _ = _run({**_clear_inputs(), **NUMPY_TRUE_OVERRIDES["FS-11"]})
    assert fs["true"] == ["FS-11"] and fs["cap_cause"] == "TRUE"
    fs, _ = _run({**_clear_inputs(), **UNKNOWN_OVERRIDES["FS-05"]})
    assert fs["true"] == [] and fs["unknown"] == ["FS-05"] and fs["cap_cause"] == "UNKNOWN"
    fs, _ = _run({**_clear_inputs(), **NUMPY_TRUE_OVERRIDES["FS-11"], **UNKNOWN_OVERRIDES["FS-05"]})
    assert fs["true"] == ["FS-11"] and fs["unknown"] == ["FS-05"]
    assert fs["cap_cause"] == "TRUE_AND_UNKNOWN"


# --------------------------------------------- chỉ nhánh cap đổi, ánh xạ gate-fail giữ nguyên


@pytest.mark.parametrize("gates,expected", [
    (({"pass": False}, {"pass": True}, {"pass": True}, {"pass": True}), "DO_NOT_BUILD"),
    (({"pass": True}, {"pass": False}, {"pass": True}, {"pass": True}), "DO_NOT_BUILD"),
    (({"pass": True}, {"pass": True}, {"pass": False}, {"pass": True}), "INCONCLUSIVE"),
    (({"pass": True}, {"pass": True}, {"pass": True}, {"pass": False}), "INCONCLUSIVE"),
])
def test_b1_01_gate_fail_mapping_unchanged_regardless_of_cap(gates, expected):
    """Khi một gate FAIL, verdict đi nhánh gate-fail — cap (dù bật vì TRUE hay UNKNOWN)
    không được đổi kết luận đó. Đây là ranh giới của lát cắt."""
    for inputs in (_clear_inputs(),
                   {**_clear_inputs(), **UNKNOWN_OVERRIDES["FS-11"]},
                   {**_clear_inputs(), **NUMPY_TRUE_OVERRIDES["FS-11"]}):
        _, v = _run(inputs, gates)
        assert v["verdict"] == expected and v["can_proceed_to_app"] is False


def _load_pre_slice_failure_signals():
    import types
    src = subprocess.run(["git", "show", f"{PRE_SLICE_SHA}:src/eth_dca_os/failure_signals.py"],
                         capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType("eth_dca_os._failure_signals_pre_b1")
    exec(compile(src, "failure_signals_pre_b1.py", "exec"), mod.__dict__)
    return mod


def test_b1_01_only_blocking_semantics_changed_vs_pre_slice():
    """So với bản TRƯỚC lát cắt (nạp từ git): GIÁ TRỊ logic của 12 signal và danh sách
    UNKNOWN trùng khớp trên mọi vector input; khác biệt duy nhất được phép là `any_true`
    trong đúng hai ca F-S015-01 (TRUE mang kiểu numpy) và CHECK-B1-01 (có UNKNOWN)."""
    before = _load_pre_slice_failure_signals()
    vectors = [_clear_inputs(), {}]
    vectors += [{**_clear_inputs(), **o} for o in NUMPY_TRUE_OVERRIDES.values()]
    vectors += [{**_clear_inputs(), **o} for o in UNKNOWN_OVERRIDES.values()]
    vectors += [{**_clear_inputs(), **{k: (float(x) if isinstance(x, np.floating) else
                                           bool(x) if isinstance(x, np.bool_) else x)
                                       for k, x in o.items()}}
                for o in NUMPY_TRUE_OVERRIDES.values() if "gate1_windows" not in o
                and "concentration" not in o]
    assert len(vectors) >= 2 + 12 + 12 + 9
    n_diff = 0
    for inputs in vectors:
        old, new = before.evaluate_failure_signals(**inputs), evaluate_failure_signals(**inputs)
        assert list(old["signals"]) == list(new["signals"]) == ALL_FS
        for k in ALL_FS:
            o, n = old["signals"][k], new["signals"][k]
            assert (o is None) == (n is None), f"{k}: UNKNOWN đổi ({o!r} -> {n!r})"
            if o is not None:
                assert bool(o) == n and type(n) is bool, f"{k}: {o!r} -> {n!r}"
        assert old["unknown"] == new["unknown"]
        # any_true chỉ được khác đúng khi: có UNKNOWN, hoặc có TRUE mà bản cũ không nhìn thấy
        old_true_logical = any(bool(x) for x in old["signals"].values() if x is not None)
        expected_new = old_true_logical or bool(new["unknown"])
        assert new["any_true"] is expected_new
        if old["any_true"] != new["any_true"]:
            n_diff += 1
            assert new["unknown"] or (old_true_logical and not old["any_true"])
    assert n_diff > 0, "đối chứng vô nghĩa: không vector nào tái lập khiếm khuyết"
