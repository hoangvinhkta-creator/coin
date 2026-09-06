# T-15 — Báo cáo gộp (implementation + bằng chứng E2) — sửa 7 lỗi kế toán L-1

**Phiên:** `S042` · **Ngày:** 2026-09-06 · **Nhánh:** `claude/fix-7-ledger-errors-91dybv`
**Nguồn lỗi:** rà soát độc lập `COINDCA_L1_REVIEW_T12_T14.md` (2026-09-06, repo @ `6c1d894`)
**Task:** `docs/tasks/T-15-sua-7-loi-ke-toan-l1.md` · **Quyết định:** `DEC-051`

Báo cáo này GỘP implementation report + bằng chứng E2 vào một file theo ngân sách artifact cứng
của `DEC-051` §B. Không có evidence log (`.txt`/`.json`/`.log`) nào được commit; mọi số liệu
tóm tắt nằm ngay trong file này và tái lập được bằng các lệnh ghi kèm.

---

## 1. Xác nhận mô tả so với code thật (làm TRƯỚC mỗi sửa)

Bản rà soát dẫn số dòng theo `6c1d894`. Trước mỗi sửa đã đọc lại code quanh dòng được nêu.
Kết quả: **mọi mô tả đều đúng về nội dung**; các chỗ lệch dưới đây chỉ là số dòng hoặc là
chi tiết cần nói chính xác hơn — không có chỗ nào lệch tới mức phải DỪNG.

| Mục | Bản rà soát ghi | Code thật (trước sửa) | Nhận xét |
|---|---|---|---|
| L1 | `ledger.js:211-214` (chỗ khác ghi `:213`) | đúng khối `211-214` | khớp |
| L2 | `ledger.js:203` | đúng dòng `203` | khớp |
| L3 | `:189`, cờ ở `:219` | đúng cả hai | khớp |
| L4 | `ledger.js:170-176`; chặn ở `~:110` | nhánh SELL `170-176`; `side` kiểm ở `110`, phí ở `112` | khớp |
| L5 | guard `~:229-235` | đúng vòng lặp `229-232` | khớp |
| L6 | oracle `~:265-280` | `comparisons` ở `270`, `costVnd` ở `276` | khớp |
| L7a | `:148,179` | `148` khai `eventEffects/invested/planSpent`; `179` GHI `eventEffects[e.id]`. Bản đồ `months` khai ở `181`, không phải `179` | lệch nhỏ; đã sửa cả bốn bản đồ |
| L7b | `ledger_ui.js:~49` | `localStorage.setItem` ở `49`; **còn một chỗ thứ hai** ở `105` (`restoreSnapshot`, nhánh restore của T-14) mà bản rà soát không nêu | đã bọc CẢ HAI qua helper `keepLocal()` |
| L7c | `:178` (reserve) | đúng | khớp |
| L7d | `:118` | đúng | khớp |
| L7e | `:112` | đúng | khớp |
| L7f | `:100,118` / `ledger_ui.js:312` | đúng | khớp |
| L7g | `build_app.js:9, 20, 34` | đúng cả ba | khớp |
| Nhãn "(Bán)" | `ledger_ui.js:~202` | đúng dòng `202` | khớp |
| Hint UI sai | `ledger_ui.js:~329` | đúng dòng `329` | khớp |
| Test bỏ lọt L1 | `test_t12_fixtures.js:~35`, `test_t12_ledger.js:~157` | đúng | khớp |

**Một chỗ mô tả không khớp thực tế, đã kiểm và báo ngay ở đây:** bản rà soát nói SELL "chỉ vào
được qua import JSON". Đúng cho đường người dùng, **nhưng repo còn hai test khẳng định hành vi
SELL cũ** — xem §4.

---

