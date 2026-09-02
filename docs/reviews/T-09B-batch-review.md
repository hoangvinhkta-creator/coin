# T-09B — BATCH REVIEW (bắt buộc, Effective Risk = HIGH)

Nguồn thẩm quyền:
`governance/v4/CORE/REVIEW_PROTOCOL.md`, `governance/v4/CORE/PRODUCTION_PATH_RULE.md`,
`governance/v4/CORE/RISK_MODEL.md` § "HIGH Does Not Mean STOP",
`PROJECT/PROJECT_DECISIONS.md` `DEC-011` (tiêu chí `BLOCKING V1` A–F), `DEC-021` (Critical Product
Question A–F, Minimum Security Floor, Over-engineering Guard).

Ngày:
2026-09-02

Phạm vi review:
TOÀN BỘ diff tích luỹ của lượt implementation ban đầu T-09B trong một lượt duy nhất. Reviewer trả
**tất cả** finding BLOCKING nhận diện được trong một lần — nối tiếp finding qua nhiều vòng là
process failure (`GOVERNANCE_V4.md` §II.2). Review này do cùng phiên thực thi làm (không có
reviewer độc lập trong môi trường agent) → mức bằng chứng là **E1 + dò đối kháng**, KHÔNG phải E2;
ghi rõ theo `EVIDENCE_STANDARD.md` § Solo Independent Review.

## 0. Sáu bước trước khi review (REVIEW_PROTOCOL.md § Before The Review Starts)

| # | Bước | Giá trị |
|---|---|---|
| 1 | SHA đầy đủ + remote SHA | BASE `4502ea6c364910004aebae0cfd046cfd97c0358d` (= `origin/main` lúc mở phiên), HEAD implementation `0d4917a634ac8ef74a0f66ceab12555145eebff2` (commit `a19d3ad` = production, `0d4917a` = test/harness/README) |
| 2 | Branch authority check | `branch_authority_check.sh --expect-branch claude/t09b-firebase-implementation-nz50is` → PASS sau khi tạo upstream (`git push -u`), production diff EMPTY lúc mở phiên |
| 3 | Phiên bản công cụ được ghim vào bằng chứng | node v22.22.2 · npm 10.9.7 · playwright 1.56.1 · firebase 12.18.0 (SDK compat, CDN pin cùng version) · firebase-tools 15.28.2 · Cloud Firestore emulator v1.22.0 (JAR) · OpenJDK 21.0.10 · Chromium `/opt/pw-browsers/chromium` · Python 3.11 |
| 4 | Tracked worktree | CLEAN trước phiên; CLEAN sau commit C (`git status --porcelain`) |
| 5 | Task Spec / Completion Gate / production paths / risk register / budget ledger | `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (16 REQUIRED FROZEN 2026-09-02); `PROJECT/PRODUCTION_PATHS.md`; `PROJECT/PROJECT_PROGRESS.md` § Active Risks (RSK-001, RSK-003); `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2 (`CAP-WEBAPP` 2/0/2) |
| 6 | Cumulative repair diff | `4502ea6..0d4917a` — **lượt implementation ban đầu** của T-09B, KHÔNG phải repair cycle (cùng quy ước `CAP-PROV` §1, `CAP-DATA` §2.1, `T-09A` §2.2) |

## 1. Diff được review

Đo bằng lệnh, không cộng tay.

Theo **khai báo** production path (`PRODUCTION_PATHS.md` §1 bảng + §2 loại trừ test):

    git diff --shortstat 4502ea6..0d4917a -- webapp/app_logic.js webapp/engine.js \
        webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock
      -> 3 files changed, 560 insertions(+), 162 deletions(-)
         webapp/app_logic.js   +/- 619 dòng · webapp/app_shell.html 42 · webapp/build_app.js 61

Ba file runtime MỚI mà bảng khai báo chưa có (xem `F-T09B-05`/`H-27`): `webapp/firebase_config.js`
25 dòng · `firestore.rules` 32 dòng · `firebase.json` 21 dòng.

Lệnh glob ghi ở `PRODUCTION_PATHS.md` §1 (nuốt cả test, harness, `package-lock.json` +9.482 dòng —
`H-21`): `12 files changed, 10152 insertions(+), 295 deletions(-)` — KHÔNG có thẩm quyền phân loại.

`webapp/engine.js` = **0 dòng đổi** (`git diff --stat` rỗng). `src/eth_dca_os/**`,
`pyproject.toml`, `pyproject.lock` = **0 dòng đổi**.

