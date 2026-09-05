# WP-D2 — Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn

## Metadata
Status:
CANCELLED

(`DEC-041` F, 2026-09-05 — nhãn phân loại **`NOT_APPLICABLE_TO_V2_1_5`**. Đầu ra của gói này
là một đề xuất **V2.2 của V2.1.5**. `DEC-040` từ chối mở V2.2, và chỉ thị Owner đi xa hơn: *"Any
future timing/reallocation strategy must be treated as a separate research hypothesis with new
evidence and must not inherit V2.1.5 validation status"* — nghĩa là công việc chiến lược tương
lai KHÔNG phải V2.2 của V2.1.5, nên tiền đề của gói này không còn.
`S-001`/`S-002`/`S-003` KHÔNG bị mất: chúng được **ghi chú kèm** tuyên bố freeze tại `DEC-041` A.
Khiếm khuyết trong một artifact đã đóng băng lịch sử thì được ghi chú, KHÔNG được sửa
(Master Index §6). KHÔNG thực thi.)

Phase:
Phase 6 — Lớp D: hoãn được / tuỳ chọn

Task Mode:
MAJOR

Lớp (RCP-001):
D — DEFERRED / OPTIONAL

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 2
B: 2
A: 4
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
2.7

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
2/4

Project Profile:
PRODUCT

## Objective

Chuẩn bị một **đề xuất** mở V2.2 cho ba khiếm khuyết thuộc về chính bộ đặc tả, đủ chi tiết để chủ
dự án quyết định — và **không sửa V2.1.5**.

Đầu ra của gói này là một tài liệu đề xuất. **Đầu ra không phải là spec mới.** Mở V2.2 là quyết định
của chủ dự án và kéo theo nghĩa vụ chạy lại các gate bắt buộc.

## Ba khiếm khuyết đặc tả

**S-001 — mâu thuẫn nội tại về `score_weights`.**
Backtest §9 (precedence 1) liệt kê `score weights (PL/MS/RV)` là một trong tám chiều bắt buộc của
Gate 2, với năm tuple đăng ký trước. Nhưng Data Model §2 + Section Inventory XC-1 (precedence 3) quy
định [F7]: schema chỉ được có thêm **đúng ba** field metadata. Không thể đồng thời: sinh manifest
Gate 2 đúng 19 ứng viên OFAT **cần** field `score_weights`, nhưng [F7] cấm mọi field ngoài ba
metadata. Implementation chọn thêm field và tự ghi chú mâu thuẫn. Theo Master Index §2, Backtest
thắng — nên lựa chọn của code **đúng precedence**, nhưng vi phạm chữ của [F7]/XC-1.

**S-002 — AE bỏ qua tiền mặt chưa đầu tư.**
Backtest §10.2 định nghĩa `AccumulationEfficiency` là tỷ số ETH. Backtest §12.1 lại yêu cầu "tiền
mặt chưa đầu tư vẫn là một phần của portfolio và không được bỏ qua khi tính giá trị". Benchmark C và
D giữ reserve; Benchmark B có thể không tiêu hết trong tháng ít Thứ Hai. So sánh thuần ETH vì vậy
**có lợi cho chiến lược tiêu hết vốn**. Code làm đúng §10.2.

**S-003 — ngữ nghĩa "có hysteresis" của mode NO_HWM không rõ.**
Strategy §6 mô tả NO_HWM "có hysteresis", nhưng §5 chỉ định nghĩa hysteresis cho Opportunity
(68/62). Không rõ hysteresis nào áp cho Smart. Code trả thẳng `current_unlock`.

## Đóng finding

- S-001, S-002, S-003

## Scope

- Một tài liệu đề xuất V2.2 (vị trí: `PROJECT/` hoặc `docs/reviews/`, thống nhất khi mở task)
- Phân tích precedence theo Master Index §2 cho từng khiếm khuyết
- Phân tích tác động: nếu V2.2 được mở thì gate/run nào phải chạy lại

## Out of Scope

- **Sửa bất kỳ file nào trong `docs/spec/`** — Master Index §6 cấm vá tại chỗ V2.1.5
- Sửa `src/`, `webapp/`, `tests/`
- Tự quyết định mở V2.2 — đó là thẩm quyền chủ dự án
- Thay đổi hành vi code để "phù hợp hơn" với một cách hiểu spec

## Dependencies
- T-04 (DONE)

Không phụ thuộc gói nào khác.

## Blocks
- Không chặn gì. Nhưng nếu chủ dự án quyết định mở V2.2, quyết định đó có thể ảnh hưởng lớp A và lớp B

## Parallel-Safe With
- Toàn bộ gói khác

## Expected Touch Area

