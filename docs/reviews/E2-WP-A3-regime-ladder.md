# E2 INDEPENDENT REVIEW

Review ID:
E2-WP-A3-001

Task / Release:
WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp (đóng F-001, F-021, F-022, F-030)

Reviewer Session:
Phiên reviewer ĐỘC LẬP theo "Solo Independent Review Procedure" (`governance/core/EVIDENCE_STANDARD.md`).
KHÔNG phải phiên implementer S003. Model: Claude (Fable 5), effort max. Mọi tuyên bố PASS của
implementer được coi là narrative chưa tin cậy cho tới khi reviewer tự chạy lại; mọi số liệu
trong file này là output THẬT do reviewer tự thực thi trong phiên review.

Executed By:
Reviewer session E2-WP-A3-001 (agent độc lập, không chung ngữ cảnh với S003)

Timestamp:
2026-08-23

## Scope

- Đối tượng: commit `347ba7c` (HEAD nhánh `claude/wp-a3-regime-ladder-3wqw66`), đối chiếu với
  commit trước remediation `5645a74`.
- Kiểm chứng lại độc lập: CHECK-A3-01, CHECK-A3-03, CHECK-A3-07 (mức E2 cho CHECK-A3-10).
- Tự tìm và thử ÍT NHẤT một kịch bản khoá vốn KHÁC ngoài F-001 (yêu cầu tường minh của
  CHECK-A3-10) — đã thử 4 kịch bản mới + 1 long-run trên cửa sổ khác.
- Kiểm tra diff nằm trong Scope Lock của file task.
- Môi trường chạy: Python 3.11.15, pytest 9.1.1, numpy 2.4.6, **pandas 3.0.5**, chạy từ
  `/home/user/coin`. Script probe của reviewer nằm ngoài repo (scratchpad `/tmp/...`); mọi
  output then chốt được trích vào Phụ lục của file này để tự đứng được.

## Inputs Read

- Repository state: `git log`, `git status` (working tree sạch), HEAD `347ba7c`.
- Frozen task gate: `docs/tasks/WP-A3-regime-va-vong-doi-ladder.md` (Completion Gate FROZEN
  2026-08-23; phần evidence implementer đã điền được đọc như narrative cần đối chứng).
- Actual diff/code: `git diff 5645a74..347ba7c -- src/ tests/ docs/CONVENTIONS.md`; đọc toàn văn
  `src/eth_dca_os/engine.py`, `regime.py`, `ladders.py`, `capital.py`, `config.py`, `score.py`,
  `tests/wp_a3_harness.py`, `tests/test_wp_a3_lifecycle.py`.
