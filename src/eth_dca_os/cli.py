"""CLI `ethdca` — research prototype & backtest theo Impl Plan §3."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(prog="ethdca",
                                description="ETH DCA OS V2.1.5 — backtest engine")
    p.add_argument("--raw-dir", default="data/raw")
    p.add_argument("--out-dir", default="results")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="tải Binance OHLCV (chạy trên máy có mạng Binance)")
    f.add_argument("--start", default="2018-01-01")
    f.add_argument("--end", default=None)

    s = sub.add_parser("synth", help="sinh synthetic dataset (dev/test, KHÔNG official)")
    s.add_argument("--start", default="2018-01-01")
    s.add_argument("--end", default="2026-06-30")

    sub.add_parser("freeze", help="Phase 0: sinh + đóng băng manifest Gate 2/3 + hash")

    r = sub.add_parser("run", help="chạy backtest")
    r.add_argument("what", choices=["gate1", "gate2", "gate3", "controls", "all"])
    r.add_argument("--dev-limit", type=int, default=None,
                   help="CHỈ dev/smoke: giới hạn số config Gate 2/3 (official = full)")

    sub.add_parser("verdict", help="tổng hợp verdict từ kết quả gần nhất trong --out-dir")

    args = p.parse_args(argv)
    raw_dir, out_dir = Path(args.raw_dir), Path(args.out_dir)

    if args.cmd == "fetch":
        from .data.fetch import fetch_all
        meta = fetch_all(raw_dir, start=args.start, end=args.end)
        print(json.dumps(meta, indent=1))
        return 0

    if args.cmd == "synth":
        from .data.synth import generate
        meta = generate(raw_dir, start=args.start, end=args.end)
        print(json.dumps(meta, indent=1))
        print("LƯU Ý: synthetic data chỉ dùng dev/test — official run cần `ethdca fetch`.")
        return 0

    if args.cmd == "freeze":
        from .manifests import freeze_manifests
        meta = freeze_manifests(out_dir / "manifests")
        print(json.dumps(meta, indent=1, ensure_ascii=False, default=str))
        return 0

    if args.cmd == "run":
        from .pipeline import Prepared, run_controls, run_gate1, run_gate2, run_gate3, run_verdict
        prep = Prepared(raw_dir)
        results = {}
        state_file = out_dir / "pipeline_state.json"
        if args.what in ("gate1", "all"):
            print("Gate 1 + OOS ...")
            g1 = run_gate1(prep, out_dir)
            results["gate1"] = g1
            from .reporting import print_gate1_report
            print(print_gate1_report(g1))
        if args.what in ("gate2", "all"):
            print(f"Gate 2 ({'FULL 219' if not args.dev_limit else f'dev-limit {args.dev_limit}'}) ...")
            g2 = run_gate2(prep, out_dir, limit=args.dev_limit)
            results["gate2"] = g2
            print(f"Gate2 PreOOS pass share: {g2['gate2']['pre_oos_pass_share']:.2%} "
                  f"-> {'PASS' if g2['gate2']['pass'] else 'FAIL'}")
        if args.what in ("gate3", "all"):
            print(f"Gate 3 ({'FULL 114' if not args.dev_limit else f'dev-limit {args.dev_limit}'}) ...")
            g3 = run_gate3(prep, out_dir, limit=args.dev_limit)
            results["gate3"] = g3
            print(f"Gate3 realistic NetEdge PM: "
                  f"{g3['realistic']['net_edge_primary_median']:+.4f} "
                  f"-> {'PASS' if g3['gate3']['pass'] else 'FAIL'}")
        if args.what in ("controls", "all"):
            g1 = results.get("gate1")
            if g1 is None:
                print("controls cần gate1 chạy trước trong cùng lần gọi (dùng `run all`).")
                return 2
            print("Random controls F/G ...")
            n = 200 if args.dev_limit else 1000
            ctl = run_controls(prep, out_dir, g1["_full_run_monthly_deployments"],
                               g1["_full_run_eth"], n_sims=n)
            results["controls"] = ctl
            print(f"F p95={ctl['random_timing']['p95']:.3f} "
                  f"G p95={ctl['random_anchor']['p95']:.3f} v2={ctl['v2_eth']:.3f}")
        if args.what == "all":
            v = run_verdict(results["gate1"], results["gate2"], results["gate3"],
                            results.get("controls"), out_dir, prep.dataset_hash)
            print("=== VERDICT ===")
            print(json.dumps(v["verdict"], indent=1, ensure_ascii=False))
            if "warning" in v:
                print("!!", v["warning"])
        # lưu state gọn để `verdict` đọc lại
        out_dir.mkdir(parents=True, exist_ok=True)
        light = {k: _strip(v) for k, v in results.items()}
        state_file.write_text(json.dumps(light, default=str, ensure_ascii=False))
        return 0

    if args.cmd == "verdict":
        state_file = out_dir / "pipeline_state.json"
        if not state_file.exists():
            print("Chưa có kết quả — chạy `ethdca run all` trước.")
            return 2
        print(state_file.read_text()[:2000])
        return 0

    return 1


def _strip(d):
    if isinstance(d, dict):
        return {k: _strip(v) for k, v in d.items()
                if not k.startswith("_") and k not in ("per_config", "windows", "run_record")}
    if isinstance(d, (list, tuple)):
        return f"[{len(d)} items]"
    return d


if __name__ == "__main__":
    sys.exit(main())
