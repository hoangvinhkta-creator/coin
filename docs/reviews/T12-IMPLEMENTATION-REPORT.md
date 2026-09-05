# T-12 Implementation Report — S034

Hiện hành sau DEC-045 và implementation/repair. Phần 1–29 là báo cáo implementation hiện tại;
phụ lục cuối giữ dấu vết hai lần discovery stop. Toàn bộ dữ liệu test là tổng hợp.

## 1. Executive Summary

Đã dựng sổ cái L-1 `coindca.ledger/2` trên đường app hiện có, thay nguồn thật cộng dồn bằng
`openingPosition + plan + events → derive`. 12/12 SC, 15/15 INV, 7/7 mutation bị diệt;
P-1…P-6 PASS trên bundle thật với 10 event được tạo qua UI và server ACK/REST/reload.
Migration W-1 hiển thị UNKNOWN; M-1…M-4 không ghi durable. Một repair cycle DEC-043 đã dùng.

**Trạng thái: IMPLEMENTED + E2_REQUIRED. Full Python regression 678/678 PASS, exit 0.**
Không tự chứng nhận E2, không DONE, không mở quyền ghi tiền thật.

## 2. Source / Branch / Base

Model thực thi: GPT-6 Astra / max theo yêu cầu Owner; cùng phiên S034, nhánh
`codex/t12-l1-ledger-impl`. Base được Owner chỉ định: `7d1985aaf306294df49c9508078d5425da10f47e`.
Mốc đo task: `91cfbba5e3af01d432c64369bb5a286f6461ab6a`.
DEC-045 documentation commit: `2cf0e7c` (không golden). Golden: c610a299ed6b66dea3cd63372a0943967c93e95d.
Repair HEAD: 2a2ab3f52c38eb30a0a8e0ee1791a95254ee9847. Không chuyển nhánh, không đổi main, không đọc `data/`.

Node v24.19.0; Python 3.11.16 trong `.venv`; Chrome hệ thống; Playwright 1.56.1;
Firebase SDK 12.18.0 / CLI 15.28.2 đúng package-lock. JRE Temurin 21 trong /tmp phục vụ emulator.
Không sửa dependency lock. npm ci/JRE download được chạy ngoài sandbox sau lỗi DNS trong sandbox.
Emulator chỉ project `demo-ethdca`, Auth :9099, Firestore :8080. Không Firebase production/deploy.

## 3. Ready Gate

DEC-045 ghi cả Group A và Group B, đúng ID kế tiếp DEC-044. Tái đánh giá 17 prerequisite
hiện hữu **đúng một lần**, 17/17 PASS; ghi tại task §Ready Gate.
`BLOCKED → READY → IN_PROGRESS`; không broad preflight mới.
Routing tính lại D/max (3.1/3.65), không manual override. Quyền persistence = DEC-043;
ngữ nghĩa/oracle = DEC-042/044/045. Dữ liệu Owner không là prerequisite.

## 4. Pre-Implementation Production Map

Trước thay đổi: `build_app.js` ghép shell + Firebase config + ENGINE + app_logic.
`emptyState()` tạo ethdca.tracker/1; addP2P/addBuy/contribution sửa treasury/eth/cost trực tiếp;
UI cũ gắn zone/ladder/score. `initPersistence()` đọc server, `persist()` transaction kiểm rev
trước tx.set vào ethdca/state, localStorage chỉ mirror. Import/wipe thiếu snapshot.

Sau thay đổi: bundle thêm ledger.js và ledger_ui.js. app_logic khởi tạo L-1, validate trước
nhận nguồn bền, render adapter L-1, giữ nguyên transaction/rev/ACK/retry. Những handler tài chính
legacy bị khóa, render/recompute chiến lược không còn đường vào L-1. Mã legacy giữ làm lịch sử,
không được dùng để tạo truth mới hay giữ test cũ xanh.

## 5. Capability Boundary

Chỉ T-12 / CAP-WEBAPP, lineage root WP-C1; không task/capability mới.
Hai module mới khai trong PROJECT/PRODUCTION_PATHS.md. Không đổi engine.js, src/eth_dca_os,
docs/spec, pyproject*, Firebase config/rules/hosting/auth. Kế hoạch hoàn toàn từ Owner; không
Research/Buy Score, notification, projection hay residual account ẩn. Adapter dùng class CSS
hiện hữu, chỉ thêm các trường nghiệp vụ cần thiết; không thi hành bước B/C/D của L-1.

## 6. Change Budget

Task cap +1600/-450, tối đa 7 production file. Đo từ 91cfbba bằng danh sách production đã khai,
không tính test/docs/build artifact. Production thực tế 5 file, +460/-7.
Diff chi tiết §24; không CHANGE_BUDGET_EXCEEDED. Không dùng golden kế toán làm mốc đo budget.
CAP-WEBAPP allowed2/used1/remaining1; T-12 chỉ được dùng 1 chu kỳ theo DEC-043, nay đã dùng.

