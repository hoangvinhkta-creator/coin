# S016 — WP-B1 (lát cắt pre-T06 theo DEC-026): đóng F-S015-01 và phần CHECK-B1-01

Ngày: 2026-09-03
Nhánh: `claude/coindca-data-stream-vv0vwv`
Baseline (SHA ngay trước lát cắt): `28b0255` (Owner Decisions S015; `src/` y hệt WP-A5 DONE `d4586b8`)
Task: `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` — **trạng thái gói VẪN `PLANNED`**
Authority: `PROJECT/PROJECT_DECISIONS.md` **DEC-026** (ROADMAP EXCEPTION, scope freeze IN/OUT)
Capability: `CAP-VERDICT` (lineage root `WP-B1`) — **implementation ban đầu**, không tiêu repair
cycle (DEC-026 (6)).
Model/Effort canonical: **Tier D / max** — phiên chạy đúng Tier D (Fable 5.1), không uỷ quyền.

## 0. Vì sao có lát cắt này

`F-S015-01` (phát hiện tại S015, xác nhận BLOCKING tại DEC-025 (4)) nằm ngay trên official verdict
path: `failure_signals.py` gộp cờ chặn bằng `any(v is True ...)`, và `numpy.bool_(True) is True`
cho **False**. Một Failure Signal TRUE mang kiểu numpy (ca thật: `FS-11` nhận `oos_ae` là
`numpy.float64`) vô hình với quy tắc chặn BT §17 — *"BUILD là không thể khi còn bất kỳ Failure
Signal nào TRUE"*. Cùng dòng đó còn làm `None` (UNKNOWN) không kích hoạt cap — đúng ca mà
`CHECK-B1-01` (FROZEN 2026-08-23) đã nêu đích danh. Roadmap đặt `WP-B1` SAU `T-06`, nhưng `T-06`
chính là nơi phát verdict official; chủ dự án quyết (DEC-026) không dùng thứ tự roadmap làm lý do
chạy một official verdict đã biết có blocker, và cho phép **một lát cắt giới hạn** đi trước.

## 1. Scope freeze đã tuân thủ (DEC-026 (3))

IN — đã làm: root cause trong `failure_signals.py`; regression test numpy TRUE; regression test
None/UNKNOWN cho **mỗi** vị trí trong 12; đóng `F-S015-01`; phần tương ứng của `CHECK-B1-01`.

OUT — không chạm: ngưỡng FS-02/FS-07/FS-12 (B1.4); Control F / F-017 (B1.3); `docs/CONVENTIONS.md`
(B1.5/B1.6); B1.8; `CHECK-B1-02…10`; E2 (`CHECK-B1-09`); H-24/H-25; WP-D2; T-06; webapp;
`benchmarks.py`, `gates.py`, `metrics.py`, `pipeline.py`, `engine.py`, `docs/spec/`.
**`verdict.py` không đổi** — không có authority mới.

## 2. Chẩn đoán: một dòng, hai ngữ nghĩa hỏng

```
failure_signals.py:80  any_true = any(v is True for v in fs.values())
verdict.py:27          if fs["any_true"]: -> BUILD_WITH_MODIFICATIONS   else: -> BUILD
verdict.py:29          trues = [k for k, x in fs["signals"].items() if x is True]
python:                np.bool_(True) is True  ==> False        (A)
                       None is True            ==> False        (B)
```

(A) Signal TRUE kiểu numpy → cờ chặn không thấy → verdict `BUILD`; và vì `verdict.py:29` cũng
dùng `is True`, tên signal **thiếu** trong câu lý do. (B) Signal `None` → không cap → verdict
`BUILD` trên bằng chứng chưa đủ. DEC-026 (3) cấm chỉ sửa (A).

Kiểm bằng chạy: trên bản `28b0255`, trong 12 signal thì FS-01/FS-04/FS-08 đã ra bool thuần
(đi qua `sum(...) > ...`, `bool()`, `not`), còn **9 signal** (FS-02/03/05/06/07/09/10/11/12) trả
thẳng kết quả so sánh — kiểu của chúng do kiểu của input quyết định.

## 3. Sửa gì (production diff = 1 file)

`src/eth_dca_os/failure_signals.py` (+45/−15, phần lớn là docstring hợp đồng):

- Hàm `_flag(value)`: `None` giữ `None`, còn lại `bool(value)`. Áp tại **nơi dựng dict** cho
  cả 12 signal → `signals[k] ∈ {True, False, None}` với bool THUẦN Python. Nhờ đó `is True` ở
  cả `failure_signals.py` lẫn `verdict.py` đều đúng mà không chạm `verdict.py`.
