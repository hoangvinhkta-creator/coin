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


**Ghi nhận S018 (2026-09-03) — vế 1 ĐÃ THOẢ, phân loại KHÔNG đổi.** Official run `T-06` chạy
trên worktree có file untracked (`?? data/`, theo chính khai báo của chủ dự án), nên
`git status --porcelain` KHÔNG rỗng tại thời điểm chạy. `code_commit` vì thế ghi một SHA sạch
cho một cây không sạch. Không đổi con số nào của run; cái mất là khả năng tái lập bit-chính-xác.
Phân loại giữ **HARDENING**, chờ Owner disposition (`OD-T06-07`). Biên bản:
`docs/sessions/S018-post-t06-evidence-closure.md` §7.

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

**Ghi chú routing tại `DEC-031` (2026-09-03).** Phát hiện tại S018: `pyproject.lock` chú
thích `# Python: 3.11.15`, trong khi official run `T-06` khai Python `3.11.16`.
`test_a1_08_lockfile_matches_installed_environment` bỏ qua dòng `#` nên không test nào bắt
được sai lệch chú thích này. Theo `governance/v4/CORE/GOVERNANCE_V4.md` § II.8 (Interpreter /
Environment Differences): một version mismatch tự nó là `ENVIRONMENT_REVERIFY_REQUIRED`,
KHÔNG phải BLOCKING trừ khi một invariant thực sự fail. Chưa có bằng chứng semantics bị ảnh
hưởng — `dependency_lock_hash` (sha256 của chính file) vẫn khớp khai báo, tái xác nhận tại
S018/S019. KHÔNG sửa lockfile trong quyết định này. Phân loại **HARDENING** và
`RE_TRIGGER_CONDITION` GIỮ NGUYÊN. Xem `PROJECT/PROJECT_DECISIONS.md` `DEC-031` — disposition
`OD-T06-10`.

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

**Cập nhật 2026-09-03 (E2-WP-A1-004 / `N-02`, xác nhận `DEC-028`).** Vế thứ ba của
`RE_TRIGGER_CONDITION` **ĐÃ KÍCH HOẠT**: `F-E2A1R3-03` được sửa tại S017 (`_official_reason`
áp tại `run_gate1/2/3`), và `run_controls` xác nhận vẫn KHÔNG tính đường dev — vẫn ghi
`official = prep.official_eligible`, `official_reason = prep.official_reason` không phân
biệt `n_sims`. Bất nhất nay **nhìn thấy được** đúng như dự đoán. Owner ghi nhận (`DEC-028`
điểm 6) và giữ nguyên phân loại **HARDENING** — trên official run thật (`dev_limit=None`,
`n_sims=1000`) mọi record vẫn `official=true` nhất quán; bất nhất chỉ hiện trên run dev, nên
không có hậu quả nghiệp vụ trên đường official. KHÔNG mở repair cycle. Đóng mục này khi nào
`WP-B3` bắt đầu tiêu thụ trường `official` của record `RANDOM_CONTROL`, hoặc khi có repair
cycle khác chạm `run_controls`.

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


**Ghi nhận S018 (2026-09-03) — vế 1 ĐÃ THOẢ (chờ Owner xác nhận), phân loại KHÔNG đổi.** Không
có evidence nào trong repository cho thấy phép đối chiếu `ethdca freeze` hai máy theo `DEC-003`
đã được thực hiện cho `T-06`. Vế này KHÔNG điều kiện hoá theo kịch bản copy dữ liệu, nên nó
thoả bất kể official run chạy một máy hay hai máy. Hệ quả: giới hạn nhãn `source` (mục này) và
giới hạn độ phủ — cả hai đã công bố ở `docs/CONVENTIONS.md` và cả hai chỉ đúng MỘT biện pháp
đối trọng này — đứng nguyên không có đối trọng trên chính run đã phát verdict. Hệ quả nghiệp vụ
thấp vì verdict là `DO_NOT_BUILD` (chiều bảo thủ, không dẫn tới xuống tiền), nhưng đây là
quyết định của chủ dự án. Phân loại giữ **HARDENING**, chờ `OD-T06-05`. Biên bản:
`docs/sessions/S018-post-t06-evidence-closure.md` §6 và §7.

**Owner disposition tại `DEC-031` (2026-09-03).** `ACCEPT_AS_IS` cho câu hỏi "biện pháp đối
trọng `DEC-003` (đối chiếu hai máy) có được thực hiện cho `T-06` hay không": Owner xác nhận
đường hai máy là countermeasure cho kịch bản copy dữ liệu/IP bị chặn, KHÔNG phải acceptance
criterion bắt buộc khi fetch và official run cùng một máy (production-realistic Mac
environment của Owner có kết nối Binance trực tiếp). Không finding nào từ S018/S019 invalidate
official execution `T-06`. Phân loại **HARDENING** và `RE_TRIGGER_CONDITION` GIỮ NGUYÊN —
quyết định này không đóng finding, chỉ ghi nhận disposition cho câu hỏi đã nêu. Xem
`PROJECT/PROJECT_DECISIONS.md` `DEC-031` mục H.

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


**Ghi nhận S018 (2026-09-03) — vế 1 (re-trigger BẮT BUỘC) ĐÃ KÍCH HOẠT, phân loại KHÔNG đổi.**
Kiểm trực tiếp `docs/CONVENTIONS.md`: file này công bố giới hạn nhãn `source` (`F-PRE008-01`)
và giới hạn độ phủ (`missing_count`/`expected_count`), nhưng **KHÔNG** công bố giới hạn
`row_count` (rằng `row_count` nằm ngoài mọi checksum và không bao giờ được đối chiếu với file).
Các lần `row_count` xuất hiện trong file đó đều thuộc ngữ cảnh khác (`row_count > 0`,
`empty_series`, `missing_count`). Nghĩa là official run `T-06` **đã chạy khi nghĩa vụ công bố
kế thừa từ phân loại BLOCKING trước đây vẫn chưa được thi hành**.

Disposition (b) — công bố giới hạn trong `docs/CONVENTIONS.md` cạnh giới hạn `source` — đã được
xác định hợp lệ từ Adoption §5.1 và có diff production path = 0, nên **KHÔNG tiêu repair cycle**
(`DEC-012`). Đây là hạng mục sạch nhất để đóng. Phân loại giữ **HARDENING** (agent không tự
phân loại lại), chờ `OD-T06-04`. Biên bản:
`docs/sessions/S018-post-t06-evidence-closure.md` §7.

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