## 7. Implemented Data Model

`schema, rev, nextSeq, plan, openingPosition, events` là durable L-1. `nextSeq` chỉ cấp thứ tự,
không là tiền; edit giữ id/seq/createdAt, delete không hạ watermark, create dùng UUID.
Event allowlist TREASURY/TRADE/RESERVE/PRICE; opening và event có validator riêng.
VND nguyên, micro-USDT, ETH 1e-8; giới hạn 9×10^15. Payload dư field hoặc kiểu sai bị từ chối;
`derivedSnapshot` bị bỏ. Legacy archive/RESEARCH_ONLY được giữ có nhãn, không được derive đọc.

## 8. derive() Semantics

Hàm thuần nhận opening, plan, events, asOfDate; clone/sort businessDate+seq, không mutate input,
không đồng hồ hay ENGINE. Replay một lượt cho quantities/cost/eventEffects; kế hoạch tính riêng
từ relief của các BUY theo tháng. Holdings có cả future event; tháng hiện tại không lấy khóa
tháng lớn nhất. Derived có exact ratios numerator/denominator dạng chuỗi BigInt; UI mới chuyển
sang thập phân để hiển thị. Không average float làm thẩm quyền.

## 9. USDT WAC / VND Cost Basis

Relief = ROUND_VND(out×cost/qty) bằng BigInt trung gian, round-half-up tất định. Phí BUY vào
out và hai cost basis; SELL ETH giảm cost theo tỷ lệ, USDT nhận về nhập pool theo WAC hiện có;
pool rỗng không bịa basis. USDT_TO_VND giải phóng WAC và tính realizedFxVnd dẫn xuất.
Full drain ép cost về0; conservation và ROUND được kiểm cả pool3USDT/cost10VND.
SC-04 giữ relief12.909.178, qty599,4USDT/cost15.475.522VND; average sau ROUND lấy đúng hai số dư
theo DEC-045, không ép tỷ số cũ bằng tolerance.

## 10. UNKNOWN Semantics

`null` là UNKNOWN, hiển thị `—`; cộng/trừ với UNKNOWN tiếp tục UNKNOWN. Thiếu basis USDT
không đổi lượng/giá vốn USDT của ETH. Prefix thiếu USDT ghi LEDGER_INCONSISTENT + id/ngày đầu
tiên dù inflow muộn làm số dư cuối dương. Reserve rút âm cũng có cờ. Không event bù, không
FX riêng per-trade, không đọc PRICE để sửa cost. Báo cáo W-1 liệt kê chỉ số legacy, lý do
USDT basis thiếu và đường sửa openingPosition.usdt.costVnd hoặc TREASURY còn thiếu.

## 11. Date / Month / Ordering

Một clock L-1 trả instant metadata và today Asia/Ho_Chi_Minh; derive không hỏi giờ.
Ngày nghiệp vụ dùng chuỗi và slice; calendar tháng/leap day viết bằng số nguyên. 150 hoán vị
và hai process TZ UTC/America/Los_Angeles cho output bằng nhau. SC-08 qua instant UTC sang
01/03. Carry chỉ chốt tháng đóng; SC-09/10 cùng ledger đánh giá A trong tháng3 và B ngày01/04.
Schedule cũ không sửa hồi tố; version mới áp dụng từ tháng thay đổi trở đi. Split80 ngân sách
×n1..12 bảo toàn tuyệt đối, phần cuối nhận dư.

## 12. Edit / Delete / Late Entry

UI có businessDate, opening, loại event, BUY/SELL, source, note RESERVE. Mọi edit/delete thay
source và replay; 20edit giữ identity và createdAt, updatedAt thay đổi. Delete/create không
reuse seq/id. Opening boundary được kiểm trước lưu. P-3 có sửa qty, xóa một P2P, nhập muộn;
server/reload khớp oracle tính tay, không phép hoàn tác incremental. Snapshot trước delete và
xóa opening; form opening/plan nạp đúng giá trị hiện hữu sau reload.

## 13. Migration

Legacy chỉ đọc khi nạp. Người dùng xác nhận ngày/thứ tự từng dòng, contribution đưa vào opening
VND hoặc bỏ; không suy businessDate từ ts. P2P cộng/trừ fee thành hai chân actual; trade legacy
luôn EXTRA, bỏ rate/vndCost/recPrice/zone. Đối chiếu ETH,USDT,VND,costUsdt theo §17.3 và ghi
float delta; costVnd chỉ báo chênh, không chặn. M1 thiếu xác nhận; M2 prefix âm lượng; M3 lệch
oracle; M4 filled zone: không ghi. W1 hoàn tất có UNKNOWN và báo cáo từng dòng. Toàn bộ raw
legacy giữ trong LEGACY_ARCHIVE và snapshot; extraDays/seed.history RESEARCH_ONLY không chạm tiền.

## 14. Persistence

