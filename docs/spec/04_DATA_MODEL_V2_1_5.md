# ETH DCA Operating System V2.1.5 — Data Model

**COMPLETE LEDGER / ZONE / CONFIG / RUN SCHEMA • LIVE-BACKTEST FEEDBACK LOOP**

## 1. Entities

| Entity | Purpose |
|---|---|
| market_candles / raw parquet | Nguồn OHLCV và dataset lineage. |
| market_snapshots | Indicator, factor, score, unlock, regime/state và capital snapshot. |
| strategy_config | Tham số CHIẾN LƯỢC; biến thiên ở Gate 2. |
| execution_config | Tham số MA SÁT và hành vi thực thi; biến thiên ở Gate 3. |
| monthly_budgets | Phân bổ VND theo tháng và vòng đời tháng. |
| capital_ledger | Nguồn có thẩm quyền cho mọi dịch chuyển và reservation vốn. |
| p2p_transactions | Giao dịch VND <-> USDT thực tế. |
| crypto_trades | Giao dịch USDT <-> ETH thực tế/mô phỏng và các trường implementation shortfall. |
| buy_ladders | Header và vòng đời ladder. |
| buy_zones | Reservation, trigger và fill state của từng zone. |
| decision_log | Audit trail của state và action. |
| backtest_runs | Metadata tái lập và verdict. |

## 2. strategy_config

**[F7]** Schema này chứa mọi field của bảng baseline ở Strategy §21, cộng thêm đúng BA field metadata: `config_name`, `created_at`, `strategy_config_hash`. Không field nào khác được phép chênh lệch giữa hai bảng (Section Inventory XC-1).

| Field | Required |
|---|---|
| strategy_version | Yes |
| config_name | Yes (metadata) |
| base_pct | Yes |
| smart_pct | Yes |
| opportunity_pct | Yes |
| opportunity_cap_months | Yes |
| smart_unlock_mode | Yes |
| hwm_decay_step | Yes |
| hwm_decay_days | Yes |
| opportunity_activate_score | Yes |
| opportunity_suspend_score | Yes |
| smart_spacing_factor | Yes |
| smart_spacing_min | Yes |
| smart_spacing_max | Yes |
| opportunity_spacing_multiplier | Yes |
| opportunity_daily_limit_pct | Yes |
| max_zones_per_cycle | Yes |
| cooldown_hours | Yes |
| cooldown_override_pct | Yes |
| suspended_zone_hold_days | Yes |
| accounting_timezone | Yes |
| created_at | Yes (metadata) |
| strategy_config_hash | Yes (metadata) |

## 3. execution_config

| Field | Required |
|---|---|
| execution_version | Yes |
| user_delay_seconds | Yes |
| funding_policy | Yes |
| funding_delay_seconds | Yes |
| spot_fee_rate | Yes |
| slippage_bps | Yes |
| action_ttl_seconds | Yes |
| behavioral_model | Yes (OFF / LOCAL_HOUR) |
| p2p_unavailable_in_crash | Yes (true/false) |
| created_at | Yes |
| execution_config_hash | Yes |

Tách strategy_config và execution_config là bắt buộc vì Gate 2 chỉ biến thiên nhóm thứ nhất và Gate 3 chỉ biến thiên nhóm thứ hai. Mỗi decision và mỗi run phải tham chiếu cả hai hash.

## 4. market_snapshots

| Nhóm trường | Trường | Nullability |
|---|---|---|
| identity | timestamp_utc, accounting_date_local, strategy_version, strategy_config_hash | LUÔN NOT NULL |
| market | eth_price, btc_price | Bắt buộc trừ khi snapshot ở trạng thái DATA_BLOCKED |
| price location | dd365, d_norm, ma200, ma_ratio, m_norm, percentile365, p_norm, price_location_score | Nullable chỉ khi data_quality = DEGRADED hoặc INVALID |
| market stress | rsi14, r_norm, return7, s7_norm, volume_ratio, v_norm, market_stress_score | Nullable chỉ khi DEGRADED / INVALID |
| relative value | ethbtc, ethbtc_return30, w_norm, ethbtc_percentile180, rp_norm, relative_value_score | Nullable chỉ khi DEGRADED / INVALID |
| score | opportunity_score_raw | Nullable chỉ khi INVALID |
| capital | smart_unlock, opportunity_unlock, smart_unlock_peak, opportunity_fund_balance_vnd, opportunity_fund_available_vnd, opportunity_fund_reserved_vnd | Bắt buộc |
| state | market_regime, execution_state, data_quality | LUÔN NOT NULL |

