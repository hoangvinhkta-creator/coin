# ETH DCA Operating System V2.1.5 — Implementation Plan

**BACKTEST-FIRST • HARD STOPPING RULES • RELEASE INTEGRITY PROCEDURE**

## 1. Nguyên tắc

- Không build dashboard hoặc full app trước khi research prototype hoàn thành và verdict cho phép.
- V2.1.5 là source of truth duy nhất. Không kế thừa ngầm bất kỳ điều gì từ V1, V2.0, V2.1, V2.1.1, V2.1.2, V2.1.3 hay V2.1.4.
- Ưu tiên tính đúng đắn của strategy engine trước khi làm UI đẹp.
- Live và backtest phải reuse cùng một core strategy function.

## 2. Phase 0 — Freeze

- Chạy Release Integrity Procedure ở §8 trên toàn bộ Section Inventory TRƯỚC khi viết dòng code đầu tiên.
- Commit baseline strategy_config (Strategy §21) và hai execution_config: Gate 1 low-friction và Gate 3 realistic.
- Sinh và đóng băng Gate 2 manifest theo thuật toán ở Backtest §9.1; lưu hash và số lượng thực tế.
- Sinh và đóng băng Gate 3 friction manifest theo Backtest §10.1; lưu hash.
- Đóng băng thuật toán chọn cửa sổ multi-anchor, ngày bắt đầu OOS 2025-01-01, dataset end date và dataset hash.
- Đóng băng master_seed = 42 và seed = 43 cho sampling ma sát của Gate 3.
- Đóng băng toàn bộ ngưỡng của Gate 1, Gate 2, Gate 3 và danh sách Failure Signal FS-01..FS-12.

## 3. Các phase triển khai

| Phase | Nội dung |
|---|---|
| 1 — Data pipeline | Tải và chuẩn hóa Binance ETHUSDT/BTCUSDT 1D và ETHUSDT 15m. Kiểm tra gap và timezone. Lưu raw parquet bất biến và processed riêng. Tính dataset hash và lineage. |
| 2 — Score engine | Cài đặt D/M/P/R/S7/V/W/RP và OSCORE đúng công thức. Unit test ScoreMultiplier piecewise và O0/O4 endpoints. Sinh correlation, VIF, score distribution và ablation. Diagnostic volume z-score — KHÔNG thay factor production. |
| 3 — Capital & ladder | Monthly budget, Opportunity cap và overflow, Base schedule, Month-End. Ledger AVAILABLE/RESERVED/DEPLOYED. Smart, Opportunity và Crash ladder với đầy đủ zone lifecycle. Ba mode HWM. Execution limit, cooldown và override. |
| 4 — Manual/P2P simulator | User delay và funding delay tất định. Trạng thái FUNDING_REQUIRED. TTL và missed action. Behavioral local-hour chỉ cho Gate 3. ON_DEMAND vs BULK_MONTHLY. Stress scenario P2P unavailable trong Crash. |
| 5 — Benchmarks & controls | A Monthly, B Weekly, C Simple Dip Reserve (chu kỳ theo [F4]), D MA200 với reserve cap 6C. Random Timing N=1000 và Random Anchor N=1000 dưới dạng lightweight replay. Kiểm tra bất biến equal external contribution. |
| 6 — Gate 1 + OOS | Chạy low-friction tất định. Tính chín window, bốn AnchorSetMedian, PrimaryMedian, PooledMedian và bảng coverage. Đánh giá điều kiện OOS riêng kèm OOS_Months và cờ SHORT_OOS. |
| 7 — Gate 2 | Chạy đúng manifest đã đóng băng. Không có chiều ma sát nào trong Gate 2. Báo cáo Gate2_PreOOS_PassShare (ngưỡng cứng) và Gate2_OOS_PassShare (báo cáo riêng). Không loại config sau khi thấy kết quả. Tìm robust plateau, không tìm global best. |
| 8 — Gate 3 | Chạy realistic baseline và manifest ma sát 114 config. Tính NetEdgePct. Tính ImplementationShortfallPP và attribution ba thành phần. Chạy behavioral robustness và stress P2P-unavailable. P2P VND spread chỉ là overlay sensitivity (Backtest §2.1). |
| 9 — Verdict | Áp bảng verdict ở §5 và quy tắc chặn ở §6 một cách tự động. |

## 4. Compute discipline

- Ước tính khối lượng: 219 config Gate 2 + 114 config Gate 3 + 1000 Random Timing + 1000 Random Anchor + 3000 bootstrap + 1000 behavioral, mỗi full run duyệt khoảng 268.000 nến 15m. Không tối ưu thì không chạy nổi trong thời gian hợp lý.
- Daily indicator được tính trước và cache MỘT LẦN cho mỗi bộ score weight, không tính lại cho từng config.
- Random Timing và Random Anchor là lightweight replay dùng lịch giải ngân đã tính sẵn; KHÔNG chạy lại full engine 15m.
- Behavioral và bootstrap simulation tái sử dụng đường dữ liệu thị trường đã cache.
- Manifest generator được unit test tách biệt khỏi simulation engine.
- Ưu tiên pandas/polars vectorized hoặc numpy; lưu kết quả từng run ra parquet để tổng hợp sau.

