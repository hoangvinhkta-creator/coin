# WP-C1 — Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test

## Metadata
Status:
READY

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION · **ưu tiên cao nhất trong lớp C**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 3
B: 2
A: 1
X: 2
U: 2
V: 3
H: 2
C: 2
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.1

Effort Routing Score:
2.45

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
2/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Đưa ba nghi vấn kế toán của app web từ mức **E0 (nghi vấn)** lên mức **E1 (kết luận có bằng chứng
chạy thật)** — xác nhận hoặc bác bỏ, không để lửng — và khôi phục bộ test webapp sao cho chạy được
**từ một bản checkout sạch**.

## Vì sao gói này được đề nghị ưu tiên cao nhất trong lớp C

Lý do không nằm ở đường găng kỹ thuật mà ở an toàn: nếu chủ dự án đang dùng app để ghi giao dịch
tiền thật, ba nghi vấn này — **nếu đúng** — đang làm sai sổ vốn **ngay lúc này**. Gói này không đụng
`src/`, không cần dữ liệu Binance, không phụ thuộc gói nào khác, nên khởi động được ngay song song
với toàn bộ lớp A.

## Ba nghi vấn phải kết luận

| ID | Nghi vấn | Vị trí | Mức hiện tại |
|---|---|---|---|
| V-01 | Release vốn có thể trả **nhầm pool** khi có nhiều tháng: hàm chọn tháng hiện hành trả về tháng có key lớn nhất, không phải tháng của ladder | `webapp/app_logic.js:124-127,315-320` | E0 |
| V-02 | Mức unlock **không giới hạn** số vốn được reserve; `reserveFor` chỉ kiểm available | `webapp/app_logic.js:289-297` | E0 |
| V-03 | Trạng thái dữ liệu INVALID **không chặn** tạo ladder mới như Strategy §3 yêu cầu | `webapp/app_logic.js:324-335` | E0 |

Đã thu hẹp được một phần (E1, S000): `webapp/test_zone.js` cho thấy bất biến `TOTAL = A + R + D`
giữ đúng **trong kịch bản một tháng**. Điều đó **không bác bỏ V-01**, vì V-01 nói về kịch bản **đa
tháng** — đúng vào điểm mù của test hiện có. V-02 và V-03 chưa có ca kiểm thử nào chạm tới.

## Đóng finding / risk

- V-01, V-02, V-03 — ba nghi vấn kế toán của app web
- F-027 — bộ test webapp không chạy được từ bản checkout sạch
- RSK-003 — xác nhận hoặc bác bỏ
- RSK-004 — xác nhận và khắc phục

**Gỡ BLOCKED cho T-03** khi hoàn tất — nhưng chỉ bằng cách **thoả CHECK-03-01**, tuyệt đối không
bằng cách hạ Completion Gate của T-03 (DEC-007 tác động 6).

## Scope

- `webapp/test_app.js`, `webapp/test_zone.js` và hạ tầng chạy test
- Khôi phục đường tạo `webapp/app_final.html` từ repo
- Khôi phục hoặc sinh lại `demo/results3/live_seed.json` (hiện **không tồn tại ở bất kỳ đâu trong repo**)
- Ca kiểm thử mới cho V-01 (đa tháng), V-02, V-03
- `.gitignore` — chặn ảnh chụp màn hình do test sinh ra
- `webapp/README.md` — hướng dẫn chạy test từ checkout sạch

## Out of Scope

- **Sửa lỗi kế toán nếu nghi vấn được xác nhận** — đó là **T-09A**. Gói này kết luận, không vá
- Thêm tính năng cho app
- Lớp lưu trữ bền (T-09B)
- Mở rộng parity JS ↔ Python (WP-C4)
- Sửa `src/eth_dca_os/`

## Dependencies
- T-01 (DONE)
- T-04 (DONE)

## Blocks
- T-03 (gỡ BLOCKED)
- T-09A (quyết định phạm vi, hoặc CANCELLED nếu cả ba nghi vấn bị bác bỏ)

## Parallel-Safe With
- Toàn bộ lớp A, WP-D1, WP-D2 — gói này độc lập hoàn toàn

## Expected Touch Area

