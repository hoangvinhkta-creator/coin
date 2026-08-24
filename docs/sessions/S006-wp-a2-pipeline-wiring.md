# SESSION HANDOFF — S006

Session ID:
S006

Task:
WP-A2 — Bật các hạng mục đã viết nhưng pipeline chưa chạy
(F-003, F-004, F-012, F-013, F-014; RSK-007)

Task Mode:
MAJOR

Project Profile:
PRODUCT

Status:
DONE — 10/10 REQUIRED check PASS (E1 toàn bộ). Exit Criteria đủ.

Model/Effort thực thi:
Tier C (Opus) / high — xác nhận lại bằng `routing_engine.py` tại phiên với đúng Routing
Inputs của file task: `base_tier=C, tier=C, model=Opus, model_score=2.0, effort=high,
effort_score=2.15, model_floors=[none], effort_floors=[none], warnings=[none]`.
**Tier C đến TỰ NHIÊN từ router, không qua nhánh override** — xác nhận MICRO-GOVDEF-001
không hồi quy (đây chính là task từng làm lộ GOVDEF-001). `validate_routing.py` PASS
(17 file MAJOR, 0 accepted manual override).

Môi trường:
Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1

Base commit khi mở phiên: `0f2a2ab` (WP-D1 DONE), working tree sạch, HEAD = origin.

## Result

**WP-A2 = DONE.** Gói **đấu nối** (wiring), không phải gói thuật toán: mọi thành phần đã tồn
tại và đúng spec, chỉ chưa được pipeline gọi. Chuỗi: Ready Gate xác nhận lại (13/13, gồm
kiểm tra hồi quy router) → baseline BEFORE tái hiện đủ 5 finding với phân biệt A/B/C/D/E →
test-first 9 test wiring (8 FAIL đúng kỳ vọng + 1 PASS xác nhận hàm vốn đúng) → remediation
chỉ trong `pipeline.py`/`diagnostics.py` + 1 dòng `cli.py` → 9/9 PASS → CHECK-A2-08:
`benchmarks.py`/`metrics.py`/`windows.py`/`bootstrap.py` **0 dòng đổi** → CHECK-A2-09: đo
BEFORE/AFTER trên cùng dataset, **159 trường metric của chiến lược + Benchmark A, 0 khác
biệt** → full regression PASS.

## Baseline BEFORE (HEAD 0f2a2ab) — phân biệt A/B/C/D/E

A = code tồn tại · B = có test riêng · C = pipeline có GỌI · D = output chứa · E = downstream dùng

| Finding | A | B | C | D | E | Bằng chứng |
|---|---|---|---|---|---|---|
| F-003 Benchmark B/C/D | ✅ `benchmarks.py:66/94/145` | ✅ `test_benchmarks.py` | ❌ | ❌ | ❌ | `pipeline.py:11` chỉ import `run_benchmark_A`; grep `src/`: zero caller B/C/D |
| F-004a ablation §2.3 | ✅ `diagnostics.py:81` | ❌ | ❌ | ❌ | ❌ | `run_all()` chỉ trả correlation/redundancy/vif/score_distribution |
| F-004b volume z-score §2.4 | ✅ `diagnostics.py:94` | ❌ | ❌ | ❌ | ❌ | như trên |
| F-012 coverage §4 | ✅ `windows.py:52` | ✅ `test_windows.py:31` | ❌ | ❌ | ❌ | grep: zero caller trong `src/` |
| F-013 XIRR §16 | ✅ `metrics.py:92` | ❌ | ❌ | ❌ | ❌ | grep: zero caller trong `src/` |
| F-014 bootstrap | ✅ `bootstrap.py:32` (mặc định 1000) | ❌ | ✅ nhưng **ghi đè 200** | ⚠️ dưới chuẩn | — | `pipeline.py:75` hard-code `n_sims=200` |

**Bằng chứng đo trực tiếp cho F-014** (không suy luận từ đọc code): fixture test thay
`pipeline.block_bootstrap_ae` bằng spy ghi lại `n_sims` thực nhận —
BEFORE `{'n_sims': 200}` → AFTER `{'n_sims': 1000}`.

## Root cause (chung cho cả 5)

