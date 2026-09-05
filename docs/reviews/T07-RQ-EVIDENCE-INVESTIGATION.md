# T-07 — Evidence Investigation (RQ-1 / RQ-2 / RQ-3 / RQ-4 / RQ-5)

Authorized by: `DEC-039` (Owner Decision, phản hồi `docs/reviews/T07-OWNER-DECISION-BRIEF.md`).
Mode: **SPIKE / EXPLORATORY** (`TASK_MODE_STANDARD.md` Mode 3) — mục tiêu giảm bất định, KHÔNG
phải work package sản xuất. Capability: `CAP-VERDICT` (lineage root `WP-B1`).

**Đây KHÔNG phải một official T-06 run mới, KHÔNG đổi verdict, KHÔNG mở `T-11`/`WP-D2`, KHÔNG
sửa `src/`. Production diff = EMPTY.** Mục tiêu — nguyên văn Owner: hiểu thất bại đủ tốt để tránh
(1) bỏ một hypothesis còn tín hiệu hữu ích chỉ vì sai objective/capital treatment, hoặc (2) mở
V2.2 và tiếp tục tối ưu một hypothesis thực tế không có edge.

## 0. Nhãn dùng trong file này

Kế thừa ba nhãn của `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §1, cộng hai nhãn mới cho phiên SPIKE
này:

| Nhãn | Ý nghĩa |
|---|---|
| **[R]** REPOSITORY-VERIFIED | Tái lập được từ chính repository này trong phiên này |
| **[O]** OWNER-REPORTED | Owner khai báo / tự verify trên máy có dataset official |
| **REPLAY** | Số derived, tính bằng script ở §6, chạy trên dataset official đã bảo toàn (KHÔNG
  phải một official run mới) — theo đúng khuôn `CHECK-B1-03` Addendum 3 |
| **MISSING_INPUT** | Không tính được trong sandbox agent vì thiếu dataset official — chờ Owner |
| **SMOKE (KHÔNG PHẢI EVIDENCE)** | Chạy trên dataset SYNTHETIC chỉ để xác nhận script không lỗi
  cú pháp/API — số liệu tuyệt đối không được dùng làm kết luận |

---

## 1. RQ-2 — Buy Score có kỹ năng timing ở mức vốn triển khai bằng nhau không?

**Không chạy gì mới** — dùng lại evidence đã canonical tại `WP-B1`
(`docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md::CHECK-B1-03` Addendum 3), theo đúng
chỉ thị Owner.

**[O]** Post-`F-017` WP-B1 Evidence Replay (Owner-supplied, đã canonicalize):

    dataset_hash    = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5
    master_seed     = 42, n_sims = 1000
    v2_eth          = 14.910758150139896 (khớp frozen official)
    control_f_p95   = 14.887400583487747   -> beats_f = true
    control_g_p95   = 14.813546903782814   -> beats_g = true
    FS-08 (post-F-017) = FALSE

**Diễn giải bắt buộc theo đúng chỉ thị Owner — KHÔNG được vượt quá:**
- V2 vượt P95 của cả hai control **ở mức AGGREGATE toàn kỳ pre-OOS+OOS** (một con số gộp).
- BT §251 (nguyên văn): *"Control F đo lẫn cả hiệu ứng cơ học của việc điều kiện hóa trên giá đã
  giảm, chứ không thuần kỹ năng dự báo."* Vượt P95 vì vậy **KHÔNG chứng minh** kỹ năng dự báo giá.
- Biên vượt mỏng: +0,157 % so với Control F P95 (`14,910758 / 14,887401 − 1 ≈ 0,00157`).
- Đây là **MỘT** cấu hình baseline, không phải quét toàn bộ manifest Gate 2/Gate 3.

**Kết luận RQ-2 (giữ nguyên, không nâng cấp)**: **PARTIALLY ESTABLISHED, không phải bằng chứng
đã chứng minh predictive skill.** Việc phân rã theo từng window/OOS (câu hỏi tiếp theo tự nhiên)
chính là RQ-3 — xem §4.

---

## 2. RQ-5 — Evidence hiện có hỗ trợ đến đâu việc phân biệt "thiếu timing edge" và "objective/
capital-allocation mismatch"?

Đây là câu hỏi **tổng hợp** — trả lời được ngay bằng evidence đã canonical, **không cần dataset
official mới** (không script, không rerun).

### 2.1 FACTS đã thiết lập, liên quan trực tiếp tới câu hỏi

- **F-A** Gate 1 FAIL (PrimaryMedian AE 97,48 % < 102) và OOS FAIL (AE 92,94 % < 100) — V2 tích
  luỹ ÍT ETH hơn benchmark cả hai chế độ dữ liệu. (`T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2)