Giữ ethdca/state và transaction revision hiện hữu. Schema detect tất định; canonical + derive
được kiểm trước nhận/lưu để không mutate state khi source không thể replay. Snapshot JSON đầy
đủ gồm state/seed, lưu local và tải xuống trước confirm/import/wipe/migration/delete. Hủy/lỗi
không ghi; storage snapshot lỗi thì dừng trước mutation.
Server ACK mỗi thao tác, REST độc lập bit-exact; reload + same-profile Chrome restart giữ sổ.
Đã kiểm reject/retry, offline mirror read-only, stale rev không đè server, corrupt schema khóa
ghi và export raw. Không triển khai persistence production H-42.

## 15. T12 Golden Accounting Baseline

T12_GOLDEN_ACCOUNTING_BASELINE_SHA = `c610a299ed6b66dea3cd63372a0943967c93e95d`.
Fixture: webapp/test_t12_fixtures.js, đủ SC-01…SC-12, inputs/expected tách khỏi ledger.js.
SHA256 file = `067de9228e8230cf38f2363f0cb40a8f2e2f7a3b0e77ce0439b9f6a125583509`.
Không thay fixture sau freeze; SC-04 theo DEC-044/045, SC-09/10 có hai evaluation.
T12_MEASURE_BASE_SHA và GOLDEN_BASELINE_SHA research V2.1.5 không bị đổi tên/thay thế.
OWNER_LOCAL_ACCEPTANCE có schema + ví dụ tổng hợp + runner chỉ in PASS/FAIL; chưa chạy dữ liệu
Owner. private/ đã ignore. Đây không là A-5 acceptance của Owner.

## 16. SC-01…SC-12 Results

| SC | Kết quả E1 | Oracle nổi bật |
|---|---|---|
| SC-01 | PASS | opening ETH0,5, costUSDT1200, costVND30m; pool200/5m |
| SC-02 | PASS | pool1200/cost30,6m; không đầu tư |
| SC-03 | PASS | relief15.315.300; ETH0,75; pool599,4/cost15.284.700 |
| SC-04 | PASS | relief12.909.178; remaining11.775.522; exact post-round ratio |
| SC-05 | PASS | edit qty0,24 → tổng ETH0,94; cost không trôi |
| SC-06 | PASS | delete P2P → relief12.750.000, pool99,4/cost2.534.700 |
| SC-07 | PASS | nhập muộn04/02 đứng trước05/02; invested15.491.014 |
| SC-08 | PASS | UTC28/02 18:30 → today01/03, carry tháng2 đã đóng |
| SC-09 | PASS A+B | invested17m/plan12m/remain8m; A chưa carryOut, B carry8m |
| SC-10 | PASS A+B | reserve6m/invested21m/plan12m; A chưa carryOut, B carry8m |
| SC-11 | PASS | future holdings, tháng hiện tại không lấy kế hoạch tháng4 |
| SC-12 | PASS | migration W1, lượng/USDT cost đúng, VND UNKNOWN, raw giữ nguyên |

Log: evidence/T12/unit.txt. Tolerance integer=0, ratio so tích chéo BigInt, không epsilon.

## 17. INV-1…INV-15 Coverage

Mỗi INV có test đích danh trong webapp/test_t12_ledger.js (32 test gồm12 SC+15 INV+5 bổ sung):
INV1 allowlist/import snapshot; INV2 150permutations+2TZ; INV3 drain/SELL/round/conservation;
INV4 first prefix deficit/reserve; INV5 integer/range; INV6 metadata; INV7 opening boundary;
INV8 P2P isolation; INV9 EXTRA/RESERVE plan/carry isolation; INV10 PRICE/noENGINE; INV11 UNKNOWN;
INV12 M1…M4 atomicity; INV13 80×12split; INV14 snapshot before accept/cancel/fail; INV15 identity.
Tất cả PASS E1; INV12/14 còn có REST production-harness evidence. E2 chưa thực hiện.

## 18. Mutation Evidence

webapp/test_t12_mutations.js sửa **source production thật** trong module tạm, chạy test chống
lại mutant, kiểm exit1 và AssertionError; production working tree không bị mutation.
7 KILLED / 0 SURVIVED: INV1 thêm durable costVnd; INV3 floor thay ROUND; INV4 bỏ deficit flag;
INV9 EXTRA/RESERVE vào plan; INV11 UNKNOWN→0; INV12 ghi khi migrationfail; INV14 bỏ snapshot.
Log evidence/T12/mutations.json chứa exact from/to và assertion thất bại.

## 19. Production Reachability P-1…P-6

webapp/test_t12_browser.js: app_final thật, SDK thật qua harness hiện có, Firestore emulator
rules từ repo (chỉ thay UID trong bộ nhớ emulator). 10 event tạo bằng UI, không Node gọi update
thay đường app; Node derive chỉ đối chứng read-only bên cạnh oracle tính tay và DOM.
Opening +2 P2P+2 PLAN+EXTRA+RESERVEcontribution+RESERVEbuy+PRICE; sửa/xóa/nhập muộn qua UI.

