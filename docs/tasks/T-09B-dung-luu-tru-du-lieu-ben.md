# T-09B — Dựng lưu trữ dữ liệu bền (Firebase)

## Metadata

Status:
PLANNED

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION

Completion Gate Freeze:
**FINALIZED, CHƯA FROZEN.** T-04/S002 chỉ đóng băng gate cho 15 work package; T-09B không nằm
trong 15 gói đó, nên chưa từng có gate nào được đóng băng cho task này. Gate dưới đây được
**finalize** tại phiên này theo `TASK_COMPLETION_GATE_STANDARD.md` mục "Gate Creation Timing"
("Before Task Becomes READY — review and finalize"). Nó **đóng băng tại đúng thời điểm
`PLANNED → READY`**, tức sau khi hai Owner Decision ở mục "OWNER_DECISION_REQUIRED" được trả
lời. KHÔNG có gate cũ nào bị sửa, xoá hay làm yếu.

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
Firebase Anonymous Auth. `DEC-020` cũng mở một khe mới — `OD-C` (recovery semantics) — vẫn
CHẶN `PLANNED → READY`. Xem mục OWNER_DECISION_REQUIRED bên dưới, nay đã cập nhật.

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

### Hai phương án — chờ chủ dự án chọn (`OWNER_DECISION_REQUIRED`)

| | Phương án | Đánh giá |
|---|---|---|
| **R1** | **Link một recovery credential vào Anonymous UID** — `linkWithCredential` gắn một cặp email/password (hoặc phone) vào UID nặc danh, một lần, ngay sau khi tạo UID lần đầu | **KHUYẾN NGHỊ.** Sinh hoạt hằng ngày KHÔNG đổi — vẫn tự động đăng nhập nặc danh trên browser đã liên kết, không có màn hình đăng nhập. Credential CHỈ dùng trên máy/browser mới: `signInWithEmailAndPassword` để quay lại ĐÚNG UID cũ, mở lại quyền đọc/ghi Firestore đã có. Đây KHÔNG phải "login UI phức tạp" hay "account system" — là một bước one-time setup, đúng tinh thần "tối thiểu cần cho durable persistence" (`DEC-019` điểm 3) |
| R2 | **Chấp nhận giới hạn, thu hẹp tuyên bố trung thực** — không thêm credential nào; viết lại phạm vi "recover" của `CHECK-T09B-04` chỉ còn same-browser-profile | Giữ đúng "không xây login system" tuyệt đối, nhưng để hở đúng kịch bản "đổi máy" — kịch bản `RSK-001` nêu tên đầu tiên. Lối thoát duy nhất còn lại cho "đổi máy" là export JSON thủ công |

**KHÔNG làm yếu `CHECK-T09B-04` để né khe này.** Cho tới khi chủ dự án chọn R1 hay R2:

    T-09B = PLANNED
    OWNER_DECISION_REQUIRED = OD-C (duy nhất còn chặn)
    Số task ID mới = 0 · Số production file bị sửa = 0

`CHECK-T09B-03` và `CHECK-T09B-04` (bên dưới, mục Completion Gate) được chú thích tham chiếu
`OD-C` — nội dung acceptance KHÔNG bị viết lại, vì nó phụ thuộc R1 hay R2 được chọn.

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
      → AUTHENTICATE: đã có Anonymous session (IndexedDB) → dùng lại UID cũ
                       chưa có (lần đầu, hoặc IndexedDB trống — xem OD-C)
                         → tạo Anonymous UID mới
                         → NẾU UID mới KHÔNG khớp owner UID đã ghi trong rules:
                           Firestore từ chối đọc — đây chính là khe OD-C, KHÔNG phải lỗi
                           Firestore. Hành vi cụ thể (bắt buộc thử recovery credential theo
                           R1, hay báo rõ "không phải máy đã đăng ký" theo R2) PHỤ THUỘC
                           quyết định OD-C, CHƯA thi hành ở gate này.
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
- [~] **Security impact được biết** — danh tính rules ✅ (`OD-B2` = Anonymous Auth một UID,
      `DEC-020`); **giới hạn recovery của danh tính đó CHƯA chốt** — xem `OD-C`
