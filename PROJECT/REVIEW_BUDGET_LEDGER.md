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
    CURRENT HEAD   = d63c222532e87643d09b71f435a7dd276b361a88   (2026-09-01)
                     KHÔNG đổi tại S009: WP-A4 sửa `src/eth_dca_os/data/` nhưng đó là công
                     việc của CAP-DATA, không phải repair cycle của CAP-PROV. Xem §2.1.
    BRANCH         = main   (canonical trunk từ `DEC-013`, 2026-09-01)
                     Lịch sử trước tích hợp nằm trên `claude/wp-a1-provenance-v67k9h`; sau
                     merge `febc2ec` toàn bộ SHA trên vẫn reachable từ `main`, nên phép đo
                     budget vẫn tái dựng được bằng git.

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

    ALLOWED BUDGET            = 2 repair cycle        <- DEC-012 (chủ dự án, 2026-09-01)
    CURRENT BUDGET USED       = 2 repair cycle
    CURRENT BUDGET REMAINING  = 0
    OWNER_EXTENSION           = NOT GRANTED

    Ngoài ra đã tiêu: 3 vòng E2 (E2-WP-A1-001, -002, -003 — cả ba FAIL);
    340 insertion / 45 deletion trên production path, tính tích luỹ từ baseline 666de14.

`MIGRATION_UNCERTAINTY` trước đây ở mục này **ĐÃ ĐƯỢC GIẢI QUYẾT** bởi `DEC-012`. Lý do
ghi lại để không ai đọc nhầm rằng hạn mức từng tồn tại: bộ governance V3.2 của repo chưa
bao giờ định nghĩa mô hình review/repair budget, nên "remaining" không thể tính ra từ dữ
liệu lịch sử — nó chưa từng tồn tại để mà tiêu. Chủ dự án nay đặt hạn mức, tính TỪ baseline
`666de14`, KHÔNG tính lại từ 0.

Hệ quả bắt buộc:

    WP-A1 KHÔNG được mở repair cycle thứ tư nếu không có OWNER_EXTENSION mới, tường minh.

Budget KHÔNG reset qua bất kỳ ranh giới nào. Đã kiểm bằng git tại phiên Owner Disposition
(2026-09-01): hai commit governance `62f8bac` (adoption V4.3) và `d63c222` (source
reconciliation) có **diff production path = 0**, nên KHÔNG được tính là repair cycle của
WP-A1. Phiên Owner Disposition cũng có diff production path = 0 và không tiêu chu kỳ nào.

Tiền lệ đã ghi trong bảng trên và được `DEC-012` khẳng định lại: một hạng mục đóng được
**hoàn toàn bằng tài liệu** có diff production path = 0, nên **không tiêu repair cycle** —
xem dòng "Decision pack PRE-S008" (`2f20e6c..bd7c5ff`).

Hai quyết định vẫn ĐANG MỞ, `DEC-012` KHÔNG quyết thay:

- `ESCALATION_PROTOCOL.md` đã kích hoạt (lần thứ BA qua E2); reviewer E2 vòng ba đề xuất
  `VERIFICATION_DEPTH` (giữ Tier C, nâng Effort `xhigh` → `max`), KHÔNG đề xuất
  `CAPABILITY_CEILING`. Chủ dự án chưa chọn.
- Disposition cho 3 hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED` của WP-A1 — xem
  `docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md` §4.

---

## 2. Các capability khác

| Capability | Lineage root | Baseline SHA | Repair cycles | Vòng E2 | Ghi chú |
|---|---|---|---|---|---|
| `CAP-PIPELINE` | `WP-A2` | `0f2a2ab` | 0 | 1 (PASS) | DONE tại S006 |
| `CAP-ENGINE` | `WP-A3` | `5645a74` | 0 | 1 (PASS) | DONE tại S003; `WP-A7` DONE tại S004 (E2 PASS WITH FOLLOW-UPS) |
| `CAP-DEBT` | `WP-D1` | `1f4c2b7` | 0 | 0 | DONE tại S005, E1 |
| `CAP-DATA` | `WP-A4` | `06b381c` | 0 | 0 | DONE tại S009 (9/9 REQUIRED PASS) — xem §2.1 và §4.2. Sửa lại 2026-09-01: ô này còn ghi `VERIFYING` sau khi WP-A4 đã DONE, lệch với `CAPABILITY_REGISTRY.md` §2 |
| `CAP-MEASURE` | `WP-A5` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-ORDER` | `WP-A6` | chưa bắt đầu | 0 | 0 | PLANNED |
| `CAP-WEBAPP` | `WP-C1` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-SPEC` | `WP-D2` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-GOVTOOL` | `MICRO-GOVDEF-001` | `4fab2e9` | 0 | 0 | Phần glob validator chưa có owner |

