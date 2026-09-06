# T-14 — CoinDCA L-1 Bước C: Firebase Isolation, Owner Auth bền vững, Backup/Recovery

## Metadata
Status:
IMPLEMENTED

Hiện hành: `READY → IN_PROGRESS → IMPLEMENTED` tại phiên thi hành `S039` (2026-09-06, nhánh
`claude/t14-step-c-firebase-isolation-xu6nxb`). Ready Gate được xác nhận lại còn hiệu lực TRƯỚC
khi viết dòng mã production đầu tiên (17/17, `docs/reviews/T14-IMPLEMENTATION-REPORT.md` §3).
12/12 REQUIRED check của Completion Gate PASS ở mức E1. **KHÔNG** chuyển `DONE` — chuyển
`IMPLEMENTED → DONE` thuộc thẩm quyền chủ dự án (`STATE_AUTHORITY.md`), sau independent E2 đúng
tiền lệ `T-09B`/`T-12`/`T-13`. Endpoint của phiên thi hành: **IMPLEMENTED — E2_REQUIRED**.

Lịch sử: Task được mở và đưa thẳng lên `READY` trong phiên định nghĩa (`S038`,
2026-09-06), theo đúng thẩm quyền Owner của chỉ thị phiên trực tiếp "COINDCA — L-1 STEP C
DEFINITION" (ghi lại thành `DEC-049`, `PROJECT/PROJECT_DECISIONS.md`) — cùng khuôn `T-12`
(`S032`) và `T-13` (`S035`): `NOT_PLANNED → READY` trong một phiên định nghĩa, trước khi có
phiên thi hành riêng. **Không implementation nào diễn ra trong phiên này** — production diff của
phiên `S038` = EMPTY (chỉ tài liệu/task/PROJECT state).

Phase:
CoinDCA L-1 — bước **C** (chặn cứng trước khi ghi tiền thật: isolation + auth bền + backup/
snapshot, §18/§24 của `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md`) của chuỗi A → B → C
→ D. Spec thi hành: `docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md`
(`CANONICAL — APPROVED`, `DEC-049`).

Task Mode:
MAJOR

Lớp (RCP-001):
Không thuộc RCP-001. `T-14` là hạng mục roadmap mới của đường sản phẩm L-1 (`DEC-041` C /
`DEC-049`), không phải work package tách ra từ một task V2.1.5.

Completion Gate Freeze:
FROZEN — 2026-09-06 (`S038`, cùng phiên tạo task). Sau mốc này, không REQUIRED check nào được
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
authentication, security

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
D

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

- `D = 3` — thấp hơn `T-12` (`D=4`, phát minh mô hình kế toán): T-14 **không** tạo công thức tài
  chính mới, không đổi schema. Vẫn cao hơn một cấu hình đơn thuần vì phải: (a) thay cơ chế danh
  tính bền vững (Anonymous → Google Sign-In) mà không phá vỡ shape `firestore.rules` đang chạy;
  (b) thiết kế backup/restore atomic + preview/validate không mở lại `derive()`; (c) suy luận
  đúng hệ quả Auth dùng chung project (§6 spec bước C) mà không giả định sai
  "authenticated == Owner".
- `R = 3` — hậu quả sai là mất quyền truy cập dữ liệu chính mình (khoá nhầm UID) hoặc — nghiêm
  trọng hơn — vô tình mở quyền ghi cho người khác vào dữ liệu tài chính, hoặc làm hỏng rules
  Content dùng chung. Một người dùng, không bên thứ ba chịu hậu quả trực tiếp, nên không phải
  mức `4`.
