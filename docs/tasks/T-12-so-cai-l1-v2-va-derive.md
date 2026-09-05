# T-12 — Sổ cái L-1 v2: mô hình dữ liệu, `derive()` tất định, migration và test kế toán

## Metadata
Status:
READY — 2026-09-05. Task được mở tại phiên `S032` theo thẩm quyền `DEC-042` § Consequence
(*"Việc mở task ID cho bước A (Ledger/Data Model v2) thuộc một phiên riêng sau `DEC-042`"*).
Đây là bước **A** của `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §24.
Toàn bộ 17 mục MAJOR Ready Gate được xác nhận trong chính file này (§ Ready Gate).
**KHÔNG có phiên thi hành nào được bắt đầu trước khi Completion Gate dưới đây đóng băng** —
gate đóng băng cùng ngày tạo file, xem `Completion Gate Freeze`.

**Amended 2026-09-05 (`S033`, Owner Decision `DEC-043`).** Owner xác nhận `T-12` là ĐÚNG MỘT
capability kế toán L-1 bước A và duyệt ba tu chỉnh: (1) phạm vi kiến trúc persistence tối thiểu
bên trong ranh giới `ethdca/state` đã có; (2) tách bạch `T12_GOLDEN_ACCOUNTING_BASELINE` (tổng
hợp) khỏi `OWNER_LOCAL_ACCEPTANCE` (dữ liệu thật) và khỏi `GOLDEN_BASELINE_SHA` tầng dự án
(`H-10`, `T-06`); (3) pre-authorize **một** repair cycle có điều kiện cho `T-12`, rút từ pool
`CAP-WEBAPP` hiện có. Task **giữ nguyên `READY`** (§ Ready Gate § Tái xác nhận `DEC-043`).
**14 REQUIRED check (`CHECK-T12-01`…`-14`) KHÔNG bị sửa một chữ.** Chi tiết từng tu chỉnh nằm
tại đúng mục nó thuộc về: § Persistence boundary, § Change budget, § Budget review/repair,
§ Stop conditions.

Phase:
CoinDCA L-1 — bước A (sự thật tài chính) của chuỗi A → B → C → D (spec §24)

Task Mode:
MAJOR

Lớp (RCP-001):
Không thuộc RCP-001. `T-12` là hạng mục roadmap mới của đường sản phẩm L-1 (`DEC-041` C),
không phải work package tách ra từ một task V2.1.5.

Completion Gate Freeze:
FROZEN — 2026-09-05 (`S032`, cùng phiên tạo task). Sau mốc này, không REQUIRED check nào được
xoá hoặc làm yếu; mọi thay đổi phải đi qua khối `COMPLETION GATE CHANGE PROPOSAL`
(`governance/core/TASK_COMPLETION_GATE_STANDARD.md` § Gate Change Control).

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới, **KHÔNG** tạo lineage root mới.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 4
R: 3
B: 3
A: 2
X: 3
U: 3
V: 4
H: 4
C: 3
F: 4

Routing Categories:
accounting_financial, destructive_migration

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.1

Effort Routing Score:
3.65

Applied Model Floor:
cognitive:D>=4&X>=3, safety_business:min_C

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
max

Difficulty:
4/4

Risk:
3/4

Blast Radius:
3/4

Project Profile:
PRODUCT

### Ghi chú chấm điểm routing (không phải cảm tính — đối chiếu với chính repo)

- `D = 4` — cùng mức `WP-A6` (`D=4`, thứ tự 18 bước) và `WP-A3`. Lý do: giá vốn hai tiền tệ WAC
  + lan truyền `UNKNOWN` + số nguyên có đối chiếu phần dư + thứ tự tất định + migration phải
  ĐỒNG THỜI đúng trên 12 kịch bản và 15 bất biến.
- `R = 3` — **KHÔNG chấm 4**, giữ nhất quán với `T-09A`/`T-09B` (`R=3`) của chính lineage này:
  một người dùng, không có bên thứ ba, và spec bắt buộc snapshot trước thao tác phá huỷ
  (`INV-14`) + migration nguyên tử không xoá dữ liệu legacy (`INV-12`, §17.5) nên hậu quả
  không phải mất dữ liệu không hồi phục.
- `B = 3` — toàn bộ bề mặt tài chính của sản phẩm L-1, cùng mức `T-09B` (mất toàn bộ sổ = 3).
- `A = 2` — spec canonical, 4 quyết định Owner đã chốt (`DEC-042`); phần mơ hồ còn lại chỉ ở
  ranh giới đấu nối vào app hiện có và các dòng `OWNER_CONFIRMATION_REQUIRED` của §17.2.
- `X = 3` — module sổ cái ↔ `webapp/app_logic.js` ↔ persistence Firestore ↔ state legacy ↔
  harness test, cùng mức `T-09B`.
- `V = 4`, `F = 4` — 12 golden scenario + 15 bất biến + đối chiếu migration + round-trip
  persistence + reachability + regression, và một con số sai là sai tiền thật.

Bằng chứng router (chạy lại được):

    python governance/scripts/governance/routing_engine.py \
      --d 4 --r 3 --b 3 --a 2 --x 3 --u 3 --v 4 --h 4 --c 3 --f 4 \
      --category accounting_financial --category destructive_migration
    -> tier=D model=Fable model_score=3.1 effort=max effort_score=3.65

Không có `Manual Override`: giá trị khai trùng đúng đầu ra router.

---

## Objective

Dựng **sự thật tài chính canonical của CoinDCA L-1** theo
`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` (`CANONICAL — APPROVED`, `DEC-042`):

    openingPosition + events[]  ->  derive() tất định  ->  DerivedState

cùng hợp đồng migration từ state legacy `ethdca.tracker/1`, ranh giới persistence tối thiểu cho
schema `coindca.ledger/2`, và bộ test kế toán `SC-01`…`SC-12` / `INV-1`…`INV-15` chạy được.

Kết thúc `T-12`, con số tài chính của app phải là **dẫn xuất** — không còn một biến cộng dồn nào
(`state.eth`, `state.costUsdt`, `state.costVnd`, `state.treasury`) là nguồn sự thật.

## Product consequence

Không có bước A thì mọi thứ sau xây trên số sai (spec §24). Cụ thể, đây là hạng mục duy nhất
xoá **cả lớp** lỗi `B1`, `B2`, `B3`, `B4`, `B5`, `B6`, `B7`, `B9` của `H-41` bằng cách thay mô
hình sự thật, thay vì vá mười lỗi riêng lẻ (`DEC-041` K.2 tường minh: *"B1–B10 là ràng buộc
thiết kế, KHÔNG phải đơn sửa lỗi riêng lẻ"*).

Cảnh báo **"dừng dùng app với tiền thật" vẫn còn hiệu lực** trong và sau `T-12`: `T-12` chỉ mở
được điều kiện `A-1`…`A-4` của spec §22; `A-5` (`OWNER_LOCAL_ACCEPTANCE`) và `A-6`
(`R-1`…`R-5`, `H-42`) nằm ngoài task này.

## Scope IN

| # | Hạng mục | Neo spec |
|---|---|---|
| S-A1 | Schema / data model L-1 `coindca.ledger/2`: `plan`, `openingPosition`, `events[]` đa hình | §5 |
| S-A2 | `openingPosition` (tối đa một, có thể vắng, `costVnd = null` hợp lệ) | §5.2, §14 |
| S-A3 | Event canonical: `TREASURY`, `TRADE`, `RESERVE`, `PRICE` | §5.3 |
| S-A4 | `derive(openingPosition, plan, events, asOfDate) -> DerivedState` — hàm thuần, không đọc đồng hồ | §9.1, §9.2 |
| S-A5 | Giá vốn VND: **một** pool USDT, WAC, giải phóng theo bình quân | §6.3, §7.3, §8.2 |
| S-A6 | Lan truyền `UNKNOWN` (STRICT / FAIL-VISIBLE), cấm fallback FX ẩn theo từng lệnh | §8.5, `INV-11`, `DEC-042` §4 |
| S-A7 | Ngữ nghĩa sửa / xoá cứng / nhập muộn + tính lại toàn bộ | §9.3, §15 |
| S-A8 | `businessDate` người dùng nhập; `Asia/Ho_Chi_Minh`; tháng lịch; thứ tự `(businessDate, seq)` | §5.4, §10.1–§10.3 |
| S-A9 | Tiền là số nguyên; `SPLIT_VND` phần dư đối chiếu được | §10.4, §10.5, `INV-5`, `INV-13` |
| S-A10 | Kế hoạch tháng: `plannedBudget`, `carryIn/Out` (`CAPPED_CARRY`, cap 1), `planInvested`, `nextPlannedDate/Amount` | §11 |
| S-A11 | Reserve là earmark dẫn xuất; `source = RESERVE` bắt buộc `note` | §12 |
| S-A12 | Hợp đồng migration từ `ethdca.tracker/1` + đối chiếu §17.3 + hai tầng kết quả `M-1..M-4` / `W-1` | §17 |
| S-A13 | Cờ `LEDGER_INCONSISTENT`, `FUTURE_DATED_EVENTS`, `UNKNOWN_VND_BASIS` + `firstOffendingEventId` | §8.4, §10.6, §16.4 |
| S-A14 | Bất biến kế toán `INV-1`…`INV-15` được **kiểm bằng test**, không bằng lời | §20, `A-2` |
| S-A15 | Golden test `SC-01`…`SC-12` trên dữ liệu **tổng hợp** | §19, `A-1` |
| S-A16 | Ranh giới persistence TỐI THIỂU: serialize/khôi phục `coindca.ledger/2` không trôi số, phát hiện version tất định, snapshot trước thao tác phá huỷ | §9.4, §15.3, `INV-12`, `INV-14` |
| S-A17 | Production reachability tối thiểu: sổ mới dùng được qua đúng đường app đã có (adapter tối thiểu được phép) | `CAPABILITY_MODEL.md` § Production Reachability |

## Scope OUT (Non-goals tường minh)

| # | KHÔNG làm | Lý do / neo |
|---|---|---|
| O-1 | Thiết kế lại dashboard, CSS, bố cục | bước B của spec §24 |
| O-2 | Tab Research, Buy Score hồi cứu | `D-1`/`D-2`, `H-43` |
| O-3 | regime, crash ladder, zone, unlock, spacing, recommendation | `N-4`, `N-6`, `INV-10`, `DEC-041` B |
| O-4 | Nhắc lịch / thông báo | `D-6`, `T-08`/`T-10` `DEFERRED` |
| O-5 | Project Firebase riêng, Google Sign-in, đổi `firebase.json` / `firestore.rules` / Hosting | §18 `R-1`…`R-5`, `H-42`, bước C |
| O-6 | Dữ liệu tài chính THẬT của Owner | `DEC-041` C, §19, §22.1 |
| O-7 | `V2.2`, thí nghiệm chiến lược, rerun `T-06` | `DEC-040`, `DEC-041` A |
| O-8 | Tax lot (FIFO/LIFO/specific-ID), sổ lãi lỗ đã thực hiện | `D-5`, §8.2 |
| O-9 | Nhiều tài sản ngoài ETH ở UI; lấy giá tự động | `D-4`, `D-7` |
| O-10 | Sửa `src/eth_dca_os/**` (research đóng băng) và `docs/spec/**` | `DEC-041` A |
| O-11 | Vá `webapp/engine.js` cho `B10` | `H-43`, ngoài đường quyết định L-1 MVP |
| O-12 | Tombstone / audit trail đầy đủ cho xoá | `D-8`, §15.3 |

**Không được mở rộng phạm vi chỉ vì mã legacy lân cận lộn xộn.** Chạm ngoài Expected Touch Area
→ khối `SCOPE EXPANSION REQUIRED`, không sửa im lặng.

## Dependencies

| Dependency | Trạng thái | Bằng chứng |
|---|---|---|
| `DEC-040` — chọn hướng L-1 | effective | `PROJECT_DECISIONS.md` |
| `DEC-041` — L-1 canonical transition; `app_development_allowed = true`; lát cắt ACTIVE = L-1 | effective | `PROJECT_DECISIONS.md`, `CAPABILITY_REGISTRY.md` §1.A |
| `DEC-042` — spec L-1 `CANONICAL — APPROVED`; 4 quyết định kế toán đã chốt | effective | `PROJECT_DECISIONS.md` |
| `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` | `CANONICAL — APPROVED` | header spec |
| `H-41` (`B1`–`B10`) là đầu vào bắt buộc | RE_TRIGGER đã kích hoạt | `HARDENING_BACKLOG.md` |
| `WP-C1`, `T-09A`, `T-09B`, `WP-C2` (lineage `CAP-WEBAPP`) | DONE | roadmap |

Không dependency nào đang mở. `T-08`/`T-10` `DEFERRED` và `WP-C3`/`WP-C4`/`WP-D2`/`T-11`
`CANCELLED` **không** phải dependency của `T-12`.

## Blocks

- Bước **B** của spec §24 (dashboard §16 + UX nhập/sửa/xoá + lịch sử §15).
- Bước **D** (`OWNER_LOCAL_ACCEPTANCE`, §22.1) — chỉ có nghĩa sau A + B + C.

## Parallel-Safe With

- Không có task nào khác đang `READY`/`IN_PROGRESS` trong repo tại thời điểm tạo. Nếu bước C
  (`H-42`, Firebase) được mở sau này thì nó **không** giao Expected Touch Area với `T-12`
  (`T-12` không chạm `firebase.json`, `firestore.rules`, `webapp/firebase_config.js`).

## Expected Touch Area

Allowed (production path):
- `webapp/app_logic.js` — thay lớp kế toán cộng dồn bằng adapter gọi sổ L-1; version detection;
  banner cờ; snapshot trước thao tác phá huỷ
- `webapp/<module sổ cái L-1 mới>.js` — module sổ cái bounded (schema + `derive()` + migration).
  **Bắt buộc**: mọi file runtime MỚI phải được khai vào `PROJECT/PRODUCTION_PATHS.md` §1 trong
  cùng task — đây là khiếm khuyết `H-32` đã xảy ra ở `T-09B`, không được lặp lại
- `webapp/app_shell.html` — **chỉ** các trường nhập tối thiểu mà sổ L-1 đòi (`businessDate`,
  `openingPosition`, `source`, sửa/xoá). KHÔNG thiết kế lại giao diện
- `webapp/build_app.js` — thêm module mới vào bundle

Allowed (không phải production path):
- `webapp/test_*.js` (test mới của L-1), fixture tổng hợp
- `docs/tasks/T-12-*.md`, `docs/reviews/`, `docs/sessions/`
- `PROJECT/PRODUCTION_PATHS.md`, `PROJECT/PROJECT_PROGRESS.md`,
  `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`,
  `PROJECT/HARDENING_BACKLOG.md`
- `.gitignore` (đường `private/` của §22.1)

Do not touch without Scope Expansion:
- `src/eth_dca_os/**` — frozen historical research authority (`DEC-041` A)
- `docs/spec/**` — cấm sửa (Master Index §6)
- `webapp/engine.js` — chỉ báo/OSCORE, ngoài đường tiền của L-1 (`INV-10`)
- `firebase.json`, `firestore.rules`, `webapp/firebase_config.js` — bước C (`H-42`)
- `pyproject.toml`, `pyproject.lock`
- Test cũ (`test_t09a_accounting.js`, `test_t09b_persistence.js`, `test_v01_v02_v03.js`,
  `test_zone.js`, `test_multi_month_invariant.js`, `test_app.js`): xem `CHECK-T12-13` —
  không được làm yếu / bỏ chọn để lấy suite xanh

## Ràng buộc kiến trúc đã được spec khoá (implementer KHÔNG được quyết lại)

1. `derive()` là hàm **thuần**; `asOfDate` là **tham số**, không đọc `new Date()` bên trong (§9.1).
2. Đúng **một** chỗ trong toàn bộ mã được phép hỏi giờ hệ thống, và nó trả `YYYY-MM-DD` theo
   `Asia/Ho_Chi_Minh` (§10.2).
3. Trường dẫn xuất **không được lưu** xuống durable state (§9.4, `INV-1`).
4. **Không** trường tỷ giá nhập tay trên từng `TRADE`; **không** `vndRateOverride`
   (§5.3, `DEC-042` §4).
5. Xoá là **hard delete**, không tombstone; bù bằng snapshot bắt buộc (§15.3, `INV-14`).
6. `seq` cấp lúc tạo, **không** đánh số lại khi sửa; `id` không tái sử dụng (§10.7, `INV-15`).
7. `plannedAmount` dẫn xuất từ `plan`, **không** ghép qua pool `Base`/`Smart`/`Opportunity`
   (§11.1) — các pool đó `DROP_LEGACY_ONLY` (§17.2).

---

## Financial invariants — ma trận phủ `INV` × `SC` × test

Ma trận này là **hợp đồng**: không được đạt suite xanh trong khi một `INV` REQUIRED chưa có test
nhắm đích. Cột "Test nhắm đích" là **yêu cầu**, tên file/hàm do implementer đặt.

| INV | Yêu cầu (rút gọn — bản đủ ở spec §20) | Golden scenario | Test nhắm đích bắt buộc | Evidence |
|---|---|---|---|---|
| `INV-1` | Chỉ dẫn xuất; không lưu `qty/cost*/avg*/invested*/remaining*/next*/price/rate` | SC-01, SC-05, SC-06 | Quét payload durable: 0 khoá dẫn xuất bị cấm; `derivedSnapshot` (nếu có) bị import BỎ QUA | E1 + E2 |
| `INV-2` | Tất định: cùng tập event → cùng `DerivedState`, độc lập thứ tự nhập / đồng hồ / múi giờ máy | SC-04, SC-07, SC-08 | Hoán vị ngẫu nhiên mảng event (≥ 100 hoán vị) → `DerivedState` trùng bit; chạy lại dưới ≥ 2 giá trị `TZ` khác nhau của tiến trình | E1 + E2 |
| `INV-3` | Bảo toàn: `usdtCostVnd = 0` ⟺ `usdtQty = 0`; VND chỉ sinh bởi opening/P2P, chỉ mất bởi giải phóng bình quân | SC-02, SC-03, SC-06 | Cạn pool: phần dư đi vào `realizedFxVnd` của chính event làm cạn (§6.5); không đồng nào sống sót | E1 + E2 |
| `INV-4` | Không âm tại **mọi tiền tố** replay; vi phạm → `LEDGER_INCONSISTENT` + id event đầu tiên | — | `usdtOut > usdtQty` (§8.4) và `RESERVE(WITHDRAW)` vượt số dư → cờ + `firstOffendingEventId` đúng; app KHÔNG tự sửa dữ liệu | E1 + E2 |
| `INV-5` | Tiền là số nguyên; không float nào xuống durable | SC-03, SC-04 | Quét đệ quy payload durable: mọi trường tiền/lượng là integer; `Number.isInteger` toàn bộ | E1 |
| `INV-6` | Ngày sạch: chỉ `businessDate` vào phép tính; `createdAt`/`updatedAt` không bao giờ | SC-07, SC-08, SC-11 | Đổi `createdAt` của mọi event sang giá trị bất kỳ → `DerivedState` **không đổi** | E1 + E2 |
| `INV-7` | Không event nào có `businessDate < openingPosition.asOf` | SC-01 | Ghi event vi phạm → **từ chối lưu**, nêu lý do; không im lặng chấp nhận | E1 |
| `INV-8` | P2P không đóng góp `investedThisMonth`, `planInvested`, `assetQty`, `assetCost*` | SC-02 | Chuỗi chỉ có `TREASURY` → cả bốn đại lượng = 0 / không đổi | E1 |
| `INV-9` | `RESERVE` và `TRADE source ∈ {EXTRA, RESERVE}` không đổi `planInvested`, `remainingPlannedBudget`, `carryOut` | SC-09, SC-10 | So khớp cặp: cùng tháng, thêm/bớt event `EXTRA`+`RESERVE` → ba đại lượng bất biến | E1 + E2 |
| `INV-10` | Tín hiệu không được chạm tiền: không score/regime/giá nào tạo, sửa hay định cỡ event | SC-10 | (a) module sổ cái không tham chiếu `ENGINE`/`engine.js`; (b) đổi tuỳ ý dữ liệu chỉ báo/`PRICE` → `DerivedState` phần tiền **không đổi** | E1 + E2 |
| `INV-11` | Không biết ≠ 0; không fallback FX ẩn theo từng lệnh | SC-12 | `openingPosition.usdt.costVnd = null` → `avgCostVnd = UNKNOWN` lan truyền, `qty`/`costUsdt` vẫn đúng; grep schema: **không tồn tại** trường tỷ giá theo lệnh | E1 + E2 |
| `INV-12` | Migration nguyên tử: ghi trọn sổ mới hoặc không ghi gì | SC-12 | Ép lỗi ở giữa migration (`M-1`…`M-4`) → durable state **không đổi một byte** | E1 + E2 |
| `INV-13` | Chia `n` phần luôn cộng lại đúng khoản gốc | SC-09 | `SPLIT_VND` với `n = 1..12` trên ≥ 50 số ngẫu nhiên: `Σ phần == gốc` tuyệt đối | E1 |
| `INV-14` | Snapshot export đầy đủ **trước** `import` / `wipe` / `migration` | SC-06, SC-12 | Ba đường đều tạo snapshot TRƯỚC khi chạm durable; huỷ giữa chừng vẫn còn snapshot | E1 + E2 |
| `INV-15` | `id`/`seq` cấp một lần, không tái sử dụng, sửa giữ nguyên cả hai | SC-05, SC-07 | Xoá event rồi tạo event mới → `id` mới ≠ id đã xoá; sửa 20 lần → `id`/`seq` bất biến | E1 |

### Ma trận `SC` → hàm production dưới test → fixture → INV

| SC | Nội dung | Đường production dưới test | Fixture | INV phủ |
|---|---|---|---|---|
| SC-01 | Số dư đầu kỳ ETH + USDT | `derive()` với `openingPosition`, `events = []` | nền chung §19 | `INV-1`, `INV-7` |
| SC-02 | P2P VND→USDT | `derive()` + cập nhật pool §6.3 | nền + 1 `TREASURY` | `INV-8`, `INV-3` |
| SC-03 | Mua ETH bằng USDT có phí | `derive()` + §7.3 | nối SC-02 | `INV-3`, `INV-5` |
| SC-04 | Nhiều tỷ giá P2P rồi mua | WAC trộn §6.3 | nối SC-03 | `INV-2`, `INV-3`, `INV-13` |
| SC-05 | Sửa giao dịch cũ | đường `edit` + `derive()` | sửa `qty` của SC-03 | `INV-1`, `INV-15`, `INV-2` |
| SC-06 | Xoá giao dịch | đường `delete` (hard) + snapshot + `derive()` | xoá `TREASURY` của SC-04 | `INV-3`, `INV-14` |
| SC-07 | Nhập muộn theo ngày thật | thứ tự `(businessDate, seq)` §5.4 | nối SC-04 | `INV-6`, `INV-15` |
| SC-08 | Ranh giới tháng `Asia/Ho_Chi_Minh` | `today()` §10.2 + `currentMonth` §10.3 | instant UTC 2026-02-28T18:30Z | `INV-6`, `INV-2` |
| SC-09 | Mua thêm ngoài kế hoạch | §11.2, §11.3, `SPLIT_VND` §10.5 | tháng 2026-03 | `INV-9`, `INV-13` |
| SC-10 | Giải ngân dự phòng thủ công | §12.2 + `source = RESERVE` | nối SC-09 | `INV-9`, `INV-10` |
| SC-11 | Dữ liệu tháng tương lai | §10.6 + cờ `FUTURE_DATED_EVENTS` | `asOfDate` 2026-03-15 | `INV-6` |
| SC-12 | Migration thiếu giá vốn VND | migration §17 + `W-1` §17.4-B | state legacy `ethdca.tracker/1` tổng hợp | `INV-11`, `INV-12`, `INV-14` |

**Số kỳ vọng của `SC-01`…`SC-12` là hợp đồng đóng băng ở spec §19.** Implementer **không được**
viết lại ngữ nghĩa hay số kỳ vọng của chúng; nếu một con số của spec hoá ra sai, dùng khối
`COMPLETION GATE CHANGE PROPOSAL` + trình Owner — không sửa im lặng.

---

## Migration boundary

Chỉ tới mức đủ để chuyển an toàn sang schema L-1. Phân loại canonical (§17.2) giữ nguyên bốn
nhãn: `SAFE_TO_MIGRATE`, `RECALCULATE`, `OWNER_CONFIRMATION_REQUIRED`, `DROP_LEGACY_ONLY`.

Yêu cầu bắt buộc:

1. Snapshot đầy đủ dữ liệu legacy **trước** khi chạm durable state (`INV-14`).
2. Phát hiện version đầu vào **tất định** (`schema: "ethdca.tracker/1"` vs `"coindca.ledger/2"`);
   không đoán, không suy diễn từ hình dạng dữ liệu.
3. **Không** diễn giải lại im lặng bất kỳ trường tài chính legacy nào — đặc biệt
   `trades[].vndRate` / `vndCost` (`RECALCULATE`, bỏ hoàn toàn, tính lại bằng WAC).
4. Hai tầng kết quả đúng §17.4: `M-1`…`M-4` = **DỪNG, không ghi gì**;
   `W-1` = **HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`**, không bịa tỷ giá.
