"""Harness quan sát cho các test vòng đời WP-A3 (F-001, F-021, F-022, F-030).

Engine không trả về pools/ladders/regime trong RunResult, nên harness này chụp state
bằng cách patch các tên trong namespace của `eth_dca_os.engine` bằng subclass/wrapper
ghi lại instance. KHÔNG đổi hành vi engine — chỉ quan sát. Nhờ vậy các finding được
tái hiện và kiểm chứng ở tầng engine thật, đúng yêu cầu WP-A3 ("không chỉ kiểm tra
biến regime").

Ngoài ra cung cấp builder dataset tổng hợp có kiểm soát theo ngày (giá phẳng trong
ngày, OHLC tự đặt) để dựng đúng kịch bản CRASH → RECOVERY → STRESSED của F-001.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import eth_dca_os.engine as engine_mod
from eth_dca_os.capital import Pool
from eth_dca_os.ladders import create_crash_ladder, create_opportunity_ladder, create_smart_ladder
from eth_dca_os.regime import RegimeTracker

DAY = 86400.0
TZ = 7 * 3600  # Asia/Ho_Chi_Minh


@dataclass
class Recorder:
    pools: list = field(default_factory=list)            # Pool instances theo thứ tự tạo
    ladders: list = field(default_factory=list)          # Ladder instances theo thứ tự tạo
    trackers: list = field(default_factory=list)         # RegimeTracker instances
    transitions: list = field(default_factory=list)      # (ts, prev_label, new_label)
    state_transitions: list = field(default_factory=list)  # (ts, prev_state, new_state) nếu có .state
    reserves: list = field(default_factory=list)         # (pool_name, amount, reason, ts) mỗi lần reserve

    def pool(self, name: str) -> Pool:
        for p in self.pools:
            if p.name == name:
                return p
        raise KeyError(name)

    def crash_ladders(self):
        return [l for l in self.ladders if l.type == "CRASH"]


def instrument(monkeypatch) -> Recorder:
    """Patch namespace engine để chụp Pool/Ladder/RegimeTracker. Hành vi không đổi."""
    rec = Recorder()

    class RecordingPool(Pool):
        def __init__(self, name: str, *a, **kw):
            super().__init__(name, *a, **kw)
            rec.pools.append(self)

        def reserve(self, amount, reason, ts=None):
            ok = super().reserve(amount, reason, ts)
            if ok:
                rec.reserves.append((self.name, amount, reason, ts))
            return ok

    class RecordingTracker(RegimeTracker):
        def __post_init__(self):  # dataclass không có __post_init__ mặc định — an toàn
            pass

        def update(self, ts, return7d, return24h, oscore):
            prev_label = self.regime
            prev_state = getattr(self, "state", None)
            out = super().update(ts, return7d, return24h, oscore)
            if out != prev_label:
                rec.transitions.append((ts, prev_label, out))
            new_state = getattr(self, "state", None)
            if prev_state is not None and new_state != prev_state:
                rec.state_transitions.append((ts, prev_state, new_state))
            return out

    def _wrap(fn):
        def inner(*a, **kw):
            lad = fn(*a, **kw)
            rec.ladders.append(lad)
            return lad
        return inner

    def _tracker_factory(*a, **kw):
        t = RecordingTracker(*a, **kw)
        rec.trackers.append(t)
        return t

    monkeypatch.setattr(engine_mod, "Pool", RecordingPool)
    monkeypatch.setattr(engine_mod, "RegimeTracker", _tracker_factory)
    monkeypatch.setattr(engine_mod, "create_crash_ladder", _wrap(create_crash_ladder))
    monkeypatch.setattr(engine_mod, "create_smart_ladder", _wrap(create_smart_ladder))
    monkeypatch.setattr(engine_mod, "create_opportunity_ladder", _wrap(create_opportunity_ladder))
    return rec


# ---------------------------------------------------------------- dataset builder

def build_dataset(day_specs: list[dict], first_local_day: str = "2023-03-01",
                  warmup_days: int = 2):
    """Dựng dataset 15m + bảng daily scores từ đặc tả theo NGÀY LOCAL.

    day_specs[k] mô tả ngày local thứ k+1 của kịch bản (Day 1 = ngày đầu accounting month):
      price     — close của mọi nến trong ngày (mặc định = ngày trước)
      low_dip   — nếu đặt, low của MỌI nến trong ngày = low_dip (để trigger zone)
      oscore    — OSCORE có hiệu lực TỪ 07:00 local của ngày này (đặt vào hàng daily hôm trước)
      return7   — Return7D đi cùng oscore đó (float hoặc None -> NaN)
      dq        — data quality, mặc định GOOD
      adr30     — mặc định 0.03

    Trả về (dataset, scores, start_ts, end_ts) cho run_engine:
      start = 00:00 local của Day 1; end = 00:00 local sau ngày cuối.
    Nến 15m: open = close nến trước (liên tục), high = max(open, close), low = min(open, close)
    hoặc low_dip nếu đặt. r24 của engine tính từ chính chuỗi close này.
    """
    first_local = pd.Timestamp(first_local_day)
    start_utc = first_local - pd.Timedelta(seconds=TZ)             # 00:00 local = 17:00 UTC hôm trước
    warmup_start = start_utc - pd.Timedelta(days=warmup_days)
    n_days = len(day_specs)
    end_utc = start_utc + pd.Timedelta(days=n_days)

    idx = pd.date_range(warmup_start, end_utc, freq="15min", tz="UTC", inclusive="left")
    n = len(idx)
    base_price = float(day_specs[0].get("price", 100.0))

    close = np.empty(n)
    low_override = np.full(n, np.nan)
    # warmup: giá phẳng bằng giá Day 1
    # Epoch-seconds KHÔNG phụ thuộc đơn vị datetime64 của pandas (ns hay us) — cùng idiom với
    # engine._epoch_seconds. KHÔNG dùng idx.asi8 // 10**9: trên pandas >= 3, date_range trả
    # datetime64[us] và asi8 là micro-giây, làm ánh xạ ngày sụp đổ âm thầm (finding F-E2-01).
    epoch_s = ((idx - pd.Timestamp(0, tz="UTC")) / pd.Timedelta(seconds=1)) \
        .to_numpy(float).astype("int64")
    day_of = (epoch_s + TZ) // int(DAY)
    day0 = int((start_utc.value // 10**9 + TZ) // DAY)             # ordinal local day của Day 1
    price_by_day = {}
    p = base_price
    for k, spec in enumerate(day_specs):
        p = float(spec.get("price", p))
        price_by_day[day0 + k] = p
    for i in range(n):
        d = int(day_of[i])
        close[i] = price_by_day.get(d, base_price)
    for k, spec in enumerate(day_specs):
        if "low_dip" in spec:
            mask = day_of == (day0 + k)
            low_override[mask] = float(spec["low_dip"])

    open_ = np.empty(n)
    open_[0] = close[0]
    open_[1:] = close[:-1]
    high = np.maximum(open_, close)
    low = np.minimum(open_, close)
    dip = ~np.isnan(low_override)
    low[dip] = np.minimum(low[dip], low_override[dip])
    volume = np.full(n, 1000.0)

    # Tự kiểm (chống tái diễn F-E2-01): mọi price/low_dip đã đặt phải THỰC SỰ xuất hiện
    # trong dataset — nếu ánh xạ ngày hỏng, spec giá sẽ bất động âm thầm và test chứng minh
    # ít hơn narrative của nó.
    specified_prices = {float(s["price"]) for s in day_specs if "price" in s}
    missing_p = specified_prices - set(np.unique(close).tolist())
    assert not missing_p, f"build_dataset: price đã đặt không xuất hiện trong close: {missing_p}"
    specified_dips = {float(s["low_dip"]) for s in day_specs if "low_dip" in s}
    missing_d = specified_dips - set(np.unique(low).tolist())
    assert not missing_d, f"build_dataset: low_dip đã đặt không xuất hiện trong low: {missing_d}"

    eth15 = pd.DataFrame({"open_time": idx, "open": open_, "high": high,
                          "low": low, "close": close, "volume": volume})
    dataset = {"ETHUSDT_15m": eth15}

    # Daily scores: hàng ngày UTC D kích hoạt tại D+1 00:00 UTC = 07:00 local D+1.
    # -> để oscore có hiệu lực từ 07:00 local Day k, đặt vào hàng UTC (Day k local) - 1 ngày.
    rows = {}
    prev = {"oscore": 20.0, "return7": 0.0, "dq": "GOOD", "adr30": 0.03}
    for k, spec in enumerate(day_specs):
        cur = {
            "oscore": spec.get("oscore", prev["oscore"]),
            "return7": spec.get("return7", prev["return7"]),
            "dq": spec.get("dq", prev["dq"]),
            "adr30": spec.get("adr30", prev["adr30"]),
        }
        # local Day k+1 bắt đầu tại start_utc + k ngày; hàng daily phải có day_end = 07:00 local
        # -> index (00:00 UTC) = ngày UTC chứa 07:00 local trừ 1 ngày + ... đơn giản:
        # day_end_ts = index + DAY; muốn day_end = (start_utc + k ngày + 7h) -> index = đó - DAY
        act = start_utc + pd.Timedelta(days=k, hours=7)
        rows[(act - pd.Timedelta(days=1)).normalize()] = cur
        prev = cur
    # warmup rows để engine có score ngay từ đầu (oscore thấp, GOOD)
    for w in range(1, warmup_days + 1):
        act = start_utc - pd.Timedelta(days=w - 1) + pd.Timedelta(hours=7)
        key = (act - pd.Timedelta(days=1)).normalize()
        rows.setdefault(key, {"oscore": 20.0, "return7": 0.0, "dq": "GOOD", "adr30": 0.03})

    sidx = pd.DatetimeIndex(sorted(rows))
    # close daily chỉ dùng cho bullish invalidation — khớp giá local ngày kích hoạt:
    # hàng index D kích hoạt tại D+1 00:00 UTC = 07:00 local (D+1)
    closes = [price_by_day.get(int((k.value // 10**9 + DAY + TZ) // DAY), base_price)
              for k in sorted(rows)]
    scores = pd.DataFrame({
        "oscore": [rows[k]["oscore"] for k in sorted(rows)],
        "data_quality": [rows[k]["dq"] for k in sorted(rows)],
        "return7": [np.nan if rows[k]["return7"] is None else rows[k]["return7"]
                    for k in sorted(rows)],
        "adr30": [rows[k]["adr30"] for k in sorted(rows)],
        "close": closes,
    }, index=sidx)

    return dataset, scores, pd.Timestamp(start_utc), pd.Timestamp(end_utc)


def run_case(day_specs, monkeypatch, strategy_cfg=None, exec_cfg=None, contribution=100.0,
             log_decisions=True, first_local_day: str = "2023-03-01"):
    """Chạy engine trên kịch bản day_specs với instrumentation. Trả (result, recorder)."""
    from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
    ds, scores, start, end = build_dataset(day_specs, first_local_day=first_local_day)
    rec = instrument(monkeypatch)
    res = engine_mod.run_engine(ds, scores, strategy_cfg or BASELINE_STRATEGY,
                                exec_cfg or GATE1_LOW_FRICTION, start, end,
                                contribution=contribution, log_decisions=log_decisions)
    return res, rec


def ledger_conservation_ok(pool: Pool, eps: float = 1e-6) -> bool:
    """Replay ledger của pool: sau mỗi entry, available/reserved/deployed khớp entry ghi lại
    và không âm; đồng thời TOTAL chỉ đổi qua CONTRIBUTION/OVERFLOW."""
    a = r = d = 0.0
    for e in pool.ledger:
        t, amt = e["entry_type"], e["amount"]
        if t in ("CONTRIBUTION", "OVERFLOW_IN"):
            a += amt
        elif t == "OVERFLOW_OUT":
            a -= amt
        elif t == "RESERVE":
            a -= amt
            r += amt
        elif t == "RELEASE":
            r -= amt
            a += amt
        elif t == "DEPLOY":
            # DEPLOY từ reserved (zone) hoặc từ available (base/month-end)
            if abs(e["reserved_after"] - (r - amt)) < eps:
                r -= amt
            else:
                a -= amt
            d += amt
        else:
            return False
        if a < -eps or r < -eps or d < -eps:
            return False
        if abs(e["available_after"] - a) > eps or abs(e["reserved_after"] - r) > eps \
                or abs(e["deployed_after"] - d) > eps:
            return False
    return abs(pool.available - a) < eps and abs(pool.reserved - r) < eps \
        and abs(pool.deployed - d) < eps
