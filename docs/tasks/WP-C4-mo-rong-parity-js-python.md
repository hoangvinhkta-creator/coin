# WP-C4 — Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS)

## Metadata
Status:
PLANNED

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
R: 3
B: 2
A: 2
X: 3
U: 2
V: 4
H: 3
C: 3
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.65

Effort Routing Score:
3.0

Applied Model Floor:
safety_business:min_C

Applied Effort Floor:
safety_business:min_high

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
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Mở rộng phạm vi kiểm parity giữa `webapp/engine.js` và `src/eth_dca_os/` từ **chỉ OSCORE tổng** sang
các đại lượng mà hai bản cài đặt có thể trôi khỏi nhau: unlock, spacing, phân bổ ladder, invalidation
price, regime.

## Vì sao gói này tồn tại

Implementation Plan §1 yêu cầu live và backtest dùng chung **một** core strategy function. Trang
tĩnh không chạy được Python, nên `webapp/engine.js` là **bản cài đặt thứ hai** của cùng đặc tả —
`webapp/README.md` thừa nhận công khai.

Cơ chế chặn hiện có là parity OSCORE 40 ngày, lệch tối đa **7,39e-11** — rất tốt **ở đại lượng được
kiểm**. Nhưng nó không phủ những đại lượng nêu trên. Mỗi tính năng port thêm sang JS mở rộng bề mặt
trôi lệch nhanh hơn khả năng phát hiện (RSK-002).

## Vì sao gói này phải đợi lớp A

Phụ thuộc **WP-A3, WP-A4, WP-A6** là bắt buộc: nếu khoá parity bây giờ, nó sẽ khoá vào một hành vi
Python **sắp thay đổi**, và sau lớp A sẽ phải làm lại toàn bộ.

## Đóng finding / risk

- F-008 — live và backtest dùng hai bản cài đặt; parity chỉ phủ OSCORE
- RSK-002 — hai bản cài đặt chiến lược trôi khỏi nhau

## Scope

- Bộ kiểm parity (script/test) và dữ liệu đầu vào cho nó
- `webapp/` — chỉ ở mức đo lường và phơi bày giá trị để so sánh
- `docs/CONVENTIONS.md` — ghi dung sai số học cho từng đại lượng

## Out of Scope

- **Sửa `webapp/engine.js` để khớp Python khi phát hiện lệch** — mọi lệch là **finding**, phải được
  ghi nhận và phân lớp trước khi sửa. Sửa mù để parity xanh là cách chắc chắn nhất để giấu một lỗi
  thật ở phía Python
- Sửa hành vi Python (lớp A)
- Thêm tính năng mới cho JS
- Partial fill (WP-C3) — hành vi này chỉ tồn tại ở tầng sản phẩm, không kỳ vọng parity

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE)
- **WP-A4** (DONE)
- **WP-A6** (DONE)
- **WP-A7** (DONE) — bắt buộc, thêm bởi **RCP-002** (2026-08-24): không đóng băng parity
  JS/Python trên behavior Smart capital đã được xác nhận là sai (F-035).

## Blocks
- T-10
- T-11

## Parallel-Safe With
- WP-C1, WP-C2, WP-C3, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- Bộ kiểm parity và dữ liệu đầu vào của nó
- `webapp/` — chỉ phần phơi bày giá trị để đo
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- Logic chiến lược trong `webapp/engine.js` và `webapp/app_logic.js`
- `src/eth_dca_os/`
- `docs/spec/`

## Subtasks
- [ ] C4.1 Xác định danh sách đầy đủ đại lượng cần parity và dung sai cho từng đại lượng
- [ ] C4.2 Mở rộng bộ kiểm sang unlock
- [ ] C4.3 Mở rộng sang spacing
- [ ] C4.4 Mở rộng sang phân bổ ladder
- [ ] C4.5 Mở rộng sang invalidation price
- [ ] C4.6 Mở rộng sang regime (bao gồm nhãn dẫn xuất sau WP-A3)
- [ ] C4.7 Làm cho bộ kiểm chạy được từ checkout sạch bằng một lệnh
- [ ] C4.8 Làm cho parity FAIL là chặn, không phải cảnh báo
- [ ] C4.9 Ghi nhận mọi lệch phát hiện được thành finding, không tự vá

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa — **đặc biệt: không vá JS để parity xanh**
- [ ] **Dependency WP-A3 DONE**
- [ ] **Dependency WP-A4 DONE**
- [ ] **Dependency WP-A6 DONE**
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — IM §1; ST §4–§18 cho các đại lượng được kiểm
- [x] Data impact được biết — không đổi dữ liệu; đo lường thuần tuý
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3, category `accounting_financial` → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

