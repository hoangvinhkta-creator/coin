# PROJECT PROGRESS

## Project Summary
Project:
ETH DCA Operating System — V2.1.5

Objective:
Xây một công cụ chạy trên trình duyệt, dùng được như bảng tính, để chủ dự án theo dõi quá trình
hold/trade coin và nhận cảnh báo dựa trên các chỉ báo phân tích của bộ spec V2.1.5
(OSCORE, regime, ladder zone, giới hạn thực thi, chất lượng dữ liệu).

Ràng buộc chi phối mục tiêu này: Implementation Plan đặt cổng chặn — app MVP đầy đủ chỉ được
dựng sau khi backtest cho verdict BUILD. Xem `PROJECT/PROJECT_DECISIONS.md` DEC-005.

Project Type:
LEGACY

Profile:
PRODUCT

Last Updated:
2026-08-23 — S003 mở WP-A3 (Ready Gate PASS, chuyển IN_PROGRESS)

Overall Status:
IN_PROGRESS

Current Phase:
Phase 2 — Lớp A (bắt buộc sửa trước official run). WP-A3 là gói đầu tiên được thực thi.

Current Task:
WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp (S003)

Current Task Mode:
MAJOR

Next Recommended Task:
Chủ dự án chọn một trong các task đã ở trạng thái READY: **WP-A3** (khuyến nghị — mắt xích đầu
tiên của đường găng), WP-A1, **WP-A2** (nay READY, Tier C tự nhiên sau MICRO-GOVDEF-001), WP-C1
(khuyến nghị vì lý do an toàn dữ liệu thật), WP-D1, WP-D2.
KHÔNG tự mở — agent dừng sau MICRO-GOVDEF-001 theo chỉ thị của chủ dự án.

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính, **trừ một ngoại lệ có ghi nhận rõ ràng**: WP-A2 dùng Tier ghi đè thủ
công (C thay vì B do router trả) theo phê duyệt của chủ dự án — xem DEC-008 và
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`. Bằng chứng routing của từng task nằm trong
file task tương ứng dưới `docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối
tài liệu này.

Roadmap này áp dụng **RCP-001** (`PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`), được chủ dự án phê
duyệt ngày 2026-08-23 kèm bốn điều kiện — xem mục "Roadmap Change Applied" bên dưới.

**Cập nhật S002:** 15 work package không còn là roadmap sơ bộ. Mỗi gói đã có file định nghĩa task
đầy đủ dưới `docs/tasks/`, với Ready Gate, Completion Gate (REQUIRED checks + Evidence Level),
Exit Criteria và Escalation Triggers **đã đóng băng** ngày 2026-08-23. Theo
`TASK_COMPLETION_GATE_STANDARD.md` mục "After Freeze", agent **không được xoá hoặc làm yếu REQUIRED
check** để task đi qua; mọi thay đổi phải dùng khối `COMPLETION GATE CHANGE PROPOSAL`.
Bản đối chiếu độ phủ: `docs/reviews/S002-coverage-regression-check.md`.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| DONE | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| BLOCKED | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. Chuyển DONE khi WP-C1 hoàn tất và ba nghi vấn có kết luận E1 |
| DONE | T-04 | Chốt lộ trình và đóng băng tiêu chí | Soạn Ready Gate + Completion Gate cho 15 work package của RCP-001, đóng băng trước khi thực thi | C | xhigh | Sau T-01, T-02, T-03. HOÀN TẤT tại S002 — 15 file task đã đóng băng gate |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. KHÔNG nằm trên đường găng tới verdict (RCP-001) — chỉ chặn T-08 và WP-C2 |
| READY | WP-A1 | Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, đúng môi trường, và tái lập lại được | C | xhigh | Sau T-04. Song song với WP-A2, WP-A3, WP-C1. Thay thế T-06A cũ (đóng F-005, F-007, F-009, F-010, F-011) |
| READY | WP-A2 | Bật các hạng mục đã viết nhưng pipeline chưa chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có, dù code đã đúng | C | high | Sau T-04 (DONE). Song song với WP-A1, WP-A3 (đóng F-003, F-004, F-012, F-013, F-014). Tier C nay route tự nhiên sau MICRO-GOVDEF-001 (trước đó là ghi đè theo DEC-008) — xem GOVDEF-001 mục Resolution |
| VERIFYING | WP-A3 | Sửa vòng đời trạng thái thị trường và ladder khẩn cấp | Vốn có thể bị khoá vĩnh viễn khi thị trường hồi phục một phần rồi yếu lại | D | max | Sau T-04. Song song với WP-A1, WP-A2, WP-C1 (đóng F-001, F-021, F-022, F-030) |
| PLANNED | WP-A4 | Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu Binance thật có lỗ hổng; xử lý sai sẽ làm sai kết quả mô phỏng | C | xhigh | Sau WP-A3 (đóng F-023, F-025, F-032) |
| PLANNED | WP-A5 | Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược | Ba tín hiệu hiện không bao giờ được đo dù vẫn cho ra kết luận cuối cùng | C | xhigh | Sau WP-A2, WP-A3 (vốn không bị khoá thì số đo mới đúng) — đóng phần đo lường của F-002, và F-016 |
| PLANNED | WP-A6 | Chốt và kiểm chứng đúng thứ tự các bước tính toán | Thứ tự sai nghĩa là con số chính thức không đại diện đúng cho chiến lược đã đặc tả | D | max | Sau WP-A3, WP-A4 (đóng F-018, F-019) |
| PLANNED | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | Sau T-05 và **GATE-A** (WP-A1…WP-A6 đều DONE). Cần máy/VPS có mạng Binance — BLK-001 chặn đúng tại đây |
| PLANNED | WP-B1 | Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo | Không cho phép kết luận thuận lợi khi vẫn còn tín hiệu cảnh báo chưa đo được | D | max | Sau T-06. QUY TẮC BẮT BUỘC: nếu remediation của F-017 (Control F) ảnh hưởng Gate 1 → Gate 1 phải chạy lại trước khi coi kết quả hợp lệ (DEC-009) — đóng phần chính sách của F-002, F-015, F-017, F-026 |
| PLANNED | WP-B2 | Bổ sung test cho các yêu cầu đặc tả còn thiếu | Nhiều yêu cầu của BT §21 hiện không có gì kiểm chứng | C | xhigh | Sau T-06. Song song với WP-B1, WP-B3 |
| PLANNED | WP-B3 | Hoàn thiện nhật ký quyết định để truy vết được | Cần truy vết được vì sao hệ thống ra quyết định như vậy tại từng thời điểm | C | high | Sau T-06. Song song với WP-B1, WP-B2. Ngữ nghĩa `previous_state/new_state` phụ thuộc WP-C2 (đóng F-024, F-033) |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | Sau T-06 và **GATE-B** (WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE). Chặn T-11 |
| READY | WP-C1 | Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test | App đang có thể dùng để ghi tiền thật; ba nghi vấn về sai sổ vẫn chưa có kết luận | C | xhigh | Sau T-01 (đã DONE). Độc lập hoàn toàn — có thể chạy ngay, song song với toàn bộ lớp A. Gỡ BLOCKED cho T-03 khi xong (đóng V-01, V-02, V-03, F-027) |
| BLOCKED | WP-C2 | Làm rõ và đặt tên trạng thái thực thi của hệ thống | Cần biết rõ hệ thống đang ở trạng thái nào trước khi đưa vào dùng thật | C | xhigh | Sau T-05 (DEC-005 còn PENDING → BLOCKED). Cần ADR quyết định phạm vi trước khi bắt đầu (đóng F-006) |
| PLANNED | WP-C3 | Xử lý mua một phần ở tầng sản phẩm | Mua một phần là tình huống thật ngoài đời, tầng ghi sổ hiện chưa xử lý đúng | C | xhigh | Sau WP-C2 (đóng F-020) |
| PLANNED | WP-C4 | Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS) | Hai bản cài đặt có thể trôi khỏi nhau khi thêm tính năng mới vào JS | C | xhigh | Sau WP-A3, WP-A4, WP-A6 (không khoá parity vào hành vi sắp đổi). Chặn T-10, T-11 (đóng F-008) |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05 |
| PLANNED | T-09A | Sửa lỗi kế toán trong app web | Vá lỗi nếu WP-C1 xác nhận là có thật, trước khi app được dùng với tiền thật | C | high | Sau WP-C1. Nếu WP-C1 bác bỏ cả ba nghi vấn, T-09A có thể thu hẹp phạm vi hoặc CANCELLED |
| PLANNED | T-09B | Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | Sau T-04. Nên làm trước T-10 |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08, T-09B, WP-C4 |
| READY | WP-D1 | Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả | Dọn cho sạch, không ảnh hưởng gì tới kết quả hiện tại | B | medium | Không phụ thuộc, làm bất cứ lúc nào (đóng F-028, F-029, F-031, F-034) |
| READY | WP-D2 | Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn | Một số mâu thuẫn thuộc về chính bộ đặc tả, cần chủ dự án quyết định mở V2.2 | C | xhigh | Không phụ thuộc. Đầu ra là đề xuất, KHÔNG sửa V2.1.5 (đóng S-001, S-002, S-003) |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07, WP-C2, WP-C3, WP-C4, và chỉ khi verdict = BUILD |

