# T-03 — Soát app web và rủi ro mất dữ liệu

## Metadata
Status:
DONE

(`DEC-041` I, 2026-09-05 — Owner-authorized Lifecycle Closure. `VERIFYING → DONE` dựa **hoàn
toàn trên bằng chứng đã có sẵn**, không chạy thêm việc nào: 5/5 REQUIRED PASS ở `E1`
(`CHECK-03-01` PASS tại `WP-C1` 2026-09-02; `03-02`, `03-03`, `03-04`, `03-06`), RECOMMENDED
`CHECK-03-05` PASS ở `E0`; không REQUIRED check nào ở `FAIL`/`BLOCKED`/`NOT_TESTED`
(`governance/core/TASK_COMPLETION_GATE_STANDARD.md`). Exit Criteria 5/5 thoả, gồm điều kiện mà
mục "Cập nhật WP-C1" ở cuối file này nêu: đã xác nhận `docs/reviews/S001-audit-findings.md` đủ
vai trò của `docs/reviews/S001-audit-findings-webapp.md` dự kiến ban đầu — file đó phủ
`V-01`/`V-02`/`V-03` cùng `F-024`/`F-027`, đủ trường Severity / Evidence / Evidence Level /
Recommended Fix / Suggested Task. `RSK-003` ĐÓNG theo đó. Production diff của lượt đóng = 0.)

Phase:
Phase 1 — Discovery & Baseline

Task Mode:
SPIKE

Chế độ phiên:
AUDIT — READ ONLY

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 3
B: 2
A: 2
X: 2
U: 2
V: 2
H: 2
C: 2
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
high

Model Routing Score:
2.25

Effort Routing Score:
2.25

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
xhigh

Difficulty:
2/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

App web trong `webapp/` là thứ gần nhất với mục tiêu cuối của chủ dự án, và là thứ duy nhất
sẽ chạm vào tiền thật. Câu hỏi phải trả lời:
**app này có an toàn để ghi chép tiền thật không, và nếu không thì hỏng ở đâu?**

Ưu tiên cao nhất không phải tính năng còn thiếu — mà là **sai sổ âm thầm** và **mất dữ liệu**.

## Ba nghi vấn phải xác minh trước tiên

Ghi nhận từ khảo sát S000 ở mức E0 (quan sát đọc code, chưa chạy). T-03 phải nâng lên E1 bằng
cách dựng ca kiểm thử thật và quan sát hành vi:

**NV-1 — Release vốn có thể trả nhầm pool khi có nhiều tháng.**
Nghi vấn: hàm chọn tháng hiện hành trả về tháng có key lớn nhất trong state, không phải tháng
của ladder đang release. Kịch bản kiểm: nạp vốn tháng 8 → tạo ladder từ vốn tháng 8 → nạp vốn
tháng 9 → hủy ladder → quan sát tiền về pool tháng nào. Nếu về tháng 9, bất biến
`TOTAL = AVAILABLE + RESERVED + DEPLOYED` của tháng 8 vỡ.

**NV-2 — Mức unlock không giới hạn số vốn được reserve.**
Nghi vấn: hàm reserve chỉ kiểm vốn available, không nhân với unlock. Strategy §12 nói rõ
"không được reserve vốn chưa unlock". Kịch bản kiểm: đặt OSCORE ở mức unlock thấp (ví dụ
OSCORE 40 → smart unlock ≈ 0,14) rồi thử reserve toàn bộ pool Smart.

**NV-3 — Trạng thái dữ liệu INVALID không chặn action mới.**
Nghi vấn: Strategy §3 bắt INVALID phải chặn mọi action Smart và Opportunity mới; app chỉ hiện
banner. Kịch bản kiểm: đưa data quality về INVALID rồi thử tạo ladder.

Mỗi nghi vấn kết luận: XÁC NHẬN LÀ LỖI / KHÔNG PHẢI LỖI / KHÔNG KIỂM ĐƯỢC, kèm bằng chứng chạy.

## Câu hỏi tiếp theo

4. Dữ liệu người dùng có thể mất theo những đường nào, và đường nào không có lối thoát?
5. Bộ test của webapp có thật sự bảo vệ được hồi quy không?
6. Parity check giữa `engine.js` và Python phủ được bao nhiêu phần bề mặt chiến lược?
7. Khoảng cách giữa app hiện tại và hình dung "dùng như bảng tính" của chủ dự án là gì?

