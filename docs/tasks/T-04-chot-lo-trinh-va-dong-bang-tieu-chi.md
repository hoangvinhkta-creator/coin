# T-04 — Chốt lộ trình và đóng băng tiêu chí

## Metadata
Status:
DONE

Phase:
Phase 1.5 — Roadmap Finalization (S002)

Task Mode:
MAJOR

Chế độ phiên:
PLANNING / GATE FREEZE — không remediation, không sửa mã sản phẩm

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 3
X: 3
U: 2
V: 2
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
2.6

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
xhigh

Difficulty:
3/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Biến 15 work package của RCP-001 — hiện mới có tên, Tier/Effort và dependency trong bảng roadmap
chuẩn — thành 15 file định nghĩa task đầy đủ, mỗi file có Ready Gate, Completion Gate với REQUIRED
checks riêng, yêu cầu Evidence và Exit Criteria, rồi **đóng băng** trước khi gói đầu tiên được thực thi.

Lý do task này tồn tại: `governance/core/00_SESSION_ORCHESTRATION.md` mục "Roadmap Finalization"
yêu cầu Completion Gate được finalize và freeze **trước** khi một task chuyển READY. Nếu gate được
soạn trong chính phiên thực thi, người soạn gate và người phải vượt gate là một — tiêu chí sẽ bị
uốn theo kết quả. Đây là cơ chế chống chính rủi ro đó.

## Vì sao gate phải riêng cho từng gói

Master Index §6 cấm chạy lại official run để làm đẹp kết quả. Vì vậy chất lượng của lần chạy đầu
tiên là không thể làm lại, và mỗi work package đứng trước nó phải có tiêu chí phản ánh đúng
**failure mode riêng** của nó. Một bộ gate chung chung sẽ PASS ở cả 15 gói mà không chứng minh
được điều gì.

## Scope

Được phép:
- Tạo/cập nhật file định nghĩa task dưới `docs/tasks/`.
- Soạn Ready Gate, Completion Gate, REQUIRED checks, Evidence Requirements, Exit Criteria.
- Cập nhật `PROJECT/PROJECT_PROGRESS.md` (trạng thái, blocker, rủi ro, quyết định, session history).
- Cập nhật `PROJECT/PROJECT_DECISIONS.md`.
- Sinh lại `PROJECT/LO_TRINH_DE_HIEU.md` bằng `sync_easy_roadmap.py`.
- Tạo bản ghi phiên dưới `docs/sessions/` và artifact đối chiếu dưới `docs/reviews/`.
- Chạy validator governance.

## Out of Scope

- Sửa `src/`, `webapp/`, `tests/`, `docs/spec/`.
- Sửa thuật toán ETH DCA.
- Remediation bất kỳ finding F-xxx, V-xx hay S-xxx nào.
- Bắt đầu thực thi WP-A1…WP-D2.
- Chạy official backtest.
- Sửa `governance/scripts/governance/routing_engine.py` hoặc `validate_routing.py`.
- Tự chốt DEC-005.
- Tự mở T-05, T-06 hay bất kỳ task nào sau T-04.

## Dependencies
- T-01 (DONE)
- T-02 (DONE)
- T-03 (BLOCKED — không chặn T-04; T-03 đóng góp đầu vào đã có ở mức đã thu được, phần còn thiếu
  được T-04 chuyển thành gate của WP-C1 chứ không được coi là đã kết luận)

## Blocks
- WP-A1, WP-A2, WP-A3, WP-A4, WP-A5, WP-A6
- WP-B1, WP-B2, WP-B3
- WP-C1, WP-C2, WP-C3, WP-C4
- WP-D1, WP-D2

## Parallel-Safe With
- Không có. T-04 là điểm hội tụ governance của toàn bộ chương trình remediation.

## Expected Touch Area

