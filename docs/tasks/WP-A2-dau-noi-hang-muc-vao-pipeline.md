# WP-A2 — Bật các hạng mục đã viết nhưng pipeline chưa chạy

## Metadata
Status:
READY

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED — MANUAL OVERRIDE (HISTORICAL). Sau MICRO-GOVDEF-001 (2026-08-23), `routing_engine.py` tự
tính đúng Tier C cho các Routing Inputs bên dưới mà không cần override — xem ghi chú cuối trường
`Manual Override` và `Router Raw Output`. Giữ nguyên nhãn MANUAL OVERRIDE để không mất dấu vết
DEC-008, đúng yêu cầu của chủ dự án.

Routing Inputs (all integers 0-4):
D: 2
R: 2
B: 2
A: 1
X: 3
U: 1
V: 3
H: 2
C: 3
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
high

Manual Override:
YES — DEC-008. Router thô **tại thời điểm phê duyệt DEC-008** trả Tier **B** (Sonnet) vì defect
biên dấu phẩy động GOVDEF-001: `model_score` hiển thị `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, nên `tier_from_score` (so sánh `s < 2`) rơi vào nhánh B, trong khi
`AGENT_CAPABILITY_MATRIX.md` quy định 2.00–2.99 → C. Effort `high` là giá trị router tính đúng và
**không** bị override.

**Cập nhật sau MICRO-GOVDEF-001 (2026-08-23):** `routing_engine.py` được sửa để làm tròn `model_score`
về cùng độ chính xác với giá trị hiển thị (3 chữ số thập phân) **trước khi** so sánh với các mốc
Tier, thay vì so sánh trên giá trị dấu phẩy động chưa xử lý sai số. Chạy lại router với đúng các
Routing Inputs bên dưới cho **Tier C tự nhiên**, không cần override nữa — xác nhận đúng
`Can Revisit After` của DEC-008. Trường này được **giữ nguyên, không xoá**, làm dấu vết governance:
Tier C của WP-A2 luôn có căn cứ, dù là qua override (trước fix) hay qua routing tự nhiên (sau fix).

Router Raw Output:
tier=B, model=Sonnet, base_tier=B, model_score=2.0, effort=high, effort_score=2.15,
model_floors=none, effort_floors=none, warnings=none

(Giá trị trên là router THÔ tại thời điểm DEC-008, trước MICRO-GOVDEF-001 — giữ nguyên làm bằng
chứng lịch sử của defect GOVDEF-001. Router hiện tại, sau fix, cho: tier=C, model=Opus,
base_tier=C, model_score=2.0, effort=high, effort_score=2.15 — khớp `Primary Agent Tier`/
`Primary Effort` phía trên mà không cần override.)

Model Routing Score:
2.0

Effort Routing Score:
2.15

Applied Model Floor:
none (Tier C đến từ override DEC-008 trước fix; sau MICRO-GOVDEF-001, Tier C đến từ chính router,
vẫn không qua floor nào — xem `Router Raw Output`)

Applied Effort Floor:
none

Routing Warnings:
none. **Lịch sử:** trước MICRO-GOVDEF-001, cảnh báo ở đây là
`manual_override_dec_008 — validate_routing.py hiện so khớp tuyệt đối với router nên sẽ báo FAIL
cho đúng file này`. Điều đó không còn đúng — `validate_routing.py` nay PASS cho file này (xác nhận
E1, xem Ready Gate). Giữ ghi chú lịch sử để không mất dấu vết.

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Difficulty:
2/4

Risk:
2/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Đấu nối vào pipeline chính những hạng mục **đã được cài đặt đúng nhưng không nơi nào gọi**, để một
official run phát ra báo cáo đầy đủ theo đúng những gì spec ghi là bắt buộc.

Đây là gói **đấu nối**, không phải gói thuật toán. Code của benchmark B/C/D, ablation, volume
z-score, coverage table và XIRR đã được S001 đối chiếu và kết luận là đúng spec khi đọc.

## Vì sao gói này ở lớp A

Chỉ **F-004** bị ràng buộc cứng vào lớp A (Strategy §2: "bắt buộc trong mọi official run") và
**F-014** (bootstrap cần purchase record tại thời điểm chạy, không lưu lại được). F-003, F-012,
F-013 về lý thuyết tính lại được từ dataset đã đóng băng. RCP-001 gộp cả năm vào lớp A vì chúng là
**cùng một sửa đổi trong cùng một file** — tách ra sẽ phải chạm `pipeline.py` hai lần cho cùng một
mục đích. Chủ dự án đã phê duyệt cách gộp này (DEC-007 quyết định 2).

Hệ quả nếu không sửa: nguyên tắc trung tâm của Backtest §22 — "luật đơn giản thắng nếu kết quả
tương đương" — **không thể áp dụng**, vì chiến lược V2.1.5 chỉ được so với Benchmark A.

## Đóng finding / risk

- F-003 — Benchmark B, C, D không bao giờ được gọi
- F-004 — ablation §2.3 và volume z-score §2.4 không được chạy
- F-012 — bảng coverage §4 không được sinh
- F-013 — XIRR §16 không được tính
- F-014 — bootstrap chạy `n_sims=200` thay vì 1000 mỗi block length
- RSK-007 — pipeline không chạy nhiều hạng mục spec ghi là bắt buộc

## Scope

- `src/eth_dca_os/pipeline.py` — lời gọi và truyền tham số
- `src/eth_dca_os/diagnostics.py` — đưa `ablation_scores` và `volume_zscore_variant` vào `run_all`
- `src/eth_dca_os/reporting.py` — payload báo cáo official
- `tests/` — test khẳng định payload official chứa đủ các mục bắt buộc

## Out of Scope

- **Sửa công thức** của bất kỳ benchmark, ablation, coverage, XIRR hay bootstrap nào
- Thêm benchmark mới hoặc đổi định nghĩa benchmark hiện có
- Đổi ngưỡng gate, cách sinh manifest, ngày split, giả định ma sát (Master Index §6)
- Sinh hoặc truyền các đại lượng Failure Signal còn thiếu — đó là **WP-A5**
- Quyết định chính sách verdict khi FS UNKNOWN — đó là **WP-B1**
- Sửa `routing_engine.py` / `validate_routing.py`

## Dependencies
- T-04 (DONE)
- ~~**BLK-003**~~ — **RESOLVED** tại `MICRO-GOVDEF-001` (2026-08-23). `validate_routing.py` được
  cập nhật để (a) làm tròn điểm số như `routing_engine.py` trước khi so sánh biên, và (b) chấp nhận
  manual override có ghi nhận (decision reference tồn tại trong `PROJECT_DECISIONS.md`, Router Raw
  Output xác thực, và chỉ được leo thang Tier/Effort chứ không được hạ). Sau fix, WP-A2 route Tier C
  **tự nhiên**, không cần nhánh override nữa. Rủi ro nền **GOV-RSK-001** đã đóng cùng lúc.
  Bằng chứng: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` (mục Resolution),
  `governance/scripts/governance/test_routing_engine.py`.

