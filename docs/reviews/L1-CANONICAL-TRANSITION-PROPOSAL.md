# L-1 CANONICAL TRANSITION PROPOSAL

Ngày: 2026-09-05
Nhánh: `claude/coindca-l1-transition-prep-32ynvi`
SOURCE: `origin/main` = `867ea9f907212a8c6d92fe7b5a29879a52049ecf` (khớp kỳ vọng của chỉ thị phiên)
Đầu vào audit: `COINDCA_REVIEW_L1_INPUT.md` (tài liệu ngoài repo, đã đối chiếu — xem §2)

Loại phiên:
CHUẨN BỊ QUYẾT ĐỊNH (decision prep). KHÔNG phải phiên thực thi.

Production diff:
**EMPTY.** Phiên này chỉ thêm đúng một file dưới `docs/reviews/`.
`PROJECT/PRODUCTION_PATHS.md` §2 xếp `docs/**` NGOÀI production path.

Phiên này KHÔNG làm (kiểm chứng lại ở §12):
tạo `DEC-041`; tạo/đăng ký task ID mới; sửa `src/`, `webapp/`, `tests/`, `docs/spec/`;
đổi tên trường production; sửa `PROJECT/*`; mở bất kỳ hạng mục nào trong §7; thiết kế
data model L-1; mở V2.2; chạy thí nghiệm chiến lược.

---

## 1. Tóm tắt điều hành

`DEC-040` đã chọn **L-1**. Phiên này KHÔNG xem xét lại lựa chọn đó.

Câu hỏi của phiên là: **cần tối thiểu những chỉnh sửa canonical nào để việc thiết kế sản phẩm
L-1 sau này không còn bị ràng buộc bởi các giả định productization V2.1.5 đã lỗi thời?**

Kết luận: cần **một** Owner Decision (`DEC-041`) chạm **bảy** bề mặt. Trong đó **ba bề mặt có
thẩm quyền CAO HƠN** `SHARED_PRODUCT_ROADMAP.md` mà tài liệu audit đầu vào không nêu — và đó
mới là thứ thực sự chặn thiết kế L-1:

| # | Bề mặt | Hạng thẩm quyền (`AGENTS.md` §1) | Audit có nêu? |
|---|---|---|---|
| A | `PROJECT/CAPABILITY_REGISTRY.md` §1 — Vertical Acceptance Slice | 7 | **KHÔNG** |
| B | `PROJECT/PROJECT_PROFILE.md` — "Mục tiêu cuối của chủ dự án" | 7 | **KHÔNG** |
| C | `DEC-011` — V1 Daily-Use Acceptance (10 điểm) | 12 | **KHÔNG** |
| D | `PROJECT/PROJECT_PROGRESS.md` — trạng thái 6 hạng mục + stale | 7 | Một phần |
| E | `docs/spec/*_V2_1_5.md` — tuyên bố frozen research | 13 | CÓ |
| F | `SHARED_PRODUCT_ROADMAP.md` | **không nằm trong bảng thẩm quyền** | CÓ |
| G | `app_development_allowed` ở tầng PROJECT | 7 | CÓ |

**Bề mặt A là bề mặt chặn thật sự.** `governance/v4/CORE/CAPABILITY_MODEL.md` bắt mọi đơn vị
công việc mới phải trả lời câu hỏi số 1: *"Is it required for the current Vertical Acceptance
Slice to run correctly?"*. Vertical Acceptance Slice đang khai báo trong
`CAPABILITY_REGISTRY.md` §1 là lát cắt V2.1.5 (`Dữ liệu thật → 18 bước → Gate 1/2/3 → VERDICT`),
đã chạy **đúng một lần** (`T-06`, `DEC-031`) và bị Master Index §6 cấm chạy lại. Vì vậy **không
một hạng mục L-1 nào trả lời được câu hỏi số 1** — mọi công việc L-1 hiện không định tuyến được
theo CORE. Đây là ràng buộc cứng, không phải vấn đề thẩm mỹ, và nó phải được gỡ TRƯỚC khi có
phiên thiết kế L-1.

---

## 2. Đối chiếu tài liệu audit đầu vào với repo

Chỉ thị phiên yêu cầu kiểm chứng các khẳng định governance/state của tài liệu audit trước khi
dựa vào chúng. Đã kiểm chứng trực tiếp trên `867ea9f`.

### 2.1 XÁC NHẬN ĐÚNG

| Khẳng định audit | Bằng chứng trong repo |
|---|---|
| `Current Task` = WP-B1 IN_PROGRESS (thực tế DONE) | `PROJECT_PROGRESS.md:742-753` vs `DEC-034` |
| `Next Recommended Task` = WP-A6/WP-A1 (cả hai DONE) | `PROJECT_PROGRESS.md:758-765` vs bảng roadmap |
| `Current Phase` = "gỡ BLK-001" (đã RESOLVED) | `PROJECT_PROGRESS.md:734-740` vs `PROJECT_PROGRESS.md:1085` (BLK-001 RESOLVED tại `DEC-031`) |
| `Current Task Snapshot` = WP-D1/S005 | `PROJECT_PROGRESS.md:937-941` |
| `Recent Decisions` dừng ở DEC-017 | `PROJECT_PROGRESS.md:1546-1573`; thực tế đã tới `DEC-040` |
| T-03 = VERIFYING từ 02/09 | `docs/tasks/T-03-...md:4-5`; bảng roadmap dòng T-03 |
| WP-C4 PLANNED, dependency đã DONE | Ready Gate `WP-C4-...md:166-168` còn `[ ]` cho WP-A3/A4/A6 — cả ba đã DONE |
| T-11 PLANNED (bảng) / BLOCKED (văn bản) | Bảng roadmap dòng T-11 = `PLANNED`; `DEC-040` §D = `BLOCKED` |
| `RCP-001` header "CHƯA ÁP DỤNG" | `ROADMAP_CHANGE_PROPOSAL_001.md:4`; nhưng `PROJECT_PROGRESS.md:826` có mục "Roadmap Change Applied — RCP-001" |
| `REVIEW_BUDGET_LEDGER` §3 ghi T-06 còn `PLANNED` | `REVIEW_BUDGET_LEDGER.md:393-394` ("hiện `PLANNED` và bị chặn bởi GATE-A lẫn `BLK-001`") vs `T-06 = DONE` (`DEC-031`) |
| Session ID: S014 trùng 2 phiên; thiếu S007/S008/S021 | `docs/sessions/` — có `S014-t09b-firebase-implementation.md` VÀ `S014-wp-a6-thu-tu-18-buoc.md`; không có S007/S008/S021 |
| `firestore.rules` placeholder `OWNER_UID_REQUIRED` | `firestore.rules:101` |
| `firebase.json` hosting không scope site | `firebase.json` — khối `hosting` không có khoá `site` |
| Bug B1 (fill zone không tỷ giá) | `webapp/app_logic.js:271` — `var amount = vndCost > 0 ? Math.min(vndCost, remaining) : remaining;` |
| Bug B2 (mua không tỷ giá → pool không trừ) | `webapp/app_logic.js:280-283` — nhánh `else if (vndCost > 0 && pool)`; `deducted = Math.min(vndCost, pool.a)` |
| Bug B3 (`currentMonth()` = key lớn nhất) | `webapp/app_logic.js:129-132` |
| Bug B4 (ngày giao dịch = lúc bấm nút) | `webapp/app_logic.js:287` — `ts: new Date().toISOString()` |
| `SHARED_PRODUCT_ROADMAP` §3.2 "Active strategy: ETH Strategy V2.1.5" | `SHARED_PRODUCT_ROADMAP.md:83` |

### 2.2 SAI — phải đính chính trước khi dùng

**C1 — `DEC-035` KHÔNG phê duyệt PA-2.** Đây là đính chính quan trọng nhất, vì audit §1.1 và
§5.1(a) dựng lập luận "đóng DEC-005 bằng PA-2 (đã de-facto)" trên khẳng định này.

Sự thật: `DEC-035` phê duyệt **PA-A** — *"phân xử HẸP chỉ cho `WP-C2`"*. Nguyên văn Owner:
*"APPROVE PA-A CHO DEC-035, VÀ CHẤP NHẬN ADR-001."* (`PROJECT_DECISIONS.md:2622`).
Câu mà audit trích — *"thực tế đã là mô hình vận hành từ T-09A/T-09B/DEC-021"* — nằm bên trong
phần mô tả của phương án **PA-B**, tức phương án **KHÔNG được chọn** (`PROJECT_DECISIONS.md:2578-2581`).
`DEC-035` còn nói tường minh, hai lần: *"`DEC-005` bản thân **vẫn PENDING**"* và *"quyết định này
KHÔNG đóng `DEC-005`, KHÔNG mở `T-08`"*.

Hệ quả: **không tồn tại tiền lệ canonical nào đã chấp nhận PA-2.** Xem §8.

**C2 — `SHARED_PRODUCT_ROADMAP.md` §2.3 không "cấm" dự án như audit mô tả.** §2.3 mở đầu bằng
*"This roadmap MUST NOT, **by itself**…"* — đây là điều khoản **tự giới hạn của chính tài liệu
roadmap**, không phải lệnh cấm áp lên dự án. Một Owner Decision hoàn toàn có thể thay đổi
accounting/persistence; §2.3 chỉ nói bản thân roadmap không được tự làm điều đó.

Thêm ba dữ kiện audit bỏ sót, đều làm **giảm** quy mô hành động cần thiết:
- §2.3 đoạn cuối: *"If an active repository governance rule conflicts with this document, the
  active repository's canonical authority wins… The conflict should then be reconciled
  explicitly rather than silently changing scope."* — roadmap **tự khai báo mình là bên thua**
  và tự yêu cầu một bản đối chiếu tường minh.
- §12 đoạn mở: *"This checkpoint is descriptive and must not override newer repository evidence."*
- `SHARED_PRODUCT_ROADMAP.md` **không xuất hiện trong bảng thẩm quyền `AGENTS.md` §1** (13 hạng).
  Nó không có hạng thẩm quyền nào trong repo này.

Hệ quả: việc cần làm **không phải** "mở khoá" (audit §5.1c) — vì không có khoá nào cần mở.
Việc cần làm là **ghi một bản đối chiếu tường minh**, đúng thủ tục mà chính §2.3 đòi. Xem §6.

**C3 — Audit bỏ sót ba bề mặt thẩm quyền cao hơn.** Bề mặt A/B/C ở §1. Xem §5.

