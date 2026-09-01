# S001 — AUDIT FINDINGS

Phiên: S001 — AUDIT READ-ONLY · Ngày: 2026-08-23 · Profile: PRODUCT
Source of Truth: **V2.1.5** (xem `S001-compliance-matrix.md` mục "Source of Truth")

Không sửa mã sản phẩm. Không remediation. Không refactor. Không finding nào được tự giải quyết.

## Thang mức bằng chứng dùng trong tài liệu này

| Mức | Nghĩa |
|---|---|
| `E0` | Đọc code, **chưa chạy**. Là nghi vấn, KHÔNG phải kết luận |
| `E1` | Đã chạy thật, có output (test suite, script kiểm chứng read-only, CLI, grep chương trình) |
| `E2` | Xác minh độc lập — **không có finding nào đạt E2 trong S001** |

## Bảng tổng hợp

| Mức | Số lượng | Có bằng chứng chạy thật (E1) | Mới là bằng chứng tĩnh (E0) |
|---|---|---|---|
| CRITICAL | 0 | — | — |
| HIGH | 8 | 7 | 1 |
| MEDIUM | 15 | 9 | 6 |
| LOW | 7 | 1 | 6 |
| INFO / SPEC DEFECT | 3 | 1 | 2 |
| **Tổng** | **33** | **18** | **15** |

Ngoài ra: **3 nghi vấn webapp kế thừa từ S000 (RSK-003) vẫn ở mức E0 và CHƯA được kiểm chứng
trong S001** — xem mục "Nghi vấn chưa kiểm chứng".

---

# HIGH

## F-001 — Reserve của Crash ladder không bao giờ được giải phóng khi Recovery kết thúc vào trạng thái STRESSED

Severity: **HIGH** · Category: Business Logic / Data Integrity · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `src/eth_dca_os/engine.py:415-419`, `src/eth_dca_os/regime.py:40-57`

**Expected Behavior** (Strategy §18.3): "Khi CRASH -> RECOVERY, các Crash zone chưa execute chuyển
SUSPENDED. Sau 72h Recovery nếu vẫn chưa hit thì CANCEL và release reserve."

**Current Behavior:** Nhánh dọn dẹp duy nhất là `engine.py:415`:
`if regime.regime == "NORMAL" and prev_regime == "RECOVERY"`.
Nhưng `RegimeTracker.update` kết thúc Recovery bằng cách đặt `regime = "NORMAL"` (regime.py:44)
rồi **rơi tiếp xuống dòng 56**, nơi nhãn STRESSED được đánh giá lại. Nếu lúc đó thị trường vẫn
yếu (`Return7D <= -10%` hoặc `Return24H <= -7%`) thì regime trở thành **STRESSED**, không phải
NORMAL. Điều kiện ở engine không khớp, Crash ladder giữ nguyên `SUSPENDED` vĩnh viễn.

Crash ladder có `expires_at = None` (`ladders.py:107`) và nhánh expiry ở `engine.py:527` **chỉ**
xử lý `OPPORTUNITY`. Không còn đường nào khác giải phóng reserve.

**Evidence (E1)** — script kiểm chứng read-only, không sửa repo:

```
=== KIỂM CHỨNG 1: RECOVERY kết thúc khi return còn yếu ===
  t=0h    regime=CRASH
  t=49h   regime=RECOVERY  (kỳ vọng RECOVERY)
  t=121h  regime=STRESSED  <-- 72h Recovery đã hết, return7d=-11%
=== KIỂM CHỨNG 2: cùng kịch bản nhưng return đã hồi ===
  t=121h  regime=NORMAL  (kỳ vọng NORMAL)
```

Bổ sung (E1, grep chương trình): mọi nơi Crash ladder bị huỷ trong engine chỉ gồm dòng 377
(lúc vào CRASH, huỷ Opportunity zone) và dòng 417 (nhánh NORMAL nói trên).

**Risk:** Vốn Smart và Opportunity bị khoá ở `RESERVED` không giới hạn thời gian. Hệ quả dây
chuyền: `smart_reservable` và `opportunity_reservable` trừ `reserved` khỏi hạn mức nên **ladder
mới không được tạo nữa**, cash ratio tăng giả tạo, AccumulationEfficiency giảm. Vì FS-07 dùng
`avg_cash_ratio` và FS-02 dùng cap-hit share, lỗi này có thể **bóp méo chính các Failure Signal**
dùng để kết luận verdict. Kịch bản kích hoạt (sập sâu → hồi một phần → vẫn yếu) là kịch bản
**thường gặp** trong crypto, không phải trường hợp biên hiếm.

**Vi phạm kép:** ngoài Strategy §18.3, đây còn là vi phạm **[F1]** (Strategy §17.3): STRESSED
được quy định "KHÔNG có bất kỳ hiệu ứng nào lên unlock, ladder, cooldown, limit hay execution".
Ở đây STRESSED **có** hiệu ứng — nó chặn việc dọn ladder.