5. Đối chiếu §17.3 trong ngưỡng đã cho; vượt ngưỡng = **thất bại migration**, không phải cảnh
   báo. `costVnd` là ngoại lệ có chủ đích — báo cáo, không phải điều kiện thất bại.
6. Không mất event nguồn liên quan migration; `ledger[]` legacy giữ **chỉ đọc**
   (`LEGACY_ARCHIVE`), không phép dẫn xuất nào đọc nó.
7. **Không** đưa `Base`/`Smart`/`Opportunity`/`ladder`/`zone`/`score` vào sự thật tài chính L-1.
8. Dữ liệu legacy **không bị xoá** bởi migration (§17.5).
9. **KHÔNG** migration Firebase trong `T-12` (`O-5`).

## Persistence boundary

Đã kiểm tra tại phiên tạo task: sổ cái v2 **bắt buộc** làm đổi schema đã lưu
(`webapp/app_logic.js:22` `schema: "ethdca.tracker/1"` → `coindca.ledger/2`), nên phần
persistence tối thiểu **không tách được** khỏi capability này và nằm **trong cùng task** —
không tạo task anh em (spec §11 của chỉ thị; `CAPABILITY_MODEL.md` §II.4 điều kiện 3 không thoả).

Ràng buộc kỹ thuật đã xác minh:

    firestore.rules chỉ allow-list ĐÚNG hai document: `ethdca/state`, `ethdca/seed`;
    mọi `ethdca/*` khác mặc định BỊ TỪ CHỐI (firestore.rules:96-105).

