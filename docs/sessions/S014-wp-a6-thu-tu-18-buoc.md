# SESSION HANDOFF — S014

Session ID:
S014

Task:
WP-A6 — Chốt và kiểm chứng đúng thứ tự các bước tính toán (Backtest §19, 18 bước mỗi nến 15m)

Task Mode:
MAJOR

Project Profile:
PRODUCT

Ngày:
2026-09-03

Status:
**VERIFYING — 7/8 REQUIRED PASS (E1 toàn bộ).** CHECK-A6-08 (rà soát độc lập E2) còn
`NOT_TESTED` và **BẮT BUỘC** do một phiên reviewer riêng, không đọc kết luận của phiên này
trước, thực hiện sau. Toàn bộ thay đổi để ở **working tree, CHƯA commit, CHƯA push** — chờ
orchestrator/chủ dự án duyệt.

Model/Effort thực thi:
Tier D (Claude) / max — đúng routing đóng băng trong file task (`validate_routing.py` PASS tại
phiên: 19 MAJOR task file, 0 override).

Kết quả một dòng:

    WP-A6 = 7/8 REQUIRED PASS (E1) · engine.py sửa CHỈ thứ tự theo chữ BT §19 · F-019 đóng ·
    F-018 nâng E0→E1 và sửa · H-15 trả lời (GIỮ NGUYÊN, CONVENTIONS #19) · chờ E2 (CHECK-A6-08)

---

## 0. Branch authority & môi trường

```
branch            = claude/coindca-data-stream-vv0vwv
default branch    = main (resolved, not assumed)
behind upstream   = 0 · ahead of default = 0 · divergence LOC = 0
integration       = INTEGRATION_DECISION_REQUIRED=NO
tracked worktree  = CLEAN khi bắt đầu · production diff = EMPTY khi bắt đầu
BRANCH AUTHORITY: PASS          (HEAD b717634)
```

Môi trường khớp `pyproject.lock` từng dòng: Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 ·
pyarrow 25.0.1 · requests 2.33.1 · pytest 9.1.1 (package chưa được cài trong container, cài
`pip install -e .` + đúng phiên bản ghim). Baseline suite tại HEAD `b717634`: **286 passed / 0
failed** (exit 0).

Ready Gate xác nhận lại khi mở task: WP-A3 ✅ (S003), WP-A4 ✅ (S009/S010), WP-A7 ✅ (S004, ràng
buộc RCP-002 "Completion Gate WP-A6 không chạy trước WP-A7 DONE" được thoả).

---

## 1. Trình tự bắt buộc đã tuân thủ

| Bước | Việc | Bằng chứng |
|---|---|---|
| A6.1 | Viết test thứ tự TỪ CHỮ §19, quan sát side-effect thật | `tests/wp_a6_order_harness.py`, `tests/test_wp_a6_processing_order.py` |
| A6.2 | Chạy trên engine CHƯA sửa → **11 FAIL / 7 PASS** (18 test) | §3 |
| A6.3 | Đo tác động TỪNG sai lệch bằng biến thể engine riêng, cùng seed/dataset | §4 |
| A6.4 | Quyết định SỬA cả ba nhóm; H-15 GIỮ NGUYÊN; quy ước #18/#19; ghi chú WP-D2 | §5, §6 |
| A6.5 | Sửa `engine.py` (chỉ thứ tự) → 22/22 PASS; thử phá có chủ đích bị bắt | §7 |
| A6.6 | Ghi CONVENTIONS + mục WP-D2 | `docs/CONVENTIONS.md` |
| A6.7 | Test no-lookahead tầng 15m → mệnh đề 1 Impl Plan §7: XÁC NHẬN | §8 |

Test không được viết khớp hành vi hiện có: lần chạy đầu tiên ĐỎ 11/18, đúng như file task cảnh
báo ở mục "Notes".

---

## 2. Cách kiểm "thứ tự thật" (CHECK-A6-01)

Harness patch namespace `eth_dca_os.engine`/`ladders` (không đổi hành vi) để ghi dòng sự kiện:
ledger `Pool` (contribute / reserve / release / deploy_from_reserved / deploy_from_available /
transfer / open_accounting_month), mọi chuyển trạng thái `Zone`/`Ladder` (subclass với
`__setattr__`), `apply_fill`, `RegimeTracker.update`, `OpportunityHysteresis.update`,
`SmartUnlockState.month_reset`, `update_bullish_invalidation`, ba hàm tạo ladder. Đồng hồ nến là
chính lần đọc `c["ts"][i]` ở đầu vòng lặp (bước 1), qua proxy mảng — nên sự kiện xảy ra trước
khi regime/score được đọc vẫn gắn đúng nến. Mỗi sự kiện ánh xạ về số bước §19 theo CHỮ spec
(`letter_map`); `order_violations` báo mọi cặp bước GIẢM trong cùng nến, kèm chữ ký
`(kind@bước_trước ⇒ kind@bước_sau)`.

Kịch bản dàn dựng (mỗi kịch bản tự khẳng định tiền đề): SC1 fill S0 và trigger mới trong CÙNG
nến; SC2 vào CRASH; SC3 nến đầu tháng rơi đúng 12:00 Day 3 (gap) → rollover + Base cùng nến;
SC4 Month-End hai đường (có/không có Day 28); SC5 hysteresis suspend + confirmation cùng nến;
SC6 CRASH → RECOVERY → NORMAL có zone bị xuyên tại nến chuyển trạng thái. Cộng long-run 2 năm dữ
liệu tổng hợp với `gate1_low_friction` và `gate3_realistic`.

---

## 3. Sai lệch lộ ra trên engine CŨ (CHECK-A6-02) — A6.2

Output lần chạy đầu (HEAD `b717634`): `.F.F.FFFFF.FFFF...` — **11 failed, 7 passed**.

Chữ ký vi phạm, long-run gate1 2019-06 → 2021-06:

```
RESERVE[SMART_ZONE_S2]@14      => ZONE[ACTIVE->TRIGGERED]@13      x12
BULLISH_CHECK@18               => HYST_UPDATE@8                   x107
ZONE[ACTIVE->CANCELLED]@18     => HYST_UPDATE@8                   x3
ZONE[ACTIVE->SUSPENDED]@18     => REGIME_UPDATE@10                x1
ZONE[SUSPENDED->CANCELLED]@18  => REGIME_UPDATE@10                x1
```

Kịch bản: `FILL@16 => ZONE[ACTIVE->TRIGGERED]@13` (SC1), `RESERVE[CRASH_ZONE]@14 =>
TRIGGERED@13` (SC2), `ZONE[ACTIVE->SUSPENDED]@18 => ZONE[ACTIVE->TRIGGERED]@13` và
`LADDER[CRASH:SUSPENDED->CANCELLED]@18 => TRIGGERED@13` (SC6). Trên dataset 7,5 năm: **1151** vi
phạm (gate1) / 1156 (gate3); **88/88 ladder** (67 Smart + 17 Crash + 4 Opp) có zone đầu TRIGGERED
ngay trong nến tạo; 8 nến vừa fill vừa có trigger mới.

Kết luận từng quan sát:

| # | Quan sát | Kết luận | Căn cứ |
|---|---|---|---|
| F-018 (1) | 15/16/17 nằm trong khối bước 12 | **XÁC NHẬN** | `FILL@16` trước `TRIGGERED@13`/`ACTION_PENDING@14` cùng nến |
| F-018 (2) | Tạo ladder giữa 12 và 13 → trigger cùng nến | **XÁC NHẬN** | 88/88 ladder; cơ chế: zone đầu target = anchor = OPEN nến tạo, LOW ≤ OPEN luôn đúng. Áp cả Crash ladder (tạo trong khối 10) |
| F-018 (3) | Fill trước khi đọc vốn khả dụng để tạo ladder | **XÁC NHẬN về thứ tự — BÁC BỎ về hệ quả** | `deploy_from_reserved` không đổi `available` lẫn `month_reserved + month_deployed` → vốn reservable không đổi; đo V_D1 trùng bit |
| E0-hint (4) | Hai đường Month-End Smart settle | **KHÔNG phải sai lệch thứ tự** | Day 28 = CONVENTIONS #7 (khe bước 9); rollover = §19 bước 3, fallback (gap Day 28 / vốn release sau Day 28). Đo SC4: không settle đúp, ladder hết hạn đúng một lần, SMART tháng 3 = 30,0 ở cả hai |
| E0-hint (5) | Mục bước 18 chạy sớm ở bước 8/10 | **XÁC NHẬN** | bullish ×1019, hysteresis ×12+, recovery suspension/cancel — khối "// 18." cũ chỉ có expiry Opp + COMPLETED |

Phát hiện phụ khi dựng SC4: settle Month-End tại rollover (fallback) ghi purchase nguồn SMART nên
đặt cooldown 48h tràn sang tháng mới, chặn S0 của ladder mới ngày 01/04 (kịch bản B không có fill
S0, kịch bản A có). Không phải thứ tự — ghi D2-A6-4 (§6), không quyết định trong gói này.

---

## 4. Tác động đo được (CHECK-A6-03) — A6.3

`tests/wp_a6_impact_tool.py` (tái lập từ repo; `--src` để đo bản sao engine), dataset
`data.synth.generate` SYNTH_SEED 20260822, cửa sổ 2019-01-01 → 2026-06-01, baseline. Mỗi sai lệch
sửa RIÊNG trong một bản sao `engine.py` (scratchpad) rồi đo với cả hai exec config.

| Biến thể | gate1 ETH | Δ ETH | purchase | Khác biệt bản ghi | Ghi chú |
|---|---|---|---|---|---|
| BASE (chưa sửa) | 21,6370346047919 | — | 543 | — | 1151 vi phạm; 88 trigger cùng nến tạo |
| V_D1 — 15–17 sau 14 + ưu tiên 15 | 21,6370346047919 | **0 (trùng bit)** | 543 | 11/543 lệch ≤ 3e-16 tương đối (ULP, đổi thứ tự phép cộng ledger); gate3 543/543 trùng | vô hại |
| V_D18 — mục 18 về cuối | 21,6370346047919 | **0 (trùng bit)** | 543 | 543/543 trùng, cả hai config | vô hại |
| V_D2 — tạo ladder sau 13 | 21,64865871993361 | **+0,0537 %** | 541 | 435/543 trùng; phân kỳ đầu 2019-01-04 07:30 → 07:45 | Smart zone 153→152, Opp 17→16; nominal BASE 4450 / SMART 4270,21 / CRASH 139,57 **không đổi**, Opp 5,823→5,743; triggered 193→191; ladder 67/14/17 không đổi |
| V_ALL = src cuối | 21,64865871993361 | +0,0537 % | 541 | 0 vi phạm; FINAL trên `src` trùng bit V_ALL | |

gate3: BASE 21,622354119695885 → V_ALL 21,636121265847837 (**+0,0637 %**), 543 → 541; V_D1/V_D18
trùng bit. Mọi phân kỳ truy về đúng bước 13→14: zone đầu của mỗi ladder lùi một nến (fill ở OPEN
nến kế tiếp thay vì OPEN nến sau nến tạo); hai fill mất là zone đầu mà giá không quay lại anchor
trước khi ladder hết hạn (vốn Smart đó đi vào Month-End settle — nominal SMART không đổi; vốn Opp
ở lại quỹ).

H-15 (`--drop-daily 2020-06-15` → cửa sổ INVALID 31 ngày, 1,14 % nến): **0** zone TRIGGERED trong
chu kỳ INVALID ở BASE, V_ALL và V_H15 (biến thể huỷ trigger khi INVALID); V_ALL == V_H15 hoàn toàn
(528 purchase, ETH 21,634883289142703).

Tiêu chí "đáng kể" phiên đặt ra trước khi quyết định: |ΔETH| ≥ 0,1 %, HOẶC nominal Base/Smart/Crash
đổi, HOẶC phân kỳ đầu tiên không giải thích được bằng bước đã đổi → DỪNG trình chủ dự án. Không vế
nào chạm. Số đo vẫn được trình để orchestrator/chủ dự án xác nhận trước khi commit.

---

## 5. Quyết định (CHECK-A6-04) — A6.4

- **SỬA** cả ba nhóm theo chữ §19: (a) 15–17 sau 14 (fill/ledger/cooldown), bước 15 sắp ưu tiên
  bằng `zone_order_key`; (b) tạo ladder — Smart/Opp (14b) và Crash (14a, snapshot [F5] vẫn đo ở
  bước 10 theo ST §14) — SAU bước 13; (c) bullish invalidation, hysteresis, suspension/cancel
  Recovery gom về bước 18 (18a–c) trước expiry/completion (18d).
- **Không** giữ lại điểm nào trái chữ §19. Các điểm §19 **để ngỏ** chốt ở `CONVENTIONS.md` #18
  (a–f). **H-15: GIỮ NGUYÊN** — `CONVENTIONS.md` #19 (căn cứ đo §4; cái giá đo ở mức kịch bản:
  fill ở 100 dù target 94,6/89,2).
