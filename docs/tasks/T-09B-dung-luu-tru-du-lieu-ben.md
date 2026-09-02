# T-09B — Dựng lưu trữ dữ liệu bền (Firebase)

## Metadata

Status:
IMPLEMENTED (phiên thực thi S014, 2026-09-02, branch `claude/t09b-firebase-implementation-nz50is`:
`READY → IN_PROGRESS` khi bắt đầu code, `IN_PROGRESS → IMPLEMENTED` khi 16/16 REQUIRED check
PASS ở mức E1 trên Firebase Emulator Suite và batch review PASS. **Chưa `DONE`**: chuyển `DONE`
là hành vi của chủ dự án (`STATE_AUTHORITY.md`), và production reachability trên project Firebase
THẬT chưa được kiểm — chủ dự án chưa tạo project; xem mục "Thực thi — S014" bên dưới.)

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION

Completion Gate Freeze:
**FROZEN — 2026-09-02, tại phiên `DEC-021`.** T-04/S002 chỉ đóng băng gate cho 15 work package;
T-09B không nằm trong 15 gói đó, nên gate của task này được finalize và freeze qua đúng quy
trình `TASK_COMPLETION_GATE_STANDARD.md` mục "Gate Creation Timing" ("Before Task Becomes
READY — review and finalize" → freeze tại `PLANNED → READY`). 16 REQUIRED check giữ nguyên số
lượng; `CHECK-T09B-04` được tái phạm vi MỘT LẦN, trước khi freeze, bằng audit trail tường minh
(OLD REQUIREMENT → OWNER PRODUCT INTENT CHANGE → NEW V1 REQUIREMENT, xem chi tiết tại chính
check đó) theo Owner Scope Decision `DEC-021` — đây KHÔNG phải sửa yếu gate sau khi freeze, mà
là bước finalize hợp lệ trước khi freeze. Từ đây, mọi thay đổi khác phải qua
`COMPLETION GATE CHANGE PROPOSAL`.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 3
A: 3
X: 3
U: 3
V: 3
H: 3
C: 3
F: 3

Routing Categories:
accounting_financial
material_sensitive_data_corruption

Primary Agent Tier:
D

Primary Effort:
xhigh

Model Routing Score:
3.0

Effort Routing Score:
3.0

Applied Model Floor:
cognitive:A>=3&X>=3
safety_business:min_C

Applied Effort Floor:
safety_business:min_high
critical:min_xhigh

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Difficulty:
3/4

Risk:
3/4

Blast Radius:
3/4

Effective Risk:
HIGH — `Effective Risk = MAX(Local Risk 3, Blast Radius 3) = 3` (`RISK_MODEL.md`). Blast Radius
chấm theo đường dữ liệu, không theo tên module: một lớp lưu trữ hỏng làm sai **toàn bộ** sổ tài
chính (Purchase History, holdings, giá vốn, pool kế toán), rơi thẳng vào "wrong money …
settlement" của `RISK_MODEL.md` § Blast Radius — HIGH. Golden Reduction KHÔNG dùng được (chưa có
Golden baseline canonical — `HARDENING_BACKLOG.md` H-10). Hệ quả: E1 bắt buộc cho mọi REQUIRED
check kiểm chứng được, và **bắt buộc batch review cuối phiên thực thi**. HIGH đặt độ sâu review,
KHÔNG phải hard-stop.

Project Profile:
PRODUCT

Capability:
`CAP-WEBAPP`

Lineage root:
`WP-C1`

## Ghi chú thẩm quyền (đọc trước khi đọc phần còn lại)

T-09B **đã được đăng ký từ trước** trong vùng registry chính thức của
`PROJECT/PROJECT_PROGRESS.md` (bảng Overall Roadmap, trạng thái `PLANNED`, từ RCP-001
2026-08-23) — đó là hình thức đăng ký thứ nhất theo `CAPABILITY_MODEL.md` §II.5. File này là
hình thức thứ hai (Task Spec) cho **cùng một ID đã tồn tại**.

    Task ID mới được tạo bởi file này = 0

`GOVERNANCE_V4.md` §II.5 cho một task bốn artifact mặc định: SPEC/TASK, PROGRESS/STATE, REVIEW,
DECISIONS dùng chung. File này là artifact SPEC/TASK — nằm trong hạn mức, không cần phê duyệt
artifact thứ năm.

Budget đọc từ `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2, **KHÔNG khai lại tại đây**. Phiên này
KHÔNG mở repair cycle: implementation T-09B sau này là **INITIAL IMPLEMENTATION**, cùng quy ước
đã dùng cho `WP-A4` (`DEC-016`/`DEC-017`) và `T-09A` (`DEC-018`).

Ràng buộc kiến trúc **Firebase** là FIXED OWNER CONSTRAINT — ghi tại
`PROJECT/PROJECT_DECISIONS.md` `DEC-019` (`OD-WEBAPP-02`). File này KHÔNG so sánh Firebase với
Supabase / SQLite / PostgreSQL / Cloudflare D1 / JSON Server hay bất kỳ provider nào khác, và
KHÔNG có thẩm quyền đổi quyết định đó.

`OD-A` (runtime host), `OD-B` (thành phần Firebase), `OD-B2` (danh tính) đã được chủ dự án
giải quyết tại `DEC-020` (`OD-WEBAPP-03`, 2026-09-02): Firebase Hosting · Cloud Firestore ·
Firebase Anonymous Auth. `DEC-020` mở một khe mới — `OD-C` (recovery semantics) — được chủ dự
án đóng ngay sau đó tại `DEC-021` (`OD-WEBAPP-04`, cùng ngày): **R2 — SIMPLIFIED
PERSONAL-TOOL RECOVERY**, một phần của **Personal Tool Simplification Principle** áp dụng cho
toàn bộ sản phẩm. Ready Gate nay ĐẠT 15/15; Completion Gate đã **FROZEN**; `T-09B: PLANNED →
READY`. Xem mục OD-C bên dưới cho chi tiết, và `CHECK-T09B-04` (mục Completion Gate) cho audit
trail đầy đủ.

---

## Objective

Làm cho state thật của app web **bền độc lập với trình duyệt**: mở app lên là dùng được, đóng
rồi mở lại vẫn tiếp tục được, và mất `localStorage` không đồng nghĩa mất sổ.

Nền tảng persistence: **Firebase** (`DEC-019`). Chỉ dùng thành phần tối thiểu cần cho durable
persistence — không kéo theo phần còn lại của hệ sinh thái.

Đây là mục **DATA PERSISTENCE** trong V1 PRIORITY RULE của `DEC-011`, và là biện pháp giảm thiểu
đã được chỉ định cho `RSK-001` từ S000.

## Vấn đề đang phải giải (thẩm quyền: RSK-001, S001, WP-C1)

App hiện lưu state ở hai chỗ, **không chỗ nào là durable source độc lập**:

| Cơ chế hiện có | Vị trí | Vì sao chưa đủ |
|---|---|---|
| `localStorage` mirror | `app_logic.js:46-59`, `825`, `994`, `1051` | Xoá dữ liệu site, cửa sổ riêng tư, đổi máy, đổi trình duyệt → mất |
| Tự xuất bản lại trang (quine) | `app_logic.js:838-889`, `build_app.js` | State nằm **trong chính file HTML**; publish thất bại → không có bản bền nào mới |

`RSK-001` (mức: cao) ghi nguyên văn: *"Đây không phải 'một database' như Implementation Plan §9
yêu cầu."* Giảm thiểu được chỉ định là T-09B.

---

## OD-A / OD-B / OD-B2 — RESOLVED (`DEC-020`, 2026-09-02)

    OD-A  = FIREBASE HOSTING
    OD-B  = CLOUD FIRESTORE  (document `ethdca/state` + `ethdca/seed`)
    OD-B2 = FIREBASE ANONYMOUS AUTH, rules khoá cứng một owner UID

Kiến trúc baseline sau khi cả ba được duyệt:

    Browser
       ↓
    Firebase Hosting
       ↓
    Firebase Authentication (Anonymous)
       ↓
    Cloud Firestore
       ↓
    durable state

`localStorage` / `sessionStorage` giữ nguyên vai trò mirror/cache — không đổi so với `DEC-019`.

Bằng chứng và lý do chấm từng quyết định được giữ nguyên bên dưới (đọc trước khi đọc `OD-C`).
Đây là **baseline đã APPROVED**, không phải hợp đồng bất biến: nếu implementation chứng minh
document size hoặc schema thực tế không đáp ứng được ở `OD-B`, KHÔNG silently redesign — báo
`ARCHITECTURE_CHANGE_REQUIRED` kèm evidence. KHÔNG đổi sang Realtime Database.

### OD-A (RESOLVED = FIREBASE HOSTING) — Runtime host của app web

**Đây không phải giới hạn của Firebase. Đây là giới hạn của nơi app đang chạy.**

Bằng chứng, dựng từ nguồn canonical 1 + 2 của `PRODUCTION_PATH_RULE.md` (production
schema/inventory hiện tại + repo config hiện tại), không phải suy đoán tương lai:

| # | Bằng chứng | Nguồn |
|---|---|---|
| 1 | *"Trang artifact chạy dưới CSP chặn mọi host ngoài (Google Fonts là ngoại lệ duy nhất)"* | `webapp/README.md:13` |
| 2 | *"CSP của trang artifact chặn mọi host ngoài trừ Google Fonts."* | `docs/reviews/S001-discovery-baseline.md:94-95` |
| 3 | Toàn bộ app chỉ có **đúng một** tham chiếu host ngoài, và đó là `fonts.googleapis.com` | `webapp/app_shell.html:2` (grep `http` trên cả file cho đúng 1 dòng) |
| 4 | Cơ chế "lưu lên đám mây" duy nhất hiện có là capability do host cấp (`window.claude.use("artifact")` / `("downloads")`), **không phải** lời gọi mạng | `webapp/app_logic.js:863`, `1022`, `1066` |
| 5 | Bản đã xuất bản đang được mở từ host artifact | `webapp/README.md:4` |

Hệ quả **trực tiếp và kiểm chứng được**: Firebase SDK cần gọi mạng tới endpoint của Firebase
lúc chạy (`firestore.googleapis.com` với Cloud Firestore, `*.firebasedatabase.app` với Realtime
Database). Dưới CSP nói trên, các lời gọi đó bị chặn. Vì vậy **Completion Gate A, B, C, D không
thể PASS chừng nào app còn chạy trên host hiện tại** — không phải vì Firebase sai, mà vì trang
không với tới được Firebase.

`PRODUCTION_PATH_RULE.md` § Forbidden Justification cấm dùng *"chuyện này có thể xảy ra trong
tương lai"* để nâng một finding lên BLOCKING. Mục này **không** dựa vào lập luận đó: CSP là cấu
hình đang có hiệu lực ngay bây giờ, và bốn gate A–D là REQUIRED của chính chủ dự án.

Ba lựa chọn đã được đưa ra, xếp theo thứ tự ưu tiên §11 của chỉ thị (correctness · usability ·
low operational burden · implementation simplicity · cost · technical elegance · scalability),
và chủ dự án đã **APPROVED phương án A1** tại `DEC-020`:

| | Phương án | Đánh giá |
|---|---|---|
| **A1** | **Firebase Hosting** — deploy `app_final.html` lên Firebase Hosting, mở bằng một URL cố định | **APPROVED (`DEC-020`).** Cùng hệ sinh thái đã chọn nên không phải quyết định provider lần hai; CSP do chính dự án đặt nên Firebase gọi được; usability đúng ý *"mở web lên là dùng được"* — một URL, không terminal cho việc dùng hằng ngày; free tier thừa cho một người dùng; `firebase deploy` chỉ chạy lúc **setup và khi đổi code**, không phải mỗi ngày |
| A2 | Mở `app_final.html` từ ổ đĩa (`file://`) | KHÔNG chọn. Origin của `file://` là `null`; Firebase Auth từ chối origin đó và Firestore/RTDB có thể chặn theo. Người dùng phải tự mang file qua từng máy, không có bản dùng chung |
| A3 | Giữ nguyên host artifact | KHÔNG chọn — bất khả thi với Firebase, chính là điều bằng chứng 1–5 chứng minh |

