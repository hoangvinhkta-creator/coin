# E2 INDEPENDENT REVIEW

Review ID:
E2-WP-A1-003 (VÒNG BA)

Task / Release:
WP-A1 — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức
(`docs/tasks/WP-A1-provenance-va-tai-lap.md`), thoả CHECK-A1-11

Reviewer Session:
Phiên rà soát độc lập vòng ba — reviewer KHÔNG phải người cài đặt, KHÔNG sửa `src/`,
KHÔNG sửa test đã có, KHÔNG commit

Executed By:
Reviewer độc lập (Opus / xhigh)

Timestamp:
2026-09-01

Commit được rà soát:
`a0c278a02a84d4e1fe1eee792cf5e7f9a57545b4` — nhánh `claude/wp-a1-provenance-v67k9h`

Trạng thái cây làm việc khi rà soát: `git status --porcelain` RỖNG trước và sau toàn bộ
phiên. Mọi đột biến được gieo trong `git worktree` tạm ngoài repo, không chạm cây chính.

## Scope

Rà soát độc lập lượt remediation vòng ba (`a0c278a`) chồng lên decision pack `bd7c5ff` và
hai vòng E2 đã bác bỏ gói này (`f49776e`…`2f20e6c`).

Trong phạm vi:

- Bắt đầu từ TRẠNG THÁI REPO. Mọi câu "PASS" trong `docs/tasks/` và trong commit message
  được coi là tường thuật không đáng tin cho tới khi reviewer tự kiểm chứng.
- Tự chạy lại CHECK-A1-05, A1-06, A1-07, A1-09, A1-10; đối chiếu toàn bộ A1-01…A1-10 với
  Completion Gate đã FROZEN.
- Chủ động TÌM ĐƯỜNG PHÁ cờ `official` (40+ probe đối kháng), không chỉ xác nhận đường
  hạnh phúc.
- MUTATION-6 (và thêm MUTATION-2, MUTATION-3) để chứng minh oracle có giá trị, không chỉ
  "hợp lệ theo thiết kế".
- Dựng venv SẠCH của riêng reviewer từ `pyproject.lock` (KHÔNG dùng `venv_a109` mà phiên
  cài đặt để lại trong scratchpad).
- Kiểm chất lượng test: assertion vô hiệu, PASS giả, test bị làm yếu so với `2f20e6c`.
- Kiểm lại toàn bộ 9 finding F-E2A1-01…09 trên HEAD mới.

Ngoài phạm vi: chạy `ethdca fetch` thật (BLK-001 chặn mạng Binance) — đường `fetch` được
kiểm bằng stub I/O; sửa mã; commit.

## Inputs Read

- Trạng thái repo tại `a0c278a`; `git diff bd7c5ff..HEAD` và `git diff 2f20e6c..HEAD`.
- Completion Gate đã FROZEN trong `docs/tasks/WP-A1-provenance-va-tai-lap.md`.
- `docs/decisions/PRE-S008-WP-A1-decision-pack.md` — contract 20 case (§10), REQUIRED_SERIES
  (§9), positive control (§11), mutation matrix (§12), reproducibility floor (§13),
  hash semantics (§14), E2 finding authority (§15).
- `docs/reviews/E2-WP-A1-provenance.md` — 9 finding vòng hai.
- Mã: `src/eth_dca_os/data/{dataset,fetch,synth}.py`, `pipeline.py`, `reporting.py`,
  `cli.py`, `benchmarks.py`, `windows.py`.
- Test: `tests/test_wp_a1_eligibility_contract.py`, `tests/test_wp_a1_provenance.py`.
- `docs/CONVENTIONS.md`, `governance/core/EVIDENCE_STANDARD.md`,
  `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`,
  `PROJECT/PROJECT_PROGRESS.md`, `docs/sessions/`.

Toàn bộ bằng chứng dưới đây do reviewer TỰ THU. Không con số nào chép lại từ báo cáo của
người cài đặt.

## Diff thực tế được rà soát

`git diff bd7c5ff..HEAD` chạm đúng bốn file:

    src/eth_dca_os/data/dataset.py            +48 / -11   (REQUIRED_SERIES + official_eligibility)
    src/eth_dca_os/data/fetch.py               +5 / -2    (mặc định SOURCE_UNKNOWN)
    tests/test_wp_a1_eligibility_contract.py  +333       (MỚI, 22 hàm test / 27 test item)
    tests/test_wp_a1_provenance.py            +17 / -6   (sửa F-E2A1-05 và F-E2A1-07)

KHÔNG có file `docs/` nào bị sửa trong `a0c278a`. Hệ quả: Completion Gate trong task file
vẫn đang ghi nguyên trạng thái vòng hai (A1-05 FAIL, A1-07 FAIL, A1-09 NOT_TESTED,
A1-11 FAIL). Commit message của `a0c278a` cũng tự ghi: "commit này để tree không treo,
**không phải tuyên bố đã xác minh xong**". Vì vậy vòng này không có tuyên bố PASS mới nào
của người cài đặt để bác — reviewer xác minh trực tiếp từ mã.