Oracle cuối: ETH1,04; costUSDT2.550,6; costVND64.351.292; USDT249,4/cost6.248.708;
reserve7.494.504; tháng3 budget20m/carry10.659.700/planned30.659.700/invested5.010.992/plan0;
remaining30.659.700; next23/03 amount20m.
Tính tay: pool sau SC0325.500VND/USDT; sau xóa P2P và lateBUY50, FebBUY500 giải phóng
1.275.000 và12.750.000. Pool tháng3 trước hai BUY100 =449,4USDT/cost11.259.700; mỗi relief
2.505.496. Harness ban đầu nhầm25.000; đã sửa oracle **harness mới**, không đổi SC golden/code.

P1…P6 PASS; 17 nhóm kiểm trình duyệt PASS, 0 page error; log evidence/T12/browser.txt.

## 20. Full Regression

Python trước: 678/678 PASS trong baseline canonical WP-B2 (report §16, 1153,20s);
Python source/tests/lock không đổi trong T-12. Lần chạy hiện tại collected 678, passed 678 / failed 0 / errors 0 / skipped 0 / xfail 0 / xpass 0, exit 0.
Lần thử đầu thiếu PYTHONPATH gây34collection errors (exit2); đã sửa môi trường bằng PYTHONPATH=src,
không sửa test/module. Không deselect/skip/xfail thêm. Bằng chứng: evidence/T12/python.txt, python-result.json và python-collected.txt.
Runner chạy double quiet nên không in dòng summary; 678 dấu PASS khớp 678 ca collected, exit 0.

Npm trước: xuất source7d1985a vào /tmp, cùng dependency/Chrome/emulator, npmtest chạy nguyên chuỗi
6 script, exit0. T09A68 assertions/0 fail; T09B285 assertions/14 check/0 fail/0 page error. Các script
không công bố tổng assertion không được tự suy thành số ca PASS; smoke/zone/v01/multi exit0.
Log evidence/T12/npm-before.txt.

Npm sau: npmtest exit1 tại seed legacy; sau đó chạy độc lập đủ6 script, cả6 exit1 ở tiền đề
seed/luồng cũ, không timeout/deselect/skip. Không gọi đây là suite xanh. Npm không là pytest
nên collected/pass/skip kiểu pytest = không được runner công bố. Chi tiết từng command/exit
ở evidence/T12/npm-after.json và npm-after-0…6.txt.
Các mục không còn áp dụng được liệt kê dưới đây; semantics persistence vẫn áp dụng đã chuyển
bằng chứng sang harness L-1, không gán N/A cho toàn bộ T09B.

### Từng ca NOT_APPLICABLE theo DEC-041 B/F/K.2, DEC-042 §3/4, spec §17.2

| File / ca cũ | Phần NOT_APPLICABLE | Phần còn áp dụng / evidence L-1 |
|---|---|---|
| test_app.js bước1 | seed→OSCORE/parity UI | SDK/server init: P1/P4 |
| test_app.js bước1b | Smart unlock bằng12ngày giá | INV10 không tín hiệu |
| test_app.js bước2 | contribution chia Base/Smart/Opp | opening+reserve explicit P2 |
| test_app.js bước4 | tạo Smart ladder | cấm trong L-1, CHECK14 |
| test_app.js bước5 | recPrice/per-trade vndRate định giá vốn | BUY thật: SC03/P2 |
| test_app.js bước6 | actionBox khuyến nghị V2.1.5 | dashboard holdings/treasury P5 |
| test_app.js bước7 | bất biến pool Base/Smart/Opp | INV3/4/7 và REST P4 |
| test_zone.js ca fill đầy zone0 | trạng thái EXECUTED và Smart reserve | BUY ledger SC03 |
| test_zone.js ca partial zone1 | PARTIALLY_FILLED | lượng ETH thực nhận ở schema |
| test_zone.js ca invalidation |2close→hủy ladder/release | không có hành động tín hiệu |
| test_v01_v02_v03.js V-01 | release đa tháng về pool chủ ladder | ledger replay SC05…07 |
| test_v01_v02_v03.js V-02 | unlock giới hạn reserve | reserve manual INV9/10 |
| test_v01_v02_v03.js V-03 | INVALID chặn tạo ladder | cấm ladder L-1 |
| test_multi_month_invariant.js ca đa tháng | A/R/D, fill0/1, invalidation trả pool tháng1 | monthly carry và source isolation SC09/10 |
| test_t09a_accounting.js CA1 | release đa tháng/active backing/upper bound | ledger conservation INV3 |
| test_t09a_accounting.js CA2 | fill zone khi currentMonth đổi | businessDate/month SC07/08/11 |
| test_t09a_accounting.js CA3a | unlock0 từ chối reserve | reserve không nhận tín hiệu |
| test_t09a_accounting.js CA3b | biên unlock cục bộ | reserve không nhận tín hiệu |
| test_t09a_accounting.js CA4 | sạch một tháng với ladder/full/partial/release | P2…P5 L-1 |
| test_t09b_persistence.js CHECK07 | pools/release/A+R+D | INV3/4, reserve source event round-trip |
| test_t09b_persistence.js CHECK08 | active ladders/zones/month | migration M4 + archive |
| test_t09b_persistence.js CHECK15 | ladder thiếu month/backfill/banner suy luận | legacy raw giữ nguyên, không tham gia tiền |

