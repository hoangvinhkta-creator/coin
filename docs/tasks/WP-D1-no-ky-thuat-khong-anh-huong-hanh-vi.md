# WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả

## Metadata
Status:
DONE

Phase:
Phase 6 — Lớp D: hoãn được / tuỳ chọn

Task Mode:
MAJOR

Lớp (RCP-001):
D — DEFERRED / OPTIONAL

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 1
R: 1
B: 1
A: 1
X: 1
U: 1
V: 1
H: 1
C: 1
F: 1

Routing Categories:
none

Primary Agent Tier:
B

Primary Effort:
medium

Model Routing Score:
1.0

Effort Routing Score:
1.0

Applied Model Floor:
none

Applied Effort Floor:
none

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
C

Escalation Effort:
high

Difficulty:
1/4

Risk:
1/4

Blast Radius:
1/4

Project Profile:
PRODUCT

## Ghi chú về Task Mode

Điểm D/R/B đều bằng 1 nên gói này **đủ điều kiện MICRO** theo `TASK_MODE_STANDARD.md`. Vẫn chọn
MAJOR vì: (a) nó gom bốn hạng mục ở ba module khác nhau, (b) hai trong bốn hạng mục chạm mã mà thuật
toán official run phụ thuộc, và (c) ràng buộc định nghĩa của gói — **không được đổi hành vi** — cần
một REQUIRED check có bằng chứng, thứ mà checklist MICRO không bắt buộc. `TASK_MODE_STANDARD.md` cho
phép nâng lên MAJOR; nó chỉ cấm ép MICRO vào khuôn MAJOR khi không cần.

## Objective

Dọn bốn khoản nợ kỹ thuật đã được S001 xác định là **không ảnh hưởng hành vi hiện tại**, để chúng
không trở thành cái bẫy cho người đọc mã hoặc cho một thay đổi trong tương lai.

Ràng buộc định nghĩa của gói: **kết quả mô phỏng không được đổi**. Nếu một hạng mục làm đổi kết quả,
hạng mục đó **không thuộc gói này**.

## Đóng finding

| ID | Nội dung | Vì sao hiện chưa gây hậu quả |
|---|---|---|
| F-028 | `Ladder.expires_at` của Smart ladder đặt `ts + 31 ngày`, không phải cuối accounting month | Trường **không được dùng**; expiry do engine xử lý riêng |
| F-029 | `ladder_completed()` coi `PARTIALLY_FILLED` là trạng thái kết thúc, mâu thuẫn ST §8 | Hàm hiện **không được engine gọi** |
| F-031 | Bộ đếm cooldown override đếm theo **zone**, không theo **sự kiện** override | Chỉ ảnh hưởng số liệu chẩn đoán |
| F-034 | `_noon_candles` chứa nhánh `pass` không tác dụng; hàm cũng không được dùng | Dead code |

## Scope

- `src/eth_dca_os/engine.py` — `expires_at` của Smart ladder; bộ đếm cooldown override
- `src/eth_dca_os/ladders.py` — `ladder_completed()`
- `src/eth_dca_os/benchmarks.py` — xoá `_noon_candles`
- `tests/`

## Out of Scope

- Bất kỳ thay đổi nào làm đổi kết quả mô phỏng
- Partial fill ở tầng sản phẩm (WP-C3) — nhưng ngữ nghĩa "hoàn tất" phải nhất quán với gói đó
- Refactor rộng, đổi tên hàng loạt, dọn dẹp ngoài bốn hạng mục trên
- Sửa các finding lớp A/B/C

## Dependencies
- T-04 (DONE)

Không phụ thuộc gói nào khác. Làm được bất cứ lúc nào.

## Blocks
- Không chặn gì

## Parallel-Safe With
- Toàn bộ gói khác. Lưu ý phối hợp: F-029 chạm ngữ nghĩa mà **WP-C3** cũng dùng

## Expected Touch Area

Allowed:
- `src/eth_dca_os/engine.py`, `ladders.py`, `benchmarks.py` — chỉ bốn hạng mục nêu trên
- `tests/`

Do not touch without Scope Expansion:
- Mọi phần khác của `src/eth_dca_os/`
- `webapp/`, `docs/spec/`

