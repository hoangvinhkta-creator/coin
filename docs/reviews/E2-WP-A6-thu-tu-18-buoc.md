# E2 INDEPENDENT REVIEW

Review ID:
E2-WP-A6-001

Task / Release:
WP-A6 — Thứ tự xử lý 18 bước mỗi nến 15m (Backtest §19), đóng F-018 / F-019 —
CHECK-A6-08 của Completion Gate trong `docs/tasks/WP-A6-thu-tu-xu-ly-18-buoc.md`

Reviewer Session:
Phiên reviewer độc lập theo "Solo Independent Review Procedure"
(`governance/core/EVIDENCE_STANDARD.md` §"Solo Independent Review Procedure").
Reviewer KHÔNG phải implementer của S014 và không có ký ức về phiên đó. Thứ tự đọc được
ép cứng: (1) spec BT §18/§19/§21.1 + IP §7 + phần câu hỏi của task file → (2) diff và
toàn bộ `engine.py` → (3) tự chạy test + công cụ đo → (4) CHỈ SAU ĐÓ mới đọc
CONVENTIONS #18/#19, Evidence đã điền của CHECK-A6-01..07 và biên bản S014 để đối chiếu.
Mọi tuyên bố PASS của implementer được coi là narrative không đáng tin cho tới khi
reviewer tái lập bằng chạy thật.

Executed By:
Reviewer agent E2-WP-A6-001 (độc lập với agent S014)

Timestamp:
2026-09-03T04:15Z (bắt đầu) — xem mục "Kết quả chạy thật" cho mốc từng lần chạy

Trạng thái repo được review:
- Nhánh `claude/coindca-data-stream-vv0vwv`, HEAD `a2fa9a5`, working tree sạch trước khi
  reviewer tạo file này (`git status --short` rỗng).
- Diff được review: `git diff b717634..a2fa9a5 -- src/eth_dca_os/engine.py`
  (`b717634` = baseline trước khi WP-A6 mở, khớp `PROJECT/REVIEW_BUDGET_LEDGER.md` dòng
  `CAP-ORDER`). Trong `src/` CHỈ `engine.py` đổi (139+/108−) — đúng Expected Touch Area.
- Baseline BEFORE chạy qua `git archive b717634 src` vào scratch, import ép bằng `--src`
  của `tests/wp_a6_impact_tool.py` (đã xác nhận `code_path` trong từng JSON trỏ đúng cây
  `base/` hoặc `cur/`), và qua `load_engine_from_source(git show b717634:…engine.py)` cho
  probe kịch bản.

Môi trường (reviewer tự đo): Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pytest 9.1.1

Probe/scratch của reviewer:
`/tmp/claude-0/-home-user-coin/230fe132-b998-5ef8-81a4-6c4aec014c5c/scratchpad/`
(`rev_probe.py`, `impact/wp_a6_impact_rev_*.json`, `pytest_full.log`) — output thật được
nhúng rút gọn dưới đây.

## Scope

1. Tự chép 18 bước từ BT §19, tự đối chiếu với `run_engine()` hiện tại, tự kết luận thứ tự
   có khớp không — TRƯỚC khi đọc kết luận của implementer.
2. Tự đánh giá test thứ tự (`tests/test_wp_a6_processing_order.py`,
   `tests/wp_a6_order_harness.py`) có kiểm THỨ TỰ THẬT (side-effect) hay không; tự chạy
   test trên engine baseline `b717634` để xác nhận test đỏ đúng chữ ký F-018.
3. Tự chạy toàn bộ suite; tự chạy công cụ đo tác động trên baseline / hiện tại / biến thể
   cô lập "ladder tạo trước bước 13" để tái lập ΔETH.
4. Đánh giá độc lập H-15 (zone TRIGGERED trong chu kỳ INVALID) dựa trên ST §3, §15.1,
   CONVENTIONS #6 và `score.py`.
5. Đối chiếu với CONVENTIONS #18/#19, Evidence CHECK-A6-01..07, biên bản S014; ghi khác
   biệt; xác nhận lại verdict từng CHECK; verdict CHECK-A6-08.

Ngoài scope: không sửa file production nào; không commit/push; finding mới được chuyển
cho orchestrator route theo REVIEW_PROTOCOL, reviewer không tự sửa.

## Inputs Read

