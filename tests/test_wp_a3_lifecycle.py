"""WP-A3 — Regime & vòng đời Crash ladder (đóng F-001, F-021, F-022, F-030).

Bám trực tiếp các REQUIRED check trong docs/tasks/WP-A3-regime-va-vong-doi-ladder.md:
  CHECK-A3-01  CRASH -> RECOVERY -> STRESSED giải phóng hết reserve (ST §18.3)
  CHECK-A3-02  mọi trạng thái ladder có đường kết thúc giải phóng reserve
  CHECK-A3-03  [F1] STRESSED không có hiệu ứng trên 5 bề mặt (ST §17.3)
  CHECK-A3-04  regime không thoát CRASH trên dữ liệu thiếu (BT §1, ST §3)
  CHECK-A3-05  snapshot [F5] không bị daily limit thu nhỏ; daily limit cưỡng chế ở
               khâu triển khai (ST §14, §15)
  CHECK-A3-06  pool label Crash zone theo nguồn vốn thật; tie-break §15.1 [F2]
  CHECK-A3-07  bất biến kế toán qua toàn bộ vòng đời mới, multi-transition

Các test này được viết TRƯỚC khi sửa code (test-first). Trạng thái FAIL của chúng trên
HEAD trước remediation là baseline; xem docs/sessions/S003-wp-a3-regime-ladder.md.
"""
import itertools

import pandas as pd
import pytest

import eth_dca_os.ladders as ladders_mod
from eth_dca_os.config import BASELINE_STRATEGY
from eth_dca_os.regime import RegimeTracker
from wp_a3_harness import ledger_conservation_ok, run_case

H = 3600.0

_SYNTH_CACHE = {}


def _synth_dir():
    """Thư mục dataset tổng hợp dùng riêng cho test dài của WP-A3 (ngoài repo)."""
    import tempfile
    from pathlib import Path
    if "dir" not in _SYNTH_CACHE:
        _SYNTH_CACHE["dir"] = Path(tempfile.mkdtemp(prefix="wp_a3_synth_"))
    return _SYNTH_CACHE["dir"]


@pytest.fixture(autouse=True)
def _reset_ladder_ids(monkeypatch):
    """Reset id sequence để hai run trong cùng test so sánh được id với nhau."""
    monkeypatch.setattr(ladders_mod, "_ladder_seq", itertools.count(1))
    monkeypatch.setattr(ladders_mod, "_zone_seq", itertools.count(1))


def scenario_f001(entry_oscore=80.0):
    """Sập sâu -> hồi một phần -> vẫn yếu: CRASH -> RECOVERY -> hết 72h -> STRESSED.

    Day 5 07:00 local: oscore cao + Return7D -16% -> CRASH; snapshot lúc đó:
    smart 30 (unlock 1.0), opp fund 20 với o_unl tuỳ entry_oscore.
    Day 8 ~07:00: đủ 48h exit -> RECOVERY. Day 11 ~07:00: hết 72h Recovery
    trong khi Return7D = -11% (<= -10%) -> nhãn STRESSED.
    """
    return [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {}, {}, {},
        {"oscore": entry_oscore, "return7": -0.16, "price": 100.5},
        {"oscore": 50.0, "return7": -0.05},
        {},
        {},
        {"return7": -0.08},
        {},
        {"return7": -0.11},
        {}, {}, {},
    ]


# ---------------------------------------------------------------- CHECK-A3-01