- `any_true = bool(trues) or bool(unknown)`: cờ chặn bật khi có TRUE **hoặc** còn UNKNOWN
  (fail-closed; BT §17 không đánh dấu signal nào tuỳ chọn → cả 12 REQUIRED). Giữ tên khoá vì là
  hợp đồng với `verdict.py`.
- Thêm hai khoá máy đọc được: `true` (danh sách signal TRUE) và
  `cap_cause ∈ {"TRUE", "UNKNOWN", "TRUE_AND_UNKNOWN", None}`.
- **Không đổi ngưỡng** (0.5 / 0.80 / 0.30 / 102.0 / 3.0 / 0.50 / 100.0) — 
  `test_a5_07_verdict_policy_thresholds_unchanged` vẫn xanh.

Hướng đã cân nhắc và loại: đổi `is True` thành `bool(v)` chỉ ở dòng `any_true` — đóng (A) ở cờ
chặn nhưng **không** đóng phần tên thiếu ở `verdict.py:29`, và không đóng (B). Chuẩn hoá tại
nguồn là điểm sửa duy nhất đóng được cả hai mà không cần authority trên `verdict.py`.

## 4. Test — ĐỎ TRƯỚC / XANH SAU (E1)

File mới `tests/test_wp_b1_slice_failure_signal_cap.py` (33 test). Bộ input "sạch" (12/12 FALSE,
0 UNKNOWN) dùng lại đúng con số của `test_verdict_mapping`, để ca đối chứng `BUILD` chứng minh
lát cắt không chặn quá tay.

**ĐỎ TRƯỚC KHI SỬA** — chạy trên bản `failure_signals.py` tại `28b0255` (snapshot `git archive`,
nạp qua `PYTHONPATH`, xác nhận `MODULE:` trỏ vào snapshot):

    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-02]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-03]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-05]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-06]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-07]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-09]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-10]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-11]
    FAILED test_b1_01_numpy_typed_true_signal_caps_build_and_is_named[FS-12]
    FAILED test_b1_01_numpy_typed_false_signals_stay_false_and_plain_bool
    FAILED test_b1_01_exactly_one_unknown_signal_blocks_build[FS-01]
    ... (đủ 12 vị trí FS-01…FS-12, cùng thông điệp
         "FS-xx UNKNOWN nhưng cap không bật — BUILD sẽ lọt", assert False is True)
    FAILED test_b1_01_exactly_one_unknown_signal_blocks_build[FS-12]
    FAILED test_b1_01_all_twelve_unknown_blocks_build
    FAILED test_b1_01_cap_cause_is_machine_readable
    FAILED test_b1_01_only_blocking_semantics_changed_vs_pre_slice
    ========================= 25 failed, 8 passed in 0.23s =========================

8 test xanh sẵn là: ca đối chứng `BUILD`; numpy TRUE cho FS-01/FS-04/FS-08 (đã bool thuần từ
trước — xem §2); 4 ca ánh xạ gate-fail. Đúng như dự đoán từ mã.

**XANH SAU KHI SỬA**: `33 passed in 0.12s`.

**Test đánh dấu của WP-A5 đỏ đúng như nó tự tiên đoán**, rồi được xoá:

    FAILED tests/test_wp_a5_failure_signal_instrumentation.py::test_a5_04_numpy_typed_signal_would_be_invisible
    AssertionError: nếu dòng này đỏ nghĩa là `any_true` đã được làm bền với numpy.bool_ —
                    đóng F-S015-01 và xoá test này
    assert True is False

Test đó tồn tại chỉ để ghi lại cơ chế khiếm khuyết và tự ghi hướng dẫn xoá khi khiếm khuyết đóng.
Nó đã hoàn thành vai trò; giữ lại sẽ là một test khẳng định hành vi SAI. **F-S015-01 ĐÓNG.**

## 5. Chứng minh "chỉ blocking semantics đổi"

- `test_b1_01_only_blocking_semantics_changed_vs_pre_slice` nạp `failure_signals.py` tại
  `28b0255` từ git và chạy **35 vector input** (sạch; rỗng; 12 ca numpy TRUE; 12 ca một-UNKNOWN;
  9 ca TRUE kiểu Python thuần) trên cả hai bản: giá trị logic của 12 signal và danh sách `unknown`
  **trùng khớp từng vector**; `any_true` chỉ khác ở đúng hai ca mà lát cắt tồn tại để sửa.
