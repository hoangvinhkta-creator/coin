# SESSION HANDOFF

Session ID:
S000

Task:
T-00 — Mở dự án và dựng bộ điều hành

Task Mode:
SPIKE

Project Profile:
PRODUCT

Status:
DONE

Ngày:
2026-08-23

## Result

S000 đã chạy đủ 15 bước của thủ tục PROJECT OPEN trong
`governance/core/00_SESSION_ORCHESTRATION.md`. Không sửa một dòng mã sản phẩm nào.

Bốn kết quả chính:

**1. Chốt profile = PRODUCT.** Dự án lưu dữ liệu tài chính thật và thực hiện tính toán dẫn tới
quyết định xuống tiền, nên vượt ngưỡng SOLO_LITE; nhưng không có đội ngũ, CI hay người dùng ngoài
để biện minh cho TEAM_PRODUCTION. Phiên kế tiếp (S001) chạy ở chế độ AUDIT read-only vì toàn bộ
code hiện có được viết trước khi governance vào repo và chưa có bằng chứng tuân thủ nào.

**2. Khởi tạo trạng thái dự án.** `PROJECT/PROJECT_PROFILE.md`, `PROJECT/PROJECT_PROGRESS.md`,
`PROJECT/PROJECT_DECISIONS.md` đã được viết đầy đủ; `PROJECT/LO_TRINH_DE_HIEU.md` được sinh tự
động bằng script. Cả năm validator governance đều PASS.

**3. Lập kế hoạch khảo sát.** Ba task định nghĩa đầy đủ (T-01, T-02, T-03) với Ready Gate,
Completion Gate sơ bộ, escalation trigger và ranh giới phạm vi rõ ràng.

**4. Lộ trình sơ bộ 14 task** qua 6 phase, mọi Tier/Effort được tính bằng
`routing_engine.py` chứ không chọn tay.

### Hai phát hiện làm đổi hình dạng lộ trình

**PH-1 — Tính năng "cảnh báo" mà chủ dự án muốn chưa hề được đặc tả.**
`docs/spec/01_PRODUCT_SPEC_V2_1_5.md` không có mục nào về alert/cảnh báo/notification. Cái spec
có là trạng thái hiển thị thụ động trên hero khi mở trang (§11–§13). Implementation Plan §9 hoãn
có chủ đích: "không cần cron cho tới khi thực sự cần notification".
Điều kiện kích hoạt thì đã có đầy đủ, nằm rải trong Strategy Spec §3, §4, §5, §9, §10, §15,
§17, §18 — và danh mục 30 reason code ở Strategy §20 chính là bộ khung tự nhiên cho danh sách
cảnh báo.
Hệ quả: đây là khoảng trống **đặc tả**, không phải khoảng trống **code**. Vì vậy lộ trình có
T-08 (đặc tả) đứng trước T-10 (triển khai). Bỏ qua T-08 thì T-10 sẽ được xây trên phỏng đoán.

**PH-2 — Cổng verdict chưa mở, và lý do là hạ tầng chứ không phải chiến lược trượt gate.**
Repo chưa từng có official run: `results/` không tồn tại và nằm trong `.gitignore`. Môi trường
phát triển bị chặn egress tới Binance nên mọi kiểm chứng chạy trên dữ liệu tổng hợp, tự gắn cờ
`official: false`. Nghĩa là cổng có thể mở được bằng cách lấy dữ liệu thật, không cần đổi spec.
Đây là đường găng tới mục tiêu cuối của chủ dự án.

## Subtasks Completed

- [x] 00.1 Đọc `CLAUDE.md` và `00_SESSION_ORCHESTRATION.md`
- [x] 00.2 Đọc ba chuẩn bắt buộc: `PROJECT_PROFILE_STANDARD`, `RULE_PRECEDENCE`, `TASK_MODE_STANDARD`
- [x] 00.3 Khảo sát repo: cấu trúc, lịch sử git, kích thước code, cấu hình
- [x] 00.4 Khảo sát bộ spec V2.1.5: precedence, phase, cổng verdict, freeze rule, nguồn dữ liệu
- [x] 00.5 Khảo sát sản phẩm app: Product Spec, webapp hiện tại, khoảng cách
- [x] 00.6 Chọn profile và ghi `PROJECT/PROJECT_PROFILE.md`
- [x] 00.7 Quyết định S001 chạy chế độ AUDIT read-only
- [x] 00.8 Tạo 6 phase và 14 task
- [x] 00.9 Lập đồ thị phụ thuộc sơ bộ
- [x] 00.10 Chấm Difficulty/Risk/Blast Radius cho mọi task
- [x] 00.11 Tính Tier + Effort bằng `routing_engine.py` cho toàn bộ 14 task
- [x] 00.12 Soạn Completion Gate sơ bộ cho T-01, T-02, T-03
- [x] 00.13 Khởi tạo `PROJECT/PROJECT_PROGRESS.md` theo bảng roadmap chuẩn
- [x] 00.14 Chạy `sync_easy_roadmap.py` sinh `PROJECT/LO_TRINH_DE_HIEU.md`
- [x] 00.15 Ghi 5 quyết định vào `PROJECT/PROJECT_DECISIONS.md`

