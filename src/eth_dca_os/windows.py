"""Multi-anchor pre-OOS gate windows và các median chống thiên vị — Backtest §3, §4, §8."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

PRE_OOS_CUTOFF = date(2024, 12, 31)
OOS_START = date(2025, 1, 1)
ORIGIN = date(2019, 1, 1)
ANCHOR_OFFSETS_MONTHS = (0, 6, 12, 18)
WINDOW_MONTHS = 24


def _add_months(d: date, months: int) -> date:
    y, m = divmod((d.year * 12 + d.month - 1) + months, 12)
    return date(y, m + 1, d.day)


def _month_end(d: date) -> date:
    from datetime import timedelta
    nxt = _add_months(date(d.year, d.month, 1), 1)
    return nxt - timedelta(days=1)


@dataclass(frozen=True)
class GateWindow:
    window_id: str
    anchor_offset: int
    start: date          # ngày đầu tháng bắt đầu
    end: date            # ngày cuối tháng kết thúc (inclusive)


def gate_windows() -> list[GateWindow]:
    """Đúng chín window 24M theo bốn anchor offset; không window nào kết thúc sau 2024-12-31."""
    windows: list[GateWindow] = []
    n = 0
    for off in ANCHOR_OFFSETS_MONTHS:
        start = _add_months(ORIGIN, off)
        while True:
            end_month_start = _add_months(start, WINDOW_MONTHS - 1)
            end = _month_end(end_month_start)
            if end > PRE_OOS_CUTOFF:
                break
            n += 1
            windows.append(GateWindow(f"W{n}", off, start, end))
            start = _add_months(start, WINDOW_MONTHS)
    return windows


def coverage_table() -> list[dict]:
    """Bảng coverage weight: mỗi tháng pre-OOS xuất hiện trong bao nhiêu window (Backtest §4)."""
    wins = gate_windows()
    rows = []
    m = ORIGIN
    while m <= PRE_OOS_CUTOFF:
        count = sum(1 for w in wins if w.start <= m <= w.end)
        rows.append({"month": m.strftime("%Y-%m"), "windows": count})
        m = _add_months(m, 1)
    return rows


def anchor_set_medians(values_by_window: dict[str, float]) -> dict[int, float]:
    """AnchorSetMedian_k = MEDIAN(metric của các window thuộc anchor set k)."""
    wins = gate_windows()
    out: dict[int, float] = {}
    for off in ANCHOR_OFFSETS_MONTHS:
        vals = [values_by_window[w.window_id] for w in wins if w.anchor_offset == off]
        out[off] = float(np.median(vals))
    return out


def primary_median(values_by_window: dict[str, float]) -> float:
    """PrimaryMedian = MEDIAN của bốn AnchorSetMedian (mỗi anchor set trọng số bằng nhau)."""
    asm = anchor_set_medians(values_by_window)
    return float(np.median([asm[k] for k in ANCHOR_OFFSETS_MONTHS]))


def pooled_median(values_by_window: dict[str, float]) -> float:
    """PooledMedian trên cả 9 window — DESCRIPTIVE ONLY."""
    return float(np.median(list(values_by_window.values())))


def oos_months(oos_end: date) -> int:
    """OOS_Months = số tháng thực tế của giai đoạn OOS (Backtest §8)."""
    return (oos_end.year - OOS_START.year) * 12 + (oos_end.month - OOS_START.month) + 1


def short_oos(oos_end: date) -> bool:
    return oos_months(oos_end) < 24