Đúng loại **"implementation đúng nhưng không được gọi"**, KHÔNG phải "implementation sai".
Không finding nào đòi sửa công thức — xác nhận bằng CHECK-A2-08 (0 dòng đổi ở 4 module
chỉ-đọc). Requirement canonical: ST §2.3, §2.4 ("báo cáo **chênh lệch kết quả**");
BT §4 (bảng coverage bắt buộc), §13 (1000 mỗi block length), §16 (XIRR), §12.1 (equal
capital rule), §22 (so sánh với benchmark đơn giản hơn).

## Test-first (9 test, FAIL trước fix → PASS sau fix)

File mới `tests/test_wp_a2_pipeline_wiring.py`. Tại `0f2a2ab`: **8 FAIL + 1 PASS**.
Test PASS-before là `test_a2_05b_xirr_known_answer` (nộp 100 → nhận 110 sau 1 năm ⇒ XIRR
10%) — đúng kỳ vọng: nó chứng minh hàm `xirr` vốn đã đúng, nên finding là "không được gọi"
chứ không phải "tính sai".

Các test là **wiring assertion**, đủ mạnh để bắt hồi quy kiểu "function vẫn tồn tại và unit
test riêng vẫn PASS nhưng pipeline ngừng gọi nó": chúng chạy `run_gate1` thật rồi kiểm nội
dung payload, kèm assertion chống suy biến (B/C/D phải cho giá trị KHÁC nhau; biến thể
z-score phải cho phân bố KHÁC bản gốc; hàng Benchmark A phải trùng khít `primary_median`
sẵn có).

## Remediation (tối thiểu, chỉ đấu nối)

- `diagnostics.run_all` — gọi `ablation_scores` (3 model §2.3) và `volume_zscore_variant`
  (§2.4); thêm helper `_oscore_delta_summary` chỉ **tổng hợp** chênh lệch giữa hai lần chấm
  điểm (không đổi công thức chấm điểm nào).
- `pipeline._benchmark_comparison` — gọi `run_benchmark_A/B/C/D` trên đúng 9 window pre-OOS
  với **cùng** `(start, end, contribution, exec_cfg)`; payload ghi `ae_by_window`,
  `eth_by_window`, `contributed_by_window`, `primary_median_ae` cho từng benchmark.
- `pipeline._xirr_payload` — dòng tiền = contribution ngoài (âm) + giá trị ETH cuối kỳ
  (dương), gọi `metrics.xirr` sẵn có.
- `pipeline._bootstrap_sims(dev_limit)` — official → 1000, dev → 200; `run_gate1` nhận thêm
  tham số `dev_limit` (cùng quy ước với `run_gate2`/`run_gate3`/`run_controls`).
- `run_gate1` — luôn sinh `window_metrics.coverage_table` (nhánh chính, không sau cờ nào).
- `cli.py` — **1 dòng**: truyền `dev_limit=args.dev_limit` xuống `run_gate1`.

## Ghi chú ranh giới scope (khai báo minh bạch)

`cli.py` không nằm trong danh sách Allowed cũng không nằm trong "Do not touch" của Expected
Touch Area. Thay đổi là một dòng truyền tham số, cùng bản chất đấu nối, không chạm công
thức/ngưỡng/định nghĩa benchmark. Không có nó, phân biệt dev/official không tới được điểm
vào thật và `ethdca run --dev-limit` sẽ chạy 1000 mô phỏng — trái với chính ngữ nghĩa
`--dev-limit` mà CLI công bố và mà gate2/gate3/controls đã dùng. Trình chủ dự án ghi nhận;
không tự coi là đã được phê duyệt.

## Impact / CHECK-A2-09

Đo BEFORE/AFTER trên **cùng dataset tổng hợp cố định** (synth 2018-01-01→2026-06-30, cùng
seed). BEFORE chạy qua `git worktree` tại `0f2a2ab` với assert provenance (`code_path` phải
thuộc worktree). So sánh **159 trường** metric của chiến lược và Benchmark A:

**Số trường khác nhau = 0.** `primary_median` 97.89745920461614 · `_full_run_eth`
22.177077553955925 · `oos_ae` 104.8556473248996 — trùng khít cả ba.

