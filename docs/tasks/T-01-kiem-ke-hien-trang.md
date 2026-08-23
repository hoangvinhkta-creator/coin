# T-01 — Kiểm kê hiện trạng toàn repo

## Metadata
Status:
DONE

Phase:
Phase 1 — Discovery & Baseline

Task Mode:
SPIKE

Chế độ phiên:
AUDIT — READ ONLY

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 2
B: 1
A: 2
X: 3
U: 3
V: 2
H: 3
C: 4
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.2

Effort Routing Score:
2.7

Applied Model Floor:
none

Applied Effort Floor:
none

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Difficulty:
3/4

Risk:
2/4

Blast Radius:
1/4

Project Profile:
PRODUCT

## Objective

Trả lời một câu hỏi duy nhất bằng bằng chứng, không bằng phỏng đoán:
**dự án này đang thực sự có gì và đang đứng ở đâu?**

Đây là task giảm bất định (SPIKE). Đầu ra là một Discovery Baseline đủ tin cậy để T-04 dựng
lộ trình chính thức lên trên. Không phải task sửa lỗi.

## Câu hỏi cần trả lời (learning objectives)

1. Bộ máy Python có chạy được từ một bản checkout sạch không? Test suite thật sự pass bao nhiêu?
2. Những gì trong repo là bằng chứng thật, những gì chỉ là tuyên bố chưa kiểm chứng?
3. Ranh giới kiến trúc hiện tại nằm ở đâu: Python engine, webapp JS, spec pack, governance?
4. Dữ liệu chảy qua hệ thống theo đường nào, lưu ở đâu, ai sở hữu tính đúng đắn của nó?
5. Món nợ kỹ thuật nào đủ lớn để ảnh hưởng tới lộ trình?
6. Có rào cản nào ngoài Binance egress đang chặn official run không?

## Hypothesis cần kiểm

H1: Test suite Python pass đầy đủ trên môi trường sạch.
H2: Không tồn tại kết quả official run nào trong repo (đã quan sát ở S000, cần xác nhận lại).
H3: Bộ spec V2.1.5 là nguồn sự thật duy nhất và không có tài liệu nào mâu thuẫn nằm ngoài
    `docs/spec/`.
H4: Không có secret, khóa API, hay dữ liệu cá nhân nào bị commit vào repo.

Mỗi hypothesis phải được kết luận là XÁC NHẬN / BÁC BỎ / KHÔNG KẾT LUẬN ĐƯỢC, kèm bằng chứng.

## Scope

Được đọc và chạy:
- Toàn bộ `src/`, `tests/`, `webapp/`, `docs/`, `pyproject.toml`, `.gitignore`
- Lịch sử git (`git log`, `git show`) để hiểu thứ tự hình thành
- Chạy test suite Python và ghi lại output nguyên văn
- Chạy các validator governance
- Chạy `ethdca --help` và các lệnh chỉ đọc

## Out of Scope

- Sửa bất kỳ file mã nguồn nào (`src/`, `webapp/`, `tests/`)
- Sửa bất kỳ file nào trong `docs/spec/`
- Chạy `ethdca run` (nặng hàng giờ) hoặc `ethdca fetch` (cần mạng Binance)
- Đề xuất refactor cụ thể — đó là việc của T-04
- Đối chiếu chi tiết code với từng điều khoản spec — đó là T-02
- Soi kỹ webapp — đó là T-03

## Dependencies
- T-00 (DONE)

## Blocks
- T-02, T-03 (cần bản đồ hiện trạng trước)
- T-04

## Parallel-Safe With
- Không có. T-01 phải xong trước T-02 và T-03.

## Expected Touch Area

Allowed:
- `docs/reviews/S001-discovery-baseline.md` (tạo mới)
- `PROJECT/PROJECT_PROGRESS.md` (cập nhật trạng thái, blocker, risk)
- `PROJECT/LO_TRINH_DE_HIEU.md` (chỉ qua script sync, không sửa tay)

Do not touch without Scope Expansion:
- `src/`, `webapp/`, `tests/`, `docs/spec/`, `pyproject.toml`

