# WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp

## Metadata
Status:
VERIFYING

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 4
R: 4
B: 3
A: 3
X: 3
U: 3
V: 4
H: 4
C: 3
F: 4

Routing Categories:
accounting_financial

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.5

Effort Routing Score:
3.65

Applied Model Floor:
cognitive:A>=3&X>=3, cognitive:D>=4&X>=3, safety_business:min_C

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
4/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Đóng vòng đời của trạng thái thị trường và của Crash ladder sao cho **không còn đường nào khoá vốn
vĩnh viễn**, và sao cho nhãn dẫn xuất STRESSED không còn tạo ra hiệu ứng thực thi mà Strategy §17.3
[F1] cấm tuyệt đối.

Đây là gói **duy nhất trong lớp A làm đổi kết quả mô phỏng**. Vì vậy nó phải chứng minh cả hai
chiều: hành vi mới đúng spec, **và** mức thay đổi kết quả được định lượng chứ không bị che đi.

## Vì sao gói này nằm trên đường găng

Khi giai đoạn RECOVERY kết thúc lúc thị trường còn yếu, `RegimeTracker.update` đặt regime về NORMAL
rồi đánh giá lại nhãn STRESSED và ghi đè thành STRESSED. Nhánh dọn Crash ladder ở `engine.py:415`
so khớp `regime == "NORMAL"` nên **không bao giờ chạy**. Crash ladder có `expires_at = None` và
nhánh expiry chỉ xử lý OPPORTUNITY — không còn đường nào khác giải phóng reserve.

Hệ quả dây chuyền: `smart_reservable` và `opportunity_reservable` trừ `reserved` khỏi hạn mức nên
**ladder mới không được tạo nữa**, cash ratio tăng giả tạo, AccumulationEfficiency giảm. FS-07 dùng
`avg_cash_ratio` và FS-02 dùng cap-hit share, nên lỗi này **bóp méo chính các Failure Signal dùng để
kết luận verdict**. Đó là lý do WP-A5 (đo lường) phụ thuộc gói này: đo trên một engine còn khoá vốn
sẽ cho số sai lệch.

Kịch bản kích hoạt — sập sâu, hồi một phần, rồi vẫn yếu — là kịch bản thường gặp trong crypto, không
phải trường hợp biên hiếm.

## Đóng finding / risk

- F-001 — reserve của Crash ladder không bao giờ được giải phóng khi Recovery kết thúc vào STRESSED
- F-021 — snapshot eligible capital [F5] bị thu nhỏ do áp thêm daily limit 20%
- F-022 — regime exit dựa trên dữ liệu thiếu (`return7d`/`return24h` = None bị ép về 0.0)
- F-030 — Crash zone luôn gắn `pool="OPPORTUNITY"` kể cả khi vốn lấy một phần từ SMART
- RSK-009 — vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn

Cũng là mệnh đề số 10 của Impl Plan §7 đã bị **BÁC BỎ** trong S001, và là điều kiện để mệnh đề 11
(định nghĩa [F5]) được xác nhận đầy đủ.

## Scope

- `src/eth_dca_os/regime.py` — mô hình hoá trạng thái nền và nhãn dẫn xuất
- `src/eth_dca_os/engine.py` — nhánh dọn ladder, snapshot [F5], vòng đời zone
- `src/eth_dca_os/ladders.py` — vòng đời và nhãn pool của Crash zone
- `tests/` — test vòng đời, test [F1], test bất biến kế toán

## Out of Scope

- Đổi ngưỡng vào/ra CRASH, RECOVERY, STRESSED — đó là tham số spec (Master Index §6)
- Đổi công thức OSCORE, unlock, spacing, phân bổ ladder
- Ngữ nghĩa dữ liệu INVALID và data gap — đó là **WP-A4**
- Thứ tự 18 bước — đó là **WP-A6**
- Sinh/đo Failure Signal — đó là **WP-A5**
- Mở rộng parity sang JS — đó là **WP-C4**, và WP-C4 **phải đợi** gói này xong

## Dependencies
- T-04 (DONE)

