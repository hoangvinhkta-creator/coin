"""WP-C2 — Execution State: đặt tên, hợp nhất, lưu vết (đóng F-006).

Bám trực tiếp các REQUIRED check trong `docs/tasks/WP-C2-execution-state-machine.md`:

  CHECK-C2-02  sáu trạng thái được đặt tên và lưu vết theo phạm vi đã quyết
  CHECK-C2-03  `FUNDING_REQUIRED` được xử lý TƯỜNG MINH (`ADR-001`: NOT_APPLICABLE ở
               tầng backtest), không im lặng vắng mặt
  CHECK-C2-04  Market Regime và Execution State lưu RIÊNG, không gói nào định nghĩa lại
               chiều của gói kia
  CHECK-C2-05  `market_snapshots.execution_state` NOT NULL
  CHECK-C2-06  kết quả backtest KHÔNG ĐỔI (ở đây: fingerprint kịch bản chụp trên cây mã
               TRƯỚC WP-C2; ở quy mô thật: `tests/wp_c2_invariance_tool.py`)
  CHECK-C2-07  không tạo class `StateMachine` chỉ để khớp danh từ trong spec

Nguyên tắc của bộ test này: KHÔNG dựng trạng thái bằng tay. Mọi trạng thái được quan sát
qua `run_engine` thật trên kịch bản tất định (`tests/wp_c2_scenarios.py`), rồi đối chiếu
với NGUỒN SỰ THẬT ĐÃ CÓ (bản ghi purchase, tham số delay, cooldown_hours, cửa sổ dữ liệu
INVALID). Nhờ vậy test chứng minh chiều mới ĐẶT TÊN cho hành vi cũ chứ không tạo hành vi
mới — nếu nó là một hệ thống trạng thái song song thì các phép đối chiếu này sẽ lệch.
"""
from __future__ import annotations

import ast
import itertools
import json
import re
from collections import Counter
from pathlib import Path

import pytest

import eth_dca_os.engine as engine_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from eth_dca_os.engine import (
    BACKTEST_NOT_APPLICABLE_STATES,
    CANDLE,
    ExecutionState,
    derive_execution_state,
)
from wp_c2_scenarios import (
    SCENARIOS,
    fingerprint,
    run_scenario,
    run_scenario_with_grid,
    states_by_candle,
)

REPO = Path(__file__).resolve().parents[1]
H = 3600.0

#: Sáu giá trị theo ĐÚNG thứ tự Strategy §16/§19.
SPEC_STATES = ("WAIT", "FUNDING_REQUIRED", "READY_TO_BUY", "ACTION_PENDING",
               "COOLDOWN", "DATA_BLOCKED")

#: Enum Market Regime (ST §16) — dùng để chứng minh hai chiều KHÔNG lẫn vào nhau.
REGIME_LABELS = ("NORMAL", "STRESSED", "CRASH", "RECOVERY")

#: Fingerprint hành vi engine CHỤP TRÊN CÂY MÃ TRƯỚC WP-C2 (HEAD `2189a8f`, origin/main),
#: bằng `python tests/wp_c2_scenarios.py` chạy trước khi sửa `engine.py`. Chỉ tính trên
#: các trường `RunResult` đã tồn tại từ trước (`PRE_WP_C2_RESULT_FIELDS`), nên bất kỳ thay
#: đổi nào của vòng đời zone, thời điểm cooldown hay hành vi chặn dữ liệu xấu đều làm đỏ.
FROZEN_PRE_WP_C2_FINGERPRINTS = {
    "wait_only": "11cf0472f22be452ba138c8a16d6e87f81a14d26e500d8365a4d7c3fbdb6ebee",
    "smart_action_cycle": "cc39918c8c2267ed4ace29b693e6a2940b71e8e640130b42d521322f2fdfb937",
    "data_invalid_window": "add58cf1285e14f9db8692a43fdcca3fc3fbd111171e987d745d5ebf9849ccfd",
    "crash_regime_cycle": "4baf1cfdebc054325aabe1387bc349177f0ccb266d6482e89e5a9f1c1f360990",
}