## Independent Verification

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-A1-01 | PASS | E2 | Record thật của run reviewer tự chạy (`run_gate1`, dev_limit=None): đủ 9 khoá provenance, không khoá nào rỗng, `data_source='synthetic'`, `official=False`. CẢNH BÁO đi kèm: xem F-E2A1-03 — trong venv sạch cài từ lockfile, hai khoá suy biến thành `'no-lockfile'` / `'unknown'` mà không cảnh báo. | Reviewer | 2026-09-01 |
| CHECK-A1-02 | PASS | E2 | Reviewer tự chạy `run_gate2`/`run_gate3`: record GATE2 = `e5b60b6f…f46`, GATE3 = `7e9ce7c0…23a` — đều 64 hex, khác rỗng. Phép đối chiếu với `manifest_hash([_cfg_row(c) …])` do `test_a1_02_manifest_hash_gate2_gate3` thực hiện trong lần chạy suite của reviewer. | Reviewer | 2026-09-01 |
| CHECK-A1-03 | PASS | E2 | Record của run reviewer: `code_commit='a0c278a02a84d4e1fe1eee792cf5e7f9a57545b4'` = `git rev-parse HEAD`; `simulation_seed=8218346625117296390` (int, ≠ `master_seed`=42, trùng nhau qua 4 process độc lập). | Reviewer | 2026-09-01 |
| CHECK-A1-04 | PASS | E2 | `StrategyConfig().created_at` / `ExecutionConfig().created_at` có mặt, ISO8601 UTC; `'created_at' in _cfg_row(BASELINE_STRATEGY)` = False; `BASELINE_STRATEGY.hash = f782f990…1b7b` và `GATE1_LOW_FRICTION.hash = 5888866f…6ec9` TRÙNG KHỚP hai giá trị mà Completion Gate ghim. | Reviewer | 2026-09-01 |
| CHECK-A1-05 | PASS | E2 | Đường `synth`: nhãn `synthetic` cho cả dataset lẫn từng series. Đường `fetch`: reviewer tự dựng stub `fetch_month_archive`/`fetch_klines` (không cần mạng) cho 5 kịch bản — archive-only, REST-only, cả hai, KHÔNG cơ chế nào, archive trả DataFrame rỗng. Nhãn đúng theo TỪNG series ở cả 5. Kịch bản "không cơ chế nào" nay cho `unknown` + `empty_series` (trước là `binance_rest` + official). F-E2A1-01 ĐÓNG. | Reviewer | 2026-09-01 |
| CHECK-A1-06 | PASS | E2 | `Prepared(synth).official_eligible = False`, reason `source_not_real:ETHUSDT_1d='synthetic'`. Reviewer chạy `ethdca run all` KHÔNG `--dev-limit` qua CLI thật: record GATE1 ghi `official=False`, `data_source='synthetic'`, metrics ghi `dev_limit=None` và `official_reason="source_not_real:ETHUSDT_1d='synthetic'"`. Gate 2/Gate 3 xem ghi chú §9 (giới hạn thời lượng). | Reviewer | 2026-09-01 |
| CHECK-A1-07 | PASS | E2 | 40+ probe đối kháng do reviewer tự dựng (bảng §"Probe đối kháng"). Không tồn tại cờ CLI, biến môi trường (grep `environ`/`getenv` trên TOÀN BỘ `src/` = 0 hit), tham số hay đường ghi nào ép được `official`. Hai đường fail-open còn lại đều thuộc lớp "vận hành sửa tay `lineage.json`" mà Completion Gate và `docs/CONVENTIONS.md` đã công bố là giới hạn — nhưng một trong hai (row_count) CHƯA được công bố: xem F-E2A1R3-01. | Reviewer | 2026-09-01 |
| CHECK-A1-08 | PASS | E2 | `pyproject.lock` 15 dòng, 15/15 dùng `==`. `sha256(pyproject.lock)` reviewer tự tính = `9ea0150fcf27c12d39335db95a01151a79e2f94aa64b0eda722fd939f76c4d9a` = `dependency_lock_hash` trong record. Trong venv sạch của reviewer, 15/15 pin resolve ĐÚNG phiên bản, 0 lệch, 0 gói thừa ngoài lock. | Reviewer | 2026-09-01 |
| CHECK-A1-09 | PASS | E2 | Vế trước đây NOT_TESTED nay đã chạy: reviewer tự dựng venv SẠCH (`python -m venv`, không dùng môi trường có sẵn, không dùng `venv_a109` của phiên cài đặt), `pip install -r pyproject.lock` THÀNH CÔNG, cài project, chạy hai process ĐỘC LẬP với `PYTHONHASHSEED` khác nhau (0 và 987654) + một process thứ ba trong môi trường có sẵn (424242). Toàn bộ metric trùng khớp tuyệt đối bằng `==`, dataset có OOS SỐ THẬT. | Reviewer | 2026-09-01 |
| CHECK-A1-10 | PASS | E2 | Reviewer tự chạy `pytest tests/` trên cây sạch tại `a0c278a`: **157 test collected, 157 PASS, exit code 0**, không FAIL, không skip (`pyproject.toml` đặt `addopts="-q"` nên dòng tóm tắt bị nén; bằng chứng là exit code 0 cộng 72+72+13 dấu chấm khớp đúng 157 test collected). Đối chiếu BEFORE/AFTER `bd7c5ff` vs `a0c278a` trên CÙNG dataset + seed qua `git worktree`: toàn bộ metric mô phỏng GIỐNG HỆT; chỉ metadata và `official_reason` đổi. | Reviewer | 2026-09-01 |
| CHECK-A1-11 | FAIL | E2 | Kết luận của chính báo cáo này — xem §Conclusion. 10/10 check A1-01…A1-10 PASS, nhưng Exit Criteria chưa thoả, follow-up BẮT BUỘC F-E2A1-03 của vòng hai bị bỏ qua hoàn toàn, và có một sai lệch với contract đã FROZEN (case 13). | Reviewer | 2026-09-01 |

Điểm reviewer tự chấm trên CHECK-A1-01…A1-10: **10 PASS / 0 FAIL / 0 NOT_TESTED**.

## Bằng chứng độc lập — chi tiết

### 1. CHECK-A1-05 — đường `fetch` kiểm được mà không cần mạng

Reviewer tự dựng lại kỹ thuật stub mà vòng hai đã dùng để chứng minh F-E2A1-01, rồi chạy
`fetch_all` với `fetch_month_archive` / `fetch_klines` bị thay bằng hàm giả:

| Kịch bản | `sources` theo từng series | `row_count` | `official_eligibility` |
|---|---|---|---|
| Archive có, REST rỗng | `binance_bulk_archive` ×3 | > 0 | `(True, 'verified')` |
| Archive 404, REST có | `binance_rest` ×3 | > 0 | `(True, 'verified')` |
| Cả hai đóng góp | `binance_bulk_archive` ×3, `source_detail` ghi cả hai | > 0 | `(True, 'verified')` |
| **KHÔNG cơ chế nào** | **`unknown` ×3** | **0** | **`(False, 'empty_series:ETHUSDT_1d')`** |
| Archive trả DataFrame RỖNG | `binance_bulk_archive` ×3 | 0 | `(False, 'empty_series:ETHUSDT_1d')` |

Dòng thứ tư chính là F-E2A1-01. Trên mã cũ nó cho `(True, 'verified')`. Nay có HAI lớp
chặn độc lập (nhãn `unknown` và `row_count == 0`), nên vẫn fail-closed kể cả khi một lớp
bị vô hiệu. Dòng thứ năm là biến thể reviewer tự nghĩ thêm (archive trả về DataFrame rỗng
thay vì `None`): `used` vẫn được gắn `binance_bulk_archive` — tức lớp nhãn KHÔNG cứu được —
và chỉ lớp `empty_series` chặn lại. Điều này cho thấy lớp `row_count` là lớp phòng thủ
thật sự chịu tải, và vì thế F-E2A1R3-01 dưới đây có trọng lượng.

### 2. CHECK-A1-07 — probe đối kháng (reviewer tự dựng, 40+ trường hợp)

Positive control: lineage nguyên vẹn nhãn `binance_bulk_archive` → `(True, 'verified')`.
Cổng MỞ ĐƯỢC, nên phần fail-closed dưới đây không phải là "một cổng đóng vĩnh viễn".

