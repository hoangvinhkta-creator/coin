# S009 — WP-A4: Ngữ nghĩa dữ liệu thiếu/hỏng + độ phủ theo khoảng được yêu cầu

## Metadata

Ngày:
2026-09-01

Task:
WP-A4 (`docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md`)

Capability:
`CAP-DATA` (lineage root = WP-A4)

Branch:
`claude/wp-a1-provenance-v67k9h`

SHA đầu phiên:
`06b381c` (khớp Expected HEAD của chỉ thị)

Task Mode:
MAJOR

Tier / Effort (từ routing metadata, không chọn tay):
C / `xhigh` — `validate_routing.py` PASS

Effective Risk:
Local Risk 3 · Blast Radius 2 → theo `RISK_MODEL.md` `Effective Risk = MAX(...)` = **3**.
Không nâng risk: không có evidence mới nào làm đổi routing input của WP-A4.

## 0. Điều kiện đầu phiên

Chạy `branch_authority_check.sh` TRƯỚC khi đọc bất kỳ state file nào (AGENTS.md §7 Step 0):

```
branch            = claude/wp-a1-provenance-v67k9h
default branch    = claude/plan-tool-from-docs-qijx5m (resolved, not assumed)
behind upstream   = 0
ahead of default  = 30 commit(s)
divergence age    = 9 day(s)
divergence LOC    = 26114
INTEGRATION_DECISION_REQUIRED: ahead>10 age>3d loc>5000
tracked worktree  = CLEAN
production diff   = EMPTY
BRANCH AUTHORITY: PASS
```

`INTEGRATION_DECISION_REQUIRED` là quyết định ĐANG MỞ thuộc chủ dự án, đã được phân tích
đầy đủ ở `docs/decisions/OWNER-DISPOSITION-2026-09-01-...` §7 (khuyến nghị A — INTEGRATE
NOW, chi phí rủi ro đo được = 0). Chỉ thị phiên này nói rõ **"Không merge default branch"**,
nên phiên KHÔNG tự tích hợp và KHÔNG tự đóng quyết định đó. Ghi nhận: cửa sổ "xung đột = 0"
mà §7.5 nêu **đã đóng lại** sau phiên này — WP-A4 vừa sửa `src/eth_dca_os/data/`.

Local clone khi mở phiên đang ở `6c11a7e` (thiếu 3 commit). Đã `git fetch` + fast-forward
tới `06b381c` trước khi đọc state — đúng lý do tồn tại của Step 0.

## 1. Owner Decision đã phê chuẩn

`OD-A4-01` (chỉ thị phiên, 2026-09-01) phê duyệt **COMPLETION GATE CHANGE PROPOSAL** cho
WP-A4: thêm đúng MỘT REQUIRED check về độ phủ theo khoảng thời gian được yêu cầu, và làm
rõ Expected Touch Area (loại trừ là về **cơ chế lấy** dữ liệu, không phải về **ngữ nghĩa
coverage**). Kèm theo: `F-E2A1R3-05` được gán cho `CAP-DATA`, hấp thụ vào WP-A4,
**không tạo task ID mới**.

Đây là hành động đúng theo `REVIEW_PROTOCOL.md` § Finding Routing: một finding được định
tuyến vào capability owner phù hợp, không được đúc thành task mới.

## 2. Vấn đề — tái lập TRƯỚC khi sửa

`F-E2A1R3-05`: dataset bị cắt cụt vẫn đủ tư cách official, `missing_count` không phát hiện.

Counterexample đi theo **đường sản xuất bình thường**, chỉ thay lớp HTTP bằng stub dựng
trên mã production thật và tham số production thật (nguồn canonical 1 + 2 của
`PROJECT/PRODUCTION_PATHS.md` §3). Không sửa tay `lineage.json`, không mock eligibility,
không input thù địch.

Kịch bản: `ethdca fetch --start 2020-01-01 --end 2021-01-01`; archive
`data.binance.vision` chỉ có file tới tháng 2020-01; REST `api.binance.com` bị chặn
(BLK-001) nên trả rỗng.

**BEFORE (`06b381c`)**

