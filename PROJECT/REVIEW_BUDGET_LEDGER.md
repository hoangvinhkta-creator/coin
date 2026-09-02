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
| `CAP-DATA` | `WP-A4` | `06b381c` | **1** | 0 | DONE lại tại S010 sau CAP-DATA REPAIR CYCLE #1 (10/10 REQUIRED PASS) — xem §2.1 và §4.2 |
| `CAP-MEASURE` | `WP-A5` | chưa bắt đầu | 0 | 0 | READY |
| `CAP-ORDER` | `WP-A6` | chưa bắt đầu | 0 | 0 | PLANNED |
| `CAP-WEBAPP` | `WP-C1` | `cb75f9d` | 0 | 0 | `WP-C1` DONE 2026-09-02; `T-09A` IMPLEMENTED 2026-09-02 — xem §2.2 |
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
| 1 | **Repair cycle 1** (S010, `DEC-016`) | `cb75f9d` | `ef8cdbb` | 1 file, +74 / −5 | `CHECK-A4-11` PASS (E1); batch review PASS → `ELIGIBLE_FOR_FREEZE` |

Chu kỳ 1 đóng `F-S009-01`. Base SHA `cb75f9d1fb139f4c5daae063e754245998819f22` là
`origin/main` tại thời điểm mở chu kỳ; head SHA `ef8cdbb00a7ff2d271c1233df4baf151ab46b62a`
là commit mang bản sửa production. Cặp SHA này là thứ làm cho quy tắc "finding nằm trong
cumulative repair diff thuộc CÙNG chu kỳ" kiểm chứng được, chứ không thành chuyện ý kiến
(`CAPABILITY_MODEL.md` §II.8).

    REPAIR CYCLES ĐÃ TIÊU  = 1   (ngoài lượt implementation ban đầu)
    VÒNG E2 ĐÃ TIÊU        = 0   (CHECK-A4-09 là RECOMMENDED, không phải điều kiện DONE;
                                  batch review S010 là E1 + dò đối kháng, KHÔNG phải E2)

Delivery change budget tích luỹ, đo trực tiếp (không cộng tay):

    git diff --shortstat 06b381cb8dd2fc41806104b2cfbb1a539d2ceaaf..HEAD \
        -- src/eth_dca_os webapp pyproject.toml pyproject.lock

    -> 6 files changed, 356 insertions(+), 41 deletions(-)     (đo lại tại S010)

Con số trước S010 là `5 files, +282 / −36`; chênh lệch đúng bằng chu kỳ 1
(`indicators.py`, +74 / −5). Tổng tích luỹ vẫn là con số ĐO, không phải phép cộng.

**Ghim mốc đo (thêm tại T-09A, 2026-09-02 — KHÔNG đổi con số nào ở trên).** `HEAD` trong lệnh
trên là `ef8cdbb`, HEAD của S010. Đọc lại lệnh đó ở một HEAD muộn hơn sẽ ra số khác vì glob
`webapp` nuốt cả công việc của capability khác (T-09A sửa `webapp/app_logic.js`) — đó là
`HARDENING_BACKLOG.md` **H-21**. Phép đo tích luỹ của `CAP-DATA` phải chạy với
`06b381c..ef8cdbb`, hoặc giới hạn path vào `src/eth_dca_os`, để không quy nhầm công việc của
`CAP-WEBAPP` sang `CAP-DATA`.

Trạng thái budget:

    ALLOWED BUDGET            = 2 repair cycle        <- DEC-017 (chủ dự án, 2026-09-01)
    CURRENT BUDGET USED       = 1 repair cycle        <- S010, CAP-DATA REPAIR CYCLE #1
    CURRENT BUDGET REMAINING  = 1 repair cycle
    OWNER_EXTENSION           = KHÔNG CẦN

Budget KHÔNG được reset ở phiên sau. `USED` đi từ 0 lên 1 vì chu kỳ 1 THỰC SỰ đã tiêu, không
phải vì phiên S010 tự đặt lại số. Phiên tiếp theo phải ĐỌC hai con số này, không tự khai lại.
Nếu cần một chu kỳ thứ hai, `REMAINING = 1` cho phép đúng một lần nữa; hết đó chỉ còn
`ACCEPT_AS_IS | DESCOPE | OWNER_EXTENSION`.

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


