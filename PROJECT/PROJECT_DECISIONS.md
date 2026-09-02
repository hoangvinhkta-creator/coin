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

## DEC-013 — RESOLVED / INTEGRATED: Integration decision cho branch WP-A1

Date:
2026-09-01 (phiên Owner Disposition)

Task:
Không thuộc task nào. Hard-stop `INTEGRATION_DECISION_REQUIRED` do
`branch_authority_check.sh` phát ra.

Status:
**RESOLVED / INTEGRATED — 2026-09-01 (phiên Integration).** Chủ dự án chọn **phương án A —
INTEGRATE NOW**. Đã thực hiện. Xem khối "Quyết định của chủ dự án" ở cuối mục này.

Ghi chú đọc hiểu: hai khối `Measured` và bảng so sánh phương án phía dưới là số đo của các
phiên TRƯỚC quyết định. Giữ nguyên để đọc được lịch sử; số đo có thẩm quyền cuối cùng nằm ở
khối quyết định cuối mục.

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

### Quyết định của chủ dự án — DEC-013 RESOLVED / INTEGRATED (2026-09-01, phiên Integration)

Decision:

    INTEGRATION OPTION            = A — INTEGRATE NOW
    CANONICAL TRUNK TỪ ĐÂY        = main
    PHƯƠNG PHÁP                   = merge commit thường (--no-ff)
                                    KHÔNG rebase · KHÔNG squash · KHÔNG cherry-pick
                                    KHÔNG rewrite history

Lý do chọn `main` làm trunk quy ước (đóng luôn "quyết định phụ" còn treo ở khối trên):
remote KHÔNG có `main`/`master`; `origin/HEAD` đang trỏ vào một branch làm việc `claude/*`;
dự án cá nhân cần mô hình đơn giản — `main` = integrated stable trunk, work branch =
`claude/*` hoặc feature branch. Phương án staged/cherry-pick bị loại đúng như khuyến nghị
sẵn có: lợi ích bằng 0 và nó phá provenance/baseline reconstruction.

Số đo thực hiện (đo lại toàn bộ bằng git ngay trước khi merge, không chép từ khối cũ):

    SOURCE_BRANCH                 = claude/wp-a1-provenance-v67k9h
    SOURCE_HEAD                   = 637278341f66f49aad77ba27dce8865fad298b95
    CURRENT_REMOTE_DEFAULT        = claude/plan-tool-from-docs-qijx5m
                                    (giải bằng GitHub API `default_branch`, KHÔNG giả định)
    CURRENT_REMOTE_DEFAULT_HEAD   = 4a46b3c2012d786f457316e3452c971bab12464a
    MERGE_BASE                    = e36842583372a2eae8335c5c7048d92d5ff2c987
    AHEAD  (source ngoài default) = 33
    BEHIND (default ngoài source) = 1

Vì sao commit "behind" duy nhất không mang nội dung nào — chứng minh, không suy đoán:

    git rev-list --parents -n1 4a46b3c
      -> 4a46b3c  aef0220  e368425
    cả hai parent đều là ancestor của SOURCE_HEAD;
    git rev-parse 4a46b3c^{tree} = 57e087686f8f23d4978ef6e4049cb3ddeb42a2b4
    git rev-parse e368425^{tree} = 57e087686f8f23d4978ef6e4049cb3ddeb42a2b4   (BẰNG NHAU)
    git diff e368425 4a46b3c     -> RỖNG

Vậy phía "ours" của phép merge ba chiều bằng đúng merge base, nên tree kết quả buộc phải
bằng tree của "theirs" (= source).

Bằng chứng tree equivalence sau merge (E1, chạy trực tiếp):

    INTEGRATION SHA (merge)  = febc2ecf345cbaaa12837beb3b2ae3c658a08b0b
    merge parents            = 4a46b3c (default lineage) · 6372783 (source)
    MERGE CONFLICTS          = 0        (git ls-files -u -> 0 dòng)
    SOURCE TREE              = 633b4c3206e4aedb624055dd1b99ef29edf0061f
    MAIN RESULT TREE         = 633b4c3206e4aedb624055dd1b99ef29edf0061f
    TREE IDENTICAL           = YES
    git diff febc2ec 6372783  -> RỖNG
    CONTENT LOST             = 0

Baseline/evidence preservation — cả 11 SHA quy chiếu đều còn là ancestor của `main`:

    666de14 · 06b381c · 85fa30f · 07bb241 · 6372783 · d63c222
    d72fbc4 · 2f20e6c · bd7c5ff · a0c278a · e368425

Riêng hai neo ledger: `CAP-PROV` baseline `666de14` và `CAP-DATA` baseline `06b381c` KHÔNG
đổi và vẫn tái dựng được bằng git từ `main`.

Impact:
- Hard-stop `INTEGRATION_DECISION_REQUIRED` **ĐÓNG**.
- Production implementation do phép tích hợp gây ra: **0 dòng**. Test: **0 dòng**. Diff mà
  phiên này tự viết là **governance-only**.
- WP state: **không đổi**. Repair budget đã tiêu: **không đổi**. Completion Gate FROZEN:
  **không đụng**. Finding: không mở, không đóng, không phân loại lại.
- Branch `claude/wp-a1-provenance-v67k9h` được **giữ lại** cho provenance/history, KHÔNG
  xoá, và KHÔNG còn được dùng làm long-running integration branch.

Branch authority từ đây:

    Mọi phiên product mới BẮT BUỘC fetch rồi branch từ origin/main.

Can Revisit After:
Không. Quyết định đã thi hành và có bằng chứng git. Việc còn lại duy nhất là thao tác của
chủ dự án trên GitHub — xem `REMOTE_DEFAULT_SWITCH_REQUIRED` trong biên bản phiên.

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

---

## DEC-016 — `OD-DATA-01`: `F-S009-01` = BLOCKING V1, thi hành bằng MỘT repair cycle của WP-A4

Date:
2026-09-01 (phiên Integration — GHI NHẬN, CHƯA THI HÀNH)

Task:
`WP-A4` / capability `CAP-DATA`. Đây là quyết định thi hành, đóng khe thẩm quyền mà `DEC-015`
để mở.

Decision:

    F-S009-01  = CONFIRMED BLOCKING V1
    Phân loại  = CAP-DATA IMPLEMENTATION_DEFECT
    Phương tiện thi hành ĐƯỢC DUYỆT = phương án (A) của
        docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md §II.7:
        REOPEN WP-A4 cho ĐÚNG MỘT repair cycle.

    Mở rộng Expected Touch Area, ở mức tối thiểu:
        cho phép  src/eth_dca_os/indicators.py
        cộng phần wiring/test trực tiếp cần thiết.

    Số task ID mới được tạo = 0.  KHÔNG tạo WP mới.

Reason:
`DEC-015` đã chốt owner (`CAP-DATA`) và phân loại (`IMPLEMENTATION_DEFECT`) nhưng vẫn để lại
`OWNER_DECISION_REQUIRED` ở khe **thẩm quyền thi hành**: `WP-A4` đang `DONE` với Completion
Gate FROZEN, và `indicators.py` nằm ngoài Expected Touch Area. Theo `STATE_AUTHORITY.md`, mở
lại một gói đã DONE và mở rộng touch area đều là hành vi của chủ dự án. Quyết định này thực
hiện đúng ba hành vi đó và không hơn. Phương án (B) DESCOPE bị loại vì trái `DEC-011` điểm 9
(fail visibly / fail closed); phương án (C) task ngoại lệ bị loại vì finding ≠ task.

Impact:
- Trạng thái `WP-A4` sẽ chuyển `DONE` → `IN_PROGRESS` **khi phiên repair thực sự mở**, không
  phải bây giờ.