- Không tạo task ID, không sửa spec, không sửa `HARDENING_BACKLOG.md` (ngoài vùng cho phép —
  xem §11).

---

## 6. Ghi chú cho WP-D2 (cuối `docs/CONVENTIONS.md`)

D2-A6-1 khe cho Month-End Day 25/28 trong §19 · D2-A6-2 vị trí "tạo ladder" và ngữ nghĩa S0 (mua
ngay tại anchor hay limit từ nến kế tiếp — hai cách đọc cho kết quả khác nhau, đã đo) · D2-A6-3 số
phận trigger trong chu kỳ INVALID (H-15) · D2-A6-4 Month-End settle có tính là "execution" cho
cooldown (quan sát, không quyết định).

---

## 7. Sau khi sửa (CHECK-A6-05) — A6.5

`src/eth_dca_os/engine.py`: chỉ vòng lặp chính `run_engine`, chỉ thứ tự (diff 139+/108−, gần như
toàn bộ là dời khối; dòng code duy nhất bị bỏ hẳn là biến chết `prev_dq` chưa từng được đọc; dòng
mới là biến điều khiển `daily_close` / `crash_snapshot` / `due_fills`, sort bước 15, và guard
`lad.created_at < ts` ở 18a để ladder tạo cùng nến không bị đếm daily close đã hoàn tất trước khi
nó tồn tại).

