# Quy ước triển khai (implementation conventions)

Những điểm dưới đây spec V2.1.5 không quy định chi tiết; engine chốt quy ước như sau
(đều là chi tiết triển khai, không đổi hypothesis; nếu muốn nâng thành spec thì đưa vào V2.2):

1. **Thời điểm tạo Smart ladder**: tạo khi (a) chưa có Smart ladder ACTIVE trong tháng,
   (b) daily score hợp lệ và effective SMART_UNLOCK > 0, (c) trước hoặc bằng Day 24,
   (d) data quality không INVALID. Anchor = OPEN của nến 15m hiện tại (giá có thể thực thi).
2. **Thời điểm tạo Opportunity ladder**: khi hysteresis ACTIVE, OPPORTUNITY_UNLOCK > 0,
   chưa có Opportunity ladder ACTIVE, data quality không INVALID.
3. **Reservation**: zone reserve target_vnd ngay khi ladder được tạo (Strategy §8 "Tạo zone /
   reservation"), trong giới hạn vốn reservable tại thời điểm đó; zone không reserve đủ
   target thì giữ phần reserve được và target_vnd co về phần đó (không reserve vốn chưa unlock).
4. **Opportunity daily limit** (20%/ngày): áp tại thời điểm tạo reservation mới trong ngày;
   deployment qua zone đã reserve từ ngày trước không bị chặn lại.
5. **Crash ladder funding**: eligible snapshot [F5] = Smart reservable + Opportunity reservable
   ngay sau khi cancel/release Opportunity zone xung đột. Reserve của mỗi Crash zone được rút
   **Opportunity trước, Smart sau** (ghi map zone → (pool, amount) để release/deploy đúng nguồn).
6. **Cooldown**: trong cooldown, zone bị xuyên vẫn chuyển TRIGGERED nhưng không tạo action;
   được xét lại ở nến sau khi cooldown hết hoặc khi cooldown override kích hoạt
   (CurrentPrice <= LastExecutionPrice × (1−7%)). Đếm override theo regime.
7. **Month-End**: Day 25 12:00 local settle 50% phần Base còn lại; Day 28 12:00 settle 100%
   phần còn lại. Smart leftover xử lý tại Day 28 12:00 theo OSCORE (≥45: mua hết;
   <45: mua 50%, chuyển 50% vào Opportunity Fund trong giới hạn cap; phần vượt cap — nếu có —
   được mua nốt để bảo toàn "Base/Smart giải ngân trong tháng").
8. **Funding delay**: ON_DEMAND → mọi zone action cần funding (treasury không giữ USDT sẵn),
   funding_delay áp toàn phần; BULK_MONTHLY → funding_delay = 0 (pre-funded).
9. **DEGRADED và unlock**: khi data quality DEGRADED, OPPORTUNITY_UNLOCK ngày đó không được
   vượt giá trị unlock hợp lệ gần nhất (unlock không tăng do đầu vào DEGRADED).
10. **Contribution schedule**: mỗi accounting month bơm đúng một contribution danh nghĩa
    bằng nhau (mặc định 100 đơn vị) tại nến đầu tiên của tháng; mọi benchmark dùng đúng
    cùng lịch này (equal capital rule, Backtest §12.1).
11. **Đơn vị danh nghĩa**: theo Backtest §2.1 [F6], backtest chạy 1 USDT = 1 đơn vị; trường
    *_vnd trong engine mang giá trị danh nghĩa này.
12. **Window run**: mỗi gate window chạy engine độc lập (state mới, contribution bắt đầu từ
    tháng đầu window) — window là một backtest 24 tháng tự đứng.
13. **Behavioral LOCAL_HOUR**: delay bốc thăm theo phân phối Backtest §6 cho từng action;
    nhánh "xử lý sáng 07:00" đặt execute tại OPEN nến 15m đầu tiên tại/sau 07:00 local
    nếu còn TTL, ngược lại MISSED.
