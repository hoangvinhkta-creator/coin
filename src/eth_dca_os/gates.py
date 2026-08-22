"""Ngưỡng cứng Gate 1 / OOS / Gate 2 / Gate 3 — Backtest §7, §8, §9.2, §10.2."""
from __future__ import annotations

import numpy as np

from .windows import gate_windows


def evaluate_gate1(win_metrics: dict) -> dict:
    aes = win_metrics["ae_by_window"]
    pm = win_metrics["primary_median"]
    share_100 = sum(1 for v in aes.values() if v >= 100.0) / len(aes)
    worst_delta = min(v - 100.0 for v in aes.values())
    # Không anchor set nào có TOÀN BỘ window dưới 100%
    wins = gate_windows()
    anchor_ok = True
    for off in (0, 6, 12, 18):
        vals = [aes[w.window_id] for w in wins if w.anchor_offset == off]
        if all(v < 100.0 for v in vals):
            anchor_ok = False
    checks = {
        "primary_median": {"value": pm, "pass": pm >= 102.0, "strong": pm >= 105.0},
        "share_windows_ge_100": {"value": share_100, "pass": share_100 >= 6 / 9 - 1e-9,
                                 "strong": share_100 >= 7 / 9 - 1e-9},
        "worst_window_delta_pp": {"value": worst_delta, "pass": worst_delta >= -5.0,
                                  "strong": worst_delta >= -3.0},
        "no_anchor_set_all_below_100": {"value": anchor_ok, "pass": anchor_ok,
                                        "strong": anchor_ok},
    }
    return {
        "checks": checks,
        "pass": all(c["pass"] for c in checks.values()),
        "strong": all(c["strong"] for c in checks.values()),
    }


def evaluate_oos(oos: dict) -> dict:
    ae = oos["ae"]
    return {"ae": ae, "oos_months": oos["oos_months"], "short_oos": oos["short_oos"],
            "pass": ae >= 100.0, "strong": ae >= 102.0}


def evaluate_gate2(config_results: list[dict]) -> dict:
    """config_results: mỗi phần tử {'config_name', 'gate1': evaluate_gate1(...), 'oos_ae': float}.

    Ngưỡng cứng CHỈ pre-OOS; OOS pass share báo cáo riêng (FS-10 nếu < 50%).
    """
    n = len(config_results)
    pre = sum(1 for r in config_results if r["gate1"]["pass"]) / n
    oos_share = sum(1 for r in config_results if r["oos_ae"] >= 100.0) / n
    combined = sum(1 for r in config_results
                   if r["gate1"]["pass"] and r["oos_ae"] >= 100.0) / n
    return {
        "denominator": n,
        "pre_oos_pass_share": pre,
        "oos_pass_share_reported_separately": oos_share,
        "combined_pass_share_reference": combined,
        "pass": pre >= 0.75,
        "strong": pre >= 0.80,
        "fs10_triggered": oos_share < 0.50,
    }


def evaluate_gate3(realistic_net_edge_pm: float, realistic_oos_ae: float,
                   manifest_positive_share: float) -> dict:
    checks = {
        "realistic_primary_median_net_edge": {
            "value": realistic_net_edge_pm,
            "pass": realistic_net_edge_pm > 0.0,
            "strong": realistic_net_edge_pm >= 0.015,
        },
        "realistic_oos_ae": {
            "value": realistic_oos_ae,
            "pass": realistic_oos_ae >= 100.0,
            "strong": realistic_oos_ae >= 102.0,
        },
        "manifest_positive_net_edge_share": {
            "value": manifest_positive_share,
            "pass": manifest_positive_share >= 0.60,
            "strong": manifest_positive_share >= 0.70,
        },
    }
    return {"checks": checks,
            "pass": all(c["pass"] for c in checks.values()),
            "strong": all(c["strong"] for c in checks.values())}
