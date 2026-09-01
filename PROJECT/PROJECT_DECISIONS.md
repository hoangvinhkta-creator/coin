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

---

## DEC-011 — Owner Product Intent và V1 Daily-Use Acceptance

Date:
2026-09-01 (phiên Owner Disposition)

Task:
Không thuộc task nào. Đây là quyết định cấp sản phẩm của chủ dự án, ghi theo §0 và §12 của
chỉ thị phiên.

Decision:

**OD-1 — PRODUCT INTENT.** ETH DCA OS là ứng dụng web **CÁ NHÂN, MỘT NGƯỜI DÙNG, DÙNG HÀNG
NGÀY**. Chủ dự án là người duy nhất sử dụng. KHÔNG xây để: public multi-user; phục vụ khách
hàng bên ngoài; chống hostile user; chống attacker; scale lớn; enterprise
security/compliance.

**V1 PRIORITY RULE.** Đường găng V1 ưu tiên theo thứ tự: CORRECT DECISION · CORRECT
MONEY/ACCOUNTING · DATA PERSISTENCE · REAL MARKET DATA · END-TO-END REACHABILITY · DAILY WEB
USABILITY.

Một finding chỉ được giữ `BLOCKING V1` khi failure có thể:

    A. làm recommendation/Buy Score sai;
    B. làm sai số tiền / ngân sách / giá vốn / ETH holding;
    C. mất hoặc làm hỏng lịch sử giao dịch thực tế;
    D. khiến dữ liệu thị trường thật không đi qua pipeline đúng;
    E. khiến web app không chạy được end-to-end;
    F. khiến hệ thống tuyên bố một official/daily result HỢP LỆ trong khi dữ liệu thực tế
       không đủ để tính đúng kết quả.

Finding chủ yếu về hostile tampering, người dùng cố tình sửa lineage, security hardening,
multi-user, permission, scale, theoretical future input, metadata perfection, hay
enterprise-grade provenance **KHÔNG mặc định BLOCKING V1**; định tuyến theo
`governance/v4/CORE/PRODUCTION_PATH_RULE.md`.

**Ràng buộc đối xứng, không được bỏ qua:** KHÔNG được hạ một finding chỉ vì "dự án cá
nhân". Phải chứng minh nó không ảnh hưởng A–F.

**V1 DAILY-USE ACCEPTANCE — 10 điểm canonical:**

    1.  Web app mở được ổn định.
    2.  Lấy được dữ liệu ETH thật cần thiết.
    3.  Pipeline chạy end-to-end.
    4.  Buy Score / regime / budget / recommendation được hiển thị.
    5.  Người dùng ghi nhận giao dịch thực tế.
    6.  Holdings / average cost / monthly budget / purchase history cập nhật đúng.
    7.  Dữ liệu tồn tại sau reload/restart.
    8.  Ngày tiếp theo tiếp tục sử dụng được mà không cần terminal hay AI coding agent.
    9.  Lỗi có thể làm sai quyết định hoặc sai tiền phải fail visibly / fail closed.
    10. Security / multi-user / scale / hostile tampering KHÔNG phải yêu cầu chấp nhận V1.

Reason:
Chủ dự án phát biểu tường minh mục đích sản phẩm trong chỉ thị phiên. Trước quyết định này,
tiêu chí "nghiêm trọng" của repo được suy ra từ profile PRODUCT và từ phán quyết reviewer
E2, chứ chưa từng có một định nghĩa V1 do chủ dự án đặt. Thiếu định nghĩa đó, mọi finding
`CONFIRMED` đều có xu hướng trôi về BLOCKING, và không có cách nào phân biệt "sai tiền" với
"metadata chưa hoàn hảo".

Impact:
- Bổ sung trục phân loại thứ hai `BLOCKING V1`, độc lập với trục Completion Gate đã FROZEN.
  Hai trục KHÔNG được gộp. Xem
  `docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md` §1.
