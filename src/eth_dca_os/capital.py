"""Capital engine — Strategy §4–§10: pool ledger A/R/D, unlock modes, hysteresis,
Opportunity Fund cap/overflow, Base schedule state, Month-End.

Mọi dịch chuyển vốn đi qua Pool (ledger-style, có audit trail) và giữ invariant
TOTAL = AVAILABLE + RESERVED + DEPLOYED, không âm (Data Model §14).

Phạm vi kế toán THEO ACCOUNTING MONTH (WP-A7, đóng F-035 — Data Model §5
`monthly_budgets`): Pool theo dõi thêm bộ đếm month-scope
(`month_reserved` / `month_deployed` / `carry_reserved`) cho pool được engine mở sổ
theo tháng (`open_accounting_month`, hiện chỉ SMART). Ledger lifetime GIỮ NGUYÊN vai
trò audit append-only (DM §6) — mở sổ không xoá/không ghi đè lịch sử. Quy tắc
carry-first cho reserve vắt tháng: xem CONVENTIONS #17.
"""
from __future__ import annotations

from dataclasses import dataclass, field

EPS = 1e-6


class InvariantError(RuntimeError):
    pass


@dataclass
class Pool:
    name: str
    available: float = 0.0
    reserved: float = 0.0
    deployed: float = 0.0
    ledger: list = field(default_factory=list)
    # ---- phạm vi ACCOUNTING MONTH (DM §5; WP-A7/F-035) — chỉ có ý nghĩa cho pool
    # được engine mở sổ theo tháng (SMART). Không ảnh hưởng A/R/D hay ledger.
    month_reserved: float = 0.0   # reserve tạo TRONG tháng đang mở (quyền tháng này đã dùng)
    month_deployed: float = 0.0   # deploy thực hiện TRONG tháng đang mở
    carry_reserved: float = 0.0   # reserve mang từ tháng trước (runoff, ngoài quyền tháng này)
    month_opened_at: float | None = None   # tương đương opened_at của monthly_budgets (DM §5)

    def _check(self):
        if self.available < -EPS or self.reserved < -EPS or self.deployed < -EPS:
            raise InvariantError(f"negative balance in {self.name}: {self}")

    def _log(self, entry_type: str, amount: float, reason: str, ts=None):
        self.ledger.append({
            "pool": self.name, "entry_type": entry_type, "amount": amount,
            "reason_code": reason, "timestamp": ts,
            "available_after": self.available, "reserved_after": self.reserved,
            "deployed_after": self.deployed,
        })

    @property
    def total(self) -> float:
        return self.available + self.reserved + self.deployed

    def open_accounting_month(self, ts: float | None = None):
        """Đóng sổ tháng cũ / mở sổ tháng mới cho PHẠM VI unlock theo tháng (DM §5).

        Không dịch chuyển vốn, không ghi ledger, không đổi A/R/D — lịch sử audit
        lifetime giữ nguyên (DM §6). Mọi reserve còn mở tại thời điểm mở sổ trở
        thành carry (lô tháng trước): carry không ăn và không trả quyền unlock của
        tháng mới (CONVENTIONS #17)."""
        self.carry_reserved = self.reserved
        self.month_reserved = 0.0
        self.month_deployed = 0.0
        self.month_opened_at = ts

    def contribute(self, amount: float, reason: str = "CONTRIBUTION", ts=None):
        self.available += amount
        self._check()
        self._log("CONTRIBUTION", amount, reason, ts)

    def reserve(self, amount: float, reason: str, ts=None) -> bool:
        """Chỉ được tạo nếu requested_reserve <= AVAILABLE (Strategy §8)."""
        if amount > self.available + EPS:
            return False
        self.available -= amount
        self.reserved += amount
        self.month_reserved += amount        # reserve mới luôn thuộc quyền tháng đang mở
        self._check()
        self._log("RESERVE", amount, reason, ts)
        return True

    def release(self, amount: float, reason: str, ts=None):
        if amount > self.reserved + EPS:
            raise InvariantError(f"release {amount} > reserved {self.reserved} in {self.name}")
        self.reserved -= amount
        self.available += amount
        # carry-first (CONVENTIONS #17): release rút lô tháng trước trước; chỉ phần
        # thuộc lô tháng này mới TRẢ LẠI quyền tháng này. Nếu nhận diện lô lẫn (carry
        # và lô mới cùng tồn tại), chiều sai lệch duy nhất là quyền KHÔNG được trả —
        # bảo thủ cho strategy (Backtest §1).
        take = min(amount, self.carry_reserved)
        self.carry_reserved -= take
        self.month_reserved = max(0.0, self.month_reserved - (amount - take))
        self._check()
        self._log("RELEASE", amount, reason, ts)

    def deploy_from_reserved(self, amount: float, reason: str, ts=None):
        if amount > self.reserved + EPS:
            raise InvariantError(f"deploy {amount} > reserved {self.reserved} in {self.name}")
        self.reserved -= amount
        self.deployed += amount
        # carry-first: deploy của lô tháng trước không ăn quyền tháng này (vốn đó đã
        # tiêu quyền của tháng nó được reserve — đếm nó lần nữa là chính họ hàng của
        # F-035). Với lô tháng này: chuyển bucket reserved -> deployed, TỔNG quyền đã
        # dùng (month_reserved + month_deployed) không đổi, nên nhận diện lô lẫn ở
        # nhánh này vô hại với quyền unlock.
        take = min(amount, self.carry_reserved)
        self.carry_reserved -= take
        rest = amount - take
        self.month_reserved = max(0.0, self.month_reserved - rest)
        self.month_deployed += rest
        self._check()
        self._log("DEPLOY", amount, reason, ts)

    def deploy_from_available(self, amount: float, reason: str, ts=None) -> bool:
        """Dùng cho Base schedule / Month-End (không qua zone reservation)."""
        if amount > self.available + EPS:
            return False
        self.available -= amount
        self.deployed += amount
        self.month_deployed += amount        # tiêu dùng thật của tháng đang mở (Base/Month-End)
        self._check()
        self._log("DEPLOY", amount, reason, ts)
        return True

    def transfer_available_to(self, other: "Pool", amount: float, reason: str, ts=None):
        if amount > self.available + EPS:
            raise InvariantError(f"transfer {amount} > available {self.available} in {self.name}")
        self.available -= amount
        other.available += amount
        self._check()
        other._check()
        self._log("OVERFLOW_OUT", amount, reason, ts)
        other._log("OVERFLOW_IN", amount, reason, ts)