22 dòng N/A có phạm vi cụ thể; không N/A cả file. Các bước test_app3(P2P),8(history),9(reload),
10(noembeddedstate) vẫn áp dụng: P2/P3/P5/build guard. T09B01/02/03/04/05/06/10/11/12/14/16
vẫn áp dụng theo schema mới: serverACK/REST, rawsourcehistory, reload, clear mirror trong
migration test, browser restart, reject/retry, offline, unrecognized init, corrupt/schema,
workflow UI và stale rev. T09B09/13 là integration accounting/full-suite: SC/INV và bảng này.
Không thay đổi bất kỳ test legacy/Python nào; 0 skip/deselect thêm.

## 21. Frozen Completion Gate Matrix

E1 đã ghi dưới từng check; trạng thái E2_REQUIRED giữ đúng 9 check độc lập, không tự PASS E2.
Exact requirement bên dưới trích từ task hiện hành sau DEC-044/045, không viết lại cho mã.

### CHECK-T12-01 — Schema L-1 canonical, không rò rỉ sự thật chiến lược legacy

Yêu cầu: durable state mang `schema = "coindca.ledger/2"`; chứa đúng `plan`, `openingPosition`,
`events[]` theo §5; **không** chứa `months[].base/smart/oppAdded/oppOverflow`, `oppFund`,
`ladders`, `zones`, `trades[].src ∈ {BASE,SMART,OPPORTUNITY}`, `recPrice`, `shortfallBps`,
`zone` như dữ liệu tài chính. `ledger[]` legacy nếu giữ thì mang nhãn `LEGACY_ARCHIVE` và
không phép dẫn xuất nào đọc. Bằng chứng: quét khoá trên payload durable thật + danh sách khoá bị
cấm.

Evidence level: E1. Implementation evidence: ledger.canonical + INV1/5 + P6.
Trạng thái: **PASS**.

### CHECK-T12-02 — `openingPosition + events -> derive()` tất định

Yêu cầu: `derive()` là hàm thuần (không `new Date()` bên trong, không đọc `createdAt`), cùng
tập event cho cùng `DerivedState` dưới ≥ 100 hoán vị thứ tự nhập và ≥ 2 `TZ` tiến trình khác
nhau. Phủ `INV-2`, `INV-6`. Golden: `SC-04`, `SC-07`, `SC-08`.

Evidence level: E1 + independent E2. Implementation evidence: SC01…12, INV2/6; unit.txt.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-03 — Giá vốn VND: WAC trên một pool USDT, đúng số

Yêu cầu: `vndRelieved = ROUND_VND(usdtOut × usdtCostVnd / usdtQty)`; giải phóng theo bình quân
giữ bình quân lý thuyết **trước** lượng tử VND. Sau ROUND_VND, bình quân dẫn xuất từ
`(C − vndRelieved) / (Q − usdtOut)`; chênh tỷ số chỉ do phép làm tròn tất định (DEC-045),
không lưu bình quân cũ, không phần dư ẩn, không tolerance bổ sung; phí USDT vào cả hai giá vốn; bán crypto/bán USDT giải phóng theo
cùng phương pháp; cạn pool ép `usdtCostVnd = 0` và đẩy phần dư vào `realizedFxVnd`. Số kỳ vọng
đối chiếu **tuyệt đối** (`tolerance = 0`) với `SC-01`…`SC-04`, `SC-06`. Phủ `INV-3`.

Evidence level: E1 + independent E2. Implementation evidence: SC01…04/06, INV3; exact ratio+BigInt; unit.txt.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-04 — `UNKNOWN` lan truyền thấy được, không bao giờ bị ép về 0

Yêu cầu: `openingPosition.usdt.costVnd = null` (và phần USDT thiếu phủ của §8.4) → `qty` và
`costUsdt` giữ nguyên đúng, phần `costVnd` liên quan = `UNKNOWN`, hiển thị `—`, cờ
`UNKNOWN_VND_BASIS` thường trực và **không ẩn được bằng một lần bấm**. Grep schema chứng minh
**không tồn tại** trường tỷ giá nhập theo từng lệnh (`vndRateOverride` hoặc tương đương).
Phủ `INV-11`. Golden: `SC-12`.

Evidence level: E1 + independent E2. Implementation evidence: SC12, INV11, UNKNOWN UI; browser.txt.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-05 — Sửa / xoá / nhập muộn tính lại đúng, không trôi

