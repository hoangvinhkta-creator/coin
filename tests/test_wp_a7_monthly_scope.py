"""WP-A7 — Phạm vi kế toán vốn Smart theo tháng (đóng F-035 / RSK-010).

Bám các REQUIRED check trong docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md:
  CHECK-A7-01  deployed tháng trước KHÔNG bóp quyền unlock tháng sau (DM §5, ST §4/§6)
  CHECK-A7-02  hành vi tương đương monthly_budgets DM §5 (month scope + reconcile với ledger)
  CHECK-A7-03  smart_unlock_mode không còn mechanically dead (ST §6, BT §9)
  CHECK-A7-04  ngữ nghĩa reset theo tháng của ba unlock mode
  CHECK-A7-05  tương tác Month-End / ranh giới đóng-mở sổ (ST §10)
  CHECK-A7-06  bất biến vốn multi-month + lịch sử audit toàn đời được bảo toàn (DM §6/§14)
  CHECK-A7-07  Opportunity Fund không regression sang ngữ nghĩa theo tháng (ST §7)

Bộ test A–G này được viết TRƯỚC remediation (test-first). Trạng thái FAIL trên HEAD
trước fix là baseline; xem docs/sessions/S004-wp-a7-monthly-smart-scope.md.
"""
import itertools

import pytest

import eth_dca_os.engine as engine_mod
import eth_dca_os.ladders as ladders_mod
from eth_dca_os.capital import (
    MonthlyCapital,
    Pool,
    SmartUnlockState,
    apply_monthly_contribution,
    opportunity_reservable,
    smart_reservable,
)
from eth_dca_os.config import BASELINE_STRATEGY
from wp_a3_harness import ledger_conservation_ok, run_case

DAY = 86400.0


@pytest.fixture(autouse=True)
def _reset_ladder_ids(monkeypatch):
    monkeypatch.setattr(ladders_mod, "_ladder_seq", itertools.count(1))
    monkeypatch.setattr(ladders_mod, "_zone_seq", itertools.count(1))


def month_days(n_days, oscore=60.0, price=100.0):
    """n_days ngày với oscore/price không đổi (ngày 1 đặt tường minh, còn lại kế thừa)."""
    return [{"oscore": oscore, "return7": 0.0, "price": price}] + [{} for _ in range(n_days - 1)]


# ---------------------------------------------------------------- A — CHECK-A7-01 (unit)


def test_a_month1_deploy_does_not_squeeze_month2_unit():
    """Chu trình đúng ST §10 + DM §5 ở tầng capital: tháng 1 tiêu HẾT ngân sách qua
    reserve→deploy và Month-End; mở sổ tháng 2 với ngân sách mới → quyền unlock tháng 2
    ở unlock = 1.00 phải bằng ĐÚNG ngân sách tháng 2, không bị deployed tháng 1 trừ."""
    p = Pool("SMART")
    budget = 30.0
    # ---- tháng 1
    p.open_accounting_month(0.0)
    p.contribute(budget, "CONTRIBUTION", 0.0)
    assert smart_reservable(p, budget, 1.0) == pytest.approx(30.0)
    assert p.reserve(21.0, "SMART_ZONE_S0", 1.0)
    p.deploy_from_reserved(21.0, "SMART_ZONE_S0", 2.0)
    # quyền còn lại trong THÁNG 1 phản ánh phần đã dùng (không relock trong tháng — ST §6)
    assert smart_reservable(p, budget, 1.0) == pytest.approx(9.0)
    p.deploy_from_available(p.available, "MONTH_END_SMART", 3.0)   # Day 28 / đóng sổ
    assert smart_reservable(p, budget, 1.0) == pytest.approx(0.0)
    # ---- tháng 2: mở sổ mới, ngân sách mới
    p.open_accounting_month(10.0)
    p.contribute(budget, "CONTRIBUTION", 10.0)
    assert p.deployed == pytest.approx(30.0)      # lịch sử lifetime GIỮ NGUYÊN (DM §6)
    assert smart_reservable(p, budget, 1.0) == pytest.approx(30.0), \
        "deployed tháng 1 không được bóp quyền unlock tháng 2 (F-035)"
    # ---- tháng 3: hành vi không suy biến dần
    p.reserve(30.0, "SMART_ZONE_S0", 11.0)
    p.deploy_from_reserved(30.0, "SMART_ZONE_S0", 12.0)
    p.open_accounting_month(20.0)
    p.contribute(budget, "CONTRIBUTION", 20.0)
    assert p.deployed == pytest.approx(60.0)
    assert smart_reservable(p, budget, 1.0) == pytest.approx(30.0)
    # unlock một phần: chỉ phần THÁNG NÀY đã dùng bị trừ
    assert p.reserve(6.0, "SMART_ZONE_S0", 21.0)
    assert smart_reservable(p, budget, 0.5) == pytest.approx(9.0)   # 15 - 6