Allowed:
- `docs/tasks/*.md`
- `docs/sessions/S002-*.md`
- `docs/reviews/S002-*.md`
- `PROJECT/PROJECT_PROGRESS.md`
- `PROJECT/PROJECT_DECISIONS.md`
- `PROJECT/LO_TRINH_DE_HIEU.md` (chỉ qua generator)

Do not touch without Scope Expansion:
- `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`

## Subtasks
- [x] 04.1 Đọc source of truth theo thứ tự governance yêu cầu
- [x] 04.2 Xác minh lại routing của 15 work package bằng `routing_engine.py` (không chọn tay)
- [x] 04.3 Soạn 15 file định nghĩa task từ `governance/templates/TASK_DEFINITION_TEMPLATE.md`
- [x] 04.4 Đưa DEC-009 thành REQUIRED check tường minh của WP-B1
- [x] 04.5 Bảo toàn đủ 8 trường provenance của T-06A cũ trong WP-A1
- [x] 04.6 Tách trách nhiệm đo lường (WP-A5) khỏi trách nhiệm chính sách verdict (WP-B1)
- [x] 04.7 Đối chiếu coverage: 33 finding + V-01..V-03 + S-001..S-003 + rủi ro + DEC-007/008/009
- [x] 04.8 Cập nhật roadmap chuẩn và sinh lại roadmap dễ hiểu
- [x] 04.9 Chạy toàn bộ validator bắt buộc và báo cáo trung thực kể cả giới hạn coverage
- [x] 04.10 Ghi bản ghi phiên S002 và xác định task READY kế tiếp

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependencies DONE hoặc được miễn trừ tường minh (T-03 BLOCKED — miễn trừ có ghi nhận: T-04 chỉ
      định nghĩa gate cho WP-C1, không kết luận thay T-03)
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu (RCP-001, S001 findings, compliance matrix)
- [x] Data impact được biết (T-04 không chạm dữ liệu sản phẩm)
- [x] Security impact được biết (không có; không chạm auth/secret)
- [x] Routing impact được biết — DEC-008 override của WP-A2 sẽ va chạm với `validate_routing.py`
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Primary agent tier được gán bằng router, không chọn tay
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi

## Completion Gate

Đóng băng: 2026-08-23 (S002, trước khi soạn nội dung 15 file).

