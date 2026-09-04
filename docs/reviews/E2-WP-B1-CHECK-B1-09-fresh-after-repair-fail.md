# E2 INDEPENDENT REVIEW

Review ID:
`E2-WP-B1-003-FRESH-AFTER-REPAIR-2026-09-04`

Task / Release:
`WP-B1 — Chính sách verdict và stopping rule`, frozen REQUIRED check `CHECK-B1-09`.

Reviewer Session:
Phiên reviewer E2 mới, review-only, độc lập với phiên implementer `S023` và với reviewer
`E2-WP-B1-002-FRESH-2026-09-04`. Mọi PASS hiện hữu được coi là narrative cho tới khi tái lập.

Executed By:
Fresh Independent E2 reviewer.

Timestamp:
`2026-09-04T09:24:09Z`

## Scope

Rà soát đúng HEAD repair `82ff39c94685151f94764c158b0b3b10c53d7d6f`: hai blocker
`E2-B1-F01`/`E2-B1-F02`, toàn bộ frozen `CHECK-B1-01/02/03/04/07/08/09/10`, F-017,
post-F-017 evidence, production reachability và H-26. Không repair production, không đổi
threshold/strategy/spec, không rerun T-06 hoặc replay 1000 simulation, không mở WP-B2/V2.2,
không merge `main`.

## Source Isolation

- Source branch: `origin/claude/wp-b1-verdict-correctness-j9d390`.
- Reviewed HEAD: `82ff39c94685151f94764c158b0b3b10c53d7d6f`; prefix `82ff39c` khớp.
- Detached worktree: `/private/tmp/wp-b1-e2.cBoZf2`.
- Branch-authority check với `TARGET_SHA` đúng full SHA: PASS; merge-base với `origin/main` =
  `fa6422c469f5e2ae5da3390de271ecace4b505b4`; ahead 7; tracked worktree ban đầu CLEAN;
  production working diff ban đầu EMPTY.
- Owner workspace không bị checkout/chạm; `data/` untracked được giữ nguyên.
- Môi trường: Python 3.11.16, numpy 2.4.6, pandas 3.0.5, pytest 9.1.1.

## Canonical Requirement Reconstructed

Đọc gate tại đúng commit freeze `4fab2e9196c8dca25d594faad3420d892dfd3368`, không dựa vào
addendum hiện tại:

- Objective: WP-B1 tồn tại để một verdict thuận lợi không được phát ra trên evidence chưa đủ.
- `CHECK-B1-01`: khi REQUIRED FS còn UNKNOWN, **verdict phải khác `BUILD`** và
  `can_proceed_to_app=false`.
- `CHECK-B1-07`: UNKNOWN/thiếu evidence không được coi PASS ở bất kỳ đâu.
- `CHECK-B1-09`: reviewer phải trả lời có đường nào để **một verdict `BUILD`** lọt qua khi
  evidence chưa đủ hay không.

Vì vậy canonical answer cho câu hỏi BUILD-vs-PROCEED là **A**: evidence non-official phải ngăn
cả `verdict=BUILD` lẫn `can_proceed_to_app=true`. Phương án B mâu thuẫn câu chữ frozen. Dòng
`CONVENTIONS.md` #21(a) rằng T-07/T-11 đọc `can_proceed_to_app` không hạ hoặc viết lại nghĩa
của Completion Gate frozen; `GOVERNANCE_V4.md` § Legacy Gate Compatibility cấm làm vậy.

## Independent Verification

