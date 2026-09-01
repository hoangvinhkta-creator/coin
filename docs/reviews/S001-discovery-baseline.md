# Discovery & Baseline Report — S001

## Project
ETH DCA Operating System — V2.1.5

## Date
2026-08-23 (phiên S001, chế độ AUDIT READ-ONLY)

## Profile
PRODUCT

## Executive Summary

Repo chứa một backtest engine Python hoàn chỉnh (26 module, ~3.400 dòng) cùng một app web
prototype (~2.100 dòng JS), viết trong 11 commit **trước khi** bộ governance được đưa vào.
S001 là lần đầu tiên implementation được đối chiếu có hệ thống với bộ spec V2.1.5.

**Kết luận ngắn: tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không.**

Toàn bộ OSCORE và tám sub-factor, unlock, ScoreMultiplier, spacing, phân bổ ladder, bốn bộ ngưỡng
gate, thuật toán sinh manifest 219/114, chọn chín window và bảng coverage đều khớp spec tới từng
hằng số — phần lớn có test trực tiếp. Đây không phải code cẩu thả.

Nhưng ba cụm vấn đề nằm **trên đường đi tới verdict**:

1. **Đã viết nhưng không được gọi.** Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng
   coverage §4, XIRR §16 — tất cả đều tồn tại, đúng spec khi đọc, và **không nơi nào trong
   pipeline gọi chúng**. Spec ghi rõ những mục này bắt buộc trong mọi official run.
2. **Vòng đời trạng thái chưa đóng.** Execution State machine không tồn tại; partial fill không
   bao giờ phát sinh; Crash ladder có đường vào nhưng đường ra bị hở — reserve có thể bị khoá
   vĩnh viễn (F-001, đã kiểm chứng bằng chạy thật).
3. **Tính chính thức và tái lập chưa được bảo vệ.** Cờ `official` không nhìn nguồn dữ liệu,
   lineage không ghi source thật, manifest hash không gắn vào run record, thư viện không ghim.

Tổng: **33 finding** — 0 CRITICAL, 8 HIGH, 15 MEDIUM, 7 LOW, 3 spec defect. 18/33 có bằng chứng
chạy thật. Không phát hiện regression kế thừa từ V2.1.1–V2.1.4.

Ba nghi vấn webapp từ S000 (RSK-003) **vẫn chưa được kiểm chứng** — chứng minh chúng cần viết
test mới, mà quy tắc S001 cấm. Chúng được chuyển thành verification task V-01/02/03.

## 1. Architecture Inventory

- **Framework/runtime:** Python >= 3.11, không framework. Phụ thuộc: numpy, pandas, pyarrow,
  requests. Dev: pytest. Entry point CLI `ethdca`.
- **Hosting:** không có. Chạy cục bộ. App web là trang tĩnh publish dạng Claude Artifact.
- **Main modules (26):** `config`, `data/{fetch,synth,dataset}`, `indicators`, `score`,
  `diagnostics`, `capital`, `ladders`, `regime`, `engine`, `execution`, `benchmarks`, `windows`,
  `manifests`, `metrics`, `gates`, `failure_signals`, `verdict`, `bootstrap`, `pipeline`, `cli`,
  `reporting`, `live_export`.
- **Shared layers:** `config` (hash tất định) và `windows` được dùng xuyên suốt. `engine` là trung
  tâm; `benchmarks` import ngược `engine` để lấy hằng số thời gian — một phụ thuộc ngược nhẹ.
- **External services:** Binance (bulk archive `data.binance.vision` + REST `api.binance.com`).
  Không API key, chỉ public market data.
- **Ranh giới thứ hai:** `webapp/` là bản cài đặt **độc lập** của cùng đặc tả bằng JS
  (`engine.js`), nối với Python chỉ qua file seed do `live_export.py` sinh.

## 2. Routing Inventory

`NOT APPLICABLE` cho backtest engine — không có HTTP routing.

App web: một trang tĩnh, năm tab điều hướng bằng JS trong cùng document. Không deep link, không
route guard. Không có backend nên không có route cần bảo vệ.

## 3. Data Inventory

- **Databases:** không có. Impl Plan §9 yêu cầu "một database" cho app MVP — chưa tồn tại.
- **Lưu trữ hiện tại:** parquet bất biến ở `data/raw/`; kết quả JSON/JSONL ở `results/`; app web
  dùng localStorage + cơ chế tự xuất bản lại trang.
- **Main entities (Data Model §1 định nghĩa 11):** chỉ một phần được hiện thực —
  `strategy_config`, `execution_config`, `capital_ledger` (qua `Pool.ledger`), `buy_ladders`,
  `buy_zones`, `backtest_runs`. **Không được hiện thực:** `market_snapshots`, `monthly_budgets`,
  `p2p_transactions`, `crypto_trades` (chỉ có purchase record rút gọn), `decision_log` (rất thiếu).
