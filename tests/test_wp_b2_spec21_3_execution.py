"""WP-B2 — Backtest §21.3 (Execution và regime): những requirement CHƯA CÓ TEST.

  CHECK-B2-03  một / hai / ba zone bị xuyên trong cùng một nến; tối đa hai zone mỗi cycle;
               tie-break §15.1 [F2] và `max_zones` áp SAU khi sắp thứ tự
  CHECK-B2-04  Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW;
               proxy ban đêm tại 07:00 local; TTL; action MISSED
  CHECK-B2-05  cooldown và override (gồm tần suất override trong CRASH);
               Crash funding unavailable scenario
  CHECK-B2-06  [F1] STRESSED không có hiệu ứng execution — lưới an toàn THƯỜNG TRỰC

Mọi khẳng định đi qua `run_engine` thật. Điểm đo trạng thái từng nến là `wp_b2_probe`
(quan sát thuần, đã được `test_b2_02c_probe_does_not_change_engine_behaviour` khoá lại).
Gói này KHÔNG sửa `src/eth_dca_os/`.
"""
from __future__ import annotations

import pytest

from eth_dca_os.config import ExecutionConfig
from eth_dca_os.engine import zone_order_key
from eth_dca_os.execution import MISSED, behavioral_delay_seconds
from eth_dca_os.regime import RegimeTracker
from wp_b2_probe import CANDLE, DAY, TZ, FixedRng, local_key, run_case

CONTRIB = 100.0
H = 3600.0


# ------------------------------------------------------------------ kịch bản dùng chung

def _two_month_days(day5_april: dict) -> list[dict]:
    """Hai accounting month, và ở tháng thứ hai thứ tự DANH SÁCH ladder KHÁC thứ tự §15.1.

    Tháng 3: OSCORE 85 tạo Smart ladder M1 **và** Opportunity ladder (TTL 90 ngày, sống
    sang tháng 4). Smart M1 hết hạn cuối tháng 3. Tháng 4: Smart ladder M2 được tạo và
    **đứng SAU** Opportunity ladder trong danh sách `ladders` của engine.

    Nhờ đó, khi một nến tháng 4 xuyên đồng thời zone của cả hai ladder, thứ tự DUYỆT thô
    (Opportunity trước) mâu thuẫn với thứ tự §15.1 (Smart trước). Đó là điều kiện cần để
    câu "max_zones áp SAU khi sắp thứ tự" trở thành một mệnh đề kiểm chứng được thay vì
    một mô tả.
    """
    return (
        [{"price": 100.0, "oscore": 20.0, "return7": 0.0},
         {"oscore": 85.0},
         {"oscore": 69.0}]                 # giữ hysteresis ACTIVE, dưới ngưỡng kéo sớm Base
        + [{} for _ in range(28)]
        + [{"oscore": 69.0}]               # 01/04 — Smart ladder M2
        + [{} for _ in range(3)]
        + [dict(day5_april)]               # 05/04 — nến bị xuyên
        + [{} for _ in range(5)]
    )


DIP_CANDLE = "2023-04-05 00:00"


def _dip_frame(probe):
    return [f for f in probe.frames if local_key(f.ts) == DIP_CANDLE][0]


def _actions_created_at(probe, ts):
    """Zone được TẠO ACTION tại nến `ts` — đọc ở khung ảnh của nến kế tiếp.

    Khung ảnh được chụp ở bước 12b, tức TRƯỚC bước 13–14 của chính nến đó; nên hệ quả của
    bước 13–14 tại nến T quan sát được ở khung ảnh của nến T+1.
    """
    i = probe.frame_index(ts)
    nxt = probe.frames[i + 1]
    return {z[3] for z in nxt.zones if z[5] == "ACTION_PENDING"}


def _still_triggered_at(probe, ts):
    i = probe.frame_index(ts)
    nxt = probe.frames[i + 1]
    return {z[3] for z in nxt.zones if z[5] == "TRIGGERED"}


def _blocked(res, ts):
    return [d["zone_id"] for d in res.decision_log
            if d["reason_code"] == "MAX_ZONES_BLOCK" and d["timestamp_utc"] == ts]


