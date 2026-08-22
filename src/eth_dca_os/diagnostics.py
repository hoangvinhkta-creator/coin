"""Redundancy diagnostics — Strategy §2 (bắt buộc mọi official run, không feed ngược)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .score import ABLATION_WEIGHTS, factor_scores, sub_factors

SUBS = ["D", "M", "P", "R", "S7", "V", "W", "RP"]
GROUPS = {"price_location": ["D", "M", "P"], "market_stress": ["R", "S7", "V"]}


def correlation_matrices(sf: pd.DataFrame, fs: pd.DataFrame) -> dict:
    subs = sf[SUBS].dropna()
    factors = fs[["price_location_score", "market_stress_score", "relative_value_score"]].dropna()
    return {
        "pearson_sub": subs.corr(method="pearson"),
        "spearman_sub": subs.corr(method="spearman"),
        "pearson_factor": factors.corr(method="pearson"),
        "spearman_factor": factors.corr(method="spearman"),
    }


def high_redundancy_flags(corr: dict) -> dict:
    """HIGH_REDUNDANCY: |corr| > 0.85 giữa sub-factor cùng nhóm, hoặc PL~MS > 0.85."""
    flags = {}
    p = corr["pearson_sub"]
    for gname, cols in GROUPS.items():
        worst = 0.0
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                worst = max(worst, abs(float(p.loc[a, b])))
        flags[f"{gname}_max_abs_corr"] = worst
        flags[f"{gname}_high_redundancy"] = worst > 0.85
    pf = corr["pearson_factor"]
    flags["pl_ms_corr"] = float(pf.loc["price_location_score", "market_stress_score"])
    flags["pl_ms_high_redundancy"] = flags["pl_ms_corr"] > 0.85
    return flags


def vif(sf: pd.DataFrame) -> dict:
    """VIF từng biến trong nhóm; >5 WARNING, >10 SEVERE (FS-04)."""
    out = {}
    for gname, cols in GROUPS.items():
        sub = sf[cols].dropna()
        X = sub.to_numpy(float)
        for i, col in enumerate(cols):
            y = X[:, i]
            others = np.delete(X, i, axis=1)
            A = np.column_stack([np.ones(len(others)), others])
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            resid = y - A @ beta
            ss_res = float(resid @ resid)
            ss_tot = float(((y - y.mean()) ** 2).sum())
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            v = np.inf if r2 >= 1 else 1.0 / (1.0 - r2)
            out[f"{gname}.{col}"] = {
                "vif": float(v),
                "level": "SEVERE" if v > 10 else ("WARNING" if v > 5 else "OK"),
            }
    out["any_severe"] = any(d["level"] == "SEVERE" for d in out.values() if isinstance(d, dict))
    return out


def score_distribution(fs: pd.DataFrame) -> dict:
    """Phân bố OSCORE theo bucket 0-20/.../80-100 (FS-05: >70% trong hai bucket)."""
    s = fs["oscore"].dropna()
    buckets = pd.cut(s, [0, 20, 40, 60, 80, 100], include_lowest=True)
    share = buckets.value_counts(normalize=True).sort_index()
    top2 = float(share.nlargest(2).sum())
    return {
        "bucket_share": {str(k): float(v) for k, v in share.items()},
        "mean": float(s.mean()), "median": float(s.median()), "std": float(s.std()),
        "p10": float(s.quantile(0.10)), "p25": float(s.quantile(0.25)),
        "p75": float(s.quantile(0.75)), "p90": float(s.quantile(0.90)),
        "top2_bucket_share": top2,
        "bimodal_fs05": top2 > 0.70,
    }


def ablation_scores(ind: pd.DataFrame, score_weights=(50, 30, 20)) -> dict[str, pd.DataFrame]:
    """OSCORE theo ba model rút gọn đã đăng ký trước (Strategy §2.3)."""
    sf = sub_factors(ind)
    out = {
        "price_minimal": factor_scores(sf, score_weights, ABLATION_WEIGHTS["price_minimal"]),
        "stress_minimal": factor_scores(sf, score_weights, ABLATION_WEIGHTS["stress_minimal"]),
        "both_minimal": factor_scores(sf, score_weights,
                                      {**ABLATION_WEIGHTS["price_minimal"],
                                       **ABLATION_WEIGHTS["stress_minimal"]}),
    }
    return out


def volume_zscore_variant(ind: pd.DataFrame, sf: pd.DataFrame) -> pd.DataFrame:
    """Diagnostic §2.4: thay V bằng z-score volume 365d chuẩn hóa vào [0,1]."""
    sf2 = sf.copy()
    z = ind["volume_z365"]
    v_alt = np.clip(z / 3.0, 0, 1)
    sf2["V"] = np.where(ind["return7"] >= 0, 0.0, v_alt)
    sf2["V"] = np.where(ind["return7"].isna() | z.isna(), np.nan, sf2["V"])
    return sf2


def run_all(ind: pd.DataFrame, score_weights=(50, 30, 20)) -> dict:
    sf = sub_factors(ind)
    fs = factor_scores(sf, score_weights)
    corr = correlation_matrices(sf, fs)
    return {
        "correlation": {k: v.to_dict() for k, v in corr.items()},
        "redundancy_flags": high_redundancy_flags(corr),
        "vif": vif(sf),
        "score_distribution": score_distribution(fs),
    }