Chỉ thị §2 (phiên trước) nói không tự thêm `hosting migration` **nếu Completion Gate không
cần**. Ở đây gate A–D **cần**, nên đây không phải tự thêm mà là hệ quả trực tiếp của một
Completion Gate REQUIRED đã FINALIZED — và chủ dự án đã duyệt tại `DEC-020`. Không biến quyết
định này thành deployment-platform redesign; không thêm server riêng.

Hệ quả kèm theo, đã được biết trước khi duyệt:

- `window.claude.use("artifact")` (đường tự publish) và `window.claude.use("downloads")` (đường
  export JSON) là capability của host artifact; rời host thì mất. Đường publish **bị thay thế**
  bởi chính Firebase (đó là mục tiêu của T-09B). Đường export phải đổi sang tải file bằng
  `<a download>` chuẩn — thay đổi nhỏ, nằm trong Expected Touch Area.
- Cơ chế quine (`build_app.js` nhúng base64 của chính trang) không còn cần thiết cho persistence.
  Phiên thực thi **không** được tự ý gỡ nó ngoài phạm vi cần thiết.

### OD-B (RESOLVED = CLOUD FIRESTORE) — Thành phần Firebase

Chủ dự án đã **APPROVED Cloud Firestore** tại `DEC-020`, theo khuyến nghị dưới đây.

| Tiêu chí (thứ tự §11) | Cloud Firestore | Realtime Database |
|---|---|---|
| Correctness — xác nhận ghi bền | `await setDoc()` chỉ resolve khi server đã ack → "confirm durable write" của §4 map 1-1 | `await set()` cũng ack; tương đương |
| Correctness — kiểu dữ liệu | Số là double đúng như JS; map/array lồng một tầng (`ladders[].zones[]`) hợp lệ; `undefined` **ném lỗi** trừ khi bật `ignoreUndefinedProperties` → buộc phải chuẩn hoá state, tốt cho gate I | Cây JSON thuần; `undefined` và giá trị `null` **bị xoá âm thầm** → nguy hiểm cho `filled_vnd: 0` / `released_vnd` và cho gate I |
| Correctness — chống mất một phần | Ghi từng document; tách sổ kế toán khỏi seed | Ghi cả cây; dễ ghi đè nhầm nhánh |
| Usability / restore | Console đọc được từng document, xuất JSON được | Console xuất cả cây JSON, cũng dễ |
| Giới hạn phải thiết kế quanh | **1 MiB / document** — buộc tách `seed` (≈40 KB và tăng ~15 KB/năm) ra khỏi document sổ | Không có trần 1 MiB, nhưng cũng không ép tách nên dễ để state phình vào một nhánh |
| Operational burden | Rules + một document; không cần index cho truy vấn nào của T-09B | Rules + một cây |
| Cost | Tính theo thao tác đọc/ghi. Một người dùng, low-frequency → gần như chắc chắn nằm trong free tier | Tính theo GB lưu/tải. Cũng trong free tier |

**Cloud Firestore — APPROVED.** Hai lý do quyết định, cả hai thuộc trục *correctness* — trục
số 1 của §11:

1. Realtime Database **xoá âm thầm** khoá có giá trị `null`. State của app có những trường mà
   sự **tồn tại** của chúng mang ngữ nghĩa kế toán (`z.filled_vnd`, `z.released_vnd`,
   `L.month`, `trades[].recPrice`). Một cơ chế lưu trữ tự ý bỏ khoá là đúng thứ gate I
   ("serialize/deserialize không được làm đổi accounting semantics") cấm.
2. Trần 1 MiB/document của Firestore **ép** tách `seed` (dữ liệu tham chiếu tĩnh, tái sinh được
   bằng `ethdca export-live`) khỏi document sổ kế toán (dữ liệu tiền thật, không tái sinh được).
   Đó là ranh giới đúng, và Firestore biến nó thành ràng buộc của nền tảng thay vì một quy ước
   dễ bị vi phạm.

Cấu trúc tối thiểu đề xuất (KHÔNG phải một provider layer, KHÔNG phải generic repository —
§11 cấm cả hai):

    ethdca/state    <- document: toàn bộ accounting state (MUST_PERSIST tầng 1)
    ethdca/seed     <- document: seed lịch sử giá + config + parity (MUST_PERSIST tầng 2)

Hai document, ghi thẳng bằng Firebase SDK, không lớp trừu tượng ở giữa.

### OD-B2 (RESOLVED = FIREBASE ANONYMOUS AUTH, một owner UID) — Danh tính tối thiểu cho security rules

Firestore/RTDB security rules cần **một** danh tính, nếu không thì lựa chọn duy nhất còn lại là
cho phép ghi công khai — nghĩa là bất kỳ ai biết project ID đều sửa được sổ tiền. `DEC-011` điểm
10 nói security/multi-user không phải yêu cầu chấp nhận V1, nhưng nó **không** cho phép để sổ
tiền mở cho toàn Internet: đó rơi vào điểm C (*"mất hoặc làm hỏng lịch sử giao dịch thực tế"*)
của chính `DEC-011`.