Hàm kế toán trong Out of Scope (`addContribution`, `addP2P`, `addBuy`, `addDay`, `reserveFor`,
`releaseLadder`, `createLadder`, `cancelLadder`, `ladderMonth`, `smartReservable`,
`oppReservable`, `month`, `currentMonth`, `monthKey`, `poolFor`, `findZone`): **không hunk nào chạm**
(kiểm bằng `git diff | grep` chữ ký hàm — rỗng). 16 hunk của `app_logic.js` nằm ở: header comment,
khối khởi tạo state (bỏ `readJSON("app-state")` + "mirror thắng"), `render()`/`renderBanners()`
(gọi persistence), guard `canWrite` ở 7 handler + huỷ ladder, khối persistence (thay hoàn toàn
`touch/pageHTML/b64ToStr/save` bằng `touch/mirror/plain/validateState/persist/renderPersistence/
persistenceBanners/reconcileMirror/initPersistence…`), `loadSeed`, export/import/wipe, wiring cuối.

## 2. Bằng chứng đã kiểm chứng lại (không tin lời kể của implementer)

| Hạng mục | Kết quả |
|---|---|
| `npm --prefix webapp test` trên bản build cuối (`0d4917a`) | 6/6 file exit 0, 2m31s, 0 page error |
| `test_t09b_persistence.js` | 14/14 check trong file PASS, **285 assertion / 0 FAIL** (3 lần chạy; lần 1 lộ 1 lỗi thiết kế TEST ở kịch bản Auth-thất-bại — sửa test, không sửa production) |
| `test_t09a_accounting.js` trên state đã round-trip Firestore | **68/68**, A–F PASS |
| `test_v01_v02_v03.js` trên state đã round-trip | V-01 BÁC BỎ · V-02 BÁC BỎ · V-03 BÁC BỎ — giống hệt T-09A |
| `test_multi_month_invariant.js`, `test_zone.js`, `test_app.js` | PASS; `test_app.js` xác nhận trang KHÔNG nhúng `app-state`/`page-template` |
| Bằng chứng phía Firebase | Đọc qua REST của emulator từ Node (`getDoc`), độc lập với SDK trong trang; bit-exact với bản trong bộ nhớ ở mọi `readState()` |
| Rules thật | Emulator nạp `firestore.rules` của repo; placeholder `OWNER_UID_REQUIRED` → mọi UID bị từ chối (đúng thiết lập mặc định-deny); UID lạ khi sổ tồn tại → `permission-denied` (H-23 visible) |
| Security floor (`DEC-021` §4) | không public write (rules deny mặc định, không delete); không secret trong repo (`firebase_config.js` là public client config, còn REQUIRED; `.firebaserc`, log, `public/` gitignored); malformed/corrupt → CORRUPT fail closed + không ghi đè (4 ca); không báo SAVED khi chưa ack (chip chỉ đổi khi transaction resolve; offline → CHƯA XÁC NHẬN/CHƯA LƯU) |
| Validators | `validate_governance.py`, `validate_structure.py`, `validate_project_state.py`, `validate_routing.py` (19 MAJOR), `sync_easy_roadmap.py` + `validate_easy_roadmap.py` → PASS |

## 3. Phép thử BLOCKING, phát biểu theo chiều phủ định

`REVIEW_PROTOCOL.md`: BLOCKING cần ĐỒNG THỜI (a) đường production hiện hành, (b) hậu quả nghiệp vụ
nằm trong Completion Gate hoặc risk register, (c) bằng chứng tái lập được. `DEC-011`/`DEC-021`
thêm trục A–F.

    CONFIRMED BLOCKING còn lại = 0

Một finding thoả cả ba trong lúc thực thi (`F-T09B-01`) đã được sửa TRƯỚC commit implementation —
nằm trong cumulative diff của chính lượt này → cùng lượt, không mở repair cycle.

## 4. Finding

### F-T09B-01 — Hai tab cùng profile: tab cũ (stale) ghi đè bản mới hơn trên Firestore
Phân loại: **CONFIRMED — đã sửa trong cùng lượt** (trước `a19d3ad`) · Capability: `CAP-WEBAPP`

Bản `persist()` đầu tiên dùng `set()` không điều kiện: tab B mở sau tab A, A ghi một giao dịch
(rev N+1), B (còn ở rev N, không có giao dịch đó) ghi một thao tác khác → B ghi đè rev N+1 bằng
bản không có giao dịch của A; cả hai tab đều hiện "Đã lưu bền". Đây là mất dữ liệu tài chính ÂM
THẦM (Critical Product Question **E**, `RSK-001`), đường production thật (hai tab là thao tác
thường ngày), và cùng lớp với `CHECK-T09B-16` ("bản cũ hơn không được âm thầm thắng nguồn bền").

