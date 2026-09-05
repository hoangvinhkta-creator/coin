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

## 1. Vertical Acceptance Slice

Lát cắt **ACTIVE** là §1.A (sản phẩm L-1). Lát cắt V2.1.5 ở §1.B là **HISTORICAL / CLOSED** —
giữ nguyên bản ghi, không xoá. Thay thế này do `DEC-041` mục C thực hiện.

Câu hỏi định tuyến số 1 của `governance/v4/CORE/CAPABILITY_MODEL.md`
(*"Is it required for the current Vertical Acceptance Slice to run correctly?"*) từ nay được
chấm **trên §1.A**, KHÔNG phải trên lát cắt validation V2.1.5 đã hoàn tất ở §1.B.

---

### 1.A — LÁT CẮT ACTIVE: sản phẩm CoinDCA L-1 (`DEC-041` C)

    Ngân sách tháng do người dùng đặt
      -> lịch mua đã lên kế hoạch
        -> người dùng ghi một giao dịch thật (có NGÀY do người dùng nhập)
          -> sổ cái + giá vốn tính lại từ (số dư đầu kỳ + toàn bộ trades)
            -> 4 con số dashboard (ngân sách · đã đầu tư · còn lại · ngày mua kế tiếp)
              -> lưu bền qua reload/restart

Lát cắt này cắt ngang module (UI → lớp ghi sổ → persistence), đúng định nghĩa Vertical Slice:
không module nào tự chứng minh được nó.

Trạng thái lát cắt: **CHƯA CHẠY.** Sản phẩm L-1 chưa được đặc tả — pha kế tiếp là
`L-1 PRODUCT + ACCOUNTING SPEC` (`DEC-041` Consequence). Không phiên nào được thi hành L-1
trước khi spec đó tồn tại.

    END_TO_END_ACCEPTANCE = PENDING_OWNER_DATA

    MISSING_DATA:
      ngân sách tháng · ngày lịch DCA · số dư đầu kỳ (crypto đang có, USDT sẵn, giá vốn cũ,
      asOf) · ít nhất một giao dịch đủ trường (ngày, USDT, price, fee, vndRate) · MỘT con số
      giá vốn trung bình kỳ vọng để làm oracle
    REQUIRED_SOURCE:
      spec L-1 định nghĩa các trường này bằng **ví dụ tổng hợp (synthetic)**
    OWNER_INPUT_REQUIRED:
      KHÔNG cần trong pha chuyển tiếp này (`DEC-041` C — Owner amendment)

**Quy tắc riêng tư/dữ liệu (`DEC-041` C, BẮT BUỘC).** KHÔNG commit dữ liệu tài chính thật của
Owner vào repo: ngân sách tháng thật, số dư đầu kỳ thật, lịch sử giao dịch thật, số dư tài khoản
riêng tư, oracle giá vốn cá nhân thật. Toạ độ nghiệp vụ mà `CAPABILITY_MODEL.md` §II.1 đòi được
thoả bằng **ví dụ tổng hợp**; kiểm chứng bằng dữ liệu thật chạy trên input cục bộ/riêng tư hoặc
fixture đã làm sạch. Đây là lý do `PENDING_OWNER_DATA` ở trên là outcome **hợp lệ** theo
`CAPABILITY_MODEL.md` §II.2 và không được "làm đầy" bằng dữ liệu bịa.

---

### 1.B — LÁT CẮT HISTORICAL / CLOSED: validation V2.1.5 (giữ nguyên, không xoá)

    Dữ liệu thật (Binance)
      -> fetch/lineage có nguồn gốc chứng minh được
        -> dataset đủ tư cách official
          -> pipeline chạy đủ 18 bước với ngữ nghĩa dữ liệu đúng
            -> Gate 1 / Gate 2 / Gate 3 + benchmark + control
              -> run record tự chứng minh nguồn gốc và tái lập được
                -> VERDICT

Đây là lát cắt mà `T-06` (official run) hiện thực hoá. Nó cắt ngang mọi module — đúng định
nghĩa Vertical Slice: không module nào tự chứng minh được nó.

**Trạng thái thẩm quyền từ `DEC-041` A/C: HISTORICAL / CLOSED.** Lát cắt này KHÔNG còn là lát
cắt chấm định tuyến; nó vẫn là authority cho câu hỏi *"V2.1.5 đã được đặc tả và chạy như thế
nào"*. `docs/spec/*_V2_1_5.md` và `src/eth_dca_os/**` = **frozen historical research authority**:
vẫn trích dẫn được, KHÔNG còn là spec sản phẩm, KHÔNG được sửa (Master Index §6), KHÔNG được kế
thừa trạng thái validation. Khiếm khuyết đặc tả đã biết `S-001`/`S-002`/`S-003` (đầu ra dự kiến
của `WP-D2`, nay `CANCELLED`) được **ghi chú kèm** freeze, không được sửa.
Giữ nguyên vĩnh viễn: `V2.1.5 validation = FAILED`; `verdict = DO_NOT_BUILD`;
`can_proceed_to_app = false`; official artifact `T-06`.

