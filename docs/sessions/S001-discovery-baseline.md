# SESSION HANDOFF

Session ID:
S001

Task:
T-01, T-02, T-03 — Discovery & Baseline

Task Mode:
SPIKE

Chế độ phiên:
AUDIT — READ ONLY

Project Profile:
PRODUCT

Status:
**S001 PASS WITH FINDINGS**

Ngày:
2026-08-23

## Result

S001 đối chiếu toàn bộ implementation với bộ spec **V2.1.5** theo chín nhóm A–I do chủ dự án
chỉ định. Không sửa một dòng mã sản phẩm nào.

### Kết luận: S001 PASS WITH FINDINGS

Không chọn `S001 PASS` vì có 8 finding HIGH, trong đó 2 finding **bác bỏ** mệnh đề bắt buộc của
Implementation Plan §7.
Không chọn `S001 BLOCKED` vì audit đã hoàn thành đầy đủ phạm vi được giao: chín nhóm A–I đều có
kết luận, 14 mệnh đề bắt buộc đều có phán quyết, và BLK-001 (Binance 403) tuy vẫn còn nhưng
**không chặn compliance audit** — nó chỉ chặn official run, việc không thuộc S001.

### Ba artifact chính

| File | Nội dung |
|---|---|
| `docs/reviews/S001-compliance-matrix.md` | Matrix `SPEC RULE → SPEC LOC → CODE LOC → TEST LOC → EVIDENCE → COMPLIANCE → SEVERITY → NOTES` cho chín nhóm A–I; hai phụ lục: kết luận 14 mệnh đề §7 và bốn hypothesis H1–H4 |
| `docs/reviews/S001-audit-findings.md` | 33 finding theo severity, kèm đề xuất verification/remediation task |
| `docs/reviews/S001-discovery-baseline.md` | Discovery Baseline đủ 12 mục theo template |

### Bức tranh một câu

**Tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không.**

OSCORE và tám sub-factor, unlock, ScoreMultiplier, spacing, phân bổ ladder, bốn bộ ngưỡng gate,
sinh manifest 219/114, chọn chín window và bảng coverage đều khớp spec tới từng hằng số — phần
lớn có test trực tiếp. Nhưng ba cụm vấn đề nằm **trên đường đi tới verdict**:

1. **Đã viết nhưng không được gọi** — Benchmark B/C/D, ablation §2.3, volume z-score §2.4,
   bảng coverage §4, XIRR §16. Spec ghi rõ chúng bắt buộc trong mọi official run.
2. **Vòng đời trạng thái chưa đóng** — Execution State machine không tồn tại; partial fill không
   bao giờ phát sinh; Crash ladder có đường vào nhưng đường ra bị hở.
3. **Tính chính thức và tái lập chưa được bảo vệ** — cờ `official` không nhìn nguồn dữ liệu,
   lineage không ghi source thật, manifest hash không gắn vào run, thư viện không ghim.

## 1. Compliance Matrix

`docs/reviews/S001-compliance-matrix.md`. Phân bố trạng thái:

| Trạng thái | Số dòng |
|---|---|
| PASS | 78 |
| PARTIAL | 19 |
| FAIL | 8 |
| NOT IMPLEMENTED | 14 |
| NOT APPLICABLE | 4 |

`NOT TESTED` được ghi trực tiếp bằng dấu `—` ở cột TEST LOCATION, **không gộp với FAIL**.

## 2. Danh sách finding theo severity

| Mức | Số lượng | ID |
|---|---|---|
| CRITICAL | 0 | — |
| **HIGH** | **8** | F-001 … F-008 |
| MEDIUM | 15 | F-009 … F-027 (một phần) |
| LOW | 7 | F-028 … F-034 |
| INFO / spec defect | 3 | S-001, S-002, S-003 |

Tám finding HIGH:

