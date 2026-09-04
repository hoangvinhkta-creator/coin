# E2 INDEPENDENT REVIEW

Review ID:
`E2-WP-B1-002-FRESH-2026-09-04`

Task / Release:
`WP-B1 — Chính sách verdict và stopping rule`, frozen REQUIRED check
`CHECK-B1-09`.

Reviewer Session:
Phiên reviewer E2 mới, review-only, độc lập với phiên triển khai `S023`. Mọi nhãn
PASS do implementer ghi được coi là narrative cho đến khi tái lập từ source HEAD.

Executed By:
Independent reviewer agent `E2-WP-B1-002-FRESH-2026-09-04`.

Timestamp:
`2026-09-04T05:20:17Z`

## Scope

Trả lời câu hỏi frozen của `CHECK-B1-09`: có đường nào trong production path để
`BUILD` hoặc `can_proceed_to_app=true` lọt qua khi bằng chứng REQUIRED còn thiếu,
`UNKNOWN`, invalid, stale, hoặc đang chịu blocking condition hay không. Rà soát lại
đặc biệt `CHECK-B1-01`, `02`, `03`, `04`, `07`, `08`; bản sửa F-017; H-26; test
targeted/full-suite; và production reachability. Phiên này không chạy lại T-06, không
sửa production, không đổi threshold/strategy, không mở WP-B2/V2.2, không merge.

## Source Isolation

- Source branch: `origin/claude/wp-b1-verdict-correctness-j9d390`.
- Reviewed HEAD: `a7963002c1ac23d01e62a43fe9a6dd8978f27750`; khớp prefix yêu cầu
  `a796300` sau `git fetch origin`.
- Worktree detached cô lập: `/private/tmp/wp-b1-e2.eOXZec/review`.
- Branch authority check ở chế độ detached với
  `TARGET_SHA=a7963002c1ac23d01e62a43fe9a6dd8978f27750`: PASS; merge-base với
  `origin/main` là `fa6422c469f5e2ae5da3390de271ecace4b505b4`; source ahead 5 commit;
  working tree ban đầu sạch.
- Owner workspace không bị checkout/chạm; `data/` untracked của Owner được giữ nguyên.

## Frozen Requirement Reconstructed

Reviewer đọc gate ở chính commit freeze
`4fab2e9196c8dca25d594faad3420d892dfd3368`, không dựa vào trạng thái hiện tại:

> Phiên reviewer độc lập theo Solo Independent Review Procedure phải kiểm lại đặc
> biệt `CHECK-B1-01`, `CHECK-B1-02`, `CHECK-B1-07`, tự trả lời có đường nào để một
> verdict `BUILD` lọt qua khi evidence chưa đủ hay không, và lưu kết quả dưới
> `docs/reviews/`.

Gate frozen còn buộc: đủ 10/10 REQUIRED, E2 cho `CHECK-B1-09`, không hạ REQUIRED
check, không coi UNKNOWN/thiếu evidence/synthetic run là PASS, và
`can_proceed_to_app = (verdict == "BUILD")` là khoá duy nhất T-07/T-11 được đọc.

## Inputs Read

- `AGENTS.md`; toàn bộ `governance/v4/CORE/*`; `STATE_AUTHORITY.md`;
  `governance/core/00_SESSION_ORCHESTRATION.md`; `EVIDENCE_STANDARD.md`; E2 template.
- `PROJECT_PROFILE.md`, `CAPABILITY_REGISTRY.md`, `PROJECT_PROGRESS.md`,
  `PRODUCTION_PATHS.md`, `REVIEW_BUDGET_LEDGER.md`, `HARDENING_BACKLOG.md`,
  `PROJECT_DECISIONS.md`.
- Frozen/current `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md`,
  `docs/sessions/S023-wp-b1-verdict-correctness-in-progress.md`,
  `docs/CONVENTIONS.md`, backtest/spec/implementation documents và
  `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`.
- Actual history/diff/code/test ở reviewed HEAD; các owner-supplied evidence chỉ được
  dùng sau khi đối chiếu cơ học với code và canonical records.