### 2.2 `CAP-WEBAPP` — App web: sổ sách, trạng thái thực thi, parity JS/Python

    LINEAGE ROOT   = WP-C1 (docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md)
    THÀNH VIÊN     = WP-C1 (DONE), T-09A (IMPLEMENTED), WP-C2 (BLOCKED), WP-C3, WP-C4 (PLANNED)
    BASELINE SHA   = cb75f9d1fb139f4c5daae063e754245998819f22   (2026-09-02, commit cuối trước
                     khi nhánh web WP-C1 tách ra khỏi `main`)
    BRANCH         = main   (canonical trunk từ `DEC-013`)

Mục này được **khởi lập tại T-09A** vì trước đó `CAP-WEBAPP` chưa tiêu gì. Bảng §2 ghi
"chưa bắt đầu" là đúng ở thời điểm viết (2026-09-01), nhưng đã lạc hậu kể từ khi `WP-C1`
DONE ngày 2026-09-02. `USED` vẫn = 0 vì **chưa tiêu**, không phải vì được reset.

| # | Loại | BASE SHA | HEAD SHA | Diff production path (theo khai báo) | Kết quả |
|---|---|---|---|---|---|
| — | `WP-C1` (kết luận, không vá) | `cb75f9d` | `814d185` | **0** — `CHECK-C1-07` chứng minh `app_logic.js`/`engine.js` không đổi một dòng | 8/8 REQUIRED PASS (E1) |
| 0 | `T-09A` implementation ban đầu | `814d185` | `d125fe5` | 1 file, +88 / −16 (`webapp/app_logic.js`) | 12/12 REQUIRED PASS (E1); batch review PASS, 0 BLOCKING |

    REPAIR CYCLES ĐÃ TIÊU  = 0   (lượt trên là implementation ban đầu, không phải repair
                                  cycle — cùng quy ước đã dùng ở §1 cho CAP-PROV và §2.1
                                  cho CAP-DATA)
    VÒNG E2 ĐÃ TIÊU        = 0   (WP-C1 và T-09A đều đóng ở mức E1; batch review T-09A là
                                  E1 + dò đối kháng, KHÔNG phải E2)

Delivery change budget tích luỹ, đo trực tiếp (không cộng tay). Hai con số vì
`PRODUCTION_PATHS.md` tự mâu thuẫn — xem `HARDENING_BACKLOG.md` **H-21**:

    # lệnh glob ghi ở PRODUCTION_PATHS.md §1 (nuốt cả file test mà §2 loại trừ)
    git diff --shortstat cb75f9d..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 8 files changed, 590 insertions(+), 17 deletions(-)

    # theo KHAI BÁO production path (§1 bảng + §2 loại trừ) — con số CÓ THẨM QUYỀN
    git diff --shortstat cb75f9d..HEAD -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 1 file changed, 88 insertions(+), 16 deletions(-)

`webapp/engine.js` = 0 dòng đổi kể từ baseline, nên T-09A KHÔNG mở rộng bề mặt trôi parity
của `RSK-002`.

Trạng thái budget:

    ALLOWED BUDGET            = 2 repair cycle   <- default V4.3 theo Effective Risk = HIGH
                                                    (`GOVERNANCE_V4.md` §II.2). Chủ dự án
                                                    CHƯA đặt con số tường minh cho
                                                    `CAP-WEBAPP` như `DEC-012`/`DEC-017` đã
                                                    làm cho `CAP-PROV`/`CAP-DATA`.
    CURRENT BUDGET USED       = 0 repair cycle
    CURRENT BUDGET REMAINING  = 2 repair cycle
    OWNER_EXTENSION           = KHÔNG CẦN

Effective Risk của `CAP-WEBAPP` tại T-09A = **HIGH**: `Effective Risk = MAX(Local Risk 3,
Blast Radius)`, và Blast Radius chấm theo đường dữ liệu — V-01/V-02 rơi thẳng vào "wrong
money … settlement" của `RISK_MODEL.md`. Golden Reduction KHÔNG thoả (chưa có Golden —
`H-10`). Hệ quả đã thi hành: batch review bắt buộc cuối phiên.

