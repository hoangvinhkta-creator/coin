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
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: một run đầy đủ sinh ra record chứa đồng thời `python_version`, `dependency_lock_hash`,
`code_commit`, `dataset_hash`, `strategy_config_hash`, `execution_config_hash`,
`sensitivity_manifest_hash`, seed (`master_seed` và `simulation_seed`). Bằng chứng phải là nội dung
record thật in ra, không phải mô tả.

Record thật từ `backtest_runs.jsonl` của run GATE1 (dữ liệu synthetic, dev_limit=None) — đủ 9 khoá
provenance, không khoá nào rỗng, cộng `data_source` và `official` để record tự trả lời "dữ liệu đến
từ đâu" và "có phải official không". Test `test_a1_01_run_record_has_all_provenance_fields` kiểm
từng khoá bằng assertion cứng, và bác riêng hai giá trị suy biến `dependency_lock_hash` =
"no-lockfile" / `code_commit` = "unknown" (nếu không, "có trường" vẫn có thể vô nghĩa).

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-02 — `sensitivity_manifest_hash` thật sự được ghi cho run GATE2 và GATE3
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: từ record của một run GATE2 và một run GATE3, đọc ra `sensitivity_manifest_hash` khác rỗng
và trùng với hash của manifest thực sự được dùng. Đóng F-009.

BEFORE (d72fbc4): lần cài đặt trước CHỈ truyền `manifest_hash` cho GATE1. Lời gọi `save_run` trong
`run_gate2` và `run_gate3` hoàn toàn không có tham số này, nên đúng hai record mà check này đòi hỏi
lại ghi `sensitivity_manifest_hash = null`. F-009 CHƯA đóng; test cũ chỉ kiểm GATE1 nên không thấy.

AFTER: `run_gate2` / `run_gate3` hash ĐÚNG manifest đã chạy bằng `manifest_hash([_cfg_row(c) ...])`
— cùng hai hàm mà `freeze_manifests` dùng, nên hash trong record đối chiếu được trực tiếp với
manifest đóng băng. Khi `--dev-limit` cắt manifest, hash phản ánh manifest đã cắt đúng như đã chạy,
không phải manifest đầy đủ.

GATE1 không chạy manifest sensitivity; nó hash tập chín window thực dùng để record vẫn tự chứng minh
được phạm vi đo.

Test: `test_a1_02_manifest_hash_gate2_gate3` (so record với hash tính độc lập từ manifest),
`test_a1_02_manifest_hash_gate1`.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-03 — `simulation_seed` và `code_commit` có mặt và đúng giá trị
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: `code_commit` khớp `git rev-parse HEAD` tại thời điểm chạy; `simulation_seed` khác rỗng và
tái lập được kết quả. Đóng F-010.

`code_commit` được đối chiếu bằng assertion cứng với `git rev-parse HEAD`. `simulation_seed` là số
nguyên dẫn xuất `deterministic_hash(master_seed, strategy_hash, execution_hash)`; test khẳng định nó
deterministic, ĐỔI theo config, và KHÁC `master_seed` — nếu không, một hằng số cũng sẽ PASS.

DEFECT ĐÃ SỬA (phát hiện trong remediation này): `_get_code_commit` và `_get_dependency_lock_hash`
hard-code `/home/user/coin`. Official run bắt buộc chạy trên máy có mạng Binance (DEC-003/BLK-001),
nơi đường dẫn đó không tồn tại — hai hàm sẽ âm thầm trả "unknown" và "no-lockfile", tức MẤT
provenance đúng lần chạy duy nhất mà Master Index §6 cấm chạy lại. Nay gốc repo suy từ vị trí module
(`Path(__file__).resolve().parents[2]`); cũng thoả ghi chú Ready Gate về việc không để lộ đường dẫn
tuyệt đối của máy chủ dự án.

Test: `test_a1_03_simulation_seed_and_code_commit`,
`test_a1_03_simulation_seed_is_derived_not_constant`.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-04 — `created_at` có mặt ở cả `StrategyConfig` và `ExecutionConfig`
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: hai config sinh ra từ pipeline đều mang `created_at`; và việc thêm trường này **không làm
đổi** `strategy_config_hash` / `execution_config_hash` của cùng một cấu hình nghiệp vụ, hoặc nếu có
đổi thì sự thay đổi được ghi nhận tường minh vì nó ảnh hưởng tính so sánh giữa các run. Đóng F-011.