Yêu cầu: sửa giữ `id`+`seq`, cập nhật `updatedAt`, chạy lại toàn bộ; **không tồn tại** phép
"hoàn tác tác động cũ" trong mã; xoá cứng TƯƠNG ĐƯƠNG CHÍNH XÁC với chưa từng nhập; nhập muộn
được xếp theo `businessDate` chứ không theo lúc nhập. Phủ `INV-1`, `INV-15`. Golden: `SC-05`,
`SC-06`, `SC-07`.

Evidence level: E1 + independent E2. Implementation evidence: SC05/06/07, INV15 và P3/P5; unit/browser.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-06 — Ngày nghiệp vụ, `Asia/Ho_Chi_Minh`, tháng lịch

Yêu cầu: `businessDate` là chuỗi, so sánh chuỗi, `month = slice(0,7)`; **đúng một** chỗ trong
toàn bộ mã hỏi giờ hệ thống và nó trả ngày theo `Asia/Ho_Chi_Minh`; `currentMonth` = tháng của
`asOfDate`, KHÔNG phải khoá tháng lớn nhất trong dữ liệu; `carryOut` chỉ chốt cho tháng đã đóng.
Bằng chứng gồm grep chứng minh không còn `getMonth()`/`toISOString()` trong đường tính tiền.
Phủ `INV-6`. Golden: `SC-08`, `SC-11`. Đóng `B3`, `B4`, `B7` của `H-41`.

Evidence level: E1 + independent E2. Implementation evidence: SC08/09/10/11, INV6 và version schedule test; unit.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-07 — Số nguyên VND, làm tròn đối chiếu được, thứ tự tất định

Yêu cầu: quét đệ quy payload durable — 0 giá trị float ở trường tiền/lượng; `SPLIT_VND(x, n)`
với `n = 1..12` trên ≥ 50 giá trị: `Σ phần == x` tuyệt đối; `ORDER = (businessDate ASC, seq ASC)`
được kiểm bằng test. Phủ `INV-5`, `INV-13`. Đóng `B9`.

Evidence level: E1. Implementation evidence: INV5/13; 80×12split; P6 canonical payload.
Trạng thái: **PASS**.

### CHECK-T12-08 — `SC-01`…`SC-12` PASS trên dữ liệu tổng hợp

Yêu cầu: **12/12** golden scenario của spec §19 chạy được và PASS, đối chiếu tuyệt đối với số
kỳ vọng đã đóng băng ở spec (không nới `tolerance`, không làm tròn để khớp). Báo cáo phải in
bảng SC × (kỳ vọng / thực tế). Ngữ nghĩa và số kỳ vọng của SC **không được viết lại**.

Evidence level: E1. Implementation evidence: 12/12 SC, golden SHA bất biến; unit.txt.
Trạng thái: **PASS**.

### CHECK-T12-09 — `INV-1`…`INV-15` được phủ, không bất biến REQUIRED nào bỏ trống

Yêu cầu: mỗi dòng của ma trận `INV` ở trên có **ít nhất một test nhắm đích** thực sự đỏ khi bất
biến bị phá (chứng minh bằng mutation/nghịch đảo có chủ đích cho tối thiểu `INV-1`, `INV-3`,
`INV-4`, `INV-9`, `INV-11`, `INV-12`, `INV-14`). Không được để một `INV` chỉ "được phủ gián
tiếp" bởi một SC mà không có phép khẳng định trực tiếp.

Evidence level: E1 + independent E2. Implementation evidence: 15/15 INV +7KILLED; mutations.json.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-10 — Hợp đồng migration PASS, gồm dữ liệu mơ hồ

