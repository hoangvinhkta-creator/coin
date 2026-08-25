# PRE-S008 — WP-A1 Contract & Environmental Satisfiability Review

Loại phiên:
PRE-S008 — rà soát, KHÔNG remediation. Không sửa product code.

Ngày:
2026-08-24

Thực hiện bởi:
Phiên PRE-S008 (Opus / xhigh)

---

## 1. HEAD / branch / ancestry

Branch:
`claude/wp-a1-provenance-v67k9h`

HEAD:
`66f5e223b9e3245ff6413cdc8de0a4a23502c9b2`

origin/claude/wp-a1-provenance-v67k9h:
`66f5e223b9e3245ff6413cdc8de0a4a23502c9b2` — trùng HEAD, không phân kỳ

Working tree:
SẠCH tại thời điểm mở phiên

Lịch sử tuyến tính, không nhánh, không merge:

    666de14  WP-A2 DONE (baseline trước WP-A1)
      └─ d72fbc4  WP-A1 cài đặt lần đầu          <- E2 lần MỘT bác bỏ commit này
         └─ f49776e  remediation: dẫn xuất official từ lineage
            └─ beae874  lockfile sinh lại từ môi trường thật
               └─ 792cafd  CHECK-A1-03 đối chiếu HEAD tại thời điểm run
                  └─ 2f20e6c  bằng chứng regression 130/130   <- E2 lần HAI review commit này
                     └─ 66f5e22  ghi kết quả E2 FAIL          <- HEAD

## 2. SHA reconciliation

| Câu hỏi | Trả lời | Bằng chứng |
|---|---|---|
| `d72fbc4` là gì? | Bản cài đặt WP-A1 lần đầu, đã bị E2 lần một bác bỏ | `git log` |
| `d72fbc4` có phải ancestor của HEAD? | CÓ | `git merge-base --is-ancestor` → YES |
| `2f20e6c` có phải ancestor của HEAD? | CÓ | `git merge-base --is-ancestor` → YES |
| `66f5e22` = HEAD? | CÓ | `git rev-parse HEAD` |
| Commit sau E2 có đổi CODE/TEST? | **KHÔNG** | `git diff --name-only 2f20e6c..HEAD` chỉ trả về `docs/reviews/E2-WP-A1-provenance.md` và `docs/tasks/WP-A1-provenance-va-tai-lap.md` |
| E2 đánh giá trạng thái hiện tại hay trạng thái cũ? | **HIỆN TẠI** | `2f20e6c..HEAD` = 2 file, 0 dòng `src/`, 0 dòng `tests/`, 0 dòng `pyproject.lock` |

KHÔNG CÓ CONFLICT. Kết luận E2 áp dụng nguyên vẹn cho HEAD: mọi verdict của E2 về code và test
vẫn đúng vì code và test không dịch chuyển một dòng nào sau khi E2 chạy.

## 3. Inventory 9 finding E2 (nguyên văn severity/verdict)

Nguồn: `docs/reviews/E2-WP-A1-provenance.md`. PRE-S008 KHÔNG có quyền tự hạ cấp finding E2;
cột "Đề xuất PRE-S008" chỉ là IMPLEMENTER PROPOSAL, phải được reviewer E2 xác nhận ở vòng sau.

| ID | Nguyên văn severity | Check bị ảnh hưởng | Đề xuất PRE-S008 | Trạng thái quyền |
|---|---|---|---|---|
| F-E2A1-01 | Mặc định fail-OPEN khi gán nhãn nguồn trong `fetch_all` (**mức: CAO**) | A1-05, A1-07 | APPLIES TO HEAD | BLOCKING — giữ nguyên |
| F-E2A1-02 | `official_eligibility` không kiểm lineage phủ đủ series được dùng (**mức: TRUNG BÌNH-CAO**) | A1-07 | APPLIES TO HEAD | BLOCKING — giữ nguyên |
| F-E2A1-03 | Provenance im lặng suy biến ngoài môi trường editable install (**mức: TRUNG BÌNH**) | A1-01, A1-03, A1-08 | APPLIES TO HEAD | Non-blocking theo E2, giữ nguyên phân loại của E2 |
| F-E2A1-04 | `code_commit` không phân biệt worktree sạch với worktree bẩn (**mức: TRUNG BÌNH**) | A1-03 | APPLIES TO HEAD | Non-blocking theo E2 |
| F-E2A1-05 | `test_a1_06_synthetic_not_official_in_gate2_gate3` không thể FAIL vì lý do nó tuyên bố (**mức: TRUNG BÌNH**) | A1-06 | APPLIES TO HEAD | Non-blocking theo E2 — nhưng cùng LỚP defect đã hạ gục E2 lần một |
| F-E2A1-06 | Lockfile không ghim tzdata của hệ điều hành (**mức: THẤP**) | A1-08, A1-09 | APPLIES TO HEAD | Non-blocking theo E2 |
| F-E2A1-07 | Assertion `oos` trong `test_a1_09` vô hiệu trên dataset đang dùng (**mức: TRUNG BÌNH**) | A1-09 | APPLIES TO HEAD | Non-blocking theo E2 — cùng lớp với F-E2A1-05 |
| F-E2A1-08 | `data_source: "mixed"` không có trong taxonomy tài liệu (**mức: THẤP**) | A1-05 | APPLIES TO HEAD | Non-blocking theo E2 |
| F-E2A1-09 | `run_controls` ghi `official` không tính tới đường dev (**mức: THẤP**) | A1-07 | APPLIES TO HEAD | Non-blocking theo E2 |