# ===================================================================== CHECK-B2-03
# §21.3 — "Một, hai và ba zone bị xuyên trong cùng một nến; giới hạn tối đa hai zone
#          mỗi cycle; thứ tự tie-break theo Strategy §15.1 [F2]"

@pytest.mark.parametrize("label,day5,n_pierced,n_actions,n_blocked", [
    ("một zone",  {"low_dip": 92.0},                  1, 1, 0),
    ("hai zone",  {"low_dip": 88.0},                  2, 2, 0),
    ("ba zone",   {"price": 90.0, "low_dip": 88.0},   3, 2, 1),
    ("bốn zone",  {"price": 81.0},                    4, 2, 2),
])
def test_b2_03a_zones_pierced_in_one_candle_and_max_two_per_cycle(
        monkeypatch, label, day5, n_pierced, n_actions, n_blocked):
    """Số zone bị xuyên trong CÙNG MỘT nến được tính ĐỘC LẬP với engine, từ OHLC của nến
    và luật §5 (`Smart: LOW <= zone`, `Opportunity: CLOSE <= zone`).

    Rồi mới đối chiếu: `max_zones_per_cycle = 2` (ST §15.1) nên số action tạo trong nến đó
    tối đa là hai, phần dư bị `MAX_ZONES_BLOCK` và được xét lại ở cycle sau.
    """
    res, probe = run_case(_two_month_days(day5), monkeypatch, contribution=CONTRIB)
    ts = _dip_frame(probe).ts

    pierced = probe.pierced_zones(ts)
    assert len(pierced) == n_pierced, f"{label}: xuyên {sorted(pierced)}"

    created = _actions_created_at(probe, ts) & pierced
    blocked = set(_blocked(res, ts))
    assert len(created) == n_actions, f"{label}: action tạo {sorted(created)}"
    assert len(blocked) == n_blocked, f"{label}: bị chặn {sorted(blocked)}"
    assert created.isdisjoint(blocked)
    assert created | blocked == pierced, "mọi zone bị xuyên phải hoặc có action hoặc bị chặn"
    assert blocked == _still_triggered_at(probe, ts) & pierced, \
        "zone bị chặn phải GIỮ TRIGGERED để xét lại cycle sau (CONVENTIONS #6/#19)"

    # Không zone nào bị bỏ rơi: zone bị chặn được cấp action ở một cycle sau và fill.
    if blocked:
        later = {z[3] for f in probe.frames if f.ts > ts
                 for z in f.zones if z[3] in blocked and z[5] == "ACTION_PENDING"}
        assert later == blocked, f"{label}: zone bị chặn không được xét lại: {blocked - later}"


def test_b2_03b_max_zones_is_applied_after_ordering_not_before(monkeypatch):
    """§19 bước 14: "max_zones_per_cycle (áp SAU khi đã sắp thứ tự theo §15.1)".

    Mệnh đề chỉ có nội dung khi hai thứ tự KHÁC nhau. Kịch bản hai tháng dựng đúng tình
    huống đó: trong danh sách `ladders`, Opportunity ladder (tháng 3) đứng TRƯỚC Smart
    ladder M2 (tháng 4), nên nếu `max_zones` được áp trên thứ tự duyệt thô thì hai zone
    Opportunity sẽ thắng. Theo §15.1 thì hai zone Smart phải thắng.
    """
    res, probe = run_case(_two_month_days({"price": 81.0}), monkeypatch, contribution=CONTRIB)
    ts = _dip_frame(probe).ts
    pierced = probe.pierced_zones(ts)
    assert len(pierced) == 4

    lad_by_id = {l.ladder_id: l for l in probe.ladders}
    zone_by_id = {z.zone_id: (z, lad_by_id[z.ladder_id])
                  for l in probe.ladders for z in l.zones}

    # (a) thứ tự DUYỆT THÔ = thứ tự ladder được tạo, rồi zone_index trong ladder
    raw = sorted(pierced, key=lambda zid: (
        [l.ladder_id for l in probe.ladders].index(zone_by_id[zid][1].ladder_id),
        zone_by_id[zid][0].zone_index))
    # (b) thứ tự CANONICAL §15.1
    canonical = sorted(pierced, key=lambda zid: zone_order_key(*zone_by_id[zid]))

    assert raw[:2] != canonical[:2], \
        "kịch bản không phân biệt được hai thứ tự — test sẽ không chứng minh gì"
    assert {zone_by_id[z][1].type for z in raw[:2]} == {"OPPORTUNITY"}
    assert {zone_by_id[z][1].type for z in canonical[:2]} == {"SMART"}

    created = _actions_created_at(probe, ts) & pierced
    assert created == set(canonical[:2]), \
        f"engine chọn {sorted(created)}; §15.1 đòi {sorted(canonical[:2])}"
    assert set(_blocked(res, ts)) == set(canonical[2:])


