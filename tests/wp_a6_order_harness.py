"""Harness quan sát THỨ TỰ side-effect cho WP-A6 — Backtest §19 (18 bước cho mỗi nến 15m).

Engine không phơi bày thứ tự bước ra ngoài, nên harness này ghi lại DÒNG SỰ KIỆN CÓ TÁC
DỤNG PHỤ thật (ledger pool, chuyển trạng thái zone/ladder, fill, cập nhật regime, tạo
ladder...) bằng cách patch namespace `eth_dca_os.engine` và hai lớp dữ liệu trong
`eth_dca_os.ladders`. KHÔNG đổi hành vi engine — chỉ quan sát. Đồng hồ nến là chính lần
đọc `c["ts"][i]` ở đầu mỗi vòng lặp (bước 1 của §19: "tiến đồng hồ"), nên mọi sự kiện
được gắn đúng vào nến đang xử lý, kể cả những sự kiện xảy ra trước khi regime/score được
đọc.

Mỗi sự kiện được ánh xạ về SỐ BƯỚC §19 mà spec quy định cho nó (`spec_step`). Test thứ tự
kiểm rằng, trong MỘT nến, dãy số bước của các sự kiện không giảm. Mapping mặc định là
CHỮ của BT §19 (`LETTER_MAP`) — viết từ spec, không từ code — để lần chạy đầu tiên được
phép FAIL và lộ ra đúng sai lệch (task file WP-A6, "Trình tự bắt buộc").

Nhóm 16/17 (fill + ledger + cooldown) được coi là MỘT nhóm: spec tách "thực thi fill" và
"cập nhật ledger" thành hai bước nhưng cả hai là một giao dịch nguyên tử trong engine
(deploy rồi ghi purchase); harness không phán xét thứ tự bên trong nhóm đó.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import eth_dca_os.engine as _ENGINE
import eth_dca_os.ladders as ladders_mod
from eth_dca_os.capital import OpportunityHysteresis, Pool, SmartUnlockState
from eth_dca_os.execution import apply_fill
from eth_dca_os.ladders import (
    Ladder,
    Zone,
    create_crash_ladder,
    create_opportunity_ladder,
    create_smart_ladder,
    update_bullish_invalidation,
)
from eth_dca_os.regime import RegimeTracker

DAY = 86400.0
TZ = 7 * 3600
CANDLE = 900.0

# Nhóm bước: 16 và 17 gộp thành một nhóm (xem docstring module).
FILL_GROUP = 16


@dataclass
class Event:
    seq: int
    candle: int
    ts: float
    kind: str
    detail: dict = field(default_factory=dict)

    def __repr__(self):
        d = ", ".join(f"{k}={v}" for k, v in self.detail.items())
        return f"[{local_str(self.ts)} #{self.candle}] {self.kind}({d})"


@dataclass
class Trace:
    events: list = field(default_factory=list)
    candle: int = -1
    ts: float = float("nan")
    pools: list = field(default_factory=list)
    ladders: list = field(default_factory=list)          # Ladder instance theo thứ tự tạo
    trackers: list = field(default_factory=list)
    _seq: int = 0

    def emit(self, kind: str, **detail) -> Event:
        ev = Event(self._seq, self.candle, self.ts, kind, detail)
        self._seq += 1
        self.events.append(ev)
        return ev

    # ---- truy vấn
    def by_candle(self) -> dict:
        out: dict[int, list] = {}
        for ev in self.events:
            out.setdefault(ev.candle, []).append(ev)
        return out

    def ladder_by_id(self, ladder_id: int):
        for lad in self.ladders:
            if lad.ladder_id == ladder_id:
                return lad
        return None

    def pool(self, name: str) -> Pool:
        for p in self.pools:
            if p.name == name:
                return p
        raise KeyError(name)

    def zone_by_id(self, zone_id: int):
        for lad in self.ladders:
            for z in lad.zones:
                if z.zone_id == zone_id:
                    return z
        return None


def local_str(ts: float) -> str:
    if ts != ts:  # NaN
        return "??"
    return pd.Timestamp(ts + TZ, unit="s").strftime("%Y-%m-%d %H:%M")


class _TsClock:
    """Proxy cho mảng `c["ts"]`: lần đọc `c["ts"][i]` với i mới là bước 1 (tiến đồng hồ)."""

    def __init__(self, arr: np.ndarray, trace: Trace):
        self._arr = arr
        self._trace = trace

    def __len__(self):
        return len(self._arr)

    def __getitem__(self, i):
        v = self._arr[i]
        if isinstance(i, (int, np.integer)) and int(i) > self._trace.candle:
            self._trace.candle = int(i)
            self._trace.ts = float(v)
            self._trace.emit("CLOCK", ts=float(v))
        return v

    def __getattr__(self, name):  # mọi thứ khác (dtype, shape...) uỷ quyền cho mảng
        return getattr(self._arr, name)


def instrument(monkeypatch, engine=None) -> Trace:
    """Patch namespace engine/ladders để chụp dòng sự kiện. Hành vi engine KHÔNG đổi.

    `monkeypatch` chỉ cần có `.setattr(obj, name, value)` (pytest MonkeyPatch hoặc lớp
    tương đương ngoài pytest — xem `SimpleMonkeyPatch`). `engine` cho phép trace một
    module engine khác (ví dụ bản ĐÃ BỊ ĐẢO THỨ TỰ có chủ đích để chứng minh test phát
    hiện được — CHECK-A6-05); mặc định là `eth_dca_os.engine`.
    """
    engine_mod = engine if engine is not None else _ENGINE
    tr = Trace()

    # ---- đồng hồ nến (bước 1)
    orig_prep = engine_mod._prep_candles

    def prep(eth15, start_ts, end_ts):
        c = orig_prep(eth15, start_ts, end_ts)
        c["ts"] = _TsClock(c["ts"], tr)
        return c

    monkeypatch.setattr(engine_mod, "_prep_candles", prep)

    # ---- ledger pool
    class TracingPool(Pool):
        def __init__(self, name, *a, **kw):
            super().__init__(name, *a, **kw)
            tr.pools.append(self)

        def open_accounting_month(self, ts=None):
            tr.emit("OPEN_MONTH", pool=self.name)
            return super().open_accounting_month(ts)

        def contribute(self, amount, reason="CONTRIBUTION", ts=None):
            tr.emit("CONTRIBUTE", pool=self.name, amount=amount, reason=reason)
            return super().contribute(amount, reason, ts)

        def reserve(self, amount, reason, ts=None):
            ok = super().reserve(amount, reason, ts)
            if ok:
                tr.emit("RESERVE", pool=self.name, amount=amount, reason=reason)
            return ok

        def release(self, amount, reason, ts=None):
            tr.emit("RELEASE", pool=self.name, amount=amount, reason=reason)
            return super().release(amount, reason, ts)

        def deploy_from_reserved(self, amount, reason, ts=None):
            tr.emit("DEPLOY_RESERVED", pool=self.name, amount=amount, reason=reason)
            return super().deploy_from_reserved(amount, reason, ts)

        def deploy_from_available(self, amount, reason, ts=None):
            ok = super().deploy_from_available(amount, reason, ts)
            if ok:
                tr.emit("DEPLOY_AVAILABLE", pool=self.name, amount=amount, reason=reason)
            return ok

        def transfer_available_to(self, other, amount, reason, ts=None):
            tr.emit("TRANSFER", pool=self.name, to=other.name, amount=amount, reason=reason)
            return super().transfer_available_to(other, amount, reason, ts)

    monkeypatch.setattr(engine_mod, "Pool", TracingPool)

    # ---- HWM reset (bước 4)
    class TracingSmartUnlock(SmartUnlockState):
        def month_reset(self, ts):
            tr.emit("HWM_RESET")
            return super().month_reset(ts)

    monkeypatch.setattr(engine_mod, "SmartUnlockState", TracingSmartUnlock)

    # ---- hysteresis (dấu hiệu quan sát được của bước 8: score/unlock mới có hiệu lực)
    class TracingHyst(OpportunityHysteresis):
        def update(self, oscore):
            out = super().update(oscore)
            tr.emit("HYST_UPDATE", oscore=float(oscore), active=out)
            return out

    monkeypatch.setattr(engine_mod, "OpportunityHysteresis", TracingHyst)

    # ---- regime (bước 10)
    class TracingTracker(RegimeTracker):
        def update(self, ts, return7d, return24h, oscore):
            prev = self.state
            out = super().update(ts, return7d, return24h, oscore)
            tr.emit("REGIME_UPDATE", prev=prev, new=self.state, label=out,
                    oscore=oscore, r7=return7d, r24=return24h)
            return out

    def tracker_factory(*a, **kw):
        t = TracingTracker(*a, **kw)
        tr.trackers.append(t)
        return t

    monkeypatch.setattr(engine_mod, "RegimeTracker", tracker_factory)

    # ---- fill (bước 16)
    def traced_fill(nominal, open_price, exec_cfg):
        eth, eff = apply_fill(nominal, open_price, exec_cfg)
        tr.emit("FILL", nominal=nominal, price=eff)
        return eth, eff

    monkeypatch.setattr(engine_mod, "apply_fill", traced_fill)

    # ---- bullish invalidation (bước 18 theo chữ §19)
    def traced_bull(ladder, daily_close):
        out = update_bullish_invalidation(ladder, daily_close)
        tr.emit("BULLISH_CHECK", ladder=ladder.ladder_id, invalidated=out)
        return out

    monkeypatch.setattr(engine_mod, "update_bullish_invalidation", traced_bull)

    # ---- zone / ladder: chuyển trạng thái
    class TracingZone(Zone):
        def __setattr__(self, name, value):
            if name == "status":
                old = self.__dict__.get("status")
                if old is not None and old != value:
                    tr.emit("ZONE", zone=self.zone_id, ladder=self.ladder_id,
                            idx=self.zone_index, old=old, new=value)
            object.__setattr__(self, name, value)

    class TracingLadder(Ladder):
        def __setattr__(self, name, value):
            if name == "status":
                old = self.__dict__.get("status")
                if old is not None and old != value:
                    tr.emit("LADDER", ladder=self.ladder_id, type=self.type, old=old, new=value)
            object.__setattr__(self, name, value)

    monkeypatch.setattr(ladders_mod, "Zone", TracingZone)
    monkeypatch.setattr(ladders_mod, "Ladder", TracingLadder)

    def wrap_create(fn, typ):
        def inner(*a, **kw):
            lad = fn(*a, **kw)
            tr.ladders.append(lad)
            tr.emit("LADDER_CREATED", ladder=lad.ladder_id, type=typ,
                    anchor=lad.anchor_price, created_at=lad.created_at)
            return lad
        return inner

    monkeypatch.setattr(engine_mod, "create_smart_ladder", wrap_create(create_smart_ladder, "SMART"))
    monkeypatch.setattr(engine_mod, "create_opportunity_ladder",
                        wrap_create(create_opportunity_ladder, "OPPORTUNITY"))
    monkeypatch.setattr(engine_mod, "create_crash_ladder", wrap_create(create_crash_ladder, "CRASH"))
    return tr


class SimpleMonkeyPatch:
    """Tương đương tối thiểu của pytest MonkeyPatch để dùng ngoài pytest (công cụ đo)."""

    def __init__(self):
        self._undo = []

    def setattr(self, obj, name, val):
        self._undo.append((obj, name, getattr(obj, name)))
        setattr(obj, name, val)

    def undo(self):
        for obj, name, val in reversed(self._undo):
            setattr(obj, name, val)
        self._undo.clear()


# =============================================================== ánh xạ về bước §19

# Lý do (reason_code) của một lần RELEASE/CANCEL -> bước §19 theo CHỮ của spec.
#   LADDER_EXPIRED (Smart, tại rollover)  -> 3   "cho hết hạn các Smart ladder của tháng trước"
#   LADDER_EXPIRED (Opportunity 90 ngày)  -> 18  "expiry"
#   BULLISH_INVALIDATION                  -> 18  "bullish invalidation"
#   OPPORTUNITY_SUSPENDED (hết 7 ngày)    -> 18  "suspension"
#   CRASH_ENTRY                            -> 10  ST §14 buộc cancel/release "tại thời điểm vào
#                                                 CRASH", tức trong bước cập nhật regime
#   RECOVERY_END                           -> 18  "expiry" của Crash ladder (ST §18.3)
#   ACTION_MISSED / ACTION_TTL_EXPIRED     -> 12  "áp TTL, đánh dấu MISSED"
_RELEASE_REASON_STEP = {
    "BULLISH_INVALIDATION": 18,
    "OPPORTUNITY_SUSPENDED": 18,
    "CRASH_ENTRY": 10,
    "RECOVERY_END": 18,
    "ACTION_MISSED": 12,
    "ACTION_TTL_EXPIRED": 12,
}


def _is_rollover_candle(events) -> bool:
    return any(ev.kind == "OPEN_MONTH" for ev in events)


def letter_map(events: list) -> list:
    """Ánh xạ từng sự kiện của MỘT nến về bước §19 theo chữ của spec.

    Trả về list (step | None, event). `None` = sự kiện không có vị trí trong §19 (bị bỏ
    qua khi kiểm thứ tự) — hiện chỉ dùng cho sự kiện không xác định được ngữ cảnh.
    """
    rollover = _is_rollover_candle(events)
    out = []
    last_release_reason = None
    last_deploy_step = None
    for ev in events:
        k, d = ev.kind, ev.detail
        step = None
        if k == "CLOCK":
            step = 1
        elif k == "OPEN_MONTH":
            step = 3        # ranh giới sổ: sau settle (3), trước HWM reset (4) — CONVENTIONS #17
        elif k == "HWM_RESET":
            step = 4
        elif k == "CONTRIBUTE":
            step = 6 if d["reason"] == "CAP_OVERFLOW_TO_SMART" else 5
        elif k == "TRANSFER":
            step = 3 if rollover else 9     # MONTH_END_SMART: overflow 50% sang Opp (ST §10)
        elif k == "DEPLOY_AVAILABLE":
            r = d["reason"]
            if r in ("BASE_SCHEDULE", "BASE_ADVANCE_SCORE"):
                step = 9
            elif r in ("MONTH_END_BASE", "MONTH_END_SMART"):
                # đóng sổ tại rollover = bước 3; Day 25/28 12:00 = sự kiện theo lịch, cùng
                # khe với Base schedule (bước 9; CONVENTIONS #7)
                step = 3 if rollover else 9
            last_deploy_step = step
        elif k == "DEPLOY_RESERVED":
            step = FILL_GROUP           # 17 — gộp nhóm 16/17
            last_deploy_step = step
        elif k == "FILL":
            step = last_deploy_step if last_deploy_step is not None else FILL_GROUP
        elif k == "RESERVE":
            step = 14                   # "tạo hoặc điều chỉnh reservation"
        elif k == "LADDER_CREATED":
            step = 14
        elif k == "RELEASE":
            r = d["reason"]
            last_release_reason = r
            if r == "LADDER_EXPIRED":
                lad_type = _ladder_type_of_release(ev, events)
                step = 18 if lad_type == "OPPORTUNITY" else (3 if rollover else 9)
            else:
                step = _RELEASE_REASON_STEP.get(r)
        elif k == "HYST_UPDATE":
            step = 8
        elif k == "REGIME_UPDATE":
            step = 10
        elif k == "BULLISH_CHECK":
            step = 18
        elif k == "ZONE":
            new, old = d["new"], d["old"]
            if new == "TRIGGERED":
                step = 13
            elif new == "ACTION_PENDING":
                step = 14
            elif new == "EXECUTED":
                step = FILL_GROUP
            elif new == "MISSED":
                step = 12
            elif new == "SUSPENDED" or (old == "SUSPENDED" and new == "ACTIVE"):
                step = 18
            elif new == "CANCELLED":
                step = _cancel_step(last_release_reason, ev, events, rollover)
        elif k == "LADDER":
            new = d["new"]
            if new == "INVALIDATED":
                step = 18
            elif new == "COMPLETED":
                step = 18
            elif new == "SUSPENDED":
                step = 18
            elif new == "EXPIRED":
                step = 18 if d["type"] == "OPPORTUNITY" else (3 if rollover else 9)
            elif new == "CANCELLED":
                step = _cancel_step(last_release_reason, ev, events, rollover)
        out.append((step, ev))
    return out


def _ladder_type_of_release(ev, events) -> str | None:
    """RELEASE LADDER_EXPIRED: tìm sự kiện ZONE/LADDER kế tiếp trong cùng nến để biết loại."""
    for nxt in events:
        if nxt.seq <= ev.seq:
            continue
        if nxt.kind == "LADDER" and nxt.detail["new"] == "EXPIRED":
            return nxt.detail["type"]
    return None


def _cancel_step(last_release_reason, ev, events, rollover):
    if last_release_reason is None:
        return None
    if last_release_reason == "LADDER_EXPIRED":
        lad_type = None
        for nxt in events:
            if nxt.seq > ev.seq and nxt.kind == "LADDER" and nxt.detail["new"] == "EXPIRED":
                lad_type = nxt.detail["type"]
                break
        return 18 if lad_type == "OPPORTUNITY" else (3 if rollover else 9)
    return _RELEASE_REASON_STEP.get(last_release_reason)


def order_violations(trace: Trace, mapper=letter_map) -> list:
    """Mọi cặp sự kiện liền kề (theo bước đã ánh xạ) trong cùng nến mà bước GIẢM.

    Trả về list dict {ts, candle, prev_step, prev, step, ev}. Rỗng = thứ tự đúng.
    """
    out = []
    for candle, events in trace.by_candle().items():
        mapped = [(s, e) for s, e in mapper(events) if s is not None]
        for (s0, e0), (s1, e1) in zip(mapped, mapped[1:]):
            if s1 < s0:
                out.append({"ts": e1.ts, "candle": candle, "prev_step": s0, "prev": e0,
                            "step": s1, "ev": e1})
    return out


def format_violations(viol: list, limit: int = 40) -> str:
    lines = []
    for v in viol[:limit]:
        lines.append(f"  {local_str(v['ts'])}  bước {v['prev_step']:>2} -> {v['step']:>2}   "
                     f"{v['prev'].kind}{_short(v['prev'])}  =>  {v['ev'].kind}{_short(v['ev'])}")
    if len(viol) > limit:
        lines.append(f"  ... và {len(viol) - limit} vi phạm nữa")
    return "\n".join(lines)


def _short(ev: Event) -> str:
    keys = ("reason", "old", "new", "zone", "ladder", "type", "amount", "prev")
    parts = [f"{k}={ev.detail[k]}" for k in keys if k in ev.detail]
    return "(" + ", ".join(parts) + ")" if parts else ""


def violation_signature(viol: list) -> dict:
    """Đếm vi phạm theo cặp (kind_trước -> kind_sau, bước_trước -> bước_sau)."""
    sig: dict = {}
    for v in viol:
        key = (f"{v['prev'].kind}{_tag(v['prev'])}@{v['prev_step']}",
               f"{v['ev'].kind}{_tag(v['ev'])}@{v['step']}")
        sig[key] = sig.get(key, 0) + 1
    return sig


def _tag(ev: Event) -> str:
    d = ev.detail
    if ev.kind == "ZONE":
        return f"[{d['old']}->{d['new']}]"
    if ev.kind == "LADDER":
        return f"[{d['type']}:{d['old']}->{d['new']}]"
    if ev.kind in ("RELEASE", "DEPLOY_AVAILABLE", "DEPLOY_RESERVED", "RESERVE", "CONTRIBUTE"):
        return f"[{d['reason']}]"
    if ev.kind == "LADDER_CREATED":
        return f"[{d['type']}]"
    return ""


# =============================================================== dựng kịch bản

def candle_index(eth15: pd.DataFrame, start_utc: pd.Timestamp, day_k: int, local_hour: float) -> int:
    """Chỉ số hàng của nến 15m tại (ngày local thứ k tính từ Day 1 = 0, giờ local)."""
    ts = ((pd.DatetimeIndex(eth15["open_time"]) - pd.Timestamp(0, tz="UTC"))
          / pd.Timedelta(seconds=1)).to_numpy(float)
    target = start_utc.value / 1e9 + day_k * DAY + local_hour * 3600.0
    # so sánh tuyệt đối: rtol mặc định của np.isclose trên epoch ~1.6e9 rộng tới ~4.6 giờ
    hits = np.nonzero(np.abs(ts - target) < 1.0)[0]
    assert len(hits) == 1, f"không tìm thấy nến duy nhất tại day={day_k} hour={local_hour}"
    return int(hits[0])


def override_candles(eth15: pd.DataFrame, start_utc: pd.Timestamp, overrides: dict) -> pd.DataFrame:
    """Ghi đè OHLC của từng nến: {(day_k, local_hour): {"low":..., "close":..., ...}}.

    Không ép liên tục open/close giữa các nến (engine không cần). Tự kiểm: giá đã đặt
    phải xuất hiện thật trong khung dữ liệu (chống lỗi ánh xạ ngày kiểu F-E2-01).
    """
    df = eth15.copy()
    for (day_k, hour), cols in overrides.items():
        i = candle_index(df, start_utc, day_k, hour)
        for col, val in cols.items():
            df.loc[i, col] = float(val)
        # giữ bất biến OHLC tối thiểu: low <= min(open, close) <= max(open, close) <= high
        row = df.loc[i]
        lo = min(row["low"], row["open"], row["close"])
        hi = max(row["high"], row["open"], row["close"])
        df.loc[i, "low"], df.loc[i, "high"] = lo, hi
    for (day_k, hour), cols in overrides.items():
        i = candle_index(df, start_utc, day_k, hour)
        for col, val in cols.items():
            if col in ("open", "close"):
                assert df.loc[i, col] == float(val)
            elif col == "low":
                assert df.loc[i, "low"] <= float(val)
    return df


def drop_candles(eth15: pd.DataFrame, start_utc: pd.Timestamp, drops) -> pd.DataFrame:
    """Xoá nến 15m theo (ngày local thứ k, giờ bắt đầu, giờ kết thúc) — như WP-A4."""
    ts = ((pd.DatetimeIndex(eth15["open_time"]) - pd.Timestamp(0, tz="UTC"))
          / pd.Timedelta(seconds=1)).to_numpy(float)
    local = ts + TZ
    day0 = int((start_utc.value // 10**9 + TZ) // DAY)
    keep = np.ones(len(eth15), dtype=bool)
    for k, h0, h1 in drops:
        mask = ((local // DAY).astype(int) == day0 + k) & \
               (local % DAY >= h0 * 3600) & (local % DAY < h1 * 3600)
        keep &= ~mask
    return eth15[keep].reset_index(drop=True)


def run_traced(monkeypatch, day_specs, overrides=None, drops=(), strategy_cfg=None,
               exec_cfg=None, contribution=100.0, first_local_day="2023-03-01",
               engine=None):
    """Dựng dataset theo ngày (wp_a3_harness), ghi đè/xoá nến, chạy engine có trace."""
    from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
    from wp_a3_harness import build_dataset

    engine_mod = engine if engine is not None else _ENGINE
    ds, scores, start, end = build_dataset(day_specs, first_local_day=first_local_day)
    ds = dict(ds)
    eth15 = ds["ETHUSDT_15m"]
    if overrides:
        eth15 = override_candles(eth15, start, overrides)
    if drops:
        eth15 = drop_candles(eth15, start, drops)
    ds["ETHUSDT_15m"] = eth15
    tr = instrument(monkeypatch, engine=engine_mod)
    res = engine_mod.run_engine(ds, scores, strategy_cfg or BASELINE_STRATEGY,
                                exec_cfg or GATE1_LOW_FRICTION, start, end,
                                contribution=contribution)
    return res, tr, (ds, scores, start, end)


# =============================================================== đảo thứ tự có chủ đích

def load_engine_from_source(src_text: str, name: str = "eth_dca_os._engine_mutant"):
    """Nạp một bản `engine.py` từ chuỗi mã nguồn thành module riêng (relative import vẫn
    trỏ về `eth_dca_os`). Dùng để tạo bản engine ĐÃ BỊ ĐẢO THỨ TỰ có chủ đích."""
    import sys
    import types
    mod = types.ModuleType(name)
    mod.__package__ = "eth_dca_os"
    mod.__file__ = _ENGINE.__file__
    # dataclass trong module (RunResult) tra `sys.modules[cls.__module__]` khi annotation là
    # chuỗi (`from __future__ import annotations`) — phải đăng ký trước khi exec.
    sys.modules[name] = mod
    try:
        exec(compile(src_text, _ENGINE.__file__, "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    return mod


def move_block(src: str, start_marker: str, end_marker: str, before_marker: str) -> str:
    """Cắt đoạn [start_marker, end_marker) và dán ngay trước before_marker. Mọi marker phải
    tồn tại đúng một lần — nếu engine.py được đổi nhãn khối, hàm này đỏ thay vì im lặng."""
    for m in (start_marker, end_marker, before_marker):
        assert src.count(m) == 1, f"marker không duy nhất/không tồn tại trong engine.py: {m!r}"
    i = src.index(start_marker)
    j = src.index(end_marker, i)
    assert j > i
    block = src[i:j]
    rest = src[:i] + src[j:]
    k = rest.index(before_marker)
    return rest[:k] + block + rest[k:]


def candle_ts(start_utc: pd.Timestamp, day_k: int, local_hour: float) -> float:
    return start_utc.value / 1e9 + day_k * DAY + local_hour * 3600.0


def events_at(trace: Trace, ts: float) -> list:
    return [ev for ev in trace.events if ev.ts == ts]
