"""Backtest §21.2–21.3: ladder immutability, invalidation 2 daily close, spacing, expiry, crash."""
import pytest

from eth_dca_os.config import BASELINE_STRATEGY
from eth_dca_os.ladders import (
    CRASH_ALLOC,
    SMART_ALLOC,
    create_crash_ladder,
    create_opportunity_ladder,
    create_smart_ladder,
    crash_spacing,
    opportunity_spacing,
    smart_spacing,
    update_bullish_invalidation,
)

CFG = BASELINE_STRATEGY


def test_spacing_formulas():
    # ADR30 2% x factor 2.0 x mult(70)=1.0 -> 4% (đúng min)
    assert smart_spacing(0.02, 70, CFG) == pytest.approx(0.04)
    # clamp min: ADR30 rất nhỏ
    assert smart_spacing(0.005, 40, CFG) == pytest.approx(CFG.smart_spacing_min)
    # clamp max
    assert smart_spacing(0.10, 90, CFG) == pytest.approx(CFG.smart_spacing_max)
    # opportunity: x1.25, clamp [6%, 15%]
    assert opportunity_spacing(0.04, CFG) == pytest.approx(0.06)  # 5% -> clamp lên 6%
    assert opportunity_spacing(0.08, CFG) == pytest.approx(0.10)
    # crash: MAX(opp, 7%)
    assert crash_spacing(0.06) == pytest.approx(0.07)
    assert crash_spacing(0.10) == pytest.approx(0.10)


def test_smart_ladder_structure():
    lad = create_smart_ladder(anchor=100.0, spacing=0.05, unlocked_smart_vnd=100.0,
                              oscore=70.0, ts=0.0, month_end_ts=30 * 86400.0)
    assert [z.target_price for z in lad.zones] == pytest.approx([100.0, 95.0, 90.0])
    assert [z.allocation_pct for z in lad.zones] == list(SMART_ALLOC)
    assert sum(z.target_vnd for z in lad.zones) == pytest.approx(100.0)


def test_opportunity_ladder_endpoints():
    lad = create_opportunity_ladder(100.0, 0.08, 100.0, oscore=80.0, ts=0.0)
    assert [round(z.allocation_pct, 2) for z in lad.zones] == [0.10, 0.15, 0.20, 0.25, 0.30]
    assert lad.zones[4].target_price == pytest.approx(100.0 * (1 - 4 * 0.08))
    assert lad.expires_at == pytest.approx(90 * 86400.0)
    lad70 = create_opportunity_ladder(100.0, 0.08, 100.0, oscore=70.0, ts=0.0)
    assert [round(z.allocation_pct, 2) for z in lad70.zones] == [0.0, 0.15, 0.20, 0.25, 0.40]


def test_crash_ladder_snapshot_immutable():
    lad = create_crash_ladder(100.0, 0.06, eligible_snapshot_vnd=200.0, oscore=80.0, ts=0.0)
    assert lad.spacing_pct == pytest.approx(0.07)  # MAX(6%, 7%)
    assert [z.allocation_pct for z in lad.zones] == list(CRASH_ALLOC)
    assert sum(z.target_vnd for z in lad.zones) == pytest.approx(200.0)
    # snapshot bất biến: eligible_capital_vnd không đổi khi tạo xong [F5]
    assert lad.eligible_capital_vnd == 200.0


def test_bullish_invalidation_two_closes():
    lad = create_smart_ladder(100.0, 0.05, 100.0, 70.0, 0.0, 30 * 86400.0)
    inv = lad.invalidation_price
    assert inv == pytest.approx(100.0 * 1.12)  # MAX(12%, 2x5%=10%) = 12%
    assert update_bullish_invalidation(lad, inv * 1.01) is False   # close 1
    assert lad.status == "ACTIVE"
    assert update_bullish_invalidation(lad, inv * 0.99) is False   # reset chuỗi
    assert update_bullish_invalidation(lad, inv * 1.01) is False   # close 1 (lại)
    assert update_bullish_invalidation(lad, inv * 1.02) is True    # close 2 liên tiếp
    assert lad.status == "INVALIDATED"


def test_invalidation_uses_2x_spacing_when_larger():
    lad = create_opportunity_ladder(100.0, 0.08, 100.0, 75.0, 0.0)
    assert lad.invalidation_price == pytest.approx(100.0 * 1.16)  # 2x8% = 16% > 12%


def test_anchor_spacing_immutable_dataclass():
    lad = create_smart_ladder(100.0, 0.05, 100.0, 70.0, 0.0, 30 * 86400.0)
    a0, s0 = lad.anchor_price, lad.spacing_pct
    update_bullish_invalidation(lad, 90.0)
    assert (lad.anchor_price, lad.spacing_pct) == (a0, s0)