- KHÔNG hồi tố viết lại bất kỳ gate nào đã FROZEN ngày 2026-08-23, không đổi contract 20
  case của PRE-S008, không hạ REQUIRED check nào. Nơi Product Intent và một gate đã FROZEN
  lệch nhau, ghi `LEGACY_GATE_DISPOSITION_REQUIRED` và để chủ dự án định đoạt.
- KHÔNG đổi `DEC-001` (profile PRODUCT). Dữ liệu tài chính thật của chủ dự án vẫn là dữ
  liệu production; điểm 9 của Acceptance giữ nguyên yêu cầu fail-closed cho sai tiền / sai
  quyết định.
- KHÔNG đổi `DEC-003` (dữ liệu tổng hợp không bao giờ dùng để ra verdict). Điểm 2 và điểm 9
  của Acceptance củng cố DEC-003 chứ không nới nó.
- KHÔNG mở task nào để ghi Acceptance này. Nó được map vào authority sản phẩm hiện có
  (`PROJECT/PROJECT_PROFILE.md` mục tiêu cuối + `CAP-WEBAPP` cho phần dùng hàng ngày).

Can Revisit After:
Khi có người thứ hai dùng công cụ, hoặc khi công cụ được phát hành cho người khác — khi đó
OD-1 hết hiệu lực và các nhóm finding bị loại ở trên phải được định tuyến lại toàn bộ.

---

## DEC-012 — Hạn mức repair budget cho CAP-PROV: allowed = 2, đã dùng hết

Date:
2026-09-01 (phiên Owner Disposition)

Task:
`WP-A1` / capability `CAP-PROV`

Decision:

    CAP-PROV Effective Risk = HIGH
    ALLOWED   = 2 repair cycle
    USED      = 2
    REMAINING = 0
    OWNER_EXTENSION = NOT GRANTED

WP-A1 **KHÔNG được mở repair cycle thứ tư** nếu không có một `OWNER_EXTENSION` mới, tường
minh.

Budget KHÔNG reset — không qua session, branch, repair cycle, subtask, work package, task
con hay sibling task. Phiên adoption V4.3 (`62f8bac`) và phiên source reconciliation
(`d63c222`) **KHÔNG** được tính là repair cycle của WP-A1: cả hai có diff production path
= 0, đã kiểm bằng git chứ không chép từ báo cáo.

Reason:
`PROJECT/REVIEW_BUDGET_LEDGER.md` §1 ghi `MIGRATION_UNCERTAINTY`: bộ governance V3.2 chưa
bao giờ định nghĩa mô hình review/repair budget, nên "remaining" không tính ra được từ lịch
sử — nó chưa từng tồn tại để mà tiêu. Ledger nêu `OWNER_DECISION_REQUIRED` đúng cho tình
huống này. Chủ dự án nay đặt hạn mức, tính TỪ baseline `666de14`, không tính lại từ 0.

Hai chu kỳ đã tiêu, tái dựng từ git:

    repair cycle 1: d72fbc4..2f20e6c   8 files, +246 / -76   -> E2 vòng HAI FAIL
    repair cycle 2: bd7c5ff..a0c278a   2 files, +56 / -10    -> E2 vòng BA FAIL

Impact:
- `MIGRATION_UNCERTAINTY` của ledger §1 được GIẢI QUYẾT. `ALLOWED BUDGET` không còn là
  "CHƯA TỪNG ĐƯỢC ĐẶT".
- `ESCALATION_PROTOCOL.md` đã kích hoạt (lần thứ ba qua E2) nay có hệ quả đếm được, không
  chỉ định tính.
- Mọi hạng mục còn mở của WP-A1 cần production code đều phải đi qua §4.2 của bản disposition:
  `ACCEPT_AS_IS` / `DESCOPE` / `OWNER_EXTENSION`.
- Ghi nhận đã kiểm chứng: hạng mục đóng được **hoàn toàn bằng tài liệu** có diff production
  path = 0, nên **không tiêu repair cycle** — tiền lệ là decision pack PRE-S008
  (`2f20e6c..bd7c5ff`) đã được ledger ghi là không tính chu kỳ.
