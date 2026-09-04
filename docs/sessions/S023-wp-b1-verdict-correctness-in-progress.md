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

### Khuyến nghị cuối cùng (tại thời điểm Addendum 3)

**WP-B1 REMAINS IN PROGRESS.** 9/10 REQUIRED PASS bằng bằng chứng thật, xác minh cơ học đầy đủ.
Việc còn lại DUY NHẤT: một phiên Independent E2 MỚI cho `CHECK-B1-09` (Independent E2 trước đã
FAIL, chưa chạy lại — không tự chạy trong phiên này). Không đề xuất DONE.

---

## Addendum 4 — Fresh Independent E2 FAIL (E2-B1-F01/F02), bounded repair batch (2026-09-04)

### Nguồn finding

`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-fail.md` — artifact do reviewer/Owner tạo (commit
`ea5c8ac`), KHÔNG phải agent phiên này. Reviewer detached worktree tại HEAD `a796300`
(khớp prefix `a7963002c1ac23d01e62a43fe9a6dd8978f27750`), branch authority PASS, không chạm
workspace Owner. Kết luận: `CHECK-B1-01/07/09 = FAIL`; 7/10 REQUIRED PASS; **E2 FAIL —
NOT_ELIGIBLE_FOR_FREEZE**.

### Tái lập độc lập TRƯỚC khi sửa (bắt buộc theo brief)

**E2-B1-F01** — tái lập bằng `evaluate_failure_signals(v2_eth=10.0, random_timing_p95=None,
random_anchor_p95=9.5, ...11 input sạch khác)` → `FS-08=False` (không phải `None`), rồi qua
`decide_verdict` → `verdict=BUILD`, `can_proceed_to_app=True`. Khớp chính xác mô tả của reviewer.
Root cause: `failure_signals.py:91-96` (trước sửa) chỉ đòi `v2_eth is not None and (F is not
None or G is not None)`, rồi coi control vắng mặt là thắng vacuously.

**E2-B1-F02** — tái lập bằng `pipeline.run_verdict()` với `g1["official"]=False`,
`controls["official"]=False`, `g2`/`g3` cũng `official=False`, gates/FS sạch → `official=False`
nhưng `verdict=BUILD`, `can_proceed_to_app=True`, chỉ có `warning` text. Khớp mô tả reviewer.
Root cause: `official = g2.get("official", False) and g3.get("official", False)` (bỏ sót Gate 1
+ Controls) và `can_proceed_to_app` không hề đọc `official`.

Cả hai tái lập KHỚP mô tả của E2 artifact — KHÔNG có discrepancy cần STOP.

### CAP-VERDICT budget

Trước repair: 0 repair cycle đã tiêu (WP-B1 chưa từng DONE — vẫn implementation ban đầu). Diff
production cộng dồn phiên (vs `fa6422c`, mốc bắt đầu phiên IN_PROGRESS thật) trước batch này:
3 file (`benchmarks.py`, `cli.py`, `pipeline.py`), +46/−25 (F-017). Sau batch này: 4 file
(`benchmarks.py`, `cli.py`, `failure_signals.py`, `pipeline.py`), +84/−33. Trong ngân sách
canonical: không REQUIRED check nào thêm (vẫn 10), Effective Risk không đổi, không kéo việc
ngoài vertical slice CAP-VERDICT, cả hai file sửa (`failure_signals.py`, `pipeline.py`) đều nằm
trong Scope đã khai của `WP-B1`. Không `CHANGE_BUDGET_EXCEEDED`.

### Repair

- `src/eth_dca_os/failure_signals.py` — FS-08 (E2-B1-F01): thêm helper `_numeric_and_finite()`
  (None/NaN/non-numeric → không hợp lệ); FS-08 chỉ tính khi CẢ BA input (`v2_eth`,
  `random_timing_p95`, `random_anchor_p95`) hợp lệ, ngược lại `None`. Không đổi chiều so sánh,
  không đổi ngưỡng.
- `src/eth_dca_os/pipeline.py::run_verdict` — officiality (E2-B1-F02): `official` nay AND đủ
  CẢ BỐN nguồn (`g1`, `g2`, `g3`, `controls`, tái dùng nguyên cờ có sẵn — không phát minh
  provenance mới); khi `not official and v["can_proceed_to_app"]` → ép `can_proceed_to_app` về
  `False`, thêm lý do vào `reasons`. `verdict.py::decide_verdict` KHÔNG bị sửa.

