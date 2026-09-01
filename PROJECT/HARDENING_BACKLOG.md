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
