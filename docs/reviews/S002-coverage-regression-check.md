# S002 — ĐỐI CHIẾU ĐỘ PHỦ VÀ KIỂM TRA HỒI QUY CỦA LỘ TRÌNH

Phiên: S002 · Task: T-04 — Chốt lộ trình và đóng băng tiêu chí · Ngày: 2026-08-23
Mức bằng chứng: **E1** — mọi bảng dưới đây được sinh bằng script đối chiếu chạy thật trên nội dung
16 file định nghĩa task, không phải bằng cách đọc rồi tự tin.

Mục đích: chứng minh việc chuyển 15 work package thành 15 file định nghĩa task **không làm rơi**
finding, rủi ro, dependency, quyết định hay stopping rule nào — và **không làm phình** work package
nào sang remediation ngoài phạm vi RCP-001.

---

## 1. Nguồn đối chiếu

| Nguồn | Vai trò |
|---|---|
| `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` | Định nghĩa 15 work package và ánh xạ finding |
| `docs/reviews/S001-audit-findings.md` | Danh mục finding gốc |
| `docs/reviews/S001-compliance-matrix.md` | 14 mệnh đề bắt buộc, 4 hypothesis |
| `PROJECT/PROJECT_PROGRESS.md` | Bảng roadmap chuẩn, rủi ro, blocker, quyết định |
| `PROJECT/PROJECT_DECISIONS.md` | DEC-003, DEC-005, DEC-007, DEC-008, DEC-009 |

---

## 2. Ánh xạ finding → work package (đầy đủ, không mục nào rỗng)

Ownership được xác định từ mục `## Đóng finding` của từng file task.

| Finding | Work package | Finding | Work package |
|---|---|---|---|
| F-001 | WP-A3 | F-018 | WP-A6 |
| F-002 (đo lường) | WP-A5 | F-019 | WP-A6 |
| F-002 (chính sách) | WP-B1 | F-020 | WP-C3 |
| F-003 | WP-A2 | F-021 | WP-A3 |
| F-004 | WP-A2 | F-022 | WP-A3 |
| F-005 | WP-A1 | F-023 | WP-A4 |
| F-006 | WP-C2 | F-024 | WP-B3 |
| F-007 | WP-A1 | F-025 | WP-A4 |
| F-008 | WP-C4 | F-026 | WP-B1 |
| F-009 | WP-A1 | F-027 | WP-C1 |
| F-010 | WP-A1 | F-028 | WP-D1 |
| F-011 | WP-A1 | F-029 | WP-D1 |
| F-012 | WP-A2 | F-030 | WP-A3 |
| F-013 | WP-A2 | F-031 | WP-D1 |
| F-014 | WP-A2 | F-032 | WP-A4 |
| F-015 | WP-B1 | F-033 | WP-B3 |
| F-016 | WP-A5 | F-034 | WP-D1 |
| F-017 | WP-B1 | | |
| V-01 | WP-C1 | S-001 | WP-D2 |
| V-02 | WP-C1 | S-002 | WP-D2 |
| V-03 | WP-C1 | S-003 | WP-D2 |

**Kết quả:** 40/40 định danh (34 × `F-xxx`, 3 × `V-xx`, 3 × `S-xxx`) đều có đúng một nơi thuộc về.
Danh sách "không có owner" là **rỗng**.

### Ba trường hợp xuất hiện ở hai file — đã kiểm từng cái

| ID | Xuất hiện tại | Kết luận |
|---|---|---|
| F-002 | WP-A5 và WP-B1 | **Chia có chủ đích** theo RCP-001 §2: phần đo lường ở lớp A, phần chính sách ở lớp B. Cả hai file đều ghi rõ ranh giới trách nhiệm |
| F-019 | WP-A6 (sở hữu), WP-B2 (loại trừ) | WP-B2 ghi "**Không đóng** F-019 — mục đó thuộc WP-A6". Không phải sở hữu kép |
| F-029 | WP-D1 (sở hữu), WP-C3 (liên quan) | WP-C3 ghi "Liên quan (**không đóng ở đây**): F-029 ... thuộc WP-D1". Không phải sở hữu kép |

---

## 3. Ánh xạ rủi ro → work package