| Check ID | Status | Evidence Level | Evidence độc lập | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-B1-01 | **FAIL** | E2 | Missing/NaN đã UNKNOWN, nhưng `±inf` vẫn được helper chấp nhận là “finite”; một số tổ hợp làm FS-08 FALSE và cho phép BUILD. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-02 | PASS | E2 | F-017 chỉ đổi đường `full.purchases → monthly_tranches → Controls F/G → FS-08`; Gate1/OOS đã tính xong trước full run, Gate2/3 tách riêng; DEC-009 không kích hoạt. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-03 | PASS | E2 | Per-tranche repair còn đúng; complete-input formula giữ strict `>`; owner replay 8/8 điều kiện vẫn cho FS-08=false. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-04 | PASS | E2 | Source giữ đúng FS-02 `>0.5`, FS-07 `>0.30 AND <102.0`, FS-12 `>0.80`; exact boundary/one-ULP PASS; DEC-033 còn hiệu lực. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-05 | PASS | E2 | Mapping gate-fail và precedence khớp code/CONVENTIONS #21(a). | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-06 | PASS | E2 | Quy ước window, `shift_days=10`, F/G per-tranche còn truy được về #20/#21. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-07 | **FAIL** | E2 | Hai đường frozen fail-closed vẫn hở: FS-08 nhận infinity; mọi tổ hợp non-official vẫn mang nhãn BUILD dù progression flag false. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-08 | PASS | E2 | Historical official chain vẫn DO_NOT_BUILD, hai lý do đầy đủ ở companion artifacts, can_proceed=false; không artifact nào bị mutate. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-09 | **FAIL** | E2 | Câu hỏi frozen có câu trả lời CÓ; hai BLOCKING findings bên dưới chưa đóng hoàn toàn. | E2-WP-B1-003 | 2026-09-04 |
| CHECK-B1-10 | PASS | E2 | Full repository suite xem § Test Evidence; không skip/xfail. Suite xanh không phủ các probe adversarial còn đỏ. | E2-WP-B1-003 | 2026-09-04 |

WP-B1 advisory count sau review: **7/10 REQUIRED PASS; 3 FAIL** (`CHECK-B1-01`, `07`, `09`).

## Finding E2-B1-F01 — CHƯA ĐÓNG: kiểm tra “finite” không loại infinity

Phân loại: **CONFIRMED BLOCKING**, giữ cùng finding; không mint ID mới.

`failure_signals.py::_numeric_and_finite` trả `not math.isnan(float(x))`. Công thức này trả
`True` cho cả `float('inf')` và `float('-inf')`, trái yêu cầu repair rằng cả ba input FS-08
phải hiện hữu **và finite**. Probe trên production function cho cả ba vị trí:

- `+inf`: `v2_eth → FS-08=False`; F/G P95 → `FS-08=True` thay vì UNKNOWN.
- `-inf`: `v2_eth → FS-08=True`; F/G P95 → `FS-08=False` thay vì UNKNOWN.
- Ba ca P95=`-inf` hoặc `v2_eth=+inf` có thể tạo vacuous beat; với 11 FS còn lại FALSE,
  `any_true=False` và `decide_verdict` có thể trả BUILD.
- `None`/NaN/chuỗi không chuyển được/object → UNKNOWN đúng. Numeric-string gây TypeError trước
  verdict (fail-loud, không leak). `bool` bị nhận như số và không UNKNOWN.

Đủ ba căn cứ BLOCKING: `src/eth_dca_os/**` là current production path; hậu quả nằm trực tiếp
trong frozen `CHECK-B1-01/07/09`; probe input/output tái hiện tất định. Existing regression
chỉ kiểm `None` và NaN, không kiểm infinity.

## Finding E2-B1-F02 — CHƯA ĐÓNG: repair chỉ chặn progression, vẫn phát nhãn BUILD

Phân loại: **CONFIRMED BLOCKING**, giữ cùng finding; không mint ID mới.

`pipeline.run_verdict` tính analytical verdict trước; khi `official=False`, code chỉ thay
`can_proceed_to_app` và reasons, không thay `v['verdict']`. `save_run(... verdict=v['verdict'])`
vẫn persist `BUILD`, CLI vẫn in `BUILD`.

Production-schema probes với gates/FS sạch:

| Tổ hợp official | `official` | `verdict` | `can_proceed_to_app` | Canonical A |
|---|---:|---|---:|---|
| Gate1/Gate2/Gate3/Controls đều true | true | BUILD | true | PASS |
| chỉ Gate1 false | false | **BUILD** | false | FAIL |
| chỉ Gate2 false | false | **BUILD** | false | FAIL |
| chỉ Gate3 false | false | **BUILD** | false | FAIL |
| chỉ Controls false | false | **BUILD** | false | FAIL |
| nhiều nguồn false | false | **BUILD** | false | FAIL |
| tất cả false | false | **BUILD** | false | FAIL |
| code provenance unresolved với flags true | không trả payload | `ProvenanceUnresolvedError` | n/a | PASS fail-loud |

Officiality đã AND đủ bốn cờ nguồn, nhưng enforcement chưa đáp ứng frozen semantic A. Đủ ba căn
cứ BLOCKING: current production output path `run_verdict → save_run/CLI`; business consequence
trong frozen Objective/CHECK-B1-07/09 và cổng T-07; probe tái hiện được cho từng tổ hợp.

## Post-F-017 / DEC-009 / Historical Evidence

