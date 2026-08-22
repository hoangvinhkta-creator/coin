"""Delay model & behavioral simulation — Backtest §5–§6."""
from __future__ import annotations

import numpy as np

MISSED = -1.0  # sentinel: action MISSED do behavioral model


def total_delay_seconds(exec_cfg) -> float:
    """total_delay = user_delay + funding_delay (funding_delay = 0 nếu pre-funded/BULK)."""
    fd = 0.0 if exec_cfg.funding_policy == "BULK_MONTHLY" else exec_cfg.funding_delay_seconds
    return exec_cfg.user_delay_seconds + fd


def behavioral_delay_seconds(trigger_local_hour: int, rng: np.random.Generator,
                             seconds_to_7am: float, ttl_seconds: float) -> float:
    """Bốc thăm delay theo phân phối local-hour (Backtest §6). Trả về giây, hoặc MISSED."""
    u = rng.random()
    if 7 <= trigger_local_hour <= 22:
        if u < 0.50:
            return rng.uniform(0, 3600)
        if u < 0.80:
            return rng.uniform(3600, 4 * 3600)
        if u < 0.95:
            return rng.uniform(4 * 3600, 12 * 3600)
        return MISSED
    else:
        if u < 0.10:
            return rng.uniform(0, 3600)
        if u < 0.35:
            return rng.uniform(3600, 4 * 3600)
        if u < 0.80:
            # thực thi tại OPEN nến đầu tiên tại/sau 07:00 local nếu còn TTL
            return seconds_to_7am if seconds_to_7am <= ttl_seconds else MISSED
        return MISSED


def apply_fill(usdt_nominal: float, open_price: float, exec_cfg) -> tuple[float, float]:
    """Trả về (eth_amount, effective_price) sau slippage + fee (Backtest §19 bước 16)."""
    eff_price = open_price * (1 + exec_cfg.slippage_bps / 10_000.0)
    eth = usdt_nominal * (1 - exec_cfg.spot_fee_rate) / eff_price
    return eth, eff_price