### Regression tests

`tests/test_wp_b1_e2_fresh_fail_repair.py` (21 test mới):
- 8 test FS-08: cả hai present (3 tổ hợp thắng/thua), F missing, G missing, cả hai missing,
  F invalid (NaN), G invalid (NaN), v2_eth missing, một test end-to-end qua `decide_verdict`
  đúng counterexample của reviewer.
- Officiality: CASE A (official đầy đủ → không đổi hành vi), CASE D (non-official toàn phần →
  `can_proceed_to_app=False`), 4 test tham số hoá (thiếu TỪNG một trong Gate1/Gate2/Gate3/
  Controls → luôn `False`), CASE E (`controls=None` → không crash, không lọt `True`), CASE E'
  (provenance unresolved khi tuyên bố official → `ProvenanceUnresolvedError` từ cơ chế
  `save_run()` có sẵn từ WP-A1 — xác nhận cơ chế vẫn chặn đúng, không sửa gì).
- Retained adversarial: tie (so sánh strict `>` không đổi), exact-boundary/one-ULP cho
  FS-02/FS-07/FS-12.

Sửa 1 test cũ: `tests/test_gates_verdict.py::test_fs08_random_control` — case đầu (chỉ truyền
Control F) vô tình mã hoá đúng hành vi lỗi (`assert FS-08 is True`); sửa thành `is None` +
tách thêm một case mới "đủ cả hai, V2 thua F -> True" để giữ nguyên phần intent gốc còn đúng.

### Test execution

Targeted: `pytest tests/test_benchmarks.py tests/test_e2e.py tests/test_gates_verdict.py
tests/test_wp_b1_verdict_policy.py tests/test_wp_b1_slice_failure_signal_cap.py
tests/test_wp_b1_e2_fresh_fail_repair.py tests/test_wp_a5_failure_signal_instrumentation.py -v`
→ **104 collected, 104 passed, 0 failed, 477.59s**.

Full suite (`pytest tests/ -q -p no:cacheprovider`): **412 collected, 412 PASS, 0 FAIL/ERROR/
SKIP/XFAIL, `EXIT=0`** (391 trước + 21 test mới = 412, khớp số học).

### Production Reachability (production-realistic, qua chính production function)

- **CASE A** (đủ 4 nguồn official=True, gates/FS sạch) → `verdict=BUILD`,
  `can_proceed_to_app=True`, không `warning` — hành vi cũ giữ nguyên khi dữ liệu THẬT official.
- **CASE B** (Control F P95 thiếu) → `FS-08=None` → verdict không thể BUILD.
- **CASE C** (Control G P95 thiếu) → `FS-08=None` → verdict không thể BUILD.
- **CASE D** (non-official toàn phần, otherwise BUILD-eligible) → `can_proceed_to_app=False`.
- **CASE E** (provenance unresolved trong khi tuyên bố official) → `ProvenanceUnresolvedError`,
  không payload nào được trả về.

Fixture dùng để chứng minh mechanism dùng dict Python trực tiếp gọi thẳng `run_verdict`/
`evaluate_failure_signals` (production function thật, KHÔNG stub/mock nội bộ) — production-
realistic theo đúng nghĩa `PRODUCTION_PATHS.md` §3 cho phép, KHÔNG trình bày như financial
validation (đó là vai trò của T-06/official run, không đổi).

### Check state trước/sau

| Check | Trước Addendum này | Sau |
|---|---|---|
| CHECK-B1-01 | `FAIL` (fresh E2) | `PASS` |
| CHECK-B1-07 | `FAIL` (fresh E2) | `PASS` |
| CHECK-B1-09 | `FAIL` | Giữ nguyên `NOT_TESTED`/FAIL — KHÔNG tự chạy lại E2 |

### Bảo toàn lịch sử T-06 / non-goals

`T-06 = DONE`, verdict = `DO_NOT_BUILD`, `reasons=["Gate 1 FAIL","OOS hard condition FAIL"]`,
`can_proceed_to_app=false` — không đổi (đã dừng ở Gate 1/OOS trước khi FS-08/officiality-gate
mới được xét, và T-06 vốn official=true nên gate mới không đổi gì ở đó). Không rerun T-06/
Gate1/Gate2/Gate3. Không đổi threshold/strategy. Không mở V2.2. Không chạm WP-B2/WP-B3. Không
tạo task mới — đúng một repair batch trong `CAP-VERDICT`/`WP-B1` hiện có.