## Blocks
- WP-A4 (tuần tự hoá: cả hai sửa `engine.py`)
- WP-A5 (đo lường chỉ đúng khi vốn không còn bị khoá)
- WP-A6 (test thứ tự phải khoá vào hành vi cuối cùng)
- WP-C4 (không khoá parity vào hành vi sắp đổi)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-A2, WP-C1, WP-D1, WP-D2
- **Không song song với WP-A4**: cả hai sửa `engine.py`

## Expected Touch Area

Allowed:
- `src/eth_dca_os/regime.py`, `engine.py`, `ladders.py`
- `tests/`
- `docs/CONVENTIONS.md` nếu phát sinh quy ước mới cho điểm spec để ngỏ

Do not touch without Scope Expansion:
- `src/eth_dca_os/score.py`, `capital.py`, `verdict.py`, `failure_signals.py`, `gates.py`
- `webapp/engine.js` — parity thuộc WP-C4
- `docs/spec/`

## Subtasks
- [x] A3.1 Tách nhãn dẫn xuất STRESSED khỏi trạng thái nền NORMAL/CRASH/RECOVERY, hoặc phương án
      tương đương đạt cùng bất biến; ghi quyết định thiết kế — `RegimeTracker.state`/`.label`,
      quyết định ghi tại `docs/CONVENTIONS.md` #14
- [x] A3.2 Đóng đường ra của Crash ladder cho **mọi** trạng thái kết thúc Recovery, không riêng NORMAL
      — nhánh dọn so trên `state`; quét cả ladder tồn đọng từ episode re-entry trước
- [x] A3.3 Chặn regime exit dựa trên dữ liệu thiếu; `None` không được coi là 0.0 — CONVENTIONS #15
- [x] A3.4 Sửa snapshot [F5] đo theo AVAILABLE đã unlock; daily limit áp ở khâu deployment
      — CONVENTIONS #4/#5; reason code `DAILY_LIMIT_BLOCK` được phát lần đầu
- [x] A3.5 Gắn nhãn pool của Crash zone theo nguồn vốn thật cho tie-break §15.1 — CONVENTIONS #16;
      `zone_order_key` bổ sung vế "crash sau ladder thường cùng pool"
