"""WP-A5 — Đo đủ dữ liệu cho ba Failure Signal chưa bao giờ nhận input.

Đóng phần ĐO LƯỜNG của F-002 (FS-02, FS-06, FS-12 luôn UNKNOWN vì không được truyền
input) và toàn bộ F-016 (FS-03/FS-07 chỉ tính trên một window đại diện W5).

Nguyên tắc của bộ test này, theo đúng chữ Completion Gate WP-A5:

* `CHECK-A5-01..03` đòi **ca có đáp số biết trước** — chứng minh đại lượng được TÍNH ĐÚNG,
  không chỉ được TRUYỀN. Vì vậy mỗi đại lượng có một test tính tay trên dữ liệu dựng sẵn,
  tách khỏi test đấu nối.
* Ranh giới ĐO LƯỜNG / CHÍNH SÁCH là ràng buộc cứng: `CHECK-A5-07` khoá **hành vi ngưỡng**
  của `failure_signals.py` bằng cách gọi tại biên, chứ không đọc văn bản mã nguồn — nếu
  WP-A5 lỡ đụng vào chính sách thì test đỏ.
* `CHECK-A5-08` so bit-for-bit engine hiện tại với engine TRƯỚC WP-A5 nạp từ git: điểm thu
  thập số liệu không được đổi một con số nào của chiến lược.
"""
from __future__ import annotations

import subprocess

import numpy as np
import pandas as pd
import pytest

from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.data.synth import generate
from eth_dca_os.engine import run_engine
from eth_dca_os.failure_signals import evaluate_failure_signals
from eth_dca_os.metrics import (
    _regime_at,
    adjacent_config_flip,
    aggregate_over_windows,
    cash_ratio_stats,
    concentration,
    opportunity_cap_hit_share,
    regime_advantage,
    regime_advantage_pooled,
    run_window,
    window_metrics,
)
from eth_dca_os.windows import primary_median

# SHA của commit ngay TRƯỚC WP-A5 (WP-A6 DONE). Dùng cho CHECK-A5-08.
PRE_A5_SHA = "b095874"


# ------------------------------------------------------------------ tiện ích


class _FakeResult:
    """RunResult tối giản: chỉ mang đúng những trường mà hàm đo đọc tới."""

    def __init__(self, opp_cap_samples=None, purchases=None, regime_timeline=None):
        self.opp_cap_samples = opp_cap_samples or []
        self.purchases = purchases or []
        self.regime_timeline = regime_timeline or []


def _sample(ts, total, cap, available):
    return {"ts": ts, "total": total, "cap": cap, "available": available,
            "at_cap": cap > 0 and total >= cap - 1e-9, "idle": available > 1e-9}


@pytest.fixture(scope="module")
def synth_raw(tmp_path_factory):
    raw = tmp_path_factory.mktemp("wp_a5") / "raw"
    generate(raw, start="2018-01-01", end="2026-06-30")
    return raw


@pytest.fixture(scope="module")
def dataset(synth_raw):
    from eth_dca_os.data.dataset import load_dataset
    return load_dataset(synth_raw)


@pytest.fixture(scope="module")
def scores(dataset):
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores
    ind = compute_daily_indicators(dataset["ETHUSDT_1d"], dataset["BTCUSDT_1d"])
    sc = compute_scores(ind, BASELINE_STRATEGY.score_weights)
    merged = pd.concat([ind, sc], axis=1)
    return merged.loc[:, ~merged.columns.duplicated()]


@pytest.fixture(scope="module")
def wm(dataset, scores):
    """Chín window pre-OOS chạy MỘT LẦN, dùng lại cho mọi test phạm vi."""
    return window_metrics(dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION)


# =========================================================== CHECK-A5-01 (FS-02)


