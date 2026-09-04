"""Orchestration các phase backtest — Impl Plan §3. Cache daily score theo score-weight tuple."""
from __future__ import annotations

import hashlib
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
    deterministic_hash,
)
from .data.dataset import SOURCE_UNKNOWN, load_dataset, official_eligibility
from .diagnostics import run_all as run_diagnostics
from .engine import TZ_OFFSET, _epoch_seconds, run_engine
from .failure_signals import evaluate_failure_signals
from .gates import evaluate_gate1, evaluate_gate2, evaluate_gate3, evaluate_oos
from .indicators import compute_daily_indicators
from .manifests import (
    _cfg_row,
    generate_gate2_manifest,
    generate_gate3_manifest,
    manifest_hash,
)
from .metrics import (
    adjacent_config_flip,
    aggregate_over_windows,
    cash_ratio_stats,
    concentration,
    net_edge,
    oos_metrics,
    opportunity_cap_hit_share,
    regime_advantage_pooled,
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
        self.raw_dir = Path(raw_dir)
        self.dataset = load_dataset(raw_dir)
        self.lineage = self.dataset["lineage"]
        self.dataset_hash = self.lineage["dataset_hash"]
        self.data_source = self.lineage.get("source", SOURCE_UNKNOWN)
        # WP-A1/A1.2: cờ `official` của MỌI gate dẫn xuất từ đúng một chỗ này — lineage đã
        # verify checksum. Không gate nào được tự suy luận lại (F-005, CHECK-A1-07).
        self.official_eligible, self.official_reason = official_eligibility(
            self.raw_dir, self.lineage)
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


def _official_reason(prep: "Prepared", dev_limit: int | None) -> str:
    """Lý do đi kèm cờ `official`, theo contract case 13 (PRE-S008, FROZEN 2026-08-25).

    Hợp đồng: `dev_limit != None` -> `official = False`, `official_reason = 'dev_limit_set'`,
    enforcement point là `pipeline.run_gate1/2/3` (không phải `official_eligibility` — mã này
    thuộc TẦNG PIPELINE, dataset tự nó vẫn hợp lệ). Trước WP-A1 repair cycle cuối, cờ
    `official` đã đúng nhưng lý do vẫn là lý do của dataset, nên nguyên nhân `dev_limit` bị
    `'verified'` che hoàn toàn (`F-E2A1R3-03`, đóng theo `DEC-027`).

    Khi dataset TỰ NÓ đã không đủ tư cách, giữ lý do GỐC của dataset: hợp đồng chỉ định nghĩa
    case 13 trên nền ca (12) hợp lệ, và che một nguyên nhân sâu hơn bằng `dev_limit_set` sẽ
    lặp lại đúng khiếm khuyết đang được sửa, chỉ đổi chiều.
    """
    if dev_limit is not None and prep.official_eligible:
        return "dev_limit_set"
    return prep.official_reason


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
    # bootstrap trên window giữa (W5) làm đại diện chẩn đoán — bootstrap KHÔNG phải input
    # của Failure Signal nào nên giữ nguyên phạm vi (ngoài scope WP-A5).
    rep = wm["windows"]["W5"]
    boot = block_bootstrap_ae(rep["result"].purchases, rep["bench"]["purchases"],
                              n_sims=_bootstrap_sims(dev_limit), master_seed=MASTER_SEED)
    # WP-A5/A5.5 (đóng F-016): FS-03 (concentration) và FS-07 (cash ratio) TRƯỚC ĐÂY chỉ
    # tính trên W5 rồi được dùng như thể đại diện cho cả mẫu. Nay tính TỪNG window rồi gộp
    # bằng PrimaryMedian — đúng phép gộp chống thiên vị của BT §4.1 (CONVENTIONS #20).
    # Chín window đã được `window_metrics` chạy xong ở trên, nên việc mở rộng này KHÔNG
    # thêm một lần chạy engine nào.
    conc_by_w = {w: concentration(r) for w, r in wm["windows"].items()}
    cash_by_w = {w: cash_ratio_stats(r["result"]) for w, r in wm["windows"].items()}
    conc_m = aggregate_over_windows({w: d["ae_ex_month"] for w, d in conc_by_w.items()})
    conc_q = aggregate_over_windows({w: d["ae_ex_quarter"] for w, d in conc_by_w.items()})
    # Giữ NGUYÊN hai khoá `ae_ex_month`/`ae_ex_quarter` mà `failure_signals.py` đang đọc:
    # WP-A5 chỉ đổi PHẠM VI TÍNH của số, không đổi hợp đồng đọc số (chính sách = WP-B1).
    conc_detail = {"ae_ex_month": conc_m["value"], "ae_ex_quarter": conc_q["value"],
                   "scope": "9_windows_primary_median",
                   "per_window_ex_month": conc_m["per_window"],
                   "per_window_ex_quarter": conc_q["per_window"],
                   "reason": conc_m["reason"] or conc_q["reason"],
                   "w5_only_legacy": conc_by_w["W5"]}
    # Khoá `concentration` là HỢP ĐỒNG với `failure_signals.py`: `None` = UNKNOWN. Nhưng
    # chi tiết vì sao UNKNOWN phải sống sót trong run record, nếu không `CHECK-A5-04`
    # ("lý do phải được ghi rõ") sẽ không thoả — nên detail luôn được ghi ở khoá riêng.
    conc = None if conc_detail["reason"] else conc_detail
    cash_pw = {w: d["avg"] for w, d in cash_by_w.items()}
    cash_agg = aggregate_over_windows(cash_pw)
    cash = {"avg": cash_agg["value"], "scope": "9_windows_primary_median",
            "per_window_avg": cash_pw, "reason": cash_agg["reason"],
            "max": max((d["max"] for d in cash_by_w.values()
                        if d["max"] is not None and not np.isnan(d["max"])),
                       default=float("nan")),
            "w5_only_legacy": cash_by_w["W5"]}
    # WP-A5/A5.1 + A5.2 (đóng phần đo lường của F-002): hai đại lượng chưa từng được sinh.
    caphit_pw = {w: opportunity_cap_hit_share(r["result"])["share"]
                 for w, r in wm["windows"].items()}
    caphit = aggregate_over_windows(caphit_pw)
    regadv = regime_advantage_pooled(wm["windows"])
    payload = {
        "window_metrics": {k: v for k, v in wm.items() if k != "windows"},
        "gate1": g1, "oos": oos_eval,
        "diagnostics": diag, "bootstrap_descriptive": boot,
        "concentration": conc, "cash_ratio": cash,
        "opportunity_cap_hit": {
            "share": caphit["value"], "scope": "9_windows_primary_median",
            "per_window": caphit_pw, "reason": caphit["reason"]},
        "regime_advantage": {
            "share": regadv["share"], "scope": "9_windows_pooled_advantage",
            "by_regime_pooled": regadv["by_regime"],
            "top_regime": regadv.get("top_regime"),
            "positive_mass": regadv["positive_mass"],
            "net_advantage": regadv["net_advantage"],
            "per_window": regadv["per_window"],
            "per_window_share_primary_median":
                regadv["per_window_share_primary_median"],
            "reason": regadv["reason"]},
        "counters_w5": rep["result"].counters,
        "benchmarks": _benchmark_comparison(prep, exec_cfg, wm),
        "official": prep.official_eligible and dev_limit is None,
        "official_reason": _official_reason(prep, dev_limit),
        "lineage": prep.lineage,
        "dev_limit": dev_limit,
    }
    payload["window_metrics"]["ae_by_window"] = wm["ae_by_window"]
    # Backtest §4: bảng coverage weight bắt buộc trong MỌI báo cáo (WP-A2/F-012)
    payload["window_metrics"]["coverage_table"] = coverage_table()
    # WP-A1/A1.3: Gate 1 không chạy manifest sensitivity — hash tập chín window nó thực sự
    # dùng, để record vẫn tự chứng minh được phạm vi đo (Gate 2/3 hash manifest của chúng).
    mh = hashlib.sha256(json.dumps(
        {w.window_id: (str(w.start), str(w.end)) for w in gate_windows()},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    # WP-A1/A1.4: seed dẫn xuất từ master_seed + config hash để tái lập được (F-010)
    sim_seed = deterministic_hash(MASTER_SEED, cfg.hash, exec_cfg.hash)
    rec = save_run(out_dir, "GATE1", payload,
                   strategy_config_hash=cfg.hash, execution_config_hash=exec_cfg.hash,
                   dataset_hash=prep.dataset_hash, manifest_hash=mh,
                   start_date="2019-01-01",
                   end_date=str(prep.oos_end().date()),
                   simulation_seed=sim_seed,
                   data_source=prep.data_source,
                   official=payload["official"])
    payload["run_record"] = rec
    # giữ full-period run cho controls
    full = run_engine(prep.dataset, scores, cfg, exec_cfg,
                      pd.Timestamp("2019-01-01"), prep.oos_end())
    # F-017 (WP-B1/CHECK-B1-03, BT §12): Control F/G phải giữ đúng KÍCH THƯỚC TRANCHE và
    # PROFILE giải ngân theo tháng của V2 — không phải tổng nominal của tháng dồn vào một
    # lệnh. `full.purchases` đã có sẵn từng tranche thật (ts + nominal) do engine ghi; nhóm
    # lại theo tháng ở ĐÂY (không sửa engine.py — engine.py ngoài touch area của WP-B1) là
    # đủ để tái tạo đúng profile mà không cần chạy lại engine hay đổi Result.
    monthly_tranches: dict[str, list[float]] = {}
    for p in full.purchases:
        mk = pd.Timestamp(p["ts"] + TZ_OFFSET, unit="s").strftime("%Y-%m")
        monthly_tranches.setdefault(mk, []).append(p["nominal"])
    payload["_full_run_monthly_tranches"] = monthly_tranches
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
               "official": prep.official_eligible and limit is None,
               "official_reason": _official_reason(prep, limit),
               "expected_denominator": man["denominator"]}
    # WP-A1/A1.3: hash ĐÚNG manifest đã chạy (đã cắt nếu dev), dựng bằng cùng hàm với
    # `freeze_manifests` nên record đối chiếu được với manifest đóng băng (CHECK-A1-02).
    mh = manifest_hash([_cfg_row(c) for c in configs])
    save_run(out_dir, "GATE2", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE1_LOW_FRICTION.hash, dataset_hash=prep.dataset_hash,
             manifest_hash=mh, data_source=prep.data_source, official=payload["official"])
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
               "official": prep.official_eligible and limit is None,
               "official_reason": _official_reason(prep, limit), "dev_limit": limit,
               "expected_manifest_size": man["size"]}
    # WP-A1/A1.3: xem ghi chú ở `run_gate2` — cùng hàm hash với `freeze_manifests`.
    mh = manifest_hash([_cfg_row(c) for c in exec_cfgs])
    save_run(out_dir, "GATE3", payload, strategy_config_hash=cfg.hash,
             execution_config_hash=GATE3_REALISTIC.hash, dataset_hash=prep.dataset_hash,
             manifest_hash=mh, data_source=prep.data_source, official=payload["official"])
    return payload


def run_controls(prep: Prepared, out_dir, monthly_tranches: dict, v2_eth: float,
                 n_sims: int = 1000) -> dict:
    start, end = pd.Timestamp("2019-01-01"), prep.oos_end()
    f = random_timing_control(prep.dataset, monthly_tranches, start, end,
                              n_sims=n_sims, master_seed=MASTER_SEED)
    g = random_anchor_control(prep.dataset, monthly_tranches, start, end,
                              n_sims=n_sims, master_seed=MASTER_SEED)
    payload = {"random_timing": {k: v for k, v in f.items() if k != "eth_distribution"},
               "random_anchor": {k: v for k, v in g.items() if k != "eth_distribution"},
               "v2_eth": v2_eth,
               "v2_beats_p95_timing": v2_eth > f["p95"],
               "v2_beats_p95_anchor": v2_eth > g["p95"],
               "official": prep.official_eligible,
               "official_reason": prep.official_reason}
    save_run(out_dir, "RANDOM_CONTROL", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE1_LOW_FRICTION.hash, dataset_hash=prep.dataset_hash,
             data_source=prep.data_source, official=payload["official"])
    return payload


def run_verdict(g1: dict, g2: dict, g3: dict, controls: dict | None, out_dir,
                dataset_hash: str, data_source: str = SOURCE_UNKNOWN) -> dict:
    diag = g1["diagnostics"]
    # WP-A5/A5.3 + A5.4 (đóng phần đo lường của F-002): ba đại lượng dưới đây trước WP-A5
    # KHÔNG BAO GIỜ được truyền, nên FS-02/FS-06/FS-12 luôn UNKNOWN dù pipeline chạy đủ.
    # FS-06 dựng từ chính manifest Gate 2 đã chạy (config OFAT = config kề nhau), nên
    # không cần thêm lần chạy engine nào.
    flip = adjacent_config_flip(g2.get("per_config", []))
    fs = evaluate_failure_signals(
        gate1_windows=g1["window_metrics"]["ae_by_window"],
        concentration=g1["concentration"],
        opportunity_cap_hit_share=g1.get("opportunity_cap_hit", {}).get("share"),
        regime_advantage_share=g1.get("regime_advantage", {}).get("share"),
        adjacent_config_flip=flip["flip"],
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
    # E2-B1-F02 (WP-B1 fresh E2, 2026-09-04; bản sửa lần hai theo `E2-WP-B1-003` — canonical
    # interpretation A): trước đây `official` chỉ AND Gate 2/Gate 3, bỏ sót Gate 1 và
    # Controls — và dù đủ bốn thì cờ đó cũng CHỈ được dùng để thêm một dòng `warning` (text)
    # hoặc (bản sửa lần một) chỉ chặn `can_proceed_to_app` mà VẪN persist/print nhãn
    # `verdict="BUILD"`. Frozen Objective/CHECK-B1-01/07/09 đòi CẢ HAI: evidence non-official
    # không được cho ra verdict=BUILD LẪN can_proceed_to_app=true — chỉ ép một cờ phụ trong
    # khi nhãn chính vẫn nói "BUILD" là chưa đủ fail-closed. `can_proceed_to_app` chỉ có thể
    # `True` khi `v["verdict"] == "BUILD"` (hợp đồng `decide_verdict`), nên chỉ nhánh đó cần
    # hạ; `BUILD_WITH_MODIFICATIONS`/`INCONCLUSIVE`/`DO_NOT_BUILD` vốn đã `can_proceed_to_app
    # = False`, không cần chạm. Hạ về `INCONCLUSIVE` — tái dùng ĐÚNG một trong bốn verdict đã
    # có sẵn (không phát minh trạng thái thứ năm), đúng nghĩa "chưa đủ căn cứ để kết luận"
    # (cùng nghĩa với nhánh Gate 2/3 FAIL hiện có), không phải "chiến lược thất bại"
    # (`DO_NOT_BUILD` sẽ sai nghĩa đó). `decide_verdict()` không đổi cho evidence official.
    # Tái dùng NGUYÊN cờ `official` đã có sẵn ở từng thành phần (không phát minh lại
    # provenance/eligibility — mỗi cờ đã tự bao gồm điều kiện lineage đủ tư cách của nó).
    official = (g1.get("official", False) and g2.get("official", False)
                and g3.get("official", False)
                and bool(controls) and controls.get("official", False))
    if not official and v["verdict"] == "BUILD":
        v = {**v, "verdict": "INCONCLUSIVE", "can_proceed_to_app": False,
             "reasons": v["reasons"] + [
                 "Non-official/chưa đủ tư cách official: verdict hạ về INCONCLUSIVE, "
                 "can_proceed_to_app buộc về false"]}
    # WP-A5: PHẠM VI và LÝ DO của từng đại lượng đo, ghi thẳng vào run record. Mục đích là
    # để một FS còn UNKNOWN luôn nói được VÌ SAO nó UNKNOWN (CHECK-A5-04) — đây là siêu dữ
    # liệu ĐO LƯỜNG, không phải chính sách verdict (chính sách = WP-B1).
    fs_inputs = {
        "FS-02": {"quantity": "opportunity_cap_hit_share",
                  **{k: v for k, v in g1.get("opportunity_cap_hit", {}).items()
                     if k != "per_window"}},
        "FS-03": {"quantity": "concentration",
                  "scope": (g1.get("concentration") or {}).get("scope"),
                  "reason": (g1.get("concentration") or {}).get(
                      "reason", "concentration_unavailable")},
        "FS-06": {"quantity": "adjacent_config_flip",
                  **{k: v for k, v in flip.items() if k != "flipped_configs"}},
        "FS-07": {"quantity": "avg_cash_ratio",
                  "scope": g1["cash_ratio"].get("scope"),
                  "reason": g1["cash_ratio"].get("reason")},
        "FS-12": {"quantity": "regime_advantage_share",
                  **{k: v for k, v in g1.get("regime_advantage", {}).items()
                     if k not in ("per_window", "by_regime_w5")}},
    }
    payload = {"verdict": v, "failure_signals": fs,
               "failure_signal_inputs_wp_a5": fs_inputs, "official": official,
               "official_reason": g2.get("official_reason")}
    if not official:
        payload["warning"] = ("DEV RUN — Gate 1/Gate 2/Gate 3/Controls chạy với dev_limit hoặc "
                              "dữ liệu không đủ tư cách official. KHÔNG phải official verdict. "
                              "`can_proceed_to_app` đã bị buộc về false (E2-B1-F02). Chạy full "
                              "manifest trên dữ liệu Binance thật để có official verdict.")
    save_run(out_dir, "BASELINE", payload, strategy_config_hash=BASELINE_STRATEGY.hash,
             execution_config_hash=GATE3_REALISTIC.hash, dataset_hash=dataset_hash,
             verdict=v["verdict"], data_source=data_source, official=official)
    return payload
