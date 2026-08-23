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
2026-08-23 — kết phiên S000

Overall Status:
PLANNING

Current Phase:
Phase 1 — Discovery & Baseline (chưa bắt đầu)

Current Task:
T-01 — Kiểm kê hiện trạng toàn repo

Current Task Mode:
SPIKE

Next Recommended Task:
T-01, mở trong phiên S001 chạy ở chế độ AUDIT read-only.

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính. Bằng chứng routing của từng task nằm trong file task tương ứng dưới
`docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối tài liệu này.

Phase 3 trở đi là **roadmap sơ bộ**. Theo `00_SESSION_ORCHESTRATION.md` ("Do not freeze distant
task details before discovery is sufficient"), các task này sẽ được tính lại routing và chốt
Completion Gate tại T-04, không đóng băng bây giờ.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| PLANNED | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| PLANNED | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| PLANNED | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. Song song được với T-02 |
| PLANNED | T-04 | Chốt lộ trình và đóng băng tiêu chí | Biến kết quả khảo sát thành lộ trình chính thức, có tiêu chí nghiệm thu đóng băng | C | xhigh | Sau T-01, T-02, T-03 |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. Chặn T-06, T-08 |
| PLANNED | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | Sau T-05. Cần máy/VPS có mạng Binance |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | Sau T-06. Chặn T-11 |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05. Song song được với T-06 |
| PLANNED | T-09A | Sửa lỗi kế toán trong app web | Vá 3 lỗi có thể làm sai sổ vốn trước khi app được dùng với tiền thật | C | high | Sau T-03 và T-04 |
| PLANNED | T-09B | Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | Sau T-04. Nên làm trước T-10 |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08 và T-09B |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07 và chỉ khi verdict = BUILD |

## Current Task Snapshot

Task:
T-01 — Kiểm kê hiện trạng toàn repo

Task Mode:
SPIKE

Status:
PLANNED

Required Gate Progress:
0 / 0 PASS — Completion Gate sơ bộ đã soạn trong `docs/tasks/T-01-kiem-ke-hien-trang.md`,
sẽ chốt khi mở phiên S001.

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.2 (D3 R2 B1 A2 X3) → base tier C, không áp floor nào

Effort Routing Score:
2.7 (U3 V2 H3 C4 F2) → xhigh, không áp floor nào

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Escalation Triggers:
- Phát hiện sai lệch giữa code và spec ở mức không thể kết luận trong một phiên
  → phân loại `CAPABILITY_CEILING` theo `AGENT_CAPABILITY_MATRIX.md` Stage 4 trước khi nâng Tier.
- Thiếu dữ liệu/quyền để kiểm chứng → `MISSING_INPUT`, chuyển BLOCKED, KHÔNG nâng Tier.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

Hiện chưa có Micro Task nào được mở.

## Active Blockers

### BLK-001 — Không có đường tới dữ liệu Binance từ môi trường phát triển
Ảnh hưởng: T-06, và qua đó chặn T-07 và T-11.
Mô tả: Repo chưa từng có official run (`results/` không tồn tại và nằm trong `.gitignore`).
Môi trường phát triển bị chặn egress tới Binance, nên mọi kiểm chứng trong repo chạy trên dữ
liệu tổng hợp và tự gắn cờ `official: false`.
Đường xử lý đã được `docs/DATA_SOURCES.md` chấp nhận: chạy `ethdca fetch` trên máy của chủ dự án
hoặc VPS nước ngoài, copy `data/raw/` về, rồi xác minh bằng cách chạy `ethdca freeze` ở cả hai
máy và đối chiếu hash manifest phải trùng khớp.
Cần từ chủ dự án: một máy hoặc VPS truy cập được `data.binance.vision` và `api.binance.com`.

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

### RSK-002 — Hai bản cài đặt chiến lược trôi khỏi nhau (mức: cao)
Implementation Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Trang
tĩnh không chạy được Python nên `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả.
Cơ chế chặn hiện có là parity check OSCORE 40 ngày (lệch tối đa 7.4e-11 lần kiểm gần nhất),
nhưng parity chỉ phủ OSCORE tổng — chưa phủ unlock, spacing, phân bổ ladder, invalidation,
regime. Mỗi tính năng port thêm sang JS sẽ mở rộng bề mặt trôi nhanh hơn khả năng phát hiện.
Giảm thiểu: mở rộng phạm vi parity trước khi port thêm; xác nhận trong T-02/T-03.

### RSK-003 — Nghi vấn ba lỗi kế toán trong app web (mức: cao, chưa xác minh)
Ghi nhận từ khảo sát S000, CHƯA được kiểm chứng bằng test chạy thật nên vẫn là nghi vấn:
(a) hàm chọn tháng hiện hành trả về tháng có key lớn nhất chứ không phải tháng của ladder, nên
release vốn có thể trả nhầm pool khi có nhiều tháng; (b) mức unlock không giới hạn số vốn được
reserve, có thể reserve phần vốn chưa mở khóa; (c) trạng thái dữ liệu INVALID không chặn tạo
action mới như Strategy §3 yêu cầu.
Xác minh: T-03. Sửa: T-09A. Không sửa trong S001 vì S001 là read-only.

### RSK-004 — Bộ test của app web không phải test thật (mức: trung bình)
Hai file test của webapp là script in ra console, không có assertion nào có thể fail, và cần
`app_final.html` cùng thư mục `demo/` — cả hai đều không có trong repo. Nghĩa là chúng không
chạy được từ một bản checkout sạch và không bảo vệ được hồi quy.
Xác minh và định lượng: T-03.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình)
`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ trong T-02 để không bị coi nhầm
là điều khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

## Open Regression Items
- None

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- S000 — PROJECT OPEN — 2026-08-23 — Chọn profile PRODUCT, khởi tạo trạng thái dự án, lập kế
  hoạch khảo sát (T-01..T-03) và lộ trình sơ bộ 13 task. Không sửa một dòng code sản phẩm nào.
  Biên bản: `docs/sessions/S000-project-open.md`.

## Routing sơ bộ cho task chưa có file định nghĩa

Ghi lại để lộ trình có bằng chứng routing, sẽ tính lại và chốt tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

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

## Next Session

Recommended Session:
S001 — Discovery & Baseline, chạy ở chế độ AUDIT read-only.

Purpose:
Thực hiện T-01, T-02, T-03. Sinh Discovery Baseline và Audit Findings. Không sửa code sản phẩm.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. `docs/tasks/T-01-kiem-ke-hien-trang.md`
6. `docs/spec/00_MASTER_INDEX_V2_1_5.md` — precedence tài liệu spec
7. `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
8. `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`

Nhắc trước khi mở S001:
S001 là read-only. Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`.
Đầu ra là tài liệu khảo sát, không phải code.