def test_a5_01_cap_hit_share_known_answer():
    """Đáp số biết trước: 3/10 mẫu thoả CẢ HAI vế -> share = 0.3 chính xác."""
    cap = 200.0
    samples = [
        _sample(1, 200.0, cap, 50.0),    # at_cap + idle   -> ĐẾM
        _sample(2, 200.0, cap, 0.0),     # at_cap, hết idle -> không đếm
        _sample(3, 120.0, cap, 120.0),   # idle nhưng chưa chạm cap -> không đếm
        _sample(4, 200.0, cap, 1.0),     # at_cap + idle   -> ĐẾM
        _sample(5, 0.0, cap, 0.0),
        _sample(6, 199.0, cap, 199.0),   # sát cap nhưng CHƯA tới -> không đếm
        _sample(7, 200.0, cap, 200.0),   # at_cap + idle   -> ĐẾM
        _sample(8, 200.0, cap, 0.0),
        _sample(9, 150.0, cap, 10.0),
        _sample(10, 200.0, cap, 0.0),
    ]
    out = opportunity_cap_hit_share(_FakeResult(opp_cap_samples=samples))
    assert out["n_samples"] == 10 and out["n_hit"] == 3
    assert out["share"] == pytest.approx(0.3)
    assert out["reason"] is None
    # thống kê phụ trợ cho WP-B1 — KHÔNG phải input của FS-02
    assert out["at_cap_share"] == pytest.approx(0.6)          # 6/10 mẫu at_cap
    assert out["share_idle_ge_10pct_cap"] == pytest.approx(0.4)  # available >= 20


def test_a5_01_cap_hit_share_no_samples_is_unknown_not_zero():
    """Không có mẫu -> None kèm lý do. Không được thay bằng 0.0 (Escalation Trigger #2)."""
    out = opportunity_cap_hit_share(_FakeResult())
    assert out["share"] is None and out["reason"] == "no_opp_cap_samples"


def test_a5_01_engine_emits_cap_samples(dataset, scores):
    """Engine thật phải sinh mẫu theo NGÀY, cùng nhịp với cash_samples."""
    res = run_engine(dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                     pd.Timestamp("2019-01-01"), pd.Timestamp("2021-01-01"))
    assert res.opp_cap_samples, "engine không sinh opp_cap_samples (FS-02 sẽ lại UNKNOWN)"
    assert len(res.opp_cap_samples) == len(res.cash_samples)
    assert opportunity_cap_hit_share(res)["share"] is not None


# =========================================================== CHECK-A5-02 (FS-12)


def test_a5_02_regime_advantage_known_answer():
    """Đáp số tính tay.

    Chiến lược: CRASH 3.0 + NORMAL 1.0 ETH. Benchmark: CRASH 1.0 + NORMAL 2.0.
    Lợi thế: CRASH +2.0, NORMAL -1.0. Khối lợi thế DƯƠNG = 2.0 -> share = 2.0/2.0 = 1.0,
    trong khi lợi thế RÒNG chỉ 1.0 (mẫu số ròng sẽ cho 2.0 — vô nghĩa vì > 1).
    """
    timeline = [(0.0, "NORMAL"), (100.0, "CRASH")]
    res = _FakeResult(
        purchases=[{"ts": 10.0, "eth": 1.0, "regime": "NORMAL"},
                   {"ts": 150.0, "eth": 3.0, "regime": "CRASH"}],
        regime_timeline=timeline)
    win = {"result": res,
           "bench": {"purchases": [{"ts": 20.0, "eth": 2.0}, {"ts": 160.0, "eth": 1.0}]}}
    out = regime_advantage(win)
    assert out["by_regime"] == pytest.approx({"CRASH": 2.0, "NORMAL": -1.0})
    assert out["positive_mass"] == pytest.approx(2.0)
    assert out["net_advantage"] == pytest.approx(1.0)
    assert out["share"] == pytest.approx(1.0)
    assert out["top_regime"] == "CRASH"


def test_a5_02_regime_advantage_two_regimes_share():
    """Hai regime cùng dương: share = phần lớn nhất / tổng khối dương (6/(6+2) = 0.75)."""
    timeline = [(0.0, "NORMAL"), (100.0, "CRASH")]
    res = _FakeResult(
        purchases=[{"ts": 10.0, "eth": 4.0, "regime": "NORMAL"},
                   {"ts": 150.0, "eth": 7.0, "regime": "CRASH"}],
        regime_timeline=timeline)
    win = {"result": res,
           "bench": {"purchases": [{"ts": 20.0, "eth": 2.0}, {"ts": 160.0, "eth": 1.0}]}}
    assert regime_advantage(win)["share"] == pytest.approx(0.75)


def test_a5_02_no_positive_advantage_is_unknown_not_zero():
    """Không regime nào có lợi thế dương -> None kèm lý do, KHÔNG phải 0.0.

    0.0 sẽ được đọc thành 'không tập trung' — một khẳng định sai về dữ liệu.
    """
    timeline = [(0.0, "NORMAL")]
    res = _FakeResult(purchases=[{"ts": 10.0, "eth": 1.0, "regime": "NORMAL"}],
                      regime_timeline=timeline)
    win = {"result": res, "bench": {"purchases": [{"ts": 20.0, "eth": 5.0}]}}
    out = regime_advantage(win)
    assert out["share"] is None
    assert out["reason"] == "no_positive_advantage_in_any_regime"


