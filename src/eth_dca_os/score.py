"""Opportunity Score — Strategy §1, §3, §4; ScoreMultiplier §11; Opportunity ladder weights §13."""
from __future__ import annotations

import numpy as np
import pandas as pd


def clamp(x, lo=0.0, hi=1.0):
    return np.minimum(np.maximum(x, lo), hi)


# ------------------------------------------------------------- sub-factors

def sub_factors(ind: pd.DataFrame) -> pd.DataFrame:
    """Tám sub-factor D, M, P, R, S7, V, W, RP (NaN nếu input thiếu)."""
    out = pd.DataFrame(index=ind.index)
    out["D"] = clamp((-ind["dd365"] - 0.05) / 0.55)
    out["M"] = clamp((1.05 - ind["ma_ratio"]) / 0.40)
    out["P"] = clamp((0.90 - ind["percentile365"]) / 0.80)
    out["R"] = clamp((55 - ind["rsi14"]) / 30)
    out["S7"] = clamp((-ind["return7"] - 0.02) / 0.18)
    v = clamp((ind["volume_ratio"] - 1) / 1.5)
    out["V"] = np.where(ind["return7"] >= 0, 0.0, v)
    out["V"] = np.where(ind["return7"].isna() | ind["volume_ratio"].isna(), np.nan, out["V"])
    out["W"] = clamp((-ind["ethbtc_return30"] - 0.02) / 0.18)
    out["RP"] = clamp((0.70 - ind["ethbtc_percentile180"]) / 0.60)
    return out


#: Indicator daily **BẮT BUỘC** — Strategy §3 nói INVALID khi "giá/lịch sử ETH hoặc
#: indicator bắt buộc không hợp lệ" nhưng KHÔNG liệt kê tập đó. Spec để ngỏ, nên quy ước
#: được chốt ở đây và ghi ở `docs/CONVENTIONS.md` (WP-A4/A4.1).
#:
#: Tiêu chí chọn: một indicator là BẮT BUỘC khi engine không thể hình thành một quyết định
#: Smart/Opportunity có căn cứ nếu thiếu nó — tức nó được đọc trên ĐƯỜNG HÀNH ĐỘNG, chứ
#: không chỉ là một sub-component của score (sub-component thiếu là DEGRADED, §3 nói rõ).
#:
#:   close    — giá/lịch sử ETH; thiếu giá thì không có gì hợp lệ để làm
#:   adr30    — engine đòi nó để dựng bất kỳ ladder nào (spacing); thiếu thì không có ladder
#:   return7  — vừa là sub-component S7, vừa là input phát hiện regime CRASH/STRESSED;
#:              thiếu nó engine không phân biệt được CRASH với NORMAL, mà chính sách hành
#:              động lại phụ thuộc vào phân biệt đó
#:
#: `btc_close` KHÔNG bắt buộc: thiếu BTC chỉ làm hai sub-component W/RP thiếu -> DEGRADED,
#: đúng như §3 mô tả ("giá/lịch sử **ETH**").
REQUIRED_DAILY_INDICATORS = ("close", "return7", "adr30")


def invalid_mask(ind: pd.DataFrame) -> np.ndarray:
    """Ngày nào INVALID theo Strategy §3 vì giá/lịch sử ETH hoặc indicator bắt buộc hỏng.

    Fail-closed: cột bắt buộc không tồn tại trong `ind` thì MỌI ngày là INVALID — một
    khung dữ liệu không mang nổi indicator bắt buộc thì không chứng minh được ngày nào
    hợp lệ, và "không chứng minh được" phải đọc thành không hợp lệ, không phải thành GOOD.
    """
    bad = np.zeros(len(ind), dtype=bool)
    for col in REQUIRED_DAILY_INDICATORS:
        if col not in ind.columns:
            return np.ones(len(ind), dtype=bool)
        vals = ind[col].to_numpy(float)
        bad |= ~np.isfinite(vals)
        if col == "close":
            # Giá <= 0 không phải "thiếu" mà là "không hợp lệ" — §3 gộp cả hai vào INVALID.
            bad |= np.nan_to_num(vals, nan=-1.0) <= 0
    return bad


FACTOR_WEIGHTS = {
    "PRICE_LOCATION": (("D", 0.50), ("M", 0.30), ("P", 0.20)),
    "MARKET_STRESS": (("R", 0.50), ("S7", 0.30), ("V", 0.20)),
    "RELATIVE_VALUE": (("W", 0.60), ("RP", 0.40)),
}

