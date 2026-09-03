# E2 INDEPENDENT REVIEW — WP-A1 / CHECK-A1-11 (vòng BỐN)

Review ID:
E2-WP-A1-004

Task / Release:
`WP-A1` — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức.
Check được rà soát: `CHECK-A1-11` (Audit độc lập, Evidence Level **E2**).

Reviewer Session:
Phiên reviewer độc lập (Opus / high). KHÔNG phải phiên cài đặt. KHÔNG sửa production code.

Executed By:
Independent E2 Reviewer

Timestamp:
2026-09-03

---

## 0. Baseline được đo trước khi rà soát

    branch                = claude/coindca-data-stream-vv0vwv
    HEAD                  = 990a6bbf675ba8daae5a4a22cedae5282cde8c4c
    default branch        = main (giải bằng script, không giả định)
    behind upstream       = 0
    ahead of default      = 11 commit · divergence LOC = 5712 · divergence age = 0 ngày
    tracked worktree      = CLEAN
    production diff       = EMPTY  (working tree + index, trên
                            `src/eth_dca_os webapp pyproject.toml pyproject.lock`)
    BRANCH AUTHORITY      = PASS
    HARD-STOP kèm theo    = INTEGRATION_DECISION_REQUIRED (ahead>10, loc>5000) — xem §9

    WP-A1 status          = IN_PROGRESS            (khớp kỳ vọng)
    CAP-PROV              = allowed 3 / used 3 / remaining 0   (khớp kỳ vọng)

Reviewer KHÔNG sửa ledger, KHÔNG sửa production code, KHÔNG tiêu repair cycle.

---

## 1. Yêu cầu FROZEN của `CHECK-A1-11` (trích nguyên văn phạm vi)

