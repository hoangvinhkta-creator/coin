# WP-B1 — Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo

## Metadata
Status:
PLANNED

Phase:
Phase 4 — Lớp B: bắt buộc sửa trước verdict

Task Mode:
MAJOR

Lớp (RCP-001):
B — MUST FIX BEFORE VERDICT · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 4
B: 3
A: 4
X: 3
U: 3
V: 3
H: 3
C: 3
F: 4

Routing Categories:
accounting_financial

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.4

Effort Routing Score:
3.25

Applied Model Floor:
cognitive:A>=3&X>=3, safety_business:min_C

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
4/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Chốt **chính sách** ra verdict: khi nào được kết luận BUILD, tín hiệu chưa đo được xử lý ra sao,
ngưỡng số nào là hợp lệ, và điều kiện nào bắt buộc phải chạy lại Gate 1 trước khi kết quả được dùng.

Gói này là **người gác cổng cuối cùng** trước T-07. Nó tồn tại để một verdict thuận lợi không được
phát ra trên nền bằng chứng chưa đủ.

## Ranh giới trách nhiệm

Gói này chịu trách nhiệm **CHÍNH SÁCH VERDICT (verdict policy)**. Việc **ĐO LƯỜNG** ba đại lượng
FS-02 / FS-06 / FS-12 và phạm vi tính FS-03 / FS-07 thuộc **WP-A5** và phải xong trước T-06. Không
trộn hai trách nhiệm; đặc biệt, gói này **không được** giải quyết một FS còn UNKNOWN bằng cách gán
giá trị mặc định.

## Vì sao gói này ở lớp B

`ethdca verdict` đọc lại được `pipeline_state.json`, nên chính sách sửa được **sau** khi official
run đã chạy. Đó là tiêu chí phân lớp B của RCP-001.

**Ngoại lệ đã được ghi nhận:** F-017 (Control F) cần **chạy lại Gate 1**. RCP-001 đã nêu rõ điều
này và chủ dự án đã phê duyệt giữ F-017 ở lớp B **kèm điều kiện DEC-009** — xem CHECK-B1-02.

## Đóng finding / risk

- F-002 — **phần chính sách**: verdict BUILD vẫn phát ra khi FS-02, FS-06, FS-12 là UNKNOWN
- F-015 — ngưỡng FS-02 (`>0.5`), FS-07 (`cash>0.30 và AE<102`), FS-12 (`>0.80`) do triển khai tự đặt
- F-017 — Control F gộp toàn bộ vốn của tháng vào một lệnh, không giữ profile tranche theo tháng
- F-026 — `verdict.py` viện dẫn `docs/CONVENTIONS.md` cho ánh xạ gate-fail → verdict, nhưng file đó
  không có mục nào về verdict
- RSK-005 — quy ước không thuộc spec đang nằm trong đường ra verdict

## Scope

- `src/eth_dca_os/verdict.py` — chính sách và ánh xạ
- `src/eth_dca_os/failure_signals.py` — quy tắc UNKNOWN và ngưỡng
- `src/eth_dca_os/benchmarks.py` — Control F (F-017), Control G (`shift_days`)
- `docs/CONVENTIONS.md` — ghi mọi quy ước không thuộc spec đang nằm trong đường ra verdict
- `tests/` — test chính sách verdict
- Chạy lại Gate 1 nếu DEC-009 kích hoạt

## Out of Scope

- Sinh dữ liệu đo lường Failure Signal (WP-A5)
- **Đổi ngưỡng gate của spec** (BT §7–§10) — cấm bởi Master Index §6
- Chạy lại official run để cải thiện kết quả — Master Index §6 cấm tuyệt đối. Chạy lại Gate 1 theo
  DEC-009 là chạy lại **vì tính hợp lệ**, không phải để cải thiện con số; đây là hai việc khác nhau
  và phải được ghi rõ là khác nhau
- Đọc verdict và quyết định hướng đi (đó là T-07, thẩm quyền chủ dự án)
- Sửa engine, regime, ladder, dữ liệu (lớp A)

## Dependencies
- T-04 (DONE)
- **T-06** (DONE) — official run đã chạy
- Gián tiếp: WP-A5 (dữ liệu đo lường phải tồn tại trong `pipeline_state.json`)

## Blocks
- GATE-B → T-07

## Parallel-Safe With
- WP-B2, WP-B3

