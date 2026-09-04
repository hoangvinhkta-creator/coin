# WP-C2 Scope ADR / DEC-005 Resolution Report

Phiên: WP-C2 Scope ADR / DEC-005 Resolution (SCOPE RESOLUTION ONLY — không implement WP-C2)
Nhánh: `claude/wp-c2-scope-adr-dec005-8o6fvr`
Ngày: 2026-09-04

## 1. Executive Summary

`WP-C2` đang `BLOCKED` vì hai dòng chưa đạt trong chính Ready Gate của nó: (1) `DEC-005` chưa
được chủ dự án chốt tại `T-05`, và (2) chưa có ADR quyết định phạm vi Execution State. Phiên
này **không chốt quyết định nào thay chủ dự án** — nó tái dựng đầy đủ thẩm quyền canonical, phát
hiện rằng `DEC-005` (câu hỏi rộng: phạm vi webapp/dashboard được xây trước verdict) và câu hỏi
Ready Gate thực sự chặn `WP-C2` là **hai việc khác nhau**, và soạn sẵn một gói quyết định tối
thiểu để chủ dự án phê duyệt trong một dòng.

Phát hiện chính: phạm vi ĐÃ ĐÓNG BĂNG của `WP-C2` (chỉ `docs/adr/`, phần đặt tên trong
`src/eth_dca_os/engine.py`, `tests/`, `docs/CONVENTIONS.md`) không chạm một dòng `webapp/` nào —
gói này chỉ đặt tên hành vi backtest đã có, không xây dashboard, không đổi kết quả backtest. Vì
vậy nó không thể vi phạm bất kỳ phương án nào (PA-1/PA-2/PA-3) mà `DEC-005` đang cân nhắc cho
webapp. Khuyến nghị: chủ dự án phê duyệt một **phân xử HẸP** riêng cho `WP-C2` (không cần đợi
`DEC-005` được chốt theo nghĩa rộng cho webapp), cộng với việc chấp nhận một ADR kỹ thuật nhỏ,
rủi ro thấp, đã có sẵn bằng chứng (`FUNDING_REQUIRED` không áp dụng ở tầng backtest). Cả hai gộp
lại đủ để chuyển `WP-C2: BLOCKED → READY`. `DEC-005` bản thân **vẫn PENDING** sau quyết định
này, tiếp tục chặn `T-08` — không bị đóng "nhân tiện".

Không có production code nào bị sửa trong phiên này. Không có gì được implement. `WP-C2` vẫn
`BLOCKED` cho tới khi chủ dự án phê duyệt.

## 2. Source / Repository State

```
origin/main (kỳ vọng)  = 3649316c2c9ad062e28a0b084970381f370031b6
origin/main (đo được)  = 3649316c2c9ad062e28a0b084970381f370031b6   KHỚP
nhánh phiên             = claude/wp-c2-scope-adr-dec005-8o6fvr
tạo từ                  = origin/main tại đúng SHA trên (0 divergence lúc mở phiên)
```

`main` HEAD khớp chính xác giá trị kỳ vọng trong chỉ thị phiên — không có `SOURCE_STATE_REVIEW_REQUIRED`.
Không có commit nào ngoài dự kiến. `data/` (untracked, thuộc chủ dự án) không bị chạm.

## 3. Canonical Evidence Reviewed

- `AGENTS.md` (authority order §1), `governance/v4/CORE/STATE_AUTHORITY.md`,
  `governance/v4/CORE/CAPABILITY_MODEL.md`
