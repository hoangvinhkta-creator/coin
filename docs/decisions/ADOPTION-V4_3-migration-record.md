# ADOPTION RECORD — AI Engineering V4.3 Portable (overlay)

Loại artifact:
MIGRATION / ADOPTION RECORD — artifact duy nhất được tạo cho phiên adoption này
(§24 Artifact Budget). Đây KHÔNG phải task file, KHÔNG phải session handoff của một work
package, KHÔNG phải repair cycle.

Ngày:
2026-09-01

Branch:
`claude/wp-a1-provenance-v67k9h`

Start SHA:
`6c11a7eb2bb7c36c70343c591c402f4bf3f1c23f`

Governance version:
V3.2 (compact) → **V3.2 + AI Engineering V4.3 overlay**

Canonical entry point:
`AGENTS.md`

Phạm vi:
GOVERNANCE MIGRATION / OVERLAY. KHÔNG phải product remediation, KHÔNG phải WP-A1 repair
cycle, KHÔNG phải S009, KHÔNG phải roadmap expansion, KHÔNG phải task creation.

---

## 1. MIGRATION_UNCERTAINTY — nguồn pack không có mặt trong môi trường

Chỉ thị adoption yêu cầu dùng nguyên bộ `AI_ENGINEERING_V4_3_PORTABLE` làm nguồn migration
và đọc tối thiểu `README.md`, `AGENTS.md`, `CORE/*`, `LESSONS_LEARNED.md`, `BOOTSTRAP/*`,
`PROJECT/*`, `templates/*`, `scripts/*`, `adapters/*`.

Đã tìm và **KHÔNG tìm thấy** pack:

    find / -xdev \( -iname "*AI_ENGINEERING*" -o -iname "*V4_3_PORTABLE*" \
        -o -iname "GOVERNANCE_V4.md" -o -iname "CAPABILITY_MODEL.md" \
        -o -iname "DELIVERY_LOOP.md" -o -iname "PRODUCTION_PATH_RULE.md" \)
    -> 0 kết quả

Pack cũng không có trong repo, trong lịch sử git, và không có trên branch nào của remote.

**Hệ quả phải nói thẳng:** nội dung `governance/v4/CORE/*` được soạn từ **ngữ nghĩa V4.3 do
chủ dự án phát biểu trong chỉ thị adoption** (§0 Owner Intent đã ratified, và các §7–§16
đặc tả chi tiết Capability Model, Finding Routing, Production Path Rule, Delivery Loop,
Budget, Absorption Limit, Minimal Fix, Confirmed/Provisional, Production Reachability).
Đây là nguồn có thẩm quyền của chủ dự án, nhưng nó KHÔNG phải văn bản gốc của pack.

    MIGRATION_UNCERTAINTY:
    CORE V4.3 trong repo này là bản dựng lại theo chỉ thị của chủ dự án, chưa được
    đối chiếu từng câu với văn bản gốc của AI_ENGINEERING_V4_3_PORTABLE.
    Khi pack có mặt, phải diff `governance/v4/CORE/*` với `CORE/*` của pack và
    bổ sung phần thiếu (đặc biệt LESSONS_LEARNED.md và templates/).

Đây KHÔNG phải cherry-pick vài câu rồi gọi là V4.3 adoption: toàn bộ bảy file CORE và toàn
bộ cơ chế (authority order, finding routing, budget không reset, absorption limit, năm
hard-stop, production reachability) đều được tích hợp. Nhưng nguồn văn bản là chỉ thị, và
điều đó được ghi nhận thay vì che đi.

Adoption KHÔNG dừng vì việc này: theo §27, "thiếu một convenience script" hay "cấu trúc
repo không giống portable pack" không phải hard-stop hợp lệ.

---

## 2. CONFLICT DETECTED — vị trí của CORE

Documentation:
`CLAUDE.md` (V3.2, "Compact Directory Layout"): static governance nằm dưới `governance/`
để giữ root mỏng; **"Do not move governance files back to root."**

Implementation:
V4.3 Portable đặt `CORE/` tại root của repo.

