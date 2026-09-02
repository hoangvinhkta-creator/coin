# T-09A — Sửa lỗi kế toán trong app web (V-01, V-02)

## Metadata
Status:
IMPLEMENTED

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION

Completion Gate Freeze:
KHÔNG FROZEN — xem mục "Ghi chú thẩm quyền" bên dưới. T-04/S002 chỉ đóng băng gate cho 15 work
package; T-09A không nằm trong 15 gói đó, nên chưa từng có gate nào được đóng băng cho task này.
Gate dưới đây được finalize tại phiên thực thi theo `TASK_COMPLETION_GATE_STANDARD.md`
mục "Gate Creation Timing". KHÔNG có gate cũ nào bị sửa, xoá hay làm yếu.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 1
X: 2
U: 1
V: 3
H: 2
C: 2
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
high

Model Routing Score:
2.35

Effort Routing Score:
2.25

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
max

Difficulty:
3/4

Risk:
3/4

Blast Radius:
2/4

Effective Risk:
HIGH — `Effective Risk = MAX(Local Risk, Blast Radius)` (`RISK_MODEL.md`). Blast Radius chấm theo
đường dữ liệu, không theo tên module: cả V-01 lẫn V-02 rơi thẳng vào "wrong money … settlement"
của `RISK_MODEL.md` § Blast Radius — HIGH. Golden Reduction KHÔNG dùng được (chưa có Golden
baseline canonical — `HARDENING_BACKLOG.md` H-10). Hệ quả: **bắt buộc batch review cuối phiên**
(`RISK_MODEL.md` § HIGH Does Not Mean STOP), và HIGH đặt độ sâu review chứ không phải hard-stop.

Project Profile:
PRODUCT

## Ghi chú thẩm quyền (đọc trước khi đọc phần còn lại)

T-09A **đã được đăng ký từ trước** trong vùng registry chính thức của
`PROJECT/PROJECT_PROGRESS.md` (bảng Overall Roadmap, trạng thái `READY`) — đó là hình thức
đăng ký thứ nhất theo `CAPABILITY_MODEL.md` §II.5. File này là hình thức thứ hai (Task Spec)
cho **cùng một ID đã tồn tại**.

    Task ID mới được tạo bởi file này = 0

`GOVERNANCE_V4.md` §II.5 cho một task bốn artifact mặc định: SPEC/TASK, PROGRESS/STATE, REVIEW,
DECISIONS dùng chung. File này là artifact SPEC/TASK — nằm trong hạn mức, không cần phê duyệt
artifact thứ năm.

Capability: `CAP-WEBAPP` · Lineage root: `WP-C1` (`PROJECT/CAPABILITY_REGISTRY.md` §2).
Budget đọc từ `PROJECT/REVIEW_BUDGET_LEDGER.md` §2, KHÔNG khai lại tại đây.

## Objective

Vá đúng nguyên nhân làm sai kế toán vốn trong app web — hai lỗi mà `WP-C1` đã XÁC NHẬN bằng ca
chạy thật (E1) — trước khi app được dùng để ghi tiền thật hằng ngày. Không mở rộng thành thiết
kế lại engine kế toán.

## Hai lỗi phải vá (thẩm quyền: WP-C1, E1)

| ID | Lỗi | Vị trí (trước vá) | Kết luận WP-C1 |
|---|---|---|---|
| V-01 | Release vốn trả **nhầm pool tháng**: `releaseLadder()` dùng `currentMonth()` (key tháng lớn nhất) thay vì tháng gốc của ladder | `webapp/app_logic.js:302-322`, `124-127` | XÁC NHẬN (E1) — `CHECK-C1-03`, `CHECK-C1-06` |
| V-02 | Mức unlock **không giới hạn** số vốn được reserve: `reserveFor()` chỉ so với available | `webapp/app_logic.js:289-297`, `324-335` | XÁC NHẬN (E1) — `CHECK-C1-04` |

V-03 đã **BÁC BỎ** tại WP-C1 và nằm ở `HARDENING_BACKLOG.md` **H-18**. Gói này **không** sửa
V-03 — xem mục "H-18" bên dưới.