Trạng thái chạy (lịch sử): **ĐÃ CHẠY ĐÚNG MỘT LẦN — `T-06`, DONE tại `DEC-031` (2026-09-03).** Kết
quả đầu-cuối = verdict **`DO_NOT_BUILD`** (Gate 1 FAIL, OOS hard condition FAIL),
`can_proceed_to_app=false`. Đây là historical governance disposition (Owner chấp nhận
execution như một historical exception, KHÔNG tạo Ready/Completion Gate hậu nghiệm) — KHÔNG
có nghĩa capability nào PASS hay production-ready. Chi tiết:
`docs/T06_OFFICIAL_EVIDENCE_RECORD.md`, `PROJECT/PROJECT_DECISIONS.md` `DEC-031`.

Hai nhóm điều kiện ĐỘC LẬP từng chặn lát cắt nay ĐỀU đã thoả:
- (A) nội tại — `GATE-A` = WP-A1 ∧ WP-A2 ∧ WP-A3 ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 đều DONE —
  CLOSED tại `DEC-028` (`T-05` KHÔNG phải điều kiện, xác nhận `DEC-029`/`DEC-030`);
- (B) hạ tầng — `BLK-001` — RESOLVED tại `DEC-031`.

Vì `T-06` bị cấm chạy lại (Master Index §6), lát cắt này **KHÔNG** trở thành một Golden trace
tái lập được cho mục đích giảm Blast Radius trong tương lai (`RISK_MODEL.md` § Golden
Reduction đòi một test tái chạy được). Hệ quả cho Production Reachability: reachability đã
được chứng minh MỘT LẦN trên dữ liệu thật cho lát cắt end-to-end, nhưng **chưa có Golden
trace tái lập được** cho bất kỳ capability riêng lẻ nào. Mọi bằng chứng reachability cấp
module hiện tại vẫn dừng ở mức "đường thực thi ngoài ranh giới module" trong môi trường
synthetic/stub, chứ không phải Golden. Đây là giới hạn thật, phải được nói rõ, không được
coi là đã thoả.

---

## 2. Bảng capability

**Ghi chú `DEC-041` (2026-09-05).** Sau khi lát cắt ACTIVE chuyển sang L-1 (§1.A), các capability
thuộc bộ máy validation V2.1.5 — `CAP-PROV`, `CAP-DATA`, `CAP-ENGINE`, `CAP-PIPELINE`,
`CAP-MEASURE`, `CAP-ORDER`, `CAP-VERDICT` — chuyển sang **FROZEN RESEARCH (lịch sử đóng)**: giữ
nguyên trạng thái `DONE`, giữ nguyên mọi con số budget, KHÔNG reset, KHÔNG đụng lại
(`AGENTS.md` §3 *"Budget does not reset"*). Chúng không còn nằm trên lát cắt định tuyến.

`CAP-WEBAPP` là **lineage còn sống** và là lineage root tự nhiên của công việc L-1
(allowed 2 / used 0 / remaining 2, Effective Risk `HIGH` — `REVIEW_BUDGET_LEDGER.md` §2.2, không
đổi). Hai thành viên `WP-C3` và `WP-C4` nay `CANCELLED` (`DEC-041` F).
`CAP-SPEC` (`WP-D2`) đóng cùng V2.1.5.

**Báo trước `ABSORPTION_LIMIT` (`DEC-041` J):** công việc L-1 dưới `CAP-WEBAPP` nhiều khả năng
chạm ngưỡng B và D của `CAPABILITY_MODEL.md`. Khi chạm: ghi `ABSORPTION_LIMIT_REACHED` và quay
lại Owner Decision — **không tự tạo task**.

