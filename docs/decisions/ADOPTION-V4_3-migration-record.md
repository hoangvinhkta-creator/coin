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

> **ĐÃ ĐƯỢC GIẢI QUYẾT MỘT PHẦN — xem §14 SOURCE RECONCILIATION (2026-09-01).**
> Mục này giữ nguyên làm lịch sử; nó mô tả đúng tình trạng tại commit `62f8bac`.
> Source pack sau đó đã được chủ dự án cung cấp và đã được đọc thật. Kết luận
> "nội dung CORE là bản dựng lại theo chỉ thị" là **đúng**, và §14 chỉ ra chính xác
> những bất biến đã bị mất trong bản dựng lại đó, cùng những gì đã được khôi phục.

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

---

# 14. SOURCE RECONCILIATION (2026-09-01)

Phiên này **không phải** một adoption mới. Nó đối chiếu overlay V4.3 đã dựng tại `62f8bac`
với **source pack gốc**, và chỉ bổ sung delta cần thiết.

Không rewrite adoption. Không sửa product code. Không sửa WP-A1. Không mở WP-A4. Không tạo
task. Không reset budget. Không merge default branch.

## 14.1 Source authority

    Tệp:        AI_ENGINEERING_V4_3_PORTABLE.zip  (chủ dự án cung cấp)
    Đọc thật:   CÓ — giải nén và đọc, không suy diễn từ governance/v4 hiện có
    SOURCE_FILE_COUNT = 38
    Thư mục gốc: AI_ENGINEERING_V4_3_PORTABLE/

    SOURCE_STRUCTURE:
      AGENTS.md, README.md, PACK_MANIFEST.md, INSTALL_NEW_PROJECT.md, LESSONS_LEARNED.md
      CORE/            7 file
      BOOTSTRAP/       7 file
      PROJECT/         5 template
      GOLDEN_BASELINE/ 3 file
      templates/       4 file
      scripts/         4 file
      adapters/        2 file
      examples/        1 file

Ghi chú danh xưng: pack tự đặt tên `V4.3` ở `README.md` / `PACK_MANIFEST.md`, nhưng phần
lớn tiêu đề file CORE vẫn ghi `V4.1` / `V4.2`. V4.3 là **phần thêm** (`DELIVERY_LOOP.md`,
Exception-First, bốn metric, CONFIRMED/PROVISIONAL, Production Reachability) chồng lên thân
V4.1/V4.2, chứ không phải bản viết lại. Overlay của repo đặt tên `V4.3` cho cả bộ — đây là
khác biệt nhãn, không phải khác biệt ngữ nghĩa.

## 14.2 Sai lệch trạng thái đã phát hiện và xử lý TRƯỚC khi đối chiếu

Bản clone local của phiên này đứng ở `6c11a7e` và **không** chứa `62f8bac`. `62f8bac` chỉ
tồn tại như một object rời cho tới khi `git fetch origin --prune` cho thấy nó **đã ở đầu**
`origin/claude/wp-a1-provenance-v67k9h`.