## Scope

- `webapp/app_logic.js` — lớp kế toán: quy thuộc tháng của ladder, giới hạn reserve theo unlock
- Ca kiểm thử bất biến kế toán mới trong `webapp/`
- Bảo trì các test WP-C1 hiện có khi tiền đề của chúng không còn hợp lệ sau bản vá

## Out of Scope

- `webapp/engine.js` — 0 dòng đổi (giữ nguyên parity với Python)
- `src/eth_dca_os/` — không đụng
- Chế độ HWM/NO_HWM/DECAY_HWM của Smart unlock (Strategy §6)
- Hysteresis Opportunity (Strategy §5) và daily limit 20%/ngày (Strategy §11)
- Lớp lưu trữ bền (T-09B), execution state machine (WP-C2), partial fill sản phẩm (WP-C3),
  mở rộng parity JS/Python (WP-C4), dashboard, cảnh báo (T-08/T-10)
- Security / multi-user / hostile tampering — `DEC-011` điểm 10

## Expected Touch Area

Allowed:
- `webapp/app_logic.js`
- `webapp/test_t09a_accounting.js`, `webapp/test_helpers.js` (mới)
- `webapp/test_app.js`, `webapp/test_zone.js`, `webapp/test_v01_v02_v03.js`,
  `webapp/test_multi_month_invariant.js` — **chỉ thêm bước tiền đề**, không nới assertion
- `webapp/package.json` — đăng ký test mới vào `npm test`

Do not touch without Scope Expansion:
- `webapp/engine.js`, `webapp/app_shell.html`, `webapp/build_app.js`
- `src/eth_dca_os/**`, `pyproject.toml`, `pyproject.lock`
- `docs/spec/**`

## Dependencies
- WP-C1 (DONE) — nguồn thẩm quyền cho V-01/V-02

## Blocks
- Việc dùng app với tiền thật (escalation của RSK-003 / WP-C1)

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope và Out-of-scope được định nghĩa
- [x] Dependency (WP-C1) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — Strategy §4, §6, §8, §12; `capital.py::smart_reservable`
- [x] Data impact được biết — state trong localStorage của chủ dự án; bản vá KHÔNG migrate,
      KHÔNG ghi đè state; ladder cũ được xử lý bằng suy luận CÓ BÁO HIỆN (xem CHECK-T09A-07)
- [x] Security impact được biết — không có dữ liệu bên thứ ba, không commit dữ liệu thật
- [x] Difficulty / Risk / Blast Radius được chấm; Effective Risk = HIGH
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize trước khi thực thi

## Completion Gate

Effective Risk = HIGH → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng được, và bắt buộc
batch review cuối phiên. Mọi check dưới đây chạy qua **đường sản phẩm thật**
(UI → `app_logic` → `engine` → state đã lưu) trên `app_final.html` đã build, không gọi trực
tiếp hàm engine.

### Correctness — bất biến kế toán

#### CHECK-T09A-01 — Pool ownership isolation (bất biến A)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: release/deploy của một ladder không được đụng pool của tháng khác.

`webapp/test_t09a_accounting.js` CA 1 — ba tháng (2026-05 A, 2026-06 B, 2026-07 C), ladder LA
thuộc tháng A (KHÔNG phải key lớn nhất), LB thuộc tháng B còn ACTIVE, huỷ LA khi
`currentMonth()` = tháng C:

```
trước huỷ LA — A: {"a":0,"r":3000000,"d":0} B: {"a":0,"r":3000000,"d":0} C: {"a":3000000,"r":0,"d":0}
sau huỷ LA  — A: {"a":3000000,"r":0,"d":0} B: {"a":0,"r":3000000,"d":0} C: {"a":3000000,"r":0,"d":0}
```

- reserved tháng A về 0 (không kẹt vốn), available tháng A nhận lại đúng số;
- pool tháng B và tháng C **không đổi một đồng nào**.

CA 2 kiểm chiều ngược lại cho deploy: fill zone của ladder tháng A trong khi `currentMonth()`
= tháng B → DEPLOYED tăng ở tháng A, pool tháng B không đổi.