- **Sensitive fields:** không có dữ liệu cá nhân. Dữ liệu nhạy cảm về nghiệp vụ = lịch sử giao
  dịch thật của chủ dự án trong app web.
- **Migration risks:** app web chưa có schema version; nạp file export cũ sẽ hỏng state âm thầm.
- **Lineage:** có `dataset_hash` và `file_hash` cho từng parquet, **nhưng trường `source` là chuỗi
  cố định** không phân biệt dữ liệu thật với dữ liệu tổng hợp (F-005).

## 4. Authentication & Authorization

`NOT APPLICABLE` ở trạng thái hiện tại.

- Auth provider: không có. Roles: không có. Permissions: không có.
- Backend enforcement: không có backend.
- UI-only restrictions: app web không có ranh giới quyền nào — một người dùng duy nhất trên máy
  của chính họ.
- **Cần quyết định** ở giai đoạn app: nếu công cụ vượt ra ngoài một thiết bị thì auth trở thành
  bắt buộc theo profile PRODUCT. Đã ghi ở `PROJECT/PROJECT_PROFILE.md`.

## 5. Security Baseline

- **Secrets:** không tạo API key (Product §14 liệt kê "không lưu trading API key" là non-goal).
  Không phát hiện secret nào bị commit.
- **Client exposure:** app web chạy hoàn toàn client-side; không gửi dữ liệu đi đâu. CSP của trang
  artifact chặn mọi host ngoài trừ Google Fonts.
- **Security rules:** không áp dụng (không có backend, không có database).
- **Logging risks:** ledger và run record không chứa dữ liệu nhạy cảm.
- **High-risk endpoints/actions:** không có endpoint. Hành động rủi ro cao duy nhất là
  "Xóa toàn bộ dữ liệu" trong app web — một lớp `confirm`, không tự động sao lưu trước.
- **XSS:** app web có hàm escape và dùng nhất quán ở mọi chỗ nội suy dữ liệu người dùng.

Không phát hiện finding bảo mật nào ở mức MEDIUM trở lên trong S001.

## 6. Business Logic Inventory

- **Critical rules:** OSCORE và tám sub-factor; unlock Smart/Opportunity; ba mode HWM; hysteresis
  68/62; cap Opportunity + overflow; Base schedule + Month-End; ba loại ladder + spacing; regime
  CRASH/RECOVERY/STRESSED; giới hạn thực thi (daily limit, max zones, cooldown + override);
  bốn bộ ngưỡng gate; 12 failure signal; bảng verdict.
- **Duplicated rules:** **có, và đây là rủi ro kiến trúc chính** — `webapp/engine.js` cài lại
  OSCORE, unlock, spacing và phân bổ ladder bằng JS. Impl Plan §1 yêu cầu dùng chung một core
  function. Giảm thiểu hiện tại là parity check chỉ phủ OSCORE tổng (F-008).
- **UI-embedded logic:** app web suy ra nhãn trạng thái thực thi ngay trong hàm render thay vì lưu
  thành state.
- **High-risk calculations:** toàn bộ tầng phân bổ vốn. Bất biến `TOTAL = A + R + D` được bảo vệ
  bằng `InvariantError` ở tầng Pool và có test — điểm mạnh thật sự của thiết kế.

## 7. API / Integration Inventory

- **Internal APIs:** không có. Giao tiếp giữa module bằng lời gọi hàm trực tiếp.
- **External APIs:** Binance bulk archive (ZIP theo tháng + `.CHECKSUM` SHA256) và REST klines
  (tối đa 1000 nến/request, weight 2, 6.000 weight/phút theo IP).
- **Webhooks/jobs:** không có. Impl Plan §9 nêu "không cần cron cho tới khi thực sự cần
  notification".
- **Retry/idempotency:** `fetch.py` verify checksum cho bulk; chưa khảo sát sâu retry policy —
  ngoài phạm vi ưu tiên của S001.

## 8. Environment & Deployment

- **Dev:** Python 3.11.15, node v22.22.2, git 2.43.0. Không lockfile.
- **Staging:** không có.
- **Production:** không có. App web publish dạng artifact.
- **CI/CD:** **không có** — repo không có `.github/`.
- **Backup:** không có cơ chế nào cho dữ liệu app web ngoài export JSON thủ công.
- **Monitoring:** không có.
- **Mạng:** `api.binance.com`, `data-api.binance.vision`, `api.coingecko.com` đều trả **403** ở
  tầng proxy trong môi trường này; PyPI thông. Official run **không thể** chạy tại đây (BLK-001).

## 9. Technical Debt

Xếp theo mức độ cản trở đường tới verdict:

1. **Cụm "đã viết nhưng không đấu nối"** — B/C/D, ablation, volume z-score, coverage, XIRR.
   Nợ rẻ nhất để trả (code đã đúng, chỉ thiếu lời gọi) nhưng hậu quả lớn nhất nếu bỏ qua.
