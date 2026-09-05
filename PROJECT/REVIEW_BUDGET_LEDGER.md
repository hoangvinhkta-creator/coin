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

    ALLOWED BUDGET            = 3 repair cycle        <- DEC-012 (2) + DEC-027 (+1)
    CURRENT BUDGET USED       = 3 repair cycle
    CURRENT BUDGET REMAINING  = 0
    OWNER_EXTENSION           = GRANTED +1 (DEC-027, 2026-09-03) — ĐÃ TIÊU tại S017

    Ngoài ra đã tiêu: 3 vòng E2 (E2-WP-A1-001, -002, -003 — cả ba FAIL);
    340 insertion / 45 deletion trên production path, tính tích luỹ từ baseline 666de14,
    CỘNG chu kỳ S017 (+2 file: reporting.py, pipeline.py).

**Chu kỳ #3 (S017, `DEC-027`)** — mục tiêu DUY NHẤT do chủ dự án đặt: `F-E2A1-03` và
`F-E2A1R3-03` phải xử lý trong CÙNG MỘT chu kỳ; cả hai đã đóng trong đúng một chu kỳ đó.
`F-E2A1R3-06`/`F-E2A1-08` đóng bằng docs-only, **production diff = 0 → KHÔNG tiêu chu kỳ
riêng** (tiền lệ: Decision pack PRE-S008, `2f20e6c..bd7c5ff`).
Budget nay lại `REMAINING = 0`: mọi hạng mục cần production code trong `CAP-PROV` từ đây trở
đi lại cần một `OWNER_EXTENSION` mới. `CHECK-A1-11` còn chờ E2 — rà soát độc lập KHÔNG tiêu
repair cycle, nhưng nếu E2 phát hiện defect mới cần sửa mã thì cần extension.

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
| `CAP-MEASURE` | `WP-A5` | `b095874` | 0 | 0 | DONE tại S015 — implementation ban đầu (không phải repair cycle); 9/9 REQUIRED PASS (E1), gói không có check nào đòi E2 (chủ dự án xác nhận không yêu cầu E2 bổ sung) |
| `CAP-ORDER` | `WP-A6` | `b717634` | 0 | 1 (PASS) | DONE tại S014 — implementation ban đầu (không phải repair cycle), 8/8 REQUIRED PASS, CHECK-A6-08 E2 PASS (`docs/reviews/E2-WP-A6-thu-tu-18-buoc.md`) |
| `CAP-WEBAPP` | `WP-C1` | `cb75f9d` | 0 | 0 | `WP-C1` DONE 2026-09-02; `T-09A` DONE 2026-09-02 (`DEC-018`) — xem §2.2 |
| `CAP-VERDICT` | `WP-B1` | `28b0255` | 0 | 3 (2 FAIL, 1 PASS) | Lát cắt pre-T06 tại S016 (`DEC-026`) — implementation ban đầu, KHÔNG tiêu repair cycle. Tiếp nối phiên `WP-B1 IN_PROGRESS` (2026-09-03→04, nhánh `claude/wp-b1-verdict-correctness-j9d390`): F-017 (CHECK-B1-03), `DEC-033` (CHECK-B1-04), Owner CHECK-B1-08 evidence, và HAI repair batch liên tiếp cho hai vòng fresh Independent E2 (`E2-B1-F01` FS-08 fail-open — sửa None/NaN ở batch 1, sửa thêm `±inf`/bool ở batch 2; `E2-B1-F02` officiality không chặn verdict — sửa `can_proceed_to_app` ở batch 1, sửa thêm nhãn `verdict` ở batch 2) — tất cả vẫn là **implementation ban đầu** của `WP-B1` (task chưa từng DONE nên chưa có repair cycle nào để mở) — KHÔNG tiêu repair cycle. `WP-B1`: `PLANNED → READY (DEC-031) → IN_PROGRESS → DONE (DEC-034, Lifecycle Closure 2026-09-04)`. **Diff production cộng dồn (đo bằng `git diff --stat fa6422c -- src/eth_dca_os`, mốc bắt đầu phiên IN_PROGRESS thật — KHÔNG dùng `28b0255` làm mốc vì SHA đó còn lẫn diff của các capability khác merge vào `main` trước khi phiên này branch ra):** 4 file (`benchmarks.py`, `cli.py`, `failure_signals.py`, `pipeline.py`), +108/−33 (batch 2 riêng: 2 file, +37/−13). Trong ngân sách canonical — không có REQUIRED check nào được thêm (vẫn 10), không Effective Risk tăng, không kéo việc ngoài vertical slice, không chạm `engine.py`/`gates.py`/`regime.py`/`ladders.py`/`capital.py`/`score.py`. Không `CHANGE_BUDGET_EXCEEDED`. **Đóng lifecycle (2026-09-04, `DEC-034`):** fresh Independent E2 vòng BA (`E2-WP-B1-004-FRESH-ROUND3-2026-09-04`) PASS trên đúng HEAD `9ac01b8`; artifact tích hợp vào canonical branch bằng fast-forward merge (`9ac01b8..f3fb81e`), production diff của lượt tích hợp = **0** (`git diff --stat 9ac01b8..f3fb81e -- src/ webapp/ pyproject.toml pyproject.lock` rỗng). Phiên đóng lifecycle KHÔNG tiêu repair cycle mới (diff production = 0). `CHECK-B1-09: NOT_TESTED → PASS`. `WP-B1 REQUIRED = 10/10 PASS`. **`WP-B3` (thành viên thứ ba của lineage này) IMPLEMENTED tại `S025` (2026-09-04, nhánh `claude/wp-b3-audit-trail-impl-3covtf`, tách từ `origin/main` `04f77ac`): implementation ban đầu — `WP-B3` chưa từng `DONE` nên chưa có repair cycle nào để mở → **KHÔNG tiêu repair cycle**, `used` giữ nguyên 0. Diff production của phiên, đo bằng `git diff --shortstat 04f77ac -- src/eth_dca_os webapp pyproject.toml pyproject.lock`: **1 file (`engine.py`), +266 / −15**. Trong ngân sách canonical: không REQUIRED check nào được thêm (vẫn 8), Effective Risk không tăng (Risk 2/4, Blast Radius 2/4 giữ nguyên — đầu ra tài chính bất biến bit-for-bit), không kéo việc ngoài vertical slice, không chạm `verdict.py`/`failure_signals.py`/`gates.py`/`regime.py`/`ladders.py`/`capital.py`/`score.py`/`webapp/`/`docs/spec/`. Không `CHANGE_BUDGET_EXCEEDED`. **Đóng lifecycle (2026-09-05, `DEC-037`):** chủ dự án chấp nhận evidence implementer (không rà soát E2 mới — gate `WP-B3` không đòi E2 ở check nào, `Risk 2/4 → E1` toàn bộ). `WP-B3: IMPLEMENTED → DONE`. Phiên đóng lifecycle KHÔNG tiêu repair cycle mới (diff production của lượt đóng = 0). `WP-B3 REQUIRED = 8/8 PASS`. **`WP-B2` (thành viên thứ hai của lineage này) IMPLEMENTED tại `S026` (2026-09-05, nhánh `claude/wp-b2-implementation-u9y68k`, tách từ `origin/main` `b778dc1`): gói **CHỈ VIẾT TEST** — diff production đo bằng `git diff --shortstat b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock` = **RỖNG (0 file, 0 dòng)**. Theo tiền lệ đã ghi ở §1 ("Decision pack PRE-S008", `2f20e6c..bd7c5ff`) và `DEC-012`: hạng mục có diff production path = 0 **KHÔNG tiêu repair cycle**. `used` giữ nguyên 0. Không REQUIRED check nào được thêm (vẫn 10), Effective Risk không tăng (Risk 2/4, Blast Radius 1/4 giữ nguyên — đầu ra tài chính bất biến bit-for-bit, `sha256 3ea7c8d7…` trùng trước–sau), không kéo việc ngoài vertical slice. Không `CHANGE_BUDGET_EXCEEDED`. `WP-B2 REQUIRED = 10/10 PASS`. **Đóng lifecycle (2026-09-05, `DEC-038`):** chủ dự án chấp nhận evidence implementer (không rà soát E2 mới — gate `WP-B2` không đòi E2 ở check nào, `Risk 2/4 → E1` toàn bộ). `WP-B2: IMPLEMENTED → DONE`. Phiên đóng lifecycle KHÔNG tiêu repair cycle mới (diff production của lượt đóng = 0). **Toàn bộ lineage `CAP-VERDICT` (`WP-B1`, `WP-B2`, `WP-B3`) nay DONE** → `GATE-B = CLOSED` (`DEC-038`), tính trực tiếp từ định nghĩa canonical `GATE-B = WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE`, không suy diễn thêm tiêu chí — cùng khuôn `DEC-028` đã dùng để đóng `GATE-A`. `T-07: PLANNED → READY` (hệ quả tất định của `T-06 DONE ∧ GATE-B`), CHƯA thực thi. Không ghi đè verdict official `DO_NOT_BUILD`/`can_proceed_to_app=false`.** |
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
    THÀNH VIÊN     = WP-C1 (DONE), T-09A (DONE), T-09B (IMPLEMENTED — S014),
                     WP-C2 (DONE — DEC-036, Owner-authorized Lifecycle Closure, 2026-09-04),
                     WP-C3 (READY — DEC-036), WP-C4 (PLANNED)
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
| 0' | `T-09B` implementation ban đầu (S014) | `4502ea6` | `0d4917a` | 3 file, +560 / −162 (`app_logic.js`, `app_shell.html`, `build_app.js`) + 3 file runtime MỚI chưa trong khai báo (`webapp/firebase_config.js` 25, `firestore.rules` 32, `firebase.json` 21 dòng — `H-32`) | 16/16 REQUIRED PASS (E1, Firebase Emulator Suite); batch review PASS, 0 BLOCKING còn lại; project thật NOT_TESTED |
| 0'' | `WP-C2` implementation ban đầu (S024) | `2189a8f` | nhánh `claude/wp-c2-execution-state-y4rraf` | **1 file, +128 / −0** (`src/eth_dca_os/engine.py`) — thuần THÊM MỚI, không xoá/sửa dòng nào; `webapp/` = 0, `pyproject.*` = 0 | 8/8 REQUIRED PASS (E1; `CHECK-C2-07` E0 theo gate FROZEN); backtest bit-for-bit không đổi (`sha256 e0492a58…`); full suite 494/494 |

    REPAIR CYCLES ĐÃ TIÊU  = 0   (ba lượt trên đều là implementation ban đầu, không phải
                                  repair cycle — cùng quy ước đã dùng ở §1 cho CAP-PROV và
                                  §2.1 cho CAP-DATA. `WP-C2` chưa từng DONE nên chưa có
                                  repair cycle nào để mở.)
    VÒNG E2 ĐÃ TIÊU        = 0   (WP-C1 và T-09A đều đóng ở mức E1; batch review T-09A là
                                  E1 + dò đối kháng, KHÔNG phải E2. Completion Gate của
                                  `WP-C2` KHÔNG đòi check E2 nào — bảy check E1, một E0.)

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

    ALLOWED BUDGET            = 2 repair cycle   <- Owner-ratified qua `DEC-018`
                                                    (`OD-WEBAPP-01`, 2026-09-02). Cùng con số
                                                    default V4.3 theo Effective Risk = HIGH
                                                    (`GOVERNANCE_V4.md` §II.2), nay được chủ
                                                    dự án RATIFY tường minh như `DEC-012`/
                                                    `DEC-017` đã làm cho `CAP-PROV`/`CAP-DATA`.
    CURRENT BUDGET USED       = 0 repair cycle
    CURRENT BUDGET REMAINING  = 2 repair cycle
    OWNER_EXTENSION           = KHÔNG CẦN