- [x] Routing/API impact được biết — không có API nội bộ; routing giữ Tier D / xhigh
- [x] Migration prerequisite sẵn sàng — `OD-A` resolved (Firebase Hosting, `DEC-020`): biết rõ
      app chạy ở đâu, biết đường đưa state hiện có lên Firestore lần đầu
- [x] Difficulty được chấm — 3/4
- [x] Risk được chấm — 3/4
- [x] Blast Radius được chấm — 3/4; Effective Risk = HIGH
- [x] Primary agent tier được gán — D / xhigh, xác nhận bằng `routing_engine.py`
- [x] Escalation trigger được định nghĩa
- [x] Completion Gate được finalize
- [ ] **Completion Gate được freeze trước implementation** — chỉ freeze khi Ready Gate đầy đủ;
      còn `OD-C` mở nên CHƯA freeze

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
| 12 | Firebase component được xác định | ✅ — Cloud Firestore, **`OD-B` RESOLVED (`DEC-020`)** |
| 13 | Completion Gate finalized | ✅ — 16 REQUIRED check dưới đây, không sửa yếu |
| 14 | Routing xác nhận | ✅ — `routing_engine.py` trả D / xhigh |
| + | Không còn architecture ambiguity ngăn implementation | ❌ — **`OD-C` chặn** (recovery semantics của Anonymous Auth, xem mục riêng ở trên) |

### Kết quả Ready Gate

    READY GATE = KHÔNG ĐẠT — 14/15 dòng ✅ (đếm cả dòng "+"); CHỈ dòng "+" còn ❌
    OD-A, OD-B, OD-B2 = RESOLVED tại DEC-020 (Firebase Hosting · Cloud Firestore ·
    Anonymous Auth một UID).
    Thiếu duy nhất: OD-C (recovery semantics — CHECK-T09B-04 nhánh "profile/cửa sổ khác"
    không PASS được trung thực với Anonymous Auth đơn thuần; chọn R1 hay R2).
    Dòng chuẩn "Completion Gate được freeze" vẫn ❌ vì nó chỉ đóng khi Ready Gate đủ 15/15.

    T-09B = PLANNED  (giữ nguyên — chỉ một Owner Decision còn thiếu, nhưng vẫn là một
    Owner Decision đang chặn theo đúng nghĩa chỉ thị §17/§"STATE TRANSITION")

---

## Completion Gate — FINALIZED

Effective Risk = HIGH → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng được, và **bắt buộc
batch review cuối phiên thực thi**. Mọi check chạy qua **đường sản phẩm thật**
(UI → `app_logic` → Firebase → nạp lại), không gọi trực tiếp hàm nội bộ.

`A`–`N` là 14 mục tối thiểu chủ dự án nêu ở §14 chỉ thị, ánh xạ 1-1 sang `CHECK-T09B-01..14`.
`CHECK-T09B-15` và `-16` suy trực tiếp từ §9 và §3/§4 của cùng chỉ thị, không phải mục tự nghĩ ra.

Toàn bộ 16 check hiện `NOT_TESTED` — chưa thực thi. `TASK_COMPLETION_GATE_STANDARD.md`: một
check chưa chạy thật thì trạng thái là `NOT_TESTED`, không phải PASS.

### Reliability — ghi và đọc bền

#### CHECK-T09B-01 (§14.A) — Firebase durable write thành công
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: một thao tác làm đổi state ghi được lên Firebase và **được server xác nhận**. Bằng
chứng phải cho thấy bản ghi tồn tại phía Firebase, không chỉ promise resolve trong app.

#### CHECK-T09B-02 (§14.B) — App load đúng state từ Firebase
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: mở app trên một phiên mới, state nạp lên **bằng đúng** bản đã ghi ở CHECK-01 — so từng
trường MUST_PERSIST tầng 1, không so ảnh chụp màn hình.

