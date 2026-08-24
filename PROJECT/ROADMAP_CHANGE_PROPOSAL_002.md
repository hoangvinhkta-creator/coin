# ROADMAP CHANGE PROPOSAL — RCP-002

Ngày: 2026-08-24
Nguồn: triage PH-03 sau khi WP-A3 được chấp nhận DONE
(`docs/reviews/PH-03-triage-smart-unlock-scope.md`)
Trạng thái: **CHƯA ÁP DỤNG — CHỜ PHÊ DUYỆT CỦA CHỦ DỰ ÁN**

Theo `governance/core/00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule", tài liệu này trình
bày thay đổi lộ trình **trước khi** thực hiện. Bảng roadmap chuẩn trong
`PROJECT/PROJECT_PROGRESS.md` **chưa bị sửa**, nên `PROJECT/LO_TRINH_DE_HIEU.md` vẫn đồng bộ với
nó. Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`. Không mở task nào.

---

## ROADMAP CHANGE PROPOSAL

### Reason

Triage PH-03 kết luận **DEFECT** và cấp finding chính thức **F-035** (severity **HIGH**,
evidence **E1**, xác nhận độc lập kế thừa từ reviewer E2-WP-A3-001).

`smart_reservable` so ngân sách Smart **theo tháng** với `deployed` **luỹ kế toàn đời**, nên từ
tháng thứ ba trở đi trả về `0` một cách **tất định, vĩnh viễn, không phụ thuộc dữ liệu** — kể cả
ở `SMART_UNLOCK = 1.00`. Hệ quả đo được:

- **2** Smart ladder trên **90** tháng; **99,98%** vốn Smart bỏ qua cơ chế ladder (ST §12) và
  chảy qua luật phần dư cuối tháng (ST §10);
- chiều `smart_unlock_mode` — **1 trong 8 chiều bắt buộc của Gate 2** (BT §9) — **trơ hoàn
  toàn**: ba mode HWM / NO_HWM / DECAY_HWM cho kết quả **trùng khít bit-for-bit**, trong khi
  ST §6 yêu cầu "báo cáo đóng góp riêng" của từng mode;
- snapshot eligible capital [F5] của Crash ladder bị triệt tiêu phần Smart, che khuất ~78% tác
  dụng thật của remediation F-021 vừa hoàn tất tại WP-A3.

Không có work package nào hiện sở hữu finding này: WP-A3 đã DONE với gate FROZEN; WP-A4 sở hữu
ngữ nghĩa dữ liệu xấu; WP-A6 sở hữu thứ tự xử lý. Vì vậy roadmap cần một mắt xích mới trên
đường găng.

### Affected tasks

| Task | Ảnh hưởng |
|---|---|
| **WP-A7** (MỚI) | Sở hữu F-035. Lớp A, nằm trên đường găng |
| WP-A5 | Thêm phụ thuộc vào WP-A7 (đo FS trên engine còn bóp vốn Smart sẽ sai — cùng lập luận đã dùng cho WP-A3) |
| WP-A6 | Thêm phụ thuộc vào WP-A7 (không khoá test thứ tự vào hành vi sắp đổi) |
| WP-C4 | Thêm phụ thuộc vào WP-A7 (không khoá parity vào hành vi sắp đổi) |
| GATE-A → T-06 | GATE-A chỉ đóng khi WP-A1…WP-A6 **và WP-A7** đều DONE |
| WP-A4 | **KHÔNG bị chặn** — chỉ cần tuần tự hoá thao tác trên `engine.py` (xem §10 của bản triage) |
| WP-A3 | **KHÔNG đổi.** Đã DONE, gate FROZEN, evidence vẫn đứng vững. Không nhét F-035 ngược vào |

### Dependency impact

Đường găng tới verdict dài thêm đúng một mắt xích:

```
TRƯỚC:  T-04 → WP-A3 ✅ → WP-A4 → WP-A6 → GATE-A → T-06 → WP-B1 → T-07
SAU:    T-04 → WP-A3 ✅ → { WP-A7, WP-A4 } → WP-A6 → GATE-A → T-06 → WP-B1 → T-07
                             ↑ WP-A7 và WP-A4 độc lập ngữ nghĩa, chỉ tuần tự hoá trên engine.py
```

- WP-A7 phụ thuộc: T-04 (DONE), WP-A3 (DONE — cùng chạm `engine.py`).
- WP-A7 chặn: WP-A5, WP-A6, WP-C4, GATE-A → T-06.
- WP-A7 song song an toàn với: WP-A1, WP-A2, WP-C1, WP-D1, WP-D2, và **WP-A4** (kèm điều kiện
  tuần tự hoá trên `engine.py`).
- BLK-001 **không** chặn WP-A7: toàn bộ kiểm chứng chạy được trên dữ liệu tổng hợp (DEC-003).

### Risk

| Rủi ro | Đánh giá |
|---|---|
| Không sửa trước T-06 | **Cao.** Verdict sẽ dựa trên engine mà 30% vốn không đi qua cơ chế được đặc tả và một chiều Gate 2 bắt buộc bị trơ. Master Index §6 cấm chạy lại official run để sửa |
| Sửa sai phạm vi | Trung bình. Có hai ranh giới ứng viên (PA-A / PA-B trong bản triage); chọn sai làm ngữ nghĩa unlock theo tháng trở nên gián tiếp. Giảm thiểu: bắt buộc ghi quyết định thiết kế và chứng minh chiều `smart_unlock_mode` hết trơ |
| Đổi kết quả mô phỏng | **Chắc chắn xảy ra và được chấp nhận** — nhưng phải định lượng và quy về điều khoản spec, đúng khuôn mẫu CHECK-A3-08 |
| Kéo dài đường găng | Chấp nhận được: đây là điều kiện hợp lệ của verdict, không phải tối ưu hoá |