Hệ quả bắt buộc: sổ `coindca.ledger/2` phải nằm **bên trong document `ethdca/state` đã có**.
Tạo document/collection mới sẽ đòi sửa `firestore.rules` — thuộc bước C (`O-5`) và **không được
làm trong `T-12`**.

Trong phạm vi:
- serialize trạng thái sổ L-1 canonical;
- khôi phục **không trôi số** (round-trip bit-exact trên trường tài chính);
- version schema an toàn + đường từ chối/migrate state legacy theo spec;
- snapshot trước `import`/`wipe`/`migration`.

Ngoài phạm vi: Firebase isolation, auth, Hosting/rules (`O-5`).

### Persistence architecture — Owner-approved bounded scope (`DEC-043`, 2026-09-05)

Owner xác nhận và duyệt **thẩm quyền kiến trúc tối thiểu** mà `T-12` cần, giải quyết đúng
`ARCHITECTURE_CHANGE_REQUIRED` đã nêu ở § Stop conditions cho trường hợp đã phạm vi hoá ở trên
(schema mới nằm trong `ethdca/state`):

    ĐƯỢC PHÉP (`DEC-043`):
      - schema/version của sổ L-1 được thay thế/tiến hoá đại diện state đã lưu, NẰM BÊN TRONG
        ranh giới persistence CoinDCA đã được phép hiện có (document `ethdca/state`, đã
        allow-list tại `firestore.rules:104-105`);
      - định danh schema canonical = `coindca.ledger/2` (định nghĩa tại spec §5, KHÔNG phải
        một giá trị mới do implementer tự chọn);
      - chỉ thay đổi serialize/deserialize/version-detect/migration TỐI THIỂU mà `T-12` cần
        (§ Scope IN `S-A16`, `S-A12`).

    KHÔNG ĐƯỢC PHÉP bởi `DEC-043` (vẫn ngoài `T-12`, vẫn `O-5`):
      - collection/document Firestore MỚI ngoài `ethdca/state` + `ethdca/seed`;
      - sửa `firestore.rules`;
      - đổi kiến trúc Firebase (project, Hosting, auth);
      - di trú Firebase project.
      `H-42` / `R-1`…`R-5` (§18) vẫn là product-readiness work SAU `T-12`.

