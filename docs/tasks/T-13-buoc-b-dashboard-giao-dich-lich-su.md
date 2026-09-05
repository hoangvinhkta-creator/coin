# T-13 — CoinDCA L-1 Bước B: Dashboard hằng ngày + Nhập giao dịch/Lịch sử

## Metadata
Status:
READY

Hiện hành: Task được mở và đưa thẳng lên `READY` trong cùng phiên định nghĩa (`S035`,
2026-09-05), theo đúng thẩm quyền Owner của chỉ thị phiên "COINDCA — L-1 STEP B DEFINITION"
(ghi lại thành `DEC-047`, `PROJECT/PROJECT_DECISIONS.md`) — cùng khuôn `T-12` tại `S032`
(`NOT_PLANNED → READY` trong một phiên, trước khi có phiên thi hành riêng). Phiên này **KHÔNG**
thi hành: production diff = EMPTY, không chuyển `IN_PROGRESS`.

Phase:
CoinDCA L-1 — bước **B** (dashboard §16 + UX nhập/sửa/xoá + lịch sử §15) của chuỗi A → B → C → D
(`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §24)

Task Mode:
MAJOR

Lớp (RCP-001):
Không thuộc RCP-001. `T-13` là hạng mục roadmap mới của đường sản phẩm L-1 (`DEC-041` C /
`DEC-047`), không phải work package tách ra từ một task V2.1.5.

Completion Gate Freeze:
FROZEN — 2026-09-05 (`S035`, cùng phiên tạo task). Sau mốc này, không REQUIRED check nào được
xoá hoặc làm yếu; mọi thay đổi phải đi qua khối `COMPLETION GATE CHANGE PROPOSAL`
(`governance/core/TASK_COMPLETION_GATE_STANDARD.md` § Gate Change Control).

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới, **KHÔNG** tạo lineage root
mới.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 3
A: 2
X: 3
U: 2
V: 3
H: 3
C: 3
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.85

Effort Routing Score:
2.8

Applied Model Floor:
safety_business:min_C

Applied Effort Floor:
safety_business:min_high

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
C

Escalation Effort:
xhigh

Difficulty:
3/4

Risk:
3/4

Blast Radius:
3/4

Project Profile:
PRODUCT

### Ghi chú chấm điểm routing (đối chiếu với chính repo, không phải cảm tính)

- `D = 3` — thấp hơn `T-12` (`D=4`, phát minh mô hình kế toán) vì Step B **không** tạo công thức
  tài chính mới, chỉ tiêu thụ `derive()`/`update()`/`migrate()`/`destructive()` đã đóng băng. Vẫn
  cao hơn một UI thuần tuý vì phải: (a) ánh xạ đúng 8 loại sự kiện vào đúng `action.type`/trường
  bắt buộc (kể cả `note` bắt buộc cho `RESERVE`) mà không lệch ngữ nghĩa; (b) gỡ bỏ ~900 dòng
  dead code + markup V2.1.5 (`app_logic.js`, `app_shell.html`) mà không chạm hành vi tài chính
  đang chạy; (c) thiết kế lại toàn bộ IA/mobile mà không phá vỡ các hook `state()/commit()/
  canWrite()/snapshot()` đã có.
- `R = 3` — cùng mức `T-09A`/`T-09B`/`T-12`: một người dùng, không bên thứ ba; hậu quả sai không
  phải mất dữ liệu không hồi phục (mọi ghi/sửa/xoá đều qua `update()`/`destructive()` đã có
  invariant + snapshot bắt buộc — `INV-14`), nhưng một UI ánh xạ sai loại sự kiện (ví dụ hiển
  thị nhầm EXTRA thành PLAN) có thể khiến người dùng tin sai vào kỷ luật DCA của chính họ mà
  không có lỗi kỹ thuật nào báo động (ledger.js không biết UI "nói dối" nhãn nào cho người dùng).
- `B = 3` — cùng mức `T-09B`/`T-12`: Step B là bề mặt UI CHÍNH của toàn bộ sản phẩm L-1 — một
  lỗi trình bày sai ở Tổng quan/Lịch sử ảnh hưởng **mọi** phiên sử dụng hằng ngày, không chỉ một
  đường kế toán hẹp.
- `A = 2` — spec kế toán canonical đã đóng băng đầy đủ (4 quyết định `DEC-042`); Step-B spec
  (`docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md`) đã chốt toàn bộ lựa chọn UX còn lại trong cùng
  phiên này (IA, form, mobile) — không còn câu hỏi mở cần Owner. Giữ `A=2` thay vì `1` vì vẫn còn
  rủi ro diễn giải khi ánh xạ 8 loại sự kiện + dọn dẹp dead code legacy đúng ranh giới.
- `X = 3` — cùng mức `T-09B`/`T-12`: UI mới ↔ `webapp/ledger.js` (không sửa nội dung) ↔
  `webapp/app_logic.js` (hooks + persistence Firestore) ↔ `webapp/app_shell.html` (markup/CSS) ↔
  `webapp/build_app.js` (bundler) ↔ harness test (`test_firebase_harness.js`) — nhiều bề mặt
  phải giữ nhất quán đồng thời, không có HTTP API tách rời.
- `U = 2`, `V = 3`, `H = 3`, `C = 3`, `F = 3` — xác minh chủ yếu là hồi quy (12 golden scenario +
  15 bất biến của `T-12` phải giữ nguyên qua toàn bộ đường UI mới, không phải chứng minh bất
  biến mới), nhưng khối lượng kịch bản UX (AS-01…AS-12) + production reachability qua giao diện
  MỚI (không phải panel tối giản cũ) + dọn dẹp dead code trên diện rộng giữ `V`/`H`/`C` ở mức
  `3` (high), không phải `2`.

Bằng chứng router (chạy lại được):

    python governance/scripts/governance/routing_engine.py \
      --d 3 --r 3 --b 3 --a 2 --x 3 --u 2 --v 3 --h 3 --c 3 --f 3 \
      --category accounting_financial
    -> tier=C model=Opus model_score=2.85 effort=xhigh effort_score=2.8

Không có `Manual Override`: giá trị khai trùng đúng đầu ra router.

---

## Objective

Biến sự thật tài chính canonical của `T-12` (`openingPosition + events -> derive() -> 4 con số
dashboard`) thành **công cụ dùng được hằng ngày**: một dashboard đúng Dashboard Contract §16, một
luồng nhập giao dịch bao phủ 8 loại sự kiện (§5 của
`docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md`), một màn lịch sử có filter/tìm kiếm/chi tiết, một
luồng sửa/xoá an toàn, và một IA di động-trước gọn còn 4 điểm đến — **không** tạo bất kỳ công
thức tài chính mới nào và **không** bật SELL cho dữ liệu thật.

## Product consequence

Không có bước B thì bước A (`T-12`, sự thật tài chính) không ai dùng được ngoài panel tối giản
`ledger_ui.js` hiện tại — đủ đúng để test nhưng không đủ để chủ dự án dùng "hằng ngày" như mục
tiêu cuối của `PROJECT_PROFILE.md` đòi hỏi ("Bốn con số trung tâm: ngân sách tháng · đã đầu tư ·
còn lại · ngày mua kế tiếp"). `T-13` là hạng mục **duy nhất** biến bốn con số đó từ "tính đúng
trong test" thành "nhìn thấy được trong vài giây trên điện thoại".

Cảnh báo **"dừng dùng app với tiền thật không giới hạn"** vẫn còn hiệu lực trong và sau `T-13`:
`T-13` chỉ mở bước B của spec §22/§24; bước **C** (`H-42`, Firebase isolation) và bước **D**
(`OWNER_LOCAL_ACCEPTANCE`, §22.1) nằm ngoài task này.

## Scope IN

| # | Hạng mục | Neo spec |
|---|---|---|
| S-B1 | IA 4 điểm đến: Tổng quan / Lịch sử / Kế hoạch / Cài đặt + FAB "+ Ghi giao dịch" toàn cục | Step-B spec §3 |
| S-B2 | Dashboard: khối chính 4 số + 1 hành động, khối dưới, banner bắt buộc không dismiss được | Step-B spec §4, spec kế toán §16 |
| S-B3 | Sheet nhập giao dịch cho 8 loại sự kiện (đúng ánh xạ `action.type`/`event.kind` đã đóng băng) | Step-B spec §5, spec kế toán §5.3 |
| S-B4 | Lịch sử có filter/tìm kiếm/chi tiết, thay thế danh sách `<p>` phẳng | Step-B spec §6 |
| S-B5 | Sửa/xoá qua UI với dialog cảnh báo + snapshot tự động trước khi xoá (gọi đúng `destructive()`) | Step-B spec §7, spec kế toán §15 |
| S-B6 | Màn Kế hoạch: ngân sách/lịch/carry tách riêng hiển thị, Số dư đầu kỳ sửa một chỗ | Step-B spec §8, spec kế toán §11/§14 |
| S-B7 | UNKNOWN UX nhất quán (banner + `—` + không tự ẩn) | Step-B spec §9 |
| S-B8 | Dọn dẹp dead code/markup V2.1.5 khỏi đường L-1 (`REMOVE_FROM_L1_PATH` ở Step-B spec §12) — KHÔNG sửa nội dung `engine.js` | Step-B spec §12 |
| S-B9 | Responsive di động: bottom-nav, card-based history, `inputmode` số, breakpoint | Step-B spec §10 |
| S-B10 | Ẩn hoàn toàn tuỳ chọn SELL khỏi mọi form/menu | Step-B spec §11 B-1 |
| S-B11 | Khai báo mọi file runtime MỚI vào `PROJECT/PRODUCTION_PATHS.md` §1 trong CÙNG task (không lặp lại `H-32`) | tiền lệ `T-09B`/`T-12` |
| S-B12 | Production reachability PR-1…PR-6 qua `app_final.html` + UI mới + Firestore Emulator | Step-B spec §15 |

## Scope OUT (Non-goals tường minh)

| # | KHÔNG làm | Lý do / neo |
|---|---|---|
| O-1 | Bật SELL cho dữ liệu thật, realized P&L | `H-46`/`F-E2-03` chưa có Owner Decision riêng |
| O-2 | Firebase project riêng, Google Sign-in, đổi `firebase.json`/`firestore.rules`/Hosting | Bước C (`H-42`), Step-B spec §11 B-2 |
| O-3 | Buy Score, Opportunity Score, regime, crash ladder, recommendation engine, tab Research | `DEC-041` B, `H-43`, Step-B spec §11 B-3 |
| O-4 | Nhắc lịch/thông báo | `D-6` spec kế toán §23, `T-08`/`T-10` DEFERRED |
| O-5 | Tax lot, sổ lãi/lỗ đã thực hiện | `D-5` spec kế toán §23 |
| O-6 | Nhiều tài sản ngoài ETH, lấy giá tự động | `D-4`/`D-7` spec kế toán §23 |
| O-7 | Tombstone/audit trail đầy đủ, undo sau khi lưu | `D-8` spec kế toán §23 |
| O-8 | Bất kỳ thay đổi nào cho `derive()`/`update()`/`migrate()`/`destructive()`, schema `coindca.ledger/2`, các bất biến `INV-1`…`INV-15` | Step B chỉ tiêu thụ API đã đóng băng của `T-12`; đổi công thức = mở lại `T-12`, không phải `T-13` |
| O-9 | Dữ liệu tài chính THẬT của Owner | `DEC-041` C |
| O-10 | Sửa `src/eth_dca_os/**` và `docs/spec/**`, `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` | frozen/canonical, ngoài quyền `T-13` |
| O-11 | Sửa nội dung `webapp/engine.js` | `INV-10`, ngoài đường tiền L-1; giữ nguyên cho khả năng Research tab tương lai (`H-43`) |
| O-12 | Đổi ranh giới persistence `ethdca/state`/`ethdca/seed` hay format serialize đã đóng băng ở `T-12` | thuộc `T-12`, không phải `T-13` |

**Không được mở rộng phạm vi chỉ vì mã legacy lân cận lộn xộn.** Chạm ngoài Expected Touch Area →
khối `SCOPE EXPANSION REQUIRED`, không sửa im lặng.

## Dependencies

| Dependency | Trạng thái | Bằng chứng |
|---|---|---|
| `DEC-041` — L-1 canonical transition | effective | `PROJECT_DECISIONS.md` |
| `DEC-042` — spec kế toán L-1 `CANONICAL — APPROVED` | effective | `PROJECT_DECISIONS.md` |
| `DEC-047` — Owner direction Step B; mở task ID | effective (phiên này) | `PROJECT_DECISIONS.md` |
| `docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md` | `CANONICAL — APPROVED` (`DEC-047`) | header spec |
| `T-12` — Sổ cái L-1 v2 + `derive()` | DONE (`DEC-046`) | `docs/tasks/T-12-so-cai-l1-v2-va-derive.md` |
| `WP-C1`, `T-09A`, `T-09B`, `WP-C2` (lineage `CAP-WEBAPP`) | DONE | roadmap |

Không dependency nào đang mở.

## Blocks

- Bước **D** (`OWNER_LOCAL_ACCEPTANCE`, spec kế toán §22.1) — chỉ có nghĩa sau A + B + C.
- Không chặn bước **C** (`H-42`) — hai bước độc lập kiến trúc (Step B không chạm Firebase/auth).

## Parallel-Safe With

- Nếu bước C (`H-42`, Firebase project riêng) được mở sau này, nó **không** giao Expected Touch
  Area với `T-13` (`T-13` không chạm `firebase.json`, `firestore.rules`,
  `webapp/firebase_config.js`).
- Không có task nào khác đang `READY`/`IN_PROGRESS` trong `CAP-WEBAPP` tại thời điểm tạo.

## Expected Touch Area

Allowed (production path):
- `webapp/app_shell.html` — thay markup/CSS 5-tab V2.1.5 bằng IA 4 điểm đến + sheet nhập liệu +
  bottom-nav di động; XOÁ markup dead-code V2.1.5 (`#tab-dash` hero, `#tab-ladder`, action box,
  form nhập cũ). KHÔNG đổi CSS component library nền (`.card`/`.stat`/`.form`/`table` — REUSE)
- `webapp/ledger_ui.js` — thiết kế lại/mở rộng đáng kể theo Step-B spec §4-§9 (dashboard, sheet
  nhập 8 loại, lịch sử filter/chi tiết, kế hoạch/carry); vẫn CHỈ gọi
  `CoinLedger.derive/update/migrate/destructive`, không viết phép tính tài chính mới
- `webapp/<module UI mới nếu tách nhỏ>.js` (tuỳ chọn implementer, ví dụ tách `dashboard_ui.js`/
  `history_ui.js` khỏi `ledger_ui.js` cho dễ bảo trì) — **bắt buộc** khai vào
  `PROJECT/PRODUCTION_PATHS.md` §1 trong CÙNG task (S-B11, tránh lặp lại `H-32`)
- `webapp/app_logic.js` — XOÁ các hàm dead code V2.1.5 (`recompute`, `renderDash`, `renderLadder`,
  `renderAction`, `deriveRegime`, `buildLadder`/`createLadder`/`releaseLadder`/`cancelLadder`,
  banner engine-parity); GIỮ NGUYÊN `persist()`, `renderPersistence()`, hooks Firebase/mirror
  đang chạy thật (không phải dead code)
- `webapp/build_app.js` — thêm module UI mới (nếu tách file) vào bundle

Allowed (không phải production path):
- `webapp/test_*.js` (test mới của Step B), fixture tổng hợp
- `docs/tasks/T-13-*.md`, `docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md`, `docs/reviews/`,
  `docs/sessions/`
- `PROJECT/PRODUCTION_PATHS.md`, `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`,
  `PROJECT/REVIEW_BUDGET_LEDGER.md`, `PROJECT/HARDENING_BACKLOG.md`

Do not touch without Scope Expansion:
- `webapp/ledger.js` — sự thật tài chính đã đóng băng ở `T-12`; Step B chỉ **gọi**, không sửa
- `webapp/engine.js` — chỉ báo/OSCORE, ngoài đường tiền L-1 (`INV-10`, `O-11`)
- `src/eth_dca_os/**` — frozen historical research authority (`DEC-041` A)
- `docs/spec/**`, `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` — cấm sửa
- `firebase.json`, `firestore.rules`, `webapp/firebase_config.js` — bước C (`H-42`)
- `pyproject.toml`, `pyproject.lock`
- `webapp/test_t12_*.js`, `test_t09a_accounting.js`, `test_t09b_persistence.js`,
  `test_v01_v02_v03.js`, `test_zone.js`, `test_multi_month_invariant.js`, `test_app.js` — không
  được làm yếu/bỏ chọn để lấy suite xanh (đúng tiền lệ `T-12` `CHECK-T12-13`)

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. Mọi con số hiển thị PHẢI đến từ `CoinLedger.derive()` — không tính lại trong UI, không cache
   một bản sao rồi tự cộng dồn (lặp lại đúng lỗi B1-B10 mà `T-12` đã diệt).
2. Mọi ghi dữ liệu PHẢI qua `CoinLedger.update()`/`migrate()`/`destructive()` — không viết
   thẳng vào `state` từ UI.
3. Không thêm trường tỷ giá nhập tay theo từng lệnh (`OD-L1-4`), dù chỉ tạm thời cho UI.
4. SELL bị ẩn hoàn toàn khỏi mọi form/menu (S-B10) — không hiển thị dạng "sắp có".
5. Xoá vẫn là hard delete kèm snapshot bắt buộc trước khi xoá (`INV-14`) — UI không tự thêm lớp
   tombstone/tự thêm lớp undo.
6. Không đổi `firestore.rules`/`firebase.json`/`webapp/firebase_config.js`.
7. File runtime MỚI phải khai vào `PROJECT/PRODUCTION_PATHS.md` §1 trong CÙNG task.

---

## Change budget (ước lượng có ràng buộc)

**Phạm vi con số này:** budget **cấp task**, KHÔNG khai `SESSION_PRODUCTION_DIFF_MAX` /
`GOLDEN_CUMULATIVE_DIFF_MAX` tầng dự án (vẫn `PENDING_OWNER_DATA` — `H-10`, không đổi).

    MỐC ĐO CẤP TASK (không phải Golden baseline):
      T13_MEASURE_BASE_SHA = <SHA của origin/main tại thời điểm mở phiên thi hành T-13>
      (ghi lại tại phiên thi hành đầu tiên — chưa tồn tại tại thời điểm định nghĩa task)

    Lệnh đo (không cộng tay từ báo cáo):
      git diff --shortstat <T13_MEASURE_BASE_SHA>..HEAD -- \
        webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js \
        webapp/ledger_ui.js webapp/ledger.js src/eth_dca_os pyproject.toml pyproject.lock

| Hạng mục | Ước lượng | Trần |
|---|---|---|
| File production dự kiến | `app_shell.html`, `app_logic.js`, `ledger_ui.js` sửa; 0-2 module UI mới (nếu tách nhỏ) | ≤ 8 file |
| File test dự kiến | 4-6 mới (`webapp/test_stepb_*.js`, mở rộng `test_firebase_harness.js` cho kịch bản UI) | — |
| Diff production | Xoá nhiều hơn thêm ròng do dọn dead code V2.1.5 (~-900 dòng dead trong `app_logic.js`, ~-300 dòng markup trong `app_shell.html`); thêm UI mới ước ~+1.200 | **+1.800 / −1.400** |
| Diff test | ≈ +1.500 | — |
| Repair cycle tối đa | rút từ pool `CAP-WEBAPP` hiện có (§ Budget review/repair dưới đây) | — |
| Vòng E2 dự trù | 1 (độc lập, cho các check REQUIRED có E2 — xem Completion Gate) | — |

Vượt trần production **hoặc** thêm file production ngoài danh sách Expected Touch Area → dừng và
ghi `CHANGE_BUDGET_EXCEEDED` hoặc `SCOPE_CHANGED`, quay lại Owner. **Không** âm thầm mở rộng.

## Budget review/repair

    Lineage root          = WP-C1  (CAP-WEBAPP)
    ALLOWED (capability)  = 2 repair cycle   (Owner Decision DEC-018 / OD-WEBAPP-01)
    USED                  = 1   (REPAIR_CYCLE_1, tiêu bởi T-12, DEC-043, KHÔNG đổi bởi T-13)
    REMAINING             = 1
    T-13 tại thời điểm mở = KHÔNG tự cấp thêm, KHÔNG pre-authorize gì (khác `T-12`/`DEC-043`) —
                            nếu implementation cần một repair cycle, đó là RÚT từ 1 chu kỳ
                            REMAINING hiện có của `CAP-WEBAPP`, theo đúng quy trình
                            `CAPABILITY_MODEL.md` §II.8 (Owner Decision riêng khi FAIL thật xảy
                            ra, không phải cấp trước)

Lượt thi hành đầu tiên của `T-13` là **INITIAL IMPLEMENTATION** — theo đúng tiền lệ đã ghi cho
`CAP-PROV`, `CAP-DATA`, và chính `CAP-WEBAPP` (`T-09A`/`T-09B`/`WP-C2`/`T-12`): không tự động
tiêu repair cycle. Nếu một REQUIRED check FAIL sau implementation ban đầu và cần sửa lại, đó là
lúc `USED` tăng 1→2 với cặp BASE/HEAD SHA ghi vào `REVIEW_BUDGET_LEDGER.md` §2.2, và
`REMAINING` về 0 — hết đó chỉ còn `ACCEPT_AS_IS`/`DESCOPE`/`OWNER_EXTENSION`.

---

## Ready Gate

`governance/core/TASK_READY_GATE_STANDARD.md` § MAJOR — đánh giá tại `S035` (2026-09-05):

- [x] Objective rõ ràng — § Objective, neo Step-B spec toàn bộ
- [x] Scope được định nghĩa — `S-B1`…`S-B12`
- [x] Out-of-scope được định nghĩa — `O-1`…`O-12`
- [x] Dependencies DONE hoặc effective — `T-12 DONE`, `DEC-041`/`DEC-042`/`DEC-047` effective,
      Step-B spec `CANONICAL — APPROVED`
- [x] Expected touch area đã xác định — § Expected Touch Area, có cả danh sách cấm chạm
- [x] Yêu cầu nghiệp vụ được hiểu — Step-B spec §1-§16 đầy đủ, không còn câu hỏi UX mở (Step-B
      spec §16 liệt kê rõ các lựa chọn đã chốt thay Owner)
- [x] Tác động dữ liệu đã biết — KHÔNG đổi schema `coindca.ledger/2`, KHÔNG đổi ranh giới
      persistence; chỉ tiêu thụ API đã đóng băng của `T-12`
- [x] Tác động bảo mật đã biết — không đụng auth/rules/hosting (`O-2`); `H-42` vẫn là điều kiện
      chặn TRƯỚC khi dùng tiền thật không giới hạn, `T-13` không gỡ điều kiện nào
- [x] Tác động routing/API đã biết — không có HTTP API; "API" là hợp đồng module
      `derive/update/migrate/destructive` đã đóng băng, Step B không đổi
- [x] Điều kiện tiên quyết migration sẵn có — luồng migration UI đã có ở `ledger_ui.js`
      (REUSE/ADAPT theo Step-B spec §12), không cần dữ liệu thật để bắt đầu hay hoàn tất gate UX
- [x] Difficulty đã chấm — 3/4
- [x] Risk đã chấm — 3/4
- [x] Blast Radius đã chấm — 3/4
- [x] Primary agent tier đã gán — C / Opus / xhigh, bằng chứng router chạy lại được
- [x] Escalation triggers đã định nghĩa — § Escalation Triggers
- [x] Completion Gate đã hoàn tất — 13 REQUIRED check dưới đây
- [x] Completion Gate đóng băng trước khi thi hành — `Completion Gate Freeze: FROZEN 2026-09-05`

**17/17 tương đương đạt** (14 mục MAJOR chuẩn + 3 mục bổ sung do category `accounting_financial`
đã gộp vào các dòng trên, cùng cách đếm `T-12` dùng). Không mục nào được đánh dấu thoả bằng lời
hứa tương lai. Nếu một mục ở trên hoá ra chưa thoả khi mở phiên thi hành, task quay về `PLANNED`.

---

## Completion Gate

`governance/core/TASK_COMPLETION_GATE_STANDARD.md` + `governance/core/EVIDENCE_STANDARD.md`.
13 check, **tất cả REQUIRED**. Trạng thái ban đầu: `NOT_TESTED`.

Quy ước Evidence của gate này (`Risk 3/4`, `Blast Radius 3/4`, category `accounting_financial`):
`E1` là tối thiểu bắt buộc cho mọi check thực thi được; các check liên quan tới ánh xạ sự kiện
tài chính, sửa/xoá, plan/carry, và production reachability thêm **E2 độc lập** — theo đúng quy
ước `T-12` đã dùng.

### UX / Product

#### CHECK-T13-01 — IA 4 điểm đến hoạt động đúng, refresh-safe
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: 4 điểm đến (`#/dashboard`, `#/history`, `#/plan`, `#/settings`) điều hướng được, refresh
giữ đúng màn hình, không có tab/markup V2.1.5 nào còn hiển thị (Step-B spec §12
`REMOVE_FROM_L1_PATH`).

#### CHECK-T13-02 — Dashboard đúng Dashboard Contract §16, không sai một trường
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: khối chính 4 số + 1 hành động, khối dưới, banner bắt buộc — đối chiếu **tuyệt đối**
(tolerance 0) với `derive()` trên fixture `SC-09`/`SC-10`. Không "GO"/"WAIT"/màu tín hiệu ở thẻ
"Mua kế tiếp" (`DEC-041` B).

#### CHECK-T13-03 — Sheet nhập liệu ánh xạ đúng 8 loại sự kiện
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: mỗi loại trong bảng Step-B spec §5 sinh đúng `action.type`/`event.kind`/trường bắt buộc;
`RESERVE` buy thiếu `note` bị chặn tại form; không có ô nhập tỷ giá riêng theo lệnh nào tồn tại
trong DOM (grep xác nhận).

#### CHECK-T13-04 — Lịch sử: filter/tìm kiếm/chi tiết/UNKNOWN badge đúng
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: lọc theo loại/khoảng ngày/tháng lịch hoạt động đúng trên tập dữ liệu tổng hợp ≥ 12 sự
kiện đủ loại; badge EXTRA/RESERVE hiển thị đúng; badge UNKNOWN không rò rỉ `realizedFxVnd` hay số
nội bộ nào khác (giữ `H-45` không bị mở rộng — Step-B spec §6).

#### CHECK-T13-05 — Sửa qua UI tính lại đúng, `id`/`seq` không đổi
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: sửa một sự kiện qua form → `derive()` chạy lại toàn bộ, Tổng quan/Lịch sử khớp ngay;
`id`/`seq` bất biến (`INV-15`).

#### CHECK-T13-06 — Xoá qua UI: cảnh báo + snapshot bắt buộc trước khi xoá
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: dialog cảnh báo tường minh xuất hiện; snapshot export tự động được tạo TRƯỚC khi xoá
thật (`INV-14`, gọi đúng `CoinLedger.destructive()`); sau xoá số liệu như giao dịch chưa từng tồn
tại; xoá Số dư đầu kỳ có cảnh báo RIÊNG mạnh hơn.

#### CHECK-T13-07 — Kế hoạch/Carry: ba đại lượng tách riêng, không cần tự tính
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: `monthlyBudgetVnd`/`carryInVnd`/`investedThisMonthVnd` (hoặc `planInvestedVnd`) hiển thị
tách biệt, không gộp; "Mua kế tiếp" đúng theo `scheduleDays`/carry của fixture `SC-09` (tolerance
0); sửa `scheduleDays`/`monthlyBudgetVnd` áp dụng đúng từ tháng hiệu lực, không hồi tố (`§11.1`).

#### CHECK-T13-08 — UNKNOWN UX nhất quán, không tự ẩn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: mọi nơi giá vốn VND UNKNOWN hiển thị `—` (không phải 0/trống/NaN); banner
`UNKNOWN_VND_BASIS` thường trực, không có nút ẩn vĩnh viễn nào tồn tại trong DOM.

#### CHECK-T13-09 — SELL bị ẩn hoàn toàn
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: grep toàn bộ UI mới — không có tuỳ chọn "SELL"/"Bán" ở bất kỳ form/menu nào; không màn
hình nào hiển thị lãi/lỗ đã thực hiện.

#### CHECK-T13-10 — Không công thức tài chính mới, chỉ gọi API đã đóng băng
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: (a) grep UI mới — mọi con số hiển thị truy được nguồn gốc về đúng một lệnh gọi
`CoinLedger.derive()`; (b) mọi ghi dữ liệu truy được về đúng
`CoinLedger.update()/migrate()/destructive()`; (c) không hàm nào trong UI tự cộng/trừ/nhân tiền
độc lập với các hàm trên.

#### CHECK-T13-11 — Di động: bottom-nav, ≤ 3 chạm cho hành động phổ biến, không cuộn ngang
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: trên khung hình ≤ 400px, FLOW-1…FLOW-7 (Step-B spec §13) thực hiện được; ghi một giao
dịch PLAN từ Tổng quan tốn ≤ 3 lần chạm; không phần tử nào gây cuộn ngang.

### Regression / Production Reachability

#### CHECK-T13-12 — Hồi quy T-12 không bị phá vỡ
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E1

Yêu cầu: toàn bộ suite `test_t12_*.js` + Python `678/678` vẫn PASS sau khi Step B hoàn tất; không
`INV-1`…`INV-15` nào bị làm yếu; không test cũ nào bị bỏ chọn/skip để lấy suite xanh.

#### CHECK-T13-13 — Production Reachability PR-1…PR-6 qua UI mới
Priority: REQUIRED · Status: NOT_TESTED · Evidence Level: E2

Yêu cầu: đúng định nghĩa Step-B spec §15 — toàn bộ AS-01…AS-11 chạy qua `app_final.html` +
Firestore Emulator + `firestore.rules` thật, không gọi hàm module trực tiếp trong Node; reload
khớp tuyệt đối (tolerance 0).

---

## Exit Criteria
- [ ] 13/13 REQUIRED check PASS
- [ ] Không finding BLOCKING chưa đóng
- [ ] Evidence Level đạt tối thiểu theo quy ước gate (E1 toàn bộ, E2 cho các check đã đánh dấu)
- [ ] `PROJECT/PRODUCTION_PATHS.md` §1 khai đủ mọi file runtime mới (S-B11)
- [ ] `PROJECT/PROJECT_PROGRESS.md` cập nhật (Last Updated, Current Task Snapshot, roadmap row)
- [ ] Session handoff viết theo Task Mode MAJOR

## Escalation Triggers
- Nếu implementation phát hiện việc ẩn SELL đòi sửa `webapp/engine.js` hoặc `webapp/ledger.js` →
  DỪNG, `SCOPE EXPANSION REQUIRED`, không tự sửa ngoài Expected Touch Area.
- Nếu dọn dead code V2.1.5 ở `app_logic.js` vô tình chạm logic Firebase/persistence đang chạy
  thật (`persist()`, `renderPersistence()`) → DỪNG, đối chiếu lại ranh giới REUSE ở Step-B spec
  §12 trước khi tiếp tục.
- Nếu một REQUIRED check của `T-12` (đã FROZEN) FAIL vì thay đổi của `T-13` → đây là dấu hiệu
  `T-13` đã chạm vào lớp tài chính bị cấm (`O-8`) — DỪNG ngay, `ARCHITECTURE_CHANGE_REQUIRED`,
  không tự "sửa nhanh" `ledger.js`.
- Nếu trần diff production (§ Change budget) bị vượt hoặc cần repair cycle thứ hai của
  `CAP-WEBAPP` (REMAINING đã về 0 sau chu kỳ đầu) → `CHANGE_BUDGET_EXCEEDED` /
  `OWNER_DECISION_REQUIRED`, không tự cấp thêm.

## Changed Files Registry

Created:
- (chưa có — phiên định nghĩa, production diff = EMPTY)

Modified:
- (chưa có)

Deleted:
- (chưa có)

Migration Impact:
- Không có (Step B không đổi schema/serialize — chỉ tiêu thụ API đã đóng băng của `T-12`)

## Notes

`T-13` được mở đúng theo năm câu hỏi của `CAPABILITY_MODEL.md` § Capability-First Question Order
(ghi tại `PROJECT/CAPABILITY_REGISTRY.md` §15, cùng khuôn `T-12` §2.1): (1) cần cho lát cắt ACTIVE
— **CÓ**, bước B là mắt xích bắt buộc để "4 con số dashboard" thật sự dùng được hằng ngày; (2)
thuộc capability đã có — **CÓ**, `CAP-WEBAPP`; (3) task/owner gần nhất — không có task nào đang
mở trong `CAP-WEBAPP` (`T-12` đã `DONE`); (4) hấp thụ vào owner đó có vượt Absorption Limit không
— không áp dụng, đây là mở task MỚI chứ không phải hấp thụ; (5) đưa lên Owner — **đã có**, chỉ
thị phiên "COINDCA — L-1 STEP B DEFINITION" (`DEC-047`).

`T-13` **không** phải sibling task tách ra để giải phóng budget: nó dùng chung pool của lineage
root `WP-C1` (`allowed 2 / used 1 / remaining 1`) và không đặt lại con số nào. Số task ID mới do
phiên `S035` tạo = **1** (`T-13`); số capability mới = **0**; số lineage root mới = **0**; số
proposal mới = **0**; số `OWNER_ASSIGNMENT_REQUIRED` mới = **0**.
