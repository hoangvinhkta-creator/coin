# S010 — CAP-DATA REPAIR CYCLE #1 (`F-S009-01`)

Ngày:
2026-09-01

Loại phiên:
Repair cycle của một capability đã có. **KHÔNG** mở gói mới, **KHÔNG** tạo task ID mới.

Thi hành:
`DEC-016` / `OD-DATA-01` (phương tiện) + `DEC-017` / `OD-DATA-02` (risk & budget).

Kết quả một dòng:

    REPAIR RESULT = PASS

---

## 0. Branch authority & môi trường

```
branch            = claude/cap-data-calendar-indicators-51fvyx
default branch    = main (resolved, not assumed)
base SHA          = cb75f9d1fb139f4c5daae063e754245998819f22   (== origin/main, khớp Expected HEAD)
ahead of default  = 0 commit khi bắt đầu
integration       = INTEGRATION_DECISION_REQUIRED = NO
tracked worktree  = CLEAN khi bắt đầu
production diff   = EMPTY khi bắt đầu
```

`branch_authority_check.sh` báo `FAIL — attached branch has no upstream` ở lần chạy đầu.
Nguyên nhân là branch cục bộ chưa có upstream (remote branch chưa tồn tại), **không** phải
branch sai hay state cũ: base SHA trùng khớp `origin/main` và đúng Expected HEAD của chỉ
thị. Upstream được tạo bằng `git push -u` ở cuối phiên; kết quả chạy lại ghi ở §9.

Môi trường bằng chứng — **trùng khớp `pyproject.lock` từng dòng**:
Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · requests 2.33.1 ·
pytest 9.1.1 · certifi 2026.2.25 · charset-normalizer 3.4.6 · idna 3.11 · iniconfig 2.3.0 ·
packaging 24.0 · pluggy 1.6.0 · Pygments 2.21.0 · python-dateutil 2.9.0.post0 · six 1.16.0 ·
urllib3 2.6.3. Không có `ENVIRONMENT_REVERIFY_REQUIRED`.

---

## 1. Trạng thái WP-A4

    TRƯỚC:  DONE   (9/9 REQUIRED PASS tại S009)
    TRONG:  IN_PROGRESS  (mở chu kỳ sửa theo DEC-016)
    SAU:    DONE   (10/10 REQUIRED PASS)

Chín check FROZEN gốc và `CHECK-A4-10` giữ nguyên câu chữ và ngữ nghĩa. Bổ sung duy nhất
của chu kỳ này là **`CHECK-A4-11`**, do chủ dự án phê duyệt TRƯỚC khi implementation bắt
đầu (`DEC-016` §4). Không check nào bị hạ, gộp hay nới. Không phát sinh
`LEGACY_GATE_COMPATIBILITY_REQUIRED`. Evidence cũ của S009 **không bị mất**: mọi khối
Evidence của CHECK-A4-01…10 còn nguyên trong task file.

---

## 2. Budget `CAP-DATA` — đo bằng lệnh

```
git diff --shortstat cb75f9d..ef8cdbb -- src/eth_dca_os webapp pyproject.toml pyproject.lock
  -> 1 file changed, 74 insertions(+), 5 deletions(-)          = REPAIR CYCLE #1

git diff --shortstat 06b381c..HEAD    -- src/eth_dca_os webapp pyproject.toml pyproject.lock
  -> 6 files changed, 356 insertions(+), 41 deletions(-)       = tích luỹ CAP-DATA
```

    TRƯỚC:  allowed 2 · used 0 · remaining 2
    SAU:    allowed 2 · used 1 · remaining 1
    OWNER_EXTENSION = KHÔNG CẦN