### CHECK-04-01 — Đủ 15 file định nghĩa task tồn tại và theo đúng canonical template
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Script đối chiếu chạy thật trên `docs/tasks/WP-*.md`: **15/15 file tồn tại**, và mỗi file có đủ 14 mục
bắt buộc của canonical template (`Objective`, `Scope`, `Out of Scope`, `Dependencies`, `Blocks`,
`Parallel-Safe With`, `Expected Touch Area`, `Subtasks`, `Ready Gate`, `Completion Gate`,
`Exit Criteria`, `Escalation Triggers`, `Changed Files Registry`, `Notes`) cộng 22 trường metadata
(gồm `Routing Inputs`, `Difficulty`, `Risk`, `Blast Radius`, `Completion Gate Freeze`).
Output: `Thiếu mục bắt buộc: KHÔNG`.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-02 — Mỗi WP có Ready Gate riêng, phản ánh điều kiện khởi động thật của gói đó
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
15/15 file có mục `## Ready Gate` với điều kiện riêng, không phải bản sao. Các điều kiện đặc thù đã
kiểm: WP-A2 có điều kiện BLK-003 (routing validation); WP-A4, WP-A5, WP-A6, WP-C4 có điều kiện
dependency gói cụ thể được đánh dấu **bắt buộc, không miễn trừ**; WP-C2 có điều kiện DEC-005 cộng
ADR; WP-B1 có điều kiện T-06 DONE và WP-A5 DONE. Ba gói có Ready Gate dẫn tới trạng thái BLOCKED
thật (WP-A2, WP-C2, và điều kiện BLOCKED của CHECK-B3-02), không phải hình thức.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-03 — Mỗi WP có Completion Gate với REQUIRED checks riêng theo failure mode của gói
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
**125 REQUIRED check** trong 15 file, phân bố 6–11 check mỗi gói theo độ phức tạp, không phải một bộ
chung nhân bản. Mỗi gói có ít nhất một check gắn trực tiếp vào failure mode riêng — ví dụ
CHECK-A3-01 (chuỗi CRASH → RECOVERY → STRESSED giải phóng reserve), CHECK-A6-02 (sai lệch thứ tự
được xác định ở mức E1 **trước** khi sửa), CHECK-C1-03 (ca đa tháng cho V-01), CHECK-D1-05 (kết quả
mô phỏng không đổi). Kiểm chéo phạm vi ở `docs/reviews/S002-coverage-regression-check.md` §8: 15/15
gói có REQUIRED check đóng vai rào chắn phạm vi.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-04 — Mọi REQUIRED check đều khai báo Evidence Level và không dùng E0 cho việc bản chất cần E1
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Script kiểm: **125/125 REQUIRED check** đều khai báo `Evidence Level` và `Status` hợp lệ. Output:
`REQUIRED check thiếu Evidence Level/Status: KHÔNG`.
Phân bố: **E1 = 116, E2 = 4, E0 = 5**.
Bốn check E2 nằm ở đúng bốn gói quyết định tính toàn vẹn của verdict (WP-A1, WP-A3, WP-A6, WP-B1) —
phù hợp `EVIDENCE_STANDARD.md` mục Risk 4–5 ("security/data-critical checks SHOULD have E2"), ở đây
được nâng thành REQUIRED.
Năm check E0 đều là check **tài liệu hoặc lập luận thiết kế**, không phải mệnh đề kiểm chứng được
bằng chạy: CHECK-C2-07 (biện minh thiết kế trong ADR) và CHECK-D2-01/02/03/05 (nội dung của một tài
liệu đề xuất). Không check nào bản chất cần E1 mà bị hạ xuống E0.
Trạng thái mặc định của cả 125 check là `NOT_TESTED` — đúng theo `EVIDENCE_STANDARD.md`; T-04 soạn
gate, không thực hiện gate.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-05 — Routing metadata của 15 file tái lập được bằng router, ngoại lệ duy nhất là override đã được phê duyệt
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Chạy `routing_engine.py` cho từng bộ D/R/B/A/X + U/V/H/C/F của 15 gói và của T-04:
**15/16 khớp tuyệt đối** Tier, Effort, model floor và effort floor với bảng roadmap chuẩn.
`validate_routing.py` cho cùng kết luận, với **đúng một lỗi**:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây là ngoại lệ **duy nhất** và là ngoại lệ **đã được phê duyệt** (DEC-008), được ghi trong file
WP-A2 dưới hai trường `Manual Override` và `Router Raw Output` đúng như DEC-008 mục Impact yêu cầu.
Không Tier/Effort nào khác được chọn tay. Hệ quả tooling được đăng ký thành **BLK-003** và
**DEC-010**; WP-A2 giữ trạng thái BLOCKED. Chi tiết: `docs/reviews/S002-coverage-regression-check.md`
mục PH-02.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-06 — DEC-009 trở thành REQUIRED check tường minh của WP-B1
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`CHECK-B1-02` trong `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` có
`Priority: REQUIRED` (xác nhận bằng script). Nội dung check ghi tường minh hai bước bắt buộc:
(1) xác định remediation có ảnh hưởng input / calculation / execution behavior / dataset
interpretation / strategy behavior / backtest behavior theo cách tác động Gate 1 hay không;
(2) nếu có, mọi kết quả Gate 1 tạo trước đó bị đánh dấu `STALE / INVALIDATED`, Gate 1 phải chạy lại,
và chỉ kết quả mới được dùng cho verdict và T-07. Check ghi rõ điều kiện FAIL và ghi rõ rằng WP-B1
không được DONE khi check này chưa được chứng minh. Không phải ghi chú, không phải OPTIONAL.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-07 — WP-A1 bảo toàn đủ 8 trường provenance mà DEC-007 quyết định 3 yêu cầu
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Script kiểm sự có mặt của cả tám trường trong `docs/tasks/WP-A1-provenance-va-tai-lap.md`:
`python_version`, `dependency_lock_hash`, `code_commit`, `dataset_hash`, `strategy_config_hash`,
`execution_config_hash`, `sensitivity_manifest_hash`, `seed` — **8/8 CÓ**.
CHECK-A1-01 (REQUIRED, E1) đòi cả tám có mặt trong một run record thật, và bằng chứng phải là nội
dung record in ra, không phải mô tả. WP-A1 cũng giữ nguyên hai verification criteria khắt khe nhất
của T-06A cũ và của RCP-001: CHECK-A1-06 (synth không thể cho `official: true`) và CHECK-A1-07
(không flag hay biến môi trường nào ép được `official`).

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-08 — Coverage: không finding / risk / dependency / decision / stopping rule nào bị rơi
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Đối chiếu bằng script, kết quả đầy đủ ở `docs/reviews/S002-coverage-regression-check.md`:
- **Finding: 40/40** định danh (34 `F-xxx` + 3 `V-xx` + 3 `S-xxx`) có đúng một nơi thuộc về; danh
  sách "không có owner" là rỗng. Ba trường hợp xuất hiện ở hai file đã được kiểm từng cái: F-002
  chia có chủ đích (A5 đo lường / B1 chính sách), F-019 và F-029 là **ghi chú loại trừ**, không phải
  sở hữu kép.