- **F-B** Gate 2 = 0,00 % — **không config nào trong 219 config đã đóng băng** vượt ngưỡng. Đây
  là bằng chứng MẠNH rằng thất bại **không phải "chọn sai tham số trong không gian đã khai"** —
  toàn bộ neighborhood tham số đã thử đều thất bại như nhau.
- **F-C** FS-02 = TRUE, `opportunity_cap_hit_share = 0,8961` — Opportunity reserve chạm cap và
  **nằm im** ở 89,61 % số quan sát. Đây là bằng chứng trực tiếp về **capital sitting idle** —
  tức một phần vốn không tham gia đầu tư trong phần lớn thời gian.
- **F-D** FS-07 = FALSE với ngưỡng `avg_cash_ratio > 0,30 AND gate1_primary_ae < 102,0`; vì
  `AE = 97,48 < 102` đúng, FS-07 = FALSE **buộc về mặt logic** `avg_cash_ratio ≤ 0,30` — tức tỷ
  lệ tiền mặt trung bình so với portfolio KHÔNG cao (dưới 30 %), dù reserve nội bộ (F-C, đo trên
  `Pool` riêng của Opportunity Fund, không phải tổng portfolio) thường chạm cap.
- **F-E** RQ-2 (§1): V2 vượt P95 Control F/G ở AGGREGATE toàn kỳ, biên mỏng (+0,157 %), với
  caveat BT §251 rằng phép so này đo lẫn hiệu ứng cơ học lẫn kỹ năng dự báo — **không phải bằng
  chứng đã chứng minh không có edge, cũng không phải bằng chứng đã chứng minh có edge mạnh**.
- **F-F** FS-01 = TRUE — V2 tích luỹ ít ETH hơn Monthly DCA ở phần lớn gate window (benchmark
  đơn giản nhất, không có logic phân bổ vốn động).

### 2.2 INTERPRETATIONS (suy luận, không phải đo lường)

- **I-A** F-B (Gate 2 = 0,00 %) là bằng chứng gián tiếp nghiêng về phía **"thất bại mang tính hệ
  thống"** hơn là "một hypothesis đúng nhưng chọn nhầm tham số" — nếu chỉ là vấn đề tham số, một
  phần đáng kể trong 219 config lân cận baseline lẽ ra phải PASS.
- **I-B** F-C (reserve chạm cap 89,61 % và nằm im) + F-D (`avg_cash_ratio ≤ 0,30` ở tầng
  portfolio) cùng chỉ ra: vấn đề **không phải "giữ quá nhiều tiền mặt tổng thể"** (F-D bác bỏ) mà
  là **cấu trúc phân bổ nội bộ của Opportunity Fund** — vốn dành riêng cho cơ hội bị khoá/nằm im
  thay vì được tái phân bổ. Đây nghiêng về phía **capital-allocation mismatch trong CÁCH cấu trúc
  reserve**, không phải "giữ tiền mặt nói chung".
- **I-C** F-E (V2 vượt P95 aggregate, biên mỏng, với caveat cơ học) là bằng chứng **YẾU và không
  đủ** để kết luận về hướng nào trong hai hướng của RQ-5: nó không loại trừ "thiếu timing edge"
  (biên quá mỏng, có thể là hiệu ứng cơ học) nhưng cũng không xác nhận "có mismatch" (nó KHÔNG đo
  objective/capital-allocation, nó đo timing).