| Capability | Tên | Lineage root | Owner task hiện hành | Trạng thái | Nằm trên Vertical Slice? |
|---|---|---|---|---|---|
| `CAP-PROV` | Nguồn gốc & khả năng tái lập của official run | `WP-A1` | `WP-A1` | DONE — CHECK-A1-11 PASS/E2 vòng BỐN, Owner xác nhận `DEC-028` (2026-09-03) | Đã thoả (GATE-A CLOSED) |
| `CAP-DATA` | Ngữ nghĩa dữ liệu thiếu/hỏng (gồm độ phủ theo khoảng được yêu cầu, và ngữ nghĩa cửa sổ indicator daily theo ngày lịch) | `WP-A4` | `WP-A4` | DONE — 10/10 REQUIRED check PASS tại S010 sau REPAIR CYCLE #1 | CÓ (đường găng) |
| `CAP-ENGINE` | Vòng đời regime & ladder, kế toán vốn | `WP-A3` | `WP-A3` (DONE), `WP-A7` (DONE) | DONE | CÓ |
| `CAP-PIPELINE` | Đấu nối hạng mục bắt buộc vào pipeline | `WP-A2` | `WP-A2` | DONE | CÓ |
| `CAP-MEASURE` | Đo Failure Signal | `WP-A5` | `WP-A5` | DONE tại S015 — 9/9 REQUIRED PASS (E1), chủ dự án phê chuẩn | CÓ |
| `CAP-ORDER` | Thứ tự 18 bước tính toán | `WP-A6` | `WP-A6` | DONE tại S014 — 8/8 REQUIRED PASS, CHECK-A6-08 (E2 độc lập) PASS | CÓ |
| `CAP-VERDICT` | Chính sách verdict, test đặc tả, audit trail | `WP-B1` | `WP-B1`, `WP-B2`, `WP-B3` | `WP-B1` **DONE** (`DEC-034`); `WP-B2` **DONE** (`DEC-038`, 2026-09-05 — Owner-authorized Lifecycle Closure, 10/10 REQUIRED PASS, 141 ca test mới, 0 dòng production bị sửa, đóng `R-09` + danh sách "chưa có test" của `S001` thuộc BT §21); `WP-B3` **DONE** (`DEC-037`, 2026-09-05 — Owner-authorized Lifecycle Closure, 8/8 REQUIRED PASS, đóng `F-024`/`F-033`). **Toàn bộ lineage DONE** — `GATE-B = CLOSED` (`DEC-038`) | CÓ (lát cắt đã chạy — T-06 DONE) |
| `CAP-WEBAPP` | App web: sổ sách, trạng thái thực thi, parity JS/Python; **từ `DEC-041` gồm cả sổ cái tài chính CoinDCA L-1** | `WP-C1` | `WP-C1`, `WP-C2`, `WP-C3`, `WP-C4`, **`T-12` (IMPLEMENTED — S034; E2_REQUIRED, Ready Gate17/17)** | `WP-C1` DONE; `WP-C2` **DONE** (`DEC-036`, Owner-authorized Lifecycle Closure, 2026-09-04 — 8/8 REQUIRED PASS); `WP-C3` **CANCELLED** (`DEC-041` F — `NOT_APPLICABLE_TO_V2_1_5`; partial fill là khái niệm zone/ladder, không tồn tại dưới L-1. Ghi chú: `DEC-036` từng chuyển `READY` nhưng không được áp vào file task — stale `ST-09`, đóng tại `DEC-041` I); `WP-C4` **CANCELLED** (`DEC-041` F — `NOT_APPLICABLE_TO_V2_1_5`; phần dư parity OSCORE → `RE_TRIGGER_CONDITION` trong `HARDENING_BACKLOG.md`, không phải task) | **CÓ — lineage còn sống, lineage root của công việc L-1** (`DEC-041`) |
| `CAP-DEBT` | Nợ kỹ thuật không đổi hành vi | `WP-D1` | `WP-D1` | DONE | KHÔNG |
| `CAP-SPEC` | Đề xuất V2.2 cho khiếm khuyết đặc tả | `WP-D2` | `WP-D2` | **CANCELLED** (`DEC-041` F — `NOT_APPLICABLE_TO_V2_1_5`; `DEC-040` từ chối V2.2 và đòi giả thuyết tương lai không kế thừa V2.1.5. `S-001`/`S-002`/`S-003` được ghi chú kèm freeze `DEC-041` A) | KHÔNG — đóng cùng V2.1.5 |
| `CAP-GOVTOOL` | Validator & tooling governance | `MICRO-GOVDEF-001` | chưa có owner cho phần glob | READY một phần | KHÔNG |

### 2.1 `T-12` — thành viên mới của `CAP-WEBAPP` (2026-09-05, `S032`)

