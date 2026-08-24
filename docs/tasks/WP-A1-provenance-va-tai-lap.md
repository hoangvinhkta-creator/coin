# WP-A1 — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức

## Metadata
Status:
IN_PROGRESS

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 3
B: 3
A: 2
X: 3
U: 2
V: 3
H: 3
C: 3
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.6

Effort Routing Score:
2.8

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
D

Escalation Effort:
max

Difficulty:
2/4

Risk:
3/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Làm cho một official run **tự chứng minh được nguồn gốc và khả năng tái lập của chính nó**, tới mức
một người đọc record nhiều năm sau có thể trả lời dứt khoát: dữ liệu đến từ đâu, chạy bằng mã nào,
bằng thư viện phiên bản nào, với manifest và seed nào — và dựng lại được kết quả đó.

Hệ quả bắt buộc kèm theo: **dữ liệu tổng hợp không bao giờ được ghi nhận là official** (DEC-003).

## Vì sao gói này tồn tại

Hôm nay cờ `official` chỉ phản ánh việc có dùng `--dev-limit` hay không, và `lineage.json` ghi
`source` là một chuỗi cố định `'see fetch/synth'` cho cả dữ liệu thật lẫn dữ liệu nhân tạo (F-005).
Chạy `ethdca synth && ethdca run all` sẽ sinh ra một record mang `official: true` trên dữ liệu hoàn
toàn nhân tạo, và **không trường nào trong record cho phép phát hiện điều đó về sau**.

Đồng thời thư viện không được ghim (F-007) và run record thiếu `sensitivity_manifest_hash` (F-009),
`simulation_seed`, `code_commit` (F-010), `created_at` của config (F-011). Master Index §6 cấm chạy
lại official run để cải thiện kết quả — nên nếu lần chạy đầu tiên không có provenance, khiếm khuyết
đó **không sửa được về sau**.

## Đóng finding / risk

- F-005 — cờ `official` không kiểm nguồn dữ liệu; lineage `source` là chuỗi cố định
- F-007 — không ghim phiên bản thư viện
- F-009 — `sensitivity_manifest_hash` không bao giờ được ghi
- F-010 — thiếu `simulation_seed` và `code_commit`
- F-011 — thiếu `created_at` ở `StrategyConfig` và `ExecutionConfig`
- RSK-006 — không tái lập được theo thời gian
- RSK-008 — run trên dữ liệu tổng hợp vẫn được ghi nhận là official

Gói này **hấp thụ toàn bộ T-06A** (DEC-007 quyết định 3). T-06A đã bị loại khỏi roadmap; không
requirement nào của nó được phép rơi.

## Scope

- `src/eth_dca_os/reporting.py` — trường của run record
- `src/eth_dca_os/config.py` — `created_at` cho strategy/execution config
- `src/eth_dca_os/data/dataset.py`, `src/eth_dca_os/data/fetch.py`, `src/eth_dca_os/data/synth.py` — lineage `source` thật
- `src/eth_dca_os/pipeline.py` — truyền `manifest_hash`, dẫn xuất cờ `official`
- `pyproject.toml` + lockfile — ghim dependency
- `tests/` — test cho các bất biến provenance
- `docs/CONVENTIONS.md` — ghi quy ước phân loại nguồn dữ liệu nếu phát sinh

## Out of Scope

- Thay đổi thuật toán, công thức, ngưỡng gate, cách sinh manifest (Master Index §6)
- Chạy `ethdca fetch` hoặc official run (đó là T-06, và bị BLK-001 chặn)
- Đấu nối benchmark/chẩn đoán vào pipeline (WP-A2)
- Sửa vòng đời regime/ladder (WP-A3)
- Đổi nguồn dữ liệu sang sàn khác (cấm bởi DEC-003 và freeze rule)

## Dependencies
- T-04 (DONE)

## Blocks
- GATE-A → T-06

