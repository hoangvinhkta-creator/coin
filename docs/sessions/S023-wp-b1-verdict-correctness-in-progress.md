# S023 — WP-B1 (verdict correctness): IN_PROGRESS, 7/10 REQUIRED PASS, 2 BLOCKED, 1 NOT_TESTED

Ngày: 2026-09-03
Nhánh: `claude/wp-b1-verdict-correctness-j9d390`
Base canonical xác nhận đầu phiên: `origin/main` = `fa6422c469f5e2ae5da3390de271ecace4b505b4`
Task: `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` — `PLANNED → READY (DEC-031) →
IN_PROGRESS` (phiên này)
Capability: `CAP-VERDICT` (lineage root `WP-B1`, baseline `28b0255`) — **implementation ban đầu
tiếp nối** (task chưa từng DONE nên chưa có repair cycle nào để mở), KHÔNG tiêu repair cycle.
Model/Effort canonical: Tier D / max.

## 0. Trạng thái canonical đầu phiên (đã xác nhận, không tự suy)

`T-06 = DONE` (historical disposition, `DEC-031`) · `V2.1.5 validation = FAILED` · official
verdict = `DO_NOT_BUILD` (Gate 1 FAIL, OOS hard condition FAIL) · `can_proceed_to_app = false` ·
`BLK-001 = RESOLVED` · `WP-B1 = READY` · `WP-B2 = READY` · `WP-B3 = BLOCKED` bởi `WP-C2` ·
`GATE-B` chưa mở · `T-07 NOT READY`. Official tag `v2.1.5-official-T06` peel = `5228130`.
Lát cắt pre-T06 (`DEC-026`, S016) đã đóng `F-S015-01` và phần cơ chế của `CHECK-B1-01` — KHÔNG
làm lại trong phiên này.

## 1. Việc đã làm trong phiên (DISCOVER → CLASSIFY → REPAIR, trong phạm vi WP-B1)

### CHECK-B1-02 (DEC-009) — PASS, kết luận KHÔNG
Đọc `src/eth_dca_os/pipeline.py::run_gate1` xác nhận Gate 1 (`evaluate_gate1`) và OOS
(`evaluate_oos`) được tính XONG và ghi vào `payload` **trước** khi `full = run_engine(...)` (dùng
riêng cho Control F/G) được gọi; Gate 2/Gate 3 nằm ở hai hàm khác không đọc `full`/
`monthly_tranches` bao giờ. Output duy nhất của Control F/G đi vào FS-08 — một Failure Signal,
không phải Gate/OOS. Vì `verdict.py` xét Gate1/OOS ở nhánh **đầu tiên**, FS không ảnh hưởng verdict
khi Gate1/OOS đã FAIL (đúng ca T-06). Kết luận: Gate 1 KHÔNG cần chạy lại.

### CHECK-B1-03 (F-017) — PASS
`random_timing_control`/`random_anchor_control` (`benchmarks.py`) trước đây gộp TOÀN BỘ nominal
một tháng vào MỘT lệnh tại một timestamp ngẫu nhiên — sai chữ BT §12. Sửa: `run_gate1` (`
pipeline.py`) nhóm `full.purchases` (bản ghi tranche thật, ĐÃ CÓ SẴN, không sửa `engine.py`) theo
tháng thành `monthly_tranches: {thang: [nominal_tranche, ...]}`; Control F/G nay lặp và random hóa
ĐỘC LẬP cho từng tranche. `cli.py`/`test_e2e.py` cập nhật theo khoá payload mới
(`_full_run_monthly_tranches`, đổi tên từ `_full_run_monthly_deployments`).

Test mới (`tests/test_benchmarks.py`): đếm số lần `_fill` thật (đúng số tranche, không phải số
tháng) + so sánh phương sai many-tranche vs one-lump (hệ quả tất yếu của randomize độc lập).

### CHECK-B1-05 / CHECK-B1-06 — PASS
`docs/CONVENTIONS.md` mục #21(a)-(d): ánh xạ gate-fail→verdict (đóng F-026), chính sách UNKNOWN
(chốt B1.1 — giữ `BUILD_WITH_MODIFICATIONS`, không thêm nhãn mới), `shift_days=10` của Control G,
và quy ước Control F/G per-tranche mới. Phạm vi window FS-03/FS-07 xác nhận đã đủ từ WP-A5 #20(d).

