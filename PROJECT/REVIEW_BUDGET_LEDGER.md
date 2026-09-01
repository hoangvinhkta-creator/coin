# REVIEW / REPAIR BUDGET LEDGER

Status:
ACTIVE — khởi lập tại phiên adoption V4.3 (2026-09-01)

Nguồn thẩm quyền:
`governance/v4/CORE/DELIVERY_LOOP.md` § Change Budget,
`governance/v4/CORE/CAPABILITY_MODEL.md` § Capability

## Quy tắc bất di dịch

Budget cộng dồn về **capability lineage root**, KHÔNG về task, session, branch, subtask,
work package, task con hay sibling task. Budget **không reset** qua bất kỳ ranh giới nào ở
trên, và **không được giải phóng bằng cách tạo một unit công việc mới**.

Adoption V4.3 KHÔNG reset budget. Lịch sử dưới đây được tái dựng từ git, không chép từ báo
cáo.

---

## 1. `CAP-PROV` — Nguồn gốc & khả năng tái lập của official run

    LINEAGE ROOT   = WP-A1 (docs/tasks/WP-A1-provenance-va-tai-lap.md)
    BASELINE SHA   = 666de143a3159b5d2a9f6237eb7160a8e590edfe   (2026-08-24, commit cuối
                     trước khi WP-A1 bắt đầu — WP-A2 DONE)
    CURRENT HEAD   = 6c11a7eb2bb7c36c70343c591c402f4bf3f1c23f   (2026-09-01)
    BRANCH         = claude/wp-a1-provenance-v67k9h

### Chu kỳ đã tiêu (đo bằng git, production paths theo `PROJECT/PRODUCTION_PATHS.md`)

| # | Loại | BASE SHA | HEAD SHA | Diff production path | Kết quả |
|---|---|---|---|---|---|
| 0 | Implementation ban đầu | `666de14` | `d72fbc4` | 4 files, +87 / -8 | E2 vòng MỘT → FAIL |
| 1 | Repair cycle 1 | `d72fbc4` | `2f20e6c` | 8 files, +246 / -76 | E2 vòng HAI → FAIL (`66f5e22`) |
| — | Decision pack PRE-S008 | `2f20e6c` | `bd7c5ff` | **0** (chỉ `docs/`) | Contract 20 case ĐÓNG BĂNG |
| 2 | Repair cycle 2 | `bd7c5ff` | `a0c278a` | 2 files, +56 / -10 | E2 vòng BA → FAIL (`6c11a7e`) |

    REPAIR CYCLES ĐÃ TIÊU  = 2  (ngoài lượt implementation ban đầu)
    VÒNG E2 ĐÃ TIÊU        = 3  (E2-WP-A1-001, -002, -003 — cả ba đều FAIL)

### Delivery change budget tích luỹ (đo trực tiếp, không cộng tay)

    git diff --shortstat 666de143a3159b5d2a9f6237eb7160a8e590edfe..HEAD \
        -- src/eth_dca_os webapp pyproject.toml pyproject.lock

    -> 8 files changed, 340 insertions(+), 45 deletions(-)

Lưu ý: tổng tích luỹ KHÁC tổng cộng từng chu kỳ, vì các chu kỳ chồng lấn lên cùng vùng mã.
Con số có thẩm quyền là con số ĐO TÍCH LUỸ ở trên, không phải phép cộng.

### Trạng thái budget

    CURRENT BUDGET USED       = 2 repair cycle + 3 vòng E2;
                                340 insertion / 45 deletion trên production path
    CURRENT BUDGET REMAINING  = KHÔNG XÁC ĐỊNH ĐƯỢC
    ALLOWED BUDGET            = CHƯA TỪNG ĐƯỢC ĐẶT

    MIGRATION_UNCERTAINTY