## Parallel-Safe With
- WP-A2, WP-A3, WP-C1, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `src/eth_dca_os/reporting.py`, `config.py`, `pipeline.py`, `data/`
- `pyproject.toml`, lockfile mới
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/engine.py`, `ladders.py`, `regime.py`, `score.py`, `capital.py`
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `gates.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [ ] A1.1 Ghi `source` thật vào lineage, phân biệt `binance_bulk_archive` / `binance_rest` / `synthetic`
- [ ] A1.2 Biến `official` thành hàm dẫn xuất từ lineage đã verify checksum, không phải trường đặt tay
- [ ] A1.3 Truyền `manifest_hash` vào mọi lời gọi `save_run` của run GATE2/GATE3
- [ ] A1.4 Bổ sung `simulation_seed`, `code_commit` (git SHA), `python_version`, `dependency_lock_hash`
- [ ] A1.5 Bổ sung `created_at` cho `StrategyConfig` và `ExecutionConfig`
- [ ] A1.6 Ghim dependency bằng lockfile; ghi hash lockfile vào record
- [ ] A1.7 Viết test cho từng bất biến provenance
- [ ] A1.8 Dựng lại môi trường từ lockfile và tái lập một run; đối chiếu kết quả
- [ ] A1.9 Ghi quy ước phân loại nguồn dữ liệu vào `docs/CONVENTIONS.md`

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Dependency (T-04) DONE
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §20, DM §12, DM §13, IM §7, DEC-003, DEC-007
- [x] Data impact được biết — gói này đổi **schema của run record và lineage**, không đổi dữ liệu thị trường
- [x] Security impact được biết — không chạm auth/secret; `code_commit` không được để lộ đường dẫn tuyệt đối của máy chủ dự án
- [x] Routing impact được biết — Tier/Effort tái lập được bằng router, không override
- [x] Migration prerequisite được xác định — run record cũ (nếu có) không tồn tại; `results/` chưa từng có, nên không cần migration ngược
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Primary agent tier được gán bằng router
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi

## Completion Gate

Áp `governance/core/TASK_COMPLETION_GATE_STANDARD.md` và `governance/core/EVIDENCE_STANDARD.md`.
Risk = 3 → mọi REQUIRED check kiểm chứng được **bắt buộc E1**. Vì gói này bảo vệ tính toàn vẹn của
verdict, CHECK-A1-11 yêu cầu E2 theo thủ tục Solo Independent Review.

### Data / Audit

#### CHECK-A1-01 — Run record chứa đủ 8 nhóm trường provenance bắt buộc
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: một run đầy đủ sinh ra record chứa đồng thời `python_version`, `dependency_lock_hash`,
`code_commit`, `dataset_hash`, `strategy_config_hash`, `execution_config_hash`,
`sensitivity_manifest_hash`, seed (`master_seed` và `simulation_seed`). Bằng chứng phải là nội dung
record thật in ra, không phải mô tả.

Executed By:
...

Timestamp:
...

#### CHECK-A1-02 — `sensitivity_manifest_hash` thật sự được ghi cho run GATE2 và GATE3
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: từ record của một run GATE2 và một run GATE3, đọc ra `sensitivity_manifest_hash` khác rỗng
và trùng với hash của manifest thực sự được dùng. Đóng F-009.

Executed By:
...

Timestamp:
...

#### CHECK-A1-03 — `simulation_seed` và `code_commit` có mặt và đúng giá trị
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `code_commit` khớp `git rev-parse HEAD` tại thời điểm chạy; `simulation_seed` khác rỗng và
tái lập được kết quả. Đóng F-010.

Executed By:
...

Timestamp:
...

#### CHECK-A1-04 — `created_at` có mặt ở cả `StrategyConfig` và `ExecutionConfig`
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: hai config sinh ra từ pipeline đều mang `created_at`; và việc thêm trường này **không làm
đổi** `strategy_config_hash` / `execution_config_hash` của cùng một cấu hình nghiệp vụ, hoặc nếu có
đổi thì sự thay đổi được ghi nhận tường minh vì nó ảnh hưởng tính so sánh giữa các run. Đóng F-011.

Executed By:
...

Timestamp:
...

#### CHECK-A1-05 — `lineage.json` phân biệt được ba nguồn dữ liệu
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: `source` nhận đúng một trong `binance_bulk_archive`, `binance_rest`, `synthetic` cho từng
series; không còn chuỗi cố định `'see fetch/synth'` ở bất kỳ đâu. Đóng F-005 phần lineage.

Executed By:
...

Timestamp:
...

#### CHECK-A1-06 — Dữ liệu tổng hợp không thể tạo ra `official: true`
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: chạy `ethdca synth` rồi `ethdca run all` **không dùng `--dev-limit`** cho ra record mang
`official: false`. Đây là kịch bản chính xác mà F-005 mô tả và hôm nay đang cho `official: true`.

Executed By:
...

Timestamp:
...

#### CHECK-A1-07 — Cờ `official` không giả mạo được bằng flag hay biến môi trường
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: liệt kê toàn bộ bề mặt CLI và biến môi trường, chứng minh không tồn tại đường nào ép
`official: true` khi lineage là `synthetic`. `official` phải là **hàm dẫn xuất** từ lineage đã
verify checksum, không phải một trường ghi được. Bằng chứng gồm test khẳng định điều này.

