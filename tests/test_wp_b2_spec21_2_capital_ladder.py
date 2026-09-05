"""WP-B2 — Backtest §21.2 (Capital và ladder): những requirement CHƯA CÓ TEST.

Mỗi test dưới đây bắt đầu từ MỘT CÂU trong `docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §21.2
(hoặc câu §19/ST mà §21.2 dẫn chiếu), không bắt đầu từ một hàm trong `engine.py` — đó là
rủi ro đặc trưng mà chính task file của WP-B2 cảnh báo: test mô tả hành vi hiện tại thì
luôn PASS và không bảo vệ gì cả.

Phạm vi (§21.2, phần `S001-audit-findings.md` đánh dấu NOT TESTED):

  CHECK-B2-01  Base execute sớm không lặp lại ngày gốc
               Month-End Day 25–27 và Day 28
               Crash eligible-capital snapshot [F5] đo SAU cancel/release
  CHECK-B2-02  Không double reservation giữa Smart / Opportunity / Crash ở TẦNG ENGINE,
               kể cả ca chuyển Opportunity ladder sang Crash ladder

Những mục §21.2 khác đã có test ở gói trước được liệt kê trong bảng đối chiếu
`docs/CONVENTIONS.md` § "Đối chiếu requirement Backtest §21 → test" — không viết lại lần hai.

Gói này KHÔNG sửa `src/eth_dca_os/`. Một test đỏ ở đây là FINDING, không phải lý do sửa mã.
"""
from __future__ import annotations

import pytest

from eth_dca_os.capital import BASE_SCHEDULE
from eth_dca_os.score import opportunity_unlock
from wp_b2_probe import financial_payload, local_parts, run_case

# Ngân sách một tháng ở contribution danh nghĩa 100 (ST §4: base 50%, smart 30%, opp 20%).
CONTRIB = 100.0
MONTH_BASE_BUDGET = CONTRIB * 0.50          # 50
TRANCHE = tuple(MONTH_BASE_BUDGET * pct for _, pct in BASE_SCHEDULE)   # (20, 15, 15)


def _base_buys(res):
    return [p for p in res.purchases if p["source"] == "BASE"]


# ===================================================================== CHECK-B2-01
# §21.2 — "Lịch Base Day 3/13/23; Base execute sớm không lặp lại ngày gốc"


def test_b2_01a_base_advance_does_not_repeat_the_original_scheduled_day(monkeypatch):
    """ST §9 / §21.2: tranche được kéo sớm thì NGÀY GỐC của nó không được chạy lại.

    Kịch bản: OSCORE 75 có hiệu lực từ 07:00 Day 1 -> engine kéo sớm tranche Day 3 ngay
    hôm đó. Ngày 3 12:00 local là ngày gốc của chính tranche đó; nếu ngày gốc lặp lại thì
    tháng sẽ giải ngân 70 thay vì 50 (chi vượt ngân sách Base một tranche).

    Đối chứng chạy cùng dataset với OSCORE 20 (không kéo sớm) để chứng minh phép so không
    rỗng: ở đó ngày gốc CÓ chạy và mang đúng số tiền của tranche đầu.
    """
    early_days = [{"price": 100.0, "oscore": 75.0, "return7": 0.0},
                  {"oscore": 20.0}] + [{} for _ in range(26)]
    control_days = [{"price": 100.0, "oscore": 20.0, "return7": 0.0}] + [{} for _ in range(27)]

    res_early, _ = run_case(early_days, monkeypatch, contribution=CONTRIB)
    res_ctl, _ = run_case(control_days, monkeypatch, contribution=CONTRIB)

    early = [p for p in res_early.purchases if p["reason"] == "BASE_ADVANCE_SCORE"]
    assert len(early) == 1, f"kỳ vọng đúng một tranche kéo sớm, có {len(early)}"
    assert early[0]["nominal"] == pytest.approx(TRANCHE[0])
    assert local_parts(early[0]["ts"]) == (1, 7, 0), "kéo sớm tại nến snapshot daily mới"
    assert res_early.counters["base_early"] == 1

    # NGÀY GỐC (Day 3 12:00) không lặp lại trong run kéo sớm...
    day3_early = [p for p in _base_buys(res_early) if local_parts(p["ts"])[0] == 3]
    assert day3_early == [], f"ngày gốc Day 3 bị chạy lại: {day3_early}"
    # ...nhưng CÓ chạy trong đối chứng, với đúng số tiền của tranche đầu (phép so không rỗng)
    day3_ctl = [p for p in _base_buys(res_ctl) if local_parts(p["ts"])[0] == 3]
    assert len(day3_ctl) == 1 and day3_ctl[0]["reason"] == "BASE_SCHEDULE"
    assert day3_ctl[0]["nominal"] == pytest.approx(TRANCHE[0])

    # Bảo toàn: cả hai đường đi giải ngân ĐÚNG ngân sách Base của tháng, không hơn không kém.
    for res in (res_early, res_ctl):
        assert sum(p["nominal"] for p in _base_buys(res)) == pytest.approx(MONTH_BASE_BUDGET)
    # và đúng ba tranche theo lịch Day 3/13/23
    assert sorted(round(p["nominal"], 9) for p in _base_buys(res_early)) == \
           sorted(round(v, 9) for v in TRANCHE)


