# SESSION HANDOFF — S003

Session ID:
S003

Task:
WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp

Task Mode:
MAJOR

Project Profile:
PRODUCT

Status:
DONE — 10/10 REQUIRED check PASS (E1 toàn bộ; E2 cho CHECK-A3-10 với kết luận reviewer độc lập
**E2 PASS**); mọi follow-up của reviewer thuộc thẩm quyền phiên đã thực hiện xong trước khi đóng.

Model/Effort thực thi:
Tier D (Fable) / max — đúng routing đã đóng băng trong file task (xác nhận lại bằng
`routing_engine.py` tại phiên: model_score 3.5 → D, effort_score 3.65 → max, ba model floor
`cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`, `safety_business:min_C`; effort floor
`safety_business:min_high`).

Môi trường:
Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1
(trùng đúng bộ phiên bản đã ghi nhận tại S000 — kết quả so sánh được với baseline S000/S001).

## Result

**WP-A3 = DONE.** Chuỗi đầy đủ: Ready Gate PASS → baseline E1 tái hiện đủ 4 finding →
regression test viết TRƯỚC fix (12 FAIL đúng kỳ vọng) → remediation trong `regime.py` +
`engine.py` → 18/18 test WP-A3 PASS → toàn bộ suite PASS (87/87) → impact BEFORE/AFTER được
định lượng và giải thích từng sai lệch bằng điều khoản spec → reviewer độc lập kết luận
**E2 PASS** → follow-up của reviewer được thực hiện ngay trong phiên → chạy lại toàn bộ xanh.

Chi tiết trạng thái từng REQUIRED check: xem "Completion Gate Summary" bên dưới và evidence
trong `docs/tasks/WP-A3-regime-va-vong-doi-ladder.md`.

## E2 độc lập (CHECK-A3-10) và xử lý follow-up

Reviewer session độc lập (không chung ngữ cảnh) rà soát commit `347ba7c` theo Solo Independent
Review Procedure; bản review: `docs/reviews/E2-WP-A3-regime-ladder.md` (E2-WP-A3-001).
Kết luận reviewer: **E2 PASS** — tự chạy lại CHECK-A3-01/03/07 bằng kịch bản/validator RIÊNG
(kể cả đối chứng code cũ `5645a74`: kịch bản riêng của reviewer cho thấy khoá vốn thật 18.7
trước fix, release = 0), và thử 4 kịch bản khoá vốn tự nghĩ + 1 long-run cửa sổ khác mà
**không tìm thấy đường khoá vốn mới nào**.

Reviewer ghi 2 finding hạ tầng kiểm chứng (không phải lỗi engine) và 4 mismatch narrative bắt
nguồn từ chúng; toàn bộ follow-up thuộc thẩm quyền phiên implementer đã được thực hiện TRONG
S003, trước khi đóng task:

| Finding của reviewer | Xử lý trong S003 (sau review, trước khi đóng) |
|---|---|
| F-E2-01 (MEDIUM): `wp_a3_harness.build_dataset` dùng `idx.asi8 // 10**9` — sai đơn vị trên pandas 3 (datetime64[us]) → spec `price`/`low_dip` theo ngày bất động âm thầm; narrative A3-03/A3-07 mô tả nhiều hơn test chứng minh (M1–M3) | Sửa epoch-seconds bằng phép chia Timedelta (cùng idiom `engine._epoch_seconds`, độc lập đơn vị) + **assert tự kiểm** trong builder (mọi price/low_dip đã đặt phải xuất hiện thật trong dataset — chống tái diễn). Làm giàu kịch bản a3_03 (thêm low_dip ngày crash, oscore 85 ngày 15) và a3_07 (thêm opportunity ladder trước crash) rồi thêm **assert tiền đề** để test tự khẳng định: run A có fill SMART/CRASH/OPPORTUNITY thật, ≥1 DAILY_LIMIT_BLOCK thật, ca release `CRASH_ENTRY` (chuyển Opportunity→Crash) thật. Narrative evidence A3-03/A3-07 trong file task được cập nhật khớp sự kiện thực. Chạy lại: 18/18 PASS; toàn suite chạy lại xanh (xem Verification Evidence). |
| F-E2-02 (LOW): script đo impact không được commit → bảng CHECK-A3-08 không tái lập từ repo (M4) | Commit công cụ tại `tests/wp_a3_impact_tool.py` (tham số `--src` cho phép đo BEFORE trên git worktree ở commit cũ, gỡ editable finder, assert + ghi provenance `code_path` vào JSON). Chạy lại bằng công cụ đã commit: **khớp HOÀN TOÀN** cả hai bản đo BEFORE (worktree `5645a74`) và AFTER với số liệu trong bảng impact của biên bản này. |
| O-1: xác nhận độc lập PH-03 | Giữ nguyên ghi nhận RSK-010/PH-03 — chờ chủ dự án (ngoài scope WP-A3). |
| O-2: engine cho phép tạo ladder mới trong CRASH bằng vốn vừa release; vòng đời vẫn đóng | Ghi nhận quan sát; spec không cấm tường minh; không đổi hành vi trong WP-A3 (ngoài 4 finding sở hữu). Nếu chủ dự án muốn cấm/giới hạn → convention mới hoặc V2.2. |

