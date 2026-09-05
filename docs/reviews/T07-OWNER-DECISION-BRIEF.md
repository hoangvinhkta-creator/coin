# T-07 Owner Decision Brief

Bản chuẩn bị quyết định cho bước DUYỆT `T-07`. **Phiên soạn brief này KHÔNG ra quyết định thay
chủ dự án, KHÔNG đổi verdict, KHÔNG đổi trạng thái vòng đời task nào.**

| Trường | Giá trị |
|---|---|
| Source HEAD | `53a63c4ac2119b2f10403ff6a198d95f61438eb6` (= `origin/main` tại thời điểm soạn) |
| Nhánh soạn brief | `claude/t-07-decision-prep-1oprq1` (tách từ `origin/main`) |
| Ngày soạn | 2026-09-05 |
| Phạm vi | **DECISION PREPARATION ONLY** — docs-only, production diff = EMPTY |
| Trạng thái `T-07` khi soạn | `READY` — **không đổi bởi tài liệu này** |
| Authority đã đọc | `AGENTS.md` §1–§4; `governance/v4/CORE/{CAPABILITY_MODEL,GOVERNANCE_V4,DELIVERY_LOOP,REVIEW_PROTOCOL,RISK_MODEL,PRODUCTION_PATH_RULE,STATE_AUTHORITY}.md`; `governance/core/{00_SESSION_ORCHESTRATION,ESCALATION_PROTOCOL}.md`; `PROJECT/{PROJECT_PROGRESS,PROJECT_DECISIONS,CAPABILITY_REGISTRY,ROADMAP_CHANGE_PROPOSAL_001,ROADMAP_CHANGE_PROPOSAL_002}.md`; `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`; `docs/spec/{00_MASTER_INDEX,03_BACKTEST_SPEC,05_IMPLEMENTATION_PLAN}_V2_1_5.md`; `docs/CONVENTIONS.md`; `docs/tasks/WP-B1-*.md`; `docs/sessions/S018-*.md`, `S020-*.md` |

> **CẢNH BÁO ĐỌC** — `T-06 = DONE` **KHÔNG** có nghĩa chiến lược thắng. `DEC-031` §F ghi rõ:
> *"`DONE` tuyệt đối không được dùng đồng nghĩa với validation PASS."* Tương tự, `GATE-B = CLOSED`
> là một cổng **thủ tục**, không phải một phán quyết về nội dung verdict (`DEC-038`).

---

## 1. Decision Required — Quyết định cần đưa ra

`T-07` là bước **DUYỆT của con người**: *"đọc verdict và chọn hướng đi"*
(`PROJECT/PROJECT_PROGRESS.md`, dòng roadmap `T-07`). Verdict chính thức của `T-06` là
`DO_NOT_BUILD` và nó **không nằm trong phạm vi quyết định này** — không được đổi, không được diễn
giải lại. Việc chủ dự án phải quyết là: **sau khi V2.1.5 trượt validation, dự án đi tiếp theo
hướng nào trong khuôn khổ mà Implementation Plan §5 (dòng `DO NOT BUILD`) và Master Index §6 cho
phép** — và có ghi nhận `T-07` là `DONE` hay không. Quyết định này quyết chiều đi của lộ trình,
KHÔNG mở `T-11`, KHÔNG đổi `can_proceed_to_app`, KHÔNG đóng `DEC-005`.

---

## 2. Canonical Starting State — Trạng thái đầu vào (kiểm từ repository, HEAD `53a63c4`)