- Reviewer E2 vòng ba KHÔNG khuyến nghị `CAPABILITY_CEILING`; đề xuất là
  `VERIFICATION_DEPTH` (giữ Tier C, nâng Effort `xhigh` → `max`). Quyết định đó vẫn ĐANG MỞ,
  không được quyết trong DEC-012 này.

Can Revisit After:
Khi chủ dự án cấp `OWNER_EXTENSION` tường minh, hoặc khi WP-A1 được `DESCOPE` một phần theo
§4.2 của bản disposition.

---

## DEC-013 — PENDING: Integration decision cho branch WP-A1

Date:
2026-09-01 (phiên Owner Disposition)

Task:
Không thuộc task nào. Hard-stop `INTEGRATION_DECISION_REQUIRED` do
`branch_authority_check.sh` phát ra.

Status:
**PENDING — chờ chủ dự án.** Phiên Owner Disposition KHÔNG merge, chỉ đo và khuyến nghị.

Measured (đo bằng git tại `d63c222`, không chép từ báo cáo cũ):

    branch          = claude/wp-a1-provenance-v67k9h @ d63c222
    default branch  = claude/plan-tool-from-docs-qijx5m @ 4a46b3c  (giải từ origin/HEAD)
    merge base      = e368425 (2026-08-23)
    ahead / behind  = 29 / 1
    age             = 9 ngày
    diff            = 88 files, +24755 / -340
                      production 14 files +662/-113 · docs+governance 66 files +21715/-227
                      · test 8 files +2378
    ngưỡng vượt     = AHEAD 2,9x · AGE 3,0x · LOC 5,0x

    XUNG ĐỘT = 0, ĐO ĐƯỢC (không ước lượng):
    git merge-tree --write-tree HEAD origin/<default>  -> 0 file xung đột,
    tree kết quả = 1a9b7e8... = ĐÚNG tree của HEAD hiện tại.
    Nguyên nhân: origin/claude/move-files-to-root-7zhv8l là TỔ TIÊN của HEAD, nên commit
    `4a46b3c` mà branch đang "behind" không mang nội dung nào mà branch này thiếu.

Recommended:
**Phương án A — INTEGRATE NOW.** Chi phí rủi ro đo được bằng 0 (merge không đưa vào một
dòng mã nào); không tốn gì ở phía WP-A1 (không đổi state/gate/budget/finding); và cửa sổ
đang đóng lại vì WP-A4 sắp chạm `src/eth_dca_os/data/` — đúng thư mục WP-A1 vừa sửa.

Phương án C (partial/staged) bị khuyến nghị LOẠI tường minh: 29 commit là tuyến tính và đan
xen, tách tập con phải viết lại lịch sử và sẽ phá neo `BASELINE SHA` của
`REVIEW_BUDGET_LEDGER.md` (`666de14` cho CAP-PROV), làm phép đo budget không còn tái dựng
được từ git.

Quyết định phụ kèm theo:
`origin/HEAD` trỏ tới `claude/plan-tool-from-docs-qijx5m` — bản thân là một branch làm việc
`claude/*`; remote KHÔNG có branch nào tên `main`. Chủ dự án cần chọn: tích hợp vào default
branch hiện tại, hay lập một trunk quy ước trước đã.

Required decision:
Chủ dự án chọn A, B hoặc C, kèm đích tích hợp. Nếu chọn B thì **bắt buộc** nêu lý do và đặt
ngày tái xét — "không làm gì" không phải phương án B hợp lệ.

Lập luận đầy đủ cho từng phương án (benefit / risk / conflict probability / rollback /
effect on WP-A1 / effect on next critical-path work / V4.3 compliance):
`docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md` §7.

Can Revisit After:
Ngay khi chủ dự án ra quyết định. Phép đo xung đột = 0 chỉ đúng khi WP-A4 chưa bắt đầu; sau
đó phải đo lại.

