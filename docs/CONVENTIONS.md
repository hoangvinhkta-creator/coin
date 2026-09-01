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
17. **Phạm vi kế toán vốn Smart theo accounting month** (quyết định thiết kế WP-A7, đóng
    F-035 — phương án PA-A của bản triage): `Pool` giữ nguyên vai trò ledger audit lifetime
    append-only (DM §6), đồng thời theo dõi bộ đếm THEO THÁNG (`month_reserved`,
    `month_deployed`, `carry_reserved`) cho pool được engine mở sổ theo tháng (hiện chỉ
    SMART). `smart_reservable` so `ngân_sách_tháng × effective_unlock` với phần đã
    reserve/deploy TRONG THÁNG — cùng phạm vi (DM §5 `monthly_budgets`), kẹp trên bởi
    `available`; "vốn đã execute không relock" (ST §6) giữ nguyên TRONG phạm vi tháng.
    Ranh giới sổ: `open_accounting_month` chạy tại rollover, SAU Month-End settle của tháng
    cũ và TRƯỚC contribution tháng mới (đúng cụm bước 3→5 của BT §19); mở sổ không dịch
    chuyển vốn, không ghi/đổi ledger. **Quy tắc carry-first** cho reserve vắt tháng (nguồn
    duy nhất: crash zone giữ vốn SMART qua ranh giới tháng — Smart ladder luôn hết hạn cuối
    tháng): mọi reserve còn mở tại thời điểm mở sổ trở thành carry; release/deploy rút carry
    TRƯỚC; carry **không ăn và không trả** quyền unlock của tháng mới (vốn đó đã tiêu quyền
    của tháng nó được reserve — đếm lại là tái phạm F-035). Khi carry và lô tháng mới cùng
    tồn tại và nhận diện lô bị lẫn: với release, chiều sai duy nhất là quyền KHÔNG được trả
    (bảo thủ cho strategy — BT §1); với deploy-from-reserved, tổng quyền đã dùng
    (`month_reserved + month_deployed`) không đổi nên vô hại. `deploy_from_available`
    (Base/Month-End) tính vào `month_deployed` của tháng đang mở. Bộ đếm tháng reconcile
    được một cách tất định từ ledger + mốc mở sổ (kiểm bằng test F của WP-A7).
    **Phạm vi hiệu lực của bộ đếm tháng**: bộ đếm chỉ có ngữ nghĩa trên pool đã được
    engine mở sổ (`open_accounting_month` — hiện chỉ SMART). Trên pool không mở sổ
    (BASE/OPPORTUNITY — `month_opened_at is None`) các trường `month_*` tích luỹ không
    ngữ nghĩa; mã tương lai KHÔNG được đọc bộ đếm tháng của pool chưa từng mở sổ
    (follow-up F-E2A7-02, phiên E2 WP-A7).

## Phân loại nguồn dữ liệu trong `lineage.json` (WP-A1/A1.9)

Nguồn dữ liệu được khai báo **tại nơi dataset được tạo** — đó là nơi duy nhất biết dữ liệu
thật sự đến từ đâu — rồi đi vào `lineage.json` cho từng series. `build_lineage()` bắt buộc
nhận `source` (không có giá trị mặc định để quên) và từ chối mọi giá trị ngoài taxonomy.

Taxonomy canonical (`data/dataset.py`):

| Giá trị | Nghĩa | Đủ tư cách official? |
|---|---|---|
| `binance_bulk_archive` | Tải từ `data.binance.vision` (archive tháng) | Có |
| `binance_rest` | Tải qua REST `api.binance.com/api/v3/klines` | Có |
| `synthetic` | `ethdca synth` sinh ra | **Không** (DEC-003) |
| `unknown` | Không xác định được nguồn | **Không** (fail-closed) |

`unknown` không phải một nguồn hợp lệ về mặt nghiệp vụ — nó là trạng thái "chưa chứng minh
được", dùng khi `lineage.json` thiếu và phải dựng lại từ file thô. Nó cố ý KHÔNG đủ tư cách
official: thiếu thông tin phải dẫn tới từ chối, không phải mặc định chấp nhận.

**Series lắp từ nhiều cơ chế.** `fetch_series` lấy các tháng đã hoàn tất từ bulk archive rồi
lấy phần đuôi còn thiếu qua REST, nên một series có thể do cả hai cơ chế đóng góp. Quy ước:
`source` ghi **cơ chế chính** (archive khi có, vì nó cấp các tháng đủ), còn thành phần đầy đủ
nằm ở `source_detail` — danh sách các cơ chế đã thực sự đóng góp, theo thứ tự. Không mất mát
thông tin, và vì cả hai đều là dữ liệu Binance thật nên lựa chọn nhãn này không ảnh hưởng tới
tư cách official.

**Cờ `official` là hàm dẫn xuất, không phải trường ghi được.** Nguồn sự thật duy nhất là
`data.dataset.official_eligibility(raw_dir, lineage)`; `Prepared` gọi nó một lần và mọi gate
dùng chung kết quả. Điều kiện, theo đúng thứ tự kiểm (thứ tự cố định để reason code tất định):