_RUN_CACHE: dict[str, tuple] = {}


def scenario(name: str):
    """Chạy (và cache) một kịch bản: `(result, candle_grid, start_ts)`."""
    if name not in _RUN_CACHE:
        res, grid, start = run_scenario_with_grid(name)
        _RUN_CACHE[name] = (res, grid, start.timestamp())
    return _RUN_CACHE[name]


def per_candle(name: str) -> list[tuple[float, str]]:
    res, grid, _ = scenario(name)
    return states_by_candle(res, grid)


def counts(name: str) -> Counter:
    return Counter(s for _, s in per_candle(name))


def zone_fill_ts(res) -> list[float]:
    """Timestamp của các lần FILL ZONE thật (không tính Base/Month-End settle)."""
    return sorted(float(p["ts"]) for p in res.purchases if "_ZONE_" in p["reason"])


# ------------------------------------------------------ CHECK-C2-02 / L — vốn từ vựng

def test_c2_02_vocabulary_is_exactly_the_six_spec_states():
    """Enum trùng KHỚP TỪNG GIÁ TRỊ với Strategy §19 — không thừa, không thiếu, không thứ bảy."""
    assert tuple(s.value for s in ExecutionState) == SPEC_STATES

    spec = (REPO / "docs/spec/02_STRATEGY_SPEC_V2_1_5.md").read_text()
    rows = re.findall(r"^\|\s*Execution [Ss]tate\s*\|([^|]+)\|", spec, re.MULTILINE)
    assert rows, "không tìm thấy dòng Execution State trong Strategy Spec"
    for row in rows:
        assert tuple(v.strip() for v in row.split("/")) == SPEC_STATES


def test_c2_02_no_seventh_state_can_be_produced_by_the_derivation():
    """Duyệt VÉT CẠN không gian đầu vào: không tổ hợp nào sinh ra giá trị ngoài enum."""
    for flags in itertools.product((False, True), repeat=4):
        out = derive_execution_state(
            action_due=flags[0], action_open=flags[1],
            data_invalid=flags[2], cooldown_blocking=flags[3])
        assert isinstance(out, ExecutionState)
        assert out.value in SPEC_STATES


def test_c2_02_derivation_precedence_table_is_frozen():
    """Bảng quyết định đầy đủ (16 tổ hợp) — đóng băng quy ước `docs/CONVENTIONS.md` #22."""
    E = ExecutionState
    expected = {
        # (action_due, action_open, data_invalid, cooldown_blocking) -> state
        (True, True, True, True): E.READY_TO_BUY,
        (True, True, True, False): E.READY_TO_BUY,
        (True, True, False, True): E.READY_TO_BUY,
        (True, True, False, False): E.READY_TO_BUY,
        (True, False, True, True): E.READY_TO_BUY,
        (True, False, True, False): E.READY_TO_BUY,
        (True, False, False, True): E.READY_TO_BUY,
        (True, False, False, False): E.READY_TO_BUY,
        (False, True, True, True): E.ACTION_PENDING,
        (False, True, True, False): E.ACTION_PENDING,
        (False, True, False, True): E.ACTION_PENDING,
        (False, True, False, False): E.ACTION_PENDING,
        (False, False, True, True): E.DATA_BLOCKED,
        (False, False, True, False): E.DATA_BLOCKED,
        (False, False, False, True): E.COOLDOWN,
        (False, False, False, False): E.WAIT,
    }
    for flags, want in expected.items():
        got = derive_execution_state(
            action_due=flags[0], action_open=flags[1],
            data_invalid=flags[2], cooldown_blocking=flags[3])
        assert got is want, f"{flags} -> {got}, mong đợi {want}"


# ------------------------------------------------------ CHECK-C2-02 — năm đường chạy thật