```
REQUEST: start=2020-01-01  end=2021-01-01

series        source                      rows  missing  first       last
BTCUSDT_1d    binance_bulk_archive          31        0  2020-01-01  2020-01-31
ETHUSDT_15m   binance_bulk_archive       38016        0  2019-01-01  2020-01-31
ETHUSDT_1d    binance_bulk_archive          31        0  2020-01-01  2020-01-31

official_eligibility -> (True, 'verified')

1d coverage thực tế = 31/366 = 8.5% khoảng thời gian ĐƯỢC YÊU CẦU
missing_count báo cáo = 0
```

Dataset thiếu **91,5%** khoảng được yêu cầu, tự khai không thiếu nến nào, và đủ tư cách
official. Sau đó `Prepared.official_eligible = True` cho MỌI gate, nên một verdict "chính
thức" có thể được sinh ra từ 8,5% dữ liệu.

## 3. Root cause

Hai chỗ, cùng một sai lầm — hệ thống **mô tả sai cái gì đang thiếu**:

1. `data/dataset.py::gap_report` tính `expected = (last_observed - first_observed)/freq + 1`.
   Số nến kỳ vọng được neo vào **khoảng quan sát được**, nên phần thiếu ở HAI ĐẦU là thứ
   mà chính dữ liệu ấy không thể tự khai. Lỗ hổng ở GIỮA thì phát hiện được; cắt cụt thì
   vô hình.
2. `data/dataset.py::official_eligibility` không đọc `first_timestamp`/`last_timestamp`
   ở bất kỳ đâu, và không có khái niệm "khoảng đã được yêu cầu".

`fetch_all` **không** có lỗi: nó trả về đúng những gì archive có. Đúng như phân tích §5.2
của Owner Disposition, defect nằm ở ngữ nghĩa coverage chứ không ở cơ chế lấy dữ liệu.

## 4. Sửa tối thiểu

Khoảng thời gian được yêu cầu là dữ kiện **chỉ nơi sản xuất dataset biết** — file parquet
kết quả không mang nó. Vì vậy: khai tại nơi tạo dataset → ghi vào lineage → cổng đọc.

| File | Thay đổi |
|---|---|
| `data/dataset.py` | `gap_report(df, interval, requested_start, requested_end)` neo `expected` vào khoảng yêu cầu; tách `missing_head` / `missing_internal` / `missing_tail`. `build_lineage(..., requested_range=...)` ghi khai báo vào từng entry và **mang theo khai báo cũ** khi dựng lại. `official_eligibility` thêm điều kiện độ phủ, fail-closed khi không có khai báo. |
| `data/fetch.py` | `fetch_all` khai `requested_range` từ chính `start`/`end` đã xin (15m từ 2019 theo BT §2). |
| `data/synth.py` | `generate` khai tương tự. |

Không redesign `fetch_all`, không tạo abstraction mới, không đổi `dataset_hash` (hash vẫn
chỉ dẫn xuất từ danh sách `file_hash`, nên mọi run record và `manifest_hash` cũ không trôi).

Chữ ký `official_eligibility(raw_dir, lineage)` **giữ nguyên** — contract WP-A1 khoá nó
bằng test, và thêm tham số ở đây sẽ mở lại đúng bề mặt "ép official" mà WP-A1 vừa đóng.

**Ngưỡng.** `MAX_MISSING_RATIO = 0.01`. Không thể đặt bằng 0: dữ liệu Binance thật có gap
bảo trì, ngưỡng 0 sẽ từ chối mọi dataset thật. Mọi lần từ chối mang theo số đo, nên khi
T-06 chạy trên dữ liệu thật, một lần từ chối là **dữ kiện để chủ dự án quyết định**, không
phải hằng số để nới cho qua. Ghi ở `docs/CONVENTIONS.md`.

**AFTER — cùng counterexample, cùng lệnh**

```
series        source                      rows  missing  first       last
BTCUSDT_1d    binance_bulk_archive          31      335  2020-01-01  2020-01-31
ETHUSDT_15m   binance_bulk_archive       38016    32160  2019-01-01  2020-01-31
ETHUSDT_1d    binance_bulk_archive          31      335  2020-01-01  2020-01-31

official_eligibility -> (False, 'incomplete_coverage:ETHUSDT_1d=31/366 head=0 internal=0 tail=335')
```