Không finding nào được PRE-S008 đề xuất FALSE POSITIVE. Không finding nào bị bỏ.

### 3.1 Hai FAIL và một NOT_TESTED — định danh chính xác

| Vị trí | Check | Nguyên văn evidence E2 |
|---|---|---|
| FAIL #1 | **CHECK-A1-05** | "Đường `synth` đúng; đường `fetch` gán nhãn `binance_rest` cho series KHÔNG có cơ chế nào đóng góp (fail-OPEN)" |
| FAIL #2 | **CHECK-A1-07** | "Bề mặt CLI/env sạch và 20+ đầu vào dị dạng fail-closed, NHƯNG tìm được HAI đường biến dữ liệu không đủ tư cách thành `official`" |
| NOT_TESTED | **CHECK-A1-09** | "Tái lập trong-môi-trường: HAI tiến trình riêng, `PYTHONHASHSEED` khác nhau → metric trùng tuyệt đối… Nửa 'dựng venv sạch từ lockfile': KHÔNG chạy được (proxy chặn cài gói)" |

## 4. Validity matrix A1-01…A1-10 trên HEAD

Cơ sở: `2f20e6c..HEAD` không đổi một dòng `src/`, `tests/` hay `pyproject.lock`. Mọi verdict E2
do đó vẫn mô tả đúng artifact hiện tại.

| CHECK | E2 VERDICT | E2 SHA | HEAD IMPACT | CURRENT VALIDITY | REASON |
|---|---|---|---|---|---|
| A1-01 | PASS | 2f20e6c | Không | STILL VALID | Không có thay đổi CODE/TEST sau E2 |
| A1-02 | PASS | 2f20e6c | Không | STILL VALID | như trên |
| A1-03 | PASS | 2f20e6c | Không | STILL VALID | như trên |
| A1-04 | PASS | 2f20e6c | Không | STILL VALID | như trên |
| A1-05 | **FAIL** | 2f20e6c | Không | STILL VALID | Defect `fetch_all` còn nguyên tại HEAD |
| A1-06 | PASS | 2f20e6c | Không | STILL VALID | như trên |
| A1-07 | **FAIL** | 2f20e6c | Không | STILL VALID | Hai đường fail-open còn nguyên tại HEAD |
| A1-08 | PASS | 2f20e6c | Không | STILL VALID | như trên |
| A1-09 | NOT_TESTED | 2f20e6c | Không (code); **CÓ (môi trường)** | **REQUIRES RE-VERIFICATION** | Blocker được ghi là "proxy chặn cài gói" — PRE-S008 chứng minh điều đó SAI (xem §6) |
| A1-10 | PASS | 2f20e6c | Không | STILL VALID | như trên |

Chỉ A1-09 cần rà lại, và không phải vì code đổi mà vì **tiền đề môi trường đã bị ghi sai**.

## 5. Environmental Satisfiability Matrix — toàn Completion Gate WP-A1

Năng lực môi trường đã đo trực tiếp trong phiên này:

| Năng lực | Kết quả đo | Bằng chứng |
|---|---|---|
| Truy cập package index (PyPI qua proxy) | **CÓ** | `pip download six==1.16.0` → "Successfully downloaded six" |
| Dựng venv sạch + cài từ lockfile | **CÓ** | `python -m venv` + `pip install -r pyproject.lock` → exit 0, 15/15 pin đúng |
| Cài project vào venv sạch | **CÓ** | `pip install --no-build-isolation -e .` → exit 0 |
| Chạy backtest trong venv sạch | **CÓ** | `run_gate1` chạy trọn trong `/tmp/cleanenv` |
| Truy cập Binance REST | **KHÔNG** | `api.binance.com/api/v3/ping` → HTTP 000 |
| Truy cập Binance bulk archive | **KHÔNG** | `data.binance.vision` → HTTP 000 |
| Wall-clock, disk, OS/container | CÓ | dùng bình thường suốt phiên |
| External reviewer (E2) | CÓ | đã thực hiện hai vòng |