## 2. Thay đổi thực tế (đo trực tiếp, không cộng tay)

    git diff --stat <base>..HEAD -- webapp
      webapp/build_app.js         |   8 +-
      webapp/ledger.js            |  70 ++++++++---
      webapp/ledger_ui.js         |  23 ++++--
      webapp/package.json         |   4 +-
      webapp/test_l1_fixes.js     | 196 +++++++++++++++++++++++++++++ (MỚI)
      webapp/test_t12_browser.js  |   5 +-
      webapp/test_t12_ledger.js   |  16 ++--
      7 files changed, 289 insertions(+), 33 deletions(-)

    # riêng mã production (không tính test/package.json)
    git diff --shortstat <base>..HEAD -- webapp/ledger.js webapp/ledger_ui.js webapp/build_app.js
      3 files changed, 77 insertions(+), 24 deletions(-)

    # frozen artifact — phải RỖNG
    git diff --stat <base>..HEAD -- src/eth_dca_os docs/spec firestore.rules
      (rỗng)

Trong ước lượng change budget của task (≤ 8 file, ≤ 300 dòng). Không `CHANGE_BUDGET_EXCEEDED`.

### 2.1 Từng lỗi

**L1 — `nextPlannedAmountVnd = 0` sau slot cuối tháng.** Nhánh "sang tháng sau" nay đặt
`nextPlannedAmountVnd = split(np.monthlyBudgetVnd, nd.length)[0]` — đúng slot đầu của tháng sau,
KHÔNG trừ `planInvested` tháng này, KHÔNG cap bằng `remaining` tháng này.

**L2 — carry-in không vào lịch mua.** `plannedPerSlot = split(month.plannedBudgetVnd, …)` thay
cho `split(p.monthlyBudgetVnd, …)`. Khi `plannedBudgetVnd === null` (không tính được ngân sách)
thì `plannedPerSlot = []` — `split()` không nhận `null`. Vòng lặp trong tháng đổi cận trên từ
`dates.length` sang `plannedPerSlot.length` để hai mảng luôn đi cùng nhau; với mọi trường hợp
tính được ngân sách hai độ dài bằng nhau, nên hành vi trong tháng KHÔNG đổi ngoài giá trị tiền.

**L1 và L2 không đá nhau** — kiểm bằng chính bộ số tái lập: cùng một sổ, `asOf 2026-01-14` đi
đường trong-tháng (9.990.000, chia theo `plannedBudgetVnd` = 20.000.000 vì carry-in tháng 1 = 0),
`asOf 2026-01-24/31` đi đường sang-tháng-sau (6.666.667). Test `L1` và `L2` chạy trên cùng fixture.

