# E2 INDEPENDENT REVIEW

Review ID:
E2-WP-A1-001

Task / Release:
WP-A1 — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức (`docs/tasks/WP-A1-provenance-va-tai-lap.md`), thoả CHECK-A1-11

Reviewer Session:
S008 — phiên rà soát độc lập (reviewer KHÔNG phải người cài đặt)

Executed By:
S008 independent reviewer (Opus / xhigh)

Timestamp:
2026-08-24

Commit được rà soát:
`2f20e6ce6007f0feac6bf152b9dd2eeac7250abb` (nhánh `claude/wp-a1-provenance-v67k9h`)

LƯU Ý VỀ TÍNH ỔN ĐỊNH CỦA ĐỐI TƯỢNG RÀ SOÁT: khi phiên này bắt đầu, HEAD là `792cafd`.
Trong lúc lần chạy test đầu tiên đang diễn ra, HEAD chuyển sang `2f20e6c` (phiên cài đặt
commit thêm bằng chứng CHECK-A1-10). Điều này làm
`test_a1_03_simulation_seed_and_code_commit` FAIL một lần vì `code_commit` ghi lúc `save_run`
(`2f20e6c`) khác HEAD chụp lúc bắt đầu run (`792cafd`). Đây là hệ quả của việc repo bị thay
đổi giữa phiên rà soát, KHÔNG phải defect của mã. Toàn bộ kết quả dưới đây đã được chạy lại
trên `2f20e6c` với working tree sạch (`git status --porcelain` rỗng). `2f20e6c` chỉ sửa
`docs/tasks/`, không đổi một dòng mã nào so với `792cafd`.

## Scope

Rà soát độc lập gói remediation WP-A1 (`f49776e`, `beae874`, `792cafd`, `2f20e6c`) chồng lên
lần cài đặt đầu `d72fbc4` đã bị E2 bác bỏ. Phạm vi:

- Chạy lại độc lập CHECK-A1-06, CHECK-A1-07, CHECK-A1-09 theo yêu cầu của CHECK-A1-11.
- Đối chiếu từng CHECK-A1-01 … CHECK-A1-10 với Completion Gate đã FROZEN (2026-08-23).
- Chủ động TÌM ĐƯỜNG PHÁ cờ `official`, không chỉ xác nhận đường hạnh phúc.
- Kiểm chất lượng test: assertion vô hiệu, test PASS giả, test bị làm yếu so với `d72fbc4`.
- Kiểm lockfile có mô tả đúng môi trường thật không.

Ngoài phạm vi: chạy `ethdca fetch` (BLK-001 chặn mạng Binance), dựng venv sạch từ lockfile
(proxy chặn cài gói), sửa mã (reviewer chỉ đọc / chạy / ghi nhận — không commit, không sửa
`src/`, không sửa `tests/`).

## Inputs Read

- Trạng thái repo tại `2f20e6c` (KHÔNG bắt đầu từ tuyên bố của người cài đặt).
- Completion Gate đã FROZEN trong `docs/tasks/WP-A1-provenance-va-tai-lap.md`.
- Diff thật `git diff d72fbc4..HEAD` — `src/eth_dca_os/{cli,config,pipeline,reporting}.py`,
  `src/eth_dca_os/data/{dataset,fetch,synth}.py`, `pyproject.lock`,
  `tests/test_wp_a1_provenance.py`, `docs/CONVENTIONS.md`.
