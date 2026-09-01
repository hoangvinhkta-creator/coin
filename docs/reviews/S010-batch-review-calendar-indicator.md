# Batch review bắt buộc — CAP-DATA REPAIR CYCLE #1 (`F-S009-01`)

Ngày:
2026-09-01 (phiên S010)

Vì sao bắt buộc:
`DEC-017` đặt `CAP-DATA` Effective Risk = **HIGH**. `governance/v4/CORE/RISK_MODEL.md`
§ "HIGH Does Not Mean STOP": *"a change on a HIGH Blast Radius path requires a mandatory
batch review at end of session, however small the change."*

Nguyên tắc áp dụng:
`REVIEW_PROTOCOL.md` — **REVIEW WIDE — REPAIR NARROW**. Toàn bộ BLOCKING finding nhận diện
được phải trả **trong một lượt**; chia nhỏ qua nhiều phiên là process failure, không phải
kỹ lưỡng.

---

## 0. Sáu bước trước khi review

| # | Bước | Giá trị |
|---|---|---|
| 1 | SHA đầy đủ + remote SHA | base `cb75f9d1fb139f4c5daae063e754245998819f22` = `origin/main`; head phiên này ghi ở `docs/sessions/S010-cap-data-repair-cycle-1.md` |
| 2 | branch authority check | chạy; xem §0 của session handoff |
| 3 | phiên bản interpreter/tool | Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · requests 2.33.1 · pytest 9.1.1 — **trùng khớp `pyproject.lock` từng dòng** |
| 4 | tracked worktree | CLEAN trước khi bắt đầu (branch authority: `production diff = EMPTY`) |
| 5 | Task Spec / gate / production path / risk / ledger | đã đọc: `WP-A4`, `PRODUCTION_PATHS.md`, `PROJECT_PROGRESS.md` § Active Risks, `REVIEW_BUDGET_LEDGER.md` |
| 6 | cumulative repair diff | `git log 666de14..cb75f9d -- src/eth_dca_os/indicators.py` → **0 commit**. `F-S009-01` nằm NGOÀI mọi cumulative repair diff đã ghi, nên bản sửa tiêu **một repair cycle mới** — đúng như `REVIEW_BUDGET_LEDGER.md` §4.3 đã cảnh báo trước |

Phạm vi review: cumulative repair diff của **chu kỳ này** —
`src/eth_dca_os/indicators.py` (+74 / −5) và `tests/test_wp_a4_calendar_indicator_semantics.py`
(file mới). Review đọc rộng hơn diff (theo REVIEW_PROTOCOL), nhưng repair giữ hẹp.

Giới hạn phải nói rõ, không giấu:
Đây **không** phải review của một reviewer độc lập là con người. Dự án là solo
(`PROJECT_PROFILE.md`: "Không có reviewer thứ hai là con người"), và cùng một hạn chế đã
được ghi ở `CHECK-A4-09`. Vì vậy verdict dưới đây là **E1 + một lượt dò đối kháng có ghi
lệnh chạy**, KHÔNG được đọc thành E2.

---

## 1. Kết quả — toàn bộ finding, một lượt

    BLOCKING   = 0
    HARDENING  = 2   (H-16, H-17)
    OUT_OF_SCOPE = 1 (routed CAP-WEBAPP / WP-C4)
    DEFERRED_BY_MINIMAL_FIX = 1
    Task ID mới = 0

Không finding nào bị giữ lại cho lượt sau.

---

## 2. Mệnh đề chính — có thoả không?

Câu chữ Completion Gate (`DEC-016` §4): *ngày lịch daily bắt buộc thiếu → indicator bị ảnh
hưởng phải tính ĐÚNG theo lịch, HOẶC DEGRADED/INVALID/NaN, nhưng KHÔNG được trả một giá trị
hữu hạn SAI rồi đi tiếp như dữ liệu bình thường.*

Dò đối kháng trên toàn bộ 18 cột của `compute_daily_indicators`, chuỗi 900 ngày, bỏ đúng
một ngày ở vị trí 400 (`scratchpad/adversarial.py` §C):

    Cot tra HUU HAN ma KHAC gia tri dung:
      ma200 81 · ma_ratio 79 · ma200_slope 125 · rsi14 462

Bốn cột này được **định lượng** ở `CHECK-A4-11` § "Độ lệch dư": `ma200` ≤ 2,11e-16 tương
đối, `rsi14` ≤ 7,44e-13 tương đối. Nguyên nhân là (a) thứ tự kết hợp phép cộng của rolling
online trong pandas khi một `NaN` đi qua cửa sổ, và (b) đuôi suy giảm `(13/14)^k` của hồi
quy Wilder được warm-up lại. Cả hai đều **không** phải ngữ nghĩa row-position, và cả hai
đều **bằng 0** trên dữ liệu sạch.

Đối chiếu với độ lớn của chính `F-S009-01`: 14,29% (§3) và 295,08% kèm ĐỔI DẤU (§II.2).
Chênh 13–16 bậc độ lớn. Mệnh đề chính **THOẢ**; phần dư được ghi thành HARDENING **H-16**,
không được xoá khỏi hồ sơ.