KẾT QUẢ: `created_at` được đóng dấu ISO8601 UTC lên cả `StrategyConfig` và `ExecutionConfig`, CỐ Ý
không phải dataclass field — `asdict()` nuôi cả `hash`, `key()` (khử trùng lặp manifest) và
`_cfg_row` (hash manifest đóng băng), nên một field mang dấu thời gian sẽ làm hash config đổi theo
thời điểm chạy và manifest hết tái lập.

Đối chiếu trực tiếp với commit d72fbc4 (trước khi thêm) qua `git worktree`, cùng interpreter:

    BEFORE strategy_hash    = f782f99077fe57693c1a7de0583f087464174a12f00c1a56479823af17501b7b
    AFTER  strategy_hash    = f782f99077fe57693c1a7de0583f087464174a12f00c1a56479823af17501b7b
    BEFORE exec1_hash       = 5888866fa8ce62bebd485df17247d654804d9462121ce935243636f4c55c6ec9
    AFTER  exec1_hash       = 5888866fa8ce62bebd485df17247d654804d9462121ce935243636f4c55c6ec9
    BEFORE exec3_hash       = 789bd885640f8c9793e6d77f21cba77ee15c782de98312dd366acf4d043ab5f4
    AFTER  exec3_hash       = 789bd885640f8c9793e6d77f21cba77ee15c782de98312dd366acf4d043ab5f4
    BEFORE g2 manifest_hash = e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e
    AFTER  g2 manifest_hash = e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e
    BEFORE g3 manifest_hash = ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f
    AFTER  g3 manifest_hash = ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f
    denominator Gate 2 = 219 (không đổi); size Gate 3 = 114 (không đổi)

Không hash nào đổi một bit. Test: `test_a1_04_created_at_in_configs`,
`test_a1_04_created_at_does_not_affect_any_hash` (ghim cứng hai hash trên).

BEFORE (d72fbc4): `hasattr(BASELINE_STRATEGY, "created_at")` = False — F-011 CHƯA đóng, và test cũ
PASS giả vì bọc trong `if hasattr(...)`.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-05 — `lineage.json` phân biệt được ba nguồn dữ liệu
Priority:
REQUIRED

Status:
PASS — E1 + E2 vòng ba (F-E2A1-01 ĐÓNG: reviewer tự chạy stub fetch 5 kịch bản)

Evidence Level:
E1

Evidence:
Yêu cầu: `source` nhận đúng một trong `binance_bulk_archive`, `binance_rest`, `synthetic` cho từng
series; không còn chuỗi cố định `'see fetch/synth'` ở bất kỳ đâu. Đóng F-005 phần lineage.

BEFORE (d72fbc4): `ethdca synth` ghi `lineage.source = 'unknown'` cho cả dataset lẫn từng series —
tham số `source` đã có nhưng KHÔNG nơi tạo dataset nào truyền. Chuỗi cố định vẫn còn trong
`data/dataset.py`. `build_lineage` chấp nhận âm thầm mọi chuỗi, kể cả `'binance-archive+api'` mà
`fetch.py` đang truyền cho `write_raw` (giá trị này còn bị `write_raw` bỏ qua hoàn toàn).

AFTER: nguồn được khai tại NƠI TẠO dataset. `build_lineage` bắt buộc `source` (bỏ giá trị mặc định
để không thể quên), nhận mapping theo từng series, và raise `ValueError` với giá trị ngoài taxonomy.
`synth.generate` truyền `synthetic`; `fetch.fetch_all` phân loại theo từng series từ các cơ chế
`fetch_series` thực sự đã dùng, kèm `source_detail` khi series lắp từ cả archive lẫn REST.

    lineage['source'] = 'synthetic'
    per-file: {'BTCUSDT_1d': 'synthetic', 'ETHUSDT_15m': 'synthetic', 'ETHUSDT_1d': 'synthetic'}

Test: `test_a1_05_synth_lineage_source_is_synthetic` (assertion CỨNG cho dataset và từng series),
`test_a1_05_no_hardcoded_source_string_remains` (quét toàn bộ `src/`),
`test_a1_05_build_lineage_rejects_unknown_taxonomy`.

GIỚI HẠN: đường `fetch` chưa chạy được E1 vì BLK-001 chặn mạng Binance, và chạy `ethdca fetch` nằm
ngoài Scope của gói này. Phần đã kiểm là logic phân loại + taxonomy; nhãn thực tế của ba series thật
chỉ xác nhận được khi T-06 chạy.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-06 — Dữ liệu tổng hợp không thể tạo ra `official: true`
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: chạy `ethdca synth` rồi `ethdca run all` **không dùng `--dev-limit`** cho ra record mang
`official: false`. Đây là kịch bản chính xác mà F-005 mô tả và hôm nay đang cho `official: true`.

