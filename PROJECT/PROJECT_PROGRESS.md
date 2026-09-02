# PROJECT PROGRESS

## Project Summary
Project:
ETH DCA Operating System — V2.1.5

Objective:
Xây một công cụ chạy trên trình duyệt, dùng được như bảng tính, để chủ dự án theo dõi quá trình
hold/trade coin và nhận cảnh báo dựa trên các chỉ báo phân tích của bộ spec V2.1.5
(OSCORE, regime, ladder zone, giới hạn thực thi, chất lượng dữ liệu).

Ràng buộc chi phối mục tiêu này: Implementation Plan đặt cổng chặn — app MVP đầy đủ chỉ được
dựng sau khi backtest cho verdict BUILD. Xem `PROJECT/PROJECT_DECISIONS.md` DEC-005.

Project Type:
LEGACY

Profile:
PRODUCT

Governance Version:
V3.2 (compact) + **AI Engineering V4.3 overlay** (adopted 2026-09-01).
Canonical AI entry point: `AGENTS.md`. CORE V4.3: `governance/v4/CORE/`.
Adoption record: `docs/decisions/ADOPTION-V4_3-migration-record.md`.
Adoption KHÔNG đổi trạng thái task nào, KHÔNG tạo task ID nào, KHÔNG sửa production code.

Last Updated:
2026-09-02 — **Owner UID production thật xác minh (checkpoint tiếp nối `DEC-023`)**: Owner
deploy Hosting thành công (`https://tinphatcontent.web.app`), mở bằng trình duyệt hằng ngày,
Anonymous Auth sinh UID `XWUo6IvUqhULI1v1EBrfndEDrE13`. Xác minh trực tiếp UID này qua emulator
(mint token bằng Auth Emulator custom-token, không sửa `firestore.rules` — file đó là test
fixture dùng chung cho 285+ assertion, thay placeholder cố định sẽ làm gãy toàn bộ owner-flow
test): 16/16 PASS — unauthenticated/wrong-UID deny, UID thật đọc/ghi state+seed allow, document
lạ + xoá đều deny, Content không đổi hành vi. Git diff checkpoint này = 0 file. Đưa Owner lệnh
deploy chính xác (thay UID cục bộ, không commit, rồi deploy `firestore.rules`). Evidence:
`docs/reviews/T-09B-shared-rules-merge.md` § Addendum. CHƯA deploy rules — chờ Owner tự chạy
lệnh. `CAP-WEBAPP` budget không đổi (2/0/2).

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-023` (`OD-WEBAPP-06`) — Firebase project thật DÙNG CHUNG
với ứng dụng "Content"; merge `firestore.rules` an toàn; Hosting RESOLVED.** Project thật
(`tinphatcontent`, display "CoinDCA") KHÔNG dành riêng cho ETH DCA OS — Firestore đang có dữ
liệu Content (`users`, `contents`, `schedules`, `groups`, `config`, `fb_queue`, `audit_logs`).
Kiến trúc T-09B (`DEC-020`) KHÔNG đổi — chỉ thêm bước merge rules an toàn. `firestore.rules`
nay là rules Content THẬT (giữ nguyên văn) + khối CoinDCA riêng biệt (`isCoinDcaOwner()`, đổi
tên khỏi `isOwner()` để không trùng hàm sẵn có của Content). Kiểm bằng Firestore Rules
Emulator (`webapp/test_shared_rules_merge.js`, `npm run test:rules-merge`): battery 53 probe
phủ toàn bộ 8 collection Content, BEFORE (rules Content nguyên văn) == AFTER (đã merge) —
**0 lệch** → `CONTENT_BEHAVIOR_PRESERVED = YES`. Ma trận CoinDCA 12 ca (§8) PASS 12/12. Evidence
đầy đủ: `docs/reviews/T-09B-shared-rules-merge.md`. Hosting: Owner tự kiểm Console — chưa
setup, không có site Content cần bảo toàn → dùng site mặc định, không cần multi-site. **CHƯA
DEPLOY** — owner UID trong rules còn placeholder, chờ Owner lấy UID thật từ trình duyệt hằng
ngày rồi tự deploy (agent không có Firebase CLI authority). `CAP-WEBAPP` budget không đổi:
2/0/2. Không tiêu repair cycle. Chi tiết: `PROJECT/PROJECT_DECISIONS.md` `DEC-023`.

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-022` (`OD-WEBAPP-05`) — Integration size disposition cho
`T-09B`: ACCEPT THE DIVERGENCE.** Phiên tiếp nối S014 trên cùng branch
`claude/t09b-firebase-implementation-nz50is` báo `INTEGRATION_DECISION_REQUIRED: loc>5000`
(divergence LOC = 12.272). Chủ dự án xác nhận CHẤP NHẬN kích thước hiện tại — KHÔNG merge `main`,
KHÔNG cut scope, KHÔNG rewrite dependency management chỉ để hạ số đo. Đo lại cho thấy phần lớn
divergence (~11.550/12.272 dòng) là generated dependency metadata (`webapp/package-lock.json`
+9.482 dòng ghim `firebase`/`firebase-tools`) + test/harness (~1.063 dòng, không phải production
path); production implementation thật theo khai báo chỉ +560/−162 (khớp `REVIEW_BUDGET_LEDGER.md`
§2.2.4). Sanity check dependency (`DEC-022` §11): 723 package mới, toàn bộ là transitive dependency
của `firebase`/`firebase-tools`, không có gói lạ — thêm `HARDENING_BACKLOG.md` **H-28** (footprint
`firebase-tools` rộng hơn phạm vi dùng thật: chỉ dùng emulator Auth+Firestore và deploy
hosting+firestore rules, nhưng CLI kéo theo Cloud SQL/Pub-Sub/App Hosting/Data Connect — tầng
tooling, không phải sản phẩm, không sửa). Chi tiết: `PROJECT/PROJECT_DECISIONS.md` `DEC-022`.

Trước đó, 2026-09-02 — **T-09B IMPLEMENTED (S014)**: persistence bền trên Firebase đã được **cài đặt và kiểm
chứng** trên branch `claude/t09b-firebase-implementation-nz50is` (BASE `4502ea6`, production commit
`a19d3ad`, test commit `0d4917a`). Kiến trúc đúng baseline FROZEN `DEC-020`/`DEC-021`: Browser →
Firebase Hosting → Firebase Anonymous Auth (một owner UID trong `firestore.rules`) → Cloud
Firestore `ethdca/state` + `ethdca/seed`; `localStorage` = mirror/cache. Trang không còn nhúng
state, không còn quine/publish của host cũ. Save flow: mỗi thao tác → mirror → ghi Firestore qua
transaction có điều kiện `rev`, UI chỉ báo "Đã lưu bền · rev N" khi máy chủ xác nhận; timeout →
"CHƯA XÁC NHẬN"; từ chối/mất mạng → "CHƯA LƯU", giữ bản local, Lưu lại/tự ghi lại khi có mạng.
Load flow: init → Anonymous Auth → đọc từ SERVER → `validateState` → ONLINE, hoặc một trong
UNCONFIGURED / AUTH_FAILED / UNRECOGNIZED ("không nhận diện được thiết bị/trình duyệt này", H-23)
/ OFFLINE (mirror chỉ để xem, đánh dấu chưa xác nhận) / CORRUPT (không nạp, không ghi đè, tải bản
thô để cứu) — mọi phase lỗi **khoá ghi sổ**. Mirror mới hơn nguồn bền không âm thầm thắng (cất
riêng + chọn tường minh). **16/16 REQUIRED check PASS (E1)** trên Firebase Emulator Suite (Auth +
Firestore, đúng `firestore.rules` repo, SDK thật, trang build thật qua HTTP; bằng chứng phía Firebase
đọc độc lập qua REST): `test_t09b_persistence.js` 285 assertion / 0 FAIL; ba test kế toán T-09A chạy
trên state đã round-trip Firestore (68/68; V-01/V-02/V-03 BÁC BỎ như trước); `npm --prefix webapp
test` 6/6. `engine.js`, `src/eth_dca_os/**`, `pyproject.*` = 0 dòng. Batch review bắt buộc → **PASS,
0 CONFIRMED BLOCKING còn lại** (1 finding hai-tab-stale-overwrite phát hiện trong phiên, sửa cùng
lượt), 4 HARDENING mới `H-24..H-27`. `CAP-WEBAPP` budget **2/0/2 không đổi** (implementation ban
đầu). Task ID mới = 0. **Giới hạn bằng chứng, ghi trung thực:** project Firebase THẬT chưa tồn tại
→ production reachability trên hạ tầng thật = NOT_TESTED; CODE IMPLEMENTATION COMPLETE, **REAL
FIREBASE SETUP REQUIRED** (chủ dự án: `webapp/README.md` § Thiết lập Firebase). Chuyển `DONE` là hành
vi của chủ dự án. `RSK-001`: giảm thiểu đã cài đặt, **chưa giảm trên thực tế** cho tới khi app
Firebase thật được dùng thay bản artifact. Handoff: `docs/sessions/S014-t09b-firebase-implementation.md`.

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-021` (`OD-WEBAPP-04`) — Personal Tool Simplification
Principle; `OD-C` = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)**, phiên tiếp nối trên nhánh thẩm
quyền `claude/t09b-firebase-decision-nnoony`. Chủ dự án phát biểu một nguyên tắc sản phẩm bao
trùm: ETH DCA OS là công cụ cá nhân, ưu tiên Financial correctness > Algorithm correctness >
Decision usefulness > Accounting correctness > không mất dữ liệu quan trọng > Daily usability
> Implementation simplicity > Low operational burden > Cost > Security hardening > Scalability
(11 mục, khai triển từ `DEC-011`/`DEC-019`, ghi tại `PROJECT/PROJECT_DECISIONS.md` `DEC-021` —
KHÔNG tạo artifact riêng, cùng vị trí đã giữ `DEC-011`). Kèm Critical Product Question (A–F, đối
chiếu `DEC-011`), Security Philosophy (security không phải trọng tâm V1) và Minimum Security
Floor (chống public write vô tình, chống commit secret, chống hiểu nhầm dữ liệu sai là hợp lệ,
chống UI báo "đã lưu" khi chưa lưu, chống security cơ chế quá yếu tới mức làm sai/mất
accounting state).

`OD-C` (khe recovery semantics mở tại `DEC-020`) được đóng bằng **R2 — SIMPLIFIED
PERSONAL-TOOL RECOVERY**: KHÔNG xây recovery credential (email/password) chỉ để đóng edge case
đổi máy/browser; cross-device/cross-browser/lost-identity recovery = **OUT OF SCOPE V1**,
ghi `PROJECT/HARDENING_BACKLOG.md` **H-23**. Đây là Owner Scope Decision dựa trên Product
Intent mới — khe kỹ thuật ghi tại `DEC-020` (Anonymous UID mới sau đổi máy bị Firestore rules
từ chối) vẫn ĐÚNG và KHÔNG bị phủ nhận, chỉ có phạm vi CHẤP NHẬN của V1 thay đổi.
`CHECK-T09B-04` được tái phạm vi bằng audit trail bắt buộc (OLD REQUIREMENT → OWNER PRODUCT
INTENT CHANGE → NEW V1 REQUIREMENT, ghi ngay tại chính check trong Task Spec) — KHÔNG được mô
tả là bug fix hay evidence PASS. `CHECK-T09B-03` và toàn bộ 15 REQUIRED check khác — bao gồm
mọi check thuộc financial/algorithm/accounting/persistence correctness — **KHÔNG đổi, KHÔNG bị
làm yếu**.

Đánh giá lại toàn bộ Ready Gate (không auto-PASS chỉ vì OD-C được quyết): **15/15 ĐẠT** — không
còn Owner Decision hay architecture ambiguity nào chặn. **Completion Gate 16/16 REQUIRED
FROZEN.** **`T-09B: PLANNED → READY`.** `CAP-WEBAPP` budget KHÔNG đổi: allowed 2 / used 0 /
remaining 2 — chuyển `READY` không phải implementation, không tiêu repair cycle. **Production
file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-020` (`OD-WEBAPP-03`) — giải quyết `OD-A`/`OD-B`/`OD-B2` cho
T-09B; phát hiện khe mới `OD-C`**, phiên tiếp nối trên nhánh thẩm quyền
`claude/t09b-firebase-decision-nnoony`. Chủ dự án APPROVED: `OD-A` = **Firebase Hosting**
(runtime host); `OD-B` = **Cloud Firestore** (document `ethdca/state` + `ethdca/seed`);
`OD-B2` = **Firebase Anonymous Auth**, rules khoá cứng một owner UID. Kiến trúc baseline:
Browser → Firebase Hosting → Firebase Authentication → Cloud Firestore → durable state;
`localStorage`/`sessionStorage` vẫn là mirror/cache. Đánh giá lại Ready Gate phát hiện khe MỚI
**`OD-C`**: Anonymous Auth session sống trong `IndexedDB` của một browser profile — ba trong
bốn kịch bản mất dữ liệu mà `RSK-001` nêu tên (cửa sổ riêng tư, đổi máy, đổi trình duyệt) tạo
`IndexedDB` trống → Anonymous UID mới → Firestore rules (khoá một UID cố định) từ chối. Đây là
khe giữa *durable STATE persistence* (đã giải quyết bằng Hosting+Firestore) và *khả năng
AUTHENTICATE lại làm owner sau khi mất local browser identity* (CHƯA). `CHECK-T09B-03` (xoá
localStorage/sessionStorage) KHÔNG bị ảnh hưởng; `CHECK-T09B-04` nhánh "profile/cửa sổ khác"
KHÔNG PASS được trung thực với Anonymous Auth đơn thuần. KHÔNG làm yếu check này. Hai phương
án chờ chủ dự án: **R1** (khuyến nghị) link recovery credential (email/password) vào UID nặc
danh, chỉ dùng khi đổi máy/browser, không đổi trải nghiệm hằng ngày; **R2** chấp nhận giới
hạn, thu hẹp phạm vi "recover" của check xuống same-browser-profile, để hở kịch bản "đổi máy".
**T-09B GIỮ `PLANNED`** — 14/15 dòng Ready Gate ✅ (đếm cả dòng "+"), chỉ dòng "+" (architecture
ambiguity) còn ❌ vì `OD-C`. Completion Gate 16/16 REQUIRED vẫn FINALIZED, KHÔNG sửa yếu, CHƯA
frozen (freeze chỉ xảy ra khi Ready Gate đủ). `CAP-WEBAPP` budget KHÔNG đổi: allowed 2 / used 0
/ remaining 2. Không mở repair cycle. Không chuyển `IN_PROGRESS`. **Production file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-019` (`OD-WEBAPP-02`) — Firebase là ràng buộc kiến trúc cố định cho
T-09B**, phiên Owner Authority / Ready-Gate Preparation. Chủ dự án bổ sung Product Intent (công cụ cá nhân,
single-user, dùng khi cần, tần suất thấp; ưu tiên correctness → usability → low operational burden →
implementation simplicity → cost → technical elegance → scalability) và chốt **Firebase** làm nền tảng
persistence — KHÔNG so sánh lại với Supabase/SQLite/PostgreSQL/D1/JSON Server. Lập Task Spec
`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` cho ID **đã tồn tại** (Task ID mới = **0**). State inventory
đọc từ schema thật (`app_logic.js::emptyState()`, `engine.js::buildLadder()`, `live_seed.json`), phân loại
MUST_PERSIST (hai tầng) / CAN_RECOMPUTE / EPHEMERAL. Completion Gate **FINALIZED** 16/16 REQUIRED, tất cả
`NOT_TESTED`. **T-09B GIỮ `PLANNED`** — Ready Gate KHÔNG đạt vì còn `OWNER_DECISION_REQUIRED`: `OD-A`
(runtime host — CSP của host hiện tại chặn mọi host ngoài trừ Google Fonts, nên Firebase không với tới được
và gate A/B/C/D không thể PASS; khuyến nghị Firebase Hosting), `OD-B` (Firestore vs Realtime Database —
khuyến nghị Cloud Firestore), `OD-B2` (danh tính tối thiểu cho security rules). `CAP-WEBAPP` budget KHÔNG
đổi: allowed 2 / used 0 / remaining 2. Không mở repair cycle. **Production file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-018` (`OD-WEBAPP-01`) — T-09A chuyển `DONE`**: chủ dự án
phê chuẩn hoàn thành T-09A và ratify hạn mức repair `CAP-WEBAPP`. **T-09A: IMPLEMENTED →
DONE.** Completion Gate GIỮ NGUYÊN 12/12 REQUIRED PASS (E1) — không sửa câu chữ/ngữ nghĩa.
`CAP-WEBAPP` budget: allowed 2 / used 0 / remaining 2 — nay là **Owner-ratified** (`DEC-018`),
không còn ở trạng thái default V4.3 chưa khai; xác nhận lượt implementation ban đầu của T-09A
KHÔNG tiêu repair cycle nào. Không mở repair cycle mới. Kết quả T-09A giữ nguyên: V-01 =
FIXED/không còn tái hiện, V-02 = FIXED/không còn tái hiện, V-03 = REJECTED, H-18 = DEFERRED,
H-19..H-22 = HARDENING với RE_TRIGGER_CONDITION, `F-T09A-03` = OUT_OF_SCOPE → WP-C4. Cảnh báo
historical state (dữ liệu lưu TRƯỚC bản vá V-01/V-02 có thể đã sai sẵn) GIỮ NGUYÊN, CHƯA đóng.
Task ID mới = 0.

Trước đó, 2026-09-02 — **T-09A IMPLEMENTED**: hai lỗi kế toán app web mà `WP-C1` đã XÁC NHẬN nay đã
được vá và kiểm chứng trên đường sản phẩm thật. **V-01** (release trả nhầm pool tháng) và
**V-02** (unlock không giới hạn reserve) đều **không còn tái hiện** — reproduction của WP-C1
chạy lại cho BÁC BỎ ở cả hai. 12/12 REQUIRED check PASS (E1). Batch review bắt buộc (Effective
Risk HIGH) → **PASS, 0 CONFIRMED BLOCKING**; sinh 4 HARDENING mới (H-19, H-20, H-21, H-22) và 1
`OUT_OF_SCOPE` định tuyến sang `WP-C4`. `CAP-WEBAPP` budget: allowed 2 (default V4.3) / used 0
/ remaining 2 — lượt vừa rồi là implementation ban đầu, không phải repair cycle. Task ID mới
= 0. `webapp/engine.js` và `src/eth_dca_os/**` 0 dòng đổi. **Chuyển T-09A sang `DONE` là hành
vi của chủ dự án** (`STATE_AUTHORITY.md`).

Trước đó, 2026-09-01 — S010 hoàn tất: **CAP-DATA REPAIR CYCLE #1** thi hành `DEC-016`. `F-S009-01`
ĐÃ ĐÓNG bằng `CHECK-A4-11` (REQUIRED, E1) — indicator daily nay neo cửa sổ vào NGÀY LỊCH,
ngày thiếu ra NaN → DEGRADED/INVALID thay vì một số hữu hạn sai. **WP-A4 trở lại DONE**
với 10/10 REQUIRED check PASS. Batch review bắt buộc (Effective Risk HIGH) → PASS, 0
BLOCKING; 2 HARDENING mới (H-16, H-17) và 1 `OUT_OF_SCOPE` định tuyến sang `WP-C4`.
`CAP-DATA` budget: allowed 2 / **used 1** / remaining 1. Task ID mới được tạo = 0.