- Spec: `docs/spec/02_STRATEGY_SPEC_V2_1_5.md` §14 [F5], §15, §15.1 [F2], §16, §17 (17.1–17.3
  [F1]), §18.2–18.3, §19; `docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §1, §19, §21.2–21.3;
  `docs/CONVENTIONS.md` #4, #5, #6, #14, #15, #16.
- Governance: `EVIDENCE_STANDARD.md` (Solo Independent Review Procedure),
  `E2_INDEPENDENT_REVIEW_TEMPLATE.md`.
- Biên bản implementer: `docs/sessions/S003-wp-a3-regime-ladder.md` (đọc SAU khi đã tự chạy,
  để đối chiếu mismatch).

### Kiểm tra Scope Lock (bước 3)

`git diff --name-only 5645a74..347ba7c` trên vùng cấm (`capital.py`, `score.py`, `verdict.py`,
`failure_signals.py`, `gates.py`, `webapp/`, `docs/spec/`) trả về **rỗng**. Các file bị chạm:
`src/eth_dca_os/engine.py`, `src/eth_dca_os/regime.py`, `tests/test_wp_a3_lifecycle.py`,
`tests/wp_a3_harness.py`, `docs/CONVENTIONS.md`, cùng file governance/tiến độ
(`docs/tasks/…`, `docs/sessions/…`, `PROJECT/PROJECT_PROGRESS.md`). `ladders.py` thuộc Allowed
nhưng không đổi — khớp Changed Files Registry. **Trong Scope Lock: ĐẠT.**

## Independent Verification

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-A3-01 | PASS | E2 | (a) Tự chạy `python -m pytest tests/test_wp_a3_lifecycle.py -k "a3_01" -v` → `test_check_a3_01_crash_recovery_stressed_releases_reserve PASSED`, `test_check_a3_01_reentry_then_clean_end_releases_everything PASSED` (2 passed). (b) Probe unit P1 của reviewer (kịch bản KHÁC — entry qua vế Return24H với `Return7D=None`, recovery-end vào STRESSED qua `r24=-8%`): `state=NORMAL label=STRESSED entry_reason=CRASH_ENTRY_24H`. (c) Probe engine P2 của reviewer (kịch bản KHÁC hẳn implementer: tháng 2024-09, sập giá thật 100→89 ⇒ r24=-11% entry 24H, C1 fill 9.0 trong CRASH qua low thật 81.0, cú sập thứ hai 89→82.5 ⇒ r24=-7.30% ⇒ recovery-end vào STRESSED): ladder `CANCELLED`, zones `{0:CANCELLED, 1:EXECUTED, 2:CANCELLED, 3:CANCELLED}`, release reason `RECOVERY_END` đúng tick kết thúc recovery, đúng pool nguồn: SMART 21.0 + OPPORTUNITY 6.0 = snapshot 36 − deployed 9; không reserve mồ côi (pool reserved 7.14 == tổng zone mở 7.14); ledger 3 pool tự hoà. (d) Đối chứng trên code CŨ `5645a74` cùng kịch bản P2: ladder kẹt `SUSPENDED`, SMART reserved kẹt **18.7**, release RECOVERY_END = **0** — khoá vốn thật trước fix, đóng sau fix. (e) Baseline test-first tái lập trên `5645a74`: cả hai test a3_01 FAIL đúng thông điệp `assert 'SUSPENDED' == 'CANCELLED'`. | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-03 | PASS (kèm mismatch M1) | E2 | (a) Tự chạy `-k "a3_03"` → `test_check_a3_03_f1_stressed_no_effect_on_five_surfaces PASSED`. (b) Audit tĩnh độc lập toàn engine: nhãn (`regime.regime`) chỉ được đọc tại `engine.py:183` (ghi purchase record) và `engine.py:574` (phân rã counter cooldown_override theo regime — BT §16); KHÔNG có nhánh điều khiển nào đọc nhãn; mọi nhánh execution đọc `regime.state` (dòng 259, 389, 393, 446, 454); không module nào khác trong `src/` đọc trường `purchase["regime"]` (grep toàn bộ `src/eth_dca_os`). (c) Counterfactual NGƯỢC CHIỀU implementer (probe P3): implementer ép nhãn LUÔN STRESSED, reviewer ép nhãn KHÔNG BAO GIỜ STRESSED trên kịch bản P2 (labels run A = {CRASH, NORMAL, RECOVERY, STRESSED}, run B = {CRASH, NORMAL, RECOVERY}); cả 5 bề mặt identical: purchases (trừ trường nhãn), eth_total, mọi ladder/zone, ledger RESERVE/DEPLOY/RELEASE 3 pool từng entry, tổng cooldown override, toàn bộ counters, chuỗi DAILY_LIMIT_BLOCK, cash_samples. (d) Trên code cũ: test FAIL (không tồn tại bề mặt `_derive_label`) — khớp tuyên bố "không dựng được counterfactual trước fix". | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-07 | PASS (kèm mismatch M2/M3) | E2 | (a) Tự chạy `-k "a3_07 or a3_02"` → `test_check_a3_07_accounting_invariants_multi_transition PASSED`, `test_check_a3_02_long_run_no_orphan_reserve PASSED` (2 passed, 6.40s). (b) Replay ĐỘC LẬP P8 của reviewer: cửa sổ KHÁC (2020-06-01→2022-12-01, synth SYNTH_SEED 20260822 sinh lại tại phiên review) + validator ledger của RIÊNG reviewer (mạnh hơn: phân loại DEPLOY bằng hai giả thuyết loại trừ nhau; kiểm `TOTAL == luỹ kế CONTRIBUTION±OVERFLOW` tại TỪNG entry, không chỉ cuối run): BASE 121 entries OK, SMART 97 OK, OPPORTUNITY 116 OK; `pool_reserved 5.622970 == open_zone_reserve 5.622970` (lệch 2.66e-15); 6/6 crash ladder `CANCELLED`; ladder terminal không giữ reserve; tổng TOTAL 3 pool = 3100.000000 == tổng contribution; run kết thúc đúng cấu hình F-001 tự nhiên (`state=NORMAL`, `label=STRESSED`) mà KHÔNG kẹt vốn; release `RECOVERY_END` n=16/68.5366; release `CRASH_ENTRY` n=14/19.5237 — ca "cancel Opportunity ladder tại crash entry" XẢY RA THẬT ở long-run và bất biến vẫn giữ. (c) Trên code cũ: a3_07 PASS (guard) — ĐÚNG như biên bản S003 khai (nằm trong 6 guard PASS trước fix), a3_02 FAIL (bề mặt `.state` chưa có). | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-10 — kịch bản khoá vốn tự tìm #1: crash zone `ACTION_PENDING` đúng lúc recovery-end | PASS (không khoá vốn) | E2 | Probe P5: exec config chậm (user_delay 30h + funding 1h, TTL 40h, ON_DEMAND); C1 trigger qua low thật 81.0 vào ngày recovery cuối → action có `execute_at` nằm **7.25h SAU** tick recovery-end. Kết quả: zone `CANCELLED` tại recovery-end, `executed_at=None`, KHÔNG có zombie execution sau cancel (0 purchase nguồn CRASH, 0 entry DEPLOY reason CRASH_ZONE), release `RECOVERY_END` = **36.0** (đủ toàn bộ snapshot), không reserve mồ côi (reserved cuối 20.10 == tổng zone mở — phần smart ladder MỚI được tạo hợp lệ bằng vốn vừa giải phóng), ledger tự hoà. | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-10 — kịch bản #2: Opportunity zone `SUSPENDED` giữ reserve quá `suspended_zone_hold_days` | PASS (không khoá vốn) | E2 | Probe P6: opp ladder eligible 2.0 (o_unl(70)=0.1 × fund 20) tạo Day 2; hysteresis rơi xuống 50 → zones SUSPENDED Day 3; sau **> 7 accounting day** engine release đủ **2.0** với reason `OPPORTUNITY_SUSPENDED` (đo được tại ~8.01 ngày kể từ reserve đầu), toàn bộ zone `CANCELLED`, opp reserved cuối = 3.3e-16 ≈ 0, ledger tự hoà. | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-10 — kịch bản #3: bullish invalidation khi zone `TRIGGERED` bị cooldown chặn | PASS (không khoá vốn) | E2 | Probe P7: S0 fill (cooldown 48h) → Day 3 low thật 90 xuyên S1 (target 94.75) nhưng cooldown chặn action (S1 `triggered_at=None`), close 116 > invalidation 112 hai daily close liên tiếp → ladder `INVALIDATED`, S1 (TRIGGERED) + S2 (ACTIVE) `CANCELLED`, release `BULLISH_INVALIDATION` = **11.4857** == eligible 17.1429 − S0 fill 5.6571, smart reserved cuối 8.9e-16 ≈ 0. | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-10 — kịch bản #4: TTL/MISSED ngay TRONG CRASH (`p2p_unavailable_in_crash=True` + ON_DEMAND) | PASS (không khoá vốn) | E2 | Probe P9: C0 (opp 4 == headroom 4, không bị daily chặn) được tạo action trong CRASH, `execute_at=None` → `MISSED` tại TTL, release `ACTION_MISSED` = **6.8** (đúng 20% snapshot 34) NGAY TRONG CRASH, tại đúng tick TTL (lọc theo timestamp); phần còn lại **27.2** release tại recovery-end; 6.8 + 27.2 == snapshot 34; 0 fill CRASH; không reserve mồ côi; ledger tự hoà. Quan sát phụ: vốn release trong CRASH được engine tái sử dụng ngay để tạo smart/opportunity ladder MỚI trong CRASH; action của chúng cũng MISSED và cũng release — vòng đời vẫn đóng (xem Findings, mục quan sát O-2). | Reviewer E2-WP-A3-001 | 2026-08-23 |
| CHECK-A3-10 — long-run không reserve mồ côi trên cửa sổ khác | PASS | E2 | Probe P8 (bảng CHECK-A3-07 ở trên): trên 30 tháng synth với 6 episode crash, `pool_reserved == open_zone_reserve` (lệch 2.66e-15), không ladder terminal nào giữ reserve, release ACTION_MISSED/TTL n=0, OPPORTUNITY_SUSPENDED n=0, BULLISH_INVALIDATION n=9 — mọi reserve đều truy vết được về một đường kết thúc hợp lệ. | Reviewer E2-WP-A3-001 | 2026-08-23 |

**Kết luận riêng cho câu hỏi trung tâm của CHECK-A3-10: reviewer KHÔNG tìm thấy kịch bản khoá
vốn mới nào** sau 4 kịch bản có chủ đích + 1 long-run cửa sổ khác + rà tĩnh vòng đời (mọi trạng
thái giữ reserve của Smart/Opportunity/Crash ladder đều đối chiếu được với ít nhất một đường
release đã được chạy thật ở trên: fill, TTL/MISSED, bullish invalidation, hysteresis-suspend
7 ngày, expiry Smart cuối tháng/Opportunity 90 ngày, cancel tại crash entry, recovery-end).

## Mismatches With Implementer Claims

Bốn mismatch tìm thấy — không mismatch nào lật kết luận PASS của check tương ứng, nhưng đều
phải được ghi nhận vì evidence narrative mô tả NHIỀU hơn những gì test thực sự chứng minh trên
môi trường này (gốc rễ là Finding F-E2-01 dưới đây):

- **M1 — CHECK-A3-03**: evidence trong file task mô tả dataset 18 ngày "có smart ladder,
  cooldown block, crash, daily-limit block, recovery, opportunity ladder". Thực chạy trên môi
  trường này (pandas 3.0.5): mọi spec `price`/`low_dip` theo ngày của harness bị bỏ qua âm
  thầm (close của TOÀN BỘ run = 100.0). Hệ quả trong đúng kịch bản đó: **0** sự kiện
  `DAILY_LIMIT_BLOCK` (chuỗi "identical" là hai danh sách RỖNG), **0** cooldown override,
  không có S1 trigger dưới cooldown (Day 3 low_dip 94 bất động), không có Opportunity fill
  (Day 16 price 93 bất động). Các bề mặt vẫn được so sánh đúng logic và test PASS hợp lệ,
  nhưng độ phủ kịch bản hẹp hơn mô tả. Reviewer đã bù bằng probe P2/P3 (357 sự kiện
  DAILY_LIMIT_BLOCK thật, cooldown thật, fill CRASH thật) — [F1] vẫn đứng vững.
- **M2 — CHECK-A3-07**: evidence viết test multi-transition "có cancel Opportunity ladder tại
  crash entry — đúng ca 'chuyển Opportunity sang Crash'". Thực chạy: kịch bản a3_07 trên môi
  trường này KHÔNG tạo ra bất kỳ Opportunity ladder nào (recorder chỉ ghi SMART + CRASH),
  nên ca đó không xảy ra TRONG TEST NÀY. Ca này CÓ xảy ra thật ở test long-run a3_02 và ở
  probe P8 của reviewer (release `CRASH_ENTRY` n=14 / 19.5237) — bất biến kế toán giữ.
- **M3 — CHECK-A3-07**: chú thích kịch bản "C1 trigger trong CRASH" (Day 7 `low_dip: 91`)
  không xảy ra (low_dip bất động). Fill CRASH duy nhất trong test đó là C0 (2.914) nhờ C0
  nằm đúng anchor. Reviewer đã chứng minh ca "C-zone sâu hơn trigger và fill trong CRASH"
  bằng probe P2 (C1 fill 9.0 qua low thật 81.0).
- **M4 — CHECK-A3-08** (ngoài ba check bắt buộc, ghi nhận khi đối chiếu): bảng impact
  BEFORE→AFTER được sinh bởi `wp_a3_impact.py` nhưng script này KHÔNG tồn tại trong repo
  lẫn git history → bảng không tái lập nguyên trạng từ trạng thái repo. Reviewer đã tự
  spot-check impact trên dataset/cửa sổ riêng (synth 2018→2023-07, engine 2019-01→2023-07,
  BEFORE = `5645a74`, AFTER = `347ba7c`): `sum_f5_snapshot` 92.281 → 105.588 (đúng chiều
  F-021), fill CRASH 24.638 → 25.926, release `RECOVERY_END` 67.644 → 79.662 (đúng chiều
  F-001/§18.3), Opportunity ladder 8 → 7 và fill OPPORTUNITY 4.973 → 3.864 (đúng hệ quả
  [F5] claim trọn phần unlocked), BASE fill 2700.0 == 2700.0 và SMART fill 2620.0 == 2620.0
  (bất biến đúng như khai), `label_transitions` 1144 == 1144 (ngữ nghĩa nhãn không đổi),
  ETH +0.003% cùng bậc với +0.0005% đã khai. **Mọi chiều hướng khớp giải thích của
  implementer**; chỉ thiếu tính tái lập của con số nguyên bảng.

Các điểm ĐÃ đối chiếu và KHỚP (không mismatch): baseline test-first (tái lập trên `5645a74`
đúng cả thông điệp `assert 'SUSPENDED' == 'CANCELLED'` của a3_01; a3_03/a3_02 FAIL; a3_07
thuộc nhóm 6 guard PASS trước fix đúng như S003 khai); snapshot 36 = smart 30 + opp 6; grep
"nhãn chỉ còn ở purchase record và counter phân rã" (reviewer xác nhận độc lập); PH-03 được
implementer TỰ KHAI trung thực (reviewer xác nhận độc lập cơ chế và số liệu: 0 Smart ladder
trên 54 tháng cửa sổ spot-check, SMART fill 2620 đi toàn bộ qua `MONTH_END_SMART`).

## Findings

- **F-E2-01 (MEDIUM — hạ tầng test / độ chính xác evidence, không phải lỗi engine):**
  `tests/wp_a3_harness.py::build_dataset` dùng `idx.asi8 // 10**9` để đổi index 15m ra
  epoch-seconds, giả định datetime64[ns]. Trên pandas 3.0.5 (môi trường phiên này và phiên
  S003 theo biên bản), `pd.date_range(...)` trả `datetime64[us, UTC]` → `asi8` là micro-giây
  → ánh xạ "ngày local → giá" sụp về một hằng số, khiến spec `price` và `low_dip` theo ngày
  **bất động âm thầm** (close toàn run = giá Day 1; bảng daily-close cho invalidation thì
  ĐÚNG vì dùng `Timestamp.value` là ns). Bằng chứng: probe P0 — cùng day_specs, harness gốc
  cho `closes={100.0}`, builder sửa đơn vị cho `closes={89.0, 100.0}`/`lows` chứa 81.0.
  Hệ quả: các mismatch M1–M3; các test engine-level của WP-A3 vẫn PASS nhưng một phần độ phủ
  kịch bản chỉ tồn tại trên giấy, và suite này sẽ tiếp tục degenerate âm thầm trên pandas ≥3.
  Khuyến nghị sửa (một dòng): tính epoch-seconds bằng phép chia Timedelta như
  `engine._epoch_seconds`, kèm một assert tự kiểm trong builder (ví dụ: close của ngày có
  `price` đặt phải xuất hiện trong dataset). Reviewer KHÔNG sửa file này (ngoài quyền ghi
  của phiên review).