- Cây mã `d72fbc4` qua `git worktree` tại `/tmp/wp-a1-before` để đối chiếu trước–sau.
- `governance/core/EVIDENCE_STANDARD.md`, `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.
- `PROJECT/PROJECT_PROGRESS.md`, `docs/sessions/`.

Bằng chứng do reviewer tự thu nằm ở phần "Bằng chứng độc lập" của từng check bên dưới.

## Independent Verification

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-A1-01 | PASS | E2 | Record thật từ `ethdca run` (CLI thật) đủ 9 khoá provenance, không khoá nào rỗng, không giá trị suy biến | S008 | 2026-08-24 |
| CHECK-A1-02 | PASS | E2 | Chạy manifest ĐẦY ĐỦ (219 + 114): hash trong record GATE2/GATE3 khớp CHÍNH XÁC hash do `ethdca freeze` sinh ra | S008 | 2026-08-24 |
| CHECK-A1-03 | PASS | E2 | `code_commit` == `git rev-parse HEAD`; `simulation_seed` deterministic qua HAI tiến trình, khác `master_seed` | S008 | 2026-08-24 |
| CHECK-A1-04 | PASS | E2 | Chạy CÙNG script trên `d72fbc4` và HEAD: toàn bộ hash config / manifest / `key()` / `_cfg_row` GIỐNG HỆT | S008 | 2026-08-24 |
| CHECK-A1-05 | **FAIL** | E2 | Đường `synth` đúng; đường `fetch` gán nhãn `binance_rest` cho series KHÔNG có cơ chế nào đóng góp (fail-OPEN) | S008 | 2026-08-24 |
| CHECK-A1-06 | PASS | E2 | `ethdca synth` + `ethdca run` KHÔNG `--dev-limit` → `official: false` ở CẢ payload lẫn run record | S008 | 2026-08-24 |
| CHECK-A1-07 | **FAIL** | E2 | Bề mặt CLI/env sạch và 20+ đầu vào dị dạng fail-closed, NHƯNG tìm được HAI đường biến dữ liệu không đủ tư cách thành `official` | S008 | 2026-08-24 |
| CHECK-A1-08 | PASS | E2 | 15/15 dòng lockfile dùng `==` và khớp `importlib.metadata`; sha256 khớp `dependency_lock_hash` trong record | S008 | 2026-08-24 |
| CHECK-A1-09 | NOT_TESTED (nửa "môi trường sạch" chưa chạy được) | E2 cho nửa đã chạy | Tái lập trong-môi-trường: HAI tiến trình riêng, `PYTHONHASHSEED` khác nhau → metric trùng tuyệt đối, gồm OOS số thật và toàn khối bootstrap. Nửa "dựng venv sạch từ lockfile": KHÔNG chạy được (proxy chặn cài gói) | S008 | 2026-08-24 |
| CHECK-A1-10 | PASS | E2 | `pytest tests/` 130/130 PASS exit 0; và snapshot mô phỏng `d72fbc4` == HEAD trên cùng dataset/seed, không dung sai | S008 | 2026-08-24 |

Tổng: **7 PASS · 2 FAIL · 1 NOT_TESTED**.

---

### CHECK-A1-01 — PASS

Bằng chứng độc lập — record sinh bởi CLI thật (`ethdca --raw-dir … --out-dir … synth`, rồi
`ethdca … run all`, KHÔNG `--dev-limit`), đọc nguyên văn từ `backtest_runs.jsonl`:

    "strategy_config_hash":      "f782f99077fe57693c1a7de0583f087464174a12f00c1a56479823af17501b7b"
    "execution_config_hash":     "5888866fa8ce62bebd485df17247d654804d9462121ce935243636f4c55c6ec9"
    "sensitivity_manifest_hash": "83aecd235e2143ced8c59c10411d29be200fd3ac9682d37651b9a0fc6addb6e6"
    "dataset_hash":              "139c600227bfca0ecf58cdf12bf25db7930e3cdd5688c11831446af90d5629b4"
    "master_seed":               42
    "simulation_seed":           8218346625117296390
    "python_version":            "3.11.15"
    "code_commit":               "2f20e6ce6007f0feac6bf152b9dd2eeac7250abb"
    "dependency_lock_hash":      "9ea0150fcf27c12d39335db95a01151a79e2f94aa64b0eda722fd939f76c4d9a"
    "data_source":               "synthetic"
    "official":                  false

Đủ 9 khoá, không khoá nào rỗng, không giá trị suy biến (`code_commit` != `"unknown"`,
`dependency_lock_hash` != `"no-lockfile"`). Đạt yêu cầu FROZEN.

Kèm theo finding **F-E2A1-03** (bên dưới): trong môi trường KHÔNG phải editable install,
hai trường này im lặng suy biến mà không có cảnh báo runtime nào.

### CHECK-A1-02 — PASS

Yêu cầu FROZEN đòi hash trong record phải "trùng với hash của manifest thực sự được dùng".
Tôi không dừng ở việc so record với chính công thức của nó (self-referential), mà chạy hai
đường ĐỘC LẬP rồi đối chiếu:

- đường A: `ethdca --out-dir m2out freeze` — sinh manifest đóng băng ra JSON/CSV;
- đường B: `run_gate2(prep, out, limit=None)` và `run_gate3(prep, out, limit=None)` —
  chạy manifest ĐẦY ĐỦ, đúng 219 và 114 config (đã xác nhận `len(per_config)`), rồi đọc
  `sensitivity_manifest_hash` từ `backtest_runs.jsonl`.

Kết quả:

    GATE2 record   e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e
    ethdca freeze  e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e   KHỚP

    GATE3 record   ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f
    ethdca freeze  ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f   KHỚP

    denominator = 219 · size = 114 (khớp `expected_denominator` / `expected_manifest_size`)

Cả hai record khác rỗng và khớp manifest đóng băng. **F-009 đóng.** Đọc mã cũng xác nhận
`run_gate2` dựng `configs = [baseline] + ofat + interaction` theo ĐÚNG thứ tự
`freeze_manifests` dùng, nên tính khớp này là cấu trúc chứ không phải ngẫu nhiên.

Ở `d72fbc4`, hai record này ghi `sensitivity_manifest_hash = null`; tôi xác nhận lời mô tả
BEFORE của người cài đặt là đúng.

### CHECK-A1-03 — PASS

`code_commit` trong mọi record tôi tự sinh = `2f20e6ce6007f0feac6bf152b9dd2eeac7250abb` =
`git rev-parse HEAD` (working tree sạch). `simulation_seed = 8218346625117296390`, giống
hệt qua HAI tiến trình interpreter riêng biệt với `PYTHONHASHSEED` khác nhau (1 / 99999 và
3 / 555), và khác `master_seed = 42`.

Defect mà người cài đặt tuyên bố đã sửa (hard-code `/home/user/coin`) được xác nhận đã sửa
thật: import module từ thư mục `/` vẫn cho `_REPO_ROOT = /home/user/coin` và
`code_commit = 2f20e6ce…`. Không còn phụ thuộc cwd.

Kèm finding **F-E2A1-04**: record không mang cờ "worktree bẩn".

### CHECK-A1-04 — PASS (đối chiếu độc lập với `d72fbc4`)

Tôi KHÔNG tin hai hằng số hash ghim trong test. Tôi chạy CÙNG một script trên hai cây mã
(`/tmp/wp-a1-before/src` = `d72fbc4`, và `/home/user/coin/src` = HEAD), cùng interpreter,
rồi `diff` toàn bộ output. Kết quả: hai file output khác nhau ĐÚNG hai dòng —
`has_created_at_strategy` và `has_created_at_exec` chuyển `false` → `true`. Mọi giá trị còn
lại giống hệt:

    strategy_hash    f782f99077fe57693c1a7de0583f087464174a12f00c1a56479823af17501b7b  (BEFORE == AFTER)
    exec1_hash       5888866fa8ce62bebd485df17247d654804d9462121ce935243636f4c55c6ec9  (BEFORE == AFTER)
    exec3_hash       789bd885640f8c9793e6d77f21cba77ee15c782de98312dd366acf4d043ab5f4  (BEFORE == AFTER)
    g2_manifest_hash e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e  (BEFORE == AFTER)
    g3_manifest_hash ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f  (BEFORE == AFTER)
    g2_denominator   219        g3_size 114                                            (BEFORE == AFTER)
    StrategyConfig().key() / ExecutionConfig().key() — repr giống hệt từng ký tự
    sorted(_cfg_row(BASELINE_STRATEGY).keys()) — 23 khoá, danh sách giống hệt, KHÔNG có 'created_at'

Cơ chế đã kiểm: `_stamp_created_at` dùng `object.__setattr__`, `created_at` KHÔNG phải
dataclass field, nên `asdict()` — nguồn của `hash`, `key()` và `_cfg_row` — không thấy nó.
Đúng như tuyên bố, và tôi đã tự dựng lại kết luận đó chứ không đọc lại của người cài đặt.

### CHECK-A1-05 — FAIL

**Phần ĐẠT.** Đường `synth`: `lineage.json` ghi `source = 'synthetic'` ở cả mức dataset lẫn
từng series (`BTCUSDT_1d`, `ETHUSDT_1d`, `ETHUSDT_15m`). `build_lineage` bắt buộc tham số
`source` và raise `ValueError` với mọi giá trị ngoài taxonomy — tôi thử `'binance-archive+api'`,
`'see fetch/synth'`, `''`, `'BINANCE_REST'`, `'real'`: tất cả đều bị từ chối. Mapping thiếu
key → `KeyError`. Chuỗi cố định `'see fetch/synth'` không còn ở đâu trong `src/`.

**Phần KHÔNG ĐẠT — defect mới.** Yêu cầu FROZEN là `source` nhận ĐÚNG một trong ba giá trị
cho TỪNG series, phản ánh nguồn thật. Đường `fetch` không thoả. Trong
`src/eth_dca_os/data/fetch.py`:

    sources[key] = used[0] if used else SOURCE_REST

`used` là danh sách cơ chế THỰC SỰ đã đóng góp. Khi `used` rỗng — không tháng nào có trong
bulk archive VÀ REST trả về rỗng — series đó không có nguồn nào cả, nhưng vẫn được dán nhãn
`binance_rest`, tức một nguồn THẬT và ĐỦ TƯ CÁCH official.

Tôi kiểm chứng bằng cách thay hai hàm I/O (`fetch_month_archive`, `fetch_klines`) bằng stub
ở namespace module — KHÔNG sửa một dòng nào trong `src/`, và không cần mạng, nên BLK-001
không chặn được phép kiểm này:

    kịch bản                          nhãn ghi vào lineage        row_count   official_eligibility
    archive có, REST rỗng             ETHUSDT_15m: binance_rest   0           True  'verified'
    archive rỗng, REST có             ETHUSDT_15m: binance_rest   0           True  'verified'
    archive + REST                    ETHUSDT_15m: binance_rest   0           True  'verified'
    KHÔNG lấy được gì (cả 3 series)   tất cả:      binance_rest   0           True  'verified'

Dòng cuối là kết luận: **một lần `fetch` không lấy được một dòng dữ liệu nào vẫn sinh ra
dataset ĐỦ TƯ CÁCH official.** Điều này mâu thuẫn trực tiếp với câu chính `docs/CONVENTIONS.md`
tự viết: "`unknown` … là trạng thái 'chưa chứng minh được' … Nó cố ý KHÔNG đủ tư cách
official: thiếu thông tin phải dẫn tới từ chối, không phải mặc định chấp nhận." Giá trị mặc
định đúng ở đây phải là `SOURCE_UNKNOWN`, không phải `SOURCE_REST`.

Đây cũng là một MISMATCH với tuyên bố của người cài đặt trong CHECK-A1-05: "`fetch.fetch_all`
phân loại theo từng series từ các cơ chế `fetch_series` thực sự đã dùng". Tuyên bố đó sai
đúng ở trường hợp không có cơ chế nào được dùng — tức trường hợp duy nhất mà việc phân loại
thật sự quan trọng.

Điểm phụ (mức thấp, ghi để đủ): `build_lineage` sinh `lineage['source'] = 'mixed'` khi các
series khác nguồn nhau. Giá trị `mixed` đi thẳng vào `run_record['data_source']` nhưng KHÔNG
có trong bảng taxonomy của `docs/CONVENTIONS.md`. Official run thật (archive cho tháng đủ +
REST cho phần đuôi) gần như chắc chắn sẽ sinh `data_source: "mixed"` — tức đúng lần chạy
quan trọng nhất sẽ ghi một giá trị không được tài liệu hoá.

### CHECK-A1-06 — PASS

Chạy đúng kịch bản F-005 bằng CLI thật, không dùng API Python:

    ethdca --raw-dir e2raw --out-dir e2out synth --start 2019-01-01 --end 2024-12-31
    ethdca --raw-dir e2raw --out-dir e2out run all          # KHÔNG có --dev-limit

Kết quả:

    lineage.json  source = 'synthetic'
                  per-file = {BTCUSDT_1d: synthetic, ETHUSDT_15m: synthetic, ETHUSDT_1d: synthetic}
    payload       official = False, official_reason = "source_not_real:BTCUSDT_1d='synthetic'"
    run record    "official": false, "data_source": "synthetic"

Tôi cũng chạy lại `run_gate1` qua API ở hai tiến trình riêng trên hai dataset khác nhau; cả
bốn lần đều `official=False`, `dev_limit=None`, record `official=false`. Kịch bản mà `d72fbc4`
cho `official: true` nay cho `false`, ở CẢ payload lẫn record — đạt yêu cầu FROZEN.

Nửa Gate 2 / Gate 3 tôi kiểm bằng đường mà test của người cài đặt KHÔNG kiểm — `limit=None`,
manifest đầy đủ, dữ liệu synthetic:

    run_gate2(prep, out, limit=None)  ->  official = False, per_config = 219
    run_gate3(prep, out, limit=None)  ->  official = False, per_config = 114
    record GATE2 / GATE3              ->  "official": false, "data_source": "synthetic"

Đây mới là phép kiểm có khả năng phân biệt: vì `limit is None` đúng, giá trị `False` chỉ có
thể đến từ `prep.official_eligible`, tức từ nhãn nguồn. Bất biến đứng vững ở cả ba gate.

CẢNH BÁO VỀ CHẤT LƯỢNG BẰNG CHỨNG (finding F-E2A1-05): test mà người cài đặt viện dẫn cho
nửa Gate 2/Gate 3 của check này —

    def test_a1_06_synthetic_not_official_in_gate2_gate3(synth_raw, tmp_path):
        prep = Prepared(synth_raw)
        assert run_gate2(prep, tmp_path, limit=1)["official"] is False
        assert run_gate3(prep, tmp_path, limit=1)["official"] is False

— KHÔNG THỂ FAIL vì lý do nó tuyên bố kiểm. Cờ là `prep.official_eligible and limit is None`;
với `limit=1` thì `limit is None` đã False, nên assertion vẫn PASS ngay cả khi toàn bộ cơ
chế chặn nguồn synthetic bị gỡ bỏ. Docstring nói "không gate nào có đường dẫn xuất riêng"
nhưng test không chứng minh điều đó. Đây đúng lớp defect đã khiến E2 lần trước bác bỏ gói
(assertion PASS vì lý do sai), chỉ khác hình thức: lần trước là `if` bọc ngoài, lần này là
điều kiện thứ hai của `and` đã đủ để quyết định kết quả.

Tôi vẫn ghi PASS cho CHECK-A1-06 vì tôi đã tự kiểm chứng HÀNH VI bằng CLI thật; nhưng bằng
chứng E1 cho nửa Gate 2/Gate 3 phải được thay bằng một test có khả năng phân biệt.

### CHECK-A1-07 — FAIL

**Phần ĐẠT — đã thử phá và không phá được.**

Bề mặt CLI/env (tự rà, không đọc lại của người cài đặt): `cli.py` chỉ có `--raw-dir`,
`--out-dir`, `--start`, `--end`, `--dev-limit`, `--history-days`, `--parity-days`. Không có
`--official` / `--force-official` / `--source` / `--real-data`. `grep -rn "os.environ|os.getenv|environ"`
trên TOÀN BỘ `src/` (không chỉ `cli.py` như test đang làm): 0 kết quả. `official_eligibility`
nhận đúng `(raw_dir, lineage)`. `reporting` không import phép dẫn xuất. `Prepared` tính một
lần; `run_gate1/2/3` và `run_verdict` dùng chung, không gate nào tính lại.

Probe đối kháng — kết quả thực tế tôi tự chạy (positive control ở P1 chứng minh cổng KHÔNG
phải "luôn trả False"):

    P1  nhãn real + checksum khớp            -> True  'verified'                (positive control)
    P0  synthetic nguyên bản                 -> False "source_not_real:BTCUSDT_1d='synthetic'"
    P2  lineage = None / 0 / True / '' / []  -> False 'lineage_missing'
    P2  lineage = {} / {'files': []} / None  -> False 'lineage_no_files'
    P2  thiếu khoá 'files' (có 'file')       -> False 'lineage_no_files'
    P3  'BINANCE_REST' / 'Binance_Rest'      -> False 'source_not_real:…'
    P3  ' binance_rest ' / 'binance_rest\n'  -> False 'source_not_real:…'
    P3  source = None / thiếu hẳn / True     -> False 'source_not_real:…'
    P3  source = list / dict                 -> TypeError (crash, không phải True)
    P6  files = [{}]                         -> False 'source_not_real:None_None=None'
    P7  sửa parquet sau khi build lineage    -> False 'file_hash_mismatch:ETHUSDT_1d.parquet'
    P7  dataset_hash bị sửa                  -> False 'dataset_hash_mismatch'
    P7  xoá 1 file parquet                   -> False 'missing_file:…'
    P8  xoá lineage.json rồi chạy            -> False "source_not_real:…='unknown'"
    P9  đặt sẵn ETHDCA_OFFICIAL / OFFICIAL / ETHDCA_FORCE_OFFICIAL / ETHDCA_SOURCE
                                             -> False (không đổi gì)
    P10 raw_dir trỏ thư mục trống            -> False 'missing_file:…'

Không đường CLI, env, hay tham số nào ép được `official`. Phần này thật sự vững.

**Phần KHÔNG ĐẠT — hai đường biến dữ liệu không đủ tư cách thành `official`.**

**(1) Mặc định fail-OPEN trên đường `fetch`** — xem CHECK-A1-05. Đây là đường của official
run thật (T-06). Một dataset không có dòng nào, không cơ chế nào tạo ra, được dán nhãn
`binance_rest` và cho `official_eligibility -> (True, 'verified')`. Đây chính xác là "dữ
liệu unknown thành official", nghĩa là hỏng đúng bất biến trung tâm mà gói này tồn tại để
bảo vệ, và nó nằm trên đường đi thật chứ không phải một góc lý thuyết.

**(2) Lineage không phủ hết các series thực sự được dùng — chưa được tài liệu hoá.**

    P5  lineage chỉ khai 1/3 series (BTCUSDT_1d, nhãn real, hash đúng);
        ETHUSDT_1d và ETHUSDT_15m vẫn là synthetic và KHÔNG có trong lineage
        -> official_eligibility = (True, 'verified')

`official_eligibility` chỉ duyệt các entry CÓ trong lineage. Nó không hề kiểm rằng lineage
phủ đủ ba series mà `load_dataset` thực sự nạp (`ETHUSDT_1d`, `BTCUSDT_1d`, `ETHUSDT_15m`).
Bỏ bớt entry là đủ để hai phần ba dataset thoát khỏi mọi kiểm tra nguồn gốc, mà lineage còn
lại vẫn hoàn toàn "thành thật" về những gì nó khai. Khác với việc dán nhãn sai (đã được ghi
nhận là giới hạn), đường này CHƯA được tài liệu hoá ở đâu, và nó âm thầm hơn: người đọc
`lineage.json` về sau thấy mọi entry đều `binance_*` và checksum khớp.

**Đường đã được công bố (ghi nhận, không tính là defect mới).**

    P4  sửa tay lineage.json: 'synthetic' -> 'binance_bulk_archive' (giữ nguyên file_hash)
        -> official_eligibility = (True, 'verified')

`dataset_hash` tính từ danh sách `file_hash` nên đổi nhãn không làm lệch checksum.
`docs/CONVENTIONS.md` và phần Evidence của CHECK-A1-07 đã công bố đúng giới hạn này (không
chống được người vận hành cố ý dán nhãn sai; cần đối chiếu `ethdca freeze` hai máy theo
DEC-003). Tôi xác nhận nó có thật, và xác nhận nó ĐÃ được công bố.

### CHECK-A1-08 — PASS

Tự kiểm, không đọc lại kết quả người cài đặt:

    sha256(pyproject.lock) = 9ea0150fcf27c12d39335db95a01151a79e2f94aa64b0eda722fd939f76c4d9a
    == dependency_lock_hash trong run record                                      OK
    15/15 dòng ghim dùng '==' (không dòng nào đặt sàn '>=')                       OK
    15/15 dòng khớp importlib.metadata trên interpreter đang chạy — 0 dòng lệch   OK

Defect nghiêm trọng của `d72fbc4` (lockfile viết tay, 9/15 dòng sai, 2 gói ghim mà chưa hề
được cài) đã thật sự được sửa: `pytz` và `tzdata` — hai gói KHÔNG được cài — đã bị gỡ khỏi
lockfile, và mọi phiên bản còn lại nay khớp môi trường thật.

Ghi kèm finding **F-E2A1-06** (mức thấp): lockfile ghim gói Python, KHÔNG ghim cơ sở dữ liệu
múi giờ của hệ điều hành. `zoneinfo.TZPATH` cho thấy `Asia/Ho_Chi_Minh` đang được đọc từ
`/usr/share/zoneinfo` (gói pip `tzdata` không được cài). `StrategyConfig.accounting_timezone
= 'Asia/Ho_Chi_Minh'` quyết định biên ngày kế toán, nên dựng lại từ lockfile trên máy có bản
tzdata khác vẫn có thể lệch. (Rủi ro thực tế thấp — múi giờ này không đổi offset từ 1975 —
nhưng RSK-006 nói về "tái lập theo thời gian", nên nên ghi rõ trong lockfile.)

### CHECK-A1-09 — NOT_TESTED (nửa yêu cầu không chạy được)

Yêu cầu FROZEN có hai vế: **(a)** cài môi trường SẠCH từ lockfile; **(b)** chạy lại cùng
dataset/config/manifest/seed và đối chiếu metric.

**Vế (b) — ĐÃ CHẠY, và tôi chạy MẠNH HƠN test của người cài đặt.** Test của họ gọi
`run_gate1` hai lần trong CÙNG một tiến trình. Tôi chạy trong HAI TIẾN TRÌNH INTERPRETER
RIÊNG với `PYTHONHASHSEED` khác nhau, nên nếu có chỗ nào phụ thuộc `hash()` của Python hay
trạng thái RNG toàn cục còn sót giữa hai lần gọi thì nó sẽ lộ ra. Hai bộ, hai dataset:

    dataset 2019-01-01..2024-12-31,  PYTHONHASHSEED = 1 vs 99999
    dataset 2019-01-01..2026-06-30,  PYTHONHASHSEED = 3 vs 555

Snapshot so sánh gồm `ae_by_window` (9 window), `primary_median`,
`pooled_median_descriptive`, `oos`, TOÀN BỘ khối `bootstrap_descriptive` (block 30/60/90),
`gate1`, `concentration`, `cash_ratio`, `counters_w5`, `benchmarks`, `diagnostics`, và mọi
trường provenance. Kết quả cả hai bộ: khác nhau ĐÚNG ba trường `run_id`, `metrics_path`,
`created_at` — tức uuid và dấu thời gian của chính record. Mọi số liệu còn lại trùng tuyệt
đối (so bằng `==`, không dung sai).

Bộ thứ hai quan trọng vì nó có OOS SỐ THẬT:

    oos = {"ae": 99.05769511161444, "oos_months": 18, "short_oos": true}
    a['oos']['ae'] == b['oos']['ae']  ->  True     (so số thật, không phải NaN)
    primary_median = 97.51432329190644  (trùng)
    bootstrap 90 = {p5: 86.4044208646096, p50: 97.05873070945637, p95: 115.40181947389675}

Điều này bịt một lỗ hổng trong bằng chứng E1 của người cài đặt (finding **F-E2A1-07**):
dataset mà test của họ dùng (2020-01-01..2023-12-31) cho `oos.ae = NaN`, và assertion
`assert a["oos"] == b["oos"]` PASS chỉ vì `np.nan` là một object singleton nên `dict.__eq__`
đi qua lối tắt identity. Tôi kiểm chứng riêng:

    {'ae': np.nan}      == {'ae': np.nan}      ->  True   (cùng một object)
    {'ae': float('nan')} == {'ae': float('nan')} ->  False

Nghĩa là trên dataset test đang dùng, assertion về `oos` KHÔNG THỂ FAIL. Nó là một assertion
vô hiệu — cùng họ với lỗi đã khiến E2 lần trước bác bỏ. Hành vi thật thì đúng (tôi đã tự
chứng minh bằng OOS số thật), nhưng test không chứng minh được điều đó.

**Vế (a) — KHÔNG CHẠY ĐƯỢC.** Proxy chặn cài gói (cùng gốc với BLK-001), nên không dựng
được venv sạch từ `pyproject.lock`. Theo `EVIDENCE_STANDARD.md`, phần chưa chạy phải ghi
NOT_TESTED, không được suy diễn từ vế (b). Vì vậy status tổng của check này là NOT_TESTED.
Thiếu cụ thể: `python -m venv` sạch + `pip install -r pyproject.lock` trên máy có mạng, rồi
chạy lại `run_gate1` trên cùng dataset và đối chiếu metric với lần chạy trong môi trường
hiện tại.

### CHECK-A1-10 — PASS

**Nửa test suite.** Tôi tự chạy `python -m pytest tests/` tại `2f20e6c`, working tree sạch:
**130/130 PASS, exit code 0**, không FAIL, không skip, không xfail. Khớp con số người cài đặt
báo cáo.

**Nửa đối chiếu số liệu trước–sau.** Tôi KHÔNG dùng lại bảng số của người cài đặt. Tôi chạy
cùng một script snapshot trên hai cây mã (`/tmp/wp-a1-before/src` = `d72fbc4` và
`/home/user/coin/src` = HEAD), trên CÙNG một dataset tổng hợp (seed 42, 2019-01-01..2026-06-30),
với NaN được chuẩn hoá thành chuỗi để so sánh không dựa vào identity của `np.nan`:

    BEFORE(d72fbc4) == AFTER(HEAD) : True
    khoá khác nhau                 : []      (không khoá nào)

    dataset_hash   = 2a412132d1798a9bb078f6f37eac8f86623ca6eda2cb6d1dd6bbabfb8fb4fd4e
    primary_median = 97.51432329190644
    oos            = {"ae": 99.05769511161444, "oos_months": 18}
    ae_by_window   = W1 94.4926850969386  W2 99.3090452187111  W3 85.63517640668388
                     W4 101.75065259539686 W5 97.75403042130573 W6 106.92305470021589
                     W7 93.39571173352473  W8 101.55966977625386 W9 88.99294037466929

Snapshot gồm cả `bootstrap_descriptive`, `benchmarks`, `diagnostics`, `anchor_set_medians`,
`concentration`, `cash_ratio`, `counters_w5`, `_full_run_eth`. So sánh của tôi MẠNH HƠN của
người cài đặt ở hai điểm: (i) dataset kéo tới 2026-06-30 nên `oos.ae` là số thật chứ không
NaN — bằng chứng của họ có `oos.ae` và `xirr` NaN ở cả hai phiên bản nên vế đó vô hiệu;
(ii) khối `bootstrap_descriptive` nằm TRONG snapshot chứ không bị bộ lọc scalar loại ra.

Kết luận: WP-A1 không đổi một số liệu mô phỏng nào. `dataset_hash` cũng không đổi, xác nhận
việc gắn nhãn nguồn không đi vào hash dữ liệu.

### Quét test PASS giả (yêu cầu riêng của phiên này)

Đây là lý do E2 lần trước bác bỏ gói, nên tôi quét kỹ `tests/test_wp_a1_provenance.py`
(66 assertion):

- `or True` / `assert True` / `except: pass` / `pytest.skip` / `xfail`: **0 kết quả**.
- `if hasattr(...)` bọc assertion: **0 kết quả** — mẫu đã hạ gục lần trước đã bị loại bỏ.
- 4 câu `if` còn lại đều nằm trong vòng lặp thu thập (`pinned`, `wrong`, `absent`), và kết
  quả thu thập được assert VÔ ĐIỀU KIỆN sau đó (`assert not absent`, `assert not wrong`).
  Không có assertion nào bị bỏ qua.
- Hai hằng số hash ghim cứng trong `test_a1_04_created_at_does_not_affect_any_hash` KHÔNG
  phải "assert vào hằng số vô nghĩa": tôi đã dựng lại cả hai từ cây mã `d72fbc4` và chúng
  khớp.
- Test bị làm yếu so với `d72fbc4`: **không có**. `git diff --name-only d72fbc4..HEAD -- tests/`
  chỉ trả về `tests/test_wp_a1_provenance.py`; không file test nào khác bị chạm. Test duy
  nhất bị XOÁ là `test_a1_10_no_simulation_behavior_changed`, thân hàm là `assert True` —
  xoá nó là cải thiện, không phải làm yếu.

Nhưng còn HAI assertion vô hiệu kiểu khác, đã ghi ở CHECK-A1-06 (F-E2A1-05) và CHECK-A1-09
(F-E2A1-07): chúng không bị bọc trong `if`, nhưng chúng không thể FAIL vì lý do chúng tuyên
bố kiểm. Chất lượng test đã tốt lên rõ rệt so với `d72fbc4`, nhưng lớp defect "PASS vì lý do
sai" chưa được dọn sạch.

## Mismatches With Implementer Claims

1. **CHECK-A1-05** — Người cài đặt viết: "`fetch.fetch_all` phân loại theo từng series từ các
   cơ chế `fetch_series` thực sự đã dùng." SAI trong trường hợp không có cơ chế nào được
   dùng: mã rơi về `SOURCE_REST`, một nhãn không có căn cứ và ĐỦ TƯ CÁCH official.
   Kiểm chứng bằng probe stub, không cần mạng.

2. **CHECK-A1-07** — Người cài đặt viết: "ĐIỀU KIỆN ĐỦ TƯ CÁCH (fail-closed) — mọi series
   phải mang nguồn thuộc `REAL_SOURCES`, VÀ lineage phải verify được checksum." Bảng probe
   của họ đầy đủ và tôi tái lập được từng dòng. Nhưng "mọi series" ở đây thực chất là "mọi
   series CÓ TRONG LINEAGE", không phải mọi series được nạp và dùng. Lineage khai thiếu →
   `(True, 'verified')`. Giới hạn này không được công bố ở đâu.

3. **CHECK-A1-06** — Người cài đặt viện dẫn `test_a1_06_synthetic_not_official_in_gate2_gate3`
   làm bằng chứng "không gate nào có đường dẫn xuất riêng". Test đó dùng `limit=1` nên
   không thể FAIL vì lý do đó. Hành vi thật thì ĐÚNG — tôi đã tự chạy `limit=None` với
   manifest đầy đủ 219/114 và cả hai gate cho `official=False` — nhưng bằng chứng E1 mà họ
   viện dẫn không chứng minh được điều họ nói.

4. **CHECK-A1-09** — Người cài đặt viết: "`ae_by_window`, `primary_median`, `oos`, và
   `bootstrap_descriptive` … so sánh bằng `==`, không có dung sai". Với dataset mà test dùng,
   `oos.ae` là NaN ở cả hai lần chạy và assertion PASS nhờ lối tắt identity của `np.nan`
   singleton, không phải nhờ số liệu trùng nhau. Họ ĐÃ tự công bố hiện tượng NaN-identity ở
   phần CHECK-A1-10 nhưng không nối nó sang CHECK-A1-09, nơi nó làm một assertion mất hiệu lực.

5. **Trạng thái gate** — Mọi check trong Completion Gate vẫn ghi `Status: NOT_TESTED` dù
   phần Evidence đã được điền đầy đủ, và `Status:` của task vẫn là `IN_PROGRESS`. Không phải
   sai sót kỹ thuật, nhưng nghĩa là gate chưa được đóng chính thức.

6. **Không có mismatch** ở CHECK-A1-01, A1-02 (phần đã chạy), A1-03, A1-04, A1-08, A1-10:
   tôi tái lập độc lập và mọi con số họ báo cáo đều đúng. Đặc biệt, bảng hash trước–sau của
   CHECK-A1-04 và bảng lệch lockfile 9/15 dòng của CHECK-A1-08 đều chính xác.

## Findings

**F-E2A1-01 — Mặc định fail-OPEN khi gán nhãn nguồn trong `fetch_all` (mức: CAO).**
`src/eth_dca_os/data/fetch.py`: `sources[key] = used[0] if used else SOURCE_REST`. Series
không có cơ chế nào đóng góp (0 dòng) được dán nhãn `binance_rest` và đủ tư cách official.
Nằm trên đúng đường đi của official run T-06, và mâu thuẫn với nguyên tắc fail-closed mà
`docs/CONVENTIONS.md` tự phát biểu. Sửa: mặc định `SOURCE_UNKNOWN`, và cân nhắc từ chối
thẳng series có `row_count == 0`. Đóng CHECK-A1-05 và một nửa CHECK-A1-07.

**F-E2A1-02 — `official_eligibility` không kiểm lineage phủ đủ series được dùng (mức: TRUNG BÌNH-CAO).**
`src/eth_dca_os/data/dataset.py::official_eligibility` chỉ duyệt entry có trong lineage.
Lineage khai 1/3 series (nhãn real, hash đúng) vẫn cho `(True, 'verified')` trong khi hai
series còn lại là synthetic. Sửa: bắt buộc tập entry trong lineage phủ đúng ba khoá mà
`load_dataset` nạp (`ETHUSDT_1d`, `BTCUSDT_1d`, `ETHUSDT_15m`), thiếu một khoá là FAIL.

**F-E2A1-03 — Provenance im lặng suy biến ngoài môi trường editable install (mức: TRUNG BÌNH).**
`_REPO_ROOT = Path(__file__).resolve().parents[2]` đúng cho checkout nguồn / `pip install -e`,
nhưng với cài đặt wheel thường thì trỏ vào site-packages. Tôi tái dựng bằng cách copy package
ra ngoài repo:

    _REPO_ROOT           = <thư mục ngoài repo>
    code_commit          = unknown
    dependency_lock_hash = no-lockfile

Không có cảnh báo runtime nào. Máy chạy official run là máy có mạng Binance (BLK-001), môi
trường chưa biết, và Master Index §6 CẤM chạy lại official run để sửa — nên đây là kịch bản
mất provenance vĩnh viễn. Sửa: `save_run` nên raise (hoặc in cảnh báo lớn) khi `official=True`
mà `code_commit == "unknown"` hoặc `dependency_lock_hash == "no-lockfile"`.

**F-E2A1-04 — `code_commit` không phân biệt worktree sạch với worktree bẩn (mức: TRUNG BÌNH).**
`_get_code_commit` chỉ chạy `git rev-parse HEAD`. Một run có sửa đổi chưa commit sẽ ghi SHA
của HEAD, tức record "chứng minh" một trạng thái mã không phải trạng thái đã chạy. Sửa: ghi
kèm `git status --porcelain` rỗng/không rỗng, hoặc thêm hậu tố `-dirty`.

**F-E2A1-05 — `test_a1_06_synthetic_not_official_in_gate2_gate3` không thể FAIL vì lý do nó tuyên bố (mức: TRUNG BÌNH).**
`limit=1` đã đủ làm `official` False. Sửa: gọi với `limit=None`, hoặc so sánh cặp
(lineage synthetic vs lineage đủ tư cách) ở cùng `limit`.

**F-E2A1-06 — Lockfile không ghim tzdata của hệ điều hành (mức: THẤP).**
`accounting_timezone = 'Asia/Ho_Chi_Minh'` quyết định biên ngày kế toán và được đọc từ
`/usr/share/zoneinfo`; gói pip `tzdata` không được cài nên lockfile không nói gì về phiên
bản cơ sở dữ liệu múi giờ. Sửa: ghi phiên bản tzdata hệ thống vào header lockfile, hoặc ghim
gói `tzdata` để `zoneinfo` dùng nguồn xác định.

**F-E2A1-07 — Assertion `oos` trong `test_a1_09` vô hiệu trên dataset đang dùng (mức: TRUNG BÌNH).**
`assert a["oos"] == b["oos"]` PASS nhờ `np.nan` là singleton, không phải nhờ số liệu trùng.
Sửa: dùng dataset có OOS thật (`end` sau `2024-12-31`), và/hoặc so sánh qua một hàm chuẩn
hoá NaN thay vì `==` trực tiếp.

**F-E2A1-08 — `data_source: "mixed"` không có trong taxonomy tài liệu (mức: THẤP).**
`build_lineage` sinh `'mixed'` ở mức dataset khi các series khác nguồn; giá trị này đi thẳng
vào run record. Official run thật (archive + REST) gần như chắc chắn sinh ra nó. Bảng
taxonomy trong `docs/CONVENTIONS.md` không liệt kê `mixed`.

**F-E2A1-09 — `run_controls` ghi `official` không tính tới đường dev (mức: THẤP).**
`src/eth_dca_os/pipeline.py::run_controls` đặt `"official": prep.official_eligible`, không
kèm điều kiện nào về `n_sims`. `cli.py` hạ `n_sims` xuống 200 khi có `--dev-limit`, nên một
dev run trên dữ liệu đủ tư cách sẽ ghi record `RANDOM_CONTROL` mang `official: true` trong
khi GATE1/GATE2/GATE3/BASELINE của cùng lần chạy đều `false`. Không nhất quán trong cùng
một `backtest_runs.jsonl`.

**Ghi nhận (không phải finding mới) — dán nhãn sai bằng tay.** Sửa `lineage.json` từ
`synthetic` thành `binance_bulk_archive` (giữ nguyên `file_hash`) cho `(True, 'verified')`.
Giới hạn này ĐÃ được công bố trong `docs/CONVENTIONS.md` và trong Evidence của CHECK-A1-07,
kèm biện pháp đối trọng (đối chiếu `ethdca freeze` hai máy theo DEC-003). Tôi xác nhận nó
có thật và đã được công bố đúng.

**Ghi nhận — Exit Criteria còn hở.** `PROJECT/PROJECT_PROGRESS.md` vẫn ghi WP-A1 ở trạng
thái `READY`; RSK-006 và RSK-008 vẫn ở nguyên trạng thái "S001 XÁC NHẬN (E1)"; chưa có file
handoff cho phiên cài đặt trong `docs/sessions/` (mới nhất là `S006-wp-a2-pipeline-wiring.md`).
Đây là ba mục Exit Criteria chưa hoàn thành, độc lập với các FAIL kỹ thuật ở trên.

**Điều gói này làm ĐÚNG (ghi để cân bằng, không phải để giảm nhẹ kết luận).** So với
`d72fbc4`, remediation đã sửa thật những gì E2 lần trước bác bỏ: chuỗi dẫn xuất
`lineage -> verified source -> official` tồn tại thật và là nguồn sự thật duy nhất cho cả
bốn loại run; lockfile viết tay đã được thay bằng lockfile sinh từ môi trường thật và tôi
xác minh 15/15 dòng; `created_at` được thêm mà không dịch chuyển một bit hash nào (tôi tự
dựng lại đối chiếu từ `d72fbc4`); `sensitivity_manifest_hash` nay có ở GATE2/GATE3; hard-code
`/home/user/coin` đã biến mất; mẫu `if hasattr(...)` bọc assertion đã bị loại bỏ hoàn toàn;
và 130/130 test PASS là thật.

## Conclusion

**E2 FAIL**

Kết luận này KHÔNG dựa trên "trông có vẻ chưa đủ". Nó dựa trên hai đường tôi tự dựng và tự
chạy được, biến dữ liệu không chứng minh được nguồn gốc thành `official_eligibility ->
(True, 'verified')`:

1. `fetch_all` dán nhãn `binance_rest` cho series mà KHÔNG cơ chế nào tạo ra (F-E2A1-01) —
   một lần `fetch` không lấy được dòng nào vẫn đủ tư cách official. Đây là đường của official
   run thật.
2. `official_eligibility` chấp nhận lineage khai thiếu series (F-E2A1-02) — hai phần ba
   dataset có thể là synthetic mà vẫn cho `verified`.

Bất biến trung tâm của WP-A1 — "không tồn tại đường nào để một run trên dữ liệu giả tự nhận
là official" — vì vậy chưa đóng. Cả hai đều là fail-open trong một cơ chế mà chính tài liệu
của gói tuyên bố là fail-closed, cả hai đều sửa được bằng vài dòng, và cả hai đều nằm ngoài
giới hạn đã được công bố.

Kèm theo: CHECK-A1-09 chỉ đạt một nửa yêu cầu FROZEN (vế "môi trường sạch từ lockfile" không
chạy được vì proxy chặn cài gói), nên theo `EVIDENCE_STANDARD.md` phải ghi NOT_TESTED chứ
không được ghi PASS.

**WP-A1 KHÔNG đủ điều kiện chuyển DONE.** Exit Criteria "100% REQUIRED checks PASS" và
"Không defect nghiêm trọng nào chưa xử lý" đều chưa thoả. Ba mục Exit Criteria khác
(PROJECT_PROGRESS, RSK-006/RSK-008, session handoff) cũng chưa hoàn thành. GATE-A không đóng
được, nên T-06 chưa được mở.

## Required Follow-up

Bắt buộc trước khi WP-A1 có thể được xét DONE:

1. **F-E2A1-01** — Đổi mặc định trong `fetch_all` từ `SOURCE_REST` sang `SOURCE_UNKNOWN`;
   cân nhắc từ chối thẳng series `row_count == 0`. Thêm test dùng stub I/O (không cần mạng,
   mẫu đã được chứng minh khả thi trong phiên này) cho đủ bốn kịch bản archive/REST/cả hai/
   không có gì, và assert nhãn cho TỪNG series. Việc này cũng biến CHECK-A1-05 từ "chỉ kiểm
   được đường synth" thành kiểm được cả đường fetch mà không cần gỡ BLK-001.

2. **F-E2A1-02** — `official_eligibility` phải yêu cầu lineage phủ đúng tập series mà
   `load_dataset` nạp; thiếu một series là FAIL kèm lý do. Thêm test cho lineage khai thiếu.

3. **F-E2A1-03** — `save_run` phải fail-loud khi `official=True` mà `code_commit == "unknown"`
   hoặc `dependency_lock_hash == "no-lockfile"`. Không được ghi âm thầm một official record
   mất provenance, vì Master Index §6 cấm chạy lại để sửa.

4. **F-E2A1-05** và **F-E2A1-07** — Sửa hai assertion vô hiệu. Đây là cùng lớp defect đã
   khiến E2 lần trước bác bỏ gói; để lại nghĩa là bằng chứng E1 cho CHECK-A1-06 (nửa
   Gate 2/3) và CHECK-A1-09 (vế OOS) không đứng vững.

5. **CHECK-A1-09** — Ghi trạng thái NOT_TESTED cho vế "môi trường sạch", chuyển phần đó sang
   T-06 (máy có mạng), và nêu tường minh trong task file rằng nó bị BLK-001 chặn. KHÔNG được
   ghi PASS.

Nên làm (không chặn DONE nhưng nên xử lý trong cùng gói):

7. **F-E2A1-04** — Ghi cờ dirty worktree vào `code_commit`.
8. **F-E2A1-06** — Ghi phiên bản tzdata hệ thống vào header lockfile.
9. **F-E2A1-08** — Bổ sung `mixed` vào bảng taxonomy trong `docs/CONVENTIONS.md`.
10. **F-E2A1-09** — Thống nhất cách `run_controls` ghi `official` với ba gate còn lại.
11. Hoàn tất Exit Criteria còn hở: cập nhật `PROJECT/PROJECT_PROGRESS.md` (trạng thái WP-A1,
    RSK-006, RSK-008) và viết session handoff.

Sau khi xử lý xong, gói cần một phiên E2 mới — phiên này KHÔNG được dùng lại làm bằng chứng
cho phiên bản đã sửa.

## Escalation

Áp `governance/core/ESCALATION_PROTOCOL.md`. Đây là lần thứ HAI phép dẫn xuất `official` bị
E2 bác bỏ (lần đầu: không tồn tại phép dẫn xuất; lần này: phép dẫn xuất tồn tại nhưng có hai
mặc định fail-open). Trigger đã ghi trong task file — "Hai cách tiếp cận khác nhau cho việc
dẫn xuất `official` đều không đóng được đường giả mạo → `CAPABILITY_CEILING`, nâng Tier lên D"
— cần được chủ dự án cân nhắc.

Ghi chú của reviewer: hai defect lần này thuộc loại KHÁC lần đầu. Lần đầu là thiếu hẳn cơ
chế; lần này cơ chế đã đúng về kiến trúc (một nguồn sự thật, fail-closed với mọi đầu vào dị
dạng tôi thử, có positive control) và chỉ hở ở hai giá trị mặc định. Vì vậy tôi khuyến nghị
coi đây là `VERIFICATION_DEPTH` (giữ Tier C, nâng Effort xhigh → max) hơn là
`CAPABILITY_CEILING`, và để chủ dự án quyết định — reviewer không tự chọn thay.