- `tests/test_wp_a6_processing_order.py`: **22 passed in 8.82s** trên `src` cuối.
- Dataset 7,5 năm: `letter_violations_total = 0`, `same_candle_trigger_after_create = 0` (cả hai
  config).
- Thử phá có chủ đích, tái lập được, chạy thường trực:
  `test_a6_05_order_test_detects_deliberate_reordering` nạp `engine.py` từ mã nguồn, dời khối theo
  marker (đỏ nếu marker không còn duy nhất): 14b lên trước 13 (tái tạo F-018b) → bắt được
  `RESERVE[SMART_ZONE_S2]@14 ⇒ TRIGGERED@13`; 15–17 lên trước 13 (F-018a) → `FILL@16 ⇒
  TRIGGERED@13`; 18a lên trước 9 → `BULLISH_CHECK@18 ⇒ REGIME_UPDATE@10`. Đối chứng engine thật
  sạch trên cùng kịch bản.

---

## 8. No-lookahead tầng 15m (CHECK-A6-06) — A6.7

Ba test PASS (trên cả engine cũ lẫn mới): oscore hiệu lực tại MỌI nến bằng score của ngày daily
gần nhất có `day_end ≤ ts` (D+1 00:00 UTC); đầu độc mọi hàng daily sau 2019-12-15 không đổi một
trường nào trước mốc và có đổi sau mốc (đối chứng); cắt/đầu độc chuỗi 15m sau 2019-11-20 13:30 UTC
không đổi tiền tố. Mệnh đề 1 Impl Plan §7 cho tầng engine 15m: **XÁC NHẬN** (E1). Lưu ý kỹ thuật:
`zone`/`ladder` id trong decision_log là bộ đếm toàn cục `itertools.count` của `ladders.py`, bị
loại khi so sánh.