- **F-E2-02 (LOW — reproducibility):** script đo impact `wp_a3_impact.py` được viện dẫn ở
  CHECK-A3-08/S003 nhưng không được commit (không có trong working tree lẫn git history) —
  trái tinh thần BT §20 (reproducibility). Chiều hướng kết quả đã được reviewer xác nhận độc
  lập (M4), nhưng bảng số nguyên bản không tái lập được từ repo.
- **O-1 (quan sát, KHÔNG phải finding mới của phiên này):** PH-03 (`smart_reservable` trừ
  `deployed` luỹ kế xuyên tháng → Smart ladder gần như không được tạo lại từ tháng 2) đã
  được implementer tự khai trong S003, nằm ngoài scope WP-A3 (`capital.py` là vùng cấm).
  Reviewer xác nhận độc lập cả cơ chế (đọc code) lẫn hiện tượng (spot-check: 0 Smart ladder /
  54 tháng; SMART giải ngân 100% qua Month-End). Tồn tại TRƯỚC WP-A3, không phải hồi quy của
  gói này; cần quyết định của chủ dự án như S003 đã đề nghị.
- **O-2 (quan sát hành vi, không khoá vốn):** engine cho phép tạo Smart/Opportunity ladder
  MỚI ngay TRONG CRASH bằng vốn vừa được release (ví dụ sau ACTION_MISSED — probe P9); spec
  không cấm tường minh, vòng đời của các ladder này vẫn đóng (đường release đầy đủ). Nếu chủ
  dự án muốn cấm/giới hạn, cần một convention hoặc đưa vào V2.2 — không chặn WP-A3.