> Một phiên reviewer độc lập theo "Solo Independent Review Procedure" của
> `EVIDENCE_STANDARD.md`, **bắt đầu từ trạng thái repo chứ không từ tuyên bố của người cài
> đặt**, chạy lại `CHECK-A1-06`, `A1-07`, `A1-09` và ghi bằng chứng riêng. Lưu tại
> `docs/reviews/` theo `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.

Phạm vi bổ sung do `DEC-027` mở ra và do đó thuộc lượt E2 này: ba hạng mục
`LEGACY_GATE_DISPOSITION_REQUIRED` — `F-E2A1-03` (B.1), `F-E2A1R3-03` (B.2),
`F-E2A1R3-06`+`F-E2A1-08` (B.3).

Không có xung đột giữa prompt phiên này và canonical contract. Nơi prompt yêu cầu rộng hơn
(môi trường clean/non-editable, đối chứng docs↔code), yêu cầu đó nằm TRONG nội dung của
finding gốc nên reviewer thực hiện.

---

## 2. Thủ tục độc lập THỰC TẾ đã thực hiện (theo đúng thứ tự)

1. Đọc `AGENTS.md` → CORE authority order → `PROJECT_*` → `DEC-027` → task file WP-A1
   (Completion Gate FROZEN) → `docs/CONVENTIONS.md` → `REVIEW_BUDGET_LEDGER.md` →
   `HARDENING_BACKLOG.md`.
2. Đọc **prior finding** `F-E2A1-03` / `F-E2A1R3-03` / `F-E2A1R3-06` / `F-E2A1-08` — được
   phép, vì frozen gate buộc reviewer tái kiểm chính chúng.
3. Đọc **implementation hiện tại** (`reporting.py`, `pipeline.py`, `data/dataset.py`,
   `cli.py`) và `git diff` của chu kỳ, KHÔNG đọc kết luận cuối của implementer.
4. Tự thiết kế 8 reproduction (R1–R8) + 5 mutation (M1–M5); tự dựng môi trường sạch.
5. Chạy toàn bộ; **ghi PROVISIONAL VERDICT ra file trước khi mở báo cáo implementer**.
6. Chỉ SAU đó mới đọc `docs/sessions/S017-*.md` và §"REPAIR CYCLE CUỐI" của task file để
   đối chiếu (§8).

**Rò rỉ độc lập phải khai báo (không che):** khi `grep` tìm định vị `dev_limit_set`, kết quả
có kèm dòng tóm tắt S017 trong `PROJECT_PROGRESS.md` / `LO_TRINH_DE_HIEU.md`; và bảng mục lục
heading của task file để lộ ba tiêu đề chứa chữ "ĐÓNG". Reviewer KHÔNG đọc thân các mục đó
trước khi kết luận, và **toàn bộ verdict dưới đây dựa trên reproduction do reviewer tự chạy**,
không dựa trên bất kỳ tuyên bố nào của implementer. Mức độ ảnh hưởng: reviewer biết trước
implementer *tuyên bố* đã đóng, nhưng không biết *bằng chứng nào* và vẫn phải tự tái lập.

---

## 3. Môi trường sạch / non-editable (điều kiện mà finding gốc đòi hỏi)

    venv sạch          = python 3.11.15, tạo mới
    cài từ lockfile    = 15/15 pin trong `pyproject.lock` cài THÀNH CÔNG
    cài project        = pip install --no-deps .   (NON-EDITABLE, wheel)
    vị trí module      = <venv>/lib/python3.11/site-packages/eth_dca_os/
    _REPO_ROOT suy ra  = <venv>/lib/python3.11        <- KHÔNG phải repo, KHÔNG có lockfile

Đây đúng môi trường mà `F-E2A1-03` mô tả và `CHECK-A1-09` bắt buộc.

---

## 4. Reproduction do reviewer tự thiết kế và tự chạy

### R1 — `save_run` trong môi trường clean/non-editable  (B.1 / `F-E2A1-03`)

    code_commit           = unknown
    dependency_lock_hash  = no-lockfile
    _provenance_state()   = ['code_commit', 'dependency_lock_hash']

    R1a  official=True   -> RAISE ProvenanceUnresolvedError
         artifact để lại -> THƯ MỤC KHÔNG TỒN TẠI  (0 file)
    R1b  official=False  -> ghi bình thường, record mang
         provenance_resolved   = False
         provenance_unresolved = ['code_commit', 'dependency_lock_hash']

### R7 — đường OFFICIAL THẬT, end-to-end (`run_gate1`, `dev_limit=None`), env clean

    dataset official_eligible = True / 'verified'   (đủ tư cách, không phải bị chặn từ dataset)
    -> RAISE ProvenanceUnresolvedError sau 41s
    -> artifact trong out_dir: THƯ MỤC KHÔNG TỒN TẠI (0 artifact)

### R8 — POSITIVE CONTROL: git checkout có lockfile → official run PHẢI ghi được

    _REPO_ROOT            = /home/user/coin
    official              = True
    code_commit           = 990a6bbf675ba8daae5a4a22cedae5282cde8c4c   (= HEAD)
    dependency_lock_hash  = 9ea0150f…4d9a  (= sha256(pyproject.lock), đối chiếu khớp)
    provenance_resolved   = True   ·  provenance_unresolved = []
    python_version 3.11.15 · simulation_seed · dataset_hash · sensitivity_manifest_hash ·
    strategy/execution_config_hash · master_seed · created_at — đủ 8 nhóm trường.

R8 là điều kiện SỐNG CÒN của lượt rà soát này: thiếu nó, một bản sửa "luôn luôn từ chối"
cũng làm R1a/R7 xanh.

### R2 — ma trận đối kháng `official_eligibility` (17 probe)  → `CHECK-A1-06`, `A1-07`

    P0  nhãn real + hash khớp (POSITIVE CONTROL) -> (True,  'verified')
    P1  synthetic                                -> (False, "source_not_real:ETHUSDT_1d='synthetic'")
    P2  unknown                                  -> (False, "source_not_real:ETHUSDT_1d='unknown'")
    P3  lineage = None                           -> (False, 'lineage_missing')
    P4  lineage = {}                             -> (False, 'lineage_malformed')
    P5  lineage = {'files': []}                  -> (False, 'missing_required_series:ETHUSDT_1d')
    P6  thiếu 1 series canonical                 -> (False, 'missing_required_series:BTCUSDT_1d')
    P7  series lạ ngoài REQUIRED                 -> (False, 'unexpected_series:SOLUSDT_1d')
    P8  series trùng lặp                         -> (False, 'duplicate_series:BTCUSDT_1d')
    P9  row_count = 0                            -> (False, 'empty_series:ETHUSDT_15m')
    P10 file_hash bị sửa                         -> (False, 'file_hash_mismatch:BTCUSDT_1d.parquet')
    P11 dataset_hash sai                         -> (False, 'dataset_hash_mismatch')
    P12 xoá 1 file trên đĩa                      -> (False, 'missing_file:BTCUSDT_1d.parquet')
    P13 không khai requested range               -> (False, 'coverage_undeclared:ETHUSDT_1d')
    P14 coverage cắt cụt                         -> (False, 'incomplete_coverage:…')
    P15 dataset='mixed' + 1 series synthetic     -> (False, "source_not_real:BTCUSDT_1d='synthetic'")
    P16 dataset='mixed', MỌI series đều REAL     -> (True,  'verified')

P15/P16 là phép kiểm trực tiếp điều mà B.3 vừa ghi vào tài liệu: `mixed` **chỉ mô tả**, tư
cách official quyết bởi kiểm per-series với `REAL_SOURCES`. Thực tế mã khớp đúng tài liệu.

Bề mặt CLI/env (tự rà, không chép lại kết luận cũ):

    `grep -rn "os.environ|getenv" src/eth_dca_os/`  -> 0 kết quả
    `cli.py`: không có --official / --force-official / --source / --real-data
    `official_eligibility(raw_dir, lineage)` — đúng hai tham số, không cờ, không override

### R4 / R5 — contract case 13 tại **cả ba** enforcement point  (B.2 / `F-E2A1R3-03`)

    _official_reason(prep, None) -> 'verified'
    _official_reason(prep, 1|5|200) -> 'dev_limit_set'

    run_gate1(dev_limit=5)  -> official=False · official_reason='dev_limit_set'  (49s)
    run_gate2(limit=2)      -> official=False · official_reason='dev_limit_set'  (49s)
    run_gate3(limit=2)      -> official=False · official_reason='dev_limit_set'  (136s)
    run_record của gate1    -> official=False · data_source='binance_rest'

### R6 — TRƯỚC/SAU repair: chứng minh KHÔNG đổi hành vi tính toán

Cùng dataset, cùng seed, cùng `dev_limit=5`; payload `run_gate1` bỏ đúng ba khoá được phép
đổi (`official_reason`, `run_record`, `lineage`) rồi băm:

    BEFORE (61cf54b) payload sha256 = 076e42a2d9c88215490ac9abcc635f05a7ea303ef44c60e539f11bce8d2c669e
    AFTER  (990a6bb) payload sha256 = 076e42a2d9c88215490ac9abcc635f05a7ea303ef44c60e539f11bce8d2c669e
    GIỐNG HỆT = True
    primary_median 98.00082425938395 -> 98.00082425938395 (bằng `==`, không dung sai)
    ae_by_window / oos / counters_w5 = giống hệt
    official_reason 'verified' -> 'dev_limit_set'   <- ĐÚNG và CHỈ MỘT thứ đổi

Bổ sung bằng đọc mã: `diff -rq` giữa cây `61cf54b` và HEAD cho **đúng 2 file** khác nhau
(`pipeline.py`, `reporting.py`); `engine.py`, `regime.py`, `ladders.py`, `capital.py`,
`score.py`, `gates.py`, `verdict.py`, `metrics.py` **giống hệt từng byte**.

### CHECK-A1-09 — tái lập trong môi trường dựng từ lockfile

    venv sạch dựng từ `pyproject.lock`: 15/15 pin cài được (tiền đề "proxy chặn cài gói" SAI)
    hai process ĐỘC LẬP, PYTHONHASHSEED mặc định vs 999983
    -> payload sha256 TRÙNG KHỚP TUYỆT ĐỐI; primary_median bằng nhau bằng `==`

### M1–M5 — kiểm tính HỢP LỆ của oracle (mutation trên bản SAO, không đụng repo)

    M1 bỏ enforcement case 13 (quay về hành vi cũ)  -> ĐỎ (3 ca)   ✔ giết được
    M2 bỏ cổng provenance fail-loud                 -> ĐỎ (3 ca)   ✔ giết được
    M3 bản sửa LƯỜI: luôn trả 'dev_limit_set'       -> ĐỎ (2 ca)   ✔ giết được
    M4 cổng LUÔN từ chối official (stub "luôn False")-> ĐỎ (2 ca)  ✔ giết được
    M5 gọi lại `_get_code_commit()` khi dựng record -> XANH (equivalent mutant, xem §9.4)

M3 và M4 là hai đối chứng quan trọng nhất: oracle không phải con dấu cao su, và cũng không
nghiệm thu một cổng chỉ biết từ chối.

---

## 5. Kết quả test

    Test đích `tests/test_wp_a1_legacy_gate_repair.py` (reviewer tự chạy, venv sạch):
        12 test / 12 PASS
    Test cũ về provenance / eligibility contract / CLI: nằm trong full suite dưới đây.

    FULL SUITE (reviewer tự chạy, venv sạch dựng từ `pyproject.lock`, cây mã HEAD):

        377 test collected  ->  377 PASS

    Cách đọc bằng chứng, không dựa vào dòng tóm tắt: `addopts = -q` của repo cộng thêm `-q`
    của lệnh làm pytest im lặng hoàn toàn ở dòng cuối, nên reviewer đếm TRỰC TIẾP trên
    progress line:

        số ký tự '.' trong log = 377          (đúng bằng số test collect được)
        số ký tự 'F' | 'E' | 's' | 'x' = 0    (không FAILED, không ERROR, không skip/xfail)

    `--collect-only -q` xác nhận độc lập: **377 tests collected**. Khớp phép cộng trong biên
    bản S017 (365 + 12 test mới = 377).

    LẦN CHẠY XÁC NHẬN (lần hai, `-o addopts=` để pytest in dòng tóm tắt, `-p no:cacheprovider`):

        377 passed in 1101.43s (0:18:21)
        EXIT=0

    Hai lần chạy độc lập trong cùng venv sạch cho cùng kết quả: 377/377 PASS, 0 FAILED,
    0 ERROR, 0 skip/xfail.
---

## 6. Đối chiếu docs ↔ implementation

| Điểm tài liệu (`docs/CONVENTIONS.md`) | Mã hiện tại | Kết quả |
|---|---|---|
| Taxonomy 4 giá trị **tầng series** quyết định official | `VALID_SOURCES` / `REAL_SOURCES` | KHỚP |
| `mixed` là nhãn **tầng dataset, chỉ mô tả**, không thuộc `VALID_SOURCES` | `build_lineage`: `"mixed"` khi `len(distinct)>1`; `official_eligibility` kiểm per-series | KHỚP (P15/P16) |
| `empty_series:<series>` khi `row_count <= 0` | `dataset.py` bước 4 | KHỚP (P9) |
| `source_not_real:<series>=<giá trị>` | `dataset.py` bước 5 | KHỚP (P1/P2) |
| Thứ tự kiểm 7 bước cố định để reason code tất định | Thứ tự mã đúng như liệt kê | KHỚP |
| `official` là hàm dẫn xuất, chữ ký khoá bằng test | `official_eligibility(raw_dir, lineage)` | KHỚP |
| Giới hạn: không chống được nhãn `binance_*` dán tay | ghi rõ, đối trọng `ethdca freeze` (DEC-003) | KHỚP |

Sai lệch tìm được: xem `N-03` (§9.3) — hành vi fail-loud mới và hai trường record mới
chưa được ghi vào `CONVENTIONS.md`.

---

## 7. So với tuyên bố của implementer (chỉ đọc SAU khi đã chốt provisional verdict)

| Tuyên bố S017 | Kết quả reviewer tự kiểm | Khớp? |
|---|---|---|
| `F-E2A1-03` đóng: official bị từ chối, chưa artifact nào được tạo | R1a, R7 — xác nhận, 0 artifact | KHỚP |
| Đường non-official ghi trạng thái suy biến tường minh | R1b — xác nhận | KHỚP |
| `F-E2A1R3-03` đóng tại cả `run_gate1/2/3` | R4, R5 — xác nhận cả ba | KHỚP |
| Dataset tự nó không hợp lệ thì GIỮ lý do gốc | M3 giết được bản sửa lười; P1/P15 giữ lý do gốc | KHỚP |
| `run_controls` ngoài hợp đồng vì không có `dev_limit` | đọc mã: đúng, `run_controls` nhận `n_sims` | KHỚP (nhưng xem `N-02`) |
| B.3 docs-only, production diff = 0 | `git diff d4586b8..28b0255 -- <production paths>` = RỖNG | KHỚP |
| Production diff chu kỳ = 2 file, không đụng engine/… | `diff -rq` — đúng 2 file | KHỚP |
| Không đổi giá trị tính toán nào | R6 — payload sha256 giống hệt | KHỚP |
| `CAP-PROV` allowed 3 / used 3 / remaining 0 | ledger — đúng | KHỚP |
| S017 KHÔNG tự đánh `CHECK-A1-11` = PASS | task file để `CHECK-A1-11` chờ E2 | KHỚP |
| "**13/13** PASS" (§5 biên bản S017) | file có **12** hàm test, chạy được **12/12** | **LỆCH** → `N-04` |

Không có tuyên bố nào của implementer bị reviewer bác bỏ về mặt hành vi.

---

## 8. Findings

Không finding nào đạt đủ **cả ba** tiêu chí BLOCKING (`REVIEW_PROTOCOL.md` §Finding Routing).

### N-01 — `code_commit` có thể nhận SHA của một git repo **LẠ** — HARDENING

Bằng chứng (reviewer tự dựng, tái lập được):

    cây mã dự án được COPY (không kèm `.git`) vào trong một git repo khác;
    `_REPO_ROOT` = thư mục copy; `pyproject.lock` THẬT nằm ở đó;
    `git rev-parse HEAD` với `cwd=_REPO_ROOT` đi NGƯỢC LÊN repo bao ngoài
    -> code_commit = 2898f912… (SHA của repo LẠ, không thuộc dự án)
    -> provenance_resolved = True, official run ĐƯỢC GHI

Vì sao KHÔNG BLOCKING: `HARDENING` được định nghĩa gồm "trường hợp đối kháng **không dựng
được từ một nguồn production hợp lệ**". Nguồn production hợp lệ cho official run — chính
`S017` đã ghi thành ràng buộc vận hành và `DEC-027` hàm ý — là **một git checkout của dự án
có lockfile**; ở đúng nguồn đó R8 cho SHA ĐÚNG. Kịch bản trên đòi vận hành viên chạy official
run từ một bản sao mã trần, tức đã vi phạm ràng buộc vận hành. Ngoài ra hậu quả **phát hiện
được về sau** (SHA lạ không phân giải được trong repo dự án), khác hẳn `'unknown'` im lặng.

    RE_TRIGGER_CONDITION:
    - quy trình `T-06` KHÔNG kiểm được rằng máy chạy official run là một git checkout của
      CHÍNH repo dự án; HOẶC
    - official run được chạy từ artifact đóng gói (wheel/sdist/container) thay vì checkout;
      HOẶC
    - `WP-B3` (audit trail) bắt đầu dùng `code_commit` làm khoá tra cứu.

    Sửa tối thiểu (nếu Owner muốn đóng): đối chiếu `git rev-parse --show-toplevel` với
    `_REPO_ROOT`, lệch thì coi như KHÔNG phân giải được. ~3 dòng trong `reporting.py`.

### N-02 — `RE_TRIGGER_CONDITION` của `H-03` (`F-E2A1-09`) **ĐÃ KÍCH HOẠT** — governance sync

`H-03` ghi rõ một trong ba vế re-trigger là: *"`F-E2A1R3-03` được sửa (mã lý do
`dev_limit_set`) — lúc đó bất nhất này trở nên nhìn thấy được và nên đóng cùng gói"*. Vế đó
nay ĐÃ xảy ra. Đọc mã xác nhận `run_controls` vẫn ghi `official = prep.official_eligible` và
`official_reason = prep.official_reason`, không tính đường dev (`n_sims`).

Vì sao KHÔNG BLOCKING: trên một official run thật (`n_sims=1000`, `dev_limit=None`) mọi
record đều `official=true` nhất quán; bất nhất chỉ hiện trên **run dev**, nên không có hậu
quả nghiệp vụ trên đường official. Tiêu chí (2) của BLOCKING không thoả.

Điều cần Owner làm: ghi nhận re-trigger đã kích hoạt trong `HARDENING_BACKLOG.md` (docs-only),
để mục này không bị đọc nhầm là "chưa tới hạn".

### N-03 — Hành vi fail-loud mới và hai trường record mới chưa vào `CONVENTIONS.md` — HARDENING (docs-only)

`ProvenanceUnresolvedError`, `provenance_resolved`, `provenance_unresolved` được ghi trong
docstring, biên bản S017, `PROJECT_PROGRESS.md` và task file — nhưng KHÔNG có trong
`docs/CONVENTIONS.md`, nơi quy ước triển khai được tra cứu. `docs/spec/04_DATA_MODEL` là spec
V2.1.5 ĐÓNG BĂNG nên không phải chỗ sửa (Master Index §6 → `WP-D2`).

Hậu quả thực tế: bằng 0 trên hành vi; là khe tra cứu cho người vận hành `T-06`.

    RE_TRIGGER_CONDITION:
    - lần cập nhật `docs/CONVENTIONS.md` kế tiếp thuộc `CAP-PROV`; HOẶC
    - quy trình vận hành `T-06` được viết thành văn bản.

### N-04 — Biên bản `S017` §5 ghi "13/13 PASS", số đo thực là 12/12 — sai lệch bằng chứng (docs-only)

`tests/test_wp_a1_legacy_gate_repair.py` có **12** hàm test; reviewer chạy được **12/12 PASS**.
§6 của chính biên bản đó lại ghi "365 + **12** test mới = 377" — tự mâu thuẫn với §5. Con số
377 và 12 là con số ĐÚNG; "13/13" là một sai số học trong phần thuyết minh.

Hậu quả: không đổi kết luận nào; nhưng đây là một con số trong hồ sơ bằng chứng của
Completion Gate nên cần sửa cho đúng. Không tiêu repair cycle (docs-only).

### Đã xét và GIỮ NGUYÊN phân loại (không nâng cấp)

- `H-26` (`gates.py` trả `numpy.bool`): reviewer KHÔNG tìm được bằng chứng MỚI nào thoả đủ ba
  tiêu chí → **GIỮ HARDENING**. Không nâng vì cùng họ với `F-S015-01`.
- `H-13` (`F-E2A1R3-01`, `row_count` ngoài mọi checksum): vẫn đúng như mô tả, vẫn HARDENING;
  không thuộc ba hạng mục `DEC-027` và không có bằng chứng mới.
- `H-01`, `H-02`, `H-04`, `H-05`, `H-06`, `H-07`: không đổi.
- `M5` (§4): **equivalent mutant** — gọi `_get_code_commit()` hai lần chỉ khác nhau khi HEAD
  đổi GIỮA hai lời gọi. KHÔNG tính là lỗ hổng oracle, KHÔNG mở finding.

---

## 9. Ghi chú governance ngoài phạm vi `CHECK-A1-11`

`branch_authority_check.sh` báo `INTEGRATION_DECISION_REQUIRED` (ahead 11 > 10, LOC 5712 >
5000) trên nhánh hiện tại. Theo `AGENTS.md` §7 bước 0 đây là **Owner Decision**, không phải
cảnh báo bỏ qua được. Nó KHÔNG ảnh hưởng verdict kỹ thuật của `CHECK-A1-11` (worktree sạch,
production diff rỗng, mọi công việc S017 nằm trên đúng nhánh này), nhưng cần Owner định đoạt
— hợp lý nhất là gộp cùng lúc chuyển `WP-A1 → DONE`. Tiền lệ: `DEC-013`.

---

## 10. Bảng verdict theo check

| Check ID | Status | Evidence Level | Bằng chứng (reviewer tự thu) |
|---|---|---|---|
| CHECK-A1-06 | PASS | E2 | R2 P0–P16, positive control HỢP LỆ |
| CHECK-A1-07 | PASS | E2 | R2 + rà bề mặt CLI/env (0 `os.environ` trong `src/`) |
| CHECK-A1-09 | PASS | E2 | venv sạch từ lockfile 15/15; 2 process, PYTHONHASHSEED khác nhau, payload sha256 trùng khớp |
| `F-E2A1-03` (B.1) | ĐÓNG | E2 | R1, R7 (từ chối, 0 artifact) + R8 (positive control) |
| `F-E2A1R3-03` (B.2) | ĐÓNG | E2 | R4, R5 (gate1/2/3) + M1, M3 (oracle hợp lệ) |
| `F-E2A1R3-06`+`F-E2A1-08` (B.3) | ĐÓNG | E2 | §6 docs↔code + production diff = 0 đo bằng git |
| An toàn thuật toán/tài chính | XÁC NHẬN | E2 | R6 payload sha256 giống hệt; `diff -rq` đúng 2 file |
| CHECK-A1-10 (regression) | PASS | E2 | full suite 377/377, 0 FAILED/ERROR/skip |
| **CHECK-A1-11** | **PASS** | **E2** | toàn bộ mục §4–§7 |

---

## 11. Kết luận

    CHECK-A1-11 = PASS
    Evidence    = E2

Căn cứ: reviewer tự dựng môi trường sạch/non-editable từ lockfile, tự thiết kế và tự chạy
tám reproduction cùng năm mutation, tự rà bề mặt CLI/env, tự đối chiếu docs với mã, và chỉ
đọc tuyên bố của implementer SAU khi đã ghi provisional verdict. Cả ba hạng mục
`LEGACY_GATE_DISPOSITION_REQUIRED` mà `DEC-027` giao đều đóng được bằng bằng chứng do
reviewer tự thu, có **đối chứng dương hợp lệ** ở cả hai vế (R8 cho cổng provenance, M3/M4 cho
oracle contract) — nên đây không phải một cổng chỉ biết từ chối, cũng không phải một oracle
chỉ biết gật.

Bốn finding mới đều KHÔNG đạt đủ ba tiêu chí BLOCKING và được định tuyến `HARDENING` /
docs-only kèm `RE_TRIGGER_CONDITION`. Không finding nào cần sửa production code trong lượt
này, nên:

    OWNER_EXTENSION_REQUIRED = KHÔNG
    CAP-PROV tiêu thêm       = 0 repair cycle  (allowed 3 / used 3 / remaining 0, KHÔNG đổi)

Do đó:

    WP-A1  ELIGIBLE_FOR_COMPLETION = YES

Reviewer KHÔNG chuyển `WP-A1 → DONE`. Thẩm quyền đó thuộc chủ dự án theo `STATE_AUTHORITY.md`.

---

## 12. Chuỗi thẩm quyền (reviewer KHÔNG tự đi quá bước của mình)

    CHECK-A1-11 PASS
            ↓
    WP-A1 ELIGIBLE_FOR_COMPLETION
            ↓
    OWNER completion authority  (STATE_AUTHORITY.md)
            ↓
    WP-A1 = DONE
            ↓
    GATE-A CLOSED

Reviewer KHÔNG viết `WP-A1 = DONE`, KHÔNG đóng `GATE-A`, KHÔNG duyệt `T-05`, KHÔNG chạy `T-06`.

## 13. Còn lại trước `T-06` (ngoài `GATE-A`)

1. Owner chuyển `WP-A1 → DONE` → `GATE-A` đóng.
2. `T-05` được Owner phê duyệt.
3. `BLK-001` — đường chạy real-data production-realistic.
4. `DEC-026`: lát cắt `WP-B1` pre-T06 đã PASS; **full `WP-B1` vẫn `PLANNED`**.
5. Ràng buộc vận hành mới: official run phải chạy từ **git checkout có lockfile** — nếu
   không, `save_run` từ chối (đúng thiết kế). Xem thêm `N-01`.