Trước đó, 2026-09-01 — S009: **WP-A4 DONE** lần đầu (9/9 REQUIRED check PASS gồm
`CHECK-A4-10` do chủ dự án bổ sung qua `DEC-014`/`OD-A4-01`; đóng F-023, F-025, F-032 và
**F-E2A1R3-05**), kèm phát hiện `F-S009-01` mà S010 vừa đóng.

Overall Status:
IN_PROGRESS

Current Phase:
Phase 2 — Lớp A (bắt buộc sửa trước official run). Năm gói lớp A đã DONE: WP-A2, WP-A3,
WP-A4, WP-A7 (+ WP-D1 lớp D). Còn lại của GATE-A: **WP-A1, WP-A5, WP-A6**.

Current Task:
`T-09B` — **IMPLEMENTED** (S014, 2026-09-02). Chờ chủ dự án: thiết lập project Firebase thật, xác
nhận CHECK-01/02/03/04/14 bằng tay trên app thật, rồi Owner Decision `IMPLEMENTED → DONE`. DỪNG
theo chỉ thị — không mở task tiếp theo.

Current Task Mode:
MAJOR

Next Recommended Task:
**WP-A6** nay đã đủ dependency (WP-A3 ✅ + WP-A4 ✅ + WP-A7 ✅) và là mắt xích tiếp theo
trên đường găng; nó cũng phải trả lời H-15 (zone TRIGGERED trong chu kỳ INVALID).
Các gói READY khác: **WP-A5** (đủ dependency từ S004; cùng sửa `pipeline.py` với WP-A2 đã
push xong), **WP-A1** (chờ quyết định của chủ dự án về budget/legacy gate — KHÔNG mở được
bằng agent), **WP-C1** (song song, độc lập — xem "Song song" bên dưới), **WP-D2**.

Hai quyết định từng chặn ở đây nay đã ĐÓNG cả hai (2026-09-01, phiên Integration):
`DEC-013` (integration → phương án A, trunk = `main`, integration SHA `febc2ec`) và
`DEC-016`/`DEC-017` (`F-S009-01` → REOPEN WP-A4 một repair cycle; budget CAP-DATA
allowed 2 / used 0 / remaining 2). `DEC-016` **đã được THI HÀNH tại S010**: chu kỳ 1 tiêu
xong, `used` = 1, `remaining` = 1 (`REVIEW_BUDGET_LEDGER.md` §2.1). Không mở chu kỳ #2.
Branch authority từ đây: mọi phiên mới branch từ `origin/main` sau khi fetch.

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính, **trừ một ngoại lệ có ghi nhận rõ ràng**: WP-A2 dùng Tier ghi đè thủ
công (C thay vì B do router trả) theo phê duyệt của chủ dự án — xem DEC-008 và
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`. Bằng chứng routing của từng task nằm trong
file task tương ứng dưới `docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối
tài liệu này.

Roadmap này áp dụng **RCP-001** (`PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`), được chủ dự án phê
duyệt ngày 2026-08-23 kèm bốn điều kiện — xem mục "Roadmap Change Applied" bên dưới.

**Cập nhật S002:** 15 work package không còn là roadmap sơ bộ. Mỗi gói đã có file định nghĩa task
đầy đủ dưới `docs/tasks/`, với Ready Gate, Completion Gate (REQUIRED checks + Evidence Level),
Exit Criteria và Escalation Triggers **đã đóng băng** ngày 2026-08-23. Theo
`TASK_COMPLETION_GATE_STANDARD.md` mục "After Freeze", agent **không được xoá hoặc làm yếu REQUIRED
check** để task đi qua; mọi thay đổi phải dùng khối `COMPLETION GATE CHANGE PROPOSAL`.
Bản đối chiếu độ phủ: `docs/reviews/S002-coverage-regression-check.md`.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| DONE | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| VERIFYING | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. **CHECK-03-01 PASS tại WP-C1 (2026-09-02)** — gỡ BLOCKED; tất cả REQUIRED/RECOMMENDED check đều PASS. Chuyển DONE cần phiên riêng xác nhận Exit Criteria đầy đủ |
| DONE | T-04 | Chốt lộ trình và đóng băng tiêu chí | Soạn Ready Gate + Completion Gate cho 15 work package của RCP-001, đóng băng trước khi thực thi | C | xhigh | Sau T-01, T-02, T-03. HOÀN TẤT tại S002 — 15 file task đã đóng băng gate |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. KHÔNG nằm trên đường găng tới verdict (RCP-001) — chỉ chặn T-08 và WP-C2 |
| IN_PROGRESS | WP-A1 | Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, đúng môi trường, và tái lập lại được | C | xhigh | Sau T-04. Song song với WP-A2, WP-A3, WP-C1. Thay thế T-06A cũ (đóng F-005, F-007, F-009, F-010, F-011). S008: CHECK-A1-01..A1-10 PASS (E2 xác nhận), CHECK-A1-11 E2 **FAIL** vòng ba — hai finding chặn F-E2A1-01/02 đã đóng nhưng F-E2A1-03 còn mở và nay ở mức CAO, cộng sai lệch contract F-E2A1R3-03. KHÔNG mở vòng patch thứ tư (ESCALATION_PROTOCOL) |
| DONE | WP-A2 | Bật các hạng mục đã viết nhưng pipeline chưa chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có, dù code đã đúng | C | high | **DONE tại S006** (10/10 REQUIRED PASS; đấu nối thuần tuý — 4 module chỉ-đọc 0 dòng đổi; chiến lược + Benchmark A không đổi 159/159 trường) (đóng F-003, F-004, F-012, F-013, F-014). Tier C route tự nhiên sau MICRO-GOVDEF-001, xác nhận lại tại S006 |
| DONE | WP-A3 | Sửa vòng đời trạng thái thị trường và ladder khẩn cấp | Vốn có thể bị khoá vĩnh viễn khi thị trường hồi phục một phần rồi yếu lại | D | max | Sau T-04. HOÀN TẤT tại S003 (đóng F-001, F-021, F-022, F-030; 10/10 REQUIRED PASS, E2 PASS) |
| DONE | WP-A4 | Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu Binance thật có lỗ hổng; xử lý sai sẽ làm sai kết quả mô phỏng | C | xhigh | **DONE lại tại S010** sau CAP-DATA REPAIR CYCLE #1 (`DEC-016`): 10/10 REQUIRED PASS (CHECK-A4-01…08 FROZEN + CHECK-A4-10 do `DEC-014` + **CHECK-A4-11** do `DEC-016`). Đóng F-023, F-025, F-032, **F-E2A1R3-05**, **F-S009-01**. Hết chặn WP-A6/WP-C4 về phía A4. Budget CAP-DATA: allowed 2 / used 1 / remaining 1. Batch review S010 PASS, 0 BLOCKING; sinh H-16, H-17 (hardening) và F-S010-03 (`OUT_OF_SCOPE` → WP-C4) |
| READY | WP-A5 | Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược | Ba tín hiệu hiện không bao giờ được đo dù vẫn cho ra kết luận cuối cùng | C | xhigh | **Đủ dependency từ S006**: WP-A2 ✅, WP-A3 ✅, WP-A7 ✅ (vốn không bị khoá và phân phối vốn qua Smart ladder đúng thì số đo mới canonical). Tuần tự hoá với WP-A2 trên `pipeline.py` — đóng phần đo lường của F-002, và F-016 |
| READY | WP-A6 | Chốt và kiểm chứng đúng thứ tự các bước tính toán | Thứ tự sai nghĩa là con số chính thức không đại diện đúng cho chiến lược đã đặc tả | D | max | **READY từ S009** — WP-A3 ✅, WP-A4 ✅, WP-A7 ✅ đều DONE. Đóng F-018, F-019. Phải trả lời `HARDENING_BACKLOG.md` H-15 (số phận zone TRIGGERED trong chu kỳ INVALID) |
| DONE | WP-A7 | Sửa phạm vi kế toán vốn Smart theo tháng | Vốn Smart gần như không bao giờ đi qua cơ chế ladder từ tháng thứ ba, và một chiều bắt buộc của Gate 2 bị vô hiệu | D | max | **DONE tại S004** (12/12 REQUIRED PASS; E2 PASS WITH FOLLOW-UPS; F-035 RESOLVED, RSK-010 CLOSED). Đã hết chặn WP-A5/WP-A6/WP-C4/GATE-A về phía A7; các gói đó còn chờ dependency khác (đóng F-035) |
| PLANNED | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | Hai nhóm điều kiện ĐỘC LẬP, phải thoả CẢ HAI: (A) nội tại — T-05 và **GATE-A** (WP-A1…**WP-A7** đều DONE); (B) hạ tầng — BLK-001 (mạng Binance). Gỡ BLK-001 KHÔNG cho phép chạy T-06 khi GATE-A chưa PASS |
| PLANNED | WP-B1 | Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo | Không cho phép kết luận thuận lợi khi vẫn còn tín hiệu cảnh báo chưa đo được | D | max | Sau T-06. QUY TẮC BẮT BUỘC: nếu remediation của F-017 (Control F) ảnh hưởng Gate 1 → Gate 1 phải chạy lại trước khi coi kết quả hợp lệ (DEC-009) — đóng phần chính sách của F-002, F-015, F-017, F-026 |
| PLANNED | WP-B2 | Bổ sung test cho các yêu cầu đặc tả còn thiếu | Nhiều yêu cầu của BT §21 hiện không có gì kiểm chứng | C | xhigh | Sau T-06. Song song với WP-B1, WP-B3 |
| PLANNED | WP-B3 | Hoàn thiện nhật ký quyết định để truy vết được | Cần truy vết được vì sao hệ thống ra quyết định như vậy tại từng thời điểm | C | high | Sau T-06. Song song với WP-B1, WP-B2. Ngữ nghĩa `previous_state/new_state` phụ thuộc WP-C2 (đóng F-024, F-033) |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | Sau T-06 và **GATE-B** (WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE). Chặn T-11 |
| DONE | WP-C1 | Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test | App đang có thể dùng để ghi tiền thật; ba nghi vấn về sai sổ vẫn chưa có kết luận | C | xhigh | **DONE 2026-09-02** (8/8 REQUIRED PASS, E1). V-01 XÁC NHẬN, V-02 XÁC NHẬN, V-03 BÁC BỎ (an toàn tình cờ, HARDENING). Harness khôi phục (F-027 đóng). Gỡ BLOCKED cho T-03 (CHECK-03-01 PASS) |
| BLOCKED | WP-C2 | Làm rõ và đặt tên trạng thái thực thi của hệ thống | Cần biết rõ hệ thống đang ở trạng thái nào trước khi đưa vào dùng thật | C | xhigh | Sau T-05 (DEC-005 còn PENDING → BLOCKED). Cần ADR quyết định phạm vi trước khi bắt đầu (đóng F-006) |
| PLANNED | WP-C3 | Xử lý mua một phần ở tầng sản phẩm | Mua một phần là tình huống thật ngoài đời, tầng ghi sổ hiện chưa xử lý đúng | C | xhigh | Sau WP-C2 (đóng F-020) |
| PLANNED | WP-C4 | Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS) | Hai bản cài đặt có thể trôi khỏi nhau khi thêm tính năng mới vào JS | C | xhigh | Sau WP-A3, WP-A4, WP-A6, **WP-A7** (không khoá parity vào hành vi Smart capital đã xác nhận là sai). Chặn T-10, T-11 (đóng F-008) |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05 |
| DONE | T-09A | Sửa lỗi kế toán trong app web | Vá lỗi WP-C1 xác nhận là có thật (V-01, V-02), trước khi app được dùng với tiền thật | C | high | **Phạm vi xác định tại WP-C1 (2026-09-02)**: (1) sửa `releaseLadder()` (`webapp/app_logic.js:302-322`) dùng đúng tháng gốc của ladder thay vì `currentMonth()`; (2) `reserveFor()`/`createLadder()` (`webapp/app_logic.js:289-297,324-335`) phải nhân giới hạn theo `view.smartUnlock`/`view.oppUnlock` trước khi cho reserve. V-03 BÁC BỎ nên không bắt buộc sửa, có thể cân nhắc thêm check `data_quality` tường minh như HARDENING phòng thủ (không bắt buộc). Sau WP-C1 (DONE). **IMPLEMENTED 2026-09-02** — 12/12 REQUIRED PASS (E1), V-01 và V-02 không còn tái hiện, batch review PASS 0 BLOCKING; Task Spec `docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`. **DONE 2026-09-02** theo Owner Decision `DEC-018` (`OD-WEBAPP-01`) — Completion Gate giữ nguyên 12/12 REQUIRED PASS (E1), không sửa câu chữ/ngữ nghĩa |
| IMPLEMENTED | T-09B | Dựng lưu trữ dữ liệu bền (Firebase) | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | Sau T-04, WP-C1 (DONE), T-09A (DONE). Nên làm trước T-10. **Nền tảng persistence = Firebase — FIXED OWNER CONSTRAINT (`DEC-019`)**. Kiến trúc baseline `DEC-020`/`DEC-021`: Firebase Hosting → Firebase Anonymous Auth → Cloud Firestore (document `ethdca/state` + `ethdca/seed`). Task Spec: `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (Task ID mới = 0). **`DEC-021` (Personal Tool Simplification Principle) đóng `OD-C` = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)**: cross-device/cross-browser/lost-identity recovery KHÔNG phải V1 requirement (`H-23`, OUT OF SCOPE V1); `CHECK-T09B-04` tái phạm vi xuống same-browser-profile qua audit trail tường minh (OLD → OWNER PRODUCT INTENT CHANGE → NEW), KHÔNG phải bug fix. Ready Gate **15/15 ĐẠT**. Completion Gate 16/16 REQUIRED **FROZEN** 2026-09-02. **`T-09B: PLANNED → READY`.** Không còn Owner Decision nào chặn. `CAP-WEBAPP` budget KHÔNG đổi: 2/0/2 — chưa tiêu, chuyển READY không phải implementation. **S014 (2026-09-02): `READY → IN_PROGRESS → IMPLEMENTED`** — 16/16 REQUIRED PASS (E1, Firebase Emulator Suite), batch review PASS 0 BLOCKING, `H-24..H-27`; production commit `a19d3ad`, test `0d4917a`. **Chưa `DONE`**: project Firebase thật chưa tồn tại (REAL FIREBASE SETUP REQUIRED — `webapp/README.md`), chuyển `DONE` là hành vi chủ dự án. Budget 2/0/2 không đổi |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08, T-09B, WP-C4 |
| DONE | WP-D1 | Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả | Dọn cho sạch, không ảnh hưởng gì tới kết quả hiện tại | B | medium | **DONE tại S005** (6/6 REQUIRED PASS; kết quả mô phỏng trùng khớp bit-for-bit, chỉ counter chẩn đoán đổi theo ngoại lệ khai báo) (đóng F-028, F-029, F-031, F-034) |
| READY | WP-D2 | Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn | Một số mâu thuẫn thuộc về chính bộ đặc tả, cần chủ dự án quyết định mở V2.2 | C | xhigh | Không phụ thuộc. Đầu ra là đề xuất, KHÔNG sửa V2.1.5 (đóng S-001, S-002, S-003) |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07, WP-C2, WP-C3, WP-C4, và chỉ khi verdict = BUILD |

## Roadmap Change Applied — RCP-001

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` ngày 2026-08-23 kèm bốn quyết định.
Toàn bộ bốn quyết định đã được phản ánh vào bảng roadmap chuẩn ở trên. Chi tiết đầy đủ ghi ở
`PROJECT/PROJECT_DECISIONS.md` DEC-007, DEC-008, DEC-009.

1. **Cấu trúc 15 work package** — APPROVED nguyên trạng.
2. **Phân lớp A/B/C/D** — APPROVED WITH CONDITION: nếu remediation của F-017 (nằm trong WP-B1)
   ảnh hưởng tới input/calculation/execution behavior/dataset interpretation/strategy behavior/
   backtest behavior có khả năng tác động Gate 1, thì **mọi kết quả Gate 1 tạo trước đó bị coi
   là STALE/INVALIDATED và Gate 1 phải chạy lại** trước khi dùng cho verdict. Điều kiện này được
   ghi trực tiếp vào dependency column của WP-B1 ở bảng trên, và thành quy tắc chính thức ở
   DEC-009.
3. **Bỏ T-06A** — APPROVED. Toàn bộ phạm vi của T-06A được hấp thụ vào WP-A1, không mất
   requirement nào. WP-A1 vẫn là điều kiện bắt buộc trước T-06.
4. **WP-A2 routing** — OVERRIDE ROUTER. Tier C/Opus (không dùng B/Sonnet mà router trả), effort
   giữ nguyên `high` (giá trị router tính đúng, không bị ảnh hưởng bởi việc override Tier).
   Ghi tại DEC-008.

### Governance defect mới phát hiện trong quá trình duyệt

`routing_engine.py` dùng so sánh dấu phẩy động không có epsilon tại các mốc biên nguyên
(0/1/2/3). Với WP-A2, `model_score` hiển thị đúng `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, khiến `tier_from_score` (so sánh `s < 2`) trả về Tier B thay vì Tier C như
bảng `AGENT_CAPABILITY_MATRIX.md` quy định cho khoảng 2.00–2.99.

Đây là **defect của công cụ governance dùng chung, không phải finding của sản phẩm ETH DCA**.
Theo yêu cầu của chủ dự án, defect này được xử lý bằng ba artifact riêng, tách khỏi 33 finding
của S001:

- **Artifact:** `docs/reviews/GOVDEF-001-routing-engine-boundary.md`
- **Task:** `MICRO-GOVDEF-001` — xem mục "Micro Tasks (Inline)" bên dưới
- **Risk:** `GOV-RSK-001` — xem mục "Active Risks — Governance / Tooling" bên dưới

Không sửa `routing_engine.py` trong bước áp dụng roadmap này. Giải pháp sau này phải tổng quát
hoá cách so sánh (dùng epsilon hoặc làm tròn trước khi so sánh), không hard-code ngoại lệ riêng
cho WP-A2 hay bất kỳ task nào khác.

## Roadmap Change Applied — RCP-002

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG (2026-08-24)

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md` kèm điều kiện bổ sung. Nguồn:
triage `docs/reviews/PH-03-triage-smart-unlock-scope.md` (PH-03 = **DEFECT** → **F-035**, HIGH).
Roadmap chuẩn tăng từ **28 → 29 task**.

Nội dung đã áp dụng:

1. **Thêm WP-A7** — "Sửa phạm vi kế toán vốn Smart theo tháng", lớp **A — MUST FIX BEFORE
   OFFICIAL RUN**, sở hữu **F-035**. Status `PLANNED` (chưa có file định nghĩa/gate → chưa
   READY). Routing xác nhận lại bằng `routing_engine.py` tại thời điểm áp dụng: **D / Fable / max**.
2. **Dependency bắt buộc mới** — WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**.
3. **WP-A6** — Completion Gate cuối cùng **không được chạy** trước khi WP-A7 DONE; không được
   dùng test fixture suy biến hiện tại để né dependency này.
4. **WP-A5** — measurement tạo trước khi F-035 được sửa **không** được coi là canonical evidence
   cho engine cuối cùng.
