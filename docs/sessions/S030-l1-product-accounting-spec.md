# S030 — L-1 PRODUCT + ACCOUNTING SPEC

Ngày: 2026-09-05
Nhánh: `claude/coindca-l1-spec-xzdl62`
SOURCE HEAD: `9d9fe51` (`origin/main`)
Loại phiên: **SPECIFICATION ONLY** — không thi hành, không tạo task ID, production diff = 0.

---

## 1. Xác minh trạng thái nguồn (bước 0)

Đối chiếu với thẩm quyền repo TRƯỚC khi làm việc. Toàn bộ khớp, không có `SOURCE_STATE_REVIEW_REQUIRED`:

| Khẳng định | Nguồn đã đọc | Kết quả |
|---|---|---|
| HEAD = `9d9fe51` | `git log` | KHỚP |
| CoinDCA L-1 = ACTIVE PRODUCT TRACK | `CAPABILITY_REGISTRY.md` §1.A | KHỚP |
| `app_development_allowed = true` | `PROJECT_PROFILE.md` § Quyền phát triển | KHỚP |
| V2.1.5 = FROZEN HISTORICAL RESEARCH AUTHORITY | `DEC-041` A | KHỚP |
| V2.1.5 validation = FAILED · verdict = `DO_NOT_BUILD` · `can_proceed_to_app = false` | `DEC-040` D, `DEC-041` A/B | KHỚP |
| `DEC-041` hiệu lực · `DEC-005 = SUPERSEDED_BY_DEC-041` | `PROJECT_DECISIONS.md:174-181` | KHỚP |
| `T-03 = DONE` · `RSK-003` ĐÓNG | `PROJECT_PROGRESS.md:799`, `:1236` | KHỚP |
| `T-08`/`T-10` = `DEFERRED` (`REDEFINE_FOR_L1`) | `PROJECT_PROGRESS.md:818`, `:821` | KHỚP |
| `T-05`/`T-11`/`WP-C3`/`WP-C4`/`WP-D2` = `CANCELLED` | `PROJECT_PROGRESS.md:801`, `:816-818`, `:823-824` | KHỚP |
| `H-41` = ràng buộc kế toán/sản phẩm | `HARDENING_BACKLOG.md:1370` | KHỚP |
| `H-42` = ràng buộc product-readiness Firebase | `HARDENING_BACKLOG.md:1419` | KHỚP |

Ngoài ra đã đọc: `AGENTS.md`, `PROJECT/PRODUCTION_PATHS.md`, `docs/reviews/L1-CANONICAL-TRANSITION-PROPOSAL.md`
(khối `B1`–`B10`), và mã hiện tại: `webapp/app_logic.js` (state model, `addP2P`, `addBuy`,
`monthKey`/`currentMonth`, `validateState`, export/import/wipe), `webapp/engine.js`.

`H-41` và `H-42` đều có `RE_TRIGGER_CONDITION` *"phiên L-1 PRODUCT + ACCOUNTING SPEC khởi động"* —
phiên này chính là điều kiện đó. Cả hai đã được xử lý như đầu vào BẮT BUỘC: xem Phụ lục A và
Phụ lục B của spec, nơi từng hạng mục `B1`–`B10` và `FB-1`–`FB-4` được trả lời tường minh.

## 2. Sản phẩm của phiên

Một tài liệu duy nhất:

    docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md

`docs/spec/` **diff = 0** (`DEC-041` A.3 — freeze chỉ ghi ở tầng `PROJECT/`, không vá spec V2.1.5).

## 3. Quyết định thiết kế chính (tóm tắt — chi tiết trong spec)

1. **Sự thật tài chính = `openingPosition` + `events`, tính lại toàn bộ mỗi lần render.** Không
   biến cộng dồn. Đây là lời giải kiến trúc cho `H-41` ràng buộc 2, xoá cả lớp lỗi `B1`/`B2`/`B5`/`B6`.
