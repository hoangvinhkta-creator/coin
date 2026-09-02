# WP-C1 — Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test

## Metadata
Status:
DONE

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION · **ưu tiên cao nhất trong lớp C**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 3
B: 2
A: 1
X: 2
U: 2
V: 3
H: 2
C: 2
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.1

Effort Routing Score:
2.45

Applied Model Floor:
none

Applied Effort Floor:
none

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
2/4

Risk:
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Đưa ba nghi vấn kế toán của app web từ mức **E0 (nghi vấn)** lên mức **E1 (kết luận có bằng chứng
chạy thật)** — xác nhận hoặc bác bỏ, không để lửng — và khôi phục bộ test webapp sao cho chạy được
**từ một bản checkout sạch**.

## Vì sao gói này được đề nghị ưu tiên cao nhất trong lớp C

Lý do không nằm ở đường găng kỹ thuật mà ở an toàn: nếu chủ dự án đang dùng app để ghi giao dịch
tiền thật, ba nghi vấn này — **nếu đúng** — đang làm sai sổ vốn **ngay lúc này**. Gói này không đụng
`src/`, không cần dữ liệu Binance, không phụ thuộc gói nào khác, nên khởi động được ngay song song
với toàn bộ lớp A.

## Ba nghi vấn phải kết luận

| ID | Nghi vấn | Vị trí | Mức hiện tại |
|---|---|---|---|
| V-01 | Release vốn có thể trả **nhầm pool** khi có nhiều tháng: hàm chọn tháng hiện hành trả về tháng có key lớn nhất, không phải tháng của ladder | `webapp/app_logic.js:124-127,315-320` | E0 |
| V-02 | Mức unlock **không giới hạn** số vốn được reserve; `reserveFor` chỉ kiểm available | `webapp/app_logic.js:289-297` | E0 |
| V-03 | Trạng thái dữ liệu INVALID **không chặn** tạo ladder mới như Strategy §3 yêu cầu | `webapp/app_logic.js:324-335` | E0 |

Đã thu hẹp được một phần (E1, S000): `webapp/test_zone.js` cho thấy bất biến `TOTAL = A + R + D`
giữ đúng **trong kịch bản một tháng**. Điều đó **không bác bỏ V-01**, vì V-01 nói về kịch bản **đa
tháng** — đúng vào điểm mù của test hiện có. V-02 và V-03 chưa có ca kiểm thử nào chạm tới.

## Đóng finding / risk

- V-01, V-02, V-03 — ba nghi vấn kế toán của app web
- F-027 — bộ test webapp không chạy được từ bản checkout sạch
- RSK-003 — xác nhận hoặc bác bỏ
- RSK-004 — xác nhận và khắc phục

**Gỡ BLOCKED cho T-03** khi hoàn tất — nhưng chỉ bằng cách **thoả CHECK-03-01**, tuyệt đối không
bằng cách hạ Completion Gate của T-03 (DEC-007 tác động 6).

## Scope

- `webapp/test_app.js`, `webapp/test_zone.js` và hạ tầng chạy test
- Khôi phục đường tạo `webapp/app_final.html` từ repo
- Khôi phục hoặc sinh lại `demo/results3/live_seed.json` (hiện **không tồn tại ở bất kỳ đâu trong repo**)
- Ca kiểm thử mới cho V-01 (đa tháng), V-02, V-03
- `.gitignore` — chặn ảnh chụp màn hình do test sinh ra
- `webapp/README.md` — hướng dẫn chạy test từ checkout sạch

## Out of Scope

- **Sửa lỗi kế toán nếu nghi vấn được xác nhận** — đó là **T-09A**. Gói này kết luận, không vá
- Thêm tính năng cho app
- Lớp lưu trữ bền (T-09B)
- Mở rộng parity JS ↔ Python (WP-C4)
- Sửa `src/eth_dca_os/`

## Dependencies
- T-01 (DONE)
- T-04 (DONE)

## Blocks
- T-03 (gỡ BLOCKED)
- T-09A (quyết định phạm vi, hoặc CANCELLED nếu cả ba nghi vấn bị bác bỏ)

## Parallel-Safe With
- Toàn bộ lớp A, WP-D1, WP-D2 — gói này độc lập hoàn toàn

## Expected Touch Area

