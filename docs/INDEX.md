# Index — ETH DCA Operating System V2.1.5

Điểm truy cập cho toàn bộ dự án. Ba trang web đi kèm:

- **Index** (tài liệu, code map, lệnh chạy, ngưỡng): <https://claude.ai/code/artifact/b0bae7ec-0068-4811-b89a-9ee5fb7893de>
- **Xem kết quả backtest**: <https://claude.ai/code/artifact/7fa3c209-ab5c-4ce3-81e2-a1a7277b5305>
  — kéo `results/report.json` vào trang để xem gate, failure signal và verdict dạng biểu đồ.
- **App theo dõi**: <https://claude.ai/code/artifact/ee1cc5bf-b66c-438f-9aee-ca229b0e1d95>
  — nhập giá và giao dịch thật, app tính OSCORE và theo dõi vốn/ladder/danh mục.
  Nguồn ở [`webapp/`](../webapp/README.md); nạp seed bằng `ethdca export-live`.
  Lưu ý: app nằm sau cổng verdict của Impl Plan §9 — xem README của webapp.

## 1. Tài liệu, xếp theo precedence

Khi hai tài liệu mâu thuẫn, áp dụng theo thứ tự này (Master Index §2). Số thứ tự là
precedence, không phải thứ tự đọc.

| # | Tài liệu | Nội dung |
|---|---|---|
| 1 | [03_BACKTEST_SPEC](spec/03_BACKTEST_SPEC_V2_1_5.md) | Chuẩn mô phỏng, 9 cửa sổ gate, manifest, delay model, benchmark, failure signals, processing order 18 bước, test suite |
| 2 | [02_STRATEGY_SPEC](spec/02_STRATEGY_SPEC_V2_1_5.md) | Opportunity Score, capital allocation, ladder, regime, limits, lifecycle, enum, baseline config |
| 3 | [04_DATA_MODEL](spec/04_DATA_MODEL_V2_1_5.md) | Schema config, ledger, zone, trade, run metadata, invariants |
| 4 | [01_PRODUCT_SPEC](spec/01_PRODUCT_SPEC_V2_1_5.md) | Workflow thủ công, treasury, dashboard dual-unit, P2P, non-goals |
| 5 | [05_IMPLEMENTATION_PLAN](spec/05_IMPLEMENTATION_PLAN_V2_1_5.md) | Phase 0 freeze, các phase, compute discipline, stopping rules, thủ tục phát hành |
| 6 | [06_SECTION_INVENTORY](spec/06_SECTION_INVENTORY_V2_1_5.md) | Danh mục đầy đủ mọi mục bắt buộc + XC-1…XC-9 |
| — | [00_MASTER_INDEX](spec/00_MASTER_INDEX_V2_1_5.md) | Precedence, trạng thái version, changelog F1–F7, freeze rule. Đọc đầu tiên |
| — | [RELEASE_CHECK](spec/RELEASE_CHECK_V2_1_5.md) | Biên bản chạy đủ sáu bước Impl Plan §8 cho V2.1.5 |

Tài liệu bổ trợ (không thuộc spec pack, nhưng bắt buộc đọc trước khi sửa code):

- [CONVENTIONS.md](CONVENTIONS.md) — quy ước cho những điểm spec cố ý để ngỏ
- [DATA_SOURCES.md](DATA_SOURCES.md) — nguồn dữ liệu, kênh API, giới hạn rate

## 2. Sửa đổi V2.1.4 → V2.1.5

Bảy lỗ hổng đặc tả đã đóng. Không mục nào đổi công thức, ngưỡng gate, seed hay ngày split —
chi tiết ở Master Index §4.

| ID | Nội dung | Vị trí |
|---|---|---|
| F1 | STRESSED là nhãn dẫn xuất chỉ dùng reporting | Strategy §17.3 |
| F2 | Tie-break khi nhiều zone cùng trigger | Strategy §15.1 |
| F3 | Base tranche rơi vào gap dữ liệu | Strategy §9 |
| F4 | Ngữ nghĩa chu kỳ của Benchmark C | Backtest §12 |
| F5 | Snapshot vốn đủ điều kiện của Crash ladder | Strategy §14 |
| F6 | VND accounting trong backtest, gom về một mục | Backtest §2.1 |
| F7 | Ngoại lệ ba field metadata giữa §21 và schema | Strategy §21 · DM §2 |

## 3. Bản đồ code

Mọi module dưới `src/eth_dca_os/`; cột cuối là điều khoản nó thực thi.

