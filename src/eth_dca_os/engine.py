"""Simulation engine — vòng lặp 15m theo ĐÚNG processing order 18 bước (Backtest §19).

Đơn vị danh nghĩa 1 USDT = 1 đơn vị (Backtest §2.1 [F6]). Các quy ước triển khai
cho những điểm spec để ngỏ: docs/CONVENTIONS.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .capital import (
    BASE_SCHEDULE,
    BaseScheduleState,
    MonthlyCapital,
    OpportunityHysteresis,
    Pool,
    SmartUnlockState,
    apply_monthly_contribution,
    opportunity_reservable,
    smart_reservable,
)
from .execution import MISSED, apply_fill, behavioral_delay_seconds, total_delay_seconds
from .ladders import (
    Ladder,
    create_crash_ladder,
    create_opportunity_ladder,
    create_smart_ladder,
    opportunity_spacing,
    smart_spacing,
    update_bullish_invalidation,
)
from .regime import RegimeTracker
from .score import opportunity_unlock, smart_unlock

TZ_OFFSET = 7 * 3600  # Asia/Ho_Chi_Minh, không DST
NOON = 12 * 3600
DAY = 86400.0

# Thứ tự pool §15.1 [F2]: Base -> Smart -> Opportunity
_POOL_RANK = {"BASE": 0, "SMART": 1, "OPPORTUNITY": 2}


def zone_order_key(zone, ladder) -> tuple:
    """Khoá sắp thứ tự thực thi khi nhiều zone cùng trigger — Strategy §15.1 [F2].

    1. Giữa các pool: Base -> Smart -> Opportunity; Crash ladder xếp theo pool
       NGUỒN VỐN của nó (zone.pool phản ánh nguồn vốn thật — xem CONVENTIONS #16),
       và SAU các ladder Smart/Opportunity thường cùng pool.
    2. Trong cùng pool: ladder có created_at sớm hơn xử lý trước.
    3. Trong cùng ladder: zone_index tăng dần.
    max_zones_per_cycle áp SAU khi đã sắp thứ tự này.
    """
    return (_POOL_RANK.get(zone.pool, 3),
            1 if ladder.type == "CRASH" else 0,
            ladder.created_at,
            zone.zone_index)


@dataclass
class RunResult:
    purchases: list = field(default_factory=list)
    contributions: list = field(default_factory=list)
    counters: dict = field(default_factory=dict)
    monthly_deployments: dict = field(default_factory=dict)  # "YYYY-MM" -> nominal deployed
    cash_samples: list = field(default_factory=list)          # (ts, cash, eth)
    decision_log: list = field(default_factory=list)

    @property
    def eth_total(self) -> float:
        return sum(p["eth"] for p in self.purchases)

    @property
    def contributed_total(self) -> float:
        return sum(c[1] for c in self.contributions)


def _epoch_seconds(series_or_index) -> np.ndarray:
    """Epoch seconds bất kể datetime64 unit (ns/us) của pandas."""
    vals = pd.DatetimeIndex(series_or_index)
    return ((vals - pd.Timestamp(0, tz=vals.tz)) / pd.Timedelta(seconds=1)).to_numpy(float)


def _prep_candles(eth15: pd.DataFrame, start_ts: float, end_ts: float) -> dict:
    ts = _epoch_seconds(eth15["open_time"])
    mask = (ts >= start_ts) & (ts < end_ts)
    idx0 = int(np.argmax(mask)) if mask.any() else 0
    arr = {k: eth15[k].to_numpy(float)[mask] for k in ("open", "high", "low", "close")}
    arr["ts"] = ts[mask]
    # Return24H nội ngày: 96 nến 15m liền trước — cần lịch sử trước start
    full_close = eth15["close"].to_numpy(float)
    sel = np.nonzero(mask)[0]
    r24 = np.full(len(sel), np.nan)
    ok = sel >= 96
    r24[ok] = full_close[sel[ok]] / full_close[sel[ok] - 96] - 1
    arr["r24"] = r24
    return arr


def _daily_arrays(scores: pd.DataFrame) -> dict:
    day_ts = _epoch_seconds(scores.index)  # 00:00 UTC của ngày D
    return {
        "day_end_ts": day_ts + DAY,  # nến daily D đóng hoàn toàn tại thời điểm này
        "oscore": scores["oscore"].to_numpy(float),
        "dq": scores["data_quality"].to_numpy(object),
        "return7": scores["return7"].to_numpy(float),
        "adr30": scores["adr30"].to_numpy(float),
        "close": scores["close"].to_numpy(float),
    }


def run_engine(dataset: dict, scores_with_ind: pd.DataFrame, strategy_cfg, exec_cfg,
               start: pd.Timestamp, end: pd.Timestamp,
               contribution: float = 100.0, behavioral_rng: np.random.Generator | None = None,
               log_decisions: bool = False) -> RunResult:
    """Chạy engine từ `start` tới `end` (state mới hoàn toàn — xem CONVENTIONS #12)."""
    cfg = strategy_cfg
    start_ts = start.tz_localize("UTC").timestamp() if start.tzinfo is None else start.timestamp()
    end_ts = end.tz_localize("UTC").timestamp() if end.tzinfo is None else end.timestamp()
    c = _prep_candles(dataset["ETHUSDT_15m"], start_ts, end_ts)
    d = _daily_arrays(scores_with_ind)
    n = len(c["ts"])
    res = RunResult()
    if n == 0:
        return res

    behavioral = exec_cfg.behavioral_model == "LOCAL_HOUR"
    if behavioral and behavioral_rng is None:
        behavioral_rng = np.random.default_rng(0)

    # ------------------------------------------------- state
    base_pool, smart_pool, opp_fund = Pool("BASE"), Pool("SMART"), Pool("OPPORTUNITY")
    mc = MonthlyCapital(base_pool, smart_pool, opp_fund,
                        monthly_opp_contribution=contribution * cfg.opportunity_pct,
                        opportunity_cap_months=cfg.opportunity_cap_months)
    su = SmartUnlockState(cfg.smart_unlock_mode, cfg.hwm_decay_step, cfg.hwm_decay_days)
    hyst = OpportunityHysteresis(cfg.opportunity_activate_score, cfg.opportunity_suspend_score)
    regime = RegimeTracker()
    base_state = BaseScheduleState()

    ladders: list[Ladder] = []
    reserve_map: dict[int, list] = {}     # zone_id -> [(pool, amount)]
    zone_meta: dict[int, dict] = {}       # zone_id -> {'recommended': px, 'behavioral_missed': bool}

    cur_month = None                      # (year, month) local
    cur_day_ord = None
    month_base_budget = 0.0
    month_smart_budget = 0.0
    smart_ladder_created_this_month = False
    day_flags: dict = {}                  # per-day: base noon fired, month-end fired
    daily_idx = -1
    oscore = np.nan
    dq = "INVALID"
    r7 = np.nan
    adr30 = np.nan
    last_good_opp_unlock = 0.0
    opp_used_today = 0.0
    cooldown_until = -np.inf
    last_exec_price = np.nan
    prev_state = "NORMAL"           # trạng thái NỀN trước đó ([F1]: execution không đọc nhãn)
    eth_total = 0.0
    counters = {
        "cooldown_override": {"NORMAL": 0, "STRESSED": 0, "CRASH": 0, "RECOVERY": 0},
        "triggered_actions": 0, "missed_actions": 0, "executed_actions": 0,
        "base_early": 0, "delayed_data_fill": 0,
    }

    day_end = d["day_end_ts"]

    def log(ts, reason, **kw):
        if log_decisions:
            res.decision_log.append({"ts": ts, "reason_code": reason, **kw})

    def record_purchase(ts, source, nominal, open_price, reason, recommended=None):
        nonlocal eth_total, cooldown_until, last_exec_price
        eth, eff = apply_fill(nominal, open_price, exec_cfg)
        eth_total += eth
        month_key = pd.Timestamp(ts + TZ_OFFSET, unit="s").strftime("%Y-%m")
        res.monthly_deployments[month_key] = res.monthly_deployments.get(month_key, 0.0) + nominal
        res.purchases.append({
            "ts": ts, "source": source, "nominal": nominal, "price": eff, "eth": eth,
            "reason": reason, "regime": regime.regime,
            "recommended_price": recommended,
            "shortfall_bps": ((eff / recommended - 1) * 1e4) if recommended else None,
        })
        if source in ("SMART", "OPPORTUNITY", "CRASH"):
            cooldown_until = ts + cfg.cooldown_hours * 3600.0
            last_exec_price = eff

    def zone_pools(z):
        return reserve_map.get(z.zone_id, [(z.pool, z.reserved_vnd)])

    def release_zone(z, ts, reason):
        for pool_name, amt in zone_pools(z):
            if amt > 0:
                _pool(pool_name).release(amt, reason, ts)
        reserve_map.pop(z.zone_id, None)
        z.reserved_vnd = 0.0

    def deploy_zone(z, ts, reason):
        for pool_name, amt in zone_pools(z):
            if amt > 0:
                _pool(pool_name).deploy_from_reserved(amt, reason, ts)
        reserve_map.pop(z.zone_id, None)

    def _pool(name: str) -> Pool:
        return {"BASE": base_pool, "SMART": smart_pool, "OPPORTUNITY": opp_fund}[name]

    def cancel_open_zones(lad, ts, reason):
        for z in lad.zones:
            if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING",
                            "PARTIALLY_FILLED"):
                if z.reserved_vnd > 0:
                    release_zone(z, ts, reason)
                z.status = "CANCELLED"

    def expire_smart_ladders(ts):
        for lad in ladders:
            if lad.type == "SMART" and lad.status == "ACTIVE":
                cancel_open_zones(lad, ts, "LADDER_EXPIRED")
                lad.status = "EXPIRED"

    def settle_month_end_smart(ts, open_price):
        avail = smart_pool.available
        if avail <= 1e-9:
            return
        if not np.isnan(oscore) and oscore >= 45:
            if smart_pool.deploy_from_available(avail, "MONTH_END_SMART", ts):
                record_purchase(ts, "SMART", avail, open_price, "MONTH_END_SMART")
        else:
            buy = avail * 0.5
            to_opp = avail - buy
            headroom = max(0.0, mc.opportunity_cap - opp_fund.total)
            xfer = min(to_opp, headroom)
            if xfer > 0:
                smart_pool.transfer_available_to(opp_fund, xfer, "MONTH_END_SMART", ts)
            leftover = to_opp - xfer
            buy += leftover  # phần vượt cap được mua nốt (CONVENTIONS #7)
            if buy > 0 and smart_pool.deploy_from_available(buy, "MONTH_END_SMART", ts):
                record_purchase(ts, "SMART", buy, open_price, "MONTH_END_SMART")

    def execute_base_tranche(idx, ts, open_price, reason):
        amt = min(base_state.tranche_amount(idx), base_pool.available)
        if amt <= 1e-9:
            base_state.executed.add(idx)
            return
        base_pool.deploy_from_available(amt, reason, ts)
        base_state.executed.add(idx)
        record_purchase(ts, "BASE", amt, open_price, reason)

    def create_action(z, lad, ts_close, close_price, local_hour):
        """TRIGGERED -> ACTION_PENDING với delay model (Backtest §5–§6)."""
        z.status = "ACTION_PENDING"
        z.triggered_at = ts_close
        z.action_expires_at = ts_close + exec_cfg.action_ttl_seconds
        zone_meta[z.zone_id] = {"recommended": close_price}
        counters["triggered_actions"] += 1
        if exec_cfg.p2p_unavailable_in_crash and regime.state == "CRASH" \
                and exec_cfg.funding_policy == "ON_DEMAND":
            z.execute_at = None  # funding không khả dụng suốt TTL -> MISSED
            return
        if behavioral:
            secs_to_7 = ((7 * 3600 - ((ts_close + TZ_OFFSET) % DAY)) % DAY)
            delay = behavioral_delay_seconds(local_hour, behavioral_rng, secs_to_7,
                                             exec_cfg.action_ttl_seconds)
            if delay == MISSED:
                z.execute_at = None
                return
            fd = 0.0 if exec_cfg.funding_policy == "BULK_MONTHLY" else exec_cfg.funding_delay_seconds
            z.execute_at = ts_close + delay + fd
        else:
            z.execute_at = ts_close + total_delay_seconds(exec_cfg)

    # ------------------------------------------------- main loop
    for i in range(n):
        ts = c["ts"][i]                              # 1. tiến đồng hồ (open time của nến)
        o, hi, lo, cl = c["open"][i], c["high"][i], c["low"][i], c["close"][i]
        local = ts + TZ_OFFSET
        day_ord = int(local // DAY)
        lts = pd.Timestamp(local, unit="s")
        month_key = (lts.year, lts.month)
        acct_day = lts.day
        tod = local % DAY

        # 2–6. accounting month mới
        if month_key != cur_month:
            if cur_month is not None:
                expire_smart_ladders(ts)             # 3. Smart ladder hết hạn cuối tháng
                # đóng sổ: Base còn sót (gap) giải ngân ngay, Smart leftover theo policy
                for idx in base_state.pending():
                    execute_base_tranche(idx, ts, o, "MONTH_END_BASE")
                    counters["delayed_data_fill"] += 1
                settle_month_end_smart(ts, o)
            cur_month = month_key
            # 3->4. đóng sổ tháng cũ / mở sổ tháng mới cho phạm vi unlock Smart theo
            # tháng (DM §5; WP-A7/F-035) — SAU settle Month-End, TRƯỚC contribution.
            smart_pool.open_accounting_month(ts)
            su.month_reset(ts)                       # 4. reset HWM theo mode
            br = apply_monthly_contribution(mc, contribution, cfg, ts)  # 5–6. contribution + cap
            res.contributions.append((ts, contribution))
            month_base_budget = br["base"]
            month_smart_budget = br["smart"] + br["opportunity_overflow_to_smart"]
            base_state.month_reset(month_base_budget)
            smart_ladder_created_this_month = False
            day_flags = {}

        # 7. reset bộ đếm theo accounting day
        if day_ord != cur_day_ord:
            cur_day_ord = day_ord
            opp_used_today = 0.0
            day_flags[day_ord] = {"noon": False, "score_advanced": False}

        # 8. daily score mới nếu nến daily nguồn đã đóng
        new_score = False
        ndi = int(np.searchsorted(day_end, ts, side="right")) - 1
        if ndi > daily_idx and ndi >= 0:
            daily_idx = ndi
            prev_dq = dq
            oscore = d["oscore"][ndi]
            dq = d["dq"][ndi]
            r7 = d["return7"][ndi]
            adr30 = d["adr30"][ndi]
            new_score = True
            # 18(một phần). bullish invalidation trên daily close mới
            daily_close = d["close"][ndi]
            for lad in ladders:
                if lad.status == "ACTIVE" and update_bullish_invalidation(lad, daily_close):
                    cancel_open_zones(lad, ts, "BULLISH_INVALIDATION")
                    log(ts, "BULLISH_INVALIDATION", ladder=lad.ladder_id)

        # unlocks hiện hành (DEGRADED không được đẩy Opp unlock lên — CONVENTIONS #9)
        s_unl = float(smart_unlock(oscore)) if not np.isnan(oscore) else 0.0
        o_unl = float(opportunity_unlock(oscore)) if not np.isnan(oscore) else 0.0
        if dq == "GOOD":
            last_good_opp_unlock = o_unl
        elif dq == "DEGRADED":
            o_unl = min(o_unl, last_good_opp_unlock)
        else:
            s_unl, o_unl = 0.0, 0.0
        eff_smart_unlock = su.effective_unlock(s_unl, ts)
        opp_active = hyst.update(oscore) if not np.isnan(oscore) else hyst.active

        # hysteresis chuyển trạng thái zone Opportunity
        for lad in ladders:
            if lad.type == "OPPORTUNITY" and lad.status == "ACTIVE":
                for z in lad.zones:
                    if not opp_active and z.status == "ACTIVE":
                        z.status = "SUSPENDED"
                        z.suspended_at = ts
                    elif opp_active and z.status == "SUSPENDED":
                        z.status = "ACTIVE"
                        z.suspended_at = None
                    elif z.status == "SUSPENDED" and z.suspended_at is not None and \
                            ts - z.suspended_at > cfg.suspended_zone_hold_days * DAY:
                        release_zone(z, ts, "OPPORTUNITY_SUSPENDED")
                        z.status = "CANCELLED"

        # 9. Base schedule (12:00 local Day 3/13/23) + Base execute sớm + Month-End
        flags = day_flags.setdefault(day_ord, {"noon": False, "score_advanced": False})
        if not flags["noon"] and tod >= NOON:
            flags["noon"] = True
            delayed = tod > NOON + 900
            for k, (day_no, _) in enumerate(BASE_SCHEDULE):
                if acct_day == day_no and k in base_state.pending():
                    execute_base_tranche(k, ts, o, "BASE_SCHEDULE")
                    if delayed:
                        counters["delayed_data_fill"] += 1
            if acct_day == 25 and base_pool.available > 1e-9:
                # Day 25–27: settle 50% phần Base còn lại (CONVENTIONS #7)
                amt = base_pool.available * 0.5
                if base_pool.deploy_from_available(amt, "MONTH_END_BASE", ts):
                    record_purchase(ts, "BASE", amt, o, "MONTH_END_BASE")
                    for k in base_state.pending():
                        base_state.executed.add(k)
            if acct_day == 28:
                if base_pool.available > 1e-9:
                    amt = base_pool.available
                    base_pool.deploy_from_available(amt, "MONTH_END_BASE", ts)
                    record_purchase(ts, "BASE", amt, o, "MONTH_END_BASE")
                expire_smart_ladders(ts)
                settle_month_end_smart(ts, o)
        if new_score and not np.isnan(oscore) and oscore >= 70 and not flags["score_advanced"]:
            nxt = base_state.next_pending()
            if nxt is not None:
                execute_base_tranche(nxt, ts, o, "BASE_ADVANCE_SCORE")
                counters["base_early"] += 1
            flags["score_advanced"] = True  # tối đa một tranche mỗi lần score mới active

        # 10. Market Regime + nhãn STRESSED. Mọi nhánh execution dưới đây so trên
        # regime.state (trạng thái nền); nhãn STRESSED chỉ dùng reporting ([F1] §17.3).
        prev_state = regime.state
        regime.update(ts, r7 if not np.isnan(r7) else None,
                      c["r24"][i] if not np.isnan(c["r24"][i]) else None,
                      None if np.isnan(oscore) else oscore)
        if regime.state == "CRASH" and prev_state != "CRASH":
            # cancel Opportunity zone xung đột -> release -> snapshot -> crash ladder [F5]
            for lad in ladders:
                if lad.type == "OPPORTUNITY" and lad.status == "ACTIVE":
                    cancel_open_zones(lad, ts, "CRASH_ENTRY")
                    lad.status = "CANCELLED"
            # [F5] ST §14: snapshot = Smart AVAILABLE + Opportunity AVAILABLE (đã unlock,
            # chưa nằm trong reservation nào) đo NGAY SAU cancel/release. KHÔNG áp daily
            # limit vào snapshot (F-021); daily limit cưỡng chế ở khâu triển khai — bước 14.
            if opp_active and o_unl > 0:
                opp_avail = min(opp_fund.available,
                                max(0.0, opp_fund.total * o_unl
                                    - opp_fund.reserved - opp_fund.deployed))
            else:
                opp_avail = 0.0
            smart_avail = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
            snapshot = opp_avail + smart_avail
            if snapshot > 1e-9 and not np.isnan(adr30):
                ssp = smart_spacing(adr30, oscore, cfg)
                osp = opportunity_spacing(ssp, cfg)
                lad = create_crash_ladder(o, osp, snapshot, oscore, ts)
                # reserve Opportunity trước, Smart sau (CONVENTIONS #5)
                for z in lad.zones:
                    want = z.target_vnd
                    parts = []
                    take_opp = min(want, opp_avail)
                    if take_opp > 0 and opp_fund.reserve(take_opp, "CRASH_ZONE", ts):
                        parts.append(("OPPORTUNITY", take_opp))
                        opp_avail -= take_opp
                        want -= take_opp
                    take_smart = min(want, smart_avail)
                    if take_smart > 0 and smart_pool.reserve(take_smart, "CRASH_ZONE", ts):
                        parts.append(("SMART", take_smart))
                        smart_avail -= take_smart
                        want -= take_smart
                    z.reserved_vnd = sum(a for _, a in parts)
                    z.target_vnd = z.reserved_vnd
                    reserve_map[z.zone_id] = parts
                # F-030: pool label của Crash ladder = pool cấp ĐA SỐ tổng reserve
                # (tie-break §15.1 [F2] xếp theo pool nguồn vốn; hoà -> OPPORTUNITY,
                # xem CONVENTIONS #16). Label thống nhất cả ladder để zone_index giữ
                # đúng thứ tự trong cùng ladder.
                smart_funded = sum(a for z in lad.zones
                                   for p, a in reserve_map.get(z.zone_id, [])
                                   if p == "SMART")
                opp_funded = sum(a for z in lad.zones
                                 for p, a in reserve_map.get(z.zone_id, [])
                                 if p == "OPPORTUNITY")
                src_pool = "SMART" if smart_funded > opp_funded else "OPPORTUNITY"
                for z in lad.zones:
                    z.pool = src_pool
                ladders.append(lad)
                log(ts, regime.last_entry_reason, ladder=lad.ladder_id)
        if regime.state == "RECOVERY" and prev_state == "CRASH":
            for lad in ladders:
                if lad.type == "CRASH" and lad.status == "ACTIVE":
                    lad.status = "SUSPENDED"
                    for z in lad.zones:
                        if z.status == "ACTIVE":
                            z.status = "SUSPENDED"
                            z.suspended_at = ts
        if regime.state == "NORMAL" and prev_state == "RECOVERY":
            # ST §18.3: hết 72h Recovery -> CANCEL crash zone chưa hit + release reserve.
            # So trên TRẠNG THÁI NỀN nên chạy cho MỌI kết cục recovery-end, kể cả khi
            # nhãn báo cáo là STRESSED (F-001). Quét mọi crash ladder còn mở để các
            # ladder tồn đọng từ episode trước (re-entry) cũng được đóng.
            for lad in ladders:
                if lad.type == "CRASH" and lad.status in ("ACTIVE", "SUSPENDED"):
                    cancel_open_zones(lad, ts, "RECOVERY_END")
                    lad.status = "CANCELLED"

        # 11. cooldown & override
        in_cooldown = ts < cooldown_until
        override_ok = (not np.isnan(last_exec_price)) and \
            (o <= last_exec_price * (1 - cfg.cooldown_override_pct))

        # 12. pending action tới hạn / TTL / MISSED
        for lad in ladders:
            for z in lad.zones:
                if z.status != "ACTION_PENDING":
                    continue
                if z.execute_at is not None and ts >= z.execute_at:
                    if z.execute_at <= z.action_expires_at:
                        nominal = z.reserved_vnd
                        deploy_zone(z, ts, f"{lad.type}_ZONE")
                        z.status = "EXECUTED"
                        z.executed_at = ts
                        counters["executed_actions"] += 1
                        src = "CRASH" if lad.type == "CRASH" else lad.type
                        record_purchase(ts, src, nominal, o,
                                        f"{lad.type}_ZONE_{z.zone_index}",
                                        recommended=zone_meta.get(z.zone_id, {}).get("recommended"))
                    else:
                        release_zone(z, ts, "ACTION_TTL_EXPIRED")
                        z.status = "MISSED"
                        counters["missed_actions"] += 1
                elif ts >= z.action_expires_at:
                    release_zone(z, ts, "ACTION_MISSED")
                    z.status = "MISSED"
                    counters["missed_actions"] += 1

        # tạo ladder mới (CONVENTIONS #1, #2) — trước bước kiểm tra trigger
        if dq != "INVALID" and not np.isnan(oscore) and not np.isnan(adr30):
            ssp = smart_spacing(adr30, oscore, cfg)
            if (not smart_ladder_created_this_month and acct_day <= 24
                    and eff_smart_unlock > 0):
                unlocked = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
                if unlocked > 1e-9:
                    # cuối accounting month (giờ local) — F-028: trước đây dùng ts + 31 ngày
                    # cố định, sai nghĩa; expiry THẬT của Smart ladder không đọc field này
                    # (xem expire_smart_ladders, dựa trên phát hiện month rollover), nên đây
                    # chỉ là sửa dữ liệu cho đúng nghĩa, không đổi hành vi (WP-D1/F-028).
                    next_month_local = lts.replace(day=1) + pd.DateOffset(months=1)
                    month_end_ts = next_month_local.value / 1e9 - TZ_OFFSET
                    lad = create_smart_ladder(o, ssp, unlocked, oscore, ts, month_end_ts)
                    for z in lad.zones:
                        if smart_pool.reserve(z.target_vnd, f"SMART_ZONE_S{z.zone_index}", ts):
                            z.reserved_vnd = z.target_vnd
                            reserve_map[z.zone_id] = [("SMART", z.target_vnd)]
                        else:
                            z.status = "CANCELLED"
                    ladders.append(lad)
                    smart_ladder_created_this_month = True
            if opp_active and o_unl > 0 and not any(
                    l.type == "OPPORTUNITY" and l.status == "ACTIVE" for l in ladders):
                osp = opportunity_spacing(ssp, cfg)
                eligible = opportunity_reservable(opp_fund, o_unl, opp_active,
                                                  opp_used_today, cfg.opportunity_daily_limit_pct)
                if eligible > 1e-9:
                    lad = create_opportunity_ladder(o, osp, eligible, oscore, ts)
                    for z in lad.zones:
                        if z.target_vnd <= 1e-12:
                            continue
                        if opp_fund.reserve(z.target_vnd, f"OPPORTUNITY_O{z.zone_index}", ts):
                            z.reserved_vnd = z.target_vnd
                            reserve_map[z.zone_id] = [("OPPORTUNITY", z.target_vnd)]
                            opp_used_today += z.target_vnd
                        else:
                            z.status = "CANCELLED"
                    ladders.append(lad)

        # 13. trigger Smart (LOW) / confirmation Opportunity (CLOSE) — sắp thứ tự §15.1 [F2]
        candidates = []
        for lad in ladders:
            if lad.status not in ("ACTIVE", "SUSPENDED"):
                continue
            for z in lad.zones:
                trig_ok = z.status == "ACTIVE" or (
                    lad.type == "CRASH" and z.status == "SUSPENDED")
                if not trig_ok or z.reserved_vnd <= 1e-12:
                    continue
                if lad.type == "SMART" or lad.type == "CRASH":
                    hit = lo <= z.target_price
                else:  # OPPORTUNITY: confirmation bằng CLOSE
                    hit = cl <= z.target_price
                if hit:
                    z.status = "TRIGGERED"
            candidates.extend([z for z in lad.zones if z.status == "TRIGGERED"])

        # 14. chuyển TRIGGERED -> ACTION_PENDING: thứ tự §15.1 [F2] (zone_order_key),
        # max_zones_per_cycle áp SAU khi sắp thứ tự; cooldown/override; INVALID chặn
        if candidates and dq != "INVALID":
            lad_by_id = {l.ladder_id: l for l in ladders}
            candidates.sort(key=lambda z: zone_order_key(z, lad_by_id[z.ladder_id]))
            created = 0
            override_counted_this_cycle = False
            ts_close = ts + 900.0
            local_hour = int(((ts_close + TZ_OFFSET) % DAY) // 3600)
            for z in candidates:
                if created >= cfg.max_zones_per_cycle:
                    break
                if in_cooldown and not override_ok:
                    continue  # zone giữ TRIGGERED, xét lại cycle sau (CONVENTIONS #6)
                if lad_by_id[z.ladder_id].type == "CRASH":
                    # ST §14: "Toàn bộ daily limit ... vẫn áp dụng trong Crash" — cưỡng chế
                    # ở khâu triển khai trên PHẦN VỐN OPPORTUNITY của zone (CONVENTIONS #4).
                    # Zone bị chặn giữ TRIGGERED, xét lại cycle sau như max_zones (§15.1).
                    opp_part = sum(a for p, a in reserve_map.get(z.zone_id, [])
                                   if p == "OPPORTUNITY")
                    if opp_part > 1e-12:
                        headroom = max(0.0, opp_fund.total * cfg.opportunity_daily_limit_pct
                                       - opp_used_today)
                        if opp_part > headroom + 1e-9:
                            log(ts, "DAILY_LIMIT_BLOCK", zone=z.zone_id)
                            continue
                        opp_used_today += opp_part
                if in_cooldown and override_ok:
                    # đếm theo SỰ KIỆN override (một cycle), không theo zone được tạo action
                    # (WP-D1/F-031; BT §16/§21 dòng 301 — "tần suất cooldown override theo
                    # regime" là số liệu chẩn đoán, không phải input cho quyết định engine)
                    if not override_counted_this_cycle:
                        counters["cooldown_override"][regime.regime] += 1
                        override_counted_this_cycle = True
                    log(ts, "COOLDOWN_OVERRIDE", zone=z.zone_id)
                create_action(z, lad_by_id[z.ladder_id], ts_close, cl, local_hour)
                created += 1

        # 18. ladder completion / expiry (Opportunity 90 ngày)
        for lad in ladders:
            if lad.status == "ACTIVE" and lad.type == "OPPORTUNITY" and lad.expires_at \
                    and ts >= lad.expires_at:
                cancel_open_zones(lad, ts, "LADDER_EXPIRED")
                lad.status = "EXPIRED"
            if lad.status == "ACTIVE" and all(
                    z.status in ("EXECUTED", "CANCELLED", "MISSED", "EXPIRED")
                    for z in lad.zones):
                lad.status = "COMPLETED"

        # snapshot cash ratio (mỗi ngày một lần, tại nến đầu ngày)
        if i == 0 or int((c["ts"][i - 1] + TZ_OFFSET) // DAY) != day_ord:
            cash = base_pool.total - base_pool.deployed + smart_pool.total \
                - smart_pool.deployed + opp_fund.total - opp_fund.deployed
            res.cash_samples.append((ts, cash, eth_total, o))

    res.counters = counters
    return res