Lý do: bộ governance V3.2 của repo này **chưa bao giờ định nghĩa một mô hình
review/repair budget**. `ESCALATION_PROTOCOL.md` chỉ có trigger định tính
("hai lần thử khác nhau về bản chất đều fail") chứ không có hạn mức đếm được. Vì vậy
"remaining" không thể tính ra từ dữ liệu lịch sử — nó chưa từng tồn tại để mà tiêu.

Đây là ghi nhận MIGRATION_UNCERTAINTY theo §19 của chỉ thị adoption. Không bịa hạn mức.

    OWNER_DECISION_REQUIRED — chủ dự án cần đặt hạn mức cho CAP-PROV:
    số repair cycle tối đa, số vòng E2 tối đa, và/hoặc trần diff production path,
    tính TỪ BASELINE 666de14, KHÔNG tính lại từ 0.

Dữ liệu đầu vào cho quyết định đó, đã đo được:

- `ESCALATION_PROTOCOL.md` đã kích hoạt: đây là lần thứ BA gói đi qua E2, và điều khoản
  "không vá đi vá lại một implementation đang hỏng" đang áp dụng — vòng sửa tiếp theo cần
  chủ dự án phê duyệt tường minh.
- Reviewer E2 vòng ba KHÔNG khuyến nghị `CAPABILITY_CEILING` (không nâng Tier lên D).
  Phân loại đề xuất là `VERIFICATION_DEPTH`: giữ Tier C, nâng Effort `xhigh` → `max`.
  Quyết định thuộc về chủ dự án; reviewer không tự chọn thay.
- Khối lượng còn lại phần lớn đã được liệt kê sẵn (5 mục bắt buộc + 7 mục nên làm trong
  `docs/reviews/E2-WP-A1-provenance-round3.md` § Required Follow-up), không phải khối
  lượng phải khám phá lại.

---

## 2. Các capability khác

| Capability | Lineage root | Baseline SHA | Repair cycles | Vòng E2 | Ghi chú |
|---|---|---|---|---|---|
| `CAP-PIPELINE` | `WP-A2` | `0f2a2ab` | 0 | 1 (PASS) | DONE tại S006 |
| `CAP-ENGINE` | `WP-A3` | `5645a74` | 0 | 1 (PASS) | DONE tại S003; `WP-A7` DONE tại S004 (E2 PASS WITH FOLLOW-UPS) |
| `CAP-DEBT` | `WP-D1` | `1f4c2b7` | 0 | 0 | DONE tại S005, E1 |
| `CAP-DATA` | `WP-A4` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-MEASURE` | `WP-A5` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-ORDER` | `WP-A6` | chưa bắt đầu | 0 | 0 | PLANNED |
| `CAP-WEBAPP` | `WP-C1` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-SPEC` | `WP-D2` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-GOVTOOL` | `MICRO-GOVDEF-001` | `4fab2e9` | 0 | 0 | Phần glob validator chưa có owner |

Các capability chưa bắt đầu có budget used = 0 vì **chưa tiêu**, không phải vì được reset.

---

## 3. Golden cumulative change budget

    GOLDEN_BASELINE_SHA = PENDING_OWNER_DATA / MIGRATION_REQUIRED

Dự án chưa có Golden baseline canonical: "Golden" ở đây là **official run** (`T-06`), hiện
`PLANNED` và bị chặn bởi GATE-A lẫn `BLK-001`. Chưa có lần chạy chính thức nào tồn tại.

Vì vậy Delivery Change Budget tích luỹ hiện được đo từ **baseline capability**
(`666de14` cho `CAP-PROV`), KHÔNG từ Golden. Đây là phép đo thay thế có ghi rõ giới hạn,
không phải Golden baseline được đổi tên. Khi `T-06` chạy được và cho ra Golden trace đầu
tiên có đủ thẩm quyền, `GOLDEN_BASELINE_SHA` phải được đặt tại đúng SHA đó và mọi phép đo
tích luỹ sau đó tính từ nó.

Không được chọn một SHA tiện lợi rồi gọi là Golden baseline.