1. lineage tồn tại và đúng dạng;
2. không series trùng lặp, không series lạ ngoài `REQUIRED_SERIES`, không thiếu series nào;
3. mỗi series có `file_hash`;
4. mỗi series có `row_count > 0` — một series canonical rỗng KHÔNG được đọc thành "không có
   tin xấu";
5. mỗi series mang nguồn thuộc `REAL_SOURCES`;
6. mỗi series **phủ đủ khoảng thời gian ĐƯỢC YÊU CẦU** (mục dưới đây, WP-A4);
7. lineage verify được checksum — từng `file_hash` khớp file trên đĩa và `dataset_hash` tái
   lập được từ chính danh sách đó.

Bất kỳ điều kiện nào không thoả đều trả `False` kèm lý do, và lý do đó được ghi vào run
record (`official_reason`). Không tham số, flag CLI hay biến môi trường nào đi vào phép dẫn
xuất này (CHECK-A1-07) — chữ ký `official_eligibility(raw_dir, lineage)` được khoá bằng test.

## Indicator daily bắt buộc và ranh giới DEGRADED / INVALID (WP-A4/A4.1)

Strategy §3 định nghĩa INVALID là "giá/lịch sử ETH **hoặc** indicator bắt buộc không hợp
lệ" nhưng **không liệt kê** tập "indicator bắt buộc". Đây là điểm spec để ngỏ, nên quy ước
được chốt ở đây (`src/eth_dca_os/score.py::REQUIRED_DAILY_INDICATORS`).

**Tiêu chí.** Một indicator là BẮT BUỘC khi engine không thể hình thành một quyết định
Smart/Opportunity có căn cứ nếu thiếu nó — tức nó được đọc trên **đường hành động**, chứ
không chỉ là một sub-component của score. §3 đã nói rõ sub-component thiếu là DEGRADED, nên
gộp sub-component vào tập bắt buộc sẽ xoá mất chính ranh giới mà §3 dựng lên.

| Indicator | Vì sao bắt buộc |
|---|---|
| `close` | Giá/lịch sử ETH. Thiếu giá thì không có gì hợp lệ để quyết. Giá `<= 0` cũng là INVALID, không phải "thiếu". |
| `adr30` | Engine đòi nó để dựng bất kỳ ladder nào (spacing Smart/Opportunity). Thiếu thì không có ladder nào hợp lệ. |
| `return7` | Vừa là sub-component S7, vừa là input phát hiện regime CRASH/STRESSED. Thiếu nó engine không phân biệt được CRASH với NORMAL, mà chính sách hành động phụ thuộc vào phân biệt đó. |

`btc_close` **không** bắt buộc: thiếu BTC chỉ làm hai sub-component W/RP thiếu → DEGRADED,
đúng như §3 mô tả ("giá/lịch sử **ETH**"). Các input sub-factor còn lại (`dd365`,
`ma_ratio`, `percentile365`, `rsi14`, `volume_ratio`, `ethbtc_return30`,
`ethbtc_percentile180`) cũng không bắt buộc — thiếu chúng là DEGRADED.

**Ranh giới.**

| Trạng thái | Điều kiện |
|---|---|
| `GOOD` | Đủ tám sub-factor và đủ indicator bắt buộc. |
| `DEGRADED` | Thiếu một phần sub-component, nhưng indicator bắt buộc còn hợp lệ. Sub-component thiếu đóng góp đúng 0, KHÔNG rescale. |
| `INVALID` | Giá/lịch sử ETH hoặc **một** indicator bắt buộc không hợp lệ. `oscore = NaN` (Data Model §4). Chặn mọi action Smart/Opportunity mới; Base schedule vẫn chạy. |

Định nghĩa TRƯỚC WP-A4 chỉ đặt INVALID khi mất **cả tám** sub-factor (`F-023`). Nó hẹp hơn
§3: thiếu `return7` chỉ làm 2/8 sub-factor NaN, nên luật cũ đọc là DEGRADED và engine tiếp
tục hành động ở đúng những thời điểm §3 yêu cầu dừng.

Fail-closed: khung dữ liệu không mang nổi một cột bắt buộc thì MỌI ngày là INVALID — không
chứng minh được hợp lệ phải đọc thành không hợp lệ.

## Nhãn chất lượng dữ liệu trên purchase record (WP-A4/A4.4, A4.5)

Backtest §18 đòi **tag trên bản ghi**, không phải bộ đếm tổng. Bộ đếm nói CÓ BAO NHIÊU bản
ghi bị ảnh hưởng bởi lỗ hổng dữ liệu; chỉ nhãn mới nói BẢN GHI NÀO — và sau official run
thì câu hỏi cần trả lời là câu thứ hai (`F-025`, `F-032`).

Mỗi purchase record mang `tags` (danh sách) và `missing_candles_before` (số nến 15m thiếu
ngay trước nến thực thi):

