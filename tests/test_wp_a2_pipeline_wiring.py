"""WP-A2 — Đấu nối các hạng mục đã viết nhưng pipeline chưa gọi.

Đóng F-003 (Benchmark B/C/D), F-004 (ablation §2.3 + volume z-score §2.4),
F-012 (bảng coverage §4), F-013 (XIRR §16), F-014 (bootstrap 1000/block length).

Đây là test ĐẤU NỐI: mỗi assertion phải fail nếu pipeline ngừng GỌI thành phần, kể cả
khi thành phần đó vẫn tồn tại và unit test riêng của nó vẫn PASS.
"""
from __future__ import annotations

import numpy as np
import pytest

import eth_dca_os.pipeline as pipeline_mod
from eth_dca_os.data.synth import generate
from eth_dca_os.metrics import xirr
from eth_dca_os.pipeline import Prepared, run_gate1


@pytest.fixture(scope="module")
def gate1_payload(tmp_path_factory):
    """Chạy Gate 1 official MỘT LẦN, chặn bootstrap thật để ghi lại n_sims đã truyền.

    Stub bootstrap vừa giữ thời gian chạy hợp lý vừa là phép đo trực tiếp cho
    CHECK-A2-06: giá trị `n_sims` mà pipeline truyền xuống được ghi lại nguyên vẹn.
    """
    root = tmp_path_factory.mktemp("wp_a2")
    raw, out = root / "raw", root / "results"
    generate(raw, start="2018-01-01", end="2026-06-30")

    seen: dict = {}

    def _spy(v2_purchases, a_purchases, n_sims=1000, master_seed=42):
        seen["n_sims"] = n_sims
        return {30: {"p5": 0.0, "p50": 0.0, "p95": 0.0, "label": "DESCRIPTIVE"}}

    orig = pipeline_mod.block_bootstrap_ae
    pipeline_mod.block_bootstrap_ae = _spy
    try:
        prep = Prepared(raw)
        payload = run_gate1(prep, out)          # mặc định = official run
    finally:
        pipeline_mod.block_bootstrap_ae = orig
    return payload, seen


# ------------------------------------------------------- CHECK-A2-01 (F-003)
def test_a2_01_benchmarks_bcd_run_and_present(gate1_payload):
    """Payload official phải chứa kết quả của CẢ B, C, D bên cạnh A."""
    payload, _ = gate1_payload
    bm = payload["benchmarks"]
    for name in ("A", "B", "C", "D"):
        assert name in bm, f"payload thiếu Benchmark {name} (F-003)"
        assert "primary_median_ae" in bm[name], f"Benchmark {name} thiếu AE tổng hợp"
        assert "ae_by_window" in bm[name] and len(bm[name]["ae_by_window"]) == 9
    med = {k: bm[k]["primary_median_ae"] for k in ("A", "B", "C", "D")}
    # hàng A của bảng so sánh phải TÁI LẬP đúng PrimaryMedian sẵn có — đường so sánh mới
    # nhất quán với đường cũ, và Benchmark A không bị đấu nối làm đổi (CHECK-A2-09)
    assert med["A"] == pytest.approx(payload["window_metrics"]["primary_median"], rel=1e-12), \
        f"AE vs A ({med['A']}) phải trùng PrimaryMedian sẵn có"
    # B, C, D phải là kết quả THẬT, khác nhau — không phải bản sao của A
    assert len({round(med[k], 6) for k in ("A", "B", "C", "D")}) == 4, \
        f"A/B/C/D phải cho bốn kết quả khác nhau, được {med}"


# ------------------------------------------------------- CHECK-A2-07 (equal capital)
def test_a2_07_equal_capital_rule_for_bcd(gate1_payload):
    """BT §12.1: mọi benchmark nhận CÙNG lịch external contribution — kiểm cho cả B, C, D."""
    payload, _ = gate1_payload
    bm = payload["benchmarks"]
    for wid in bm["A"]["contributed_by_window"]:
        vals = {name: bm[name]["contributed_by_window"][wid] for name in ("A", "B", "C", "D")}
        assert len({round(v, 6) for v in vals.values()}) == 1, \
            f"window {wid}: contribution của B/C/D phải bằng A, được {vals}"


