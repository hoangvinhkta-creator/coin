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
2026-08-24 — S004 mở WP-A7 (Ready Gate PASS, chuyển IN_PROGRESS)

Overall Status:
IN_PROGRESS

Current Phase:
Phase 2 — Lớp A (bắt buộc sửa trước official run). WP-A3 (mắt xích đầu đường găng) đã DONE;
WP-A4 hết bị chặn bởi WP-A3. RCP-002 đã áp dụng: thêm **WP-A7** vào lớp A (đóng F-035).

Current Task:
WP-A7 — Sửa phạm vi kế toán vốn Smart theo tháng (S004)

Current Task Mode:
MAJOR (phiên vừa hoàn tất; không task nào đang IN_PROGRESS)

Next Recommended Task:
Chủ dự án chọn một trong các task đã ở trạng thái READY: **WP-A4** (khuyến nghị — mắt xích kế
tiếp trên đường găng T-04 → WP-A3 ✅ → {WP-A4 ∥ WP-A7} → WP-A6 → GATE-A → T-06; tuần tự sau WP-A3 vì cùng
sửa `engine.py`), WP-A1, WP-A2, WP-C1 (khuyến nghị vì lý do an toàn dữ liệu thật), WP-D1, WP-D2.
KHÔNG tự mở — agent dừng sau WP-A3 theo chỉ thị của chủ dự án (S003 mục 20).

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính, **trừ một ngoại lệ có ghi nhận rõ ràng**: WP-A2 dùng Tier ghi đè thủ
công (C thay vì B do router trả) theo phê duyệt của chủ dự án — xem DEC-008 và
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`. Bằng chứng routing của từng task nằm trong
file task tương ứng dưới `docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối
tài liệu này.

Roadmap này áp dụng **RCP-001** (`PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`), được chủ dự án phê
duyệt ngày 2026-08-23 kèm bốn điều kiện — xem mục "Roadmap Change Applied" bên dưới.

**Cập nhật S002:** 15 work package không còn là roadmap sơ bộ. Mỗi gói đã có file định nghĩa task
đầy đủ dưới `docs/tasks/`, với Ready Gate, Completion Gate (REQUIRED checks + Evidence Level),
Exit Criteria và Escalation Triggers **đã đóng băng** ngày 2026-08-23. Theo
`TASK_COMPLETION_GATE_STANDARD.md` mục "After Freeze", agent **không được xoá hoặc làm yếu REQUIRED
check** để task đi qua; mọi thay đổi phải dùng khối `COMPLETION GATE CHANGE PROPOSAL`.
Bản đối chiếu độ phủ: `docs/reviews/S002-coverage-regression-check.md`.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| DONE | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| BLOCKED | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. Chuyển DONE khi WP-C1 hoàn tất và ba nghi vấn có kết luận E1 |
| DONE | T-04 | Chốt lộ trình và đóng băng tiêu chí | Soạn Ready Gate + Completion Gate cho 15 work package của RCP-001, đóng băng trước khi thực thi | C | xhigh | Sau T-01, T-02, T-03. HOÀN TẤT tại S002 — 15 file task đã đóng băng gate |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. KHÔNG nằm trên đường găng tới verdict (RCP-001) — chỉ chặn T-08 và WP-C2 |
| READY | WP-A1 | Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, đúng môi trường, và tái lập lại được | C | xhigh | Sau T-04. Song song với WP-A2, WP-A3, WP-C1. Thay thế T-06A cũ (đóng F-005, F-007, F-009, F-010, F-011) |
| READY | WP-A2 | Bật các hạng mục đã viết nhưng pipeline chưa chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có, dù code đã đúng | C | high | Sau T-04 (DONE). Song song với WP-A1, WP-A3 (đóng F-003, F-004, F-012, F-013, F-014). Tier C nay route tự nhiên sau MICRO-GOVDEF-001 (trước đó là ghi đè theo DEC-008) — xem GOVDEF-001 mục Resolution |
| DONE | WP-A3 | Sửa vòng đời trạng thái thị trường và ladder khẩn cấp | Vốn có thể bị khoá vĩnh viễn khi thị trường hồi phục một phần rồi yếu lại | D | max | Sau T-04. HOÀN TẤT tại S003 (đóng F-001, F-021, F-022, F-030; 10/10 REQUIRED PASS, E2 PASS) |
| READY | WP-A4 | Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu Binance thật có lỗ hổng; xử lý sai sẽ làm sai kết quả mô phỏng | C | xhigh | Sau WP-A3 (DONE tại S003) — READY. Song song roadmap với WP-A7, KHÔNG bị chặn bởi F-035; ba điều kiện bắt buộc ghi ở RCP-002 §Điều kiện phê duyệt (đóng F-023, F-025, F-032) |
| PLANNED | WP-A5 | Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược | Ba tín hiệu hiện không bao giờ được đo dù vẫn cho ra kết luận cuối cùng | C | xhigh | Sau WP-A2, WP-A3, **WP-A7** (vốn không bị khoá và phân phối vốn qua Smart ladder đúng thì số đo mới canonical) — đóng phần đo lường của F-002, và F-016 |
| PLANNED | WP-A6 | Chốt và kiểm chứng đúng thứ tự các bước tính toán | Thứ tự sai nghĩa là con số chính thức không đại diện đúng cho chiến lược đã đặc tả | D | max | Sau WP-A3, WP-A4, **WP-A7**. Completion Gate cuối cùng KHÔNG được chạy trước khi WP-A7 DONE (đường xử lý Smart hiện suy biến) — đóng F-018, F-019 |
| IN_PROGRESS | WP-A7 | Sửa phạm vi kế toán vốn Smart theo tháng | Vốn Smart gần như không bao giờ đi qua cơ chế ladder từ tháng thứ ba, và một chiều bắt buộc của Gate 2 bị vô hiệu | D | max | Sau WP-A3 (DONE). Song song roadmap với WP-A4 (phải tuần tự hoá merge trên `engine.py`). Chặn WP-A5, WP-A6, WP-C4, GATE-A → T-06 (đóng F-035) |
| PLANNED | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | Hai nhóm điều kiện ĐỘC LẬP, phải thoả CẢ HAI: (A) nội tại — T-05 và **GATE-A** (WP-A1…**WP-A7** đều DONE); (B) hạ tầng — BLK-001 (mạng Binance). Gỡ BLK-001 KHÔNG cho phép chạy T-06 khi GATE-A chưa PASS |
| PLANNED | WP-B1 | Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo | Không cho phép kết luận thuận lợi khi vẫn còn tín hiệu cảnh báo chưa đo được | D | max | Sau T-06. QUY TẮC BẮT BUỘC: nếu remediation của F-017 (Control F) ảnh hưởng Gate 1 → Gate 1 phải chạy lại trước khi coi kết quả hợp lệ (DEC-009) — đóng phần chính sách của F-002, F-015, F-017, F-026 |
| PLANNED | WP-B2 | Bổ sung test cho các yêu cầu đặc tả còn thiếu | Nhiều yêu cầu của BT §21 hiện không có gì kiểm chứng | C | xhigh | Sau T-06. Song song với WP-B1, WP-B3 |
| PLANNED | WP-B3 | Hoàn thiện nhật ký quyết định để truy vết được | Cần truy vết được vì sao hệ thống ra quyết định như vậy tại từng thời điểm | C | high | Sau T-06. Song song với WP-B1, WP-B2. Ngữ nghĩa `previous_state/new_state` phụ thuộc WP-C2 (đóng F-024, F-033) |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | Sau T-06 và **GATE-B** (WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE). Chặn T-11 |
| READY | WP-C1 | Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test | App đang có thể dùng để ghi tiền thật; ba nghi vấn về sai sổ vẫn chưa có kết luận | C | xhigh | Sau T-01 (đã DONE). Độc lập hoàn toàn — có thể chạy ngay, song song với toàn bộ lớp A. Gỡ BLOCKED cho T-03 khi xong (đóng V-01, V-02, V-03, F-027) |
| BLOCKED | WP-C2 | Làm rõ và đặt tên trạng thái thực thi của hệ thống | Cần biết rõ hệ thống đang ở trạng thái nào trước khi đưa vào dùng thật | C | xhigh | Sau T-05 (DEC-005 còn PENDING → BLOCKED). Cần ADR quyết định phạm vi trước khi bắt đầu (đóng F-006) |
| PLANNED | WP-C3 | Xử lý mua một phần ở tầng sản phẩm | Mua một phần là tình huống thật ngoài đời, tầng ghi sổ hiện chưa xử lý đúng | C | xhigh | Sau WP-C2 (đóng F-020) |
| PLANNED | WP-C4 | Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS) | Hai bản cài đặt có thể trôi khỏi nhau khi thêm tính năng mới vào JS | C | xhigh | Sau WP-A3, WP-A4, WP-A6, **WP-A7** (không khoá parity vào hành vi Smart capital đã xác nhận là sai). Chặn T-10, T-11 (đóng F-008) |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05 |
| PLANNED | T-09A | Sửa lỗi kế toán trong app web | Vá lỗi nếu WP-C1 xác nhận là có thật, trước khi app được dùng với tiền thật | C | high | Sau WP-C1. Nếu WP-C1 bác bỏ cả ba nghi vấn, T-09A có thể thu hẹp phạm vi hoặc CANCELLED |
| PLANNED | T-09B | Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | Sau T-04. Nên làm trước T-10 |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08, T-09B, WP-C4 |
| READY | WP-D1 | Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả | Dọn cho sạch, không ảnh hưởng gì tới kết quả hiện tại | B | medium | Không phụ thuộc, làm bất cứ lúc nào (đóng F-028, F-029, F-031, F-034) |
| READY | WP-D2 | Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn | Một số mâu thuẫn thuộc về chính bộ đặc tả, cần chủ dự án quyết định mở V2.2 | C | xhigh | Không phụ thuộc. Đầu ra là đề xuất, KHÔNG sửa V2.1.5 (đóng S-001, S-002, S-003) |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07, WP-C2, WP-C3, WP-C4, và chỉ khi verdict = BUILD |