5. **WP-C4** — không đóng băng parity JS/Python trên hành vi Smart capital đã xác nhận là sai.
6. **GATE-A** — định nghĩa lại thành `WP-A1…WP-A7 đều DONE`.
7. **T-06** — ghi rõ **hai nhóm prerequisite ĐỘC LẬP**: (A) nội tại = GATE-A gồm WP-A7;
   (B) hạ tầng = BLK-001. Gỡ BLK-001 **không** cho phép chạy T-06 khi GATE-A chưa PASS.
8. **WP-A4** — `MAY PROCEED IN PARALLEL` với WP-A7 về mặt semantic dependency, kèm ba điều kiện
   (xem RCP-002). "Parallel" ở đây là **roadmap parallelism**: không cho phép hai agent đồng thời
   sửa/merge cùng vùng `engine.py` mà không có branch isolation và merge ordering rõ ràng.
9. **WP-A3 giữ nguyên DONE** — không reopen, không sửa Completion Gate đã FROZEN, không làm mất
   evidence E1/E2. Ghi nhận: F-035 tồn tại **trước** WP-A3 và làm giảm **độ lớn** của một số quan
   sát liên quan Smart, nhưng **không invalidate** các kết luận đúng đắn mà WP-A3 đã chứng minh
   trong phạm vi của nó.

### Gate staleness (DEC-009 áp cho F-035)

F-035 có khả năng thay đổi capital allocation, Smart ladder creation, execution behavior,
deployed capital, ETH accumulated và kết quả Gate 1/2/3. Vì vậy **mọi Gate result tạo trước
remediation F-035 phải được coi là STALE / INVALIDATED khi dùng cho verdict**.

Trạng thái hiện tại: **NO CURRENT OFFICIAL RESULT TO INVALIDATE** — chưa từng có official run.
Điều kiện vì thế chuyển thành dependency bắt buộc: **WP-A7 phải DONE trước T-06**.

### Critical path sau RCP-002

```
T-04 ✅
 └─> WP-A3 ✅
      ├─> WP-A4 ✅ ─┐   (DONE tại S009)
      └─> WP-A7 ✅ ─┤
                    └─> WP-A6 ──> GATE-A ──> T-06 ──> WP-B1 ──> T-07 ──> T-11
WP-A5: sau WP-A2 ∧ WP-A3 ∧ WP-A7 — vẫn là prerequisite của GATE-A
WP-A1, WP-A2: prerequisite của GATE-A, không nằm trên chuỗi dài nhất
GATE-A = WP-A1 ∧ WP-A2 ∧ WP-A3 ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 đều DONE
T-06 = GATE-A ∧ T-05 ∧ (BLK-001 đã gỡ)
```

## Current Task Snapshot

Task:
WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả (S005)

Task Mode:
MAJOR (đủ điều kiện MICRO nhưng nâng lên MAJOR theo ghi chú frozen của file task)

Status:
DONE — 6/6 REQUIRED PASS (E1 toàn bộ); Exit Criteria 6/6.

File định nghĩa:
`docs/tasks/WP-D1-no-ky-thuat-khong-anh-huong-hanh-vi.md`

Required Gate Progress:
6 / 6 PASS. Chi tiết evidence trong file task và biên bản
`docs/sessions/S005-wp-d1-debt-cleanup.md`.

Kết quả chính của S005:
- Baseline E0/E1 (HEAD 1f4c2b7) tái hiện đủ 4 finding đúng như S001 mô tả: F-028
  (`expires_at` Smart ladder = `ts+31 ngày`, sai nghĩa nhưng không được đọc), F-029
  (`ladder_completed()` coi PARTIALLY_FILLED là kết thúc, zero caller), F-031 (bộ đếm
  cooldown override đếm theo zone thay vì sự kiện, chỉ dùng chẩn đoán), F-034
  (`_noon_candles` dead code).
- Kiểm tra rủi ro hành vi TRƯỚC khi sửa: xác nhận không finding nào chạm OSCORE/ladder/
  capital/execution/backtest/gate/verdict — không escalation nào kích hoạt.
- Test-first 4 test viết TRƯỚC fix: 4/4 FAIL đúng kỳ vọng → sau fix 4/4 PASS
  (`tests/test_wp_d1_debt_cleanup.py`).
- Remediation tối thiểu: `expires_at` tính đúng cuối accounting month (local);
  `ladder_completed()` bỏ PARTIALLY_FILLED khỏi tập kết thúc; `cooldown_override` đếm
  theo cycle (cờ `override_counted_this_cycle`); xoá `_noon_candles`.
- Toàn suite: **99 passed, 0 failed, 0 skipped** (95 cũ + 4 mới).
- Impact BEFORE/AFTER cùng dataset synth cố định: **toàn bộ 543 purchase record trùng
  khớp bit-for-bit** (so sánh `==` python); `eth_total` không đổi; mọi pool/ladder/
  transition/release giống hệt; **khác biệt DUY NHẤT** là `counters.cooldown_override`
  (tổng sự kiện 35→31) — đúng ngoại lệ đã khai báo trong Completion Gate.
- Không phát hiện finding/risk mới nào.

Primary Agent Tier:
B

Primary Effort:
medium

Model Routing Score:
1.0 (D1 R1 B1 A1 X1) → không floor → B

Effort Routing Score:
1.0 (U1 V1 H1 C1 F1) → không floor → medium

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Escalation Triggers:
- Theo file task WP-A3 (CAPABILITY_CEILING / CONFLICT DETECTED / metric đổi không giải thích
  được / phải chạm capital.py|score.py). Không trigger nào kích hoạt trong S003: một phương án
  thiết kế duy nhất (tách state/label) đạt đồng thời [F1] và vòng đời đóng; mọi sai lệch metric
  giải thích được; không chạm capital.py/score.py.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

### MICRO-GOVDEF-001 — Sửa lỗi so sánh boundary trong routing_engine.py
Status:
DONE

Checklist Reference:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Mô tả ngắn:
`tier_from_score`/`effort_from_score` trong `governance/scripts/governance/routing_engine.py`
dùng so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn, nên một điểm số ở đúng biên
nguyên (ví dụ 2.0) có thể bị tính sai một bậc Tier/Effort do sai số biểu diễn nhị phân
(`1.9999999999999998` thay vì `2.0`). Chi tiết đầy đủ, bằng chứng tái lập:
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`.

Phạm vi được làm rõ tại T-04 (S002), theo đúng câu đã có sẵn trong DEC-008 mục Impact
("`validate_routing.py` cần được cập nhật ở một task riêng — MICRO-GOVDEF-001 hoặc kế tiếp"):
task này bao gồm **cả** `validate_routing.py`, để công cụ chấp nhận một manual override **có ghi
nhận** (kèm `Manual Override` và `Router Raw Output` trong file task) thay vì báo lỗi khớp tuyệt
đối. Đây là làm rõ phạm vi đã được DEC-008 dự liệu, không phải quyết định mới. Việc mở task này
vẫn cần chỉ thị của chủ dự án — xem BLK-003 và DEC-010.

Ràng buộc bắt buộc khi sửa: tổng quát hoá cách so sánh (làm tròn trước khi so sánh, hoặc dùng
epsilon nhất quán với `EPS` đã dùng ở nơi khác trong codebase, ví dụ `capital.py`).
**Không hard-code ngoại lệ riêng cho bất kỳ task nào** (kể cả WP-A2, task đã kích hoạt phát hiện
này).

Đánh giá MICRO eligibility (`TASK_MODE_STANDARD.md`): Difficulty <= 2, Risk <= 2, Blast Radius
<= 2 — không đổi kiến trúc, không đổi auth, không migration, không thao tác phá huỷ dữ liệu.
Đủ điều kiện MICRO. Chấm điểm tham khảo (không bắt buộc với MICRO): D1 R2 B2 A1 X1 → 1.45 → B;
U1 V2 H1 C1 F2 → 1.45 → medium.

Evidence Summary (2026-08-23, chủ dự án phê duyệt PA-1 cho DEC-010):

**Compact Ready Gate** (`MICRO_TASK_CHECKLIST.md`) — đủ điều kiện, xác nhận lại khi mở: yêu cầu rõ
ràng (sửa boundary comparison + validator override); Risk 2 <= 2; Blast Radius 2 <= 2; không đổi
kiến trúc/auth/schema/thao tác phá huỷ; phạm vi hẹp và đã biết (`routing_engine.py`,
`validate_routing.py`, test governance mới); phương pháp kiểm chứng đã biết (brute-force toàn không
gian đầu vào + test override tổng hợp).

**Compact Completion Gate:**
- [x] Hành vi dự định đã cài đặt — `routing_engine.py` làm tròn `model_score`/`effort_score` về 3
  chữ số **trước khi** so sánh biên (căn cứ: trọng số chỉ có tối đa 2 chữ số thập phân, nên làm
  tròn 3 chữ số loại bỏ đúng nhiễu IEEE-754 ~1e-15, không đổi giá trị thật) — không phải epsilon
  tuỳ tiện, không hard-code WP-A2 hay bất kỳ task nào.
- [x] `validate_routing.py` chấp nhận manual override có ghi nhận (decision reference tồn tại
  trong `PROJECT_DECISIONS.md`, `Router Raw Output` xác thực khớp router hiện tại, chỉ được leo
  thang Tier/Effort chứ không hạ) — hàm `check_override`, tổng quát cho mọi `DEC-###`.
- [x] Verification thực sự chạy: brute-force toàn bộ 5^5 × 5^5 tổ hợp đầu vào cho **0** lệch còn
  lại; `governance/scripts/governance/test_routing_engine.py` — **37/37 check PASS**, gồm 6 ca
  override hợp lệ/không hợp lệ tổng hợp (không phụ thuộc WP-A2).
- [x] Evidence ghi theo `EVIDENCE_STANDARD.md`, mức E1 (chạy thật): xem
  `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- [x] Không mở rộng phạm vi ngoài dự kiến — `git diff` xác nhận chỉ chạm
  `governance/scripts/governance/routing_engine.py`, `validate_routing.py` (thêm), file task
  `WP-A2` (chỉ bổ sung ghi chú, không xoá dấu vết), và các artifact governance liên quan. Không
  chạm `src/`, `webapp/`, `tests/`, `docs/spec/`.
- [x] Regression liên quan đã PASS: `routing_engine.py`/`validate_routing.py` chạy lại trên toàn bộ
  16 file MAJOR task hiện có — **đúng một dòng đổi** (WP-A2, Tier B → C), không task nào khác đổi
  Tier/Effort. `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
  override(s))`.
- [x] `PROJECT/PROJECT_PROGRESS.md` inline Micro Task entry được cập nhật — mục này.

**Kết quả:** BLK-003 RESOLVED. GOV-RSK-001 CLOSED. WP-A2 chuyển `BLOCKED` → `READY`, giữ nguyên
Tier C / Opus / Effort high (nay route tự nhiên, không cần override — nhưng dấu vết DEC-008/Manual
Override/Router Raw Output trong file WP-A2 được **giữ nguyên**, không xoá).

Chi tiết đầy đủ: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
Test: `governance/scripts/governance/test_routing_engine.py`.

## Active Blockers

### BLK-001 — Không có đường tới dữ liệu Binance từ môi trường phát triển
Ảnh hưởng: **chỉ T-06** (RCP-001 xác định lại: không work package nào trong 15 gói lớp A/B/C/D
cần dữ liệu Binance thật — toàn bộ phát triển và kiểm chứng được trên dữ liệu tổng hợp theo
DEC-003). T-06 là điểm duy nhất trên đường găng cần blocker này được gỡ; T-07 và T-11 chỉ bị
chặn gián tiếp qua chuỗi phụ thuộc vào T-06, không phải trực tiếp bởi BLK-001.

Mô tả: Repo chưa từng có official run (`results/` không tồn tại và nằm trong `.gitignore`).
Môi trường phát triển bị chặn egress tới Binance, nên mọi kiểm chứng trong repo chạy trên dữ
liệu tổng hợp và tự gắn cờ `official: false`.
Đường xử lý đã được `docs/DATA_SOURCES.md` chấp nhận: chạy `ethdca fetch` trên máy của chủ dự án
hoặc VPS nước ngoài, copy `data/raw/` về, rồi xác minh bằng cách chạy `ethdca freeze` ở cả hai
máy và đối chiếu hash manifest phải trùng khớp.
Cần từ chủ dự án: một máy hoặc VPS truy cập được `data.binance.vision` và `api.binance.com`.

Bằng chứng E1 thu tại S000 (2026-08-23): cả ba host đều bị chặn ở tầng proxy, không phải lỗi
cấu hình phía repo.
`api.binance.com` → `curl: (56) CONNECT tunnel failed, response 403`
`data-api.binance.vision` → `curl: (56) CONNECT tunnel failed, response 403`
`api.coingecko.com` → `curl: (56) CONNECT tunnel failed, response 403`
PyPI thì thông, nên đây là chặn có chọn lọc theo host, không phải mất mạng.

Không bypass BLK-001. Không đổi nguồn dữ liệu. Không dùng dữ liệu tổng hợp để tạo official
verdict.

### BLK-003 — RESOLVED (`validate_routing.py` chưa biểu diễn được manual override đã được phê duyệt)
Trạng thái: **RESOLVED — 2026-08-23, tại MICRO-GOVDEF-001.**
Ảnh hưởng khi còn mở: **chỉ WP-A2**.

Mô tả: `governance/scripts/governance/validate_routing.py` so khớp **tuyệt đối** giữa
`Primary Agent Tier` trong file task và kết quả của `routing_engine.py`. Khi T-04 soạn file định
nghĩa cho WP-A2 với Tier C theo DEC-008, validator báo:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây **không phải defect mới**. DEC-008 mục Impact đã ghi trước rằng tình huống này sẽ xảy ra và
rằng `validate_routing.py` "cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để
chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối". T-04 làm đúng phần được giao và
không làm phần được giao cho task khác.

Vì sao nó chặn WP-A2: `CLAUDE.md` mục "Every Implementation Session" điểm 9 yêu cầu
`validate_routing.py` **PASS trước khi thực thi** một MAJOR task; `ROADMAP_SYNC_STANDARD.md` cũng
yêu cầu chạy validator này trước roadmap sync. Vì vậy WP-A2 giữ trạng thái `BLOCKED` cho tới khi
điều kiện được gỡ.

Đường gỡ (cần chủ dự án quyết định — xem DEC-010):
1. Cho phép mở `MICRO-GOVDEF-001` (đã mở rộng phạm vi để phủ cả `validate_routing.py`), hoặc
2. Miễn trừ bằng văn bản, ghi vào `PROJECT/PROJECT_DECISIONS.md`.

**Không được gỡ bằng cách hạ Tier WP-A2 về B** — DEC-008 cấm, và làm vậy là hạ tiêu chuẩn để
validator xanh.

Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-02.

**Cách đã gỡ (2026-08-23):** chủ dự án phê duyệt **PA-1**. `routing_engine.py` được sửa tổng quát
(làm tròn điểm số về cùng độ chính xác hiển thị trước khi so sánh biên); `validate_routing.py` được
bổ sung cơ chế chấp nhận manual override có ghi nhận. Sau fix, `validate_routing.py` PASS cho toàn
bộ 16 file MAJOR task, và WP-A2 route Tier C **tự nhiên** (không cần nhánh override nữa, dù nhánh đó
đã được xây và kiểm chứng độc lập cho các trường hợp tương lai). Không hạ Tier WP-A2 về B.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution";
`MICRO-GOVDEF-001` ở mục "Micro Tasks (Inline)".

### BLK-002 — Tính năng cảnh báo chưa được đặc tả
Ảnh hưởng: T-10, và là lý do T-08 tồn tại.
Mô tả: `docs/spec/01_PRODUCT_SPEC_V2_1_5.md` không có mục nào về alert/cảnh báo/notification.
Product Spec chỉ quy định trạng thái hiển thị thụ động trên hero khi mở trang (§11–§13).
Implementation Plan §9 hoãn có chủ đích: "không cần cron cho tới khi thực sự cần notification".
Điều kiện kích hoạt thì đã có đầy đủ trong Strategy Spec (§3, §4, §5, §9, §10, §15, §17, §18)
và danh mục 30 reason code ở Strategy §20 chính là bộ khung tự nhiên cho danh sách cảnh báo.
Nghĩa là: đây là khoảng trống ĐẶC TẢ, không phải khoảng trống code. Không thể triển khai đúng
trước khi đặc tả xong (T-08).

## Active Risks

### RSK-001 — Mất lịch sử giao dịch thật (mức: cao)
App web hiện lưu state trong localStorage của trình duyệt cộng cơ chế tự xuất bản lại trang.
Đây không phải "một database" như Implementation Plan §9 yêu cầu. Xóa dữ liệu site, dùng cửa sổ
riêng tư, đổi máy, hoặc publish thất bại đều có thể làm mất dữ liệu chưa xuất ra ngoài.
Giảm thiểu: T-09B. Cho tới khi T-09B xong, chủ dự án nên xuất file JSON định kỳ.
**Cập nhật 2026-09-02 (`DEC-019`)**: nền tảng giảm thiểu đã được chốt là **Firebase**; T-09B có Task Spec
và Completion Gate FINALIZED (`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`). Risk **CHƯA giảm** — chưa
một dòng production nào đổi. T-09B vẫn `PLANNED`, chờ `OD-A`/`OD-B`/`OD-B2`. Khuyến nghị xuất JSON định kỳ
vẫn còn nguyên hiệu lực.
**Cập nhật 2026-09-02 (`DEC-020`)**: `OD-A`/`OD-B`/`OD-B2` đã RESOLVED (Firebase Hosting · Cloud
Firestore · Anonymous Auth). Phát hiện khe mới `OD-C`: kịch bản **"đổi máy"** nêu tên ngay trong risk này
cần thêm một quyết định (recovery credential hay chấp nhận giới hạn) trước khi coi là được đóng bằng
đường Firebase Auth thuần. Risk **VẪN CHƯA giảm** — chưa một dòng production nào đổi. Khuyến nghị xuất
JSON định kỳ vẫn còn nguyên hiệu lực, đặc biệt trước khi đổi máy.
**Cập nhật 2026-09-02 (`DEC-021`)**: `OD-C` đóng = **R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)** — chủ dự
án chấp nhận rằng kịch bản **"đổi máy"** (và đổi trình duyệt, mất browser profile) sẽ **KHÔNG** tự phục
hồi qua Firebase Auth trong V1 (`H-23`, OUT OF SCOPE V1). Lối thoát cho kịch bản này VẪN LÀ xuất JSON
thủ công — khuyến nghị này **không đổi và quan trọng hơn trước**, vì đây nay là cách DUY NHẤT đóng đúng
kịch bản "đổi máy" ở V1. Kịch bản "xoá dữ liệu site (chỉ localStorage/sessionStorage)" và "publish thất
bại" (nay là "Firebase write thất bại") vẫn được T-09B đóng qua đường Firestore một khi implementation
hoàn tất — risk **VẪN CHƯA giảm** cho tới khi đó, vì chưa một dòng production nào đổi. `T-09B` nay
`READY`, Completion Gate FROZEN 16/16 REQUIRED.
**Cập nhật 2026-09-02 (S014 — T-09B IMPLEMENTED)**: giảm thiểu đã được **cài đặt** (`a19d3ad`) và
**kiểm chứng E1 trên Firebase Emulator Suite**: xoá `localStorage`+`sessionStorage` vẫn phục hồi sổ
từ Firestore (CHECK-03); đóng/mở lại trình duyệt cùng profile vẫn tiếp tục (CHECK-04); ghi thất bại
/ mất mạng hiện rõ, không báo "đã lưu" giả, giữ bản local để cứu (CHECK-10); bản bền hỏng không bị
nạp, không bị ghi đè (CHECK-12); hai tab không ghi đè lẫn nhau (CHECK-16). Risk **CHƯA giảm trên
thực tế** vì project Firebase thật chưa tồn tại và chủ dự án vẫn đang ở bản artifact cũ — giảm khi
(a) thiết lập xong theo `webapp/README.md`, (b) dữ liệu cũ được export/import sang app Firebase,
(c) chuỗi CHECK-01/02/03/04/14 được lặp lại bằng tay trên app thật. Kịch bản "đổi máy" vẫn mở theo
`H-23` (export/import JSON). Risk KHÔNG tự đóng — thẩm quyền chủ dự án.

### RSK-002 — Hai bản cài đặt chiến lược trôi khỏi nhau (mức: cao) — S001 XÁC NHẬN (E1)
Implementation Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Trang
tĩnh không chạy được Python nên `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả.
Cơ chế chặn hiện có là parity check OSCORE 40 ngày (lệch tối đa 7.4e-11 lần kiểm gần nhất),
nhưng parity chỉ phủ OSCORE tổng — chưa phủ unlock, spacing, phân bổ ladder, invalidation,
regime. Mỗi tính năng port thêm sang JS sẽ mở rộng bề mặt trôi nhanh hơn khả năng phát hiện.
Giảm thiểu: **WP-C4** (RCP-001) — mở rộng phạm vi parity trước khi port thêm.