## Roadmap Change Applied — RCP-001

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` ngày 2026-08-23 kèm bốn quyết định.
Toàn bộ bốn quyết định đã được phản ánh vào bảng roadmap chuẩn ở trên. Chi tiết đầy đủ ghi ở
`PROJECT/PROJECT_DECISIONS.md` DEC-007, DEC-008, DEC-009.

1. **Cấu trúc 15 work package** — APPROVED nguyên trạng.
2. **Phân lớp A/B/C/D** — APPROVED WITH CONDITION: nếu remediation của F-017 (nằm trong WP-B1)
   ảnh hưởng tới input/calculation/execution behavior/dataset interpretation/strategy behavior/
   backtest behavior có khả năng tác động Gate 1, thì **mọi kết quả Gate 1 tạo trước đó bị coi
   là STALE/INVALIDATED và Gate 1 phải chạy lại** trước khi dùng cho verdict. Điều kiện này được
   ghi trực tiếp vào dependency column của WP-B1 ở bảng trên, và thành quy tắc chính thức ở
   DEC-009.
3. **Bỏ T-06A** — APPROVED. Toàn bộ phạm vi của T-06A được hấp thụ vào WP-A1, không mất
   requirement nào. WP-A1 vẫn là điều kiện bắt buộc trước T-06.
4. **WP-A2 routing** — OVERRIDE ROUTER. Tier C/Opus (không dùng B/Sonnet mà router trả), effort
   giữ nguyên `high` (giá trị router tính đúng, không bị ảnh hưởng bởi việc override Tier).
   Ghi tại DEC-008.

### Governance defect mới phát hiện trong quá trình duyệt

`routing_engine.py` dùng so sánh dấu phẩy động không có epsilon tại các mốc biên nguyên
(0/1/2/3). Với WP-A2, `model_score` hiển thị đúng `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, khiến `tier_from_score` (so sánh `s < 2`) trả về Tier B thay vì Tier C như
bảng `AGENT_CAPABILITY_MATRIX.md` quy định cho khoảng 2.00–2.99.

Đây là **defect của công cụ governance dùng chung, không phải finding của sản phẩm ETH DCA**.
Theo yêu cầu của chủ dự án, defect này được xử lý bằng ba artifact riêng, tách khỏi 33 finding
của S001:

- **Artifact:** `docs/reviews/GOVDEF-001-routing-engine-boundary.md`
- **Task:** `MICRO-GOVDEF-001` — xem mục "Micro Tasks (Inline)" bên dưới
- **Risk:** `GOV-RSK-001` — xem mục "Active Risks — Governance / Tooling" bên dưới

Không sửa `routing_engine.py` trong bước áp dụng roadmap này. Giải pháp sau này phải tổng quát
hoá cách so sánh (dùng epsilon hoặc làm tròn trước khi so sánh), không hard-code ngoại lệ riêng
cho WP-A2 hay bất kỳ task nào khác.

## Current Task Snapshot

Task:
WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp (S003)

Task Mode:
MAJOR

Status:
VERIFYING (implementation + toàn bộ E1 hoàn tất; đang chờ đóng E2 — CHECK-A3-10)

File định nghĩa:
`docs/tasks/WP-A3-regime-va-vong-doi-ladder.md`

Required Gate Progress:
9 / 10 PASS (E1); CHECK-A3-10 (E2 độc lập) đang thực hiện. Chi tiết evidence trong file task
và biên bản `docs/sessions/S003-wp-a3-regime-ladder.md`.

Kết quả chính của S003 (tới thời điểm snapshot):
- Baseline E1 tái hiện đủ F-001, F-021, F-022, F-030 ở tầng engine/regime TRƯỚC khi sửa.
- Regression test viết TRƯỚC fix: 12 FAIL đúng kỳ vọng → sau fix 18/18 PASS.
- Toàn bộ suite: **87 passed, 0 failed, 0 skipped** — không test cũ nào bị sửa/nới lỏng.
- Impact BEFORE/AFTER trên cùng dataset synth: mọi sai lệch truy về [F5] ST §14 và ST §18.3+[F1].
- Phát hiện mới ngoài scope: **PH-03** → RSK-010 (không sửa, chờ chủ dự án).

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.5 (D4 R4 B3 A3 X3) → floors `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`, `safety_business:min_C` → D

