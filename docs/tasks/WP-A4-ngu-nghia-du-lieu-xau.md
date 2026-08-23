# WP-A4 — Xử lý đúng khi dữ liệu thiếu hoặc hỏng

## Metadata
Status:
PLANNED

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 3
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
2.65

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
3/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Làm cho engine xử lý dữ liệu thiếu hoặc hỏng **đúng theo ngữ nghĩa của spec**, và làm cho mọi bản
ghi bị ảnh hưởng bởi lỗ hổng dữ liệu **tự khai báo điều đó**, thay vì chỉ được đếm ở một bộ đếm tổng.

## Vì sao gói này ở lớp A

Dữ liệu Binance thật **có gap**. Định nghĩa INVALID hiện hẹp hơn spec: code chỉ đặt INVALID khi
**cả 8** sub-factor thiếu, trong khi Strategy §3 nói INVALID khi "giá/lịch sử ETH **hoặc indicator
bắt buộc** không hợp lệ" (F-023). Nghĩa là trên dữ liệu thật, engine sẽ tiếp tục hành động ở những
thời điểm mà spec yêu cầu dừng — và điều đó **đổi hành vi ngay trong official run**, không sửa lại
được sau.

Song song, `EXECUTION_DATA_GAP` không tồn tại trong `src/` (F-025) và `DELAYED_DATA_FILL` chỉ là bộ
đếm, không gắn tag lên purchase record như BT §18 mô tả (F-032). Hệ quả: sau official run không ai
truy được **bản ghi nào** bị ảnh hưởng bởi gap, chỉ biết **có bao nhiêu**.

## Đóng finding

- F-023 — định nghĩa INVALID hẹp hơn Strategy §3
- F-025 — tag `EXECUTION_DATA_GAP` cho nến 15m thiếu không tồn tại
- F-032 — `DELAYED_DATA_FILL` chỉ là bộ đếm, không gắn tag lên purchase record

## Scope

- `src/eth_dca_os/score.py` — định nghĩa INVALID / DEGRADED
- `src/eth_dca_os/engine.py` — gắn tag lên bản ghi, hành vi khi dữ liệu INVALID
- `tests/` — test ngữ nghĩa dữ liệu xấu, test data gap
- `docs/CONVENTIONS.md` — ghi rõ danh sách "indicator bắt buộc" nếu spec để ngỏ

## Out of Scope

- Vòng đời regime và ladder — đó là **WP-A3** (phải xong trước)
- Thứ tự 18 bước — đó là **WP-A6**
- Đo Failure Signal — đó là **WP-A5**
- Sửa nguồn dữ liệu hoặc lấp gap bằng dữ liệu tự sinh
- Đổi công thức OSCORE hay trọng số sub-factor

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE) — tuần tự hoá vì cùng sửa `engine.py`, và vì hành vi khi dữ liệu xấu phải khoá
  vào vòng đời regime đã sửa

## Blocks
- WP-A6 (test thứ tự phải khoá vào hành vi cuối cùng)
- WP-C4 (không khoá parity vào hành vi sắp đổi)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-A2, WP-C1, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `src/eth_dca_os/score.py`, `engine.py`
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `verdict.py`, `failure_signals.py`
- `src/eth_dca_os/data/` — gói này xử lý **ngữ nghĩa** dữ liệu xấu, không xử lý việc **lấy** dữ liệu
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] A4.1 Xác định danh sách "indicator bắt buộc" theo Strategy §3; ghi vào CONVENTIONS nếu spec để ngỏ
- [ ] A4.2 Siết định nghĩa INVALID cho khớp §3: giá/lịch sử ETH **hoặc** indicator bắt buộc không hợp lệ
- [ ] A4.3 Khẳng định INVALID chặn tạo action mới ở tầng engine
- [ ] A4.4 Gắn tag `EXECUTION_DATA_GAP` lên bản ghi bị ảnh hưởng theo BT §18
- [ ] A4.5 Gắn tag `DELAYED_DATA_FILL` lên purchase record, không chỉ đếm
- [ ] A4.6 Viết test cho từng ca dữ liệu xấu, gồm ca biên giữa DEGRADED và INVALID
- [ ] A4.7 Định lượng thay đổi kết quả mô phỏng trên dataset tổng hợp **có gap**

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency WP-A3 DONE** — bắt buộc, không được miễn trừ: hành vi khi dữ liệu xấu phải khoá
      vào vòng đời regime đã sửa, nếu không sẽ phải làm lại
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §3; BT §1, §18
- [x] Data impact được biết — **gói này làm đổi hành vi engine trên dữ liệu có gap**
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

Nguyên tắc bằng chứng riêng của gói này: mọi mệnh đề về hành vi phải được chứng minh trên **dataset
có gap thật sự**, không phải trên dataset sạch rồi suy luận.

### Functional / Data Semantics

#### CHECK-A4-01 — Định nghĩa INVALID khớp Strategy §3, không còn đòi thiếu cả 8 sub-factor
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: bảng ca kiểm thử phủ đủ ba nhóm — (a) giá/lịch sử ETH không hợp lệ, (b) một indicator bắt
buộc không hợp lệ, (c) chỉ các sub-factor không bắt buộc thiếu — và khẳng định trạng thái dữ liệu
trả về đúng INVALID / DEGRADED cho từng nhóm. Đóng F-023.