**C4 — Audit bỏ sót một mâu thuẫn trạng thái mới.** `WP-C3`: file task ghi `Status: PLANNED`
(`docs/tasks/WP-C3-partial-fill-tang-san-pham.md:5`), trong khi bảng roadmap và
`CAPABILITY_REGISTRY.md` §2 ghi `READY` (theo `DEC-036`). `DEC-036` chỉ được áp vào hai nơi,
sót file task. Đây là stale thật, cùng loại với danh sách §9.

**C5 — Đề xuất "bỏ review budget ledger" (audit §5.3) mâu thuẫn CORE.** `AGENTS.md` §3:
*"**Budget does not reset.** Not across session, branch, repair cycle, subtask, work package,
child task or sibling task."* `STATE_AUTHORITY.md` xếp "Review budget ledger" là một lớp state
có holder canonical duy nhất; `AGENTS.md` §1 xếp nó hạng 11. Xoá sổ ledger là **xoá state
canonical**, không phải giảm nghi thức. Phương án tuân thủ ở §11.

**C6 — Ngụ ý hạ profile (audit §5.3) đi ngược chính lập luận của `PROJECT_PROFILE.md`.**
Profile PRODUCT được chọn (`DEC-001`) vì ba lý do, trong đó lý do 1 là *"Dữ liệu nghiệp vụ
thật… Mất hoặc sai dữ liệu này là thiệt hại thật"* và lý do 2 là *"Tính toán tài chính trọng
yếu"*. Dưới L-1, sản phẩm **chính là** sổ cái tiền thật — hai lý do đó mạnh hơn chứ không yếu
đi. Lý do 3 (spec V2.1.5 tự áp kỷ luật PRODUCT) là lý do duy nhất suy yếu. Không đề xuất hạ
profile. Xem §11.

### 2.3 KHÔNG kiểm chứng lại trong phiên này (và vì sao)

- `pytest` 677/678, `ethdca synth → run gate1`, build `webapp`, harness `engine.js + app_logic.js`:
  chỉ thị phiên giới hạn *"Run applicable docs/state validators only if files are changed."*
  Phiên không sửa production nên các số liệu này không ảnh hưởng kết luận nào ở đây.
- Đánh giá của audit §2 (verdict FAILED không phải vì thanh quá cao): **ngoài phạm vi** —
  `DEC-040` đã chốt, phiên này không xem xét lại L-1.

---

## 3. CONFLICTS CONFIRMED — danh sách điều khoản

Mỗi dòng là một điều khoản còn hiệu lực, mâu thuẫn với `DEC-040`.

### 3.1 Thẩm quyền hạng 7 — `PROJECT/CAPABILITY_REGISTRY.md`

| ID | Vị trí | Nguyên văn / nội dung | Vì sao mâu thuẫn L-1 |
|---|---|---|---|
| CF-01 | §1, dòng 21-27 | Vertical Acceptance Slice = `Dữ liệu thật (Binance) → lineage → dataset official → pipeline 18 bước → Gate 1/2/3 → run record → VERDICT` | Đây là lát cắt V2.1.5, đã chạy xong một lần và bị cấm chạy lại. `CAPABILITY_MODEL.md` bắt mọi công việc mới trả lời "có cần cho lát cắt hiện tại chạy đúng không?" → **mọi hạng mục L-1 đều trả lời KHÔNG** → không định tuyến được. **Đây là ràng buộc chặn thật sự.** |
| CF-02 | §2, dòng `CAP-WEBAPP` | Owner task = `WP-C1, WP-C2, WP-C3, WP-C4`; "Nằm trên Vertical Slice? = KHÔNG (song song)" | Dưới L-1, app web **chính là** sản phẩm, phải nằm TRÊN lát cắt, không còn "song song". Hai thành viên (`WP-C3`, `WP-C4`) sẽ NOT_APPLICABLE (§7). |

### 3.2 Thẩm quyền hạng 7 — `PROJECT/PROJECT_PROFILE.md`

| ID | Vị trí | Nguyên văn | Vì sao mâu thuẫn L-1 |
|---|---|---|---|
| CF-03 | § "Bối cảnh dự án" → "Mục tiêu cuối của chủ dự án" | *"…phát cảnh báo dựa trên các chỉ báo phân tích đã được đặc tả trong bộ spec (`docs/spec/01_PRODUCT_SPEC_V2_1_5.md` và `docs/spec/02_STRATEGY_SPEC_V2_1_5.md`)"* | Khai báo mục tiêu cuối của dự án **trỏ đích danh vào spec V2.1.5**. Dưới L-1, spec V2.1.5 là research artifact đóng băng, không còn là spec sản phẩm. Đây là hạng 7, cao hơn roadmap. |
| CF-04 | § "Bối cảnh dự án" → "Tên dự án" | *"ETH DCA Operating System — V2.1.5"* | Tên dự án gắn cứng số hiệu version đã FAILED. Cosmetic hơn CF-03 nhưng cùng gốc. |
| CF-05 | § "Hệ quả bắt buộc" điểm 4 | *"schema phải bám `docs/spec/04_DATA_MODEL_V2_1_5.md`"* | Ràng buộc data model L-1 vào data model V2.1.5. Đây chính là "obsolete productization assumption" mà chỉ thị phiên yêu cầu gỡ. |

### 3.3 Thẩm quyền hạng 12 — `PROJECT/PROJECT_DECISIONS.md` `DEC-011`

`DEC-011` là Owner Decision còn hiệu lực, chưa từng bị supersede.

| ID | Vị trí | Nguyên văn | Vì sao mâu thuẫn L-1 |
|---|---|---|---|
| CF-06 | V1 Daily-Use Acceptance điểm 4 | *"Buy Score / regime / budget / recommendation được hiển thị."* | Là **tiêu chí chấp nhận V1 bắt buộc**. Dưới L-1, Buy Score/regime hạ xuống research mô tả và `recommendation` biến mất. Một tiêu chí chấp nhận đòi hiển thị recommendation trực tiếp mâu thuẫn với *"Dừng productization chiến lược"*. |
| CF-07 | V1 Daily-Use Acceptance điểm 2, 3 | *"Lấy được dữ liệu ETH thật cần thiết"*; *"Pipeline chạy end-to-end."* | "Pipeline" ở đây là pipeline 18 bước V2.1.5. Dưới L-1 nó không nằm trên đường sản phẩm. |
| CF-08 | Tiêu chí `BLOCKING V1`, mục A | *"A. làm recommendation/Buy Score sai;"* | Trở thành **vacuous** dưới L-1 (không còn recommendation). Để nguyên thì trục phân loại `BLOCKING V1` mất một chiều mà không ai nhận ra. Các mục B/C/E/F vẫn đúng nguyên và **phải giữ** — B/C là lõi tiền đúng của L-1. |

### 3.4 Thẩm quyền hạng 13 — `docs/spec/`

| ID | Vị trí | Nguyên văn | Ghi chú |
|---|---|---|---|
| CF-09 | `05_IMPLEMENTATION_PLAN_V2_1_5.md` §1 | *"Không build dashboard hoặc full app trước khi research prototype hoàn thành và verdict cho phép."* | Xem §6.2 — cách đọc đúng, KHÔNG cần sửa spec |
| CF-10 | cùng file §7 | *"INCONCLUSIVE và DO NOT BUILD không thể đi tiếp sang phase app."* | như trên |
| CF-11 | cùng file §9 tiêu đề | *"App MVP — chỉ sau verdict cho phép"* | như trên |

### 3.5 Không có hạng thẩm quyền — `SHARED_PRODUCT_ROADMAP.md`

| ID | Vị trí | Nguyên văn | Mức |
|---|---|---|---|
| CF-12 | §2.2 điểm 2 | *"Current **verified** strategy remains ETH Strategy V2.1.5."* | **Sai sự thật**, không chỉ lỗi thời: V2.1.5 = FAILED, verdict `DO_NOT_BUILD` (`DEC-031`, 2026-09-03) — có TRƯỚC ngày roadmap ghi (2026-09-02 → commit sau). Nằm trong mục "effective immediately". |
| CF-13 | §3.2 | *"Active strategy: **ETH Strategy V2.1.5**"*; *"ETH remains the strategy asset currently implemented and **validated**"* | Sai sự thật (từ "validated") + lỗi thời (từ "Active") |
| CF-14 | §3.2 "Expected ownership includes" | `Buy Score`; `regime`; `buy zones/ladders`; `ETH strategy recommendations` | Bốn hạng mục ownership thuần V2.1.5 |
| CF-15 | §5.2 | CoinDCA giữ semantic mạnh cho `Buy Score`, `regime`, `GO/WAIT`, `ladder status` | `ladder status`, `GO/WAIT` biến mất dưới L-1 |
| CF-16 | Stage 1, "CoinDCA Stream — V1 production completion" điểm 3-6 + khối `Conceptual path` | `Real market data → … → Buy Score / regime → recommendation / budget → web → record trade` | **Định nghĩa V1 = productization V2.1.5** — chính là thứ `DO_NOT_BUILD` cấm |
| CF-17 | §10 "Target end state" | *"CoinDCA answers: 'Given the **validated** crypto strategy…'"* | Tiền đề sai |
| CF-18 | §12 "Current checkpoint" | *"Current active strategy: **ETH Strategy V2.1.5**."* | Lỗi thời — nhưng §12 tự khai *"must not override newer repository evidence"* |

### 3.6 KHÔNG mâu thuẫn (đã kiểm, để Owner khỏi phải kiểm lại)

- `SHARED_PRODUCT_ROADMAP.md` §7 (thứ tự ưu tiên) — tương thích hoàn toàn với L-1; ưu tiên 1
  *"prevent incorrect financial/accounting results"* đúng là ưu tiên số 1 của L-1.
- §8 (idea intake), §9 (non-goals), §11 (agent start rule) — tương thích.
- `DEC-011` OD-1 (PRODUCT INTENT: cá nhân, một người dùng, hằng ngày) — **tương thích và nên
  giữ nguyên**; nó là nền cho việc giảm nghi thức ở §11.
- `DEC-011` V1 Acceptance điểm 1, 5, 6, 7, 8, 9, 10 — tương thích, nên giữ nguyên. Điểm 5/6/7
  (*ghi giao dịch · holdings/average cost/monthly budget/purchase history đúng · dữ liệu tồn tại
  sau reload*) **chính là mô tả sản phẩm L-1**.
- `DEC-003` (dữ liệu tổng hợp không bao giờ dùng ra verdict) — không liên quan L-1, giữ nguyên.
- `DEC-021` (Personal Tool Simplification Principle) — tương thích, hữu ích cho L-1.

---

## 4. V2.1.5 TREATMENT — đóng băng làm authority nghiên cứu/lịch sử

