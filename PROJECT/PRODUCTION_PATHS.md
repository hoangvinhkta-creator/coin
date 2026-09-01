# PRODUCTION PATHS — dự án coin (ETH DCA Operating System V2.1.5)

Status:
ACTIVE

Nguồn thẩm quyền:
`governance/v4/CORE/PRODUCTION_PATH_RULE.md` (§ "Production Paths Are Declared, Not Inferred")

Ngày khai báo:
2026-09-01 (phiên adoption V4.3)

Mục đích:
Khai báo tường minh đâu là **production path**. Agent KHÔNG được tự suy luận tại thời điểm
thực thi xem file nào là "production"; agent đọc bảng này. Ba nơi dùng bảng này:

1. phân loại finding BLOCKING / HARDENING (`REVIEW_PROTOCOL.md`);
2. đo Delivery Change Budget tích luỹ (`DELIVERY_LOOP.md`);
3. xác nhận "production code diff = 0" trong các phiên governance-only.

---

## 1. Production paths (ĐANG có đường vào runtime)

| Đường dẫn | Vai trò trong runtime | Ghi chú |
|---|---|---|
| `src/eth_dca_os/**` | Backtest engine Python — đường duy nhất sinh ra official run và verdict | 26 module; là production path chính |
| `webapp/app_logic.js` | Logic sổ sách của app web (ghi giao dịch, vốn, P&L) | Có thể được dùng với tiền thật — xem RSK-001, RSK-003 |
| `webapp/engine.js` | Bản cài đặt JS song song của engine chiến lược | Nguồn của rủi ro parity RSK-002 |
| `webapp/app_shell.html` | Vỏ app web được người dùng mở trực tiếp | |
| `webapp/build_app.js` | Sinh ra bản app phát hành từ shell + logic | Đầu ra là artifact người dùng chạy |
| `pyproject.toml` | Khai báo dependency và cấu hình chạy | Ảnh hưởng kết quả tính toán |
| `pyproject.lock` | Ghim phiên bản; hash của file này đi vào run record | `dependency_lock_hash` — WP-A1 |

Lệnh đo budget chuẩn (không cộng tay từ báo cáo):

    git diff --shortstat <BASELINE_SHA>..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock

---

## 2. KHÔNG phải production path

| Đường dẫn | Lý do |
|---|---|
| `tests/**` | Test harness; không có đường vào runtime của người dùng |
| `webapp/test_app.js`, `webapp/test_zone.js` | Test của app web (nằm trong `webapp/` nhưng là test) |
| `docs/**` | Tài liệu, task, review, session, spec |
| `governance/**` | Rule, template, validator, reference |
| `PROJECT/**` | Trạng thái dự án |
| `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `README.md` | Entry point và adapter |

Ngoại lệ có ý nghĩa: `docs/CONVENTIONS.md` KHÔNG phải production path, nhưng nó **được
Exit Criteria của WP-A1 nêu đích danh**, nên sai lệch giữa nó và mã vẫn có thể BLOCKING qua
đường Completion Gate — không qua đường production path. Hai cơ chế này độc lập; đừng nhầm.

---

## 3. Ranh giới quan trọng khi phân loại finding

Một counterexample chỉ **production-realistic** khi dựng được từ ít nhất một trong bốn
nguồn canonical của `PRODUCTION_PATH_RULE.md`. Với dự án này, bốn nguồn đó cụ thể là:

1. **Production schema/annotation inventory hiện tại** — `lineage.json` do
   `src/eth_dca_os/data/fetch.py::fetch_all` hoặc `data/synth.py::generate` sinh ra;
   `backtest_runs.jsonl` và `*_metrics.json` do `reporting.py::save_run` ghi;
   `REQUIRED_SERIES` / `VALID_SOURCES` / `REAL_SOURCES` trong `data/dataset.py`.
2. **Repo config hiện tại** — `pyproject.toml`, `pyproject.lock`, tham số mặc định của
   `cli.py` (ví dụ `--dev-limit` dùng `n_sims=200`).
3. **Approved Golden fixture** — **CHƯA TỒN TẠI**. Xem §4.
4. **Approved raw/production-like data** — **CHƯA TỒN TẠI**. `BLK-001` chặn đường tới
   `data.binance.vision` / `api.binance.com`; toàn bộ dữ liệu hiện có là synthetic.

Hệ quả trực tiếp và phải được tôn trọng: vì nguồn 3 và 4 chưa tồn tại, phần lớn
counterexample về dữ liệu thật hiện chỉ dựng được bằng **stub I/O của reviewer**. Stub dựng
trên mã production thật và tham số production thật vẫn tính là nguồn 1 + 2. Nhưng một
counterexample chỉ dựng được bằng cách **sửa tay artifact** (`lineage.json`) mà không có
đường sinh ra nó từ mã hiện tại thì mặc định là HARDENING, không phải BLOCKING.

---

## 4. Golden baseline

    GOLDEN_BASELINE_SHA = PENDING_OWNER_DATA / MIGRATION_REQUIRED

Lý do: "Golden" của dự án này là **official run** (T-06). T-06 đang `PLANNED` và bị chặn
bởi hai nhóm điều kiện độc lập (GATE-A chưa PASS; BLK-001 chưa gỡ). Chưa có lần chạy chính
thức nào, nên chưa có Golden trace nào có đủ thẩm quyền.

Không được chọn một SHA tiện lợi rồi gọi đó là Golden baseline. Xem
`PROJECT/REVIEW_BUDGET_LEDGER.md` §3 để biết baseline nào đang được dùng tạm cho phép đo
Delivery Change Budget và giới hạn của nó.
