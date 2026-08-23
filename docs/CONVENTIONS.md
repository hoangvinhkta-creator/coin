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
4. **Opportunity daily limit** (20%/ngày): với ladder Smart/Opportunity thường, áp tại thời
   điểm tạo reservation mới trong ngày; deployment qua zone đã reserve từ ngày trước không bị
   chặn lại. Với **Crash zone** (vốn được reserve toàn phần tại crash entry theo [F5]), limit
   được cưỡng chế ở **khâu triển khai** — bước 14, thời điểm engine cam kết tạo action: phần
   vốn OPPORTUNITY của zone so với headroom còn lại trong ngày (20% × Opportunity Fund total
   − đã dùng trong ngày). Zone vượt headroom bị chặn nguyên tử (không partial), log
   `DAILY_LIMIT_BLOCK`, giữ TRIGGERED và xét lại cycle sau (cùng cơ chế với max_zones §15.1);
   phần đã cam kết không được hoàn lại headroom nếu action sau đó MISSED (bảo thủ theo BT §1).
   (Sửa tại WP-A3 — trước đó limit bị áp cả vào snapshot [F5], xem F-021.)
5. **Crash ladder funding**: eligible snapshot [F5] = **Smart AVAILABLE + Opportunity
   AVAILABLE (đã unlock, chưa nằm trong reservation nào)** đo ngay sau khi cancel/release
   Opportunity zone xung đột — KHÔNG áp daily limit vào snapshot (đúng nghĩa đen ST §14;
   sửa F-021 tại WP-A3). Reserve của mỗi Crash zone được rút **Opportunity trước, Smart sau**
   (ghi map zone → (pool, amount) để release/deploy đúng nguồn).
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
14. **Tách trạng thái nền và nhãn dẫn xuất** (quyết định thiết kế WP-A3, subtask A3.1 —
    đóng F-001): Strategy §16 liệt kê STRESSED trong enum Market Regime nhưng §17.3 [F1]
    định nghĩa nó là nhãn dẫn xuất chỉ dùng reporting; spec để ngỏ việc nhãn có được gộp
    vào trạng thái nền hay không. Engine chốt: `RegimeTracker.state` là trạng thái nền
    (chỉ NORMAL/CRASH/RECOVERY — máy trạng thái §17.1–§17.2), `RegimeTracker.label`
    (alias `regime`) là nhãn báo cáo theo enum §16. **Mọi quyết định execution trong
    engine chỉ đọc `state`**; `label` chỉ xuất hiện trong purchase record và phân rã
    counter theo regime (BT §16). Nhờ đó [F1] được bảo đảm bằng cấu trúc: không tồn tại
    đường code nào để nhãn STRESSED ảnh hưởng unlock/ladder/cooldown/limit/execution.
15. **Dữ liệu thiếu trong transition regime** (đóng F-022): điều kiện enter/exit/nhãn chỉ
    được coi là thoả khi có dữ liệu THẬT chứng minh (BT §1 — giả định bảo thủ; ST §3 —
    dữ liệu xấu không được đẩy trạng thái theo hướng có lợi). `None` không bị ép về 0.0.
    Với điều kiện exit "liên tục trong 48h" (§17.2): một quan sát thiếu dữ liệu phá chuỗi
    liên tục (reset đồng hồ exit-candidate). Mỗi vế của điều kiện OR (entry, STRESSED)
    đánh giá độc lập trên dữ liệu thật của vế đó.
16. **Pool label của Crash ladder cho tie-break §15.1 [F2]** (đóng F-030): spec xếp Crash
    ladder "theo pool nguồn vốn của nó, sau Smart/Opportunity thường" nhưng không định
    nghĩa trường hợp vốn pha trộn hai pool. Engine chốt: label của cả ladder (gán cho mọi
    zone của nó, để zone_index giữ đúng thứ tự trong cùng ladder) = pool cấp **đa số**
    tổng reserve tại thời điểm tạo; hoà → OPPORTUNITY. Khoá sắp thứ tự đầy đủ:
    `(pool_rank, is_crash, created_at, zone_index)` — crash ladder đứng sau ladder thường
    cùng pool; hạch toán release/deploy vẫn theo map (pool, amount) thật của từng zone,
    không theo label.