- Chín REQUIRED check FROZEN của `WP-A4` giữ nguyên câu chữ và ngữ nghĩa. Không check nào bị
  hạ, gộp hay nới. Không phát sinh `LEGACY_GATE_COMPATIBILITY_REQUIRED`.
- Bản sửa sẽ tiêu **repair cycle #1** của `CAP-DATA` — xem `DEC-017` và
  `REVIEW_BUDGET_LEDGER.md` §4.3 (`F-S009-01` nằm NGOÀI mọi cumulative repair diff, nên
  không miễn phí).
- `WP-A1` / `CAP-PROV` không đụng tới: allowed=2, used=2, remaining=0, `OWNER_EXTENSION` NOT
  GRANTED.

Trạng thái thi hành tại phiên Integration:

    KHÔNG THỰC HIỆN. Phiên Integration chỉ GHI NHẬN quyết định này.
    Không mở repair cycle, không sửa production code, không sửa test,
    không đổi state của WP-A4 tại commit này.

Can Revisit After:
Không cần. Phiên DATA kế tiếp thi hành trực tiếp theo quyết định này, branch từ `origin/main`.

---

## DEC-017 — `OD-DATA-02`: `CAP-DATA` Effective Risk = HIGH; hạn mức repair = 2, đã dùng 0

Date:
2026-09-01 (phiên Integration — GHI NHẬN, CHƯA TIÊU)

Task:
Không thuộc task nào. Quyết định ở cấp capability lineage root `CAP-DATA` (`WP-A4`).

Decision:

    CAP-DATA Effective Risk = HIGH

    Chủ dự án phê chuẩn V4.3 default repair budget cho CAP-DATA:

        ALLOWED    = 2 repair cycle
        USED       = 0
        REMAINING  = 2

    Ba con số trên đúng tại thời điểm TRƯỚC bản sửa F-S009-01.
    Bản sửa F-S009-01, nếu thực hiện, là repair cycle #1.

Reason:
`REVIEW_BUDGET_LEDGER.md` §2.1 và §4.2 trước đây ghi `ALLOWED = CHƯA LƯỢNG HOÁ (V4.3 default
theo Effective Risk)`, vì `DELIVERY_LOOP.md` §II.4 nói rõ con số `<N>` là **PROJECT value** và
tầng dự án chưa khai. Quyết định này khai con số đó. Theo `STATE_AUTHORITY.md`, đặt một hạn
mức là hành vi của chủ dự án; ledger ghi lại, không tự chọn.

Nâng Effective Risk từ **3** lên **HIGH** là chấm lại **Blast Radius**, không phải trực giác:
`RISK_MODEL.md` § Blast Radius — HIGH liệt kê "a wrong aggregation feeding an important
decision", đúng đường đi của `F-S009-01` (indicator tính theo vị trí hàng → `return7` sai →
Buy Score sai, không NaN, không DEGRADED, dataset vẫn official). Local Risk giữ nguyên; công
thức `Effective Risk = MAX(Local Risk, Blast Radius)` không đổi. Điều kiện Golden Reduction
KHÔNG thoả (dự án chưa có Golden baseline canonical — `HARDENING_BACKLOG.md` H-10), nên không
được hạ một mức.

Hệ quả bắt buộc theo `RISK_MODEL.md` § HIGH Does Not Mean STOP: mọi thay đổi trên đường
Blast Radius HIGH phải có **mandatory batch review cuối phiên**, dù nhỏ đến đâu.

Impact:
- `REVIEW_BUDGET_LEDGER.md` §2.1 và §4.2 được cập nhật đúng ba con số trên. `USED` vẫn là
  **0** — đây là **khai hạn mức**, KHÔNG phải reset: `USED` chưa từng khác 0 cho `CAP-DATA`.
- `CAP-PROV` không đổi: allowed=2, used=2, remaining=0.
- Budget KHÔNG được reset ở phiên sau, theo `DELIVERY_LOOP.md` § Change Budget và quy tắc bất
  di dịch ở đầu ledger. Phiên DATA kế tiếp phải ĐỌC ledger, không tự đặt lại số.
- `GOLDEN_BASELINE_SHA` vẫn `PENDING_OWNER_DATA / MIGRATION_REQUIRED`; H-10 vẫn mở. Quyết định
  này khai budget tầng A (review/repair), KHÔNG khai budget tầng B (delivery change budget).

Trạng thái thi hành tại phiên Integration:

    KHÔNG TIÊU chu kỳ nào. Diff production path của phiên này = 0.

Can Revisit After:
Khi `REMAINING` về 0 và cần `OWNER_EXTENSION`, hoặc khi có Golden baseline canonical làm đổi
điều kiện Golden Reduction.

---

## DEC-018 — `OD-WEBAPP-01`: phê chuẩn hoàn thành T-09A (`DONE`) và ratify hạn mức repair `CAP-WEBAPP`

Date:
2026-09-02 (phiên Integration — GHI NHẬN VÀ THI HÀNH)

Task:
`T-09A` / capability `CAP-WEBAPP`. Đóng khe thẩm quyền `STATE_AUTHORITY.md` để lại: chuyển
`DONE` cho một task đã `IMPLEMENTED` + batch review PASS là hành vi của chủ dự án; đặt hạn mức
repair budget tường minh cho một capability cũng vậy (như `DEC-012`/`DEC-017` đã làm cho
`CAP-PROV`/`CAP-DATA`).

Decision:

    (1) T-09A: IMPLEMENTED -> DONE.
        Completion Gate T-09A GIỮ NGUYÊN: 12/12 REQUIRED PASS (E1). Không sửa câu chữ hay
        ngữ nghĩa của gate.
        Xác nhận rõ: bản vá T-09A vừa hoàn thành là INITIAL IMPLEMENTATION, KHÔNG phải một
        repair cycle. Không mở repair cycle mới.

    (2) CAP-WEBAPP Effective Risk = HIGH (đã chấm tại T-09A batch review — xem
        REVIEW_BUDGET_LEDGER.md §2.2 — chủ dự án RATIFY, không đổi số).

        Chủ dự án phê chuẩn hạn mức repair budget cho CAP-WEBAPP:

            ALLOWED    = 2 repair cycle
            USED       = 0
            REMAINING  = 2

        Ba con số trên đúng tại thời điểm SAU khi T-09A implementation ban đầu hoàn tất.
        T-09A implementation ban đầu KHÔNG tiêu repair cycle nào (đây là initial
        implementation, không phải repair — cùng quy ước ở DEC-016/DEC-017 cho CAP-DATA).

Reason:
`REVIEW_BUDGET_LEDGER.md` §2.2 trước quyết định này ghi `ALLOWED = 2 (default V4.3 theo
Effective Risk HIGH)` và tự nói rõ đây KHÔNG phải Owner Decision. Quyết định này khai con số
đó thành owner-ratified, đúng cơ chế `DEC-012`/`DEC-017` đã dùng cho `CAP-PROV`/`CAP-DATA`.
Theo `STATE_AUTHORITY.md`, đặt một hạn mức và chuyển một task sang `DONE` đều là hành vi của
chủ dự án; ledger và roadmap ghi lại, không tự chọn.

Impact:
- `PROJECT/PROJECT_PROGRESS.md`: roadmap row T-09A đổi `IMPLEMENTED` → `DONE`; "Current Task"
  cập nhật để phản ánh quyết định. Không có nội dung Completion Gate nào bị sửa.