def test_b2_01b_base_advance_at_most_one_tranche_per_new_daily_score(monkeypatch):
    """ST §9: kéo sớm bám vào snapshot daily mới; một snapshot chỉ kéo được MỘT tranche.

    OSCORE giữ 75 suốt ba ngày đầu -> ba tranche được kéo sớm, mỗi ngày một tranche, và
    không ngày gốc nào (3/13/23) chạy lại.
    """
    days = [{"price": 100.0, "oscore": 75.0, "return7": 0.0}] + [{} for _ in range(27)]
    res, _ = run_case(days, monkeypatch, contribution=CONTRIB)

    early = [p for p in res.purchases if p["reason"] == "BASE_ADVANCE_SCORE"]
    assert len(early) == len(BASE_SCHEDULE) == 3
    assert [local_parts(p["ts"]) for p in early] == [(1, 7, 0), (2, 7, 0), (3, 7, 0)]
    assert [round(p["nominal"], 9) for p in early] == [round(v, 9) for v in TRANCHE]
    assert [p for p in _base_buys(res) if p["reason"] == "BASE_SCHEDULE"] == []
    assert sum(p["nominal"] for p in _base_buys(res)) == pytest.approx(MONTH_BASE_BUDGET)


# §21.2 — "Month-End Day 25–27 và Day 28"


def test_b2_01c_month_end_day25_settles_half_and_day28_settles_the_rest(monkeypatch):
    """ST §10 / CONVENTIONS #7: Day 25 12:00 settle 50% phần Base còn lại; Day 28 12:00
    settle 100% phần còn lại.

    Kịch bản mở sổ tháng từ Day 5 nên tranche Day 3 không bao giờ tới lượt theo lịch —
    đúng tình huống Month-End sinh ra để dọn: 20 đơn vị Base còn treo tới cuối tháng.
    Day 13 và Day 23 vẫn chạy theo lịch. Nếu Month-End không chạy, 20 đơn vị đó bị mất
    theo tháng (vi phạm 'Base/Smart giải ngân trong tháng').
    """
    days = [{"price": 100.0, "oscore": 20.0, "return7": 0.0}] + [{} for _ in range(24)]
    res, probe = run_case(days, monkeypatch, contribution=CONTRIB,
                          first_local_day="2023-03-05")

    by_day = [(local_parts(p["ts"]), p["reason"], p["nominal"]) for p in _base_buys(res)]
    assert by_day == [
        ((13, 12, 0), "BASE_SCHEDULE", pytest.approx(TRANCHE[1])),
        ((23, 12, 0), "BASE_SCHEDULE", pytest.approx(TRANCHE[2])),
        ((25, 12, 0), "MONTH_END_BASE", pytest.approx(TRANCHE[0] * 0.5)),   # 50% của 20
        ((28, 12, 0), "MONTH_END_BASE", pytest.approx(TRANCHE[0] * 0.5)),   # phần còn lại
    ], by_day

    # Cửa sổ Day 25–27 settle ĐÚNG MỘT LẦN (không settle lại ở Day 26/27).
    in_window = [p for p in _base_buys(res) if local_parts(p["ts"])[0] in (25, 26, 27)]
    assert len(in_window) == 1

    # Không đơn vị Base nào còn treo sau Day 28, và tổng bằng đúng ngân sách tháng.
    assert probe.pool("BASE").available == pytest.approx(0.0, abs=1e-9)
    assert sum(p["nominal"] for p in _base_buys(res)) == pytest.approx(MONTH_BASE_BUDGET)


