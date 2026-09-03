# S017 — WP-A1: repair cycle cuối (`DEC-027`), đóng ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED`

Ngày: 2026-09-03
Nhánh: `claude/coindca-data-stream-vv0vwv`
Baseline nhánh này: `61cf54b` (lát cắt WP-B1 theo `DEC-026`, S016)
Task: `docs/tasks/WP-A1-provenance-va-tai-lap.md`
Capability: `CAP-PROV` (lineage root `WP-A1`)
Authority: `DEC-027` (`OD-A1-02`) — `OWNER_EXTENSION` +1 repair cycle
Model/Effort canonical: **Tier C / Opus / `xhigh`** — phiên chạy đúng Tier C (Opus 5).

## 0. Vì sao chu kỳ này tồn tại

Ba hạng mục treo từ 2026-09-01: E2 vòng ba của WP-A1 FAIL, `CAP-PROV` hết budget
(`DEC-012`: allowed 2 / used 2 / remaining 0, `OWNER_EXTENSION = NOT GRANTED`), nên ba hạng
mục rơi vào `LEGACY_GATE_DISPOSITION_REQUIRED` chờ đúng một hành động của chủ dự án. `WP-A1`
là mắt xích **duy nhất** còn lại của `GATE-A` sau khi `WP-A5` DONE tại S015.

Chủ dự án chọn `OWNER_EXTENSION` cho hai hạng mục cần production code (gộp **một** chu kỳ), và
docs-only cho hạng mục thứ ba.

## 1. Điểm cốt lõi của `F-E2A1-03` — vì sao không thể hoãn

Không phải vì mức độ nghiêm trọng. Các con số của một run có provenance suy biến **vẫn đúng**;
thứ mất đi là khả năng chứng minh *về sau* mã nào sinh ra chúng. Điều làm nó không thể hoãn là
**Master Index §6 cấm chạy lại official run**: nếu `T-06` chạy trong tình trạng này, provenance
mất **VĨNH VIỄN**, không có đường vá.

Vì vậy bản sửa chọn **fail loud TRƯỚC khi ghi**, không phải ghi rồi cảnh báo:

```
save_run(...)
  ├─ phân giải code_commit + dependency_lock_hash        <- TRƯỚC mọi thao tác ghi
  ├─ official=True và một trong hai không phân giải được ->  ProvenanceUnresolvedError
  │                                                          (chưa file nào được tạo)
  └─ ngược lại: ghi metrics + record, kèm provenance_resolved / provenance_unresolved
```

Chi phí của việc nổ ở đây là chạy lại một lần trong môi trường đúng. Chi phí của việc ghi im
lặng là một official run không tự chứng minh được và **không sửa được**. Đây là lý do
`test_a1r_b1_nothing_is_written_when_provenance_unresolved` tồn tại: nó khẳng định không có
`backtest_runs.jsonl` và không có `*_metrics.json` nào sót lại sau khi từ chối — nếu artifact
đã kịp ghi rồi mới nổ thì bản sửa vô nghĩa.

**Hệ quả vận hành cần chủ dự án biết trước `T-06`:** official run bắt buộc chạy từ một **git
checkout có lockfile**, không phải từ một bản sao mã trần. `BLK-001` dự kiến chạy trên máy chủ
dự án hoặc VPS nước ngoài — nếu môi trường đó không thoả, `save_run` sẽ từ chối. Đây là ràng
buộc mới, có chủ đích, và nó giao thoa với điều kiện 4 của `T-06`
("production-realistic real-data execution path").

Ranh giới của bản sửa: fail-loud chỉ áp cho đường **official**. Run dev trong môi trường không
có git vẫn chạy được — nhưng record nay mang `provenance_resolved: false` và
`provenance_unresolved: [...]`, thay vì để người đọc tự biết rằng `"unknown"` / `"no-lockfile"`
là giá trị suy biến. Đó chính là chữ "im lặng" trong tên finding.

## 2. `F-E2A1R3-03` — vi phạm một hợp đồng đã FROZEN

Contract PRE-S008 case 13 (FROZEN 2026-08-25) đặc tả chính xác: `dev_limit != None` →
`official = False`, `official_reason = 'dev_limit_set'`, enforcement point
`pipeline.run_gate1/2/3`, test `T-EC-13`, và `MUTATION-5` phải làm suite đỏ.