## Subtasks
- [x] D1.1 Sửa hoặc bỏ `expires_at` của Smart ladder để dữ liệu không còn sai nghĩa (F-028)
- [x] D1.2 Sửa `ladder_completed()` cho khớp ST §8 (F-029)
- [x] D1.3 Cho bộ đếm cooldown override đếm theo sự kiện (F-031)
- [x] D1.4 Xoá dead code `_noon_candles` (F-034)
- [x] D1.5 Chứng minh kết quả mô phỏng không đổi (impact tool BEFORE/AFTER, xem CHECK-D1-05)

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency (T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §8; và các quan sát F-028, F-029, F-031, F-034
- [x] Data impact được biết — `expires_at` đổi nghĩa; không có dữ liệu bền cần migrate
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S005 2026-08-24: routing tái xác nhận
      bằng `routing_engine.py` (D1 R1 B1 A1 X1 → 1.0 → Tier B; U1 V1 H1 C1 F1 → 1.0 → medium;
      không floor, không warning, khớp roadmap), `validate_routing.py` PASS (17 file);
      T-04 vẫn DONE; git status sạch, HEAD `1f4c2b7`, không nhánh nào đụng scope WP-D1

## Completion Gate

Risk = 1 → E0/E1 tuỳ loại check. Nhưng CHECK-D1-05 (không đổi hành vi) là mệnh đề định nghĩa của gói
nên **bắt buộc E1**.

### Functional

#### CHECK-D1-01 — `expires_at` của Smart ladder không còn mang giá trị sai nghĩa
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: hoặc trường mang đúng cuối accounting month, hoặc trường bị bỏ. Trong cả hai trường hợp,
test khẳng định engine vẫn xử lý expiry đúng như trước. Đóng F-028.

**Kết quả (S005):** chọn phương án "trường mang đúng cuối accounting month" (giữ field vì
`Ladder.expires_at` dùng chung cho cả OPPORTUNITY — không được xoá khỏi dataclass).
`engine.py`: thay `month_end_ts = ts + 31 * DAY` bằng tính đúng mốc đầu tháng kế tiếp theo
giờ local (`lts.replace(day=1) + pd.DateOffset(months=1)`, quy đổi lại epoch UTC). Baseline
BEFORE tái hiện: trên tháng 31 ngày (March) hai giá trị trùng nhau NGẪU NHIÊN (không phân
biệt được) — test dùng tháng 30 ngày (April 2023) để loại trừ trùng hợp; FAIL trước fix
đúng 86400s (lệch một ngày), PASS sau fix (khớp `pytest.approx`).
Hành vi expiry KHÔNG đổi: `expire_smart_ladders()` xác định hết hạn Smart bằng phát hiện
month rollover (`month_key != cur_month`), KHÔNG đọc `.expires_at` — xác nhận bằng grep
(field chỉ được đọc ở nhánh `lad.type == "OPPORTUNITY"`, engine.py) và bằng chạy thật
(`test_f028...`: `lad.status == "EXPIRED"` đúng thời điểm, không đổi so với trước).
Test: `tests/test_wp_d1_debt_cleanup.py::test_f028_smart_expires_at_matches_accounting_month_end` — PASS.

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:35Z

#### CHECK-D1-02 — `ladder_completed()` khớp Strategy §8
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `PARTIALLY_FILLED` không còn được coi là trạng thái kết thúc; phần chưa fill còn `RESERVED`
tới hết TTL. Test khẳng định trực tiếp. Đóng F-029. Ngữ nghĩa phải nhất quán với WP-C3.

**Kết quả (S005):** `ladders.py::ladder_completed()` bỏ `PARTIALLY_FILLED` khỏi tập trạng
thái được coi là "đã kết thúc" — khớp ST §8 ("Phần còn lại TIẾP TỤC ở RESERVED cho tới hết
ACTION_TTL") và khớp `OPEN_ZONE_STATUSES` (đã coi PARTIALLY_FILLED là còn mở từ trước —
mâu thuẫn nội bộ cũ nay được giải). Baseline BEFORE: hàm trả `True` sai cho ladder còn zone
PARTIALLY_FILLED. Xác nhận PARTIALLY_FILLED hiện KHÔNG reachable ở bất kỳ đường code thật
nào trong engine (grep: không nơi nào gán `z.status = "PARTIALLY_FILLED"`) — WP-C3 (partial
fill ở tầng sản phẩm) chưa triển khai, nên không có xung đột với gói đó ở thời điểm này;
ngữ nghĩa mới đã nhất quán sẵn cho khi WP-C3 hiện thực hoá partial fill.
Escalation trigger "hàm CÓ được gọi ở đâu đó" — đã kiểm tra: KHÔNG, zero caller trong
`src/`, `tests/`, `webapp/` (không kích hoạt).
Test: `tests/test_wp_d1_debt_cleanup.py::test_f029_ladder_completed_partially_filled_not_terminal`
— 4 kịch bản (còn PARTIALLY_FILLED / mọi zone kết thúc thật + có EXECUTED / mọi zone kết
thúc nhưng không EXECUTED / còn zone mở) — PASS.

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:35Z

#### CHECK-D1-03 — Bộ đếm cooldown override đếm theo sự kiện override
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test dựng ca một sự kiện override tạo action cho nhiều zone, khẳng định bộ đếm tăng đúng
một lần. Đóng F-031. Lưu ý: số liệu chẩn đoán đổi giá trị — điều này **được phép** và phải được ghi
nhận là đổi số liệu, không phải đổi hành vi.

**Kết quả (S005):** `engine.py` thêm cờ `override_counted_this_cycle` (reset mỗi cycle,
trong khối "14. chuyển TRIGGERED -> ACTION_PENDING"); `counters["cooldown_override"][regime]`
chỉ `+= 1` lần đầu tiên trong cycle khi `in_cooldown and override_ok`, các zone tiếp theo
cùng cycle không tăng thêm. `log(ts, "COOLDOWN_OVERRIDE", zone=...)` GIỮ NGUYÊN mỗi zone
(không thuộc phạm vi finding — vẫn là log chi tiết đúng nghĩa).
Kịch bản tự dựng (`test_f031...`): Smart ladder 3 zone (S0=100, S1≈94.6, S2≈89.2); Day2
dip vừa đủ trigger MỘT MÌNH S0 → exec → mở cooldown 48h, `last_exec_price≈100`; Day3 dip
sâu (85) trigger CẢ S1 và S2; candle đầu day3 (open=100) chưa đủ chiết khấu 7%
(`override_ok=False`) nên hai zone giữ TRIGGERED; candle kế (open=90, đủ chiết khấu) →
`in_cooldown=True` và `override_ok=True` cho CẢ HAI zone TRONG CÙNG MỘT cycle (xác nhận
tiền đề bằng chạy thật: hai dòng `COOLDOWN_OVERRIDE` trong decision_log cùng `ts`).
BEFORE: `sum(counters["cooldown_override"].values()) == 2`. AFTER: `== 1`.
Đổi số liệu chẩn đoán được ghi nhận rõ ở CHECK-D1-05 (impact BEFORE/AFTER trên dataset
tổng hợp: tổng sự kiện 35→31; KHÔNG có consumer nào khác đọc counter này ngoài
`res.counters` — xác nhận grep `gates.py`/`verdict.py`/`metrics.py`/`reporting.py`/
`diagnostics.py`: không match).
Test: `tests/test_wp_d1_debt_cleanup.py::test_f031_cooldown_override_counts_once_per_event_not_per_zone` — PASS.

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:35Z

#### CHECK-D1-04 — Dead code `_noon_candles` được xoá
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: hàm không còn trong `benchmarks.py`; grep chứng minh không nơi nào gọi nó. Đóng F-034.

**Kết quả (S005):** hàm `_noon_candles` (benchmarks.py, kèm nhánh `pass` chết) đã bị xoá.
`grep -rn "_noon_candles" src/ tests/ webapp/` sau khi xoá: chỉ còn match trong chính
`tests/test_wp_d1_debt_cleanup.py` (tên test + docstring) — không còn tham chiếu nào trong
mã sản phẩm. Import `TZ_OFFSET, NOON, DAY` ở đầu `benchmarks.py` vẫn dùng bởi các hàm khác
trong file (`_monthly_buy_points`, v.v.) — xác nhận không phát sinh import thừa/lint issue.
Test: `tests/test_wp_d1_debt_cleanup.py::test_f034_noon_candles_removed` — PASS
(`not hasattr(benchmarks, "_noon_candles")`).

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:35Z

### Regression

#### CHECK-D1-05 — Kết quả mô phỏng không đổi
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric của chiến lược và của toàn bộ benchmark trước–sau **trùng khớp
hoàn toàn**. Đây là mệnh đề định nghĩa gói này. Ngoại lệ duy nhất được phép là bộ đếm cooldown
override (CHECK-D1-03) — phải nêu rõ.

**Kết quả (S005):** đo bằng `tests/wp_a3_impact_tool.py` trên CÙNG dataset synth cố định
(SYNTH_SEED mặc định, cửa sổ 2019-01-01→2026-06-01) — BEFORE chạy qua git worktree tại
`1f4c2b7` (HEAD trước S005) với `--src`, AFTER chạy trên working tree hiện tại (4 fix áp
dụng). So sánh 66 trường phẳng của JSON output:
- **Khác biệt DUY NHẤT ngoài metadata** (`tag`, `code_path` — dự kiến, chỉ nhãn/đường dẫn):
  `counters.cooldown_override.CRASH` 12→9, `counters.cooldown_override.NORMAL` 7→6
  (STRESSED 16→16, RECOVERY 0→0 không đổi; tổng sự kiện 35→31) — ĐÚNG NGOẠI LỆ đã khai báo.
- **Mọi thứ khác trùng khớp bit-for-bit**: `eth_total` = 21.6370346047919 cả hai phía;
  `purchases_count` = 543 cả hai; **danh sách 543 purchase record so sánh bằng `==` python
  cho kết quả `True` tuyệt đối** (ts/source/nominal/reason từng phần tử); toàn bộ
  `final_pools` (BASE/SMART/OPPORTUNITY: available/reserved/deployed/total), toàn bộ
  `label_transitions`/`state_transitions`, `smart_ladders_created`/`opp_ladders_created`/
  `crash_ladders_created`, `releases_count_by_reason`/`releases_total_by_reason`,
  `avg_cash_ratio_vs_contributed`, `daily_limit_blocks`, `stuck_crash_reserve_at_end` —
  tất cả giống hệt.
Đây là bằng chứng mạnh hơn yêu cầu tối thiểu của check (không chỉ metric tổng hợp mà cả
TOÀN BỘ chuỗi purchase record, đến từng bản ghi).
Benchmark module (`benchmarks.py`): F-034 chỉ xoá dead code không được gọi — không có hàm
benchmark nào (`Benchmark A–D`, `F`, `G`) phụ thuộc `_noon_candles` (xác nhận bằng grep
trước khi xoá); do đó không cần đo lại benchmark riêng — thay đổi không thể ảnh hưởng.
File: `wp_a3_impact_WP_D1_BEFORE.json` / `wp_a3_impact_WP_D1_AFTER.json` /
`wp_a3_purchases_WP_D1_{BEFORE,AFTER}.json` (lưu phiên).

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:40Z

#### CHECK-D1-06 — Toàn bộ test suite PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ.

**Kết quả (S005):** `python -m pytest tests/` → **99 passed in 431.57s (0:07:11)** —
0 failed, 0 skipped, 0 xfail, exit code 0 (95 test trước WP-D1 + 4 test mới
`test_wp_d1_debt_cleanup.py`). Không test nào bị sửa để "cho qua"; không skip/nới lỏng.

Executed By:
Agent phiên S005 (Tier B / medium)

Timestamp:
2026-08-24T07:56Z

## Exit Criteria
- [x] 100% REQUIRED checks PASS (6/6: CHECK-D1-01..06)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [x] Kết quả mô phỏng không đổi, trừ ngoại lệ đã nêu rõ (cooldown_override 35→31 sự kiện)
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] Session handoff được viết (`docs/sessions/S005-wp-d1-debt-cleanup.md`)
- [x] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Một hạng mục hoá ra **làm đổi kết quả mô phỏng** → `SCOPE_CHANGED`: gỡ hạng mục đó khỏi WP-D1,
  tính lại routing và phân lớp lại theo tiêu chí RCP-001. Nó có thể thuộc lớp A hoặc B. **Không
  được giữ trong gói "không ảnh hưởng hành vi" một hạng mục có ảnh hưởng hành vi.**