def test_c2_02_wait_path_is_the_state_when_nothing_is_actionable():
    """A — không ladder, không action, không cooldown, dữ liệu GOOD: MỌI nến là WAIT."""
    res, grid, _ = scenario("wait_only")
    assert counts("wait_only") == Counter({"WAIT": len(grid)})
    assert res.execution_state_timeline == [(grid[0], ExecutionState.WAIT)]
    assert zone_fill_ts(res) == []


def test_c2_02_ready_to_buy_coincides_exactly_with_zone_fills():
    """B — `READY_TO_BUY` đúng bằng tập nến có fill zone THẬT, ở cả bốn kịch bản.

    Đây là phép thử "đặt tên chứ không tạo mới": bước 12 xác định action tới hạn và bước
    16–17 fill NGAY trong nến đó, nên hai tập phải trùng khớp tuyệt đối. Lệch một nến
    nghĩa là chiều mới đã trở thành một nguồn sự thật thứ hai.
    """
    for name in SCENARIOS:
        res, _, _ = scenario(name)
        ready = sorted(ts for ts, s in per_candle(name) if s == "READY_TO_BUY")
        assert ready == zone_fill_ts(res), name


def test_c2_02_action_pending_spans_exactly_the_configured_delay():
    """C — số nến `ACTION_PENDING` = ĐÚNG total_delay của execution_config, không hơn.

    `gate3_realistic`: user_delay 4h + funding_delay 1h = 5h = 20 nến.
    `gate1_low_friction`: 15 phút = 1 nến.
    """
    for name, exec_cfg in (("smart_action_cycle", GATE3_REALISTIC),
                           ("data_invalid_window", GATE1_LOW_FRICTION),
                           ("crash_regime_cycle", GATE1_LOW_FRICTION)):
        res, _, _ = scenario(name)
        fills = zone_fill_ts(res)
        assert fills, f"{name}: kịch bản phải có ít nhất một fill zone"
        delay = exec_cfg.user_delay_seconds + (
            0 if exec_cfg.funding_policy == "BULK_MONTHLY" else exec_cfg.funding_delay_seconds)
        assert counts(name)["ACTION_PENDING"] == len(fills) * int(delay / CANDLE), name


def test_c2_02_cooldown_covers_exactly_the_window_after_a_zone_fill():
    """D — `COOLDOWN` phủ đúng cửa sổ `cooldown_hours` sau fill, trừ chính nến fill."""
    name = "smart_action_cycle"
    res, _, _ = scenario(name)
    fill = zone_fill_ts(res)[0]
    cd = sorted(ts for ts, s in per_candle(name) if s == "COOLDOWN")
    window = BASELINE_STRATEGY.cooldown_hours * H
    assert cd[0] == fill + CANDLE                      # nến fill = READY_TO_BUY, không COOLDOWN
    assert cd[-1] == fill + window - CANDLE
    assert len(cd) == int(window / CANDLE) - 1
    assert all(fill < ts < fill + window for ts in cd)


def test_c2_02_data_blocked_covers_exactly_the_invalid_daily_window():
    """E — `DATA_BLOCKED` phủ đúng cửa sổ hai ngày daily INVALID (hiệu lực từ 07:00 local)."""
    name = "data_invalid_window"
    db = sorted(ts for ts, s in per_candle(name) if s == "DATA_BLOCKED")
    _, _, start = scenario(name)
    # Hàng daily của local Day k có hiệu lực từ 07:00 local Day k tới 07:00 local Day k+1.
    first = start + 2 * 86400.0 + 7 * H                # 07:00 local Day 3
    last_exclusive = start + 4 * 86400.0 + 7 * H       # 07:00 local Day 5
    assert db, "kịch bản phải quan sát được DATA_BLOCKED"
    assert db[0] == first and db[-1] == last_exclusive - CANDLE
    assert len(db) == int((last_exclusive - first) / CANDLE)


def test_c2_02_every_in_scope_state_is_reached_through_the_real_engine():
    """Năm trạng thái thuộc phạm vi `ADR-001` đều quan sát được từ `run_engine` thật."""
    seen = set()
    for name in SCENARIOS:
        res, _, _ = scenario(name)
        seen |= {str(s) for _, s in res.execution_state_timeline}
    assert seen == {"WAIT", "READY_TO_BUY", "ACTION_PENDING", "COOLDOWN", "DATA_BLOCKED"}