Hiện trạng trước chu kỳ này: cờ `official` **đúng** (fail-closed), nhưng lý do vẫn là lý do của
dataset (`'verified'`), nên nguyên nhân `dev_limit` bị che hoàn toàn; mã `dev_limit_set` không
tồn tại trong `src/`. Đây là rủi ro **diễn giải**, không phải rủi ro tính toán — nhưng
`RISK_MODEL.md` xếp vi phạm một FROZEN contract mà Completion Gate phụ thuộc là BLOCKING **bất
kể severity**.

Một quyết định thiết kế đáng ghi: khi dataset **tự nó** đã không đủ tư cách, lý do GỐC của
dataset được giữ, không bị `dev_limit_set` che. Hợp đồng chỉ định nghĩa case 13 trên nền ca
(12) hợp lệ; che một nguyên nhân sâu hơn bằng một mã nông hơn sẽ lặp lại **đúng** khiếm khuyết
đang được sửa, chỉ đổi chiều. Có test riêng khoá điều này
(`test_a1r_b2_ineligible_dataset_keeps_its_own_reason`).

Ba ca đối chứng chặn bản sửa lười: không có `dev_limit` thì reason vẫn `verified`; dataset
không hợp lệ giữ lý do gốc; và `dev_limit_set` **không** được cài vào `official_eligibility`
(sai tầng — sẽ làm dataset bị coi là không hợp lệ ngay cả khi không chạy dev).

## 3. `F-E2A1R3-06` + `F-E2A1-08` — đóng ở chi phí budget bằng 0

Đóng hoàn toàn bằng `docs/CONVENTIONS.md`, **production diff = 0**, không tiêu repair cycle
riêng (tiền lệ ledger: Decision pack PRE-S008, `2f20e6c..bd7c5ff`). Nội dung: ghi **hai TẦNG**
nhãn nguồn — bảng bốn giá trị là nhãn **series** và quyết định tư cách official; `mixed` là
nhãn **dataset-level, chỉ mô tả**, KHÔNG phải lối tắt qua cổng official vì
`official_eligibility` kiểm per-series với `REAL_SOURCES`. Bổ sung hai mã lý do chưa từng được
ghi: `empty_series`, `source_not_real`.

Một mục trong bản disposition hoá ra **không cần sửa**: "mã lý do lỗi thời trong Evidence
`CHECK-A1-06`" — kiểm lại thì Evidence đó đang ghi `source_not_real:BTCUSDT_1d='synthetic'`,
đúng hiện trạng mã. Không sửa thừa, và ghi lại việc đã kiểm để lần sau không phải kiểm lại.

## 4. Trình tự thi hành — vì sao KHÔNG chạy song song với nhánh A

`DEC-027`/Owner Checkpoint cho phép hai nhánh chạy song song *"nếu governance/session
architecture cho phép"*. Ở đây **không cho phép** với phần production: hai nhánh dùng chung một
working tree, mà cả hai đều phải nộp bằng chứng "full suite" và "pipeline đủ phase trước/sau".
Sửa `pipeline.py`/`reporting.py` trong lúc nhánh A đang đo sẽ làm nhiễm bằng chứng của cả hai,
và các test đỏ theo phương pháp test-first của nhánh B sẽ làm full suite của nhánh A đỏ oan.

Vì vậy: B.3 (docs-only, không ảnh hưởng phép đo) làm trước; B.1 + B.2 làm **sau khi** nhánh A
hoàn tất và đã commit (`61cf54b`). Hệ quả có lợi: `pipeline_AFTER` của nhánh A chính là
`pipeline_BEFORE` của nhánh B — cùng một phép đo, không phải chạy lại.

## 5. Bằng chứng

**Test-first.** Toàn bộ 9 ca ĐỎ trước khi sửa (`a1r_RED.log`, `EXIT=1`), chữ ký rõ ràng
`AssertionError: assert 'verified' == 'dev_limit_set'`; 4 ca đối chứng xanh sẵn từ đầu. Sau khi
sửa: **13/13 PASS** (`a1r_GREEN.log`, `EXIT=0`).

**Không phá test cũ.** `test_wp_a1_provenance.py` + `test_wp_a1_eligibility_contract.py` +
`test_cli.py`: **50/50 PASS**, exit 0.

**Full suite / pipeline trước-sau / production diff:** xem §6.