### H-26

Giữ nguyên `CONFIRMED HARDENING` — chính reviewer E2 cũng xác nhận lại không có business
consequence mới, không nâng BLOCKING, không Scope Expansion.

### WP-B1 REQUIRED checks sau Addendum này

**9/10 PASS** (01,02,03,04,05,06,07,08,10). 1/10 `NOT_TESTED`/FAIL (09) — cần một phiên E2 độc
lập MỚI (khác reviewer E2 này, không tự chạy trong phiên implementer).

### Khuyến nghị cuối cùng (tại thời điểm Addendum 4, sau repair batch 1)

**WP-B1 REMAINS IN PROGRESS.** Hai finding BLOCKING của fresh Independent E2 đã được chấp nhận
và sửa trong MỘT repair batch có phạm vi hẹp, đúng CAP-VERDICT/WP-B1, trong ngân sách canonical.
Việc còn lại DUY NHẤT: một phiên Independent E2 MỚI cho `CHECK-B1-09`. Không đề xuất DONE.

---

## Addendum 5 — Fresh Independent E2 VÒNG HAI (`E2-WP-B1-003`) FAIL trên repair batch 1;
## repair batch 2; CHECK-B1-01/07 phục hồi PASS lần thứ hai (2026-09-04)

### Finding

Reviewer E2 độc lập thứ ba (`E2-WP-B1-003-FRESH-AFTER-REPAIR-2026-09-04`, khác cả implementer
lẫn reviewer vòng 1) review đúng HEAD mang repair batch 1
(`82ff39c94685151f94764c158b0b3b10c53d7d6f`) và tái lập được CẢ HAI phần CHƯA đóng hết của
CÙNG hai finding (không phải finding mới, giữ nguyên ID):

- **`E2-B1-F01` còn hở**: `_numeric_and_finite()` batch 1 = `not math.isnan(float(x))` — loại
  NaN nhưng KHÔNG loại `+inf`/`-inf` (`math.isnan(inf)` là `False`). Một P95 vô hạn vẫn so
  sánh được, tạo `beats_*` giả.
- **`E2-B1-F02` còn hở**: batch 1 chỉ ép `can_proceed_to_app=False` khi non-official, để
  NGUYÊN `v["verdict"]="BUILD"` — cả trong payload trả về LẪN bản ghi đã `save_run()` xuống
  đĩa. Reviewer tái dựng canonical interpretation A trực tiếp từ frozen Objective/CHECK-B1-01/
  07/09: non-official phải ngăn CẢ verdict=BUILD LẪN can_proceed_to_app=true.

**Chấp nhận nguyên vẹn, không tranh cãi/bypass** — đây là loại "sibling fail-open path tại
cùng verdict boundary" mà chỉ thị phiên này yêu cầu tìm và đóng, không phải mở rộng phạm vi.
Tái lập độc lập trước khi sửa (khớp mô tả reviewer cả hai finding — xem thân bài chat log của
phiên).

### Budget trước/sau

Trước: 0 repair cycle tiêu; diff cộng dồn (vs `fa6422c`) 4 file, +84/−33 (F-017 + repair batch
1). Sau: cùng 4 file, +108/−33 (repair batch 2 riêng: 2 file — `failure_signals.py`,
`pipeline.py` — +37/−13). Vẫn trong ngân sách canonical: không REQUIRED check mới, không Risk
tăng, không kéo việc ngoài vertical slice, không chạm `engine.py`/`gates.py`/`regime.py`/
`ladders.py`/`capital.py`/`score.py`. Không `CHANGE_BUDGET_EXCEEDED`.

### Repair batch 2

- `failure_signals.py::_numeric_and_finite()`: viết lại — loại `None`; loại tường minh `bool`
  (Python `bool` subclass `int`, `float(True)==1.0` sẽ lọt nếu không chặn riêng); `numpy.bool_`
  tự động bị loại vì KHÔNG phải instance của `numbers.Real`; `isinstance(x, numbers.Real)`
  kiểm TRƯỚC khi ép kiểu; `math.isfinite(float(x))` loại cả NaN lẫn `±inf`.
