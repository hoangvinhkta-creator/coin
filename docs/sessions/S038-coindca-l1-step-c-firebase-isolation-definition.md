# S038 — CoinDCA L-1 Bước C: Firebase Isolation / Auth / Backup / Recovery — Task Definition

Phiên: `S038` · Ngày: 2026-09-06 · Nhánh: `claude/coindca-l1-step-c-arch-fog4cb`
Loại phiên: **ARCHITECTURE + TASK DEFINITION ONLY** — không thi hành, production diff = EMPTY.

---

## 1. Nguồn thẩm quyền

    SOURCE HEAD (khởi phiên) = efda187088447f7a2b1e688f9562b7fd61eb47b1   (origin/main, khớp
    HEAD kỳ vọng của chỉ thị phiên)

Xác minh trước khi đọc state (`AGENTS.md` §7 Step 0):

| Điều kiện | Kết quả | Nguồn |
|---|---|---|
| `T-12` = DONE | ✅ | `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`, `DEC-046` |
| `T-13` = DONE | ✅ | `docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md`, `DEC-048` |
| Không task nào đang mở trong `CAP-WEBAPP` | ✅ | `PROJECT/PROJECT_PROGRESS.md` § Next Session (trước phiên) |
| Bước C chưa mở, là Owner decision | ✅ | `docs/reviews/T13-OWNER-CLOSURE.md` §7, `PROJECT_PROGRESS.md` § Next Session |

