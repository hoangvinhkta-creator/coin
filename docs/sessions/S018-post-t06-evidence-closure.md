# S018 — POST-T06 EVIDENCE CLOSURE: kiểm chứng official run và ghi nhận `OWNER_DECISION_REQUIRED`

Session ID:
S018

Ngày: 2026-09-03
Nhánh: `claude/coindca-data-stream-vv0vwv`
HEAD phiên này: `5228130677e9e9875335eef890b6ed748a384603` (= `origin/…`, khớp canonical checkout Owner khai)
Baseline khi phiên mở: `990a6bb` (local checkout lạc hậu 4 commit — xem §1)
Task: `T-06` — **KHÔNG có file định nghĩa** (xem §4, đây là phát hiện trung tâm)
Capability: `CAP-PROV` (provenance), `CAP-DATA` (dataset)
Authority: không có Owner Decision nào cho phép chuyển `T-06` → `DONE` (xem §6)
Model/Effort: Tier C / Opus / `xhigh`

Task Mode:
MAJOR (theo routing `T-06` — D2 R3 B3 A1 X3 → C; U2 V4 H3 C3 F3 → `xhigh`)

Status:
**OWNER_DECISION_REQUIRED** — hard-stop hợp lệ theo `AGENTS.md` §3. `T-06` **KHÔNG** được
chuyển sang `DONE` trong phiên này. Không state nào bị đổi.

---

## 0. Kết luận một dòng

Official run của `T-06` **không có dấu hiệu nào cho thấy nó không hợp lệ** — mọi thứ kiểm
chứng được đều khớp chính xác. Nhưng `T-06` **không thể được ghi `DONE`** vì bộ máy gate mà
nó phải đi qua **chưa tồn tại**, và evidence official **không nằm trong repository**. Đây là
vấn đề *bookkeeping và gate-existence*, KHÔNG phải vấn đề *validity*.

---

## 1. Sai lệch checkout phát hiện đầu phiên (đã xử lý)

Container mở phiên ở `990a6bb`, không phải `5228130` như canonical checkout khai. `origin`
ref cục bộ cũng lạc hậu. `990a6bb` là **ancestor** thật của `5228130` (kiểm bằng
`git merge-base --is-ancestor`), nên phiên đã `git fetch origin <branch>` rồi
`git merge --ff-only` — thao tác **fast-forward thuần** (dịch con trỏ), KHÔNG merge commit,
KHÔNG rebase, KHÔNG reset. Sau đó `HEAD == origin == 5228130`.

Ghi để không ai đọc nhầm: container này **KHÔNG** phải máy đã chạy official run. Nó không có
`data/`, không có stash `pre-T06-local-artifacts`, và không có `results/`. Mọi phát biểu dưới
đây về "vắng mặt artifact" là phát biểu về **repository canonical**, không phải phủ nhận
artifact tồn tại trên máy Owner.

Branch authority check (`AGENTS.md` §7 Step 0) đã chạy TRƯỚC khi đọc state file:

    BRANCH AUTHORITY: PASS
    behind upstream = 0 · ahead of default = 15 · divergence LOC = 6464
    tracked worktree = CLEAN · production diff = EMPTY
    INTEGRATION_DECISION_REQUIRED: ahead>10 loc>5000  -> đã xử lý tại DEC-029 (ACCEPT DIVERGENCE)

---

## 2. Những gì ĐÃ kiểm chứng độc lập được (E1, tái lập tại HEAD `5228130`)

Đây là phần mạnh của phiên. Năm nhóm dữ kiện được tái lập **từ chính canonical checkout**,
không dùng lời khai:

| # | Dữ kiện | Khai báo | Tái lập tại `5228130` | Kết quả |
|---|---|---|---|---|
| 1 | `code_commit` | `5228130…` | `git rev-parse HEAD` = `5228130…`; `git ls-remote` khớp | **KHỚP** |
| 2 | `dependency_lock_hash` | `9ea0150fcf27…` | `sha256(pyproject.lock)` = `9ea0150fcf27…` | **KHỚP** |
| 3 | Gate 2 manifest freeze | 19 / 1 / 18 / 200 / 219 · `e34f92ae…` | tái sinh `generate_gate2_manifest()` | **KHỚP CẢ 6** |
| 4 | Gate 3 manifest freeze | 14 / 100 / 114 · `ef30f657…` | tái sinh `generate_gate3_manifest()` | **KHỚP CẢ 4** |
| 5 | FS-12 `net_advantage` | `-1.0935215802236702` | tái tính `_advantage_share` từ 4 số regime | **KHỚP TỚI BIT CUỐI** |

Chi tiết #3/#4: `manifest_hash` chỉ phụ thuộc **mã + seed**, không phụ thuộc dataset — nên
kiểm chứng được mà **không cần chạy lại `T-06`** và không cần dữ liệu Binance. Hai hash
khớp tuyệt đối nghĩa là **pre-T06 manifest freeze là thật và tái lập được**.

