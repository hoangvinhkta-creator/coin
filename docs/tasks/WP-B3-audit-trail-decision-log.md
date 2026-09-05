# WP-B3 — Hoàn thiện nhật ký quyết định để truy vết được

## Metadata
Status:
**DONE — 2026-09-05, Owner-authorized Lifecycle Closure (`DEC-037`).** `IMPLEMENTED → DONE`.
Chủ dự án chấp nhận bằng chứng Completion Gate đóng băng trong
`docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md` và uỷ quyền đóng vòng đời — xem `DEC-037`
(`PROJECT/PROJECT_DECISIONS.md`) cho toàn văn quyết định và hệ quả downstream. Đóng `F-024`
và `F-033`.

Trước đó, 2026-09-04 — IMPLEMENTED, phiên `S025` (nhánh `claude/wp-b3-audit-trail-impl-3covtf`,
tách từ `origin/main` `04f77ac`). Ready Gate được xác nhận lại đầy đủ khi mở task;
`READY → IN_PROGRESS → IMPLEMENTED`. **8/8 REQUIRED check PASS** (`CHECK-B3-01`…`CHECK-B3-08`),
đầu ra tài chính/chiến lược trùng khớp **bit-for-bit** trước–sau, full suite 537/537 PASS.
Bằng chứng đầy đủ: `docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md`.

Trước đó nữa: READY (`DEC-036`): dependency `WP-C2 DONE` nay thoả, cả hai dependency đủ.

Trước đó nữa: BLOCKED — cập nhật tại `DEC-031` (2026-09-03): dependency `T-06 DONE` thoả; lý do
chặn DUY NHẤT còn lại khi đó là `Dependency WP-C2 DONE`.

Phase:
Phase 4 — Lớp B: bắt buộc sửa trước verdict

Task Mode:
MAJOR

Lớp (RCP-001):
B — MUST FIX BEFORE VERDICT

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 2
B: 2
A: 2
X: 2
U: 1
V: 2
H: 2
C: 2
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
high

Model Routing Score:
2.0

Effort Routing Score:
1.8

Applied Model Floor:
none

Applied Effort Floor:
none

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Difficulty:
2/4

Risk:
2/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Làm cho `decision_log` đủ để trả lời câu hỏi **"vì sao hệ thống quyết định như vậy tại thời điểm
đó?"** mà không cần chạy lại engine — theo đúng Data Model §11 và Strategy §20.

## Vì sao gói này tồn tại

Hôm nay `decision_log` chỉ ghi khi `log_decisions=True` và chỉ ba loại sự kiện (invalidation, crash
entry, cooldown override). Thiếu `previous_state` / `new_state`, thiếu snapshot
`available/reserved/deployed`, thiếu `strategy_config_hash` (F-024). Và Base execute sớm không mang
nhãn `EXECUTED_EARLY` dù Strategy §9 yêu cầu "phải đánh dấu" (F-033).

Hệ quả: sau official run, không truy được vì sao một quyết định xảy ra — chỉ biết là nó đã xảy ra.

## Đóng finding

- F-024 — `decision_log` thiếu trường và thiếu loại sự kiện theo DM §11 / ST §20
- F-033 — Base execute sớm không mang nhãn `EXECUTED_EARLY` theo ST §9

## Phụ thuộc ngữ nghĩa vào WP-C2 — đọc kỹ

`previous_state` / `new_state` của Data Model §11 dùng **enum Execution State**
(`WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED`). Enum đó hiện
**không tồn tại trong `src/`** (F-006) và việc quyết định phạm vi của nó thuộc **WP-C2**.

Vì vậy CHECK-B3-02 phụ thuộc WP-C2. Nếu WP-C2 chưa DONE, CHECK-B3-02 = `BLOCKED`, và theo
`TASK_COMPLETION_GATE_STANDARD.md`, WP-B3 **không được DONE**. Không được lấp chỗ trống bằng một
enum tự chế trong gói này — làm vậy sẽ tạo ra chiều trạng thái thứ hai, đúng loại trôi lệch mà
Implementation Plan §1 muốn chặn.

