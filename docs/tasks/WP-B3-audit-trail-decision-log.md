# WP-B3 — Hoàn thiện nhật ký quyết định để truy vết được

## Metadata
Status:
PLANNED

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
- [ ] B3.1 Bổ sung trường còn thiếu theo DM §11: snapshot `available/reserved/deployed`, `strategy_config_hash`
- [ ] B3.2 Bổ sung `previous_state` / `new_state` theo enum của WP-C2
- [ ] B3.3 Mở rộng phạm vi loại sự kiện được ghi theo ST §20
- [ ] B3.4 Ghi log cho official run không phụ thuộc cờ `log_decisions`
- [ ] B3.5 Gắn nhãn `EXECUTED_EARLY` cho Base execute sớm theo ST §9
- [ ] B3.6 Viết test tái dựng lý do của ba quyết định mẫu chỉ từ log

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency T-06 DONE**
- [ ] **Dependency WP-C2 DONE** — cho phần ngữ nghĩa trạng thái; nếu chưa, gói vẫn mở được nhưng
      CHECK-B3-02 sẽ BLOCKED và gói không DONE được
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — DM §11; ST §9, §20
- [x] Data impact được biết — `decision_log` mang thêm trường; kích thước log tăng
- [x] Security impact được biết — log không được chứa dữ liệu nhạy cảm của chủ dự án
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được.

### Observability / Audit

#### CHECK-B3-01 — `decision_log` chứa đủ trường theo Data Model §11
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: đọc log của một lần chạy thật, chứng minh có snapshot `available/reserved/deployed`,
`strategy_config_hash`, và các trường còn lại mà DM §11 quy định. Đóng F-024 phần trường.

Executed By:
...

Timestamp:
...

#### CHECK-B3-02 — `previous_state` / `new_state` dùng đúng enum Execution State
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: giá trị của hai trường thuộc enum do **WP-C2** định nghĩa, không phải enum tự chế trong gói
này. Nếu WP-C2 chưa DONE → check này là `BLOCKED`, **không phải** `NOT_APPLICABLE` và **không phải**
`PASS`.

Executed By:
...

Timestamp:
...

#### CHECK-B3-03 — Phạm vi loại sự kiện được ghi phủ đủ theo Strategy §20
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: đối chiếu danh mục reason code của ST §20 với các loại sự kiện thực sự được ghi; mọi mục
không ghi phải có lý do. Hôm nay chỉ ghi ba loại.

Executed By:
...

Timestamp:
...

#### CHECK-B3-04 — Official run luôn ghi decision_log, không phụ thuộc cờ tuỳ chọn
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy official không bật cờ nào thêm, chứng minh log vẫn được ghi. Audit trail của một
official run không thể là tuỳ chọn.

Executed By:
...

Timestamp:
...

#### CHECK-B3-05 — Base execute sớm mang nhãn `EXECUTED_EARLY`
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng ca Base execute sớm và khẳng định nhãn có mặt theo ST §9. Hành vi "không lặp lại
ngày gốc" vốn đã đúng — không được làm hỏng nó. Đóng F-033.

Executed By:
...

Timestamp:
...

#### CHECK-B3-06 — Từ log tái dựng được lý do của một quyết định mà không cần chạy lại engine
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chọn ba quyết định mẫu ở ba loại khác nhau, và **chỉ từ log** trả lời được: trạng thái
trước, trạng thái sau, vốn khả dụng lúc đó, lý do, và cấu hình nào đang có hiệu lực. Đây là phép thử
thật của mục tiêu gói này.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-B3-07 — Hành vi quyết định của engine không đổi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric trước–sau trùng khớp. Ghi log không được đổi kết quả.

Executed By:
...

Timestamp:
...

#### CHECK-B3-08 — Toàn bộ test suite PASS
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Không enum trạng thái nào được tự chế trong gói này
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

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
- (dự kiến) test mới trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/engine.py`, `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- `decision_log` mang thêm trường; log cũ (nếu có) sẽ thiếu trường mới — phải phân biệt được bằng
  `strategy_config_hash` hoặc phiên bản schema

## Notes

Gói này rất dễ bị hiểu thành "thêm vài trường vào log". Phép thử thật nằm ở CHECK-B3-06: nếu không
tái dựng được lý do của một quyết định **chỉ từ log**, thì dù đủ trường theo hình thức, mục tiêu vẫn
chưa đạt.