Chi tiết #5: `share = max(adv)/positive_mass = 1.6273303598351732 / 2.8027805105699284
= 0.5806128427460292`. Ngưỡng FS-12 là `> 0.80` ⇒ **FALSE**, đúng như khai báo. `positive_mass`
(không phải net) là mẫu số đúng theo `CONVENTIONS #20`.

### 2.1 Nhất quán nội tại với ngưỡng ĐÃ ĐÓNG BĂNG

Bốn gate và các signal khai báo đều nhất quán với ngưỡng cứng trong `gates.py` /
`failure_signals.py` tại HEAD này (ngưỡng kiểm chứng được; **giá trị đầu vào thì không**):

| Hạng mục | Khai báo | Ngưỡng canonical | Nhất quán |
|---|---|---|---|
| Gate 1 | PrimaryMedian 97.48% → FAIL | `pm >= 102.0` | ✔ 97.48 < 102.0 |
| OOS | AE 92.94%, 21 tháng, SHORT_OOS → FAIL | `ae >= 100.0` | ✔ 92.94 < 100.0 |
| Gate 2 | PreOOS pass share 0.00% → FAIL | `pre >= 0.75` | ✔ 0.00 < 0.75 |
| Gate 3 | realistic NetEdge PM −0.0264 → FAIL | `> 0.0` | ✔ −0.0264 ≤ 0 |
| FS-02 | `opportunity_cap_hit_share` 0.8961 → TRUE | `> 0.5` | ✔ |
| FS-11 | TRUE | `oos_ae < 100.0` | ✔ 92.94 < 100 |
| FS-10 | TRUE | `gate2_oos_pass_share < 0.50` | ✔ nhất quán với Gate 2 sụp |
| Verdict | `DO_NOT_BUILD`; reasons = Gate 1 FAIL + OOS hard condition FAIL | `decide_verdict` nhánh 1 | ✔ đúng thứ tự reason |
| `can_proceed_to_app` | `false` | `v == "BUILD"` | ✔ |

**Một quan sát làm GIẢM rủi ro, cần ghi lại.** `decide_verdict` vào nhánh
`not gate1["pass"] or not oos["pass"]` **TRƯỚC** khi đọc `fs["any_true"]`. Nghĩa là khiếm
khuyết `F-S015-01` (`any_true` dùng `v is True` nên `numpy.bool_` vô hình) **KHÔNG THỂ** đã
ảnh hưởng tới verdict của official run này: cờ FS chưa từng được hỏi tới. Và chiều sai của
`F-S015-01` là "để BUILD lọt qua", trong khi verdict thực tế là `DO_NOT_BUILD` — chiều bảo
thủ. Điều này **thu hẹp** phần dư của `RSK-007` (lo ngại `WP-B1` đứng sau `T-06` nhưng
`T-06` mới phát verdict) **cho riêng run này**; nó KHÔNG đóng `RSK-007`.

Cũng không diễn giải: `FS-02 = 0.8961` và bộ số regime FS-12 được ghi lại **như số đo**,
KHÔNG được đọc thành nguyên nhân gốc — evidence hiện có không chứng minh quan hệ nhân quả.

---

## 3. Những gì KHÔNG kiểm chứng được trong repository canonical

Tìm kiếm toàn repo (trừ `.git`):

    gate1_eef3d951aaa0        -> 0 file
    gate2_b08da9ba5229        -> 0 file
    gate3_a0099f6bf0c0        -> 0 file
    random_control_21b7d88e9691 -> 0 file
    baseline_808b61fa5ffe     -> 0 file
    dataset_hash 3150860c…    -> 0 file
    thư mục runs/ artifacts/ data/ evidence/ -> không tồn tại

`results/` **nằm trong `.gitignore`** — nên artifact thô vắng mặt khỏi git là **hợp lệ**.
Nhưng evidence cũng **không** được ghi ở bất kỳ đâu trong `docs/` hay `PROJECT/`: không
evidence record, không biên bản, không bảng kết quả. Vậy toàn bộ các dữ kiện sau chỉ tồn tại
dưới dạng **lời khai trong session prompt**:

- `dataset_hash` `3150860cb379…` và `official=True / official_reason=verified`
- năm run record ID và `provenance_resolved=true / provenance_unresolved=[]`
- số liệu thô bốn gate, 12 Failure Signal, verdict `DO_NOT_BUILD`

Đây chính là điều `EVIDENCE_STANDARD.md` tồn tại để chặn:

> Purpose: **Prevent an AI agent from marking gates PASS using unsupported narrative claims.**
> Do not invent: command output, test results… **If not executed: Status = NOT_TESTED.**
> **Do not leave E2 results only in chat history.**

và `STATE_AUTHORITY.md`:

> Every state transition whose truth depends on code must carry a SHA **and its evidence**.
> **A transition asserted without one is narrative, and narrative does not move state.**

SHA thì có (và khớp). Evidence thì không có trong repo.