Đây là phép kiểm có ý nghĩa thật chứ không hình thức: diagnostic mới gọi `sub_factors(ind)`
và `volume_zscore_variant(ind, sf)` trên cùng `prep.indicators`, nên nếu chúng mutate đầu
vào thì score và engine sẽ đổi. Kết quả 0/159 chứng minh không có mutation.

**Payload official mở rộng** (đây là mục đích của gói, không phải tác dụng phụ): thêm
`benchmarks` (A–D), `diagnostics.ablation`, `diagnostics.volume_zscore_variant`,
`window_metrics.coverage_table`, `xirr`, `official`/`dev_limit`. Dữ liệu tổng hợp **chỉ**
dùng cho engineering verification theo DEC-003 — không tuyên bố edge, không official verdict.

## Gate staleness (DEC-009)

WP-A2 **không** đổi input/calculation/execution/dataset interpretation của chiến lược —
CHECK-A2-09 chứng minh 0/159 trường đổi. Phần mở rộng là **nội dung báo cáo**, không phải
hành vi backtest. Hiện trạng: **NO CURRENT OFFICIAL RESULT TO INVALIDATE** (repo chưa từng
có official run; BLK-001 vẫn mở). Không chạy official Gate trong phiên này.

## Full regression

`python -m pytest tests/` → **108 passed in 525.31s (0:08:45)**, 0 failed, 0 skipped,
exit code 0 (99 test trước WP-A2 + 9 test wiring mới). Không test cũ nào bị sửa/skip/nới
lỏng — diff `tests/` chỉ THÊM một file mới. Thời gian tăng (431s → 525s) là hệ quả trực
tiếp và đúng đắn của bootstrap 1000 mô phỏng/block length (BT §13), tức chính hành vi mà
CHECK-A2-06 yêu cầu.

## Governance validators

structure / project_state / routing / easy_roadmap / evidence / task_completion — PASS.
**Giới hạn đã biết, không coi là bằng chứng chất lượng của WP-A2:** `validate_evidence` và
`validate_task_completion` quét glob `TASK-*.md`, không khớp quy ước `WP-*.md` của repo →
PASS trên **tập rỗng** (0 record, 0 DONE task được kiểm). Tồn đọng tooling từ S003, ngoài
scope WP-A2, vẫn nằm trong danh sách chờ chủ dự án.

## Finding / risk mới

Không phát hiện finding hay risk mới. Không hàm nào "được cho là đúng" hoá ra sai khi chạy
thật (điều kiện escalation không kích hoạt).

## Key Decisions

1. Đối chiếu B/C/D theo **từng window pre-OOS** (song song với cách A đang được dùng), thay
   vì một lần trên toàn kỳ — giữ đúng khung so sánh của BT §4.1/§22 và cho phép kiểm equal
   capital rule theo window.
2. `dev_limit` (thay vì cờ `official` riêng) để đồng nhất quy ước dev/official đã có ở
   gate2/gate3/controls.
3. XIRR lấy giá trị cuối kỳ theo close cuối dataset — dòng tiền tối thiểu, không thêm giả
   định định giá nào ngoài spec.

## Files changed

- `src/eth_dca_os/pipeline.py` — import B/C/D + `xirr` + `coverage_table`/`gate_windows`/
  `primary_median`; thêm `_bootstrap_sims`, `_benchmark_comparison`, `_xirr_payload`;
  `run_gate1` nhận `dev_limit`, payload thêm `benchmarks`/`coverage_table`/`xirr`/`official`
- `src/eth_dca_os/diagnostics.py` — `run_all` gọi ablation + volume z-score, thêm
  `_oscore_delta_summary`
- `src/eth_dca_os/cli.py` — 1 dòng truyền `dev_limit`
- `tests/test_wp_a2_pipeline_wiring.py` — MỚI, 9 test wiring
- `docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md` — evidence + Status
- `PROJECT/PROJECT_PROGRESS.md` (+ `LO_TRINH_DE_HIEU.md` sinh tự động)

## Files Next Agent Should Read

1. `PROJECT/PROJECT_PROGRESS.md`
2. `docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md` (evidence 10 check)
3. File task của gói được chọn tiếp theo