Executed By:
...

Timestamp:
...

### Reliability / Reproducibility

#### CHECK-A1-08 — Dependency được ghim và hash lockfile được ghi vào record
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: tồn tại lockfile ghim phiên bản chính xác (không chỉ đặt sàn); `dependency_lock_hash` trong
record khớp hash của lockfile đó. Đóng F-007, giảm thiểu RSK-006.

Executed By:
...

Timestamp:
...

#### CHECK-A1-09 — Dựng lại môi trường từ lockfile và tái lập một run cho kết quả trùng khớp
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: cài môi trường sạch từ lockfile, chạy lại cùng dataset hash + config hash + manifest hash +
seed, đối chiếu kết quả ở mức metric theo BT §20 ("bit-for-bit ở mức metric"). Sai lệch bất kỳ phải
được giải thích, không được làm tròn cho qua.

Executed By:
...

Timestamp:
...

### Regression

#### CHECK-A1-10 — Toàn bộ test suite Python PASS và không hành vi mô phỏng nào bị đổi
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E1

Evidence:
Yêu cầu: test suite PASS đầy đủ; và chạy cùng seed/dataset trước–sau cho **cùng metric**. WP-A1 là
gói provenance, không phải gói đổi hành vi — mọi sai lệch kết quả mô phỏng là dấu hiệu gói đã đi
ra ngoài phạm vi.

Executed By:
...

Timestamp:
...

### Audit độc lập

#### CHECK-A1-11 — Có bản rà soát độc lập E2 cho các bất biến provenance
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: một phiên reviewer độc lập theo "Solo Independent Review Procedure" của
`EVIDENCE_STANDARD.md`, bắt đầu từ trạng thái repo chứ không từ tuyên bố của người cài đặt, chạy lại
CHECK-A1-06, A1-07, A1-09 và ghi bằng chứng riêng. Lưu tại `docs/reviews/` theo
`governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.

Executed By:
...

Timestamp:
...

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 cho toàn bộ; E2 cho CHECK-A1-11)
- [ ] Không defect nghiêm trọng nào chưa xử lý
- [ ] `docs/CONVENTIONS.md` ghi quy ước phân loại nguồn dữ liệu
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-006 và RSK-008 được cập nhật trạng thái
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Không dựng được lockfile tái lập được vì công cụ đóng gói không khả dụng → `MISSING_INPUT`,
  chuyển BLOCKED, ghi rõ thiếu gì. KHÔNG nâng Tier, KHÔNG ghi PASS.
- Tái lập cho kết quả lệch mà không giải thích được sau khi đã điều tra → `VERIFICATION_DEPTH`,
  nâng Effort một bậc (xhigh → max).
- Hai cách tiếp cận khác nhau cho việc dẫn xuất `official` đều không đóng được đường giả mạo →
  `CAPABILITY_CEILING`, nâng Tier lên D.
- Phát hiện phải đổi công thức/hash schema để đạt provenance → `SCOPE_CHANGED` và **CONFLICT
  DETECTED** với Master Index §6; dừng và trình chủ dự án, không tự sửa.

## Ảnh hưởng nếu gói này thất bại

GATE-A không đóng được → T-06 không được mở. Nếu bỏ qua và vẫn chạy official run, kết quả sẽ mang
`official: true` mà không chứng minh được nguồn gốc, và theo Master Index §6 **không được chạy lại
để sửa** — verdict khi đó không dùng được cho T-07, kéo theo T-11 mất căn cứ.

## Changed Files Registry

Created:
- (dự kiến) lockfile ghim dependency
- (dự kiến) `docs/reviews/E2-WP-A1-*.md`

Modified:
- (dự kiến) `src/eth_dca_os/reporting.py`, `config.py`, `pipeline.py`, `data/`
- (dự kiến) `pyproject.toml`, `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- Không có run record cũ cần migrate (`results/` chưa từng tồn tại — xác nhận E1 tại S000)

## Notes

Cạm bẫy của gói này: thêm đủ trường vào record rồi tuyên bố xong. Nhưng điều thật sự phải chứng minh
là **không tồn tại đường nào để một run trên dữ liệu giả tự nhận là official**. Đó là lý do
CHECK-A1-07 yêu cầu liệt kê bề mặt CLI/env, không chỉ thêm một test hạnh phúc.

Ràng buộc DEC-003 là tuyệt đối: dữ liệu tổng hợp dùng để phát triển và kiểm chứng thì hợp lệ; dùng
để tạo verdict thì không, trong mọi hoàn cảnh.
