"""Backtest §21.2: unlock/hysteresis, HWM modes, Opp cap overflow, reserve/release/partial fill."""
import pytest

from eth_dca_os.capital import (
    BASE_SCHEDULE,
    InvariantError,
    MonthlyCapital,
    OpportunityHysteresis,
    Pool,
    SmartUnlockState,
    apply_monthly_contribution,
    opportunity_reservable,
    smart_reservable,
)
from eth_dca_os.config import BASELINE_STRATEGY

DAY = 86400.0


def test_pool_invariants_and_flow():
    p = Pool("SMART")
    p.contribute(100.0)
    assert p.total == 100.0
    assert p.reserve(60.0, "SMART_ZONE_S0")
    assert (p.available, p.reserved) == (40.0, 60.0)
    assert not p.reserve(50.0, "SMART_ZONE_S1")  # requested_reserve > AVAILABLE
    p.deploy_from_reserved(25.0, "SMART_ZONE_S0")   # partial fill
    assert (p.reserved, p.deployed) == (35.0, 25.0)
    p.release(35.0, "ACTION_TTL_EXPIRED")           # phần chưa fill release sau TTL
    assert p.available == pytest.approx(75.0)
    assert p.total == pytest.approx(100.0)          # TOTAL = A + R + D bảo toàn
    with pytest.raises(InvariantError):
        p.release(999.0, "X")


def test_opportunity_hysteresis_zone():
    h = OpportunityHysteresis()
    assert h.update(60) is False
    assert h.update(68) is True          # activate tại 68
    assert h.update(65) is True          # vùng 62–68 giữ trạng thái
    assert h.update(63) is True          # ACTIVE trong vùng 62–65: hợp lệ
    assert h.update(62) is False         # suspend tại 62
    assert h.update(66) is False         # vùng giữ trạng thái (đang suspended)
    assert h.update(69) is True


def test_active_with_zero_unlock_is_valid():
    from eth_dca_os.score import opportunity_unlock
    h = OpportunityHysteresis()
    h.update(70)
    assert h.update(63) is True
    fund = Pool("OPP")
    fund.contribute(100.0)
    # ACTIVE nhưng unlock(63) = 0 -> không được reserve vốn MỚI
    assert opportunity_reservable(fund, float(opportunity_unlock(63)), True, 0.0, 0.20) == 0.0


def test_hwm_modes():
    ts0 = 0.0
    # HWM: peak giữ nguyên trong tháng
    s = SmartUnlockState(mode="HWM")
    s.month_reset(ts0)
    assert s.effective_unlock(0.8, ts0) == 0.8
    assert s.effective_unlock(0.3, ts0 + DAY) == 0.8
    # NO_HWM: bám unlock hiện tại
    s2 = SmartUnlockState(mode="NO_HWM")
    s2.month_reset(ts0)
    assert s2.effective_unlock(0.8, ts0) == 0.8
    assert s2.effective_unlock(0.3, ts0 + DAY) == 0.3
    # DECAY_HWM: giảm 0.10 mỗi 7 ngày không revalidate, sàn = unlock hiện tại
    s3 = SmartUnlockState(mode="DECAY_HWM", hwm_decay_step=0.10, hwm_decay_days=7)
    s3.month_reset(ts0)
    assert s3.effective_unlock(0.8, ts0) == 0.8
    assert s3.effective_unlock(0.3, ts0 + 6 * DAY) == pytest.approx(0.8)   # chưa đủ 7 ngày
    assert s3.effective_unlock(0.3, ts0 + 7 * DAY) == pytest.approx(0.7)   # decay 1 bậc
    assert s3.effective_unlock(0.3, ts0 + 14 * DAY) == pytest.approx(0.6)  # decay 2 bậc
    assert s3.effective_unlock(0.55, ts0 + 100 * DAY) == pytest.approx(0.55)  # sàn
    # revalidate bởi unlock cao hơn
    assert s3.effective_unlock(0.9, ts0 + 101 * DAY) == pytest.approx(0.9)


def test_monthly_contribution_cap_overflow():
    cfg = BASELINE_STRATEGY
    mc = MonthlyCapital(Pool("BASE"), Pool("SMART"), Pool("OPP_FUND"),
                        monthly_opp_contribution=20.0, opportunity_cap_months=4)
    # cap = 80; nạp 5 tháng: tháng 5 phải overflow sang Smart
    for month in range(5):
        r = apply_monthly_contribution(mc, 100.0, cfg)
    assert mc.opportunity_fund.total == pytest.approx(80.0)
    assert r["opportunity_added"] == pytest.approx(0.0)
    assert r["opportunity_overflow_to_smart"] == pytest.approx(20.0)
    assert mc.smart.total == pytest.approx(30.0 * 5 + 20.0)
    assert mc.base.total == pytest.approx(50.0 * 5)


def test_smart_reservable_no_relock():
    smart = Pool("SMART")
    smart.contribute(100.0)
    # unlock 0.5 -> 50 reservable
    assert smart_reservable(smart, 100.0, 0.5) == pytest.approx(50.0)
    smart.reserve(50.0, "SMART_ZONE_S0")
    smart.deploy_from_reserved(50.0, "SMART_ZONE_S0")
    # unlock tụt về 0.2 nhưng deployed 50 không relock; không còn phần mới để reserve
    assert smart_reservable(smart, 100.0, 0.2) == 0.0
    # unlock lên 0.7 -> 70 - 50 deployed = 20
    assert smart_reservable(smart, 100.0, 0.7) == pytest.approx(20.0)


def test_opportunity_daily_limit():
    fund = Pool("OPP")
    fund.contribute(100.0)
    # unlock đủ nhưng daily limit 20% và đã dùng 15 hôm nay -> chỉ còn 5
    assert opportunity_reservable(fund, 0.6, True, 15.0, 0.20) == pytest.approx(5.0)
    # suspended -> 0
    assert opportunity_reservable(fund, 0.6, False, 0.0, 0.20) == 0.0


def test_base_schedule_shares():
    assert [d for d, _ in BASE_SCHEDULE] == [3, 13, 23]
    assert sum(p for _, p in BASE_SCHEDULE) == pytest.approx(1.0)
