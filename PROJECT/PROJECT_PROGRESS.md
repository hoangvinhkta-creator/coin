# PROJECT PROGRESS

## Project Summary
Project:
ETH DCA Operating System — V2.1.5

Objective:
Xây một công cụ chạy trên trình duyệt, dùng được như bảng tính, để chủ dự án theo dõi quá trình
hold/trade coin và nhận cảnh báo dựa trên các chỉ báo phân tích của bộ spec V2.1.5
(OSCORE, regime, ladder zone, giới hạn thực thi, chất lượng dữ liệu).

Ràng buộc chi phối mục tiêu này: Implementation Plan đặt cổng chặn — app MVP đầy đủ chỉ được
dựng sau khi backtest cho verdict BUILD. Xem `PROJECT/PROJECT_DECISIONS.md` DEC-005.

Project Type:
LEGACY

Profile:
PRODUCT

Last Updated:
2026-08-23 — kết phiên S001 (AUDIT READ-ONLY)

Overall Status:
IN_PROGRESS

Current Phase:
Phase 1 — Discovery & Baseline (HOÀN TẤT). Kế tiếp: Phase 2 — Chốt hướng đi (T-04)

Current Task:
T-04 — Chốt lộ trình và đóng băng tiêu chí (chưa mở, chờ chỉ thị của chủ dự án)

Current Task Mode:
MAJOR

Next Recommended Task:
Phê duyệt RCP-001 (xem mục "Pending Roadmap Change Proposal"). Sau khi duyệt mới mở T-04 ở phiên
S002. KHÔNG tự mở.

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính. Bằng chứng routing của từng task nằm trong file task tương ứng dưới
`docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối tài liệu này.

Phase 3 trở đi là **roadmap sơ bộ**. Theo `00_SESSION_ORCHESTRATION.md` ("Do not freeze distant
task details before discovery is sufficient"), các task này sẽ được tính lại routing và chốt
Completion Gate tại T-04, không đóng băng bây giờ.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| DONE | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| BLOCKED | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. Song song được với T-02 |
| PLANNED | T-04 | Chốt lộ trình và đóng băng tiêu chí | Biến kết quả khảo sát thành lộ trình chính thức, có tiêu chí nghiệm thu đóng băng | C | xhigh | Sau T-01, T-02, T-03 |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. Chặn T-06, T-08 |
| PLANNED | T-06A | Ghim phiên bản thư viện và ghi môi trường vào run record | Không ghim thì kết quả chạy chính thức không tái lập lại được về sau | B | high | Sau T-04. BẮT BUỘC xong trước T-06 |
| PLANNED | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | Sau T-05 và T-06A. Cần máy/VPS có mạng Binance |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | Sau T-06. Chặn T-11 |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05. Song song được với T-06 |
| PLANNED | T-09A | Sửa lỗi kế toán trong app web | Vá 3 lỗi có thể làm sai sổ vốn trước khi app được dùng với tiền thật | C | high | Sau T-03 và T-04 |
| PLANNED | T-09B | Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | Sau T-04. Nên làm trước T-10 |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08 và T-09B |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07 và chỉ khi verdict = BUILD |

## Pending Roadmap Change Proposal

### RCP-001 — CHỜ PHÊ DUYỆT
Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`
Ngày trình: 2026-08-23
Nguồn: 33 finding của S001 + R-01…R-11 + V-01…V-03 + RSK-002…RSK-009 + BLK-001, BLK-002

Đề xuất: gom thành **15 work package** theo 10 nguyên nhân gốc, chia bốn lớp
A (trước official run) / B (trước verdict) / C (trước productization) / D (defer).
ADDED 15 · CHANGED 5 (T-03, T-06, T-07, T-09A, T-10/T-11) · REMOVED 1 (T-06A, bị WP-A1 thay thế).
Tổng lộ trình sẽ thành 28 task nếu được duyệt.

