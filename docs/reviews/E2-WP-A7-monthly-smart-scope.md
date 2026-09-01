# E2 INDEPENDENT REVIEW

Review ID:
E2-WP-A7-001

Task / Release:
WP-A7 — Sửa phạm vi kế toán vốn Smart theo accounting month (đóng F-035 / RSK-010) —
CHECK-A7-12 của Completion Gate frozen trong
`docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md`

Reviewer Session:
Phiên reviewer độc lập theo "Solo Independent Review Procedure"
(`governance/core/EVIDENCE_STANDARD.md`). Reviewer KHÔNG phải implementer của S004;
mọi tuyên bố của implementer được coi là narrative KHÔNG đáng tin cho tới khi
reviewer tự tái lập bằng chạy thật.

Executed By:
Reviewer agent E2-WP-A7-001 (độc lập với agent S004)

Timestamp:
2026-08-24T04:36Z

Trạng thái repo được review:
- Commit review: `39a8c22` ("WP-A7 — Sửa phạm vi kế toán vốn Smart theo accounting month (F-035, PA-A)")
- Diff được review: `git diff 68bd8be..39a8c22` (68bd8be = task definition FROZEN, trạng thái trước fix)
- Nhánh: `claude/wp-a3-regime-ladder-3wqw66`, working tree sạch (`git status`: nothing to commit)
- Baseline BEFORE chạy qua git worktree tại `68bd8be` (import ép bằng `PYTHONPATH=<worktree>/src`,
  đã xác nhận `capital.py`/`eth_dca_os` nạp từ worktree trong từng lần chạy)

Môi trường:
- Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pytest 9.1.1
  (trùng bộ phiên bản implementer khai trong handoff S004 — reviewer tự đo)

Probe/scratch của reviewer:
`/tmp/claude-0/-home-user-coin/53a10a43-8743-5c7d-b0f4-0e4a8310206b/scratchpad/e2_wp_a7/`
(probe1..probe7 — mã và output thật được nhúng rút gọn trong report này)

## Scope

Kiểm ĐỘC LẬP tối thiểu năm nội dung do Completion Gate frozen quy định cho CHECK-A7-12:

1. Monthly scope — phạm vi kế toán theo tháng thực sự đúng (CHECK-A7-01/02)
2. Multi-month capital conservation — bất biến vốn qua nhiều tháng (CHECK-A7-06)
3. `smart_unlock_mode` no longer dead — tự dựng kịch bản divergence (CHECK-A7-03)
4. Opportunity Fund non-regression (CHECK-A7-07)
5. No new capital lock/leak path — tự tìm kịch bản khoá/rò vốn ngoài bộ test implementer

Kèm theo: đối chiếu phê phán evidence CHECK-A7-01..11 do implementer viết; xác minh
độc lập tuyên bố cấu trúc PH-04 và trả lời câu hỏi "PH-04 có làm CHECK-A7-03 không đạt
theo câu chữ frozen không". Reviewer KHÔNG sửa bất kỳ file implementation/test nào;
file duy nhất được tạo là report này.

## Inputs Read

- Repository state: HEAD `39a8c22`, working tree sạch; worktree BEFORE tại `68bd8be`
- Frozen task gate: `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` (đọc toàn bộ)
- Actual diff/code: `git diff 68bd8be..39a8c22` (7 file); đọc trọn `src/eth_dca_os/capital.py`,
  `src/eth_dca_os/engine.py`, `tests/test_wp_a7_monthly_scope.py`, `tests/wp_a3_harness.py`,
  `src/eth_dca_os/ladders.py`, `regime.py`, `score.py`, `config.py`
- Governance: `governance/core/EVIDENCE_STANDARD.md` (Solo Independent Review Procedure, E2),
  `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`
- Spec: DM §5/§6/§14; ST §4/§5/§6/§7/§10/§12/§14/§18.3; BT §1/§19
- Bối cảnh: `docs/CONVENTIONS.md` #17 (PA-A), `docs/reviews/PH-03-triage-smart-unlock-scope.md`,
  `docs/sessions/S004-wp-a7-monthly-smart-scope.md`, `PROJECT/PROJECT_PROGRESS.md`

