# PROJECT DECISIONS

File này ghi các quyết định chiến thuật quan trọng xuyên phiên nhưng chưa đủ tầm để viết ADR.
Quyết định kiến trúc lớn đi vào `docs/adr/`.

---

## DEC-001 — Chọn Project Profile = PRODUCT

Date:
2026-08-23 (S000)

Task:
S000 — Project Open, bước 0–1

Decision:
Chọn profile **PRODUCT** cho dự án. Không chọn SOLO_LITE, không chọn TEAM_PRODUCTION.

Reason:
Công cụ lưu dữ liệu giao dịch/vốn thật của chủ dự án và thực hiện tính toán dẫn tới quyết định
xuống tiền thật, nên vượt ngưỡng SOLO_LITE ("không có dữ liệu production nhạy cảm"). Đồng thời
dự án không có đội ngũ, CI, staging hay người dùng ngoài để biện minh cho TEAM_PRODUCTION.
Chi tiết lập luận đầy đủ ở `PROJECT/PROJECT_PROFILE.md`.

Impact:
- Bắt buộc thêm các nhóm luật data model, business logic, backup/DR, data governance.
- Mọi task chạm lớp tính toán tài chính mang category `accounting_financial` → hard floor
  Tier ≥ C và Effort ≥ `high`.
- REQUIRED check thực thi được phải đạt tối thiểu E1.

Can Revisit After:
Khi có người thứ hai tham gia repo, hoặc khi công cụ được phát hành cho người khác dùng
(khi đó xét nâng lên TEAM_PRODUCTION).

---

## DEC-002 — Phiên S001 chạy ở chế độ AUDIT read-only

Date:
2026-08-23 (S000)

Task:
S000 — bước 5 (quyết định có mở đầu bằng AUDIT mode không)

Decision:
Profile dự án là PRODUCT, nhưng **phiên kế tiếp (S001) chạy ở chế độ AUDIT read-only**.
Trong S001 không được sửa bất kỳ file mã nguồn sản phẩm nào (`src/`, `webapp/`, `tests/`).
Đầu ra của S001 là Discovery Baseline + Audit Findings, không phải code.

Reason:
Toàn bộ code hiện có (26 module Python, ~3.400 dòng; webapp JS) được viết **trước khi**
governance được đưa vào repo, trong 11 commit không có phiên governance nào. Không tồn tại
bằng chứng đã ghi nhận nào cho việc code khớp spec. `00_SESSION_ORCHESTRATION.md` mục
"Large / Legacy Project" khuyến nghị đúng đường đi này: S000 mở dự án → S001 discovery →
S002 chốt roadmap → S003+ mới thực thi.

Chủ dự án cũng đã yêu cầu rõ trong S000: "chưa remediation hay refactor".

Impact:
- Không có dòng code sản phẩm nào bị sửa cho tới khi S002 chốt roadmap.
- Chế độ AUDIT là thuộc tính của phiên, không phải profile dự án. Không đổi DEC-001.

Can Revisit After:
S002 — Roadmap Finalization.

---

## DEC-003 — Dữ liệu tổng hợp không bao giờ được dùng để ra verdict

Date:
2026-08-23 (S000)

Task:
S000 — bước 4 (khảo sát bối cảnh repo)

Decision:
`ethdca synth` chỉ dùng cho dev/test. Verdict chính thức **bắt buộc** chạy trên dữ liệu
Binance thật. Đường đi được `docs/DATA_SOURCES.md` chấp nhận khi IP bị chặn là: chạy
`ethdca fetch` ở nơi có mạng (máy của chủ dự án hoặc VPS nước ngoài) → copy thư mục
`data/raw/` về → xác minh bằng cách chạy `ethdca freeze` ở cả hai máy và đối chiếu hash
manifest phải trùng khớp.