Risk:
Đặt `CORE/` ở root vi phạm một luật đang có hiệu lực của repo. Ép rename/di chuyển
`governance/` để giống pack vi phạm §3 (overlay, không rewrite) và có nguy cơ làm hỏng
đường dẫn mà 17 task file, 7 session file và 11 validator đang tham chiếu.

Recommended resolution — ĐÃ ÁP DỤNG:
CORE đặt tại `governance/v4/CORE/` với **đúng tên file và đúng thứ tự authority của V4.3**.
Entry point canonical duy nhất là `AGENTS.md` tại root. Chỉ có tiền tố đường dẫn khác;
tên, nội dung và thứ tự authority giữ nguyên. Mapping ghi trong `AGENTS.md` §1 và §6.
Không file cũ nào bị đổi tên hay di chuyển. Theo §5 chỉ thị: "không ép rename ngay, tạo
mapping rõ ràng".

---

## 3. CORE / PROJECT mapping

### 3.1 CORE (mới, project-agnostic)

| V4.3 canonical | File trong repo này |
|---|---|
| `CORE/CAPABILITY_MODEL.md` | `governance/v4/CORE/CAPABILITY_MODEL.md` |
| `CORE/GOVERNANCE_V4.md` | `governance/v4/CORE/GOVERNANCE_V4.md` |
| `CORE/DELIVERY_LOOP.md` | `governance/v4/CORE/DELIVERY_LOOP.md` |
| `CORE/STATE_AUTHORITY.md` | `governance/v4/CORE/STATE_AUTHORITY.md` |
| `CORE/RISK_MODEL.md` | `governance/v4/CORE/RISK_MODEL.md` |
| `CORE/REVIEW_PROTOCOL.md` | `governance/v4/CORE/REVIEW_PROTOCOL.md` |
| `CORE/PRODUCTION_PATH_RULE.md` | `governance/v4/CORE/PRODUCTION_PATH_RULE.md` |

Đã kiểm: không file CORE nào chứa `WP-A1`, `ETH`, `Binance`, `Buy Score`, task ID, tên
branch, hay finding ID. Ranh giới CORE/PROJECT được giữ.

### 3.2 PROJECT — MAP vào file đã có (KHÔNG duplicate source of truth)

| V4.3 canonical | Canonical file đã có trong repo | Hành động |
|---|---|---|
| `PROJECT_PROFILE` | `PROJECT/PROJECT_PROFILE.md` | MAP — giữ nguyên |
| `PROJECT_STATE` | `PROJECT/PROJECT_PROGRESS.md` | MAP — giữ nguyên, vẫn là roadmap source of truth duy nhất |
| `RISK_REGISTER` | `PROJECT/PROJECT_PROGRESS.md` § Active Risks + § Active Risks — Governance/Tooling | MAP — KHÔNG tạo file mới, tránh duplicate |
| `COMPLETION_GATES` | `docs/tasks/*.md` (FROZEN 2026-08-23) | MAP — giữ nguyên, không đụng |
| `PROJECT_DECISIONS` | `PROJECT/PROJECT_DECISIONS.md` | MAP — giữ nguyên |
| `SESSION_HANDOFF` | `docs/sessions/` + `governance/templates/SESSION_HANDOFF_TEMPLATE.md` | MAP — giữ nguyên |

### 3.3 PROJECT — TẠO MỚI (thật sự chưa tồn tại)

| V4.3 canonical | File mới | Vì sao phải tạo |
|---|---|---|
| `CAPABILITY_REGISTRY` | `PROJECT/CAPABILITY_REGISTRY.md` | Repo chưa có khái niệm capability; dẫn xuất từ roadmap hiện có |
| `PRODUCTION_PATHS` | `PROJECT/PRODUCTION_PATHS.md` | Chưa từng khai báo; cần cho finding routing và đo budget |
| `REVIEW_BUDGET_LEDGER` | `PROJECT/REVIEW_BUDGET_LEDGER.md` | Repo chưa từng có mô hình budget đếm được |
| `HARDENING_BACKLOG` | `PROJECT/HARDENING_BACKLOG.md` | Chưa có nơi chứa hardening + re-trigger |

Không giá trị nào trong bốn file này được điền giả để validator PASS. Chỗ nào không đủ dữ
liệu lịch sử thì ghi `MIGRATION_UNCERTAINTY` hoặc `OWNER_DECISION_REQUIRED`.

