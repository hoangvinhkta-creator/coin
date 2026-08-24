"""WP-D1 — Dọn bốn khoản nợ kỹ thuật không ảnh hưởng hành vi (F-028, F-029, F-031, F-034).

Ràng buộc định nghĩa của gói: mỗi test chứng minh finding tồn tại/được sửa ĐÚNG như mô tả,
KHÔNG đổi hành vi mô phỏng ngoài phạm vi đã khai báo (F-031 là số liệu chẩn đoán, ngoại lệ
tường minh — xem CHECK-D1-03/05).
"""
from __future__ import annotations

import sys

import pandas as pd
import pytest

sys.path.insert(0, "tests")
from wp_a3_harness import run_case  # noqa: E402

from eth_dca_os.ladders import Ladder, Zone, ladder_completed  # noqa: E402

DAY = 86400.0
TZ = 7 * 3600


# --------------------------------------------------------------- F-028
def test_f028_smart_expires_at_matches_accounting_month_end(monkeypatch):
    """CHECK-D1-01: Ladder.expires_at của Smart ladder phải đúng cuối accounting month (giờ
    local), không phải ts + 31 ngày cố định. Đồng thời expiry THẬT của engine (dựa trên phát
    hiện month rollover, không đọc field này) phải giữ nguyên hành vi."""
    # 2023-04 có 30 ngày: "ts + 31 ngày" lệch khỏi cuối tháng thật ~1 ngày, đủ để phân biệt
    # với "đúng cuối accounting month" (tránh trùng hợp của tháng 31 ngày như March).
    day_specs = [{"price": 100.0, "oscore": 60.0}] + [{} for _ in range(33)]
    res, rec = run_case(day_specs, monkeypatch, first_local_day="2023-04-01")
    smart_lads = [l for l in rec.ladders if l.type == "SMART"]
    assert len(smart_lads) >= 1
    lad = smart_lads[0]
    created_local = pd.Timestamp(lad.created_at + TZ, unit="s")
    expected_next_month_local = (created_local.replace(day=1)
                                  + pd.DateOffset(months=1))
    expected_expires_at = expected_next_month_local.value / 1e9 - TZ
    assert lad.expires_at == pytest.approx(expected_expires_at), (
        f"expires_at phải là đúng cuối accounting month (local); "
        f"got {lad.expires_at}, expected {expected_expires_at}")
    # engine vẫn phải EXPIRE ladder đúng lúc rollover tháng, hệt như trước khi sửa (field
    # không được đọc bởi expire_smart_ladders — hành vi này độc lập với giá trị field)
    assert lad.status == "EXPIRED"


# --------------------------------------------------------------- F-029
def test_f029_ladder_completed_partially_filled_not_terminal():
    """CHECK-D1-02: PARTIALLY_FILLED không còn được coi là trạng thái kết thúc — phần chưa
    fill còn RESERVED tới hết TTL (ST §8), ladder KHÔNG được coi là completed khi còn zone
    PARTIALLY_FILLED."""
    def _lad(statuses):
        zones = [Zone(zone_id=i, ladder_id=1, zone_index=i, target_price=100.0,
                       allocation_pct=1.0 / len(statuses), target_vnd=10.0, pool="SMART",
                       status=s) for i, s in enumerate(statuses)]
        return Ladder(1, "SMART", 100.0, 0.05, 0.0, None, 60.0, 30.0, zones=zones)

    # còn một zone PARTIALLY_FILLED -> ladder KHÔNG completed (F-029: trước fix, đây trả True)
    assert ladder_completed(_lad(["EXECUTED", "PARTIALLY_FILLED", "CANCELLED"])) is False
    # mọi zone đã ở trạng thái kết thúc THẬT (EXECUTED/CANCELLED/EXPIRED/MISSED),
    # có ít nhất một EXECUTED -> completed
    assert ladder_completed(_lad(["EXECUTED", "CANCELLED", "EXPIRED"])) is True
    # không zone nào EXECUTED -> không completed dù mọi zone đã kết thúc
    assert ladder_completed(_lad(["CANCELLED", "EXPIRED", "MISSED"])) is False
    # còn zone đang mở (ACTIVE/TRIGGERED/...) -> không completed
    assert ladder_completed(_lad(["EXECUTED", "ACTIVE", "CANCELLED"])) is False


# --------------------------------------------------------------- F-031
def test_f031_cooldown_override_counts_once_per_event_not_per_zone(monkeypatch):
    """CHECK-D1-03: một sự kiện override (một cycle, cooldown+override đồng thời đúng) tạo
    action cho NHIỀU zone trong CÙNG cycle -> bộ đếm chỉ tăng ĐÚNG MỘT LẦN cho sự kiện đó,
    không phải một lần cho mỗi zone.

    Kịch bản: Day1 tạo Smart ladder (anchor=100, spacing~0.06 -> S0=100, S1=94, S2=88).
    Day2 dip vừa đủ trigger MỘT MÌNH S0 -> exec -> mở cooldown 48h, last_exec_price~100.
    Day3 dip sâu (85) trigger CẢ S1 và S2 cùng lúc; candle đầu day3 open=100 (chưa đủ chiết
    khấu -> override_ok=False, hai zone giữ TRIGGERED); candle kế (open=90, đã đủ chiết khấu
    7%) -> in_cooldown=True và override_ok=True CHO CẢ HAI zone trong CÙNG một cycle."""
    day_specs = [{"price": 100.0, "oscore": 60.0}, {"price": 100.0, "low_dip": 99.0},
                 {"price": 90.0, "low_dip": 85.0}] + [{} for _ in range(3)]
    res, rec = run_case(day_specs, monkeypatch)

    ov_log = [d for d in res.decision_log if d["reason_code"] == "COOLDOWN_OVERRIDE"]
    assert len(ov_log) == 2, "tiền đề: đúng hai zone override trong kịch bản (log không đổi)"
    assert ov_log[0]["ts"] == ov_log[1]["ts"], "tiền đề: cùng một cycle/sự kiện"

    total_override = sum(res.counters["cooldown_override"].values())
    assert total_override == 1, (
        f"một sự kiện override tạo action cho nhiều zone phải đếm ĐÚNG MỘT LẦN; "
        f"got {total_override} (counters={res.counters['cooldown_override']})")


# --------------------------------------------------------------- F-034
def test_f034_noon_candles_removed():
    """CHECK-D1-04: `_noon_candles` không còn tồn tại trong benchmarks.py; module vẫn import
    và hoạt động bình thường (các benchmark khác không phụ thuộc hàm này)."""
    import eth_dca_os.benchmarks as bm
    assert not hasattr(bm, "_noon_candles"), "_noon_candles phải bị xoá khỏi benchmarks.py"