Executed By:
Claude (T-09A, nhánh `claude/t09a-accounting-repair-v4ewhq`)

Timestamp:
2026-09-02

#### CHECK-T09A-02 — Active backing preservation (bất biến B)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: vốn đang backing một ladder ACTIVE không được trở thành available do release của
owner khác. `webapp/test_t09a_accounting.js` — hàm `backingOk()` khẳng định, với từng tháng,
`smart.r` của tháng ≥ tổng cam kết chưa fill của các ladder ACTIVE **thuộc chính tháng đó**.
Sau khi huỷ LA: LB vẫn `ACTIVE` và backing của LB nguyên vẹn (CA 1); kiểm lại ở CA 4 cho kịch
bản một tháng.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-03 — Release upper bound (bất biến C)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: số được release không vượt reserve hợp lệ của đúng owner, và bút toán ghi đúng số
thực sự dịch chuyển.

- CA 1: đúng **một** bút toán `RELEASE`, mang `month: "2026-05"` (tháng sở hữu), `vnd` bằng
  đúng số đã chuyển, không có trường `shortfall`;
- CA 1: huỷ rồi nhập thêm ngày giá → ladder đã `CANCELLED` **không** release lần thứ hai;
- CA 2: sau khi fill một phần rồi huỷ, chỉ phần **chưa fill** được trả về; phần đã deploy
  không bị trả lại; `smart.r` tháng sở hữu về 0;
- CA 3: `reserved` không vượt phần đã unlock sau hai lần thử reserve liên tiếp.

Trước bản vá, `releaseLadder()` ghi `vnd: open` (số cam kết) chứ không phải số thực chuyển —
nay ghi số thực chuyển và ghi `shortfall` khi hai số lệch nhau, để sổ không nhất quán thì
nhìn thấy được.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-04 — Conservation (bất biến D)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: sau mọi transition kế toán, tổng vốn không tự sinh/mất. Hàm `conservation()` khẳng
định `TOTAL(pool tháng) = a + r + d` giữ nguyên qua toàn bộ chuỗi (reserve → fill toàn phần →
fill một phần → contribution tháng mới → invalidation/cancel → release), và không pool nào âm,
ở CẢ BỐN ca. `webapp/test_multi_month_invariant.js` (WP-C1) khẳng định lại cùng bất biến trên
kịch bản gốc của WP-C1.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-05 — Multi-month behavior (bất biến E)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: trình tự nhiều tháng không làm ownership nhập nhằng. CA 1 dựng **ba** tháng và đặt
ladder ở tháng không phải key lớn nhất — đúng yêu cầu mà `CHECK-C1-03` của WP-C1 đặt ra. CA 2
kiểm deploy xuyên tháng. Ladder mới mang trường `month` tường minh, khẳng định bằng assertion
(`LA.month === "2026-05"`, `LB.month === "2026-06"`).

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-06 — Giới hạn reserve theo unlock, đúng biên trên (V-02)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `reserve ≤ unlocked(tháng) − (đã reserve + đã deploy trong tháng)`, kẹp trên bởi
available — cùng công thức với `src/eth_dca_os/capital.py::smart_reservable`. Hạn mức được so
với **oracle tính lại từ chính `engine.js`** (`test_helpers.readUnlock`), không hard-code số.

`webapp/test_t09a_accounting.js` CA 3:

```
unlock ban đầu: 0.000% (OSCORE 30.742)
ldMsg (cap = 100% available, unlock 0%):
  "Vượt phần đã unlock (0.0%): tối đa 0 ₫ được reserve lúc này (Strategy §12)."
  -> 0 ladder được tạo; pool KHÔNG bị đụng (fail closed, không side effect)
unlock sau 3 ngày giảm: 16.9748%
cap = 101% hạn mức  -> TỪ CHỐI
cap = 99,9% hạn mức -> CHẤP NHẬN, reserved 508735,40 ≤ hạn mức 509244,64
reserve lần hai vượt phần còn lại -> TỪ CHỐI (hạn mức trừ đi phần đã reserve/deploy)
```