Các capability chưa bắt đầu có budget used = 0 vì **chưa tiêu**, không phải vì được reset.

### 2.1 `CAP-DATA` — Ngữ nghĩa dữ liệu thiếu/hỏng

    LINEAGE ROOT   = WP-A4 (docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md)
    BASELINE SHA   = 06b381cb8dd2fc41806104b2cfbb1a539d2ceaaf   (2026-09-01, commit cuối
                     trước khi WP-A4 bắt đầu — phiên Owner Disposition)
    BRANCH         = main   (canonical trunk từ `DEC-013`, 2026-09-01)
                     Baseline SHA KHÔNG đổi và vẫn là ancestor của `main` sau merge `febc2ec`.

| # | Loại | BASE SHA | HEAD SHA | Diff production path | Kết quả |
|---|---|---|---|---|---|
| 0 | Implementation ban đầu (S009) | `06b381c` | `85fa30f` | 5 files, +282 / −36 | 9/9 REQUIRED check PASS |

    REPAIR CYCLES ĐÃ TIÊU  = 0
    VÒNG E2 ĐÃ TIÊU        = 0   (CHECK-A4-09 là RECOMMENDED, không phải điều kiện DONE)

Delivery change budget tích luỹ, đo trực tiếp (không cộng tay):

    git diff --shortstat 06b381cb8dd2fc41806104b2cfbb1a539d2ceaaf..HEAD \
        -- src/eth_dca_os webapp pyproject.toml pyproject.lock

    -> 5 files changed, 282 insertions(+), 36 deletions(-)

Trạng thái budget:

    ALLOWED BUDGET            = 2 repair cycle        <- DEC-017 (chủ dự án, 2026-09-01)
    CURRENT BUDGET USED       = 0 repair cycle
    CURRENT BUDGET REMAINING  = 2 repair cycle
    OWNER_EXTENSION           = KHÔNG CẦN

Effective Risk của `CAP-DATA` = **HIGH** — `DEC-017` (chủ dự án, 2026-09-01). Trước đó mục này
ghi `MAX(Local Risk 3, Blast Radius 2)` = **3**, tính từ routing metadata đã FROZEN của WP-A4
(`R: 3`, `B: 2`). Chủ dự án chấm lại **Blast Radius**, không nâng bằng trực giác:
`RISK_MODEL.md` § Blast Radius — HIGH liệt kê "a wrong aggregation feeding an important
decision", đúng đường đi của `F-S009-01`. Local Risk giữ nguyên; công thức
`Effective Risk = MAX(Local Risk, Blast Radius)` không đổi. Golden Reduction KHÔNG thoả (chưa
có Golden baseline canonical — `HARDENING_BACKLOG.md` H-10), nên không được hạ một mức.
Routing metadata FROZEN của WP-A4 KHÔNG bị sửa; đây là chấm risk ở cấp capability.

`ALLOWED` trước đây ghi "CHƯA LƯỢNG HOÁ" vì `DELIVERY_LOOP.md` §II.4 nói `<N>` là **PROJECT
value** mà tầng dự án chưa khai. `DEC-017` khai con số đó. `USED = 0` giữ nguyên: đây là
**khai hạn mức**, KHÔNG phải reset — `USED` của `CAP-DATA` chưa từng khác 0.

Ghi rõ giới hạn: chỉ thị phiên S009 yêu cầu "nếu budget chưa được canonical xác định thì áp
dụng V4.3 default theo Effective Risk hiện tại". Dự án chưa có một con số `<N>` cho
`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX` — `DELIVERY_LOOP.md` §II.4 nói
rõ đó là **PROJECT value**, phải khai ở tầng dự án, và tầng dự án chưa khai. Nguyên nhân
gốc đã có số hiệu: `HARDENING_BACKLOG.md` **H-10** — chưa có Golden Baseline nên tầng budget
thứ hai chưa đo được. Vì vậy `ALLOWED BUDGET` ở đây ghi đúng như nó là: default V4.3 chưa
được lượng hoá. **Không** chọn một con số tiện tay rồi gọi đó là hạn mức.

`CAP-DATA` KHÔNG kế thừa và KHÔNG bị tính vào budget của `CAP-PROV`. Hai lineage root khác
nhau (`WP-A4` vs `WP-A1`); đây không phải một task split để giải phóng budget — WP-A4 đã tồn
tại trong roadmap từ T-04 (2026-08-23), trước khi WP-A1 tiêu hết budget (`DEC-012`,
2026-09-01). Việc hấp thụ `F-E2A1R3-05` vào WP-A4 (`DEC-014`) là định tuyến finding theo
`REVIEW_PROTOCOL.md`, không phải tạo unit công việc mới: số task ID mới = **0**.

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