**Bảng roadmap chuẩn ở mục "Overall Roadmap" phía trên CHƯA bị sửa.** Theo
`00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule", thay đổi lộ trình phải được trình và
chấp thuận trước khi áp dụng. Vì bảng chuẩn không đổi, `PROJECT/LO_TRINH_DE_HIEU.md` vẫn đồng bộ
với nó — hai roadmap không có state riêng.

Hai phát hiện của RCP-001 làm đổi cách hiểu về lộ trình:
1. **BLK-001 chỉ chặn đúng một điểm là T-06.** Không work package nào trong 15 gói cần dữ liệu
   Binance thật, nên toàn bộ chương trình remediation chạy được trong khi BLK-001 vẫn còn.
2. **DEC-005 rời khỏi đường găng tới verdict.** DEC-005 quyết định phạm vi app; toàn bộ lớp A là
   backtest engine. Lớp A khởi động được mà không cần chốt DEC-005.

Chủ dự án cần quyết bốn điểm nêu ở mục 11 của tài liệu đề xuất.

## Current Task Snapshot

Task:
T-04 — Chốt lộ trình và đóng băng tiêu chí

Task Mode:
MAJOR

Status:
PLANNED

Required Gate Progress:
0 / 0 PASS — Ready Gate và Completion Gate của T-04 CHƯA soạn. Sẽ soạn khi chủ dự án cho phép
mở S002. Chủ dự án đã yêu cầu dừng sau S001, không tự chuyển phase.

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.80 (D3 R3 B2 A3 X3) → floor `cognitive:A>=3&X>=3` → C

Effort Routing Score:
2.60 (U2 V2 H3 C3 F3) → xhigh

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Escalation Triggers:
- Số lượng finding vượt khả năng xếp thứ tự trong một phiên → chia T-04 thành nhiều phiên,
  KHÔNG nâng Tier.
- Chủ dự án chưa chốt DEC-005 → `MISSING_INPUT`, chuyển BLOCKED, KHÔNG nâng Tier.

Lưu ý bàn giao: kết quả S001 đề xuất chèn một phase "đóng cổng verdict" (R-01…R-04, R-07, R-08,
T-06A, V-01/02/03) vào trước T-06. Đề xuất này CHƯA được đưa vào bảng roadmap — theo
`00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule", việc tái cấu trúc roadmap phải đi qua
khối `ROADMAP CHANGE PROPOSAL` và được chủ dự án chấp thuận, không làm im lặng.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

Hiện chưa có Micro Task nào được mở.

## Active Blockers

### BLK-001 — Không có đường tới dữ liệu Binance từ môi trường phát triển
Ảnh hưởng: T-06, và qua đó chặn T-07 và T-11.
Mô tả: Repo chưa từng có official run (`results/` không tồn tại và nằm trong `.gitignore`).
Môi trường phát triển bị chặn egress tới Binance, nên mọi kiểm chứng trong repo chạy trên dữ
liệu tổng hợp và tự gắn cờ `official: false`.
Đường xử lý đã được `docs/DATA_SOURCES.md` chấp nhận: chạy `ethdca fetch` trên máy của chủ dự án
hoặc VPS nước ngoài, copy `data/raw/` về, rồi xác minh bằng cách chạy `ethdca freeze` ở cả hai
máy và đối chiếu hash manifest phải trùng khớp.
Cần từ chủ dự án: một máy hoặc VPS truy cập được `data.binance.vision` và `api.binance.com`.

Bằng chứng E1 thu tại S000 (2026-08-23): cả ba host đều bị chặn ở tầng proxy, không phải lỗi
cấu hình phía repo.
`api.binance.com` → `curl: (56) CONNECT tunnel failed, response 403`
`data-api.binance.vision` → `curl: (56) CONNECT tunnel failed, response 403`
`api.coingecko.com` → `curl: (56) CONNECT tunnel failed, response 403`
PyPI thì thông, nên đây là chặn có chọn lọc theo host, không phải mất mạng.