Allowed:
- `webapp/test_app.js`, `webapp/test_zone.js`, `webapp/build_app.js`, `webapp/README.md`
- Ca kiểm thử mới trong `webapp/`
- `demo/` — dữ liệu seed cho test
- `.gitignore`

Do not touch without Scope Expansion:
- `webapp/app_logic.js`, `webapp/engine.js` — **chỉ được đọc**; sửa là T-09A
- `src/eth_dca_os/` — kể cả `live_export.py`
- `docs/spec/`

## Subtasks
- [ ] C1.1 Khôi phục đường dựng `app_final.html` từ repo, không cần thao tác thủ công ngoài repo
- [ ] C1.2 Khôi phục hoặc sinh lại `demo/results3/live_seed.json` bằng một lệnh có trong repo
- [ ] C1.3 Chạy hai test webapp từ bản checkout sạch, ghi lại quy trình
- [ ] C1.4 Dựng ca kiểm thử **đa tháng** cho V-01
- [ ] C1.5 Dựng ca kiểm thử cho V-02 (unlock giới hạn reserve)
- [ ] C1.6 Dựng ca kiểm thử cho V-03 (INVALID chặn tạo action)
- [ ] C1.7 Kiểm bất biến kế toán qua kịch bản đa tháng đầy đủ
- [ ] C1.8 Chặn ảnh chụp màn hình do test sinh ra khỏi repo
- [ ] C1.9 Ghi kết luận E1 cho từng nghi vấn và cập nhật RSK-003, RSK-004

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa — **đặc biệt: không sửa lỗi, chỉ kết luận**
- [x] Dependency (T-01, T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §3; Product Spec §4, §5, §8; và Completion Gate của T-03
- [x] Data impact được biết — **cảnh báo an toàn:** nếu chủ dự án đang có dữ liệu thật trong app,
      phải xuất dữ liệu ra file trước khi chạy bất kỳ thử nghiệm nào chạm localStorage
- [x] Security impact được biết — không có dữ liệu bên thứ ba; không commit dữ liệu tài chính thật
      của chủ dự án vào repo
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3 → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng được. Ba nghi vấn V-01/V-02/V-03
**không được kết luận bằng đọc code** — đó chính là mức E0 mà gói này tồn tại để vượt qua.

### Testing / Harness

#### CHECK-C1-01 — Bộ test webapp chạy được từ bản checkout sạch
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: từ một clone sạch, chạy được cả hai test **chỉ bằng các lệnh có trong repo**, không dựng
thủ công file nào. Bằng chứng gồm chuỗi lệnh và output. Đóng F-027, giảm thiểu RSK-004.

Executed By:
...

Timestamp:
...

#### CHECK-C1-02 — Ảnh chụp màn hình do test sinh ra không làm bẩn repo
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: sau khi chạy test từ trong `webapp/`, `git status --porcelain` không xuất hiện
`app-dash.png` hay `app-zone.png`.

Executed By:
...

Timestamp:
...

### Data Integrity / Verification

#### CHECK-C1-03 — V-01 có kết luận E1 bằng ca kiểm thử đa tháng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: dựng kịch bản có **ít nhất ba tháng** với ladder thuộc tháng **không phải** tháng có key
lớn nhất, thực hiện release, và khẳng định vốn quay về **đúng pool của tháng đó**. Kết luận phải là
XÁC NHẬN hoặc BÁC BỎ, kèm output. Không được ghi "chưa kết luận được" nếu ca kiểm thử dựng được.

Executed By:
...

Timestamp:
...

#### CHECK-C1-04 — V-02 có kết luận E1: mức unlock có giới hạn được số vốn reserve hay không
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: dựng ca cố gắng reserve vượt mức unlock hiện hành trong khi available vẫn còn, khẳng định
hành vi thật. Kết luận XÁC NHẬN hoặc BÁC BỎ kèm output.

Executed By:
...

Timestamp:
...

#### CHECK-C1-05 — V-03 có kết luận E1: INVALID có chặn tạo action mới hay không
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: dựng ca dữ liệu INVALID rồi kích hoạt điều kiện tạo ladder, khẳng định hành vi thật so với
Strategy §3. Kết luận XÁC NHẬN hoặc BÁC BỎ kèm output.

Executed By:
...

Timestamp:
...

#### CHECK-C1-06 — Bất biến kế toán giữ đúng qua kịch bản đa tháng đầy đủ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `TOTAL = AVAILABLE + RESERVED + DEPLOYED` giữ đúng qua chuỗi fill toàn phần → fill một phần
→ invalidation → release, **trải trên nhiều tháng**; không pool nào âm. Test hiện có mới phủ một
tháng.

Executed By:
...

Timestamp:
...

### Scope / Governance

#### CHECK-C1-07 — Không sửa logic app trong gói này
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh `webapp/app_logic.js` và `webapp/engine.js` không bị sửa. Nếu một
nghi vấn được xác nhận, việc sửa thuộc **T-09A**.

Executed By:
...

Timestamp:
...

#### CHECK-C1-08 — Đủ căn cứ để T-03 thoả CHECK-03-01 mà không hạ gate của T-03
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: ba kết luận E1 của CHECK-C1-03/04/05 được ghi vào nơi T-03 viện dẫn được, và
`docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md` được cập nhật trạng thái CHECK-03-01 từ
`BLOCKED` sang `PASS` **dựa trên bằng chứng thật**, không bằng cách sửa nội dung yêu cầu của check.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Ba nghi vấn đều có kết luận dứt khoát — không nghi vấn nào còn ở mức E0
- [ ] Bộ test webapp chạy được từ checkout sạch
- [ ] RSK-003 và RSK-004 được cập nhật trạng thái
- [ ] T-03 được cập nhật trạng thái theo bằng chứng thật
- [ ] Phạm vi T-09A được xác định (hoặc T-09A được đề nghị CANCELLED nếu cả ba bị bác bỏ)
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- **Xác nhận V-01 hoặc V-02 là lỗi thật → báo chủ dự án NGAY trong phiên.** Nếu app đang được dùng
  để ghi tiền thật thì phải dừng dùng hoặc xuất dữ liệu ra ngoài trước khi tiếp tục. Nâng severity
  lên tối thiểu HIGH.
- Không dựng lại được `live_seed.json` vì dữ liệu nguồn đã mất → `MISSING_INPUT`, BLOCKED, ghi rõ
  thiếu gì. Không tự bịa dữ liệu seed rồi coi test là hợp lệ.
- Ca kiểm thử cho một nghi vấn không dựng được vì kiến trúc app → `VERIFICATION_DEPTH` trước; nếu
  vẫn không được thì ghi `BLOCKED` kèm lý do kỹ thuật. **Không ghi PASS, không ghi "bác bỏ".**
- Phát hiện đường mất dữ liệu không có lối thoát → CRITICAL, báo ngay, liên kết RSK-001 và T-09B.

## Ảnh hưởng nếu gói này thất bại

T-03 giữ nguyên BLOCKED. T-09A không xác định được phạm vi. Quan trọng hơn: **rủi ro sai sổ vốn
thật vẫn ở trạng thái chưa biết** — không phải "không có", mà là "chưa ai kiểm". Với một công cụ
đang được dùng để ghi tiền thật, đó là trạng thái tệ nhất trong ba khả năng.

## Changed Files Registry

Created:
- (dự kiến) ca kiểm thử mới trong `webapp/`
- (dự kiến) `demo/results3/live_seed.json` hoặc lệnh sinh ra nó

Modified:
- (dự kiến) `webapp/test_app.js`, `webapp/test_zone.js`, `webapp/build_app.js`, `webapp/README.md`
- (dự kiến) `.gitignore`
- (dự kiến) `docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md` — chỉ cập nhật **trạng thái** của
  CHECK-03-01 kèm bằng chứng; không sửa nội dung yêu cầu

Deleted:
- Không

Migration Impact:
- Không

## Notes

Ghi nhớ nguyên tắc chia việc: gói này **kết luận**, T-09A **sửa**. Trộn hai việc sẽ dẫn tới tình
huống người sửa cũng là người quyết định lỗi có thật hay không — đúng loại thiên lệch mà cả bộ
governance này tồn tại để chặn.

`webapp/test_zone.js` đã chạy được ở S000 và cho kết quả đúng trong kịch bản một tháng. Điều đó là
tin tốt nhưng không phải bằng chứng bác bỏ. Điểm mù của nó — đa tháng — chính là điểm mà V-01 nói
tới.
