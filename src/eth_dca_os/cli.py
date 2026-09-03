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

    el = sub.add_parser("export-live",
                        help="xuất live_seed.json cho app theo dõi trên web")
    el.add_argument("--history-days", type=int, default=420)
    el.add_argument("--parity-days", type=int, default=40)

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

    if args.cmd == "export-live":
        from .live_export import write_seed
        path = write_seed(out_dir, raw_dir, history_days=args.history_days,
                          parity_days=args.parity_days)
        size_kb = path.stat().st_size / 1024
        print(f"{path}  ({size_kb:.0f} KB)")
        print("Mở app theo dõi trên web và nạp file này để khởi tạo lịch sử giá.")
        return 0

    if args.cmd == "run":
        from .pipeline import Prepared, run_controls, run_gate1, run_gate2, run_gate3, run_verdict
        prep = Prepared(raw_dir)
        results = {}
        state_file = out_dir / "pipeline_state.json"
        if args.what in ("gate1", "all"):
            print("Gate 1 + OOS ...")
            g1 = run_gate1(prep, out_dir, dev_limit=args.dev_limit)
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
            ctl = run_controls(prep, out_dir, g1["_full_run_monthly_tranches"],
                               g1["_full_run_eth"], n_sims=n)
            results["controls"] = ctl
            print(f"F p95={ctl['random_timing']['p95']:.3f} "
                  f"G p95={ctl['random_anchor']['p95']:.3f} v2={ctl['v2_eth']:.3f}")
        if args.what == "all":
            verdict_payload = run_verdict(results["gate1"], results["gate2"], results["gate3"],
                                          results.get("controls"), out_dir, prep.dataset_hash,
                                          data_source=prep.data_source)
            results["verdict"] = verdict_payload
            print("=== VERDICT ===")
            print(json.dumps(verdict_payload["verdict"], indent=1, ensure_ascii=False))
            if "warning" in verdict_payload:
                print("!!", verdict_payload["warning"])
        # lưu state gọn để `verdict` đọc lại
        out_dir.mkdir(parents=True, exist_ok=True)
        light = {k: _strip(v) for k, v in results.items()}
        state_file.write_text(json.dumps(light, default=str, ensure_ascii=False))
        # report.json: payload đầy đủ, không strip — dùng cho viewer web / phân tích ngoài
        from .reporting import write_report
        report_path = write_report(out_dir, results, dataset_hash=prep.dataset_hash)
        print(f"\nReport đầy đủ: {report_path}")
        print("Mở trang viewer và kéo file này vào để xem kết quả dạng web.")
        return 0

    if args.cmd == "verdict":
        state_file = out_dir / "pipeline_state.json"
        if not state_file.exists():
            print("Chưa có kết quả — chạy `ethdca run all` trước.")
            return 2
        state = json.loads(state_file.read_text())
        if "verdict" in state:
            print(json.dumps(state["verdict"]["verdict"], indent=1, ensure_ascii=False))
            if "warning" in state["verdict"]:
                print("!!", state["verdict"]["warning"])
        else:
            print("pipeline_state.json chưa có verdict — chạy `ethdca run all` "
                  "(không chỉ `run gate1`/`gate2`/`gate3` riêng lẻ) để có verdict.")
            print(json.dumps(list(state.keys()), ensure_ascii=False))
        return 0

    return 1


_STRIP_KEYS = ("per_config", "windows", "run_record")


def _strip(d):
    if isinstance(d, dict):
        return {k: _strip(v) for k, v in d.items()
                if not (isinstance(k, str) and (k.startswith("_") or k in _STRIP_KEYS))}
    if isinstance(d, (list, tuple)):
        return f"[{len(d)} items]"
    return d


if __name__ == "__main__":
    sys.exit(main())