| CHECK | REQUIRED EVIDENCE | CAPABILITY NEEDED | CURRENT ENV | SAT STATUS | BLOCKER | SATISFIABLE TRONG PHIÊN? |
|---|---|---|---|---|---|---|
| A1-01 | Nội dung record thật in ra | Chạy pipeline trên dataset bất kỳ | Có | **SAT** | — | Có (E2 đã làm) |
| A1-02 | Record GATE2+GATE3 mang hash khớp manifest thật | Chạy manifest đầy đủ 219+114 | Có | **SAT** | — | Có (E2 đã chạy đầy đủ) |
| A1-03 | `code_commit` == git HEAD; seed tái lập | git + chạy pipeline | Có | **SAT** | — | Có |
| A1-04 | `created_at` có mặt, hash không đổi | Đối chiếu hai commit | Có | **SAT** | — | Có (worktree `d72fbc4`) |
| A1-05 | `source` ∈ 3 giá trị cho TỪNG series; hết chuỗi cố định | Đường `synth`: chạy trực tiếp. Đường `fetch`: kiểm LOGIC gán nhãn | Có (synth); fetch cần stub biên I/O | **SAT** | Dán nhãn dữ liệu Binance THẬT cần mạng → thuộc T-06, không thuộc A1-05 | Có — E2 đã stub `fetch_month_archive`/`fetch_klines` để chứng minh F-E2A1-01 mà không cần mạng |
| A1-06 | synth + không dev-limit → record `official: false` | Chạy CLI thật | Có | **SAT** | — | Có |
| A1-07 | Liệt kê bề mặt CLI/env + test khẳng định không giả mạo được | Đọc mã + probe đối kháng | Có | **SAT** | — | Có |
| A1-08 | Lockfile ghim chính xác; hash khớp record | Đọc file + `importlib.metadata` | Có | **SAT** | — | Có |
| A1-09 | Cài env SẠCH từ lockfile, chạy lại, đối chiếu metric | venv + package index + chạy pipeline | **Có — đã chứng minh** | **SAT** | KHÔNG CÓ (xem §6) | **Có — PRE-S008 đã chạy thử toàn bộ chuỗi** |
| A1-10 | Test suite PASS + metric trước/sau không đổi | Chạy pytest + hai worktree | Có | **SAT** | — | Có |
| A1-11 | Phiên reviewer độc lập E2, lưu `docs/reviews/` | Reviewer riêng | Có | **SAT** | — | Có (đã hai vòng) |

Tổng kết: **SAT 11/11. BLOCKED-ENV 0. BLOCKED-DATA 0. BLOCKED-HUMAN 0. BLOCKED-GOVERNANCE 0.**

Không REQUIRED check nào của WP-A1 bất khả thi trong môi trường hiện tại. Việc `ethdca fetch`
không chạy được là ràng buộc của **T-06**, không phải của Completion Gate WP-A1: gate chỉ yêu cầu
lineage phân loại ĐÚNG, và logic phân loại kiểm được mà không cần mạng.

## 6. A1-09 — điều tra reproducibility satisfiability

Completion Gate FROZEN yêu cầu: "cài môi trường sạch từ lockfile, chạy lại cùng dataset hash +
config hash + manifest hash + seed, đối chiếu kết quả ở mức metric theo BT §20."

Phân rã A–F và kết quả đo trực tiếp:

| Bước | Nội dung | Trạng thái | Bằng chứng |
|---|---|---|---|
| A | Lockfile tồn tại | ĐẠT | `pyproject.lock` |
| B | Exact resolved versions | ĐẠT | 15/15 dòng dùng `==`, khớp `importlib.metadata` |
| C | Clean env cài được từ lockfile | **ĐẠT** | `pip install -r pyproject.lock` trong venv mới → exit 0 |
| D | Clean env chạy lại được | **ĐẠT** | `pip install -e .` + `run_gate1` chạy trọn trong venv |
| E | Output tái lập | **ĐẠT** | So với môi trường hiện tại, `PYTHONHASHSEED=12345`: `CURRENT-ENV == CLEAN-VENV : True`; `dataset_hash` `3ba67072…`, `primary_median` `96.23260701438292`, `final_eth` `56.03896168942767` |
| F | Environment/runtime provenance được ghi | ĐẠT | `python_version`, `dependency_lock_hash`, `code_commit` trong record |

**BLOCKER CHÍNH XÁC: KHÔNG CÓ.**

Đây là một đính chính, không phải một sắc thái. Trong S007 tôi đã ghi vào task file rằng vế
"môi trường sạch" bị chặn vì "proxy chặn cài gói". Câu đó là một GIẢ ĐỊNH CHƯA KIỂM CHỨNG — tôi
suy ra từ việc Binance bị chặn (BLK-001) rồi mở rộng sang PyPI mà không thử. Reviewer E2 kế thừa
câu đó và ghi A1-09 = NOT_TESTED. PRE-S008 thử thật: index truy cập được, chuỗi C→D→E chạy trọn.