#### CHECK-T09B-03 (§14.C) — Xoá localStorage vẫn recover được state
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: xoá sạch `localStorage` + `sessionStorage`, mở lại app, state kế toán phục hồi đầy đủ
từ Firebase. Đây là chứng minh trực tiếp rằng `RSK-001` đã được giảm thiểu.
Ghi chú (`OD-C`, `DEC-020`): kịch bản này **không** đụng `IndexedDB` nên **không** bị ảnh hưởng
bởi khe recovery của Anonymous Auth — acceptance criteria trên vẫn đứng nguyên, PASS được
trung thực với thiết kế đã duyệt.

#### CHECK-T09B-04 (§14.D) — Đóng/mở lại môi trường sử dụng vẫn recover được state
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: đóng hẳn trình duyệt (hoặc dùng một profile/cửa sổ khác), mở lại, state phục hồi đầy đủ.
**CHẶN bởi `OD-C` (`DEC-020`), CHƯA đóng băng nội dung acceptance của nhánh "profile/cửa sổ
khác":** nhánh đó tạo `IndexedDB` trống → Anonymous UID mới → bị Firestore rules từ chối, nên
PASS trung thực phụ thuộc chủ dự án chọn R1 (recovery credential — PASS được qua đường
`signInWithEmailAndPassword`) hay R2 (thu hẹp phạm vi "recover" xuống same-browser-profile —
nhánh "profile/cửa sổ khác" khi đó tách khỏi acceptance của check này). KHÔNG tự chọn thay chủ
dự án; KHÔNG hạ acceptance criteria hiện tại chỉ để né kết luận NOT_TESTED.

### Data — bảo toàn sổ qua vòng lưu/nạp

#### CHECK-T09B-05 (§14.E) — Purchase History bảo toàn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: `trades[]` round-trip nguyên vẹn — đúng số phần tử, đúng thứ tự, và mọi trường
(`ts`, `src`, `usdt`, `price`, `recPrice`, `eth`, `fee`, `vndRate`, `vndCost`, `shortfallBps`,
`zone`) bằng nhau từng giá trị, kể cả `null`.

#### CHECK-T09B-06 (§14.F) — Holdings / average cost bảo toàn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: `eth`, `costUsdt`, `costVnd` round-trip **bằng đúng bit** (so sánh đẳng thức, không so
sánh có dung sai — chúng là số đã lưu, không phải số vừa tính).

#### CHECK-T09B-07 (§14.G) — Accounting pools / reserve / release / available bảo toàn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: mọi `months[k].base{a,r,d}`, `months[k].smart{a,r,d}`, `months[k].contribution`,
`oppAdded`, `oppOverflow`, `oppFund{a,r,d}`, `treasury{vnd,usdt}` round-trip bằng đúng bit. Bất
biến `TOTAL = AVAILABLE + RESERVED + DEPLOYED` giữ nguyên trước và sau.

#### CHECK-T09B-08 (§14.H) — Active ladders + `ladder.month` bảo toàn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: `ladders[]` round-trip nguyên vẹn, **đặc biệt là `ladders[].month`** và toàn bộ
`zones[]` gồm `filled_vnd` và `released_vnd` — kể cả khi giá trị bằng `0`. Ca kiểm phải có ít
nhất một zone `filled_vnd: 0` để bắt đúng lỗi "xoá khoá có giá trị rỗng".

#### CHECK-T09B-09 (§14.I) — Bất biến kế toán T-09A không drift
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: chạy lại **toàn bộ** `webapp/test_t09a_accounting.js`,
`webapp/test_multi_month_invariant.js`, `webapp/test_v01_v02_v03.js` trên state **đã đi qua
Firebase** (ghi lên, nạp về), và cho kết quả **giống hệt** khi chạy trên state trong bộ nhớ.
Phủ: pool ownership isolation, `ladder.month`, reserve, release, available, active backing.
Serialize/deserialize không được làm đổi accounting semantics.

### Error Handling — failure phải nhìn thấy được

#### CHECK-T09B-10 (§14.J) — Firebase write failure visible
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: dựng một lần ghi thất bại (mất mạng / rules từ chối). App **không** được hiển thị bất
kỳ dấu hiệu nào hàm ý đã lưu bền. Trạng thái persistence hiện rõ là chưa lưu, và bản local vẫn
còn để cứu.