Theo đúng thứ tự thời gian:
- Giai đoạn 1: `docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §18, §19, §21.1;
  `docs/spec/05_IMPLEMENTATION_PLAN_V2_1_5.md` §7; task file WP-A6 các mục Objective /
  Trình tự bắt buộc / Sai lệch đã biết (F-018) / Scope / Out of Scope / Expected Touch
  Area / Completion Gate (CHỈ tiêu đề câu hỏi CHECK-A6-01..08) / Notes;
  `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`; `PROJECT/HARDENING_BACKLOG.md`
  H-15.
- Giai đoạn 2: `git diff b717634..a2fa9a5 -- src/eth_dca_os/engine.py`; toàn bộ
  `src/eth_dca_os/engine.py`; `src/eth_dca_os/ladders.py`; `src/eth_dca_os/capital.py`
  (để phán xét tác dụng phụ thật của `deploy_from_reserved`, `reserve`, `release`,
  `cancel_open_zones`, `created_at`); `docs/spec/02_STRATEGY_SPEC_V2_1_5.md` §3, §5, §14,
  §15/§15.1, §17, §18; `docs/CONVENTIONS.md` #6 (quy ước có sẵn từ trước WP-A6);
  `src/eth_dca_os/score.py` phần `REQUIRED_DAILY_INDICATORS` / `invalid_mask` (chỉ đọc).
- Giai đoạn 3: `tests/test_wp_a6_processing_order.py`, `tests/wp_a6_order_harness.py`,
  `tests/wp_a6_impact_tool.py`; chạy thật (mục dưới).
- Giai đoạn 4 (sau khi đã viết xong mục A–C bên dưới): `docs/CONVENTIONS.md` #18, #19 và
  mục "Ghi chú cho WP-D2 từ WP-A6"; Evidence/Status của CHECK-A6-01..07;
  `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md`; `PROJECT/REVIEW_BUDGET_LEDGER.md`.

---

# PHẦN A — Kết luận ĐỘC LẬP của reviewer (viết trước khi đọc kết luận implementer)

## A.1 18 bước BT §19 theo reviewer chép

| # | Bước (rút gọn từ chữ spec) |
|---|---|
| 1 | Tiến đồng hồ tới nến 15m kế tiếp |
| 2 | Phát hiện accounting month mới |
| 3 | Hết hạn Smart ladder tháng trước + đóng sổ cuối tháng |
| 4 | Reset Smart HWM / mode theo `smart_unlock_mode` |
| 5 | Monthly contribution |
| 6 | Trần Opportunity Fund, overflow sang Smart tháng đó |
| 7 | Reset bộ đếm theo accounting day (00:00 Asia/Ho_Chi_Minh) |
| 8 | Kích hoạt daily score + data-quality snapshot nếu nến daily nguồn đã đóng |
| 9 | Sự kiện Base theo lịch, gồm Base execute sớm |
| 10 | Cập nhật Market Regime + bộ đếm Crash-Exit/Recovery (gồm nhãn STRESSED) |
| 11 | Hết hạn cooldown + điều kiện override |
| 12 | Pending action tới hạn (user_delay + funding_delay); TTL; MISSED |
| 13 | Trigger Smart (LOW ≤ zone), confirmation Opp (CLOSE ≤ zone); sắp thứ tự §15.1 [F2] |
| 14 | Tạo/điều chỉnh reservation; pool availability; max_zones_per_cycle (áp SAU sắp thứ tự) |
| 15 | Funding state + execution priority Base → Smart → Opportunity |
| 16 | Thực thi fill tại execution proxy; fee + slippage |
| 17 | Cập nhật capital ledger, portfolio, cooldown |
| 18 | Ladder completion / suspension / expiry / bullish invalidation; decision log, purchase log, diagnostic snapshot |

Ràng buộc kèm theo: BT §18 (không interpolate 15m thiếu; indicator daily bắt buộc thiếu →
giữ score ≤ 24h rồi đóng băng unlock mới; DEGRADED/INVALID theo ST §3); BT §21.1
no-lookahead ("score của ngày D không dùng dữ liệu nào sau khi nến daily D đóng"); IP §7
"Không phát hiện lookahead trong unit test và integration test".

## A.2 Đối chiếu độc lập `run_engine()` @ `a2fa9a5` với 18 bước

Bảng dưới là phán xét của RIÊNG reviewer sau khi đọc toàn bộ hàm (không dựa vào comment
đánh số của implementer — reviewer tự dò tác dụng phụ của từng khối qua `capital.py`,
`ladders.py`).

| Bước §19 | Vị trí trong `run_engine()` (dòng @a2fa9a5) | Khớp? | Ghi chú của reviewer |
|---|---|---|---|
| 1 | L314 `ts = c["ts"][i]` | KHỚP | |
| 2–6 | L325–347: `expire_smart_ladders` → Base tồn (gap) → `settle_month_end_smart` → `open_accounting_month` → `su.month_reset` → `apply_monthly_contribution` (cap/overflow bên trong) | KHỚP | Thứ tự nội bộ 3 → 4 → 5/6 đúng chữ. |
| 7 | L350–353 | KHỚP | |
| 8 | L357–367 (chỉ kích hoạt oscore/dq/r7/adr30/daily_close) + L370–379 (unlock, `hyst.update`) | KHỚP | `hyst.update` chỉ đổi cờ `opp_active` (dẫn xuất của score) — chuyển trạng thái zone nằm ở 18. Reviewer coi đây là cách đọc hợp lý của "kích hoạt snapshot". |
| 9 | L382–409 (Base Day 3/13/23, Day 25/28 Month-End, Base advance khi score ≥ 70) | KHỚP | Day 28 gọi `expire_smart_ladders` + `settle_month_end_smart` ở bước 9 — đó là CONVENTIONS #7 có từ trước, không thuộc WP-A6; spec §19 chỉ đặt đóng sổ ở bước 3 (rollover). Mơ hồ spec, không phải sai lệch của gói này. |
| 10 | L417–439: `regime.update`; tại crash entry: cancel Opp zone → release → snapshot [F5] | KHỚP | ST §14 đòi cancel/release "tại thời điểm vào CRASH" và snapshot "đo NGAY SAU cancel/release" → đặt ở 10 là hợp lý. Tạo Crash ladder (reservation mới) KHÔNG ở đây nữa. |
| 11 | L442–444 | KHỚP | Đọc `cooldown_until`/`last_exec_price` TRƯỚC mọi fill của nến. |
| 12 | L448–463: chỉ gom `due_fills` + đánh MISSED/TTL (release) | KHỚP | Reviewer chấp nhận cách đọc "xử lý" = xác định đủ điều kiện, vì §19 đặt "thực thi fill" tường minh ở 16. |
| 13 | L467–482 | KHỚP | `candidates` gồm cả zone đã TRIGGERED từ nến trước (giữ-TRIGGERED §15.1/CONV #6). Ladder tạo ở 14 chưa tồn tại → không trigger cùng nến. |
| 14 | L485–521 (14a Crash ladder từ snapshot bước 10) → L524–561 (14b Smart/Opp ladder) → L568–602 (14c TRIGGERED→ACTION_PENDING, sort `zone_order_key`, max_zones SAU sort, cooldown/override, INVALID chặn, daily limit Crash) | KHỚP | Thứ tự nội bộ 14a/14b/14c không được §19 quy định; reviewer kiểm: 14c không reserve thêm vốn nên vị trí tương đối 14b/14c chỉ ảnh hưởng `opp_used_today` cho daily-limit của Crash zone — cùng cơ chế trước và sau WP-A6. |
| 15 | L607 `due_fills.sort(zone_order_key)` | KHỚP (một phần mơ hồ) | "Giải quyết funding state" thực tế đã được quyết ở `create_action` (14c: `execute_at=None` khi P2P không khả dụng trong CRASH; funding_delay cộng vào `execute_at`). §19 bước 12 tự nó nhắc "user_delay + funding_delay" nên reviewer coi đây là mơ hồ của spec, không phải sai lệch. Ưu tiên Base→Smart→Opp: Base luôn fill ở bước 9 nên thứ tự pool giữa zone fill chỉ còn Smart/Opp/Crash — sort đúng khoá §15.1. |
| 16–17 | L612–620: `deploy_zone` (ledger R→D) → `record_purchase` (fee/slippage, portfolio, cooldown, last_exec_price) | KHỚP | Hai bước là một giao dịch nguyên tử; reviewer không thấy lý do tách. |
| 18 | L626–673: 18a bullish invalidation (guard `created_at < ts`) → 18b hysteresis Opp → 18c Crash suspend/cancel theo chuyển trạng thái nền → 18d expiry Opp 90 ngày + completion; L676–679 cash snapshot | KHỚP | Decision/purchase log ghi rải rác ở nơi phát sinh — không ảnh hưởng thứ tự side-effect. |

**Kết luận A.2 của reviewer: thứ tự thực thi hiện tại KHỚP 18 bước BT §19 ở mọi điểm spec
nói rõ.** Ba điểm spec để ngỏ (Day 28 Month-End ở bước 9; "funding state" quyết ở 14c
thay vì 15; thứ tự nội bộ 14a/14b/14c) không thể phán xét dứt khoát và không phải sai lệch
do WP-A6 tạo ra.

## A.3 Phân tích tác dụng phụ thật của từng nhóm dời chỗ (reviewer tự suy từ code)

Reviewer nhận diện BỐN nhóm thay đổi trong diff (không phải ba như S001 liệt kê):

1. **Fill/ledger/cooldown 12 → 16–17, thêm sort ở 15.** Reviewer kiểm `capital.py`:
   `deploy_from_reserved` chỉ chuyển R→D, KHÔNG đổi `available`; `smart_reservable` dùng
   `month_reserved + month_deployed` (tổng bất biến khi deploy); `opportunity_reservable`
   dùng `reserved + deployed` (tổng bất biến). `cooldown_until`/`last_exec_price` được đọc
   ở bước 11 trước cả hai vị trí. `apply_fill` dùng cùng `o` cho mọi fill trong nến. ⇒
   **Về kết quả (ETH, vốn) nhóm này là NO-OP; chỉ đổi thứ tự bản ghi purchase trong
   nến.** Quan sát S001 "fill xảy ra trước khi vốn khả dụng được đọc để tạo ladder" đúng
   về vị trí nhưng KHÔNG có hệ quả vốn — reviewer ghi nhận để không ai hiểu nhầm đây là
   nguồn ΔETH.
2. **Tạo ladder (Smart/Opp/Crash) sau bước 13.** Hệ quả: zone S0/C0 (= anchor = OPEN)
   không còn TRIGGERED ngay nến tạo; sớm nhất là nến kế tiếp, và chỉ khi `low` nến đó ≤
   anchor. ⇒ **có tác động thật lên ETH** (trễ 1 nến; đôi khi mất trigger nếu giá đi lên).
3. **Hysteresis Opportunity 8/9 → 18b.** Hệ quả: tại nến score tụt ≤ 62, Opp zone vẫn
   ACTIVE khi qua bước 13 → có thể confirm (CLOSE ≤ zone) → 14c tạo action; 18b sau đó
   chỉ suspend zone còn ACTIVE, nên zone TRIGGERED/ACTION_PENDING **thoát suspension và
   thực thi dù hysteresis đã SUSPENDED**. Đúng chữ §19 (13 trước 18) nhưng là thay đổi
   hành vi có thật so với baseline. Reviewer lưu ý thêm: việc 18b không đụng zone
   TRIGGERED là hành vi có từ trước (baseline cũng chỉ suspend `status == "ACTIVE"`) —
   WP-A6 mở rộng cửa sổ chứ không tạo ra lỗ hổng.
4. **Crash ladder 10 → 14a; Crash suspend/cancel 10 → 18c.** Hệ quả (a): C0 trễ 1 nến
   như nhóm 2. Hệ quả (b): ở nến RECOVERY→NORMAL, crash zone bị xuyên ở 13 → 14c
   ACTION_PENDING → 18c `cancel_open_zones` (hàm này huỷ cả TRIGGERED/ACTION_PENDING) →
   CANCELLED cùng nến. ETH không đổi so với baseline (baseline huỷ trước khi trigger),
   nhưng `counters["triggered_actions"]` tăng thêm và trạng thái zone đi qua
   TRIGGERED→ACTION_PENDING→CANCELLED — mâu thuẫn với chữ ST §18.3 "nếu **vẫn chưa hit**
   thì CANCEL" (zone đó ĐÃ hit ở chính nến ấy, và theo §19 trigger (13) đi trước expiry
   (18)). Xem Finding R-02.

Ngoài ra `18a` thêm guard `lad.created_at < ts`: reviewer kiểm — baseline chạy bullish
check ở bước 8 TRƯỚC khi tạo ladder nên ladder tạo trong nến cũng không bị đếm; guard
giữ nguyên ngữ nghĩa "hai daily close hoàn chỉnh SAU khi tạo" (ST §18.2). Không đổi hành vi.

## A.4 Đánh giá độc lập chất lượng test thứ tự

`tests/wp_a6_order_harness.py`:
- Quan sát **side-effect thật**: subclass `Pool` (contribute/reserve/release/deploy_*),
  `SmartUnlockState.month_reset`, `OpportunityHysteresis.update`, `RegimeTracker.update`,
  `apply_fill`, `update_bullish_invalidation`, `Zone.__setattr__`/`Ladder.__setattr__`
  (mọi chuyển trạng thái), wrapper `create_*_ladder`. Đồng hồ nến = lần đọc `c["ts"][i]`
  qua proxy `_TsClock` — gắn đúng sự kiện vào nến kể cả sự kiện trước regime/score.
  **Không** phải mock hời hợt, không kiểm "tồn tại hàm".
- `letter_map` ánh xạ sự kiện → bước §19 **theo chữ spec** (reviewer đối chiếu từng dòng
  với bảng A.1: CONTRIBUTE→5/6, HWM_RESET→4, RESERVE/LADDER_CREATED→14, TRIGGERED→13,
  ACTION_PENDING→14, MISSED→12, FILL/DEPLOY_RESERVED→16-17 gộp, SUSPENDED/BULLISH→18,
  CRASH_ENTRY release→10 theo ST §14, RECOVERY_END→18 theo ST §18.3, LADDER_EXPIRED
  Smart→3 tại rollover / 9 tại Day 28, Opp→18). Reviewer đồng ý với mọi ánh xạ; điểm duy
  nhất có thể tranh luận là "Smart LADDER_EXPIRED tại Day 28 → bước 9" (hệ quả CONV #7,
  không thuộc WP-A6).
- `order_violations`: bước GIẢM giữa hai sự kiện liền kề trong cùng nến ⇒ phép kiểm
  "không giảm" đúng bản chất "thứ tự".

`tests/test_wp_a6_processing_order.py`:
- Mỗi kịch bản **tự khẳng định tiền đề** (có FILL + có TRIGGERED mới cùng nến; có
  SUSPENDED + close 92 < O1; có 3 chuyển regime đúng thứ tự; …) trước khi kiểm thứ tự —
  chặn "pass rỗng".
- `test_a6_05_order_test_detects_deliberate_reordering`: nạp `engine.py` từ mã nguồn, dời
  khối theo marker (tái tạo F-018a/F-018b + một đảo mới), khẳng định test ĐỎ với đúng chữ
  ký và engine thật SẠCH trên cùng kịch bản. `move_block` đòi marker duy nhất → nếu ai
  đổi nhãn khối, test đỏ thay vì im lặng. Đây là bằng chứng mạnh rằng test không "khớp
  hành vi hiện có".
- Long-run 2 năm synth với GATE1 + GATE3, no-lookahead 3 phép (score hiệu lực theo
  `day_end`; đầu độc daily tương lai; cắt/đầu độc 15m tương lai) so tiền tố bit-for-bit,
  có đối chứng "sau mốc phải khác".

**Nhận xét của reviewer:** test kiểm THỨ TỰ THẬT, viết từ spec; không phải bẫy "test khớp
code" mà task file Notes cảnh báo. Điểm yếu nhỏ: SC5/SC6 chỉ khẳng định tiền đề + không vi
phạm, KHÔNG khẳng định tường minh hệ quả nghiệp vụ mới (Opp zone fill khi hysteresis
SUSPENDED; crash zone hit rồi bị huỷ cùng nến) — reviewer phải tự probe để thấy (A.5).

## A.5 Kết quả chạy thật của reviewer

### A.5.1 Test thứ tự trên engine BASELINE `b717634` (probe `rev_probe.py`)

Reviewer nạp engine baseline bằng `load_engine_from_source(git show b717634:…engine.py)`
và chạy ba kịch bản của test; engine hiện tại chạy song song để đối chứng:

```
BASELINE SC1 fill+trigger : 4 vi phạm  {RESERVE[SMART_ZONE_S2]@14 => TRIGGERED@13: 1,
                                        FILL@16 => TRIGGERED@13: 1,
                                        BULLISH_CHECK@18 => HYST_UPDATE@8: 2}
