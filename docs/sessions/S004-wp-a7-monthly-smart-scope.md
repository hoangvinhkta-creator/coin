# SESSION HANDOFF — S004

Session ID:
S004

Task:
WP-A7 — Phạm vi kế toán vốn Smart theo accounting month (đóng F-035 / RSK-010)

Task Mode:
MAJOR

Project Profile:
PRODUCT

Status:
DONE — 12/12 REQUIRED check PASS (E1 toàn bộ; E2 cho CHECK-A7-12 với kết luận reviewer
độc lập **E2 PASS WITH FOLLOW-UPS** — follow-up không chặn DONE); mọi follow-up thuộc
thẩm quyền phiên đã thực hiện xong trước khi đóng (F-E2A7-02 → CONVENTIONS #17;
F-E2A7-03 → ghi vào PROGRESS mục PH-04).

Model/Effort thực thi:
Tier D (Fable) / max — đúng routing đã đóng băng trong file task WP-A7
(D3 R4 B3 A3 X3 → model_score 3.25 → D; U3 V4 H3 C3 F4 → effort_score 3.45 → max;
category `accounting_financial`; `validate_routing.py` PASS tại thời điểm freeze 68bd8be).

Môi trường:
Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1
(trùng bộ phiên bản S000/S003 — kết quả so sánh được với baseline trước đó).

Base commit khi mở phiên: `68bd8be` (task definition WP-A7 frozen, Status READY).

## Result

**WP-A7 = DONE.** Chuỗi đầy đủ: Ready Gate xác nhận lại (20/20) → baseline BEFORE tái
hiện F-035 đúng root cause đã triage → test-first A–G viết TRƯỚC fix (7 FAIL đúng kỳ
vọng + 1 PASS guard) → remediation PA-A trong `capital.py` + đúng MỘT hook trong
`engine.py` → 8/8 test WP-A7 PASS → regression WP-A3 + capital + engine 34/34 PASS →
toàn suite **95/95 PASS** (87 test trước + 8 test mới, 354s) → impact BEFORE/AFTER đo
trên cùng dataset tổng hợp cố định, mọi sai lệch truy vết về điều khoản spec → phát
hiện mới NGOÀI scope ghi nhận là PH-04 (không sửa) → reviewer độc lập kết luận
**E2 PASS WITH FOLLOW-UPS** → follow-up thuộc thẩm quyền phiên thực hiện ngay →
Completion Gate 12/12 PASS → F-035 RESOLVED, RSK-010 CLOSED.

## Ready Gate (xác nhận lại khi mở task — 2026-08-24)

Toàn bộ 20 mục Ready Gate trong file task xác nhận PASS tại đầu S004:
task definition frozen tại `68bd8be`; F-035/RSK-010/PH-03 triage đọc lại; DM §5/§6/§14,
ST §4/§6/§7/§10/§12, BT §1/§9/§19 đọc lại; Scope Lock nạp; routing xác nhận;
WP-A3 DONE không mở lại; branch không có push WP-A4 song song (kiểm `git fetch` — chỉ
`claude/wp-a3-regime-ladder-3wqw66` hoạt động).

## Baseline BEFORE (E1 — tái hiện TRƯỚC khi sửa, HEAD 68bd8be)

Nguồn: probe cấu trúc + probe 3-mode chạy tại 2026-08-24T03:45Z (log lưu phiên;
impact chính thức bằng tool đã commit `tests/wp_a3_impact_tool.py`, tag `WP_A7_BEFORE`,
BEFORE chạy qua git worktree tại 68bd8be với `--src` + assert provenance `code_path`).

**A — Chứng minh cấu trúc (số học thuần, dùng hàm thật `smart_reservable`):**
với budget_tháng=30, unlock=1.00, available=30 mỗi tháng:

| tháng | pool.deployed (lifetime) | smart_reservable |
|---|---|---|
| 1 | 0.0 | **30.000** |
| 2 | 30.0 | **0.000** |
| 3 | 60.0 | **0.000** |
| 4 | 90.0 | **0.000** |
| 5 | 120.0 | **0.000** |

Đúng root cause F-035: `monthly_smart_budget × unlock` là đại lượng THEO THÁNG nhưng
implementation trừ `pool.reserved + pool.deployed` trong đó `pool.deployed` là
**cumulative lifetime** → về 0 vĩnh viễn từ khi lifetime deployed ≥ ngân sách 1 tháng.