### Cập nhật số đo — phiên Integration Recheck (2026-09-01)

Số đo ở khối `Measured` phía trên được chụp tại `d63c222` và **đã hết giá trị** sau khi WP-A4
chạy (`DEC-014` đã báo trước điều này). Giữ nguyên để đọc được lịch sử. Số đo có thẩm quyền
từ đây là bảng dưới, đo lại toàn bộ bằng git tại `07bb241`, không chép từ báo cáo cũ:

    CURRENT BRANCH        = claude/wp-a1-provenance-v67k9h
    CURRENT HEAD          = 07bb2412e31e957dcfc211ec9c8e5e601f20d2b1
    DEFAULT BRANCH        = claude/plan-tool-from-docs-qijx5m
                            (giải bằng `git ls-remote --symref origin HEAD`, KHÔNG giả định;
                             remote KHÔNG có branch nào tên main/master)
    DEFAULT BRANCH HEAD   = 4a46b3c2012d786f457316e3452c971bab12464a
    MERGE BASE            = e36842583372a2eae8335c5c7048d92d5ff2c987  (2026-08-23)
    AHEAD                 = 32
    BEHIND                = 1
    DIVERGENCE AGE        = 9 ngày
    TOTAL DIFF            = 95 files, +27857 / -372
    PRODUCTION DIFF       = 15 files, +940 / -145
    TEST DIFF             = 11 files, +3150 / -0
    GOVERNANCE/DOC DIFF   = 69 files, +23767 / -227

    (PRODUCTION DIFF đo đúng tập khai ở `PRODUCTION_PATHS.md` §1: `src/eth_dca_os`,
     `webapp/app_logic.js`, `webapp/engine.js`, `webapp/app_shell.html`, `webapp/build_app.js`,
     `pyproject.toml`, `pyproject.lock` — KHÔNG gộp `webapp/test_*.js`.)

Bằng chứng xung đột, git-native, KHÔNG dùng kết quả cũ của `DEC-013`:

    git merge-tree --write-tree HEAD origin/claude/plan-tool-from-docs-qijx5m
      -> exit 0, tree = 605b6210989e664a61e747c91156ec3d36c4c44c
    git rev-parse HEAD^{tree}
      -> 605b6210989e664a61e747c91156ec3d36c4c44c        (TRÙNG KHÍT)

    MERGE CONFLICT COUNT             = 0
    CONTENT MISSING FROM CURRENT BR. = 0 file, 0 dòng
    CONTENT MISSING FROM DEFAULT BR. = 95 file, +27857 / -372
    RESULT TREE DETERMINISTIC        = YES

Lý do `BEHIND = 1` vẫn cho 0 nội dung thiếu: commit `4a46b3c` là merge commit của
`claude/move-files-to-root-7zhv8l`, và branch đó **là tổ tiên của HEAD** (kiểm bằng
`git merge-base --is-ancestor`). Nó không mang nội dung nào mà branch này chưa có.

**Kết luận đo được: hợp nhất KHÔNG đưa vào một dòng nội dung nào.** Tree kết quả bằng đúng
tree của HEAD hiện tại. Đây là số đo mạnh hơn "0 xung đột": nội dung sau merge trùng khít
HEAD.

Bảo toàn baseline/provenance — kiểm bằng `git merge-base --is-ancestor`, toàn bộ đều là tổ
tiên của HEAD và vẫn reachable sau một merge commit thường:

    666de14 (CAP-PROV baseline)   YES      06b381c (WP-A4/CAP-DATA baseline)  YES
    d72fbc4 · 2f20e6c · bd7c5ff · a0c278a (các chu kỳ WP-A1)                  YES
    85fa30f (WP-A4 DONE)          YES      d63c222 · e368425                  YES

`4a46b3c` KHÔNG phải tổ tiên của HEAD, nên default **không** fast-forward được tới HEAD:
tích hợp cần một **merge commit thường**, và merge commit giữ cả hai parent nên KHÔNG có
history rewrite, KHÔNG mất neo baseline nào.

