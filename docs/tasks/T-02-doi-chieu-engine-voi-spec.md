# T-02 — Đối chiếu engine Python với spec

## Metadata
Status:
PLANNED

Phase:
Phase 1 — Discovery & Baseline

Task Mode:
SPIKE

Chế độ phiên:
AUDIT — READ ONLY

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 4
R: 3
B: 2
A: 2
X: 3
U: 3
V: 3
H: 3
C: 4
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.9

Effort Routing Score:
3.15

Applied Model Floor:
cognitive:D>=4&X>=3, safety_business:min_C

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
4/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Verdict sẽ quyết định chủ dự án có xuống tiền theo chiến lược này hay không. Verdict đó do
engine Python tính ra. Nên câu hỏi phải trả lời là:
**engine có thực sự tính đúng như spec đặc tả không, hay chỉ trông có vẻ đúng?**

Đây là task giảm bất định. Đầu ra là danh sách nonconformance có bằng chứng, không phải bản vá.

## Vì sao task này cần thiết

Toàn bộ code được viết trong 11 commit trước khi governance vào repo. Không tồn tại bằng chứng
tuân thủ nào đã được ghi nhận. `RELEASE_CHECK_V2_1_5.md` chứng minh **spec đầy đủ**, không chứng
minh **code khớp spec** — và chính file đó ghi rằng các con số "sẽ được kiểm lại bằng unit test
của manifest generator và window selector", tức bước xác nhận bằng code vẫn đang để ngỏ.

## Phạm vi ưu tiên theo rủi ro

Không đối chiếu đều tay 26 module. Ưu tiên theo hậu quả nếu sai:

**Tầng 1 — bắt buộc đối chiếu đến từng công thức:**
| Module | Điều khoản | Vì sao ưu tiên cao nhất |
|---|---|---|
| `score.py` | ST §1–4, §11, §13 | OSCORE chi phối toàn bộ unlock và ladder |
| `capital.py` | ST §4–10 | Bất biến kế toán `TOTAL = AVAILABLE + RESERVED + DEPLOYED`, chống double reservation |
| `engine.py` | BT §19 | Thứ tự 18 bước; sai thứ tự là lookahead |
| `manifests.py` | BT §9.1, §10.1 | Con số 219 và 114 là ngưỡng cứng của gate |
| `gates.py` / `verdict.py` | BT §7–10, IM §5–6 | Đường ra verdict |

**Tầng 2 — đối chiếu ở mức hợp đồng và biên:**
`ladders.py` (ST §11–14, §18), `regime.py` (ST §17), `execution.py` (BT §5–6),
`windows.py` (BT §3–4, §8), `metrics.py` (BT §10.2, §11, §16), `failure_signals.py` (BT §17).

**Tầng 3 — chỉ kiểm tồn tại và hợp đồng:**
`indicators.py`, `benchmarks.py`, `diagnostics.py`, `bootstrap.py`, `data/`, `reporting.py`.

## Điểm phải kiểm bắt buộc

Rút từ acceptance criteria của Implementation Plan §7 — đây là những mệnh đề có thể sai âm thầm:

1. **Không lookahead.** Engine chỉ dùng nến đã đóng. Kiểm cả unit lẫn integration.
2. **Không vốn âm** ở bất kỳ pool nào, bất kỳ thời điểm nào.
3. **Không double reservation** giữa Smart / Opportunity / Crash.
4. **Manifest Gate 2 tái lập đúng:** 19 ứng viên OFAT, loại đúng 1, còn 18 hợp lệ,
   mẫu số 219. Phải chạy generator và đếm thật, không đọc tài liệu rồi tin.
5. **Manifest Gate 3 tái lập đúng 114 config** và **không tồn tại config BULK_MONTHLY với
   funding_delay > 0**.
6. **Mọi benchmark nhận đúng cùng lịch external contribution** (equal capital rule).
7. **Benchmark D có reserve cap 6C; Benchmark C theo ngữ nghĩa chu kỳ [F4].**
8. **Cùng hash config/manifest/dataset + cùng seed → tái lập chính xác cùng kết quả.**
9. **Rolling window chồng lấn được gắn nhãn DESCRIPTIVE trong mọi output.**
10. **STRESSED không gây hiệu ứng nào** lên unlock, ladder, cooldown, limit, execution [F1].
11. **Crash ladder [F5]:** cancel Opportunity zone xung đột và release reserve **trước**, rồi
    mới chụp snapshot vốn đủ điều kiện; snapshot bất biến.
12. **Tie-break [F2]** ba tầng khi nhiều zone cùng trigger, và `max_zones` áp **sau** khi sắp
    thứ tự.
13. **Base tranche không bao giờ bị bỏ vì gap dữ liệu [F3].**
14. **DEGRADED không đẩy score lên**, và Opportunity unlock không tăng do đầu vào DEGRADED.

## Scope

Được đọc và chạy:
- Toàn bộ `src/eth_dca_os/`, `tests/`
- Toàn bộ `docs/spec/`, `docs/CONVENTIONS.md`
- Chạy test hiện có, chạy `ethdca freeze` để đếm manifest thật
- Viết script kiểm chứng **tạm thời, ngoài repo** (trong scratchpad) để đếm/đối chiếu

## Out of Scope