Effective Risk của `CAP-WEBAPP` tại T-09A = **HIGH**: `Effective Risk = MAX(Local Risk 3,
Blast Radius)`, và Blast Radius chấm theo đường dữ liệu — V-01/V-02 rơi thẳng vào "wrong
money … settlement" của `RISK_MODEL.md`. Golden Reduction KHÔNG thoả (chưa có Golden —
`H-10`). Hệ quả đã thi hành: batch review bắt buộc cuối phiên.

`ALLOWED = 2` ở đây là **Owner Decision** (`DEC-018`/`OD-WEBAPP-01`, 2026-09-02) — cùng con
số default V4.3, nay được chủ dự án ratify tường minh thay vì để ở trạng thái default chưa
khai. Nếu chủ dự án muốn đổi con số này sau này, đó là một quyết định mới ghi ở
`PROJECT/PROJECT_DECISIONS.md`.

Budget tầng B (`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX`) vẫn chưa khai
được vì chưa có Golden baseline canonical — `H-10` vẫn mở, `GOLDEN_BASELINE_SHA` vẫn
`PENDING_OWNER_DATA / MIGRATION_REQUIRED`.

`CAP-WEBAPP` KHÔNG kế thừa và KHÔNG bị tính vào budget của `CAP-PROV` hay `CAP-DATA`: ba
lineage root khác nhau, và `T-09A` đã tồn tại trong roadmap từ RCP-001 (2026-08-23) — không
phải task tách ra để giải phóng budget. Số task ID mới do T-09A tạo = **0**.