Effort Routing Score:
3.65 (U3 V4 H4 C3 F4) → floor `safety_business:min_high` → max

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Escalation Triggers:
- Theo file task WP-A3 (CAPABILITY_CEILING / CONFLICT DETECTED / metric đổi không giải thích
  được / phải chạm capital.py|score.py). Không trigger nào kích hoạt trong S003: một phương án
  thiết kế duy nhất (tách state/label) đạt đồng thời [F1] và vòng đời đóng; mọi sai lệch metric
  giải thích được; không chạm capital.py/score.py.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

### MICRO-GOVDEF-001 — Sửa lỗi so sánh boundary trong routing_engine.py
Status:
DONE

Checklist Reference:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Mô tả ngắn:
`tier_from_score`/`effort_from_score` trong `governance/scripts/governance/routing_engine.py`
dùng so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn, nên một điểm số ở đúng biên
nguyên (ví dụ 2.0) có thể bị tính sai một bậc Tier/Effort do sai số biểu diễn nhị phân
(`1.9999999999999998` thay vì `2.0`). Chi tiết đầy đủ, bằng chứng tái lập:
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`.

Phạm vi được làm rõ tại T-04 (S002), theo đúng câu đã có sẵn trong DEC-008 mục Impact
("`validate_routing.py` cần được cập nhật ở một task riêng — MICRO-GOVDEF-001 hoặc kế tiếp"):
task này bao gồm **cả** `validate_routing.py`, để công cụ chấp nhận một manual override **có ghi
nhận** (kèm `Manual Override` và `Router Raw Output` trong file task) thay vì báo lỗi khớp tuyệt
đối. Đây là làm rõ phạm vi đã được DEC-008 dự liệu, không phải quyết định mới. Việc mở task này
vẫn cần chỉ thị của chủ dự án — xem BLK-003 và DEC-010.

Ràng buộc bắt buộc khi sửa: tổng quát hoá cách so sánh (làm tròn trước khi so sánh, hoặc dùng
epsilon nhất quán với `EPS` đã dùng ở nơi khác trong codebase, ví dụ `capital.py`).
**Không hard-code ngoại lệ riêng cho bất kỳ task nào** (kể cả WP-A2, task đã kích hoạt phát hiện
này).

Đánh giá MICRO eligibility (`TASK_MODE_STANDARD.md`): Difficulty <= 2, Risk <= 2, Blast Radius
<= 2 — không đổi kiến trúc, không đổi auth, không migration, không thao tác phá huỷ dữ liệu.
Đủ điều kiện MICRO. Chấm điểm tham khảo (không bắt buộc với MICRO): D1 R2 B2 A1 X1 → 1.45 → B;
U1 V2 H1 C1 F2 → 1.45 → medium.

Evidence Summary (2026-08-23, chủ dự án phê duyệt PA-1 cho DEC-010):

**Compact Ready Gate** (`MICRO_TASK_CHECKLIST.md`) — đủ điều kiện, xác nhận lại khi mở: yêu cầu rõ
ràng (sửa boundary comparison + validator override); Risk 2 <= 2; Blast Radius 2 <= 2; không đổi
kiến trúc/auth/schema/thao tác phá huỷ; phạm vi hẹp và đã biết (`routing_engine.py`,
`validate_routing.py`, test governance mới); phương pháp kiểm chứng đã biết (brute-force toàn không
gian đầu vào + test override tổng hợp).

**Compact Completion Gate:**
- [x] Hành vi dự định đã cài đặt — `routing_engine.py` làm tròn `model_score`/`effort_score` về 3
  chữ số **trước khi** so sánh biên (căn cứ: trọng số chỉ có tối đa 2 chữ số thập phân, nên làm
  tròn 3 chữ số loại bỏ đúng nhiễu IEEE-754 ~1e-15, không đổi giá trị thật) — không phải epsilon
  tuỳ tiện, không hard-code WP-A2 hay bất kỳ task nào.
- [x] `validate_routing.py` chấp nhận manual override có ghi nhận (decision reference tồn tại
  trong `PROJECT_DECISIONS.md`, `Router Raw Output` xác thực khớp router hiện tại, chỉ được leo
  thang Tier/Effort chứ không hạ) — hàm `check_override`, tổng quát cho mọi `DEC-###`.
- [x] Verification thực sự chạy: brute-force toàn bộ 5^5 × 5^5 tổ hợp đầu vào cho **0** lệch còn
  lại; `governance/scripts/governance/test_routing_engine.py` — **37/37 check PASS**, gồm 6 ca
  override hợp lệ/không hợp lệ tổng hợp (không phụ thuộc WP-A2).
