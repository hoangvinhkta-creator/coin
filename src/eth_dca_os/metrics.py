"""Gate metrics — Backtest §4.1, §7, §8, §10.2, §11, §16."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .benchmarks import run_benchmark_A
from .engine import run_engine
from .windows import (
    OOS_START,
    gate_windows,
    oos_months,
    pooled_median,
    primary_median,
    short_oos,
    anchor_set_medians,
)


def _ts(d) -> pd.Timestamp:
    return pd.Timestamp(d)


def run_window(dataset, scores, cfg, exec_cfg, start, end, contribution=100.0) -> dict:
    """Một window độc lập: engine V2 + benchmark A dưới cùng giả định ma sát."""
    res = run_engine(dataset, scores, cfg, exec_cfg, _ts(start), _ts(end), contribution)
    bench = run_benchmark_A(dataset, _ts(start), _ts(end), contribution, exec_cfg)
    ae = (res.eth_total / bench["eth"] * 100.0) if bench["eth"] > 0 else np.nan
    return {"eth_v2": res.eth_total, "eth_a": bench["eth"], "ae": ae,
            "result": res, "bench": bench}


def window_metrics(dataset, scores, cfg, exec_cfg, contribution=100.0) -> dict:
    """Chín window pre-OOS: AE từng window + AnchorSetMedian + PrimaryMedian + PooledMedian."""
    out = {}
    for w in gate_windows():
        end = pd.Timestamp(w.end) + pd.Timedelta(days=1)  # end inclusive -> exclusive
        r = run_window(dataset, scores, cfg, exec_cfg, w.start, end, contribution)
        out[w.window_id] = r
    aes = {k: v["ae"] for k, v in out.items()}
    return {
        "windows": out,
        "ae_by_window": aes,
        "anchor_set_medians": anchor_set_medians(aes),
        "primary_median": primary_median(aes),
        "pooled_median_descriptive": pooled_median(aes),
    }


def oos_metrics(dataset, scores, cfg, exec_cfg, oos_end, contribution=100.0) -> dict:
    end = pd.Timestamp(oos_end) + pd.Timedelta(days=1)
    r = run_window(dataset, scores, cfg, exec_cfg, pd.Timestamp(OOS_START), end, contribution)
    months = oos_months(pd.Timestamp(oos_end).date())
    return {"ae": r["ae"], "oos_months": months,
            "short_oos": short_oos(pd.Timestamp(oos_end).date()), "detail": r}


def net_edge(win_metrics: dict) -> dict:
    """NetEdgePct theo window = AE/100 - 1; PrimaryMedian NetEdge (Backtest §10.2)."""
    ne = {k: v / 100.0 - 1.0 for k, v in win_metrics["ae_by_window"].items()}
    return {"by_window": ne, "primary_median": primary_median(ne),
            "pooled_median_descriptive": pooled_median(ne)}


def implementation_shortfall_pp(gate1_primary_ae: float, gate3_primary_ae: float) -> float:
    return gate1_primary_ae - gate3_primary_ae


def shortfall_attribution(dataset, scores, cfg, gate1_cfg, gate3_cfg, contribution=100.0) -> dict:
    """Paired runs (Backtest §11): (a) chỉ user_delay; (b) chỉ funding; (c) chỉ slippage/fee."""
    from dataclasses import replace

    def pm(exec_cfg):
        return window_metrics(dataset, scores, cfg, exec_cfg, contribution)["primary_median"]

    base = pm(gate1_cfg)
    only_delay = replace(gate1_cfg, user_delay_seconds=gate3_cfg.user_delay_seconds,
                         config_name="attr_delay")
    only_funding = replace(gate1_cfg, funding_policy=gate3_cfg.funding_policy,
                           funding_delay_seconds=gate3_cfg.funding_delay_seconds,
                           config_name="attr_funding")
    only_friction = replace(gate1_cfg, spot_fee_rate=gate3_cfg.spot_fee_rate,
                            slippage_bps=gate3_cfg.slippage_bps, config_name="attr_friction")
    return {
        "gate1_primary_ae": base,
        "manual_delay_pp": base - pm(only_delay),
        "funding_pp": base - pm(only_funding),
        "fee_slippage_pp": base - pm(only_friction),
    }


def xirr(cashflows: list[tuple[float, float]], guess=0.1) -> float:
    """Money-weighted return từ [(epoch_seconds, amount)] (âm = nộp vốn, dương = giá trị cuối)."""
    if not cashflows:
        return np.nan
    t0 = cashflows[0][0]
    years = np.array([(t - t0) / (365.25 * 86400) for t, _ in cashflows])
    amounts = np.array([a for _, a in cashflows])
    rate = guess
    for _ in range(100):
        d = (1 + rate) ** years
        f = float((amounts / d).sum())
        fprime = float((-years * amounts / d / (1 + rate)).sum())
        if abs(fprime) < 1e-12:
            break
        step = f / fprime
        rate -= step
        if abs(step) < 1e-10:
            break
    return rate


def cash_ratio_stats(result) -> dict:
    """Average và max cash ratio từ cash_samples của engine (Backtest §16)."""
    if not result.cash_samples:
        return {"avg": np.nan, "max": np.nan}
    ratios = []
    for ts, cash, eth, price in result.cash_samples:
        port = cash + eth * price
        if port > 0:
            ratios.append(cash / port)
    return {"avg": float(np.mean(ratios)), "max": float(np.max(ratios))}


def opportunity_cap_hit_share(result) -> dict:
    """FS-02 (BT §17): tỷ lệ quan sát mà Opportunity Fund vừa CHẠM CAP vừa NẰM IM.

    Hai vế của câu spec được đo ĐỒNG THỜI trên cùng một mẫu ngày (xem CONVENTIONS #20):
    `at_cap` = `total >= cap` — dùng ĐÚNG phép so mà engine dùng để chặn contribution
               (`apply_monthly_contribution`), không phát minh phép so mới;
    `idle`   = còn vốn `available` chưa vào reservation nào và chưa deploy.

    GIỚI HẠN PHẢI BIẾT: `Pool.total = available + reserved + deployed` nên `total` KHÔNG
    giảm khi vốn được giải ngân. Vế `at_cap` vì thế **bão hoà** — đúng một lần quỹ đầy là
    nó TRUE mãi. Sức phân biệt của số đo nằm ở vế `idle`. Đây là ngữ nghĩa của `Pool` có
    sẵn (DM §6, WP-A7), WP-A5 KHÔNG đổi nó; giới hạn được ghi ra để người đọc số không
    hiểu nhầm, và các thống kê `idle_*` dưới đây tồn tại để WP-B1 tinh chỉnh ngưỡng mà
    KHÔNG phải chạy lại engine.

    Trả về dict để nơi gọi phân biệt được "đo ra 0.0" với "không đo được" — không bao giờ
    thay một số đo thiếu bằng giá trị mặc định (WP-A5 Escalation Trigger #2).
    """
    samples = getattr(result, "opp_cap_samples", None) or []
    if not samples:
        return {"share": None, "n_samples": 0, "n_hit": 0,
                "reason": "no_opp_cap_samples"}
    n = len(samples)
    n_hit = sum(1 for s in samples if s["at_cap"] and s["idle"])
    idle_ratios = [(s["available"] / s["cap"]) if s["cap"] > 0 else 0.0 for s in samples]
    return {
        "share": n_hit / n, "n_samples": n, "n_hit": n_hit, "reason": None,
        # Thống kê phụ trợ (KHÔNG phải input của FS-02): độ lớn của phần nằm im, để
        # WP-B1 chọn được ngưỡng vật chất mà không cần chạy lại engine.
        "at_cap_share": sum(1 for s in samples if s["at_cap"]) / n,
        "mean_idle_ratio": float(np.mean(idle_ratios)),
        "share_idle_ge_1pct_cap": sum(1 for r in idle_ratios if r >= 0.01) / n,
        "share_idle_ge_10pct_cap": sum(1 for r in idle_ratios if r >= 0.10) / n,
    }


def _regime_at(timeline: list, ts: float) -> str | None:
    """Nhãn regime đang hiệu lực tại `ts`, theo mốc đổi nhãn engine ghi lại (BT §15)."""
    if not timeline:
        return None
    lo, hi = 0, len(timeline) - 1
    if ts < timeline[0][0]:
        return timeline[0][1]          # trước mốc đầu tiên: nhãn khởi tạo của window
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if timeline[mid][0] <= ts:
            lo = mid
        else:
            hi = mid - 1
    return timeline[lo][1]


def regime_advantage(win_result: dict) -> dict:
    """Lợi thế ETH so với Benchmark A của MỘT window, phân rã theo nhãn regime (FS-12).

    `share` = phần lợi thế của regime đóng góp lớn nhất trên TỔNG KHỐI LỢI THẾ DƯƠNG
    (xem CONVENTIONS #20 cho lý do chọn mẫu số này thay vì lợi thế ròng). Khi không
    regime nào có lợi thế dương thì đại lượng không có nghĩa — trả `None` kèm lý do,
    KHÔNG quy về 0.0 (0.0 sẽ đọc thành "không tập trung", tức một khẳng định sai).
    """
    res = win_result["result"]
    timeline = getattr(res, "regime_timeline", None) or []
    if not timeline:
        return {"share": None, "by_regime": {}, "reason": "no_regime_timeline"}
    v2_r: dict[str, float] = {}
    for p in res.purchases:
        lab = p.get("regime") or _regime_at(timeline, p["ts"])
        v2_r[lab] = v2_r.get(lab, 0.0) + p["eth"]
    a_r: dict[str, float] = {}
    for p in win_result["bench"]["purchases"]:
        lab = _regime_at(timeline, p["ts"])
        a_r[lab] = a_r.get(lab, 0.0) + p["eth"]
    labels = sorted(set(v2_r) | set(a_r))
    adv = {r: v2_r.get(r, 0.0) - a_r.get(r, 0.0) for r in labels}
    return _advantage_share(adv)


def _advantage_share(adv: dict[str, float]) -> dict:
    """Tỷ lệ tập trung của lợi thế theo regime, dùng chung cho một window và cho gộp."""
    positive_mass = sum(a for a in adv.values() if a > 0)
    if positive_mass <= 0:
        return {"share": None, "by_regime": adv, "positive_mass": positive_mass,
                "net_advantage": sum(adv.values()),
                "reason": "no_positive_advantage_in_any_regime"}
    return {"share": max(adv.values()) / positive_mass, "by_regime": adv,
            "top_regime": max(adv, key=adv.get), "positive_mass": positive_mass,
            "net_advantage": sum(adv.values()), "reason": None}


def regime_advantage_pooled(windows: dict) -> dict:
    """FS-12 gộp: cộng lợi thế theo regime trên CẢ CHÍN window rồi mới lấy tỷ lệ.

    Vì sao gộp khối lợi thế thay vì gộp chín tỷ lệ bằng PrimaryMedian (CONVENTIONS #20):
    một window mà chiến lược không có lợi thế dương ở bất kỳ regime nào thì tỷ lệ tập
    trung KHÔNG xác định — gộp tỷ lệ sẽ làm cả đại lượng thành UNKNOWN chỉ vì một window,
    tức FS-12 lại UNKNOWN vì lý do KHÔNG phải thiếu đo lường, đúng thứ WP-A5 tồn tại để
    loại bỏ. FS-12 hỏi về chiến lược ("lợi thế tập trung vào một regime duy nhất"), không
    hỏi từng window, nên khối lợi thế là đơn vị gộp đúng. Thiên lệch do chín window chồng
    lấn tác động lên TỬ và MẪU cùng chiều nên chỉ còn bậc hai với một TỶ LỆ — khác với đại
    lượng MỨC (AE) mà BT §4.1 buộc dùng PrimaryMedian. Tỷ lệ từng window và PrimaryMedian
    của chúng vẫn được ghi lại để WP-B1 đổi input mà không phải chạy lại engine.
    """
    per_window = {w: regime_advantage(r) for w, r in windows.items()}
    pooled: dict[str, float] = {}
    for d in per_window.values():
        for r, a in d.get("by_regime", {}).items():
            pooled[r] = pooled.get(r, 0.0) + a
    out = _advantage_share(pooled)
    out["per_window"] = {w: {k: v for k, v in d.items() if k != "by_regime"}
                         for w, d in per_window.items()}
    out["per_window_share_primary_median"] = aggregate_over_windows(
        {w: d["share"] for w, d in per_window.items()})["value"]
    return out


def adjacent_config_flip(gate2_per_config: list) -> dict:
    """FS-06 (BT §17): config tham số KỀ NHAU có đảo ngược kết luận Gate 1 không.

    "Kề nhau" = config OFAT của manifest Gate 2: đổi ĐÚNG MỘT chiều tham số khỏi baseline
    (`manifests.generate_gate2_manifest`, tên `ofat_<dim>=<level>`). Config `lhs_*` đổi
    nhiều chiều cùng lúc nên KHÔNG kề nhau và không được tính (CONVENTIONS #20).

    "Đảo ngược kết luận" = `gate1.pass` khác baseline — cả hai chiều PASS→FAIL và
    FAIL→PASS, vì spec nói "đảo ngược", không nói riêng chiều xấu đi.
    """
    base = next((r for r in gate2_per_config
                 if not r["config_name"].startswith(("ofat_", "lhs_"))), None)
    if base is None:
        return {"flip": None, "reason": "baseline_config_missing", "n_adjacent": 0}
    adjacent = [r for r in gate2_per_config if r["config_name"].startswith("ofat_")]
    if not adjacent:
        return {"flip": None, "reason": "no_adjacent_config_in_manifest", "n_adjacent": 0}
    base_pass = base["gate1"]["pass"]
    flipped = [r["config_name"] for r in adjacent if r["gate1"]["pass"] != base_pass]
    return {"flip": bool(flipped), "baseline_pass": base_pass,
            "n_adjacent": len(adjacent), "n_flipped": len(flipped),
            "flipped_configs": flipped, "reason": None}


def aggregate_over_windows(per_window: dict[str, float | None]) -> dict:
    """Gộp một đại lượng đã tính TỪNG WINDOW về một số, theo PrimaryMedian (BT §4.1).

    Chín window pre-OOS chồng lấn nhau, nên trung bình trơn sẽ đếm trùng giai đoạn được
    nhiều window phủ. PrimaryMedian là phép gộp mà chính spec chọn để chống thiên vị đó,
    nên WP-A5 dùng lại đúng phép gộp ấy thay vì phát minh phép mới (CONVENTIONS #20).

    Thiếu bất kỳ window nào -> trả `None` kèm danh sách window thiếu. Không nội suy,
    không bỏ qua window để "còn tính được".
    """
    missing = [w for w, v in per_window.items()
               if v is None or (isinstance(v, float) and np.isnan(v))]
    if missing or not per_window:
        return {"value": None, "per_window": per_window,
                "reason": f"undefined_in_windows:{','.join(sorted(missing))}"
                          if missing else "no_window"}
    return {"value": primary_median(per_window), "per_window": per_window, "reason": None}


def concentration(win_result: dict) -> dict:
    """AE sau khi loại tháng/quý có lợi thế ETH tăng thêm lớn nhất (FS-03)."""
    res = win_result["result"]
    bench = win_result["bench"]
    v2_m: dict[str, float] = {}
    for p in res.purchases:
        mk = pd.Timestamp(p["ts"] + 7 * 3600, unit="s").strftime("%Y-%m")
        v2_m[mk] = v2_m.get(mk, 0.0) + p["eth"]
    a_m: dict[str, float] = {}
    for p in bench["purchases"]:
        a_m[p["month"]] = a_m.get(p["month"], 0.0) + p["eth"]
    months = sorted(set(v2_m) | set(a_m))
    adv = {m: v2_m.get(m, 0.0) - a_m.get(m, 0.0) for m in months}
    if not adv:
        return {"ae_ex_month": np.nan, "ae_ex_quarter": np.nan}
    m_star = max(adv, key=adv.get)
    q_of = lambda m: f"{m[:4]}-Q{(int(m[5:7]) - 1) // 3 + 1}"
    q_adv: dict[str, float] = {}
    for m, a in adv.items():
        q_adv[q_of(m)] = q_adv.get(q_of(m), 0.0) + a
    q_star = max(q_adv, key=q_adv.get)
    e_v2, e_a = win_result["eth_v2"], win_result["eth_a"]
    ex_m_v2 = e_v2 - v2_m.get(m_star, 0.0)
    ex_m_a = e_a - a_m.get(m_star, 0.0)
    q_months = [m for m in months if q_of(m) == q_star]
    ex_q_v2 = e_v2 - sum(v2_m.get(m, 0.0) for m in q_months)
    ex_q_a = e_a - sum(a_m.get(m, 0.0) for m in q_months)
    return {
        "best_month": m_star, "best_quarter": q_star,
        "ae_ex_month": ex_m_v2 / ex_m_a * 100.0 if ex_m_a > 0 else np.nan,
        "ae_ex_quarter": ex_q_v2 / ex_q_a * 100.0 if ex_q_a > 0 else np.nan,
    }
