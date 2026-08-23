# ROADMAP CHANGE PROPOSAL — RCP-001

Ngày: 2026-08-23
Nguồn: kết quả S001 (đã được chủ dự án chấp nhận ở trạng thái **S001 PASS WITH FINDINGS**)
Trạng thái: **CHƯA ÁP DỤNG — CHỜ PHÊ DUYỆT**

Theo `governance/core/00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule", tài liệu này
trình bày thay đổi lộ trình trước khi thực hiện. Bảng roadmap chuẩn trong
`PROJECT/PROJECT_PROGRESS.md` **chưa bị sửa**, và `PROJECT/LO_TRINH_DE_HIEU.md` vì thế vẫn đồng bộ
với nó. Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`.

---

## Reason

S001 sinh 33 finding, 14 đề xuất R/V, và 3 rủi ro mới. Lộ trình hiện tại (14 task) được lập ở
S000 **trước khi** có bất kỳ bằng chứng compliance nào, nên nó không phản ánh:

1. Việc official run hiện sẽ tạo ra một verdict **thiếu benchmark so sánh, thiếu chẩn đoán bắt
   buộc, thiếu ba failure signal, không truy được manifest, không tái lập được theo thời gian,
   và không phân biệt được với dữ liệu tổng hợp**.
2. Việc `T-06A` (ghim thư viện) chỉ đóng **một** trong năm lỗ hổng provenance.
3. Việc `T-09A` giả định ba lỗi webapp là có thật, trong khi chúng vẫn ở mức E0 chưa kiểm chứng.

Master Index §6 cấm chạy lại official run để làm đẹp kết quả. Vì vậy chất lượng của lần chạy đầu
tiên là không thể làm lại — đó là lý do trọng tâm của đề xuất này.

---

# 1. OLD ROADMAP

14 task, 6 phase (trạng thái tại thời điểm lập đề xuất):

| Status | ID | Tên | Tier/Effort |
|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | C/xhigh |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | C/xhigh |
| DONE | T-02 | Đối chiếu engine Python với spec | C/xhigh |
| **BLOCKED** | T-03 | Soát app web và rủi ro mất dữ liệu | C/high |
| PLANNED | T-04 | Chốt lộ trình và đóng băng tiêu chí | C/xhigh |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | DUYET |
| PLANNED | T-06A | Ghim phiên bản thư viện | B/high |
| PLANNED | T-06 | Chạy backtest chính thức | C/xhigh |
| PLANNED | T-07 | DUYỆT — đọc verdict | DUYET |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | C/xhigh |
| PLANNED | T-09A | Sửa lỗi kế toán trong app web | C/high |
| PLANNED | T-09B | Dựng lưu trữ dữ liệu bền | D/xhigh |
| PLANNED | T-10 | Triển khai lớp cảnh báo | C/xhigh |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | D/max |

**Đường găng cũ:** T-04 → T-05 → T-06A → T-06 → T-07 → T-11

---

# 2. FINDINGS S001 — PHÂN TÍCH NGUYÊN NHÂN GỐC

Không gom một finding thành một task. Gom theo **nguyên nhân gốc chung** hoặc **vùng
implementation chung**, vì sửa chúng cùng lúc rẻ hơn và có chung một câu chuyện kiểm chứng.

| Nguyên nhân gốc | Finding | Vùng code |
|---|---|---|
| **RC-1 — Pipeline không đấu nối hạng mục đã cài đặt** | F-003, F-004, F-012, F-013, F-014 | `pipeline.py`, `diagnostics.py`, `reporting.py` |
| **RC-2 — Provenance và tái lập của run record** | F-005, F-007, F-009, F-010, F-011 | `reporting.py`, `config.py`, `data/dataset.py`, `pyproject.toml` |
| **RC-3 — Mô hình hoá trạng thái regime và vòng đời ladder** | F-001, F-021, F-022, F-030 | `regime.py`, `engine.py`, `ladders.py` |
| **RC-4 — Ngữ nghĩa dữ liệu xấu và data gap** | F-023, F-025, F-032 | `score.py`, `engine.py` |
| **RC-5 — Failure signal: đo lường và chính sách** | F-002, F-015, F-016, F-017, F-026 | `pipeline.py`, `failure_signals.py`, `verdict.py`, `benchmarks.py` |
| **RC-6 — Thứ tự xử lý và độ phủ test** | F-018, F-019 + danh sách §21 chưa có test | `engine.py`, `tests/` |
| **RC-7 — Trạng thái thực thi và audit trail** | F-006, F-024, F-033 | `engine.py` (chưa có mô hình) |
| **RC-8 — Niềm tin vào app web** | F-008, F-020, F-027, V-01, V-02, V-03 | `webapp/`, `live_export.py` |
| **RC-9 — Nợ không ảnh hưởng hành vi** | F-028, F-029, F-031, F-034 | rải rác |
| **RC-10 — Khiếm khuyết đặc tả** | S-001, S-002, S-003 | `docs/spec/` — **không vá V2.1.5** |

**Nhận xét quan trọng về RC-5:** finding F-002 **trải trên hai lớp**. Phần *đo lường*
(instrumentation để sinh `opportunity_cap_hit_share`, `regime_advantage_share`, và tính
FS-03/FS-07 trên toàn bộ window thay vì chỉ W5) cần dữ liệu **tại thời điểm chạy** → không thể
làm sau. Phần *chính sách* (UNKNOWN có chặn BUILD không, ngưỡng nào hợp lệ) đọc lại được từ
kết quả đã lưu qua lệnh `ethdca verdict` → làm sau được. Đề xuất tách thành hai gói ở hai lớp
khác nhau, thay vì giả vờ nó là một khối nguyên tử.

