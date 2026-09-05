# S026 — Thực thi WP-B2: bổ sung test cho requirement Backtest §21 còn thiếu

Ngày: 2026-09-05
Nhánh: `claude/wp-b2-implementation-u9y68k` (tách từ `origin/main` `b778dc1`)
Commit: `ce91a325159b5c665fa366522f7c22684b472b33` — branch authority sau push: PASS
Vai trò phiên: **implementer** (không phải rà soát độc lập)
Báo cáo đầy đủ: `docs/reviews/WP-B2-IMPLEMENTATION-REPORT.md`

---

## 1. Phiên này đã làm gì

Thực thi `WP-B2` — đóng đề xuất `R-09` và toàn bộ danh sách "Requirement của spec CHƯA CÓ TEST"
của `S001` thuộc BT §21. Gói **chỉ viết test**; nó không đổi một dòng hành vi nào.

- `WP-B2`: `READY → IN_PROGRESS → IMPLEMENTED`. **Chưa `DONE`** (xem §4).
- 10/10 REQUIRED check PASS (`CHECK-B2-01`…`CHECK-B2-10`), E1 toàn bộ.
- Diff production: **0 file, 0 dòng** — `git diff` rỗng trên mọi production path.
- Test mới: **141 ca** (4 file test + 1 module quan sát).
- Task ID mới: **0**. Repair cycle tiêu: **0**. Budget `CAP-VERDICT` không đổi.

## 2. Thiết kế đã chốt (một câu mỗi ý)

- **Test bắt đầu từ một câu trong §21, không từ một hàm trong `engine.py`.** Rủi ro đặc trưng
  của gói viết test cho code đã có là mô tả hành vi hiện tại rồi gọi đó là kiểm chứng; mỗi test
  ở đây mở đầu bằng câu spec mà nó phục vụ.
- **Số zone "bị xuyên trong cùng một nến" được tính ĐỘC LẬP với engine** — từ OHLC của nến và
  luật BT §5 (`Smart: LOW <= zone`, `Opportunity: CLOSE <= zone`) — rồi mới đối chiếu với engine.
- **Mệnh đề chỉ có nội dung khi hai khả năng khác nhau.** "max_zones áp SAU khi sắp thứ tự" được
  kiểm trên một kịch bản hai tháng dựng đúng tình huống thứ tự duyệt thô ≠ thứ tự §15.1; nếu hai
  thứ tự trùng nhau, test tự tuyên bố mình vô nghĩa và ĐỎ.
- **Phản chứng có số.** Snapshot Crash [F5] "đo SAU cancel/release" được chứng minh bằng cách
  tính lại snapshot theo ĐÚNG công thức ST §14 trên trạng thái pool của nến TRƯỚC đó: 5,8 (đo
  sau) so với 2,0 (nếu đo trước), chênh lệch đúng 3,8 = lượng vừa release.
- **Quan sát, không mô phỏng.** `tests/wp_b2_probe.py` chụp Pool/Ladder/trạng thái zone theo từng
  nến bằng cách bọc `derive_execution_state` (hàm engine gọi đúng một lần mỗi nến ở bước 12b
  §19). Bản bọc trả về đúng giá trị hàm thật, và `test_b2_02c` khoá điều đó bằng phép so
  bit-for-bit có/không instrumentation.
- **Lưới STRESSED đi NGƯỢC CHIỀU WP-A3.** WP-A3 ÉP nhãn STRESSED bật lên; WP-B2 để nhãn phát
  sinh tự nhiên rồi LOẠI BỎ nó. Hai chiều bắt hai lớp lỗi khác nhau.
- **Không requirement nào im lặng.** Bảng đối chiếu 31/31 gạch đầu dòng §21 ở
  `docs/CONVENTIONS.md`, và `tests/test_wp_b2_spec21_coverage_matrix.py` giữ cho bảng không trôi
  khỏi chính văn bản spec.

## 3. Bằng chứng chốt (số, không phải lời)