Chủ dự án đã **APPROVED Firebase Anonymous Auth** tại `DEC-020`, rules khoá cứng vào đúng một
UID. Người dùng không phải đăng nhập; trình duyệt tự lấy UID và giữ lại. Mục đích duy nhất: cấp
danh tính tối thiểu cho rules — KHÔNG xây account system, login UI phức tạp, multi-user, roles,
permissions framework, social login, email/password login **cho việc dùng hằng ngày**. Security
boundary nằm ở Firebase Authentication + Firestore Rules; KHÔNG public read/write; Firebase
public client config KHÔNG tự động coi là secret; KHÔNG hard-code secret/private credential vào
source repo.

---

## OD-C (MỚI, CHẶN) — Recovery semantics: durable STATE khác với khả năng AUTHENTICATE lại làm owner

Phát hiện tại `DEC-020` khi đánh giá lại Ready Gate sau khi OD-A/OD-B/OD-B2 được duyệt. Đây
**không phải** vấn đề của Firestore — Firestore lưu đúng những gì được ghi. Đây là giới hạn của
**Anonymous Auth**, thành phần đã được duyệt ở `OD-B2` để giải quyết một câu hỏi khác (rules cần
một danh tính).

### Bằng chứng

Firebase Anonymous Auth lưu session (refresh token) trong `IndexedDB` của **đúng một browser
profile**. Ba trong bốn kịch bản mất dữ liệu mà chính `RSK-001` nêu tên nguyên văn — *"Xóa dữ
liệu site, dùng cửa sổ riêng tư, đổi máy, hoặc publish thất bại"* — sinh ra một `IndexedDB`
**trống**, tức một **anonymous UID hoàn toàn mới**:

| Kịch bản (từ `RSK-001`) | `IndexedDB` của Anonymous Auth | UID sau đó |
|---|---|---|
| Xoá `localStorage` + `sessionStorage` (không đụng `IndexedDB`) | Còn nguyên | **Cùng UID cũ** |
| Cửa sổ riêng tư (private window) | Trống (private mode không giữ `IndexedDB` qua phiên) | **UID mới** |
| Đổi máy | Không tồn tại trên máy mới | **UID mới** |
| Đổi trình duyệt | Không tồn tại ở trình duyệt khác | **UID mới** |

Nếu Firestore Security Rules khoá cứng vào MỘT UID cố định (đúng thiết kế `OD-B2` đã duyệt), một
UID mới bị rules **từ chối đọc/ghi** dữ liệu đã có — không phải vì Firestore mất dữ liệu, mà vì
trình duyệt/máy mới **không chứng minh được nó là owner**.

### Hệ quả lên hai REQUIRED check đã FINALIZED

| Check | Nhánh | Ảnh hưởng bởi Anonymous Auth? |
|---|---|---|
| `CHECK-T09B-03` — xoá `localStorage` + `sessionStorage` | Không đụng `IndexedDB` | **KHÔNG** — PASS được trung thực với thiết kế đã duyệt |
| `CHECK-T09B-04` — đóng/mở lại môi trường, **"một profile/cửa sổ khác"** | Sinh `IndexedDB` mới | **CÓ** — nhánh này KHÔNG PASS được trung thực với Anonymous Auth đơn thuần |

Ranh giới đúng như chỉ thị đặt tên trước: **(A) durable STATE persistence** đã được kiến trúc
Hosting + Firestore giải quyết; **(B) khả năng AUTHENTICATE làm owner sau khi mất local browser
identity** thì CHƯA. Không được tuyên bố "Firestore durable" = "chắc chắn recover được từ máy
mới" — và Task Spec này không tuyên bố như vậy.

### RESOLVED = R2 — SIMPLIFIED PERSONAL-TOOL RECOVERY (`DEC-021`, 2026-09-02)

| | Phương án | Kết quả |
|---|---|---|
| R1 | Link một recovery credential vào Anonymous UID | KHÔNG chọn — chủ dự án không muốn thêm bất kỳ credential nào cho V1, kể cả một credential chỉ dùng cho recovery |
| **R2** | Chấp nhận giới hạn, thu hẹp phạm vi "recover" của `CHECK-T09B-04` xuống same-browser-profile | **APPROVED.** Xem `DEC-021` §(5)-(6) |

Đây là **OWNER SCOPE DECISION dựa trên Personal Tool Simplification Principle**
(`DEC-021`), KHÔNG phải kết luận kỹ thuật rằng Anonymous Auth "đủ" theo nghĩa PASS. Khe kỹ
thuật ghi ở trên (Anonymous UID mới sau đổi máy/browser/cửa sổ riêng tư bị Firestore rules từ
chối) vẫn **ĐÚNG** và **KHÔNG bị phủ nhận** — điều thay đổi là phạm vi CHẤP NHẬN của V1, không
phải sự thật kỹ thuật. Cross-device/lost-identity recovery được ghi `OUT OF SCOPE V1` tại
`PROJECT/HARDENING_BACKLOG.md` **H-23**.

    T-09B: Ready Gate được đánh giá lại — xem mục Ready Gate bên dưới.
    Số task ID mới = 0 · Số production file bị sửa = 0

`CHECK-T09B-03` **KHÔNG đổi, KHÔNG bị làm yếu** — kịch bản đó không đụng `IndexedDB`, không
liên quan `OD-C`. `CHECK-T09B-04` được viết lại theo audit trail bắt buộc — xem mục Completion
Gate bên dưới.

---

## State Inventory

Đọc từ production state schema thật: `webapp/app_logic.js::emptyState()` (dòng 15-30),
`webapp/build_app.js` (`initialState`), `webapp/engine.js::buildLadder()`, và
`demo/results3/live_seed.json`. **Không suy diễn từ tài liệu.**

### MUST_PERSIST — tầng 1: sổ kế toán (mất = sai tiền)

| Trường | Kiểu | Vì sao bắt buộc bền |
|---|---|---|
| `schema` | `"ethdca.tracker/1"` | Nhận dạng bản ghi bền; thiếu thì không validate được |
| `rev` | number | Số hiệu bản; là căn cứ so sánh durable vs mirror (§3) |
| `months{}` | map `"YYYY-MM"` → `{contribution, base{a,r,d}, smart{a,r,d}, oppAdded, oppOverflow}` | **monthly budget** + **accounting pools** + **reserved/available/deployed** theo tháng. `a`=available, `r`=reserved, `d`=deployed |
| `oppFund{a,r,d}` | object | Opportunity Fund xuyên tháng — pool thứ ba, không nằm trong `months` |
| `treasury{vnd, usdt}` | object | Kho tiền thật chưa chuyển thành ETH |
| `eth` | number | **holdings** |
| `costUsdt` | number | Cơ sở tính **average cost** (USDT) |
| `costVnd` | number | Cơ sở tính **average cost** (VND) |
| `ladders[]` | array of object | **active ladders**. Mỗi phần tử: `id`, `type`, **`month`**, `created`, `status`, `anchor_price`, `spacing_pct`, `score_at_creation`, `eligible_capital_vnd`, `invalidation_price`, `consecutive_invalidation_closes`, `zones[]` |
| `ladders[].month` | string `"YYYY-MM"` | **`ladder.month`** — tháng SỞ HỮU vốn, bản vá V-01 của T-09A. Mất trường này là tái tạo lại đúng lỗi T-09A vừa vá |
| `ladders[].zones[]` | array of object | `index`, `target_price`, `allocation_pct`, `target_vnd`, `status`, `filled_vnd`, `released_vnd` |
| `trades[]` | array of object | **Purchase History**: `ts`, `src`, `usdt`, `price`, `recPrice`, `eth`, `fee`, `vndRate`, `vndCost`, `shortfallBps`, `zone` |
| `p2p[]` | array of object | Quy đổi VND↔USDT: `ts`, `dir`, `vnd`, `usdt`, `fee`, `rate`. Ảnh hưởng treasury và giá vốn |
| `ledger[]` | array of object | Audit trail mọi dịch chuyển vốn (Data Model §6): `ts`, `pool`, `type`, `vnd`, `usdt`, `eth`, `reason`, `month`, `ladder`, `price`, `rate`, `shortfall` |
| `extraDays[]` | array of `{d, e, b, v}` | Giá đóng cửa người dùng gõ tay sau seed. **Không tái sinh được trong app** — app không gọi được `api.binance.com` (`webapp/README.md`) |

### MUST_PERSIST — tầng 2: dữ liệu tham chiếu (mất = không dùng được app, nhưng không sai tiền)

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `seed{}` | `{schema, strategy_version, strategy_config_hash, dataset_hash, config, history[], parity[]}` | 420 ngày lịch sử giá + config chiến lược + 40 ngày parity. **Không phải state kế toán.** Tái sinh được ngoài app bằng `ethdca export-live` — nhưng việc đó cần terminal, trái `DEC-011` điểm 8, nên vẫn phải bền |

