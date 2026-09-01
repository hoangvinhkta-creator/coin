# CAPABILITY REGISTRY — dự án coin (ETH DCA Operating System V2.1.5)

Status:
ACTIVE

Nguồn thẩm quyền:
`governance/v4/CORE/CAPABILITY_MODEL.md`

Ngày lập:
2026-09-01 (phiên adoption V4.3 — MAP từ roadmap hiện có, KHÔNG tạo task mới)

Nguyên tắc lập bảng này:
Capability được **dẫn xuất** từ các work package đã tồn tại trong
`PROJECT/PROJECT_PROGRESS.md`. Không capability nào phát sinh task mới, không task ID nào
được đặt lại, không Scope Lock nào bị đổi.

---

## 1. Vertical Acceptance Slice hiện tại

    Dữ liệu thật (Binance)
      -> fetch/lineage có nguồn gốc chứng minh được
        -> dataset đủ tư cách official
          -> pipeline chạy đủ 18 bước với ngữ nghĩa dữ liệu đúng
            -> Gate 1 / Gate 2 / Gate 3 + benchmark + control
              -> run record tự chứng minh nguồn gốc và tái lập được
                -> VERDICT

Đây là lát cắt mà `T-06` (official run) hiện thực hoá. Nó cắt ngang mọi module — đúng định
nghĩa Vertical Slice: không module nào tự chứng minh được nó.

Trạng thái lát cắt: **CHƯA CHẠY LẦN NÀO.** Bị chặn bởi hai nhóm điều kiện ĐỘC LẬP:

- (A) nội tại — `GATE-A` = WP-A1 ∧ WP-A2 ∧ WP-A3 ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 đều DONE,
  và `T-05`;
- (B) hạ tầng — `BLK-001` (không có đường tới `data.binance.vision` / `api.binance.com`).

Hệ quả cho Production Reachability: **chưa có Golden trace nào chứng minh reachability cho
bất kỳ capability nào**. Mọi bằng chứng reachability hiện tại đều dừng ở mức
"đường thực thi ngoài ranh giới module" trong môi trường synthetic/stub, chứ không phải
Golden. Đây là giới hạn thật, phải được nói rõ, không được coi là đã thoả.

---

## 2. Bảng capability

| Capability | Tên | Lineage root | Owner task hiện hành | Trạng thái | Nằm trên Vertical Slice? |
|---|---|---|---|---|---|
| `CAP-PROV` | Nguồn gốc & khả năng tái lập của official run | `WP-A1` | `WP-A1` | IN_PROGRESS — E2 vòng ba FAIL | CÓ (bắt buộc cho GATE-A) |
| `CAP-DATA` | Ngữ nghĩa dữ liệu thiếu/hỏng (gồm độ phủ theo khoảng được yêu cầu) | `WP-A4` | `WP-A4` | DONE — 9/9 REQUIRED check PASS tại S009 | CÓ (đường găng) |
| `CAP-ENGINE` | Vòng đời regime & ladder, kế toán vốn | `WP-A3` | `WP-A3` (DONE), `WP-A7` (DONE) | DONE | CÓ |
| `CAP-PIPELINE` | Đấu nối hạng mục bắt buộc vào pipeline | `WP-A2` | `WP-A2` | DONE | CÓ |
| `CAP-MEASURE` | Đo Failure Signal | `WP-A5` | `WP-A5` | READY | CÓ |
| `CAP-ORDER` | Thứ tự 18 bước tính toán | `WP-A6` | `WP-A6` | PLANNED | CÓ |
| `CAP-VERDICT` | Chính sách verdict, test đặc tả, audit trail | `WP-B1` | `WP-B1`, `WP-B2`, `WP-B3` | PLANNED (sau T-06) | CÓ (sau lát cắt) |
| `CAP-WEBAPP` | App web: sổ sách, trạng thái thực thi, parity JS/Python | `WP-C1` | `WP-C1`, `WP-C2`, `WP-C3`, `WP-C4` | READY / BLOCKED | KHÔNG (song song) |
| `CAP-DEBT` | Nợ kỹ thuật không đổi hành vi | `WP-D1` | `WP-D1` | DONE | KHÔNG |
| `CAP-SPEC` | Đề xuất V2.2 cho khiếm khuyết đặc tả | `WP-D2` | `WP-D2` | READY | KHÔNG |
| `CAP-GOVTOOL` | Validator & tooling governance | `MICRO-GOVDEF-001` | chưa có owner cho phần glob | READY một phần | KHÔNG |