**Likely Cause:** `regime.py` gộp nhãn dẫn xuất (STRESSED) vào cùng trường với trạng thái máy
(NORMAL/CRASH/RECOVERY). Strategy §16 yêu cầu Market Regime và Execution State lưu riêng, nhưng
không nói rõ nhãn dẫn xuất phải tách khỏi trạng thái nền — đây là chỗ spec để ngỏ và code chọn
cách gộp.

**Recommended Fix (KHÔNG thực hiện trong S001):** tách nhãn dẫn xuất khỏi trạng thái nền, hoặc
đổi điều kiện dọn dẹp sang "prev_regime == RECOVERY và regime không phải CRASH/RECOVERY".
Cần quyết định thiết kế, không phải sửa một dòng.

**Suggested Task:** R-01 · **Dependencies:** không
**Verification Required:** test cho chuỗi CRASH → RECOVERY → STRESSED, khẳng định reserve về 0.

---

## F-002 — Ba Failure Signal không bao giờ được đánh giá; verdict BUILD vẫn có thể phát ra

Severity: **HIGH** · Category: Business Logic · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `src/eth_dca_os/pipeline.py:187-203`, `src/eth_dca_os/verdict.py:26-37`

**Expected Behavior:** Backtest §17 định nghĩa FS-01…FS-12 và quy tắc chặn. Impl Plan §7:
"Bảng verdict và Failure-signal cap được áp dụng **tự động**."

**Current Behavior:** `run_verdict` gọi `evaluate_failure_signals` mà **không truyền** ba tham số.

**Evidence (E1)** — đối chiếu chương trình giữa chữ ký hàm và lời gọi thật:
```
Tham số KHÔNG được truyền: ['adjacent_config_flip', 'opportunity_cap_hit_share', 'regime_advantage_share']
```
Tức **FS-02, FS-06, FS-12 luôn = None (UNKNOWN)** trong mọi run.

Đồng thời `failure_signals.py:80` tính `any_true = any(v is True ...)` — `None` không phải `True`,
nên `verdict.py:27` đi vào nhánh `BUILD`. Verdict BUILD được phát ra kèm một dòng lý do
"FS chưa đánh giá được: FS-02, FS-06, FS-12", nhưng **không bị cap**.

**Risk:** Đây là cổng mở tới toàn bộ giai đoạn app (`can_proceed_to_app = (v == "BUILD")`).
Backtest §17 nói rõ lý do Failure Signal quan trọng hơn chính các gate: "chỉ có khoảng ba block
dữ liệu độc lập ... Failure Signal chẩn đoán cơ chế và đáng tin hơn". Bỏ qua 3/12 signal rồi
kết luận BUILD là bỏ đúng phần bằng chứng mà spec coi là mạnh nhất.
FS-02 (Opportunity reserve chạm cap và nằm im) đặc biệt đáng lo vì nó chính là triệu chứng mà
**F-001** sẽ tạo ra.

**Recommended Fix:** đấu nối ba input còn thiếu; và quyết định chính sách cho trường hợp UNKNOWN
(đề xuất: UNKNOWN chặn BUILD, vì §7 đòi "áp dụng tự động"). Chính sách này là quyết định của
chủ dự án, không phải của agent.

**Suggested Task:** R-02 · **Dependencies:** không
**Verification Required:** test khẳng định verdict không thể là BUILD khi tồn tại FS UNKNOWN.

---

## F-003 — Benchmark B, C, D được cài đặt đầy đủ nhưng pipeline không bao giờ chạy

Severity: **HIGH** · Category: Architecture / Evaluation · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `src/eth_dca_os/benchmarks.py:81-188`, `src/eth_dca_os/pipeline.py`

**Expected Behavior:** Backtest §12 định nghĩa benchmark A–G là bắt buộc. Backtest §22:
"Nếu Simple DCA hoặc một luật dip một dòng cho kết quả tương đương với độ phức tạp thấp hơn
nhiều, **luật đơn giản thắng**."

**Current Behavior:** Chỉ `run_benchmark_A` được gọi (trong `metrics.run_window`). B, C, D không
được gọi ở bất kỳ đâu trong `pipeline.py`, `cli.py`, `reporting.py`.

**Evidence (E1):**
```
KHÔNG ĐƯỢC GỌI: run_benchmark_B
KHÔNG ĐƯỢC GỌI: run_benchmark_C
KHÔNG ĐƯỢC GỌI: run_benchmark_D
KHÔNG ĐƯỢC GỌI: coverage_table
KHÔNG ĐƯỢC GỌI: xirr
KHÔNG ĐƯỢC GỌI: ablation_scores
KHÔNG ĐƯỢC GỌI: volume_zscore_variant
```