## Subtasks Remaining

Không. Việc còn lại thuộc T-01 trở đi.

Một mục chờ chủ dự án: **DEC-005 chưa chốt** — phạm vi công cụ được phép xây trước khi có
verdict. Đã soạn sẵn ba phương án, sẽ trình tại T-05.

## Completion Gate Summary

Required:
6

PASS:
6

FAIL:
0

BLOCKED:
0

NOT_TESTED:
0

## Verification Evidence

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-00-01 — Profile được chốt và ghi nhận có lý do | PASS | E1 | `validate_project_state.py` → `PROJECT STATE: PASS`, exit=0 | Agent S000 | 2026-08-23 |
| CHECK-00-02 — Cấu trúc governance đầy đủ | PASS | E1 | `validate_structure.py` → `GOVERNANCE STRUCTURE: PASS`, checked 27 required paths, exit=0 | Agent S000 | 2026-08-23 |
| CHECK-00-03 — Roadmap chuẩn parse được và hợp lệ | PASS | E1 | `sync_easy_roadmap.py` → `ROADMAP SYNC: PASS - wrote PROJECT/LO_TRINH_DE_HIEU.md`, exit=0 | Agent S000 | 2026-08-23 |
| CHECK-00-04 — Roadmap dễ hiểu đồng bộ với nguồn | PASS | E1 | `validate_easy_roadmap.py` → `EASY ROADMAP: PASS`, exit=0 | Agent S000 | 2026-08-23 |
| CHECK-00-05 — Routing hợp lệ | PASS | E1 | `validate_routing.py` → `ROUTING VALIDATION: PASS (0 MAJOR task file(s) checked)`, exit=0. Ba task file của Phase 1 ở chế độ SPIKE nên validator không kiểm; routing của chúng vẫn được ghi đầy đủ trong file và tính bằng `routing_engine.py` | Agent S000 | 2026-08-23 |
| CHECK-00-06 — Không sửa mã sản phẩm | PASS | E1 | `git status --porcelain` cuối phiên: chỉ có thay đổi trong `PROJECT/`, `docs/tasks/`, `docs/sessions/`. Không có mục nào thuộc `src/`, `webapp/`, `tests/`, `docs/spec/` | Agent S000 | 2026-08-23 |

### Bằng chứng nền E1 thu được cuối phiên

Một khảo sát nền đã chạy thật trong phiên này và trả về bằng chứng E1. Chi tiết đầy đủ ở
`PROJECT/PROJECT_PROGRESS.md` mục "Bằng chứng nền thu tại S000". Tóm tắt:

| Hạng mục | Kết quả |
|---|---|
| Test suite Python | **69 passed, 0 failed, 0 skipped** trong 372,63s |
| Mạng tới Binance / CoinGecko | Cả ba host trả **403** ở tầng proxy; PyPI thông |
| `ethdca freeze` | Đếm ra đúng **219** (Gate 2) và **114** (Gate 3) |
| Parity engine JS ↔ Python | Lệch tối đa **7,39e-11** trên 40 ngày |
| Bất biến kế toán ladder (một tháng) | Tổng bảo toàn qua fill → partial → invalidation → release |
| `results/`, `data/` trong repo | Không tồn tại — xác nhận chưa từng có official run |

Điều này **đổi đánh giá ban đầu theo hướng tốt hơn**: mã nguồn khỏe hơn tài liệu gợi ý.
Hệ quả: T-02 nên tập trung vào tuân thủ spec, không phải sức khỏe cơ bản của engine.

### Hai điều chỉnh sau bằng chứng

**RSK-003 hạ từ cao xuống trung bình.** Bất biến kế toán giữ đúng trong kịch bản một tháng.
Nhưng nghi vấn (a) nói về kịch bản **đa tháng** — đúng vào điểm mù của test hiện có, nên chưa
bị bác bỏ. Nghi vấn (b) và (c) chưa có ca kiểm thử nào chạm tới. T-03 giữ nguyên nhiệm vụ.

**Thêm RSK-006 và task T-06A.** `pyproject.toml` chỉ đặt sàn thư viện, không có lockfile.
Khi cài mới, pip kéo về numpy 2.4.6 / pandas 3.0.5 — vượt sàn hai thế hệ lớn. Test vẫn xanh,
nhưng run record lưu hash config/manifest/dataset/seed mà **không lưu phiên bản thư viện**.
Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu, nên đây là khiếm khuyết thật:
official run chạy hôm nay có thể không tái lập được về sau mà không ai phát hiện, vì mọi hash
đầu vào vẫn trùng. Phải xử lý **trước** T-06 — đó là lý do T-06A được chèn vào lộ trình.

### Ghi chú về mức bằng chứng còn lại

Các nhận định chưa được chạy thật — ba nghi vấn lỗi kế toán, đối chiếu app với Product Spec,
danh sách tính năng còn thiếu — vẫn ở mức **E0, tuyên bố của agent**, và được ghi dưới dạng
rủi ro chưa xác minh. Không được trích dẫn chúng như kết luận đã kiểm chứng.

