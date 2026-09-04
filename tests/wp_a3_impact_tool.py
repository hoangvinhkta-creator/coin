"""Công cụ đo impact cho CHECK-A3-08 (WP-A3) — KHÔNG phải test tự động.

Chạy engine trên dataset tổng hợp cố định (data.synth.generate, SYNTH_SEED mặc định)
với config baseline + GATE1_LOW_FRICTION và xuất metric JSON, để so sánh BEFORE/AFTER
một remediation trên CÙNG dataset/cửa sổ (tái lập được từ trạng thái repo — BT §20).

Usage:
    python tests/wp_a3_impact_tool.py TAG [--out DIR] [--raw DIR] [--src SRC_DIR]
                                          [--start 2019-01-01] [--end 2026-06-01]

  TAG    nhãn của lần đo (ví dụ BEFORE / AFTER) — dùng trong tên file output.
  --out  thư mục ghi wp_a3_impact_<TAG>.json và wp_a3_purchases_<TAG>.json (mặc định cwd).
  --raw  thư mục dataset synth; sinh mới nếu chưa có (mặc định <out>/impact_raw).
  --src  ép import eth_dca_os từ đúng thư mục src này (dùng khi đo BEFORE trên một
         git worktree ở commit cũ, vì bản cài editable trỏ về repo chính; tool sẽ gỡ
         editable finder khỏi sys.meta_path và assert module thật sự nạp từ --src).

Quy trình tái lập bảng CHECK-A3-08 của S003:
    git worktree add /tmp/wt_before 5645a74
    python tests/wp_a3_impact_tool.py BEFORE --out /tmp/imp --src /tmp/wt_before/src
    python tests/wp_a3_impact_tool.py AFTER  --out /tmp/imp
    # rồi diff hai file JSON (cùng --raw để dùng đúng một dataset)
"""
import argparse
import json
import sys
from pathlib import Path


def _force_src(src_dir: str):
    src = Path(src_dir).resolve()
    # gỡ editable finder (PEP 660) để sys.path quyết định nguồn import
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
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end", default="2026-06-01")
    args = ap.parse_args()

    if args.src:
        _force_src(args.src)

    import pandas as pd

    import eth_dca_os
    from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
    from eth_dca_os.data.dataset import load_dataset
    from eth_dca_os.data.synth import generate
    from eth_dca_os.engine import run_engine
    from eth_dca_os.indicators import compute_daily_indicators
    from eth_dca_os.score import compute_scores

    sys.path.insert(0, str(Path(__file__).parent))
    from wp_a3_harness import instrument

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = Path(args.raw) if args.raw else out / "impact_raw"

    class MP:
        def __init__(self):
            self._undo = []

        def setattr(self, obj, name, val):
            self._undo.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

        def undo(self):
            for obj, name, val in reversed(self._undo):
                setattr(obj, name, val)
            self._undo.clear()

    if not (raw / "ETHUSDT_15m.parquet").exists():
        print("generating synth dataset (SYNTH_SEED mặc định)...")
        generate(raw)
    ds = load_dataset(raw)
    ind = compute_daily_indicators(ds["ETHUSDT_1d"], ds["BTCUSDT_1d"])
    scores = pd.concat([ind, compute_scores(ind)], axis=1)
    scores = scores.loc[:, ~scores.columns.duplicated()]

    mp = MP()
    try:
        rec = instrument(mp)
        res = run_engine(ds, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                         pd.Timestamp(args.start), pd.Timestamp(args.end))
    finally:
        mp.undo()

    pools = {p.name: p for p in rec.pools}
    releases, release_total = {}, {}
    for p in rec.pools:
        for e in p.ledger:
            if e["entry_type"] == "RELEASE":
                key = e["reason_code"]
                releases[key] = releases.get(key, 0) + 1
                release_total[key] = release_total.get(key, 0.0) + e["amount"]

    label_trans, state_trans = {}, {}
    for _, a, b in rec.transitions:
        label_trans[f"{a}->{b}"] = label_trans.get(f"{a}->{b}", 0) + 1
    for _, a, b in rec.state_transitions:
        state_trans[f"{a}->{b}"] = state_trans.get(f"{a}->{b}", 0) + 1

    crash = rec.crash_ladders()
    cash_ratio, cum = [], 0.0
    contrib_iter = iter(res.contributions)
    nxt = next(contrib_iter, None)
    for ts, cash, eth, price in res.cash_samples:
        while nxt is not None and nxt[0] <= ts:
            cum += nxt[1]
            nxt = next(contrib_iter, None)
        if cum > 0:
            cash_ratio.append(cash / cum)

    out_doc = {
        "tag": args.tag,
        "code_path": str(Path(eth_dca_os.__file__).resolve()),
        "window": [args.start, args.end],
        "eth_total": res.eth_total,
        "contributed_total": res.contributed_total,
        "purchases_count": len(res.purchases),
        "purchases_by_source": {
            s: {"n": sum(1 for p in res.purchases if p["source"] == s),
                "nominal": sum(p["nominal"] for p in res.purchases if p["source"] == s)}
            for s in ("BASE", "SMART", "OPPORTUNITY", "CRASH")
        },
        "counters": res.counters,
        "label_transitions": label_trans,
        "state_transitions": state_trans,
        "n_regime_label_transitions": len(rec.transitions),
        "crash_ladders_created": len(crash),
        "crash_ladder_status_counts": {
            s: sum(1 for l in crash if l.status == s)
            for s in sorted({l.status for l in crash})},
        "crash_snapshots_sum": sum(l.eligible_capital_vnd for l in crash),
        "smart_ladders_created": sum(1 for l in rec.ladders if l.type == "SMART"),
        "opp_ladders_created": sum(1 for l in rec.ladders if l.type == "OPPORTUNITY"),
        "releases_count_by_reason": releases,
        "releases_total_by_reason": {k: round(v, 6) for k, v in release_total.items()},
        "final_pools": {
            name: {"available": round(p.available, 6), "reserved": round(p.reserved, 6),
                   "deployed": round(p.deployed, 6), "total": round(p.total, 6)}
            for name, p in pools.items()},
        "avg_cash_ratio_vs_contributed":
            (sum(cash_ratio) / len(cash_ratio)) if cash_ratio else None,
        "daily_limit_blocks": sum(1 for d in res.decision_log
                                  if d["reason_code"] == "DAILY_LIMIT_BLOCK"),
        "stuck_crash_reserve_at_end": round(sum(
            z.reserved_vnd for l in crash for z in l.zones
            if z.status in ("ACTIVE", "SUSPENDED", "TRIGGERED", "ACTION_PENDING")), 6),
    }
    path = out / f"wp_a3_impact_{args.tag}.json"
    path.write_text(json.dumps(out_doc, indent=2, ensure_ascii=False))
    (out / f"wp_a3_purchases_{args.tag}.json").write_text(json.dumps(
        [{k: p[k] for k in ("ts", "source", "nominal", "reason")} for p in res.purchases]))
    print(json.dumps(out_doc, indent=2, ensure_ascii=False))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