## Roadmap Change Applied — RCP-001

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` ngày 2026-08-23 kèm bốn quyết định.
Toàn bộ bốn quyết định đã được phản ánh vào bảng roadmap chuẩn ở trên. Chi tiết đầy đủ ghi ở
`PROJECT/PROJECT_DECISIONS.md` DEC-007, DEC-008, DEC-009.

1. **Cấu trúc 15 work package** — APPROVED nguyên trạng.
2. **Phân lớp A/B/C/D** — APPROVED WITH CONDITION: nếu remediation của F-017 (nằm trong WP-B1)
   ảnh hưởng tới input/calculation/execution behavior/dataset interpretation/strategy behavior/
   backtest behavior có khả năng tác động Gate 1, thì **mọi kết quả Gate 1 tạo trước đó bị coi
   là STALE/INVALIDATED và Gate 1 phải chạy lại** trước khi dùng cho verdict. Điều kiện này được
   ghi trực tiếp vào dependency column của WP-B1 ở bảng trên, và thành quy tắc chính thức ở
   DEC-009.
3. **Bỏ T-06A** — APPROVED. Toàn bộ phạm vi của T-06A được hấp thụ vào WP-A1, không mất
   requirement nào. WP-A1 vẫn là điều kiện bắt buộc trước T-06.
4. **WP-A2 routing** — OVERRIDE ROUTER. Tier C/Opus (không dùng B/Sonnet mà router trả), effort
   giữ nguyên `high` (giá trị router tính đúng, không bị ảnh hưởng bởi việc override Tier).
   Ghi tại DEC-008.

### Governance defect mới phát hiện trong quá trình duyệt

`routing_engine.py` dùng so sánh dấu phẩy động không có epsilon tại các mốc biên nguyên
(0/1/2/3). Với WP-A2, `model_score` hiển thị đúng `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, khiến `tier_from_score` (so sánh `s < 2`) trả về Tier B thay vì Tier C như
bảng `AGENT_CAPABILITY_MATRIX.md` quy định cho khoảng 2.00–2.99.

Đây là **defect của công cụ governance dùng chung, không phải finding của sản phẩm ETH DCA**.
Theo yêu cầu của chủ dự án, defect này được xử lý bằng ba artifact riêng, tách khỏi 33 finding
của S001:

- **Artifact:** `docs/reviews/GOVDEF-001-routing-engine-boundary.md`
- **Task:** `MICRO-GOVDEF-001` — xem mục "Micro Tasks (Inline)" bên dưới
- **Risk:** `GOV-RSK-001` — xem mục "Active Risks — Governance / Tooling" bên dưới

Không sửa `routing_engine.py` trong bước áp dụng roadmap này. Giải pháp sau này phải tổng quát
hoá cách so sánh (dùng epsilon hoặc làm tròn trước khi so sánh), không hard-code ngoại lệ riêng
cho WP-A2 hay bất kỳ task nào khác.

## Roadmap Change Applied — RCP-002

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG (2026-08-24)

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md` kèm điều kiện bổ sung. Nguồn:
triage `docs/reviews/PH-03-triage-smart-unlock-scope.md` (PH-03 = **DEFECT** → **F-035**, HIGH).
Roadmap chuẩn tăng từ **28 → 29 task**.

Nội dung đã áp dụng:

1. **Thêm WP-A7** — "Sửa phạm vi kế toán vốn Smart theo tháng", lớp **A — MUST FIX BEFORE
   OFFICIAL RUN**, sở hữu **F-035**. Status `PLANNED` (chưa có file định nghĩa/gate → chưa
   READY). Routing xác nhận lại bằng `routing_engine.py` tại thời điểm áp dụng: **D / Fable / max**.
2. **Dependency bắt buộc mới** — WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**.
3. **WP-A6** — Completion Gate cuối cùng **không được chạy** trước khi WP-A7 DONE; không được
   dùng test fixture suy biến hiện tại để né dependency này.
4. **WP-A5** — measurement tạo trước khi F-035 được sửa **không** được coi là canonical evidence
   cho engine cuối cùng.
5. **WP-C4** — không đóng băng parity JS/Python trên hành vi Smart capital đã xác nhận là sai.
6. **GATE-A** — định nghĩa lại thành `WP-A1…WP-A7 đều DONE`.
7. **T-06** — ghi rõ **hai nhóm prerequisite ĐỘC LẬP**: (A) nội tại = GATE-A gồm WP-A7;
   (B) hạ tầng = BLK-001. Gỡ BLK-001 **không** cho phép chạy T-06 khi GATE-A chưa PASS.
8. **WP-A4** — `MAY PROCEED IN PARALLEL` với WP-A7 về mặt semantic dependency, kèm ba điều kiện
   (xem RCP-002). "Parallel" ở đây là **roadmap parallelism**: không cho phép hai agent đồng thời
   sửa/merge cùng vùng `engine.py` mà không có branch isolation và merge ordering rõ ràng.
9. **WP-A3 giữ nguyên DONE** — không reopen, không sửa Completion Gate đã FROZEN, không làm mất
   evidence E1/E2. Ghi nhận: F-035 tồn tại **trước** WP-A3 và làm giảm **độ lớn** của một số quan
   sát liên quan Smart, nhưng **không invalidate** các kết luận đúng đắn mà WP-A3 đã chứng minh
   trong phạm vi của nó.

### Gate staleness (DEC-009 áp cho F-035)

F-035 có khả năng thay đổi capital allocation, Smart ladder creation, execution behavior,
deployed capital, ETH accumulated và kết quả Gate 1/2/3. Vì vậy **mọi Gate result tạo trước
remediation F-035 phải được coi là STALE / INVALIDATED khi dùng cho verdict**.

Trạng thái hiện tại: **NO CURRENT OFFICIAL RESULT TO INVALIDATE** — chưa từng có official run.
Điều kiện vì thế chuyển thành dependency bắt buộc: **WP-A7 phải DONE trước T-06**.

### Critical path sau RCP-002

```
T-04 ✅
 └─> WP-A3 ✅
      ├─> WP-A4  ─┐   (song song roadmap; tuần tự hoá merge trên engine.py)
      └─> WP-A7  ─┤
                  └─> WP-A6 ──> GATE-A ──> T-06 ──> WP-B1 ──> T-07 ──> T-11