### BLK-002 — Tính năng cảnh báo chưa được đặc tả
Ảnh hưởng: T-10, và là lý do T-08 tồn tại.
Mô tả: `docs/spec/01_PRODUCT_SPEC_V2_1_5.md` không có mục nào về alert/cảnh báo/notification.
Product Spec chỉ quy định trạng thái hiển thị thụ động trên hero khi mở trang (§11–§13).
Implementation Plan §9 hoãn có chủ đích: "không cần cron cho tới khi thực sự cần notification".
Điều kiện kích hoạt thì đã có đầy đủ trong Strategy Spec (§3, §4, §5, §9, §10, §15, §17, §18)
và danh mục 30 reason code ở Strategy §20 chính là bộ khung tự nhiên cho danh sách cảnh báo.
Nghĩa là: đây là khoảng trống ĐẶC TẢ, không phải khoảng trống code. Không thể triển khai đúng
trước khi đặc tả xong (T-08).

## Active Risks

### RSK-001 — Mất lịch sử giao dịch thật (mức: cao)
App web hiện lưu state trong localStorage của trình duyệt cộng cơ chế tự xuất bản lại trang.
Đây không phải "một database" như Implementation Plan §9 yêu cầu. Xóa dữ liệu site, dùng cửa sổ
riêng tư, đổi máy, hoặc publish thất bại đều có thể làm mất dữ liệu chưa xuất ra ngoài.
Giảm thiểu: T-09B. Cho tới khi T-09B xong, chủ dự án nên xuất file JSON định kỳ.

### RSK-002 — Hai bản cài đặt chiến lược trôi khỏi nhau (mức: cao) — S001 XÁC NHẬN (E1)
Implementation Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Trang
tĩnh không chạy được Python nên `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả.
Cơ chế chặn hiện có là parity check OSCORE 40 ngày (lệch tối đa 7.4e-11 lần kiểm gần nhất),
nhưng parity chỉ phủ OSCORE tổng — chưa phủ unlock, spacing, phân bổ ladder, invalidation,
regime. Mỗi tính năng port thêm sang JS sẽ mở rộng bề mặt trôi nhanh hơn khả năng phát hiện.
Giảm thiểu: mở rộng phạm vi parity trước khi port thêm; xác nhận trong T-02/T-03.

### RSK-003 — Nghi vấn ba lỗi kế toán trong app web (mức: trung bình, một phần đã được loại trừ)
Ghi nhận ban đầu từ việc đọc code: (a) hàm chọn tháng hiện hành trả về tháng có key lớn nhất
chứ không phải tháng của ladder, nên release vốn có thể trả nhầm pool khi có nhiều tháng;
(b) mức unlock không giới hạn số vốn được reserve; (c) trạng thái dữ liệu INVALID không chặn
tạo action mới như Strategy §3 yêu cầu.

Cập nhật sau bằng chứng E1 tại S000: `webapp/test_zone.js` chạy thật và cho thấy bất biến kế
toán **giữ đúng trong kịch bản một tháng** — tổng bảo toàn 3.000.000 qua đủ chuỗi thao tác
fill toàn phần → fill một phần → invalidation → release, và không pool nào âm.
Nghĩa là (a) **chưa bị bác bỏ nhưng cũng chưa được tái hiện**: test hiện có chỉ dùng một tháng,
đúng vào điểm mù của nghi vấn. (b) và (c) chưa có ca kiểm thử nào chạm tới.

Còn lại phải xác minh ở T-03 bằng ca kiểm thử **đa tháng** cho (a), và ca kiểm thử riêng cho
(b), (c). Sửa: T-09A. Không sửa trong S001 vì S001 là read-only.

### RSK-004 — Bộ test app web không chạy được từ bản checkout sạch (mức: trung bình)
Bằng chứng E1 tại S000: hai test webapp **chạy được và cho kết quả đúng**, nhưng chỉ sau khi
dựng thủ công hai thứ không có trong repo — `webapp/app_final.html` (phải build) và
`demo/results3/live_seed.json` (**không tồn tại ở bất kỳ đâu trong repo**).
Nghĩa là không ai clone repo về mà chạy được test của app, và không có gì bảo vệ hồi quy tự động.

Ghi nhận thêm: hai test ghi ảnh chụp màn hình vào thư mục làm việc hiện hành. Nếu chạy từ trong
`webapp/` sẽ để lại `app-dash.png` và `app-zone.png` trong repo, mà hai file này không nằm trong
`.gitignore`.

Định lượng mức bảo vệ hồi quy thật sự (có assertion nào fail được không): T-03.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình) — S001 XÁC NHẬN VÀ MỞ RỘNG (E1)
S001 xác nhận và phát hiện quy ước không được ghi ở nhiều chỗ hơn dự kiến: ngoài ánh xạ
gate-fail → verdict, còn có ngưỡng số tự đặt của FS-02/FS-07/FS-12, phạm vi tính FS-03/FS-07 chỉ
trên window W5, và tham số `shift_days=10` của Control G. `verdict.py` còn ghi rằng ánh xạ được
tài liệu hoá ở `docs/CONVENTIONS.md`, nhưng file đó không có mục nào về verdict.
Xem finding F-015, F-016, F-026.

`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ trong T-02 để không bị coi nhầm
là điều khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