## Expected Touch Area

Allowed:
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `benchmarks.py`
- `docs/CONVENTIONS.md`
- `tests/`

Do not touch without Scope Expansion:
- `src/eth_dca_os/gates.py` — ngưỡng gate là điều khoản spec
- `src/eth_dca_os/engine.py`, `regime.py`, `ladders.py`, `capital.py`, `score.py`
- `docs/spec/`, `webapp/`

## Subtasks
- [ ] B1.1 Chốt và cài đặt quy tắc: REQUIRED Failure Signal còn UNKNOWN thì không được BUILD
- [ ] B1.2 Xác định remediation nào ảnh hưởng Gate 1 và áp DEC-009 (xem CHECK-B1-02)
- [ ] B1.3 Sửa Control F giữ đúng kích thước tranche và profile giải ngân theo tháng (F-017)
- [ ] B1.4 Phê chuẩn hoặc thay thế ngưỡng FS-02 / FS-07 / FS-12, có căn cứ ghi lại
- [ ] B1.5 Ghi ánh xạ gate-fail → verdict vào `docs/CONVENTIONS.md`
- [ ] B1.6 Ghi các quy ước còn lại: phạm vi window của FS-03/FS-07, `shift_days=10` của Control G
- [ ] B1.7 Viết test chính sách verdict, gồm ca "đúng một FS là None"
- [ ] B1.8 Tính lại verdict từ `pipeline_state.json` đã lưu và ghi nhận kết quả

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa, và **ranh giới chính sách / đo lường được nêu tường minh**
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency T-06 DONE** — phải có official run thật; không được chạy gói này trên dữ liệu tổng hợp
      để tạo verdict (DEC-003)
- [ ] **WP-A5 DONE** — nếu ba đại lượng FS chưa từng được đo trong official run thì chính sách không
      có gì để áp; khi đó gói này BLOCKED, không được "xử lý" bằng giá trị mặc định
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §12, §16, §17; IM §5, §6, §7; Master Index §6; DEC-009
- [x] Data impact được biết — đổi cách diễn giải kết quả đã lưu, không đổi dữ liệu đã chạy
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 4 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được; category `accounting_financial` và
vai trò gác cổng verdict → **E2 bắt buộc** cho CHECK-B1-09.

### Business Logic / Verdict Policy

#### CHECK-B1-01 — BUILD không được phép khi bất kỳ REQUIRED Failure Signal nào còn UNKNOWN
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: Backtest §17 liệt kê FS-01…FS-12 mà **không đánh dấu mục nào là tuỳ chọn**, nên cả 12 đều
REQUIRED. Test phải dựng một tập FS trong đó **đúng một** signal là `None` và khẳng định verdict trả
về **không phải** `BUILD`, đồng thời `can_proceed_to_app` là `false`. Lặp lại cho mỗi vị trí trong
12 signal, không chỉ cho một vị trí thuận tiện.

Hôm nay `any_true = any(v is True ...)` khiến `None` không kích hoạt cap và verdict BUILD vẫn phát
ra — đây là ca phải thất bại trước khi sửa. Đóng F-002 phần chính sách.

Executed By:
...

Timestamp:
...

#### CHECK-B1-02 — DEC-009: quy tắc Gate 1 staleness được cưỡng chế
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
**Đây là REQUIRED check chính thức hoá DEC-009. Không được hạ xuống RECOMMENDED hay OPTIONAL, không
được biến thành ghi chú, và không được thoả bằng narrative.**

Nội dung phải chứng minh, theo hai bước:

**Bước 1 — Xác định.** Đánh giá tường minh xem remediation của F-017 (Control F) — và bất kỳ
remediation nào khác trong gói này — có thay đổi hoặc **có khả năng ảnh hưởng** một trong các yếu tố
sau hay không:
- input,
- calculation,
- execution behavior,
- dataset interpretation,
- strategy behavior,
- backtest behavior.

Kết luận phải là CÓ hoặc KHÔNG, kèm căn cứ cụ thể (đường mã dùng chung, dữ liệu dùng chung), không
phải phỏng đoán.

**Bước 2 — Hệ quả.** Nếu kết luận là CÓ và thay đổi đó có khả năng ảnh hưởng Gate 1:
- **mọi** kết quả Gate 1 được tạo **trước** remediation phải được đánh dấu `STALE / INVALIDATED`
  trong bản ghi;