WP-A5: sau WP-A2 ∧ WP-A3 ∧ WP-A7 — vẫn là prerequisite của GATE-A
WP-A1, WP-A2: prerequisite của GATE-A, không nằm trên chuỗi dài nhất
GATE-A = WP-A1 ∧ WP-A2 ∧ WP-A3 ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 đều DONE
T-06 = GATE-A ∧ T-05 ∧ (BLK-001 đã gỡ)
```

## Current Task Snapshot

Task:
WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp (S003)

Task Mode:
MAJOR

Status:
DONE — 10/10 REQUIRED PASS (E1 toàn bộ; E2 cho CHECK-A3-10 với kết luận reviewer độc lập
**E2 PASS**); Exit Criteria 7/7.

File định nghĩa:
`docs/tasks/WP-A3-regime-va-vong-doi-ladder.md`

Required Gate Progress:
10 / 10 PASS. Chi tiết evidence trong file task và biên bản
`docs/sessions/S003-wp-a3-regime-ladder.md`; bản E2: `docs/reviews/E2-WP-A3-regime-ladder.md`.

Kết quả chính của S003:
- Baseline E1 tái hiện đủ F-001, F-021, F-022, F-030 ở tầng engine/regime TRƯỚC khi sửa.
- Regression test viết TRƯỚC fix: 12 FAIL đúng kỳ vọng → sau fix 18/18 PASS.
- Toàn bộ suite: **87 passed, 0 failed, 0 skipped** — không test cũ nào bị sửa/nới lỏng.
- Impact BEFORE/AFTER trên cùng dataset synth: mọi sai lệch truy về [F5] ST §14 và ST §18.3+[F1];
  công cụ đo commit tại `tests/wp_a3_impact_tool.py`, tái lập HOÀN TOÀN.
- E2 độc lập PASS; 2 finding hạ tầng test của reviewer (F-E2-01/F-E2-02) đã xử lý ngay trong
  phiên; 4 kịch bản khoá vốn reviewer tự thử: không đường khoá vốn mới.
- Phát hiện mới ngoài scope: **PH-03** → RSK-010. **Đã triage 2026-08-24: DEFECT, cấp F-035
  (HIGH); RCP-002 đã được phê duyệt và áp dụng — ownership là WP-A7 mới.** Không sửa trong WP-A3
  — đúng Scope Lock. WP-A3 giữ nguyên DONE, gate FROZEN, evidence E1/E2 nguyên vẹn.

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.5 (D4 R4 B3 A3 X3) → floors `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`, `safety_business:min_C` → D

Effort Routing Score:
3.65 (U3 V4 H4 C3 F4) → floor `safety_business:min_high` → max

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Escalation Triggers:
- Theo file task WP-A3 (CAPABILITY_CEILING / CONFLICT DETECTED / metric đổi không giải thích
  được / phải chạm capital.py|score.py). Không trigger nào kích hoạt trong S003: một phương án
  thiết kế duy nhất (tách state/label) đạt đồng thời [F1] và vòng đời đóng; mọi sai lệch metric
  giải thích được; không chạm capital.py/score.py.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

### MICRO-GOVDEF-001 — Sửa lỗi so sánh boundary trong routing_engine.py
Status:
DONE

Checklist Reference:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Mô tả ngắn:
`tier_from_score`/`effort_from_score` trong `governance/scripts/governance/routing_engine.py`
dùng so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn, nên một điểm số ở đúng biên
nguyên (ví dụ 2.0) có thể bị tính sai một bậc Tier/Effort do sai số biểu diễn nhị phân
(`1.9999999999999998` thay vì `2.0`). Chi tiết đầy đủ, bằng chứng tái lập:
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`.

Phạm vi được làm rõ tại T-04 (S002), theo đúng câu đã có sẵn trong DEC-008 mục Impact
("`validate_routing.py` cần được cập nhật ở một task riêng — MICRO-GOVDEF-001 hoặc kế tiếp"):
task này bao gồm **cả** `validate_routing.py`, để công cụ chấp nhận một manual override **có ghi
nhận** (kèm `Manual Override` và `Router Raw Output` trong file task) thay vì báo lỗi khớp tuyệt
đối. Đây là làm rõ phạm vi đã được DEC-008 dự liệu, không phải quyết định mới. Việc mở task này
vẫn cần chỉ thị của chủ dự án — xem BLK-003 và DEC-010.

Ràng buộc bắt buộc khi sửa: tổng quát hoá cách so sánh (làm tròn trước khi so sánh, hoặc dùng
epsilon nhất quán với `EPS` đã dùng ở nơi khác trong codebase, ví dụ `capital.py`).
**Không hard-code ngoại lệ riêng cho bất kỳ task nào** (kể cả WP-A2, task đã kích hoạt phát hiện
này).

Đánh giá MICRO eligibility (`TASK_MODE_STANDARD.md`): Difficulty <= 2, Risk <= 2, Blast Radius
<= 2 — không đổi kiến trúc, không đổi auth, không migration, không thao tác phá huỷ dữ liệu.
Đủ điều kiện MICRO. Chấm điểm tham khảo (không bắt buộc với MICRO): D1 R2 B2 A1 X1 → 1.45 → B;
U1 V2 H1 C1 F2 → 1.45 → medium.

Evidence Summary (2026-08-23, chủ dự án phê duyệt PA-1 cho DEC-010):

**Compact Ready Gate** (`MICRO_TASK_CHECKLIST.md`) — đủ điều kiện, xác nhận lại khi mở: yêu cầu rõ
ràng (sửa boundary comparison + validator override); Risk 2 <= 2; Blast Radius 2 <= 2; không đổi
kiến trúc/auth/schema/thao tác phá huỷ; phạm vi hẹp và đã biết (`routing_engine.py`,
`validate_routing.py`, test governance mới); phương pháp kiểm chứng đã biết (brute-force toàn không
gian đầu vào + test override tổng hợp).

**Compact Completion Gate:**
- [x] Hành vi dự định đã cài đặt — `routing_engine.py` làm tròn `model_score`/`effort_score` về 3
  chữ số **trước khi** so sánh biên (căn cứ: trọng số chỉ có tối đa 2 chữ số thập phân, nên làm
  tròn 3 chữ số loại bỏ đúng nhiễu IEEE-754 ~1e-15, không đổi giá trị thật) — không phải epsilon
  tuỳ tiện, không hard-code WP-A2 hay bất kỳ task nào.
- [x] `validate_routing.py` chấp nhận manual override có ghi nhận (decision reference tồn tại
  trong `PROJECT_DECISIONS.md`, `Router Raw Output` xác thực khớp router hiện tại, chỉ được leo
  thang Tier/Effort chứ không hạ) — hàm `check_override`, tổng quát cho mọi `DEC-###`.
- [x] Verification thực sự chạy: brute-force toàn bộ 5^5 × 5^5 tổ hợp đầu vào cho **0** lệch còn
  lại; `governance/scripts/governance/test_routing_engine.py` — **37/37 check PASS**, gồm 6 ca
  override hợp lệ/không hợp lệ tổng hợp (không phụ thuộc WP-A2).