Capability: `CAP-ORDER` · Owner: `WP-A6` · Phân loại: **CONFIRMED HARDENING — quyết định đã
chốt, một vế RE_TRIGGER_CONDITION còn mở**
Ngày ghi nhận: 2026-09-01 (S009) · Cập nhật: 2026-09-03 (S014, WP-A6 DONE)

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

**Quyết định (S014, `WP-A6`, DONE):** **GIỮ NGUYÊN.** Zone TRIGGERED giữ trạng thái qua
chu kỳ INVALID, thành action ở chu kỳ hợp lệ đầu tiên — cùng cơ chế giữ-TRIGGERED của
max_zones (ST §15.1) và cooldown (`docs/CONVENTIONS.md` #6). Căn cứ đo: dataset tổng hợp
7,5 năm với một hàng daily bị xoá (cửa sổ INVALID 31 ngày, ~1,14 % số nến) — **0** zone
trigger trong chu kỳ INVALID ở cả engine hiện tại lẫn biến thể "huỷ trigger khi INVALID";
hai biến thể cho kết quả trùng khớp hoàn toàn (`docs/CONVENTIONS.md` #19). Quyết định đã
qua rà soát độc lập E2 — `docs/reviews/E2-WP-A6-thu-tu-18-buoc.md` mục A.6: reviewer tự đi
tới cùng kết luận trước khi đọc của implementer, verdict CHECK-A6-08 = PASS. Ghi chú V2.2
cho phương án thay thế: `docs/CONVENTIONS.md` D2-A6-3.

    RE_TRIGGER_CONDITION (hai vế đầu ĐÃ ĐÓNG tại S014; vế thứ ba CÒN MỞ):
    - ~~`WP-A6` chốt thứ tự 18 bước và phải quyết định số phận của zone TRIGGERED trong chu
      kỳ INVALID~~ — ĐÃ CHỐT, xem "Quyết định" ở trên.
    - ~~`WP-D2` xác định đây là khiếm khuyết đặc tả của V2.1.5 cần V2.2 làm rõ~~ — đã ghi
      thành ghi chú D2-A6-3 cho WP-D2 (chưa cần WP-D2 tự mở phiên để vế này coi là đóng;
      chỉ đóng thật khi WP-D2 ra quyết định).
    - **CÒN MỞ:** official run (`T-06`) cho thấy có action được thực thi trên zone trigger
      trong cửa sổ INVALID và con số bị ảnh hưởng đáng kể. `tests/wp_a6_impact_tool.py` đã
      đếm sẵn chỉ số `invalid_cycle_triggers_actioned` cho lần official run đầu tiên dùng.
      Vế này không đóng được bằng dữ liệu synthetic (DEC-003) — chỉ đóng được sau `T-06`.

---

## H-16 — Sai số mức ULP còn lại trên dataset CÓ GAP sau khi cửa sổ đã trượt qua

Nguồn:
Batch review CAP-DATA REPAIR CYCLE #1 — `docs/reviews/S010-batch-review-calendar-indicator.md`
§3 / F-S010-01. Ghi 2026-09-01.

Phân loại:
`HARDENING`

Nội dung:
Sau bản sửa `F-S009-01`, trên dataset **có ngày daily thiếu**, bốn cột không trở lại bằng
nhau từng bit so với chuỗi đầy đủ ngay cả khi cửa sổ đã trượt qua hẳn ngày thiếu:

| Cột | max lệch tương đối | Nguyên nhân |
|---|---|---|
| `ma200` | 2,11e-16 | pandas cộng dồn rolling kiểu online; một `NaN` đi qua cửa sổ đổi thứ tự kết hợp phép cộng (~1 ULP của `double`) |
| `ma_ratio` | 3,04e-16 | dẫn xuất từ `ma200` |
| `ma200_slope` | 5,83e-10 (tuyệt đối 7,11e-15) | hiệu hai `ma200`; mẫu số gần 0 làm tỷ lệ lớn |
| `rsi14` | 7,44e-13 | Wilder có bộ nhớ vô hạn; dải sau gap warm-up lại, đuôi suy giảm `(13/14)^k` |

Trên dữ liệu **sạch** lệch bằng 0 tuyệt đối (khoá bởi CASE G, bit-identical).

Vì sao KHÔNG phải BLOCKING: thiếu tiêu chí thứ hai của `REVIEW_PROTOCOL.md`. Để 2e-16 lật
một quyết định thì `ma_ratio` phải nằm cách ngưỡng dưới 1 ULP; counterexample đó không dựng
được từ bốn nguồn canonical của `PRODUCTION_PATHS.md` §3. `PRODUCTION_PATH_RULE.md` xếp
đúng loại này là HARDENING theo định nghĩa, không phải theo nhân nhượng. Chênh 13–16 bậc độ
lớn so với chính `F-S009-01` (14,29% và 295% đổi dấu).

    RE_TRIGGER_CONDITION:
    Khi `T-06` chạy trên dữ liệu Binance THẬT và dataset official chứa ít nhất một ngày
    daily thiếu: đối chiếu `ma200` / `ma_ratio` / `rsi14` quanh mọi ngưỡng quyết định. Nếu
    tồn tại một ngày mà lệch ULP đủ để lật một so sánh ngưỡng, mục này thành BLOCKING và
    quay lại `CAP-DATA`.


**Ghi nhận S018 (2026-09-03) — nửa đầu điều kiện ĐÃ THOẢ, phép kiểm chứng ĐẾN HẠN, chưa chạy
được.** `T-06` đã chạy trên dữ liệu Binance THẬT, nên vế "khi `T-06` chạy trên dữ liệu Binance
THẬT" thoả. Nửa sau — dataset official có chứa ít nhất một ngày daily thiếu hay không — chưa xác
định được: dataset official không nằm trong repository và không có trong checkout canonical.
Phép đối chiếu `ma200`/`ma_ratio`/`rsi14` quanh mọi ngưỡng quyết định vì thế **đang đến hạn mà
chưa thực hiện**. Nhắc lại điều kiện leo cấp đã ghi ở trên: nếu tồn tại một ngày mà lệch ULP đủ
để lật một so sánh ngưỡng thì mục này thành **BLOCKING** và quay lại `CAP-DATA`. Phân loại giữ
nguyên tới khi phép kiểm chứng chạy được, chờ `OD-T06-06`. Biên bản:
`docs/sessions/S018-post-t06-evidence-closure.md` §7.

---

## H-17 — Ngày daily TRÙNG LẶP nay ném `ValueError` thay vì đi qua im lặng

Nguồn:
Batch review CAP-DATA REPAIR CYCLE #1 — `docs/reviews/S010-batch-review-calendar-indicator.md`
§3 / F-S010-02. Ghi 2026-09-01.

Phân loại:
`HARDENING`

Nội dung:
`compute_daily_indicators` nay reindex chuỗi daily về lịch ngày liên tục. Nếu series có hai
hàng cùng một ngày, `reindex` ném
`ValueError: cannot reindex on an axis with duplicate labels`. TRƯỚC bản sửa, trùng lặp đi
qua im lặng và một trong hai hàng được dùng tuỳ thứ tự.

Không dựng được từ nguồn canonical: `data/fetch.py::fetch_series` đã
`drop_duplicates("open_time")`, và `data/synth.py` dựng daily bằng `groupby(freq="1D")`.
Chiều thay đổi là **fail-closed** — ném lỗi thay vì chọn thầm một hàng — nên đúng hướng của
`DEC-011` điểm 9. Điều còn thiếu là chất lượng chẩn đoán, không phải tính đúng đắn.

Không sửa trong chu kỳ #1: sửa nó là thêm ngữ nghĩa khử trùng lặp cho dữ liệu, tức mở rộng
phạm vi ngoài `DEC-016`.

    RE_TRIGGER_CONDITION:
    Khi một nguồn dữ liệu mới có thể sinh hai hàng cùng ngày (REST tail chồng lấn archive,
    nguồn thứ ba, import thủ công), HOẶC khi `ValueError` này thực sự xuất hiện một lần.
    Khi đó thay bằng một lỗi có chẩn đoán rõ ràng, hoặc một quy tắc khử trùng lặp được ghi
    ở `docs/CONVENTIONS.md`.

---

## H-18 — `createLadder()` chặn được INVALID chỉ nhờ trùng hợp toán học, không phải kiểm tra tường minh

_Ghi chú reconciliation (WP-C1 web stream integration, 2026-09-02): finding này được WP-C1
ghi ban đầu với ID `H-16` trên nhánh `claude/wp-c1-web-skeleton-b3oieq`, tách từ `main` tại
`cb75f9d` — trước khi `H-16`/`H-17` (DATA, CAP-DATA REPAIR CYCLE #1) được ghi trên `main`.
Khi hợp nhất, `H-16`/`H-17` DATA trên `main` là canonical và được giữ nguyên; finding WEB này
đổi số thành `H-18` (next free ID) để không đụng độ. Đây là RENUMBER do trùng ID giữa hai
nhánh song song — không phải finding mới, không đổi ngữ nghĩa nội dung._

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

## H-19 — `monthKey()` dùng giờ địa phương của máy, không dùng `accounting_timezone` đã khai

Capability: `CAP-WEBAPP` · Owner: `T-09A` (ghi nhận tại batch review) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09A batch review, `docs/reviews/T-09A-batch-review.md` §4 `F-T09A-01`)

`monthKey()` (`webapp/app_logic.js`) tính khoá tháng bằng `getFullYear()`/`getMonth()` — giờ
địa phương của máy đang chạy — trong khi `config.accounting_timezone = "Asia/Ho_Chi_Minh"`
được khai trong seed và không được dùng ở bất kỳ đâu trong app. Bản vá T-09A mở rộng vùng ảnh
hưởng của hàm này: nhánh suy luận của `ladderMonth()` gọi `monthKey(new Date(L.created))` để
đoán tháng sở hữu của ladder tạo TRƯỚC bản vá.

Vì sao KHÔNG phải BLOCKING: ladder tạo từ bản vá trở đi luôn mang `L.month` tường minh nên
nhánh suy luận không chạy; mọi ladder rơi vào nhánh suy luận đều được liệt kê tên trên banner
"THÁNG SỞ HỮU SUY LUẬN" (fail visibly, `DEC-011` điểm 9); và `DEC-011` OD-1 xác định V1 chạy
trên MỘT máy của chủ dự án, nên không dựng được counterexample từ nguồn canonical nào của
`PRODUCTION_PATHS.md` §3. Cùng lớp với `H-02` (tzdata quyết định biên accounting month).

    RE_TRIGGER_CONDITION:
    - app được mở trên máy hoặc múi giờ khác `Asia/Ho_Chi_Minh`; HOẶC
    - banner "THÁNG SỞ HỮU SUY LUẬN" bật lên trên state thật của chủ dự án; HOẶC
    - `WP-C2` / `T-09B` chốt lại ngữ nghĩa biên accounting month cho app.

---

## H-20 — Đường mua TRỰC TIẾP (không gắn zone) không bị giới hạn theo unlock

Capability: `CAP-WEBAPP` · Owner: `T-09A` (ghi nhận tại batch review) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09A batch review, `F-T09A-02`)

`addBuy()` nhánh không gắn zone trừ thẳng `pool.a → pool.d` mà không tham chiếu unlock. Sau
bản vá V-02, đây là đường duy nhất còn lại để vốn Smart chưa unlock chuyển sang DEPLOYED.

Vì sao KHÔNG phải BLOCKING — và vì sao chặn nó sẽ là lỗi TỆ HƠN: đường này **ghi nhận một
giao dịch đã xảy ra ngoài đời**. Chặn nó theo unlock sẽ làm mất bản ghi giao dịch thật, chạm
thẳng tiêu chí **C** của `DEC-011` ("mất hoặc làm hỏng lịch sử giao dịch thực tế") — nặng hơn
hẳn hệ quả nó gây ra. Strategy §12 nói về **reserve**, không về ghi nhận.

    RE_TRIGGER_CONDITION:
    - `WP-C2` biến app từ GHI NHẬN sang ĐẶT LỆNH (execution state machine); HOẶC
    - chủ dự án yêu cầu đường mua trực tiếp cũng bị chặn theo unlock, kèm một lối thoát tường
      minh để vẫn ghi được giao dịch đã xảy ra.

---

## H-21 — Lệnh đo budget ở `PRODUCTION_PATHS.md` §1 nuốt cả file test mà §2 loại trừ

Capability: `CAP-GOVTOOL` · Owner: **chưa có** (cùng khe với `H-08`, `H-12`) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09A batch review, `F-T09A-04`)