def test_b2_01d_month_end_day28_is_reached_even_without_a_day25_leftover(monkeypatch):
    """Đối chứng cho câu trên: khi lịch Day 3/13/23 chạy đủ, Base đã hết ở Day 25 nên
    Month-End Base không phát sinh — Month-End là đường DỌN, không phải một tranche thứ tư.
    """
    days = [{"price": 100.0, "oscore": 20.0, "return7": 0.0}] + [{} for _ in range(29)]
    res, probe = run_case(days, monkeypatch, contribution=CONTRIB)
    reasons = [p["reason"] for p in _base_buys(res)]
    assert reasons == ["BASE_SCHEDULE"] * 3
    assert probe.pool("BASE").available == pytest.approx(0.0, abs=1e-9)
    # Smart leftover vẫn được settle ở Day 28 (ST §10) — nhánh Month-End có chạy thật.
    assert any(p["reason"] == "MONTH_END_SMART" for p in res.purchases)


# §21.2 — "Crash eligible-capital snapshot [F5]: đo sau cancel/release,
#          bất biến trong đời Crash ladder"


def _crash_scenario():
    """Có Opportunity ladder ĐANG GIỮ reservation tại thời điểm vào CRASH.

    Đây là điểm mù của bộ test WP-A3: kịch bản `scenario_f001` không có Opportunity ladder
    mở khi crash entry, nên nó chứng minh được "snapshot không bị daily limit thu nhỏ"
    (F-021) nhưng KHÔNG chứng minh được "đo SAU cancel/release".
    """
    return [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {"oscore": 75.0},                                     # Smart + Opportunity ladder
        {"oscore": 69.0},                                     # giữ hysteresis ACTIVE
        {},
        {"oscore": 80.0, "return7": -0.16, "price": 100.5},   # CRASH entry
        {"oscore": 50.0, "return7": -0.05},
        {}, {},
        {"return7": -0.08},
        {},
        {"return7": -0.11},
        {}, {}, {},
    ]