Allowed:
- Tài liệu đề xuất mới
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/PROJECT_DECISIONS.md`

Do not touch without Scope Expansion:
- `docs/spec/` — **tuyệt đối không**
- `src/`, `webapp/`, `tests/`

## Subtasks
- [ ] D2.1 Viết phần S-001: mâu thuẫn, precedence, phương án, tác động
- [ ] D2.2 Viết phần S-002: mâu thuẫn, precedence, phương án, tác động
- [ ] D2.3 Viết phần S-003: điểm để ngỏ, phương án, tác động
- [ ] D2.4 Thu nhận các mục do gói khác chuyển sang (WP-A6, WP-C2, WP-C3, WP-A4 có thể chuyển tới)
- [ ] D2.5 Phân tích nghĩa vụ chạy lại gate nếu V2.2 được mở
- [ ] D2.6 Xác nhận `docs/spec/` không bị chạm

## Ready Gate

- [x] Objective rõ ràng — **đầu ra là đề xuất, không phải spec mới**
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency (T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — Master Index §2 (precedence), §6 (freeze rule); BT §9, §10.2,
      §12.1; ST §5, §6; DM §2; XC-1 [F7]
- [x] Data impact được biết — không có
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 2. Gói này sinh ra tài liệu, nên phần lớn check ở mức E0 là phù hợp — trừ CHECK-D2-04 (không
chạm spec), kiểm chứng được bằng công cụ nên đặt E1.

### Documentation

#### CHECK-D2-01 — Ba khiếm khuyết đều có phân tích đầy đủ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Yêu cầu: mỗi mục có đủ — phát biểu mâu thuẫn, điều khoản liên quan kèm precedence theo Master
Index §2, các phương án xử lý, và khuyến nghị kèm lý do. Không mục nào được để ở mức "ghi nhận có
vấn đề".

Executed By:
...

Timestamp:
...

#### CHECK-D2-02 — Nghĩa vụ chạy lại gate được phân tích cho từng phương án
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Yêu cầu: với mỗi phương án, nêu rõ gate nào (Gate 1/2/3) và run nào phải chạy lại nếu được chọn, kể
cả tương tác với **DEC-009**. Đây là thông tin chủ dự án cần để cân nhắc chi phí, và là lý do gói
này không thể chỉ là danh sách vấn đề.

Executed By:
...

Timestamp:
...

#### CHECK-D2-03 — Các mục do gói khác chuyển sang đều được thu nhận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Yêu cầu: WP-A4, WP-A6, WP-C2, WP-C3 đều có escalation trigger "chuyển sang WP-D2 nếu là mâu thuẫn
nội tại của spec". Gói này phải thu nhận mọi mục đã được chuyển tới, hoặc ghi rõ chưa có mục nào.

Executed By:
...

Timestamp:
...

### Governance

#### CHECK-D2-04 — `docs/spec/` không bị sửa
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git status --porcelain` và `git diff` chứng minh không file nào dưới `docs/spec/` bị thay
đổi. Master Index §6 cấm vá tại chỗ V2.1.5.

Executed By:
...

Timestamp:
...

#### CHECK-D2-05 — Tài liệu nêu rõ V2.2 chưa được mở
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Yêu cầu: tài liệu tự khai báo trạng thái là **đề xuất chờ quyết định**, không phải quyết định đã
thông qua. DONE của gói này nghĩa là **đề xuất đã được giao**, không nghĩa là spec đã đổi.

Executed By:
...

Timestamp:
...

#### CHECK-D2-06 — Không mã sản phẩm nào bị sửa
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh `src/`, `webapp/`, `tests/` không bị chạm.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Ba khiếm khuyết đều có phương án và khuyến nghị
- [ ] `docs/spec/` không bị chạm
- [ ] Tài liệu tự khai báo là đề xuất chờ quyết định
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Phát hiện một khiếm khuyết đặc tả **ảnh hưởng tới kết quả official run đã chạy** →
  `CONFLICT DETECTED`, trình chủ dự án ngay; đây không còn là việc hoãn được của lớp D.
- Cám dỗ "sửa một chữ trong spec cho rõ nghĩa" → DỪNG. Master Index §6 cấm tuyệt đối, kể cả sửa nhỏ.
- Một khiếm khuyết hoá ra là **lỗi code chứ không phải lỗi spec** → gỡ khỏi gói này, mở finding và
  phân lớp theo tiêu chí RCP-001.

## Ảnh hưởng nếu gói này thất bại

Không chặn gì trong ngắn hạn. Nhưng ba mâu thuẫn sẽ tiếp tục tồn tại trong nền của mọi quyết định
sau: S-002 đặc biệt đáng lưu ý vì nó **có lợi cho chiến lược** trong phép so sánh với benchmark —
nghĩa là nó có thể làm verdict trông tốt hơn thực tế mà không ai gọi tên được nguyên nhân.

## Changed Files Registry

Created:
- (dự kiến) tài liệu đề xuất V2.2

Modified:
- (dự kiến) `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/PROJECT_DECISIONS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Ghi nhớ ranh giới: S001 đã kết luận rằng ba mục này là **lỗi đặc tả, không phải lỗi code**. Code
hiện đang làm đúng precedence trong cả ba trường hợp. Vì vậy gói này không được biến thành một đợt
sửa code nhân danh "làm cho khớp spec".