---

# 3. PROPOSED CHANGES — 15 WORK PACKAGE

## Tiêu chí phân lớp

Phân lớp theo **dependency và ảnh hưởng thực tế**, không theo severity. Câu hỏi phân lớp:

| Lớp | Câu hỏi quyết định |
|---|---|
| **A — MUST FIX BEFORE OFFICIAL RUN** | *Nếu chạy official mà chưa sửa, lần chạy đó có bị hỏng không thể cứu không?* Áp dụng khi dữ liệu cần thiết chỉ sinh ra tại thời điểm chạy, hoặc khi kết quả mô phỏng bị sai lệch |
| **B — MUST FIX BEFORE VERDICT** | *Có tính lại được từ kết quả đã lưu không?* Nếu có, và nó ảnh hưởng tới độ tin cậy của verdict → lớp B. `ethdca verdict` đọc lại được `pipeline_state.json` nên nhiều thứ thuộc lớp này |
| **C — MUST FIX BEFORE PRODUCTIZATION** | Không ảnh hưởng kết quả backtest, nhưng chặn việc đưa công cụ vào dùng thật |
| **D — DEFERRED / OPTIONAL** | Không ảnh hưởng hành vi, hoặc thuộc thẩm quyền spec (V2.2) |

**Hệ quả của tiêu chí này:** không phải HIGH nào cũng vào lớp A. F-006 (HIGH) vào lớp C vì nó
không đổi kết quả backtest. F-008 (HIGH) vào lớp C vì nó chỉ chặn productization. Ngược lại
F-023 (MEDIUM) vào lớp A vì nó đổi hành vi engine trên dữ liệu thật có gap.

## LỚP A — MUST FIX BEFORE OFFICIAL RUN

### WP-A1 — Provenance và tái lập của official run
Đóng: **F-005, F-007, F-009, F-010, F-011** · Xác nhận RSK-006, RSK-008
**Thay thế T-06A** (T-06A chỉ đóng F-007, tức 1/5 lỗ hổng).

Nội dung: ghi `source` thật vào lineage; `official` chỉ đúng khi nguồn dữ liệu hợp lệ; ghim
thư viện; bổ sung trường còn thiếu vào run record và config schema.

Trường bắt buộc của official run record (theo yêu cầu 9 của chủ dự án, đối chiếu hiện trạng):

| Trường | Hiện trạng |
|---|---|
| `dataset_hash` | ✅ đã có |
| `strategy_config_hash` | ✅ đã có |
| `execution_config_hash` | ✅ đã có |
| `master_seed` | ✅ đã có |
| `sensitivity_manifest_hash` | ⚠️ trường có nhưng **không bao giờ được ghi** (F-009) |
| `simulation_seed` | ❌ thiếu (F-010) |
| `code_commit` (git SHA) | ❌ thiếu (F-010) |
| `python_version` | ❌ thiếu |
| `dependency_lock_hash` | ❌ thiếu |
| `dataset_source` / `dataset_is_synthetic` | ❌ thiếu (F-005) |
| `created_at` trong strategy/execution config | ❌ thiếu (F-011) |

**Verification criteria (đáp yêu cầu 8 — provenance không thể giả mạo bằng flag):**
- Chạy `ethdca synth` rồi `ethdca run all` **không dev-limit** phải cho `official: false`.
- Không tồn tại tham số CLI hay biến môi trường nào ép `official: true` khi nguồn dữ liệu là
  synthetic. Cờ `official` phải là **hàm dẫn xuất** từ lineage đã verify checksum, không phải
  một trường có thể đặt tay.
- `lineage.json` phân biệt được `binance_bulk_archive` / `binance_rest` / `synthetic`.
- Dựng lại môi trường từ lockfile và tái lập một run cho kết quả trùng khớp bit-for-bit.

### WP-A2 — Đấu nối hạng mục bắt buộc vào pipeline
Đóng: **F-003, F-004, F-012, F-013, F-014** · Xác nhận RSK-007

Toàn bộ là "code đã đúng, chỉ thiếu lời gọi": Benchmark B/C/D, ablation §2.3, volume z-score
§2.4, bảng coverage §4, XIRR §16, và bootstrap về đúng 1000/block length.

**Ghi chú phân lớp trung thực:** chỉ **F-004** bị ràng buộc cứng vào lớp A (Strategy §2 ghi
"bắt buộc trong mọi official run") và **F-014** (bootstrap cần purchase record tại thời điểm
chạy, không được lưu lại). F-003, F-012, F-013 về lý thuyết tính lại được từ dataset đã đóng
băng. Đề xuất gộp cả năm vào lớp A vì chúng là **cùng một sửa đổi trong cùng một file**; tách ra
sẽ phải chạm `pipeline.py` hai lần cho cùng một mục đích. Chủ dự án có thể yêu cầu tách.

### WP-A3 — Mô hình hoá regime và vòng đời ladder
Đóng: **F-001, F-021, F-022, F-030** · Xác nhận RSK-009

Đây là gói duy nhất trong lớp A **làm đổi kết quả mô phỏng**. Nguyên nhân gốc chung: trạng thái
regime được mô hình hoá thiếu chính xác — nhãn dẫn xuất STRESSED bị gộp vào cùng trường với
trạng thái nền NORMAL/CRASH/RECOVERY, và dữ liệu thiếu bị ép về 0.

**Không đề xuất giải pháp cụ thể ở đây** — thiết kế thuộc phiên thực thi. Nhưng ràng buộc bắt
buộc: sau khi sửa, **[F1] phải đúng theo nghĩa đen** — STRESSED không được có bất kỳ hiệu ứng nào
lên unlock, ladder, cooldown, limit hay execution.

