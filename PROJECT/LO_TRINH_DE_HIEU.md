# LỘ TRÌNH DỰ ÁN — BẢN DỄ HIỂU

> File này dành cho người **không chuyên lập trình**.
> Nguồn sự thật: `PROJECT/PROJECT_PROGRESS.md`.
> **File này được sinh tự động — không sửa tay.**

| Tick | Tên việc | Mục đích | Mức xử lý | Thứ tự/phụ thuộc |
|---|---|---|---|---|
| ✅ | T-00 — Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C — Opus — xhigh | Không phụ thuộc. Mở đường cho T-01 |
| ✅ | T-01 — Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C — Opus — xhigh | Sau T-00. Chế độ AUDIT read-only |
| ✅ | T-02 — Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C — Opus — xhigh | Sau T-01. Song song được với T-03 |
| 🟡 | T-03 — Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C — Opus — high | Sau T-01. Chuyển DONE khi WP-C1 hoàn tất và ba nghi vấn có kết luận E1 |
| ⬜ | T-04 — Chốt lộ trình và đóng băng tiêu chí | Soạn Ready Gate + Completion Gate cho 15 work package của RCP-001, đóng băng trước khi thực thi | C — Opus — xhigh | Sau T-01, T-02, T-03. Mở đường cho toàn bộ WP-* |
| ⬜ | T-05 — DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | Duyệt — Con người — - | Sau T-04. KHÔNG nằm trên đường găng tới verdict (RCP-001) — chỉ chặn T-08 và WP-C2 |
| ⬜ | WP-A1 — Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, đúng môi trường, và tái lập lại được | C — Opus — xhigh | Sau T-04. Song song với WP-A2, WP-A3, WP-C1. Thay thế T-06A cũ (đóng F-005, F-007, F-009, F-010, F-011) |
| ⬜ | WP-A2 — Bật các hạng mục đã viết nhưng pipeline chưa chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có, dù code đã đúng | C — Opus — high | Sau T-04. Song song với WP-A1, WP-A3 (đóng F-003, F-004, F-012, F-013, F-014). Tier ghi đè thủ công — router trả B, xem DEC-008/GOVDEF-001 |
| ⬜ | WP-A3 — Sửa vòng đời trạng thái thị trường và ladder khẩn cấp | Vốn có thể bị khoá vĩnh viễn khi thị trường hồi phục một phần rồi yếu lại | D — Fable — max | Sau T-04. Song song với WP-A1, WP-A2, WP-C1 (đóng F-001, F-021, F-022, F-030) |
| ⬜ | WP-A4 — Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu Binance thật có lỗ hổng; xử lý sai sẽ làm sai kết quả mô phỏng | C — Opus — xhigh | Sau WP-A3 (đóng F-023, F-025, F-032) |
| ⬜ | WP-A5 — Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược | Ba tín hiệu hiện không bao giờ được đo dù vẫn cho ra kết luận cuối cùng | C — Opus — xhigh | Sau WP-A2, WP-A3 (vốn không bị khoá thì số đo mới đúng) — đóng phần đo lường của F-002, và F-016 |
| ⬜ | WP-A6 — Chốt và kiểm chứng đúng thứ tự các bước tính toán | Thứ tự sai nghĩa là con số chính thức không đại diện đúng cho chiến lược đã đặc tả | D — Fable — max | Sau WP-A3, WP-A4 (đóng F-018, F-019) |
| ⬜ | T-06 — Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C — Opus — xhigh | Sau T-05 và **GATE-A** (WP-A1…WP-A6 đều DONE). Cần máy/VPS có mạng Binance — BLK-001 chặn đúng tại đây |
| ⬜ | WP-B1 — Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo | Không cho phép kết luận thuận lợi khi vẫn còn tín hiệu cảnh báo chưa đo được | D — Fable — max | Sau T-06. QUY TẮC BẮT BUỘC: nếu remediation của F-017 (Control F) ảnh hưởng Gate 1 → Gate 1 phải chạy lại trước khi coi kết quả hợp lệ (DEC-009) — đóng phần chính sách của F-002, F-015, F-017, F-026 |
| ⬜ | WP-B2 — Bổ sung test cho các yêu cầu đặc tả còn thiếu | Nhiều yêu cầu của BT §21 hiện không có gì kiểm chứng | C — Opus — xhigh | Sau T-06. Song song với WP-B1, WP-B3 |
| ⬜ | WP-B3 — Hoàn thiện nhật ký quyết định để truy vết được | Cần truy vết được vì sao hệ thống ra quyết định như vậy tại từng thời điểm | C — Opus — high | Sau T-06. Song song với WP-B1, WP-B2. Ngữ nghĩa `previous_state/new_state` phụ thuộc WP-C2 (đóng F-024, F-033) |
| ⬜ | T-07 — DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | Duyệt — Con người — - | Sau T-06 và **GATE-B** (WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE). Chặn T-11 |
| ⬜ | WP-C1 — Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test | App đang có thể dùng để ghi tiền thật; ba nghi vấn về sai sổ vẫn chưa có kết luận | C — Opus — xhigh | Sau T-01 (đã DONE). Độc lập hoàn toàn — có thể chạy ngay, song song với toàn bộ lớp A. Gỡ BLOCKED cho T-03 khi xong (đóng V-01, V-02, V-03, F-027) |
| ⬜ | WP-C2 — Làm rõ và đặt tên trạng thái thực thi của hệ thống | Cần biết rõ hệ thống đang ở trạng thái nào trước khi đưa vào dùng thật | C — Opus — xhigh | Sau T-05 (DEC-005 quyết phạm vi). Cần ADR quyết định phạm vi trước khi bắt đầu — xem WP-C2 Notes (đóng F-006) |
| ⬜ | WP-C3 — Xử lý mua một phần ở tầng sản phẩm | Mua một phần là tình huống thật ngoài đời, tầng ghi sổ hiện chưa xử lý đúng | C — Opus — xhigh | Sau WP-C2 (đóng F-020) |
| ⬜ | WP-C4 — Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS) | Hai bản cài đặt có thể trôi khỏi nhau khi thêm tính năng mới vào JS | C — Opus — xhigh | Sau WP-A3, WP-A4, WP-A6 (không khoá parity vào hành vi sắp đổi). Chặn T-10, T-11 (đóng F-008) |
| ⬜ | T-08 — Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C — Opus — xhigh | Sau T-05 |
| ⬜ | T-09A — Sửa lỗi kế toán trong app web | Vá lỗi nếu WP-C1 xác nhận là có thật, trước khi app được dùng với tiền thật | C — Opus — high | Sau WP-C1. Nếu WP-C1 bác bỏ cả ba nghi vấn, T-09A có thể thu hẹp phạm vi hoặc CANCELLED |
| ⬜ | T-09B — Dựng lưu trữ dữ liệu bền | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D — Fable — xhigh | Sau T-04. Nên làm trước T-10 |
| ⬜ | T-10 — Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C — Opus — xhigh | Sau T-08, T-09B, WP-C4 |
| ⬜ | WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả | Dọn cho sạch, không ảnh hưởng gì tới kết quả hiện tại | B — Sonnet — medium | Không phụ thuộc, làm bất cứ lúc nào (đóng F-028, F-029, F-031, F-034) |
| ⬜ | WP-D2 — Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn | Một số mâu thuẫn thuộc về chính bộ đặc tả, cần chủ dự án quyết định mở V2.2 | C — Opus — xhigh | Không phụ thuộc. Đầu ra là đề xuất, KHÔNG sửa V2.1.5 (đóng S-001, S-002, S-003) |
| ⬜ | T-11 — Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D — Fable — max | Sau T-07, WP-C2, WP-C3, WP-C4, và chỉ khi verdict = BUILD |

> Đồng bộ bằng `python governance/scripts/governance/sync_easy_roadmap.py`.