BEFORE (d72fbc4) — chạy đúng kịch bản trên, dev_limit=None:

    payload['official']  = True        <-- F-005 CHƯA đóng
    lineage['source']    = 'unknown'
    'lineage' in payload = False       <-- nên assertion trong test cũ không bao giờ chạy

AFTER — cùng kịch bản:

    payload['official']        = False
    payload['official_reason'] = "source_not_real:BTCUSDT_1d='synthetic'"
    run_record['official']     = False
    run_record['data_source']  = 'synthetic'

Cờ `official` nay là hàm dẫn xuất từ `official_eligibility(raw_dir, lineage)`; `Prepared` gọi một
lần và Gate 1/2/3 cùng verdict dùng chung kết quả — không gate nào suy luận lại.

Test: `test_a1_06_synthetic_cannot_be_official` (kiểm cả payload lẫn run record),
`test_a1_06_synthetic_not_official_in_gate2_gate3`.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-07 — Cờ `official` không giả mạo được bằng flag hay biến môi trường
Priority:
REQUIRED

Status:
PASS — E1 + E2 vòng ba (F-E2A1-01 và F-E2A1-02 ĐÓNG: reviewer thử phá, không phá được trong phạm vi gate)

Evidence Level:
E1

Evidence:
Yêu cầu: liệt kê toàn bộ bề mặt CLI và biến môi trường, chứng minh không tồn tại đường nào ép
`official: true` khi lineage là `synthetic`. `official` phải là **hàm dẫn xuất** từ lineage đã
verify checksum, không phải một trường ghi được. Bằng chứng gồm test khẳng định điều này.

BEFORE (d72fbc4): không tồn tại phép dẫn xuất nào — `official = dev_limit is None` ở cả ba gate.
Nghĩa là mọi run không dùng `--dev-limit` đều tự nhận official bất kể dữ liệu từ đâu.

BỀ MẶT ĐÃ RÀ (E1):
- CLI: không có `--official`, `--force-official`, `--source`, `--real-data`; không đọc `os.environ`
  hay `os.getenv` ở bất kỳ đâu trong `cli.py`.
- `official_eligibility(raw_dir, lineage)` nhận ĐÚNG hai tham số — không có cờ, không có override.
- `reporting` không import `official_eligibility`: nơi ghi record không có khả năng tự quyết định
  official, chỉ ghi lại giá trị pipeline đã tính.
- `Prepared` tính một lần; Gate 1/2/3 và verdict dùng chung, không gate nào có nhánh riêng.

ĐIỀU KIỆN ĐỦ TƯ CÁCH (fail-closed) — mọi series phải mang nguồn thuộc `REAL_SOURCES`, VÀ lineage
phải verify được checksum. Probe đối kháng, kết quả thực tế:

    synthetic (nhãn đúng)          -> (False, "source_not_real:BTCUSDT_1d='synthetic'")
    unknown                        -> (False, "source_not_real:...='unknown'")
    lineage = None                 -> (False, 'lineage_missing')
    lineage = {}                   -> (False, 'lineage_no_files')
    lineage = {'files': []}        -> (False, 'lineage_no_files')
    nhãn real + checksum khớp      -> (True,  'verified')      <-- positive control
    nhãn real + file_hash bị sửa   -> (False, 'file_hash_mismatch:BTCUSDT_1d.parquet')
    nhãn real + dataset_hash sai   -> (False, 'dataset_hash_mismatch')
    nhãn real + xoá 1 file         -> (False, 'missing_file:...')
    lineage đủ tư cách + dev_limit -> official = False

Positive control quan trọng: nếu thiếu nó, một cổng "luôn trả False" cũng sẽ PASS mọi test còn lại.

Test: `test_a1_07_unknown_source_is_not_official`, `test_a1_07_missing_lineage_is_not_official`,
`test_a1_07_tampered_dataset_is_not_official`, `test_a1_07_dev_limit_still_forces_non_official`,
`test_a1_07_no_cli_or_env_surface_can_force_official`,
`test_a1_07_real_sources_are_exactly_the_binance_ones`.

GIỚI HẠN đã ghi vào `docs/CONVENTIONS.md`: cơ chế này chứng minh dữ liệu KHỚP nguồn đã khai và
không bị sửa sau khi khai. Nó không phát hiện được người vận hành cố ý dán nhãn `binance_*` lên dữ
liệu không phải của Binance — chống điều đó cần đối chiếu `ethdca freeze` hai máy theo DEC-003.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

### Reliability / Reproducibility