def test_check_a3_01_crash_recovery_stressed_releases_reserve(monkeypatch):
    """F-001: kết thúc Recovery vào STRESSED vẫn phải CANCEL crash zone + release reserve."""
    res, rec = run_case(scenario_f001(), monkeypatch)

    # tiền đề kịch bản: đúng chuỗi nhãn NORMAL -> CRASH -> RECOVERY -> STRESSED
    labels = [(a, b) for _, a, b in rec.transitions]
    assert ("NORMAL", "CRASH") in labels
    assert ("CRASH", "RECOVERY") in labels
    assert ("RECOVERY", "STRESSED") in labels
    tracker = rec.trackers[0]
    assert tracker.regime == "STRESSED"

    # ST §18.3: sau 72h Recovery, crash zone chưa hit phải CANCEL và release reserve
    lads = rec.crash_ladders()
    assert len(lads) == 1
    lad = lads[0]
    assert lad.status == "CANCELLED"
    for z in lad.zones:
        assert z.status in ("EXECUTED", "CANCELLED")

    smart, opp = rec.pool("SMART"), rec.pool("OPPORTUNITY")
    # crash zone không được giữ lại một đồng reserve nào
    open_reserve = sum(z.reserved_vnd for l in lads for z in l.zones
                       if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    assert open_reserve == pytest.approx(0.0, abs=1e-9)
    # không reserve mồ côi: reserve của pool = tổng reserve các zone còn mở (mọi ladder);
    # (sau khi release, engine được phép tạo ladder MỚI bằng vốn vừa giải phóng — đó là
    # chính hành vi "vốn không còn bị khoá" mà spec đòi, nên không assert reserved == 0)
    open_all = sum(z.reserved_vnd for l in rec.ladders for z in l.zones
                   if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    assert smart.reserved + opp.reserved + rec.pool("BASE").reserved == \
        pytest.approx(open_all, abs=1e-6)

    # reason + timestamp: release mang reason RECOVERY_END đúng tại tick kết thúc recovery
    rec_end_ts = [ts for ts, a, b in rec.state_transitions if a == "RECOVERY" and b == "NORMAL"]
    assert len(rec_end_ts) == 1
    smart_releases = [e for e in smart.ledger
                      if e["entry_type"] == "RELEASE" and e["reason_code"] == "RECOVERY_END"]
    assert smart_releases, "phải có release reserve với reason RECOVERY_END ở pool SMART"
    assert all(e["timestamp"] == rec_end_ts[0] for e in smart_releases)
    # đúng lượng vốn crash đã giữ phải quay về: tổng release RECOVERY_END = tổng reserve CRASH_ZONE
    # trừ phần đã deploy qua fill (nếu có)
    crash_reserved = sum(a for n, a, r, _ in rec.reserves if r == "CRASH_ZONE")
    crash_deployed = sum(e["amount"] for p in (smart, opp) for e in p.ledger
                         if e["entry_type"] == "DEPLOY" and e["reason_code"] == "CRASH_ZONE")
    released = sum(e["amount"] for p in (smart, opp) for e in p.ledger
                   if e["entry_type"] == "RELEASE" and e["reason_code"] == "RECOVERY_END")
    assert released == pytest.approx(crash_reserved - crash_deployed, abs=1e-6)

    # ledger bảo toàn qua toàn bộ chuỗi
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert ledger_conservation_ok(rec.pool(name))


def test_check_a3_01_reentry_then_clean_end_releases_everything(monkeypatch):
    """Multi-transition + multi-episode:
    CRASH#1 -> RECOVERY -> re-enter CRASH#2 -> RECOVERY -> NORMAL (tháng 1), rồi
    CRASH#3 -> RECOVERY -> NORMAL (tháng 2, contribution mới).

    Kỳ vọng: ladder #1 sống qua re-entry (vốn đang reserve không được đếm lại vào
    snapshot mới theo [F5] — snapshot lần re-enter = 0 nên KHÔNG có ladder thứ hai
    trong tháng 1), và được CANCEL + release ở recovery-end cuối của episode;
    ladder #2 của tháng 2 cũng đóng sạch. Không reserve mồ côi ở bất kỳ pool nào."""
    quiet = {"oscore": 50.0, "return7": -0.02}
    days = [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {}, {}, {},
        {"oscore": 80.0, "return7": -0.16, "price": 100.5},   # Day 5: CRASH #1
        {"oscore": 50.0, "return7": -0.05},                    # Day 6..7: exit candidate 48h
        {},
        {},                                                    # Day 8: RECOVERY #1
        {"oscore": 80.0, "return7": -0.16},                    # Day 9: re-enter CRASH #2
        {"oscore": 50.0, "return7": -0.05},                    # Day 10..11: exit candidate
        {},
        {},                                                    # Day 12: RECOVERY #2
        {"return7": -0.02}, {},                                # Day 13..14: thị trường ổn
        {"return7": -0.02},                                    # Day 15: hết 72h -> NORMAL
    ]
    days += [dict(quiet) for _ in range(17)]                   # Day 16..32 (sang tháng 4)
    days += [
        {"oscore": 80.0, "return7": -0.16},                    # Day 33: CRASH #3 (tháng mới)
        {"oscore": 50.0, "return7": -0.05},                    # Day 34..35: exit candidate
        {},
        {},                                                    # Day 36: RECOVERY
        {"return7": -0.02}, {},                                # Day 37..38
        {"return7": -0.02},                                    # Day 39: hết 72h -> NORMAL
        {}, {},
    ]
    res, rec = run_case(days, monkeypatch)
    tracker = rec.trackers[0]
    assert tracker.regime == "NORMAL"
    state_seq = [(a, b) for _, a, b in rec.state_transitions]
    assert state_seq.count(("RECOVERY", "CRASH")) == 1     # re-entry có xảy ra (tháng 1)
    assert state_seq.count(("NORMAL", "CRASH")) == 2       # hai episode vào từ NORMAL

    lads = rec.crash_ladders()
    # tháng 1: một ladder duy nhất (re-entry không tạo ladder mới vì snapshot [F5] = 0
    # khi toàn bộ vốn còn nằm trong reservation của ladder cũ); tháng 2: một ladder mới
    assert len(lads) == 2
    for lad in lads:
        assert lad.status in ("CANCELLED", "COMPLETED")
        open_reserve = sum(z.reserved_vnd for z in lad.zones
                           if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
        assert open_reserve == pytest.approx(0.0, abs=1e-9)
    # ladder #1 được dọn đúng tại recovery-end CUỐI của episode 1 (không phải khi re-enter)
    rec_ends = [ts for ts, a, b in rec.state_transitions if (a, b) == ("RECOVERY", "NORMAL")]
    assert len(rec_ends) == 2
    releases_1 = [e for n in ("SMART", "OPPORTUNITY") for e in rec.pool(n).ledger
                  if e["entry_type"] == "RELEASE" and e["reason_code"] == "RECOVERY_END"
                  and e["timestamp"] == rec_ends[0]]
    assert releases_1, "reserve của ladder #1 phải được release tại recovery-end thứ nhất"

    # không reserve mồ côi sau chuỗi multi-transition
    open_all = sum(z.reserved_vnd for l in rec.ladders for z in l.zones
                   if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    total_reserved = sum(rec.pool(n).reserved for n in ("BASE", "SMART", "OPPORTUNITY"))
    assert total_reserved == pytest.approx(open_all, abs=1e-6)
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert ledger_conservation_ok(rec.pool(name))


# ---------------------------------------------------------------- CHECK-A3-04


def test_check_a3_04_none_does_not_exit_crash():
    """F-022: None không phải bằng chứng thoả điều kiện exit (BT §1 — giả định bảo thủ)."""
    t = RegimeTracker()
    t.update(0.0, -0.20, -0.12, 80.0)
    assert t.regime == "CRASH"
    t.update(1 * H, None, None, None)
    t.update(25 * H, None, None, None)
    t.update(49 * H, None, None, None)
    t.update(73 * H, None, None, None)
    assert t.regime == "CRASH", "toàn bộ input None mà vẫn rời CRASH là dùng dữ liệu giả"


def test_check_a3_04_partial_none_does_not_exit_crash():
    # thiếu Return7D — dù Return24H khỏe cũng không đủ bằng chứng (điều kiện exit là AND)
    t = RegimeTracker()
    t.update(0.0, -0.20, -0.12, 80.0)
    for h in (1, 25, 49):
        t.update(h * H, None, -0.02, 80.0)
    assert t.regime == "CRASH"
    # thiếu Return24H
    t2 = RegimeTracker()
    t2.update(0.0, -0.20, -0.12, 80.0)
    for h in (1, 25, 49):
        t2.update(h * H, -0.05, None, 80.0)
    assert t2.regime == "CRASH"


def test_check_a3_04_none_breaks_exit_continuity():
    """'liên tục trong 48h' (ST §17.2): một quan sát None ở giữa phá chuỗi liên tục."""
    t = RegimeTracker()
    t.update(0.0, -0.20, -0.12, 80.0)
    t.update(1 * H, -0.04, -0.02, 80.0)          # bắt đầu candidate tại 1h
    t.update(40 * H, -0.04, -0.02, 80.0)
    t.update(47 * H, None, None, 80.0)           # đứt chuỗi tại 47h
    t.update(49 * H, -0.04, -0.02, 80.0)         # restart candidate tại 49h
    assert t.regime == "CRASH"                    # 1h + 48h = 49h KHÔNG được exit vì đã đứt
    t.update(96 * H, -0.04, -0.02, 80.0)
    assert t.regime == "CRASH"                    # 49h + 47h — chưa đủ
    t.update(97 * H, -0.04, -0.02, 80.0)
    assert t.regime == "RECOVERY"                 # 49h + 48h — đủ 48h liên tục có dữ liệu


def test_check_a3_04_real_data_still_exits():
    """Chống over-blocking: dữ liệu thật thoả điều kiện vẫn exit đúng 48h (ST §17.2)."""
    t = RegimeTracker()
    t.update(0.0, -0.20, -0.12, 80.0)
    t.update(1 * H, -0.04, -0.02, 80.0)
    t.update(48 * H, -0.04, -0.02, 80.0)
    assert t.regime == "CRASH"
    t.update(49 * H, -0.04, -0.02, 80.0)
    assert t.regime == "RECOVERY"


def test_check_a3_04_none_does_not_enter_crash_or_stress():
    """Đối xứng: None không được tạo bằng chứng ENTER hay bằng chứng STRESSED;
    dữ liệu THẬT ở một vế của điều kiện OR thì vẫn có giá trị bằng chứng."""
    t = RegimeTracker()
    assert t.update(0.0, None, None, None) == "NORMAL"       # không dữ liệu -> không bằng chứng gì
    assert t.update(1 * H, None, None, 80.0) == "NORMAL"     # thiếu return -> không entry
    # r24 = -12% là dữ liệu THẬT: thiếu OSCORE nên không entry, nhưng nhãn STRESSED đúng spec
    assert t.update(2 * H, None, -0.12, None) == "STRESSED"
    # một input return có thật + OSCORE đủ -> entry qua nhánh 24H
    assert t.update(3 * H, None, -0.12, 80.0) == "CRASH"


# ---------------------------------------------------------------- CHECK-A3-05


def test_check_a3_05_f5_snapshot_not_shrunk_by_daily_limit(monkeypatch):
    """F-021: snapshot [F5] = Smart AVAILABLE + Opportunity AVAILABLE (đã unlock,
    chưa reserve) — KHÔNG áp daily limit 20% (ST §14)."""
    res, rec = run_case(scenario_f001(entry_oscore=80.0), monkeypatch)
    lads = rec.crash_ladders()
    assert len(lads) == 1
    # smart 30 (unlock 1.0, chưa reserve) + opp 20 * 0.6*clamp((80-65)/30)=0.3 -> 6
    assert lads[0].eligible_capital_vnd == pytest.approx(36.0)
    # allocation C0..C3 áp đúng trên snapshot
    for z, alloc in zip(lads[0].zones, (0.20, 0.25, 0.25, 0.30)):
        assert z.target_vnd == pytest.approx(36.0 * alloc)


def test_check_a3_05_daily_limit_blocks_above_boundary(monkeypatch):
    """VƯỢT boundary: phần vốn Opportunity của crash zone (6) > headroom ngày (4)
    -> DAILY_LIMIT_BLOCK ở khâu triển khai, zone giữ TRIGGERED, không có fill CRASH;
    reserve được giải phóng đủ khi recovery kết thúc (không tạo kênh khoá vốn mới)."""
    res, rec = run_case(scenario_f001(entry_oscore=80.0), monkeypatch)
    lads = rec.crash_ladders()
    assert len(lads) == 1
    crash_buys = [p for p in res.purchases if p["source"] == "CRASH"]
    assert crash_buys == [], "C0 có 6 đơn vị vốn Opportunity > daily headroom 4 nên không được fill"
    blocks = [d for d in res.decision_log if d["reason_code"] == "DAILY_LIMIT_BLOCK"]
    assert blocks, "phải log DAILY_LIMIT_BLOCK (ST §20) khi daily limit chặn deployment"
    # zone bị chặn không mất trạng thái ngay; tới recovery-end thì cancel + release đủ
    assert lads[0].status == "CANCELLED"
    open_crash = sum(z.reserved_vnd for z in lads[0].zones
                     if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    assert open_crash == pytest.approx(0.0, abs=1e-9)
    released = sum(e["amount"] for n in ("SMART", "OPPORTUNITY")
                   for e in rec.pool(n).ledger
                   if e["entry_type"] == "RELEASE" and e["reason_code"] == "RECOVERY_END")
    assert released == pytest.approx(36.0)   # toàn bộ snapshot quay về vì không zone nào fill


def test_check_a3_05_daily_limit_allows_at_boundary(monkeypatch):
    """ĐÚNG boundary: oscore 75 -> o_unl = 0.2 -> phần Opportunity của C0 = 4 == headroom 4
    -> được phép triển khai (limit là 'tối đa', chạm đúng ngưỡng không bị chặn)."""
    res, rec = run_case(scenario_f001(entry_oscore=75.0), monkeypatch)
    lads = rec.crash_ladders()
    assert len(lads) == 1
    # snapshot = smart 30 + opp 20*0.2 = 34; C0 = 6.8 (opp 4 + smart 2.8)
    assert lads[0].eligible_capital_vnd == pytest.approx(34.0)
    crash_buys = [p for p in res.purchases if p["source"] == "CRASH"]
    assert len(crash_buys) == 1 and crash_buys[0]["reason"] == "CRASH_ZONE_0"
    assert crash_buys[0]["nominal"] == pytest.approx(6.8)


def test_check_a3_05_daily_limit_allows_below_boundary(monkeypatch):
    """DƯỚI boundary: opportunity_pct 0.30 (level Gate 2 hợp lệ) -> fund 30, headroom 6,
    phần Opportunity của C0 = 5.2 < 6 -> triển khai bình thường."""
    cfg = BASELINE_STRATEGY.with_(opportunity_pct=0.30)   # smart_pct tự derive = 0.20
    res, rec = run_case(scenario_f001(entry_oscore=75.0), monkeypatch, strategy_cfg=cfg)
    lads = rec.crash_ladders()
    assert len(lads) == 1
    # snapshot = smart 20 + opp 30*0.2 = 26; C0 = 5.2 (opp 5.2 vì opp-first, avail opp = 6)
    assert lads[0].eligible_capital_vnd == pytest.approx(26.0)
    crash_buys = [p for p in res.purchases if p["source"] == "CRASH"]
    assert len(crash_buys) == 1
    assert crash_buys[0]["nominal"] == pytest.approx(5.2)


# ---------------------------------------------------------------- CHECK-A3-06


def test_check_a3_06_pool_label_reflects_funding(monkeypatch):
    """F-030: crash ladder lấy 30/36 từ SMART -> pool label các zone phải là SMART
    (pool nguồn vốn chiếm đa số), không phải OPPORTUNITY mặc định."""
    res, rec = run_case(scenario_f001(entry_oscore=80.0), monkeypatch)
    lad = rec.crash_ladders()[0]
    crash_reserves = [(n, a) for n, a, r, _ in rec.reserves if r == "CRASH_ZONE"]
    smart_funded = sum(a for n, a in crash_reserves if n == "SMART")
    opp_funded = sum(a for n, a in crash_reserves if n == "OPPORTUNITY")
    assert smart_funded > opp_funded          # tiền đề kịch bản: SMART chiếm đa số
    for z in lad.zones:
        assert z.pool == "SMART"


def test_check_a3_06_pool_label_opportunity_majority(monkeypatch):
    """Ladder được cấp vốn đa số từ OPPORTUNITY thì giữ nhãn OPPORTUNITY."""
    cfg = BASELINE_STRATEGY.with_(opportunity_pct=0.30)   # opp fund lớn, smart_pct 0.20
    days = scenario_f001(entry_oscore=80.0)
    # thu nhỏ smart trước entry: Day 2 oscore 60 tạo smart ladder reserve trước phần lớn smart
    days[1] = {"oscore": 60.0}
    res, rec = run_case(days, monkeypatch, strategy_cfg=cfg)
    lad = rec.crash_ladders()[0]
    crash_reserves = [(n, a) for n, a, r, _ in rec.reserves if r == "CRASH_ZONE"]
    smart_funded = sum(a for n, a in crash_reserves if n == "SMART")
    opp_funded = sum(a for n, a in crash_reserves if n == "OPPORTUNITY")
    assert opp_funded > smart_funded
    for z in lad.zones:
        assert z.pool == "OPPORTUNITY"


def test_check_a3_06_tiebreak_order_crash_after_normal_same_pool():
    """§15.1 [F2] + F-030: thứ tự khoá sắp xếp — Base -> Smart -> Opportunity;
    crash ladder xếp theo pool NGUỒN VỐN, SAU ladder thường cùng pool;
    trong cùng pool created_at sớm hơn trước; trong cùng ladder zone_index tăng."""
    from eth_dca_os.engine import zone_order_key
    from eth_dca_os.ladders import Ladder, Zone

    def mk(zid, lid, idx, pool):
        return Zone(zone_id=zid, ladder_id=lid, zone_index=idx, target_price=1.0,
                    allocation_pct=0.5, target_vnd=1.0, pool=pool)

    smart_normal = Ladder(1, "SMART", 100.0, 0.05, created_at=1000.0, expires_at=None,
                          score_at_creation=50.0, eligible_capital_vnd=10.0)
    crash_smart = Ladder(2, "CRASH", 100.0, 0.07, created_at=500.0, expires_at=None,
                         score_at_creation=80.0, eligible_capital_vnd=10.0)
    opp_normal = Ladder(3, "OPPORTUNITY", 100.0, 0.06, created_at=100.0, expires_at=None,
                        score_at_creation=70.0, eligible_capital_vnd=10.0)

    z_s1 = mk(11, 1, 1, "SMART")
    z_c0 = mk(21, 2, 0, "SMART")          # crash zone cấp vốn từ SMART
    z_c1 = mk(22, 2, 1, "SMART")
    z_o0 = mk(31, 3, 0, "OPPORTUNITY")

    lad_by_id = {1: smart_normal, 2: crash_smart, 3: opp_normal}
    order = sorted([z_o0, z_c1, z_c0, z_s1], key=lambda z: zone_order_key(z, lad_by_id[z.ladder_id]))
    # smart thường trước crash-smart (dù crash tạo sớm hơn), crash-smart trước opportunity;
    # trong crash ladder: C0 trước C1
    assert [z.zone_id for z in order] == [11, 21, 22, 31]


# ---------------------------------------------------------------- CHECK-A3-03


def _strip_regime(purchases):
    return [{k: v for k, v in p.items() if k != "regime"} for p in purchases]


def test_check_a3_03_f1_stressed_no_effect_on_five_surfaces(monkeypatch):
    """[F1] ST §17.3 theo nghĩa đen: hai lần chạy giống hệt nhau, chỉ khác NHÃN STRESSED
    (một bên nhãn chuẩn, một bên ép STRESSED cho toàn bộ thời gian nền NORMAL).
    Cả năm bề mặt unlock / ladder / cooldown / limit / execution phải không đổi."""
    days = [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {"oscore": 55.0},                                    # Day 2: smart ladder + S0 fill
        {"low_dip": 94.0},                                   # Day 3: S1 trigger, đang cooldown
        {},                                                  # Day 4: cooldown hết -> S1 fill
        # Day 5: CRASH; low 91 xuyên cả C1 -> C0 tạo action (opp 3.77 <= headroom 4) rồi C1
        # bị DAILY_LIMIT_BLOCK (opp 2.23 > headroom còn lại 0.23); C1 fill lại Day 7 sau cooldown
        {"oscore": 80.0, "return7": -0.16, "price": 100.5, "low_dip": 91.0},
        {"oscore": 50.0, "return7": -0.05},
        {},
        {},                                                  # Day 8: RECOVERY
        {"return7": -0.08},
        {},
        {"return7": -0.11},                                  # Day 11: hết recovery -> STRESSED
        {}, {},
        {"return7": -0.02},                                  # Day 14: hết stress -> NORMAL
        {"oscore": 85.0},                                    # Day 15: opportunity ladder + O0 fill
        {"price": 93.0},                                     # Day 16: r24 -7% -> nhãn phân kỳ tiếp
        {}, {},
    ]

    def run(force_stressed: bool):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(ladders_mod, "_ladder_seq", itertools.count(1))
            mp.setattr(ladders_mod, "_zone_seq", itertools.count(1))
            if force_stressed:
                mp.setattr(RegimeTracker, "_derive_label",
                           lambda self, r7, r24: "STRESSED" if self.state == "NORMAL"
                           else self.state)
            return run_case(days, mp)

    res_a, rec_a = run(False)
    res_b, rec_b = run(True)

    # tiền đề 1: nhãn thực sự khác nhau giữa hai run (counterfactual có nghĩa)
    labels_a = {b for _, _, b in rec_a.transitions}
    labels_b = {b for _, _, b in rec_b.transitions}
    assert ("STRESSED" in labels_b) and (labels_a != labels_b or
                                         rec_a.transitions != rec_b.transitions)
    # trạng thái nền giống hệt nhau
    assert rec_a.state_transitions == rec_b.state_transitions
    # tiền đề 2 (chống kịch bản degenerate — bài học F-E2-01): cả năm bề mặt phải có
    # SỰ KIỆN THẬT trong run A để phép so sánh không rỗng
    assert any(p["source"] == "SMART" for p in res_a.purchases)          # unlock/ladder/fill
    assert any(p["source"] == "CRASH" for p in res_a.purchases)          # crash fill thật
    assert any(p["source"] == "OPPORTUNITY" for p in res_a.purchases)    # opportunity fill thật
    assert any(d["reason_code"] == "DAILY_LIMIT_BLOCK"
               for d in res_a.decision_log)                              # limit block thật
    assert res_a.counters["triggered_actions"] >= 4                      # cooldown giữ TRIGGERED
    assert {l.type for l in rec_a.ladders} == {"SMART", "CRASH", "OPPORTUNITY"}

    # 1) EXECUTION: mọi giao dịch identical (trừ trường nhãn reporting)
    assert _strip_regime(res_a.purchases) == _strip_regime(res_b.purchases)
    assert res_a.eth_total == res_b.eth_total

    # 2) LADDER: cùng số ladder, cùng loại/anchor/spacing/target/trạng thái cuối
    assert len(rec_a.ladders) == len(rec_b.ladders)
    for la, lb in zip(rec_a.ladders, rec_b.ladders):
        assert (la.type, la.anchor_price, la.spacing_pct, la.created_at,
                la.eligible_capital_vnd, la.status) == \
               (lb.type, lb.anchor_price, lb.spacing_pct, lb.created_at,
                lb.eligible_capital_vnd, lb.status)
        assert [(z.zone_index, z.target_price, z.target_vnd, z.status, z.pool)
                for z in la.zones] == \
               [(z.zone_index, z.target_price, z.target_vnd, z.status, z.pool)
                for z in lb.zones]

    # 3) UNLOCK (quyền dùng vốn -> thể hiện ở ledger RESERVE/DEPLOY từng pool)
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert rec_a.pool(name).ledger == rec_b.pool(name).ledger

    # 4) COOLDOWN: tổng số lần override không đổi (phân rã theo nhãn được phép đổi
    #    vì đó chính là reporting decomposition của BT §16)
    ca, cb = res_a.counters["cooldown_override"], res_b.counters["cooldown_override"]
    assert sum(ca.values()) == sum(cb.values())

    # 5) LIMIT: cùng số action bị tạo/miss/executed, cùng số DAILY_LIMIT_BLOCK
    for k in ("triggered_actions", "missed_actions", "executed_actions",
              "base_early", "delayed_data_fill"):
        assert res_a.counters[k] == res_b.counters[k]
    blocks_a = [d for d in res_a.decision_log if d["reason_code"] == "DAILY_LIMIT_BLOCK"]
    blocks_b = [d for d in res_b.decision_log if d["reason_code"] == "DAILY_LIMIT_BLOCK"]
    assert blocks_a == blocks_b

    # cash samples (định giá danh mục) identical
    assert res_a.cash_samples == res_b.cash_samples


# ---------------------------------------------------------------- CHECK-A3-07 / A3-02


def test_check_a3_07_accounting_invariants_multi_transition(monkeypatch):
    """Bảo toàn vốn qua chuỗi CRASH -> RECOVERY -> re-entry -> RECOVERY -> NORMAL,
    có cả fill, block, cancel: TOTAL = A + R + D tại mọi entry ledger, không âm,
    không double reservation (mọi RESERVE đều đi tới đúng một RELEASE hoặc DEPLOY)."""
    days = [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {"oscore": 60.0},                                     # smart ladder trước crash + S0 fill
        {"oscore": 70.0},                                     # opportunity ladder trước crash
        {},
        {"oscore": 80.0, "return7": -0.16, "price": 100.5},   # CRASH #1: cancel opp ladder
        {"oscore": 50.0, "return7": -0.05},                   #   -> release -> snapshot [F5]
        {"low_dip": 91.0},                                    # S1 + C1 trigger cùng nến
        {},                                                   # RECOVERY #1
        {"oscore": 80.0, "return7": -0.16},                   # re-enter CRASH #2
        {"oscore": 50.0, "return7": -0.05},
        {},
        {},                                                   # RECOVERY #2
        {"return7": -0.02}, {},
        {"return7": -0.02},                                   # NORMAL
        {}, {},
    ]
    res, rec = run_case(days, monkeypatch)

    # tiền đề (chống kịch bản degenerate): ca "chuyển Opportunity ladder sang Crash ladder"
    # phải THẬT SỰ xảy ra — có opp ladder trước crash, bị cancel + release tại crash entry
    assert any(l.type == "OPPORTUNITY" for l in rec.ladders)
    crash_entry_rel = [e for e in rec.pool("OPPORTUNITY").ledger
                       if e["entry_type"] == "RELEASE" and e["reason_code"] == "CRASH_ENTRY"]
    assert crash_entry_rel, "opportunity ladder phải bị cancel + release tại crash entry"
    assert any(p["source"] == "CRASH" for p in res.purchases)   # fill CRASH thật trong chuỗi

    for name in ("BASE", "SMART", "OPPORTUNITY"):
        pool = rec.pool(name)
        assert ledger_conservation_ok(pool), f"ledger {name} không tự hoà"
        assert pool.available >= -1e-9 and pool.reserved >= -1e-9 and pool.deployed >= -1e-9
        assert pool.total == pytest.approx(pool.available + pool.reserved + pool.deployed)

    # không double reservation: reserve đang mở đúng bằng tổng reserve của các zone mở
    open_zone_reserve = sum(
        z.reserved_vnd for lad in rec.ladders for z in lad.zones
        if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    total_pool_reserved = sum(rec.pool(n).reserved for n in ("BASE", "SMART", "OPPORTUNITY"))
    assert total_pool_reserved == pytest.approx(open_zone_reserve, abs=1e-6)

    # kết thúc ở NORMAL: không crash ladder nào còn giữ reserve
    assert rec.trackers[0].regime == "NORMAL"
    for lad in rec.crash_ladders():
        assert lad.status in ("CANCELLED", "COMPLETED")

    # bảo toàn tổng thể: contribution = A + R + D trên cả ba pool (không mất/tạo vốn)
    total_all = sum(rec.pool(n).total for n in ("BASE", "SMART", "OPPORTUNITY"))
    assert total_all == pytest.approx(res.contributed_total)


def test_check_a3_02_long_run_no_orphan_reserve(monkeypatch):
    """Chạy dài trên dữ liệu tổng hợp có chu kỳ crash: không tồn tại reserve mồ côi —
    reserve của pool luôn bằng tổng reserve các zone còn mở; mọi crash ladder đã qua
    recovery-end đều CANCELLED/COMPLETED; ladder terminal không giữ reserve."""
    from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
    from eth_dca_os.data.dataset import load_dataset
    from eth_dca_os.data.synth import generate
    from eth_dca_os.engine import run_engine
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores
    from wp_a3_harness import instrument

    raw = _synth_dir()
    if not (raw / "ETHUSDT_15m.parquet").exists():
        generate(raw, start="2018-01-01", end="2023-01-01")
    ds = load_dataset(raw)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = pd.concat([ind, compute_scores(ind)], axis=1)
    scores = scores.loc[:, ~scores.columns.duplicated()]

    rec = instrument(monkeypatch)
    run_engine(ds, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
               pd.Timestamp("2019-01-01"), pd.Timestamp("2023-01-01"))

    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert ledger_conservation_ok(rec.pool(name))

    open_zone_reserve = sum(
        z.reserved_vnd for lad in rec.ladders for z in lad.zones
        if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING"))
    total_pool_reserved = sum(rec.pool(n).reserved for n in ("BASE", "SMART", "OPPORTUNITY"))
    assert total_pool_reserved == pytest.approx(open_zone_reserve, abs=1e-6)

    # trạng thái terminal không giữ reserve
    for lad in rec.ladders:
        if lad.status in ("CANCELLED", "COMPLETED", "EXPIRED", "INVALIDATED"):
            assert sum(z.reserved_vnd for z in lad.zones
                       if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING")) \
                == pytest.approx(0.0, abs=1e-9)

    # nếu kết thúc ngoài CRASH/RECOVERY thì mọi crash ladder phải đã đóng
    if rec.trackers[0].state == "NORMAL":
        for lad in rec.crash_ladders():
            assert lad.status in ("CANCELLED", "COMPLETED")


# ---------------------------------------------------------------- state/label unit


def test_regime_state_label_separation():
    """Thiết kế A3.1: trạng thái nền (state) chỉ gồm NORMAL/CRASH/RECOVERY;
    STRESSED là nhãn dẫn xuất (label) và .regime trả về nhãn."""
    t = RegimeTracker()
    assert t.state == "NORMAL" and t.regime == "NORMAL"
    t.update(0.0, -0.11, 0.0, 40.0)
    assert t.state == "NORMAL" and t.regime == "STRESSED"
    t.update(1 * H, -0.20, -0.12, 80.0)
    assert t.state == "CRASH" and t.regime == "CRASH"
    t.update(2 * H, -0.04, -0.02, 80.0)
    t.update(2 * H + 48 * H, -0.04, -0.02, 80.0)
    assert t.state == "RECOVERY" and t.regime == "RECOVERY"
    # hết 72h recovery trong khi thị trường còn yếu: state NORMAL, label STRESSED
    t.update(2 * H + 48 * H + 72 * H, -0.11, -0.02, 50.0)
    assert t.state == "NORMAL" and t.regime == "STRESSED"
