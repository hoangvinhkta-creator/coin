# S012 — Owner Decision: giải quyết OD-A/OD-B/OD-B2 cho T-09B; phát hiện OD-C

## Nhận dạng phiên

Ngày:
2026-09-02

Loại phiên:
OWNER AUTHORITY — tiếp nối S011 trên cùng nhánh thẩm quyền. **Không phải phiên thực thi.**

Branch:
`claude/t09b-firebase-decision-nnoony`

Baseline SHA đầu phiên:
`03281ea` (commit của `DEC-019` / S011)

Task:
`T-09B` — capability `CAP-WEBAPP` · lineage root `WP-C1`

Owner Decision ghi tại phiên:
`DEC-020` (`OD-WEBAPP-03`)

Ràng buộc phiên (chủ dự án nêu tường minh, tất cả được giữ):
KHÔNG implement Firebase · KHÔNG sửa production code · KHÔNG chuyển `T-09B` sang `IN_PROGRESS` ·
KHÔNG tạo task mới · KHÔNG mở repair cycle.

---

## Việc đã làm

### 1. Ghi ba quyết định chủ dự án đã trả lời

`OD-A = Firebase Hosting`, `OD-B = Cloud Firestore`, `OD-B2 = Firebase Anonymous Auth (một owner
UID)`. Cập nhật `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`: đánh dấu RESOLVED, thêm sơ đồ
kiến trúc baseline 4 tầng, bổ sung bước Auth vào Load flow, bổ sung hàng "Auth thất bại" vào
Failure semantics — **chỉ làm rõ wording để phản ánh Owner Decision, không đổi bất kỳ acceptance
criteria nào**.

### 2. Đánh giá lại toàn bộ Ready Gate — không auto-PASS

Đúng yêu cầu *"Không auto-PASS chỉ vì OD-A/B/B2 đã được quyết định"*: đọc lại từng dòng của bảng
14 điều kiện và 17 dòng MAJOR Ready Gate chuẩn, kiểm riêng runtime host / Firebase component /
security model / **recovery semantics** / migration prerequisite / Expected Touch Area /
Completion Gate / architecture ambiguity.

Phát hiện tại bước này: **`OD-B2` (Anonymous Auth) giải quyết đúng câu hỏi nó được hỏi — "cần
một danh tính để rules không public" — nhưng không tự động giải quyết một câu hỏi khác — "danh
tính đó có sống sót qua đổi máy không".** Hai câu hỏi độc lập.

### 3. Dựng bằng chứng cho khe mới — `OD-C`

Firebase Anonymous Auth lưu session (refresh token) trong `IndexedDB` của **một** browser
profile. Đối chiếu với bốn kịch bản mất dữ liệu mà `RSK-001` nêu tên nguyên văn:

| Kịch bản (`RSK-001`) | `IndexedDB` | UID sau đó |
|---|---|---|
| Xoá `localStorage`+`sessionStorage` | Còn nguyên | Cùng UID cũ |
| Cửa sổ riêng tư | Trống | UID mới |
| Đổi máy | Không tồn tại | UID mới |
| Đổi trình duyệt | Không tồn tại | UID mới |

Ba trong bốn kịch bản → UID mới → bị Firestore rules (khoá cứng một UID, đúng thiết kế `OD-B2`
đã duyệt) từ chối đọc/ghi dữ liệu đã có. **Đây không phải Firestore mất dữ liệu — đây là trình
duyệt/máy mới không chứng minh được nó là owner.**

### 4. Đối chiếu trực tiếp với hai REQUIRED check đã FINALIZED

- `CHECK-T09B-03` (xoá `localStorage`+`sessionStorage`) — không đụng `IndexedDB` → **không bị
  ảnh hưởng**, PASS được trung thực với thiết kế đã duyệt. Đã thêm ghi chú, **không đổi**
  acceptance criteria.
- `CHECK-T09B-04` (đóng/mở lại môi trường, **"một profile/cửa sổ khác"**) — nhánh đó sinh UID
  mới → **không PASS được trung thực** với Anonymous Auth đơn thuần. Đã thêm ghi chú chặn bởi
  `OD-C`, **không đổi** acceptance criteria, **không** hạ yêu cầu.