#### CHECK-A1-08 — Dependency được ghim và hash lockfile được ghi vào record
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: tồn tại lockfile ghim phiên bản chính xác (không chỉ đặt sàn); `dependency_lock_hash` trong
record khớp hash của lockfile đó. Đóng F-007, giảm thiểu RSK-006.

DEFECT NGHIÊM TRỌNG ĐÃ SỬA (phát hiện trong remediation này): `pyproject.lock` của lần cài đặt
trước được VIẾT TAY và phần lớn không đúng sự thật — 9/15 dòng lệch môi trường thật:

    lockfile ghi                 thực tế đã cài
    requests==2.31.0             2.33.1
    pluggy==1.5.0                1.6.0
    python-dateutil==2.8.2       2.9.0.post0
    urllib3==2.1.0               2.6.3
    certifi==2024.2.2            2026.2.25
    charset-normalizer==3.3.2    3.4.6
    idna==3.6.0                  3.11
    pytz==2024.1                 KHÔNG ĐƯỢC CÀI
    tzdata==2024.1               KHÔNG ĐƯỢC CÀI

Hệ quả: `dependency_lock_hash` sẽ "chứng minh" một môi trường CHƯA TỪNG TỒN TẠI. Dựng lại từ
lockfile đó cho ra môi trường khác với môi trường đã sinh ra số liệu official — đúng RSK-006 mà
gói này sinh ra để chặn, và theo Master Index §6 thì official run không được chạy lại để sửa.

AFTER: lockfile được SINH TỪ MÔI TRƯỜNG THẬT — đóng gói bắc cầu của dependency khai trong
`pyproject.toml`, phiên bản đọc bằng `importlib.metadata` trên chính interpreter chạy backtest.

Kiểm chứng: `test_a1_08_lockfile_and_hash` bắt buộc mọi dòng có `==` (lockfile đặt sàn `>=` sẽ
FAIL) và so `dependency_lock_hash` với sha256 tính độc lập từ file.
`test_a1_08_lockfile_matches_installed_environment` đối chiếu TỪNG dòng với môi trường đang chạy —
lockfile viết tay không thể lọt qua lần nữa.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

#### CHECK-A1-09 — Dựng lại môi trường từ lockfile và tái lập một run cho kết quả trùng khớp
Priority:
REQUIRED

Status:
PASS — E2 vòng ba (reviewer tự dựng venv sạch, 15/15 pin khớp, 3 process độc lập)

Evidence Level:
E1

Evidence:
Yêu cầu: cài môi trường sạch từ lockfile, chạy lại cùng dataset hash + config hash + manifest hash +
seed, đối chiếu kết quả ở mức metric theo BT §20 ("bit-for-bit ở mức metric"). Sai lệch bất kỳ phải
được giải thích, không được làm tròn cho qua.

Hai run độc lập trên cùng dataset/config/seed cho metric trùng khớp tuyệt đối (so sánh bằng `==`,
không có dung sai): `ae_by_window`, `primary_median`, `oos`, và `bootstrap_descriptive` — khối
bootstrap được so riêng vì nó là phần duy nhất dùng số ngẫu nhiên, nên nếu seed không thật sự dẫn
xuất thì nó là chỗ lộ ra đầu tiên. Toàn bộ trường provenance cũng phải trùng giữa hai run.

Test: `test_a1_09_reproducibility_same_seed_same_metrics`.

GIỚI HẠN — đây là E1 một phần, phải nói rõ: mới chứng minh tính tái lập TRONG một môi trường (cùng
interpreter, cùng thư viện đã cài). Yêu cầu "cài môi trường SẠCH từ lockfile" chưa thực hiện được vì
proxy chặn cài đặt gói (cùng gốc với BLK-001). Phần còn thiếu: dựng venv sạch từ `pyproject.lock`
trên máy có mạng rồi đối chiếu metric — nên làm cùng T-06, khi official run chạy ở đó.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

### Regression

#### CHECK-A1-10 — Toàn bộ test suite Python PASS và không hành vi mô phỏng nào bị đổi
Priority:
REQUIRED

Status:
PASS — E1 (test tự động) + E2 (reviewer độc lập tự chạy lại)

Evidence Level:
E1

Evidence:
Yêu cầu: test suite PASS đầy đủ; và chạy cùng seed/dataset trước–sau cho **cùng metric**. WP-A1 là
gói provenance, không phải gói đổi hành vi — mọi sai lệch kết quả mô phỏng là dấu hiệu gói đã đi
ra ngoài phạm vi.

TEST SUITE: `pytest tests/` — 130/130 PASS, exit code 0, không FAIL, không skip.