def test_a5_02_benchmark_purchase_attributed_by_timeline():
    """Purchase của benchmark KHÔNG mang nhãn regime -> phải quy về mốc đổi nhãn."""
    timeline = [(0.0, "NORMAL"), (100.0, "CRASH"), (200.0, "RECOVERY")]
    assert _regime_at(timeline, -5.0) == "NORMAL"     # trước mốc đầu -> nhãn khởi tạo
    assert _regime_at(timeline, 0.0) == "NORMAL"
    assert _regime_at(timeline, 99.9) == "NORMAL"
    assert _regime_at(timeline, 100.0) == "CRASH"
    assert _regime_at(timeline, 199.9) == "CRASH"
    assert _regime_at(timeline, 10_000.0) == "RECOVERY"


def test_a5_02_engine_emits_regime_timeline(dataset, scores):
    """Engine phải ghi mốc đổi nhãn, và chỉ ghi KHI ĐỔI (không ghi mỗi nến)."""
    res = run_engine(dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                     pd.Timestamp("2019-01-01"), pd.Timestamp("2021-01-01"))
    tl = res.regime_timeline
    assert tl, "engine không ghi regime_timeline (FS-12 sẽ lại UNKNOWN)"
    labels = [lab for _, lab in tl]
    assert all(a != b for a, b in zip(labels, labels[1:])), "có mốc trùng nhãn liên tiếp"
    assert [t for t, _ in tl] == sorted(t for t, _ in tl)
    assert len(tl) < len(res.cash_samples), "timeline phải thưa hơn mẫu ngày"


# =========================================================== CHECK-A5-03 (FS-06)


def _cfg_row(name, passed):
    return {"config_name": name, "gate1": {"pass": passed}}


def test_a5_03_adjacent_config_flip_known_answer():
    """Baseline PASS, một config OFAT FAIL -> flip = True, đếm đúng 1."""
    per_config = [_cfg_row("baseline", True),
                  _cfg_row("ofat_cooldown_hours=24", True),
                  _cfg_row("ofat_base_pct=0.5", False),
                  _cfg_row("lhs_000", False)]      # lhs KHÔNG kề nhau -> không tính
    out = adjacent_config_flip(per_config)
    assert out["flip"] is True
    assert out["n_adjacent"] == 2 and out["n_flipped"] == 1
    assert out["flipped_configs"] == ["ofat_base_pct=0.5"]


def test_a5_03_lhs_config_alone_never_counts_as_adjacent():
    """Chỉ có config nhiều chiều (lhs) -> không có config kề nhau -> UNKNOWN có lý do."""
    out = adjacent_config_flip([_cfg_row("baseline", True), _cfg_row("lhs_000", False)])
    assert out["flip"] is None
    assert out["reason"] == "no_adjacent_config_in_manifest"


def test_a5_03_flip_detected_in_both_directions():
    """Spec nói 'đảo ngược', không nói riêng chiều xấu đi -> FAIL->PASS cũng là flip."""
    out = adjacent_config_flip([_cfg_row("baseline", False),
                                _cfg_row("ofat_base_pct=0.5", True)])
    assert out["flip"] is True and out["baseline_pass"] is False


def test_a5_03_no_flip_when_all_adjacent_agree():
    out = adjacent_config_flip([_cfg_row("baseline", True),
                                _cfg_row("ofat_a=1", True), _cfg_row("ofat_b=2", True)])
    assert out["flip"] is False and out["n_flipped"] == 0


def test_a5_03_real_manifest_names_are_recognised_as_adjacent():
    """Khoá vào tên THẬT của manifest Gate 2: nếu quy ước đặt tên đổi, test đỏ."""
    from eth_dca_os.manifests import generate_gate2_manifest
    man = generate_gate2_manifest()
    assert man["ofat"], "manifest Gate 2 không còn config OFAT nào"
    assert all(c.config_name.startswith("ofat_") for c in man["ofat"])
    per_config = ([_cfg_row(man["baseline"].config_name, True)]
                  + [_cfg_row(c.config_name, True) for c in man["ofat"]])
    out = adjacent_config_flip(per_config)
    assert out["n_adjacent"] == len(man["ofat"]) and out["flip"] is False