Sửa (tối thiểu, ~20 dòng): `persist()` ghi qua `runTransaction` đọc `rev` hiện có và chỉ ghi khi
`serverRev === durableRev` mà trang đã nạp/ghi lần cuối; lệch → từ chối `stale-durable`, KHÔNG ghi
đè, banner "NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC" hướng dẫn *Tải về JSON* rồi tải lại. Không phải
conflict-resolution framework (không merge, không realtime) — chỉ một tiền điều kiện ghi. Kịch bản
hai tab được thêm vào `CHECK-T09B-16` và PASS. Hệ quả kèm theo: lệnh ghi khi mất mạng nay bị SDK từ
chối `unavailable` sau vài giây (transaction cần mạng) thay vì treo vô hạn → visible sớm hơn; app tự
ghi lại khi có sự kiện `online`. Phần còn hở → `F-T09B-03`/`H-25`.

### F-T09B-02 — Trần 1 MiB/document Firestore với `ethdca/state` (ledger tăng không giới hạn)
Phân loại: **HARDENING (PROVISIONAL)** → `H-24`

Không dựng được từ nguồn canonical nào (sổ demo cỡ KB); "sẽ xảy ra sau nhiều năm" là Forbidden
Justification. Khi chạm trần app hiện "CHƯA LƯU — invalid-argument" (không mất bản local) nhưng cần
`ARCHITECTURE_CHANGE_REQUIRED` (tách document) — đúng điều kiện `DEC-020` (2) đã dự liệu.

    RE_TRIGGER_CONDITION: document thật > 512 KiB; hoặc ledger > 3.000 bút toán; hoặc Owner thấy
    "invalid-argument" khi lưu.

### F-T09B-03 — Thay đổi bị từ chối `stale-durable` chỉ còn trong bộ nhớ tab
Phân loại: **HARDENING (CONFIRMED)** → `H-25`

Sau khi bị từ chối, nếu người dùng tải lại mà không export, thay đổi đó mất (mirror có cùng `rev`
với bản bền nên không bị xem là lệch). KHÔNG âm thầm: chip "CHƯA LƯU", banner nêu cách giữ. Đóng hẳn
cần stash theo nội dung — thuộc phạm vi conflict-resolution mà `DEC-021` (9)-(10) để ngoài V1.

    RE_TRIGGER_CONDITION: Owner gặp banner này trên sổ thật; hoặc H-23 kích hoạt lại.

### F-T09B-04 — `validateState()` giả định `base_pct + smart_pct + opportunity_pct = 1`
Phân loại: **HARDENING (CONFIRMED)** → `H-26`

Bất biến "TOTAL = A+R+D" được đo bằng `contribution = Σbase + Σsmart + oppAdded` (và
`oppFund = Σ oppAdded`), đúng với config 50/30/20 hiện tại và bảo toàn qua mọi thao tác kể cả
dưới lỗi V-01/V-02 cũ (đã suy luận từ mã: release/reserve chỉ dịch chuyển a↔r↔d trong một tháng).
Config tương lai có tổng ≠ 1 sẽ làm mọi sổ hợp lệ bị bác (fail closed). Cùng lớp: nếu JSON thật của
Owner (xuất từ bản artifact) lệch đẳng thức vì lý do chưa biết, *Nạp lại từ JSON* sẽ từ chối và nêu
tháng — đúng gate L, nhưng Owner cần biết trước.

    RE_TRIGGER_CONDITION: đổi tổng tỷ lệ config; hoặc import JSON thật bị từ chối vì "TOTAL = A+R+D".

### F-T09B-05 — `PRODUCTION_PATHS.md` §1 chưa khai `firebase_config.js`, `firestore.rules`, `firebase.json`
Phân loại: **HARDENING (CONFIRMED, tầng governance)** → `H-27` · Capability: `CAP-GOVTOOL` · Owner: chưa có

Ba file có đường runtime thật (config nhúng vào trang; rules gate mọi read/write; hosting). Khai báo
production path là giá trị PROJECT do chủ dự án đặt — phiên này không tự sửa, chỉ báo cả hai phép đo
ở §1. Cùng khe với `H-12`/`H-21`.

    RE_TRIGGER_CONDITION: Owner cập nhật PRODUCTION_PATHS.md; hoặc một phiên dùng số "theo khai báo"
    để tuyên bố diff = 0 trong khi ba file này đổi.

### Giới hạn bằng chứng — KHÔNG phải finding về mã: project Firebase thật chưa tồn tại
Phân loại: **OWNER_INPUT_REQUIRED** (không phải task, không phải BLOCKING của mã)