- **Rủi ro: 10/10** có nơi thuộc về; hai rủi ro (RSK-001 → T-09B, GOV-RSK-001 → MICRO-GOVDEF-001)
  cố ý nằm ngoài 15 gói, đúng roadmap chuẩn.
- **Dependency: 15/15** khớp bảng roadmap chuẩn; ràng buộc tuần tự hoá do xung đột file
  (WP-A3 ∦ WP-A4, WP-A2 ∦ WP-A5) được bảo toàn.
- **DEC-007 / DEC-008 / DEC-009: 9/9** điều kiện được kiểm và đạt.
- **Stopping rule: 9/9** mệnh đề có nơi cưỡng chế.
Phát sinh **PH-01**: bảng tóm tắt của S001 ghi 33 finding trong khi danh mục liệt kê 34 `F-xxx` +
3 `S-xxx`. Đây là sai số **đếm tổng**, không phải finding bị rơi — đã ghi vào Open Regression Items;
T-04 không tự sửa biên bản audit của một phiên đã đóng.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-09 — Không work package nào bị mở rộng sang remediation ngoài phạm vi RCP-001
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
15/15 gói có ít nhất một REQUIRED check đóng vai rào chắn phạm vi — bảng đầy đủ tại
`docs/reviews/S002-coverage-regression-check.md` §8. Bốn ranh giới dễ trượt nhất được đặt tường minh:
(1) WP-A5 **đo lường** so với WP-B1 **chính sách verdict** — có bảng ranh giới trách nhiệm ở cả hai
file; (2) WP-C1 **kết luận** so với T-09A **sửa** — CHECK-C1-07 cấm sửa logic app; (3) WP-A3 sở hữu
**Market Regime**, WP-C2 sở hữu **Execution State** — không gói nào định nghĩa lại chiều của gói kia;
(4) WP-C3 **tầng sản phẩm** so với backtest — CHECK-C3-05 cấm chạm backtest và Out of Scope cấm thêm
partial fill vào engine (đổi giả định ma sát, Master Index §6).
Không gói nào được giao thêm finding ngoài ánh xạ của RCP-001 §6.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-10 — Không file mã sản phẩm nào bị sửa trong T-04
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`git status --porcelain` cuối phiên không có mục nào thuộc `src/`, `webapp/`, `tests/`, `docs/spec/`
hay `governance/`. Toàn bộ thay đổi nằm ở `docs/tasks/`, `docs/reviews/`, `docs/sessions/` và
`PROJECT/`. `routing_engine.py` và `validate_routing.py` **không bị sửa**, đúng chỉ thị của chủ dự án
và đúng phân công của DEC-008.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-11 — Roadmap dễ hiểu được sinh lại và đồng bộ tuyệt đối với roadmap chuẩn
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Chạy `python governance/scripts/governance/sync_easy_roadmap.py` →
`ROADMAP SYNC: PASS - wrote PROJECT/LO_TRINH_DE_HIEU.md`.
Chạy `python governance/scripts/governance/validate_easy_roadmap.py` → `EASY ROADMAP: PASS`.
Validator này sinh lại nội dung kỳ vọng trong bộ nhớ và so khớp từng byte, nên PASS ở đây có nghĩa
roadmap dễ hiểu đồng bộ tuyệt đối với bảng chuẩn. Không dòng tick nào bị chỉnh tay.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