## Conclusion

**E2 PASS.**

- CHECK-A3-01, CHECK-A3-03, CHECK-A3-07: PASS — reviewer tự chạy lại test của implementer VÀ
  kiểm chứng chéo bằng kịch bản/validator của riêng mình (unit, engine-level với biến động giá
  thật, counterfactual ngược chiều, replay ledger cửa sổ khác, đối chứng code cũ `5645a74`
  cho cả baseline FAIL lẫn hiện tượng khoá vốn 18.7 trên kịch bản riêng của reviewer).
- CHECK-A3-10 (nội dung trung tâm): sau 4 kịch bản khoá vốn tự nghĩ (ACTION_PENDING tại
  recovery-end; SUSPENDED quá 7 ngày; invalidation với zone TRIGGERED bị cooldown chặn;
  TTL/MISSED trong CRASH với p2p off) và 1 long-run cửa sổ khác: **không tìm thấy đường khoá
  vốn nào còn lại**; mọi reserve truy vết được về đúng một đường release đã chạy thật.
- Bốn mismatch (M1–M4) là về ĐỘ CHÍNH XÁC CỦA NARRATIVE EVIDENCE và tính tái lập, bắt nguồn
  từ F-E2-01/F-E2-02; chúng KHÔNG làm sai hành vi engine, KHÔNG lật kết luận của check nào,
  và phần độ phủ bị thiếu đã được chính phiên review này phủ lại bằng chạy thật.

