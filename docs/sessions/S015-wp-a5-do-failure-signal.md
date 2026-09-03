# S015 — WP-A5: Đo đủ dữ liệu cho ba Failure Signal

Ngày: 2026-09-03
Nhánh: `claude/coindca-data-stream-vv0vwv`
Baseline (SHA ngay trước WP-A5): `b095874` (WP-A6 DONE)
Task: `docs/tasks/WP-A5-instrumentation-failure-signal.md`
Capability: `CAP-MEASURE` (lineage root `WP-A5`) — lượt này là **implementation ban đầu**,
không tiêu repair cycle.
Model/Effort canonical: **Tier C / Opus / `xhigh`** — phiên chạy đúng Tier C (Opus 5), không
uỷ quyền subagent.

## 0. Vì sao gói này tồn tại

Backtest §17 đặt mười hai Failure Signal lên trên chính các Decision Gate: *"Với chỉ khoảng ba
block dữ liệu độc lập, Failure Signals mang nhiều thông tin hơn chính các Decision Gate, vì
chúng chẩn đoán CƠ CHẾ chứ không chỉ đo kết quả."* Nhưng ba trong mười hai signal chưa bao giờ
nhận được input, và hai signal khác chỉ được tính trên một window đại diện. Nghĩa là 3/12 bằng
chứng mạnh nhất luôn UNKNOWN, và 2/12 nữa đo trên một mẫu hẹp hơn mẫu thật.

Điều quyết định gói này ở lớp A (phải xong TRƯỚC official run): ba đại lượng đó **chỉ sinh ra
được khi engine đang chạy**. Chính sách đọc lại được từ `pipeline_state.json` nên sửa sau cũng
kịp; dữ liệu chưa từng được đo thì không đọc lại được từ đâu.

## 1. Trạng thái vào phiên

Ready Gate xác nhận lại đầy đủ tại phiên này: `T-04` ✅, `WP-A2` ✅ (S006), `WP-A3` ✅ (S003),
`WP-A7` ✅ (S004) — cả bốn dependency đều DONE. Ràng buộc "không song song với WP-A2 vì cùng
sửa `pipeline.py`" hết hiệu lực vì WP-A2 đã DONE. `branch_authority_check.sh` PASS.
Completion Gate 9 REQUIRED check, **E1 toàn bộ** (gói này không có check nào đòi E2).

## 2. Chẩn đoán chính xác — cái gì đang thiếu (E1, đọc từ mã, xác nhận bằng chạy)

Lời gọi `evaluate_failure_signals` trong `pipeline.py::run_verdict` **không truyền** đúng ba
tham số, dù chữ ký hàm đã có sẵn chúng với mặc định `None`:

| Tham số thiếu | Signal | Hệ quả trước WP-A5 |
|---|---|---|
| `opportunity_cap_hit_share` | FS-02 | luôn `None` = UNKNOWN |
| `adjacent_config_flip` | FS-06 | luôn `None` = UNKNOWN |
| `regime_advantage_share` | FS-12 | luôn `None` = UNKNOWN |

Và `run_gate1` tính `concentration` (→FS-03) cùng `cash_ratio_stats` (→FS-07) **chỉ trên
`wm["windows"]["W5"]`**, kèm chú thích "window giữa (W5) làm đại diện chẩn đoán" — đúng nội
dung F-016.

## 3. Điểm khó thật sự: spec định nghĩa bằng văn xuôi, không có công thức

BT §17 mô tả cả mười hai signal bằng một câu tiếng Việt, không kèm công thức. Đây đúng là
Escalation Trigger #1 của gói ("không tự sáng tạo định nghĩa rồi im lặng"), nên mọi định nghĩa
được chốt thành quy ước tường minh tại **`docs/CONVENTIONS.md` #20 (a)–(f)**, kèm lý do và kèm
phương án thay thế đã cân nhắc. Ba điểm đáng ghi lại:

**(a) FS-02 — vế "chạm cap" bão hoà, và điều đó được nói ra.** `Pool.total = available +
reserved + deployed` (DM §6) nên `total` không giảm khi vốn được giải ngân: một khi quỹ đầy
lần đầu, `at_cap` là TRUE vĩnh viễn. Sức phân biệt thật nằm ở vế `idle`. Quy ước vẫn dùng
**đúng phép so mà engine dùng để chặn contribution** (không phát minh phép so mới), nhưng ghi
thẳng giới hạn này vào CONVENTIONS để người đọc số không hiểu nhầm, và kèm bốn thống kê phụ
trợ (`at_cap_share`, `mean_idle_ratio`, `share_idle_ge_1pct_cap`, `share_idle_ge_10pct_cap`)
để `WP-B1` tinh chỉnh ngưỡng vật chất **mà không phải chạy lại engine**.