#### CHECK-T09B-11 (§14.K) — Firebase read failure visible
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: dựng một lần đọc thất bại. App **không** được im lặng khởi động với state rỗng như thể
sổ trống là sự thật. Banner đỏ, và mọi hành động ghi sổ bị chặn.

#### CHECK-T09B-12 (§14.L) — Corrupt / malformed durable state không thành accounting state
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: ít nhất ba ca — (a) thiếu khoá `schema`; (b) `months` sai kiểu; (c) đủ khoá nhưng vi
phạm `TOTAL = AVAILABLE + RESERVED + DEPLOYED`. Cả ba: **không** được nạp âm thầm thành official
accounting state, và bản durable **không** bị ghi đè.

### Regression — không phá thứ đang chạy đúng

#### CHECK-T09B-13 (§14.M) — Existing clean web behavior không regression
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: `npm --prefix webapp test` PASS toàn bộ (`test_app.js`, `test_zone.js`,
`test_v01_v02_v03.js`, `test_multi_month_invariant.js`, `test_t09a_accounting.js`). `engine.js`
đổi **0 dòng** — chứng minh bằng `git diff --stat`, không bằng lời.

### UI/UX — dùng được hằng ngày

#### CHECK-T09B-14 (§14.N) — Workflow cá nhân đơn giản, không cần terminal / AI coding agent
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: mô tả và chạy thật đúng chuỗi thao tác hằng ngày — mở app, nhập giá đóng cửa, ghi một
giao dịch, đóng, mở lại — mà **không** dùng terminal, không dùng AI coding agent, không thao tác
thủ công ngoài trình duyệt. Ánh xạ `DEC-011` điểm 8.

### Data — ranh giới historical (§9 chỉ thị)

#### CHECK-T09B-15 — Không tuyên bố historical state là sạch
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: nạp một state có ladder **không** mang `month` (dạng trước T-09A), ghi lên Firebase,
nạp lại. Ladder đó **vẫn** không có `month` (không bị backfill), và banner "THÁNG SỞ HỮU SUY
LUẬN" của `renderBanners()` **vẫn** hiện. Đưa sổ lên Firebase không được làm cái sai trở thành
cái đúng.

### Data — vai trò của localStorage (§3, §4 chỉ thị)

#### CHECK-T09B-16 — Mirror không bao giờ âm thầm thắng nguồn bền
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1
Yêu cầu: dựng ca `localStorage.rev > durable.rev`. App **không** được âm thầm lấy bản mirror làm
official accounting state (hành vi hiện tại ở `app_logic.js:46-56`, đúng ở kiến trúc cũ, sai ở
kiến trúc mới). Chênh lệch phải hiện ra và việc chọn bản nào là hành động **tường minh của người
dùng**.

### Exit Criteria

1. 16/16 REQUIRED check PASS ở mức E1.
2. Batch review cuối phiên PASS, 0 BLOCKING còn lại có production path.
3. `npm --prefix webapp test` PASS.
4. `webapp/engine.js` đổi 0 dòng.
5. Không có hàm kế toán nào trong Out of Scope bị sửa.
6. `PROJECT/PROJECT_PROGRESS.md` cập nhật; `PROJECT/LO_TRINH_DE_HIEU.md` sinh lại bằng
   `sync_easy_roadmap.py`; `validate_easy_roadmap.py` PASS.
7. `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2 ghi cặp BASE/HEAD SHA của lượt implementation.
8. Session handoff được viết.
9. `RSK-001` được cập nhật bằng bằng chứng, KHÔNG tự đóng — `DONE` và việc đóng risk thuộc thẩm
   quyền chủ dự án (`STATE_AUTHORITY.md`).

### Gate Change Control

Sau khi gate này FROZEN (tại `PLANNED → READY`), mọi thay đổi phải đi qua
`COMPLETION GATE CHANGE PROPOSAL` của `TASK_COMPLETION_GATE_STANDARD.md`. Không được gỡ hay làm
yếu một REQUIRED check chỉ để task PASS.
