# ETH DCA Operating System — V2.1.5 Research Prototype & Backtest Engine

Công cụ backtest-first cho chiến lược tích lũy ETH dài hạn, triển khai đúng bộ spec
**V2.1.5** tại [`docs/spec/`](docs/spec/) (source of truth — Master Index §2 quy định precedence).
Theo Implementation Plan §1: **không build app/dashboard trước khi có verdict cho phép** —
repo này là research prototype + backtest engine (Phase 0–9).

> **Bắt đầu ở đây:** [`docs/INDEX.md`](docs/INDEX.md) — điểm truy cập cho tài liệu, bản đồ code,
> lệnh chạy, ngưỡng gate và nguồn dữ liệu.

## Nguồn gốc

- Bộ spec V2.1.4 gốc do chủ dự án cung cấp (7 file .docx).
- V2.1.5 là corrective release đóng 7 lỗ hổng đặc tả F1–F7 (xem Master Index §4, biên bản
  [`docs/spec/RELEASE_CHECK_V2_1_5.md`](docs/spec/RELEASE_CHECK_V2_1_5.md)) — không đổi công
  thức chiến lược, ngưỡng gate, seed hay thuật toán manifest.
- Quy ước triển khai cho các điểm spec để ngỏ: [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md).

## Cài đặt

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest          # toàn bộ test suite (bám Backtest Spec §21)
```

## Sử dụng

```bash
# 1. Dữ liệu — official run BẮT BUỘC dùng dữ liệu Binance thật (chạy trên máy có mạng):
ethdca fetch                        # ETHUSDT/BTCUSDT 1D từ 2018 + ETHUSDT 15m từ 2019
# Dev/test không cần mạng:
ethdca synth                        # synthetic dataset deterministic (KHÔNG official)

# 2. Phase 0 — freeze manifest (Gate 2: 219 config seed 42; Gate 3: 114 config seed 43):
ethdca freeze                       # ghi results/manifests/*.json|csv + hash

# 3. Backtest:
ethdca run gate1                    # 9 window multi-anchor + OOS + diagnostics
ethdca run gate2                    # full 219 config (nặng — hàng giờ)
ethdca run gate3                    # full 114 config ma sát + shortfall attribution
ethdca run all                      # tất cả + random controls F/G + verdict tự động

# Dev smoke (KHÔNG phải official — kết quả gắn cờ official=false):
ethdca run all --dev-limit 3
```

Kết quả ghi vào `results/`: metrics JSON từng run + `backtest_runs.jsonl` (run record đầy đủ
strategy/execution/manifest/dataset hash + seed, theo Data Model §12 và Backtest §20).

## Kiến trúc

| Module | Nội dung | Spec |
|---|---|---|
| `config.py` | StrategyConfig / ExecutionConfig + SHA256 hash | Strategy §21, DM §2–3 |
| `data/` | fetch Binance, synthetic generator, gap report, lineage | BT §2, §18, DM §13 |
| `indicators.py` | High365, MA200, RSI14 Wilder, percentile, ADR30, ETHBTC | Strategy §1, §11 |
| `score.py` | 8 sub-factor, OSCORE, DEGRADED rule, unlock, ScoreMultiplier | Strategy §1–§4, §11, §13 |
| `diagnostics.py` | correlation, VIF, ablation, volume z-score, score buckets | Strategy §2 |
| `capital.py` | pool ledger A/R/D, 3 HWM mode, hysteresis, Opp cap overflow | Strategy §4–§10 |
| `ladders.py` | Smart/Opportunity/Crash ladder, lifecycle, invalidation | Strategy §11–§14, §18 |
| `regime.py` | CRASH entry/exit/RECOVERY + nhãn STRESSED [F1] | Strategy §17 |
| `engine.py` | vòng lặp 15m đúng 18 bước, Base/Month-End, cooldown, tie-break [F2] | BT §19 |
| `execution.py` | delay model, TTL, behavioral local-hour, fill fee/slippage | BT §5–§6 |
| `benchmarks.py` | A/B/C/D (+ C cycle [F4], D cap 6C) và controls F/G | BT §12 |
| `windows.py` | 9 window multi-anchor, coverage, PrimaryMedian, OOS | BT §3–§4, §8 |
| `manifests.py` | Gate 2 (1+18+200=219), Gate 3 (14+100=114), freeze + hash | BT §9.1, §10.1 |
| `metrics.py` | AE, NetEdge, shortfall + attribution, XIRR, concentration | BT §10.2, §11, §16 |
| `gates.py` / `failure_signals.py` / `verdict.py` | ngưỡng gate, FS-01..12, verdict cap | BT §7–§10, §17; IP §5–6 |
| `bootstrap.py` | block bootstrap 30/60/90 (DESCRIPTIVE) | BT §13 |
| `pipeline.py` / `cli.py` / `reporting.py` | orchestration, CLI, run records | IP §3 |

## Giới hạn hiện tại

- Môi trường phát triển của repo này bị chặn truy cập Binance, nên mọi verify trong repo dùng
  synthetic data. **Official verdict phải chạy trên máy của bạn** với `ethdca fetch` rồi
  `ethdca run all` (không `--dev-limit`).
- Gate 2 full (219 config × 9 window + OOS) là phép chạy nặng (~vài giờ trên một máy);
  Impl Plan §4 cho phép tối ưu thêm (cache, chạy song song theo config) mà không đổi kết quả.
- App MVP (dashboard dual-unit, treasury, P2P tracking — Product Spec) chỉ được build sau khi
  verdict = BUILD (Impl Plan §9).