## Required Follow-up

1. **Sửa F-E2-01** (`tests/wp_a3_harness.py::build_dataset` — epoch-seconds đúng đơn vị + assert
   tự kiểm), sau đó chạy lại `tests/test_wp_a3_lifecycle.py` toàn bộ. Việc sửa nằm trong vùng
   Allowed (`tests/`) của WP-A3; khuyến nghị làm trước khi đóng task (MICRO), hoặc chủ dự án
   chấp nhận rủi ro và mở task riêng — quyết định thuộc chủ dự án.
2. **F-E2-02**: commit script đo impact (hoặc tái tạo và commit) để CHECK-A3-08 tái lập được
   từ trạng thái repo, đúng BT §20.
3. Cập nhật evidence CHECK-A3-03/A3-07 trong file task cho khớp sự kiện thực (sau khi sửa
   harness, các câu mô tả kịch bản sẽ đúng trở lại nếu chạy lại và xác nhận).
4. PH-03 (O-1): chờ quyết định chủ dự án (đã nằm trong Risks/Blockers của S003).
5. Điền kết quả E2 này vào CHECK-A3-10 của file task (Status PASS, Evidence Level E2, trỏ tới
   file này) — thao tác điền thuộc phiên implementer/chủ dự án, không thuộc phiên review.

