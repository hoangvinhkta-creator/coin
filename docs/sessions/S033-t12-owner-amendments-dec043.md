# S033 — Owner Decision DEC-043: tu chỉnh `T-12` (persistence, golden baseline, repair authority)

Ngày: 2026-09-05
Nhánh: `claude/coindca-l1-step-a-task-1ka2zj`
SOURCE HEAD trước phiên: `c657cab` (đầu ra `S032`)
Loại phiên: **OWNER DECISION APPLICATION** — áp dụng tu chỉnh Owner vào task đã tạo ở `S032`,
không thi hành, không tạo task ID mới, production diff = 0.

---

## 1. Đầu vào

Owner Review toàn văn, chấp nhận `T-12` là ĐÚNG MỘT capability kế toán L-1 bước A, kèm ba tu
chỉnh: (1) phê duyệt kiến trúc persistence tối thiểu; (2) tách bạch khái niệm golden baseline,
cấm phụ thuộc dữ liệu thật của Owner; (3) pre-authorize một repair cycle có điều kiện. Chi tiết
đầy đủ ghi tại `DEC-043` (`PROJECT/PROJECT_DECISIONS.md`).

## 2. Thay đổi áp dụng vào `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`

1. **Metadata Status** — thêm đoạn "Amended 2026-09-05 (`S033`, `DEC-043`)" tóm tắt ba tu chỉnh
   và xác nhận 14 REQUIRED check không đổi.
2. **§ Persistence boundary** — thêm mục con "Persistence architecture — Owner-approved bounded
   scope (`DEC-043`)": liệt kê rõ ĐƯỢC PHÉP (schema `coindca.ledger/2` bên trong `ethdca/state`)
   và KHÔNG ĐƯỢC PHÉP (collection mới, sửa rules, đổi kiến trúc Firebase), cùng điều khoản "không
   suy diễn rộng".
3. **§ Change budget** — thay đoạn có câu gây hiểu lầm `GOLDEN_BASELINE_SHA = PENDING_OWNER_DATA`
   bằng bảng ba khái niệm (`T12_GOLDEN_ACCOUNTING_BASELINE` / `GOLDEN_BASELINE_SHA` tầng dự án /
   `OWNER_LOCAL_ACCEPTANCE`) và định nghĩa thời điểm đóng băng
   `T12_GOLDEN_ACCOUNTING_BASELINE_SHA` (SHA của commit đầu tiên đưa đủ 12 fixture SC vào).
4. **§ Budget review/repair** — đổi tiêu đề từ "KHÔNG tự cấp" thành "MỘT chu kỳ pre-authorized có
   điều kiện"; thêm mục con liệt kê chín điều kiện đồng thời và hệ quả khi không đủ điều kiện
   hoặc khi chu kỳ đã dùng mà vẫn FAIL.
5. **§ Stop conditions** — tách dòng "repair cycle" thành hai dòng (chu kỳ thứ nhất dùng
   pre-authorized; chu kỳ thứ hai cần Owner Decision mới); thu hẹp dòng
   `ARCHITECTURE_CHANGE_REQUIRED` về đúng phạm vi ngoài `DEC-043`.
6. **§ Ready Gate** — thêm mục con "Tái xác nhận Ready Gate sau `DEC-043`": xác nhận `READY` giữ
   nguyên, không `READY_GATE_FAIL`.
7. **§ Evidence / E2** — thêm câu xác nhận không đổi.
8. **§ Implementation authority** — làm rõ ranh giới của "không tự cấp repair budget" (chỉ được
   dùng đúng MỘT chu kỳ pre-authorized, tự đối chiếu điều kiện trước khi dùng).
9. **§ Notes** — thêm con trỏ tới `DEC-043`.

Bảng `Repair cycle tối đa` trong § Change budget cũng đổi từ "0 tự cấp" thành "1 pre-authorized
có điều kiện".

## 3. Không đổi

**14 REQUIRED check (`CHECK-T12-01`…`-14`) — không một chữ nào bị sửa.** SC-01…SC-12,
INV-1…INV-15, P-1…P-6, trần LOC/file, capability `CAP-WEBAPP`, lineage root `WP-C1`, cấm dữ liệu
tài chính thật, cấm UI redesign, cấm Firebase isolation/auth, cấm Research/Buy Score/regime,
cấm `V2.2` — tất cả giữ nguyên.

## 4. Governance

Ghi `DEC-043` vào `PROJECT/PROJECT_DECISIONS.md` (Owner Decision, cùng khuôn `DEC-040`/`DEC-041`/
`DEC-042`). Cập nhật canonical state holders:

- `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2 (dòng THÀNH VIÊN) + §2.2.6 (chú thích trỏ tới §2.2.7,
  không sửa lại nội dung lịch sử) + §2.2.7 mới (ghi pre-authorization, `USED` vẫn `0` vì
  pre-authorize ≠ tiêu thụ).
- `PROJECT/CAPABILITY_REGISTRY.md` §2.1 — thêm đoạn "Amended `S033`" tóm tắt ba tu chỉnh.
- `PROJECT/PROJECT_PROGRESS.md` — `Last Updated` (mục `S033` mới, đặt trước mục `S032`);
  `Current Task Snapshot` (khối `T-12` cập nhật với dòng Kiến trúc/Golden/Budget mới); `Next
  Session` (điều kiện phiên thi hành cập nhật theo `DEC-043`).
- `docs/reviews/L1-STEP-A-TASK-DEFINITION.md` — thêm Addendum `S033` ở cuối, không viết lại nội
  dung 12 mục gốc.

Không sửa `PROJECT/PROJECT_PROFILE.md`, `PROJECT/HARDENING_BACKLOG.md`,
`PROJECT/PRODUCTION_PATHS.md` — không cần thiết cho ba tu chỉnh này.

## 5. Ranh giới đã giữ

KHÔNG: sửa `src/`, `tests/`, `webapp/`, `docs/spec/`, `docs/spec-l1/`, `firebase.json`,
`firestore.rules`, `pyproject.*`; thi hành ledger/migration/UI/Firebase/auth; tạo task ID nào
khác ngoài việc tu chỉnh `T-12`; đổi trạng thái task nào khác; tiêu bất kỳ repair cycle nào (chỉ
pre-authorize để dùng SAU); merge/push `main`.

    git diff --shortstat 91cfbba..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> rỗng (production diff = EMPTY)

## 6. Validator

    validate_structure        PASS
    validate_project_state    PASS
    validate_governance       PASS
    validate_routing          PASS (20 MAJOR task file, 0 manual override — routing của T-12
                                     không đổi, ba tu chỉnh không chạm D/R/B/A/X hay U/V/H/C/F)
    sync_easy_roadmap         PASS (không có thay đổi Tier/Effort/status roadmap cần sync lại)
    validate_easy_roadmap     PASS
    validate_evidence         PASS
    validate_task_completion  PASS
    branch_authority_check    PASS (ahead of default tăng đúng bằng commit của S033; production
                                     diff vẫn EMPTY)

`task_registry_snapshot.sh`: task file vẫn 23; roadmap ID vẫn 30 — `DEC-043` tu chỉnh nội dung,
không thêm task ID nào.

## 7. Bước kế tiếp

Không đổi so với `S032`: mở một phiên thi hành riêng cho `T-12`, nhánh mới tách từ `origin/main`.
Điều kiện đầy đủ: `PROJECT/PROJECT_PROGRESS.md` § Next Session (đã cập nhật theo `DEC-043`).