**L3 — `startMonth` sớm hơn version đầu tiên.** Ba lớp:
(a) `planCheck` từ chối, thông báo tiếng Việt nêu đúng hai tháng và hai cách sửa;
(b) `buildMonth` cho `carryOutVnd = 0` khi tháng không có version (`null` chỉ dành cho "chưa
biết"), nên một tháng thiếu version không đầu độc chuỗi tháng sau;
(c) `month.plannedBudgetVnd` được thêm vào điều kiện cờ → trạng thái "không tính được ngân
sách" luôn hiện `UNKNOWN_VND_BASIS`, không còn `flags = []` im lặng.

**L4 — SELL.** `eventCheck` từ chối `side === 'SELL'` với thông báo dẫn `H-46`. KHÔNG thiết kế
P&L. Khối SELL trong `derive()` (`170-176` cũ) được GIỮ NGUYÊN và gắn nhãn "KHÔNG CÒN TỚI ĐƯỢC"
làm điểm neo cho `H-46` — xoá nó sẽ khiến `H-46` phải viết lại từ đầu, giữ nó không đổi hành vi
nào vì không đường nào tới được.

**L5 — sửa hồi tố.** Guard version cũ nay so `FROZEN = [effectiveFrom, asset, monthlyBudgetVnd,
scheduleDays, carryPolicy, carryCapMonths]` bằng `JSON.stringify` từng trường. Hint UI ở
`ledger_ui.js:329` viết lại cho đúng hành vi thật.

**L6 — migration.** Oracle `costUsdt` nay so với `costUsdtExFee = d.holdings.ETH.costUsdt −
Σ feeUsdt của các BUY` — cùng định nghĩa với `legacy.costUsdt`. Dung sai **giữ nguyên** ±1
micro-USDT. `derive()` KHÔNG đổi định nghĩa: giá vốn USDT thật vẫn gồm phí (test L6 khẳng định
`costUsdt = 120.500.000` sau migrate, trong khi oracle so `120.000.000`). Oracle `costVnd` nâng
thành cờ CỨNG: `|delta| > 1 VND` → `errors.push('M-3: lệch costVnd')`; `actual === null` (UNKNOWN)
KHÔNG chặn vì đã có `W-1`/`UNKNOWN_VND_BASIS`; `legacy.costVnd` không phải số → `M-3: thiếu oracle
costVnd`.

**L7a** — `Object.create(null)` cho `eventEffects`, `invested`, `planSpent`, `months`. Ở biên
public, `derive()` trả `months`/`eventEffects` qua `plain()` (`Object.defineProperties` +
`getOwnPropertyDescriptors`) để prototype trở lại bình thường mà `__proto__` **vẫn là own
data-property**. Cần thiết vì `INV-2` so kết quả in-process với kết quả qua JSON của một process
khác — hai bên phải cùng prototype.
**L7b** — helper `keepLocal()` bọc `localStorage.setItem` trong `try/catch` cho **cả hai** nhánh
snapshot; lỗi báo cho người dùng qua `message()`, không ném ra ngoài. Bản backup TẢI VỀ vẫn được
tạo — đó mới là backup thật; `localStorage` chỉ là lớp tiện lợi thứ hai.
**L7c** — `vnd.balance < 0` bật `LEDGER_INCONSISTENT` + `firstOffendingEventId`, cùng cơ chế
với `reserve`.
**L7d** — `priceUsdt = 0` bị từ chối. **Thêm một dòng cùng bản chất, ghi rõ ở đây để không lọt
âm thầm:** `usdVndRate = 0` cũng bị từ chối (vẫn cho `null`) — một tỷ giá 0 sẽ cho định giá 0 ₫,
đúng loại vô nghĩa mà L7d nhắm tới.
**L7e** — `feeUsdt > usdtNotional` bị từ chối cho MỌI trade (trước chỉ kiểm SELL).
**L7f/L7g** — xem §3.

---

## 3. Ba lựa chọn được yêu cầu nêu rõ

### 3.1 L1 — carry của tháng sau: **dùng ngân sách GỐC của tháng sau**

Carry-out của tháng hiện tại chỉ chốt được khi tháng đó đóng (`carryOutVnd = m < currentMonth ?
… : null` — bất biến sẵn có, không đổi). Vì vậy khi trỏ sang slot đầu tháng sau, con số duy nhất
biết chắc là `monthlyBudgetVnd` của version áp dụng cho tháng sau. Hệ quả trung thực: nếu tháng
này còn dư, số hiển thị cho slot đầu tháng sau sẽ **thấp hơn** thực tế sau khi tháng này đóng —
thà thiếu một cách xác định còn hơn đoán một carry chưa chốt. Ghi lại bằng một comment một dòng
ngay tại chỗ sửa.

### 3.2 L7f — `usdVndRate`: **DÙNG, không bỏ**

Chọn dùng, vì hai lý do đo được:
1. **Bỏ khỏi schema là thay đổi phá vỡ dữ liệu bền.** `canonical()` từ chối trường lạ
   (`Trường không canonical`), nên mọi sổ đã lưu có event `PRICE` mang `usdVndRate` sẽ **không
   nạp được nữa** — biến một trường chết thành một sổ chết.
2. Dùng nó KHÔNG phạm `OD-L1-4 STRICT`. Lệnh cấm đó nói về **giá vốn**: không suy tỷ giá để bịa
   giá vốn VND. Ở đây tỷ giá do chính Owner nhập trên chính event `PRICE`, và chỉ chảy vào
   **định giá hiển thị** (`valuation.vnd`), không bao giờ chạm `costVnd`/`avgCostVnd`/carry.
   Không có tỷ giá → `valuation.vnd = null`, không suy diễn.

`derive()` nay trả `valuation = { usdt, vnd, usdVndRate, businessDate }`; UI hiện
`480 USDT ≈ 12.480.000 ₫ (2026-01-31)`. Nhãn ô nhập đổi thành "USDT/VND để quy đổi định giá
(tùy chọn)".

### 3.3 L7g — `engine.js`: **GỠ khỏi bundle**

Đã kiểm toàn bộ đường L-1 còn tham chiếu `ENGINE` hay không:

    grep -rn "ENGINE" webapp/*.js webapp/*.html   # ngoài chính engine.js
      build_app.js:34   (assertion cũ)
      test_helpers.js   (harness legacy V2.1.5)
      test_t12_ledger.js:98 (INV-10: khẳng định ledger.js KHÔNG nhắc ENGINE)

`app_logic.js`, `ledger_ui.js`, `app_shell.html`: **0 tham chiếu**. Tab "Cài đặt" chỉ dùng `seed`
như một khối dữ liệu mờ (`RESEARCH_ONLY`, backup payload), không gọi hàm nào của engine — không
có seed/parity check nào còn sống. `test_helpers.js` gọi `ENGINE` **bên trong trang**, nhưng nó
chỉ phục vụ bộ `test:legacy-v215`, vốn đã không chạy được từ T-13: harness đó thao tác
`[data-tab="entry"]`/`#pxAdd`, và `app_shell.html` hiện có **0** phần tử như vậy. Bộ đó cũng
không nằm trong `npm test`.

Kết luận: `engine.js` là dead code trên trang, và nó **vẫn mang lỗi B10** (rolling window đếm
dòng thay vì đếm ngày lịch). Đã gỡ khỏi `build_app.js`; assertion `'const ENGINE'` đổi chiều
thành **cấm** nhúng, và thêm `'window.CoinLedger'` vào danh sách mảnh bắt buộc để assertion vẫn
canh đúng một mảnh sống. File `webapp/engine.js` GIỮ NGUYÊN trên đĩa (frozen research, không
xoá). Ghi một dòng HARDENING cho bộ `test:legacy-v215` đã chết — xem §6.

---

## 4. Test cũ khẳng định hành vi SAI — báo trước khi sửa

`grep -rn "SELL" tests/ webapp/ docs/`:

- `tests/fixtures/t12/*.json`: **0** kết quả. Fixture Owner và schema acceptance **không** chứa
  `SELL` → chặn SELL không làm hỏng fixture nào.
- `docs/reviews/evidence/T13/`, `T14-E2/`: có `SELL`, nhưng là **evidence log đã đóng băng** của
  các phiên trước, không phải đường chạy — không đụng tới.
- **`webapp/test_t12_ledger.js` có HAI ca chạy thật khẳng định hành vi SELL cũ:**
  - `INV-3` (`:48-56`) — assert số sau SELL, tức là assert **chính cái bất biến bị vỡ**
    (10.010.000 + 39.990.000 + 0 → 5.005.000 + 44.990.000 + 0).
  - `INV-11` (`:110-111`) — dùng SELL trên pool rỗng để chứng minh `usdt.costVnd` thành `null`.

  Đây là "test khẳng định hành vi sai", không phải fixture/state production. Đã báo ở đây và
  xử lý tối thiểu, giữ nguyên tên test để `test_t12_mutations.js` (`--test-name-pattern=^INV-3 `,
  `^INV-11 `) chạy nguyên văn:
  - `INV-3`: ba dòng assert số sau SELL → **một** `A.throws(…, /H-46/)`; tiêu đề đổi
    "SELL ETH/USDT" → "SELL bị chặn". Phần WAC/pool-drain/ROUND_VND giữ nguyên.
  - `INV-11`: ca SELL-trên-pool-rỗng → cùng ý nghĩa qua đường `TREASURY USDT_TO_VND` trên pool
    `costVnd = null`. Vẫn giết được mutant `INV-11` (`portion` trả `0` thay vì `null`).

- **`webapp/test_t12_browser.js:57`** — oracle tính tay `month.nextPlannedAmountVnd = 20.000.000`
  cho tháng 3/2026 có `carryIn = 10.659.700`. Con số đó **chính là lỗi L2** được đóng băng thành
  oracle: ngân sách gồm carry là 30.659.700 nhưng lịch chỉ chia 20.000.000. Sau sửa, giá trị đúng
  là **30.659.700** (3 × 10.219.900). Đã cập nhật oracle kèm comment giải thích. Đây là ca duy
  nhất trong toàn bộ bộ test mà L2 làm đổi một con số đã đóng băng.

Không có state/fixture production nào chứa SELL → không có gì bị hỏng bởi việc chặn.

---

## 5. Bằng chứng chạy

### 5.1 Đỏ trước — xanh sau

`webapp/test_l1_fixes.js` (MỚI, 15 test) chạy trên **code trước khi sửa**:

    node --test test_l1_fixes.js
      # tests 15 | # pass 0 | # fail 15

Từng test đỏ vì đúng lý do của lỗi nó nhắm tới (trích lý do thất bại):

| Test | Lý do đỏ trước khi sửa |
|---|---|
| L1 | `nextPlannedAmountVnd` = 0 tại `asOf 2026-01-24`/`31` |
| L2 | `Σ plannedPerSlot` = 20.000.000 ≠ `plannedBudgetVnd` 40.000.000 |
| L3a | `Missing expected exception` — plan sai được nhận |
| L3b | `carryOutVnd = null`, `plannedBudgetVnd` tháng 6 = `null` |
| L3c | `flags = []` |
| L4 | `Missing expected exception` — SELL được nhận |
| L5 | `Missing expected exception: {"monthlyBudgetVnd":30000000}` |
| L6 (1) | `["M-3: lệch costUsdt"]`, delta 500000 |
| L6 (2) | lệch `costVnd` 900.000.000 vẫn `ok: true` |
| L7a | `__proto__` không phải own-property |
| L7c | `flags = []` dù `vnd.balance = -50.000.000` |
| L7d | `priceUsdt = 0` được nhận |
| L7e | BUY `feeUsdt > usdtNotional` được nhận |
| L7f | `valuation.vnd` không tồn tại |
| L7g | `build_app.js` còn đọc `engine.js` |

Sau khi sửa:

    node --test test_l1_fixes.js
      # tests 15 | # pass 15 | # fail 0

### 5.2 Toàn bộ bộ test

| Suite | Cần emulator | Kết quả |
|---|---|---|
| `test_t12_ledger.js` (+ `test_t12_fixtures.js` làm module oracle) | không | **PASS** — 32/32 |
| `test_l1_fixes.js` | không | **PASS** — 15/15 |
| `test_t12_mutations.js` | không | **PASS** — 7/7 mutant KILLED, 0 survivor |
| `test_t14_deploy_isolation.js` | không | **PASS** — 18 assertion, FAIL 0 |
| `test_t14_rules.js` | có | **PASS** — 120 assertion, FAIL 0 |
| `test_t14_persistence.js` | có | **PASS** — 60 assertion, FAIL 0 |
| `test_t14_backup_restore.js` | có | **PASS** — 47 assertion, FAIL 0 |
| `test_t12_browser.js` | có | **PASS** — P-1…P-6 + migration M-1..M-4 |
| `test_stepb_ui.js` | có | **PASS** — 0 mục `"status": "FAIL"` |

**`npm --prefix webapp test` → exit 0.** Firestore/Auth Emulator **chạy được thật** trong phiên
này (`firebase emulators:start --only auth,firestore --project demo-ethdca`, sau `npm ci` 725
package), Chromium dùng `/opt/pw-browsers/chromium`. Khác với rà soát trước (emulator bị proxy
chặn), phiên này KHÔNG có suite nào phải bỏ qua — không suite nào được báo PASS mà không chạy.

`test_stepb_ui.js` AS-10 (grep toàn DOM: không `SELL`/`Bán` ở bất kỳ nhãn nào) vẫn PASS sau khi
gỡ nhãn "(Bán)" chết.

### 5.3 Fixture Owner — không đổi

    node test_t12_owner.js ../tests/fixtures/t12/owner-example.synthetic.json
      OWNER_LOCAL_ACCEPTANCE: PASS

9/9 trường `expected` khớp bit-exact với `tolerance = {vnd:0, usdt:0, qty:0}`. Fixture **không bị
sửa một byte nào** (`git diff --stat -- tests/fixtures` rỗng).

### 5.4 Vì sao báo cáo này thay cho một vòng E2 riêng

Bảy lỗi do một **rà soát độc lập** (không phải implementer) tái lập bằng harness riêng, kèm số
liệu cụ thể. Bộ test tái lập dùng **đúng số liệu của người rà soát**, không phải số do implementer
tự sinh, và đã được chứng minh **đỏ trên code trước khi sửa** — tức nó đóng vai trò oracle độc lập
với người sửa. Cộng thêm: fixture Owner đóng băng không đổi, mutation suite 7/7 KILLED, và toàn bộ
`npm test` chạy trên emulator + trình duyệt thật. `DEC-051` §C ghi nhận đây là mức bằng chứng đủ
cho gate `T-15` (E1 toàn bộ), KHÔNG mở vòng E2 thứ hai.

---

## 6. HARDENING — ghi nhận, KHÔNG sửa trong task này

| ID | Nội dung | Vì sao không sửa ở đây |
|---|---|---|
| `H-46` | Thiết kế P&L thực hiện khi bán (`usdt.costVnd += relieved`; `realizedPnlVnd`) | Scope OUT tường minh. L4 chỉ chặn đường vào |
| `H-54` | `RESERVE CONTRIBUTE` không trừ `vnd.balance` → cùng số tiền đếm hai lần trên Dashboard | Không nằm trong 7 lỗi được giao |
| `H-55` | `startMonth = '0001-01'` hợp lệ → vòng lặp 24.309 lần mỗi render | Không nằm trong 7 lỗi được giao |
| `H-56` | `LEGACY_ARCHIVE`/`RESEARCH_ONLY` không giới hạn kích thước → có thể vượt trần 1 MiB Firestore | Không nằm trong 7 lỗi được giao; cùng họ với `H-29` |
| `H-57` | Bộ `test:legacy-v215` đã chết từ T-13 (harness thao tác `#pxAdd`/`[data-tab="entry"]` không còn tồn tại) và `test_helpers.js` còn gọi `ENGINE` trong trang | Gỡ bộ test là quyết định riêng; L7g chỉ gỡ engine khỏi **bundle** |
| `H-58` | `planCheck` nay từ chối plan có `startMonth` < `effectiveFrom` nhỏ nhất. Một sổ bền đã lưu ở hình dạng đó sẽ **không nạp được** cho tới khi Owner sửa `startMonth` | Đây là hệ quả CỐ Ý của L3(a) (fail-visible thay cho null im lặng). Rủi ro thấp: UI mặc định `l1StartMonth = l1Effective =` tháng hiện tại. Đường cứu: sửa `startMonth` trong file backup rồi restore |

---

## 7. Ngân sách artifact của chính phiên này

| Hạng mục | Cho phép (`DEC-051` §B) | Thực tế |
|---|---|---|
| Task file | 1 | 1 — `docs/tasks/T-15-sua-7-loi-ke-toan-l1.md` |
| Báo cáo | 1 (gộp implementation + E2) | 1 — chính file này |
| DEC | 1 (closure) | 1 — `DEC-051` |
| Evidence log commit (`.txt`/`.json`/`.log`) | 0 | **0** |

Ngoài bốn mục trên, phiên chỉ cập nhật **state surface** đã tồn tại (`PROJECT_PROGRESS.md`,
`REVIEW_BUDGET_LEDGER.md`, `HARDENING_BACKLOG.md`) — bắt buộc theo `STATE_AUTHORITY.md`, không
phải artifact mới. Phụ lục dọn stale đi ở **một commit riêng, không cần DEC**.
