# Release Integrity Check — V2.1.5

Thực hiện theo Implementation Plan §8 (sáu bước bắt buộc) trước khi đánh dấu V2.1.5 là ACTIVE.
Ngày kiểm: 2026-08-22. Người kiểm: AI coding agent (Claude Code), theo yêu cầu của chủ dự án.

## Bước 1 — Mở Section Inventory hiện tại

Dùng 06_SECTION_INVENTORY_V2_1_5.md (danh mục đầy đủ, không phải danh sách audit findings).

## Bước 2 — Xác nhận từng dòng inventory tồn tại

| Tài liệu | Số mục inventory | Kết quả |
|---|---|---|
| 00 Master Index | 6 (MI-1..MI-6) | ĐỦ — 6/6 section |
| 01 Product Spec | 14 (PR-1..PR-14) | ĐỦ — 14/14 section |
| 02 Strategy Spec | 24 (ST-1..ST-24, tăng 2 do §15.1 [F2] và §17.3 [F1]) | ĐỦ — 24/24 |
| 03 Backtest Spec | 23 (BT-1..BT-23, tăng 1 do §2.1 [F6]) | ĐỦ — 23/23 |
| 04 Data Model | 14 (DM-1..DM-14) | ĐỦ — 14/14 |
| 05 Implementation Plan | 9 (IM-1..IM-9) | ĐỦ — 9/9 |

## Bước 3 — Deliberate Removals

Không có mục nào bị xóa. Bảng Deliberate Removals của 06 ghi "(không có)". ĐẠT.

## Bước 4 — Đối chiếu cơ học heading giữa V2.1.4 và V2.1.5

Chạy script trích text V2.1.4 (.docx) và V2.1.5 (.md), so sánh danh sách heading cấp 1 theo số section:

| Tài liệu | Heading V2.1.4 | Heading V2.1.5 | Heading biến mất |
|---|---|---|---|
| 00 | 6 | 6 | 0 |
| 01 | 14 | 14 | 0 |
| 02 | 21 | 21 (+2 sub-section mới 15.1, 17.3) | 0 |
| 03 | 22 | 22 (+1 sub-section mới 2.1) | 0 |
| 04 | 14 | 14 | 0 |
| 05 | 9 | 9 | 0 |
| 06 | 9 | 9 | 0 |

Không heading nào biến mất. Các mục mới đều là sub-section được changelog §4 khai báo (F1, F2, F6). ĐẠT.

## Bước 5 — Tham số tham chiếu chéo có định nghĩa

- Mọi chiều lưới Gate 2 (base_pct, opportunity_pct, opportunity_cap_months, cooldown_hours, cooldown_override_pct, smart_spacing_factor, score weights, smart_unlock_mode) có ngữ nghĩa tại Strategy §4, §7, §15, §11, §1, §6. ĐẠT.
- Mọi chiều ma sát Gate 3 (user_delay, funding_policy, funding_delay, spot_fee, slippage) có field tương ứng trong execution_config (Data Model §3). ĐẠT.
- STRESSED (mới ở F1) được định nghĩa tại Strategy §17.3 trước khi được dùng ở Backtest §16. ĐẠT.

## Bước 6 — Baseline config khớp schema

Strategy §21: 20 field baseline. Data Model §2: 23 field schema. Chênh đúng ba field metadata (config_name, created_at, strategy_config_hash) theo quy tắc [F7]/XC-1. ĐẠT.

## Kiểm bổ sung XC-8 (con số trong bảng đếm)

- OFAT Gate 2: (3−1)+(3−1)+(4−1)+(3−1)+(3−1)+(3−1)+(5−1)+(3−1) = 2+2+3+2+2+2+4+2 = 19. Loại đúng 1 (base_pct 0.70 + opportunity_pct 0.20 → smart_pct 0.10 < 0.15) → 18 hợp lệ. Denominator = 1+18+200 = 219. KHỚP.
- Gate 3 OFAT: 3 (user_delay) + 3 (funding_delay) + 3 (spot_fee) + 3 (slippage) + 1 (cặp BULK, delay 0) + 1 baseline = 14. Tổng manifest = 14 + 100 = 114. KHỚP.
- Window: anchor +0M → 3 block; +6M/+12M/+18M → 2 block mỗi anchor; tổng 9. Không block nào kết thúc sau 2024-12-31. KHỚP.

Các con số này sẽ được kiểm lại lần nữa bằng unit test của manifest generator và window selector (Backtest §21.4).

## Kết luận

Cả sáu bước ĐẠT. V2.1.5 đủ điều kiện đánh dấu **ACTIVE / SOURCE OF TRUTH**.
