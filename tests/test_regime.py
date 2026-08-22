"""Backtest §21.3: crash entry 24h/7D, chặn khi OSCORE<75, exit 48h, recovery 72h, re-entry, STRESSED."""
from eth_dca_os.regime import RegimeTracker

H = 3600.0


def test_crash_entry_conditions():
    t = RegimeTracker()
    # đủ điều kiện giá nhưng OSCORE < 75 -> không vào CRASH (thành STRESSED)
    assert t.update(0, -0.16, -0.02, 60) == "STRESSED"
    # entry qua 7D
    assert t.update(1 * H, -0.16, -0.02, 80) == "CRASH"
    assert t.last_entry_reason == "CRASH_ENTRY_7D"
    t2 = RegimeTracker()
    # entry qua 24H
    assert t2.update(0, -0.05, -0.11, 76) == "CRASH"
    assert t2.last_entry_reason == "CRASH_ENTRY_24H"


def test_crash_exit_requires_48h_sustained():
    t = RegimeTracker()
    t.update(0, -0.20, -0.12, 80)
    assert t.regime == "CRASH"
    # điều kiện exit xuất hiện nhưng chưa đủ 48h
    assert t.update(10 * H, -0.05, -0.02, 80) == "CRASH"
    assert t.update(40 * H, -0.05, -0.02, 80) == "CRASH"
    # bị ngắt quãng -> reset đồng hồ
    assert t.update(41 * H, -0.12, -0.06, 80) == "CRASH"
    assert t.update(42 * H, -0.05, -0.02, 80) == "CRASH"
    assert t.update(42 * H + 47 * H, -0.05, -0.02, 80) == "CRASH"   # 47h liên tục
    assert t.update(42 * H + 48 * H, -0.05, -0.02, 80) == "RECOVERY"


def test_recovery_72h_then_normal_and_reentry():
    t = RegimeTracker()
    t.update(0, -0.20, -0.12, 80)
    t.update(1 * H, -0.05, -0.02, 80)
    t.update(1 * H + 48 * H, -0.05, -0.02, 80)
    assert t.regime == "RECOVERY"
    start = 1 * H + 48 * H
    assert t.update(start + 71 * H, 0.02, 0.01, 50) == "RECOVERY"
    assert t.update(start + 72 * H, 0.02, 0.01, 50) == "NORMAL"
    # re-entry trong recovery
    t2 = RegimeTracker()
    t2.update(0, -0.20, -0.12, 80)
    t2.update(1 * H, -0.05, -0.02, 80)
    t2.update(49 * H, -0.05, -0.02, 80)
    assert t2.regime == "RECOVERY"
    assert t2.update(60 * H, -0.02, -0.11, 80) == "CRASH"  # re-enter


def test_stressed_label_reporting_only():
    t = RegimeTracker()
    assert t.update(0, -0.11, 0.0, 40) == "STRESSED"   # 7D <= -10%
    assert t.update(1, -0.02, -0.08, 40) == "STRESSED" # 24H <= -7%
    assert t.update(2, -0.02, -0.01, 40) == "NORMAL"
    # STRESSED không dính hysteresis, không ảnh hưởng crash counters
    assert t.crash_entered_at is None
