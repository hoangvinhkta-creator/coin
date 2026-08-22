"""Gate metrics — Backtest §4.1, §7, §8, §10.2, §11, §16."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .benchmarks import run_benchmark_A
from .engine import run_engine
from .windows import (
    OOS_START,
    gate_windows,
    oos_months,
    pooled_median,
    primary_median,
    short_oos,
    anchor_set_medians,
)


def _ts(d) -> pd.Timestamp:
    return pd.Timestamp(d)


def run_window(dataset, scores, cfg, exec_cfg, start, end, contribution=100.0) -> dict:
    """Một window độc lập: engine V2 + benchmark A dưới cùng giả định ma sát."""
    res = run_engine(dataset, scores, cfg, exec_cfg, _ts(start), _ts(end), contribution)
    bench = run_benchmark_A(dataset, _ts(start), _ts(end), contribution, exec_cfg)
    ae = (res.eth_total / bench["eth"] * 100.0) if bench["eth"] > 0 else np.nan
    return {"eth_v2": res.eth_total, "eth_a": bench["eth"], "ae": ae,
            "result": res, "bench": bench}


def window_metrics(dataset, scores, cfg, exec_cfg, contribution=100.0) -> dict:
    """Chín window pre-OOS: AE từng window + AnchorSetMedian + PrimaryMedian + PooledMedian."""
    out = {}
    for w in gate_windows():
        end = pd.Timestamp(w.end) + pd.Timedelta(days=1)  # end inclusive -> exclusive
        r = run_window(dataset, scores, cfg, exec_cfg, w.start, end, contribution)
        out[w.window_id] = r
    aes = {k: v["ae"] for k, v in out.items()}
    return {
        "windows": out,
        "ae_by_window": aes,
        "anchor_set_medians": anchor_set_medians(aes),
        "primary_median": primary_median(aes),
        "pooled_median_descriptive": pooled_median(aes),
    }


def oos_metrics(dataset, scores, cfg, exec_cfg, oos_end, contribution=100.0) -> dict:
    end = pd.Timestamp(oos_end) + pd.Timedelta(days=1)
    r = run_window(dataset, scores, cfg, exec_cfg, pd.Timestamp(OOS_START), end, contribution)
    months = oos_months(pd.Timestamp(oos_end).date())
    return {"ae": r["ae"], "oos_months": months,
            "short_oos": short_oos(pd.Timestamp(oos_end).date()), "detail": r}


def net_edge(win_metrics: dict) -> dict:
    """NetEdgePct theo window = AE/100 - 1; PrimaryMedian NetEdge (Backtest §10.2)."""
    ne = {k: v / 100.0 - 1.0 for k, v in win_metrics["ae_by_window"].items()}
    return {"by_window": ne, "primary_median": primary_median(ne),
            "pooled_median_descriptive": pooled_median(ne)}


def implementation_shortfall_pp(gate1_primary_ae: float, gate3_primary_ae: float) -> float:
    return gate1_primary_ae - gate3_primary_ae


def shortfall_attribution(dataset, scores, cfg, gate1_cfg, gate3_cfg, contribution=100.0) -> dict:
    """Paired runs (Backtest §11): (a) chỉ user_delay; (b) chỉ funding; (c) chỉ slippage/fee."""
    from dataclasses import replace

    def pm(exec_cfg):
        return window_metrics(dataset, scores, cfg, exec_cfg, contribution)["primary_median"]

    base = pm(gate1_cfg)
    only_delay = replace(gate1_cfg, user_delay_seconds=gate3_cfg.user_delay_seconds,
                         config_name="attr_delay")
    only_funding = replace(gate1_cfg, funding_policy=gate3_cfg.funding_policy,
                           funding_delay_seconds=gate3_cfg.funding_delay_seconds,
                           config_name="attr_funding")
    only_friction = replace(gate1_cfg, spot_fee_rate=gate3_cfg.spot_fee_rate,
                            slippage_bps=gate3_cfg.slippage_bps, config_name="attr_friction")
    return {
        "gate1_primary_ae": base,
        "manual_delay_pp": base - pm(only_delay),
        "funding_pp": base - pm(only_funding),
        "fee_slippage_pp": base - pm(only_friction),
    }


def xirr(cashflows: list[tuple[float, float]], guess=0.1) -> float:
    """Money-weighted return từ [(epoch_seconds, amount)] (âm = nộp vốn, dương = giá trị cuối)."""
    if not cashflows:
        return np.nan
    t0 = cashflows[0][0]
    years = np.array([(t - t0) / (365.25 * 86400) for t, _ in cashflows])
    amounts = np.array([a for _, a in cashflows])
    rate = guess
    for _ in range(100):
        d = (1 + rate) ** years
        f = float((amounts / d).sum())
        fprime = float((-years * amounts / d / (1 + rate)).sum())
        if abs(fprime) < 1e-12:
            break
        step = f / fprime
        rate -= step
        if abs(step) < 1e-10:
            break
    return rate


def cash_ratio_stats(result) -> dict:
    """Average và max cash ratio từ cash_samples của engine (Backtest §16)."""
    if not result.cash_samples:
        return {"avg": np.nan, "max": np.nan}
    ratios = []
    for ts, cash, eth, price in result.cash_samples:
        port = cash + eth * price
        if port > 0:
            ratios.append(cash / port)
    return {"avg": float(np.mean(ratios)), "max": float(np.max(ratios))}


def concentration(win_result: dict) -> dict:
    """AE sau khi loại tháng/quý có lợi thế ETH tăng thêm lớn nhất (FS-03)."""
    res = win_result["result"]
    bench = win_result["bench"]
    v2_m: dict[str, float] = {}
    for p in res.purchases:
        mk = pd.Timestamp(p["ts"] + 7 * 3600, unit="s").strftime("%Y-%m")
        v2_m[mk] = v2_m.get(mk, 0.0) + p["eth"]
    a_m: dict[str, float] = {}
    for p in bench["purchases"]:
        a_m[p["month"]] = a_m.get(p["month"], 0.0) + p["eth"]
    months = sorted(set(v2_m) | set(a_m))
    adv = {m: v2_m.get(m, 0.0) - a_m.get(m, 0.0) for m in months}
    if not adv:
        return {"ae_ex_month": np.nan, "ae_ex_quarter": np.nan}
    m_star = max(adv, key=adv.get)
    q_of = lambda m: f"{m[:4]}-Q{(int(m[5:7]) - 1) // 3 + 1}"
    q_adv: dict[str, float] = {}
    for m, a in adv.items():
        q_adv[q_of(m)] = q_adv.get(q_of(m), 0.0) + a
    q_star = max(q_adv, key=q_adv.get)
    e_v2, e_a = win_result["eth_v2"], win_result["eth_a"]
    ex_m_v2 = e_v2 - v2_m.get(m_star, 0.0)
    ex_m_a = e_a - a_m.get(m_star, 0.0)
    q_months = [m for m in months if q_of(m) == q_star]
    ex_q_v2 = e_v2 - sum(v2_m.get(m, 0.0) for m in q_months)
    ex_q_a = e_a - sum(a_m.get(m, 0.0) for m in q_months)
    return {
        "best_month": m_star, "best_quarter": q_star,
        "ae_ex_month": ex_m_v2 / ex_m_a * 100.0 if ex_m_a > 0 else np.nan,
        "ae_ex_quarter": ex_q_v2 / ex_q_a * 100.0 if ex_q_a > 0 else np.nan,
    }