Tức là: local branch đang **BEHIND upstream 1 commit** — đúng điều kiện mà
`branch_authority_check.sh` của source pack bắt (exit 4: "không được đọc PROJECT_STATE ở
trạng thái này"). Overlay lúc đó **không** có check này. Đây là bằng chứng chạy thật cho
delta `R-08`/`R-09` bên dưới, không phải giả thuyết.

Xử lý: `git merge --ff-only origin/...` — fast-forward thuần, không rewrite, không reset.

## 14.3 Semantic delta — theo THÀNH PHẦN, không theo file

| # | Thành phần V4.3 | Kết quả | Ghi chú |
|---|---|---|---|
| 1 | 5 hard-stop | **EXACT** | đủ 5, đúng tên |
| 2 | `UNAUTHORIZED_STOP = PROCESS_FAILURE` | EQUIVALENT | |
| 3 | Finding Routing (BLOCKING/HARDENING/OUT_OF_SCOPE) | EQUIVALENT | overlay đủ 3 điều kiện BLOCKING |
| 4 | `OWNER_ASSIGNMENT_REQUIRED` | EQUIVALENT | |
| 5 | `RE_TRIGGER_CONDITION` | EQUIVALENT | có validator kiểm |
| 6 | Review rộng / Repair hẹp | EQUIVALENT | |
| 7 | Production Path Rule — 4 nguồn + nguồn thứ 5 | EQUIVALENT | |
| 8 | Absorption Limit — 4 ngưỡng A–D | EQUIVALENT | ngưỡng đúng số |
| 9 | `DEFERRED_BY_MINIMAL_FIX` | EQUIVALENT | đủ trường |
| 10 | Production Reachability | EQUIVALENT | |
| 11 | Budget không reset (dọc + ngang) | EQUIVALENT | |
| 12 | Hardening Backlog | PROJECT_ADAPTED | `PROJECT/HARDENING_BACKLOG.md` |
| 13 | State Authority — nguồn sự thật đơn | PROJECT_ADAPTED | overlay **thêm** Vacuous Validation, source không có |
| 14 | `CONFIRMED` vs `PROVISIONAL` | **MISSING** (cơ chế) → đã khôi phục | overlay có tên gọi, thiếu bảng quyền + luật promote |
| 15 | Vertical Acceptance Slice — toạ độ bắt buộc | **MISSING** → đã khôi phục | §2.1–2.3 nguồn |
| 16 | `PENDING_OWNER_DATA` | **MISSING** → đã khôi phục | |
| 17 | Ba điều kiện tạo sibling task | **MISSING** → đã khôi phục | overlay chỉ có mặt phủ định |
| 18 | Định nghĩa "registration" | **MISSING** → đã khôi phục | |
| 19 | Module != Task | **MISSING** → đã khôi phục | |
| 20 | Absorption: tiền đề baseline + 9 bước + lựa chọn Owner | **MISSING** → đã khôi phục | |
| 21 | Ledger schema `base_sha`/`head_sha`, §7.1 trần, §7.3 chuyển tiếp | **MISSING** → đã khôi phục | |
| 22 | Bằng chứng chống proliferation (SET A / SET B) | **MISSING** → đã khôi phục | tool đã có sẵn |
| 23 | `Effective Risk = MAX(Local Risk, Blast Radius)` | **MISSING** → đã khôi phục | overlay định nghĩa Effective Risk theo nghĩa KHÁC |
| 24 | Local Risk / Blast Radius + ví dụ HIGH/MED/LOW | **MISSING** → đã khôi phục | |
| 25 | Golden giảm Blast Radius 1 bậc — 4 điều kiện | **MISSING** → đã khôi phục | |
| 26 | Số budget mặc định LOW 1 / MEDIUM 2 / HIGH 2 | **MISSING** → đã khôi phục | xem §14.6 |
| 27 | Định nghĩa "một repair cycle" + luật cumulative repair diff | **MISSING** → đã khôi phục | |
| 28 | `ACCEPT_AS_IS \| DESCOPE \| OWNER_EXTENSION` khi hết budget | **MISSING** → đã khôi phục | |
| 29 | Branch Authority machine-first + 3 ngưỡng Integration | **MISSING** → đã khôi phục | doc + script |
| 30 | Merge gate BLOCKED > 30 ngày | **MISSING** → đã khôi phục | |
| 31 | Artifact Budget (mặc định 4, thứ 5 cần Owner) | **MISSING** → đã khôi phục | |
| 32 | Artifact Internal Precedence | **MISSING** → đã khôi phục | |
| 33 | Clean worktree semantics | **MISSING** → đã khôi phục | |
| 34 | `ENVIRONMENT_REVERIFY_REQUIRED` | **MISSING** → đã khôi phục | |
| 35 | `POLICY_ADOPTED` vs `FULLY_ENFORCED` | **MISSING** → đã khôi phục | |
| 36 | Điều kiện hội tụ (10 mục) | **MISSING** → đã khôi phục | |
| 37 | "Những chuẩn không được mất" | **MISSING** → đã khôi phục | cầu nối sang governance V3.2 |
| 38 | Bảng state machine + AI được ghi state nào | **MISSING** → đã khôi phục | overlay `STATE_AUTHORITY.md` không hề có |
| 39 | Không dùng state chưa định nghĩa | **MISSING** → đã khôi phục | |
| 40 | Tiền kiểm 6 bước trước review | **MISSING** → đã khôi phục | |
| 41 | Verdict `ELIGIBLE_FOR_FREEZE` / `NOT_ELIGIBLE_FOR_FREEZE` | **MISSING** → đã khôi phục | |
| 42 | Chuỗi `INPUT → … → OUTPUT/CONSUMER` | **MISSING** → xem §14.7 (H-12) | ngữ nghĩa CORE đã ghi; bảng dự án giữ nguyên |
| 43 | Runtime thật cấp quyền sửa ("không trace → không fix") | **MISSING** → đã khôi phục | |
| 44 | Outcome là đơn vị delivery | **MISSING** → đã khôi phục | |
| 45 | Budget 2 tầng (session + cumulative) + giới hạn MEDIUM | **MISSING** → đã khôi phục | `<N>` là giá trị PROJECT |
| 46 | Golden PASS chứng minh MỘT đường + Golden sau phải khác biệt chủ đích | **MISSING** → đã khôi phục | |
| 47 | Progress chỉ tính CONFIRMED (BEFORE/AFTER, N có thể tăng) | **MISSING** → đã khôi phục | |
| 48 | Exception-First (tắt ở pha Golden, 3 điều kiện, báo theo lô, `AUTO+QUEUE=100%`, state phải persist) | **MISSING** → đã khôi phục | một trong hai bổ sung đầu bảng của V4.3 |
| 49 | Bốn metric đúng thứ tự (`SILENT_ERROR_RATE` → … → `MANUAL_WORK_REDUCTION`) | **MISSING** → đã khôi phục | bổ sung đầu bảng thứ hai của V4.3 |
| 50 | Bảy luật dễ nhớ | **MISSING** → đã khôi phục | |
| 51 | Bootstrap Gate + `bootstrap_scaffold.sh` + `BOOTSTRAP/*` + `INSTALL_NEW_PROJECT.md` | **NOT_APPLICABLE** | dành cho repo mới; repo này đang chạy |
| 52 | `PROJECT/*_TEMPLATE.md` | **NOT_APPLICABLE** | repo đã có file thật làm SoT |
| 53 | `templates/*` (TASK_SPEC, REVIEW_REPORT, …) | **NOT_APPLICABLE** | `docs/tasks/`, `docs/reviews/` đã có bản thật |
| 54 | `templates/OWNER_TASK_CREATION_PROPOSAL.md` | PROJECT_ADAPTED | trỏ sang `PROJECT/ROADMAP_CHANGE_PROPOSAL_*.md` đã có |
| 55 | `GOLDEN_BASELINE/*` | OPTIONAL → HARDENING **H-10** | repo chưa có Golden |
| 56 | `LESSONS_LEARNED.md` | OPTIONAL → HARDENING **H-11** | bất biến đã khôi phục; văn bản lý do không chép |
| 57 | `examples/README.md` | NOT_APPLICABLE | |
| 58 | CORE đặt ở root | **CONFLICT** (đã xử lý tại §2) | giữ `governance/v4/CORE/`; `AGENTS.md` vẫn là entry point |

    EXACT               = 1
    EQUIVALENT          = 10
    PROJECT_ADAPTED     = 4
    MISSING             = 36   (35 đã khôi phục trong phiên này, 1 định tuyến H-12)
    CONFLICT            = 1    (đã xử lý từ trước, không mở lại)
    NOT_APPLICABLE      = 6

Kết luận thẳng: overlay tại `62f8bac` **giữ đúng bộ khung định tuyến** của V4.3 (finding
routing, budget lineage, absorption, 5 hard-stop, reachability) nhưng **mất gần như toàn bộ
tầng chứng minh** của V4.1/V4.2 mà V4.3 chồng lên, cùng hai bổ sung đầu bảng của chính V4.3
(Exception-First và bốn metric). Đó là hệ quả trực tiếp của việc dựng lại từ chỉ thị thay vì
từ văn bản gốc — đúng như §1 đã cảnh báo.

## 14.4 REQUIRED DELTA — đã sửa

| ID | File | Nội dung |
|---|---|---|
| R-01 | `governance/v4/CORE/GOVERNANCE_V4.md` | thêm **Part II — The Proof Layer** (II.0–II.10) |
| R-02 | `governance/v4/CORE/CAPABILITY_MODEL.md` | thêm **Part II** (II.1–II.9) |
| R-03 | `governance/v4/CORE/DELIVERY_LOOP.md` | thêm **Part II** (II.1–II.10) |
| R-04 | `governance/v4/CORE/RISK_MODEL.md` | Local Risk / Blast Radius / `MAX()` / giảm Golden 4 điều kiện / HIGH ≠ STOP |
| R-05 | `governance/v4/CORE/PRODUCTION_PATH_RULE.md` | chuỗi `INPUT → … → OUTPUT/CONSUMER` |
| R-06 | `governance/v4/CORE/REVIEW_PROTOCOL.md` | tiền kiểm 6 bước, test BLOCKING dạng phủ định, verdict |
| R-07 | `governance/v4/CORE/STATE_AUTHORITY.md` | state machine + bảng quyền ghi + map sang lifecycle V3.2 |
| R-08 | `AGENTS.md` | **Bước 0** — chạy branch authority check TRƯỚC khi đọc state |
| R-09 | `governance/scripts/governance/branch_authority_check.sh` | fetch, default branch động, behind-upstream, detached `TARGET_SHA`, tracked worktree, 3 ngưỡng Integration, `STRICT_DIVERGENCE` |
| R-10 | `governance/scripts/governance/validate_governance.py` | kiểm **26 marker** bất biến để không mất lần nữa |

Nguyên tắc áp dụng: **bổ sung, không thay thế.** Không câu nào của overlay bị xoá; phần
khôi phục nằm trong các mục "Part II" / phần thêm cuối file, có ghi ngày đối chiếu. Không
file nào bị đổi tên hay di chuyển. Không tạo `CORE/` thứ hai ở root.

## 14.5 OPTIONAL DELTA — KHÔNG sửa, đã định tuyến

    H-09  danh sách production path bị nhân bản trong branch_authority_check.sh
    H-10  chưa có Golden Baseline → tầng budget thứ hai chưa đo được
    H-11  LESSONS_LEARNED.md không chép vào repo (bất biến đã khôi phục)
    H-12  PRODUCTION_PATHS.md khai báo theo file, chưa theo chuỗi dữ liệu

Cả bốn đều có `RE_TRIGGER_CONDITION`. Không mục nào sinh task ID.

## 14.6 Hệ quả cho budget — OWNER_DECISION_REQUIRED (KHÔNG tự áp dụng)

`PROJECT/REVIEW_BUDGET_LEDGER.md` ghi `ALLOWED BUDGET = CHƯA TỪNG ĐƯỢC ĐẶT` +
`MIGRATION_UNCERTAINTY`, với lý do "governance V3.2 chưa bao giờ định nghĩa mô hình budget".

Source pack **có** định nghĩa mặc định (`GOVERNANCE_V4.md` §4, nay là II.2):
LOW = 1, MEDIUM = 2, HIGH = 2 blocking repair cycle, gắn với lineage root.

`CAP-PROV` có `REPAIR CYCLES ĐÃ TIÊU = 2`. Nếu áp mặc định HIGH = 2 thì
`remaining = 0`, và WP-A1 chỉ còn ba nước: `ACCEPT_AS_IS`, `DESCOPE`, `OWNER_EXTENSION`.

**Ledger KHÔNG bị sửa trong phiên này.** Áp một trần budget hồi tố lên một capability đã
tiêu 2 cycle là quyết định của chủ dự án, không phải hệ quả tự động của việc đọc được source
pack. Ghi nhận:

    OWNER_DECISION_REQUIRED — Owner Decision #4
    Đặt `capability_repair_cycles_allowed` cho CAP-PROV.
    Mặc định theo source pack = 2 (Effective Risk HIGH). Đã tiêu = 2.
    Chọn: (a) chấp nhận mặc định → remaining = 0; hoặc
          (b) OWNER_EXTENSION kèm lý do; hoặc
          (c) đặt một trần khác kèm lý do.

Điều này KHÔNG reset gì cả: 2 cycle đã tiêu, 3 vòng E2 đã tiêu, và toàn bộ lineage
`CAP-PROV` giữ nguyên. Nó chỉ nêu con số trần mà trước đây chưa có nguồn.

## 14.7 WP-A1 — phân loại KHÔNG đổi

Đã kiểm từng bất biến khôi phục xem có bất biến nào làm đổi phân loại đã ghi tại `62f8bac`:

- `MAX(Local Risk, Blast Radius)` + giảm Golden — repo chưa có Golden nên chưa từng có
  path nào được giảm bậc; **không đổi**.
- Ba điều kiện BLOCKING — đã có đủ trong overlay từ trước; **không đổi**.
- `CONFIRMED` / `PROVISIONAL` — record ghi PROVISIONAL = 0; luật promote không tạo ra
  finding mới; **không đổi**.
- Luật cumulative repair diff — ledger đã ghi base/head SHA cho từng cycle; cách đếm 2 cycle
  vẫn đúng; **không đổi**.
- Chuỗi production path (H-12) — là khiếm khuyết chất lượng khai báo, không phân loại lại
  finding nào; **không đổi**.

    CLASSIFICATION_RECONCILIATION_REQUIRED = KHÔNG

Không finding nào bị sửa. Không code nào bị sửa. Không repair cycle nào được mở.

## 14.8 INTEGRATION_DECISION_REQUIRED — phát hiện mới, đo được

`branch_authority_check.sh` sau khi khôi phục đo được, trên chính branch này:

    ahead of default  = 28 commit(s)      (ngưỡng 10)
    divergence age    = 9 day(s)          (ngưỡng 3)
    divergence LOC    = 23870             (ngưỡng 5000)
    INTEGRATION_DECISION_REQUIRED: ahead>10 age>3d loc>5000

**Cả ba ngưỡng đều vượt.** Đây là Owner Decision theo `GOVERNANCE_V4.md` § II.3, KHÔNG phải
cảnh báo được đi qua trong im lặng. Phiên này KHÔNG merge default branch (bị cấm tường minh
trong chỉ thị) và KHÔNG tự chọn thay chủ dự án.

    OWNER_DECISION_REQUIRED — Owner Decision #5
    Chọn: integrate/merge sớm | cắt scope | chấp nhận divergence kèm lý do + hạn đánh giá lại.

Trước khi khôi phục delta R-09, ngưỡng này **không thể được phát hiện**: script cũ không đo
divergence. Đây là giá trị cụ thể của reconciliation, không phải parity hình thức.

## 14.9 MIGRATION_UNCERTAINTY sau đối chiếu

    MIGRATION_UNCERTAINTY = PARTIAL

**Đã RESOLVED:** nghi vấn "CORE V4.3 trong repo là bản dựng lại, chưa đối chiếu với văn bản
gốc". Source pack đã có mặt, đã đọc thật 38/38 file, đã đối chiếu theo thành phần, và 35
bất biến bị mất đã được khôi phục vào đúng bảy file CORE hiện có. Validator kiểm 26 marker
để không mất lần nữa (đã kiểm chứng bằng negative test: xoá một marker → FAIL).

**Còn PARTIAL, đúng hai mục — không dùng câu chung chung:**

1. `capability_repair_cycles_allowed` của `CAP-PROV` vẫn chưa có giá trị. Nguyên nhân đã
   ĐỔI: không còn là "chưa có mô hình" (source pack đã cung cấp mặc định 2 cho HIGH) mà là
   "việc áp trần hồi tố cần Owner Decision #4" — xem §14.6.
2. Chuỗi production path (H-12) chưa được khai báo, nên Effective Risk hiện chấm ở mức file
   chứ chưa ở mức đường dữ liệu.

Ngoài hai mục trên, không còn delta ngữ nghĩa nào giữa source pack và repo mà phiên này
biết mà không ghi.

## 14.10 Bằng chứng — đã chạy thật

    python3 governance/scripts/governance/validate_governance.py
      -> GOVERNANCE V4.3: PASS
         core_files_checked = 7        project_files_checked = 7
         adapters_checked = 2          hard_stops_checked = 5
         source_invariants_checked = 26
         budget_lineage_roots = 1      hardening_items = 12
         production_path_rows = 13     task_files_present = 20
      negative test: xoá 'MAX(Local Risk, Blast Radius)' khỏi RISK_MODEL.md -> FAIL
                     (validator KHÔNG vacuous)

    bash governance/scripts/governance/branch_authority_check.sh --expect-branch <branch>
      -> BRANCH AUTHORITY: PASS
         default branch resolved (KHÔNG đoán 'main'), behind upstream = 0,
         tracked worktree khai báo, production diff = EMPTY,
         INTEGRATION_DECISION_REQUIRED: ahead>10 age>3d loc>5000   (§14.8)
      STRICT_DIVERGENCE=1 -> rc=1  (ngưỡng thi hành được, không chỉ là văn bản)

    bash governance/scripts/governance/task_registry_snapshot.sh
      -> count_roadmap_task_ids = 29   (before = after)

    Validator legacy: KHÔNG xoá, KHÔNG sửa. H-08 (vacuous "Checked 0 records") giữ nguyên
    định tuyến.

    PRODUCTION CODE DIFF   = 0    (git diff -- src/eth_dca_os webapp pyproject.*)
    WP-A1 PRODUCT CODE DIFF = 0
    TASK REGISTRY DIFF     = 0    (29 → 29, không task ID mới)
    docs/tasks/            = 0 file thay đổi
    Ledger CAP-PROV        = 0 thay đổi

## 14.11 Owner Decision còn thiếu

Bổ sung vào danh sách ở §12 (không thay thế):

    #4  Trần repair budget của CAP-PROV (§14.6) — mặc định source pack = 2, đã tiêu = 2.
    #5  INTEGRATION_DECISION_REQUIRED (§14.8) — cả ba ngưỡng divergence đều vượt.

## 14.12 Hành động NHỎ NHẤT tiếp theo

§13 vẫn đúng về **công việc sản phẩm**: `WP-A4`.

Nhưng reconciliation này làm lộ hai Owner Decision chặn trước nó, và cả hai đều rẻ hơn bất
kỳ dòng code nào: **Owner Decision #5** (divergence — 28 commit / 9 ngày / 23.870 LOC chưa
tích hợp; càng để lâu càng đắt) rồi **#4** (trần budget CAP-PROV — quyết định WP-A1 còn
đường đi tiếp hay chỉ còn `ACCEPT_AS_IS`/`DESCOPE`).

Không mở WP-A4, không mở repair, không tạo task trong phiên này.
