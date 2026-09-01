# OWNER DISPOSITION — Product Intent, phân loại lại finding, và Integration Decision

Loại artifact:
OWNER DISPOSITION / DECISION RECORD — artifact duy nhất được tạo cho phiên này
(§24 Artifact Budget). ĐÂY KHÔNG PHẢI task file, KHÔNG phải session handoff của một work
package, KHÔNG phải repair cycle, KHÔNG phải review độc lập mới.

Ngày:
2026-09-01

Branch:
`claude/wp-a1-provenance-v67k9h`

Start SHA:
`d63c222532e87643d09b71f435a7dd276b361a88`

Phạm vi:
READ-ONLY đối với production code và test code. Không mở WP mới, không mở repair cycle,
không tạo task ID, không merge, không chạy T-06, không chạy Gate-A, không sửa wording của
bất kỳ gate đã FROZEN.

Nguồn thẩm quyền:
`AGENTS.md` §1 · `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing ·
`governance/v4/CORE/PRODUCTION_PATH_RULE.md` · `governance/v4/CORE/RISK_MODEL.md` ·
`governance/v4/CORE/CAPABILITY_MODEL.md` § Absorption Limit

---

## 0. Ghi nhận sai lệch HEAD lúc vào phiên

Chỉ thị nêu expected starting HEAD `d63c222`. Worktree khi mở phiên đang ở
`6c11a7e` — tức **cũ hơn** remote hai commit (`62f8bac`, `d63c222`).

Đã kiểm `git merge-base --is-ancestor` → fast-forward an toàn, không rewrite, không mất
commit. Đã fast-forward lên `d63c222` TRƯỚC khi đọc bất kỳ state file nào, đúng yêu cầu
Step 0 của `AGENTS.md` §7 ("đọc PROJECT_PROGRESS từ branch cũ là defect đã tái diễn").

    HEAD lúc mở phiên   = 6c11a7e
    HEAD sau fast-forward = d63c222   ← khớp expected starting HEAD

---

## 1. HAI TRỤC PHÂN LOẠI — điểm cốt lõi của phiên này

Product Intent mới (OD-1, `DEC-011`) và WP-A1 Completion Gate đã FROZEN là **hai hệ quy
chiếu độc lập**. Một finding có thể chặn trục này mà không chặn trục kia. Gộp hai trục
lại là cách nhanh nhất để hoặc (a) thổi phồng khối lượng V1, hoặc (b) lặng lẽ hạ một gate
đã đóng băng. Vì vậy toàn bộ mục §3 chấm điểm trên CẢ HAI trục, không bao giờ chỉ một.

    TRỤC 1 — BLOCKING V1
    Failure có chạm A/B/C/D/E/F trong `DEC-011` §V1 PRIORITY RULE không?
    Đây là trục SẢN PHẨM. Chủ dự án vừa định nghĩa lại nó.

    TRỤC 2 — BLOCKING WP-A1 FROZEN GATE
    Finding có vi phạm một REQUIRED check, một contract đã FROZEN, hay một Exit Criteria
    nêu đích danh không?
    Đây là trục HỢP ĐỒNG. Product Intent KHÔNG hồi tố viết lại nó (§5 chỉ thị;
    `AGENTS.md` §4).

`RISK_MODEL.md` nói thẳng điều này: *"a low-severity finding IS blocking when it violates a
FROZEN contract that a Completion Gate depends on. Severity and blocking status are separate
axes."*

Hệ quả trực tiếp, và đây là kết luận chính của phiên: **ba hạng mục vừa rời khỏi
BLOCKING V1 nhưng vẫn ĐANG chặn gate đã FROZEN.** Đó chính xác là định nghĩa của
`LEGACY_GATE_DISPOSITION_REQUIRED` — xem §4.

---

## 2. Nguyên tắc áp dụng khi hạ cấp

Chỉ thị §1 cấm hạ một finding chỉ vì "dự án cá nhân". Mỗi lần hạ cấp dưới đây phải dựa
trên MỘT trong hai căn cứ đo được, không phải trên tính chất cá nhân của dự án:

- **Căn cứ P** — `PRODUCTION_PATH_RULE.md`: counterexample chỉ dựng được bằng **sửa tay
  artifact**, không có đường sinh nào từ mã hiện tại. Mặc định HARDENING.
- **Căn cứ F** — không chạm A–F: failure không làm sai quyết định, không sai tiền, không
  mất lịch sử, không làm hỏng dữ liệu thị trường, không làm app không chạy, và **không**
  khiến hệ thống tuyên bố một kết quả official hợp lệ trên dữ liệu không đủ.

Ranh giới mà chỉ thị §4 yêu cầu phân biệt, áp dụng nguyên văn:

    "có thể sửa file thủ công để phá"          -> KHÔNG đủ để BLOCKING  (căn cứ P)
    "pipeline tự sinh metadata sai lúc runtime" -> CÓ THỂ BLOCKING

`F-E2A1R3-01` rơi vào vế trên. `F-E2A1R3-05` rơi vào vế dưới — và đó là lý do nó là
finding DUY NHẤT giữ BLOCKING V1.

---

## 3. PHÂN LOẠI LẠI TỪNG FINDING

### 3.1 `F-E2A1R3-05` — fetch bị cắt cụt vẫn đủ tư cách official

    PRODUCTION PATH        = fetch_all -> lineage.json -> official_eligibility -> dataset
                             -> pipeline 18 bước -> Buy Score / regime / verdict.
                             CHUỖI ĐẦY ĐỦ, không mắt xích nào là stub của reviewer.
    REALISTIC DAILY-USE    = CÓ, và là kịch bản DỰ KIẾN chứ không phải kịch bản hiếm:
    TRIGGER                  archive Binance trễ tới 2020-01, REST bị chặn/rate-limit.
                             BLK-001 nghĩa là chủ dự án SẼ fetch qua đường mạng bất
                             thường (máy khác/VPS, DEC-003) — đúng điều kiện sinh ra lỗi.
    V1 CONSEQUENCE         = dataset thiếu ~92% khoảng thời gian ĐƯỢC YÊU CẦU;
                             `missing_count = 0`; `official_eligibility -> (True,'verified')`.
                             Pipeline tính Buy Score / regime / budget trên dữ liệu cụt và
                             hệ thống TUYÊN BỐ kết quả đó hợp lệ.
    A/B/C/D/E/F IMPACTED   = **A** (recommendation/Buy Score sai)
                             **D** (dữ liệu thị trường thật không đi qua pipeline đúng)
                             **F** (tuyên bố official hợp lệ trên dữ liệu không đủ)
                             -> 3/6. Đây là finding nặng nhất của toàn tập.
    REPRODUCTION EVIDENCE  = E2 vòng ba, reviewer stub I/O trên mã production thật và tham
                             số production thật (nguồn 1 + 2). CONFIRMED.
    CURRENT OWNER          = KHÔNG CÓ — `OWNER_ASSIGNMENT_REQUIRED` (adoption §5.4)
    CURRENT CLASSIFICATION = OWNER_ASSIGNMENT_REQUIRED
    RECLASSIFICATION       = KHÔNG hạ cấp. **BLOCKING V1 — GIỮ NGUYÊN và KHẲNG ĐỊNH LẠI.**
                             Product Intent làm nó NẶNG HƠN chứ không nhẹ hơn: OD-1 đặt
                             "REAL MARKET DATA" và "CORRECT DECISION" lên đầu ưu tiên.
    RE_TRIGGER             = không áp dụng (không phải HARDENING)

Xem §5 để biết đề xuất capability owner.

### 3.2 `F-E2A1-03` — provenance suy biến im lặng ngoài editable install

    PRODUCTION PATH        = reporting.py -> save_run -> backtest_runs.jsonl. CÓ THẬT.
    REALISTIC DAILY-USE    = CÓ, nhưng chỉ ở lần chạy T-06 trên venv sạch — không phải
    TRIGGER                  vòng lặp dùng hàng ngày qua web app.
    V1 CONSEQUENCE         = record ghi `code_commit='unknown'` và
                             `dependency_lock_hash='no-lockfile'`, im lặng. **Các con số
                             của lần chạy vẫn ĐÚNG.** Thứ mất đi là khả năng chứng minh
                             về sau mã nào đã sinh ra chúng.
    A/B/C/D/E/F IMPACTED   = **KHÔNG CÁI NÀO.** Không sai quyết định (A), không sai tiền
                             (B), không mất lịch sử giao dịch thật (C — provenance của
                             backtest run không phải lịch sử giao dịch của chủ dự án),
                             dữ liệu thị trường vẫn đi qua pipeline đúng (D), app vẫn
                             chạy (E), và hệ thống KHÔNG tuyên bố kết quả hợp lệ trên dữ
                             liệu không đủ (F — dữ liệu đủ, chỉ metadata về mã bị thiếu).
                             Đây đúng nhóm "enterprise-grade provenance" mà §1 chỉ thị
                             loại khỏi BLOCKING V1 mặc định.
    REPRODUCTION EVIDENCE  = E2 vòng ba, reviewer tự dựng venv sạch. CONFIRMED. Không đổi.
    CURRENT OWNER          = `WP-A1` / `CAP-PROV`
    CURRENT CLASSIFICATION = CONFIRMED BLOCKING (adoption §5.1)
    RECLASSIFICATION       = **BLOCKING V1 -> KHÔNG.** Căn cứ F.
                             **BLOCKING WP-A1 FROZEN GATE -> VẪN CÓ.** Nó là follow-up
                             BẮT BUỘC #1 của E2 vòng ba và rơi vào Exit Criteria
                             "Không defect nghiêm trọng nào chưa xử lý" — một mục đã
                             FROZEN. Reviewer E2 xếp mức CAO.
                             -> `LEGACY_GATE_DISPOSITION_REQUIRED` (§4).
    GHI CHÚ RÀNG BUỘC      = Master Index §6 CẤM chạy lại official run để sửa. Nếu T-06
                             chạy trong tình trạng này, provenance mất VĨNH VIỄN. Đó là
                             lý do mục này không được đẩy xuống HARDENING im lặng mà phải
                             đi qua quyết định tường minh của chủ dự án.

### 3.3 `F-E2A1R3-03` — contract case 13 chưa thi hành (`official_reason`)

    PRODUCTION PATH        = mọi lần chạy dev. `pipeline.run_gate1/2/3` -> `save_run`
                             -> `*_metrics.json`. CÓ THẬT, và đây LÀ "pipeline tự sinh
                             metadata sai trong normal runtime" — vế được phép BLOCKING.
    REALISTIC DAILY-USE    = CÓ. Không cần sửa tay gì cả.
    TRIGGER
    V1 CONSEQUENCE         = ghi cặp mâu thuẫn `{"official": false,
                             "official_reason": "verified"}`. Cờ THẨM QUYỀN
                             (`official: false`) ĐÚNG — hệ thống vẫn fail-closed. Sai là
                             mã lý do: nguyên nhân `dev_limit` bị che hoàn toàn, và mã
                             `dev_limit_set` không tồn tại trong `src/`.
    A/B/C/D/E/F IMPACTED   = **KHÔNG CÁI NÀO — nhưng đây là mục sát ranh giới nhất.**
                             F không bị chạm vì hệ thống KHÔNG tuyên bố kết quả hợp lệ:
                             nó nói `official: false`, đúng. Rủi ro còn lại là **người
                             đọc** artifact thấy chữ `"verified"` và tin nhầm — rủi ro
                             diễn giải, không phải rủi ro tính toán. Với dự án một người
                             dùng, người đọc chính là tác giả.
    REPRODUCTION EVIDENCE  = reviewer chạy `run_gate1(prep,out,dev_limit=5)` và
                             `run_gate2(prep,out,limit=3)`. CONFIRMED. Không đổi.
    CURRENT OWNER          = `WP-A1` / `CAP-PROV`
    CURRENT CLASSIFICATION = CONFIRMED BLOCKING (adoption §5.1)
    RECLASSIFICATION       = **BLOCKING V1 -> KHÔNG** (căn cứ F, sát ranh giới).
                             **BLOCKING WP-A1 FROZEN GATE -> VẪN CÓ, và mạnh nhất trong
                             ba mục.** Contract 20 case của PRE-S008 đã ĐÓNG BĂNG và ghi
                             rõ "S008 thực thi đúng bảng này, không tự thêm/bớt case".
                             `RISK_MODEL.md` áp dụng trực tiếp: vi phạm FROZEN contract
                             mà Completion Gate phụ thuộc = BLOCKING bất kể severity.
                             -> `LEGACY_GATE_DISPOSITION_REQUIRED` (§4).
    KHUYẾN NGHỊ CHO OWNER  = trong ba mục ở §4, đây là mục KHÓ biện minh cho `DESCOPE`
                             nhất, vì hạ nó nghĩa là chấp nhận mã lệch khỏi một hợp đồng
                             mới đóng băng cách đây bảy ngày.

### 3.4 `F-E2A1R3-01` — `row_count` ngoài mọi checksum

    PRODUCTION PATH        = KHÔNG ĐỦ. Đây là điểm quyết định.
                             `official_eligibility` là enforcement point thật, nhưng
                             counterexample đòi **sửa tay đúng một số nguyên trong
                             `lineage.json`** (0 -> 140156) sau khi đã làm rỗng parquet.
                             Không đường sinh nào của `fetch_all` / `synth.generate` tạo
                             ra tổ hợp đó: nếu fetch trả rỗng, writer ghi `row_count=0`
                             trung thực và `empty_series` bắn đúng.
    REALISTIC DAILY-USE    = KHÔNG. Luồng dùng hàng ngày không sửa tay `lineage.json`.
    TRIGGER                  OD-1 loại bỏ hostile user: người duy nhất sửa file đó là
                             chủ dự án, tự phá dữ liệu của chính mình.
    V1 CONSEQUENCE         = chỉ hiện thực hoá được sau một hành vi tampering có chủ ý.
    A/B/C/D/E/F IMPACTED   = D/F **chỉ trong kịch bản tampering**, mà OD-1 đặt ngoài phạm
                             vi V1 tường minh.
    REPRODUCTION EVIDENCE  = E2 vòng ba, reviewer tái hiện thật. CONFIRMED — bằng chứng
                             KHÔNG bị nghi ngờ; cái thiếu là ĐƯỜNG SINH, không phải bằng
                             chứng.
    CURRENT OWNER          = `WP-A1` / `CAP-PROV`
    CURRENT CLASSIFICATION = CONFIRMED BLOCKING (adoption §5.1)
    RECLASSIFICATION       = **HARDENING.** Căn cứ P, áp dụng nguyên văn
                             `PRODUCTION_PATH_RULE.md`: counterexample chỉ dựng được bằng
                             sửa tay artifact -> mặc định HARDENING. Đây là CÙNG LỚP với
                             `F-PRE008-01` (H-06) và `F-E2A1R3-04` (H-05), cả hai đã là
                             HARDENING từ trước — giữ nó ở BLOCKING là bất nhất nội bộ.
                             Ghi vào backlog là **H-13**.
    LƯU Ý KHÔNG ĐƯỢC BỎ   = adoption §5.1 giữ nó BLOCKING vì một lý do KHÁC production
                             path: giới hạn này **chưa được công bố**, trong khi
                             `F-PRE008-01` đã công bố. Lý do đó vẫn đúng và không bị bác.
                             Nó được chuyển thành nghĩa vụ công bố trong
                             `RE_TRIGGER_CONDITION` của H-13, không bị đánh rơi.

### 3.5 `F-E2A1R3-06` (bao gồm `F-E2A1-08`) — tài liệu đã lệch so với mã

    PRODUCTION PATH        = `docs/CONVENTIONS.md` KHÔNG phải production path
                             (`PRODUCTION_PATHS.md` §2). Nhưng nó được Exit Criteria của
                             WP-A1 NÊU ĐÍCH DANH — đường Completion Gate, độc lập với
                             đường production path.
    REALISTIC DAILY-USE    = KHÔNG. Tài liệu không tham gia runtime.
    TRIGGER
    V1 CONSEQUENCE         = người đọc hiểu cơ chế MẠNH HƠN thực tế. Với dự án một người,
                             người đọc là tác giả.
    A/B/C/D/E/F IMPACTED   = **KHÔNG CÁI NÀO.**
    REPRODUCTION EVIDENCE  = đối chiếu tài liệu ↔ mã + stub cho `lineage['source']='mixed'`
                             với `(True,'verified')`. CONFIRMED.
    CURRENT OWNER          = `WP-A1` / `CAP-PROV`
    CURRENT CLASSIFICATION = CONFIRMED BLOCKING (adoption §5.1)
    RECLASSIFICATION       = **BLOCKING V1 -> KHÔNG** (căn cứ F).
                             **BLOCKING WP-A1 FROZEN GATE -> VẪN CÓ**, qua Exit Criteria
                             "`docs/CONVENTIONS.md` ghi quy ước phân loại nguồn dữ liệu".
                             -> `LEGACY_GATE_DISPOSITION_REQUIRED` (§4).
    PHÁT HIỆN QUAN TRỌNG   = **mục này đóng được mà KHÔNG tiêu repair budget.** Xem §4.3.

### 3.6 Bảy finding đang HARDENING (H-01…H-07) — soát lại dưới Product Intent

Soát từng mục theo A–F. Product Intent chỉ có thể làm YẾU đi lập luận blocking, trừ khi
A–F bị chạm. Không mục nào chạm A–F, nên **cả bảy giữ nguyên HARDENING**, re-trigger giữ
nguyên. Ghi riêng hai mục có sắc thái:

- **H-02 (`F-E2A1-06`, tzdata)** — là mục HARDENING duy nhất chạm được **B** về lý thuyết:
  tzdata quyết định biên accounting month, mà WP-A7 vừa khoá ngữ nghĩa vốn Smart vào đó,
  nên lệch biên tháng = lệch ngân sách. Vẫn giữ HARDENING vì hai lẽ độc lập: (1) chưa có
  divergence ĐO ĐƯỢC, bằng chứng hiện là suy luận từ mã; (2) OD-1 xác định V1 chạy trên
  MỘT máy của chủ dự án, nên "tái lập trên máy có tzdata khác" không phải luồng dùng hàng
  ngày. Product Intent làm mục này nhẹ đi, không nặng lên. Re-trigger giữ nguyên.
- **H-04 (`F-E2A1R3-02`, `TypeError`)** — Product Intent làm nó nhẹ đi rõ rệt: V1
  Acceptance điểm 9 yêu cầu lỗi có thể làm sai quyết định/sai tiền phải **fail visibly**.
  Một traceback là fail visibly ở dạng thuần tuý nhất. Giữ HARDENING.

Ba mục H-05, H-06, H-13 nay cùng một lớp (sửa tay artifact) và cùng một biện pháp đối
trọng (DEC-003, đối chiếu hai máy). Chúng nên được xử lý như MỘT gói nếu chủ dự án quyết
định đóng, chứ không phải ba lần sửa rời rạc.

### 3.7 Bốn mục `CAP-GOVTOOL` (H-08…H-12)

Không đổi. Không mục nào chạm A–F, không mục nào trên đường găng V1. H-08 giữ
`OUT_OF_SCOPE` với kênh Owner Decision đã có (mục #5 trong danh sách quyết định của
`PROJECT_PROGRESS.md`). H-11 giữ tư cách reference.

### 3.8 Kiểm đếm

Tập vào phiên — 13 finding WP-A1 (adoption §5.5), cộng các mục CAP-GOVTOOL ngoài tập.

| Phân loại | TRƯỚC | SAU | Thay đổi |
|---|---|---|---|
| CONFIRMED BLOCKING | 5 | — | tách thành hai trục dưới đây |
| ├─ BLOCKING V1 | (5 gộp chung) | **1** | `F-E2A1R3-05` |
| └─ BLOCKING FROZEN GATE, không BLOCKING V1 | (5 gộp chung) | **4 finding / 3 hạng mục** | `F-E2A1-03`, `F-E2A1R3-03`, `F-E2A1R3-06`+`F-E2A1-08` |
| CONFIRMED HARDENING (WP-A1) | 7 | **8** | +`F-E2A1R3-01` (H-13) |
| PROVISIONAL | 0 | **0** | — |
| OWNER_ASSIGNMENT_REQUIRED | 1 | **0** | `F-E2A1R3-05` nay có đề xuất owner (§5) |
| **Cộng tập WP-A1** | **13** | **13** | không mất, không thêm finding |

Ngoài tập WP-A1: `OUT_OF_SCOPE` = 1 (H-08); HARDENING `CAP-GOVTOOL` = 3 (H-09, H-10,
H-12); reference = 1 (H-11). Không đổi.

    TASK MỚI ĐƯỢC TẠO = 0
    FINDING BỊ ĐÁNH RƠI = 0
    FINDING ĐÃ ĐÓNG BỊ MỞ LẠI = 0   (F-E2A1-01, -02, -05, -07 không đụng tới)

---

## 4. `LEGACY_GATE_DISPOSITION_REQUIRED`

    TRẠNG THÁI: KÍCH HOẠT — 3 hạng mục.

Adoption V4.3 ghi `LEGACY_GATE_COMPATIBILITY_REQUIRED: KHÔNG kích hoạt`, và điều đó ĐÚNG
tại thời điểm đó: V4.3 là overlay governance thuần tuý, không đổi ngữ nghĩa gate nào.
Thứ kích hoạt disposition lần này là **Product Intent OD-1**, một đầu vào mới hoàn toàn
không tồn tại lúc adoption.

Ba hạng mục dưới đây thoả đúng điều kiện §5 chỉ thị: một yêu cầu đã FROZEN không còn phù
hợp với V1, nhưng **wording KHÔNG được sửa**.

| Hạng mục | Neo vào gate | V1 (A–F) | Ghi chú |
|---|---|---|---|
| `F-E2A1-03` | Exit Criteria "không defect nghiêm trọng nào chưa xử lý" + follow-up BẮT BUỘC #1 | không chạm | provenance/reproducibility — §1 loại khỏi BLOCKING V1 mặc định |
| `F-E2A1R3-03` | contract §10 case 13 (FROZEN 2026-08-25, PRE-S008) | không chạm | vi phạm FROZEN contract; khó `DESCOPE` nhất |
| `F-E2A1R3-06` + `F-E2A1-08` | Exit Criteria "`docs/CONVENTIONS.md` ghi quy ước phân loại nguồn" | không chạm | đóng được bằng tài liệu — xem §4.3 |

### 4.1 KHÔNG được làm

Không sửa wording của CHECK-A1-01…11, không sửa Exit Criteria, không sửa contract 20 case,
không hạ REQUIRED check nào, không chuyển WP-A1 sang DONE. Toàn bộ những thứ đó giữ nguyên
sau phiên này.

### 4.2 Ba lựa chọn canonical thuộc thẩm quyền chủ dự án

Agent KHÔNG tự chọn. Trình bày để chủ dự án chọn, một lựa chọn cho mỗi hạng mục:

    ACCEPT_AS_IS      Giữ gate nguyên vẹn. WP-A1 chưa DONE cho tới khi đóng đủ ba hạng
                      mục. Cần OWNER_EXTENSION vì budget đã hết (§6).

    DESCOPE           Tuyên bố hạng mục nằm ngoài V1. Gate giữ nguyên wording; hạng mục
                      được ghi là ĐÃ DESCOPE kèm lý do, và chuyển sang Hardening Backlog
                      với re-trigger. KHÔNG phải xoá, KHÔNG phải "đã đóng".

    OWNER_EXTENSION   Cấp thêm repair budget cho CAP-PROV để đóng hạng mục trong WP-A1.

### 4.3 Một đường đi không cần OWNER_EXTENSION — đã kiểm chứng bằng ledger

Đây là kết quả có giá trị thực hành nhất của §4, nên nêu tách riêng.

`REVIEW_BUDGET_LEDGER.md` §1 đo repair cycle bằng **diff trên production path**, và trong
bảng lịch sử có sẵn một tiền lệ:

    | — | Decision pack PRE-S008 | 2f20e6c | bd7c5ff | 0 (chỉ docs/) | KHÔNG tính là repair cycle |

`F-E2A1R3-06` (+`F-E2A1-08`) đóng được **hoàn toàn bằng `docs/CONVENTIONS.md`**: ghi
coverage invariant, ghi `empty_series`, thêm `mixed` vào bảng taxonomy, sửa mã lý do đã
lỗi thời trong Evidence CHECK-A1-06. Không dòng nào trong `src/` hay `webapp/`.
Diff production path = 0 -> **không tiêu repair cycle, không cần OWNER_EXTENSION.**

Cùng cơ chế áp dụng cho disposition (b) của `F-E2A1R3-01`/H-13: adoption §5.1 đã xác định
"công bố giới hạn trong `docs/CONVENTIONS.md`" là một trong hai cách đóng hợp lệ.

Hệ quả: **hai trong bốn hạng mục khắc phục của WP-A1 nằm trong tầm với ở chi phí budget
bằng 0.** Còn lại `F-E2A1-03` và `F-E2A1R3-03` là hai mục thật sự cần production code, và
chỉ hai mục đó mới cần quyết định của §4.2.

Đây là ghi nhận phân tích, KHÔNG phải hành động. Phiên này không sửa `docs/CONVENTIONS.md`
— đó là công việc của WP-A1, cần chỉ thị riêng.

---

## 5. `F-E2A1R3-05` — ĐỀ XUẤT CAPABILITY OWNER

Yêu cầu §6 chỉ thị: xác định capability owner phù hợp nhất TỪ `CAPABILITY_REGISTRY` hiện
có; ưu tiên capability đã tồn tại; KHÔNG tạo task ID.

### 5.1 Loại `CAP-PROV` (`WP-A1`)

`data/` nằm trong Expected Touch Area của WP-A1, nên về mặt đường dẫn thì hợp. Nhưng
`CAPABILITY_REGISTRY` §4 đã ghi `ABSORPTION_LIMIT_REACHED` với hai ngưỡng A và C, và
`DEC-012` vừa phê chuẩn `REMAINING = 0` với `OWNER_EXTENSION = NOT GRANTED`. Gán vào
WP-A1 là mở repair cycle thứ tư mà không có thẩm quyền. **LOẠI.**

### 5.2 Đề xuất: `CAP-DATA` (`WP-A4`) — theo CHỦ ĐỀ, không theo đường dẫn file

Điều chặn WP-A4 hiện nay là một câu trong Expected Touch Area loại trừ
`src/eth_dca_os/data/`. Nhưng đọc kỹ **lý do** của câu đó:

> "gói này xử lý **ngữ nghĩa** dữ liệu xấu, không xử lý việc **lấy** dữ liệu"

Defect của `F-E2A1R3-05` KHÔNG nằm ở việc lấy dữ liệu. `fetch_all` hành xử trung thực: nó
trả về đúng những gì archive có. Defect nằm ở chỗ **`gap_report` chỉ đo khoảng trống GIỮA
first và last quan sát được, không bao giờ đối chiếu với `start`/`end` ĐÃ YÊU CẦU**, và
`official_eligibility` không nhìn `first_timestamp`/`last_timestamp` ở bất kỳ đâu. Nói
cách khác: hệ thống **mô tả sai cái gì đang thiếu**. Đó chính xác là *ngữ nghĩa dữ liệu
thiếu* — đúng chủ đề của `CAP-DATA`.

Thứ loại WP-A4 hiện nay vì vậy là **hình thức đường dẫn file**, không phải chủ đề. Và
`HARDENING_BACKLOG.md` H-12 đã ghi sẵn chính khiếm khuyết đó ở tầng governance:
`PRODUCTION_PATHS.md` khai báo theo FILE chứ chưa theo CHUỖI dữ liệu, trong khi
`GOVERNANCE_V4.md` §II.1 cấm chấm rủi ro theo tên module thay vì theo đường dữ liệu. Gán
quyền sở hữu theo đường dẫn file là cùng một lỗi, ở tầng capability.

Ba lý do độc lập ủng hộ `CAP-DATA`:

1. **Chủ đề khớp** — lập luận ở trên.
2. **Budget sạch** — `REVIEW_BUDGET_LEDGER.md` §2: WP-A4 baseline "chưa bắt đầu",
   repair cycles = 0, vòng E2 = 0. Không có absorption limit nào bị chạm.
3. **Đúng chỗ trên đường găng** — WP-A4 đang `READY`, là prerequisite của GATE-A, và
   GATE-A đứng trước T-06. Finding này bắt buộc phải đóng TRƯỚC T-06 (lời reviewer E2).
   Hai mốc trùng nhau, nên không kéo dài đường găng thêm một bước nào.

### 5.3 Quyết định tối thiểu trình chủ dự án

`CAP-DATA` là đề xuất, chưa phải chỉ định: chín REQUIRED check của WP-A4 đã FROZEN từ
2026-08-23 và **không check nào phủ truncation-vs-requested-range**. Vì vậy cần đúng MỘT
quyết định, không hơn:

    OWNER_DECISION_REQUIRED

    Phê duyệt một COMPLETION GATE CHANGE PROPOSAL cho WP-A4 bổ sung MỘT REQUIRED check:
    "coverage của dataset phải được đối chiếu với khoảng thời gian ĐƯỢC YÊU CẦU
     (start/end), không chỉ với khoảng quan sát được; official_eligibility phải từ chối
     dataset không phủ đủ khoảng yêu cầu."

    Kèm làm rõ Expected Touch Area của WP-A4: loại trừ là về CƠ CHẾ LẤY dữ liệu
    (HTTP, retry, rate-limit, nguồn archive/REST), KHÔNG phải về NGỮ NGHĨA COVERAGE.

Nếu chủ dự án từ chối, `F-E2A1R3-05` quay lại `OWNER_ASSIGNMENT_REQUIRED` và **T-06 vẫn
bị chặn** — không có đường thứ ba. KHÔNG đặt task ID mới trong cả hai nhánh: WP-A4 đã tồn
tại.

---

## 6. CAP-PROV BUDGET — đã phê chuẩn

Chi tiết ở `DEC-012` và `PROJECT/REVIEW_BUDGET_LEDGER.md` §1.

    ALLOWED   = 2
    USED      = 2   (repair cycle 1: d72fbc4..2f20e6c; repair cycle 2: bd7c5ff..a0c278a)
    REMAINING = 0
    OWNER_EXTENSION = NOT GRANTED

`MIGRATION_UNCERTAINTY` của ledger §1 được GIẢI QUYẾT: hạn mức nay do chủ dự án đặt, không
còn là "chưa từng được đặt". Không reset. Adoption V4.3 và source reconciliation KHÔNG
được tính là repair cycle của WP-A1 — cả hai có diff production path = 0, đã kiểm bằng git.

---

## 7. INTEGRATION DECISION CHECK

### 7.1 Baseline — đo bằng git tại phiên này, không chép từ báo cáo cũ

    CURRENT BRANCH           = claude/wp-a1-provenance-v67k9h
    CURRENT HEAD             = d63c222532e87643d09b71f435a7dd276b361a88
    DEFAULT BRANCH           = claude/plan-tool-from-docs-qijx5m
                               (giải từ origin/HEAD, KHÔNG giả định 'main')
    DEFAULT BRANCH HEAD      = 4a46b3c2012d786f457316e3452c971bab12464a
    MERGE BASE               = e36842583372a2eae8335c5c7048d92d5ff2c987 (2026-08-23)
    AHEAD                    = 29 commit
    BEHIND                   = 1 commit
    DIVERGENCE AGE           = 9 ngày
    PRODUCTION DIFF          = 14 files, +662 / -113
    GOVERNANCE/DOCS DIFF     = 66 files, +21715 / -227
    TEST DIFF                = 8 files, +2378 / -0
    TỔNG                     = 88 files, +24755 / -340

Sai lệch so với con số trong chỉ thị (28 commit / 23.870 LOC) là do hai commit governance
`62f8bac` và `d63c222` đã landed sau khi con số đó được ghi. Con số có thẩm quyền là con số
đo tại phiên này.

Ngưỡng của `branch_authority_check.sh`: AHEAD_MAX=10, AGE_DAYS_MAX=3, LOC_MAX=5000.
Vượt lần lượt **2,9x / 3,0x / 5,0x** -> `INTEGRATION_DECISION_REQUIRED` hợp lệ.

### 7.2 Hai phép đo quyết định — xác suất xung đột KHÔNG phải ước lượng

Chạy `git merge-tree --write-tree` (thuần tính toán, không chạm worktree, không tạo commit):

    git merge-tree --write-tree --name-only HEAD origin/claude/plan-tool-from-docs-qijx5m
    -> exit 0
    -> 0 file xung đột
    -> tree kết quả = 1a9b7e855fbc154e3c1b5100bb082cf807549bda

    git rev-parse HEAD^{tree}
    -> 1a9b7e855fbc154e3c1b5100bb082cf807549bda      ← TRÙNG KHỚP

**Hai tree BẰNG NHAU.** Nghĩa là merge default branch vào HEAD cho ra đúng cây hiện tại,
không đổi một byte. Lý do đã kiểm:

    git merge-base --is-ancestor origin/claude/move-files-to-root-7zhv8l HEAD -> YES

Commit mà branch này "behind" (`4a46b3c`) là merge của PR #1 từ
`claude/move-files-to-root-7zhv8l`, và nhánh đó đã là **tổ tiên** của HEAD. Nội dung của nó
đã nằm sẵn trong branch hiện tại từ lâu.

    XÁC SUẤT XUNG ĐỘT = 0, ĐO ĐƯỢC, không phải ước lượng.
    `git diff --stat HEAD..origin/<default>` là XOÁ THUẦN TUÝ 29 commit của branch này.
    Default branch KHÔNG chứa bất kỳ công việc nào mà branch này thiếu.

### 7.3 Phát hiện kèm theo — repo KHÔNG có trunk quy ước

`origin/HEAD` trỏ tới `claude/plan-tool-from-docs-qijx5m` — bản thân nó là một branch làm
việc kiểu `claude/*`, không phải `main`/`master`. Không branch nào tên `main` tồn tại trên
remote. Đây không làm tăng rủi ro kỹ thuật của việc tích hợp, nhưng nó khiến câu hỏi
"tích hợp VÀO ĐÂU" trở thành một quyết định thật, không phải mặc định. Xem §7.5.

### 7.4 Ba phương án

**A. INTEGRATE NOW** — merge branch hiện tại vào default branch.

    benefit                    Gỡ hard-stop INTEGRATION_DECISION_REQUIRED. Đưa 6 đơn vị
                               công việc ĐÃ DONE (T-04, MICRO-GOVDEF-001, WP-A3, WP-A7,
                               WP-D1, WP-A2) ra khỏi tình trạng nằm trên một branch duy
                               nhất. Bỏ single point of failure.
    risk                       WP-A1 đang IN_PROGRESS với gate chưa đóng. Nhưng branch
                               này đã là NƠI DUY NHẤT có công việc; default branch đứng
                               sau hoàn toàn; không có consumer nào khác, không release.
                               Rủi ro "phát hành việc dang dở" ở mức danh nghĩa.
    conflict probability       **0 — đo được** (§7.2), tree sau merge trùng tree hiện tại.
    rollback difficulty        THẤP. Default branch chỉ hơn merge-base 1 commit và không
                               có consumer; revert merge commit là đủ.
    effect on WP-A1            KHÔNG CÓ. Tích hợp là thao tác git; không đổi state, gate,
                               budget hay finding của WP-A1. Production diff giữ nguyên.
    effect on next work        TÍCH CỰC. WP-A4 — capability được đề xuất sở hữu blocker V1
                               duy nhất (§5) — sẽ nhánh ra từ nền đã tích hợp thay vì
                               chồng branch dài thứ hai lên một branch chưa tích hợp.
    V4.3 compliance            ĐẠT. Thoả hard-stop bằng một Owner Decision tường minh.

**B. CONTINUE CURRENT BRANCH WITH LIMIT** — không tích hợp, ghi lý do + ngày tái xét.

    benefit                    Không thao tác git nào lúc này.
    risk                       Divergence tiếp tục lớn lên từ mức đã vượt ngưỡng 2,9–5,0x.
                               WP-A4 sẽ chạm `src/eth_dca_os/data/` — ĐÚNG thư mục WP-A1
                               vừa sửa — nên xác suất xung đột 0 hiện nay sẽ không giữ
                               nguyên. Hard-stop sẽ bắn lại ở mỗi phiên.
    conflict probability       0 hôm nay; TĂNG theo thời gian.
    rollback difficulty        Không áp dụng bây giờ; khó hơn về sau.
    effect on WP-A1            KHÔNG CÓ.
    effect on next work        TIÊU CỰC. WP-A4 chồng lên nền chưa tích hợp.
    V4.3 compliance            ĐẠT **chỉ khi** chủ dự án nêu lý do VÀ đặt ngày tái xét.
                               "Không làm gì" KHÔNG phải phương án B hợp lệ.

**C. PARTIAL / STAGED INTEGRATION** — chỉ tích hợp các work package đã DONE.

    benefit                    Trên lý thuyết: tách việc đã xong khỏi WP-A1 dang dở.
    risk                       CAO, và đây là điểm quyết định. 29 commit là TUYẾN TÍNH và
                               đan xen: 8 commit WP-A1 (d72fbc4…6c11a7e) nằm TRÊN commit
                               DONE của WP-A2 (666de14), và hai commit governance nằm trên
                               tất cả. Tách tập con = viết lại lịch sử, tạo lineage thứ
                               hai, và **phá neo BASELINE SHA của budget ledger**
                               (`666de14` cho CAP-PROV). Ledger quy định con số phải
                               "tái dựng từ git, không chép từ báo cáo" — phương án này
                               làm điều đó bất khả thi. Nó cũng huỷ luôn tính chất
                               merge-tree = 0.
    conflict probability       CAO — do chính thao tác tạo ra, không phải vốn có.
    rollback difficulty        CAO.
    effect on WP-A1            XẤU. Phép đo budget tích luỹ không còn tái dựng được.
    effect on next work        TIÊU CỰC.
    V4.3 compliance            Đi ngược `STATE_AUTHORITY.md` § Single Source Of Truth.

### 7.5 KHUYẾN NGHỊ

    KHUYẾN NGHỊ = A (INTEGRATE NOW)

Ba lý do, xếp theo sức nặng:

1. **Chi phí rủi ro đo được bằng 0.** Đây không phải đánh giá định tính: tree sau merge
   TRÙNG KHỚP tree hiện tại (§7.2). Tích hợp không đưa vào một dòng mã nào và không thể
   làm hỏng thứ gì đang chạy.
2. **Không tốn gì ở phía WP-A1.** Không đổi state, không đổi gate, không tiêu budget,
   không đụng finding. Hai quyết định hoàn toàn độc lập — không cần chờ WP-A1 xong.
3. **Cửa sổ đang đóng lại.** Xác suất xung đột bằng 0 là do WP-A4 CHƯA bắt đầu. WP-A4
   phải chạm `src/eth_dca_os/data/`, đúng thư mục WP-A1 vừa sửa. Tích hợp trước khi WP-A4
   mở là rẻ nhất mà tình huống này sẽ còn có.

Phương án C nên bị loại tường minh: nó phá neo đo lường của ledger để đổi lấy một lợi ích
mà phương án A vốn đã cho miễn phí.

Quyết định kèm theo, thuộc thẩm quyền chủ dự án (§7.3): tích hợp vào chính
`claude/plan-tool-from-docs-qijx5m`, hay lập một trunk quy ước (`main`) trước đã. Agent
không tự chọn.

    KHÔNG MERGE TRONG PHIÊN NÀY. Đây là khuyến nghị, không phải hành động.

---

## 8. ĐƯỜNG NGẮN NHẤT TỚI V1

Theo trình tự §11 chỉ thị. Mỗi đoạn chỉ nêu blocker THỰC SỰ còn lại.

    CURRENT
      WP-A1 IN_PROGRESS · CHECK-A1-01…10 PASS · CHECK-A1-11 FAIL
      Blocker THẬT: budget REMAINING = 0 và OWNER_EXTENSION NOT GRANTED.
                    3 hạng mục LEGACY_GATE_DISPOSITION_REQUIRED chờ chủ dự án (§4).
                    2 trong 3 đóng được ở chi phí budget = 0 (§4.3).
      -> cần: quyết định của chủ dự án. Không cần khám phá thêm.

    -> NEXT CAPABILITY = CAP-DATA (WP-A4)
      Vì sao là gói tiếp theo: nó sở hữu blocker V1 DUY NHẤT (F-E2A1R3-05, §5),
      đang READY, budget sạch, và đã nằm trên đường găng GATE-A từ trước.
      Blocker THẬT: một COMPLETION GATE CHANGE PROPOSAL cần chủ dự án phê duyệt (§5.3).
      Không blocker kỹ thuật nào.

    -> GATE-A  (WP-A1 ∧ WP-A2 ✅ ∧ WP-A3 ✅ ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 ✅)
      Còn thiếu: WP-A1 (disposition), WP-A4, WP-A5, WP-A6.
      Blocker THẬT: WP-A5 đã đủ dependency (A2 ✅ ∧ A3 ✅ ∧ A7 ✅) — READY, không bị chặn.
                    WP-A6 chờ WP-A4. Đó là toàn bộ chuỗi phụ thuộc còn lại.
      Không blocker nào khác. Đây là công việc đã biết, không phải công việc phải khám phá.

    -> T-06 REAL DATA
      Blocker THẬT: **BLK-001** — không có đường tới data.binance.vision / api.binance.com.
                    Đây là blocker HẠ TẦNG, agent không tự gỡ được: cần máy/VPS của chủ
                    dự án. Kèm DEC-003: đối chiếu hash `ethdca freeze` trên hai máy.
      Lưu ý: gỡ BLK-001 KHÔNG cho phép chạy T-06 khi GATE-A chưa PASS. Hai nhóm điều kiện
      độc lập, phải thoả cả hai.

    -> GOLDEN RUN
      Lần chạy official đầu tiên CHÍNH LÀ Golden baseline đầu tiên.
      Nó đặt GOLDEN_BASELINE_SHA và đóng H-10; từ đó Blast Radius mới được phép giảm.
      Blocker THẬT: không có blocker riêng — nó là sản phẩm của T-06.

    -> WEB APP DAILY-USE  (CAP-WEBAPP: WP-C1…WP-C4)
      Blocker THẬT: WP-C1 đang READY, độc lập hoàn toàn với lớp A — **chạy song song
                    được ngay bây giờ, không phải chờ GATE-A.**
                    WP-C2 BLOCKED bởi DEC-005 (PENDING, thẩm quyền chủ dự án).
                    WP-C4 chờ WP-A4 ∧ WP-A6.
                    RSK-002 (parity JS/Python) là rủi ro thật của đoạn này.

    -> V1

### 8.1 Một căng thẳng phải nêu, không tự quyết

Trình tự §11 đặt WEB APP DAILY-USE **sau** T-06/GOLDEN RUN. Nhưng `DEC-011` định nghĩa V1
theo web app dùng hàng ngày, còn T-06 là đường **nghiên cứu/verdict**
(`CAPABILITY_REGISTRY` xếp `CAP-WEBAPP` là "KHÔNG nằm trên Vertical Slice — song song").

Đọc thẳng: nếu V1 Acceptance là 10 điểm của `DEC-011`, thì phần lớn 10 điểm đó do
`CAP-WEBAPP` thoả, không phải do T-06. Có thể tồn tại một V1 hợp lệ mà GATE-A/T-06 chưa
xong — trừ khi chủ dự án coi Buy Score đã được backtest xác thực là điều kiện bắt buộc để
tin vào khuyến nghị (điểm 4 của Acceptance).

Phiên này tuân theo trình tự §11 nguyên văn và KHÔNG tự sắp lại roadmap. Nhưng câu hỏi là
thật và nó đổi đường găng một cách vật chất, nên được đưa vào §9 làm quyết định còn thiếu.

### 8.2 Hardening bị loại khỏi đường găng — tường minh

13 mục H-01…H-13 KHÔNG có mục nào trên đường găng V1. Không mục nào chạm A–F. Tất cả giữ
`RE_TRIGGER_CONDITION`; không mục nào bị xoá hay bị coi là đã đóng.

---

## 9. OWNER DECISION CÒN THIẾU

Xếp theo mức chặn đường găng.

1. **`F-E2A1R3-05` — phê duyệt COMPLETION GATE CHANGE PROPOSAL cho WP-A4** (§5.3).
   Chặn: blocker V1 DUY NHẤT, và chặn T-06. **Ưu tiên cao nhất.**
2. **WP-A1 — disposition cho 3 hạng mục LEGACY_GATE** (§4.2): mỗi hạng mục chọn
   `ACCEPT_AS_IS` / `DESCOPE` / `OWNER_EXTENSION`. Lưu ý §4.3: 2 trong 3 có đường đóng ở
   chi phí budget = 0.
3. **Integration** — chọn A / B / C (§7.4), kèm: tích hợp vào default branch hiện tại hay
   lập trunk `main` trước (§7.3). Khuyến nghị = A.
4. **Trình tự V1** — T-06/GATE-A có thật sự là điều kiện tiên quyết của V1 daily-use
   không, hay đường web app chạy song song được (§8.1). Câu này đổi đường găng.
5. **BLK-001** — máy/VPS có mạng tới Binance. Blocker hạ tầng của T-06, agent không gỡ được.
6. **DEC-005** (tồn đọng) — phạm vi công cụ trước verdict. Đang chặn WP-C2.
7. **Glob validator / H-08** (tồn đọng) — `CAP-GOVTOOL` chưa có owner. Sẽ thành vấn đề khi
   GATE-A được đánh giá, vì Exit Criteria viện dẫn "validators PASS" mà hai validator đang
   PASS trên tập rỗng.

---

## 10. XÁC NHẬN PHẠM VI PHIÊN

    PRODUCTION CODE DIFF      = 0
    TEST CODE DIFF            = 0
    TASK REGISTRY DIFF        = 0   (29 task ID trước và sau)
    REPAIR CYCLE COUNT        = 2, KHÔNG ĐỔI
    TASK ID MỚI               = 0
    WP MỚI                    = 0
    GATE WORDING SỬA          = 0
    FROZEN CONTRACT SỬA       = 0
    MERGE                     = KHÔNG
    T-06 / GATE-A CHẠY        = KHÔNG

WP-A1 sau phiên này: `IN_PROGRESS`. CHECK-A1-01…10 `PASS`. CHECK-A1-11 `FAIL`.
GATE-A KHÔNG ĐÓNG. T-06 KHÔNG MỞ. Không thay đổi nào.
