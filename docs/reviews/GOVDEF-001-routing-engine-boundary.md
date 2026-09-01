# GOVDEF-001 — Sai số biên dấu phẩy động trong routing_engine.py

**LƯU Ý PHẠM VI:** đây là defect của **công cụ governance dùng chung**
(`governance/scripts/governance/routing_engine.py`), **không phải finding của sản phẩm
ETH DCA**. Không tính vào 33 finding của S001 (`docs/reviews/S001-audit-findings.md`).
Không gộp vào compliance matrix S001.

Phát hiện: 2026-08-23, trong quá trình áp dụng RCP-001 (routing các work package remediation).
Trạng thái: **RESOLVED — 2026-08-23, tại `MICRO-GOVDEF-001`** (chủ dự án phê duyệt PA-1 cho
DEC-010). Xem mục "Resolution" ở cuối tài liệu này.

## Severity
MEDIUM (theo `governance/audit/AUDIT_FINDINGS_TEMPLATE.md` — "Meaningful weakness with bounded
impact"). Hệ quả là chọn sai một bậc Tier/Effort tại đúng biên, không phải sai kết quả tính toán
nghiệp vụ của bất kỳ dự án nào dùng công cụ này.

## Category
Tooling / Governance infrastructure

## Affected Area
`governance/scripts/governance/routing_engine.py:10-11`

```python
def tier_from_score(s): return 'A' if s < 1 else 'B' if s < 2 else 'C' if s < 3 else 'D'
def effort_from_score(s): return 'low' if s < .8 else 'medium' if s < 1.6 else 'high' if s < 2.4 else 'xhigh' if s < 3.2 else 'max'
```

## Current Behavior

`route()` tính `model_score` bằng tổng có trọng số của năm số nguyên 0–4:
```python
ms = .25*D + .25*R + .20*B + .15*A + .15*X
```
rồi so sánh trực tiếp giá trị dấu phẩy động chưa làm tròn với các mốc nguyên 1, 2, 3 để chọn
Tier. Kết quả in ra màn hình (`json.dumps(..., indent=2)` sau `round(ms, 3)`) đã làm tròn, nhưng
**quyết định Tier dùng giá trị chưa làm tròn**.

## Expected Behavior

Theo `governance/core/AGENT_CAPABILITY_MATRIX.md`, bảng "Base routing":

| MODEL_SCORE_BASE | Tier |
|---|---|
| 0.00–0.99 | A |
| 1.00–1.99 | B |
| 2.00–2.99 | C |
| 3.00–4.00 | D |

Một điểm số **hiển thị đúng bằng 2.0** phải rơi vào Tier C. Công cụ phải cho kết quả nhất quán
với giá trị mà chính nó hiển thị cho người đọc.

## Evidence — E1, tái lập được

Trường hợp kích hoạt: WP-A2 trong RCP-001, với đầu vào `D=2, R=2, B=2, A=1, X=3`.

```
$ python3 -c "
D,R,B,A,X = 2,2,2,1,3
ms = .25*D+.25*R+.20*B+.15*A+.15*X
print('giá trị float thật :', repr(ms))
print('hiển thị round(,3) :', round(ms,3))
print('router tier_from_score  :', 'A' if ms<1 else 'B' if ms<2 else 'C')
"
giá trị float thật : 1.9999999999999998
hiển thị round(,3) : 2.0
router tier_from_score  : B
```

Chạy trực tiếp `routing_engine.py` xác nhận cùng kết quả:

```
$ python3 governance/scripts/governance/routing_engine.py --d 2 --r 2 --b 2 --a 1 --x 3 \
    --u 1 --v 3 --h 2 --c 3 --f 2
{
  "routing_status": "ROUTED",
  "model_score": 2.0,
  "base_tier": "B",
  "tier": "B",
  "model": "Sonnet",
  ...
}
```

`model_score` hiển thị `2.0` — theo bảng routing đây phải là Tier C — nhưng `tier`/`base_tier`
trả về `B`.

## Risk

Bất kỳ task nào (không riêng dự án này, vì `routing_engine.py` là công cụ dùng chung theo
AI Engineering Constitution) có tổ hợp D/R/B/A/X cho tổng dấu phẩy động rơi đúng vào một trong
ba mốc nguyên 1.0, 2.0, 3.0 đều có nguy cơ bị lệch một bậc Tier — theo cả hai chiều tuỳ dấu của
sai số làm tròn nhị phân (có thể under-route hoặc over-route). Với các mốc hard floor trong
`AGENT_CAPABILITY_MATRIX.md` neo vào đúng các số nguyên này (`A>=3`, `X>=3`, `D>=4`...), hiệu ứng
tương tự có thể ảnh hưởng tới cognitive-complexity floor và effort floor, không chỉ base tier.

`effort_from_score` dùng cùng mẫu so sánh với các mốc `.8, 1.6, 2.4, 3.2` — dễ bị ảnh hưởng hơn
vì các mốc không phải số nguyên tròn, nhưng cùng một lớp lỗi.

## Likely Cause

Phép cộng dấu phẩy động (`0.25*D + 0.25*R + ...`) không đảm bảo cho kết quả đúng bằng số nguyên
kỳ vọng ngay cả khi các số hạng là bội số "tròn" theo thập phân — đây là hạn chế cố hữu của biểu
diễn nhị phân IEEE 754, không phải lỗi logic công thức. So sánh `<` trực tiếp trên giá trị chưa
xử lý sai số là nguyên nhân trực tiếp.

## Recommended Fix — KHÔNG thực hiện ở đây

Tổng quát hoá cách so sánh, ví dụ một trong hai hướng:
1. Làm tròn `ms`/`es` về cùng độ chính xác với giá trị hiển thị (`round(ms, 3)`) **trước khi**
   so sánh với mốc, rồi so sánh trên giá trị đã làm tròn.
2. Dùng epsilon nhất quán với cách các module khác trong codebase đã xử lý sai số dấu phẩy động
   (ví dụ `EPS = 1e-6` ở `src/eth_dca_os/capital.py:11`), ví dụ so sánh `s < 2 - EPS` thay vì
   `s < 2`.

**Ràng buộc bắt buộc từ chủ dự án:** giải pháp phải tổng quát, áp dụng cho mọi tổ hợp đầu vào,
**không hard-code ngoại lệ riêng cho WP-A2** hay bất kỳ task cụ thể nào. Cùng một lớp sửa nên áp
dụng cho cả `tier_from_score` và `effort_from_score`.

## Suggested Task
`MICRO-GOVDEF-001` — xem `PROJECT/PROJECT_PROGRESS.md` mục "Micro Tasks (Inline)".

## Dependencies
Không phụ thuộc finding nào của S001. Độc lập với 15 work package của RCP-001.

## Status
**RESOLVED** — 2026-08-23, tại `MICRO-GOVDEF-001`. Xem mục "Resolution" bên dưới.

## Verification Required
- Test bổ sung cho `routing_engine.py` (hoặc script kiểm chứng tương đương) khẳng định mọi tổ
  hợp D/R/B/A/X mà tổng có trọng số **hiển thị** đúng bằng 1.0, 2.0, hoặc 3.0 đều route vào Tier
  ở cận trên của mốc đó (ví dụ hiển thị 2.0 → Tier C), không phải cận dưới.
- Xác nhận không có task nào trong RCP-001 hay S001 bị route sai theo hướng ngược lại (over-route)
  do cùng lớp lỗi này — soát lại toàn bộ bảng routing ở `PROJECT_PROGRESS.md` mục "Routing sơ bộ"
  sau khi sửa.
- Không giới thiệu ngoại lệ hard-code nào trong diff sửa lỗi.

---

## Resolution — MICRO-GOVDEF-001 (2026-08-23)

Chủ dự án phê duyệt **PA-1** cho DEC-010: sửa `routing_engine.py` một cách tổng quát và cập nhật
`validate_routing.py` để chấp nhận manual override có ghi nhận.

### Root cause xác nhận lại (E1, trước khi sửa)

Tái lập đúng như tài liệu này mô tả:

```
$ python3 -c "
D,R,B,A,X = 2,2,2,1,3
ms = .25*D+.25*R+.20*B+.15*A+.15*X
print('raw:', repr(ms)); print('round3:', round(ms,3))
print('tier via s<2:', 'B' if ms<2 else 'C')
"
raw: 1.9999999999999998
round3: 2.0
tier via s<2: B
```

### Cách sửa

**`routing_engine.py`** — áp dụng phương án 1 đã đề xuất trong tài liệu này ("làm tròn `ms`/`es`
về cùng độ chính xác với giá trị hiển thị trước khi so sánh với mốc"): thêm hằng số
`SCORE_DECIMALS = 3` và làm tròn `model_score`/`effort_score` **một lần, ngay sau khi tính**, rồi
dùng đúng giá trị đã làm tròn đó cho cả hiển thị lẫn mọi so sánh biên (`tier_from_score`,
`effort_from_score`). Không còn hai nguồn sự thật (một giá trị hiển thị, một giá trị dùng để quyết
định) như trước.

Căn cứ toán học cho việc làm tròn 3 chữ số là an toàn tuyệt đối, không phải epsilon tuỳ tiện: các
trọng số (`.25/.20/.15` cho model_score; `.20/.20/.15/.25` cho effort_score) đều có tối đa 2 chữ số
thập phân, nhân với số nguyên 0–4, nên giá trị toán học **chính xác** của mọi tổng có trọng số luôn
có tối đa 2 chữ số thập phân có nghĩa. Sai số biểu diễn nhị phân IEEE-754 chỉ ở bậc 1e-15 đến 1e-16
— nhỏ hơn chữ số thập phân thứ 3 hơn mười bậc độ lớn. Làm tròn 3 chữ số vì vậy chỉ loại bỏ đúng
phần nhiễu, không bao giờ đổi giá trị thật.

**`validate_routing.py`** — bổ sung cơ chế xác minh manual override tổng quát (hàm `check_override`),
áp dụng cho **mọi** task tương lai, không riêng WP-A2:

1. Yêu cầu trường `Manual Override: YES — DEC-###` (regex `DEC-\d{3,4}`, không hard-code số nào).
2. Yêu cầu `DEC-###` đó tồn tại như một heading `## DEC-###` thật trong `PROJECT/PROJECT_DECISIONS.md`
   — override phải được governance ghi nhận, không chỉ tự khai trong file task.
3. Yêu cầu trường `Router Raw Output:` khớp **chính xác** với kết quả `routing_engine.route()` tính
   lại ngay tại thời điểm kiểm tra, từ đúng `Routing Inputs` của file — chặn override dựa trên baseline
   giả mạo hoặc lỗi thời.
4. Yêu cầu override chỉ được **leo thang** (Tier/Effort cao hơn router), không bao giờ được hạ thấp —
   cùng triết lý với cơ chế floor sẵn có (`max_tier`/`max_eff` chỉ nâng, không hạ).

Nếu bất kỳ điều kiện nào ở trên không thoả, validator **FAIL** với lý do cụ thể — không im lặng bỏ
qua và không coi override là hợp lệ mặc định.

### Kết quả cho WP-A2

Sau khi sửa `routing_engine.py`, chạy lại router với đúng Routing Inputs của WP-A2
(D=2, R=2, B=2, A=1, X=3; U=1, V=3, H=2, C=3, F=2):

```
{
  "model_score": 2.0, "base_tier": "C", "tier": "C", "model": "Opus",
  "effort_score": 2.15, "effort": "high"
}
```

WP-A2 nay route **Tier C tự nhiên**, không cần nhánh manual override nữa — đúng như DEC-008 mục
"Can Revisit After" đã dự đoán. File `docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md` **giữ
nguyên** `Manual Override: YES — DEC-008`, `Router Raw Output` (giá trị thô trước fix) và toàn bộ
dấu vết governance khác — không xoá gì, chỉ bổ sung ghi chú cập nhật. `validate_routing.py` chạy
trên toàn bộ 16 file MAJOR task hiện có cho:

```
ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual override(s))
```

(0 override được chấp nhận vì WP-A2 không còn mismatch để cần override — nhưng cơ chế
`check_override` đã được kiểm chứng độc lập bằng test tổng hợp, xem
`governance/scripts/governance/test_routing_engine.py`.)

### Regression

Quét toàn bộ không gian đầu vào hợp lệ (5^5 = 3125 tổ hợp cho model_score, 3125 cho effort_score):
**0** trường hợp còn lệch giữa giá trị hiển thị và Tier/Effort quyết định, ở cả hai công thức.

Trong 16 file task MAJOR hiện có của repo, đối chiếu routing trước/sau fix: **đúng một dòng thay
đổi** — WP-A2, Tier B → C. Không task nào khác đổi Tier hay Effort. Danh sách đầy đủ trước/sau nằm
trong evidence của `MICRO-GOVDEF-001` (`docs/tasks` session log).

### Không hard-code ngoại lệ

Xác nhận: diff không chứa bất kỳ so sánh nào tham chiếu tới `WP-A2`, `DEC-008`, hay bất kỳ task ID
cụ thể nào trong `routing_engine.py`. Cơ chế làm tròn áp dụng đồng nhất cho mọi input. Cơ chế
override trong `validate_routing.py` cũng tổng quát — nó chấp nhận **bất kỳ** `DEC-###` hợp lệ nào,
không riêng DEC-008.

### Governance defect

**Đã đóng.** Không còn ảnh hưởng tới bất kỳ task nào khác trong repo (xác nhận bằng quét toàn bộ
16 file MAJOR + brute-force toàn không gian đầu vào).