2. **Vòng đời Crash ladder hở** (F-001) — cần quyết định thiết kế nhỏ, không phải sửa một dòng.
3. **Không ghim thư viện** (F-007) — không sửa được về sau nếu official run đã chạy.
4. **Execution State machine vắng mặt** (F-006) — nợ kiến trúc, sẽ đắt dần khi sang app.
5. **Hai bản cài đặt chiến lược** (F-008) — bề mặt trôi lệch tăng theo mỗi tính năng port thêm.
6. **Bộ test không phủ tầng engine** — §21.3 gần như trống: tie-break, max_zones, cooldown,
   TTL/MISSED, crash funding, no-lookahead ở tầng 15m đều không có test.
7. **Quy ước không được ghi** — ngưỡng FS, phạm vi W5, ánh xạ verdict, `shift_days`.
8. **Bộ test webapp không chạy được từ checkout sạch** (thiếu `demo/` và `app_final.html`).

## 10. Audit Findings Summary

| Mức | Số lượng |
|---|---|
| Critical | 0 |
| High | 8 |
| Medium | 15 |
| Low | 7 |
| Info / Spec defect | 3 |
| **Tổng** | **33** |

Chi tiết đầy đủ: `docs/reviews/S001-audit-findings.md`.
Đối chiếu theo từng điều khoản: `docs/reviews/S001-compliance-matrix.md`.

Phân bố bằng chứng: **18 finding có bằng chứng chạy thật (E1)**, 15 mới là bằng chứng tĩnh (E0).
Không finding nào đạt E2 — S001 không có xác minh độc lập.

## 11. Recommended Remediation Order

**Không thực hiện trong S001.** Đề xuất, chờ chủ dự án quyết tại T-04/T-05.

1. V-01/02/03 — kiểm chứng ba nghi vấn webapp (chỉ viết test, chưa sửa code)
2. R-04 — `source` thật trong lineage + `official` phụ thuộc nguồn dữ liệu
3. T-06A — ghim thư viện + ghi môi trường vào run record *(đã có trong roadmap)*
4. R-02 — đấu nối FS-02/06/12 + chính sách verdict khi FS UNKNOWN
5. R-03 — đấu nối B/C/D, ablation, volume z-score, coverage, XIRR; bootstrap về 1000
6. R-01 — sửa vòng đời Crash ladder
7. R-07 — manifest_hash / simulation_seed / code_commit / created_at
8. R-08 — regime không exit trên dữ liệu thiếu; siết định nghĩa INVALID
9. R-09 — bổ sung test §19/§21 còn thiếu
10. R-05 — quyết định phạm vi Execution State machine (cần ADR)
11. R-06 — mở rộng parity JS ↔ Python *(chặn trước T-10/T-11)*
12. R-10 — ghi các quy ước còn thiếu vào CONVENTIONS
13. R-11 — nhóm LOW
14. S-001/S-002/S-003 → đề xuất V2.2, **không vá V2.1.5**

Mục 2–8 đều nằm trước T-06 (official run) trong đề xuất, vì Master Index §6 cấm chạy lại official
run để làm đẹp kết quả — chất lượng lần chạy đầu rất đáng giá.

## 12. Roadmap Inputs

**Dependencies mới phát hiện:**
- T-06 (official run) nên phụ thuộc thêm R-01…R-04, R-07, R-08 ngoài T-06A đã có.
- T-10/T-11 (app) nên phụ thuộc R-06 (parity) và R-05 (Execution State).
- V-01/02/03 chặn T-09A (sửa lỗi kế toán webapp) — chưa xác minh thì chưa biết sửa gì.

**High-risk areas:**
- Đường đi tới verdict: pipeline đấu nối, failure signal, tính chính thức của run.
- Vòng đời vốn: Crash ladder (F-001), partial fill (F-020).
- Tái lập: ghim thư viện (F-007).

**Suggested first phase (sau T-04):**
Một phase "đóng cổng verdict" gom R-01…R-04, R-07, R-08, T-06A và V-01/02/03 — tất cả đều là
điều kiện để official run có giá trị. Ước lượng: đây là khối lượng lớn hơn một phiên.

**Đề xuất cập nhật risk register:** xem `PROJECT/PROJECT_PROGRESS.md`. RSK-002 và RSK-006 được
S001 xác nhận bằng bằng chứng E1; RSK-004 xác nhận; RSK-005 xác nhận và mở rộng (quy ước không
chỉ nằm ở `verdict.py` mà còn ở ngưỡng FS và phạm vi W5); RSK-003 **vẫn chưa kiểm chứng**.
Bổ sung RSK-007 (pipeline không chạy hạng mục bắt buộc) và RSK-008 (run trên synth được ghi là
official).