# ------------------------------------------------------ CHECK-C2-03 — FUNDING_REQUIRED

def test_c2_03_funding_required_is_declared_not_applicable_at_backtest_layer():
    """Trạng thái TỒN TẠI trong vốn từ vựng (Product Spec §6/§11 vẫn đòi nó ở tầng app)
    nhưng được TUYÊN BỐ NOT_APPLICABLE ở tầng backtest — không phải vắng mặt im lặng."""
    assert ExecutionState.FUNDING_REQUIRED in ExecutionState
    assert BACKTEST_NOT_APPLICABLE_STATES == (ExecutionState.FUNDING_REQUIRED,)


def test_c2_03_funding_required_is_unreachable_by_construction():
    """Không tổ hợp đầu vào nào của hàm dẫn xuất sinh ra `FUNDING_REQUIRED` (vét cạn)."""
    for flags in itertools.product((False, True), repeat=4):
        assert derive_execution_state(
            action_due=flags[0], action_open=flags[1],
            data_invalid=flags[2], cooldown_blocking=flags[3]) is not \
            ExecutionState.FUNDING_REQUIRED


def test_c2_03_funding_required_never_emitted_by_any_real_run():
    """F — không đường chạy tình cờ nào phát ra nó, ở timeline lẫn ở snapshot."""
    for name in SCENARIOS:
        res, _, _ = scenario(name)
        assert "FUNDING_REQUIRED" not in {str(s) for _, s in res.execution_state_timeline}
        assert "FUNDING_REQUIRED" not in {str(m["execution_state"])
                                          for m in res.market_snapshots}


def _identifiers(path: Path) -> set[str]:
    """Mọi định danh THẬT của một module (bỏ qua comment và docstring)."""
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
    return names


def test_c2_03_engine_never_models_a_usdt_treasury_balance():
    """`ADR-001`: engine KHÔNG mô hình hoá số dư treasury USDT.

    Chốt bằng cấu trúc trên ĐỊNH DANH THẬT (không tính comment): không biến/thuộc tính
    nào mang khái niệm treasury, và `funding_delay` chỉ là hàm của `funding_policy`
    (`docs/CONVENTIONS.md` #8) — nên không tồn tại nhánh "treasury có đủ không" để
    `FUNDING_REQUIRED` phát sinh.
    """
    for module in ("engine.py", "execution.py"):
        idents = _identifiers(REPO / "src/eth_dca_os" / module)
        assert not [n for n in idents if "treasury" in n.lower()], module
    assert 'funding_policy == "BULK_MONTHLY"' in (
        REPO / "src/eth_dca_os/engine.py").read_text()


# ------------------------------------------------------ CHECK-C2-04 — hai chiều tách biệt

def test_c2_04_regime_and_execution_state_are_stored_as_separate_fields():
    """G — hai chiều nằm ở hai trường riêng của cùng bản ghi và biến thiên độc lập."""
    res, _, _ = scenario("crash_regime_cycle")
    regimes = {m["market_regime"] for m in res.market_snapshots}
    states = {str(m["execution_state"]) for m in res.market_snapshots}
    assert len(regimes) >= 3 and regimes <= set(REGIME_LABELS)
    assert len(states) >= 2 and states <= set(SPEC_STATES)
    for m in res.market_snapshots:
        assert set(m) >= {"market_regime", "execution_state"}


def test_c2_04_no_execution_state_value_encodes_a_regime():
    """Cấm thiết kế kiểu `CRASH_READY_TO_BUY`: không giá trị nào mang token regime."""
    for s in ExecutionState:
        for label in REGIME_LABELS:
            assert label not in s.value


def test_c2_04_regime_module_is_untouched_by_the_execution_state_dimension():
    """WP-C2 không định nghĩa lại chiều của WP-A3: `regime.py` không biết gì về enum này."""
    src = (REPO / "src/eth_dca_os/regime.py").read_text()
    assert "ExecutionState" not in src and "execution_state" not in src