## Independent Verification

| Check ID | Status | Evidence Level | Evidence độc lập tóm tắt | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-B1-01 | **FAIL** | E2 | 11 signal khác known/FALSE, `v2_eth=10`, Control F `p95=null`, Control G `p95=9.5` làm FS-08 thành FALSE thay vì UNKNOWN; production `run_verdict` ra BUILD/true | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-02 | PASS | E2 | Call graph cho thấy Gate 1/OOS chạy trước full-period result; F/G chỉ đọc `full.purchases`; không giao input/calculation/execution/dataset/strategy/backtest của Gate 1 | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-03 | PASS | E2 | F-017 đúng; post-F-017 replay khớp đủ 11 điểm kiểm của brief; FS-08=false theo hai P95 hiện hữu | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-04 | PASS | E2 | DEC-033 phê chuẩn as-is; source giữ đúng ba toán tử/ngưỡng; exact-boundary và one-ULP đúng | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-05 | PASS | E2 | Mapping gate-fail khớp `verdict.py` và `CONVENTIONS.md` #21(a) | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-06 | PASS | E2 | Window scope FS-03/07 và Control G `shift_days=10` truy được về #20/#21 | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-07 | **FAIL** | E2 | Hai đường fail-open tái hiện được; thiếu FS-08 input có thể thành FALSE, và non-official evidence có thể mang BUILD/true | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-08 | PASS | E2 | Chuỗi artifact chéo đủ theo câu chữ frozen; `pipeline_state.json` chỉ có reasons compact, report/metrics giữ full reasons; kết quả lịch sử vẫn DO_NOT_BUILD/false | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-09 | **FAIL** | E2 | Câu hỏi chính có câu trả lời **CÓ**, với hai counterexample production-path bên dưới | E2-WP-B1-002 | 2026-09-04 |
| CHECK-B1-10 | PASS | E2 | Reviewer chạy full suite: 391 collected, 391 passed, 0 failed; không có skip/xfail trong output; exit 0 | E2-WP-B1-002 | 2026-09-04 |

Kết quả REQUIRED advisory sau E2: **7/10 PASS; 3 FAIL** (`CHECK-B1-01`, `07`, `09`).
Reviewer không có thẩm quyền sửa status canonical trong task/progress.

## Finding E2-B1-F01 — FS-08 thiếu một control bị biến thành FALSE

**Phân loại: CONFIRMED BLOCKING.**

Production code tại `src/eth_dca_os/failure_signals.py:91-96` chỉ yêu cầu *một trong hai*
P95 hiện hữu, rồi coi P95 còn thiếu là một lần V2 tự động “beat”:

```python
if v2_eth is not None and (random_timing_p95 is not None or random_anchor_p95 is not None):
    beats_f = (random_timing_p95 is None) or (v2_eth > random_timing_p95)
    beats_g = (random_anchor_p95 is None) or (v2_eth > random_anchor_p95)
    fs["FS-08"] = _flag(not (beats_f and beats_g))
```

Probe biên trên hàm production `evaluate_failure_signals`:

```text
FS08 = {beats_both: false, ties_f: true, missing_f: false}
```

`ties_f=true` là đúng vì so sánh phải strict `>`; `missing_f=false` là sai fail-closed:
evidence Control F không tồn tại nhưng FS-08 được tuyên bố known/FALSE.

Probe tiếp qua chính production chain `pipeline.run_verdict`, với payload đúng schema
runtime, Gate 1/OOS/Gate 2/Gate 3 PASS, 11 FS khác known/FALSE,
`controls.random_timing.p95=None`, `controls.random_anchor.p95=9.5`, `v2_eth=10.0`:

```text
{"FS-08": false, "unknown": [], "verdict": "BUILD",
 "can_proceed_to_app": true, "official": true}
```

Ba điều kiện BLOCKING của Governance V4.3 đều đủ:

1. Current production path: `src/eth_dca_os/**` được `PRODUCTION_PATHS.md` khai báo;
   probe dùng production schema và gọi `failure_signals -> decide_verdict` thật.
2. Business consequence trong frozen Completion Gate: `CHECK-B1-01/07/09` cấm missing
   evidence thành PASS; BUILD/true là khoá duy nhất mở T-07/T-11.
3. Reproducible evidence: input/output và dòng mã ở trên tái hiện tất định.

Test hiện hữu bỏ sót ca này: `UNKNOWN_OVERRIDES["FS-08"]` chỉ đặt `v2_eth=None`; ca
`test_fs08_random_control` cho phép chỉ Control F nhưng chỉ thử chiều V2 thua F. Không có
ca “thiếu đúng một control trong khi V2 beat control còn lại”.

## Finding E2-B1-F02 — officiality không chặn BUILD/can_proceed

**Phân loại: CONFIRMED BLOCKING.**

`pipeline.run_verdict` gọi `decide_verdict` trước (`pipeline.py:409`); officiality chỉ
được tính sau đó và chỉ từ Gate 2/Gate 3 (`pipeline.py:410-439`). Nó bỏ qua
`g1["official"]` và `controls["official"]`. `decide_verdict` đặt
`can_proceed_to_app` chỉ theo `v == "BUILD"` (`verdict.py:36-37`), không nhận hoặc kiểm
officiality. Tìm toàn `src/eth_dca_os` cho thấy không consumer nào kết hợp
`can_proceed_to_app` với `official`.

Hai probe dùng production function và production payload schema:

```text
gate1_official=false, controls_official=false, gate2_official=true,
gate3_official=true, gates/FS clean
=> payload_official=true, warning=None, verdict=BUILD, can_proceed_to_app=true

gate1/gate2/gate3/controls official=false, gates/FS clean
=> payload_official=false, warning="DEV RUN ...", verdict=BUILD,
   can_proceed_to_app=true
```

Nhánh thứ hai là tổ hợp schema tự nhiên của synthetic/dev run; warning chỉ là text và
không giảm `can_proceed_to_app`. `CONVENTIONS.md` #21 nói T-07/T-11 chỉ đọc khoá này,
nên warning không phải enforcement. Stub/reachability trên production code + production
schema là nguồn production-realistic được `PRODUCTION_PATHS.md` §3 cho phép; synthetic
chỉ chứng minh cơ chế, không được dùng làm evidence tài chính.

Ba điều kiện BLOCKING đều đủ: current declared production path; hậu quả trực tiếp trong
frozen Completion Gate/đường T-07→T-11; input/output tái hiện tất định. Đây không thay
đổi kết quả T-06 lịch sử (vốn đã DO_NOT_BUILD), nhưng làm policy tương lai fail-open.

## CHECK-B1-02 / DEC-009

Kết luận độc lập: **KHÔNG kích hoạt chạy lại Gate 1**.

- `run_gate1` hoàn tất Gate 1/OOS/diagnostics, sau đó mới chạy full-period engine và dựng
  `_full_run_monthly_tranches` từ `full.purchases`.
- `run_controls` chỉ nhận dataset, tranches, V2 ETH và không feed ngược Gate 1.
- `run_gate2`/`run_gate3` tự tính từ dataset/config; không gọi controls.
- F-017 chỉ sửa `benchmarks.py`, phần nối dữ liệu ở `pipeline.py`, và tên payload ở
  `cli.py`; không sửa `engine.py`, strategy, gate, threshold hay dataset semantics.

Do đó kết quả Gate 1/OOS cũ không stale vì F-017; rerun official T-06 không được yêu cầu.

## CHECK-B1-03 / Post-F-017 Evidence

Owner-supplied replay **đóng đúng blocker evidence trước đó**, dù không cứu được hai
finding policy mới:

1. `702b9406ee80ec3100fba8f3d5a511534fb7080f` chứa `fd6a51467f13d3a1680542f601cf00f954051c4c`
   (commit F-017).