| Rủi ro | Mức | Gói chịu trách nhiệm | Ghi chú |
|---|---|---|---|
| RSK-001 — mất lịch sử giao dịch thật | cao | **T-09B** (không phải WP) | WP-C1 liên kết qua escalation trigger |
| RSK-002 — hai bản cài đặt trôi khỏi nhau | cao | **WP-C4** | |
| RSK-003 — ba nghi vấn kế toán webapp | trung bình | **WP-C1** | Xác nhận hoặc bác bỏ, không để lửng |
| RSK-004 — test webapp không chạy từ checkout sạch | trung bình | **WP-C1** | |
| RSK-005 — quy ước ngoài spec trong đường ra verdict | trung bình | **WP-B1** | |
| RSK-006 — không ghim thư viện | cao | **WP-A1** | |
| RSK-007 — pipeline không chạy hạng mục bắt buộc | cao | **WP-A2** + **WP-A5** | A2 đấu nối, A5 đo lường |
| RSK-008 — synth vẫn được ghi là official | cao | **WP-A1** | |
| RSK-009 — vòng đời Crash ladder hở | cao | **WP-A3** | |
| GOV-RSK-001 — sai số biên router | trung bình | **MICRO-GOVDEF-001** | Ngoài 15 gói; WP-A2 tham chiếu qua BLK-003 |

**Kết quả:** không rủi ro nào mất nơi thuộc về. Hai rủi ro (RSK-001, GOV-RSK-001) cố ý **không**
thuộc 15 gói — chúng thuộc T-09B và MICRO-GOVDEF-001, đúng như roadmap chuẩn đã ghi.

---

## 4. Blocker

| Blocker | Chặn gì | Đã phản ánh vào file task chưa |
|---|---|---|
| BLK-001 — không có đường tới dữ liệu Binance | **chỉ T-06** | Có — WP-A1 ghi rõ; không gói nào trong 15 gói bị chặn bởi BLK-001 |
| BLK-002 — tính năng cảnh báo chưa được đặc tả | T-08, T-10 | **Không thuộc 15 gói** — đúng, đây là khoảng trống đặc tả của nhánh app |
| BLK-003 — `validate_routing.py` chưa biểu diễn được override DEC-008 | **WP-A2** | Có — WP-A2 = BLOCKED; ghi trong Ready Gate |

Xác nhận DEC-003 vẫn được cưỡng chế: dữ liệu tổng hợp dùng được cho phát triển và kiểm chứng ở cả
15 gói, **không** dùng được để tạo verdict. Điều này được ghi tường minh ở WP-A1 và WP-B1.

---

## 5. Quyết định DEC-007 / DEC-008 / DEC-009 — kiểm từng điều kiện

| Điều kiện | Nguồn | Nơi được bảo toàn | Trạng thái |
|---|---|---|---|
| Giữ nguyên cấu trúc 15 work package, gom theo nguyên nhân gốc | DEC-007 (1) | 15 file task, đúng tên và đúng phạm vi RCP-001 | ĐẠT |
| Giữ nguyên phân lớp A/B/C/D | DEC-007 (2) | Trường `Lớp (RCP-001)` trong metadata của từng file | ĐẠT |
| **Quy tắc Gate 1 staleness cho F-017** | DEC-007 (2) → DEC-009 | **CHECK-B1-02**, Priority = REQUIRED | ĐẠT |
| Bỏ T-06A, hấp thụ vào WP-A1, không mất requirement | DEC-007 (3) | WP-A1 mục "Đóng finding / risk" + CHECK-A1-01…A1-09 | ĐẠT |
| WP-A2 giữ Tier C / Opus, Effort high | DEC-007 (4) → DEC-008 | Metadata WP-A2 + trường `Manual Override` + `Router Raw Output` | ĐẠT |
| Tám trường provenance bắt buộc | DEC-007 (3) | WP-A1 CHECK-A1-01 và bảng phạm vi | ĐẠT (8/8) |
| Không hạ Completion Gate của T-03 | DEC-007 tác động | WP-C1 CHECK-C1-08 ghi tường minh | ĐẠT |
| DEC-005 giữ PENDING, không tự chốt | DEC-007 tác động | WP-C2 Ready Gate = BLOCKED trên DEC-005 | ĐẠT |
| DEC-005 không được dùng để chặn lớp A | RCP-001 §5 | Ghi chú tường minh trong Ready Gate của WP-C2 | ĐẠT |

### Kiểm riêng tám trường provenance (DEC-007 quyết định 3)

`python_version` · `dependency_lock_hash` · `code_commit` · `dataset_hash` · `strategy_config_hash` ·
`execution_config_hash` · `sensitivity_manifest_hash` · `seed` — **8/8 xuất hiện trong WP-A1**, và
CHECK-A1-01 (REQUIRED, E1) đòi cả tám có mặt trong một run record thật.

---

## 6. Stopping rule — kiểm từng mệnh đề