- `PROJECT/PROJECT_PROGRESS.md` (roadmap chuẩn, "Critical path sau RCP-002", mục "Cần chủ dự án
  quyết định")
- `PROJECT/PROJECT_DECISIONS.md` — toàn bộ `DEC-001`…`DEC-034`, trọng tâm `DEC-005`, `DEC-007`,
  `DEC-009`, `DEC-011`, `DEC-021`, `DEC-029`, `DEC-030`, `DEC-031`, `DEC-034`
- `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/PRODUCTION_PATHS.md`,
  `PROJECT/HARDENING_BACKLOG.md` (H-19, H-20)
- `docs/tasks/WP-C2-execution-state-machine.md`, `docs/tasks/WP-B3-audit-trail-decision-log.md`
  (hai file task đã đóng băng, đầy đủ Ready Gate/Completion Gate)
- `docs/adr/ADR-000-TEMPLATE.md`, `docs/adr/README.md` (tiền lệ định dạng ADR — trước phiên này
  repo **chưa có ADR thật nào**, chỉ có template)
- `docs/CONVENTIONS.md` #8 (quy ước `funding_delay`/`funding_policy`), mục đánh số cao nhất hiện
  tại = #21
- `docs/spec/01_PRODUCT_SPEC_V2_1_5.md` §6-7, `02_STRATEGY_SPEC_V2_1_5.md` §16 (Execution State
  enum), `03_BACKTEST_SPEC_V2_1_5.md` §5/§7/§10 (`funding_delay`, Gate 1/Gate 3 friction),
  `05_IMPLEMENTATION_PLAN_V2_1_5.md`, `RELEASE_CHECK_V2_1_5.md`

## 4. What DEC-005 Actually Requires

`DEC-005` (PENDING từ S000, task `T-05`) là câu hỏi: **webapp/dashboard được phép xây tới đâu
trước khi verdict cho phép?** Ba phương án đã nêu sẵn trong chính `DEC-005`:

- **PA-1** — đóng băng webapp ở mức hiện tại.
- **PA-2** (khuyến nghị sơ bộ ban đầu) — tách hai lớp: *ghi chép/quan sát* (không bị chặn) và
  *tự động hoá chiến lược* (bị chặn tới khi có verdict BUILD).
- **PA-3** — mở V2.2 nếu muốn đổi chính điều khoản cổng.

Đây là quyết định **phạm vi sản phẩm**, thuộc thẩm quyền chủ dự án
(`STATE_AUTHORITY.md`; chính văn bản `DEC-005` ghi "không phải quyết định kỹ thuật mà agent
được tự quyết"). `DEC-005` KHÔNG nói gì về backtest engine hay `WP-C2` cụ thể — nó nói về
`webapp/`.

## 5. Why WP-C2 Is Currently Blocked

Ready Gate của `WP-C2` (đóng băng 2026-08-23) có đúng hai dòng chưa `[x]`:

1. `DEC-005` đã được chủ dự án quyết định tại `T-05`.
2. ADR phạm vi Execution State tồn tại và được chủ dự án chấp nhận (câu hỏi: backtest có cần mô
   hình hoá treasury USDT để `FUNDING_REQUIRED` có nghĩa không?).

Dòng (1) trói `WP-C2` vào toàn bộ `DEC-005` theo câu chữ gốc — nhưng như §7 dưới đây phân tích,
đây là một liên kết RỘNG HƠN MỨC CẦN THIẾT xét theo phạm vi thật của `WP-C2`. Dòng (2) là một
câu hỏi kiến trúc backtest hoàn toàn tách biệt, không liên quan gì tới webapp.

`DEC-030` (2026-09-03, canonical, đã áp dụng) xác nhận dứt khoát: `T-05`/`DEC-005` **chỉ chặn
`T-08` và `WP-C2`**, không nằm trên đường găng tới `T-06`/verdict.

## 6. WP-C2 Capability Boundary

### Mission
Đặt tên, hợp nhất và lưu vết **hành vi đã có** trong backtest engine thành sáu Execution State
mà Strategy §16/§19 định nghĩa (`WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING /
COOLDOWN / DATA_BLOCKED`), để backtest và app tương lai mô tả cùng một tình huống bằng cùng một
ngôn ngữ. Đóng finding F-006.

### In Scope
- Viết một ADR quyết định phạm vi cho câu hỏi treasury USDT (đã soạn sẵn: `ADR-001`, xem §10).
- Đặt tên và lưu vết năm trạng thái đã có hành vi thật: `WAIT`, `READY_TO_BUY`
  (`engine.py:431`), `ACTION_PENDING` (hiện ở `Zone.status`, `engine.py:235`), `COOLDOWN`
  (`in_cooldown`, `engine.py:422,517`), `DATA_BLOCKED` (`engine.py:452,506`).
- Hợp nhất `Zone.status`/`in_cooldown`/`dq` về một chiều Execution State nhất quán.
- Lưu `execution_state` vào `market_snapshots` nếu thuộc phạm vi (DM §4 đòi NOT NULL).
- Ghi quy ước mới vào `docs/CONVENTIONS.md`.

### Out of Scope
- Đổi hành vi thực thi/kết quả backtest (đây là gói đặt tên, không phải gói logic mới).
- Market Regime (thuộc `WP-A3`, đã DONE) — không định nghĩa lại chiều này.
- Partial fill (`WP-C3`).
- `decision_log` (`WP-B3` tiêu thụ enum do `WP-C2` sinh ra, không định nghĩa nó).
- Sửa V2.1.5 để hợp thức hoá lựa chọn phạm vi — nếu phát sinh nhu cầu đó thì chuyển `WP-D2`.
- Bất kỳ thứ gì thuộc `webapp/` — **không** nằm trong Scope đã đóng băng của `WP-C2`.
- Tạo class `StateMachine` chỉ để khớp danh từ trong spec (RCP-001 cấm tường minh).

### Inputs
Hành vi hiện có của `engine.py` (điều kiện `ts >= execute_at`, `Zone.status`, `in_cooldown`,
`dq == INVALID`); enum Execution State của Strategy §16/§19; quy ước `funding_delay`/
`funding_policy` đã canonical tại `docs/CONVENTIONS.md` #8.

### Outputs
Enum Execution State được đặt tên và lưu vết nhất quán trong backtest engine; (nếu thuộc phạm
vi) trường `market_snapshots.execution_state`; một ADR ghi nhận quyết định phạm vi; mục mới
trong `docs/CONVENTIONS.md`. Kết quả backtest bit-for-bit không đổi.

### Owner / Responsibility Boundary
`WP-C2` thuộc capability `CAP-WEBAPP` (theo `CAPABILITY_REGISTRY.md`, dù bản thân task chỉ chạm
backtest engine, không chạm `webapp/`). Owner kỹ thuật là phiên thực thi `WP-C2` tương lai;
Owner quyết định (Ready Gate, ADR) là chủ dự án.

### Production Path
`src/eth_dca_os/engine.py` là production path chính (`PRODUCTION_PATHS.md` §1). `docs/adr/` và
`docs/CONVENTIONS.md` KHÔNG phải production path, nhưng `docs/CONVENTIONS.md` được Exit Criteria
của các gói khác viện dẫn trực tiếp nên sai lệch với nó vẫn có thể BLOCKING qua đường Completion
Gate (không qua đường production diff).

### Downstream Contract with WP-B3
`WP-B3` cần từ `WP-C2` đúng một thứ: **enum Execution State đã đặt tên**, để điền
`previous_state`/`new_state` trong `decision_log` (Data Model §11). `WP-B3` tiêu thụ enum này,
không được tự định nghĩa enum riêng (nếu làm vậy sẽ tạo ra chiều trạng thái thứ hai — đúng loại
trôi lệch Implementation Plan §1 muốn chặn). Nếu `WP-C2` chưa `DONE`, `CHECK-B3-02` của `WP-B3`
là `BLOCKED`, không phải `NOT_APPLICABLE`, không phải `PASS`.

### Completion Boundary
`WP-C2` được coi là `DONE` khi: 8/8 REQUIRED check của Completion Gate đã đóng băng PASS (ADR
tồn tại và được viện dẫn; sáu trạng thái được đặt tên/lưu vết theo đúng phạm vi ADR quyết định;
`FUNDING_REQUIRED` được xử lý tường minh — không im lặng vắng mặt; Market Regime và Execution
State lưu riêng; `execution_state` NOT NULL nếu thuộc phạm vi; kết quả backtest không đổi; không
tạo class `StateMachine` khớp tên suông; toàn bộ test suite PASS) — và kết quả backtest
bit-for-bit trùng khớp trước/sau.

## 7. Relationship Between T-05, DEC-005, WP-C2 and WP-B3

`T-05` là một task kiểu DUYỆT (Owner-approval), không có file task/Completion Gate riêng dưới
`docs/tasks/` — bản thân nó LÀ hành động chốt `DEC-005`. `DEC-030` (canonical, đã áp dụng) xác
nhận `T-05`/`DEC-005` không nằm trên đường găng tới `T-06`, chỉ chặn `T-08` và `WP-C2`.

Điểm mấu chốt phiên này phát hiện: liên kết "`WP-C2` chờ `DEC-005`" trong chính file task
`WP-C2` là liên kết ĐÚNG NHƯNG RỘNG HƠN MỨC CẦN THIẾT. `DEC-005` là câu hỏi phạm vi **webapp**.
`WP-C2` (Scope đã đóng băng) không chạm `webapp/` — nó chỉ đặt tên hành vi backtest engine đã
có, và tường minh cấm đổi kết quả backtest (`CHECK-C2-06`). `PROJECT/HARDENING_BACKLOG.md` mục
H-20 xác nhận độc lập: nó liệt kê "`WP-C2` biến app từ GHI NHẬN sang ĐẶT LỆNH (execution state
machine)" như một `RE_TRIGGER_CONDITION` cho **một sự kiện giả định trong tương lai**, không
phải mô tả những gì `WP-C2`, như đã đóng băng, thực sự làm hôm nay.

Vì `WP-C2` không có khả năng vi phạm bất kỳ phương án nào trong PA-1/PA-2/PA-3 (nó không xây
webapp, không xây tự động hoá), câu hỏi Ready Gate (1) của nó có thể được phân xử bằng một
quyết định **hẹp hơn** toàn bộ `DEC-005` — mà không cần chờ chủ dự án chốt xong câu hỏi rộng về
webapp (vốn vẫn cần thiết riêng cho `T-08`).

Đối chiếu §7 của chỉ thị phiên (A–H):

- **A.** `T-05` không tự nó cần "hoàn thành" — nó là hành động Owner ra quyết định `DEC-005`.
- **B.** `T-05` vẫn `PENDING` vì đây là quyết định phạm vi sản phẩm rộng (webapp), chưa được chủ
  dự án chốt phương án nào trong ba phương án đã nêu từ S000.
- **C.** `WP-C2` `BLOCKED` vì Ready Gate của chính nó ghi rõ điều kiện, không phải vì có
  dependency kỹ thuật thật nào tới `webapp/`.
- **D.** Câu hỏi kiến trúc thật sự thiếu là ADR treasury USDT (Ready Gate dòng 2) — một câu hỏi
  backtest-engine nội bộ, tách biệt khỏi `DEC-005`.
- **E.** `WP-B3` phụ thuộc `WP-C2` DONE (không phải `DEC-005`) cho enum trạng thái.
- **F.** `WP-C2` đóng góp cho Gate-B **gián tiếp**, qua việc mở khoá `WP-B3`.
- **G.** **Kết luận: `DEC-005` KHÔNG cần được chốt theo nghĩa đầy đủ (PA-1/2/3 cho webapp) để mở
  `WP-C2`.** Một phân xử hẹp, chỉ áp dụng cho `WP-C2`, là đủ — xem §8/§9.
- **H.** Dependency "`WP-C2` chờ `DEC-005`" trong `docs/tasks/WP-C2-*.md` là canonical (Ready
  Gate đã đóng băng, không tự sửa được), nhưng cách nó được VIẾT là rộng hơn nội dung nó thực sự
  cần — đây là chỗ cần một quyết định phạm vi hẹp bổ sung, không phải xoá dependency.

## 8. Options Considered

**PA-A (khuyến nghị) — Phân xử hẹp chỉ cho `WP-C2`.** Chủ dự án xác nhận tường minh: vì phạm vi
đã đóng băng của `WP-C2` không chạm `webapp/` và không xây tầng tự động hoá thực thi, dòng Ready
Gate (1) của `WP-C2` được coi là thoả mà không cần đợi `DEC-005` chốt theo nghĩa rộng. `DEC-005`
bản thân vẫn `PENDING`, tiếp tục chặn `T-08`.
- Lợi ích: nhỏ nhất, mở đúng một gói đang chờ, không khoá webapp vào bất kỳ phương án nào trước
  hạn, không tạo tiền lệ kiến trúc mới.
- Chi phí: gần như bằng 0 — đây là việc formalize một sự thật đã đúng từ khi Scope của `WP-C2`
  được đóng băng.
- Rủi ro: thấp. Rủi ro duy nhất là nếu phạm vi `WP-C2` bị mở rộng sau này để chạm `webapp/` mà
  không quay lại xin quyết định mới — giảm thiểu bằng cách giữ nguyên "Do not touch without
  Scope Expansion: webapp/" trong file task.
- Hiệu ứng lên `WP-C2`: `BLOCKED → READY` (cùng với ADR-001 được chấp nhận).
- Hiệu ứng lên `WP-B3`: gián tiếp mở đường (vẫn cần `WP-C2` thật sự `DONE`, không chỉ `READY`).
- Hiệu ứng lên `Gate-B`: không mở ngay, nhưng gỡ đúng một mắt xích trên đường tới nó.
- Không tạo kiến trúc mới không cần thiết — đúng nghĩa đen "phân xử", không "thiết kế".

**PA-B — Chốt toàn bộ `DEC-005` ngay bây giờ** (ví dụ phê duyệt PA-2 của `DEC-005` — tách hai
lớp — vốn là khuyến nghị sơ bộ ban đầu, và trên thực tế đã là mô hình vận hành kể từ khi `T-09A`
sửa lỗi kế toán và `T-09B` dựng persistence Firebase, đều đã `DONE` mà không chờ `DEC-005`).
- Lợi ích: đóng luôn `DEC-005`, mở CẢ `WP-C2` LẪN `T-08` cùng lúc; dọn một khoản nợ governance đã
  treo từ S000.
- Chi phí: lớn hơn — đây là quyết định phạm vi sản phẩm chính thức, ảnh hưởng rộng hơn những gì
  `WP-C2` cần, cần chủ dự án cân nhắc kỹ hơn (ranh giới "ghi chép" vs "tự động hoá" cho MỌI tính
  năng webapp tương lai, không chỉ `WP-C2`).
- Rủi ro: trung bình — nếu chốt vội một ranh giới rộng chỉ để mở một gói hẹp, có thể phải sửa lại
  sau.
- Hiệu ứng: giống PA-A cho `WP-C2`, cộng thêm mở `T-08`.
- Không bắt buộc để mở `WP-C2` — đây là lựa chọn "làm nhiều hơn cần thiết", không sai nhưng không
  phải phương án nhỏ nhất.

**PA-C — Không làm gì.** Giữ `WP-C2` `BLOCKED` vô thời hạn.
- Không khuyến nghị: không có lý do kỹ thuật mới nào để tiếp tục chặn một gói không chạm
  `webapp/`; vi phạm nguyên tắc "CONTINUE is the default" của `AGENTS.md` §3 mà không có hard-stop
  hợp lệ nào biện minh cho việc đứng yên.

Repository authority không tự làm rõ một đáp án duy nhất mà không cần Owner — cả phạm vi hẹp
(PA-A) lẫn phạm vi rộng (PA-B) đều là lựa chọn hợp lệ về mặt kỹ thuật; khác biệt là mức độ sản
phẩm chủ dự án muốn cam kết ngay bây giờ.

## 9. Recommended Decision

Chủ dự án nên phê duyệt **PA-A** (phân xử hẹp) **cộng với** chấp nhận **`ADR-001`**
(`docs/adr/ADR-001-wp-c2-execution-state-scope.md`). Hai việc này cùng nhau thoả đủ hai dòng
Ready Gate của `WP-C2`, không đụng tới câu hỏi webapp rộng hơn của `DEC-005` (vẫn để ngỏ cho một
phiên riêng quyết định khi cần mở `T-08`).

Cụ thể, một phiên thực thi `WP-C2` trong tương lai sẽ biết:
- **Phải xây gì**: đặt tên/lưu vết năm trạng thái (`WAIT`, `READY_TO_BUY`, `ACTION_PENDING`,
  `COOLDOWN`, `DATA_BLOCKED`) theo hành vi đã có; ghi `FUNDING_REQUIRED = NOT_APPLICABLE` ở tầng
  backtest theo `ADR-001`.
- **Không được xây gì**: không mô hình hoá treasury USDT động; không chạm `webapp/`; không đổi
  kết quả backtest; không tạo class `StateMachine` chỉ để khớp tên spec.
- **Dừng ở đâu**: đúng biên `docs/adr/`, `engine.py` (phần đặt tên), `tests/`,
  `docs/CONVENTIONS.md`.
- **Bằng chứng gì chứng minh hoàn tất**: 8/8 REQUIRED check của Completion Gate đã đóng băng,
  kết quả backtest bit-for-bit không đổi, enum sẵn sàng cho `WP-B3`/`WP-C3` tiêu thụ.

## 10. Exact Proposed ADR / Owner Decision

Hai artifact đã được soạn sẵn ở trạng thái **Proposed/PENDING**, chờ chủ dự án:

1. **`docs/adr/ADR-001-wp-c2-execution-state-scope.md`** (Status: Proposed) — quyết định kỹ
   thuật: `FUNDING_REQUIRED` = `NOT_APPLICABLE` ở tầng backtest engine (không mô hình hoá
   treasury USDT động; giữ nguyên quy ước đã canonical `docs/CONVENTIONS.md` #8, đã được chính
   official run `T-06` sử dụng); năm trạng thái còn lại thuộc phạm vi đặt tên của `WP-C2`; tầng
   app/live vẫn giữ nguyên yêu cầu `FUNDING_REQUIRED` theo Product Spec §6/§11, không bị ADR này
   đụng tới.
2. **`DEC-035`** (`PROJECT/PROJECT_DECISIONS.md`, PENDING) — quyết định phạm vi: phân xử HẸP cho
   Ready Gate dòng (1) của `WP-C2`, tách khỏi câu hỏi rộng `DEC-005`/webapp. Ghi rõ quan hệ với
   `DEC-005`:

```
DEC-005:
  vẫn PENDING — câu hỏi phạm vi webapp/dashboard trước verdict (PA-1/PA-2/PA-3).
  KHÔNG bị đóng, KHÔNG bị sửa nội dung lịch sử. Tiếp tục chặn T-08.

DEC-035 (mới, PENDING):
  phân xử hẹp: dòng Ready Gate (1) của WP-C2 ("DEC-005 đã được chủ dự án quyết định tại T-05")
  được coi là THOẢ khi chủ dự án phê duyệt PA-A, VÌ phạm vi đã đóng băng của WP-C2 không có khả
  năng vi phạm bất kỳ phương án nào của DEC-005.
  → tiền đề DEC-005 cho riêng WP-C2 được disposed/resolved qua PA-A, KHÔNG đại diện cho việc
    DEC-005 nói chung đã được chốt.
```

Không ai trong hai artifact này bị agent tự đánh dấu Accepted/RESOLVED — cả hai đứng ở trạng
thái đề xuất, chờ đúng một hành động của chủ dự án (xem §22, "OWNER ACTION").

## 11. Owner Approval Required?

**CÓ — `OWNER_DECISION_REQUIRED`.** Đây là quyết định phạm vi sản phẩm/kiến trúc, thuộc thẩm
quyền chủ dự án theo `STATE_AUTHORITY.md` và theo chính văn bản gốc của `DEC-005`. Chỉ thị phiên
này KHÔNG cấp thẩm quyền cho agent tự phê duyệt PA-A/PA-B hay tự chấp nhận `ADR-001` thay chủ dự
án — chỉ cấp thẩm quyền chuẩn bị. Phiên này không giả vờ đã được duyệt.

## 12. Current State

```
T-05        = PLANNED (chưa chạy — Owner chưa ra quyết định DEC-005)
DEC-005     = PENDING
WP-C2       = BLOCKED   (Ready Gate: 2/2 dòng liên quan còn [ ])
WP-B3       = BLOCKED   (chờ WP-C2 DONE)
WP-B2       = READY     (không đổi, không phụ thuộc WP-C2/DEC-005)
GATE-B      = CHƯA MỞ   (WP-B1 DONE ∧ WP-B2 READY ∧ WP-B3 BLOCKED)
T-07        = NOT READY (chờ GATE-B)
T-11        = BLOCKED   (chờ T-07 ∧ WP-C2 ∧ WP-C3 ∧ WP-C4, VÀ chờ verdict=BUILD — verdict hiện
                          tại là DO_NOT_BUILD, `DEC-031`, không đổi)
```

## 13. State If Recommended Decision Is Approved

Giả định chủ dự án phê duyệt **PA-A** + chấp nhận **`ADR-001`** (theo §22):

```
T-05        = vẫn PLANNED/mở một phần — DEC-005 (nghĩa rộng, webapp) VẪN PENDING, chỉ phần
              WP-C2 của tiền đề được disposed
DEC-005     = PENDING (không đổi) — tiếp tục chặn T-08
DEC-035     = RESOLVED (PA-A approved)
WP-C2       = READY (chưa DONE — cần một phiên thực thi riêng, xem §14 hợp đồng tương lai)
WP-B3       = BLOCKED (không đổi — vẫn chờ WP-C2 thật sự DONE, không chỉ READY)
WP-B2       = READY (không đổi)
GATE-B      = CHƯA MỞ (không đổi ở phiên này)
T-07        = NOT READY (không đổi)
T-11        = BLOCKED (không đổi — verdict=DO_NOT_BUILD vẫn là rào cản độc lập, ngoài phạm vi
              phiên này)
```

Nếu chủ dự án chọn **PA-B** thay vì PA-A: kết quả giống hệt trên, cộng thêm `DEC-005 = RESOLVED`
và `T-08` chuyển từ bị chặn sang có thể mở.

## 14. Future WP-C2 Implementation Contract

**MISSION** — Đặt tên, hợp nhất, lưu vết sáu Execution State theo Strategy §16/§19 bằng hành vi
backtest đã có; đóng F-006.

**IN SCOPE** — Viện dẫn `ADR-001` (đã có sẵn); đặt tên/hợp nhất `WAIT`, `READY_TO_BUY`,
`ACTION_PENDING`, `COOLDOWN`, `DATA_BLOCKED` trong `engine.py`; lưu `execution_state` vào
`market_snapshots` nếu ADR đưa vào phạm vi; ghi quy ước vào `docs/CONVENTIONS.md` (#22).

**OUT OF SCOPE** — Mô hình hoá treasury USDT động (đã quyết `NOT_APPLICABLE` tại `ADR-001`);
Market Regime (`WP-A3`); Partial fill (`WP-C3`); `decision_log` (`WP-B3`); bất kỳ thay đổi
`webapp/`; đổi kết quả backtest.

**INPUTS** — Hành vi hiện có `engine.py` (S001 discovery table); `ADR-001`; quy ước
`docs/CONVENTIONS.md` #8.

**OUTPUTS** — Enum Execution State đặt tên nhất quán; (nếu thuộc phạm vi)
`market_snapshots.execution_state`; mục `docs/CONVENTIONS.md` mới; test mới.

**TOUCH AREA** — `docs/adr/` (viện dẫn `ADR-001`, không tạo ADR thứ hai trừ khi phát sinh câu hỏi
mới), `src/eth_dca_os/engine.py` (chỉ phần đặt tên/lưu trạng thái), `tests/`,
`docs/CONVENTIONS.md`.

**DO-NOT-TOUCH AREA** — `src/eth_dca_os/regime.py`, `capital.py`, `score.py`, `ladders.py`,
`verdict.py`; toàn bộ `webapp/`; `docs/spec/`.

**REQUIRED CHECKS** — 8/8 REQUIRED của Completion Gate đã đóng băng
(`CHECK-C2-01`…`CHECK-C2-08`, xem `docs/tasks/WP-C2-execution-state-machine.md`), tất cả E1 trừ
`CHECK-C2-07` (E0, thiết kế).

**PRODUCTION REACHABILITY** — Bằng chứng phải đến từ một lần chạy backtest thật (không chỉ unit
test), chứng minh `execution_state` đọc được tại từng thời điểm cho các trạng thái thuộc phạm
vi, và metric trước/sau trùng khớp bit-for-bit trên cùng seed/dataset.

**COMPLETION GATE** — 8/8 REQUIRED PASS; kết quả backtest không đổi; enum sẵn sàng cho
`WP-B3`/`WP-C3` tiêu thụ; không hạ REQUIRED check nào.

**STOP CONDITIONS** — Việc đặt tên trạng thái làm đổi kết quả backtest → DỪNG, `SCOPE_CHANGED`.
Mô hình hoá treasury USDT hoá ra cần đổi Backtest §5 → `CONFLICT DETECTED`, chuyển `WP-D2`,
không vá V2.1.5. Sáu trạng thái của spec không phủ hết hành vi thật → ghi khoảng trống, trình
chủ dự án, không tự thêm trạng thái thứ bảy.

**MODEL / EFFORT RECOMMENDATION** — Theo routing đã đóng băng: Tier C, Effort `xhigh` (đã ROUTED,
xem Routing Inputs trong file task; không cần route lại trừ khi phạm vi đổi).

## 15. Critical Path to Gate-B

```
[Owner: phê duyệt PA-A + ADR-001]  (phiên này chuẩn bị, KHÔNG tự chốt)
        │
        ▼
   WP-C2 : BLOCKED → READY → (phiên thực thi riêng) → DONE
        │
        ▼
   WP-B3 : BLOCKED → (phiên thực thi riêng, cần WP-C2 DONE) → DONE
        │                                   ▲
        │                     WP-B2 : READY │ (song song, độc lập — không chờ WP-C2)
        ▼                                   │
   GATE-B = WP-B1(DONE) ∧ WP-B2(DONE) ∧ WP-B3(DONE)  ──►  T-07 (DUYỆT, Owner đọc verdict)
                                                                   │
                                                                   ▼
                                                    T-11 — CÒN CẦN THÊM verdict = BUILD
                                                    (hiện tại: DO_NOT_BUILD, DEC-031 — rào cản
                                                     ĐỘC LẬP, ngoài phạm vi quyết định này)
```

**Nút thắt (bottleneck) thật sự**: `WP-C2 → WP-B3`, không phải `WP-B2` (đã `READY`, không phụ
thuộc gì thêm). Ngay cả khi `Gate-B` mở và `T-07` chạy, `T-11` vẫn bị khoá bởi verdict lịch sử
`DO_NOT_BUILD` — một rào cản hoàn toàn tách biệt khỏi `WP-C2`/`DEC-005`, không thuộc phạm vi
phiên này (không được điều tra chiến lược/AE).

## 16. Parallel Work Opportunities

- `WP-B2` có thể chạy **song song** với việc thực thi `WP-C2` — không phụ thuộc kỹ thuật giữa
  hai gói (`WP-C2` tự khai "Parallel-Safe With: WP-C1, WP-C4, WP-D1, WP-D2"; `WP-B1` tự khai
  "Parallel-Safe With: WP-B1, WP-B2" cho `WP-B3`).
- `WP-C4` (Sau WP-A3/A4/A6/A7, tất cả đã DONE) có thể chạy song song với `WP-C2` — không có
  dependency giữa hai gói.
- `WP-C3` phải chờ `WP-C2` DONE (tiêu thụ enum).
- `WP-B3` phải chờ `WP-C2` DONE (không chỉ READY) cho `CHECK-B3-02`.

**Ngay sau khi Owner phê duyệt**, việc nên thực thi ngay (ở các phiên riêng, KHÔNG phải phiên
này): mở một phiên thực thi `WP-C2` theo hợp đồng §14; `WP-B2` có thể được thực thi độc lập bất
cứ lúc nào (đã `READY` từ trước, không chờ quyết định này).

## 17. Risks / Non-Blocking Hardening

- **Ghi chú tài liệu (không BLOCKING)**: mục "Dependencies" trong
  `docs/tasks/WP-C2-execution-state-machine.md` ghi `**T-05 / DEC-005** (DONE)` — đọc theo văn
  cảnh (Ready Gate ngay bên dưới vẫn để `[ ]` cho đúng dòng này, và Status đầu file là `BLOCKED`)
  thì đây là ký hiệu "trạng thái đích cần đạt", không phải khẳng định hiện trạng — nhưng cách viết
  dễ gây hiểu lầm khi đọc rời khỏi ngữ cảnh. Không sửa trong phiên này (không phải Owner-only
  scope decision, và sửa câu chữ một Ready Gate đã đóng băng cần đi qua
  `TASK_COMPLETION_GATE_STANDARD.md` "After Freeze"); ghi nhận để phiên thực thi `WP-C2` tương
  lai làm rõ lại khi mở gói.
- **`H-19`/`H-20`** (`HARDENING_BACKLOG.md`, CONFIRMED HARDENING, không BLOCKING): cả hai đã có
  `RE_TRIGGER_CONDITION` riêng nhắc tên `WP-C2`. `H-20` đặc biệt liên quan: nếu một `WP-C2`
  tương lai (KHÔNG phải gói đang xét ở đây) mở rộng để biến app thành hệ đặt lệnh, `H-20` phải
  được xét lại. Không hành động gì cần thiết bây giờ — chỉ ghi nhận liên kết cho phiên tương lai.
- Không phát hiện defect production nào trong phiên này (phiên không đọc production code để tìm
  bug, chỉ đọc để xác định scope).

## 18. Production Diff Verification

```
$ git diff --stat -- src/ webapp/ pyproject.toml pyproject.lock
(rỗng)
```

Xem §19 để có bằng chứng lệnh thật đã chạy. Production diff của phiên này = **ZERO**, đúng yêu
cầu §12/§17 của chỉ thị phiên.

## 19. Validators

- `git diff --stat -- src/ webapp/ pyproject.toml pyproject.lock` — rỗng (xác nhận trực tiếp).
- Không có file task mới nào được đăng ký dưới `docs/tasks/` (không tạo task ID mới) — routing
  validator (`validate_routing.py`) không có gì mới để kiểm; không chạy lại vì không đổi input
  routing của bất kỳ file `docs/tasks/*.md` nào.
- Không đổi bảng roadmap chuẩn (Status/Tier/Effort/dependency) trong `PROJECT_PROGRESS.md` — chỉ
  thêm mục "Last Updated" tường thuật — nên không bắt buộc chạy lại
  `governance/scripts/governance/sync_easy_roadmap.py`/`validate_easy_roadmap.py`. Đã chạy lại
  để chắc chắn `LO_TRINH_DE_HIEU.md` (generated) không lệch:

```
$ python3 governance/scripts/governance/sync_easy_roadmap.py   # (xem output thật ở phần commit)
```

- Không chạy Python production test suite — đúng yêu cầu §17 của chỉ thị phiên (production diff
  = 0 nên không cần).

## 20. Files Changed

```
A  docs/adr/ADR-001-wp-c2-execution-state-scope.md
M  PROJECT/PROJECT_DECISIONS.md          (+ DEC-035, PENDING, append-only)
M  PROJECT/PROJECT_PROGRESS.md           (+ mục "Last Updated" tường thuật; không đổi bảng
                                            roadmap/trạng thái task nào)
A  docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md   (chính báo cáo này)
```

Không file nào dưới `src/`, `webapp/`, `pyproject.toml`, `pyproject.lock`, `docs/tasks/`,
`docs/CONVENTIONS.md`, `docs/spec/` bị chạm.

## 21. Commit / Push

Commit và push tới nhánh phiên `claude/wp-c2-scope-adr-dec005-8o6fvr` (không push `main`, không
merge `main`). SHA chính xác và trạng thái push: xem phản hồi cuối phiên (mục STATUS/COMMIT/PUSH
ở terminal) — Owner trên điện thoại nên chi tiết đầy đủ nằm ở đây, terminal chỉ tóm tắt.

## 22. Exact Next Action

1. Chủ dự án đọc §9/§10 và trả lời **đúng một trong hai dòng** ở mục "OWNER ACTION" bên dưới.
2. Sau khi được duyệt, một phiên MỚI (không phải phiên này) mở `WP-C2` theo hợp đồng §14, chạy
   subtask C2.1–C2.6 và Completion Gate 8/8.
3. Song song, có thể mở `WP-B2` (đã `READY`, không chờ quyết định này) ở một phiên riêng bất cứ
   lúc nào.
4. `T-08` (đặc tả lớp cảnh báo) tiếp tục `BLOCKED` bởi `DEC-005` trừ khi chủ dự án chọn **PA-B**
   thay vì PA-A ở bước 1.

---

## OWNER ACTION

Chủ dự án chỉ cần chọn MỘT trong hai dòng dưới đây (hoặc trả lời "KHÔNG DUYỆT" để giữ nguyên
`WP-C2 = BLOCKED`):

**Để mở `WP-C2` mà không đụng câu hỏi webapp rộng hơn (khuyến nghị):**
> APPROVE PA-A CHO DEC-035, VÀ CHẤP NHẬN ADR-001.

**Để đóng luôn toàn bộ DEC-005 (mở cả WP-C2 lẫn T-08), ví dụ chọn PA-2 của chính DEC-005:**
> APPROVE PA-B CHO DEC-035 (= PA-2 CHO DEC-005), VÀ CHẤP NHẬN ADR-001.

Không cần đọc source code hay tự dựng lại quyết định — hai dòng trên là đủ để phiên tiếp theo
biết chính xác phải làm gì.