Bài học quy trình: một blocker chỉ được ghi sau khi ĐO, không phải sau khi suy luận. Đây đúng là
lớp lỗi mà chính WP-A1 tồn tại để chống — khẳng định không có bằng chứng.

### 6.1 Khiếm khuyết lockfile CÒN LẠI (không chặn A1-09 như đã diễn đạt)

Ba điểm khiến "clean env" chưa phải bit-identical, cần cân nhắc ở S008 hoặc task hạ tầng riêng:

1. Không ghim build backend: `pip install -e .` kéo `setuptools 79.0.1` KHÔNG do lockfile quy định.
2. Không có hash artifact (`--require-hashes`) → không chống được artifact bị thay ở registry.
3. Không ghim `tzdata` hệ điều hành (F-E2A1-06) — `Asia/Ho_Chi_Minh` quyết định biên ngày kế toán.

Ba điểm này KHÔNG làm A1-09 fail theo cách gate đang diễn đạt (đối chiếu ở mức metric), nhưng làm
yếu tuyên bố "tái lập được nhiều năm sau" — đúng mục tiêu của WP-A1.

## 7. PA-1…PA-4 cho A1-09

Vì §6 chứng minh A1-09 KHÔNG bị chặn, ba PA đầu mất lý do tồn tại ở dạng ban đầu. Ghi lại đầy đủ
để chủ dự án thấy vì sao chúng không còn cần thiết.

| PA | Giải quyết blocker nào | Prerequisite | Đổi Completion Gate? | Residual risk | Quota | Critical path | Khuyến nghị |
|---|---|---|---|---|---|---|---|
| PA-1 — Mở network/proxy | Blocker giả định "proxy chặn PyPI" | Không | Không | — | 0 | Không ảnh hưởng | **KHÔNG CẦN** — index đã truy cập được |
| PA-2 — Offline wheelhouse | Cùng blocker giả định | Cần một môi trường có mạng để build wheelhouse (tự nó không độc lập) | Không | Wheelhouse có thể lệch registry | Trung bình | Không | **KHÔNG CẦN** |
| PA-3 — Tách A1-09 thành infrastructure task | Blocker giả định | Change Procedure hợp lệ để đổi gate | **CÓ** — đụng gate FROZEN | Hạ chuẩn gate mà không có lý do thật | Thấp | Kéo dài GATE-A | **KHÔNG DÙNG** — không được hạ REQUIRED check khi check đó thoả được |
| PA-4 — Lockfile remediation thành task hạ tầng riêng | Ba khiếm khuyết ở §6.1 (build backend, artifact hash, tzdata) | Không | Không (gia cố, không hạ) | Nếu bỏ qua: tuyên bố tái lập yếu hơn thực chất cần | Thấp–trung bình | Không chặn S008 | **CÓ CƠ SỞ** — trình chủ dự án quyết: gộp vào S008 hay tách task riêng |

## 8. Official Eligibility Contract — OWNER-RATIFIED

RULE-1…RULE-15 do chủ dự án phê chuẩn, ghi nhận là DECIDED, không trình lại dưới dạng proposal.

Kiểm xung đột với canonical spec:

- **RULE-4** (extra/unexpected series → FAIL CLOSED vô điều kiện): BT §2 định nghĩa dataset đúng
  ba series (indicator ETHUSDT+BTCUSDT 1D, execution ETHUSDT 15m). Không điều khoản nào cho phép
  series thừa. **KHÔNG CÓ CONFLICT.** Ghi chú thực thi: `build_lineage` hiện `glob("*.parquet")`
  nên một file parquet lạ SẼ vào lineage — RULE-4 buộc trạng thái đó thành FAIL.
- **RULE-15** (official=False không buộc abort pipeline): hành vi hiện tại đúng như vậy —
  `run_verdict` vẫn sinh verdict kèm `official: false` và cảnh báo DEV RUN. **KHÔNG CÓ CONFLICT.**
- RULE-1,2,3,5…14: không điều khoản spec nào quy định ngược. **KHÔNG CÓ CONFLICT.**

## 9. REQUIRED_SERIES

    REQUIRED_SERIES_TYPE = STATIC

    CANONICAL_SOURCE     = docs/spec/03_BACKTEST_SPEC_V2_1_5.md §2
                           dòng 16: "Indicator data: Binance Spot ETHUSDT và BTCUSDT, khung 1D."
                           dòng 17: "Execution data: Binance Spot ETHUSDT, khung 15m."

    DERIVATION_FUNCTION  = không có (tập tĩnh)

    INPUTS               = không có

    BIỂU DIỄN TRONG MÃ   = src/eth_dca_os/data/dataset.py::load_dataset, tuple
                           ("ETHUSDT_1d", "BTCUSDT_1d", "ETHUSDT_15m")