### CHECK-04-12 — Toàn bộ validator bắt buộc được chạy thật và kết quả được báo cáo kèm giới hạn coverage
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Bốn validator bắt buộc đã chạy thật, kết quả nguyên văn:

```
GOVERNANCE STRUCTURE: PASS   (Checked 27 required paths.)
PROJECT STATE: PASS
ROUTING VALIDATION: FAIL     (1 lỗi — WP-A2, override DEC-008; xem CHECK-04-05, BLK-003, DEC-010)
EASY ROADMAP: PASS
```

Hai validator còn lại cũng đã chạy, và **kết quả PASS của chúng phải đọc kèm giới hạn coverage**:

```
EVIDENCE VALIDATION: PASS    (Checked 0 REQUIRED PASS evidence record(s).)
TASK COMPLETION: PASS        (Checked 0 DONE task(s).)
```

Cả hai chỉ quét `docs/tasks/TASK-*.md`, trong khi quy ước đặt tên thực tế của repo là `T-01-*.md`,
`WP-A1-*.md`… nên chúng đang **PASS trên tập rỗng**. Chúng KHÔNG chứng minh điều gì về 125 REQUIRED
check vừa được đóng băng. Ghi nhận trung thực theo yêu cầu; sửa chúng nằm ngoài phạm vi T-04 (đụng
`governance/scripts/`).

Cảnh báo đã có từ S000 vẫn đúng nguyên: các dòng PASS này nói về **khung**, không nói về **chất
lượng implementation**. Sau T-04, số task DONE ở tầng sản phẩm vẫn là 0.

Executed By:
Agent phiên S002 (T-04)

Timestamp:
2026-08-23

## Exit Criteria
- [x] 100% REQUIRED checks PASS — 12/12
- [x] Không defect nghiêm trọng nào chưa được xử lý — hai phát hiện PH-01 và PH-02 đều ở mức
      tài liệu/tooling, đã đăng ký thành Open Regression Item, BLK-003 và DEC-010
- [x] Mức evidence yêu cầu được thoả — E1 cho cả 12 check
- [x] Tài liệu bắt buộc được cập nhật
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] `PROJECT/LO_TRINH_DE_HIEU.md` được sinh lại và validator đồng bộ PASS
- [x] Bản ghi phiên S002 được viết
- [x] Không hạ tiêu chuẩn gate của bất kỳ task nào để ép DONE — ngược lại, T-04 **tạo thêm** một
      blocker thật (BLK-003) thay vì hạ Tier WP-A2 để validator xanh

## Escalation Triggers

- Số lượng work package vượt khả năng đóng băng gate trong một phiên → chia T-04 thành nhiều phiên,
  KHÔNG nâng Tier (`VERIFICATION_DEPTH` không áp dụng cho vấn đề khối lượng).
- Chủ dự án chưa chốt DEC-005 → `MISSING_INPUT`, chuyển BLOCKED riêng cho nhánh T-08/WP-C2,
  KHÔNG chặn nhánh lớp A.