- [x] Evidence ghi theo `EVIDENCE_STANDARD.md`, mức E1 (chạy thật): xem
  `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- [x] Không mở rộng phạm vi ngoài dự kiến — `git diff` xác nhận chỉ chạm
  `governance/scripts/governance/routing_engine.py`, `validate_routing.py` (thêm), file task
  `WP-A2` (chỉ bổ sung ghi chú, không xoá dấu vết), và các artifact governance liên quan. Không
  chạm `src/`, `webapp/`, `tests/`, `docs/spec/`.
- [x] Regression liên quan đã PASS: `routing_engine.py`/`validate_routing.py` chạy lại trên toàn bộ
  16 file MAJOR task hiện có — **đúng một dòng đổi** (WP-A2, Tier B → C), không task nào khác đổi
  Tier/Effort. `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
  override(s))`.
- [x] `PROJECT/PROJECT_PROGRESS.md` inline Micro Task entry được cập nhật — mục này.

**Kết quả:** BLK-003 RESOLVED. GOV-RSK-001 CLOSED. WP-A2 chuyển `BLOCKED` → `READY`, giữ nguyên
Tier C / Opus / Effort high (nay route tự nhiên, không cần override — nhưng dấu vết DEC-008/Manual
Override/Router Raw Output trong file WP-A2 được **giữ nguyên**, không xoá).

Chi tiết đầy đủ: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
Test: `governance/scripts/governance/test_routing_engine.py`.

## Active Blockers

### BLK-001 — Không có đường tới dữ liệu Binance từ môi trường phát triển
Ảnh hưởng: **chỉ T-06** (RCP-001 xác định lại: không work package nào trong 15 gói lớp A/B/C/D
cần dữ liệu Binance thật — toàn bộ phát triển và kiểm chứng được trên dữ liệu tổng hợp theo
DEC-003). T-06 là điểm duy nhất trên đường găng cần blocker này được gỡ; T-07 và T-11 chỉ bị
chặn gián tiếp qua chuỗi phụ thuộc vào T-06, không phải trực tiếp bởi BLK-001.

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

Không bypass BLK-001. Không đổi nguồn dữ liệu. Không dùng dữ liệu tổng hợp để tạo official
verdict.

### BLK-003 — RESOLVED (`validate_routing.py` chưa biểu diễn được manual override đã được phê duyệt)
Trạng thái: **RESOLVED — 2026-08-23, tại MICRO-GOVDEF-001.**
Ảnh hưởng khi còn mở: **chỉ WP-A2**.

Mô tả: `governance/scripts/governance/validate_routing.py` so khớp **tuyệt đối** giữa
`Primary Agent Tier` trong file task và kết quả của `routing_engine.py`. Khi T-04 soạn file định
nghĩa cho WP-A2 với Tier C theo DEC-008, validator báo:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây **không phải defect mới**. DEC-008 mục Impact đã ghi trước rằng tình huống này sẽ xảy ra và
rằng `validate_routing.py` "cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để
chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối". T-04 làm đúng phần được giao và
không làm phần được giao cho task khác.

Vì sao nó chặn WP-A2: `CLAUDE.md` mục "Every Implementation Session" điểm 9 yêu cầu
`validate_routing.py` **PASS trước khi thực thi** một MAJOR task; `ROADMAP_SYNC_STANDARD.md` cũng
yêu cầu chạy validator này trước roadmap sync. Vì vậy WP-A2 giữ trạng thái `BLOCKED` cho tới khi
điều kiện được gỡ.

Đường gỡ (cần chủ dự án quyết định — xem DEC-010):
1. Cho phép mở `MICRO-GOVDEF-001` (đã mở rộng phạm vi để phủ cả `validate_routing.py`), hoặc
2. Miễn trừ bằng văn bản, ghi vào `PROJECT/PROJECT_DECISIONS.md`.

**Không được gỡ bằng cách hạ Tier WP-A2 về B** — DEC-008 cấm, và làm vậy là hạ tiêu chuẩn để
validator xanh.

Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-02.

**Cách đã gỡ (2026-08-23):** chủ dự án phê duyệt **PA-1**. `routing_engine.py` được sửa tổng quát
(làm tròn điểm số về cùng độ chính xác hiển thị trước khi so sánh biên); `validate_routing.py` được
bổ sung cơ chế chấp nhận manual override có ghi nhận. Sau fix, `validate_routing.py` PASS cho toàn
bộ 16 file MAJOR task, và WP-A2 route Tier C **tự nhiên** (không cần nhánh override nữa, dù nhánh đó
đã được xây và kiểm chứng độc lập cho các trường hợp tương lai). Không hạ Tier WP-A2 về B.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution";
`MICRO-GOVDEF-001` ở mục "Micro Tasks (Inline)".

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
Giảm thiểu: **WP-C4** (RCP-001) — mở rộng phạm vi parity trước khi port thêm.

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

Còn lại phải xác minh ở **WP-C1** (RCP-001) bằng ca kiểm thử **đa tháng** cho (a), và ca kiểm
thử riêng cho (b), (c). Sửa (nếu xác nhận): T-09A.

### RSK-004 — Bộ test app web không chạy được từ bản checkout sạch (mức: trung bình) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: hai test webapp **chạy được và cho kết quả đúng**, nhưng chỉ sau khi
dựng thủ công hai thứ không có trong repo — `webapp/app_final.html` (phải build) và
`demo/results3/live_seed.json` (**không tồn tại ở bất kỳ đâu trong repo**).
Nghĩa là không ai clone repo về mà chạy được test của app, và không có gì bảo vệ hồi quy tự động.

Ghi nhận thêm: hai test ghi ảnh chụp màn hình vào thư mục làm việc hiện hành. Nếu chạy từ trong
`webapp/` sẽ để lại `app-dash.png` và `app-zone.png` trong repo, mà hai file này không nằm trong
`.gitignore`.

Giảm thiểu: **WP-C1** (RCP-001) khôi phục harness trước khi định lượng mức bảo vệ hồi quy thật.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình) — S001 XÁC NHẬN VÀ MỞ RỘNG (E1)
S001 xác nhận và phát hiện quy ước không được ghi ở nhiều chỗ hơn dự kiến: ngoài ánh xạ
gate-fail → verdict, còn có ngưỡng số tự đặt của FS-02/FS-07/FS-12, phạm vi tính FS-03/FS-07 chỉ
trên window W5, và tham số `shift_days=10` của Control G. `verdict.py` còn ghi rằng ánh xạ được
tài liệu hoá ở `docs/CONVENTIONS.md`, nhưng file đó không có mục nào về verdict.
Xem finding F-015, F-016, F-026. Giảm thiểu: **WP-B1** (RCP-001).

`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ để không bị coi nhầm là điều
khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

### RSK-006 — Không ghim phiên bản thư viện, nên kết quả không tái lập được theo thời gian (mức: cao) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: `pyproject.toml` chỉ đặt sàn (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không có lockfile và không có trần. Khi cài mới, pip kéo về `numpy 2.4.6`,
`pandas 3.0.5`, `pyarrow 25.0.1` — vượt xa sàn tới hai thế hệ lớn. Toàn bộ 69 test vẫn PASS
trên bộ này, đó là tín hiệu tốt về độ bền, nhưng là **may mắn chứ không phải bảo đảm**.

Vì sao mức cao: Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu —
"cùng dataset hash + config hash + manifest hash + seed thì tái lập chính xác cùng kết quả".
Run record hiện lưu hash của config, manifest, dataset và seed, **nhưng không lưu phiên bản thư
viện**. Một thay đổi dấu phẩy động trong numpy/pandas ở phiên bản sau có thể làm official run
không tái lập được, mà không ai phát hiện — vì mọi hash đầu vào vẫn trùng khớp.

Giảm thiểu: **WP-A1** (RCP-001) — thay thế T-06A, đóng đủ cả 8 trường provenance yêu cầu
(Python version, dependency/lock hash, git commit SHA, dataset hash, strategy config hash,
execution config hash, manifest hash, seed), không chỉ ghim thư viện.

