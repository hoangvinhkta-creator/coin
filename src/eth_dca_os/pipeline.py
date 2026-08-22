"""Orchestration các phase backtest — Impl Plan §3. Cache daily score theo score-weight tuple."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import MASTER_SEED
from .benchmarks import random_anchor_control, random_timing_control, run_benchmark_A
from .bootstrap import block_bootstrap_ae
from .config import (
    BASELINE_STRATEGY,
    GATE1_LOW_FRICTION,
    GATE3_REALISTIC,
    ExecutionConfig,
    StrategyConfig,
)
from .data.dataset import load_dataset
from .diagnostics import run_all as run_diagnostics
from .engine import run_engine
from .failure_signals import evaluate_failure_signals
from .gates import evaluate_gate1, evaluate_gate2, evaluate_gate3, evaluate_oos
from .indicators import compute_daily_indicators
from .manifests import generate_gate2_manifest, generate_gate3_manifest
from .metrics import (
    cash_ratio_stats,
    concentration,
    net_edge,
    oos_metrics,
    shortfall_attribution,
    window_metrics,
)
from .reporting import save_run
from .score import compute_scores
from .verdict import decide_verdict
from .windows import OOS_START


class Prepared:
    """Dataset + indicator + cache scores theo từng score-weight tuple (Impl Plan §4)."""

    def __init__(self, raw_dir: str | Path):
        self.dataset = load_dataset(raw_dir)
        self.dataset_hash = self.dataset["lineage"]["dataset_hash"]
        self.indicators = compute_daily_indicators(
            self.dataset["ETHUSDT_1d"], self.dataset["BTCUSDT_1d"])
        self._score_cache: dict[tuple, pd.DataFrame] = {}

    def scores(self, weights=(50, 30, 20)) -> pd.DataFrame:
        key = tuple(weights)
        if key not in self._score_cache:
            sc = compute_scores(self.indicators, key)
            merged = pd.concat([self.indicators, sc], axis=1)
            self._score_cache[key] = merged.loc[:, ~merged.columns.duplicated()]
        return self._score_cache[key]

    def oos_end(self) -> pd.Timestamp:
        last = self.dataset["ETHUSDT_1d"]["open_time"].max()
        return pd.Timestamp(last).tz_localize(None).normalize()


def run_gate1(prep: Prepared, out_dir, cfg: StrategyConfig = BASELINE_STRATEGY,
              exec_cfg: ExecutionConfig = GATE1_LOW_FRICTION) -> dict:
    scores = prep.scores(cfg.score_weights)
    wm = window_metrics(prep.dataset, scores, cfg, exec_cfg)
    g1 = evaluate_gate1(wm)
    oos = oos_metrics(prep.dataset, scores, cfg, exec_cfg, prep.oos_end())
    oos_eval = evaluate_oos(oos)
    diag = run_diagnostics(prep.indicators, cfg.score_weights)
    # bootstrap + concentration + cash trên window giữa (W5) làm đại diện chẩn đoán
    rep = wm["windows"]["W5"]
    boot = block_bootstrap_ae(rep["result"].purchases, rep["bench"]["purchases"],
                              n_sims=200, master_seed=MASTER_SEED)
    conc = concentration(rep)
    cash = cash_ratio_stats(rep["result"])
    payload = {
        "window_metrics": {k: v for k, v in wm.items() if k != "windows"},
        "gate1": g1, "oos": oos_eval,
        "diagnostics": diag, "bootstrap_descriptive": boot,
        "concentration": conc, "cash_ratio": cash,
        "counters_w5": rep["result"].counters,
    }
    payload["window_metrics"]["ae_by_window"] = wm["ae_by_window"]
    rec = save_run(out_dir, "GATE1", payload,
                   strategy_config_hash=cfg.hash, execution_config_hash=exec_cfg.hash,
                   dataset_hash=prep.dataset_hash, start_date="2019-01-01",
                   end_date=str(prep.oos_end().date()))
    payload["run_record"] = rec
    # giữ full-period run cho controls
    full = run_engine(prep.dataset, scores, cfg, exec_cfg,
                      pd.Timestamp("2019-01-01"), prep.oos_end())
    payload["_full_run_monthly_deployments"] = full.monthly_deployments
    payload["_full_run_eth"] = full.eth_total
    return payload


def run_gate2(prep: Prepared, out_dir, limit: int | None = None) -> dict:
    """Chạy manifest Gate 2 (219 config). `limit` CHỈ dùng dev/smoke — official = full."""
    man = generate_gate2_manifest()
    configs = [man["baseline"]] + man["ofat"] + man["interaction"]
    if limit:
        configs = configs[:limit]
    results = []
    for cfg in configs:
        scores = prep.scores(cfg.score_weights)
        wm = window_metrics(prep.dataset, scores, cfg, GATE1_LOW_FRICTION)
        g1 = evaluate_gate1(wm)
        oos = oos_metrics(prep.dataset, scores, cfg, GATE1_LOW_FRICTION, prep.oos_end())
        results.append({"config_name": cfg.config_name, "hash": cfg.hash,
                        "gate1": g1, "oos_ae": oos["ae"],
                        "primary_median": wm["primary_median"]})
    g2 = evaluate_gate2(results)
    g2["dev_limit"] = limit
    payload = {"gate2": g2, "per_config": results,
               "official": limit is None,
               "expected_denominator": man["denominator"]}
    save_run(out_dir, "GATE2", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE1_LOW_FRICTION.hash, dataset_hash=prep.dataset_hash)
    return payload


def run_gate3(prep: Prepared, out_dir, limit: int | None = None) -> dict:
    """Manifest ma sát 114 config + realistic baseline + shortfall attribution."""
    man = generate_gate3_manifest()
    exec_cfgs = man["manifest"]
    if limit:
        exec_cfgs = exec_cfgs[:limit]
    cfg = BASELINE_STRATEGY
    scores = prep.scores(cfg.score_weights)
    per = []
    realistic_payload = None
    for ec in exec_cfgs:
        wm = window_metrics(prep.dataset, scores, cfg, ec)
        ne = net_edge(wm)
        row = {"config_name": ec.config_name, "hash": ec.hash,
               "net_edge_primary_median": ne["primary_median"]}
        per.append(row)
        if ec.config_name == "gate3_realistic":
            oos = oos_metrics(prep.dataset, scores, cfg, ec, prep.oos_end())
            realistic_payload = {"window_metrics_pm": wm["primary_median"],
                                 "net_edge": ne, "oos": oos}
    if realistic_payload is None:  # limit cắt mất realistic -> chạy riêng
        ec = GATE3_REALISTIC
        wm = window_metrics(prep.dataset, scores, cfg, ec)
        ne = net_edge(wm)
        oos = oos_metrics(prep.dataset, scores, cfg, ec, prep.oos_end())
        realistic_payload = {"window_metrics_pm": wm["primary_median"],
                             "net_edge": ne, "oos": oos}
    positive_share = sum(1 for r in per if r["net_edge_primary_median"] > 0) / len(per)
    g3 = evaluate_gate3(realistic_payload["net_edge"]["primary_median"],
                        realistic_payload["oos"]["ae"], positive_share)
    attr = shortfall_attribution(prep.dataset, scores, cfg, GATE1_LOW_FRICTION, GATE3_REALISTIC)
    payload = {"gate3": g3, "per_config": per, "realistic": {
                   "primary_median_ae": realistic_payload["window_metrics_pm"],
                   "net_edge_primary_median": realistic_payload["net_edge"]["primary_median"],
                   "oos_ae": realistic_payload["oos"]["ae"]},
               "shortfall_attribution": attr,
               "official": limit is None, "dev_limit": limit,
               "expected_manifest_size": man["size"]}
    save_run(out_dir, "GATE3", payload, strategy_config_hash=cfg.hash,
             execution_config_hash=GATE3_REALISTIC.hash, dataset_hash=prep.dataset_hash)
    return payload


def run_controls(prep: Prepared, out_dir, monthly_deployments: dict, v2_eth: float,
                 n_sims: int = 1000) -> dict:
    start, end = pd.Timestamp("2019-01-01"), prep.oos_end()
    f = random_timing_control(prep.dataset, monthly_deployments, start, end,
                              n_sims=n_sims, master_seed=MASTER_SEED)
    g = random_anchor_control(prep.dataset, monthly_deployments, start, end,
                              n_sims=n_sims, master_seed=MASTER_SEED)
    payload = {"random_timing": {k: v for k, v in f.items() if k != "eth_distribution"},
               "random_anchor": {k: v for k, v in g.items() if k != "eth_distribution"},
               "v2_eth": v2_eth,
               "v2_beats_p95_timing": v2_eth > f["p95"],
               "v2_beats_p95_anchor": v2_eth > g["p95"]}
    save_run(out_dir, "RANDOM_CONTROL", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE1_LOW_FRICTION.hash, dataset_hash=prep.dataset_hash)
    return payload


def run_verdict(g1: dict, g2: dict, g3: dict, controls: dict | None, out_dir,
                dataset_hash: str) -> dict:
    diag = g1["diagnostics"]
    fs = evaluate_failure_signals(
        gate1_windows=g1["window_metrics"]["ae_by_window"],
        concentration=g1["concentration"],
        vif_any_severe=diag["vif"]["any_severe"],
        corr_high_redundancy=any(v for k, v in diag["redundancy_flags"].items()
                                 if k.endswith("high_redundancy")),
        score_bimodal=diag["score_distribution"]["bimodal_fs05"],
        avg_cash_ratio=g1["cash_ratio"]["avg"],
        gate1_primary_ae=g1["window_metrics"]["primary_median"],
        v2_eth=controls.get("v2_eth") if controls else None,
        random_timing_p95=controls["random_timing"]["p95"] if controls else None,
        random_anchor_p95=controls["random_anchor"]["p95"] if controls else None,
        shortfall_pp=g1["window_metrics"]["primary_median"]
        - g3["realistic"]["primary_median_ae"],
        gate2_oos_pass_share=g2["gate2"]["oos_pass_share_reported_separately"],
        oos_ae=g1["oos"]["ae"],
    )
    v = decide_verdict(g1["gate1"], g1["oos"], g2["gate2"], g3["gate3"], fs)
    official = g2.get("official", False) and g3.get("official", False)
    payload = {"verdict": v, "failure_signals": fs, "official": official}
    if not official:
        payload["warning"] = ("DEV RUN — Gate 2/Gate 3 chạy với dev_limit, "
                              "KHÔNG phải official verdict. Chạy full manifest trên dữ liệu "
                              "Binance thật để có official verdict.")
    save_run(out_dir, "BASELINE", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE3_REALISTIC.hash, dataset_hash=dataset_hash,
             verdict=v["verdict"])
    return payload