**Verification criteria:**
- Test chuỗi CRASH → RECOVERY → STRESSED khẳng định reserve của Crash zone về 0 sau 72h Recovery.
- Test khẳng định `Return7D`/`Return24H` thiếu **không** cho phép thoát CRASH.
- Test khẳng định snapshot [F5] đo theo AVAILABLE đã unlock, và daily limit áp ở khâu deployment
  chứ không thu nhỏ snapshot.

### WP-A4 — Ngữ nghĩa dữ liệu xấu và data gap
Đóng: **F-023, F-025, F-032**

Siết định nghĩa INVALID cho khớp Strategy §3 ("indicator **bắt buộc** không hợp lệ", không phải
"mất cả 8 sub-factor"); gắn tag `EXECUTION_DATA_GAP` và `DELAYED_DATA_FILL` lên bản ghi thay vì
chỉ đếm.

Vào lớp A vì dữ liệu Binance thật **có gap**, nên định nghĩa INVALID sai sẽ đổi hành vi engine
ngay trong official run.

### WP-A5 — Instrumentation cho failure signal
Đóng: phần **đo lường** của **F-002**, và **F-016**

Sinh `opportunity_cap_hit_share` (FS-02), `regime_advantage_share` (FS-12), `adjacent_config_flip`
(FS-06); và tính FS-03/FS-07 trên **toàn bộ chín window** thay vì chỉ W5.

Vào lớp A vì ba đại lượng này chỉ sinh ra được khi engine đang chạy.
Phụ thuộc **WP-A3**: nếu vốn còn bị khoá do F-001 thì FS-02 và FS-07 đo ra số sai lệch.

### WP-A6 — Đóng thứ tự xử lý 18 bước
Đóng: **F-018, F-019**

Trình tự bắt buộc: **viết test thứ tự trước** (F-019 — spec §19 yêu cầu tường minh "phải
unit-test được thứ tự đó"), rồi mới xác định sai lệch hiện tại (bước 15/16/17 bị gộp vào bước 12;
tạo ladder chèn giữa bước 12 và 13) có làm đổi kết quả hay không, rồi mới quyết định sửa hay ghi
nhận là chấp nhận được.

Vào lớp A vì nó quyết định **official run đại diện cho thuật toán nào**.
Phụ thuộc WP-A3, WP-A4 để test khoá đúng hành vi cuối cùng.

## LỚP B — MUST FIX BEFORE VERDICT

### WP-B1 — Chính sách verdict, ngưỡng failure signal và stopping rule
Đóng: phần **chính sách** của **F-002**, **F-015**, **F-017**, **F-026** · Xác nhận RSK-005

**Verification criteria bắt buộc (đáp yêu cầu 7 của chủ dự án):**

> **BUILD không được phép nếu bất kỳ REQUIRED Failure Signal nào vẫn UNKNOWN.**

Cụ thể hoá: Backtest §17 liệt kê FS-01…FS-12 mà không đánh dấu mục nào là tuỳ chọn, nên
**cả 12 đều REQUIRED**. Test phải dựng một tập FS trong đó đúng một signal là `None` và khẳng
định verdict trả về **không phải** `BUILD`, đồng thời `can_proceed_to_app` là `false`.

Ngoài ra: phê chuẩn hoặc thay thế các ngưỡng số hiện do triển khai tự đặt (FS-02 `>0.5`,
FS-07 `cash>0.30 và AE<102`, FS-12 `>0.80`); sửa Control F giữ đúng profile tranche theo tháng
(F-017); và ghi ánh xạ gate-fail → verdict vào `docs/CONVENTIONS.md` cho khớp với chính docstring
của `verdict.py`.

Ở lớp B vì `ethdca verdict` đọc lại được kết quả đã lưu, nên chính sách sửa được sau khi chạy.
**Ngoại lệ cần lưu ý:** F-017 (Control F) cần **chạy lại Gate 1** — rẻ, không cần chạy lại
Gate 2/3. Nếu chủ dự án muốn tuyệt đối không chạy lại bất cứ thứ gì, hãy chuyển F-017 lên lớp A.

### WP-B2 — Bổ sung test cho requirement §21 còn thiếu
Đóng: đề xuất **R-09** và toàn bộ danh sách "requirement chưa có test" của S001

Trọng tâm: §21.3 hiện gần như trống — tie-break [F2], max_zones, cooldown và override, TTL/MISSED,
crash funding unavailable, proxy đêm 07:00, "STRESSED không có hiệu ứng execution"; cộng §21.4
[F4] Benchmark C và data gap.

### WP-B3 — Audit trail decision_log
Đóng: **F-024, F-033**

`decision_log` đầy đủ theo Data Model §11 và nhãn `EXECUTED_EARLY` theo Strategy §9.
Phụ thuộc **WP-C2** về mặt ngữ nghĩa (`previous_state`/`new_state` cần Execution State enum) —
xem ghi chú phụ thuộc chéo ở §4.

## LỚP C — MUST FIX BEFORE PRODUCTIZATION

### WP-C1 — Xác minh ba nghi vấn webapp và khôi phục harness test
Đóng: **V-01, V-02, V-03, F-027** · Xác nhận/bác bỏ RSK-003, xác nhận RSK-004
**Gỡ BLOCKED cho T-03** (đáp yêu cầu 10 — đưa verification vào phase phù hợp, **không hạ
Completion Gate của T-03**).

Nội dung: khôi phục để test webapp chạy được từ bản checkout sạch (hiện thiếu `app_final.html`
và `demo/results3/live_seed.json`), rồi dựng ca kiểm thử cho ba nghi vấn.