`T-12` (*Sổ cái L-1 v2: mô hình dữ liệu, `derive()` tất định, migration và test kế toán*,
`docs/tasks/T-12-so-cai-l1-v2-va-derive.md`) là bước **A** của
`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §24 và là hạng mục **đầu tiên** nằm trên lát
cắt ACTIVE §1.A.

Định tuyến theo `CAPABILITY_MODEL.md` § Capability-First Question Order, ghi lại để không phải
quyết lại:

1. *Cần cho lát cắt ACTIVE chạy đúng không?* — **CÓ.** §1.A đi qua "sổ cái + giá vốn tính lại từ
   (số dư đầu kỳ + toàn bộ trades)"; không có bước A thì lát cắt không chạy đúng được.
2. *Thuộc capability đã có không?* — **CÓ**, `CAP-WEBAPP` (`DEC-041` J đã chỉ định đây là lineage
   còn sống của công việc L-1). **Không** tạo capability mới, **không** tạo lineage root mới.
3. *Task/owner nào gần nhất?* — **không có task nào đang mở**: `WP-C1`, `T-09A`, `T-09B`, `WP-C2`
   đều `DONE`; `WP-C3`, `WP-C4` `CANCELLED` (`DEC-041` F).
4. *Hấp thụ vào owner đó có vượt Absorption Limit không?* — **hấp thụ không khả dụng**:
   `CAPABILITY_MODEL.md` §II.7 chỉ cho hấp thụ tự động vào task có scope baseline đã duyệt và
   **còn mở**; không có task nào như vậy trong `CAP-WEBAPP`.
5. *Đưa lên Owner.* — **đã có**: `DEC-042` § Consequence, *"Việc mở task ID cho bước A
   (Ledger/Data Model v2) thuộc một phiên riêng sau `DEC-042`"*.

`T-12` **không** phải sibling task tách ra để giải phóng budget: nó nằm **trong** capability đã
có, dùng chung pool của lineage root `WP-C1` và không đặt lại con số nào
(`REVIEW_BUDGET_LEDGER.md` §2.2). Số task ID mới do phiên `S032` tạo = **1**; số capability mới =
**0**; số lineage root mới = **0**; số proposal mới = **0**;
số `OWNER_ASSIGNMENT_REQUIRED` mới = **0**.

`END_TO_END_ACCEPTANCE` của §1.A vẫn `PENDING_OWNER_DATA` — **không đổi**. `T-12` được chấp nhận
bằng toạ độ nghiệp vụ **tổng hợp** (`SC-01`…`SC-12`, spec §19, có số cụ thể), đúng như `DEC-041`
C cho phép; `A-5` (`OWNER_LOCAL_ACCEPTANCE`, spec §22.1) vẫn nằm ngoài `T-12`.

**Amended `S033` (2026-09-05), Owner Decision `DEC-043`.** Owner duyệt ba tu chỉnh cho `T-12`:
phạm vi kiến trúc persistence bên trong `ethdca/state`; tách bạch `T12_GOLDEN_ACCOUNTING_BASELINE`
(tổng hợp) khỏi `GOLDEN_BASELINE_SHA` tầng dự án (`H-10`, lineage `T-06`, không thuộc
`CAP-WEBAPP`) và khỏi `OWNER_LOCAL_ACCEPTANCE`; pre-authorize một repair cycle có điều kiện, rút
từ pool `CAP-WEBAPP` hiện có (không cộng thêm budget). `T-12` giữ `READY`, giữ nguyên trong
`CAP-WEBAPP`. Chi tiết: `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`,
`PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.7, `PROJECT_DECISIONS.md` `DEC-043`.

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
| Ngữ nghĩa cửa sổ indicator daily (ngày lịch vs vị trí hàng) | `CAP-DATA` (WP-A4) — `DEC-015`/`DEC-016`, đóng tại S010 |
| Đơn vị/ngữ nghĩa còn để ngỏ của `ma200`/`adr30`/`rsi14`/`VR`/`ETHBTC_Percentile180` | `CAP-SPEC` (WP-D2) — phần dư SPEC_AMBIGUITY, KHÔNG bị chu kỳ sửa S010 quyết thay |
| Đối chiếu parity JS/Python của cùng công thức | `CAP-WEBAPP` (WP-C4) — nhận `F-S010-03` |

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

---

## 6. Cập nhật tại phiên Integration Recheck (2026-09-01) — `F-S009-01`

Nguồn thẩm quyền: `DEC-015`, và
`docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` PHẦN II.

Bảng §2 **KHÔNG đổi**: không capability nào được thêm, đổi tên hay đổi lineage root. Số task
ID mới = **0**.

### 6.1 Owner của `F-S009-01`

    F-S009-01 ("indicator daily tính theo VỊ TRÍ, không theo LỊCH")
      -> capability owner = CAP-DATA        (DEC-015, chủ dự án)
      -> OWNER_ASSIGNMENT_REQUIRED = ĐÓNG