Hai finding F-E2-01/F-E2-02 nằm ở tầng test/công cụ đo, không đổi hành vi engine; các sửa
follow-up chỉ chạm `tests/` (vùng Allowed) và tài liệu — không chạm `src/` sau khi review.

## Ready Gate (xác nhận lại khi mở task — 2026-08-23)

| Mục | Kết quả |
|---|---|
| Dependency T-04 | DONE (12/12 REQUIRED check của T-04 PASS tại S002) |
| Completion Gate | FROZEN 2026-08-23, không sửa/không làm yếu check nào |
| `validate_routing.py` | PASS (16 MAJOR task, 0 override) — chạy tại phiên |
| `validate_easy_roadmap.py` | PASS — chạy tại phiên |
| Routing WP-A3 | Router trả D/max tự nhiên, khớp file task; phiên chạy đúng D/Fable/max |
| Scope Lock | Load từ file task; chỉ được chạm `regime.py`, `engine.py`, `ladders.py`, `tests/`, `docs/CONVENTIONS.md` |
| Trạng thái | WP-A3 chuyển READY → IN_PROGRESS trong PROJECT_PROGRESS, sync roadmap PASS |

## Completion Gate Summary

Required: 10 (CHECK-A3-01 … CHECK-A3-10, toàn bộ REQUIRED)
PASS: 10
FAIL: 0
BLOCKED: 0
NOT_TESTED: 0

## Verification Evidence

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-A3-01 | PASS | E1 | test engine-level kịch bản F-001 + multi-episode; BEFORE FAIL (`SUSPENDED != CANCELLED`, kẹt 27.2) → AFTER release đủ tại tick recovery-end, reason RECOVERY_END | S003 agent | 2026-08-23 |
| CHECK-A3-02 | PASS | E1 | bảng liệt kê vòng đời đầy đủ + long-run 4 năm không reserve mồ côi; impact 7,5 năm stuck=0 | S003 agent | 2026-08-23 |
| CHECK-A3-03 | PASS | E1 | counterfactual hai run chỉ khác nhãn, 5 bề mặt identical; kịch bản tự khẳng định (fill S/C/O + DAILY_LIMIT_BLOCK thật) | S003 agent | 2026-08-23 |
| CHECK-A3-04 | PASS | E1 | None không thoát/không vào/không đứt-quãng-mà-vẫn-exit; dữ liệu thật vẫn exit đúng 48h | S003 agent | 2026-08-23 |
| CHECK-A3-05 | PASS | E1 | snapshot 36 đúng [F5]; daily limit ở khâu triển khai với dưới/đúng/vượt boundary | S003 agent | 2026-08-23 |
| CHECK-A3-06 | PASS | E1 | pool label theo đa số nguồn vốn (SMART/OPPORTUNITY); `zone_order_key` kiểm trực tiếp thứ tự [F2] + crash-sau-thường | S003 agent | 2026-08-23 |
| CHECK-A3-07 | PASS | E1 | replay ledger từng entry, 3 pool; multi-transition 2 episode/2 tháng; tổng = contribution; không double reservation | S003 agent | 2026-08-23 |
| CHECK-A3-08 | PASS | E1 | bảng impact 14 nhóm metric, mỗi dòng quy về điều khoản spec; công cụ đo đã commit, tái lập HOÀN TOÀN | S003 agent | 2026-08-23 |
| CHECK-A3-09 | PASS | E1 | suite đầy đủ 87 passed / 0 failed / 0 skipped (456.49s); chạy lại sau follow-up E2: xem dòng cuối mục này | S003 agent | 2026-08-23 |
| CHECK-A3-10 | PASS | E2 | `docs/reviews/E2-WP-A3-regime-ladder.md` — reviewer độc lập kết luận E2 PASS; 4 kịch bản khoá vốn tự tìm + long-run: không đường khoá vốn mới | Reviewer E2-WP-A3-001 | 2026-08-23 |

Chạy lại toàn suite SAU follow-up E2 (harness fix + kịch bản giàu + công cụ impact):
**87 passed, 0 failed, 0 skipped — 454.08s (0:07:34)**. Trước đó, lần chạy sau remediation:
87 passed / 456.49s; lần chạy độc lập của reviewer: 87 passed / 467.43s.