Trạng thái `0 < unlock < 1` được dựng qua **đúng UI "Nhập số liệu"** (`#pxAdd`), không thao
túng state.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

### Backward Compatibility / Data

#### CHECK-T09A-07 — State cũ không bị hỏng, và suy luận phải nhìn thấy được
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: ladder tạo TRƯỚC bản vá không mang trường `month`. Bản vá KHÔNG migrate và KHÔNG ghi
đè state đã lưu. `ladderMonth()` suy luận tháng sở hữu từ `L.created` nếu tháng đó thật sự có
sổ, ngược lại rơi về `currentMonth()`; **mọi ladder rơi vào nhánh suy luận đều được liệt kê
tên trên một banner cảnh báo** ("THÁNG SỞ HỮU SUY LUẬN"), đúng `DEC-011` điểm 9 (sai tiền phải
fail visibly). `webapp/test_app.js` (bước 9) khẳng định state sống sót qua reload; toàn bộ 4
test WP-C1 chạy trên state do chính chúng dựng và PASS.

Giới hạn đã ghi rõ, không giấu: suy luận có thể SAI nếu tháng tạo (theo đồng hồ) khác tháng có
key lớn nhất tại thời điểm tạo. Không có dữ liệu nào trong state cũ cho phép khôi phục chính
xác — đây là lý do chọn "suy luận + báo hiện" thay vì "suy luận im lặng" hoặc "migrate mù".

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

### Regression

#### CHECK-T09A-08 — Bộ test webapp đầy đủ PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`npm --prefix webapp test` — 5 test (`test_app.js`, `test_zone.js`, `test_v01_v02_v03.js`,
`test_multi_month_invariant.js`, `test_t09a_accounting.js`), exit code 0, không page error.

Bốn test WP-C1 hiện có được **bảo trì**, không nới lỏng: kịch bản gốc của chúng reserve 100%
Smart available trong khi Smart unlock = 0% — đúng hành vi mà V-02 tố cáo là SAI. Sau bản vá
thao tác đó bị từ chối, nên mỗi test được thêm **một** bước tiền đề: nhập chuỗi ngày giảm giá
qua đúng UI để mở unlock. Không assertion nào bị xoá hay hạ ngưỡng; mọi bước và phép kiểm phía
sau giữ nguyên.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-09 — Không regression phía Python
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`webapp/engine.js` và `src/eth_dca_os/**` **0 dòng đổi** (`git diff --stat`). Bản vá làm JS
**tiến gần** bản Python chứ không rời xa: `smartReservable()` dùng đúng công thức của
`capital.py::smart_reservable`. Chạy đầy đủ bộ test Python để xác nhận đường Python/official
không bị ảnh hưởng:

```
$ pip install -q -e ".[dev]" && python3 -m pytest -q
........................................................................ [ 25%]
........................................................................ [ 50%]
........................................................................ [ 75%]
......................................................................   [100%]
286 passed — exit code 0
```

Phiên bản công cụ được ghim vào bằng chứng: Python 3.11.15 · node v22.22.2 · npm 10.9.7 ·
playwright 1.56.1 · Chromium `/opt/pw-browsers/chromium`.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-10 — Hành vi hợp lệ cũ không đổi (bất biến F)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
CA 4 của `webapp/test_t09a_accounting.js` (kịch bản sạch MỘT tháng: reserve trong hạn mức →
fill toàn phần zone 0 → fill một phần zone 1 → huỷ) **PASS trên CẢ hai cây**: cây chưa vá và
cây đã vá. Đó là bằng chứng bản vá không đổi hành vi ở vùng vốn đã đúng.

Đo trên cây CHƯA vá (`git checkout -- webapp/app_logic.js`, build lại, chạy cùng file test):

```
assertion đã chạy: 68 | FAIL: 17     <- 17 FAIL đều thuộc CA 1 / CA 2 / CA 3
CA 4: 0 FAIL
```

Đo trên cây ĐÃ vá:

```
assertion đã chạy: 68 | FAIL: 0
```

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

### Scope / Governance

#### CHECK-T09A-11 — Không tạo task ID mới, không đụng trạng thái đã chốt
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Đo trên **registry**, không grep cả repo (`CAPABILITY_MODEL.md` §II.9).