> **Đề nghị ưu tiên cao nhất trong lớp C, và có thể khởi động ngay song song với lớp A.**
> Lý do không nằm ở đường găng kỹ thuật mà ở an toàn: nếu chủ dự án đang dùng app để ghi giao
> dịch tiền thật, ba nghi vấn này — nếu đúng — đang làm sai sổ vốn **ngay lúc này**. Gói này
> không đụng `src/`, không cần dữ liệu Binance, không phụ thuộc gói nào khác.

### WP-C2 — Execution State machine, tiếp cận behavior-first
Đóng: **F-006**

**Kết quả xác định hiện trạng (đáp yêu cầu 6 của chủ dự án).** S001 đã kiểm từng trạng thái.
Kết luận: **PHÂN TÁN, không phải hoàn toàn thiếu** — trừ một ngoại lệ.

| Trạng thái | Hiện trạng | Vị trí |
|---|---|---|
| `WAIT` | **Tồn tại ngầm** — không có candidate action. Không đặt tên, không lưu | — |
| `FUNDING_REQUIRED` | **THIẾU THẬT** như một trạng thái phân biệt được | — |
| `READY_TO_BUY` | **Tồn tại ngầm** — điều kiện `ts >= execute_at` | `engine.py:431` |
| `ACTION_PENDING` | **Tồn tại tường minh** nhưng ở `Zone.status`, không phải Execution State | `engine.py:235` |
| `COOLDOWN` | **Tồn tại** như biến cục bộ `in_cooldown`; hành vi được cưỡng chế đúng | `engine.py:422, 517` |
| `DATA_BLOCKED` | **Hành vi tồn tại** (chặn khi `dq == INVALID`) nhưng không được đặt tên/lưu | `engine.py:452, 506` |

Vì sao `FUNDING_REQUIRED` thiếu thật: Backtest §5 định nghĩa `funding_delay = 0 nếu USDT treasury
đã đủ`, nhưng engine **không mô hình hoá treasury USDT**, và `docs/CONVENTIONS.md` #8 chốt quy ước
"ON_DEMAND: mọi zone action đều cần funding". Nên nhánh điều kiện đó không bao giờ được thực thi.

**Hệ quả cho remediation — đây là điểm chủ dự án yêu cầu làm rõ:**
Phần lớn công việc là **đặt tên, hợp nhất và lưu vết hành vi đã có**, không phải viết logic mới.
Đề xuất KHÔNG tạo một class `StateMachine` chỉ để khớp tên trong spec. Việc cần quyết định trước
tiên là **phạm vi**: backtest có cần mô hình treasury USDT để `FUNDING_REQUIRED` có nghĩa không,
hay trạng thái đó chỉ thuộc tầng app? Câu hỏi này cần một **ADR**.

Vào lớp C vì đặt tên và lưu vết hành vi đã có **không làm đổi kết quả backtest**.

### WP-C3 — Partial fill ở tầng sản phẩm
Đóng: **F-020**

Ghi nhận quan trọng: trong backtest, fill xảy ra trọn vẹn tại execution proxy (Backtest §5), nên
partial fill **không phát sinh được** — đây là hiện tượng của tầng live (Product §8). Primitive
kế toán ở tầng `Pool` đã có và đã có test. Vì vậy đây là công việc **tầng sản phẩm**, không phải
lỗ hổng của backtest engine. Phụ thuộc WP-C2 (cần trạng thái).

### WP-C4 — Mở rộng phạm vi parity JS ↔ Python
Đóng: **F-008** · Xác nhận RSK-002

Parity hiện chỉ phủ **OSCORE tổng** (lệch 7,39e-11 — rất tốt ở đại lượng được kiểm), nhưng không
phủ unlock, spacing, phân bổ ladder, invalidation price, regime.

Phụ thuộc **WP-A3, WP-A4, WP-A6**: phải chốt hành vi Python trước, nếu không parity sẽ khoá vào
một hành vi sắp thay đổi. **Chặn T-10 và T-11.**

## LỚP D — DEFERRED / OPTIONAL

### WP-D1 — Nhóm nợ không ảnh hưởng hành vi
Đóng: **F-028, F-029, F-031, F-034**
`expires_at` của Smart ladder gây hiểu nhầm; `ladder_completed()` coi PARTIALLY_FILLED là kết
thúc (hiện không được gọi); bộ đếm cooldown override đếm theo zone; dead code `_noon_candles`.

### WP-D2 — Đề xuất V2.2 cho ba khiếm khuyết đặc tả
Đóng: **S-001, S-002, S-003**

S-001 là mâu thuẫn nội tại thật giữa Backtest §9 (precedence 1, yêu cầu `score_weights` là chiều
Gate 2) và Data Model §2 + XC-1 (precedence 3, [F7] cấm field ngoài ba metadata).
S-002: AE là tỷ số ETH nhưng §12.1 đòi tính cả tiền mặt chưa đầu tư.
S-003: mode NO_HWM "có hysteresis" — không rõ hysteresis nào.

**Master Index §6 cấm vá tại chỗ V2.1.5.** Gói này chỉ sinh *đề xuất*; mở V2.2 là quyết định của
chủ dự án và kéo theo nghĩa vụ chạy lại các gate bắt buộc.

---

# 4. DEPENDENCY GRAPH