Tập này KHÔNG phải hard-code mới nghĩ ra để test PASS: nó đã tồn tại trong `load_dataset` từ trước
WP-A1 và khớp một-đối-một với BT §2. `synth.generate` sinh đúng ba file này; `fetch_all` tải đúng
ba series này. S008 phải THAM CHIẾU tập canonical đó, không được khai một tập thứ hai song song.

## 10. Official Eligibility Contract — bảng

Enforcement point canonical duy nhất: `src/eth_dca_os/data/dataset.py::official_eligibility`
(RULE-14). `pipeline.Prepared` gọi một lần; Gate 1/2/3, controls và verdict dùng chung kết quả.
Điều kiện dev (RULE-11) áp ở tầng gate: `official = prep.official_eligible and <điều kiện dev>`.

| # | CASE | EXPECTED OFFICIAL | REASON CODE | ENFORCEMENT POINT | TEST ID |
|---|---|---|---|---|---|
| 1 | Dataset synthetic (nhãn đúng) | False | `source_not_real:<series>='synthetic'` | `dataset.official_eligibility` | T-EC-01 |
| 2 | Source `unknown` | False | `source_not_real:<series>='unknown'` | `dataset.official_eligibility` | T-EC-02 |
| 3 | Canonical series có `row_count == 0` | False | `empty_series:<series>` | `dataset.official_eligibility` | T-EC-03 |
| 4 | Thiếu REQUIRED series | False | `missing_required_series:<series>` | `dataset.official_eligibility` | T-EC-04 |
| 5 | Có series thừa ngoài REQUIRED_SERIES | False | `unexpected_series:<series>` | `dataset.official_eligibility` | T-EC-05 |
| 6 | Series trùng lặp trong lineage | False | `duplicate_series:<series>` | `dataset.official_eligibility` | T-EC-06 |
| 7 | Lineage khai series mà loader không nạp | False | `unexpected_series:<series>` | `dataset.official_eligibility` | T-EC-07 |
| 8 | Loader nạp series mà lineage không khai | False | `missing_required_series:<series>` | `dataset.official_eligibility` | T-EC-08 |
| 9 | Thiếu `file_hash` | False | `checksum_missing:<series>` | `dataset.verify_lineage` | T-EC-09 |
| 10 | `dataset_hash` không tái lập được | False | `dataset_hash_mismatch` | `dataset.verify_lineage` | T-EC-10 |
| 11 | `file_hash` lệch file trên đĩa (tampered) | False | `file_hash_mismatch:<file>` | `dataset.verify_lineage` | T-EC-11 |
| 12 | 3/3 canonical, nhãn real, checksum khớp | **True** | `verified` | `dataset.official_eligibility` | T-EC-12 (positive control) |
| 13 | Như (12) nhưng `dev_limit != None` | False | `dev_limit_set` | `pipeline.run_gate1/2/3` | T-EC-13 |
| 14 | Lineage dị dạng (không phải dict / `files` không phải list) | False | `lineage_malformed` | `dataset.official_eligibility` | T-EC-14 |
| 15 | Không có lineage | False | `lineage_missing` | `dataset.official_eligibility` | T-EC-15 |
| 16 | Thử ép official qua CLI | False | không tồn tại đường ép | `cli.main` (không có cờ) | T-EC-16 |
| 17 | Thử ép official qua biến môi trường | False | không tồn tại đường ép | toàn `src/` (không đọc `environ`) | T-EC-17 |
| 18 | Lineage phủ 1/3 series | False | `missing_required_series:<series>` | `dataset.official_eligibility` | T-EC-18 |
| 19 | Lineage phủ 2/3 series | False | `missing_required_series:<series>` | `dataset.official_eligibility` | T-EC-19 |
| 20 | Positive control canonical (fixture thật, checksum thật) | **True** | `verified` | `dataset.official_eligibility` | T-EC-20 |

Reason code phải deterministic và phân biệt được nguyên nhân — cấm gộp tất cả về `invalid`.
Các mã `empty_series`, `missing_required_series`, `unexpected_series`, `duplicate_series`,
`checksum_missing` là MỚI so với implementation hiện tại; `source_not_real`, `file_hash_mismatch`,
`dataset_hash_mismatch`, `lineage_missing`, `verified` đã tồn tại và giữ nguyên tên.

Trạng thái: **FROZEN** kể từ artifact này. S008 thực thi đúng bảng này, không tự thêm/bớt case.

## 11. Positive Control — đặc tả

