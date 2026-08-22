# Nguồn dữ liệu và cách gọi API

Câu trả lời ngắn: **Binance Spot, và chỉ Binance Spot** — nhưng dùng ba kênh khác nhau cho
ba mục đích khác nhau. Đây không phải lựa chọn kỹ thuật mà là ràng buộc của spec:
Backtest §2 khóa nguồn dữ liệu, nên đổi sang sàn khác là đổi dataset, tức phải mở version mới
theo freeze rule (Master Index §6).

## Ba kênh

| Kênh | Dùng cho | Chi tiết |
|---|---|---|
| **Bulk archive** — `data.binance.vision` | Tải lịch sử một lần: ~268.000 nến 15m + hai chuỗi daily | ZIP theo tháng tại `/data/spot/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-YYYY-MM.zip`, mỗi file kèm `.CHECKSUM` SHA256. Miễn phí, không cần key, không rate limit đáng kể. **Đây là kênh đúng cho backtest.** |
| **REST klines** — `api.binance.com` | Bù tháng hiện tại chưa có trong archive; cập nhật hằng ngày | `GET /api/v3/klines`, tối đa 1000 nến/request, weight 2. Giới hạn 6.000 weight/phút theo IP (≈1.000 request/phút); theo dõi header `X-MBX-USED-WEIGHT-1M`. Market data không cần API key. |
| **WebSocket** — `stream.binance.com` | App realtime sau này; **không dùng cho backtest** | `wss://stream.binance.com:9443/ws/ethusdt@kline_15m`, đẩy mỗi giây. Chỉ nhận nến có `k.x == true` (đã đóng) — dùng nến đang chạy là vi phạm luật no-lookahead (Backtest §1, §2). Không polling REST cho realtime. |

`eth_dca_os/data/fetch.py` đã cài đặt hai kênh đầu: `fetch_series()` kéo bulk archive cho các
tháng đã hoàn tất (có verify SHA256), rồi tự chuyển sang REST cho phần đuôi.

## Không cần API key, và đừng tạo

Cả ba kênh trên đều là public market data. Product Spec §14 liệt kê "không lưu trading API key
hoặc credential custody" là non-goal — hệ thống chỉ khuyến nghị, người dùng tự đặt lệnh, nên
không có lý do gì để một API key tồn tại trong dự án này.

## Tỷ giá P2P VND/USDT

**Không scrape.** Binance có endpoint tìm kiếm quảng cáo P2P nhưng nó không nằm trong API công
khai, không cam kết ổn định và hay bị chặn. Quan trọng hơn: Product Spec §9 quy định
`vnd_amount` và `usdt_amount` phải là giá trị thực tế của giao dịch đã thực hiện — đó mới là
source of truth để đo funding delay và cost basis. Giá trong bảng quảng cáo không phải giá đã khớp.

Nếu cần một con số tham chiếu để hiển thị ước tính USDT trên dashboard, nhập tay tỷ giá tham
chiếu mỗi ngày là đủ, và UI phải ghi rõ đó là ước tính (Product Spec §4).

Nhắc lại ràng buộc của Backtest §2.1 [F6]: Gate 1 và Gate 2 chạy trên đơn vị danh nghĩa
1 USDT = 1 đơn vị; spread P2P chỉ là overlay sensitivity ở phần reporting của Gate 3, không bao
giờ là điều kiện PASS.

## Các nguồn khác

| Nguồn | Vai trò hợp lệ | Vì sao không thay được Binance |
|---|---|---|
| CoinGecko / CoinMarketCap | Đối chiếu giá, hiển thị dự phòng khi Binance lỗi | Giá là trung bình gia quyền nhiều sàn, volume không phải volume Binance — phá thẳng factor VR (Strategy §1.2) và percentile365 |
| CryptoCompare / Coinbase / Kraken | Kiểm tra chéo khi nghi ngờ một cây nến bất thường | Khác sổ lệnh, khác giờ đóng nến, khác thanh khoản; trộn vào là dataset khác |
| Kaiko / Amberdata / Tardis.dev | Nếu sau này cần tick data để mô phỏng slippage thật thay vì giả định bps | Trả phí, và là mở rộng phạm vi — thuộc V2.2, không phải V2.1.5 |

## Nếu IP Việt Nam bị chặn

Chạy `ethdca fetch` trên VPS nước ngoài rồi copy thư mục `data/raw/` về máy — `dataset_hash`
đi theo nội dung file nên tính tái lập không mất. Kiểm tra bằng cách chạy `ethdca freeze` ở cả
hai máy: hash manifest phải trùng khớp.

## Nguồn tham chiếu

- Binance Spot API — [LIMITS](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/limits),
  [Market Data endpoints](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints),
  [WebSocket Streams](https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams)
- [binance/binance-public-data](https://github.com/binance/binance-public-data) — cấu trúc archive và cách verify checksum