@dataclass
class SmartUnlockState:
    """Ba mode HWM / NO_HWM / DECAY_HWM (Strategy §6)."""
    mode: str = "HWM"
    hwm_decay_step: float = 0.10
    hwm_decay_days: int = 7
    peak: float = 0.0
    last_revalidated_ts: float | None = None  # epoch seconds

    def month_reset(self, ts: float):
        self.peak = 0.0
        self.last_revalidated_ts = ts

    def effective_unlock(self, current_unlock: float, ts: float) -> float:
        if self.mode == "NO_HWM":
            return current_unlock
        if self.mode == "HWM":
            if current_unlock >= self.peak:
                self.peak = current_unlock
            return self.peak
        # DECAY_HWM
        if self.last_revalidated_ts is None:
            self.last_revalidated_ts = ts
        if current_unlock >= self.peak:
            self.peak = current_unlock
            self.last_revalidated_ts = ts
        else:
            period = self.hwm_decay_days * 86400.0
            while ts - self.last_revalidated_ts >= period:
                self.peak = max(self.peak - self.hwm_decay_step, current_unlock)
                self.last_revalidated_ts += period
            self.peak = max(self.peak, current_unlock)  # sàn = SMART_UNLOCK hiện tại
        return self.peak


@dataclass
class OpportunityHysteresis:
    """ACTIVE/SUSPENDED theo Strategy §5. ACTIVE với unlock = 0 (vùng 62–65) là hợp lệ."""
    activate_score: float = 68.0
    suspend_score: float = 62.0
    active: bool = False

    def update(self, oscore: float) -> bool:
        if oscore >= self.activate_score:
            self.active = True
        elif oscore <= self.suspend_score:
            self.active = False
        return self.active


