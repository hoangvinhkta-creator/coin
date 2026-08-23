# WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả

## Metadata
Status:
READY

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
D: 1
R: 1
B: 1
A: 1
X: 1
U: 1
V: 1
H: 1
C: 1
F: 1

Routing Categories:
none

Primary Agent Tier:
B

Primary Effort:
medium

Model Routing Score:
1.0

Effort Routing Score:
1.0

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
C

Escalation Effort:
high

Difficulty:
1/4

Risk:
1/4

Blast Radius:
1/4

Project Profile:
PRODUCT

## Ghi chú về Task Mode

Điểm D/R/B đều bằng 1 nên gói này **đủ điều kiện MICRO** theo `TASK_MODE_STANDARD.md`. Vẫn chọn
MAJOR vì: (a) nó gom bốn hạng mục ở ba module khác nhau, (b) hai trong bốn hạng mục chạm mã mà thuật
toán official run phụ thuộc, và (c) ràng buộc định nghĩa của gói — **không được đổi hành vi** — cần
một REQUIRED check có bằng chứng, thứ mà checklist MICRO không bắt buộc. `TASK_MODE_STANDARD.md` cho
phép nâng lên MAJOR; nó chỉ cấm ép MICRO vào khuôn MAJOR khi không cần.

## Objective

Dọn bốn khoản nợ kỹ thuật đã được S001 xác định là **không ảnh hưởng hành vi hiện tại**, để chúng
không trở thành cái bẫy cho người đọc mã hoặc cho một thay đổi trong tương lai.

Ràng buộc định nghĩa của gói: **kết quả mô phỏng không được đổi**. Nếu một hạng mục làm đổi kết quả,
hạng mục đó **không thuộc gói này**.

## Đóng finding

| ID | Nội dung | Vì sao hiện chưa gây hậu quả |
|---|---|---|
| F-028 | `Ladder.expires_at` của Smart ladder đặt `ts + 31 ngày`, không phải cuối accounting month | Trường **không được dùng**; expiry do engine xử lý riêng |
| F-029 | `ladder_completed()` coi `PARTIALLY_FILLED` là trạng thái kết thúc, mâu thuẫn ST §8 | Hàm hiện **không được engine gọi** |
| F-031 | Bộ đếm cooldown override đếm theo **zone**, không theo **sự kiện** override | Chỉ ảnh hưởng số liệu chẩn đoán |
| F-034 | `_noon_candles` chứa nhánh `pass` không tác dụng; hàm cũng không được dùng | Dead code |

## Scope

- `src/eth_dca_os/engine.py` — `expires_at` của Smart ladder; bộ đếm cooldown override
- `src/eth_dca_os/ladders.py` — `ladder_completed()`
- `src/eth_dca_os/benchmarks.py` — xoá `_noon_candles`
- `tests/`

## Out of Scope

- Bất kỳ thay đổi nào làm đổi kết quả mô phỏng
- Partial fill ở tầng sản phẩm (WP-C3) — nhưng ngữ nghĩa "hoàn tất" phải nhất quán với gói đó
- Refactor rộng, đổi tên hàng loạt, dọn dẹp ngoài bốn hạng mục trên
- Sửa các finding lớp A/B/C

## Dependencies
- T-04 (DONE)

Không phụ thuộc gói nào khác. Làm được bất cứ lúc nào.

## Blocks
- Không chặn gì

## Parallel-Safe With
- Toàn bộ gói khác. Lưu ý phối hợp: F-029 chạm ngữ nghĩa mà **WP-C3** cũng dùng

## Expected Touch Area

Allowed:
- `src/eth_dca_os/engine.py`, `ladders.py`, `benchmarks.py` — chỉ bốn hạng mục nêu trên
- `tests/`