## Blocks
- WP-A5 (cần benchmark/diagnostic được chạy để đo đủ dữ liệu)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-A3, WP-C1, WP-D1, WP-D2
- **Không song song với WP-A5**: cả hai sửa `pipeline.py`, nên tuần tự hoá để tránh xung đột merge

## Expected Touch Area

Allowed:
- `src/eth_dca_os/pipeline.py`, `diagnostics.py`, `reporting.py`
- `tests/`

Do not touch without Scope Expansion:
- `src/eth_dca_os/benchmarks.py`, `metrics.py`, `windows.py`, `bootstrap.py` — **chỉ được đọc**;
  nếu phải sửa thân hàm thì gói đã đi ra ngoài phạm vi "đấu nối"
- `src/eth_dca_os/engine.py`, `verdict.py`, `failure_signals.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] A2.1 Gọi `run_benchmark_B`, `run_benchmark_C`, `run_benchmark_D` trong pipeline chính
- [ ] A2.2 Đưa kết quả B/C/D vào payload báo cáo so sánh với chiến lược và với Benchmark A
- [ ] A2.3 Đưa `ablation_scores` (ba model, §2.3) vào `run_all` và vào payload
- [ ] A2.4 Đưa `volume_zscore_variant` (§2.4) vào `run_all`, báo cáo **chênh lệch kết quả**
- [ ] A2.5 Sinh bảng coverage §4 trong mọi báo cáo official
- [ ] A2.6 Tính XIRR §16 và đưa vào payload
- [ ] A2.7 Đặt `n_sims=1000` mỗi block length cho official run
- [ ] A2.8 Viết test khẳng định payload official chứa đủ các mục bắt buộc

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §2, §2.3, §2.4; BT §4, §4.1, §12, §13, §16, §22
- [x] Data impact được biết — không đổi dữ liệu; đổi **nội dung payload báo cáo**
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] **Dependency T-04 DONE** — thoả sau S002
- [x] **BLK-003 được gỡ:** `python governance/scripts/governance/validate_routing.py` PASS —
      xác nhận E1: `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
      override(s))`. WP-A2 route Tier C tự nhiên sau fix, không cần nhánh override.
      **Không hạ Tier WP-A2 về B** — Tier vẫn là C, đúng ràng buộc của DEC-008.
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 2 → REQUIRED check kiểm chứng được ưu tiên E1 ở nơi thực thi được. Vì gói này quyết định
báo cáo official có đủ căn cứ so sánh hay không, toàn bộ REQUIRED check dưới đây đặt ở mức E1.

### Functional

#### CHECK-A2-01 — Benchmark B, C, D thực sự được chạy trong pipeline và có mặt trong payload
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy pipeline đầy đủ trên dữ liệu tổng hợp, in ra payload, chứng minh có kết quả của cả
B, C và D bên cạnh A. Đóng F-003.

Executed By:
...

Timestamp:
...

#### CHECK-A2-02 — Ablation ba model của §2.3 có mặt trong payload official
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: payload chứa đủ ba model ablation, đủ để trả lời "P có đóng góp gì ngoài D không" và
"RSI có đóng góp gì ngoài Return7 không". Đóng F-004 phần ablation.

Executed By:
...

Timestamp:
...

#### CHECK-A2-03 — Diagnostic volume z-score §2.4 được chạy và **chênh lệch kết quả** được báo cáo
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: payload chứa cả kết quả biến thể z-score lẫn **bảng chênh lệch** so với bản gốc — §2.4
đòi "báo cáo chênh lệch kết quả", không chỉ chạy. Đóng F-004 phần volume z-score.

Executed By:
...

Timestamp:
...

#### CHECK-A2-04 — Bảng coverage weight §4 được sinh trong mọi báo cáo official
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: bảng coverage có mặt trong báo cáo, và có mặt **trong mọi** báo cáo official chứ không chỉ
khi bật cờ. Đóng F-012.

Executed By:
...

Timestamp:
...

#### CHECK-A2-05 — XIRR / money-weighted return §16 được tính và có trong payload
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: giá trị XIRR có mặt và được kiểm bằng một ca có đáp số biết trước. Đóng F-013.

Executed By:
...

Timestamp:
...

#### CHECK-A2-06 — Bootstrap chạy 1000 mô phỏng mỗi block length trong official run
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh `n_sims=1000` được dùng cho mỗi block length khi `official` là true, và pipeline
không còn ghi đè xuống 200. Đóng F-014.

Executed By:
...

Timestamp:
...

#### CHECK-A2-07 — Mọi benchmark nhận đúng cùng lịch external contribution
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: equal capital rule được kiểm cho **cả B, C, D**, không chỉ A như hiện nay. Đây là điều kiện
để phép so sánh của BT §22 có nghĩa.

Executed By:
...

Timestamp:
...

### Regression / Scope

#### CHECK-A2-08 — Không công thức nào bị sửa; diff chỉ là đấu nối
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` cho thấy thân hàm của `benchmarks.py`, `metrics.py`, `windows.py`,
`bootstrap.py` không đổi (trừ sửa mặc định `n_sims` nếu chọn cách đó, phải nêu rõ). Nếu một công
thức phải đổi thì gói đã ra ngoài phạm vi → xem Escalation.