Mười bốn cột còn lại (`return7`, `adr30`, `high365`, `percentile365`, `dd365`,
`volume_ratio`, `vol7`, `vol90`, `volume_z365`, `ethbtc`, `ethbtc_return30`,
`ethbtc_percentile180`, `close`, `btc_close`) lệch **đúng bằng 0** sau khi cửa sổ trượt qua
ngày thiếu.

---

## 3. Finding

### F-S010-01 — HARDENING (`H-16`): sai số ULP trên dataset CÓ GAP

Ba tiêu chí BLOCKING, kiểm từng cái:

- **Production path** — CÓ (`src/eth_dca_os/indicators.py`).
- **Hệ quả nghiệp vụ trong Completion Gate hoặc risk register** — **KHÔNG chứng minh được.**
  Để 2e-16 làm đổi một quyết định thì `ma_ratio` phải nằm cách ngưỡng đúng dưới 1 ULP.
  Counterexample đó không dựng được từ bốn nguồn canonical của `PRODUCTION_PATHS.md` §3;
  `PRODUCTION_PATH_RULE.md` xếp đúng loại này là HARDENING **theo định nghĩa, không phải
  theo nhân nhượng**.
- **Bằng chứng tái lập** — CÓ (`scratchpad/quantify_drift.py`, tất định theo seed).

Thiếu tiêu chí thứ hai → **HARDENING**, không mặc định BLOCKING.

    RE_TRIGGER_CONDITION:
    Khi T-06 chạy trên dữ liệu Binance THẬT và dataset official chứa ít nhất một ngày daily
    thiếu, đối chiếu `ma200` / `ma_ratio` / `rsi14` quanh mọi ngưỡng quyết định. Nếu tồn tại
    một ngày mà lệch ULP đủ để lật một so sánh ngưỡng, mục này thành BLOCKING và quay lại
    CAP-DATA.

### F-S010-02 — HARDENING (`H-17`): ngày daily TRÙNG LẶP nay làm `ValueError` thay vì đi qua im lặng

`eth.reindex(cal)` ném `ValueError: cannot reindex on an axis with duplicate labels` khi
series daily có hai hàng cùng một ngày. TRƯỚC bản sửa, trùng lặp đi qua im lặng và một
trong hai hàng được dùng tuỳ thứ tự.

- **Production path** — CÓ.
- **Dựng được từ nguồn canonical?** — KHÔNG. `data/fetch.py::fetch_series` đã
  `drop_duplicates("open_time")`; `data/synth.py` dựng daily bằng `groupby(freq="1D")`.
  Không đường sinh nào tạo được ngày trùng.
- Chiều thay đổi là **fail-closed** (ném lỗi thay vì chọn thầm một hàng), tức đúng hướng
  của `DEC-011` điểm 9.

→ **HARDENING**. Không sửa trong chu kỳ này: sửa nó là thêm ngữ nghĩa khử trùng lặp cho dữ
liệu, tức mở rộng phạm vi ngoài `DEC-016`.

    RE_TRIGGER_CONDITION:
    Khi một nguồn dữ liệu mới (REST tail chồng lấn archive, nguồn thứ ba, import thủ công)
    có thể sinh hai hàng cùng ngày; hoặc khi `ValueError` này thực sự xuất hiện một lần.
    Khi đó thay bằng một lỗi có chẩn đoán rõ ràng, hoặc một quy tắc khử trùng lặp được ghi.

### F-S010-03 — OUT_OF_SCOPE → `CAP-WEBAPP` / `WP-C4`: parity JS/Python nay lệch

`webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả và vẫn tính theo **vị trí hàng**
(`rollMax`, `rollMean`, `wilderRSI`, `rollPercentileOfLast` — dòng 18–112), với chú thích
ngay trong file: *"khớp semantics của pandas trong indicators.py"*. Sau chu kỳ này câu chú
thích đó **không còn đúng** trên dữ liệu có ngày daily thiếu.

Định tuyến, KHÔNG sửa ở đây:

- `webapp/` nằm trong danh sách **"Do not touch without Scope Expansion"** của WP-A4, và
  `DEC-016` chỉ mở touch area sang `indicators.py`. Chỉ thị mở chu kỳ nói thẳng: không mở
  `WP-C1`.
- Rủi ro đã có số hiệu: **RSK-002** (mức cao), và biện pháp giảm thiểu đã được đặt tên sẵn
  là **WP-C4** — "Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS)".
- Roadmap đã lường trước đúng tình huống này: WP-A4 § Blocks ghi *"WP-C4 (không khoá parity
  vào hành vi sắp đổi)"*, và WP-C4 được xếp lịch SAU WP-A4 chính vì lý do đó.

`REVIEW_PROTOCOL.md`: *"OUT_OF_SCOPE → route to the appropriate owner/capability.
OUT_OF_SCOPE does not mean 'new task'."* Owner đã tồn tại → **số task ID mới = 0**.

Không BLOCKING ở chu kỳ này: app web nằm sau cổng verdict (Impl Plan §9) và verdict chưa
tồn tại (T-06 chưa chạy), nên chưa có đường để lệch này chạm quyết định thật.

---

## 4. `DEFERRED_BY_MINIMAL_FIX` — khai báo điều đã CỐ Ý không làm

`CAPABILITY_MODEL.md` § Minimal Fix đòi khai báo tường minh; không khai là khiếm khuyết về
**chất lượng khai báo** (`DELIVERY_LOOP.md` §II.7).

    DEFERRED_BY_MINIMAL_FIX
    Owner:        CAP-DATA / WP-A4
    Implemented:  Neo chỉ mục daily vào lịch ngày liên tục. Cửa sổ nào phủ ngày thiếu ->
                  NaN -> DEGRADED/INVALID qua score.invalid_mask sẵn có.
    Intentionally deferred:
                  Ngữ nghĩa "cửa sổ N ngày có một ngày khuyết" cho nhóm cửa sổ DÀI —
                  ma200 (200), high365 / percentile365 (365), ethbtc_percentile180 (180),
                  volume_ratio (90). Bản sửa chọn NaN (fail-closed). Một cách đọc khác —
                  "tính trên các ngày HỢP LỆ trong cửa sổ lịch N ngày" — KHÔNG được cài đặt.
    Reason:       Cách đọc thứ hai là một QUYẾT ĐỊNH ĐẶC TẢ, không phải một bản sửa cài
                  đặt. `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` §II.4 đã tách
                  sẵn phần dư SPEC_AMBIGUITY (ma200, adr30, rsi14, VR, ETHBTC_Percentile180)
                  và route sang CAP-SPEC / WP-D2. Chỉ thị mở chu kỳ §2 cấm kéo phần đó vào
                  đây. NaN cũng là lựa chọn có chỗ dựa trong spec: BT §2 đòi warm-up
                  "365 ngày HỢP LỆ", và BT §18 đòi kết cục DEGRADED/INVALID.
    Cost measured (không suy luận):
                  Một ngày daily thiếu -> 31 ngày INVALID (đúng cửa sổ adr30) + 169 ngày
                  DEGRADED trên dataset 2020. Vốn BASE 600.0 và SMART 520.0 vẫn giải ngân
                  ĐỦ (ST §9 [F3]); CRASH/OPPORTUNITY về 0 vì oscore thấp hơn — đúng chiều
                  bảo thủ mà CHECK-A4-06 đã khoá. Escalation trigger "engine dừng phần lớn
                  thời gian" KHÔNG kích hoạt (INVALID 8,5%).
    Re-trigger:   Khi WP-D2 chốt đơn vị và ngữ nghĩa khuyết cho nhóm cửa sổ dài; hoặc khi
                  T-06 trên dữ liệu thật cho thấy bóng DEGRADED làm hỏng một cửa sổ gate.
    Evidence:     CHECK-A4-11; scratchpad/shadow_profile.py; scratchpad/decision_regression.py

---

## 5. Những gì đã soát mà KHÔNG thành finding

| Đã soát | Kết quả |
|---|---|
| DataFrame rỗng / một hàng | không ném lỗi; trả đúng hình dạng `(0,18)` / `(1,18)` |
| `wilder_rsi` chuỗi rỗng / toàn `NaN` / có `inf` | không ném lỗi; `inf` thành biên dải (fail-closed, tốt hơn trước — trước đây `inf` đầu độc toàn bộ phần đuôi) |
| BTC thiếu ngày mà ETH đủ | **không** sinh giá trị hữu hạn sai ở cột nào |
| Tác động hồi tố | 896 ngày TRƯỚC ngày thiếu khớp **từng bit** trên mọi cột — bản sửa không sửa quá khứ |
| Hệ validity thứ hai | không có: `indicators.py` không thêm trường trạng thái nào; INVALID vẫn đi qua `score.REQUIRED_DAILY_INDICATORS` |
| `MAX_MISSING_RATIO` | KHÔNG đổi (`= 0.01`), không hạ về 0, không nới |
| Chữ ký hàm public | `compute_daily_indicators`, `wilder_rsi` giữ nguyên chữ ký |
| `dataset_hash` / `manifest_hash` | không đổi (không chạm `data/`) |
| Test cũ bị nới/skip | `git diff --stat -- tests/` **rỗng**; `grep skip\|xfail tests/*.py` **rỗng** |
| Hiệu năng | full suite trước 232 test / sau 286 test, thời gian cùng bậc (~16 phút) |

---

## 6. Verdict

    PASS -> ELIGIBLE_FOR_FREEZE

Không BLOCKING finding nào còn lại với đường sản xuất hiện tại.

Theo `STATE_AUTHORITY.md`, verdict này là **advisory**: reviewer ghi nhận, KHÔNG tự viết
`FROZEN`, và KHÔNG tự đổi budget hay gate. Việc đưa `WP-A4` về `DONE` được thực hiện theo
`DEC-016` (chủ dự án đã phê duyệt trước phương tiện thi hành và điều kiện đóng).

Nhắc lại giới hạn ở §0: đây là E1 + dò đối kháng, **không phải E2**. `CHECK-A4-09` vẫn
`NOT_TESTED` và vẫn là RECOMMENDED.
