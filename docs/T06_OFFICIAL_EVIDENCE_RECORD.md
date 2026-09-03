# T-06 — Bản ghi bảo toàn evidence chính thức (Official Evidence Record)

Trạng thái: **BẢO TOÀN EVIDENCE — KHÔNG phải Completion Gate, KHÔNG phải Owner Decision.**
`T-06` vẫn `PLANNED` trong `PROJECT/PROJECT_PROGRESS.md`. File này KHÔNG tự cấp cho `T-06`
tư cách `DONE`, KHÔNG resolve `BLK-001`, và KHÔNG viết acceptance criteria hậu nghiệm.

Ngày lập: 2026-09-03. Phiên: S019 (`docs/sessions/S019-t06-evidence-preservation.md`).
Code commit của official run: `5228130677e9e9875335eef890b6ed748a384603`.

## 0. File này LÀ gì / KHÔNG LÀ gì

**LÀ**: một bản kê khai tối thiểu, reviewable, đối chiếu được — cho biết official run nào đã
xảy ra, chạy trên code/dataset/environment nào, tạo ra record ID và verdict gì, và raw
artifact được bảo toàn ở đâu về mặt logic. Mọi khẳng định đều gắn nhãn theo mức độ kiểm
chứng được (§1–§7), không trộn lẫn.

**KHÔNG LÀ**: raw dataset, raw run artifact, Completion Gate, Ready Gate, Owner Decision, hay
một tuyên bố rằng `T-06` đã qua governance đầy đủ. Owner narrative không tự động trở thành
`MACHINE_VERIFIED` chỉ vì được chép vào đây.

## 1. Ba mức nhãn dùng trong toàn file

| Nhãn | Ý nghĩa |
|---|---|
| **REPOSITORY-VERIFIED** | Tái lập/đối chiếu được TỪ chính repository này, bằng công cụ/mã nguồn tại `code_commit` đã khai, trong phiên tạo file này. |
| **OWNER-REPORTED / EXTERNALLY-VERIFIED** | Owner khai báo và/hoặc tự verify trên máy đã chạy `T-06`; repository KHÔNG có phương tiện để tái lập độc lập (thiếu raw bytes). Ghi lại nguyên văn, không nâng cấp nhãn. |
| **NOT PRESENT IN REPOSITORY** | Không tồn tại dưới bất kỳ hình thức nào trong git tree hiện tại — kể cả gián tiếp. |

---

## 2. Định danh mã nguồn — REPOSITORY-VERIFIED

| Trường | Giá trị | Cách kiểm |
|---|---|---|
| `code_commit` | `5228130677e9e9875335eef890b6ed748a384603` | `git rev-parse HEAD` tại nhánh này = giá trị trên; `git ls-remote origin` xác nhận cùng SHA trên remote |
| `dependency_lock_hash` | `9ea0150fcf27c12d39335db95a01151a79e2f94aa64b0eda722fd939f76c4d9a` | `sha256sum pyproject.lock` tại `code_commit` = giá trị trên (đối chiếu lại tại S018 và S019) |

### 2.1 Git tag chính thức — REPOSITORY-VERIFIED

Tag annotated `v2.1.5-official-T06` tồn tại trên `origin` và **peel đúng** về `code_commit`:

```
$ git ls-remote --tags origin
5b2e5278daa73852ecd72deae836f76fefc055d9  refs/tags/v2.1.5-official-T06
5228130677e9e9875335eef890b6ed748a384603  refs/tags/v2.1.5-official-T06^{}   <-- peeled target

$ git cat-file -p v2.1.5-official-T06
object 5228130677e9e9875335eef890b6ed748a384603
type commit
tag v2.1.5-official-T06
tagger hoangvinhkta-creator <hoangvinhkta@gmail.com>

CoinDCA ETH Strategy V2.1.5 - T-06 official run
Official verdict: DO_NOT_BUILD
Gate 1: FAIL
OOS hard condition: FAIL
Official dataset hash: 3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5
```