Executed By:
...

Timestamp:
...

#### CHECK-A2-09 — Kết quả của chiến lược và Benchmark A không đổi sau khi đấu nối
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric của chiến lược và của Benchmark A trước–sau trùng khớp.
Đấu nối thêm mục báo cáo **không được** làm đổi kết quả đã có.

Executed By:
...

Timestamp:
...

#### CHECK-A2-10 — Toàn bộ test suite Python PASS
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; không test nào bị skip hoặc nới lỏng để gói này đi qua.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [ ] Không công thức nào bị sửa ngoài phạm vi đấu nối
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-007 được cập nhật trạng thái
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- BLK-003 chưa được gỡ khi mở task → `MISSING_INPUT`, giữ BLOCKED. KHÔNG nâng Tier, KHÔNG hạ Tier.
- Đấu nối một hạng mục làm đổi kết quả của chiến lược hoặc Benchmark A → `SCOPE_CHANGED`: dừng, xác
  định nguyên nhân; nếu nguyên nhân là công thức sai thì đó là **finding mới**, không được sửa im
  lặng trong gói đấu nối.
- Một hàm được cho là "đã đúng" hoá ra sai khi chạy thật → mở finding mới, trình chủ dự án qua
  `COMPLETION GATE CHANGE PROPOSAL`; không tự mở rộng gói.