Reason:
Bằng chứng thu được trong S000: repo không có thư mục `results/` (và `.gitignore` loại trừ nó),
nên **chưa từng có official run nào**. Môi trường phát triển hiện tại bị chặn egress tới
Binance. `docs/INDEX.md` §4 ghi rõ kết quả chạy trên synth tự gắn cờ `official: false`.
`docs/DATA_SOURCES.md` khẳng định không có nguồn thay thế hợp lệ: đổi sang CoinGecko/sàn khác
là đổi dataset, tức phải mở version mới theo freeze rule (Master Index §6).

Impact:
- Official run nằm trên đường găng (critical path) tới mục tiêu cuối của chủ dự án.
- Bước này cần máy/VPS có mạng tới Binance — agent không tự làm được trong môi trường này.
- Mọi số liệu hiện có trong repo không được trích dẫn như kết quả thật.

Can Revisit After:
Không revisit. Đây là ràng buộc từ spec đã đóng băng.

---

## DEC-004 — Xác nhận Provider Mapping cho Tier A/B/C/D

Date:
2026-08-23 (S000)

Task:
S000 — bước 11

Decision:
Xác nhận mapping mặc định của `AGENT_CAPABILITY_MATRIX.md` còn hiệu lực:
A→Haiku, B→Sonnet, C→Opus, D→Fable. Effort khả dụng: `low|medium|high|xhigh|max`.
Execution Profile mặc định: `DEFAULT` (không dùng ULTRACODE).

Reason:
`AGENT_CAPABILITY_MATRIX.md` mục "Provider Mapping Rule" yêu cầu xác nhận model khả dụng
trong S000 và ghi nhận thay thế nếu có. Bốn lớp model đều khả dụng trong runtime hiện tại.

Impact:
Tier/Effort trong roadmap đọc theo mapping này. Nếu mapping đổi, ghi nhận ở đây mà không đổi
ngữ nghĩa Tier A/B/C/D.

Can Revisit After:
Bất kỳ lúc nào lớp model khả dụng thay đổi.

---

## DEC-005 — PENDING: Phạm vi công cụ được phép xây trước khi có verdict

Date:
2026-08-23 (S000) — **CHƯA CHỐT, chờ chủ dự án duyệt (task T-05)**

Task:
T-05 — DUYET: Quyết định phạm vi app so với cổng verdict

Vấn đề:
Mục tiêu cuối của chủ dự án là công cụ web theo dõi hold/trade + cảnh báo theo chỉ báo.
Nhưng Implementation Plan đặt cổng chặn:

- IM §1: "Không build dashboard hoặc **full app** trước khi research prototype hoàn thành và
  verdict cho phép."
- IM §9 (tiêu đề): "App MVP — **chỉ sau verdict cho phép**", và liệt kê "Dashboard dual-unit
  VND/USDT và Treasury đầy đủ" là nội dung của MVP bị chặn.
- IM §7: "INCONCLUSIVE và DO NOT BUILD **không thể đi tiếp sang phase app**."
- IM §5: chỉ verdict BUILD mới mở cổng; đã được cài đặt tự động trong
  `src/eth_dca_os/verdict.py` qua trường `can_proceed_to_app`.

Tình trạng hiện tại tạo tiền lệ chưa được ghi nhận thành quyết định: `webapp/` **đã tồn tại**
(commit `aef0220`), và `webapp/README.md` tự khai báo nó được xây "theo yêu cầu của chủ dự án
như một công cụ ghi chép và tính toán, không phải bằng chứng rằng chiến lược đã được chứng
thực", kèm banner cảnh báo thường trực.

Các phương án sẽ trình ở T-05:
- **PA-1 — Tuân thủ chặt:** đóng băng webapp ở mức hiện tại, không thêm tính năng nào cho tới
  khi có verdict BUILD. Ưu tiên toàn lực cho official run.
