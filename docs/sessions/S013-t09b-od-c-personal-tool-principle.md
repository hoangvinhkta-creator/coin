# S013 — Owner Decision: Personal Tool Simplification Principle; đóng OD-C; T-09B → READY

## Nhận dạng phiên

Ngày:
2026-09-02

Loại phiên:
OWNER AUTHORITY — tiếp nối S011/S012 trên cùng nhánh thẩm quyền. **Không phải phiên thực thi.**

Branch:
`claude/t09b-firebase-decision-nnoony`

Baseline SHA đầu phiên (đã xác nhận khớp HEAD kỳ vọng của chỉ thị):
`0958b84` (commit của `DEC-020` / S012)

Task:
`T-09B` — capability `CAP-WEBAPP` · lineage root `WP-C1`

Owner Decision ghi tại phiên:
`DEC-021` (`OD-WEBAPP-04`)

Ràng buộc phiên (tất cả được giữ):
KHÔNG implement Firebase · KHÔNG sửa production code · KHÔNG tạo task ID mới · KHÔNG mở repair
cycle.

---

## Việc đã làm

### 1. Ghi Product Principle vào canonical location — không tạo artifact mới

Personal Tool Simplification Principle (priority order 11 mục, Critical Product Question A–F,
Security Philosophy, Minimum Security Floor) ghi tại `PROJECT/PROJECT_DECISIONS.md` `DEC-021` —
**cùng vị trí** đã giữ `DEC-011` (Product Intent gốc) và `DEC-019` (bổ sung lần một). Đây là
lần bổ sung thứ hai, không thay thế, không mâu thuẫn — chỉ khai triển chi tiết hơn. Không nhân
bản sang `PROJECT_PROFILE.md`, giữ đúng tiền lệ `DEC-011` (§ Single Source Of Truth,
`STATE_AUTHORITY.md`).

### 2. Đóng `OD-C` = R2, ghi rõ đây là Owner Scope Decision, không phải kết luận kỹ thuật

Khe kỹ thuật ghi tại `DEC-020` (Anonymous UID mới sau đổi máy/browser bị Firestore rules từ
chối) **vẫn đúng, không bị phủ nhận**. Điều thay đổi là phạm vi CHẤP NHẬN của V1: chủ dự án
không yêu cầu V1 tự phục hồi qua các kịch bản đó, và không muốn thêm bất kỳ recovery credential
nào (loại R1) chỉ để đóng edge case này.

### 3. Viết audit trail bắt buộc cho `CHECK-T09B-04` — không gọi là bug fix

OLD REQUIREMENT → OWNER PRODUCT INTENT CHANGE → NEW V1 REQUIREMENT, ghi trực tiếp tại chính
check trong `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`. `CHECK-T09B-03` và 15 REQUIRED
check còn lại — bao gồm toàn bộ financial/algorithm/accounting/persistence correctness —
**không đổi, không bị làm yếu**.

### 4. Thêm `H-23` vào Hardening Backlog

Cross-device/cross-browser/lost-identity recovery = OUT OF SCOPE V1, phân loại **OWNER SCOPE
DECISION** (không phải defect). `RE_TRIGGER_CONDITION`: người dùng thứ hai, hoặc chủ dự án tự
yêu cầu lại, hoặc Firebase đổi cách Anonymous Auth persist.

### 5. Đánh giá lại toàn bộ Ready Gate — không auto-PASS

Kiểm từng dòng: runtime host ✅, Firebase component ✅, security model ✅ (Minimum Security
Floor định nghĩa xong), recovery semantics ✅ (đã chốt phạm vi, không còn mơ hồ), migration
prerequisite ✅, Expected Touch Area ✅, Completion Gate ✅ finalize, architecture ambiguity ✅
(không còn). Kết quả: **15/15 ĐẠT** (14 điều kiện riêng §13 + dòng "+"), 17/17 dòng MAJOR Ready
Gate chuẩn ✅.

### 6. Freeze Completion Gate; chuyển `T-09B: PLANNED → READY`

Theo `STATE_AUTHORITY.md` (`READY` do Implementer/Owner viết) và uỷ quyền tường minh của chỉ
thị phiên §18 ("Nếu Ready Gate FULL PASS... T-09B: PLANNED → READY và freeze Completion Gate").
16 REQUIRED check giữ nguyên số lượng; chỉ `CHECK-T09B-04` được tái phạm vi TRƯỚC khi freeze —
đây là bước finalize hợp lệ theo `TASK_COMPLETION_GATE_STANDARD.md` § Gate Creation Timing,
không phải sửa yếu gate đã đóng băng.

---

## Cập nhật state canonical

| File | Thay đổi |
|---|---|
| `PROJECT/PROJECT_DECISIONS.md` | Thêm `DEC-021` (append-only) |
| `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` | `OD-C` → RESOLVED (R2); `CHECK-T09B-04` viết lại theo audit trail; `CHECK-T09B-11` chú thích; Ready Gate → 15/15; Completion Gate → FROZEN; Status → READY |
| `PROJECT/HARDENING_BACKLOG.md` | Thêm `H-23` |
| `PROJECT/PROJECT_PROGRESS.md` | Row `T-09B` → `READY`; `Last Updated`; ghi chú `RSK-001` |
| `PROJECT/CAPABILITY_REGISTRY.md` | Thêm §9 |
| `PROJECT/REVIEW_BUDGET_LEDGER.md` | Thêm §2.2.3 — budget không đổi |
| `PROJECT/LO_TRINH_DE_HIEU.md` | Sinh lại bằng `sync_easy_roadmap.py` |

---

## Kiểm chứng

| Phép đo | Kết quả |
|---|---|
| Production diff vs `origin/main` | **0** |
| `validate_governance.py` | PASS |
| `validate_structure.py` | PASS |
| `validate_project_state.py` | PASS |
| `validate_routing.py` | PASS (19 MAJOR, 0 override) |
| `sync_easy_roadmap.py` / `validate_easy_roadmap.py` | PASS |
| Task ID mới | 0 (28 không đổi) |
| `T-09B` state | `PLANNED → READY` |
| Completion Gate | `FINALIZED → FROZEN` |
| `CAP-WEBAPP` budget | 2/0/2 (không đổi) |

---

## Bàn giao — việc kế tiếp

### NEXT SMALLEST ACTION

Mở phiên thực thi riêng cho `T-09B` (`READY → IN_PROGRESS`). Mang theo:
- Kiến trúc baseline FROZEN: Firebase Hosting → Firebase Anonymous Auth → Cloud Firestore
  (`ethdca/state` + `ethdca/seed`).
- 16 REQUIRED check FROZEN, đặc biệt `CHECK-T09B-04` (same-browser-profile, không phải
  cross-device).
- Expected Touch Area đã khai trong Task Spec — không mở rộng.
- `CAP-WEBAPP` budget 2/0/2; implementation đầu tiên là INITIAL IMPLEMENTATION, không tự động
  tiêu repair cycle.
- Không backfill `ladders[].month`, không migrate historical state.

### Rủi ro mang sang

- `RSK-001` **vẫn chưa giảm** — 0 dòng production đổi qua ba phiên S011/S012/S013.
- Kịch bản "đổi máy" của `RSK-001` **chính thức không được T-09B đóng ở V1** — lối thoát duy
  nhất là export JSON thủ công, nay quan trọng hơn trước vì đó là hướng đóng chính thức, không
  phải biện pháp tạm.