| Mệnh đề | Nơi được cưỡng chế |
|---|---|
| UNKNOWN không được tự động coi là PASS | WP-B1 CHECK-B1-01, CHECK-B1-07 |
| REQUIRED Failure Signal còn UNKNOWN thì không được BUILD | WP-B1 CHECK-B1-01 (cả 12 FS đều REQUIRED) |
| Missing evidence không được coi là PASS | WP-B1 CHECK-B1-07; và trạng thái mặc định `NOT_TESTED` ở toàn bộ 125 check |
| BLOCKED required check không cho ra DONE | WP-B3 CHECK-B3-02, WP-B1 CHECK-B1-04, WP-C2 Ready Gate |
| Synthetic run không thay được official run | WP-A1 CHECK-A1-06, CHECK-A1-07; WP-B1 Ready Gate |
| Finding chưa kiểm chứng không được âm thầm đổi thành false | WP-C1 CHECK-C1-03/04/05 đòi kết luận E1; WP-C4 CHECK-C4-06 |
| Không hạ tiêu chuẩn gate để task DONE được | Exit Criteria cuối cùng của **cả 15 file** |
| Gate 1 staleness (DEC-009) | WP-B1 CHECK-B1-02 |
| Không chạy lại official run để làm đẹp kết quả | WP-B1 Out of Scope + Escalation Triggers |

Không ngưỡng số mới nào được sáng tạo trong T-04. Các ngưỡng hiện có (FS-02 `>0.5`, FS-07
`cash>0.30 và AE<102`, FS-12 `>0.80`, Control G `shift_days=10`) được **giữ nguyên** và chuyển thành
đối tượng phê chuẩn của WP-B1 CHECK-B1-04, không bị thay đổi ở T-04.

---

## 7. Dependency — đối chiếu file task với bảng roadmap chuẩn

| Gói | Dependency trong file task | Khớp roadmap |
|---|---|---|
| WP-A1 | T-04 | ✔ |
| WP-A2 | T-04, BLK-003 | ✔ (BLK-003 là bổ sung mới của T-04, xem §9) |
| WP-A3 | T-04 | ✔ |
| WP-A4 | T-04, WP-A3 | ✔ |
| WP-A5 | T-04, WP-A2, WP-A3 | ✔ |
| WP-A6 | T-04, WP-A3, WP-A4 | ✔ |
| WP-B1 | T-04, T-06, (WP-A5) | ✔ |
| WP-B2 | T-04, T-06 | ✔ |
| WP-B3 | T-04, T-06, WP-C2 | ✔ |
| WP-C1 | T-01, T-04 | ✔ |
| WP-C2 | T-04, T-05/DEC-005 | ✔ |
| WP-C3 | T-04, WP-C2 | ✔ |
| WP-C4 | T-04, WP-A3, WP-A4, WP-A6 | ✔ |
| WP-D1 | T-04 | ✔ |
| WP-D2 | T-04 | ✔ |

Ràng buộc tuần tự hoá do xung đột file (RCP-001 §4) cũng được bảo toàn: WP-A3 ∦ WP-A4 (cùng
`engine.py`), WP-A2 ∦ WP-A5 (cùng `pipeline.py`) — ghi ở mục `Parallel-Safe With` của bốn file.

---

## 8. Kiểm phình phạm vi (scope creep)

Câu hỏi kiểm: *có gói nào được viết gate đòi hỏi việc mà RCP-001 không giao cho nó không?*

| Gói | Rào chắn phạm vi trong Completion Gate |
|---|---|
| WP-A1 | CHECK-A1-10 — không hành vi mô phỏng nào được đổi |
| WP-A2 | CHECK-A2-08 — diff chỉ là đấu nối; CHECK-A2-09 — kết quả A và chiến lược không đổi |
| WP-A3 | CHECK-A3-08 — mọi sai lệch phải quy về một điều khoản spec |
| WP-A4 | CHECK-A4-07 — như trên, trên dataset có gap |
| WP-A5 | CHECK-A5-07 — không đổi chính sách verdict; CHECK-A5-08 — không đổi hành vi |
| WP-A6 | CHECK-A6-04 — quyết định sửa/ghi nhận phải có căn cứ đo được |
| WP-B1 | Out of Scope — không sinh dữ liệu đo lường, không đổi ngưỡng gate spec |
| WP-B2 | CHECK-B2-09 — không sửa `src/` để test đi qua |
| WP-B3 | CHECK-B3-07 — hành vi quyết định không đổi |
| WP-C1 | CHECK-C1-07 — không sửa logic app (đó là T-09A) |
| WP-C2 | CHECK-C2-06 — kết quả backtest không đổi; CHECK-C2-07 — không tạo class chỉ để khớp tên |
| WP-C3 | CHECK-C3-05 — không chạm backtest |
| WP-C4 | CHECK-C4-06 — không vá JS để parity xanh |
| WP-D1 | CHECK-D1-05 — kết quả mô phỏng không đổi (mệnh đề định nghĩa gói) |
| WP-D2 | CHECK-D2-04, CHECK-D2-06 — không chạm `docs/spec/`, không chạm mã sản phẩm |

