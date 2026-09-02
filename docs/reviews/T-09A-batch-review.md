# T-09A — BATCH REVIEW (bắt buộc, Effective Risk = HIGH)

Nguồn thẩm quyền:
`governance/v4/CORE/REVIEW_PROTOCOL.md`, `governance/v4/CORE/PRODUCTION_PATH_RULE.md`,
`governance/v4/CORE/RISK_MODEL.md` § "HIGH Does Not Mean STOP",
`PROJECT/PROJECT_DECISIONS.md` `DEC-011` (tiêu chí `BLOCKING V1` A–F).

Ngày:
2026-09-02

Phạm vi review:
TOÀN BỘ diff tích luỹ của T-09A trong một lượt duy nhất. Reviewer trả **tất cả** finding
BLOCKING nhận diện được trong một lần — nối tiếp finding qua nhiều vòng là process failure
(`GOVERNANCE_V4.md` §II.2).

## 0. Sáu bước trước khi review (REVIEW_PROTOCOL.md § Before The Review Starts)

| # | Bước | Giá trị |
|---|---|---|
| 1 | SHA đầy đủ + remote SHA | BASE `814d185c925d7c630f9d9c5443742f4b580e3444` (= `origin/main`), HEAD `d125fe5a3da82aac84b09f780ced2babc3b15220` |
| 2 | Branch authority check | `branch_authority_check.sh` — xem `PROJECT/PROJECT_PROGRESS.md` mục phiên T-09A |
| 3 | Phiên bản công cụ được ghim vào bằng chứng | node v22.22.2 · npm 10.9.7 · playwright 1.56.1 (`webapp/package.json`) · Chromium `/opt/pw-browsers/chromium` · Python 3.11.15 |
| 4 | Tracked worktree | CLEAN trước và sau (`git status --porcelain`) |
| 5 | Task Spec / Completion Gate / production paths / risk register / budget ledger | `docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`; `PROJECT/PRODUCTION_PATHS.md`; `PROJECT/PROJECT_PROGRESS.md` § Active Risks (RSK-003); `PROJECT/REVIEW_BUDGET_LEDGER.md` §2 (`CAP-WEBAPP`) |
| 6 | Cumulative repair diff | `814d185..d125fe5` — đây là **lượt implementation ban đầu** của T-09A, KHÔNG phải repair cycle (cùng quy ước đã dùng cho `CAP-PROV` §1 và `CAP-DATA` §2.1 của ledger) |

## 1. Diff được review

Đo bằng lệnh, không cộng tay.

Lệnh chuẩn ghi ở `PRODUCTION_PATHS.md` §1 (glob theo thư mục):

    git diff --shortstat 814d185..d125fe5 -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 8 files changed, 590 insertions(+), 17 deletions(-)

Đo theo **khai báo** production path (`PRODUCTION_PATHS.md` §1 bảng + §2 loại trừ test):

    git diff --shortstat 814d185..d125fe5 -- \
        webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js \
        src/eth_dca_os pyproject.toml pyproject.lock
      -> 1 file changed, 88 insertions(+), 16 deletions(-)

Hai con số lệch nhau vì lệnh glob nuốt cả file test. Xem `F-T09A-04` bên dưới. Con số có
thẩm quyền cho phân loại finding và cho Delivery Change Budget là con số **theo khai báo**:
`webapp/app_logic.js`, **+88 / −16, một file duy nhất**.

`webapp/engine.js` = **0 dòng đổi**. `src/eth_dca_os/**` = **0 dòng đổi**.
`pyproject.toml` / `pyproject.lock` = **0 dòng đổi**.

## 2. Bằng chứng đã kiểm chứng lại (không tin lời kể của implementer)

| Hạng mục | Kết quả |
|---|---|
| Reproduction V-01 trước vá | `test_v01_v02_v03.js::testV01` → **XÁC NHẬN** (tháng B bị cộng 1.000.000 và bị rút 1.000.000 khỏi reserve đang backing LB; tháng A kẹt) |
| Reproduction V-02 trước vá | `test_v01_v02_v03.js::testV02` → **XÁC NHẬN** (reserve 3.000.000 = 100% available khi Smart unlock = 0,0%) |
| Bất biến A–F trước vá | `test_t09a_accounting.js` trên cây chưa vá → **17 assertion FAIL / 68** |
| Bất biến A–F sau vá | **0 FAIL / 68** |
| Reproduction V-01 sau vá | **BÁC BỎ** — "vốn release quay đúng về tháng A; tháng B/LB không bị ảnh hưởng" |
| Reproduction V-02 sau vá | **BÁC BỎ** — "reserve bị chặn hoặc giới hạn đúng theo mức unlock đo được" |
| V-03 sau vá | **BÁC BỎ**, message không đổi ("Chưa đủ lịch sử để tính ADR30.") — hành vi V-03 không đổi |
| Bộ test webapp đầy đủ | `npm --prefix webapp test` → 5/5 test, exit 0, không page error |