- [x] Evidence ghi theo `EVIDENCE_STANDARD.md`, mức E1 (chạy thật): xem
  `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- [x] Không mở rộng phạm vi ngoài dự kiến — `git diff` xác nhận chỉ chạm
  `governance/scripts/governance/routing_engine.py`, `validate_routing.py` (thêm), file task
  `WP-A2` (chỉ bổ sung ghi chú, không xoá dấu vết), và các artifact governance liên quan. Không
  chạm `src/`, `webapp/`, `tests/`, `docs/spec/`.
- [x] Regression liên quan đã PASS: `routing_engine.py`/`validate_routing.py` chạy lại trên toàn bộ
  16 file MAJOR task hiện có — **đúng một dòng đổi** (WP-A2, Tier B → C), không task nào khác đổi
  Tier/Effort. `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
  override(s))`.
- [x] `PROJECT/PROJECT_PROGRESS.md` inline Micro Task entry được cập nhật — mục này.

**Kết quả:** BLK-003 RESOLVED. GOV-RSK-001 CLOSED. WP-A2 chuyển `BLOCKED` → `READY`, giữ nguyên
Tier C / Opus / Effort high (nay route tự nhiên, không cần override — nhưng dấu vết DEC-008/Manual
Override/Router Raw Output trong file WP-A2 được **giữ nguyên**, không xoá).

Chi tiết đầy đủ: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
Test: `governance/scripts/governance/test_routing_engine.py`.

## Active Blockers

### BLK-001 — Không có đường tới dữ liệu Binance từ môi trường phát triển
Ảnh hưởng: **chỉ T-06** (RCP-001 xác định lại: không work package nào trong 15 gói lớp A/B/C/D
cần dữ liệu Binance thật — toàn bộ phát triển và kiểm chứng được trên dữ liệu tổng hợp theo
DEC-003). T-06 là điểm duy nhất trên đường găng cần blocker này được gỡ; T-07 và T-11 chỉ bị
chặn gián tiếp qua chuỗi phụ thuộc vào T-06, không phải trực tiếp bởi BLK-001.

Mô tả: Repo chưa từng có official run (`results/` không tồn tại và nằm trong `.gitignore`).
Môi trường phát triển bị chặn egress tới Binance, nên mọi kiểm chứng trong repo chạy trên dữ
liệu tổng hợp và tự gắn cờ `official: false`.
Đường xử lý đã được `docs/DATA_SOURCES.md` chấp nhận: chạy `ethdca fetch` trên máy của chủ dự án
hoặc VPS nước ngoài, copy `data/raw/` về, rồi xác minh bằng cách chạy `ethdca freeze` ở cả hai
máy và đối chiếu hash manifest phải trùng khớp.
Cần từ chủ dự án: một máy hoặc VPS truy cập được `data.binance.vision` và `api.binance.com`.

Bằng chứng E1 thu tại S000 (2026-08-23): cả ba host đều bị chặn ở tầng proxy, không phải lỗi
cấu hình phía repo.
`api.binance.com` → `curl: (56) CONNECT tunnel failed, response 403`
`data-api.binance.vision` → `curl: (56) CONNECT tunnel failed, response 403`
`api.coingecko.com` → `curl: (56) CONNECT tunnel failed, response 403`
PyPI thì thông, nên đây là chặn có chọn lọc theo host, không phải mất mạng.

Không bypass BLK-001. Không đổi nguồn dữ liệu. Không dùng dữ liệu tổng hợp để tạo official
verdict.

### BLK-003 — RESOLVED (`validate_routing.py` chưa biểu diễn được manual override đã được phê duyệt)
Trạng thái: **RESOLVED — 2026-08-23, tại MICRO-GOVDEF-001.**
Ảnh hưởng khi còn mở: **chỉ WP-A2**.

Mô tả: `governance/scripts/governance/validate_routing.py` so khớp **tuyệt đối** giữa
`Primary Agent Tier` trong file task và kết quả của `routing_engine.py`. Khi T-04 soạn file định
nghĩa cho WP-A2 với Tier C theo DEC-008, validator báo:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây **không phải defect mới**. DEC-008 mục Impact đã ghi trước rằng tình huống này sẽ xảy ra và
rằng `validate_routing.py` "cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để
chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối". T-04 làm đúng phần được giao và
không làm phần được giao cho task khác.

Vì sao nó chặn WP-A2: `CLAUDE.md` mục "Every Implementation Session" điểm 9 yêu cầu
`validate_routing.py` **PASS trước khi thực thi** một MAJOR task; `ROADMAP_SYNC_STANDARD.md` cũng
yêu cầu chạy validator này trước roadmap sync. Vì vậy WP-A2 giữ trạng thái `BLOCKED` cho tới khi
điều kiện được gỡ.

Đường gỡ (cần chủ dự án quyết định — xem DEC-010):
1. Cho phép mở `MICRO-GOVDEF-001` (đã mở rộng phạm vi để phủ cả `validate_routing.py`), hoặc
2. Miễn trừ bằng văn bản, ghi vào `PROJECT/PROJECT_DECISIONS.md`.

**Không được gỡ bằng cách hạ Tier WP-A2 về B** — DEC-008 cấm, và làm vậy là hạ tiêu chuẩn để
validator xanh.

Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-02.

**Cách đã gỡ (2026-08-23):** chủ dự án phê duyệt **PA-1**. `routing_engine.py` được sửa tổng quát
(làm tròn điểm số về cùng độ chính xác hiển thị trước khi so sánh biên); `validate_routing.py` được
bổ sung cơ chế chấp nhận manual override có ghi nhận. Sau fix, `validate_routing.py` PASS cho toàn
bộ 16 file MAJOR task, và WP-A2 route Tier C **tự nhiên** (không cần nhánh override nữa, dù nhánh đó
đã được xây và kiểm chứng độc lập cho các trường hợp tương lai). Không hạ Tier WP-A2 về B.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution";
`MICRO-GOVDEF-001` ở mục "Micro Tasks (Inline)".

### BLK-002 — Tính năng cảnh báo chưa được đặc tả
Ảnh hưởng: T-10, và là lý do T-08 tồn tại.
Mô tả: `docs/spec/01_PRODUCT_SPEC_V2_1_5.md` không có mục nào về alert/cảnh báo/notification.
Product Spec chỉ quy định trạng thái hiển thị thụ động trên hero khi mở trang (§11–§13).
Implementation Plan §9 hoãn có chủ đích: "không cần cron cho tới khi thực sự cần notification".
Điều kiện kích hoạt thì đã có đầy đủ trong Strategy Spec (§3, §4, §5, §9, §10, §15, §17, §18)
và danh mục 30 reason code ở Strategy §20 chính là bộ khung tự nhiên cho danh sách cảnh báo.
Nghĩa là: đây là khoảng trống ĐẶC TẢ, không phải khoảng trống code. Không thể triển khai đúng
trước khi đặc tả xong (T-08).

## Active Risks

### RSK-001 — Mất lịch sử giao dịch thật (mức: cao)
App web hiện lưu state trong localStorage của trình duyệt cộng cơ chế tự xuất bản lại trang.
Đây không phải "một database" như Implementation Plan §9 yêu cầu. Xóa dữ liệu site, dùng cửa sổ
riêng tư, đổi máy, hoặc publish thất bại đều có thể làm mất dữ liệu chưa xuất ra ngoài.
Giảm thiểu: T-09B. Cho tới khi T-09B xong, chủ dự án nên xuất file JSON định kỳ.

### RSK-002 — Hai bản cài đặt chiến lược trôi khỏi nhau (mức: cao) — S001 XÁC NHẬN (E1)
Implementation Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Trang
tĩnh không chạy được Python nên `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả.
Cơ chế chặn hiện có là parity check OSCORE 40 ngày (lệch tối đa 7.4e-11 lần kiểm gần nhất),
nhưng parity chỉ phủ OSCORE tổng — chưa phủ unlock, spacing, phân bổ ladder, invalidation,
regime. Mỗi tính năng port thêm sang JS sẽ mở rộng bề mặt trôi nhanh hơn khả năng phát hiện.
Giảm thiểu: **WP-C4** (RCP-001) — mở rộng phạm vi parity trước khi port thêm.

### RSK-003 — Nghi vấn ba lỗi kế toán trong app web (mức: trung bình, một phần đã được loại trừ)
Ghi nhận ban đầu từ việc đọc code: (a) hàm chọn tháng hiện hành trả về tháng có key lớn nhất
chứ không phải tháng của ladder, nên release vốn có thể trả nhầm pool khi có nhiều tháng;
(b) mức unlock không giới hạn số vốn được reserve; (c) trạng thái dữ liệu INVALID không chặn
tạo action mới như Strategy §3 yêu cầu.

