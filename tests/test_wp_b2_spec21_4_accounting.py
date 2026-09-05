"""WP-B2 — Backtest §21.4 (Accounting và evaluation): những requirement CHƯA CÓ TEST.

  CHECK-B2-07  data gap và delayed Base fill;
               Benchmark C [F4] — mỗi trigger bắn tối đa MỘT lần mỗi chu kỳ, chu kỳ reset
               đúng luật

Phần "data gap và delayed Base fill" đã có độ phủ đáng kể ở WP-A4 (nhãn `EXECUTION_DATA_GAP`
/ `DELAYED_DATA_FILL` trên bản ghi, tranche Base không bị bỏ). Gói này KHÔNG viết lại phần
đó; nó đóng đúng câu ĐẦU TIÊN của BT §18 mà chưa test nào chạm tới:

    "Nến 15m thiếu: KHÔNG interpolate OHLC để trigger zone."

Bảng đối chiếu đầy đủ §21 → test nằm ở `docs/CONVENTIONS.md`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from eth_dca_os.benchmarks import run_benchmark_A, run_benchmark_C
from wp_a3_harness import build_dataset
from wp_b2_probe import CANDLE, local_key, run_case

CONTRIB = 100.0


# ===================================================================== CHECK-B2-07 (a)
# BT §18 — "Nến 15m thiếu: KHÔNG interpolate OHLC để trigger zone"

def _gap_days():
    """Ladder Smart ở Day 2; cú dip xuyên S1 nằm TRỌN trong Day 5."""
    return [{"price": 100.0, "oscore": 20.0, "return7": 0.0},
            {"oscore": 60.0}, {}, {},
            {"low_dip": 90.0},
            {}, {}]


DAY5_GAP = [("2023-03-05 00:00", "2023-03-05 23:59")]


def test_b2_07a_a_missing_candle_window_is_not_interpolated_into_a_trigger(monkeypatch):
    """Cùng một `day_specs`, hai dataset: đầy đủ và bị khoét trọn ngày có cú dip.

    Dataset đầy đủ: S1 bị xuyên và fill. Dataset bị khoét: engine KHÔNG được dựng lại cú
    dip từ hai đầu lỗ hổng — S1 phải còn nguyên ACTIVE. Không có phép so này thì "không
    interpolate" chỉ là một câu trong spec.
    """
    res_full, probe_full = run_case(_gap_days(), monkeypatch, contribution=CONTRIB)
    res_gap, probe_gap = run_case(_gap_days(), monkeypatch, contribution=CONTRIB,
                                  drop=DAY5_GAP)

    # tiền đề: lỗ hổng là THẬT và đúng bằng một ngày nến 15m
    assert len(probe_full.grid) - len(probe_gap.grid) == 96
    assert not [f for f in probe_gap.frames if local_key(f.ts).startswith("2023-03-05")]

    s1_full = [z for l in probe_full.by_type("SMART") for z in l.zones if z.zone_index == 1][0]
    s1_gap = [z for l in probe_gap.by_type("SMART") for z in l.zones if z.zone_index == 1][0]
    assert s1_full.target_price == pytest.approx(s1_gap.target_price)

    # dataset đầy đủ: giá thật xuống dưới target -> zone chạy hết vòng đời
    assert s1_full.status == "EXECUTED"
    assert [p for p in res_full.purchases if p["reason"] == "SMART_ZONE_1"]
    # dataset bị khoét: không nến nào tồn tại để xuyên -> zone còn nguyên
    assert s1_gap.status == "ACTIVE"
    assert [p for p in res_gap.purchases if p["reason"] == "SMART_ZONE_1"] == []
    assert res_gap.counters["triggered_actions"] < res_full.counters["triggered_actions"]

    # và không nến nào của engine nằm ngoài dataset (không nến tổng hợp nào được chèn)
    ds_ts = set(probe_gap.candles["ts"].tolist())
    assert all(f.ts in ds_ts for f in probe_gap.frames)


def test_b2_07b_delayed_base_fill_lands_on_a_real_candle_after_the_gap(monkeypatch):
    """BT §18 / ST §9 [F3]: tranche Base rơi vào gap được giải ngân ở nến HỢP LỆ ĐẦU TIÊN
    sau gap — một nến CÓ THẬT trong dataset, không phải một mốc 12:00 được dựng lại.
    """
    specs = [{"price": 100.0, "oscore": 20.0, "return7": 0.0}] + [{} for _ in range(5)]
    drop = [("2023-03-03 12:00", "2023-03-03 12:59")]     # khoét 12:00, 12:15, 12:30, 12:45
    res, probe = run_case(specs, monkeypatch, contribution=CONTRIB, drop=drop)

    base = [p for p in res.purchases if p["source"] == "BASE"]
    assert len(base) == 1
    rec = base[0]
    assert rec["reason"] == "BASE_SCHEDULE"
    assert "DELAYED_DATA_FILL" in rec["tags"]
    assert local_key(rec["ts"]) == "2023-03-03 13:00"
    assert rec["missing_candles_before"] == 4

    ds_ts = set(probe.candles["ts"].tolist())
    assert rec["ts"] in ds_ts, "fill phải rơi vào một nến CÓ THẬT"
    k = probe.grid.index(rec["ts"])
    assert probe.grid[k] - probe.grid[k - 1] == pytest.approx(5 * CANDLE), \
        "nến trước fill phải cách 5 nến — tức fill nằm ngay sau lỗ hổng"
    # giá thực thi là OPEN THẬT của nến đó (slippage = 0 ở gate1_low_friction)
    assert rec["price"] == pytest.approx(probe.candle(rec["ts"])["open"])

    # đối chứng: dataset liên tục -> chạy đúng 12:00 và không mang nhãn fill trễ
    res_clean, _ = run_case(specs, monkeypatch, contribution=CONTRIB)
    clean = [p for p in res_clean.purchases if p["source"] == "BASE"][0]
    assert local_key(clean["ts"]) == "2023-03-03 12:00"
    assert clean["tags"] == [] and clean["missing_candles_before"] == 0
    assert clean["nominal"] == pytest.approx(rec["nominal"]), \
        "lỗ hổng không được làm đổi SỐ TIỀN của tranche, chỉ đổi thời điểm"


# ===================================================================== CHECK-B2-07 (b)
# BT §12 / §21.4 — "Benchmark C: mỗi trigger bắn tối đa một lần mỗi chu kỳ,
#                   chu kỳ reset đúng luật [F4]"

N_DAYS = 150
FIRE30_A, RESET_A, FIRE30_B, FIRE45_B, RESET_B, FIRE30_C = 40, 60, 62, 80, 90, 92


def _benchmark_c_inputs(with_resets: bool):
    """Dataset 15m + bảng indicator daily điều khiển tay cho Benchmark C.

    Ánh xạ ngày: `run_benchmark_C` quy một nến về `normalize(mốc đầu ngày LOCAL tính bằng
    UTC)`, tức ngày UTC LIỀN TRƯỚC ngày local. Vì vậy hàng indicator thứ `k` (bắt đầu từ
    2022-12-31) tương ứng ngày local `2023-01-01 + k`.

    Kịch bản `with_resets=True`:
      - ngày 40–59: `dd365 = -0.35` -> trigger -30% ĐƯỢC PHÉP bắn một lần
      - ngày 60: `close >= ma200` -> chu kỳ mới
      - ngày 62–79: `dd365 = -0.35` -> trigger -30% bắn lại (chu kỳ 2)
      - ngày 80–89: `dd365 = -0.50` -> trigger -45% bắn (cùng chu kỳ 2, trigger KHÁC)
      - ngày 90: `close >= ma200` -> chu kỳ mới
      - ngày 92+: `dd365 = -0.35` -> trigger -30% bắn lại (chu kỳ 3)
    `with_resets=False` giữ nguyên chuỗi `dd365` nhưng KHÔNG bao giờ cho `close >= ma200`.
    """
    specs = [{"price": 100.0, "oscore": 20.0, "return7": 0.0}] + \
            [{} for _ in range(N_DAYS - 1)]
    ds, _scores, start, end = build_dataset(specs, first_local_day="2023-01-01")

    idx = pd.date_range("2022-12-31", periods=N_DAYS, freq="D", tz="UTC")
    dd = np.zeros(N_DAYS)
    ma = np.full(N_DAYS, 1000.0)
    close = np.full(N_DAYS, 100.0)
    for k in range(FIRE30_A, RESET_A):
        dd[k] = -0.35
    for k in range(FIRE30_B, FIRE45_B):
        dd[k] = -0.35
    for k in range(FIRE45_B, RESET_B):
        dd[k] = -0.50
    for k in range(FIRE30_C, N_DAYS):
        dd[k] = -0.35
    if with_resets:
        close[RESET_A] = 2000.0
        close[RESET_B] = 2000.0
    ind = pd.DataFrame({"dd365": dd, "ma200": ma, "close": close}, index=idx)
    return ds, ind, start, end


def _split(ds, ind, start, end):
    """Tách purchase của Benchmark C thành (mua theo tháng, lần bắn dip).

    Mốc mua theo tháng đọc từ Benchmark A — cùng `_monthly_buy_points`, nên phép tách này
    không phải một bản dựng lại của chính hàm đang được kiểm.
    """
    c = run_benchmark_C(ds, ind, start, end)
    monthly_ts = {p["ts"] for p in run_benchmark_A(ds, start, end)["purchases"]}
    dips = [p for p in c["purchases"] if p["ts"] not in monthly_ts]
    months = [p for p in c["purchases"] if p["ts"] in monthly_ts]
    return c, months, dips


def _local_day(ts) -> str:
    return pd.Timestamp(ts + 7 * 3600, unit="s").strftime("%Y-%m-%d")


def test_b2_07c_benchmark_c_each_trigger_fires_once_per_cycle_and_resets_by_rule():
    """[F4]: bốn lần bắn, đúng bốn — không phải một lần mỗi ngày thoả điều kiện."""
    ds, ind, start, end = _benchmark_c_inputs(with_resets=True)
    c, months, dips = _split(ds, ind, start, end)

    assert len(months) == 5, "tiền đề: đúng năm mốc mua theo tháng trong cửa sổ"
    assert [_local_day(p["ts"]) for p in dips] == [
        "2023-02-10",   # chu kỳ 1, trigger -30%
        "2023-03-04",   # chu kỳ 2, trigger -30% (sau reset ngày 2023-03-02)
        "2023-03-22",   # chu kỳ 2, trigger -45% (trigger KHÁC, cùng chu kỳ)
        "2023-04-03",   # chu kỳ 3, trigger -30% (sau reset ngày 2023-04-01)
    ], [_local_day(p["ts"]) for p in dips]

    # Chu kỳ 1 kéo dài 20 ngày liên tục dd <= -30% mà chỉ bắn MỘT lần.
    window = [p for p in dips if "2023-02-10" <= _local_day(p["ts"]) <= "2023-03-01"]
    assert len(window) == 1

    # Mỗi lần bắn tiêu đúng 50% reserve đang có, và bảo toàn vốn theo §12.1.
    assert c["contributed"] == pytest.approx(500.0)
    spent = sum(p["nominal"] for p in c["purchases"])
    assert spent + c["final_reserve"] == pytest.approx(c["contributed"])
    assert c["final_reserve"] >= 0


def test_b2_07d_benchmark_c_without_a_reset_each_trigger_fires_at_most_once_ever():
    """Đối chứng của "chu kỳ reset đúng luật": bỏ mọi lần `close >= ma200` thì hai trigger
    chỉ còn bắn ĐÚNG MỘT lần trên toàn bộ cửa sổ, dù điều kiện dd thoả suốt 90 ngày.
    """
    ds, ind, start, end = _benchmark_c_inputs(with_resets=False)
    c, months, dips = _split(ds, ind, start, end)

    assert len(months) == 5
    assert [_local_day(p["ts"]) for p in dips] == ["2023-02-10", "2023-03-22"], \
        [_local_day(p["ts"]) for p in dips]
    assert c["contributed"] == pytest.approx(500.0)
    spent = sum(p["nominal"] for p in c["purchases"])
    assert spent + c["final_reserve"] == pytest.approx(c["contributed"])


def test_b2_07e_benchmark_c_reset_needs_a_fired_trigger_first():
    """`close >= ma200` khi CHƯA trigger nào bắn không tạo ra một 'chu kỳ' nào cả — nó
    không được biến thành một đường làm trigger bắn thêm lần nữa.
    """
    ds, ind, start, end = _benchmark_c_inputs(with_resets=True)
    early = ind.copy()
    early.iloc[10, early.columns.get_loc("close")] = 2000.0   # reset "rỗng" trước mọi dip
    c_ref, _m, dips_ref = _split(ds, ind, start, end)
    c_new, _m2, dips_new = _split(ds, early, start, end)
    assert [p["ts"] for p in dips_new] == [p["ts"] for p in dips_ref]
    assert c_new["eth"] == pytest.approx(c_ref["eth"])