---

## Phụ lục — bằng chứng chi tiết

Output thật do reviewer chạy trong phiên này; vài dòng dài được NGẮT DÒNG lại cho dễ đọc,
con số giữ nguyên như output gốc.

### A. Chạy lại test của implementer trên HEAD `347ba7c`

```
tests/test_wp_a3_lifecycle.py::test_check_a3_01_crash_recovery_stressed_releases_reserve PASSED
tests/test_wp_a3_lifecycle.py::test_check_a3_01_reentry_then_clean_end_releases_everything PASSED
tests/test_wp_a3_lifecycle.py::test_check_a3_03_f1_stressed_no_effect_on_five_surfaces PASSED
======================= 3 passed, 15 deselected in 0.78s =======================

tests/test_wp_a3_lifecycle.py::test_check_a3_07_accounting_invariants_multi_transition PASSED
tests/test_wp_a3_lifecycle.py::test_check_a3_02_long_run_no_orphan_reserve PASSED
======================= 2 passed, 16 deselected in 6.40s =======================
```

### B. Probe của reviewer trên HEAD `347ba7c` (8/8 PASS)

```
P0: harness goc: closes=[100.0] lows=[100.0] | builder sua: closes=[89.0, 100.0] lows=[81.0, 89.0, 100.0]
P1: state=NORMAL label=STRESSED entry_reason=CRASH_ENTRY_24H
P2: snapshot=36.0 crash_fill=9.0 release_RECOVERY_END smart=21.0 opp=6.0 ladder=CANCELLED
    zones={0: 'CANCELLED', 1: 'EXECUTED', 2: 'CANCELLED', 3: 'CANCELLED'}
    reserved_end=7.140000 open_zone=7.140000 n_daily_blocks=357
P3: labels_a=['CRASH', 'NORMAL', 'RECOVERY', 'STRESSED'] labels_b=['CRASH', 'NORMAL', 'RECOVERY']
    purchases=6 identical=True
P5: execute_at-rec_end=7.25h release_RECOVERY_END=36.0 c1_status=CANCELLED crash_buys=0
    reserved_end=20.100000
P6: reserved=2.0 released=2.0 release_ts_hold_days=8.01
    zones=['CANCELLED', 'CANCELLED', 'CANCELLED', 'CANCELLED', 'CANCELLED']
    opp_reserved_end=3.3306690738754696e-16
P7: eligible=17.1429 S0_fill=5.6571 released_BULLISH_INVALIDATION=11.4857 ladder=INVALIDATED
    smart_reserved_end=8.881784197001252e-16
P9: snapshot=34.0 rel_ACTION_MISSED=6.8000 rel_RECOVERY_END=27.2000 c0=MISSED lad=CANCELLED
============================== 8 passed in 0.79s ==============================
```