# ------------------------------------------------------- CHECK-A2-02 (F-004 ablation)
def test_a2_02_ablation_three_models_in_payload(gate1_payload):
    """§2.3: ba model ablation đăng ký trước phải có mặt trong payload official."""
    payload, _ = gate1_payload
    abl = payload["diagnostics"]["ablation"]
    assert set(abl) >= {"price_minimal", "stress_minimal", "both_minimal"}, \
        f"thiếu model ablation (F-004): {sorted(abl)}"
    for name, row in abl.items():
        # đủ để trả lời "P có đóng góp gì ngoài D không" / "RSI ngoài Return7 không"
        assert "corr_with_baseline_oscore" in row and np.isfinite(row["corr_with_baseline_oscore"])
        assert "score_distribution" in row and "mean" in row["score_distribution"]
        assert "mean_abs_oscore_delta" in row


# ------------------------------------------------------- CHECK-A2-03 (F-004 z-score)
def test_a2_03_volume_zscore_variant_with_delta(gate1_payload):
    """§2.4: chạy biến thể z-score VÀ báo cáo **chênh lệch kết quả**, không chỉ chạy."""
    payload, _ = gate1_payload
    vz = payload["diagnostics"]["volume_zscore_variant"]
    assert "variant" in vz and "delta_vs_baseline" in vz, \
        "§2.4 đòi báo cáo chênh lệch, payload phải có cả biến thể lẫn bảng delta"
    d = vz["delta_vs_baseline"]
    assert {"mean_oscore_delta", "mean_abs_oscore_delta", "corr_with_baseline_oscore"} <= set(d)
    assert np.isfinite(d["mean_abs_oscore_delta"])
    assert vz["variant"]["score_distribution"]["mean"] != \
        payload["diagnostics"]["score_distribution"]["mean"], \
        "biến thể phải cho phân bố khác bản gốc — nếu trùng khít thì nó chưa thực sự được áp dụng"


# ------------------------------------------------------- CHECK-A2-04 (F-012 coverage)
def test_a2_04_coverage_table_always_present(gate1_payload):
    """§4: bảng coverage weight có trong MỌI báo cáo official, không phụ thuộc cờ."""
    payload, _ = gate1_payload
    cov = payload["window_metrics"]["coverage_table"]
    assert isinstance(cov, list) and len(cov) > 0, "thiếu bảng coverage §4 (F-012)"
    assert {"month", "windows"} <= set(cov[0])
    assert all(r["windows"] >= 0 for r in cov)
    assert max(r["windows"] for r in cov) >= 2, "coverage weight phải phản ánh window chồng lấn"


# ------------------------------------------------------- CHECK-A2-05 (F-013 XIRR)
def test_a2_05_xirr_present_in_payload(gate1_payload):
    """§16: XIRR / money-weighted return được tính và có trong payload."""
    payload, _ = gate1_payload
    x = payload["xirr"]
    assert "xirr" in x and np.isfinite(x["xirr"]), f"XIRR phải có và hữu hạn (F-013): {x}"
    assert x["n_cashflows"] >= 2
    assert "final_eth" in x and "final_price" in x


def test_a2_05b_xirr_known_answer():
    """Ca có đáp số biết trước: nộp 100 rồi nhận 110 sau đúng 1 năm -> XIRR = 10%."""
    year = 365.25 * 86400
    assert xirr([(0.0, -100.0), (year, 110.0)]) == pytest.approx(0.10, abs=1e-6)
    # hai kỳ nộp vốn, giá trị cuối gấp đôi tổng vốn -> lợi suất dương rõ rệt
    r = xirr([(0.0, -100.0), (year, -100.0), (2 * year, 400.0)])
    assert r > 0.5


# ------------------------------------------------------- CHECK-A2-06 (F-014 bootstrap)
def test_a2_06_bootstrap_uses_1000_sims_for_official(gate1_payload):
    """BT §13: official run dùng 1000 mô phỏng MỖI block length; pipeline không ghi đè 200."""
    _, seen = gate1_payload
    assert seen["n_sims"] == 1000, \
        f"official run phải truyền n_sims=1000 xuống bootstrap, được {seen.get('n_sims')}"


def test_a2_06b_dev_limit_keeps_smoke_fast(tmp_path):
    """Đường dev vẫn phải tồn tại và KHÁC official — dev_limit -> 200, official -> 1000."""
    assert pipeline_mod._bootstrap_sims(dev_limit=None) == 1000
    assert pipeline_mod._bootstrap_sims(dev_limit=3) == 200
