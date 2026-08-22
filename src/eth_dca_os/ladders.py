"""Ladder & zone lifecycle — Strategy §11–§14, §18, §19.

Anchor và spacing BẤT BIẾN; zone không bao giờ dịch lên trên; expiry theo loại;
bullish invalidation cần đúng HAI daily close liên tiếp trên InvalidationPrice.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

from .score import opportunity_ladder_weights, score_multiplier

_ladder_seq = count(1)
_zone_seq = count(1)

ZONE_STATUSES = ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING", "PARTIALLY_FILLED",
                 "EXECUTED", "CANCELLED", "EXPIRED", "MISSED")
LADDER_STATUSES = ("ACTIVE", "SUSPENDED", "COMPLETED", "INVALIDATED", "EXPIRED", "CANCELLED")

SMART_ALLOC = (0.33, 0.33, 0.34)
CRASH_ALLOC = (0.20, 0.25, 0.25, 0.30)


def smart_spacing(adr30: float, oscore: float, cfg) -> float:
    raw = adr30 * cfg.smart_spacing_factor * float(score_multiplier(oscore))
    return min(max(raw, cfg.smart_spacing_min), cfg.smart_spacing_max)


def opportunity_spacing(smart_sp: float, cfg) -> float:
    return min(max(smart_sp * cfg.opportunity_spacing_multiplier, 0.06), 0.15)


def crash_spacing(opp_spacing: float) -> float:
    return max(opp_spacing, 0.07)


@dataclass
class Zone:
    zone_id: int
    ladder_id: int
    zone_index: int
    target_price: float
    allocation_pct: float
    target_vnd: float                 # SOURCE OF TRUTH cho phân bổ
    pool: str                         # BASE / SMART / OPPORTUNITY (Crash zone giữ pool nguồn)
    status: str = "ACTIVE"
    reserved_vnd: float = 0.0
    filled_vnd: float = 0.0
    triggered_at: float | None = None
    action_expires_at: float | None = None
    execute_at: float | None = None   # thời điểm proxy thực thi (delay model)
    executed_at: float | None = None
    suspended_at: float | None = None

    @property
    def remaining_vnd(self) -> float:
        return max(0.0, self.target_vnd - self.filled_vnd)


@dataclass
class Ladder:
    ladder_id: int
    type: str                          # SMART / OPPORTUNITY / CRASH
    anchor_price: float                # BẤT BIẾN
    spacing_pct: float                 # BẤT BIẾN
    created_at: float
    expires_at: float | None
    score_at_creation: float
    eligible_capital_vnd: float
    zones: list[Zone] = field(default_factory=list)
    status: str = "ACTIVE"
    consecutive_invalidation_closes: int = 0

    @property
    def invalidation_price(self) -> float:
        return self.anchor_price * (1 + max(0.12, 2 * self.spacing_pct))


def _mk_zone(ladder: Ladder, idx: int, price: float, alloc: float, pool: str) -> Zone:
    return Zone(zone_id=next(_zone_seq), ladder_id=ladder.ladder_id, zone_index=idx,
                target_price=price, allocation_pct=alloc,
                target_vnd=ladder.eligible_capital_vnd * alloc, pool=pool)


def create_smart_ladder(anchor: float, spacing: float, unlocked_smart_vnd: float,
                        oscore: float, ts: float, month_end_ts: float) -> Ladder:
    lad = Ladder(next(_ladder_seq), "SMART", anchor, spacing, ts, month_end_ts, oscore,
                 unlocked_smart_vnd)
    for i, alloc in enumerate(SMART_ALLOC):
        lad.zones.append(_mk_zone(lad, i, anchor * (1 - i * spacing), alloc, "SMART"))
    return lad


def create_opportunity_ladder(anchor: float, spacing: float, eligible_vnd: float,
                              oscore: float, ts: float) -> Ladder:
    lad = Ladder(next(_ladder_seq), "OPPORTUNITY", anchor, spacing, ts,
                 ts + 90 * 86400.0, oscore, eligible_vnd)
    for i, alloc in enumerate(opportunity_ladder_weights(oscore)):
        lad.zones.append(_mk_zone(lad, i, anchor * (1 - i * spacing), alloc, "OPPORTUNITY"))
    return lad


def create_crash_ladder(anchor: float, opp_spacing: float, eligible_snapshot_vnd: float,
                        oscore: float, ts: float, source_pool: str = "OPPORTUNITY") -> Ladder:
    """eligible_snapshot_vnd = snapshot theo Strategy §14 [F5], bất biến trong đời ladder."""
    sp = crash_spacing(opp_spacing)
    lad = Ladder(next(_ladder_seq), "CRASH", anchor, sp, ts, None, oscore,
                 eligible_snapshot_vnd)
    for i, alloc in enumerate(CRASH_ALLOC):
        lad.zones.append(_mk_zone(lad, i, anchor * (1 - i * sp), alloc, source_pool))
    return lad


# ------------------------------------------------------------- lifecycle

OPEN_ZONE_STATUSES = ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING", "PARTIALLY_FILLED")


def update_bullish_invalidation(ladder: Ladder, daily_close: float) -> bool:
    """Gọi mỗi khi có daily close mới. Trả về True nếu ladder vừa INVALIDATED."""
    if ladder.status != "ACTIVE":
        return False
    if daily_close > ladder.invalidation_price:
        ladder.consecutive_invalidation_closes += 1
    else:
        ladder.consecutive_invalidation_closes = 0
    if ladder.consecutive_invalidation_closes >= 2:
        ladder.status = "INVALIDATED"
        return True
    return False


def open_zones(ladder: Ladder) -> list[Zone]:
    return [z for z in ladder.zones if z.status in OPEN_ZONE_STATUSES]


def ladder_completed(ladder: Ladder) -> bool:
    return all(z.status in ("EXECUTED", "PARTIALLY_FILLED", "CANCELLED", "EXPIRED", "MISSED")
               for z in ladder.zones) and any(z.status == "EXECUTED" for z in ladder.zones)