| Hạng mục | Trạng thái | Nguồn thẩm quyền |
|---|---|---|
| `T-06` (official run) | `DONE` — historical governance disposition, **KHÔNG phải validation PASS** | `DEC-031` §A–§G |
| Official verdict | **`DO_NOT_BUILD`**, reasons = `["Gate 1 FAIL", "OOS hard condition FAIL"]` | `DEC-031` §E; `T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2; tag `v2.1.5-official-T06` |
| `can_proceed_to_app` | `false` | `DEC-031` §E; `CONVENTIONS.md` #21(a) |
| V2.1.5 validation | **`FAILED`** | `DEC-031` §E |
| `WP-B1` | `DONE` | `DEC-034` (10/10 REQUIRED PASS, E2 vòng ba PASS) |
| `WP-B2` | `DONE` | `DEC-038` (10/10 REQUIRED PASS, suite 678/678) |
| `WP-B3` | `DONE` | `DEC-037` (8/8 REQUIRED PASS) |
| `GATE-B` | **`CLOSED`** (= `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`) — cổng **thủ tục** | `DEC-038` |
| `T-07` | **`READY`**, CHƯA thực thi | `DEC-038` |
| `T-11` | `BLOCKED` — đòi `T-07 DONE ∧ WP-C2 ∧ WP-C3 ∧ WP-C4 ∧ verdict=BUILD` | `DEC-038`; `PROJECT_PROGRESS.md` §sơ đồ phụ thuộc |
| `WP-C2` | `DONE` | `DEC-036` |
| `WP-C3` | `READY` (chưa mở) | `DEC-036` |
| `WP-C4` | `PLANNED` | roadmap |
| `DEC-005` | **`PENDING`** — vẫn chặn `T-08` | `DEC-005`; xác nhận lại tại `DEC-035`, `DEC-038` |
| `T-08` | bị chặn bởi `DEC-005` | `DEC-038` § Consequence |
| `T-05` (DUYỆT phạm vi) | `PLANNED` — không nằm trên đường găng tới verdict | `DEC-029`, `DEC-030` |
| `WP-D2` (đề xuất V2.2) | `READY`, không phụ thuộc gói nào | roadmap; `RCP-001` |
| `DEC-035` | `RESOLVED / APPROVED` (PA-A + `ADR-001`) | `PROJECT_DECISIONS.md` |

**Ghi nhận bất nhất tài liệu (không sửa ở phiên này).** Cột `Status` của dòng roadmap `T-11`
trong `PROJECT/PROJECT_PROGRESS.md` vẫn ghi `PLANNED`, trong khi phần tường thuật, sơ đồ phụ
thuộc và `DEC-038` đều ghi `T-11 = BLOCKED`. Đây là một sai lệch **trình bày**, không phải sai
lệch trạng thái: mọi nguồn quyết định đều nhất quán là `BLOCKED`. Đề nghị một phiên state-sync
riêng đồng bộ cột này; **không** thuộc phạm vi `T-07`.

---

## 3. What T-06 Tested — `T-06` đã kiểm tra chính xác cái gì

`T-06` là **một lần chạy backtest chính thức trên dữ liệu Binance thật**, dùng đúng bộ tiêu chí
đã đóng băng từ `T-04`/`RCP-002` **trước khi** chạy. Nội dung được kiểm:

| Thành phần | Nội dung | Ngưỡng cứng |
|---|---|---|
| **Gate 1** | Chín cửa sổ pre-OOS multi-anchor, tính `PrimaryMedian` AccumulationEfficiency (AE) theo BT §4.1 | `PrimaryMedian ≥ 102.0` |
| **OOS** (điều kiện cứng riêng) | Giai đoạn out-of-sample tách biệt, mốc bắt đầu 2025-01-01 đã đóng băng; báo `OOS_Months` và cờ `SHORT_OOS` | `AE ≥ 100.0` |
| **Gate 2** | 219 config đã đóng băng (19 ứng viên OFAT − 1 loại = 18 hợp lệ, + 200 LHS), **không** chiều ma sát nào; tìm robust plateau, không tìm global best | `Gate2_PreOOS_PassShare ≥ 0.75` |
| **Gate 3** | 114 config ma sát thực tế; tính NetEdgePct, ImplementationShortfall và attribution ba thành phần; behavioral robustness; stress P2P-unavailable | `realistic NetEdge > 0` |
| **Control F / G** | Random Timing (1000 sim, giữ nguyên tháng + kích thước tranche + profile giải ngân, chỉ random hoá thời điểm mua) và Random Anchor (1000 sim) | nuôi FS-08 |
| **Benchmark A–E** | Monthly DCA và các benchmark đối chiếu, cùng lịch external contribution | nuôi FS-01 |
| **Failure Signals FS-01…FS-12** | 12 tín hiệu chẩn đoán cơ chế (BT §17) | mỗi tín hiệu có ngưỡng riêng, `DEC-033` phê chuẩn giữ nguyên FS-02/FS-07/FS-12 |
| **Verdict** | Áp tự động bảng IM §5 + Failure-signal cap IM §6 | `can_proceed_to_app = (verdict == "BUILD")` |

Định danh của lần chạy: code commit `5228130677e9e9875335eef890b6ed748a384603`, tag annotated
`v2.1.5-official-T06`, `dataset_hash 3150860cb379…`, `dependency_lock_hash 9ea0150fcf27…`,
`master_seed = 42`.

**`T-06` KHÔNG kiểm tra**: mục tiêu thay thế nào khác (ví dụ tối đa hoá ETH so với giữ optionality
tiền mặt), phiên bản chiến lược nào khác, benchmark đơn giản hơn nào khác, hay app/webapp.

---

## 4. What Passed — Cái gì THỰC SỰ đạt (về mặt kỹ thuật)

Nhãn theo `T06_OFFICIAL_EVIDENCE_RECORD.md` §1: **[R]** = REPOSITORY-VERIFIED, **[O]** =
OWNER-REPORTED / EXTERNALLY-VERIFIED.

**(a) Provenance và khả năng tái lập** — `WP-A1` `DONE`, `GATE-A` `CLOSED` (`DEC-028`), sau
Independent E2 vòng BỐN.
- Code commit của official run xác định duy nhất; tag annotated `v2.1.5-official-T06` peel **đúng**
  về commit đó **[R]**.
- `dependency_lock_hash` khai báo = `sha256(pyproject.lock)` thật tại commit đó **[R]**.
- Official run **bị TỪ CHỐI** khi không phân giải được provenance (0 artifact); run non-official
  ghi `provenance_resolved`/`provenance_unresolved` tường minh **[R]** (`WP-A1`, `F-E2A1-03`).

**(b) Định danh dataset** — `dataset_hash` khai báo tái tính **khớp tuyệt đối** khi đưa ba
`file_hash` Owner khai vào đúng thuật toán `_dataset_hash()` tại commit đó, và khớp với message
của git tag **[R]**. Rằng ba `file_hash` đó thực sự là sha256 của dữ liệu Binance thật: **[O]** —
repository không có byte gốc.

**(c) Official eligibility** — `official_eligibility()` trả `(True, "verified")`, tức đã qua đủ
chuỗi: lineage đúng dạng → không trùng/thừa/thiếu series → mỗi series không rỗng →
`source ∈ {binance_bulk_archive, binance_rest}` → độ phủ `missing ≤ 1%` → `verify_lineage()` đối
chiếu `file_sha256` từng file trên đĩa. Ngữ nghĩa của chuỗi này **[R]**; việc bước cuối thực sự
đã chạy trên byte đĩa thật **[O]**.

**(d) Pipeline thực thi** — cả năm record chính thức tồn tại và khai `provenance_resolved=true`,
`provenance_unresolved=[]`: `gate1_eef3d951aaa0`, `gate2_b08da9ba5229`, `gate3_a0099f6bf0c0`,
`random_control_21b7d88e9691`, `baseline_808b61fa5ffe` **[O]**.

**(e) Pre-T06 manifest freeze** — tái lập **hoàn toàn độc lập từ mã + seed, không cần dataset**:
Gate 2 (19/1/18/200/219 + `manifest_hash e34f92ae…`) và Gate 3 (14/100/114 +
`manifest_hash ef30f657…`) — **10/10 giá trị và 2/2 hash KHỚP** **[R]**. Đây là bằng chứng mạnh
rằng việc đóng băng không gian tìm kiếm **trước** khi chạy là có thật.

**(f) Sinh evidence đầy đủ** — `WP-A5` (`DEC-025`) đã tạo đường sinh thật cho ba đại lượng trước
đó **chưa từng được sinh** (`opportunity_cap_hit_share` FS-02, `regime_advantage_share` FS-12,
`adjacent_config_flip` FS-06). Kết quả: official run có **`UNKNOWN: []`** — cả 12 Failure Signal
đều được đánh giá, không cái nào bị bỏ trống **[O, nhất quán với ngưỡng [R]]**.

**(g) Nhất quán nội tại với ngưỡng đã đóng băng** — cả bốn kết quả gate, các Failure Signal và
verdict Owner khai đều **nhất quán tuyệt đối** với ngưỡng cứng trong `gates.py`/`verdict.py`/
`failure_signals.py` tại commit đó; không phát hiện mâu thuẫn nội bộ nào **[R]** (S018 §2.1).
Phép toán FS-12 (`net_advantage = −1.0935215802236702`, `share = 0.5806…`) tái tính **khớp tới
bit cuối** **[R]**.

**(h) Hạ tầng chất lượng đóng sau official run** (lớp B/C — không phải bằng chứng về chính con số
của official run, xem §10): `WP-B1` chính sách verdict + stopping rule 10/10 PASS sau ba vòng E2
độc lập; `WP-B2` 31/31 requirement BT §21 có test, suite 678/678; `WP-B3` decision log 19 trường
+ `tags`, 25 loại sự kiện, 2.441/2.478 bản ghi trên production; `WP-C2` `ExecutionState` sáu giá
trị; bất biến tài chính `sha256 3ea7c8d7…` giữ nguyên bit-for-bit xuyên suốt B3/B2/C2 **[R]**.

**Tóm lại:** *bộ máy* (dữ liệu, provenance, đóng băng manifest, pipeline, sinh evidence, chính
sách verdict, audit trail) **đạt**. Cái trượt là *chiến lược*.

---

## 5. What Failed — Cái gì trượt (về mặt chiến lược)

Kết quả gate chính thức (`T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2; đối chiếu ngưỡng S018 §2.1):