### 3.4 Adapter

| V4.3 | File | Trạng thái |
|---|---|---|
| `adapters/CLAUDE.md` | `CLAUDE.md` | Chuyển thành ADAPTER; trỏ về `AGENTS.md`; giữ nguyên Language Rule, lifecycle token, `CONFLICT DETECTED`, Compact Layout, Progress Questions, Scope Expansion |
| `adapters/CODEX.md` | `CODEX.md` | TẠO MỚI; cùng authority semantics với `CLAUDE.md` |

Nội dung V3.2 bị lược khỏi `CLAUDE.md` là các mục **chỉ trỏ tới** `governance/core/*` —
các file đó không đổi và vẫn có hiệu lực qua `AGENTS.md` §4. Không luật nào bị mất.

---

## 4. Capability + Vertical Slice + Production Paths

Xem `PROJECT/CAPABILITY_REGISTRY.md` và `PROJECT/PRODUCTION_PATHS.md`.

Tóm tắt: Vertical Acceptance Slice hiện tại là đường
`dữ liệu thật → lineage chứng minh được → dataset đủ tư cách → pipeline 18 bước → gate/benchmark/control → run record tự chứng minh → VERDICT`,
tức chính `T-06`. Lát cắt này **chưa chạy lần nào**, nên chưa có Golden trace, nên chưa
capability nào có bằng chứng Production Reachability ở mức Golden.

---

## 5. RECLASSIFICATION — finding đang mở của WP-A1

**KHÔNG sửa mã. KHÔNG mở repair. KHÔNG tạo task ID.** Đây thuần tuý là định tuyến lại
trạng thái governance theo `governance/v4/CORE/REVIEW_PROTOCOL.md`.

Nguồn đọc: `docs/reviews/E2-WP-A1-provenance-round3.md`,
`docs/reviews/E2-WP-A1-provenance.md`, `docs/decisions/PRE-S008-WP-A1-decision-pack.md`,
`docs/tasks/WP-A1-provenance-va-tai-lap.md` (gate FROZEN),
`PROJECT/PROJECT_PROGRESS.md` (risk register), `PROJECT/PRODUCTION_PATHS.md`.

Finding đã ĐÓNG ở vòng ba (`F-E2A1-01`, `-02`, `-05`, `-07`) không được reclassify — đóng
là đóng.

### 5.1 CONFIRMED BLOCKING (5 finding / 4 hạng mục khắc phục)

Mỗi mục dưới đây thoả ĐỒNG THỜI cả ba điều kiện của §8.

---

**`F-E2A1-03` — provenance suy biến im lặng ngoài môi trường editable install**

    PRODUCTION SOURCE:     nguồn 1 + 2 — `src/eth_dca_os/reporting.py` (`_REPO_ROOT`,
                           `_get_code_commit`, hash lockfile) + `pyproject.lock` hiện tại.
    PRODUCTION PATH:       reporting.py -> save_run -> backtest_runs.jsonl. Kích hoạt trong
                           venv sạch cài từ lockfile — ĐÚNG môi trường mà CHECK-A1-09 yêu
                           cầu và là môi trường dự kiến của máy chạy T-06.
    BUSINESS CONSEQUENCE:  record ghi `code_commit='unknown'` và
                           `dependency_lock_hash='no-lockfile'` KHÔNG cảnh báo. Master Index
                           §6 CẤM chạy lại official run để sửa -> mất provenance VĨNH VIỄN,
                           đúng thứ WP-A1 sinh ra để chặn.
    COMPLETION GATE/RISK:  Exit Criteria WP-A1 "không defect nghiêm trọng nào chưa xử lý";
                           follow-up BẮT BUỘC #1 của E2 vòng ba; RSK-006.
    REPRODUCTION EVIDENCE: E2 vòng ba — reviewer tự dựng venv sạch, cài project, đọc record.
                           Mức E2. `reporting.py` không đổi một dòng trong `a0c278a`.

---