Và ở tầng quyết định: `Prepared.official_eligible = False`, `official_reason` bắt đầu bằng
`incomplete_coverage:` — mà `Prepared` là nơi DUY NHẤT mọi gate lấy cờ `official`
(WP-A1/A1.2), nên chặn ở đây là chặn cho toàn bộ Gate 1/2/3 và verdict. Fail closed.

## 5. Phạm vi FROZEN của WP-A4 — đã thực hiện

Ngoài check Owner vừa thêm, phiên đóng ba finding gốc của gói:

**F-023 — định nghĩa INVALID hẹp hơn Strategy §3.** Trước đây INVALID chỉ khi mất **cả
tám** sub-factor. §3 nói INVALID khi "giá/lịch sử ETH **hoặc** indicator bắt buộc không hợp
lệ". Spec không liệt kê tập "indicator bắt buộc" → quy ước được chốt và ghi ở
`docs/CONVENTIONS.md`: `close`, `return7`, `adr30` (tiêu chí: được đọc trên **đường hành
động**, không chỉ là sub-component của score). Ngày INVALID có `oscore = NaN` theo Data
Model §4.

Khoảng cách cụ thể mà luật cũ bỏ lọt: thiếu `return7` chỉ làm 2/8 sub-factor NaN → luật cũ
đọc là DEGRADED và engine tiếp tục hành động ở đúng thời điểm §3 yêu cầu dừng.

**F-025 — `EXECUTION_DATA_GAP` không tồn tại trong `src/`.** Engine vốn đã không interpolate
OHLC để trigger zone (nó chỉ duyệt nến có thật), nhưng không bản ghi nào cho biết mình nằm
ngay sau một lỗ hổng. Nay mỗi purchase record mang `tags` và `missing_candles_before`.

**F-032 — `DELAYED_DATA_FILL` chỉ là bộ đếm.** Nay là tag TRÊN BẢN GHI. Bộ đếm vẫn còn để
đối chiếu, và test khoá đẳng thức "số bản ghi mang tag = giá trị bộ đếm" theo cả hai chiều.

## 6. Định lượng thay đổi kết quả mô phỏng (CHECK-A4-07)

Cùng seed, cùng file parquet, cùng config (`BASELINE_STRATEGY` + `GATE1_LOW_FRICTION`),
cửa sổ 2020-01-01…2021-01-01. Dataset synth `2018-01-01…2021-06-30` được khoét ba loại lỗ
hổng, mỗi loại ứng với một điều khoản spec:

1. 108 nến 15m bị xoá — gồm khung 12:00–13:00 local ba ngày Base của 2020-04, một cửa sổ
   bảo trì 6h (2020-05-11) và một 18h (2020-08-02) → BT §18, ST §9 [F3];
2. 19 dòng daily BTC bị xoá (tháng archive BTC hỏng) → ST §3 nhóm DEGRADED;
3. 7 dòng daily ETH có `close` không hợp lệ → ST §3 nhóm INVALID.

BEFORE = `06b381c`, AFTER = HEAD phiên này.