Tag là **annotated** (object riêng, không phải lightweight ref) và peeled commit khớp CHÍNH
XÁC `code_commit` đã khai. Nội dung message của tag (verdict, dataset_hash) là do Owner viết
lúc tạo tag — bản thân việc tag TỒN TẠI và trỏ đúng chỗ là REPOSITORY-VERIFIED; nội dung message
được đối chiếu chéo với các mục §3/§5 dưới đây và **khớp**.

---

## 3. Định danh dataset

### 3.1 `dataset_hash` khai báo
`3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5`

### 3.2 Thuật toán tính — REPOSITORY-VERIFIED (nhất quán nội bộ, KHÔNG xác thực byte gốc)

`src/eth_dca_os/data/dataset.py::_dataset_hash` tính:
`sha256(json.dumps([file_hash cho từng file, theo thứ tự sorted(glob("*.parquet"))]))`.

Đưa ba `file_hash` do Owner khai (§4) vào ĐÚNG thuật toán này (thứ tự `sorted()` alphabetically
= `BTCUSDT_1d.parquet`, `ETHUSDT_15m.parquet`, `ETHUSDT_1d.parquet`), tái tính trong phiên này:

```
blob = ["ea90ae2f0438216e573421252ecb62da31490c1121ca86a28d56945df036beed",
        "1fb60015fbe110fb9a42458cac43345607682e10a8a648666e8e26cacc0eebbd",
        "699596c78bc525742439e83c92aa93d92f69e5e2a3d3091c8b5abf33a443f8ee"]
sha256(json.dumps(blob).encode()).hexdigest()
  = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5
```

**Khớp tuyệt đối** với `dataset_hash` khai báo và với message của git tag (§2.1). Đây là bằng
chứng **nhất quán thuật toán** — bốn con số (ba `file_hash` + một `dataset_hash`) tự OK với
nhau theo đúng mã đang chạy tại `code_commit` này. Nó **KHÔNG** chứng minh ba `file_hash` đó
thực sự là sha256 của ba file Binance thật — điều đó đòi hỏi chính byte của ba file `.parquet`,
thứ repository này không có (§4, §8 mục C).

### 3.3 `official_reason = "verified"` — ý nghĩa theo mã, KHÔNG tự kiểm chứng được ở đây

`official_eligibility()` chỉ trả `(True, "verified")` sau khi (thứ tự cố định trong mã):
lineage đúng dạng, không trùng/thừa/thiếu series so với `REQUIRED_SERIES`, mỗi series không
rỗng, `source ∈ REAL_SOURCES = {binance_bulk_archive, binance_rest}`, độ phủ so với khoảng
yêu cầu đạt (`missing ≤ 1% × expected`), **và** `verify_lineage()` đối chiếu lại `file_sha256`
của TỪNG file trên đĩa với `file_hash` khai trong lineage, cộng `dataset_hash` tái tính khớp.
Bước cuối đòi hỏi đọc byte thật của ba file `.parquet` — chỉ chạy được trên máy có file đó.
Nhãn: **OWNER-REPORTED / EXTERNALLY-VERIFIED** cho việc bước cuối này thực sự đã chạy đúng.

---

## 4. Bản kê SHA-256 raw artifact (16 file) — OWNER-REPORTED / EXTERNALLY-VERIFIED

Owner khai đã backup 16/16 file này ra một vị trí độc lập trên máy đã chạy `T-06`, tự verify
SHA-256 khớp giữa bản gốc và bản backup. **Không file nào trong bảng này nằm trong git tree.**
Repository không có byte gốc để đối chiếu độc lập — nhãn giữ nguyên OWNER-REPORTED, KHÔNG nâng
lên MACHINE_VERIFIED.

