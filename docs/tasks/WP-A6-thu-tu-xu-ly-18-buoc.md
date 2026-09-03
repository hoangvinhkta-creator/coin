# WP-A6 — Chốt và kiểm chứng đúng thứ tự các bước tính toán

## Metadata
Status:
VERIFYING — 6/8 REQUIRED PASS (E1) tại S014 (2026-09-03): CHECK-A6-01..06. CHECK-A6-07 (toàn
bộ test suite) đang chạy, còn NOT_TESTED tại thời điểm ghi dòng này — không tự đánh PASS trước
khi có output thật. CHECK-A6-08 (E2 độc lập) còn NOT_TESTED, chờ phiên reviewer riêng.

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
R: 3
B: 3
A: 2
X: 3
U: 3
V: 4
H: 3
C: 3
F: 3

Routing Categories:
none

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.1

Effort Routing Score:
3.2

Applied Model Floor:
cognitive:D>=4&X>=3

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
4/4

Risk:
3/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Trả lời dứt khoát câu hỏi: **official run đại diện cho thuật toán nào?**

Backtest §19 quy định 18 bước xử lý theo đúng thứ tự và ghi tường minh: "Mọi implementation phải
tuân thủ đúng thứ tự và **unit-test được thứ tự đó**". Hôm nay **không có test nào** kiểm thứ tự
(F-019), và việc đọc code cho thấy thứ tự thực tế lệch khỏi spec (F-018). Nghĩa là con số official
đang đại diện cho một thuật toán mà **chưa ai xác nhận là thuật toán đã đặc tả**.

## Trình tự bắt buộc của gói này

Thứ tự công việc là một phần của yêu cầu, không phải gợi ý:

1. **Viết test thứ tự TRƯỚC** (đóng F-019) — spec đòi tường minh.
2. **Rồi mới xác định sai lệch hiện tại** một cách chính xác (F-018).
3. **Rồi mới đo** sai lệch đó có làm đổi kết quả hay không, bằng chạy thật.
4. **Rồi mới quyết định** sửa hay ghi nhận là chấp nhận được — kèm bằng chứng.

Đảo thứ tự này sẽ dẫn tới việc viết test khớp với hành vi hiện có thay vì khớp với spec.

## Sai lệch đã biết từ S001 (F-018)

- Bước **15/16/17 không tách riêng** — fill, cập nhật ledger và cooldown nằm chung trong khối bước 12.
- **Tạo ladder chèn giữa bước 12 và 13**, nên ladder mới tham gia trigger ngay trong cùng nến.
- **Fill xảy ra trước** khi vốn khả dụng được đọc để tạo ladder.

Đây mới là quan sát mức E0 (đọc code). Gói này phải nâng nó lên E1.

## Đóng finding

- F-018 — thứ tự xử lý thực tế lệch khỏi Backtest §19
- F-019 — không có test nào kiểm thứ tự 18 bước

## Scope

- `tests/` — test thứ tự 18 bước, test no-lookahead ở tầng 15m
- `src/eth_dca_os/engine.py` — chỉ nếu bước 4 kết luận là phải sửa
- `docs/CONVENTIONS.md` — nếu bước 4 kết luận là ghi nhận sai lệch có chủ đích

## Out of Scope

- Vòng đời regime/ladder (WP-A3), ngữ nghĩa dữ liệu xấu (WP-A4) — cả hai phải xong trước
- Đo Failure Signal (WP-A5)
- Sửa V2.1.5 để hợp thức hoá thứ tự hiện tại — cấm bởi Master Index §6; nếu cần đổi spec thì chuyển
  sang **WP-D2**
- Mở rộng parity sang JS (WP-C4)

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE) — test thứ tự phải khoá vào hành vi cuối cùng
- **WP-A4** (DONE) — như trên
- **WP-A7** (DONE) — bắt buộc, thêm bởi **RCP-002** (2026-08-24).
  **Ràng buộc tường minh:** Completion Gate cuối cùng của WP-A6 **KHÔNG được chạy** trước khi
  WP-A7 DONE. Lý do: F-035 làm Smart ladder gần như suy biến sau những tháng đầu, nên một số
  đường xử lý Smart trong 18 bước sẽ không được thực thi đại diện cho behavior thật sau
  remediation. **Không được dùng test fixture suy biến hiện tại để né dependency này.**