**Phạm vi phê duyệt này CHỈ giới hạn cho đúng thay đổi mà `T-12` đã đóng khung** (schema
`coindca.ledger/2` bên trong `ethdca/state`). Nếu thi hành phát hiện hành vi ĐÚNG của `T-12`
thật sự đòi một trong bốn mục "KHÔNG ĐƯỢC PHÉP" ở trên — ranh giới document/collection mới, sửa
`firestore.rules`, đổi kiến trúc Firebase, hoặc một topology persistence vượt xa khuôn khổ đã
đóng băng — thì **DỪNG LẠI với `ARCHITECTURE_CHANGE_REQUIRED` một lần nữa**; `DEC-043` KHÔNG
được suy diễn rộng ra thành thẩm quyền kiến trúc tổng quát.

## Production Reachability — định nghĩa PASS

Bằng chứng reachability phải đến từ **đường thực thi ngoài ranh giới module**
(`CAPABILITY_MODEL.md` § Production Reachability). Với repo này, đường đó đã tồn tại và được
`T-09A`/`T-09B` dùng: `webapp/test_firebase_harness.js` (Playwright + Chromium + Firestore
Emulator + `firestore.rules` thật) chạy trên `webapp/app_final.html` do `build_app.js` sinh.

    PRODUCTION REACHABILITY PASS  ⟺  TẤT CẢ các điều sau, đo trên app đã build:

    P-1  App được nạp qua `app_final.html` (bundle thật), KHÔNG gọi trực tiếp hàm module
         trong Node.
    P-2  Ít nhất **8 event thật** được tạo qua đường ghi của chính app, phủ tối thiểu:
         1 × openingPosition, 2 × TREASURY, 2 × TRADE(source=PLAN), 1 × TRADE(source=EXTRA),
         1 × RESERVE(CONTRIBUTE), 1 × TRADE(source=RESERVE có note).
    P-3  Ít nhất **1 sửa** và **1 xoá** thực hiện qua đường của app, và ít nhất **1 nhập muộn**
         (businessDate < ngày thao tác).
    P-4  Toàn bộ được ghi lên nguồn bền và **máy chủ xác nhận** (không tính cache SDK), rồi
         đọc lại từ SERVER.
    P-5  Reload trang → `derive()` chạy lại → 4 con số dashboard + holdings + giá vốn TRÙNG
         KHỚP oracle tính tay của kịch bản (đối chiếu tuyệt đối, `tolerance = 0`).
    P-6  Payload durable đọc lại KHÔNG chứa một khoá dẫn xuất bị cấm nào (`INV-1`).

    Anti-vacuity: 0 event / 0 case chạy qua đường production = **FAIL**, không phải PASS.
    Một suite unit test lớn KHÔNG thay thế được P-1…P-6.

## Change budget (ước lượng có ràng buộc)

**Phạm vi của con số này:** đây là budget **cấp task**. Nó **KHÔNG** khai
`SESSION_PRODUCTION_DIFF_MAX` / `GOLDEN_CUMULATIVE_DIFF_MAX` của tầng dự án.

### Ba khái niệm "golden/baseline" — TÁCH BẠCH, KHÔNG lẫn vào nhau (`DEC-043`, 2026-09-05)

| Khái niệm | Là gì | Dữ liệu | Trạng thái | Là Ready Gate của `T-12`? |
|---|---|---|---|---|
| `T12_GOLDEN_ACCOUNTING_BASELINE` | Bộ fixture `SC-01`…`SC-12` + số kỳ vọng canonical của spec §19, dùng làm oracle cho implementation/E2 của `T-12` | **Tổng hợp** (synthetic) | định nghĩa dưới đây | **CÓ** — chính là § SC Coverage của gate này |
| `GOLDEN_BASELINE_SHA` (tầng dự án, `H-10`) | Golden trace tái lập được của backtest/strategy engine V2.1.5 (`T-06`), dùng để đo `GOLDEN_CUMULATIVE_DIFF_MAX` và Golden Reduction của Blast Radius | dữ liệu thị trường thật (Binance) | vẫn `PENDING_OWNER_DATA / MIGRATION_REQUIRED` (`PRODUCTION_PATHS.md` §4) — **không đổi bởi quyết định này**, thuộc lineage `T-06`, không thuộc `CAP-WEBAPP` | **KHÔNG** — chưa từng, và vẫn không phải, phụ thuộc của `T-12` |
| `OWNER_LOCAL_ACCEPTANCE` (spec §22.1) | Chấp nhận dùng thật trên máy Owner | dữ liệu THẬT, riêng tư, ngoài repo | bước **D**, ngoài `T-12` (`O-6`) | **KHÔNG** |

Câu ở bản trước — *"`GOLDEN_BASELINE_SHA` vẫn `PENDING_OWNER_DATA`"* — bị Owner xác nhận là **gây
hiểu lầm** khi đọc trong ngữ cảnh `T-12`: nó khiến tưởng rằng gate kế toán tự động của `T-12` cần
dữ liệu thật của Owner. **Không đúng.** `T-12` không, và chưa từng, phụ thuộc dòng
`GOLDEN_BASELINE_SHA` của tầng dự án; dòng đó thuộc lineage `T-06`/backtest, KHÔNG phải
`CAP-WEBAPP`, và **KHÔNG** phải Ready Gate của `T-12`.