### 4.1 Đề xuất

Tuyên bố (bằng `DEC-041`, không sửa một chữ nào trong `docs/spec/`):

    docs/spec/*_V2_1_5.md            = FROZEN HISTORICAL RESEARCH AUTHORITY
    src/eth_dca_os/**                = FROZEN HISTORICAL RESEARCH IMPLEMENTATION
    V2.1.5 validation                = FAILED            [KHÔNG ĐỔI, VĨNH VIỄN]
    T-06 official verdict            = DO_NOT_BUILD      [KHÔNG ĐỔI]
    can_proceed_to_app (V2.1.5)      = false             [KHÔNG ĐỔI]

Nghĩa chính xác của "frozen historical research authority":
1. **Vẫn là authority** cho câu hỏi *"V2.1.5 đã được đặc tả và chạy như thế nào"* — trích dẫn
   được, không bị hạ giá trị, không xoá.
2. **KHÔNG còn là spec sản phẩm.** Không còn là nguồn của yêu cầu sản phẩm, tiêu chí chấp nhận,
   hay ràng buộc data model cho công việc mới (gỡ CF-05).
3. **Không sửa.** Master Index §6 cấm vá tại chỗ; freeze này **củng cố** lệnh cấm đó chứ không
   nới. Mọi khiếm khuyết đã biết (S-001, S-002, S-003) được **ghi chú kèm**, không được sửa.
4. **Không kế thừa.** Đúng nguyên văn `DEC-040`: *"must not inherit V2.1.5 validation status"*.

### 4.2 Vì sao freeze KHÔNG cần sửa `docs/spec/`

Đây là điểm phân kỳ có chủ ý với audit §1.3 (*"cần tuyên bố rõ… spec V2.1.5 = frozen research
artifact"* — audit ngụ ý đụng vào spec).

Master Index §6 cấm sửa spec dựa trên kết quả official run. Một dòng "FROZEN" viết vào chính
file spec là một sửa đổi phát sinh từ kết quả run. Cách đúng: tuyên bố freeze **ở tầng
`PROJECT/`** (`CAPABILITY_REGISTRY.md` + `PROJECT_PROFILE.md`), nơi có thẩm quyền hạng 7 và
không bị Master Index §6 ràng buộc. Spec giữ nguyên bit-for-bit; **trạng thái** của spec đổi.

Kết quả: `docs/spec/` diff = 0, và CF-09/CF-10/CF-11 không cần đụng tới — xem §6.2.

---

## 5. ROADMAP IMPACT — sửa đổi canonical tối thiểu

Nguyên tắc: **sửa đổi tối thiểu**, và **không sửa lén thẩm quyền** (`CLAUDE.md` § Scope
Expansion; chỉ thị phiên: *"Do not silently edit authority"*). Mọi thay đổi dưới đây chỉ được
thực thi bởi một phiên khác SAU KHI Owner phê duyệt `DEC-041`.

### 5.1 `PROJECT/CAPABILITY_REGISTRY.md` §1 — bắt buộc, ưu tiên cao nhất

Hành động: **thêm** một lát cắt L-1; **giữ nguyên** lát cắt V2.1.5 dưới nhãn lịch sử (không xoá
— `STATE_AUTHORITY.md` và tiền lệ `BLK-001` đều giữ lịch sử).

Đề xuất khung lát cắt L-1 (mô tả nghiệp vụ, chưa phải thiết kế — thiết kế thuộc phiên spec L-1):

    Ngân sách tháng do người dùng đặt
      -> lịch mua đã lên kế hoạch
        -> người dùng ghi một giao dịch thật (có NGÀY do người dùng nhập)
          -> sổ cái + giá vốn tính lại từ (số dư đầu kỳ + toàn bộ trades)
            -> 4 con số dashboard (ngân sách · đã đầu tư · còn lại · ngày mua kế tiếp)
              -> lưu bền qua reload/restart

Lát cắt này **cắt ngang module** (UI → logic sổ sách → persistence) đúng định nghĩa Vertical
Slice, và mọi hạng mục L-1 sẽ trả lời được câu hỏi số 1 của `CAPABILITY_MODEL.md`.

**Chưa đủ để READY.** `CAPABILITY_MODEL.md` §II.1 đòi lát cắt mang toạ độ nghiệp vụ thật (một
bản ghi có thật, con số kỳ vọng cụ thể, oracle bằng công thức). Phiên này **không được bịa dữ
liệu nghiệp vụ** (§II.2). Vì vậy ghi:

    END_TO_END_ACCEPTANCE = PENDING_OWNER_DATA
    MISSING_DATA:     ngân sách tháng thật (VND); ngày lịch DCA thật; số dư đầu kỳ
                      (ETH đang có, USDT sẵn, giá vốn cũ, asOf); ít nhất một giao dịch
                      thật đủ trường (ngày, USDT, price, fee, vndRate) và giá vốn TB
                      kỳ vọng tính tay
    REQUIRED_SOURCE:  chủ dự án (sổ sách cá nhân thật)
    OWNER_INPUT_REQUIRED: đúng các trường trên, kèm MỘT con số giá vốn TB kỳ vọng để làm oracle

Đây là outcome **hợp lệ** theo §II.2 và có giá trị hơn một mô tả trông đầy đủ nhưng rỗng.

### 5.2 `PROJECT/PROJECT_PROFILE.md` — bắt buộc

- CF-03: viết lại "Mục tiêu cuối" → công cụ web cá nhân theo dõi kỷ luật DCA (ngân sách · lịch ·
  ghi giao dịch · giá vốn/tài sản). Bỏ trỏ tới `01_PRODUCT_SPEC_V2_1_5` / `02_STRATEGY_SPEC_V2_1_5`
  làm nguồn yêu cầu; nếu cần thì trỏ lại như **tham chiếu lịch sử**.
- CF-05: điểm 4 § "Hệ quả bắt buộc" → bỏ ràng buộc *"schema phải bám `04_DATA_MODEL_V2_1_5.md`"*;
  thay bằng: schema L-1 bám spec L-1 (chưa tồn tại) và `03_DATA_MODEL_RULES.md`.
- CF-04: tên dự án — **đề xuất DEFER**. Đổi tên chạm rất nhiều nơi; `SHARED_PRODUCT_ROADMAP.md`
  §2.2(3) và §9 đều cấm mass-rename. Chỉ đổi dòng "Tên dự án" nếu Owner muốn, không lan ra.
- **Giữ nguyên**: profile = PRODUCT (`DEC-001`), toàn bộ lập luận chọn PRODUCT, Provider Mapping.
  Xem C6 (§2.2) và §11.

### 5.3 `PROJECT/PROJECT_DECISIONS.md` `DEC-011` — bắt buộc, và phải làm ĐÚNG CÁCH

`DEC-011` là Owner Decision, append-only (`STATE_AUTHORITY.md`). **Không được sửa tại chỗ.**
`DEC-041` phải **supersede một phần** `DEC-011` bằng cách ghi tường minh:

- CF-06: điểm 4 → `SUPERSEDED BY DEC-041`. Thay bằng: *"4. Ngân sách tháng · đã đầu tư · còn
  lại · ngày mua kế tiếp được hiển thị."*
- CF-07: điểm 2, 3 → `NOT_APPLICABLE_TO_L1` (giữ hiệu lực cho mọi đánh giá lịch sử V2.1.5).
- CF-08: tiêu chí `BLOCKING V1` mục A → `NOT_APPLICABLE_TO_L1`. **Mục B, C, E, F giữ nguyên
  nguyên văn** — B (sai tiền/ngân sách/giá vốn/holding) và C (mất/hỏng lịch sử giao dịch) là
  lõi của L-1 và là căn cứ cho E2 ở §11. Mục D (dữ liệu thị trường thật qua pipeline đúng) →
  `NOT_APPLICABLE_TO_L1` trừ khi tab Research được bật.
- **Giữ nguyên tuyệt đối**: OD-1 PRODUCT INTENT; "Ràng buộc đối xứng" (*không được hạ một
  finding chỉ vì "dự án cá nhân"*); điểm 1, 5, 6, 7, 8, 9, 10.

### 5.4 `SHARED_PRODUCT_ROADMAP.md` — sửa đổi TỐI THIỂU

Vì tài liệu này (a) không có hạng thẩm quyền trong `AGENTS.md` §1, (b) tự khai báo mình thua
canonical authority của repo, và (c) §12 tự khai *"must not override newer repository evidence"*
— **không cần và không nên viết lại nó**. Đề xuất tối thiểu, đúng thủ tục mà chính §2.3 đòi
(*"reconciled explicitly"*):

**Bắt buộc — sửa hai khẳng định SAI SỰ THẬT** (không phải "unlock", mà là đính chính):
- CF-12 §2.2(2): `"Current verified strategy remains ETH Strategy V2.1.5."` →
  `"ETH Strategy V2.1.5 was evaluated and FAILED validation (official verdict DO_NOT_BUILD,
  DEC-031). It is a frozen historical research authority, not the active product strategy.
  CoinDCA's product direction is L-1 (DEC-040)."`
- CF-13 §3.2: bỏ từ `validated`; `"Active strategy: ETH Strategy V2.1.5"` →
  `"Active strategy: none. Product direction = L-1 simple-DCA discipline (DEC-040).
  V2.1.5 = frozen historical research."`

**Bắt buộc — một khối đối chiếu**, chèn ngay đầu §12 (hoặc thành §13):

    ## Reconciliation — 2026-09-05 (DEC-041)
    This roadmap predates DEC-031/DEC-040. Per §2.3 (last paragraph) and §12, the coin
    repository's canonical authority wins and the conflict is reconciled here explicitly.
    Superseded for CoinDCA: §2.2(2), §3.2, §3.2 ownership list (Buy Score, regime,
    buy zones/ladders, ETH strategy recommendations), §5.2 (ladder status, GO/WAIT),
    Stage 1 "CoinDCA Stream — V1 production completion" items 3-6 and its Conceptual path,
    §10 ("validated crypto strategy"), §12 ("Current active strategy").
    Unchanged and still in force: §7 priority order, §8 idea intake, §9 non-goals,
    §11 agent start rule, and all Finance-stream content.
    Authority: PROJECT/PROJECT_DECISIONS.md DEC-041.

**KHÔNG đề xuất**: viết lại Stage 1 nội dung CoinDCA; đụng bất kỳ nội dung Finance nào (repo
khác, ngoài phạm vi phiên và ngoài phạm vi Owner ở đây); đổi §7/§8/§9/§11.

### 5.5 `PROJECT/PROJECT_PROGRESS.md`

Bảng roadmap chuẩn: đổi trạng thái 6 hạng mục theo §7; dọn stale theo §9. Sau đó **bắt buộc**
chạy `python governance/scripts/governance/sync_easy_roadmap.py` (`ROADMAP_SYNC_STANDARD.md`;
`LO_TRINH_DE_HIEU.md` là file sinh, cấm sửa tay).

---

## 6. APP DEVELOPMENT — tách quyền "app" khỏi quyền "chiến lược"

### 6.1 Giữ nguyên trường production

    can_proceed_to_app = false        [GIỮ NGUYÊN — kết quả productization chiến lược V2.1.5]

`src/eth_dca_os/verdict.py:37` tính `"can_proceed_to_app": v == "BUILD"` — hàm thuần của verdict.
Với verdict `DO_NOT_BUILD` nó là `false` và phải mãi mãi là `false`.

**KHÔNG đổi tên trong phiên này** (chỉ thị phiên tường minh). Ghi nhận để Owner biết đầy đủ:
audit §5.2 đề xuất đổi tên `can_proceed_to_app` → `strategy_productization_allowed`. Đó là sửa
production path (`src/eth_dca_os/`), sẽ tiêu delivery change budget, và chạm `verdict.py` — file
đã có 2 vòng E2 fresh tìm ra lỗ hở fail-open (`E2-B1-F02`) và một chùm test hồi quy
(`tests/test_wp_b1_e2_fresh_fail_repair*.py`) khoá đúng tên trường này. **Khuyến nghị: KHÔNG đổi
tên, cả sau này.** Trường này là kết quả đóng băng của một verdict lịch sử; đổi tên nó chỉ tạo
rủi ro cho một giá trị không bao giờ đổi nữa. Ngữ nghĩa được làm rõ bằng **văn bản** ở §6.3, rẻ
hơn và an toàn hơn.

### 6.2 `app_development_allowed = true` — biện minh canonical

Đề xuất thêm ở tầng `PROJECT/PROJECT_PROFILE.md` (KHÔNG phải trong `verdict.py`, KHÔNG phải đầu
ra của backtest):

    app_development_allowed = true          # tầng PROJECT, do Owner đặt (DEC-041)
    phạm vi:  sản phẩm L-1 (sổ cái DCA + lịch + giá vốn) — KHÔNG bao gồm tầng tự
              động hoá chiến lược V2.1.5

**Biện minh canonical — nằm ngay trong chính spec V2.1.5, không cần sửa spec:**

`05_IMPLEMENTATION_PLAN_V2_1_5.md` §5, dòng `DO NOT BUILD`, nguyên văn:

> **"Dừng productization chiến lược. Chọn benchmark đơn giản hơn hoặc thiết kế lại thành
> version mới."**

Ba điều đọc ra được, tất cả đều là nguyên văn spec:
1. Lệnh dừng có **định ngữ**: *"productization **chiến lược**"* — không phải "dừng mọi việc app".
2. *"Chọn benchmark đơn giản hơn"* là **hành động BẮT BUỘC** (cột "Hành động bắt buộc") mà spec
   tự chỉ định cho verdict `DO_NOT_BUILD`. L-1 **chính là** hành động đó. Vậy làm L-1 là **tuân
   thủ** IM §5, không phải lách nó.
3. Đối chiếu dòng `BUILD` cùng bảng: *"Tiến sang **app MVP single-user dùng đúng strategy engine
   đã khóa**."* → "app MVP" mà IM §9 và IM §7 nói tới được **định nghĩa ngay trong bảng** là app
   **chạy strategy engine V2.1.5 đã khoá**.

Hệ quả: CF-09 / CF-10 / CF-11 **không phải mâu thuẫn cần gỡ** — chúng chỉ cấm đúng một thứ: app
chạy strategy engine V2.1.5. Sản phẩm L-1 (sổ cái + lịch, Buy Score hạ xuống mô tả, không
recommendation) **không phải app đó**. Vì vậy:

- **`docs/spec/` diff = 0.** Không sửa, không diễn giải lại, không mở V2.2.
- Không mâu thuẫn Master Index §6.
- Hai quyền tách bạch **không chồng lấn**:

| Quyền | Giá trị | Ai đặt | Ý nghĩa |
|---|---|---|---|
| `can_proceed_to_app` | `false` (vĩnh viễn) | `verdict.py`, từ verdict `DO_NOT_BUILD` | Cấm productization **chiến lược V2.1.5** |
| `app_development_allowed` | `true` | Owner, `DEC-041`, tầng PROJECT | Cho phép sản phẩm **L-1** — đúng hành động IM §5 quy định cho `DO_NOT_BUILD` |

### 6.3 Ranh giới phải ghi kèm (chống trượt dần)

`app_development_allowed = true` chỉ an toàn nếu có ranh giới tường minh. Đề xuất ghi kèm trong
`DEC-041`:

    ĐƯỢC PHÉP dưới L-1:
      ngân sách/lịch/kỷ luật DCA · ghi-sửa-xoá giao dịch có ngày người dùng nhập ·
      giá vốn & holdings tính lại từ (số dư đầu kỳ + trades) · treasury VND/USDT + P2P ·
      quỹ dự phòng giải ngân THỦ CÔNG có ghi lý do · persistence/backup/export-import ·
      đối chiếu lịch sử DESCRIPTIVE (giá mua TB thực tế vs kế hoạch DCA thuần) ·
      hiển thị hồi cứu Buy Score có nhãn DESCRIPTIVE

    KHÔNG ĐƯỢC PHÉP (vẫn thuộc can_proceed_to_app = false):
      recommendation/GO-WAIT/Action box · ladder/zone/unlock/spacing sinh ra hành động ·
      bất kỳ tự động hoá nào kích hoạt hoặc gợi ý MUA từ một score/regime ·
      quỹ dự phòng tự giải ngân theo tín hiệu · tuyên bố bất kỳ edge nào ·
      dùng lại trạng thái validation của V2.1.5

Ranh giới này **là** tập tiêu chí phân định mà `DEC-005`/PA-2 đòi nhưng chưa bao giờ được viết
(xem §8) — lần này viết ra, và neo vào L-1 chứ không vào cửa verdict.

---

## 7. PHÂN LOẠI CÔNG VIỆC ROADMAP CŨ

Nhắc lại: chỉ thị phiên — *"Do not start any of them."* Không hạng mục nào được mở ở đây;
`DEC-041` cũng không mở hạng mục nào.

| Hạng mục | Trạng thái hiện tại | **Phân loại đề xuất** | Lý do |
|---|---|---|---|
| **T-08** — Đặc tả lớp cảnh báo | `PLANNED`; bị `DEC-005` chặn | **REDEFINE_FOR_L1** | Nhu cầu gốc ("được nhắc") sống sót; **nội dung** thì không — "cảnh báo theo chỉ báo" là khái niệm V2.1.5. Dưới L-1, cảnh báo = nhắc lịch DCA (audit §4.3 đề xuất export `.ics`, rẻ hơn nhiều). Đặc tả V2.1.5 bên trong T-08 = `NOT_APPLICABLE_TO_V2_1_5`. |
| **T-10** — Triển khai lớp cảnh báo | `PLANNED`; sau T-08, T-09B, WP-C4 | **REDEFINE_FOR_L1** | Cùng lý do T-08. Thêm: chuỗi phụ thuộc phải dựng lại — `WP-C4` (một dependency) sẽ `NOT_APPLICABLE` (dưới đây), nên dependency cũ không còn nghĩa. Xếp lịch **sau** khi spec L-1 tồn tại. |
| **T-11** — Tầng tự động hoá chiến lược đầy đủ | `PLANNED` (bảng) / `BLOCKED` (`DEC-040` §D) | **NOT_APPLICABLE_TO_V2_1_5** | Rõ nhất trong sáu. Điều kiện gồm `verdict = BUILD`, mà `DEC-040` §E xác lập điều kiện này **không bao giờ thoả được nữa dưới V2.1.5**. `DEC-040` §E đã dùng đúng cụm *"not applicable vĩnh viễn dưới V2.1.5"* trong phần văn bản — phân loại này chỉ **ghi trạng thái cho khớp lời văn đã có**, không phải quyết định mới. Đồng thời đóng mâu thuẫn `PLANNED` vs `BLOCKED`. |
| **WP-C3** — Xử lý mua một phần ở tầng sản phẩm | `READY` (bảng, `DEC-036`) / `PLANNED` (file task — xem C4) | **NOT_APPLICABLE_TO_V2_1_5** | "Partial fill" là khái niệm **zone/ladder**: một zone có `target_vnd`, fill được một phần. Dưới L-1 không có zone, không có ladder, không có target per-zone — một giao dịch chỉ là một giao dịch với số tiền bất kỳ. Completion Gate đã FROZEN (2026-08-23) viết theo zone → không áp được. Mối lo nghiệp vụ ("mua ít hơn kế hoạch") được **mô hình dữ liệu L-1 hấp thụ tự nhiên** qua `trades[]`, không cần cơ chế riêng. |
| **WP-C4** — Mở rộng parity JS/Python | `PLANNED`; Ready Gate còn 3 dòng `[ ]` cho dependency đã DONE | **NOT_APPLICABLE_TO_V2_1_5** | Parity chỉ có nghĩa khi **cả hai** bản cài đặt còn là authority. Dưới L-1: `src/eth_dca_os/` thành research đóng băng; `engine.js` thành optional/descriptive. Các đại lượng trong gate FROZEN (regime, ladder, vốn Smart) đều biến mất. **Phần dư**: nếu tab Research được bật thì parity OSCORE `engine.js` ↔ `score.py` mới có nghĩa lại — ghi làm `RE_TRIGGER_CONDITION` trong `HARDENING_BACKLOG.md`, **KHÔNG** phải task (`REVIEW_PROTOCOL.md`: finding không phải task). |
| **WP-D2** — Đề xuất mở V2.2 cho khiếm khuyết đặc tả | `READY`; không phụ thuộc; đóng S-001/S-002/S-003 | **NOT_APPLICABLE_TO_V2_1_5** | Đầu ra là đề xuất **V2.2 của V2.1.5**. `DEC-040` từ chối mở V2.2, **và** chỉ thị Owner mạnh hơn thế: *"Any future timing/reallocation strategy must be treated as a separate research hypothesis… must not inherit V2.1.5 validation status"* — tức công việc chiến lược tương lai **không phải V2.2 của V2.1.5**, nên tiền đề của WP-D2 chết. Khiếm khuyết spec trong một artifact **đóng băng lịch sử** thì được **ghi chú**, không được sửa (Master Index §6). **Điều kiện kèm theo**: tuyên bố freeze ở §4.1 phải mang theo danh sách khiếm khuyết đã biết (S-001, S-002, S-003), nếu không ba finding này thành mồ côi. |

Không hạng mục nào được xếp `DEFER`. Đây là kết quả thật, không phải bỏ sót: `DEFER` nghĩa là
"nội dung còn đúng, chỉ dời thời điểm" — không hạng mục nào trong sáu rơi vào đó, vì tất cả đều
hoặc phải đổi nội dung, hoặc chết cùng V2.1.5.

Bốn hạng mục còn dang dở **không** thuộc phạm vi câu hỏi, ghi để bức tranh đủ:
`T-05` (`PLANNED` — gắn với `DEC-005`, xem §8), `T-03` (`VERIFYING` — xem §9),
`WP-D1`/`WP-C1`/`WP-C2` (đã `DONE`).

---

## 8. DEC-005 — PA-2 có thực sự giải quyết không?

### 8.1 Trả lời: **KHÔNG.** Đề xuất: **GIỮ `PENDING`.**

Chỉ thị phiên: *"Do not close it merely for housekeeping."* Đây là kết luận theo nội dung, không
theo tiện lợi.

### 8.2 Bốn lý do

**L1 — Tiền đề của audit sai.** Audit §5.1(a) đề xuất *"đóng DEC-005 bằng PA-2 (đã de-facto)"*,
dựa trên khẳng định `DEC-035` đã thừa nhận PA-2. `DEC-035` phê duyệt **PA-A**, không phải PA-2;
câu được trích nằm trong mô tả phương án **PA-B đã bị loại**; và `DEC-035` nói hai lần rằng
`DEC-005` vẫn `PENDING` (chi tiết: C1, §2.2). Không có tiền lệ canonical nào ủng hộ PA-2.

**L2 — PA-2 chưa bao giờ có nội dung thi hành.** `DEC-005` định nghĩa PA-2 là *"ghi nhận chính
thức ranh giới… **kèm tiêu chí phân định rõ ràng để không trượt dần qua ranh giới**"*. Bộ tiêu
chí đó **không tồn tại ở bất kỳ đâu trong repo** — đã tìm. Phê duyệt "PA-2" hôm nay là phê duyệt
một cái nhãn mà phần vận hành duy nhất của nó còn trống. Đúng theo `AGENTS.md` cuối §7 và
`CLAUDE.md` § Final Rule (*"prove completion through artifacts and evidence, not through
narrative confidence"*), đó không phải một quyết định thi hành được.

**L3 — Câu hỏi của `DEC-005` đã hết hiệu lực theo thời gian.** Tiêu đề nguyên văn: *"Phạm vi
công cụ được phép xây **trước khi có verdict**"*, và `Can Revisit After: T-05… và sau đó là T-07
(đọc verdict thật)`. Cả hai điều kiện đã xảy ra: verdict tồn tại (`DO_NOT_BUILD`, `DEC-031`) và
`T-07` đã thực thi (`DEC-040`). **Cửa sổ tiền-verdict đã đóng.** Câu hỏi còn sống hôm nay là câu
khác — *"được xây gì **dưới L-1**"* — và `DEC-005` chưa bao giờ hỏi câu đó. Trả lời câu B rồi dán
nhãn "đã đóng câu A" là closure giả.

**L4 — `DEC-040` dành riêng vấn đề này.** *"DEC-005 unchanged unless separately resolved"* và §F:
*"Quyết định này KHÔNG resolve `DEC-005`"*. Một resolve riêng là **được phép**, nhưng phải là
resolve thật, đủ nội dung — không phải một dòng dọn dẹp kèm trong quyết định khác.

### 8.3 Vì sao giữ `PENDING` không gây thiệt hại

Tác dụng chặn duy nhất còn lại của `DEC-005` là chặn `T-08` (`DEC-035`, `DEC-040` §F). Theo §7,
`T-08` được xếp `REDEFINE_FOR_L1` — nội dung V2.1.5 của nó ngừng áp dụng. **Thứ mà `DEC-005`
đang chặn thì tự nó đang được cho nghỉ.** Áp lực "phải đóng `DEC-005` để đi tiếp" là áp lực
tưởng tượng: `DEC-041` cấp quyền xây L-1 qua `app_development_allowed` (§6), một đường độc lập,
không đi qua `DEC-005`.

### 8.4 Điều `DEC-041` NÊN làm với `DEC-005` (không phải đóng)

1. Giữ `DEC-005 = PENDING`; giữ `T-05 = PLANNED`.
2. Ghi tường minh: **phạm vi hiệu lực còn lại của `DEC-005` chỉ là câu hỏi tiền-verdict của
   V2.1.5**; nó **không** chi phối phạm vi sản phẩm L-1 — L-1 do `app_development_allowed` +
   ranh giới §6.3 chi phối.
3. Ghi tường minh rằng ranh giới §6.3 **là** bộ tiêu chí phân định mà PA-2 hình dung nhưng chưa
   bao giờ được viết — nay được viết cho L-1. Đây là lý do thực chất khiến `DEC-005` mất áp lực,
   thay vì bị đóng bằng thủ tục.
4. **Tuỳ chọn cho Owner** (không phải khuyến nghị của phiên này): nếu Owner muốn dứt điểm, đường
   đúng **không** phải phê duyệt PA-2, mà là ghi `DEC-005 = SUPERSEDED_BY_DEC-041` với lý do L3
   ở trên — câu hỏi hết hiệu lực vì bối cảnh, chứ không phải vì được trả lời. Phiên này **không
   khuyến nghị** điều đó: `DEC-005` `PENDING` không tốn gì, và giữ nguyên thì lịch sử đọc chính
   xác hơn.

---

## 9. STALE STATE — bề mặt cosmetic, tách khỏi quyết định sản phẩm

Chỉ thị phiên: *"Identify stale/cosmetic surfaces separately from product decisions.
Do not create tasks for cleanup."*

Đây **không** phải quyết định sản phẩm. Đây là state đã sai so với các `DEC` đã tồn tại. Sửa
chúng là **thi hành** quyết định cũ, không phải ra quyết định mới, nên **không cần task ID**
(`CAPABILITY_MODEL.md` § "Reasons That Are NEVER Sufficient To Create A New Task").

| # | Bề mặt | Đang ghi | Đúng phải là | Thẩm quyền đã có sẵn |
|---|---|---|---|---|
| ST-01 | `PROJECT_PROGRESS.md` `Current Task` | `WP-B1 — IN_PROGRESS` | `WP-B1 DONE`; không có task đang chạy | `DEC-034` |
| ST-02 | `PROJECT_PROGRESS.md` `Current Phase` | "Kế tiếp: gỡ `BLK-001`" | `BLK-001 RESOLVED`; `GATE-A`/`GATE-B` CLOSED; `T-06`/`T-07` DONE; giai đoạn = chuyển tiếp L-1 | `DEC-031`, `DEC-028`, `DEC-038`, `DEC-040` |
| ST-03 | `PROJECT_PROGRESS.md` `Next Recommended Task` | `WP-A6` / `WP-A1` | Cả hai DONE 09-03; đề xuất kế tiếp = spec L-1 (sau `DEC-041`) | `DEC-028` |
| ST-04 | `PROJECT_PROGRESS.md` `Current Task Snapshot` | `WP-D1`, S005 (24/08) | `WP-D1 DONE`; snapshot đã lạc hậu 12 ngày | S005 |
| ST-05 | `PROJECT_PROGRESS.md` `Recent Decisions` | dừng ở `DEC-017` | đã tới `DEC-040` (thiếu 23 mục) | `PROJECT_DECISIONS.md` |
| ST-06 | Bảng roadmap dòng `T-03` | `VERIFYING` từ 02/09 | Mọi REQUIRED/RECOMMENDED check PASS tại WP-C1; chỉ chờ Owner chuyển `DONE` (`STATE_AUTHORITY.md` dành `DONE` cho Owner) | `docs/tasks/T-03-...md:349-351` |
| ST-07 | `RSK-003` | còn mở | Treo **chỉ vì** `T-03` chưa `DONE` (`PROJECT_PROGRESS.md:1277`) — đóng theo ST-06 | như trên |
| ST-08 | Bảng roadmap dòng `T-11` | `PLANNED` | mâu thuẫn với `DEC-040` §D (`BLOCKED`) — cả hai sai sau §7 (`NOT_APPLICABLE_TO_V2_1_5`) | `DEC-040` |
| ST-09 | `docs/tasks/WP-C3-...md:5` | `PLANNED` | `READY` — `DEC-036` đã áp vào bảng roadmap và `CAPABILITY_REGISTRY` nhưng **sót file task** (phát hiện mới, §2.2 C4) | `DEC-036` |
| ST-10 | `ROADMAP_CHANGE_PROPOSAL_001.md:4` header | "**CHƯA ÁP DỤNG — CHỜ PHÊ DUYỆT**" | Đã APPROVED (`DEC-007`) và đã áp dụng (`PROJECT_PROGRESS.md:826` "Roadmap Change Applied — RCP-001") | `DEC-007` |
| ST-11 | `REVIEW_BUDGET_LEDGER.md:393-394` §3 | "`T-06`… hiện `PLANNED` và bị chặn bởi GATE-A lẫn `BLK-001`" | `T-06 DONE`; nhận định "chưa có Golden tái lập được" thì **vẫn đúng** và phải giữ | `DEC-031` |
| ST-12 | `docs/sessions/` — ID phiên | `S014` dùng cho 2 phiên; thiếu `S007`/`S008`/`S021` | Ghi chú đính chính vào `docs/sessions/README.md`. **KHÔNG đổi tên file** — session ID bị trích dẫn khắp `PROJECT_DECISIONS.md` | — |

**Tách bạch:** ST-01…ST-05, ST-10, ST-11, ST-12 là **thuần cosmetic** (state hiển thị lệch, đã
có thẩm quyền, không ai phải quyết gì). ST-06/ST-07 cần **một chữ ký Owner** (`DONE` là quyền
Owner) — nhỏ nhưng không phải cosmetic. ST-08/ST-09 **giao thoa** với quyết định sản phẩm ở §7
và phải làm cùng lúc, không tách.

**Không đề xuất task nào cho toàn bộ §9.**

---

## 10. RÀNG BUỘC TRIỂN KHAI L-1 (chỉ ghi nhận — KHÔNG sửa)

Chỉ thị phiên: *"Record them as L-1 implementation constraints only. Do NOT repair Firebase /
app_logic.js accounting bugs / auth / data model / UI."* Không một dòng nào trong `webapp/`,
`firestore.rules`, `firebase.json` bị sửa ở phiên này.

Định tuyến governance: theo `REVIEW_PROTOCOL.md` + `PRODUCTION_PATH_RULE.md`, các mục dưới đây
là **ràng buộc thiết kế** cho phiên spec L-1, KHÔNG phải finding BLOCKING mới, KHÔNG phải task.
Chỗ neo canonical đúng của chúng là `PROJECT/HARDENING_BACKLOG.md` (đang có 40 mục mở) kèm
`RE_TRIGGER_CONDITION`, cộng với việc spec L-1 phải trả lời tường minh.

### 10.1 FIREBASE — bốn ràng buộc

| ID | Ràng buộc | Bằng chứng | Hệ quả cho spec L-1 |
|---|---|---|---|
| FB-1 | Project Firebase dùng chung `tinphatcontent` với app Content. Rules của Content dùng `signedIn() = request.auth != null`, mà CoinDCA đòi bật Anonymous Auth → **bất kỳ khách vô danh nào** cũng ghi được `users/{uid}`, `contents`, `schedules`, `fb_queue`, `audit_logs` của Content | `DEC-023` (ràng buộc dùng chung, Owner-fixed); `docs/reviews/T-09B-shared-rules-merge.md` §OBSERVATION | Rủi ro thuộc **app Content**, không phải CoinDCA. Nhưng nó do CoinDCA gây ra. Spec L-1 phải chốt: tách project riêng, hay Owner chấp nhận rủi ro cho Content bằng một quyết định tường minh. |
| FB-2 | `firebase.json` khối `hosting` **không có khoá `site`** → `firebase deploy` từ repo này **đè** Hosting site mặc định của Content | `firebase.json` (đã đọc); `webapp/README.md` cảnh báo | Ràng buộc **vận hành**, không phải code. Bất kỳ hướng dẫn deploy L-1 nào cũng phải xử lý trước. |
| FB-3 | `firestore.rules:101` còn placeholder `OWNER_UID_REQUIRED`, trong khi production đã deploy UID thật → **deploy lại từ repo sẽ tự khoá chính Owner ra ngoài** | `firestore.rules:101` | Cạm bẫy vận hành có thật, xác nhận. Spec L-1 phải nói UID production đến từ đâu (biến môi trường / bước thủ công / tách project). |
| FB-4 | Anonymous UID nằm trong IndexedDB trình duyệt → xoá site data / đổi máy / cửa sổ ẩn danh = **mất quyền truy cập dữ liệu của chính mình**, phải sửa rules + redeploy bằng terminal | `H-23`; `DEC-021` xếp recovery **OUT OF SCOPE V1** — có chủ ý, không phải sót | **Điểm đau số 1** cho một app cá nhân dùng cả điện thoại lẫn máy tính. `DEC-021` là quyết định tiền-L-1, ra khi app chưa phải sản phẩm chính. Dưới L-1 app **là** sản phẩm → spec L-1 phải đặt lại câu hỏi này (audit §4.5 đề xuất Google Sign-in một tài khoản). Đây là quyết định Owner, **không** phải agent tự đảo `DEC-021`. |

Thêm: production hiện chạy dữ liệu **synthetic rev 4** — chưa đồng tiền thật nào đi qua app.
Điều này **giảm** rủi ro migration cho L-1 (không có dữ liệu thật cần bảo toàn ngay) và nên được
ghi rõ, vì nó cho phép data model v2 mạnh tay hơn.

### 10.2 KẾ TOÁN — ràng buộc từ `webapp/app_logic.js`

Đã xác minh trực tiếp trên mã 4/10 mục (B1, B2, B3, B4 — xem §2.1). Sáu mục còn lại lấy từ audit,
**chưa kiểm chứng độc lập trong phiên này**, và được ghi đúng như vậy.

| ID | Vị trí | Hiện tượng | Trạng thái |
|---|---|---|---|
| B1 | `app_logic.js:271` | Fill zone không nhập tỷ giá → `amount = remaining` → mua 1 USDT cũng đánh dấu zone `EXECUTED` và chuyển toàn bộ target R→D | **XÁC MINH** |
| B2 | `app_logic.js:280-283` | Mua không tỷ giá → `deducted = 0`, pool không bị trừ. Mua vượt `pool.a` → phần dư không trừ vào đâu → "available" ảo | **XÁC MINH** |
| B3 | `app_logic.js:129-132` | `currentMonth()` = key tháng **lớn nhất**, không phải tháng lịch; nhập nhầm vốn cho tháng tương lai → mọi thao tác trừ vào tháng đó | **XÁC MINH** |
| B4 | `app_logic.js:287` (và `:168`, `:218`) | Ngày giao dịch = `new Date()` lúc bấm nút — không nhập được ngày thật | **XÁC MINH** |
| B5 | toàn bộ | Không edit/delete giao dịch, P2P, contribution, ngày giá | audit |
| B6 | — | Không nhập được số dư đầu kỳ | audit |
| B7 | `:125` vs `:1432` | `monthKey` giờ local, `today`/`daysSince` UTC → 00:00–07:00 ngày 1 hằng tháng mặc định tháng trước | audit |
| B8 | `:1420` | Wipe chỉ `confirm()` một lần rồi ghi state rỗng lên Firestore, không snapshot trước | audit |
| B9 | — | VND lưu float (`102000.00000000001`) | audit |
| B10 | `engine.js:21-59` | Rolling window đếm **số dòng**, không theo lịch → bỏ nhập ngày nào thì MA200/High365/ADR30 lệch âm thầm | audit |

**Ba ràng buộc thiết kế rút ra** (dành cho spec L-1, không phải đơn sửa lỗi):

1. **`date` do người dùng nhập là trường bắt buộc trên mọi giao dịch** (B4, B7) — không phải
   tính năng thêm; nó quyết định cost basis theo thời gian đúng hay sai. Toàn bộ ngày theo
   `Asia/Ho_Chi_Minh` (config đã có `Asia/Ho_Chi_Minh` nhưng không dùng).
2. **Cost basis / holdings / PnL phải TÍNH LẠI từ `(số dư đầu kỳ + toàn bộ trades)` mỗi lần
   render**, không cộng dồn vào state (B1, B2, B5, B6). Đây là ràng buộc **kiến trúc**: chỉ mô
   hình tính-lại mới làm edit/delete an toàn, và nó xoá bỏ **cả một lớp** lỗi cộng dồn cùng lúc
   thay vì vá từng cái.
3. **Tháng là tháng lịch, không phải key lớn nhất; tiền VND lưu integer** (B3, B9).

**Cảnh báo còn hiệu lực:** khuyến nghị "dừng dùng app với tiền thật" **vẫn đúng** cho tới khi
pivot L-1 hoàn tất. Lưu ý phân biệt: `RSK-003` escalation đã được gỡ tại WP-C1/T-09A cho **hai
lỗi ladder V-01/V-02**; B1–B10 là **nhóm khác**, chưa từng được vá.

### 10.3 KHÔNG sửa gì trong phiên này

Xác nhận: 0 dòng trong `webapp/`, `src/`, `firestore.rules`, `firebase.json`, `tests/`.
Không auth, không data model, không UI. `git status` sạch ngoài đúng một file `docs/reviews/`.

---

## 11. GOVERNANCE — bộ tối thiểu cho L-1

Chỉ thị phiên nêu mục tiêu: một spec sản phẩm canonical · một bề mặt tiến độ/state · decision log
chỉ cho Owner decision thật · E2 chỉ cho financial correctness / persistence / migration · không
chạy strategy-validation suite trên công việc UI L-1 thông thường.

Đây là **đề xuất cho Owner**; agent không tự cấp quyền giảm nghi thức (`CLAUDE.md` § Adapter
Constraints).

### 11.1 Bộ tối thiểu đề xuất

| Vai trò | File | Ghi chú |
|---|---|---|
| Entry point | `AGENTS.md` | giữ |
| CORE | `governance/v4/CORE/` (7 file) | giữ — project-agnostic, không phải nghi thức V2.1.5 |
| Profile | `PROJECT/PROJECT_PROFILE.md` | giữ, sửa CF-03/CF-05 (§5.2) |
| **Spec sản phẩm canonical** | **spec L-1 (chưa tồn tại)** | **≤ 5 trang**; nguồn duy nhất của yêu cầu L-1; thay `docs/spec/*_V2_1_5.md` ở vai trò này |
| State/roadmap | `PROJECT/PROJECT_PROGRESS.md` (+ `LO_TRINH_DE_HIEU.md` sinh ra) | giữ — `STATE_AUTHORITY.md` đòi đúng một nguồn |
| Capability | `PROJECT/CAPABILITY_REGISTRY.md` | giữ, cập nhật §1 lát cắt (§5.1) |
| Decision log | `PROJECT/PROJECT_DECISIONS.md` | giữ — **chỉ Owner decision thật** |
| Production paths | `PROJECT/PRODUCTION_PATHS.md` | giữ — cần cho việc đo "production diff" |
| Hardening | `PROJECT/HARDENING_BACKLOG.md` | giữ — nơi neo §10 |
| Budget | `PROJECT/REVIEW_BUDGET_LEDGER.md` | **giữ** — xem 11.3 |

### 11.2 Giảm nghi thức được — mà không đụng CORE

Bốn điều audit muốn, **đã hợp lệ sẵn** theo luật hiện hành, không cần đổi governance:

1. **UI L-1 không tự động Tier C/`xhigh`.** Hard floor này gắn với category
   `accounting_financial` (`PROJECT_PROFILE.md` § "Hệ quả bắt buộc" điểm 2), không gắn với
   "công việc trong `webapp/`". Việc UI **không** chạm lớp tính tiền thì **không** mang category
   đó → routing tự cho Tier thấp hơn. Chỉ cần chấm `routing_engine.py` trung thực. Ngược lại,
   cost basis / ledger / persistence / migration **vẫn phải** Tier ≥ C, Effort ≥ `high` — và
   dưới L-1 điều đó càng đúng, vì đó **là** sản phẩm.
2. **E2 chỉ cho tiền đúng / persistence / migration** — đúng luật sẵn: `EVIDENCE_STANDARD.md`
   gắn E2 theo Risk và category, không theo mọi task. Tiền lệ đã có: `DEC-037`/`DEC-038` đóng
   `WP-B3`/`WP-B2` **không cần E2 mới** vì gate không đòi E2 ở check nào (`Risk 2/4 → E1`).
   Nên ghi vào `DEC-041` để phiên sau không tự nâng chuẩn.
3. **Suite Python 25 phút không nằm trên đường build app L-1.** `src/eth_dca_os/` thành research
   đóng băng (§4) → test của nó là hồi quy cho một artifact đóng băng, chạy khi chạm vào nó, và
   L-1 không chạm. Không cần đổi luật; chỉ cần freeze ở §4 được ghi nhận.
4. **`PHASE_RELEASE_GATE_STANDARD.md`, `RCP-*` mới, `docs/adr/`** — vẫn còn hiệu lực nhưng
   L-1 gần như không kích hoạt chúng.

### 11.3 Hai điều audit đề xuất mà phiên này KHÔNG khuyến nghị

**(a) "Bỏ review budget ledger" — mâu thuẫn CORE, xem C5 (§2.2).** `AGENTS.md` §3 (*"Budget does
not reset"*) là một trong bốn luật được nêu đích danh là "An agent must not get wrong". Ledger
là hạng 11 và là holder canonical của một lớp state. Xoá nó là xoá state, không phải giảm nghi
thức.

Phương án tuân thủ, đạt gần hết mục tiêu thực tế: **giữ file, thu gọn về những lineage còn
sống.** Dưới L-1, `CAP-PROV`/`CAP-DATA`/`CAP-ENGINE`/`CAP-PIPELINE`/`CAP-MEASURE`/`CAP-ORDER`/
`CAP-VERDICT` đều thuộc research đã đóng băng — budget của chúng thành **lịch sử đóng**, giữ
nguyên số, không bao giờ đụng lại. Chỉ **`CAP-WEBAPP`** còn sống (allowed 2 / used 0 /
remaining 2, Effective Risk `HIGH`) và là lineage root tự nhiên của L-1. Hằng ngày chỉ phải đọc
một dòng. Không reset, không xoá, không mâu thuẫn CORE.

**(b) Hạ profile PRODUCT — không đề xuất, xem C6 (§2.2).** Hai trong ba lý do chọn PRODUCT (dữ
liệu nghiệp vụ thật; tính toán tài chính trọng yếu) **mạnh lên** dưới L-1, vì sổ cái tiền thật
chính là sản phẩm. Chỉ lý do 3 (spec V2.1.5 tự áp kỷ luật PRODUCT) suy yếu. Giữ PRODUCT.
`DEC-011` OD-1 + `DEC-021` (Personal Tool Simplification Principle) đã cho đủ đòn bẩy giảm nghi
thức mà không phải đụng profile.

### 11.4 Cảnh báo về `CAP-WEBAPP` (`ABSORPTION_LIMIT_REACHED` sẽ chạm)

Nếu L-1 được xây dưới lineage `CAP-WEBAPP`, `CAPABILITY_MODEL.md` § Absorption Limit gần như
chắc chắn bị chạm — ngưỡng B (>3 hạng mục hấp thụ vào một baseline đã duyệt) và D (kéo việc
ngoài vertical slice) — vì L-1 viết lại ~60% `app_logic.js` và ~50% `app_shell.html`.

Luật nói rõ: khi chạm, ghi `ABSORPTION_LIMIT_REACHED` và **đưa lên Owner Decision — không tự tạo
task**. Owner chọn A (duyệt phạm vi rộng ra + hệ quả risk/budget) / B (descope) / C (task mới,
ngoại lệ). Nêu ở đây để `DEC-041` **báo trước**, tránh phiên spec L-1 dừng giữa chừng vì một
hard-stop đoán trước được. Phiên này **không** chọn thay Owner.

---

## 12. ĐO CHỐNG SINH SÔI TASK (`CAPABILITY_MODEL.md` §II.9)

Luật đòi **đo trên registry**, không tự chứng nhận. Công cụ:
`governance/scripts/governance/task_registry_snapshot.sh`.

    SET A — task ID trong registry (bảng roadmap, PROJECT_PROGRESS.md)
      BEFORE = 28      AFTER = 28
    SET B — task ID có Task Spec dưới docs/tasks/
      BEFORE = 22      AFTER = 22

    new_registered_task_ids                  = 0   (danh sách: rỗng)
    proposals_created                        = 0
    owner_assignment_required_entries_added  = 0

Phiên này thêm đúng một file, `docs/reviews/L1-CANONICAL-TRANSITION-PROPOSAL.md`, dưới
`docs/reviews/` — **không** phải vùng đăng ký task (`CAPABILITY_MODEL.md` §II.5: nhắc tên task ID
trong một phân tích/đề xuất **không** phải đăng ký). Sáu hạng mục ở §7 đã tồn tại trong registry
từ trước; §7 **phân loại lại**, không tạo mới.

`DEC-041` như đề xuất **cũng không** tạo task ID mới.

---

## 13. TRẠNG THÁI VALIDATOR

Phiên chỉ thêm một file dưới `docs/reviews/` (không phải production path, không phải state file).
Đã chạy các validator áp dụng được:

    validate_structure.py     PASS   (27 required paths)
    validate_project_state.py PASS
    validate_governance.py    PASS   (7 core, 7 project, 2 adapters, 5 hard-stops,
                                      26 source invariants, 3 budget lineage roots,
                                      40 hardening items, 13 production path rows,
                                      22 task files)

Không chạy `sync_easy_roadmap.py` — `PROJECT_PROGRESS.md` không đổi ở phiên này. Nó **bắt buộc**
phải chạy ở phiên thi hành `DEC-041` (§5.5).

Không chạy `pytest` / `ethdca` — không có thay đổi production nào để kiểm chứng, và chỉ thị phiên
giới hạn ở docs/state validator.

`branch_authority_check.sh` báo `FAIL — attached branch has no upstream` (nhánh chưa từng được
push). Mọi kiểm tra nội dung của nó đều sạch: `ahead of default = 0`, `tracked worktree = CLEAN`,
`production diff = EMPTY`, `INTEGRATION_DECISION_REQUIRED = NO`. Upstream được thiết lập bởi
`git push -u` của chính phiên này.

### 13.1 Cạm bẫy đo lường — ref `main` cục bộ bị cũ (ghi để phiên sau không sập bẫy)

Trong môi trường phiên này, ref `main` **cục bộ** đứng ở `cb75f9d`, **sau `origin/main` 70 commit**
(`origin/main` = `HEAD` = `867ea9f`). Hệ quả: lệnh đo budget canonical của
`PRODUCTION_PATHS.md` nếu chạy với baseline `main` sẽ báo **24 file / +13.866 / −422** — một
"production diff" hoàn toàn ảo, thực chất là 70 commit lịch sử đã merge.

Đo đúng, với baseline `origin/main`:

    git diff --shortstat origin/main -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    -> RỖNG

Quy tắc cho mọi phiên sau: baseline đo budget/diff là **`origin/main` sau khi fetch**, KHÔNG phải
ref `main` cục bộ. Điều này khớp ghi chú đã có trong `PROJECT_PROGRESS.md`
(*"Branch authority từ đây: mọi phiên mới branch từ `origin/main` sau khi fetch"*) và với
`REVIEW_BUDGET_LEDGER.md` §2.1 — nơi một mốc SHA sai đã từng bị ghi nhận là gây sai số đo.

---

## 14. THỨ TỰ THI HÀNH ĐỀ XUẤT (sau khi Owner duyệt)

Không phải task. Là thứ tự để một phiên khác thi hành `DEC-041` mà không tự mâu thuẫn.

1. Ghi `DEC-041` vào `PROJECT/PROJECT_DECISIONS.md` (append-only).
2. `CAPABILITY_REGISTRY.md` §1 — thêm lát cắt L-1 + `PENDING_OWNER_DATA` (§5.1). **Làm trước**,
   vì mọi định tuyến sau đó phụ thuộc nó.
3. `PROJECT_PROFILE.md` — CF-03, CF-05, `app_development_allowed = true` (§5.2, §6.2).
4. `PROJECT_PROGRESS.md` — phân loại §7 + dọn stale §9 → chạy `sync_easy_roadmap.py`.
5. `docs/tasks/WP-C3-...md` — ST-09; `ROADMAP_CHANGE_PROPOSAL_001.md` — ST-10;
   `REVIEW_BUDGET_LEDGER.md` — ST-11 + thu gọn 11.3(a); `docs/sessions/README.md` — ST-12.
6. `SHARED_PRODUCT_ROADMAP.md` — hai đính chính + khối Reconciliation (§5.4).
7. Chạy `validate_project_state.py`, `validate_governance.py`, `validate_structure.py`,
   `validate_easy_roadmap.py`, `validate_routing.py`.
8. **DỪNG.** Phiên spec L-1 là phiên riêng, và nó cần dữ liệu `PENDING_OWNER_DATA` ở bước 2.

---

## OWNER DECISION REQUIRED

Cần chủ dự án quyết định. Agent **không** được tự thi hành bất kỳ mục nào dưới đây.

Ba điểm phiên này **phân kỳ với tài liệu audit đầu vào**, xin đọc trước khi duyệt:
1. `DEC-035` phê duyệt **PA-A**, không phải PA-2 → đề xuất **GIỮ `DEC-005 = PENDING`** (§8),
   ngược với audit §5.1(a).
2. Bề mặt chặn thật là **Vertical Acceptance Slice** trong `CAPABILITY_REGISTRY.md` §1, cùng
   `PROJECT_PROFILE.md` và `DEC-011` — cả ba **cao hơn** `SHARED_PRODUCT_ROADMAP.md`, và audit
   không nêu (§1, §3).
3. **Không** đề xuất bỏ `REVIEW_BUDGET_LEDGER.md`, **không** đề xuất hạ profile PRODUCT — cả hai
   mâu thuẫn CORE / mâu thuẫn chính lập luận của `PROJECT_PROFILE.md` (§11.3).

---

### Văn bản `DEC-041` đề xuất

    ## DEC-041 — L-1 CANONICAL TRANSITION: đóng băng V2.1.5 làm research authority;
    ## tách quyền phát triển app khỏi quyền productization chiến lược

    Date:   2026-09-05
    Task:   Không thuộc task nào. Quyết định chuyển tiếp canonical sau DEC-040.
    Báo cáo: docs/reviews/L1-CANONICAL-TRANSITION-PROPOSAL.md

    A. V2.1.5 = FROZEN HISTORICAL RESEARCH AUTHORITY.
       docs/spec/*_V2_1_5.md và src/eth_dca_os/** vẫn là authority cho câu hỏi "V2.1.5
       đã được đặc tả và chạy thế nào", KHÔNG còn là spec sản phẩm, và không còn là
       nguồn yêu cầu/tiêu chí chấp nhận/ràng buộc data model cho công việc mới.
       Không sửa một chữ nào trong docs/spec/ (Master Index §6). Tuyên bố freeze ghi ở
       tầng PROJECT/. Freeze mang theo danh sách khiếm khuyết đã biết S-001/S-002/S-003.
       GIỮ NGUYÊN VĨNH VIỄN, không đổi một chữ:
           V2.1.5 validation            = FAILED
           T-06 official verdict        = DO_NOT_BUILD
           can_proceed_to_app (V2.1.5)  = false

    B. TÁCH HAI QUYỀN.
           can_proceed_to_app      = false  [production, verdict.py, KHÔNG đổi, KHÔNG đổi tên]
           app_development_allowed = true   [PROJECT/PROJECT_PROFILE.md, do Owner đặt]
       Biện minh: 05_IMPLEMENTATION_PLAN_V2_1_5.md §5 dòng DO NOT BUILD quy định
       "Dừng productization CHIẾN LƯỢC. Chọn benchmark đơn giản hơn…" — L-1 CHÍNH LÀ
       hành động bắt buộc mà spec chỉ định. "App MVP" bị IM §7/§9 chặn được chính bảng
       §5 (dòng BUILD) định nghĩa là app "dùng đúng strategy engine đã khoá" — L-1
       không phải app đó. Không sửa spec, không mở V2.2.
       Ranh giới ĐƯỢC PHÉP / KHÔNG ĐƯỢC PHÉP: theo §6.3 của báo cáo, nhập nguyên văn.

    C. VERTICAL ACCEPTANCE SLICE.
       CAPABILITY_REGISTRY.md §1: thêm lát cắt L-1
       (ngân sách tháng → lịch mua → ghi giao dịch có NGÀY người dùng nhập → sổ cái +
        giá vốn tính lại từ (số dư đầu kỳ + trades) → 4 số dashboard → lưu bền);
       giữ lát cắt V2.1.5 dưới nhãn lịch sử, không xoá.
       END_TO_END_ACCEPTANCE = PENDING_OWNER_DATA (§5.1) — Owner cần cấp: ngân sách
       tháng thật, ngày lịch DCA, số dư đầu kỳ, một giao dịch thật đủ trường, và MỘT
       con số giá vốn TB kỳ vọng làm oracle.

    D. SUPERSEDE MỘT PHẦN DEC-011 (không sửa tại chỗ; DEC-011 append-only).
       Điểm 4 V1 Acceptance -> thay bằng "Ngân sách tháng · đã đầu tư · còn lại ·
         ngày mua kế tiếp được hiển thị."
       Điểm 2, 3 -> NOT_APPLICABLE_TO_L1.  Tiêu chí BLOCKING V1 mục A, D -> NOT_APPLICABLE_TO_L1.
       GIỮ NGUYÊN: OD-1 PRODUCT INTENT; ràng buộc đối xứng ("không hạ finding chỉ vì
       dự án cá nhân"); điểm 1,5,6,7,8,9,10; BLOCKING V1 mục B, C, E, F.

    E. PROJECT_PROFILE.md: viết lại "Mục tiêu cuối" (bỏ trỏ 01_PRODUCT_SPEC/02_STRATEGY_SPEC
       làm nguồn yêu cầu); bỏ ràng buộc "schema phải bám 04_DATA_MODEL_V2_1_5.md".
       GIỮ profile = PRODUCT (DEC-001 không đổi). Đổi tên dự án: DEFER.

    F. PHÂN LOẠI CÔNG VIỆC ROADMAP CŨ — không hạng mục nào được MỞ:
           T-08   REDEFINE_FOR_L1            (nhắc lịch DCA, không phải cảnh báo chỉ báo)
           T-10   REDEFINE_FOR_L1            (xếp sau khi spec L-1 tồn tại)
           T-11   NOT_APPLICABLE_TO_V2_1_5   (khớp lời văn DEC-040 §E; đóng mâu thuẫn PLANNED/BLOCKED)
           WP-C3  NOT_APPLICABLE_TO_V2_1_5   (partial fill là khái niệm zone/ladder)
           WP-C4  NOT_APPLICABLE_TO_V2_1_5   (parity dư nghĩa; phần dư -> RE_TRIGGER_CONDITION
                                              trong HARDENING_BACKLOG, KHÔNG phải task)
           WP-D2  NOT_APPLICABLE_TO_V2_1_5   (V2.2-của-V2.1.5 không còn là đường đi; khiếm
                                              khuyết spec được ghi chú theo A, không sửa)

    G. DEC-005 = GIỮ PENDING. T-05 = GIỮ PLANNED.
       PA-2 KHÔNG resolve DEC-005: (1) DEC-035 phê duyệt PA-A chứ không phải PA-2;
       (2) bộ "tiêu chí phân định" mà PA-2 đòi chưa bao giờ được viết; (3) câu hỏi của
       DEC-005 là câu hỏi TIỀN-VERDICT, mà verdict đã tồn tại và T-07 đã thực thi.
       Ghi rõ: hiệu lực còn lại của DEC-005 chỉ phủ câu hỏi tiền-verdict V2.1.5; nó
       KHÔNG chi phối phạm vi L-1 — L-1 do B chi phối. Ranh giới ở B CHÍNH LÀ bộ tiêu
       chí phân định mà PA-2 hình dung, nay được viết cho L-1.

    H. SHARED_PRODUCT_ROADMAP.md — sửa đổi tối thiểu, đúng thủ tục §2.3 tự đòi:
       đính chính hai khẳng định SAI SỰ THẬT (§2.2(2) "verified"; §3.2 "Active/validated"),
       và chèn một khối "Reconciliation — 2026-09-05 (DEC-041)" liệt kê các mục bị
       supersede cho CoinDCA (§2.2(2), §3.2 + danh sách ownership, §5.2, Stage 1 mục 3-6
       + Conceptual path, §10, §12) và các mục GIỮ NGUYÊN (§7, §8, §9, §11, toàn bộ
       nội dung Finance). KHÔNG viết lại tài liệu. KHÔNG đụng nội dung Finance.

    I. DỌN STALE STATE — thi hành các DEC đã có, KHÔNG phải quyết định mới, KHÔNG task:
       ST-01…ST-05 (Current Task/Phase/Next/Snapshot/Recent Decisions),
       ST-08 (T-11), ST-09 (file task WP-C3 PLANNED -> READY, sót từ DEC-036),
       ST-10 (header RCP-001), ST-11 (ledger §3 nói T-06 còn PLANNED),
       ST-12 (ghi chú trùng/thiếu session ID vào docs/sessions/README.md — KHÔNG đổi tên file).
       Sau đó chạy sync_easy_roadmap.py.
       CẦN CHỮ KÝ RIÊNG CỦA OWNER (DONE là quyền Owner): T-03 VERIFYING -> DONE, kéo
       theo đóng RSK-003. Nếu Owner không ký ở đây, hai mục này ở nguyên.

    J. GOVERNANCE CHO L-1: một spec sản phẩm L-1 canonical (≤5 trang, chưa tồn tại);
       một bề mặt state (PROJECT_PROGRESS.md); decision log chỉ cho Owner decision thật;
       E2 chỉ bắt buộc cho tiền đúng / persistence / migration; UI L-1 không chạm lớp
       tính tiền thì không mang category accounting_financial nên không dính hard floor
       Tier C/high; suite Python không nằm trên đường build app L-1.
       GIỮ REVIEW_BUDGET_LEDGER.md (AGENTS.md §3 "Budget does not reset") — chỉ thu gọn
       về lineage còn sống: CAP-WEBAPP (allowed 2 / used 0 / remaining 2), các lineage
       research khác đóng băng theo A, giữ nguyên số, không reset.
       GIỮ profile PRODUCT.
       BÁO TRƯỚC: công việc L-1 dưới CAP-WEBAPP nhiều khả năng chạm ABSORPTION_LIMIT
       (ngưỡng B và D). Khi chạm, ghi ABSORPTION_LIMIT_REACHED và quay lại Owner —
       không tự tạo task.

    K. RÀNG BUỘC TRIỂN KHAI L-1 — ghi nhận, KHÔNG sửa trong phạm vi quyết định này:
       Firebase FB-1..FB-4 (project dùng chung tinphatcontent; firebase.json không scope
       site; firestore.rules:101 placeholder OWNER_UID_REQUIRED; Anonymous UID trong
       IndexedDB = mất quyền khi đổi máy/xoá site data).
       Kế toán B1..B10 trong webapp/app_logic.js (B1-B4 đã xác minh trên mã).
       Ba ràng buộc thiết kế bắt buộc cho spec L-1: (1) date do người dùng nhập là trường
       bắt buộc, mọi ngày theo Asia/Ho_Chi_Minh; (2) cost basis/holdings/PnL TÍNH LẠI từ
       (số dư đầu kỳ + trades), không cộng dồn vào state; (3) tháng = tháng lịch, VND lưu integer.
       Neo canonical: HARDENING_BACKLOG.md + spec L-1. Không task nào được tạo cho chúng.
       Cảnh báo "dừng dùng app với tiền thật" VẪN CÒN HIỆU LỰC tới khi pivot L-1 xong.

    L. KHÔNG mở/không làm: V2.2; WP-C3/WP-C4/WP-D2/T-08/T-10/T-11; thí nghiệm chiến lược;
       rerun T-06; đổi verdict hay can_proceed_to_app; đổi tên trường production; sửa
       Firebase/auth/data model/UI/lỗi kế toán; task ID mới; thiết kế data model L-1.
       Production diff của quyết định này = 0.

---

### Owner cần trả lời

    1. DUYỆT / SỬA / TỪ CHỐI  DEC-041 A–L (duyệt được từng mục)
    2. Mục G (DEC-005 giữ PENDING) — đồng ý, hay muốn ghi SUPERSEDED_BY_DEC-041?
       (phiên này khuyến nghị GIỮ PENDING — §8.4 điểm 4)
    3. Mục I — có ký T-03 VERIFYING -> DONE (kéo theo đóng RSK-003) ngay ở đây không?
    4. Mục C — cấp dữ liệu PENDING_OWNER_DATA ở đây, hay để phiên spec L-1 hỏi?
    5. Mục E — đổi "Tên dự án" trong PROJECT_PROFILE.md ngay, hay DEFER như đề xuất?
    6. FB-4 / DEC-021 — có mở lại câu hỏi recovery đa thiết bị (Google Sign-in một tài
       khoản) cho L-1 không? DEC-021 xếp nó OUT OF SCOPE V1 khi app chưa phải sản phẩm
       chính; dưới L-1 app LÀ sản phẩm. Đây là quyết định Owner, agent không tự đảo DEC-021.

**STOP.** Không thi hành bất kỳ mục nào cho tới khi Owner phản hồi.