Ranh giới tầng 1 / tầng 2 là ranh giới tách document ở OD-B: mất tầng 2 thì nạp lại được; mất
tầng 1 thì **không có gì tái tạo được**.

### CAN_RECOMPUTE — tính lại được từ MUST_PERSIST, KHÔNG persist

| Giá trị | Sinh ra bởi |
|---|---|
| `view.hist`, `view.ind` | `recompute()` từ `seed.history` + `state.extraDays` |
| `view.last`, `view.prev`, `view.score` | `E.computeIndicators()`, `E.scoreForDay()` |
| `view.smartUnlock`, `view.oppUnlock`, `view.multiplier` | `E.smartUnlock()`, `E.opportunityUnlock()`, `E.scoreMultiplier()` |
| `view.smartSpacing`, `view.oppSpacing` | `E.smartSpacing()`, `E.opportunitySpacing()` |
| `view.regime` | `deriveRegime()` |
| `poolTotal(p)`, `smartReservable(m)`, `oppReservable()` | Hàm thuần trên `months`/`oppFund` + `view` |
| `currentMonth()`, `ladderMonth(L)` | Suy từ `months` / `ladders[].month` |
| Kết quả parity JS↔Python | `E.checkParity(seed)` |
| P&L, giá vốn trung bình hiển thị | Suy từ `eth`, `costUsdt`, `costVnd`, `view.last.close` |

Persist các giá trị này là nhân bản nguồn sự thật — `STATE_AUTHORITY.md` gọi đó là governance
defect, không phải dự phòng.

### EPHEMERAL — không bao giờ persist

| Giá trị | Vì sao |
|---|---|
| `dirty` | Cờ "có thay đổi chưa lưu"; ý nghĩa chỉ trong một phiên trình duyệt |
| `canPublish` | Kết quả dò capability của host; thuộc về host, không thuộc về sổ |
| Tab đang mở, giá trị đang gõ trong form | UI |
| Nội dung `saveChip`, `banners`, `*Msg` | Hiển thị, sinh lại mỗi lần render |
| `today` (mặc định ngày/tháng) | Tính từ đồng hồ máy |

### Mirror hiện có — đổi vai, không xoá

`localStorage["ethdca-tracker-state-v1"]`, `localStorage["ethdca-tracker-seed-v1"]`,
`sessionStorage["ethdca-tracker-state-v1"]`: theo §3 chúng được **giữ lại làm cache / mirror /
local recovery**, và **thôi làm nguồn sự thật**. Xem CHECK-T09B-16.

---

## Persistence Model

    WEBAPP
       ↓
    APP STATE (trong bộ nhớ)
       ↓
    FIREBASE DURABLE STORAGE      <- nguồn bền duy nhất
       ↕
    localStorage / sessionStorage <- mirror, cache, local recovery. KHÔNG phải nguồn bền

Mất `localStorage` **không được** đồng nghĩa mất state thật.

### Load flow

    MỞ APP
      → khởi tạo Firebase bằng config trong webapp/ (Firebase Hosting phục vụ trang — OD-A)
      → AUTHENTICATE: đã có Anonymous session (IndexedDB) → dùng lại UID cũ (kịch bản
                       REQUIRED của CHECK-T09B-04 — same-browser-profile)
                       chưa có (lần đầu, hoặc IndexedDB trống — thiết bị/trình duyệt mới)
                         → tạo Anonymous UID mới
                         → UID mới KHÔNG khớp owner UID trong rules → Firestore từ chối đọc.
                           Đây KHÔNG phải lỗi Firestore, và KHÔNG phải app lỗi — đây là hành
                           vi ĐÚNG theo `OD-C = R2` (`DEC-021`): cross-device recovery ngoài
                           phạm vi V1. Hiện banner **"không nhận diện được thiết bị/trình
                           duyệt này"** (gate K/`CHECK-T09B-11`), khác thông điệp với lỗi
                           mạng; hướng dẫn export/import JSON (`H-23`). KHÔNG tạo Anonymous
                           UID mới rồi âm thầm cho ghi — điều đó sẽ mở một bản sổ "rỗng" song
                           song với bản sổ thật, đúng thứ gate L cấm.
      → ĐỌC durable state (document sổ + document seed)
      → VALIDATE: schema + bất biến kế toán T-09A
          ├─ hợp lệ            → state := bản durable
          │                       localStorage := mirror của bản đó
          │                       PERSISTENCE = ONLINE
          ├─ malformed/corrupt → KHÔNG nạp thành accounting state (gate L)
          │                       banner đỏ, chặn mọi hành động ghi sổ
          │                       KHÔNG ghi đè bản durable — giữ nguyên để cứu
          └─ đọc thất bại      → PERSISTENCE = OFFLINE, banner đỏ (gate K)
                                  được phép hiển thị mirror nhưng phải ĐÁNH DẤU
                                  "chưa xác nhận từ nguồn bền"; chặn ghi sổ mới
      → recompute() dựng view từ seed + extraDays
      → DÙNG APP

### Save flow

    THAO TÁC LÀM ĐỔI STATE (touch())
      → áp dụng vào state trong bộ nhớ; rev += 1
      → ghi mirror localStorage (best-effort, KHÔNG phải durable)
      → GHI DURABLE lên Firebase và ĐỢI XÁC NHẬN TỪ SERVER
          ├─ thành công → PERSISTENCE = SAVED (rev đã bền)
          └─ thất bại   → PERSISTENCE = NOT SAVED (gate J)
                          KHÔNG hiển thị bất kỳ dấu hiệu nào hàm ý đã lưu bền
                          giữ bản local để cứu; cho thử lại; cho export JSON

Không thiết kế realtime synchronization. Đây không phải ứng dụng tần suất cao (§4).

Lưu ý thi hành bắt buộc: nếu bật offline persistence của Firestore, **việc SDK áp bản ghi vào
cache cục bộ KHÔNG phải xác nhận bền**. Chỉ promise của `setDoc()` resolve mới là ack của
server. Nhầm hai thứ này chính là điều gate J cấm.

### Failure semantics (IN SCOPE)

| Tình huống | Hành vi bắt buộc |
|---|---|
| Firebase **load** thất bại | Hiện rõ. Không giả vờ state rỗng là state thật. Chặn ghi sổ mới |
| Firebase **write** thất bại | Hiện rõ. Không hiển thị "đã lưu". Giữ bản local, cho thử lại |
| State **malformed** (sai schema/thiếu khoá) | Không trở thành accounting state. Không ghi đè bản durable |
| State **corrupt** (đủ khoá nhưng sai bất biến kế toán) | Như trên |
| **Thiếu accounting state bắt buộc** | Như trên |
| Firebase **Auth** thất bại hoặc rules từ chối UID hiện tại (`OD-C`) | Hiện rõ — banner phân biệt rành mạch với "load thất bại": đây là **không chứng minh được danh tính**, không phải "Firestore không có dữ liệu". Không giả vờ đây là state rỗng của một owner mới |

Mọi failure có khả năng làm sai tiền phải **visible** — `DEC-011` điểm 9, fail visibly /
fail closed. KHÔNG xây enterprise fault-tolerance (retry policy nhiều tầng, circuit breaker,
queue bền, reconciliation nền).

---

## Ranh giới historical state

Chỉ thị §9 và `RSK-003`: state tạo **trước** T-09A có thể đã sai sẵn do V-01/V-02.

- Forensic / migrate / sửa historical accounting = **OUT OF SCOPE T-09B V1**.
- T-09B **không được** tuyên bố historical state là sạch. Đưa một bản sổ có thể sai lên Firebase
  không làm nó đúng — nó chỉ làm cái sai trở nên bền.
- Cảnh báo hiện có phải sống sót qua vòng lưu/nạp: ladder không có `month` tường minh phải **vẫn**
  không có `month` sau khi round-trip, để `inferredMonthLadders()` tiếp tục sinh banner
  "THÁNG SỞ HỮU SUY LUẬN" (`app_logic.js:465-508`).
- T-09B **không** được backfill `ladders[].month`. Backfill là forensic migration.

Xem CHECK-T09B-15.

---

## Scope (Scope Lock)

- Lớp persistence của app web: đọc/ghi durable state qua Firebase, validate lúc nạp, báo trạng
  thái persistence ra UI
- Đổi vai `localStorage`/`sessionStorage` từ nguồn sự thật thành mirror/cache/recovery
- Cấu hình Firebase + security rules tối thiểu cho một người dùng
- Ca kiểm thử round-trip và bất biến kế toán sau round-trip
- Điều chỉnh đường export/import JSON nếu capability của host cũ không còn (phụ thuộc OD-A)