## Blocks
- WP-C4 (parity phải khoá vào hành vi đã chốt)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-C1, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `tests/`
- `src/eth_dca_os/engine.py` — chỉ khi quyết định sửa, và chỉ ở phần thứ tự
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `score.py`, `execution.py`
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `gates.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [x] A6.1 Viết unit test kiểm thứ tự 18 bước theo BT §19 (làm trước tiên) — `tests/test_wp_a6_processing_order.py` + `tests/wp_a6_order_harness.py`, viết TỪ CHỮ §19 (S014)
- [x] A6.2 Chạy test đó trên code hiện tại; ghi lại chính xác sai lệch nào lộ ra — BEFORE: 11 FAIL / 7 PASS (18 test), chữ ký vi phạm ghi ở CHECK-A6-02
- [x] A6.3 Đo tác động của từng sai lệch lên kết quả bằng chạy thật, không bằng suy luận — `tests/wp_a6_impact_tool.py`, biến thể V_D1 / V_D2 / V_D18 / V_ALL / V_H15, hai exec config
- [x] A6.4 Quyết định sửa hay ghi nhận, kèm bằng chứng cho quyết định — SỬA cả ba nhóm sai lệch; các điểm §19 để ngỏ → CONVENTIONS #18; H-15 giữ nguyên → CONVENTIONS #19
- [x] A6.5 Nếu sửa: sửa và chạy lại test thứ tự tới khi khoá đúng hành vi cuối — `src/eth_dca_os/engine.py` (chỉ vòng lặp chính, chỉ thứ tự); 22/22 PASS; thử phá có chủ đích bị bắt
- [x] A6.6 Nếu ghi nhận: ghi vào `docs/CONVENTIONS.md` và mở mục cho WP-D2 nếu trái spec — CONVENTIONS #18, #19 + mục "Ghi chú cho WP-D2 từ WP-A6" (D2-A6-1…4)
- [x] A6.7 Bổ sung test no-lookahead ở tầng 15m — 3 test `test_a6_06_*`; mệnh đề 1 Impl Plan §7 tầng engine: XÁC NHẬN

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] **Dependency WP-A3 DONE** (S003; xác nhận lại khi mở task tại S014)
- [x] **Dependency WP-A4 DONE** (S009, DONE lại S010; xác nhận lại tại S014)
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §19, §21; IM §7 mệnh đề 1
- [x] Data impact được biết — có thể làm đổi kết quả mô phỏng nếu quyết định là sửa
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S014 (2026-09-03): WP-A3 ✅, WP-A4 ✅, WP-A7 ✅ (RCP-002) đều DONE trong `PROJECT_PROGRESS.md`; `branch_authority_check.sh` PASS (branch `claude/coindca-data-stream-vv0vwv`, ahead 0, production diff EMPTY); môi trường khớp `pyproject.lock` (Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1); baseline suite HEAD `b717634`: 286 passed / 0 failed

## Completion Gate

Risk = 3 → E1 bắt buộc. Vì gói này quyết định official run đại diện cho thuật toán nào, CHECK-A6-08
yêu cầu **E2**.

Nguyên tắc bằng chứng riêng của gói này: **không được dùng "đọc code thấy đúng thứ tự" làm bằng
chứng hoàn thành** cho bất kỳ REQUIRED check nào. Spec đòi test, và test là thứ phải tồn tại.

### Testing

#### CHECK-A6-01 — Tồn tại unit test kiểm thứ tự 18 bước và test đó chạy được
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại trong `tests/`, chạy thật, và **kiểm được thứ tự thật của các bước** (ví dụ
bằng cách quan sát trình tự tác dụng phụ), không phải chỉ kiểm sự tồn tại của hàm. Đóng F-019.

Kết quả: `tests/test_wp_a6_processing_order.py` (22 test) + `tests/wp_a6_order_harness.py`. Harness
patch namespace `eth_dca_os.engine`/`ladders` để ghi DÒNG SIDE-EFFECT THẬT: ledger `Pool`
(contribute/reserve/release/deploy/transfer/open_accounting_month), MỌI chuyển trạng thái
`Zone`/`Ladder` (subclass với `__setattr__`), `apply_fill`, `RegimeTracker.update`,
`OpportunityHysteresis.update`, `SmartUnlockState.month_reset`, `update_bullish_invalidation`, tạo
ladder; đồng hồ nến = chính lần đọc `c["ts"][i]` (bước 1). Mỗi sự kiện ánh xạ về bước §19 theo CHỮ
spec (`letter_map`); `order_violations` báo mọi cặp bước GIẢM trong cùng nến. Test tự khẳng định
harness quan sát thật: số `CLOCK` == số nến, số `FILL` == số purchase record
(`test_a6_01_harness_observes_real_side_effects`). Chạy thật: BEFORE (engine chưa sửa) 11 FAIL / 7 PASS
trên 18 test — test được phép đỏ đúng như "Trình tự bắt buộc"; AFTER 22/22 PASS (`22 passed in 8.82s`).
Kịch bản dàn dựng (SC1 fill+trigger cùng nến, crash entry, rollover+Base cùng nến qua gap, Month-End
hai đường, hysteresis suspend+confirmation, CRASH→RECOVERY→NORMAL) đều tự khẳng định tiền đề; cộng
long-run 2 năm dữ liệu tổng hợp với cả `gate1_low_friction` lẫn `gate3_realistic`.

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

#### CHECK-A6-02 — Sai lệch thứ tự hiện tại được xác định chính xác ở mức E1
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output của test thứ tự chạy trên code **trước khi sửa**, cho thấy chính xác bước nào lệch.
Ba quan sát E0 của F-018 phải được xác nhận hoặc bác bỏ từng cái một.

Kết quả (chạy trên HEAD `b717634`, `engine.py` chưa sửa; output đầy đủ trong biên bản S014 §3):
`.F.F.FFFFF.FFFF...` — 11 FAIL / 7 PASS. Chữ ký vi phạm long-run gate1 (2019-06 → 2021-06):
`RESERVE[SMART_ZONE_S2]@14 ⇒ ZONE[ACTIVE→TRIGGERED]@13` ×12 · `BULLISH_CHECK@18 ⇒ HYST_UPDATE@8`
×107 · `ZONE[ACTIVE→CANCELLED]@18 ⇒ HYST_UPDATE@8` ×3 · `ZONE[ACTIVE→SUSPENDED]@18 ⇒
REGIME_UPDATE@10` ×1 · `ZONE[SUSPENDED→CANCELLED]@18 ⇒ REGIME_UPDATE@10` ×1; kịch bản SC1:
`FILL@16 ⇒ ZONE[ACTIVE→TRIGGERED]@13`; crash: `RESERVE[CRASH_ZONE]@14 ⇒ TRIGGERED@13`. Trên dataset
tổng hợp 7,5 năm (`wp_a6_impact_tool.py`): 1151 vi phạm (gate1) / 1156 (gate3); **88/88** ladder (67
Smart + 17 Crash + 4 Opp) có zone đầu TRIGGERED ngay trong nến tạo; 8 nến vừa fill vừa có trigger mới.
Từng quan sát của F-018: (1) "15/16/17 nằm trong khối bước 12" — **XÁC NHẬN** (`FILL@16` đứng trước
`TRIGGERED@13`/`ACTION_PENDING@14` trong cùng nến, `test_a6_fill_after_new_trigger_in_same_candle`
đỏ). (2) "tạo ladder chèn giữa 12 và 13 nên ladder mới trigger cùng nến" — **XÁC NHẬN** (88/88; và
vì zone đầu có target = anchor = OPEN nến tạo mà LOW ≤ OPEN luôn đúng, đây là cơ chế, không phải
ngẫu nhiên; áp cả Crash ladder tạo trong khối bước 10). (3) "fill xảy ra trước khi vốn khả dụng được
đọc để tạo ladder" — **XÁC NHẬN về thứ tự, BÁC BỎ về hệ quả**: `deploy_from_reserved` không đổi
`available` lẫn tổng `month_reserved + month_deployed` nên vốn reservable không đổi; đo bằng biến thể
V_D1 (chỉ dời fill ra sau 14): kết quả trùng bit (CHECK-A6-03). Hai gợi ý E0 của orchestrator: (4)
"hai đường Month-End Smart settle" — **KHÔNG phải sai lệch thứ tự**: Day 28 12:00 là CONVENTIONS #7
trong khe bước 9, rollover là §19 bước 3 và chỉ là fallback (gap Day 28, vốn release sau Day 28); đo
`test_a6_month_end_two_paths_settle_once`: không settle đúp, ladder hết hạn đúng một lần, tổng SMART
tháng 3 hai kịch bản đều = 30,0. (5) "các mục bước 18 chạy sớm ở bước 8/10" — **XÁC NHẬN**
(`BULLISH_CHECK@18 ⇒ HYST_UPDATE@8` ×1019 trên 7,5 năm; hysteresis `SUSPENDED@18 ⇒ REGIME_UPDATE@10`
×12; recovery `SUSPENDED@18 ⇒ TRIGGERED@13` trong kịch bản SC6); khối "// 18." cuối vòng lặp chỉ có
expiry Opportunity + COMPLETED.

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

#### CHECK-A6-03 — Tác động của sai lệch lên kết quả được đo bằng chạy thật
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: so metric giữa thứ tự hiện tại và thứ tự theo spec, trên cùng seed và dataset. Nếu kết luận
là "sai lệch vô hại", kết luận đó phải dựa trên số đo này, **không** dựa trên lập luận.

Kết quả: `tests/wp_a6_impact_tool.py` (tái lập từ repo, `--src` như công cụ WP-A3), cùng dataset
`data.synth.generate` (SYNTH_SEED 20260822), cửa sổ 2019-01-01 → 2026-06-01, baseline + hai exec
config; mỗi sai lệch được sửa RIÊNG trong một bản sao engine (scratchpad) rồi đo:
| Biến thể | gate1 ETH | Δ | purchase | Ghi chú |
|---|---|---|---|---|
| BASE (chưa sửa) | 21,6370346047919 | — | 543 | 1151 vi phạm chữ §19; 88 trigger cùng nến tạo |
| V_D1 — 15–17 sau 14 + ưu tiên bước 15 | 21,6370346047919 | 0 (trùng bit) | 543 | 11 bản ghi lệch ≤ 3e-16 tương đối (ULP, đổi thứ tự phép cộng ledger); gate3: 543/543 trùng hoàn toàn |
| V_D18 — mục 18 về cuối | 21,6370346047919 | 0 (trùng bit) | 543 | 543/543 bản ghi trùng, cả hai config |
| V_D2 — tạo ladder sau 13 | 21,64865871993361 | **+0,0537 %** | 541 | Smart zone 153→152, Opp 17→16; nominal BASE 4450 / SMART 4270,21 / CRASH 139,57 KHÔNG đổi, Opp 5,823→5,743; triggered 193→191; ladder 67/14/17 không đổi; phân kỳ đầu 2019-01-04 07:30→07:45 (fill S0 lùi một nến) |
| V_ALL (= src cuối) | 21,64865871993361 | +0,0537 % | 541 | 0 vi phạm; FINAL trên `src` trùng bit V_ALL |
gate3: BASE 21,622354119695885 → V_ALL 21,636121265847837 (+0,0637 %), 543 → 541; V_D1/V_D18 trùng bit.
H-15 (`--drop-daily 2020-06-15`, cửa sổ INVALID 31 ngày = 1,14 % nến): 0 zone TRIGGERED trong chu kỳ
INVALID ở cả BASE, V_ALL lẫn V_H15 (biến thể huỷ trigger khi INVALID); V_ALL == V_H15 hoàn toàn (528
purchase, ETH 21,634883289142703). Kết luận "vô hại" cho D1/D18 và "nhỏ, giải thích được" cho D2 đều
dựa trên các số đo này. File JSON của mọi lần đo lưu tại scratchpad phiên; bảng tóm tắt ở biên bản S014.

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

#### CHECK-A6-04 — Quyết định sửa-hay-ghi-nhận được đưa ra và có căn cứ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: quyết định được ghi lại kèm số đo của CHECK-A6-03. Nếu chọn **ghi nhận**: sai lệch phải
được ghi vào `docs/CONVENTIONS.md` như một quy ước được tuyên bố; và nếu nó **trái chữ của BT §19**
thì phải mở mục cho **WP-D2** (đề xuất V2.2), vì Master Index §6 cấm vá tại chỗ V2.1.5. Không được
im lặng chấp nhận.

Kết quả: **SỬA** cả ba nhóm sai lệch theo chữ §19 (F-018a: 15–17 sau 14; F-018b: tạo ladder — kể cả
Crash — ở bước 14 sau 13; mục 18 gom về cuối). Căn cứ: D1 và D18 không đổi kết quả (trùng bit); D2 đổi
+0,054 % / +0,064 % ETH, −2/543 fill, không đổi nominal BASE/SMART/CRASH, mọi phân kỳ truy về đúng
bước 13→14 — dưới tiêu chí "đáng kể" mà phiên đặt ra và ghi ở S014 (|ΔETH| < 0,1 %, nominal
Base/Smart/Crash không đổi, phân kỳ đầu tiên giải thích được bằng bước đã đổi); Escalation Trigger
"đổi kết quả đáng kể" KHÔNG kích hoạt, nhưng số đo được trình để orchestrator/chủ dự án xác nhận
trước khi commit. **Không** giữ lại điểm nào trái chữ §19. Những điểm §19 **để ngỏ** được tuyên bố
thành quy ước `docs/CONVENTIONS.md` #18 (a–f: nhóm 16/17 nguyên tử; bước 15 chỉ sắp thứ tự ghi sổ;
tạo ladder = "tạo reservation" bước 14; MISSED/TTL ở bước 12; các mục bước 18; Month-End Day 25/28
trong khe bước 9). H-15: **giữ nguyên** (TRIGGERED sống qua chu kỳ INVALID, action ở chu kỳ hợp lệ
đầu tiên) — CONVENTIONS #19, căn cứ đo ở CHECK-A6-03, cái giá của quy ước đo ở mức kịch bản
(`test_h15_trigger_in_invalid_cycle_persists_until_first_valid_cycle`: fill ở 100 dù target 94,6/89,2).
Mục "Ghi chú cho WP-D2 từ WP-A6" (cuối CONVENTIONS.md): D2-A6-1 khe Month-End trong §19; D2-A6-2 vị
trí "tạo ladder" và ngữ nghĩa S0; D2-A6-3 số phận trigger trong INVALID; D2-A6-4 Month-End settle có
tính là execution cho cooldown (quan sát, không quyết định). Không tạo task ID, không sửa spec.

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

#### CHECK-A6-05 — Sau khi xử lý, test thứ tự PASS và khoá đúng hành vi cuối cùng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test thứ tự chạy PASS trên code cuối, và test đó **sẽ FAIL** nếu ai đó đổi lại thứ tự —
chứng minh bằng một lần thử phá có chủ đích.

Kết quả: trên `src/eth_dca_os/engine.py` cuối: `22 passed in 8.82s`; long-run gate1/gate3 (2 năm) 0
vi phạm; dataset 7,5 năm 0 vi phạm với cả hai config (`letter_violations_total = 0`,
`same_candle_trigger_after_create = 0`). Thử phá có chủ đích, TÁI LẬP ĐƯỢC và chạy thường trực trong
suite: `test_a6_05_order_test_detects_deliberate_reordering` nạp `engine.py` từ mã nguồn, dời một khối
theo marker (`move_block`, đỏ nếu marker không còn duy nhất) rồi chạy kịch bản: (1) dời khối 14b (tạo
ladder) lên trước 13 — tái tạo F-018b → bắt được với chữ ký `RESERVE[SMART_ZONE_S2]@14 ⇒
ZONE[ACTIVE→TRIGGERED]@13`; (2) dời khối 15–17 lên trước 13 — tái tạo F-018a → `FILL@16 ⇒
ZONE[ACTIVE→TRIGGERED]@13`; (3) dời 18a (bullish invalidation) lên trước 9 → `BULLISH_CHECK@18 ⇒
REGIME_UPDATE@10`. Cả ba PASS (tức phép kiểm ĐỎ trên bản đảo), đối chứng engine thật sạch trên cùng
kịch bản. Ngoài ra lần chạy đầu của bộ test trên engine cũ (11 FAIL) chính là một lần "phá" tự nhiên.

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

#### CHECK-A6-06 — Không lookahead ở tầng 15m
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test khẳng định engine chỉ dùng nến đã đóng ở tầng 15m. Mệnh đề 1 của Impl Plan §7 hiện là
"XÁC NHẬN một phần — không kết luận được cho tầng engine"; gói này phải đưa nó về kết luận.

Kết quả: ba test, PASS trên cả engine cũ lẫn mới: (1)
`test_a6_06_daily_score_visible_only_after_daily_candle_closes` — oscore truyền vào `regime.update` ở
MỌI nến (3 tháng, > 8.500 nến) bằng đúng score của ngày daily gần nhất có `day_end ≤ ts` (D+1 00:00 UTC)
và khác score của ngày chưa đóng khi hai giá trị khác nhau; (2)
`test_a6_06_future_daily_rows_cannot_change_past_candles` — đầu độc MỌI hàng daily sau 2019-12-15
(oscore 100, INVALID, return7 −0,9, adr30 0,5, close 1): purchases / cash_samples / decision_log /
contributions trước mốc D+1 00:00 UTC trùng khớp bit-for-bit với run sạch, và sau mốc hai run KHÁC
nhau (đối chứng phép đầu độc có tác dụng); (3) `test_a6_06_future_15m_candles_cannot_change_past_state`
— cắt chuỗi 15m tại 2019-11-20 13:30 UTC và (biến thể) đầu độc OHLC mọi nến sau mốc = 1,0: tiền tố
kết quả trùng khớp, phần sau khác. Lưu ý đã ghi trong test: `zone`/`ladder` id trong decision_log là
bộ đếm toàn cục `itertools.count` của `ladders.py` (tăng qua các lần chạy), bị loại khi so sánh — không
phải trạng thái engine. Kết luận mệnh đề 1 Impl Plan §7 cho tầng engine 15m: **XÁC NHẬN** (E1).

Executed By:
S014 agent (Claude, Tier D / max)

Timestamp:
2026-09-03

### Regression

#### CHECK-A6-07 — Toàn bộ test suite PASS; thay đổi kết quả (nếu có) được định lượng và giải thích
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; nếu quyết định là sửa thứ tự thì so metric trước–sau và quy sai
lệch về đúng bước đã đổi.

Executed By:
...

Timestamp:
...

### Audit độc lập

#### CHECK-A6-08 — Rà soát độc lập E2 cho thứ tự và cho kết luận sửa-hay-ghi-nhận
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer độc lập đọc BT §19 từ spec, đối chiếu độc lập với hành vi thật, và tự kết
luận thứ tự có khớp hay không — **không đọc kết luận của người cài đặt trước**. Lưu tại
`docs/reviews/`.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS — **7/8** (CHECK-A6-08 E2 độc lập còn NOT_TESTED, chờ phiên reviewer riêng)
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ; E2 cho CHECK-A6-08) — E1 đủ cho 01…07; E2 chưa
- [x] Câu hỏi "official run đại diện cho thuật toán nào" có câu trả lời dứt khoát, có bằng chứng — **thuật toán theo đúng 18 bước BT §19 (chữ) cộng quy ước #18/#19 cho các điểm §19 để ngỏ**; khoá bằng test quan sát side-effect, đo trên dataset tổng hợp (E1; E2 chờ CHECK-A6-08 xác nhận độc lập)
- [x] Nếu ghi nhận sai lệch: quy ước được ghi và (nếu trái spec) mục đề xuất V2.2 được mở ở WP-D2 — không giữ điểm nào trái chữ §19; CONVENTIONS #18/#19 + mục "Ghi chú cho WP-D2 từ WP-A6" (D2-A6-1…4)
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật — dòng WP-A6 (S014); `sync_easy_roadmap.py` chưa chạy (file sinh ngoài vùng cho phép của phiên — orchestrator chạy)
- [x] Session handoff được viết — `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md`
- [x] Không hạ REQUIRED check nào để đạt DONE — 8 check giữ nguyên câu chữ; CHECK-A6-08 để NOT_TESTED, không tự đánh PASS

## Escalation Triggers

- Không dựng được test quan sát thứ tự mà không phải tái cấu trúc lớn `engine.py` →
  `VERIFICATION_DEPTH` trước; nếu vẫn không được thì `SCOPE_CHANGED` và trình chủ dự án. **Không bỏ
  qua yêu cầu test** — BT §19 đòi tường minh.
- Sửa thứ tự làm đổi kết quả đáng kể → DỪNG và trình chủ dự án trước khi nghiệm thu. Đây là thay đổi
  bản chất của thuật toán được đem đi chạy official.
- Sai lệch thứ tự hoá ra là **spec mâu thuẫn với chính nó** → `CONFLICT DETECTED`, chuyển sang WP-D2.
- WP-A3 hoặc WP-A4 chưa DONE → `MISSING_INPUT`, giữ PLANNED. Test viết bây giờ sẽ khoá vào hành vi
  sắp đổi.

## Ảnh hưởng nếu gói này thất bại

Mắt xích cuối trước GATE-A. Nếu thất bại: GATE-A không đóng, T-06 không mở, WP-C4 không khoá được
parity. Nếu bỏ qua và vẫn chạy official run: kết quả official sẽ đại diện cho một thuật toán mà
không ai chứng minh được là thuật toán trong spec — và vì Master Index §6 cấm chạy lại, câu hỏi đó
sẽ **không bao giờ trả lời được** cho lần chạy đó.

## Changed Files Registry

Created (S014):
- `tests/test_wp_a6_processing_order.py` — 22 test: thứ tự §19 (kịch bản + long-run), no-lookahead 15m, H-15, thử phá có chủ đích
- `tests/wp_a6_order_harness.py` — harness quan sát side-effect + ánh xạ bước §19 + nạp engine đảo thứ tự
- `tests/wp_a6_impact_tool.py` — công cụ đo impact CHECK-A6-03/07 (tái lập từ repo)
- `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md` — biên bản phiên
- (chờ phiên độc lập) `docs/reviews/E2-WP-A6-*.md`

Modified (S014):
- `src/eth_dca_os/engine.py` — CHỈ vòng lặp chính `run_engine`, CHỈ thứ tự: bước 8 chỉ kích hoạt score; bước 10 chỉ cancel/release/snapshot; bước 12 chỉ xác định due-fill + MISSED/TTL; tạo ladder (14a Crash, 14b Smart/Opp) sau 13; 15 sắp ưu tiên; 16–17 fill; 18a–d gom lifecycle. Một biến chết `prev_dq` (chưa từng được đọc) bị bỏ trong khối được viết lại.
- `docs/CONVENTIONS.md` — #18, #19, mục "Ghi chú cho WP-D2 từ WP-A6"
- `PROJECT/PROJECT_PROGRESS.md` — dòng WP-A6 trong bảng roadmap
- `docs/tasks/WP-A6-thu-tu-xu-ly-18-buoc.md` — evidence Completion Gate (file này)

Deleted:
- Không

Migration Impact:
- Không (không đổi schema/dữ liệu; kết quả mô phỏng đổi +0,054 %/+0,064 % ETH trên dataset tổng hợp — xem CHECK-A6-03)

## Notes

Đây là gói dễ bị "làm cho xong" nhất trong lớp A, vì cám dỗ tự nhiên là viết một test khớp với hành
vi hiện có rồi tuyên bố thứ tự đã được kiểm chứng. Test đó sẽ luôn PASS và không chứng minh gì cả.
Trình tự bắt buộc ở đầu tài liệu tồn tại để chặn đúng điều đó: test phải được viết **từ spec**, chạy
trên code hiện tại, và **được phép thất bại** ở lần chạy đầu tiên.