Ghi rõ giới hạn, không tự nâng thẩm quyền: `ALLOWED = 2` ở đây là **default V4.3**, không
phải một Owner Decision. Nếu chủ dự án muốn một con số khác cho `CAP-WEBAPP`, đó là quyết
định của chủ dự án và phải ghi ở `PROJECT/PROJECT_DECISIONS.md`; phiên T-09A KHÔNG tự đặt
hạn mức và KHÔNG cấp `OWNER_EXTENSION`.

Budget tầng B (`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX`) vẫn chưa khai
được vì chưa có Golden baseline canonical — `H-10` vẫn mở, `GOLDEN_BASELINE_SHA` vẫn
`PENDING_OWNER_DATA / MIGRATION_REQUIRED`.

`CAP-WEBAPP` KHÔNG kế thừa và KHÔNG bị tính vào budget của `CAP-PROV` hay `CAP-DATA`: ba
lineage root khác nhau, và `T-09A` đã tồn tại trong roadmap từ RCP-001 (2026-08-23) — không
phải task tách ra để giải phóng budget. Số task ID mới do T-09A tạo = **0**.

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

    Ba con số trên đúng TRƯỚC bản sửa `F-S009-01`.

**Cập nhật tại S010 (2026-09-01) — chu kỳ đã tiêu, đo lại bằng lệnh:**

    git diff --shortstat cb75f9d..ef8cdbb -- <production paths>
      -> 1 file changed, 74 insertions(+), 5 deletions(-)     = CAP-DATA REPAIR CYCLE #1
    git diff --shortstat 06b381c..HEAD    -- <production paths>
      -> 6 files changed, 356 insertions(+), 41 deletions(-)  = tích luỹ CAP-DATA

    ALLOWED repair cycles     = 2                   <- DEC-017, KHÔNG đổi
    USED repair cycles        = 1                   <- chu kỳ 1 đóng F-S009-01
    REMAINING repair cycles   = 1
    OWNER_EXTENSION           = KHÔNG CẦN

    Chu kỳ 1 KHÔNG bị reset bởi phản hồi của batch review: `DEC-016` và
    `GOVERNANCE_V4.md` §II.2 quy định một repair cycle = MỘT lượt sửa sau khi reviewer trả
    TOÀN BỘ BLOCKING finding. Batch review S010 trả 0 BLOCKING, nên không phát sinh lượt
    sửa thứ hai và `USED` dừng ở 1. Phiên này KHÔNG tự mở chu kỳ #2.

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

**Đã thi hành tại S010 đúng như dự báo ở trên.** `indicators.py` nay có đúng MỘT commit kể từ
baseline `666de14`:

    git log --oneline 666de14..HEAD -- src/eth_dca_os/indicators.py
      -> ef8cdbb  WP-A4 REPAIR CYCLE #1 — neo cửa sổ indicator daily vào NGÀY LỊCH

Commit đó LÀ cumulative repair diff của chu kỳ 1. Mọi finding nằm bên trong `cb75f9d..ef8cdbb`
từ đây trở đi là khiếm khuyết của CHÍNH chu kỳ 1 và **không** mở chu kỳ mới.

### 4.4 Không đổi

- `CAP-PROV`: `ALLOWED = 2 · USED = 2 · REMAINING = 0 · OWNER_EXTENSION = NOT GRANTED`
  (`DEC-012`). Phiên này KHÔNG cấp `OWNER_EXTENSION`, KHÔNG đụng ba con số đó.
- `LEGACY_GATE_DISPOSITION` của WP-A1: KHÔNG giải quyết ở phiên này.
- Hai quyết định đang mở nêu ở §1 (`VERIFICATION_DEPTH`; disposition 3 hạng mục legacy của
  WP-A1) vẫn ĐANG MỞ.
- `GOLDEN_BASELINE_SHA` = `PENDING_OWNER_DATA / MIGRATION_REQUIRED`, không đổi.