**B — Bảng theo tháng trên dataset tổng hợp (90 tháng, 2019-01→2026-06):**
chỉ **2** Smart ladder toàn kỳ (id=1 2019-01-04 eligible 0.6962 = 2.32% ngân sách tháng;
id=2 2019-02-21 eligible 1.3670 = 4.56%). Từ dep_life≈120 trở đi: mọi mẫu
`reservable=0.0000` bất kể unlock (0.199…0.975). Tổng 135 251 lần gọi
`smart_reservable`, **135 249 lần trả 0**.

**C — Kênh giải ngân Smart:** qua ladder 0.9106 / qua Month-End 4369.09
→ tỷ lệ ladder = **0.0208%** (cơ chế ST §12 chết trên thực tế).

**D — 3 mode smart_unlock (ST §6, BT §9 Gate-2 dimension):** HWM / NO_HWM / DECAY_HWM
cho `eth_total` **bằng nhau bit-for-bit** = 21.480751489892, purchases 392,
smart_via_ladder 0.9106 → dimension ablation mechanically dead.

**E — Impact BEFORE (tag `WP_A7_BEFORE`):** eth_total 21.480751489892178,
purchases 392, smart_ladders_created 2, crash_snapshots_sum 111.1302,
final SMART {available 50.0, reserved −0.0, deployed 4370.0, total 4420.0}.

## Test-first A–G (FAIL trước fix → PASS sau fix)

File test mới: `tests/test_wp_a7_monthly_scope.py` (8 test). Chạy tại HEAD 68bd8be
(TRƯỚC remediation): `FFFFF.FF` — **7 FAIL đúng kỳ vọng + 1 PASS**:

| Test | Nội dung | BEFORE | AFTER |
|---|---|---|---|
| test_a | (A) unit 3 tháng: quyền tháng 2/3 = đúng ngân sách tháng ở unlock 1.0; lifetime deployed bảo toàn 30/60 | FAIL (`Pool` chưa có `open_accounting_month`) | PASS |
| test_a2 | (A) engine 31+30 ngày → **2** ladder, mỗi cái eligible `30×(25/35)`=21.4286 | FAIL (1 ladder) | PASS |
| test_b | (B) 4 tháng liên tiếp → **4** ladder, không suy giảm | FAIL (1 ladder) | PASS |
| test_c | (C) sống/chết 3 mode — xem bảng dưới | FAIL | PASS |
| test_c2 | (D) month reset: peak tháng cũ không vắt sang tháng mới, cả 3 mode eligible `30×(10/35)` | FAIL | PASS |
| test_d | (E) guard hai chiều: Opportunity Fund cumulative + `opportunity_reservable` lifetime GIỮ NGUYÊN | **PASS** (guard, phải PASS cả hai phía) | PASS |
| test_e | (F) Month-End Day-28 OSCORE<45: mua 50%/chuyển 50% (OVERFLOW reason MONTH_END_SMART) + tháng sau vẫn tạo ladder 21.4286 | FAIL | PASS |
| test_f | (G) 3 tháng có crash vắt ranh giới tháng → carry; bảo toàn vốn ledger mọi pool; reconcile tất định bộ đếm tháng từ ledger | FAIL | PASS |

**Bằng chứng sống/chết mode (test_c, kịch bản tất định 2 tháng — ladder tháng 2 tạo ở
unlock 0.714, bullish invalidation → release, OSCORE tụt 40, 13 ngày decay):**

| Mode | eff_final | smart_reservable cuối (quyền còn lại của tháng) | month_deployed |
|---|---|---|---|
| HWM | 0.714286 (giữ peak 25/35) | **14.357143** | 7.071429 |
| DECAY_HWM | 0.614286 (tụt bậc 0.10/7 ngày) | **11.357143** | 7.071429 |
| NO_HWM | 0.142857 (bám 5/35) | **0.000000** | 7.071429 |

Ba mode cho ba đường unlock KHÁC NHAU và ba giá trị quyền vốn KHÁC NHAU đúng thứ tự
semantics ST §6 (HWM > DECAY_HWM > NO_HWM ≥ 0), trên engine run thật — dimension không
còn mechanically dead ở tầng path/quyền vốn. BEFORE: mọi mode đều 0 từ tháng 2.
(Giới hạn còn lại ở tầng OUTCOME toàn kỳ: xem PH-04 bên dưới.)