| ID | Tóm tắt |
|---|---|
| F-001 | Reserve của Crash ladder không bao giờ được giải phóng khi Recovery kết thúc vào trạng thái STRESSED. Vi phạm kép: ST §18.3 và [F1] |
| F-002 | FS-02, FS-06, FS-12 không bao giờ được đánh giá; verdict BUILD vẫn phát ra khi 3/12 failure signal là UNKNOWN |
| F-003 | Benchmark B, C, D cài đặt đúng nhưng pipeline không bao giờ chạy → không thể áp BT §22 |
| F-004 | Chẩn đoán bắt buộc §2.3 (ablation) và §2.4 (volume z-score) không được chạy |
| F-005 | Cờ `official` không kiểm nguồn dữ liệu; lineage ghi `source` là chuỗi cố định → run trên dữ liệu tổng hợp vẫn được ghi là chính thức |
| F-006 | Execution State machine không được cài đặt ở đâu trong `src/` |
| F-007 | Không ghim thư viện; tái lập theo thời gian không được bảo đảm (xác nhận RSK-006) |
| F-008 | Live và backtest dùng hai bản cài đặt; parity chỉ phủ OSCORE tổng (xác nhận RSK-002) |

## 3. Finding nào có bằng chứng chạy thật, finding nào mới là bằng chứng tĩnh

| | Số lượng | Ghi chú |
|---|---|---|
| **E1 — đã chạy thật** | **18/33** | Gồm 7/8 finding HIGH |
| **E0 — bằng chứng tĩnh** | **15/33** | Gồm F-017 (Control F/G), F-018 (thứ tự 18 bước), F-021 ([F5] snapshot), F-024, và nhóm LOW |
| E2 — xác minh độc lập | **0/33** | S001 không có xác minh độc lập. Theo `EVIDENCE_STANDARD.md`, E2 cần một phiên reviewer riêng |

Hai finding được nâng từ E0 lên E1 nhờ script kiểm chứng read-only chạy trong phiên:
- **F-001** — chạy `RegimeTracker` trực tiếp, quan sát chuỗi CRASH → RECOVERY → **STRESSED**
- **F-022** — chạy với đầu vào `None`, quan sát CRASH → RECOVERY trên dữ liệu thiếu

Ba finding được xác nhận bằng đối chiếu chương trình (so chữ ký hàm với lời gọi thật):
**F-002**, **F-003**, **F-004**.

## 4. Spec requirement chưa có test

Danh sách đầy đủ ở `S001-audit-findings.md` mục "Requirement của spec CHƯA CÓ TEST".
Tóm tắt: **§21.3 (Execution và regime) gần như trống** — không có test cho tie-break [F2],
max_zones, cooldown và override, TTL/MISSED, crash funding unavailable, proxy đêm 07:00, hay
"STRESSED không có hiệu ứng execution". Ngoài ra **không có test nào kiểm thứ tự 18 bước**, dù
BT §19 yêu cầu tường minh "phải unit-test được thứ tự đó".

## 5. Code tồn tại nhưng không truy được về requirement V2.1.5

| Code | Nhận định |
|---|---|
| `src/eth_dca_os/live_export.py` | Phục vụ app web, không phục vụ điều khoản nào của bộ backtest. App đang nằm sau cổng verdict chưa mở |
| `random_anchor_control(shift_days=10)` | Tham số và ngữ nghĩa "dịch ±10 ngày" không có trong spec, không ghi ở CONVENTIONS |
| Ngưỡng FS-02 / FS-07 / FS-12 | Hằng số tự đặt (0.5 / 0.30 và 102.0 / 0.80), không truy được về spec |
| `benchmarks._noon_candles` | Dead code, không được gọi |

## 6. Regression từ phiên bản cũ

**Không phát hiện regression kế thừa nào.** Bảy sửa đổi F1–F7 của V2.1.5 đều có dấu vết hiện
thực trong code: [F1] nhãn STRESSED có mặt (dù có lỗi hiệu ứng — F-001), [F2] tie-break ba tầng
có mặt, [F3] delayed data fill có bộ đếm, [F4] ngữ nghĩa chu kỳ Benchmark C có mặt, [F5] snapshot
bất biến có mặt, [F6] đơn vị danh nghĩa có mặt, [F7] được xử lý một phần (xem S-001).

Không tìm thấy code nào bám theo hành vi của V2.1.1–V2.1.4 trái với V2.1.5.

## 7. Blocker

| ID | Trạng thái sau S001 |
|---|---|
| **BLK-001** — không có đường tới dữ liệu Binance | **VẪN CÒN.** Không cố bypass. Không dùng dữ liệu tổng hợp để tạo verdict. Không đổi nguồn dữ liệu. Không tuyên bố Gate 1/2/3 PASS. S001 là compliance audit, không phải strategy validation |
| **BLK-002** — tính năng cảnh báo chưa được đặc tả | **VẪN CÒN.** Giữ nguyên là spec/product gap, không tính là code defect — đúng theo chỉ thị của chủ dự án |
| **MỚI: CHECK-03-01 bị BLOCKED** | Ba nghi vấn webapp đòi dựng ca kiểm thử mới, mà quy tắc S001 số 10 cấm. Chuyển thành verification task V-01/02/03 |