| Tag | Khi nào gắn |
|---|---|
| `EXECUTION_DATA_GAP` | Bản ghi được tạo tại nến 15m hợp lệ ĐẦU TIÊN sau một lỗ hổng — mọi quyết định ở đó dựa trên dữ liệu không liên tục. Engine KHÔNG interpolate OHLC để trigger zone (§18); nó chỉ duyệt các nến có thật. |
| `DELAYED_DATA_FILL` | Tranche Base không chạy được ở nến 12:00 local của ngày trigger vì nến đó nằm trong gap, nên được execute ở nến hợp lệ đầu tiên sau đó (ST §9 [F3]). Tranche Base **không bao giờ** bị bỏ vì gap dữ liệu. |

Bộ đếm `counters["execution_data_gap"]` / `counters["delayed_data_fill"]` vẫn còn để đối
chiếu, nhưng chúng phải luôn bằng số bản ghi mang tag tương ứng — test khoá cả hai chiều.

## Độ phủ so với khoảng thời gian được yêu cầu (WP-A4, `OD-A4-01`)

**Vấn đề.** `gap_report` trước WP-A4 chỉ đo lỗ hổng **giữa nến đầu và nến cuối quan sát
được**. Phần thiếu ở HAI ĐẦU vì thế vô hình: một lần `ethdca fetch --start 2020-01-01
--end 2021-01-01` mà archive chỉ có tới tháng 2020-01 và REST bị chặn cho ra 31/366 ngày —
tức thiếu ~92% khoảng được yêu cầu — nhưng tự khai `missing_count = 0` và đi qua
`official_eligibility` với `(True, 'verified')`. Dataset cắt cụt vẫn đủ tư cách official
(`F-E2A1R3-05`).

**Quy ước.** Khoảng thời gian được yêu cầu là **dữ kiện chỉ nơi sản xuất dataset biết** —
file parquet kết quả không mang nó. Vì vậy nó được khai tại nơi tạo dataset và đi vào
`lineage.json` cho từng series:

| Trường | Nghĩa |
|---|---|
| `requested_start` / `requested_end` | Khoảng nửa mở `[start, end)` đã được yêu cầu cho series đó |
| `expected_count` | Số nến kỳ vọng trong khoảng ĐƯỢC YÊU CẦU |
| `missing_count` | `expected_count - row_count`, neo vào khoảng được yêu cầu |
| `missing_head` / `missing_internal` / `missing_tail` | Thiếu ở đầu / giữa / đuôi — để một lần từ chối nói được thiếu **ở đâu** |

`fetch_all` khai theo đúng tham số đã xin (`--start`/`--end`; riêng ETHUSDT 15m bắt đầu từ
2019 theo Backtest §2). `synth.generate` khai tương tự. `build_lineage` khi dựng lại từ file
trên đĩa sẽ **mang theo khai báo cũ** trong `lineage.json` nếu không được truyền khai báo
mới — dựng lại mà đánh rơi khai báo là làm mất provenance, và mất nó là mất luôn khả năng
phát hiện cắt cụt.

**Ngưỡng.** Một series đủ tư cách official khi `missing_count <= expected_count *
MAX_MISSING_RATIO`, hiện `MAX_MISSING_RATIO = 0.01`. Ngưỡng KHÔNG thể đặt bằng 0: dữ liệu
Binance thật có gap do bảo trì sàn, nên ngưỡng 0 sẽ từ chối mọi dataset thật và làm official
run bất khả thi. Ngưỡng đặt thấp và cố định; mọi lần từ chối đều mang theo số đo
(`incomplete_coverage:ETHUSDT_1d=31/366 head=0 internal=0 tail=335`), nên khi T-06 chạy trên
dữ liệu thật, một lần từ chối là **dữ kiện để chủ dự án quyết định**, không phải một hằng số
để nới cho qua.

**Fail-closed khi thiếu khai báo.** Lineage không khai được `requested_start`/`requested_end`
cho một series thì series đó trả `coverage_undeclared:<series>` — "không chứng minh được là
đủ" phải đọc thành KHÔNG ĐỦ, cùng nguyên tắc đã dùng cho dữ liệu rỗng và cho lineage thiếu
series.

**Giới hạn cần biết.** `missing_count` và
`expected_count` là do `build_lineage` tính từ chính file trên đĩa, và `file_hash` khoá bản
ghi vào đúng nội dung file đó. Nhưng người vận hành sửa TAY `lineage.json` để khai một khoảng
yêu cầu hẹp khớp với dữ liệu cắt cụt thì cơ chế này không phát hiện được — cùng một giới hạn
đã công bố ở `F-PRE008-01`, và cùng một biện pháp đối trọng (`ethdca freeze` hai máy theo
DEC-003).

**Giới hạn của quy ước NHÃN NGUỒN (WP-A1/A1.9, mục đầu trang này).** Quy ước đó chứng minh
dữ liệu **khớp với nguồn đã khai và không bị sửa sau khi khai**. Nó không thể phát hiện
người vận hành cố ý dán nhãn `binance_*` lên dữ liệu không phải của Binance — chống điều đó
cần đối chiếu với sàn (`ethdca freeze` hai máy theo DEC-003), nằm ngoài phạm vi WP-A1
(`F-PRE008-01`). Giới hạn về độ phủ nêu ngay trên là **cùng một lớp** với nó.