---

## 4. Kiểm lại bằng git tại phiên Integration Recheck (2026-09-01, HEAD `07bb241`)

Toàn bộ số dưới đây được **đo lại bằng lệnh**, không chép từ mục trên và không cộng tay.
Production paths theo `PRODUCTION_PATHS.md` §1.

### 4.1 Các con số đã ghi — ĐỐI CHIẾU KHỚP

    git diff --shortstat 666de14..d63c222 -- <production paths>
      -> 8 files, +340 / -45          KHỚP §1
    git diff --shortstat 06b381c..HEAD  -- <production paths>
      -> 5 files, +282 / -36          KHỚP §2.1

Các commit governance-only, kiểm lại diff production path = 0 (nên KHÔNG tiêu chu kỳ nào):

    6c11a7e..62f8bac  = 0      (adoption V4.3)
    62f8bac..d63c222  = 0      (source reconciliation)
    d63c222..06b381c  = 0      (phiên Owner Disposition)
    85fa30f..07bb241  = 0      (commit sửa số đo ledger)

### 4.2 `CAP-DATA` — trạng thái budget sau khi `WP-A4` DONE

    Effective Risk            = HIGH                <- DEC-017 (chủ dự án, 2026-09-01)
                                      Blast Radius chấm lại theo RISK_MODEL.md;
                                      Local Risk và routing metadata FROZEN không đổi
    ALLOWED repair cycles     = 2                   <- DEC-017
    USED repair cycles        = 0
    REMAINING repair cycles   = 2
    OWNER_EXTENSION           = KHÔNG CẦN

    Ba con số trên đúng TRƯỚC bản sửa `F-S009-01`. Bản sửa đó, nếu thực hiện theo `DEC-016`,
    là **repair cycle #1** của `CAP-DATA` và phải được ghi vào bảng §2.1. Budget KHÔNG được
    reset ở phiên sau.

`USED = 0` **không** phải vì WP-A4 DONE thì được reset. Lượt `06b381c..85fa30f` là
**implementation ban đầu**, và ledger này đã dùng đúng quy ước đó cho `CAP-PROV` ở §1
("REPAIR CYCLES ĐÃ TIÊU = 2, **ngoài lượt implementation ban đầu**"). Canonical V4.3 không
định nghĩa lượt implementation đầu tiên là repair cycle, nên KHÔNG tự tính thành một.

`ALLOWED` nay đã có con số nhờ `DEC-017` — con số do **chủ dự án** đặt, không phải do phiên
làm việc chọn tiện tay. Lưu ý phạm vi: `DEC-017` khai budget **tầng A** (review/repair cycle).
Budget **tầng B** (`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX`) VẪN chưa
khai được vì chưa có Golden baseline canonical — `HARDENING_BACKLOG.md` **H-10** vẫn mở, và
`GOLDEN_BASELINE_SHA` vẫn `PENDING_OWNER_DATA / MIGRATION_REQUIRED`.

### 4.3 `F-S009-01` nằm NGOÀI mọi cumulative repair diff — hệ quả budget

    git log --oneline 666de14..HEAD -- src/eth_dca_os/indicators.py   ->  0 commit

`indicators.py` chưa từng bị chạm kể từ baseline `666de14`. Vậy `F-S009-01` **không** nằm
trong cumulative repair diff của `CAP-PROV`, cũng **không** nằm trong của `CAP-DATA`.

`REVIEW_PROTOCOL.md` quy định: *"A finding inside the current cycle's cumulative repair diff
is a defect of that same repair. It does not open a new repair cycle and does not consume new
budget."* Ở đây điều ngược lại đúng: đây KHÔNG phải khiếm khuyết của một lượt sửa đã tiêu,
nên sửa nó **SẼ tiêu một repair cycle mới** của capability nhận nó. Bản sửa không miễn phí —
dữ kiện này phải nằm trước mặt chủ dự án khi chọn phương án ở
`docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` §II.7.

### 4.4 Không đổi

- `CAP-PROV`: `ALLOWED = 2 · USED = 2 · REMAINING = 0 · OWNER_EXTENSION = NOT GRANTED`
  (`DEC-012`). Phiên này KHÔNG cấp `OWNER_EXTENSION`, KHÔNG đụng ba con số đó.
- `LEGACY_GATE_DISPOSITION` của WP-A1: KHÔNG giải quyết ở phiên này.
- Hai quyết định đang mở nêu ở §1 (`VERIFICATION_DEPTH`; disposition 3 hạng mục legacy của
  WP-A1) vẫn ĐANG MỞ.
- `GOLDEN_BASELINE_SHA` = `PENDING_OWNER_DATA / MIGRATION_REQUIRED`, không đổi.