Allowed:
- `webapp/test_app.js`, `webapp/test_zone.js`, `webapp/build_app.js`, `webapp/README.md`
- Ca kiểm thử mới trong `webapp/`
- `demo/` — dữ liệu seed cho test
- `.gitignore`

Do not touch without Scope Expansion:
- `webapp/app_logic.js`, `webapp/engine.js` — **chỉ được đọc**; sửa là T-09A
- `src/eth_dca_os/` — kể cả `live_export.py`
- `docs/spec/`

## Subtasks
- [x] C1.1 Khôi phục đường dựng `app_final.html` từ repo, không cần thao tác thủ công ngoài repo
- [x] C1.2 Khôi phục hoặc sinh lại `demo/results3/live_seed.json` bằng một lệnh có trong repo
- [x] C1.3 Chạy hai test webapp từ bản checkout sạch, ghi lại quy trình
- [x] C1.4 Dựng ca kiểm thử **đa tháng** cho V-01
- [x] C1.5 Dựng ca kiểm thử cho V-02 (unlock giới hạn reserve)
- [x] C1.6 Dựng ca kiểm thử cho V-03 (INVALID chặn tạo action)
- [x] C1.7 Kiểm bất biến kế toán qua kịch bản đa tháng đầy đủ
- [x] C1.8 Chặn ảnh chụp màn hình do test sinh ra khỏi repo
- [x] C1.9 Ghi kết luận E1 cho từng nghi vấn và cập nhật RSK-003, RSK-004

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa — **đặc biệt: không sửa lỗi, chỉ kết luận**
- [x] Dependency (T-01, T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §3; Product Spec §4, §5, §8; và Completion Gate của T-03
- [x] Data impact được biết — **cảnh báo an toàn:** nếu chủ dự án đang có dữ liệu thật trong app,
      phải xuất dữ liệu ra file trước khi chạy bất kỳ thử nghiệm nào chạm localStorage
- [x] Security impact được biết — không có dữ liệu bên thứ ba; không commit dữ liệu tài chính thật
      của chủ dự án vào repo
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 3 → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng được. Ba nghi vấn V-01/V-02/V-03
**không được kết luận bằng đọc code** — đó chính là mức E0 mà gói này tồn tại để vượt qua.

### Testing / Harness

#### CHECK-C1-01 — Bộ test webapp chạy được từ bản checkout sạch
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: từ một clone sạch, chạy được cả hai test **chỉ bằng các lệnh có trong repo**, không dựng
thủ công file nào. Bằng chứng gồm chuỗi lệnh và output. Đóng F-027, giảm thiểu RSK-004.

Root cause của F-027: `webapp/build_app.js` và `webapp/test_*.js` đọc/ghi file bằng path
tương đối theo `process.cwd()` (`fs.readFileSync('app_shell.html', ...)`,
`'demo/results3/live_seed.json'`), nên chỉ chạy đúng khi gọi từ đúng một thư mục cwd cụ thể —
gãy khi gọi theo cách tự nhiên nhất (`node webapp/build_app.js` từ gốc repo). Sửa: chuyển toàn
bộ path sang `__dirname`-based trong `webapp/build_app.js`, `webapp/test_app.js`,
`webapp/test_zone.js` (screenshot, `app_final.html`, seed path) — chạy đúng bất kể cwd.

Bằng chứng chạy thật (mô phỏng clone sạch — xoá toàn bộ artifact sinh ra rồi làm lại chỉ bằng
lệnh repo, không thao tác thủ công):

```
rm -rf demo webapp/app_final.html webapp/node_modules webapp/app-dash.png webapp/app-zone.png
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm --prefix webapp install
source .venv/bin/activate   # venv theo README gốc repo, pip install -e ".[dev]"
ethdca --raw-dir data/raw synth --start 2024-01-01 --end 2026-06-30
ethdca --raw-dir data/raw --out-dir demo/results3 export-live
node webapp/build_app.js
npm --prefix webapp test     # test_app.js && test_zone.js && test_v01_v02_v03.js && test_multi_month_invariant.js
```

Exit code toàn bộ chuỗi = 0. `test_app.js`: "no page errors"; `test_zone.js`: "no errors";
`test_v01_v02_v03.js` + `test_multi_month_invariant.js`: "Tất cả assertion ... PASS". Không
sửa file nào ngoài repo, không thao tác tay ngoài các lệnh trên. `webapp/package.json` +
`webapp/package-lock.json` (mới, ghim `playwright@1.56.1`) là artifact commit được để
`npm install` tái lập đúng version; `webapp/node_modules/`, `webapp/app_final.html`,
`demo/`, ảnh chụp màn hình đều sinh lại được, không commit.

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

#### CHECK-C1-02 — Ảnh chụp màn hình do test sinh ra không làm bẩn repo
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: sau khi chạy test từ trong `webapp/`, `git status --porcelain` không xuất hiện
`app-dash.png` hay `app-zone.png`.

Thêm `webapp/app-dash.png`, `webapp/app-zone.png` (và `webapp/app_final.html`,
`webapp/node_modules/`) vào `.gitignore`. Chạy `node webapp/test_app.js` +
`node webapp/test_zone.js` (tạo cả hai ảnh trên đĩa, xác nhận bằng `ls webapp/*.png`), sau đó
`git status --porcelain` — không dòng nào nhắc tới `app-dash.png`/`app-zone.png`.

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

### Data Integrity / Verification

#### CHECK-C1-03 — V-01 có kết luận E1 bằng ca kiểm thử đa tháng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: dựng kịch bản có **ít nhất ba tháng** với ladder thuộc tháng **không phải** tháng có key
lớn nhất, thực hiện release, và khẳng định vốn quay về **đúng pool của tháng đó**. Kết luận phải là
XÁC NHẬN hoặc BÁC BỎ, kèm output. Không được ghi "chưa kết luận được" nếu ca kiểm thử dựng được.

**KẾT LUẬN: XÁC NHẬN LÀ LỖI THẬT.**

Ca kiểm thử: `webapp/test_v01_v02_v03.js` (`testV01`) — tháng A (2026-06): nạp vốn, tạo ladder
LA (reserve 1.000.000 từ pool Smart tháng A). Tháng B (2026-07, mới hơn): nạp vốn, tạo ladder
LB RIÊNG (reserve 2.000.000 từ pool Smart tháng B, LB vẫn ACTIVE trong suốt kịch bản) —
`currentMonth()` giờ trỏ về tháng B. Huỷ LA (nút "Hủy" → `cancelLadder()` → `releaseLadder(LA)`).

Số liệu chạy thật (output đầy đủ trong log CI/session, tóm tắt):
- Tháng A trước huỷ: `smart = {a:2.000.000, r:1.000.000, d:0}`
- Tháng B trước huỷ LA: `smart = {a:1.000.000, r:2.000.000, d:0}` (r=2.000.000 backing LB)
- Tháng A SAU huỷ LA: `smart = {a:2.000.000, r:1.000.000, d:0}` — **KHÔNG ĐỔI**, dù LA đã
  CANCELLED và zones đã `released_vnd` = 1.000.000
- Tháng B SAU huỷ LA: `smart = {a:2.000.000, r:1.000.000, d:0}` — `a` **TĂNG** 1.000.000
  (không tương ứng contribution nào), `r` **GIẢM** 1.000.000 (rút từ vốn đang backing LB, vẫn
  ACTIVE, không liên quan gì tới LA)

Root cause: `releaseLadder()` (`webapp/app_logic.js:302-322`) dùng `mk = currentMonth()`
(`webapp/app_logic.js:124-127` — trả về key lớn nhất trong `state.months`, không phải tháng
ladder được tạo/reserve) để xác định pool nhận lại vốn, thay vì tra cứu tháng gốc của ladder.
`take = Math.min(open, m.smart.r)` với `m` = tháng SAI: nếu tháng đó có `r` đủ lớn (như LB ở
đây), vốn của LA bị "đánh cắp" từ chỗ đang backing LB; nếu tháng đó có `r` không đủ/bằng 0
(xem `webapp/test_multi_month_invariant.js`), vốn của tháng gốc bị KẸT VĨNH VIỄN thay vì được
release. Tái hiện được qua CẢ nút Hủy thủ công LẪN luồng invalidation tự động (2 daily close
liên tiếp trên invalidation price) — xem `webapp/test_multi_month_invariant.js`.

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

#### CHECK-C1-04 — V-02 có kết luận E1: mức unlock có giới hạn được số vốn reserve hay không
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: dựng ca cố gắng reserve vượt mức unlock hiện hành trong khi available vẫn còn, khẳng định
hành vi thật. Kết luận XÁC NHẬN hoặc BÁC BỎ kèm output.

**KẾT LUẬN: XÁC NHẬN LÀ LỖI THẬT.**

Ca kiểm thử: `webapp/test_v01_v02_v03.js` (`testV02`) — nạp seed thật (OSCORE tính ra 30,7 từ
dữ liệu, "Smart unlock 0,0%" hiển thị đúng trên UI, đọc trực tiếp từ `#stateChips`). Nạp
contribution 10.000.000 → Smart available = 3.000.000 (30%). Tạo ladder SMART với cap =
3.000.000 = **100% Smart available**, trong khi Smart unlock đo được = **0,0%**.

Kết quả chạy thật: `ldMsg` = "Đã tạo ladder SMART với spacing 7,72%." — **ladder được tạo
thành công**, `smart.r` tăng đúng 3.000.000 (toàn bộ available bị reserve).

Root cause: `reserveFor()` (`webapp/app_logic.js:289-297`) chỉ so `vnd > m.smart.a` (hoặc
`state.oppFund.a`) — không có bất kỳ tham chiếu nào tới `view.smartUnlock` /
`view.oppUnlock` ở đây hay ở nơi gọi nó (`createLadder()`, dòng 324-335). Vi phạm trực tiếp
Strategy §12 "Không được reserve vốn chưa unlock" — `view.smartUnlock` được TÍNH
(`webapp/app_logic.js:92`) và HIỂN THỊ (dòng 472) nhưng không bao giờ được DÙNG để giới hạn gì.

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

#### CHECK-C1-05 — V-03 có kết luận E1: INVALID có chặn tạo action mới hay không
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: dựng ca dữ liệu INVALID rồi kích hoạt điều kiện tạo ladder, khẳng định hành vi thật so với
Strategy §3. Kết luận XÁC NHẬN hoặc BÁC BỎ kèm output.

**KẾT LUẬN: BÁC BỎ (về hành vi quan sát được) — kèm ghi chú kiến trúc quan trọng.**

Ca kiểm thử: `webapp/test_v01_v02_v03.js` (`testV03`) — KHÔNG nạp seed, nhập tay 5 ngày giá
liên tiếp qua UI (`#pxAdd`). Với 5 ngày, `factorScores()` (`webapp/engine.js:167-193`) cho cả
8 sub-factor NaN (R cần >14 ngày, S7 cần ≥7 ngày — cả hai đều chưa đủ) →
`data_quality = "INVALID"`, xác nhận qua `#stateChips` (chip đỏ "INVALID"). Nạp contribution
10.000.000 → Smart available = 3.000.000 (> 0, để phép thử không bị chặn vì "không đủ vốn").
Thử tạo ladder SMART cap = 1.000.000.

Kết quả chạy thật: `ldMsg` = "Chưa đủ lịch sử để tính ADR30." — **ladder KHÔNG được tạo**
(`state.ladders.length === 0` sau thao tác). Về mặt hành vi observable, INVALID (gián tiếp)
NGĂN được việc tạo ladder mới trong mọi trạng thái dựng được — khớp yêu cầu Strategy §3.

**Ghi chú kiến trúc bắt buộc (không hạ mức BÁC BỎ, nhưng phải ghi lại):** đọc
`createLadder()` (`webapp/app_logic.js:324-335`) xác nhận nó **không hề kiểm tra
`view.score.data_quality`** ở bất kỳ đâu. Block quan sát được ở trên đến từ guard
`!Number.isFinite(sp)` (`sp` = `view.smartSpacing`/`oppSpacing`, cần `adr30` hữu hạn — tức
≥30 ngày lịch sử liên tục, `webapp/engine.js` `smartSpacing`). Guard này TÌNH CỜ trùng với
vùng INVALID: theo toán học của `factorScores`/`computeIndicators` hiện tại, `INVALID` (8/8
sub-factor NaN) chỉ đạt được khi tổng lịch sử <7 ngày — và ở đó `adr30` (cần ≥30 ngày) LUÔN
NaN. Hai điều kiện không bao giờ cùng đúng, nên **không dựng được** một trạng thái
INVALID + spacing hữu hạn để kiểm tra guard ADR30 có thực sự là điều đang chặn hay có channel
khác — nói cách khác, mọi trạng thái INVALID đạt được ĐỀU bị guard ADR30 chặn trước khi có cơ
hội chạm bất kỳ logic nào khác. Ghi HARDENING (`H-16`,
`PROJECT/HARDENING_BACKLOG.md`) — không phải BLOCKING, vì không có đường production nào cho
kết quả sai; nhưng cơ chế bảo vệ này dễ vỡ nếu `smartSpacing`/`factorScores` thay đổi độc lập
với nhau trong tương lai (ví dụ thêm fallback spacing).

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

#### CHECK-C1-06 — Bất biến kế toán giữ đúng qua kịch bản đa tháng đầy đủ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `TOTAL = AVAILABLE + RESERVED + DEPLOYED` giữ đúng qua chuỗi fill toàn phần → fill một phần
→ invalidation → release, **trải trên nhiều tháng**; không pool nào âm. Test hiện có mới phủ một
tháng.

Ca kiểm thử mới: `webapp/test_multi_month_invariant.js` — tháng 1 (2026-06): nạp vốn, tạo
ladder cap = 100% Smart available (3.000.000), P2P đổi USDT, fill toàn phần zone 0, fill một
phần zone 1. Sang tháng 2 (2026-07): nạp vốn mới (`currentMonth()` chuyển sang tháng 2).
Invalidation tự động (2 daily close liên tiếp trên invalidation price) → release qua
`releaseLadder()`.

**Bất biến thô `TOTAL(tháng) = A+R+D` (không đổi trừ contribution mới) VÀ "không pool âm" GIỮ
ĐÚNG ở CẢ HAI tháng qua TOÀN BỘ chuỗi** — mọi assertion PASS (script exit code 0). Cụ thể:
tháng 1 giữ nguyên `a+r+d = 3.000.000` từ đầu tới cuối (kể cả sau release); tháng 2 giữ nguyên
`a+r+d` của chính nó không đổi qua bước invalidation/release.

**Nhưng bất biến thô này KHÔNG đủ để phát hiện V-01**: trong lần chạy này, `reserved` còn lại
của tháng 1 sau invalidation (1.755.550 đ, phần chưa fill của zone bị invalidate/cancel)
KHÔNG hề giảm về 0 — nó vẫn cộng đúng vào `TOTAL` tháng 1 (nên phép kiểm tổng không phát hiện
gì bất thường) nhưng về nghiệp vụ là vốn KẸT VĨNH VIỄN, không dùng lại được cho ladder mới.
Nguyên nhân: `releaseLadder()` ghi `take = Math.min(open, m.smart.r)` với `m` = tháng 2 (đang
là `currentMonth()` tại thời điểm invalidation) — tháng 2 có `smart.r = 0` (không có ladder
riêng nào đang reserve ở đó) nên `take = 0`, không gì được release ở CẢ HAI tháng. Kết hợp với
CHECK-C1-03 (ca có tháng đích với `r` > 0, vốn bị chuyển nhầm thay vì kẹt): cùng root cause,
hai hậu quả khác nhau tuỳ trạng thái `reserved` của tháng đang là `currentMonth()` tại thời
điểm release.

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

### Scope / Governance

#### CHECK-C1-07 — Không sửa logic app trong gói này
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh `webapp/app_logic.js` và `webapp/engine.js` không bị sửa. Nếu một
nghi vấn được xác nhận, việc sửa thuộc **T-09A**.

```
$ git diff --stat -- webapp/app_logic.js webapp/engine.js
(rỗng)
```

Không dòng nào trong hai file bị đổi trong suốt phiên, kể cả sau khi V-01/V-02 được XÁC NHẬN
là lỗi thật. Việc vá để **T-09A** (phạm vi đã xác định — xem `PROJECT/PROJECT_PROGRESS.md`
mục T-09A).

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

#### CHECK-C1-08 — Đủ căn cứ để T-03 thoả CHECK-03-01 mà không hạ gate của T-03
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: ba kết luận E1 của CHECK-C1-03/04/05 được ghi vào nơi T-03 viện dẫn được, và
`docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md` được cập nhật trạng thái CHECK-03-01 từ
`BLOCKED` sang `PASS` **dựa trên bằng chứng thật**, không bằng cách sửa nội dung yêu cầu của check.

`docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md` — CHECK-03-01 cập nhật `BLOCKED` → `PASS`,
`E0` → `E1`, Evidence viết lại tóm tắt ba kết luận NV-1/NV-2/NV-3 = V-01/V-02/V-03 kèm tham
chiếu tới CHECK-C1-03/04/05/06 ở đây. Nội dung YÊU CẦU của CHECK-03-01 (tiêu đề, Priority) giữ
nguyên — chỉ Status/Evidence Level/Evidence bị sửa, đúng CHECK-C1-08. Thêm mục "Cập nhật WP-C1"
ở cuối file T-03 (append, không sửa "Kết quả S001" lịch sử). `Status` đầu file T-03 chuyển
`BLOCKED` → `VERIFYING` (gỡ chặn, KHÔNG tự đóng `DONE` — nằm ngoài scope WP-C1, cần phiên
riêng cho T-03 xác nhận đủ Exit Criteria).

Executed By:
Claude (WP-C1, phiên `claude/wp-c1-web-skeleton-b3oieq`)

Timestamp:
2026-09-02 (phiên WP-C1)

## Exit Criteria
- [x] 100% REQUIRED checks PASS — 8/8 (CHECK-C1-01..08)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [x] Ba nghi vấn đều có kết luận dứt khoát — không nghi vấn nào còn ở mức E0
      (V-01 XÁC NHẬN, V-02 XÁC NHẬN, V-03 BÁC BỎ)
- [x] Bộ test webapp chạy được từ checkout sạch
- [x] RSK-003 và RSK-004 được cập nhật trạng thái
- [x] T-03 được cập nhật trạng thái theo bằng chứng thật (CHECK-03-01 PASS, Status → VERIFYING)
- [x] Phạm vi T-09A được xác định (V-01 + V-02 xác nhận → phạm vi vá cụ thể; V-03 bác bỏ →
      không bắt buộc, chỉ hardening tuỳ chọn)
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] Session handoff được viết (mục "Cập nhật WP-C1" cuối file này + Session History trong
      `PROJECT/PROJECT_PROGRESS.md`)