- [x] A3.6 Viết test vòng đời CRASH → RECOVERY → STRESSED — CHECK-A3-01
- [x] A3.7 Viết test [F1] phủ đủ năm bề mặt: unlock, ladder, cooldown, limit, execution — CHECK-A3-03
- [x] A3.8 Định lượng thay đổi kết quả mô phỏng trước–sau trên cùng seed/dataset — CHECK-A3-08
- [x] A3.9 Rà soát toàn diện: mọi trạng thái ladder đều có đường kết thúc giải phóng reserve
      — bảng liệt kê tại evidence CHECK-A3-02

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency (T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §14 [F5], §15.1 [F2], §17.3 [F1], §18.3; BT §1, §19
- [x] Data impact được biết — **gói này làm đổi kết quả mô phỏng**; mọi kết quả chạy trước đó trên
      engine cũ không được dùng để so sánh như thể cùng một thuật toán
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Primary agent tier được gán bằng router (D/Fable/max, ba floor độc lập)
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [ ] Xác nhận lại toàn bộ Ready Gate khi mở task

## Completion Gate

Risk = 4 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được; category `accounting_financial` và
vị trí trên đường găng → **E2 bắt buộc** cho CHECK-A3-10.

Nguyên tắc bằng chứng riêng của gói này: **"đọc code thấy hợp lý" không được dùng làm bằng chứng
hoàn thành** cho bất kỳ REQUIRED check nào dưới đây. Mọi mệnh đề ở đây đều kiểm chứng được bằng
chạy thật.

### Functional / Business Logic

#### CHECK-A3-01 — Chuỗi CRASH → RECOVERY → STRESSED giải phóng hết reserve của Crash zone
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng đúng kịch bản của F-001 — vào CRASH, chuyển RECOVERY, hết 72h Recovery trong khi
`Return7D <= -10%` (tức regime thành STRESSED chứ không phải NORMAL). Khẳng định Crash zone chưa
execute chuyển CANCEL và reserve về 0. Đây là ca mà hôm nay thất bại.

Kết quả: `tests/test_wp_a3_lifecycle.py::test_check_a3_01_crash_recovery_stressed_releases_reserve`
dựng đúng kịch bản ở tầng engine (chuỗi nhãn NORMAL→CRASH→RECOVERY→STRESSED được assert làm
tiền đề). BEFORE fix: FAIL với `assert 'SUSPENDED' == 'CANCELLED'`, SMART reserved kẹt 27.2
(baseline đầy đủ trong `docs/sessions/S003-wp-a3-regime-ladder.md`). AFTER fix: PASS — ladder
CANCELLED, mọi zone chưa execute CANCELLED, reserve zone mở = 0, release mang reason
`RECOVERY_END` đúng tại tick kết thúc recovery, tổng release = tổng reserve CRASH_ZONE trừ phần
đã deploy, ledger ba pool tự hoà. Thêm
`test_check_a3_01_reentry_then_clean_end_releases_everything` phủ multi-episode/re-entry.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-02 — Không còn trạng thái ladder nào thiếu đường kết thúc giải phóng reserve
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: liệt kê **đầy đủ** các trạng thái vòng đời của Smart / Opportunity / Crash ladder và chứng
minh mỗi trạng thái có ít nhất một đường tới kết thúc trả reserve. Kèm test chạy dài trên dữ liệu
tổng hợp khẳng định không tồn tại reserve tồn tại quá thời hạn spec cho phép. Đây là check chống
tái diễn F-001 dưới một hình thức khác.

Liệt kê đầy đủ (trạng thái giữ reserve × đường kết thúc trả reserve):

| Ladder | Trạng thái giữ reserve | Đường kết thúc trả reserve |
|---|---|---|
| SMART | ACTIVE (zone ACTIVE/TRIGGERED/ACTION_PENDING) | fill (RESERVED→DEPLOYED); TTL/MISSED (release); bullish invalidation (release); hết hạn cuối accounting month — hai điểm: rollover tháng và Day 28 (release) |
| OPPORTUNITY | ACTIVE (zone ACTIVE/SUSPENDED/TRIGGERED/ACTION_PENDING) | fill; TTL/MISSED; bullish invalidation; expiry 90 ngày; cancel tại crash entry; zone SUSPENDED quá 7 accounting day → cancel + release |
| CRASH | ACTIVE (trong CRASH) | fill; TTL/MISSED; bullish invalidation; chuyển SUSPENDED khi CRASH→RECOVERY |
| CRASH | SUSPENDED (trong RECOVERY, kể cả ladder tồn đọng từ episode re-entry trước) | zone SUSPENDED vẫn trigger được (hit → fill); TTL/MISSED; **recovery-end cancel + release — SAU FIX chạy cho MỌI kết cục kết thúc recovery (state NORMAL), không phụ thuộc nhãn** |
| Mọi loại | Trạng thái terminal (COMPLETED/CANCELLED/EXPIRED/INVALIDATED) | bất biến: không giữ reserve khi vào trạng thái terminal (mọi đường vào đều release/deploy trước) |

Chứng minh vòng đời CRASH đóng: trong một run hữu hạn, mỗi episode CRASH hoặc (a) chưa kết thúc
khi run dừng (mô phỏng cắt — không phải trạng thái thiếu đường ra), hoặc (b) đi tới RECOVERY;
mỗi RECOVERY hoặc re-enter (đếm hữu hạn) hoặc kết thúc sau đúng 72h → nhánh cleanup (so trên
state) cancel + release MỌI crash ladder còn mở, kể cả ladder các episode trước.

Kết quả chạy: `test_check_a3_02_long_run_no_orphan_reserve` (4 năm dữ liệu tổng hợp có chu kỳ
crash) — pool.reserved == tổng reserve các zone còn mở (không reserve mồ côi), ladder terminal
không giữ reserve, kết thúc state NORMAL thì mọi crash ladder CANCELLED/COMPLETED, ledger ba
pool tự hoà. Impact run 7,5 năm: `stuck_crash_reserve_at_end = 0`, 10/10 crash ladder đóng.
BEFORE fix: test FAIL (bề mặt `state` chưa tồn tại); kịch bản F-001 baseline giữ reserve 27.2
vô hạn.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-03 — [F1] đúng theo nghĩa đen: STRESSED không có hiệu ứng trên cả năm bề mặt
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test đối chứng hai lần chạy giống hệt nhau, khác nhau **chỉ ở nhãn STRESSED**, khẳng định
unlock, ladder, cooldown, limit và execution đều không đổi. Không được kiểm bằng cách đọc code.
Đây là mệnh đề số 10 của Impl Plan §7 đã bị BÁC BỎ ở S001.

Kết quả: `test_check_a3_03_f1_stressed_no_effect_on_five_surfaces` — chạy engine HAI lần trên
cùng dataset 18 ngày (có smart ladder, cooldown block, crash, daily-limit block, recovery,
opportunity ladder): run A nhãn chuẩn; run B ép `_derive_label` trả STRESSED cho toàn bộ thời
gian nền NORMAL (phân kỳ nhãn tối đa; test assert hai run có nhãn khác nhau thật và trạng thái
nền identical — counterfactual "chỉ khác nhãn" đúng nghĩa đen). Khẳng định bằng chạy thật:
execution (purchases identical từng field trừ trường nhãn; eth_total identical), ladder (mọi
ladder/zone identical), unlock (ledger RESERVE/DEPLOY/RELEASE ba pool identical từng entry),
cooldown (tổng override bằng nhau; timestamp mọi fill identical), limit (counters
triggered/missed/executed identical; chuỗi DAILY_LIMIT_BLOCK identical), cash_samples identical.
Năm bề mặt lấy đúng từ ST §17.3/A3.7: unlock, ladder, cooldown, limit, execution.
BEFORE fix: không tồn tại bề mặt nhãn tách rời để dựng counterfactual (nhãn trộn vào trạng
thái nền) — bằng chứng VI PHẠM [F1] trước fix là baseline F-001 (nhãn chặn nhánh dọn ladder,
tức bề mặt "ladder" bị ảnh hưởng), đúng kết luận S001 bác bỏ mệnh đề 10.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-04 — Regime không thoát CRASH dựa trên dữ liệu thiếu
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test khẳng định với `Return7D = None` và/hoặc `Return24H = None`, regime **không** rời
CRASH. Hôm nay `None` bị ép về `0.0` và thoả điều kiện exit — dữ liệu xấu đang đẩy trạng thái theo
hướng có lợi cho strategy. Đóng F-022.

Kết quả: bốn test `test_check_a3_04_*` PASS sau fix — (1) toàn bộ input None ≥ 48h giữ CRASH
(BEFORE fix: FAIL, thành RECOVERY sau 49h — output baseline trong biên bản S003); (2) thiếu một
trong hai return giữ CRASH (điều kiện exit là AND); (3) một quan sát None phá chuỗi "liên tục
48h" — đồng hồ reset, exit chỉ sau 48h liên tục CÓ dữ liệu thoả; (4) chống over-blocking: dữ
liệu thật thoả điều kiện vẫn exit đúng mốc 48h; (5) đối xứng: None không tạo bằng chứng entry
hay STRESSED, nhưng một vế OR có dữ liệu thật vẫn giữ nguyên giá trị bằng chứng. Không dùng giá
trị mặc định giả ở bất kỳ đâu (quy ước CONVENTIONS #15).

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-05 — Snapshot [F5] đo theo AVAILABLE đã unlock; daily limit áp ở khâu deployment
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test khẳng định snapshot eligible capital của Crash ladder bằng Smart AVAILABLE +
Opportunity AVAILABLE theo định nghĩa [F5], **không** bị thu nhỏ bởi daily limit 20%; và daily limit
vẫn được cưỡng chế đúng ở khâu triển khai. Đóng F-021. Giữ nguyên tính bất biến của snapshot và giữ
đúng thứ tự "cancel/release trước, snapshot sau" mà mệnh đề 11 đã xác nhận.

Kết quả: bốn test `test_check_a3_05_*` PASS sau fix —
(1) snapshot = 36 = smart 30 + opp unlocked 6, KHÔNG bị daily headroom 4 thu nhỏ (BEFORE fix:
FAIL `assert 34.0 == 36.0`); allocation C0–C3 = 20/25/25/30% áp đúng trên snapshot; field
`eligible_capital_vnd` không được ghi lại sau khi tạo (bất biến giữ nguyên); thứ tự
cancel/release → snapshot giữ nguyên vị trí cũ trong code (mệnh đề 11 không bị phá).
(2) VƯỢT boundary: phần vốn Opportunity của C0 (6) > headroom ngày (4) → `DAILY_LIMIT_BLOCK`
(reason code ST §20, trước đây không bao giờ phát), zone giữ TRIGGERED xét lại cycle sau, không
fill CRASH nào xảy ra, và recovery-end vẫn giải phóng đủ 36 (không tạo kênh khoá vốn mới).
(3) ĐÚNG boundary: phần Opportunity C0 = 4 == headroom 4 → được triển khai (limit là "tối đa").
(4) DƯỚI boundary: opp fund 30 (level Gate-2 hợp lệ), phần Opportunity C0 = 5.2 < headroom 6 →
triển khai bình thường. Ladder Opportunity thường giữ nguyên cơ chế reserve-time cũ
(CONVENTIONS #4) — ngoài phạm vi F-021.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-06 — Nhãn pool của Crash zone phản ánh nguồn vốn thật, tie-break §15.1 xếp đúng nhóm
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng ca Crash zone được cấp vốn một phần từ SMART, khẳng định thứ tự tie-break [F2]
xếp đúng nhóm pool. Đóng F-030.

Kết quả: ba test `test_check_a3_06_*` PASS sau fix — (1) ladder lấy 30/36 từ SMART (ca pha trộn:
C0 = 6 OPPORTUNITY + phần SMART; C1–C3 toàn SMART): mọi zone mang label SMART (BEFORE fix: FAIL
`assert 'OPPORTUNITY' == 'SMART'`); (2) ladder đa số vốn OPPORTUNITY giữ label OPPORTUNITY;
(3) khoá sắp thứ tự `zone_order_key` kiểm trực tiếp: zone Smart thường trước crash-zone cấp vốn
SMART (dù crash ladder tạo sớm hơn — vế "sau Smart/Opportunity thường" của §15.1 mục 1, trước
đây thiếu), crash-SMART trước mọi zone OPPORTUNITY, zone_index tăng dần trong cùng ladder.
Quy ước cho ca pha trộn (spec để ngỏ): label = pool cấp đa số tổng reserve, hoà → OPPORTUNITY —
ghi tại CONVENTIONS #16; hạch toán release/deploy vẫn theo map (pool, amount) thật từng zone.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

### Data Integrity

#### CHECK-A3-07 — Bất biến kế toán giữ nguyên qua toàn bộ vòng đời mới
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: trên một lần chạy dài, khẳng định `TOTAL = AVAILABLE + RESERVED + DEPLOYED` tại mọi thời
điểm, không pool nào âm, và **không double reservation** giữa Smart / Opportunity / Crash — kể cả ở
ca chuyển Opportunity ladder sang Crash ladder. Mệnh đề 3 của Impl Plan §7 hiện đang **KHÔNG KẾT
LUẬN ĐƯỢC**; gói này phải đưa nó về kết luận.

Kết quả: `test_check_a3_07_accounting_invariants_multi_transition` (chuỗi CRASH → RECOVERY →
re-enter CRASH → RECOVERY → NORMAL qua HAI tháng, có fill giữa chừng, có cancel Opportunity
ladder tại crash entry — đúng ca "chuyển Opportunity sang Crash") + `test_check_a3_02_long_run_
no_orphan_reserve` (4 năm dữ liệu tổng hợp): replay TỪNG entry ledger của cả ba pool khớp số dư
`available/reserved/deployed_after` ghi tại entry (tức bất biến giữ tại MỌI thời điểm có dịch
chuyển vốn, không chỉ cuối run), không số dư âm, tổng ba pool == tổng contribution (không
mất/không tạo vốn), và pool.reserved == tổng `reserved_vnd` các zone còn mở (không double
reservation, không release về sai pool — release/deploy đi theo map (pool, amount) từng zone).
Mệnh đề 3 Impl Plan §7 nay có kết luận E1 ở tầng engine: **XÁC NHẬN**.

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

### Regression

#### CHECK-A3-08 — Thay đổi kết quả mô phỏng được định lượng và giải thích được
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, so metric trước–sau và **giải thích từng sai lệch bằng một điều khoản
spec cụ thể**. Gói này được phép làm đổi kết quả; nó **không** được phép làm đổi kết quả theo cách
không giải thích được. Sai lệch không giải thích được là dấu hiệu của một defect mới.

Kết quả: cùng dataset tổng hợp (SYNTH_SEED 20260822, sinh một lần dùng chung), cùng config,
cùng cửa sổ 2019-01→2026-06; BEFORE đo trên HEAD 5645a74 TRƯỚC khi sửa. Bảng so sánh đầy đủ
14 nhóm metric với giải thích từng dòng bằng điều khoản spec: biên bản
`docs/sessions/S003-wp-a3-regime-ladder.md` mục "Impact BEFORE → AFTER". Tóm tắt: mọi sai lệch
quy về đúng hai requirement được khôi phục — [F5] ST §14 (snapshot 99.30→111.13; fill CRASH
24.77→26.82; ít Opportunity ladder song song trong crash hơn 20→18 vì snapshot claim trọn phần
unlocked) và ST §18.3 + [F1] (release RECOVERY_END 74.54→84.31, chạy cho mọi kết cục recovery-
end). Nhãn `label_transitions` identical từng cặp (ngữ nghĩa nhãn không đổi); BASE/SMART fill
không đổi; ETH accumulated đổi +5e-6 (0.0005%) có giải thích; avg cash ratio giảm nhẹ đúng chiều
FS-07 hết bị bóp méo. Không sai lệch nào không giải thích được; điều kiện escalation "metric đổi
theo hướng có lợi không giải thích được" KHÔNG kích hoạt. Không dùng số liệu synthetic để tuyên
bố edge (DEC-003).

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

#### CHECK-A3-09 — Toàn bộ test suite Python PASS; không test nào bị nới lỏng hoặc skip
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ. Nếu một test hiện có phải sửa vì hành vi đổi, phải nêu rõ test
nào, đổi gì, và vì sao hành vi mới mới là hành vi đúng theo spec.

Kết quả: `python -m pytest tests/` → **87 passed, 0 failed, 0 skipped trong 456.49s** (69 test
có sẵn + 18 test WP-A3 mới). **Không một test hiện có nào bị sửa, nới lỏng, hay skip** — mọi
expected value cũ giữ nguyên và vẫn PASS trên code mới (các test regime cũ kiểm nhãn qua
`.regime`/`update()` — bề mặt reporting được giữ tương thích bằng property). Trước fix, đúng bộ
test này: 69 cũ PASS + 18 mới → 12 FAIL đúng kỳ vọng / 6 guard PASS (chi tiết ở biên bản S003).

Executed By:
S003 agent (Tier D / Fable / max)

Timestamp:
2026-08-23

### Audit độc lập

#### CHECK-A3-10 — Có bản rà soát độc lập E2 cho vòng đời regime/ladder
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer độc lập theo "Solo Independent Review Procedure", bắt đầu từ trạng thái
repo, chạy lại CHECK-A3-01, A3-03, A3-07 và tự tìm thêm ít nhất một kịch bản khoá vốn khác. Lưu tại
`docs/reviews/` theo `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ; E2 cho CHECK-A3-10)
- [ ] Mọi sai lệch kết quả mô phỏng được định lượng và quy về một điều khoản spec
- [ ] Quyết định thiết kế (tách nhãn dẫn xuất hay phương án tương đương) được ghi lại
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-009 được cập nhật trạng thái
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Hai phương án thiết kế khác nhau đều không đạt đồng thời [F1] và vòng đời đóng →
  `CAPABILITY_CEILING`. Gói đã ở Tier D — khi đó dừng và trình chủ dự án, kèm phân tích, thay vì
  chồng thêm bản vá.
- Phát hiện spec để ngỏ ở chỗ "nhãn dẫn xuất có được gộp vào trạng thái nền không" →
  `CONFLICT DETECTED`: ghi quy ước vào `docs/CONVENTIONS.md` nếu đó là điểm để ngỏ hợp lệ; nếu là
  mâu thuẫn nội tại của spec thì chuyển sang **WP-D2** (đề xuất V2.2), **không vá V2.1.5**.
- Sửa xong nhưng metric đổi theo hướng làm chiến lược trông tốt hơn mà không giải thích được →
  DỪNG. Không được nghiệm thu. Đây đúng là loại thiên lệch mà stopping rule tồn tại để chặn.
- Phải chạm `capital.py` hoặc `score.py` để đóng vòng đời → `SCOPE_CHANGED`, mở
  `COMPLETION GATE CHANGE PROPOSAL`.

## Ảnh hưởng nếu gói này thất bại

Đây là mắt xích đầu tiên của đường găng T-04 → WP-A3 → WP-A4 → WP-A6 → GATE-A → T-06. Nếu gói thất
bại: WP-A4 và WP-A6 không khởi động được, WP-A5 sẽ đo trên engine còn khoá vốn (số FS-02/FS-07 sai
lệch), WP-C4 không được khoá parity, GATE-A không đóng, T-06 không mở, và toàn bộ đường tới verdict
dừng lại. Nếu bỏ qua và vẫn chạy official run, verdict sẽ dựa trên các Failure Signal bị bóp méo bởi
chính lỗi này — và Master Index §6 không cho chạy lại để sửa.

## Changed Files Registry

Created:
- `tests/wp_a3_harness.py` — harness quan sát + builder kịch bản (không đổi hành vi engine)
- `tests/test_wp_a3_lifecycle.py` — 18 test cho CHECK-A3-01…A3-07
- `docs/sessions/S003-wp-a3-regime-ladder.md` — biên bản phiên + baseline + impact
- `docs/reviews/E2-WP-A3-regime-ladder.md` — rà soát độc lập E2

Modified:
- `src/eth_dca_os/regime.py` — tách state/label; ngữ nghĩa None
- `src/eth_dca_os/engine.py` — execution đọc state; snapshot [F5]; daily limit bước 14;
  `zone_order_key`; pool label theo nguồn vốn
- `docs/CONVENTIONS.md` — sửa #4/#5, thêm #14/#15/#16
- `PROJECT/PROJECT_PROGRESS.md`, file task này (điền evidence)
- `ladders.py` KHÔNG cần sửa (label gán tại engine sau khi biết nguồn vốn thật)

Deleted:
- Không

Migration Impact:
- Không có dữ liệu bền cần migrate. Nhưng **mọi kết quả chạy thử trước gói này không còn so sánh
  được** với kết quả sau, vì thuật toán đã đổi

## Notes

Nguyên nhân gốc mà S001 chỉ ra: `regime.py` gộp nhãn dẫn xuất (STRESSED) vào cùng trường với trạng
thái máy (NORMAL/CRASH/RECOVERY). Strategy §16 yêu cầu Market Regime và Execution State lưu riêng
nhưng **không nói rõ** nhãn dẫn xuất phải tách khỏi trạng thái nền — đây là chỗ spec để ngỏ và code
đã chọn cách gộp. Vì vậy đây là **quyết định thiết kế**, không phải sửa một dòng, và quyết định đó
phải được ghi lại.

Lưu ý phối hợp với WP-C2: WP-C2 mô hình hoá Execution State (chiều khác). Hai gói không được cùng
định nghĩa lại một chiều trạng thái. WP-A3 sở hữu Market Regime; WP-C2 sở hữu Execution State.