2. `702b940..a796300` không có production diff.
3. Dataset hash khớp đúng official T-06:
   `3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5`.
4. `master_seed=42` khớp canonical config.
5. `n_sims=1000` khớp official default.
6. `v2_eth=14.910758150139896` bằng frozen V2 ETH bit-for-bit.
7. Control F/G P95 đi vào production FS-08 tại `pipeline.py:401-403`.
8. So sánh đúng chiều strict: `v2_eth > p95`.
9. `14.910758150139896` lớn hơn cả `14.887400583487747` và
   `14.813546903782814`; production formula cho `FS-08=false`.
10. F/G/FS-08 nằm sau và ngoài Gate 1/OOS/Gate 2/Gate 3; không invalid các gate.
11. Historical T-06 vẫn `DO_NOT_BUILD` vì Gate 1/OOS precedence chạy trước FS.

Hai kết quả phải tách biệt: historical T-06 là official verdict; post-F-017 replay chỉ
là WP-B1 evidence tính lại FS-08 trên cùng official dataset, không phải official T-06 mới.

## F-017 Production Repair

PASS. Diff F-017 ở `fd6a514` trên ba file production là 46 additions/25 deletions:
`benchmarks.py` 31/19, `pipeline.py` 14/5, `cli.py` 1/1. Reviewer xác nhận:

- `monthly_tranches` lấy từng `p["nominal"]` từ actual `full.purchases`, nhóm theo tháng;
- Control F chọn timestamp độc lập cho từng tranche trong đúng tháng;
- Control G shift/clip độc lập từng tranche và giữ cùng nominal/profile;
- không còn monthly lumping;
- không đổi engine/strategy/threshold; `verdict.py` không bị sửa để ưu ái V2.1.5.

## CHECK-B1-04 Thresholds

PASS. DEC-033 chỉ phê chuẩn compatibility/preservation cho V2.1.5, không tuyên bố
empirical optimality và không cấp quyền V2.2. Code hiện tại giữ nguyên:

- FS-02: `opportunity_cap_hit_share > 0.5`;
- FS-07: `avg_cash_ratio > 0.30 and gate1_primary_ae < 102.0`;
- FS-12: `regime_advantage_share > 0.80`.

Probe exact-boundary/one-ULP: FS-02 và FS-12 FALSE tại đúng ngưỡng, TRUE ngay phía
trên; FS-07 chỉ TRUE khi cash ngay trên 0.30 **và** AE ngay dưới 102, FALSE nếu một vế
đúng boundary. Không có threshold diff sau DEC-033.

## CHECK-B1-08 Official Evidence Chain

PASS theo đúng câu chữ frozen nhờ đối chiếu chéo:

- `pipeline_state.json`: verdict/can_proceed; `reasons` bị `_strip` thành `"[2 items]"`;
- `baseline_808b61fa5ffe_metrics.json` và `report.json`: giữ full reasons;
- `backtest_runs.jsonl`: corroborate official run, commit/dataset provenance.

Không tuyên bố sai rằng `pipeline_state.json` chứa full reasons. Reviewer gọi lại
production policy với Gate 1/OOS false và xác nhận:

```text
{"verdict":"DO_NOT_BUILD",
 "reasons":["Gate 1 FAIL","OOS hard condition FAIL"],
 "can_proceed_to_app":false}
```

## Adversarial and Regression Evidence

- Python bool TRUE và `numpy.bool_(True)` đều chuẩn hoá thành plain bool và bật cap.
- Đúng một UNKNOWN (theo 12 vector hiện hữu), all UNKNOWN, TRUE+UNKNOWN đều chặn BUILD;
  `cap_cause` lần lượt `UNKNOWN`/`TRUE_AND_UNKNOWN` đúng. Ngoại lệ fail-open mới là
  **input thành phần của FS-08** bị coi known/FALSE trước khi danh sách UNKNOWN được dựng.