`PRODUCTION_PATHS.md` §2 loại trừ tường minh `webapp/test_app.js`, `webapp/test_zone.js` khỏi
production path, nhưng lệnh đo budget chuẩn ở §1 dùng glob `-- ... webapp ...` nên đếm cả file
test. Đo được ở T-09A: **590 insertion** (glob) so với **88 insertion** (theo khai báo) — lệch
bảy lần.

`GOVERNANCE_V4.md` §II.6 yêu cầu nguồn cao hơn thắng **và** phải nêu finding reconciliation
khi mâu thuẫn nằm trong CÙNG một artifact. Bảng khai báo (§1 + §2) thắng lệnh tiện dụng, nên
T-09A báo cáo con số theo khai báo và ghi cả hai. Đây là `H-12` biểu hiện ở dạng đo được.

Không BLOCKING: hệ quả là phép đo budget bị thổi phồng — chặt hơn chứ không lỏng hơn; không
đường production nào cho ra kết quả sai.

    RE_TRIGGER_CONDITION:
    - một phiên bất kỳ dùng con số glob làm căn cứ tuyên bố `CHANGE_BUDGET_EXCEEDED`; HOẶC
    - `H-12` được chủ dự án mở để khai lại production path theo CHUỖI dữ liệu; HOẶC
    - `webapp/` có thêm file production mới khiến hai phép đo lệch tiếp.