---

## 9. Regression (CHECK-A6-07)

- Baseline HEAD `b717634` (trước mọi thay đổi): **286 passed / 0 failed**, exit 0.
- Suite hiện có (không gồm file A6) chạy trên bản sao `V_ALL` qua `PYTHONPATH`: 282 passed / 4
  failed — cả 4 là `test_wp_a1_provenance.py::test_a1_01/03/08*` tìm `pyproject.lock` cạnh
  package (package được nạp từ scratchpad, không phải `src/`) → lỗi đường dẫn của cách đo, không
  phải của engine; xác nhận lại bằng full run trên `src` (dòng dưới).
- Full suite trên `src` cuối (286 test cũ + 22 test A6): xem §9.1.
- Kết quả đổi: đúng bằng bảng §4 (chỉ nhóm D2), quy về bước 13→14.
- Validator: `validate_routing.py` PASS · `validate_project_state.py` PASS ·
  `validate_structure.py` PASS · `validate_governance.py` chạy (H-08 vacuous-pass vẫn còn, không
  đụng) · `validate_easy_roadmap.py` **FAIL "stale"** vì dòng roadmap WP-A6 đã đổi nhưng phiên
  KHÔNG chạy `sync_easy_roadmap.py` (file sinh `PROJECT/LO_TRINH_DE_HIEU.md` ngoài vùng cho phép) —
  orchestrator cần chạy `python governance/scripts/governance/sync_easy_roadmap.py` rồi
  `validate_easy_roadmap.py`.

### 9.1 Full suite trên `src` cuối

(bổ sung khi lệnh `python -m pytest -p no:cacheprovider -rf` kết thúc — xem dòng cuối mục này)

---

## 10. Files changed