## 5. monthly_budgets

| Field | Rule |
|---|---|
| month_local | YYYY-MM theo Asia/Ho_Chi_Minh |
| contribution_vnd | Bắt buộc; source of truth |
| base_budget_vnd / smart_budget_vnd / opportunity_contribution_vnd | Bắt buộc |
| base_available_vnd / base_reserved_vnd / base_deployed_vnd | Bắt buộc |
| smart_available_vnd / smart_reserved_vnd / smart_deployed_vnd | Bắt buộc |
| opportunity_added_vnd / opportunity_overflow_to_smart_vnd | Bắt buộc |
| smart_unlock_mode_applied | Bản sao audit của mode thực sự được áp dụng trong tháng |
| smart_unlock_peak | Nullable tùy mode |
| status | OPEN / CLOSED |
| opened_at / closed_at | Bắt buộc / nullable |

## 6. capital_ledger

Quỹ phải được quản lý bằng ledger, không phải một balance mutable.

| Field | Rule |
|---|---|
| ledger_id | PK |
| timestamp_utc / accounting_timestamp_local | Bắt buộc / derived |
| pool | BASE / SMART / OPPORTUNITY / TREASURY |
| asset | VND / USDT / ETH |
| entry_type | CONTRIBUTION / RESERVE / RELEASE / DEPLOY / P2P_BUY / P2P_SELL / ETH_BUY / ETH_SELL / FEE / ROLLOVER / OVERFLOW / ADJUSTMENT |
| amount_asset | Có dấu |
| economic_value_vnd | Bắt buộc khi có ý nghĩa |
| related_zone_id / related_trade_id / related_p2p_id | Nullable |
| available_after / reserved_after / deployed_after | Audit |
| reason_code | Bắt buộc, theo Strategy §20 |

## 7. p2p_transactions

| Field | Rule |
|---|---|
| p2p_id | PK |
| direction | VND_TO_USDT / USDT_TO_VND |
| vnd_amount / usdt_amount | Thực tế |
| fee_vnd | Thực tế, mặc định 0 |
| effective_rate | Derived |
| started_at / completed_at | Bắt buộc — dùng đo funding delay thực tế |
| platform | Tùy chọn |
| related_action_id | Nullable |

## 8. crypto_trades

Đây là bảng khép kín vòng phản hồi giữa live và backtest: nó cho phép đo implementation shortfall THỰC TẾ và đối chiếu ngược với giả định delay của backtest.

| Field | Rule |
|---|---|
| trade_id | PK |
| direction | USDT_TO_ETH / ETH_TO_USDT |
| source | BASE / SMART / OPPORTUNITY / CRASH / MANUAL |
| recommended_price | Bắt buộc với action do hệ thống tạo |
| triggered_at | Bắt buộc với zone action |
| action_created_at | Bắt buộc |
| funding_started_at / ready_to_buy_at | Nullable |
| executed_at | Thực tế |
| actual_price_usdt | Thực tế |
| usdt_amount / eth_amount | Thực tế |
| fee_asset / fee_amount | Thực tế |
| transferred_vnd_cost_basis | Bắt buộc với lệnh mua |
| fx_rate_vnd_per_usdt | Bắt buộc với lệnh mua; tỷ giá dùng để quy đổi cost basis |
| zone_id / ladder_id | Nullable |
| opportunity_score_at_trigger | Bắt buộc với action hệ thống |
| market_regime / execution_state | Snapshot tại thời điểm thực thi |
| user_delay_seconds / funding_delay_seconds | Derived |
| implementation_shortfall_bps | Derived: (actual_price / recommended_price - 1) x 10000 với lệnh mua |
| strategy_version / strategy_config_hash | Bắt buộc |

## 9. buy_ladders