| Gate | Giá trị đo | Ngưỡng | Kết quả | Khoảng cách |
|---|---|---|---|---|
| **Gate 1** | PrimaryMedian AE = **97,48 %** | `≥ 102,0` | **FAIL** | thiếu 4,52 điểm |
| **OOS** (điều kiện cứng) | AE = **92,94 %**, 21 tháng, cờ `SHORT_OOS` | `≥ 100,0` | **FAIL** | thiếu 7,06 điểm |
| **Gate 2** | PreOOS pass share = **0,00 %** | `≥ 75 %` | **FAIL** | **0 / 219 config** đạt |
| **Gate 3** | realistic NetEdge PM = **−0,0264** | `> 0` | **FAIL** | âm |

AE < 100 % nghĩa là: **chiến lược V2.1.5 tích luỹ ÍT ETH hơn benchmark đối chiếu**, cả trên
pre-OOS lẫn OOS. Gate 2 = 0,00 % nghĩa là **không một config nào trong 219 config đã đóng băng
vượt được ngưỡng** — không phải "chọn sai tham số", mà là **không tồn tại plateau nào trong không
gian tham số đã khai**.

Failure Signal chính thức:
- **TRUE (7)**: FS-01 (V2 tích luỹ ít ETH hơn Monthly DCA ở phần lớn gate window), FS-02
  (Opportunity reserve thường xuyên chạm cap và nằm im — `opportunity_cap_hit_share = 0,8961`),
  FS-03 (lợi thế biến mất khi loại một tháng/quý đóng góp lớn nhất), FS-04 (redundancy nghiêm
  trọng giữa sub-factor), FS-08 (V2 không vượt P95 của random control — **xem cảnh báo dưới**),
  FS-10 (`Gate2_OOS_PassShare < 50 %`), FS-11 (`OOS AE < 100 %`).
- **FALSE (5)**: FS-05, FS-06, FS-07, FS-09, FS-12.
- **UNKNOWN**: rỗng.

**Verdict chính thức**: `DO_NOT_BUILD`, reasons `["Gate 1 FAIL", "OOS hard condition FAIL"]`,
`can_proceed_to_app = false`.

> **Cảnh báo quan trọng về FS-08 — con số official đã bị thay thế bởi một phép tính lại hợp lệ.**
> `F-017` (Control F/G không giữ đúng kích thước tranche và profile giải ngân theo tháng) là một
> khiếm khuyết **được sửa trong `WP-B1`, tức SAU official run**. `CHECK-B1-03` (FROZEN) đòi tính
> lại FS-08 sau khi sửa. Chủ dự án đã tự chạy script replay trên máy có dataset official được bảo
> toàn; xác minh cơ học 8/8 điều kiện KHỚP (`dataset_hash` trùng official, `master_seed = 42`,
> `n_sims = 1000`, `v2_eth = 14,910758150139896` trùng frozen official bit-for-bit):
>
>     control_f_p95 = 14,887400583487747   → beats_f = true
>     control_g_p95 = 14,813546903782814   → beats_g = true
>     FS-08 (post-F-017) = FALSE
>
> Nghĩa là: **sau khi sửa Control F/G, V2 VƯỢT P95 của cả hai random control** — ngược chiều với
> `FS-08 = TRUE` ghi trong bản kê official. Điều này **KHÔNG** đổi verdict (xem §9 F-11) nhưng nó
> **thay đổi vật chất** cách đọc câu hỏi "Buy Score có kỹ năng timing hay không" (xem §11).

---

## 6. Meaning of DO_NOT_BUILD — `DO_NOT_BUILD` nghĩa là gì trong ngữ nghĩa repository

**Nguyên văn canonical** (Implementation Plan §5, bảng "Verdict và stopping rules", dòng
`DO NOT BUILD`, cột "Hành động bắt buộc"):

> *"Dừng productization chiến lược. Chọn benchmark đơn giản hơn hoặc thiết kế lại thành version mới."*

Các điều khoản ràng buộc kèm theo:
- IM §7: *"INCONCLUSIVE và DO NOT BUILD không thể đi tiếp sang phase app."*
- IM §1: *"Không build dashboard hoặc full app trước khi research prototype hoàn thành và verdict
  cho phép."*
- IM §9 (tiêu đề): *"App MVP — chỉ sau verdict cho phép."*
- Master Index §6: *"Nếu kết quả yêu cầu đổi hypothesis, tạo V2.2 với hypothesis mới và chạy lại
  các gate bắt buộc. **Không vá tại chỗ**."* — và cấm sửa công thức, ngưỡng gate, phương pháp sinh
  manifest, ngày split, giả định ma sát **dựa trên kết quả run**.
- `CONVENTIONS.md` #21(a): *"`can_proceed_to_app = (verdict == "BUILD")` là khoá duy nhất T-07/T-11
  được đọc."*

### 6.1 Phân biệt bắt buộc — hai mệnh đề KHÁC NHAU

| Mệnh đề | Canonical authority nói gì |
|---|---|
| **"Chiến lược V2.1.5 trượt validation"** | **ĐÚNG, canonical, tường minh.** `DEC-031` §E: `V2.1.5 validation = FAILED`. Đây chính là nội dung của verdict. |
| **"Sản phẩm/dự án CoinDCA phải bị bỏ"** | **KHÔNG có bất kỳ authority nào phát biểu điều này.** Không tìm thấy trong IM §5/§6/§7/§9, Master Index §6, `DEC-031`, `DEC-038`, hay bất kỳ `DEC-xxx` nào. |

Bằng chứng repository cho thấy hai mệnh đề **không** được canonical authority gộp làm một:
- IM §5 dùng đúng chữ *"Dừng productization **chiến lược**"* — đối tượng bị dừng được nêu đích
  danh là **chiến lược**, không phải dự án.