## Scope

Được đọc và chạy:
- Toàn bộ `webapp/`, `src/eth_dca_os/live_export.py`
- `docs/spec/01_PRODUCT_SPEC_V2_1_5.md`, `02_STRATEGY_SPEC_V2_1_5.md`
- Build app ra thư mục tạm **ngoài repo** và chạy thử trong trình duyệt để dựng ca kiểm thử
- Sinh seed bằng dữ liệu tổng hợp để có dữ liệu chạy thử

## Out of Scope

- Sửa bất kỳ file nào trong `webapp/`, `src/`, `tests/`
- Viết test mới vào repo — đó là remediation
- Thiết kế kiến trúc lưu trữ mới — đó là T-09B
- Đặc tả cảnh báo — đó là T-08

## Dependencies
- T-01

## Blocks
- T-04, T-09A

## Parallel-Safe With
- T-02

## Expected Touch Area

Allowed:
- `docs/reviews/S001-audit-findings-webapp.md` (tạo mới)
- `PROJECT/PROJECT_PROGRESS.md`

Do not touch without Scope Expansion:
- `webapp/`, `src/`, `tests/`, `docs/spec/`

## Subtasks
- [ ] 03.1 Build app ra thư mục tạm ngoài repo; ghi lại chính xác những gì còn thiếu để build
- [ ] 03.2 Dựng ca kiểm thử cho NV-1 và kết luận
- [ ] 03.3 Dựng ca kiểm thử cho NV-2 và kết luận
- [ ] 03.4 Dựng ca kiểm thử cho NV-3 và kết luận
- [ ] 03.5 Lập bản đồ đường mất dữ liệu; đánh dấu đường nào không có lối thoát
- [ ] 03.6 Đánh giá bộ test webapp: có assertion nào fail được không, chạy được từ checkout sạch không
- [ ] 03.7 Định lượng phạm vi parity: liệt kê đại lượng nào được đối chiếu, đại lượng nào không
- [ ] 03.8 Kiểm validate đầu vào: giá trị vô lý có bị chặn không (ví dụ giá ETH sai một chữ số)
- [ ] 03.9 Đối chiếu app với Product Spec §4 dual-unit, §5 treasury, §11 hero, §12 panel
- [ ] 03.10 Ghi nhận khoảng cách so với hình dung "dùng như bảng tính" (sửa/xóa bản ghi, hoàn tác, lọc)
- [ ] 03.11 Viết Audit Findings có Severity + Evidence Level

## Ready Gate

- [x] Câu hỏi/ẩn số được nêu rõ — NV-1..NV-3 và 4 câu hỏi
- [x] Learning objective được định nghĩa
- [x] Phạm vi và giới hạn được định nghĩa
- [x] Phương pháp thu bằng chứng được định nghĩa — dựng ca kiểm thử thật, không đọc code rồi suy
- [x] Định dạng đầu ra được định nghĩa
- [ ] T-01 DONE
- [ ] Xác nhận lại khi mở task

## Completion Gate

### CHECK-03-01 — Ba nghi vấn NV-1..NV-3 đều được kiểm bằng ca chạy thật
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Cập nhật tại WP-C1 (`docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md`,
CHECK-C1-03/04/05/06), chạy thật trên `app_final.html` đã build, seed DEMO/SYNTHETIC sinh bằng
`ethdca synth` + `ethdca export-live`:

- **NV-1 (= V-01) — XÁC NHẬN LÀ LỖI.** `webapp/test_v01_v02_v03.js` + `webapp/test_multi_month_invariant.js`:
  huỷ/invalidate một ladder thuộc tháng A sau khi tháng B (mới hơn) trở thành `currentMonth()`
  khiến `releaseLadder()` (`webapp/app_logic.js:302-322`, dùng `currentMonth()` thay vì tháng
  gốc của ladder) hoặc (a) cộng nhầm vốn vào `smart.a` của tháng B trong khi rút nhầm từ
  `smart.r` đang backing một ladder RIÊNG, vẫn ACTIVE, của tháng B — hoặc (b) khiến vốn của
  tháng A kẹt vĩnh viễn ở `smart.r` nếu tháng B không có reserved sẵn. Cả hai đều quan sát
  được bằng chạy thật, kèm assertion PASS.