CURRENT  SC1 fill+trigger : 0 vi phạm
BASELINE SC2b crash-entry : 10 vi phạm {RESERVE[SMART_ZONE_S2]@14 => TRIGGERED@13: 1,
                                        BULLISH_CHECK@18 => HYST_UPDATE@8: 8,
                                        RESERVE[CRASH_ZONE]@14 => TRIGGERED@13: 1}
CURRENT  SC2b crash-entry : 0 vi phạm
BASELINE SC5 hysteresis   : 6 vi phạm  {RESERVE[OPPORTUNITY_O4]@14 => TRIGGERED@13: 1,
                                        BULLISH_CHECK@18 => HYST_UPDATE@8: 4,
                                        ZONE[ACTIVE->SUSPENDED]@18 => REGIME_UPDATE@10: 1}
CURRENT  SC5 hysteresis   : 0 vi phạm
```

⇒ Test viết từ spec **thật sự đỏ trên code cũ** với đúng chữ ký F-018 (14→13, 16→13) VÀ
lộ thêm hai sai lệch S001 không nêu (bullish invalidation ở bước 8; hysteresis suspend
trước bước 10). Engine hiện tại sạch. Đây là bằng chứng E1 độc lập cho CHECK-A6-02.

### A.5.2 Probe hệ quả nghiệp vụ của hai điểm A.3 (3) và (4)

SC5, nến 07:00 Day 3 (score 70 → 60, close 92 < O1 = 92.5):
```
BASELINE: HYST_UPDATE(active=False) → 5 zone Opp ACTIVE->SUSPENDED → (Smart S1 TRIGGERED)
          OPPORTUNITY purchases: []
CURRENT : HYST_UPDATE(active=False) → Smart S1 TRIGGERED → Opp O1 ACTIVE->TRIGGERED
          → 4 zone Opp còn lại ACTIVE->SUSPENDED (O1 giữ TRIGGERED, KHÔNG bị suspend)
          OPPORTUNITY purchases: [('2023-03-03 08:15', 'OPPORTUNITY_ZONE_1', 0.3)]
