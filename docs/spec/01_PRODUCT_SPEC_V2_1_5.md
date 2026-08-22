# ETH DCA Operating System V2.1.5 — Product Specification

**SINGLE-USER • MANUAL EXECUTION • VND ACCOUNTING / USDT EXECUTION**

## 1. Product vision

ETH DCA OS là hệ thống quản trị quyết định và quản trị vốn cho chiến lược tích lũy ETH dài hạn. Hệ thống không dự đoán giá và không tự động đặt lệnh. Nó tạo recommendation, quản lý vốn VND/USDT, theo dõi giao dịch P2P, và chỉ cập nhật portfolio sau khi người dùng xác nhận giao dịch thực tế.

## 2. Core flow

```
VND -> P2P BUY -> USDT TREASURY -> ACTION READY -> MANUAL ETH BUY -> CONFIRM -> ETH PORTFOLIO
ETH SELL -> USDT -> P2P SELL -> VND
```

## 3. Currency model

| Vai trò | Đơn vị | Source of truth cho |
|---|---|---|
| Accounting currency | VND | Budget, contribution, reserve, capital limit, hiệu quả fiat đã thực hiện. |
| Execution currency | USDT | Thực thi spot ETH và tham chiếu market value. |
| Investment asset | ETH | Mục tiêu tích lũy. |

## 4. Dual-unit UX

Không dùng toggle để giấu một đơn vị. Mỗi card hiển thị cả hai, primary/secondary tùy ngữ cảnh.

| Ngữ cảnh | Primary | Secondary |
|---|---|---|
| Monthly Budget | VND | USDT ước tính theo P2P buy reference hiện hành |
| Next ETH Buy | USDT | VND source allocation |
| Portfolio market value | USDT | VND thanh khoản ước tính theo P2P sell reference |
| Cost basis | USDT/ETH | VND/ETH |
| PnL | USDT | VND |

## 5. Treasury model

| Bucket | Ý nghĩa |
|---|---|
| VND available | Fiat chưa đổi sang USDT. |
| USDT available | USDT sẵn sàng thực thi ngay. |
| USDT reserved | USDT hoặc giá trị kinh tế tương đương đã dành cho action/zone đang mở. |
| ETH holdings | ETH đã mua và đã được xác nhận. |
| Opportunity reserve VND | Giá trị kinh tế là source of truth; có thể được funded một phần bằng USDT, phần còn lại vẫn ở VND. |

## 6. Execution states

`WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED`

## 7. Manual execution workflow

```
ZONE TRIGGER -> ACTION_PENDING -> CHECK TREASURY -> [FUNDING_REQUIRED] -> READY_TO_BUY
             -> USER EXECUTES -> USER CONFIRMS -> PURCHASE RECORDED
```

- Zone trigger không đồng nghĩa với fill. Hệ thống không giả định đã mua.
- ACTION_TTL mặc định 12h.
- FUNDING_REQUIRED xuất hiện khi USDT available nhỏ hơn USDT ước tính cần cho action.
- Live app phải lưu recommended_price, triggered_at, action_created_at, funding_started_at, ready_to_buy_at, executed_at và actual_price để đo implementation shortfall thực tế và đối chiếu ngược với giả định delay của backtest.
- Phân bổ kinh tế của zone luôn tính bằng VND. Nếu tỷ giá P2P dịch chuyển, lượng USDT/ETH thu được sẽ khác, nhưng zone được coi là hoàn thành theo phân bổ VND thực tế, không theo một mục tiêu USDT cố định.

## 8. Partial fill

- Nếu người dùng thực thi ít hơn phân bổ VND được khuyến nghị, zone chuyển PARTIALLY_FILLED.
- Phần VND chưa fill tiếp tục ở trạng thái RESERVED cho tới khi ACTION_TTL hết hạn hoặc người dùng hoàn tất action.
- Khi TTL hết hạn, phần chưa fill được RELEASE về AVAILABLE. Zone lịch sử giữ nguyên trạng thái PARTIALLY_FILLED và đóng lại cho action đó.
- Engine có thể tạo action mới sau đó nếu điều kiện chiến lược vẫn thỏa mãn.

## 9. P2P transaction model

| Field | Rule |
|---|---|
| direction | VND_TO_USDT / USDT_TO_VND |
| vnd_amount | Bắt buộc, giá trị thực tế |
| usdt_amount | Bắt buộc, giá trị thực tế |
| fee_vnd | Bắt buộc, mặc định 0 |
| effective_rate | Derived. Với chiều mua: (VND đã trả + phí) / USDT nhận được. Với chiều bán: tỷ giá thực hiện tương ứng. |
| started_at / completed_at | Bắt buộc; dùng để đo funding delay thực tế |
| platform | Tùy chọn |
| related_action_id | Nullable |

## 10. Funding policies

| Policy | Định nghĩa | Vai trò |
|---|---|---|
| ON_DEMAND | Chỉ đổi VND sang USDT khi có action đủ điều kiện cần USDT. | Hypothesis sản phẩm ban đầu; baseline thực tế của Gate 3. |
| BULK_MONTHLY | Nạp trước lượng USDT dự kiến của tháng trong một lần. | Đối chứng bắt buộc ở Gate 3. Có thể trở thành default live nếu bằng chứng ủng hộ. |

Quyết định default live phải dựa trên kết quả Gate 3 realistic, không quyết trước.

## 11. Dashboard hero

- Giá ETHUSDT hiện tại / tham chiếu.
- Opportunity Score raw kèm nhãn hiển thị.
- Market Regime: NORMAL / STRESSED / CRASH / RECOVERY.
- Execution State: WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED.
- Recommended action kèm số tiền VND và USDT.
- Next zone và khoảng cách phần trăm tới zone đó.
- Data Quality: GOOD / DEGRADED / INVALID.

## 12. Capital / Treasury / P2P panels

| Panel | Nội dung bắt buộc |
|---|---|
| Monthly capital | Base, Smart, Opportunity theo VND kèm USDT ước tính; tiến độ available / reserved / deployed từng pool. |
| Treasury | VND available, USDT available, USDT reserved, ETH holdings. |
| Opportunity Fund | Balance, cap, unlocked %, unlocked amount, used today, daily limit. |
| P2P | Buy reference hiện hành, sell reference, spread, weighted USDT cost basis theo VND. |
| Buy Ladder | Zone \| Target \| Distance \| Capital \| Source \| Status. |
| Score breakdown | Price Location /50, Market Stress /30, Relative Value /20 kèm sub-factor. |
| Portfolio | Số lượng ETH, market value USDT, VND thanh khoản ước tính, average cost USDT/ETH và VND/ETH. |

## 13. Data quality display

Trạng thái DEGRADED và INVALID phải hiển thị rõ trên hero, không được ẩn. Khi DEGRADED, UI phải nêu component nào đang thiếu và nói rõ rằng score không được chuẩn hóa lên.

## 14. Non-goals V2.1.5

- Không auto-execute lệnh trên sàn.
- Không lưu trading API key hoặc credential custody.
- Không có sell-signal engine, không leverage, không futures.
- Không khuyến nghị đa dạng hóa danh mục, không kế toán thuế.
- Ước lượng VND/P2P lịch sử không được dùng làm điều kiện quyết định của Gate 1 hoặc Gate 2 (xem Backtest §2.1).