- `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2: `ALLOWED`/`USED`/`REMAINING` giữ nguyên số
  (2/0/2), chỉ đổi trạng thái xác thực từ "default V4.3, chưa Owner Decision" sang
  "Owner-ratified qua `DEC-018`".
- Budget CAP-WEBAPP là **cumulative**, KHÔNG được reset theo session/task/branch/finding —
  cùng quy tắc bất di dịch đã áp dụng cho `CAP-PROV`/`CAP-DATA`.
- V-01 = FIXED / không còn tái hiện, V-02 = FIXED / không còn tái hiện, V-03 = REJECTED,
  H-18 = DEFERRED, H-19..H-22 = HARDENING với RE_TRIGGER_CONDITION, F-T09A-03 =
  OUT_OF_SCOPE → WP-C4 — TẤT CẢ giữ nguyên, quyết định này không đụng tới.
- Cảnh báo historical state (dữ liệu lưu TRƯỚC bản vá V-01/V-02 có thể đã sai sẵn) GIỮ
  NGUYÊN, KHÔNG đóng — quyết định này không phải evidence xác minh dữ liệu lịch sử sạch.
- `WP-A4` (`CAP-DATA`), `WP-A1` (`CAP-PROV`), `WP-C2`/`WP-C3`/`WP-C4` không đụng tới.

Trạng thái thi hành tại phiên Integration:

    THI HÀNH NGAY: cập nhật `PROJECT_PROGRESS.md` §roadmap + Last Updated,
    `REVIEW_BUDGET_LEDGER.md` §2.2 theo đúng ba con số trên. Không sửa production code,
    không mở repair cycle.

Can Revisit After:
Khi `REMAINING` về 0 và cần `OWNER_EXTENSION`, hoặc khi chủ dự án muốn đặt lại Effective Risk
sau khi có Golden baseline canonical cho webapp.

---

## DEC-019 — `OD-WEBAPP-02`: Firebase là ràng buộc kiến trúc cố định cho T-09B; bổ sung Product Intent

Date:
2026-09-02 (phiên Owner Authority / Ready-Gate Preparation cho T-09B)

Task:
`T-09B` / capability `CAP-WEBAPP`. Đây là quyết định cấp kiến trúc + cấp sản phẩm của chủ dự
án, ghi theo §0, §1, §2 và §6 của chỉ thị phiên. Không thuộc thẩm quyền agent.

Decision:

    (1) PRODUCT INTENT — BỔ SUNG cho DEC-011, KHÔNG thay thế.

        ETH DCA OS là công cụ CÁ NHÂN, SINGLE-USER, DÙNG KHI CẦN. Không phải ứng dụng tần
        suất cao, không phải hệ thống enterprise. Không cần tối ưu cho scale lớn, không cần
        kiến trúc backend phức tạp. Ưu tiên DỄ SỬ DỤNG và ÍT VẬN HÀNH.

        Mục tiêu phát biểu nguyên văn: "mở web lên là sử dụng được, state thật được lưu bền,
        đóng/mở lại vẫn tiếp tục được".

        Không tối ưu kiến trúc chỉ để đạt technical elegance nếu làm giảm usability hoặc
        tăng operational burden.

        THỨ TỰ ƯU TIÊN khi có nhiều phương án khả thi:
            1. correctness · 2. usability · 3. low operational burden ·
            4. implementation simplicity · 5. cost · 6. technical elegance · 7. scalability

    (2) FIREBASE = FIXED OWNER CONSTRAINT cho persistence của T-09B.

        KHÔNG thực hiện comparison để thay Firebase bằng Supabase, SQLite, PostgreSQL,
        Cloudflare D1, JSON Server hay database/provider nào khác. Agent KHÔNG có thẩm quyền
        đổi quyết định này chỉ vì một phương án khác được đánh giá technical-optimal hơn.

        Nếu Firebase có limitation thực sự ngăn Completion Gate: báo OWNER_DECISION_REQUIRED
        kèm evidence cụ thể. KHÔNG silently đổi architecture.

    (3) FIREBASE SCOPE PRINCIPLE.

        "Đã chọn Firebase" KHÔNG có nghĩa "phải dùng toàn bộ hệ sinh thái Firebase". Chỉ dùng
        thành phần TỐI THIỂU cần cho durable persistence. Không tự thêm authentication phức
        tạp, Cloud Functions, analytics, messaging, hosting migration, multi-user permission
        system, realtime collaboration, event architecture, microservices — nếu Completion
        Gate của T-09B không cần.

        Trong phạm vi Firebase, agent ĐƯỢC PHÉP đánh giá thành phần phù hợp nhất (Realtime
        Database vs Cloud Firestore) và trả recommendation để chủ dự án duyệt, nhưng KHÔNG
        được đổi khỏi Firebase.

    (4) T-09B AUTHORITY.

        T-09B là existing V1 task. KHÔNG tạo task ID mới.
        Capability = CAP-WEBAPP · Lineage root = WP-C1.
        Routing giữ nguyên: Tier D / Effort xhigh, category `accounting_financial` +
        `material_sensitive_data_corruption`. KHÔNG tự hạ routing.

    (5) CAP-WEBAPP BUDGET GIỮ NGUYÊN — KHÔNG reset, KHÔNG cấp thêm.

            ALLOWED = 2 · USED = 0 · REMAINING = 2      (không đổi so với DEC-018)

        Implementation T-09B sau này là INITIAL IMPLEMENTATION, KHÔNG phải repair cycle —
        cùng quy ước ở DEC-016/DEC-017 (CAP-DATA) và DEC-018 (T-09A).

    (6) HISTORICAL STATE.

        Forensic / migrate / sửa historical accounting state tạo trước T-09A = OUT OF SCOPE
        T-09B V1. Giữ nguyên cảnh báo hiện tại. T-09B KHÔNG được tự tuyên bố historical state
        là sạch.

Reason:
Trước quyết định này, `PROJECT/PROJECT_PROGRESS.md` ghi T-09B là "Dựng lưu trữ dữ liệu bền"
mà không nêu nền tảng, và `PROJECT/PROJECT_PROFILE.md` để ngỏ ("Backup: KHÔNG có cơ chế backup
nào"). Thiếu một ràng buộc kiến trúc do chủ dự án đặt, mọi phiên chuẩn bị T-09B đều có xu
hướng mở lại cuộc so sánh provider — tốn ngân sách mà không tiến gần hơn tới việc app dùng
được. Chủ dự án chốt nền tảng để phiên thực thi bắt đầu từ một điểm cố định.

Điểm (1) bổ sung chứ không thay `DEC-011`: `DEC-011` đã chốt single-user và 10 điểm V1 Daily-Use
Acceptance; quyết định này thêm trục *tần suất sử dụng thấp* và *thứ tự ưu tiên khi chọn giữa
nhiều cách cài đặt đúng*. Ràng buộc đối xứng của `DEC-011` giữ nguyên: KHÔNG được hạ một finding
chỉ vì "dự án cá nhân" — vẫn phải chứng minh nó không ảnh hưởng A–F.

Impact:
- `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` được lập (Task Spec cho ID **đã tồn tại** từ
  RCP-001 2026-08-23). Số task ID mới = **0**.
- `PROJECT/PROJECT_PROGRESS.md`: roadmap row T-09B giữ `PLANNED`, ghi thêm ràng buộc Firebase
  và trạng thái `OWNER_DECISION_REQUIRED`. Không gate nào bị sửa.
- `PROJECT/CAPABILITY_REGISTRY.md` §2: `T-09B` được ghi vào danh sách owner task của
  `CAP-WEBAPP`. KHÔNG capability mới, KHÔNG đổi lineage root.
- `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2: thêm `T-09B` vào THÀNH VIÊN; ba con số budget
  **không đổi** (2/0/2).