- Gate 1 **bắt buộc phải chạy lại**;
- **chỉ kết quả Gate 1 mới** được dùng làm căn cứ cho verdict và cho T-07;
- bằng chứng phải gồm bản ghi lần chạy lại, không chỉ tuyên bố rằng đã chạy lại.

Nếu kết luận là KHÔNG, bằng chứng phải cho thấy **vì sao** đường mã của Control F không giao với
đường mã của Gate 1 — ở mức đủ để một reviewer độc lập kiểm lại được.

Check này FAIL nếu: bước 1 không được thực hiện; hoặc bước 1 kết luận CÓ mà Gate 1 không được chạy
lại; hoặc kết quả Gate 1 cũ vẫn được dùng cho verdict. WP-B1 **không được DONE** khi check này chưa
được chứng minh.

Executed By:
...

Timestamp:
...

#### CHECK-B1-03 — Control F giữ đúng kích thước tranche và profile giải ngân theo tháng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test khẳng định Control F **không** gộp toàn bộ vốn của tháng vào một lệnh tại thời điểm
ngẫu nhiên, mà giữ profile theo tháng như BT §12 yêu cầu. Đóng F-017. Kết quả FS-08 (do Control F
nuôi) phải được tính lại sau khi sửa.

Executed By:
...

Timestamp:
...

#### CHECK-B1-04 — Ngưỡng FS-02 / FS-07 / FS-12 được phê chuẩn hoặc thay thế, có căn cứ ghi lại
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: ba ngưỡng hiện do triển khai tự đặt (`>0.5`, `cash>0.30 và AE<102`, `>0.80`) phải được
(a) phê chuẩn kèm lý do, hoặc (b) thay thế kèm lý do — và trong cả hai trường hợp được ghi vào
`docs/CONVENTIONS.md` như quy ước tuyên bố, truy được về đâu ra. Đóng F-015.

**Ràng buộc:** không được nới ngưỡng theo hướng làm verdict thuận lợi hơn sau khi đã nhìn thấy kết
quả. Nếu ngưỡng cần đổi bản chất thì đó là thay đổi hypothesis và phải đi qua V2.2 (Master Index §6),
không vá tại chỗ.

**Ghi nhận:** việc phê chuẩn ngưỡng có thể cần quyết định của chủ dự án. Nếu chưa có quyết định →
check này là `BLOCKED`, không phải `PASS`.

Executed By:
...

Timestamp:
...

#### CHECK-B1-05 — Ánh xạ gate-fail → verdict được ghi ở `docs/CONVENTIONS.md`
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `docs/CONVENTIONS.md` có mục về verdict, khớp với chính docstring của `verdict.py`. Đóng
F-026. Ánh xạ này là **quy ước triển khai**, không phải điều khoản spec — phải ghi rõ như vậy để
không bị viện dẫn nhầm về sau.

Executed By:
...

Timestamp:
...

#### CHECK-B1-06 — Các quy ước không thuộc spec còn lại trong đường ra verdict được ghi đầy đủ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: ghi phạm vi window dùng để tính FS-03/FS-07 (kết quả của WP-A5) và tham số `shift_days=10`
của Control G. Giảm thiểu RSK-005. Sau gói này, không được còn quy ước nào ảnh hưởng verdict mà
không truy được về một dòng tài liệu.

Executed By:
...

Timestamp:
...

### Stopping Rule Integrity

#### CHECK-B1-07 — Stopping rule không bị nới ở bất kỳ điểm nào
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh bằng test và bằng diff rằng sau gói này:
- `UNKNOWN` không được coi là PASS ở bất kỳ đâu;
- thiếu bằng chứng không được coi là PASS;
- một REQUIRED check `BLOCKED` không cho ra DONE;
- run trên dữ liệu tổng hợp không được dùng thay official run (DEC-003);
- không finding nào bị đổi thành "sai" mà không có bằng chứng bác bỏ;
- không ngưỡng nào bị hạ để verdict trở nên thuận lợi.

Executed By:
...

Timestamp:
...

#### CHECK-B1-08 — Verdict được tính lại từ kết quả đã lưu và kết quả được ghi nhận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy `ethdca verdict` trên `pipeline_state.json` của official run (và trên kết quả Gate 1
mới nếu DEC-009 kích hoạt), ghi lại verdict cuối cùng cùng toàn bộ lý do. Đây là đầu vào của T-07.