Quyết định này KHÔNG mở ranh giới capability mới — nó rơi đúng vào một dòng ĐÃ có ở §3:

| Chủ đề | Capability sở hữu |
|---|---|
| Ngữ nghĩa DEGRADED / INVALID, nhãn gap trên bản ghi | `CAP-DATA` (WP-A4) |
| Ngữ nghĩa cửa sổ indicator daily (ngày lịch vs vị trí hàng) | `CAP-DATA` (WP-A4) — `DEC-015`/`DEC-016`, đóng tại S010 |
| Đơn vị/ngữ nghĩa còn để ngỏ của `ma200`/`adr30`/`rsi14`/`VR`/`ETHBTC_Percentile180` | `CAP-SPEC` (WP-D2) — phần dư SPEC_AMBIGUITY, KHÔNG bị chu kỳ sửa S010 quyết thay |
| Đối chiếu parity JS/Python của cùng công thức | `CAP-WEBAPP` (WP-C4) — nhận `F-S010-03` |

Bằng chứng cơ chế thu tại phiên này: `score.py::invalid_mask` chỉ đặt INVALID trên giá trị
**không hữu hạn**; cửa sổ theo vị trí luôn sinh số **hữu hạn nhưng sai**, nên nhánh
DEGRADED/INVALID của `CAP-DATA` không bao giờ kích hoạt. Đó là lý do finding thuộc `CAP-DATA`
chứ không phải một capability khác.

`CAP-SPEC` (`WP-D2`) giữ **phần dư** `SPEC_AMBIGUITY`: `ma200`, `adr30`, `rsi14`, `VR`,
`ethbtc_percentile180` được spec nêu bằng một con số không kèm đơn vị. Phần dư này KHÔNG mang
theo phần BLOCKING và KHÔNG đổi owner ở §6.1.

### 6.2 Absorption Limit — đo lại cho `F-S009-01` vào `WP-A4`

| Ngưỡng | Đo | Kết luận |
|---|---|---|
| **A** — Effective Risk +≥1 | `MAX(Local Risk 3, Blast Radius 2) = 3` → `MAX(3, 3) = 3`. Blast Radius riêng của finding = HIGH theo `RISK_MODEL.md`, nhưng Local Risk 3 đã trội nên Effective Risk **không đổi**. Golden Reduction không dùng được (chưa có Golden — `H-10`). | KHÔNG chạm ở B=3. Chạm nếu chủ dự án chấm B=4 — phiên này KHÔNG tự chọn con số |
| **B** — >3 mục hấp thụ | `F-E2A1R3-05` + `F-S009-01` = **2** | KHÔNG chạm |
| **C** — REQUIRED check +>50% | 9 → 10 = **+11,1%** | KHÔNG chạm |
| **D** — việc ngoài slice lên đường găng | `indicators.py` **nằm trên** vertical slice §1 | KHÔNG chạm |

    ABSORPTION_LIMIT_REACHED = KHÔNG

Khác với bảng §4 (nơi `F-E2A1R3-05` vào `WP-A1` chạm ngưỡng A và C), mục này **không** bị chặn
bởi Absorption Limit.

### 6.3 Điều thực sự đang chặn — khe thẩm quyền thi hành, không phải khe ownership

`CAP-DATA` ở **tầng capability** vẫn còn authority: `CAPABILITY_MODEL.md` định nghĩa capability
gồm *"a set of tasks that have implemented it over time"*, nên capability sống lâu hơn từng
task thành viên. `WP-A4` DONE không xoá `CAP-DATA`.

Ở **tầng task/thi hành** thì không, nếu không có một hành vi của chủ dự án. `CAP-DATA` chỉ có
đúng một thành viên là `WP-A4`, và ba rào sau đều do `STATE_AUTHORITY.md` dành riêng cho chủ
dự án:

1. Completion Gate của `WP-A4` đang FROZEN — *"FROZEN gates are immutable"*, *"Changing a gate
   … is an Owner action"*; mà `F-S009-01` không được phủ bởi check nào đang tồn tại nên đóng
   nó cần một REQUIRED check mới.
2. `WP-A4` = `DONE` — `DONE` do *"Owner, or a designated completion authority"* viết.
3. `indicators.py` ngoài Expected Touch Area của `WP-A4` → `SCOPE EXPANSION REQUIRED`.

```
OWNER_DECISION_REQUIRED
absorption_status = DEFERRED_UNTIL_WP-A4_REOPENED_BY_OWNER
```

Ba lựa chọn và khuyến nghị: `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` §II.7.
Phiên này KHÔNG tự mở lại `WP-A4`, KHÔNG tự sửa gate, KHÔNG tạo task ID.