- `PROJECT/PROJECT_PROFILE.md`: KHÔNG đổi. Profile vẫn PRODUCT (`DEC-001`); mục "Backup: KHÔNG
  có cơ chế nào" vẫn đúng cho tới khi T-09B DONE.
- KHÔNG đổi `DEC-011` (Product Intent + 10 điểm Acceptance vẫn nguyên hiệu lực).
- KHÔNG đổi `DEC-018` (T-09A DONE, hạn mức CAP-WEBAPP 2/0/2 giữ nguyên).
- KHÔNG mở repair cycle. Số production file bị sửa tại phiên ghi quyết định này = **0**.

Hệ quả phát sinh ngay tại phiên chuẩn bị — CHƯA được quyết:

    OWNER_DECISION_REQUIRED — hai quyết định còn thiếu, chặn T-09B PLANNED -> READY:

    OD-A (CHẶN) — RUNTIME HOST của app web.
      App hiện chạy trên host artifact, dưới CSP chặn mọi host ngoài trừ Google Fonts
      (`webapp/README.md:13`, `docs/reviews/S001-discovery-baseline.md:94-95`,
      `webapp/app_shell.html:2`). Firebase cần gọi mạng tới endpoint của chính Firebase lúc
      chạy, nên Completion Gate A/B/C/D KHÔNG THỂ PASS chừng nào app còn ở host đó.
      Đây KHÔNG phải limitation của Firebase — đây là limitation của nơi app đang chạy, và
      vì vậy KHÔNG phải lý do để đổi khỏi Firebase.
      Khuyến nghị: Firebase Hosting (cùng hệ sinh thái đã chọn, một URL cố định, không cần
      terminal cho việc dùng hằng ngày). Chi tiết ba phương án:
      `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` § OWNER_DECISION_REQUIRED.

    OD-B (phụ thuộc OD-A) — THÀNH PHẦN FIREBASE.
      Khuyến nghị: Cloud Firestore, vì Realtime Database xoá âm thầm khoá có giá trị `null`
      (nguy hiểm cho `filled_vnd`/`released_vnd`/`ladder.month`) và vì trần 1 MiB/document
      của Firestore ép tách seed khỏi sổ kế toán — đúng ranh giới cần có.

    OD-B2 (kèm OD-B) — DANH TÍNH TỐI THIỂU cho security rules.
      Không có danh tính thì lựa chọn còn lại là cho ghi công khai, tức bất kỳ ai biết
      project ID đều sửa được sổ tiền — rơi vào điểm C của `DEC-011` (mất/hỏng lịch sử giao
      dịch thực tế). Khuyến nghị tối thiểu: Firebase Anonymous Auth, rules khoá vào đúng một
      UID. Đây KHÔNG phải "authentication phức tạp" theo điểm (3) ở trên.

Can Revisit After:
Khi có người thứ hai dùng công cụ hoặc công cụ được phát hành cho người khác — khi đó điểm (1)
và điểm (3) phải được định tuyến lại toàn bộ. Hoặc khi Firebase thay đổi điều khoản/giới hạn
làm Completion Gate T-09B không đạt được — khi đó là `ARCHITECTURE_CHANGE_REQUIRED`, không phải
quyết định của agent.

---

## DEC-020 — `OD-WEBAPP-03`: giải quyết OD-A/OD-B/OD-B2 cho T-09B; phát hiện khe mới OD-C (recovery semantics)

Date:
2026-09-02 (phiên Owner Decision — RESOLVE T-09B OD-A/OD-B/OD-B2)

Task:
`T-09B` / capability `CAP-WEBAPP`. Tiếp tục trên nhánh thẩm quyền hiện có
`claude/t09b-firebase-decision-nnoony`. Không implement Firebase, không sửa production code,
không chuyển `T-09B` sang `IN_PROGRESS`, không tạo task mới, không mở repair cycle.

Decision:

    (1) OD-A — RUNTIME HOST: APPROVED = FIREBASE HOSTING.

        Firebase Hosting trở thành runtime host cho ETH DCA OS webapp. Mục tiêu: URL web ổn
        định; browser được phép kết nối Firebase; không phụ thuộc host cũ (CSP chặn Firebase);
        chủ dự án mở web và dùng trực tiếp; daily/occasional use không cần terminal/coding
        agent. KHÔNG biến quyết định này thành deployment-platform redesign, KHÔNG thêm server
        riêng.

    (2) OD-B — DATABASE: APPROVED = CLOUD FIRESTORE.

        Firestore là durable source of truth cho T-09B. Baseline architecture:

            ethdca/state    <- document sổ kế toán (MUST_PERSIST tầng 1)
            ethdca/seed     <- document seed lịch sử giá (MUST_PERSIST tầng 2)

        Đây là baseline, không phải hợp đồng bất biến: nếu implementation chứng minh document
        size hoặc schema thực tế không đáp ứng được, KHÔNG silently redesign — báo
        `ARCHITECTURE_CHANGE_REQUIRED` kèm evidence. KHÔNG đổi sang Realtime Database.

    (3) OD-B2 — IDENTITY: APPROVED = FIREBASE AUTHENTICATION, ANONYMOUS AUTH.

        Mục đích duy nhất: cấp danh tính tối thiểu để Firestore Security Rules giới hạn đọc/ghi
        về đúng một owner UID. KHÔNG xây account system, login UI phức tạp, multi-user, roles,
        permissions framework, social login, email/password login — trừ khi Completion Gate
        yêu cầu (xem điểm (4) dưới đây, nơi email/password xuất hiện lại nhưng CHỈ cho mục đích
        recovery, không phải cho login hằng ngày).

        Security boundary nằm ở Firebase Authentication + Firestore Rules — KHÔNG public
        read/write. Firebase public client config KHÔNG tự động coi là secret; KHÔNG hard-code
        secret/private credential nào vào source repo. Phiên này chỉ ghi contract, KHÔNG cấu
        hình Firebase thật.

    (4) KIẾN TRÚC BASELINE (đã APPROVED, thay bản cũ chỉ có 2 tầng):

            Browser
               ↓
            Firebase Hosting
               ↓
            Firebase Authentication
               ↓
            Cloud Firestore
               ↓
            durable state

        `localStorage`/`sessionStorage`: mirror/cache only — không đổi so với `DEC-019`.

    (5) PHÁT HIỆN MỚI TẠI PHIÊN NÀY — `OD-C` (CHẶN, chưa quyết): khe giữa DURABLE STATE và
        KHẢ NĂNG AUTHENTICATE LẠI làm chủ sở hữu.

        Anonymous Auth cấp một UID được lưu **trong `IndexedDB` của đúng một browser profile**.
        Ba trong bốn kịch bản mất dữ liệu mà chính `RSK-001` nêu tên — "dùng cửa sổ riêng tư,
        đổi máy, đổi trình duyệt" — đều tạo ra **một `IndexedDB` trống**, tức một **anonymous
        UID MỚI**. Nếu Firestore Security Rules khoá cứng vào MỘT UID cố định (đúng như (3)
        approved), UID mới đó bị rules từ chối đọc/ghi — **không phải vì Firestore mất dữ liệu,
        mà vì trình duyệt mới không chứng minh được nó là owner**.

        Hệ quả cụ thể lên hai REQUIRED check đã FINALIZED của `T-09B`:

        - `CHECK-T09B-03` (xoá `localStorage` + `sessionStorage`) — **không bị ảnh hưởng**, vì
          Anonymous Auth session nằm ở `IndexedDB`, một kho khác. Check này vẫn PASS được trung
          thực với thiết kế đã approved.
        - `CHECK-T09B-04` (đóng/mở lại môi trường sử dụng, **"một profile/cửa sổ khác"**) —
          nhánh "profile/cửa sổ khác" **không PASS được trung thực** với Anonymous Auth đơn
          thuần, vì đó chính xác là kịch bản sinh UID mới.

        Đây đúng là ranh giới mà chỉ thị phiên này đặt tên trước: **(A) durable STATE
        persistence** đã được kiến trúc (1)-(4) giải quyết; **(B) khả năng AUTHENTICATE làm
        owner sau khi mất local browser identity** thì CHƯA. Không được tuyên bố "Firestore
        durable" = "chắc chắn recover được từ máy mới".

        KHÔNG làm yếu `CHECK-T09B-04` để né khe này. Ghi `OWNER_DECISION_REQUIRED` cho đúng một
        quyết định còn thiếu — hai phương án:

            R1 (KHUYẾN NGHỊ) — LINK MỘT RECOVERY CREDENTIAL VÀO ANONYMOUS UID.
              Dùng `linkWithCredential` gắn một cặp email/password (hoặc phone) vào UID nặc
              danh hiện có, một lần, ngay sau khi tạo UID lần đầu. Sinh hoạt hằng ngày KHÔNG
              đổi — vẫn tự động đăng nhập nặc danh trên browser đã liên kết, không có màn hình
              đăng nhập. Credential đó CHỈ dùng trên máy mới / browser mới: `signInWithEmailAnd
              Password` để quay lại ĐÚNG UID cũ, mở lại quyền đọc/ghi Firestore đã có. Đây
              KHÔNG phải "login UI phức tạp" hay "account system" — nó là một bước one-time
              setup, đúng tinh thần "tối thiểu cần cho durable persistence" của `DEC-019` điểm
              (3), vì không có nó thì "đổi máy" của `RSK-001` không có lối thoát nào khác
              ngoài forensic thủ công qua Firebase Console.

            R2 — CHẤP NHẬN GIỚI HẠN, THU HẸP TUYÊN BỐ TRUNG THỰC.
              Không thêm credential nào. Viết lại phạm vi "recover" của `CHECK-T09B-04` chỉ còn
              đúng SAME-BROWSER-PROFILE (đóng/mở lại trình duyệt, không đổi profile/máy). Kịch
              bản "đổi máy" của `RSK-001` KHÔNG được T-09B đóng bằng đường Firebase Auth; lối
              thoát duy nhất còn lại là export JSON thủ công (đã có, capability giữ nguyên qua
              `DEC-019`/OD-A). Phương án này giữ đúng "không xây login system" tuyệt đối, nhưng
              để hở đúng kịch bản rủi ro nặng nhất mà `RSK-001` nêu tên đầu tiên.

        Cho tới khi có quyết định, `T-09B` GIỮ `PLANNED`. `CHECK-T09B-03`, `CHECK-T09B-04` được
        chú thích tham chiếu `OD-C` — KHÔNG bị viết lại nội dung acceptance, vì nội dung cuối
        cùng phụ thuộc R1 hay R2 được chọn.