- [x] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- **Xác nhận V-01 hoặc V-02 là lỗi thật → báo chủ dự án NGAY trong phiên.** Nếu app đang được dùng
  để ghi tiền thật thì phải dừng dùng hoặc xuất dữ liệu ra ngoài trước khi tiếp tục. Nâng severity
  lên tối thiểu HIGH.
- Không dựng lại được `live_seed.json` vì dữ liệu nguồn đã mất → `MISSING_INPUT`, BLOCKED, ghi rõ
  thiếu gì. Không tự bịa dữ liệu seed rồi coi test là hợp lệ.
- Ca kiểm thử cho một nghi vấn không dựng được vì kiến trúc app → `VERIFICATION_DEPTH` trước; nếu
  vẫn không được thì ghi `BLOCKED` kèm lý do kỹ thuật. **Không ghi PASS, không ghi "bác bỏ".**
- Phát hiện đường mất dữ liệu không có lối thoát → CRITICAL, báo ngay, liên kết RSK-001 và T-09B.

## Ảnh hưởng nếu gói này thất bại

T-03 giữ nguyên BLOCKED. T-09A không xác định được phạm vi. Quan trọng hơn: **rủi ro sai sổ vốn
thật vẫn ở trạng thái chưa biết** — không phải "không có", mà là "chưa ai kiểm". Với một công cụ
đang được dùng để ghi tiền thật, đó là trạng thái tệ nhất trong ba khả năng.