# Ablation models (Strategy §2.3) — chỉ dùng cho diagnostics
ABLATION_WEIGHTS = {
    "price_minimal": {"PRICE_LOCATION": (("D", 0.70), ("M", 0.30))},
    "stress_minimal": {"MARKET_STRESS": (("S7", 0.60), ("V", 0.40))},
}


def factor_scores(sf: pd.DataFrame, score_weights=(50, 30, 20),
                  weights_map: dict | None = None,
                  ind: pd.DataFrame | None = None) -> pd.DataFrame:
    """Ba factor score + OSCORE, áp rule DEGRADED (Strategy §3):

    Sub-component thiếu (NaN) nhận contribution = 0, KHÔNG rescale phần còn lại.
    Nếu MỌI sub-component của cả ba factor đều thiếu -> OSCORE = NaN (INVALID).

    WP-A4/A4.2 (đóng F-023): khi `ind` được truyền, INVALID còn được đặt theo đúng §3 —
    "giá/lịch sử ETH **hoặc** indicator bắt buộc không hợp lệ" — chứ không chỉ khi mất
    CẢ TÁM sub-factor. Định nghĩa cũ hẹp hơn spec: trên dữ liệu thật có gap, engine vẫn
    hành động ở những thời điểm §3 yêu cầu dừng. Ngày INVALID có `oscore = NaN` theo
    Data Model §4 ("opportunity_score_raw nullable chỉ khi INVALID").

    `ind=None` giữ nguyên hành vi cũ — dùng cho ablation/diagnostic vốn chỉ so sánh trọng
    số trên cùng một tập sub-factor, không phán xét chất lượng dữ liệu.
    """
    wm = dict(FACTOR_WEIGHTS)
    if weights_map:
        wm.update(weights_map)
    top = dict(zip(("PRICE_LOCATION", "MARKET_STRESS", "RELATIVE_VALUE"), score_weights))
    out = pd.DataFrame(index=sf.index)
    all_nan = None
    for factor, pairs in wm.items():
        acc = np.zeros(len(sf))
        nan_mask = np.ones(len(sf), dtype=bool)
        for name, w in pairs:
            vals = sf[name].to_numpy(float)
            acc += np.where(np.isnan(vals), 0.0, vals) * w
            nan_mask &= np.isnan(vals)
        out[factor.lower() + "_score"] = top[factor] * acc
        all_nan = nan_mask if all_nan is None else (all_nan & nan_mask)
    out["oscore"] = (out["price_location_score"] + out["market_stress_score"]
                     + out["relative_value_score"])
    out.loc[all_nan, "oscore"] = np.nan
    # Ranh giới §3: GOOD = đủ 8 sub-factor; DEGRADED = thiếu một phần sub-component;
    # INVALID = giá/lịch sử ETH hoặc indicator bắt buộc hỏng (khi có `ind`), hoặc mất hết
    # sub-factor (luật cũ, vẫn giữ để `ind=None` không đổi hành vi).
    n_missing = sf.isna().sum(axis=1)
    quality = np.select(
        [n_missing == 0, n_missing < len(sf.columns)], ["GOOD", "DEGRADED"], default="INVALID")
    if ind is not None:
        inv = invalid_mask(ind)
        quality = np.where(inv, "INVALID", quality)
        out.loc[inv, "oscore"] = np.nan
    out["data_quality"] = quality
    return out


def compute_scores(ind: pd.DataFrame, score_weights=(50, 30, 20)) -> pd.DataFrame:
    sf = sub_factors(ind)
    fs = factor_scores(sf, score_weights, ind=ind)
    return pd.concat([sf, fs], axis=1)


# ------------------------------------------------------------- unlocks

def smart_unlock(oscore):
    return clamp((oscore - 35) / 35)


def opportunity_unlock(oscore):
    return 0.60 * clamp((oscore - 65) / 30)


# ------------------------------------------------------------- ScoreMultiplier (piecewise)

_ANCHORS = np.array([40.0, 60.0, 70.0, 80.0, 90.0])
_MULTS = np.array([0.80, 0.90, 1.00, 1.15, 1.30])


def score_multiplier(oscore):
    """Nội suy tuyến tính từng đoạn qua anchor (<=40: 0.80; >=90: 1.30)."""
    return np.interp(oscore, _ANCHORS, _MULTS)


# ------------------------------------------------------------- Opportunity ladder weights

def opportunity_ladder_weights(oscore: float) -> list[float]:
    """O0..O4 theo Strategy §13 — chỉ chuyển weight giữa O4 và O0, tổng luôn 100%."""
    t = float(clamp((oscore - 70) / 10))
    return [0.10 * t, 0.15, 0.20, 0.25, 0.40 - 0.10 * t]