ĐỐI CHIẾU SỐ LIỆU TRƯỚC–SAU: cùng một dataset tổng hợp (seed 42, 2020-01-01..2023-12-31) chạy
`run_gate1` ở HAI phiên bản mã — worktree tại d72fbc4 và working tree sau remediation — rồi so
snapshot metric bằng `==`, không dung sai:

    BEFORE == AFTER : True

    dataset_hash   = 3ba67072ba769d0d4abb315003e1607f2acd3fcc1acef63bfaeb6f7c36ddc5e3  (không đổi)
    primary_median = 96.23260701438292
    final_eth      = 56.03896168942767
    ae_by_window   = W1 90.11972716149029  W2 107.20019002978864  W3 91.53173036360930
                     W4 91.43746206075359  W5 101.64416673297248  W6 93.09823928306028
                     W7 98.75055998074536  W8 100.26314001913342  W9 97.11604113387443

Snapshot gồm: dataset_hash, chín AE theo window, primary_median, pooled_median_descriptive,
anchor_set_medians, gate1.pass, oos.ae, concentration, cash_ratio, counters_w5, xirr, final_eth.
`dataset_hash` không đổi là điều đáng chú ý: nhãn nguồn nay được ghi vào lineage nhưng hash tập dữ
liệu vẫn tính từ hash các file parquet, nên việc gắn nhãn KHÔNG làm đứt tính so sánh với các run cũ.

Hai điểm phải nói rõ để không bị đọc thành mạnh hơn thực tế:
- `oos.ae` và `xirr` là NaN ở CẢ HAI phiên bản — dataset tổng hợp kết thúc 2023-12-31 nên cửa sổ OOS
  không có dữ liệu. Chúng so bằng nhau do `json` dùng chung một đối tượng NaN khi parse, tức đây là
  đặc thù kỹ thuật; điều có ý nghĩa là cả hai phiên bản cùng ở trạng thái NaN.
- Khối `bootstrap_descriptive` không nằm trong snapshot này (mọi trường của nó là list/dict nên bị
  bộ lọc scalar loại). Nó được phủ riêng bởi `test_a1_09_reproducibility_same_seed_same_metrics`,
  test này so toàn bộ khối bootstrap giữa hai run.

Executed By:
S007 remediation session (Opus / xhigh)

Timestamp:
2026-08-24

### Audit độc lập

#### CHECK-A1-11 — Có bản rà soát độc lập E2 cho các bất biến provenance
Priority:
REQUIRED

Status:
FAIL — vòng ba (xem `docs/reviews/E2-WP-A1-provenance-round3.md`)

Evidence Level:
E2

