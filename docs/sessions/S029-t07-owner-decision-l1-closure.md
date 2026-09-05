# S029 — Owner Decision: T-07 chọn L-1, lifecycle closure (DEC-040)

Ngày: 2026-09-05. Nhánh: `claude/t-07-decision-prep-1oprq1` (tiếp nối `S027`, `S028`).

## 1. Bối cảnh

Sau khi `S028` canonicalize evidence replay RQ-1/RQ-3/RQ-4 (dataset official T-06) và cập nhật
`docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` §10 (Decision Impact), Owner đọc cả hai tài liệu
(`T07-OWNER-DECISION-BRIEF.md` và `T07-RQ-EVIDENCE-INVESTIGATION.md`) và ra quyết định thực thi
`T-07` lần đầu tiên.

## 2. Owner Decision

Owner chọn **L-1 — benchmark đơn giản hơn**, một trong hai lựa chọn canonical đã đóng khung tại
`T07-OWNER-DECISION-BRIEF.md` §7 (nguyên văn Implementation Plan §5, dòng `DO NOT BUILD`). Lý do
Owner nêu: evidence replay mới (Control F P95 chỉ 2/9 window, Control G P95 chỉ 3/9, `OOS` thua
cả hai control ở cả median lẫn P95) làm yếu giả thuyết timing edge ổn định; capital-allocation
mismatch mới ở mức PARTIALLY_ESTABLISHED, chưa đủ để mở V2.2.

Owner tường minh:
- Giữ nguyên: `V2.1.5 = FAILED`, verdict `= DO_NOT_BUILD`, `can_proceed_to_app = false`, `T-11`
  theo quy tắc downstream canonical, `DEC-005` không đổi trừ khi resolve riêng.
- Uỷ quyền: ghi Owner Decision tiếp theo và hoàn tất `T-07` theo đúng authority repository.
- Cấm: triển khai thay đổi sản phẩm downstream trong phiên này; dừng ngay sau khi đóng lifecycle
  `T-07`.

## 3. Việc đã làm

1. Ghi `DEC-040` (`PROJECT/PROJECT_DECISIONS.md`) — canonical hoá lựa chọn L-1, dẫn nguyên Owner
   Response, đối chiếu với ý nghĩa L-1 đã đóng khung TRƯỚC KHI Owner chọn (không viết lại sau khi
   biết lựa chọn — đúng nguyên tắc chống hậu nghiệm của `DEC-031`/Master Index §6), giải thích rõ
   `T-11` chuyển từ "blocked chờ dependency" sang "not-applicable vĩnh viễn dưới V2.1.5".
2. `T-07: READY → DONE` trong `PROJECT/PROJECT_PROGRESS.md` (bảng roadmap + sơ đồ phụ thuộc +
   narrative "Last Updated").
3. **Không** đổi Status column của `T-11` (giữ nguyên `PLANNED` — sai lệch trình bày đã ghi nhận
   từ trước, ngoài phạm vi quyết định này) — chỉ cập nhật văn bản mô tả trong sơ đồ phụ thuộc và
   dòng roadmap `T-07` để phản ánh đúng: `T-11` vẫn `BLOCKED` trên thực tế, verdict không bao giờ
   `BUILD` được nữa dưới V2.1.5.
4. **Không** chạm `PROJECT/CAPABILITY_REGISTRY.md` hay `PROJECT/REVIEW_BUDGET_LEDGER.md` — `T-07`
   là Tier `DUYET`, không có Completion Gate/budget riêng, không phải thành viên capability
   lineage nào; không tìm thấy tham chiếu `T-07` trong hai file đó.
5. Chạy `sync_easy_roadmap.py` + `validate_easy_roadmap.py` + bốn validator governance khác — tất
   cả PASS.

## 4. Trạng thái sau quyết định

`T-07 = DONE` (`DEC-040`). Giữ nguyên tuyệt đối: `T-06 = DONE` (lịch sử, `DEC-031`); verdict
official `= DO_NOT_BUILD`; `V2.1.5 validation = FAILED` (vĩnh viễn); `can_proceed_to_app = false`;
`GATE-B = CLOSED` (`DEC-038`); `DEC-005 = PENDING`. `T-11` vẫn `BLOCKED`/not-applicable dưới
V2.1.5. Không mở `V2.2`/`WP-D2`/`WP-C3`/`WP-C4`/`T-08`. Không resolve `DEC-005`. Không chọn
Objective A/C. Không sửa `src/`/`tests/`/`webapp/`. Không task ID mới.

Production diff = EMPTY (`git diff 53a63c4 -- src/eth_dca_os webapp pyproject.toml pyproject.lock
tests` rỗng). Thay đổi: `PROJECT/PROJECT_DECISIONS.md` (+`DEC-040`), `PROJECT/PROJECT_PROGRESS.md`
(bảng roadmap + sơ đồ + narrative), `PROJECT/LO_TRINH_DE_HIEU.md` (regenerate),
`docs/sessions/S029-t07-owner-decision-l1-closure.md` (mới).

Validators: `sync_easy_roadmap.py`, `validate_easy_roadmap.py`, `validate_governance.py`,
`validate_structure.py`, `validate_project_state.py`, `validate_routing.py` — tất cả PASS.

## 5. Dừng lại

Đúng theo chỉ thị Owner: "STOP after T-07 lifecycle closure." Phiên này KHÔNG triển khai bất kỳ
thay đổi sản phẩm downstream nào. `T-07` đã đóng lifecycle hoàn chỉnh. Bước tiếp theo (nếu có)
thuộc về một phiên/quyết định riêng của Owner — không được suy diễn hay bắt đầu ở đây.