### RSK-003 — Ba lỗi kế toán trong app web (mức: CAO — hai trong ba XÁC NHẬN LÀ LỖI THẬT) — WP-C1 XÁC NHẬN (E1)
Ghi nhận ban đầu từ việc đọc code: (a) hàm chọn tháng hiện hành trả về tháng có key lớn nhất
chứ không phải tháng của ladder, nên release vốn có thể trả nhầm pool khi có nhiều tháng;
(b) mức unlock không giới hạn số vốn được reserve; (c) trạng thái dữ liệu INVALID không chặn
tạo action mới như Strategy §3 yêu cầu.

**Cập nhật WP-C1 (2026-09-02) — kết luận E1 bằng ca kiểm thử chạy thật, không đọc code suông**
(`webapp/test_v01_v02_v03.js`, `webapp/test_multi_month_invariant.js` — output đầy đủ trong
`docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md`):

- **(a) V-01 — XÁC NHẬN LÀ LỖI THẬT.** Ca kiểm thử đa tháng (ladder tháng A + ladder riêng
  tháng B, huỷ ladder tháng A khi tháng B đang là `currentMonth()`) cho thấy `releaseLadder()`
  (`webapp/app_logic.js:302-322`) cộng nhầm vốn vào `smart.a` tháng B đồng thời rút nhầm từ
  `smart.r` đang backing ladder RIÊNG, còn ACTIVE, của tháng B — trong khi `smart.r` của tháng
  A (nơi vốn thực sự bị reserve) không hề giảm, tức KẸT VĨNH VIỄN. Tái hiện được cả bằng thao
  tác Hủy thủ công lẫn qua luồng invalidation tự động (2 daily close liên tiếp trên
  invalidation price).
- **(b) V-02 — XÁC NHẬN LÀ LỖI THẬT.** Với Smart unlock đo được = 0,0% (OSCORE thật của seed),
  `reserveFor()` (`webapp/app_logic.js:289-297`) vẫn cho reserve 100% Smart available — không
  hề so sánh với `view.smartUnlock`. Vi phạm trực tiếp Strategy §12 "Không được reserve vốn
  chưa unlock".
- **(c) V-03 — BÁC BỎ về hành vi quan sát được, nhưng an toàn một cách TÌNH CỜ, không phải do
  chủ đích.** Toán học của `engine.js` khiến `data_quality = INVALID` (cần <7 ngày lịch sử) và
  `adr30` hữu hạn (cần ≥30 ngày) không bao giờ cùng đúng, nên `createLadder()` luôn bị chặn bởi
  guard ADR30 trước khi có cơ hội tạo ladder khi INVALID — dù `createLadder()` không hề kiểm
  tra `data_quality`. Ghi HARDENING (không BLOCKING) vì cơ chế bảo vệ này dễ vỡ nếu spacing
  logic thay đổi độc lập với data quality sau này — xem `PROJECT/HARDENING_BACKLOG.md`.

**Escalation đã kích hoạt theo đúng trigger của WP-C1 và T-03**: NV-1/NV-2 (=V-01/V-02) là lỗi
thật → nếu app đang được dùng để ghi tiền thật, phải dừng dùng hoặc xuất dữ liệu ra ngoài trước
khi tiếp tục, cho tới khi **T-09A** vá xong. Severity nâng lên **HIGH**.

Sửa: **T-09A** (đã có phạm vi xác định — xem mục T-09A trong roadmap).

**Cập nhật T-09A (2026-09-02) — hai lỗi ĐÃ VÁ, escalation GỠ; risk hạ xuống mức thấp, CHƯA
đóng.** Bằng chứng E1 chạy thật trên đường sản phẩm
(`webapp/test_t09a_accounting.js`, 68 assertion — **17 FAIL trước vá, 0 FAIL sau vá**;
`docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`; `docs/reviews/T-09A-batch-review.md`):

- **(a) V-01 — ĐÃ VÁ.** Ladder nay mang tháng sở hữu tường minh (`L.month`) ghi ngay tại lúc
  reserve; release VÀ deploy đều quay về đúng pool tháng đó. Reproduction gốc của WP-C1
  (`test_v01_v02_v03.js::testV01`) chạy lại cho **BÁC BỎ**: huỷ ladder tháng A trả 1.000.000 đ
  về đúng `smart.a` tháng A, pool tháng B (đang backing một ladder ACTIVE riêng) không đổi một
  đồng. Ca đa tháng của `test_multi_month_invariant.js` cũng hết kẹt vốn (`smart.r` tháng 1 về
  0 sau invalidation, trước đây kẹt 1.755.550 đ).
- **(b) V-02 — ĐÃ VÁ.** `reserveFor()` nay áp đúng công thức của
  `capital.py::smart_reservable`. Với Smart unlock = 0,0% thì reserve bị TỪ CHỐI hoàn toàn và
  pool không bị đụng (fail closed, không side effect); biên trên kiểm tại 101% / 99,9% hạn
  mức; hạn mức trừ dần phần đã reserve/deploy trong tháng. Reproduction gốc cho **BÁC BỎ**.
- **(c) V-03 — KHÔNG ĐỔI.** Vẫn BÁC BỎ, `H-18` giữ nguyên DEFERRED: ba điều kiện re-trigger
  đều không xảy ra (`webapp/engine.js` 0 dòng đổi).

Vì sao **chưa đóng RSK-003** ở phiên này: `STATE_AUTHORITY.md` dành `DONE` cho chủ dự án, và
risk này gắn với `T-09A` + `T-03` — cả hai chưa được chủ dự án chuyển trạng thái. Escalation
"dừng dùng app với tiền thật" thì **gỡ được ngay**: hai đường làm sai sổ đã bị chặn và có test
hồi quy giữ chúng. Lưu ý dữ liệu cũ: state đã lưu TRƯỚC bản vá có thể đã sai sẵn do V-01/V-02;
bản vá KHÔNG migrate và KHÔNG sửa lịch sử — chủ dự án cần tự đối chiếu sổ. Ladder tạo trước
bản vá được suy luận tháng sở hữu và ĐƯỢC BÁO HIỆN bằng banner trên app.

### RSK-004 — Bộ test app web không chạy được từ bản checkout sạch (mức: trung bình) — S001 XÁC NHẬN (E1); **ĐÃ KHẮC PHỤC tại WP-C1 (2026-09-02)**
Bằng chứng E1 tại S000: hai test webapp **chạy được và cho kết quả đúng**, nhưng chỉ sau khi
dựng thủ công hai thứ không có trong repo — `webapp/app_final.html` (phải build) và
`demo/results3/live_seed.json` (**không tồn tại ở bất kỳ đâu trong repo**).
Nghĩa là không ai clone repo về mà chạy được test của app, và không có gì bảo vệ hồi quy tự động.

Ghi nhận thêm: hai test ghi ảnh chụp màn hình vào thư mục làm việc hiện hành. Nếu chạy từ trong
`webapp/` sẽ để lại `app-dash.png` và `app-zone.png` trong repo, mà hai file này không nằm trong
`.gitignore`.

**Cập nhật WP-C1 (2026-09-02) — RESOLVED, bằng chứng E1 chạy thật từ bản checkout sạch mô
phỏng** (xoá toàn bộ artifact sinh ra, làm lại từ đầu chỉ bằng lệnh trong repo):
`webapp/package.json` (mới, ghim `playwright@1.56.1`) + `npm --prefix webapp install` →
`ethdca synth` + `ethdca export-live --out-dir demo/results3` (dữ liệu DEMO/SYNTHETIC) →
`node webapp/build_app.js` → `npm --prefix webapp test` (4 test: `test_app.js`, `test_zone.js`,
`test_v01_v02_v03.js` mới, `test_multi_month_invariant.js` mới) — exit code 0, không page
error. `build_app.js`/`test_*.js` chuyển từ path tương đối theo `process.cwd()` sang
`__dirname` nên chạy đúng dù gọi từ gốc repo hay từ trong `webapp/`. Ảnh chụp màn hình
(`app-dash.png`, `app-zone.png`) và `app_final.html` nay nằm trong `.gitignore`;
`git status --porcelain` sau khi chạy test không xuất hiện file nào trong số đó. Đóng F-027.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình) — S001 XÁC NHẬN VÀ MỞ RỘNG (E1)
S001 xác nhận và phát hiện quy ước không được ghi ở nhiều chỗ hơn dự kiến: ngoài ánh xạ
gate-fail → verdict, còn có ngưỡng số tự đặt của FS-02/FS-07/FS-12, phạm vi tính FS-03/FS-07 chỉ
trên window W5, và tham số `shift_days=10` của Control G. `verdict.py` còn ghi rằng ánh xạ được
tài liệu hoá ở `docs/CONVENTIONS.md`, nhưng file đó không có mục nào về verdict.
Xem finding F-015, F-016, F-026. Giảm thiểu: **WP-B1** (RCP-001).