# ------------------------------------------------------ CHECK-C2-05 — market_snapshots

REQUIRED_SNAPSHOT_FIELDS = (
    "ts", "accounting_date_local", "eth_price", "opportunity_score_raw",
    "smart_unlock", "opportunity_unlock", "smart_unlock_peak",
    "opportunity_fund_balance_vnd", "opportunity_fund_available_vnd",
    "opportunity_fund_reserved_vnd", "market_regime", "execution_state", "data_quality",
)


def test_c2_05_execution_state_is_never_null_in_any_snapshot():
    """H — DM §4: nhóm `state` LUÔN NOT NULL. Không bản ghi nào để trống."""
    total = 0
    for name in SCENARIOS:
        res, _, _ = scenario(name)
        assert res.market_snapshots, name
        for m in res.market_snapshots:
            total += 1
            assert set(m) == set(REQUIRED_SNAPSHOT_FIELDS)
            assert m["execution_state"] is not None
            assert isinstance(m["execution_state"], ExecutionState)
            assert m["market_regime"] in REGIME_LABELS
            assert m["data_quality"] in ("GOOD", "DEGRADED", "INVALID")
    assert total > 0, "vacuous: không snapshot nào được kiểm"


def test_c2_05_one_snapshot_per_accounting_day():
    """Nhịp lưu = một bản ghi mỗi accounting day, cùng nhịp `cash_samples` sẵn có."""
    for name in SCENARIOS:
        res, _, _ = scenario(name)
        dates = [m["accounting_date_local"] for m in res.market_snapshots]
        assert len(dates) == len(set(dates)) == len(res.cash_samples), name
        assert [m["ts"] for m in res.market_snapshots] == [c[0] for c in res.cash_samples]


def test_c2_05_snapshot_execution_state_serialises_as_a_plain_string():
    """Trường phải ghi được ra JSON như một chuỗi thuần — không rò rỉ `repr` của enum."""
    res, _, _ = scenario("data_invalid_window")
    dumped = json.loads(json.dumps(
        [{"execution_state": m["execution_state"]} for m in res.market_snapshots]))
    assert {d["execution_state"] for d in dumped} <= set(SPEC_STATES)


# ------------------------------------------------------ CHECK-C2-06 — hành vi không đổi

@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_c2_06_engine_behaviour_is_bit_identical_to_pre_wp_c2(name):
    """I + J + K — vòng đời zone, thời điểm cooldown và hành vi chặn dữ liệu xấu KHÔNG đổi.

    Fingerprint được chụp trên cây mã TRƯỚC WP-C2 (`origin/main` `2189a8f`) và đóng băng ở
    đây, nên đây là phép so TRƯỚC–SAU thật, không phải một khẳng định tự quy chiếu.
    """
    assert fingerprint(run_scenario(name)) == FROZEN_PRE_WP_C2_FINGERPRINTS[name]


def test_c2_06_frozen_fingerprints_cover_every_scenario():
    """Chống PASS rỗng: mỗi kịch bản phải có đúng một fingerprint đóng băng."""
    assert set(FROZEN_PRE_WP_C2_FINGERPRINTS) == set(SCENARIOS)


# ------------------------------------------------------ CHECK-C2-07 — không dựng kiến trúc

