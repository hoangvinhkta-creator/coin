# HARDENING BACKLOG

Status:
ACTIVE — khởi lập tại phiên adoption V4.3 (2026-09-01)

Nguồn thẩm quyền:
`governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing

## Quy tắc

- Mục trong backlog này **KHÔNG phải task** và **không sinh ra task**. Không mục nào ở đây
  được cấp task ID.
- Mọi mục BẮT BUỘC có `RE_TRIGGER_CONDITION`. Mục không có re-trigger là mục sẽ bị mất.
- Khi re-trigger kích hoạt, mục được **định tuyến lại** qua Finding Routing (có thể trở
  thành BLOCKING), chứ không tự động trở thành task.
- HARDENING không có nghĩa là "sai" hay "bị bác". Nó có nghĩa là: chưa chứng minh được
  đường vào runtime hiện tại theo `governance/v4/CORE/PRODUCTION_PATH_RULE.md`.

Phân loại `CONFIRMED` / `PROVISIONAL` theo `REVIEW_PROTOCOL.md`: `CONFIRMED` = có bằng
chứng chạy thật trên đường production; `PROVISIONAL` = mới ở mức chẩn đoán/lý thuyết.

---

## H-01 — `F-E2A1-04` — `code_commit` không phân biệt worktree sạch với worktree bẩn

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: TRUNG BÌNH · E2 xếp non-blocking ở cả vòng hai và vòng ba

Vì sao KHÔNG phải BLOCKING: `_get_code_commit` thoả đúng điều mà CHECK-A1-03 (đã FROZEN)
yêu cầu — `code_commit == git rev-parse HEAD`. Hậu quả (mã ghi SHA sạch cho một cây bẩn)
không nằm trong REQUIRED check nào và không ánh xạ vào risk đã đăng ký nào: RSK-006 nói về
ghim phiên bản thư viện, không nói về trạng thái cây làm việc.

    RE_TRIGGER_CONDITION:
    - official run (T-06) sắp chạy trên một máy KHÔNG bảo đảm được `git status --porcelain`
      rỗng tại thời điểm chạy; HOẶC
    - ngữ nghĩa CHECK-A1-03 được siết lại qua COMPLETION GATE CHANGE PROPOSAL; HOẶC
    - một lần tái lập official run thất bại và `code_commit` là nghi phạm.

---

## H-02 — `F-E2A1-06` — Lockfile không ghim `tzdata` của hệ điều hành

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: THẤP

Vì sao KHÔNG phải BLOCKING: có đường vào runtime thật (`Asia/Ho_Chi_Minh` quyết định biên
accounting month, mà WP-A7 vừa khoá ngữ nghĩa vào đó), nhưng chưa có bằng chứng tái lập nào
cho thấy hai phiên bản tzdata cho ra kết quả khác nhau trên dataset của dự án. Bằng chứng
hiện có là suy luận từ mã và lockfile, không phải divergence đo được.

    RE_TRIGGER_CONDITION:
    - official run được tái lập trên máy có phiên bản tzdata khác máy đã ghi record; HOẶC
    - `pyproject.lock` được sinh lại trên một OS/distro khác; HOẶC
    - bất kỳ sai lệch kết quả nào rơi đúng vào biên tháng kế toán.

---

## H-03 — `F-E2A1-09` — `run_controls` ghi `official` không thống nhất với ba gate

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: THẤP · Bằng chứng: reviewer tự chạy `run_controls(..., n_sims=200)`, record
`RANDOM_CONTROL` ghi `official=True` trong khi GATE1/2/3/BASELINE cùng lần chạy đều `false`

Vì sao KHÔNG phải BLOCKING: đây là bất nhất nội bộ giữa các loại record trong cùng một lần
chạy, KHÔNG phải "synthetic được ghi là official". Nó không ánh xạ vào RSK-008 (RSK-008 nói
về run trên dữ liệu tổng hợp): trong kịch bản này lineage là dữ liệu ĐỦ TƯ CÁCH, còn ba gate
ghi `false` vì `dev_limit`. Reviewer E2 — cơ quan có thẩm quyền theo §15 decision pack —
xếp mục này vào nhóm "nên làm, không chặn DONE".

    RE_TRIGGER_CONDITION:
    - `WP-B3` (audit trail / decision log) bắt đầu tiêu thụ trường `official` từ record
      loại control; HOẶC
    - official run T-06 được chạy với `dev_limit` khác `None` ở bất kỳ giai đoạn nào; HOẶC
    - `F-E2A1R3-03` được sửa (mã lý do `dev_limit_set`) — lúc đó bất nhất này trở nên
      nhìn thấy được và nên đóng cùng gói.

---

## H-04 — `F-E2A1R3-02` — `official_eligibility` raise `TypeError` thay vì `lineage_malformed`

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: TRUNG BÌNH-THẤP · Bằng chứng: reviewer chạy thật, `src in REAL_SOURCES` với
`src` là `list`/`dict` raise `TypeError: unhashable type`

Vì sao KHÔNG phải BLOCKING dù chạm contract đã FROZEN: contract §10 case 14 quy định lineage
dị dạng phải cho `(False, 'lineage_malformed')`, nên đây LÀ một sai lệch với contract đóng
băng — phải nói thẳng điều đó. Nhưng hậu quả là **fail-closed bằng cách sập** (traceback),
không phải fail-open: không có đường nào từ lỗi này dẫn tới một record `official=true` sai.
Khác hẳn `F-E2A1R3-03` (case 13), nơi mã ghi một cặp giá trị mâu thuẫn vào file kết quả của
mọi lần chạy dev bình thường, không cần artifact hỏng.

    RE_TRIGGER_CONDITION:
    - một REQUIRED check bất kỳ bắt đầu khẳng định contract case 14; HOẶC
    - `lineage.json` được sinh bởi một writer khác `fetch_all` / `synth.generate`; HOẶC
    - quy trình vận hành T-06 cho phép thao tác tay trên `lineage.json`; HOẶC
    - chủ dự án quyết định đóng nốt sai lệch contract trong cùng gói với `F-E2A1R3-03`.

---

## H-05 — `F-E2A1R3-04` — `data_source` mức dataset hoàn toàn không được kiểm

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: TRUNG BÌNH-THẤP · Bằng chứng: reviewer đặt `lineage["source"]` thành
`'synthetic'`, `'mixed'`, `'hoan-toan-bia'`, `None`, `12345` — cả năm lần
`official_eligible = True` và record ghi đúng giá trị bịa vào `data_source`

Vì sao KHÔNG phải BLOCKING: tổ hợp nguy hiểm (`official: true` cạnh
`data_source: "synthetic"`) chỉ dựng được khi trường roll-up mâu thuẫn với các nhãn
per-file — tức phải sửa tay `lineage.json` hoặc phải có bug ở writer. Không đường sinh nào
của mã hiện tại (`fetch_all`, `synth.generate`) tạo ra tổ hợp đó. Theo
`PRODUCTION_PATH_RULE.md`, counterexample chỉ dựng được bằng sửa tay artifact mặc định là
HARDENING. Cùng LỚP với `F-PRE008-01` (H-06).

Lưu ý ranh giới: phần **taxonomy `mixed` thiếu trong tài liệu** của `F-E2A1-08` KHÔNG nằm ở
đây — nó là BLOCKING qua đường Exit Criteria, xem migration record §5.

    RE_TRIGGER_CONDITION:
    - `lineage.json` được sinh bởi bất kỳ writer nào ngoài `fetch_all` / `synth.generate`;
      HOẶC
    - `data_source` mức dataset được một hạng mục hạ nguồn tiêu thụ để ra quyết định
      (không chỉ để hiển thị); HOẶC
    - `F-PRE008-01` được đóng bằng một hash phủ nhãn `source` — lúc đó trường roll-up phải
      được đưa vào cùng phạm vi bảo vệ.

---

## H-06 — `F-PRE008-01` — Không hash nào phủ nhãn `source`, nên dán nhãn sai bằng tay qua được

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING — ĐÃ CÔNG BỐ**
Mức theo PRE-S008: THẤP–TRUNG BÌNH

Vì sao KHÔNG phải BLOCKING: giới hạn này đã được **công bố tường minh** ở ba nơi —
`docs/CONVENTIONS.md`, Evidence của CHECK-A1-07, và decision pack PRE-S008 — và đã có biện
pháp đối trọng được quyết định: đối chiếu `ethdca freeze` trên hai máy theo `DEC-003`.
Reviewer E2 vòng ba xác nhận nó có thật và cố ý KHÔNG dùng nó để FAIL một gate đã tự công
bố nó nằm ngoài phạm vi.

Ghi để không ai đọc nhầm: kết luận "CHECK-A1-07 PASS" KHÔNG có nghĩa là "không thể giả mạo".

    RE_TRIGGER_CONDITION:
    - biện pháp đối trọng `DEC-003` (đối chiếu hai máy) KHÔNG được thực hiện cho T-06; HOẶC
    - `lineage.json` trở nên ghi được bởi một tiến trình không tin cậy; HOẶC
    - chủ dự án quyết định thêm `lineage_hash` phủ `source` (câu hỏi disposition đã nêu
      trong decision pack) — khi đó H-05 phải được đóng cùng.

---

## H-07 — `F-E2A1R3-07` — `REQUIRED_SERIES` chưa phải nguồn khai báo duy nhất

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: THẤP

Vì sao KHÔNG phải BLOCKING: `synth.generate` và `fetch.fetch_all` vẫn viết cứng bộ series
riêng, nên ràng buộc §9 decision pack ("không khai một tập thứ hai song song") mới thoả một
nửa (loader ↔ eligibility, chưa thoả cho producer). Nhưng hậu quả của phân kỳ là
**fail-closed**: nếu `REQUIRED_SERIES` đổi mà producer không đi theo,
`official_eligibility` sẽ TỪ CHỐI mọi dataset chúng tạo ra. Không có đường fail-open.
Phần "docstring tuyên bố NƠI DUY NHẤT" là một tuyên bố quá mức trong tài liệu mã, không
phải defect hành vi.

    RE_TRIGGER_CONDITION:
    - bất kỳ thay đổi nào tới `REQUIRED_SERIES` (thêm/bớt symbol, interval, hoặc đổi tên
      file); HOẶC
    - `WP-A4` / `T-06` cần một series hoặc khung thời gian khác bộ ba hiện tại; HOẶC
    - một test hoặc tài liệu bắt đầu dựa vào tuyên bố "NƠI DUY NHẤT" của docstring.

---

## H-08 — Khiếm khuyết glob của `validate_evidence.py` / `validate_task_completion.py`

Capability: `CAP-GOVTOOL` · Owner: **CHƯA CÓ** · Phân loại: **OUT_OF_SCOPE → đã có kênh
Owner Decision**

Hai validator quét `TASK_DIR.glob("TASK-*.md")` trong khi task file của dự án theo quy ước
`WP-*.md` và `T-*.md`. Đo được tại phiên adoption:

    validate_evidence.py       -> "EVIDENCE VALIDATION: PASS ... Checked 0 REQUIRED PASS evidence record(s)."
    validate_task_completion.py -> "TASK COMPLETION: PASS ... Checked 0 DONE task(s)."

Theo `governance/v4/CORE/STATE_AUTHORITY.md` § Vacuous Validation, "Checked 0 records"
KHÔNG phải PASS có nghĩa. Hai dòng PASS này hiện không chứng minh điều gì.

Đây KHÔNG phải finding mới: nó đã nằm ở mục "Cần chủ dự án quyết định" #5 của
`PROJECT/PROJECT_PROGRESS.md` (tồn đọng từ S003, follow-up #3 của E2-WP-A7-001). Adoption
V4.3 chỉ ghi lại phép đo và giữ nguyên định tuyến — KHÔNG tạo owner mới, KHÔNG tạo task.

    RE_TRIGGER_CONDITION:
    - bất kỳ task nào chuyển sang DONE và viện dẫn "validators PASS" trong Exit Criteria;
      HOẶC
    - GATE-A hoặc PHASE_RELEASE_GATE được đánh giá; HOẶC
    - chủ dự án phê duyệt một gói governance-tooling cho `CAP-GOVTOOL`.

## H-09 — Danh sách production path bị nhân bản trong `branch_authority_check.sh`

Capability: `CAP-GOVTOOL` · Owner: **CHƯA CÓ** · Phân loại: **HARDENING** · `CONFIRMED`

`governance/scripts/governance/branch_authority_check.sh` khai báo cứng:

    PRODUCTION_PATHS=(src/eth_dca_os webapp pyproject.toml pyproject.lock)

trong khi nguồn sự thật duy nhất là `PROJECT/PRODUCTION_PATHS.md`. Theo
`governance/v4/CORE/STATE_AUTHORITY.md` § Single Source Of Truth, "nhân bản một nguồn sự
thật là khiếm khuyết governance, không phải dự phòng". Hiện hai nơi đang trùng khớp, nên
chưa có hậu quả nghiệp vụ — đó là lý do đây là HARDENING chứ không phải BLOCKING.

KHÔNG sửa trong phiên reconciliation này: đọc danh sách từ file sẽ làm check có nguy cơ trở
thành vacuous ("checked 0 paths") nếu parse hỏng, và rủi ro đó lớn hơn lợi ích ngay lúc này.

    RE_TRIGGER_CONDITION:
    - `PROJECT/PRODUCTION_PATHS.md` thêm/bớt/đổi tên bất kỳ path nào; HOẶC
    - script được dùng trong CI như một gate chặn merge; HOẶC
    - chủ dự án phê duyệt gói governance-tooling cho `CAP-GOVTOOL`.

## H-10 — Golden Baseline chưa tồn tại, nên delivery change budget chưa có mốc đo

Capability: `CAP-GOVTOOL` · Owner: **CHƯA CÓ** · Phân loại: **HARDENING** · `CONFIRMED`

Source pack cung cấp `GOLDEN_BASELINE/README.md`, `BASELINE_SPEC_TEMPLATE.md` và
`golden_baseline_template.py.txt` (đuôi `.txt` để pytest không collect). Repo hiện **chưa**
có Golden Baseline, và `PROJECT/PRODUCTION_PATHS.md` ghi nhận `GOLDEN_BASELINE_SHA` chưa
được đặt.

Hệ quả đã ghi vào CORE tại phiên này: `governance/v4/CORE/DELIVERY_LOOP.md` § II.4 định
nghĩa `GOLDEN_CUMULATIVE_DIFF_MAX` đo từ `GOLDEN_BASELINE_SHA`; chưa có Golden thì tầng
budget thứ hai chưa đo được, và theo `RISK_MODEL.md` **không path nào được giảm Blast
Radius**.

KHÔNG copy template vào repo ở phiên này: đó là tiện ích, không phải bất biến bị thiếu, và
việc chọn Golden case đầu tiên là quyết định nghiệp vụ của chủ dự án
(`END_TO_END_ACCEPTANCE` cần toạ độ thật + con số kỳ vọng thật, xem `CAPABILITY_MODEL.md`
§ II.1–II.2).

    RE_TRIGGER_CONDITION:
    - chủ dự án cung cấp một ca nghiệp vụ thật kèm con số kỳ vọng (thoát
      `PENDING_OWNER_DATA`); HOẶC
    - bất kỳ artifact nào tuyên bố giảm Blast Radius nhờ Golden; HOẶC
    - `FULLY_ENFORCED` được đặt làm mục tiêu (hiện trạng là `POLICY_ADOPTED`).

## H-11 — `LESSONS_LEARNED.md` của source pack không được chép vào repo

Capability: `CAP-GOVTOOL` · Owner: **CHƯA CÓ** · Phân loại: **OUT_OF_SCOPE → reference**

Source pack có `LESSONS_LEARNED.md` (26 KB, 5 nhóm A–F, 30 mục) giải thích **vì sao** mỗi
bất biến tồn tại. Phiên reconciliation này đã khôi phục **các bất biến** vào
`governance/v4/CORE/*` nhưng KHÔNG chép văn bản bài học vào repo.

Lý do: đó là tài liệu tham chiếu/lý do, không phải runtime governance. Chép 26 KB vào repo
chỉ để đạt file parity đi ngược `§ Artifact Budget`. Bất biến mới là thứ ràng buộc hành vi,
và chúng đã được ghi và được validator kiểm (`source_invariants_checked`).

    RE_TRIGGER_CONDITION:
    - một phiên tranh luận về *lý do* một bất biến tồn tại và không giải quyết được bằng
      chính văn bản CORE; HOẶC
    - chủ dự án yêu cầu bản đối chiếu đầy đủ với văn bản gốc.

## H-12 — `PRODUCTION_PATHS.md` khai báo theo FILE, chưa theo CHUỖI dữ liệu

Capability: `CAP-GOVTOOL` · Owner: **CHƯA CÓ** · Phân loại: **HARDENING** · `CONFIRMED`

Source pack yêu cầu mỗi production path được viết thành chuỗi, từng mắt xích có tên
(`governance/v4/CORE/PRODUCTION_PATH_RULE.md` § "A Production Path Is Written As A Chain"):

    INPUT -> PARSER/VALIDATOR -> TRANSFORM -> BUSINESS STATE -> OUTPUT/CONSUMER

kèm `FAILURE CONSEQUENCE` và `REALISTIC SOURCE` cho từng path. Validator gốc của pack
kiểm đúng các trường này.

`PROJECT/PRODUCTION_PATHS.md` hiện khai báo theo **file → vai trò** (13 dòng). Nó đã thoả
bất biến CORE quan trọng nhất — "production path được KHAI BÁO, không được suy luận" — và
đủ dùng cho ba mục đích đang dùng (phân loại finding, đo budget, xác nhận diff = 0). Vì vậy
giữ nguyên làm SoT.

Phần còn thiếu là **ngữ nghĩa**, không phải file: chấm risk theo file thay vì theo đường dữ
liệu chính là điều `GOVERNANCE_V4.md` § II.1 cấm. Một file (`src/eth_dca_os/**`, 26 module)
có thể chứa nhiều đường dữ liệu với Blast Radius khác nhau, và bảng hiện tại không phân biệt
được.

KHÔNG viết lại ở phiên này: phân rã 13 path thành chuỗi kèm hậu quả nghiệp vụ là công việc
khai báo của dự án, không phải delta của source reconciliation, và nó sẽ chạm vào vùng phân
loại của WP-A1.

    RE_TRIGGER_CONDITION:
    - một finding cần phân biệt Blast Radius giữa hai đường dữ liệu trong cùng một file;
      HOẶC
    - bất kỳ artifact nào tuyên bố Effective Risk ở mức path chứ không phải mức file; HOẶC
    - Golden Baseline đầu tiên được dựng (H-10) — khi đó chuỗi là đầu vào bắt buộc.

## H-13 — `F-E2A1R3-01` — `row_count` nằm ngoài mọi checksum và không bao giờ đối chiếu với file

Capability: `CAP-PROV` · Owner: `WP-A1` · Phân loại: **CONFIRMED HARDENING**
Mức theo E2: TRUNG BÌNH · Ngày định tuyến lại: 2026-09-01 (phiên Owner Disposition)

Trạng thái trước: `CONFIRMED BLOCKING` (adoption V4.3 §5.1).
Trạng thái sau: `HARDENING`. Căn cứ: `governance/v4/CORE/PRODUCTION_PATH_RULE.md` +
`DEC-011`. Lập luận đầy đủ ở
`docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md` §3.4.

Bằng chứng KHÔNG bị nghi ngờ: reviewer E2 vòng ba làm rỗng thật `ETHUSDT_15m.parquet`, dựng
lineage trung thực, rồi sửa `row_count: 0 -> 140156`; mọi `file_hash` và `dataset_hash` vẫn
khớp và `official_eligibility` cho `(True,'verified')`. Kiểu chuỗi `"999"` hoặc `True` cũng
qua được.

Vì sao KHÔNG (còn) là BLOCKING: cái thiếu là **đường sinh**, không phải bằng chứng.
Counterexample đòi sửa tay đúng một số nguyên trong `lineage.json`. Không đường sinh nào của
mã hiện tại tạo ra tổ hợp đó — nếu fetch trả rỗng thì writer ghi `row_count=0` trung thực và
`empty_series` bắn đúng. Theo `PRODUCTION_PATH_RULE.md`, counterexample chỉ dựng được bằng
sửa tay artifact mặc định là HARDENING. `DEC-011` (OD-1) loại hostile tampering khỏi phạm vi
V1: người duy nhất sửa được file đó là chủ dự án, tự phá dữ liệu của chính mình.

Cùng LỚP với H-05 (`F-E2A1R3-04`) và H-06 (`F-PRE008-01`), cả hai đã là HARDENING từ trước —
giữ mục này ở BLOCKING là bất nhất nội bộ.

**Nghĩa vụ KHÔNG được đánh rơi khi hạ cấp.** Adoption §5.1 giữ mục này BLOCKING vì một lý do
KHÁC production path: giới hạn `row_count` **chưa được công bố**, trong khi giới hạn nhãn
`source` (H-06) đã công bố ở ba nơi. Lý do đó vẫn đúng và không bị bác. Nó được chuyển
thành nghĩa vụ công bố trong re-trigger dưới đây, không bị xoá. Adoption §5.1 cũng đã xác
định hai disposition ĐỀU hợp lệ: (a) đối chiếu `row_count` với `len(pd.read_parquet(p))`
trong `verify_lineage`; HOẶC (b) công bố giới hạn trong `docs/CONVENTIONS.md` cạnh giới hạn
về `source`. Disposition (b) có diff production path = 0 nên **không tiêu repair cycle**
(`DEC-012`).

    RE_TRIGGER_CONDITION:
    - T-06 sắp chạy mà giới hạn `row_count` VẪN CHƯA được công bố ở `docs/CONVENTIONS.md`
      (nghĩa vụ công bố kế thừa từ phân loại BLOCKING trước đây — re-trigger BẮT BUỘC); HOẶC
    - `lineage.json` được sinh hoặc sửa bởi bất kỳ tiến trình nào ngoài `fetch_all` /
      `synth.generate`; HOẶC
    - quy trình vận hành T-06 cho phép thao tác tay trên `lineage.json`; HOẶC
    - `row_count` được một hạng mục hạ nguồn tiêu thụ để ra quyết định (không chỉ để hiển
      thị); HOẶC
    - H-05 hoặc H-06 được đóng bằng một cơ chế hash mở rộng — khi đó `row_count` phải được
      đưa vào cùng phạm vi bảo vệ.

---

## H-14 — Trường độ phủ trong `lineage.json` nằm ngoài mọi checksum

Capability: `CAP-DATA` · Owner: `WP-A4` · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-01 (S009)

`CHECK-A4-10` đọc `requested_start` / `requested_end` / `expected_count` / `missing_count`
từ `lineage.json`. Bốn trường này do `build_lineage` TÍNH từ chính file trên đĩa, và
`file_hash` khoá bản ghi vào đúng nội dung file đó — nhưng bản thân chúng KHÔNG nằm trong
`dataset_hash` (hash chỉ dẫn xuất từ danh sách `file_hash`). Người vận hành sửa TAY
`lineage.json` để khai một khoảng yêu cầu hẹp khớp với dữ liệu cắt cụt thì cổng độ phủ
không phát hiện được.

Vì sao KHÔNG phải BLOCKING: đây ĐÚNG cùng lớp với H-05, H-06 và H-13 — counterexample chỉ
dựng được bằng **sửa tay artifact**, không có đường sinh nào của mã hiện tại tạo ra tổ hợp
đó (`fetch_all` và `synth.generate` luôn khai trung thực). `PRODUCTION_PATH_RULE.md` xếp
loại này là HARDENING, và `DEC-011` (OD-1) loại hostile tampering khỏi phạm vi V1. Chỉ thị
mở WP-A4 cũng cấm dùng manual lineage tampering làm bằng chứng blocker.

Giới hạn ĐÃ ĐƯỢC CÔNG BỐ tại `docs/CONVENTIONS.md` § "Độ phủ so với khoảng thời gian được
yêu cầu", cạnh giới hạn nhãn `source` (H-06) — nghĩa vụ công bố mà H-13 nêu được thoả ngay
tại nguồn cho các trường mới này.

Kèm theo, cùng lớp: `official_eligibility` ép kiểu `missing_head`/`missing_internal`/
`missing_tail` khi dựng chuỗi lý do `incomplete_coverage`. Một `lineage.json` bị sửa tay để
ba trường đó mang giá trị không phải số sẽ cho traceback thay vì `lineage_malformed` —
ĐÚNG cùng lớp với H-04 (`F-E2A1R3-02`), và cùng disposition: `DEC-011` điểm 9 coi traceback
là "fail visibly" ở dạng thuần tuý nhất, và đường sinh duy nhất là sửa tay artifact. Nếu
H-04 được đóng, ba trường này phải được đóng CÙNG LÚC.

    RE_TRIGGER_CONDITION:
    - H-05, H-06 hoặc H-13 được đóng bằng một cơ chế hash mở rộng — khi đó bốn trường độ
      phủ PHẢI được đưa vào cùng phạm vi bảo vệ, cùng một lần; HOẶC
    - H-04 được đóng bằng cách chuẩn hoá lỗi kiểu thành `lineage_malformed` — khi đó ba
      trường `missing_head`/`missing_internal`/`missing_tail` phải đi cùng; HOẶC
    - `lineage.json` được sinh hoặc sửa bởi bất kỳ tiến trình nào ngoài `fetch_all` /
      `synth.generate`; HOẶC
    - quy trình vận hành T-06 cho phép thao tác tay trên `lineage.json`.

---

## H-15 — Zone TRIGGERED trong lúc dữ liệu INVALID vẫn thành action sau khi dữ liệu phục hồi

Capability: `CAP-ORDER` · Owner: `WP-A6` · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-01 (S009)

Strategy §3 nói INVALID "chặn mọi action Smart và Opportunity **mới**". Engine thi hành
đúng câu đó: trong chu kỳ INVALID không action nào được tạo. Nhưng bước phát hiện trigger
(đánh dấu zone `TRIGGERED`) đọc giá 15m chứ không đọc chất lượng daily, nên zone vẫn được
đánh dấu trong lúc INVALID và được chuyển thành action ở chu kỳ SAU, khi dữ liệu tốt trở
lại.

Bằng chứng: `tests/test_wp_a4_bad_data_semantics.py::test_a4_02_block_is_temporal_not_permanent`
khẳng định chính hành vi này (và cố ý khẳng định nó, vì vế "cổng không đóng vĩnh viễn" là
cần thiết).

Vì sao KHÔNG phải BLOCKING: hành vi hiện tại **thoả** câu chữ §3 và thoả REQUIRED check
`CHECK-A4-02` đã FROZEN. Câu hỏi "một trigger phát hiện trong lúc dữ liệu xấu có được phép
sống sót không" là câu hỏi về **thứ tự xử lý 18 bước**, thuộc `WP-A6` (`CAP-ORDER`), không
thuộc ngữ nghĩa dữ liệu xấu. Không có điều khoản spec nào hiện nói zone TRIGGERED phải bị
huỷ khi dữ liệu INVALID.

    RE_TRIGGER_CONDITION:
    - `WP-A6` chốt thứ tự 18 bước và phải quyết định số phận của zone TRIGGERED trong chu kỳ
      INVALID (re-trigger BẮT BUỘC — không được bỏ qua khi mở WP-A6); HOẶC
    - `WP-D2` xác định đây là khiếm khuyết đặc tả của V2.1.5 cần V2.2 làm rõ; HOẶC
    - official run cho thấy có action được thực thi trên zone trigger trong cửa sổ INVALID
      và con số bị ảnh hưởng đáng kể.

---

## H-16 — `createLadder()` chặn được INVALID chỉ nhờ trùng hợp toán học, không phải kiểm tra tường minh

Capability: `CAP-WEBAPP` · Owner: `WP-C1` (phát hiện) → `T-09A` (nếu chủ dự án muốn vá phòng
thủ) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (WP-C1)

V-03 (nghi vấn NV-3 của T-03): "trạng thái dữ liệu INVALID không chặn tạo action mới như
Strategy §3 yêu cầu" — kiểm bằng ca chạy thật (`webapp/test_v01_v02_v03.js`) cho kết quả
**BÁC BỎ** về hành vi quan sát được: không tạo được ladder nào trong bất kỳ trạng thái INVALID
nào dựng được. Nhưng đọc `createLadder()` (`webapp/app_logic.js:324-335`) xác nhận nó **không
hề kiểm tra `view.score.data_quality`** ở bất kỳ đâu. Lý do chặn thực tế là guard
`!Number.isFinite(sp)` ("Chưa đủ lịch sử để tính ADR30", `sp` từ `view.smartSpacing`/
`oppSpacing`, cần ≥30 ngày lịch sử liên tục — `webapp/engine.js` `smartSpacing`).

`INVALID` (`data_quality`, `webapp/engine.js` `factorScores`) xảy ra khi cả 8 sub-factor đều
NaN, mà `R` (rsi14) chỉ cần >14 ngày và `S7` (return7) chỉ cần ≥7 ngày — nên với engine hiện
tại, `INVALID` chỉ đạt được khi tổng lịch sử <7 ngày, và ở đó `adr30` (cần ≥30 ngày) LUÔN NaN.
Hai điều kiện không giao nhau về mặt toán học trong cách `computeIndicators`/`factorScores`
hiện được viết — đây là lý do hành vi hiện tại AN TOÀN, không phải vì có chủ đích.

Vì sao KHÔNG phải BLOCKING: không có đường production nào cho ra kết quả sai — mọi trạng thái
INVALID dựng được đều bị chặn tạo ladder, đúng yêu cầu Strategy §3. Không risk nào trong
`PROJECT/PROJECT_PROGRESS.md` § Active Risks ánh xạ tới hành vi này (RSK-003 mục (c)/V-03 đã
ghi BÁC BỎ, không phải BLOCKING).

    RE_TRIGGER_CONDITION:
    - `smartSpacing`/`oppSpacing` hoặc `adr30` được đổi để không còn cần đủ 30 ngày liên tục
      (ví dụ thêm giá trị mặc định/fallback khi thiếu dữ liệu) — khi đó guard ADR30 có thể
      không còn tình cờ trùng với vùng INVALID nữa; HOẶC
    - `factorScores`/`SUB_NAMES` được đổi (thêm/bớt sub-factor, đổi ngưỡng `R`/`S7`) làm
      ngưỡng đạt INVALID không còn cố định ở <7 ngày; HOẶC
    - `T-09A` mở để vá V-01/V-02 và chủ dự án muốn thêm luôn một kiểm tra `data_quality`
      tường minh trong `createLadder()` làm phòng thủ chiều sâu (không bắt buộc — hành vi
      hiện tại đã đúng yêu cầu).

---

## Soát lại toàn bộ backlog dưới Owner Product Intent (2026-09-01)

`DEC-011` bổ sung trục `BLOCKING V1` (tiêu chí A–F). Đã soát lại **từng mục** H-01…H-13 theo
A–F (H-14 và H-15 được thêm sau, tại S009, và đã được soát theo cùng tiêu chí ngay khi ghi). Kết quả: **không mục nào chạm A–F**, nên toàn bộ giữ nguyên `HARDENING` /
`OUT_OF_SCOPE` và giữ nguyên `RE_TRIGGER_CONDITION`. Không mục nào bị xoá, không mục nào
được coi là đã đóng.

Product Intent chỉ có thể làm YẾU lập luận blocking, không bao giờ làm mạnh thêm — trừ khi
A–F bị chạm. Hai mục có sắc thái, ghi lại để không phải soát lại từ đầu ở phiên sau:

- **H-02 (`F-E2A1-06`, tzdata)** — mục HARDENING DUY NHẤT chạm được tiêu chí **B** về lý
  thuyết: tzdata quyết định biên accounting month, mà WP-A7 đã khoá ngữ nghĩa vốn Smart vào
  đó, nên lệch biên tháng = lệch ngân sách. Vẫn giữ HARDENING vì hai lẽ ĐỘC LẬP: (1) chưa
  có divergence ĐO ĐƯỢC — bằng chứng hiện là suy luận từ mã và lockfile; (2) `DEC-011` xác
  định V1 chạy trên MỘT máy của chủ dự án, nên "tái lập trên máy có tzdata khác" không phải
  luồng dùng hàng ngày. Product Intent làm mục này NHẸ đi, không nặng lên.
- **H-04 (`F-E2A1R3-02`, `TypeError`)** — Product Intent làm nhẹ đi rõ rệt: điểm 9 của V1
  Acceptance yêu cầu lỗi có thể làm sai quyết định/sai tiền phải **fail visibly**. Một
  traceback là fail visibly ở dạng thuần tuý nhất.

**Ba mục cùng lớp, nên xử lý như MỘT gói:** H-05, H-06, H-13 đều là "sửa tay artifact
`lineage.json`" và đều có cùng biện pháp đối trọng (`DEC-003` — đối chiếu `ethdca freeze`
trên hai máy). Nếu chủ dự án quyết định đóng, đóng cùng nhau; ba lần sửa rời rạc là lãng
phí và dễ để lọt một trường.

**Không mục nào trong backlog này nằm trên đường găng V1.** Ghi tường minh theo §19 chỉ thị
phiên Owner Disposition. Vẫn đúng sau khi thêm H-14 và H-15 tại S009: H-14 cùng lớp
"sửa tay artifact" với H-05/H-06/H-13, H-15 là câu hỏi thứ tự xử lý mà `WP-A6` sẽ phải
trả lời dù có mục này hay không.