def test_b2_01e_crash_snapshot_is_measured_after_cancel_and_release(monkeypatch):
    """ST §14 [F5]: eligible capital của Crash ladder đo NGAY SAU khi cancel/release các
    Opportunity zone xung đột.

    Phép thử phản chứng: tính lại snapshot bằng ĐÚNG công thức §14 trên trạng thái pool
    của nến TRƯỚC crash entry (tức 'nếu đo TRƯỚC cancel/release'). Hai con số phải khác
    nhau, và số engine dùng phải là số ĐO SAU — chênh lệch đúng bằng lượng vừa release.
    """
    res, probe = run_case(_crash_scenario(), monkeypatch, contribution=CONTRIB)

    crash = probe.by_type("CRASH")
    assert len(crash) == 1, "kịch bản phải sinh đúng một Crash ladder"
    lad = crash[0]

    released = [e["amount"] for e in probe.ledger("OPPORTUNITY", "RELEASE", "CRASH_ENTRY")]
    assert released, "tiền đề: phải có reservation Opportunity bị cancel tại crash entry"
    total_released = sum(released)
    assert total_released == pytest.approx(3.8)          # O1..O4 = 0.6+0.8+1.0+1.4

    i = probe.frame_index(lad.created_at)
    before = probe.frames[i - 1].pools["OPPORTUNITY"]     # nến trước: reservation còn nguyên
    after = probe.frames[i].pools["OPPORTUNITY"]          # cùng nến, sau bước 10 (cancel/release)
    o_unl = float(opportunity_unlock(80.0))
    assert o_unl == pytest.approx(0.30)

    def opp_part(pool_state):
        avail, reserved, deployed = pool_state
        total = avail + reserved + deployed
        return min(avail, max(0.0, total * o_unl - reserved - deployed))

    measured_after = opp_part(after)
    measured_before = opp_part(before)
    assert measured_before == pytest.approx(2.0)
    assert measured_after == pytest.approx(5.8)
    assert measured_after - measured_before == pytest.approx(total_released)

    # Smart AVAILABLE = 0 ở kịch bản này (toàn bộ đã nằm trong Smart ladder), nên snapshot
    # bằng đúng phần Opportunity đo SAU release.
    assert probe.frames[i].pools["SMART"][0] == pytest.approx(0.0, abs=1e-9)
    assert lad.eligible_capital_vnd == pytest.approx(measured_after)
    assert lad.eligible_capital_vnd == pytest.approx(5.8)
    assert lad.eligible_capital_vnd != pytest.approx(measured_before)


def test_b2_01f_crash_snapshot_is_immutable_for_the_life_of_the_ladder(monkeypatch):
    """ST §14 [F5]: snapshot BẤT BIẾN trong đời Crash ladder — kể cả khi zone fill, khi
    Recovery bắt đầu, và khi Recovery kết thúc (cancel + release).
    """
    res, probe = run_case(_crash_scenario(), monkeypatch, contribution=CONTRIB)
    lad = probe.by_type("CRASH")[0]
    seen = [snap for f in probe.frames for (lid, _t, snap) in f.ladder_snapshots
            if lid == lad.ladder_id]
    assert seen, "Crash ladder phải xuất hiện trong ít nhất một khung ảnh"
    assert len(set(seen)) == 1, f"snapshot đổi trong đời ladder: {sorted(set(seen))}"
    assert seen[0] == pytest.approx(lad.eligible_capital_vnd)
    # tiền đề chống rỗng: ladder thực sự đi qua fill và cancel, không phải nằm im
    assert any(z.status == "EXECUTED" for z in lad.zones)
    assert lad.status == "CANCELLED"


# ===================================================================== CHECK-B2-02
# §21.2 — "không double reservation" (Smart / Opportunity / Crash, ở TẦNG ENGINE)


def _assert_no_double_reservation(probe, label: str):
    """Bất biến: tổng RESERVED của mọi pool == tổng `reserved_vnd` của mọi zone ĐANG MỞ.

    Double reservation là đúng trạng thái làm hai vế này lệch nhau: một zone vẫn 'giữ' vốn
    trong khi vốn đó đã được release và cấp cho zone khác (vế phải lớn hơn), hoặc pool bị
    trừ hai lần cho cùng một zone (vế trái lớn hơn). Kiểm ở MỌI nến, không chỉ cuối run.
    """
    bad = [(k, f.total_reserved, f.open_zone_reserved) for k, f in enumerate(probe.frames)
           if abs(f.total_reserved - f.open_zone_reserved) > 1e-9]
    assert not bad, f"{label}: lệch reserved tại {len(bad)} nến, ví dụ {bad[:3]}"


