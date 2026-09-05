# L-1 STEP A — TASK DEFINITION REPORT

Phiên: `S032` · Ngày: 2026-09-05 · Nhánh: `claude/coindca-l1-step-a-task-1ka2zj`
Loại phiên: **TASK DEFINITION ONLY** — không thi hành, production diff = EMPTY.

---

## 1. Canonical Source

    SOURCE HEAD = 91cfbba5e3af01d432c64369bb5a286f6461ab6a   (== origin/main, khớp HEAD kỳ vọng)

Xác minh từ thẩm quyền repo (không lấy từ prompt):

| Điều kiện | Kết quả | Nguồn |
|---|---|---|
| CoinDCA L-1 = ACTIVE PRODUCT TRACK | ✅ | `CAPABILITY_REGISTRY.md` §1.A (lát cắt ACTIVE), `DEC-041` C |
| `app_development_allowed = true` | ✅ | `PROJECT_PROFILE.md` § Quyền phát triển, `DEC-041` B |
| `DEC-041` effective | ✅ | `PROJECT_DECISIONS.md` |
| `DEC-042` effective | ✅ | `PROJECT_DECISIONS.md` |
| Spec L-1 = `CANONICAL — APPROVED` | ✅ | header `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` |

Trạng thái lịch sử V2.1.5 **giữ nguyên, không đụng một chữ** (đã đọc lại để xác nhận):

    FROZEN HISTORICAL RESEARCH AUTHORITY   (DEC-041 A)
    V2.1.5 validation = FAILED
    official verdict  = DO_NOT_BUILD
    can_proceed_to_app = false

`branch_authority_check.sh` báo `BRANCH AUTHORITY: FAIL — attached branch has no upstream`. Đây là
**tình trạng nhánh mới chưa push**, không phải divergence: `ahead of default = 0`,
`divergence LOC = 0`, `INTEGRATION_DECISION_REQUIRED = NO`, worktree CLEAN, production diff EMPTY,
và `HEAD == origin/main == 91cfbba`. Upstream được thiết lập ở lệnh `git push -u` cuối phiên; chạy
lại sau push cho **`BRANCH AUTHORITY: PASS`** (`behind upstream = 0`, `ahead of default = 1`,
`production diff = EMPTY`, `INTEGRATION_DECISION_REQUIRED = NO`). Không có state nào bị đọc từ
nhánh cũ.

## 2. Proposed Task — ĐÃ TẠO, đúng MỘT ID

    TASK ID     T-12
    TÊN         Sổ cái L-1 v2: mô hình dữ liệu, derive() tất định, migration và test kế toán
    FILE        docs/tasks/T-12-so-cai-l1-v2-va-derive.md
    MODE        MAJOR
    STATE       READY
    ROUTING     D / Fable / max — model_score 3.1, effort_score 3.65
                inputs D4 R3 B3 A2 X3 · U3 V4 H4 C3 F4
                categories accounting_financial, destructive_migration
                floors cognitive:D>=4&X>=3, safety_business:min_C, safety_business:min_high
    CAPABILITY  CAP-WEBAPP (lineage root WP-C1) — không capability mới, không lineage mới

**Vì sao `T-12` chứ không phải một namespace mới.** `WP-x` là namespace do `RCP-001` sinh ra để
phân rã các hạng mục V2.1.5; L-1 bước A không phân rã từ hạng mục nào, nó là **hạng mục roadmap
mới của đường sản phẩm L-1**. Dãy `T-00`…`T-11` là dãy roadmap chính và `T-12` là ID kế tiếp còn
trống (đã grep toàn repo: `T-12` chưa từng được dùng cho task nào).

**Vì sao được phép tạo ID.** Năm câu hỏi của `CAPABILITY_MODEL.md`, chấm trên lát cắt ACTIVE §1.A:

1. Cần cho lát cắt chạy đúng? — **CÓ** (lát cắt đi qua "sổ cái + giá vốn tính lại").
2. Thuộc capability đã có? — **CÓ**, `CAP-WEBAPP`.
3. Task/owner gần nhất? — **không có task nào đang mở**: `WP-C1`/`T-09A`/`T-09B`/`WP-C2` `DONE`,
   `WP-C3`/`WP-C4` `CANCELLED`.