Executed By:
...

Timestamp:
...

#### CHECK-A4-02 — Dữ liệu INVALID chặn tạo action mới ở tầng engine
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test chạy engine với dữ liệu INVALID tại một thời điểm có trigger, khẳng định **không**
action nào được tạo, theo Strategy §3.

Executed By:
...

Timestamp:
...

#### CHECK-A4-03 — Tag `EXECUTION_DATA_GAP` được gắn lên bản ghi bị ảnh hưởng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy trên dataset có nến 15m thiếu, đọc bản ghi và chứng minh tag có mặt đúng chỗ. Không
chấp nhận "có bộ đếm là đủ". Đóng F-025.

Executed By:
...

Timestamp:
...

#### CHECK-A4-04 — Tag `DELAYED_DATA_FILL` được gắn lên purchase record
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: dựng ca Base fill bị trễ vì gap, chứng minh purchase record mang tag theo BT §18. Đóng
F-032.

Executed By:
...

Timestamp:
...

#### CHECK-A4-05 — [F3] Base tranche không bao giờ bị bỏ vì gap dữ liệu
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test trên dataset có gap khẳng định Base tranche vẫn được giải ngân (khi sang tháng, và ở
Day 25/28). Mệnh đề 13 của Impl Plan §7 hiện mới ở mức "XÁC NHẬN ở tầng code, không có test" — gói
này phải đưa nó lên E1.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-A4-06 — DEGRADED không đẩy score lên; Opportunity unlock không tăng do đầu vào DEGRADED
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: giữ nguyên hành vi đã được S001 xác nhận đúng (mệnh đề 14). Sau khi siết định nghĩa
INVALID, khẳng định lại bằng test rằng ranh giới DEGRADED không bị nới theo hướng có lợi cho
strategy.

Executed By:
...

Timestamp:
...

#### CHECK-A4-07 — Thay đổi kết quả mô phỏng trên dataset có gap được định lượng và giải thích
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed, chạy trước–sau trên dataset **có gap**, so metric, và quy từng sai lệch về một
điều khoản spec. Sai lệch không giải thích được là dấu hiệu defect mới.

Executed By:
...

Timestamp:
...

#### CHECK-A4-08 — Toàn bộ test suite Python PASS; không test nào bị nới lỏng hoặc skip
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; nếu test hiện có phải sửa vì hành vi đổi, nêu rõ test nào và vì
sao hành vi mới đúng spec hơn.

Executed By:
...

Timestamp:
...

### Audit

#### CHECK-A4-09 — Rà soát độc lập E2 cho ngữ nghĩa INVALID
Priority:
RECOMMENDED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Khuyến nghị: một phiên reviewer độc lập kiểm lại bảng ca kiểm thử của CHECK-A4-01, đặc biệt các ca
biên. `EVIDENCE_STANDARD.md` yêu cầu E1 cho Risk 3; E2 ở đây là nâng cao, không phải điều kiện DONE.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ REQUIRED)
- [ ] Danh sách "indicator bắt buộc" được ghi ở nơi tra cứu được
- [ ] Mọi sai lệch kết quả được định lượng và quy về điều khoản spec
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Spec không nói rõ **indicator nào là bắt buộc** → `CONFLICT DETECTED`. Nếu là điểm để ngỏ hợp lệ:
  chốt quy ước và ghi vào `docs/CONVENTIONS.md`. Nếu là mâu thuẫn nội tại của spec: chuyển sang
  **WP-D2**, không vá V2.1.5.
- Siết định nghĩa INVALID làm engine dừng ở phần lớn thời gian trên dữ liệu thật → `SCOPE_CHANGED`:
  dừng, định lượng, trình chủ dự án. Đây có thể là dấu hiệu dữ liệu đầu vào không đủ chất lượng cho
  official run, tức một vấn đề lớn hơn gói này.
- Phải chạm `regime.py` hoặc `capital.py` để đóng gói → `SCOPE_CHANGED`, mở
  `COMPLETION GATE CHANGE PROPOSAL`.
- WP-A3 chưa DONE mà vẫn muốn mở gói → `MISSING_INPUT`, giữ PLANNED.

## Ảnh hưởng nếu gói này thất bại

Mắt xích thứ hai của đường găng. WP-A6 không khởi động được, GATE-A không đóng, T-06 không mở. Nếu
bỏ qua và vẫn chạy official run trên dữ liệu Binance thật (vốn có gap), engine sẽ hành động ở những
thời điểm spec yêu cầu dừng, và không bản ghi nào cho biết bản ghi nào bị ảnh hưởng — official
simulation sai một cách **âm thầm**.

## Changed Files Registry

Created:
- (dự kiến) test mới trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/score.py`, `engine.py`
- (dự kiến) `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Bản ghi mang thêm trường tag; không có dữ liệu bền cần migrate

## Notes

Cạm bẫy: siết định nghĩa INVALID là việc dễ viết nhưng khó chứng minh là **đúng mức**. Quá lỏng thì
lỗi cũ còn nguyên; quá chặt thì engine đứng im trên dữ liệu thật và official run mất ý nghĩa. Đó là
lý do CHECK-A4-01 đòi bảng ca kiểm thử phủ ba nhóm, và CHECK-A4-07 đòi định lượng trên dataset có
gap thật.