Cập nhật sau bằng chứng E1 tại S000: `webapp/test_zone.js` chạy thật và cho thấy bất biến kế
toán **giữ đúng trong kịch bản một tháng** — tổng bảo toàn 3.000.000 qua đủ chuỗi thao tác
fill toàn phần → fill một phần → invalidation → release, và không pool nào âm.
Nghĩa là (a) **chưa bị bác bỏ nhưng cũng chưa được tái hiện**: test hiện có chỉ dùng một tháng,
đúng vào điểm mù của nghi vấn. (b) và (c) chưa có ca kiểm thử nào chạm tới.

Còn lại phải xác minh ở **WP-C1** (RCP-001) bằng ca kiểm thử **đa tháng** cho (a), và ca kiểm
thử riêng cho (b), (c). Sửa (nếu xác nhận): T-09A.

### RSK-004 — Bộ test app web không chạy được từ bản checkout sạch (mức: trung bình) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: hai test webapp **chạy được và cho kết quả đúng**, nhưng chỉ sau khi
dựng thủ công hai thứ không có trong repo — `webapp/app_final.html` (phải build) và
`demo/results3/live_seed.json` (**không tồn tại ở bất kỳ đâu trong repo**).
Nghĩa là không ai clone repo về mà chạy được test của app, và không có gì bảo vệ hồi quy tự động.

Ghi nhận thêm: hai test ghi ảnh chụp màn hình vào thư mục làm việc hiện hành. Nếu chạy từ trong
`webapp/` sẽ để lại `app-dash.png` và `app-zone.png` trong repo, mà hai file này không nằm trong
`.gitignore`.

Giảm thiểu: **WP-C1** (RCP-001) khôi phục harness trước khi định lượng mức bảo vệ hồi quy thật.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình) — S001 XÁC NHẬN VÀ MỞ RỘNG (E1)
S001 xác nhận và phát hiện quy ước không được ghi ở nhiều chỗ hơn dự kiến: ngoài ánh xạ
gate-fail → verdict, còn có ngưỡng số tự đặt của FS-02/FS-07/FS-12, phạm vi tính FS-03/FS-07 chỉ
trên window W5, và tham số `shift_days=10` của Control G. `verdict.py` còn ghi rằng ánh xạ được
tài liệu hoá ở `docs/CONVENTIONS.md`, nhưng file đó không có mục nào về verdict.
Xem finding F-015, F-016, F-026. Giảm thiểu: **WP-B1** (RCP-001).