- **NV-2 (= V-02) — XÁC NHẬN LÀ LỖI.** `webapp/test_v01_v02_v03.js`: với Smart unlock đo được
  = 0,0% (OSCORE thật của seed synthetic), `reserveFor()` (`webapp/app_logic.js:289-297`) vẫn
  cho reserve 100% Smart available — không có so sánh nào với `view.smartUnlock`.
- **NV-3 (= V-03) — KHÔNG PHẢI LỖI về mặt hành vi quan sát được, nhưng an toàn một cách tình
  cờ.** `webapp/test_v01_v02_v03.js`: mọi trạng thái đạt được `data_quality = INVALID` (cần
  <7 ngày lịch sử để 8/8 sub-factor đều NaN — `webapp/engine.js` `factorScores`) đều đã có
  `adr30` = NaN (cần ≥30 ngày), nên `createLadder()` luôn bị chặn bởi guard "Chưa đủ lịch sử
  để tính ADR30" (`webapp/app_logic.js:327`) — KHÔNG phải một kiểm tra `data_quality` tường
  minh (không hề tồn tại trong `createLadder()`, dòng 324-335). Hành vi hiện tại khớp yêu cầu
  Strategy §3 trong mọi trạng thái quan sát được, nhưng cơ chế bảo vệ này dễ vỡ nếu logic
  spacing thay đổi độc lập với data_quality trong tương lai — ghi HARDENING trong
  `PROJECT/HARDENING_BACKLOG.md`, không phải BLOCKING.

Ba nghi vấn đều có kết luận dứt khoát, không nghi vấn nào còn E0. Chi tiết đầy đủ + output
chạy thật: `docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md` §Completion Gate.

### CHECK-03-02 — Bản đồ đường mất dữ liệu được lập đầy đủ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Bản đồ đường mất dữ liệu đã lập tại S000 (8 đường, gồm 3 đường không có lối thoát: localStorage bị xoá khi chưa publish, publish không khả dụng do thiếu quyền writer, export thất bại im lặng khi không có capability `downloads`). Ghi trong RSK-001.

### CHECK-03-03 — Tình trạng thật của bộ test webapp được xác định
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Chạy thật: hai test webapp PASS nhưng CHỈ sau khi dựng thủ công `app_final.html` (phải build) và `demo/results3/live_seed.json` (không tồn tại ở bất kỳ đâu trong repo). Không chạy được từ bản checkout sạch.

### CHECK-03-04 — Phạm vi parity được định lượng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Parity chỉ phủ **OSCORE tổng** trên 40 ngày, lệch tối đa 7,39e-11. KHÔNG phủ: unlock, spacing, phân bổ ladder, invalidation price, regime. Ghi trong F-008.

### CHECK-03-05 — Đối chiếu với Product Spec §4, §5, §11, §12 hoàn tất
Priority:
RECOMMENDED

Status:
PASS

Evidence Level:
E0

Evidence:
Đối chiếu Product Spec §4 dual-unit, §5 treasury, §11 hero, §12 panel — kết quả trong compliance matrix nhóm I và trong khảo sát S000.

### CHECK-03-06 — Không có file mã nguồn nào bị sửa
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`git status --porcelain` cuối phiên: không mục nào thuộc `webapp/`, `src/`, `tests/`, `docs/spec/`.

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Ba nghi vấn đều có kết luận dứt khoát kèm bằng chứng chạy
- [ ] Mỗi phát hiện có Severity, Evidence, Evidence Level, Recommended Fix, Suggested Task
- [ ] Không có file mã nguồn nào bị sửa
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật

## Escalation Triggers

- Xác nhận NV-1 hoặc NV-2 là lỗi thật → nâng Severity lên HIGH tối thiểu, và **báo chủ dự án
  ngay trong phiên**: nếu đang dùng app để ghi tiền thật thì phải dừng dùng hoặc xuất dữ liệu
  ra ngoài trước khi tiếp tục.
- Phát hiện đường mất dữ liệu không có lối thoát → CRITICAL, báo ngay.
- Không build được app → `MISSING_INPUT`, BLOCKED, ghi rõ thiếu gì. KHÔNG nâng Tier.