---

## H-22 — `task_registry_snapshot.sh` bỏ sót trạng thái `IMPLEMENTED` và `VERIFYING` của chính lifecycle canonical

Capability: `CAP-GOVTOOL` · Owner: **chưa có** (cùng khe với `H-08`, `H-09`, `H-21`) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09A batch review, `F-T09A-05`)

`governance/scripts/governance/task_registry_snapshot.sh` lọc dòng roadmap bằng danh sách
trạng thái `DONE|PLANNED|READY|BLOCKED|IN_PROGRESS|DEFERRED|CANCELLED|NOT_PLANNED`. Thiếu
**`IMPLEMENTED`** và **`VERIFYING`** — hai trạng thái nằm ngay trong lifecycle canonical mà
`AGENTS.md` §4 và `CLAUDE.md` khai (`NOT_PLANNED → PLANNED → READY → IN_PROGRESS →
IMPLEMENTED → VERIFYING → DONE`). Task ở hai trạng thái đó **biến mất im lặng** khỏi ảnh chụp
registry.

Đo được: `T-03` đang `VERIFYING` từ 2026-09-02 và **đã** vắng mặt trong ảnh chụp TRƯỚC khi
T-09A đụng vào bất cứ thứ gì — khiếm khuyết này có trước phiên T-09A. Khi T-09A chuyển
`READY → IMPLEMENTED`, `T-09A` cũng biến mất, làm `count_roadmap_task_ids` **giảm** 28 → 27
trong khi tập ID thật không đổi.

Vì sao nguy hiểm hơn vẻ ngoài: đây đúng là công cụ mà `CAPABILITY_MODEL.md` §II.9 chỉ định để
đo chống-sinh-sôi ("measured, not asserted"). Một công cụ đếm thiếu có thể (a) giấu một ID
thật sự mới nếu nó được thêm ở trạng thái `IMPLEMENTED`/`VERIFYING`, hoặc (b) làm một phiên
trung thực trông như vừa xoá task. `STATE_AUTHORITY.md` § Vacuous Validation cấm coi một phép
đo không nhìn thấy hết tập là PASS có ý nghĩa.

Vì sao KHÔNG phải BLOCKING: không có đường production nào cho ra kết quả sai — đây là tầng
tooling governance, cùng lớp với `H-08` và `H-09`, và `CAP-GOVTOOL` vẫn đang
`OWNER_ASSIGNMENT_REQUIRED`. T-09A KHÔNG tự sửa script (ngoài Expected Touch Area, và sửa nó
là kéo việc ngoài Vertical Slice lên đường găng — ngưỡng **D** của Absorption Limit). Phiên
T-09A thay vào đó ĐO LẠI BẰNG TAY với danh sách trạng thái đầy đủ và báo cáo cả hai con số.

    RE_TRIGGER_CONDITION:
    - chủ dự án giao owner cho `CAP-GOVTOOL` (khi đó gom cùng `H-08`, `H-09`, `H-21` thành một
      gói — ba lần sửa rời rạc là lãng phí); HOẶC
    - một phiên bất kỳ dùng `count_roadmap_task_ids` làm bằng chứng chống-sinh-sôi mà không đo
      lại bằng tay; HOẶC
    - lifecycle canonical được bổ sung thêm trạng thái mới.

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