**(b) FS-12 — mẫu số là khối lợi thế DƯƠNG, không phải lợi thế ròng.** Lợi thế ròng có thể âm
hoặc gần 0, làm tỷ lệ vô nghĩa hoặc nổ quá 1. Câu hỏi của §17 là "trong phần lợi thế đã tạo
ra, bao nhiêu đến từ một regime" — nên mẫu số đúng là khối dương. Khi không regime nào có lợi
thế dương, đại lượng **không xác định** → trả `None` kèm lý do, **không quy về 0.0** (0.0 sẽ
bị đọc thành "không tập trung", một khẳng định sai).

**(c) FS-12 gộp theo KHỐI, FS-02/03/07 gộp theo PrimaryMedian — và lý do khác nhau.** Với đại
lượng MỨC (concentration AE, cash ratio, cap-hit share) thì PrimaryMedian là phép gộp mà chính
BT §4.1 đặt ra để chống thiên vị do chín window chồng lấn, nên dùng lại đúng phép đó. Với FS-12
thì không: gộp chín TỶ LỆ sẽ khiến chỉ một window không có lợi thế dương là cả đại lượng thành
UNKNOWN — tức UNKNOWN vì lý do **không phải thiếu đo lường**, đúng thứ gói này tồn tại để loại
bỏ (thực tế đo được: W4 rơi đúng vào ca này). FS-12 hỏi về chiến lược chứ không hỏi từng
window, nên cộng khối lợi thế trên cả chín window rồi mới lấy tỷ lệ. Thiên lệch do chồng lấn
tác động lên tử và mẫu cùng chiều nên với một TỶ LỆ chỉ còn bậc hai. Tỷ lệ từng window và
PrimaryMedian của chúng **vẫn được ghi lại** để WP-B1 đổi input mà không phải chạy lại engine.

## 4. Đã làm gì

**`engine.py` — chỉ thêm hai điểm thu thập số liệu, không đổi hành vi.** `RunResult` mang thêm
`opp_cap_samples` (mẫu theo ngày, cùng nhịp và cùng vị trí với `cash_samples` sẵn có) và
`regime_timeline` (mốc đổi nhãn regime, để quy purchase của benchmark — vốn không mang nhãn —
về đúng regime). Cả hai chỉ ĐỌC property và append vào list; không nhánh execution nào đọc
chúng.

**`metrics.py` — năm hàm đo mới**: `opportunity_cap_hit_share`, `regime_advantage`,
`regime_advantage_pooled`, `adjacent_config_flip`, `aggregate_over_windows` (cộng helper
`_regime_at`, `_advantage_share`).

**`pipeline.py` — mở phạm vi và đấu nối.** FS-03/FS-07 tính từng window rồi gộp PrimaryMedian
(giữ nguyên tên khoá `ae_ex_month`/`ae_ex_quarter`/`avg` mà `failure_signals.py` đang đọc —
đổi PHẠM VI của số, không đổi hợp đồng đọc số); giá trị W5 cũ giữ lại dưới `w5_only_legacy`.
Ba đại lượng mới được truyền vào `evaluate_failure_signals`. Run record mang thêm khối
`failure_signal_inputs_wp_a5` ghi phạm vi + lý do của từng đại lượng, để một signal còn UNKNOWN
luôn nói được **vì sao**.

Mở rộng phạm vi **không thêm một lần chạy engine nào**: chín window đã được `window_metrics`
chạy sẵn, FS-06 dựng từ chính manifest Gate 2 đã chạy.

## 5. Số đo trên dữ liệu tổng hợp (2018-01-01 → 2026-06-30, seed mặc định)

| Đại lượng | Giá trị | Ghi chú |
|---|---|---|
| `opportunity_cap_hit_share` (FS-02) | **0,9063** | PrimaryMedian 9 window; từng window 0,874–0,919 |
| `regime_advantage_share` (FS-12) | **1,0** | khối gộp: chỉ STRESSED có lợi thế dương (+3,179); NORMAL −3,893, CRASH −0,602, RECOVERY −0,238 |
| `concentration.ae_ex_month` (FS-03) | **96,05** | W5-only cũ: **100,64** |
| `concentration.ae_ex_quarter` (FS-03) | **95,25** | W5-only cũ: **101,17** |
| `cash_ratio.avg` (FS-07) | **0,1535** | W5-only cũ: 0,1661 |