---

## 4. Phát hiện trung tâm — `T-06` KHÔNG có Completion Gate

`task_registry_snapshot.sh` (công cụ canonical) xác nhận:

    count_task_files      = 22
    count_roadmap_task_ids = 28
    T-06 xuất hiện trong bảng roadmap — KHÔNG có docs/tasks/T-06-*.md

Và `grep` toàn repo cho `CHECK-T06` / `CHECK-06` / `CHECK-T-06` → **0 kết quả**.

Hệ quả theo governance, theo thứ tự authority:

1. `TASK_MODE_STANDARD.md` Mode 2 (MAJOR) **Requires**: task definition file, dedicated
   session, Ready Gate, **frozen Completion Gate**, session handoff. `T-06` là MAJOR
   (Tier C, `xhigh`, category `accounting_financial`, nằm trên đường găng). Không có file ⇒
   không có ba thứ đầu.
2. `TASK_READY_GATE_STANDARD.md` **Rule**: "A task cannot transition `PLANNED` → `IN_PROGRESS`.
   It must transition `PLANNED` → `READY` → `IN_PROGRESS`." `T-06` hiện `PLANNED` và chưa từng
   `READY`. MAJOR Ready Gate còn đòi "Completion Gate is **frozen before implementation**".
   Official run đã chạy **trước khi** có gate để đóng băng.
3. `TASK_COMPLETION_GATE_STANDARD.md`: "A task is DONE only when **all REQUIRED checks PASS**,
   the required evidence level is satisfied, Exit Criteria are satisfied." `T-06` **không có
   REQUIRED check nào** ⇒ điều kiện này không thể thoả, cũng không thể bị vi phạm — nó vô
   nghĩa. Và: "The agent must not remove or weaken REQUIRED checks simply to make the task
   pass."
4. `AGENTS.md` §1 hàng 10: Completion gates sống ở `docs/tasks/*.md`, **FROZEN 2026-08-23**.
   Viết acceptance criteria cho `T-06` **bây giờ**, sau khi đã biết kết quả, là đúng thứ mà cơ
   chế đóng băng gate tồn tại để ngăn.

Nói thẳng: nhiệm vụ #2 của phiên này ("kiểm tra T-06 Completion Gate / acceptance criteria
canonical") **không thực hiện được vì đối tượng kiểm tra không tồn tại**.

Ghi cho công bằng: `T-05`, `T-07`, `T-08`, `T-10`, `T-11`, `T-00` cũng không có file — đó là
chuẩn cho task **chưa mở**. Sự vắng mặt của file `T-06` nhất quán với "T-06 chưa từng được mở
như một task", và đó chính xác là vấn đề.

---

## 5. Thẩm quyền ghi `DONE`

`STATE_AUTHORITY.md` § "The State Machine And Who May Write It":

| `DONE` | **Owner, hoặc một completion authority được chỉ định** |

Tiền lệ trong repo này: `WP-A1` → `DONE` được ghi kèm *"DONE do Owner xác nhận tại Owner
Checkpoint 2026-09-03 (`DEC-028`)"* — tức qua một **Owner Decision có số hiệu**, không qua
session prompt.

`AGENTS.md` §1: *"An Owner Decision in `PROJECT/PROJECT_DECISIONS.md` outranks any session
prompt. **A session prompt NEVER outranks canonical governance.**"*

Session prompt của phiên này không phải Owner Decision, và agent **không được tự mint** một
Owner Decision. Đây là lý do độc lập thứ ba khiến `T-06` → `DONE` không thực hiện được ở đây.

Tương tự với `BLK-001 = RESOLVED`. Trên **thực tế** blocker đã gỡ (Owner khai `api.binance.com`
→ 200, `data.binance.vision` → 200, canonical fetch hoàn tất). Nhưng E1 của hai HTTP 200 đó
nằm trên máy Owner, không trong repo; và `BLK-001` là mục trong `PROJECT_PROGRESS.md`
§ Active Blockers, đổi nó là đổi state canonical. Cần evidence trong repo + Owner ghi nhận.

---

## 6. `DEC-003` / đối chiếu hai máy — trả lời nhiệm vụ #5

Câu hỏi: đây có phải REQUIRED condition chưa đáp ứng, và có làm **invalid** `T-06` không?

**Trả lời: KHÔNG làm invalid.** Căn cứ, đọc nguyên văn:

- `DEC-003` § Decision: cái **bắt buộc** là *"Verdict chính thức bắt buộc chạy trên dữ liệu
  Binance thật"*. Phần hai máy được nêu là *"Đường đi được `docs/DATA_SOURCES.md` **chấp nhận
  khi IP bị chặn**"* — tức quy trình cho **tình huống copy dữ liệu giữa hai máy**.
- `docs/DATA_SOURCES.md` § "Nếu IP Việt Nam bị chặn" xác nhận đúng khung đó: fetch ở VPS →
  copy `data/raw/` về → *"Kiểm tra bằng cách chạy `ethdca freeze` ở cả hai máy"*.