```
⇒ xác nhận A.3 (3): Opp zone confirm ở nến score tụt được thực thi lúc hysteresis đang
SUSPENDED (action tạo sau khi cooldown Smart hết, fill 08:15).

SC6, nến RECOVERY→NORMAL 2023-03-11 07:00 (low 55):
```
BASELINE: RELEASE RECOVERY_END ×2 → C2,C3 SUSPENDED->CANCELLED → CRASH ladder CANCELLED
          → Smart S2 TRIGGERED → ACTION_PENDING     counters.triggered_actions = 5
CURRENT : Smart S2 TRIGGERED, C2 SUSPENDED->TRIGGERED, C3 SUSPENDED->TRIGGERED
          → S2 ACTION_PENDING, C2 ACTION_PENDING (max_zones=2 chặn C3)
          → RELEASE RECOVERY_END ×2 → C2 ACTION_PENDING->CANCELLED, C3 TRIGGERED->CANCELLED
          → CRASH ladder CANCELLED                  counters.triggered_actions = 6
CRASH purchases: baseline C0 07:30 Day 5 / hiện tại C0 07:45 Day 5 (trễ đúng 1 nến), C1 như nhau
```
⇒ xác nhận A.3 (4)(b) và (a). ETH không đổi ở kịch bản này; bộ đếm `triggered_actions`
bị thổi lên 1 bởi một action bị huỷ trong cùng nến.

### A.5.3 Toàn bộ test suite (reviewer tự chạy)

Lệnh: `python -m pytest tests/ -q -p no:cacheprovider --durations=15`
(pyproject: `testpaths = ["tests"]`, `addopts = "-q"`). Lần chạy foreground đầu bị
`timeout 580` cắt (suite dài hơn ~10 phút vì các fixture synth) — reviewer chạy lại nền,
log tại `scratchpad/pytest_full.log`.

KẾT QUẢ (reviewer, HEAD ổn định `a2fa9a5`, không có commit nào xen giữa):
**308 test chạy · 308 PASS · 0 FAIL · 0 ERROR · 0 skip/xfail · exit code 0 · 11m51s**
(pyproject `addopts=-q` cộng `-q` của reviewer thành `-qq` nên log chỉ có dấu chấm; reviewer
đếm: 308 `.` / 0 `F` / 0 `E`, khớp 308 test `--collect-only` = 286 cũ + 22 A6; `EXIT=0`).
Chậm nhất: `test_e2e.py::test_full_pipeline_smoke` 181,96s;
`test_wp_a1_provenance.py::test_a1_09_reproducibility_same_seed_same_metrics` 64,72s — PASS
(không tái hiện failure "code_commit đổi giữa chừng" mà implementer gặp, đúng như họ giải
thích là artefact HEAD đổi trong lúc chạy).

### A.5.4 Tác động đo trên dataset synth (reviewer tự chạy `tests/wp_a6_impact_tool.py`)

Cửa sổ mặc định 2019-01-01 → 2026-06-01, `SYNTH_SEED` mặc định, cùng raw dir cho mọi
biến thể. `base` = cây `src/` tại `b717634`; `cur` = tại `a2fa9a5`; `var_ladder13` = `cur`
nhưng khối 14b (tạo Smart/Opp ladder) được `move_block` dán lại TRƯỚC bước 13 (cô lập
riêng tác động của "ladder tạo sau 13").

| Biến thể | exec | eth_total | purchases | Smart n/eth | Opp n/eth | Crash n/eth | triggered | letter_violations | same_candle_trigger_after_create |
|---|---|---|---|---|---|---|---|---|---|
| base | gate1 | 21.637034605 | 543 | 236 / 10.250003 | 17 / 0.015042 | 23 / 0.280498 | 193 | 1151 | 88 |
| cur | gate1 | 21.648658720 | 541 | 235 / 10.260456 | 16 / 0.015358 | 23 / 0.281353 | 191 | 0 | 0 |
| var_ladder13 | gate1 | 21.638762867 | 544 | 236 / 10.248913 | 19 / 0.018642 | 22 / 0.279716 | 194 | 72 | 72 |
| base | gate3 | 21.622354120 | 543 | 236 / 10.244129 | 17 / 0.014931 | 23 / 0.277345 | 193 | 1156 | 88 |
| cur | gate3 | 21.636121266 | 541 | 235 / 10.256918 | 16 / 0.015270 | 23 / 0.277984 | 191 | 0 | 0 |

- ΔETH (cur − base) gate1 = **+0.011624 ETH (+0.054 %)**; gate3 = **+0.013767 ETH (+0.064 %)**.
  Base ETH không đổi (267 lần, 11.091492) — đúng kỳ vọng vì bước 9 không bị đụng.
- Tác động RIÊNG của "ladder tạo sau 13" (cur − var_ladder13, gate1) = **+0.009896 ETH
  (+0.046 %)** — chiếm ~85 % ΔETH tổng; phần còn lại (~+0.0017) đến từ hysteresis 18b +
  Crash 14a/18c. Chiều là **tăng** ETH — tức thứ tự đúng spec KHÔNG "bảo thủ" hơn thứ tự
  cũ; reviewer ghi nhận để orchestrator không mặc định "sửa = an toàn hơn".
- Chữ ký vi phạm của baseline trên 7 năm synth: 67× RESERVE Smart@14→TRIGGERED@13,
  17× RESERVE Crash@14→TRIGGERED@13, 4× RESERVE Opp@14→TRIGGERED@13, 1× FILL@16→TRIGGERED@13,
  1019× BULLISH_CHECK@18→HYST@8, 12× SUSPENDED@18→REGIME@10, 5× SUSPENDED→ACTIVE@18→REGIME@10,
  và 26× CANCELLED@18→HYST@8/REGIME@10. `invalid_candles_share = 0` trên synth mặc định
  nên H-15 không đo được ở đây (xem A.5.5).
- Mọi con số trên là của reviewer; không dùng số implementer báo cáo.

### A.5.5 H-15 trên synth có gap daily (`--drop-daily 2022-05-15`)

Reviewer chọn ngày xoá KHÁC implementer (chưa biết họ chọn ngày nào ở thời điểm chạy):

| Biến thể | drop_daily | invalid_share | eth_total | purchases | invalid_cycle_triggers | actioned |
|---|---|---|---|---|---|---|
| base | 2022-05-15 | 1,14 % | 21,626469199 | 525 | 0 | 0 |
| cur | 2022-05-15 | 1,14 % | 21,632933988 | 524 | 0 | 0 |

⇒ Trên synth, cửa sổ INVALID 31 ngày (do `adr30`) không có zone nào bị xuyên trong lúc
INVALID → không đo được cái giá của H-15 bằng dataset này; bằng chứng hành vi duy nhất là
kịch bản `test_h15_trigger_in_invalid_cycle_persists_until_first_valid_cycle` (reviewer đã đọc:
trigger S1/S2 trong INVALID → action ở nến GOOD đầu tiên → fill ở giá 100 dù target 94,6/89,2).
(Tái lập đúng ngày của implementer: xem B.3 mục 5.)

## A.6 Đánh giá độc lập H-15 (trước khi đọc CONVENTIONS #19)

Câu hỏi H-15: zone TRIGGERED trong chu kỳ INVALID có được sống sót và thành action khi dữ
liệu tốt trở lại không?

Căn cứ reviewer tự đọc:
- ST §3 INVALID: "Chặn mọi action Smart và Opportunity **mới**". Câu chữ chặn ACTION,
  không nói gì về TRIGGER (phát hiện giá xuyên zone). Bước 13 §19 đọc LOW/CLOSE 15m —
  dữ liệu execution, không phải daily score — nên việc đánh dấu TRIGGERED trong INVALID
  không vi phạm §3 và không dùng dữ liệu xấu.
- ST §15.1 và CONVENTIONS #6 đã có sẵn cơ chế "giữ TRIGGERED, xét lại cycle sau" cho
  max_zones và cooldown — với cùng hệ quả kinh tế (action tạo ở giá của cycle sau, có
  thể cao hơn target). Áp cùng cơ chế cho INVALID là **nhất quán** với lifecycle hiện có,
  không cần trạng thái mới, không cần sửa `ladders.py`/`score.py` (ngoài touch area).
- `score.py`: INVALID theo `invalid_mask` trên `close/return7/adr30`; ngày INVALID có
  `oscore = NaN` → engine đặt `s_unl = o_unl = 0`, 14b không tạo ladder, 14c không tạo
  action. Cổng ST §3 vẫn đóng đúng ở "action mới". Reviewer không thấy đường nào để zone
  TRIGGERED trong INVALID **fill** trong INVALID.
- Phương án thay thế (hoàn TRIGGERED → ACTIVE, đòi hit lại) sẽ là quy tắc MỚI không có
  trong V2.1.5 — Master Index §6 cấm vá spec; đúng chỗ là WP-D2.
- Giá của quy ước "giữ nguyên": mua ở giá cycle hợp lệ (có thể > target). Chiều này
  KHÔNG làm đẹp kết quả backtest (mua đắt hơn target) — chấp nhận được về mặt bảo thủ.

**Kết luận A.6 của reviewer: "GIỮ NGUYÊN" là quyết định có căn cứ vững**, với điều kiện
(i) được ghi thành quy ước tường minh, (ii) có test khoá hành vi, (iii) chuyển câu hỏi
"có nên re-arm zone" cho WP-D2. Reviewer sẽ đối chiếu ba điều kiện này ở Phần B.

## A.7 Verdict độc lập từng CHECK (trước khi đọc Evidence implementer)

| Check | Câu hỏi | Verdict reviewer | Căn cứ (của reviewer) |
|---|---|---|---|
| CHECK-A6-01 | Tồn tại unit test kiểm thứ tự 18 bước và chạy được | PASS | A.4 + A.5.1/A.5.3 |
| CHECK-A6-02 | Sai lệch hiện tại xác định chính xác ở E1 | PASS | A.5.1: baseline đỏ đúng chữ ký F-018 + 2 sai lệch thêm; A.5.4: 1151/1156 vi phạm trên 7 năm |
| CHECK-A6-03 | Tác động đo bằng chạy thật | PASS (tái lập độc lập) | A.5.4 ΔETH +0.054 %/+0.064 %; cô lập nhóm 2 = +0.046 % |
| CHECK-A6-04 | Quyết định sửa-hay-ghi-nhận có căn cứ | Chờ đối chiếu Phần B | Reviewer độc lập kết luận: sửa cả 4 nhóm là đúng chữ §19; giữ nguyên H-15 có căn cứ (A.6) |
| CHECK-A6-05 | Test thứ tự PASS và khoá hành vi cuối | PASS | `test_a6_05_*` đảo có chủ đích → đỏ đúng chữ ký; engine thật sạch (A.5.1) |
| CHECK-A6-06 | Không lookahead tầng 15m | PASS | 3 test no-lookahead có đối chứng; `ndi` dùng `day_end = day_ts + DAY` (score D chỉ hiệu lực từ D+1 00:00 UTC); `r24` chỉ dùng 96 nến TRƯỚC |
| CHECK-A6-07 | Toàn suite PASS; thay đổi kết quả định lượng + giải thích | Chờ A.5.3 + Phần B | |
| CHECK-A6-08 | Rà soát độc lập E2 | Xem Kết luận | |

---

# PHẦN B — Đối chiếu với kết luận của implementer (đọc SAU khi Phần A đã viết)

## B.1 Nguồn đối chiếu

`docs/CONVENTIONS.md` #18 (a–f), #19, mục "Ghi chú cho WP-D2 từ WP-A6" (D2-A6-1…4);
Evidence/Status CHECK-A6-01..07 trong task file; `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md`
§0–§14.

## B.2 Điểm KHỚP giữa kết luận reviewer (Phần A) và implementer

| Chủ đề | Implementer | Reviewer (Phần A) | Kết quả |
|---|---|---|---|
| Thứ tự cuối khớp chữ §19 | CONV #18 "thi hành đúng 18 bước theo CHỮ" | A.2: KHỚP ở mọi điểm spec nói rõ | KHỚP |
| Nhóm 16/17 nguyên tử; cooldown fill nến N hiệu lực từ bước 11 nến N+1 | #18(a) | A.2 dòng 11/16–17, A.3(1) | KHỚP |
| Bước 15 chỉ sắp thứ tự ghi sổ, không đổi lượng vốn | #18(b) | A.3(1): `deploy_from_reserved` không đổi `available`/tổng month_* → no-op về vốn | KHỚP (reviewer suy từ `capital.py`, implementer đo V_D1 trùng bit — hai đường độc lập cùng kết luận) |
| Tạo ladder = "tạo reservation" bước 14, sau 13; Crash: cancel/release/snapshot ở 10, tạo ở 14a | #18(c) | A.2 dòng 10/14, A.3(2)(4a) | KHỚP |
| F-018 (3) "fill trước khi đọc vốn" đúng vị trí, sai hệ quả | CHECK-A6-02 "XÁC NHẬN về thứ tự, BÁC BỎ về hệ quả" | A.3(1) cùng kết luận | KHỚP |
| Bullish invalidation 18a với guard `created_at < ts` không đổi ngữ nghĩa | #18(e) | A.3 đoạn cuối | KHỚP |
| Zone ACTION_PENDING cùng nến không bị suspend nhưng bị cancel bởi invalidation/recovery-end | #18(e) câu cuối | A.3(4b), A.5.2 SC6 | KHỚP về mô tả cơ chế (xem R-02 về ngữ nghĩa) |
| Month-End Day 25/28 trong khe bước 9 là điểm spec để ngỏ → WP-D2 | #18(f), D2-A6-1 | A.2 dòng 9 | KHỚP |
| ΔETH synth 7,5 năm | +0,0537 % gate1 / +0,0637 % gate3; 543 → 541; 88/88; 1151/1156 vi phạm; phân kỳ đầu 2019-01-04 07:30 → 07:45 | A.5.4: 21,637034605 → 21,648658720 (+0,054 %); 21,622354120 → 21,636121266 (+0,064 %); 543 → 541; 88; 1151/1156 | KHỚP tới 9 chữ số — reviewer tái lập độc lập từ `git archive` + `--src` |
| H-15 giữ nguyên, căn cứ ST §3 + cơ chế giữ-TRIGGERED §15.1/#6, cái giá ghi rõ, chuyển WP-D2 | #19, D2-A6-3, `test_h15_*` | A.6: cùng kết luận và cùng ba điều kiện (quy ước tường minh ✓, test khoá ✓, WP-D2 ✓) | KHỚP |
| Test kiểm thứ tự thật, không phải mock; viết từ spec; đỏ trước khi sửa | CHECK-A6-01/02/05 | A.4, A.5.1 (baseline đỏ đúng chữ ký F-018 + 2 sai lệch thêm) | KHỚP |
| Không lookahead tầng 15m | CHECK-A6-06 | A.7 | KHỚP |
| BEFORE 11 FAIL / 7 PASS trên 18 test | S014 §3 | Reviewer không chạy lại nguyên bộ 18 test cũ (bộ hiện tại đã 22 test, có test H-15/A6-05 phụ thuộc marker mới); thay vào đó tái lập 3 kịch bản cốt lõi trên engine baseline → đỏ đúng chữ ký (A.5.1) | KHỚP về bản chất; con số 11/7 không tái lập nguyên văn |

## B.3 Điểm reviewer thấy KHÁC hoặc implementer chưa nói tới

1. **CONV #18(e) / CHECK-A6-03 "V_D18 — mục 18 về cuối: 0 (trùng bit), 543/543 trùng khớp"
   và CHECK-A6-04 "D1 và D18 không đổi kết quả" → chỉ đúng trên dataset synth, KHÔNG đúng
   tổng quát.** Probe SC5 của reviewer (A.5.2) cho thấy dời hysteresis xuống 18b làm Opp
   zone O1 confirm ở đúng nến score tụt ≤ 62, giữ TRIGGERED (không bị 18b suspend, vì 18b
   chỉ suspend ACTIVE và zone đang bị cooldown giữ TRIGGERED), rồi **fill lúc hysteresis
   đang SUSPENDED** — baseline không có purchase Opp nào ở kịch bản này. Implementer đo
   "trùng bit" vì synth 7,5 năm không có nến nào chạm đúng ca (score rơi ≤ 62 cùng nến với
   CLOSE ≤ zone Opp chưa trigger). Biến thể cô lập của reviewer (A.5.6): dời riêng 18b về vị trí cũ trên engine hiện tại
   → **trùng bit** với engine hiện tại trên synth 7,5 năm (541/541 purchase, ETH
   21,648658719933611) — tức số đo của implementer ĐÚNG, nhưng là số đo "không xảy ra trên
   dataset này", không phải "không thể xảy ra".
   ⇒ Kết luận "vô hại" cho D18 là kết luận **theo dataset**, đúng với yêu cầu chữ của
   CHECK-A6-03 ("dựa trên số đo"), nhưng CONV #18(e) và CHECK-A6-04 nên nói rõ "trên
   dataset synth" thay vì để người đọc hiểu là bất biến. Không làm đổi verdict (thứ tự
   mới ĐÚNG chữ §19: 13 trước 18), nhưng là mismatch về cách trình bày. Xem Finding R-01.
2. **Zone TRIGGERED bị giữ (cooldown / max_zones / INVALID) thoát hysteresis suspension**
   — CONV #18(e) chỉ ghi "zone đã thành ACTION_PENDING … không bị suspension"; trường hợp
   zone còn ở TRIGGERED (giữ theo #6/§15.1/#19) cũng không bị 18b suspend (18b chỉ xét
   ACTIVE) và có thể thành action nhiều nến sau khi hysteresis đã SUSPENDED. Cơ chế này có
   từ baseline (khối hysteresis cũ cũng chỉ xét ACTIVE) nên KHÔNG phải WP-A6 tạo ra, nhưng
   WP-A6 mở rộng cửa sổ (thêm ca confirm cùng nến) và tài liệu chưa nêu. Xem R-01.
3. **ST §18.3 "Sau 72h Recovery nếu vẫn chưa hit thì CANCEL" vs. `cancel_open_zones`
   huỷ cả TRIGGERED/ACTION_PENDING ở 18c.** Với thứ tự mới, crash zone bị xuyên ở chính
   nến RECOVERY→NORMAL đã "hit" (bước 13) rồi vẫn bị huỷ (bước 18c) — probe SC6 (A.5.2).
   ETH không đổi so với baseline (baseline huỷ trước khi trigger), nhưng (i) mâu thuẫn chữ
   "chưa hit"; (ii) `counters["triggered_actions"]` đếm một action bị huỷ cùng nến
   (6 vs 5 ở SC6) — BT §16 dùng bộ đếm này cho báo cáo. Implementer ghi cơ chế ở #18(e)
   ("vẫn bị cancel bởi … recovery-end") như thiết kế, không nêu tension với §18.3 và
   không ghi WP-D2. Xem R-02. Cùng mẫu áp cho expiry Opp 90 ngày (18d) và bullish
   invalidation (18a) — với bullish, ST §18.2 nói "zone còn lại chuyển CANCELLED" nên huỷ
   zone đã trigger là chấp nhận được; với §18.3 chữ "chưa hit" thì không rõ.
4. **Tiêu chí "đáng kể" (|ΔETH| < 0,1 %, nominal Base/Smart/Crash không đổi, phân kỳ đầu
   giải thích được) do chính phiên S014 tự đặt**, không phải từ Owner/spec. Implementer
   minh bạch điều này (S014 §4, CHECK-A6-04 "số đo được trình để orchestrator/chủ dự án
   xác nhận trước khi commit") và orchestrator đã commit checkpoint `1af38f3` — reviewer
   coi là đã được xác nhận ngầm, nhưng ghi lại để Owner biết ngưỡng này chưa có trong
   governance/spec. Reviewer bổ sung một sự thật đo được: chiều ΔETH là **tăng** (thứ tự
   đúng spec mua S0 trễ một nến, hoá ra mua rẻ hơn trên synth) — không phải "bảo thủ hơn".
5. **H-15 trên synth có gap:** implementer dùng `--drop-daily 2020-06-15` → 0 trigger
   trong INVALID. Reviewer dùng thêm `2022-05-15` (A.5.5) và tái lập đúng ngày của họ
   (`--drop-daily 2020-06-15`, engine hiện tại, gate1: **ETH 21,634883289142703 · 528
   purchase · 0 trigger trong INVALID · 0 vi phạm** — trùng từng chữ số với #19/S014 §4). Cả hai đều 0 ⇒ căn cứ đo cho #19 là "không xảy ra trên synth", tức chưa đo
   được cái giá thật; cái giá chỉ thấy ở mức kịch bản (`test_h15_*`, fill ở 100 dù target
   94,6/89,2). Implementer có nói rõ điều này ở #19 và D2-A6-3 — KHỚP, reviewer chỉ nhấn
   mạnh rằng vế RE_TRIGGER thứ ba của H-15 (official run có action trên trigger INVALID
   đáng kể) vẫn phải được orchestrator giữ mở cho tới khi official run chạy.
6. **CHECK-A6-07:** implementer báo `1 failed, 307 passed` rồi chạy lại riêng
   `test_a1_09` → 308/308, nguyên nhân HEAD đổi giữa chừng do commit checkpoint. Reviewer
   chạy trên HEAD ổn định `a2fa9a5`: **308/308 PASS, exit 0, 11m51s, không cần chạy lại test nào** (A.5.3). Tổng collected reviewer đếm
   độc lập = 308 (286 cũ + 22 A6) — khớp.
7. Không test cũ nào bị sửa: reviewer xác nhận qua `git diff --stat b717634..a2fa9a5`
   (trong `tests/` chỉ 3 file MỚI). KHỚP.

## B.4 Đánh giá quyết định "SỬA cả ba nhóm + GIỮ NGUYÊN H-15"

- **Sửa nhóm fill 12→16–17 + sort 15:** đúng chữ §19; reviewer chứng minh độc lập là
  no-op về vốn (A.3(1)) ⇒ rủi ro ≈ 0. ĐỒNG Ý.
- **Sửa tạo ladder sau 13 (Smart/Opp/Crash):** đúng chữ §19 (13 trước 14); tác động
  +0,05 % ETH được reviewer tái lập bit; chiều tăng; nominal Base/Smart/Crash không đổi;
  phân kỳ giải thích được bằng đúng bước. ĐỒNG Ý, kèm lưu ý D2-A6-2 (ngữ nghĩa S0) là
  câu hỏi thật cho V2.2 — hai cách đọc cho kết quả khác nhau và spec không chọn.
- **Gom bullish/hysteresis/recovery về 18:** đúng chữ §19; bullish + recovery về mặt
  ETH không đổi (reviewer suy luận + probe); hysteresis có cửa sổ hành vi mới (R-01)
  chưa xảy ra trên synth. ĐỒNG Ý về thứ tự; YÊU CẦU ghi bổ sung (R-01) — không chặn.
- **GIỮ NGUYÊN H-15:** ĐỒNG Ý (A.6): đúng chữ ST §3, nhất quán với cơ chế giữ-TRIGGERED
  có sẵn, không mở rộng touch area, có test khoá, có ghi WP-D2, chiều kinh tế không làm
  đẹp kết quả. Phương án "huỷ/re-arm" là quy tắc mới → thuộc WP-D2, không thuộc WP-A6.

## A.5.6 (bổ sung sau Phần B) Biến thể cô lập thêm của reviewer

Sau khi đọc Phần B, reviewer dựng thêm hai biến thể trên engine HIỆN TẠI (`move_block` theo
marker, cùng cơ chế `test_a6_05_*`) để kiểm riêng tuyên bố "D18 trùng bit":

| Biến thể (từ `cur`) | Khối dời | eth_total gate1 | purchases | trùng `cur`? | vi phạm chữ §19 |
|---|---|---|---|---|---|
| `var_hyst_early` | 18b hysteresis → trước bước 9 (vị trí cũ) | 21,648658719933611 | 541 | **trùng bit** (541/541 bản ghi) | 22 (`SUSPENDED/ACTIVE/CANCELLED@18 ⇒ REGIME_UPDATE@10`) |
| `var_crash18_early` | 18c Crash suspend/cancel → trước bước 11 (vị trí cũ) | 21,648658719933611 | 541 | **trùng bit** | 0 (synth không có nến chuyển RECOVERY/NORMAL trùng nến có trigger) |
| `var_ladder13` (A.5.4) | 14b tạo Smart/Opp ladder → trước bước 13 | 21,638762867 | 544 | KHÁC (−0,009896) | 72 |

Đọc cùng A.5.2: hai khối 18b/18c là **inert trên synth** nhưng **không inert ở mức kịch
bản** (SC5: Opp fill khi SUSPENDED; SC6: crash zone hit rồi huỷ). Tuyên bố "trùng bit" của
implementer đúng và tái lập được; phạm vi của nó ("trên dataset synth") cần được ghi rõ.

## Mismatches With Implementer Claims

- **M-01** — CONV #18(e), CHECK-A6-03 (V_D18), CHECK-A6-04: "dời mục 18 xuống cuối không đổi
  một bản ghi nào / trùng bit" được trình bày như tính chất chung; thực tế là kết quả **trên
  dataset synth** (reviewer tái lập trùng bit ở A.5.6) trong khi kịch bản SC5/SC6 (A.5.2) cho
  thấy hành vi khác baseline. Không đổi verdict thứ tự; là mismatch về phạm vi của tuyên bố.
- **M-02** — Implementer không nêu tension giữa 18c (`cancel_open_zones` huỷ zone đã
  TRIGGERED/ACTION_PENDING ở nến kết thúc Recovery) và chữ ST §18.3 "nếu **vẫn chưa hit**";
  và không nêu bộ đếm `triggered_actions` bị cộng cho action bị huỷ cùng nến. Không có mục
  WP-D2 cho điểm này.
- **M-03** — CONV #18(e) chỉ nói zone ACTION_PENDING thoát suspension; zone còn TRIGGERED (bị
  giữ bởi cooldown/max_zones/INVALID) cũng thoát 18b và có thể thành action khi hysteresis
  đang SUSPENDED (A.5.2 SC5: O1 giữ TRIGGERED qua cooldown rồi fill 08:15). Cơ chế có từ
  baseline, không do WP-A6 tạo, nhưng WP-A6 mở rộng cửa sổ và tài liệu chưa ghi.
- Ngoài ba điểm trên: **mọi con số** (ETH, purchase, vi phạm, 88/88, 308/308, H-15 528/
  21,634883289142703) và **mọi kết luận thứ tự** của implementer được reviewer tái lập độc lập
  và KHỚP. Con số "11 FAIL / 7 PASS" của lần chạy đầu không tái lập nguyên văn (bộ test đã
  thành 22) nhưng bản chất "đỏ trên baseline với đúng chữ ký F-018" được tái lập (A.5.1).

## Findings

Reviewer KHÔNG sửa code, KHÔNG tạo task, KHÔNG tự route — các finding dưới đây chuyển
orchestrator xử lý theo `governance/v4/CORE/REVIEW_PROTOCOL.md`. Không finding nào là vi
phạm thứ tự BT §19; không finding nào chặn CHECK-A6-08.

- **R-01 (NON-BLOCKING, ghi nhận/tài liệu — đề nghị mục WP-D2 mới + có thể là HARDENING
  item cho CAP lifecycle)** — *Zone Opportunity ở trạng thái TRIGGERED/ACTION_PENDING không
  chịu hysteresis suspension.* Với thứ tự §19 (13 trước 18), một Opp zone có thể confirm ở
  đúng nến score rơi ≤ 62 và thực thi khi hysteresis đang SUSPENDED; zone TRIGGERED bị giữ
  (cooldown/max_zones/INVALID) cũng thoát suspension nhiều nến. Bằng chứng: A.5.2 SC5 (engine
  hiện tại có purchase `OPPORTUNITY_ZONE_1` 0,3 lúc 08:15 Day 3; baseline không có). Tác động
  synth 7,5 năm: **0** (A.5.6 trùng bit). Spec: ST §5 chỉ nói "SUSPEND trạng thái Opportunity"
  và "Suspended zone giữ reserve tối đa 7 ngày", không nói zone đã trigger có bị suspend. Hành
  vi hiện tại đúng chữ §19; đề nghị: (a) bổ sung câu phạm vi vào CONV #18(e) ("zone TRIGGERED
  bị giữ cũng không bị suspend; đo trên synth: không xảy ra"); (b) mở D2-A6-5 cho V2.2 quyết
  định. Thuộc ngữ nghĩa lifecycle (`ladders.py`/khối 18b), ngoài Scope Lock WP-A6 nếu muốn
  đổi hành vi.
- **R-02 (NON-BLOCKING, spec ambiguity — đề nghị mục WP-D2)** — *Crash zone "hit" ở nến kết
  thúc Recovery vẫn bị huỷ bởi `cancel_open_zones` (18c), trái chữ "nếu vẫn chưa hit" ST
  §18.3; `counters["triggered_actions"]` đếm action bị huỷ cùng nến.* Bằng chứng: A.5.2 SC6
  (C2 TRIGGERED→ACTION_PENDING→CANCELLED cùng nến; triggered 6 vs 5). ETH không đổi so với
  baseline (baseline huỷ trước khi trigger nên zone không bao giờ "hit"); trên synth 7,5 năm
  ca này không xảy ra (A.5.6 `var_crash18_early` trùng bit, triggered = executed = 191). Cùng
  mẫu áp cho expiry Opp 90 ngày (18d). Đề nghị: ghi D2-A6-6 (V2.2 chọn: zone hit trong nến
  expiry được thực thi hay bị huỷ); nếu Owner muốn giữ "huỷ", nên đổi bộ đếm để không đếm
  action bị huỷ cùng nến (báo cáo BT §16). Ngoài Scope Lock WP-A6 (`cancel_open_zones` là
  lifecycle).
- **R-03 (INFO)** — Ngưỡng "đáng kể" |ΔETH| < 0,1 % là do phiên S014 tự đặt; chiều ΔETH của
  thứ tự đúng spec là **tăng** ETH trên synth (+0,054 %/+0,064 %), không phải bảo thủ hơn.
  Orchestrator/Owner nên xác nhận tường minh (đã commit checkpoint `1af38f3` — coi như
  chấp nhận ngầm) và cân nhắc đưa ngưỡng này vào governance nếu còn dùng lại.
- **R-04 (INFO, ngoài WP-A6)** — Trong CRASH, khối 14b vẫn có thể tạo Opportunity ladder
  MỚI ngay sau khi crash entry huỷ Opp ladder cũ (14b không đọc `regime.state`; vốn còn lại
  sau khi 14a reserve). Hành vi có từ baseline (khối tạo ladder cũ cũng sau bước 10), không do
  WP-A6; reviewer chỉ ghi để orchestrator quyết có cần HARDENING item (CAP regime/ladder).
  Reviewer chưa đo tác động (ngoài scope review này).
- **R-05 (INFO, đã được implementer ghi ở S014 §11)** — Các artefact ngoài touch area chưa
  cập nhật: `HARDENING_BACKLOG.md` H-15 (cần dòng RESOLVED tham chiếu CONV #19 + review này),
  `CAPABILITY_REGISTRY.md` `CAP-ORDER`, `REVIEW_BUDGET_LEDGER.md`, `LO_TRINH_DE_HIEU.md`
  (chạy `sync_easy_roadmap.py`). Orchestrator xử lý sau khi nhận E2 này.

## Independent Verification

| Check ID | Status | Evidence Level | Evidence (của reviewer) | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-A6-01 | PASS | E2 | Test tồn tại (22 test, `--collect-only` = 22); harness quan sát side-effect thật (A.4); tự chạy trong suite 308/308 (A.5.3); `test_a6_01_harness_observes_real_side_effects` khẳng định CLOCK = số nến, FILL = số purchase | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-02 | PASS | E2 | Reviewer tự chạy 3 kịch bản trên engine `b717634` (A.5.1): đỏ với đúng chữ ký F-018a/b + 2 sai lệch bổ sung; synth 7,5 năm baseline 1151/1156 vi phạm, 88 trigger cùng nến tạo (A.5.4); từng quan sát F-018 (1)(2)(3) được reviewer xác nhận/bác bỏ độc lập giống implementer (A.3) | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-03 | PASS | E2 | Reviewer tái lập ΔETH +0,054 % (gate1) / +0,064 % (gate3), 543 → 541, nominal Base không đổi, bằng `--src` trên cây `git archive` (A.5.4); cô lập riêng "ladder sau 13" (A.5.4) và 18b/18c (A.5.6); H-15 hai ngày drop đều 0 trigger, ngày 2020-06-15 trùng từng chữ số (B.3-5) | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-04 | PASS | E2 | Quyết định "SỬA cả 3 nhóm + GIỮ NGUYÊN H-15" được reviewer kết luận độc lập TRƯỚC khi đọc (A.2/A.3/A.6) và trùng với implementer (B.4); có CONV #18/#19, có D2-A6-1…4, không vá spec. Bổ sung: phạm vi tuyên bố "trùng bit" cần nói rõ là trên synth (M-01) — không hạ verdict | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-05 | PASS | E2 | 22/22 PASS trong suite reviewer; `test_a6_05_*` (3 đảo có chủ đích) đỏ đúng chữ ký và engine thật sạch — reviewer đọc cơ chế `move_block`/marker duy nhất (A.4); reviewer tự dựng thêm 3 biến thể đảo (A.5.4/A.5.6) và `order_violations` bắt được 72/22/0 đúng như kỳ vọng theo khối bị dời | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-06 | PASS | E2 | 3 test `test_a6_06_*` PASS trong suite reviewer; reviewer đọc code: score D hiệu lực qua `searchsorted(day_end = day_ts + DAY, ts, "right")` → chỉ sau D+1 00:00 UTC; `r24` dùng 96 nến TRƯỚC; không đường nào đọc nến i+1 (A.2, A.7) | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-07 | PASS | E2 | Reviewer chạy full suite trên HEAD `a2fa9a5`: **308 PASS / 0 FAIL, exit 0, 11m51s** (A.5.3) — không tái hiện failure môi trường của implementer; không test cũ nào bị sửa (`git diff --stat`: tests/ chỉ 3 file mới); thay đổi kết quả quy đúng về bước 13→14 (A.5.4: cô lập ladder = ~85 % ΔETH, phần còn lại từ Crash 14a; 18b/18c trùng bit) | E2-WP-A6-001 | 2026-09-03T04:20Z |
| CHECK-A6-08 | **PASS** | E2 | Review này: thứ tự hiện tại KHỚP 18 bước BT §19 ở mọi điểm spec nói rõ (A.2), kết luận sửa/ghi nhận có căn cứ và được reviewer đi tới độc lập (A.3/A.6 → B.4), số đo tái lập bit, suite 308/308 do reviewer chạy. Ba mismatch M-01…M-03 là về phạm vi tài liệu/ngữ nghĩa lifecycle, không phải vi phạm thứ tự; hai finding R-01/R-02 chuyển orchestrator (non-blocking) | E2-WP-A6-001 | 2026-09-03T04:20Z |

## Conclusion

**E2 PASS — CHECK-A6-08 = PASS.**

Căn cứ (của reviewer, không phải chép lại):
1. Thứ tự thực thi trong `run_engine()` @ `a2fa9a5` khớp 18 bước BT §19 tại mọi điểm spec
   nói rõ; ba điểm spec để ngỏ (Month-End Day 25/28; "funding state"; thứ tự nội bộ 14a/b/c)
   đã được ghi thành quy ước hoặc không thuộc WP-A6 (A.2).
2. Test thứ tự kiểm side-effect thật, viết từ spec, đỏ trên baseline với đúng chữ ký F-018
   và bắt được đảo thứ tự có chủ đích — reviewer tự tái lập cả hai chiều (A.5.1, A.5.6).
3. Suite đầy đủ 308/308 PASS do reviewer chạy trên HEAD ổn định (A.5.3).
4. Tác động +0,054 %/+0,064 % ETH tái lập bit; quy về đúng bước 13→14 (A.5.4).
5. Quyết định "SỬA cả ba nhóm + GIỮ NGUYÊN H-15": reviewer đi tới cùng kết luận trước khi
   đọc của implementer (A.3, A.6); có quy ước, có test khoá, có ghi WP-D2 (B.4).

Điều kiện kèm theo (không chặn PASS, orchestrator xử lý theo REVIEW_PROTOCOL): M-01…M-03 và
R-01/R-02 là câu hỏi ngữ nghĩa lifecycle/tài liệu, không phải sai lệch thứ tự; nếu Owner
muốn đổi hành vi thì thuộc WP-D2 (spec) hoặc CAP lifecycle, không mở lại WP-A6.

Hạn chế của review này (ghi thật): reviewer không chạy lại nguyên văn "11 FAIL / 7 PASS"
của lần chạy đầu (bộ test đã ở dạng 22 test); không đo tác động của R-04; cái giá của H-15
chỉ có ở mức kịch bản vì synth không tạo ra ca đó.

## Required Follow-up

Cho orchestrator (reviewer KHÔNG tự làm các việc dưới đây):
1. Điền CHECK-A6-08 = PASS / E2 trong task file WP-A6 với tham chiếu file này; chuyển
   WP-A6 VERIFYING → DONE theo Completion Gate; đóng F-018/F-019.
2. Route M-01 (phạm vi tuyên bố "trùng bit") → sửa câu chữ CONV #18(e) và Evidence
   CHECK-A6-03/04 (thêm "trên dataset synth"); đây là sửa tài liệu, không phải sửa code.
3. Route R-01, R-02 → mục WP-D2 (D2-A6-5, D2-A6-6) và/hoặc HARDENING_BACKLOG (CAP lifecycle);
   quyết định theo REVIEW_PROTOCOL — không thuộc Scope Lock WP-A6.
4. R-05: cập nhật H-15 trong `HARDENING_BACKLOG.md` (RESOLVED → CONV #19 + review này),
   `CAPABILITY_REGISTRY.md` `CAP-ORDER`, `REVIEW_BUDGET_LEDGER.md`, chạy
   `sync_easy_roadmap.py` + `validate_easy_roadmap.py`.
5. Giữ mở vế RE_TRIGGER thứ ba của H-15 (official run có action trên trigger INVALID đáng
   kể) — `wp_a6_impact_tool.py` đã đếm sẵn `invalid_cycle_triggers_actioned`.
6. Owner xác nhận tường minh ngưỡng "đáng kể" 0,1 % (R-03) nếu sẽ tái sử dụng.