**Risk:** Nguyên tắc trung tâm của Backtest §22 — "bác bỏ trước, chứng minh sau", và luật đơn
giản thắng nếu tương đương — **không thể áp dụng**. Chiến lược V2.1.5 chỉ được so với A (Monthly
DCA). Nếu D (MA200 DCA, đã có reserve cap 6C đúng spec) cho kết quả tương đương thì theo §22 D
phải thắng, nhưng không ai biết vì D không được chạy. Verdict BUILD có thể được phát ra cho một
chiến lược phức tạp mà chưa từng bị đối chiếu với ba đối thủ đơn giản hơn.

Điểm đáng chú ý: code của B/C/D **đúng spec** khi đọc (D có cap 6C ở dòng 181-183; C có ngữ nghĩa
chu kỳ [F4] ở dòng 153-154). Đây là lỗi **đấu nối**, không phải lỗi thuật toán.

**Recommended Fix:** đấu nối B/C/D vào pipeline và đưa vào báo cáo so sánh.
**Suggested Task:** R-03 · **Verification Required:** test [F4] cho Benchmark C (BT §21.4 yêu cầu
tường minh nhưng hiện chưa có).

---

## F-004 — Chẩn đoán bắt buộc §2.3 (ablation) và §2.4 (volume z-score) không được chạy trong official run

Severity: **HIGH** · Category: Evaluation · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `src/eth_dca_os/diagnostics.py:81-103` và `run_all:104-113`

**Expected Behavior:** Strategy §2: "Các chẩn đoán dưới đây là **bắt buộc trong mọi official
run**." §2.3 yêu cầu ba model ablation; §2.4 yêu cầu "**Bắt buộc** chạy diagnostic song song với
V thay bằng rolling z-score ... và **báo cáo chênh lệch kết quả**".

**Current Behavior:** `ablation_scores` và `volume_zscore_variant` tồn tại, đúng công thức, nhưng
`run_all` chỉ trả về `correlation`, `redundancy_flags`, `vif`, `score_distribution`. Hai hàm kia
không được gọi ở đâu (bằng chứng E1 ở F-003).

**Risk:** Ablation là cơ chế duy nhất trả lời "P có đóng góp gì ngoài D không" và "RSI có đóng
góp gì ngoài Return7 không". Không chạy nó thì không có cơ sở kết luận ở §2.3 ("ưu tiên mô hình
đơn giản hơn ở version SAU"). §2.4 tồn tại vì thị phần Binance biến động theo năm khiến factor V
có thể nhiễm xu hướng cấu trúc — bỏ qua nghĩa là không biết OSCORE có bị nhiễm hay không.

**Recommended Fix:** đấu nối vào `run_all` và vào payload báo cáo.
**Suggested Task:** R-03 (cùng cụm đấu nối) · **Verification Required:** khẳng định payload
official chứa đủ ablation ba model và bảng chênh lệch volume z-score.

---

## F-005 — Cờ `official` không kiểm nguồn dữ liệu; run trên dữ liệu tổng hợp vẫn được ghi là chính thức

Severity: **HIGH** · Category: Data / Audit · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `src/eth_dca_os/pipeline.py:117,160,205`; `src/eth_dca_os/data/dataset.py:57`

**Expected Behavior:** Impl Plan §9 và DEC-003: verdict chính thức **bắt buộc** chạy trên dữ liệu
Binance thật. `ethdca synth` chỉ dùng dev/test. Data Model §13 yêu cầu lineage lưu **`source`**.

**Current Behavior:** Hai lỗ hổng cộng hưởng:
1. `official = (limit is None)` — chỉ phản ánh việc có dùng `--dev-limit` hay không. **Không có
   bất kỳ kiểm tra nào về nguồn dataset.**
2. `build_lineage` ghi `"source": "see fetch/synth"` — một **chuỗi cố định**, giống hệt nhau cho
   dữ liệu thật lẫn dữ liệu tổng hợp.

**Evidence (E1)** — đọc lineage của một dataset do `ethdca synth` sinh ra:
```
dataset_hash: 3ffcefbe047af8a8 ...
  BTCUSDT_1d  source='see fetch/synth'  rows=3102
  ETHUSDT_15m source='see fetch/synth'  rows=262748
  ETHUSDT_1d  source='see fetch/synth'  rows=3102
```

**Risk:** Chạy `ethdca synth && ethdca run all` (không `--dev-limit`) sẽ tạo ra một record mang
`official: true` và một verdict, trên dữ liệu **hoàn toàn nhân tạo**. Không có trường nào trong
`backtest_runs.jsonl` cho phép người đọc sau này phát hiện điều đó — `dataset_hash` chỉ chứng minh
tính tái lập, không chứng minh **nguồn gốc**. Đây là rủi ro thẳng vào tính toàn vẹn của verdict,
tức vào chính cổng mở đường cho app.