- Phát hiện xung đột governance thật giữa hai nguồn có thẩm quyền → `CONFLICT DETECTED`, ghi khối
  `RULE CONFLICT`, không tự chọn một cách hiểu.
- Phát hiện một finding không có nơi thuộc về sau khi gom 15 gói → `SCOPE_CHANGED`, mở
  `COMPLETION GATE CHANGE PROPOSAL` thay vì âm thầm nhét vào một gói gần nhất.

## Changed Files Registry

Created:
- `docs/tasks/T-04-chot-lo-trinh-va-dong-bang-tieu-chi.md`
- `docs/tasks/WP-A1-provenance-va-tai-lap.md`
- `docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md`
- `docs/tasks/WP-A3-regime-va-vong-doi-ladder.md`
- `docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md`
- `docs/tasks/WP-A5-instrumentation-failure-signal.md`
- `docs/tasks/WP-A6-thu-tu-xu-ly-18-buoc.md`
- `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md`
- `docs/tasks/WP-B2-bo-sung-test-requirement-con-thieu.md`
- `docs/tasks/WP-B3-audit-trail-decision-log.md`
- `docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md`
- `docs/tasks/WP-C2-execution-state-machine.md`
- `docs/tasks/WP-C3-partial-fill-tang-san-pham.md`
- `docs/tasks/WP-C4-mo-rong-parity-js-python.md`
- `docs/tasks/WP-D1-no-ky-thuat-khong-anh-huong-hanh-vi.md`
- `docs/tasks/WP-D2-de-xuat-v2-2-cho-khiem-khuyet-dac-ta.md`
- `docs/reviews/S002-coverage-regression-check.md`
- `docs/sessions/S002-t04-gate-freeze.md`

Modified:
- `PROJECT/PROJECT_PROGRESS.md`
- `PROJECT/PROJECT_DECISIONS.md`
- `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động)

Deleted:
- Không

Migration Impact:
- Không

## Notes

Cám dỗ lớn nhất của T-04 là viết 15 bộ gate na ná nhau rồi tuyên bố xong. Kiểm tra tự vấn cho mỗi
gói: *nếu gói này được làm sai một cách hợp lý nhất, check nào trong gate sẽ bắt được?* Nếu không
check nào bắt được thì gate đó chưa đủ.

T-04 **soạn** Completion Gate; T-04 **không thực hiện** Completion Gate của bất kỳ gói nào.
Trạng thái mặc định của mọi check trong 15 file là `NOT_TESTED` — đó là trạng thái đúng theo
`EVIDENCE_STANDARD.md`, không phải thiếu sót.

---

## Kết quả S002 — DONE (PASS WITH FINDINGS)

Mười hai REQUIRED check đều PASS ở mức E1. Đầu ra: 15 file định nghĩa task với **125 REQUIRED check**
đã đóng băng, cộng bản đối chiếu độ phủ `docs/reviews/S002-coverage-regression-check.md`.

Hai phát hiện được ghi nhận thay vì che đi:

- **PH-01** — bảng tóm tắt của S001 ghi 33 finding trong khi danh mục liệt kê 34 `F-xxx` + 3 `S-xxx`.
  Sai số đếm tổng; **không finding nào bị rơi** (40/40 có nơi thuộc về). Chờ chủ dự án quyết định
  cách đính chính biên bản audit của phiên đã đóng.
- **PH-02 → BLK-003** — `validate_routing.py` báo FAIL cho đúng một dòng: override DEC-008 của WP-A2.
  Đây là hệ quả **đã được DEC-008 dự đoán và hoãn lại cho một task riêng**. T-04 giữ nguyên override
  theo DEC-008, đăng ký blocker, và chuyển WP-A2 sang `BLOCKED` — thay vì hạ Tier để công cụ hài
  lòng. Cần chủ dự án quyết định **DEC-010**.

Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`. Không bắt đầu work package nào.
Không mở T-05 hay bất kỳ task nào sau T-04.