4. Hấp thụ có vượt Absorption Limit? — **hấp thụ không khả dụng**: §II.7 chỉ cho hấp thụ tự động
   vào task có scope baseline đã duyệt và **còn mở**; không có task nào như vậy.
5. Đưa lên Owner — **đã có sẵn**: `DEC-042` § Consequence, *"Việc mở task ID cho bước A
   (Ledger/Data Model v2) thuộc một phiên riêng sau `DEC-042`"*.

Anti-proliferation đo trên registry (`task_registry_snapshot.sh`), không grep cả repo:

    BEFORE: task_files = 22 · roadmap_task_ids = 29
    AFTER:  task_files = 23 · roadmap_task_ids = 30
    new_registered_task_ids            = 1   (T-12)
    proposals_created                  = 0
    owner_assignment_required_added    = 0
    capabilities/lineage roots created = 0

## 3. Capability Boundary

**IN** (`S-A1`…`S-A17`): schema `coindca.ledger/2`; `openingPosition`; event `TREASURY`/`TRADE`/
`RESERVE`/`PRICE`; `derive()` thuần; WAC một pool USDT; lan truyền `UNKNOWN`; sửa/xoá/nhập muộn;
`businessDate` + `Asia/Ho_Chi_Minh` + tháng lịch; VND integer + `SPLIT_VND`; kế hoạch tháng +
`CAPPED_CARRY`; reserve earmark; hợp đồng migration; cờ fail-visible; `SC-01`…`SC-12`;
`INV-1`…`INV-15`; persistence tối thiểu; production reachability tối thiểu.

**OUT** (`O-1`…`O-12`): dashboard/CSS redesign, tab Research, Buy Score, regime, crash ladder,
recommendation, thông báo, Firebase/auth/hosting/rules, dữ liệu thật của Owner, `V2.2`, thí nghiệm
chiến lược, tax lot, đa tài sản ở UI, lấy giá tự động, sửa `src/eth_dca_os/**` và `docs/spec/**`,
vá `B10` trong `engine.js`, tombstone.

Phạm vi **không** được mở rộng chỉ vì mã legacy lân cận lộn xộn; chạm ngoài Expected Touch Area →
`SCOPE EXPANSION REQUIRED`.

## 4. Existing Code Map (đọc trực tiếp, không đoán)

| Vùng | Hiện trạng | Hệ quả cho `T-12` |
|---|---|---|
| `webapp/app_logic.js:20-35` `emptyState()` | `schema: "ethdca.tracker/1"`, và **các biến cộng dồn** `eth`, `costUsdt`, `costVnd`, `treasury{vnd,usdt}`, `months[].base/smart`, `oppFund`, `ladders` | Chính là mô hình bị thay. Các trường cộng dồn biến mất khỏi state được lưu (§4.1) |
| `webapp/app_logic.js:129-132` `currentMonth()` | trả **khoá tháng lớn nhất**, không phải tháng lịch | `B3` — `CHECK-T12-06` |
| `webapp/app_logic.js:~205` `addP2P()` | lưu `fee` và `rate` riêng; `ts = new Date()` | §6.2 bỏ `fee`/`rate`; `B4` — `businessDate` người dùng nhập |
| `webapp/app_logic.js:~240-300` `addBuy()` | `ethAmt = usdt / price`; `vndCost = vndRate ? usdt*vndRate : 0`; fill zone theo pool tháng | Đúng lỗi §8.1; `qty` phải là lượng THỰC NHẬN, `vndCost` phải từ pool WAC. `B1`, `B2` |
| `webapp/app_logic.js` khối persistence (`touch`/`mirror`/`persist`/`validateState`) | Firestore `ethdca/state` là nguồn bền duy nhất; ghi có điều kiện theo `rev`; `validateState()` khoá cứng `schema === "ethdca.tracker/1"` và các bất biến pool `a/r/d` | Phải có validator mới cho `coindca.ledger/2` + phát hiện version tất định; **giữ** cơ chế `rev`/transaction đã có |
| `webapp/app_logic.js` `expBtn`/`impBtn`/`wipeBtn` | export/import JSON; **wipe chỉ `confirm()` rồi ghi state rỗng** | `B8` — `INV-14` bắt buộc snapshot trước `import`/`wipe`/`migration` |
| `webapp/app_shell.html` | 5 tab (`dash`, `entry`, `ladder`, `history`, `setup`); form nhập không có ô ngày giao dịch | Chỉ thêm trường nhập tối thiểu; KHÔNG thiết kế lại |
| `webapp/build_app.js` | ghép `app_shell` + `firebase_config` + `engine` + `app_logic` → `app_final.html` + `public/index.html` | Module sổ cái mới phải được ghép vào bundle |
| `webapp/test_firebase_harness.js`, `test_helpers.js` | Playwright + Chromium + Firestore Emulator + rules thật; `readState()` đọc bản DURABLE qua REST và đối chiếu bit-exact | **Đường production reachability đã tồn tại** — `T-12` dùng lại, không dựng cơ chế mới |
| `webapp/engine.js` | OSCORE/chỉ báo, rolling window đếm số dòng (`B10`) | Ngoài đường tiền L-1 (`INV-10`); không sửa |
| `firestore.rules:96-105` | allow-list **đúng hai** document `ethdca/state`, `ethdca/seed`; mọi `ethdca/*` khác **bị từ chối** | Ràng buộc cứng: sổ L-1 phải nằm **trong** `ethdca/state` |
| `src/eth_dca_os/**`, `docs/spec/**` | frozen historical research authority | Không chạm |