- **PA-2 — Tách hai lớp (khuyến nghị sơ bộ):** ghi nhận chính thức ranh giới giữa
  *lớp ghi chép/quan sát* (không bị chặn) và *lớp tự động hóa chiến lược* (bị chặn sau verdict),
  kèm tiêu chí phân định rõ ràng để không trượt dần qua ranh giới.
- **PA-3 — Mở V2.2:** nếu chủ dự án muốn thay đổi chính điều khoản cổng, phải mở V2.2 change
  proposal theo Master Index §6 — **không được vá tại chỗ V2.1.5**.

Ràng buộc không thể thương lượng dù chọn phương án nào:
Master Index §6 cấm sửa công thức, ngưỡng gate, phương pháp sinh manifest, ngày split và giả
định ma sát dựa trên kết quả run. Mọi thay đổi hypothesis phải đi qua V2.2.

Reason chưa chốt trong S000:
Đây là quyết định phạm vi sản phẩm thuộc thẩm quyền chủ dự án, không phải quyết định kỹ thuật
mà agent được tự quyết. `CLAUDE.md` mục "Conflict Rule" yêu cầu không giải quyết mâu thuẫn
trọng yếu một cách im lặng.

Can Revisit After:
T-05 (cần quyết định của chủ dự án) và sau đó là T-07 (đọc verdict thật).

---

## DEC-006 — Source of Truth cho compliance audit là V2.1.5, không phải V2.1.3

Date:
2026-08-23 (S001)

Task:
S001 — Discovery & Baseline

Decision:
Compliance matrix của S001 đối chiếu implementation với bộ **V2.1.5**.