| Nhóm | Trường hợp | Kết quả |
|---|---|---|
| Nguồn | `source` viết HOA / thừa khoảng trắng / `None` / thiếu khoá | `source_not_real:…` (đóng) |
| Nguồn | `source` là **list** hoặc **dict** | **TypeError không bắt** → F-E2A1R3-02 |
| Nguồn | sửa tay `synthetic` → `binance_rest`, giữ nguyên hash | `(True,'verified')` — giới hạn ĐÃ CÔNG BỐ (F-PRE008-01) |
| row_count | series RỖNG THẬT + `row_count` bịa 140156, mọi hash vẫn khớp | **`(True,'verified')`** → F-E2A1R3-01 |
| row_count | `row_count` là chuỗi `"999"` / `True` | `(True,'verified')` → F-E2A1R3-01 |
| row_count | âm / `0.5` | `empty_series:…` (đóng) |
| row_count | `NaN` / thiếu khoá | `lineage_malformed` (đóng) |
| Coverage | thiếu 1 series | `missing_required_series:BTCUSDT_1d` (đóng) |
| Coverage | trùng lặp entry | `duplicate_series:BTCUSDT_1d` (đóng) |
| Coverage | series thừa trong lineage | `unexpected_series:DOGEUSDT_1d` (đóng) |
| Coverage | `files: []` | `missing_required_series:ETHUSDT_1d` (đóng) |
| Coverage | parquet thừa trên ĐĨA, `lineage.json` cũ 3 entry | `(True,'verified')` → F-E2A1R3-04 (mức THẤP) |
| Khoá | `symbol='ETHUSDT_1d', interval=''` (thử alias khoá) | `unexpected_series:ETHUSDT_1d_` (đóng) |
| Khoá | `interval='1d '` thừa space / `symbol=None` | đóng |
| Checksum | `file_hash` rỗng / `None` / thiếu | `checksum_missing:…` (đóng) |
| Checksum | `dataset_hash` sai / thiếu | `dataset_hash_mismatch` (đóng) |
| Checksum | parquet bị sửa SAU khi build lineage | `file_hash_mismatch:…` (đóng) |
| Checksum | parquet bị sửa + lineage dựng lại tự nhất quán | `(True,'verified')` — giới hạn ĐÃ CÔNG BỐ |
| Lineage | `None` | `lineage_missing` (đóng) |
| Lineage | chuỗi / int / list / `files` không phải list / `files` chứa list / `{}` / `files=None` | `lineage_malformed` (đóng) |
| Bề mặt ép | `--official`, `--force-official`, `--source`, `--real-data` | KHÔNG tồn tại trong `cli.py` |
| Bề mặt ép | `os.environ` / `os.getenv` | **0 hit trên TOÀN BỘ `src/`** (reviewer grep độc lập) |
| Bề mặt ép | tham số hàm | `official_eligibility(raw_dir, lineage)` — đúng hai tham số |
| Bề mặt ép | nơi ghi record | `reporting` không import `official_eligibility` |
| Bề mặt ép | `ethdca verdict` đọc `pipeline_state.json` từ đĩa | KHÔNG gọi `run_verdict`, KHÔNG ghi record mới — chỉ IN lại verdict đã lưu. Sửa tay `"official": true` trong file state KHÔNG tạo được record official. Đường này reviewer kiểm riêng vì `run_verdict` cố ý không tính lại eligibility mà tin payload Gate 2/3; may là payload đó chỉ đến từ bộ nhớ của cùng một `Prepared`. |

Thứ tự kiểm là TẤT ĐỊNH và phân biệt được nguyên nhân: `sorted(by_key)` cho `unexpected`,
thứ tự `REQUIRED_SERIES` cho `missing` / `checksum_missing` / `empty_series` /
`source_not_real`. Reviewer xác nhận không có case nào bị gộp về một mã chung.

### 3. MUTATION — oracle có giá trị THẬT, không chỉ "VALID theo thiết kế"

Đột biến được gieo trong `git worktree` tạm (`HEAD` detached), KHÔNG chạm cây chính, và
được chèn bằng công cụ dựa trên `ast` — chèn vào ĐẦU THÂN HÀM sau docstring, không dùng
regex (regex `.*?"""` non-greedy dừng ở nháy MỞ và đột biến sẽ vô hiệu; reviewer tránh
đúng bẫy đó). Mỗi đột biến được xác minh HAI lần trước khi kết luận: in lại mã nguồn đã
sửa, và gọi hàm ở runtime để thấy hành vi đã đổi.

| ID | Đột biến | Kỳ vọng | Kết quả THỰC TẾ |
|---|---|---|---|
| MUTATION-6 | `official_eligibility` luôn trả `(False, "MUTANT6")` | Positive control PHẢI ĐỎ | **24/27 test ĐỎ**, gồm cả `test_ec_12_positive_control_eligibility` và `test_ec_20_positive_control_gate_level` |
| MUTATION-2 | Bỏ nhánh `empty_series` | `T-EC-03` đỏ | Đúng 1 test đỏ: `test_ec_03_empty_canonical_series_not_official` (`assert True is False` — tức mã cũ THẬT SỰ cho official) |
| MUTATION-3 | Bỏ kiểm phủ đủ/thừa `REQUIRED_SERIES` | 4+ test đỏ | Đúng 6 test đỏ: `test_ec_04/05/07/08/18/19` |

MUTATION-6 là điều kiện sống còn theo §12 decision pack, và nó **PROVEN**, không còn là
"VALID theo thiết kế". Đáng chú ý: phần lớn case fail-closed cũng đỏ dưới MUTATION-6, vì
chúng khẳng định MÃ LÝ DO cụ thể chứ không chỉ `ok is False` — một cổng hằng-False không
qua nổi. Đây là điểm thiết kế test mạnh, reviewer ghi nhận.

MUTATION-2 và MUTATION-3 đồng thời là bằng chứng ngược chiều rằng F-E2A1-01 (vế
`row_count == 0`) và F-E2A1-02 là defect CÓ THẬT trên mã trước `a0c278a`, chứ không phải
finding suy diễn.

### 4. Positive control — kiểm tra thật, không tin mô tả

Reviewer đọc trực tiếp `tests/test_wp_a1_eligibility_contract.py`:

- Fixture `real_like_raw` gọi `synth.generate` → parquet THẬT trên đĩa, ba series
  `row_count > 0`, rồi `build_lineage(raw, SOURCE_BULK_ARCHIVE)` — checksum được TÍNH THẬT
  từ chính file fixture.
- `grep` toàn file cho `mock` / `monkeypatch` / `patch` / `MagicMock`: đúng **2 hit, cả hai
  nằm trong docstring**, không có `import unittest.mock`, không có fixture `monkeypatch`,
  không một lời gọi patch nào. Không có chỗ nào thay `verify_lineage`, `load_dataset` hay
  `official_eligibility`. (`tests/test_wp_a1_provenance.py`: 0 hit.)
- `test_ec_20` chạy `Prepared` + `run_gate1` THẬT với `dev_limit=None` và bắt buộc
  `official is True` ở cả payload lẫn `run_record`.
- Chỉ NHÃN nguồn là do fixture đặt — nhãn là dữ liệu đầu vào, không phải mock. Giới hạn
  này được nêu thẳng trong docstring fixture và trùng với §11 decision pack.

Kết luận: positive control THẬT.

### 5. CHECK-A1-09 — venv sạch dựng từ lockfile (vế trước đây NOT_TESTED)

Reviewer KHÔNG dùng `venv_a109` mà phiên cài đặt để lại trong scratchpad; reviewer tự dựng
venv mới:

    python -m venv <venv riêng của reviewer>
    pip install -r pyproject.lock        -> THÀNH CÔNG (không bị proxy chặn)
    pip install --no-deps <worktree HEAD> -> eth-dca-os 2.1.5

Đối chiếu resolved versions với exact pins: **15/15 ĐÚNG, 0 lệch, 0 gói thiếu, 0 gói thừa
ngoài lock** (certifi 2026.2.25, charset-normalizer 3.4.6, idna 3.11, iniconfig 2.3.0,
numpy 2.4.6, packaging 24.0, pandas 3.0.5, pluggy 1.6.0, pyarrow 25.0.1, Pygments 2.21.0,
pytest 9.1.1, python-dateutil 2.9.0.post0, requests 2.33.1, six 1.16.0, urllib3 2.6.3).

Ba process ĐỘC LẬP trên CÙNG dataset (`dataset_hash =
b3e9a146186f9beb0376476031cd0c4bec0b228c272b7b7f4b6037b4b27cebfc`, synth
2020-01-01…2025-06-30, seed 42):

| Run | Môi trường | PYTHONHASHSEED |
|---|---|---|
| A | venv SẠCH từ lockfile | 0 |
| B | venv SẠCH từ lockfile | 987654 |
| C | môi trường có sẵn (editable) | 424242 |