- Complete evidence vẫn hợp lệ: dataset hash
  `3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5`, seed 42,
  n_sims 1000, `v2_eth=14.910758150139896`, F P95 `14.887400583487747`, G P95
  `14.813546903782814`; cả hai strict comparisons true; FS-08=false.
- Không rerun 1000 simulations; chỉ áp công thức production hiện tại cho complete finite inputs.
- F-017 không giao đường Gate1/OOS/Gate2/Gate3 nên DEC-009 kết luận KHÔNG; không rerun Gate1/T-06.
- Historical T-06 không đổi: `DO_NOT_BUILD`, reasons `['Gate 1 FAIL', 'OOS hard condition FAIL']`,
  `can_proceed_to_app=false`.

## Test Evidence

- Existing targeted WP-B1 suite: **104 collected, 104 passed, 0 failed, 0 errors, 0 skipped,
  0 xfailed; exit 0; 800.20s (0:13:20)**.
- Review-only adversarial probe `/private/tmp/wp_b1_e2_adversarial_probe.py`: **38 collected,
  20 passed, 18 failed, 0 errors, 0 skipped, 0 xfailed; exit 1; 0.41s**. Trong 18 fail:
  6 infinity, 3 numeric-string (fail-loud nhưng khác assertion UNKNOWN), 3 bool-as-number, và
  6 non-official BUILD-label combinations.
- Full suite: **412 collected, 412 passed, 0 failed, 0 errors, 0 skipped, 0 xfailed;
  exit 0; 2022.28s (0:33:42)**.

Probe là review-only, nằm ngoài repository và không được commit.

## Production Reachability

- `full.purchases → pipeline.run_gate1::_full_run_monthly_tranches → run_controls → Control F/G
  P95 → evaluate_failure_signals::FS-08 → decide_verdict → run_verdict → save_run/CLI` được xác
  nhận bằng code, targeted E2E và probe production functions.
- CASE A valid/official giữ BUILD/true.
- CASE B/C missing F/G đi UNKNOWN và không BUILD: repair phần missing đã đóng.
- CASE D/E Gate1 hoặc Controls non-official: official=false, progression=false nhưng nhãn BUILD
  vẫn lọt: không đáp ứng A.
- CASE F unresolved code provenance: fail-loud trước khi payload được trả.

## H-26

Giữ **CONFIRMED HARDENING**. `gates.py` trả `numpy.bool_`, nhưng current consumer dùng truthiness;
probe Python bool/`numpy.bool_(True)` không làm sai verdict. Không có business consequence mới
trên current path; thiếu bộ ba BLOCKING. `RE_TRIGGER_CONDITION` hiện hữu giữ nguyên.

## Production Diff and State Authority

- Reviewed production diff so với merge-base `fa6422c`: 4 file, +84/−33.
- Production diff do review tạo: **ZERO**.
- Reviewer chỉ tạo artifact E2 này theo `EVIDENCE_STANDARD.md`; không sửa task/progress/decision,
  không ghi `FROZEN`/`DONE`.
- Không HARDENING finding mới; các ca finite/officiality được hấp thụ vào hai finding hiện hữu.

## Mismatches With Implementer Claims

- Claim `_numeric_and_finite()` loại input không finite là sai: nó chỉ loại NaN.
- Claim `CHECK-B1-01/07` đã phục hồi PASS không đứng vững trước infinity probes.
- Claim F02 đã đóng chỉ đúng cho progression flag; frozen authority đòi cả verdict label.
- Claim 9/10 REQUIRED PASS giảm lại thành advisory 7/10.

## Conclusion

**E2 FAIL — NOT_ELIGIBLE_FOR_FREEZE.** `CHECK-B1-09=FAIL`; Completion Gate chưa đạt; reviewer
không có thẩm quyền đánh dấu `FROZEN` hoặc `DONE`.

## Required Follow-up

STOP trước repair theo vai trò review-only. Exact next action: implementer xử lý cả hai phần còn
hở trong cùng ownership/budget hiện hữu của `CAP-VERDICT/WP-B1`, không tạo task mới: dùng kiểm tra
finite thật cho ba input FS-08 và bảo đảm evidence non-official không phát ra nhãn `BUILD` theo
canonical A; thêm regression cho `±inf`, non-numeric/bool và ma trận officiality; sau đó chạy lại
targeted/full suite và một fresh Independent E2 khác. Không rerun T-06, không đổi threshold/
strategy, không mở WP-B2/V2.2, không merge `main`.