```
                    T-04 (chốt lộ trình + đóng băng gate)
                      │  [phụ thuộc governance cho MỌI gói bên dưới]
                      │
      ┌───────────────┼────────────────────────────────┬──────────────────┐
      │               │                                │                  │
 ┌────▼────┐    ┌─────▼─────┐                    ┌─────▼─────┐      ┌─────▼─────┐
 │ WP-A1   │    │  WP-A2    │                    │  WP-A3    │      │  WP-C1    │
 │provenance│   │ đấu nối   │                    │regime &   │      │xác minh   │
 │(gồm A-7) │   │ pipeline  │                    │ladder     │      │webapp     │
 └────┬────┘    └─────┬─────┘                    └─────┬─────┘      └─────┬─────┘
      │               │                                │                  │
      │               └──────────┬─────────────────────┤             gỡ BLOCKED
      │                          │                     │              cho T-03
      │                    ┌─────▼─────┐         ┌─────▼─────┐
      │                    │  WP-A5    │         │  WP-A4    │
      │                    │instrument │         │dữ liệu xấu│
      │                    │   FS      │         └─────┬─────┘
      │                    └─────┬─────┘               │
      │                          │               ┌─────▼─────┐
      │                          │               │  WP-A6    │
      │                          │               │thứ tự 18  │
      │                          │               └─────┬─────┘
      └──────────────┬───────────┴─────────────────────┘
                     │
              ╔══════▼═══════════════════════╗
              ║  GATE-A — LỚP A HOÀN TẤT     ║
              ╚══════╤═══════════════════════╝
                     │            ┌──────────────────┐
                     │◄───────────┤ BLK-001 được gỡ  │  (chỉ tại đây)
                     │            │ dataset Binance  │
                     │            └──────────────────┘
              ┌──────▼──────┐
              │    T-06     │  official run
              └──────┬──────┘
                     │
       ┌─────────────┼─────────────┐
  ┌────▼────┐  ┌─────▼─────┐ ┌─────▼─────┐
  │ WP-B1   │  │  WP-B2    │ │  WP-B3    │
  │ verdict │  │ test §21  │ │audit trail│
  │ policy  │  └───────────┘ └─────┬─────┘
  └────┬────┘                      │ (ngữ nghĩa) ──► WP-C2
       │
╔══════▼═══════════════════════╗
║  GATE-B — LỚP B HOÀN TẤT     ║
╚══════╤═══════════════════════╝
       │
 ┌─────▼─────┐
 │   T-07    │  DUYỆT verdict
 └─────┬─────┘
       │
       │   ┌──────────────────────────────────────────┐
       │   │ T-05 DUYỆT phạm vi (DEC-005) — PENDING   │
       │   └───────┬──────────────────────────────────┘
       │           │
       │      ┌────▼────┐       ┌─────────┐      ┌─────────┐
       │      │  T-08   │       │ WP-C2   │      │ WP-C4   │
       │      │đặc tả   │       │Exec     │◄─────┤parity   │◄── WP-A3/A4/A6
       │      │cảnh báo │       │State    │      └────┬────┘
       │      └────┬────┘       └────┬────┘           │
       │           │            ┌────▼────┐           │
       │           │            │ WP-C3   │           │
       │           │            │partial  │           │
       │           │            │  fill   │           │
       │           │            └────┬────┘           │
       │      ┌────▼────┐            │                │
       │      │ T-09B   │            │                │
       │      │lưu trữ  │            │                │
       │      └────┬────┘            │                │
       │           │                 │                │
       │      ┌────▼─────────────────┴────────────────▼──┐
       │      │              T-10  lớp cảnh báo           │
       │      └───────────────────┬───────────────────────┘
       │                          │
       └──────────────────────────▼─────────┐
                            ┌───────────────▼──┐
                            │  T-11 (chỉ khi   │
                            │  verdict = BUILD)│
                            └──────────────────┘

WP-C1 ──► T-09A (chỉ thực hiện nếu nghi vấn được xác nhận)
WP-D1, WP-D2 — độc lập, không chặn gì
```

## Trả lời trực tiếp các câu hỏi phụ thuộc của chủ dự án

| Câu hỏi | Trả lời |
|---|---|
| **Finding nào phải sửa trước finding nào** | WP-A3 trước WP-A5 (vốn bị khoá làm sai số đo FS-02/FS-07). WP-A3, WP-A4 trước WP-A6 (test thứ tự phải khoá hành vi cuối). WP-A3/A4/A6 trước WP-C4 (không khoá parity vào hành vi sắp đổi). WP-C2 trước WP-C3 và trước phần ngữ nghĩa của WP-B3 |
| **Finding nào chạy song song được** | WP-A1 ∥ WP-A2 ∥ WP-A3 ∥ WP-C1 — bốn nhánh độc lập hoàn toàn. WP-B2 ∥ WP-B3. WP-D1 ∥ WP-D2 ∥ mọi thứ |
| **Finding nào chặn official backtest** | Toàn bộ lớp A: WP-A1…WP-A6 |
| **Finding nào chặn verdict** | Lớp B: WP-B1 (bắt buộc), WP-B2 và WP-B3 (khuyến nghị, xem §7) |
| **Finding nào chỉ chặn productization** | Lớp C: WP-C1, WP-C2, WP-C3, WP-C4 |
| **Finding nào defer được** | Lớp D: WP-D1, WP-D2 |
| **Xung đột file cần tuần tự hoá** | WP-A3 và WP-A4 đều sửa `engine.py` — **không có phụ thuộc logic** nhưng nên tuần tự để tránh xung đột merge. WP-A2 và WP-A5 đều sửa `pipeline.py` — tương tự |

## BLK-001 — vị trí chính xác trên đường găng (đáp yêu cầu 11)

**Không một work package nào trong WP-A1…WP-D2 cần dữ liệu Binance thật.** Toàn bộ 15 gói phát
triển và kiểm chứng được trên dữ liệu tổng hợp — việc này hợp lệ theo DEC-003, vốn chỉ cấm dùng
synthetic để **tạo verdict**, không cấm dùng để **phát triển và test**.