## Changed Files Registry

Created:
- `webapp/test_v01_v02_v03.js` — ca kiểm thử V-01/V-02/V-03
- `webapp/test_multi_month_invariant.js` — bất biến kế toán đa tháng đầy đủ
- `webapp/package.json`, `webapp/package-lock.json` — ghim `playwright@1.56.1` cho harness
- `demo/results3/live_seed.json` KHÔNG commit (gitignore mặc định của thư mục sinh ra); lệnh
  sinh nó (`ethdca synth` + `ethdca export-live`) ghi trong `webapp/README.md`

Modified:
- `webapp/test_app.js`, `webapp/test_zone.js`, `webapp/build_app.js` — path tương đối theo
  `process.cwd()` → `__dirname` (root cause F-027)
- `webapp/README.md` — hướng dẫn chạy từ checkout sạch, phân biệt DEMO/SYNTHETIC vs REAL/OFFICIAL
- `.gitignore` — `webapp/app_final.html`, `webapp/node_modules/`, `webapp/app-dash.png`,
  `webapp/app-zone.png`
- `docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md` — chỉ cập nhật **trạng thái** của
  CHECK-03-01 kèm bằng chứng (+ `Status` đầu file `BLOCKED`→`VERIFYING`); không sửa nội dung
  yêu cầu của check nào