## Changed Files Registry

Created:
- (dự kiến) `docs/reviews/S001-audit-findings-webapp.md`

Modified:
- (dự kiến) `PROJECT/PROJECT_PROGRESS.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

Lưu ý về thứ tự ưu tiên: task này rất dễ trượt thành liệt kê tính năng còn thiếu, vì danh sách
đó dài. Nhưng tính năng thiếu thì **nhìn thấy được**; sai sổ âm thầm và mất dữ liệu thì **không**.
Nếu hết thời gian, hoàn thành NV-1..NV-3 và bản đồ mất dữ liệu trước; đối chiếu Product Spec
để sau.

Ghi nhận sẵn để T-03 xác minh, không thừa nhận: app không có cơ chế thông báo chủ động nào —
mọi cảnh báo chỉ hiện khi người dùng mở trang. Nếu giá chạm zone lúc người dùng không mở app
thì không có gì báo. Điều này khớp với việc Implementation Plan §9 cố ý hoãn notification, và
là lý do T-08 phải đặc tả lớp cảnh báo trước khi T-10 triển khai.

---

## Kết quả S001 — BLOCKED

**Task KHÔNG đạt DONE.** `governance/core/TASK_COMPLETION_GATE_STANDARD.md` quy định: bất kỳ
REQUIRED check nào ở trạng thái FAIL, BLOCKED hoặc NOT_TESTED đều chặn DONE.

CHECK-03-01 là REQUIRED và bị **BLOCKED**: chứng minh ba nghi vấn NV-1/NV-2/NV-3 đòi dựng ca
kiểm thử mới, mà quy tắc S001 số 10 của chủ dự án cấm viết test mới trong phiên audit.
Đây là **xung đột có chủ đích giữa Ready Gate của task và quy tắc phiên**, không phải thất bại
kỹ thuật.

Năm REQUIRED/RECOMMENDED check còn lại đều PASS.

**Ba nghi vấn vẫn ở mức E0** và KHÔNG được coi là kết luận. Chuyển thành verification task
V-01, V-02, V-03 cho phase sau (xem `docs/reviews/S001-audit-findings.md`).

Thu hẹp được một phần bằng bằng chứng E1: `webapp/test_zone.js` cho thấy bất biến
`TOTAL = A + R + D` giữ đúng trong kịch bản **một tháng**. Điều này không bác bỏ NV-1 vì NV-1 nói
về kịch bản **đa tháng** — đúng điểm mù của test hiện có.

---

## Cập nhật WP-C1 — 2026-09-02

CHECK-03-01 chuyển **BLOCKED → PASS** (E0 → E1) dựa trên bằng chứng chạy thật do WP-C1 cung
cấp — xem khối Evidence cập nhật ở trên và `docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md`.
Chỉ trạng thái/evidence của CHECK-03-01 được sửa; nội dung yêu cầu của check không đổi
(CHECK-C1-08).

Với CHECK-03-01 nay PASS, cả năm REQUIRED check của T-03 đều PASS (03-01, 03-02, 03-03, 03-04,
03-06) và RECOMMENDED 03-05 cũng PASS. Trường `Status` ở đầu file chuyển `BLOCKED` → `VERIFYING`
(gỡ trạng thái chặn, KHÔNG tự đóng `DONE`) — WP-C1 chỉ được phép sửa trạng thái CHECK-03-01,
không được tự đóng một task khác; việc chuyển `Status` của T-03 sang `DONE` (đối chiếu đủ toàn
bộ Exit Criteria, gồm xác nhận `docs/reviews/S001-audit-findings.md` đã đủ vai trò của
`docs/reviews/S001-audit-findings-webapp.md` như dự kiến ban đầu) cần một phiên riêng cho T-03.

**Escalation theo đúng trigger của T-03 và WP-C1**: NV-1 và NV-2 đều được **XÁC NHẬN LÀ LỖI
THẬT** trong lần chạy này. Nếu chủ dự án đang dùng `webapp/app_final.html` để ghi giao dịch
tiền thật, cần dừng dùng hoặc xuất dữ liệu (`localStorage`) ra ngoài trước khi tiếp tục dùng
app, cho tới khi T-09A vá xong. Severity nâng lên tối thiểu HIGH.