BLK-001 chỉ nằm trên đường găng tại **đúng một điểm: T-06**, nơi cần official dataset thật.

Hệ quả: **toàn bộ chương trình remediation có thể chạy trọn vẹn trong khi BLK-001 vẫn còn.**
Đây là thay đổi đáng kể so với cách hiểu ở S000, nơi BLK-001 được coi là chặn cả nhánh.

Không bypass BLK-001. Không đổi nguồn dữ liệu. Không dùng synthetic để tạo official verdict.

---

# 5. NEW CRITICAL PATH

**Đường găng cũ:** T-04 → T-05 → T-06A → T-06 → T-07 → T-11

**Đường găng mới:**

```
T-04 → WP-A3 → WP-A4 → WP-A6 → GATE-A → T-06 → WP-B1 → GATE-B → T-07 → T-11
         (D/max)  (C/xhigh) (D/max)        [cần BLK-001]  (D/max)
```

Nhánh song song không nằm trên đường găng: WP-A1, WP-A2 → WP-A5 (hội tụ tại GATE-A);
WP-C1 (độc lập hoàn toàn); WP-B2, WP-B3 (hội tụ tại GATE-B).

**Thay đổi quan trọng so với đường găng cũ:**

1. **T-05 (DUYỆT DEC-005) rời khỏi đường găng.** DEC-005 quyết định phạm vi *app*; toàn bộ lớp A
   là backtest engine. Lớp A khởi động được mà không cần chốt DEC-005. DEC-005 chỉ chặn nhánh
   T-08 → T-10 và nhánh lớp C.
2. **T-06A biến mất khỏi đường găng**, được hấp thụ vào WP-A1 — và WP-A1 cũng không nằm trên
   đường găng vì nó song song với nhánh engine.
3. **Đường găng dài thêm ba mắt xích**, trong đó hai mắt là D/Fable/max.

---

# 6. TASKS ADDED / CHANGED / REMOVED

## ADDED — 15 work package

| ID | Tên | Lớp | Đóng finding |
|---|---|---|---|
| WP-A1 | Provenance và tái lập của official run | A | F-005, F-007, F-009, F-010, F-011 |
| WP-A2 | Đấu nối hạng mục bắt buộc vào pipeline | A | F-003, F-004, F-012, F-013, F-014 |
| WP-A3 | Mô hình hoá regime và vòng đời ladder | A | F-001, F-021, F-022, F-030 |
| WP-A4 | Ngữ nghĩa dữ liệu xấu và data gap | A | F-023, F-025, F-032 |
| WP-A5 | Instrumentation cho failure signal | A | F-002 (đo lường), F-016 |
| WP-A6 | Đóng thứ tự xử lý 18 bước | A | F-018, F-019 |
| WP-B1 | Chính sách verdict và stopping rule | B | F-002 (chính sách), F-015, F-017, F-026 |
| WP-B2 | Bổ sung test §21 còn thiếu | B | R-09 |
| WP-B3 | Audit trail decision_log | B | F-024, F-033 |
| WP-C1 | Xác minh webapp và khôi phục harness | C | V-01, V-02, V-03, F-027 |
| WP-C2 | Execution State machine (behavior-first) | C | F-006 |
| WP-C3 | Partial fill ở tầng sản phẩm | C | F-020 |
| WP-C4 | Mở rộng parity JS ↔ Python | C | F-008 |
| WP-D1 | Nhóm nợ không ảnh hưởng hành vi | D | F-028, F-029, F-031, F-034 |
| WP-D2 | Đề xuất V2.2 cho ba khiếm khuyết đặc tả | D | S-001, S-002, S-003 |

## CHANGED — 5 task

| ID | Thay đổi |
|---|---|
| **T-03** | Giữ nguyên `BLOCKED`. **Không hạ Completion Gate.** Bổ sung ghi chú: CHECK-03-01 sẽ được thoả bởi **WP-C1**; T-03 chuyển `DONE` khi WP-C1 hoàn tất và ba nghi vấn có kết luận E1 |
| **T-06** | Phụ thuộc đổi từ `T-05 + T-06A` thành **`GATE-A (toàn bộ lớp A) + BLK-001 được gỡ`**. T-05 không còn là điều kiện |
| **T-07** | Phụ thuộc thêm **GATE-B (lớp B hoàn tất)** |
| **T-09A** | Phụ thuộc đổi thành **WP-C1**. Ghi chú: ba lỗi vẫn ở mức E0; nếu WP-C1 bác bỏ, T-09A có thể chuyển `CANCELLED` hoặc thu hẹp phạm vi. Task hiện đang giả định lỗi có thật — đó là giả định chưa được chứng minh |
| **T-10 / T-11** | T-10 phụ thuộc thêm **WP-C4**. T-11 phụ thuộc thêm **WP-C2, WP-C3, WP-C4** |

## REMOVED — 1 task

| ID | Lý do |
|---|---|
| **T-06A** | **Bị thay thế bởi WP-A1.** T-06A chỉ đóng F-007 (ghim thư viện) — một trong năm lỗ hổng provenance. Giữ cả hai sẽ tạo hai task chồng lấn trên cùng một file. Toàn bộ nội dung T-06A được bảo toàn bên trong WP-A1, và yêu cầu "T-06A phải nằm trước official run" của chủ dự án được giữ nguyên vì WP-A1 thuộc lớp A |

**Tổng lộ trình:** 14 task hiện tại + 15 thêm − 1 bỏ = **28 task**.

---

# 7. MODEL + EFFORT ĐỀ XUẤT