---

## 7. Cập nhật tại phiên Owner Authority T-09B (2026-09-02) — `DEC-019`

Nguồn thẩm quyền: `DEC-019` (`OD-WEBAPP-02`), và
`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`.

Bảng §2 **KHÔNG đổi**: không capability nào được thêm, đổi tên hay đổi lineage root. Số task ID
mới = **0**. Giữ nguyên §2 theo đúng tiền lệ §5/§6 — bảng đó ghi lại trạng thái tại thời điểm
lập (2026-09-01), và các mục dưới đây là bản đính chính có ngày tháng, không phải viết đè.

### 7.1 `CAP-WEBAPP` — danh sách thành viên, đính chính

Ô "Owner task hiện hành" của `CAP-WEBAPP` ở §2 ghi `WP-C1`, `WP-C2`, `WP-C3`, `WP-C4`. Đúng tại
2026-09-01, lạc hậu từ 2026-09-02. Danh sách đầy đủ tính đến hôm nay:

| Task | Trạng thái | Ghi chú |
|---|---|---|
| `WP-C1` | DONE (2026-09-02) | Lineage root |
| `T-09A` | DONE (2026-09-02, `DEC-018`) | Vá V-01/V-02 |
| `T-09B` | **PLANNED** | Lưu trữ bền trên Firebase (`DEC-019`) — task này |
| `WP-C2` | **DONE** (`DEC-036`, 2026-09-04) | Owner-authorized Lifecycle Closure — 8/8 REQUIRED PASS, bất biến backtest bit-for-bit. `DEC-005` nghĩa rộng vẫn PENDING (không liên quan) |
| `WP-C3` | **READY** (`DEC-036`, 2026-09-04) | Dependency WP-C2 DONE nay thoả; chưa mở/thực thi |
| `WP-C4` | PLANNED | Sau WP-A3/A4/A6/A7 |

Cả `T-09A` và `T-09B` đều **đã tồn tại trong roadmap từ RCP-001 (2026-08-23)**. Chúng không phải
task tách ra để giải phóng budget — `GOVERNANCE_V4.md` §II.2, trục ngang.

### 7.2 `T-09B` — không chạm Absorption Limit

T-09B là một **thành viên đã có sẵn** của capability, không phải một mục được hấp thụ vào task
khác. Bốn ngưỡng của `CAPABILITY_MODEL.md` §Absorption Limit đo trên hành vi *hấp thụ*, nên
không áp dụng ở đây:

    ABSORPTION_LIMIT_REACHED = KHÔNG (không có hành vi hấp thụ nào diễn ra)

### 7.3 Ràng buộc kiến trúc gắn vào capability

`CAP-WEBAPP` nay mang một ràng buộc nền tảng do chủ dự án đặt: **persistence của app web dùng
Firebase** (`DEC-019` điểm 2). Ràng buộc này thuộc về capability, không thuộc về một task, nên
các task thành viên sau này (`WP-C2`, `WP-C3`) thừa hưởng nó và không được mở lại cuộc so sánh
provider mà không có Owner Decision mới.

`DEC-019` điểm 3 giới hạn phạm vi: chỉ thành phần Firebase tối thiểu cần cho durable
persistence. "Đã chọn Firebase" không mở cửa cho phần còn lại của hệ sinh thái.

### 7.4 Khe thẩm quyền còn mở

    OWNER_DECISION_REQUIRED
    OD-A  — runtime host của app web (CHẶN T-09B PLANNED -> READY)
    OD-B  — thành phần Firebase: Cloud Firestore vs Realtime Database
    OD-B2 — danh tính tối thiểu cho security rules

Chi tiết, bằng chứng và khuyến nghị: `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`
§ OWNER_DECISION_REQUIRED, và `DEC-019` mục "Hệ quả phát sinh ngay tại phiên chuẩn bị".

Đây là khe thẩm quyền **thi hành**, giống hình thái §6.3: capability có authority, nhưng ba rào
(host, component, danh tính) đều do `STATE_AUTHORITY.md` dành cho chủ dự án. Phiên này KHÔNG tự
chọn host, KHÔNG tự chọn component, KHÔNG tạo task ID, KHÔNG sửa production code.

---

## 8. Cập nhật tại phiên Owner Decision `DEC-020` (2026-09-02) — OD-A/OD-B/OD-B2 resolved, khe mới OD-C

Bảng §2 **KHÔNG đổi**. Số task ID mới = **0**. Không capability mới, không lineage mới.

