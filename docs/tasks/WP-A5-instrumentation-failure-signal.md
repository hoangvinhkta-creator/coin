# WP-A5 — Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược

## Metadata
Status:
PLANNED

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 3
X: 3
U: 3
V: 3
H: 3
C: 3
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.8

Effort Routing Score:
3.0

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
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Sinh ra **dữ liệu đo lường** mà ba Failure Signal hiện không bao giờ nhận được, và mở rộng phạm vi
tính FS-03/FS-07 ra toàn bộ chín window thay vì chỉ một window đại diện.

## Ranh giới trách nhiệm — đọc trước khi làm

Gói này chịu trách nhiệm **ĐO LƯỜNG (measurement)**. Gói này **KHÔNG** chịu trách nhiệm **CHÍNH SÁCH
VERDICT (verdict policy)**.

| Câu hỏi | Thuộc gói nào |
|---|---|
| Làm sao sinh ra `opportunity_cap_hit_share`, `regime_advantage_share`, `adjacent_config_flip`? | **WP-A5** |
| FS-03/FS-07 tính trên bao nhiêu window? | **WP-A5** |
| UNKNOWN có được phép cho ra BUILD không? | **WP-B1** |
| Ngưỡng số của FS-02/FS-07/FS-12 có hợp lệ không? | **WP-B1** |
| Gate 1 có phải chạy lại sau remediation không (DEC-009)? | **WP-B1** |

Nguyên tắc từ S001 — "không được phép BUILD nếu REQUIRED Failure Signal còn UNKNOWN" — **thuộc
WP-B1**, không thuộc gói này. WP-A5 chỉ có nghĩa vụ làm cho trạng thái UNKNOWN **không còn lý do
tồn tại** vì thiếu đo lường. Không trộn hai trách nhiệm.

## Vì sao gói này ở lớp A

Ba đại lượng này chỉ sinh ra được **khi engine đang chạy**. `ethdca verdict` đọc lại
`pipeline_state.json` nên chính sách sửa được sau; nhưng dữ liệu chưa từng được đo thì không đọc lại
được từ đâu. Đó là tiêu chí phân lớp A của RCP-001.

Phụ thuộc WP-A3 là bắt buộc chứ không phải khuyến nghị: nếu vốn còn bị khoá do F-001 thì FS-02
(cap-hit share) và FS-07 (`avg_cash_ratio`) **đo ra số sai lệch** — đo đúng quy trình nhưng sai bản
chất.

## Đóng finding

- F-002 — **phần đo lường**: ba Failure Signal FS-02, FS-06, FS-12 không bao giờ được truyền input
- F-016 — FS-03 và FS-07 chỉ tính trên một window đại diện (W5), không trên toàn mẫu

Phần chính sách của F-002 thuộc WP-B1.

## Scope

- `src/eth_dca_os/pipeline.py` — sinh và truyền ba đại lượng còn thiếu; mở rộng phạm vi window
- `src/eth_dca_os/engine.py` — chỉ ở mức **thu thập số liệu**, không đổi hành vi thực thi
- `src/eth_dca_os/metrics.py` — tính đại lượng phái sinh nếu cần
- `tests/` — test khẳng định không FS nào còn UNKNOWN vì thiếu input

## Out of Scope

- **Mọi thay đổi trong `verdict.py`** — ngưỡng, ánh xạ, chính sách UNKNOWN đều thuộc WP-B1
- Thay đổi ngưỡng số của FS-02 / FS-07 / FS-12 (WP-B1)
- Thay đổi hành vi thực thi của engine (WP-A3, WP-A4)
- Đấu nối benchmark/chẩn đoán (WP-A2)
- Sửa Control F / Control G (WP-B1)

## Dependencies
- T-04 (DONE)
- **WP-A2** (DONE) — cần các hạng mục đã đấu nối để đo được đầy đủ
- **WP-A3** (DONE) — bắt buộc: vốn không bị khoá thì FS-02/FS-07 mới đo đúng

## Blocks
- GATE-A → T-06
- Gián tiếp: WP-B1 (không có dữ liệu thì chính sách không kiểm chứng được)

## Parallel-Safe With
- WP-A1, WP-C1, WP-D1, WP-D2
- **Không song song với WP-A2**: cả hai sửa `pipeline.py`

## Expected Touch Area

Allowed:
- `src/eth_dca_os/pipeline.py`, `metrics.py`
- `src/eth_dca_os/engine.py` — **chỉ thêm điểm thu thập số liệu**
- `tests/`
- `docs/CONVENTIONS.md` — ghi phạm vi tính của từng FS