def test_b2_02a_no_double_reservation_when_opportunity_becomes_crash(monkeypatch):
    """§21.3 + §21.2: 'Chuyển Opportunity ladder sang Crash ladder không tạo double
    reservation'. Đây là mệnh đề 3 của Impl Plan §7 mà S001 ghi là KHÔNG KẾT LUẬN ĐƯỢC.
    """
    res, probe = run_case(_crash_scenario(), monkeypatch, contribution=CONTRIB)

    # tiền đề: cả ba loại ladder cùng tồn tại và ca chuyển thật sự xảy ra
    assert {l.type for l in probe.ladders} == {"SMART", "OPPORTUNITY", "CRASH"}
    opp = probe.by_type("OPPORTUNITY")[0]
    crash = probe.by_type("CRASH")[0]
    assert opp.status == "CANCELLED"

    _assert_no_double_reservation(probe, "opportunity->crash")

    # Vốn Opportunity bị cancel được cấp LẠI cho Crash zone, không phải cấp THÊM:
    # tổng reserve Crash rút từ pool OPPORTUNITY <= lượng khả dụng sau release.
    crash_from_opp = sum(e["amount"] for e in probe.ledger("OPPORTUNITY", "RESERVE", "CRASH_ZONE"))
    i = probe.frame_index(crash.created_at)
    avail_after_release = probe.frames[i].pools["OPPORTUNITY"][0]
    assert crash_from_opp > 0
    assert crash_from_opp <= avail_after_release + 1e-9

    # Zone Opportunity đã CANCELLED không còn giữ đồng nào.
    assert all(z.reserved_vnd == pytest.approx(0.0, abs=1e-12)
               for z in opp.zones if z.status == "CANCELLED")

    # Bảo toàn ledger: TOTAL của mỗi pool chỉ đổi qua CONTRIBUTION/OVERFLOW.
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        pool = probe.pool(name)
        assert pool.available >= -1e-9 and pool.reserved >= -1e-9 and pool.deployed >= -1e-9


def test_b2_02b_no_double_reservation_across_smart_and_opportunity(monkeypatch):
    """Cùng bất biến, trên đường đi KHÔNG có Crash: Smart ladder và Opportunity ladder
    cùng sống, cùng trigger, cùng fill, qua hai accounting month.
    """
    days = (
        [{"price": 100.0, "oscore": 20.0, "return7": 0.0},
         {"oscore": 85.0},
         {"oscore": 69.0}]
        + [{} for _ in range(28)]
        + [{"oscore": 69.0}]            # tháng sau: Smart ladder mới
        + [{} for _ in range(3)]
        + [{"price": 81.0}]             # close 81: Smart theo LOW, Opportunity theo CLOSE
        + [{} for _ in range(5)]
    )
    res, probe = run_case(days, monkeypatch, contribution=CONTRIB)
    assert len({l.ladder_id for l in probe.ladders}) >= 3
    assert sum(1 for p in res.purchases if p["source"] == "SMART") >= 3
    assert sum(1 for p in res.purchases if p["source"] == "OPPORTUNITY") >= 2
    _assert_no_double_reservation(probe, "smart+opportunity")


def test_b2_02c_probe_does_not_change_engine_behaviour(monkeypatch):
    """Tiền đề của MỌI test dùng probe: instrumentation là QUAN SÁT thuần.

    Cùng kịch bản, chạy có và không instrumentation -> đầu ra tài chính trùng khớp
    bit-for-bit. Nếu không có test này thì mọi khẳng định phía trên chỉ nói về một engine
    đã bị test làm biến dạng.
    """
    days = _crash_scenario()
    res_probed, probe = run_case(days, monkeypatch, contribution=CONTRIB)
    res_plain, none_probe = run_case(days, monkeypatch, contribution=CONTRIB, probe=False)
    assert none_probe is None
    assert probe is not None and probe.frames
    assert financial_payload(res_probed) == financial_payload(res_plain)