- `PROJECT/PROJECT_PROGRESS.md` — RSK-003, RSK-004, roadmap table (T-03/WP-C1/T-09A), Session
  History
- `PROJECT/HARDENING_BACKLOG.md` — thêm H-16 (ghi chú kiến trúc cho V-03)

Deleted:
- Không

Migration Impact:
- Không

## Notes

Ghi nhớ nguyên tắc chia việc: gói này **kết luận**, T-09A **sửa**. Trộn hai việc sẽ dẫn tới tình
huống người sửa cũng là người quyết định lỗi có thật hay không — đúng loại thiên lệch mà cả bộ
governance này tồn tại để chặn.

`webapp/test_zone.js` đã chạy được ở S000 và cho kết quả đúng trong kịch bản một tháng. Điều đó là
tin tốt nhưng không phải bằng chứng bác bỏ. Điểm mù của nó — đa tháng — chính là điểm mà V-01 nói
tới.

---

## Kết quả — DONE (2026-09-02)

8/8 REQUIRED check PASS, toàn bộ ở mức E1 (chạy thật, không đọc code suông). Chi tiết đầy đủ
từng check ở trên; tóm tắt:

- **F-027 đóng**: root cause là path tương đối theo `process.cwd()` trong
  `build_app.js`/`test_*.js`, sửa sang `__dirname`. Harness chạy được từ checkout sạch chỉ bằng
  lệnh trong repo (`npm --prefix webapp install` → `ethdca synth`/`export-live` → `node
  webapp/build_app.js` → `npm --prefix webapp test`), xác nhận bằng cách xoá sạch mọi artifact
  rồi làm lại từ đầu.