## Baseline E1 — tái hiện TRƯỚC khi sửa (bắt buộc theo chỉ thị S003 mục 4)

Toàn bộ tái hiện chạy trên HEAD `5645a74` (chưa sửa dòng code sản phẩm nào), bằng harness
quan sát phía test (`tests/wp_a3_harness.py` — patch namespace engine để chụp Pool/Ladder/
RegimeTracker, KHÔNG đổi hành vi). Script: `wp_a3_baseline.py` (scratchpad phiên).

### F-001 — tầng engine, kịch bản "sập sâu → hồi một phần → vẫn yếu"

Kịch bản 14 ngày (giá phẳng 100 → 100.5; Day 5 07:00 local: OSCORE 80, Return7D −16% →
CRASH; Day 6–7: Return7D −5% giữ 48h; Day 8 07:00: RECOVERY; Day 11 07:00: hết 72h Recovery
trong khi Return7D = −11%). Output chạy thật:

```
Regime label transitions (ts local, prev -> new):
  03-05 07:00 local  NORMAL    -> CRASH
  03-08 07:00 local  CRASH     -> RECOVERY
  03-11 07:00 local  RECOVERY  -> STRESSED

Crash ladders tạo ra: 1
  ladder id=1 status=SUSPENDED anchor=100 spacing=0.08625 eligible_snapshot=34
    C0: status=EXECUTED       target_vnd=6.8  reserved=6.8  pool=OPPORTUNITY
    C1: status=SUSPENDED      target_vnd=8.5  reserved=8.5  pool=OPPORTUNITY
    C2: status=SUSPENDED      target_vnd=8.5  reserved=8.5  pool=OPPORTUNITY
    C3: status=SUSPENDED      target_vnd=10.2 reserved=10.2 pool=OPPORTUNITY

Pool state cuối run:
  BASE         available=15   reserved=0     deployed=35
  SMART        available=0    reserved=27.2  deployed=2.8
  OPPORTUNITY  available=15.8 reserved=0     deployed=4.2

--- KẾT LUẬN BASELINE F-001 ---
Regime cuối:            STRESSED
Crash ladder status:    ['SUSPENDED']
SMART reserved cuối:    27.2        <- kỳ vọng spec §18.3: 0 sau khi Recovery kết thúc
```

27,2 đơn vị SMART bị khoá vô hạn: `smart_reservable` trừ `reserved` nên **không tạo được
ladder mới**, đúng chuỗi hệ quả RSK-009. Ledger ba pool tự hoà (bảo toàn vốn) — lỗi nằm ở
vòng đời, không nằm ở sổ.

### F-021 — snapshot [F5] bị daily limit thu nhỏ

Cùng kịch bản, tại crash entry: Opportunity unlocked = 20 × 0.3 = 6 nhưng
`opportunity_reservable` áp thêm daily headroom 20 × 20% = 4:

```
eligible_capital_vnd (code hiện tại) = 34   (= smart 30 + min(6, daily 4))
theo [F5] ST §14 (không daily limit)  = 36   (= smart 30 + opp unlocked 6)
```

### F-030 — pool label của Crash zone

```
Reserve thật theo pool: [('OPPORTUNITY', 4.0), ('SMART', 2.8), ('SMART', 8.5),
                         ('SMART', 8.5), ('SMART', 10.2)]
Pool label trên từng zone: C0..C3 đều 'OPPORTUNITY'
-> 30/34 lấy từ SMART nhưng mọi zone dán nhãn OPPORTUNITY (tie-break §15.1 [F2] sai nhóm)
```

### F-022 — thoát CRASH bằng dữ liệu None

```
  t=0h    update(-20%, -12%, oscore 80) -> CRASH
  t=1h    update(None, None, None) -> CRASH
  t=25h   update(None, None, None) -> CRASH
  t=49h   update(None, None, None) -> RECOVERY   <- exit bằng dữ liệu không tồn tại
  Biến thể Return7D=None, Return24H=-2%: sau 49h -> RECOVERY
```

### Test-first: 12 FAIL đúng kỳ vọng trước fix

`tests/test_wp_a3_lifecycle.py` được viết TRƯỚC khi sửa code. Chạy trên HEAD chưa sửa:
**12 failed, 6 passed** (pytest 9.1.1). Các thông điệp fail trỏ thẳng vào từng finding:

```
FAILED test_check_a3_01_crash_recovery_stressed_releases_reserve
       AssertionError: assert 'SUSPENDED' == 'CANCELLED'          <- F-001
FAILED test_check_a3_04_none_does_not_exit_crash
       assert 'RECOVERY' == 'CRASH'  (toàn bộ input None)         <- F-022
FAILED test_check_a3_05_f5_snapshot_not_shrunk_by_daily_limit
       assert 34.0 == 36.0                                        <- F-021
FAILED test_check_a3_06_pool_label_reflects_funding
       AssertionError: assert 'OPPORTUNITY' == 'SMART'            <- F-030
FAILED test_check_a3_04_partial_none_does_not_exit_crash          <- F-022 (biến thể)
FAILED test_check_a3_04_none_breaks_exit_continuity               <- F-022 ("liên tục 48h")
FAILED test_check_a3_05_daily_limit_blocks_above_boundary         <- F-021 (khâu triển khai)
FAILED test_check_a3_01_reentry_then_clean_end_releases_everything (multi-episode)
FAILED test_check_a3_06_tiebreak_order_crash_after_normal_same_pool (bề mặt mới zone_order_key)
FAILED test_check_a3_03_f1_stressed_no_effect_on_five_surfaces    (bề mặt mới _derive_label)
FAILED test_check_a3_02_long_run_no_orphan_reserve                (bề mặt mới .state)
FAILED test_regime_state_label_separation                         (bề mặt mới .state)
```

6 test PASS trước fix là các guard biên được thiết kế để đúng ở cả hai phía (exit bằng dữ
liệu thật, entry qua một vế OR có dữ liệu, boundary đúng/dưới daily limit, nhãn OPPORTUNITY
khi Opportunity chiếm đa số, bất biến kế toán multi-transition).

Lưu ý riêng cho CHECK-A3-03: KHÔNG thể dựng counterfactual "chỉ khác nhãn" trên code cũ,
vì code cũ trộn nhãn vào trạng thái nền (không tồn tại bề mặt để ép nhãn khác đi mà không
đổi máy trạng thái). Bằng chứng VI PHẠM [F1] trước fix chính là baseline F-001 ở trên
(nhãn STRESSED chặn nhánh dọn ladder = hiệu ứng lên bề mặt "ladder"), đúng như S001 đã
kết luận khi BÁC BỎ mệnh đề 10 của Impl Plan §7.

## Root cause từng finding → requirement → thay đổi code