- `test_b1_01_gate_fail_mapping_unchanged_regardless_of_cap`: khi một gate FAIL, verdict đi
  nhánh gate-fail (`DO_NOT_BUILD` / `INCONCLUSIVE`) bất kể cap bật vì TRUE hay UNKNOWN.
- `test_b1_01_numpy_typed_false_signals_stay_false_and_plain_bool`: toàn input numpy nhưng
  FALSE → 12 bool thuần đều False → `BUILD`. Chuẩn hoá không lật FALSE, không tạo UNKNOWN giả.
- Run đủ phase TRƯỚC/SAU (§7): 12 giá trị signal không đổi, verdict không đổi.

## 6. `verdict.py` không đổi (E1)

    $ git diff --stat b095874..HEAD -- src/eth_dca_os/verdict.py
    (rỗng)
    $ git diff --stat -- src/eth_dca_os/verdict.py          # working tree vs HEAD
    (rỗng)
    $ git show HEAD:src/eth_dca_os/verdict.py | md5sum ; md5sum src/eth_dca_os/verdict.py
    c44f6982a5ac817f02c6f7593f1f2267  -
    c44f6982a5ac817f02c6f7593f1f2267  src/eth_dca_os/verdict.py

Production diff của lát cắt:

    $ git diff --stat -- src/eth_dca_os
     src/eth_dca_os/failure_signals.py | 60 +++++++++++++++++++++++++++++----------
     1 file changed, 45 insertions(+), 15 deletions(-)

## 7. Run đủ phase TRƯỚC / SAU (synthetic, KHÔNG official)

Cùng dataset tổng hợp (2018-01-01 → 2026-06-30, seed mặc định), cùng `dev_limit=25`, `n_sims=50`.
Run TRƯỚC chạy trên snapshot `git archive 28b0255` (PYTHONPATH), run SAU trên working tree.
Đây là dữ liệu tổng hợp + dev_limit — **không phải official verdict** (DEC-003 / BLK-001).

| Mục | TRƯỚC (`28b0255`, snapshot) | SAU (working tree) |
|---|---|---|
| `FS-11` trong `json.dumps(default=str)` | `"False"` — **chuỗi** (dấu vết `numpy.bool_`) | **`false`** — bool JSON thật |
| 11 signal còn lại | FS-01 f, 02 t, 03 t, 04 t, 05 f, 06 f, 07 f, 08 t, 09 f, 10 f, 12 t | **y hệt** |
| `UNKNOWN` | `[]` | `[]` |
| `any_true` | `True` | `True` |
| `true` (khoá mới) | — | `['FS-02', 'FS-03', 'FS-04', 'FS-08', 'FS-12']` |
| `cap_cause` (khoá mới) | — | `TRUE` |
| `failure_signal_inputs_wp_a5` (FS-02/03/06/07/12) | — | **diff rỗng** so với TRƯỚC |
| Gate | gate1 FAIL / oos PASS / gate2 FAIL / gate3 FAIL | y hệt |
| `VERDICT` | `DO_NOT_BUILD`, `['Gate 1 FAIL']`, `can_proceed_to_app=False` | **y hệt** |
| Thời gian | 1051 s | 1015 s |

Log: `pipeline_BEFORE.log` / `pipeline_AFTER.log` (scratchpad S016, script `b1_full.py` = `a5_full.py`
của S015 + in thêm `any_true`/`true`/`cap_cause`/gate).

Kết luận: `FS-11` từ chuỗi `"False"` (dấu vết `numpy.bool_` qua `json.dumps(default=str)`) thành
bool JSON thật; 12 giá trị logic không đổi; verdict không đổi (`DO_NOT_BUILD`, `Gate 1 FAIL`) —
nhánh cap không được chạm tới ở dataset này, đúng như dự đoán.

## 8. Full suite

    $ python -m pytest tests/ -q -p no:cacheprovider
    `365 tests collected`, 365 kết quả `.` (0 `F`/`E`/`s`/`x`), `EXIT=0`, real 14m04s (pyproject `addopts="-q"` nên không in dòng tổng kết; đếm từ log). Trước lát cắt tại `28b0255`: 333 collected (orchestrator ghi 330 PASS); 333 − 1 (test đánh dấu xoá) + 33 (test lát cắt) = 365 ✓

Trước lát cắt: 330 PASS. Chênh lệch = −1 (test đánh dấu đã xoá) + 33 (test lát cắt).

## 9. Điều chỉnh có ý thức trong `tests/test_wp_a5_failure_signal_instrumentation.py`