## Scope

- `src/eth_dca_os/engine.py` — nội dung và phạm vi ghi `decision_log`
- `tests/` — test tái dựng quyết định từ log
- `docs/CONVENTIONS.md` — nếu phát sinh quy ước về mức chi tiết log

## Out of Scope

- Định nghĩa Execution State enum (WP-C2)
- Đổi hành vi quyết định của engine — gói này **ghi lại** quyết định, không **đổi** quyết định
- Chính sách verdict (WP-B1)
- Lớp lưu trữ bền cho app (T-09B)

## Dependencies
- T-04 (DONE)
- **T-06** (DONE)
- **WP-C2** (DONE) — chỉ cho phần ngữ nghĩa `previous_state`/`new_state`

## Blocks
- GATE-B → T-07

## Parallel-Safe With
- WP-B1, WP-B2

## Expected Touch Area

Allowed:
- `src/eth_dca_os/engine.py` — phần ghi log
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `gates.py`
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `score.py` — phần logic quyết định
- `webapp/`, `docs/spec/`

## Subtasks
- [x] B3.1 Bổ sung trường còn thiếu theo DM §11: snapshot `available/reserved/deployed`, `strategy_config_hash`
- [x] B3.2 Bổ sung `previous_state` / `new_state` theo enum của WP-C2
- [x] B3.3 Mở rộng phạm vi loại sự kiện được ghi theo ST §20
- [x] B3.4 Ghi log cho official run không phụ thuộc cờ `log_decisions`
- [x] B3.5 Gắn nhãn `EXECUTED_EARLY` cho Base execute sớm theo ST §9
- [x] B3.6 Viết test tái dựng lý do của ba quyết định mẫu chỉ từ log

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] **Dependency T-06 DONE** — `DEC-031` (2026-09-03): official run thật đã chạy, verdict `DO_NOT_BUILD`
- [x] **Dependency WP-C2 DONE** — `DEC-036` (2026-09-04, Owner-authorized Lifecycle Closure).
      Hợp đồng `ExecutionState` / `derive_execution_state` / `execution_state_timeline` /
      `market_snapshots.execution_state` đã có thật trong `src/eth_dca_os/engine.py` và
      production-reachable (17.532 bản ghi `market_snapshots`, `CHECK-C2-05` PASS)
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — DM §11; ST §9, §20
- [x] Data impact được biết — `decision_log` mang thêm trường; kích thước log tăng
- [x] Security impact được biết — log không được chứa dữ liệu nhạy cảm của chủ dự án
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — phiên `S025` (2026-09-04), đọc từ nguồn
      canonical chứ không từ báo cáo; xem `docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md` §3

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được.

### Observability / Audit

#### CHECK-B3-01 — `decision_log` chứa đủ trường theo Data Model §11
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: đọc log của một lần chạy thật, chứng minh có snapshot `available/reserved/deployed`,
`strategy_config_hash`, và các trường còn lại mà DM §11 quy định. Đóng F-024 phần trường.

**Kết quả (PASS):**