`governance/scripts/governance/task_registry_snapshot.sh` BEFORE/AFTER cho `28 → 27`. Con số
đó **SAI** và không phải do phiên này: script bỏ sót hai trạng thái `IMPLEMENTED` và
`VERIFYING` của chính lifecycle canonical — xem `HARDENING_BACKLOG.md` **H-22** /
`F-T09A-05`. `T-03` (`VERIFYING`) đã vắng mặt trong ảnh chụp TRƯỚC khi T-09A chạm vào bất cứ
thứ gì.

Đo lại bằng tay với danh sách trạng thái ĐẦY ĐỦ (`git show 814d185:PROJECT/PROJECT_PROGRESS.md`
so với working tree):

```
BEFORE = 29 task ID   AFTER = 29 task ID   diff = RỖNG (tập ID trùng khít)

new_registered_task_ids                 = 0
proposals_created                       = 0
owner_assignment_required_entries_added = 0
```

Số file task tăng 20 → 21 vì file này là Task Spec cho **T-09A đã đăng ký sẵn** (hình thức 1
của `CAPABILITY_MODEL.md` §II.5), không phải ID mới.

WP-A4 giữ `DONE`; `F-S009-01` giữ `CLOSED`; `CAP-DATA` giữ `allowed 2 / used 1 / remaining 1`;
`F-S010-03` giữ `OUT_OF_SCOPE → WP-C4`. Bản vá không chạm `src/eth_dca_os/**` nên không chạm
ngữ nghĩa DATA.

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

#### CHECK-T09A-12 — Batch review bắt buộc (Effective Risk HIGH)
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`docs/reviews/T-09A-batch-review.md` — một lượt duy nhất trên TOÀN BỘ diff tích luỹ của T-09A,
trả tất cả finding BLOCKING trong một lần theo `REVIEW_PROTOCOL.md`. Kết quả: **0 CONFIRMED
BLOCKING**, 0 PROVISIONAL, **4 HARDENING** (`H-19`, `H-20`, `H-21`, `H-22` — mỗi mục có
`RE_TRIGGER_CONDITION`), **1 OUT_OF_SCOPE** đã có owner (`F-T09A-03` → `WP-C4`).
VERDICT = PASS → `ELIGIBLE_FOR_FREEZE` (advisory; phiên này KHÔNG ghi `FROZEN`/`DONE`).

Executed By:
Claude (T-09A)

Timestamp:
2026-09-02

## DEFERRED_BY_MINIMAL_FIX