Tuân thủ đúng chỉ thị: *"Nếu Anonymous Auth làm check đó không khả thi sau mất browser identity:
không freeze gate giả tạo. Giữ PLANNED và trả OWNER_DECISION_REQUIRED."*

### 5. Trả `OWNER_DECISION_REQUIRED` cho `OD-C`, hai phương án

- **R1 (khuyến nghị)** — `linkWithCredential` gắn một cặp email/password vào Anonymous UID một
  lần, dùng CHỈ cho recovery (không đổi trải nghiệm hằng ngày, không phải login UI/account
  system).
- **R2** — chấp nhận giới hạn, thu hẹp phạm vi "recover" của `CHECK-T09B-04` xuống
  same-browser-profile; để hở kịch bản "đổi máy".

Không tự chọn thay chủ dự án — đây đúng là loại đánh đổi mà `STATE_AUTHORITY.md` dành riêng cho
Owner Decision.

---

## Cập nhật state canonical

| File | Thay đổi |
|---|---|
| `PROJECT/PROJECT_DECISIONS.md` | Thêm `DEC-020` (append-only) |
| `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` | OD-A/B/B2 → RESOLVED; thêm mục `OD-C`; cập nhật Load flow, Failure semantics, Ready Gate 14-mục + MAJOR checklist; chú thích `CHECK-T09B-03`/`-04` (không đổi acceptance) |
| `PROJECT/PROJECT_PROGRESS.md` | Row `T-09B`; `Last Updated`; ghi chú `RSK-001` |
| `PROJECT/CAPABILITY_REGISTRY.md` | Thêm §8 (OD-A/B/B2 resolved, `OD-C` mới). Bảng §2 không đổi |
| `PROJECT/REVIEW_BUDGET_LEDGER.md` | Thêm §2.2.2 — xác nhận budget KHÔNG đổi |
| `PROJECT/LO_TRINH_DE_HIEU.md` | Sinh lại bằng `sync_easy_roadmap.py` |

---

## Kiểm chứng

| Phép đo | Lệnh | Kết quả |
|---|---|---|
| Production diff | `git diff --shortstat origin/main..HEAD -- webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock` | **0** |
| `validate_governance.py` | — | PASS |
| `validate_structure.py` | — | PASS |
| `validate_project_state.py` | — | PASS |
| `validate_routing.py` | — | PASS (19 MAJOR, 0 override) |
| `sync_easy_roadmap.py` / `validate_easy_roadmap.py` | — | PASS |
| `branch_authority_check.sh` | — | PASS |
| Task ID mới | `task_registry_snapshot.sh` | 28 (không đổi) |
| `T-09B` state | — | `PLANNED` (không đổi — vẫn đúng vì `OD-C` chặn) |
| `CAP-WEBAPP` budget | `REVIEW_BUDGET_LEDGER.md` §2.2 | 2/0/2 (không đổi) |

---

## Bàn giao — việc kế tiếp

### NEXT SMALLEST ACTION

Chủ dự án chọn **R1** hay **R2** cho `OD-C`. Đây là quyết định duy nhất còn chặn `T-09B`
`PLANNED → READY`.

### Sau khi có quyết định OD-C

1. Nếu R1: ghi cụ thể cách one-time link credential vào Task Spec (thời điểm gọi
   `linkWithCredential`, nơi hiển thị recovery flow), cập nhật `CHECK-T09B-04` để phản ánh PASS
   qua đường `signInWithEmailAndPassword`.
2. Nếu R2: viết lại phạm vi `CHECK-T09B-04` xuống same-browser-profile bằng
   `COMPLETION GATE CHANGE PROPOSAL` (không phải sửa tay, vì gate đã FINALIZED); cập nhật
   `RSK-001` để nói rõ "đổi máy" vẫn chỉ có lối thoát export JSON thủ công.
3. Đóng dòng "Security impact" (hiện `[~]` một phần) và dòng "Completion Gate freeze" trong Ready
   Gate → 15/15.
4. `T-09B`: `PLANNED → READY`. Freeze Completion Gate.
5. Mở phiên thực thi riêng.

### Rủi ro mang sang

- `RSK-001` **vẫn chưa giảm** — 0 dòng production đổi ở cả S011 lẫn S012.
- Kịch bản "đổi máy" của `RSK-001` **chưa có lối đóng nào được chốt** — phụ thuộc R1/R2.
