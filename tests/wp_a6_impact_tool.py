"""Công cụ đo impact cho CHECK-A6-03 / CHECK-A6-07 (WP-A6) — KHÔNG phải test tự động.

Chạy engine trên dataset tổng hợp cố định (data.synth.generate, SYNTH_SEED mặc định) với
config baseline và MỘT execution config đã commit, xuất metric JSON để so sánh giữa các
biến thể THỨ TỰ XỬ LÝ (engine hiện tại vs. từng sai lệch được sửa) trên CÙNG dataset,
cửa sổ và seed — tái lập được từ trạng thái repo (BT §20). Cùng cách dùng `--src` như
`tests/wp_a3_impact_tool.py`.

Usage:
    python tests/wp_a6_impact_tool.py TAG [--out DIR] [--raw DIR] [--src SRC_DIR]
                                          [--exec gate1|gate3] [--start ...] [--end ...]
                                          [--drop-daily YYYY-MM-DD]

  --drop-daily  xoá MỘT hàng daily ETH/BTC (tạo cửa sổ INVALID ~31 ngày theo adr30) để đo
                H-15 (zone TRIGGERED trong chu kỳ INVALID) trên dataset có gap thật.

Ngoài metric tổng, tool đếm các đại lượng chỉ có ý nghĩa với thứ tự xử lý:
  same_candle_trigger_after_create   zone TRIGGERED ngay trong nến tạo ladder
  same_candle_fill_and_new_trigger   nến vừa có fill (bước 16) vừa có trigger mới (bước 13)
  invalid_cycle_triggers             zone TRIGGERED trong nến dữ liệu INVALID
  invalid_cycle_triggers_actioned    ... rồi thành ACTION_PENDING ở chu kỳ hợp lệ sau đó
"""
import argparse
import json
import sys
from pathlib import Path