Toàn bộ tính bằng `governance/scripts/governance/routing_engine.py`. Không chọn tay.

| ID | D/R/B/A/X | U/V/H/C/F | Category | Tier | Model | Effort | Floor áp dụng |
|---|---|---|---|---|---|---|---|
| WP-A1 | 2/3/3/2/3 | 2/3/3/3/3 | — | C | Opus | xhigh | none |
| WP-A2 | 2/2/2/1/3 | 1/3/2/3/2 | — | B | Sonnet | high | none |
| WP-A3 | 4/4/3/3/3 | 3/4/4/3/4 | accounting_financial | **D** | **Fable** | **max** | cognitive A≥3&X≥3, cognitive D≥4&X≥3, safety min_C / safety min_high |
| WP-A4 | 3/3/2/3/2 | 2/3/2/2/3 | — | C | Opus | xhigh | none |
| WP-A5 | 3/3/2/3/3 | 3/3/3/3/3 | — | C | Opus | xhigh | cognitive A≥3&X≥3 |
| WP-A6 | 4/3/3/2/3 | 3/4/3/3/3 | — | **D** | **Fable** | **max** | cognitive D≥4&X≥3 |
| WP-B1 | 3/4/3/4/3 | 3/3/3/3/4 | accounting_financial | **D** | **Fable** | **max** | cognitive A≥3&X≥3, safety min_C / safety min_high |
| WP-B2 | 3/2/1/2/3 | 2/3/3/3/2 | — | C | Opus | xhigh | none |
| WP-B3 | 2/2/2/2/2 | 1/2/2/2/2 | — | C | Opus | high | none |
| WP-C1 | 2/3/2/1/2 | 2/3/2/2/3 | — | C | Opus | xhigh | none |
| WP-C2 | 3/2/3/3/3 | 3/2/3/3/2 | — | C | Opus | xhigh | cognitive A≥3&X≥3 |
| WP-C3 | 3/3/2/2/2 | 2/3/2/2/3 | accounting_financial | C | Opus | xhigh | safety min_C / safety min_high |
| WP-C4 | 3/3/2/2/3 | 2/4/3/3/3 | accounting_financial | C | Opus | xhigh | safety min_C / safety min_high |
| WP-D1 | 1/1/1/1/1 | 1/1/1/1/1 | — | B | Sonnet | medium | none |
| WP-D2 | 3/2/2/4/3 | 3/2/3/3/2 | — | C | Opus | xhigh | cognitive A≥3&X≥3 |

Phân bố: **3 × D/Fable/max**, 10 × C/Opus, 2 × B/Sonnet.

Ba gói D/Fable/max — WP-A3, WP-A6, WP-B1 — đều là gói **đổi hành vi lõi hoặc quyết định cổng
verdict**. Router đưa chúng lên Tier D qua cả điểm nền lẫn floor nhận thức, không phải do tôi
chọn.

## ⚠ Ghi nhận một sai lệch của chính công cụ routing

Khi tính WP-A2, router trả `model_score = 2.0` nhưng gán **Tier B**. Bảng trong
`AGENT_CAPABILITY_MATRIX.md` quy định `2.00–2.99 → Tier C`.

Nguyên nhân đã kiểm chứng: giá trị dấu phẩy động thật là `1.9999999999999998`, chỉ hiển thị
thành `2.0` sau khi làm tròn. `routing_engine.py:10` dùng so sánh `s < 2` nên rơi vào nhánh B.

```
giá trị float thật : 1.9999999999999998
hiển thị round(,3) : 2.0
bảng AGENT_CAPABILITY_MATRIX: 2.00-2.99 -> C
router tier_from_score  : B
```

Đây là **khiếm khuyết của công cụ governance**, không thuộc phạm vi S001 (S001 audit mã sản phẩm).
Hệ quả: một task nằm đúng biên có thể bị **under-route** một bậc. Tôi giữ nguyên kết quả router
vì `ROADMAP_SYNC_STANDARD.md` quy định router là thẩm quyền, nhưng nêu ra để chủ dự án quyết định:
chấp nhận B/Sonnet/high cho WP-A2, hay nâng lên C/Opus. Đề xuất bổ sung một finding riêng cho
công cụ governance ở phiên sau.

---

# 8. TÁC ĐỘNG TỚI TỔNG LỘ TRÌNH

| Khía cạnh | Trước | Sau |
|---|---|---|
| Số task | 14 | 28 |
| Task trên đường găng tới verdict | 5 (T-04→T-05→T-06A→T-06→T-07) | 8 (T-04→WP-A3→WP-A4→WP-A6→T-06→WP-B1→T-07) |
| Task Tier D | 2 (T-09B, T-11) | 5 (thêm WP-A3, WP-A6, WP-B1) |
| DEC-005 trên đường găng | Có | **Không** — chỉ chặn nhánh app |
| BLK-001 chặn | Cả nhánh official | **Đúng một điểm: T-06** |
| Công việc khởi động được ngay | T-04 | T-04, và sau đó **4 nhánh song song** |

**Điều gì đổi về bản chất:** lộ trình cũ coi official run là bước gần kề sau một task chuẩn bị.
Lộ trình mới đặt **sáu work package** giữa hiện tại và official run. Đó không phải vì thận trọng
quá mức, mà vì Master Index §6 cấm chạy lại official run để cải thiện kết quả — nên lần chạy đầu
tiên phải đúng ngay.

**Điều gì KHÔNG đổi:** mục tiêu cuối (công cụ web theo dõi + cảnh báo), thứ tự T-08 → T-10 cho
nhánh cảnh báo, và việc T-11 vẫn khoá sau verdict BUILD.