Cảnh báo quan trọng: các validator governance đang **PASS trên tập rỗng** — 0 evidence record,
0 MAJOR task file, 0 task DONE. `PROJECT STATE` chỉ vừa chuyển FAIL → PASS trong chính phiên
này. Khung đã có, nội dung thì chưa. Đừng đọc những dòng PASS đó như bằng chứng chất lượng.

## Files Changed

Created:
- `docs/tasks/T-01-kiem-ke-hien-trang.md`
- `docs/tasks/T-02-doi-chieu-engine-voi-spec.md`
- `docs/tasks/T-03-soat-app-web-va-rui-ro-du-lieu.md`
- `docs/sessions/S000-project-open.md`

Modified:
- `PROJECT/PROJECT_PROFILE.md` (từ khung trống → hồ sơ đầy đủ)
- `PROJECT/PROJECT_PROGRESS.md` (từ khung trống → trạng thái + roadmap 14 task)
- `PROJECT/PROJECT_DECISIONS.md` (từ khung trống → 5 quyết định)
- `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động bằng script, không sửa tay)

Deleted:
- Không

## Key Decisions

- **DEC-001** — Chọn profile PRODUCT
- **DEC-002** — Phiên S001 chạy chế độ AUDIT read-only
- **DEC-003** — Dữ liệu tổng hợp không bao giờ được dùng để ra verdict
- **DEC-004** — Xác nhận provider mapping Tier A/B/C/D
- **DEC-005** — **PENDING**, chờ chủ dự án duyệt tại T-05: phạm vi công cụ trước verdict

Chi tiết đầy đủ: `PROJECT/PROJECT_DECISIONS.md`.

## Risks / Blockers

Blocker:
- **BLK-001** — Không có đường tới dữ liệu Binance từ môi trường phát triển. Chặn T-06, qua đó
  chặn T-07 và T-11. Cần chủ dự án cung cấp máy hoặc VPS truy cập được `data.binance.vision`
  và `api.binance.com`.
- **BLK-002** — Tính năng cảnh báo chưa được đặc tả. Chặn T-10. Xử lý bằng T-08.

Risk:
- **RSK-001** — Mất lịch sử giao dịch thật (cao). Giảm thiểu: T-09B.
- **RSK-002** — Hai bản cài đặt chiến lược trôi khỏi nhau (cao). Xác minh: T-02, T-03.
- **RSK-003** — Ba nghi vấn lỗi kế toán trong app web (cao, chưa xác minh). Xác minh: T-03.
- **RSK-004** — Bộ test webapp không phải test thật (trung bình). Xác minh: T-03.
- **RSK-005** — Quy ước không thuộc spec nằm trong đường ra verdict (trung bình). Xác minh: T-02.
- **RSK-006** — Không ghim phiên bản thư viện nên kết quả không tái lập theo thời gian (cao).
  Giảm thiểu: T-06A, bắt buộc xong trước T-06.

Chi tiết: `PROJECT/PROJECT_PROGRESS.md`.

## Regression Items

Không có.

## Do Not Change Yet

Phiên S001 là **read-only**. Tuyệt đối không sửa:

- `src/` — engine Python
- `webapp/` — app web
- `tests/` — bộ test
- `docs/spec/` — bộ spec đã đóng băng V2.1.5

Ba lý do:
1. Chủ dự án đã yêu cầu rõ trong S000: chưa remediation, chưa refactor.
2. Chưa có Discovery Baseline nên chưa biết sửa gì là đúng.
3. `docs/spec/` bị freeze rule của Master Index §6 chi phối — sửa spec dựa trên kết quả run là
   vi phạm; mọi thay đổi hypothesis phải mở V2.2, không vá tại chỗ.

Riêng ba nghi vấn lỗi kế toán (RSK-003): **không sửa trong S001**, kể cả khi xác nhận là lỗi
thật. Xác minh ở T-03, sửa ở T-09A sau khi T-04 chốt lộ trình.

## Next Recommended Session

**S001 — Discovery & Baseline**, chạy ở chế độ AUDIT read-only.

Nội dung: T-01 → rồi T-02 và T-03 (hai task này chạy song song được).

Mục tiêu: sinh Discovery Baseline và Audit Findings đủ tin cậy để T-04 dựng lộ trình chính thức.

Nếu chủ dự án muốn rút ngắn đường tới mục tiêu cuối, việc có giá trị nhất có thể làm **song song
và không cần agent** là chuẩn bị máy hoặc VPS truy cập được Binance cho T-06. Đó là đường găng
duy nhất mà agent không tự tháo được.

## Files Next Agent Should Read

- `CLAUDE.md`
- `PROJECT/PROJECT_PROFILE.md`
- `PROJECT/PROJECT_PROGRESS.md`
- `PROJECT/PROJECT_DECISIONS.md`
- `docs/tasks/T-01-kiem-ke-hien-trang.md`
- `docs/spec/00_MASTER_INDEX_V2_1_5.md` — precedence giữa các tài liệu spec
- `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
- `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`
- `governance/core/EVIDENCE_STANDARD.md` — vì S001 tạo ra nhiều bằng chứng