| Module | Nội dung | Spec |
|---|---|---|
| `config.py` | StrategyConfig / ExecutionConfig, SHA256 hash | ST §21 · DM §2–3 |
| `data/fetch.py` | Bulk archive + REST, verify checksum | BT §2 |
| `data/synth.py` | Dataset tổng hợp deterministic (dev/test) | — |
| `data/dataset.py` | Gap report, dataset_hash, lineage | BT §18 · DM §13 |
| `indicators.py` | High365, MA200, RSI14 Wilder, percentile, ADR30, ETHBTC | ST §1 · §11 |
| `score.py` | 8 sub-factor, OSCORE, DEGRADED, unlock, ScoreMultiplier | ST §1–4 · §11 · §13 |
| `diagnostics.py` | Correlation, VIF, ablation, volume z-score, phân bố score | ST §2 |
| `capital.py` | Pool ledger A/R/D, ba mode HWM, hysteresis, cap & overflow | ST §4–10 |
| `ladders.py` | Smart / Opportunity / Crash ladder, lifecycle, invalidation | ST §11–14 · §18 |
| `regime.py` | CRASH entry/exit, RECOVERY, nhãn STRESSED | ST §17 |
| `engine.py` | Vòng lặp 15m đúng 18 bước, Base, Month-End, cooldown | BT §19 |
| `execution.py` | Delay model, TTL, MISSED, behavioral, fee & slippage | BT §5–6 |
| `benchmarks.py` | A/B/C/D và random control F/G | BT §12 |
| `windows.py` | 9 window multi-anchor, coverage, PrimaryMedian, OOS | BT §3–4 · §8 |
| `manifests.py` | Sinh và đóng băng manifest Gate 2 / Gate 3 kèm hash | BT §9.1 · §10.1 |
| `metrics.py` | AE, NetEdge, shortfall + attribution, XIRR, concentration | BT §10.2 · §11 · §16 |
| `gates.py` | Ngưỡng cứng Gate 1 / OOS / Gate 2 / Gate 3 | BT §7–10 |
| `failure_signals.py` | FS-01 … FS-12 | BT §17 |
| `verdict.py` | Verdict tự động + failure-signal cap | IM §5–6 |
| `bootstrap.py` | Block bootstrap 30/60/90 ngày (DESCRIPTIVE) | BT §13 |
| `pipeline.py` · `cli.py` · `reporting.py` | Orchestration, CLI, run record | IM §3 · BT §20 |

## 4. Cách chạy

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && pytest

ethdca fetch        # 1 — dữ liệu Binance thật (bắt buộc cho official run)
ethdca freeze       # 2 — Phase 0: đóng băng manifest + hash, TRƯỚC mọi gate
ethdca run all      # 3 — Gate 1/2/3 + controls + verdict
ethdca verdict      # 4 — đọc lại kết quả đã lưu
ethdca export-live  # seed cho app theo dõi trên web
```

`--dev-limit N` chạy nhanh với vài config để kiểm cơ chế; kết quả tự gắn cờ `official: false`.
`ethdca synth` sinh dataset tổng hợp khi không có mạng Binance — chỉ dev/test.

Kết quả ghi ở `results/`:

| File | Dùng để |
|---|---|
| `report.json` | Payload đầy đủ — **kéo vào trang xem kết quả** ở đầu tài liệu này |
| `backtest_runs.jsonl` | Run record: đủ hash config/manifest/dataset và seed để tái lập |
| `<run_id>_metrics.json` | Metrics chi tiết từng run |
| `pipeline_state.json` | State rút gọn cho lệnh `ethdca verdict` đọc lại |

## 5. Ngưỡng cứng

| Gate | Điều kiện | PASS | STRONG |
|---|---|---|---|
| Gate 1 | PrimaryMedian AE | ≥ 102% | ≥ 105% |
| Gate 1 | Tỷ lệ window có AE ≥ 100% | ≥ 6/9 | ≥ 7/9 |
| Gate 1 | Window xấu nhất, delta | ≥ −5 pp | ≥ −3 pp |
| Gate 1 | Không anchor set nào toàn bộ dưới 100% | bắt buộc | bắt buộc |
| OOS | AE, kèm OOS_Months và cờ SHORT_OOS | ≥ 100% | ≥ 102% |
| Gate 2 | Pre-OOS pass share (ngưỡng cứng duy nhất) | ≥ 75% | ≥ 80% |
| Gate 2 | OOS pass share — báo cáo riêng, < 50% bật FS-10 | — | — |
| Gate 3 | PrimaryMedian NetEdge, baseline thực tế | > 0 | ≥ +1,5% |
| Gate 3 | OOS AE, baseline thực tế | ≥ 100% | ≥ 102% |
| Gate 3 | Tỷ lệ config có NetEdge dương | ≥ 60% | ≥ 70% |

Verdict: **BUILD** chỉ khi cả ba gate PASS và không FS nào TRUE. Có FS bật →
**BUILD WITH MODIFICATIONS** (mở V2.2, không vá tại chỗ). Gate 2/3 trượt → **INCONCLUSIVE**.
Gate 1 hoặc OOS trượt → **DO NOT BUILD**.

## 6. Việc còn lại

1. **Official run trên dữ liệu Binance thật** — môi trường build bị chặn egress tới Binance nên
   mọi kiểm chứng trong repo chạy trên dữ liệu tổng hợp; đủ để chứng minh cơ chế đúng và tái lập
   bit-for-bit, không phải con số thật.
2. **Tối ưu compute cho Gate 2 full** — 219 config × 9 window là phép chạy tính bằng giờ;
   Impl Plan §4 cho phép chạy song song theo config.
3. **App MVP đầy đủ** — bản hiện tại ([`webapp/`](../webapp/README.md)) là công cụ ghi chép:
   chưa tự động Base schedule, Month-End, Crash ladder, cooldown và daily limit; Return24H
   dùng daily return làm xấp xỉ. Impl Plan §9 vẫn khóa bản đầy đủ sau verdict BUILD.