**`F-E2A1R3-03` — contract case 13 chưa thi hành: `official_reason` = `'verified'` thay vì `dev_limit_set`**

    PRODUCTION SOURCE:     nguồn 1 + 2 — `pipeline.run_gate1/2/3` và giá trị `--dev-limit`
                           thật của `cli.py`.
    PRODUCTION PATH:       mọi lần chạy dev. `save_run` ghi cặp mâu thuẫn
                           `{"official": false, "official_reason": "verified"}` vào
                           `*_metrics.json`. Mã `dev_limit_set` không tồn tại trong `src/`.
    BUSINESS CONSEQUENCE:  reason code không phân biệt được nguyên nhân — nguyên nhân dev bị
                           che hoàn toàn. Trực tiếp phá yêu cầu "reason code phải phân biệt
                           được nguyên nhân".
    COMPLETION GATE/RISK:  contract §10 decision pack đã ĐÓNG BĂNG ("S008 thực thi đúng bảng
                           này, không tự thêm/bớt case"); lý do FAIL #2 của E2 vòng ba;
                           follow-up BẮT BUỘC #2.
    REPRODUCTION EVIDENCE: reviewer chạy `run_gate1(prep, out, dev_limit=5)` và
                           `run_gate2(prep, out, limit=3)`, đọc giá trị trả về. Mức E2.
                           `test_ec_13` không khẳng định mã lý do nên oracle yếu hơn contract.

---

**`F-E2A1R3-01` — `row_count` nằm ngoài mọi checksum và không bao giờ đối chiếu với file**

    PRODUCTION SOURCE:     nguồn 1 — `_dataset_hash` / `verify_lineage` /
                           `official_eligibility` trong `data/dataset.py`, và kịch bản fetch
                           "archive trả DataFrame rỗng" dựng từ mã `fetch_all` thật.
    PRODUCTION PATH:       `official_eligibility` là enforcement point canonical DUY NHẤT
                           (RULE-14). Trong kịch bản archive trả DataFrame rỗng, lớp
                           `row_count` là lớp DUY NHẤT chặn được — lớp nhãn không cứu.
    BUSINESS CONSEQUENCE:  đây là lớp phòng thủ ĐÃ ĐƯỢC DÙNG ĐỂ ĐÓNG một finding CHẶN
                           (`F-E2A1-01`). Sửa đúng MỘT SỐ NGUYÊN trong `lineage.json` biến
                           dataset có một series rỗng hoàn toàn thành `(True,'verified')`.
                           Kiểu chuỗi `"999"` hoặc `True` cũng qua được.
    COMPLETION GATE/RISK:  follow-up BẮT BUỘC #3 của E2 vòng ba — "Không được để nó ở trạng
                           thái không sửa và không công bố"; RSK-008.
    REPRODUCTION EVIDENCE: reviewer làm rỗng thật `ETHUSDT_15m.parquet`, dựng lineage trung
                           thực, sửa `row_count: 0 -> 140156`; mọi `file_hash` và
                           `dataset_hash` vẫn khớp. Mức E2.

    GHI CHÚ ĐỊNH TUYẾN: mục này KHÁC `F-PRE008-01` (H-06) ở đúng một điểm quyết định —
    giới hạn dán nhãn sai ĐÃ ĐƯỢC CÔNG BỐ, còn giới hạn `row_count` thì CHƯA. Vì vậy nó
    BLOCKING với HAI disposition đều hợp lệ, do chủ dự án chọn: (a) đối chiếu `row_count`
    với `len(pd.read_parquet(p))` trong `verify_lineage`; HOẶC (b) công bố giới hạn trong
    `docs/CONVENTIONS.md` cạnh giới hạn về `source`. Cả hai đều đóng được finding.

---

**`F-E2A1R3-06` (bao gồm `F-E2A1-08`) — tài liệu đã lệch so với mã**

    PRODUCTION SOURCE:     nguồn 1 — bất biến `REQUIRED_SERIES` coverage và `row_count > 0`
                           đang chạy trong `data/dataset.py`; nhãn `mixed` do `fetch_all`
                           thật sinh ra khi archive phủ một phần series.
    PRODUCTION PATH:       `docs/CONVENTIONS.md` không phải production path, nhưng nó được
                           Exit Criteria của WP-A1 NÊU ĐÍCH DANH. Đây là đường Completion
                           Gate, không phải đường production path — hai cơ chế độc lập.
    BUSINESS CONSEQUENCE:  người đọc tài liệu hiểu cơ chế MẠNH HƠN thực tế ở phần vừa được
                           sửa để đóng hai finding chặn; `mixed` là giá trị mà một run ĐỦ TƯ
                           CÁCH OFFICIAL ghi ra nhưng không có trong bảng taxonomy.
    COMPLETION GATE/RISK:  Exit Criteria WP-A1 "docs/CONVENTIONS.md ghi quy ước phân loại
                           nguồn" — CHƯA ĐẦY ĐỦ; follow-up BẮT BUỘC #4. `F-E2A1-08` đóng
                           cùng mục này theo chỉ dẫn của reviewer.
    REPRODUCTION EVIDENCE: đối chiếu tài liệu ↔ mã của reviewer + stub fetch cho ra
                           `lineage['source'] = 'mixed'` với `(True,'verified')`. Mức E2.

### 5.2 CONFIRMED HARDENING (7)

Đã ghi vào `PROJECT/HARDENING_BACKLOG.md`, mỗi mục kèm `RE_TRIGGER_CONDITION`:

| ID | Finding | Mục backlog |
|---|---|---|
| `F-E2A1-04` | `code_commit` không phân biệt worktree bẩn | H-01 |
| `F-E2A1-06` | lockfile không ghim tzdata | H-02 |
| `F-E2A1-09` | `run_controls` ghi `official` không thống nhất | H-03 |
| `F-E2A1R3-02` | `TypeError` thay vì `lineage_malformed` | H-04 |
| `F-E2A1R3-04` | `data_source` mức dataset không được kiểm | H-05 |
| `F-PRE008-01` | không hash nào phủ nhãn `source` (ĐÃ CÔNG BỐ) | H-06 |
| `F-E2A1R3-07` | `REQUIRED_SERIES` chưa là nguồn duy nhất | H-07 |

### 5.3 PROVISIONAL (0)

Không có. Toàn bộ finding đang mở đều đã được reviewer E2 chạy thật trên mã, nên đều
`CONFIRMED` theo `REVIEW_PROTOCOL.md`. Đây là điểm mạnh của hồ sơ WP-A1, ghi lại để không
ai hạ cấp một finding bằng cách gọi nó là "lý thuyết".

### 5.4 OUT_OF_SCOPE / OWNER_ASSIGNMENT_REQUIRED (2)

---

**`F-E2A1R3-05` — fetch bị cắt cụt vẫn đủ tư cách official → `OWNER_ASSIGNMENT_REQUIRED`**

Đây là finding NẶNG NHẤT về hệ quả nghiệp vụ trong toàn bộ tập: reviewer dựng kịch bản rất
thật của T-06 (archive chỉ tới 2020-01, REST bị chặn/rate-limit), dataset thiếu ~92% khoảng
thời gian được yêu cầu, `missing_count = 0`, và `official_eligibility` cho `(True,'verified')`.
`gap_report` chỉ đo khoảng trống GIỮA first và last quan sát được, không đối chiếu với
`start`/`end` đã yêu cầu; `official_eligibility` không nhìn `first_timestamp`/`last_timestamp`
ở bất kỳ đâu.

Vì sao KHÔNG gán vào WP-A4 dù reviewer gợi ý WP-A4 là "nơi tự nhiên": đã kiểm trực tiếp
`docs/tasks/WP-A4-ngu-nghia-du-lieu-xau.md`. Expected Touch Area của WP-A4 **loại trừ tường
minh** `src/eth_dca_os/data/` với lý do "gói này xử lý **ngữ nghĩa** dữ liệu xấu, không xử
lý việc **lấy** dữ liệu". Chín REQUIRED check của WP-A4 đã FROZEN và không check nào phủ
truncation-vs-requested-range. Hấp thụ vào WP-A4 đòi hỏi đổi Scope Lock đã khoá + một
`COMPLETION GATE CHANGE PROPOSAL` — thẩm quyền của chủ dự án.

Vì sao KHÔNG gán vào WP-A1 dù `data/` nằm trong Expected Touch Area của WP-A1: chạm
Absorption Limit — ngưỡng **A** (Effective Risk tăng: thêm một lớp bất biến dữ liệu mới vào
gói đã qua ba vòng E2) và ngưỡng **C** (thêm REQUIRED check vào một gate 11 check đã FROZEN).

    ABSORPTION_LIMIT_REACHED
    OWNER_ASSIGNMENT_REQUIRED

Hai ứng viên owner được nêu tên (`WP-A4`, `WP-A1`), mỗi ứng viên kèm điều kiện phải thoả.
**KHÔNG đặt ID mới.** Ghi nhận thêm, theo đúng lời reviewer: mục này phải đóng TRƯỚC T-06,
bất kể ai sở hữu.

---

**Khiếm khuyết glob validator → `OUT_OF_SCOPE`, đã có kênh Owner Decision**

Định tuyến về `CAP-GOVTOOL`. Đã nằm sẵn ở mục "Cần chủ dự án quyết định" #5 của
`PROJECT/PROJECT_PROGRESS.md`. Ghi vào backlog là H-08. Không tạo owner mới, không tạo task.

### 5.5 Kiểm đếm

Tập finding đang mở khi vào phiên adoption — 13 finding:
5 từ vòng hai còn mở (`F-E2A1-03`, `-04`, `-06`, `-08`, `-09`),
7 finding mới vòng ba (`F-E2A1R3-01`…`-07`), và `F-PRE008-01`.

| Phân loại | Số lượng | Finding |
|---|---|---|
| CONFIRMED BLOCKING | **5** | `F-E2A1-03`, `F-E2A1-08`, `F-E2A1R3-01`, `F-E2A1R3-03`, `F-E2A1R3-06` |
| CONFIRMED HARDENING | **7** | `F-E2A1-04`, `F-E2A1-06`, `F-E2A1-09`, `F-E2A1R3-02`, `F-E2A1R3-04`, `F-E2A1R3-07`, `F-PRE008-01` (H-01…H-07) |
| PROVISIONAL | **0** | — |
| OWNER_ASSIGNMENT_REQUIRED | **1** | `F-E2A1R3-05` |
| **Cộng** | **13** | khớp đúng tập đầu vào |

Ngoài tập 13 finding của WP-A1:

| Phân loại | Số lượng | Mục |
|---|---|---|
| OUT_OF_SCOPE | **1** | khiếm khuyết glob validator → `CAP-GOVTOOL` (H-08) |

Đã ĐÓNG ở vòng ba, KHÔNG reclassify: 4 (`F-E2A1-01`, `-02`, `-05`, `-07`).

Năm finding BLOCKING gộp thành **4 hạng mục khắc phục**, vì `F-E2A1-08` (taxonomy `mixed`)
đóng cùng `F-E2A1R3-06` theo chỉ dẫn của reviewer.

Task mới được tạo: **0**.

---

## 6. LEGACY_GATE_COMPATIBILITY

    LEGACY_GATE_COMPATIBILITY_REQUIRED: KHÔNG kích hoạt.

Đã đối chiếu: V4.3 overlay không đổi ngữ nghĩa của bất kỳ gate nào đã FROZEN ngày
2026-08-23, không đổi contract 20 case của PRE-S008, không đổi Exit Criteria của WP-A1.
Reclassification ở §5 chỉ gán nhãn định tuyến (BLOCKING/HARDENING/OUT_OF_SCOPE) cho finding
— nó KHÔNG hạ, không nâng, không xoá REQUIRED check nào.

Điểm cần chủ dự án lưu ý nhưng KHÔNG phải xung đột: 7 finding được phân loại HARDENING vẫn
giữ nguyên tư cách CONFIRMED và vẫn nằm trong danh sách "nên xử lý" của E2 vòng ba. Phân
loại HARDENING KHÔNG có nghĩa là chúng được bỏ qua — chúng có re-trigger.

---

## 7. WP-A1 — trạng thái KHÔNG bị đổi

    WP-A1 = IN_PROGRESS (giữ nguyên)
    CHECK-A1-01 .. CHECK-A1-10 = PASS (E2 xác nhận, giữ nguyên)
    CHECK-A1-11 (E2) = FAIL (giữ nguyên)
    GATE-A = KHÔNG ĐÓNG (giữ nguyên)
    T-06 = KHÔNG ĐƯỢC MỞ (giữ nguyên)

Phiên adoption KHÔNG chuyển WP-A1 sang DONE, KHÔNG mở repair cycle thứ tư, KHÔNG sửa
`src/`, KHÔNG chạy T-06, KHÔNG chạy Gate-A, KHÔNG merge main.

Escalation đang treo (giữ nguyên từ E2 vòng ba, adoption không quyết thay):
`ESCALATION_PROTOCOL.md` đã kích hoạt vì đây là lần thứ BA qua E2; vòng sửa tiếp theo cần
chủ dự án phê duyệt tường minh. Phân loại đề xuất của reviewer là `VERIFICATION_DEPTH`
(giữ Tier C, nâng Effort `xhigh` → `max`), KHÔNG phải `CAPABILITY_CEILING`.

---

## 8. Bootstrap — MIGRATION BOOTSTRAP, không phải project reset

Repo này đang chạy, không phải dự án trống. Không chạy bootstrap như repo mới.

Adoption Check đã xác nhận:

- [x] `PROJECT_PROFILE` = PRODUCT, đã tồn tại, không đổi
- [x] `PROJECT_STATE` đã tồn tại (`PROJECT_PROGRESS.md`), không đổi, vẫn là roadmap SoT
- [x] Task registry giữ nguyên 29 task, không thêm không bớt (xem §10)
- [x] Completion Gates FROZEN giữ nguyên hiệu lực
- [x] Capability và Vertical Slice được xác định từ roadmap hiện có
- [x] Production paths được khai báo
- [x] Review/repair budget được tái dựng từ git, không reset
- [x] Hardening backlog có re-trigger cho từng mục
- [x] Canonical entry point tồn tại và cả hai adapter trỏ về nó

**WP-A1 KHÔNG bị đưa về TASK-001.** Không task ID nào được đánh số lại.

---

## 9. Validator

| Validator | Kết quả | Nhận định |
|---|---|---|
| `validate_structure.py` | PASS — 27 required paths | Có nghĩa |
| `validate_project_state.py` | PASS | Có nghĩa |
| `validate_routing.py` | PASS — 17 MAJOR task, 0 manual override | Có nghĩa |
| `validate_easy_roadmap.py` | PASS | Có nghĩa |
| `validate_evidence.py` | PASS — **Checked 0 records** | **KHÔNG có nghĩa** — H-08 |
| `validate_task_completion.py` | PASS — **Checked 0 DONE task(s)** | **KHÔNG có nghĩa** — H-08 |
| `validate_governance.py` | MỚI — kiểm bất biến V4.3 | Xem §9.1 |
| `branch_authority_check.sh` | MỚI | Xem §9.1 |
| `task_registry_snapshot.sh` | MỚI | Xem §9.1 |

Không validator cũ nào bị xoá. Đã đánh giá overlap: `validate_governance.py` kiểm bất biến
**V4.3** (entry point, CORE/PROJECT boundary, budget không reset, hardening có re-trigger,
adapter không tự cấp authority, phát hiện vacuous pass). Không chồng lấn với validator V3.2
hiện có — những validator đó kiểm cấu trúc V3.2, routing và roadmap sync, đều vẫn có
invariant riêng đáng giữ.

### 9.1 Script mới

- `governance/scripts/governance/validate_governance.py` — bất biến V4.3.
- `governance/scripts/governance/branch_authority_check.sh` — xác nhận branch hiện tại là
  branch được uỷ quyền và cây làm việc không có thay đổi production path ngoài ý muốn.
- `governance/scripts/governance/task_registry_snapshot.sh` — chụp task registry để so
  before/after, dùng cho §10.

---

## 10. Task registry — before / after

Đo bằng `governance/scripts/governance/task_registry_snapshot.sh`, không đếm tay:

    BEFORE (start SHA 6c11a7e): count_roadmap_task_ids = 29 ; count_task_files = 20
                                (20 file dưới docs/tasks/ ngoài README.md;
                                 17 trong số đó là MAJOR đã ROUTED theo validate_routing.py)
    AFTER  (phiên adoption):    count_roadmap_task_ids = 29 ; count_task_files = 20

    diff BEFORE/AFTER -> RỖNG (registry giống hệt)
    Task ID mới được tạo trong phiên này: 0
    File dưới docs/tasks/ được thêm/sửa/xoá:  0

Xác nhận tường minh: KHÔNG có `WP-A8`, `WP-A9`, `S009`, `TASK-XYZ` hay ID tương tự nào được
sinh ra. Reclassification ở §5 tạo ra mục backlog (`H-01`…`H-08`) — đó là mục hardening có
re-trigger, KHÔNG phải task, không có Ready Gate, không có Completion Gate, không vào
roadmap.

---

## 11. Production code diff

    git diff --stat <start SHA>..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    -> RỖNG

Phiên này chỉ chạm `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `governance/v4/CORE/*`,
`governance/scripts/governance/*` (3 file mới), `PROJECT/*` (4 file mới) và file này.

---

## 12. Owner Decision còn thiếu

1. **Hạn mức budget cho `CAP-PROV`** — `OWNER_DECISION_REQUIRED`. Repo chưa từng có mô hình
   budget đếm được, nên "remaining" không tính ra được từ lịch sử. Xem
   `PROJECT/REVIEW_BUDGET_LEDGER.md` §1.
2. **Owner cho `F-E2A1R3-05`** (fetch cắt cụt vẫn official) — `OWNER_ASSIGNMENT_REQUIRED`.
   Hai ứng viên đã nêu, mỗi ứng viên kèm điều kiện. Phải đóng trước T-06.
3. **Phê duyệt vòng sửa WP-A1 tiếp theo** — `ESCALATION_PROTOCOL.md` yêu cầu phê duyệt
   tường minh cho lần thứ tư, kèm phân loại `VERIFICATION_DEPTH` mà reviewer đề xuất.
4. **Disposition của `F-E2A1R3-01`** — sửa (đối chiếu `row_count` với parquet) hay công bố
   giới hạn trong `docs/CONVENTIONS.md`. Cả hai hợp lệ; "không sửa và không công bố" thì
   không.
5. **`GOLDEN_BASELINE_SHA`** — `PENDING_OWNER_DATA / MIGRATION_REQUIRED` cho tới khi T-06
   chạy được.
6. Các mục tồn đọng từ trước, adoption KHÔNG đụng tới: `DEC-005`, `PH-01`, `BLK-001`,
   `PH-04`, glob validator (#5 cũ, nay là H-08).

---

## 13. Hành động NHỎ NHẤT tiếp theo theo V4.3

Câu hỏi V4.3 đặt ra không phải "còn bao nhiêu việc" mà "việc NHỎ NHẤT nào đưa Vertical
Slice tiến thêm một bước thật".

Trả lời: **`WP-A4`** (`CAP-DATA`, đang `READY`, Tier C / Effort xhigh, nằm trên đường găng
`T-04 → WP-A3 ✅ → {WP-A4 ∥ WP-A7 ✅} → WP-A6 → GATE-A → T-06`).

Vì sao KHÔNG phải WP-A1 dù nó có 4 finding BLOCKING: WP-A1 đang bị chặn bởi
`ESCALATION_PROTOCOL` — vòng sửa thứ tư cần chủ dự án phê duyệt tường minh (Owner Decision
#3). Đó là một trong năm hard-stop hợp lệ (`OWNER_DECISION_REQUIRED`), không phải một chỗ
dừng tuỳ tiện. WP-A4 không bị chặn bởi bất kỳ hard-stop nào và cũng không phụ thuộc WP-A1.

Ghi chú định tuyến kèm theo, để phiên sau không phải khám phá lại: khi WP-A4 được mở, nó
KHÔNG tự động nuốt `F-E2A1R3-05` — Scope Lock của WP-A4 loại trừ `src/eth_dca_os/data/`, và
việc đó cần Owner Decision #2 trước.

**DỪNG SAU BÁO CÁO NÀY.** Không mở repair, không mở S009, không tạo WP mới, không sửa
WP-A1, không chạy T-06, không chạy Gate-A, không merge main.