Lưu ý cân bằng: `cli.py` có in cảnh báo và `run_verdict` gắn `warning` khi dùng `--dev-limit`.
Nhưng không có lớp bảo vệ nào cho trường hợp full-run-trên-synth.

**Recommended Fix:** ghi `source` thật (fetch/synth) vào lineage, và để `official` phụ thuộc cả
nguồn dữ liệu lẫn `dev_limit`.
**Suggested Task:** R-04 — **nên làm trước T-06 (official run)** · **Verification Required:**
test khẳng định dataset synth không thể cho `official: true`.

---

## F-006 — Execution State machine không được cài đặt

Severity: **HIGH** · Category: Architecture · Status: OPEN · Evidence Level: **E1**

**Affected Area:** toàn bộ `src/`

**Expected Behavior:** Strategy §16 và §19 định nghĩa Execution State
`WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED`, và nêu rõ:
"Market Regime và Execution State là hai chiều độc lập và **phải được lưu riêng**".
Data Model §4 yêu cầu `market_snapshots.execution_state` LUÔN NOT NULL; §11 yêu cầu
`decision_log.previous_state / new_state` theo enum này.

**Current Behavior (E1, grep toàn `src/`):**
```
>>> KHÔNG tìm thấy: Execution State enum không được cài đặt ở đâu trong src/
```
Không chuỗi `WAIT`, `FUNDING_REQUIRED`, `READY_TO_BUY`, `DATA_BLOCKED` nào tồn tại.
Engine dùng `Zone.status` (một chiều khác, thuộc §19 zone enum) và biến cục bộ `in_cooldown`,
`dq` — tức thông tin có tồn tại nhưng **không được mô hình hoá thành trạng thái, không được lưu**.

**Risk:** Ba hệ quả. (a) `decision_log` không thể có `previous_state/new_state` → audit trail
không đạt Data Model §11. (b) `market_snapshots` không được sinh. (c) Khi sang giai đoạn app,
Product Spec §6/§11 đòi hiển thị đúng sáu trạng thái này — nếu backtest không mô hình hoá chúng
thì live và backtest sẽ mô tả cùng một tình huống bằng hai ngôn ngữ khác nhau, đúng loại trôi
lệch mà Impl Plan §1 muốn chặn.

**Recommended Fix:** cần quyết định phạm vi — mô hình hoá đầy đủ trong backtest, hay tuyên bố
NOT_APPLICABLE cho backtest và chỉ bắt buộc ở app. **Đây là quyết định kiến trúc của chủ dự án.**
**Suggested Task:** R-05 (kèm ADR) · **Dependencies:** liên quan DEC-005

---

## F-007 — Không ghim phiên bản thư viện; tái lập theo thời gian không được bảo đảm

Severity: **HIGH** · Category: Reliability / Reproducibility · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `pyproject.toml:8-13`, `src/eth_dca_os/reporting.py:37-51`

**Expected Behavior:** Backtest §20: "Cùng input phải cho cùng output, bit-for-bit ở mức metric."
Impl Plan §7 đặt tái lập làm tiêu chí nghiệm thu.