### 8.1 T-09B — ba quyết định trong §7.4 nay RESOLVED

    OD-A  = Firebase Hosting     (RESOLVED, DEC-020)
    OD-B  = Cloud Firestore      (RESOLVED, DEC-020)
    OD-B2 = Firebase Anonymous Auth, một owner UID   (RESOLVED, DEC-020)

Ràng buộc kiến trúc của `CAP-WEBAPP` (§7.3) nay cụ thể hơn:

    Browser -> Firebase Hosting -> Firebase Authentication -> Cloud Firestore -> durable state

### 8.2 Khe thẩm quyền mới — `OD-C` (recovery semantics)

Đánh giá lại Ready Gate sau khi ba quyết định trên được duyệt phát hiện một câu hỏi độc lập mà
`OD-B2` không tự trả lời: danh tính Anonymous Auth có sống sót qua "đổi máy" không.

    OWNER_DECISION_REQUIRED
    OD-C — Anonymous Auth session gắn với IndexedDB của MỘT browser profile. Kịch bản cửa sổ
           riêng tư / đổi máy / đổi trình duyệt (đều được RSK-001 nêu tên) sinh UID mới, bị
           Firestore rules (khoá một UID cố định) từ chối đọc/ghi dữ liệu đã có.

Đây KHÔNG phải absorption — không có hành vi hấp thụ nào, không chạm ngưỡng nào của Absorption
Limit. Đây là một Owner Decision còn thiếu ở tầng thi hành, cùng hình thái §6.3/§7.4: capability
có authority, nhưng quyết định cụ thể dành cho chủ dự án theo `STATE_AUTHORITY.md`.

Chi tiết, bằng chứng, hai phương án (R1/R2): `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`
§ OD-C, và `DEC-020` mục (5).

### 8.3 Trạng thái T-09B sau phiên này

    T-09B = PLANNED (không đổi). Ready Gate 14/15 dòng ✅ (đếm cả dòng "+"); chỉ OD-C còn chặn.
    Completion Gate 16/16 REQUIRED vẫn FINALIZED, KHÔNG sửa yếu, CHƯA frozen.
    CAP-WEBAPP budget KHÔNG đổi: 2/0/2. Không mở repair cycle. Không chuyển IN_PROGRESS.

---

## 9. Cập nhật tại phiên Owner Decision `DEC-021` (2026-09-02) — Personal Tool Simplification Principle; `OD-C` đóng = R2

Bảng §2 **KHÔNG đổi**. Số task ID mới = **0**.

### 9.1 `OD-C` (§8.2) — RESOLVED = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)

Chủ dự án chọn **không** thêm recovery credential; cross-device/cross-browser/lost-identity
recovery = **OUT OF SCOPE V1** (`PROJECT/HARDENING_BACKLOG.md` **H-23**). Đây là Owner Scope
Decision dựa trên một nguyên tắc sản phẩm mới — **Personal Tool Simplification Principle**
(`DEC-021`, khai triển từ `DEC-011`/`DEC-019`) — KHÔNG phải phủ nhận bằng chứng kỹ thuật đã ghi
tại §8.2 (Anonymous UID mới sau đổi máy vẫn thật sự bị Firestore rules từ chối).

### 9.2 T-09B: `PLANNED → READY`

Ready Gate đánh giá lại đầy đủ (14 điều kiện riêng + 17 dòng MAJOR Ready Gate chuẩn), không
auto-PASS: **15/15 ĐẠT.** Completion Gate 16/16 REQUIRED **FROZEN**. Không còn Owner Decision
hay architecture ambiguity nào chặn `CAP-WEBAPP` ở nhánh `T-09B`.

    T-09B: PLANNED -> READY   (STATE_AUTHORITY.md: READY do Implementer/Owner viết —
                                 chỉ thị phiên §18 uỷ quyền tường minh chuyển trạng thái này)

### 9.3 Ranh giới capability không đổi

`CAP-WEBAPP` budget vẫn 2/0/2 — chuyển `READY` là chuẩn bị, không phải implementation, không
tiêu repair cycle. `T-09B` implementation sau này vẫn là **INITIAL IMPLEMENTATION** khi bắt
đầu (đúng quy ước `WP-A4`/`T-09A`).

---

## 10. Cập nhật tại phiên thực thi T-09B — S014 (2026-09-02): `READY → IN_PROGRESS → IMPLEMENTED`

Bảng §2 **KHÔNG đổi** (owner task hiện hành, lineage root `WP-C1`). Số task ID mới = **0**.

### 10.1 `T-09B` đã được thực thi đúng baseline FROZEN

