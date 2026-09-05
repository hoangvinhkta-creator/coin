# WP-C3 — Xử lý mua một phần ở tầng sản phẩm

## Metadata
Status:
CANCELLED

(`DEC-041` F, 2026-09-05 — nhãn phân loại **`NOT_APPLICABLE_TO_V2_1_5`**. "Partial fill" là
khái niệm zone/ladder: một zone có `target_vnd` được fill một phần. Dưới hướng sản phẩm L-1
(`DEC-040`) không có zone, không có ladder, không có target per-zone — một giao dịch chỉ là một
giao dịch với số tiền bất kỳ. Completion Gate **vẫn FROZEN 2026-08-23, không bị sửa hay làm
yếu**; nó chỉ không còn đối tượng để áp. Mối lo nghiệp vụ "mua ít hơn kế hoạch" được mô hình
`trades[]` của L-1 hấp thụ tự nhiên, không cần cơ chế riêng.
Ghi chú state: `DEC-036` từng chuyển gói này `BLOCKED → READY` nhưng chỉ áp vào
`PROJECT_PROGRESS.md` và `CAPABILITY_REGISTRY.md`, **sót file task này** — stale `ST-09`, đóng
tại `DEC-041` I. KHÔNG thực thi. KHÔNG tạo task ID thay thế.)

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
X: 2
U: 2
V: 3
H: 2
C: 2
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.5

Effort Routing Score:
2.45

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

Xử lý đúng tình huống **mua một phần** ở tầng sản phẩm: phần đã khớp được ghi sổ, phần chưa khớp giữ
nguyên ở `RESERVED` cho tới hết TTL theo Strategy §8, và bất biến kế toán không bị phá.

## Ghi nhận quan trọng về phạm vi

Trong backtest, fill xảy ra **trọn vẹn** tại execution proxy (Backtest §5), nên partial fill **không
phát sinh được** ở tầng đó. Đây là hiện tượng của **tầng live** (Product §8).

Primitive kế toán ở tầng `Pool` đã có và đã có test. Vì vậy đây là công việc **tầng sản phẩm**,
không phải lỗ hổng của backtest engine — và gói này **không được** thêm partial fill vào backtest để
"cho đủ".

## Đóng finding

- F-020 — partial fill không được cài trong engine: `filled_vnd` khai báo nhưng không bao giờ được
  gán; trạng thái `PARTIALLY_FILLED` không bao giờ phát sinh

Liên quan (không đóng ở đây): F-029 — `ladder_completed()` coi `PARTIALLY_FILLED` là trạng thái kết
thúc, mâu thuẫn ST §8. F-029 thuộc **WP-D1**; hai gói phải nhất quán về ngữ nghĩa "hoàn tất".

## Scope

- Tầng sản phẩm: `webapp/` và/hoặc lớp ghi sổ tương ứng theo phạm vi mà WP-C2 và DEC-005 đã chốt
- `tests/` hoặc bộ test webapp — ca kiểm thử partial fill
- `docs/CONVENTIONS.md`

## Out of Scope

- **Thêm partial fill vào backtest engine** — Backtest §5 quy định fill trọn vẹn tại proxy; thay đổi
  điều đó là thay đổi giả định ma sát, cấm bởi Master Index §6
- Sửa `ladder_completed()` — đó là **WP-D1**
- Định nghĩa Execution State (WP-C2)
- Lớp lưu trữ bền (T-09B)

## Dependencies
- T-04 (DONE)
- **WP-C2** (DONE) — cần trạng thái đã được đặt tên

## Blocks
- T-11