Đánh giá lại ba phương án tại số đo mới:

| | A — INTEGRATE NOW | B — CONTINUE WITH LIMIT | C — STAGED |
|---|---|---|---|
| Risk | 0 xung đột đo được; tree kết quả = tree HEAD | Divergence tiếp tục lớn (đã 3,2× ngưỡng ahead, 3,0× age, 5,6× LOC); cửa sổ 0-xung-đột KHÔNG bảo đảm còn khi CAP-DATA sửa `indicators.py` và WP-A5/A6 sửa `pipeline.py`/`engine.py` | CAO |
| Benefit | Đóng hard-stop `INTEGRATION_DECISION_REQUIRED`; 95 file thành reachable từ default; WP-C1 khởi động từ base đã tích hợp | Không phải làm gì bây giờ | **0** — staged tồn tại để giảm rủi ro merge, mà rủi ro merge đo được đã bằng 0 |
| History rewrite? | KHÔNG (merge commit thường) | KHÔNG | **CÓ** — 32 commit tuyến tính đan xen, tách tập con phải viết lại lịch sử |
| Baseline SHA impact | KHÔNG | KHÔNG | **PHÁ** neo `666de14` / `06b381c` của ledger → budget không còn tái dựng được từ git, trái `DELIVERY_LOOP.md` ("MEASURED, not summed by hand") |
| WP-A1 ledger impact | KHÔNG (state/gate/budget/finding không đổi) | KHÔNG | Hỏng |
| WP-A4 evidence impact | KHÔNG (mọi SHA bằng chứng vẫn reachable) | KHÔNG | Hỏng |
| Next CAP-DATA work | Thuận lợi — bản sửa `F-S009-01` bắt đầu từ base đã tích hợp | Bất lợi — đào sâu thêm divergence | Bất lợi |
| WP-C1 parallel | Thuận lợi — tránh sinh divergence dài thứ hai | Trung tính | Bất lợi |

**Khuyến nghị giữ nguyên: phương án A.** Phương án C bị loại theo đúng quy tắc phiên này —
không chọn staged/cherry-pick khi nó phá provenance/baseline mà không có lợi ích thật; ở đây
lợi ích đúng bằng 0. Phương án B chỉ hợp lệ nếu chủ dự án nêu lý do VÀ đặt ngày tái xét.

**Quyết định phụ vẫn còn nguyên, chưa được quyết:** `origin/HEAD` trỏ tới
`claude/plan-tool-from-docs-qijx5m` — bản thân là một branch làm việc `claude/*`. Chủ dự án
chọn: tích hợp vào default branch hiện tại, hay lập một trunk quy ước trước đã.

Phiên Integration Recheck **KHÔNG merge**. `DEC-013` vẫn `PENDING`.

---

## DEC-014 — `OD-A4-01`: bổ sung một REQUIRED check cho WP-A4 và làm rõ Expected Touch Area

Date:
2026-09-01 (chỉ thị mở WP-A4 / phiên S009)

Task:
`WP-A4` / capability `CAP-DATA`

Decision:

    APPROVE COMPLETION GATE CHANGE PROPOSAL cho WP-A4.

    Bổ sung ĐÚNG MỘT REQUIRED check (CHECK-A4-10):
    "Coverage phải được đối chiếu với khoảng thời gian ĐƯỢC YÊU CẦU (start/end),
     không chỉ với khoảng thời gian quan sát được trong dữ liệu đã fetch."

    F-E2A1R3-05 -> CAP-DATA -> hấp thụ vào WP-A4. KHÔNG tạo task ID mới.

    Expected Touch Area của WP-A4 được làm rõ: việc loại trừ `src/eth_dca_os/data/`
    có nghĩa KHÔNG redesign cơ chế FETCH dữ liệu. Nó KHÔNG loại trừ coverage
    semantics, gap semantics, hay requested-range validation.