**Kiểm tra toàn vẹn gate frozen** (điều kiện tiên quyết của phiên E2): diff file task
giữa `68bd8be` và `39a8c22` có đúng 47 dòng bị xoá — toàn bộ là placeholder
(`NOT_TESTED`, `...`), status `READY`→`IN_PROGRESS`, checkbox subtask, và registry
"(dự kiến)". **KHÔNG một dòng câu chữ check nào bị sửa** trong khi điền evidence. PASS.

## Independent Verification

Tóm tắt (chi tiết + bằng chứng từng nội dung ở các mục V1–V5 bên dưới):

| Check ID | Nội dung | Status | Evidence Level | Evidence (của reviewer) | Executed By | Timestamp |
|---|---|---|---|---|---|---|
| CHECK-A7-12 / V1 | Monthly scope (CHECK-A7-01/02) | PASS | E2 | probe1 (unit 4 tháng + engine 5 tháng, AFTER và BEFORE), kiểm tra chương trình `smart_reservable` | E2-WP-A7-001 | 2026-08-24T04:36Z |
| CHECK-A7-12 / V2 | Multi-month conservation (CHECK-A7-06) | PASS | E2 | probe2 (6 tháng, 2 crash vắt ranh giới, replayer độc lập từng entry) | E2-WP-A7-001 | 2026-08-24T04:36Z |
| CHECK-A7-12 / V3 | `smart_unlock_mode` không còn trơ (CHECK-A7-03) | PASS | E2 | probe3 (kịch bản tự dựng, phân kỳ tới tận `eth_total`) + rerun test_c | E2-WP-A7-001 | 2026-08-24T04:36Z |
| CHECK-A7-12 / V4 | Opportunity Fund non-regression (CHECK-A7-07) | PASS | E2 | probe4 (diff text hàm, lưới 648 điểm BEFORE==AFTER, engine cap/overflow) | E2-WP-A7-001 | 2026-08-24T04:36Z |
| CHECK-A7-12 / V5 | No new capital lock/leak path | PASS | E2 | probe5a (carry vắt 2 ranh giới) + probe5b (interleaving đối kháng vs reference per-lot) | E2-WP-A7-001 | 2026-08-24T04:36Z |
| CHECK-A7-12 (tổng) | Rà soát độc lập E2 | **PASS (with follow-ups)** | E2 | Toàn bộ report này | E2-WP-A7-001 | 2026-08-24T04:36Z |

Đối chiếu chéo với bộ test/baseline của implementer (chạy lại bởi reviewer — dùng để
đối chiếu, KHÔNG phải bằng chứng chính):

| Lần chạy | Kết quả reviewer | Tuyên bố implementer | Khớp? |
|---|---|---|---|
| `python -m pytest tests/test_wp_a7_monthly_scope.py` (HEAD) | **8 passed** in 1.85s | 8/8 PASS | ✔ |
| Cùng file test, code BEFORE (`PYTHONPATH=<worktree 68bd8be>/src`) | **7 failed, 1 passed** (test_d pass) | `FFFFF.FF` — 7 FAIL + 1 PASS | ✔ |
| FAIL messages BEFORE | `assert 1 == 4` (test_b), "mỗi tháng phải có một Smart ladder khi unlock > 0; có 1" (test_a2), `AttributeError: 'RecordingPool' object has no attribute 'carry_reserved'` (test_f — chứng minh code BEFORE thật sự được nạp) | FAIL "đúng cách" theo bản chất finding | ✔ |
| `pytest tests/test_wp_a3_lifecycle.py tests/test_capital.py tests/test_engine.py` | **34 passed** in 24.37s | 34/34 PASS | ✔ |
| `python -m pytest tests/` (toàn suite, HEAD) | **95 passed** in 356.63s | 95 passed in 354.34s | ✔ |
| Full synth BEFORE (probe7, worktree 68bd8be, cùng dataset SYNTH_SEED) | eth_total **21.480751489892178**, purchases **392**, smart_ladders **2**, smart_via_ladder **0.9106** | 21.480751489892, 392, 2, 0.9106 | ✔ |
| Full synth AFTER (probe6, HEAD) | purchases **543**, smart_via_ladder **1045.9713**, eth_total **21.6370346047919** | 543, 1045.97, 21.637035 (+0.73%) | ✔ |