Mục đích: chống PASS giả kiểu "cổng luôn trả False". Nếu không có nó, toàn bộ 19 case fail-closed
vẫn PASS trên một implementation hỏng theo hướng ngược lại.

Đặc tả fixture `verified_real_like`:

1. Sinh dữ liệu bằng `synth.generate` → parquet THẬT trên đĩa, `row_count > 0` cả ba series
   (đã đo trên dataset mẫu: ETHUSDT_1d 1460, BTCUSDT_1d 1460, ETHUSDT_15m 140156).
2. Ghi lineage bằng `build_lineage(raw, SOURCE_BULK_ARCHIVE)` — checksum được TÍNH THẬT từ chính
   file fixture, không chép tay, không hằng số.
3. Đủ REQUIRED_SERIES = 3/3, không series thừa, không trùng lặp.
4. Gọi `official_eligibility` THẬT trên fixture đó.

Cấm tuyệt đối trong positive control: mock/monkeypatch `verify_lineage`, `official_eligibility`,
`load_dataset`; patch loader; hard-code `official=True`; bỏ qua checksum.

Điểm cần nói thẳng về sức mạnh của nó: fixture mang NHÃN nguồn thật trong khi byte là dữ liệu tổng
hợp. Nó chứng minh cổng MỞ ĐƯỢC khi nhãn hợp lệ và checksum khớp — không chứng minh dữ liệu thật
sự của Binance. Phân biệt dữ liệu Binance thật với dữ liệu bị dán nhãn sai nằm ngoài khả năng của
mã (cần đối chiếu `ethdca freeze` hai máy theo DEC-003) và đã được ghi ở `docs/CONVENTIONS.md`.

Khả thi: **FEASIBLE** trong Scope Lock hiện tại, không cần mạng, không cần mock.

## 12. Mutation Matrix — oracle phải bắt được lỗi

PRE-S008 chỉ THIẾT KẾ; không sửa product code để chạy mutation trong phiên read-only này.

| ID | Đột biến gieo vào product code | Kỳ vọng | Test bắt được | Khả thi |
|---|---|---|---|---|
| MUTATION-1 | `unknown` được coi là verified (thêm `SOURCE_UNKNOWN` vào `REAL_SOURCES`) | Suite PHẢI đỏ | T-EC-02, T-EC-15 | Có |
| MUTATION-2 | Bỏ kiểm `row_count`, gắn `binance_rest` cho series rỗng | Suite PHẢI đỏ | T-EC-03 | Có |
| MUTATION-3 | Bỏ kiểm phủ đủ REQUIRED_SERIES | Suite PHẢI đỏ | T-EC-04, T-EC-08, T-EC-18, T-EC-19 | Có |
| MUTATION-4 | Bỏ qua checksum thiếu/lệch (`verify_lineage` luôn trả True) | Suite PHẢI đỏ | T-EC-09, T-EC-10, T-EC-11 | Có |
| MUTATION-5 | Bỏ điều kiện `dev_limit` khỏi phép tính official | Suite PHẢI đỏ | T-EC-13 | Có |
| **MUTATION-6** | `official_eligibility` luôn trả `(False, ...)` | **POSITIVE CONTROL PHẢI ĐỎ** | T-EC-12, T-EC-20 | Có |

MUTATION-6 là điều kiện sống còn: nếu ép eligibility luôn False mà suite vẫn xanh thì positive
control vô giá trị và mọi case fail-closed chỉ đang xác nhận một cổng đóng vĩnh viễn.
Oracle: **VALID theo thiết kế** — T-EC-12/T-EC-20 khẳng định `official is True`, nên eligibility
hằng False làm chúng đỏ ngay. Chỉ được tuyên bố PROVEN sau khi S008 chạy thật.

## 13. Reproducibility Test Floor — bắt buộc cho S008

S008 không được dùng verification yếu hơn những gì đã thực hiện được. Sàn tối thiểu:

| Yêu cầu | Nội dung | Đã chứng minh khả thi? |
|---|---|---|
| A | Ít nhất HAI process độc lập (không phải hai lần gọi trong cùng process) | Có — E2 và PRE-S008 đều làm |
| B | `PYTHONHASHSEED` khác nhau giữa các lần | Có — PRE-S008 dùng `PYTHONHASHSEED=12345` cho lần venv sạch |
| C | Cùng dataset / config / manifest / seed / resolved dependencies | Có |
| D | Dataset có giá trị THỰC, không NaN ở metric được so | Có — E2 dùng dataset có OOS thật (`ae = 99.0577`, 18 tháng) |
| E | So sánh deterministic theo Completion Gate, không dung sai | Có |
| F | Ít nhất một lần chạy trong venv SẠCH dựng từ lockfile | **Có — PRE-S008 đã chạy** |