def test_a2_month2_ladder_forms_engine(monkeypatch):
    """CHECK-A7-01 ở tầng engine: hai accounting month liên tiếp, oscore 60 đều —
    tháng 2 PHẢI tạo được Smart ladder mới với eligible = budget × unlock, dù tháng 1
    đã deploy trọn ngân sách Smart qua ladder + Month-End."""
    # first_local 2023-03-01: tháng 3 = 31 ngày, tháng 4 = 30 ngày
    days = month_days(31, oscore=60.0) + month_days(30, oscore=60.0)
    res, rec = run_case(days, monkeypatch)
    smart_lads = [l for l in rec.ladders if l.type == "SMART"]
    assert len(smart_lads) == 2, \
        f"mỗi tháng phải có một Smart ladder khi unlock > 0; có {len(smart_lads)}"
    for lad in smart_lads:
        # unlock(60) = (60-35)/35 = 0.714…; budget 30 -> eligible 21.4286
        assert lad.eligible_capital_vnd == pytest.approx(30.0 * (25.0 / 35.0), rel=1e-6)
    # ladder thứ hai nằm ở accounting month thứ hai
    TZ = 7 * 3600
    import pandas as pd
    m2 = pd.Timestamp(smart_lads[1].created_at + TZ, unit="s")
    m1 = pd.Timestamp(smart_lads[0].created_at + TZ, unit="s")
    assert (m2.year, m2.month) != (m1.year, m1.month)
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert ledger_conservation_ok(rec.pool(name))


# ---------------------------------------------------------------- B — multi-month


def test_b_multimonth_ladders_keep_forming(monkeypatch):
    """Bốn tháng liên tiếp score/unlock cho phép → BỐN Smart ladder (BEFORE: 1)."""
    days = []
    for n in (31, 30, 31, 30):          # 2023-03..2023-06 theo lịch thực
        days += month_days(n, oscore=60.0)
    res, rec = run_case(days, monkeypatch)
    smart_lads = [l for l in rec.ladders if l.type == "SMART"]
    assert len(smart_lads) == 4
    # không suy biến dần: eligible tháng 4 == tháng 1
    assert smart_lads[3].eligible_capital_vnd == pytest.approx(
        smart_lads[0].eligible_capital_vnd, rel=1e-9)
    # Smart đi qua ladder thật sự (không chỉ Month-End)
    via_ladder = sum(p["nominal"] for p in res.purchases
                     if p["reason"].startswith("SMART_ZONE"))
    assert via_ladder > 0


# ---------------------------------------------------------------- C — CHECK-A7-03/04


class _RecordingUnlock(SmartUnlockState):
    """Ghi lại effective-unlock path theo thời gian (instrument, không đổi hành vi)."""
    paths: list

    def effective_unlock(self, current_unlock, ts):
        v = super().effective_unlock(current_unlock, ts)
        type(self).paths.append((ts, current_unlock, v))
        return v


def _run_mode(mode, days, monkeypatch_cls):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(ladders_mod, "_ladder_seq", itertools.count(1))
        mp.setattr(ladders_mod, "_zone_seq", itertools.count(1))
        rec_cls = type(f"_Rec_{mode}", (_RecordingUnlock,), {"paths": []})
        mp.setattr(engine_mod, "SmartUnlockState", rec_cls)
        cfg = BASELINE_STRATEGY.with_(smart_unlock_mode=mode)
        res, rec = run_case(days, mp, strategy_cfg=cfg)
        return res, rec, rec_cls.paths