| Đường dẫn (trên máy đã chạy `T-06`) | SHA-256 (Owner-reported) |
|---|---|
| `data/raw/BTCUSDT_1d.parquet` | `ea90ae2f0438216e573421252ecb62da31490c1121ca86a28d56945df036beed` |
| `data/raw/ETHUSDT_15m.parquet` | `1fb60015fbe110fb9a42458cac43345607682e10a8a648666e8e26cacc0eebbd` |
| `data/raw/ETHUSDT_1d.parquet` | `699596c78bc525742439e83c92aa93d92f69e5e2a3d3091c8b5abf33a443f8ee` |
| `data/raw/lineage.json` | `71460726d210a5997951c790822a7fa5905b7089cee3df717d22759e38ed34f3` |
| `results/backtest_runs.jsonl` | `0eaa05c0b7622b1f1e4e2e0ad4abf9ba584cda7ea933d94dc1127457bb321afa` |
| `results/baseline_808b61fa5ffe_metrics.json` | `1bda31955d6730ec8df1823813fe100b2ca55b0cb63306db0f6fbead7ad0b88c` |
| `results/gate1_eef3d951aaa0_metrics.json` | `cd0567d08e4f87554dfb36511216e6a724dddfd48e74aa12428b000db4e96e99` |
| `results/gate2_b08da9ba5229_metrics.json` | `ed998511a48c78b2aaeddb8893010bc23039022f8e6f4509bbf9f549bca1d011` |
| `results/gate3_a0099f6bf0c0_metrics.json` | `fdc5e46183fcd78e1abe4bbc26c7aef9e927ea1d183fcf2902dc5c98b0817e45` |
| `results/manifests/gate2_manifest.csv` | `277e5b13417ac9011425d7c27f205a4178b37ba8d7b737420b3fc713a9553f40` |
| `results/manifests/gate2_manifest.json` | `da69848b2743056b3b9fec53f67e9d265ac1b60ed1252baed243bf420f8e4726` |
| `results/manifests/gate3_manifest.csv` | `8230be7b72628bca3efe44eeb8248922a521db731d2964032d5f3028a20c1e6d` |
| `results/manifests/gate3_manifest.json` | `6bea22ebea2e17b2cd3a664ca2fbb4c702f1bb8e88c26ab018329d6f86bd2f23` |
| `results/pipeline_state.json` | `db87d1068c28bf311b78b16741a362447fcfb492d96299085b240ff4ac96f3b4` |
| `results/random_control_21b7d88e9691_metrics.json` | `b0520823059ff2429103280a052fa9cfab2dd11cf3432b3623c5183b232665d7` |
| `results/report.json` | `281b3d878822cbab3d7b3c6c16068f92754a6e913ae34a2c7f42888bb536857c` |

Tổng: 16/16 khai đã backup độc lập, Owner tự verify SHA-256 PASS. Vị trí lưu trữ là **mô tả
logic**, không phải dependency của repository: một bản backup thao tác trên máy cá nhân của
Owner, ngoài phạm vi git. Đường dẫn tuyệt đối cụ thể trên máy Owner **cố ý không được chép**
vào file này.

Đối chiếu chéo với `results/manifests/gate2_manifest.json` và `gate3_manifest.json`: đây là
ĐÚNG hai file mà `freeze_manifests()` ghi ra (`src/eth_dca_os/manifests.py`). §5 dưới đây tái
lập được `manifest_hash` bên trong hai file này TỪ mã nguồn (không cần đọc chính file), nên dù
bản thân file không có trong repo, **nội dung mong đợi của chúng đã được kiểm chứng độc lập**.

---

## 5. Pre-T06 manifest freeze — REPOSITORY-VERIFIED (tái lập từ mã + seed, không cần dataset)

`manifest_hash` chỉ phụ thuộc mã nguồn và seed cố định, KHÔNG phụ thuộc dataset — nên tái lập
được đầy đủ mà không cần raw data và không cần chạy lại `T-06`. Đã tái lập trong S018, đối
chiếu lại tại S019:

| | Khai báo | Tái lập tại `code_commit` |
|---|---|---|
| Gate 2 — `ofat_candidates` | 19 | 19 |
| Gate 2 — `rejected` | 1 | 1 |
| Gate 2 — `ofat_valid` | 18 | 18 |
| Gate 2 — `interaction` | 200 | 200 |
| Gate 2 — `denominator` | 219 | 219 |
| Gate 2 — `manifest_hash` | `e34f92ae7b34ec3ff3a6bdd54c2576ba6126b078db9c309027dcd74eca7e162e` | **KHỚP** |
| Gate 3 — `deterministic` | 14 | 14 |
| Gate 3 — `sampled` | 100 | 100 |
| Gate 3 — `size` | 114 | 114 |
| Gate 3 — `manifest_hash` | `ef30f657d30c9c144fb68315a79e50852ebb6ee013d477712fa73b4d1b061f1f` | **KHỚP** |