**Định nghĩa `T12_GOLDEN_ACCOUNTING_BASELINE`:**

    T12_GOLDEN_ACCOUNTING_BASELINE_SHA =
      SHA của commit ĐẦU TIÊN trên nhánh thi hành T-12 đưa đủ 12 fixture SC-01…SC-12
      (dữ liệu vào + số kỳ vọng, khớp NGUYÊN VĂN spec §19) vào dưới dạng file test đã commit.

    Thời điểm đóng băng = ngay khi commit đó được tạo. Từ thời điểm đó, số kỳ vọng của fixture
    là FROZEN — cùng quy tắc đã áp cho spec §19 (implementer không được viết lại ngữ nghĩa/số
    kỳ vọng SC); mọi thay đổi sau đó phải qua `COMPLETION GATE CHANGE PROPOSAL`.

    Vì T-12 chưa thi hành, SHA này CHƯA TỒN TẠI tại thời điểm định nghĩa task — đây là quy tắc
    xác định NÓ SẼ được đóng băng thế nào, không phải một SHA bịa ra trước. Không chọn SHA tiện
    tay: `T12_MEASURE_BASE_SHA` bên dưới là mốc đo diff, KHÔNG phải baseline kế toán, và hai giá
    trị này KHÔNG được đọc lẫn vào nhau.

    Dùng bởi: CHECK-T12-08 (oracle của SC), và là input bắt buộc cho vòng E2 độc lập.

    MỐC ĐO CẤP TASK (không phải Golden baseline):
      T12_MEASURE_BASE_SHA = 91cfbba5e3af01d432c64369bb5a286f6461ab6a   (origin/main, 2026-09-05)

    Lệnh đo (không cộng tay từ báo cáo):
      git diff --shortstat 91cfbba..HEAD -- \
        webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js \
        <module sổ cái L-1 mới> src/eth_dca_os pyproject.toml pyproject.lock

| Hạng mục | Ước lượng | Trần |
|---|---|---|
| File production dự kiến | 4 sửa + 1–2 mới | ≤ 7 file |
| File test dự kiến | 4–5 mới | — |
| File migration/adapter | nằm trong 1–2 file mới ở trên | — |
| Diff production | ≈ +1.300 / −300 | **+1.600 / −450** |
| Diff test | ≈ +2.250 | — |
| Repair cycle tối đa | **1 pre-authorized có điều kiện** (`DEC-043`) — xem § Budget review/repair | — |
| Vòng E2 dự trù | **1** (vòng độc lập đầu tiên) | — |

Vượt trần production **hoặc** thêm file production ngoài danh sách → dừng và ghi
`CHANGE_BUDGET_EXCEEDED` hoặc `SCOPE_CHANGED`, quay lại Owner. **Không** âm thầm mở rộng.

## Budget review/repair — MỘT chu kỳ pre-authorized có điều kiện (`DEC-043`)

    Lineage root          = WP-C1  (CAP-WEBAPP)
    ALLOWED (capability)  = 2 repair cycle   (Owner Decision DEC-018 / OD-WEBAPP-01)
    USED                  = 0
    REMAINING             = 2
    T-12 PRE-AUTHORIZED   = 1 repair cycle, RÚT TỪ pool CAP-WEBAPP hiện có
                            (KHÔNG cộng thêm budget, KHÔNG tạo lineage mới — DEC-043, 2026-09-05)

`T-12` là task MỚI **bên trong** capability đã có; nó **không** làm budget reset trên trục ngang
(`GOVERNANCE_V4.md` §II.2). Lượt thi hành đầu tiên là **implementation ban đầu**, theo tiền lệ
đã ghi cho `CAP-PROV` §1, `CAP-DATA` §2.1, `CAP-VERDICT`/`CAP-WEBAPP` §2.2 của
`REVIEW_BUDGET_LEDGER.md`: **không tiêu repair cycle**.

### Pre-authorization (`DEC-043`, 2026-09-05) — Owner cấp trước, không phải bỏ qua quy tắc

`CAPABILITY_MODEL.md` §II.8 vẫn đúng nguyên văn: *"task creation approval != repair-budget
allocation approval"*, và `migration_status` của `CAP-WEBAPP` chưa từng khai `ADOPTED`. Owner
KHÔNG bỏ qua quy tắc đó — Owner thực hiện đúng bước quy tắc đòi, chỉ khác là TRƯỚC thay vì SAU:
`DEC-043` LÀ Owner Decision cấp phép cho repair cycle đầu tiên của `T-12`, ghi trước thay vì chờ
FAIL rồi mới xin.

    ĐIỀU KIỆN dùng chu kỳ pre-authorized này — TẤT CẢ phải đúng đồng thời:
    - một REQUIRED check của T-12 (CHECK-T12-01…-14) FAIL;
    - thất bại nằm TRONG capability T-12 đã đóng băng — không phải một hạng mục ngoài scope;
    - KHÔNG ngữ nghĩa tài chính nào của DEC-042/spec cần đổi (nếu cần đổi ⇒ đây không phải
      repair, đây là COMPLETION GATE CHANGE PROPOSAL + Owner Decision riêng — xem § Stop
      conditions);
    - KHÔNG cần thẩm quyền kiến trúc mới ngoài § Persistence boundary § Owner-approved bounded
      scope;
    - KHÔNG mở rộng phạm vi Firebase/auth;
    - KHÔNG cần task ID mới;
    - Expected Touch Area vẫn ≤ 7 file production;
    - diff production cộng dồn vẫn trong trần đã đóng băng (§ Change budget);
    - repair KHÔNG làm yếu/xoá một REQUIRED test/check/invariant nào.

    MỤC ĐÍCH DUY NHẤT được phép: làm cho capability T-12 ĐÃ DUYỆT thoả đúng hợp đồng đã đóng
    băng của chính nó.

    KHÔNG được phép dùng chu kỳ này để: thiết kế lại spec; diễn giải lại quy tắc kế toán; thêm
    tính năng; hấp thụ việc UI; thêm hành vi research/strategy; mở rộng phạm vi Firebase; làm
    yếu kỳ vọng SC/INV.

Nếu MỘT trong các điều kiện trên không đúng — ví dụ thất bại đòi đổi ngữ nghĩa tài chính, hoặc
đòi thẩm quyền kiến trúc ngoài phạm vi đã duyệt — chu kỳ pre-authorized **không áp dụng được**;
quay lại § Stop conditions (`OWNER_DECISION_REQUIRED` cho một Owner Decision MỚI; `DEC-043`
không tự hợp thức hoá trường hợp đó).

**Nếu chu kỳ pre-authorized này đã dùng** (USED 0→1, REMAINING của `CAP-WEBAPP` 2→1, đo bằng cặp
BASE/HEAD SHA theo đúng quy ước `REVIEW_BUDGET_LEDGER.md`) **và REQUIRED evidence vẫn FAIL:**
**DỪNG** với `OWNER_DECISION_REQUIRED` (nếu cần quyết định phạm vi/ngữ nghĩa) hoặc
`CHANGE_BUDGET_EXCEEDED` (nếu vượt trần diff) — theo đúng trường hợp thực tế. **Không** tự cấp
chu kỳ thứ hai.

Hết cả pre-authorization lẫn pool `CAP-WEBAPP` thì chỉ còn `ACCEPT_AS_IS` / `DESCOPE` /
`OWNER_EXTENSION`; tạo thêm một unit công việc **không** nằm trong ba lựa chọn đó.

---

## Ready Gate

`governance/core/TASK_READY_GATE_STANDARD.md` § MAJOR — 17/17 xác nhận tại `S032` (2026-09-05):

- [x] Objective rõ ràng — § Objective, neo spec §5/§9/§17/§19/§20
- [x] Scope được định nghĩa — `S-A1`…`S-A17`
- [x] Out-of-scope được định nghĩa — `O-1`…`O-12`
- [x] Dependencies DONE hoặc được waive tường minh — bảng § Dependencies: `DEC-040`/`DEC-041`/
      `DEC-042` effective, spec `CANONICAL — APPROVED`, 4 task lineage `CAP-WEBAPP` đều DONE
- [x] Expected touch area đã xác định — § Expected Touch Area, có cả danh sách cấm chạm
- [x] Yêu cầu nghiệp vụ được hiểu — spec §1–§16 + 4 quyết định Owner `DEC-042` §21
- [x] Tác động dữ liệu đã biết — đổi schema đã lưu `ethdca.tracker/1` → `coindca.ledger/2`;
      § Persistence boundary
- [x] Tác động bảo mật đã biết — không đụng auth/rules/hosting (`O-5`); `R-1`…`R-5` của §18 vẫn
      là điều kiện chặn TRƯỚC khi ghi tiền thật, `T-12` không gỡ điều kiện nào
- [x] Tác động routing/API đã biết — không có HTTP API; "API" ở đây là hợp đồng module sổ cái +
      hợp đồng schema đã lưu (`20_API_VERSIONING_COMPATIBILITY.md` kích hoạt theo
      `PROJECT_PROFILE.md` § Conditional Governance vì định dạng lưu là hợp đồng tương thích)
- [x] Điều kiện tiên quyết migration sẵn có — bảng phân loại §17.2 đã canonical; fixture legacy
      dựng được từ `emptyState()` (`app_logic.js:20-35`) bằng dữ liệu **tổng hợp**; các dòng
      `OWNER_CONFIRMATION_REQUIRED` cần Owner **lúc CHẠY migration trên dữ liệu thật**, không
      phải lúc thi hành — `T-12` xây bề mặt xác nhận đó, không cần số thật (`DEC-041` C)
