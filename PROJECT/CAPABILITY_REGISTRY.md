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
| `CAP-DATA` | Ngữ nghĩa dữ liệu thiếu/hỏng | `WP-A4` | `WP-A4` | READY | CÓ (đường găng) |
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

## 3. Ranh giới capability đang gây ra ownership gap

`CAP-PROV` (`WP-A1`) sở hữu `src/eth_dca_os/data/` theo Expected Touch Area của WP-A1.
`CAP-DATA` (`WP-A4`) **loại trừ tường minh** `src/eth_dca_os/data/` khỏi phạm vi:
Expected Touch Area của WP-A4 ghi "gói này xử lý **ngữ nghĩa** dữ liệu xấu, không xử lý
việc **lấy** dữ liệu".

Hệ quả: một finding về "dữ liệu bị cắt cụt lúc fetch vẫn đủ tư cách official" rơi đúng vào
khe giữa hai capability. Xem `docs/decisions/ADOPTION-V4_3-migration-record.md` §5 —
`F-E2A1R3-05` được phân loại `OWNER_ASSIGNMENT_REQUIRED`, **không** được gán bừa vào WP-A4
và **không** được đặt ID mới.

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
