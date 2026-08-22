# ETH DCA Operating System V2.1.5 — Master Index

**LOCKED CORRECTIVE RELEASE • SOURCE OF TRUTH • COMPLETENESS-CONTROLLED**

## 1. Mục đích và phạm vi

V2.1.5 là corrective release của V2.1.4. Nó (a) giữ nguyên toàn bộ nội dung và hypothesis của V2.1.4, (b) đóng bảy lỗ hổng đặc tả (F1–F7, xem §4) được phát hiện khi chuẩn bị implement — tất cả đều là **hoàn thiện đặc tả**, không thay đổi công thức chiến lược, ngưỡng gate, thuật toán sinh manifest, seed hay ngày split, và (c) được phát hành TRƯỚC khi bất kỳ official run nào được thực hiện, nên tuân thủ đúng freeze rule §6.

Phạm vi sản phẩm KHÔNG thay đổi. Pack này phải đủ để một AI coding agent triển khai research prototype và backtest mà không cần đọc bất kỳ version cũ nào.

## 2. Precedence

Nếu hai tài liệu mâu thuẫn, áp dụng thứ tự dưới đây. Agent không được tự chọn.

1. **03_BACKTEST_SPEC_V2_1_5** — chuẩn mô phỏng, cửa sổ gate, manifest, delay, benchmark, failure signals, processing order, test suite.
2. **02_STRATEGY_SPEC_V2_1_5** — score, capital, ladder, regime, limits, lifecycle, enum, baseline config.
3. **04_DATA_MODEL_V2_1_5** — schema, ledger, config, run metadata, invariants.
4. **01_PRODUCT_SPEC_V2_1_5** — workflow, treasury, dashboard, dual-unit VND/USDT, P2P.
5. **05_IMPLEMENTATION_PLAN_V2_1_5** — phase, compute discipline, verdict stopping rules, release integrity procedure.
6. **06_SECTION_INVENTORY_V2_1_5** — danh mục đầy đủ mọi mục bắt buộc; dùng để kiểm tính toàn vẹn trước mỗi lần phát hành.

## 3. Trạng thái tài liệu cũ

| Version | Status | Quy tắc sử dụng |
|---|---|---|
| V1 | DEPRECATED | Historical reference. Không dùng để implement. |
| V2.0 | DEPRECATED | Mọi rule còn hiệu lực đã gộp vào V2.1.4/V2.1.5. |
| V2.1 | SUPERSEDED | Không giao agent. |
| V2.1.1 | SUPERSEDED | Không giao agent. |
| V2.1.2 | SUPERSEDED | Không giao agent. |
| V2.1.3 | SUPERSEDED | Không giao agent. Có regression đã được sửa ở V2.1.4. |
| V2.1.4 | SUPERSEDED | Không giao agent. Có bảy lỗ hổng đặc tả đã được đóng ở V2.1.5 (§4). |
| **V2.1.5** | **ACTIVE / SOURCE OF TRUTH** | Bộ duy nhất dùng cho Phase 0 và official backtest. |

## 4. Changelog V2.1.4 → V2.1.5

Không có công thức chiến lược, ngưỡng gate, thuật toán manifest, seed, ngày split hoặc giả định ma sát nào thay đổi. Bảy mục dưới đây chỉ **định nghĩa những điều V2.1.4 để ngỏ** hoặc sửa câu chữ mâu thuẫn.