`branch_authority_check.sh` (đầu phiên):

    branch            = claude/coindca-l1-step-c-arch-fog4cb
    default branch    = main
    ahead of default  = 0 commit(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: FAIL — attached branch has no upstream

Tình trạng nhánh mới chưa push, không phải divergence: `ahead of default = 0`, worktree CLEAN,
production diff EMPTY, `HEAD = efda187` khớp đúng "Canonical main expected" của chỉ thị phiên.
Upstream thiết lập ở lệnh `git push -u` cuối phiên.

## 2. Việc đã làm

1. Đọc đầy đủ chuỗi thẩm quyền: `AGENTS.md`, `PROJECT/PROJECT_PROFILE.md`,
   `PROJECT/CAPABILITY_REGISTRY.md` (§15/§15.1), `PROJECT/PROJECT_PROGRESS.md` (Current Task
   Snapshot, Next Session, RSK-001), `PROJECT/PRODUCTION_PATHS.md`,
   `PROJECT/HARDENING_BACKLOG.md` (`H-42`, `H-44`…`H-50`), `PROJECT/PROJECT_DECISIONS.md`
   (`DEC-019`/`020`/`021`/`023`/`041`/`043`/`046`…`048`), `firestore.rules`, `firebase.json`,
   `webapp/firebase_config.js`, `webapp/app_logic.js` (đường auth/persistence),
   `webapp/ledger_ui.js` (backup/export/import hiện có), `docs/spec-l1/
   COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §18/§24/Phụ lục B, `docs/reviews/T12-OWNER-CLOSURE.md`,
   `docs/reviews/T13-OWNER-CLOSURE.md`.
2. Xác nhận kiến trúc hiện có: `firestore.rules` đã cô lập `ethdca/*` khỏi Content bằng allow-list
   tường minh + `isCoinDcaOwner()` so một UID cố định (không đổi shape cần thiết); `firebase.json`
   thiếu `hosting.target` (FB-2); client dùng `signInAnonymously()` làm thẩm quyền danh tính
   (FB-4); `webapp/ledger_ui.js` đã có export/import/snapshot-trước-phá-huỷ nhưng thiếu
   timestamp/preview/validate tường minh.
3. Chấm routing bằng `routing_engine.py`: `D3 R3 B3 A2 X3 U2 V3 H3 C3 F3` (category
   `authentication`, `security`) → `tier=C model=Opus effort=xhigh`, floor
   `safety_business:min_C`/`min_high` (đã thoả bởi điểm cơ bản, không cần nâng).
4. Soạn `docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md` (mới) — spec kiến trúc bước C:
   giữ nguyên namespace `ethdca/*` (không di dời — `DEC-043` LOCKED); Google Sign-In thay Anonymous
   Auth; giữ shape `isCoinDcaOwner()`; `hosting.target`; runbook deploy rules 3 bước (thủ tục, vì
   Firestore không thể target-hoá rules); backup có timestamp/schema version; restore có
   preview/validate/snapshot/atomic; multi-device; bảng thất bại mode; 14 acceptance scenario;
   định nghĩa production reachability; change budget.
5. Mở `docs/tasks/T-14-buoc-c-firebase-isolation-auth-backup.md` (mới) — Task Mode MAJOR, Scope
   IN/OUT (10+10 mục), Expected Touch Area, ràng buộc kiến trúc khoá, change budget
   (+600/−400 trần đề xuất), Ready Gate (17/17 tương đương), Completion Gate 12 REQUIRED check
   FROZEN (danh tính/rules, deploy isolation, backup/recovery, multi-device + hấp thụ `H-49`,
   production reachability).
6. Ghi `DEC-049` (`PROJECT/PROJECT_DECISIONS.md`) — formalize chỉ thị phiên Owner thành Owner
   Decision Record: chiến lược "Shared Firebase Project with Strong Logical Isolation", duyệt
   spec bước C, mở đúng một task ID (`T-14`), tách disposition `H-42` (REQUIRED/DEFERRED), hấp
   thụ `H-49`.
7. Cập nhật `PROJECT/HARDENING_BACKLOG.md`: `H-42` (thêm khối disposition REQUIRED cho `T-14` /
   DEFERRED cho project riêng, `RE_TRIGGER_CONDITION` mới cho phần REQUIRED — không xoá bảng
   `FB-1`…`FB-4` gốc); `H-49` (thêm ghi chú hấp thụ vào `CHECK-T14-11`, không đóng).
   `H-44`…`H-48`, `H-50` giữ nguyên tuyệt đối, không sửa.
8. Cập nhật state surfaces: `PROJECT/PROJECT_PROGRESS.md` (roadmap thêm dòng `T-14`, Current Task
   Snapshot, Session History, Recent Decisions, Next Session), `PROJECT/CAPABILITY_REGISTRY.md`
   §16, `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.11.
9. KHÔNG sửa `PROJECT/PRODUCTION_PATHS.md` — chưa có file runtime mới nào được tạo trong phiên
   này (phiên định nghĩa, không implementation; `firestore.rules`/`firebase.json`/
   `webapp/firebase_config.js` đã được khai từ trước — khiếm khuyết khai báo `H-32` không thuộc
   phạm vi phiên này).

## 3. Kết quả

    TASK ID     T-14
    TÊN         CoinDCA L-1 Bước C: Firebase Isolation, Owner Auth bền vững, Backup/Recovery
    FILE        docs/tasks/T-14-buoc-c-firebase-isolation-auth-backup.md
    SPEC        docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md (CANONICAL — APPROVED, DEC-049)
    MODE        MAJOR
    STATE       NOT_PLANNED -> READY (Ready Gate 17/17 tương đương)
    GATE        Completion Gate 12/12 REQUIRED, FROZEN 2026-09-06
    ROUTING     C / Opus / xhigh — model_score 2.85, effort_score 2.8
                inputs D3 R3 B3 A2 X3 · U2 V3 H3 C3 F3 · category authentication, security
                floors safety_business:min_C, safety_business:min_high
    CAPABILITY  CAP-WEBAPP (lineage root WP-C1) — không capability mới, không lineage mới
    BUDGET      allowed 2 / used 1 / remaining 1 — KHÔNG đổi (mở task không tiêu chu kỳ)
    OWNER DEC   DEC-049 — "Shared Firebase Project with Strong Logical Isolation"; project riêng
                DEFERRED; H-42 tách REQUIRED (T-14) / DEFERRED; H-49 hấp thụ vào CHECK-T14-11

**Vì sao `T-14` chứ không tách nhỏ thêm.** Auth, rules, deploy isolation, backup, recovery, và
multi-device chia sẻ đúng MỘT lifecycle sản phẩm-sẵn-sàng (bước C của spec kế toán §24) và không
có output độc lập có ý nghĩa với người dùng nếu tách rời — danh tính bền vững vô nghĩa nếu không
có backup cho trường hợp auth thất bại, và ngược lại. Bốn điều kiện của `CAPABILITY_MODEL.md`
§II.4 (Independent Capability, Independent Lifecycle, Outside Capability) KHÔNG thoả cho bất kỳ
tách nhỏ nào trong số đó.

**Vì sao KHÔNG di dời `ethdca/state`/`ethdca/seed`.** `DEC-043` đã LOCK ranh giới persistence
"bên trong `ethdca/state`" như một ràng buộc kiến trúc của `T-12`. Cô lập dữ liệu hiện tại dựa
vào `firestore.rules` (allow-list tường minh, đã verify bằng emulator tại `DEC-023`), không dựa
vào tên namespace — đổi tên không tăng cô lập, chỉ tạo rủi ro migration không cần thiết.

**Vì sao Google Sign-In, không phải link-credential vào Anonymous UID.** `DEC-020` R1 (phương án
cũ) đòi `linkWithCredential` phức tạp hơn để giữ được Anonymous UID gốc. Vì Owner Decision lần
này (chỉ thị phiên §5) xác định "Anonymous Auth is no longer the durable authority", không còn lý
do giữ Anonymous UID — Google Sign-In trực tiếp cho UID bền vững hơn (gắn tài khoản, không gắn
thiết bị) mà không cần bước linking, đơn giản hơn đúng theo Personal Tool Simplification
Principle (`DEC-021`).

## 4. Điều KHÔNG làm trong phiên này (đúng chỉ thị "architecture + task definition only")

- KHÔNG viết một dòng code sản phẩm nào (`webapp/**`, `firestore.rules`, `firebase.json` không
  đổi trong phiên này — chỉ đọc và phân tích).
- KHÔNG chuyển `T-14` sang `IN_PROGRESS`.
- KHÔNG tạo project Firebase mới, không tài khoản Google thứ hai.
- KHÔNG giải quyết `H-46` (SELL) — vẫn mở, chờ Owner Decision riêng.
- KHÔNG đổi schema `coindca.ledger/2`, công thức `derive()`/`update()`/`migrate()`/`destructive()`,
  hay bất kỳ bất biến `INV-1`…`INV-15` nào.
- KHÔNG redesign UX Step B (`T-13`) ngoài việc mô tả một điểm vào nhỏ cho đăng nhập/backup/restore
  (thiết kế cụ thể để lại cho phiên thi hành).
- KHÔNG tự đóng `H-42`/`H-49` — cả hai giữ HARDENING, chờ `T-14` đạt Completion Gate.
- KHÔNG tự động sửa `H-44`/`H-45`/`H-47`/`H-48`/`H-50` (không liên quan bước C).

## 5. Validators chạy trong phiên

    python governance/scripts/governance/routing_engine.py \
      --d 3 --r 3 --b 3 --a 2 --x 3 --u 2 --v 3 --h 3 --c 3 --f 3 \
      --category authentication --category security
    -> tier=C model=Opus model_score=2.85 effort=xhigh effort_score=2.8
    -> model_floors=[safety_business:min_C] effort_floors=[safety_business:min_high]

    python governance/scripts/governance/validate_routing.py
    python governance/scripts/governance/sync_easy_roadmap.py
    python governance/scripts/governance/validate_easy_roadmap.py

Kết quả các lệnh trên: xem log cuối phiên (điền sau khi chạy). Kỳ vọng: PASS trên
routing/roadmap; `validate_evidence.py`/`validate_task_completion.py` PASS-vacuous (khiếm khuyết
glob đã biết, `H-08`, không phải bằng chứng closure cho phiên này).

## 6. Đường dẫn tiếp theo

`NEXT SMALLEST ACTION` = mở một phiên thi hành riêng cho `T-14` (đúng tiền lệ `T-12`/`T-13`).
Điều kiện đầy đủ: `PROJECT/PROJECT_PROGRESS.md` § Next Session.