Kết quả so bằng `==`, không dung sai, trên `ae_by_window`, `primary_median`,
`pooled_median_descriptive`, `gate1`, `oos`, `bootstrap_descriptive`, `concentration`,
`cash_ratio`, `counters_w5`, `benchmarks`, `diagnostics`:

    A vs B  : metric giống nhau = True
    A vs C  : metric giống nhau = True

Dataset có OOS SỐ THẬT, không NaN — sàn D của §13 decision pack:

    oos = {'ae': 79.56325238738884, 'oos_months': 6, 'short_oos': True, ...}
    primary_median = 96.37463507136648
    ae_by_window   = W1 90.26413485634406  W2 108.41083354064955  W3 94.05528152598211
                     W4 91.63293766677863  W5 100.77737447319618  W6 93.43144984771672
                     W7 99.65677829777444  W8 100.66453626433850  W9 98.36405569246651

`run_record` giữa A và B chỉ khác ở `created_at`, `run_id`, `metrics_path` — mọi trường
provenance còn lại trùng khớp.

Toàn bộ sàn §13 (A…F) đã thoả, trong đó F ("ít nhất một lần chạy trong venv SẠCH dựng từ
lockfile") lần đầu được reviewer độc lập xác nhận. **Đề xuất (a) của PRE-S008 §15 — chuyển
A1-09 khỏi NOT_TESTED — được reviewer E2 XÁC NHẬN.**

### 6. CHECK-A1-10 — non-regression `bd7c5ff` → `a0c278a`

Chạy `run_gate1` ở hai phiên bản mã qua `git worktree`, cùng dataset và seed:

    Metric mô phỏng giống hệt nhau : True
    dataset_hash    : b3e9a146…cebfc  (không đổi)
    primary_median  : 96.37463507136648   (cả hai)
    oos.ae          : 79.56325238738884   (cả hai — SỐ THẬT, không phải NaN)
    ae_by_window / bootstrap_descriptive / benchmarks / diagnostics : giống

Chỉ metadata và phân loại official đổi, đúng như cho phép:

    official_eligible  BEFORE/AFTER : False / False
    official_reason    BEFORE       : source_not_real:BTCUSDT_1d='synthetic'
    official_reason    AFTER        : source_not_real:ETHUSDT_1d='synthetic'
    run_record khác ở              : code_commit, created_at, run_id, metrics_path

Reviewer xác nhận `git diff 2f20e6c bd7c5ff -- src/ tests/` là **RỖNG** — `bd7c5ff` chỉ
thêm tài liệu. Vì vậy phép so `bd7c5ff` ↔ `a0c278a` phủ TRỌN VẸN delta mã của vòng ba, và
nối liền với phép so `d72fbc4` ↔ `2f20e6c` mà vòng hai đã thực hiện.

Đổi tên series trong `official_reason` là hệ quả CÓ CHỦ ĐÍCH của việc duyệt theo thứ tự
canonical `REQUIRED_SERIES` thay vì thứ tự glob — nó làm mã lý do tất định hơn. Ghi chú:
Evidence của CHECK-A1-06 trong task file đang trích `source_not_real:BTCUSDT_1d='synthetic'`,
nay đã cũ (xem F-E2A1R3-06).

### 7. Rà "một nguồn sự thật" — có chỗ nào tự diễn giải `official` riêng không?

Reviewer đọc từng nơi tính `official` trong `pipeline.py`:

| Nơi | Công thức | Nhận xét |
|---|---|---|
| `Prepared.__init__` | `official_eligibility(self.raw_dir, self.lineage)` | Enforcement point duy nhất, gọi ĐÚNG một lần |
| `run_gate1` | `prep.official_eligible and dev_limit is None` | Nhất quán |
| `run_gate2` | `prep.official_eligible and limit is None` | Nhất quán |
| `run_gate3` | `prep.official_eligible and limit is None` | Nhất quán |
| `run_controls` | `prep.official_eligible` | **LỆCH — thiếu điều kiện dev (F-E2A1-09)** |
| `run_verdict` | `g2['official'] and g3['official']` | Dẫn xuất, không tính lại eligibility |
| `reporting.save_run` | chỉ ghi lại `official` được truyền vào | Không tự suy luận (reviewer xác nhận `reporting` không import `official_eligibility`) |

Nghĩa là kiến trúc "một nguồn sự thật" ĐÚNG cho phần eligibility; chỗ duy nhất diễn giải
riêng là điều kiện dev ở `run_controls`, và đó đúng là F-E2A1-09 vẫn còn mở.

### 8. Chất lượng test

- `git diff 2f20e6c..HEAD -- tests/`: chỉ hai file bị chạm, **không hàm test nào bị xoá**
  (22 hàm trong `test_wp_a1_provenance.py` trước và sau đều là 22; danh sách tên trùng
  khớp hoàn toàn). Không có test nào bị làm yếu.
- Quét mẫu PASS giả trong hai file (`assert True/False`, `or True`, `except` nuốt lỗi,
  `pytest.skip`, `xfail`, assertion bọc trong `if`): **0 hit**. Hai `if` duy nhất nằm
  trong vòng lặp gom danh sách của `test_a1_08_lockfile_matches_installed_environment`,
  và sau đó là assertion cứng trên danh sách gom được — không nuốt lỗi.
- F-E2A1-05 được sửa ĐÚNG NGUYÊN NHÂN, không phải sửa hình thức: test nay neo vào
  `prep.official_eligible is False` + `official_reason.startswith("source_not_real:")`
  TRƯỚC khi chạy gate, rồi bắt buộc `payload["official_reason"] == prep.official_reason`.
  `limit=1` không còn là thứ duy nhất làm test xanh.
- F-E2A1-07 được sửa ĐÚNG NGUYÊN NHÂN: fixture kéo tới `2025-06-30` (sau
  `OOS_START = 2025-01-01`) và test thêm precondition `a["oos"]["ae"] == a["oos"]["ae"]`
  (bác NaN) cùng `a["oos"]["oos_months"] > 0`. Reviewer xác nhận bằng số của chính mình:
  `oos.ae = 79.5632…`, `oos_months = 6` — assertion `a["oos"] == b["oos"]` nay so số thật.

### 9. CHECK-A1-06 — phạm vi thực tế reviewer chạy được, nói thẳng

Reviewer chạy CLI thật: `ethdca --raw-dir <synth 2020-01-01..2025-06-30> --out-dir <…>
run all`, KHÔNG `--dev-limit`. Kết quả GATE1 (đường official đầy đủ):

    run_record : official=False | data_source='synthetic' | code_commit=a0c278a0 | lock=9ea0150f
    metrics    : official=False | official_reason="source_not_real:ETHUSDT_1d='synthetic'" | dev_limit=None

Nhánh Gate 2 (FULL 219) + Gate 3 (FULL 114) + controls 1000 sim của cùng lần gọi đó KHÔNG
chạy hết trong khung thời gian phiên rà soát (ước tính hàng giờ trên máy đang có regression
chạy song song), nên reviewer dừng nó và **không ghi PASS cho phần chưa chạy**. Phần đó
được phủ bằng ba bằng chứng khác, tất cả do reviewer tự thu:

- `run_gate2`/`run_gate3` đều tính `official = prep.official_eligible and limit is None`.
  Với dataset synthetic, `prep.official_eligible` đã là `False` nên biểu thức là `False`
  với MỌI `limit`, kể cả `None` — reviewer đọc trực tiếp `pipeline.py` dòng 225 và 273 và
  đo `prep.official_eligible = False`.
- `test_a1_06_synthetic_not_official_in_gate2_gate3` (chạy trong lần chạy suite của
  reviewer) neo vào đúng nguyên nhân đó, không còn dựa vào `limit=1`.
- Reviewer tự chạy `run_gate2`/`run_gate3` trên lineage ĐỦ TƯ CÁCH và xác nhận chiều ngược
  lại: khi eligibility True thì chính `limit` mới là thứ hạ `official` xuống False —
  tức hai điều kiện độc lập, không cái nào che cái nào.

### 10. Đối chiếu TRỰC TIẾP mã BEFORE / AFTER trên ba case chặn

Ngoài mutation, reviewer chạy CÙNG một script probe lên hai cây mã qua `git worktree`, trên
cùng dữ liệu. Đây là bằng chứng mạnh nhất vì nó không dựa vào đột biến nhân tạo mà chạy
đúng mã của hai commit thật:

    BEFORE — bd7c5ff (dataset.py không có REQUIRED_SERIES)
      series canonical RỖNG (row_count=0)          -> (True, 'verified')    FAIL-OPEN
      lineage phủ 1/3 series (hash nhất quán)      -> (True, 'verified')    FAIL-OPEN
      series THỪA trên đĩa (hash nhất quán)        -> (True, 'verified')    FAIL-OPEN

    AFTER — a0c278a
      series canonical RỖNG (row_count=0)          -> (False, 'empty_series:ETHUSDT_15m')
      lineage phủ 1/3 series (hash nhất quán)      -> (False, 'missing_required_series:BTCUSDT_1d')
      series THỪA trên đĩa (hash nhất quán)        -> (False, 'unexpected_series:DOGEUSDT_1d')

Cả ba lineage BEFORE đều được `build_lineage` dựng lại nên **tự nhất quán tuyệt đối về
hash** — tức phòng thủ checksum không hề bị vi phạm, nó chỉ đơn giản không nói gì về ba
trạng thái này. Đây đúng là luận điểm của F-E2A1-01 và F-E2A1-02, và nay cả ba đều
fail-closed với mã lý do riêng biệt.

## Trạng thái 9 finding của vòng hai

| Finding | Mức (vòng 2) | Trạng thái trên `a0c278a` | Bằng chứng của reviewer |
|---|---|---|---|
| F-E2A1-01 | CAO (chặn) | **ĐÓNG** | Stub fetch 5 kịch bản: "không cơ chế nào" → `unknown` + `empty_series`, không còn `binance_rest`. Chạy trực tiếp mã `bd7c5ff` (§10): series rỗng cho `(True,'verified')`; trên `a0c278a` cho `empty_series:ETHUSDT_15m`. MUTATION-2 chứng minh nhánh này chịu tải thật. |
| F-E2A1-02 | TRUNG BÌNH-CAO (chặn) | **ĐÓNG** | Coverage hai chiều: thiếu / thừa / trùng / lineage-only / loader-only đều fail-closed với mã lý do riêng. Chạy trực tiếp mã `bd7c5ff` (§10): 1/3 series và series thừa đều cho `(True,'verified')` với lineage TỰ NHẤT QUÁN về hash; trên `a0c278a` cho `missing_required_series` / `unexpected_series`. MUTATION-3 chứng minh 6 test sập khi gỡ bỏ. |
| F-E2A1-03 | TRUNG BÌNH | **CÒN MỞ — nâng mức lên CAO** | `reporting.py` không đổi một dòng. Reviewer cài project vào venv sạch: `_REPO_ROOT` → `…/e2r3_venv/lib/python3.11`, record ghi `dependency_lock_hash='no-lockfile'`, `code_commit='unknown'`, KHÔNG cảnh báo. Đây chính là môi trường mà CHECK-A1-09 yêu cầu. |
| F-E2A1-04 | TRUNG BÌNH | **CÒN MỞ** | `_get_code_commit` vẫn chỉ `git rev-parse HEAD`, không có cờ dirty. |
| F-E2A1-05 | TRUNG BÌNH | **ĐÓNG** | Test neo vào nguyên nhân (xem §8). Sửa thực chất, không phải hình thức. |
| F-E2A1-06 | THẤP | **CÒN MỞ** | `pyproject.lock` không ghim `tzdata` và header không ghi phiên bản tzdata hệ thống. |
| F-E2A1-07 | TRUNG BÌNH | **ĐÓNG** | Dataset có OOS số thật + precondition bác NaN (xem §8). Sửa thực chất. |
| F-E2A1-08 | THẤP | **CÒN MỞ — có bằng chứng mới** | Reviewer dựng stub fetch trong đó BTCUSDT chỉ có REST còn hai series kia có archive: `lineage['source'] = 'mixed'`, `official_eligibility = (True,'verified')`. Tức một run ĐỦ TƯ CÁCH OFFICIAL ghi `data_source='mixed'`, giá trị không có trong bảng taxonomy `docs/CONVENTIONS.md`. |
| F-E2A1-09 | THẤP | **CÒN MỞ — có bằng chứng mới** | Reviewer chạy `run_controls(..., n_sims=200)` (đúng giá trị `cli.py` dùng cho `--dev-limit`) trên lineage đủ tư cách: record `RANDOM_CONTROL` ghi `official=True` trong khi GATE1/2/3/BASELINE của cùng lần chạy đều `false`. |

Theo §15 decision pack, implementer không được tự bác finding E2; reviewer vòng này giữ
nguyên toàn bộ 9 finding và chỉ đóng những finding có bằng chứng đóng thật.

## Findings mới (vòng ba)

**F-E2A1R3-01 — Phòng thủ `empty_series` đặt trên một trường KHÔNG được checksum bảo vệ và
KHÔNG được đối chiếu với file (mức: TRUNG BÌNH).**
`_dataset_hash` chỉ phủ danh sách `file_hash`; `row_count` nằm ngoài mọi hash.
`official_eligibility` cũng không bao giờ đọc số dòng thật của parquet, dù nó đã mở chính
file đó để băm. Reviewer làm rỗng THẬT `ETHUSDT_15m.parquet`, dựng lineage trung thực
(`empty_series`), rồi sửa ĐÚNG MỘT SỐ NGUYÊN `row_count: 0 -> 140156`: mọi `file_hash` và
`dataset_hash` vẫn khớp, kết quả `(True, 'verified')` — dataset có một series thực thi
rỗng hoàn toàn trở thành đủ tư cách official. Cùng cơ chế: `row_count` kiểu chuỗi `"999"`
hoặc `True` cũng qua được. Điểm nghiêm trọng là ĐÂY LÀ LỚP PHÒNG THỦ ĐÃ ĐƯỢC DÙNG ĐỂ ĐÓNG
MỘT FINDING CHẶN (F-E2A1-01), và kịch bản "archive trả DataFrame rỗng" ở §1 cho thấy nó là
lớp DUY NHẤT chặn được trong trường hợp đó. Sửa: đối chiếu `row_count` với
`len(pd.read_parquet(p))` ngay trong `verify_lineage` (chi phí gần bằng 0 vì file đã được
đọc để băm), hoặc tối thiểu ép kiểu chặt (`isinstance(row_count, int) and not isinstance(row_count, bool)`).
Nếu chấp nhận không sửa thì PHẢI công bố trong `docs/CONVENTIONS.md` cạnh giới hạn về
`source` — hiện giới hạn `source` được công bố còn giới hạn `row_count` thì không, nên
người đọc tài liệu sẽ hiểu cơ chế mạnh hơn thực tế.

**F-E2A1R3-02 — `official_eligibility` không tổng (`TypeError` không bắt) khi `source` là
list/dict (mức: TRUNG BÌNH-THẤP).**
`src in REAL_SOURCES` với `REAL_SOURCES` là `frozenset` raise
`TypeError: unhashable type: 'list'` (và `'dict'`) thay vì trả mã lý do. Contract §10
case 14 quy định lineage dị dạng phải cho `(False, 'lineage_malformed')`; RULE-14 quy định
đây là enforcement point canonical DUY NHẤT. Một `lineage.json` hỏng/bị sửa sẽ làm sập
`Prepared.__init__` với traceback thay vì fail-closed có mã lý do. Mã đã bắt
`(TypeError, ValueError)` cho `row_count` nhưng không bắt cho `source`. Sửa: kiểm
`isinstance(src, str)` trước, hoặc bọc phép kiểm tra thành viên.

**F-E2A1R3-03 — Contract case 13 chưa thi hành đúng: `official_reason` của run dev là
`"verified"`, không phải `dev_limit_set` (mức: TRUNG BÌNH).**
Bảng contract §10 (FROZEN, "S008 thực thi đúng bảng này, không tự thêm/bớt case") quy định
case 13 → REASON CODE `dev_limit_set`, enforcement point `pipeline.run_gate1/2/3`.
Thực tế reviewer đo được:

    run_gate1(prep, out, dev_limit=5) -> official=False, official_reason='verified'
    run_gate2(prep, out, limit=3)     -> official=False, official_reason='verified'

File `*_metrics.json` do `save_run` ghi vì thế chứa cặp mâu thuẫn
`{"official": false, "official_reason": "verified"}`. Mã `dev_limit_set` không tồn tại ở
bất kỳ đâu trong `src/`. Đây vừa là sai lệch với contract đã đóng băng, vừa vi phạm yêu
cầu "reason code phải phân biệt được nguyên nhân": nguyên nhân dev bị che hoàn toàn.
Test `test_ec_13` chỉ khẳng định `payload["official"] is False` mà KHÔNG khẳng định mã lý
do, nên nó không thể phát hiện thiếu sót này — tức oracle của case 13 yếu hơn contract.

**F-E2A1R3-04 — `data_source` trong run record hoàn toàn không được kiểm (mức: TRUNG BÌNH-THẤP).**
`Prepared.data_source = lineage.get("source")` — trường ở MỨC DATASET này không đi qua
`VALID_SOURCES` khi đọc và không được `official_eligibility` xem xét. Reviewer đặt
`lineage["source"]` lần lượt thành `'synthetic'`, `'mixed'`, `'hoan-toan-bia'`, `None`,
`12345` trong khi ba entry per-file vẫn mang nhãn thật: cả năm lần đều
`official_eligible = True` và record ghi đúng giá trị bịa đó vào `data_source`. Nghĩa là
một record có thể mang `official: true` cạnh `data_source: "synthetic"`. Đây là trường mà
CHECK-A1-01 dựa vào để record "tự trả lời dữ liệu đến từ đâu". Finding này bao trùm và
làm nặng thêm F-E2A1-08.

**F-E2A1R3-05 — Fetch bị cắt cụt vẫn đủ tư cách official, và `missing_count` không phát
hiện được (mức: TRUNG BÌNH; giao thoa WP-A4).**
Reviewer stub kịch bản rất thật của T-06: archive chỉ có tới tháng 2020-01, REST không trả
dòng nào (bị chặn/rate-limit). Yêu cầu 2020-01-01…2021-01-01:

    ETHUSDT_1d   source=binance_bulk_archive  rows=28   missing_count=0  last=2020-01-28
    BTCUSDT_1d   source=binance_bulk_archive  rows=28   missing_count=0  last=2020-01-28
    ETHUSDT_15m  source=binance_bulk_archive  rows=34944                 last=2020-01-28
    official_eligibility -> (True, 'verified')

Dataset thiếu ~92% khoảng thời gian được yêu cầu nhưng `missing_count = 0`, vì `gap_report`
chỉ đo khoảng trống GIỮA first và last quan sát được, không đối chiếu với `start`/`end` đã
yêu cầu. `official_eligibility` không nhìn `first_timestamp`/`last_timestamp` ở bất kỳ đâu.
Contract 20 case đã FROZEN không có case này, nên nó KHÔNG làm FAIL check nào của WP-A1;
nhưng nó nằm đúng trên đường đi của official run và phải được đóng trước T-06. Nơi tự
nhiên là **WP-A4** (Xử lý đúng khi dữ liệu thiếu hoặc hỏng, hiện READY, lớp A). Nếu WP-A4
không phủ, phải mở thành finding riêng có chủ.

**F-E2A1R3-06 — Tài liệu đã lệch so với mã (mức: THẤP, nhưng chạm Exit Criteria).**
`docs/CONVENTIONS.md` — file mà Exit Criteria của WP-A1 yêu cầu — vẫn mô tả điều kiện đủ
tư cách theo phiên bản TRƯỚC S008: "mọi series phải mang nguồn thuộc `REAL_SOURCES`, **và**
lineage phải verify được checksum". Hai bất biến MỚI vừa đóng hai finding chặn — phủ đúng
`REQUIRED_SERIES` (thiếu/thừa/trùng) và `row_count > 0` — KHÔNG được ghi ở đâu trong tài
liệu. Kèm theo: `mixed` vẫn vắng trong bảng taxonomy (F-E2A1-08); Evidence CHECK-A1-06
trong task file còn trích mã lý do cũ `source_not_real:BTCUSDT_1d='synthetic'` (nay là
`ETHUSDT_1d`); docstring `official_eligibility` và `CONVENTIONS.md` nói lý do "được ghi vào
run record" trong khi `backtest_runs.jsonl` KHÔNG có trường `official_reason` (nó nằm ở
file `*_metrics.json` mà record trỏ tới).

