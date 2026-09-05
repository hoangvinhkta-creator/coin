# S028 — Canonicalize Owner-Run RQ Replay Evidence (T-07 SPIKE, DEC-039)

Ngày: 2026-09-05. Nhánh: `claude/t-07-decision-prep-1oprq1` (tiếp nối `S027`).

## 1. Bối cảnh

`S027` đã thiết kế và smoke-test một script REPLAY (RQ-1/RQ-3/RQ-4) trên dataset SYNTHETIC, và
đưa ra hướng dẫn cho Owner chạy trên dataset official T-06 đã bảo toàn. Owner đã chạy đúng script
đó (không sửa) trên máy có dataset official và trả lại toàn văn stdout.

## 2. Việc đã làm

1. **Xác nhận nội dung có thật** trước khi xử lý — không canonicalize placeholder/text giả định
   (một lượt trước đó bị từ chối vì message chỉ chứa `[PASTE THE COMPLETE OUTPUT HERE]` chưa điền
   — không có hành động nào được thực hiện ở lượt đó, đúng nguyên tắc "narrative does not move
   state").
2. **Kiểm tra nhất quán nội bộ** trên output thật nhận được (không tính lại engine, thuần đối
   chiếu số học): `SMOKE_MODE=false`; `STEP_0` đúng chuỗi PASS; 10/10 boolean `beats_f`/`beats_g`
   tái tính khớp với `v2_eth`/`control_*_p95`; tổng ETH theo nguồn (`SMART+BASE+OPPORTUNITY+CRASH
   = 14,910758150139898`) khớp `1,78×10⁻¹⁵` với `v2_eth` aggregate đã biết từ `CHECK-B1-03`
   Addendum 3 (`14,910758150139896`) — xác nhận độc lập ngoài kế hoạch của script, không có mâu
   thuẫn nào giữa các block.
3. **Bảo toàn evidence thô**: `docs/reviews/T07-RQ-REPLAY-EVIDENCE-RECORD.md` (mới) — toàn văn
   JSON verbatim + bảng 8 phép kiểm nhất quán, dán nhãn REPLAY EVIDENCE / OWNER-RUN / OFFICIAL
   T-06 DATASET / NOT A NEW OFFICIAL T-06 RUN, tách khỏi diễn giải.
4. **Tái đánh giá** `docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md`: cập nhật §1 (RQ-2), §2
   (RQ-5), §3 (RQ-1), §4 (RQ-3), §5 (RQ-4) với số liệu thật; thêm §9 (tóm tắt định lượng bắt
   buộc — đếm window, so sánh OOS bốn phép, giải thích vì sao aggregate-thắng và
   per-window/OOS-đa-số-thua không mâu thuẫn — khác phạm vi `run_engine`: một run liên tục so
   với chín run độc lập reset + một run OOS riêng, đúng phương pháp luận multi-anchor BT §4.1)
   và §10 (Decision Impact — làm rõ evidence WEAKENS giả thuyết timing edge ổn định, PARTIALLY
   SUPPORTS giả thuyết capital-allocation mismatch, không đổi bất kỳ fact đóng băng nào).

## 3. Kết quả định lượng chính (đầy đủ tại §9 của investigation doc)

- Control F P95: **2/9** window pre-OOS thắng (`W1`, `W4`).
- Control G P95: **3/9** window pre-OOS thắng (`W1`, `W4`, `W6` — biên rất mỏng).
- `OOS`: thua CẢ HAI control ở CẢ median lẫn P95 (bốn phép so, bốn thua).
- `SMART`/`BASE`/`OPPORTUNITY`/`CRASH`: `OPPORTUNITY+CRASH` gộp = 1,56 % tổng nominal, 3,20 %
  tổng ETH, giá mua bình quân thấp hơn rõ rệt (294,55/345,37 so với 603,78/648,16).
- Opportunity pool: `mean_idle_ratio=0,5917` (59,17 % CAP CỦA RIÊNG pool đó — KHÔNG phải 59,17 %
  tiền mặt toàn danh mục; cash toàn danh mục = `0,0369`, một đại lượng hoàn toàn khác).
- Tương quan quan sát (KHÔNG nhân quả) cash_ratio × AE theo 9 window: Pearson `+0,546`,
  Spearman `+0,5`.

## 4. Phân loại RQ sau cùng

| RQ | Trạng thái |
|---|---|
| RQ-1 (nhân quả) | NOT ESTABLISHED (không đổi — ngoài phạm vi, cần counterfactual) |
| RQ-1 (tương quan) | có số liệu, không nhân quả — không nâng cấp |
| RQ-2 | PARTIALLY ESTABLISHED (thu hẹp — xem §1.1) |
| RQ-3 | ESTABLISHED (như REPLAY evidence) |
| RQ-4 | PARTIALLY ESTABLISHED |
| RQ-5 | PARTIALLY ESTABLISHED (cả hai vế cùng nhận thêm bằng chứng) |

## 5. Trạng thái giữ nguyên (không đổi)

`T-07 = READY` (không transition); `DEC-039`/`L-0` không đổi; `official verdict = DO_NOT_BUILD`;
`V2.1.5 validation = FAILED`; `can_proceed_to_app = false`; `T-11 = BLOCKED`; `DEC-005 = PENDING`.
Không chọn L-1/L2 thay Owner. Không chọn objective A/C. Không sửa `src/`/`tests/`/`webapp/`.
Không rerun `T-06`, không đổi/ghi đè official artifact. Không mở `T-11`/`WP-D2`. Không resolve
`DEC-005`. Không tạo task ID mới.

Production diff = EMPTY (`git diff 53a63c4 -- src/eth_dca_os webapp pyproject.toml pyproject.lock
tests` rỗng). Thay đổi: `docs/reviews/T07-RQ-REPLAY-EVIDENCE-RECORD.md` (mới),
`docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` (cập nhật), `PROJECT/PROJECT_PROGRESS.md`
(narrative), `PROJECT/LO_TRINH_DE_HIEU.md` (regenerate).

Validators: `sync_easy_roadmap.py`, `validate_easy_roadmap.py`, `validate_governance.py`,
`validate_structure.py`, `validate_project_state.py`, `validate_routing.py`,
`branch_authority_check.sh` — tất cả PASS.

## 6. Bước tiếp theo

Quay lại `T-07`: Owner chọn giữa L-1 (benchmark đơn giản hơn) và L-2 (mở V2.2) với evidence đã
sắc nét hơn đáng kể (`docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` §10). Quyết định đó vẫn
PENDING, không được đưa ra ở bất kỳ phiên nào cho tới nay.