## 6. Số đo cuối

**Full suite:** `python -m pytest tests/ -q -p no:cacheprovider` → **377 test, 377 PASS,
0 FAILED, 0 ERROR, `EXIT=0`**. Đếm khớp: 365 (sau lát cắt WP-B1, `61cf54b`) + 12 test mới của
`tests/test_wp_a1_legacy_gate_repair.py` = 377.

**Pipeline đủ phase TRƯỚC / SAU** (synthetic, dev_limit 25 — KHÔNG official). `TRƯỚC` lấy trực
tiếp từ lần chạy `AFTER` của nhánh A (`b1/pipeline_AFTER.log`) — cùng một phép đo, không chạy
lại:

| | TRƯỚC (`61cf54b`) | SAU |
|---|---|---|
| 12 signal | 02,03,04,08,12 = true; còn lại false | **y hệt** |
| `UNKNOWN` | `[]` | **y hệt** |
| VERDICT | `DO_NOT_BUILD` `['Gate 1 FAIL']` | **y hệt** |

⇒ Chu kỳ này **không đổi một giá trị tính toán nào**, đúng như thiết kế: B.1 chỉ chạm đường
ghi provenance, B.2 chỉ chạm chuỗi `official_reason`. Lưu ý cách đọc: dataset của lần chạy này
là synthetic nên `official_eligible = False`, và `_official_reason` đi đúng nhánh "giữ lý do
GỐC của dataset" (`source_not_real:...`) chứ không phải `dev_limit_set` — tức nhánh phòng thủ
mà `test_a1r_b2_ineligible_dataset_keeps_its_own_reason` khoá lại cũng được chạy thật trong
pipeline, không chỉ trong unit test.

**Không phá test cũ:** `test_wp_a1_provenance.py` + `test_wp_a1_eligibility_contract.py` +
`test_cli.py` → **50/50 PASS**, exit 0. `test_a1_01` (assertion CỨNG bác `"unknown"` /
`"no-lockfile"`) và `test_a1_09` (tái lập `code_commit`) đều xanh — hai test này chạm đúng vùng
mã B.1 sửa.

**Production diff (chu kỳ này):** 2 file.

    src/eth_dca_os/pipeline.py  | +24 −3
    src/eth_dca_os/reporting.py | +48 −2

`git diff` trên `engine.py`, `regime.py`, `ladders.py`, `capital.py`, `score.py`, `gates.py`,
`verdict.py`, `metrics.py` = **rỗng** ⇒ không đụng logic financial/algorithm (`DEC-027` điểm 3).
B.3 đóng góp **0 dòng** production.

## 7. Phát sinh — `H-26` (HARDENING, không sửa trong chu kỳ này)

Quan sát từ phiên S016 và được phiên này kiểm chứng chính xác: `evaluate_gate1`/`evaluate_oos`
trả cờ `pass` kiểu `numpy.bool` khi đầu vào là `numpy.float64` (đúng cái pipeline thật sinh
ra), nên `x is True` cho `False` — **cùng họ** với `F-S015-01`. Hôm nay **vô hại** vì
`verdict.py` đọc cờ này bằng truthiness (`not oos["pass"]`), vốn đúng với numpy bool.

Phân loại HARDENING chứ không BLOCKING: có production path, nhưng **không** có hậu quả nghiệp
vụ ở hiện trạng. Ghi `PROJECT/HARDENING_BACKLOG.md` **H-26** kèm ba điều kiện re-trigger. Không
sửa trong chu kỳ này — ngoài mục tiêu mà `DEC-027` đặt cho extension, và `gates.py` ngoài
Expected Touch Area của `WP-A1`.

## 8. Còn lại

- `CHECK-A1-11` là **E2**: cần một phiên reviewer độc lập xác nhận ba hạng mục đã đóng, trước
  khi chủ dự án xét `WP-A1 → DONE`. Phiên này **không** tự đánh `CHECK-A1-11` = PASS.
- `CAP-PROV` budget lại về `REMAINING = 0` — mọi hạng mục cần production code từ đây cần một
  `OWNER_EXTENSION` mới. Rà soát E2 tự nó không tiêu repair cycle; nhưng nếu E2 phát hiện defect
  mới cần sửa mã thì cần extension.
- `GATE-A` chỉ đóng khi `WP-A1` DONE.