### V1 — Monthly scope (CHECK-A7-01/02) — PASS

**Kiểm tra chương trình (diff + code):** `smart_reservable` sau fix chỉ đọc
`smart.month_reserved`/`smart.month_deployed` (capital.py:234-236); BEFORE đọc
`smart.reserved`/`smart.deployed` lifetime (xác nhận trực tiếp trên source worktree
68bd8be). Toàn bộ consumer của bộ đếm tháng trong `src/`: chỉ `capital.py` nội bộ và
đúng MỘT hook `smart_pool.open_accounting_month(ts)` tại engine.py:298, đặt SAU
`settle_month_end_smart` và TRƯỚC `apply_monthly_contribution` — đúng cụm bước 3→5
của BT §19. `expire_smart_ladders` (ST §18.3) chạy TRƯỚC khi mở sổ nên reserve Smart
ladder của tháng cũ được release về đúng phạm vi tháng cũ; nguồn reserve vắt tháng duy
nhất còn lại là crash zone (khớp CONVENTIONS #17).

**Probe1 phần A (unit — số học của reviewer, KHÁC test_a của implementer: budget 40,
unlock từng phần 0.6/0.25/1.0, release giữa tháng, 4 tháng).** Output thật (AFTER):

```
PASS - T1 quyền ban đầu = 24 (unlock 0.6) got 24.0
PASS - T1 sau release: quyền = 14 (không relock phần deployed trong tháng) got 14.0
PASS - T1 unlock lên 1.0: quyền = 30
PASS - T1 sau Month-End: quyền = 0
PASS - T2 unlock=1.0: quyền = 40 (lifetime deployed = 40.0)   | T3: (deployed=80.0) | T4: (deployed=120.0)
PASS - T2/T3/T4 unlock=0.25: quyền = 10
PASS - Lifetime deployed bảo toàn = 160.0 ; ledger tháng 1 còn nguyên (append-only)
```

Cùng probe chạy trên code BEFORE (68bd8be):

```
Pool.open_accounting_month tồn tại: False
BEFORE smart_reservable theo tháng (unlock=1.0): [40.0, 0.0, 0.0, 0.0]  lifetime deployed: 160.0
```

**Probe1 phần B (engine — 5 accounting month liên tiếp 2023-03..2023-07, oscore 60).**
AFTER: **5 Smart ladder**, mỗi ladder ở một accounting month riêng; tháng 1–4 eligible
= `30×(25/35)` = 21.428571; tháng 5 eligible = `50×(25/35)` = 35.714286 (ngân sách gồm
cap-overflow +20 của CHÍNH tháng đó — kiểm chéo ST §7 / BT §19 bước 6); S0 execute ở
CẢ 5 tháng; `ledger_conservation_ok` PASS cả 3 pool; lifetime deployed cuối run 170.0
(lịch sử KHÔNG bị reset). BEFORE (cùng probe): **chỉ 1 Smart ladder** — đúng triệu chứng
F-035.

Kết luận V1: vốn deployed tháng trước KHÔNG còn bóp quyền unlock tháng sau trên kịch bản
≥3 tháng (unit 4 tháng + engine 5 tháng); giá trị lifetime không còn được dùng sai phạm
vi trong `smart_reservable`; hành vi tương đương mô hình DM §5 (bộ ba theo tháng, một
tháng OPEN tại mọi thời điểm, `month_opened_at` ≙ `opened_at`); ledger lifetime giữ vai
trò DM §6. **PASS.**

### V2 — Multi-month capital conservation (CHECK-A7-06) — PASS

**Probe2 (kịch bản của reviewer, KHÁC test_f):** 6 tháng 2023-03..2023-08, gồm: fill
S0/S1 (low_dip), **2 crash episode vắt ranh giới tháng** (Mar 29→Apr, Jul 29→Aug),
Month-End cả nhánh OSCORE ≥ 45 lẫn nhánh < 45 (Apr 28, Jun 28 → mua 50% / chuyển 50%),
một ngày `dq INVALID` (May 15), ladder expire hằng tháng. Replayer viết ĐỘC LẬP bởi
reviewer (không dùng `ledger_conservation_ok` của harness) replay TỪNG entry ledger.
Output thật:

```
PASS - replay ledger BASE/SMART/OPPORTUNITY: TOTAL=A+R+D mọi entry, không âm, *_after khớp
PASS - Không tạo/mất vốn: tổng total 3 pool == tổng contribution 600.000000 vs 600.000000
PASS - OVERFLOW: mọi OUT của SMART khớp 1-1 IN của OPPORTUNITY (và ngược lại)
PASS - Có OVERFLOW_OUT MONTH_END_SMART (nhánh OSCORE<45 đã chạy)
PASS - Ledger lifetime: DEPLOY tháng 3 còn nguyên ở cuối run (không reset) n=3
PASS - Đúng 2 crash ladder (2023-03-29, 2023-07-29) — cả hai CANCELLED
PASS - pool.reserved == tổng reserve của zone còn mở  0.000000 vs 0.000000
Smart ladder theo tháng: {'2023-03': 21.4286, '2023-04': 30.0, '2023-05': 21.4286,
                          '2023-06': 25.0714, '2023-07': 35.7143, '2023-08': 50.0}
PASS - Quyền tháng 4 = TRỌN 30.0 dù crash carry ~8.57 đang treo qua ranh giới
PASS - Bộ đếm tháng SMART reconcile tất định từ ledger (carry/month_reserved/month_deployed khớp từng giá trị)
PASS - Carry đã drain về 0 sau khi crash #2 được release trong tháng 8
```

Ghi chú xác nhận độc lập: chuỗi eligible theo tháng ở trên tự giải thích khớp spec —
tháng 6 = `35.1×(25/35)` = 25.0714 vì headroom cap Opportunity chỉ còn 14.9 sau khi
Month-End Apr chuyển 5.1 vào quỹ (overflow 5.1 về Smart tháng 6); tháng 7–8 = `50×…`
vì quỹ đã chạm cap 80. Diff `capital.py` không đụng `_ledger_append`/`_log` và không có
bất kỳ nhánh nào xoá/reset `ledger` hay các trường lifetime (kiểm tra diff từng hunk).
**PASS.**

### V3 — `smart_unlock_mode` no longer dead (CHECK-A7-03) — PASS

**Kịch bản TỰ DỰNG của reviewer (probe3), KHÁC cơ chế test_c của implementer** (test_c
dùng bullish invalidation + OSCORE tụt; probe3 dùng crash chiếm vốn làm HOÃN tạo ladder
one-shot): Day 1 CRASH entry (oscore 80, return7 −0.16) — crash ladder reserve TOÀN BỘ
vốn Smart ⇒ nến đầu tiên có `eff > 0` không tạo được Smart ladder (`reservable = 0`);
OSCORE tụt 50 từ Day 2; exit → RECOVERY Day 7 → NORMAL Day 10 release vốn; NGAY nến đó
engine tạo Smart ladder và TIÊU THỤ `effective_unlock` đang phân kỳ giữa 3 mode.
Zone C0 crash bị `DAILY_LIMIT_BLOCK` (phần Opportunity 6.0 > headroom 20%×20 = 4.0 —
CONVENTIONS #4/WP-A3, reviewer xác nhận từ decision log) nên không có crash fill —
trạng thái vốn tại điểm tạo ladder là `month_deployed = 0`, `available = 30`. Output thật:

```
HWM        eligible=30.0                S0_nominal=9.9      eth_total=0.448551000000
DECAY_HWM  eligible=27.0                S0_nominal=8.91     eth_total=0.438660900000
NO_HWM     eligible=12.857142857142854  S0_nominal=4.242857 eth_total=0.392036142857
PASS - eligible khớp dự đoán canonical: HWM=30×1.0 (giữ peak); DECAY=30×0.9 (đúng MỘT
       bậc decay 0.10/7d kể từ lần revalidate cuối); NO_HWM=30×(15/35) (bám hiện tại)
PASS - Phân kỳ đúng thứ tự ST §6: HWM > DECAY_HWM > NO_HWM > 0
PASS - S0 nominal EXECUTED phân kỳ (downstream execution thật)
PASS - eth_total phân kỳ ở TẦNG OUTCOME trên cùng dataset tất định (3 giá trị khác nhau)
PASS - ledger conservation cả 3 pool, cả 3 mode
```

Ba mode cho ba đường unlock, ba quyền vốn, ba lệnh execute và ba `eth_total` KHÁC NHAU
trên engine run thật, tất định — chiều `smart_unlock_mode` **không còn chết cơ học**,
chứng minh bằng kịch bản reviewer tự nghĩ (mạnh hơn mức "unlock path + quyền vốn" của
test_c: phân kỳ ở đây đi tới tận OUTCOME). Reviewer cũng đã chạy lại test_c/test_c2 của
implementer trong 8/8 PASS và tái lập FAIL-before của chúng. **PASS.**

**Ý kiến độc lập về PH-04** (bắt buộc theo đề bài của phiên E2):

1. *Xác minh cấu trúc:* đúng là engine chỉ TIÊU THỤ `eff_smart_unlock` tại hai điểm —
   tạo Smart ladder one-shot (engine.py:501-502) và crash snapshot [F5] (engine.py:411)
   (grep toàn `src/`; dòng 341 chỉ là điểm TÍNH, mọi consumer khác không tồn tại).
2. *Xác minh empirical:* reviewer tự chạy full synth (SYNTH_SEED mặc định,
   2019-01-01..2026-06-01) 3 mode trên HEAD — `eth_total` trùng **bit-for-bit**
   `21.6370346047919`, purchases 543 cả 3 mode (probe6). Tuyên bố PH-04 của implementer
   là THẬT, không phải che đậy.
3. *Tinh chỉnh của reviewer:* hai mệnh đề đỡ của PH-04 là thuộc tính CỦA DATASET, không
   phải bất biến cấu trúc: (a) "one-shot luôn ở peak==current" chỉ đúng khi nến `eff>0`
   đầu tiên trong tháng đồng thời thoả điều kiện tạo ladder VÀ còn `reservable > 0` —
   probe3 là counterexample: crash chiếm vốn hoãn tạo ladder qua thời điểm phân kỳ, và
   outcome LẬP TỨC phân kỳ mà không cần đổi engine; (b) "crash snapshot ⇒ 1.0 mọi mode"
   cần thêm điều kiện `dq != INVALID` tại nến entry (engine.py:340 ép `s_unl = 0` khi
   INVALID trong khi `regime.update` vẫn nhận oscore). Trên full synth cả hai điều kiện
   đều thoả nên kết quả trùng khít; trên dataset thật thì KHÔNG có bảo đảm nào như vậy.
4. *Trả lời câu hỏi:* CHECK-A7-03 theo CÂU CHỮ frozen — "Không yêu cầu ba mode phải khác
   nhau về `eth_total` trên MỌI dataset — chỉ yêu cầu chứng minh chiều này không còn trơ"
   kèm bảng báo cáo tối thiểu từng mode — **ĐẠT**: test_c của implementer thoả đúng yêu
   cầu tối thiểu, probe3 của reviewer chứng minh thêm ở tầng outcome. PH-04 **không**
   làm CHECK-A7-03 fail; nó là quan sát hợp lệ về sức phân giải của Gate-2 ablation ở
   tầng OUTCOME trên một dataset cụ thể, ngoài Scope Lock WP-A7, chờ owner định đoạt
   (xem Findings/Follow-up).

### V4 — Opportunity Fund non-regression (CHECK-A7-07) — PASS

**Probe4**, ba lớp bằng chứng:

1. *Diff/text:* trích xuất bằng AST — text hàm `opportunity_reservable` VÀ
   `apply_monthly_contribution` **giống hệt từng ký tự** giữa 68bd8be và 39a8c22.
2. *Lưới số:* nạp song song hai phiên bản `capital.py` (BEFORE/AFTER), so
   `opportunity_reservable` trên lưới **648 điểm trạng thái**
   (total×reserved×deployed×unlock×hysteresis×used_today): **0 khác biệt** —
   ngữ nghĩa lifetime/cumulative + daily limit 20% giữ nguyên.
3. *Engine (HEAD):* 6 tháng oscore 60 — quỹ tích luỹ đúng cumulative +20/tháng trong 4
   tháng đầu, chạm cap `80 = 20×4` rồi GIỮ NGUYÊN; tháng 5–6 overflow 20 sang Smart của
   CHÍNH tháng đó (eligible tháng 7/8 = `50×(25/35)` = 35.7143 kiểm chéo); pool
   OPPORTUNITY và BASE có `month_opened_at is None` — engine KHÔNG bao giờ mở sổ theo
   tháng cho chúng (grep: đúng MỘT call site `open_accounting_month`, engine.py:298,
   trên `smart_pool`); hysteresis inactive ở oscore 60 → quỹ không bị ép tiêu.

Cộng thêm ở probe2: hai vế OVERFLOW_OUT/OVERFLOW_IN reason `MONTH_END_SMART` khớp 1-1
về (timestamp, amount) trong giới hạn cap. **PASS.**

### V5 — No new capital lock/leak path — PASS (không tìm thấy đường khoá/rò mới chặn gói)

Reviewer tự thiết kế hai lớp probe NGOÀI những kịch bản implementer đã thử:

**Probe5a (engine): crash zone giữ vốn SMART vắt HAI ranh giới tháng liên tiếp**
(test_f của implementer chỉ vắt MỘT): CRASH entry 2023-03-20, giữ CRASH suốt tháng 4,
release trong tháng 5. Output thật:

```
PASS - crash ladder tạo 2023-03-20, CANCELLED trong tháng 5
PASS - release RECOVERY_END phần SMART xảy ra TRONG THÁNG 5 (reserve sống qua 2 lần mở sổ
       1/4 và 1/5)  amounts=[0.5571, 3.6429, 4.3714]  (tổng 8.5714 — khớp phần smart
       của crash ladder do reviewer tự tính tay từ snapshot)
PASS - carry_reserved drain về 0 (không kẹt vốn vĩnh viễn)
Smart ladder theo tháng: {'2023-03': 21.428571, '2023-04': 30.0, '2023-05': 30.0}
PASS - CẢ tháng 4 và tháng 5 đều TRỌN quyền 30.0 (carry không ăn quyền của BẤT KỲ tháng
       nào nó vắt qua)
PASS - conservation 3 pool; tổng total == contribution 300; reserved cuối == zone mở 20.1
```

**Probe5b (unit): interleaving đối kháng trộn carry + lô tháng mới**, so từng bước với
REFERENCE per-lot ĐÚNG do reviewer viết (reference biết lot thật của từng op — điều mà
code chỉ suy bằng quy tắc carry-first). Chuỗi đối kháng: release lô-THÁNG-MỚI khi carry
còn (code rút nhầm carry → quyền KHÔNG được trả), deploy lô-CARRY vượt carry còn lại
(phần dư 3.0 bị đếm nhầm vào `month_deployed`), rồi drain carry, sang tháng mới; kèm
`open_accounting_month` gọi HAI lần liên tiếp, tháng không contribution, unlock tụt
1.0→0.3 sau khi đã reserve 20. Kết quả đo:

```
worst over-grant  = +0.000000   (KHÔNG tồn tại bước nào code cấp quyền NHIỀU HƠN lot thật)
worst under-grant = -10.000000  (chiều BẢO THỦ duy nhất; bị chặn bởi cỡ carry)
PASS - sau khi carry drain, month_reserved code == true (tự hội tụ phần reserve)
PASS - bias còn lại (3.0) nằm ở month_deployed, đúng bằng phần deploy carry nhầm lô — hết
       sạch tại lần mở sổ kế (M3: code == true toàn bộ)
PASS - double open idempotent; tháng không contribution không nổ, không âm; unlock tụt →
       reservable kẹp 0, không relock; A/R/D không bị bộ đếm tháng đụng tới
```

Kết luận V5: reviewer KHÔNG tìm được đường khoá vốn vĩnh viễn, rò vốn, hay ĐẾM DƯ quyền
tháng nào. Sai lệch duy nhất tồn tại là under-grant TẠM THỜI khi nhận diện lô bị lẫn —
đúng chiều bảo thủ (BT §1), bị chặn bởi cỡ carry, tự hết ở lần mở sổ kế — trùng khớp
với giới hạn ĐÃ ĐƯỢC KHAI BÁO trước trong CONVENTIONS #17 (không phải phát hiện chôn
giấu). Xem Findings để ghi nhận định lượng. **PASS.**

## Mismatches With Implementer Claims

**Không phát hiện mâu thuẫn.** Mọi tuyên bố then chốt reviewer đụng tới đều tái lập được:

- Mẫu FAIL-before `FFFFF.FF` (7 FAIL + 1 PASS, test_d là guard hai chiều) — tái lập chính xác.
- 8/8, 34/34, **95 passed** toàn suite — tái lập (95 passed in 356.63s so với 354.34s của implementer).
- Baseline BEFORE full synth: eth 21.480751489892178 / purchases 392 / 2 Smart ladder /
  via-ladder 0.9106 — tái lập chính xác từng con số bằng run riêng của reviewer trên
  worktree 68bd8be (provenance import đã assert).
- AFTER full synth: purchases 543 / via-ladder 1045.9713 / eth 21.6370346047919 (+0.73%) — khớp.
- PH-04 (3 mode trùng bit-for-bit trên full synth sau fix) — reviewer XÁC NHẬN bằng run riêng;
  đây là khai báo trung thực của implementer về giới hạn còn lại, kèm tinh chỉnh của
  reviewer ở mục V3 (hai mệnh đề đỡ là thuộc tính dataset, không phải bất biến cấu trúc).
- Tuyên bố "validators quét glob `TASK-*.md` nên PASS trên tập rỗng" — reviewer xác nhận
  (`validate_evidence.py:12`, `validate_task_completion.py:9`); giới hạn tooling có sẵn
  từ trước, đã ghi nhận từ S003, ngoài scope WP-A7.
- Câu chữ gate frozen không bị sửa khi điền evidence (47 dòng xoá đều là placeholder/status).

## Findings

- **F-E2A7-01 (LOW — xác nhận định lượng một giới hạn ĐÃ khai báo, không phải defect mới):**
  quy tắc carry-first gây under-grant TẠM THỜI quyền unlock tháng khi release/deploy lô
  tháng mới đan xen carry (đo được tới −10/30 trong kịch bản đối kháng probe5b; phần
  deploy nhầm lô không tự hội tụ trong tháng mà chỉ hết khi mở sổ kế). Chiều sai lệch
  DUY NHẤT là bảo thủ cho strategy (BT §1); không tồn tại over-grant (worst +0.000000).
  Đã được mô tả đúng trong CONVENTIONS #17. Không chặn gói; không yêu cầu hành động.
- **F-E2A7-02 (LOW — hygiene, mới, không chặn):** bộ đếm tháng (`month_reserved` /
  `month_deployed`) TÍCH LUỸ VÔ HẠN không reset trên các pool KHÔNG được mở sổ
  (BASE qua `deploy_from_available` mỗi tranche; OPPORTUNITY qua `reserve`/`deploy`).
  Hiện KHÔNG có reader nào ngoài `smart_reservable` (chỉ đọc pool SMART) — reviewer đã
  grep toàn `src/` và xác nhận `month_opened_at is None` cho BASE/OPPORTUNITY trong run
  thật — nên KHÔNG có tác động hành vi hôm nay; nhưng là bẫy tiềm ẩn nếu mã tương lai
  đọc bộ đếm của pool chưa từng mở sổ. Đề nghị follow-up tài liệu hoá hoặc guard.
- **F-E2A7-03 (INFO — tinh chỉnh PH-04, ngoài scope WP-A7):** phân kỳ 3 mode CÓ THỂ
  chạm tầng OUTCOME ngay với engine hiện tại trên lớp dataset có chuỗi
  "crash chiếm vốn → OSCORE tụt → release" (probe3 chứng minh); đồng thời mệnh đề
  "crash snapshot ⇒ eff = 1.0 mọi mode" cần thêm điều kiện `dq != INVALID` tại nến entry.
  Sức phân giải của chiều `smart_unlock_mode` ở Gate-2 trên DATASET CHÍNH THỨC vì vậy là
  câu hỏi EMPIRICAL, không phải đã bị đóng cơ học — cần được đo trước khi diễn giải
  `Gate2_PreOOS_PassShare`. Chuyển kèm PH-04 cho owner.

Không có finding HIGH/CRITICAL mới trong phạm vi WP-A7.

## Conclusion

**E2 PASS WITH FOLLOW-UPS.**

Cả năm nội dung bắt buộc của CHECK-A7-12 đều PASS bằng bằng chứng chạy thật do reviewer
tự tạo (probe1–probe7, log nhúng ở trên); không nội dung nào dựa vào evidence của
implementer. F-035 được xác nhận đã đóng đúng phạm vi kế toán DM §5, ledger audit DM §6
bảo toàn, không phát hiện đường khoá/rò vốn mới, không mâu thuẫn nào giữa tuyên bố của
implementer và kết quả tái lập độc lập. CHECK-A7-12: **PASS — E2**.

Follow-up bên dưới KHÔNG chặn việc WP-A7 chuyển DONE (không có finding HIGH/CRITICAL
mới trong scope; các follow-up đều LOW/INFO hoặc ngoài scope và đã có chủ trương xử lý).

## Required Follow-up

1. **[Ngoài scope WP-A7 — chờ owner định đoạt, đã ghi nhận là PH-04]** Quyết định phương
   án cho sức phân giải OUTCOME của chiều `smart_unlock_mode` trong Gate-2 ablation
   (mở WP mới / đưa V2.2 / chấp nhận như giới hạn đã biết), NAY BỔ SUNG tinh chỉnh
   F-E2A7-03 của reviewer: trước khi diễn giải Gate-2 trên dataset chính thức, nên ĐO
   xem dataset đó có chuỗi sự kiện làm 3 mode phân kỳ hay không (probe3 là mẫu kịch bản
   tái lập), thay vì mặc định chiều này trơ ở tầng outcome.
2. **[Trong scope diện chạm WP-A7 — hygiene LOW, không chặn DONE]** F-E2A7-02: tài liệu
   hoá (docstring `Pool` hoặc CONVENTIONS #17) — hoặc xử lý ở lần chạm `capital.py`
   hợp lệ kế tiếp — việc bộ đếm tháng trên pool không được mở sổ (BASE/OPPORTUNITY)
   tích luỹ không ngữ nghĩa; cấm mã tương lai đọc bộ đếm của pool chưa `open_accounting_month`.
3. **[Ngoài scope WP-A7 — tồn đọng tooling từ S003]** `validate_evidence.py` /
   `validate_task_completion.py` glob `TASK-*.md` không khớp quy ước đặt tên `WP-*.md`
   → hai validator này hiện PASS rỗng; cần mở rộng glob trong một gói governance-tooling
   để Exit Criteria "Governance validators PASS" có nghĩa thực chất cho các gói WP-*.