- Owner khai `BLK-001` đã gỡ **trên chính máy production-realistic** và fetch hoàn tất ở đó.
  Nếu fetch và official run cùng một máy, **không có bước copy nào để đối chiếu** ⇒ phép đối
  chiếu hai máy về mặt kỹ thuật là N/A.

Vậy nó **không phải** acceptance criterion của `T-06` (điều đó sẽ phải nằm trong Completion
Gate của `T-06`, thứ không tồn tại). Nó là **biện pháp đối trọng** đã công bố cho các giới hạn
provenance. Và ở vai trò đó, nó kích hoạt `H-06` — xem §7.

Điểm cần Owner biết: `docs/CONVENTIONS.md` công bố **hai** giới hạn và cả hai đều chỉ đúng
**một** biện pháp đối trọng là `ethdca freeze` hai máy theo `DEC-003` — giới hạn nhãn `source`
(`F-PRE008-01`) và giới hạn độ phủ (`missing_count`/`expected_count`). Nếu phép đối chiếu
không được thực hiện, hai giới hạn đó **đứng nguyên, không có đối trọng**, trên chính run đã
phát verdict. Điều đó không làm số liệu sai; nó làm mất khả năng **chứng minh** dữ liệu đúng
là của Binance. Với verdict `DO_NOT_BUILD` (chiều bảo thủ, không dẫn tới xuống tiền) hệ quả
nghiệp vụ là thấp — nhưng đây là quyết định của Owner, không phải của agent.

---

## 7. Hardening retrigger — nhiệm vụ #3 và #4

Rà **toàn bộ** 28 hạng mục / 32 khối `RE_TRIGGER_CONDITION`. 15 hạng mục có vế chạm `T-06` /
official run / dữ liệu Binance thật / môi trường production-realistic. Đánh giá từng vế:

### KÍCH HOẠT — cần Owner disposition

| Mục | Vế | Bằng chứng | Ghi chú |
|---|---|---|---|
| **H-13** | vế 1 — *"`T-06` sắp chạy mà giới hạn `row_count` VẪN CHƯA được công bố ở `docs/CONVENTIONS.md`"* — đánh dấu **"re-trigger BẮT BUỘC"** | `grep row_count docs/CONVENTIONS.md` → chỉ có `row_count > 0` / `empty_series` / `missing_count`. Giới hạn thật (`row_count` nằm ngoài mọi checksum, không bao giờ đối chiếu với file) **KHÔNG được công bố**. `CONVENTIONS.md` công bố giới hạn `source` và giới hạn độ phủ, **không** công bố `row_count`. | **Mạnh nhất trong phiên.** `H-13` từng là `CONFIRMED BLOCKING`; khi hạ xuống HARDENING, nghĩa vụ công bố được giữ lại tường minh (*"Nghĩa vụ KHÔNG được đánh rơi khi hạ cấp"*), disposition (b) diff = 0 nên **không tiêu repair cycle** (`DEC-012`). Official run đã chạy khi nghĩa vụ này chưa thi hành. |
| **H-06** | vế 1 — *"biện pháp đối trọng `DEC-003` (đối chiếu hai máy) KHÔNG được thực hiện cho `T-06`"* | Không có evidence nào trong repo cho thấy phép đối chiếu đã chạy. Vế này **không** điều kiện hoá theo kịch bản copy. | Xem §6. Cần Owner xác nhận: đã chạy `ethdca freeze` đối chiếu hay chưa. |
| **H-01** | vế 1 — *"official run (`T-06`) sắp chạy trên một máy KHÔNG bảo đảm được `git status --porcelain` rỗng tại thời điểm chạy"* | Chính Owner khai worktree lúc chạy có `?? data/`. `git status --porcelain` hiển thị file untracked ⇒ **không rỗng**. | `code_commit` ghi SHA sạch cho một cây không rỗng. Không đổi con số; làm yếu khả năng tái lập bit-chính-xác. |

### ĐIỀU KIỆN ĐÃ THOẢ — phép kiểm chứng nay ĐẾN HẠN, chưa chạy được

