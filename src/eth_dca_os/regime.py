"""Market Regime — Strategy §17: CRASH entry/exit, RECOVERY, và nhãn STRESSED [F1].

Thiết kế (WP-A3, đóng F-001/F-022 — xem docs/CONVENTIONS.md #14, #15):

- `state`  = TRẠNG THÁI NỀN của máy trạng thái §17.1–§17.2, chỉ gồm
  NORMAL / CRASH / RECOVERY. Mọi quyết định EXECUTION trong engine đọc trường này.
- `label`  = NHÃN BÁO CÁO theo enum Market Regime §16
  (NORMAL / STRESSED / CRASH / RECOVERY). STRESSED là nhãn dẫn xuất chỉ dùng cho
  reporting/phân rã metric (§17.3 [F1]) — không code execution nào được đọc nhãn.
  `regime` là alias đọc của `label` để giữ bề mặt reporting cũ.

- None KHÔNG bị ép về 0.0: một điều kiện chỉ được coi là thoả khi có dữ liệu thật
  chứng minh nó thoả (Backtest §1 — giả định bảo thủ; Strategy §3 — dữ liệu xấu
  không được đẩy trạng thái theo hướng có lợi). Riêng điều kiện exit "liên tục
  trong 48h" (§17.2): một quan sát thiếu dữ liệu phá chuỗi liên tục.
"""
from __future__ import annotations

from dataclasses import dataclass

EXIT_SUSTAIN_SECONDS = 48 * 3600.0
RECOVERY_SECONDS = 72 * 3600.0


@dataclass
class RegimeTracker:
    state: str = "NORMAL"           # trạng thái nền: NORMAL / CRASH / RECOVERY
    label: str = "NORMAL"           # nhãn báo cáo:  NORMAL / STRESSED / CRASH / RECOVERY
    crash_entered_at: float | None = None
    exit_candidate_since: float | None = None
    recovery_started_at: float | None = None
    last_entry_reason: str | None = None

    @property
    def regime(self) -> str:
        """Nhãn báo cáo (§16). Execution phải dùng `state`, không dùng nhãn này."""
        return self.label

    def update(self, ts: float, return7d: float | None, return24h: float | None,
               oscore: float | None) -> str:
        r7, r24 = return7d, return24h
        entry = ((r7 is not None and r7 <= -0.15) or (r24 is not None and r24 <= -0.10)) \
            and (oscore is not None and oscore >= 75)

        if self.state == "CRASH":
            # EXIT candidate: Return24H > -5% AND Return7D > -10% liên tục 48h (§17.2).
            # Thiếu dữ liệu => điều kiện KHÔNG được coi là thoả và chuỗi liên tục bị đứt.
            exit_ok = (r24 is not None and r24 > -0.05) and (r7 is not None and r7 > -0.10)
            if exit_ok:
                if self.exit_candidate_since is None:
                    self.exit_candidate_since = ts
                elif ts - self.exit_candidate_since >= EXIT_SUSTAIN_SECONDS:
                    self.state = "RECOVERY"
                    self.recovery_started_at = ts
                    self.exit_candidate_since = None
            else:
                self.exit_candidate_since = None
        elif self.state == "RECOVERY":
            if entry:  # re-enter
                self._enter_crash(ts, r7, r24)
            elif ts - self.recovery_started_at >= RECOVERY_SECONDS:
                # Hết 72h Recovery: trạng thái nền LUÔN về NORMAL (§17.2); thị trường còn
                # yếu hay không chỉ ảnh hưởng NHÃN (§17.3), không ảnh hưởng trạng thái nền.
                self.state = "NORMAL"
                self.recovery_started_at = None
        else:  # NORMAL
            if entry:
                self._enter_crash(ts, r7, r24)

        # [F1] §17.3: nhãn được đánh giá lại mỗi nến SAU khi cập nhật CRASH/RECOVERY
        self.label = self._derive_label(r7, r24)
        return self.label

    def _derive_label(self, r7: float | None, r24: float | None) -> str:
        """Nhãn dẫn xuất §17.3 — chỉ reporting. STRESSED cần BẰNG CHỨNG thật về yếu."""
        if self.state != "NORMAL":
            return self.state
        stressed = (r7 is not None and r7 <= -0.10) or (r24 is not None and r24 <= -0.07)
        return "STRESSED" if stressed else "NORMAL"

    def _enter_crash(self, ts: float, r7: float | None, r24: float | None):
        self.state = "CRASH"
        self.crash_entered_at = ts
        self.exit_candidate_since = None
        self.recovery_started_at = None
        self.last_entry_reason = "CRASH_ENTRY_7D" if (r7 is not None and r7 <= -0.15) \
            else "CRASH_ENTRY_24H"