Ghi chú F-E2A1-07: `assert a["oos"] == b["oos"]` trên dataset kết thúc 2023-12-31 PASS vì `np.nan`
là singleton chứ không vì số liệu. Sàn D loại bỏ chỗ hở này.

## 14. Hash Semantics Matrix

| Hash | WHAT IT COVERS | METADATA INCLUDED? | EXPECTED BEFORE→AFTER | MUST REMAIN IDENTICAL? | WHY |
|---|---|---|---|---|---|
| `dataset_hash` | Danh sách `file_hash` của các parquet | **KHÔNG** — không phủ `source`, `row_count`, timestamp | Identical | **CÓ** | Định danh NỘI DUNG thị trường. Nếu gắn nhãn nguồn làm đổi hash thì mọi run cũ hết so sánh được, và DM §14 mất mốc |
| `strategy_config_hash` | Trường nghiệp vụ của `StrategyConfig` trừ `config_name` | KHÔNG (`created_at` không phải field) | Identical | **CÓ** | Cùng cấu hình nghiệp vụ phải cho cùng hash giữa các run — nền của so sánh Gate 2 |
| `execution_config_hash` | Như trên cho `ExecutionConfig` | KHÔNG | Identical | **CÓ** | Như trên, cho Gate 3 |
| `sensitivity_manifest_hash` | Các `_cfg_row` của manifest thực chạy | KHÔNG | Gate 2/3: từ `null` → giá trị thật (đóng F-009). Nội dung manifest: identical | Nội dung: CÓ | Trước đây gate 2/3 không ghi; nay ghi. Bản thân manifest không đổi |
| `dependency_lock_hash` | sha256 của `pyproject.lock` | Có (là metadata môi trường) | **ĐỔI** — lockfile được sinh lại từ môi trường thật | **KHÔNG** | Đây chính là chỗ metadata môi trường phải phản ánh sự thật; giá trị cũ mô tả môi trường không tồn tại |
| lineage/provenance hash | Không tồn tại | — | — | — | Hiện KHÔNG có hash riêng phủ lineage |
| environment hash | Không tồn tại (chỉ có `python_version` + `dependency_lock_hash` rời) | — | — | — | Thiết kế hiện hành |

### 14.1 "Tại sao S007 thêm provenance mà manifest hash vẫn identical?"

Vì manifest hash **theo thiết kế không phủ provenance**. `_cfg_row` chỉ serialize các field nghiệp
vụ của config cộng `cfg.hash`; `created_at` cố ý không phải dataclass field nên không lọt vào
`asdict()`. Tương tự `dataset_hash` chỉ phủ nội dung parquet, nên gắn nhãn `source` không dịch nó.

Đây là **design hiện hành, không phải defect** — spec không yêu cầu manifest phủ provenance, và
Completion Gate A1-04 còn yêu cầu NGƯỢC LẠI (hash phải không đổi).

### 14.2 Tamper surface phát sinh từ ranh giới đó (finding mới, KHÔNG remediation ở PRE-S008)

`dataset_hash` không phủ `source`, nên sửa nhãn `source` trong `lineage.json` KHÔNG làm đổi
`dataset_hash`. Phòng thủ hiện có là `official_eligibility` verify lại `file_hash` từ đĩa, nên
việc đổi nhãn không giấu được việc **thay dữ liệu**; nhưng nó cho phép **dán nhãn sai** một tập dữ
liệu nguyên vẹn. Trùng với giới hạn đã ghi ở `docs/CONVENTIONS.md`; ghi lại đây thành finding có
số hiệu để không rơi:

**F-PRE008-01 (mức: THẤP–TRUNG BÌNH)** — không có hash nào phủ nhãn `source`, nên `data_source`
trong record không được bảo vệ bởi bất kỳ checksum nào. Đề xuất (chưa thực hiện): thêm một
`lineage_hash` phủ cả `source` + `source_detail`, ghi vào record cạnh `dataset_hash`. Phải đi qua
Change Procedure vì nó thêm trường vào run record.

## 15. E2 Finding Authority

Implementer KHÔNG được tự bác finding của reviewer E2. Phân định trong artifact này:

| Loại | Nội dung |
|---|---|
| **E2 CONFIRMED** | Toàn bộ 9 finding F-E2A1-01…09, hai FAIL (A1-05, A1-07), verdict E2 FAIL, và 7 PASS. PRE-S008 giữ nguyên, không hạ cấp cái nào. |
| **IMPLEMENTER PROPOSAL** | (a) A1-09 chuyển NOT_TESTED → SAT/READY TO VERIFY vì tiền đề "proxy chặn cài gói" được chứng minh sai bằng đo trực tiếp (§6). (b) F-PRE008-01 là finding MỚI do PRE-S008 nêu. (c) Ba khiếm khuyết lockfile ở §6.1. |