## Parallel-Safe With
- WP-C1, WP-C4, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- Tầng sản phẩm theo phạm vi đã chốt (`webapp/app_logic.js` và lân cận)
- Bộ test tương ứng
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/engine.py`, `execution.py` — hành vi fill của backtest
- `src/eth_dca_os/capital.py` — primitive kế toán đã có và đã có test
- `docs/spec/`

## Subtasks
- [ ] C3.1 Cài đặt gán `filled_vnd` và phát sinh trạng thái `PARTIALLY_FILLED` ở tầng sản phẩm
- [ ] C3.2 Giữ phần chưa khớp ở `RESERVED` tới hết TTL theo ST §8
- [ ] C3.3 Viết ca kiểm thử partial fill, gồm chuỗi nhiều lần khớp một phần
- [ ] C3.4 Kiểm bất biến kế toán qua chuỗi partial fill, trải nhiều tháng
- [ ] C3.5 Chứng minh backtest không đổi
- [ ] C3.6 Ghi ngữ nghĩa "hoàn tất" của ladder vào `docs/CONVENTIONS.md`, nhất quán với WP-D1

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa — **và ranh giới backtest / sản phẩm được nêu tường minh**
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency WP-C2 DONE**
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §8; DM §14; BT §5, §21.2; Product Spec §8
- [x] Data impact được biết — **gói này chạm lớp ghi sổ vốn thật của chủ dự án**; phải có đường xuất
      dữ liệu trước khi thử nghiệm trên dữ liệu thật
- [x] Security impact được biết — không có dữ liệu bên thứ ba
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3, category `accounting_financial` → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

### Functional

#### CHECK-C3-01 — Partial fill phát sinh được và `filled_vnd` được gán đúng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: ca kiểm thử dựng một lệnh khớp một phần, khẳng định trạng thái `PARTIALLY_FILLED` phát sinh
và `filled_vnd` mang đúng giá trị đã khớp. Đóng F-020 ở tầng sản phẩm.

Executed By:
...

Timestamp:
...

#### CHECK-C3-02 — Phần chưa khớp giữ ở `RESERVED` tới hết TTL
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: theo ST §8, phần dư **không** được coi là kết thúc. Ca kiểm thử phải chứng minh phần dư vẫn
ở `RESERVED` cho tới TTL, và chỉ được giải phóng khi TTL hết.

Executed By:
...

Timestamp:
...

### Data Integrity

#### CHECK-C3-03 — Bất biến kế toán giữ đúng qua chuỗi partial fill nhiều tháng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `TOTAL = AVAILABLE + RESERVED + DEPLOYED` giữ đúng qua chuỗi khớp một phần nhiều lần, có
invalidation và release xen kẽ, trải nhiều tháng. Không pool nào âm. Liên kết với kết luận của
WP-C1 về V-01.

Executed By:
...

Timestamp:
...

#### CHECK-C3-04 — Ngữ nghĩa "hoàn tất" của ladder nhất quán giữa WP-C3 và WP-D1
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh không tồn tại hai định nghĩa "ladder đã hoàn tất" khác nhau giữa tầng sản phẩm
và `ladder_completed()` sau khi WP-D1 xử lý F-029. Nếu WP-D1 chưa DONE, ghi rõ ràng buộc và điều
kiện đồng bộ.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-C3-05 — Kết quả backtest không đổi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric trước–sau trùng khớp. Gói này là tầng sản phẩm; backtest không
được chạm.

Executed By:
...

Timestamp:
...

#### CHECK-C3-06 — Bộ test hiện có (Python và webapp) đều PASS
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

### Parity

#### CHECK-C3-07 — Ảnh hưởng tới phạm vi parity được ghi nhận cho WP-C4
Priority:
RECOMMENDED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Khuyến nghị: ghi lại việc partial fill là hành vi chỉ tồn tại ở tầng JS/sản phẩm, để WP-C4 không
kỳ vọng parity ở đại lượng này. Đây là ghi chú thiết kế, E0 là mức phù hợp.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 cho REQUIRED)
- [ ] Backtest không bị chạm
- [ ] Ngữ nghĩa "hoàn tất" nhất quán với WP-D1
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Cảm thấy cần thêm partial fill vào backtest để "cho nhất quán" → DỪNG. Đó là đổi giả định ma sát,
  cấm bởi Master Index §6. Nếu thật sự cần thì mở đề xuất V2.2 qua **WP-D2**.
- Bất biến kế toán bị phá trong một ca partial fill → CRITICAL nếu app đang giữ dữ liệu thật; báo
  chủ dự án ngay.
- WP-C2 chưa DONE → `MISSING_INPUT`, giữ PLANNED.
- Phát hiện ngữ nghĩa TTL của ST §8 mâu thuẫn với hành vi mong muốn ở tầng live →
  `CONFLICT DETECTED`, chuyển sang WP-D2.

## Ảnh hưởng nếu gói này thất bại

T-11 không mở. Ở tầng vận hành: mua một phần là tình huống thật ngoài đời; nếu tầng ghi sổ không xử
lý đúng, sổ vốn của chủ dự án sẽ sai ngay lần đầu gặp tình huống đó — và sai theo hướng khó phát
hiện vì tổng vẫn có thể trông cân.

## Changed Files Registry

Created:
- (dự kiến) ca kiểm thử partial fill

Modified:
- (dự kiến) tầng sản phẩm theo phạm vi đã chốt; `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Bản ghi ladder mang thêm ngữ nghĩa cho `filled_vnd`; dữ liệu cũ (nếu có) phải đọc được với giá trị mặc định

## Notes

Đây là một trong hai gói mà ranh giới "backtest hay sản phẩm" quyết định phần lớn cách làm. S001 đã
chốt: partial fill là hiện tượng tầng live. Nếu trong lúc thực hiện thấy muốn kéo nó xuống backtest,
đó là dấu hiệu phải dừng lại và đọc lại Backtest §5, không phải dấu hiệu spec sai.
