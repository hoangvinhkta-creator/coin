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