Reason:
Chỉ thị phiên yêu cầu tường minh: nếu Anonymous Auth làm một REQUIRED gate không PASS được một
cách trung thực, không được làm yếu gate — phải trả `OWNER_DECISION_REQUIRED` và giải thích
quyết định tối thiểu cần thêm. Đây đúng là tình huống đó: (3) giải quyết đúng câu hỏi nó được
hỏi ("cần một danh tính để rules không phải public"), nhưng không tự động giải quyết câu hỏi
khác ("danh tính đó có sống sót qua đổi máy không") — hai câu hỏi độc lập, và `STATE_AUTHORITY.md`
không cho phép agent tự chọn thay chủ dự án khi có đánh đổi thật (thêm một credential tối thiểu
so với thu hẹp lời hứa "đóng/mở lại vẫn dùng được" ở đúng kịch bản nặng nhất).

Impact:
- `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`: OD-A/OD-B/OD-B2 chuyển từ mở sang RESOLVED;
  thêm mục kiến trúc baseline 4 tầng; Load flow/Save flow được bổ sung bước Auth (làm rõ, không
  đổi acceptance); Failure semantics thêm dòng "Firebase Auth thất bại" (IN SCOPE, cùng nguyên
  tắc fail-visible); Ready Gate 14-mục: mục 12 (Firebase component) chuyển ✅; dòng "+" (không
  còn architecture ambiguity) VẪN ❌ vì `OD-C`. `CHECK-T09B-03`/`-04` được chú thích tham chiếu
  `OD-C`, KHÔNG đổi acceptance criteria.
- 16 REQUIRED check của Completion Gate **KHÔNG bị sửa yếu**. Completion Gate KHÔNG được freeze
  ở phiên này — freeze chỉ xảy ra khi Ready Gate đầy đủ (`STATE_AUTHORITY.md`,
  `TASK_COMPLETION_GATE_STANDARD.md` § Gate Creation Timing).
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`: cập nhật để phản ánh OD-A/
  OD-B/OD-B2 resolved và `OD-C` mở. Không sửa gate, không đổi capability/lineage.
- `PROJECT/REVIEW_BUDGET_LEDGER.md`: `CAP-WEBAPP` budget KHÔNG đổi — allowed 2 / used 0 /
  remaining 2. Không tiêu repair cycle (không có implementation nào chạy ở phiên này).
- `T-09B`: KHÔNG chuyển `IN_PROGRESS`. Ready Gate CHƯA đạt 100% (khối "+`" còn chặn) →
  **GIỮ `PLANNED`**, đúng chỉ thị §"STATE TRANSITION". Completion Gate CHƯA frozen.
- Số task ID mới = **0**. Số production file bị sửa = **0**.

Can Revisit After:
Khi chủ dự án chọn R1 hay R2 cho `OD-C`. Sau đó: hoàn tất Ready Gate, freeze Completion Gate,
`T-09B: PLANNED → READY`, rồi mở phiên thực thi riêng.

---

## DEC-021 — `OD-WEBAPP-04`: Personal Tool Simplification Principle; `OD-C` = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)

Date:
2026-09-02 (phiên Owner Decision — T-09B OD-C, tiếp nối `DEC-020` trên cùng nhánh thẩm quyền)

Task:
`T-09B` / capability `CAP-WEBAPP`. Đồng thời là quyết định cấp sản phẩm áp dụng cho toàn bộ
ETH DCA OS, không riêng T-09B — ghi theo §0 của chỉ thị phiên.

Canonical location:
File này (`PROJECT/PROJECT_DECISIONS.md`) — **cùng vị trí** đã giữ `DEC-011` (Owner Product
Intent gốc) và `DEC-019` (bổ sung lần một). Quyết định dưới đây là **lần bổ sung thứ hai** vào
cùng một mạch Product Intent, KHÔNG tạo artifact riêng: `DEC-011` đã lập tiền lệ "map vào
authority sản phẩm hiện có" thay vì nhân bản sang `PROJECT_PROFILE.md`; quyết định này giữ
đúng tiền lệ đó để không vi phạm `STATE_AUTHORITY.md` § Single Source Of Truth.