### CHECK-B1-07 — PASS
`tests/test_wp_b1_verdict_policy.py` (12 test mới): precedence khi nhiều gate FAIL đồng thời
(Gate1/OOS luôn thắng Gate2/3/FS), `can_proceed_to_app` đúng nghĩa qua 6 tổ hợp, numpy.bool_/bool
ở tầng `gates.py` (họ H-26) không làm verdict sai (kiểm bằng input `numpy.float64` thật qua
`evaluate_gate1`/`evaluate_oos`), determinism (input giống hệt, kể cả mang numpy type → output
giống hệt).

### CHECK-B1-01 — addendum (không đổi status PASS đã có từ lát cắt DEC-026)
Câu hỏi chính sách B1.1 còn mở (UNKNOWN → BWM hay INCONCLUSIVE) nay CHỐT bằng #21(b): giữ BWM,
không sửa `verdict.py`.

## 2. Không làm được trong phiên — lý do cụ thể, không phải lười

### CHECK-B1-04 (ngưỡng FS-02/FS-07/FS-12) — `BLOCKED`
Cần quyết định chủ dự án. Escalation Trigger của chính task cấm agent tự phê chuẩn thay. Không
đổi hằng số nào trong `failure_signals.py`.

### CHECK-B1-08 (tính lại verdict từ `pipeline_state.json` official) — `BLOCKED / MISSING_INPUT`
File này là 1 trong 16 artifact official được chủ dự án bảo toàn **bên ngoài repository**
(`docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4). `find` toàn repo xác nhận không tồn tại trong
`/home/user/coin`. Agent không có quyền/khả năng lấy file này, và không được rerun official run
(Master Index §6). Cần chủ dự án cung cấp file hoặc tự chạy `ethdca verdict` và dán lại kết quả.

### CHECK-B1-09 (E2 độc lập) — `NOT_TESTED`
Đòi một phiên reviewer KHÁC, chưa đọc kết luận implementer. Cùng một agent/phiên không thể tự cấp
E2 cho chính mình.

## 3. Finding mới phát sinh, đã ghi nhận đúng phân loại

`HARDENING_BACKLOG.md` H-26 (`gates.py` trả `numpy.bool`, cùng họ `F-S015-01`): RE_TRIGGER_CONDITION
thứ hai ("WP-B1 đầy đủ mở đường verdict, B1.1/B1.5") ĐÃ KÍCH HOẠT trong phiên này. Nhưng `gates.py`
nằm trong "Do not touch without Scope Expansion" của Expected Touch Area — agent KHÔNG tự ý sửa,
chỉ ghi nhận điều kiện đã kích hoạt và để lại cho một quyết định Scope Expansion tường minh. Vẫn
CONFIRMED HARDENING (không có hậu quả nghiệp vụ — consumer đọc bằng truthiness).

Không có finding BLOCKING mới nào khác phát sinh trong phạm vi capability này.

## 4. Bằng chứng test

Targeted: `pytest tests/test_benchmarks.py tests/test_e2e.py tests/test_gates_verdict.py
tests/test_wp_b1_verdict_policy.py -v` → **26/26 PASS**.

Full suite (`pytest tests/ -q -p no:cacheprovider`): **391 collected, 391 PASS, 0 FAIL/ERROR/SKIP,
`EXIT=0`.** (Lần chạy đầu tiên trong phiên phát hiện 1 FAIL không liên quan đến WP-B1:
`test_a1_08_lockfile_matches_installed_environment` — venv sạch dựng trong phiên này lệch phiên
bản transitive dependency của `requests` so với `pyproject.lock` do PyPI có bản patch mới hơn từ
lúc lockfile được sinh. Đây là artifact môi trường của phiên, không phải regression code — xác
nhận bằng cách ghim lại đúng phiên bản theo `pyproject.lock` [không sửa file production/lockfile
nào] rồi chạy lại full suite sạch, PASS 391/391.) → **CHECK-B1-10 PASS**.

Production diff phiên này (đo bằng lệnh, không suy diễn):
`git diff --shortstat fa6422c -- src/eth_dca_os` → 3 file (`benchmarks.py`, `cli.py`,
`pipeline.py`), +46/−25. Không chạm `gates.py`, `engine.py`, `verdict.py`, `regime.py`,
`ladders.py`, `capital.py`, `score.py`. Không đổi hằng số ngưỡng nào.

## 5. Production reachability

`test_e2e.py::test_full_pipeline_smoke`/`test_gate1_reproducible` chạy nguyên pipeline
(`Prepared` → `run_gate1` → `run_gate2`/`run_gate3` (dev-limit) → `run_controls` → `run_verdict`)
qua CLI thật (`eth_dca_os.cli`) trên dữ liệu synthetic — xác nhận `monthly_tranches` mới đấu nối
đúng từ `run_gate1` qua `run_controls` tới `run_verdict` không lỗi runtime, verdict vẫn nằm trong
bốn giá trị hợp lệ. Đây là bằng chứng CƠ CHẾ (mechanism), KHÔNG phải bằng chứng cho số liệu
official — số liệu official cần CHECK-B1-08 (BLOCKED).

## 6. State preservation — xác nhận KHÔNG đổi

`T-06 = DONE`, `V2.1.5 = FAILED`, verdict = `DO_NOT_BUILD`, `can_proceed_to_app = false`,
`BLK-001 = RESOLVED` — không đổi. `WP-B2 = READY`, `WP-B3 = BLOCKED` (WP-C2), `GATE-B` chưa mở,
`T-07 NOT READY` — không đổi. Official tag `v2.1.5-official-T06` không bị chạm, vẫn peel về
`5228130`. Không mở WP-B2/WP-B3/GATE-B/T-07. Không merge `main`. Không tạo task ID mới (0 task
mới — chỉ cập nhật check/subtask có sẵn trong `WP-B1`).

## 7. Khuyến nghị (tại thời điểm phần 1-6 ở trên)

**WP-B1 REMAINS IN PROGRESS.** 7/10 REQUIRED PASS (01, 02, 03, 05, 06, 07, 10) trong phạm vi agent
có thể tự thực hiện. 2 check `BLOCKED` cần input/quyết định của chủ dự án (CHECK-B1-04: phê chuẩn
ngưỡng; CHECK-B1-08: cung cấp `pipeline_state.json` official hoặc tự chạy `ethdca verdict`). 1
check `NOT_TESTED` cần một phiên E2 độc lập riêng (CHECK-B1-09). Không đề xuất DONE.

---

## Addendum — Owner Decision `DEC-033` + CHECK-B1-08 Owner-supplied evidence (cùng phiên, tiếp nối)

### A. CHECK-B1-04 — Owner Decision `DEC-033` (`OD-B1-02`)

Chủ dự án APPROVE AS-IS toàn bộ ba ngưỡng, không đổi giá trị nào:

    FS-02: opportunity_cap_hit_share > 0.5
    FS-07: avg_cash_ratio > 0.30 AND gate1_primary_ae < 102.0
    FS-12: regime_advantage_share > 0.80

Lý do (nguyên văn Owner): "Giữ nguyên các threshold đã được sử dụng trong V2.1.5 vì đây là
semantics implementation ban đầu và hiện chưa có evidence độc lập đủ mạnh để biện minh cho
threshold thay thế." Không tuyên bố ngưỡng là tối ưu thực nghiệm; không tự động cho phép mang
sang V2.2. Canonical hóa tại `docs/CONVENTIONS.md` #21(e) và `PROJECT/PROJECT_DECISIONS.md`
`DEC-033`. **Production diff của phần này = 0** (đúng chỉ thị "Không sửa threshold trong
production code" — giá trị số y hệt từ trước). Vì verdict T-06 quyết ở nhánh Gate 1/OOS FAIL,
trước khi FS cap được xét (CHECK-B1-02), quyết định này không đổi semantics đã dùng ở T-06.
`CHECK-B1-04: BLOCKED → PASS`. `F-015` ĐÓNG.

### B. CHECK-B1-08 — Owner-supplied official evidence

Owner thực hiện read-only verification trên COPY của frozen official T-06 backup
(`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`), chạy
`ethdca verdict --out-dir results`. Kết quả:

- `pipeline_state.json`: `verdict=DO_NOT_BUILD`, `can_proceed_to_app=false`, `reasons` hiển thị
  dưới dạng chuỗi literal `"[2 items]"`.
- Xác nhận bằng đọc code: đây là hành vi THIẾT KẾ có sẵn (`cli.py::_strip()` nén MỌI list thành
  `"[N items]"` khi ghi state "gọn"; `reporting.py::write_report()` tự ghi rõ trong docstring:
  "Khác `pipeline_state.json` ở chỗ KHÔNG rút gọn list... còn file này giữ nguyên số liệu
  (reasons...)") — không phải lỗi mới, không phải mất dữ liệu.
- Full reasons cross-verified từ hai artifact KHÁC cùng gói frozen official evidence, cả hai đã
  canonical hoá SHA-256 tại `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4:
  `results/baseline_808b61fa5ffe_metrics.json` và `results/report.json` — cả hai đều
  `verdict=DO_NOT_BUILD`, `reasons=["Gate 1 FAIL", "OOS hard condition FAIL"]`,
  `can_proceed_to_app=false`. `backtest_runs.jsonl` (`run_id=baseline_808b61fa5ffe`) corroborate:
  `code_commit=5228130677e9e9875335eef890b6ed748a384603` (khớp official commit), `official=true`.
- Đánh giá acceptance criteria: `report.json`/`baseline_*_metrics.json` không phải "nguồn khác"
  hay dữ liệu suy diễn — chúng là companion file được CHÍNH THIẾT KẾ HỆ THỐNG (`save_run()`/
  `write_report()`, không qua `_strip()`) chỉ định là bản đầy đủ, sinh cùng lúc, từ cùng phép
  tính, thuộc cùng gói official evidence đã canonical hoá. Kết luận: **CHO PHÉP** cross-artifact
  evidence trong trường hợp cụ thể này.
- Không rerun T-06. Không sửa artifact nào (Owner thao tác trên bản copy; `ethdca verdict` xác
  nhận read-only qua đọc code ở phiên trước).

`CHECK-B1-08: BLOCKED → PASS`, ghi rõ cả bốn điểm trên trong evidence (không tuyên bố
`pipeline_state.json` tự nó chứa full reasons).

### C. H-26

Giữ nguyên `HARDENING`. Không Scope Expansion, không sửa `gates.py` trong lượt này.

### D. Test/validator chạy trong lượt này

Lượt này KHÔNG sửa bất kỳ file production nào (`git status` xác nhận: chỉ
`PROJECT/PROJECT_DECISIONS.md`, `docs/CONVENTIONS.md`, `docs/tasks/WP-B1-*.md` thay đổi — 0 file
dưới `src/`/`tests/`). Không cần chạy lại test suite vì không có code nào để hỏng. Không rerun
official T-06. Không chạy CHECK-B1-09.

### E. Production diff của lượt này

`git diff --shortstat -- src/eth_dca_os tests` = rỗng (0 file). Toàn bộ thay đổi là docs/state:
`PROJECT/PROJECT_DECISIONS.md` (+`DEC-033`), `docs/CONVENTIONS.md` (+#21(e)),
`docs/tasks/WP-B1-*.md` (evidence CHECK-B1-04/08, subtask B1.4/B1.8, Exit Criteria),
`PROJECT/PROJECT_PROGRESS.md`, `docs/sessions/S023-*.md` (addendum này).

### F. WP-B1 REQUIRED checks sau lượt này

9/10 PASS (01, 02, 03, 04, 05, 06, 07, 08, 10). 1/10 `NOT_TESTED`: CHECK-B1-09 (E2 độc lập) — check
REQUIRED DUY NHẤT còn lại trước khi WP-B1 có thể đạt Completion Gate 100%.

### G. WP-B1 technical/lifecycle state

Technical: 9/10 REQUIRED PASS, 1 NOT_TESTED. Lifecycle: `IN_PROGRESS` (không đổi, chưa DONE —
CHECK-B1-09 chưa PASS).

### H. Requirement còn lại trước Completion Gate

Duy nhất: một phiên "Solo Independent Review Procedure" độc lập cho `CHECK-B1-09`, rà soát đặc
biệt CHECK-B1-01/02/07 (và nay có thể mở rộng xem xét CHECK-B1-04/08 vì đây là hai check vừa
đóng), lưu tại `docs/reviews/E2-WP-B1-*.md`.

### Khuyến nghị cập nhật (tại thời điểm Addendum này)

**WP-B1 REMAINS IN PROGRESS.** 9/10 REQUIRED PASS — tiến bộ đáng kể so với phần 1-6 (7/10).
Không còn `BLOCKED` nào. Chỉ còn một việc duy nhất chặn Completion Gate: phiên E2 độc lập
(`CHECK-B1-09`). Không đề xuất DONE.

---

## Addendum 2 — Independent E2 (CHECK-B1-09) FAILED: CHECK-B1-03/07 đảo về BLOCKED (2026-09-04)

### Finding

Independent E2 trên `CHECK-B1-09` báo: `CHECK-B1-03` (frozen) đòi nguyên văn "Kết quả FS-08 (do
Control F nuôi) phải được tính lại sau khi sửa" [F-017] — check này đã bị đóng khung `Status:
PASS` ở Addendum 1 dù chính đoạn evidence agent tự viết ("Giá trị FS-08 thật của official run
T-06 CHỈ tính lại được khi có `pipeline_state.json`...") đã tự thừa nhận việc tính lại đó CHƯA xảy
ra. Đây là một REQUIRED check tuyên bố PASS trong khi thiếu đúng phần bằng chứng mà chính nó yêu
cầu — vi phạm trực tiếp CHECK-B1-07 ("Thiếu bằng chứng không được coi là PASS").

**Chấp nhận nguyên vẹn, không tranh cãi, không bypass** — đúng chỉ thị phiên này. Ghi chú minh
bạch (không phải để giảm nhẹ): `ls docs/reviews/ | grep -i b1` rỗng tại thời điểm nhận finding —
không có artifact `E2-WP-B1-*.md` nào trong repo. Nội dung finding vẫn được xác nhận ĐÚNG độc lập
bằng đối chiếu trực tiếp với câu chữ frozen của `CHECK-B1-03` và evidence agent tự viết — nên được
sửa trên cơ sở đó, không phải vì đã xác minh được một phiên E2 hình thức đã ghi hồ sơ.

### Reconstruct yêu cầu (mục 2 của brief)

- FS-08 = "Random control bao trùm/vượt V2 (không vượt P95)". Công thức:
  `fs["FS-08"] = _flag(not (beats_f and beats_g))`,
  `beats_f = (random_timing_p95 is None) or (v2_eth > random_timing_p95)`,
  `beats_g = (random_anchor_p95 is None) or (v2_eth > random_anchor_p95)`.
- Cả **F VÀ G** đều bắt buộc: `run_verdict()` luôn truyền cả hai `p95` từ cùng khối `controls`
  (không có đường chỉ dùng một control).
- Input: `v2_eth` (CÓ SẴN trong `results/random_control_21b7d88e9691_metrics.json`, không cần
  tính lại) + `random_timing_p95`/`random_anchor_p95` MỚI (cần tính lại bằng code đã sửa, cần
  `monthly_tranches` — KHÔNG có trong bất kỳ artifact frozen nào, phải tái tạo bằng `run_engine()`
  trên dataset official).
- Provenance bắt buộc: `dataset_hash = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af
  3ca815d2a652d2c5`, `master_seed = 42`, code commit chứa bản sửa F-017 (nhánh này, hiện tại
  `badbfdf` hoặc mới hơn).
- Output đủ để thoả CHECK-B1-03: `control_f_p95`, `control_g_p95`, `v2_eth`, `FS-08` (TRUE/FALSE/
  UNKNOWN), cùng đủ provenance để tái lập.

### Frozen input/provenance gate

`dataset_hash`/`master_seed`/official code commit như trên đã xác định rõ. Backup official:
`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03` (chỉ đọc, không mutate).
Owner workspace có `data/` từ lần fetch official trước — dùng lại, KHÔNG fetch mới.

### Replay design + validity

Thiết kế dùng ĐÚNG `run_engine()` (production, không sửa) để tái tạo `full.purchases` → nhóm
`monthly_tranches` (logic y hệt `pipeline.run_gate1()`, tách riêng để KHÔNG gọi
`evaluate_gate1`/`window_metrics`/`evaluate_gate2`/`evaluate_gate3` — xác nhận KHÔNG rerun
Gate1/Gate2/Gate3) → `random_timing_control`/`random_anchor_control` (đã sửa F-017) →
FS-08 qua `_flag()` (đúng hợp đồng F-S015-01, tránh numpy.bool_). `v2_eth` tính lại được assert
khớp `results/random_control_21b7d88e9691_metrics.json["v2_eth"]` (dung sai 1e-6) làm validity
check — sai lệch → STOP, không coi là bằng chứng hợp lệ. Script đầy đủ: xem
`docs/tasks/WP-B1-*.md::CHECK-B1-03`.

**Smoke test** (KHÔNG phải evidence): chạy chính script trên trên dataset SYNTHETIC
(`eth_dca_os.data.synth.generate`, phạm vi 2018-01-01..2022-12-31, n_sims=30) trong phiên này —
PASS, output JSON hợp lệ, không exception, `FS-08` kiểu `bool` thuần (không phải `numpy.bool_`).
Dataset_hash in ra là synthetic — không được và không dùng làm bằng chứng FS-08 thật.

### MISSING_INPUT — không tính được trong môi trường này

Sandbox phiên này không có `data/raw/*.parquet` official (gitignored, `find` toàn repo xác nhận
không tồn tại), không có kết nối Binance, và KHÔNG được fetch dữ liệu mới thay thế (chỉ thị +
Master Index §6). **STOP với MISSING_INPUT** đúng chỉ thị mục 3 của brief — không tự tính bằng dữ
liệu khác, không suy diễn FS-08 = FALSE. FS-08 post-F-017 = **CHƯA TÍNH ĐƯỢC (UNKNOWN)**, không
coerce về FALSE.

### CHECK-B1-03 / CHECK-B1-07 trước/sau

| Check | Trước | Sau |
|---|---|---|
| CHECK-B1-03 | `PASS` | `BLOCKED — EVIDENCE INCOMPLETE` |
| CHECK-B1-07 | `PASS` | `BLOCKED — pending CHECK-B1-03` (phạm vi hẹp; 5/6 gạch đầu dòng khác không đổi, có bằng chứng riêng) |
| CHECK-B1-09 | `NOT_TESTED` (E2 vừa FAIL) | Giữ nguyên `NOT_TESTED`/FAIL — KHÔNG tự chạy lại trong phiên này |

### Test/validator chạy trong lượt này

Smoke test harness trên dataset synthetic (ngoài `src/`, tại `/tmp` scratchpad phiên — không
commit vào repo). Không sửa/chạy lại `tests/` (không có code production nào thay đổi). Không rerun
official T-06. Không chạy CHECK-B1-09.

### Production diff của lượt này

`0` — lượt này chỉ sửa `docs/tasks/WP-B1-*.md`, `PROJECT/PROJECT_PROGRESS.md`,
`docs/sessions/S023-*.md`. Không file nào dưới `src/`/`tests/` bị đổi.

### Historical T-06 / mutation

Không artifact official nào bị sửa (chỉ đọc `v2_eth` từ `random_control_21b7d88e9691_metrics.json`
bằng con số đã biết, không ghi). Không rerun T-06. Kết quả replay (khi Owner chạy) sẽ được gắn nhãn
**"POST-F-017 WP-B1 EVIDENCE REPLAY"**, không phải một official T-06 validation mới.

### WP-B1 REQUIRED checks sau lượt này

7/10 PASS (01,02,04,05,06,08,10). 2/10 BLOCKED (03,07). 1/10 NOT_TESTED/FAIL (09).

### Khuyến nghị cuối cùng (tại thời điểm Addendum 2)

**WP-B1 REMAINS IN PROGRESS.** Independent E2 finding được xử lý trung thực (đảo status, không
che giấu). Việc còn lại KHÔNG nằm trong quyền hạn agent: cần Owner chạy đúng script đã viết sẵn
trên máy có dataset official, dán lại output FS-08 post-F-017, rồi chạy lại E2 độc lập cho
CHECK-B1-09. Không đề xuất DONE.

---

## Addendum 3 — Owner cung cấp POST-F-017 WP-B1 EVIDENCE REPLAY; CHECK-B1-03/07 phục hồi PASS (2026-09-04)

Chủ dự án tự chạy đúng script replay (đã viết sẵn ở Addendum 2, không sửa) trên máy Mac giữ dataset
official T-06, cung cấp lại output:

```json
{
  "replay_label": "POST-F-017 WP-B1 EVIDENCE REPLAY",
  "source_head": "702b940",
  "dataset_hash": "3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5",
  "master_seed": 42, "n_sims": 1000,
  "v2_eth": 14.910758150139896, "frozen_v2_eth": 14.910758150139896,
  "control_f_p95": 14.887400583487747, "control_g_p95": 14.813546903782814,
  "beats_f": true, "beats_g": true, "FS-08": false
}
```

### Xác minh (không suy diễn/tối ưu — đối chiếu bằng số, 8/8 khớp)

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | `source_head=702b940` là hậu duệ trực tiếp của `fd6a514` (commit F-017) | KHỚP — `git log` xác nhận, 0 production diff giữa hai commit |
| 2 | `dataset_hash` khớp official T-06 | KHỚP nguyên văn `3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5` |
| 3 | `master_seed=42` | KHỚP |
| 4 | `n_sims=1000` (official) | KHỚP |
| 5 | `v2_eth` vs `frozen_v2_eth` | KHỚP BIT-FOR-BIT (`14.910758150139896 == 14.910758150139896`) |
| 6 | `beats_f = v2_eth > control_f_p95` | `14.910758150139896 > 14.887400583487747` → `True`, khớp |
| 7 | `beats_g = v2_eth > control_g_p95` | `14.910758150139896 > 14.813546903782814` → `True`, khớp |
| 8 | `FS-08 = not(beats_f and beats_g)` | `not(True and True) = False`, khớp |

Tính toán lại độc lập bằng Python xác nhận cùng kết quả (xem CHECK-B1-03 Addendum 3 trong task
file). Không có điều kiện nào cần STOP.

### CHECK-B1-03 / CHECK-B1-07 sau Addendum này

| Check | Trước Addendum này | Sau |
|---|---|---|
| CHECK-B1-03 | `BLOCKED — EVIDENCE INCOMPLETE` | `PASS` |
| CHECK-B1-07 | `BLOCKED — pending CHECK-B1-03` | `PASS` (phạm vi hẹp — 5 gạch đầu dòng khác không đổi) |
| CHECK-B1-09 | `NOT_TESTED`/FAIL | Giữ nguyên — KHÔNG tự chạy lại E2 trong phiên này |

### Bảo toàn lịch sử T-06

`T-06 = DONE`, `V2.1.5 = FAILED`, verdict = `DO_NOT_BUILD`,
`reasons = ["Gate 1 FAIL", "OOS hard condition FAIL"]`, `can_proceed_to_app = false` — không đổi.
`FS-08=false` (post-F-017) không lật ngược verdict lịch sử vì Gate1/OOS đã FAIL trước khi FS được
xét trong precedence của `verdict.py` (CHECK-B1-02). Kết quả replay dán nhãn tường minh
**"POST-F-017 WP-B1 EVIDENCE REPLAY"**, không phải một official T-06 validation mới. Không mutate
artifact official. Không rerun T-06/Gate1/Gate2/Gate3. Không đổi ngưỡng. Không tune V2.1.5.

### Production diff

`0` — chỉ `docs/tasks/WP-B1-*.md`, `PROJECT/PROJECT_PROGRESS.md`, `docs/sessions/S023-*.md` thay
đổi. Không sửa `tests/` (canonical validator không đòi hỏi gì bất ngờ).

### WP-B1 REQUIRED checks sau Addendum này

**9/10 PASS** (01,02,03,04,05,06,07,08,10). 1/10 `NOT_TESTED`/FAIL (09) — check REQUIRED duy nhất
còn lại.

### Khuyến nghị cuối cùng (cập nhật)

**WP-B1 REMAINS IN PROGRESS.** 9/10 REQUIRED PASS bằng bằng chứng thật, xác minh cơ học đầy đủ.
Việc còn lại DUY NHẤT: một phiên Independent E2 MỚI cho `CHECK-B1-09` (Independent E2 trước đã
FAIL, chưa chạy lại — không tự chạy trong phiên này). Không đề xuất DONE.