---

## 6. Kết quả official run — OWNER-REPORTED / EXTERNALLY-VERIFIED

Repository không có `results/backtest_runs.jsonl` hay bất kỳ `*_metrics.json` nào (§8 mục C),
nên toàn bộ mục này là khai báo của Owner, chưa tái lập độc lập được từ repo.

### 6.1 Record ID chính thức

| Loại | Record ID |
|---|---|
| GATE1 | `gate1_eef3d951aaa0` |
| GATE2 | `gate2_b08da9ba5229` |
| GATE3 | `gate3_a0099f6bf0c0` |
| RANDOM_CONTROL | `random_control_21b7d88e9691` |
| BASELINE | `baseline_808b61fa5ffe` |

Cả năm khai `provenance_resolved=true`, `provenance_unresolved=[]`,
`code_commit`/`dataset_hash`/`dependency_lock_hash` như §2/§3.

### 6.2 Kết quả gate và verdict

Gate 1 FAIL (PrimaryMedian 97.48%) · OOS FAIL (AE 92.94%, 21 tháng, SHORT_OOS) · Gate 2 FAIL
(PreOOS pass share 0.00%) · Gate 3 FAIL (realistic NetEdge PM −0.0264).

**Verdict: `DO_NOT_BUILD`**. Reasons: `Gate 1 FAIL`, `OOS hard condition FAIL`.
`can_proceed_to_app = false`.

Failure Signals TRUE: FS-01, FS-02, FS-03, FS-04, FS-08, FS-10, FS-11.
FALSE: FS-05, FS-06, FS-07, FS-09, FS-12. UNKNOWN: rỗng.

### 6.3 Nhất quán với ngưỡng đã đóng băng (REPOSITORY-VERIFIED, xác nhận lại từ S018)

Toàn bộ số liệu §6.2 đã được đối chiếu tại S018 với ngưỡng cứng trong `gates.py` / `verdict.py`
/ `failure_signals.py` tại `code_commit` này và **nhất quán tuyệt đối** — không lặp lại chi
tiết ở đây, xem `docs/sessions/S018-post-t06-evidence-closure.md` §2.1.

---

## 7. FS-12 — đối chiếu số học — REPOSITORY-VERIFIED (given đầu vào Owner-reported)

Đầu vào (Owner-reported, `regime_advantage_share`):
`CRASH=+1.6273303598351732`, `NORMAL=−3.3713896238538967`, `RECOVERY=−0.5249124669397018`,
`STRESSED=+1.1754501507347552`.

Đưa đúng bốn số này vào `_advantage_share()` (`src/eth_dca_os/metrics.py`) trong phiên S018:

```
positive_mass = 1.6273303598351732 + 1.1754501507347552 = 2.8027805105699284
share         = max(adv) / positive_mass = 1.6273303598351732 / 2.8027805105699284
              = 0.5806128427460292
net_advantage = sum(adv) = -1.0935215802236702
```

`net_advantage` tái tính khớp **tới bit cuối** với khai báo. `share = 0.5806… ≤ 0.80` ⇒ FS-12
= FALSE, khớp khai báo. Bốn số đầu vào (CRASH/NORMAL/RECOVERY/STRESSED) tự chúng là
OWNER-REPORTED (repository không có timeline giao dịch để tái tính); phép TOÁN từ bốn số đó
ra `share`/`net_advantage` là REPOSITORY-VERIFIED.

---

## 8. Ma trận NOT PRESENT IN REPOSITORY — đầy đủ

Không tồn tại dưới bất kỳ hình thức nào trong git tree tại `code_commit` này hay bất kỳ đâu
khác trong repository:

- `data/raw/*.parquet` (ba file dataset gốc)
- `data/raw/lineage.json` (nội dung — chỉ có hash khai báo, không có nội dung)
- Toàn bộ `results/` — `backtest_runs.jsonl`, năm `*_metrics.json`, `pipeline_state.json`,
  `report.json`, `manifests/gate2_manifest.{json,csv}`, `manifests/gate3_manifest.{json,csv}`
