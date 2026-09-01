# WP-C2 — Làm rõ và đặt tên trạng thái thực thi của hệ thống

## Metadata
Status:
BLOCKED

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 2
B: 3
A: 3
X: 3
U: 3
V: 2
H: 3
C: 3
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.75

Effort Routing Score:
2.55

Applied Model Floor:
cognitive:A>=3&X>=3

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
max

Difficulty:
3/4

Risk:
2/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Đặt tên, hợp nhất và lưu vết **hành vi đã có** thành sáu Execution State mà Strategy §16/§19 định
nghĩa, sao cho backtest và app mô tả cùng một tình huống bằng **cùng một ngôn ngữ**.

## Hiện trạng đã được S001 xác định — không phải "thiếu hoàn toàn"

| Trạng thái | Hiện trạng | Vị trí |
|---|---|---|
| `WAIT` | Tồn tại ngầm — không có candidate action. Không đặt tên, không lưu | — |
| `FUNDING_REQUIRED` | **THIẾU THẬT** như một trạng thái phân biệt được | — |
| `READY_TO_BUY` | Tồn tại ngầm — điều kiện `ts >= execute_at` | `engine.py:431` |
| `ACTION_PENDING` | Tồn tại tường minh nhưng ở `Zone.status`, không phải Execution State | `engine.py:235` |
| `COOLDOWN` | Tồn tại như biến cục bộ `in_cooldown`; hành vi được cưỡng chế đúng | `engine.py:422, 517` |
| `DATA_BLOCKED` | Hành vi tồn tại (chặn khi `dq == INVALID`) nhưng không đặt tên, không lưu | `engine.py:452, 506` |

`FUNDING_REQUIRED` thiếu thật vì Backtest §5 định nghĩa `funding_delay = 0 nếu USDT treasury đã đủ`,
nhưng engine **không mô hình hoá treasury USDT**, và `docs/CONVENTIONS.md` #8 chốt quy ước
"ON_DEMAND: mọi zone action đều cần funding" — nên nhánh điều kiện đó không bao giờ được thực thi.

Hệ quả cho remediation: **phần lớn công việc là đặt tên và lưu vết**, không phải viết logic mới.

## Câu hỏi phạm vi phải quyết trước khi bắt đầu

Backtest có cần mô hình hoá treasury USDT để `FUNDING_REQUIRED` có nghĩa không, hay trạng thái đó
chỉ thuộc tầng app?

Câu hỏi này cần một **ADR** và liên quan tới **DEC-005** (phạm vi công cụ trước verdict). Đó là lý
do gói này BLOCKED cho tới khi T-05 chốt DEC-005.

## Đóng finding

- F-006 — Execution State machine không được cài đặt

## Scope

- `docs/adr/` — ADR quyết định phạm vi Execution State
- `src/eth_dca_os/engine.py` — đặt tên, hợp nhất, lưu vết trạng thái đã có
- `src/eth_dca_os/` — sinh `market_snapshots` với `execution_state` nếu ADR quyết định thuộc phạm vi
- `tests/`
- `docs/CONVENTIONS.md`

## Out of Scope

- **Thay đổi hành vi thực thi.** Gói này đặt tên cho hành vi đã có; nó không được làm đổi kết quả
  backtest
- Market Regime — chiều đó thuộc **WP-A3**; hai gói không được cùng định nghĩa lại một chiều
- Partial fill (WP-C3)
- `decision_log` (WP-B3) — WP-B3 **tiêu thụ** enum do gói này định nghĩa
- Sửa V2.1.5 để hợp thức hoá lựa chọn phạm vi; nếu cần thì chuyển sang **WP-D2**

## Dependencies
- T-04 (DONE)
- **T-05 / DEC-005** (DONE) — quyết định phạm vi công cụ trước verdict

## Blocks
- WP-C3
- WP-B3 (phần ngữ nghĩa `previous_state` / `new_state`)
- T-11