`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ để không bị coi nhầm là điều
khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

### RSK-006 — Không ghim phiên bản thư viện, nên kết quả không tái lập được theo thời gian (mức: cao) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: `pyproject.toml` chỉ đặt sàn (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không có lockfile và không có trần. Khi cài mới, pip kéo về `numpy 2.4.6`,
`pandas 3.0.5`, `pyarrow 25.0.1` — vượt xa sàn tới hai thế hệ lớn. Toàn bộ 69 test vẫn PASS
trên bộ này, đó là tín hiệu tốt về độ bền, nhưng là **may mắn chứ không phải bảo đảm**.

Vì sao mức cao: Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu —
"cùng dataset hash + config hash + manifest hash + seed thì tái lập chính xác cùng kết quả".
Run record hiện lưu hash của config, manifest, dataset và seed, **nhưng không lưu phiên bản thư
viện**. Một thay đổi dấu phẩy động trong numpy/pandas ở phiên bản sau có thể làm official run
không tái lập được, mà không ai phát hiện — vì mọi hash đầu vào vẫn trùng khớp.

Giảm thiểu: **WP-A1** (RCP-001) — thay thế T-06A, đóng đủ cả 8 trường provenance yêu cầu
(Python version, dependency/lock hash, git commit SHA, dataset hash, strategy config hash,
execution config hash, manifest hash, seed), không chỉ ghim thư viện.

### RSK-007 — Pipeline không chạy nhiều hạng mục mà spec ghi là bắt buộc cho official run (mức: cao) — S001 XÁC NHẬN (E1)
S001 phát hiện (E1): Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng coverage §4 và
XIRR §16 đều đã được cài đặt đúng nhưng **không nơi nào trong pipeline gọi chúng**. Hệ quả: một
official run sẽ phát ra verdict kèm báo cáo thiếu, và nguyên tắc Backtest §22 ("luật đơn giản
thắng nếu kết quả tương đương") không thể áp dụng vì không có B/C/D để so.
Ngoài ra ba Failure Signal (FS-02, FS-06, FS-12) không bao giờ được truyền input nên luôn UNKNOWN,
trong khi verdict BUILD vẫn phát ra bình thường.
Xem finding F-002, F-003, F-004, F-012, F-013. Giảm thiểu: **WP-A2, WP-A5** (RCP-001).

### RSK-008 — Run trên dữ liệu tổng hợp vẫn được ghi nhận là official (mức: cao) — S001 XÁC NHẬN (E1)
S001 xác nhận (E1): cờ `official` chỉ phụ thuộc việc có dùng `--dev-limit` hay không, hoàn toàn
không kiểm nguồn dữ liệu; và `lineage.json` ghi `source` là chuỗi cố định `'see fetch/synth'` cho
cả dữ liệu thật lẫn dữ liệu tổng hợp. Chạy `ethdca synth && ethdca run all` sẽ tạo record mang
`official: true` trên dữ liệu nhân tạo, không có trường nào cho phép phát hiện về sau.
Đây là rủi ro thẳng vào tính toàn vẹn của verdict — tức vào chính cổng mở đường cho app.
Xem finding F-005. Giảm thiểu: **WP-A1** (RCP-001).

### RSK-009 — Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn (mức: cao) — ĐÃ REMEDIATE tại S003 (WP-A3)
S001 phát hiện và kiểm chứng bằng chạy thật (E1): khi giai đoạn RECOVERY kết thúc lúc thị trường
còn yếu, regime chuyển thành STRESSED chứ không phải NORMAL, nên nhánh dọn Crash ladder ở
`engine.py:415` không bao giờ chạy. Reserve của Crash zone không được giải phóng, kéo theo không
tạo được ladder mới và cash ratio tăng giả tạo — có thể bóp méo chính FS-02 và FS-07.
Đây đồng thời là vi phạm [F1] (STRESSED phải không có hiệu ứng execution).
Xem finding F-001. Giảm thiểu: **WP-A3** (RCP-001).

**Cập nhật S003 (2026-08-23):** WP-A3 đã tách trạng thái nền khỏi nhãn STRESSED
(`RegimeTracker.state`/`.label`, CONVENTIONS #14) và nhánh dọn chạy cho MỌI kết cục kết thúc
Recovery; bằng chứng E1: baseline tái hiện lock 27.2 đơn vị trước fix → 0 sau fix, chuỗi test
CHECK-A3-01/02, suite 87 PASS. Trạng thái risk: **đóng khi WP-A3 DONE** (chờ E2 CHECK-A3-10).

### RSK-010 — Nghi vấn `smart_reservable` trừ `deployed` luỹ kế XUYÊN THÁNG làm Smart ladder gần như không được tạo lại từ tháng 2 (mức: cao — NGHI VẤN, chưa kết luận) — PH-03, S003
Quan sát E1 tại S003 (impact run 90 tháng dữ liệu tổng hợp, cả TRƯỚC lẫn SAU fix WP-A3 — tức
tồn tại từ trước, KHÔNG phải hồi quy của WP-A3): chỉ **2** Smart ladder được tạo trong 90 tháng.
Đọc code: `smart_reservable(pool, month_smart_budget, unlock)` tính
`unlocked(≤ ngân sách THÁNG ~30) − pool.reserved − pool.deployed`, trong đó `pool.deployed` là
luỹ kế TOÀN ĐỜI; từ tháng 2 trở đi `deployed ≫ unlocked` nên hàm trả 0 vĩnh viễn — Smart chỉ còn
giải ngân qua Month-End settle, không qua ladder. Có dấu hiệu mâu thuẫn ST §6 (unlock/peak là
khái niệm THEO THÁNG — "Peak reset khi sang accounting month mới").
**Ngoài ownership WP-A3** (không thuộc F-001/021/022/030; chạm `capital.py` là vùng cấm Scope
Lock) → ghi nhận theo đúng chỉ thị "không tiện tay sửa". Cần chủ dự án quyết định: gắn định danh
finding chính thức (F-035?) và giao cho WP nào, hay xác nhận là hành vi chủ đích rồi ghi
CONVENTIONS. Nếu là defect thật, ảnh hưởng kết quả mô phỏng LỚN hơn WP-A3 nhiều.

## Active Risks — Governance / Tooling

Rủi ro của bản thân bộ công cụ governance dùng chung, **tách khỏi rủi ro sản phẩm ETH DCA** ở
mục trên. Không tính vào 33 finding của S001.

### GOV-RSK-001 — Sai số biên dấu phẩy động trong routing_engine.py có thể under-route task đúng biên (mức: trung bình) — CLOSED
Phát hiện khi áp dụng RCP-001 (2026-08-23), tái lập được (E1): `tier_from_score` và
`effort_from_score` so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn/chưa có
epsilon. Một task có điểm nền đúng bằng 2.0 (biên Tier B/C) có thể nhận `model_score` nội bộ là
`1.9999999999999998` do cách `0.25*D+0.25*R+0.20*B+0.15*A+0.15*X` cộng dồn sai số nhị phân, và
bị route xuống Tier B thay vì Tier C.

Trường hợp cụ thể đã xác nhận: WP-A2 (D2 R2 B2 A1 X3) — hiển thị `model_score: 2.0` nhưng nội bộ
`1.9999999999999998`, router trả Tier B trong khi bảng `AGENT_CAPABILITY_MATRIX.md` quy định
2.00–2.99 → Tier C.

Ảnh hưởng: bất kỳ task nào (không riêng dự án này) có điểm nền rơi đúng vào các mốc nguyên
0/1/2/3 đều có nguy cơ tương tự, theo cả hai chiều (có thể over-route hoặc under-route tuỳ dấu
sai số). Mức trung bình vì hệ quả là chọn sai một bậc Tier/Effort, không phải sai kết quả tính
toán nghiệp vụ.

Giảm thiểu tạm thời đã áp dụng cho WP-A2: **manual override** theo DEC-008, ghi nhận công khai
trong bảng roadmap.
Giảm thiểu triệt để: **MICRO-GOVDEF-001** — **HOÀN TẤT 2026-08-23**. `routing_engine.py` làm tròn
điểm số về cùng độ chính xác hiển thị trước khi so sánh biên; xác nhận bằng quét toàn bộ 5^5 × 5^5
tổ hợp đầu vào cho 0 lệch còn lại (`test_routing_engine.py`, 37/37 PASS). WP-A2 nay route Tier C tự
nhiên, không cần override. Không task nào khác trong 16 file MAJOR hiện có bị ảnh hưởng.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".

## Open Regression Items
- None ở tầng mã nguồn. S001 không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với
  V2.1.5; bảy sửa đổi F1–F7 đều có dấu vết hiện thực.
- **PH-01 (tài liệu, không phải mã nguồn)** — bảng "Tổng hợp" của `docs/reviews/S001-audit-findings.md`
  ghi MEDIUM 15 và Tổng 33, nhưng đếm thật trên chính danh mục được liệt kê cho **34 định danh
  `F-xxx`** (HIGH 8 + MEDIUM 19 + LOW 7) cộng 3 `S-xxx`. Con số 33 đã được chép sang tài liệu này và
  sang RCP-001. **Không finding nào bị rơi** — RCP-001 §2 và §6 phân đủ 34 `F-xxx` vào 15 gói, và
  T-04 xác nhận 40/40 định danh có nơi thuộc về. T-04 **không tự sửa** con số trong biên bản audit
  của phiên đã đóng; chờ chủ dự án quyết định cách đính chính.
  Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-01.

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)
- DEC-006 — Source of Truth cho compliance audit là V2.1.5, không phải V2.1.3
- DEC-007 — RCP-001 được phê duyệt và áp dụng kèm bốn điều kiện
- DEC-008 — Ghi đè thủ công routing của WP-A2 (Tier C, không dùng Tier B từ router)
- DEC-009 — Quy tắc Gate 1 staleness: remediation ảnh hưởng Gate 1 bắt buộc chạy lại Gate 1
- DEC-010 — RESOLVED: PA-1 phê duyệt cho BLK-003; `routing_engine.py`/`validate_routing.py` đã sửa

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- MICRO-GOVDEF-001 — SỬA BOUNDARY DEFECT + OVERRIDE MECHANISM — 2026-08-23 — Chủ dự án phê duyệt
  PA-1 cho DEC-010. Sửa tổng quát `routing_engine.py` (làm tròn `model_score`/`effort_score` về
  cùng độ chính xác hiển thị **trước khi** so sánh biên Tier/Effort — không epsilon tuỳ tiện, không
  hard-code task nào). Bổ sung cơ chế `check_override` vào `validate_routing.py`: chấp nhận manual
  override chỉ khi có decision reference tồn tại thật trong `PROJECT_DECISIONS.md`, `Router Raw
  Output` xác thực khớp router hiện tại, và override chỉ được leo thang chứ không hạ Tier/Effort.
  Thêm `governance/scripts/governance/test_routing_engine.py` (37 check, gồm quét toàn bộ 5^5×5^5
  tổ hợp đầu vào — 0 lệch còn lại — và 6 ca override hợp lệ/không hợp lệ tổng hợp). Kết quả: WP-A2
  route Tier C **tự nhiên** (giữ nguyên Model Opus, Effort high), không cần override — chuyển
  `BLOCKED` → `READY`. BLK-003 RESOLVED, GOV-RSK-001 CLOSED. Đối chiếu trước/sau trên toàn bộ 16
  file MAJOR task: đúng một dòng đổi (WP-A2, Tier B → C), không task nào khác bị ảnh hưởng. Không
  sửa `src/`, `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, không mở S003.
  Kết luận: **MICRO-GOVDEF-001 DONE**.
  Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- S002 — ROADMAP FINALIZATION / GATE FREEZE (T-04) — 2026-08-23 — Soạn và đóng băng Ready Gate +
  Completion Gate đầy đủ cho toàn bộ 15 work package của RCP-001 (**125 REQUIRED check**), cộng file
  định nghĩa cho chính T-04 (12 REQUIRED check). Chính thức hoá DEC-009 thành `CHECK-B1-02`
  (REQUIRED) của WP-B1. Bảo toàn override DEC-008 cho WP-A2 (Tier C / Opus / high) kèm giá trị
  router thô. Bảo toàn đủ 8 trường provenance của T-06A cũ trong WP-A1. Tách rõ trách nhiệm đo lường
  (WP-A5) khỏi trách nhiệm chính sách verdict (WP-B1). Đối chiếu độ phủ bằng script: 40/40 định danh
  finding có nơi thuộc về. Phát hiện PH-01 (sai số đếm trong tóm tắt S001) và PH-02 → **BLK-003**.
  Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`. Không bắt đầu work package nào.
  Kết luận: **T-04 DONE — PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S002-t04-gate-freeze.md`.
  Đối chiếu: `docs/reviews/S002-coverage-regression-check.md`.
