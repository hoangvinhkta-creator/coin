# T-09B — Production Verification (CHECK-T09B-01/02/03/04/14 trên project thật)

Nguồn thẩm quyền:
`governance/core/EVIDENCE_STANDARD.md`, `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`,
`PROJECT/PROJECT_DECISIONS.md` `DEC-023`.

Ngày:
2026-09-03

## Bối cảnh

Toàn bộ 16/16 REQUIRED check của T-09B đã PASS ở mức E1 trên Firebase Emulator Suite tại phiên
S014 (2026-09-02). Task Spec (§14 chỉ thị gốc) yêu cầu tường minh: production reachability trên
project Firebase THẬT không được suy ra từ emulator — phải kiểm riêng sau khi chủ dự án tạo
project và deploy. Phiên này ghi nhận kết quả của lần kiểm đó.

**Giới hạn trung thực bắt buộc phải nêu**: môi trường agent (sandbox chạy phiên này) bị chặn
mạng tới `*.web.app`/`*.firebaseapp.com` ở tầng proxy tổ chức (xác nhận nhiều lần, ví dụ
`curl https://tinphatcontent.web.app/` → `CONNECT tunnel failed, response 403`). Agent **không
tự thực hiện được** các bước dưới đây trên hạ tầng thật. Toàn bộ evidence trong tài liệu này là
**Owner báo cáo trực tiếp** (Owner tự thao tác trên trình duyệt thật của mình, dán lại kết quả
quan sát được). Đây là mức **E1** hợp lệ theo `EVIDENCE_STANDARD.md` ("browser/devtool
verification result when appropriate"), **không phải E2** (không có reviewer độc lập tái xác
nhận trên chính hạ tầng thật). Không có phần nào trong tài liệu này giả vờ agent đã tự chạy được
trên production.

## Hạ tầng thật đã dùng

    Firebase project     = tinphatcontent (display name "CoinDCA"; dùng chung với ứng dụng
                            Content — DEC-023)
    Hosting URL           = https://tinphatcontent.web.app
    Owner Anonymous UID   = XWUo6IvUqhULI1v1EBrfndEDrE13 (28 ký tự, đúng định dạng Firebase;
                            xác minh cơ chế qua emulator ở checkpoint trước — xem
                            docs/reviews/T-09B-shared-rules-merge.md § Addendum)
    firestore.rules       = đã merge với rules Content thật (DEC-023), deploy với UID owner
                            thật thay cho placeholder OWNER_UID_REQUIRED

## Quy trình verification (do agent thiết kế, Owner tự thực hiện)

Vì `addP2P("VND_TO_USDT", ...)` yêu cầu `treasury.vnd` đã có sẵn (`webapp/app_logic.js:209`),
và `treasury.vnd` chỉ được nạp qua `addContribution()` (dòng 194), quy trình gồm một bước "Nạp
vốn tháng" trước P2P — phát hiện và sửa ngay trong phiên khi lần thử đầu tiên (chỉ P2P, không có
contribution trước) bị chặn đúng như thiết kế ("Không đủ VND trong kho.") — **xác nhận đây là
accounting guard đúng, không phải defect**; không sửa code, chỉ sửa quy trình test.

| # | Thao tác qua UI | rev kỳ vọng | rev Owner báo cáo |
|---|---|---|---|
| 1 | Nhập giá đóng cửa synthetic (ETHUSDT 1111.11, BTCUSDT 22222.22, volume 100000) | 1 | 1 ✅ |
| 2a | Nạp vốn tháng 100.000 ₫ | 2 | (gộp vào báo cáo cuối) |
| 2b | P2P VND→USDT: 100.000 ₫ → 4 USDT | 3 | (gộp vào báo cáo cuối) |
| 2c | Xác nhận mua ETH: 3 USDT @ 1111.11, tỷ giá 25.000 | 4 | 4 ✅ |

rev kỳ vọng được tính TRƯỚC từ chính công thức kế toán (`touch()` tăng `rev` mỗi lần ghi), không
biết trước kết quả Owner sẽ báo — khớp đúng 1→4 là bằng chứng gián tiếp quy trình được thực hiện
đúng như hướng dẫn, không phải báo cáo qua loa.