- **V-01 XÁC NHẬN LÀ LỖI THẬT** — `releaseLadder()` dùng `currentMonth()` thay vì tháng gốc của
  ladder; hậu quả là trả nhầm pool (đánh cắp reserved của ladder khác đang ACTIVE) hoặc kẹt vốn
  vĩnh viễn, tuỳ trạng thái tháng đích tại thời điểm release.
- **V-02 XÁC NHẬN LÀ LỖI THẬT** — `reserveFor()` không nhân giới hạn theo `smartUnlock`/
  `oppUnlock`; reserve được 100% available dù unlock đo được = 0%.
- **V-03 BÁC BỎ** về hành vi quan sát được (mọi trạng thái INVALID dựng được đều bị chặn tạo
  ladder) nhưng chỉ nhờ trùng hợp toán học giữa ngưỡng INVALID và ngưỡng ADR30 trong
  `engine.js`, không do kiểm tra `data_quality` tường minh — ghi H-16 (HARDENING).
- `webapp/app_logic.js` và `webapp/engine.js` **không bị sửa một dòng nào** trong suốt phiên
  (`git diff` rỗng) — đúng ranh giới "kết luận, không vá" của gói này.
- Escalation đã kích hoạt đúng trigger: V-01/V-02 là lỗi thật → nếu app đang ghi tiền thật,
  dừng dùng hoặc xuất dữ liệu ra ngoài cho tới khi **T-09A** (nay `READY`, phạm vi xác định) vá
  xong.
- T-03/CHECK-03-01 chuyển `BLOCKED` → `PASS`; `Status` của T-03 chuyển `BLOCKED` → `VERIFYING`
  (không tự đóng `DONE` — ngoài scope gói này).
- 0 task ID mới, 0 WP mới mở. Không phụ thuộc DATA stream, không chạm `src/eth_dca_os/**`.