### RSK-007 — Pipeline không chạy nhiều hạng mục mà spec ghi là bắt buộc cho official run (mức: cao) — S001 XÁC NHẬN (E1)
S001 phát hiện (E1): Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng coverage §4 và
XIRR §16 đều đã được cài đặt đúng nhưng **không nơi nào trong pipeline gọi chúng**. Hệ quả: một
official run sẽ phát ra verdict kèm báo cáo thiếu, và nguyên tắc Backtest §22 ("luật đơn giản
thắng nếu kết quả tương đương") không thể áp dụng vì không có B/C/D để so.
Ngoài ra ba Failure Signal (FS-02, FS-06, FS-12) không bao giờ được truyền input nên luôn UNKNOWN,
trong khi verdict BUILD vẫn phát ra bình thường.
Xem finding F-002, F-003, F-004, F-012, F-013. Giảm thiểu: **WP-A2, WP-A5** (RCP-001).

### RSK-008 — Run trên dữ liệu tổng hợp vẫn được ghi nhận là official (mức: cao) — S001 XÁC NHẬN (E1)
S001 xác nhận (E1): cờ `official` chỉ phụ thuộc việc có dùng `--dev-limit` hay không, hoàn toàn
không kiểm nguồn dữ liệu; và `lineage.json` ghi `source` là chuỗi cố định `'see fetch/synth'` cho
cả dữ liệu thật lẫn dữ liệu tổng hợp. Chạy `ethdca synth && ethdca run all` sẽ tạo record mang
`official: true` trên dữ liệu nhân tạo, không có trường nào cho phép phát hiện về sau.
Đây là rủi ro thẳng vào tính toàn vẹn của verdict — tức vào chính cổng mở đường cho app.
Xem finding F-005. Giảm thiểu: **WP-A1** (RCP-001).

### RSK-009 — Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn (mức: cao) — ĐÃ REMEDIATE tại S003 (WP-A3)
S001 phát hiện và kiểm chứng bằng chạy thật (E1): khi giai đoạn RECOVERY kết thúc lúc thị trường
còn yếu, regime chuyển thành STRESSED chứ không phải NORMAL, nên nhánh dọn Crash ladder ở
`engine.py:415` không bao giờ chạy. Reserve của Crash zone không được giải phóng, kéo theo không
tạo được ladder mới và cash ratio tăng giả tạo — có thể bóp méo chính FS-02 và FS-07.
Đây đồng thời là vi phạm [F1] (STRESSED phải không có hiệu ứng execution).
Xem finding F-001. Giảm thiểu: **WP-A3** (RCP-001).

**Cập nhật S003 (2026-08-23): CLOSED.** WP-A3 (DONE) đã tách trạng thái nền khỏi nhãn STRESSED
(`RegimeTracker.state`/`.label`, CONVENTIONS #14) và nhánh dọn chạy cho MỌI kết cục kết thúc
Recovery; bằng chứng E1: baseline tái hiện lock 27.2 đơn vị trước fix → 0 sau fix, chuỗi test
CHECK-A3-01/02, suite 87 PASS; E2 độc lập PASS — reviewer tự dựng kịch bản khác (kẹt 18.7 trên
code cũ, release đủ trên code mới) và không tìm thấy đường khoá vốn mới sau 4 kịch bản tự nghĩ.

### RSK-010 — Phạm vi kế toán của Smart unlock sai: Smart ladder ngừng hình thành từ tháng thứ ba (mức: cao) — **XÁC NHẬN LÀ DEFECT → F-035**
Trạng thái: **CONFIRMED DEFECT** (nâng cấp từ "nghi vấn" tại phiên triage PH-03, 2026-08-24).
Finding chính thức: **F-035** · Severity **HIGH** · Evidence **E1** (chứng minh cấu trúc + chạy
thật), có xác nhận độc lập kế thừa từ reviewer E2-WP-A3-001.

`smart_reservable` so ngân sách Smart **theo tháng** với `pool.deployed` **luỹ kế toàn đời**
(`Pool` không có vòng đời tháng, trong khi Data Model §5 `monthly_budgets` định nghĩa
`smart_available/reserved/deployed_vnd` là trường của bản ghi **tháng** có `status OPEN/CLOSED`).
Vì Month-End (ST §10) giải ngân hết phần Smart mỗi tháng, `deployed` tăng ~một ngân sách tháng
mỗi tháng ⇒ từ tháng thứ ba hàm trả **0 tất định, vĩnh viễn, không phụ thuộc dữ liệu**, kể cả ở
`SMART_UNLOCK = 1.00`.

Hệ quả đo được (90 tháng dữ liệu tổng hợp): **2** Smart ladder; **99,98%** vốn Smart bỏ qua cơ
chế ladder (ST §12) và chảy qua luật phần dư cuối tháng; **chiều `smart_unlock_mode` — 1 trong 8
chiều bắt buộc của Gate 2 (BT §9) — trơ hoàn toàn**, ba mode HWM/NO_HWM/DECAY_HWM cho kết quả
**trùng khít bit-for-bit** trong khi ST §6 yêu cầu báo cáo đóng góp riêng từng mode; snapshot
[F5] của Crash ladder bị triệt tiêu phần Smart (che ~78% tác dụng thật của remediation F-021 vừa
xong ở WP-A3).

**Official backtest KHÔNG đáng tin trước khi sửa** (Gate 1/2/3 đều đo trên engine mà 30% vốn
không đi qua cơ chế được đặc tả). Áp dụng **DEC-009**: mọi kết quả Gate 1 tạo trước remediation
là STALE/INVALIDATED — hiện `no current result to invalidate` (chưa từng có official run), nên
điều kiện chuyển thành dependency bắt buộc: **phải DONE trước T-06**.

Tồn tại **trước** WP-A3, **không phải hồi quy** của WP-A3; WP-A3 giữ nguyên DONE và gate FROZEN.
Ownership: **WP-A7** (lớp A, đường găng, D/Fable/max) — **ĐÃ CHỐT**: RCP-002 được chủ dự án phê
duyệt kèm điều kiện và **đã áp dụng** vào bảng roadmap chuẩn ngày 2026-08-24. WP-A7 là
prerequisite của WP-A5, WP-A6, WP-C4, GATE-A, T-06.
Trạng thái risk: **CONFIRMED DEFECT — OPEN**, sẽ đóng khi WP-A7 DONE.

Triage đầy đủ (requirement canonical, root cause, bằng chứng, phân lớp, ảnh hưởng gate, đánh giá
WP-A4): `docs/reviews/PH-03-triage-smart-unlock-scope.md`.

### PH-04 — Ba mode `smart_unlock` phân kỳ ở tầng quyền vốn nhưng vẫn trùng kết quả cuối trên full run (GHI NHẬN S004 — chờ chủ dự án, CHƯA triage, KHÔNG remediation)

Phát hiện trong S004 (WP-A7), **ngoài Scope Lock**, ghi nhận theo đúng quy trình
"phát hiện mới không sửa trong phiên":

Sau khi F-035 được sửa, ba mode HWM / NO_HWM / DECAY_HWM đã **phân kỳ thật** ở tầng
unlock path và quyền vốn (`smart_reservable` cuối kịch bản tất định: 14.36 / 11.36 / 0.00
— test C của WP-A7), tức chiều ablation không còn chết cơ học theo đúng câu chữ
CHECK-A7-03. Tuy nhiên trên **full synthetic run 90 tháng**, ba mode vẫn cho `eth_total`
trùng **bit-for-bit** (21.637034604792). Nguyên nhân cấu trúc (E1, đã xác minh bằng probe):
engine hiện chỉ **tiêu thụ** `effective_unlock` tại đúng hai điểm — (a) tạo Smart ladder
one-shot ở lần eff > 0 đầu tiên trong tháng, nơi peak == current nên ba mode cho cùng giá
trị (CONVENTIONS #1); (b) crash snapshot [F5], nơi OSCORE ≥ 75 ⇒ smart_unlock = 1.0 ở mọi
mode. ST §6 yêu cầu ba mode nằm trong Gate-2 ablation với "báo cáo đóng góp riêng" (BT §9)
— muốn chiều này phân biệt được ở tầng OUTCOME cần một kênh tiêu thụ unlock **liên tục
trong tháng** (ví dụ top-up/resize ladder khi eff tăng), là thay đổi hành vi engine nằm
ngoài phạm vi WP-A7 (phạm vi kế toán) và không được đặc tả tường minh trong V2.1.5.

Phương án thuộc thẩm quyền chủ dự án: (1) mở WP mới trong lớp A/B; (2) chuyển WP-D2 đề
xuất V2.2; (3) chấp nhận như giới hạn đã biết của Gate-2 ablation dimension này. Chi tiết:
`docs/sessions/S004-wp-a7-monthly-smart-scope.md` mục "PH-04".

## Active Risks — Governance / Tooling

Rủi ro của bản thân bộ công cụ governance dùng chung, **tách khỏi rủi ro sản phẩm ETH DCA** ở
mục trên. Không tính vào 33 finding của S001.

### GOV-RSK-001 — Sai số biên dấu phẩy động trong routing_engine.py có thể under-route task đúng biên (mức: trung bình) — CLOSED
Phát hiện khi áp dụng RCP-001 (2026-08-23), tái lập được (E1): `tier_from_score` và
`effort_from_score` so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn/chưa có
epsilon. Một task có điểm nền đúng bằng 2.0 (biên Tier B/C) có thể nhận `model_score` nội bộ là
`1.9999999999999998` do cách `0.25*D+0.25*R+0.20*B+0.15*A+0.15*X` cộng dồn sai số nhị phân, và
bị route xuống Tier B thay vì Tier C.

Trường hợp cụ thể đã xác nhận: WP-A2 (D2 R2 B2 A1 X3) — hiển thị `model_score: 2.0` nhưng nội bộ
`1.9999999999999998`, router trả Tier B trong khi bảng `AGENT_CAPABILITY_MATRIX.md` quy định
2.00–2.99 → Tier C.

Ảnh hưởng: bất kỳ task nào (không riêng dự án này) có điểm nền rơi đúng vào các mốc nguyên
0/1/2/3 đều có nguy cơ tương tự, theo cả hai chiều (có thể over-route hoặc under-route tuỳ dấu
sai số). Mức trung bình vì hệ quả là chọn sai một bậc Tier/Effort, không phải sai kết quả tính
toán nghiệp vụ.

Giảm thiểu tạm thời đã áp dụng cho WP-A2: **manual override** theo DEC-008, ghi nhận công khai
trong bảng roadmap.
Giảm thiểu triệt để: **MICRO-GOVDEF-001** — **HOÀN TẤT 2026-08-23**. `routing_engine.py` làm tròn
điểm số về cùng độ chính xác hiển thị trước khi so sánh biên; xác nhận bằng quét toàn bộ 5^5 × 5^5
tổ hợp đầu vào cho 0 lệch còn lại (`test_routing_engine.py`, 37/37 PASS). WP-A2 nay route Tier C tự
nhiên, không cần override. Không task nào khác trong 16 file MAJOR hiện có bị ảnh hưởng.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".

## Open Regression Items
- None ở tầng mã nguồn. S001 không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với
  V2.1.5; bảy sửa đổi F1–F7 đều có dấu vết hiện thực.
- **PH-01 (tài liệu, không phải mã nguồn)** — bảng "Tổng hợp" của `docs/reviews/S001-audit-findings.md`
  ghi MEDIUM 15 và Tổng 33, nhưng đếm thật trên chính danh mục được liệt kê cho **34 định danh
  `F-xxx`** (HIGH 8 + MEDIUM 19 + LOW 7) cộng 3 `S-xxx`. Con số 33 đã được chép sang tài liệu này và
  sang RCP-001. **Không finding nào bị rơi** — RCP-001 §2 và §6 phân đủ 34 `F-xxx` vào 15 gói, và
  T-04 xác nhận 40/40 định danh có nơi thuộc về. T-04 **không tự sửa** con số trong biên bản audit
  của phiên đã đóng; chờ chủ dự án quyết định cách đính chính.
  Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-01.

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)
- DEC-006 — Source of Truth cho compliance audit là V2.1.5, không phải V2.1.3
- DEC-007 — RCP-001 được phê duyệt và áp dụng kèm bốn điều kiện
- DEC-008 — Ghi đè thủ công routing của WP-A2 (Tier C, không dùng Tier B từ router)
- DEC-009 — Quy tắc Gate 1 staleness: remediation ảnh hưởng Gate 1 bắt buộc chạy lại Gate 1
- DEC-010 — RESOLVED: PA-1 phê duyệt cho BLK-003; `routing_engine.py`/`validate_routing.py` đã sửa

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- WP-A7 — TASK DEFINITION & GATE FREEZE — 2026-08-24 — Soạn và **đóng băng** task definition cho
  WP-A7 theo `TASK_DEFINITION_TEMPLATE.md`: `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md`.
  **20 mục Ready Gate** (19 đã xác nhận, 1 để xác nhận lại khi mở task) và **12 REQUIRED
  Completion check** — E1 toàn bộ, **E2 bắt buộc** cho CHECK-A7-12 (Risk 4 + `accounting_financial`).
  Kiểm precedence Master Index §2 trên bốn tầng tài liệu: **không phát hiện CONFLICT** — BT §19
  (precedence 1) bước 3/4/6 nói "đóng sổ cuối tháng", "reset trạng thái Smart HWM/mode", "overflow
  sang **Smart của tháng đó**", cùng hướng với DM §5 (`monthly_budgets` keyed by `month_local`) và
  ST §4/§6/§10/§12; DM §6 (`capital_ledger` append-only, audit) là căn cứ bắt buộc **giữ lịch sử
  toàn đời** song song với trạng thái theo tháng. Root cause được giữ nguyên văn (tử số theo tháng
  trừ `pool.deployed` cumulative lifetime), kèm lệnh cấm diễn giải lại finding thành "cần tăng số
  ladder". Routing xác nhận lại bằng router: **D / Fable / max**; `validate_routing.py` PASS trên
  **17** MAJOR task file. Coverage regression: 22/22 requirement của RCP-002 có mặt trong gate,
  không dependency nào bị làm yếu (A7 → A5/A6/C4/GATE-A/T-06 giữ nguyên). **WP-A7: PLANNED →
  READY.** Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`; không remediation F-035; không bắt
  đầu WP nào.
- RCP-002 — ROADMAP CHANGE APPLIED — 2026-08-24 — Chủ dự án phê duyệt RCP-002 kèm điều kiện bổ
  sung. Áp dụng vào bảng roadmap chuẩn: **28 → 29 task**. Thêm **WP-A7** ("Sửa phạm vi kế toán vốn
  Smart theo tháng", lớp A, sở hữu **F-035**, status `PLANNED`, routing **D/Fable/max** xác nhận
  lại bằng `routing_engine.py` tại thời điểm áp dụng: model_score 3.25, effort_score 3.45,
  floors `cognitive:A>=3&X>=3` + `safety_business:min_C` + `safety_business:min_high`). Dependency
  bắt buộc: WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**; WP-A6 không được chạy
  Completion Gate cuối trước khi WP-A7 DONE; WP-A5 measurement trước F-035 không phải canonical
  evidence; WP-C4 không đóng băng parity trên hành vi Smart capital sai. **GATE-A** định nghĩa lại
  = WP-A1…WP-A7 đều DONE. **T-06** ghi rõ hai nhóm prerequisite độc lập (nội tại GATE-A / hạ tầng
  BLK-001) — gỡ BLK-001 không cho phép chạy T-06 khi GATE-A chưa PASS. **WP-A4** giữ READY, song
  song roadmap với WP-A7 kèm ba điều kiện. **WP-A3 giữ nguyên DONE**, không reopen, gate FROZEN,
  evidence E1/E2 nguyên vẹn. DEC-009 áp cho F-035: mọi Gate result trước remediation là
  STALE/INVALIDATED — hiện **NO CURRENT OFFICIAL RESULT TO INVALIDATE**, chuyển thành dependency
  WP-A7 DONE trước T-06. Toàn bộ 35 finding, 11 risk, 3 blocker được bảo toàn. Không sửa `src/`,
  `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, đặc biệt không bắt đầu WP-A7.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`,
  `docs/reviews/PH-03-triage-smart-unlock-scope.md`.
- S003-TRIAGE — PH-03 / RSK-010 — 2026-08-24 — Triage governance + kỹ thuật, **không remediation**.
  Kết luận: PH-03 = **DEFECT**, cấp finding chính thức **F-035** (HIGH, E1). Requirement canonical
  bị vi phạm: **DM §5** (`monthly_budgets` định nghĩa `smart_deployed_vnd` là trường của bản ghi
  THÁNG), củng cố bởi ST §4/§6/§12 và ST §10. Root cause: `smart_reservable` trừ `pool.deployed`
  luỹ kế toàn đời khỏi một tử số theo tháng; `Pool` không có vòng đời tháng. Chứng minh cấu trúc:
  ở `unlock = 1.00`, hàm trả **0.000 từ tháng thứ hai sau khi tháng đầu đóng sổ**, tất định và
  không phụ thuộc dữ liệu. Quan sát 90 tháng: 2 Smart ladder; 135.249/135.251 lời gọi trả 0;
  **99,98%** vốn Smart đi qua Month-End thay vì ladder. Hệ quả nặng nhất: **chiều
  `smart_unlock_mode` của Gate 2 (BT §9) trơ hoàn toàn** — ba mode cho kết quả trùng khít
  bit-for-bit, vi phạm ST §6. Kết luận official run: **không đáng tin trước khi sửa**; DEC-009 áp
  dụng phòng ngừa (`no current result to invalidate`). Phân lớp: **A — MUST FIX BEFORE OFFICIAL
  RUN**, chứng minh bằng dependency. Ownership đề xuất: **WP-A7 mới** (RCP-002, chờ phê duyệt) —
  không nhét vào WP-A3 đã DONE, không sửa gate FROZEN của WP-A4/WP-A6. **WP-A4 MAY PROCEED IN
  PARALLEL** kèm 3 điều kiện (assert tiền đề không suy biến; không hard-code kỳ vọng vốn/ETH nhiều
  tháng; tuần tự hoá thao tác trên `engine.py`). Không sửa `src/`, `tests/`, `webapp/`,
  `docs/spec/`; không chạy official backtest; không mở WP nào.
  Artifact: `docs/reviews/PH-03-triage-smart-unlock-scope.md`,
  `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`.
- S003 — WP-A3: REGIME & VÒNG ĐỜI CRASH LADDER — 2026-08-23 — Gói đầu tiên của lớp A và là gói
  duy nhất lớp A làm đổi kết quả mô phỏng. Ready Gate xác nhận lại (T-04 DONE, routing D/Fable/max
  tự nhiên, validator PASS). Baseline E1 tái hiện đủ 4 finding TRƯỚC khi sửa (F-001: kẹt 27.2
  SMART vĩnh viễn sau CRASH→RECOVERY→STRESSED; F-021: snapshot [F5] 34 thay vì 36; F-030: mọi
  crash zone dán nhãn OPPORTUNITY dù 30/34 vốn SMART; F-022: thoát CRASH sau 49h toàn None).
  Test-first: 18 test mới, 12 FAIL đúng kỳ vọng trước fix. Remediation: tách
  `RegimeTracker.state`/`.label` (CONVENTIONS #14 — [F1] bảo đảm bằng cấu trúc), None không
  được coi là bằng chứng transition (CONVENTIONS #15), snapshot [F5] đúng nghĩa đen + daily
  limit cưỡng chế ở khâu triển khai với `DAILY_LIMIT_BLOCK` (CONVENTIONS #4/#5), pool label
  theo đa số nguồn vốn + `zone_order_key` bổ sung vế "crash sau ladder thường" (CONVENTIONS
  #16). Chỉ chạm `regime.py`, `engine.py`, `tests/`, `docs/CONVENTIONS.md` — đúng Scope Lock,
  không chạm `capital.py`/`score.py`/`webapp/`/`docs/spec/`. Suite 87/87 PASS, không test cũ
  nào bị sửa/nới lỏng. Impact BEFORE/AFTER cùng seed/dataset: mọi sai lệch quy về [F5] ST §14
  và ST §18.3+[F1]; nhãn label_transitions identical; công cụ đo commit tại
  `tests/wp_a3_impact_tool.py` (tái lập HOÀN TOÀN, kể cả BEFORE qua git worktree). E2 độc lập:
  **E2 PASS** (`docs/reviews/E2-WP-A3-regime-ladder.md`) — reviewer tự dựng kịch bản khác chứng
  minh khoá vốn trước fix (kẹt 18.7, release 0) và giải phóng đủ sau fix; 4 kịch bản khoá vốn
  tự nghĩ + long-run: không đường khoá vốn mới; 2 finding hạ tầng test (F-E2-01 đơn vị
  datetime64 trong harness, F-E2-02 script đo chưa commit) được xử lý ngay trong phiên và chạy
  lại xanh. Phát hiện mới ngoài scope: PH-03 → RSK-010 (nghi vấn `smart_reservable` trừ
  deployed xuyên tháng — chờ chủ dự án). WP-A4 chuyển PLANNED → READY. BLK-001 giữ nguyên;
  không official run, không verdict; số liệu synthetic chỉ phục vụ verification (DEC-003).
  Kết luận: **WP-A3 DONE — 10/10 REQUIRED PASS, E2 PASS**.
  Biên bản: `docs/sessions/S003-wp-a3-regime-ladder.md`.
- MICRO-GOVDEF-001 — SỬA BOUNDARY DEFECT + OVERRIDE MECHANISM — 2026-08-23 — Chủ dự án phê duyệt
  PA-1 cho DEC-010. Sửa tổng quát `routing_engine.py` (làm tròn `model_score`/`effort_score` về
  cùng độ chính xác hiển thị **trước khi** so sánh biên Tier/Effort — không epsilon tuỳ tiện, không
  hard-code task nào). Bổ sung cơ chế `check_override` vào `validate_routing.py`: chấp nhận manual
  override chỉ khi có decision reference tồn tại thật trong `PROJECT_DECISIONS.md`, `Router Raw
  Output` xác thực khớp router hiện tại, và override chỉ được leo thang chứ không hạ Tier/Effort.
  Thêm `governance/scripts/governance/test_routing_engine.py` (37 check, gồm quét toàn bộ 5^5×5^5
  tổ hợp đầu vào — 0 lệch còn lại — và 6 ca override hợp lệ/không hợp lệ tổng hợp). Kết quả: WP-A2
  route Tier C **tự nhiên** (giữ nguyên Model Opus, Effort high), không cần override — chuyển
  `BLOCKED` → `READY`. BLK-003 RESOLVED, GOV-RSK-001 CLOSED. Đối chiếu trước/sau trên toàn bộ 16
  file MAJOR task: đúng một dòng đổi (WP-A2, Tier B → C), không task nào khác bị ảnh hưởng. Không
  sửa `src/`, `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, không mở S003.
  Kết luận: **MICRO-GOVDEF-001 DONE**.
  Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- S002 — ROADMAP FINALIZATION / GATE FREEZE (T-04) — 2026-08-23 — Soạn và đóng băng Ready Gate +
  Completion Gate đầy đủ cho toàn bộ 15 work package của RCP-001 (**125 REQUIRED check**), cộng file
  định nghĩa cho chính T-04 (12 REQUIRED check). Chính thức hoá DEC-009 thành `CHECK-B1-02`
  (REQUIRED) của WP-B1. Bảo toàn override DEC-008 cho WP-A2 (Tier C / Opus / high) kèm giá trị
  router thô. Bảo toàn đủ 8 trường provenance của T-06A cũ trong WP-A1. Tách rõ trách nhiệm đo lường
  (WP-A5) khỏi trách nhiệm chính sách verdict (WP-B1). Đối chiếu độ phủ bằng script: 40/40 định danh
  finding có nơi thuộc về. Phát hiện PH-01 (sai số đếm trong tóm tắt S001) và PH-02 → **BLK-003**.
  Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`. Không bắt đầu work package nào.
  Kết luận: **T-04 DONE — PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S002-t04-gate-freeze.md`.
  Đối chiếu: `docs/reviews/S002-coverage-regression-check.md`.
- RCP-001 — ROADMAP CHANGE APPLIED — 2026-08-23 — Chủ dự án phê duyệt RCP-001 kèm bốn điều kiện
  (cấu trúc 15 work package; phân lớp A/B/C/D với quy tắc Gate 1 staleness cho F-017; bỏ T-06A,
  hấp thụ vào WP-A1; ghi đè routing của WP-A2 lên Tier C). Bảng roadmap chuẩn được cập nhật từ
  14 lên 28 task. Phát hiện và ghi nhận riêng một governance/tooling defect (GOVDEF-001) trong
  chính `routing_engine.py`, tách khỏi finding sản phẩm. Không sửa `src/`, `webapp/`, `tests/`,
  `docs/spec/`. Không bắt đầu thực thi work package nào. Không bắt đầu S002.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`, `docs/reviews/GOVDEF-001-routing-engine-boundary.md`.
- RCP-001 — ROADMAP CHANGE PROPOSAL (trình) — 2026-08-23 — Chuyển 33 finding của S001 thành 15
  work package có dependency graph và phân lớp A/B/C/D. Trình để chủ dự án phê duyệt.
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
S001 xác nhận: tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không (xem RCP-001).

Cảnh báo quan trọng về ý nghĩa của các validator governance: chúng đang PASS trên **tập rỗng** —
0 evidence record, 0 MAJOR task file, 0 task DONE. Khung đã có, nội dung thì chưa. Không được
đọc các dòng PASS đó như bằng chứng chất lượng dự án.

## Routing sơ bộ cho task chưa có file định nghĩa

**Cập nhật S002:** mục này không còn là nguồn routing cho 15 work package — cả 15 đã có file định
nghĩa đầy đủ dưới `docs/tasks/`, và file task là nguồn routing chính thức theo
`ROADMAP_SYNC_STANDARD.md`. Các giá trị dưới đây được **giữ lại làm dấu vết lịch sử** và đã được
T-04 xác minh lại bằng `routing_engine.py` (E1): 15/15 khớp, ngoại lệ duy nhất là override DEC-008
của WP-A2. Task còn lại chưa có file định nghĩa (T-05…T-11) vẫn dùng mục này.

Ghi lại để lộ trình có bằng chứng routing, sẽ soạn thành file task đầy đủ và đóng băng tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

### Task gốc (S000)

- T-00 — D3 R2 B1 A3 X3 → 2.35 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C4 F2 → 2.7 → xhigh
- T-04 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U2 V2 H3 C3 F3 → 2.60 → xhigh
- T-06 — D2 R3 B3 A1 X3 → 2.45 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-08 — D3 R3 B2 A3 X3 → 2.80 → C (2 floor); U3 V2 H3 C3 F3 → 2.80 → xhigh
- T-09A — D3 R3 B2 A1 X2 → 2.35 → C (floor `safety_business:min_C`); U1 V3 H2 C2 F3 → 2.25 → high
- T-09B — D3 R3 B3 A3 X3 → 3.00 → D (2 floor); U3 V3 H3 C3 F3 → 3.00 → xhigh
- T-10 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-11 — D4 R4 B3 A2 X4 → 3.50 → D (2 floor); U3 V4 H4 C4 F4 → 3.80 → max

Category `accounting_financial` được gắn cho T-06, T-08, T-09A, T-09B, T-10, T-11 vì chúng chạm
lớp tính toán dẫn tới quyết định xuống tiền thật. T-09B gắn thêm
`material_sensitive_data_corruption` vì thao tác chuyển đổi lưu trữ có thể làm hỏng sổ tài chính.

**T-06A đã bị loại khỏi roadmap theo RCP-001** (hấp thụ vào WP-A1). Routing gốc của nó vẫn được
lưu lại để đối chiếu lịch sử: D2 R2 B2 A1 X2 → 1.85 → B; U1 V2 H2 C2 F2 → 1.80 → high.

### Work package của RCP-001 (2026-08-23)

- WP-A1 — D2 R3 B3 A2 X3 → 2.60 → C (không floor); U2 V3 H3 C3 F3 → 2.80 → xhigh
- **WP-A2** — D2 R2 B2 A1 X3 → **model_score = 2.0 (hiển thị), 1.9999999999999998 (nội bộ)** →
  router trả **B** (Sonnet). **GHI ĐÈ THỦ CÔNG theo DEC-008 → Tier C (Opus)**, lý do: defect biên
  dấu phẩy động của router (GOVDEF-001), không phải lỗi chấm điểm đầu vào.
  Effort: U1 V3 H2 C3 F2 → 2.15 → high (giữ nguyên, không bị override)
- WP-A3 — D4 R4 B3 A3 X3 → 3.50 → D (floor `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`,
  `safety_business:min_C`); U3 V4 H4 C3 F4 → 3.65 → max (floor `safety_business:min_high`)
  · category `accounting_financial`
- WP-A4 — D3 R3 B2 A3 X2 → 2.65 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-A5 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U3 V3 H3 C3 F3 → 3.00 → xhigh
- WP-A6 — D4 R3 B3 A2 X3 → 3.10 → D (floor `cognitive:D>=4&X>=3`); U3 V4 H3 C3 F3 → 3.20 → max
- WP-B1 — D3 R4 B3 A4 X3 → 3.40 → D (floor `cognitive:A>=3&X>=3`, `safety_business:min_C`);
  U3 V3 H3 C3 F4 → 3.25 → max (floor `safety_business:min_high`) · category `accounting_financial`
- WP-B2 — D3 R2 B1 A2 X3 → 2.20 → C (không floor); U2 V3 H3 C3 F2 → 2.55 → xhigh
- WP-B3 — D2 R2 B2 A2 X2 → 2.00 → C (không floor); U1 V2 H2 C2 F2 → 1.80 → high
- WP-C1 — D2 R3 B2 A1 X2 → 2.10 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-C2 — D3 R2 B3 A3 X3 → 2.75 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh
- WP-C3 — D3 R3 B2 A2 X2 → 2.50 → C (floor `safety_business:min_C`); U2 V3 H2 C2 F3 → 2.45 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-C4 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-D1 — D1 R1 B1 A1 X1 → 1.00 → B (không floor); U1 V1 H1 C1 F1 → 1.00 → medium
- WP-D2 — D3 R2 B2 A4 X3 → 2.70 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh

- **WP-A7** — D3 R4 B3 A3 X3 → **3.25** → **D** (floor `cognitive:A>=3&X>=3`,
  `safety_business:min_C`); U3 V4 H3 C3 F4 → **3.45** → **max** (floor `safety_business:min_high`)
  · category `accounting_financial` · warnings: none.
  **Đã có file định nghĩa** `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` (2026-08-24)
  → **file task là nguồn routing chính thức**; giá trị ở đây giữ làm dấu vết lịch sử và đã được
  `validate_routing.py` kiểm khớp (17 MAJOR task file).

**GOVDEF-001 / MICRO-GOVDEF-001** — không bắt buộc full routing (MICRO). Chấm điểm tham khảo:
D1 R2 B2 A1 X1 → 1.45 → B; U1 V2 H1 C1 F2 → 1.45 → medium.

## Next Session

Recommended Session:
S004 — hai lựa chọn, chủ dự án quyết định:

- **Theo đường găng — ưu tiên cao nhất:** `WP-A7` (D/Fable/max) — nay **READY**, gate đã đóng
  băng 2026-08-24. Đây là gói duy nhất còn lại chặn cả WP-A5, WP-A6, WP-C4 và GATE-A.
- **Song song được:** `WP-A4` (C/Opus/xhigh) — không bị F-035 chặn về ngữ nghĩa; ba điều kiện của
  RCP-002 phải được tuân thủ (assert tiền đề không suy biến; không hard-code kỳ vọng vốn/ETH
  nhiều tháng; branch isolation + tuần tự hoá merge trên `engine.py`).
- **Theo an toàn dữ liệu thật:** `WP-C1` (C/Opus/xhigh) — độc lập hoàn toàn với lớp A.

Task đang READY (đủ điều kiện bắt đầu, chưa bắt đầu):
`WP-A1`, `WP-A2`, `WP-A4`, **`WP-A7`** (mới), `WP-C1`, `WP-D1`, `WP-D2`.

Task đang PLANNED, chưa đủ điều kiện READY:
- `WP-A5` — chờ WP-A2, WP-A3 ✅, **WP-A7**
- `WP-A6` — chờ WP-A3 ✅, WP-A4, **WP-A7**
- `WP-C4` — chờ WP-A3 ✅, WP-A4, WP-A6, **WP-A7**

Task đang BLOCKED và lý do:
- `WP-C2` — DEC-005 còn PENDING (thuộc T-05, thẩm quyền chủ dự án)
- `T-03` — chờ WP-C1 (giữ nguyên, không hạ Completion Gate)

Cần chủ dự án quyết định:
1. **DEC-005** — phạm vi công cụ trước verdict (T-05). Không chặn lớp A.
2. **PH-01** — cách đính chính số đếm finding trong biên bản S001.
3. **Thứ tự thực thi** — WP-A7 (READY, gate đã đóng băng) và WP-A4 (READY) song song được về
   roadmap. Chủ dự án chọn chạy gói nào trước, hoặc chạy cả hai với branch isolation + merge
   ordering rõ ràng trên `engine.py`. RCP-002 đã áp dụng xong, không còn gì chờ duyệt ở đây.
4. **BLK-001** — máy/VPS truy cập được `data.binance.vision` và `api.binance.com`, cần cho T-06.
   Không gói nào trong 15 gói cần nó, nên chưa gấp.
5. **PH-04** — kênh tiêu thụ unlock liên tục để ba mode `smart_unlock` phân biệt được ở tầng
   outcome (mở WP mới / đề xuất V2.2 qua WP-D2 / chấp nhận giới hạn). Xem mục PH-04 ở
   Active Risks.

Purpose:
Tiếp tục chương trình remediation lớp A trên đường găng tới official run, với Completion Gate đã
đóng băng từ T-04.

KHÔNG tự mở — chủ dự án sẽ ra chỉ thị riêng.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. File định nghĩa của work package được chọn, dưới `docs/tasks/`
6. `docs/sessions/S003-wp-a3-regime-ladder.md` (phiên gần nhất; ngữ nghĩa regime/ladder mới)
7. `docs/CONVENTIONS.md` #14–#16 (nếu gói chạm engine/regime)
8. `docs/reviews/S001-audit-findings.md` — phần finding mà gói đó đóng
9. `docs/spec/` — các điều khoản được viện dẫn trong Completion Gate của gói

Nhắc trước khi mở S003:
Completion Gate của cả 15 gói đã **đóng băng** ngày 2026-08-23. Không được xoá hay làm yếu bất kỳ
REQUIRED check nào để gói đi qua. Nếu một check hoá ra sai hoặc bất khả thi, dùng khối
`COMPLETION GATE CHANGE PROPOSAL` theo `TASK_COMPLETION_GATE_STANDARD.md` và trình chủ dự án —
không sửa im lặng.