### Architecture / Parity

#### CHECK-C4-01 — Danh sách đại lượng cần parity đầy đủ và có dung sai tường minh
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: danh sách phủ tối thiểu OSCORE, unlock, spacing, phân bổ ladder, invalidation price,
regime; mỗi đại lượng có **dung sai số học được nêu rõ** (như OSCORE hiện đã có: 7,39e-11). Đại
lượng cố ý không kiểm phải được ghi kèm lý do.

Executed By:
...

Timestamp:
...

#### CHECK-C4-02 — Parity thực sự được kiểm trên từng đại lượng trong danh sách
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output chạy thật cho từng đại lượng, trên chuỗi dữ liệu đủ dài để đi qua nhiều regime, kể
cả CRASH và RECOVERY. Không chấp nhận kiểm trên đoạn dữ liệu êm ả.

Executed By:
...

Timestamp:
...

#### CHECK-C4-03 — Parity khoá vào hành vi Python **sau** WP-A3, WP-A4, WP-A6
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh ba gói phụ thuộc đã DONE, và bộ kiểm chạy trên commit chứa hành vi cuối. Nếu
parity được khoá trước đó thì kết quả vô nghĩa.

Executed By:
...

Timestamp:
...

#### CHECK-C4-04 — Parity chạy được từ bản checkout sạch bằng một lệnh
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: từ clone sạch, một lệnh có trong repo chạy được toàn bộ bộ kiểm. Đây là bài học từ F-027 —
một cơ chế bảo vệ không chạy được từ checkout sạch thì trên thực tế là không tồn tại.

Executed By:
...

Timestamp:
...

#### CHECK-C4-05 — Lệch parity là chặn, không phải cảnh báo
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh bằng một lần thử phá có chủ đích — cố tình làm lệch một đại lượng và khẳng định
bộ kiểm trả về trạng thái thất bại, không phải cảnh báo bỏ qua được.

Executed By:
...

Timestamp:
...

### Governance / Scope

#### CHECK-C4-06 — Mọi lệch phát hiện được ghi thành finding, không tự vá
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh không sửa logic chiến lược ở `webapp/engine.js` / `app_logic.js` và
không sửa `src/eth_dca_os/`. Mỗi lệch phát hiện được có một finding tương ứng, đã phân lớp và có
quyết định xử lý ở gói nào — **kể cả khi nguyên nhân nằm ở phía Python**.

Executed By:
...

Timestamp:
...

#### CHECK-C4-07 — Bộ test hiện có (Python và webapp) đều PASS
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output cả hai bộ test.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Phạm vi parity và dung sai được ghi ở `docs/CONVENTIONS.md`
- [ ] Không logic chiến lược nào bị sửa trong gói này
- [ ] RSK-002 được cập nhật trạng thái
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Phát hiện lệch mà nguyên nhân nằm ở phía **Python** → finding lớp A hoặc B tuỳ ảnh hưởng; nếu nó
  ảnh hưởng official run đã chạy thì `CONFLICT DETECTED` và trình chủ dự án — có thể kích hoạt
  DEC-009 nếu chạm Gate 1.
- Một đại lượng không thể so sánh được vì hai bản dùng biểu diễn khác nhau →
  `VERIFICATION_DEPTH` trước; nếu vẫn không được thì ghi NOT_APPLICABLE kèm lý do kỹ thuật và ghi
  nhận **khoảng trống bảo vệ còn lại**, không im lặng bỏ.
- Muốn sửa JS cho parity xanh → DỪNG. Xem Out of Scope.
- Ba gói phụ thuộc chưa DONE → `MISSING_INPUT`, giữ PLANNED.

## Ảnh hưởng nếu gói này thất bại

T-10 và T-11 không mở. Rủi ro thực chất: mỗi tính năng được port thêm sang JS làm hai bản cài đặt xa
nhau thêm, và cơ chế phát hiện duy nhất chỉ phủ OSCORE tổng. Khi công cụ được dùng thật, app có thể
khuyên một hành động mà backtest chưa từng mô phỏng — mà không ai biết.

## Changed Files Registry

Created:
- (dự kiến) bộ kiểm parity mở rộng

Modified:
- (dự kiến) `webapp/` phần phơi bày giá trị; `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Parity là một cơ chế phòng vệ, và cơ chế phòng vệ chỉ có giá trị bằng phạm vi nó phủ. Con số
7,39e-11 rất đẹp nhưng chỉ nói về OSCORE tổng; nó **không** nói gì về unlock hay phân bổ ladder.
Cám dỗ của gói này là trích dẫn con số đẹp đó như bằng chứng hai bản đồng thuận — đó là điều gói này
tồn tại để chấm dứt.