#### 2.2.1 Phiên Owner Authority T-09B (2026-09-02) — `DEC-019`, budget KHÔNG đổi

`T-09B` được thêm vào THÀNH VIÊN ở trên. Đây là **mapping một task đã tồn tại** trong roadmap từ
RCP-001 (2026-08-23) vào capability đã tồn tại — không phải task mới, không phải nhánh tách ra để
xin thêm budget (`GOVERNANCE_V4.md` §II.2, trục ngang).

    ALLOWED BUDGET            = 2 repair cycle    <- KHÔNG ĐỔI (Owner-ratified, `DEC-018`;
                                                     `DEC-019` điểm 5 xác nhận lại)
    CURRENT BUDGET USED       = 0 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET REMAINING  = 2 repair cycle    <- KHÔNG ĐỔI
    OWNER_EXTENSION           = KHÔNG CẦN

Ba con số trên **không được đọc lại như thể vừa được cấp mới**. `USED = 0` vì `CAP-WEBAPP` chưa
tiêu chu kỳ sửa nào, không phải vì phiên này đặt lại. Implementation `T-09B` sau này là **INITIAL
IMPLEMENTATION**, KHÔNG tiêu repair cycle — cùng quy ước đã dùng cho `WP-A4` (`DEC-016`/`DEC-017`)
và `T-09A` (`DEC-018`).