Decision:

    (1) PERSONAL TOOL SIMPLIFICATION PRINCIPLE — BỔ SUNG LẦN HAI cho `DEC-011`
        (`DEC-019` là lần một), KHÔNG thay thế.

        ETH DCA OS là công cụ CÁ NHÂN, SINGLE-USER, DÙNG KHI CẦN, TẦN SUẤT THẤP — không phải
        sản phẩm thương mại, không phải public multi-user, không phải enterprise application.
        Mục tiêu KHÔNG phải một hệ thống hoàn hảo về mọi khía cạnh kỹ thuật. Mục tiêu là ĐƠN
        GIẢN + DỄ SỬ DỤNG + ĐÚNG Ở NHỮNG CHỖ ẢNH HƯỞNG ĐẾN TIỀN.

        PRIORITY ORDER (thay thế cách viết rút gọn "correctness · usability · low operational
        burden · implementation simplicity · cost · technical elegance · scalability" của
        `DEC-019` điểm 1 bằng một danh sách chi tiết hơn — KHÔNG mâu thuẫn, chỉ khai triển):

            1. Financial correctness
            2. Algorithm correctness
            3. Decision/recommendation usefulness
            4. Accounting correctness
            5. Không mất dữ liệu quan trọng
            6. Daily usability
            7. Implementation simplicity
            8. Low operational burden
            9. Cost
            10. Security hardening
            11. Scalability / enterprise concerns

        KHÔNG đảo thứ tự này chỉ vì technical best practice chung.

    (2) CRITICAL PRODUCT QUESTION — bài kiểm tra bắt buộc trước khi một finding/proposal vào
        V1 critical path:

            "Nếu không xử lý vấn đề này, nó có khả năng thực tế:
             A. làm Owner đưa ra quyết định tài chính sai?
             B. làm thuật toán phân tích giá sai?
             C. làm Buy Score/regime/budget/recommendation sai?
             D. làm accounting/holdings/average cost sai?
             E. làm mất dữ liệu tài chính quan trọng?
             F. hoặc khiến Owner không thể sử dụng app theo workflow cá nhân thông thường?"

        Nếu KHÔNG cho cả sáu: mặc định route HARDENING / DEFER / OUT OF SCOPE theo canonical
        governance phù hợp. Finding không tự động tạo task.

        Đây khớp với `DEC-011` điểm A–F đã có (làm sai recommendation/tiền/mất lịch sử/dữ
        liệu thị trường không đúng/app không chạy được/official result sai) — quyết định này
        diễn đạt lại thành một câu hỏi thực thi trực tiếp, KHÔNG thay `DEC-011` điểm A–F.

    (3) SECURITY PHILOSOPHY. Security KHÔNG phải trọng tâm chính của V1. Chủ dự án chấp nhận:
        công cụ chỉ phục vụ cá nhân; khả năng có người chủ động reverse-engineer/tấn công được
        xem là THẤP; dữ liệu không cần mức bảo vệ enterprise; không cần threat model phức tạp;
        không cần security architecture vượt nhu cầu thực tế. Vẫn giữ một MINIMUM SECURITY
        FLOOR.

    (4) MINIMUM SECURITY FLOOR — V1 chỉ cần đủ để tránh:
          - vô tình public write nếu điều đó có thể làm state bị sửa/hỏng;
          - commit password/private credential/service-account secret vào repo;
          - lỗi authentication/persistence làm app hiểu nhầm dữ liệu sai là state hợp lệ;
          - lỗi ghi dữ liệu nhưng UI báo đã lưu thành công;
          - security mechanism quá yếu đến mức tạo nguy cơ thực tế làm sai/mất accounting
            state.
        KHÔNG mở rộng security scope chỉ để chống hypothetical attacker.

    (5) OD-C = R2 — SIMPLIFIED PERSONAL-TOOL RECOVERY. APPROVED.

        Chủ dự án KHÔNG yêu cầu V1 đảm bảo seamless identity recovery khi đổi máy, đổi
        browser, mất toàn bộ browser profile, hoặc mất Firebase Anonymous Auth identity. Các
        tình huống này KHÔNG phải V1 critical acceptance requirement. KHÔNG xây email/password
        recovery chỉ để giải quyết các edge case này — giữ nguyên architecture Anonymous Auth
        thuần, KHÔNG thêm email/password, Google Sign-In, account system, registration, login
        UI, password recovery, multi-user support cho V1.

        Đây là **OWNER SCOPE DECISION dựa trên Product Intent mới**, KHÔNG phải kết luận kỹ
        thuật rằng Anonymous Auth "đủ" theo nghĩa PASS — khe kỹ thuật ghi ở `DEC-020` (Anonymous
        UID mới sau đổi máy/browser/cửa sổ riêng tư bị Firestore rules từ chối) vẫn ĐÚNG và
        KHÔNG bị phủ nhận. Điều thay đổi là phạm vi CHẤP NHẬN của V1, không phải sự thật kỹ
        thuật.

    (6) `CHECK-T09B-04` DISPOSITION — audit trail bắt buộc, KHÔNG được gọi đây là bug fix hay
        evidence PASS:

            OLD REQUIREMENT (viết tại `DEC-019`/Task Spec ban đầu):
              "đóng hẳn trình duyệt (hoặc dùng một profile/cửa sổ khác), mở lại, state phục
              hồi đầy đủ" — bao gồm cả nhánh cross-device/cross-browser.

            OWNER PRODUCT INTENT CHANGE (quyết định này):
              Personal Tool Simplification Principle §(1)-(4) + OD-C = R2: cross-device /
              cross-browser / lost-identity recovery KHÔNG phải V1 critical acceptance
              requirement.

            NEW V1 REQUIREMENT:
              Đóng/mở lại trình duyệt THÔNG THƯỜNG (cùng browser profile); reload; quay lại
              app sau một khoảng thời gian; restart máy NẾU browser profile / site identity
              (tức `IndexedDB` giữ Anonymous Auth session) vẫn còn — state PHẢI tiếp tục sử
              dụng được, và bất biến kế toán PHẢI được bảo toàn.

              Cross-device / cross-browser / lost-identity recovery: **OUT OF SCOPE V1**.
              Khi rules từ chối một UID không khớp owner (đúng kịch bản này), app PHẢI hiện rõ
              đây là "không nhận diện được thiết bị/trình duyệt này" — KHÔNG được im lặng hiện
              state rỗng như thể đó là sổ hợp lệ của một owner mới (thuộc `CHECK-T09B-11`,
              không mở REQUIRED check mới). Lối thoát cho cross-device V1: export/import JSON
              thủ công (capability đã giữ nguyên qua `OD-A`, `DEC-019`).

        `CHECK-T09B-03` (xoá `localStorage`+`sessionStorage`, cùng browser) **KHÔNG đổi, KHÔNG
        bị làm yếu** — kịch bản đó không đụng `IndexedDB`, không liên quan `OD-C`.

    (7) PERSISTENCE CORRECTNESS VẪN REQUIRED, không bị hạ bởi việc giảm ưu tiên security:
        save đúng; load đúng; Firebase write có xác nhận từ server; write failure visible;
        load failure visible (gồm cả "rules từ chối UID" — một dạng read/auth failure, PHẢI
        visible, KHÔNG được hiểu nhầm thành state hợp lệ); malformed/corrupt state không âm
        thầm thành official accounting state; localStorage mirror không âm thầm ghi đè durable
        source mới hơn; T-09A accounting invariants được bảo toàn. KHÔNG đổi 16 REQUIRED check
        khác ngoài `CHECK-T09B-04`.

    (8) FINANCIAL/ALGORITHM/ACCOUNTING CORRECTNESS GIỮ NGUYÊN NGHIÊM NGẶT — market data
        correctness, indicator correctness, Buy Score, regime, budget, opportunity fund,
        recommendation, trade accounting, holdings, average cost, pool ownership,
        reserve/release, ladder accounting, historical transaction integrity: KHÔNG một gate/
        evidence nào trong nhóm này bị hạ bởi quyết định này.

    (9) HARDENING RULE. Finding thuộc advanced security, cross-device identity recovery,
        enterprise backup, high availability, scalability, multi-user, roles, advanced
        authorization, sophisticated attacker, provider abstraction, disaster recovery,
        future-proof architecture — KHÔNG tự động là V1 blocker. Mặc định HARDENING / DEFER /
        OUT OF SCOPE, trừ khi có bằng chứng production-realistic cho A-F ở điểm (2).

    (10) OVER-ENGINEERING GUARD. Trước khi thêm bất kỳ mechanism mới: hỏi "Owner có thực sự
         cần cơ chế này để sử dụng ETH DCA OS không?" — nếu KHÔNG, không implement chỉ vì đó
         là best practice. Ưu tiên minimal sufficient implementation.

    (11) T-09B SCOPE giữ nguyên: DURABLE PERSISTENCE. KHÔNG biến thành authentication project,
         security project, backup project, deployment platform project, data migration
         project.

    (12) HISTORICAL STATE giữ nguyên `DEC-019` điểm 6: forensic/migrate/backfill = OUT OF
         SCOPE T-09B V1. Không tự sửa lịch sử, không tự tuyên bố sạch. Banner cảnh báo hiện có
         phải sống sót qua persistence round-trip (đã yêu cầu ở `CHECK-T09B-15`, không đổi).