Đề xuất (a) làm THAY ĐỔI phân loại một REQUIRED check của E2, nên **phải được reviewer E2 xác nhận
ở vòng sau**. PRE-S008 không tự chuyển A1-09 sang PASS: nó vẫn chưa có evidence chính thức được
reviewer độc lập ghi nhận; điều PRE-S008 chứng minh là check đó **thoả được**, không phải đã thoả.

## 16. Governance Improvement Proposal — CHECK-SAT

**Đề xuất: "Completion Gate Environmental Satisfiability Review".**

Quan sát nền: governance hiện tại cho phép Ready Gate PASS → mở implementation → mãi về sau mới
phát hiện Completion Gate không tạo được evidence canonical trong môi trường. WP-A1 là ca minh
hoạ theo hướng ngược lại và còn khó chịu hơn: một REQUIRED check bị tuyên bố là bị chặn dựa trên
GIẢ ĐỊNH chưa đo, khiến gate đứng yên nhiều phiên trong khi nó vốn thoả được từ đầu.

Nội dung đề xuất:

1. Bổ sung một bước vào Ready Gate: với TỪNG REQUIRED check, phân loại năng lực môi trường cần có
   thành `SAT` / `BLOCKED-ENV` / `BLOCKED-DATA` / `BLOCKED-HUMAN` / `BLOCKED-GOVERNANCE`.
2. Nguyên tắc: không mở implementation task nếu một REQUIRED Completion Check đã biết trước là
   không thể tạo canonical evidence trong môi trường hiện tại — trừ khi chính task định nghĩa
   blocker đó là dependency/external completion condition (như BLK-001 với T-06).
3. Nguyên tắc bổ sung rút ra từ chính ca này: **một blocker chỉ được ghi sau khi ĐO.** Suy luận
   "X bị chặn nên Y cũng bị chặn" không đủ tư cách làm evidence, kể cả khi X đúng là bị chặn.

Đây CHỈ là proposal. PRE-S008 không sửa Constitution/governance engine.

## 17. Unresolved decisions — cần chủ dự án quyết

| # | Quyết định | Ghi chú |
|---|---|---|
| U-1 | Escalation cho S008: `VERIFICATION_DEPTH` (giữ Tier C, xhigh → max) hay mức khác | Reviewer E2 khuyến nghị VERIFICATION_DEPTH; đây là lần thứ HAI E2 bác bỏ nên `ESCALATION_PROTOCOL` yêu cầu phê duyệt tường minh cho vòng sửa thứ ba |
| U-2 | PA-4: gia cố lockfile (build backend, artifact hash, tzdata) gộp vào S008 hay tách task hạ tầng | Không chặn S008 |
| U-3 | F-PRE008-01: có thêm `lineage_hash` phủ `source` không | Thêm trường vào run record → cần Change Procedure |
| U-4 | Xác nhận của reviewer E2 cho việc chuyển A1-09 khỏi NOT_TESTED | Bắt buộc theo §15 |

## 18. Kết luận S008 Readiness theo §17 (luật cứng)

| Tiêu chí | Nội dung | Trạng thái |
|---|---|---|
| A | A1-09 = READY TO VERIFY hoặc có Human Decision hợp lệ | **ĐẠT** — §6 chứng minh chuỗi C→D→E chạy được trọn vẹn |
| B | Cả 2 FAIL trong E2 được định danh chính xác | **ĐẠT** — CHECK-A1-05, CHECK-A1-07 (§3.1) |
| C | Official Eligibility Contract đã đóng | **ĐẠT** — bảng 20 case, FROZEN (§10) |
| D | REQUIRED_SERIES xác định STATIC hay DERIVED | **ĐẠT** — STATIC, BT §2 (§9) |
| E | 9 finding inventory + phân loại; không hạ cấp blocking chưa được reviewer xác nhận | **ĐẠT** — §3, §15; không finding nào bị hạ cấp |
| F | A1-01…A1-10 rà validity trên HEAD | **ĐẠT** — §4 |
| G | Env Sat Matrix không còn REQUIRED check blocked thiếu phương án | **ĐẠT** — SAT 11/11 (§5) |
| H | Positive control khả thi, không mock verifier/loader/eligibility | **ĐẠT** — §11 FEASIBLE |
| I | Mutation-6 có oracle rõ ràng | **ĐẠT theo thiết kế** — §12; PROVEN chỉ sau khi S008 chạy |

**S008 = READY** (readiness để MỞ phiên remediation, không phải WP-A1 DONE).

WP-A1 vẫn **KHÔNG DONE**: A1-05, A1-07, A1-11 = FAIL; A1-09 chưa có evidence chính thức.
GATE-A chưa đóng → T-06 chưa mở.