`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ để không bị coi nhầm là điều
khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

### RSK-006 — Không ghim phiên bản thư viện, nên kết quả không tái lập được theo thời gian (mức: cao) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: `pyproject.toml` chỉ đặt sàn (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không có lockfile và không có trần. Khi cài mới, pip kéo về `numpy 2.4.6`,
`pandas 3.0.5`, `pyarrow 25.0.1` — vượt xa sàn tới hai thế hệ lớn. Toàn bộ 69 test vẫn PASS
trên bộ này, đó là tín hiệu tốt về độ bền, nhưng là **may mắn chứ không phải bảo đảm**.

Vì sao mức cao: Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu —
"cùng dataset hash + config hash + manifest hash + seed thì tái lập chính xác cùng kết quả".
Run record hiện lưu hash của config, manifest, dataset và seed, **nhưng không lưu phiên bản thư
viện**. Một thay đổi dấu phẩy động trong numpy/pandas ở phiên bản sau có thể làm official run
không tái lập được, mà không ai phát hiện — vì mọi hash đầu vào vẫn trùng khớp.

Giảm thiểu: **WP-A1** (RCP-001) — thay thế T-06A, đóng đủ cả 8 trường provenance yêu cầu
(Python version, dependency/lock hash, git commit SHA, dataset hash, strategy config hash,
execution config hash, manifest hash, seed), không chỉ ghim thư viện.

### RSK-007 — Pipeline không chạy nhiều hạng mục mà spec ghi là bắt buộc cho official run (mức: cao) — **GIẢM THIỂU MỘT PHẦN tại S006 (WP-A2 DONE); còn mở phần WP-A5**
**Cập nhật S006 (2026-08-24):** WP-A2 (DONE) đã đấu nối **toàn bộ** phần thuộc quyền sở hữu của
nó: Benchmark B/C/D (F-003), ablation §2.3 + volume z-score §2.4 kèm bảng chênh lệch (F-004),
bảng coverage §4 (F-012), XIRR §16 (F-013), bootstrap 1000/block length cho official (F-014).
Bằng chứng E1: 9 test wiring chạy `run_gate1` thật (8 FAIL trước fix → 9/9 PASS sau fix), spy
đo trực tiếp `n_sims` 200→1000; đấu nối KHÔNG đổi kết quả chiến lược/Benchmark A (159 trường
metric, 0 khác biệt). Nguyên tắc BT §22 nay áp dụng được.
**Phần CÒN MỞ:** ba Failure Signal (FS-02, FS-06, FS-12) vẫn không được truyền input nên luôn
UNKNOWN — thuộc **WP-A5** (chưa bắt đầu). Risk chỉ đóng hoàn toàn khi WP-A5 DONE.

Nội dung gốc S001 (giữ nguyên để audit) — S001 phát hiện (E1): Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng coverage §4 và
XIRR §16 đều đã được cài đặt đúng nhưng **không nơi nào trong pipeline gọi chúng**. Hệ quả: một
official run sẽ phát ra verdict kèm báo cáo thiếu, và nguyên tắc Backtest §22 ("luật đơn giản
thắng nếu kết quả tương đương") không thể áp dụng vì không có B/C/D để so.
Ngoài ra ba Failure Signal (FS-02, FS-06, FS-12) không bao giờ được truyền input nên luôn UNKNOWN,
trong khi verdict BUILD vẫn phát ra bình thường.
Xem finding F-002, F-003, F-004, F-012, F-013. Giảm thiểu: **WP-A2, WP-A5** (RCP-001).

### RSK-008 — Run trên dữ liệu tổng hợp vẫn được ghi nhận là official (mức: cao) — S001 XÁC NHẬN (E1)
S001 xác nhận (E1): cờ `official` chỉ phụ thuộc việc có dùng `--dev-limit` hay không, hoàn toàn
không kiểm nguồn dữ liệu; và `lineage.json` ghi `source` là chuỗi cố định `'see fetch/synth'` cho
cả dữ liệu thật lẫn dữ liệu tổng hợp. Chạy `ethdca synth && ethdca run all` sẽ tạo record mang
`official: true` trên dữ liệu nhân tạo, không có trường nào cho phép phát hiện về sau.
Đây là rủi ro thẳng vào tính toàn vẹn của verdict — tức vào chính cổng mở đường cho app.
Xem finding F-005. Giảm thiểu: **WP-A1** (RCP-001).

### RSK-009 — Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn (mức: cao) — ĐÃ REMEDIATE tại S003 (WP-A3)
S001 phát hiện và kiểm chứng bằng chạy thật (E1): khi giai đoạn RECOVERY kết thúc lúc thị trường
còn yếu, regime chuyển thành STRESSED chứ không phải NORMAL, nên nhánh dọn Crash ladder ở
`engine.py:415` không bao giờ chạy. Reserve của Crash zone không được giải phóng, kéo theo không
tạo được ladder mới và cash ratio tăng giả tạo — có thể bóp méo chính FS-02 và FS-07.
Đây đồng thời là vi phạm [F1] (STRESSED phải không có hiệu ứng execution).
Xem finding F-001. Giảm thiểu: **WP-A3** (RCP-001).

**Cập nhật S003 (2026-08-23): CLOSED.** WP-A3 (DONE) đã tách trạng thái nền khỏi nhãn STRESSED
(`RegimeTracker.state`/`.label`, CONVENTIONS #14) và nhánh dọn chạy cho MỌI kết cục kết thúc
Recovery; bằng chứng E1: baseline tái hiện lock 27.2 đơn vị trước fix → 0 sau fix, chuỗi test
CHECK-A3-01/02, suite 87 PASS; E2 độc lập PASS — reviewer tự dựng kịch bản khác (kẹt 18.7 trên
code cũ, release đủ trên code mới) và không tìm thấy đường khoá vốn mới sau 4 kịch bản tự nghĩ.

### RSK-010 — Phạm vi kế toán của Smart unlock sai: Smart ladder ngừng hình thành từ tháng thứ ba (mức: cao) — **CLOSED (F-035 RESOLVED tại S004)**
Trạng thái: **CLOSED 2026-08-24** — WP-A7 DONE qua Completion Gate frozen (12/12 REQUIRED
PASS, E2 độc lập PASS WITH FOLLOW-UPS). Lịch sử xác nhận defect giữ nguyên bên dưới.

**Cập nhật S004 (2026-08-24): CLOSED.** WP-A7 (DONE) đưa kế toán Smart về đúng phạm vi
accounting month (PA-A — bộ đếm tháng trong `Pool` + một hook mở sổ tại rollover;
CONVENTIONS #17), giữ nguyên ledger audit lifetime DM §6. Bằng chứng E1: unit+engine
nhiều tháng (quyền tháng mới trọn vẹn ở unlock 1.0, 4/4 rồi 5/5 tháng đều tạo ladder),
suite 95 PASS; impact: Smart qua ladder 0.0208% → 24.49%, snapshot [F5] sống lại phần
Smart; E2 độc lập tái lập toàn bộ và tự dựng counterexample (probe3, probe5a/b): không
đường khoá/rò vốn mới, worst over-grant = +0.000000. Chiều `smart_unlock_mode` hết chết
cơ học (phân kỳ quyền vốn ở test C; phân kỳ tới tận eth_total ở probe3 của reviewer).
Giới hạn còn lại ở tầng outcome trên full synth → PH-04 (ngoài scope, chờ chủ dự án).

Nội dung dưới đây là hồ sơ trạng thái TRƯỚC khi đóng (giữ nguyên để audit):
Finding chính thức: **F-035** · Severity **HIGH** · Evidence **E1** (chứng minh cấu trúc + chạy
thật), có xác nhận độc lập kế thừa từ reviewer E2-WP-A3-001.

`smart_reservable` so ngân sách Smart **theo tháng** với `pool.deployed` **luỹ kế toàn đời**
(`Pool` không có vòng đời tháng, trong khi Data Model §5 `monthly_budgets` định nghĩa
`smart_available/reserved/deployed_vnd` là trường của bản ghi **tháng** có `status OPEN/CLOSED`).
Vì Month-End (ST §10) giải ngân hết phần Smart mỗi tháng, `deployed` tăng ~một ngân sách tháng
mỗi tháng ⇒ từ tháng thứ ba hàm trả **0 tất định, vĩnh viễn, không phụ thuộc dữ liệu**, kể cả ở
`SMART_UNLOCK = 1.00`.

Hệ quả đo được (90 tháng dữ liệu tổng hợp): **2** Smart ladder; **99,98%** vốn Smart bỏ qua cơ
chế ladder (ST §12) và chảy qua luật phần dư cuối tháng; **chiều `smart_unlock_mode` — 1 trong 8
chiều bắt buộc của Gate 2 (BT §9) — trơ hoàn toàn**, ba mode HWM/NO_HWM/DECAY_HWM cho kết quả
**trùng khít bit-for-bit** trong khi ST §6 yêu cầu báo cáo đóng góp riêng từng mode; snapshot
[F5] của Crash ladder bị triệt tiêu phần Smart (che ~78% tác dụng thật của remediation F-021 vừa
xong ở WP-A3).

**Official backtest KHÔNG đáng tin trước khi sửa** (Gate 1/2/3 đều đo trên engine mà 30% vốn
không đi qua cơ chế được đặc tả). Áp dụng **DEC-009**: mọi kết quả Gate 1 tạo trước remediation
là STALE/INVALIDATED — hiện `no current result to invalidate` (chưa từng có official run), nên
điều kiện chuyển thành dependency bắt buộc: **phải DONE trước T-06**.

Tồn tại **trước** WP-A3, **không phải hồi quy** của WP-A3; WP-A3 giữ nguyên DONE và gate FROZEN.
Ownership: **WP-A7** (lớp A, đường găng, D/Fable/max) — **ĐÃ CHỐT**: RCP-002 được chủ dự án phê
duyệt kèm điều kiện và **đã áp dụng** vào bảng roadmap chuẩn ngày 2026-08-24. WP-A7 là
prerequisite của WP-A5, WP-A6, WP-C4, GATE-A, T-06.
Trạng thái risk (lịch sử): CONFIRMED DEFECT — OPEN, sẽ đóng khi WP-A7 DONE → **đã đóng
tại S004 như ghi ở đầu mục**.

Triage đầy đủ (requirement canonical, root cause, bằng chứng, phân lớp, ảnh hưởng gate, đánh giá
WP-A4): `docs/reviews/PH-03-triage-smart-unlock-scope.md`.

### PH-04 — Ba mode `smart_unlock` phân kỳ ở tầng quyền vốn nhưng vẫn trùng kết quả cuối trên full run (GHI NHẬN S004 — chờ chủ dự án, CHƯA triage, KHÔNG remediation)

Phát hiện trong S004 (WP-A7), **ngoài Scope Lock**, ghi nhận theo đúng quy trình
"phát hiện mới không sửa trong phiên":

Sau khi F-035 được sửa, ba mode HWM / NO_HWM / DECAY_HWM đã **phân kỳ thật** ở tầng
unlock path và quyền vốn (`smart_reservable` cuối kịch bản tất định: 14.36 / 11.36 / 0.00
— test C của WP-A7), tức chiều ablation không còn chết cơ học theo đúng câu chữ
CHECK-A7-03. Tuy nhiên trên **full synthetic run 90 tháng**, ba mode vẫn cho `eth_total`
trùng **bit-for-bit** (21.637034604792). Nguyên nhân cấu trúc (E1, đã xác minh bằng probe):
engine hiện chỉ **tiêu thụ** `effective_unlock` tại đúng hai điểm — (a) tạo Smart ladder
one-shot ở lần eff > 0 đầu tiên trong tháng, nơi peak == current nên ba mode cho cùng giá
trị (CONVENTIONS #1); (b) crash snapshot [F5], nơi OSCORE ≥ 75 ⇒ smart_unlock = 1.0 ở mọi
mode. ST §6 yêu cầu ba mode nằm trong Gate-2 ablation với "báo cáo đóng góp riêng" (BT §9)
— muốn chiều này phân biệt được ở tầng OUTCOME cần một kênh tiêu thụ unlock **liên tục
trong tháng** (ví dụ top-up/resize ladder khi eff tăng), là thay đổi hành vi engine nằm
ngoài phạm vi WP-A7 (phạm vi kế toán) và không được đặc tả tường minh trong V2.1.5.

Phương án thuộc thẩm quyền chủ dự án: (1) mở WP mới trong lớp A/B; (2) chuyển WP-D2 đề
xuất V2.2; (3) chấp nhận như giới hạn đã biết của Gate-2 ablation dimension này. Chi tiết:
`docs/sessions/S004-wp-a7-monthly-smart-scope.md` mục "PH-04".

**Tinh chỉnh của reviewer E2 (F-E2A7-03, 2026-08-24):** hai mệnh đề đỡ của PH-04 là
thuộc tính CỦA DATASET, không phải bất biến cấu trúc — reviewer tự dựng được kịch bản
(crash chiếm vốn làm hoãn tạo ladder qua thời điểm phân kỳ) trong đó 3 mode phân kỳ tới
tận `eth_total` NGAY với engine hiện tại; và "crash snapshot ⇒ 1.0 mọi mode" cần thêm
điều kiện `dq != INVALID` tại nến entry. Vậy sức phân giải của chiều này trên dataset
chính thức là câu hỏi EMPIRICAL — nên ĐO trước khi diễn giải `Gate2_PreOOS_PassShare`,
không mặc định chiều này trơ ở tầng outcome. (probe3 trong
`docs/reviews/E2-WP-A7-monthly-smart-scope.md` là mẫu kịch bản tái lập.)

## Active Risks — Governance / Tooling

Rủi ro của bản thân bộ công cụ governance dùng chung, **tách khỏi rủi ro sản phẩm ETH DCA** ở
mục trên. Không tính vào 33 finding của S001.

### GOV-RSK-001 — Sai số biên dấu phẩy động trong routing_engine.py có thể under-route task đúng biên (mức: trung bình) — CLOSED
Phát hiện khi áp dụng RCP-001 (2026-08-23), tái lập được (E1): `tier_from_score` và
`effort_from_score` so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn/chưa có
epsilon. Một task có điểm nền đúng bằng 2.0 (biên Tier B/C) có thể nhận `model_score` nội bộ là
`1.9999999999999998` do cách `0.25*D+0.25*R+0.20*B+0.15*A+0.15*X` cộng dồn sai số nhị phân, và
bị route xuống Tier B thay vì Tier C.

Trường hợp cụ thể đã xác nhận: WP-A2 (D2 R2 B2 A1 X3) — hiển thị `model_score: 2.0` nhưng nội bộ
`1.9999999999999998`, router trả Tier B trong khi bảng `AGENT_CAPABILITY_MATRIX.md` quy định
2.00–2.99 → Tier C.

Ảnh hưởng: bất kỳ task nào (không riêng dự án này) có điểm nền rơi đúng vào các mốc nguyên
0/1/2/3 đều có nguy cơ tương tự, theo cả hai chiều (có thể over-route hoặc under-route tuỳ dấu
sai số). Mức trung bình vì hệ quả là chọn sai một bậc Tier/Effort, không phải sai kết quả tính
toán nghiệp vụ.

Giảm thiểu tạm thời đã áp dụng cho WP-A2: **manual override** theo DEC-008, ghi nhận công khai
trong bảng roadmap.
Giảm thiểu triệt để: **MICRO-GOVDEF-001** — **HOÀN TẤT 2026-08-23**. `routing_engine.py` làm tròn
điểm số về cùng độ chính xác hiển thị trước khi so sánh biên; xác nhận bằng quét toàn bộ 5^5 × 5^5
tổ hợp đầu vào cho 0 lệch còn lại (`test_routing_engine.py`, 37/37 PASS). WP-A2 nay route Tier C tự
nhiên, không cần override. Không task nào khác trong 16 file MAJOR hiện có bị ảnh hưởng.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".

## Open Regression Items
- None ở tầng mã nguồn. S001 không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với
  V2.1.5; bảy sửa đổi F1–F7 đều có dấu vết hiện thực.
- **PH-01 (tài liệu, không phải mã nguồn)** — bảng "Tổng hợp" của `docs/reviews/S001-audit-findings.md`
  ghi MEDIUM 15 và Tổng 33, nhưng đếm thật trên chính danh mục được liệt kê cho **34 định danh
  `F-xxx`** (HIGH 8 + MEDIUM 19 + LOW 7) cộng 3 `S-xxx`. Con số 33 đã được chép sang tài liệu này và
  sang RCP-001. **Không finding nào bị rơi** — RCP-001 §2 và §6 phân đủ 34 `F-xxx` vào 15 gói, và
  T-04 xác nhận 40/40 định danh có nơi thuộc về. T-04 **không tự sửa** con số trong biên bản audit
  của phiên đã đóng; chờ chủ dự án quyết định cách đính chính.
  Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-01.

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)
- DEC-006 — Source of Truth cho compliance audit là V2.1.5, không phải V2.1.3
- DEC-007 — RCP-001 được phê duyệt và áp dụng kèm bốn điều kiện
- DEC-008 — Ghi đè thủ công routing của WP-A2 (Tier C, không dùng Tier B từ router)
- DEC-009 — Quy tắc Gate 1 staleness: remediation ảnh hưởng Gate 1 bắt buộc chạy lại Gate 1
- DEC-010 — RESOLVED: PA-1 phê duyệt cho BLK-003; `routing_engine.py`/`validate_routing.py` đã sửa
- DEC-011 — Owner Product Intent và V1 Daily-Use Acceptance (tiêu chí A–F)
- DEC-012 — Hạn mức repair budget cho CAP-PROV: allowed 2 / used 2 / remaining 0
- DEC-013 — **RESOLVED / INTEGRATED**: phương án A (INTEGRATE NOW); canonical trunk = `main`;
  integration SHA `febc2ec` (merge commit thường, 0 xung đột, tree kết quả TRÙNG KHÍT tree source)
- DEC-014 — `OD-A4-01`: bổ sung MỘT REQUIRED check cho WP-A4 (`CHECK-A4-10`) và làm rõ
  Expected Touch Area; `F-E2A1R3-05` → `CAP-DATA`, hấp thụ vào WP-A4, 0 task ID mới
- DEC-015 — `F-S009-01` → capability owner `CAP-DATA`; spec verdict `IMPLEMENTATION_DEFECT`;
  CONFIRMED BLOCKING V1 giữ nguyên; 0 task ID mới. `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG, còn
  `OWNER_DECISION_REQUIRED` cho phương tiện thi hành
- DEC-016 — `OD-DATA-01`: `F-S009-01` = CONFIRMED BLOCKING V1; phương tiện thi hành được
  duyệt = **REOPEN WP-A4 cho ĐÚNG MỘT repair cycle**, mở touch area tối thiểu sang
  `indicators.py` + wiring/test trực tiếp; 0 task ID mới, 0 WP mới. **GHI NHẬN, CHƯA THI
  HÀNH** — `OWNER_DECISION_REQUIRED` của `DEC-015` nhờ đó ĐÓNG
- DEC-017 — `OD-DATA-02`: `CAP-DATA` Effective Risk = **HIGH**; hạn mức repair budget
  allowed 2 / used 0 / remaining 2 (khai hạn mức, KHÔNG reset). Bản sửa `F-S009-01` sẽ là
  repair cycle **#1**

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- T-09B (SHARED FIREBASE PROJECT / RULES SAFE MERGE — tiếp nối) — 2026-09-02 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `f9330eb`. Owner xác nhận project thật
  (`tinphatcontent`) dùng chung với ứng dụng Content, cung cấp nguyên văn rules Content đang
  chạy. Phân tích: không có collection nào tên `ethdca`, không có catch-all sẵn có — merge an
  toàn bằng cách CHỈ thêm hai khối `match /ethdca/state`/`match /ethdca/seed` (hàm đổi tên
  `isCoinDcaOwner()`), không đụng bất kỳ match/function nào của Content. Dựng
  `webapp/test_shared_rules_merge.js` trên `test_firebase_harness.js` đã có: battery 53 probe
  Content (đọc từ chính rules text, phủ cả 8 collection — vượt yêu cầu tối thiểu `audit_logs`/
  `config`/`users`) chạy trên Firestore Rules Emulator, so BEFORE (rules Content nguyên văn) ==
  AFTER (đã merge) — **0 lệch**, cả 53 probe khớp đúng phân tích rules text. Ma trận CoinDCA 12
  ca (§8 chỉ thị) PASS 12/12, gồm xác nhận owner UID KHÔNG có thêm quyền Content nào ngoài đúng
  mức "signedIn thường" mà Content vốn đã cấp cho MỌI actor. `DEC-023` ghi quyết định + Hosting
  RESOLVED (Owner tự kiểm Console: chưa setup, dùng site mặc định). CHƯA deploy — chờ owner UID
  thật. Evidence: `docs/reviews/T-09B-shared-rules-merge.md`.
- T-09B (REAL FIREBASE SETUP — tiếp nối S014) — 2026-09-02 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `7f78c14`. Mục tiêu: thiết lập Firebase
  project thật + xác minh production reachability. Bước đầu gặp
  `INTEGRATION_DECISION_REQUIRED: loc>5000` (branch authority check) → chủ dự án ACCEPT THE
  DIVERGENCE (`DEC-022`, không merge, không cut scope). Kiểm tra thẩm quyền Firebase CLI:
  `firebase login:list` → "No authorized accounts" — môi trường agent KHÔNG có Firebase
  Console/CLI authority (không trình duyệt, không credential). Theo đúng chỉ thị phiên §3: DỪNG
  ở bước đầu tiên cần Owner thao tác, không tự invent project ID/config/UID. Xem yêu cầu gửi chủ
  dự án ở cuối báo cáo phiên này.
- T-09B (IMPLEMENTATION — S014) — 2026-09-02 — branch `claude/t09b-firebase-implementation-nz50is`
  từ `origin/main` @ `4502ea6`. **IMPLEMENTED** — 16/16 REQUIRED check PASS (E1), toàn bộ qua đường
  sản phẩm (trang build thật → Firebase SDK compat 12.18.0 thật → Firebase Emulator Suite Auth +
  Firestore với đúng `firestore.rules` của repo → nạp lại), bằng chứng phía Firebase đọc độc lập qua
  REST của emulator.
  (1) **Kiến trúc đúng baseline FROZEN**, không thêm thành phần: Hosting (`firebase.json`) · Anonymous
  Auth · Firestore `ethdca/state` + `ethdca/seed` · rules khoá cứng một owner UID (placeholder
  `OWNER_UID_REQUIRED` = mặc định deny), không delete. `localStorage` = mirror/cache.
  (2) **Production diff theo khai báo**: 3 file, +560 / −162 (`app_logic.js` khối persistence/init/
  banner/guard/export-import-wipe; `app_shell.html`; `build_app.js` bỏ nhúng state/quine) + 3 file
  runtime mới chưa trong khai báo (`webapp/firebase_config.js`, `firestore.rules`, `firebase.json` —
  `H-27`). `engine.js`, `src/eth_dca_os/**`, `pyproject.*` = **0 dòng**. Không hàm kế toán nào bị chạm.
  (3) **Test**: `test_firebase_harness.js` (mới) + `test_t09b_persistence.js` (mới, 285 assertion /
  0 FAIL, 14 check trực tiếp); `test_helpers.readState()` đọc bản durable + đối chiếu bit-exact →
  ba test kế toán T-09A chạy nguyên văn trên state đã round-trip (CHECK-09: 68/68; V-01/V-02/V-03
  BÁC BỎ). `npm --prefix webapp test` **6/6 exit 0**.
  (4) **Batch review bắt buộc** → **PASS, 0 CONFIRMED BLOCKING còn lại**: `F-T09B-01` (hai tab cùng
  profile, tab stale ghi đè bản mới hơn — mất dữ liệu âm thầm) phát hiện trong phiên và sửa TRƯỚC
  commit bằng transaction có điều kiện `rev` (cùng lượt, không repair cycle); 4 HARDENING `H-24`
  (trần 1 MiB/document), `H-25` (stale change chỉ trong bộ nhớ tab), `H-26` (`validateState` giả
  định tổng tỷ lệ = 1), `H-27` (ba file runtime mới chưa khai production path). Biên bản:
  `docs/reviews/T-09B-batch-review.md`.
  (5) **Giới hạn bằng chứng (chỉ thị §14)**: project Firebase thật CHƯA tồn tại; emulator không suy
  ra production reachability. CODE IMPLEMENTATION COMPLETE · REAL FIREBASE SETUP REQUIRED · real
  deploy = KHÔNG. Chủ dự án làm 5 bước ở `webapp/README.md` rồi lặp lại CHECK-01/02/03/04/14 bằng
  tay trên app thật trước khi `DONE`.
  (6) Budget `CAP-WEBAPP` 2/0/2 **không đổi** (implementation ban đầu). Task ID mới = 0 (29 = 29 theo danh sách trạng thái đầy đủ; `task_registry_snapshot.sh` báo 28 → 27 vì bỏ sót `IMPLEMENTED` — `H-22`).
  `H-19`, `H-20`, `H-23` không đổi. Không sửa Product Principle, không mở lại quyết định kiến trúc.
  Handoff: `docs/sessions/S014-t09b-firebase-implementation.md`.
- T-09A (REPAIR V-01/V-02) — 2026-09-02 — branch `claude/t09a-accounting-repair-v4ewhq` từ
  `origin/main` @ `814d185`. **IMPLEMENTED** — 12/12 REQUIRED check PASS (E1), toàn bộ bằng
  chứng chạy thật qua đường sản phẩm (UI → `app_logic` → `engine` → state), không gọi trực
  tiếp hàm engine.
  (1) **Test trước, vá sau.** Chạy lại reproduction WP-C1 trên `origin/main` @ `814d185`:
  `BEFORE V-01 = XÁC NHẬN`, `BEFORE V-02 = XÁC NHẬN`. Dựng
  `webapp/test_t09a_accounting.js` (68 assertion, sáu bất biến A–F) và chứng minh nó **FAIL 17
  assertion trên cây chưa vá** trước khi sửa một dòng production nào.
  (2) **Root cause V-01**: ladder không mang tháng kế toán sở hữu vốn; `releaseLadder()` **và**
  `poolFor()` trong `addBuy()` đều dùng `currentMonth()` (key tháng lớn nhất) làm pool đích.
  Sửa: `L.month` ghi tường minh ngay tại lúc reserve; release và deploy đều quay về đúng pool
  đó. Ladder tạo trước bản vá được suy luận tháng từ `L.created` và **được báo hiện bằng
  banner** — không migrate, không ghi đè state.
  (3) **Root cause V-02**: `reserveFor()` chỉ so với available, không tham chiếu unlock. Sửa:
  `smartReservable()`/`oppReservable()` dùng đúng công thức của `capital.py::smart_reservable`
  (unlocked(tháng) − đã reserve − đã deploy trong tháng, kẹp trên bởi available), fail closed
  khi chưa có `view`.
  (4) Bút toán `RELEASE` nay ghi số **thực sự dịch chuyển** (trước ghi số cam kết) và đánh dấu
  `LADDER_RELEASE_SHORTFALL` khi hai số lệch nhau.
  (5) `AFTER V-01 = BÁC BỎ`, `AFTER V-02 = BÁC BỎ` (reproduction gốc của WP-C1, không sửa logic
  kết luận). `test_t09a_accounting.js` **0 FAIL / 68**. `npm --prefix webapp test` 5/5 exit 0.
  `python3 -m pytest -q` **286 passed, exit 0**.
  (6) Diff production theo KHAI BÁO: **1 file, +88 / −16** (`webapp/app_logic.js`).
  `webapp/engine.js`, `src/eth_dca_os/**`, `pyproject.*` = **0 dòng đổi**.
  (7) **Batch review bắt buộc** (Effective Risk HIGH) → **PASS, 0 CONFIRMED BLOCKING**,
  `ELIGIBLE_FOR_FREEZE` (advisory). 4 HARDENING mới: `H-19` (`monthKey()` dùng giờ địa phương),
  `H-20` (đường mua trực tiếp không bị giới hạn unlock), `H-21` (lệnh đo budget trong
  `PRODUCTION_PATHS.md` §1 nuốt file test mà §2 loại trừ), `H-22`
  (`task_registry_snapshot.sh` bỏ sót `IMPLEMENTED`/`VERIFYING` — khiếm khuyết CÓ TRƯỚC phiên
  này, `T-03` đã vắng mặt trong ảnh chụp từ trước). 1 `OUT_OF_SCOPE` → `WP-C4`
  (`F-T09A-03`: thiếu HWM §6 / hysteresis §5 / daily limit §11 — lệch theo chiều CHẶT HƠN).
  Biên bản: `docs/reviews/T-09A-batch-review.md`.
  (8) `H-18` / V-03: **giữ nguyên DEFERRED**, không re-trigger.
  (9) Budget `CAP-WEBAPP`: allowed 2 (default V4.3 theo Effective Risk HIGH — chủ dự án CHƯA
  đặt con số tường minh) / used **0** / remaining 2. Lượt `814d185..d125fe5` là implementation
  ban đầu, không phải repair cycle. Ledger §2.2 mới khởi lập.
  (10) **Task ID mới = 0.** `docs/tasks/T-09A-sua-loi-ke-toan-app-web.md` là Task Spec cho ID
  **đã đăng ký sẵn** trong registry (`CAPABILITY_MODEL.md` §II.5 hình thức 1). Registry đo lại
  bằng tay với danh sách trạng thái ĐẦY ĐỦ: **BEFORE 29 → AFTER 29 task ID, diff RỖNG**; file
  task 20 → 21. (`task_registry_snapshot.sh` báo 28 → 27 vì nó bỏ sót `IMPLEMENTED` và
  `VERIFYING` — `H-22`, khiếm khuyết có trước phiên này.)
  (11) KHÔNG đụng: `WP-A4` (`DONE`), `F-S009-01` (`CLOSED`), `CAP-DATA` (allowed 2 / used 1 /
  remaining 1), `F-S010-03` (`OUT_OF_SCOPE` → `WP-C4`). KHÔNG mở dashboard, `WP-C2`, `WP-A6`,
  KHÔNG chạy `T-06`.
  (12) **Escalation "dừng dùng app với tiền thật" được GỠ** — xem `RSK-003`. Cảnh báo còn lại:
  state đã lưu TRƯỚC bản vá có thể đã sai sẵn; bản vá không sửa lịch sử.