# =========================================================== CHECK-A5-05 (F-016)


def test_a5_05_fs03_fs07_computed_over_nine_windows(wm):
    """FS-03 và FS-07 phải gộp trên CẢ CHÍN window bằng PrimaryMedian, không phải W5."""
    assert len(wm["windows"]) == 9
    conc_pw = {w: concentration(r)["ae_ex_month"] for w, r in wm["windows"].items()}
    cash_pw = {w: cash_ratio_stats(r["result"])["avg"] for w, r in wm["windows"].items()}
    assert len(conc_pw) == 9 and len(cash_pw) == 9
    # phép gộp phải TRÙNG KHỚP PrimaryMedian tính độc lập trong test
    assert aggregate_over_windows(conc_pw)["value"] == pytest.approx(primary_median(conc_pw))
    assert aggregate_over_windows(cash_pw)["value"] == pytest.approx(primary_median(cash_pw))


def test_a5_05_nine_window_scope_differs_from_w5_only(wm):
    """Chứng minh mở rộng phạm vi KHÔNG phải thay đổi hình thức: số đo thật sự khác.

    Đây là lý do F-016 tồn tại — một window đại diện không đại diện cho cả mẫu.
    """
    conc_pw = {w: concentration(r)["ae_ex_month"] for w, r in wm["windows"].items()}
    assert conc_pw["W5"] != pytest.approx(primary_median(conc_pw), rel=1e-6), (
        "giá trị W5 trùng khít giá trị gộp — kiểm lại dữ liệu, mở rộng phạm vi sẽ vô nghĩa")


def test_a5_05_missing_window_is_unknown_not_silently_dropped():
    """Thiếu một window -> None kèm tên window thiếu. Không bỏ qua để 'còn tính được'."""
    out = aggregate_over_windows({"W1": 1.0, "W2": None, "W3": float("nan")})
    assert out["value"] is None
    assert "W2" in out["reason"] and "W3" in out["reason"]


def test_a5_05_fs12_pooled_scope_covers_nine_windows(wm):
    """FS-12 gộp theo KHỐI LỢI THẾ trên chín window; per-window vẫn được ghi lại."""
    out = regime_advantage_pooled(wm["windows"])
    assert len(out["per_window"]) == 9
    assert out["share"] is not None, f"FS-12 vẫn UNKNOWN: {out['reason']}"
    assert 0.0 <= out["share"] <= 1.0
    # tổng khối lợi thế phải bằng tổng của từng window (phép cộng, không phải median)
    pooled_net = sum(out["by_regime"].values())
    per_win_net = sum(regime_advantage(r)["net_advantage"] for r in wm["windows"].values())
    assert pooled_net == pytest.approx(per_win_net)


# =========================================================== CHECK-A5-04


def test_a5_04_wp_a5_quantities_are_plain_python_floats(wm):
    """Đại lượng WP-A5 giao đi phải là `float` THUẦN PYTHON, không phải `numpy.float64`.

    Không phải chuyện thẩm mỹ. `failure_signals.py` gộp cờ chặn bằng
    `any(v is True for v in ...)`, mà `numpy.bool_(True) is True` cho **False**. Một
    `numpy.float64` đi vào so sánh ngưỡng sẽ sinh `numpy.bool_`, khiến một Failure Signal
    TRUE trở nên VÔ HÌNH với quy tắc chặn của BT §17 — verdict sẽ ra BUILD trong khi spec
    nói BUILD là không thể. WP-A5 không được sửa `failure_signals.py`, nên nó phải giao
    đúng kiểu.
    """
    caphit = {w: opportunity_cap_hit_share(r["result"])["share"]
              for w, r in wm["windows"].items()}
    assert all(type(v) is float for v in caphit.values())
    assert type(aggregate_over_windows(caphit)["value"]) is float
    pooled = regime_advantage_pooled(wm["windows"])
    assert type(pooled["share"]) is float
    assert all(type(v) is float for v in pooled["by_regime"].values())
    assert type(pooled["positive_mass"]) is float
    assert type(pooled["net_advantage"]) is float


