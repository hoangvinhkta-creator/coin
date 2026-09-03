# WP-B2 — Bổ sung test cho các yêu cầu đặc tả còn thiếu

## Metadata
Status:
READY — cập nhật tại `DEC-031` (2026-09-03): dependency `T-06 DONE` nay thoả. Mục "Xác nhận
lại toàn bộ Ready Gate khi mở task" còn `[ ]` — thực hiện bởi phiên mở `IN_PROGRESS`.

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
D: 3
R: 2
B: 1
A: 2
X: 3
U: 2
V: 3
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
2.2

Effort Routing Score:
2.55

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
max

Difficulty:
3/4

Risk:
2/4

Blast Radius:
1/4

Project Profile:
PRODUCT

## Objective

Đóng khoảng trống độ phủ test cho những yêu cầu mà Backtest §21 liệt kê là **bắt buộc** nhưng hiện
không có gì kiểm chứng — đặc biệt §21.3, hiện gần như trống.

Mục tiêu không phải là "tăng số test". Mục tiêu là: mỗi requirement §21 hoặc **có test**, hoặc
**được ghi rõ vì sao không thể có test** — không requirement nào rơi vào im lặng.

## Vì sao gói này ở lớp B

Test không đổi kết quả official run đã chạy, nhưng nó quyết định mức tin cậy đặt vào kết quả đó, và
nó là lưới an toàn cho mọi thay đổi sau này (lớp C, T-10, T-11).

## Đóng finding / đề xuất

- R-09 — bổ sung test cho các requirement §19/§21 chưa có test
- Toàn bộ danh sách "Requirement của spec CHƯA CÓ TEST" trong `docs/reviews/S001-audit-findings.md`

Không đóng F-019 (thứ tự 18 bước) — mục đó thuộc **WP-A6** và phải xong trước T-06.

## Scope

- `tests/` — bổ sung test
- `docs/CONVENTIONS.md` — ghi lý do cho các mục NOT_APPLICABLE

## Out of Scope

- **Sửa mã sản phẩm để test đi qua.** Nếu một test mới thất bại, đó là **finding**, không phải lý do
  sửa `src/`. Mở finding và xử lý theo lớp phù hợp
- Test thứ tự 18 bước (WP-A6)
- Test cho partial fill ở tầng engine — không thể có, vì partial fill không phát sinh trong backtest
  (F-020); phần sản phẩm thuộc WP-C3
- Chính sách verdict (WP-B1)

## Dependencies
- T-04 (DONE)
- **T-06** (DONE)

## Blocks
- GATE-B → T-07

## Parallel-Safe With
- WP-B1, WP-B3

## Expected Touch Area

Allowed:
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- Toàn bộ `src/eth_dca_os/` — gói này **chỉ viết test**
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] B2.1 §21.2 — Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và Day 28
- [ ] B2.2 §21.2 — không double reservation giữa Smart / Opportunity / Crash ở tầng engine
- [ ] B2.3 §21.2 — Crash eligible-capital snapshot [F5] đo **sau** cancel/release
- [ ] B2.4 §21.3 — một, hai và ba zone bị xuyên trong cùng một nến; giới hạn tối đa hai zone mỗi cycle
- [ ] B2.5 §21.3 — tie-break §15.1 [F2]; `max_zones` áp sau khi sắp thứ tự
- [ ] B2.6 §21.3 — Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW
- [ ] B2.7 §21.3 — proxy ban đêm tại 07:00 local; TTL; action MISSED
- [ ] B2.8 §21.3 — Crash funding unavailable scenario
- [ ] B2.9 §21.3 — cooldown và override, gồm tần suất override trong CRASH
- [ ] B2.10 §21.3 — chuyển Opportunity ladder sang Crash ladder không tạo double reservation
- [ ] B2.11 §21.3 — [F1] STRESSED không có hiệu ứng execution (test hồi quy thường trực)
- [ ] B2.12 §21.4 — data gap và delayed Base fill
- [ ] B2.13 §21.4 — Benchmark C [F4]: mỗi trigger bắn tối đa một lần mỗi chu kỳ, chu kỳ reset đúng luật
- [ ] B2.14 Ghi nhận các mục NOT_APPLICABLE kèm lý do

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa — **đặc biệt: không sửa `src/` để test đi qua**
- [x] **Dependency T-06 DONE** — `DEC-031` (2026-09-03): official run thật đã chạy, verdict `DO_NOT_BUILD`
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §21.2, §21.3, §21.4
- [x] Data impact được biết — không có
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được (bản chất gói này là chạy test, nên E1 là mức tự nhiên).

### Testing

#### CHECK-B2-01 — §21.2 capital và ladder có test đầy đủ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại và PASS cho — Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và
Day 28; snapshot [F5] đo sau cancel/release.

Executed By:
...

Timestamp:
...