- WP-C1 (STREAM WEB) — 2026-09-02 — branch `claude/wp-c1-web-skeleton-b3oieq` từ `origin/main`
  @ `cb75f9d`. **DONE** — 8/8 REQUIRED check PASS (E1), evidence chạy thật, không đọc code suông.
  (1) F-027 đóng: harness khôi phục từ bản checkout sạch — `webapp/package.json` mới (ghim
  `playwright@1.56.1`), `webapp/build_app.js` + `webapp/test_app.js` + `webapp/test_zone.js`
  chuyển path tương đối theo `__dirname` (trước đó phụ thuộc `process.cwd()`, gãy khi gọi từ
  gốc repo — chính là root cause của F-027 đúng như tên gọi). `demo/results3/live_seed.json`
  sinh bằng `ethdca synth` + `ethdca export-live` (DEMO/SYNTHETIC, không phải Binance thật).
  Ảnh chụp màn hình test (`app-dash.png`, `app-zone.png`) và `app_final.html` thêm vào
  `.gitignore`. (2) Ba nghi vấn kết luận E1 bằng hai test mới —
  `webapp/test_v01_v02_v03.js`, `webapp/test_multi_month_invariant.js`: **V-01 XÁC NHẬN**
  (release đa tháng trả nhầm pool VÀ/HOẶC kẹt vốn vĩnh viễn, tái hiện cả qua Hủy thủ công lẫn
  invalidation tự động), **V-02 XÁC NHẬN** (reserve không bị giới hạn theo unlock — reserve
  100% available dù unlock đo được = 0%), **V-03 BÁC BỎ** (INVALID luôn trùng với ADR30 NaN
  theo toán học của `engine.js` nên `createLadder()` vẫn bị chặn trong mọi trạng thái quan sát
  được — nhưng KHÔNG do một kiểm tra `data_quality` tường minh; ghi HARDENING). (3) `git diff`
  xác nhận `webapp/app_logic.js` và `webapp/engine.js` không đổi một dòng nào (CHECK-C1-07).
  (4) Cập nhật: `RSK-003` (mức trung bình → **CAO**, escalation NV-1/NV-2 = lỗi thật), `RSK-004`
  (RESOLVED), `T-03` `CHECK-03-01` `BLOCKED` → `PASS`, `Status` `BLOCKED` → `VERIFYING`
  (KHÔNG tự đóng `DONE` — ngoài scope WP-C1), `T-09A` `PLANNED` → `READY` với phạm vi xác định
  (sửa `releaseLadder()` dùng đúng tháng gốc của ladder; `reserveFor()`/`createLadder()` phải
  nhân giới hạn unlock). (5) 0 task ID mới tạo, 0 WP mới mở, không mở WP-C2/C3/C4/UI polish/
  auth/mobile/chart task. (6) DATA stream dependency = **KHÔNG** — không chạm
  `src/eth_dca_os/**`, không pull/cherry-pick branch DATA. (7) **Escalation kích hoạt**: V-01 và
  V-02 là lỗi thật — nếu app đang ghi tiền thật, dừng dùng hoặc xuất dữ liệu ra ngoài cho tới
  khi T-09A vá xong.
- Integration (DEC-013) — 2026-09-01 — **governance-only**, integration SHA `febc2ec`.
  KHÔNG sửa production code, KHÔNG sửa test code, KHÔNG mở WP, KHÔNG mở repair cycle,
  KHÔNG tạo task ID, KHÔNG chạy T-06. Kết quả:
  (1) `DEC-013` **RESOLVED / INTEGRATED** theo phương án **A — INTEGRATE NOW**; canonical
  trunk từ đây = **`main`**.
  (2) Đo lại toàn bộ bằng git ngay trước merge: source `claude/wp-a1-provenance-v67k9h` @
  `6372783`; default cũ `claude/plan-tool-from-docs-qijx5m` @ `4a46b3c` (giải bằng GitHub
  API `default_branch`, KHÔNG giả định); merge base `e368425`; ahead 33 / behind 1.
  Chứng minh commit "behind" duy nhất không mang nội dung: `4a46b3c` là merge commit có
  **cả hai parent** (`aef0220`, `e368425`) là ancestor của source, và
  `tree(4a46b3c) = tree(e368425) = 57e0876`, `git diff e368425 4a46b3c` **RỖNG**.
  (3) Tích hợp bằng **merge commit thường** (`--no-ff`), KHÔNG rebase / squash /
  cherry-pick / rewrite history. `MERGE CONFLICTS = 0`;
  source tree `633b4c3` == main result tree `633b4c3` → **TREE IDENTICAL = YES**;
  `git diff febc2ec 6372783` RỖNG → **CONTENT LOST = 0**.
  (4) Cả 11 SHA baseline/evidence quy chiếu vẫn là ancestor của `main`, gồm hai neo ledger
  `666de14` (CAP-PROV) và `06b381c` (CAP-DATA). Baseline SHA KHÔNG đổi, budget KHÔNG reset,
  WP state KHÔNG đổi.
  (5) Ghi nhận (KHÔNG thi hành) hai quyết định của chủ dự án cho phiên sau: `DEC-016`
  (`OD-DATA-01`) và `DEC-017` (`OD-DATA-02`).
  (6) Validators trên `main`: `validate_governance` **PASS** · `validate_project_state`
  **PASS** · `validate_structure` **PASS** (27 path) · `validate_routing` **PASS** (17 MAJOR
  task file) · `validate_easy_roadmap` **PASS** · `sync_easy_roadmap` PASS, file sinh ra
  KHÔNG đổi (không có status/Tier/Effort nào thay đổi).
  `branch_authority_check.sh --expect-branch main` báo **FAIL** — ghi đúng như nó là, và
  **hai nguyên nhân đều KHÔNG phải khiếm khuyết tích hợp**:
  (a) script hard-code `case main|master` = "feature work must not commit to the default
  branch" (dòng 66–70). Đây là quy tắc bảo vệ trunk, đúng theo thiết kế, và chính là hành vi
  mong muốn từ đây trở đi: phiên sau phải branch từ `origin/main` chứ không commit thẳng lên
  `main`. Phiên Integration buộc phải commit lên trunk vì việc của nó LÀ lập trunk.
  (b) `INTEGRATION_DECISION_REQUIRED: ahead of default 35` — script giải default branch từ
  remote và remote vẫn đang trỏ vào `claude/plan-tool-from-docs-qijx5m`. Con số này về 0 ngay
  khi chủ dự án đổi GitHub default branch sang `main`
  (`REMOTE_DEFAULT_SWITCH_REQUIRED = YES`). Không có cách nào đóng nó từ phía git.
  `production diff = EMPTY` và `tracked worktree = CLEAN` trong cùng lần chạy đó.
  KHÔNG chạy lại chiến dịch verification lớn: tree kết quả TRÙNG KHÍT tree source, nên phép
  tích hợp không đổi working tree và không có gì để regression lại. Không tạo report mới:
  bằng chứng và số đo đầy đủ nằm trong `PROJECT/PROJECT_DECISIONS.md` § `DEC-013`.
  (7) `WP-C1` giữ nguyên `PARALLEL_READY = YES`, KHÔNG mở trong phiên này.