## Parallel-Safe With
- WP-C1, WP-C4, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `docs/adr/`
- `src/eth_dca_os/engine.py` — phần đặt tên và lưu trạng thái
- `tests/`, `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py` — Market Regime thuộc WP-A3
- `src/eth_dca_os/capital.py`, `score.py`, `ladders.py`, `verdict.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] C2.1 Viết ADR quyết định phạm vi: backtest có mô hình hoá treasury USDT không
- [ ] C2.2 Đặt tên và lưu sáu trạng thái theo phạm vi đã quyết
- [ ] C2.3 Hợp nhất `Zone.status`, `in_cooldown`, `dq` về một chiều Execution State nhất quán
- [ ] C2.4 Lưu `execution_state` vào snapshot nếu thuộc phạm vi (DM §4 yêu cầu NOT NULL)
- [ ] C2.5 Chứng minh kết quả backtest **không đổi**
- [ ] C2.6 Ghi quy ước vào `docs/CONVENTIONS.md`

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [ ] **DEC-005 đã được chủ dự án quyết định tại T-05.** Chừng nào DEC-005 còn PENDING, gói này là
      `BLOCKED` theo `TASK_READY_GATE_STANDARD.md` (Ready Status: PLANNED / READY / BLOCKED) và
      escalation `MISSING_INPUT` của `ESCALATION_PROTOCOL.md`. **Agent không được tự quyết DEC-005.**
- [ ] **ADR phạm vi Execution State tồn tại và được chủ dự án chấp nhận**
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §16, §19; DM §4, §11; BT §5; Product Spec §6, §11
- [x] Data impact được biết — thêm chiều trạng thái vào snapshot; không đổi dữ liệu thị trường
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

**Ghi chú quan trọng:** việc DEC-005 còn PENDING **không được dùng để chặn lớp A**. RCP-001 và
DEC-007 đã xác định DEC-005 không nằm trên đường găng tới verdict; nó chỉ chặn nhánh T-08 và nhánh
lớp C này.

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được.

### Architecture

#### CHECK-C2-01 — ADR quyết định phạm vi tồn tại và được viện dẫn
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: file ADR trong `docs/adr/` trả lời dứt khoát câu hỏi treasury USDT, nêu phương án đã chọn,
phương án bị loại và lý do. Không có ADR thì gói không được bắt đầu.

Executed By:
...

Timestamp:
...

#### CHECK-C2-02 — Sáu Execution State được đặt tên và lưu vết theo phạm vi đã quyết
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy thật và đọc ra được trạng thái tại từng thời điểm cho các trạng thái thuộc phạm vi.
Với trạng thái ngoài phạm vi (nếu ADR quyết định như vậy), phải có ghi nhận tường minh — không im
lặng bỏ.

Executed By:
...

Timestamp:
...

#### CHECK-C2-03 — `FUNDING_REQUIRED` được xử lý tường minh, không im lặng vắng mặt
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: hoặc (a) trạng thái được mô hình hoá cùng treasury USDT và có test chứng minh nó phát sinh
được; hoặc (b) được tuyên bố `NOT_APPLICABLE` cho tầng backtest, kèm lý do trong ADR và mục trong
`docs/CONVENTIONS.md`, và kèm ghi nhận rằng tầng app vẫn phải có nó theo Product Spec §6/§11.

Executed By:
...

Timestamp:
...

#### CHECK-C2-04 — Market Regime và Execution State được lưu riêng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: Strategy §16 đòi hai chiều độc lập và "phải được lưu riêng". Chứng minh bằng cấu trúc dữ
liệu thật, và chứng minh không gói nào định nghĩa lại chiều của gói kia (ranh giới với WP-A3).

Executed By:
...

Timestamp:
...

#### CHECK-C2-05 — `market_snapshots.execution_state` NOT NULL nếu thuộc phạm vi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: nếu ADR đưa snapshot vào phạm vi, chứng minh trường luôn có giá trị theo DM §4. Nếu ngoài
phạm vi, ghi `NOT_APPLICABLE` kèm lý do — không để trống im lặng.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-C2-06 — Kết quả backtest không đổi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric trước–sau **trùng khớp hoàn toàn**. Đây là ràng buộc định
nghĩa của gói: đặt tên cho hành vi đã có không được làm đổi hành vi. Bất kỳ sai lệch nào là dấu hiệu
gói đã viết logic mới thay vì đặt tên.

Executed By:
...

Timestamp:
...

#### CHECK-C2-07 — Không tạo class `StateMachine` chỉ để khớp tên trong spec
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Yêu cầu: thiết kế được biện minh trong ADR theo tiêu chí "hợp nhất hành vi đã có", không theo tiêu
chí "khớp danh từ trong spec". Đây là check thiết kế, E0 là mức phù hợp — nhưng nó vẫn REQUIRED vì
RCP-001 nêu tường minh.

Executed By:
...

Timestamp:
...

#### CHECK-C2-08 — Toàn bộ test suite PASS
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
- [ ] Mức evidence yêu cầu được thoả
- [ ] ADR tồn tại và được viện dẫn từ file task
- [ ] Kết quả backtest không đổi
- [ ] Enum Execution State sẵn sàng cho WP-B3 và WP-C3 tiêu thụ
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- DEC-005 chưa được chốt → `MISSING_INPUT`, giữ BLOCKED. **Agent không tự quyết DEC-005.**
- Việc đặt tên trạng thái làm đổi kết quả backtest → DỪNG. Đó là dấu hiệu gói đã vượt ra ngoài
  "đặt tên hành vi đã có", `SCOPE_CHANGED`, tính lại routing và phân lớp (có thể phải lên lớp A).
- Mô hình hoá treasury USDT hoá ra đòi đổi Backtest §5 → `CONFLICT DETECTED`, chuyển sang **WP-D2**,
  không vá V2.1.5.
- Sáu trạng thái của spec không phủ hết hành vi thật của engine → ghi nhận khoảng trống, trình chủ
  dự án; không tự thêm trạng thái thứ bảy vào enum của spec.

## Ảnh hưởng nếu gói này thất bại

WP-C3 và phần ngữ nghĩa của WP-B3 không hoàn tất được; T-11 không mở. Khi sang giai đoạn app,
Product Spec §6/§11 đòi hiển thị đúng sáu trạng thái — nếu backtest không mô hình hoá chúng thì live
và backtest sẽ mô tả cùng một tình huống bằng hai ngôn ngữ khác nhau, đúng loại trôi lệch mà
Implementation Plan §1 muốn chặn.

## Changed Files Registry

Created:
- (dự kiến) `docs/adr/ADR-00X-execution-state-scope.md`
- (dự kiến) test mới trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/engine.py`, `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Snapshot mang thêm chiều trạng thái; không có dữ liệu bền cần migrate ở tầng backtest

## Notes

RCP-001 nêu rõ: **không tạo một class `StateMachine` chỉ để khớp tên trong spec**. Việc cần quyết
định trước tiên là phạm vi, và phạm vi cần một ADR. Đây là một trong hai gói trong toàn bộ chương
trình mà quyết định kiến trúc phải có trước khi viết dòng mã đầu tiên.