Khai báo bắt buộc theo `CAPABILITY_MODEL.md` § Minimal Fix.

    Owner:      T-09A (capability CAP-WEBAPP, lineage root WP-C1)

    Implemented:
      - quy thuộc tháng sở hữu cho ladder (`L.month`), dùng ở release VÀ deploy;
      - giới hạn reserve theo unlock, đúng công thức của `capital.py::smart_reservable`;
      - bút toán RELEASE ghi số thực chuyển + `shortfall` khi lệch;
      - banner báo hiện ladder có tháng sở hữu SUY LUẬN.

    Intentionally deferred:
      1. Chế độ Smart unlock HWM / NO_HWM / DECAY_HWM (Strategy §6). App dùng SMART_UNLOCK
         hiện hành, tức luôn ≤ peak HWM → **chặt hơn** baseline, không bao giờ cho reserve
         vốn chưa unlock. Sai lệch có thể có: app từ chối một reserve mà baseline HWM cho
         phép (fail closed, không sai tiền).
      2. Hysteresis Opportunity ACTIVATE/SUSPEND (Strategy §5) và daily limit 20%/ngày
         (Strategy §11) — app chỉ áp phần unlock của `opportunity_reservable`.
      3. Giới hạn unlock cho đường mua TRỰC TIẾP không gắn zone (`addBuy` nhánh `else`).
         Đường đó GHI NHẬN một giao dịch đã xảy ra ngoài đời; chặn nó sẽ làm mất bản ghi
         giao dịch thật (`DEC-011` tiêu chí C) — tệ hơn hẳn hệ quả nó gây ra.
      4. Migrate state cũ để gắn `month` cho ladder đã tồn tại — xem CHECK-T09A-07.
      5. Kiểm tra `data_quality` tường minh trong `createLadder()` — đó là H-18, chủ dự án
         không yêu cầu, và điều kiện re-trigger của H-18 không xảy ra.

    Reason:
      Mỗi mục trên trả lời NO cho câu hỏi kiểm soát phạm vi: "không làm phần này thì chủ dự
      án có bị ngăn dùng ETH DCA OS hằng ngày với tiền thật một cách ĐÚNG không?" Không mục
      nào làm sai tiền theo hướng nới lỏng; mục 1 và 2 chỉ chặt hơn spec (fail closed).

    Re-trigger:
      - (1) khi chủ dự án cần Smart unlock giữ peak trong tháng, hoặc khi một lần từ chối
        reserve fail-closed thực sự cản trở thao tác hằng ngày;
      - (2) khi app bắt đầu tạo Opportunity ladder thường xuyên, hoặc WP-C4 mở rộng parity
        sang đường Opportunity;
      - (3) khi đường mua trực tiếp được dùng để ĐẶT LỆNH chứ không chỉ GHI NHẬN;
      - (4) khi có state thật mang ladder chưa gắn `month` và banner suy luận bật lên;
      - (5) theo đúng `RE_TRIGGER_CONDITION` của H-18.

    Evidence:
      `webapp/test_t09a_accounting.js` (68 assertion, 0 FAIL trên cây đã vá; 17 FAIL trên cây
      chưa vá), `docs/reviews/T-09A-batch-review.md`.

## H-18 (V-03) — giữ nguyên DEFERRED

`HARDENING_BACKLOG.md` H-18 có ba điều kiện re-trigger. Kiểm từng điều kiện trên diff của
T-09A:

1. `smartSpacing` / `oppSpacing` / `adr30` bị đổi → **KHÔNG**. `webapp/engine.js` 0 dòng đổi.
2. `factorScores` / `SUB_NAMES` bị đổi → **KHÔNG**. Cùng lý do.
3. Chủ dự án muốn thêm kiểm tra `data_quality` tường minh → **KHÔNG** được yêu cầu, và điều
   kiện này tự nó ghi "(không bắt buộc — hành vi hiện tại đã đúng yêu cầu)".

Kết luận: H-18 **giữ nguyên DEFERRED**, không sửa. `webapp/test_v01_v02_v03.js::testV03` chạy
lại trên cây đã vá vẫn cho **BÁC BỎ** với đúng message cũ ("Chưa đủ lịch sử để tính ADR30.") —
hành vi V-03 không đổi.

## Exit Criteria

- [x] V-01 không còn tái hiện trên đường sản phẩm thật
- [x] V-02 không còn tái hiện trên đường sản phẩm thật
- [x] Sáu bất biến A–F có test chạy thật, FAIL trước vá và PASS sau vá
- [x] Toàn bộ bộ test webapp PASS
- [x] Không regression phía Python
- [x] Batch review bắt buộc đã chạy, 0 CONFIRMED BLOCKING
- [x] Mọi HARDENING mới có `RE_TRIGGER_CONDITION`
- [x] Task ID mới = 0
- [ ] Chủ dự án chuyển T-09A sang `DONE` (`STATE_AUTHORITY.md`: `DONE` do chủ dự án viết)

## Escalation Triggers

- Phát hiện một đường làm SAI TIỀN nằm ngoài V-01/V-02 mà không vá được trong phạm vi này →
  ghi finding, phân loại theo `REVIEW_PROTOCOL.md`, **không** tự mở task.
- Bản vá đòi hỏi đổi ngữ nghĩa kế toán ở `src/eth_dca_os/` → `ARCHITECTURE_CHANGE_REQUIRED`.
- Bản vá đòi hỏi migrate/ghi đè state đã lưu của chủ dự án → `DATA_INTEGRITY_RISK`.
- Chạm hạn mức repair của `CAP-WEBAPP` → `CHANGE_BUDGET_EXCEEDED`, dừng đúng V4.3.