| Việc | Số đo |
|---|---|
| Mã sản phẩm bị sửa | **0 dòng** — `git diff b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock` rỗng |
| Bất biến tài chính | payload chuẩn tắc 3.728.853 byte, `sha256 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7` — TRÙNG trước–sau, và trùng cả giá trị `WP-B3` ghi ở phiên trước (tái lập được qua phiên) |
| Độ phủ §21 | **31/31** gạch đầu dòng có test hoặc `NOT_APPLICABLE` kèm lý do; 29 `TESTED`, 1 `MIXED`, 1 `NOT_APPLICABLE` |
| Production reachability | mọi test engine chạy `run_engine` THẬT; kịch bản lớn nhất duyệt 3.936 nến; bất biến không-double-reservation đo ở **mọi nến**, không chỉ cuối run |
| Chống PASS rỗng | mọi test có tiền đề khẳng định sự kiện cần kiểm THỰC SỰ xảy ra (số zone bị xuyên, có fill của cả bốn nguồn, có override, nhãn STRESSED có/không) |
| Test của gói | **141 ca**: 9 (§21.2) + 31 (§21.3) + 5 (§21.4) + 96 (bảng đối chiếu) |
| Regression | full suite **678/678 PASS**, exit 0 (trước gói 537/537) |
| Chống sinh sôi task | SET A = 28 → 28, SET B = 22 → 22 (`task_registry_snapshot.sh`); 0 task ID mới, 0 proposal |
| Validator | 7 công cụ chạy; 2 validator PASS **vacuous** (`H-08`, không sửa trong phiên này) |

Công cụ tái lập được, đã commit:

    python -m pytest tests/test_wp_b2_spec21_2_capital_ladder.py \
                     tests/test_wp_b2_spec21_3_execution.py \
                     tests/test_wp_b2_spec21_4_accounting.py \
                     tests/test_wp_b2_spec21_coverage_matrix.py
    PYTHONPATH=tests python tests/wp_b3_invariance_tool.py --raw <raw> --out <payload.json>

## 4. Việc còn lại — đúng một, và thuộc chủ dự án

    OWNER_DECISION_REQUIRED — đóng vòng đời: WP-B2: IMPLEMENTED -> DONE

`STATE_AUTHORITY.md` quy định `DONE` do chủ dự án ghi (tiền lệ `WP-B1`/`DEC-034`,
`WP-C2`/`DEC-036`, `WP-B3`/`DEC-037`). Gate của `WP-B2` **không đòi E2** ở check nào
(`Risk = 2 → E1`), nên **không** có `E2_REQUIRED`.

Đây là mắt xích cuối của `GATE-B`: `WP-B1` DONE, `WP-B3` DONE, `WP-B2` chỉ còn chờ quyết định
đóng vòng đời.

## 5. Downstream — KHÔNG đổi

`GATE-B` (= `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`) **VẪN CHƯA MỞ**: `WP-B2` mới `IMPLEMENTED`.
`T-07` vẫn `NOT READY`; `T-11` vẫn `BLOCKED`.
Giữ nguyên: `T-06 = DONE`, V2.1.5 validation = `FAILED`, verdict = `DO_NOT_BUILD`,
`can_proceed_to_app = false`, `DEC-005 = PENDING` (vẫn chặn `T-08`), `WP-C3 = READY` (chưa mở).

Phiên này KHÔNG chạy `WP-C3`, KHÔNG mở `GATE-B`/`T-07`, KHÔNG rerun hay chạm bằng chứng `T-06`,
KHÔNG di chuyển tag `v2.1.5-official-T06`, KHÔNG đổi threshold/strategy/verdict/benchmark,
KHÔNG đụng `webapp/` hay `docs/spec/`, KHÔNG merge `main`. Thư mục `data/` không tồn tại trong
container của phiên và không lệnh nào tạo/xoá/clean/stash/commit nó; dataset dùng cho test và
replay nằm ngoài repo.

## 6. Hardening phát sinh (finding ≠ task)

- **H-39** — hai kịch bản robustness Gate 3 mà Impl Plan §8 ghi là **bắt buộc** (behavioral
  simulation BT §6; stress P2P-unavailable BT §5) **không có đường chạy trong pipeline**:
  `manifests.GATE3_GRID` không biến thiên `behavioral_model` / `p2p_unavailable_in_crash`, nên cả
  114 config Gate 3 đều `OFF/False`. Ánh xạ vào risk đã đăng ký `RSK-007`; định tuyến
  `OUT_OF_SCOPE` về `CAP-PIPELINE` (`WP-A2` đã DONE → `OWNER_ASSIGNMENT_REQUIRED`). KHÔNG sửa ở
  đây: ngoài Expected Touch Area, và sửa rồi chạy lại Gate 3 chính là "chạy lại để làm đẹp kết
  quả official" mà BT §22 / Master Index §6 cấm. Không đổi verdict (`DO_NOT_BUILD` đã do
  Gate/Failure Signal quyết).
- **H-40** — nhánh "proxy 07:00 vượt TTL → MISSED" của BT §6 không tới lượt chạy ở TTL baseline
  12h (giờ đêm cho `seconds_to_7am` tối đa 8h). Cùng họ `H-36`; được kiểm ở tầng hàm và ghi rõ
  giới hạn thay vì tuyên bố một độ phủ mà đường production không có.

Cả hai đều có `RE_TRIGGER_CONDITION` cụ thể trong `PROJECT/HARDENING_BACKLOG.md`.
