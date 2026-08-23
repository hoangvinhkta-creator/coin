# WP-A6 — Chốt và kiểm chứng đúng thứ tự các bước tính toán

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
D: 4
R: 3
B: 3
A: 2
X: 3
U: 3
V: 4
H: 3
C: 3
F: 3

Routing Categories:
none

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.1

Effort Routing Score:
3.2

Applied Model Floor:
cognitive:D>=4&X>=3

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
4/4

Risk:
3/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Trả lời dứt khoát câu hỏi: **official run đại diện cho thuật toán nào?**

Backtest §19 quy định 18 bước xử lý theo đúng thứ tự và ghi tường minh: "Mọi implementation phải
tuân thủ đúng thứ tự và **unit-test được thứ tự đó**". Hôm nay **không có test nào** kiểm thứ tự
(F-019), và việc đọc code cho thấy thứ tự thực tế lệch khỏi spec (F-018). Nghĩa là con số official
đang đại diện cho một thuật toán mà **chưa ai xác nhận là thuật toán đã đặc tả**.

## Trình tự bắt buộc của gói này

Thứ tự công việc là một phần của yêu cầu, không phải gợi ý:

1. **Viết test thứ tự TRƯỚC** (đóng F-019) — spec đòi tường minh.
2. **Rồi mới xác định sai lệch hiện tại** một cách chính xác (F-018).
3. **Rồi mới đo** sai lệch đó có làm đổi kết quả hay không, bằng chạy thật.
4. **Rồi mới quyết định** sửa hay ghi nhận là chấp nhận được — kèm bằng chứng.

Đảo thứ tự này sẽ dẫn tới việc viết test khớp với hành vi hiện có thay vì khớp với spec.

## Sai lệch đã biết từ S001 (F-018)

- Bước **15/16/17 không tách riêng** — fill, cập nhật ledger và cooldown nằm chung trong khối bước 12.
- **Tạo ladder chèn giữa bước 12 và 13**, nên ladder mới tham gia trigger ngay trong cùng nến.
- **Fill xảy ra trước** khi vốn khả dụng được đọc để tạo ladder.

Đây mới là quan sát mức E0 (đọc code). Gói này phải nâng nó lên E1.

## Đóng finding

- F-018 — thứ tự xử lý thực tế lệch khỏi Backtest §19
- F-019 — không có test nào kiểm thứ tự 18 bước

## Scope

- `tests/` — test thứ tự 18 bước, test no-lookahead ở tầng 15m
- `src/eth_dca_os/engine.py` — chỉ nếu bước 4 kết luận là phải sửa
- `docs/CONVENTIONS.md` — nếu bước 4 kết luận là ghi nhận sai lệch có chủ đích

## Out of Scope

- Vòng đời regime/ladder (WP-A3), ngữ nghĩa dữ liệu xấu (WP-A4) — cả hai phải xong trước
- Đo Failure Signal (WP-A5)
- Sửa V2.1.5 để hợp thức hoá thứ tự hiện tại — cấm bởi Master Index §6; nếu cần đổi spec thì chuyển
  sang **WP-D2**
- Mở rộng parity sang JS (WP-C4)

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE) — test thứ tự phải khoá vào hành vi cuối cùng
- **WP-A4** (DONE) — như trên

