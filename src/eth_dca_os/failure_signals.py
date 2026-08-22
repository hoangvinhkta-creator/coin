"""Failure Signals FS-01..FS-12 và verdict cap — Backtest §17, Impl Plan §6.

Mỗi signal đánh giá từ artifact đã tính; thiếu input -> None (UNKNOWN), không đoán.
"""
from __future__ import annotations

FS_DESCRIPTIONS = {
    "FS-01": "V2 tích lũy ít ETH hơn Monthly DCA ở phần lớn gate window",
    "FS-02": "Opportunity reserve thường xuyên chạm cap và nằm im",
    "FS-03": "Lợi thế biến mất sau khi loại một tháng hoặc một quý lớn nhất",
    "FS-04": "Redundancy nghiêm trọng: VIF > 10 hoặc corr > 0.85",
    "FS-05": "Score lưỡng cực: >70% quan sát trong hai bucket",
    "FS-06": "Config kề nhau đảo ngược kết luận",
    "FS-07": "Cash ratio cao nhưng không có accumulation benefit",
    "FS-08": "Random control bao trùm/vượt V2 (không vượt P95)",
    "FS-09": "ImplementationShortfallPP > 3.0 pp",
    "FS-10": "Gate2_OOS_PassShare < 50%",
    "FS-11": "OOS AccumulationEfficiency < 100%",
    "FS-12": "Lợi thế tập trung vào một crash/regime duy nhất",
}


def evaluate_failure_signals(*, gate1_windows: dict | None = None,
                             opportunity_cap_hit_share: float | None = None,
                             concentration: dict | None = None,
                             vif_any_severe: bool | None = None,
                             corr_high_redundancy: bool | None = None,
                             score_bimodal: bool | None = None,
                             adjacent_config_flip: bool | None = None,
                             avg_cash_ratio: float | None = None,
                             gate1_primary_ae: float | None = None,
                             v2_eth: float | None = None,
                             random_timing_p95: float | None = None,
                             random_anchor_p95: float | None = None,
                             shortfall_pp: float | None = None,
                             gate2_oos_pass_share: float | None = None,
                             oos_ae: float | None = None,
                             regime_advantage_share: float | None = None) -> dict:
    fs: dict[str, bool | None] = {}

    if gate1_windows is not None:
        below = sum(1 for v in gate1_windows.values() if v < 100.0)
        fs["FS-01"] = below > len(gate1_windows) / 2
    else:
        fs["FS-01"] = None

    fs["FS-02"] = (opportunity_cap_hit_share > 0.5) if opportunity_cap_hit_share is not None else None

    if concentration is not None:
        fs["FS-03"] = (concentration.get("ae_ex_month", 100.0) < 100.0
                       or concentration.get("ae_ex_quarter", 100.0) < 100.0)
    else:
        fs["FS-03"] = None

    if vif_any_severe is not None or corr_high_redundancy is not None:
        fs["FS-04"] = bool(vif_any_severe) or bool(corr_high_redundancy)
    else:
        fs["FS-04"] = None

    fs["FS-05"] = score_bimodal
    fs["FS-06"] = adjacent_config_flip

    if avg_cash_ratio is not None and gate1_primary_ae is not None:
        fs["FS-07"] = avg_cash_ratio > 0.30 and gate1_primary_ae < 102.0
    else:
        fs["FS-07"] = None

    if v2_eth is not None and (random_timing_p95 is not None or random_anchor_p95 is not None):
        beats_f = (random_timing_p95 is None) or (v2_eth > random_timing_p95)
        beats_g = (random_anchor_p95 is None) or (v2_eth > random_anchor_p95)
        fs["FS-08"] = not (beats_f and beats_g)
    else:
        fs["FS-08"] = None

    fs["FS-09"] = (shortfall_pp > 3.0) if shortfall_pp is not None else None
    fs["FS-10"] = (gate2_oos_pass_share < 0.50) if gate2_oos_pass_share is not None else None
    fs["FS-11"] = (oos_ae < 100.0) if oos_ae is not None else None
    fs["FS-12"] = (regime_advantage_share > 0.80) if regime_advantage_share is not None else None

    any_true = any(v is True for v in fs.values())
    return {"signals": fs, "any_true": any_true,
            "unknown": [k for k, v in fs.items() if v is None]}