| Field | Rule |
|---|---|
| ladder_id | PK |
| type | SMART / OPPORTUNITY / CRASH |
| created_at / expires_at | Bắt buộc |
| anchor_price | BẤT BIẾN |
| spacing_pct | BẤT BIẾN |
| score_at_creation | Bắt buộc |
| eligible_capital_vnd / reserved_capital_vnd | Bắt buộc. Với CRASH ladder, eligible_capital_vnd là snapshot theo Strategy §14 [F5], bất biến trong đời ladder. |
| invalidation_price | Derived: Anchor x (1 + MAX(12%, 2 x spacing)) |
| status | ACTIVE / SUSPENDED / COMPLETED / INVALIDATED / EXPIRED / CANCELLED |
| strategy_version | Bắt buộc |

## 10. buy_zones

| Field | Rule |
|---|---|
| zone_id / ladder_id | PK / FK |
| zone_index | 0..n |
| target_price_usdt | Bắt buộc |
| allocation_pct | Bắt buộc |
| target_vnd | SOURCE OF TRUTH cho phân bổ |
| reserved_vnd / filled_vnd / remaining_vnd | Bắt buộc / mặc định 0 / derived |
| status | ACTIVE / SUSPENDED / TRIGGERED / ACTION_PENDING / PARTIALLY_FILLED / EXECUTED / CANCELLED / EXPIRED / MISSED |
| triggered_at / action_expires_at / executed_at | Nullable |
| actual_trade_id | Nullable |

## 11. decision_log

| Field | Rule |
|---|---|
| decision_id | PK |
| timestamp_utc | Bắt buộc |
| previous_state / new_state | Execution State enum |
| market_regime / data_quality | Bắt buộc |
| trigger_type | zone / base / regime / funding / cooldown / month_end / data |
| reason_code | Bắt buộc, theo Strategy §20 |
| opportunity_score | Raw |
| recommended_price / recommended_vnd / recommended_usdt_est | Nullable |
| zone_id / ladder_id | Nullable |
| available_vnd / reserved_vnd / deployed_vnd | Snapshot bắt buộc |
| strategy_config_hash / execution_config_hash | Bắt buộc |

## 12. backtest_runs

| Field | Rule |
|---|---|
| run_id | PK |
| strategy_version / backtest_spec_version | Bắt buộc |
| strategy_config_hash / execution_config_hash | Bắt buộc |
| sensitivity_manifest_hash | Nullable tùy run_type |
| dataset_hash | Bắt buộc |
| start_date / end_date | Bắt buộc |
| master_seed / simulation_seed | Bắt buộc / nullable |
| code_commit | Tùy chọn |
| run_type | BASELINE / GATE1 / GATE2 / GATE3 / RANDOM_CONTROL / BOOTSTRAP / ABLATION / STRESS |
| metrics_path | Bắt buộc |
| verdict | BUILD / BUILD_WITH_MODIFICATIONS / INCONCLUSIVE / DO_NOT_BUILD / NULL cho tới khi đánh giá |
| created_at | Bắt buộc |

## 13. Dataset lineage

Raw OHLCV có thể giữ ở parquet bất biến thay vì lưu thành hàng trong database. Tối thiểu phải lưu: symbol, interval, source, first_timestamp, last_timestamp, row_count, missing_count, file hash và dataset_hash mà backtest_runs tham chiếu.

## 14. Invariants

- TOTAL = AVAILABLE + RESERVED + DEPLOYED, trong dung sai số học.
- Không số dư âm ở bất kỳ pool nào.
- requested_reserve <= AVAILABLE tại mọi thời điểm.
- Không double reservation giữa Smart, Opportunity và Crash.
- VND allocation là source of truth cho ngân sách; lượng USDT/ETH thực tế có thể thay đổi theo tỷ giá P2P, nhưng zone vẫn được coi là hoàn thành theo phân bổ VND.
- Partial fill: phần chưa fill vẫn RESERVED cho tới hết TTL, sau đó RELEASE.
- Action bị MISSED, EXPIRED hoặc CANCELLED phải release toàn bộ reserve còn lại.
- Portfolio chỉ thay đổi sau sự kiện thực thi đã được xác nhận (live) hoặc đã được mô phỏng thực thi (backtest).
- strategy_config và execution_config snapshot là bất biến; mọi decision và run phải tham chiếu hash của chúng.
- Transaction conservation phải có unit test.