def test_a5_04_wp_a5_signals_visible_to_bt17_blocking_rule(wm):
    """Signal do WP-A5 cấp input phải BẬT ĐƯỢC cờ chặn `any_true` của BT §17.

    Đây là phép kiểm end-to-end của "được TRUYỀN": một giá trị mà quy tắc chặn không nhìn
    thấy thì chưa phải là đã truyền tới nơi.
    """
    caphit = aggregate_over_windows(
        {w: opportunity_cap_hit_share(r["result"])["share"]
         for w, r in wm["windows"].items()})["value"]
    share = regime_advantage_pooled(wm["windows"])["share"]

    fs02 = evaluate_failure_signals(opportunity_cap_hit_share=caphit)
    fs12 = evaluate_failure_signals(regime_advantage_share=share)
    for out, key in ((fs02, "FS-02"), (fs12, "FS-12")):
        assert type(out["signals"][key]) is bool, (
            f"{key} không phải bool thuần Python -> vô hình với `any_true`")
    # trên dữ liệu tổng hợp cả hai đều TRUE; cờ chặn phải thấy được
    assert fs02["signals"]["FS-02"] is True and fs02["any_true"] is True
    assert fs12["signals"]["FS-12"] is True and fs12["any_true"] is True


def test_a5_04_numpy_typed_signal_would_be_invisible():
    """Ghi lại CƠ CHẾ của khiếm khuyết F-S015-01, để nó không bị quên.

    Test này KHÔNG khẳng định hành vi hiện tại là đúng — nó chứng minh vì sao kiểu dữ liệu
    quan trọng, và sẽ đỏ nếu `failure_signals.py` sau này được làm bền với numpy (khi đó
    xoá test này và đóng F-S015-01).
    """
    out = evaluate_failure_signals(regime_advantage_share=np.float64(0.95))
    assert out["signals"]["FS-12"], "giá trị vẫn TRUE về mặt logic"
    assert out["any_true"] is False, (
        "nếu dòng này đỏ nghĩa là `any_true` đã được làm bền với numpy.bool_ — "
        "đóng F-S015-01 và xoá test này")


# =========================================================== CHECK-A5-06


def test_a5_06_cap_hit_and_cash_see_released_capital(dataset, scores):
    """Số đo FS-02/FS-07 phản ánh vốn THỰC SỰ khả dụng, không phải vốn bị treo.

    Đây là lý do WP-A5 phụ thuộc WP-A3: trước khi F-001 được sửa, vốn có thể bị khoá
    vĩnh viễn trong reservation, và khi đó `available` (vế `idle` của FS-02) cùng cash
    ratio đều đo ra số nhỏ hơn sự thật. Test khẳng định vốn được release đi VÀO số đo.
    """
    win = run_window(dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                     "2021-01-01", "2023-01-01")
    res = win["result"]
    # Bất biến kiểm được từ chính mẫu: total = available + reserved + deployed luôn đúng,
    # và không mẫu nào có available âm (vốn bị treo sẽ lộ ra ở đây).
    assert res.opp_cap_samples
    for s in res.opp_cap_samples:
        assert s["available"] >= -1e-9, "available âm — vốn kế toán sai"
        assert s["total"] >= s["available"] - 1e-9
    # Trong một cửa sổ đi qua CRASH -> RECOVERY -> NORMAL, phải tồn tại ít nhất một lần
    # `available` TĂNG so với mẫu trước: đó chính là vốn được trả lại sau recovery-end /
    # huỷ zone. Nếu vốn bị khoá vĩnh viễn (F-001 chưa sửa) thì chuỗi này đơn điệu giảm.
    avail = [s["available"] for s in res.opp_cap_samples]
    assert any(b > a + 1e-9 for a, b in zip(avail, avail[1:])), (
        "available không bao giờ tăng — dấu hiệu vốn bị treo, số đo FS-02/FS-07 sẽ sai")
    labels = {lab for _, lab in res.regime_timeline}
    assert len(labels) > 1, "cửa sổ không đi qua nhiều regime, ca kiểm không có hiệu lực"
    cash = cash_ratio_stats(res)
    assert 0.0 <= cash["avg"] <= 1.0 and not np.isnan(cash["avg"])


# =========================================================== CHECK-A5-07