- RCP-001 — ROADMAP CHANGE APPLIED — 2026-08-23 — Chủ dự án phê duyệt RCP-001 kèm bốn điều kiện
  (cấu trúc 15 work package; phân lớp A/B/C/D với quy tắc Gate 1 staleness cho F-017; bỏ T-06A,
  hấp thụ vào WP-A1; ghi đè routing của WP-A2 lên Tier C). Bảng roadmap chuẩn được cập nhật từ
  14 lên 28 task. Phát hiện và ghi nhận riêng một governance/tooling defect (GOVDEF-001) trong
  chính `routing_engine.py`, tách khỏi finding sản phẩm. Không sửa `src/`, `webapp/`, `tests/`,
  `docs/spec/`. Không bắt đầu thực thi work package nào. Không bắt đầu S002.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`, `docs/reviews/GOVDEF-001-routing-engine-boundary.md`.
- RCP-001 — ROADMAP CHANGE PROPOSAL (trình) — 2026-08-23 — Chuyển 33 finding của S001 thành 15
  work package có dependency graph và phân lớp A/B/C/D. Trình để chủ dự án phê duyệt.
- S001 — DISCOVERY & BASELINE (AUDIT READ-ONLY) — 2026-08-23 — Đối chiếu toàn bộ implementation
  với spec V2.1.5 theo chín nhóm A–I. Sinh Compliance Matrix, Audit Findings (33 finding: 0
  CRITICAL, 8 HIGH, 15 MEDIUM, 7 LOW, 3 spec defect; 18/33 có bằng chứng chạy thật) và Discovery
  Baseline. Không sửa một dòng mã sản phẩm nào. Kết luận: **S001 PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S001-discovery-baseline.md`.
- S000 — PROJECT OPEN — 2026-08-23 — Chọn profile PRODUCT, khởi tạo trạng thái dự án, lập kế
  hoạch khảo sát (T-01..T-03) và lộ trình sơ bộ 14 task. Không sửa một dòng code sản phẩm nào.
  Biên bản: `docs/sessions/S000-project-open.md`.

## Bằng chứng nền thu tại S000

Đây là bằng chứng **E1 — chạy thật**, khác với các quan sát đọc code (E0) đã nêu ở mục rủi ro.

| Hạng mục | Kết quả | Mức |
|---|---|---|
| Test suite Python | **69 passed, 0 failed, 0 skipped, 0 error** trong 372,63s | E1 |
| Môi trường | Python 3.11.15, node v22.22.2, git 2.43.0 | E1 |
| Thư viện thực cài | numpy 2.4.6, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1 | E1 |
| Mạng tới Binance/CoinGecko | Cả ba host trả 403 ở tầng proxy; PyPI thông | E1 |
| `ethdca synth` | 2,0s — 262.748 nến 15m, 3.102 nến ngày | E1 |
| `ethdca freeze` Gate 2 | 19 ứng viên OFAT → loại 1 (`base_pct=0.7`, lý do `smart_pct < 0.15`) → 18 hợp lệ; 200 interaction; **mẫu số 219** | E1 |
| `ethdca freeze` Gate 3 | 14 deterministic + 100 sampled = **114 config** | E1 |
| Parity engine JS ↔ Python | Lệch tối đa **7,39e-11** trên 40 ngày — hai bản đồng thuận | E1 |
| Bất biến kế toán ladder (một tháng) | Tổng bảo toàn 3.000.000 qua fill toàn phần → fill một phần → invalidation → release; không pool nào âm | E1 |
| Build quine của webapp | Self-check đạt, template giải mã lại được | E1 |
| CLI | 6 lệnh: `fetch`, `synth`, `freeze`, `run`, `verdict`, `export-live` | E1 |
| `results/`, `data/`, `.venv/` trong repo | Không tồn tại — xác nhận chưa từng có official run | E1 |

Điều này làm đổi đánh giá ban đầu theo hướng tốt hơn: **mã nguồn khỏe hơn tài liệu gợi ý**.
S001 xác nhận: tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không (xem RCP-001).

Cảnh báo quan trọng về ý nghĩa của các validator governance: chúng đang PASS trên **tập rỗng** —
0 evidence record, 0 MAJOR task file, 0 task DONE. Khung đã có, nội dung thì chưa. Không được
đọc các dòng PASS đó như bằng chứng chất lượng dự án.

## Routing sơ bộ cho task chưa có file định nghĩa

**Cập nhật S002:** mục này không còn là nguồn routing cho 15 work package — cả 15 đã có file định
nghĩa đầy đủ dưới `docs/tasks/`, và file task là nguồn routing chính thức theo
`ROADMAP_SYNC_STANDARD.md`. Các giá trị dưới đây được **giữ lại làm dấu vết lịch sử** và đã được
T-04 xác minh lại bằng `routing_engine.py` (E1): 15/15 khớp, ngoại lệ duy nhất là override DEC-008
của WP-A2. Task còn lại chưa có file định nghĩa (T-05…T-11) vẫn dùng mục này.

Ghi lại để lộ trình có bằng chứng routing, sẽ soạn thành file task đầy đủ và đóng băng tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

### Task gốc (S000)