## Out of Scope

- **Đổi khỏi Firebase** sang bất kỳ database/provider nào khác — `DEC-019`, FIXED
- Cloud Functions, Analytics, Messaging, Remote Config, Storage, App Check
- Multi-user, permission system, phân quyền theo vai trò, realtime collaboration
- Realtime synchronization, event architecture, microservices
- Provider abstraction layer, generic repository framework, "future-proof" indirection (§11)
- Forensic / migrate / sửa historical accounting state (§9)
- Backfill `ladders[].month`
- Sửa logic kế toán: `addContribution`, `addP2P`, `addBuy`, `reserveFor`, `releaseLadder`,
  `createLadder`, `cancelLadder`, `ladderMonth`, `smartReservable`, `oppReservable`
- `webapp/engine.js` — 0 dòng đổi (giữ nguyên parity với Python, `RSK-002`)
- `src/eth_dca_os/**` — Python decision engine không đụng (§16)
- Redesign webapp, UI polish, dashboard, chart, mobile
- WP-C2 (execution state machine), WP-C3 (partial fill), WP-C4 (parity), T-08/T-10 (cảnh báo)
- H-19 (`monthKey()` dùng giờ địa phương thay vì `accounting_timezone`), H-20 (đường mua trực
  tiếp không giới hạn theo unlock) — hardening đã có backlog, không hấp thụ vào đây
- Security hardening ngoài mức rules tối thiểu — `DEC-011` điểm 10

## Expected Touch Area

Suy ra từ implementation thật, **không cấp authority toàn repo**.

Allowed:
- `webapp/app_logic.js` — **chỉ** khối `/* persistence */` (`touch`, `save`, `pageHTML`), khối
  khởi tạo state (dòng 32-59), `renderBanners()` (thêm banner trạng thái persistence), và các
  handler export/import nếu OD-A làm mất capability của host
- `webapp/app_shell.html` — thẻ `<script>` nạp Firebase SDK + phần tử hiển thị trạng thái
  persistence
- `webapp/build_app.js` — chỉ phần liên quan đến việc nhúng state, nếu OD-A làm nó không còn cần
- `webapp/firebase_config.js` (mới) — project config
- `webapp/test_t09b_persistence.js` (mới) + đăng ký vào `webapp/package.json`
- `firestore.rules`, `firebase.json` (mới) — chỉ khi OD-A chọn A1

Do not touch without SCOPE EXPANSION REQUIRED:
- `webapp/engine.js`
- Các hàm kế toán trong `app_logic.js` liệt kê ở Out of Scope
- `src/eth_dca_os/**`, `pyproject.toml`, `pyproject.lock`
- `docs/spec/**`
- `governance/**`, các file khác trong `PROJECT/**` ngoài phần roadmap/ledger bắt buộc cập nhật

## Dependencies

- `WP-C1` — DONE (nguồn thẩm quyền cho hiện trạng persistence và cho `RSK-001`)
- `T-09A` — DONE (`DEC-018`). Bắt buộc: T-09B phải bảo toàn bất biến mà T-09A vừa dựng
- `DEC-019` — ràng buộc Firebase (đã ghi tại phiên này)
- **`OD-A`, `OD-B`, `OD-B2`** — CHƯA CÓ. Đây là thứ đang chặn `PLANNED → READY`

## Blocks

- `T-10` (triển khai lớp cảnh báo) — roadmap ghi "Sau T-08, T-09B, WP-C4"
- Việc dùng app hằng ngày với tiền thật mà không phải thủ công xuất JSON định kỳ (`RSK-001`)

## Escalation Triggers

- Phát hiện đường làm **mất hoặc hỏng sổ đã bền** mà không có lối cứu → dừng, báo ngay, liên kết
  `RSK-001`
- Round-trip làm đổi một con số kế toán bất kỳ → `DATA_INTEGRITY_RISK`, dừng
- Phải sửa hàm kế toán để persistence chạy được → `SCOPE EXPANSION REQUIRED`, không tự làm
- Phải đổi khỏi Firebase → `ARCHITECTURE_CHANGE_REQUIRED` + `OWNER_DECISION_REQUIRED`; tuyệt đối
  không silently đổi
- Chạm bất kỳ ngưỡng nào của Absorption Limit → `ABSORPTION_LIMIT_REACHED`, không tự tạo task

---

## Ready Gate

Theo `TASK_READY_GATE_STANDARD.md` § MAJOR Ready Gate, cộng 14 điều kiện riêng ở §13 của chỉ thị.

### MAJOR Ready Gate chuẩn

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency DONE hoặc được waive tường minh — `WP-C1` DONE, `T-09A` DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — `DEC-011` điểm 5-9, Strategy §8, Data Model §6
- [x] Data impact được biết — state inventory ở trên, phân loại đủ ba nhóm
- [x] Security impact được biết — danh tính rules ✅ (`OD-B2` = Anonymous Auth một UID,
      `DEC-020`); Minimum Security Floor ✅ (`DEC-021` §4); giới hạn recovery của danh tính đó
      ✅ đã chốt = OUT OF SCOPE V1, `OD-C = R2` (`DEC-021`)
- [x] Routing/API impact được biết — không có API nội bộ; routing giữ Tier D / xhigh
- [x] Migration prerequisite sẵn sàng — `OD-A` resolved (Firebase Hosting, `DEC-020`): biết rõ
      app chạy ở đâu, biết đường đưa state hiện có lên Firestore lần đầu
- [x] Difficulty được chấm — 3/4
- [x] Risk được chấm — 3/4
- [x] Blast Radius được chấm — 3/4; Effective Risk = HIGH
- [x] Primary agent tier được gán — D / xhigh, xác nhận bằng `routing_engine.py`
- [x] Escalation trigger được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được freeze trước implementation — Ready Gate đủ 15/15; freeze thực hiện
      ngay dưới đây, cùng phiên với `DEC-021`

### 14 điều kiện riêng (§13 chỉ thị)

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | Scope Lock rõ | ✅ |
| 2 | `CAP-WEBAPP` authority rõ | ✅ — `CAPABILITY_REGISTRY.md` §2 |
| 3 | `WP-C1` lineage rõ | ✅ |
| 4 | Firebase constraint recorded | ✅ — `DEC-019` |
| 5 | State inventory rõ | ✅ |
| 6 | MUST_PERSIST rõ | ✅ — hai tầng |
| 7 | Load/save flow rõ | ✅ — cập nhật thêm bước Auth (`DEC-020`) |
| 8 | Failure semantics rõ | ✅ — cập nhật thêm hàng Auth thất bại (`DEC-020`) |
| 9 | T-09A invariants rõ | ✅ |
| 10 | Historical boundary rõ | ✅ |
| 11 | Expected Touch Area rõ | ✅ |
| 12 | Firebase component được xác định | ✅ — Cloud Firestore, `OD-B` RESOLVED (`DEC-020`) |
| 13 | Completion Gate finalized | ✅ — 16 REQUIRED check dưới đây, không sửa yếu (1 check tái phạm vi theo Owner Scope Decision có audit trail, xem `CHECK-T09B-04`) |
| 14 | Routing xác nhận | ✅ — `routing_engine.py` trả D / xhigh |
| + | Không còn architecture ambiguity ngăn implementation | ✅ — `OD-C = R2` RESOLVED (`DEC-021`); khe kỹ thuật vẫn ghi lại (không phủ nhận), nhưng không còn ambiguity về việc phải làm gì |

### Kết quả Ready Gate

    READY GATE = ĐẠT — 15/15 dòng ✅ (đếm cả dòng "+"), 17/17 dòng MAJOR Ready Gate chuẩn ✅
    OD-A, OD-B, OD-B2 = RESOLVED tại DEC-020. OD-C = RESOLVED (R2) tại DEC-021.
    Không còn Owner Decision nào chặn.

    T-09B: PLANNED -> READY
    Completion Gate: FINALIZED -> FROZEN (freeze thực hiện tại phiên DEC-021, 2026-09-02)

---

## Thực thi — S014 (2026-09-02) · `READY → IN_PROGRESS → IMPLEMENTED`

Branch `claude/t09b-firebase-implementation-nz50is` từ `origin/main` @ `4502ea6`
(BASE). Kiến trúc thực thi đúng baseline FROZEN — không đổi, không thêm thành phần:

    Browser → Firebase Hosting (firebase.json: public = webapp/public)
            → Firebase Authentication, Anonymous (signInAnonymously; session trong IndexedDB)
            → Cloud Firestore: ethdca/state (sổ) + ethdca/seed (tham chiếu)
              firestore.rules: chỉ MỘT owner UID đọc/tạo/sửa hai document; không delete; mặc định deny.
    localStorage: mirror/cache (STORE_STATE, STORE_SEED) + stash bản lệch (STORE_STASH). Không còn
    nhúng state vào trang, không còn quine/publish, export dùng <a download>.