## Blocks
- WP-C4 (parity phải khoá vào hành vi đã chốt)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-C1, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `tests/`
- `src/eth_dca_os/engine.py` — chỉ khi quyết định sửa, và chỉ ở phần thứ tự
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `score.py`, `execution.py`
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `gates.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] A6.1 Viết unit test kiểm thứ tự 18 bước theo BT §19 (làm trước tiên)
- [ ] A6.2 Chạy test đó trên code hiện tại; ghi lại chính xác sai lệch nào lộ ra
- [ ] A6.3 Đo tác động của từng sai lệch lên kết quả bằng chạy thật, không bằng suy luận
- [ ] A6.4 Quyết định sửa hay ghi nhận, kèm bằng chứng cho quyết định
- [ ] A6.5 Nếu sửa: sửa và chạy lại test thứ tự tới khi khoá đúng hành vi cuối
- [ ] A6.6 Nếu ghi nhận: ghi vào `docs/CONVENTIONS.md` và mở mục cho WP-D2 nếu trái spec
- [ ] A6.7 Bổ sung test no-lookahead ở tầng 15m (mệnh đề 1 của Impl Plan §7 hiện chưa kết luận được)

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency WP-A3 DONE**
- [ ] **Dependency WP-A4 DONE**
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §19, §21; IM §7 mệnh đề 1
- [x] Data impact được biết — có thể làm đổi kết quả mô phỏng nếu quyết định là sửa
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3 → E1 bắt buộc. Vì gói này quyết định official run đại diện cho thuật toán nào, CHECK-A6-08
yêu cầu **E2**.

Nguyên tắc bằng chứng riêng của gói này: **không được dùng "đọc code thấy đúng thứ tự" làm bằng
chứng hoàn thành** cho bất kỳ REQUIRED check nào. Spec đòi test, và test là thứ phải tồn tại.

### Testing

#### CHECK-A6-01 — Tồn tại unit test kiểm thứ tự 18 bước và test đó chạy được
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại trong `tests/`, chạy thật, và **kiểm được thứ tự thật của các bước** (ví dụ
bằng cách quan sát trình tự tác dụng phụ), không phải chỉ kiểm sự tồn tại của hàm. Đóng F-019.

Executed By:
...

Timestamp:
...

#### CHECK-A6-02 — Sai lệch thứ tự hiện tại được xác định chính xác ở mức E1
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output của test thứ tự chạy trên code **trước khi sửa**, cho thấy chính xác bước nào lệch.
Ba quan sát E0 của F-018 phải được xác nhận hoặc bác bỏ từng cái một.

Executed By:
...

Timestamp:
...

#### CHECK-A6-03 — Tác động của sai lệch lên kết quả được đo bằng chạy thật
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: so metric giữa thứ tự hiện tại và thứ tự theo spec, trên cùng seed và dataset. Nếu kết luận
là "sai lệch vô hại", kết luận đó phải dựa trên số đo này, **không** dựa trên lập luận.

Executed By:
...

Timestamp:
...

#### CHECK-A6-04 — Quyết định sửa-hay-ghi-nhận được đưa ra và có căn cứ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: quyết định được ghi lại kèm số đo của CHECK-A6-03. Nếu chọn **ghi nhận**: sai lệch phải
được ghi vào `docs/CONVENTIONS.md` như một quy ước được tuyên bố; và nếu nó **trái chữ của BT §19**
thì phải mở mục cho **WP-D2** (đề xuất V2.2), vì Master Index §6 cấm vá tại chỗ V2.1.5. Không được
im lặng chấp nhận.

Executed By:
...

Timestamp:
...

#### CHECK-A6-05 — Sau khi xử lý, test thứ tự PASS và khoá đúng hành vi cuối cùng
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test thứ tự chạy PASS trên code cuối, và test đó **sẽ FAIL** nếu ai đó đổi lại thứ tự —
chứng minh bằng một lần thử phá có chủ đích.

Executed By:
...

Timestamp:
...

#### CHECK-A6-06 — Không lookahead ở tầng 15m
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test khẳng định engine chỉ dùng nến đã đóng ở tầng 15m. Mệnh đề 1 của Impl Plan §7 hiện là
"XÁC NHẬN một phần — không kết luận được cho tầng engine"; gói này phải đưa nó về kết luận.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-A6-07 — Toàn bộ test suite PASS; thay đổi kết quả (nếu có) được định lượng và giải thích
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; nếu quyết định là sửa thứ tự thì so metric trước–sau và quy sai
lệch về đúng bước đã đổi.

Executed By:
...

Timestamp:
...

### Audit độc lập

#### CHECK-A6-08 — Rà soát độc lập E2 cho thứ tự và cho kết luận sửa-hay-ghi-nhận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer độc lập đọc BT §19 từ spec, đối chiếu độc lập với hành vi thật, và tự kết
luận thứ tự có khớp hay không — **không đọc kết luận của người cài đặt trước**. Lưu tại
`docs/reviews/`.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ; E2 cho CHECK-A6-08)
- [ ] Câu hỏi "official run đại diện cho thuật toán nào" có câu trả lời dứt khoát, có bằng chứng
- [ ] Nếu ghi nhận sai lệch: quy ước được ghi và (nếu trái spec) mục đề xuất V2.2 được mở ở WP-D2
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Không dựng được test quan sát thứ tự mà không phải tái cấu trúc lớn `engine.py` →
  `VERIFICATION_DEPTH` trước; nếu vẫn không được thì `SCOPE_CHANGED` và trình chủ dự án. **Không bỏ
  qua yêu cầu test** — BT §19 đòi tường minh.
- Sửa thứ tự làm đổi kết quả đáng kể → DỪNG và trình chủ dự án trước khi nghiệm thu. Đây là thay đổi
  bản chất của thuật toán được đem đi chạy official.
- Sai lệch thứ tự hoá ra là **spec mâu thuẫn với chính nó** → `CONFLICT DETECTED`, chuyển sang WP-D2.
- WP-A3 hoặc WP-A4 chưa DONE → `MISSING_INPUT`, giữ PLANNED. Test viết bây giờ sẽ khoá vào hành vi
  sắp đổi.

## Ảnh hưởng nếu gói này thất bại

Mắt xích cuối trước GATE-A. Nếu thất bại: GATE-A không đóng, T-06 không mở, WP-C4 không khoá được
parity. Nếu bỏ qua và vẫn chạy official run: kết quả official sẽ đại diện cho một thuật toán mà
không ai chứng minh được là thuật toán trong spec — và vì Master Index §6 cấm chạy lại, câu hỏi đó
sẽ **không bao giờ trả lời được** cho lần chạy đó.

## Changed Files Registry

Created:
- (dự kiến) test thứ tự và test no-lookahead trong `tests/`
- (dự kiến) `docs/reviews/E2-WP-A6-*.md`

Modified:
- (dự kiến) `src/eth_dca_os/engine.py` (chỉ nếu quyết định sửa)
- (dự kiến) `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Đây là gói dễ bị "làm cho xong" nhất trong lớp A, vì cám dỗ tự nhiên là viết một test khớp với hành
vi hiện có rồi tuyên bố thứ tự đã được kiểm chứng. Test đó sẽ luôn PASS và không chứng minh gì cả.
Trình tự bắt buộc ở đầu tài liệu tồn tại để chặn đúng điều đó: test phải được viết **từ spec**, chạy
trên code hiện tại, và **được phép thất bại** ở lần chạy đầu tiên.