CA 4 (kịch bản sạch MỘT tháng) PASS trên **cả hai** cây — đây là phép kiểm bất biến F, và là
bằng chứng bản vá không đổi hành vi ở vùng vốn đã đúng.

## 3. Phép thử BLOCKING, phát biểu theo chiều phủ định

`REVIEW_PROTOCOL.md`: BLOCKING cần ĐỒNG THỜI (a) đường production hiện hành, (b) hậu quả
nghiệp vụ nằm trong Completion Gate hoặc risk register, (c) bằng chứng tái lập được.
`DEC-011` bổ sung trục `BLOCKING V1` A–F.

    CONFIRMED BLOCKING = 0

Không finding nào của lượt review này thoả đồng thời cả ba điều kiện.

## 4. Finding

### F-T09A-01 — `monthKey()` dùng giờ địa phương, không dùng `accounting_timezone` đã khai
Phân loại: **HARDENING** · Capability: `CAP-WEBAPP` · Owner: `T-09A` (ghi nhận), backlog

`monthKey()` (`webapp/app_logic.js:120-123`) tính tháng bằng `getFullYear()/getMonth()` — giờ
địa phương của máy — trong khi `config.accounting_timezone = "Asia/Ho_Chi_Minh"` được khai
trong seed và không được dùng ở bất kỳ đâu trong app. Bản vá T-09A **mở rộng** vùng ảnh hưởng
của hàm này: nhánh suy luận của `ladderMonth()` gọi `monthKey(new Date(L.created))`.

Vì sao KHÔNG BLOCKING (phải thoả cả ba, ở đây thiếu (a) và (c)):
- ladder tạo TỪ bản vá trở đi luôn mang `L.month` tường minh → nhánh suy luận **không chạy**;
- nhánh suy luận chỉ chạm ladder legacy, và mọi ladder legacy đều được liệt kê tên trên banner
  cảnh báo → fail visibly, đúng `DEC-011` điểm 9;
- `DEC-011` OD-1 xác định V1 chạy trên MỘT máy của chủ dự án; không dựng được counterexample
  từ nguồn canonical nào của `PRODUCTION_PATHS.md` §3 cho máy thứ hai.

Cùng lớp với `H-02` (tzdata quyết định biên accounting month) đã có trong backlog.

    RE_TRIGGER_CONDITION:
    - app được mở trên máy hoặc múi giờ khác Asia/Ho_Chi_Minh; HOẶC
    - banner "THÁNG SỞ HỮU SUY LUẬN" bật lên trên state thật của chủ dự án; HOẶC
    - WP-C2 / T-09B chốt lại ngữ nghĩa biên accounting month cho app.

### F-T09A-02 — đường mua TRỰC TIẾP (không gắn zone) không bị giới hạn theo unlock
Phân loại: **HARDENING** · Capability: `CAP-WEBAPP` · Owner: `T-09A` (ghi nhận), backlog

`addBuy()` nhánh `else if (vndCost > 0 && pool)` (`webapp/app_logic.js:265-268`) trừ thẳng
`pool.a → pool.d` mà không tham chiếu unlock. Sau bản vá V-02, đây là đường duy nhất còn lại
để vốn Smart chưa unlock chuyển sang DEPLOYED.