Production file đổi: `webapp/app_logic.js` (chỉ khối persistence/init/banner/handler guard/export-
import-wipe), `webapp/app_shell.html`, `webapp/build_app.js`; mới: `webapp/firebase_config.js`,
`firestore.rules`, `firebase.json`. `webapp/engine.js`, `src/eth_dca_os/**`, `pyproject.*` = 0 dòng.
Test: `webapp/test_firebase_harness.js` (mới), `webapp/test_t09b_persistence.js` (mới), năm test cũ
chuyển sang harness (kịch bản/assertion giữ nguyên). Chi tiết: `docs/sessions/S014-*.md`.

**Bằng chứng và giới hạn của bằng chứng (phân loại trung thực theo chỉ thị §14):**

- Mọi check chạy qua đường sản phẩm thật (trang build thật → Firebase SDK compat 12.18.0 thật →
  Firebase **Emulator Suite** Auth + Firestore với đúng `firestore.rules` của repo). Emulator là
  Firebase chạy cục bộ của Google (cùng rules engine, cùng giao thức) — không phải mock SDK, không
  phải mock Firestore. Bằng chứng "phía Firebase" được đọc độc lập với app qua REST của emulator.
- Môi trường agent chặn `www.gstatic.com` nên thẻ `<script>` SDK trong `app_shell.html` được harness
  trả bằng file cùng version từ `node_modules/firebase`; trên Hosting thật trình duyệt tải thẳng từ
  gstatic — chưa kiểm được ở đây.
- **Project Firebase thật CHƯA tồn tại** (chủ dự án chưa tạo; `firebase_config.js` còn `REQUIRED`).
  Do đó: *CODE IMPLEMENTATION COMPLETE*; *REAL FIREBASE SETUP REQUIRED* (tạo project, bật Anonymous,
  tạo Firestore, điền config, `firebase deploy`, chép UID vào rules, deploy rules — `webapp/README.md`
  § Thiết lập Firebase). **Production reachability trên project thật/Hosting thật = NOT_TESTED** và
  KHÔNG được suy ra từ emulator. Sau khi thiết lập, chủ dự án lặp lại bằng tay chuỗi CHECK-01/02/03/
  04/14 trên app thật (mở app → nhập giá → ghi giao dịch → đóng → mở lại; xoá site data → mở lại) để
  đóng khoảng trống này trước khi chuyển `DONE`.
- Real deploy: **KHÔNG** thực hiện trong phiên (không có project, không có credential).

## Completion Gate — FROZEN (2026-09-02, `DEC-021`)

Effective Risk = HIGH → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng được, và **bắt buộc
batch review cuối phiên thực thi**. Mọi check chạy qua **đường sản phẩm thật**
(UI → `app_logic` → Firebase → nạp lại), không gọi trực tiếp hàm nội bộ.

`A`–`N` là 14 mục tối thiểu chủ dự án nêu ở §14 chỉ thị, ánh xạ 1-1 sang `CHECK-T09B-01..14`.
`CHECK-T09B-15` và `-16` suy trực tiếp từ §9 và §3/§4 của cùng chỉ thị, không phải mục tự nghĩ ra.

Trạng thái ban đầu (lúc freeze): 16 check `NOT_TESTED`. **Cập nhật S014 (2026-09-02): 16/16
PASS, Evidence Level E1**, chạy trên Firebase Emulator Suite (Auth + Firestore, đúng
`firestore.rules` của repo, Firebase SDK thật, trang build thật phục vụ qua HTTP) — xem mục
"Thực thi — S014" cho phạm vi và giới hạn của bằng chứng. Câu chữ của từng check KHÔNG đổi; chỉ
ô Status và khối Evidence được điền.

### Reliability — ghi và đọc bền

#### CHECK-T09B-01 (§14.A) — Firebase durable write thành công
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: một thao tác làm đổi state ghi được lên Firebase và **được server xác nhận**. Bằng
chứng phải cho thấy bản ghi tồn tại phía Firebase, không chỉ promise resolve trong app.

Evidence (S014, E1 — emulator): `webapp/test_t09b_persistence.js` § CHECK-T09B-01 — thao tác nạp
vốn qua UI → `rev` 22→23, chip "Đã lưu bền · rev 23" chỉ hiện sau khi promise transaction resolve;
document `ethdca/state` (rev 23) và `ethdca/seed` (420 ngày) được đọc lại **độc lập với app** qua
REST API của emulator từ Node (`test_firebase_harness.getDoc`), bit-exact với bản trong bộ nhớ.
Kết quả: PASS (0 assert FAIL trong 10).

#### CHECK-T09B-02 (§14.B) — App load đúng state từ Firebase
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: mở app trên một phiên mới, state nạp lên **bằng đúng** bản đã ghi ở CHECK-01 — so từng
trường MUST_PERSIST tầng 1, không so ảnh chụp màn hình.

Evidence (S014, E1 — emulator): § CHECK-T09B-02 — mở trang mới (phiên mới, cùng profile), so
`diff(canon(bản đã ghi), canon(bản nạp))` = 0 lệch, và so riêng từng trường `schema, rev, months,
oppFund, treasury, eth, costUsdt, costVnd, ladders, trades, p2p, ledger, extraDays` (13/13 bằng
nhau); seed nạp từ `ethdca/seed` (OSCORE hiển thị). PASS.

#### CHECK-T09B-03 (§14.C) — Xoá localStorage vẫn recover được state
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: xoá sạch `localStorage` + `sessionStorage`, mở lại app, state kế toán phục hồi đầy đủ
từ Firebase. Đây là chứng minh trực tiếp rằng `RSK-001` đã được giảm thiểu.
Ghi chú (`OD-C`, `DEC-020`): kịch bản này **không** đụng `IndexedDB` nên **không** bị ảnh hưởng
bởi khe recovery của Anonymous Auth — acceptance criteria trên vẫn đứng nguyên, PASS được
trung thực với thiết kế đã duyệt.

Evidence (S014, E1 — emulator): § CHECK-T09B-03 — `localStorage.clear(); sessionStorage.clear()`
(đo `length` = 0), tải lại: cùng Anonymous UID (IndexedDB còn), state phục hồi bit-exact từ
Firestore (0 lệch), seed phục hồi, không banner lệch bản. PASS.

#### CHECK-T09B-04 (§14.D) — Đóng/mở lại môi trường sử dụng vẫn recover được state (đã tái phạm vi bởi Owner Scope Decision, `DEC-021`)
Priority: REQUIRED · Status: PASS · Evidence Level: E1

**Audit trail bắt buộc (`DEC-021` §6) — KHÔNG phải bug fix, KHÔNG phải evidence PASS:**

    OLD REQUIREMENT (DEC-019 / bản gốc của Task Spec này):
      "đóng hẳn trình duyệt (hoặc dùng một profile/cửa sổ khác), mở lại, state phục hồi
      đầy đủ" — bao gồm cả nhánh cross-device/cross-browser.

    OWNER PRODUCT INTENT CHANGE:
      DEC-021 — Personal Tool Simplification Principle + OD-C = R2 (SIMPLIFIED
      PERSONAL-TOOL RECOVERY). Chủ dự án không yêu cầu V1 đảm bảo seamless identity
      recovery khi đổi máy/browser/mất profile. Không xây recovery credential chỉ để
      đóng edge case này.

    NEW V1 REQUIREMENT (áp dụng từ đây):
      Đóng/mở lại trình duyệt THÔNG THƯỜNG (cùng browser profile, IndexedDB còn nguyên);
      reload; quay lại app sau một khoảng thời gian; restart máy NẾU browser profile / site
      identity vẫn còn — state kế toán PHẢI phục hồi đầy đủ, và bất biến kế toán T-09A PHẢI
      được bảo toàn.

Cross-device / cross-browser / lost-identity recovery: **OUT OF SCOPE V1** —
`PROJECT/HARDENING_BACKLOG.md` **H-23**. Khi Firestore rules từ chối một Anonymous UID không
khớp owner (đúng kịch bản này), app PHẢI hiện rõ đây là **"không nhận diện được thiết bị/trình
duyệt này"** — KHÔNG được im lặng hiện state rỗng như thể đó là sổ hợp lệ của một owner mới.
Đây là một dạng của `CHECK-T09B-11` (Firebase read/auth failure visible) — không mở REQUIRED
check mới, chỉ là một tình huống cụ thể mà check đó phải phủ.