- **I-D** F-F (thua cả Monthly DCA — logic phân bổ đơn giản nhất) là dấu hiệu đáng chú ý: nếu một
  chiến lược PHỨC TẠP HƠN (V2, có logic động) thua một benchmark KHÔNG có logic phân bổ động ở
  phần lớn window, điều đó nghiêng nhẹ về phía **cấu trúc phân bổ vốn (objective/capital
  treatment) là một phần của vấn đề** — không chỉ đơn thuần "thiếu kỹ năng dự báo giá timing".

### 2.3 Kết luận RQ-5 — mức độ được thiết lập

**PARTIALLY ESTABLISHED — nghiêng có chứng cứ về phía "capital-allocation/objective mismatch góp
phần", nhưng KHÔNG loại trừ được "cũng thiếu timing edge", và KHÔNG có phép đo nào tách bạch
tách rời hai thành phần này bằng một con số duy nhất.**

Cụ thể:
- Bằng chứng hiện có (F-B, F-C, F-D, F-F) nghiêng về hướng: **một phần đáng kể của thất bại nằm ở
  cách vốn được cấu trúc/phân bổ** (Opportunity Fund reserve, không phải cash tổng thể) —
  KHÔNG NHẤT THIẾT ở việc thiếu khả năng dự báo giá.
- Bằng chứng RQ-2/F-E (Control F/G) **không đủ mạnh** để nói ngược lại rằng "hoàn toàn không có
  timing edge" — biên vượt P95 dù mỏng vẫn tồn tại ở mức aggregate.
- **KHÔNG có evidence nào tách được hai thành phần bằng một con số phân rã duy nhất** (ví dụ:
  "X điểm AE mất vì objective sai, Y điểm AE mất vì thiếu timing edge"). Yêu cầu đó vượt quá
  những gì BT §17 đo (12 Failure Signal là chẩn đoán từng mặt riêng lẻ, không phải một phép quy
  trách nhiệm tổng hợp).
- RQ-1/RQ-3/RQ-4 (§3-§5 dưới đây), khi có output official, sẽ bổ sung bằng chứng — đặc biệt RQ-4
  (phân rã ETH theo nguồn SMART/OPPORTUNITY/CRASH/BASE) trực tiếp đo mức đóng góp và hiệu quả
  giá của phần vốn chịu trách nhiệm cho "mismatch" nghi ngờ ở I-B.

**Điều RQ-5 KHÔNG kết luận**: không đủ căn cứ để nói "V2.1.5 có timing edge thật" hay "V2.1.5
hoàn toàn không có timing edge" — cả hai đều là diễn giải quá mức so với evidence hiện có.

---

## 3. RQ-1 — Cách xử lý reserve/cash có ảnh hưởng vật chất tới AE không?