Reason:
`OD-C` (`DEC-020`) trả đúng hai phương án kỹ thuật và không tự chọn thay chủ dự án, vì đó là
đánh đổi thật giữa thêm một credential tối thiểu (R1) và thu hẹp lời hứa recovery (R2). Chủ
dự án chọn R2 và đi xa hơn: phát biểu tường minh một nguyên tắc sản phẩm bao trùm để các phiên
tương lai không phải hỏi lại "có cần cơ chế X không" cho từng finding — đúng tinh thần
`CAPABILITY_MODEL.md` § Capability-First Question Order, nay có thêm một bộ lọc sản phẩm cụ
thể trước khi một finding được xem xét đưa vào V1 critical path.

Impact:
- `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`: `OD-C` đóng = R2. `CHECK-T09B-04` được viết
  lại theo audit trail ở điểm (6) — KHÔNG xoá lịch sử yêu cầu cũ, chỉ thêm bằng
  `COMPLETION GATE CHANGE PROPOSAL`-style disclosure trước khi freeze. Ready Gate đánh giá lại
  toàn bộ; nếu không còn blocker nào thuộc financial/data/persistence correctness →
  `T-09B: PLANNED → READY`, Completion Gate → FROZEN.
- `PROJECT/HARDENING_BACKLOG.md`: thêm `H-23` — cross-device/lost-identity recovery, OUT OF
  SCOPE V1, `RE_TRIGGER_CONDITION` = khi có người dùng thứ hai hoặc khi Owner tự yêu cầu lại.
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`: cập nhật trạng thái `T-09B`
  và ghi nhận Personal Tool Simplification Principle.
- `PROJECT/REVIEW_BUDGET_LEDGER.md`: `CAP-WEBAPP` budget KHÔNG đổi — allowed 2 / used 0 /
  remaining 2. Freeze Completion Gate và chuyển `READY` không tiêu repair cycle (đây vẫn là
  chuẩn bị, không phải implementation).
- KHÔNG đổi `DEC-011` (10 điểm Acceptance, điểm A–F) — điểm (2) của quyết định này diễn đạt lại
  thành câu hỏi thực thi, không thay nội dung. KHÔNG đổi `DEC-019` điểm 1 (thứ tự ưu tiên 7
  mục) — điểm (1) của quyết định này khai triển chi tiết hơn, không mâu thuẫn.
- KHÔNG đổi bất kỳ REQUIRED check nào thuộc financial/algorithm/accounting correctness.
- Số task ID mới = **0**. Số production file bị sửa = **0**.

Can Revisit After:
Khi có người thứ hai dùng công cụ hoặc công cụ được phát hành cho người khác (cùng điều kiện
`DEC-011`/`DEC-019` đã ghi) — khi đó Personal Tool Simplification Principle và `OD-C = R2` phải
được định tuyến lại toàn bộ, và `H-23` được xem xét lại.

---

## DEC-022 — `OD-WEBAPP-05`: Integration size disposition cho `T-09B` — ACCEPT THE DIVERGENCE

Date:
2026-09-02 (phiên tiếp nối S014 — REAL FIREBASE SETUP & PRODUCTION REACHABILITY)

Task:
`T-09B` / capability `CAP-WEBAPP`. Đóng hard-stop `INTEGRATION_DECISION_REQUIRED` mà
`branch_authority_check.sh` báo trên branch `claude/t09b-firebase-implementation-nz50is`
(divergence LOC = 12.272, ngưỡng cảnh báo > 5.000).

Decision:

    ACCEPT THE DIVERGENCE cho `T-09B` tại thời điểm này. KHÔNG "integrate now" (không merge
    `main`), KHÔNG cut scope.

Bằng chứng đo được — số đo LOC thô của script KHÔNG đại diện cho business/production
complexity:

    git diff --shortstat main..claude/t09b-firebase-implementation-nz50is
      -> divergence LOC = 12.272

    Phân rã theo declared production path (PRODUCTION_PATHS.md §1 bảng + §2 loại trừ):
      webapp/app_logic.js + app_shell.html + build_app.js  -> +560 / -162  (implementation thật)

    Phần còn lại (~11.550 dòng) là generated dependency metadata:
      webapp/package-lock.json  -> +9.482 dòng (ghim `firebase@12.18.0` + `firebase-tools@15.28.2`
                                    và toàn bộ transitive dependency của hai package đó)
      webapp/test_firebase_harness.js, test_t09b_persistence.js (mới) và bảo trì 5 test cũ
                                 -> ~892 + ~171 dòng test/harness (KHÔNG phải production path,
                                    `PRODUCTION_PATHS.md` §2)

    Kiểm tra tương ứng (sanity, KHÔNG cut/rewrite dependency tree chỉ để làm số này đẹp hơn):
      723 package entry mới trong lockfile; 677/723 không chứa chuỗi "firebase" trong đường dẫn
      nhưng TOÀN BỘ là transitive dependency trực tiếp của `firebase-tools` (CLI monolith bao
      Cloud SQL connector, Pub/Sub, App Hosting, Data Connect/pglite — các sản phẩm Firebase
      T-09B KHÔNG dùng) hoặc của package `firebase` (SDK modular — có mặt trong node_modules
      cho MỌI sản phẩm Firebase, nhưng trang chỉ nạp 3 file compat qua CDN: app/auth/firestore;
      không có byte nào của Analytics/Messaging/Storage/... được gửi tới trình duyệt). Không
      phát hiện dependency nào ngoài `firebase`/`firebase-tools` — không cần scope-expand để dọn.

Reason:
`branch_authority_check.sh` đo LOC thô của toàn bộ diff, không phân biệt được production code với
generated lockfile — đây là hạn mức của chính công cụ (`H-09`/`H-12`/`H-21` đã ghi các khiếm
khuyết cùng lớp của bộ đo). Coi 9.482 dòng lockfile là "12.272 dòng thay đổi cần review" sẽ đánh
giá sai độ phức tạp thật của T-09B: `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.4 đã đo delivery change
budget CHUẨN (theo khai báo production path) là 3 file, +662/−188 — nằm trong mọi ngưỡng đã có.
Không có lý do nghiệp vụ nào để cắt scope (rules/config/harness đều cần thiết cho architecture đã
FROZEN ở `DEC-020`) hay viết lại cách quản lý dependency (vendor một `firebase-tools` tối giản là
over-engineering, trái Personal Tool Simplification Principle `DEC-021`).

Impact:
- Hard-stop `INTEGRATION_DECISION_REQUIRED` trên branch `claude/t09b-firebase-implementation-nz50is`
  **ĐÓNG** cho mục đích tiếp tục thực thi T-09B trên chính branch này. KHÔNG mở merge vào `main`.