Lối thoát V1 cho cross-device: export/import JSON thủ công (capability giữ nguyên qua `OD-A`).

Evidence (S014, E1 — emulator): § CHECK-T09B-04 — `launchPersistentContext(userDataDir)` →
`ctx.close()` (đóng hẳn trình duyệt) → mở lại cùng user-data-dir: cùng UID, `rev` = rev bền, state
bit-exact, bất biến T-09A (TOTAL = A+R+D theo contribution, không âm, reserved đủ backing ladder
ACTIVE, oppFund = Σ oppAdded) giữ nguyên; tiếp tục ghi sổ được (rev +1 bền). Phạm vi đúng NEW V1
REQUIREMENT (same-browser-profile); cross-device KHÔNG kiểm ở đây (H-23) — nhánh UID lạ được kiểm
tại CHECK-T09B-11. PASS.

### Data — bảo toàn sổ qua vòng lưu/nạp

#### CHECK-T09B-05 (§14.E) — Purchase History bảo toàn
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: `trades[]` round-trip nguyên vẹn — đúng số phần tử, đúng thứ tự, và mọi trường
(`ts`, `src`, `usdt`, `price`, `recPrice`, `eth`, `fee`, `vndRate`, `vndCost`, `shortfallBps`,
`zone`) bằng nhau từng giá trị, kể cả `null`.

Evidence (S014, E1 — emulator): § CHECK-T09B-05 — `trades[]` 3 phần tử (một có `recPrice`, một
`recPrice: null`, một mua thủ công `zone: null`, `vndRate: null`), so 11 trường × 3 phần tử bằng
`Object.is` (null giữ nguyên null), đúng thứ tự. PASS (35/35 assert).

#### CHECK-T09B-06 (§14.F) — Holdings / average cost bảo toàn
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: `eth`, `costUsdt`, `costVnd` round-trip **bằng đúng bit** (so sánh đẳng thức, không so
sánh có dung sai — chúng là số đã lưu, không phải số vừa tính).

Evidence (S014, E1 — emulator): § CHECK-T09B-06 — `eth`, `costUsdt`, `costVnd` so `Object.is`
(không dung sai) giữa bản trong bộ nhớ và bản durable đọc qua REST; ba số đều > 0. PASS.

#### CHECK-T09B-07 (§14.G) — Accounting pools / reserve / release / available bảo toàn
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: mọi `months[k].base{a,r,d}`, `months[k].smart{a,r,d}`, `months[k].contribution`,
`oppAdded`, `oppOverflow`, `oppFund{a,r,d}`, `treasury{vnd,usdt}` round-trip bằng đúng bit. Bất
biến `TOTAL = AVAILABLE + RESERVED + DEPLOYED` giữ nguyên trước và sau.

Evidence (S014, E1 — emulator): § CHECK-T09B-07 — hai tháng (2026-05, 2026-06): `contribution`,
`oppAdded`, `oppOverflow`, `base{a,r,d}`, `smart{a,r,d}`, `oppFund{a,r,d}`, `treasury{vnd,usdt}`
bằng `Object.is`; bất biến TOTAL = A+R+D (theo contribution) và backing ladder ACTIVE đo TRƯỚC và
SAU round-trip; ca có reserved > 0 và deployed > 0. PASS (40/40 assert).

#### CHECK-T09B-08 (§14.H) — Active ladders + `ladder.month` bảo toàn
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: `ladders[]` round-trip nguyên vẹn, **đặc biệt là `ladders[].month`** và toàn bộ
`zones[]` gồm `filled_vnd` và `released_vnd` — kể cả khi giá trị bằng `0`. Ca kiểm phải có ít
nhất một zone `filled_vnd: 0` để bắt đúng lỗi "xoá khoá có giá trị rỗng".

Evidence (S014, E1 — emulator): § CHECK-T09B-08 — 2 ladder (một ACTIVE có `month = "2026-06"`,
một CANCELLED có `released_vnd > 0`), mọi trường ladder và 7 trường × mọi zone bằng nhau, kể cả sự
**tồn tại** của khoá (`(k in z) === (k in D)`); có zone `filled_vnd: 0` và giá trị 0 được giữ. PASS
(66/66 assert).

#### CHECK-T09B-09 (§14.I) — Bất biến kế toán T-09A không drift
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: chạy lại **toàn bộ** `webapp/test_t09a_accounting.js`,
`webapp/test_multi_month_invariant.js`, `webapp/test_v01_v02_v03.js` trên state **đã đi qua
Firebase** (ghi lên, nạp về), và cho kết quả **giống hệt** khi chạy trên state trong bộ nhớ.
Phủ: pool ownership isolation, `ladder.month`, reserve, release, available, active backing.
Serialize/deserialize không được làm đổi accounting semantics.

Evidence (S014, E1 — emulator): `test_helpers.readState()` nay CHỜ máy chủ xác nhận, đọc bản
DURABLE từ Firestore qua REST (Node, độc lập với SDK) và đối chiếu bit-exact với bản trong bộ nhớ
(ném lỗi nếu lệch). Ba bộ test chạy NGUYÊN VĂN kịch bản/assertion trên state đã đi qua Firebase:
`test_t09a_accounting.js` **68/68 assert, 0 FAIL** (A ownership · B backing · C upper bound · D
conservation · E multi-month · F existing behavior); `test_multi_month_invariant.js` tất cả PASS;
`test_v01_v02_v03.js` V-01 = BÁC BỎ, V-02 = BÁC BỎ, V-03 = BÁC BỎ — giống hệt kết quả T-09A trên
state trong bộ nhớ (`docs/reviews/T-09A-batch-review.md` §2). PASS.

### Error Handling — failure phải nhìn thấy được

#### CHECK-T09B-10 (§14.J) — Firebase write failure visible
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: dựng một lần ghi thất bại (mất mạng / rules từ chối). App **không** được hiển thị bất
kỳ dấu hiệu nào hàm ý đã lưu bền. Trạng thái persistence hiện rõ là chưa lưu, và bản local vẫn
còn để cứu.

Evidence (S014, E1 — emulator): § CHECK-T09B-10 — (a) rules chỉ cho đọc: lệnh ghi bị từ chối
`permission-denied`, chip "CHƯA LƯU — permission-denied", banner "GHI THẤT BẠI", `durableRev` giữ
nguyên, bản local rev +1 vẫn trong localStorage, phía Firebase không đổi (REST); khôi phục rules →
"Lưu lại" → bền. (b) `setOffline(true)`: sau `ackTimeoutMs` chip "CHƯA XÁC NHẬN", rồi SDK từ chối
`unavailable` → "CHƯA LƯU"; không lúc nào chip hàm ý "Đã lưu"; bản local còn; có mạng lại → tự ghi
lại thành công (sự kiện `online`). PASS.

#### CHECK-T09B-11 (§14.K) — Firebase read failure visible
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: dựng một lần đọc thất bại. App **không** được im lặng khởi động với state rỗng như thể
sổ trống là sự thật. Banner đỏ, và mọi hành động ghi sổ bị chặn.
Ghi chú (`DEC-021`): "đọc thất bại" gồm cả trường hợp Firestore rules **từ chối** vì UID hiện
tại không khớp owner (thiết bị/trình duyệt mới, ngoài phạm vi V1 theo `CHECK-T09B-04`/`H-23`).
Nhánh đó phải hiện banner phân biệt rõ **"không nhận diện được thiết bị/trình duyệt này"**,
không dùng chung thông điệp mơ hồ với lỗi mạng, để chủ dự án biết cần export/import JSON thay
vì chờ tự phục hồi.

Evidence (S014, E1 — emulator): § CHECK-T09B-11 — (a) context mới (UID mới) khi sổ đã tồn tại:
phase UNRECOGNIZED, banner "KHÔNG NHẬN DIỆN ĐƯỢC THIẾT BỊ/TRÌNH DUYỆT NÀY" (khác thông điệp lỗi
mạng), không hiện sổ rỗng như sổ hợp lệ, ghi sổ bị chặn, phía Firebase không đổi. (b) Firestore
không với tới được: phase OFFLINE, banner đỏ "KHÔNG ĐỌC ĐƯỢC NGUỒN BỀN", mirror hiển thị nhưng ĐÁNH
DẤU "CHƯA xác nhận từ nguồn bền", ghi sổ bị chặn. (c) Auth không với tới được (context mới): phase
AUTH_FAILED, banner "KHÔNG XÁC THỰC ĐƯỢC", ghi sổ bị chặn. (d) `firebase_config.js` còn REQUIRED:
UNCONFIGURED, banner "CHƯA CẤU HÌNH FIREBASE", ghi sổ bị chặn. Mở lại bình thường sau đó: sổ nguyên
vẹn. PASS (24/24 assert).