- Integration Recheck / Owner Disposition — 2026-09-01 — **governance-only**, HEAD
  `07bb241`. KHÔNG sửa production code, KHÔNG sửa test code, KHÔNG mở WP, KHÔNG mở repair
  cycle, KHÔNG tạo task ID, KHÔNG merge. Kết quả:
  (1) `DEC-015` — `F-S009-01` → owner `CAP-DATA`, verdict `IMPLEMENTATION_DEFECT`,
  `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG; bốn ngưỡng Absorption Limit đều KHÔNG chạm; còn lại đúng
  MỘT `OWNER_DECISION_REQUIRED` về phương tiện thi hành (`WP-A4` đang DONE + gate FROZEN +
  `indicators.py` ngoài touch area — ba rào đều thuộc thẩm quyền chủ dự án).
  (2) Bằng chứng E1 tái lập độc lập trên chính hàm production `compute_daily_indicators`,
  môi trường trùng khớp `pyproject.lock` (Python 3.11.15 / numpy 2.4.6 / pandas 3.0.5):
  một ngày lịch thiếu làm `return7` **đổi dấu** (+0,0187 → −0,0365; lệch 295%) và làm sai
  thêm `ethbtc_return30`, `adr30`, `rsi14` — **không cái nào NaN**. Cơ chế: `score.py::
  invalid_mask` chỉ bắt giá trị KHÔNG HỮU HẠN, mà cửa sổ theo vị trí luôn sinh số hữu hạn
  nhưng sai, nên nhánh DEGRADED/INVALID mà BT §18 bắt buộc không bao giờ chạy.
  (3) `DEC-013` đo lại toàn bộ bằng git (số cũ tại `d63c222` đã hết giá trị): default branch
  giải được là `claude/plan-tool-from-docs-qijx5m` (remote KHÔNG có `main`); ahead 32 /
  behind 1 / age 9 ngày; total 95 files +27857/−372; production 15 files +940/−145; test 11
  files +3150; governance/doc 69 files +23767/−227. `merge-tree` → **0 xung đột**, tree kết
  quả `605b621` **trùng khít** tree của HEAD; nội dung thiếu ở branch hiện tại = **0**; ở
  default = 95 file. Mọi baseline SHA (`666de14`, `06b381c`, `85fa30f`, `d63c222`, `e368425`)
  đều còn là tổ tiên của HEAD. Khuyến nghị giữ **phương án A**; C bị loại vì phá neo baseline
  của ledger mà lợi ích đúng bằng 0.
  (4) Ledger đối chiếu khớp git; `CAP-DATA` used = 0 (lượt đầu là implementation, không phải
  repair cycle), `ALLOWED` vẫn CHƯA LƯỢNG HOÁ (gốc: `H-10`). `CAP-PROV` 2/2/0 không đổi.
  (5) `WP-C1` xác nhận lại read-only: `PARALLEL_READY = YES`.
- S009 — WP-A4 — 2026-09-01 — **DONE.** Ngữ nghĩa dữ liệu thiếu/hỏng + độ phủ theo khoảng
  ĐƯỢC YÊU CẦU. 9/9 REQUIRED check PASS (232/232 test suite PASS): chín check FROZEN
  2026-08-23 giữ nguyên câu chữ,
  cộng đúng MỘT check `CHECK-A4-10` do chủ dự án phê duyệt TRƯỚC khi implementation
  (`DEC-014` / `OD-A4-01`). Đóng **F-023** (định nghĩa INVALID hẹp hơn ST §3 — nay INVALID
  khi giá/lịch sử ETH **hoặc** một indicator bắt buộc `close`/`return7`/`adr30` hỏng, quy
  ước ghi ở `docs/CONVENTIONS.md`), **F-025** (`EXECUTION_DATA_GAP` nay là tag TRÊN BẢN GHI
  kèm `missing_candles_before`), **F-032** (`DELAYED_DATA_FILL` nay là tag, không chỉ bộ
  đếm), và **F-E2A1R3-05** (fetch cắt cụt vẫn đủ tư cách official).
  Root cause của F-E2A1R3-05: `gap_report` neo số nến kỳ vọng vào khoảng QUAN SÁT ĐƯỢC nên
  phần thiếu ở hai đầu vô hình; `official_eligibility` không có khái niệm "khoảng đã được
  yêu cầu". Sửa tối thiểu: khai `requested_range` tại nơi sản xuất dataset (`fetch_all`,
  `synth.generate`) → ghi vào `lineage.json` → cổng đọc. KHÔNG redesign fetch, KHÔNG đổi
  chữ ký `official_eligibility(raw_dir, lineage)`, KHÔNG đổi `dataset_hash`.
  BEFORE: yêu cầu 2020-01-01…2021-01-01, archive chỉ có tới 2020-01, REST bị chặn →
  31/366 ngày (8,5%), `missing_count = 0`, `official_eligibility -> (True,'verified')`.
  AFTER: `missing_count = 335`, `(False, 'incomplete_coverage:ETHUSDT_1d=31/366 head=0
  internal=0 tail=335')`, `Prepared.official_eligible = False`. CASE A–F đều đúng kỳ vọng.
  Định lượng trên dataset có gap (cùng seed, BEFORE=`06b381c`): INVALID 0 → 37 ngày,
  action 17 → 13, `eth_total` −0,19%, nominal BASE 600.0 → 600.0 (Base không bao giờ bị bỏ),
  bản ghi mang tag 0 → 3. Trên dataset sạch: trùng khớp từng chữ số, không drift nền.
  Phát hiện mới NGOÀI gate: **`F-S009-01`** — CONFIRMED BLOCKING,
  `OWNER_ASSIGNMENT_REQUIRED` — indicator daily tính theo VỊ TRÍ, không theo LỊCH; một ngày
  daily thiếu làm `return7` sai 14,29% mà không NaN/DEGRADED/INVALID, và dataset vẫn qua
  cổng official (0,27% < ngưỡng 1%). KHÔNG làm FAIL check nào của WP-A4; phải đóng trước
  T-06. Hardening mới: **H-14**, **H-15**.
  Không tạo task ID mới. Không mở repair cycle WP-A1. Không đụng budget `CAP-PROV`. Không
  chạm `regime.py`/`ladders.py`/`capital.py`/`verdict.py`/`failure_signals.py`/`webapp/`/
  `docs/spec/`. Không merge default branch. Không mở WP-C1/WP-A5/WP-A6, không chạy T-06.
  Tài liệu: `docs/sessions/S009-wp-a4-ngu-nghia-du-lieu-xau.md`,
  `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md`.
- S006 — WP-A2 — 2026-08-24 — **DONE.** Đấu nối các hạng mục đã viết nhưng pipeline chưa
  gọi (đóng **F-003, F-004, F-012, F-013, F-014**; RSK-007 giảm thiểu một phần). Routing
  xác nhận lại: router trả **Tier C tự nhiên**, không qua override — MICRO-GOVDEF-001 không
  hồi quy. Ready Gate 13/13 → baseline BEFORE tái hiện đủ 5 finding với phân biệt
  A/B/C/D/E (code tồn tại / có test / pipeline gọi / output chứa / downstream dùng) →
  test-first 9 test wiring (8 FAIL + 1 PASS đúng kỳ vọng: hàm `xirr` vốn đã đúng) →
  remediation THUẦN ĐẤU NỐI trong `pipeline.py` + `diagnostics.py` (+1 dòng `cli.py`
  truyền `dev_limit`, đã khai báo ranh giới scope) → 9/9 PASS → **CHECK-A2-08: 4 module
  chỉ-đọc (`benchmarks/metrics/windows/bootstrap`) 0 dòng đổi** → **CHECK-A2-09: 159
  trường metric của chiến lược + Benchmark A, 0 khác biệt** (đo qua worktree, assert
  provenance) → full regression PASS → Completion Gate 10/10. Payload official nay có
  `benchmarks` A–D, `diagnostics.ablation` (3 model), `volume_zscore_variant` + bảng
  chênh lệch, `coverage_table`, `xirr`, và bootstrap **1000/block length** (spy đo trực
  tiếp 200→1000). Không finding/risk mới. Artifact:
  `docs/sessions/S006-wp-a2-pipeline-wiring.md`, `tests/test_wp_a2_pipeline_wiring.py`.
- S005 — WP-D1 — 2026-08-24 — **DONE.** Dọn 4 khoản nợ kỹ thuật không ảnh hưởng hành vi
  (đóng **F-028, F-029, F-031, F-034**). Ready Gate 12/12 xác nhận lại (routing B/Sonnet/
  medium khớp roadmap) → baseline E0/E1 tái hiện đủ 4 finding tại 1f4c2b7 → kiểm tra rủi
  ro hành vi bắt buộc (không finding nào chạm OSCORE/ladder/capital/execution/backtest/
  gate/verdict — không escalation) → test-first 4 test (4 FAIL đúng cách) → remediation
  tối thiểu: `expires_at` Smart ladder đúng cuối accounting month (engine.py), bỏ
  PARTIALLY_FILLED khỏi `ladder_completed()` (ladders.py), `cooldown_override` đếm theo
  sự kiện thay vì zone (engine.py), xoá dead code `_noon_candles` (benchmarks.py) → 4/4
  PASS → toàn suite **99/99 PASS** → impact BEFORE/AFTER cùng dataset: **543 purchase
  record trùng khớp bit-for-bit**, chỉ `cooldown_override` đổi (35→31 sự kiện, đúng
  ngoại lệ khai báo) → Completion Gate 6/6 PASS. Không finding/risk mới. Artifact:
  `docs/sessions/S005-wp-d1-debt-cleanup.md`, `tests/test_wp_d1_debt_cleanup.py`.
- S004 — WP-A7 — 2026-08-24 — **DONE.** Sửa phạm vi kế toán vốn Smart theo accounting
  month (đóng **F-035**, CLOSED **RSK-010**). Ready Gate 20/20 xác nhận lại → baseline
  BEFORE tái hiện root cause tại 68bd8be (tháng 2+ reservable=0 ở unlock 1.0; 2 ladder/
  90 tháng; 3 mode trùng bit-for-bit) → test-first A–G (7 FAIL đúng cách + 1 guard PASS)
  → PA-A: bộ đếm tháng trong `Pool` + `open_accounting_month`, carry-first cho reserve
  vắt tháng, MỘT hook engine tại rollover (BT §19 bước 3→5); ledger lifetime +
  `opportunity_reservable` không đổi (CONVENTIONS #17) → 8/8 + 34/34 + toàn suite
  **95/95 PASS** → impact cùng dataset: ladder 2→67, Smart qua ladder 0.0208%→24.49%,
  [F5] 111.13→492.07, BASE/regime bất biến, mọi dòng truy về spec → E2 độc lập
  **PASS WITH FOLLOW-UPS** (5/5 nội dung, probe tự dựng, over-grant = 0; follow-up
  trong thẩm quyền thực hiện ngay: F-E2A7-02 → CONVENTIONS #17) → Completion Gate
  12/12 PASS. Phát hiện mới ngoài scope: **PH-04** (+ tinh chỉnh F-E2A7-03) chờ chủ
  dự án. Artifact: `docs/sessions/S004-wp-a7-monthly-smart-scope.md`,
  `docs/reviews/E2-WP-A7-monthly-smart-scope.md`, `tests/test_wp_a7_monthly_scope.py`.
- WP-A7 — TASK DEFINITION & GATE FREEZE — 2026-08-24 — Soạn và **đóng băng** task definition cho
  WP-A7 theo `TASK_DEFINITION_TEMPLATE.md`: `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md`.
  **20 mục Ready Gate** (19 đã xác nhận, 1 để xác nhận lại khi mở task) và **12 REQUIRED
  Completion check** — E1 toàn bộ, **E2 bắt buộc** cho CHECK-A7-12 (Risk 4 + `accounting_financial`).
  Kiểm precedence Master Index §2 trên bốn tầng tài liệu: **không phát hiện CONFLICT** — BT §19
  (precedence 1) bước 3/4/6 nói "đóng sổ cuối tháng", "reset trạng thái Smart HWM/mode", "overflow
  sang **Smart của tháng đó**", cùng hướng với DM §5 (`monthly_budgets` keyed by `month_local`) và
  ST §4/§6/§10/§12; DM §6 (`capital_ledger` append-only, audit) là căn cứ bắt buộc **giữ lịch sử
  toàn đời** song song với trạng thái theo tháng. Root cause được giữ nguyên văn (tử số theo tháng
  trừ `pool.deployed` cumulative lifetime), kèm lệnh cấm diễn giải lại finding thành "cần tăng số
  ladder". Routing xác nhận lại bằng router: **D / Fable / max**; `validate_routing.py` PASS trên
  **17** MAJOR task file. Coverage regression: 22/22 requirement của RCP-002 có mặt trong gate,
  không dependency nào bị làm yếu (A7 → A5/A6/C4/GATE-A/T-06 giữ nguyên). **WP-A7: PLANNED →
  READY.** Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`; không remediation F-035; không bắt
  đầu WP nào.
- RCP-002 — ROADMAP CHANGE APPLIED — 2026-08-24 — Chủ dự án phê duyệt RCP-002 kèm điều kiện bổ
  sung. Áp dụng vào bảng roadmap chuẩn: **28 → 29 task**. Thêm **WP-A7** ("Sửa phạm vi kế toán vốn
  Smart theo tháng", lớp A, sở hữu **F-035**, status `PLANNED`, routing **D/Fable/max** xác nhận
  lại bằng `routing_engine.py` tại thời điểm áp dụng: model_score 3.25, effort_score 3.45,
  floors `cognitive:A>=3&X>=3` + `safety_business:min_C` + `safety_business:min_high`). Dependency
  bắt buộc: WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**; WP-A6 không được chạy
  Completion Gate cuối trước khi WP-A7 DONE; WP-A5 measurement trước F-035 không phải canonical
  evidence; WP-C4 không đóng băng parity trên hành vi Smart capital sai. **GATE-A** định nghĩa lại
  = WP-A1…WP-A7 đều DONE. **T-06** ghi rõ hai nhóm prerequisite độc lập (nội tại GATE-A / hạ tầng
  BLK-001) — gỡ BLK-001 không cho phép chạy T-06 khi GATE-A chưa PASS. **WP-A4** giữ READY, song
  song roadmap với WP-A7 kèm ba điều kiện. **WP-A3 giữ nguyên DONE**, không reopen, gate FROZEN,
  evidence E1/E2 nguyên vẹn. DEC-009 áp cho F-035: mọi Gate result trước remediation là
  STALE/INVALIDATED — hiện **NO CURRENT OFFICIAL RESULT TO INVALIDATE**, chuyển thành dependency
  WP-A7 DONE trước T-06. Toàn bộ 35 finding, 11 risk, 3 blocker được bảo toàn. Không sửa `src/`,
  `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, đặc biệt không bắt đầu WP-A7.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`,
  `docs/reviews/PH-03-triage-smart-unlock-scope.md`.
- S003-TRIAGE — PH-03 / RSK-010 — 2026-08-24 — Triage governance + kỹ thuật, **không remediation**.
  Kết luận: PH-03 = **DEFECT**, cấp finding chính thức **F-035** (HIGH, E1). Requirement canonical
  bị vi phạm: **DM §5** (`monthly_budgets` định nghĩa `smart_deployed_vnd` là trường của bản ghi
  THÁNG), củng cố bởi ST §4/§6/§12 và ST §10. Root cause: `smart_reservable` trừ `pool.deployed`
  luỹ kế toàn đời khỏi một tử số theo tháng; `Pool` không có vòng đời tháng. Chứng minh cấu trúc:
  ở `unlock = 1.00`, hàm trả **0.000 từ tháng thứ hai sau khi tháng đầu đóng sổ**, tất định và
  không phụ thuộc dữ liệu. Quan sát 90 tháng: 2 Smart ladder; 135.249/135.251 lời gọi trả 0;
  **99,98%** vốn Smart đi qua Month-End thay vì ladder. Hệ quả nặng nhất: **chiều
  `smart_unlock_mode` của Gate 2 (BT §9) trơ hoàn toàn** — ba mode cho kết quả trùng khít
  bit-for-bit, vi phạm ST §6. Kết luận official run: **không đáng tin trước khi sửa**; DEC-009 áp
  dụng phòng ngừa (`no current result to invalidate`). Phân lớp: **A — MUST FIX BEFORE OFFICIAL
  RUN**, chứng minh bằng dependency. Ownership đề xuất: **WP-A7 mới** (RCP-002, chờ phê duyệt) —
  không nhét vào WP-A3 đã DONE, không sửa gate FROZEN của WP-A4/WP-A6. **WP-A4 MAY PROCEED IN
  PARALLEL** kèm 3 điều kiện (assert tiền đề không suy biến; không hard-code kỳ vọng vốn/ETH nhiều
  tháng; tuần tự hoá thao tác trên `engine.py`). Không sửa `src/`, `tests/`, `webapp/`,
  `docs/spec/`; không chạy official backtest; không mở WP nào.
  Artifact: `docs/reviews/PH-03-triage-smart-unlock-scope.md`,
  `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`.
- S003 — WP-A3: REGIME & VÒNG ĐỜI CRASH LADDER — 2026-08-23 — Gói đầu tiên của lớp A và là gói
  duy nhất lớp A làm đổi kết quả mô phỏng. Ready Gate xác nhận lại (T-04 DONE, routing D/Fable/max
  tự nhiên, validator PASS). Baseline E1 tái hiện đủ 4 finding TRƯỚC khi sửa (F-001: kẹt 27.2
  SMART vĩnh viễn sau CRASH→RECOVERY→STRESSED; F-021: snapshot [F5] 34 thay vì 36; F-030: mọi
  crash zone dán nhãn OPPORTUNITY dù 30/34 vốn SMART; F-022: thoát CRASH sau 49h toàn None).
  Test-first: 18 test mới, 12 FAIL đúng kỳ vọng trước fix. Remediation: tách
  `RegimeTracker.state`/`.label` (CONVENTIONS #14 — [F1] bảo đảm bằng cấu trúc), None không
  được coi là bằng chứng transition (CONVENTIONS #15), snapshot [F5] đúng nghĩa đen + daily
  limit cưỡng chế ở khâu triển khai với `DAILY_LIMIT_BLOCK` (CONVENTIONS #4/#5), pool label
  theo đa số nguồn vốn + `zone_order_key` bổ sung vế "crash sau ladder thường" (CONVENTIONS
  #16). Chỉ chạm `regime.py`, `engine.py`, `tests/`, `docs/CONVENTIONS.md` — đúng Scope Lock,
  không chạm `capital.py`/`score.py`/`webapp/`/`docs/spec/`. Suite 87/87 PASS, không test cũ
  nào bị sửa/nới lỏng. Impact BEFORE/AFTER cùng seed/dataset: mọi sai lệch quy về [F5] ST §14
  và ST §18.3+[F1]; nhãn label_transitions identical; công cụ đo commit tại
  `tests/wp_a3_impact_tool.py` (tái lập HOÀN TOÀN, kể cả BEFORE qua git worktree). E2 độc lập:
  **E2 PASS** (`docs/reviews/E2-WP-A3-regime-ladder.md`) — reviewer tự dựng kịch bản khác chứng
  minh khoá vốn trước fix (kẹt 18.7, release 0) và giải phóng đủ sau fix; 4 kịch bản khoá vốn
  tự nghĩ + long-run: không đường khoá vốn mới; 2 finding hạ tầng test (F-E2-01 đơn vị
  datetime64 trong harness, F-E2-02 script đo chưa commit) được xử lý ngay trong phiên và chạy
  lại xanh. Phát hiện mới ngoài scope: PH-03 → RSK-010 (nghi vấn `smart_reservable` trừ
  deployed xuyên tháng — chờ chủ dự án). WP-A4 chuyển PLANNED → READY. BLK-001 giữ nguyên;
  không official run, không verdict; số liệu synthetic chỉ phục vụ verification (DEC-003).
  Kết luận: **WP-A3 DONE — 10/10 REQUIRED PASS, E2 PASS**.
  Biên bản: `docs/sessions/S003-wp-a3-regime-ladder.md`.
- MICRO-GOVDEF-001 — SỬA BOUNDARY DEFECT + OVERRIDE MECHANISM — 2026-08-23 — Chủ dự án phê duyệt
  PA-1 cho DEC-010. Sửa tổng quát `routing_engine.py` (làm tròn `model_score`/`effort_score` về
  cùng độ chính xác hiển thị **trước khi** so sánh biên Tier/Effort — không epsilon tuỳ tiện, không
  hard-code task nào). Bổ sung cơ chế `check_override` vào `validate_routing.py`: chấp nhận manual
  override chỉ khi có decision reference tồn tại thật trong `PROJECT_DECISIONS.md`, `Router Raw
  Output` xác thực khớp router hiện tại, và override chỉ được leo thang chứ không hạ Tier/Effort.
  Thêm `governance/scripts/governance/test_routing_engine.py` (37 check, gồm quét toàn bộ 5^5×5^5
  tổ hợp đầu vào — 0 lệch còn lại — và 6 ca override hợp lệ/không hợp lệ tổng hợp). Kết quả: WP-A2
  route Tier C **tự nhiên** (giữ nguyên Model Opus, Effort high), không cần override — chuyển
  `BLOCKED` → `READY`. BLK-003 RESOLVED, GOV-RSK-001 CLOSED. Đối chiếu trước/sau trên toàn bộ 16
  file MAJOR task: đúng một dòng đổi (WP-A2, Tier B → C), không task nào khác bị ảnh hưởng. Không
  sửa `src/`, `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, không mở S003.
  Kết luận: **MICRO-GOVDEF-001 DONE**.
  Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- S002 — ROADMAP FINALIZATION / GATE FREEZE (T-04) — 2026-08-23 — Soạn và đóng băng Ready Gate +
  Completion Gate đầy đủ cho toàn bộ 15 work package của RCP-001 (**125 REQUIRED check**), cộng file
  định nghĩa cho chính T-04 (12 REQUIRED check). Chính thức hoá DEC-009 thành `CHECK-B1-02`
  (REQUIRED) của WP-B1. Bảo toàn override DEC-008 cho WP-A2 (Tier C / Opus / high) kèm giá trị
  router thô. Bảo toàn đủ 8 trường provenance của T-06A cũ trong WP-A1. Tách rõ trách nhiệm đo lường
  (WP-A5) khỏi trách nhiệm chính sách verdict (WP-B1). Đối chiếu độ phủ bằng script: 40/40 định danh
  finding có nơi thuộc về. Phát hiện PH-01 (sai số đếm trong tóm tắt S001) và PH-02 → **BLK-003**.
  Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`. Không bắt đầu work package nào.
  Kết luận: **T-04 DONE — PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S002-t04-gate-freeze.md`.
  Đối chiếu: `docs/reviews/S002-coverage-regression-check.md`.
- RCP-001 — ROADMAP CHANGE APPLIED — 2026-08-23 — Chủ dự án phê duyệt RCP-001 kèm bốn điều kiện
  (cấu trúc 15 work package; phân lớp A/B/C/D với quy tắc Gate 1 staleness cho F-017; bỏ T-06A,
  hấp thụ vào WP-A1; ghi đè routing của WP-A2 lên Tier C). Bảng roadmap chuẩn được cập nhật từ
  14 lên 28 task. Phát hiện và ghi nhận riêng một governance/tooling defect (GOVDEF-001) trong
  chính `routing_engine.py`, tách khỏi finding sản phẩm. Không sửa `src/`, `webapp/`, `tests/`,
  `docs/spec/`. Không bắt đầu thực thi work package nào. Không bắt đầu S002.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`, `docs/reviews/GOVDEF-001-routing-engine-boundary.md`.
- RCP-001 — ROADMAP CHANGE PROPOSAL (trình) — 2026-08-23 — Chuyển 33 finding của S001 thành 15
  work package có dependency graph và phân lớp A/B/C/D. Trình để chủ dự án phê duyệt.
- S001 — DISCOVERY & BASELINE (AUDIT READ-ONLY) — 2026-08-23 — Đối chiếu toàn bộ implementation
  với spec V2.1.5 theo chín nhóm A–I. Sinh Compliance Matrix, Audit Findings (33 finding: 0
  CRITICAL, 8 HIGH, 15 MEDIUM, 7 LOW, 3 spec defect; 18/33 có bằng chứng chạy thật) và Discovery
  Baseline. Không sửa một dòng mã sản phẩm nào. Kết luận: **S001 PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S001-discovery-baseline.md`.
- S000 — PROJECT OPEN — 2026-08-23 — Chọn profile PRODUCT, khởi tạo trạng thái dự án, lập kế
  hoạch khảo sát (T-01..T-03) và lộ trình sơ bộ 14 task. Không sửa một dòng code sản phẩm nào.
  Biên bản: `docs/sessions/S000-project-open.md`.

## Bằng chứng nền thu tại S000

Đây là bằng chứng **E1 — chạy thật**, khác với các quan sát đọc code (E0) đã nêu ở mục rủi ro.

| Hạng mục | Kết quả | Mức |
|---|---|---|
| Test suite Python | **69 passed, 0 failed, 0 skipped, 0 error** trong 372,63s | E1 |
| Môi trường | Python 3.11.15, node v22.22.2, git 2.43.0 | E1 |
| Thư viện thực cài | numpy 2.4.6, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1 | E1 |
| Mạng tới Binance/CoinGecko | Cả ba host trả 403 ở tầng proxy; PyPI thông | E1 |
| `ethdca synth` | 2,0s — 262.748 nến 15m, 3.102 nến ngày | E1 |
| `ethdca freeze` Gate 2 | 19 ứng viên OFAT → loại 1 (`base_pct=0.7`, lý do `smart_pct < 0.15`) → 18 hợp lệ; 200 interaction; **mẫu số 219** | E1 |
| `ethdca freeze` Gate 3 | 14 deterministic + 100 sampled = **114 config** | E1 |
| Parity engine JS ↔ Python | Lệch tối đa **7,39e-11** trên 40 ngày — hai bản đồng thuận | E1 |
| Bất biến kế toán ladder (một tháng) | Tổng bảo toàn 3.000.000 qua fill toàn phần → fill một phần → invalidation → release; không pool nào âm | E1 |
| Build quine của webapp | Self-check đạt, template giải mã lại được | E1 |
| CLI | 6 lệnh: `fetch`, `synth`, `freeze`, `run`, `verdict`, `export-live` | E1 |
| `results/`, `data/`, `.venv/` trong repo | Không tồn tại — xác nhận chưa từng có official run | E1 |

Điều này làm đổi đánh giá ban đầu theo hướng tốt hơn: **mã nguồn khỏe hơn tài liệu gợi ý**.
S001 xác nhận: tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không (xem RCP-001).

Cảnh báo quan trọng về ý nghĩa của các validator governance: chúng đang PASS trên **tập rỗng** —
0 evidence record, 0 MAJOR task file, 0 task DONE. Khung đã có, nội dung thì chưa. Không được
đọc các dòng PASS đó như bằng chứng chất lượng dự án.

## Routing sơ bộ cho task chưa có file định nghĩa

**Cập nhật S002:** mục này không còn là nguồn routing cho 15 work package — cả 15 đã có file định
nghĩa đầy đủ dưới `docs/tasks/`, và file task là nguồn routing chính thức theo
`ROADMAP_SYNC_STANDARD.md`. Các giá trị dưới đây được **giữ lại làm dấu vết lịch sử** và đã được
T-04 xác minh lại bằng `routing_engine.py` (E1): 15/15 khớp, ngoại lệ duy nhất là override DEC-008
của WP-A2. Task còn lại chưa có file định nghĩa (T-05…T-11) vẫn dùng mục này.

Ghi lại để lộ trình có bằng chứng routing, sẽ soạn thành file task đầy đủ và đóng băng tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

### Task gốc (S000)

- T-00 — D3 R2 B1 A3 X3 → 2.35 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C4 F2 → 2.7 → xhigh
- T-04 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U2 V2 H3 C3 F3 → 2.60 → xhigh
- T-06 — D2 R3 B3 A1 X3 → 2.45 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-08 — D3 R3 B2 A3 X3 → 2.80 → C (2 floor); U3 V2 H3 C3 F3 → 2.80 → xhigh
- T-09A — D3 R3 B2 A1 X2 → 2.35 → C (floor `safety_business:min_C`); U1 V3 H2 C2 F3 → 2.25 → high
- T-09B — D3 R3 B3 A3 X3 → 3.00 → D (2 floor); U3 V3 H3 C3 F3 → 3.00 → xhigh
- T-10 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-11 — D4 R4 B3 A2 X4 → 3.50 → D (2 floor); U3 V4 H4 C4 F4 → 3.80 → max

Category `accounting_financial` được gắn cho T-06, T-08, T-09A, T-09B, T-10, T-11 vì chúng chạm
lớp tính toán dẫn tới quyết định xuống tiền thật. T-09B gắn thêm
`material_sensitive_data_corruption` vì thao tác chuyển đổi lưu trữ có thể làm hỏng sổ tài chính.

**T-06A đã bị loại khỏi roadmap theo RCP-001** (hấp thụ vào WP-A1). Routing gốc của nó vẫn được
lưu lại để đối chiếu lịch sử: D2 R2 B2 A1 X2 → 1.85 → B; U1 V2 H2 C2 F2 → 1.80 → high.

### Work package của RCP-001 (2026-08-23)

- WP-A1 — D2 R3 B3 A2 X3 → 2.60 → C (không floor); U2 V3 H3 C3 F3 → 2.80 → xhigh
- **WP-A2** — D2 R2 B2 A1 X3 → **model_score = 2.0 (hiển thị), 1.9999999999999998 (nội bộ)** →
  router trả **B** (Sonnet). **GHI ĐÈ THỦ CÔNG theo DEC-008 → Tier C (Opus)**, lý do: defect biên
  dấu phẩy động của router (GOVDEF-001), không phải lỗi chấm điểm đầu vào.
  Effort: U1 V3 H2 C3 F2 → 2.15 → high (giữ nguyên, không bị override)
- WP-A3 — D4 R4 B3 A3 X3 → 3.50 → D (floor `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`,
  `safety_business:min_C`); U3 V4 H4 C3 F4 → 3.65 → max (floor `safety_business:min_high`)
  · category `accounting_financial`
- WP-A4 — D3 R3 B2 A3 X2 → 2.65 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-A5 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U3 V3 H3 C3 F3 → 3.00 → xhigh
- WP-A6 — D4 R3 B3 A2 X3 → 3.10 → D (floor `cognitive:D>=4&X>=3`); U3 V4 H3 C3 F3 → 3.20 → max
- WP-B1 — D3 R4 B3 A4 X3 → 3.40 → D (floor `cognitive:A>=3&X>=3`, `safety_business:min_C`);
  U3 V3 H3 C3 F4 → 3.25 → max (floor `safety_business:min_high`) · category `accounting_financial`
- WP-B2 — D3 R2 B1 A2 X3 → 2.20 → C (không floor); U2 V3 H3 C3 F2 → 2.55 → xhigh
- WP-B3 — D2 R2 B2 A2 X2 → 2.00 → C (không floor); U1 V2 H2 C2 F2 → 1.80 → high
- WP-C1 — D2 R3 B2 A1 X2 → 2.10 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-C2 — D3 R2 B3 A3 X3 → 2.75 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh
- WP-C3 — D3 R3 B2 A2 X2 → 2.50 → C (floor `safety_business:min_C`); U2 V3 H2 C2 F3 → 2.45 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-C4 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-D1 — D1 R1 B1 A1 X1 → 1.00 → B (không floor); U1 V1 H1 C1 F1 → 1.00 → medium
- WP-D2 — D3 R2 B2 A4 X3 → 2.70 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh

- **WP-A7** — D3 R4 B3 A3 X3 → **3.25** → **D** (floor `cognitive:A>=3&X>=3`,
  `safety_business:min_C`); U3 V4 H3 C3 F4 → **3.45** → **max** (floor `safety_business:min_high`)
  · category `accounting_financial` · warnings: none.
  **Đã có file định nghĩa** `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` (2026-08-24)
  → **file task là nguồn routing chính thức**; giá trị ở đây giữ làm dấu vết lịch sử và đã được
  `validate_routing.py` kiểm khớp (17 MAJOR task file).

**GOVDEF-001 / MICRO-GOVDEF-001** — không bắt buộc full routing (MICRO). Chấm điểm tham khảo:
D1 R2 B2 A1 X1 → 1.45 → B; U1 V2 H1 C1 F2 → 1.45 → medium.

## Next Session

**Cập nhật sau T-09B (2026-09-02, S014).** `T-09B` = `IMPLEMENTED`. **NEXT SMALLEST ACTION (chủ dự
án, không cần agent):** tạo project Firebase và làm 5 bước ở `webapp/README.md` § Thiết lập Firebase
(tạo project + bật Anonymous + tạo Firestore → điền `webapp/firebase_config.js` → `node
webapp/build_app.js` → `firebase deploy` → mở app ở trình duyệt dùng hằng ngày → chép UID vào
`firestore.rules` → deploy rules), export JSON từ bản artifact cũ và *Nạp lại từ JSON*, rồi lặp lại
bằng tay CHECK-01/02/03/04/14 trên app thật. Sau đó Owner Decision `T-09B: IMPLEMENTED → DONE` kèm
cập nhật `RSK-001`, và khai ba file runtime mới vào `PRODUCTION_PATHS.md` (`H-27`). Không mở task
tiếp theo trong S014.

**Cập nhật sau T-09A (2026-09-02).** Mục "Recommended Session" bên dưới được viết trước
S010/T-09A và giữ nguyên làm dấu vết. Trạng thái hiện tại và hành động nhỏ nhất kế tiếp:

- `WP-A4` **DONE** (S010, `CAP-DATA` repair cycle #1 đã tiêu).
- `WP-C1` **DONE**; `T-09A` **DONE** (2026-09-02, Owner Decision `DEC-018`/`OD-WEBAPP-01`).
  `CAP-WEBAPP` budget Owner-ratified: allowed 2 / used 0 / remaining 2. DỪNG theo chỉ thị chủ
  dự án ở phiên Integration này — không mở task tiếp theo, không chạy T-06, không xây dashboard.
- **NEXT SMALLEST ACTION** — chủ dự án chọn giữa hai đường đang mở trên GATE-A:
  `WP-A1` (`CAP-PROV` budget = 0, cần Owner Decision để mở `OWNER_EXTENSION`), `WP-A5`, `WP-A6`.
  Lưu ý cảnh báo historical state ở mục V-01/V-02 bên dưới — chưa có evidence dữ liệu lịch sử
  sạch, việc code T-09A DONE không tự động xác minh điều đó.
- Blocker V1 còn lại **không đổi** vì T-09A: `WP-A1` (`CAP-PROV` budget = 0, cần Owner
  Decision), `WP-A5`, `WP-A6` trên đường găng GATE-A; `BLK-001` (mạng Binance); `T-09B`
  (RSK-001, lưu trữ bền) cho phần V1 "dữ liệu tồn tại sau reload/restart" ở mức bền vững.

Branch authority (bắt buộc, từ `DEC-013` 2026-09-01):

    Canonical trunk = main.
    Mọi phiên product mới: git fetch origin && git checkout -b <branch> origin/main
    KHÔNG dùng claude/wp-a1-provenance-v67k9h làm long-running integration branch nữa.
    Branch đó được GIỮ cho provenance/history, KHÔNG xoá.

Sau tích hợp, **hai stream chạy độc lập, branch riêng từ `origin/main`**. Repo không có
dependency thật giữa hai stream, nên KHÔNG tạo dependency giả:

- **STREAM DATA** — thi hành `DEC-016`: mở lại `WP-A4` cho **đúng một** repair cycle để sửa
  `F-S009-01`. Budget: `CAP-DATA` allowed 2 / used 0 / remaining 2 (`DEC-017`) — bản sửa này
  là repair cycle **#1**, KHÔNG được reset. Effective Risk = HIGH ⇒ **mandatory batch review
  cuối phiên** theo `RISK_MODEL.md`.
- **STREAM WEB** — `WP-C1` (C/xhigh), `PARALLEL_READY = YES`. Expected Touch Area
  (`webapp/`, `demo/`, `.gitignore`) KHÔNG giao với vùng của STREAM DATA
  (`src/eth_dca_os/**`).

Recommended Session:
S010 — chủ dự án quyết định:

- **Theo đường găng — ưu tiên cao nhất:** `WP-A6` (D/max) — mắt xích cuối của chuỗi
  T-04 → WP-A3 ✅ → {WP-A4 ✅ ∥ WP-A7 ✅} → **WP-A6** → GATE-A → T-06. Nay đủ dependency
  sau khi WP-A4 DONE tại S009. Gói này phải trả lời `HARDENING_BACKLOG.md` **H-15** (số
  phận zone TRIGGERED trong chu kỳ INVALID) — re-trigger BẮT BUỘC, không được bỏ qua.
- **Song song, đủ dependency từ S004:** `WP-A5` (C/xhigh). Lưu ý tuần tự hoá: WP-A5 cùng
  sửa `pipeline.py` với WP-A2 (đã push xong, không còn phiên nào giữ file).
- **Độc lập hoàn toàn với lớp A:** `WP-C1` (C/xhigh). Xác nhận read-only tại S009: Status
  `READY`, dependency T-01 ✅ + T-04 ✅, Expected Touch Area (`webapp/`, `demo/`,
  `.gitignore`) **không giao** với vùng WP-A4 vừa sửa (`src/eth_dca_os/**`). WP-A4 không
  chạm một dòng nào trong `webapp/`. → **WP-C1 vẫn READY và độc lập.**
- `WP-A4`, `WP-D1` đã **DONE** — không còn trong danh sách READY.
- ~~**Trước khi mở bất kỳ gói nào ở trên**, hai hard-stop governance đang chờ quyết định~~ —
  **CẢ HAI ĐÃ ĐÓNG** (2026-09-01, phiên Integration): `DEC-013` đã thi hành (trunk = `main`,
  integration SHA `febc2ec`), và khe thẩm hành của `F-S009-01` đã được `DEC-016` đóng. Không
  còn hard-stop governance nào chặn việc mở gói.

Task đang READY (đủ điều kiện bắt đầu, chưa bắt đầu):
`WP-A5`, `WP-A6` (mới đủ dependency từ S009), `WP-C1`, `WP-D2`.
`WP-A1` đang `IN_PROGRESS` và bị chặn bởi quyết định của chủ dự án, không phải bởi kỹ thuật.

Task đang PLANNED, chưa đủ điều kiện READY:
- `WP-C4` — chờ WP-A6 (WP-A3 ✅, WP-A4 ✅, WP-A7 ✅)

Task đang BLOCKED và lý do:
- `WP-C2` — DEC-005 còn PENDING (thuộc T-05, thẩm quyền chủ dự án)
- `T-03` — chờ WP-C1 (giữ nguyên, không hạ Completion Gate)

Cần chủ dự án quyết định:
1. **DEC-005** — phạm vi công cụ trước verdict (T-05). Không chặn lớp A.
2. **PH-01** — cách đính chính số đếm finding trong biên bản S001.
3. **BLK-001** — máy/VPS truy cập được `data.binance.vision` và `api.binance.com`, cần cho T-06.
   Không gói nào trong 15 gói cần nó, nên chưa gấp.
4. **PH-04** — kênh tiêu thụ unlock liên tục để ba mode `smart_unlock` phân biệt được ở tầng
   outcome (mở WP mới / đề xuất V2.2 qua WP-D2 / chấp nhận giới hạn). Kèm tinh chỉnh
   F-E2A7-03 của reviewer E2: sức phân giải trên dataset chính thức là câu hỏi empirical
   — nên đo trước khi diễn giải Gate-2. Xem mục PH-04 ở Active Risks.
5. **Glob validator** (follow-up #3 của E2-WP-A7-001; tồn đọng từ S003) —
   `validate_evidence.py` / `validate_task_completion.py` quét `TASK-*.md` không khớp
   quy ước `WP-*.md` → hiện PASS trên tập rỗng; cần một gói governance-tooling mở rộng
   glob để Exit Criteria "validators PASS" có nghĩa thực chất.
6. ~~**`F-E2A1R3-05` — phê duyệt COMPLETION GATE CHANGE PROPOSAL cho WP-A4**~~ —
   **ĐÃ QUYẾT** (`DEC-014` / `OD-A4-01`, 2026-09-01) và **ĐÃ ĐÓNG** tại S009:
   `CHECK-A4-10` PASS. Không còn là mục chờ quyết định.
6b. ~~**`F-S009-01` — ownership**~~ — **ĐÃ QUYẾT phần ownership** (`DEC-015`, 2026-09-01,
   phiên Integration Recheck): capability owner = **`CAP-DATA`**; spec verdict =
   **`IMPLEMENTATION_DEFECT`** (BT §18 buộc DEGRADED/INVALID khi indicator daily bắt buộc
   thiếu, và ST §1.1/§1.3/§17 + BT §2 phát biểu cửa sổ theo NGÀY LỊCH — trong khi ST §17.2
   cho thấy spec nói "96 nến" khi muốn đếm theo nến). `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG.
   Số task ID mới = 0.

   **ĐÃ QUYẾT — `OWNER_DECISION_REQUIRED` ĐÓNG** (`DEC-016` / `OD-DATA-01`, 2026-09-01,
   phiên Integration): chủ dự án chọn **phương án (A)** — REOPEN `WP-A4` cho ĐÚNG MỘT repair
   cycle, mở touch area tối thiểu sang `indicators.py` + wiring/test trực tiếp cần thiết;
   KHÔNG tạo WP mới, 0 task ID mới. Chi phí đã được chủ dự án nhìn thấy trước khi quyết:
   bản sửa tiêu repair cycle **#1** của `CAP-DATA` (`DEC-017`: allowed 2 / used 0 /
   remaining 2). Phiên Integration **KHÔNG thi hành** quyết định này. Đoạn dưới giữ nguyên
   để đọc được bối cảnh lúc quyết định.

   **ĐÃ THI HÀNH và ĐÃ ĐÓNG tại S010** (2026-09-01, CAP-DATA REPAIR CYCLE #1):
   `CHECK-A4-11` PASS ở E1, `WP-A4` trở lại `DONE` với 10/10 REQUIRED. Diff production của
   chu kỳ đo bằng lệnh — `git diff --shortstat cb75f9d..ef8cdbb -- <production paths>` →
   `1 file, +74 / −5`, đúng một file `src/eth_dca_os/indicators.py`. `CAP-DATA` budget nay
   allowed 2 / **used 1** / remaining 1 (`REVIEW_BUDGET_LEDGER.md` §2.1 và §4.2). Batch
   review bắt buộc: PASS, 0 BLOCKING —
   `docs/reviews/S010-batch-review-calendar-indicator.md`. `MAX_MISSING_RATIO` KHÔNG đổi.
   Số task ID mới = 0. `F-S009-01` không còn là mục chờ quyết định.

   Bối cảnh lúc còn mở — đúng MỘT quyết định, ưu tiên cao nhất. Đây không
   còn là khe ownership mà là khe **thẩm quyền thi hành**: `CAP-DATA` chỉ có một thành viên
   là `WP-A4`, đang `DONE` với Completion Gate FROZEN, và `indicators.py` nằm ngoài Expected
   Touch Area. Bốn ngưỡng Absorption Limit đều **KHÔNG chạm** (A: Effective Risk `MAX(3,2)=3`
   không đổi; B: 2/3 mục; C: +11,1%; D: nằm trên vertical slice), nên đây **không** phải
   `ABSORPTION_LIMIT_REACHED`. Ba lựa chọn của chủ dự án — (A) mở lại `WP-A4` + gate change
   proposal + mở touch area sang `indicators.py` *(khuyến nghị)*; (B) DESCOPE *(mâu thuẫn
   `DEC-011` điểm 9)*; (C) task ngoại lệ *(chủ dự án tự đặt ID)*. Chi tiết + bằng chứng E1
   tái lập tại phiên: `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` PHẦN II.

   Dữ kiện budget cho quyết định: `git log 666de14..HEAD -- src/eth_dca_os/indicators.py`
   = **0 commit**, nên finding nằm NGOÀI mọi cumulative repair diff và bản sửa **sẽ tiêu một
   repair cycle mới** của owner nhận nó.
7. **WP-A1 — disposition cho 3 hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED`**
   (`F-E2A1-03`, `F-E2A1R3-03`, `F-E2A1R3-06`+`F-E2A1-08`): mỗi hạng mục chọn
   `ACCEPT_AS_IS` / `DESCOPE` / `OWNER_EXTENSION`. Budget CAP-PROV đã hết
   (`DEC-012`: allowed 2 / used 2 / remaining 0). Lưu ý: 2 trong 3 hạng mục đóng được ở
   chi phí budget = 0 vì chỉ cần tài liệu. Xem bản disposition §4.
8. ~~**Integration decision** (`DEC-013`)~~ — **ĐÃ QUYẾT và ĐÃ THI HÀNH** (2026-09-01,
   phiên Integration): phương án **A — INTEGRATE NOW**; canonical trunk = **`main`**; tích
   hợp bằng merge commit thường `febc2ec`; 0 xung đột; tree kết quả TRÙNG KHÍT tree source;
   content lost = 0; 11/11 baseline SHA vẫn reachable. Hard-stop
   `INTEGRATION_DECISION_REQUIRED` **ĐÓNG**. Không còn là mục chờ quyết định.

   Còn lại đúng **một thao tác của chủ dự án trên GitHub**, không phải quyết định kỹ thuật:
   `REMOTE_DEFAULT_SWITCH_REQUIRED` — đổi default branch của repository sang `main` (GitHub
   → Settings → General → Default branch → Switch to `main`). `origin/main` đã tồn tại và
   đúng nội dung; việc chưa đổi `origin/HEAD` KHÔNG làm phép tích hợp thất bại.
9. **Trình tự V1** — T-06/GATE-A có thật sự là điều kiện tiên quyết của V1 daily-use không,
   hay đường web app (`CAP-WEBAPP`, WP-C1 đang READY và độc lập với lớp A) chạy song song
   được? `DEC-011` định nghĩa V1 theo web app dùng hàng ngày, trong khi
   `CAPABILITY_REGISTRY` xếp `CAP-WEBAPP` ngoài Vertical Slice. Câu này đổi đường găng một
   cách vật chất. Xem bản disposition §8.1.

Owner Decision đã ghi tại phiên Owner Disposition (2026-09-01):
`DEC-011` (Product Intent + V1 Daily-Use Acceptance), `DEC-012` (hạn mức budget CAP-PROV),
`DEC-013` (integration — nay **RESOLVED / INTEGRATED** tại phiên Integration cùng ngày). Phân loại lại toàn bộ finding đang mở, đề xuất capability
owner cho `F-E2A1R3-05`, và Integration Decision Check đầy đủ nằm ở
`docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md`.

Trạng thái WP-A1 KHÔNG đổi sau phiên đó: `IN_PROGRESS`, CHECK-A1-01…10 `PASS`,
CHECK-A1-11 `FAIL`, GATE-A KHÔNG ĐÓNG, T-06 KHÔNG MỞ. Không task ID mới, không WP mới,
production/test diff = 0.

**S009 cũng KHÔNG đổi trạng thái WP-A1.** WP-A4 đóng `F-E2A1R3-05` ở `CAP-DATA`, nên
finding đó chuyển từ "đang mở, chưa có chủ" sang "đã đóng, chủ = CAP-DATA". WP-A1 vẫn
`IN_PROGRESS`, CHECK-A1-11 vẫn `FAIL`, repair cycle của WP-A1 vẫn = 2 (KHÔNG tăng), budget
`CAP-PROV` REMAINING vẫn = 0, và ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED` vẫn chờ chủ
dự án — S009 KHÔNG tự đóng mục nào trong đó.

Purpose:
Tiếp tục chương trình remediation lớp A trên đường găng tới official run, với Completion Gate đã
đóng băng từ T-04.

KHÔNG tự mở — chủ dự án sẽ ra chỉ thị riêng.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. File định nghĩa của work package được chọn, dưới `docs/tasks/`
6. `docs/sessions/S004-wp-a7-monthly-smart-scope.md` (phiên gần nhất; kế toán Smart theo
   tháng mới) và `docs/sessions/S003-wp-a3-regime-ladder.md` (ngữ nghĩa regime/ladder)
7. `docs/CONVENTIONS.md` #14–#17 (nếu gói chạm engine/regime/capital)
8. `docs/reviews/S001-audit-findings.md` — phần finding mà gói đó đóng
9. `docs/spec/` — các điều khoản được viện dẫn trong Completion Gate của gói

Nhắc trước khi mở S005:
Completion Gate của cả 15 gói đã **đóng băng** ngày 2026-08-23. Không được xoá hay làm yếu bất kỳ
REQUIRED check nào để gói đi qua. Nếu một check hoá ra sai hoặc bất khả thi, dùng khối
`COMPLETION GATE CHANGE PROPOSAL` theo `TASK_COMPLETION_GATE_STANDARD.md` và trình chủ dự án —
không sửa im lặng.
