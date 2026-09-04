"""WP-A6 — Thứ tự 18 bước xử lý mỗi nến 15m (Backtest §19) và no-lookahead tầng 15m.

Đóng F-019 (không có test thứ tự) và nâng F-018 (thứ tự lệch spec) từ E0 lên E1.

Nguyên tắc (task file WP-A6, "Trình tự bắt buộc"): test được viết TỪ CHỮ của BT §19,
KHÔNG từ hành vi hiện có; nó quan sát THỨ TỰ SIDE-EFFECT THẬT (ledger pool, chuyển trạng
thái zone/ladder, fill, cập nhật regime...) trong từng nến qua `wp_a6_order_harness`, chứ
không kiểm sự tồn tại của hàm. Lần chạy đầu tiên trên code chưa sửa ĐƯỢC PHÉP FAIL — đó
chính là bằng chứng CHECK-A6-02.

Mọi kịch bản dưới đây đều TỰ KHẲNG ĐỊNH tiền đề của nó (các sự kiện cần thiết thật sự xảy
ra trong nến được dàn dựng) trước khi kiểm thứ tự — một kịch bản không dựng được phải đỏ,
không được lặng lẽ pass rỗng.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import eth_dca_os.engine as engine_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from wp_a6_order_harness import (
    DAY,
    candle_ts,
    events_at,
    format_violations,
    instrument,
    letter_map,
    load_engine_from_source,
    local_str,
    move_block,
    order_violations,
    run_traced,
    violation_signature,
)

# Ngưỡng/giá dùng chung cho kịch bản (giá phẳng 100; adr30 = 0.03 của harness)
P = 100.0
# oscore 60: smart_spacing = clamp(0.03*2*0.90, 0.04, 0.12) = 0.054 -> S1 = 94.6, S2 = 89.2
S1_60, S2_60 = P * (1 - 0.054), P * (1 - 2 * 0.054)
# oscore 70: smart_spacing = 0.06 -> opp_spacing = clamp(0.075, 0.06, 0.15) = 0.075 -> O1 = 92.5
O1_70 = P * (1 - 0.075)


def _kinds(events, kind):
    return [e for e in events if e.kind == kind]


def _zone_events(events, new=None, old=None):
    out = []
    for e in events:
        if e.kind != "ZONE":
            continue
        if new is not None and e.detail["new"] != new:
            continue
        if old is not None and e.detail["old"] != old:
            continue
        out.append(e)
    return out


def _assert_no_violation(trace, label):
    viol = order_violations(trace, letter_map)
    assert not viol, (
        f"[{label}] {len(viol)} vi phạm thứ tự §19 (bước GIẢM trong cùng nến):\n"
        + format_violations(viol) + f"\nchữ ký: {violation_signature(viol)}")


# ============================================================ kịch bản

def _sc_fill_and_new_trigger(monkeypatch, exec_cfg=None, engine=None):
    """SC1 — trong MỘT nến: action S0 tới hạn (fill) VÀ một zone khác bị xuyên (trigger mới).

    Smart ladder (oscore 60) được tạo tại 07:00 Day 1 (score có hiệu lực từ 07:00 theo
    harness); S0 = anchor = 100 (giá phẳng nên low <= S0 ở mọi nến). Với GATE1 (delay 15
    phút, BULK) action fill sau 2 nến. Dip S1 (low 94 < 94.6) tại 07:30 và dip S2 (low 89
    < 89.2) tại 07:45 để nến fill S0 LUÔN có một trigger mới, bất kể S0 trigger ở nến tạo
    (thứ tự cũ: fill 07:30, S1 trigger) hay ở nến kế tiếp (thứ tự §19: fill 07:45, S2
    trigger). Kịch bản vì thế không khoá vào thứ tự nào — test tự định vị nến fill S0.
    """
    specs = [{"price": P, "oscore": 60.0} for _ in range(3)]
    res, tr, ctx = run_traced(monkeypatch, specs,
                              overrides={(0, 7.5): {"low": 94.0}, (0, 7.75): {"low": 89.0}},
                              exec_cfg=exec_cfg, engine=engine)
    return res, tr, ctx


def _s0_fill_candle(res, tr):
    """Nến fill S0 của Smart ladder đầu tiên + các sự kiện của nến đó (tiền đề tự khẳng định)."""
    s0 = [p for p in res.purchases if p["reason"] == "SMART_ZONE_0"]
    assert len(s0) == 1, "kịch bản: S0 phải fill đúng một lần"
    t = s0[0]["ts"]
    evs = events_at(tr, t)
    assert _kinds(evs, "FILL"), "kịch bản: nến fill S0 phải có sự kiện FILL"
    return t, evs


def _sc_crash_entry(monkeypatch):
    """SC2b — vào CRASH tại 07:00 Day 5 (oscore 80, Return7D −16%): Crash ladder được tạo
    trong chính nến đó; C0 = anchor = OPEN của nến."""
    specs = [{"price": P, "oscore": 60.0} for _ in range(4)]
    specs.append({"price": P, "oscore": 80.0, "return7": -0.16})
    specs += [{"price": P, "oscore": 80.0, "return7": -0.05} for _ in range(4)]
    return run_traced(monkeypatch, specs)


def _sc_rollover_with_base_same_candle(monkeypatch):
    """SC3 — nến ĐẦU TIÊN của tháng 2 rơi đúng 12:00 Day 3 (gap từ 00:00 Day 1 tới 11:45
    Day 3): các bước 2–6 (rollover, HWM reset, contribution) và bước 9 (Base tranche Day 3)
    xảy ra trong CÙNG một nến."""
    specs = [{"price": P, "oscore": 30.0} for _ in range(34)]  # 01/03 -> 03/04
    drops = [(31, 0, 24), (32, 0, 24), (33, 0, 12)]
    return run_traced(monkeypatch, specs, drops=drops)


def _sc_hysteresis_suspend_with_confirmation(monkeypatch, engine=None):
    """SC5 — Opportunity ladder (oscore 70 từ Day 1) rồi score tụt 60 (≤ 62) tại 07:00
    Day 3 -> hysteresis SUSPEND. Nến 07:00 Day 3 được ép close = 92 < O1 = 92.5: theo chữ
    §19, bước 13 (confirmation CLOSE <= zone) đứng TRƯỚC bước 18 (suspension)."""
    specs = [{"price": P, "oscore": 70.0} for _ in range(2)]
    specs.append({"price": P, "oscore": 60.0})
    specs += [{"price": P, "oscore": 60.0} for _ in range(2)]
    return run_traced(monkeypatch, specs, overrides={(2, 7.0): {"close": 92.0}}, engine=engine)


def _sc_recovery(monkeypatch):
    """SC6 — CRASH (Day 5) -> RECOVERY (Day 8 07:00) -> NORMAL (Day 11 07:00); tại nến
    RECOVERY và nến kết thúc Recovery, một Smart zone còn ACTIVE bị xuyên (low dip) để có
    sự kiện bước 13 trong cùng nến với suspension/cancel (bước 18)."""
    specs = [{"price": P, "oscore": 60.0} for _ in range(4)]
    specs.append({"price": P, "oscore": 80.0, "return7": -0.16})       # Day 5: CRASH
    specs += [{"price": P, "oscore": 80.0, "return7": -0.05} for _ in range(2)]
    specs.append({"price": P, "oscore": 80.0, "return7": -0.05})       # Day 8: RECOVERY
    specs += [{"price": P, "oscore": 80.0, "return7": -0.05} for _ in range(2)]
    specs.append({"price": P, "oscore": 80.0, "return7": -0.05})       # Day 11: NORMAL
    specs += [{"price": P, "oscore": 80.0, "return7": -0.05} for _ in range(2)]
    # oscore 80: crash spacing = clamp(0.03*2*1.15*1.25, .06, .15) = 0.08625 -> C1 = 91.375;
    # dip 90 tại nến RECOVERY chỉ xuyên C1 (và S1 = 94.6), để C2/C3 còn reserve tới khi
    # Recovery kết thúc; dip 55 tại nến NORMAL xuyên S2 = 89.2 (còn ACTIVE).
    return run_traced(monkeypatch, specs, overrides={(7, 7.0): {"low": 90.0},
                                                     (10, 7.0): {"low": 55.0}})


def _sc_month_end(monkeypatch, drop_day_28: bool):
    """SC4 — hai đường Month-End Smart: Day 28 12:00 (CONVENTIONS #7) và rollover (§19
    bước 3). Kịch bản B xoá trọn Day 25–28 để đường Day 28 không tồn tại."""
    specs = [{"price": P, "oscore": 60.0} for _ in range(33)]           # 01/03 -> 02/04
    drops = [(d, 0, 24) for d in (24, 25, 26, 27)] if drop_day_28 else ()
    return run_traced(monkeypatch, specs, drops=drops)


# ============================================================ CHECK-A6-01: harness quan sát thật

def test_a6_01_harness_observes_real_side_effects(monkeypatch):
    """Harness ghi được ĐÚNG số nến (một CLOCK mỗi nến) và các side-effect thật của engine
    — nếu không có sự kiện ledger/zone thì test thứ tự phía dưới chỉ pass rỗng."""
    res, tr, (ds, scores, start, end) = _sc_fill_and_new_trigger(monkeypatch)
    n_candles = int(((ds["ETHUSDT_15m"]["open_time"] >= start.tz_localize("UTC"))
                     & (ds["ETHUSDT_15m"]["open_time"] < end.tz_localize("UTC"))).sum())
    clocks = _kinds(tr.events, "CLOCK")
    assert len(clocks) == n_candles and n_candles > 0
    assert all(c.candle == i for i, c in enumerate(clocks))
    assert _kinds(tr.events, "CONTRIBUTE") and _kinds(tr.events, "RESERVE")
    assert _kinds(tr.events, "FILL") and _zone_events(tr.events, new="TRIGGERED")
    assert _kinds(tr.events, "REGIME_UPDATE") and _kinds(tr.events, "DEPLOY_AVAILABLE")
    # sự kiện phải khớp kết quả thật: mỗi FILL là một purchase record
    assert len(_kinds(tr.events, "FILL")) == len(res.purchases)


# ============================================================ thứ tự §19 trên kịch bản dàn dựng

def test_a6_fill_after_new_trigger_in_same_candle(monkeypatch):
    """§19: bước 13/14 (trigger mới -> action) đứng TRƯỚC bước 16/17 (fill, ledger, cooldown)
    trong cùng nến. Đây là quan sát thứ nhất của F-018 ("15/16/17 nằm trong khối bước 12")."""
    res, tr, (ds, scores, start, end) = _sc_fill_and_new_trigger(monkeypatch)
    t, evs = _s0_fill_candle(res, tr)
    assert t in (candle_ts(start, 0, 7.5), candle_ts(start, 0, 7.75)), local_str(t)
    fills = _kinds(evs, "FILL")
    trig = _zone_events(evs, new="TRIGGERED")
    pend = _zone_events(evs, new="ACTION_PENDING")
    # tiền đề: nến fill S0 có CẢ trigger mới (S1 hoặc S2) lẫn action cho zone đó
    assert trig and trig[0].detail["idx"] in (1, 2), "kịch bản: phải có trigger mới tại nến fill S0"
    assert pend and pend[0].detail["zone"] == trig[0].detail["zone"]
    z_new = tr.zone_by_id(trig[0].detail["zone"])
    assert z_new.target_price == pytest.approx(S1_60 if trig[0].detail["idx"] == 1 else S2_60)
    # chữ §19: mọi TRIGGERED (13) và ACTION_PENDING (14) của nến này đứng trước mọi FILL (16)
    first_fill = min(e.seq for e in fills)
    late = [e for e in trig + pend if e.seq > first_fill]
    assert not late, ("fill (bước 16/17) xảy ra TRƯỚC trigger/action mới (bước 13/14): "
                      + ", ".join(repr(e) for e in late))
    _assert_no_violation(tr, "SC1 fill+trigger")


def test_a6_same_candle_fill_cooldown_does_not_gate_same_candle_action(monkeypatch):
    """§19: bước 11 (đọc cooldown) đứng trước bước 14 (tạo action) và bước 17 (cập nhật
    cooldown sau fill). Cooldown do fill S0 tại nến N KHÔNG được chặn action S1 tạo ở
    chính nến N — cả hai thứ tự (hiện tại và spec) đều phải cho kết quả này."""
    res, tr, (ds, scores, start, end) = _sc_fill_and_new_trigger(monkeypatch)
    t, evs = _s0_fill_candle(res, tr)
    pend = _zone_events(evs, new="ACTION_PENDING")
    assert pend, "zone trigger mới phải thành ACTION_PENDING ngay trong nến fill S0"
    idx = pend[0].detail["idx"]
    # và zone đó thực thi thật sau đó (không bị cooldown 48h của S0 nuốt): +2 nến (GATE1)
    later = [p for p in res.purchases if p["reason"] == f"SMART_ZONE_{idx}"]
    assert len(later) == 1 and later[0]["ts"] == t + 1800.0


def test_a6_new_ladder_zones_not_triggered_in_creation_candle(monkeypatch):
    """§19: bước 13 (kiểm trigger) đứng TRƯỚC bước 14 (tạo reservation/ladder mới), nên zone
    của ladder tạo ở nến N chỉ được xét trigger từ nến N+1. Quan sát thứ hai của F-018
    ("ladder mới tham gia trigger ngay trong cùng nến"). Kiểm cả Smart lẫn Crash ladder."""
    for label, runner in (("SMART", _sc_fill_and_new_trigger), ("CRASH", _sc_crash_entry)):
        res, tr, (ds, scores, start, end) = runner(monkeypatch)
        created = _kinds(tr.events, "LADDER_CREATED")
        assert any(c.detail["type"] == label for c in created), f"kịch bản {label}: không tạo ladder"
        same_candle = []
        for c in created:
            for e in _zone_events(events_at(tr, c.ts), new="TRIGGERED"):
                if e.detail["ladder"] == c.detail["ladder"]:
                    same_candle.append((c, e))
        assert not same_candle, (
            f"[{label}] zone của ladder mới tạo đã TRIGGERED ngay trong nến tạo (bước 14 đứng "
            f"trước bước 13):\n" + "\n".join(f"  {c!r}\n  -> {e!r}" for c, e in same_candle))


def test_a6_rollover_steps_2_to_6_before_base_step_9_same_candle(monkeypatch):
    """§19 bước 2–6 (tháng mới, HWM reset, contribution, cap/overflow) đứng trước bước 9
    (Base schedule) khi cả hai rơi vào cùng một nến (gap tới đúng 12:00 Day 3)."""
    res, tr, (ds, scores, start, end) = _sc_rollover_with_base_same_candle(monkeypatch)
    t = candle_ts(start, 33, 12.0)                     # 12:00 Day 3 tháng 4
    evs = events_at(tr, t)
    assert _kinds(evs, "OPEN_MONTH") and _kinds(evs, "HWM_RESET"), "kịch bản: phải là nến rollover"
    contrib = _kinds(evs, "CONTRIBUTE")
    base = [e for e in _kinds(evs, "DEPLOY_AVAILABLE") if e.detail["reason"] == "BASE_SCHEDULE"]
    assert len(contrib) == 3 and base, "kịch bản: contribution VÀ Base tranche cùng nến"
    assert max(e.seq for e in contrib) < min(e.seq for e in base)
    assert _kinds(evs, "HWM_RESET")[0].seq < min(e.seq for e in contrib)
    assert _kinds(evs, "OPEN_MONTH")[0].seq < _kinds(evs, "HWM_RESET")[0].seq
    # Base tranche đúng 40% ngân sách Base tháng mới, có tag gap
    rec = [p for p in res.purchases if p["ts"] == t and p["reason"] == "BASE_SCHEDULE"]
    assert len(rec) == 1 and rec[0]["nominal"] == pytest.approx(20.0)
    assert "EXECUTION_DATA_GAP" in rec[0]["tags"]
    _assert_no_violation(tr, "SC3 rollover+base")


def test_a6_month_end_two_paths_settle_once(monkeypatch):
    """E0-hint: hai đường Month-End Smart (Day 28 12:00 theo CONVENTIONS #7; rollover theo
    §19 bước 3). Kiểm bằng chạy thật: (A) có Day 28 -> settle tại Day 28, rollover KHÔNG
    settle lại; (B) Day 25–28 nằm trong gap -> fallback settle tại rollover; tổng Smart
    giải ngân hai kịch bản bằng nhau (không mất, không đúp)."""
    res_a, tr_a, (_, _, start, _) = _sc_month_end(monkeypatch, drop_day_28=False)
    res_b, tr_b, _ = _sc_month_end(monkeypatch, drop_day_28=True)
    t28 = candle_ts(start, 27, 12.0)
    t_roll = candle_ts(start, 31, 0.0)                 # 00:00 01/04

    def settles(res):
        return [(p["ts"], p["nominal"]) for p in res.purchases if p["reason"] == "MONTH_END_SMART"]

    sa, sb = settles(res_a), settles(res_b)
    assert sa and all(ts == t28 for ts, _ in sa), f"A: settle phải tại Day 28 12:00, được {sa}"
    assert not [e for e in events_at(tr_a, t_roll) if e.kind == "DEPLOY_AVAILABLE"
                and e.detail["reason"] == "MONTH_END_SMART"], "A: rollover không được settle lần hai"
    assert sb and all(ts == t_roll for ts, _ in sb), f"B: fallback phải tại rollover, được {sb}"
    assert sum(n for _, n in sa) == pytest.approx(sum(n for _, n in sb))
    # Smart ladder tháng 3 hết hạn đúng một lần ở mỗi kịch bản
    exp_a = [e for e in tr_a.events if e.kind == "LADDER" and e.detail["new"] == "EXPIRED"]
    exp_b = [e for e in tr_b.events if e.kind == "LADDER" and e.detail["new"] == "EXPIRED"]
    assert len(exp_a) == 1 and exp_a[0].ts == t28
    assert len(exp_b) == 1 and exp_b[0].ts == t_roll
    # tổng SMART của THÁNG 3 (zone + settle) bằng nhau -> không mất vốn khi rơi vào gap.
    # (Chỉ so trong tháng: settle tại rollover ghi purchase nguồn SMART nên đặt cooldown 48h
    # tràn sang tháng mới — quan sát nghiệp vụ ghi ở biên bản S014, không thuộc thứ tự.)
    tot = lambda r: sum(p["nominal"] for p in r.purchases
                        if p["source"] == "SMART" and p["ts"] <= t_roll)
    assert tot(res_a) == pytest.approx(tot(res_b)) == pytest.approx(30.0)
    _assert_no_violation(tr_a, "SC4-A month-end")
    _assert_no_violation(tr_b, "SC4-B month-end gap")


def test_a6_hysteresis_suspension_is_step_18_after_confirmation_step_13(monkeypatch):
    """§19: confirmation Opportunity (bước 13, CLOSE <= zone) đứng TRƯỚC suspension (bước 18)
    trong cùng nến. Nến 07:00 Day 3: score 60 -> hysteresis SUSPEND, và close 92 < O1."""
    res, tr, (ds, scores, start, end) = _sc_hysteresis_suspend_with_confirmation(monkeypatch)
    t = candle_ts(start, 2, 7.0)
    evs = events_at(tr, t)
    susp = _zone_events(evs, new="SUSPENDED")
    assert susp, "kịch bản: zone Opportunity phải bị SUSPENDED tại 07:00 Day 3"
    opp = [l for l in tr.ladders if l.type == "OPPORTUNITY"]
    assert opp and opp[0].zones[1].target_price == pytest.approx(O1_70)
    assert float(ds["ETHUSDT_15m"].loc[
        ds["ETHUSDT_15m"]["open_time"] == pd.Timestamp(t, unit="s", tz="UTC"), "close"].iloc[0]) == 92.0
    _assert_no_violation(tr, "SC5 hysteresis")


def test_a6_recovery_transitions_are_step_18_after_trigger_step_13(monkeypatch):
    """§19: suspension/expiry của Crash ladder (bước 18) đứng SAU kiểm trigger (bước 13) trong
    cùng nến; nến RECOVERY và nến kết thúc Recovery đều có một zone bị xuyên."""
    res, tr, (ds, scores, start, end) = _sc_recovery(monkeypatch)
    trans = [e for e in tr.events if e.kind == "REGIME_UPDATE" and e.detail["prev"] != e.detail["new"]]
    kinds = [(e.detail["prev"], e.detail["new"]) for e in trans]
    assert kinds == [("NORMAL", "CRASH"), ("CRASH", "RECOVERY"), ("RECOVERY", "NORMAL")], kinds
    t_rec, t_norm = trans[1].ts, trans[2].ts
    assert _zone_events(events_at(tr, t_rec), new="SUSPENDED"), "kịch bản: crash zone SUSPENDED tại RECOVERY"
    assert _zone_events(events_at(tr, t_rec), new="TRIGGERED"), "kịch bản: có trigger tại nến RECOVERY"
    assert [e for e in events_at(tr, t_norm) if e.kind == "RELEASE"
            and e.detail["reason"] == "RECOVERY_END"], "kịch bản: release RECOVERY_END"
    _assert_no_violation(tr, "SC6 recovery")


@pytest.mark.parametrize("name,runner", [
    ("fill+trigger", _sc_fill_and_new_trigger),
    ("crash-entry", _sc_crash_entry),
    ("rollover+base", _sc_rollover_with_base_same_candle),
    ("hysteresis", _sc_hysteresis_suspend_with_confirmation),
    ("recovery", _sc_recovery),
])
def test_a6_step_order_monotonic_per_candle(monkeypatch, name, runner):
    """Kiểm tổng quát: trong MỖI nến, dãy số bước §19 của các side-effect không giảm."""
    res, tr, _ = runner(monkeypatch)
    _assert_no_violation(tr, name)


# ============================================================ long-run trên dataset tổng hợp

@pytest.fixture(scope="module")
def synth_prepared(tmp_path_factory):
    from eth_dca_os.data.dataset import load_dataset
    from eth_dca_os.data.synth import generate
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores
    d = tmp_path_factory.mktemp("a6raw")
    generate(d, start="2018-01-01", end="2021-06-30")
    ds = load_dataset(d)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = pd.concat([ind, compute_scores(ind)], axis=1)
    scores = scores.loc[:, ~scores.columns.duplicated()]
    return ds, scores


@pytest.mark.parametrize("exec_cfg", [GATE1_LOW_FRICTION, GATE3_REALISTIC],
                         ids=["gate1_low_friction", "gate3_realistic"])
def test_a6_step_order_monotonic_long_run(monkeypatch, synth_prepared, exec_cfg):
    """Cùng phép kiểm trên 2 năm dữ liệu tổng hợp (mọi đường xử lý: crash, recovery, month-end,
    hysteresis, TTL...) với cả hai execution config đã commit."""
    ds, scores = synth_prepared
    tr = instrument(monkeypatch)
    res = engine_mod.run_engine(ds, scores, BASELINE_STRATEGY, exec_cfg,
                                pd.Timestamp("2019-06-01"), pd.Timestamp("2021-06-01"))
    assert res.eth_total > 0 and _zone_events(tr.events, new="TRIGGERED")
    _assert_no_violation(tr, f"long-run {exec_cfg.config_name}")


# ============================================================ CHECK-A6-06: no-lookahead tầng 15m

def _run_plain(ds, scores, start, end, exec_cfg=GATE1_LOW_FRICTION):
    return engine_mod.run_engine(ds, scores, BASELINE_STRATEGY, exec_cfg, start, end)


def _state_prefix(res, cut_ts):
    """Phần kết quả thuộc các nến có ts <= cut_ts (mọi trường).

    `zone_id`/`ladder_id` trong decision_log là bộ đếm TOÀN CỤC của `ladders.py`
    (`itertools.count`), tăng qua mọi lần chạy trong cùng tiến trình — không phải trạng
    thái engine, nên được bỏ khi so sánh. `decision_id` thì KHÔNG bỏ: nó là bộ đếm theo
    RUN (WP-B3) nên vẫn tất định giữa hai lần chạy.
    """
    return {
        "purchases": [p for p in res.purchases if p["ts"] <= cut_ts],
        "cash": [c for c in res.cash_samples if c[0] <= cut_ts],
        "log": [{k: v for k, v in d.items() if k not in ("zone_id", "ladder_id")}
                for d in res.decision_log if d["timestamp_utc"] <= cut_ts],
        "contrib": [c for c in res.contributions if c[0] <= cut_ts],
    }


def test_a6_06_daily_score_visible_only_after_daily_candle_closes(monkeypatch, synth_prepared):
    """Score của ngày D chỉ có hiệu lực từ nến 15m đầu tiên có ts >= D+1 00:00 UTC (nến daily
    D đã đóng); trước đó engine dùng score của ngày gần nhất đã đóng. Quan sát qua oscore
    truyền vào regime.update ở MỌI nến."""
    ds, scores = synth_prepared
    tr = instrument(monkeypatch)
    start, end = pd.Timestamp("2019-06-01"), pd.Timestamp("2019-09-01")
    engine_mod.run_engine(ds, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION, start, end)
    day_ts = ((pd.DatetimeIndex(scores.index) - pd.Timestamp(0, tz=scores.index.tz))
              / pd.Timedelta(seconds=1)).to_numpy(float)
    day_end = day_ts + DAY
    osc = scores["oscore"].to_numpy(float)
    dq = scores["data_quality"].to_numpy(object)
    checked = 0
    for e in tr.events:
        if e.kind != "REGIME_UPDATE":
            continue
        j = int(np.searchsorted(day_end, e.ts, side="right")) - 1   # ngày gần nhất ĐÃ đóng
        assert j >= 0
        expected = None if (dq[j] == "INVALID" or np.isnan(osc[j])) else osc[j]
        got = e.detail["oscore"]
        assert (got is None and expected is None) or got == expected, (
            f"{e!r}: oscore hiệu lực {got} != score ngày đã đóng gần nhất {expected} "
            f"(day_end={day_end[j]})")
        # và KHÔNG bằng score của ngày chưa đóng nếu ngày đó khác
        if j + 1 < len(osc) and osc[j + 1] != osc[j] and got is not None:
            assert got != osc[j + 1]
        checked += 1
    assert checked > 90 * 96 - 96


def test_a6_06_future_daily_rows_cannot_change_past_candles(synth_prepared):
    """Đầu độc mọi hàng daily SAU ngày D (oscore 100, INVALID, adr30/return7 lố): mọi kết quả
    tại các nến trước khi nến daily D đóng phải trùng bit-for-bit với run không đầu độc."""
    ds, scores = synth_prepared
    start, end = pd.Timestamp("2019-06-01"), pd.Timestamp("2020-06-01")
    d_cut = pd.Timestamp("2019-12-15", tz="UTC")
    cut_ts = d_cut.timestamp() + DAY                     # nến daily D đóng tại D+1 00:00 UTC
    poison = scores.copy()
    after = poison.index > d_cut
    assert after.sum() > 100
    poison.loc[after, "oscore"] = 100.0
    poison.loc[after, "data_quality"] = "INVALID"
    poison.loc[after, "return7"] = -0.9
    poison.loc[after, "adr30"] = 0.5
    poison.loc[after, "close"] = 1.0
    base, pz = _run_plain(ds, scores, start, end), _run_plain(ds, poison, start, end)
    a, b = _state_prefix(base, cut_ts - 1), _state_prefix(pz, cut_ts - 1)
    assert a["purchases"] and a == b, "dữ liệu daily tương lai đã đổi quá khứ -> lookahead"
    # đối chứng: sau mốc, hai run PHẢI khác nhau (nếu không, phép đầu độc vô nghĩa)
    assert _state_prefix(base, end.timestamp()) != _state_prefix(pz, end.timestamp())


def test_a6_06_future_15m_candles_cannot_change_past_state(synth_prepared):
    """Cắt chuỗi 15m tại nến N: toàn bộ purchase/cash/log/contribution tới nến N trùng khớp
    với run trên chuỗi đầy đủ — engine chỉ dùng nến đã đóng, không nhìn nến sau."""
    ds, scores = synth_prepared
    start, end = pd.Timestamp("2019-06-01"), pd.Timestamp("2020-06-01")
    cut = pd.Timestamp("2019-11-20 13:30", tz="UTC")
    e15 = ds["ETHUSDT_15m"]
    ds_cut = dict(ds)
    ds_cut["ETHUSDT_15m"] = e15[e15["open_time"] <= cut].reset_index(drop=True)
    full = _run_plain(ds, scores, start, end)
    part = _run_plain(ds_cut, scores, start, end)
    a, b = _state_prefix(full, cut.timestamp()), _state_prefix(part, cut.timestamp())
    assert a["purchases"] and a == b
    # đầu độc thay vì cắt: đổi OHLC mọi nến sau N thành giá lố -> tiền tố vẫn bất biến
    ds_poison = dict(ds)
    e2 = e15.copy()
    m = e2["open_time"] > cut
    for col in ("open", "high", "low", "close"):
        e2.loc[m, col] = 1.0
    ds_poison["ETHUSDT_15m"] = e2
    pz = _run_plain(ds_poison, scores, start, end)
    assert _state_prefix(pz, cut.timestamp()) == a
    assert _state_prefix(pz, end.timestamp()) != _state_prefix(full, end.timestamp())


# ============================================================ H-15: zone TRIGGERED trong chu kỳ INVALID

def test_h15_trigger_in_invalid_cycle_persists_until_first_valid_cycle(monkeypatch):
    """H-15 (HARDENING_BACKLOG) — quyết định của WP-A6, ghi ở CONVENTIONS #19.

    Bước 13 (phát hiện trigger) đọc giá 15m, không đọc chất lượng daily; INVALID chỉ chặn
    ở bước 14 (ST §3: "chặn mọi action Smart/Opportunity MỚI"). Zone TRIGGERED trong chu
    kỳ INVALID vì thế GIỮ trạng thái và thành action ở chu kỳ hợp lệ đầu tiên — cùng cơ chế
    giữ-TRIGGERED của max_zones (ST §15.1) và cooldown (CONVENTIONS #6). Cái giá đo được của
    quy ước này (ghi để WP-D2 cân nhắc): action được tạo ở giá của chu kỳ hợp lệ, có thể
    cao hơn target của zone. Kịch bản cùng khung với CHECK-A4-02: dq INVALID từ 07:00 Day 5
    tới 06:45 Day 7, dip Day 6 xuyên S1 (94.6) và S2 (89.2), GOOD từ 07:00 Day 7.
    """
    from pathlib import Path
    specs = [{"price": P, "oscore": 60.0} for _ in range(4)]
    specs.append({"price": P, "oscore": 60.0, "dq": "INVALID"})
    specs.append({"price": P, "low_dip": 60.0, "oscore": 60.0, "dq": "INVALID"})
    specs += [{"price": P, "oscore": 60.0, "dq": "GOOD"} for _ in range(3)]
    res, tr, (ds, scores, start, end) = run_traced(monkeypatch, specs)
    t_invalid_from, t_valid_from = candle_ts(start, 4, 7.0), candle_ts(start, 6, 7.0)

    trig = [e for e in _zone_events(tr.events, new="TRIGGERED") if e.detail["idx"] in (1, 2)]
    assert len(trig) == 2 and all(t_invalid_from <= e.ts < t_valid_from for e in trig), \
        "kịch bản: S1 và S2 phải TRIGGERED trong cửa sổ INVALID"
    pend = [e for e in _zone_events(tr.events, new="ACTION_PENDING") if e.detail["idx"] in (1, 2)]
    assert pend and all(e.ts >= t_valid_from for e in pend), "INVALID chặn action mới (ST §3)"
    assert all(e.ts == t_valid_from for e in pend), "action ở CHU KỲ HỢP LỆ ĐẦU TIÊN (giữ TRIGGERED)"
    # không zone nào bị hoàn về ACTIVE / CANCELLED vì INVALID
    assert not [e for e in tr.events if e.kind == "ZONE" and e.detail["old"] == "TRIGGERED"
                and e.detail["new"] not in ("ACTION_PENDING",)]
    fills = [p for p in res.purchases if p["reason"] in ("SMART_ZONE_1", "SMART_ZONE_2")]
    assert len(fills) == 2 and all(p["ts"] == t_valid_from + 1800.0 for p in fills)
    # cái giá của quy ước: fill ở giá chu kỳ hợp lệ (100) dù target zone là 94.6 / 89.2
    assert all(p["price"] > S1_60 for p in fills)
    conventions = Path("docs/CONVENTIONS.md").read_text(encoding="utf-8")
    assert "H-15" in conventions, "quyết định H-15 phải được ghi ở docs/CONVENTIONS.md"


# ============================================================ CHECK-A6-05: thử phá có chủ đích

def _engine_source() -> str:
    from pathlib import Path
    return Path(engine_mod.__file__).read_text(encoding="utf-8")


# (nhãn, marker đầu khối, marker cuối khối, marker đích "dán trước", chữ ký vi phạm kỳ vọng,
#  kịch bản dùng để phát hiện)
DELIBERATE_REORDERS = {
    "F-018b: tạo ladder (14b) trước kiểm trigger (13)": (
        "        # 14b. tạo reservation mới: Smart / Opportunity ladder",
        "        # 14c. điều chỉnh reservation",
        "        # 13. trigger Smart (LOW)",
        ("RESERVE[SMART_ZONE_S2]@14", "ZONE[ACTIVE->TRIGGERED]@13"),
        _sc_fill_and_new_trigger,
    ),
    "F-018a: fill (15-17) trong khối trước bước 13": (
        "        # 15. ưu tiên thực thi",
        "        # 18. ladder completion",
        "        # 13. trigger Smart (LOW)",
        ("FILL@16", "ZONE[ACTIVE->TRIGGERED]@13"),
        _sc_fill_and_new_trigger,
    ),
    # SC1 fill hết ba zone ngay Day 1 (ladder COMPLETED) nên không còn gì để bullish-check;
    # kịch bản hysteresis giữ ladder Smart/Opportunity sống qua nhiều ngày.
    "18a bullish invalidation trước bước 9": (
        "        # 18a. bullish invalidation",
        "        # 18b. hysteresis",
        "        # 9. Base schedule",
        ("BULLISH_CHECK@18", "REGIME_UPDATE@10"),
        _sc_hysteresis_suspend_with_confirmation,
    ),
}


@pytest.mark.parametrize("label", list(DELIBERATE_REORDERS), ids=list(DELIBERATE_REORDERS))
def test_a6_05_order_test_detects_deliberate_reordering(monkeypatch, label):
    """CHECK-A6-05: test thứ tự PHẢI đỏ nếu ai đó đảo lại thứ tự. Nạp `engine.py` từ mã nguồn,
    dời một khối theo marker (tái tạo đúng sai lệch F-018 hoặc một sai lệch mới), chạy kịch
    bản tương ứng và khẳng định phép kiểm bắt được với chữ ký vi phạm kỳ vọng; đối chứng:
    engine thật trên cùng kịch bản không vi phạm."""
    start_m, end_m, before_m, expected, runner = DELIBERATE_REORDERS[label]
    src = _engine_source()
    mutated = move_block(src, start_m, end_m, before_m)
    assert mutated != src
    mutant = load_engine_from_source(mutated)
    res_m, tr_m, _ = runner(monkeypatch, engine=mutant)
    viol = order_violations(tr_m, letter_map)
    sig = violation_signature(viol)
    assert expected in sig, (f"[{label}] test thứ tự KHÔNG bắt được bản đảo thứ tự; chữ ký thu "
                             f"được: {sig}")
    res_r, tr_r, _ = runner(monkeypatch)
    assert not order_violations(tr_r, letter_map), "đối chứng: engine thật phải sạch"
    assert res_r.eth_total > 0