Vẫn đúng sau khi thêm **H-16** và **H-17** tại S010 (CAP-DATA REPAIR CYCLE #1): cả hai đều
chỉ biểu hiện trên dataset có ngày daily thiếu, cả hai đều đã được soát theo A–F của
`DEC-011` ngay khi ghi, và không mục nào chạm A–F. H-16 thiếu đường sinh cho hệ quả (lệch
ULP không lật được ngưỡng nào dựng được từ nguồn canonical); H-17 đã là fail-closed. Không
mục nào bị xoá và không mục nào được coi là đã đóng.

Một finding thứ ba của cùng batch review — **F-S010-03**, lệch parity JS/Python — KHÔNG nằm
trong backlog này vì nó có owner: `OUT_OF_SCOPE` → `CAP-WEBAPP` / `WP-C4`, dưới rủi ro đã
đăng ký `RSK-002`. Ghi ở đây một dòng để người đọc backlog không tưởng rằng nó bị bỏ quên.

**Cập nhật 2026-09-02 (T-09A batch review).** Bốn mục mới **H-19**, **H-20**, **H-21**, **H-22** đã được
soát theo A–F của `DEC-011` ngay khi ghi; không mục nào chạm A–F, không mục nào nằm trên đường
găng V1. `H-18` **giữ nguyên DEFERRED**: ba điều kiện re-trigger của nó đều KHÔNG xảy ra —
`webapp/engine.js` 0 dòng đổi (nên `smartSpacing`/`adr30`/`factorScores`/`SUB_NAMES` không đổi)
và chủ dự án không yêu cầu thêm kiểm tra `data_quality` tường minh.

Một finding thứ tư của batch review T-09A — **F-T09A-03** (app chỉ áp SMART_UNLOCK hiện hành;
thiếu HWM §6, hysteresis §5, daily limit §11) — KHÔNG nằm trong backlog này vì nó có owner:
`OUT_OF_SCOPE` → `CAP-WEBAPP` / `WP-C4`, cùng đường với `F-S010-03`, dưới `RSK-002`. Lệch theo
chiều CHẶT HƠN spec (fail closed), đã khai ở khối `DEFERRED_BY_MINIMAL_FIX` của
`docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`.

---

## H-23 — Cross-device / cross-browser / lost-identity recovery cho `T-09B` (Firebase Anonymous Auth) — OUT OF SCOPE V1

Capability: `CAP-WEBAPP` · Owner: `T-09B` (`WP-C1` lineage) · Phân loại: **OWNER SCOPE DECISION,
OUT OF SCOPE V1** (không phải defect)
Ngày ghi nhận: 2026-09-02 (`DEC-020` phát hiện khe kỹ thuật; `DEC-021` chốt phạm vi V1)

Firebase Anonymous Auth (đã APPROVED cho `T-09B` tại `DEC-020`) lưu danh tính trong `IndexedDB`
của một browser profile. Cửa sổ riêng tư, đổi máy, đổi trình duyệt đều sinh một Anonymous UID
mới; nếu Firestore Security Rules khoá cứng vào một owner UID cố định (đúng thiết kế đã duyệt),
UID mới bị từ chối đọc/ghi dữ liệu đã có. Đây là bằng chứng kỹ thuật thật, ghi đầy đủ tại
`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` § OD-C và `DEC-020`.

`DEC-021` (Personal Tool Simplification Principle + `OD-C = R2`) chốt: đây KHÔNG phải V1 critical
acceptance requirement. Chủ dự án chấp nhận giới hạn này để giữ Anonymous Auth thuần — không
thêm email/password, Google Sign-In, account system nào chỉ để đóng edge case này.

Vì sao KHÔNG BLOCKING theo `PRODUCTION_PATH_RULE.md` và Critical Product Question của `DEC-021`:
mất khả năng auto-recover trên máy mới KHÔNG làm sai tiền, KHÔNG làm sai thuật toán, KHÔNG làm
mất dữ liệu đã bền trên Firestore (dữ liệu vẫn còn — chỉ không đọc được từ thiết bị chưa được
công nhận), và có lối thoát thủ công (export/import JSON, capability giữ nguyên qua `OD-A`).
Không thoả điều nào trong A–F của `DEC-011`/`DEC-021`.

Ràng buộc vẫn giữ (KHÔNG bị hạ bởi quyết định này): khi rules từ chối một UID lạ, app PHẢI hiện
rõ đây là "không nhận diện được thiết bị/trình duyệt này" — KHÔNG được im lặng hiện state rỗng
như thể đó là sổ hợp lệ của một owner mới. Đây thuộc `CHECK-T09B-11` (Firebase read/auth failure
visible) đã FINALIZED, không phải một REQUIRED check mới.

    RE_TRIGGER_CONDITION:
    - có người thứ hai dùng công cụ, hoặc công cụ được phát hành cho người khác (điều kiện
      `DEC-011`/`DEC-019`/`DEC-021` đều dùng chung); HOẶC
    - chủ dự án tự yêu cầu lại cross-device recovery sau khi trải nghiệm thực tế việc đổi máy;
      HOẶC
    - Firebase thay đổi cách Anonymous Auth persist khiến bằng chứng ở `DEC-020` không còn đúng.

---

## H-24 — Zone Opportunity TRIGGERED/ACTION_PENDING không chịu hysteresis suspension

Capability: `CAP-ENGINE` (`ladders.py`/lifecycle) · Owner: chưa có (ngoài Scope Lock `WP-A6`,
`WP-A3` đã DONE/FROZEN) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-03 (S014, phát hiện bởi rà soát độc lập E2 của `WP-A6`, finding R-01)

Với thứ tự 18 bước đúng chữ BT §19 (bước 13 trigger/confirm trước bước 18 hysteresis
suspend), một Opportunity zone có thể **confirm đúng tại nến score tụt xuống ≤ 62** (ngưỡng
suspend hysteresis) và được thực thi trong khi hysteresis đã chuyển SUSPENDED — vì bước 18b
chỉ suspend zone đang `ACTIVE`, không đụng zone đã `TRIGGERED`/`ACTION_PENDING`. Cùng cơ chế
áp cho zone `TRIGGERED` bị giữ nhiều nến bởi cooldown/max_zones/INVALID (`docs/CONVENTIONS.md`
#6, #19): zone đó cũng thoát suspension và có thể thành action nhiều nến sau khi hysteresis
đã tắt.

Bằng chứng: `docs/reviews/E2-WP-A6-thu-tu-18-buoc.md` mục A.5.2 (kịch bản SC5) — engine hiện
tại tạo purchase `OPPORTUNITY_ZONE_1` lúc hysteresis đang SUSPENDED; engine baseline (trước
WP-A6) không có purchase đó ở cùng kịch bản. Đo trên dataset synth 7,5 năm: **0 lần xảy ra**
(mục A.5.6, trùng bit với biến thể đưa bước 18b về vị trí cũ) — cơ chế "zone đã trigger
không bị suspend" có TỪ TRƯỚC WP-A6 (khối hysteresis cũ cũng chỉ xét `ACTIVE`); WP-A6 chỉ mở
rộng cửa sổ xảy ra (thêm ca confirm cùng nến với suspend) bằng cách đặt đúng chữ thứ tự §19.

Vì sao KHÔNG BLOCKING: Strategy §5 chỉ nói "SUSPEND trạng thái Opportunity" và "Suspended
zone giữ reserve tối đa 7 ngày" — không có điều khoản nào nói zone đã trigger phải bị
suspend/huỷ theo. Hành vi hiện tại đúng chữ thứ tự BT §19 (đã qua E2, `CHECK-A6-08` PASS).
Tác động đo được trên dataset production-realistic hiện có = 0.

    RE_TRIGGER_CONDITION:
    - `WP-D2` xác định đây là khiếm khuyết đặc tả V2.1.5 cần V2.2 làm rõ (ghi chú
      `D2-A6-5` tại `docs/CONVENTIONS.md`); HOẶC
    - official run (`T-06`) cho thấy trường hợp này xảy ra và ảnh hưởng đáng kể tới kết quả;
      HOẶC
    - một task chạm `ladders.py`/lifecycle Opportunity (ngoài Scope Lock `WP-A6`) nhận việc
      này qua Capability Model (không tự hấp thụ, cần Owner routing).

---

## H-25 — Crash zone "hit" ở nến kết thúc Recovery vẫn bị huỷ, trái chữ "nếu vẫn chưa hit" (ST §18.3)

Capability: `CAP-ENGINE` (`ladders.py`/lifecycle) · Owner: chưa có (ngoài Scope Lock `WP-A6`,
`WP-A3` đã DONE/FROZEN) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-03 (S014, phát hiện bởi rà soát độc lập E2 của `WP-A6`, finding R-02)

Strategy §18.3: "Sau 72h Recovery nếu vẫn **chưa hit** thì CANCEL crash zone chưa hit + release
reserve." Với thứ tự đúng chữ BT §19 (bước 13 trigger trước bước 18 xử lý cuối-Recovery), một
Crash zone có thể bị xuyên (`TRIGGERED`, rồi `ACTION_PENDING`) **ở chính nến** Recovery kết
thúc (chuyển RECOVERY → NORMAL) trước khi `cancel_open_zones` (bước 18c) chạy — và bị huỷ dù
đã "hit" trong cùng nến đó, trái nghĩa đen "nếu vẫn chưa hit". Hệ quả phụ:
`counters["triggered_actions"]` (dùng cho báo cáo BT §16) đếm luôn action đã bị huỷ cùng nến,
làm bộ đếm cao hơn số action thật sự tồn tại.

Bằng chứng: `docs/reviews/E2-WP-A6-thu-tu-18-buoc.md` mục A.5.2 (kịch bản SC6) — zone Crash
`C2` đi qua `TRIGGERED → ACTION_PENDING → CANCELLED` trong cùng nến; `triggered_actions` = 6
so với 5 ở baseline (baseline huỷ zone TRƯỚC khi nó kịp trigger, nên never "hit"). ETH không
đổi so với baseline ở kịch bản này. Trên dataset synth 7,5 năm: ca này **không xảy ra** (mục
A.5.6, biến thể đưa bước 18c về vị trí cũ trùng bit hoàn toàn với engine hiện tại). Cùng mẫu
áp dụng cho expiry Opportunity 90 ngày (bước 18d).

Vì sao KHÔNG BLOCKING: BT §19 đặt trigger (bước 13) trước xử lý cuối-chu-kỳ (bước 18) một
cách tường minh — thứ tự hiện tại đúng chữ đó (đã qua E2, `CHECK-A6-08` PASS). Mâu thuẫn là
giữa hai điều khoản spec khác nhau (BT §19 vs ST §18.3), không phải một defect implementation.
Tác động đo được trên dataset production-realistic hiện có = 0 ETH; chỉ bộ đếm chẩn đoán bị
lệch.

    RE_TRIGGER_CONDITION:
    - `WP-D2` xác định đây là mâu thuẫn spec cần V2.2 giải quyết — chọn zone hit trong nến
      expiry được thực thi hay bị huỷ (ghi chú `D2-A6-6` tại `docs/CONVENTIONS.md`); nếu
      Owner chọn giữ "huỷ", cân nhắc đổi `counters["triggered_actions"]` để không đếm action
      bị huỷ cùng nến; HOẶC
    - official run (`T-06`) cho thấy trường hợp này xảy ra và ảnh hưởng đáng kể tới kết quả
      hoặc tới số liệu báo cáo BT §16; HOẶC
    - một task chạm `ladders.py`/lifecycle Crash (ngoài Scope Lock `WP-A6`) nhận việc này qua
      Capability Model (không tự hấp thụ, cần Owner routing).

---

## H-26 — `gates.py` trả cờ `pass` kiểu `numpy.bool` — cùng họ `F-S015-01`, hiện chưa hoạt động

Capability: `CAP-VERDICT` (`gates.py` → `verdict.py`) · Owner: chưa gán (ứng viên tự nhiên là
`WP-B1`, đang sở hữu đường verdict) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-03 (S016 — quan sát ngoài frozen slice của `DEC-026`, không sửa trong
lát cắt)

`evaluate_gate1`/`evaluate_oos` dựng cờ `pass` từ phép so trên giá trị đầu vào. Trong pipeline
thật, các giá trị đó là `numpy.float64` (AE tính từ tổng ETH), nên `pass` ra `numpy.bool` chứ
không phải `bool` thuần Python:

    evaluate_oos({'ae': np.float64(105.0), ...})['pass']
      -> type = numpy.bool ;  x is True  ->  False

Đây **cùng một họ khiếm khuyết** với `F-S015-01` (đã đóng tại lát cắt `DEC-026` cho
`failure_signals.py`).

Vì sao KHÔNG BLOCKING: người tiêu thụ hiện tại đọc cờ này bằng **truthiness**, không bằng
phép so danh tính — `verdict.py:14` dùng `if not gate1["pass"] or not oos["pass"]`, và
`not np.True_` cho `False` đúng như mong đợi. Không có hậu quả nghiệp vụ nào ở hiện trạng,
nên theo `PRODUCTION_PATH_RULE.md` mặc định là HARDENING chứ không phải BLOCKING.

Vì sao vẫn phải ghi: khiếm khuyết là **tiềm ẩn, không phải không tồn tại**. Nó trở thành lỗi
thật ngay khi một người tiêu thụ chuyển sang `is True` / `is False` — đúng con đường mà
`F-S015-01` đã đi qua một lần ở `failure_signals.py`, và lần đó hậu quả là verdict có thể ra
`BUILD` khi một Failure Signal đang TRUE.

    RE_TRIGGER_CONDITION:
    - bất kỳ mã nào bắt đầu so cờ `pass` của gate bằng `is True`/`is False` thay vì
      truthiness; HOẶC
    - `WP-B1` đầy đủ mở đường verdict (B1.1/B1.5) — khi đó chuẩn hoá kiểu ở `gates.py` là
      việc rẻ và cùng phạm vi, nên đóng luôn; HOẶC
    - cờ `pass` được tuần tự hoá ra artifact và bị đọc lại bởi một hệ khác (JSON hoá
      `numpy.bool` qua `default=str` cho chuỗi `"True"`/`"False"` — đúng dấu vết đã giúp
      phát hiện `F-S015-01`).

---

## H-27 — `N-01` — `code_commit` có thể phân giải SHA của một git repo LẠ khi chạy từ bản sao mã trần nằm trong repo khác

Capability: `CAP-PROV` (`WP-A1`, đã DONE) · Owner: chưa gán · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-03 (`docs/reviews/E2-WP-A1-CHECK-A1-11-round4.md`, `N-01`; xác nhận
`DEC-028` điểm 6)

`reporting._get_code_commit()` chạy `git rev-parse HEAD` với `cwd=_REPO_ROOT`. Nếu cây mã dự
án được COPY (không kèm `.git` riêng) vào bên trong một git repo KHÁC, `git` đi ngược lên
tìm `.git` gần nhất và trả về SHA của repo LẠ đó, không phải SHA của dự án. Reviewer tái lập
được: `code_commit` = SHA của repo bao ngoài, `provenance_resolved = True`, official run
ĐƯỢC GHI với provenance sai.

Vì sao KHÔNG BLOCKING: kịch bản chỉ dựng được khi vận hành viên chạy official run từ một bản
sao mã trần đặt bên trong một git repo khác — đã vi phạm ràng buộc vận hành mà `DEC-027`/
`DEC-028` xác lập (official run phải chạy từ **canonical git checkout** của chính dự án). Từ
đúng nguồn hợp lệ đó, `code_commit` giải đúng (đối chứng dương `R8` trong báo cáo E2). Hậu
quả cũng KHÁC `'unknown'` im lặng: SHA sai vẫn phát hiện được về sau bằng đối chiếu
`git log`/branch của dự án — không mất khả năng chứng minh hoàn toàn.

    RE_TRIGGER_CONDITION:
    - quy trình vận hành `T-06` KHÔNG kiểm được rằng máy chạy official run là một git
      checkout của CHÍNH repo dự án; HOẶC
    - official run được chạy từ artifact đóng gói (wheel/sdist/container) thay vì checkout;
      HOẶC
    - `WP-B3` (audit trail) bắt đầu dùng `code_commit` làm khoá tra cứu mà không đối chiếu
      thêm với `git log` của dự án.

    Sửa tối thiểu nếu Owner muốn đóng: đối chiếu `git rev-parse --show-toplevel` (hoặc
    `git remote get-url origin`) với `_REPO_ROOT`/tên repo dự án; lệch thì coi `code_commit`
    là KHÔNG phân giải được. Ước lượng ~3 dòng trong `reporting.py`.


**Ghi nhận S018 (2026-09-03) — vế 1 ĐÃ THOẢ, phân loại KHÔNG đổi.** Không tồn tại quy trình vận
hành `T-06` dạng văn bản nào trong repository (chính `H-28` vế 2 xác nhận điều đó chưa được
viết). Không có văn bản thì không thể đã kiểm được rằng máy chạy official run là một git
checkout của CHÍNH repo dự án. Giảm nhẹ, kiểm chứng được tại S018: run record khai
`provenance_resolved=true`, và `code_commit` khai (`5228130…`) khớp đúng HEAD canonical thật của
repo này — nên trên thực tế không có dấu hiệu SHA lạ. Cùng lý do, vế "quy trình vận hành `T-06`
cho phép thao tác tay trên `lineage.json`" của `H-04` và `H-14` cũng chưa xác định được. Phân
loại giữ **HARDENING**, chờ `OD-T06-09`. Biên bản:
`docs/sessions/S018-post-t06-evidence-closure.md` §7.

---

## H-28 — `N-03` — hành vi fail-loud + hai trường record mới của provenance chưa vào `docs/CONVENTIONS.md`

Capability: `CAP-PROV` (`WP-A1`, đã DONE) · Owner: chưa gán · Phân loại: **CONFIRMED HARDENING (docs-only)**
Ngày ghi nhận: 2026-09-03 (`docs/reviews/E2-WP-A1-CHECK-A1-11-round4.md`, `N-03`; xác nhận
`DEC-028` điểm 6)

`ProvenanceUnresolvedError`, `provenance_resolved`, `provenance_unresolved` (đóng
`F-E2A1-03` tại S017) được ghi trong docstring của `reporting.py`, biên bản `S017`,
`PROJECT_PROGRESS.md` và task file `WP-A1` — nhưng KHÔNG có trong `docs/CONVENTIONS.md`, nơi
quy ước triển khai được tra cứu khi vận hành `T-06`. `docs/spec/04_DATA_MODEL` là spec
V2.1.5 ĐÓNG BĂNG nên không phải chỗ sửa (Master Index §6 → `WP-D2`).

Hậu quả thực tế trên hành vi hệ thống: **0**. Đây là khe tra cứu vận hành, không phải khiếm
khuyết mã.

    RE_TRIGGER_CONDITION:
    - lần cập nhật `docs/CONVENTIONS.md` kế tiếp thuộc `CAP-PROV`; HOẶC
    - quy trình vận hành `T-06` được viết thành văn bản (khi đó ràng buộc "git checkout có
      lockfile" và ngữ nghĩa `provenance_resolved`/`provenance_unresolved` nên vào cùng một
      chỗ); HOẶC
    - một người vận hành đọc `docs/CONVENTIONS.md` và không tìm thấy giải thích cho
      `ProvenanceUnresolvedError`.

---
## H-29 — Trần 1 MiB/document của Firestore đối với `ethdca/state` (ledger tăng không giới hạn)

Capability: `CAP-WEBAPP` · Owner: `T-09B` (ghi nhận tại batch review) · Phân loại: **PROVISIONAL HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09B batch review, `docs/reviews/T-09B-batch-review.md` `F-T09B-02`)

Toàn bộ sổ kế toán nằm trong MỘT document `ethdca/state` (baseline `DEC-020`). `ledger[]` tăng
~150 byte mỗi bút toán, `trades[]`/`extraDays[]` cũng tăng theo thời gian; Firestore từ chối ghi
document > 1 MiB (`invalid-argument`). Với tần suất cá nhân (vài thao tác/tuần) ngưỡng này cách
xa nhiều năm; sổ demo dựng trong test ~15 KB. Khi chạm trần, lệnh ghi bị từ chối và app hiện
"CHƯA LƯU — invalid-argument" (fail visibly, không mất bản local) nhưng không thể ghi thêm cho tới
khi tách document — đó là `ARCHITECTURE_CHANGE_REQUIRED` theo đúng điều kiện `DEC-020` (2) đã ghi
trước.

Vì sao KHÔNG BLOCKING: không có đường production hiện tại nào tạo ra document gần trần (nguồn
canonical duy nhất là sổ demo + thao tác UI, cỡ KB); "sẽ xảy ra trong tương lai" không phải căn cứ
BLOCKING (`PRODUCTION_PATH_RULE.md` § Forbidden Justification).

    RE_TRIGGER_CONDITION:
    - `ethdca/state` thật vượt 512 KiB (đo bằng Firebase Console hoặc `Tải về JSON`); HOẶC
    - `ledger[]` thật vượt 3.000 bút toán; HOẶC
    - chủ dự án thấy "CHƯA LƯU — invalid-argument" trên app thật.

---

## H-30 — Thay đổi bị từ chối vì `stale-durable` chỉ còn trong bộ nhớ tab, không được cất riêng

Capability: `CAP-WEBAPP` · Owner: `T-09B` (ghi nhận tại batch review) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09B batch review, `F-T09B-03`)