### C. Replay độc lập P8 (cửa sổ 2020-06-01 → 2022-12-01, validator của reviewer)

```
pool BASE: replay=OK (OK) {'n_entries': 121, 'available': 50.0, 'reserved': 0.0,
    'deployed': 1500.0, 'contributed_net': 1550.0}
pool SMART: replay=OK (OK) {'n_entries': 97, 'available': 50.0,
    'reserved': 8.881784197001252e-16, 'deployed': 1420.0, 'contributed_net': 1470.0}
pool OPPORTUNITY: replay=OK (OK) {'n_entries': 116, 'available': 47.368203065558774,
    'reserved': 5.622969529128833, 'deployed': 27.0088274053124, 'contributed_net': 80.0}
pool_reserved=5.622970 vs open_zone_reserve=5.622970 (lech 2.66e-15)
regime cuoi: state=NORMAL label=STRESSED
crash ladders: n=6 theo status={'CANCELLED': 6}
release RECOVERY_END: n=16 tong=68.5366
release CRASH_ENTRY (cancel Opportunity tai crash entry): n=14 tong=19.5237
release ACTION_MISSED/TTL: n=0 | OPPORTUNITY_SUSPENDED: n=0 | BULLISH_INVALIDATION: n=9
tong TOTAL 3 pool = 3100.000000; tong contribution rong = 3100.000000
KET LUAN P8: PASS
```