---

## 3. Ranh giới capability — ownership gap ĐÃ ĐÓNG (2026-09-01)

Khe giữa `CAP-PROV` và `CAP-DATA` đã được chủ dự án đóng bằng `DEC-014` / `OD-A4-01`.

Trạng thái CŨ (giữ lại để đọc được lịch sử): `CAP-PROV` (`WP-A1`) sở hữu
`src/eth_dca_os/data/` theo Expected Touch Area của WP-A1, còn `CAP-DATA` (`WP-A4`) loại
trừ tường minh thư mục đó. Một finding về "dữ liệu bị cắt cụt lúc fetch vẫn đủ tư cách
official" (`F-E2A1R3-05`) vì thế rơi đúng vào khe giữa hai capability và được phân loại
`OWNER_ASSIGNMENT_REQUIRED` — xem `docs/decisions/ADOPTION-V4_3-migration-record.md` §5.

Trạng thái HIỆN TẠI: chủ dự án đọc câu loại trừ đúng như nó viết — loại trừ là về **cơ chế
LẤY** dữ liệu (HTTP, retry, rate-limit, nguồn archive/REST), KHÔNG phải về **ngữ nghĩa
coverage**. `F-E2A1R3-05` được gán cho `CAP-DATA` và hấp thụ vào `WP-A4`. Đóng tại S009,
`CHECK-A4-10` PASS.

Ranh giới từ đây, để không phải quyết lại:

| Chủ đề | Capability sở hữu |
|---|---|
| Nguồn dữ liệu, nhãn lineage, checksum, tái lập run | `CAP-PROV` (WP-A1) |
| Cơ chế LẤY dữ liệu: HTTP, retry, rate-limit, archive/REST | `CAP-PROV` (WP-A1) |
| Ngữ nghĩa coverage / gap / đối chiếu khoảng được yêu cầu | `CAP-DATA` (WP-A4) |
| Ngữ nghĩa DEGRADED / INVALID, nhãn gap trên bản ghi | `CAP-DATA` (WP-A4) |

Không task ID mới được tạo trong cả quá trình này.

`CAP-GOVTOOL` chưa có owner cho khiếm khuyết glob của `validate_evidence.py` /
`validate_task_completion.py`. Đây là mục đã nằm sẵn trong danh sách "Cần chủ dự án quyết
định" #5 của `PROJECT/PROJECT_PROGRESS.md` — adoption KHÔNG tạo owner mới cho nó.

---

## 4. Absorption Limit — trạng thái hiện tại

Áp bốn ngưỡng của `CAPABILITY_MODEL.md`:

| Ứng viên hấp thụ | Vào owner | Ngưỡng chạm | Kết luận |
|---|---|---|---|
| `F-E2A1R3-05` (fetch cắt cụt) | `WP-A4` | Ngoài Scope Lock đã FROZEN + Completion Gate không phủ | Không hấp thụ được nếu không có COMPLETION GATE CHANGE PROPOSAL → Owner Decision |
| `F-E2A1R3-05` (fetch cắt cụt) | `WP-A1` | **A** (Effective Risk tăng: thêm bất biến dữ liệu mới vào gói đã qua 3 vòng E2) và **C** (thêm REQUIRED check vào gate 11 check đã FROZEN) | `ABSORPTION_LIMIT_REACHED` → Owner Decision |
| Khiếm khuyết glob validator | bất kỳ WP lớp A nào | **D** (việc ngoài Vertical Slice bị kéo lên đường găng) | Không hấp thụ; giữ ở `CAP-GOVTOOL`, chờ Owner |

Không mục nào ở trên được phép tự sinh task. Đây là kết quả routing, không phải danh sách
việc phải làm.

---

## 5. Cập nhật tại phiên Owner Disposition (2026-09-01)