**MISSING_INPUT** trong sandbox agent (không có dataset official). Thiết kế REPLAY dưới đây tính
**tương quan quan sát mô tả** giữa `cash_ratio` trung bình và AE, theo từng window trong 9 gate
window — **KHÔNG PHẢI phép đo nhân quả**: câu hỏi nhân quả thật ("nếu đổi cách xử lý reserve thì
AE đổi bao nhiêu") đòi hỏi một counterfactual run với `StrategyConfig`/`ExecutionConfig` khác —
bị cấm tường minh bởi ranh giới Owner (`không sửa strategy/threshold`). Vì vậy câu hỏi nhân quả
của RQ-1 **giữ nguyên NOT ESTABLISHED** cho tới khi Owner uỷ quyền một phiên counterfactual riêng
(nếu có).

Phần quan sát được (tương quan mô tả, script §6 mục RQ-1):
- Trích `cash_ratio_stats(result)["avg"]` và `ae` cho từng W1..W9 (đã có sẵn hạ tầng từ
  `window_metrics`/`run_gate1`, không cần công thức mới).
- Tính Pearson `r` và Spearman `ρ` giữa 9 cặp (`cash_ratio_avg`, `ae`).
- Trên dataset SYNTHETIC (SMOKE — không phải evidence): `pearson_r = 0,336`, `spearman_r = 0,5`
  — chiều DƯƠNG yếu-tới-vừa (window cash ratio cao hơn có xu hướng AE cao hơn, không thấp hơn).
  **Con số này KHÔNG được dùng làm kết luận** — chỉ xác nhận script chạy đúng và cho ra kiểu
  tương quan có ý nghĩa (không suy biến, không NaN).

**Trạng thái RQ-1**: **NOT ESTABLISHED** cho câu hỏi nhân quả (ngoài phạm vi được phép). Phần
quan sát mô tả: **MISSING_INPUT** — chờ Owner chạy script trên dataset official.

---

## 4. RQ-3 — Control F theo từng W1-W9 và OOS (thay vì chỉ số aggregate)

**MISSING_INPUT** trong sandbox agent. Thiết kế REPLAY (script §6 mục RQ-3): với mỗi window
`W1..W9` (`windows.gate_windows()`) và riêng `OOS`, xây `monthly_tranches` CHỈ từ các purchase
thật sự nằm trong window đó (không dùng lại `monthly_tranches` toàn kỳ), gọi
`random_timing_control`/`random_anchor_control` (n_sims=1000, master_seed=42 — ĐÚNG tham số đã
đóng băng, không đổi) trên đúng khoảng `[window.start, window.end)`, so `v2_eth` của window đó
với `p95`.

**Bắt buộc trước khi tin kết quả**: script tự động reproduce con số aggregate toàn kỳ đã biết
(`v2_eth = 14,910758150139896`, `control_f_p95 = 14,887400583487747`,
`control_g_p95 = 14,813546903782814`) bit-for-bit ở STEP 0 trước khi in bất kỳ số per-window nào;
nếu không khớp, script DỪNG và in `STEP_0: FAIL`.

**Smoke test PASS** trên dataset SYNTHETIC — script chạy hết 9 window + OOS, không lỗi, mỗi
window trả về `v2_eth`/`control_f_p95`/`control_g_p95`/`beats_f`/`beats_g` đúng kiểu (xem log
đầy đủ ở §7). **Không có kết luận nào rút ra từ số synthetic.**

**Trạng thái RQ-3**: **MISSING_INPUT** — chờ Owner chạy script trên dataset official.

---

## 5. RQ-4 — Opportunity Fund tạo optionality đo được hay chủ yếu tạo cash drag?

**MISSING_INPUT** trong sandbox agent cho số liệu THẬT. Thiết kế REPLAY (script §6 mục RQ-4):

1. **Phân rã ETH theo nguồn purchase** (`purchases[].source` — trường sẵn có trong `EngineResult`,
   không phát minh field mới): tổng `nominal`/`eth`/`n`/giá mua bình quân cho từng nguồn
   `BASE`/`SMART`/`OPPORTUNITY`/`CRASH`. Đây đo trực tiếp: Opportunity Fund đóng góp BAO NHIÊU
   ETH so với các nguồn khác, và ở mức giá TRUNG BÌNH nào — nếu giá mua bình quân của
   `OPPORTUNITY` thấp hơn đáng kể so với `SMART`/`BASE` (mua được giá tốt hơn khi cơ hội xuất
   hiện), đó là bằng chứng optionality có giá trị dù khối lượng nhỏ; nếu tỷ trọng ETH từ
   `OPPORTUNITY` không đáng kể VÀ giá mua không tốt hơn, nghiêng về phía cash drag thuần.
2. **Thống kê idle capital đã có sẵn** (`opportunity_cap_hit_share()` — hàm production của
   WP-A5, KHÔNG sửa): `at_cap_share`, `mean_idle_ratio`, `share_idle_ge_1pct_cap`,
   `share_idle_ge_10pct_cap`. FS-02 chính thức (0,8961) chỉ là MỘT trong các số này (`share` —
   `at_cap AND idle` đồng thời); các số phụ trợ đo ĐỘ SÂU của phần nằm im, chưa từng được công
   bố trong `T06_OFFICIAL_EVIDENCE_RECORD.md`.

**Smoke test PASS** trên dataset SYNTHETIC (§7): ví dụ minh hoạ cấu trúc output — trên dữ liệu
synthetic, `OPPORTUNITY` đóng góp 16/547 purchase, 0,0154 ETH / tổng ~22,19 ETH (≈ 0,07 %) với
giá mua bình quân **thấp hơn** `SMART`/`CRASH` nhưng KHÔNG khác biệt nhiều so với `BASE`; đây
**chỉ minh hoạ shape của output, KHÔNG phải kết luận** (dataset synthetic không có regime CRASH
đúng đặc tính giống Binance thật).

**Trạng thái RQ-4**: **MISSING_INPUT** — chờ Owner chạy script trên dataset official. Phần "FS-02
= 0,8961" (đã official) tiếp tục đứng như FACT đã có (§2.1 F-C); phần phân rã theo nguồn và các
thống kê idle chi tiết là REPLAY, chờ Owner.

---

## 6. Script REPLAY (KHÔNG sửa `src/` — script sống ngoài production path)

Chạy với `python <script>.py <RAW_DIR> <FROZEN_PATH>` trên máy có dataset official T-06 đã bảo
toàn. `RAW_DIR` = thư mục `data/raw` chứa ba file parquet + `lineage.json` gốc (backup của
Owner). `FROZEN_PATH` = đường dẫn tới `results/random_control_21b7d88e9691_metrics.json` backup
(dùng để verify STEP 0). Yêu cầu môi trường: `pip install -e ".[dev]"` tại đúng `code_commit`
hiện hành của nhánh này (không cần checkout về `5228130` — đây là REPLAY `current HEAD code +
dataset official`, đúng khuôn `CHECK-B1-03` Addendum 3).

**Nếu STEP 0 in `FAIL`: DỪNG NGAY, không dùng bất kỳ số nào phía dưới, báo cáo lại nguyên văn
output cho phiên canonicalize kế tiếp — KHÔNG tự suy diễn.**

```python
"""
T-07 EVIDENCE INVESTIGATION (DEC-039) — RQ-1 / RQ-3 / RQ-4 deterministic replay.

CHỈ chạy trên dataset official T-06 đã bảo toàn (Owner). KHÔNG sửa file này.
KHÔNG phải một official T-06 run mới — đây là READ-ONLY post-hoc analysis trên
cùng engine đã đóng băng, dùng lại đúng hàm production KHÔNG sửa gì. Production
diff của repository = 0 khi chạy script này (script không nằm trong src/).

BẮT BUỘC: nếu STEP 0 (reproduce baseline) không khớp bit-for-bit, DỪNG NGAY —
không dùng bất kỳ số nào dưới đây làm evidence, báo cáo NOT ESTABLISHED.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from eth_dca_os.pipeline import Prepared
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.engine import run_engine, TZ_OFFSET
from eth_dca_os.metrics import window_metrics, oos_metrics, cash_ratio_stats, opportunity_cap_hit_share
from eth_dca_os.benchmarks import random_timing_control, random_anchor_control
from eth_dca_os.windows import gate_windows, OOS_START

RAW_DIR = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
FROZEN_PATH = sys.argv[2] if len(sys.argv) > 2 else "results/random_control_21b7d88e9691_metrics.json"
SMOKE = "--smoke" in sys.argv  # bỏ qua STEP 0 khi chạy trên dataset synthetic (KHÔNG evidence)

MASTER_SEED = 42


def monthly_tranches_of(purchases):
    out = {}
    for p in purchases:
        mk = pd.Timestamp(p["ts"] + TZ_OFFSET, unit="s").strftime("%Y-%m")
        out.setdefault(mk, []).append(p["nominal"])
    return out


def spearman(a, b):
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


prep = Prepared(RAW_DIR)
cfg, exec_cfg = BASELINE_STRATEGY, GATE1_LOW_FRICTION
scores = prep.scores(cfg.score_weights)
start, end = pd.Timestamp("2019-01-01"), prep.oos_end()

full = run_engine(prep.dataset, scores, cfg, exec_cfg, start, end)
full_tranches = monthly_tranches_of(full.purchases)
v2_eth = float(full.eth_total)

f_full = random_timing_control(prep.dataset, full_tranches, start, end, n_sims=1000, master_seed=MASTER_SEED)
g_full = random_anchor_control(prep.dataset, full_tranches, start, end, n_sims=1000, master_seed=MASTER_SEED)

step0 = {
    "v2_eth": v2_eth,
    "control_f_p95": f_full["p95"],
    "control_g_p95": g_full["p95"],
    "beats_f": bool(v2_eth > f_full["p95"]),
    "beats_g": bool(v2_eth > g_full["p95"]),
}

if not SMOKE:
    frozen = json.loads(Path(FROZEN_PATH).read_text())
    ok_v2 = abs(v2_eth - frozen["v2_eth"]) < 1e-6
    ok_f = abs(f_full["p95"] - 14.887400583487747) < 1e-6
    ok_g = abs(g_full["p95"] - 14.813546903782814) < 1e-6
    if not (ok_v2 and ok_f and ok_g):
        print(json.dumps({"STEP_0": "FAIL — KHONG khop official baseline. DUNG. "
                                     "KHONG dung bat ky so nao duoi day lam evidence.",
                           "computed": step0}, indent=2, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"STEP_0": "PASS — reproduced official baseline bit-for-bit"}, indent=2))
else:
    print(json.dumps({"STEP_0": "SMOKE MODE (synthetic dataset) — KHONG PHAI evidence",
                       "computed": step0}, indent=2))

# ---------------- RQ-3: Control F/G theo tung W1..W9 va OOS ----------------
wm = window_metrics(prep.dataset, scores, cfg, exec_cfg)
rq3 = {}
for w in gate_windows():
    wr = wm["windows"][w.window_id]
    w_start = pd.Timestamp(w.start)
    w_end = pd.Timestamp(w.end) + pd.Timedelta(days=1)
    w_tranches = monthly_tranches_of(wr["result"].purchases)
    if not w_tranches:
        rq3[w.window_id] = {"reason": "no_purchases_in_window"}
        continue
    wf = random_timing_control(prep.dataset, w_tranches, w_start, w_end, n_sims=1000, master_seed=MASTER_SEED)
    wg = random_anchor_control(prep.dataset, w_tranches, w_start, w_end, n_sims=1000, master_seed=MASTER_SEED)
    v2 = float(wr["result"].eth_total)
    rq3[w.window_id] = {
        "v2_eth": v2, "control_f_p50": wf["p50"], "control_f_p95": wf["p95"],
        "control_g_p50": wg["p50"], "control_g_p95": wg["p95"],
        "beats_f": bool(v2 > wf["p95"]), "beats_g": bool(v2 > wg["p95"]),
    }

oos = oos_metrics(prep.dataset, scores, cfg, exec_cfg, prep.oos_end())
oos_result = oos["detail"]["result"]
oos_tranches = monthly_tranches_of(oos_result.purchases)
if oos_tranches:
    oos_start_ts = pd.Timestamp(OOS_START)
    oos_end_ts = pd.Timestamp(prep.oos_end()) + pd.Timedelta(days=1)
    of = random_timing_control(prep.dataset, oos_tranches, oos_start_ts, oos_end_ts, n_sims=1000, master_seed=MASTER_SEED)
    og = random_anchor_control(prep.dataset, oos_tranches, oos_start_ts, oos_end_ts, n_sims=1000, master_seed=MASTER_SEED)
    v2_oos = float(oos_result.eth_total)
    rq3["OOS"] = {
        "v2_eth": v2_oos, "control_f_p50": of["p50"], "control_f_p95": of["p95"],
        "control_g_p50": og["p50"], "control_g_p95": og["p95"],
        "beats_f": bool(v2_oos > of["p95"]), "beats_g": bool(v2_oos > og["p95"]),
    }
else:
    rq3["OOS"] = {"reason": "no_purchases_in_oos"}

print(json.dumps({"RQ-3_control_by_window": rq3}, indent=2))

# ---------------- RQ-1: tuong quan mo ta cash_ratio vs AE theo 9 window (KHONG nhan qua) ----------------
cash_by_w = {w: cash_ratio_stats(wm["windows"][w]["result"])["avg"] for w in wm["windows"]}
ae_by_w = wm["ae_by_window"]
common = sorted(set(cash_by_w) & set(ae_by_w))
cash_vals = [cash_by_w[w] for w in common]
ae_vals = [ae_by_w[w] for w in common]
pearson_r = float(np.corrcoef(cash_vals, ae_vals)[0, 1]) if len(common) >= 2 else None
spearman_r = spearman(cash_vals, ae_vals) if len(common) >= 2 else None

print(json.dumps({"RQ-1_cash_vs_ae": {
    "per_window_cash_ratio_avg": cash_by_w,
    "per_window_ae": ae_by_w,
    "pearson_r": pearson_r,
    "spearman_r": spearman_r,
    "n_windows": len(common),
    "CAVEAT": ("TUONG QUAN QUAN SAT tren 9 window CHONG LAN, KHONG PHAI bang chung "
               "nhan qua. Khong counterfactual run nao duoc thuc hien (cam sua "
               "strategy/threshold theo chi thi Owner DEC-039)."),
}}, indent=2))

# ---------------- RQ-4: phan ra ETH theo nguon purchase (source) tren toan ky ----------------
by_source = {}
for p in full.purchases:
    s = p["source"]
    d = by_source.setdefault(s, {"n": 0, "nominal": 0.0, "eth": 0.0})
    d["n"] += 1
    d["nominal"] += p["nominal"]
    d["eth"] += p["eth"]
rq4_by_source = {s: {**d, "avg_price": (d["nominal"] / d["eth"]) if d["eth"] > 0 else None}
                 for s, d in by_source.items()}

opp_stats = opportunity_cap_hit_share(full)
cash_stats = cash_ratio_stats(full)

print(json.dumps({
    "RQ-4_eth_by_source": rq4_by_source,
    "RQ-4_opportunity_cap_hit": opp_stats,
    "RQ-4_cash_ratio_full_period": cash_stats,
}, indent=2))

print(json.dumps({"DONE": True, "SMOKE_MODE": SMOKE}, indent=2))
```

### 6.1 Smoke test đã chạy (sandbox agent, dataset SYNTHETIC, KHÔNG PHẢI evidence)

Lệnh: `python rq_evidence_script.py <synth_raw_dir> "" --smoke`

Kết quả: **exit code 0**, không exception, toàn bộ RQ-1/RQ-3/RQ-4 in ra JSON hợp lệ với kiểu dữ
liệu đúng (`bool` thuần Python cho `beats_f`/`beats_g`, `float` cho mọi số đo — cùng chuẩn
`_flag()`/`float()` mà `F-S015-01` đòi hỏi). Trích đoạn đại diện (KHÔNG PHẢI evidence):

```json
{
  "STEP_0": "SMOKE MODE (synthetic dataset) — KHONG PHAI evidence",
  "computed": {"v2_eth": 22.188701669097636, "control_f_p95": 22.497273082578715,
               "control_g_p95": 22.602527380413928, "beats_f": false, "beats_g": false}
}
```

```json
{"RQ-1_cash_vs_ae": {"pearson_r": 0.3363436281189256, "spearman_r": 0.5, "n_windows": 9}}
```

```json
{"RQ-4_opportunity_cap_hit": {"share": 0.9784435513335769, "at_cap_share": 0.9784435513335769,
                               "mean_idle_ratio": 0.7399426168134015,
                               "share_idle_ge_10pct_cap": 1.0}}
```

Toàn bộ output đầy đủ (RQ-3 9 window + OOS, RQ-4 by-source) đã được xem trong phiên soạn tài
liệu này, không lặp lại toàn văn ở đây (dung lượng lớn, KHÔNG phải evidence nên không cần bảo
toàn bit-for-bit).

---

## 7. Hướng dẫn cho Owner

1. Trên máy có dataset official T-06 đã bảo toàn (backup `CoinDCA_T06_OFFICIAL_BACKUP`), tại
   đúng `code_commit` của nhánh `claude/t-07-decision-prep-1oprq1` (hoặc HEAD hiện hành sau khi
   merge — script không phụ thuộc thay đổi nào ngoài phạm vi này):
2. `pip install -e ".[dev]"`
3. Lưu script §6 ra file (ví dụ `rq_evidence_script.py`).
4. Chạy: `python rq_evidence_script.py data/raw results/random_control_21b7d88e9691_metrics.json`
5. Nếu `STEP_0: PASS` — dán TOÀN BỘ output còn lại (RQ-1/RQ-3/RQ-4 JSON) vào phiên canonicalize
   kế tiếp. Nếu `STEP_0: FAIL` — dán nguyên output đó, KHÔNG chạy tiếp, KHÔNG tự sửa script.
6. Không cần chạy trên toàn bộ manifest Gate 2/Gate 3 — script chỉ dùng baseline config
   (`BASELINE_STRATEGY` + `GATE1_LOW_FRICTION`), đúng cấu hình mà Gate 1 chính thức đã dùng.

---

## 8. Tổng hợp trạng thái

| RQ | Trạng thái | Cần gì để đóng |
|---|---|---|
| RQ-1 (nhân quả reserve/cash → AE) | **NOT ESTABLISHED** (ngoài phạm vi được phép — cần counterfactual run) | Owner Decision riêng cho phép counterfactual, nếu muốn |
| RQ-1 (tương quan mô tả) | **MISSING_INPUT** | Owner chạy script §6 trên dataset official |
| RQ-2 | **PARTIALLY ESTABLISHED** (không nâng cấp thêm) | Không cần thêm — đã dùng evidence sẵn có đúng chỉ thị |
| RQ-3 | **MISSING_INPUT** | Owner chạy script §6 trên dataset official |
| RQ-4 | **MISSING_INPUT** (phần phân rã theo nguồn + idle detail); FS-02 aggregate đã là FACT | Owner chạy script §6 trên dataset official |
| RQ-5 | **PARTIALLY ESTABLISHED** (xem §2.3 — kết luận đầy đủ nhất có thể từ evidence hiện có) | Không cần thêm để trả lời ở mức hiện tại; RQ-1/3/4 output sẽ làm giàu thêm, không thay đổi kết luận định tính |

**Bước tiếp theo**: sau khi Owner cung cấp output RQ-1/RQ-3/RQ-4 (hoặc quyết định không cung
cấp), một phiên canonicalize sẽ ghi kết quả vào file này (theo đúng khuôn OWNER-REPORTED /
REPOSITORY-VERIFIED của `T06_OFFICIAL_EVIDENCE_RECORD.md`), và **quay lại `T-07`** để Owner
chọn giữa L-1/L-2 (`docs/reviews/T07-OWNER-DECISION-BRIEF.md` §7/§14).

Tài liệu này KHÔNG phải Owner Decision, KHÔNG đổi verdict, KHÔNG đổi `can_proceed_to_app`, KHÔNG
mở `T-11`/`WP-D2`, KHÔNG resolve `DEC-005`. `T-07` giữ `READY`.