### D. Bộ test mới chạy trên code CŨ `5645a74` (baseline đối chứng)

```
test_check_a3_01_crash_recovery_stressed_releases_reserve FAILED
  E  AssertionError: assert 'SUSPENDED' == 'CANCELLED'
test_check_a3_01_reentry_then_clean_end_releases_everything FAILED
test_check_a3_03_f1_stressed_no_effect_on_five_surfaces FAILED
test_check_a3_07_accounting_invariants_multi_transition PASSED   (guard — đúng như S003 khai)
test_check_a3_02_long_run_no_orphan_reserve FAILED
================== 4 failed, 1 passed, 13 deselected in 7.06s ==================
```

Kịch bản P2 của reviewer trên code cũ (chứng minh khoá vốn trước fix):

```
regime cuoi: NORMAL | co .state? False
crash ladder status=SUSPENDED zones=['EXECUTED', 'EXECUTED', 'SUSPENDED', 'SUSPENDED'] reserve dang giu=18.7
SMART reserved cuoi=18.7 | OPP reserved cuoi=1.8
release RECOVERY_END: 0
```

### E. Spot-check impact độc lập (BEFORE `5645a74` vs AFTER `347ba7c`, synth 2018→2023-07, engine 2019-01-01→2023-07-01)

| Metric | BEFORE | AFTER | Chiều hướng vs giải thích của implementer |
|---|---|---|---|
| n_crash_ladders | 7 | 7 | Khớp (entry §17.1 không đổi) |
| sum [F5] snapshot | 92.281450 | 105.588113 | Khớp (F-021: hết bị daily limit thu nhỏ) |
| Fill CRASH (nominal) | 24.637599 | 25.926415 | Khớp |
| Opportunity ladder | 8 | 7 | Khớp (snapshot claim trọn phần unlocked) |
| Fill OPPORTUNITY | 4.972708 | 3.863683 | Khớp |
| Fill BASE / SMART | 2700.0 / 2620.0 | 2700.0 / 2620.0 | Khớp (bất biến) |
| release RECOVERY_END | 67.643850 | 79.661698 | Khớp (§18.3 chạy cho mọi kết cục) |
| label_transitions | 1144 | 1144 | Khớp (ngữ nghĩa nhãn không đổi) |
| ETH total | 15.665030478 | 15.665499517 | +0.003%, cùng bậc với +0.0005% đã khai (cửa sổ khác) |
| Reserved cuối 3 pool | 0 / 0 / 0 | 0 / 0 / 0 | Khớp ghi chú "giải cứu muộn bởi recovery sạch kế tiếp" |

### F. Toàn cảnh suite (đối chứng bổ sung cho CHECK-A3-09)

Reviewer chạy lại toàn bộ `python -m pytest tests/` trên HEAD `347ba7c`:

```
87 passed in 467.43s (0:07:47)
```

**87 passed, 0 failed, 0 skipped** — khớp tuyên bố CHECK-A3-09 (họ ghi 456.49s; chênh lệch
thời lượng chạy không phải mismatch). Lưu ý: kết quả "87 passed" này bao gồm các test
engine-level đang chịu ảnh hưởng F-E2-01 (PASS hợp lệ nhưng độ phủ kịch bản hẹp hơn mô tả).