**F-E2A1R3-07 — `REQUIRED_SERIES` chưa phải nguồn duy nhất như docstring tuyên bố
(mức: THẤP).**
Docstring khẳng định "Đây là NƠI DUY NHẤT khai tập này". Thực tế `synth.generate` vẫn viết
cứng ba tên file (`dataset.py` không tham gia), và `fetch.fetch_all` vẫn viết cứng ba bộ
`(symbol, interval, start)`. Nếu `REQUIRED_SERIES` đổi, hai nơi sản xuất dataset sẽ không
đi theo và `official_eligibility` sẽ từ chối MỌI dataset chúng tạo ra. Test
`test_required_series_is_the_single_canonical_definition` chỉ kiểm `load_dataset`, nên
không phát hiện được phân kỳ này. Ràng buộc §9 decision pack ("không được khai một tập thứ
hai song song") mới được thoả một nửa (loader ↔ eligibility), chưa thoả cho producer.

### Ghi nhận — KHÔNG phải finding mới

- **Dán nhãn sai bằng tay.** Sửa `lineage.json` từ `synthetic` sang `binance_rest` (giữ
  nguyên hash) vẫn cho `(True,'verified')`. Reviewer xác nhận có thật. Đây là giới hạn ĐÃ
  ĐƯỢC CÔNG BỐ trong Evidence của CHECK-A1-07, trong `docs/CONVENTIONS.md`, và có số hiệu
  F-PRE008-01, kèm biện pháp đối trọng (đối chiếu `ethdca freeze` hai máy theo DEC-003).
  Reviewer KHÔNG dùng nó để FAIL một gate đã tự công bố nó nằm ngoài phạm vi — nhưng ghi
  rõ ở đây để không ai đọc kết luận PASS thành "không thể giả mạo".
- **Nhánh `lineage_no_files` trong `verify_lineage`** nay không thể tới được từ
  `official_eligibility` (coverage đã chặn trước). Mã chết vô hại.
- **`_dataset_hash` nhạy với THỨ TỰ entry** trong `files`. Đảo thứ tự → `dataset_hash_mismatch`
  (fail-closed), nên không phải lỗ hổng, chỉ là điểm giòn.
- **`test_ec_17` hẹp hơn contract.** Bảng §10 ghi enforcement point của case 17 là "toàn
  `src/` (không đọc `environ`)", nhưng test chỉ quét `inspect.getsource(cli_mod)`. Reviewer
  đã tự grep TOÀN BỘ `src/` và xác nhận 0 hit cho `environ`/`getenv`/`os.env`, nên kết luận
  đứng vững; nhưng oracle sẽ không bắt được nếu về sau một module khác đọc biến môi trường.
  Nên mở rộng phạm vi quét của test.

### Điều gói này làm ĐÚNG (ghi để cân bằng, không để giảm nhẹ kết luận)

Hai finding CHẶN của vòng hai được đóng THẬT, không phải đóng bằng lời: reviewer tự dựng
lại cả hai đường tấn công và cả hai đều fail-closed; MUTATION-2/3 chứng minh ngược lại
rằng chúng từng mở. Suite contract mới khẳng định MÃ LÝ DO chứ không chỉ cờ boolean, nên
MUTATION-6 làm đỏ 24/27 test — oracle mạnh hơn mức tối thiểu §12 đòi hỏi. Positive control
chạy pipeline thật, không mock. Thứ tự kiểm được thiết kế tất định. Hai defect test
(F-E2A1-05, F-E2A1-07) được sửa đúng nguyên nhân chứ không sửa hình thức. Và CHECK-A1-09 —
vế treo suốt hai vòng — nay chạy được thật: venv sạch, 15/15 pin đúng, ba process độc lập,
metric trùng khớp tuyệt đối trên dataset có OOS số thật.

## Mismatches With Implementer Claims

- Commit `a0c278a` KHÔNG cập nhật `docs/`, và commit message tự ghi "không phải tuyên bố đã
  xác minh xong". Vì vậy không có tuyên bố PASS mới nào để đối chiếu. Completion Gate trong
  task file vẫn ghi trạng thái vòng hai (A1-05 FAIL, A1-07 FAIL, A1-09 NOT_TESTED,
  A1-11 FAIL) — nay đã LẠC HẬU so với mã, và phải được cập nhật bằng chính báo cáo này.
- Commit message tuyên bố "AFTER — 16/16 PASS". Reviewer không tái lập con số 16 (suite
  thực tế là 22 hàm / 27 test item), nhưng đã tự chạy toàn bộ 27 item: PASS. Tuyên bố về
  bản chất là đúng.
- Docstring `official_eligibility` và `docs/CONVENTIONS.md` tuyên bố mạnh hơn thực tế ở ba
  điểm: lý do "được ghi vào run record" (thực tế nằm ở metrics JSON), `REQUIRED_SERIES` là
  "NƠI DUY NHẤT khai tập này" (thực tế `synth`/`fetch` khai lại), và điều kiện đủ tư cách
  chưa được cập nhật theo S008. Xem F-E2A1R3-06, F-E2A1R3-07.

## Exit Criteria — trạng thái đo được

| Exit Criterion | Trạng thái |
|---|---|
| 100% REQUIRED checks PASS | **CHƯA** — A1-01…A1-10 đều PASS, nhưng A1-11 (E2) FAIL theo báo cáo này |
| Mức evidence được thoả (E1 toàn bộ; E2 cho A1-11) | E1 thoả; E2 đã thực hiện, kết quả FAIL |
| Không defect nghiêm trọng nào chưa xử lý | **CHƯA** — F-E2A1-03 (nay mức CAO), F-E2A1-04, F-E2A1R3-01, F-E2A1R3-03 còn mở |
| `docs/CONVENTIONS.md` ghi quy ước phân loại nguồn | **CHƯA ĐẦY ĐỦ** — thiếu coverage invariant, `empty_series`, `mixed` (F-E2A1R3-06) |
| `PROJECT/PROJECT_PROGRESS.md` cập nhật; RSK-006/RSK-008 cập nhật | **CHƯA** — dòng 78 vẫn ghi WP-A1 `READY`; RSK-006 và RSK-008 vẫn "S001 XÁC NHẬN (E1)" |
| Session handoff được viết | **CHƯA** — `docs/sessions/` mới nhất vẫn là `S006-wp-a2-pipeline-wiring.md` |
| Không hạ REQUIRED check nào để đạt DONE | THOẢ — không check nào bị hạ; A1-09 được NÂNG từ NOT_TESTED lên PASS bằng bằng chứng mới |

## Conclusion

**E2 FAIL**

Nói cho chính xác về bản chất của kết luận này, vì nó khác hai vòng trước: **phần kỹ thuật
lõi của WP-A1 đã đứng vững.** Reviewer đã thử phá và không phá được đường nào mà Completion
Gate đã đóng băng yêu cầu phải đóng. Cả 10 check CHECK-A1-01…A1-10 đều PASS với bằng chứng
E2 do reviewer tự thu, gồm cả CHECK-A1-09 vốn treo suốt hai vòng. Hai finding CHẶN của vòng
hai đã đóng thật, được chứng minh hai chiều: chạy trực tiếp mã `bd7c5ff` cho thấy cả ba
case chặn từng cho `(True,'verified')` với lineage tự nhất quán về hash, và mutation cho thấy
test mới sập đúng chỗ khi gỡ phòng thủ.

E2 vẫn FAIL vì ba lý do độc lập, không lý do nào là "trông chưa đủ":

1. **Một follow-up BẮT BUỘC của vòng hai bị bỏ qua hoàn toàn.** Vòng hai liệt kê năm mục
   "Bắt buộc trước khi WP-A1 có thể được xét DONE": F-E2A1-01 (ĐÓNG), F-E2A1-02 (ĐÓNG),
   **F-E2A1-03 (KHÔNG ĐỘNG TỚI)**, F-E2A1-05 + F-E2A1-07 (ĐÓNG), và ghi lại trạng thái
   CHECK-A1-09 trong task file (chưa làm, vì `a0c278a` không sửa `docs/`). PRE-S008 §15 giữ
   nguyên cả 9 finding là E2 CONFIRMED. `reporting.py` không đổi một dòng nào trong `a0c278a`.
   Reviewer còn nâng mức F-E2A1-03 lên CAO vì tự chứng minh được nó kích hoạt trong CHÍNH
   môi trường mà CHECK-A1-09 bắt buộc: cài project vào venv sạch dựng từ lockfile thì record
   ghi `code_commit='unknown'` và `dependency_lock_hash='no-lockfile'` mà không một cảnh báo
   nào. Máy chạy T-06 là máy chưa biết, và Master Index §6 CẤM chạy lại official run để sửa —
   nên đây là kịch bản mất provenance vĩnh viễn, đúng thứ WP-A1 sinh ra để chặn.

2. **Sai lệch với contract đã FROZEN.** §10 quy định case 13 phải cho mã lý do
   `dev_limit_set`; mã thực tế trả `'verified'` và ghi cặp `{"official": false,
   "official_reason": "verified"}` vào metrics JSON. Mã `dev_limit_set` không tồn tại trong
   `src/`, và `test_ec_13` không khẳng định mã lý do nên không phát hiện được. Decision pack
   ghi "S008 thực thi đúng bảng này, không tự thêm/bớt case" — điều kiện này chưa thoả.

3. **Exit Criteria còn hở bốn mục**, ba trong số đó y hệt vòng hai và chưa ai chạm tới:
   `PROJECT/PROJECT_PROGRESS.md` vẫn ghi WP-A1 `READY`, RSK-006/RSK-008 vẫn nguyên trạng
   thái S001, chưa có session handoff. Mục thứ tư là `docs/CONVENTIONS.md` — file mà Exit
   Criteria nêu đích danh — nay đã lệch so với mã ở đúng phần vừa được sửa.

Kèm theo, reviewer nêu bảy finding mới, trong đó F-E2A1R3-01 đáng chú ý nhất: lớp phòng thủ
`empty_series` vừa được dùng để đóng một finding CHẶN lại đặt trên `row_count` — một trường
không nằm dưới bất kỳ checksum nào và không bao giờ được đối chiếu với file thật, dù hàm đã
mở chính file đó để băm. Sửa đúng một số nguyên trong `lineage.json` là đủ để một series
thực thi RỖNG HOÀN TOÀN trở thành `(True, 'verified')`. Nó cùng lớp với giới hạn dán nhãn
sai đã được công bố, nên reviewer KHÔNG dùng nó để FAIL CHECK-A1-07; nhưng khác ở chỗ giới
hạn kia được công bố còn cái này thì không, và nó chống đỡ một finding chặn.

**WP-A1 CHƯA đủ điều kiện chuyển DONE.** Exit Criteria "100% REQUIRED checks PASS" và
"Không defect nghiêm trọng nào chưa xử lý" đều chưa thoả. **GATE-A không đóng được → T-06
chưa được mở.**

## Required Follow-up

Bắt buộc trước khi WP-A1 được xét DONE:

1. **F-E2A1-03 (mức CAO)** — `save_run` phải fail-loud (raise, hoặc từ chối ghi
   `official=True`) khi `code_commit == "unknown"` hoặc
   `dependency_lock_hash == "no-lockfile"`. Reviewer đã chứng minh trạng thái này xảy ra
   trong venv sạch dựng từ lockfile, tức đúng quy trình mà CHECK-A1-09 khuyến nghị.

2. **F-E2A1R3-03** — Thi hành đúng contract case 13: `official_reason = "dev_limit_set"`
   khi run bị hạ vì `dev_limit`, và **bổ sung assertion mã lý do vào `test_ec_13`**.

3. **F-E2A1R3-01** — Hoặc đối chiếu `row_count` với số dòng thật của parquet trong
   `verify_lineage` (chi phí gần bằng 0), hoặc — nếu chủ dự án chấp nhận rủi ro — công bố
   giới hạn này trong `docs/CONVENTIONS.md` cạnh giới hạn về `source`. Không được để nó ở
   trạng thái "không sửa và không công bố".

4. **F-E2A1R3-06** — Cập nhật `docs/CONVENTIONS.md` cho khớp mã: coverage invariant hai
   chiều, `empty_series`, `mixed` trong taxonomy (đóng luôn F-E2A1-08), và nói đúng nơi
   `official_reason` được lưu. Cập nhật Evidence CHECK-A1-06 trong task file (mã lý do nay
   là `ETHUSDT_1d`).

5. **Exit Criteria còn hở** — cập nhật `PROJECT/PROJECT_PROGRESS.md` (trạng thái WP-A1,
   RSK-006, RSK-008), viết session handoff, và cập nhật Completion Gate trong task file
   theo kết quả E2 vòng ba (A1-05 và A1-07 chuyển FAIL → PASS; A1-09 chuyển NOT_TESTED →
   PASS, có xác nhận của reviewer E2 theo yêu cầu §15 decision pack).

Nên làm (không chặn DONE nhưng nên xử lý trong cùng gói):

6. **F-E2A1-04** — Ghi cờ dirty worktree vào `code_commit`.
7. **F-E2A1-06** — Ghi phiên bản tzdata hệ thống vào header lockfile hoặc ghim gói `tzdata`.
8. **F-E2A1-09** — Thống nhất cách `run_controls` ghi `official` với ba gate còn lại.
9. **F-E2A1R3-02** — `official_eligibility` phải trả `lineage_malformed` thay vì raise
   `TypeError` khi `source` là list/dict.
10. **F-E2A1R3-04** — Kiểm `lineage["source"]` theo taxonomy khi đọc, hoặc dẫn xuất
    `data_source` từ các nhãn per-file đã được kiểm thay vì tin trường roll-up.
11. **F-E2A1R3-05** — Định tuyến sang **WP-A4** (dữ liệu thiếu/cắt cụt vẫn official;
    `missing_count` không phát hiện truncation). Nếu WP-A4 không phủ, mở finding riêng —
    phải đóng trước T-06.
12. **F-E2A1R3-07** — Cho `synth.generate` và `fetch.fetch_all` dẫn xuất từ
    `REQUIRED_SERIES` thay vì khai lại, hoặc hạ tuyên bố "NƠI DUY NHẤT" trong docstring cho
    đúng sự thật.

Ghi chú về Scope Lock: reviewer đối chiếu "Expected Touch Area" của WP-A1 — mọi follow-up
BẮT BUỘC ở trên đều rơi vào vùng ĐƯỢC PHÉP (`src/eth_dca_os/reporting.py`, `pipeline.py`,
`data/`, `tests/`, `docs/CONVENTIONS.md`). **Không mục nào cần Scope Expansion.** Riêng
F-E2A1R3-05 nếu xử lý trong WP-A1 sẽ chạm ngữ nghĩa dữ liệu xấu — nên định tuyến sang
WP-A4 thay vì mở rộng phạm vi WP-A1.

Sau khi xử lý xong, gói cần một phiên E2 mới cho những phần bị sửa. Báo cáo này KHÔNG được
dùng lại làm bằng chứng cho phiên bản đã sửa.

## Escalation

Áp `governance/core/ESCALATION_PROTOCOL.md`. Đây là lần thứ BA gói đi qua E2, nên điều
khoản "không vá đi vá lại một implementation đang hỏng" vẫn áp dụng và vòng sửa tiếp theo
cần chủ dự án phê duyệt tường minh.

Nhận định của reviewer để chủ dự án cân nhắc: bản chất của vòng này KHÁC hai vòng trước.
Vòng một thiếu hẳn cơ chế dẫn xuất; vòng hai cơ chế có nhưng hở hai mặc định fail-open.
Vòng ba, hai lỗ hổng đó đã bị bịt và reviewer không phá được đường nào nằm trong phạm vi
Completion Gate đã đóng băng. Những gì còn lại là (a) ba follow-up đã được nêu từ vòng hai
mà lượt remediation này KHÔNG đụng tới, (b) một sai lệch mã lý do so với contract, và
(c) các mục Exit Criteria hành chính. Không mục nào cho thấy bế tắc về cách tiếp cận.

Vì vậy reviewer KHÔNG khuyến nghị `CAPABILITY_CEILING` (nâng Tier lên D). Trigger phù hợp
là **`VERIFICATION_DEPTH`** — giữ Tier C, Effort đã ở `xhigh`, nâng lên `max` cho lượt
đóng nốt — với ghi chú rằng khối lượng còn lại phần lớn là công việc đã được liệt kê sẵn,
không phải công việc phải khám phá lại. Quyết định thuộc về chủ dự án; reviewer không tự
chọn thay.
