# S031 — Owner Decision DEC-042: DUYỆT CoinDCA L-1 Product + Accounting Spec

Ngày: 2026-09-05
Nhánh: `claude/coindca-l1-spec-xzdl62`
SOURCE HEAD trước phiên: `e5e7073` (đầu ra `S030`)
Loại phiên: **OWNER DECISION APPLICATION** — áp dụng quyết định Owner vào spec đã soạn ở `S030`,
không thi hành, không tạo task ID, production diff = 0.

---

## 1. Đầu vào

Owner Decision toàn văn, DUYỆT `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` (`S030`)
kèm bốn quyết định kế toán (§21) + duyệt có điều kiện `DEVIATION-1` (§0). Chi tiết đầy đủ ghi tại
`DEC-042` (`PROJECT/PROJECT_DECISIONS.md`).

## 2. Thay đổi áp dụng vào spec

1. **Header** — `Status` đổi `DRAFT — PENDING_OWNER_DECISIONS` → `CANONICAL — APPROVED`, thêm
   `DEC-042` vào thẩm quyền nền.
2. **Tóm tắt Thi hành** — thêm mới, ngay sau header, trước §0 (đáp ứng điều kiện Owner cho
   `DEVIATION-1`): định nghĩa sản phẩm, mô hình sự thật tài chính, thực thể lõi, bảng 4 quyết
   định đã duyệt, chỉ mục `INV-1`…`INV-15`, chỉ mục `SC-01`…`SC-12`, lát cắt chấp nhận MVP.
3. **§5.3 (TRADE schema)** — bỏ trường `vndRateOverride`. Owner cấm tường minh *"hidden per-trade
   FX fallback"*; đây là cơ chế duy nhất bị bác trong toàn bộ nội dung spec ban đầu.
4. **§8.3, §8.4, §8.5** — viết lại theo chính sách STRICT/FAIL-VISIBLE canonical: giá vốn VND
   không xác định lan truyền `UNKNOWN`, sửa được duy nhất qua thao tác sửa `openingPosition`
   tường minh (không phải qua ô nhập theo từng lệnh).
5. **§11.1, §11.4, §12.1** — đổi khung "OWNER DECISION — khuyến nghị" thành "QUYẾT ĐỊNH
   (`DEC-042`)", bổ sung đúng nguyên văn ràng buộc Owner: không ghép `plannedAmount` với pool
   Base/Smart/Opportunity cũ; giữ tách biệt ngân sách tháng/carry/đã đầu tư; quỹ dự phòng tách
   hẳn và không được Buy Score/Opportunity Score/Crash kích hoạt.
6. **§12.3** — liệt kê tường minh "Buy Score" cùng "Opportunity Score"/"Crash logic" theo đúng
   từ ngữ Owner dùng.
7. **§17.4** — tách hai tầng: `M-1`…`M-4` (DỪNG — dữ liệu mâu thuẫn số lượng) và `W-1` mới
   (TIẾP TỤC kèm cờ `UNKNOWN_VND_BASIS` — chỉ thiếu giá vốn, không phải mâu thuẫn số lượng).
   Trước đó toàn bộ trường hợp "không truy được giá vốn" là `M-2` hard-stop; nay đúng theo Owner
   *"may later supply... through an explicit correction"* nên không chặn migration.
8. **`SC-12`** — viết lại từ "migration DỪNG" thành "migration HOÀN TẤT, gắn cờ, không bịa số".
9. **`INV-11`** — bổ sung "không fallback ẩn theo từng lệnh" vào phát biểu bất biến.
10. **§21** — đổi tên "Owner Decisions Required" → "Owner-Approved Decisions (`DEC-042`)"; mỗi
    mục chuyển từ khung phương án/khuyến nghị sang khung QUYẾT ĐỊNH, giữ bảng phương án + lý do
    làm hồ sơ thể chế.
11. **§24** — sửa câu "chờ Owner định đoạt sau khi trả lời §21" (đã trả lời) → làm rõ việc mở
    task ID cho bước A vẫn thuộc một phiên riêng.
12. Dọn tham chiếu chéo còn sót: `carryPolicy` comment, `M-5` → `M-4` ở Phụ lục A.

## 3. Không đổi

Kiến trúc lõi (`openingPosition + events → derive()`), WAC một pool USDT, tách P2P khỏi đầu tư,
tách `investedThisMonth`/`planInvested`, ngày/giờ/tiền tệ (`Asia/Ho_Chi_Minh`, integer, tháng
lịch), xoá cứng + snapshot, 12 golden scenario (trừ SC-12 sửa kết quả kỳ vọng), 15 invariant
(trừ `INV-11` bổ sung một câu), ràng buộc Firebase §18, phân loại migration §17.2, Non-Goals,
Explicitly Deferred — **không đổi**.

## 4. Governance

Ghi `DEC-042` vào `PROJECT/PROJECT_DECISIONS.md` (Owner Decision, cùng khuôn `DEC-040`/`DEC-041`).
Không sửa `PROJECT/PROJECT_PROGRESS.md`: `DEC-042` chỉ đóng vòng đời spec, không mở task ID nào,
không đổi trạng thái roadmap nào. `validate_project_state.py` và `validate_governance.py` chạy
lại sau khi ghi `DEC-042` — cả hai `PASS`.

## 5. Ranh giới đã giữ

KHÔNG: sửa `src/`, `tests/`, `webapp/`, `docs/spec/`, `firebase.json`, `firestore.rules`,
`pyproject.*`; tạo task ID; thi hành ledger v2/migration/UI/Firebase/auth/Buy Score
research/notifications; merge `main`; commit dữ liệu tài chính thật của Owner.

## 6. Bước kế tiếp

Không có bước nào được mở bởi phiên này. Việc gán task ID cho bước A (`Ledger/Data Model v2` —
§24) thuộc một phiên riêng, không tự động theo sau `DEC-042`.