#### CHECK-B2-02 — Không double reservation giữa Smart / Opportunity / Crash được kiểm ở tầng engine
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test phủ cả ca chuyển Opportunity ladder sang Crash ladder. Mệnh đề 3 của Impl Plan §7
hiện **KHÔNG KẾT LUẬN ĐƯỢC** vì không có test nào ở tầng engine; gói này phải đưa nó về kết luận
(nếu WP-A3 chưa đóng phần này).

Executed By:
...

Timestamp:
...

#### CHECK-B2-03 — §21.3 execution: đa zone, giới hạn cycle, tie-break [F2]
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test cho một/hai/ba zone bị xuyên trong cùng nến; tối đa hai zone mỗi cycle; tie-break ba
tầng theo §15.1 và `max_zones` áp **sau** khi sắp thứ tự. Mệnh đề 12 hiện chỉ xác nhận ở tầng code.

Executed By:
...

Timestamp:
...

#### CHECK-B2-04 — §21.3 trigger và proxy: CLOSE/LOW, proxy 07:00, TTL, MISSED
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test cho Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW;
proxy ban đêm tại 07:00 local; TTL hết hạn; action chuyển MISSED.

Executed By:
...

Timestamp:
...

#### CHECK-B2-05 — §21.3 cooldown, override và Crash funding unavailable
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test cho cooldown, override, tần suất override trong CRASH, và kịch bản Crash funding
unavailable.

Executed By:
...

Timestamp:
...

#### CHECK-B2-06 — [F1] STRESSED không có hiệu ứng execution có test hồi quy thường trực
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại lâu dài trong `tests/`, độc lập với test tạm thời của WP-A3. Đây là mệnh đề đã
từng BÁC BỎ; nó cần một lưới an toàn thường trực.

Executed By:
...

Timestamp:
...

#### CHECK-B2-07 — §21.4 data gap, delayed Base fill và Benchmark C [F4]
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test cho data gap và delayed Base fill; và test [F4] cho Benchmark C — mỗi trigger bắn tối
đa một lần mỗi chu kỳ, chu kỳ reset đúng luật. BT §21.4 đòi tường minh test [F4] nhưng hiện chưa có.

Executed By:
...

Timestamp:
...

### Documentation / Integrity

#### CHECK-B2-08 — Mọi requirement §21 không thể test được ghi NOT_APPLICABLE kèm lý do
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: bảng đối chiếu đầy đủ requirement §21 → test tương ứng, hoặc → NOT_APPLICABLE kèm lý do.
Ví dụ đã biết: partial fill giữ phần dư ở RESERVED tới hết TTL — không test được ở tầng backtest vì
partial fill không phát sinh (F-020), thuộc WP-C3; VND → USDT dual cost basis — NOT_APPLICABLE theo
[F6]. **Không mục nào được im lặng bỏ qua.**

Executed By:
...

Timestamp:
...

#### CHECK-B2-09 — Test mới thất bại được ghi thành finding, không được sửa `src/` để đi qua
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh gói này không sửa `src/eth_dca_os/`. Nếu có test mới FAIL, phải tồn
tại finding tương ứng đã được ghi nhận và phân lớp, kèm quyết định xử lý ở gói nào.

Executed By:
...

Timestamp:
...

#### CHECK-B2-10 — Toàn bộ test suite PASS hoặc mọi FAIL đều là finding đã ghi nhận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ. Không test hiện có nào bị skip, xoá hay nới lỏng để nhường chỗ
cho test mới.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Bảng đối chiếu requirement §21 → test/NOT_APPLICABLE hoàn chỉnh
- [ ] Không mã sản phẩm nào bị sửa trong gói này
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Một test mới phát hiện hành vi sai → **không sửa trong gói này**. Mở finding, phân lớp theo tiêu
  chí RCP-001 (ảnh hưởng official run / verdict / productization), trình chủ dự án.
- Một requirement §21 không thể test được nếu không tái cấu trúc `src/` → ghi NOT_APPLICABLE kèm lý
  do kỹ thuật, và mở đề xuất cho gói phù hợp. Không tự tái cấu trúc.
- Số requirement chưa có test vượt khả năng đóng trong một phiên → chia phiên, KHÔNG nâng Tier, và
  KHÔNG đóng gói khi danh sách chưa hết.

## Ảnh hưởng nếu gói này thất bại

GATE-B không đóng → T-07 không mở. Rủi ro dài hạn lớn hơn: mọi thay đổi sau này ở lớp C, T-10, T-11
sẽ không có lưới an toàn cho §21.3 — đúng vùng hành vi phức tạp nhất của engine.

## Changed Files Registry

Created:
- (dự kiến) nhiều file test mới trong `tests/`

Modified:
- (dự kiến) `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Rủi ro đặc trưng của gói viết test cho code đã có: viết test **mô tả hành vi hiện tại** thay vì
**kiểm chứng yêu cầu spec**. Test kiểu đó luôn PASS và không bảo vệ gì cả. Mỗi test ở đây phải bắt
đầu từ một câu trong §21, không phải từ một hàm trong `engine.py`.