- [x] Difficulty đã chấm — 4/4
- [x] Risk đã chấm — 3/4
- [x] Blast Radius đã chấm — 3/4
- [x] Primary agent tier đã gán — D / Fable / max, có bằng chứng router chạy lại được
- [x] Escalation triggers đã định nghĩa — § Escalation Triggers
- [x] Completion Gate đã hoàn tất — 14 REQUIRED check dưới đây
- [x] Completion Gate đóng băng trước khi thi hành — `Completion Gate Freeze: FROZEN 2026-09-05`

**Không có mục nào được đánh dấu thoả bằng lời hứa tương lai.** Nếu một mục ở trên hoá ra chưa
thoả khi mở phiên thi hành, task quay về `PLANNED` chứ không đi tiếp.

### Tái xác nhận Ready Gate sau `DEC-043` (2026-09-05, `S033`)

Owner yêu cầu tái đánh giá sau ba tu chỉnh (`DEC-043`, `PROJECT_DECISIONS.md`). Kết quả: **`T-12` GIỮ NGUYÊN
`READY`** — không mục nào trong 17 mục ở trên bị mất điều kiện; hai mục sau được CỦNG CỐ thêm
(không đổi từ thoả → không thoả):

- *Tác động dữ liệu / bảo mật đã biết* — khoảng trống thẩm quyền kiến trúc trước đây (persistence
  bên trong `ethdca/state`) nay có phê duyệt Owner tường minh (`DEC-043`, § Persistence boundary
  § Owner-approved bounded scope), thay vì chỉ là một giả định thi hành.
- *Điều kiện tiên quyết migration / dữ liệu* — Owner xác nhận **không cần dữ liệu tài chính thật**
  để bắt đầu hay hoàn tất gate kế toán tự động; `T12_GOLDEN_ACCOUNTING_BASELINE` (tổng hợp) là đủ
  (§ Change budget § Ba khái niệm golden/baseline).

Không phát sinh điều kiện tiên quyết mới nào chưa thoả. Không `READY_GATE_FAIL`.

---

## Completion Gate

`governance/core/TASK_COMPLETION_GATE_STANDARD.md` + `governance/core/EVIDENCE_STANDARD.md`.
14 check, **tất cả REQUIRED**. Trạng thái ban đầu: `NOT_TESTED`.

Quy ước Evidence của gate này (`Risk 3/4`, `Blast Radius 3/4`, category `accounting_financial`):
`E1` là **tối thiểu bắt buộc** cho mọi check thực thi được; các check thuộc nhóm tính đúng tài
chính / bất biến sổ cái / migration / persistence / reachability thêm **`E2` độc lập** — xem
§ Evidence / E2.

### Correctness — sự thật tài chính

#### CHECK-T12-01 — Schema L-1 canonical, không rò rỉ sự thật chiến lược legacy
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: durable state mang `schema = "coindca.ledger/2"`; chứa đúng `plan`, `openingPosition`,
`events[]` theo §5; **không** chứa `months[].base/smart/oppAdded/oppOverflow`, `oppFund`,
`ladders`, `zones`, `trades[].src ∈ {BASE,SMART,OPPORTUNITY}`, `recPrice`, `shortfallBps`,
`zone` như dữ liệu tài chính. `ledger[]` legacy nếu giữ thì mang nhãn `LEGACY_ARCHIVE` và
không phép dẫn xuất nào đọc. Bằng chứng: quét khoá trên payload durable thật + danh sách khoá bị
cấm.

Executed By:
—

Timestamp:
—

#### CHECK-T12-02 — `openingPosition + events -> derive()` tất định
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `derive()` là hàm thuần (không `new Date()` bên trong, không đọc `createdAt`), cùng
tập event cho cùng `DerivedState` dưới ≥ 100 hoán vị thứ tự nhập và ≥ 2 `TZ` tiến trình khác
nhau. Phủ `INV-2`, `INV-6`. Golden: `SC-04`, `SC-07`, `SC-08`.

Executed By:
—

Timestamp:
—

#### CHECK-T12-03 — Giá vốn VND: WAC trên một pool USDT, đúng số
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `vndRelieved = ROUND_VND(usdtOut × usdtCostVnd / usdtQty)`; giải phóng theo bình quân
**không** làm đổi bình quân; phí USDT vào cả hai giá vốn; bán crypto/bán USDT giải phóng theo
cùng phương pháp; cạn pool ép `usdtCostVnd = 0` và đẩy phần dư vào `realizedFxVnd`. Số kỳ vọng
đối chiếu **tuyệt đối** (`tolerance = 0`) với `SC-01`…`SC-04`, `SC-06`. Phủ `INV-3`.

Executed By:
—

Timestamp:
—

#### CHECK-T12-04 — `UNKNOWN` lan truyền thấy được, không bao giờ bị ép về 0
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `openingPosition.usdt.costVnd = null` (và phần USDT thiếu phủ của §8.4) → `qty` và
`costUsdt` giữ nguyên đúng, phần `costVnd` liên quan = `UNKNOWN`, hiển thị `—`, cờ
`UNKNOWN_VND_BASIS` thường trực và **không ẩn được bằng một lần bấm**. Grep schema chứng minh
**không tồn tại** trường tỷ giá nhập theo từng lệnh (`vndRateOverride` hoặc tương đương).
Phủ `INV-11`. Golden: `SC-12`.

Executed By:
—

Timestamp:
—

#### CHECK-T12-05 — Sửa / xoá / nhập muộn tính lại đúng, không trôi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: sửa giữ `id`+`seq`, cập nhật `updatedAt`, chạy lại toàn bộ; **không tồn tại** phép
"hoàn tác tác động cũ" trong mã; xoá cứng TƯƠNG ĐƯƠNG CHÍNH XÁC với chưa từng nhập; nhập muộn
được xếp theo `businessDate` chứ không theo lúc nhập. Phủ `INV-1`, `INV-15`. Golden: `SC-05`,
`SC-06`, `SC-07`.

Executed By:
—

Timestamp:
—

#### CHECK-T12-06 — Ngày nghiệp vụ, `Asia/Ho_Chi_Minh`, tháng lịch
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `businessDate` là chuỗi, so sánh chuỗi, `month = slice(0,7)`; **đúng một** chỗ trong
toàn bộ mã hỏi giờ hệ thống và nó trả ngày theo `Asia/Ho_Chi_Minh`; `currentMonth` = tháng của
`asOfDate`, KHÔNG phải khoá tháng lớn nhất trong dữ liệu; `carryOut` chỉ chốt cho tháng đã đóng.
Bằng chứng gồm grep chứng minh không còn `getMonth()`/`toISOString()` trong đường tính tiền.
Phủ `INV-6`. Golden: `SC-08`, `SC-11`. Đóng `B3`, `B4`, `B7` của `H-41`.

Executed By:
—

Timestamp:
—

#### CHECK-T12-07 — Số nguyên VND, làm tròn đối chiếu được, thứ tự tất định
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: quét đệ quy payload durable — 0 giá trị float ở trường tiền/lượng; `SPLIT_VND(x, n)`
với `n = 1..12` trên ≥ 50 giá trị: `Σ phần == x` tuyệt đối; `ORDER = (businessDate ASC, seq ASC)`
được kiểm bằng test. Phủ `INV-5`, `INV-13`. Đóng `B9`.

Executed By:
—

Timestamp:
—

### Golden / Invariant coverage

#### CHECK-T12-08 — `SC-01`…`SC-12` PASS trên dữ liệu tổng hợp
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: **12/12** golden scenario của spec §19 chạy được và PASS, đối chiếu tuyệt đối với số
kỳ vọng đã đóng băng ở spec (không nới `tolerance`, không làm tròn để khớp). Báo cáo phải in
bảng SC × (kỳ vọng / thực tế). Ngữ nghĩa và số kỳ vọng của SC **không được viết lại**.

Executed By:
—

Timestamp:
—

#### CHECK-T12-09 — `INV-1`…`INV-15` được phủ, không bất biến REQUIRED nào bỏ trống
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: mỗi dòng của ma trận `INV` ở trên có **ít nhất một test nhắm đích** thực sự đỏ khi bất
biến bị phá (chứng minh bằng mutation/nghịch đảo có chủ đích cho tối thiểu `INV-1`, `INV-3`,
`INV-4`, `INV-9`, `INV-11`, `INV-12`, `INV-14`). Không được để một `INV` chỉ "được phủ gián
tiếp" bởi một SC mà không có phép khẳng định trực tiếp.

Executed By:
—

Timestamp:
—

### Migration