- Bootstrap 1000 × mỗi block length vượt ngân sách thời gian chấp nhận được → `CONFLICT DETECTED`
  giữa BT §13 và ràng buộc vận hành; trình chủ dự án, **không tự hạ xuống 200**.

## Ảnh hưởng nếu gói này thất bại

Official run sẽ phát verdict mà chưa từng đối chiếu chiến lược với ba benchmark đơn giản hơn, không
có ablation, không có chẩn đoán z-score, không có bảng coverage, không có XIRR, và bootstrap dưới
chuẩn. Theo Master Index §6 không được chạy lại official run để bổ sung — nghĩa là **khiếm khuyết
này không sửa được sau khi T-06 đã chạy**. GATE-A không đóng.

## Changed Files Registry

Created:
- Không dự kiến

Modified:
- (dự kiến) `src/eth_dca_os/pipeline.py`, `diagnostics.py`, `reporting.py`
- (dự kiến) `tests/`

Deleted:
- Không

Migration Impact:
- Payload báo cáo mở rộng; không có consumer nào ngoài repo phụ thuộc định dạng này ở thời điểm hiện tại

## Notes

Ghi nhận về routing: Tier C của gói này là **ghi đè thủ công có phê duyệt** (DEC-008), không phải
kết quả router. Việc `validate_routing.py` báo FAIL cho file này là hệ quả đã được DEC-008 dự đoán
trước, không phải một defect mới. Xem `docs/reviews/GOVDEF-001-routing-engine-boundary.md` và
BLK-003. **Không sửa `routing_engine.py` từ bên trong gói này**, và tuyệt đối không hard-code ngoại
lệ riêng cho WP-A2.

Ghi nhận về thứ tự: WP-A2 và WP-A5 cùng sửa `pipeline.py`. Không có phụ thuộc logic hai chiều —
WP-A5 phụ thuộc WP-A2 — nhưng nên tuần tự hoá để tránh xung đột merge.