## Kết quả từng CHECK

### CHECK-T09B-01 — Firebase durable write thành công
**PASS.** Chip đầu trang chuyển "Đang lưu…" → "Đã lưu bền · rev N" đúng sau mỗi thao tác,
kết thúc ở rev 4. Durable write có xác nhận máy chủ (chip chỉ đổi sau ack, đúng thiết kế
`webapp/app_logic.js::save()`).

### CHECK-T09B-02 — App load đúng state từ Firebase (phiên mới)
**PASS.** Đóng hẳn Chrome, mở lại `https://tinphatcontent.web.app` (phiên hoàn toàn mới): state
nạp đúng rev 4, tab Lịch sử ETH 1 dòng, tab Lịch sử P2P 1 dòng, ledger phục hồi đầy đủ.

### CHECK-T09B-03 — Xoá localStorage/sessionStorage vẫn recover từ Firebase
**PASS.** Chạy `localStorage.clear(); sessionStorage.clear(); location.reload();` trong Console
(không đụng IndexedDB). Sau reload: không banner "KHÔNG NHẬN DIỆN ĐƯỢC THIẾT BỊ", durable state
rev 4 còn nguyên, lịch sử ETH/P2P còn nguyên. Xác nhận trực tiếp trên hạ tầng thật: Firestore,
không phải localStorage, là nguồn bền — đúng mục tiêu chính của T-09B / giảm thiểu `RSK-001`.

### CHECK-T09B-04 — Đóng/mở lại cùng browser profile
**PASS.** Cùng lần đóng/mở ở CHECK-02 (một hành động vật lý chứng minh cả hai check — đóng hẳn
trình duyệt là phép thử mạnh hơn "tab mới cùng context" nên gộp hợp lệ): Anonymous identity vẫn
được nhận diện, không banner từ chối, state/lịch sử/ledger nguyên vẹn.

### CHECK-T09B-14 — Workflow cá nhân, không cần terminal/AI coding agent
**PASS.** Toàn bộ chuỗi (mở app → nhập giá đóng cửa → ghi giao dịch → đóng → mở lại) thực hiện
qua trình duyệt thật, không terminal, không AI coding agent điều khiển thay (agent chỉ đưa
hướng dẫn văn bản — không có quyền/khả năng truy cập trình duyệt của Owner). Đóng dứt điểm ghi
chú "phải lặp lại trên Hosting thật" còn treo từ evidence S014.

## Không phát hiện defect production

Owner báo cáo: không xuất hiện hành vi bất thường nào trong toàn bộ quy trình (sau khi sửa đúng
quy trình test ở bước P2P). Không có finding mới cần phân loại BLOCKING/HARDENING từ phiên này.

## Những gì KHÔNG được kiểm ở đây (ngoài phạm vi yêu cầu)

- CHECK-T09B-05..09, 11, 12, 15, 16 — đã PASS E1 trên emulator (S014), KHÔNG lặp lại trên
  production trong phiên này (không được yêu cầu; các check này không phụ thuộc riêng vào hạ
  tầng thật khác với 01-04 — chúng kiểm bất biến kế toán/serialize, đã chứng minh đủ bằng
  emulator theo đúng kiến trúc SDK+wire-protocol thật).
- CHECK-T09B-10 (write failure) — KHÔNG dựng lại trên production (rules từ chối ghi hoặc mất
  mạng thật) vì đây là phép thử có chủ đích gây lỗi trên hạ tầng đang giữ dữ liệu thật của
  Owner; Owner không yêu cầu và agent không tự ý mở rộng phạm vi sang việc đó.
- Hosting content-integrity (SDK tải từ `gstatic.com` thật) — không kiểm độc lập được từ agent
  (mạng chặn); Owner không báo lỗi tải trang nào trong toàn bộ quy trình, gián tiếp cho thấy SDK
  tải đúng.

## Kết luận

    CHECK-T09B-01  PASS (E1, production)
    CHECK-T09B-02  PASS (E1, production)
    CHECK-T09B-03  PASS (E1, production)
    CHECK-T09B-04  PASS (E1, production)
    CHECK-T09B-14  PASS (E1, production)

    Production reachability: PASS — không còn NOT_TESTED.
    Defect mới: 0.