def test_c_mode_divergence_deterministic(monkeypatch):
    """CHECK-A7-03 (sống/chết) + CHECK-A7-04: kịch bản tất định hai tháng —
    tháng 1 vận hành thường; tháng 2: ladder tạo ở unlock 0.714, bị bullish
    invalidation (giá +13% hai daily close) → release, rồi OSCORE tụt về 40.
    Theo ST §6: HWM giữ peak 0.714; NO_HWM bám 0.143; DECAY_HWM tụt bậc 0.10/7 ngày.
    Chứng minh: (i) unlock path ba mode PHÂN KỲ trên engine run thật;
    (ii) smart_reservable — quyền vốn còn lại của tháng — cho BA GIÁ TRỊ KHÁC NHAU
    đúng thứ tự semantics (HWM > DECAY_HWM > NO_HWM), và HWM > 0.
    BEFORE fix: mọi mode đều 0 (dimension mechanically dead từ tháng 2)."""
    days = month_days(31, oscore=60.0)              # tháng 1 bình thường
    days += month_days(2, oscore=60.0)              # tháng 2: ladder tạo nến đầu (0.714)
    days += [{"price": 113.0}, {}]                  # 2 daily close > invalidation 112
    days += [{"oscore": 40.0, "price": 100.0}]      # OSCORE tụt -> unlock 0.143
    days += [{} for _ in range(13)]                 # decay chạy qua >= 2 bậc 7 ngày

    out = {}
    for mode in ("HWM", "NO_HWM", "DECAY_HWM"):
        res, rec, path = _run_mode(mode, days, monkeypatch)
        smart = rec.pool("SMART")
        # ladder tháng 2 phải tồn tại và đã INVALIDATED (release về quyền tháng 2)
        lads2 = [l for l in rec.ladders if l.type == "SMART"]
        assert len(lads2) == 2, f"{mode}: tháng 2 phải tạo được ladder (F-035)"
        assert lads2[1].status == "INVALIDATED"
        eff_final = path[-1][2]
        out[mode] = {
            "eff_path": path,
            "eff_final": eff_final,
            "reservable_final": smart_reservable(smart, 30.0, eff_final),
            "month_deployed": smart.month_deployed,
        }

    # (i) unlock path phân kỳ thật sau ngày OSCORE tụt
    finals = {m: out[m]["eff_final"] for m in out}
    assert finals["HWM"] == pytest.approx(25.0 / 35.0)          # giữ peak 0.714
    assert finals["NO_HWM"] == pytest.approx(5.0 / 35.0)        # bám 0.143
    assert finals["NO_HWM"] < finals["DECAY_HWM"] < finals["HWM"]   # decay ở giữa
    # (ii) quyền vốn còn lại phân kỳ — dimension không còn mechanically dead
    r = {m: out[m]["reservable_final"] for m in out}
    assert r["HWM"] > r["DECAY_HWM"] > r["NO_HWM"] >= 0.0
    assert r["HWM"] > 1.0, f"HWM phải còn quyền dương rõ rệt ở tháng 2, được {r['HWM']}"


def test_c2_month_reset_no_peak_carryover(monkeypatch):
    """CHECK-A7-04: peak KHÔNG mang qua tháng — tháng 1 oscore 80 (peak 1.0),
    tháng 2 oscore 45 (unlock 0.2857): eligible ladder tháng 2 phải theo 0.2857,
    không phải 1.0, ở CẢ BA mode (ST §6: 'Peak reset khi sang accounting month mới').

    Nến đầu tháng 2 vẫn dùng daily score cuối tháng 1 (oscore 80) tới 07:00 nên chặn
    tạo ladder sớm bằng dq INVALID cho đúng ngày đầu tháng 2."""
    days = month_days(30, oscore=80.0)
    days += [{"dq": "INVALID"}]                       # ngày 31/3: score carry sang 00:00 1/4 bị chặn
    days += [{"oscore": 45.0, "dq": "GOOD"}]          # ngày 1 tháng 4: unlock(45) từ 07:00 ngày 2
    days += [{} for _ in range(8)]
    for mode in ("HWM", "NO_HWM", "DECAY_HWM"):
        res, rec, _ = _run_mode(mode, days, monkeypatch)
        lads = [l for l in rec.ladders if l.type == "SMART"]
        assert len(lads) == 2, mode
        assert lads[1].eligible_capital_vnd == pytest.approx(30.0 * (10.0 / 35.0), rel=1e-6), \
            f"{mode}: eligible tháng 2 phải theo unlock(45)=0.2857 — peak tháng 1 không được mang qua"