Reason:
Normal production runtime có thể fetch dữ liệu bị cắt cụt, thiếu ~92% khoảng thời gian được
yêu cầu, nhưng `gap_report` vẫn khai `missing_count = 0` và dataset tiếp tục được coi là
official. Failure này tác động trực tiếp tới A (CORRECT DECISION), D (REAL MARKET DATA) và
F (OFFICIAL RESULT VALIDITY) của `DEC-011`, nên là **V1 BLOCKING**.

Ba điều kiện BLOCKING của `REVIEW_PROTOCOL.md` đều thoả: (1) production path — `fetch_all`
và `official_eligibility` đều nằm trong `PROJECT/PRODUCTION_PATHS.md` §1; (2) hệ quả nghiệp
vụ nằm trong Completion Gate của WP-A1 (CHECK-A1-07) và trong `DEC-011`; (3) bằng chứng tái
lập được, dựng từ nguồn canonical 1 + 2.

Đề xuất gốc: `docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md`
§5.3 (`OWNER_DECISION_REQUIRED`). Đây là quyết định của chủ dự án đóng lại mục đó.

Impact:
- WP-A4 có **9 REQUIRED check** (CHECK-A4-01…08 FROZEN + CHECK-A4-10). Chín check FROZEN
  2026-08-23 giữ nguyên câu chữ và ngữ nghĩa; không check nào bị hạ, gộp hay nới. Không
  phát sinh `LEGACY_GATE_COMPATIBILITY_REQUIRED`: gate được BỔ SUNG, không bị viết lại.
- `F-E2A1R3-05` chuyển chủ sở hữu từ `OWNER_ASSIGNMENT_REQUIRED` sang `CAP-DATA`. WP-A1
  KHÔNG mở repair cycle thứ tư; budget `CAP-PROV` không bị đụng tới.
- Số task ID mới được tạo = **0**. Finding ≠ task.
- Hệ quả sang `DEC-013`: cửa sổ "xung đột merge = 0" mà §7.5 dựa vào đã đóng lại sau S009,
  vì WP-A4 vừa sửa `src/eth_dca_os/data/`. `DEC-013` vẫn PENDING; phép đo phải chạy lại.

Can Revisit After:
Không. Check đã được thực thi và PASS tại S009; nó là điều kiện của GATE-A từ đây.

---

## DEC-015 — `F-S009-01`: capability owner = `CAP-DATA`, phân loại `IMPLEMENTATION_DEFECT`

Date:
2026-09-01 (phiên Integration Recheck / Owner Disposition)

Task:
Không thuộc task nào. Đây là quyết định định tuyến finding ở cấp capability.

Decision:

    F-S009-01  ->  capability owner = CAP-DATA
    F-S009-01  =   CONFIRMED BLOCKING V1
    Spec verdict = IMPLEMENTATION_DEFECT
    Task ID mới được tạo = 0

Reason:

Đường sản xuất bình thường: yêu cầu dữ liệu daily → dataset thiếu một ngày lịch → indicator
tính theo **vị trí hàng** → `return7` và các cửa sổ trượt sai → **không NaN, không DEGRADED,
không INVALID** → dataset vẫn đủ tư cách official → Buy Score có thể sai.

Tác động trực tiếp tới ba tiêu chí của `DEC-011`: **A — CORRECT DECISION**, **D — REAL MARKET
DATA**, **F — OFFICIAL RESULT VALIDITY**. Không phải hostile tampering, không phải theoretical
hardening, không phải security issue. Ràng buộc đối xứng của `DEC-011` được giữ: finding
KHÔNG bị hạ mức.