**Phát hiện đáng chú ý — mở rộng phạm vi làm FS-03 LẬT.** Với W5 đơn lẻ, `ae_ex_month` =
100,64 và `ae_ex_quarter` = 101,17, cả hai ≥ 100 → FS-03 = FALSE. Với chín window gộp
PrimaryMedian, hai số là 96,05 và 95,25, cả hai < 100 → **FS-03 = TRUE**. Đây chính xác là
điều F-016 cảnh báo: một window đại diện không đại diện cho cả mẫu, và lần này nó che mất một
Failure Signal. Đây là thay đổi do **DỮ LIỆU ĐO MỚI**, không phải do chính sách mới — ngưỡng
100,0 trong `failure_signals.py` không bị đụng tới (xem §7).

FS-12 tính theo từng-window-rồi-gộp (phương án đã bị loại) cho `None` vì W4 không có lợi thế
dương ở bất kỳ regime nào — bằng chứng thực nghiệm cho lựa chọn ở §3(c). Con số của phương án
đó vẫn được ghi trong run record (`per_window_share_primary_median`).

## 6. Kết quả run đủ phase (CHECK-A5-04)

Run đủ phase trên dữ liệu tổng hợp (gate1 + gate2 + gate3 + controls + verdict, dev_limit 25,
tổng 1029 s):

    SIGNALS: {"FS-01": false, "FS-02": true,  "FS-03": true,  "FS-04": true,
              "FS-05": false, "FS-06": false, "FS-07": false, "FS-08": true,
              "FS-09": false, "FS-10": false, "FS-11": "False", "FS-12": true}
    UNKNOWN: []
    VERDICT: DO_NOT_BUILD (Gate 1 FAIL) — KHÔNG official (synthetic + dev_limit, DEC-003)

**Không còn Failure Signal nào UNKNOWN.** Đây là mục tiêu chính của gói, và nó đạt được ở
nghĩa mạnh: không phải "UNKNOWN được che bằng giá trị mặc định", mà là mọi đại lượng đều có
đường sinh ra thật. FS-06 nhận `n_adjacent = 18` config OFAT từ manifest Gate 2 (đúng số OFAT
mà manifest sinh ra), `flip = false`.

## 6b. Khiếm khuyết phát hiện NGAY TRONG run này — `F-S015-01`

Run đủ phase lần đầu ghi ra `"FS-11": "False"` và `"FS-12": "True"` — **dạng chuỗi**, trong
khi mười signal còn lại ra bool JSON thường. Dấu vết đó là `numpy.bool_` đi qua
`json.dumps(default=str)`. Truy tiếp thì đây không phải chuyện thẩm mỹ:

```
failure_signals.py:  any_true = any(v is True for v in fs.values())
verdict.py:27:       if fs["any_true"]:  -> BUILD_WITH_MODIFICATIONS   else: -> BUILD
python:              np.bool_(True) is True   ==>   False
```

Nghĩa là một Failure Signal TRUE mang kiểu `numpy.bool_` **vô hình** với quy tắc chặn của
BT §17 (*"BUILD là không thể khi còn bất kỳ Failure Signal nào TRUE"*). Nếu Gate 1/2/3 đều
PASS và signal TRUE duy nhất mang kiểu numpy, verdict sẽ ra **BUILD** kèm đúng câu "không
Failure Signal nào TRUE" — mở đường sang phase app một cách sai.

Phân loại theo `PRODUCTION_PATH_RULE.md` (cần đủ CẢ BA): production path — CÓ
(`src/eth_dca_os/**`, chuỗi engine → metrics → `evaluate_failure_signals` → `any_true` →
`decide_verdict`); hậu quả nghiệp vụ trong Completion Gate/risk register — CÓ (quy tắc chặn
BT §17, cổng verdict quyết định T-07/T-11); bằng chứng tái lập — CÓ. ⇒ **BLOCKING**, không
phải HARDENING.

**Phần WP-A5 tự sửa (trong Expected Touch Area):** hai đại lượng do gói này cấp được ép về
`float` thuần Python tại `metrics.py`, kèm hai test kiểu và một test end-to-end khẳng định
cờ chặn `any_true` **nhìn thấy được** FS-02/FS-12 khi chúng TRUE. Không phải sửa một dòng
nào trong `failure_signals.py`.

**Phần CÒN MỞ, định tuyến sang `WP-B1`:** `FS-11` vẫn nhận `numpy.bool_` từ `oos_ae`, và
`any_true` vẫn mong manh với mọi đầu vào numpy về sau. Sửa gốc nằm trong `failure_signals.py`
— file mà `CHECK-A5-07` (FROZEN) bắt buộc WP-A5 chứng minh là KHÔNG đổi, và Out of Scope của
gói ghi rõ "mọi thay đổi trong `verdict.py`" là của WP-B1. Vì vậy phiên này **không** tự sửa,
không tạo task mới, không đổi roadmap. Test `test_a5_04_numpy_typed_signal_would_be_invisible`
ghi lại cơ chế và sẽ **đỏ** khi WP-B1 đóng khiếm khuyết — lúc đó xoá test và đóng F-S015-01.