| Mục | Vế | Vì sao chưa kết luận được |
|---|---|---|
| **H-16** | *"Khi `T-06` chạy trên dữ liệu Binance THẬT và dataset official chứa ít nhất một ngày daily thiếu: đối chiếu `ma200`/`ma_ratio`/`rsi14` quanh mọi ngưỡng quyết định"* | `T-06` **đã** chạy trên dữ liệu thật ⇒ nửa đầu điều kiện THOẢ. Nửa sau cần dataset official để biết có ngày daily thiếu. Dataset không có trong checkout này. **Nếu tồn tại một ngày mà lệch ULP đủ lật một so sánh ngưỡng ⇒ mục này thành BLOCKING và quay về `CAP-DATA`.** |
| **H-24** | *"official run (`T-06`) cho thấy trường hợp này xảy ra và ảnh hưởng đáng kể tới kết quả"* | Cần đọc counter Opportunity zone trong artifact official. |
| **H-25** | *"official run (`T-06`) cho thấy trường hợp này xảy ra và ảnh hưởng đáng kể tới kết quả hoặc tới số liệu báo cáo BT §16"* | Cần đọc counter Crash zone trong artifact official. |
| **H-27** | vế 1 — *"quy trình vận hành `T-06` KHÔNG kiểm được rằng máy chạy official run là một git checkout của CHÍNH repo dự án"* | **Không có quy trình vận hành `T-06` dạng văn bản nào tồn tại** (chính `H-28` vế 2 xác nhận điều đó chưa được viết). Không có văn bản ⇒ không thể đã kiểm. Giảm nhẹ: `provenance_resolved=true` và `code_commit` khớp HEAD canonical thật. |
| **H-04** / **H-14** | vế *"quy trình vận hành `T-06` cho phép thao tác tay trên `lineage.json`"* | Cùng lý do: quy trình chưa thành văn ⇒ chưa xác định được. |

### KHÔNG kích hoạt — GIỮ HARDENING

| Mục | Lý do |
|---|---|
| **H-02** | Vế 1 nói về **tái lập** trên máy có `tzdata` khác. Chưa có lần tái lập nào. |
| **H-03** | Vế 2 (`dev_limit != None` ở official run) KHÔNG thoả: `official_reason=verified` — nếu `dev_limit` được đặt thì theo bản sửa S017 lý do sẽ là `dev_limit_set`. Vế 3 đã kích hoạt và **đã được Owner disposition tại `DEC-028` điểm 6**, giữ HARDENING. |
| **H-05**, **H-07** | Không vế nào thoả. |
| **H-28** | Vế 2 (*"quy trình vận hành `T-06` được viết thành văn bản"*) chưa xảy ra ⇒ chưa kích hoạt. Nhưng chính sự **không tồn tại** của văn bản đó là đầu vào cho `H-27`/`H-04`/`H-14` ở trên. |