`persist()` ghi qua transaction có điều kiện `rev`: nếu Firestore đã đổi ở nơi khác (tab thứ hai
cùng profile), lệnh ghi bị từ chối `stale-durable`, bản mới hơn trên máy chủ KHÔNG bị ghi đè, app
hiện banner "NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC" và hướng dẫn *Tải về JSON* trước khi tải lại
(`CHECK-T09B-16`, kịch bản hai tab trong `test_t09b_persistence.js`). Thay đổi bị từ chối chỉ
tồn tại trong bộ nhớ tab đó: nếu người dùng tải lại trang mà không export, thay đổi đó mất (mirror
có cùng `rev` với bản bền nên `reconcileMirror()` không xem là lệch).

Vì sao KHÔNG BLOCKING: không có mất mát ÂM THẦM — lệnh bị từ chối, chip "CHƯA LƯU", banner nêu rõ
cách giữ; kịch bản đòi hỏi hai tab cùng ghi trong một phiên, hiếm với công cụ cá nhân dùng khi cần
(`DEC-021`). Đóng hẳn cần một cơ chế "stash theo nội dung" — thuộc conflict-resolution mà `DEC-021`
(9)-(10) đặt ngoài V1.

    RE_TRIGGER_CONDITION:
    - chủ dự án gặp banner "NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC" trên sổ thật; HOẶC
    - `H-23` được kích hoạt lại (thiết bị thứ hai trở thành yêu cầu V1).

