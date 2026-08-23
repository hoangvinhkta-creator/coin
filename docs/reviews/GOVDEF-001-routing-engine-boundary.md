# GOVDEF-001 — Sai số biên dấu phẩy động trong routing_engine.py

**LƯU Ý PHẠM VI:** đây là defect của **công cụ governance dùng chung**
(`governance/scripts/governance/routing_engine.py`), **không phải finding của sản phẩm
ETH DCA**. Không tính vào 33 finding của S001 (`docs/reviews/S001-audit-findings.md`).
Không gộp vào compliance matrix S001.

Phát hiện: 2026-08-23, trong quá trình áp dụng RCP-001 (routing các work package remediation).
Trạng thái: OPEN. Chưa sửa — theo chỉ thị của chủ dự án, không sửa `routing_engine.py` trong
bước áp dụng roadmap change.

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
OPEN

## Verification Required
- Test bổ sung cho `routing_engine.py` (hoặc script kiểm chứng tương đương) khẳng định mọi tổ
  hợp D/R/B/A/X mà tổng có trọng số **hiển thị** đúng bằng 1.0, 2.0, hoặc 3.0 đều route vào Tier
  ở cận trên của mốc đó (ví dụ hiển thị 2.0 → Tier C), không phải cận dưới.
- Xác nhận không có task nào trong RCP-001 hay S001 bị route sai theo hướng ngược lại (over-route)
  do cùng lớp lỗi này — soát lại toàn bộ bảng routing ở `PROJECT_PROGRESS.md` mục "Routing sơ bộ"
  sau khi sửa.
- Không giới thiệu ngoại lệ hard-code nào trong diff sửa lỗi.