Yêu cầu, trên fixture legacy **tổng hợp**:
(a) snapshot legacy được ghi TRƯỚC mọi thao tác ghi (`INV-14`);
(b) phát hiện version tất định;
(c) phân loại §17.2 áp đúng cho từng trường; `trades[].vndRate/vndCost` bị bỏ và tính lại;
(d) đối chiếu §17.3 trong ngưỡng; vượt ngưỡng ⇒ FAIL migration (kiểm bằng một fixture cố ý lệch);
(e) `M-1`…`M-4` ⇒ **DỪNG, durable không đổi một byte** (`INV-12`);
(f) `W-1` ⇒ **HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`**, không bịa tỷ giá (`SC-12`);
(g) dữ liệu legacy không bị xoá; `ledger[]` chỉ đọc;
(h) không `Base`/`Smart`/`Opportunity`/`ladder`/`zone`/`score` nào lọt vào sự thật tài chính L-1.

Evidence level: E1 + independent E2. Implementation evidence: migration M1…M4 và W1; unit + serverREST browser.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-11 — Round-trip persistence giữ nguyên sự thật sổ cái

Yêu cầu: ghi → máy chủ xác nhận → đọc lại từ SERVER → `derive()` cho `DerivedState` **trùng
tuyệt đối**; payload durable không chứa khoá dẫn xuất bị cấm (`INV-1`); nếu file export có khối
`derivedSnapshot` thì import **bỏ qua** khối đó (kiểm bằng file export bị sửa tay). Sổ nằm trong
document `ethdca/state` đã được `firestore.rules` allow-list — **không** tạo document mới.

Evidence level: E1 + independent E2. Implementation evidence: P4/P5/P6, snapshot/ACK/reload/restart/reject/corrupt; browser.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-12 — Production Reachability PASS

Yêu cầu: `P-1`…`P-6` của § Production Reachability, đo trên `app_final.html` đã build qua
`webapp/test_firebase_harness.js` (Playwright + Firestore Emulator + rules thật). Báo cáo phải
nêu **số event thật** và **số case** đã chạy qua đường production. `0 event / 0 case = FAIL`.
Mọi file runtime MỚI được khai vào `PROJECT/PRODUCTION_PATHS.md` §1 (khiếm khuyết `H-32` không
được lặp lại).

Evidence level: E1 + independent E2. Implementation evidence: P1…P6,10 event UI +17 nhóm browser.
Trạng thái: **E2_REQUIRED** (E1 PASS, E2 chưa thực hiện).

### CHECK-T12-13 — Regression áp dụng được PASS, không test nào bị làm yếu

Yêu cầu: chạy đủ suite áp dụng được (`webapp/`: `npm test`; Python: `pytest`) và báo cáo con số
trước/sau. Test cũ mô tả hành vi **đã bị `DEC-041`/`DEC-042` gỡ bỏ** (ladder/zone/pool
Base-Smart-Opportunity) chỉ được đánh dấu `NOT_APPLICABLE` kèm neo quyết định tường minh, từng
file, từng ca — **không** được xoá/skip/deselect hàng loạt để lấy suite xanh, và số ca
`NOT_APPLICABLE` phải được liệt kê đích danh trong báo cáo. Không test nào của `src/eth_dca_os`
được đổi.

Evidence level: E1. Implementation evidence: npm before/after +22 dòngN/A; Python 678/678 PASS.
Trạng thái: **PASS**.

### CHECK-T12-14 — Không hồi quy productization chiến lược

Yêu cầu: Buy Score / OSCORE / regime / crash / ladder / recommendation **không** nằm trên đường
quyết định tài chính L-1: (a) module sổ cái không tham chiếu `ENGINE`/`engine.js`; (b) đổi tuỳ ý
dữ liệu chỉ báo và event `PRICE` → phần tiền của `DerivedState` **không đổi**; (c) không tín
hiệu nào tạo/gợi ý/định cỡ một `TRADE`, đặc biệt `source = RESERVE` (bắt buộc có `note` do người
dùng nhập). Phủ `INV-10`. Neo: `DEC-041` B, `DEC-042` §3, spec §12.3.

Evidence level: E1. Implementation evidence: INV10; dead legacy write/render paths; engine diff0.
Trạng thái: **PASS**.

## 22. Repair Cycle

REPAIR_CYCLE_1 = CONSUMED, đúng DEC-043. BASE `c610a299ed6b66dea3cd63372a0943967c93e95d`; HEAD `2a2ab3f52c38eb30a0a8e0ee1791a95254ee9847`.
Trigger: CHECK06 cho phép sửa schedule version lịch cũ; CHECK10 thiếu dòng legacy/lý do/
correction trong report UNKNOWN. Test đỏ29pass/2fail trước sửa ở pre-repair.txt; sau sửa32/32.
Cùng batch bổ sung adapter: report W1 hiển thị từng dòng, form nạp source hiện hữu, dùng class
CSS sẵn có; validate replay trước gán state. Không task mới, không phạm vi tiền/kiến trúc mới,
không golden change, không làm yếu test. Repair diff3 production files, +44/-15.
Không cấp chu kỳ thứ hai. CAP-WEBAPP2/1/1; DEC044/045 không tiêu repair.

## 23. Findings / Hardening

Hai defect implementation trong repair đã đóng bằng test. Không BLOCKING đã biết còn mở
; independent E2 vẫn chưa thực hiện. H-41: B1/B2 đóng bằng kiến trúc không có ladder/pool L-1;
B3…B9 có evidence StepA; H-41 chưa đóng lifecycle vì E2/T12DONE chưa có; B10 giữ re-triggerH43.
H-42/R1…R5 và A5 Owner acceptance vẫn ngoài task, không mở quyền dùng tiền thật. H-08 validator
globTASK-* còn vacuous; H-22 task_registry snapshot chưa đếm IMPLEMENTED: ghi hạn chế, không vá.
Không tạo H/task ID mới cho defect đang nằm trong batch; không dùng findings để reset budget.

## 24. Production Diff

Lệnh có thể chạy lại:

```sh
git diff --numstat 91cfbba5e3af01d432c64369bb5a286f6461ab6a..HEAD -- \
  webapp/app_logic.js webapp/app_shell.html webapp/build_app.js webapp/ledger.js webapp/ledger_ui.js