- Sửa `ladder_completed()` làm lộ ra rằng hàm **có** được gọi ở đâu đó → dừng, đánh giá lại ảnh
  hưởng; đó là một tình huống khác với giả định của F-029.
- Cám dỗ dọn dẹp thêm ngoài bốn hạng mục → không. `ESCALATION_PROTOCOL.md` cấm refactor không liên
  quan.

## Ảnh hưởng nếu gói này thất bại

Không chặn gì. Rủi ro còn lại là rủi ro dài hạn: dữ liệu sai nghĩa (`expires_at`) và một hàm sai
ngữ nghĩa (`ladder_completed`) đang nằm chờ — nếu một thay đổi tương lai bắt đầu gọi chúng, lỗi sẽ
xuất hiện ở nơi không ai ngờ.

## Changed Files Registry

Created:
- `tests/test_wp_d1_debt_cleanup.py` — 4 test test-first (F-028/029/031/034)
- `docs/sessions/S005-wp-d1-debt-cleanup.md` — session handoff

Modified:
- `src/eth_dca_os/engine.py` — `expires_at` Smart ladder tính đúng cuối accounting month
  (F-028); bộ đếm `cooldown_override` đếm theo sự kiện (F-031)
- `src/eth_dca_os/ladders.py` — `ladder_completed()` bỏ PARTIALLY_FILLED khỏi tập kết thúc (F-029)
- `docs/tasks/WP-D1-no-ky-thuat-khong-anh-huong-hanh-vi.md` — evidence + Status DONE
- `PROJECT/PROJECT_PROGRESS.md` (+ `PROJECT/LO_TRINH_DE_HIEU.md` sinh tự động)

Deleted:
- `benchmarks._noon_candles` (dead code, F-034)

Migration Impact:
- Không

## Notes

Gói này rẻ và an toàn, nhưng chính vì thế nó dễ bị làm ẩu. Điểm kiểm soát duy nhất thật sự quan
trọng là CHECK-D1-05: nếu số liệu đổi mà không giải thích được, gói đã làm sai — và vì gói này có
thể chạy song song với mọi thứ khác, một thay đổi hành vi lọt qua đây sẽ rất khó quy trách nhiệm về
sau.