def test_c2_07_no_state_machine_class_was_created():
    """RCP-001: không tạo class `StateMachine` chỉ để khớp danh từ trong spec.

    Thiết kế thực tế: MỘT enum (vốn từ vựng) + MỘT hàm thuần (hợp nhất dữ kiện đã có).
    Không class, không đối tượng có vòng đời, không bảng chuyển trạng thái.
    """
    for path in sorted((REPO / "src/eth_dca_os").rglob("*.py")):
        for cls in re.findall(r"^class\s+(\w+)", path.read_text(), re.MULTILINE):
            assert "StateMachine" not in cls, f"{path}: {cls}"
    assert callable(derive_execution_state)
    assert not isinstance(derive_execution_state, type)
    # Enum chỉ mang giá trị; không phương thức tự viết nào (không phải nơi giữ hành vi).
    own = {n for n in vars(ExecutionState)
           if not n.startswith("_") and n not in ExecutionState.__members__}
    assert own == set()


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_c2_07_forcing_a_wrong_execution_state_changes_no_behaviour(name, monkeypatch):
    """Bằng chứng HÀNH VI cho "chiều dẫn xuất, không phải nguồn sự thật thứ hai".

    Ép hàm dẫn xuất luôn trả một trạng thái SAI: nếu có bất kỳ nhánh execution nào đọc
    Execution State — dù chỉ một — thì kết quả engine phải đổi. Fingerprint vẫn trùng
    khớp cây mã trước WP-C2 nghĩa là không nhánh nào đọc nó. Đây là phép thử mạnh hơn mọi
    phép soi văn bản: nó không phụ thuộc vào cách viết mã.
    """
    monkeypatch.setattr(engine_mod, "derive_execution_state",
                        lambda **kw: ExecutionState.COOLDOWN)
    res = run_scenario(name)
    assert fingerprint(res) == FROZEN_PRE_WP_C2_FINGERPRINTS[name]
    # ...và bản thân phép ép đã thực sự có hiệu lực (chống PASS rỗng).
    assert {str(s) for _, s in res.execution_state_timeline} == {"COOLDOWN"}


def test_c2_07_execution_state_adds_no_engine_state_variable():
    """Chiều mới là DẪN XUẤT: engine không giữ thêm biến trạng thái nào cho nó.

    `derive_execution_state` là hàm thuần — gọi lại với cùng đầu vào luôn cho cùng kết quả
    và không có tác dụng phụ nào để quan sát.
    """
    args = dict(action_due=False, action_open=True, data_invalid=True, cooldown_blocking=True)
    first = derive_execution_state(**args)
    assert all(derive_execution_state(**args) is first for _ in range(5))


# ------------------------------------------------------ hợp đồng downstream WP-B3

def test_c2_downstream_contract_is_consumable_without_a_second_enum():
    """WP-B3 tiêu thụ `previous_state`/`new_state` (DM §11) từ ĐÚNG enum này."""
    from eth_dca_os.engine import ExecutionState as Imported
    assert Imported is ExecutionState
    prev, new = ExecutionState.ACTION_PENDING, ExecutionState.READY_TO_BUY
    record = json.loads(json.dumps({"previous_state": prev, "new_state": new}))
    assert record == {"previous_state": "ACTION_PENDING", "new_state": "READY_TO_BUY"}
    assert ExecutionState(record["new_state"]) is ExecutionState.READY_TO_BUY


def test_c2_timeline_is_a_lossless_transition_log():
    """`execution_state_timeline` ghi-khi-đổi nhưng đọc lại được trạng thái TỪNG nến.

    Bất biến: hai mốc liên tiếp không bao giờ cùng giá trị, mốc đầu nằm ở nến đầu, và số
    lần đổi dựng lại từ chuỗi từng-nến khớp đúng độ dài timeline.
    """
    for name in SCENARIOS:
        res, grid, _ = scenario(name)
        tl = res.execution_state_timeline
        assert tl and tl[0][0] == grid[0], name
        assert all(a[1] != b[1] for a, b in zip(tl, tl[1:])), name
        assert [t for t, _ in tl] == sorted(t for t, _ in tl), name
        seq = [s for _, s in states_by_candle(res, grid)]
        changes = 1 + sum(1 for a, b in zip(seq, seq[1:]) if a != b)
        assert changes == len(tl), name


def test_c2_engine_module_exports_the_vocabulary():
    """Vốn từ vựng nằm ở một chỗ duy nhất và import được ổn định."""
    assert engine_mod.ExecutionState is ExecutionState
    assert engine_mod.derive_execution_state is derive_execution_state
    assert engine_mod.BACKTEST_NOT_APPLICABLE_STATES == BACKTEST_NOT_APPLICABLE_STATES