#### CHECK-T12-10 — Hợp đồng migration PASS, gồm dữ liệu mơ hồ
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu, trên fixture legacy **tổng hợp**:
(a) snapshot legacy được ghi TRƯỚC mọi thao tác ghi (`INV-14`);
(b) phát hiện version tất định;
(c) phân loại §17.2 áp đúng cho từng trường; `trades[].vndRate/vndCost` bị bỏ và tính lại;
(d) đối chiếu §17.3 trong ngưỡng; vượt ngưỡng ⇒ FAIL migration (kiểm bằng một fixture cố ý lệch);
(e) `M-1`…`M-4` ⇒ **DỪNG, durable không đổi một byte** (`INV-12`);
(f) `W-1` ⇒ **HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`**, không bịa tỷ giá (`SC-12`);
(g) dữ liệu legacy không bị xoá; `ledger[]` chỉ đọc;
(h) không `Base`/`Smart`/`Opportunity`/`ladder`/`zone`/`score` nào lọt vào sự thật tài chính L-1.

Executed By:
—

Timestamp:
—

### Persistence

#### CHECK-T12-11 — Round-trip persistence giữ nguyên sự thật sổ cái
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: ghi → máy chủ xác nhận → đọc lại từ SERVER → `derive()` cho `DerivedState` **trùng
tuyệt đối**; payload durable không chứa khoá dẫn xuất bị cấm (`INV-1`); nếu file export có khối
`derivedSnapshot` thì import **bỏ qua** khối đó (kiểm bằng file export bị sửa tay). Sổ nằm trong
document `ethdca/state` đã được `firestore.rules` allow-list — **không** tạo document mới.

Executed By:
—

Timestamp:
—

### Production reachability

#### CHECK-T12-12 — Production Reachability PASS
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `P-1`…`P-6` của § Production Reachability, đo trên `app_final.html` đã build qua
`webapp/test_firebase_harness.js` (Playwright + Firestore Emulator + rules thật). Báo cáo phải
nêu **số event thật** và **số case** đã chạy qua đường production. `0 event / 0 case = FAIL`.
Mọi file runtime MỚI được khai vào `PROJECT/PRODUCTION_PATHS.md` §1 (khiếm khuyết `H-32` không
được lặp lại).

Executed By:
—

Timestamp:
—

### Regression

#### CHECK-T12-13 — Regression áp dụng được PASS, không test nào bị làm yếu
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy đủ suite áp dụng được (`webapp/`: `npm test`; Python: `pytest`) và báo cáo con số
trước/sau. Test cũ mô tả hành vi **đã bị `DEC-041`/`DEC-042` gỡ bỏ** (ladder/zone/pool
Base-Smart-Opportunity) chỉ được đánh dấu `NOT_APPLICABLE` kèm neo quyết định tường minh, từng
file, từng ca — **không** được xoá/skip/deselect hàng loạt để lấy suite xanh, và số ca
`NOT_APPLICABLE` phải được liệt kê đích danh trong báo cáo. Không test nào của `src/eth_dca_os`
được đổi.

Executed By:
—

Timestamp:
—

### Ranh giới sản phẩm

#### CHECK-T12-14 — Không hồi quy productization chiến lược
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: Buy Score / OSCORE / regime / crash / ladder / recommendation **không** nằm trên đường
quyết định tài chính L-1: (a) module sổ cái không tham chiếu `ENGINE`/`engine.js`; (b) đổi tuỳ ý
dữ liệu chỉ báo và event `PRICE` → phần tiền của `DerivedState` **không đổi**; (c) không tín
hiệu nào tạo/gợi ý/định cỡ một `TRADE`, đặc biệt `source = RESERVE` (bắt buộc có `note` do người
dùng nhập). Phủ `INV-10`. Neo: `DEC-041` B, `DEC-042` §3, spec §12.3.

Executed By:
—

Timestamp:
—

---

## Exit Criteria

- [ ] 14/14 REQUIRED check PASS
- [ ] Evidence level thoả: `E1` toàn bộ; `E2` độc lập PASS cho khối tính đúng tài chính
      (xem § Evidence / E2)
- [ ] 0 defect nghiêm trọng chưa xử lý; 0 finding BLOCKING còn mở có đường production hiện hành
- [ ] Regression áp dụng được PASS, không REQUIRED check nào bị xoá/làm yếu
- [ ] `PROJECT/PRODUCTION_PATHS.md` khai đủ mọi file runtime mới
- [ ] `PROJECT/PROJECT_PROGRESS.md` cập nhật; `sync_easy_roadmap.py` chạy lại;
      `validate_routing.py` + `validate_easy_roadmap.py` PASS
- [ ] `PROJECT/REVIEW_BUDGET_LEDGER.md` cập nhật (diff đo bằng lệnh, không cộng tay)
- [ ] `H-41` được cập nhật: hạng mục nào đã đóng bằng kiến trúc, hạng mục nào còn lại
- [ ] Session handoff được viết (`MAJOR` bắt buộc)
- [ ] Owner đóng vòng đời (`IMPLEMENTED → DONE`) — xem § Owner closure authority

## Evidence / E2

**Không đổi bởi `DEC-043`.** Yêu cầu `E2` độc lập dưới đây giữ NGUYÊN VẸN đúng như đã đóng băng;
implementer vẫn không được tự chứng nhận `E2`. Tám điểm dò đối kháng bắt buộc (số học WAC, lan
truyền `UNKNOWN`, tính lại sau sửa/xoá/nhập muộn, ranh giới tháng/múi giờ, mơ hồ migration,
round-trip persistence, production reachability, state dị dạng/thiếu) không mất mục nào.

Phân bổ theo `EVIDENCE_STANDARD.md` (Risk 3 ⇒ `E1` bắt buộc cho mọi kiểm chứng thực thi được;
`DEC-041` J ⇒ `E2` bắt buộc cho **tính đúng tài chính, bất biến sổ cái, migration, persistence**).

    E2 BẮT BUỘC (một vòng rà soát độc lập, phủ TRỌN khối này như MỘT chỉnh thể):
      CHECK-T12-02, -03, -04, -05, -06, -09, -10, -11, -12

    E1 là đủ:
      CHECK-T12-01, -07, -08, -13, -14
      (vẫn nằm trong tầm quan sát của reviewer E2, chỉ không đòi verdict E2 riêng)

Người thi hành **KHÔNG được tự chứng nhận E2**. E2 tạo bằng thủ tục "Solo Independent Review"
(`EVIDENCE_STANDARD.md`): phiên reviewer riêng, bắt đầu từ trạng thái repo, đọc gate đã đóng
băng, tự chạy lại kiểm chứng, coi mọi câu PASS của implementer là narrative chưa tin được. Lưu
tại `docs/reviews/` theo `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.

E2 phải dò đối kháng tối thiểu tám điểm sau (không đòi E2 cho chi tiết mỹ thuật/không liên quan
tiền):

1. số học WAC — gồm cạn pool, phần dư làm tròn, bán ra;
2. lan truyền `UNKNOWN` — và chứng minh không tồn tại fallback FX ẩn;
3. sửa/xoá/nhập muộn — có tạo ra trôi số hay một phép hoàn tác ngầm nào không;
4. ranh giới tháng và múi giờ — gồm instant UTC rơi sang ngày hôm sau ở `Asia/Ho_Chi_Minh`;
5. mơ hồ migration — `M-1`…`M-4` vs `W-1`, và tính nguyên tử khi lỗi giữa chừng;
6. round-trip persistence — gồm file export bị sửa tay và state legacy;
7. production reachability — reviewer tự chạy harness, không tin số của implementer;
8. state dị dạng/thiếu — payload cắt cụt, kiểu sai, `null` ở chỗ không mong đợi, số vượt trần
   an toàn §10.4.

## Stop conditions

Chỉ năm hard-stop canonical (`DELIVERY_LOOP.md`) là hợp lệ; dừng vì lý do khác là
`UNAUTHORIZED_STOP`.

| Điều kiện gặp phải | Hành động |
|---|---|
| Cần dùng chu kỳ repair **thứ NHẤT** của `T-12`, đúng đủ điều kiện § Budget review/repair | Dùng chu kỳ pre-authorized (`DEC-043`) — **không** cần Owner Decision mới nếu đủ điều kiện |
| Cần chu kỳ repair **thứ HAI**, hoặc điều kiện của chu kỳ thứ nhất KHÔNG đủ | `OWNER_DECISION_REQUIRED` — `DEC-043` không tự động mở rộng |
| Vượt trần diff production hoặc thêm file production ngoài danh sách | `CHANGE_BUDGET_EXCEEDED` / `SCOPE_CHANGED` |
| Sổ L-1 cần collection/document Firestore MỚI, sửa `firestore.rules`, hoặc đổi kiến trúc Firebase (ngoài phạm vi đã duyệt ở `DEC-043`) | `ARCHITECTURE_CHANGE_REQUIRED` (chạm bước C) |
| Migration có nguy cơ làm mất/hỏng dữ liệu legacy hoặc snapshot không dựng được | `DATA_INTEGRITY_RISK` |
| Một con số kỳ vọng của `SC-01`…`SC-12` hoặc một `INV` mâu thuẫn nội tại với spec | `OWNER_DECISION_REQUIRED` + `COMPLETION GATE CHANGE PROPOSAL` — **không** sửa im lặng |
| Chạm ngưỡng Absorption (B: > 3 hạng mục hấp thụ; D: kéo việc ngoài lát cắt) | ghi `ABSORPTION_LIMIT_REACHED` → Owner Decision, **không tự tạo task** |
| Hết `SC` xanh nhưng còn `INV` chưa có test nhắm đích | KHÔNG được coi là `GOLDEN_PASS` |