---

## H-31 — `validateState()` giả định `base_pct + smart_pct + opportunity_pct = 1` khi kiểm TOTAL = A+R+D

Capability: `CAP-WEBAPP` · Owner: `T-09B` (ghi nhận tại batch review) · Phân loại: **CONFIRMED HARDENING**
Ngày ghi nhận: 2026-09-02 (T-09B batch review, `F-T09B-04`)

Bất biến kế toán mà `validateState()` (`webapp/app_logic.js`) dùng để bác một bản durable/JSON
nhập vào là `contribution = Σbase + Σsmart + oppAdded` cho từng tháng và `oppFund = Σ oppAdded`.
Đẳng thức đúng vì `addContribution()` chia trọn contribution theo 50/30/20 (Strategy §8, cả
`DEFAULT_CFG` lẫn `config` trong seed) và mọi thao tác sau đó chỉ dịch chuyển giữa a/r/d — kể cả
dưới lỗi V-01/V-02 cũ (release/reserve nhầm tháng vẫn bảo toàn tổng từng tháng). Nếu một config
tương lai có tổng tỷ lệ ≠ 1, mọi bản sổ hợp lệ sẽ bị bác (fail closed, không ghi đè) — app không
dùng được cho tới khi sửa kiểm tra. Cùng lớp: nếu file JSON thật của chủ dự án (xuất từ bản
artifact cũ) vi phạm đẳng thức vì lý do chưa biết, *Nạp lại từ JSON* sẽ từ chối và nêu tháng lệch —
đây là hành vi đúng của gate L, nhưng chủ dự án cần biết trước để không tưởng là app hỏng.

    RE_TRIGGER_CONDITION:
    - config chiến lược đổi tổng `base_pct + smart_pct + opportunity_pct` khác 1; HOẶC
    - *Nạp lại từ JSON* bản sổ thật của chủ dự án bị từ chối với lý do "TOTAL = A+R+D bị vi phạm".