- Bất kỳ thư mục `evidence/`/`artifacts/` nào

`results/` và `data/raw/*.parquet` nằm trong `.gitignore` — vắng mặt khỏi git là **hợp lệ**
theo cấu hình hiện có, không phải một khiếm khuyết của phiên này.

---

## 9. File này CHỨNG MINH được gì

- Official run tham chiếu đúng một `code_commit` xác định, có tag annotated trỏ đúng chỗ.
- `dependency_lock_hash` khai đúng bằng hash thật của `pyproject.lock` tại commit đó.
- `dataset_hash` khai đúng bằng kết quả thuật toán `_dataset_hash()` thật khi đưa ba
  `file_hash` Owner khai vào — bốn con số tự nhất quán với nhau theo mã đang chạy.
- Pre-T06 manifest freeze (Gate 2/Gate 3, tất cả 10 giá trị + 2 hash) tái lập được **hoàn
  toàn độc lập** từ mã nguồn, không cần dataset, không cần chạy lại `T-06`.
- Bốn kết quả gate, Failure Signal, và verdict Owner khai **nhất quán** với ngưỡng cứng đã
  đóng băng trong mã tại `code_commit` này (không mâu thuẫn nội bộ nào bị phát hiện).
- Phép toán FS-12 (`net_advantage`, `share`) đúng với công thức `_advantage_share()` thật.

## 10. File này KHÔNG chứng minh được gì

- Rằng ba `file_hash` trong §4 THỰC SỰ là sha256 của dữ liệu Binance thật (cần byte gốc —
  repository không có).
- Rằng `official_eligibility()`/`verify_lineage()` THỰC SỰ đã chạy trên máy Owner và đối
  chiếu đúng byte đĩa (bước cuối của official_eligibility đòi hỏi file thật).
- Rằng các trường số trong `*_metrics.json` (PrimaryMedian, AE, NetEdge…) được TÍNH ĐÚNG bởi
  engine — file này chỉ đối chiếu chúng với NGƯỠNG đã đóng băng, không tái chạy engine trên
  dataset thật để tái sinh chúng (Master Index §6 cấm chạy lại official run).
- Rằng `T-06` đã đi qua Ready Gate / frozen Completion Gate — nó CHƯA (`docs/sessions/S018-post-t06-evidence-closure.md` §4). File này không thay đổi sự thật đó.
- Rằng `BLK-001` đã RESOLVED trong sổ governance — chưa; file này không tự resolve nó.

---

## 11. Không đổi gì (xác nhận rõ cho người đọc sau)

`T-06` giữ nguyên `PLANNED`. `BLK-001` giữ nguyên ACTIVE trong `PROJECT/PROJECT_PROGRESS.md`.
Không thuật toán, không ngưỡng, không verdict nào bị đổi. Official run **không** bị chạy lại
để tạo file này — mọi phép tái lập ở trên (§3.2, §5, §7) chỉ dùng mã + seed + số Owner khai,
không đụng tới `ethdca fetch`/`ethdca run`. `H-13` và các hardening khác **không** bị xử lý ở
đây — việc ghi evidence này không đòi hỏi cập nhật `docs/CONVENTIONS.md`.

## 12. Còn cần Owner Decision (KHÔNG ban hành ở đây)

Danh sách đầy đủ (không tạo mới, không đổi khỏi trạng thái nêu) tại
`docs/sessions/S018-post-t06-evidence-closure.md` §13 (`OD-T06-01`…`OD-T06-10`). File này
đóng góp trực tiếp cho `OD-T06-01` (bảo toàn — đã xác nhận qua §4) và `OD-T06-02` (cơ chế đưa
evidence vào repo — bản thân file này là một phần câu trả lời khả dĩ, KHÔNG phải quyết định).
Đường (A)/(B) của `OD-T06-03` (hợp thức hoá gate) **vẫn treo**, chờ Owner chọn — Owner đã báo
sẽ chọn (B) trong một phiên riêng, chưa ban hành.