### RSK-006 — Không ghim phiên bản thư viện, nên kết quả không tái lập được theo thời gian (mức: cao)
Bằng chứng E1 tại S000: `pyproject.toml` chỉ đặt sàn (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không có lockfile và không có trần. Khi cài mới, pip kéo về `numpy 2.4.6`,
`pandas 3.0.5`, `pyarrow 25.0.1` — vượt xa sàn tới hai thế hệ lớn. Toàn bộ 69 test vẫn PASS
trên bộ này, đó là tín hiệu tốt về độ bền, nhưng là **may mắn chứ không phải bảo đảm**.

Vì sao mức cao: Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu —
"cùng dataset hash + config hash + manifest hash + seed thì tái lập chính xác cùng kết quả".
Run record hiện lưu hash của config, manifest, dataset và seed, **nhưng không lưu phiên bản thư
viện**. Một thay đổi dấu phẩy động trong numpy/pandas ở phiên bản sau có thể làm official run
không tái lập được, mà không ai phát hiện — vì mọi hash đầu vào vẫn trùng khớp.

Hệ quả về thứ tự công việc: phải xử lý **trước** khi chạy official run, nếu không thì kết quả
chính thức mang khiếm khuyết không sửa được về sau. Đó là lý do T-06A được chèn vào lộ trình
và đặt làm điều kiện tiên quyết của T-06.

### RSK-007 — Pipeline không chạy nhiều hạng mục mà spec ghi là bắt buộc cho official run (mức: cao)
S001 phát hiện (E1): Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng coverage §4 và
XIRR §16 đều đã được cài đặt đúng nhưng **không nơi nào trong pipeline gọi chúng**. Hệ quả: một
official run sẽ phát ra verdict kèm báo cáo thiếu, và nguyên tắc Backtest §22 ("luật đơn giản
thắng nếu kết quả tương đương") không thể áp dụng vì không có B/C/D để so.
Ngoài ra ba Failure Signal (FS-02, FS-06, FS-12) không bao giờ được truyền input nên luôn UNKNOWN,
trong khi verdict BUILD vẫn phát ra bình thường.
Xem finding F-002, F-003, F-004, F-012, F-013.
Giảm thiểu đề xuất: R-02, R-03 — trước T-06.

### RSK-008 — Run trên dữ liệu tổng hợp vẫn được ghi nhận là official (mức: cao)
S001 xác nhận (E1): cờ `official` chỉ phụ thuộc việc có dùng `--dev-limit` hay không, hoàn toàn
không kiểm nguồn dữ liệu; và `lineage.json` ghi `source` là chuỗi cố định `'see fetch/synth'` cho
cả dữ liệu thật lẫn dữ liệu tổng hợp. Chạy `ethdca synth && ethdca run all` sẽ tạo record mang
`official: true` trên dữ liệu nhân tạo, không có trường nào cho phép phát hiện về sau.
Đây là rủi ro thẳng vào tính toàn vẹn của verdict — tức vào chính cổng mở đường cho app.
Xem finding F-005. Giảm thiểu đề xuất: R-04 — trước T-06.

### RSK-009 — Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn (mức: cao)
S001 phát hiện và kiểm chứng bằng chạy thật (E1): khi giai đoạn RECOVERY kết thúc lúc thị trường
còn yếu, regime chuyển thành STRESSED chứ không phải NORMAL, nên nhánh dọn Crash ladder ở
`engine.py:415` không bao giờ chạy. Reserve của Crash zone không được giải phóng, kéo theo không
tạo được ladder mới và cash ratio tăng giả tạo — có thể bóp méo chính FS-02 và FS-07.
Đây đồng thời là vi phạm [F1] (STRESSED phải không có hiệu ứng execution).
Xem finding F-001. Giảm thiểu đề xuất: R-01.

## Open Regression Items
- None. S001 không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với V2.1.5;
  bảy sửa đổi F1–F7 đều có dấu vết hiện thực.

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- RCP-001 — ROADMAP CHANGE PROPOSAL — 2026-08-23 — Chuyển 33 finding của S001 thành 15 work
  package có dependency graph và phân lớp A/B/C/D. **CHƯA ÁP DỤNG, chờ phê duyệt.**
  Không sửa bảng roadmap chuẩn, không sửa mã sản phẩm, không bắt đầu S002.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`.
- S001 — DISCOVERY & BASELINE (AUDIT READ-ONLY) — 2026-08-23 — Đối chiếu toàn bộ implementation
  với spec V2.1.5 theo chín nhóm A–I. Sinh Compliance Matrix, Audit Findings (33 finding: 0
  CRITICAL, 8 HIGH, 15 MEDIUM, 7 LOW, 3 spec defect; 18/33 có bằng chứng chạy thật) và Discovery
  Baseline. Không sửa một dòng mã sản phẩm nào. Kết luận: **S001 PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S001-discovery-baseline.md`.
- S000 — PROJECT OPEN — 2026-08-23 — Chọn profile PRODUCT, khởi tạo trạng thái dự án, lập kế
  hoạch khảo sát (T-01..T-03) và lộ trình sơ bộ 14 task. Không sửa một dòng code sản phẩm nào.
  Biên bản: `docs/sessions/S000-project-open.md`.

## Bằng chứng nền thu tại S000

Đây là bằng chứng **E1 — chạy thật**, khác với các quan sát đọc code (E0) đã nêu ở mục rủi ro.
T-01 vẫn phải chạy lại để xác nhận trạng thái tại thời điểm S001, nhưng không cần dò lại từ đầu.

| Hạng mục | Kết quả | Mức |
|---|---|---|
| Test suite Python | **69 passed, 0 failed, 0 skipped, 0 error** trong 372,63s | E1 |
| Môi trường | Python 3.11.15, node v22.22.2, git 2.43.0 | E1 |
| Thư viện thực cài | numpy 2.4.6, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1 | E1 |
| Mạng tới Binance/CoinGecko | Cả ba host trả 403 ở tầng proxy; PyPI thông | E1 |
| `ethdca synth` | 2,0s — 262.748 nến 15m, 3.102 nến ngày | E1 |
| `ethdca freeze` Gate 2 | 19 ứng viên OFAT → loại 1 (`base_pct=0.7`, lý do `smart_pct < 0.15`) → 18 hợp lệ; 200 interaction; **mẫu số 219** | E1 |
| `ethdca freeze` Gate 3 | 14 deterministic + 100 sampled = **114 config** | E1 |
| Parity engine JS ↔ Python | Lệch tối đa **7,39e-11** trên 40 ngày — hai bản đồng thuận | E1 |
| Bất biến kế toán ladder (một tháng) | Tổng bảo toàn 3.000.000 qua fill toàn phần → fill một phần → invalidation → release; không pool nào âm | E1 |
| Build quine của webapp | Self-check đạt, template giải mã lại được | E1 |
| CLI | 6 lệnh: `fetch`, `synth`, `freeze`, `run`, `verdict`, `export-live` | E1 |
| `results/`, `data/`, `.venv/` trong repo | Không tồn tại — xác nhận chưa từng có official run | E1 |

Điều này làm đổi đánh giá ban đầu theo hướng tốt hơn: **mã nguồn khỏe hơn tài liệu gợi ý**.
Đây không phải prototype dở dang. T-02 vì vậy nên tập trung vào **tuân thủ spec** chứ không phải
sức khỏe cơ bản của engine.

Cảnh báo quan trọng về ý nghĩa của các validator governance: chúng đang PASS trên **tập rỗng** —
0 evidence record, 0 MAJOR task file, 0 task DONE. `PROJECT STATE` chỉ vừa chuyển từ FAIL sang
PASS trong chính phiên S000 này. Khung đã có, nội dung thì chưa. Không được đọc các dòng PASS đó
như bằng chứng chất lượng dự án.

Ghi chú về con số manifest: việc `freeze` đếm ra đúng 219 và 114 chứng minh **thuật toán sinh
manifest chạy ra đúng số lượng**. Nó KHÔNG chứng minh **nội dung từng config đúng ngữ nghĩa**
spec. T-02 vẫn phải đối chiếu nội dung, không được dừng ở con số.

## Routing sơ bộ cho task chưa có file định nghĩa

Ghi lại để lộ trình có bằng chứng routing, sẽ tính lại và chốt tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

- T-00 — D3 R2 B1 A3 X3 → 2.35 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C4 F2 → 2.7 → xhigh
- T-04 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U2 V2 H3 C3 F3 → 2.60 → xhigh
- T-06A — D2 R2 B2 A1 X2 → 1.85 → B (không floor); U1 V2 H2 C2 F2 → 1.80 → high
- T-06 — D2 R3 B3 A1 X3 → 2.45 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-08 — D3 R3 B2 A3 X3 → 2.80 → C (2 floor); U3 V2 H3 C3 F3 → 2.80 → xhigh
- T-09A — D3 R3 B2 A1 X2 → 2.35 → C (floor `safety_business:min_C`); U1 V3 H2 C2 F3 → 2.25 → high
- T-09B — D3 R3 B3 A3 X3 → 3.00 → D (2 floor); U3 V3 H3 C3 F3 → 3.00 → xhigh
- T-10 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-11 — D4 R4 B3 A2 X4 → 3.50 → D (2 floor); U3 V4 H4 C4 F4 → 3.80 → max

Category `accounting_financial` được gắn cho T-06, T-08, T-09A, T-09B, T-10, T-11 vì chúng chạm
lớp tính toán dẫn tới quyết định xuống tiền thật. T-09B gắn thêm
`material_sensitive_data_corruption` vì thao tác chuyển đổi lưu trữ có thể làm hỏng sổ tài chính.

## Next Session

Recommended Session:
S001 — Discovery & Baseline, chạy ở chế độ AUDIT read-only.

Purpose:
Thực hiện T-01, T-02, T-03. Sinh Discovery Baseline và Audit Findings. Không sửa code sản phẩm.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. `docs/tasks/T-01-kiem-ke-hien-trang.md`
6. `docs/spec/00_MASTER_INDEX_V2_1_5.md` — precedence tài liệu spec
7. `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
8. `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`

Nhắc trước khi mở S001:
S001 là read-only. Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`.
Đầu ra là tài liệu khảo sát, không phải code.