Effective Risk của `CAP-WEBAPP` tại `T-09B` = **HIGH**, cùng mức đã chấm tại `T-09A`:
`Effective Risk = MAX(Local Risk 3, Blast Radius 3) = 3`. Blast Radius của T-09B chấm **3** (cao
hơn mức 2 của T-09A) vì một lớp lưu trữ hỏng làm sai **toàn bộ** sổ, không chỉ một đường kế toán.
Mức HIGH không đổi vì công thức lấy MAX. Golden Reduction KHÔNG dùng được (`H-10`).

Phiên ghi `DEC-019` là phiên governance-only. Đo trực tiếp, không cộng tay:

    git diff --shortstat <base>..HEAD -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 0   (production diff = 0; xem `docs/sessions/S011-t09b-firebase-authority.md`)

Vì diff production = 0, phiên này **không tiêu** chu kỳ nào và không cần cặp BASE/HEAD SHA trong
bảng §2.2. Cặp SHA sẽ được ghi tại lượt implementation thật của `T-09B`.

#### 2.2.2 Phiên `DEC-020` (2026-09-02) — OD-A/OD-B/OD-B2 resolved, budget KHÔNG đổi

`OD-A`, `OD-B`, `OD-B2` được chủ dự án giải quyết (Firebase Hosting · Cloud Firestore ·
Anonymous Auth). Một khe mới `OD-C` (recovery semantics) được phát hiện và ghi lại — xem
`CAPABILITY_REGISTRY.md` §8.2 và Task Spec `T-09B` § OD-C. Đây là governance/tài liệu, KHÔNG
phải implementation.

    ALLOWED BUDGET            = 2 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET USED       = 0 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET REMAINING  = 2 repair cycle    <- KHÔNG ĐỔI

    git diff --shortstat origin/main..HEAD -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 0   (production diff = 0)