Toàn bộ E1 chạy trên Firebase Emulator Suite (rules engine + Auth + Firestore của Google chạy cục
bộ, SDK thật). Chưa có project thật, chưa deploy Hosting thật, thẻ `<script>` gstatic chưa được
tải thật (môi trường agent chặn gstatic; harness trả bản local cùng version). Production
reachability trên hạ tầng thật = **NOT_TESTED** và không được suy ra từ emulator (chỉ thị §14).
Việc cần Owner: tạo project, bật Anonymous, tạo Firestore, điền `firebase_config.js`, deploy, chép
UID vào rules, deploy rules, rồi lặp lại bằng tay chuỗi CHECK-01/02/03/04/14 trên app thật
(`webapp/README.md` § Thiết lập Firebase).

## 5. Những thứ đã soi và KHÔNG thành finding

- **`window.ETHDCA_DEBUG`** chỉ đọc (trả bản sao primitive), không mutate; cần cho bộ test chờ
  ack mà không đoán DOM. `ackTimeoutMs`/`emulator` trong config: nhánh emulator chỉ chạy khi config
  có khoá `emulator` (production không có).
- **`undefined`/`NaN` khi ghi Firestore**: `plain()` = `JSON.parse(JSON.stringify())` — đúng bản mà
  localStorage đã dùng từ WP-C1; không thêm/không đổi trường; NaN không phát sinh từ đường UI (mọi
  input được `Number.isFinite` gác).
- **Tên khoá Firestore**: khoá tháng `YYYY-MM`, id ladder `L<n>-<base36>` — không dấu chấm, không
  `__`; mảng lồng chỉ qua map (`ladders[].zones[]`) — hợp lệ.
- **Token Auth đã cache**: profile có session, Auth server không với tới → app vẫn ONLINE bằng
  token cache (≤ 1h), sau đó Firestore từ chối → OFFLINE visible. Đúng hành vi SDK, không âm thầm.
- **`wipeBtn`** ghi đè bản bền bằng sổ rỗng — hành động tường minh có `confirm` nêu rõ "kể cả bản
  bền trên Firestore"; hành vi có từ WP-C1.
- **`beforeunload`** chỉ bật khi ONLINE và còn lệnh chưa ack — không ảnh hưởng test/reload bình thường.
- **Rules placeholder** = mặc định deny toàn bộ cho tới khi Owner điền UID — an toàn.
- **`H-19`** (monthKey giờ địa phương): T-09B KHÔNG chốt lại ngữ nghĩa biên tháng → không re-trigger.
  **`H-20`** không đổi. **`H-23`**: đúng như dự liệu — UID lạ bị từ chối, banner phân biệt rõ.
- **Bảo trì 5 test cũ**: chỉ đổi cách mở trang và nguồn đọc state (durable + đối chiếu bit-exact);
  không assertion nào bị xoá/nới; bước 10 `test_app.js` (quine) thay bằng kiểm "không nhúng state".
- **Bỏ quine/`app-state`**: nằm trong "phạm vi cần thiết" của Task Spec — giữ chúng là giữ một nguồn
  state thứ ba trong trang, trái CHECK-T09B-16.

## 6. Verdict

    CONFIRMED BLOCKING (còn lại)   = 0   (F-T09B-01 đã sửa cùng lượt, có test)
    PROVISIONAL                    = 1   (F-T09B-02 -> H-24)
    HARDENING                      = 4   (F-T09B-02 -> H-24, F-T09B-03 -> H-25,
                                          F-T09B-04 -> H-26, F-T09B-05 -> H-27)
    OWNER_INPUT_REQUIRED           = 1   (project Firebase thật + xác nhận trên app thật)
    Task ID mới                    = 0

    VERDICT = PASS -> ELIGIBLE_FOR_FREEZE (advisory)

Theo `REVIEW_PROTOCOL.md` § Verdict, phán quyết này là **advisory**: phiên này KHÔNG ghi `FROZEN`
và KHÔNG ghi `DONE`. Chuyển T-09B sang `DONE` là hành vi của chủ dự án (`STATE_AUTHORITY.md`) và
nên chờ xác nhận trên project thật (mục "Giới hạn bằng chứng").

## 7. Hệ quả budget

Lượt `4502ea6..0d4917a` là **implementation ban đầu** của T-09B, không phải repair cycle. Batch
review trả 0 BLOCKING còn lại nên **không** phát sinh lượt sửa sau review.

    CAP-WEBAPP repair cycles USED = 0   (vẫn 0 sau phiên này; ALLOWED 2, REMAINING 2)