Do not touch without Scope Expansion:
- Mọi phần khác của `src/eth_dca_os/`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] D1.1 Sửa hoặc bỏ `expires_at` của Smart ladder để dữ liệu không còn sai nghĩa (F-028)
- [ ] D1.2 Sửa `ladder_completed()` cho khớp ST §8 (F-029)
- [ ] D1.3 Cho bộ đếm cooldown override đếm theo sự kiện (F-031)
- [ ] D1.4 Xoá dead code `_noon_candles` (F-034)
- [ ] D1.5 Chứng minh kết quả mô phỏng không đổi

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency (T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §8; và các quan sát F-028, F-029, F-031, F-034
- [x] Data impact được biết — `expires_at` đổi nghĩa; không có dữ liệu bền cần migrate
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 1 → E0/E1 tuỳ loại check. Nhưng CHECK-D1-05 (không đổi hành vi) là mệnh đề định nghĩa của gói
nên **bắt buộc E1**.

### Functional

#### CHECK-D1-01 — `expires_at` của Smart ladder không còn mang giá trị sai nghĩa
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: hoặc trường mang đúng cuối accounting month, hoặc trường bị bỏ. Trong cả hai trường hợp,
test khẳng định engine vẫn xử lý expiry đúng như trước. Đóng F-028.

Executed By:
...

Timestamp:
...

#### CHECK-D1-02 — `ladder_completed()` khớp Strategy §8
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `PARTIALLY_FILLED` không còn được coi là trạng thái kết thúc; phần chưa fill còn `RESERVED`
tới hết TTL. Test khẳng định trực tiếp. Đóng F-029. Ngữ nghĩa phải nhất quán với WP-C3.

Executed By:
...

Timestamp:
...

#### CHECK-D1-03 — Bộ đếm cooldown override đếm theo sự kiện override
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng ca một sự kiện override tạo action cho nhiều zone, khẳng định bộ đếm tăng đúng
một lần. Đóng F-031. Lưu ý: số liệu chẩn đoán đổi giá trị — điều này **được phép** và phải được ghi
nhận là đổi số liệu, không phải đổi hành vi.

Executed By:
...

Timestamp:
...

#### CHECK-D1-04 — Dead code `_noon_candles` được xoá
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: hàm không còn trong `benchmarks.py`; grep chứng minh không nơi nào gọi nó. Đóng F-034.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-D1-05 — Kết quả mô phỏng không đổi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric của chiến lược và của toàn bộ benchmark trước–sau **trùng khớp
hoàn toàn**. Đây là mệnh đề định nghĩa gói này. Ngoại lệ duy nhất được phép là bộ đếm cooldown
override (CHECK-D1-03) — phải nêu rõ.

Executed By:
...

Timestamp:
...

#### CHECK-D1-06 — Toàn bộ test suite PASS
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
- [ ] Kết quả mô phỏng không đổi, trừ ngoại lệ đã nêu rõ
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Một hạng mục hoá ra **làm đổi kết quả mô phỏng** → `SCOPE_CHANGED`: gỡ hạng mục đó khỏi WP-D1,
  tính lại routing và phân lớp lại theo tiêu chí RCP-001. Nó có thể thuộc lớp A hoặc B. **Không
  được giữ trong gói "không ảnh hưởng hành vi" một hạng mục có ảnh hưởng hành vi.**
- Sửa `ladder_completed()` làm lộ ra rằng hàm **có** được gọi ở đâu đó → dừng, đánh giá lại ảnh
  hưởng; đó là một tình huống khác với giả định của F-029.
- Cám dỗ dọn dẹp thêm ngoài bốn hạng mục → không. `ESCALATION_PROTOCOL.md` cấm refactor không liên
  quan.

## Ảnh hưởng nếu gói này thất bại

Không chặn gì. Rủi ro còn lại là rủi ro dài hạn: dữ liệu sai nghĩa (`expires_at`) và một hàm sai
ngữ nghĩa (`ladder_completed`) đang nằm chờ — nếu một thay đổi tương lai bắt đầu gọi chúng, lỗi sẽ
xuất hiện ở nơi không ai ngờ.

## Changed Files Registry

Created:
- (dự kiến) test nhỏ trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/engine.py`, `ladders.py`, `benchmarks.py`, `tests/`

Deleted:
- (dự kiến) `benchmarks._noon_candles`

Migration Impact:
- Không

## Notes

Gói này rẻ và an toàn, nhưng chính vì thế nó dễ bị làm ẩu. Điểm kiểm soát duy nhất thật sự quan
trọng là CHECK-D1-05: nếu số liệu đổi mà không giải thích được, gói đã làm sai — và vì gói này có
thể chạy song song với mọi thứ khác, một thay đổi hành vi lọt qua đây sẽ rất khó quy trách nhiệm về
sau.