---

## H-32 — `PRODUCTION_PATHS.md` §1 chưa khai `webapp/firebase_config.js`, `firestore.rules`, `firebase.json`

Capability: `CAP-GOVTOOL` · Owner: **chưa có** (cùng khe với `H-08`, `H-09`, `H-21`, `H-22`) · Phân loại: **CONFIRMED HARDENING** (tầng governance)
Ngày ghi nhận: 2026-09-02 (T-09B batch review, `F-T09B-05`)

T-09B đưa ba file mới vào đường runtime thật: `webapp/firebase_config.js` được `build_app.js`
nhúng vào trang (INPUT của mọi kết nối Firebase), `firestore.rules` quyết định mọi read/write sổ
(BUSINESS STATE boundary), `firebase.json` định nghĩa Hosting + rules deploy. Bảng khai báo §1
của `PROJECT/PRODUCTION_PATHS.md` (khai theo FILE, `H-12`) chưa có ba file này, nên phép đo
Delivery Change Budget "theo khai báo" bỏ sót chúng, trong khi lệnh glob §1 lại đếm cả file test
(`H-21`). Khai báo production path là giá trị PROJECT do chủ dự án đặt
(`PRODUCTION_PATH_RULE.md` § Declared, Not Inferred) — phiên T-09B KHÔNG tự sửa, chỉ báo cả hai
con số đo (`docs/reviews/T-09B-batch-review.md` §1).

    RE_TRIGGER_CONDITION:
    - chủ dự án cập nhật `PRODUCTION_PATHS.md` (cùng lúc với `H-12`/`H-21`); HOẶC
    - một phiên dùng con số "theo khai báo" để tuyên bố diff production = 0 trong khi ba file này đổi.

---

## H-33 — Dependency footprint của `firebase-tools` (devDependency) rộng hơn nhiều phạm vi dùng thật

Capability: `CAP-WEBAPP` · Owner: `T-09B` (ghi nhận tại phiên real-setup) · Phân loại: **PROVISIONAL HARDENING** (tầng tooling, không phải sản phẩm)
Ngày ghi nhận: 2026-09-02 (phiên tiếp nối S014 — REAL FIREBASE SETUP; `DEC-022` §11 sanity check)

`firebase-tools@15.28.2` là một CLI monolith: cài nó kéo theo transitive dependency cho MỌI sản
phẩm Firebase (`@google-cloud/pubsub`, `@google-cloud/cloud-sql-connector`, `@apphosting/common`,
`@electric-sql/pglite` cho Data Connect emulator, …) dù T-09B chỉ dùng đúng hai lệnh:
`emulators:start --only auth,firestore` và `deploy --only hosting,firestore:rules`. Đo được: 723
package entry mới trong `webapp/package-lock.json`, 677/723 không có chuỗi "firebase" trong đường
dẫn nhưng đều là transitive dependency trực tiếp của `firebase-tools` hoặc của package `firebase`
(SDK modular — mọi sản phẩm nằm sẵn trong npm package dù trang chỉ nạp 3 file compat qua CDN,
không byte nào của phần không dùng tới trình duyệt).

Vì sao KHÔNG BLOCKING: đây là devDependency (test/setup), không phải runtime browser — 0 ảnh hưởng
tới người dùng cuối; không có đường production nào bị chạm; kích thước `node_modules/` (~440 MB)
không nằm trong bất kỳ Completion Gate hay risk register nào. Vendor một `firebase-tools` tối giản
là provider-abstraction/over-engineering, trái Personal Tool Simplification Principle (`DEC-021`
§10 Over-engineering Guard) — không tự làm.

    RE_TRIGGER_CONDITION:
    - `webapp/node_modules` vượt hạn mức đĩa/thời gian cài đặt thực tế gây khó cho Owner; HOẶC
    - `firebase-tools` phát hành bản CLI tách nhỏ theo sản phẩm (modular install) mà dự án muốn
      chuyển sang; HOẶC
    - một audit bảo mật dependency (không phải mục tiêu V1, `DEC-021` §3) yêu cầu giảm bề mặt.
