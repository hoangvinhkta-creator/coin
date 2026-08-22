"""Backtest §21.4: đúng chín window pre-OOS, OOS tách, PrimaryMedian đúng §4.1."""
from datetime import date

from eth_dca_os.windows import (
    PRE_OOS_CUTOFF,
    anchor_set_medians,
    coverage_table,
    gate_windows,
    oos_months,
    pooled_median,
    primary_median,
    short_oos,
)


def test_nine_windows_by_anchor():
    wins = gate_windows()
    assert len(wins) == 9
    per_anchor = {off: [w for w in wins if w.anchor_offset == off] for off in (0, 6, 12, 18)}
    assert [len(per_anchor[k]) for k in (0, 6, 12, 18)] == [3, 2, 2, 2]
    for w in wins:
        assert w.end <= PRE_OOS_CUTOFF
    # đối chiếu đúng bảng Backtest §3
    w = {x.window_id: x for x in wins}
    assert (w["W1"].start, w["W1"].end) == (date(2019, 1, 1), date(2020, 12, 31))
    assert (w["W3"].start, w["W3"].end) == (date(2023, 1, 1), date(2024, 12, 31))
    assert (w["W5"].start, w["W5"].end) == (date(2021, 7, 1), date(2023, 6, 30))
    assert (w["W9"].start, w["W9"].end) == (date(2022, 7, 1), date(2024, 6, 30))


def test_coverage_table():
    cov = {r["month"]: r["windows"] for r in coverage_table()}
    assert cov["2019-03"] == 1
    assert cov["2019-09"] == 2
    assert cov["2020-03"] == 3
    assert cov["2021-06"] == 4   # phần giữa đếm gấp 4
    assert cov["2023-09"] == 3
    assert cov["2024-03"] == 2
    assert cov["2024-10"] == 1


def test_primary_vs_pooled_median_skewed():
    # Phân phối lệch: anchor +0 có 3 giá trị cao, các anchor khác thấp
    vals = {"W1": 110.0, "W2": 111.0, "W3": 112.0,
            "W4": 100.0, "W5": 101.0,
            "W6": 99.0, "W7": 100.0,
            "W8": 98.0, "W9": 99.0}
    asm = anchor_set_medians(vals)
    assert asm[0] == 111.0 and asm[6] == 100.5 and asm[12] == 99.5 and asm[18] == 98.5
    pm = primary_median(vals)
    assert pm == 100.0  # median(111, 100.5, 99.5, 98.5)
    # Phân phối lệch: PrimaryMedian phải KHÁC PooledMedian (Backtest §21.4)
    vals2 = {"W1": 110.0, "W2": 111.0, "W3": 112.0,
             "W4": 100.0, "W5": 102.0,
             "W6": 98.0, "W7": 99.0,
             "W8": 97.0, "W9": 96.0}
    pm2 = primary_median(vals2)      # median(111, 101, 98.5, 96.5) = 99.75
    pooled2 = pooled_median(vals2)   # median của 9 giá trị = 100.0
    assert pm2 == 99.75 and pooled2 == 100.0
    assert pm2 != pooled2


def test_oos_flags():
    assert oos_months(date(2026, 8, 31)) == 20
    assert short_oos(date(2026, 8, 31)) is True
    assert oos_months(date(2026, 12, 31)) == 24
    assert short_oos(date(2026, 12, 31)) is False