- `PROJECT/HARDENING_BACKLOG.md`: thêm `H-28` — dependency footprint của `firebase-tools`
  (devDependency, không phải runtime browser) rộng hơn nhiều so với phạm vi dùng thật
  (`emulators:start --only auth,firestore`, `deploy --only hosting,firestore:rules`) —
  PROVISIONAL HARDENING, tầng tooling, không phải finding sản phẩm.
- KHÔNG đổi `CAP-WEBAPP` budget (`REVIEW_BUDGET_LEDGER.md` §2.2/§2.2.4) — quyết định này không
  phải repair cycle, không tiêu budget.
- Số task ID mới = **0**. Số production file bị sửa bởi CHÍNH quyết định này = **0**.

Can Revisit After:
Khi branch `claude/t09b-firebase-implementation-nz50is` được đề xuất tích hợp vào `main` (một
Owner Decision khác, theo đúng mẫu `DEC-013`) — khi đó đo lại divergence LOC tại thời điểm đó,
không dùng lại con số của quyết định này. Hoặc khi `firebase-tools`/`firebase` phát hành phiên bản
làm thay đổi đáng kể cỡ lockfile.

---

## DEC-023 — `OD-WEBAPP-06`: `T-09B` chạy trên Firebase project DÙNG CHUNG (`tinphatcontent`); merge rules an toàn; Hosting site mặc định

Date:
2026-09-02 (phiên tiếp nối — SHARED FIREBASE PROJECT / FIRESTORE RULES SAFE MERGE)

Task:
`T-09B` / capability `CAP-WEBAPP`.

Decision:

    (1) SHARED PROJECT LÀ THỰC TẾ ĐƯỢC CHẤP NHẬN, KHÔNG PHẢI ARCHITECTURE_CHANGE_REQUIRED.

        Project Firebase thật Owner cấp cho T-09B (`tinphatcontent`, display name "CoinDCA")
        trước đó phục vụ một ứng dụng khác ("Content — công cụ Zalo Group, Tín Phát"). Kiến
        trúc T-09B (`DEC-020`) — Browser → Firebase Hosting → Anonymous Auth → Cloud Firestore
        → `ethdca/state` + `ethdca/seed` — KHÔNG đổi. Điểm triển khai thực tế duy nhất: cùng
        một Cloud Firestore database còn chứa namespace Content (`users`, `contents`,
        `schedules`, `groups`, `config`, `fb_queue`, `audit_logs`). Không tạo Firebase project
        mới, không đổi Firestore sang database khác, không đổi Authentication model, không thêm
        backend/provider abstraction chỉ để cách ly Content.

    (2) FIRESTORE RULES — MERGE AN TOÀN, KHÔNG THAY THẾ.

        `firestore.rules` của repo nay là rules Content THẬT (giữ nguyên văn, không refactor/
        format lại/đổi tên/thêm-bớt quyền) cộng thêm đúng hai khối `match /ethdca/state` và
        `match /ethdca/seed` (hàm đổi tên `isCoinDcaOwner()` để không trùng hàm `isOwner(f)`
        đã có sẵn của Content — trùng tên là lỗi biên dịch rules). Không thêm catch-all mới.

        Kiểm chứng bằng Firestore Rules Emulator (`webapp/test_shared_rules_merge.js`, đăng ký
        `npm run test:rules-merge`): battery 53 probe phủ toàn bộ 8 collection Content, so
        ALLOW/DENY giữa rules Content nguyên văn (BEFORE) và rules đã merge (AFTER) —
        **0 lệch**. Ma trận CoinDCA 12 ca (§8 chỉ thị) PASS 12/12 trên rules đã merge. Chi tiết
        đầy đủ: `docs/reviews/T-09B-shared-rules-merge.md`.

        `CONTENT_BEHAVIOR_PRESERVED = YES`. Chưa deploy — owner UID trong rules còn placeholder
        `OWNER_UID_REQUIRED`; deploy thật cần UID Anonymous Auth thật của Owner (lấy từ trình
        duyệt hằng ngày, chưa có tại phiên này) và do chính Owner chạy (agent không có Firebase
        CLI authority trong môi trường này — không đổi từ checkpoint trước).

    (3) HOSTING — RESOLVED = DÙNG SITE MẶC ĐỊNH CỦA `tinphatcontent`.

        Owner tự kiểm tra Firebase Console: Hosting của project `tinphatcontent` **chưa được
        setup** (còn màn hình "Get started"), không có site/deployment Content nào cần bảo
        toàn. Owner quyết định CoinDCA dùng Hosting site mặc định — KHÔNG cần multi-site,
        hosting target riêng, hay project Firebase mới chỉ để cách ly Content. `firebase.json`
        của repo (`webapp/public` → Hosting) giữ nguyên, không cần sửa.

    (4) OBSERVATION VỀ RULES CONTENT — KHÔNG SỬA.

        Rules Content hiện tại cho `schedules` (update) và `fb_queue` (write) chỉ yêu cầu
        `signedIn()` (bất kỳ ai đã xác thực, kể cả Anonymous, không cần role) — permissive hơn
        các collection khác. Đây là thiết kế có sẵn của Content, không liên quan tới merge của
        CoinDCA (xác nhận identical BEFORE/AFTER), không thuộc `DEC-021` Critical Product
        Question A-F của ETH DCA OS. Không sửa trong T-09B. Không tạo `HARDENING_BACKLOG.md`
        entry — đó là backlog của CAP-* thuộc dự án này, không phải nơi audit ứng dụng khác.

Reason:
Firestore chỉ có một rules document cho cả database; deploy nguyên văn `firestore.rules` cũ
(chỉ có CoinDCA, catch-all deny) lên project dùng chung sẽ xoá quyền truy cập của Content —
đúng loại hậu quả `CLAUDE.md` § Conflict Rule yêu cầu dừng lại và xử lý tường minh, KHÔNG được
đoán. Owner đã tự xác nhận Hosting an toàn (chưa setup) nên không cần quyết định gì thêm ở đó;
phần rules cần bằng chứng kỹ thuật (không chỉ lời hứa "sẽ không đổi hành vi Content"), nên dùng
đúng cơ chế RISK_MODEL.md đã có sẵn cho HIGH Blast Radius: batch verification trước khi cho
phép bước kế tiếp (deploy), không phải một hard-stop kiến trúc.

Impact:
- `firestore.rules`: merge hoàn tất, CHƯA deploy.
- `webapp/test_shared_rules_merge.js` (mới), `webapp/package.json` (`test:rules-merge`).
- `docs/reviews/T-09B-shared-rules-merge.md` (mới) — evidence đầy đủ.
- `PROJECT/PROJECT_PROGRESS.md`: cập nhật Last Updated + Session History (tối thiểu).
- KHÔNG đổi Completion Gate 16 REQUIRED check nào. KHÔNG đổi `DEC-019`/`DEC-020`/`DEC-021`/
  `DEC-022`. KHÔNG tiêu `CAP-WEBAPP` budget (2/0/2 không đổi) — đây không phải repair cycle.
- Số task ID mới = **0**. Số hàm/quyền Content bị đổi = **0** (đo được bằng 53 probe emulator).

Can Revisit After:
Khi rules Content thật đổi (Owner tự deploy thay đổi phía Content, ngoài phạm vi T-09B) — khi
đó `webapp/test_shared_rules_merge.js` cần chạy lại với bản BEFORE mới trước khi tái xác nhận
merge an toàn. Hoặc khi Owner tách CoinDCA sang project Firebase riêng (không còn lý do giữ
merge phức tạp này).