## 8. Risk register cập nhật

| ID | Thay đổi sau S001 |
|---|---|
| RSK-001 | Giữ nguyên (cao) |
| RSK-002 | **XÁC NHẬN (E1)** — parity đo được 7,39e-11 nhưng chỉ phủ OSCORE tổng |
| RSK-003 | **VẪN CHƯA KIỂM CHỨNG** — giữ nguyên E0, chuyển thành V-01/02/03 |
| RSK-004 | **XÁC NHẬN (E1)** — test webapp không chạy được từ checkout sạch |
| RSK-005 | **XÁC NHẬN VÀ MỞ RỘNG (E1)** — quy ước không ghi nhiều hơn dự kiến |
| RSK-006 | **XÁC NHẬN (E1)** = F-007 |
| **RSK-007** (mới) | Pipeline không chạy nhiều hạng mục spec ghi là bắt buộc cho official run |
| **RSK-008** (mới) | Run trên dữ liệu tổng hợp vẫn được ghi nhận là official |
| **RSK-009** (mới) | Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn |

## 9. Đề xuất remediation task — CHƯA THỰC HIỆN

Bảng đầy đủ ở `S001-audit-findings.md` mục cuối. Tóm tắt thứ tự đề xuất:

**Trước T-06 (official run):** V-01/02/03, R-04 (`source` + `official`), T-06A (ghim thư viện),
R-02 (FS còn thiếu), R-03 (đấu nối B/C/D + chẩn đoán + coverage + XIRR + bootstrap 1000),
R-01 (vòng đời Crash ladder), R-07 (manifest_hash/simulation_seed/created_at),
R-08 (regime không exit trên dữ liệu thiếu).

**Trước T-10/T-11 (app):** R-06 (mở rộng parity), R-05 (quyết định Execution State — cần ADR).

**Song song:** R-09 (bổ sung test §19/§21), R-10 (ghi quy ước còn thiếu), R-11 (nhóm LOW).

**Đưa vào đề xuất V2.2, không vá V2.1.5:** S-001, S-002, S-003.

Không finding nào được tự giải quyết trong S001.

## Completion Gate Summary

| Task | Required | PASS | BLOCKED | Kết quả |
|---|---|---|---|---|
| T-01 | 6 | 6 | 0 | **DONE** |
| T-02 | 6 | 6 | 0 | **DONE** |
| T-03 | 5 REQUIRED + 1 RECOMMENDED | 5 | 1 | **BLOCKED** |

**T-03 không đạt DONE** và điều đó là đúng, không phải thiếu sót.
`TASK_COMPLETION_GATE_STANDARD.md` quy định bất kỳ REQUIRED check nào ở trạng thái BLOCKED đều
chặn DONE. CHECK-03-01 yêu cầu kiểm chứng ba nghi vấn bằng ca chạy thật, nhưng quy tắc S001 số 10
của chủ dự án cấm viết test mới trong phiên audit. Đây là **xung đột có chủ đích giữa Ready Gate
của task và quy tắc phiên** — được ghi nhận trung thực thay vì hạ tiêu chí để task trông "xong".

## Verification Evidence

| Check ID | Status | Evidence Level | Evidence | Timestamp |
|---|---|---|---|---|
| CHECK-01-01 | PASS | E1 | 69 passed / 0 failed / 0 skipped / 0 error, 372,63s. `git log e368425..HEAD -- src/ tests/` rỗng → mã đo được vẫn là mã hiện tại | 2026-08-23 |
| CHECK-01-02 | PASS | E1 | Bốn validator chạy lại trong S001, đều PASS | 2026-08-23 |
| CHECK-01-03 | PASS | E1 | Quét `git log --all -p`: mọi khớp đều là văn bản tài liệu governance. Không `.env`/`.pem`/`.key` nào từng tồn tại | 2026-08-23 |
| CHECK-01-04 | PASS | E1 | H1–H4 đều XÁC NHẬN, phụ lục trong compliance matrix | 2026-08-23 |
| CHECK-01-05 | PASS | E0 | Discovery Baseline đủ 12 mục | 2026-08-23 |
| CHECK-02-02 | PASS | E1 | `ethdca freeze`: 19 → 18, 200, denominator 219; Gate 3 14 + 100 = 114 | 2026-08-23 |
| CHECK-02-03 | PASS | E1 | 14 mệnh đề: 5 XÁC NHẬN, 6 một phần, **2 BÁC BỎ**, 2 KHÔNG KẾT LUẬN ĐƯỢC | 2026-08-23 |
| CHECK-03-01 | **BLOCKED** | E0 | Không thực hiện được — quy tắc S001 số 10 cấm viết test mới | 2026-08-23 |
| CHECK-0x-06 | PASS | E1 | `git status --porcelain`: không mục nào thuộc `src/`, `webapp/`, `tests/`, `docs/spec/` | 2026-08-23 |