#### CHECK-T09B-12 (§14.L) — Corrupt / malformed durable state không thành accounting state
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: ít nhất ba ca — (a) thiếu khoá `schema`; (b) `months` sai kiểu; (c) đủ khoá nhưng vi
phạm `TOTAL = AVAILABLE + RESERVED + DEPLOYED`. Cả ba: **không** được nạp âm thầm thành official
accounting state, và bản durable **không** bị ghi đè.

Evidence (S014, E1 — emulator): § CHECK-T09B-12 — bốn ca ghi thẳng lên Firestore qua REST: (a)
thiếu `schema`; (b) `months` là mảng; (c) đủ khoá nhưng `smart.a` tháng 2026-06 bị cộng thêm →
TOTAL = A+R+D ≠ contribution; (d) `smart.r` âm. Cả bốn: phase CORRUPT, lý do nêu đúng lỗi, `rev`
trong bộ nhớ = 0 (không thành accounting state), banner "NGUỒN BỀN KHÔNG HỢP LỆ … không ghi đè",
ghi sổ bị chặn, bấm Lưu lại không làm gì, `canonJSON(durable)` trước/sau bằng nhau (KHÔNG ghi đè).
Khôi phục bản hợp lệ → ONLINE lại. PASS (33/33 assert).

### Regression — không phá thứ đang chạy đúng

#### CHECK-T09B-13 (§14.M) — Existing clean web behavior không regression
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: `npm --prefix webapp test` PASS toàn bộ (`test_app.js`, `test_zone.js`,
`test_v01_v02_v03.js`, `test_multi_month_invariant.js`, `test_t09a_accounting.js`). `engine.js`
đổi **0 dòng** — chứng minh bằng `git diff --stat`, không bằng lời.

Evidence (S014, E1): `npm --prefix webapp test` → 6/6 file test exit 0 (`test_app.js`,
`test_zone.js`, `test_v01_v02_v03.js`, `test_multi_month_invariant.js`, `test_t09a_accounting.js`,
`test_t09b_persistence.js`), 0 page error. `git diff --stat 4502ea6 -- webapp/engine.js` → **rỗng
(0 dòng đổi)**; `src/eth_dca_os/**`, `pyproject.*` 0 dòng đổi. Bảo trì test: các test cũ chỉ đổi
cách mở trang (qua harness Firebase) và nguồn đọc state (durable), không đổi kịch bản/assertion;
bước 10 của `test_app.js` (quine template) được thay bằng kiểm "trang không nhúng state" vì cơ chế
quine không còn (OD-A). PASS.

### UI/UX — dùng được hằng ngày

#### CHECK-T09B-14 (§14.N) — Workflow cá nhân đơn giản, không cần terminal / AI coding agent
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: mô tả và chạy thật đúng chuỗi thao tác hằng ngày — mở app, nhập giá đóng cửa, ghi một
giao dịch, đóng, mở lại — mà **không** dùng terminal, không dùng AI coding agent, không thao tác
thủ công ngoài trình duyệt. Ánh xạ `DEC-011` điểm 8.

Evidence (S014, E1 — emulator): § CHECK-T09B-14 — trên profile bền, chỉ qua UI: nhập giá đóng
cửa (tab Nhập số liệu) → ghi một giao dịch mua → hai rev bền → `ctx.close()` (đóng trình duyệt) →
mở lại: giá và giao dịch còn nguyên, tab Lịch sử hiện đủ số lệnh. Không terminal, không AI agent,
không thao tác ngoài trình duyệt. Thiết lập MỘT LẦN (tạo project, điền config, deploy, chép UID
vào rules) có cần terminal — đúng ranh giới "Owner deploy khi setup" của chỉ thị §16 và
`DEC-011` điểm 8 (hằng ngày). PASS. Ghi chú: chuỗi này chạy trên emulator; trên Hosting thật
chủ dự án phải lặp lại một lần sau khi thiết lập (xem "Thực thi — S014").

### Data — ranh giới historical (§9 chỉ thị)

#### CHECK-T09B-15 — Không tuyên bố historical state là sạch
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: nạp một state có ladder **không** mang `month` (dạng trước T-09A), ghi lên Firebase,
nạp lại. Ladder đó **vẫn** không có `month` (không bị backfill), và banner "THÁNG SỞ HỮU SUY
LUẬN" của `renderBanners()` **vẫn** hiện. Đưa sổ lên Firebase không được làm cái sai trở thành
cái đúng.

Evidence (S014, E1 — emulator): § CHECK-T09B-15 — ghi qua REST một bản sổ hợp lệ mà mọi ladder
đều bị xoá khoá `month` (dạng trước T-09A); tải lại: nạp được (không bị coi là corrupt), banner
"THÁNG SỞ HỮU SUY LUẬN" hiện; thực hiện một thao tác → ghi lại lên Firestore → đọc lại qua REST:
`ladders[]` vẫn KHÔNG có khoá `month` (không backfill); tải lại lần nữa: banner vẫn hiện, ladder
nguyên vẹn. PASS.

### Data — vai trò của localStorage (§3, §4 chỉ thị)

#### CHECK-T09B-16 — Mirror không bao giờ âm thầm thắng nguồn bền
Priority: REQUIRED · Status: PASS · Evidence Level: E1
Yêu cầu: dựng ca `localStorage.rev > durable.rev`. App **không** được âm thầm lấy bản mirror làm
official accounting state (hành vi hiện tại ở `app_logic.js:46-56`, đúng ở kiến trúc cũ, sai ở
kiến trúc mới). Chênh lệch phải hiện ra và việc chọn bản nào là hành động **tường minh của người
dùng**.

Evidence (S014, E1 — emulator): § CHECK-T09B-16 — giả lập `localStorage.rev = durable.rev + 5`
(kèm đổi `treasury.vnd`): tải lại → sổ chính thức = nguồn bền (rev cũ), mirror bị thay bằng bản
bền, bản mới hơn cất riêng ở khoá `…local-diverged`, banner "BẢN TRÊN MÁY MỚI HƠN NGUỒN BỀN" với
hai nút; chọn *Bỏ* → stash xoá, nguồn bền không đổi; dựng lại và chọn *Đẩy lên* → nguồn bền nhận
nội dung bản trên máy với rev lớn hơn. Thêm: hai tab cùng profile — tab stale ghi sau bị từ chối
`stale-durable` (transaction có điều kiện rev), phía Firebase giữ bản của tab mới hơn, tab stale
hiện "NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC"; mirror CŨ HƠN nguồn bền bị thay lặng lẽ, không banner. PASS.

### Exit Criteria

1. 16/16 REQUIRED check PASS ở mức E1. — **ĐẠT (S014)**, E1 trên Firebase Emulator Suite; project
   thật: NOT_TESTED (xem "Thực thi — S014").
2. Batch review cuối phiên PASS, 0 BLOCKING còn lại có production path. — **ĐẠT**:
   `docs/reviews/T-09B-batch-review.md`, CONFIRMED BLOCKING = 0, 4 HARDENING (H-24..H-27).
3. `npm --prefix webapp test` PASS. — **ĐẠT** (6/6 file test).
4. `webapp/engine.js` đổi 0 dòng. — **ĐẠT** (`git diff --stat` rỗng).
5. Không có hàm kế toán nào trong Out of Scope bị sửa. — **ĐẠT** (diff `app_logic.js` không chạm
   `addContribution/addP2P/addBuy/addDay/reserveFor/releaseLadder/createLadder/cancelLadder/
   ladderMonth/smartReservable/oppReservable`; xem review §1).
6. `PROJECT/PROJECT_PROGRESS.md` cập nhật; `PROJECT/LO_TRINH_DE_HIEU.md` sinh lại bằng
   `sync_easy_roadmap.py`; `validate_easy_roadmap.py` PASS. — **ĐẠT**.
7. `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2 ghi cặp BASE/HEAD SHA của lượt implementation. — **ĐẠT**.
8. Session handoff được viết. — **ĐẠT**: `docs/sessions/S014-t09b-firebase-implementation.md`.
9. `RSK-001` được cập nhật bằng bằng chứng, KHÔNG tự đóng — `DONE` và việc đóng risk thuộc thẩm
   quyền chủ dự án (`STATE_AUTHORITY.md`). — **ĐẠT** (cập nhật, không đóng).

### Gate Change Control

Sau khi gate này FROZEN (tại `PLANNED → READY`), mọi thay đổi phải đi qua
`COMPLETION GATE CHANGE PROPOSAL` của `TASK_COMPLETION_GATE_STANDARD.md`. Không được gỡ hay làm
yếu một REQUIRED check chỉ để task PASS.