2. **Giá vốn VND: WAC trên một pool USDT duy nhất, giải phóng theo bình quân khi chi.** USDT được
   mô hình hoá là **tài sản có giá vốn VND**, không phải tiền trung tính. Đây là điểm mà app hiện
   tại sai (`app_logic.js:251` — `vndCost = usdt × vndRate` với tỷ giá gõ lúc mua ETH).
3. **P2P không phải chi phí đầu tư** (`INV-8`); chỉ giao dịch crypto mới là "đã đầu tư".
4. **Hai con số tách bạch**: `investedThisMonth` (mọi nguồn) và `planInvested` (chỉ `source=PLAN`).
   `EXTRA` và `RESERVE` không đụng tới mức tuân thủ kế hoạch (`INV-9`).
5. **`businessDate` do người dùng nhập là trường thời gian tài chính duy nhất**; `createdAt` là
   metadata và không bao giờ vào phép tính (`INV-6`). Một chỗ duy nhất hỏi giờ, `Asia/Ho_Chi_Minh`.
6. **Tiền lưu số nguyên** (VND đồng · USDT 1e-6 · crypto 1e-8) — `INV-5`.
7. **Xoá cứng + snapshot bắt buộc trước mọi thao tác phá huỷ**, thay cho tombstone.
8. **Migration nguyên tử, thất bại thấy được**, dùng chính accumulator legacy làm oracle đối chiếu.
9. **Không tín hiệu nào được chạm tiền** (`INV-10`) — không có cửa sau cho Buy Score.

## 4. Ranh giới đã giữ

KHÔNG: sửa `src/`, `tests/`, `webapp/`, `docs/spec/`, `firebase.json`, `firestore.rules`,
`pyproject.*`; tạo task ID; tạo roadmap; mở capability mới; mở lại V2.1.5; tạo V2.2; chạy test
chiến lược; chạy `T-06`; vá `H-41`/`H-42` trong mã; yêu cầu hay commit dữ liệu tài chính thật của
Owner (mọi số trong spec là **tổng hợp**, `DEC-041` C); merge `main`.

Không sửa `PROJECT/PROJECT_PROGRESS.md`: phiên kết thúc tại **ranh giới Owner Decision**, chưa có
thay đổi trạng thái nào được phép ghi.

## 5. Sai lệch cần Owner định đoạt

`DEVIATION-1` — `DEC-041` J đặt kỳ vọng spec L-1 *"≤ 5 trang"*. Tài liệu dài hơn đáng kể vì bề
mặt deliverable (24 mục + 12 kịch bản kế toán) do chính chỉ thị phiên quy định, và mô hình giá vốn
hai tiền tệ không đặc tả đủ chặt được trong 5 trang. Tinh thần *"MỘT tài liệu yêu cầu canonical
thay cho pack 6 tài liệu"* được giữ. Ghi nhận để Owner định đoạt; **không** tự cho là đã duyệt.

## 6. Cần Owner trả lời trước khi làm tiếp

Bốn câu, ở §21 của spec:

| # | Câu hỏi | Khuyến nghị |
|---|---|---|
| `OD-L1-1` | Mô hình lịch DCA | số tiền cố định/tháng + `scheduleDays` (vd `[3,13,23]`) |
| `OD-L1-2` | Ngân sách tháng chưa dùng hết | `CAPPED_CARRY`, `carryCapMonths = 1` |
| `OD-L1-3` | Cách đối xử với quỹ dự phòng | tách hẳn khỏi ngân sách DCA; không tính vào tuân thủ |
| `OD-L1-4` | Giá vốn VND khi không truy được lô P2P | `POOL_AVERAGE` + ô `vndRateOverride` tuỳ chọn |

## 7. Bước kế tiếp (đề xuất, KHÔNG phải task)

A. Ledger/Data Model v2 + migration + test kế toán → B. Dashboard + UX sổ →
C. Firebase isolation/auth/backup → D. Chấp nhận dùng thật.

Không hạng mục nào được mở cho tới khi Owner trả lời §21 và định đoạt `DEVIATION-1`.