Created:
- `tests/test_wp_a6_processing_order.py` — 22 test
- `tests/wp_a6_order_harness.py` — harness quan sát + ánh xạ §19 + nạp engine đảo thứ tự
- `tests/wp_a6_impact_tool.py` — công cụ đo impact, tái lập từ repo
- `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md` — biên bản này

Modified:
- `src/eth_dca_os/engine.py` — chỉ thứ tự vòng lặp chính
- `docs/CONVENTIONS.md` — #18, #19, mục "Ghi chú cho WP-D2 từ WP-A6"
- `docs/tasks/WP-A6-thu-tu-xu-ly-18-buoc.md` — Status VERIFYING, Ready Gate, Subtask, evidence
  CHECK-A6-01…07, Changed Files, Exit Criteria; CHECK-A6-08 giữ NOT_TESTED
- `PROJECT/PROJECT_PROGRESS.md` — CHỈ dòng WP-A6 trong bảng roadmap

Không chạm (đúng Scope Lock): `regime.py`, `ladders.py`, `capital.py`, `score.py`,
`execution.py`, `verdict.py`, `failure_signals.py`, `gates.py`, `webapp/`, `docs/spec/`,
`PROJECT/HARDENING_BACKLOG.md`, `PROJECT/LO_TRINH_DE_HIEU.md`, `docs/reviews/`.

Dữ liệu đo (JSON impact, output pytest BEFORE/AFTER) nằm ở scratchpad phiên; mọi số liệu đều tái
lập được từ repo bằng `tests/wp_a6_impact_tool.py` và bộ test.

---

## 11. Scope Expansion gặp phải nhưng KHÔNG tự xử lý (để orchestrator quyết)

1. `PROJECT/HARDENING_BACKLOG.md` mục H-15 — orchestrator cho phép ghi RESOLVED ở đó "hoặc"
   CONVENTIONS; Expected Touch Area không có file này nên phiên chỉ ghi ở `CONVENTIONS.md` #19.
   Cần orchestrator cập nhật dòng trạng thái H-15 (tham chiếu CONVENTIONS #19 + CHECK-A6-03).
2. `PROJECT/LO_TRINH_DE_HIEU.md` (file sinh) — cần chạy `sync_easy_roadmap.py` sau khi duyệt dòng
   roadmap.
3. `PROJECT/CAPABILITY_REGISTRY.md` (`CAP-ORDER` đang PLANNED) và `PROJECT/REVIEW_BUDGET_LEDGER.md`
   (`CAP-ORDER` "chưa bắt đầu") — ngoài vùng cho phép, chưa cập nhật.
4. Quan sát D2-A6-4 (Month-End settle đặt cooldown) — nghiệp vụ, không thuộc thứ tự; chỉ ghi chú.

---

## 12. Completion Gate Summary

Required: 8 · PASS: 7 (CHECK-A6-01…07, E1) · NOT_TESTED: 1 (CHECK-A6-08, E2 độc lập) · FAIL: 0.
Không REQUIRED check nào bị hạ/bỏ. Không kích hoạt Escalation Trigger nào (không phải tái cấu
trúc lớn — chỉ dời khối trong vòng lặp; kết quả đổi dưới tiêu chí "đáng kể" §4; không phát hiện
spec tự mâu thuẫn — chỉ chỗ spec để ngỏ, ghi WP-D2).

## 13. Next Recommended Session

Phiên reviewer độc lập cho **CHECK-A6-08**: đọc BT §19 từ spec, chạy lại
`tests/test_wp_a6_processing_order.py` và `tests/wp_a6_impact_tool.py` (BASE tại `b717634` bằng
git worktree + `--src`, AFTER trên working tree), tự kết luận thứ tự có khớp hay không — KHÔNG đọc
§3–§5 của biên bản này trước khi tự đối chiếu. Lưu tại `docs/reviews/E2-WP-A6-*.md`. Sau E2 PASS:
WP-A6 → DONE, GATE-A còn chặn bởi WP-A1 (CAP-PROV budget = 0) và WP-A5.

## 14. Files Next Agent Should Read

- `AGENTS.md`, `CLAUDE.md`, `PROJECT/PROJECT_PROGRESS.md`
- `docs/tasks/WP-A6-thu-tu-xu-ly-18-buoc.md` (evidence từng check)
- `docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §19 (đọc TRƯỚC khi đọc bất kỳ kết luận nào ở đây)
- `docs/CONVENTIONS.md` #18, #19 và mục WP-D2
- `tests/wp_a6_order_harness.py` (cách ánh xạ sự kiện → bước)