| # | Vấn đề ở V2.1.4 | Xử lý ở V2.1.5 |
|---|---|---|
| F1 | STRESSED nằm trong enum Market Regime và Backtest §16 yêu cầu báo cáo cooldown override theo STRESSED, nhưng không tồn tại rule enter/exit nào cho STRESSED. | Strategy §17.3 định nghĩa STRESSED là **nhãn dẫn xuất chỉ dùng cho reporting**, không có hiệu ứng execution: STRESSED khi (Return7D ≤ −10% OR Return24H ≤ −7%) và không ở CRASH/RECOVERY; NORMAL cho phần còn lại. |
| F2 | Không có tie-break khi nhiều zone bị xuyên trong cùng một nến; chỉ có priority Base → Smart → Opportunity giữa các pool. | Strategy §15.1: trong cùng pool, zone thực thi theo zone_index tăng dần; giữa hai ladder cùng pool, ladder tạo trước xử lý trước; max_zones_per_cycle áp SAU khi đã sắp thứ tự. Backtest §19 bước 13–14 tham chiếu quy tắc này. |
| F3 | Base tranche rơi vào gap dữ liệu chỉ được xử lý gián tiếp ở Backtest §18. | Strategy §9 bổ sung câu tham chiếu tường minh: nến 12:00 local thiếu → execute tại nến 15m hợp lệ đầu tiên sau đó, tag DELAYED_DATA_FILL; tranche Base không bao giờ bị bỏ. |
| F4 | Benchmark C: "cho phép reset chu kỳ tích lũy/giải ngân reserve" không định nghĩa chu kỳ. | Backtest §12: mỗi trigger giải ngân (−30%, −45%) bắn tối đa MỘT lần trong một chu kỳ; chu kỳ mới bắt đầu khi daily close ≥ MA200 sau ít nhất một trigger đã bắn; reserve không âm. |
| F5 | Crash ladder: "phần vốn đủ điều kiện" không định nghĩa thời điểm chốt. | Strategy §14: eligible capital = snapshot tổng Smart + Opportunity AVAILABLE (đã unlock, chưa reserve) đo NGAY SAU khi cancel các Opportunity zone xung đột tại thời điểm vào CRASH. C0–C3 áp trên snapshot đó và snapshot bất biến trong đời Crash ladder. |
| F6 | Quy tắc hạch toán VND trong backtest nằm rải rác ở Product §14, Backtest §10, §16. | Backtest §2.1 "VND accounting trong backtest" gom về một chỗ: Gate 1/Gate 2 chạy trên đơn vị danh nghĩa 1 USDT = 1 đơn vị; VND/P2P spread lịch sử chỉ là overlay sensitivity ở Gate 3 reporting, không bao giờ là điều kiện gate. |
| F7 | Strategy §21 nói baseline "khớp một-một" với Data Model §2, nhưng schema có thêm 3 field metadata — mâu thuẫn câu chữ với XC-1. | Strategy §21 và Data Model §2 nêu tường minh ngoại lệ đúng ba field metadata: config_name, created_at, strategy_config_hash. |

Changelog V2.1.3 → V2.1.4 (fix A1–A5 và khôi phục nội dung) được giữ nguyên giá trị lịch sử trong pack V2.1.4; các kết quả của nó đã nằm trọn trong nội dung V2.1.5.

## 5. Release integrity register

Nguyên nhân gốc của ba lần regression liên tiếp (V2.1.1 → V2.1.3): mỗi bản phát hành chỉ kiểm lại các mục mà audit vòng trước chỉ ra, nên những mục không bị chỉ ra sẽ rơi mà không ai biết. Checklist theo audit findings luôn thất bại theo đúng kiểu này.

Từ V2.1.4 trở đi, quy tắc bắt buộc: tài liệu 06_SECTION_INVENTORY liệt kê MỌI mục bắt buộc trên cả năm tài liệu. Trước khi phát hành bất kỳ version nào, phải kiểm toàn bộ danh mục đó, không phải kiểm danh sách audit findings. Xem Implementation Plan §8 để biết thủ tục. V2.1.5 đã chạy đủ thủ tục này; kết quả ghi tại `docs/spec/RELEASE_CHECK_V2_1_5.md`.

## 6. Versioning và freeze rule

- Sau khi Phase 0 khóa V2.1.5, không sửa công thức, ngưỡng gate, phương pháp sinh manifest, ngày split hoặc giả định ma sát dựa trên kết quả official run.
- Nếu kết quả yêu cầu đổi hypothesis, tạo V2.2 với hypothesis mới và chạy lại các gate bắt buộc. Không vá tại chỗ.
- Mọi run lưu strategy_version, backtest_spec_version, strategy_config_hash, execution_config_hash, manifest_hash, dataset_hash và seed.
- Mọi version mới phải đi kèm một Section Inventory đã được kiểm đầy đủ.