**Không finding nào ở trên được biến thành task trong phiên này** (`AGENTS.md` §3: *"A finding
is not a task"*). Không task ID mới, không work package mới, không repair cycle nào bị tiêu.

---

## 8. Quan sát mới (KHÔNG phải task, KHÔNG phải BLOCKING)

**Lockfile khai Python `3.11.15`, official run khai Python `3.11.16`.**
`pyproject.lock` có dòng chú thích `# Python: 3.11.15` kèm tuyên bố *"SINH TỪ MÔI TRƯỜNG
THẬT … phiên bản đọc bằng `importlib.metadata` trên **chính interpreter đã chạy backtest**"*.
Canonical checkout của phiên khai Python `3.11.16`.

- `test_a1_08_lockfile_matches_installed_environment` **bỏ qua** mọi dòng bắt đầu bằng `#`,
  nên **không test nào** bắt được sai lệch này.
- Nó **không** làm `dependency_lock_hash` sai: hash là sha256 của **chính file**, file không
  đổi, và hash đã được kiểm khớp (§2 #2).
- Phân loại đề xuất: tài liệu provenance bị lạc hậu, cùng lớp với `H-02` (lockfile không phủ
  hết môi trường), thuộc `CAP-PROV`. **Cần Owner routing** — phiên này không tự phân loại,
  không tự sửa.

**Hai validator báo PASS rỗng.** `validate_evidence.py` và `validate_task_completion.py` đều
in `Checked 0 …` vì chúng glob `TASK-*.md` trong khi repo dùng `T-*.md`/`WP-*.md` (đã route
thành `H-08`). Theo `STATE_AUTHORITY.md` § Vacuous Validation — *"'Checked 0 records' is not a
meaningful PASS"* — **PASS của hai validator này không được đọc là xác nhận** rằng evidence
của `T-06` đầy đủ. Chúng sẽ không bắt được sự vắng mặt đó dù có.

---

## 9. Trạng thái sau `T-06` — nhiệm vụ #7

Đọc từ Ready Gate **đã đóng băng** của từng gói, không từ suy luận:

| Hạng mục | Trạng thái | Căn cứ canonical |
|---|---|---|
| **T-06** | **`PLANNED`** (KHÔNG đổi) | `PROJECT_PROGRESS.md` dòng 196. Không có Owner Decision, không có gate, evidence không trong repo. |
| **WP-B1** | **`BLOCKED`** | Ready Gate: `- [ ] **Dependency T-06 DONE**` — chưa tick. (`WP-A5 DONE` thì đã thoả.) |
| **WP-B2** | **`BLOCKED`** | Ready Gate: `- [ ] **Dependency T-06 DONE**` — chưa tick. |
| **WP-B3** | **`BLOCKED`** | Ready Gate: `- [ ] **Dependency T-06 DONE**` **và** `- [ ] **Dependency WP-C2 DONE**`. `WP-C2` hiện `BLOCKED` ⇒ ngay cả khi `T-06` xong, `CHECK-B3-02` sẽ `BLOCKED` và gói không `DONE` được. |
| **GATE-B** | **CHƯA MỞ / KHÔNG CLOSED** | Định nghĩa (dòng 200): `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`. Cả ba `BLOCKED`. |
| **T-07** | **`PLANNED`, bị chặn** | Điều kiện: sau `T-06` **và** `GATE-B`. Cả hai chưa đạt. Chặn tiếp `T-11`. |

Cả ba gói lớp B **BLOCKED bởi đúng một mắt xích**: `T-06` chưa `DONE`. Phiên này **không**
thực thi `WP-B1/B2/B3` (nhiệm vụ #8).

Lưu ý trình tự Owner đã treo từ trước (`RSK-007`, và ghi chú ở dòng 197): roadmap đặt `WP-B1`
**sau** `T-06`, nhưng `T-06` mới là nơi phát verdict official — nên phần chính sách của
`F-S015-01` lẽ ra phải đóng **trước** khi verdict của `T-06` được coi là có thẩm quyền. §2.1
cho thấy với **run cụ thể này** khiếm khuyết đó không thể đã ảnh hưởng verdict (nhánh
`DO_NOT_BUILD` được lấy trước khi `any_true` được đọc). Điều đó **thu hẹp** nhưng không xoá
câu hỏi trình tự của Owner.

---

## 10. Validator đã chạy — nhiệm vụ #9

| Validator | Kết quả |
|---|---|
| `branch_authority_check.sh --expect-branch claude/coindca-data-stream-vv0vwv` | **PASS** (kèm `INTEGRATION_DECISION_REQUIRED`, đã xử lý tại `DEC-029`) |
| `validate_governance.py` | **PASS** — 7 core, 7 project, 2 adapter, 5 hard-stop, 26 source invariant, 3 budget root, **28 hardening**, 13 production path row, **22 task file** |
| `validate_project_state.py` | **PASS** |
| `validate_structure.py` | **PASS** — 27 required path |
| `validate_routing.py` | **PASS** — 19 MAJOR task file, 0 manual override |
| `validate_evidence.py` | **PASS nhưng RỖNG** — `Checked 0` (H-08, xem §8) |
| `validate_task_completion.py` | **PASS nhưng RỖNG** — `Checked 0 DONE task` (H-08, xem §8) |
| `validate_easy_roadmap.py` | **PASS** |
| `task_registry_snapshot.sh` | 22 task file / 28 roadmap ID — **`T-06` không có file** (§4) |

Test suite: **NOT_TESTED**. Container không cài `pandas`/`pyarrow`/`pytest`, và phiên này
không sửa `src/`/`tests/` nên không phát sinh nghĩa vụ regression. Chỉ cài `numpy==2.4.6`
(đúng pin lockfile) để tái lập manifest hash ở §2. `production diff = EMPTY` — xác nhận bằng
`branch_authority_check.sh`.

---

## 11. Không có finding nào làm mất hiệu lực official run

Nói rõ vì đây là câu hỏi Owner đặt trực tiếp: **phiên này KHÔNG tìm thấy finding nào làm
invalid official run của `T-06`.**

- Provenance kiểm chứng được và **đúng**: `code_commit` khớp HEAD canonical, và
  `dependency_lock_hash` tái tính khớp tuyệt đối.
- Pre-T06 manifest freeze **tái lập chính xác** — cả 10 giá trị, cả 2 hash.
- Bốn kết quả gate và các signal **nhất quán** với ngưỡng đã đóng băng.
- Verdict `DO_NOT_BUILD` cùng đúng hai reason là **chính xác** thứ `decide_verdict` sinh ra
  từ các đầu vào đã khai; `can_proceed_to_app=false` đúng theo `v == "BUILD"`.
- `F-S015-01` **không thể** đã ảnh hưởng verdict này (§2.1).
- Verdict đi về chiều **bảo thủ** — `DO_NOT_BUILD` không dẫn tới bất kỳ hành động xuống tiền.

Ba vật cản ở §3/§4/§5 là **thiếu gate và thiếu evidence trong repo**, không phải bằng chứng
sai. Phân biệt này quan trọng: nó nói với Owner rằng việc cần làm là **ghi lại và hợp thức
hoá**, KHÔNG phải chạy lại (điều mà Master Index §6 vốn đã **cấm**).

---

## 12. Vì sao KHÔNG chạy lại, và vì sao artifact phải được bảo toàn NGAY

`Master Index §6` **cấm chạy lại official run** (dẫn lại trong biên bản `S017` §1: *"nếu
`T-06` chạy trong tình trạng này, provenance mất **VĨNH VIỄN**, không có đường vá"*).

Hệ quả vận hành, và đây là hạng mục **cấp bách nhất** của phiên này: artifact official đang
nằm trên máy Owner (`data/` untracked + `results/` bị gitignore + stash
`pre-T06-local-artifacts`) là **không thể thay thế**. Nếu chúng mất trước khi được ghi vào
repo, `T-06` **không bao giờ** còn có thể được hợp thức hoá — và cũng không được phép chạy lại
để tạo lại.

Phiên này **không** delete / stash / commit / drop bất cứ thứ gì (nhiệm vụ ràng buộc), và
container này không hề chứa chúng nên không có rủi ro từ phía phiên.

---

## Completion Gate Summary

Required:
Không xác định được — `T-06` không có Completion Gate (§4).

PASS: —
FAIL: —
BLOCKED: —
NOT_TESTED: toàn bộ, theo `EVIDENCE_STANDARD.md` (*"If not executed: Status = NOT_TESTED"*).

## Verification Evidence

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| S018-V-01 `code_commit` | PASS | E1 | `git rev-parse HEAD` = `5228130…`; `git ls-remote origin` khớp | S018 | 2026-09-03 |
| S018-V-02 `dependency_lock_hash` | PASS | E1 | `sha256sum pyproject.lock` = `9ea0150fcf27…` = khai báo | S018 | 2026-09-03 |
| S018-V-03 Gate 2 manifest freeze | PASS | E1 | tái sinh `generate_gate2_manifest()`: 19/1/18/200/219, hash `e34f92ae…` | S018 | 2026-09-03 |
| S018-V-04 Gate 3 manifest freeze | PASS | E1 | tái sinh `generate_gate3_manifest()`: 14/100/114, hash `ef30f657…` | S018 | 2026-09-03 |
| S018-V-05 FS-12 số học | PASS | E1 | `_advantage_share` tái tính: `net = -1.0935215802236702`, `share = 0.5806128427460292` ⇒ FALSE | S018 | 2026-09-03 |
| S018-V-06 nhất quán ngưỡng gate | PASS | E1 | ngưỡng đọc từ `gates.py`/`verdict.py`/`failure_signals.py` tại HEAD; xem bảng §2.1 | S018 | 2026-09-03 |
| S018-V-07 artifact official trong repo | **NOT_TESTED** | — | 5/5 record ID → 0 file; `dataset_hash` → 0 file; không `data/`/`results/`/`evidence/` | S018 | 2026-09-03 |
| S018-V-08 `T-06` Completion Gate | **NOT_TESTED** | — | không có `docs/tasks/T-06-*.md`; `CHECK-T06*` → 0 kết quả; `task_registry_snapshot.sh` xác nhận | S018 | 2026-09-03 |
| S018-V-09 `H-13` nghĩa vụ công bố | **FAIL** | E1 | `row_count` limitation KHÔNG có trong `docs/CONVENTIONS.md` | S018 | 2026-09-03 |
| S018-V-10 governance validators | PASS | E1 | 8/8 PASS; 2 trong đó rỗng (H-08) — xem §10 | S018 | 2026-09-03 |

## Files Changed

Created:
- `docs/sessions/S018-post-t06-evidence-closure.md` (file này)

Modified:
- `PROJECT/PROJECT_PROGRESS.md` — thêm mục Session History cho S018; **không** đổi trạng thái
  task, blocker, Tier, Effort hay dependency nào
- `PROJECT/HARDENING_BACKLOG.md` — ghi nhận điều kiện retrigger đã thoả ở `H-01`, `H-06`,
  `H-13`, `H-16`, `H-27`; **phân loại của cả năm mục KHÔNG đổi**, chờ Owner disposition

Deleted:
- (không)

## Key Decisions
- Không có. Phiên này không ra decision nào; nó dừng để Owner ra decision.

## Risks / Blockers
- `BLK-001` — **giữ ACTIVE trong sổ**, dù thực tế đã gỡ trên máy Owner. Evidence chưa trong repo.
- `T-06` — `PLANNED`, chặn `WP-B1/B2/B3` ⇒ `GATE-B` ⇒ `T-07` ⇒ `T-11`.
- **Rủi ro cấp bách:** artifact official không thể thay thế đang nằm ngoài repo (§12).

## Do Not Change Yet
- Không chạy lại official run `T-06` trong bất kỳ hoàn cảnh nào (Master Index §6).
- Không viết Completion Gate cho `T-06` sau khi đã biết kết quả, trừ khi Owner quyết định
  tường minh cách hợp thức hoá (§13 đường (A)/(B)).
- Không đổi thuật toán, không đổi ngưỡng, không sửa `src/`.
- Không xoá/stash/commit `data/` và không drop `stash@{0}` trên máy Owner.

## 13. `OWNER_DECISION_REQUIRED` — quyết định cần Owner ra

**OD-T06-01 — Bảo toàn artifact (CẤP BÁCH, làm trước mọi thứ khác).**
Sao lưu toàn bộ artifact official ra khỏi máy đang chạy trước khi mất. Chúng không thể tái tạo
và không được phép chạy lại để tạo lại.

**OD-T06-02 — Cơ chế đưa evidence official vào repo.** `results/` đang bị `.gitignore`. Chọn:
(a) ngoại lệ gitignore cho một đường dẫn evidence official; (b) evidence record trong `docs/`
mang đầy đủ payload + hash của năm run record; (c) cả hai. Không có evidence trong repo thì
`T-06` không thể `DONE` theo bất kỳ đường nào.

**OD-T06-03 — Hợp thức hoá gate cho `T-06`.** Chọn:
(A) tạo file `docs/tasks/T-06-*.md` với Completion Gate viết **từ tiêu chí đã đóng băng ở
`T-04`/BT §7–§10** (không phải từ kết quả đã biết), Owner đóng băng nó, rồi chấm `T-06` theo
đó; hoặc
(B) Owner ghi một `DEC-0xx` **dispositioning tường minh** sự vắng mặt của gate — tương tự
`LEGACY_GATE_COMPATIBILITY_REQUIRED` — nêu rõ vì sao official run vẫn có thẩm quyền dù chưa
đi qua Ready Gate / frozen Completion Gate.
Agent **không** được tự chọn giữa hai đường này.

**OD-T06-04 — `H-13`** (`row_count` chưa công bố, re-trigger BẮT BUỘC). Thi hành disposition
(b) đã được chấp thuận từ trước — công bố giới hạn trong `docs/CONVENTIONS.md`, cạnh giới hạn
`source`. Diff production = 0 ⇒ **không tiêu repair cycle** (`DEC-012`). Đây là mục sạch nhất
để đóng.

**OD-T06-05 — `H-06` / `DEC-003`.** Xác nhận: phép đối chiếu `ethdca freeze` hai máy có được
thực hiện cho `T-06` hay không. Nếu không, và Owner chấp nhận (xem §6 về hệ quả nghiệp vụ
thấp với verdict `DO_NOT_BUILD`), ghi `ACCEPT_AS_IS` kèm lý do.

**OD-T06-06 — `H-16` (có thể thành BLOCKING).** Từ dataset official: dataset có chứa ngày
daily thiếu nào không? Nếu có, chạy phép đối chiếu ULP `ma200`/`ma_ratio`/`rsi14` quanh mọi
ngưỡng quyết định. Nếu một ngưỡng bị lật ⇒ `H-16` thành **BLOCKING** và về `CAP-DATA`.

**OD-T06-07 — `H-01`.** Ghi nhận official run chạy trên worktree có file untracked (`?? data/`).

**OD-T06-08 — `H-24`/`H-25`.** Từ artifact official: hai trường hợp zone đó có xảy ra và có
ảnh hưởng đáng kể tới kết quả / số liệu BT §16 không?

**OD-T06-09 — `H-27`/`H-04`/`H-14`/`H-28`.** Quy trình vận hành `T-06` chưa bao giờ thành văn
bản. Owner quyết định có viết nó (đóng luôn `H-28` vế 2) hay ghi `ACCEPT_AS_IS` cho run đã
chạy.

**OD-T06-10 — Sai lệch Python patch** (§8): lockfile ghi `3.11.15`, run khai `3.11.16`. Route
theo governance (đề xuất: `CAP-PROV`, cùng lớp `H-02`). **Không phải task.**

## Next Recommended Session
Sau khi Owner ra `OD-T06-01`…`OD-T06-03`: một phiên **ghi evidence** đưa artifact official vào
repo theo cơ chế Owner chọn, rồi thi hành `OD-T06-04` (`H-13`, docs-only, diff = 0). Chỉ sau
khi `T-06` được hợp thức hoá `DONE` thì `WP-B1`/`WP-B2` mới rời `BLOCKED`; `WP-B3` còn cần
`WP-C2`.

## Files Next Agent Should Read
- `AGENTS.md` (§1 authority order, §3 hard-stops, §7 reading order — **chạy Step 0 trước**)
- `governance/v4/CORE/STATE_AUTHORITY.md` (ai được ghi `DONE`; Vacuous Validation)
- `governance/core/EVIDENCE_STANDARD.md`, `governance/core/TASK_READY_GATE_STANDARD.md`,
  `governance/core/TASK_COMPLETION_GATE_STANDARD.md`, `governance/core/TASK_MODE_STANDARD.md`
- `PROJECT/PROJECT_PROGRESS.md` (dòng 196 `T-06`; §Active Blockers `BLK-001`; `RSK-007`)
- `PROJECT/HARDENING_BACKLOG.md` (`H-01`, `H-06`, `H-13`, `H-16`, `H-24`, `H-25`, `H-27`, `H-28`)
- `PROJECT/PROJECT_DECISIONS.md` (`DEC-003`, `DEC-011`, `DEC-012`, `DEC-028`, `DEC-029`, `DEC-030`)
- `docs/CONVENTIONS.md` (mục giới hạn cuối trang — nơi `H-13` phải được công bố)
- File này
