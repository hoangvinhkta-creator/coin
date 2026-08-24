"""Benchmarks A–D và random controls F/G — Backtest §12.

Mọi benchmark nhận CÙNG lịch external contribution (equal capital rule §12.1).
F/G là lightweight replay từ lịch giải ngân đã tính sẵn, KHÔNG chạy lại engine.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import deterministic_hash
from .engine import TZ_OFFSET, NOON, DAY, _epoch_seconds
from .execution import apply_fill


def _candles(dataset, start, end):
    eth15 = dataset["ETHUSDT_15m"]
    ts = _epoch_seconds(eth15["open_time"])
    st = start.tz_localize("UTC").timestamp() if start.tzinfo is None else start.timestamp()
    en = end.tz_localize("UTC").timestamp() if end.tzinfo is None else end.timestamp()
    m = (ts >= st) & (ts < en)
    return ts[m], eth15["open"].to_numpy(float)[m]


def _month_key(local_seconds: float) -> str:
    return pd.Timestamp(local_seconds, unit="s").strftime("%Y-%m")


def _monthly_buy_points(ts: np.ndarray, buy_day: int):
    """(month_key -> candle idx) tại Day `buy_day` 12:00 local (nến hợp lệ đầu tiên sau đó)."""
    local = ts + TZ_OFFSET
    points = {}
    lts = pd.to_datetime(local, unit="s")
    days = lts.day
    tod = local % DAY
    month = pd.Series(lts).dt.strftime("%Y-%m").to_numpy()
    for i in range(len(ts)):
        mk = month[i]
        if mk in points:
            continue
        if (days[i] > buy_day) or (days[i] == buy_day and tod[i] >= NOON):
            points[mk] = i
    return points


def run_benchmark_A(dataset, start, end, contribution=100.0, exec_cfg=None) -> dict:
    """Monthly DCA: 100% contribution mua Day 3 12:00 local."""
    ts, op = _candles(dataset, start, end)
    points = _monthly_buy_points(ts, 3)
    eth = 0.0
    purchases = []
    for mk, i in points.items():
        nominal = contribution
        e, px = _fill(nominal, op[i], exec_cfg)
        eth += e
        purchases.append({"ts": ts[i], "month": mk, "nominal": nominal, "price": px, "eth": e})
    return {"eth": eth, "purchases": purchases, "contributed": contribution * len(points)}


def _fill(nominal, open_price, exec_cfg):
    if exec_cfg is None:
        return nominal / open_price, open_price
    return apply_fill(nominal, open_price, exec_cfg)


def run_benchmark_B(dataset, start, end, contribution=100.0, exec_cfg=None) -> dict:
    """Weekly DCA: contribution/4 mỗi Thứ Hai 12:00 local; Thứ Hai thứ 5 không thêm."""
    ts, op = _candles(dataset, start, end)
    local = ts + TZ_OFFSET
    lts = pd.to_datetime(local, unit="s")
    month = pd.Series(lts).dt.strftime("%Y-%m").to_numpy()
    dow = pd.Series(lts).dt.dayofweek.to_numpy()   # 0 = Monday
    tod = local % DAY
    day_ord = (local // DAY).astype(int)
    eth, purchases = 0.0, []
    bought_days = set()
    count_in_month: dict[str, int] = {}
    for i in range(len(ts)):
        if dow[i] == 0 and tod[i] >= NOON and day_ord[i] not in bought_days:
            mk = month[i]
            k = count_in_month.get(mk, 0)
            if k < 4:
                nominal = contribution / 4
                e, px = _fill(nominal, op[i], exec_cfg)
                eth += e
                purchases.append({"ts": ts[i], "month": mk, "nominal": nominal,
                                  "price": px, "eth": e})
                count_in_month[mk] = k + 1
            bought_days.add(day_ord[i])
    contributed = contribution * len({p["month"] for p in purchases})
    return {"eth": eth, "purchases": purchases, "contributed": contributed}


def run_benchmark_C(dataset, indicators, start, end, contribution=100.0, exec_cfg=None) -> dict:
    """Simple Dip Reserve với ngữ nghĩa chu kỳ [F4]."""
    ts, op = _candles(dataset, start, end)
    points = _monthly_buy_points(ts, 3)
    dd365 = indicators["dd365"]
    ma200 = indicators["ma200"]
    close_d = indicators["close"]
    day_index = indicators.index
    eth, reserve = 0.0, 0.0
    purchases = []
    fired30 = fired45 = False
    # daily walk đồng thời với monthly buys
    di = {d.normalize(): i for i, d in enumerate(day_index)}
    days = pd.to_datetime((ts + TZ_OFFSET) // DAY * DAY - TZ_OFFSET, unit="s", utc=True)
    month_pts = {i: mk for mk, i in points.items()}
    seen_days = set()
    for i in range(len(ts)):
        if i in month_pts:
            nominal = contribution * 0.70
            e, px = _fill(nominal, op[i], exec_cfg)
            eth += e
            reserve += contribution * 0.30
            purchases.append({"ts": ts[i], "nominal": nominal, "price": px, "eth": e})
        dkey = days[i].normalize()
        if dkey in seen_days or dkey not in di:
            continue
        seen_days.add(dkey)
        j = di[dkey]
        dd, ma, cl = dd365.iloc[j], ma200.iloc[j], close_d.iloc[j]
        if not np.isnan(dd):
            if dd <= -0.45 and not fired45 and reserve > 0:
                amt = reserve * 0.5
                e, px = _fill(amt, op[i], exec_cfg)
                eth += e
                reserve -= amt
                fired45 = True
                purchases.append({"ts": ts[i], "nominal": amt, "price": px, "eth": e})
            elif dd <= -0.30 and not fired30 and reserve > 0:
                amt = reserve * 0.5
                e, px = _fill(amt, op[i], exec_cfg)
                eth += e
                reserve -= amt
                fired30 = True
                purchases.append({"ts": ts[i], "nominal": amt, "price": px, "eth": e})
        if (fired30 or fired45) and not np.isnan(ma) and cl >= ma:
            fired30 = fired45 = False   # chu kỳ mới [F4]
    contributed = contribution * len(points)
    return {"eth": eth, "purchases": purchases, "contributed": contributed,
            "final_reserve": reserve}


def run_benchmark_D(dataset, indicators, start, end, contribution=100.0, exec_cfg=None) -> dict:
    """MA200 DCA với RESERVE CAP = 6C (bắt buộc, fix A4)."""
    ts, op = _candles(dataset, start, end)
    points = _monthly_buy_points(ts, 3)
    ma200 = indicators["ma200"]
    close_d = indicators["close"]
    di = {d.normalize(): (ma200.iloc[i], close_d.iloc[i]) for i, d in enumerate(indicators.index)}
    eth, reserve = 0.0, 0.0
    purchases = []
    C = contribution
    for mk, i in points.items():
        dkey = pd.Timestamp((ts[i] + TZ_OFFSET) // DAY * DAY - TZ_OFFSET, unit="s",
                            tz="UTC").normalize()
        ma, cl = di.get(dkey, (np.nan, np.nan))
        if not np.isnan(ma) and cl >= ma:
            deploy = 0.70 * C
            reserve += 0.30 * C
        else:
            extra = min(0.30 * C, reserve)
            deploy = C + extra
            reserve -= extra
        if reserve > 6 * C:   # reserve cap: phần vượt giải ngân ngay trong tháng
            deploy += reserve - 6 * C
            reserve = 6 * C
        e, px = _fill(deploy, op[i], exec_cfg)
        eth += e
        purchases.append({"ts": ts[i], "month": mk, "nominal": deploy, "price": px, "eth": e})
    return {"eth": eth, "purchases": purchases, "contributed": C * len(points),
            "final_reserve": reserve}


# --------------------------------------------------- Random controls (lightweight replay)

def random_timing_control(dataset, monthly_deployments: dict, start, end,
                          n_sims=1000, master_seed=42, exec_cfg=None) -> dict:
    """Control F: giữ tổng giải ngân theo tháng của V2, random timestamp mua trong tháng."""
    ts, op = _candles(dataset, start, end)
    local = ts + TZ_OFFSET
    month = pd.Series(pd.to_datetime(local, unit="s")).dt.strftime("%Y-%m").to_numpy()
    idx_by_month: dict[str, np.ndarray] = {
        mk: np.nonzero(month == mk)[0] for mk in set(monthly_deployments)}
    eths = np.zeros(n_sims)
    for s in range(n_sims):
        rng = np.random.default_rng(deterministic_hash(master_seed, "random_timing", s))
        tot = 0.0
        for mk, nominal in monthly_deployments.items():
            idxs = idx_by_month.get(mk)
            if idxs is None or len(idxs) == 0 or nominal <= 0:
                continue
            i = int(rng.choice(idxs))
            e, _ = _fill(nominal, op[i], exec_cfg)
            tot += e
        eths[s] = tot
    return {"eth_distribution": eths, "p50": float(np.median(eths)),
            "p95": float(np.percentile(eths, 95))}


def random_anchor_control(dataset, monthly_deployments: dict, start, end,
                          n_sims=1000, master_seed=42, exec_cfg=None,
                          shift_days=10) -> dict:
    """Control G: giữ luật vốn, random hóa ngày tạo anchor trong phạm vi tháng.

    Lightweight replay: xấp xỉ bằng dịch chuyển ngẫu nhiên (±shift_days) thời điểm
    giải ngân của tháng, mô phỏng anchor đặt ở ngày khác trong tháng cho phép.
    """
    ts, op = _candles(dataset, start, end)
    local = ts + TZ_OFFSET
    month = pd.Series(pd.to_datetime(local, unit="s")).dt.strftime("%Y-%m").to_numpy()
    idx_by_month: dict[str, np.ndarray] = {
        mk: np.nonzero(month == mk)[0] for mk in set(monthly_deployments)}
    eths = np.zeros(n_sims)
    per_day = 96
    for s in range(n_sims):
        rng = np.random.default_rng(deterministic_hash(master_seed, "random_anchor", s))
        tot = 0.0
        for mk, nominal in monthly_deployments.items():
            idxs = idx_by_month.get(mk)
            if idxs is None or len(idxs) == 0 or nominal <= 0:
                continue
            shift = int(rng.integers(-shift_days, shift_days + 1)) * per_day
            i = int(np.clip(idxs[len(idxs) // 2] + shift, idxs[0], idxs[-1]))
            e, _ = _fill(nominal, op[i], exec_cfg)
            tot += e
        eths[s] = tot
    return {"eth_distribution": eths, "p50": float(np.median(eths)),
            "p95": float(np.percentile(eths, 95))}
