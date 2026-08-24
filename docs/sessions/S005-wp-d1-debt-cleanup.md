# SESSION HANDOFF — S005

Session ID:
S005

Task:
WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả (F-028, F-029, F-031, F-034)

Task Mode:
MAJOR (đủ điều kiện MICRO nhưng nâng lên MAJOR theo ghi chú frozen của file task —
gom 3 module, hai hạng mục chạm mã đường găng official run, cần REQUIRED check có bằng chứng)

Project Profile:
PRODUCT

Status:
DONE — 6/6 REQUIRED check PASS (E1 toàn bộ). Exit Criteria 6/6.

Model/Effort thực thi:
Tier B (Sonnet) / medium — xác nhận lại bằng `routing_engine.py` tại phiên:
D1 R1 B1 A1 X1 → model_score 1.0 → B; U1 V1 H1 C1 F1 → effort_score 1.0 → medium;
không floor nào kích hoạt (category `none`); khớp roadmap; `validate_routing.py` PASS
(17 file MAJOR, 0 override).

Môi trường:
Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1
(trùng bộ phiên bản các phiên trước — kết quả so sánh được).

Base commit khi mở phiên: `1f4c2b7` (WP-A7 DONE).

## Result

**WP-D1 = DONE.** Bốn khoản nợ kỹ thuật đóng đúng ràng buộc định nghĩa của gói ("kết quả mô
phỏng không được đổi"): Ready Gate xác nhận lại (12/12) → baseline E0/E1 tái hiện đủ 4 finding
tại HEAD hiện tại → kiểm tra rủi ro hành vi bắt buộc (không finding nào chạm OSCORE/ladder/
capital/execution/backtest/gate/verdict) → test-first 4 test viết TRƯỚC fix (4 FAIL đúng kỳ
vọng) → remediation tối thiểu trong `engine.py`/`ladders.py`/`benchmarks.py` → 4/4 test PASS
→ impact BEFORE/AFTER trên dataset tổng hợp cố định chứng minh **toàn bộ 543 purchase record
trùng khớp bit-for-bit**, chỉ bộ đếm chẩn đoán `cooldown_override` đổi (35→31 sự kiện — đúng
ngoại lệ đã khai báo) → toàn bộ suite **99/99 PASS** → Completion Gate 6/6 PASS.

## Ready Gate (xác nhận lại khi mở task — 2026-08-24)

Routing tái xác nhận bằng `routing_engine.py` (Tier B/Sonnet/medium, không floor, không
warning); `validate_routing.py` PASS; T-04 vẫn DONE; git status sạch tại HEAD `1f4c2b7`;
không nhánh remote nào đụng scope WP-D1 (`engine.py`, `ladders.py`, `benchmarks.py`).

## Baseline E0/E1 — tái hiện TRƯỚC khi sửa (HEAD 1f4c2b7)

- **F-028**: `engine.py:504-505` (trước fix) `month_end_ts = ts + 31 * DAY`, gán cho
  `Ladder.expires_at` của Smart ladder — sai nghĩa. Xác nhận field KHÔNG được đọc cho SMART:
  `expire_smart_ladders()` (dòng 218-222) xác định hết hạn qua phát hiện month rollover
  (`month_key != cur_month`), không đọc `.expires_at`; field chỉ được đọc ở nhánh
  `lad.type == "OPPORTUNITY"` (dòng 584-585).
- **F-029**: `ladders.py:137-139` `ladder_completed()` coi `PARTIALLY_FILLED` là trạng thái
  kết thúc — mâu thuẫn `OPEN_ZONE_STATUSES` (đã coi nó là mở) và ST §8. Grep xác nhận:
  zero caller trong `src/`, `tests/`, `webapp/`; đồng thời `PARTIALLY_FILLED` hiện KHÔNG
  reachable ở bất kỳ đường code thật nào (không nơi nào gán trạng thái này).
- **F-031**: `engine.py:558-582` (trước fix) `counters["cooldown_override"][regime] += 1`
  bên trong vòng `for z in candidates:` — tăng MỘT LẦN CHO MỖI ZONE cùng cycle thay vì một
  lần cho sự kiện. Grep xác nhận counter chỉ dùng trong output chẩn đoán `res.counters`,
  KHÔNG được `gates.py`/`verdict.py`/`metrics.py`/`reporting.py`/`diagnostics.py` đọc.
- **F-034**: `benchmarks.py:29-41` `_noon_candles` — nhánh `pass` chết, zero caller.

Cả 4 finding tái hiện đúng như S001 mô tả, không finding nào "biến mất" dù `engine.py` đã
bị WP-A3/WP-A7 sửa đáng kể ở các vùng khác.

## Kiểm tra rủi ro hành vi (bắt buộc trước remediation)

Xác nhận KHÔNG có đường đọc nào ảnh hưởng OSCORE / Buy Zone-Ladder / capital accounting /
execution behavior / backtest result / Gate 1-2-3 / verdict / dataset interpretation:
- F-028: field write-only đối với SMART (chỉ OPPORTUNITY đọc) → an toàn tuyệt đối.
- F-029: zero caller → an toàn tuyệt đối bất kể sửa gì.
- F-031: chỉ xuất hiện trong `res.counters` (diagnostic output); đây CHÍNH LÀ ngoại lệ được
  CHECK-D1-03/05 cho phép đổi giá trị tường minh.
- F-034: zero caller → an toàn tuyệt đối.

Không finding nào rơi vào điều kiện `SCOPE/RISK ESCALATION` của chỉ thị S005 mục 7.

## Test-first (4 test, FAIL trước fix → PASS sau fix)

File mới: `tests/test_wp_d1_debt_cleanup.py`. Chạy tại HEAD `1f4c2b7` (TRƯỚC remediation):
**4/4 FAIL đúng cách**:

| Test | Nội dung | FAIL trước fix | PASS sau fix |
|---|---|---|---|
| `test_f028_smart_expires_at_matches_accounting_month_end` | expires_at đúng cuối accounting month (dùng tháng 30 ngày — April — để loại trừ trùng hợp với công thức cũ trên tháng 31 ngày như March) | lệch đúng 86400s (1 ngày) | khớp `pytest.approx` |
| `test_f029_ladder_completed_partially_filled_not_terminal` | PARTIALLY_FILLED không còn là trạng thái kết thúc (4 kịch bản) | `assert True is False` | 4/4 đúng |
| `test_f031_cooldown_override_counts_once_per_event_not_per_zone` | một sự kiện, hai zone cùng cycle → đếm đúng 1 lần | `2 == 1` fail | `== 1` |
| `test_f034_noon_candles_removed` | hàm bị xoá | `hasattr == True` | `hasattr == False` |

Kịch bản F-031 (tự dựng, xác nhận bằng probe trước khi viết test chính thức): Smart ladder
3 zone (S0=100, S1≈94.6, S2≈89.2, anchor=100, spacing≈0.06). Day2 dip 99 → trigger MỘT MÌNH
S0 → exec → mở cooldown 48h, `last_exec_price≈100`. Day3 dip 85 trigger CẢ S1 và S2; candle
đầu day3 (open=100, kế thừa close day2) chưa đủ chiết khấu 7% → hai zone giữ TRIGGERED;
candle kế (open=90, đủ chiết khấu) → `in_cooldown=True` và `override_ok=True` cho CẢ HAI
zone TRONG CÙNG một cycle (xác nhận: hai dòng `COOLDOWN_OVERRIDE` trong decision_log cùng
`ts=1677777300.0`).

## Remediation (tối thiểu, đúng scope)

- **F-028** (`engine.py`): thay `ts + 31 * DAY` bằng
  `lts.replace(day=1) + pd.DateOffset(months=1)` quy đổi lại epoch UTC — tính đúng mốc đầu
  tháng kế tiếp theo giờ local, dùng biến `lts` đã có sẵn trong scope vòng lặp chính.
  Field vẫn giữ trong dataclass `Ladder` (dùng chung với OPPORTUNITY) — không xoá.
- **F-029** (`ladders.py`): bỏ `"PARTIALLY_FILLED"` khỏi tập trạng thái "đã kết thúc" trong
  `ladder_completed()`.
- **F-031** (`engine.py`): thêm cờ cục bộ `override_counted_this_cycle` (reset đầu mỗi cycle
  trong khối bước 14), `counters["cooldown_override"][regime] += 1` chỉ khi cờ còn False,
  set cờ True ngay sau đó. `log(ts, "COOLDOWN_OVERRIDE", ...)` GIỮ NGUYÊN mỗi zone (không
  thuộc phạm vi finding).
- **F-034** (`benchmarks.py`): xoá nguyên hàm `_noon_candles` (13 dòng). Import
  `TZ_OFFSET, NOON, DAY` ở đầu file vẫn dùng bởi các hàm khác — không dọn thừa.

Không refactor rộng, không đổi tên hàng loạt, không chạm gì ngoài 4 hạng mục.

## Impact BEFORE → AFTER (cùng dataset tổng hợp cố định)

Đo bằng `tests/wp_a3_impact_tool.py` (công cụ đã commit từ WP-A3), cùng
`SYNTH_SEED` mặc định, cửa sổ 2019-01-01→2026-06-01. BEFORE chạy qua git worktree tại
`1f4c2b7` với `--src` (provenance assert); AFTER chạy trên working tree hiện tại.

So sánh 66 trường phẳng của JSON output — **khác biệt DUY NHẤT ngoài metadata**
(`tag`, `code_path`):

| Trường | BEFORE | AFTER |
|---|---|---|
| `counters.cooldown_override.CRASH` | 12 | 9 |
| `counters.cooldown_override.NORMAL` | 7 | 6 |
| `counters.cooldown_override.STRESSED` | 16 | 16 (không đổi) |
| `counters.cooldown_override.RECOVERY` | 0 | 0 (không đổi) |
| **Tổng sự kiện** | **35** | **31** |

**Mọi thứ khác trùng khớp bit-for-bit**: `eth_total` = 21.6370346047919 cả hai phía;
`purchases_count` = 543 cả hai; **so sánh bằng `==` python toàn bộ danh sách 543 purchase
record (ts/source/nominal/reason) → `True` tuyệt đối**; `final_pools` (BASE/SMART/
OPPORTUNITY: available/reserved/deployed/total), `label_transitions`, `state_transitions`,
`smart_ladders_created`, `opp_ladders_created`, `crash_ladders_created`,
`releases_count_by_reason`, `releases_total_by_reason`, `avg_cash_ratio_vs_contributed`,
`daily_limit_blocks`, `stuck_crash_reserve_at_end` — tất cả giống hệt.

Đây là bằng chứng mạnh hơn yêu cầu tối thiểu của CHECK-D1-05 (không chỉ metric tổng hợp mà
cả toàn bộ chuỗi purchase record, đến từng bản ghi). Benchmark module: F-034 chỉ xoá dead
code không được gọi bởi bất kỳ hàm benchmark A–D/F/G nào — không cần đo lại riêng.

Files: `wp_a3_impact_WP_D1_{BEFORE,AFTER}.json`, `wp_a3_purchases_WP_D1_{BEFORE,AFTER}.json`
(lưu tại scratchpad phiên).

## Full regression

`python -m pytest tests/` → **99 passed in 431.57s (0:07:11)** — 0 failed, 0 skipped, exit
code 0 (95 test trước WP-D1 + 4 test mới). Không test nào bị sửa/nới lỏng/xoá.

## Governance validators

`validate_structure`/`validate_project_state`/`validate_routing`/`validate_easy_roadmap`/
`validate_evidence`/`validate_task_completion` — tất cả PASS. **Giới hạn đã biết** (không
phải bằng chứng chất lượng mới): `validate_evidence`/`validate_task_completion` quét glob
`TASK-*.md`, không khớp quy ước đặt tên `WP-*.md` của repo này → PASS trên **tập rỗng**
(0 REQUIRED PASS record, 0 DONE task được kiểm) — tồn đọng tooling từ S003, ngoài scope
WP-D1, đã ghi trong danh sách chờ chủ dự án tại PROGRESS.

## Finding/risk mới

Không phát hiện finding hay risk mới nào trong phiên này.

## Key Decisions

1. F-028: giữ field `expires_at` trong dataclass (dùng chung OPPORTUNITY), chỉ sửa giá trị
   gán cho SMART — không chọn phương án "bỏ trường" vì sẽ phải đổi type hint/callers khác.
2. F-031: granularity "một sự kiện" = một cycle (một vòng lặp thời gian chính của engine),
   khớp cách `in_cooldown`/`override_ok` được tính một lần mỗi cycle và khớp diễn giải tự
   nhiên nhất của BT §16/§21 ("tần suất cooldown override theo regime").
3. Không đổi `log(ts, "COOLDOWN_OVERRIDE", ...)` — log chi tiết theo zone vẫn đúng nghĩa,
   chỉ counter tổng hợp mới cần sửa.

## Git status cuối phiên

Working tree sạch sau commit cuối. Hai commit của S005:
- `2af59b8` — implementation + evidence CHECK-D1-01..05 (WIP, CHECK-D1-06 lúc đó đang chờ
  full suite chạy nền).
- Commit thứ hai (sau file này) — CHECK-D1-06 PASS, Status DONE, PROGRESS cập nhật.

## Files Next Agent Should Read

1. `PROJECT/PROJECT_PROGRESS.md`
2. `docs/tasks/WP-D1-no-ky-thuat-khong-anh-huong-hanh-vi.md` (evidence 6 check)
3. File task của work package được chọn tiếp theo, dưới `docs/tasks/`
