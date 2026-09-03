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
18. **Thứ tự xử lý trong một nến 15m — các điểm BT §19 để ngỏ** (quyết định WP-A6, đóng
    F-018/F-019): engine thi hành đúng 18 bước theo CHỮ của BT §19 và
    `tests/test_wp_a6_processing_order.py` khoá thứ tự đó bằng quan sát side-effect thật
    (`tests/wp_a6_order_harness.py`: ledger pool, chuyển trạng thái zone/ladder, fill, regime;
    dãy số bước trong mỗi nến không được giảm). Những điểm §19 không nói rõ, engine chốt:
    (a) **Bước 16 và 17 là một giao dịch nguyên tử cho từng fill** (deploy ledger rồi ghi
    purchase kèm fee/slippage, cập nhật cooldown và `last_exec_price`); test không phán xét
    thứ tự bên trong nhóm 16/17. Cooldown do fill của nến N chỉ có hiệu lực từ bước 11 của
    nến N+1 (bước 11 đọc trước bước 14 và 17 trong cùng nến) — action mới của nến N không
    bị fill cùng nến chặn.
    (b) **Bước 15** ("execution priority Base → Smart → Opportunity") sắp các fill tới hạn
    theo cùng khoá `zone_order_key` của bước 14. Mỗi zone tiêu đúng phần reserve của nó nên
    ưu tiên chỉ quyết định thứ tự ghi sổ trong nến, không quyết định lượng vốn (đo: chỉ khác
    ở mức ULP do đổi thứ tự phép cộng dấu phẩy động trong ledger — 11/543 bản ghi lệch
    ≤ 3e-16 tương đối, ETH tổng trùng bit).
    (c) **Tạo ladder mới là "tạo reservation" của bước 14, SAU bước 13** (Smart/Opportunity
    theo #1, #2; Crash theo ST §14). Zone của ladder tạo ở nến N chỉ được xét trigger từ
    nến N+1. Trước WP-A6 ladder được tạo TRƯỚC bước 13, và vì zone đầu (S0/C0/O0) có
    target = anchor = OPEN nến tạo mà LOW ≤ OPEN luôn đúng, zone đầu của MỌI ladder trigger
    ngay trong nến tạo (đo: 88/88 ladder trên dataset tổng hợp 7,5 năm). Với Crash: cancel/
    release Opportunity zone xung đột và đo snapshot [F5] vẫn ở bước 10 ("tại thời điểm vào
    CRASH", ST §14); chỉ việc tạo ladder và reserve dời xuống bước 14a, trước 14b (Smart/
    Opportunity) và 14c (TRIGGERED → ACTION_PENDING). Tác động đo được của riêng điểm này
    (cùng seed/dataset/config, cửa sổ 2019-01-01 → 2026-06-01): ETH 21,6370346 → 21,6486587
    (+0,054 %) với `gate1_low_friction`, +0,064 % với `gate3_realistic`; purchase 543 → 541
    (Smart zone 153 → 152, Opportunity 17 → 16); nominal BASE 4450 / SMART 4270,21 / CRASH
    139,57 KHÔNG đổi, Opportunity 5,823 → 5,743; số ladder tạo 67/14/17 không đổi; phân kỳ
    đầu tiên đúng tại fill S0 của ladder đầu tiên (2019-01-04 07:30 → 07:45, lùi một nến).
    (d) **Bước 12** chỉ xác định action tới hạn và áp TTL/MISSED — kể cả dịch chuyển
    RESERVED → AVAILABLE của ST §8 cho MISSED (spec đặt "đánh dấu MISSED" ở bước 12); vốn
    được release ở bước 12 có thể được reserve lại ở bước 14 cùng nến.
    (e) **Bước 18 gom**: bullish invalidation trên daily close vừa kích hoạt ở bước 8 (ladder
    tạo ở bước 14 của cùng nến chưa tồn tại khi daily close đó hoàn tất nên không bị đếm —
    giữ đúng "hai daily close hoàn chỉnh liên tiếp" ST §18.2), hysteresis Opportunity
    (suspend/reactivate/cancel sau 7 ngày, ST §5), suspension khi vào RECOVERY và cancel khi
    hết Recovery (ST §18.3), expiry Opportunity 90 ngày, completion. Zone đã thành
    ACTION_PENDING ở bước 14 cùng nến không bị suspension (chỉ ACTIVE → SUSPENDED) nhưng vẫn
    bị cancel bởi invalidation/recovery-end (`cancel_open_zones`). Trước WP-A6 các mục này
    chạy ở bước 8/10 (trước 13); đo: dời xuống 18 không đổi một bản ghi nào (543/543 trùng
    khớp, cả hai exec config).
    (f) **Month-End**: Day 25 và Day 28 12:00 là sự kiện theo lịch nằm trong khe bước 9 (cùng
    đồng hồ với Base schedule; #7). Bước 3 tại rollover là đường đóng sổ còn lại: fallback
    khi nến 12:00 Day 28 nằm trong gap, và cho vốn Smart được release sau Day 28 (ví dụ crash
    zone bị cancel). Hai đường không settle đúp và không mất vốn
    (`test_a6_month_end_two_paths_settle_once`). BT §19 không có khe cho Day 25/28 → ghi
    chú WP-D2 bên dưới.
19. **Zone TRIGGERED trong chu kỳ dữ liệu INVALID (H-15)** — quyết định WP-A6: **GIỮ
    NGUYÊN**. Bước 13 đọc giá 15m, không đọc chất lượng daily; INVALID chặn ở bước 14 (ST §3:
    "chặn mọi action Smart và Opportunity **mới**"). Zone TRIGGERED giữ trạng thái qua chu kỳ
    INVALID và thành action ở chu kỳ hợp lệ đầu tiên — cùng cơ chế giữ-TRIGGERED của
    max_zones (ST §15.1) và cooldown (#6), và khớp `CHECK-A4-02` (FROZEN). Căn cứ đo: dataset
    tổng hợp 7,5 năm với một hàng daily bị xoá (2020-06-15 → cửa sổ INVALID 31 ngày theo
    adr30, 1,14 % số nến): **0** zone trigger trong chu kỳ INVALID ở cả engine hiện tại lẫn
    biến thể "huỷ trigger khi INVALID"; hai biến thể cho kết quả trùng khớp hoàn toàn (528
    purchase, ETH 21,634883…). Ở mức kịch bản
    (`test_h15_trigger_in_invalid_cycle_persists_until_first_valid_cycle`): trigger trong
    ngày INVALID được thực thi ở giá của chu kỳ hợp lệ đầu tiên (100) dù target zone là
    94,6 / 89,2 — đó là cái giá của quy ước; phương án ngược lại sẽ không mua. Spec không quy
    định điểm này → ghi chú WP-D2. Điều kiện xem lại (H-15, vế thứ ba): official run cho
    thấy action trên zone trigger trong cửa sổ INVALID với số lượng đáng kể — công cụ
    `tests/wp_a6_impact_tool.py` đếm sẵn (`invalid_cycle_triggers_actioned`).

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

## Ghi chú cho WP-D2 từ WP-A6 (đề xuất V2.2 — KHÔNG vá V2.1.5, Master Index §6)

Các điểm dưới đây là chỗ BT §19 / ST **không nói** hoặc nói chưa đủ; WP-A6 đã chốt bằng quy ước
#18/#19 (có số đo) để engine chạy được, và ghi lại đây để WP-D2 đưa vào đề xuất V2.2. Không
mục nào là task mới; không mục nào sửa spec.

- **D2-A6-1 — Khe cho sự kiện Month-End Day 25/28.** BT §19 bước 3 chỉ nói "đóng sổ cuối
  tháng" tại rollover; ST §10 lại định nghĩa Day 25–27 và Day 28 12:00. Engine đặt hai sự
  kiện này trong khe bước 9 (#18f). Đề nghị V2.2 ghi tường minh vị trí của chúng trong §19.
- **D2-A6-2 — Vị trí "tạo ladder mới" trong 18 bước.** §19 không có bước "tạo ladder"; WP-A6
  đọc "tạo reservation" của bước 14 là nơi đó (theo F-018), nên zone đầu S0/C0/O0 (= anchor =
  OPEN nến tạo, #1) không trigger trong nến tạo mà từ nến kế tiếp (#18c, tác động đã đo:
  +0,054 %/+0,064 % ETH, −2/543 fill). Đề nghị V2.2 ghi tường minh, kèm ngữ nghĩa của S0
  ("mua ngay tại anchor" hay "limit tại anchor từ nến kế tiếp") vì hai cách đọc cho kết quả
  khác nhau.
- **D2-A6-3 — Số phận trigger phát hiện trong chu kỳ INVALID (H-15).** ST §3 chỉ chặn
  "action mới"; không điều khoản nào nói trigger phát hiện lúc INVALID có sống sót không.
  WP-A6 giữ nguyên (#19) với căn cứ đo là 0 lần xảy ra trên dataset tổng hợp có cửa sổ
  INVALID 31 ngày. Đề nghị V2.2 quyết định tường minh, cân nhắc rằng một hàng daily thiếu
  tạo cửa sổ INVALID dài (31 ngày do `adr30`, WP-A4/S010) mà vẫn đủ tư cách official
  (`MAX_MISSING_RATIO` = 1 %), nên action trên trigger cũ có thể thực thi ở giá rất xa target.
- **D2-A6-4 — Month-End Smart settle có tính là "execution" cho cooldown?** (quan sát ngoài
  phạm vi thứ tự, WP-A6 KHÔNG quyết định.) `record_purchase` ghi settle Month-End với nguồn
  SMART nên đặt cooldown 48h (ST §15: "cooldown sau execution Smart/Opportunity/Crash"). Khi
  settle rơi vào đường fallback tại rollover (#18f), cooldown tràn sang 48h đầu tháng mới và
  chặn zone đầu của Smart ladder mới (đo trong `test_a6_month_end_two_paths_settle_once`:
  kịch bản B không có fill S0 ngày 01/04, kịch bản A có). Spec không nói Month-End settle có
  phải "execution" theo nghĩa cooldown hay không.