### F-001 (HIGH) — Reserve của Crash ladder không được giải phóng khi Recovery kết thúc vào STRESSED
- Requirement khôi phục: **ST §18.3** ("Sau 72h Recovery nếu vẫn chưa hit thì CANCEL và
  release reserve") và **ST §17.3 [F1]** (STRESSED không có hiệu ứng execution).
- Root cause: `regime.py` gộp nhãn dẫn xuất STRESSED vào cùng trường với trạng thái nền;
  khi Recovery hết hạn lúc thị trường còn yếu, trường `regime` thành `STRESSED`, trong khi
  nhánh dọn ở engine so `regime == "NORMAL"` → không bao giờ chạy; Crash ladder không có
  đường expiry nào khác (`expires_at=None`, nhánh expiry chỉ xử lý OPPORTUNITY).
- Thay đổi: **quyết định thiết kế A3.1** — tách `RegimeTracker.state` (trạng thái nền
  NORMAL/CRASH/RECOVERY, máy trạng thái §17.1–§17.2) khỏi `RegimeTracker.label` (nhãn báo
  cáo enum §16; `regime` là alias đọc). Mọi nhánh execution trong engine đọc `state`;
  nhãn chỉ còn trong purchase record và phân rã counter (BT §16). Nhánh dọn đổi thành
  `state == NORMAL and prev_state == RECOVERY`, quét mọi crash ladder còn mở (ACTIVE/
  SUSPENDED) để ladder tồn đọng từ episode re-entry trước cũng được đóng.
  Ghi tại `docs/CONVENTIONS.md` #14.

### F-022 (MEDIUM) — Regime exit dựa trên dữ liệu thiếu
- Requirement khôi phục: **BT §1** (giả định bảo thủ; backtest tồn tại để bác bỏ) và
  **ST §3** (dữ liệu xấu không được đẩy trạng thái theo hướng có lợi), áp lên điều kiện
  exit **ST §17.2** ("liên tục trong 48h").
- Root cause: `return7d/return24h = None` bị ép về `0.0`, mà `0.0 > −5%` và `0.0 > −10%`
  thoả điều kiện exit → dữ liệu không tồn tại được dùng làm bằng chứng thoát CRASH.
- Thay đổi: bỏ ép kiểu; mọi so sánh chỉ thoả khi có dữ liệu thật (`x is not None and ...`).
  Điều kiện exit dạng AND: thiếu bất kỳ vế nào → không thoả VÀ phá chuỗi "liên tục 48h"
  (reset exit-candidate). Entry/STRESSED dạng OR: từng vế đánh giá độc lập trên dữ liệu
  thật của vế đó (một vế None không chặn vế kia có dữ liệu). Ghi tại CONVENTIONS #15.

### F-021 (MEDIUM) — Snapshot [F5] bị daily limit 20% thu nhỏ
- Requirement khôi phục: **ST §14 [F5]** (snapshot = Smart AVAILABLE + Opportunity
  AVAILABLE — đã unlock, chưa nằm trong reservation nào — đo ngay sau cancel/release;
  bất biến trong đời ladder) và **ST §14/§15** ("Toàn bộ daily limit ... vẫn áp dụng
  trong Crash" — tức áp vào THỰC THI, không vào snapshot).
- Root cause: engine dùng `opportunity_reservable(...)` cho snapshot — hàm này min thêm
  `headroom_daily = 20% × fund − used_today`, hẹp hơn định nghĩa [F5].
- Thay đổi: phần Opportunity của snapshot tính đúng nghĩa đen [F5]
  (`min(available, max(0, total×unlock − reserved − deployed))`, giữ gating hysteresis/
  unlock như cũ); KHÔNG đụng `capital.py` (ngoài scope — hàm cũ vẫn dùng cho ladder
  Opportunity thường). Daily limit chuyển sang cưỡng chế ở **khâu triển khai** (bước 14,
  điểm engine cam kết tạo action): phần vốn OPPORTUNITY của crash zone > headroom còn lại
  trong ngày → chặn nguyên tử, log `DAILY_LIMIT_BLOCK` (reason code ST §20 — trước đây
  không bao giờ được phát), zone giữ TRIGGERED xét lại cycle sau (cùng cơ chế max_zones
  §15.1). Ghi tại CONVENTIONS #4/#5.

### F-030 (LOW) — Crash zone luôn dán nhãn pool OPPORTUNITY
- Requirement khôi phục: **ST §15.1 [F2]** mục 1 ("Crash ladder xếp theo pool nguồn vốn
  của nó, sau Smart/Opportunity thường").
- Root cause: `create_crash_ladder` dùng `source_pool="OPPORTUNITY"` mặc định, không nhìn
  nguồn vốn thật.
- Thay đổi: sau khi funding từng zone, engine gán label cả ladder = pool cấp **đa số**
  tổng reserve (hoà → OPPORTUNITY; spec để ngỏ trường hợp pha trộn — quy ước ghi tại
  CONVENTIONS #16). Khoá sắp thứ tự tách thành hàm module `zone_order_key`:
  `(pool_rank, is_crash, created_at, zone_index)` — bổ sung đúng vế "sau Smart/Opportunity
  thường" mà khoá cũ thiếu. Hạch toán release/deploy vẫn theo map (pool, amount) thật.

## Files changed

Modified:
- `src/eth_dca_os/regime.py` — tách state/label; ngữ nghĩa None; docstring thiết kế
- `src/eth_dca_os/engine.py` — nhánh execution đọc `state`; snapshot [F5] đúng nghĩa đen;
  daily limit ở bước 14; `zone_order_key`; label pool theo nguồn vốn
- `docs/CONVENTIONS.md` — sửa #4, #5; thêm #14, #15, #16
- `PROJECT/PROJECT_PROGRESS.md` — trạng thái WP-A3, RSK-009, phát hiện mới
- `docs/tasks/WP-A3-regime-va-vong-doi-ladder.md` — điền evidence Completion Gate

Created:
- `tests/wp_a3_harness.py` — harness quan sát + builder kịch bản (không đổi hành vi engine;
  sau follow-up E2: epoch-seconds độc lập đơn vị + assert tự kiểm)
- `tests/test_wp_a3_lifecycle.py` — 18 test cho CHECK-A3-01…A3-07 (kịch bản tự khẳng định)
- `tests/wp_a3_impact_tool.py` — công cụ đo impact CHECK-A3-08, tái lập từ repo (BT §20)
- `docs/sessions/S003-wp-a3-regime-ladder.md` — biên bản này
- `docs/reviews/E2-WP-A3-regime-ladder.md` — bản rà soát độc lập E2 (reviewer session riêng)

Không chạm (đúng Scope Lock): `capital.py`, `score.py`, `verdict.py`, `failure_signals.py`,
`gates.py`, `ladders.py` (được phép nhưng không cần sửa), `webapp/`, `docs/spec/`.

## Kết quả 5 bề mặt [F1] (CHECK-A3-03)

Task definition A3.7 và ST §17.3 nêu đúng năm bề mặt: **unlock, ladder, cooldown, limit,
execution**. Test `test_check_a3_03_f1_stressed_no_effect_on_five_surfaces` chạy engine
HAI lần trên cùng dataset 18 ngày (có smart ladder, cooldown block, crash, daily-limit
block, recovery, opportunity ladder): run A nhãn chuẩn, run B ép nhãn STRESSED cho toàn bộ
thời gian nền NORMAL (phân kỳ nhãn tối đa; xác nhận hai run có nhãn khác nhau thật và
trạng thái nền identical). Kết quả PASS với ánh xạ bề mặt → khẳng định:

| Bề mặt | Bằng chứng không đổi |
|---|---|
| execution | danh sách purchases identical từng field (trừ trường nhãn `regime` — reporting), `eth_total` identical |
| ladder | số ladder, loại, anchor, spacing, created_at, eligible, trạng thái cuối, và từng zone (index/target/status/pool) identical |
| unlock | ledger RESERVE/DEPLOY/RELEASE của cả ba pool identical từng entry |
| cooldown | tổng số cooldown override bằng nhau (phân rã theo nhãn được phép đổi — đó chính là reporting decomposition BT §16); timestamp mọi fill identical |
| limit | counters triggered/missed/executed/base_early/delayed identical; chuỗi `DAILY_LIMIT_BLOCK` identical |

Cấu trúc code sau fix bảo đảm thêm một tầng: grep toàn engine, nhãn (`regime.regime`)
chỉ còn xuất hiện ở purchase record và counter phân rã — không nhánh điều khiển nào đọc nó.

## Kết quả None transition (CHECK-A3-04)

- Toàn bộ input None ≥ 48h: giữ CRASH (trước fix: RECOVERY sau 49h).
- Thiếu một trong hai return (vế còn lại khỏe): giữ CRASH (điều kiện exit là AND).
- None ở giữa chuỗi 48h: phá "liên tục" — đồng hồ reset; exit chỉ xảy ra sau 48h liên tục
  CÓ dữ liệu thoả (test chứng minh mốc 96h chưa exit, 97h mới exit sau khi restart tại 49h).
- Chống over-blocking: dữ liệu thật thoả điều kiện vẫn exit đúng 48h như cũ.
- Đối xứng: None không tạo bằng chứng ENTER; một vế OR có dữ liệu thật vẫn đủ (entry qua
  Return24H thật khi Return7D thiếu); nhãn STRESSED cần bằng chứng thật.

## Kết quả [F5] / daily limit (CHECK-A3-05)

- Snapshot = 36 (smart 30 + opp unlocked 6) đúng nghĩa đen [F5]; C0–C3 áp 20/25/25/30%
  trên đúng snapshot đó; bất biến trong đời ladder (field không được ghi lại sau khi tạo).
- Dưới limit (opp fund 30, phần Opportunity của C0 = 5.2 < headroom 6): triển khai ngay.
- Đúng boundary (phần Opportunity C0 = 4 == headroom 4): triển khai (limit là "tối đa").
- Vượt boundary (phần Opportunity C0 = 6 > headroom 4): `DAILY_LIMIT_BLOCK`, zone giữ
  TRIGGERED; không tạo kênh khoá vốn mới — recovery-end cancel giải phóng đủ 36.
- Ladder Opportunity thường giữ nguyên cơ chế cũ (reserve-time, CONVENTIONS #4) — ngoài
  phạm vi F-021, không đổi.

## Accounting invariants (CHECK-A3-07) + vòng đời đóng (CHECK-A3-02)

- Test multi-transition (CRASH → RECOVERY → re-enter → RECOVERY → NORMAL, có fill giữa
  chừng, hai episode qua hai tháng): replay từng entry ledger của cả ba pool khớp số dư
  ghi lại, không số dư âm, `TOTAL = AVAILABLE + RESERVED + DEPLOYED` tại mọi điểm, tổng
  ba pool == tổng contribution (không mất/không tạo vốn), pool.reserved == tổng reserve
  các zone còn mở (không double reservation, không reserve mồ côi).
- Chạy dài 4 năm dữ liệu tổng hợp (chu kỳ crash thật của generator): cùng các bất biến;
  ladder terminal không giữ reserve; kết thúc ở state NORMAL thì mọi crash ladder đã đóng.
- Liệt kê vòng đời đầy đủ (CHECK-A3-02): xem bảng trong file task (evidence CHECK-A3-02).

## Impact BEFORE → AFTER (CHECK-A3-08)

Cùng dataset tổng hợp (`data.synth.generate`, SYNTH_SEED 20260822, sinh MỘT lần và dùng
chung), cùng config baseline + GATE1_LOW_FRICTION, cùng cửa sổ 2019-01-01 → 2026-06-01,
cùng code đo (`wp_a3_impact.py`). BEFORE chạy trên HEAD `5645a74` trước khi sửa.

| Metric | BEFORE | AFTER | Giải thích bằng requirement |
|---|---|---|---|
| Số transition nhãn (tổng) | 1968 | 1968 | Ngữ nghĩa NHÃN không đổi — bảng label_transitions identical từng cặp (961 NORMAL→STRESSED, 21 CRASH→RECOVERY, 19 RECOVERY→NORMAL, 1 RECOVERY→STRESSED, …) |
| Số transition trạng thái nền | (không tồn tại) | 62 (20 NORMAL→CRASH, 1 RECOVERY→CRASH, 21 CRASH→RECOVERY, 20 RECOVERY→NORMAL) | Bề mặt mới theo thiết kế A3.1; tự hoà: 21 lần vào recovery = 20 kết thúc + 1 re-entry |
| Crash ladder tạo ra | 10 | 10 | Điều kiện entry không đổi (§17.1) |
| Tổng snapshot [F5] | 99.30 | 111.13 | **ST §14 [F5]**: snapshot không còn bị daily limit thu nhỏ (F-021) |
| Fill CRASH (nominal) | 24.77 | 26.82 | C0–C3 áp trên snapshot đúng → target lớn hơn (cùng [F5]) |
| Opportunity ladder tạo ra | 20 | 18 | Snapshot [F5] đúng nghĩa claim TRỌN phần Opportunity đã unlock → trong crash không còn phần "unlocked nhưng chưa claim" để mở ladder Opportunity song song (hệ quả trực tiếp của [F5]) |
| Fill OPPORTUNITY | 23 lệnh / 10.78 | 21 lệnh / 8.77 | Hệ quả của dòng trên |
| Tổng fill bị ảnh hưởng | 394 lệnh | 392 lệnh | 24 lệnh chỉ-BEFORE vs 22 chỉ-AFTER; phân kỳ đầu tiên 2021-12-20 07:30 local — đúng crash entry đầu tiên có daily-limit shrink; BASE và SMART fill không đổi |
| Release RECOVERY_END | 74.54 | 84.31 | **ST §18.3**: release chạy cho MỌI kết cục recovery-end (F-001) + reserve lớn hơn do [F5] |
| Release BULLISH_INVALIDATION / OPPORTUNITY_SUSPENDED | 22 / 23 lần | 18 / 19 lần | Ít ladder Opportunity song song hơn (dòng trên) → ít sự kiện vòng đời của chúng |
| Reserved cuối run | 0 / 0 / 0 | 0 / 0 / 0 | Trên dataset này lock của F-001 được "giải cứu muộn" bởi recovery-end sạch kế tiếp; khác biệt nằm ở THỜI ĐIỂM release (sớm và đúng spec) chứ không ở tồn kho cuối. Kịch bản không có recovery sạch kế tiếp (baseline 14 ngày) cho thấy lock vĩnh viễn 27.2 trước fix và 0 sau fix |
| Deployed cuối (BASE/SMART/OPP) | 4450 / 4370 / 35.55 | 4450 / 4370 / 35.59 | Chỉ OPPORTUNITY đổi nhẹ theo cấu trúc fill ở trên |
| ETH accumulated | 21.480637 | 21.480751 | +0.0005% — hệ quả ròng của cấu trúc fill; KHÔNG dùng để tuyên bố edge (DEC-003: dữ liệu tổng hợp chỉ phục vụ verification) |
| Avg cash ratio | 0.068310 | 0.068263 | Giảm nhẹ — vốn được giải phóng đúng hạn nên bớt nằm im; đây là chiều FS-07/FS-02 bị F-001 bóp méo |
| DAILY_LIMIT_BLOCK | 0 | 0 | Dataset này không có ca vượt headroom; nhánh chặn được chứng minh bằng test boundary riêng |

Mọi sai lệch đều truy về đúng hai requirement bị khôi phục ([F5] ST §14; §18.3 + [F1]) và
hệ quả bậc nhất của chúng; không có sai lệch không giải thích được; không có thay đổi nào
ở Base schedule, Smart fill, nhãn regime, hay contribution (đúng kỳ vọng "không đổi
hypothesis"). Điều kiện escalation "metric đổi theo hướng làm chiến lược trông tốt hơn mà
không giải thích được" KHÔNG kích hoạt (thay đổi ETH +5e-6, có giải thích đầy đủ).

## Regression toàn hệ thống (CHECK-A3-09)

`python -m pytest tests/` sau fix: **87 passed, 0 failed, 0 skipped — 456.49s (0:07:36)**
(69 test có sẵn + 18 test WP-A3 mới). Không test hiện có nào bị sửa/nới lỏng/skip; không
expected value nào bị cập nhật. Các test cũ của regime (`tests/test_regime.py`) pass nguyên
trạng vì bề mặt reporting `.regime`/`update()` được giữ tương thích (property alias) — hành
vi nhãn trên dữ liệu thật không đổi, đúng như bảng `label_transitions` identical ở mục impact.
Governance validators (`validate_routing.py`, `validate_easy_roadmap.py`) PASS — xem mục
Verification Evidence.

## Phát hiện mới NGOÀI scope (ghi nhận, KHÔNG sửa — theo chỉ thị S003 mục 5)

### PH-03 — `smart_reservable` trừ `deployed` tích luỹ XUYÊN THÁNG khiến Smart ladder gần như không bao giờ được tạo lại từ tháng thứ 2

Quan sát E1 (impact run, cả BEFORE lẫn AFTER — tức tồn tại TRƯỚC WP-A3, không phải hồi
quy của phiên này): 90 tháng mô phỏng chỉ tạo **2** Smart ladder. Nguyên nhân đọc được từ
code: `smart_reservable(smart_pool, month_smart_budget, unlock)` tính
`unlocked − pool.reserved − pool.deployed`, trong đó `month_smart_budget` là ngân sách
CỦA THÁNG (~30) nhưng `pool.deployed` là luỹ kế TOÀN ĐỜI pool; từ tháng 2 trở đi
`deployed ≈ 30×(số tháng đã qua) ≫ unlocked` → hàm trả 0 vĩnh viễn; Smart chỉ còn giải
ngân qua Month-End settle. Điều này có dấu hiệu mâu thuẫn với ST §6 (unlock/peak là khái
niệm THEO THÁNG — "Peak reset khi sang accounting month mới").

Không thuộc ownership của WP-A3 (không phải F-001/F-021/F-022/F-030; chạm `capital.py`
là vùng cấm của Scope Lock). Đề nghị chủ dự án quyết định nơi xử lý (finding mới cho một
WP lớp A bổ sung, hoặc xác nhận đây là hành vi chủ đích và ghi CONVENTIONS). Lưu ý: nếu
xác nhận là defect, nó ảnh hưởng kết quả mô phỏng ở quy mô LỚN hơn WP-A3 nhiều.

## Key Decisions

- Thiết kế A3.1: tách `state`/`label` trong `RegimeTracker` (CONVENTIONS #14) — chọn thay
  cho phương án chỉ đổi điều kiện nhánh dọn, vì nó bảo đảm [F1] bằng cấu trúc cho MỌI bề
  mặt hiện tại và tương lai, không chỉ vá đúng chỗ F-001.
- Daily limit cho crash zone cưỡng chế tại điểm cam kết action (bước 14), chặn nguyên tử,
  không hoàn headroom khi MISSED (CONVENTIONS #4) — nhất quán với cơ chế cooldown/max_zones
  hiện có và bảo thủ theo BT §1.
- Pool label crash ladder = đa số nguồn vốn, hoà → OPPORTUNITY (CONVENTIONS #16).
- KHÔNG sửa `capital.py` (`opportunity_reservable` giữ nguyên cho ladder thường) — snapshot
  [F5] tính inline trong engine để tôn trọng Scope Lock.

## Risks / Blockers

- BLK-001 giữ nguyên (chỉ chặn T-06). Không đổi nguồn dữ liệu, không official run, không
  verdict — toàn bộ số liệu phiên này là synthetic/dev theo DEC-003.
- PH-03 (trên) cần quyết định của chủ dự án.

## Regression Items

- Không test nào bị nới lỏng hay skip. Không sửa bất kỳ expected value nào của test cũ —
  toàn bộ test hiện có pass nguyên trạng với code mới (xem CHECK-A3-09).

## Do Not Change Yet

- `capital.py` (PH-03) — chờ quyết định chủ dự án.
- `webapp/engine.js` — parity thuộc WP-C4 và phải đợi WP-A3 DONE (nay đã thoả).

## Next Recommended Session

S004 — chủ dự án chọn. Theo đường găng: **WP-A4** (nay hết bị chặn bởi WP-A3; tuần tự hoá
vì cùng sửa `engine.py`). Song song an toàn: WP-A1, WP-A2, WP-C1, WP-D1, WP-D2.
KHÔNG tự mở — chờ chỉ thị.

## Files Next Agent Should Read

- `CLAUDE.md`
- `PROJECT/PROJECT_PROGRESS.md`
- `PROJECT/PROJECT_DECISIONS.md`
- `docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md` (nếu mở WP-A4)
- `docs/sessions/S003-wp-a3-regime-ladder.md` (biên bản này)
- `docs/CONVENTIONS.md` #14–#16 (ngữ nghĩa regime/ladder mới)