Vì sao KHÔNG BLOCKING — và vì sao chặn nó sẽ là một lỗi TỆ HƠN: đường này **ghi nhận một giao
dịch đã xảy ra ngoài đời** (người dùng đã mua ETH thật rồi mới vào app ghi sổ). Chặn nó theo
unlock sẽ làm **mất bản ghi giao dịch thật** — chạm thẳng tiêu chí **C** của `DEC-011` ("mất
hoặc làm hỏng lịch sử giao dịch thực tế"), nặng hơn hẳn hệ quả nó gây ra. Strategy §12 nói về
**reserve**, không về ghi nhận.

    RE_TRIGGER_CONDITION:
    - `WP-C2` biến app từ GHI NHẬN sang ĐẶT LỆNH (execution state machine); HOẶC
    - chủ dự án yêu cầu đường mua trực tiếp cũng phải bị chặn theo unlock, kèm một lối thoát
      tường minh để vẫn ghi được giao dịch đã xảy ra (ví dụ nguồn "Thủ công").

### F-T09A-03 — app chỉ áp SMART_UNLOCK hiện hành; thiếu HWM, hysteresis, daily limit
Phân loại: **OUT_OF_SCOPE → `CAP-WEBAPP` / `WP-C4`** (không phải backlog hardening)

Bản Python có `SmartUnlockState` (HWM/NO_HWM/DECAY_HWM, Strategy §6),
`opportunity_reservable` với hysteresis (§5) và daily limit 20%/ngày (§11). Bản JS sau T-09A
mới áp **phần unlock** của công thức. Đây là một mặt của lệch parity JS ↔ Python — đúng chủ đề
mà `CAPABILITY_REGISTRY.md` §3 đã giao cho `WP-C4` ("Đối chiếu parity JS/Python của cùng công
thức"), cùng đường với `F-S010-03`, dưới rủi ro đã đăng ký `RSK-002`.

Lệch theo chiều **CHẶT HƠN**: `SMART_UNLOCK` hiện hành luôn ≤ peak HWM, nên app không bao giờ
cho reserve vốn chưa unlock. Hệ quả xấu nhất là một lần từ chối reserve mà baseline HWM cho
phép — fail closed, không sai tiền. Đã khai ở `DEFERRED_BY_MINIMAL_FIX` mục 1–2 của Task Spec.

`OUT_OF_SCOPE` **không** có nghĩa là task mới. Không ID nào được đặt.

### F-T09A-04 — `PRODUCTION_PATHS.md` tự mâu thuẫn: lệnh đo §1 nuốt file test bị §2 loại trừ
Phân loại: **HARDENING** (tầng governance) · Capability: `CAP-GOVTOOL` · Owner: chưa có

`PRODUCTION_PATHS.md` §2 loại trừ tường minh `webapp/test_app.js`, `webapp/test_zone.js` khỏi
production path, nhưng lệnh đo budget chuẩn ở §1 dùng glob `-- ... webapp ...` nên đếm cả file
test. Ở T-09A khoảng lệch là **590 vs 88 insertion** — bảy lần.

`GOVERNANCE_V4.md` §II.6 yêu cầu: khi trong CÙNG một artifact có mâu thuẫn, nguồn cao hơn
thắng **và** phải nêu finding reconciliation. Bảng khai báo (§1 + §2) là nguồn cao hơn lệnh
tiện dụng, nên phiên này báo cáo con số theo khai báo và ghi rõ cả hai. Đây chính là `H-12`
("`PRODUCTION_PATHS.md` khai theo FILE chứ chưa theo CHUỖI dữ liệu") biểu hiện ở dạng đo được.

Không BLOCKING: không có đường production nào cho ra kết quả sai; hậu quả là phép đo budget
bị thổi phồng, tức chặt hơn chứ không lỏng hơn.

    RE_TRIGGER_CONDITION:
    - một phiên bất kỳ dùng con số glob làm căn cứ tuyên bố CHANGE_BUDGET_EXCEEDED; HOẶC
    - `H-12` được chủ dự án mở để khai lại production path theo CHUỖI dữ liệu; HOẶC
    - `webapp/` có thêm file production mới khiến hai phép đo lệch tiếp.

### F-T09A-05 — `task_registry_snapshot.sh` bỏ sót `IMPLEMENTED` và `VERIFYING`
Phân loại: **HARDENING** (tầng governance) · Capability: `CAP-GOVTOOL` · Owner: chưa có

Công cụ mà `CAPABILITY_MODEL.md` §II.9 chỉ định để đo chống-sinh-sôi lọc dòng roadmap bằng
danh sách trạng thái thiếu hai state của chính lifecycle canonical (`AGENTS.md` §4). Hệ quả đo
được ngay trong phiên này:

```
# công cụ, BEFORE (main 814d185)              -> count_roadmap_task_ids = 28   (thiếu T-03 VERIFYING)
# công cụ, AFTER                              -> count_roadmap_task_ids = 27   (thiếu thêm T-09A IMPLEMENTED)
# đo lại bằng tay, danh sách trạng thái ĐẦY ĐỦ:
#   BEFORE = 29 ID · AFTER = 29 ID · diff = RỖNG
```

`T-03` đã vắng mặt TRƯỚC khi T-09A chạm vào bất cứ thứ gì — khiếm khuyết có trước phiên này.
Không BLOCKING (tầng tooling, không có đường production sai), nhưng phải ghi vì nó làm cho một
phiên trung thực trông như vừa xoá task. Xem `HARDENING_BACKLOG.md` **H-22**.

T-09A **không tự sửa script**: ngoài Expected Touch Area, `CAP-GOVTOOL` vẫn
`OWNER_ASSIGNMENT_REQUIRED`, và kéo nó vào đây chạm ngưỡng **D** của Absorption Limit (việc
ngoài Vertical Slice lên đường găng). Phép đo thay thế bằng tay được ghi ở trên và trong
`CHECK-T09A-11`.

## 5. Những thứ đã soi và KHÔNG thành finding

Ghi lại để phiên sau không phải soi lại từ đầu.

- **`month(mk)` có side effect tạo sổ tháng** khi `mk` chưa tồn tại, và `currentMonth()` trả
  key lớn nhất. Đã kiểm: `L.month` luôn là một tháng đã tồn tại tại thời điểm reserve; nhánh
  suy luận chỉ trả `guess` khi `state.months[guess]` tồn tại, ngược lại trả `currentMonth()`
  (cũng tồn tại). Không có đường nào tạo ra một key mới lớn hơn mọi key hiện có, nên
  `currentMonth()` không bị dịch chuyển bởi bản vá.
- **Hai ladder cùng tháng, huỷ một cái**: `take = min(open₁, m.smart.r)` với
  `m.smart.r = cap₁ + cap₂` → `take = cap₁`, backing của ladder còn lại nguyên vẹn. Có
  assertion (`backingOk`).
- **Ladder OPPORTUNITY**: `state.oppFund` xuyên tháng nên `ladderMonth` không đổi kết quả;
  `poolFor("OPPORTUNITY", mk)` vẫn trả `state.oppFund`. Không đổi hành vi.
- **Unlock tụt về 0 sau khi đã reserve**: reserve cũ không bị đụng, release không bị gate bởi
  unlock — đúng Strategy §8 và "vốn đã execute không relock" (§6).
- **`createLadder` thất bại có để lại side effect không**: không. `reserveFor` trả về trước
  khi mutate ở cả hai nhánh từ chối; có assertion "pool không bị đụng tới khi reserve bị từ
  chối".
- **`clamp` trả NaN cho input không hữu hạn** → `Number.isFinite` guard trong
  `smartReservable`/`oppReservable` → cap = 0 (fail closed). Không có đường nào cho `undefined`
  đi qua thành "không giới hạn".
- **`deducted = min(amount, pool.r)` trong `addBuy`** có thể ghi nhận fill nhỏ hơn số USDT
  thật chi nếu `pool.r` thiếu. Hành vi này **có trước** T-09A và không bị bản vá đổi; sau bản
  vá nó chỉ đạt được từ state đã hỏng sẵn, không dựng được từ nguồn canonical nào.
- **Với seed demo (OSCORE 30,7 → unlock 0%) app không tạo được Smart ladder nào nữa.** Đây
  KHÔNG phải regression: đó chính là hành vi Strategy §12 yêu cầu, và message nêu rõ lý do kèm
  hạn mức. Ưu tiên số 1 của `DEC-011` là CORRECT DECISION.
- **Bảo trì 4 test WP-C1**: chỉ THÊM một bước tiền đề mở unlock qua đúng UI. Không assertion
  nào bị xoá, không ngưỡng nào bị hạ, không bước nào bị bỏ. Bằng chứng đã ghi của WP-C1 tại
  SHA của nó không bị sửa.

## 6. Verdict

    CONFIRMED BLOCKING          = 0
    PROVISIONAL                 = 0
    HARDENING                   = 4   (F-T09A-01 -> H-19, F-T09A-02 -> H-20,
                                       F-T09A-04 -> H-21, F-T09A-05 -> H-22)
    OUT_OF_SCOPE (đã có owner)  = 1   (F-T09A-03 -> WP-C4)
    Task ID mới                 = 0

    VERDICT = PASS -> ELIGIBLE_FOR_FREEZE

Theo `REVIEW_PROTOCOL.md` § Verdict, phán quyết này là **advisory**: phiên này KHÔNG ghi
`FROZEN` và KHÔNG ghi `DONE`. Chuyển T-09A sang `DONE` là hành vi của chủ dự án
(`STATE_AUTHORITY.md`).

## 7. Hệ quả budget

Lượt `814d185..d125fe5` là **implementation ban đầu** của T-09A, không phải repair cycle —
cùng quy ước đã áp cho `CAP-PROV` (§1 ledger: "REPAIR CYCLES ĐÃ TIÊU = 2, **ngoài lượt
implementation ban đầu**") và cho `CAP-DATA` (§2.1). Batch review trả 0 BLOCKING nên **không**
phát sinh lượt sửa sau review.

    CAP-WEBAPP repair cycles USED = 0   (vẫn 0 sau phiên này)

Hai defect do chính reviewer phát hiện trong lượt này (banner suy luận không hiện khi chưa nạp
seed; `shortfall` không nhìn thấy được trên UI) nằm TRONG cumulative repair diff của chính lượt
này, nên là khiếm khuyết của cùng lượt và **không** mở chu kỳ mới
(`REVIEW_PROTOCOL.md` § "inside the cumulative repair diff -> same cycle"). Cả hai đã được sửa
trước khi commit.