Reason:
Chủ dự án mở S001 với chỉ định "V2.1.3 là ACTIVE Source of Truth". Agent nêu `CONFLICT DETECTED`
thay vì tự chọn, theo `CLAUDE.md` mục "Conflict Rule" và Master Index §2 ("Agent không được tự
chọn"). Ba bằng chứng được trình:

1. Không file V2.1.3 nào tồn tại trong repo, và `git log --all` cho thấy chưa từng tồn tại.
   Chỉ có bộ V2_1_5 (8 file).
2. `00_MASTER_INDEX_V2_1_5.md:31` — `V2.1.3 | SUPERSEDED | Không giao agent. Có regression đã
   được sửa ở V2.1.4.`
3. `05_IMPLEMENTATION_PLAN_V2_1_5.md:8` — "V2.1.5 là source of truth duy nhất. Không kế thừa
   ngầm bất kỳ điều gì từ V1, V2.0, V2.1, V2.1.1, V2.1.2, V2.1.3 hay V2.1.4."

Chủ dự án đã chọn phương án "Dùng V2.1.5".

Impact:
- Compliance đo theo V2.1.5. Nếu đo theo V2.1.3 thì sẽ gắn cờ sai ở đúng những chỗ V2.1.4/V2.1.5
  đã sửa regression.
- S001 đã kiểm riêng và **không phát hiện regression kế thừa** nào: bảy sửa đổi F1–F7 đều có dấu
  vết hiện thực trong code.

Can Revisit After:
Chỉ khi chủ dự án cung cấp bộ tài liệu V2.1.3 thật và chấp nhận rủi ro đã nêu. Kể cả khi đó,
Master Index §6 vẫn cấm vá tại chỗ; thay đổi hypothesis phải mở V2.2.

---

## DEC-007 — RCP-001 được phê duyệt và áp dụng kèm bốn điều kiện

Date:
2026-08-23 (áp dụng RCP-001)

Task:
Áp dụng ROADMAP CHANGE PROPOSAL RCP-001

Decision:
Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` và cho phép áp dụng vào bảng
roadmap chuẩn, kèm bốn quyết định:

1. **APPROVED** — cấu trúc 15 work package và cách gom 33 finding theo nguyên nhân gốc, giữ
   nguyên dependency graph và nguyên tắc phân loại theo ảnh hưởng thực tế (không theo severity).
2. **APPROVED WITH CONDITION** — phân lớp A/B/C/D giữ nguyên như đề xuất (bao gồm WP-A2 ở lớp A,
   F-006/F-008 ở lớp C, F-023 ở lớp A), với điều kiện bắt buộc cho F-017 (nằm trong WP-B1): nếu
   remediation ảnh hưởng Gate 1, mọi kết quả Gate 1 tạo trước đó là STALE/INVALIDATED và Gate 1
   phải chạy lại trước khi dùng cho verdict. Xem DEC-009.
3. **APPROVED** — bỏ T-06A như task độc lập, hấp thụ toàn bộ phạm vi vào WP-A1. Không được mất
   requirement nào của T-06A cũ; WP-A1 phải bao gồm tối thiểu: Python version, dependency/lock
   hash, git commit SHA, dataset hash, strategy config hash, execution config hash, manifest
   hash, seed.
4. **OVERRIDE ROUTER** — WP-A2 dùng Tier C/Opus thay vì Tier B/Sonnet mà router trả, vì router có
   defect biên dấu phẩy động (GOVDEF-001). Xem DEC-008.

Reason:
Kết quả S001 (33 finding, 0 CRITICAL/8 HIGH/15 MEDIUM/7 LOW/3 spec defect) cần được phản ánh vào
roadmap trước khi bắt đầu bất kỳ remediation nào, theo yêu cầu tường minh của chủ dự án và theo
`00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule".

Impact:
- Bảng roadmap chuẩn trong `PROJECT/PROJECT_PROGRESS.md` tăng từ 14 lên 28 task.
- Đường găng tới verdict dài thêm ba mắt xích: T-04 → WP-A3 → WP-A4 → WP-A6 → T-06 → WP-B1 → T-07.
- DEC-005 xác nhận không nằm trên đường găng tới verdict; chỉ chặn nhánh T-08/WP-C2.
- BLK-001 xác nhận chỉ chặn đúng một điểm: T-06.
- T-03 giữ nguyên BLOCKED; CHECK-03-01 sẽ được thoả bởi WP-C1, không hạ Completion Gate.
- Chưa remediation hoặc sửa code sản phẩm nào được phép trong bước áp dụng này.

Can Revisit After:
T-04, khi soạn Ready Gate/Completion Gate chi tiết cho từng work package có thể phát hiện cần
điều chỉnh phạm vi hoặc thứ tự — dùng khối `COMPLETION GATE CHANGE PROPOSAL`, không sửa im lặng.

---

## DEC-008 — Ghi đè thủ công routing của WP-A2 (Tier C, không dùng Tier B từ router)

Date:
2026-08-23 (áp dụng RCP-001, quyết định 4)

Task:
RCP-001 — routing của WP-A2

Decision:
WP-A2 ("Bật các hạng mục đã viết nhưng pipeline chưa chạy") dùng **Tier C / Opus**, ghi đè kết
quả tự động của `routing_engine.py` (Tier B / Sonnet). Effort giữ nguyên `high` — giá trị này do
router tính đúng và không bị ảnh hưởng bởi defect gây ra việc ghi đè Tier.

Reason:
`routing_engine.py` có defect biên dấu phẩy động (xem GOVDEF-001): với đầu vào
D=2, R=2, B=2, A=1, X=3, giá trị `model_score` **hiển thị** đúng `2.0` nhưng giá trị nội bộ dùng
để so sánh là `1.9999999999999998`, khiến hàm `tier_from_score` (so sánh `s < 2`) trả về Tier B
thay vì Tier C như bảng `AGENT_CAPABILITY_MATRIX.md` quy định cho khoảng 2.00–2.99.

Chủ dự án xác nhận: đây là lỗi công cụ, không phải chấm điểm đầu vào sai; task tính hợp lệ ảnh
hưởng trực tiếp tới tính hợp lệ của backtest (đấu nối benchmark B/C/D, ablation, coverage, XIRR
vào pipeline chính) nên xứng đáng Tier C.

Impact:
- Bảng roadmap chuẩn ghi Tier C cho WP-A2 kèm chú thích "ghi đè thủ công, xem DEC-008".
- Không tạo xung đột với `validate_routing.py` vì WP-A2 chưa có file task riêng dưới `docs/tasks/`
  (chỉ tồn tại trong bảng roadmap và mục "Routing sơ bộ"); khi T-04 soạn file task đầy đủ cho
  WP-A2, file đó phải ghi rõ "Manual Override: YES — DEC-008" bên cạnh giá trị router thô, và
  `validate_routing.py` cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để
  chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối.
- Không sửa `routing_engine.py` trong quyết định này.

Can Revisit After:
Khi MICRO-GOVDEF-001 hoàn tất và router được sửa tổng quát, chạy lại routing cho WP-A2 để xác
nhận nó tự nhiên rơi vào Tier C mà không cần override thủ công nữa.

---

## DEC-009 — Quy tắc Gate 1 staleness: remediation ảnh hưởng Gate 1 bắt buộc chạy lại Gate 1

Date:
2026-08-23 (áp dụng RCP-001, điều kiện của quyết định 2)

Task:
RCP-001 — Lớp B, WP-B1 (đặc biệt phần đóng F-017 — Control F)

Decision:
Nếu bất kỳ remediation nào (không giới hạn ở F-017) thay đổi một trong các điều sau theo cách có
khả năng ảnh hưởng Gate 1:
- input,
- calculation,
- execution behavior,
- dataset interpretation,
- strategy behavior,
- backtest behavior,

thì **mọi kết quả Gate 1 được tạo trước remediation đó phải coi là STALE/INVALIDATED**.
Gate 1 **bắt buộc phải chạy lại** trước khi bất kỳ kết quả nào của nó được dùng làm căn cứ cho
verdict.

Áp dụng cụ thể trước mắt: F-017 (Control F giữ đúng profile tranche theo tháng) nằm trong WP-B1,
tức về nguyên tắc thuộc lớp B ("must fix before verdict", làm sau T-06). Nếu khi thực thi WP-B1
xác nhận sửa F-017 chạm vào logic dùng chung với Gate 1, thì phần việc đó phải kéo theo chạy lại
Gate 1 trước khi WP-B1 được coi là hoàn tất, và trước khi T-07 (DUYỆT verdict) được mở.

Reason:
Chủ dự án yêu cầu tường minh bảo vệ stopping rule: không được dùng kết quả Gate 1 cũ sau một
remediation có ảnh hưởng tới Gate 1, để tránh verdict dựa trên hỗn hợp code cũ (Gate 1) và code
mới (Gate 3/controls) không tương thích.

Impact:
- Dependency column của WP-B1 trong bảng roadmap chuẩn ghi rõ quy tắc này.
- T-04 phải đưa quy tắc này vào Completion Gate của WP-B1 dưới dạng một REQUIRED check tường
  minh (ví dụ: "Xác định remediation có ảnh hưởng Gate 1 hay không; nếu có, Gate 1 đã được chạy
  lại và kết quả mới được ghi nhận").
- Đường găng có thể kéo dài thêm nếu điều kiện này kích hoạt (một vòng lặp về T-06 trước khi
  GATE-B đóng) — chấp nhận được vì Master Index §6 vẫn cấm chạy lại official run để "làm đẹp"
  kết quả; đây là chạy lại vì tính hợp lệ, không phải để cải thiện con số.

Can Revisit After:
Khi WP-B1 thực thi và xác định rõ F-017 có chạm Gate 1 hay không.

---

## DEC-010 — RESOLVED: PA-1 phê duyệt cho BLK-003 (override DEC-008 và `validate_routing.py`)

Date:
2026-08-23 (S002 / T-04, PENDING) — **RESOLVED tại MICRO-GOVDEF-001, cùng ngày**

Task:
T-04 — Chốt lộ trình và đóng băng tiêu chí

Vấn đề:

T-04 soạn file định nghĩa đầy đủ cho WP-A2 với `Primary Agent Tier: C` theo **DEC-008**. Kể từ khi
file đó tồn tại với `Task Mode: MAJOR`, `governance/scripts/governance/validate_routing.py` — vốn so
khớp **tuyệt đối** giữa Tier trong file và kết quả `routing_engine.py` — báo:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây là **lỗi duy nhất**; 14 work package còn lại cộng T-04 đều khớp router tuyệt đối.

RULE CONFLICT

Higher-priority rule:
DEC-008 (quyết định của chủ dự án, đã phê duyệt) — WP-A2 dùng Tier C/Opus, và file task phải ghi rõ
`Manual Override: YES — DEC-008` bên cạnh giá trị router thô.

Lower-priority rule:
`governance/core/ROADMAP_SYNC_STANDARD.md` — "A Tier/Effort value that does not match the
deterministic router is invalid"; và `CLAUDE.md` điểm 9 — "require `validate_routing.py` to PASS
before execution".

Why both cannot be satisfied:
`validate_routing.py` không có cách biểu diễn một override **có ghi nhận**. Nó chỉ so khớp chuỗi.
Vì `routing_engine.py` có defect biên dấu phẩy động (GOVDEF-001) khiến nó trả Tier B cho một điểm
số hiển thị đúng `2.0`, việc tuân thủ validator đồng nghĩa với việc **vi phạm DEC-008 và vi phạm
chính bảng routing trong `AGENT_CAPABILITY_MATRIX.md`**.

Risk:
Trung bình, có giới hạn. Hệ quả là **một work package (WP-A2) không thể chuyển sang thực thi**, chứ
không phải sai kết quả tính toán nghiệp vụ. WP-A2 không nằm trên đường găng tới verdict.

Đã được dự đoán trước:
DEC-008 mục Impact đã ghi nguyên văn rằng tình huống này sẽ xảy ra và rằng `validate_routing.py`
"cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để chấp nhận override có ghi
nhận thay vì báo lỗi khớp tuyệt đối". Vì vậy đây **không phải xung đột mới**, mà là điểm mà DEC-008
đã hoãn lại và bây giờ đến hạn.

Vì sao T-04 không tự xử lý:
Chủ dự án chỉ thị tường minh cho S002 rằng T-04 không sửa `routing_engine.py`, và DEC-008 giao việc
sửa validator cho một task riêng. T-04 làm đúng phần được giao (ghi override vào file task) và dừng
tại ranh giới đó.

Các phương án:
- **PA-1 (khuyến nghị)** — cho phép mở `MICRO-GOVDEF-001` với phạm vi đã được làm rõ: sửa
  `routing_engine.py` (so sánh biên tổng quát, không hard-code ngoại lệ) **và** cập nhật
  `validate_routing.py` để chấp nhận override có ghi nhận. Sau khi sửa, chạy lại routing cho WP-A2
  để xác nhận nó tự nhiên rơi vào Tier C mà không cần override.
- **PA-2** — miễn trừ bằng văn bản: chủ dự án ghi nhận rằng `validate_routing.py` được phép FAIL cho
  đúng dòng WP-A2, và WP-A2 vẫn được mở. Rẻ hơn nhưng để lại một validator đỏ thường trực, làm mất
  giá trị tín hiệu của chính validator đó.
- **PA-3** — hạ Tier WP-A2 về B để validator xanh. **Bị DEC-008 cấm** và là hạ tiêu chuẩn để công
  cụ hài lòng. Nêu ra để loại bỏ tường minh, không phải để cân nhắc.

Required decision:
Chủ dự án chọn PA-1 hoặc PA-2. Cho tới lúc đó **WP-A2 = BLOCKED** (BLK-003).

**Quyết định của chủ dự án: PA-1.** Ghi nhận nguyên văn: *"Tôi phê duyệt PA-1 cho DEC-010."*
(chỉ thị mở `MICRO-GOVDEF-001`).

## Thực thi PA-1 (MICRO-GOVDEF-001, 2026-08-23)

- `governance/scripts/governance/routing_engine.py`: thêm `SCORE_DECIMALS = 3`; `model_score` và
  `effort_score` được làm tròn **một lần, ngay sau khi tính**, và giá trị đã làm tròn đó — không
  phải giá trị dấu phẩy động thô — được dùng cho cả hiển thị lẫn mọi so sánh biên Tier/Effort.
  Không phải epsilon tuỳ tiện: trọng số công thức chỉ có tối đa 2 chữ số thập phân, nên giá trị
  toán học đúng của mọi tổng có trọng số luôn có tối đa 2 chữ số thập phân có nghĩa; làm tròn 3 chữ
  số chỉ loại bỏ nhiễu biểu diễn nhị phân (~1e-15), không bao giờ đổi giá trị thật.
- `governance/scripts/governance/validate_routing.py`: bổ sung hàm `check_override` — chấp nhận một
  mismatch giữa Tier/Effort khai báo và router **chỉ khi** cả bốn điều kiện đều đúng: (1) trường
  `Manual Override: YES — DEC-###` tồn tại (regex tổng quát, không hard-code số); (2) `DEC-###` đó
  có heading thật trong `PROJECT_DECISIONS.md`; (3) trường `Router Raw Output` khớp chính xác với
  kết quả `route()` tính lại tại chỗ từ đúng Routing Inputs của file (chặn baseline giả mạo/lỗi
  thời); (4) override chỉ được **leo thang** Tier/Effort, không bao giờ được hạ.
- Test mới: `governance/scripts/governance/test_routing_engine.py` — 37 check, gồm quét brute-force
  toàn bộ 5^5 × 5^5 tổ hợp đầu vào hợp lệ (0 lệch còn lại) và 6 kịch bản override hợp lệ/không hợp
  lệ tổng hợp (độc lập với WP-A2, để chứng minh cơ chế tổng quát chứ không chỉ vá đúng một trường
  hợp).

**Kết quả cho WP-A2:** route lại với đúng Routing Inputs (D=2,R=2,B=2,A=1,X=3; U=1,V=3,H=2,C=3,F=2)
cho **Tier C tự nhiên** — không cần nhánh override nữa. File
`docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md` giữ nguyên `Primary Agent Tier: C`,
`Primary Effort: high`, và toàn bộ dấu vết `Manual Override: YES — DEC-008` /
`Router Raw Output` gốc — chỉ bổ sung ghi chú cập nhật, không xoá gì. `validate_routing.py` chạy
trên toàn bộ 16 file MAJOR task: `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0
accepted manual override(s))`.

**Regression:** đối chiếu routing trước/sau trên cả 16 file — đúng một dòng đổi (WP-A2, Tier B → C).
Không task nào khác trong repo đổi Tier hoặc Effort.

**Hệ quả cho các quyết định liên quan:**
- **BLK-003 RESOLVED.**
- **GOV-RSK-001 CLOSED.**
- **WP-A2 chuyển `BLOCKED` → `READY`.**
- **DEC-008 "Can Revisit After" đã xảy ra:** xác nhận WP-A2 tự nhiên rơi vào Tier C mà không cần
  override thủ công nữa — đúng như DEC-008 dự đoán. DEC-008 vẫn giữ nguyên làm quyết định lịch sử
  (nó là căn cứ đúng tại thời điểm được đưa ra); không sửa lại nội dung DEC-008 ở trên.

Can Revisit After:
Không cần revisit — đã thực thi PA-1 và xác nhận đủ evidence E1. Nếu về sau `routing_engine.py`
đổi công thức trọng số, chạy lại toàn bộ `test_routing_engine.py` trước khi merge.