```

```text
28	7	webapp/app_logic.js
1	0	webapp/app_shell.html
4	0	webapp/build_app.js
298	0	webapp/ledger.js
129	0	webapp/ledger_ui.js
```

5 file production, +460/-7, dưới cap +1600/-450/7file. src/eth_dca_os, engine.js, docs/spec,
Firebase/auth/rules/config/hosting và dependency locks diff0. Build outputs/deps/logsignored
không là thay đổi source. Test/fixtures mới nằm ngoài production path, không tráo phân loại.

## 25. Files Changed

Production5 file: app_logic.js, app_shell.html, build_app.js, ledger.js, ledger_ui.js.
Test5 file mới: test_t12_fixtures.js, test_t12_ledger.js, test_t12_mutations.js,
test_t12_browser.js, test_t12_owner.js. Hai JSON schema/example ở tests/fixtures/t12;
.gitignore thêm private/ theo spec22.1. Không sửa test Python/legacy.
Canonical: DEC045 + specL1/CHECK03/SC09/10; PROJECT progress/capability/productionpaths/budget/
hardening/derivedroadmap; taskT12; cùng report và sessionS034. Rawtestlogs ở evidence/T12.

## 26. Validators

structure PASS (27 paths), project_state PASS, governance PASS (7CORE/7PROJECT/23task),
routing PASS (20MAJOR/0override), easy_roadmap PASS. evidence/task_completion in PASS nhưng
quét 0 record (H-08); không là evidence T12. Branch Authority sau fetch PASS: behind0,
INTEGRATION_DECISION_REQUIRED=NO. Registry23taskfile/30roadmapIDs; không task mới.
Log: evidence/T12/validators.json, routing.txt, task-registry.txt. Chạy structure/project_state/governance/routing/easy_roadmap/evidence/
task_completion, Branch Authority và registry snapshot trước/final. Hai script evidence/task
completion globTASK-* không đọc task thật: PASS tự in không được dùng chứng nhận T12.
Kiểm riêng14 check tồn tại, E2surface9 check và fixtureSHA không đổi.

## 27. Lifecycle State

T-12: BLOCKED → READY → IN_PROGRESS → **IMPLEMENTED**. Ready Gate 17/17;
E1 của cả 14 check hoàn tất, regression áp dụng được PASS. Completion matrix: 5 PASS +
9 E2_REQUIRED; không DONE, không GOLDEN_PASS thay cho E2.
Không còn implementation work được mở trong phiên này; independent E2 là evidence còn thiếu.

## 28. Independent E2 Required

Bắt buộc reviewer ở phiên độc lập, từ repo hiện hành: CHECK02/03/04/05/06/09/10/11/12.
Phủ8 nhóm đối kháng nguyên bản: WAC/drain/round/SELL; UNKNOWN/noFX; edit/delete/late; timezone/
month; M1…M4/W1/atomic; persistence/export tampered; P1…P6; malformed/missing/range.
Implementer không tự ký E2; 5 check chỉ cầnE1 không làm giảm thẩm quyền của9 check kia.

## 29. Exact Next Action

Reviewer độc lập chạy lại implementation từ `2a2ab3f52c38eb30a0a8e0ee1791a95254ee9847` và golden `c610a299ed6b66dea3cd63372a0943967c93e95d`;
chỉ Owner có quyền IMPLEMENTED→DONE khi gate/evidence đủ. Không cần dữ liệu Owner cho E2
tổng hợp. Không cấp tiếp repair thứ hai; cần Owner Decision nếu ngoài quyền DEC043.
Commit/push chỉ codex/t12-l1-ledger-impl; không main, không deploy. Commit báo cáo cuối
được xác định qua `git log -1` của nhánh, production HEAD giữ `2a2ab3f`.

## Phụ lục — lịch sử discovery stop trước implementation

- S034 tại2642c8e: chưa production/fixture/golden; SC04 remaining7.090.822 mâu thuẫn
  CAPPED_CARRY11.775.522; BLOCKED/OWNER_DECISION_REQUIRED, repairNOT_CONSUMED.
- DEC044 tại8407735: sửa carrySC04; một preflight đủ12 SC cho9CONSISTENT/3CONTRACT_CONFLICT,
  gom GroupA WAC quantization và GroupB SC09/10closedmonth; chưa implementation/golden.
- DEC045 tại2cf0e7c: Owner duyệt cả hai; integeroracle/tolerance0 không đổi;
  ReadyGate tái đánh giá đúng1lần17/17, BLOCKED→READY→IN_PROGRESS, không preflight khác.
Chi tiết bản ghi gốc được bảo toàn ở lịch sử git của chính report và sessionS034; các quyết
định Owner append-only tại PROJECT_DECISIONS.md.