**Kết quả:** 15/15 gói có ít nhất một REQUIRED check đóng vai rào chắn phạm vi.

---

## 9. Phát hiện của chính T-04

### PH-01 — Số đếm finding trong bản tóm tắt S001 không khớp với danh mục liệt kê

Mức: **E1** (đếm bằng script trên chính `docs/reviews/S001-audit-findings.md`).

Bảng "Tổng hợp" của S001 ghi: HIGH 8, **MEDIUM 15**, LOW 7, INFO/SPEC DEFECT 3, **Tổng 33**.
Đếm thật trên các mục được liệt kê:

```
HIGH   :  8 -> F-001 ... F-008
MEDIUM : 19 -> F-009 ... F-027
LOW    :  7 -> F-028 ... F-034
SPEC   :  3 -> S-001, S-002, S-003
```

Tức **34 định danh `F-xxx` + 3 `S-xxx` = 37 mục**, không phải 33. Con số 33 được chép sang
`PROJECT/PROJECT_PROGRESS.md` và `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`.

**Đánh giá ảnh hưởng:** đây là sai số **đếm tổng**, không phải finding bị rơi. Bảng root cause của
RCP-001 §2 liệt kê đủ 34 `F-xxx` và cả 3 `S-xxx`; §6 phân đủ chúng vào 15 gói; và §2 của tài liệu
này xác nhận 40/40 định danh có nơi thuộc về. Không hạng mục nội dung nào bị mất.

**T-04 không tự sửa con số này** ở `docs/reviews/S001-audit-findings.md` vì đó là biên bản audit của
một phiên đã đóng. Ghi nhận để chủ dự án quyết định cách đính chính.

### PH-02 — Ghi đè DEC-008 làm `validate_routing.py` báo FAIL, đúng như DEC-008 đã dự đoán

Mức: **E1**.

Khi WP-A2 có file định nghĩa task với `Task Mode: MAJOR` và `Primary Agent Tier: C`,
`validate_routing.py` — vốn so khớp **tuyệt đối** với router — báo FAIL:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây không phải defect mới. `PROJECT/PROJECT_DECISIONS.md` DEC-008 mục Impact đã ghi trước:

> "khi T-04 soạn file task đầy đủ cho WP-A2, file đó phải ghi rõ 'Manual Override: YES — DEC-008'
> bên cạnh giá trị router thô, và `validate_routing.py` **cần được cập nhật ở một task riêng**
> (MICRO-GOVDEF-001 hoặc kế tiếp) để chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối."

T-04 làm đúng phần được giao (ghi override vào file) và **không** làm phần được giao cho task khác
(sửa validator). Hệ quả được đăng ký thành **BLK-003** và WP-A2 giữ trạng thái `BLOCKED`.

Xác nhận quan trọng: **14/15 gói còn lại + T-04 khớp router tuyệt đối.** Đây là lỗi duy nhất, và nó
đến từ đúng một dòng đã được phê duyệt trước.

---

## 10. Kết luận

| Câu hỏi kiểm tra hồi quy | Kết luận |
|---|---|
| Có finding nào bị rơi không? | **Không** — 40/40 định danh có nơi thuộc về |
| Có rủi ro bắt buộc nào bị rơi không? | **Không** — 10/10 rủi ro có nơi thuộc về hoặc lý do nằm ngoài 15 gói |
| Có dependency nào bị mất không? | **Không** — 15/15 khớp bảng roadmap chuẩn; ràng buộc tuần tự hoá được bảo toàn |
| Có quyết định DEC-007/008/009 nào bị mất không? | **Không** — 9/9 điều kiện được kiểm và đạt |
| Có stopping rule nào bị mất không? | **Không** — 9/9 mệnh đề có nơi cưỡng chế |
| Có gói nào phình sang remediation ngoài phạm vi không? | **Không** — 15/15 có rào chắn phạm vi bằng REQUIRED check |
| Phát hiện mới của T-04 | **PH-01** (sai số đếm trong tóm tắt S001), **PH-02** (BLK-003) |