## Files Changed

Created:
- `docs/reviews/S001-compliance-matrix.md`
- `docs/reviews/S001-audit-findings.md`
- `docs/reviews/S001-discovery-baseline.md`
- `docs/sessions/S001-discovery-baseline.md`

Modified:
- `PROJECT/PROJECT_PROGRESS.md` (trạng thái task, 3 risk mới, session history)
- `PROJECT/PROJECT_DECISIONS.md` (DEC-006)
- `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động bằng script)
- `docs/tasks/T-01…T-03` (trạng thái + kết quả Completion Gate)

**Không file nào trong `src/`, `webapp/`, `tests/`, `docs/spec/` bị sửa.**

## Key Decisions

- **DEC-006** — Source of Truth cho compliance audit là **V2.1.5**, không phải V2.1.3.
  Chủ dự án đã chọn sau khi agent nêu `CONFLICT DETECTED` kèm ba bằng chứng.
- **DEC-005 giữ nguyên PENDING** — S001 không tự chốt. Bằng chứng và khuyến nghị cho T-05 đã
  được chuẩn bị nhưng trạng thái quyết định không đổi, đúng chỉ thị của chủ dự án.

## Do Not Change Yet

Chủ dự án đã yêu cầu: **không chuyển sang S002 và không sửa finding nào sau khi hoàn thành audit
nếu chưa có chỉ thị tiếp theo.**

Cụ thể, KHÔNG được làm nếu chưa có chỉ thị:
- Sửa bất kỳ finding nào, kể cả F-001 dù đã có bằng chứng chạy thật
- Mở T-04 hoặc bất kỳ task nào của Phase 2
- Đưa các task R-01…R-11 và V-01…V-03 vào bảng roadmap — theo
  `00_SESSION_ORCHESTRATION.md` mục "Roadmap Change Rule", tái cấu trúc roadmap phải đi qua khối
  `ROADMAP CHANGE PROPOSAL` và được chủ dự án chấp thuận
- Sửa `docs/spec/` — Master Index §6 cấm vá tại chỗ; S-001/S-002/S-003 phải đi qua V2.2
- Chạy official run — BLK-001 vẫn còn, và 8 task được đề xuất làm trước T-06 chưa được duyệt

## Next Recommended Session

**S002 — Roadmap Finalization (T-04)** — nhưng **chỉ khi chủ dự án ra chỉ thị**.

Nội dung đề xuất cho S002:
1. Chốt DEC-005 (T-05) — nhiều đề xuất remediation phụ thuộc quyết định này
2. Xếp thứ tự 33 finding thành task chính thức, tính routing bằng `routing_engine.py`
3. Trình `ROADMAP CHANGE PROPOSAL` cho phase "đóng cổng verdict"
4. Đóng băng Completion Gate cho các task được duyệt

Việc có giá trị nhất chủ dự án có thể làm song song và không cần agent: chuẩn bị máy hoặc VPS
truy cập được Binance cho T-06.

## Files Next Agent Should Read

- `CLAUDE.md`
- `PROJECT/PROJECT_PROFILE.md`
- `PROJECT/PROJECT_PROGRESS.md`
- `PROJECT/PROJECT_DECISIONS.md` (đặc biệt DEC-005 PENDING và DEC-006)
- `docs/reviews/S001-compliance-matrix.md`
- `docs/reviews/S001-audit-findings.md`
- `docs/reviews/S001-discovery-baseline.md`
- `docs/spec/00_MASTER_INDEX_V2_1_5.md` — precedence và freeze rule