`engine.DECISION_LOG_FIELDS` khai báo hình dạng bản ghi = **đúng 19 trường của bảng DM §11**
(`decision_id`, `timestamp_utc`, `previous_state`, `new_state`, `market_regime`,
`data_quality`, `trigger_type`, `reason_code`, `opportunity_score`, `recommended_price`,
`recommended_vnd`, `recommended_usdt_est`, `zone_id`, `ladder_id`, `available_vnd`,
`reserved_vnd`, `deployed_vnd`, `strategy_config_hash`, `execution_config_hash`) **cộng đúng
một** trường `tags` mang nhãn ST §9 / BT §18 (khai báo ở `docs/CONVENTIONS.md` #23(d)).

- `test_b3_01_record_shape_is_exactly_the_data_model_table` — **đọc THẲNG bảng §11 từ
  `docs/spec/04_DATA_MODEL_V2_1_5.md`** (không chép tay danh sách trường) và khẳng định tập
  trường của MỌI bản ghi khớp đúng, trên **5.614 bản ghi** sinh bởi **12 lần chạy
  `run_engine` thật** (2 run toàn kỳ + 6 kịch bản WP-B3 + 4 kịch bản WP-C2).
- `test_b3_01_mandatory_fields_are_never_null` — 11 trường DM §11 đánh dấu
  "Bắt buộc"/"Snapshot bắt buộc": **0 null trên 5.614 bản ghi**.
- `test_b3_01_capital_snapshot_reconciles_with_the_contribution_ledger` — snapshot vốn không
  chỉ khác null mà còn ĐÚNG: tại mọi bản ghi, `available + reserved + deployed` = (số
  contribution đã bơm tới thời điểm đó) × 100, tức bất biến DM §14 đo trên chính bản ghi audit.
- `test_b3_01_recommended_usdt_est_follows_the_nominal_unit_convention` — BT §2.1 [F6] /
  CONVENTIONS #11.

Đối chứng chống PASS rỗng, đo trên đường production thật (`run_engine` toàn kỳ 2019-01-01 →
OOS end, cả hai execution config đã commit):

    HEAD 04f77ac (trước gói):  decision_log = 0 bản ghi   (cả hai config)
    sau bản sửa:               decision_log = 2.441 / 2.478 bản ghi

Đóng phần "thiếu trường" của **F-024**.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-02 — `previous_state` / `new_state` dùng đúng enum Execution State
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: giá trị của hai trường thuộc enum do **WP-C2** định nghĩa, không phải enum tự chế trong gói
này. Nếu WP-C2 chưa DONE → check này là `BLOCKED`, **không phải** `NOT_APPLICABLE` và **không phải**
`PASS`.

**Kết quả (PASS):**

`WP-C2` đã `DONE` (`DEC-036`), nên check này KHÔNG `BLOCKED`. Hai trường tiêu thụ TRỰC TIẾP
`engine.ExecutionState` do `WP-C2` định nghĩa — không có enum tự chế trong gói này.

- `test_b3_02_states_are_the_wp_c2_enum_itself` — `isinstance(v, ExecutionState)` cho từng giá
  trị, trên 5.614 bản ghi; mọi giá trị thuộc sáu giá trị ST §16/§19.
- `test_b3_02_no_second_execution_state_vocabulary` — quét **toàn bộ `src/eth_dca_os/`**: chỉ
  đúng MỘT class mang từ hai trở lên trong sáu tên trạng thái, và đó là `ExecutionState`.
- `test_b3_02_states_serialise_as_plain_strings` — `json.dumps` cho ra chuỗi thuần, không rò rỉ
  `repr` của enum.
- `test_b3_02_every_wp_c2_transition_has_exactly_one_audit_record` — **một nguồn sự thật**: số
  bản ghi có `previous_state != new_state` = số mốc `execution_state_timeline` − 1
  (**1.043 = 1.044 − 1** ở `gate1_low_friction`; **1.077 = 1.078 − 1** ở `gate3_realistic`), và
  từng cặp `(ts, trước, sau)` khớp đúng mốc timeline tương ứng.
- `test_b3_02_states_are_null_only_before_the_first_measurement` — **0 bản ghi thiếu trạng
  thái** trên cả hai run production.

Thứ tự ưu tiên và điểm đo giữ NGUYÊN theo `docs/CONVENTIONS.md` #22(b)/(c); `WP-B3` không sửa
một dòng ngữ nghĩa nào của `WP-C2`.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-03 — Phạm vi loại sự kiện được ghi phủ đủ theo Strategy §20
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: đối chiếu danh mục reason code của ST §20 với các loại sự kiện thực sự được ghi; mọi mục
không ghi phải có lý do. Hôm nay chỉ ghi ba loại.

**Kết quả (PASS):**

- `test_b3_03_reason_code_catalogue_matches_the_spec_text` — danh mục được **đọc THẲNG từ khối
  mã của ST §20** trong `docs/spec/02_STRATEGY_SPEC_V2_1_5.md` (khai triển các họ viết tắt
  `S0/S1/S2`, `O0..O4`, `CRASH_ZONE_C0..C3`) = **36 mã**, và bằng đúng
  `engine.STRATEGY_REASON_CODES`. Không mã nào được phát minh.
- `test_b3_03_every_emitted_code_and_trigger_type_is_canonical` — mọi `reason_code` thuộc danh
  mục; mọi `trigger_type` thuộc bảy giá trị DM §11 và khớp bảng tra tất định.
- `test_b3_03_catalogue_coverage_is_complete_or_declared` — **32/36 mã được ghi thật**; bốn mã
  còn lại đều có lý do canonical, khai báo trong mã nguồn:

  | Mã | Vì sao không ghi | Nguồn |
  |---|---|---|
  | `FUNDING_REQUIRED` | engine không mô hình hoá số dư USDT treasury; chỉ có ở tầng app | `ADR-001` / `DEC-035` |
  | `FUNDING_COMPLETE` | mặt còn lại của trên | `ADR-001` / `DEC-035` |
  | `PARTIAL_FILL` | engine fill nguyên zone; partial fill thuộc `WP-C3` | `engine.BACKTEST_NOT_EMITTED_REASONS` |
  | `DELAYED_DATA_FILL` | ghi làm **NHÃN** trên bản ghi của chính lần fill đó, không phải sự kiện riêng | CONVENTIONS #23(d) |

- `test_b3_03_tag_recorded_codes_really_appear_as_tags` — nhãn `DELAYED_DATA_FILL` quan sát
  được thật trên đường chạy có lỗ hổng dữ liệu.
- Sáu test tham số hoá `test_b3_03_each_added_event_type_has_a_real_engine_path` chứng minh
  ĐƯỜNG SINH THẬT cho từng loại sự kiện mới: `MAX_ZONES_BLOCK`, `ACTION_MISSED`,
  `ACTION_TTL_EXPIRED`, `DATA_DEGRADED`, `BASE_ADVANCE_SCORE`, `MONTH_END_BASE`.
- `test_b3_03_legacy_events_survive_the_migration` — ba loại sự kiện ĐÃ CÓ trước gói
  (`BULLISH_INVALIDATION`, `CRASH_ENTRY_7D`, `COOLDOWN_OVERRIDE`) không mất và giữ danh tính
  zone/ladder.

Trước gói: 3 loại sự kiện, và chỉ khi bật cờ. Sau gói, trên một run toàn kỳ thật:
**25 loại sự kiện khác nhau** trong cùng một log. Đóng phần "thiếu loại sự kiện" của **F-024**.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-04 — Official run luôn ghi decision_log, không phụ thuộc cờ tuỳ chọn
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chạy official không bật cờ nào thêm, chứng minh log vẫn được ghi. Audit trail của một
official run không thể là tuỳ chọn.

**Kết quả (PASS):**

Cờ `log_decisions` **bị gỡ khỏi hợp đồng `run_engine`**, không phải bị đặt mặc định `True`:

- `test_b3_04_run_engine_has_no_logging_flag` — `inspect.signature(run_engine)` không còn tham
  số nào chứa "log", và chuỗi `log_decisions` không còn tồn tại trong `engine.py`.
- `test_b3_04_production_window_path_writes_the_log` — chạy `metrics.run_window` (ĐÚNG hàm mà
  Gate 1 gọi cho từng window) **không truyền cờ nào**: log được ghi, và cửa sổ có giao dịch
  thật (chống PASS rỗng).

Bằng chứng mạnh nhất là phép đo trước–sau trên đường production đầy đủ (pipeline Gate 1/2/3 +
controls + verdict + hai run toàn kỳ), không bật thêm bất cứ thứ gì:

    HEAD 04f77ac:  decision_log = 0 bản ghi  -> audit trail của official run RỖNG
    sau bản sửa:   decision_log = 2.441 / 2.478 bản ghi

Đúng khiếm khuyết mà **F-024** mô tả: audit trail từng là tuỳ chọn, và trên thực tế chưa từng
được bật ở đường production.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-05 — Base execute sớm mang nhãn `EXECUTED_EARLY`
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng ca Base execute sớm và khẳng định nhãn có mặt theo ST §9. Hành vi "không lặp lại
ngày gốc" vốn đã đúng — không được làm hỏng nó. Đóng F-033.

**Kết quả (PASS):**

Kịch bản `base_advance_early` (`tests/wp_b3_scenarios.py`) dựng ca Base kéo sớm bằng
`run_engine` THẬT: OSCORE 75 ≥ 70 tại thời điểm snapshot daily mới active.

- `test_b3_05_early_base_tranche_carries_the_executed_early_label` — **3/3** bản ghi
  `BASE_ADVANCE_SCORE` mang nhãn `EXECUTED_EARLY`; số bản ghi = `counters["base_early"]`
  (không nhiều, không ít); nhãn KHÔNG bị gắn nhầm cho bất kỳ loại quyết định nào khác.
- `test_b3_05_original_schedule_day_is_not_repeated` — vế thứ hai của ST §9 vẫn đúng: cả ba
  tranche Base đều mang `reason = BASE_ADVANCE_SCORE`, **không** có bản ghi `BASE_SCHEDULE`
  nào, tức ngày gốc không bị lặp lại. Hành vi "không lặp lại ngày gốc" vốn đúng và không bị
  làm hỏng.
- `test_b3_05_executed_early_is_not_written_onto_the_purchase_record` — nhãn nằm ở AUDIT TRAIL
  (DM §11), **không** ở `purchases[].tags`. Lý do canonical ghi ở `docs/CONVENTIONS.md` #23(d):
  danh mục nhãn của purchase record là nhãn chất lượng dữ liệu BT §18 (và là đầu vào của
  `counters`), còn purchase record là đầu ra tài chính phải bất biến theo `CHECK-B3-07`.

Trên run toàn kỳ production: **66 bản ghi `BASE_ADVANCE_SCORE`**, tất cả mang nhãn. Đóng
**F-033**.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-06 — Từ log tái dựng được lý do của một quyết định mà không cần chạy lại engine
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chọn ba quyết định mẫu ở ba loại khác nhau, và **chỉ từ log** trả lời được: trạng thái
trước, trạng thái sau, vốn khả dụng lúc đó, lý do, và cấu hình nào đang có hiệu lực. Đây là phép thử
thật của mục tiêu gói này.

**Kết quả (PASS):**

`test_b3_06_three_decisions_are_explained_by_the_log_alone` chọn **ba quyết định ở ba
`trigger_type` khác nhau** từ run toàn kỳ `gate3_realistic`, trả lời năm câu hỏi CHỈ từ một
bản ghi (hàm `_answer_from_row_alone` không chạm engine), rồi **đối chiếu từng câu trả lời với
một nguồn ĐỘC LẬP**: trạng thái ↔ `execution_state_timeline` của WP-C2 đọc lại độc lập; vốn
khả dụng ↔ sổ contribution; cấu hình ↔ `BASELINE_STRATEGY.hash` / `GATE3_REALISTIC.hash`.
`test_b3_06_a_fill_record_reconstructs_its_purchase` khớp **≥100 bản ghi fill** với đúng
purchase (cùng `ts`, cùng lượng vốn).

Ba ví dụ có thật, đọc nguyên văn từ log của run toàn kỳ (chi tiết đầy đủ ở báo cáo §9):

    id=689  2021-12-20T00:00:00Z  CRASH_ENTRY_7D (regime)
      WAIT -> WAIT | regime=CRASH dq=GOOD oscore=83,876
      A/R/D = 108,9564 / 0,0000 / 3491,0436 | cfg f782f99077fe… / 789bd885640f…

    id=423  2020-10-02T00:00:00Z  BASE_ADVANCE_SCORE (base)
      COOLDOWN -> COOLDOWN | regime=STRESSED dq=GOOD oscore=71,445 | rec_vnd=20,0
      A/R/D = 123,2622 / 27,1765 / 2049,5613 | tags=['EXECUTED_EARLY']

    id=6    2019-01-04T05:30:00Z  SMART_ZONE_S0 (zone)
      ACTION_PENDING -> READY_TO_BUY | regime=STRESSED dq=GOOD oscore=35,812
      A/R/D = 79,3038 / 0,6962 / 20,0000

Mỗi dòng tự trả lời: trạng thái trước, trạng thái sau, vốn khả dụng lúc đó, lý do, và hai hash
cấu hình đang hiệu lực — không cần chạy lại engine.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

### Regression

#### CHECK-B3-07 — Hành vi quyết định của engine không đổi
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric trước–sau trùng khớp. Ghi log không được đổi kết quả.

**Kết quả (PASS):**

Phép đo TRƯỚC–SAU trên **cùng dataset, cùng config, cùng seed, cùng đường production**
(`tests/wp_b3_invariance_tool.py`, cùng họ với công cụ đã dùng ở WP-A3/WP-A6/WP-C2). Khối bất
biến gồm: Gate 1 (chín window + OOS + benchmark + diagnostics + bootstrap + concentration +
cash ratio + failure-signal inputs), Gate 2, Gate 3, Control F/G, **verdict**, và HAI lần chạy
engine toàn kỳ kèm TỪNG bản ghi purchase / contribution / cash sample / opp-cap sample /
regime timeline — **cộng cả `execution_state_timeline` và `market_snapshots` của WP-C2**
(WP-B3 tiêu thụ hợp đồng đó, không được đổi nó). `decision_log` nằm NGOÀI khối bất biến vì nó
là bề mặt gói này cố ý thay đổi.

    TRƯỚC (HEAD 04f77ac):  invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
                           invariance_bytes  = 3.728.853
    SAU  (bản sửa WP-B3):  invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
                           invariance_bytes  = 3.728.853

**Trùng khớp bit-for-bit.** Không có `BEHAVIOR_CHANGED`.

Hai phép thử độc lập nữa, ở tầng test:

- `test_b3_07_engine_behaviour_is_identical_with_the_audit_layer` (4 kịch bản) — fingerprint
  hành vi bằng đúng giá trị **chụp trên cây mã TRƯỚC bản sửa** (`tests/wp_c2_scenarios.py`
  chạy tại HEAD `04f77ac`, trước khi viết một dòng production nào).
- `test_b3_07_removing_the_audit_layer_changes_no_behaviour` (4 kịch bản) — **gỡ bỏ hoàn toàn
  lớp ghi log** (mọi `append` bị nuốt) rồi chạy lại: fingerprint vẫn trùng khớp, và
  `decision_log == []` chứng minh phép gỡ thực sự có hiệu lực. Đây là bằng chứng HÀNH VI cho
  "log quan sát, không điều khiển" — mạnh hơn mọi phép soi văn bản.

Thời gian chạy pipeline gates: 261,9s (trước) → 277,1s (sau); run toàn kỳ 7,17s → 6,68s /
5,96s. Không phát sinh escalation `SCOPE_CHANGED` về hiệu năng.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

#### CHECK-B3-08 — Toàn bộ test suite PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ.

**Kết quả (PASS):**

Xem báo cáo `docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md` §16 cho output đầy đủ (collected /
passed / failed / errors / skipped / xfail / exit code). Không test nào bị skip hay deselect để
lấy màu xanh.

Executed By:
Phiên `S025` (implementer) — nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main`
`04f77ac`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1.

Timestamp:
2026-09-04

## Exit Criteria
- [x] 100% REQUIRED checks PASS — 8/8 (`CHECK-B3-01`…`CHECK-B3-08`)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ) — không check nào bị hạ mức, không check nào
      bị đánh `NOT_APPLICABLE`
- [x] Không enum trạng thái nào được tự chế trong gói này —
      `test_b3_02_no_second_execution_state_vocabulary` quét toàn bộ `src/`
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] Session handoff được viết — `docs/sessions/S025-wp-b3-audit-trail.md`
- [x] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- WP-C2 chưa DONE khi cần đóng CHECK-B3-02 → `MISSING_INPUT`, giữ BLOCKED. **Không tự định nghĩa
  enum** để gỡ bí.
- Ghi log đầy đủ làm chậm official run tới mức không chấp nhận được → `SCOPE_CHANGED`, trình chủ dự
  án phương án (ví dụ mức chi tiết theo cấu hình), **không tự cắt trường bắt buộc của DM §11**.
- Phát hiện một quyết định của engine không thể giải thích được từ dữ liệu có sẵn → đó là finding về
  chính engine, không phải về log. Mở finding, phân lớp.

## Ảnh hưởng nếu gói này thất bại

GATE-B không đóng → T-07 không mở. Ngoài ra: khi công cụ được dùng thật, không có cách nào truy lại
vì sao hệ thống khuyên xuống tiền tại một thời điểm — mất khả năng kiểm chứng chính thứ mà chủ dự án
sẽ dựa vào để ra quyết định tài chính.

## Changed Files Registry

Created:
- `tests/test_wp_b3_audit_trail.py` — 43 test cho tám REQUIRED check + rà đối kháng A–L
- `tests/wp_b3_scenarios.py` — sáu kịch bản engine tất định cho các loại sự kiện ST §20 mà bốn
  kịch bản WP-C2 không phủ
- `tests/wp_b3_invariance_tool.py` — công cụ đo bất biến tài chính/chiến lược trước–sau
- `docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md`
- `docs/sessions/S025-wp-b3-audit-trail.md`

Modified:
- `src/eth_dca_os/engine.py` — **file production DUY NHẤT** (+266 / −15)
- `docs/CONVENTIONS.md` — quy ước #23
- `PROJECT/HARDENING_BACKLOG.md` — H-36, H-37
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`,
  `PROJECT/REVIEW_BUDGET_LEDGER.md`
- `tests/` (thích ứng, không đổi ngữ nghĩa test): `wp_c2_scenarios.py`,
  `test_wp_c2_execution_state.py`, `test_wp_a6_processing_order.py`,
  `test_wp_a4_bad_data_semantics.py`, `test_wp_d1_debt_cleanup.py`, `wp_a3_harness.py`,
  `wp_a6_order_harness.py`, `wp_a3_impact_tool.py`, `wp_a6_impact_tool.py`

Deleted:
- Không

Migration Impact:
- `decision_log` đổi hình dạng bản ghi sang đúng DM §11. Ba trường cũ được ĐỔI TÊN sang tên
  canonical, không mất thông tin: `ts` → `timestamp_utc`, `zone` → `zone_id`,
  `ladder` → `ladder_id`. Log cũ phân biệt được vì thiếu `strategy_config_hash` /
  `execution_config_hash` — hai trường nay có trên MỌI dòng theo DM §11/§14.
- `run_engine` bỏ tham số `log_decisions`. Không đường production nào truyền nó (chỉ
  `tests/` truyền), nên không consumer production nào bị ảnh hưởng.

## Notes

Gói này rất dễ bị hiểu thành "thêm vài trường vào log". Phép thử thật nằm ở CHECK-B3-06: nếu không
tái dựng được lý do của một quyết định **chỉ từ log**, thì dù đủ trường theo hình thức, mục tiêu vẫn
chưa đạt.