# ---------------------------------------------------------------- D — CHECK-A7-07 (guard)


def test_d_opportunity_fund_stays_cumulative():
    """Opportunity Fund là quỹ XUYÊN THÁNG (ST §7): fix Smart không được biến nó
    thành reset theo tháng. Guard hai phía (PASS cả trước lẫn sau fix)."""
    cfg = BASELINE_STRATEGY
    mc = MonthlyCapital(Pool("BASE"), Pool("SMART"), Pool("OPP_FUND"),
                        monthly_opp_contribution=20.0, opportunity_cap_months=4)
    for _ in range(5):
        r = apply_monthly_contribution(mc, 100.0, cfg)
    fund = mc.opportunity_fund
    assert fund.total == pytest.approx(80.0)                       # cap 4 tháng, luỹ kế
    assert r["opportunity_overflow_to_smart"] == pytest.approx(20.0)
    # opportunity_reservable giữ ngữ nghĩa LIFETIME: deployed luỹ kế vẫn trừ unlock
    fund.reserve(10.0, "OPPORTUNITY_O1")
    fund.deploy_from_reserved(10.0, "OPPORTUNITY_O1")
    assert opportunity_reservable(fund, 0.3, True, 0.0, 0.20) == pytest.approx(
        min(fund.available, 80.0 * 0.3 - 0.0 - 10.0))
    assert opportunity_reservable(fund, 0.6, True, 15.0, 0.20) == pytest.approx(
        min(fund.available, 80.0 * 0.6 - 10.0, 80.0 * 0.2 - 15.0))


# ---------------------------------------------------------------- E — CHECK-A7-05


def test_e_month_end_transition(monkeypatch):
    """Month-End ST §10 và ranh giới đóng/mở sổ: tháng 1 kết thúc với OSCORE < 45
    (mua 50% phần Smart còn lại, chuyển 50% sang Opportunity Fund trong cap);
    tháng 2: ngân sách mới, unlock mới — deployment/transfer cuối tháng 1 KHÔNG
    bóp quyền unlock tháng 2."""
    days = month_days(27, oscore=60.0)
    days += [{"oscore": 40.0}]                        # ngày 28/3 — active 07:00 CÙNG ngày -> Day-28 settle thấy 40
    days += [{"oscore": 60.0}] + [{} for _ in range(2)]   # ngày 29..31 — carry sang 00:00 1/4 là 60
    days += month_days(30, oscore=60.0)               # tháng 4/2023 = 30 ngày
    res, rec = run_case(days, monkeypatch)
    smart, opp = rec.pool("SMART"), rec.pool("OPPORTUNITY")
    # Month-End: có MONTH_END_SMART deploy và có chuyển sang Opportunity Fund
    assert any(p["reason"] == "MONTH_END_SMART" for p in res.purchases)
    assert any(e["entry_type"] == "OVERFLOW_OUT" and e["reason_code"] == "MONTH_END_SMART"
               for e in smart.ledger), "OSCORE<45: 50% phần Smart còn lại phải sang Opp Fund"
    assert any(e["entry_type"] == "OVERFLOW_IN" and e["reason_code"] == "MONTH_END_SMART"
               for e in opp.ledger)
    # tháng 2 vẫn tạo ladder với eligible đúng theo budget tháng 2 × unlock(60)
    smart_lads = [l for l in rec.ladders if l.type == "SMART"]
    assert len(smart_lads) == 2
    assert smart_lads[1].eligible_capital_vnd == pytest.approx(30.0 * (25.0 / 35.0), rel=1e-6)
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert ledger_conservation_ok(rec.pool(name))