- Cùng dòng đó liệt kê hai hướng đi tiếp (*"chọn benchmark đơn giản hơn"*, *"thiết kế lại thành
  version mới"*) — một dòng ra lệnh **bỏ dự án** sẽ không có hai hướng đi tiếp.
- Master Index §6 cung cấp sẵn cơ chế V2.2 cho đúng tình huống "kết quả yêu cầu đổi hypothesis".
- Sau khi verdict `DO_NOT_BUILD` đã tồn tại, repository vẫn tiếp tục và **đóng thành công** các
  gói `WP-B1`/`WP-B2`/`WP-B3`/`WP-C2` (`DEC-034`, `DEC-038`, `DEC-037`, `DEC-036`) — chủ dự án
  đã bốn lần thực thi thẩm quyền Owner để tiếp tục dự án **sau** verdict.
- `webapp/` (lớp ghi chép/theo dõi) đã đi qua `T-09A` `DONE` và `T-09B` `DONE` (`DEC-018`,
  `DEC-024`, `DEC-021`) sau khi cổng verdict đã tồn tại — dưới `DEC-005` vẫn `PENDING`, tức ranh
  giới "ghi chép" vs "tự động hoá chiến lược" chưa được chốt chính thức nhưng **trên thực tế**
  lớp ghi chép chưa từng bị coi là bị cấm bởi verdict.

### 6.2 Cái bị `DO_NOT_BUILD` khoá — chính xác và hết

1. **`T-11` — Tầng tự động hoá chiến lược đầy đủ (app MVP theo spec).** Điều kiện của `T-11` gồm
   `verdict = BUILD`. Với `DO_NOT_BUILD`, `T-11` **không áp dụng được**, không chỉ bị chặn dây
   chuyền (`DEC-031` § Consequence).
2. **`can_proceed_to_app = false`** — cờ máy, khoá duy nhất `T-07`/`T-11` được đọc.
3. **Mọi hành vi "vá tại chỗ V2.1.5" để làm verdict đổi chiều** — Master Index §6 cấm tuyệt đối.

Cái **không** bị `DO_NOT_BUILD` khoá theo bất kỳ authority nào đã rà soát: sự tồn tại của dự án;
lớp ghi chép/quan sát `webapp/`; công việc hardening/chất lượng; việc soạn đề xuất V2.2
(`WP-D2`); việc nghiên cứu tiếp để hiểu vì sao V2.1.5 trượt.

---

## 7. Canonical Owner Choices — Các lựa chọn canonical

### 7.0 ⚠ `OWNER_DECISION_SURFACE_UNCLEAR` — ghi nhận bắt buộc trước khi đọc bảng

**Sự thật kiểm chứng được:** `T-07` **KHÔNG có file task** (`docs/tasks/T-07-*.md` không tồn tại),
**KHÔNG có Ready Gate**, **KHÔNG có Completion Gate đóng băng**, và **KHÔNG có danh sách lựa chọn
được liệt kê ở cấp task**. Toàn bộ định nghĩa canonical của `T-07` là ba dòng: tên
(*"DUYỆT — đọc verdict và chọn hướng đi"*), lý do (*"Verdict quyết định được xây app đầy đủ hay
phải mở V2.2"*), Tier `DUYET`, và dependency `T-06 DONE ∧ GATE-B` (`PROJECT_PROGRESS.md`;
`RCP-001` dòng 44/356/472). `T-05` — bước DUYỆT còn lại — cũng không có file task.

**Hệ quả:** bảng §7.1 dưới đây **KHÔNG phải** một danh sách lựa chọn đã đóng băng ở cấp `T-07`.
Nó là **bề mặt hành động canonical** lấy **nguyên văn** từ authority mà `T-07` tồn tại để áp dụng
(IM §5 dòng `DO NOT BUILD`, IM §6/§7, Master Index §6). Không có lựa chọn nào trong bảng do phiên
này phát minh. Cách trình bày này theo đúng tiền lệ của chính repository cho các quyết định thuộc
thẩm quyền Owner mà task không tự liệt kê: `DEC-005` (PA-1/PA-2/PA-3 cho `T-05`) và `DEC-035`
(PA-A/PA-B/PA-C cho `WP-C2`) — trong cả hai trường hợp agent soạn phương án, Owner chọn.

**Chủ dự án nên xác nhận bề mặt lựa chọn này trước khi chọn trong nó** (xem §13 câu hỏi Q1).

### 7.1 Bảng so sánh

| | **L-1 — Benchmark đơn giản hơn** | **L-2 — Thiết kế lại thành version mới (V2.2)** | **L-0 — Chưa quyết (mặc định)** |
|---|---|---|---|
| Nguồn canonical | IM §5, `DO NOT BUILD`, vế 1: *"Chọn benchmark đơn giản hơn"* | IM §5, `DO NOT BUILD`, vế 2: *"thiết kế lại thành version mới"* + Master Index §6 | **KHÔNG phải lựa chọn IM §5** — là hệ quả nếu không quyết |
| Ý nghĩa | Dừng hẳn việc productize chiến lược V2.1.5; chấp nhận một benchmark đơn giản hơn (ví dụ Monthly DCA thuần) làm hướng đi | Dừng productize V2.1.5 **và** mở một phiên bản đặc tả mới với hypothesis mới, chạy lại các gate bắt buộc | Giữ nguyên mọi thứ; `T-07` ở `READY` |
| `T-07` lifecycle | `READY → DONE` (thẩm quyền Owner) | `READY → DONE` (thẩm quyền Owner) | giữ `READY` |
| V2.1.5 verdict | `DO_NOT_BUILD` — **không đổi** | `DO_NOT_BUILD` — **không đổi** | không đổi |
| V2.1.5 validation | `FAILED` — **không đổi** | `FAILED` — **không đổi** | không đổi |
| `can_proceed_to_app` | `false` — **không đổi** | `false` — **không đổi** | không đổi |
| `T-11` | vẫn `BLOCKED`/không áp dụng được | vẫn `BLOCKED` dưới V2.1.5; chỉ có thể áp dụng lại dưới V2.2 **nếu và chỉ nếu** V2.2 tự chạy đủ gate và ra `BUILD` | vẫn `BLOCKED` |
| Cần version chiến lược mới? | **Không** | **Có** — bắt buộc, qua Master Index §6 | Không |
| Mở `V2.2`? | Không | Có (bước tiếp là **soạn đề xuất** qua `WP-D2`, không phải đóng băng hypothesis ngay) | Không |
| `DEC-005` | vẫn `PENDING` | vẫn `PENDING` | vẫn `PENDING` |
| Rủi ro / bất khả nghịch | Ghi nhận chính thức "dừng chiến lược" — có thể tạo cảm giác đóng dự án; công việc lớp A/B/C đã đầu tư không được dùng tiếp cho một chiến lược mới | Chi phí lớn: đóng băng hypothesis mới + chạy lại **toàn bộ** gate bắt buộc; nguy cơ **post-hoc tuning** nếu hypothesis mới được chọn sau khi đã biết kết quả V2.1.5 | Không có hành động bất khả nghịch; nhưng lộ trình đứng yên vô thời hạn và `T-07` không bao giờ `DONE` |

**Lưu ý về vế bắt buộc chung.** Cả L-1 lẫn L-2 đều đứng sau cùng một mệnh lệnh của IM §5:
**"Dừng productization chiến lược"**. Đây **không** phải một lựa chọn — nó là phần bắt buộc của
dòng `DO NOT BUILD`, đã có hiệu lực từ khi verdict tồn tại. Cái Owner chọn là **vế sau**.

---

## 8. Consequences of Each Choice — Hệ quả từng lựa chọn

### L-1 — Chọn benchmark đơn giản hơn

- **Ý nghĩa chính xác:** chấp nhận rằng V2.1.5 không tạo được accumulation edge, và hướng đi của
  dự án là một benchmark đơn giản hơn thay vì một chiến lược phức tạp hơn.
- **Được phép sau đó:** ghi nhận `T-07 = DONE`; tiếp tục lớp ghi chép/quan sát trong khuôn khổ
  `DEC-005` (vẫn `PENDING`); tiếp tục hardening; đóng các gói lớp C còn lại nếu chủ dự án muốn
  (`WP-C3` `READY`, `WP-C4` `PLANNED`).
- **Vẫn bị cấm:** `T-11`; `can_proceed_to_app = true`; sửa bất kỳ công thức/ngưỡng/manifest/ngày
  split/giả định ma sát nào của V2.1.5 dựa trên kết quả run (Master Index §6); tuyên bố V2.1.5
  PASS.
- **Trạng thái downstream:** `T-07: READY → DONE`. `T-11` giữ `BLOCKED` (điều kiện `verdict=BUILD`
  không bao giờ thoả dưới V2.1.5). `T-08` vẫn bị `DEC-005` chặn. `WP-C3`/`WP-C4` không tự mở.
- **`T-11` có đổi được không?** Không.
- **`can_proceed_to_app` có đổi được không?** Không.
- **V2.1.5 còn `FAILED` không?** Có, vĩnh viễn.
- **Cần strategy/version mới không?** Không.
- **Bất khả nghịch / rủi ro:** quyết định này có thể xem lại sau (chuyển sang L-2 vẫn khả thi vì
  Master Index §6 luôn còn hiệu lực). Rủi ro thực tế là **rủi ro truyền đạt**: `T-07 = DONE` kèm
  L-1 rất dễ bị đọc nhầm thành "dự án kết thúc" — nên câu chữ của `DEC` tương ứng phải ghi rõ
  điều ngược lại.

### L-2 — Thiết kế lại thành version mới (mở V2.2)

- **Ý nghĩa chính xác:** kết quả V2.1.5 được coi là yêu cầu đổi hypothesis. Theo Master Index §6,
  đường duy nhất hợp lệ là **tạo V2.2 với hypothesis mới và chạy lại các gate bắt buộc** — tuyệt
  đối **không vá tại chỗ** V2.1.5.
- **Được phép sau đó:** ghi nhận `T-07 = DONE`; **mở `WP-D2`** (`READY`, không phụ thuộc gói nào)
  để **soạn đề xuất** V2.2 — `RCP-001` ghi rõ `WP-D2` *"chỉ sinh đề xuất; mở V2.2 là quyết định
  của chủ dự án"*. `HARDENING_BACKLOG.md` đã tích sẵn nhiều mục chờ V2.2 (H-24/H-25, và các mục
  §1220/§1327/§1333/§1363).