Nguồn: `DEC-011`, `DEC-012`, và
`docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md`.
Bảng §2 KHÔNG đổi: không capability nào được thêm, đổi tên hay đổi lineage root.

### 5.1 `CAP-PROV` — budget đã có hạn mức

    ALLOWED = 2 · USED = 2 · REMAINING = 0 · OWNER_EXTENSION = NOT GRANTED   (DEC-012)

`ABSORPTION_LIMIT_REACHED` ở §4 vẫn đứng nguyên, và nay được củng cố bằng một hạn mức đếm
được thay vì chỉ bằng hai ngưỡng định tính. Hệ quả: `CAP-PROV` **không thể** nhận thêm bất
kỳ hạng mục nào cần production code cho tới khi có `OWNER_EXTENSION` mới.

### 5.2 `F-E2A1R3-05` — đề xuất owner: `CAP-DATA`

Trạng thái trước: `OWNER_ASSIGNMENT_REQUIRED` với hai ứng viên được nêu tên, không ứng
viên nào được chọn (§3, §4).
Trạng thái sau: **đề xuất `CAP-DATA` (`WP-A4`)**, chờ đúng MỘT quyết định của chủ dự án.

`CAP-PROV` bị loại: budget `REMAINING = 0` và `OWNER_EXTENSION = NOT GRANTED` (`DEC-012`);
gán vào đây là mở repair cycle thứ tư không có thẩm quyền.

`CAP-DATA` được đề xuất theo **CHỦ ĐỀ**, không theo đường dẫn file. Điều đang chặn WP-A4 là
một câu loại trừ `src/eth_dca_os/data/` trong Expected Touch Area, nhưng LÝ DO của câu đó là
"gói này xử lý **ngữ nghĩa** dữ liệu xấu, không xử lý việc **lấy** dữ liệu". Defect của
`F-E2A1R3-05` không nằm ở việc lấy dữ liệu — `fetch_all` trả về trung thực đúng những gì
archive có. Defect là `gap_report` chỉ đo khoảng trống GIỮA first và last quan sát được,
không đối chiếu với `start`/`end` ĐÃ YÊU CẦU, và `official_eligibility` không nhìn
`first_timestamp`/`last_timestamp` ở đâu cả. Tức: hệ thống **mô tả sai cái gì đang thiếu** —
đúng chủ đề `CAP-DATA`.

Thứ loại WP-A4 hiện nay vì vậy là **hình thức đường dẫn file**, không phải chủ đề. Đây
chính là khiếm khuyết mà `HARDENING_BACKLOG.md` H-12 đã ghi ở tầng governance
(`PRODUCTION_PATHS.md` khai theo FILE chứ chưa theo CHUỖI dữ liệu), lặp lại ở tầng
capability.

Ba lý do độc lập ủng hộ `CAP-DATA`: (1) chủ đề khớp; (2) budget sạch — `REVIEW_BUDGET_LEDGER`
§2 ghi WP-A4 "chưa bắt đầu", 0 repair cycle, 0 vòng E2, không ngưỡng absorption nào bị chạm;
(3) đúng chỗ trên đường găng — WP-A4 đang `READY`, là prerequisite của GATE-A, và GATE-A
đứng trước T-06, đúng mốc mà finding này bắt buộc phải đóng trước.

    OWNER_DECISION_REQUIRED — đúng một quyết định:
    phê duyệt COMPLETION GATE CHANGE PROPOSAL cho WP-A4, bổ sung MỘT REQUIRED check
    (coverage đối chiếu với khoảng thời gian ĐƯỢC YÊU CẦU), kèm làm rõ Expected Touch Area:
    loại trừ là về CƠ CHẾ LẤY dữ liệu, KHÔNG phải về NGỮ NGHĨA COVERAGE.

Nếu chủ dự án từ chối: `F-E2A1R3-05` quay lại `OWNER_ASSIGNMENT_REQUIRED` và **T-06 vẫn bị
chặn** — không có đường thứ ba. **KHÔNG đặt task ID mới trong cả hai nhánh**: `WP-A4` đã tồn
tại, đây là định tuyến vào capability sẵn có.