- `pipeline.py::run_verdict`: khi `not official and v["verdict"] == "BUILD"`, hạ **verdict**
  về `"INCONCLUSIVE"` (tái dùng một trong bốn nhãn có sẵn, không phát minh trạng thái mới) VÀ
  ép `can_proceed_to_app=False`. Nhánh khác không cần chạm vì `can_proceed_to_app` chỉ `True`
  khi `verdict=="BUILD"` (hợp đồng `decide_verdict`, không đổi).

### Test mới

`tests/test_wp_b1_e2_fresh_fail_repair_v2.py` (49 test): ma trận `_numeric_and_finite` đầy đủ
(hợp lệ: int/float/`numpy.float64`/`numpy.int64`; loại: `None`/NaN/`±inf` Python lẫn
`numpy.float64`/`bool`/`numpy.bool_`/chuỗi số/chuỗi bất kỳ/object); ma trận FS-08 cho từng vị
trí input × mọi giá trị invalid (16 tổ hợp); end-to-end đúng counterexample `-inf` của reviewer;
ma trận officiality 6 tổ hợp (từng nguồn/nhiều nguồn/tất cả false) khẳng định CẢ
`verdict != "BUILD"` LẪN `can_proceed_to_app=False`, kiểm cả trên payload trả về VÀ trên bản ghi
`backtest_runs.jsonl` đã persist; case toàn official giữ nguyên `verdict=BUILD`/
`can_proceed_to_app=True` (không "xoá BUILD khỏi hệ thống"); unresolved provenance vẫn
fail-loud; và một test khoá nguyên giá trị post-F-017 owner replay (complete finite input,
KHÔNG rerun 1000 sim) để chứng minh repair không chạm formula hợp lệ. Hai test hiện có trong
`tests/test_wp_b1_e2_fresh_fail_repair.py` được TĂNG CƯỜNG (không xoá/nới) thêm assertion
`verdict != "BUILD"`.

### Kết quả test

Targeted (7 file, gồm hai test file mới): 151 PASS (không tính `test_e2e.py`, chạy riêng vì
chậm) + `test_e2e.py` 2/2 PASS (430.60s). Full suite: **461 collected, 461 PASS, 0 FAIL/ERROR/
SKIP/XFAIL, `EXIT=0`** — khớp số học 412 + 49 = 461.

### CHECK-B1-01 / CHECK-B1-07 trước/sau (lần thứ hai)

| Check | Trước Addendum này | Sau |
|---|---|---|
| CHECK-B1-01 | `FAIL` (E2 vòng 2) | `PASS` |
| CHECK-B1-07 | `FAIL` (E2 vòng 2) | `PASS` |
| CHECK-B1-09 | `FAIL` (E2 vòng 2) | Giữ nguyên — cần E2 vòng 3, không tự chạy |

### Bảo toàn lịch sử T-06 / post-F-017 evidence

`T-06 = DONE`, `V2.1.5 = FAILED`, verdict=`DO_NOT_BUILD`,
`reasons=["Gate 1 FAIL","OOS hard condition FAIL"]`, `can_proceed_to_app=false` — không đổi
(quyết ở nhánh Gate 1/OOS FAIL, trước cả FS-08 lẫn officiality gate; T-06 vốn official=true nên
không bị ảnh hưởng bởi gate mới). Post-F-017 owner replay
(`dataset_hash=3150860cb...`, `v2_eth=14.910758150139896`, `FS-08=false`) giữ nguyên, KHÔNG
rerun 1000 simulation — repair này chỉ đổi hành vi cho input thiếu/invalid/non-official, không
đổi formula cho input đầy đủ/hợp lệ/official.

### Production diff batch 2

2 file (`failure_signals.py`, `pipeline.py`), +37/−13. Cộng dồn phiên (vs `fa6422c`): 4 file,
+108/−33.

### H-26

Giữ nguyên `CONFIRMED HARDENING` (reviewer vòng 2 cũng xác nhận lại).

### WP-B1 REQUIRED checks sau Addendum này

**9/10 PASS** (01,02,03,04,05,06,07,08,10). 1/10 `NOT_TESTED`/FAIL (09) — cần phiên E2 độc lập
MỚI (vòng 3, khác cả hai reviewer trước và implementer).

### Khuyến nghị cuối cùng (cập nhật)

**WP-B1 REMAINS IN PROGRESS.** Hai vòng E2 liên tiếp đã cùng làm đúng chức năng của
`CHECK-B1-07`: bắt một stopping rule bị nới ở chi tiết kỹ thuật (dù ý định đúng cả hai lần),
buộc sửa tới khi không còn đường lọt nào tái lập được. Việc còn lại DUY NHẤT: một phiên
Independent E2 MỚI (vòng 3) cho `CHECK-B1-09`. Không đề xuất DONE.

