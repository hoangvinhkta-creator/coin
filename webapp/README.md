# App theo dõi trên web

App single-user để theo dõi vốn, ladder và danh mục theo ETH DCA OS V2.1.5.
Bản đã xuất bản: <https://claude.ai/code/artifact/ee1cc5bf-b66c-438f-9aee-ca229b0e1d95>

> **App này nằm sau một cổng chưa mở.** Implementation Plan §9 chỉ cho phép dựng app MVP sau
> khi backtest cho verdict BUILD. Verdict chưa chạy trên dữ liệu Binance thật, nên app được
> xây theo yêu cầu của chủ dự án như một **công cụ ghi chép và tính toán**, không phải bằng
> chứng rằng chiến lược đã được chứng thực. Banner cảnh báo này hiển thị thường trực trên app.

## Vì sao app không tự lấy giá

Trang artifact chạy dưới CSP chặn mọi host ngoài (Google Fonts là ngoại lệ duy nhất), và
tài khoản chưa nối connector nào. App **không thể** gọi `api.binance.com`. Hệ quả:

1. Lịch sử 365+ ngày đến từ file seed do engine Python thật sinh ra: `ethdca export-live`.
2. Mỗi ngày bạn nhập giá đóng cửa ETH/BTC và volume ở tab **Nhập số liệu**.

Chỉ nhập nến **đã đóng** — dùng nến đang chạy là vi phạm luật no-lookahead (Backtest §1–2).

## Vấn đề hai bản cài đặt, và cách xử lý

Impl Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Một trang tĩnh
không chạy được Python, nên `engine.js` là **bản cài đặt thứ hai** của cùng đặc tả — và hai
bản cài đặt thì trôi khỏi nhau.

Cách chặn: mỗi seed mang theo OSCORE do Python tính cho 40 ngày gần nhất (`parity`). App tính
lại các ngày đó bằng JS và so; lệch quá dung sai thì hiện banner đỏ và bạn không nên tin số
trên trang. Kết quả đối chiếu hiển thị ở tab **Thiết lập**.

Lần kiểm gần nhất: lệch tối đa 7.4e-11 trên 40 ngày — hai bản đồng thuận.

## Build

```bash
node webapp/build_app.js      # ghép shell + engine + logic -> app_final.html
```

`build_app.js` nhúng base64 của chính template vào trang (quine) để app tự publish được bản
mới khi bạn bấm **Lưu** — đó là cách dữ liệu sống qua nhiều thiết bị. Song song, state được
ghi vào `localStorage` ngay lập tức nên một lần lưu thất bại không mất dữ liệu.

## Test

```bash
node webapp/test_app.js     # luồng: nạp seed -> vốn -> P2P -> ladder -> mua -> reload
node webapp/test_zone.js    # zone fill, partial fill, invalidation và release đúng kế toán
```

Hai test này cần Playwright và chạy trên `app_final.html` đã build.

## Những gì app CHƯA làm

Có chủ đích, để không giả vờ đầy đủ hơn thực tế:

- **Return24H dùng daily return làm xấp xỉ.** Spec tính trên 96 nến 15m; app chỉ có dữ liệu
  daily. Nhãn regime vì vậy là gần đúng.
- **Base schedule Day 3/13/23 và Month-End chưa tự động.** Bạn tự nạp vốn và tự mua.
- **Crash ladder chưa tự sinh.** Chỉ có Smart và Opportunity ladder tạo thủ công.
- **Cooldown 48h và daily limit 20% chưa cưỡng chế** trong app.

Những phần đó đã có trong engine Python (`src/eth_dca_os/engine.py`) và chạy đúng trong
backtest; app chỉ chưa port sang.