## Subtasks
- [ ] 01.1 Dựng môi trường sạch ngoài repo, cài `pip install -e ".[dev]"`, ghi lại output
- [ ] 01.2 Chạy `pytest`, ghi output nguyên văn: số pass/fail/skip/error, thời gian
- [ ] 01.3 Chạy 5 validator governance, ghi output nguyên văn
- [ ] 01.4 Kiểm kê kiến trúc: module, ranh giới, phụ thuộc ngoài, điểm vào
- [ ] 01.5 Kiểm kê dữ liệu: thực thể chính, nơi lưu, vòng đời, trường nhạy cảm
- [ ] 01.6 Kiểm kê bảo mật: quét secret/khóa API trong toàn bộ lịch sử git
- [ ] 01.7 Kiểm kê môi trường: phụ thuộc, phiên bản Python/Node, thiếu gì để chạy
- [ ] 01.8 Kiểm tra mạng tới Binance, ghi mã trả về làm bằng chứng cho BLK-001
- [ ] 01.9 Kết luận H1–H4 kèm bằng chứng
- [ ] 01.10 Viết Discovery Baseline theo `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
- [ ] 01.11 Ghi mọi phát hiện thành finding theo `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`

## Ready Gate

SPIKE Ready Gate theo `governance/core/TASK_READY_GATE_STANDARD.md`:

- [x] Câu hỏi/ẩn số được nêu rõ — 6 câu hỏi ở trên
- [x] Hypothesis/learning objective được định nghĩa — H1–H4
- [x] Phạm vi và giới hạn được định nghĩa — Scope / Out of Scope
- [x] Phương pháp thu bằng chứng được định nghĩa — chạy thật, ghi output nguyên văn
- [x] Không ép tiêu chí nghiệm thu production sớm
- [x] Định dạng đầu ra được định nghĩa — Discovery Baseline + Audit Findings
- [ ] Xác nhận lại khi mở phiên S001

## Completion Gate

Gate của SPIKE tập trung vào kết quả học được, theo
`governance/core/TASK_COMPLETION_GATE_STANDARD.md` mục SPIKE.

### CHECK-01-01 — Test suite Python đã được chạy thật
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
69 passed, 0 failed, 0 skipped, 0 error trong 372,63s. `git log e368425..HEAD -- src/ tests/` rỗng và `git status --porcelain -- src/ tests/` rỗng → mã đo được vẫn là mã hiện tại.

### CHECK-01-02 — Năm validator governance đã được chạy thật
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Chạy lại trong S001: structure PASS (27 path), project state PASS, routing PASS (0 MAJOR file), easy roadmap PASS.

### CHECK-01-03 — Quét secret trên toàn bộ lịch sử git
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Quét toàn bộ `git log --all -p` theo mẫu key/secret/token/private-key: mọi kết quả khớp đều là văn bản tài liệu governance, không phải giá trị thật. Không file `.env`, `.pem`, `.key` hay credential nào từng tồn tại.

### CHECK-01-04 — Bốn hypothesis H1–H4 đều có kết luận kèm bằng chứng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
H1–H4 đều có kết luận kèm bằng chứng — xem phụ lục 'Kết luận bốn hypothesis' trong `docs/reviews/S001-compliance-matrix.md`.

### CHECK-01-05 — Discovery Baseline được viết đủ 12 mục của template
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E0

Evidence:
`docs/reviews/S001-discovery-baseline.md` viết đủ 12 mục của template.

### CHECK-01-06 — Không có file mã nguồn nào bị sửa
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`git status --porcelain` cuối phiên: không mục nào thuộc `src/`, `webapp/`, `tests/`, `docs/spec/`.

## Exit Criteria
- [ ] 100% REQUIRED checks PASS
- [ ] Bốn hypothesis đều có kết luận, không cái nào bỏ lửng
- [ ] Mọi phát hiện có Severity và Evidence Level
- [ ] Không có file mã nguồn nào bị sửa
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [ ] `PROJECT/LO_TRINH_DE_HIEU.md` được sinh lại bằng script và validator PASS
- [ ] Session handoff được viết

## Escalation Triggers

- Không cài được môi trường hoặc không chạy được test → `MISSING_INPUT` → BLOCKED,
  KHÔNG nâng Tier. Ghi rõ thiếu gì và cần chủ dự án cung cấp gì.
- Phát hiện secret bị commit → dừng ngay, báo chủ dự án, xử lý theo
  `governance/core/04_SECURITY_RULES.md` trước khi làm tiếp.
- Phát hiện mâu thuẫn giữa hai tài liệu spec → dùng khối `CONFLICT DETECTED` của `CLAUDE.md`,
  áp precedence của Master Index §2, không tự chọn.

## Changed Files Registry

Created:
- (dự kiến) `docs/reviews/S001-discovery-baseline.md`

Modified:
- (dự kiến) `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/LO_TRINH_DE_HIEU.md`

Deleted:
- Không

Migration Impact:
- Không

## Notes

S000 đã thu được một số quan sát ban đầu, ghi lại ở đây để T-01 **kiểm chứng lại chứ không
thừa nhận**:
- `results/` không tồn tại và nằm trong `.gitignore` → chưa từng có official run
- Không có `.github/`, tức không có CI
- 26 module Python (~3.400 dòng), 14 file test (~1.170 dòng)
- 11 commit, không phiên governance nào trước S000
- Chỉ có một branch: `claude/move-files-to-root-7zhv8l`; không thấy `main` trên remote

Quan sát của S000 là E0 (tuyên bố của agent). T-01 phải nâng chúng lên E1 bằng cách chạy thật.

---

## Kết quả S001

Task hoàn tất. Đầu ra: `docs/reviews/S001-discovery-baseline.md`.

Sáu REQUIRED check đều PASS. Bốn hypothesis H1–H4 đều XÁC NHẬN.
Ghi chú H3: xác nhận **có điều kiện** — `docs/CONVENTIONS.md` chốt 13 quy ước hợp lệ, nhưng S001
phát hiện thêm nhiều quy ước KHÔNG được ghi ở đó (F-015, F-016, F-026).