- Sửa bất kỳ file nào trong `src/`, `tests/`, `docs/spec/`
- Thêm test vào `tests/` — kể cả test tốt. Đó là remediation, thuộc phase sau
- Chạy `ethdca run` full hoặc `ethdca fetch`
- Soi webapp — đó là T-03
- Đề xuất bản vá cụ thể — ghi `Recommended Fix` ở mức hướng xử lý, không viết code

## Dependencies
- T-01

## Blocks
- T-04

## Parallel-Safe With
- T-03

## Expected Touch Area

Allowed:
- `docs/reviews/S001-audit-findings-engine.md` (tạo mới)
- `PROJECT/PROJECT_PROGRESS.md`

Do not touch without Scope Expansion:
- `src/`, `tests/`, `webapp/`, `docs/spec/`

## Subtasks
- [ ] 02.1 Đối chiếu `score.py` với ST §1–4, §11, §13 tới từng sub-factor và endpoint O0/O4
- [ ] 02.2 Đối chiếu `capital.py` với ST §4–10; kiểm ba bất biến kế toán
- [ ] 02.3 Đối chiếu thứ tự 18 bước của `engine.py` với BT §19, từng bước một
- [ ] 02.4 Chạy manifest generator, **đếm thật** 19/18/219 và 114; kiểm ràng buộc BULK_MONTHLY
- [ ] 02.5 Đối chiếu `gates.py` và `verdict.py` với ngưỡng BT §7–10 và bảng IM §5–6
- [ ] 02.6 Kiểm 14 mệnh đề bắt buộc ở trên, mỗi mệnh đề một kết luận
- [ ] 02.7 Đối chiếu tầng 2 ở mức hợp đồng và biên
- [ ] 02.8 Kiểm tầng 3 chỉ ở mức tồn tại và chữ ký hàm
- [ ] 02.9 Đánh giá độ phủ thật của `tests/`: test nào kiểm hành vi, test nào chỉ kiểm shape
- [ ] 02.10 Ghi nhận mọi quy ước không thuộc spec (đã biết một: ánh xạ gate-fail → verdict
      trong `verdict.py`, xem RSK-005)
- [ ] 02.11 Viết Audit Findings có Severity + Evidence Level cho từng phát hiện

## Ready Gate

- [x] Câu hỏi/ẩn số được nêu rõ
- [x] Learning objective được định nghĩa
- [x] Phạm vi và ưu tiên theo rủi ro được định nghĩa
- [x] Phương pháp thu bằng chứng được định nghĩa
- [x] Định dạng đầu ra được định nghĩa
- [ ] T-01 DONE
- [ ] Xác nhận lại khi mở task

## Completion Gate

### CHECK-02-01 — Năm module tầng 1 đều được đối chiếu tới từng công thức
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Chưa chạy.

### CHECK-02-02 — Con số manifest được đếm thật bằng cách chạy generator
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Chưa chạy. Không được chấp nhận việc đọc `RELEASE_CHECK` rồi ghi PASS — đó là E0.

### CHECK-02-03 — Mười bốn mệnh đề bắt buộc đều có kết luận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Chưa chạy. Mệnh đề không kiểm được phải ghi KHÔNG KẾT LUẬN ĐƯỢC kèm lý do, không được ghi PASS.

### CHECK-02-04 — Độ phủ thật của test suite được định lượng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Chưa chạy.

### CHECK-02-05 — Mọi quy ước không thuộc spec được liệt kê
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E0

Evidence:
Chưa chạy.

### CHECK-02-06 — Không có file mã nguồn nào bị sửa
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Chưa chạy. Kiểm bằng `git status --porcelain`.

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mỗi nonconformance có Severity, Evidence, Evidence Level, Recommended Fix, Suggested Task
- [ ] Mệnh đề không kiểm được được ghi rõ là không kết luận được, không ghi PASS
- [ ] Không có file mã nguồn nào bị sửa
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật

## Escalation Triggers

- Phát hiện nonconformance CRITICAL ở tầng 1 (ví dụ lookahead thật, hoặc double reservation)
  → dừng đối chiếu phần còn lại, báo chủ dự án ngay. Một engine sai ở tầng này thì official run
  là vô nghĩa và T-06 phải hoãn.
- Hai lần đối chiếu khác cách nhau vẫn không kết luận được cùng một điều khoản
  → `CAPABILITY_CEILING`, nâng Tier lên D.
- Spec mâu thuẫn nội bộ → `CONFLICT DETECTED`, áp precedence Master Index §2, không tự chọn.

## Changed Files Registry

Created:
- (dự kiến) `docs/reviews/S001-audit-findings-engine.md`

Modified:
- (dự kiến) `PROJECT/PROJECT_PROGRESS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Cảnh báo phương pháp: cám dỗ lớn nhất của task này là đọc code, thấy tên biến khớp tên trong
spec, rồi kết luận đúng. Tên khớp không phải bằng chứng. Với tầng 1, phải đối chiếu **giá trị
tính ra**, không phải hình thức code.

`docs/CONVENTIONS.md` liệt kê 13 điểm spec cố ý để ngỏ mà engine tự chốt quy ước. Những điểm đó
**không phải nonconformance** — nhưng phải được xác nhận là code thật sự làm đúng quy ước đã
ghi, và phải kiểm xem có quy ước nào đang được dùng mà chưa được ghi vào CONVENTIONS không.