- T-00 — D3 R2 B1 A3 X3 → 2.35 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C4 F2 → 2.7 → xhigh
- T-04 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U2 V2 H3 C3 F3 → 2.60 → xhigh
- T-06 — D2 R3 B3 A1 X3 → 2.45 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-08 — D3 R3 B2 A3 X3 → 2.80 → C (2 floor); U3 V2 H3 C3 F3 → 2.80 → xhigh
- T-09A — D3 R3 B2 A1 X2 → 2.35 → C (floor `safety_business:min_C`); U1 V3 H2 C2 F3 → 2.25 → high
- T-09B — D3 R3 B3 A3 X3 → 3.00 → D (2 floor); U3 V3 H3 C3 F3 → 3.00 → xhigh
- T-10 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-11 — D4 R4 B3 A2 X4 → 3.50 → D (2 floor); U3 V4 H4 C4 F4 → 3.80 → max

Category `accounting_financial` được gắn cho T-06, T-08, T-09A, T-09B, T-10, T-11 vì chúng chạm
lớp tính toán dẫn tới quyết định xuống tiền thật. T-09B gắn thêm
`material_sensitive_data_corruption` vì thao tác chuyển đổi lưu trữ có thể làm hỏng sổ tài chính.

**T-06A đã bị loại khỏi roadmap theo RCP-001** (hấp thụ vào WP-A1). Routing gốc của nó vẫn được
lưu lại để đối chiếu lịch sử: D2 R2 B2 A1 X2 → 1.85 → B; U1 V2 H2 C2 F2 → 1.80 → high.

### Work package của RCP-001 (2026-08-23)

- WP-A1 — D2 R3 B3 A2 X3 → 2.60 → C (không floor); U2 V3 H3 C3 F3 → 2.80 → xhigh
- **WP-A2** — D2 R2 B2 A1 X3 → **model_score = 2.0 (hiển thị), 1.9999999999999998 (nội bộ)** →
  router trả **B** (Sonnet). **GHI ĐÈ THỦ CÔNG theo DEC-008 → Tier C (Opus)**, lý do: defect biên
  dấu phẩy động của router (GOVDEF-001), không phải lỗi chấm điểm đầu vào.
  Effort: U1 V3 H2 C3 F2 → 2.15 → high (giữ nguyên, không bị override)
- WP-A3 — D4 R4 B3 A3 X3 → 3.50 → D (floor `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`,
  `safety_business:min_C`); U3 V4 H4 C3 F4 → 3.65 → max (floor `safety_business:min_high`)
  · category `accounting_financial`
- WP-A4 — D3 R3 B2 A3 X2 → 2.65 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-A5 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U3 V3 H3 C3 F3 → 3.00 → xhigh
- WP-A6 — D4 R3 B3 A2 X3 → 3.10 → D (floor `cognitive:D>=4&X>=3`); U3 V4 H3 C3 F3 → 3.20 → max
- WP-B1 — D3 R4 B3 A4 X3 → 3.40 → D (floor `cognitive:A>=3&X>=3`, `safety_business:min_C`);
  U3 V3 H3 C3 F4 → 3.25 → max (floor `safety_business:min_high`) · category `accounting_financial`
- WP-B2 — D3 R2 B1 A2 X3 → 2.20 → C (không floor); U2 V3 H3 C3 F2 → 2.55 → xhigh
- WP-B3 — D2 R2 B2 A2 X2 → 2.00 → C (không floor); U1 V2 H2 C2 F2 → 1.80 → high
- WP-C1 — D2 R3 B2 A1 X2 → 2.10 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-C2 — D3 R2 B3 A3 X3 → 2.75 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh
- WP-C3 — D3 R3 B2 A2 X2 → 2.50 → C (floor `safety_business:min_C`); U2 V3 H2 C2 F3 → 2.45 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-C4 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-D1 — D1 R1 B1 A1 X1 → 1.00 → B (không floor); U1 V1 H1 C1 F1 → 1.00 → medium
- WP-D2 — D3 R2 B2 A4 X3 → 2.70 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh

**GOVDEF-001 / MICRO-GOVDEF-001** — không bắt buộc full routing (MICRO). Chấm điểm tham khảo:
D1 R2 B2 A1 X1 → 1.45 → B; U1 V2 H1 C1 F2 → 1.45 → medium.

## Next Session

Recommended Session:
S003 — thực thi **một** work package đã READY. Khuyến nghị theo hai tiêu chí khác nhau:

- **Theo đường găng:** `WP-A3` — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp (D/Fable/max).
  Đây là mắt xích đầu tiên của T-04 → WP-A3 → WP-A4 → WP-A6 → GATE-A → T-06, và mọi gói lớp A khác
  đều chờ nó ở mức độ nào đó.
- **Theo an toàn dữ liệu thật:** `WP-C1` — Kiểm chứng ba nghi vấn ở app web (C/Opus/xhigh). Nếu chủ
  dự án đang dùng app để ghi giao dịch tiền thật, ba nghi vấn này — nếu đúng — đang làm sai sổ vốn
  ngay lúc này. Gói này độc lập hoàn toàn và chạy song song được với lớp A.

Task đang READY (đủ điều kiện bắt đầu, chưa bắt đầu):
`WP-A1`, `WP-A2` (mới, sau MICRO-GOVDEF-001), `WP-A3`, `WP-C1`, `WP-D1`, `WP-D2`.

Task đang BLOCKED và lý do:
- `WP-C2` — DEC-005 còn PENDING (thuộc T-05, thẩm quyền chủ dự án)
- `T-03` — chờ WP-C1 (giữ nguyên, không hạ Completion Gate)

Cần chủ dự án quyết định:
1. **DEC-005** — phạm vi công cụ trước verdict (T-05). Không chặn lớp A.
2. **PH-01** — cách đính chính số đếm finding trong biên bản S001.
3. **BLK-001** — máy/VPS truy cập được `data.binance.vision` và `api.binance.com`, cần cho T-06.
   Không gói nào trong 15 gói cần nó, nên chưa gấp.

Purpose:
Bắt đầu thực thi chương trình remediation với Completion Gate đã được đóng băng từ trước, để tiêu
chí không bị uốn theo kết quả.

KHÔNG tự mở — chủ dự án sẽ ra chỉ thị riêng.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. File định nghĩa của work package được chọn, dưới `docs/tasks/`
6. `docs/sessions/S002-t04-gate-freeze.md`
7. `docs/reviews/S001-audit-findings.md` — phần finding mà gói đó đóng
8. `docs/spec/` — các điều khoản được viện dẫn trong Completion Gate của gói

Nhắc trước khi mở S003:
Completion Gate của cả 15 gói đã **đóng băng** ngày 2026-08-23. Không được xoá hay làm yếu bất kỳ
REQUIRED check nào để gói đi qua. Nếu một check hoá ra sai hoặc bất khả thi, dùng khối
`COMPLETION GATE CHANGE PROPOSAL` theo `TASK_COMPLETION_GATE_STANDARD.md` và trình chủ dự án —
không sửa im lặng.