## Thiết kế PA-A (đã chốt tại triage PH-03; chi tiết CONVENTIONS #17)

- `Pool` giữ nguyên ledger audit lifetime append-only (DM §6) — KHÔNG xoá/reset lịch sử;
  thêm bộ đếm THEO THÁNG: `month_reserved`, `month_deployed`, `carry_reserved`,
  `month_opened_at`; API mới `open_accounting_month(ts)`.
- `smart_reservable` so `ngân_sách_tháng × effective_unlock` với
  `month_reserved + month_deployed` — cùng phạm vi tháng (DM §5 `monthly_budgets`),
  kẹp trên bởi `available`. Chữ ký hàm KHÔNG đổi → engine chỉ cần đúng MỘT hook.
- Hook engine tại rollover: `smart_pool.open_accounting_month(ts)` — SAU Month-End
  settle tháng cũ, TRƯỚC contribution tháng mới (đúng cụm bước 3→5 của BT §19),
  ngay trước `su.month_reset(ts)` (ST §6 peak reset).
- **Carry-first** cho reserve vắt tháng (nguồn duy nhất: crash zone giữ vốn SMART qua
  ranh giới — Smart ladder luôn hết hạn cuối tháng): reserve còn mở tại thời điểm mở sổ
  thành carry; release/deploy rút carry TRƯỚC; carry không ăn và không trả quyền tháng
  mới. Chiều sai duy nhất khi nhận diện lẫn lô là quyền KHÔNG được trả — bảo thủ theo
  BT §1; với deploy-from-reserved tổng quyền đã dùng không đổi → vô hại.
- `deploy_from_available` (Base/Month-End) tính vào `month_deployed` tháng đang mở.
- `opportunity_reservable` GIỮ NGUYÊN lifetime semantics (ST §7 — Opportunity Fund
  cumulative, test_d guard).
- "Vốn đã execute không relock" (ST §6) giữ nguyên TRONG phạm vi tháng —
  `tests/test_capital.py::test_smart_reservable_no_relock` pass KHÔNG sửa.

## AFTER proofs (cùng probe, cùng dataset)

- Bảng theo tháng: Smart ladder tạo được **67** (mẫu 2025-08→2026-06: mỗi tháng một
  ladder, eligible 1.35…50.0); `smart_reservable` gọi 88 lần, chỉ **6** lần trả 0
  (so với 135 249/135 251 BEFORE). Các eligible >100% ngân sách 30 là hợp lệ:
  `month_smart_budget` bao gồm cả cap-overflow từ Opportunity (+20), mẫu số hiển thị
  probe chia 30.
- Kênh giải ngân: qua ladder 1045.9713 / Month-End 3224.24 → tỷ lệ ladder **24.49%**
  (BEFORE 0.0208%) — cơ chế ST §12 sống lại.
- Month reset test_c2: ladder tháng mới eligible `30×(10/35)` cho cả 3 mode — peak
  tháng cũ không vắt sang (ST §6 "peak reset mỗi tháng").
- Month-End test_e: Day-28 12:00 OSCORE 40 <45 → mua 50%, chuyển 50% vào Opportunity
  (ledger OVERFLOW_OUT/OVERFLOW_IN, reason MONTH_END_SMART, trong cap); tháng sau vẫn
  tạo ladder đủ quyền 21.4286.
- Bảo toàn vốn test_f (3 tháng, crash vắt ranh giới): `ledger_conservation_ok` PASS
  mọi pool; tổng total == contributed; không orphan reserve; bộ đếm tháng
  **reconcile tất định** từ ledger + mốc mở sổ (replayer độc lập trong test khớp
  từng giá trị pool counters).

## Impact BEFORE → AFTER (cùng dataset tổng hợp cố định, tool đã commit)

Tag `WP_A7_BEFORE` (worktree 68bd8be, provenance assert) → `WP_A7_AFTER` (HEAD làm việc).
Mọi khác biệt truy vết về điều khoản spec — KHÔNG dùng "ETH AFTER > BEFORE" làm bằng chứng đúng:

| Chỉ số | BEFORE | AFTER | Truy vết nguyên nhân (spec) |
|---|---|---|---|
| smart_ladders_created | 2 | 67 | Trực tiếp F-035 fix: quyền tháng mới không bị lifetime deployed trừ (DM §5; ST §12 sống lại) |
| purchases SMART (n / nominal) | 92 / 4370.00 | 236 / 4270.21 | Dịch kênh Month-End → ladder 33/33/34 (ST §12); tổng Smart giải ngân vẫn trong ngân sách |
| crash_snapshots_sum | 111.13 | 492.07 | [F5] snapshot = Smart AVAILABLE + Opp AVAILABLE; Smart available giờ được reserve/luân chuyển qua ladder → thành phần Smart của snapshot sống lại (khuếch đại fix F-021 của WP-A3, không phải hành vi mới) |
| crash_ladders_created / CANCELLED | 10 / 10 | 17 / 17 | Nhiều capital-flow hơn qua pool Smart → nhiều crash entry đủ vốn snapshot ([F5], ST §14) |
| purchases CRASH (n / nominal) | 12 / 26.82 | 23 / 139.57 | Hệ quả snapshot trên |
| opp_ladders_created | 18 | 14 | [F5] claim Opportunity available cho crash zone → ít Opportunity ladder thường hơn (ST §14 ưu tiên crash) |
| purchases OPPORTUNITY (n / nominal) | 21 / 8.77 | 17 / 5.82 | Hệ quả trên |
| releases BULLISH_INVALIDATION / LADDER_EXPIRED / RECOVERY_END | 14.37 / 0.24 / 84.31 | 302.04 / 160.16 / 352.49 | Có 67 ladder sống thì mới có release theo vòng đời (ST §18.3, §15) — BEFORE gần như không có gì để release |
| cooldown_override (CRASH/NORMAL/STRESSED) | 5/1/0 | 12/7/16 | Nhiều execution hơn → nhiều LastExecutionPrice hơn → nhiều cơ hội override (CONVENTIONS #6); nhãn STRESSED chỉ là phân rã báo cáo [F1] |
| executed_actions / purchases_count | 36 / 392 | 193 / 543 | Hệ quả tổng của ladder sống lại |
| final SMART {avail, res, dep} | {50.0, −0.0, 4370.0} | {27.49, 15.08, 4377.43} | reserved 15.08 = ladder tháng cuối còn OPEN tại điểm cắt dữ liệu (hợp lệ, không phải leak — tháng chưa đóng) |
| final OPPORTUNITY {avail, dep} | {44.41, 35.59} | {41.82, 38.18} | Chênh 2.59 = crash fill từ nguồn Opportunity nhiều hơn; total giữ 80 (cap) |
| BASE (mọi chỉ số) | 267 / 4450.0 | 267 / 4450.0 | **Bất biến** — WP-A7 không đụng Base (guard) |
| state_transitions / label_transitions | (bảng) | **giống hệt** | **Bất biến** — regime layer WP-A3 không bị ảnh hưởng (non-regression) |
| daily_limit_blocks / missed / stuck_crash_reserve | 0 / 0 / 0 | 0 / 0 / 0 | Bất biến |
| eth_total | 21.480751 | 21.637035 (+0.73%) | Hệ quả, KHÔNG phải bằng chứng đúng đắn; cùng bậc với ước lượng triage (+0.79%) |
| avg_cash_ratio | 0.06826 | 0.06635 | Vốn Smart làm việc qua ladder thay vì nằm chờ Month-End |

## Phát hiện mới NGOÀI scope (ghi nhận, KHÔNG sửa — theo chỉ thị S004)

**PH-04 (đề xuất finding mới — chờ owner quyết):** Sau khi F-035 được sửa, ba mode
smart_unlock vẫn cho **kết quả cuối bit-for-bit giống nhau trên full synthetic run**
(eth 21.637034604792 cả 3 mode), dù đường unlock và quyền vốn ĐÃ phân kỳ (test_c).
Nguyên nhân cấu trúc: engine hiện chỉ TIÊU THỤ `effective_unlock` tại (a) thời điểm tạo
ladder one-shot ở lần eff>0 đầu tiên trong tháng — tại đó peak==current nên 3 mode trùng
(CONVENTIONS #1), và (b) crash snapshot — tại đó OSCORE≥75 ⇒ smart_unlock=1.0 mọi mode.
ST §6 yêu cầu 3 mode nằm trong Gate-2 ablation "báo cáo đóng góp riêng" (BT §9) — muốn
dimension này phân biệt được ở tầng OUTCOME cần một kênh tiêu thụ unlock LIÊN TỤC
(ví dụ: top-up/resize ladder trong tháng) — đó là thay đổi hành vi engine NGOÀI Scope
Lock WP-A7. Phương án xử lý thuộc owner: mở WP mới / đưa vào V2.2 / chấp nhận như
giới hạn đã biết của Gate-2 ablation. CHECK-A7-03 theo đúng câu chữ frozen ("unlock path
và quyền vốn phân kỳ, dimension không còn mechanically dead") — ĐẠT bằng test_c.

## WP-A3 non-regression

- 34/34 test WP-A3 + capital + engine PASS không sửa expected value nào.
- Toàn suite 95/95 PASS.
- Impact: `state_transitions`, `label_transitions`, BASE hoàn toàn bất biến;
  không mở lại finding F-001/F-021/F-022/F-030; không sửa file nào của WP-A3 ngoài
  đúng một hook rollover trong `engine.py` (thuộc Allowed list WP-A7).

## Key Decisions

1. PA-A (bộ đếm tháng trong `Pool` + một hook engine) thay vì tách struct budget riêng —
   tối thiểu xâm lấn, chữ ký `smart_reservable` không đổi (chi tiết CONVENTIONS #17).
2. Ranh giới mở sổ: SAU Month-End settle, TRƯỚC contribution (BT §19 bước 3→5).
3. Carry-first cho reserve vắt tháng; chiều sai duy nhất là bảo thủ (BT §1).
4. `opportunity_reservable` không đổi (ST §7 lifetime là ĐÚNG — bất đối xứng có chủ đích).
5. Lịch sử lifetime ledger không bị xoá/reset trong bất kỳ nhánh code hay test nào.

## Risks / Blockers

- Không blocker cho WP-A7. PH-04 là giới hạn đã biết, ngoài scope, chờ owner.
- Validator `validate_evidence.py`/`validate_task_completion.py` quét glob `TASK-*.md`
  không khớp file task hiện tại (đặt tên `WP-*`) → PASS trên tập rỗng; đây là giới hạn
  tooling có sẵn từ trước, KHÔNG được sửa trong scope WP-A7 (ghi nhận lại, đã nêu ở S003).

## Regression Items (giữ nguyên các mục S003 + bổ sung)

- Không sửa expected value test WP-A3/WP-A7 để "cho qua" — mọi thay đổi phải truy vết spec.
- Không reset/xoá ledger lifetime để làm đẹp bộ đếm tháng (tái phạm F-035 chiều ngược).
- Carry không được đếm vào quyền tháng mới (không "trả quyền" khi release carry).

## Do Not Change Yet

- `score.py`, `verdict.py`, `failure_signals.py`, `gates.py`, `benchmarks.py`,
  `metrics.py`, `pipeline.py`, `regime.py`, `ladders.py`, `data/`, `webapp/`,
  `docs/spec/` — ngoài Scope Lock WP-A7.
- BLK-001 giữ nguyên: không chạy official backtest, không tạo official verdict.

## Next Recommended Session

- WP-A4 (ngữ nghĩa dữ liệu xấu) — READY, song song roadmap-level đã được phép;
  `engine.py` merge tuần tự (S004 đã push trước, WP-A4 rebase sau).
- WP-A5 cần WP-A2+WP-A3+WP-A7; WP-A6 cần WP-A4 → chưa READY.

## Files Next Agent Should Read

1. `PROJECT/PROJECT_PROGRESS.md`
2. `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` (evidence 12 check)
3. `docs/CONVENTIONS.md` #17
4. `docs/reviews/PH-03-triage-smart-unlock-scope.md`
5. `tests/test_wp_a7_monthly_scope.py`

## E2 độc lập (CHECK-A7-12) và xử lý follow-up

Reviewer E2-WP-A7-001 (phiên riêng, bắt đầu từ trạng thái repo tại 39a8c22, diff từ
68bd8be, coi mọi tuyên bố implementer là không đáng tin): report đầy đủ tại
`docs/reviews/E2-WP-A7-monthly-smart-scope.md`. Kết luận: **E2 PASS WITH FOLLOW-UPS**
— cả 5 nội dung bắt buộc PASS bằng probe reviewer tự dựng (probe1–probe7):

1. Monthly scope: PASS — probe1 unit 4 tháng (budget 40, unlock từng phần, release giữa
   tháng) + engine 5 tháng (5 ladder, tháng 5 eligible 35.7143 gồm cap-overflow);
   BEFORE cùng probe: [40, 0, 0, 0].
2. Conservation: PASS — probe2 6 tháng / 2 crash vắt ranh giới / replayer độc lập từng
   entry; tổng == contribution 600; OVERFLOW khớp 1-1 hai vế.
3. Mode alive: PASS — probe3 TỰ DỰNG (crash chiếm vốn → hoãn tạo ladder qua điểm phân
   kỳ): 3 mode phân kỳ tới tận **eth_total** (0.4486 / 0.4387 / 0.3920) — mạnh hơn mức
   test_c; eligible khớp dự đoán canonical từng mode (30×1.0 / 30×0.9 / 30×(15/35)).
4. Opportunity non-regression: PASS — AST text hai hàm giống hệt; lưới 648 điểm
   BEFORE==AFTER; engine cap 80/overflow đúng; chỉ SMART được mở sổ.
5. No new lock/leak: PASS — probe5a crash vắt HAI ranh giới (carry drain về 0, mọi
   tháng trọn quyền 30); probe5b interleaving đối kháng vs reference per-lot:
   **worst over-grant = +0.000000** (không tồn tại cấp quyền dư), chỉ under-grant tạm
   thời đúng chiều bảo thủ BT §1, tự hết ở lần mở sổ kế.

Đối chiếu chéo: mọi con số then chốt của S004 tái lập chính xác (7F/1P, 8/8, 34/34,
95 passed, baseline 21.480751489892178/392/2/0.9106, AFTER 543/1045.9713/21.6370346).
**Không phát hiện mâu thuẫn.** Gate frozen xác nhận không bị sửa câu chữ.

Finding của reviewer và xử lý trong phiên:
- **F-E2A7-01 (LOW)** — định lượng giới hạn carry-first đã khai báo (under-grant tạm
  thời, tối đa cỡ carry, không over-grant). Không hành động (đúng như CONVENTIONS #17).
- **F-E2A7-02 (LOW hygiene)** — bộ đếm tháng trên pool không mở sổ tích luỹ không ngữ
  nghĩa. **Đã xử lý ngay trong S004**: bổ sung quy ước "phạm vi hiệu lực của bộ đếm
  tháng" vào CONVENTIONS #17 (cấm mã tương lai đọc bộ đếm của pool chưa mở sổ).
- **F-E2A7-03 (INFO)** — tinh chỉnh PH-04: hai mệnh đề đỡ là thuộc tính dataset, không
  phải bất biến cấu trúc; sức phân giải trên dataset chính thức là câu hỏi empirical.
  **Đã ghi vào PROGRESS** mục PH-04 (chờ owner cùng PH-04).
- Follow-up glob validator (`TASK-*.md` vs `WP-*`): tồn đọng tooling từ S003, ngoài
  scope — đã có trong danh sách chờ chủ dự án.

## Files changed (S004 — commit 1 `39a8c22` + commit 2 đóng gói)

Commit 2 bổ sung: `docs/reviews/E2-WP-A7-monthly-smart-scope.md` (report E2),
CONVENTIONS #17 (bổ sung F-E2A7-02), task file WP-A7 (CHECK-A7-12 + DONE + Exit
Criteria), PROGRESS/LO_TRINH (WP-A7 DONE, RSK-010 CLOSED, PH-04 tinh chỉnh), file này.

- `src/eth_dca_os/capital.py` — Pool: bộ đếm tháng + `open_accounting_month`;
  `reserve/release/deploy_from_reserved/deploy_from_available` cập nhật bộ đếm
  (carry-first); `smart_reservable` chuyển sang phạm vi tháng. Ledger không đổi.
- `src/eth_dca_os/engine.py` — MỘT hook: `smart_pool.open_accounting_month(ts)` tại
  rollover (sau settle, trước contribution, trước `su.month_reset`).
- `tests/test_wp_a7_monthly_scope.py` — MỚI: 8 test A–G test-first.
- `docs/CONVENTIONS.md` — thêm quy ước #17 (PA-A).
- `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` — Status IN_PROGRESS + evidence.
- `PROJECT/PROJECT_PROGRESS.md` (+ `PROJECT/LO_TRINH_DE_HIEU.md` sinh tự động).
- `docs/sessions/S004-wp-a7-monthly-smart-scope.md` — file này.