Budget KHÔNG reset. `CAP-PROV` không đụng tới (allowed 2 / used 2 / remaining 0).
Ghi ở `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.1 và §4.2.

---

## 3. Tái lập BEFORE (test-first, đường sản xuất bình thường)

`fetch_all` (stub CHỈ thay lớp HTTP) → `build_lineage` → `official_eligibility` →
`Prepared` → `compute_daily_indicators`. Không sửa tay artifact, không monkeypatch
eligibility, không input thù địch.

`--start 2019-01-01 --end 2020-01-01`, archive thiếu đúng ngày 2019-07-15, đọc tại
2019-07-20:

| | FULL (kỳ vọng) | GAP (thực tế BEFORE) | NaN? |
|---|---|---|---|
| `return7` | 6.98993449431e-05 | **7.98857633582e-05** | False |
| `ethbtc_return30` | −3.33066907388e-16 | −1.11022302463e-16 | False |
| `adr30` | 9.98646841002e-06 | 1.03194055464e-05 | False |
| `rsi14` | 99.9018663068 | 99.8996490166 | False |
| `ma200` | 130.378014 | 130.383227 | False |

    validity state = DEGRADED · oscore = 9.928762762751692 · invalid_mask = False
    official state = Prepared.official_eligible True ('verified')
    ngày 2019-07-15 KHÔNG có trong index indicators

Năm indicator sai, không cái nào tự khai, dataset vẫn official. Đúng `F-S009-01`.

---

## 4. Root cause

`compute_daily_indicators` lập chỉ mục theo **các ngày QUAN SÁT ĐƯỢC**, rồi tính mọi cửa sổ
theo **vị trí hàng**: `np.roll(close, 7)` lấy hàng `i-7`, `rolling(365)` lấy 365 HÀNG. Khi
một ngày lịch vắng mặt, chỉ mục co lại — hàng `i-7` là ngày `D-8` — nhưng phép tính vẫn
chạy trót lọt và trả một số **hữu hạn**. `score.invalid_mask` chỉ bắt giá trị không hữu hạn
nên không thấy gì.

Đo trực tiếp: tại 2019-07-20 phần tử `i-7` của chuỗi có gap là **2019-07-12**, trong khi
lịch đòi **2019-07-13**.

---

## 5. Bản sửa tối thiểu đã chọn

Hướng **A** của chỉ thị §6 ("reindex calendar daily series trước rolling/shift"), một điểm
sửa duy nhất trong **một file production**:

- `indicators._calendar_index` — chỉ mục daily neo vào lịch ngày UTC liên tục phủ
  `[min, max]` quan sát được. Ngày thiếu hiện ra thành một hàng `NaN` thật.
- `wilder_rsi` — tính riêng từng dải ngày lịch liên tục; hồi quy Wilder không bắc qua được
  một ngày vắng mặt nên warm-up lại sau mỗi lần đứt.
- `_rolling_percentile_of_last` — trả `NaN` khi cửa sổ thiếu ngày, thay vì âm thầm đếm
  `NaN` là "không thấp hơn".

Không hard-code riêng `return7`: một sửa đổi ngữ nghĩa ở tầng chỉ mục xử lý cả nhóm
indicator cùng defect class. Không dựng framework mới, không thêm trường trạng thái nào,
không dựng hệ validity thứ hai — INVALID vẫn đi qua `score.REQUIRED_DAILY_INDICATORS`.

---

## 6. AFTER — cùng lệnh, cùng stub

| | FULL | GAP (AFTER) | |
|---|---|---|---|
| `return7` | 6.98993449431e-05 | 6.98993449431e-05 | **ĐÚNG theo lịch** |
| `ethbtc_return30` | −3.33066907388e-16 | −3.33066907388e-16 | **ĐÚNG theo lịch** |
| `adr30` | 9.98646841002e-06 | `NaN` | cửa sổ phủ ngày thiếu |
| `rsi14` | 99.9018663068 | `NaN` | dải đứt, warm-up lại |
| `ma200` | 130.378014 | `NaN` | cửa sổ phủ ngày thiếu |

    phần tử i-7 của chuỗi CÓ GAP = 2019-07-13 == lịch đòi 2019-07-13
    validity state = INVALID · oscore = NaN · invalid_mask = True
    ngày 2019-07-15 CÓ trong index indicators (hàng NaN)

Không còn giá trị hữu hạn sai nào.

---

## 7. CASE A–H

`tests/test_wp_a4_calendar_indicator_semantics.py` — **54 test, PASS toàn bộ**. Bảng chi
tiết ở `CHECK-A4-11`. Tóm tắt: A không regression · B không finite-wrong · C không invalid
sai phạm vi (khoá cả hai phía của bóng) · D multi-day gap đúng · E biên đầu cửa sổ, khoá
off-by-one `D-7`/`D-8` và `D-30`/`D-31` · F biên cuối/vùng hiện tại · G positive control
bit-identical · H tích hợp `Prepared`/`invalid_mask`.

---

## 8. Non-regression ở tầng quyết định

Dataset **SẠCH**, `run_engine` thật, cùng seed/parquet/config, cửa sổ 2020:

| | BEFORE | AFTER |
|---|---|---|
| `eth_total` | 2.1967521311211984 | 2.1967521311211984 |
| `n_purchases` | 66 | 66 |
| nominal BASE / SMART / CRASH / OPPORTUNITY | 600.0 / 520.0 / 14.1027503435 / 0.2633261223 | y hệt |
| triggered / executed / base_early | 18 / 18 / 2 | 18 / 18 / 2 |
| cooldown_override | STRESSED 4 | STRESSED 4 |
| nhãn regime (CRASH/NORMAL/STRESSED) | 140 / 169 / 57 | 140 / 169 / 57 |
| `data_quality` | GOOD 366 | GOOD 366 |
| tổng `oscore` | 8509.33685713 | 8509.33685713 |

**Không trôi một chữ số nào.** Ngoài ra: 896 ngày TRƯỚC ngày thiếu khớp từng bit trên mọi
cột — bản sửa không có tác dụng hồi tố.

Dataset **CÓ GAP** (bỏ 2020-06-15): BEFORE 365 GOOD / 0 INVALID / ngày thiếu vô hình →
AFTER 31 INVALID (2020-06-15…2020-07-15, đúng cửa sổ `adr30`) / 169 DEGRADED / 166 GOOD;
nominal BASE 600.0 và SMART 520.0 **không đổi** (ST §9 [F3]).

`MAX_MISSING_RATIO` **KHÔNG đổi** (`= 0.01`), không hạ về 0, không nới.

---

## 9. Regression & validators

```
python -m pytest -q
  BEFORE chu kỳ: 232 PASS / 0 FAIL / 0 SKIP / 0 XFAIL
  SAU   chu kỳ: 286 PASS / 0 FAIL / 0 SKIP / 0 XFAIL     (232 + 54 test mới)