def _force_src(src_dir: str):
    src = Path(src_dir).resolve()
    sys.meta_path = [f for f in sys.meta_path if "editable" not in type(f).__module__.lower()
                     and "editable" not in repr(f).lower()]
    sys.path.insert(0, str(src))
    for m in [m for m in sys.modules if m == "eth_dca_os" or m.startswith("eth_dca_os.")]:
        del sys.modules[m]
    import eth_dca_os
    got = Path(eth_dca_os.__file__).resolve()
    assert str(got).startswith(str(src)), f"import eth_dca_os từ {got}, kỳ vọng dưới {src}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--out", default=".")
    ap.add_argument("--raw", default=None)
    ap.add_argument("--src", default=None)
    ap.add_argument("--exec", default="gate1", choices=["gate1", "gate3"])
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end", default="2026-06-01")
    ap.add_argument("--drop-daily", default=None)
    args = ap.parse_args()

    if args.src:
        _force_src(args.src)

    import numpy as np
    import pandas as pd

    import eth_dca_os
    from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
    from eth_dca_os.data.dataset import load_dataset
    from eth_dca_os.data.synth import generate
    from eth_dca_os.engine import run_engine
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores

    sys.path.insert(0, str(Path(__file__).parent))
    import wp_a6_order_harness as H

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = Path(args.raw) if args.raw else out / "impact_raw"
    if not (raw / "ETHUSDT_15m.parquet").exists():
        print("generating synth dataset (SYNTH_SEED mặc định)...")
        generate(raw)
    ds = load_dataset(raw)
    if args.drop_daily:
        d0 = pd.Timestamp(args.drop_daily, tz="UTC")
        for k in ("ETHUSDT_1d", "BTCUSDT_1d"):
            df = ds[k]
            ds[k] = df[df["open_time"] != d0].reset_index(drop=True)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = pd.concat([ind, compute_scores(ind)], axis=1)
    scores = scores.loc[:, ~scores.columns.duplicated()]
    exec_cfg = GATE1_LOW_FRICTION if args.exec == "gate1" else GATE3_REALISTIC

    mp = H.SimpleMonkeyPatch()
    try:
        tr = H.instrument(mp)
        res = run_engine(ds, scores, BASELINE_STRATEGY, exec_cfg,
                         pd.Timestamp(args.start), pd.Timestamp(args.end), log_decisions=True)
    finally:
        mp.undo()

    # ---- đại lượng theo thứ tự xử lý
    by_c = tr.by_candle()
    created_at = {}
    for ev in tr.events:
        if ev.kind == "LADDER_CREATED":
            created_at[ev.detail["ladder"]] = ev.ts
    same_create = 0
    same_fill_trig = 0
    for cidx, evs in by_c.items():
        trig = [e for e in evs if e.kind == "ZONE" and e.detail["new"] == "TRIGGERED"]
        for e in trig:
            if created_at.get(e.detail["ladder"]) == e.ts:
                same_create += 1
        if trig and any(e.kind == "FILL" for e in evs):
            same_fill_trig += 1

    # INVALID theo nến: score hiệu lực tại nến = ngày daily gần nhất đã đóng
    day_ts = ((pd.DatetimeIndex(scores.index) - pd.Timestamp(0, tz=scores.index.tz))
              / pd.Timedelta(seconds=1)).to_numpy(float)
    day_end = day_ts + H.DAY
    dq = scores["data_quality"].to_numpy(object)

    def dq_at(ts):
        j = int(np.searchsorted(day_end, ts, side="right")) - 1
        return dq[j] if j >= 0 else "INVALID"

    invalid_trig, invalid_trig_actioned, invalid_actions = 0, 0, []
    trig_ts = {}
    for ev in tr.events:
        if ev.kind != "ZONE":
            continue
        zid = ev.detail["zone"]
        if ev.detail["new"] == "TRIGGERED":
            trig_ts[zid] = (ev.ts, dq_at(ev.ts))
            if dq_at(ev.ts) == "INVALID":
                invalid_trig += 1
        elif ev.detail["new"] == "ACTION_PENDING" and zid in trig_ts:
            t0, q0 = trig_ts[zid]
            if q0 == "INVALID":
                invalid_trig_actioned += 1
                z = tr.zone_by_id(zid)
                invalid_actions.append({"zone": zid, "trigger_ts": H.local_str(t0),
                                        "action_ts": H.local_str(ev.ts),
                                        "delay_days": round((ev.ts - t0) / H.DAY, 2),
                                        "target_price": z.target_price if z else None})

    viol = H.order_violations(tr, H.letter_map)
    sig = {f"{a} => {b}": n for (a, b), n in H.violation_signature(viol).items()}

    purchases = res.purchases
    by_src = {
        s: {"n": sum(1 for p in purchases if p["source"] == s),
            "nominal": round(sum(p["nominal"] for p in purchases if p["source"] == s), 6),
            "eth": round(sum(p["eth"] for p in purchases if p["source"] == s), 9)}
        for s in ("BASE", "SMART", "OPPORTUNITY", "CRASH")
    }
    by_reason = {}
    for p in purchases:
        r = p["reason"].rsplit("_", 1)[0] if p["reason"].startswith(("SMART_ZONE", "OPPORTUNITY_ZONE", "CRASH_ZONE")) else p["reason"]
        by_reason[r] = by_reason.get(r, 0) + 1
    zone_status = {}
    for lad in tr.ladders:
        for z in lad.zones:
            key = f"{lad.type}:{z.status}"
            zone_status[key] = zone_status.get(key, 0) + 1
    pools = {p.name: p for p in tr.pools}
    ndays = (pd.Timestamp(args.end) - pd.Timestamp(args.start)).days
    out_doc = {
        "tag": args.tag,
        "code_path": str(Path(eth_dca_os.__file__).resolve()),
        "exec_config": exec_cfg.config_name,
        "window": [args.start, args.end],
        "drop_daily": args.drop_daily,
        "eth_total": res.eth_total,
        "contributed_total": res.contributed_total,
        "purchases_count": len(purchases),
        "purchases_by_source": by_src,
        "purchases_by_reason": dict(sorted(by_reason.items())),
        "counters": res.counters,
        "ladders_created": {t: sum(1 for l in tr.ladders if l.type == t)
                            for t in ("SMART", "OPPORTUNITY", "CRASH")},
        "zone_status_final": dict(sorted(zone_status.items())),
        "final_pools": {
            name: {"available": round(p.available, 6), "reserved": round(p.reserved, 6),
                   "deployed": round(p.deployed, 6), "total": round(p.total, 6)}
            for name, p in pools.items()},
        "invalid_candles_share": round(float(np.mean([dq_at(e.ts) == "INVALID"
                                                      for e in tr.events if e.kind == "CLOCK"])), 6),
        "order_metrics": {
            "same_candle_trigger_after_create": same_create,
            "same_candle_fill_and_new_trigger": same_fill_trig,
            "invalid_cycle_triggers": invalid_trig,
            "invalid_cycle_triggers_actioned": invalid_trig_actioned,
            "invalid_cycle_actions": invalid_actions,
            "letter_violations_total": len(viol),
            "letter_violations_signature": sig,
        },
        "n_days": ndays,
    }
    path = out / f"wp_a6_impact_{args.tag}.json"
    path.write_text(json.dumps(out_doc, indent=2, ensure_ascii=False, default=float))
    (out / f"wp_a6_purchases_{args.tag}.json").write_text(json.dumps(
        [{k: p[k] for k in ("ts", "source", "nominal", "reason", "price", "eth")}
         for p in purchases], default=float))
    print(json.dumps({k: v for k, v in out_doc.items() if k != "order_metrics"},
                     indent=1, ensure_ascii=False, default=float))
    print(json.dumps(out_doc["order_metrics"], indent=1, ensure_ascii=False, default=float))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