KHÔNG phải hard-stop (phải `CONTINUE`): thiếu một hàm, thiếu một tham số, một test local đỏ, một
mẩu wiring còn thiếu, một adapter nhỏ phải viết, một finding vừa xuất hiện.

## Escalation Triggers

- `CAPABILITY_CEILING` — hai lượt liên tiếp không đạt cùng một REQUIRED check với cùng nguyên
  nhân gốc ⇒ `ESCALATION_PROTOCOL.md`; Escalation Tier/Effort đã ở trần (`D`/`max`), nên bước kế
  tiếp là Owner Decision chứ không phải tăng Tier.
- `CONFLICT DETECTED` — spec L-1 mâu thuẫn với mã/dữ liệu/hành vi hiện tại ⇒ khối `CONFLICT
  DETECTED` + `RULE_PRECEDENCE.md`.
- `SCOPE EXPANSION REQUIRED` — phải chạm ngoài Expected Touch Area.
- Phải chạm `firestore.rules` / `firebase.json` / auth ⇒ dừng, đây là bước C.
- Phải chạm `src/eth_dca_os/**` hoặc `docs/spec/**` ⇒ dừng, cả hai đã đóng băng.
- Xuất hiện nhu cầu dùng dữ liệu tài chính THẬT của Owner ⇒ dừng (`DEC-041` C).

## Implementation authority

- **Được phép**: thi hành `S-A1`…`S-A17` trong Expected Touch Area; viết test mới; viết adapter
  tối thiểu; khai file production mới vào `PRODUCTION_PATHS.md`; cập nhật `PROJECT/` state theo
  đúng holder canonical.
- **Không được phép**: tạo thêm bất kỳ task ID nào (kể cả task con / task anh em / task dọn dẹp);
  tự cấp một chu kỳ repair NGOÀI chu kỳ pre-authorized của `DEC-043` (và ngay cả chu kỳ đó phải
  tự đối chiếu đủ điều kiện § Budget review/repair trước khi dùng, ghi rõ trong evidence); tự
  khai `T12_GOLDEN_ACCOUNTING_BASELINE_SHA` sai với quy tắc đóng băng đã định nghĩa; làm yếu/xoá
  REQUIRED check; tự chứng nhận `E2`; viết `FROZEN` hay `DONE` cho chính mình; sửa lịch sử quyết
  định; suy diễn rộng thẩm quyền kiến trúc của `DEC-043` ra ngoài phạm vi đã đóng khung.
- Trạng thái mà người thi hành được ghi: `IN_PROGRESS`, `IMPLEMENTED`, `BLOCKED` (chỉ với một
  trong năm hard-stop). `DONE` thuộc Owner.

## Owner closure authority

`IMPLEMENTED → DONE` là hành động của Owner (`STATE_AUTHORITY.md` § The State Machine And Who May
Write It), ghi vào `PROJECT/PROJECT_DECISIONS.md` bằng DEC ID hợp lệ kế tiếp, cùng khuôn
`DEC-036`/`DEC-037`/`DEC-038`. Owner cũng là người duy nhất:

- cấp repair budget cho `T-12` nếu cần;
- chấp nhận `ACCEPT_AS_IS` / `DESCOPE` / `OWNER_EXTENSION` khi budget cạn;
- duyệt bất kỳ `COMPLETION GATE CHANGE PROPOSAL` nào.

---

## Truy vết `H-41` (`B1`–`B10`) — ràng buộc, KHÔNG phải mười task

`H-41` yêu cầu mỗi hạng mục được **trả lời hoặc bác bỏ tường minh**. `T-12` không tạo một task
sửa lỗi nào cho `B1`–`B10`; nó thay mô hình sự thật và do đó xoá cả lớp lỗi.

| # | Phân loại | Neo trong `T-12` |
|---|---|---|
| `B1` | `CLOSED_BY_ARCHITECTURE` | ladder/zone `DROP_LEGACY_ONLY`; khái niệm không tồn tại dưới L-1 (`CHECK-T12-01`); `M-4` chặn migration khi zone đã phát tác (`CHECK-T12-10`) |
| `B2` | `CLOSED_BY_ARCHITECTURE` | không còn pool cộng dồn; `planInvested` dẫn xuất từ `vndRelieved` (`CHECK-T12-01`, `-03`) |
| `B3` | `COVERED_BY_STEP_A` | `CHECK-T12-06` — tháng lịch từ `asOfDate` (`SC-08`) |
| `B4` | `COVERED_BY_STEP_A` | `CHECK-T12-06` — `businessDate` người dùng nhập (`SC-07`) |
| `B5` | `COVERED_BY_STEP_A` | `CHECK-T12-05` — mọi event sửa/xoá được (`SC-05`, `SC-06`) |
| `B6` | `COVERED_BY_STEP_A` | `CHECK-T12-01`, `-03` — `openingPosition` (`SC-01`) |
| `B7` | `COVERED_BY_STEP_A` | `CHECK-T12-06` — đúng một chỗ hỏi giờ, `Asia/Ho_Chi_Minh` (`SC-08`) |
| `B8` | `COVERED_BY_STEP_A` | `CHECK-T12-10`, `-11` — snapshot trước `import`/`wipe`/`migration` (`INV-14`) |
| `B9` | `COVERED_BY_STEP_A` | `CHECK-T12-07` — VND integer (`INV-5`) |
| `B10` | `OUTSIDE_STEP_A` / `RETRIGGER_LATER` | rolling window của `engine.js` nằm ngoài đường tiền L-1 (`O-11`); re-trigger giữ ở `H-43` — bật tab Research |

Sau khi `T-12` `DONE`, `H-41` được cập nhật (không xoá): `B1`–`B9` đóng theo bảng trên, `B10`
ở lại backlog với re-trigger nguyên vẹn.

## Subtasks (chỉ dẫn thi hành, không phải hợp đồng)

- [ ] 12.1 Schema `coindca.ledger/2` + validator schema (§5)
- [ ] 12.2 `derive()` + pool USDT WAC + holdings + cờ (§6, §7, §8, §9)
- [ ] 12.3 Lớp kế hoạch tháng: `plannedPerSlot`, carry, `planInvested`, `next*` (§10.5, §11)
- [ ] 12.4 Reserve như earmark dẫn xuất (§12)
- [ ] 12.5 Sửa / xoá cứng / nhập muộn + snapshot (§15)
- [ ] 12.6 Migration `ethdca.tracker/1` → `coindca.ledger/2` + đối chiếu §17.3 + hai tầng §17.4
- [ ] 12.7 Persistence: serialize/khôi phục/version trong `ethdca/state` (§9.4, `INV-12`, `INV-14`)
- [ ] 12.8 Adapter tối thiểu để app dùng được sổ mới (reachability `P-1`…`P-6`)
- [ ] 12.9 Golden test `SC-01`…`SC-12`
- [ ] 12.10 Test nhắm đích `INV-1`…`INV-15`
- [ ] 12.11 Khai file production mới vào `PRODUCTION_PATHS.md`; cập nhật `PROJECT/` state
- [ ] 12.12 Phiên E2 độc lập (không do người thi hành tự chạy)

## Changed Files Registry

Created:
- (điền khi thi hành)

Modified:
- (điền khi thi hành)

Deleted:
- (điền khi thi hành)

Migration Impact:
- Đổi schema durable `ethdca.tracker/1` → `coindca.ledger/2` bên trong document `ethdca/state`.
  Dữ liệu legacy không bị xoá; snapshot bắt buộc trước khi ghi; hai tầng kết quả §17.4.

## Notes

- Nguồn yêu cầu canonical duy nhất: `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md`.
  File này **không** lặp lại thân spec; nó neo vào từng mục. Khi hai bên lệch, spec thắng và
  phải mở khối `CONFLICT DETECTED`.
- `T-12` **không** đòi `T-06`, `Gate1/2/3`, failure signal chiến lược, backtest bootstrap hay bộ
  máy verdict — governance tương xứng theo `DEC-041` J.
- Không dữ liệu tài chính thật nào của Owner được commit. Fixture là **tổng hợp**.
  `private/owner_local_acceptance.json` (§22.1) thuộc bước D, phải nằm trong `.gitignore`.
- Ba tu chỉnh của `S033` (persistence architecture, golden baseline, repair pre-authorization)
  được ghi Owner Decision đầy đủ tại `DEC-043` (`PROJECT/PROJECT_DECISIONS.md`). File này chỉ
  neo vào từng mục của `DEC-043`, không lặp lại toàn văn quyết định.