Ownership thuộc `CAP-DATA` theo ranh giới ĐÃ CHỐT ở `CAPABILITY_REGISTRY.md` §3 — *"Ngữ nghĩa
DEGRADED / INVALID, nhãn gap trên bản ghi"* thuộc `CAP-DATA`. Bằng chứng cơ chế thu tại phiên
này: `score.py::invalid_mask` chỉ kích hoạt trên giá trị **không hữu hạn**, mà cửa sổ theo vị
trí luôn sinh số **hữu hạn nhưng sai** — nên đúng là ngữ nghĩa DEGRADED/INVALID của `CAP-DATA`
không kích hoạt được. Quyết định này KHÔNG mở ranh giới capability mới.

Verdict `IMPLEMENTATION_DEFECT` (không phải `SPEC_AMBIGUITY`) dựa trên spec canonical, KHÔNG
sửa spec:
- BT §18 buộc *"indicator daily bắt buộc thiếu → … đánh dấu DEGRADED hoặc INVALID theo
  Strategy §3"*; implementation trả về số hữu hạn sai nên nhánh spec bắt buộc không bao giờ
  chạy;
- ST §1.1 "365 ngày gần nhất", ST §1.3 `ETHBTC_30d_ago`, ST §17 `Return7D`, BT §2 "365 ngày
  hợp lệ" — đều là đơn vị NGÀY LỊCH;
- đối chứng quyết định: ST §17.2 nói "**96 nến 15m** liền trước" khi muốn đếm theo nến. Spec
  phân biệt hai cách đếm và đã chọn ngày cho chỉ báo daily.

Phần dư `SPEC_AMBIGUITY` được ghi nhận riêng và KHÔNG đổi owner của phần BLOCKING: `ma200`,
`adr30`, `rsi14`, `VR`, `ethbtc_percentile180` được spec nêu bằng một con số không kèm đơn vị.
Phần dư đó thuộc chủ đề `CAP-SPEC` (`WP-D2`).

Impact:
- `OWNER_ASSIGNMENT_REQUIRED` của `F-S009-01` **ĐÓNG**.
- `WP-A4` giữ nguyên **DONE**, 9/9 REQUIRED PASS. Không check nào bị thêm, hạ, gộp hay nới.
  Gói KHÔNG bị mở lại ở phiên này.
- `WP-A1` / `CAP-PROV` không đổi: allowed=2, used=2, remaining=0, `OWNER_EXTENSION` NOT
  GRANTED.
- Absorption test bốn ngưỡng: **không ngưỡng nào chạm** —
  A: Effective Risk `MAX(3,2)=3` → `MAX(3,3)=3`, không đổi (chạm chỉ khi chủ dự án chấm
  Blast Radius = 4; phiên này KHÔNG tự chọn con số đó);
  B: 2 mục hấp thụ ≤ 3; C: REQUIRED 9→10 = +11,1% ≤ 50%; D: `indicators.py` nằm TRÊN vertical
  slice. Vậy **KHÔNG** phải `ABSORPTION_LIMIT_REACHED`.
- Vẫn còn `OWNER_DECISION_REQUIRED` — **không phải** khe ownership mà là khe **thẩm quyền thi
  hành**: `WP-A4` đang `DONE` với Completion Gate FROZEN, và `indicators.py` ngoài Expected
  Touch Area. Ba rào đều là hành vi của chủ dự án theo `STATE_AUTHORITY.md`. Xem
  `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` §II.7 cho ba lựa chọn (A) mở rộng
  `WP-A4` / (B) DESCOPE / (C) task ngoại lệ, kèm khuyến nghị (A).
- Dữ kiện budget đo tại phiên này: `git log 666de14..HEAD -- src/eth_dca_os/indicators.py`
  = **0 commit**. F-S009-01 nằm NGOÀI cumulative repair diff của cả `CAP-PROV` lẫn
  `CAP-DATA`, nên bản sửa **sẽ tiêu một repair cycle mới** của owner nhận nó. Không miễn phí.
- Số task ID mới = **0**. Finding ≠ task.

Can Revisit After:
Khi chủ dự án chọn một trong ba phương tiện thi hành ở §II.7. Nếu chọn (B) DESCOPE thì phải
đối chiếu tường minh với `DEC-011` điểm 9 (fail visibly / fail closed).
