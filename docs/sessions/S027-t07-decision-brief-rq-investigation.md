# S027 — T-07 Decision Brief + Owner Response + RQ Evidence Investigation (SPIKE)

Ngày: 2026-09-05. Nhánh: `claude/t-07-decision-prep-1oprq1` (tách từ `origin/main` `53a63c4`).

## 1. Phần một — chuẩn bị quyết định T-07 (decision preparation only)

Đọc toàn bộ authority canonical liên quan `T-07` (`AGENTS.md`, `governance/v4/CORE/*`,
`PROJECT/PROJECT_PROGRESS.md`, `PROJECT/PROJECT_DECISIONS.md`, `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`,
`docs/spec/{00_MASTER_INDEX,03_BACKTEST_SPEC,05_IMPLEMENTATION_PLAN}_V2_1_5.md`,
`docs/tasks/WP-B1-*.md`, `docs/sessions/S018,S020`). Soạn
`docs/reviews/T07-OWNER-DECISION-BRIEF.md` (14 mục theo yêu cầu): trạng thái đầu vào; những gì
`T-06` kiểm; cái gì đạt kỹ thuật vs trượt chiến lược; ngữ nghĩa `DO_NOT_BUILD` (tách bạch "V2.1.5
trượt validation" khỏi "dự án phải bị bỏ" — không authority nào phát biểu vế sau); bề mặt lựa
chọn canonical L-1 (benchmark đơn giản hơn) / L-2 (mở V2.2); FACTS/INTERPRETATIONS/NOT
ESTABLISHED; năm câu hỏi nghiên cứu RQ-1..RQ-5 gắn nhãn trạng thái mà KHÔNG chạy thí nghiệm mới.
Ghi nhận `OWNER_DECISION_SURFACE_UNCLEAR` (T-07 không có file task/Ready Gate/Completion Gate).
Không transition `T-07`. Không tạo DEC. Production diff = EMPTY. Commit `6f28fe1`, push.

## 2. Phần hai — Owner phản hồi + DEC-039

Owner đọc brief, trả lời qua chat theo đúng format §14: `LUA CHON: L-0` (chưa chọn giữa L-1/L-2),
`T-07 LIFECYCLE: GIU READY`, xác nhận toàn bộ ràng buộc bắt buộc giữ nguyên (verdict, validation,
`can_proceed_to_app`, `T-11`, `DEC-005`), **không** uỷ quyền ghi quyết định chiến lược cuối cùng,
nhưng **có** uỷ quyền một phiên evidence-investigation phạm vi hẹp (RQ-1, RQ-3, RQ-4, RQ-5; RQ-2
dùng evidence sẵn có) với ranh giới rất cụ thể (không sửa `src/`, không đổi strategy/threshold,
không rerun `T-06`, không mở `T-11`/`WP-D2`, không resolve `DEC-005`, tách REPLAY khỏi OFFICIAL,
phải reproduce baseline trước khi tin số derived).

Ghi nhận `DEC-039` (`PROJECT/PROJECT_DECISIONS.md`) canonical hoá phản hồi này. `T-07` **không**
transition, giữ `READY`.

## 3. Phần ba — phiên SPIKE evidence-investigation

Đọc code liên quan (`metrics.py`, `benchmarks.py`, `pipeline.py::run_gate1`, `windows.py`,
`engine.py`) để xác định: (a) RQ-5 trả lời được ngay bằng tổng hợp evidence hiện có, không cần
dataset mới; (b) RQ-1 phần nhân quả (counterfactual reserve/cash) **ngoài phạm vi được phép**
(cấm sửa strategy) — chỉ phần tương quan quan sát mô tả là khả thi; (c) RQ-3 (Control F/G theo
từng W1-W9 + OOS) và RQ-4 (phân rã ETH theo nguồn purchase + thống kê idle capital) đều tái dùng
được nguyên hàm production có sẵn (`window_metrics`, `oos_metrics`, `random_timing_control`,
`random_anchor_control`, `cash_ratio_stats`, `opportunity_cap_hit_share`) mà KHÔNG cần sửa
`src/` — chỉ cần một script gọi lại các hàm đó với phạm vi hẹp hơn (từng window thay vì toàn kỳ).

Thiết kế một script REPLAY duy nhất bao phủ RQ-1/RQ-3/RQ-4, có bước STEP 0 bắt buộc reproduce
bit-for-bit ba con số official đã biết (`v2_eth`, `control_f_p95`, `control_g_p95` từ
`CHECK-B1-03` Addendum 3) trước khi in bất kỳ số derived nào — nếu không khớp, script tự DỪNG và
báo `STEP_0: FAIL`. **Smoke test PASS** trên dataset SYNTHETIC (`eth_dca_os.data.synth.generate`)
trong sandbox agent: exit code 0, không exception, mọi giá trị đúng kiểu Python thuần
(`bool`/`float`, tránh tái phạm `F-S015-01`). Số liệu synthetic **KHÔNG** được dùng làm evidence.

**MISSING_INPUT** xác nhận lại: sandbox agent không có `data/raw/*.parquet` official (gitignored,
không tồn tại ở đây), không có kết nối Binance, không được fetch dữ liệu mới. RQ-1 (phần quan
sát)/RQ-3/RQ-4 giữ `MISSING_INPUT` chờ Owner chạy script trên dataset official đã bảo toàn và
dán lại output.

**RQ-5 trả lời đầy đủ ngay trong phiên này** (§2 của `T07-RQ-EVIDENCE-INVESTIGATION.md`):
**PARTIALLY ESTABLISHED** — Gate 2 = 0,00 % (219 config), FS-02 = 0,8961 (reserve nằm im) cùng
FS-07 = FALSE (buộc `avg_cash_ratio ≤ 0,30` ở tầng portfolio) và FS-01 = TRUE (thua cả Monthly
DCA) cùng nghiêng về phía cấu trúc phân bổ vốn Opportunity Fund góp phần vào thất bại, nhưng
KHÔNG loại trừ được việc cũng thiếu timing edge, và không có phép đo tách bạch hai thành phần.

**RQ-2**: giữ nguyên kết luận đã canonical (`CHECK-B1-03` Addendum 3), không chạy gì mới, diễn
giải đúng theo chỉ thị Owner (không nâng cấp thành "đã chứng minh predictive skill").

Kết quả đầy đủ: `docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md`.

## 4. Trạng thái sau phiên

`T-07 = READY` (không đổi). `official verdict = DO_NOT_BUILD`, `V2.1.5 validation = FAILED`,
`can_proceed_to_app = false`, `T-11 = BLOCKED`, `DEC-005 = PENDING` — tất cả giữ nguyên. Không
task ID mới. Không mở `WP-D2`/`T-11`. Không resolve `DEC-005`. Không rerun `T-06`. Production
diff = EMPTY (`git diff 53a63c4 -- src/eth_dca_os webapp pyproject.toml pyproject.lock tests` =
rỗng). Thay đổi: `PROJECT/PROJECT_DECISIONS.md` (+`DEC-039`), `PROJECT/PROJECT_PROGRESS.md`
(narrative + dòng roadmap `T-07`), `PROJECT/LO_TRINH_DE_HIEU.md` (regenerate),
`docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` (mới).

Validators: `sync_easy_roadmap.py` PASS, `validate_easy_roadmap.py` PASS, `validate_governance.py`
PASS (V4.3), `validate_structure.py` PASS (27 path), `validate_project_state.py` PASS,
`validate_routing.py` PASS (19 MAJOR task file), `branch_authority_check.sh` PASS (production
diff = EMPTY).

## 5. Bước tiếp theo

Chờ Owner chạy script REPLAY (`docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` §6) trên dataset
official đã bảo toàn và cung cấp lại output. Một phiên canonicalize sẽ ghi kết quả (theo khuôn
REPOSITORY-VERIFIED/OWNER-REPORTED của `T06_OFFICIAL_EVIDENCE_RECORD.md`), sau đó **quay lại
`T-07`** để Owner chọn giữa L-1 (benchmark đơn giản hơn) và L-2 (mở V2.2) — quyết định đó vẫn
PENDING, không được đưa ra thay Owner ở bất kỳ phiên nào cho tới nay.