@dataclass
class MonthlyCapital:
    """Ngân sách một accounting month + Opportunity Fund xuyên tháng."""
    base: Pool
    smart: Pool
    opportunity_fund: Pool           # xuyên tháng, quản lý bằng ledger
    monthly_opp_contribution: float  # để tính cap
    opportunity_cap_months: int

    @property
    def opportunity_cap(self) -> float:
        return self.monthly_opp_contribution * self.opportunity_cap_months


def apply_monthly_contribution(mc: MonthlyCapital, contribution: float, cfg, ts=None) -> dict:
    """Bơm contribution tháng mới: Base/Smart/Opp theo tỷ lệ; áp cap Opp -> overflow sang Smart
    của CHÍNH tháng đó (Strategy §7). Trả về breakdown để ghi monthly_budgets."""
    base_amt = contribution * cfg.base_pct
    smart_amt = contribution * cfg.smart_pct
    opp_amt = contribution * cfg.opportunity_pct
    mc.base.contribute(base_amt, "CONTRIBUTION", ts)
    mc.smart.contribute(smart_amt, "CONTRIBUTION", ts)

    cap = mc.opportunity_cap
    headroom = max(0.0, cap - mc.opportunity_fund.total)
    to_fund = min(opp_amt, headroom)
    overflow = opp_amt - to_fund
    if to_fund > 0:
        mc.opportunity_fund.contribute(to_fund, "CONTRIBUTION", ts)
    if overflow > 0:
        mc.smart.contribute(overflow, "CAP_OVERFLOW_TO_SMART", ts)
    return {"base": base_amt, "smart": smart_amt, "opportunity_added": to_fund,
            "opportunity_overflow_to_smart": overflow}


def smart_reservable(smart: Pool, budget_total: float, effective_unlock: float) -> float:
    """Phần Smart có thể reserve thêm TRONG THÁNG = unlocked(tháng) − (đã reserve +
    đã deploy TRONG THÁNG), kẹp trên bởi available. Không âm.

    Phạm vi theo ACCOUNTING MONTH (DM §5 `monthly_budgets`; ST §4/§6) — WP-A7 đóng
    F-035: `budget_total × effective_unlock` là đại lượng theo tháng nên chỉ được so
    với phần đã dùng TRONG THÁNG, không so với deployed luỹ kế toàn đời. "Vốn đã
    execute không relock" (ST §6) giữ nguyên TRONG phạm vi tháng: month_deployed vẫn
    bị trừ khi unlock tụt rồi tăng lại trong cùng tháng. Reserve mang từ tháng trước
    (carry) không ăn quyền tháng này nhưng cũng không nằm trong available.
    """
    unlocked = budget_total * effective_unlock
    return max(0.0, min(smart.available,
                        unlocked - smart.month_reserved - smart.month_deployed))


def opportunity_reservable(fund: Pool, unlock: float, hysteresis_active: bool,
                           used_today: float, daily_limit_pct: float) -> float:
    """Phần Opportunity có thể reserve thêm: unlock quyền dùng vốn + daily limit 20%/ngày."""
    if not hysteresis_active or unlock <= 0:
        return 0.0
    unlocked = fund.total * unlock
    headroom_unlock = max(0.0, unlocked - fund.reserved - fund.deployed)
    headroom_daily = max(0.0, fund.total * daily_limit_pct - used_today)
    return min(fund.available, headroom_unlock, headroom_daily)


# ------------------------------------------------------------- Base schedule

BASE_SCHEDULE = ((3, 0.40), (13, 0.30), (23, 0.30))  # (accounting day, % base) — Strategy §9


@dataclass
class BaseScheduleState:
    """Theo dõi tranche Base trong tháng, gồm execute sớm (EXECUTED_EARLY)."""
    executed: set = field(default_factory=set)     # index tranche đã chạy
    month_budget: float = 0.0

    def month_reset(self, month_budget: float):
        self.executed = set()
        self.month_budget = month_budget

    def pending(self):
        return [i for i in range(len(BASE_SCHEDULE)) if i not in self.executed]

    def next_pending(self):
        p = self.pending()
        return p[0] if p else None

    def tranche_amount(self, idx: int) -> float:
        return self.month_budget * BASE_SCHEDULE[idx][1]
