# ETH DCA Operating System V2.1.5 — Section Inventory

**COMPLETENESS REGISTER • KIỂM TRƯỚC MỖI LẦN PHÁT HÀNH**

## 1. Mục đích

Tài liệu này tồn tại vì một lý do cụ thể: ba version liên tiếp (V2.1.1, V2.1.2, V2.1.3) đều sửa đúng các lỗi được audit chỉ ra, và đều đánh rơi những mục KHÔNG được chỉ ra. Checklist theo audit findings luôn thất bại theo kiểu này vì nó chỉ nhớ vòng trước.

Đây là danh mục ĐẦY ĐỦ mọi mục bắt buộc. Trước khi đánh dấu bất kỳ version nào là ACTIVE, phải kiểm toàn bộ danh mục này theo thủ tục ở Implementation Plan §8.

## 2. 00 — Master Index

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| MI-1 | Mục đích và phạm vi | §1 |
| MI-2 | Precedence | §2 |
| MI-3 | Trạng thái tài liệu cũ | §3 |
| MI-4 | Changelog | §4 |
| MI-5 | Release integrity register | §5 |
| MI-6 | Versioning và freeze rule | §6 |

## 3. 01 — Product Spec

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| PR-1 | Product vision | §1 |
| PR-2 | Core flow | §2 |
| PR-3 | Currency model | §3 |
| PR-4 | Dual-unit UX | §4 |
| PR-5 | Treasury model | §5 |
| PR-6 | Execution states | §6 |
| PR-7 | Manual execution workflow | §7 |
| PR-8 | Partial fill | §8 |
| PR-9 | P2P transaction model | §9 |
| PR-10 | Funding policies | §10 |
| PR-11 | Dashboard hero | §11 |
| PR-12 | Capital / Treasury / P2P panels | §12 |
| PR-13 | Data quality display | §13 |
| PR-14 | Non-goals | §14 |

## 4. 02 — Strategy Spec

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| ST-1 | Opportunity Score và ba factor | §1 |
| ST-2 | Redundancy diagnostics: correlation, VIF, ablation | §2.1–2.3 |
| ST-3 | Volume structural-trend diagnostic | §2.4 |
| ST-4 | Data degradation rule (DEGRADED = 0, không rescale) | §3 |
| ST-5 | Monthly capital allocation và unlock | §4 |
| ST-6 | Opportunity hysteresis | §5 |
| ST-7 | Smart unlock modes HWM / NO_HWM / DECAY_HWM | §6 |
| ST-8 | Opportunity Fund cap và overflow | §7 |
| ST-9 | Capital accounting và partial fill | §8 |
| ST-10 | Base DCA schedule (kèm gap rule [F3]) | §9 |
| ST-11 | Month-End policy | §10 |
| ST-12 | ADR30 và continuous spacing (piecewise anchors) | §11 |
| ST-13 | Smart ladder | §12 |
| ST-14 | Opportunity ladder smoothing | §13 |
| ST-15 | Crash ladder (CrashSpacing, C0–C3, eligible-capital snapshot [F5]) | §14 |
| ST-16 | Execution limits | §15 |
| ST-17 | Multi-zone tie-break order [F2] — MỚI ở V2.1.5 | §15.1 |
| ST-18 | Market Regime và Execution State | §16 |
| ST-19 | Crash regime entry/exit/recovery | §17.1–17.2 |
| ST-20 | STRESSED label [F1] — MỚI ở V2.1.5 | §17.3 |
| ST-21 | Ladder lifecycle: immutability, invalidation, expiry | §18 |
| ST-22 | Status enums | §19 |
| ST-23 | Reason codes | §20 |
| ST-24 | Complete baseline strategy_config (kèm quy tắc ba-field-metadata [F7]) | §21 |