### Recommended change

**Thêm đúng một dòng vào bảng roadmap chuẩn** (giữa WP-A6 và T-06 theo thứ tự lớp A):

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| PLANNED | WP-A7 | Sửa phạm vi kế toán của vốn Smart theo tháng | Vốn Smart hiện gần như không bao giờ đi qua cơ chế ladder từ tháng thứ ba, và một chiều bắt buộc của Gate 2 bị vô hiệu | D | max | Sau WP-A3 (DONE). Song song được với WP-A4 (tuần tự hoá trên `engine.py`). Chặn WP-A5, WP-A6, WP-C4, GATE-A (đóng F-035) |

Và cập nhật cột phụ thuộc của WP-A5, WP-A6, WP-C4 để thêm WP-A7; cập nhật định nghĩa GATE-A
thành `WP-A1…WP-A7 đều DONE`.

**Routing** (tính bằng `governance/scripts/governance/routing_engine.py`, không chọn bằng cảm
tính) — inputs `D3 R4 B3 A3 X3` / `U3 V4 H3 C3 F4`, category `accounting_financial`:

```
model_score  = 3.25 → base_tier D → Tier D (Fable)
               floors: cognitive:A>=3&X>=3, safety_business:min_C
effort_score = 3.45 → max
               floors: safety_business:min_high
warnings: none
```

**Phạm vi dự kiến của WP-A7** (sẽ được chốt và ĐÓNG BĂNG khi soạn file task, trước khi thực thi):

- Allowed: `src/eth_dca_os/capital.py`, `src/eth_dca_os/engine.py` (hai lời gọi
  `smart_reservable`), `tests/`, `docs/CONVENTIONS.md`.
- Out of scope: công thức `SMART_UNLOCK` và mọi ngưỡng (ST §4, §21); luật Month-End (ST §10);
  ngữ nghĩa dữ liệu xấu (WP-A4); thứ tự 18 bước (WP-A6); đo Failure Signal (WP-A5); parity JS
  (WP-C4); mọi thay đổi `docs/spec/`.
- Completion Gate phải bao gồm tối thiểu (soạn chi tiết sau khi phê duyệt): bằng chứng phạm vi
  tháng khớp DM §5; **chứng minh chiều `smart_unlock_mode` hết trơ** (ba mode cho kết quả phân
  biệt được — bài kiểm tra sống/chết của ST §6 + BT §9); bất biến kế toán DM §14 qua nhiều
  tháng; định lượng impact BEFORE/AFTER quy về điều khoản spec; toàn bộ suite PASS không nới
  lỏng test; **E2 độc lập** (category `accounting_financial`, Risk 4).

### Gate invalidation (DEC-009)

Remediation F-035 chắc chắn đổi capital allocation, ladder creation, execution count, deployed
capital và ETH accumulated ⇒ **chắc chắn ảnh hưởng Gate 1**.

Theo **DEC-009**: mọi kết quả Gate 1 tạo **trước** remediation F-035 là **STALE / INVALIDATED**.

Trạng thái hiện tại: **`no current result to invalidate`** — repo chưa từng có official run
(`results/` không tồn tại; BLK-001 vẫn mở). DEC-009 vì vậy áp dụng **phòng ngừa**: dependency
phải bảo đảm WP-A7 DONE **trước T-06**.

---

## Các phương án đã cân nhắc và loại bỏ

| Phương án | Vì sao loại |
|---|---|
| Nhét F-035 vào WP-A3 | WP-A3 đã DONE, Completion Gate FROZEN. Governance cấm mở lại task đã hoàn tất và cấm sửa gate đã đóng băng |
| Mở rộng WP-A4 | Khác requirement (ST §3 / BT §18 vs DM §5 / ST §4-§6-§12), khác file gốc (`score.py` vs `capital.py`); phải sửa gate đã FROZEN |
| Mở rộng WP-A6 | WP-A6 sở hữu **thứ tự** bước, không sở hữu **số tiền** tính ở bước 14; gate cũng đã FROZEN |
| Xếp lớp B (sau T-06) | Bị bác bằng dependency: F-035 làm một chiều Gate 2 bắt buộc trơ và làm 30% vốn không đi qua cơ chế đặc tả ⇒ chính official run mất hiệu lực |
| Defer (lớp D) | Bị bác: nằm trực tiếp trên đường găng tới T-06 |

---

## Cần chủ dự án quyết định

1. **Phê duyệt / từ chối RCP-002** (thêm WP-A7 vào roadmap chuẩn với routing D/Fable/max).
2. Nếu phê duyệt: cho phép soạn file định nghĩa WP-A7 và **đóng băng** Ready Gate + Completion
   Gate (bước tương đương T-04) **trước khi** thực thi.
3. Thứ tự thực thi mong muốn giữa **WP-A7** và **WP-A4** (cả hai đều READY-able; triage kết luận
   WP-A4 không bị chặn, chỉ cần tuần tự hoá thao tác trên `engine.py`).

Không tự áp dụng. Không mở task remediation cho tới khi có phê duyệt.