- **Vẫn bị cấm:** `T-11` dưới V2.1.5; đổi verdict/threshold của V2.1.5; mang nguyên ba ngưỡng
  FS-02/FS-07/FS-12 sang V2.2 theo mặc định (`DEC-033` cấm tường minh: *"Approval này KHÔNG tự
  động authorize mang nguyên ba ngưỡng sang V2.2"*); chọn hypothesis/objective mới **trong chính
  quyết định `T-07`** (xem §12).
- **Trạng thái downstream:** `T-07: READY → DONE`. `T-11` giữ `BLOCKED`. V2.2, nếu được mở, là
  một **nhánh lộ trình mới** với gate riêng — nó không kế thừa `can_proceed_to_app` của V2.1.5.
- **`T-11` có đổi được không?** Không phải bởi quyết định này. Chỉ một verdict `BUILD` của **V2.2**
  (sau khi V2.2 tự chạy đủ gate bắt buộc) mới có thể mở lại điều kiện đó.
- **`can_proceed_to_app` có đổi được không?** Không — cờ này thuộc về run của V2.1.5.
- **V2.1.5 còn `FAILED` không?** Có, vĩnh viễn. V2.2 không "sửa" V2.1.5; nó thay thế.
- **Cần strategy/version mới không?** Có — đó chính là nội dung lựa chọn.
- **Bất khả nghịch / rủi ro:**
  - **Rủi ro post-hoc tuning (nghiêm trọng nhất).** Hypothesis của V2.2 sẽ được chọn *sau khi* đã
    biết V2.1.5 trượt ở đâu. Master Index §6 và `DEC-031` §B (từ chối tạo gate hậu nghiệm) tồn tại
    chính để chặn kiểu này. Bất kỳ V2.2 nào cũng phải đóng băng tiêu chí **trước** khi chạy.
  - **Chi phí:** chạy lại toàn bộ gate bắt buộc (219 config Gate 2 + 114 config Gate 3 + 1000
    Random Timing + 1000 Random Anchor + 3000 bootstrap + 1000 behavioral, mỗi full run duyệt
    ~268.000 nến 15m — IM §4).
  - **Rủi ro chọn mục tiêu quá sớm:** xem §12 và §8 của chỉ thị phiên — objective selection phải
    tách khỏi kết quả V2.1.5.

### L-0 — Chưa quyết

- **Ý nghĩa chính xác:** không có hành động. `T-07` ở `READY` vô thời hạn.
- **Được phép sau đó:** không có gì mới được mở.
- **Trạng thái downstream:** mọi thứ giữ nguyên như §2.
- **Bất khả nghịch / rủi ro:** không có hành động bất khả nghịch. Rủi ro là lộ trình đứng yên và
  `GATE-B` đã đóng nhưng không dẫn tới đâu. Lưu ý `GOVERNANCE_V4.md` có quy tắc *"A merge gate
  BLOCKED for more than 30 days forces an Owner Decision"* — quy tắc đó viết cho merge gate, không
  tự động áp cho `T-07`, nhưng tinh thần "không để treo vô hạn" là có trong governance.

---

## 9. Facts — Dữ kiện được bằng chứng canonical hậu thuẫn trực tiếp

- **F-01** Official verdict = `DO_NOT_BUILD`; reasons = `["Gate 1 FAIL", "OOS hard condition FAIL"]`;
  `can_proceed_to_app = false`. (`DEC-031` §E; `T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2; tag)
- **F-02** V2.1.5 validation = `FAILED`. (`DEC-031` §E)
- **F-03** Bốn kết quả gate: Gate 1 PrimaryMedian 97,48 (< 102); OOS AE 92,94, 21 tháng, `SHORT_OOS`
  (< 100); Gate 2 PreOOS pass share 0,00 % (< 75 %); Gate 3 realistic NetEdge −0,0264 (≤ 0).
  Tất cả **nhất quán tuyệt đối** với ngưỡng cứng đã đóng băng trong mã tại official commit.
  (S018 §2.1 **[R]**; giá trị đầu vào **[O]**)
- **F-04** 7/12 Failure Signal = TRUE (FS-01, 02, 03, 04, 08, 10, 11); 5 = FALSE; **UNKNOWN rỗng**.
  (`T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2)
- **F-05** Gate 2 = 0,00 %: **không config nào trong 219 config đã đóng băng** đạt ngưỡng.
- **F-06** Pre-T06 manifest freeze tái lập được **hoàn toàn từ mã + seed**: 10/10 giá trị + 2/2 hash
  KHỚP. (**[R]**, S018 §2/§5)
- **F-07** Tag annotated `v2.1.5-official-T06` peel đúng về commit `5228130…`;
  `dependency_lock_hash` khớp `sha256(pyproject.lock)`. (**[R]**)
- **F-08** `dataset_hash 3150860c…` tái tính khớp tuyệt đối từ ba `file_hash` Owner khai qua đúng
  thuật toán `_dataset_hash()`. (**[R]** cho tính nhất quán thuật toán; **[O]** cho việc ba
  `file_hash` là dữ liệu Binance thật)
- **F-09** Raw artifact của official run (16 file: 3 parquet, `lineage.json`, toàn bộ `results/`)
  **không nằm trong git tree**; `results/` và `data/raw/*.parquet` nằm trong `.gitignore`. Owner
  khai đã backup độc lập 16/16 và tự verify SHA-256 PASS. (**[O]**)
- **F-10** `DEC-031` §D/§F ghi tường minh: `T-06 = DONE` **không** có nghĩa strategy PASS / gates
  PASS / V2.1.5 validated / được phép productionize / `can_proceed_to_app = true`.
- **F-11** Hai khiếm khuyết verdict tìm thấy **sau** official run (`E2-B1-F01` FS-08 thiếu input,
  `E2-B1-F02` `official` không AND đủ bốn nguồn) và `F-S015-01` (`numpy.bool_`) **không thể** đã
  ảnh hưởng verdict của run đó: `decide_verdict` vào nhánh `Gate 1 FAIL or OOS FAIL` **trước** khi
  đọc cờ Failure Signal, và chiều sai của cả ba là "để BUILD lọt qua", ngược với verdict thực tế.
  (S018 §2.1 **[R]**; `CHECK-B1-02`)
- **F-12** `F-017` (Control F/G không giữ đúng tranche/profile theo tháng) được sửa **sau** official
  run. Phép tính lại FS-08 post-F-017 do Owner chạy trên dataset official (8/8 điều kiện xác minh
  cơ học KHỚP; `v2_eth = 14,910758150139896` trùng frozen official bit-for-bit) cho
  `beats_f = true`, `beats_g = true`, **`FS-08 (post-F-017) = FALSE`** — ngược với `FS-08 = TRUE`
  trong bản kê official. (`docs/tasks/WP-B1-*.md::CHECK-B1-03` Addendum 3; `DEC-034`)
- **F-13** `GATE-B = CLOSED` là cổng **thủ tục** (`WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`), **không**
  phải phán quyết về nội dung verdict. (`DEC-038`)
- **F-14** `T-07` không có file task, không có Ready Gate, không có Completion Gate, không có danh
  sách lựa chọn được liệt kê ở cấp task. (kiểm trực tiếp `docs/tasks/`)
- **F-15** IM §5 dòng `DO NOT BUILD` nguyên văn: *"Dừng productization chiến lược. Chọn benchmark
  đơn giản hơn hoặc thiết kế lại thành version mới."*
- **F-16** Không authority nào trong repository phát biểu rằng dự án/sản phẩm CoinDCA phải bị bỏ.
  (rà `docs/spec/*`, `governance/v4/CORE/*`, toàn bộ `PROJECT/PROJECT_DECISIONS.md`)
- **F-17** `DEC-005` vẫn `PENDING`; nó — chứ không phải verdict — là thứ đang chặn `T-08` và là nơi
  ranh giới webapp được quyết. (`DEC-005`, `DEC-035`, `DEC-038`)
- **F-18** `DEC-033` cấm tường minh việc mang mặc định ba ngưỡng FS-02/FS-07/FS-12 sang V2.2.

---

## 10. Interpretations — Diễn giải hợp lý (KHÔNG phải bằng chứng thực nghiệm)

Nhãn rõ: các mục dưới đây là **suy luận từ dữ kiện §9**, không phải kết quả đo.

- **I-01** Gate 2 = 0,00 % trên 219 config gợi ý rằng thất bại **không phải do chọn sai tham số**
  mà mang tính hệ thống hơn — không tồn tại plateau nào trong không gian tham số đã khai. Đây là
  suy luận từ F-05; nó **không** xác định nguyên nhân.
- **I-02** Việc cả Gate 1 lẫn OOS đều FAIL với AE < 100 % nghĩa là V2.1.5 thua benchmark ở cả hai
  chế độ dữ liệu — nhất quán với FS-01 TRUE. Suy luận từ F-03/F-04.
- **I-03** F-12 (FS-08 post-F-017 = FALSE, V2 vượt P95 cả hai control) **không mâu thuẫn** với
  verdict `DO_NOT_BUILD`, vì FS-08 chưa từng được `decide_verdict` hỏi tới (F-11). Nhưng nó gợi ý
  rằng "V2.1.5 hoàn toàn không có tín hiệu timing" là một cách đọc **quá mạnh** so với bằng chứng
  hiện có. Đây là diễn giải, không phải kết luận nhân quả.
- **I-04** Vì bộ máy (§4) đạt trong khi chiến lược trượt (§5), thất bại nhiều khả năng nằm ở
  **giả thuyết chiến lược**, không ở hạ tầng. Suy luận từ tương phản §4/§5; **không** loại trừ
  khả năng một khiếm khuyết chưa phát hiện trong engine đã ảnh hưởng con số (raw artifact không
  có trong repo để kiểm chứng độc lập — F-09).
- **I-05** Việc chủ dự án bốn lần thực thi thẩm quyền Owner để đóng gói việc **sau** verdict
  (`DEC-034`/`036`/`037`/`038`) cho thấy trên thực tế dự án chưa từng được đối xử như đã bị bỏ.
  Đây là quan sát hành vi, không phải một điều khoản canonical.
- **I-06** Các gói lớp B/C (`WP-B1`, `WP-B2`, `WP-B3`, `WP-C2`) đóng **sau** official run là bằng
  chứng về **năng lực hiện tại của repository**, **không** phải bằng chứng rằng con số của official
  run được sinh bởi mã đã-được-chứng-minh-đúng. Ngược lại, `F-017`/`E2-B1-F01`/`E2-B1-F02` cho
  thấy mã tại thời điểm official run **có** khiếm khuyết — chỉ là đã chứng minh được rằng chúng
  không đảo verdict (F-11) và một trong số đó đã được tính lại (F-12).

---

## 11. Not Established — Chưa được thiết lập bởi bằng chứng hiện có

### 11.1 Năm câu hỏi nghiên cứu đã biết (KHÔNG điều tra ở phiên này — chỉ kiểm xem đã có kết luận chưa)

| # | Câu hỏi | Trạng thái | Cái ĐÃ có / cái CÒN thiếu |
|---|---|---|---|
| **RQ-1** | Cách xử lý reserve/tiền mặt có ảnh hưởng vật chất tới AE không? | **NOT ESTABLISHED** | **Đã có:** FS-02 = TRUE (`opportunity_cap_hit_share = 0,8961` > 0,5) — reserve thường xuyên chạm cap và nằm im. FS-07 = FALSE với ngưỡng `avg_cash_ratio > 0,30 AND gate1_primary_ae < 102,0`; vì AE 97,48 < 102 là đúng, FS-07 = FALSE **buộc** `avg_cash_ratio ≤ 0,30`. **Còn thiếu:** không có phép đo phản-thực (counterfactual) nào về AE khi đổi cách xử lý reserve. S018 §2.1 ghi tường minh: FS-02/FS-12 *"được ghi lại như số đo, KHÔNG được đọc thành nguyên nhân gốc — evidence hiện có không chứng minh quan hệ nhân quả"*. |
| **RQ-2** | Buy Score có kỹ năng timing ở mức vốn triển khai bằng nhau không? | **PARTIALLY ESTABLISHED — và ngược chiều với bản kê official** | **Đã có:** Control F theo BT §239 giữ nguyên tháng, kích thước tranche và profile giải ngân theo tháng, **chỉ** random hoá thời điểm mua ⇒ vốn triển khai bằng nhau **theo cấu tạo**. Phép tính lại post-`F-017` (F-12): `v2_eth = 14,910758150139896` > `control_f_p95 = 14,887400583487747` và > `control_g_p95 = 14,813546903782814` ⇒ **V2 vượt P95 cả hai control**, `FS-08 = FALSE`. **Còn thiếu / cảnh báo:** (a) biên rất mỏng — +0,157 % so với Control F P95; (b) BT §251 ghi rõ Control F *"đo lẫn cả hiệu ứng cơ học của việc điều kiện hoá trên giá đã giảm, chứ không thuần kỹ năng dự báo"* ⇒ vượt P95 **không** chứng minh kỹ năng dự báo; (c) chỉ là **một** con số gộp toàn kỳ, không tách theo window/OOS (xem RQ-3); (d) đây là replay của **một** cấu hình baseline, không phải toàn bộ manifest. |
| **RQ-3** | Hiệu năng Control F theo từng window riêng lẻ / OOS? | **NOT ESTABLISHED** | **Đã có:** đúng một con số gộp cho khoảng `2019-01-01 → oos_end` (F-12). **Còn thiếu:** phân rã theo từng window trong chín cửa sổ, và tách riêng OOS. Raw artifact `results/random_control_21b7d88e9691_metrics.json` **không nằm trong repository** (F-09), nên không thể phân rã ở đây. |
| **RQ-4** | Opportunity Fund có tạo optionality hữu ích không? | **NOT ESTABLISHED** | **Đã có:** FS-02 = TRUE, `opportunity_cap_hit_share = 0,8961` — reserve chạm cap và **nằm im** ở 89,61 % phép đo (BT §313: *"Opportunity reserve thường xuyên chạm cap và nằm im không được dùng"*). Đây là một phép đo **chiều tiêu cực** về mức sử dụng. **Còn thiếu:** không có phép đo nào về **giá trị optionality** (ví dụ giá trị của việc còn tiền mặt khi crash xảy ra) — mà chính đó mới là nội dung câu hỏi. Mức sử dụng thấp ≠ optionality vô giá trị. |
| **RQ-5** | Thất bại chủ yếu do lệch mục tiêu (objective mismatch) hay do thiếu edge timing? | **NOT ESTABLISHED** | **Đã có:** không artifact canonical nào thực hiện phép quy trách nhiệm này. RQ-2 lại gợi ý (yếu, có cảnh báo) rằng ít nhất không phải "hoàn toàn không có timing edge". **Còn thiếu:** toàn bộ. S018 §2.1 cấm đọc số đo thành nguyên nhân gốc. **Đây chính là câu hỏi mà bằng chứng hiện có KHÔNG trả lời được.** |

### 11.2 Các điểm khác chưa được thiết lập

- **NE-01** **Nguyên nhân vì sao V2.1.5 trượt.** Bằng chứng hiện có chứng minh **RẰNG** nó trượt và
  trượt ở đâu (§5). Nó **không** chứng minh **VÌ SAO**. Không có phân tích nhân quả nào trong
  repository, và `DEC-031` không tạo ra một phân tích như vậy.
- **NE-02** Rằng các trường số trong `*_metrics.json` (PrimaryMedian, AE, NetEdge…) được **tính
  đúng** bởi engine — evidence record chỉ đối chiếu chúng với **ngưỡng**, không tái chạy engine
  trên dataset thật (Master Index §6 cấm chạy lại official run).
  (`T06_OFFICIAL_EVIDENCE_RECORD.md` §10)
- **NE-03** Rằng ba `file_hash` là sha256 của dữ liệu Binance thật (cần byte gốc — không có trong
  repo).
- **NE-04** Rằng `official_eligibility()`/`verify_lineage()` thực sự đã chạy đối chiếu byte đĩa
  trên máy Owner.
- **NE-05** Rằng một benchmark đơn giản hơn (L-1) sẽ tốt hơn V2.1.5 — **chưa từng được đo**. IM §5
  đề xuất hướng đi này nhưng không có thí nghiệm nào trong repository so sánh nó.
- **NE-06** Rằng bất kỳ hypothesis V2.2 nào sẽ vượt gate — theo định nghĩa chưa đo được.
- **NE-07** Năm mục `OD-T06-04`, `OD-T06-06`, `OD-T06-08`, `OD-T06-09` vẫn `STILL_OPEN` sau
  `DEC-031`; ba trong số đó cần đọc dataset/artifact official thật.

---

## 12. What This Decision Does NOT Decide — Quyết định `T-07` KHÔNG quyết cái gì

1. **Không đổi verdict.** `DO_NOT_BUILD` là kết quả của `T-06`, đã đóng băng. `T-07` **đọc** nó.
2. **Không đổi `can_proceed_to_app`** (`false`) và không đổi V2.1.5 validation (`FAILED`).
3. **Không mở `T-11`.** Điều kiện `verdict = BUILD` không thoả dưới V2.1.5.
4. **Không đóng `DEC-005`** và không mở `T-08`. `GATE-B`/`T-07` không nằm trong điều kiện của
   `T-08` (`DEC-038`).
5. **Không chọn objective cho tương lai.** Cụ thể, `T-07` **không** chọn giữa
   *"A — tối đa hoá tích luỹ ETH / ETH-equivalent"* và *"C — giữ optionality vốn / triển khai khi
   crash"*. Không có authority canonical nào định nghĩa hai mục tiêu này; chúng chỉ xuất hiện
   trong repository như **hạng mục bị loại trừ tường minh** khỏi phạm vi (`DEC-031`
   § Không mở rộng phạm vi; `S020` §146). Nếu nghiên cứu chiến lược tiếp tục được phép sau `T-07`,
   **việc chọn objective phải được xử lý tách rời khỏi kết quả official của V2.1.5** — vì V2.1.5
   chưa từng kiểm tra objective nào khác, kết quả của nó không thể được dùng để biện minh cho một
   objective mới (đó chính là post-hoc selection mà Master Index §6 và `DEC-031` §B tồn tại để
   chặn).
6. **Không thiết kế V2.2.** Ngay cả L-2 cũng chỉ **cho phép mở đường** tới việc soạn đề xuất qua
   `WP-D2`; nó không đóng băng hypothesis nào.
7. **Không mở `WP-C3`/`WP-C4`**, không rerun `T-06`, không chạy lại thí nghiệm chiến lược nào.
8. **Không giải quyết `H-39`/`H-40` hay bất kỳ mục HARDENING nào**, không tạo task ID mới.
9. **Không trả lời RQ-1…RQ-5.** Chúng thuộc về sau khi chủ dự án xác định hướng nghiên cứu được
   phép.

---

## 13. Recommended Questions for Owner — Câu hỏi đề nghị chủ dự án tự trả lời

*(Chỉ là câu hỏi. Phiên này KHÔNG trả lời thay.)*

- **Q1** Chủ dự án có xác nhận rằng bề mặt lựa chọn ở §7.1 (L-1 / L-2, đứng sau mệnh lệnh chung
  *"Dừng productization chiến lược"* của IM §5) là **đúng và đủ** cho `T-07` không — biết rằng
  `T-07` không có file task và không có danh sách lựa chọn được đóng băng (F-14)?
- **Q2** Có lựa chọn nào khác mà chủ dự án cho là canonical nhưng không xuất hiện ở §7.1 không?
- **Q3** Chủ dự án có muốn `T-07` chuyển `READY → DONE` trong cùng quyết định này, hay giữ `READY`
  cho tới khi hướng đi được cụ thể hoá?
- **Q4** Nếu chọn L-2: chủ dự án muốn bước kế tiếp là **mở `WP-D2` để soạn đề xuất V2.2** (đúng
  ranh giới `RCP-001`: `WP-D2` chỉ sinh đề xuất), hay chỉ ghi nhận hướng L-2 mà chưa mở gói nào?
- **Q5** Nếu chọn L-2: chủ dự án chấp nhận ràng buộc rằng hypothesis của V2.2 phải được đóng băng
  **trước** khi chạy, và **không** được kế thừa mặc định ngưỡng của V2.1.5 (`DEC-033`) chứ?
- **Q6** Chủ dự án có muốn `DEC-005` được đưa ra quyết định **cùng lúc** với `T-07` không? (Hai
  quyết định độc lập về mặt điều kiện, nhưng cùng chạm câu hỏi "được xây tới đâu"; `DEC-005` là
  thứ đang thực sự chặn `T-08`.)
- **Q7** Với F-12 (FS-08 post-`F-017` = FALSE, ngược với bản kê official): chủ dự án có muốn bản kê
  official trong `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2 được **chú thích** để hai con số
  không mâu thuẫn khi đọc sau này không? (chỉ là chú thích evidence, không đổi verdict — sẽ là
  một phiên riêng)
- **Q8** Với RQ-3 (Control F theo từng window/OOS) và RQ-1/RQ-4/RQ-5 — chủ dự án có muốn uỷ quyền
  một phiên nghiên cứu **sau** `T-07` để trả lời chúng không, và nếu có thì trong ranh giới nào
  (raw artifact official chỉ tồn tại trên máy chủ dự án — F-09)?
- **Q9** Chủ dự án có muốn phiên tiếp theo ghi Owner Decision (`DEC-039`) cho `T-07`, hay chính chủ
  dự án sẽ viết?
- **Q10** Sai lệch trình bày ở cột `Status` của dòng roadmap `T-11` (`PLANNED` vs `BLOCKED` — xem
  §2) có được uỷ quyền sửa trong một phiên state-sync riêng không?

---

## 14. Exact Owner Response Required — Định dạng trả lời tối thiểu

Dán nguyên khối dưới đây vào chat, điền các trường viết hoa. Đây là mức tối thiểu đủ để một phiên
sau ghi Owner Decision hợp lệ theo `STATE_AUTHORITY.md`.

```
OWNER DECISION — T-07

XAC NHAN BE MAT LUA CHON (Q1): ĐỒNG Ý | KHÔNG ĐỒNG Ý (nếu không: nêu lựa chọn còn thiếu)

LUA CHON: L-1 | L-2 | L-0

T-07 LIFECYCLE: READY -> DONE | GIU READY

RANG BUOC BAT BUOC (xác nhận giữ nguyên, không được đổi):
  - official verdict            = DO_NOT_BUILD        [GIU NGUYEN]
  - V2.1.5 validation           = FAILED              [GIU NGUYEN]
  - can_proceed_to_app          = false               [GIU NGUYEN]
  - T-11                        = BLOCKED             [GIU NGUYEN]
  - DEC-005                     = PENDING             [GIU NGUYEN | QUYET RIENG]

NEU CHON L-2:
  - MO WP-D2 DE SOAN DE XUAT V2.2: CO | KHONG
  - XAC NHAN hypothesis V2.2 phai dong bang TRUOC khi chay,
    KHONG ke thua mac dinh nguong V2.1.5 (DEC-033): CO | KHONG

UY QUYEN GHI QUYET DINH: CHO PHEP phien sau ghi DEC-039 | OWNER TU GHI

UY QUYEN NGHIEN CUU SAU T-07 (Q8): CO (ghi ranh gioi) | KHONG | QUYET SAU

GHI CHU: <tuỳ chọn>
```

**Ràng buộc bắt buộc với phiên thực thi sau đó** (bất kể lựa chọn nào): không rerun `T-06`; không
sửa công thức/ngưỡng/manifest/ngày split/giả định ma sát của V2.1.5; không mở `T-11`; không đóng
`DEC-005` trừ khi chủ dự án quyết riêng; không chọn objective A/C; production diff phải = EMPTY
trừ khi chủ dự án uỷ quyền tường minh.

---

*Tài liệu này là bản chuẩn bị quyết định. Nó không phải Owner Decision, không phải Completion
Gate, không phải Ready Gate, và không đổi trạng thái bất kỳ task nào.*