**Current Behavior:** `pyproject.toml` chỉ đặt **sàn** (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không lockfile, không trần. Run record lưu hash config/manifest/dataset và seed
nhưng **không lưu phiên bản thư viện** hay `code_commit`.

**Evidence (E1, đo tại S000):** cài mới kéo về `numpy 2.4.6`, `pandas 3.0.5`, `pyarrow 25.0.1` —
vượt sàn hai thế hệ lớn. Toàn bộ 69 test vẫn PASS trên bộ này.

**Risk:** Một thay đổi dấu phẩy động trong numpy/pandas ở bản sau có thể làm official run **không
tái lập được**, mà **mọi hash đầu vào vẫn trùng khớp** — nghĩa là hỏng âm thầm, không có tín hiệu.
Với một dự án mà official run chạy một lần rồi được viện dẫn nhiều năm, đây là khiếm khuyết
không sửa được về sau nếu run đã chạy.

**Recommended Fix:** ghim thư viện (lockfile hoặc trần phiên bản) và ghi môi trường vào run record.
**Suggested Task:** **T-06A đã có sẵn trong roadmap** — giữ nguyên làm điều kiện tiên quyết của T-06.
Xác nhận RSK-006. **Verification Required:** dựng lại môi trường từ lockfile và tái lập một run.

---

## F-008 — Live và backtest dùng hai bản cài đặt chiến lược; parity chỉ phủ OSCORE

Severity: **HIGH** · Category: Architecture · Status: OPEN · Evidence Level: **E1**

**Affected Area:** `webapp/engine.js` so với `src/eth_dca_os/`

**Expected Behavior:** Impl Plan §1: "Live và backtest phải reuse **cùng một** core strategy function."

**Current Behavior:** `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả, do trang tĩnh
không chạy được Python. `webapp/README.md` thừa nhận công khai.

**Evidence (E1, chạy thật tại S000):** parity OSCORE 40 ngày, lệch tối đa **7,39e-11** — hai bản
đồng thuận **ở đại lượng được kiểm**. Nhưng parity **chỉ so OSCORE tổng**; không phủ unlock,
spacing, phân bổ ladder, invalidation price, regime.

**Risk:** Mỗi tính năng port thêm sang JS mở rộng bề mặt trôi lệch nhanh hơn khả năng phát hiện.
Xác nhận RSK-002.

**Recommended Fix:** mở rộng phạm vi parity **trước** khi port thêm bất kỳ tính năng nào sang JS.
**Suggested Task:** R-06 · **Dependencies:** chặn trước T-10, T-11

---

# MEDIUM

| ID | Finding | Evidence | Vị trí | Vi phạm |
|---|---|---|---|---|
| F-009 | `sensitivity_manifest_hash` **không bao giờ** được ghi vào run record — không lời gọi `save_run` nào truyền `manifest_hash=`, kể cả run GATE2/GATE3. Không truy được run nào dùng manifest nào | **E1** | `reporting.py:43`, `pipeline.py:86,119,162,179,211` | BT §20, DM §12 |
| F-010 | `simulation_seed` và `code_commit` thiếu hoàn toàn trong run record | **E1** | `reporting.py:37-51` | BT §20, DM §12 |
| F-011 | `created_at` thiếu ở cả `StrategyConfig` và `ExecutionConfig` | **E1** | `config.py:41-67,106-138` | DM §2, §3 |
| F-012 | Bảng coverage weight không được sinh trong báo cáo dù §4 ghi "bắt buộc trong mọi báo cáo official"; hàm `coverage_table` đúng và có test nhưng không được gọi | **E1** | `windows.py:52`, `pipeline.py` | BT §4, §4.1 |
| F-013 | XIRR / money-weighted return không được tính; hàm `xirr` không được gọi | **E1** | `metrics.py:92`, `pipeline.py` | BT §16 |
| F-014 | Block bootstrap chạy `n_sims=200` **kể cả trong official run**, spec yêu cầu **1000 mỗi block length**. Mặc định của hàm là 1000 nhưng pipeline ghi đè | **E1** | `pipeline.py:74-75` vs `bootstrap.py:33` | BT §13 |
| F-015 | Ngưỡng số của FS-02 (`>0.5`), FS-07 (`cash>0.30 và AE<102`), FS-12 (`>0.80`) do triển khai **tự đặt**, không có trong spec và **không được ghi ở `docs/CONVENTIONS.md`**. Chúng trực tiếp quyết định verdict | **E1** | `failure_signals.py:47,64,78` | BT §17 |
| F-016 | FS-03 và FS-07 chỉ tính trên **một window đại diện (W5)**, không trên toàn mẫu — quy ước không được ghi ở đâu | **E1** | `pipeline.py:72-77` | BT §16, §17 |
| F-017 | Control F gộp **toàn bộ vốn của tháng vào một lệnh** tại thời điểm ngẫu nhiên, không giữ "kích thước tranche và profile giải ngân theo tháng" như §12 yêu cầu. Control G tự khai là xấp xỉ. Cả hai nuôi FS-08 | E0 | `benchmarks.py:193-245` | BT §12 |
| F-018 | Processing order: bước **15/16/17 không tách riêng** — fill, cập nhật ledger và cooldown nằm trong khối bước 12; tạo ladder chèn giữa bước 12 và 13 nên ladder mới tham gia trigger ngay trong cùng nến, và fill xảy ra **trước** khi vốn khả dụng được đọc để tạo ladder | E0 | `engine.py:426-484` | BT §19 |
| F-019 | **Không có test nào kiểm thứ tự 18 bước**, dù BT §19 ghi tường minh "Mọi implementation phải tuân thủ đúng thứ tự và **unit-test được thứ tự đó**" | **E1** | `tests/` | BT §19 |
| F-020 | Partial fill không được cài trong engine: `filled_vnd` khai báo nhưng **không bao giờ được gán**; trạng thái `PARTIALLY_FILLED` không bao giờ phát sinh. Engine luôn fill toàn phần | **E1** | `ladders.py:48`, `engine.py:431-441` | ST §8, DM §14, BT §21.2 |
| F-021 | Snapshot eligible capital của Crash ladder dùng `opportunity_reservable(...)` — hàm này **áp thêm daily limit 20%**. [F5] định nghĩa snapshot theo Smart AVAILABLE + Opportunity AVAILABLE, không nhắc daily limit. Eligible bị thu nhỏ so với spec | E0 | `engine.py:379-382` | ST §14 [F5] |
| F-022 | Regime exit dựa trên **dữ liệu thiếu**: `return7d=None`/`return24h=None` bị ép về `0.0`, thoả điều kiện exit. Chạy thật cho CRASH → RECOVERY với toàn bộ đầu vào `None`. Dữ liệu xấu đẩy trạng thái theo hướng có lợi cho strategy | **E1** | `regime.py:23-24` | BT §1, ST §3 |
| F-023 | Định nghĩa INVALID hẹp hơn spec: code chỉ đặt INVALID khi **cả 8** sub-factor thiếu; spec nói INVALID khi "giá/lịch sử ETH **hoặc indicator bắt buộc** không hợp lệ" | **E1** | `score.py:69-71` | ST §3 |
| F-024 | `decision_log` chỉ ghi khi `log_decisions=True` và chỉ 3 loại sự kiện (invalidation, crash entry, cooldown override); thiếu `previous_state/new_state`, `available/reserved/deployed` snapshot, `strategy_config_hash` | E0 | `engine.py:152-154` | ST §20, DM §11 |
| F-025 | Tag `EXECUTION_DATA_GAP` cho nến 15m thiếu không tồn tại trong `src/` | **E1** | — | BT §18 |
| F-026 | `verdict.py` ghi ánh xạ gate-fail→verdict là "quy ước, ghi ở `docs/CONVENTIONS.md`", nhưng **CONVENTIONS.md không có mục nào về verdict** | **E1** | `verdict.py:4-5` vs `docs/CONVENTIONS.md` | Doc integrity |
| F-027 | Bộ test webapp không chạy được từ bản checkout sạch: cần `app_final.html` (phải build) và `demo/results3/live_seed.json` (**không tồn tại trong repo**) | **E1** (S000) | `webapp/test_*.js` | Xác nhận RSK-004 |

# LOW

| ID | Finding | Evidence | Vị trí |
|---|---|---|---|
| F-028 | `Ladder.expires_at` của Smart ladder đặt `ts + 31 ngày`, không phải cuối accounting month. Trường này **không được dùng** (expiry do engine xử lý riêng ở dòng 270/359) nên không gây hậu quả hành vi, nhưng là dữ liệu sai nghĩa nếu ai đó đọc record | E0 | `engine.py:458` |
| F-029 | `ladder_completed()` coi `PARTIALLY_FILLED` là trạng thái kết thúc, mâu thuẫn ST §8 (phần chưa fill còn RESERVED tới hết TTL). Hàm hiện **không được engine gọi** nên chưa gây hậu quả | E0 | `ladders.py:137-139` |
| F-030 | Crash zone luôn gắn `pool="OPPORTUNITY"` kể cả khi vốn lấy một phần từ SMART → tie-break §15.1 xếp sai nhóm pool | E0 | `ladders.py:104,110`, `engine.py:388-404` |
| F-031 | Bộ đếm cooldown override đếm theo **zone** được tạo action, không theo **sự kiện** override | E0 | `engine.py:519-521` |
| F-032 | `DELAYED_DATA_FILL` chỉ là bộ đếm; không gắn tag lên purchase record như BT §18 mô tả | E0 | `engine.py:274,341-346` |
| F-033 | Base execute sớm không mang nhãn `EXECUTED_EARLY` (ST §9 yêu cầu "phải đánh dấu"); chỉ dùng reason `BASE_ADVANCE_SCORE`. Hành vi "không lặp lại ngày gốc" thì đúng | E0 | `engine.py:361-366` |
| F-034 | `_noon_candles` chứa nhánh `pass` không tác dụng (dead code); hàm cũng không được dùng | E0 | `benchmarks.py:29-41` |

# INFO / SPEC DEFECT — không phải lỗi implementation

## S-001 — Mâu thuẫn nội tại của spec về `score_weights`

Backtest §9 (precedence **1**) liệt kê `score weights (PL/MS/RV)` là **một trong tám chiều bắt
buộc của Gate 2**, với năm tuple đăng ký trước. Nhưng Strategy §21 (precedence 2) không có field
này trong bảng baseline, và Data Model §2 + Section Inventory XC-1 (precedence 3) quy định
**[F7]**: schema chỉ được có thêm **đúng ba** field metadata `config_name`, `created_at`,
`strategy_config_hash`.

Không thể đồng thời: sinh manifest Gate 2 đúng 19 ứng viên OFAT **cần** một field `score_weights`,
nhưng [F7] cấm mọi field ngoài ba metadata.

Implementation chọn thêm field `score_weights` (`config.py:65`) và tự ghi chú mâu thuẫn ở dòng
63-64. Theo Master Index §2, Backtest thắng, nên lựa chọn của code là **đúng precedence** — nhưng
nó vi phạm chữ của [F7]/XC-1.

**Đây là lỗi đặc tả, không phải lỗi code.** Sửa spec thuộc thẩm quyền chủ dự án và, theo Master
Index §6, phải đi qua V2.2 chứ không vá tại chỗ V2.1.5. Ghi nhận, không tự xử lý.

## S-002 — AE bỏ qua tiền mặt chưa đầu tư, trong khi §12.1 yêu cầu tính

Backtest §10.2 định nghĩa `AccumulationEfficiency` là **tỷ số ETH**. Backtest §12.1 lại yêu cầu
"Tiền mặt chưa đầu tư (USDT hoặc VND) vẫn là một phần của portfolio và không được bỏ qua khi tính
giá trị." Benchmark C và D giữ reserve (`final_reserve` được trả về nhưng không dùng), Benchmark B
có thể không tiêu hết trong tháng ít Thứ Hai. So sánh thuần ETH vì vậy có lợi cho chiến lược tiêu
hết vốn. Căng thẳng nội tại của spec; code làm đúng §10.2. Ghi nhận để chủ dự án quyết.

## S-003 — Ngữ nghĩa "có hysteresis" của mode NO_HWM không rõ

Strategy §6 mô tả NO_HWM: "Smart available bám theo SMART_UNLOCK hiện tại theo lifecycle bình
thường, **có hysteresis**, không mang peak qua ngày." Nhưng §5 chỉ định nghĩa hysteresis cho
Opportunity (68/62). Không rõ hysteresis nào áp cho Smart. Code trả thẳng `current_unlock`
(`capital.py:108-109`). Điểm spec để ngỏ; cần làm rõ ở V2.2.

---

# Nghi vấn chưa kiểm chứng (giữ nguyên E0 — KHÔNG được coi là kết luận)

Ba nghi vấn webapp kế thừa từ S000 (RSK-003). Chứng minh chúng đòi **dựng ca kiểm thử mới**, mà
quy tắc S001 số 10 cấm viết test mới trong phiên này. Vì vậy chúng **vẫn ở mức E0** và được
chuyển thành verification task.

| ID | Nghi vấn | Vị trí | Mức | Verification task |
|---|---|---|---|---|
| V-01 | Release vốn có thể trả **nhầm pool** khi có nhiều tháng: hàm chọn tháng hiện hành trả về tháng có key lớn nhất, không phải tháng của ladder | `webapp/app_logic.js:124-127,315-320` | **E0** | V-01 |
| V-02 | Mức unlock **không giới hạn** số vốn được reserve; `reserveFor` chỉ kiểm available | `webapp/app_logic.js:289-297` | **E0** | V-02 |
| V-03 | Trạng thái dữ liệu INVALID **không chặn** tạo ladder mới | `webapp/app_logic.js:324-335` | **E0** | V-03 |

**Đã thu hẹp được một phần (E1, S000):** `webapp/test_zone.js` chạy thật cho thấy bất biến
`TOTAL = A + R + D` **giữ đúng trong kịch bản một tháng** (bảo toàn 3.000.000 qua fill toàn phần
→ fill một phần → invalidation → release, không pool nào âm). Điều này **không bác bỏ** V-01 vì
V-01 nói về kịch bản **đa tháng** — đúng vào điểm mù của test hiện có.

---

# Requirement của spec CHƯA CÓ TEST

Backtest §21 liệt kê bộ test bắt buộc. Các mục sau **không có test nào tương ứng** (`NOT TESTED`
— nhắc lại: khác `FAIL`):

**§21.2 — Capital và ladder**
- Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và Day 28
- Partial fill giữ phần dư ở RESERVED tới hết TTL *(không thể test — chưa cài, xem F-020)*
- Không double reservation giữa Smart / Opportunity / Crash *(ở tầng engine)*
- Expiry: Smart cuối tháng, Crash suspend rồi cancel sau 72h Recovery *(chính là F-001)*
- Crash eligible-capital snapshot [F5] đo **sau** cancel/release *(ở tầng engine)*

**§21.3 — Execution và regime**
- Một, hai và ba zone bị xuyên trong cùng một nến
- Giới hạn tối đa hai zone mỗi cycle
- Thứ tự tie-break theo §15.1 **[F2]**
- Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW *(tầng engine)*
- Proxy ban đêm tại 07:00 local; TTL; action MISSED
- Crash funding unavailable scenario
- Cooldown và override, gồm tần suất override trong CRASH
- Chuyển Opportunity ladder sang Crash ladder không tạo double reservation
- Nhãn STRESSED **[F1]**: "không có hiệu ứng execution" *(chính là F-001)*

**§21.4 — Accounting và evaluation**
- Data gap và delayed Base fill
- Benchmark C: mỗi trigger bắn tối đa một lần mỗi chu kỳ, chu kỳ reset đúng luật **[F4]**
- VND → USDT, weighted USDT cost basis, dual cost basis *(NOT APPLICABLE theo [F6])*

**§19 — Processing order**
- Không có test nào kiểm thứ tự 18 bước, dù spec yêu cầu tường minh

---

# Code tồn tại nhưng KHÔNG truy được về requirement V2.1.5

| Code | Nhận định |
|---|---|
| `src/eth_dca_os/live_export.py` (95 dòng) | Sinh seed cho app web. Không phục vụ điều khoản nào của bộ backtest V2.1.5; phục vụ app — mà app đang nằm sau cổng verdict IM §9 chưa mở. Không phải lỗi, nhưng cần ghi nhận là code phục vụ giai đoạn chưa được mở khoá |
| `random_anchor_control(..., shift_days=10)` | Tham số `shift_days` và ngữ nghĩa "dịch ±10 ngày" không có trong spec — là quy ước tự đặt, không được ghi ở CONVENTIONS |
| Ngưỡng FS-02/FS-07/FS-12 | Xem F-015 — hằng số tự đặt, không truy được về spec |
| `benchmarks._noon_candles` | Dead code, không được gọi (F-034) |

**Không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với V2.1.5.** Bảy sửa đổi
F1–F7 đều có dấu vết hiện thực: [F1] nhãn STRESSED có mặt (dù có lỗi hiệu ứng — F-001),
[F2] tie-break ba tầng có mặt, [F3] delayed data fill có bộ đếm, [F4] ngữ nghĩa chu kỳ Benchmark C
có mặt, [F5] snapshot bất biến có mặt, [F6] đơn vị danh nghĩa có mặt, [F7] được xử lý một phần
(xem S-001). Không có **regression kế thừa** nào được phát hiện.

---

# Đề xuất remediation task cho phase sau — CHƯA THỰC HIỆN

Thứ tự đề xuất theo rủi ro và phụ thuộc. Routing sẽ được tính bằng `routing_engine.py` tại T-04,
**không chọn tay ở đây**.

| ID | Nội dung | Đóng finding | Ghi chú thứ tự |
|---|---|---|---|
| V-01/02/03 | Dựng ca kiểm thử cho ba nghi vấn webapp | RSK-003 | Làm sớm — chỉ cần test, chưa sửa code |
| R-04 | Ghi `source` thật vào lineage; `official` phụ thuộc nguồn dữ liệu | F-005 | **Trước T-06** |
| T-06A | Ghim thư viện + ghi môi trường vào run record | F-007 (RSK-006) | **Trước T-06**, đã có trong roadmap |
| R-02 | Đấu nối FS-02/06/12; chính sách verdict khi FS UNKNOWN | F-002 | **Trước T-06** |
| R-03 | Đấu nối Benchmark B/C/D, ablation §2.3, volume z-score §2.4, coverage table §4, XIRR; sửa bootstrap về 1000 | F-003, F-004, F-012, F-013, F-014 | **Trước T-06** |
| R-01 | Sửa vòng đời Crash ladder khi Recovery kết thúc vào STRESSED | F-001 | Trước T-06 |
| R-07 | Ghi `manifest_hash`, `simulation_seed`, `code_commit`, `created_at` vào record/config | F-009, F-010, F-011 | Trước T-06 |
| R-08 | Regime không được exit dựa trên dữ liệu thiếu; làm chặt định nghĩa INVALID | F-022, F-023 | Trước T-06 |
| R-09 | Bổ sung test cho các requirement §19/§21 chưa có test | F-019 + danh sách "chưa có test" | Song song |
| R-05 | Quyết định phạm vi Execution State machine (cần ADR) | F-006 | Cần quyết định của chủ dự án |
| R-06 | Mở rộng phạm vi parity JS ↔ Python | F-008 (RSK-002) | **Trước T-10/T-11** |
| R-10 | Ghi các quy ước chưa được ghi vào `docs/CONVENTIONS.md` (ánh xạ verdict, ngưỡng FS, phạm vi W5, shift_days) | F-015, F-016, F-026 | Rẻ, làm sớm |
| R-11 | Nhóm LOW: expires_at, ladder_completed, pool label Crash, các tag còn thiếu | F-028…F-034 | Sau cùng |
| — | Đưa S-001, S-002, S-003 vào đề xuất V2.2 | S-001…S-003 | **Không vá V2.1.5** (Master Index §6) |

**Một nhận định về thứ tự:** bảy task được đánh dấu "trước T-06" đều nằm trên đường đi tới
verdict. Chạy official run trước khi đóng chúng sẽ tạo ra một verdict **thiếu benchmark so sánh,
thiếu chẩn đoán bắt buộc, thiếu ba failure signal, không truy được manifest, không tái lập được
theo thời gian, và không phân biệt được với dữ liệu tổng hợp**. Theo Master Index §6, official run
không được chạy lại để "làm đẹp" kết quả, nên chất lượng của lần chạy đầu tiên rất đáng giá.
Đây là khuyến nghị; quyết định là của chủ dự án.