Executed By:
...

Timestamp:
...

### Audit độc lập

#### CHECK-B1-09 — Rà soát độc lập E2 cho chính sách verdict và cho kết luận DEC-009
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer độc lập theo "Solo Independent Review Procedure", kiểm lại **đặc biệt**
CHECK-B1-01, CHECK-B1-02 và CHECK-B1-07, coi mọi tuyên bố PASS của người cài đặt là narrative chưa
tin được. Reviewer phải tự trả lời câu hỏi: *có đường nào để một verdict BUILD lọt qua khi bằng
chứng chưa đủ không?* Lưu tại `docs/reviews/`.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-B1-10 — Toàn bộ test suite PASS; không test nào bị skip hoặc nới lỏng
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
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ; E2 cho CHECK-B1-09)
- [ ] **DEC-009 được chứng minh, không chỉ được nhắc tới**
- [ ] Mọi quy ước ảnh hưởng verdict đều truy được về `docs/CONVENTIONS.md`
- [ ] Verdict cuối cùng được ghi nhận kèm toàn bộ lý do
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-005 được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Ngưỡng FS chưa được chủ dự án phê chuẩn → `MISSING_INPUT`, CHECK-B1-04 = `BLOCKED`, gói không DONE.
  KHÔNG tự phê chuẩn thay chủ dự án.
- DEC-009 kích hoạt và việc chạy lại Gate 1 kéo theo phải chạy lại cả Gate 2/3 → `SCOPE_CHANGED`,
  dừng và trình chủ dự án: đó là một vòng lặp lớn hơn về T-06, phải được quyết định chứ không tự làm.
- Phát hiện chính sách đúng đắn sẽ dẫn tới verdict không thuận lợi → **không phải escalation**. Đó là
  gói đang làm đúng việc của nó. Ghi nhận và tiếp tục.
- Muốn chạy lại official run để "làm sạch" số liệu → DỪNG. Master Index §6 cấm. Chỉ chạy lại phần
  bắt buộc theo DEC-009 và ghi rõ lý do là tính hợp lệ.
- Ba Failure Signal vẫn UNKNOWN vì WP-A5 không được thực hiện trước T-06 → `MISSING_INPUT`, BLOCKED.
  Không được gán giá trị mặc định để gỡ bí.

## Ảnh hưởng nếu gói này thất bại

GATE-B không đóng → T-07 (DUYỆT verdict) không mở → T-11 không mở. Nếu bỏ qua: verdict có thể là
BUILD trong khi ba Failure Signal chưa từng được đánh giá và ngưỡng quyết định thì không truy được
về đâu ra. Đó chính là cổng mở đường cho toàn bộ giai đoạn app
(`can_proceed_to_app = (v == "BUILD")`) — mở nhầm cổng này là hỏng ở mức nghiêm trọng nhất mà dự án
có thể hỏng.

## Changed Files Registry

Created:
- (dự kiến) `docs/reviews/E2-WP-B1-*.md`
- (dự kiến) bản ghi Gate 1 chạy lại, nếu DEC-009 kích hoạt

Modified:
- (dự kiến) `src/eth_dca_os/verdict.py`, `failure_signals.py`, `benchmarks.py`
- (dự kiến) `docs/CONVENTIONS.md`, `tests/`

Deleted:
- Không

Migration Impact:
- Nếu DEC-009 kích hoạt: kết quả Gate 1 cũ phải được đánh dấu `STALE / INVALIDATED` **trong bản ghi**,
  không được xoá — dấu vết phải còn để truy lại

## Notes

DEC-009 tồn tại để chặn một tình huống rất cụ thể: verdict được tính trên **hỗn hợp** kết quả Gate 1
sinh bởi code cũ và kết quả Gate 3/controls sinh bởi code mới. Hai nửa đó có thể không tương thích
mà không có gì báo động. Chi phí chấp nhận được (một vòng lặp về T-06) đã được chủ dự án cân nhắc và
phê duyệt.

Lưu ý về sự khác nhau giữa hai loại "chạy lại": Master Index §6 cấm chạy lại official run **để cải
thiện kết quả**. DEC-009 yêu cầu chạy lại Gate 1 **vì kết quả cũ không còn hợp lệ**. Khi ghi nhận,
phải ghi rõ thuộc loại thứ hai, kèm lý do — nếu không, về sau sẽ không phân biệt được.
