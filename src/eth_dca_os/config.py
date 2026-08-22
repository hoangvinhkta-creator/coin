"""strategy_config / execution_config theo Strategy §21 và Data Model §2–3.

strategy_config: tham số CHIẾN LƯỢC, biến thiên ở Gate 2.
execution_config: tham số MA SÁT, biến thiên ở Gate 3.
Mỗi snapshot là immutable và tự tính SHA256 hash (Data Model §14).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict, replace

from . import STRATEGY_VERSION

SMART_UNLOCK_MODES = ("HWM", "NO_HWM", "DECAY_HWM")
FUNDING_POLICIES = ("ON_DEMAND", "BULK_MONTHLY")
BEHAVIORAL_MODELS = ("OFF", "LOCAL_HOUR")

# Năm tuple score-weight đã đăng ký trước (Backtest §9, chia cho 100 khi áp dụng)
SCORE_WEIGHT_TUPLES = (
    (50, 30, 20),
    (55, 25, 20),
    (45, 35, 20),
    (50, 25, 25),
    (50, 35, 15),
)


def _hash_of(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def deterministic_hash(*parts) -> int:
    """Stochastic run seed = deterministic_hash(master_seed, run_id, simulation_id) (Backtest §13)."""
    blob = json.dumps(list(parts), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return int.from_bytes(hashlib.sha256(blob.encode("utf-8")).digest()[:8], "big")


@dataclass(frozen=True)
class StrategyConfig:
    # Bảng baseline Strategy §21 — 20 field
    strategy_version: str = STRATEGY_VERSION
    base_pct: float = 0.50
    smart_pct: float = 0.30
    opportunity_pct: float = 0.20
    opportunity_cap_months: int = 4
    smart_unlock_mode: str = "HWM"
    hwm_decay_step: float = 0.10
    hwm_decay_days: int = 7
    opportunity_activate_score: float = 68.0
    opportunity_suspend_score: float = 62.0
    smart_spacing_factor: float = 2.0
    smart_spacing_min: float = 0.04
    smart_spacing_max: float = 0.12
    opportunity_spacing_multiplier: float = 1.25
    opportunity_daily_limit_pct: float = 0.20
    max_zones_per_cycle: int = 2
    cooldown_hours: int = 48
    cooldown_override_pct: float = 0.07
    suspended_zone_hold_days: int = 7
    accounting_timezone: str = "Asia/Ho_Chi_Minh"
    # Score weights: không thuộc bảng §21 dưới dạng field riêng nhưng là chiều Gate 2
    # (PL/MS/RV trên thang điểm 50/30/20). Baseline = (50, 30, 20).
    score_weights: tuple = (50, 30, 20)
    # Metadata — đúng BA field được phép thêm theo XC-1 [F7]
    config_name: str = "baseline"

    def __post_init__(self):
        if self.smart_unlock_mode not in SMART_UNLOCK_MODES:
            raise ValueError(f"smart_unlock_mode invalid: {self.smart_unlock_mode}")
        if tuple(self.score_weights) not in SCORE_WEIGHT_TUPLES:
            raise ValueError(f"score_weights not pre-registered: {self.score_weights}")
        object.__setattr__(self, "score_weights", tuple(self.score_weights))
        if self.smart_pct < 0.15 - 1e-12:
            raise ValueError(
                f"validity constraint smart_pct >= 0.15 violated: {self.smart_pct}"
            )
        total = self.base_pct + self.smart_pct + self.opportunity_pct
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"base+smart+opportunity must equal 1.0, got {total}")

    @property
    def hash(self) -> str:
        d = asdict(self)
        d.pop("config_name")
        d["score_weights"] = list(self.score_weights)
        return _hash_of(d)

    def with_(self, **kw) -> "StrategyConfig":
        """Sinh biến thể (dùng cho manifest Gate 2); tự derive smart_pct khi đổi base/opp."""
        if ("base_pct" in kw or "opportunity_pct" in kw) and "smart_pct" not in kw:
            base = kw.get("base_pct", self.base_pct)
            opp = kw.get("opportunity_pct", self.opportunity_pct)
            kw["smart_pct"] = round(1.0 - base - opp, 10)
        return replace(self, **kw)

    def key(self) -> tuple:
        """Tuple định danh dùng khử trùng lặp trong manifest (bỏ metadata)."""
        d = asdict(self)
        d.pop("config_name")
        d["score_weights"] = tuple(self.score_weights)
        return tuple(sorted(d.items()))


@dataclass(frozen=True)
class ExecutionConfig:
    # Data Model §3
    execution_version: str = STRATEGY_VERSION
    user_delay_seconds: int = 4 * 3600
    funding_policy: str = "ON_DEMAND"
    funding_delay_seconds: int = 3600
    spot_fee_rate: float = 0.001
    slippage_bps: float = 5.0
    action_ttl_seconds: int = 12 * 3600
    behavioral_model: str = "OFF"
    p2p_unavailable_in_crash: bool = False
    config_name: str = "gate3_realistic"

    def __post_init__(self):
        if self.funding_policy not in FUNDING_POLICIES:
            raise ValueError(f"funding_policy invalid: {self.funding_policy}")
        if self.behavioral_model not in BEHAVIORAL_MODELS:
            raise ValueError(f"behavioral_model invalid: {self.behavioral_model}")
        # Ràng buộc Backtest §10: BULK_MONTHLY => funding_delay = 0
        if self.funding_policy == "BULK_MONTHLY" and self.funding_delay_seconds != 0:
            raise ValueError("BULK_MONTHLY requires funding_delay = 0 (Backtest §10)")

    @property
    def hash(self) -> str:
        d = asdict(self)
        d.pop("config_name")
        return _hash_of(d)

    def key(self) -> tuple:
        d = asdict(self)
        d.pop("config_name")
        return tuple(sorted(d.items()))


# Hai execution_config được commit ở Phase 0 (Impl Plan §2)
GATE1_LOW_FRICTION = ExecutionConfig(
    user_delay_seconds=15 * 60,
    funding_policy="BULK_MONTHLY",
    funding_delay_seconds=0,
    spot_fee_rate=0.001,
    slippage_bps=0.0,
    behavioral_model="OFF",
    config_name="gate1_low_friction",
)

GATE3_REALISTIC = ExecutionConfig(config_name="gate3_realistic")

BASELINE_STRATEGY = StrategyConfig()
