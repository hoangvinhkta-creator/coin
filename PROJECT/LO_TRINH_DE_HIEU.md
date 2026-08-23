# LỘ TRÌNH DỰ ÁN — BẢN DỄ HIỂU

> File này dành cho người **không chuyên lập trình**.
> Nguồn sự thật: `PROJECT/PROJECT_PROGRESS.md`.
> **File này được sinh tự động — không sửa tay.**

| Tick | Tên việc | Mục đích | Mức xử lý | Thứ tự/phụ thuộc |
|---|---|---|---|---|
| ✅ | T-00 — Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C — Opus — xhigh | Không phụ thuộc. Mở đường cho T-01 |
| ⬜ | T-01 — Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C — Opus — xhigh | Sau T-00. Chế độ AUDIT read-only |
| ⬜ | T-02 — Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C — Opus — xhigh | Sau T-01. Song song được với T-03 |
| ⬜ | T-03 — Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C — Opus — high | Sau T-01. Song song được với T-02 |
| ⬜ | T-04 — Chốt lộ trình và đóng băng tiêu chí | Biến kết quả khảo sát thành lộ trình chính thức, có tiêu chí nghiệm thu đóng băng | C — Opus — xhigh | Sau T-01, T-02, T-03 |
| ⬜ | T-05 — DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | Duyệt — Con người — - | Sau T-04. Chặn T-06, T-08 |
| ⬜ | T-06 — Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C — Opus — xhigh | Sau T-05. Cần máy/VPS có mạng Binance |
| ⬜ | T-07 — DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | Duyệt — Con người — - | Sau T-06. Chặn T-11 |
| ⬜ | T-08 — Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C — Opus — xhigh | Sau T-05. Song song được với T-06 |
| ⬜ | T-09A — Sửa lỗi kế toán trong app web | Vá 3 lỗi có thể làm sai sổ vốn trước khi app được dùng với tiền thật | C — Opus — high | Sau T-03 và T-04 |
| ⬜ | T-09B — Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D — Fable — xhigh | Sau T-04. Nên làm trước T-10 |
| ⬜ | T-10 — Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C — Opus — xhigh | Sau T-08 và T-09B |
| ⬜ | T-11 — Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D — Fable — max | Sau T-07 và chỉ khi verdict = BUILD |

> Đồng bộ bằng `python governance/scripts/governance/sync_easy_roadmap.py`.