Do not touch without Scope Expansion:
- `src/eth_dca_os/verdict.py`, `failure_signals.py` (phần ngưỡng và chính sách), `gates.py`
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `score.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] A5.1 Sinh `opportunity_cap_hit_share` (FS-02) tại thời điểm chạy
- [ ] A5.2 Sinh `regime_advantage_share` (FS-12) tại thời điểm chạy
- [ ] A5.3 Sinh `adjacent_config_flip` (FS-06) tại thời điểm chạy
- [ ] A5.4 Truyền cả ba vào `evaluate_failure_signals`
- [ ] A5.5 Mở rộng tính FS-03 và FS-07 ra toàn bộ chín window
- [ ] A5.6 Ghi rõ phạm vi tính của từng FS vào `docs/CONVENTIONS.md`
- [ ] A5.7 Viết test khẳng định sau khi chạy đầy đủ, không FS nào còn UNKNOWN vì thiếu input
- [ ] A5.8 Chứng minh gói không đụng chính sách verdict (scope guard)

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa, và **ranh giới đo lường / chính sách được nêu tường minh**
- [x] Out-of-scope được định nghĩa
- [ ] **Dependency WP-A2 DONE**
- [ ] **Dependency WP-A3 DONE** — bắt buộc, không miễn trừ
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §16, §17; IM §7
- [x] Data impact được biết — thêm trường đo lường vào `pipeline_state.json`
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

### Functional / Instrumentation

#### CHECK-A5-01 — `opportunity_cap_hit_share` được sinh và truyền vào FS-02
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy pipeline đầy đủ, chứng minh FS-02 nhận giá trị số (không phải `None`). Kèm một ca có
đáp số biết trước để chứng minh đại lượng được **tính đúng**, không chỉ được truyền.

Executed By:
...

Timestamp:
...

#### CHECK-A5-02 — `regime_advantage_share` được sinh và truyền vào FS-12
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: như trên, cho FS-12.

Executed By:
...

Timestamp:
...

#### CHECK-A5-03 — `adjacent_config_flip` được sinh và truyền vào FS-06
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: như trên, cho FS-06.

Executed By:
...

Timestamp:
...

#### CHECK-A5-04 — Sau một run đầy đủ, không Failure Signal nào còn UNKNOWN vì thiếu input
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: in ra trạng thái của cả FS-01…FS-12 sau một run đầy đủ và chứng minh không mục nào là
`None`. Nếu một FS vẫn `None` vì lý do khác (ví dụ dữ liệu đầu vào không đủ dài), lý do đó phải được
ghi rõ và **không được che bằng một giá trị mặc định**.

Executed By:
...

Timestamp:
...

#### CHECK-A5-05 — FS-03 và FS-07 được tính trên toàn bộ chín window
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh phạm vi tính đã mở rộng khỏi W5, và phạm vi mới được ghi tường minh ở
`docs/CONVENTIONS.md`. Đóng F-016 phần đo lường.

Executed By:
...

Timestamp:
...

#### CHECK-A5-06 — Số đo FS-02 và FS-07 không bị bóp méo bởi vốn bị khoá
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh dependency WP-A3 đã thoả bằng một ca chạy kịch bản
CRASH → RECOVERY → STRESSED, khẳng định cap-hit share và cash ratio phản ánh vốn thực sự khả dụng,
không phải vốn bị treo. Đây là lý do WP-A5 phụ thuộc WP-A3.

Executed By:
...

Timestamp:
...

### Scope / Regression

#### CHECK-A5-07 — Gói không thay đổi chính sách verdict
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh không đổi ngưỡng, không đổi ánh xạ gate-fail → verdict, không đổi
quy tắc UNKNOWN trong `verdict.py` / `failure_signals.py`. Nếu gói này vô tình làm verdict đổi kết
quả trên cùng dữ liệu, phải giải thích được rằng nguyên nhân là **dữ liệu đo mới**, không phải chính
sách mới.

Executed By:
...

Timestamp:
...

#### CHECK-A5-08 — Hành vi thực thi của engine không đổi vì việc thêm điểm thu thập số liệu
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, so metric của chiến lược trước–sau. Instrumentation không được làm
đổi hành vi.

Executed By:
...

Timestamp:
...

#### CHECK-A5-09 — Toàn bộ test suite Python PASS
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; không test nào bị skip hoặc nới lỏng.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Phạm vi tính của từng Failure Signal được ghi ở `docs/CONVENTIONS.md`
- [ ] Không quyết định chính sách verdict nào được đưa ra trong gói này
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-007 được cập nhật
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Một trong ba đại lượng không định nghĩa được rõ ràng từ spec → `CONFLICT DETECTED`: chốt quy ước
  và ghi vào `docs/CONVENTIONS.md`, hoặc chuyển sang WP-D2 nếu là khiếm khuyết đặc tả. **Không tự
  sáng tạo định nghĩa rồi im lặng.**
- Muốn "xử lý" một FS còn UNKNOWN bằng cách gán giá trị mặc định → DỪNG. Đó là quyết định chính
  sách, thuộc WP-B1, và mặc định hoá một tín hiệu chưa đo được chính là điều stopping rule tồn tại
  để chặn.
- WP-A3 chưa DONE mà vẫn muốn đo → `MISSING_INPUT`, giữ PLANNED. Số đo sẽ sai.
- Đo lường đòi đổi hành vi engine → `SCOPE_CHANGED`, mở `COMPLETION GATE CHANGE PROPOSAL`.

## Ảnh hưởng nếu gói này thất bại

GATE-A không đóng. Nếu bỏ qua và vẫn chạy official run: ba trong mười hai Failure Signal vĩnh viễn
UNKNOWN trên official run, và dữ liệu để đo chúng **không tồn tại ở đâu để tính lại**. Khi đó WP-B1
sẽ đứng trước lựa chọn giữa một verdict không đầy đủ hoặc chạy lại official run — mà Master Index §6
cấm chạy lại để cải thiện kết quả.

## Changed Files Registry

Created:
- (dự kiến) test mới trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/pipeline.py`, `metrics.py`, `engine.py` (chỉ điểm thu thập)
- (dự kiến) `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- `pipeline_state.json` mang thêm trường; `ethdca verdict` đọc lại được nên WP-B1 sau này không cần chạy lại engine

## Notes

Backtest §17 nói rõ vì sao các Failure Signal quan trọng hơn chính các gate: "chỉ có khoảng ba block
dữ liệu độc lập ... Failure Signal chẩn đoán cơ chế và đáng tin hơn". Bỏ qua 3/12 signal rồi kết
luận BUILD là bỏ đúng phần bằng chứng mà spec coi là mạnh nhất. Gói này tồn tại để phần bằng chứng
đó **có dữ liệu**; việc nó **được dùng thế nào** là WP-B1.