def test_b2_03c_tiebreak_orders_fills_inside_one_candle_base_smart_opportunity(monkeypatch):
    """§15.1 [F2] tầng 1 (pool: Base -> Smart -> Opportunity) và tầng 3 (zone_index tăng
    dần) quan sát được trên THỨ TỰ GHI SỔ của các fill cùng một nến (§19 bước 15).
    """
    days = [{"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 75.0}, {}, {}, {}]
    res, probe = run_case(days, monkeypatch, contribution=CONTRIB)

    same_candle: dict = {}
    for p in res.purchases:
        same_candle.setdefault(p["ts"], []).append(p)
    multi = [v for v in same_candle.values() if len(v) > 1]
    assert multi, "tiền đề: phải có nến có nhiều hơn một fill"
    for group in multi:
        rank = {"BASE": 0, "SMART": 1, "OPPORTUNITY": 2, "CRASH": 2}
        got = [rank[p["source"]] for p in group]
        assert got == sorted(got), [(p["source"], p["reason"]) for p in group]

    # tầng 3 trong cùng ladder: zone_index tăng dần trên toàn bộ chuỗi fill của ladder đó
    for pref in ("SMART_ZONE_", "OPPORTUNITY_ZONE_"):
        idx = [int(p["reason"][len(pref):]) for p in res.purchases
               if p["reason"].startswith(pref)]
        assert idx == sorted(idx), (pref, idx)


# ===================================================================== CHECK-B2-04
# §21.3 / §5 — "Opportunity cần confirmation bằng CLOSE và thực thi ở nến sau;
#               Smart trigger bằng LOW"

def test_b2_04a_smart_triggers_on_low_while_opportunity_ignores_the_same_wick(monkeypatch):
    """§5: `Smart trigger: LOW[T] <= zone_price`; `Opportunity trigger: CLOSE[T] <= zone`.

    Nến có LOW = 88 nhưng CLOSE = 100. Zone Smart tại 94.06 và 88.12 bị xuyên; zone
    Opportunity tại 90.81 — thấp hơn LOW nhưng cao hơn CLOSE — KHÔNG được kích hoạt.
    Nếu Opportunity cũng đọc LOW thì zone đó đã trigger; đây chính là phép phân biệt.
    """
    res, probe = run_case(_two_month_days({"low_dip": 88.0}), monkeypatch, contribution=CONTRIB)
    f = _dip_frame(probe)
    c = probe.candle(f.ts)
    assert (c["low"], c["close"]) == (88.0, 100.0)

    opp_open = [z for z in f.zones if z[1] == "OPPORTUNITY" and z[5] == "ACTIVE" and z[6] > 0]
    assert opp_open, "tiền đề: phải còn zone Opportunity đang mở"
    wick_only = [z for z in opp_open if c["low"] <= z[8] < c["close"]]
    assert wick_only, "tiền đề: phải có zone Opportunity nằm giữa LOW và CLOSE"

    pierced = probe.pierced_zones(f.ts)
    assert {z[3] for z in wick_only}.isdisjoint(pierced)
    created = _actions_created_at(probe, f.ts)
    assert {z[3] for z in wick_only}.isdisjoint(created), \
        "zone Opportunity chỉ bị bấc nến chạm KHÔNG được confirm (§5 dùng CLOSE)"
    assert {z[1] for z in f.zones if z[3] in pierced} == {"SMART"}


def test_b2_04b_opportunity_confirms_on_close_and_executes_on_a_later_candle(monkeypatch):
    """§5: confirm tại CLOSE nến T -> `ACTION_PENDING` tạo tại close của T -> execution
    proxy là OPEN của nến ĐẦU TIÊN tại/sau (user_delay + funding_delay). Không có fill nào
    xảy ra trong chính nến confirm.
    """
    res, probe = run_case(_two_month_days({"price": 81.0}), monkeypatch, contribution=CONTRIB)
    opp_buys = [p for p in res.purchases if p["source"] == "OPPORTUNITY"]
    assert opp_buys, "tiền đề: phải có fill Opportunity"

    for p in opp_buys:
        zone_idx = int(p["reason"].split("_")[-1])
        zid = _zone_id(probe, "OPPORTUNITY", zone_idx)
        confirm = [t for t in _pierce_candles(probe, zid) if t < p["ts"]]
        assert confirm, f"không tìm thấy nến confirm cho zone {zid}"
        assert p["ts"] >= confirm[0] + CANDLE, \
            "fill Opportunity rơi vào chính nến confirm — trái §5"


# §21.3 / §6 — "Manual delay, funding delay, proxy ban đêm tại 07:00 local, TTL, action MISSED"

BEHAVIORAL = ExecutionConfig(
    user_delay_seconds=15 * 60, funding_policy="BULK_MONTHLY", funding_delay_seconds=0,
    slippage_bps=0.0, behavioral_model="LOCAL_HOUR", config_name="behavioral_local_hour")


def _night_dip_days():
    """Ladder Smart tạo ở 07:00 Day 2; cú dip lúc 00:00 local Day 5 (giờ ĐÊM theo BT §6)."""
    return [{"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0}, {}, {},
            {"low_dip": 90.0},
            {}, {}]


def _zone_id(probe, ladder_type: str, zone_index: int) -> int:
    return [z.zone_id for l in probe.by_type(ladder_type) for z in l.zones
            if z.zone_index == zone_index][0]


def _pierce_candles(probe, zone_id: int):
    return [f.ts for f in probe.frames if zone_id in probe.pierced_zones(f.ts)]


def test_b2_04c_night_trigger_executes_at_the_first_candle_at_or_after_07_00_local(monkeypatch):
    """BT §6: nhánh 45% của giờ đêm 'thực thi tại OPEN của nến 15m đầu tiên tại hoặc sau
    07:00 local nếu vẫn còn TTL'.

    `run_engine` nhận `behavioral_rng` như một tham số công khai; ở đây nó nhận một RNG
    tất định trả u = 0.5 -> rơi đúng vào nhánh proxy 07:00 của giờ đêm.
    """
    res, probe = run_case(_night_dip_days(), monkeypatch, exec_cfg=BEHAVIORAL,
                          behavioral_rng=FixedRng(0.5), contribution=CONTRIB)
    fills = [p for p in res.purchases if p["reason"] == "SMART_ZONE_1"]
    assert len(fills) == 1, [(local_key(p["ts"]), p["reason"]) for p in res.purchases]
    ts = fills[0]["ts"]
    assert local_key(ts) == "2023-03-05 07:00"
    assert (ts + TZ) % DAY == 7 * H
    # tiền đề: CHÍNH zone này bị xuyên ở một nến ĐÊM, không phải đã ở sẵn 07:00
    trig = _pierce_candles(probe, _zone_id(probe, "SMART", 1))
    assert trig, "tiền đề: phải có nến trigger cho S1"
    hour = int(((trig[0] + TZ) % DAY) // H)
    assert hour >= 23 or hour <= 6, f"nến trigger phải thuộc giờ đêm, có {hour}"
    assert local_key(trig[0]) == "2023-03-05 00:00"
    # và proxy đặt fill ĐÚNG nến 07:00 đầu tiên sau đó, không sớm hơn, không muộn hơn
    assert ts == trig[0] + (7 * H - 900) + 900, "execute_at = close(T) + seconds_to_7am"


def test_b2_04d_behavioral_missed_releases_the_reservation_at_ttl(monkeypatch):
    """BT §6: 5% (ngày) / 20% (đêm) action trở thành MISSED. §21.3 đòi test cho 'action
    MISSED': trạng thái zone MISSED, reserve được trả lại pool, bộ đếm khớp.
    """
    res, probe = run_case(_night_dip_days(), monkeypatch, exec_cfg=BEHAVIORAL,
                          behavioral_rng=FixedRng(0.97), contribution=CONTRIB)
    missed = [d for d in res.decision_log
              if d["reason_code"] in ("ACTION_MISSED", "ACTION_TTL_EXPIRED")]
    assert missed, "u = 0.97 phải rơi vào nhánh MISSED ở cả giờ ngày lẫn giờ đêm"
    assert res.counters["missed_actions"] == len(missed)
    assert res.counters["executed_actions"] == 0
    assert [p for p in res.purchases if p["source"] == "SMART"] == []

    lad = probe.by_type("SMART")[0]
    assert {z.status for z in lad.zones if z.zone_index in (0, 1)} == {"MISSED"}
    assert all(z.reserved_vnd == pytest.approx(0.0, abs=1e-12)
               for z in lad.zones if z.status == "MISSED")

    # TTL: MISSED xảy ra ĐÚNG tại mốc `close(nến trigger) + action_ttl_seconds` (§5/§6).
    # `close(T) = T + 900`, và TTL 12h là bội số của nến nên mốc rơi đúng lên lưới.
    ttl = BEHAVIORAL.action_ttl_seconds
    for d in missed:
        pierced = _pierce_candles(probe, d["zone_id"])
        assert pierced, f"zone {d['zone_id']} không có nến trigger nào"
        assert d["timestamp_utc"] == pierced[0] + CANDLE + ttl, (
            local_key(d["timestamp_utc"]), local_key(pierced[0]))
    first = min(d["timestamp_utc"] for d in missed)
    assert local_key(first) == "2023-03-02 19:30"    # trigger 07:15 -> close 07:30 + 12h


@pytest.mark.parametrize("hour,u,expect", [
    # 07:00–22:59 — 50% <= 1h, 30% <= 4h, 15% <= 12h, 5% MISSED
    (12, 0.00, ("uniform", 0.0, 1 * H)),
    (12, 0.49, ("uniform", 0.0, 1 * H)),
    (12, 0.50, ("uniform", 1 * H, 4 * H)),
    (12, 0.79, ("uniform", 1 * H, 4 * H)),
    (12, 0.80, ("uniform", 4 * H, 12 * H)),
    (12, 0.94, ("uniform", 4 * H, 12 * H)),
    (12, 0.95, ("missed", None, None)),
    (12, 0.99, ("missed", None, None)),
    # 23:00–06:59 — 10% <= 1h, 25% <= 4h, 45% proxy 07:00, 20% MISSED
    (2, 0.00, ("uniform", 0.0, 1 * H)),
    (2, 0.09, ("uniform", 0.0, 1 * H)),
    (2, 0.10, ("uniform", 1 * H, 4 * H)),
    (2, 0.34, ("uniform", 1 * H, 4 * H)),
    (2, 0.35, ("proxy", None, None)),
    (2, 0.79, ("proxy", None, None)),
    (2, 0.80, ("missed", None, None)),
    (23, 0.50, ("proxy", None, None)),
])
def test_b2_04e_behavioral_distribution_matches_the_spec_table(hour, u, expect):
    """BT §6 bảng phân phối, đọc theo đúng các mốc xác suất của spec.

    Đây là hàm production `execution.behavioral_delay_seconds` — không phải bản dựng lại.
    """
    kind, lo, hi = expect
    secs_to_7 = 5 * H
    ttl = 12 * H
    got = behavioral_delay_seconds(hour, FixedRng(u), secs_to_7, ttl)
    if kind == "missed":
        assert got == MISSED
    elif kind == "proxy":
        assert got == secs_to_7
    else:
        assert behavioral_delay_seconds(hour, FixedRng(u, "low"), secs_to_7, ttl) == lo
        assert behavioral_delay_seconds(hour, FixedRng(u, "high"), secs_to_7, ttl) == hi


def test_b2_04f_night_proxy_becomes_missed_when_it_would_outlive_the_ttl():
    """BT §6: nhánh proxy 07:00 chỉ được dùng 'nếu vẫn còn TTL'; ngoài TTL thì MISSED.

    Ghi nhận đi kèm (xem `PROJECT/HARDENING_BACKLOG.md` H-40): với `action_ttl_seconds`
    = 12h baseline, `seconds_to_7am` của mọi giờ đêm (23:00–06:59) tối đa là 8h, nên nhánh
    này KHÔNG tới lượt chạy trên cấu hình baseline. Nó chỉ tới lượt khi TTL bị hạ xuống —
    một chiều mà lưới Gate 3 đóng băng không biến thiên. Vì vậy nhánh được kiểm ở tầng hàm.
    """
    assert behavioral_delay_seconds(2, FixedRng(0.5), 7 * H, 12 * H) == 7 * H
    assert behavioral_delay_seconds(2, FixedRng(0.5), 7 * H, 4 * H) == MISSED
    assert behavioral_delay_seconds(2, FixedRng(0.5), 4 * H, 4 * H) == 4 * H   # biên: '<=' TTL


# ===================================================================== CHECK-B2-05
# §21.3 — "Cooldown và override, bao gồm tần suất override trong CRASH"

def _crash_override_days(day6_price: float):
    return [
        {"price": 100.0, "oscore": 20.0, "return7": 0.00},
        {"oscore": 75.0},
        {"oscore": 69.0},
        {},
        {"oscore": 80.0, "return7": -0.16, "price": 100.5},      # CRASH entry
        {"oscore": 50.0, "return7": -0.05, "price": day6_price},  # trong 48h cooldown
        {}, {},
        {"return7": -0.08},
        {},
        {"return7": -0.11},
        {}, {}, {},
    ]


def test_b2_05a_cooldown_holds_a_pierced_zone_and_override_releases_it_in_crash(monkeypatch):
    """ST §15 + CONVENTIONS #6: trong cooldown, zone bị xuyên chuyển TRIGGERED nhưng
    KHÔNG tạo action; override (`CurrentPrice <= LastExecutionPrice x (1 - 7%)`) mở khoá.

    Cả hai vế chạy TRONG CRASH, nên đây đồng thời là bằng chứng cho 'tần suất override
    trong CRASH' mà §21.3 đòi.
    """
    res, probe = run_case(_crash_override_days(90.0), monkeypatch, contribution=CONTRIB)

    crash_buys = [p for p in res.purchases if p["source"] == "CRASH"]
    assert len(crash_buys) == 2, [(local_key(p["ts"]), p["reason"]) for p in crash_buys]
    first, second = crash_buys
    assert first["reason"] == "CRASH_ZONE_0" and second["reason"] == "CRASH_ZONE_1"
    # fill thứ hai nằm TRONG cửa sổ cooldown 48h của fill thứ nhất
    assert second["ts"] - first["ts"] < 48 * H

    ov = [d for d in res.decision_log if d["reason_code"] == "COOLDOWN_OVERRIDE"]
    assert ov, "không có sự kiện override nào được ghi"
    assert {d["market_regime"] for d in ov} == {"CRASH"}
    assert res.counters["cooldown_override"]["CRASH"] == 1, res.counters["cooldown_override"]
    assert sum(res.counters["cooldown_override"].values()) == 1, \
        "override đếm theo SỰ KIỆN một cycle, không theo từng zone (ST §15 / F-031)"

    # Giá override thoả đúng ngưỡng 7% so với giá execution gần nhất.
    assert second["price"] <= first["price"] * (1 - 0.07) + 1e-9

    # Trước khi override kích hoạt, zone bị xuyên GIỮ TRIGGERED chứ không bị bỏ.
    ts_ov = min(d["timestamp_utc"] for d in ov)
    prev = probe.frames[probe.frame_index(ts_ov)]
    assert any(z[5] == "TRIGGERED" for z in prev.zones), \
        "phải quan sát được trạng thái GIỮ-TRIGGERED do cooldown"


def test_b2_05b_without_override_the_cooldown_blocks_the_fill_entirely(monkeypatch):
    """Đối chứng: cùng kịch bản, mức giảm 3,5% < 7% -> không override -> zone không được
    fill trong cooldown, và cuối Recovery bị CANCEL (vốn trả về pool).
    """
    res, probe = run_case(_crash_override_days(97.0), monkeypatch, contribution=CONTRIB)
    crash_buys = [p for p in res.purchases if p["source"] == "CRASH"]
    assert len(crash_buys) == 1 and crash_buys[0]["reason"] == "CRASH_ZONE_0"
    assert sum(res.counters["cooldown_override"].values()) == 0
    assert [d for d in res.decision_log if d["reason_code"] == "COOLDOWN_OVERRIDE"] == []
    lad = probe.by_type("CRASH")[0]
    assert [z.status for z in lad.zones] == ["EXECUTED", "CANCELLED", "CANCELLED", "CANCELLED"]
    assert probe.pool("OPPORTUNITY").reserved == pytest.approx(0.0, abs=1e-9)


# §21.3 — "Crash funding unavailable scenario"

P2P_UNAVAILABLE = ExecutionConfig(
    user_delay_seconds=4 * 3600, funding_policy="ON_DEMAND", funding_delay_seconds=3600,
    p2p_unavailable_in_crash=True, config_name="stress_p2p_unavailable_in_crash")
P2P_AVAILABLE = ExecutionConfig(
    user_delay_seconds=4 * 3600, funding_policy="ON_DEMAND", funding_delay_seconds=3600,
    p2p_unavailable_in_crash=False, config_name="ctl_p2p_available")


def test_b2_05c_crash_funding_unavailable_turns_every_crash_action_into_missed(monkeypatch):
    """BT §5: 'khi ở CRASH và action cần funding, funding có thể không khả dụng suốt TTL
    và action trở thành MISSED'. Scenario stress riêng, đối chứng là chính cấu hình đó với
    cờ tắt.
    """
    days = _crash_override_days(90.0)
    res_stress, probe_s = run_case(days, monkeypatch, exec_cfg=P2P_UNAVAILABLE,
                                   contribution=CONTRIB)
    res_ctl, probe_c = run_case(days, monkeypatch, exec_cfg=P2P_AVAILABLE,
                                contribution=CONTRIB)

    # đối chứng: cùng dataset, cùng ma sát, chỉ khác cờ -> CÓ fill Crash
    assert [p for p in res_ctl.purchases if p["source"] == "CRASH"], \
        "đối chứng không có fill Crash: kịch bản không phân biệt được cờ"
    # stress: KHÔNG fill Crash nào, và mọi action Crash kết thúc ở MISSED
    assert [p for p in res_stress.purchases if p["source"] == "CRASH"] == []
    assert res_stress.counters["missed_actions"] >= 1
    lad = probe_s.by_type("CRASH")[0]
    assert any(z.status == "MISSED" for z in lad.zones)
    assert all(z.status != "EXECUTED" for z in lad.zones)

    # vốn không bị khoá: mọi reserve của Crash ladder quay về pool
    assert probe_s.pool("OPPORTUNITY").reserved == pytest.approx(0.0, abs=1e-9)
    assert all(z.reserved_vnd == pytest.approx(0.0, abs=1e-12)
               for z in lad.zones if z.status in ("MISSED", "CANCELLED"))
    # và không đường nào biến funding-unavailable thành fill ở giá khác
    assert res_stress.counters["executed_actions"] < res_ctl.counters["executed_actions"]


# ===================================================================== CHECK-B2-06
# §21.3 — "Nhãn STRESSED [F1]: đúng điều kiện, không có hiệu ứng execution"

def _strip(purchases):
    return [{k: v for k, v in p.items() if k != "regime"} for p in purchases]


def test_b2_06_stressed_label_has_no_execution_effect_permanent_regression(monkeypatch):
    """[F1] ST §17.3 — lưới an toàn THƯỜNG TRỰC cho một mệnh đề ĐÃ TỪNG BỊ BÁC BỎ (F-001).

    Phép phản chứng đi theo chiều NGƯỢC với test của WP-A3 (vốn ÉP nhãn STRESSED bật lên):
    ở đây nhãn STRESSED phát sinh TỰ NHIÊN từ dữ liệu, và run đối chứng LOẠI BỎ nó
    (STRESSED -> NORMAL). Nếu bất kỳ nhánh execution nào đọc nhãn, hai run sẽ lệch.

    Bề mặt so sánh rộng hơn: ngoài purchase/ladder/ledger/counter, còn cả
    `execution_state_timeline` (chiều WP-C2) và `market_snapshots`.
    """
    days = _crash_override_days(90.0)

    def run(collapse: bool):
        with pytest.MonkeyPatch.context() as mp:
            if collapse:
                real = RegimeTracker._derive_label
                mp.setattr(RegimeTracker, "_derive_label",
                           lambda self, r7, r24: ("NORMAL" if real(self, r7, r24) == "STRESSED"
                                                  else real(self, r7, r24)))
            return run_case(days, mp, contribution=CONTRIB)

    res_a, probe_a = run(False)
    res_b, probe_b = run(True)

    # tiền đề 1: nhãn STRESSED thực sự xuất hiện ở run A và biến mất ở run B
    labels_a = [lab for _, lab in res_a.regime_timeline]
    labels_b = [lab for _, lab in res_b.regime_timeline]
    assert "STRESSED" in labels_a and "STRESSED" not in labels_b
    # tiền đề 2: run A có sự kiện thật trên đủ các bề mặt để phép so không rỗng
    assert {p["source"] for p in res_a.purchases} >= {"BASE", "SMART", "OPPORTUNITY", "CRASH"}
    assert sum(res_a.counters["cooldown_override"].values()) >= 1
    assert {l.type for l in probe_a.ladders} == {"SMART", "OPPORTUNITY", "CRASH"}

    # 1) execution: từng giao dịch identical (trừ trường nhãn reporting)
    assert _strip(res_a.purchases) == _strip(res_b.purchases)
    assert res_a.eth_total == res_b.eth_total
    assert res_a.contributions == res_b.contributions
    assert res_a.monthly_deployments == res_b.monthly_deployments
    assert res_a.cash_samples == res_b.cash_samples
    assert res_a.opp_cap_samples == res_b.opp_cap_samples

    # 2) counters: mọi bộ đếm bằng nhau; riêng override so TỔNG vì phân rã theo nhãn
    #    chính là reporting decomposition của BT §16
    for k, v in res_a.counters.items():
        if k == "cooldown_override":
            assert sum(v.values()) == sum(res_b.counters[k].values())
        else:
            assert v == res_b.counters[k], k

    # 3) ladder / zone: cùng cấu trúc và cùng kết cục
    assert [(l.type, l.anchor_price, l.spacing_pct, l.created_at, l.eligible_capital_vnd,
             l.status, [(z.zone_index, z.target_price, z.target_vnd, z.status, z.pool)
                        for z in l.zones]) for l in probe_a.ladders] == \
           [(l.type, l.anchor_price, l.spacing_pct, l.created_at, l.eligible_capital_vnd,
             l.status, [(z.zone_index, z.target_price, z.target_vnd, z.status, z.pool)
                        for z in l.zones]) for l in probe_b.ladders]

    # 4) ledger từng pool identical (quyền dùng vốn / unlock / limit)
    for name in ("BASE", "SMART", "OPPORTUNITY"):
        assert probe_a.pool(name).ledger == probe_b.pool(name).ledger

    # 5) chiều Execution State (WP-C2) độc lập với nhãn (ST §16 'lưu riêng')
    assert res_a.execution_state_timeline == res_b.execution_state_timeline
    strip_regime = [{k: v for k, v in s.items() if k != "market_regime"}
                    for s in res_a.market_snapshots]
    assert strip_regime == [{k: v for k, v in s.items() if k != "market_regime"}
                            for s in res_b.market_snapshots]