Ràng buộc kiến trúc của `CAP-WEBAPP` (§7.3, §8.1) nay là **mã đang chạy**: Firebase Hosting →
Firebase Anonymous Auth (một owner UID trong `firestore.rules`) → Cloud Firestore
(`ethdca/state` + `ethdca/seed`); `localStorage` = mirror/cache. Không thêm thành phần Firebase nào
ngoài ba thành phần đã duyệt; không provider abstraction; không login UI; không cross-device
recovery (`H-23` giữ nguyên).

    T-09B: READY -> IN_PROGRESS -> IMPLEMENTED   (STATE_AUTHORITY.md: IN_PROGRESS/READY_FOR_REVIEW
                                                  do Implementer viết; DONE thuộc chủ dự án)
    Completion Gate: 16/16 REQUIRED PASS (E1, Firebase Emulator Suite) — câu chữ gate KHÔNG đổi
    Batch review: PASS, CONFIRMED BLOCKING = 0, HARDENING mới = 4 (H-29..H-32)
    Production reachability trên project Firebase THẬT: NOT_TESTED (chủ dự án chưa tạo project)

### 10.2 Ranh giới capability không đổi

`CAP-WEBAPP` budget vẫn **2/0/2**: lượt này là INITIAL IMPLEMENTATION (quy ước `WP-A4`/`T-09A`),
không tiêu repair cycle. Finding hai-tab-stale-overwrite phát hiện trong chính phiên và sửa TRƯỚC
commit implementation → cùng lượt, không mở chu kỳ (`REVIEW_PROTOCOL.md` § same cycle).

`H-32` (ba file runtime mới `webapp/firebase_config.js`, `firestore.rules`, `firebase.json` chưa
được khai trong `PROJECT/PRODUCTION_PATHS.md` §1) thuộc `CAP-GOVTOOL` — cùng khe owner với `H-08`,
`H-09`, `H-21`, `H-22`; phiên này không tự khai production path (giá trị PROJECT do chủ dự án đặt).

## 11. Cập nhật tại phiên Owner Confirmation `DEC-024` (2026-09-03): `T-09B` → `DONE`

Bảng §2 **KHÔNG đổi**. Số task ID mới = **0**.

Production reachability trên project Firebase thật đóng bằng evidence E1
(CHECK-T09B-01/02/03/04/14 trên `https://tinphatcontent.web.app`, Owner tự báo cáo —
`docs/reviews/T-09B-production-verification.md`). Chủ dự án xác nhận `DEC-024`:

    T-09B: IMPLEMENTED -> DONE   (STATE_AUTHORITY.md: DONE do Owner/completion authority viết)
    Completion Gate: 16/16 REQUIRED PASS — câu chữ gate KHÔNG đổi
    CAP-WEBAPP budget: 2/0/2 KHÔNG đổi — toàn chuỗi phiên vẫn là INITIAL IMPLEMENTATION

`RSK-001`: chủ dự án ghi nhận phần V1 durable persistence đã kiểm chứng trên production;
`H-23` (cross-device/lost-identity) vẫn HARDENING/OUT OF SCOPE V1 theo `DEC-021`, không đổi.

## 12. S034 — T-12 dừng trước implementation (2026-09-05)

`T-12: READY → BLOCKED`, `OWNER_DECISION_REQUIRED`: SC-04 mâu thuẫn với §11.2/§11.4 của spec L-1.
Bằng chứng: `docs/reviews/T12-IMPLEMENTATION-REPORT.md` §3/§29. Không đổi capability/lineage;
không task ID mới; pool `CAP-WEBAPP` giữ 2/0/2. Chưa có fixture hay golden accounting baseline.

**Tiếp nối S034, DEC-044:** xung đột carry SC-04 ở đoạn trên đã đóng bằng sửa oracle 11.775.522.
Preflight đủ 12 SC còn hai nhóm (SC04 WAC exact vs ROUND_VND; SC09/10 carryOut tháng đang mở),
nên T-12 giữ BLOCKED — OWNER_DECISION_REQUIRED. Xem phần bổ sung báo cáo T12.
Không implementation, không task/capability/lineage mới, budget giữ 2/0/2.

## 13. S034 tiếp nối DEC-045 — implementation L-1

Ready Gate đánh giá duy nhất17/17; BLOCKED→READY→IN_PROGRESS. Golden frozen tại
`c610a299ed6b66dea3cd63372a0943967c93e95d`; repair cycle1 DEC-043 tại`2a2ab3f`,
CAP-WEBAPP2/1/1. SC12/12, INV15/15, mutation7/7, P1…P6 PASS E1. Full Python regression
678/678 PASS; T-12 IN_PROGRESS → IMPLEMENTED; E2 độc lập REQUIRED. Không task/capability mới, không reset WP-C1.