---

## Addendum — Lifecycle Closure (2026-09-04, phiên riêng, nhánh giữ nguyên)

Phiên riêng biệt (Sonnet 5), sau khi hai addendum repair trên đóng trên chính nhánh này. Nhiệm
vụ DUY NHẤT: canonical hoá kết quả fresh Independent E2 vòng BA và đóng lifecycle `WP-B1`, theo
uỷ quyền tường minh của chủ dự án.

**Nguồn:**
- Nhánh implementation canonical: `origin/claude/wp-b1-verdict-correctness-j9d390`, HEAD xác
  nhận = `9ac01b8d3df19a68244b05f14a66f8a4ff9b90c0` (khớp SHA kỳ vọng).
- Nhánh E2 độc lập: `origin/claude/wp-b1-check-b1-09-e2-review-rzrrjx`, HEAD =
  `f3fb81eb7341b8a9521358245b30ece62f528a36`, commit CHỈ thêm đúng một file
  (`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-round3-pass.md`, +265) trên đúng HEAD `9ac01b8` —
  `git diff --stat 9ac01b8..f3fb81e -- src/ webapp/ pyproject.toml pyproject.lock` rỗng.

**Tích hợp:** fast-forward merge (`git merge --ff-only`) artifact E2 vào nhánh canonical —
history-preserving, không tạo merge commit không cần thiết vì đã là fast-forward tự nhiên.

**Cập nhật state (chỉ các file evidence/state tối thiểu cần thiết):**
- `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` — `CHECK-B1-09: NOT_TESTED → PASS`;
  Exit Criteria 10/10; Status metadata → DONE (lịch sử giữ nguyên, không viết lại).
- `PROJECT/PROJECT_DECISIONS.md` — `DEC-034` (Owner authorization đóng lifecycle).
- `PROJECT/PROJECT_PROGRESS.md` — entry Last Updated mới + hàng roadmap `WP-B1: IN_PROGRESS →
  DONE`.
- `PROJECT/REVIEW_BUDGET_LEDGER.md` — ghi nhận đóng lifecycle tại hàng `CAP-VERDICT`, 0 repair
  cycle mới tiêu.
- `PROJECT/LO_TRINH_DE_HIEU.md` — regenerate bằng `sync_easy_roadmap.py` (không sửa tay).

**Validators chạy (production code không đổi nên KHÔNG chạy lại full 461-test suite — dùng lại
evidence E2 vòng BA):**
- `branch_authority_check.sh --expect-branch claude/wp-b1-verdict-correctness-j9d390` → PASS,
  production diff = EMPTY.
- `validate_routing.py` → PASS.
- `sync_easy_roadmap.py` → PASS.
- `validate_easy_roadmap.py` → PASS.
- `validate_structure.py` → PASS.
- `validate_governance.py` → GOVERNANCE V4.3: PASS.
- `validate_project_state.py` → PASS.

**Production diff của toàn bộ phiên đóng lifecycle: ZERO** (`src/`, `webapp/`,
`pyproject.toml`, `pyproject.lock` không đổi một dòng nào).

**Kết quả:** `WP-B1: IN_PROGRESS → DONE`. `CHECK-B1-09 = PASS`. `WP-B1 REQUIRED = 10/10 PASS`.
Completion Gate = PASS. Không BLOCKING còn lại. Hai quan sát HARDENING (`H-27` đề xuất,
`aggregate_over_windows ±inf`) ghi nhận, không chặn đóng, không tạo task mới.

**Downstream KHÔNG tự mở:** `WP-B2` giữ `READY`; `WP-B3` giữ `BLOCKED` (dependency `WP-C2` chưa
`DONE`); `GATE-B` (đòi cả ba gói B `DONE`) VẪN CHƯA MỞ; `T-07` vẫn `NOT READY`; `T-11` vẫn
`BLOCKED`. Không chạy WP-B2/WP-B3. Không mở GATE-B/T-07. Không rerun T-06. Không replay Control
F/G. Không đổi threshold/strategy. Không merge `main`. Không xoá/dọn branch.

Chi tiết đầy đủ: `PROJECT/PROJECT_DECISIONS.md` `DEC-034`,
`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-round3-pass.md`.