Ngoài việc xoá test đánh dấu, `test_a5_07_no_diff_in_policy_files` trước đây chạy
`git diff b095874..HEAD -- verdict.py failure_signals.py` và đòi rỗng. Mệnh đề của CHECK-A5-07 là
"**WP-A5** không đụng hai file chính sách" — một mệnh đề về khoảng lịch sử của WP-A5. Nếu giữ
`..HEAD`, test sẽ đỏ ngay ở commit đầu tiên mà chủ sở hữu chính sách (`CAP-VERDICT`) sửa
`failure_signals.py` một cách hợp lệ — tức ở chính commit của lát cắt này — dù mệnh đề của WP-A5
vẫn đúng. Vì vậy khoá khoảng vào `b095874..d4586b8` (WP-A5 DONE); `git diff` trên khoảng đó vẫn
rỗng (kiểm tại phiên). Đây là điều chỉnh cách đo, không đổi mệnh đề và không đổi status của
CHECK-A5-07. **Nêu rõ để orchestrator/chủ dự án xét** — nếu không đồng ý, hoàn lại một dòng.

## 10. Phần dư mỹ thuật — ghi nhận cho WP-B1 đầy đủ (B1.5), KHÔNG tự sửa

Khi cap bật **chỉ vì UNKNOWN**, `verdict.py:29-30` (không đổi) dựng danh sách tên bằng
`x is True` → rỗng, và in `"Failure-signal cap:  TRUE"`. Dòng lý do kế tiếp
(`FS chưa đánh giá được: FS-xx`, `verdict.py:34-35`) và khoá `cap_cause = "UNKNOWN"` /
`true = []` trong output của `failure_signals.py` mới là nguồn đúng, máy đọc được. Câu chữ lý do
thuộc `verdict.py` — ngoài authority của lát cắt — nên để nguyên và ghi nhận tại đây.

Cùng nhóm: với `verdict.py` hiện tại, UNKNOWN đi ra `BUILD_WITH_MODIFICATIONS` (nhánh không-BUILD
duy nhất khi ba gate PASS). Chữ của CHECK-B1-01 chỉ đòi "không phải BUILD" — thoả. Việc UNKNOWN có
nên là `INCONCLUSIVE` là quyết định chính sách của WP-B1 đầy đủ (B1.1/B1.5), cần authority trên
`verdict.py`.

## 11. Việc KHÔNG làm (giữ Scope Lock DEC-026)

Không sửa `verdict.py`, `benchmarks.py`, `gates.py`, `metrics.py`, `pipeline.py`, `engine.py`,
`webapp/`, `docs/spec/`, `docs/CONVENTIONS.md`. Không đổi ngưỡng. Không tạo task mới. Không sửa
câu chữ Completion Gate. Không đánh PASS cho check nào ngoài `CHECK-B1-01`. Không chuyển WP-B1
khỏi `PLANNED`. Không chạy T-06, không dùng dữ liệu Binance (BLK-001). Không khởi tạo dòng budget
`CAP-VERDICT` trong `REVIEW_BUDGET_LEDGER.md` (DEC-026 (6) là việc của chủ dự án/orchestrator —
adapter không tự cấp budget). Không cập nhật `PROJECT_PROGRESS.md` (trạng thái gói không đổi;
orchestrator quyết cách ghi nhận lát cắt trong roadmap).

## 11b. Sự cố thao tác trong phiên (ghi để minh bạch)

Một lệnh `git stash -q` bị gõ nhầm trong lúc đếm test; phát hiện ngay và `git stash pop` trong
cùng phút, `git stash list` sau đó rỗng. Kiểm lại: `git diff --stat` không đổi (3 file, +136/−37),
39 test verdict/lát cắt vẫn xanh, không đổi branch, không commit. Hai run pipeline và full suite
đã nạp module từ trước nên không bị ảnh hưởng.

## 12. Blocker mới ngoài frozen slice

Không phát hiện. Mục §9 là điều chỉnh trong `tests/` (touch area cho phép), được nêu để xét chứ
không phải blocker.

## 13. Còn lại sau lát cắt

- `WP-B1` VẪN `PLANNED`; 9/10 check `NOT_TESTED`; `CHECK-B1-01` PASS ở mức PARTIAL (E1, chưa E2,
  chưa tính lại trên official run).
- `T-06` vẫn BLOCKED cho tới khi đủ các điều kiện còn lại của Owner Checkpoint S015 §10
  (`T-05`, `WP-A1`/DEC-027, `BLK-001`).