## 5. SC/INV Coverage

Ma trận đầy đủ nằm trong file task (`§ Financial invariants` và `§ Ma trận SC → ...`). Tóm tắt:

- **12/12** golden scenario `SC-01`…`SC-12` có: đường production dưới test, fixture, số kỳ vọng
  (đóng băng ở spec §19, **không được viết lại**), và tập `INV` được phủ.
- **15/15** bất biến `INV-1`…`INV-15` có **test nhắm đích bắt buộc**, kể cả bốn bất biến **không**
  được SC nào phủ trực tiếp: `INV-4` (không âm ở mọi tiền tố + `firstOffendingEventId`), `INV-5`
  (không float xuống durable), `INV-10` (tín hiệu không chạm tiền), `INV-13` (`SPLIT_VND` cộng
  đúng gốc).
- `CHECK-T12-09` đòi chứng minh **mutation**: test của tối thiểu `INV-1`, `INV-3`, `INV-4`,
  `INV-9`, `INV-11`, `INV-12`, `INV-14` phải thực sự đỏ khi bất biến bị phá — chặn đúng tình
  huống "suite xanh nhưng bất biến chưa được kiểm".

## 6. Migration / Persistence Boundary

**Migration** — dùng nguyên bốn nhãn canonical `SAFE_TO_MIGRATE` / `RECALCULATE` /
`OWNER_CONFIRMATION_REQUIRED` / `DROP_LEGACY_ONLY` (§17.2). Bắt buộc: snapshot trước khi ghi;
phát hiện version tất định; không diễn giải lại im lặng trường tài chính legacy
(`trades[].vndRate`/`vndCost` bị bỏ, tính lại bằng WAC); hai tầng kết quả `M-1`…`M-4` (**DỪNG,
không ghi gì**) vs `W-1` (**HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`**); đối chiếu §17.3 vượt ngưỡng =
thất bại; không mất event nguồn; **không** đưa Base/Smart/Opportunity/ladder/score vào sự thật
tài chính L-1. **Không** migration Firebase.

**Persistence** — đã kiểm: ledger v2 **bắt buộc** đổi schema đã lưu, nên phần persistence tối
thiểu **không tách được** khỏi capability và nằm **trong cùng task `T-12`**, không tạo task anh em
(đúng chỉ thị §11 và `CAPABILITY_MODEL.md` §II.4 điều kiện 3). Ràng buộc cứng đã xác minh:
`firestore.rules` chỉ allow-list `ethdca/state` và `ethdca/seed`, nên sổ `coindca.ledger/2` phải
nằm **bên trong** `ethdca/state`; tạo document mới sẽ đòi sửa rules → thuộc bước C, và nếu bắt
buộc thì đó là `ARCHITECTURE_CHANGE_REQUIRED` chứ không phải mở rộng phạm vi im lặng.

## 7. Completion Gate — FROZEN 2026-09-05, 14 REQUIRED

| ID | Nội dung | Nguồn chỉ thị |
|---|---|---|
| `CHECK-T12-01` | Schema L-1 canonical, không rò rỉ sự thật chiến lược legacy | CHECK-A-01 |
| `CHECK-T12-02` | `openingPosition + events → derive()` tất định | CHECK-A-02 |
| `CHECK-T12-03` | WAC một pool USDT đúng số | CHECK-A-03 |
| `CHECK-T12-04` | `UNKNOWN` fail-visible, không bao giờ ép về 0 | CHECK-A-04 |
| `CHECK-T12-05` | Sửa / xoá / nhập muộn tính lại đúng | CHECK-A-05 |
| `CHECK-T12-06` | `businessDate`, `Asia/Ho_Chi_Minh`, tháng lịch | CHECK-A-06 |
| `CHECK-T12-07` | VND integer, làm tròn đối chiếu được, thứ tự tất định | CHECK-A-07 |
| `CHECK-T12-08` | `SC-01`…`SC-12` PASS | CHECK-A-08 |
| `CHECK-T12-09` | `INV-1`…`INV-15` phủ, không bất biến REQUIRED nào bỏ trống | CHECK-A-09 |
| `CHECK-T12-10` | Hợp đồng migration PASS gồm dữ liệu mơ hồ | CHECK-A-10 |
| `CHECK-T12-11` | Round-trip persistence giữ nguyên sự thật sổ cái | CHECK-A-11 |
| `CHECK-T12-12` | Production Reachability PASS | CHECK-A-12 |
| `CHECK-T12-13` | Regression áp dụng được PASS, không test nào bị làm yếu | CHECK-A-13 |
| `CHECK-T12-14` | Không hồi quy productization chiến lược | CHECK-A-14 |

Nhãn đổi từ `CHECK-A-xx` sang `CHECK-T12-xx` theo đúng quy ước prefix task ID của repo
(`CHECK-T09A-xx`, `CHECK-T09B-xx`, `CHECK-C2-xx`). **Nội dung không bị làm yếu ở bất kỳ mục nào**;
mỗi check được bổ sung tiêu chí đo được (ngưỡng, số lượng, cách chứng minh).

**Production Reachability PASS** được định nghĩa cụ thể, chống rỗng: `P-1` app nạp qua
`app_final.html` đã build (không gọi hàm module trong Node); `P-2` ≥ 8 event thật phủ
opening/TREASURY×2/TRADE PLAN×2/TRADE EXTRA/RESERVE CONTRIBUTE/TRADE RESERVE-có-note; `P-3` ≥ 1
sửa + 1 xoá + 1 nhập muộn qua đường app; `P-4` máy chủ xác nhận rồi đọc lại từ SERVER; `P-5`
reload → `derive()` khớp oracle tính tay với `tolerance = 0`; `P-6` payload durable không chứa
khoá dẫn xuất bị cấm. **0 event / 0 case = FAIL.**

## 8. Evidence / E2

`E1` là tối thiểu bắt buộc cho mọi check thực thi được (Risk 3, `EVIDENCE_STANDARD.md`).

    E2 ĐỘC LẬP BẮT BUỘC — phủ TRỌN khối này như MỘT chỉnh thể:
      CHECK-T12-02, -03, -04, -05, -06, -09, -10, -11, -12
    E1 là đủ (vẫn trong tầm quan sát của reviewer):
      CHECK-T12-01, -07, -08, -13, -14

Người thi hành **KHÔNG được tự chứng nhận `E2`**; `E2` tạo bằng thủ tục "Solo Independent Review"
ở một phiên reviewer riêng, lưu tại `docs/reviews/` theo template. Tám điểm dò đối kháng bắt buộc:
số học WAC (gồm cạn pool và phần dư), lan truyền `UNKNOWN`, sửa/xoá tính lại, ranh giới tháng/múi
giờ, mơ hồ migration + tính nguyên tử, round-trip persistence, production reachability (reviewer
tự chạy harness), state dị dạng/thiếu. Không đòi `E2` cho chi tiết mỹ thuật/không chạm tiền.

## 9. Change Budget

    Mốc đo CẤP TASK (KHÔNG phải Golden baseline):
      T12_MEASURE_BASE_SHA = 91cfbba5e3af01d432c64369bb5a286f6461ab6a

| Hạng mục | Ước lượng | Trần |
|---|---|---|
| File production | 4 sửa + 1–2 mới | ≤ 7 |
| File test | 4–5 mới | — |
| Migration/adapter | trong 1–2 file mới ở trên | — |
| Diff production | ≈ +1.300 / −300 | **+1.600 / −450** |
| Diff test | ≈ +2.250 | — |
| Repair budget tối đa | **0 tự cấp** | Owner Decision riêng |
| Vòng `E2` dự trù | 1 | — |

`GOLDEN_BASELINE_SHA` **vẫn** `PENDING_OWNER_DATA / MIGRATION_REQUIRED` (`H-10`); phiên này
**không** chọn một SHA tiện tay làm Golden, và **không** khai giá trị tầng B
(`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX`) của dự án.

Budget review/repair: `CAP-WEBAPP` `allowed 2 / used 0 / remaining 2` (`DEC-018`) — **không đổi,
không reset, không cấp thêm**. `T-12` tự cấp = 0. Theo `CAPABILITY_MODEL.md` §II.8
(`migration_status` của `CAP-WEBAPP` chưa bao giờ khai `ADOPTED`), **mở một repair cycle cho
`T-12` cần Owner Decision riêng**; lượt thi hành đầu tiên là *initial implementation* nên không
tiêu chu kỳ nào.

Vượt trần → `CHANGE_BUDGET_EXCEEDED` / `SCOPE_CHANGED`, quay lại Owner — **không** âm thầm mở rộng.

## 10. Ready Gate — READY, không phải bịa

17/17 mục MAJOR Ready Gate được xác nhận trong file task với neo cụ thể. Bốn mục đáng nói:

- **Dependencies** — không dependency nào đang mở: `DEC-040`/`DEC-041`/`DEC-042` effective, spec
  `CANONICAL — APPROVED`, cả bốn task `CAP-WEBAPP` (`WP-C1`, `T-09A`, `T-09B`, `WP-C2`) `DONE`.
- **Điều kiện tiên quyết migration** — bảng phân loại §17.2 đã canonical; fixture legacy dựng
  được **tổng hợp** từ `emptyState()`. Các dòng `OWNER_CONFIRMATION_REQUIRED` cần Owner **lúc
  chạy migration trên dữ liệu thật**, không phải lúc thi hành — `T-12` xây bề mặt xác nhận đó.
- **Completion Gate đóng băng trước khi thi hành** — FROZEN 2026-09-05, cùng phiên tạo task,
  trước khi bất kỳ dòng mã nào được viết.
- **Không manufacture** — nếu một mục hoá ra chưa thoả khi mở phiên thi hành, task quay về
  `PLANNED` chứ không đi tiếp.

Hai việc **cần Owner** nhưng **không chặn** việc bắt đầu: repair budget nếu vòng rà soát đầu tiên
FAIL, và `IMPLEMENTED → DONE`.

## 11. Roadmap Impact

| File (canonical holder) | Thay đổi |
|---|---|
| `PROJECT/PROJECT_PROGRESS.md` | thêm 1 dòng roadmap `T-12` (`READY`, D/max); `Current Task Snapshot` → `T-12`; `Next Session` → mở phiên thi hành `T-12`; `Last Updated` |
| `PROJECT/LO_TRINH_DE_HIEU.md` | **sinh lại** bằng `sync_easy_roadmap.py` (không sửa tay) |
| `PROJECT/CAPABILITY_REGISTRY.md` | `T-12` vào THÀNH VIÊN `CAP-WEBAPP`; §2.1 ghi lại 5 câu hỏi định tuyến |
| `PROJECT/REVIEW_BUDGET_LEDGER.md` | §2.2 THÀNH VIÊN (đồng thời sửa `WP-C3`/`WP-C4`/`T-09B` đã lạc hậu) + §2.2.6 ghi rõ budget KHÔNG đổi |
| `PROJECT/HARDENING_BACKLOG.md` | `H-41` nhận owner `T-12` cho `B1`–`B9` + bảng phân loại; `H-42`/`H-43` ghi rõ `T-12` **không** nhận |
| `docs/tasks/T-12-…md` | **mới** |
| `docs/reviews/L1-STEP-A-TASK-DEFINITION.md` | **mới** (báo cáo này) |
| `docs/sessions/S032-…md` | **mới** (handoff, bắt buộc với MAJOR) |

**Không** tạo epic cha, task con, task anh em, task dọn dẹp. **Không** ghi `DEC` mới — thẩm quyền
đã có sẵn ở `DEC-042`; ghi thêm một DEC sẽ là bịa ra một quyết định Owner không tồn tại.
**Không** đổi trạng thái bất kỳ task nào khác.

## 12. Exact Next Action

    Mở MỘT phiên thi hành riêng cho T-12, nhánh mới tách từ origin/main.

Trình tự bắt buộc của phiên đó: chạy `branch_authority_check.sh` **trước** khi đọc state → đọc
`AGENTS.md` → `governance/v4/CORE/*` → `PROJECT/*` → `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`
→ `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` → `T-12: READY → IN_PROGRESS`.

Ràng buộc mang theo: Completion Gate đã đóng băng (không xoá/làm yếu REQUIRED check); không mở
thêm task ID; không tự cấp repair budget; không tự chứng nhận `E2`; batch review bắt buộc cuối
phiên (Effective Risk `HIGH`); `E2` do một phiên reviewer **độc lập** chạy sau khi thi hành xong.

---

## Addendum — `S033` (2026-09-05), Owner Decision `DEC-043`

Owner đọc báo cáo này và `T-12`, rồi tu chỉnh ba điểm — không thi hành, không task ID mới:

1. **Persistence (§6 ở trên).** Owner GRANT thẩm quyền kiến trúc tối thiểu mà §6 đã xác định là
   bắt buộc: schema `coindca.ledger/2` được thay thế/tiến hoá state đã lưu **bên trong**
   `ethdca/state`. Collection/document mới, sửa `firestore.rules`, đổi kiến trúc Firebase vẫn
   **ngoài** phạm vi và vẫn kích hoạt `ARCHITECTURE_CHANGE_REQUIRED` nếu thật sự cần.
2. **Golden baseline (§9 ở trên).** Câu *"`GOLDEN_BASELINE_SHA` vẫn `PENDING_OWNER_DATA`"* trong
   §9 bị Owner xác nhận gây hiểu lầm khi đọc trong ngữ cảnh `T-12` — nó không, và chưa từng, là
   phụ thuộc của `T-12`. `T-12` nay có khái niệm riêng, tổng hợp: `T12_GOLDEN_ACCOUNTING_BASELINE`
   (bộ fixture `SC-01`…`SC-12` + số kỳ vọng spec §19), tách khỏi cả `GOLDEN_BASELINE_SHA` tầng dự
   án (`H-10`, lineage `T-06`) lẫn `OWNER_LOCAL_ACCEPTANCE` (dữ liệu thật, bước D).
3. **Repair budget (§9 § Budget review/repair ở trên).** Owner pre-authorize MỘT repair cycle
   cho `T-12`, rút từ pool `CAP-WEBAPP` hiện có (không cộng thêm), dùng được chỉ khi đủ các điều
   kiện đã liệt kê trong file task. Chu kỳ thứ hai vẫn cần Owner Decision riêng.

**Ready Gate (§10 ở trên) tái xác nhận: `T-12` giữ nguyên `READY`.** 17/17 mục vẫn thoả; hai mục
(tác động dữ liệu/bảo mật, điều kiện tiên quyết dữ liệu) được củng cố thêm bằng phê duyệt Owner
tường minh thay vì giả định thi hành. Không `READY_GATE_FAIL`.

**§7 Completion Gate KHÔNG đổi một chữ** — 14 REQUIRED check giữ nguyên. **§8 Evidence/E2 KHÔNG
đổi** — yêu cầu độc lập giữ nguyên vẹn.

Chi tiết đầy đủ: `PROJECT_DECISIONS.md` `DEC-043`, `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`,
`docs/sessions/S033-t12-owner-amendments-dec043.md`.