**Điểm cần chủ dự án quyết (trình tự, không phải kỹ thuật):** roadmap đặt `WP-B1` SAU `T-06`,
nhưng chính `T-06` mới phát ra verdict official. Nếu giữ nguyên trình tự, verdict official
đầu tiên sẽ được tạo bởi mã còn mang khiếm khuyết này. Phiên S015 nêu ra chứ không tự đổi
trình tự.

**Bằng chứng TRƯỚC/SAU của chính lần sửa này** (hai run đủ phase, cùng dataset, cùng dev_limit):

| Signal | Trước khi ép kiểu | Sau khi ép kiểu |
|---|---|---|
| `FS-12` | `"True"` (chuỗi ⇒ `numpy.bool_`, vô hình với `any_true`) | **`true`** (bool JSON ⇒ cờ chặn thấy được) |
| `FS-11` | `"False"` (chuỗi) | `"False"` (**vẫn** chuỗi — ngoài phạm vi WP-A5) |
| 10 signal còn lại | không đổi | không đổi |

Bảng này là bằng chứng hai chiều: (1) phần WP-A5 sở hữu đã thật sự đóng; (2) phần định tuyến
sang WP-B1 đúng là còn mở, không phải suy đoán. Và vì mười signal còn lại giữ nguyên giá trị,
sửa kiểu chỉ đổi **kiểu**, không đổi **kết luận** nào.

## 7. Ranh giới ĐO LƯỜNG / CHÍNH SÁCH được giữ (CHECK-A5-07)

`git diff b095874..HEAD -- src/eth_dca_os/verdict.py src/eth_dca_os/failure_signals.py` = **rỗng**.
Không ngưỡng nào, không ánh xạ gate-fail → verdict nào, không quy tắc UNKNOWN nào bị đụng.
Test `test_a5_07_verdict_policy_thresholds_unchanged` khoá hành vi ngưỡng bằng cách **gọi tại
biên** (0,50/0,51 cho FS-02; 0,80/0,81 cho FS-12; 100,0 cho FS-03; cặp 0,30 & 102,0 cho FS-07)
chứ không đọc văn bản mã nguồn — nếu một gói sau lỡ đổi chính sách, test đỏ ngay tại con số bị
đổi. Test `test_a5_07_no_diff_in_policy_files` chạy đúng lệnh `git diff` mà chữ check yêu cầu.

Mọi trường hợp không đo được đều đi vào **đúng đường UNKNOWN sẵn có** (`None` → signal `None`)
— WP-A5 không thêm đường mới và không gán giá trị mặc định.

## 8. Instrumentation không đổi hành vi (CHECK-A5-08)

`test_a5_08_instrumentation_does_not_change_engine_behaviour` nạp `engine.py` tại `b095874` từ
git (dùng `load_engine_from_source` mà WP-A6 để lại) và so **bit-for-bit** với engine hiện tại
trên cùng dataset và cùng cửa sổ 2019-01-01 → 2022-01-01: `eth_total`, từng bản ghi purchase,
`counters`, `cash_samples`, `monthly_deployments` đều trùng khớp. Test cũng khẳng định bản cũ
đúng là bản CHƯA có instrumentation (nếu không, phép so vô nghĩa).

## 9. Việc KHÔNG làm (giữ Scope Lock)

Không đụng `verdict.py`, `failure_signals.py` (ngưỡng/chính sách), `gates.py`, `regime.py`,
`ladders.py`, `capital.py`, `score.py`, `webapp/`, `docs/spec/`. Không quyết định chính sách
verdict nào. Không đổi hành vi thực thi engine. Không chạm `WP-A1`, `T-05`, `T-06`, `BLK-001`,
`H-24`/`H-25`, `WP-D2`, nhánh `T-09B`.

## 10. Còn lại sau gói này

- Giá trị **official** của cả mười hai signal vẫn phải chờ `T-06` trên dữ liệu Binance thật
  (`BLK-001` chưa gỡ; `DEC-003` cấm dùng dữ liệu tổng hợp cho official verdict). Số ở §5 chứng
  minh **instrumentation đúng**, không phải bằng chứng verdict.
- Việc *dùng* các signal (ngưỡng, chính sách UNKNOWN, quy tắc chặn BUILD) thuộc **WP-B1**.
- `GATE-A` vẫn chưa đóng: còn `WP-A1` (`IN_PROGRESS`, budget `CAP-PROV` hết, chờ Owner
  disposition ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED`).