def test_a5_07_verdict_policy_thresholds_unchanged():
    """Khoá HÀNH VI ngưỡng của `failure_signals.py` bằng cách gọi tại biên.

    WP-A5 chỉ được sinh và truyền số ĐO. Mọi ngưỡng dưới đây thuộc WP-B1; nếu gói này
    (hoặc một gói sau) lỡ đụng vào chính sách, test đỏ ngay tại con số bị đổi.
    """
    # FS-02: ngưỡng 0.5, so sánh CHẶT
    assert evaluate_failure_signals(opportunity_cap_hit_share=0.50)["signals"]["FS-02"] is False
    assert evaluate_failure_signals(opportunity_cap_hit_share=0.51)["signals"]["FS-02"] is True
    # FS-12: ngưỡng 0.80, so sánh CHẶT
    assert evaluate_failure_signals(regime_advantage_share=0.80)["signals"]["FS-12"] is False
    assert evaluate_failure_signals(regime_advantage_share=0.81)["signals"]["FS-12"] is True
    # FS-06: truyền thẳng, không có ngưỡng
    assert evaluate_failure_signals(adjacent_config_flip=True)["signals"]["FS-06"] is True
    assert evaluate_failure_signals(adjacent_config_flip=False)["signals"]["FS-06"] is False
    # FS-03: ngưỡng 100.0 trên ex-month HOẶC ex-quarter
    assert evaluate_failure_signals(
        concentration={"ae_ex_month": 100.0, "ae_ex_quarter": 100.0})["signals"]["FS-03"] is False
    assert evaluate_failure_signals(
        concentration={"ae_ex_month": 99.9, "ae_ex_quarter": 100.0})["signals"]["FS-03"] is True
    # FS-07: cần CẢ HAI vế (cash > 0.30 VÀ ae < 102.0)
    assert evaluate_failure_signals(avg_cash_ratio=0.31,
                                    gate1_primary_ae=101.9)["signals"]["FS-07"] is True
    assert evaluate_failure_signals(avg_cash_ratio=0.30,
                                    gate1_primary_ae=101.9)["signals"]["FS-07"] is False
    assert evaluate_failure_signals(avg_cash_ratio=0.31,
                                    gate1_primary_ae=102.0)["signals"]["FS-07"] is False


def test_a5_07_unknown_policy_untouched():
    """Chính sách UNKNOWN (`None` -> signal `None`) là của WP-B1 — WP-A5 không thêm đường mới."""
    fs = evaluate_failure_signals()["signals"]
    assert set(fs) == {f"FS-{i:02d}" for i in range(1, 13)}
    assert all(v is None for v in fs.values()), "một FS có giá trị mặc định khi thiếu input"
    assert evaluate_failure_signals()["unknown"] == list(fs)


def test_a5_07_no_diff_in_policy_files():
    """`git diff` đúng như chữ CHECK-A5-07: hai file chính sách không đổi kể từ trước WP-A5."""
    diff = subprocess.run(
        ["git", "diff", "--stat", f"{PRE_A5_SHA}..HEAD", "--",
         "src/eth_dca_os/verdict.py", "src/eth_dca_os/failure_signals.py"],
        capture_output=True, text=True, check=True).stdout.strip()
    assert diff == "", f"WP-A5 đã đụng vào file chính sách:\n{diff}"


# =========================================================== CHECK-A5-08


def test_a5_08_instrumentation_does_not_change_engine_behaviour(dataset, scores):
    """So bit-for-bit với engine TRƯỚC WP-A5 (nạp từ git): đo không được đổi hành vi."""
    from tests.wp_a6_order_harness import load_engine_from_source

    src = subprocess.run(["git", "show", f"{PRE_A5_SHA}:src/eth_dca_os/engine.py"],
                         capture_output=True, text=True, check=True).stdout
    before = load_engine_from_source(src, name="eth_dca_os._engine_pre_a5")
    args = (dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
            pd.Timestamp("2019-01-01"), pd.Timestamp("2022-01-01"))
    old, new = before.run_engine(*args), run_engine(*args)

    assert old.eth_total == new.eth_total, "instrumentation làm đổi ETH tích luỹ"
    assert len(old.purchases) == len(new.purchases)
    for a, b in zip(old.purchases, new.purchases):
        assert a == b, f"purchase khác nhau: {a} vs {b}"
    assert old.counters == new.counters
    assert old.cash_samples == new.cash_samples
    assert old.monthly_deployments == new.monthly_deployments
    # và bản cũ đúng là bản CHƯA có instrumentation (nếu không, phép so vô nghĩa)
    assert not getattr(old, "opp_cap_samples", None)
    assert not getattr(old, "regime_timeline", None)
    assert new.opp_cap_samples and new.regime_timeline