git diff --stat -- tests/     -> (rỗng)   không file test cũ nào bị sửa
git status --short tests/     -> ?? một file mới duy nhất
grep -rn "skip|xfail" tests/  -> (rỗng)
```

Validators (chạy tại phiên này):

| Validator | Kết quả | Ghi chú |
|---|---|---|
| `branch_authority_check.sh` | xem §0 | FAIL ban đầu chỉ vì thiếu upstream; base SHA đúng |
| `validate_routing.py` | **PASS** | 17 MAJOR task file, 0 manual override |
| `validate_governance.py` | **PASS** | 5 hard-stop · 26 source invariant · 2 budget lineage root · **17 hardening item** · 13 production path row · 20 task file |
| `validate_project_state.py` | **PASS** | |
| `validate_structure.py` | **PASS** | 27 required path |
| `sync_easy_roadmap.py` | **PASS** | ghi lại `PROJECT/LO_TRINH_DE_HIEU.md` (file SINH, không sửa tay) |
| `validate_easy_roadmap.py` | **PASS** | |
| `validate_evidence.py` | PASS **nhưng VÔ NGHĨA** | "Checked **0** REQUIRED PASS evidence record" |
| `validate_task_completion.py` | PASS **nhưng VÔ NGHĨA** | "Checked **0** DONE task" |

Hai dòng cuối **không được đọc thành bằng chứng**. Cả hai glob `TASK-*.md` trong khi quy ước
repo là `WP-*.md`, nên chúng quét tập RỖNG. `STATE_AUTHORITY.md` § Vacuous Validation:
*"Checked 0 records is not a meaningful PASS."* Chính `validate_governance.py` cũng tự báo
rủi ro này (`task_files_matching_legacy_glob = 0`). Đã có số hiệu: `HARDENING_BACKLOG.md`
**H-08**, và là mục #5 trong danh sách "Cần chủ dự án quyết định". Phiên này KHÔNG sửa H-08
(chỉ thị §16 cấm) và KHÔNG dùng hai dòng đó làm chứng cứ cho bất kỳ mệnh đề nào.

---

## 10. Batch review bắt buộc

Effective Risk `CAP-DATA` = HIGH (`DEC-017`) → `RISK_MODEL.md` buộc batch review cuối phiên.
Đã chạy, trả **toàn bộ finding trong một lượt**:

    BLOCKING     = 0
    HARDENING    = 2   H-16 (sai số ULP trên dataset có gap), H-17 (ngày trùng lặp -> ValueError)
    OUT_OF_SCOPE = 1   F-S010-03 parity JS/Python -> CAP-WEBAPP / WP-C4 (rủi ro RSK-002 đã đăng ký)
    DEFERRED_BY_MINIMAL_FIX = 1   ngữ nghĩa "cửa sổ N ngày khuyết một ngày" cho nhóm cửa sổ dài
    Verdict      = PASS -> ELIGIBLE_FOR_FREEZE

Chi tiết: `docs/reviews/S010-batch-review-calendar-indicator.md`.

Giới hạn phải nói rõ: đây là **E1 + một lượt dò đối kháng có ghi lệnh chạy**, KHÔNG phải E2.
Dự án là solo, không có reviewer thứ hai là con người — cùng hạn chế đã ghi ở `CHECK-A4-09`,
mục này vẫn `NOT_TESTED` và vẫn RECOMMENDED.

---

## 11. Anti-proliferation — đo trên registry, không tự khai

Đo bằng `governance/scripts/governance/task_registry_snapshot.sh`, so BEFORE (`cb75f9d`)
với AFTER — **không tự khai "guard respected = YES"** (`CAPABILITY_MODEL.md` §II.9):

```
BEFORE (cb75f9d):  count_task_files = 20   count_roadmap_task_ids = 29
AFTER  (HEAD):     count_task_files = 20   count_roadmap_task_ids = 29
```

    SET A (registry) BEFORE == AFTER
    SET B (task spec files) BEFORE == AFTER
    new_registered_task_ids = 0
    proposals_created       = 0
    owner_assignment_required_entries_added = 0
    WP-A1 / CAP-PROV    = KHÔNG đụng (allowed 2 / used 2 / remaining 0)
    WP-A5, WP-A6, WP-C1 = KHÔNG mở
    T-06                = KHÔNG chạy
    H-01…H-15           = KHÔNG sửa (H-08, H-14, H-15 không mở)

---

## 12. NEXT SMALLEST DATA ACTION

**Không có hành động DATA nào còn mở trên đường găng.** `CAP-DATA` đã đóng cả
`F-E2A1R3-05` lẫn `F-S009-01`; `WP-A4` DONE với 10/10 REQUIRED.

Hành động DATA nhỏ nhất còn lại, theo thứ tự chi phí tăng dần — cả ba đều **cần chủ dự án
quyết**, phiên này không tự mở:

1. **Không làm gì thêm ở `CAP-DATA`.** Chuyển sang mắt xích tiếp theo của đường găng:
   `WP-A6` (đã đủ dependency: WP-A3 ✅ WP-A4 ✅ WP-A7 ✅) hoặc `WP-A5`. *Khuyến nghị.*
2. Nếu chủ dự án muốn E2 thật cho `CAP-DATA`: mở `CHECK-A4-09` (RECOMMENDED, hiện
   `NOT_TESTED`) với một reviewer độc lập. Tiêu một vòng E2, **không** tiêu repair cycle.
3. Nếu bóng DEGRADED của nhóm cửa sổ dài (`ma200`/`high365`/`percentile365`, 200–365 ngày
   cho mỗi ngày daily thiếu) bị coi là quá rộng: đó là câu hỏi ĐẶC TẢ, thuộc `WP-D2`
   (`CAP-SPEC`), không thuộc `CAP-DATA` — xem khối `DEFERRED_BY_MINIMAL_FIX`.

`GATE-A` còn chặn bởi: **WP-A1** (IN_PROGRESS, `CAP-PROV` remaining = 0 → cần quyết định
của chủ dự án), **WP-A5** (READY), **WP-A6** (READY). `T-06` còn chặn thêm bởi `BLK-001`.