Evidence:
Yêu cầu: một phiên reviewer độc lập theo "Solo Independent Review Procedure" của
`EVIDENCE_STANDARD.md`, bắt đầu từ trạng thái repo chứ không từ tuyên bố của người cài đặt, chạy lại
CHECK-A1-06, A1-07, A1-09 và ghi bằng chứng riêng. Lưu tại `docs/reviews/` theo
`governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.

KẾT QUẢ: **E2 FAIL** (lần rà soát thứ hai, trên commit 2f20e6c).
Báo cáo: `docs/reviews/E2-WP-A1-provenance.md`.

Điểm số reviewer tự chấm: 7 PASS / 2 FAIL / 1 NOT_TESTED trên CHECK-A1-01..A1-10.

HAI FINDING CHẶN — cả hai đều là mặc định FAIL-OPEN do chính lượt remediation này đưa vào, tức
đúng nguyên tắc mà gói này tuyên bố bảo vệ:

- F-E2A1-01 (CAO) — `fetch_all`: `sources[key] = used[0] if used else SOURCE_REST`. Series mà
  KHÔNG cơ chế nào tạo ra (0 dòng) vẫn được dán nhãn `binance_rest` — một nguồn THẬT, đủ tư cách
  official. Reviewer chứng minh bằng stub hai hàm I/O (không cần mạng): một lần fetch không lấy
  được dòng nào cho `official_eligibility -> (True, 'verified')`. Nằm trên đúng đường đi của
  official run T-06.
- F-E2A1-02 (TRUNG BÌNH-CAO) — `official_eligibility` chỉ duyệt entry CÓ trong lineage, không
  kiểm lineage phủ đủ ba series mà `load_dataset` nạp. Lineage khai 1/3 series (nhãn real, hash
  đúng) cho `(True, 'verified')` trong khi hai series còn lại vẫn synthetic.

FINDING KHÁC: F-E2A1-03 (provenance im lặng suy biến ngoài editable install), F-E2A1-04 (không
phân biệt worktree bẩn), F-E2A1-05 và F-E2A1-07 (hai assertion không thể FAIL vì lý do chúng
tuyên bố — cùng LỚP defect đã hạ gục E2 lần trước, khác hình thức), F-E2A1-06 (lockfile không
ghim tzdata hệ điều hành), F-E2A1-08 (`data_source: "mixed"` không nằm trong taxonomy, official
run thật gần như chắc chắn sinh ra), F-E2A1-09 (`run_controls` ghi `official` không tính đường dev).

Executed By:
Phiên reviewer độc lập (Opus / xhigh), không phải người cài đặt

Timestamp:
2026-08-24

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Mức evidence yêu cầu được thoả (E1 cho toàn bộ; E2 cho CHECK-A1-11)
- [ ] Không defect nghiêm trọng nào chưa xử lý
- [ ] `docs/CONVENTIONS.md` ghi quy ước phân loại nguồn dữ liệu
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-006 và RSK-008 được cập nhật trạng thái
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Trạng thái gate sau E2 lần BA (2026-09-01)

WP-A1 **KHÔNG DONE**. Nhưng bản chất đã đổi so với hai vòng trước: bất biến đã ĐỨNG VỮNG.

| Check | Trạng thái |
|---|---|
| A1-01 … A1-10 | **PASS** — cả 10, bằng chứng E2 vòng ba tự thu |
| A1-11 | **FAIL** |

Hai finding CHẶN của vòng hai đã ĐÓNG, reviewer tự tái hiện trên mã `bd7c5ff` rồi đối chiếu HEAD:

- F-E2A1-01: `bd7c5ff` cho series rỗng `(True,'verified')`; HEAD cho `empty_series`. Stub fetch
  năm kịch bản: "không cơ chế nào đóng góp" nay ra `unknown` + `empty_series`.
- F-E2A1-02: `bd7c5ff` cho coverage 1/3 và series thừa (lineage tự nhất quán hash) đều
  `(True,'verified')`; HEAD cho `missing_required_series` / `unexpected_series`.

MUTATION-6 được reviewer chứng minh bằng `ast` (tránh bẫy regex docstring): 24/27 test ĐỎ, gồm
cả hai positive control. Oracle VALID.

CHECK-A1-09 chuyển NOT_TESTED → PASS: reviewer tự dựng venv sạch, cài từ lockfile thành công
(tiền đề "proxy chặn cài gói" của S007 là SAI), 15/15 pin đúng, ba process độc lập với
`PYTHONHASHSEED` khác nhau, metric trùng khớp trên dataset có OOS số thật. Đây là xác nhận E2
mà PRE-S008 §15 / U-4 yêu cầu.

### Vì sao A1-11 vẫn FAIL

1. **F-E2A1-03 còn mở và reviewer NÂNG lên mức CAO.** `reporting.py` không đổi một dòng ở S008.
   Cài project vào venv sạch từ lockfile — đúng môi trường mà CHECK-A1-09 bắt buộc — thì record
   ghi `code_commit='unknown'` và `dependency_lock_hash='no-lockfile'`, im lặng, không cảnh báo.
   Máy chạy official run là máy lạ, và Master Index §6 CẤM chạy lại official run để sửa.
2. **F-E2A1R3-03 — sai lệch với contract đã FROZEN.** Case 13 đòi reason `dev_limit_set`; mã ghi
   `official_reason: "verified"`. Mã `dev_limit_set` không tồn tại trong `src/`. `test_ec_13`
   không assert reason nên oracle không bắt được — cùng lớp lỗ hổng đã hạ gục E2 vòng một.
3. **F-E2A1R3-01 (TB)** — phòng thủ `empty_series` đặt trên `row_count`, trường KHÔNG được hash
   nào phủ và không bao giờ đối chiếu với file. Làm rỗng parquet thật rồi sửa đúng một số nguyên
   trong `lineage.json` cho lại `(True,'verified')`. Đây chính là lớp vừa dùng để đóng một finding
   CHẶN.
4. **Exit Criteria còn hở**: `docs/CONVENTIONS.md` chưa ghi coverage invariant và `empty_series`
   (F-E2A1R3-06); RSK-006/RSK-008 chưa cập nhật; chưa viết session handoff.

Bảy finding mới: F-E2A1R3-01…07. Bốn finding cũ còn mở: F-E2A1-03 (CAO), F-E2A1-04, F-E2A1-06,
F-E2A1-08, F-E2A1-09 — hai cái sau có bằng chứng mới (`data_source='mixed'` xuất hiện trên run
ĐỦ TƯ CÁCH official; `RANDOM_CONTROL` ghi `official=true` ở `n_sims=200`, tức đường dev).

**GATE-A không đóng được → T-06 chưa mở.**

Theo `ESCALATION_PROTOCOL.md` và chỉ thị S008 §23: E2 vòng ba FAIL thì **KHÔNG mở vòng patch thứ
tư**. Dừng và escalate. Reviewer khuyến nghị `VERIFICATION_DEPTH` chứ không phải
`CAPABILITY_CEILING`, và ghi nhận mọi follow-up bắt buộc đều nằm trong Expected Touch Area nên
không cần Scope Expansion — chủ dự án quyết.

## Trạng thái gate sau E2 lần hai (2026-08-24)

WP-A1 **KHÔNG DONE**. Completion Gate chưa đóng:

| Check | Trạng thái |
|---|---|
| A1-01, A1-02, A1-03, A1-04, A1-06, A1-08, A1-10 | PASS (E1 + E2 tự chạy lại) |
| A1-05, A1-07 | FAIL (F-E2A1-01, F-E2A1-02) |
| A1-09 | NOT_TESTED (vế môi trường sạch từ lockfile) |
| A1-11 | FAIL (E2 FAIL) |

Exit Criteria chưa thoả: "100% REQUIRED checks PASS" và "không defect nghiêm trọng nào chưa xử lý".
Ba mục còn hở: `PROJECT/PROJECT_PROGRESS.md` chưa cập nhật, RSK-006/RSK-008 chưa cập nhật trạng
thái, chưa viết session handoff. **GATE-A không đóng được → T-06 chưa mở.**

ĐỀ XUẤT ESCALATION (chủ dự án quyết, không tự chọn): reviewer khuyến nghị `VERIFICATION_DEPTH`
— giữ Tier C, nâng Effort xhigh → max — thay vì `CAPABILITY_CEILING`, với lý do kiến trúc dẫn xuất
đã đúng và hai defect chặn là hai GIÁ TRỊ MẶC ĐỊNH fail-open, không phải bế tắc về cách tiếp cận.
Lưu ý ngược lại: đây là lần thứ HAI E2 bác bỏ gói này, nên `ESCALATION_PROTOCOL.md` ("không vá đi
vá lại một implementation đang hỏng") áp dụng — vòng sửa thứ ba cần chủ dự án phê duyệt tường minh
chứ không tự động tiếp tục.

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

---

## REPAIR CYCLE CUỐI — S017 (2026-09-03), `OWNER_EXTENSION` theo `DEC-027`

Chủ dự án cấp `CAP-PROV` **+1 repair cycle** (`allowed 2 → 3`, `used 2 → 3`, `remaining 0`) với
mục tiêu DUY NHẤT: đóng `F-E2A1-03` và `F-E2A1R3-03` trong **cùng một** chu kỳ. Hạng mục thứ ba
(`F-E2A1R3-06` + `F-E2A1-08`) đóng bằng **docs-only, production diff = 0**, không tiêu chu kỳ
riêng — đúng tiền lệ ledger (Decision pack PRE-S008, `2f20e6c..bd7c5ff`).

### (1) `F-E2A1-03` — ĐÓNG. Provenance không còn suy biến im lặng

Bản sửa ở `reporting.py`: phân giải `code_commit` và `dependency_lock_hash` **TRƯỚC** khi ghi
bất cứ file nào. Nếu run được ghi `official` mà một trong hai không phân giải được →
`ProvenanceUnresolvedError`, và **chưa artifact nào được tạo**. Đây là điểm cốt lõi: Master
Index §6 cấm chạy lại official run, nên một official record thiếu provenance đã ghi ra đĩa là
mất vĩnh viễn; từ chối TRƯỚC khi ghi thì chi phí chỉ là chạy lại trong môi trường đúng.

Đường KHÔNG official vẫn chạy được trong môi trường thiếu git/lockfile — nhưng record nay mang
`provenance_resolved: false` và `provenance_unresolved: [...]` tường minh, thay vì để người đọc
tự biết rằng `"unknown"` / `"no-lockfile"` là giá trị suy biến.

Bằng chứng E1 (`tests/test_wp_a1_legacy_gate_repair.py`), tất cả ĐỎ trước khi sửa:
`test_a1r_b1_official_run_refuses_unresolved_code_commit`;
`test_a1r_b1_official_run_refuses_missing_lockfile`;
`test_a1r_b1_nothing_is_written_when_provenance_unresolved` (khẳng định KHÔNG có
`backtest_runs.jsonl` và KHÔNG có `*_metrics.json` sau khi từ chối);
`test_a1r_b1_non_official_run_still_records_degraded_state`;
`test_a1r_b1_official_run_with_resolvable_provenance_still_works` — đối chứng dương, thiếu ca
này thì một bản sửa "luôn luôn nổ" cũng làm các ca kia xanh.

**Hệ quả vận hành phải biết TRƯỚC khi chạy `T-06`:** official run bắt buộc chạy từ một git
checkout có lockfile, không phải từ một bản sao mã trần. `BLK-001` dự kiến chạy trên máy chủ dự
án hoặc VPS nước ngoài — điều kiện này phải được thoả ở đó, nếu không `save_run` sẽ từ chối.

### (2) `F-E2A1R3-03` — ĐÓNG. Contract case 13 được thi hành

Bản sửa ở `pipeline.py`: hàm `_official_reason(prep, dev_limit)` áp tại **cả ba** enforcement
point mà hợp đồng nêu tên (`run_gate1`, `run_gate2`, `run_gate3`). `dev_limit != None` trên nền
dataset hợp lệ → `official_reason = "dev_limit_set"`. `run_controls` KHÔNG có tham số
`dev_limit` nên không nằm trong hợp đồng và không bị đụng.

Khi dataset **tự nó** đã không đủ tư cách, lý do GỐC của dataset được giữ: hợp đồng chỉ định
nghĩa case 13 trên nền ca (12) hợp lệ, và che một nguyên nhân sâu hơn bằng `dev_limit_set` sẽ
lặp lại đúng khiếm khuyết đang được sửa, chỉ đổi chiều.

Bằng chứng E1, ĐỎ trước khi sửa với chữ ký `assert 'verified' == 'dev_limit_set'`:
`test_a1r_b2_gate1/gate2/gate3_dev_limit_sets_canonical_reason`;
`test_a1r_b2_reason_written_into_run_record` (lý do phải tới ARTIFACT, không chỉ nằm trong
payload trong bộ nhớ). Ba ca đối chứng chặn bản sửa lười:
`..._no_dev_limit_keeps_dataset_reason` (không dev_limit thì vẫn `verified`);
`..._ineligible_dataset_keeps_its_own_reason`;
`..._dev_limit_set_is_not_a_valid_source_or_eligibility_code` — sai TẦNG: nếu ai cài mã này vào
`official_eligibility` thì dataset bị coi là không hợp lệ ngay cả khi không chạy dev.

### (3) `F-E2A1R3-06` + `F-E2A1-08` — ĐÓNG bằng tài liệu, production diff = 0

`docs/CONVENTIONS.md` nay ghi **hai TẦNG** nhãn nguồn: bảng bốn giá trị là nhãn **series** và là
thứ quyết định tư cách official; `mixed` là nhãn **dataset-level, chỉ mô tả**, sinh khi các
series không cùng nguồn, và KHÔNG phải lối tắt qua cổng official vì `official_eligibility` kiểm
per-series với `REAL_SOURCES`. Bổ sung hai mã lý do chưa từng được ghi ở đâu: `empty_series` và
`source_not_real`. Coverage invariant đã được WP-A4/S010 ghi từ trước.

Kiểm lại mục mà bản disposition nêu là "mã lý do lỗi thời trong Evidence `CHECK-A1-06`":
Evidence đó đang ghi `source_not_real:BTCUSDT_1d='synthetic'` — **đúng hiện trạng mã**, không có
gì lỗi thời để sửa. Không sửa thừa.

### Phạm vi đã giữ

Production diff của chu kỳ này: **2 file** — `reporting.py`, `pipeline.py`. `git diff` trên
`engine.py`, `regime.py`, `ladders.py`, `capital.py`, `score.py`, `gates.py`, `verdict.py`,
`metrics.py` = **rỗng** ⇒ không đụng logic financial/algorithm, đúng `DEC-027` điểm 3.

`RSK-006` (cao → trung bình) và `RSK-008` (cao → thấp) đã cập nhật tại
`PROJECT/PROJECT_PROGRESS.md`, kèm phần dư ghi rõ chứ không tuyên bố đóng hoàn toàn.

### Còn lại của `CHECK-A1-11`

Ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED` nay đã đóng. `CHECK-A1-11` là **E2** — cần một
phiên reviewer độc lập theo "Solo Independent Review Procedure" xác nhận, và đó là bước kế
tiếp trước khi chủ dự án xét `WP-A1 → DONE`. Phiên S017 KHÔNG tự đánh `CHECK-A1-11` = PASS.