## 5. 03 — Backtest Spec

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| BT-1 | Core principle | §1 |
| BT-2 | Data and chronology | §2 |
| BT-3 | VND accounting trong backtest [F6] — MỚI ở V2.1.5 | §2.1 |
| BT-4 | Multi-anchor pre-OOS gate windows | §3 |
| BT-5 | Window coverage weighting và PrimaryMedian | §4 |
| BT-6 | Manual và funding delay model | §5 |
| BT-7 | Behavioral simulation (local hour) | §6 |
| BT-8 | Gate 1 | §7 |
| BT-9 | OOS hard condition và SHORT_OOS | §8 |
| BT-10 | Gate 2 grid, manifest, pass rule | §9 |
| BT-11 | Gate 3 grid, manifest, Net Edge, pass rule | §10 |
| BT-12 | Implementation shortfall measurement | §11 |
| BT-13 | Benchmarks và null controls (A–G, chu kỳ C [F4]) | §12 |
| BT-14 | Bootstrap, seeds và N | §13 |
| BT-15 | Walk-forward references | §14 |
| BT-16 | Regime labeling | §15 |
| BT-17 | Required metrics | §16 |
| BT-18 | Failure Signals và verdict cap | §17 |
| BT-19 | Data gaps | §18 |
| BT-20 | Processing order (18 bước) | §19 |
| BT-21 | Reproducibility | §20 |
| BT-22 | Test suite | §21 |
| BT-23 | Backtest philosophy | §22 |

## 6. 04 — Data Model

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| DM-1 | Entities | §1 |
| DM-2 | strategy_config | §2 |
| DM-3 | execution_config | §3 |
| DM-4 | market_snapshots | §4 |
| DM-5 | monthly_budgets | §5 |
| DM-6 | capital_ledger | §6 |
| DM-7 | p2p_transactions | §7 |
| DM-8 | crypto_trades | §8 |
| DM-9 | buy_ladders | §9 |
| DM-10 | buy_zones | §10 |
| DM-11 | decision_log | §11 |
| DM-12 | backtest_runs | §12 |
| DM-13 | Dataset lineage | §13 |
| DM-14 | Invariants | §14 |

## 7. 05 — Implementation Plan

| ID | Mục bắt buộc | V2.1.5 |
|---|---|---|
| IM-1 | Nguyên tắc | §1 |
| IM-2 | Phase 0 freeze | §2 |
| IM-3 | Các phase triển khai | §3 |
| IM-4 | Compute discipline | §4 |
| IM-5 | Verdict và stopping rules | §5 |
| IM-6 | Failure-signal override | §6 |
| IM-7 | Research prototype acceptance criteria | §7 |
| IM-8 | Release integrity procedure | §8 |
| IM-9 | App MVP gate | §9 |

## 8. Cross-document consistency checks

| ID | Kiểm tra |
|---|---|
| XC-1 | MỌI field trong baseline config ở Strategy §21 phải tồn tại trong schema strategy_config ở Data Model §2. Schema chỉ được phép có thêm đúng ba field metadata: config_name, created_at, strategy_config_hash. Bất kỳ field nào khác chênh lệch giữa hai bảng là lỗi phát hành. Trạng thái V2.1.5: 20 field baseline, 23 field schema, chênh đúng ba field metadata — ĐẠT. |
| XC-2 | Mọi chiều trong lưới Gate 2 (Backtest §9) đều có định nghĩa ngữ nghĩa trong Strategy Spec — đặc biệt smart_unlock_mode. |
| XC-3 | Mọi tham số ma sát trong Gate 3 (Backtest §10) đều có trong execution_config (Data Model §3). |
| XC-4 | Mọi giá trị enum dùng trong Data Model đều được định nghĩa trong Strategy §19. |
| XC-5 | Mọi Failure Signal ở Backtest §17 đều có metric tương ứng trong Backtest §16. |
| XC-6 | Mọi rule được test ở Backtest §21 đều có đặc tả tương ứng ở nơi khác trong pack. |
| XC-7 | Không tài liệu nào tham chiếu tới V1, V2.0, V2.1, V2.1.1, V2.1.2, V2.1.3 hoặc V2.1.4 như nguồn định nghĩa. |
| XC-8 | Mọi con số trong bảng đếm (19 / 18 / 200 / 219 / 14 / 100 / 114 / 9 window) đều được tính lại và khớp với thuật toán mô tả. |
| XC-9 | Mọi mục [F1]–[F7] trong changelog Master Index §4 đều có nội dung tương ứng tại đúng vị trí được trích dẫn, và không mục nào thay đổi công thức, ngưỡng gate, seed hay thuật toán manifest — MỚI ở V2.1.5. |

## 9. Deliberate removals

Mọi mục bị xóa khỏi một version phải được ghi ở đây kèm lý do. Trống nghĩa là không có mục nào bị xóa có chủ đích.

| Version | Mục bị xóa | Lý do |
|---|---|---|
| V2.1.5 | (không có) | V2.1.5 chỉ định nghĩa thêm và làm rõ, không xóa mục nào. |