## 5. Verdict và stopping rules

| Verdict | Hành động bắt buộc |
|---|---|
| BUILD | Chỉ khi Gate 1, 2, 3 đều PASS VÀ không Failure Signal nào TRUE. Tiến sang app MVP single-user dùng đúng strategy engine đã khóa. |
| BUILD WITH MODIFICATIONS | KHÔNG vá V2.1.5. Tạo V2.2 change proposal, đóng băng hypothesis mới, chạy lại các gate bắt buộc. |
| INCONCLUSIVE | Dừng productization. Cải thiện dữ liệu hoặc diagnostics, hoặc chờ thêm bằng chứng. Không build full app. |
| DO NOT BUILD | Dừng productization chiến lược. Chọn benchmark đơn giản hơn hoặc thiết kế lại thành version mới. |

## 6. Failure-signal override

Nếu Gate 1, Gate 2 và Gate 3 đều PASS nhưng BẤT KỲ Failure Signal FS-01..FS-12 nào = TRUE, verdict cuối cùng bị giới hạn ở BUILD WITH MODIFICATIONS. BUILD là KHÔNG THỂ khi còn bất kỳ Failure Signal nào TRUE.

Lý do: chỉ có khoảng ba block dữ liệu độc lập trong toàn bộ lịch sử khả dụng, nên ba con số của gate là bằng chứng yếu. Failure Signal chẩn đoán cơ chế và đáng tin hơn. Không được để ba con số yếu ghi đè lên các chẩn đoán mạnh.

## 7. Research prototype acceptance criteria

- Cùng dataset hash, config hash, manifest hash và seed thì tái lập chính xác cùng kết quả.
- Không phát hiện lookahead trong unit test và integration test.
- Không có vốn âm và không có double reservation ở bất kỳ thời điểm nào.
- Mọi benchmark nhận đúng cùng lịch external contribution.
- Gate 1 dùng đúng chín window pre-OOS multi-anchor; OOS hoàn toàn tách biệt; PrimaryMedian tính theo §4.1 của Backtest Spec.
- Gate 2 manifest tái lập đúng: 19 ứng viên OFAT, 1 bị loại, 18 hợp lệ, 200 LHS duy nhất, denominator 219.
- Gate 3 manifest tái lập đúng 114 config và không tồn tại config BULK_MONTHLY với funding_delay > 0.
- Bootstrap, behavioral và random control dùng đúng N và seed đã khai báo.
- Benchmark D được cài đặt đúng, bao gồm reserve cap 6C; Benchmark C theo ngữ nghĩa chu kỳ [F4].
- Partial fill, DEGRADED contribution = 0, và toàn bộ ladder lifecycle được unit test.
- Toàn bộ metric của gate được sinh tự động, không tính tay.
- Rolling window chồng lấn được gắn nhãn DESCRIPTIVE rõ ràng trong mọi output.
- Bảng verdict và Failure-signal cap được áp dụng tự động; INCONCLUSIVE và DO NOT BUILD không thể đi tiếp sang phase app.

## 8. Release integrity procedure

Ba version liên tiếp đã sửa được các lỗi được chỉ ra và đồng thời đánh rơi những mục không được chỉ ra. Nguyên nhân là checklist theo audit findings chỉ nhớ vòng trước. Thủ tục sau đây là bắt buộc cho MỌI version từ nay.

1. Mở 06_SECTION_INVENTORY của version hiện tại. Đây là danh mục ĐẦY ĐỦ mọi mục bắt buộc trên cả năm tài liệu, không phải danh sách audit findings.
2. Với từng dòng trong inventory, xác nhận mục đó TỒN TẠI trong bản mới và ghi số mục thực tế.
3. Mọi mục bị xóa phải được ghi vào Deliberate Removals kèm lý do. Xóa mà không có dòng lý do là lỗi phát hành.
4. Chạy đối chiếu cơ học: trích text cả hai version, so sánh danh sách heading cấp 1, liệt kê mọi heading biến mất.
5. Xác nhận mọi tham số được tham chiếu ở một tài liệu đều có định nghĩa ở tài liệu khác. Ví dụ: mọi level trong lưới Gate 2 phải có ngữ nghĩa trong Strategy Spec.
6. Xác nhận baseline config ở Strategy §21 khớp với schema strategy_config ở Data Model §2 theo đúng quy tắc ba-field-metadata [F7].

Chỉ khi cả sáu bước trên đạt thì version mới được đánh dấu ACTIVE.

## 9. App MVP — chỉ sau verdict cho phép

- Single-user; tính toán on-demand khi mở trang; không cần cron cho tới khi thực sự cần notification.
- Xác nhận mua thủ công; portfolio chỉ cập nhật sau xác nhận.
- Dashboard dual-unit VND/USDT và Treasury đầy đủ.
- Lưu implementation shortfall thực tế và P2P delay thực tế để đối chiếu model với live.
- Một database, code modular, không microservice.
- Nếu ON_DEMAND thua BULK_MONTHLY đáng kể dưới ma sát thực tế, default live phải được quyết theo bằng chứng đó TRƯỚC khi làm MVP.
