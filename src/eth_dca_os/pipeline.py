"""Orchestration các phase backtest — Impl Plan §3. Cache daily score theo score-weight tuple."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import MASTER_SEED
from .benchmarks import (
    random_anchor_control,
    random_timing_control,
    run_benchmark_A,
    run_benchmark_B,
    run_benchmark_C,
    run_benchmark_D,
)
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
from .engine import _epoch_seconds, run_engine
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
    xirr,
)
from .reporting import save_run
from .score import compute_scores
from .verdict import decide_verdict
from .windows import OOS_START, coverage_table, gate_windows, primary_median


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


def _bootstrap_sims(dev_limit: int | None) -> int:
    """Backtest §13: official run = 1000 mô phỏng MỖI block length; chỉ dev/smoke mới hạ 200.

    Cùng quy ước dev/official với `run_gate2`/`run_gate3`/`run_controls`: `dev_limit=None`
    nghĩa là official (WP-A2/F-014 — trước đây pipeline ghi đè cứng xuống 200).
    """
    return 200 if dev_limit else 1000


def _benchmark_comparison(prep: Prepared, exec_cfg: ExecutionConfig, wm: dict,
                          contribution: float = 100.0) -> dict:
    """AE của chiến lược so với TỪNG benchmark A–D trên đúng chín window pre-OOS.

    Backtest §22 chỉ có nghĩa khi chiến lược được đối chiếu với cả ba benchmark đơn giản
    hơn, không riêng A (WP-A2/F-003). Mọi benchmark nhận CÙNG (start, end, contribution,
    exec_cfg) với engine — điều kiện equal capital rule §12.1 (CHECK-A2-07).
    Không sửa công thức benchmark nào; đây thuần tuý là lời gọi + tổng hợp.
    """
    runners = {
        "A": lambda s, e: run_benchmark_A(prep.dataset, s, e, contribution, exec_cfg),
        "B": lambda s, e: run_benchmark_B(prep.dataset, s, e, contribution, exec_cfg),
        "C": lambda s, e: run_benchmark_C(prep.dataset, prep.indicators, s, e,
                                          contribution, exec_cfg),
        "D": lambda s, e: run_benchmark_D(prep.dataset, prep.indicators, s, e,
                                          contribution, exec_cfg),
    }
    out = {name: {"ae_by_window": {}, "eth_by_window": {}, "contributed_by_window": {}}
           for name in runners}
    for w in gate_windows():
        start = pd.Timestamp(w.start)
        end = pd.Timestamp(w.end) + pd.Timedelta(days=1)   # end inclusive -> exclusive
        eth_v2 = wm["windows"][w.window_id]["eth_v2"]
        for name, run in runners.items():
            r = run(start, end)
            ae = (eth_v2 / r["eth"] * 100.0) if r["eth"] > 0 else np.nan
            out[name]["ae_by_window"][w.window_id] = ae
            out[name]["eth_by_window"][w.window_id] = r["eth"]
            out[name]["contributed_by_window"][w.window_id] = r["contributed"]
    for name in out:
        out[name]["primary_median_ae"] = primary_median(out[name]["ae_by_window"])
    return out


def _xirr_payload(dataset, full_run) -> dict:
    """XIRR / money-weighted return của chiến lược (Backtest §16, WP-A2/F-013).

    Dòng tiền = mỗi contribution ngoài (âm) + giá trị ETH cuối kỳ theo giá đóng cửa
    cuối dataset (dương). Dùng `metrics.xirr` sẵn có, không sửa công thức.
    """
    d1 = dataset["ETHUSDT_1d"]
    final_price = float(d1["close"].to_numpy(float)[-1])
    flows = [(float(ts), -float(amt)) for ts, amt in full_run.contributions]
    if not flows:
        return {"xirr": float("nan"), "n_cashflows": 0,
                "final_eth": full_run.eth_total, "final_price": final_price}
    end_ts = float(_epoch_seconds(d1["open_time"])[-1])
    final_value = full_run.eth_total * final_price
    flows.append((end_ts, final_value))
    return {"xirr": float(xirr(flows)), "n_cashflows": len(flows),
            "final_eth": float(full_run.eth_total), "final_price": final_price,
            "total_contributed": float(sum(-a for _, a in flows[:-1])),
            "final_value_usdt": float(final_value)}


def run_gate1(prep: Prepared, out_dir, cfg: StrategyConfig = BASELINE_STRATEGY,
              exec_cfg: ExecutionConfig = GATE1_LOW_FRICTION,
              dev_limit: int | None = None) -> dict:
    """`dev_limit` CHỈ dùng dev/smoke (giảm số mô phỏng bootstrap); official = None."""
    scores = prep.scores(cfg.score_weights)
    wm = window_metrics(prep.dataset, scores, cfg, exec_cfg)
    g1 = evaluate_gate1(wm)
    oos = oos_metrics(prep.dataset, scores, cfg, exec_cfg, prep.oos_end())
    oos_eval = evaluate_oos(oos)
    diag = run_diagnostics(prep.indicators, cfg.score_weights)
    # bootstrap + concentration + cash trên window giữa (W5) làm đại diện chẩn đoán
    rep = wm["windows"]["W5"]
    boot = block_bootstrap_ae(rep["result"].purchases, rep["bench"]["purchases"],
                              n_sims=_bootstrap_sims(dev_limit), master_seed=MASTER_SEED)
    conc = concentration(rep)
    cash = cash_ratio_stats(rep["result"])
    payload = {
        "window_metrics": {k: v for k, v in wm.items() if k != "windows"},
        "gate1": g1, "oos": oos_eval,
        "diagnostics": diag, "bootstrap_descriptive": boot,
        "concentration": conc, "cash_ratio": cash,
        "counters_w5": rep["result"].counters,
        "benchmarks": _benchmark_comparison(prep, exec_cfg, wm),
        "official": dev_limit is None,
        "dev_limit": dev_limit,
    }
    payload["window_metrics"]["ae_by_window"] = wm["ae_by_window"]
    # Backtest §4: bảng coverage weight bắt buộc trong MỌI báo cáo (WP-A2/F-012)
    payload["window_metrics"]["coverage_table"] = coverage_table()
    # WP-A1: truyền manifest_hash và simulation_seed cho provenance (A1.3–A1.4)
    # manifest_hash tính từ gate_windows (simplified, xem manifests.py cho gate2/3)
    import hashlib
    mh = hashlib.sha256(json.dumps(
        {w.window_id: (str(w.start), str(w.end)) for w in gate_windows()},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    # simulation_seed: lấy từ master_seed kèm config hash để deterministic
    from .config import deterministic_hash
    sim_seed = deterministic_hash(MASTER_SEED, cfg.hash, exec_cfg.hash)
    rec = save_run(out_dir, "GATE1", payload,
                   strategy_config_hash=cfg.hash, execution_config_hash=exec_cfg.hash,
                   dataset_hash=prep.dataset_hash, manifest_hash=mh,
                   start_date="2019-01-01",
                   end_date=str(prep.oos_end().date()),
                   simulation_seed=sim_seed)
    payload["run_record"] = rec
    # giữ full-period run cho controls
    full = run_engine(prep.dataset, scores, cfg, exec_cfg,
                      pd.Timestamp("2019-01-01"), prep.oos_end())
    payload["_full_run_monthly_deployments"] = full.monthly_deployments
    payload["_full_run_eth"] = full.eth_total
    # Backtest §16: XIRR / money-weighted return (WP-A2/F-013)
    payload["xirr"] = _xirr_payload(prep.dataset, full)
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