# ---------------------------------------------------------------- F — CHECK-A7-06/02


def _replay_month_scope(pool):
    """Reconcile CHECK-A7-02/06: dựng lại (carry, month_reserved, month_deployed) CHỈ từ
    ledger + quy tắc carry-first (CONVENTIONS #17), mốc mở sổ = các entry CONTRIBUTION
    reason CONTRIBUTION (rollover). Trả về bộ ba cuối để so với counters của Pool."""
    carry = month_res = month_dep = 0.0
    reserved = 0.0
    seen_open_ts = set()
    for e in pool.ledger:
        if e["entry_type"] == "CONTRIBUTION" and e["reason_code"] == "CONTRIBUTION" \
                and e["timestamp"] not in seen_open_ts:
            seen_open_ts.add(e["timestamp"])
            carry, month_res, month_dep = reserved, 0.0, 0.0
        t, a = e["entry_type"], e["amount"]
        if t == "RESERVE":
            reserved += a
            month_res += a
        elif t == "RELEASE":
            reserved -= a
            take = min(a, carry)
            carry -= take
            month_res = max(0.0, month_res - (a - take))
        elif t == "DEPLOY":
            # DEPLOY từ reserved hay từ available? — suy từ reserved_after
            if abs(e["reserved_after"] - (reserved - a)) < 1e-6:
                reserved -= a
                take = min(a, carry)
                carry -= take
                rest = a - take
                month_res = max(0.0, month_res - rest)
                month_dep += rest
            else:
                month_dep += a
    return carry, month_res, month_dep


def test_f_invariants_multimonth_with_crash_spanning_boundary(monkeypatch):
    """Bất biến vốn qua BA tháng có crash episode VẮT RANH GIỚI THÁNG (carry-reserve):
    TOTAL = A+R+D tại mọi entry, không âm, không mất/tạo vốn, không reserve mồ côi;
    lịch sử ledger lifetime giữ nguyên; month counters reconcile được từ ledger
    (derive deterministic — CHECK-A7-02)."""
    days = month_days(28, oscore=60.0)
    # cuối tháng 1: vào CRASH (ngày 29), exit-candidate 2 ngày cuối, recovery vắt sang tháng 2
    days += [{"oscore": 80.0, "return7": -0.16, "price": 100.5},
             {"oscore": 50.0, "return7": -0.05}, {}]
    days += [{}]                                    # tháng 2 ngày 1: RECOVERY bắt đầu ~ngày này
    days += [{"return7": -0.02}, {}, {}]            # recovery hết trong tháng 2 -> release carry
    days += [{} for _ in range(24)]                 # phần còn lại tháng 2
    days += month_days(31, oscore=60.0)             # tháng 3 bình thường
    res, rec = run_case(days, monkeypatch)

    total_all = 0.0
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        pool = rec.pool(name)
        assert ledger_conservation_ok(pool), f"ledger {name} không tự hoà"
        assert pool.available >= -1e-9 and pool.reserved >= -1e-9 and pool.deployed >= -1e-9
        total_all += pool.total
    assert total_all == pytest.approx(res.contributed_total)      # không tạo/mất vốn

    open_zone = sum(z.reserved_vnd for l in rec.ladders for z in l.zones
                    if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    pool_reserved = sum(rec.pool(n).reserved for n in ("BASE", "SMART", "OPPORTUNITY"))
    assert pool_reserved == pytest.approx(open_zone, abs=1e-6)    # không double/mồ côi

    # crash episode có thật và có carry vắt tháng
    assert rec.crash_ladders(), "kịch bản phải tạo crash ladder"
    # reconcile month counters từ ledger (derive deterministic)
    smart = rec.pool("SMART")
    carry, m_res, m_dep = _replay_month_scope(smart)
    assert smart.carry_reserved == pytest.approx(carry, abs=1e-6)
    assert smart.month_reserved == pytest.approx(m_res, abs=1e-6)
    assert smart.month_deployed == pytest.approx(m_dep, abs=1e-6)
    # tháng 3 vẫn tạo ladder (không suy biến sau crash + carry)
    smart_lads = [l for l in rec.ladders if l.type == "SMART"]
    assert len(smart_lads) >= 3
