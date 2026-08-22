"""Market Regime — Strategy §17: CRASH entry/exit, RECOVERY, và nhãn STRESSED [F1].

STRESSED chỉ là nhãn reporting, không có hiệu ứng execution.
"""
from __future__ import annotations

from dataclasses import dataclass

EXIT_SUSTAIN_SECONDS = 48 * 3600.0
RECOVERY_SECONDS = 72 * 3600.0


@dataclass
class RegimeTracker:
    regime: str = "NORMAL"          # NORMAL / STRESSED / CRASH / RECOVERY
    crash_entered_at: float | None = None
    exit_candidate_since: float | None = None
    recovery_started_at: float | None = None
    last_entry_reason: str | None = None

    def update(self, ts: float, return7d: float | None, return24h: float | None,
               oscore: float | None) -> str:
        r7 = return7d if return7d is not None else 0.0
        r24 = return24h if return24h is not None else 0.0

        if self.regime == "CRASH":
            # EXIT candidate: Return24H > -5% AND Return7D > -10% liên tục 48h
            if r24 > -0.05 and r7 > -0.10:
                if self.exit_candidate_since is None:
                    self.exit_candidate_since = ts
                elif ts - self.exit_candidate_since >= EXIT_SUSTAIN_SECONDS:
                    self.regime = "RECOVERY"
                    self.recovery_started_at = ts
                    self.exit_candidate_since = None
            else:
                self.exit_candidate_since = None
            return self.regime

        entry = (r7 <= -0.15 or r24 <= -0.10) and (oscore is not None and oscore >= 75)
        if self.regime == "RECOVERY":
            if entry:  # re-enter
                self._enter_crash(ts, r7, r24)
            elif ts - self.recovery_started_at >= RECOVERY_SECONDS:
                self.regime = "NORMAL"
                self.recovery_started_at = None
            if self.regime == "RECOVERY":
                return self.regime
            if self.regime == "CRASH":
                return self.regime

        if entry:
            self._enter_crash(ts, r7, r24)
            return self.regime

        # [F1] STRESSED: nhãn dẫn xuất, chỉ reporting
        self.regime = "STRESSED" if (r7 <= -0.10 or r24 <= -0.07) else "NORMAL"
        return self.regime

    def _enter_crash(self, ts: float, r7: float, r24: float):
        self.regime = "CRASH"
        self.crash_entered_at = ts
        self.exit_candidate_since = None
        self.recovery_started_at = None
        self.last_entry_reason = "CRASH_ENTRY_7D" if r7 <= -0.15 else "CRASH_ENTRY_24H"