- Gate precedence đúng; FS-08 tie là TRUE (strict `>`); comparison direction đúng.
- Threshold exact-boundary và one-ULP đúng như mục trên.
- Targeted command:
  `PYTHONPATH=src /Users/hoangvinh/Documents/coin/.venv/bin/python -m pytest tests/test_benchmarks.py tests/test_e2e.py tests/test_gates_verdict.py tests/test_wp_b1_verdict_policy.py tests/test_wp_b1_slice_failure_signal_cap.py -q -p no:cacheprovider`
  → **59 collected, 59 passed, 0 failed, 0 skipped, 0 xfailed, exit 0**.
- Full command:
  `PYTHONPATH=src /Users/hoangvinh/Documents/coin/.venv/bin/python -m pytest tests/ -o addopts='' -p no:cacheprovider`
  → **391 collected, 391 passed, 0 failed, 0 skipped, 0 xfailed, exit 0**,
  `1994.61s (0:33:14)`.
- Environment: Python 3.11.16, numpy 2.4.6, pandas 3.0.5, pytest 9.1.1.

Test xanh không phủ định counterexample: suite hiện thiếu đúng hai invariants mà findings
nêu. Không có test nào bị sửa/nới trong phiên review.

## H-26

Giữ **CONFIRMED HARDENING**, không nâng BLOCKING. `gates.py` có thể trả `numpy.bool_`, nhưng
`verdict.py` đọc bằng truthiness nên probe PASS/FAIL đều đúng. Không có evidence mới về
business consequence trên current path do H-26; vì vậy thiếu đủ bộ ba điều kiện BLOCKING.
`RE_TRIGGER_CONDITION` hiện hữu giữ nguyên; không scope-expand vào WP-B1 trong phiên này.

## Production Diff and Change Boundary

- Reviewed WP-B1 production diff so với `origin/main`/merge-base `fa6422c4`:
  **3 files, 46 insertions, 25 deletions** (`benchmarks.py`, `pipeline.py`, `cli.py`).
- Later production diff `702b940..a796300`: **zero**.
- Working production diff do reviewer tạo: **zero**.
- File duy nhất reviewer tạo là artifact E2 FAIL này, theo yêu cầu bắt buộc của
  `EVIDENCE_STANDARD.md` rằng E2 không được chỉ tồn tại trong chat.

## Mismatches With Implementer Claims

- `CHECK-B1-03`/post-F-017 replay: claim PASS được tái lập và giữ PASS.
- `CHECK-B1-01`: claim PASS không bao phủ missing-one-control của FS-08; kết quả E2 FAIL.
- `CHECK-B1-07`: claim “missing evidence không được coi PASS ở bất kỳ đâu” bị hai
  production counterexample bác bỏ; kết quả E2 FAIL.
- `CHECK-B1-09`: không thể PASS vì câu hỏi frozen có câu trả lời CÓ.

## Conclusion

**E2 FAIL — NOT_ELIGIBLE_FOR_FREEZE.** `CHECK-B1-09=FAIL`; WP-B1 chỉ có **7/10**
REQUIRED PASS, Completion Gate chưa thoả, không được đánh dấu `DONE`. Reviewer E2 dù PASS
cũng chỉ có quyền đưa advisory result; `STATE_AUTHORITY.md` không cho reviewer tự ghi
`FROZEN`/`DONE` vào canonical state.

## Required Follow-up

STOP trước repair. Implementer/Owner phải, trong **một repair batch**:

1. xác nhận ownership và số budget `CAP-VERDICT` còn lại theo ledger/open repair cycle;
2. làm FS-08 fail-closed nếu thiếu bất kỳ `v2_eth`, Control F P95 hoặc Control G P95;
3. buộc `BUILD`/`can_proceed_to_app=true` chỉ khi toàn bộ Gate 1/OOS/Gate 2/Gate 3,
   controls và verdict evidence đều official/valid/current;
4. thêm regression tests cho missing-one-control và non-official BUILD path;
5. chạy lại targeted/full suite và một phiên E2 mới.

Không rerun T-06, không đổi threshold/strategy, không mở WP-B2/V2.2, không merge main.