## Preview roadmap dễ hiểu (KHÔNG phải file sinh tự động)

Bảng dưới đây **chỉ để chủ dự án hình dung**. Nó **không** phải `PROJECT/LO_TRINH_DE_HIEU.md` và
không được chép tay vào đó. Nếu đề xuất được duyệt, file thật sẽ được sinh bằng
`sync_easy_roadmap.py` từ bảng chuẩn.

| Tick | Tên việc | Mục đích | Mức xử lý |
|---|---|---|---|
| ⬜ | WP-A1 — Chứng minh nguồn gốc và tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, không phải dữ liệu giả | C — Opus — xhigh |
| ⬜ | WP-A2 — Bật những phần đã viết nhưng chưa được chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có | B — Sonnet — high |
| ⬜ | WP-A3 — Sửa cách theo dõi trạng thái thị trường và vòng đời lệnh mua | Đang có lỗi khiến tiền bị khoá vĩnh viễn, không dùng lại được | D — Fable — max |
| ⬜ | WP-A4 — Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu thật có lỗ hổng; xử lý sai sẽ ra kết quả sai | C — Opus — xhigh |
| ⬜ | WP-A5 — Đo đủ các tín hiệu cảnh báo hỏng | Ba tín hiệu hiện không bao giờ được đo, nhưng vẫn kết luận như thể đã đo | C — Opus — xhigh |
| ⬜ | WP-A6 — Chốt đúng thứ tự các bước tính toán | Sai thứ tự nghĩa là con số chính thức không đại diện cho chiến lược đã đặc tả | D — Fable — max |
| ⬜ | WP-B1 — Chốt luật ra kết luận cuối | Không cho phép kết luận "làm đi" khi còn tín hiệu chưa được đo | D — Fable — max |
| ⬜ | WP-C1 — Kiểm chứng ba nghi ngờ ở app web | App đang ghi tiền thật; ba nghi ngờ chưa được chứng minh đúng hay sai | C — Opus — xhigh |

---

# 9. RISK CỦA CHÍNH ĐỀ XUẤT NÀY

| Rủi ro | Đánh giá |
|---|---|
| **Đề xuất quá nặng, làm chậm mục tiêu cuối** | Có thật. 15 gói là nhiều. Nhưng 6/15 nằm trước official run và lý do là điều khoản không thể lách của Master Index §6. Chủ dự án có thể chọn thu hẹp lớp A — xem "Phương án thay thế" |
| **WP-A3 ở Tier D/max có thể vượt ngân sách** | Router đưa ra con số này qua ba floor độc lập. Nếu muốn hạ, cách hợp lệ duy nhất là **thu hẹp phạm vi gói** rồi tính lại routing, không phải hạ tay |
| **Gộp gói có thể che mất một finding** | Mỗi gói liệt kê tường minh finding nó đóng. Bảng đối chiếu đảm bảo cả 33 finding + V-01…V-03 đều có nơi thuộc về |
| **Ước lượng khối lượng chưa có** | Đề xuất này **không** ước lượng thời gian. Việc đó thuộc T-04 khi soạn Completion Gate cho từng gói |

## Phương án thay thế nếu chủ dự án muốn tới official run nhanh hơn

**Lớp A tối thiểu tuyệt đối** — chỉ giữ những gói mà nếu thiếu thì official run **không cứu được**:
WP-A1 (provenance), WP-A3 (kết quả mô phỏng sai), WP-A5 (dữ liệu chỉ sinh khi chạy).
Chuyển WP-A2, WP-A4, WP-A6 xuống lớp B, chấp nhận phải **chạy lại Gate 1** (rẻ) và chấp nhận
official run đại diện cho thuật toán có sai lệch thứ tự chưa được chứng minh là vô hại.

Tôi **không khuyến nghị** phương án này, vì WP-A6 quyết định "official run đại diện cho thuật
toán nào" — câu hỏi đó không nên để ngỏ. Nhưng đây là quyết định của chủ dự án, không phải của
agent.

---

# 10. NHỮNG GÌ ĐỀ XUẤT NÀY KHÔNG LÀM

- **Không chốt DEC-005.** Giữ nguyên PENDING. Đề xuất chỉ ghi nhận rằng DEC-005 không còn nằm
  trên đường găng tới verdict.
- **Không sửa** `src/`, `webapp/`, `tests/`, `docs/spec/`.
- **Không sửa bảng roadmap chuẩn** trong `PROJECT/PROJECT_PROGRESS.md`.
- **Không bắt đầu S002.**
- **Không bypass BLK-001**, không đổi nguồn dữ liệu, không dùng synthetic để tạo official verdict.
- **Không hạ Completion Gate của T-03.**
- **Không tự quyết** phạm vi Execution State machine — đề xuất một ADR thay vì áp giải pháp.

---

# 11. YÊU CẦU PHÊ DUYỆT

Chủ dự án cần quyết bốn điểm:

1. **Chấp thuận cấu trúc 15 work package** và cách gom theo nguyên nhân gốc?
2. **Chấp thuận phân lớp A/B/C/D**, đặc biệt: gộp cả năm finding của WP-A2 vào lớp A (§3),
   và để F-017 ở lớp B dù nó cần chạy lại Gate 1 (§3)?
3. **Chấp thuận bỏ T-06A** và hấp thụ vào WP-A1?
4. **Quyết định về sai lệch biên của router** với WP-A2: giữ B/Sonnet/high theo router, hay
   nâng lên C/Opus?

Sau khi được duyệt, bảng roadmap chuẩn sẽ được cập nhật và `sync_easy_roadmap.py` được chạy
trong cùng phiên theo `ROADMAP_SYNC_STANDARD.md`.