`T-09B` vẫn `PLANNED`, chưa `IN_PROGRESS`, nên không có implementation nào để tiêu budget.

#### 2.2.3 Phiên `DEC-021` (2026-09-02) — `OD-C` đóng = R2, `T-09B: PLANNED → READY`

Personal Tool Simplification Principle chốt `OD-C = R2`. Ready Gate 15/15 ĐẠT, Completion Gate
16/16 REQUIRED FROZEN, `T-09B: PLANNED → READY`. Đây vẫn là chuẩn bị, KHÔNG phải implementation.

    ALLOWED BUDGET            = 2 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET USED       = 0 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET REMAINING  = 2 repair cycle    <- KHÔNG ĐỔI

    git diff --shortstat origin/main..HEAD -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 0   (production diff = 0)

Khi implementation thật của `T-09B` bắt đầu (task chuyển `READY → IN_PROGRESS`), lượt đầu tiên
vẫn là **INITIAL IMPLEMENTATION** — cùng quy ước `WP-A4`/`T-09A` — và không tự động tiêu repair
cycle.

---

#### 2.2.4 Phiên thực thi T-09B — S014 (2026-09-02): implementation ban đầu, budget KHÔNG đổi

Lượt `4502ea6..0d4917a` (hàng `0'` ở bảng trên) là **INITIAL IMPLEMENTATION** của `T-09B` — cùng
quy ước đã dùng cho `WP-A4` (`DEC-016`/`DEC-017`) và `T-09A` (`DEC-018`/`DEC-019` điểm 5). Batch
review (`docs/reviews/T-09B-batch-review.md`) trả 0 BLOCKING còn lại: finding `F-T09B-01` (hai tab
stale ghi đè) được phát hiện và sửa TRƯỚC commit implementation, tức nằm trong cumulative diff của
chính lượt này → **cùng lượt**, không mở repair cycle (`REVIEW_PROTOCOL.md` § "inside the cumulative
repair diff -> same cycle").

Delivery change budget tích luỹ từ baseline `cb75f9d` của `CAP-WEBAPP`, đo trực tiếp:

    # theo KHAI BÁO production path (§1 bảng + §2 loại trừ)
    git diff --shortstat cb75f9d..0d4917a -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 4 files changed, 736 insertions(+), 193 deletions(-)
         (gồm src/eth_dca_os/indicators.py của CAP-DATA repair cycle #1 — S010 — đã vào main trong
          khoảng này: 1 file changed, 74 insertions(+), 5 deletions(-); KHÔNG thuộc CAP-WEBAPP)
    # phần thuộc CAP-WEBAPP (bốn file webapp trong khai báo) — con số có thẩm quyền cho lineage này
    git diff --shortstat cb75f9d..0d4917a -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js
      -> 3 files changed, 662 insertions(+), 188 deletions(-)
    # + ba file runtime mới KHÔNG nằm trong khai báo (H-32): 78 dòng
    # lệnh glob §1 (nuốt test/harness/package-lock — H-21): 16 files changed, 12315 insertions(+), 248 deletions(-) — không dùng để phân loại

`webapp/engine.js` = 0 dòng đổi kể từ baseline — bề mặt trôi parity `RSK-002` không mở rộng.

    ALLOWED BUDGET            = 2 repair cycle    <- KHÔNG ĐỔI (Owner-ratified, `DEC-018`)
    CURRENT BUDGET USED       = 0 repair cycle    <- KHÔNG ĐỔI (implementation ban đầu, không phải repair)
    CURRENT BUDGET REMAINING  = 2 repair cycle    <- KHÔNG ĐỔI
    OWNER_EXTENSION           = KHÔNG CẦN

`T-09B` = `IMPLEMENTED`, chưa `DONE` (thẩm quyền chủ dự án; production reachability trên project
Firebase thật chưa kiểm). Số task ID mới = **0**.

#### 2.2.5 `T-09B`: `IMPLEMENTED → DONE` (`DEC-024`, 2026-09-03) — budget KHÔNG đổi

Production reachability đóng bằng evidence E1 trên `https://tinphatcontent.web.app` thật
(CHECK-T09B-01/02/03/04/14, Owner tự báo cáo — `docs/reviews/T-09B-production-verification.md`).
Chủ dự án xác nhận `DEC-024`: `T-09B: IMPLEMENTED → DONE`. Toàn bộ chuỗi phiên từ S014 tới đây
(rules merge với project dùng chung, xác minh Owner UID, production verification) vẫn là
**INITIAL IMPLEMENTATION** — không phát sinh finding CONFIRMED BLOCKING nào cần sửa sau lần
16/16 PASS đầu tiên, nên không mở repair cycle.

    ALLOWED BUDGET            = 2 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET USED       = 0 repair cycle    <- KHÔNG ĐỔI
    CURRENT BUDGET REMAINING  = 2 repair cycle    <- KHÔNG ĐỔI

## 3. Golden cumulative change budget

    GOLDEN_BASELINE_SHA = PENDING_OWNER_DATA / MIGRATION_REQUIRED

Dự án chưa có Golden baseline canonical. "Golden" ở đây là **official run** (`T-06`).

**Cập nhật `DEC-041` I (2026-09-05) — đóng stale `ST-11`.** Câu cũ ở vị trí này ghi `T-06` là
`PLANNED` và bị chặn bởi `GATE-A` lẫn `BLK-001`; điều đó đã sai từ 2026-09-03: `T-06 = DONE`
(`DEC-031`, historical governance disposition — KHÔNG phải validation PASS), `GATE-A = CLOSED`
(`DEC-028`), `BLK-001 = RESOLVED` (`DEC-031`). Official run **đã tồn tại**, verdict =
`DO_NOT_BUILD`.

Nhận định cốt lõi của mục này thì **VẪN ĐÚNG và phải giữ**: vì Master Index §6 cấm chạy lại
`T-06`, lát cắt đó KHÔNG trở thành một Golden trace **tái lập được**, nên không capability nào
được giảm Blast Radius nhờ nó (`RISK_MODEL.md` § Golden Reduction đòi một test chạy lại được).

**Trạng thái lineage sau `DEC-041` A/J.** Các lineage thuộc bộ máy validation V2.1.5 —
`CAP-PROV`, `CAP-DATA`, `CAP-ENGINE`, `CAP-PIPELINE`, `CAP-MEASURE`, `CAP-ORDER`, `CAP-VERDICT`
— chuyển sang **FROZEN RESEARCH (lịch sử đóng)**: giữ nguyên mọi con số đã ghi, **KHÔNG reset,
KHÔNG chuyển, KHÔNG xoá** (`AGENTS.md` §3 *"Budget does not reset"*). `CAP-SPEC` đóng cùng
V2.1.5 (`WP-D2` `CANCELLED`).
**`CAP-WEBAPP` là lineage còn sống** và là lineage root tự nhiên của công việc L-1 —
allowed 2 / used 0 / remaining 2, Effective Risk `HIGH` (§2.2), **không đổi** ở phiên `DEC-041`
(production diff của phiên = 0 → không tiêu repair cycle, theo tiền lệ §1 và `DEC-012`).
Báo trước: công việc L-1 dưới `CAP-WEBAPP` nhiều khả năng chạm `ABSORPTION_LIMIT` ngưỡng B/D →
ghi `ABSORPTION_LIMIT_REACHED` và quay lại Owner, **không tự tạo task** (`DEC-041` J).

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

---

## 8. Phiên `S024` (2026-09-04) — `WP-C2` implementation ban đầu, budget KHÔNG đổi

    CAPABILITY      = CAP-WEBAPP        (lineage root WP-C1)
    TASK            = WP-C2             (READY -> IN_PROGRESS -> IMPLEMENTED)
    LOẠI            = INITIAL IMPLEMENTATION — KHÔNG tiêu repair cycle
    BRANCH          = claude/wp-c2-execution-state-y4rraf   (tách từ origin/main 2189a8f)

`WP-C2` **chưa từng `DONE`**, nên chưa có repair cycle nào để mở — cùng quy ước đã áp dụng
cho `WP-A4` (`DEC-016`/`DEC-017`), `T-09A` (`DEC-018`), `T-09B` (`DEC-019`) và `WP-B1`
(`DEC-034`). Ba con số dưới đây **không được đọc lại như thể vừa được cấp mới**: `USED = 0`
vì `CAP-WEBAPP` chưa tiêu chu kỳ sửa nào, không phải vì phiên này đặt lại.

    ALLOWED BUDGET            = 2 repair cycle     (Owner-ratified, `DEC-018`/`OD-WEBAPP-01`)
    CURRENT BUDGET USED       = 0 repair cycle
    CURRENT BUDGET REMAINING  = 2 repair cycle
    OWNER_EXTENSION           = KHÔNG CẦN

Delivery change budget — đo trực tiếp bằng lệnh chuẩn của `PRODUCTION_PATHS.md` §1, không
cộng tay từ báo cáo:

    git diff --shortstat 2189a8f -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 1 file changed, 128 insertions(+)

Một file production, **thuần thêm mới** (`−0`). `webapp/engine.js` và `webapp/app_logic.js`
= 0 dòng đổi, nên phiên này KHÔNG mở rộng bề mặt trôi parity của `RSK-002`. `pyproject.toml`
/ `pyproject.lock` = 0 dòng đổi, nên `dependency_lock_hash` của run record không đổi.

**Bốn ngưỡng Absorption Limit** (`CAPABILITY_MODEL.md`) — không ngưỡng nào bị chạm:

| Ngưỡng | Điều kiện | Phiên này |
|---|---|---|
| A | Effective Risk tăng ≥ 1 mức do việc được hấp thụ | KHÔNG — không hấp thụ việc nào; Effective Risk `CAP-WEBAPP` giữ HIGH |
| B | > 3 hạng mục mới hấp thụ vào một task baseline đã duyệt | KHÔNG — 0 hạng mục hấp thụ |
| C | Số REQUIRED check tăng > 50 % | KHÔNG — vẫn đúng 8, gate FROZEN không đổi một chữ |
| D | Việc ngoài Vertical Slice bị kéo lên đường găng | KHÔNG — không mở việc nào ngoài phạm vi đóng băng |

Số task ID mới do phiên này tạo = **0**. Không finding nào được chuyển thành task
(`REVIEW_PROTOCOL.md` § "A Finding Is Not A Task"). Hai quan sát non-blocking của phiên được
route vào `PROJECT/HARDENING_BACKLOG.md` (`H-34`, `H-35`) kèm `RE_TRIGGER_CONDITION`.

`GOLDEN_BASELINE_SHA` vẫn `PENDING_OWNER_DATA / MIGRATION_REQUIRED` (`H-10` chưa đóng), nên
budget tầng B vẫn chưa khai được — phiên này KHÔNG chọn một SHA tiện lợi để gọi là Golden.

---

## 9. Phiên Lifecycle Closure (2026-09-04, `DEC-036`) — budget KHÔNG đổi

`WP-C2: IMPLEMENTED → DONE`, Owner-authorized. Phiên này **thuần state/docs** — không sửa một
dòng production nào (`git diff --shortstat` trên bốn production path = rỗng cho lượt commit này).
Do đó:

    ALLOWED BUDGET            = 2 repair cycle     (không đổi)
    CURRENT BUDGET USED       = 0 repair cycle     (không đổi)
    CURRENT BUDGET REMAINING  = 2 repair cycle     (không đổi)

Không rà soát độc lập (E2) nào được tiêu — Completion Gate của `WP-C2` không đòi E2; quyết định
dựa trên báo cáo implementer đã có (`docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md`), không phải
một vòng review mới. Chi tiết quyết định: `PROJECT/PROJECT_DECISIONS.md` `DEC-036`.