| Metric | BEFORE | AFTER | Δ | Quy về điều khoản |
|---|---|---|---|---|
| `data_quality` GOOD | 210 | 210 | 0 | — |
| `data_quality` DEGRADED | 156 | 119 | −37 | 37 ngày chuyển sang INVALID |
| `data_quality` INVALID | 0 | **37** | +37 | **ST §3** — 7 ngày `close` hỏng + 30 ngày `adr30` NaN kế tiếp (rolling 30 cần 30 giá trị hợp lệ) |
| `oscore` NaN (ngày) | 0 | **37** | +37 | **DM §4** — `opportunity_score_raw` nullable chỉ khi INVALID |
| `triggered_actions` | 17 | 13 | −4 | **ST §3** — "chặn mọi action Smart và Opportunity mới" trong 37 ngày INVALID |
| `executed_actions` | 17 | 13 | −4 | hệ quả trực tiếp của dòng trên |
| `n_purchases` | 65 | 61 | −4 | hệ quả trực tiếp |
| `eth_total` | 2.1983245965 | 2.1941171636 | **−0.19%** | cùng số tiền, giải ngân ở thời điểm/giá khác |
| nominal BASE | 600.0 | 600.0 | **0** | **ST §9 [F3]** — Base không bao giờ bị bỏ vì gap |
| nominal SMART | 520.0 | 520.0 | **0** | vốn Smart bị chặn ở zone được settle theo Month-End policy (ST §10) |
| `contributed_total` | 1300.0 | 1300.0 | 0 | không đụng lớp vốn |
| `delayed_data_fill` | 3 | 3 | 0 | bộ đếm vốn đã đúng — thứ thiếu là tag |
| bản ghi mang tag | **0** | **3** | +3 | **F-032 đóng** — BT §18 |
| `execution_data_gap` | (không tồn tại) | 3 | mới | **F-025 đóng** — BT §18 |
| `cooldown_override[NORMAL]` | 2 | 0 | −2 | ít action hơn → ít sự kiện override hơn |

Không có sai lệch nào **không** quy được về một điều khoản spec.

Đọc thêm: trên dataset synth **không** khoét lỗ (cùng cửa sổ, cùng seed), BEFORE và AFTER
cho kết quả **trùng khớp từng chữ số** (`eth_total = 2.1995839535`, 65 purchase, 366 ngày
GOOD). Nghĩa là thay đổi hành vi chỉ xuất hiện đúng ở nơi dữ liệu xấu — không có drift nền.

## 7. Điều KHÔNG làm

- Không redesign `fetch_all` / kiến trúc fetch.
- Không đụng `regime.py`, `ladders.py`, `capital.py`, `verdict.py`, `failure_signals.py`.
- Không đụng `webapp/`, `docs/spec/`.
- Không mở repair cycle cho WP-A1; không tự đóng 3 hạng mục
  `LEGACY_GATE_DISPOSITION_REQUIRED` của WP-A1.
- Không tạo task ID mới (finding ≠ task).
- Không merge default branch.
- Không mở WP-C1 / WP-A5 / WP-A6; không chạy T-06.

## 8. Budget

`CAP-DATA` — lineage root WP-A4. Trước phiên: repair cycles = 0, vòng E2 = 0, baseline
"chưa bắt đầu". Phiên này là **implementation ban đầu**, không phải repair cycle.
KHÔNG kế thừa và KHÔNG đụng budget của `CAP-PROV`.

## 9. Phát hiện mới trong phiên

**`F-S009-01` — CONFIRMED BLOCKING, `OWNER_ASSIGNMENT_REQUIRED`.** Indicator daily được
tính theo VỊ TRÍ hàng, không theo NGÀY LỊCH (`return7 = close / np.roll(close, 7) - 1`, và
mọi `rolling(N)`). Một ngày daily thiếu làm `return7` sai **14,29%** mà không NaN, không
DEGRADED, không INVALID — và dataset vẫn qua `official_eligibility` với `(True,'verified')`
vì 1/365 = 0,27% nằm dưới ngưỡng 1%. Đi trọn đường sản xuất, không sửa tay artifact.

KHÔNG làm FAIL check nào của WP-A4 (nằm ngoài gate đã FROZEN + `CHECK-A4-10`), KHÔNG sửa ở
phiên này (`indicators.py` ngoài Expected Touch Area), KHÔNG tạo task ID. Phải đóng trước
T-06. Chi tiết và định tuyến: `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md`.

**HARDENING mới:** `H-14` (trường độ phủ nằm ngoài mọi checksum — cùng lớp H-05/H-06/H-13,
kèm ghi nhận ép kiểu `missing_head/internal/tail` cùng lớp H-04), `H-15` (zone TRIGGERED
trong chu kỳ INVALID vẫn thành action sau khi dữ liệu phục hồi — thuộc `WP-A6`). Cả hai đều
có `RE_TRIGGER_CONDITION`.

## 10. Kết quả

Xem `docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md` § Completion Gate cho trạng thái từng check.