- `B = 3` — đúng "Blast Radius — HIGH" của `RISK_MODEL.md` ("wrong identity, ownership or
  permission"; "a security/privacy boundary with a real consequence"): auth+rules quyết định ai
  chạm được vào toàn bộ sổ cái tài chính CoinDCA, và deploy sai có thể ảnh hưởng app Content dùng
  chung project. Không đạt Golden Reduction (chưa có Golden test nào phủ đúng path này).
- `A = 2` — phần lớn câu hỏi kiến trúc đã được Owner quyết định trong chính chỉ thị phiên (giữ
  project dùng chung, Google Sign-In, không di dời `ethdca/*`) — giữ `A=2` (không phải `1`) vì
  còn diễn giải khi thiết kế chính xác luồng UI đăng nhập/preview-restore và khi viết runbook
  deploy procedural cho rules (không thể target-hoá).
- `X = 3` — trải trên `firestore.rules` (dùng chung với Content) ↔ `firebase.json` ↔
  `webapp/app_logic.js` (auth + persistence) ↔ `webapp/ledger_ui.js` (backup/restore UI) ↔ bộ
  test emulator (rules + persistence) ↔ tài liệu vận hành deploy — nhiều bề mặt phải nhất quán
  đồng thời, cộng thêm ràng buộc không được phá vỡ hành vi Content đang chạy.
- `U = 2` — luồng Google Sign-In qua Firebase Auth Emulator có tiền lệ rõ (`DEC-020` R1 đã phác
  thảo cơ chế linking tương tự); không phải nghiên cứu từ số 0.
- `V = 3` — khối lượng kiểm chứng lớn: 14 acceptance scenario, emulator rules matrix (5 dòng),
  multi-device matrix (5 dòng), regression an toàn cho Content (safe-merge), cộng thêm bằng
  chứng persistence executable thay `H-49`.
- `H = 3` — nhiều bước phụ thuộc nối tiếp: đổi auth client → cập nhật rules comment → viết test
  rules → viết test persistence/multi-device → viết backup/restore UI → viết runbook deploy →
  chạy production reachability qua emulator.
- `C = 3` — phải giữ nhất quán đồng thời: spec kế toán T-12 (không đổi), Step-B UI đã đóng băng
  (T-13, không đổi ngoài một điểm vào nhỏ), rules Content thật (không đổi hành vi), và toàn bộ
  lịch sử Owner Decision về Firebase (`DEC-019/020/021/023/041/043`).
- `F = 3` — sai lệch ở tầng này có thể khoá Owner khỏi dữ liệu của chính họ hoặc làm lộ dữ liệu
  tài chính; nhưng backup/snapshot bắt buộc (§8 spec) và rules mặc định-deny giữ đây ở mức có thể
  phục hồi (không phải `4`/không thể đảo ngược).

Bằng chứng router (chạy lại được):

    python governance/scripts/governance/routing_engine.py \
      --d 3 --r 3 --b 3 --a 2 --x 3 --u 2 --v 3 --h 3 --c 3 --f 3 \
      --category authentication --category security
    -> tier=C model=Opus model_score=2.85 effort=xhigh effort_score=2.8
    -> model_floors=[safety_business:min_C] effort_floors=[safety_business:min_high]

Không có `Manual Override`: giá trị khai trùng đúng đầu ra router. Hard floor
`authentication/authorization → minimum Tier C` VÀ `→ minimum effort high` (`AGENT_CAPABILITY_
MATRIX.md` § Safety/business hard floors) đều được thoả bởi chính điểm số cơ bản — không cần floor
nâng số lên, nhưng floor vẫn được ghi nhận theo yêu cầu "router MUST record which floor, if any,
changed the result" (ở đây: floor trùng khớp giá trị cơ bản, không nâng thêm).

---

## Objective

Đóng ba khoảng trống operational còn lại trước khi CoinDCA được phép dùng với tiền thật không
giới hạn (`H-42`, spec kế toán §18 R-1…R-5): (1) danh tính Owner bền vững qua đổi thiết bị/trình
duyệt (thay Anonymous Auth bằng Google Sign-In); (2) cô lập logic bên trong project Firebase dùng
chung với app Content (rules, deploy) — không tạo project riêng; (3) backup thủ công + recovery
có validate/snapshot/atomic cho ledger canonical. Đồng thời khôi phục bằng chứng persistence
executable đã mất khả năng chạy (`H-49`) bằng cách hấp thụ nó vào chính Completion Gate này.

## Product consequence

Không có bước C thì cảnh báo "dừng dùng app với tiền thật không giới hạn" (`H-41`/spec §18) vẫn
còn hiệu lực vĩnh viễn — `T-12`/`T-13` chỉ chứng minh app **tính đúng** và **dùng được hằng
ngày**, không chứng minh app **an toàn để giữ danh tính và dữ liệu Owner qua thời gian trong một
project Firebase dùng chung**. `T-14` là hạng mục duy nhất đóng khoảng trống đó mà không cần chờ
Owner tạo project Firebase riêng hay tài khoản Google thứ hai.

Cảnh báo "dừng dùng app với tiền thật không giới hạn" (`H-41`, `DEC-041` K.2) **KHÔNG** tự động
được gỡ bởi `T-14 DONE`. Bước C chỉ đóng nhóm điều kiện Firebase/auth/backup — bước D
(`OWNER_LOCAL_ACCEPTANCE`, spec §22.1) và guard SELL (`H-46`) nằm ngoài task này.

## Scope IN

| # | Hạng mục | Neo spec |
|---|---|---|
| S-C1 | Thay `signInAnonymously()` bằng Google Sign-In (`GoogleAuthProvider`) làm thẩm quyền danh tính Owner duy nhất | Step-C spec §3 |
| S-C2 | UI đăng nhập tối thiểu (nút "Đăng nhập bằng Google", trạng thái "chưa nhận diện" rõ ràng khi UID sai) | Step-C spec §3.2 |
| S-C3 | Xác nhận/khoá `firestore.rules` khối `COINDCA` giữ nguyên shape, chỉ đổi tài liệu/comment | Step-C spec §3.3, §4 |
| S-C4 | Bộ test Firestore Rules Emulator mở rộng: 5 kịch bản danh tính (Owner đúng/ẩn danh/UID sai/không delete/regression Content) | Step-C spec §4 |
| S-C5 | `firebase.json` thêm `hosting.target = "coindca"` | Step-C spec §5.1 |
| S-C6 | Runbook deploy 3 bước cho rules (test safe-merge → đọc diff thủ công → deploy) ghi vào tài liệu vận hành | Step-C spec §5.2 |
| S-C7 | Export backup: thêm `exportedAt` (ISO 8601) + `schemaVersion` + tên file có timestamp | Step-C spec §7.2 |
| S-C8 | Import/restore: preview (số event, khoảng ngày, kết quả validate) TRƯỚC khi ghi; từ chối không mutate khi schema dị dạng; snapshot tên riêng trước khi ghi đè | Step-C spec §8.2 |
| S-C9 | Test multi-device/reconcile/persist chạy lại được qua UI Step B hiện hành (hấp thụ `H-49`) | Step-C spec §9, §12 |
| S-C10 | Production reachability qua Auth Emulator + Firestore Emulator + rules thật + UI thật | Step-C spec §15 |

## Scope OUT (Non-goals tường minh)

| # | KHÔNG làm | Lý do / neo |
|---|---|---|
| O-1 | Project Firebase riêng cho CoinDCA | Owner Decision (`DEC-049`) — DEFERRED, không phải blocker của bước C |
| O-2 | Tài khoản Google thứ hai / hệ thống multi-user / roles | Personal Tool Simplification Principle (`DEC-021`); một Owner, một UID |
| O-3 | Mở nghiệp vụ SELL / realized P&L | `H-46` chưa có Owner Decision xử lý; guard giữ nguyên tuyệt đối |
| O-4 | Đổi công thức/schema kế toán của `T-12` (`derive/update/migrate/destructive`) | `DEC-042`, `DEC-043` — LOCKED |
| O-5 | Redesign IA/UX của `T-13` ngoài một điểm vào đăng nhập/backup/restore nhỏ | Step-C spec §13; Step-B spec đã đóng băng |
| O-6 | Di dời `ethdca/state`/`ethdca/seed` sang namespace khác | `DEC-043` LOCKED; Step-C spec §2 chứng minh không cần thiết |
| O-7 | Tắt Anonymous Auth provider trong Firebase Console | Thao tác Owner-executed ngoài repo; khuyến nghị, không REQUIRED (spec §3.4) |
| O-8 | CI/CD pipeline cho deploy | Dự án cá nhân, không có CI (`PROJECT_PROFILE.md`); runbook thủ công đủ dùng |
| O-9 | `OWNER_LOCAL_ACCEPTANCE` (bước D) | Ngoài phạm vi — chỉ có nghĩa sau khi A+B+C đều đóng (spec kế toán §24) |
| O-10 | Đồng bộ hoá cộng tác thời gian thực nhiều thiết bị | Một Owner, dùng thỉnh thoảng nhiều thiết bị — không phải nhiều người dùng đồng thời (Step-C spec §9) |

## Dependencies

| Dependency | Trạng thái | Bằng chứng |
|---|---|---|
| `T-12` DONE (sự thật tài chính canonical) | DONE | `DEC-046` |
| `T-13` DONE (UI dùng được hằng ngày, điểm vào cho đăng nhập/backup) | DONE | `DEC-048` |
| `T-09B` DONE (nền tảng Firebase Hosting/Auth/Firestore baseline) | DONE | `DEC-024` |
| `docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md` CANONICAL — APPROVED | DONE (cùng phiên) | `DEC-049` |
| Owner Decision mở bước C | DONE | `DEC-049`, chỉ thị phiên "COINDCA — L-1 STEP C DEFINITION" |

## Blocks

Không task nào hiện đang chờ `T-14`. Bước D (`OWNER_LOCAL_ACCEPTANCE`) chỉ có nghĩa sau khi
`T-14 DONE`, nhưng chưa được mở như một task.

## Parallel-Safe With

Không có task nào khác đang mở trong `CAP-WEBAPP` tại thời điểm này (`T-12`, `T-13` đều `DONE`).

## Expected Touch Area

**Allowed production:**
`webapp/app_logic.js` (đường auth/persistence — thay cơ chế đăng nhập, KHÔNG đổi hooks
`state()/commit()/canWrite()/snapshot()`), `webapp/ledger_ui.js` (backup/restore UI, KHÔNG đổi
`webapp/ledger.js`), `firestore.rules` (chỉ khối `COINDCA` — comment/tài liệu, KHÔNG đổi khối
Content, KHÔNG đổi shape logic `isCoinDcaOwner()`), `firebase.json` (thêm `hosting.target`),
`webapp/firebase_config.js` (chỉ nếu cần tham số liên quan Auth provider — không thêm secret).

**Allowed non-production:** test mới dưới `webapp/test_*.js` (rules emulator, persistence,
multi-device qua UI), tài liệu vận hành (`webapp/README.md` hoặc tương đương), `docs/reviews/`,
`docs/sessions/`, `PROJECT/*`.

**Do not touch without Scope Expansion:** `webapp/ledger.js` (schema/derive/migrate/destructive —
LOCKED bởi `DEC-042`/`DEC-043`), bất kỳ khối Content nào trong `firestore.rules`, `src/eth_dca_os/**`
(frozen research), bất kỳ UI nào liên quan SELL/realized P&L.

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. Firebase = fixed owner constraint (`DEC-019`) — không đổi provider persistence.
2. Project Firebase dùng chung `tinphatcontent` — không tạo project mới (`DEC-049`).
3. Namespace `ethdca/state`/`ethdca/seed` không đổi (`DEC-043`).
4. `isCoinDcaOwner()` giữ shape so-sánh-một-UID; chỉ nguồn UID đổi (Anonymous → Google) — không
   thêm role, không thêm bảng hồ sơ Owner trong Firestore.
5. Không schema/công thức kế toán nào của `T-12` bị chạm.
6. Không SELL/realized P&L nào được bật.

---

## Change budget (ước lượng có ràng buộc)

Theo `docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md` §16: ước lượng production diff
(loại trừ test/docs theo `PRODUCTION_PATHS.md`) **~150–380 dòng** trải trên 5 file
(`app_logic.js`, `ledger_ui.js`, `firestore.rules`, `firebase.json`, `firebase_config.js`). Trần
đề xuất cho phiên thi hành: **+600/−400** (rộng hơn ước lượng trung tâm để chừa biên độ UI đăng
nhập, thấp hơn hẳn trần đã dùng của `T-12`/`T-13`, +1800/−1400). Vượt trần này mà không có
`COMPLETION GATE CHANGE PROPOSAL` là `CHANGE_BUDGET_EXCEEDED`.

## Budget review/repair

`CAP-WEBAPP`: `allowed 2 / used 1 / remaining 1` (`REVIEW_BUDGET_LEDGER.md` §2.2.10). Mở `T-14`
là thành viên MỚI của capability đã có (giống `T-12`/`T-13`), **không** phải hấp thụ và **không**
tiêu repair cycle — số dư giữ nguyên `2/1/1` sau khi mở task này (xác nhận tại
`REVIEW_BUDGET_LEDGER.md` §2.2.11). Phiên thi hành `T-14` là **INITIAL IMPLEMENTATION** của chính
task này, không phải repair cycle của `T-12`/`T-13`.

---

## Ready Gate

`governance/core/TASK_READY_GATE_STANDARD.md` § MAJOR — đánh giá tại `S038` (2026-09-06):

- [x] Objective rõ ràng — § Objective, ba khoảng trống cụ thể (auth bền, isolation logic, backup/recovery) với neo `H-42` R-1…R-5
- [x] Scope được định nghĩa — § Scope IN, 10 hạng mục có neo spec Step-C
- [x] Out-of-scope được định nghĩa — § Scope OUT, 10 mục với lý do/neo tường minh
- [x] Dependencies DONE hoặc effective — T-12/T-13/T-09B đều DONE; spec Step-C CANONICAL cùng phiên
- [x] Expected touch area đã xác định — § Expected Touch Area, allowed/disallowed tường minh
- [x] Yêu cầu nghiệp vụ được hiểu — chỉ thị phiên "COINDCA — L-1 STEP C DEFINITION" đủ chi tiết 22 mục, không câu hỏi mở còn lại thuộc thẩm quyền Owner
- [x] Tác động dữ liệu đã biết — không đổi schema/namespace (§2 spec); backup/restore chỉ thao tác trên nguồn sự thật hiện có
- [x] Tác động bảo mật đã biết — auth+rules là trọng tâm task; § Ràng buộc kiến trúc đã khoá + Step-C spec §3/§4/§6
- [x] Tác động routing/API đã biết — không có HTTP API; N/A tường minh
- [x] Điều kiện tiên quyết migration sẵn có — không có migration schema; UID Owner thật là dữ liệu Owner tự cung cấp lúc deploy (đúng tiền lệ `OWNER_UID_REQUIRED` của `T-09B`), không chặn Ready Gate
- [x] Difficulty đã chấm — 3/4
- [x] Risk đã chấm — 3/4
- [x] Blast Radius đã chấm — 3/4
- [x] Primary agent tier đã gán — C / Opus / xhigh, bằng chứng router chạy lại được (§ Ghi chú chấm điểm routing)
- [x] Escalation triggers đã định nghĩa — § Escalation Triggers
- [x] Completion Gate đã hoàn tất — 12 REQUIRED check dưới đây
- [x] Completion Gate đóng băng trước khi thi hành — `Completion Gate Freeze: FROZEN 2026-09-06`

**17/17 tương đương đạt.** Không mục nào được đánh dấu thoả bằng lời hứa tương lai. Nếu một mục
ở trên hoá ra chưa thoả khi mở phiên thi hành, task quay về `PLANNED`.

---

## Completion Gate

### Danh tính & Rules

#### CHECK-T14-01 — Google Sign-In thay thế Anonymous Auth làm thẩm quyền danh tính
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: `webapp/app_logic.js::initPersistence()` không còn gọi `signInAnonymously()`. Đăng nhập
qua `GoogleAuthProvider`. UID phiên đăng nhập là UID dùng để so sánh trong `firestore.rules`.
Đăng xuất/đăng nhập lại (cùng tài khoản) trả về đúng UID, đọc đúng `ethdca/state` cũ.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_persistence.js` — `PR-AUTH-0` (không còn lệnh gọi `signInAnonymously()` trong `app_logic.js` lẫn bản build), `C-AS-01`, `CHECK-T14-01` (đăng xuất → đăng nhập lại cùng tài khoản Google → đúng UID cũ → sổ cũ hiện lại y hệt).

#### CHECK-T14-02 — `isCoinDcaOwner()` giữ nguyên shape, không mở rộng quyền
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: diff `firestore.rules` chỉ chạm khối `COINDCA` (comment/tài liệu); logic so sánh vẫn là
một biểu thức UID duy nhất; không thêm `delete`; khối Content không đổi một ký tự.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_rules.js` §A — SHA-256 của header và của TOÀN BỘ khối Content trùng từng byte với bản trước T-14; các dòng thi hành khối `COINDCA` trùng đúng danh sách khoá cứng; 0 rule `delete`; đúng MỘT biểu thức so UID.

#### CHECK-T14-03 — Emulator rules matrix 5 kịch bản danh tính PASS
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: Owner (UID đúng) ALLOW; ẩn danh DENY; UID xác thực khác DENY; `delete` DENY (mặc định);
hành vi Content không đổi so với baseline `DEC-023` (chạy lại `test_shared_rules_merge.js` hoặc
kế thừa, 0 deviation).

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_rules.js` §B — 5 kịch bản danh tính trên rules THẬT của repo với token THẬT do Auth Emulator ký (Owner google.com ALLOW; không đăng nhập DENY; ẩn danh DENY; tài khoản Google khác DENY; `delete` DENY cho mọi actor; Owner không có quyền Content đặc biệt) + chạy lại nguyên văn `test_shared_rules_merge.js` (120 assertion, exit 0, 0 deviation so với baseline `DEC-023`).

### Deploy isolation

#### CHECK-T14-04 — `firebase.json` khai `hosting.target`
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: khối `hosting` có khoá `target: "coindca"`. Tài liệu vận hành ghi lệnh
`firebase target:apply hosting coindca <site-id>` Owner cần chạy một lần.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_deploy_isolation.js` — `firebase.json` có `hosting.target: "coindca"`; phần cấu hình còn lại trùng ĐÚNG bản trước T-14; `webapp/README.md` § Runbook deploy ghi lệnh `firebase target:apply hosting coindca <site-id-coindca>`.

#### CHECK-T14-05 — Runbook deploy rules 3 bước được ghi lại
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: tài liệu vận hành mô tả đúng ba bước (test safe-merge → đọc diff thủ công → deploy có
điều kiện) trước mọi `firebase deploy --only firestore:rules`. Lệnh deploy khuyến nghị dùng
`--only hosting:coindca` / `--only firestore:rules`, không dùng `firebase deploy` trần.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_deploy_isolation.js` — `webapp/README.md` § Runbook deploy có đúng ba bước theo đúng thứ tự (`test:rules-merge` → `git diff -- firestore.rules` → chỉ deploy sau khi (1) và (2) đạt), cấm tường minh `firebase deploy` trần, lệnh khuyến nghị là `--only hosting:coindca` / `--only firestore:rules`.

### Backup & Recovery

#### CHECK-T14-06 — Export mang timestamp + schema version + chỉ chứa nguồn sự thật
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: tên file `coindca-ledger-<ISO8601>.json`; JSON có `exportedAt` (ISO 8601) và
`schemaVersion` (= `CoinLedger.SCHEMA`); nếu có `derivedSnapshot`, nó nằm trong khối
`_meta: "INFORMATIONAL — NOT IMPORTED"`.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_backup_restore.js` — tên file `coindca-ledger-<ISO8601>.json` khớp `exportedAt`; `schemaVersion === CoinLedger.SCHEMA`; `state` bit-exact với bản durable phía Firebase và chỉ chứa allowlist canonical; `derivedSnapshot._meta === "INFORMATIONAL — NOT IMPORTED"`.

#### CHECK-T14-07 — Preview + validate bắt buộc trước khi restore ghi đè
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: sau khi đọc file, hiển thị tóm tắt (schemaVersion, số event, khoảng ngày, kết quả
validate) TRƯỚC dialog xác nhận ghi. Owner xác nhận dựa trên tóm tắt, không dựa trên "tin tưởng
file".

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_backup_restore.js` — nội dung `#l1Message` ĐƯỢC ĐỌC TẠI ĐÚNG THỜI ĐIỂM hộp thoại xác nhận bật lên và đã chứa `schemaVersion`, số giao dịch, khoảng ngày min→max, `validate PASS`, thời điểm xuất.

#### CHECK-T14-08 — Backup dị dạng bị từ chối, không mutate
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: file với `schemaVersion` sai hoặc field bắt buộc thiếu/hỏng khiến `canonical()`/
`validate()` ném lỗi → restore dừng TRƯỚC khi ghi Firestore/`localStorage` chính; state hiện tại
không đổi (đo bằng snapshot trước/sau thao tác thất bại, phải bit-for-bit giống nhau).

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_backup_restore.js` — 4 ca dị dạng (schemaVersion sai, trường hỏng kiểu, thiếu `events`, không phải JSON): app báo TỪ CHỐI KHÔI PHỤC, **không hộp thoại xác nhận nào bật lên**, bản durable phía Firebase + mirror + `coindca-last-snapshot` + số liệu màn hình đều không đổi một byte.

#### CHECK-T14-09 — Snapshot tự động trước khi restore ghi đè
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: trước khi `destructive()`/ghi Firestore trên đường restore, tự động tải file
`coindca-before-restore-<ISO8601>.json` chứa state hiện tại + ghi
`localStorage['coindca-last-snapshot']`.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_backup_restore.js` — file `coindca-before-restore-<ISO8601>.json` được tải xuống TRƯỚC bước xác nhận, chứa đúng state hiện tại, `reason: "BEFORE_RESTORE"`; `localStorage['coindca-last-snapshot']` mang cùng nội dung.

#### CHECK-T14-10 — Restore hợp lệ tái tạo đúng trạng thái tài chính canonical
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: `backup hợp lệ → state rỗng/hỏng → restore → ACK → reload → derive()` cho đúng y hệt
bốn con số dashboard + toàn bộ trường `DerivedState` như trước khi hỏng (tolerance 0 trên số
nguyên VND, dung sai làm tròn đã định nghĩa của `T-12` cho phần còn lại).

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_backup_restore.js` — backup hợp lệ → `Xóa sổ` → restore → ACK máy chủ → reload → `derive()` (tính độc lập trong Node trên bản durable) TRÙNG KHÍT bản gốc, toàn bộ số liệu dashboard/tóm tắt hiển thị y hệt; `state` canonical khớp bản gốc trừ `rev`; `derivedSnapshot` không được nhập.

### Multi-device & Persistence evidence (hấp thụ H-49)

#### CHECK-T14-11 — Multi-device/mirror-reconcile chạy lại được qua UI Step B
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: bộ kịch bản Step-C spec §9 (reload, logout/login, hồ sơ mới, mirror cũ, ghi xung đột)
chạy được bằng một test suite executable trỏ vào UI Step B hiện hành (thay thế 118 assertion
legacy đã mất khả năng chạy khi `#tab-setup` bị gỡ, `H-49`), và `npm --prefix webapp test` (hoặc
lệnh kế thừa tương đương) thoát mã 0 khi bao gồm suite mới này.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_persistence.js` — 14 kịch bản/60 assertion qua UI Step B hiện hành phủ đúng nhóm `CHECK-T09B-01/02/03/04/10/12/16` (ghi có ACK, reload khớp chính xác, xoá localStorage+sessionStorage, đóng/mở lại trình duyệt, ghi bị rules từ chối, durable hỏng fail-closed, mirror mới hơn không âm thầm thắng, ghi xung đột stale-durable) + `C-AS-06` hồ sơ trình duyệt mới. `npm --prefix webapp test` **exit 0** (log `docs/reviews/evidence/T14/npm-test.log`).

### Production reachability

#### CHECK-T14-12 — Production reachability qua Auth Emulator + Firestore Emulator + rules thật
Priority: REQUIRED · Status: **PASS** · Evidence Level: E1 (E2 độc lập chưa chạy)

Yêu cầu: kịch bản Step-C spec §15 chạy trên app thật (Step B UI) + Firebase SDK thật + Auth
Emulator + Firestore Emulator (rules thật của repo, không mock) + ít nhất một ca âm (C-AS-02
hoặc C-AS-03) trên cùng hạ tầng.

Kết quả `S039`: PASS · Bằng chứng: `webapp/test_t14_persistence.js` chạy trên `app_final.html` do `build_app.js` sinh ra, phục vụ qua HTTP như Hosting, Firebase SDK compat thật, Auth Emulator + Firestore Emulator với ĐÚNG `firestore.rules` của repo. Ca âm trên cùng hạ tầng: `C-AS-02` (chưa đăng nhập) và `C-AS-03` (tài khoản Google khác) đều DENY và app fail closed. `PR-AUTH-1` chứng minh nút bấm chạy THẬT `signInWithPopup(GoogleAuthProvider)`. Giới hạn môi trường ghi rõ tại `docs/reviews/T14-IMPLEMENTATION-REPORT.md` §14.

---

## Exit Criteria

- [x] 12/12 REQUIRED check PASS (E1 tối thiểu) — `S039`
- [x] 0 defect nghiêm trọng chưa xử lý
- [x] 0 REQUIRED security check chưa xử lý
- [x] Regression: `test_t12_ledger` (SC-01…SC-12, INV-1…INV-15), `test_t12_mutations` (7/7 mutant bị diệt), `test_t12_browser` (P-1…P-6 + 17 PASS), `test_stepb_ui` (T-13, AS-01…AS-12) đều PASS; `webapp/ledger.js` diff = 0 dòng
- [x] Regression: hành vi Content trong `firestore.rules` không đổi — `test_shared_rules_merge.js` 120 assertion, 0 deviation; khối Content trùng SHA-256 từng byte
- [x] `PROJECT/PROJECT_PROGRESS.md` cập nhật (roadmap, Current Task Snapshot, Session History)
- [x] `H-49` — re-scope tường minh dựa trên `CHECK-T14-11`: sáu file V2.1.5 chính thức NGHỈ HƯU khỏi cổng release, thay bằng `webapp/test_t14_persistence.js`; ghi tại `PROJECT/HARDENING_BACKLOG.md` `H-49`. Đóng dứt điểm là hệ quả của `T-14 DONE` (thẩm quyền chủ dự án), không phải của phiên thi hành.
- [x] `H-42` cập nhật disposition — phần REQUIRED (FB-2/FB-4/backup-recovery/bằng chứng persistence) đã đóng ở mức E1; `FB-3` giữ HARDENING (deploy là hành động Owner-executed, runbook là giảm thiểu); phần DEFERRED giữ nguyên. Ghi tại `PROJECT/HARDENING_BACKLOG.md` `H-42`.

## Escalation Triggers

Chỉ năm hard-stop canonical (`DELIVERY_LOOP.md`) hợp lệ; dừng vì lý do khác là `UNAUTHORIZED_STOP`.

| Điều kiện gặp phải | Hành động |
|---|---|
| Cần thêm collection/document CoinDCA ngoài `ethdca/state`/`seed` | `ARCHITECTURE_CHANGE_REQUIRED` — vi phạm `DEC-043` LOCKED |
| Cần đổi shape logic `isCoinDcaOwner()` (không chỉ đổi nguồn UID) | `ARCHITECTURE_CHANGE_REQUIRED` |
| Safe-merge rules regression FAIL (hành vi Content đổi) | Dừng ngay, không deploy, `DATA_INTEGRITY_RISK` nếu đã trót deploy |
| Cần mở SELL/realized P&L để hoàn tất một check | `OWNER_DECISION_REQUIRED` (`H-46`) — KHÔNG tự mở |
| Vượt trần diff production (+600/−400) hoặc thêm file production ngoài Expected Touch Area | `CHANGE_BUDGET_EXCEEDED` / `SCOPE_CHANGED` |
| Restore hợp lệ nhưng `derive()` lệch dù chỉ 1 VND | `DATA_INTEGRITY_RISK` — dừng, không tiếp tục |
| Chạm ngưỡng Absorption khi mở rộng phạm vi | Ghi `ABSORPTION_LIMIT_REACHED` → Owner Decision, **không tự tạo task** |
| Owner UID thật cần cho production reachability nhưng chưa có | KHÔNG phải hard-stop — dùng identity giả lập của Auth Emulator, đúng tiền lệ `T-09B`/`T-12`/`T-13` |

KHÔNG phải hard-stop (phải `CONTINUE`): thiếu một hàm nhỏ, một tham số UI, một test local đỏ cần
sửa, một adapter nhỏ phải viết, một finding vừa xuất hiện được route đúng chỗ.

## Stop conditions

| Điều kiện gặp phải | Hành động |
|---|---|
| Bất kỳ REQUIRED check nào FAIL sau khi đã sửa hợp lý trong phạm vi | Dùng 1 repair cycle còn lại của `CAP-WEBAPP` (`allowed 2/used 1/remaining 1`) nếu cần |
| Repair cycle thứ hai bị tiêu hết mà vẫn FAIL | `CHANGE_BUDGET_EXCEEDED` → `OWNER_DECISION_REQUIRED` |
| Phát hiện `H-42`/`H-49` cần phạm vi rộng hơn dự kiến | Ghi nhận, đánh giá Absorption Limit, KHÔNG tự mở task mới |
| Bất kỳ đường nào phải chạm `webapp/ledger.js` để hoàn tất check | `ARCHITECTURE_CHANGE_REQUIRED` — LOCKED bởi `DEC-042`/`DEC-043` |

## Changed Files Registry

Phiên thi hành `S039` (2026-09-06), base `origin/main` = `97434d0`, nhánh
`claude/t14-step-c-firebase-isolation-xu6nxb`.

**Production path** (theo `PROJECT/PRODUCTION_PATHS.md` §1 + hai file cấu hình Firebase mà Step-C
spec §16 tính vào ước lượng production):

| File | Diff | Nội dung |
|---|---|---|
| `webapp/app_logic.js` | +93 / −20 | Bỏ Anonymous Auth; `onAuthStateChanged` là điểm vào danh tính duy nhất; `signIn()` = `signInWithPopup(GoogleAuthProvider)`; `signOut()`; `resetLedger()`; tách `loadDurable()`; phase `SIGNED_OUT`; nút đăng nhập/đăng xuất render từ JS (KHÔNG chạm `app_shell.html`) |
| `webapp/ledger_ui.js` | +80 / −2 | `stamp()`, `exportPayload()` (timestamp + `schemaVersion` + `derivedSnapshot._meta`), `restorePreview()` (dry-run validate), `restoreSnapshot()` (`coindca-before-restore-*`), luồng `l1Import` mới |
| `firestore.rules` | +20 / −1 | CHỈ comment/tài liệu trong khối `COINDCA` (nguồn UID, cảnh báo "authenticated ≠ Owner", con trỏ runbook). Logic không đổi một ký tự |
| `firebase.json` | +1 / −0 | `hosting.target: "coindca"` |
| `webapp/firebase_config.js` | 0 | KHÔNG cần đổi — `authDomain` đã có, không thêm secret nào |
| `webapp/ledger.js` | **0** | LOCKED (`DEC-042`/`DEC-043`) — không chạm |
| `webapp/engine.js`, `webapp/app_shell.html`, `webapp/build_app.js`, `src/eth_dca_os/**` | **0** | không chạm |

    git diff --shortstat origin/main -- webapp/app_logic.js webapp/ledger_ui.js webapp/ledger.js \
      webapp/engine.js webapp/app_shell.html webapp/build_app.js webapp/firebase_config.js \
      firestore.rules firebase.json src/eth_dca_os pyproject.toml pyproject.lock
      -> 4 files changed, 194 insertions(+), 23 deletions(-)

**Non-production** (test + tài liệu vận hành + governance):

| File | Diff | Nội dung |
|---|---|---|
| `webapp/test_t14_rules.js` | mới | CHECK-T14-02/03, C-AS-01…04/13 |
| `webapp/test_t14_persistence.js` | mới | CHECK-T14-01/11/12, C-AS-01/02/03/05/06/07/14 |
| `webapp/test_t14_backup_restore.js` | mới | CHECK-T14-06…10, C-AS-08…11 |
| `webapp/test_t14_deploy_isolation.js` | mới | CHECK-T14-04/05, C-AS-12/13 |
| `webapp/test_firebase_harness.js` | +103 / −7 | `googleAccount`/`anonAccount`/`googleSignIn`/`googleSignOut`/`popupAttempt`; `bootstrapOwner` qua đường Google |
| `webapp/test_t12_browser.js` | +5 / −1 | CHỈ giàn giáo: context mới nay bắt đầu ở `SIGNED_OUT` nên phải đăng nhập trước khi tới nhánh OFFLINE; một nhãn log được sửa cho đúng sự thật. Không assertion nào bị đổi/bỏ |
| `webapp/package.json` | +6 / −3 | `scripts.test` = cổng release L-1 (bao gồm bốn bộ T-14); `test:legacy-v215` giữ sáu file V2.1.5 chạy được bằng tay. Bắt buộc bởi chính `CHECK-T14-11` (check gọi đích danh `npm --prefix webapp test`) |
| `webapp/README.md` | +175 / −44 | § Danh tính chủ sở hữu · § Runbook deploy · § Sao lưu và khôi phục · mục Test viết lại |

## Implementation authority

Phiên thi hành `T-14` được uỷ quyền thực hiện `READY → IN_PROGRESS → IMPLEMENTED` mà không cần
hỏi lại Owner cho các lựa chọn kỹ thuật đã chốt trong § Ràng buộc kiến trúc đã khoá và trong
`docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md`. Chuyển `IMPLEMENTED → DONE` vẫn dành
riêng cho chủ dự án (`STATE_AUTHORITY.md`), theo đúng tiền lệ `T-09B`/`T-12`/`T-13`.

## Notes — định tuyến 5-câu-hỏi (Capability-First Question Order)

1. *Cần cho lát cắt ACTIVE chạy đúng không?* — **CÓ, gián tiếp**: lát cắt §1.A của
   `CAPABILITY_REGISTRY.md` tự nó không đòi Firebase auth để `derive()` chạy đúng trên dữ liệu
   tổng hợp, nhưng mục tiêu cuối của `PROJECT_PROFILE.md` ("dùng cá nhân... ghi giao dịch thật")
   không đạt được an toàn nếu danh tính Owner không bền vững qua thời gian — đây là điều kiện
   product-readiness đã được `docs/spec-l1/...ACCOUNTING_SPEC.md` §18/§24 khai rõ là bước bắt
   buộc TRƯỚC khi dùng tiền thật, không phải một tính năng tuỳ chọn.
2. *Thuộc capability đã có không?* — **CÓ**, `CAP-WEBAPP` (lineage root `WP-C1`, cùng lineage
   `T-09B`/`T-12`/`T-13`). Không tạo capability mới, không tạo lineage root mới.
3. *Task/owner nào gần nhất?* — Không có task nào đang mở: `T-12`, `T-13` đều `DONE`. `H-42`
   chính là finding đã ghi rõ "Owner: chưa có — T-12 KHÔNG nhận mục này" (bước C nằm ngoài phạm
   vi T-12 mục O-5).
4. *Hấp thụ vào owner đó có vượt Absorption Limit không?* — **Không áp dụng**: đây là mở một
   task MỚI trong capability đã có (giống hình thái `T-12`/`T-13`), không phải hấp thụ một
   finding vào một task đang mở. `H-49` được **hấp thụ vào chính `T-14` mới mở** (không phải vào
   một task cũ đã đóng băng gate) — đúng cơ chế "Nếu Step-C acceptance có thể khôi phục bằng
   chứng persistence, ABSORB vào Step C" của chỉ thị phiên, không phải absorption theo
   §II.7 `CAPABILITY_MODEL.md` (không có owner cũ nào bị mở lại).
5. *Đưa lên Owner.* — **đã có**: chỉ thị phiên trực tiếp "COINDCA — L-1 STEP C DEFINITION", ghi
   nhận thành `DEC-049` (`PROJECT/PROJECT_DECISIONS.md`).

`T-14` **không** phải sibling task tách ra để giải phóng budget: nó nằm **trong** capability đã
có, dùng chung pool của lineage root `WP-C1` (`allowed 2 / used 1 / remaining 1` — không đổi bởi
việc mở task) và không đặt lại con số nào. Số task ID mới do phiên `S038` tạo = **1**; số
capability mới = **0**; số lineage root mới = **0**; số proposal mới = **0**; số
`OWNER_ASSIGNMENT_REQUIRED` mới = **0**.
