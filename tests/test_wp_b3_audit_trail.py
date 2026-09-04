"""WP-B3 — audit trail / decision_log (Data Model §11, Strategy §9/§20). Đóng F-024, F-033.

Ánh xạ tới Completion Gate ĐÃ ĐÓNG BĂNG của `docs/tasks/WP-B3-audit-trail-decision-log.md`:

  CHECK-B3-01  `decision_log` đủ trường theo DM §11 (đối chiếu THẲNG với văn bản spec)
  CHECK-B3-02  `previous_state`/`new_state` dùng ĐÚNG enum `ExecutionState` của WP-C2
  CHECK-B3-03  phạm vi loại sự kiện phủ danh mục reason code ST §20; mục không ghi có lý do
  CHECK-B3-04  official run luôn ghi log, không phụ thuộc cờ tuỳ chọn
  CHECK-B3-05  Base execute sớm mang nhãn `EXECUTED_EARLY` (ST §9)
  CHECK-B3-06  từ LOG tái dựng được lý do một quyết định, không cần chạy lại engine
  CHECK-B3-07  hành vi quyết định của engine KHÔNG đổi
  CHECK-B3-08  toàn bộ suite PASS (đo ở tầng suite, không ở file này)

Nguyên tắc: mọi bản ghi được kiểm ở đây đều do `run_engine` THẬT sinh ra
(`tests/wp_b3_scenarios.py`, `tests/wp_c2_scenarios.py` và một lần chạy toàn kỳ trên
dataset synthetic), KHÔNG bản ghi nào được dựng bằng tay. Mọi khẳng định "không có X" đều
đi kèm khẳng định "có Y" tương ứng để không PASS rỗng.
"""
from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pytest

import eth_dca_os.engine as engine_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION, GATE3_REALISTIC
from eth_dca_os.engine import (
    BACKTEST_NOT_EMITTED_REASONS,
    DECISION_LOG_FIELDS,
    DECISION_LOG_NOT_NULL_FIELDS,
    REASON_CODES_RECORDED_AS_TAG,
    STRATEGY_REASON_CODES,
    TRIGGER_TYPE_BY_REASON,
    TRIGGER_TYPES,
    ExecutionState,
    RunResult,
    run_engine,
    zone_reason_code,
)

import wp_b3_scenarios as b3
import wp_c2_scenarios as c2
from wp_c2_scenarios import fingerprint
from test_wp_c2_execution_state import FROZEN_PRE_WP_C2_FINGERPRINTS

REPO = Path(__file__).resolve().parents[1]
SPEC_DM = REPO / "docs/spec/04_DATA_MODEL_V2_1_5.md"
SPEC_ST = REPO / "docs/spec/02_STRATEGY_SPEC_V2_1_5.md"

#: Sáu Execution State của ST §16/§19 — dùng để chứng minh KHÔNG có vốn từ vựng thứ hai.
SPEC_STATES = ("WAIT", "FUNDING_REQUIRED", "READY_TO_BUY", "ACTION_PENDING",
               "COOLDOWN", "DATA_BLOCKED")

_CACHE: dict = {}


# --------------------------------------------------------------------- nguồn bản ghi thật

def scenario(name: str):
    """Kết quả của một kịch bản WP-B3 (chạy một lần, dùng lại)."""
    key = ("b3", name)
    if key not in _CACHE:
        _CACHE[key] = b3.run_scenario(name)
    return _CACHE[key]


def c2_scenario(name: str):
    key = ("c2", name)
    if key not in _CACHE:
        _CACHE[key] = c2.run_scenario(name)
    return _CACHE[key]


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    """Dataset synthetic + scores — cùng đường sinh mà pipeline production dùng."""
    from eth_dca_os.data.synth import generate
    from eth_dca_os.pipeline import Prepared
    raw = tmp_path_factory.mktemp("raw_b3")
    generate(raw)
    prep = Prepared(raw)
    return prep, prep.scores(BASELINE_STRATEGY.score_weights)


@pytest.fixture(scope="module")
def full_period(synth):
    """Chạy engine TOÀN KỲ trên cả hai execution config đã commit — đường production thật."""
    prep, scores = synth
    out = {}
    for name, ec in (("gate1_low_friction", GATE1_LOW_FRICTION),
                     ("gate3_realistic", GATE3_REALISTIC)):
        out[name] = run_engine(prep.dataset, scores, BASELINE_STRATEGY, ec,
                               pd.Timestamp("2019-01-01"), prep.oos_end())
    return out


def all_logs(full_period) -> list[list[dict]]:
    """Mọi `decision_log` quan sát được: hai run toàn kỳ + mọi kịch bản tất định."""
    logs = [r.decision_log for r in full_period.values()]
    logs += [scenario(n).decision_log for n in b3.SCENARIOS]
    logs += [c2_scenario(n).decision_log for n in c2.SCENARIOS]
    return logs


# ============================================================ CHECK-B3-01 — trường DM §11

def _data_model_11_fields() -> set[str]:
    """Đọc bảng §11 của Data Model từ CHÍNH văn bản spec, không chép tay."""
    text = SPEC_DM.read_text()
    block = text.split("## 11. decision_log", 1)[1].split("## 12.", 1)[0]
    fields: set[str] = set()
    for line in block.splitlines():
        if not line.startswith("|") or line.startswith("| Field") or set(line) <= set("|- "):
            continue
        cell = line.split("|")[1].strip()
        for part in cell.split("/"):
            fields.add(part.strip())
    return fields


def test_b3_01_record_shape_is_exactly_the_data_model_table(full_period):
    """Tập trường của MỌI bản ghi = đúng bảng DM §11 (+ `tags`), không thiếu không thừa."""
    spec_fields = _data_model_11_fields()
    assert spec_fields, "không đọc được bảng DM §11 — test sẽ PASS rỗng"
    assert spec_fields <= set(DECISION_LOG_FIELDS), \
        f"thiếu trường DM §11: {sorted(spec_fields - set(DECISION_LOG_FIELDS))}"
    extra = set(DECISION_LOG_FIELDS) - spec_fields
    assert extra == {"tags"}, f"trường ngoài DM §11 không được khai báo: {sorted(extra)}"

    seen = 0
    for log in all_logs(full_period):
        for d in log:
            assert tuple(d) == DECISION_LOG_FIELDS, f"sai tập/thứ tự trường: {list(d)}"
            seen += 1
    assert seen > 1000, f"chỉ quan sát {seen} bản ghi — quá ít để kết luận"


def test_b3_01_mandatory_fields_are_never_null(full_period):
    """F — trường DM §11 đánh dấu Bắt buộc/Snapshot bắt buộc KHÔNG được null ở bất kỳ đâu."""
    seen = 0
    for log in all_logs(full_period):
        for d in log:
            for k in DECISION_LOG_NOT_NULL_FIELDS:
                assert d[k] is not None, f"{k} null trong bản ghi {d}"
            seen += 1
    assert seen > 1000


def test_b3_01_capital_snapshot_reconciles_with_the_contribution_ledger(full_period):
    """Snapshot vốn phải ĐÚNG, không chỉ khác null.

    Tổng vốn của hệ thống chỉ đổi qua contribution (mọi bước còn lại chỉ dịch chuyển giữa
    AVAILABLE/RESERVED/DEPLOYED và giữa các pool), nên tại mọi bản ghi:

        available + reserved + deployed == (số contribution đã bơm) × 100

    Đây là bất biến DM §14 đo TRÊN CHÍNH bản ghi audit — nếu snapshot đọc sai pool hoặc sai
    thời điểm thì đẳng thức vỡ.
    """
    for res in full_period.values():
        contrib_ts = [t for t, _ in res.contributions]
        for d in res.decision_log:
            n = sum(1 for t in contrib_ts if t <= d["timestamp_utc"])
            total = d["available_vnd"] + d["reserved_vnd"] + d["deployed_vnd"]
            assert total == pytest.approx(n * 100.0, abs=1e-6), \
                f"vỡ bất biến DM §14 tại decision {d['decision_id']}: {total} != {n * 100.0}"
            assert min(d["available_vnd"], d["reserved_vnd"], d["deployed_vnd"]) >= -1e-9


def test_b3_01_recommended_usdt_est_follows_the_nominal_unit_convention(full_period):
    """BT §2.1 [F6] / CONVENTIONS #11: backtest chạy 1 USDT = 1 đơn vị."""
    seen = 0
    for log in all_logs(full_period):
        for d in log:
            assert d["recommended_usdt_est"] == d["recommended_vnd"]
            seen += d["recommended_vnd"] is not None
    assert seen > 100, "quá ít bản ghi mang lượng vốn để kết luận"


# ============================================================ CHECK-B3-02 — enum WP-C2

def test_b3_02_states_are_the_wp_c2_enum_itself(full_period):
    """Giá trị hai trường là THÀNH VIÊN của `engine.ExecutionState`, không phải chuỗi rời."""
    seen = 0
    for log in all_logs(full_period):
        for d in log:
            for k in ("previous_state", "new_state"):
                v = d[k]
                if v is None:
                    continue
                assert isinstance(v, ExecutionState), f"{k}={v!r} không thuộc enum WP-C2"
                assert v.value in SPEC_STATES
                seen += 1
    assert seen > 1000


def test_b3_02_states_are_null_only_before_the_first_measurement(full_period):
    """Null chỉ được phép ở các sự kiện xảy ra TRƯỚC lần đo đầu tiên của bước 12b.

    Trên đường production thật, con số đó là 0: lần đo đầu tiên nằm ở nến đầu tiên.
    """
    for name, res in full_period.items():
        nulls = [d for d in res.decision_log if d["new_state"] is None]
        assert not nulls, f"{name}: {len(nulls)} bản ghi thiếu trạng thái"


def test_b3_02_states_serialise_as_plain_strings(full_period):
    """B — ghi ra JSON phải là chuỗi thuần, không rò rỉ `repr` của enum."""
    for res in full_period.values():
        dumped = json.loads(json.dumps(
            [{"p": d["previous_state"], "n": d["new_state"]} for d in res.decision_log]))
        vals = {x for d in dumped for x in (d["p"], d["n"]) if x is not None}
        assert vals and vals <= set(SPEC_STATES), vals


def test_b3_02_no_second_execution_state_vocabulary():
    """A — CHỈ `ExecutionState` mang vốn từ vựng trạng thái thực thi trong toàn bộ `src/`."""
    import importlib
    import pkgutil

    import eth_dca_os

    owners = []
    for mod in pkgutil.walk_packages(eth_dca_os.__path__, "eth_dca_os."):
        m = importlib.import_module(mod.name)
        for obj in vars(m).values():
            if isinstance(obj, type) and getattr(obj, "__module__", "").startswith("eth_dca_os"):
                names = {n for n in dir(obj) if not n.startswith("_")}
                if len(names & set(SPEC_STATES)) >= 2:
                    owners.append(obj)
    assert {o.__qualname__ for o in owners} == {"ExecutionState"}, \
        f"có vốn từ vựng trạng thái thứ hai: {owners}"
    # ...và không mã reason nào trùng tên một Execution State (chống alias lệch ngữ nghĩa).
    assert set(STRATEGY_REASON_CODES) & set(SPEC_STATES) == {"FUNDING_REQUIRED"}, \
        "chỉ FUNDING_REQUIRED là tên chung của cả một state (ST §16) và một reason code (ST §20)"


def test_b3_02_every_wp_c2_transition_has_exactly_one_audit_record(full_period):
    """D + E — mỗi lần `execution_state_timeline` đổi mốc sinh ĐÚNG một bản ghi audit,
    đúng thứ tự thời gian, đúng cặp (trước, sau). Không có nguồn sự thật thứ hai."""
    for name, res in full_period.items():
        tl = res.execution_state_timeline
        trans = [d for d in res.decision_log if d["previous_state"] != d["new_state"]]
        assert len(tl) > 100, f"{name}: quá ít mốc trạng thái để kết luận"
        assert len(trans) == len(tl) - 1, \
            f"{name}: {len(trans)} bản ghi chuyển vs {len(tl) - 1} mốc timeline"
        for (ts_prev, s_prev), (ts_new, s_new), d in zip(tl, tl[1:], trans):
            assert (d["timestamp_utc"], d["previous_state"], d["new_state"]) == \
                   (ts_new, s_prev, s_new)


# ============================================================ CHECK-B3-03 — danh mục ST §20

def _strategy_20_codes() -> set[str]:
    """Đọc danh mục reason code từ CHÍNH văn bản ST §20 và khai triển các họ viết tắt."""
    body = SPEC_ST.read_text().split("## 20. Reason codes", 1)[1].split("## 21.", 1)[0]
    code_block = body.split("```")[1]
    raw = [t for t in re.split(r"[\s/]+", code_block) if t]
    out: set[str] = set()
    for tok in raw:
        if tok in ("S0", "S1", "S2"):
            out.add(f"SMART_ZONE_{tok}")
        elif re.fullmatch(r"C0\.\.C3", tok):
            out |= {f"CRASH_ZONE_C{i}" for i in range(4)}
        elif re.fullmatch(r"O[0-4]", tok):
            out.add(f"OPPORTUNITY_{tok}")
        elif tok == "CRASH_ZONE_C0..C3":
            out |= {f"CRASH_ZONE_C{i}" for i in range(4)}
        else:
            out.add(tok)
    return out


def test_b3_03_reason_code_catalogue_matches_the_spec_text():
    """Vốn từ vựng lý do = ĐÚNG danh mục ST §20; WP-B3 không phát minh mã mới."""
    spec = _strategy_20_codes()
    assert len(spec) > 25, f"đọc spec hỏng, chỉ ra {len(spec)} mã"
    assert spec == set(STRATEGY_REASON_CODES), (
        f"thiếu: {sorted(spec - set(STRATEGY_REASON_CODES))} · "
        f"thừa: {sorted(set(STRATEGY_REASON_CODES) - spec)}")


def test_b3_03_every_emitted_code_and_trigger_type_is_canonical(full_period):
    seen = 0
    for log in all_logs(full_period):
        for d in log:
            assert d["reason_code"] in STRATEGY_REASON_CODES, d["reason_code"]
            assert d["trigger_type"] in TRIGGER_TYPES, d["trigger_type"]
            assert d["trigger_type"] == TRIGGER_TYPE_BY_REASON[d["reason_code"]]
            seen += 1
    assert seen > 1000


def test_b3_03_catalogue_coverage_is_complete_or_declared(full_period):
    """Mọi mã ST §20 hoặc ĐƯỢC GHI thật, hoặc có lý do canonical vì sao không bao giờ ghi."""
    emitted = {d["reason_code"] for log in all_logs(full_period) for d in log}
    declared = set(BACKTEST_NOT_EMITTED_REASONS) | set(REASON_CODES_RECORDED_AS_TAG)
    missing = set(STRATEGY_REASON_CODES) - emitted - declared
    assert not missing, f"mã ST §20 không được ghi và cũng không có lý do: {sorted(missing)}"
    assert not (emitted & set(BACKTEST_NOT_EMITTED_REASONS)), \
        "một mã đã tuyên bố KHÔNG BAO GIỜ ghi lại xuất hiện trong log"
    for code, reason in BACKTEST_NOT_EMITTED_REASONS.items():
        assert len(reason) > 40, f"{code}: lý do quá mỏng để coi là tuyên bố"


def test_b3_03_tag_recorded_codes_really_appear_as_tags():
    """`DELAYED_DATA_FILL` là NHÃN của một quyết định khác — phải quan sát được ở `tags`."""
    log = scenario("base_gap_month_end").decision_log
    tagged = [d for d in log if "DELAYED_DATA_FILL" in d["tags"]]
    assert tagged, "không quan sát được nhãn DELAYED_DATA_FILL trên đường chạy thật"
    assert all(t["reason_code"] in ("BASE_SCHEDULE", "MONTH_END_BASE") for t in tagged)
    for code in REASON_CODES_RECORDED_AS_TAG:
        assert code not in {d["reason_code"] for d in log}


@pytest.mark.parametrize("name,code", [
    ("max_zones_block", "MAX_ZONES_BLOCK"),
    ("action_missed", "ACTION_MISSED"),
    ("action_ttl_expired", "ACTION_TTL_EXPIRED"),
    ("data_degraded", "DATA_DEGRADED"),
    ("base_advance_early", "BASE_ADVANCE_SCORE"),
    ("base_gap_month_end", "MONTH_END_BASE"),
])
def test_b3_03_each_added_event_type_has_a_real_engine_path(name, code):
    """Mỗi loại sự kiện mới được ghi phải có ĐƯỜNG SINH THẬT từ `run_engine`."""
    res = scenario(name)
    rows = [d for d in res.decision_log if d["reason_code"] == code]
    assert rows, f"{name}: engine không sinh ra {code}"


def test_b3_03_data_blocked_is_attributable_to_real_data_quality():
    """G — mọi bản ghi vào `DATA_BLOCKED` phải mang `data_quality == INVALID` thật."""
    res = c2_scenario("data_invalid_window")
    rows = [d for d in res.decision_log
            if d["new_state"] is ExecutionState.DATA_BLOCKED
            and d["previous_state"] != d["new_state"]]
    assert rows, "kịch bản không tạo được DATA_BLOCKED — test sẽ PASS rỗng"
    for d in rows:
        assert d["data_quality"] == "INVALID"
        assert d["reason_code"] == "DATA_INVALID"
        assert d["trigger_type"] == "data"


def test_b3_03_cooldown_transition_follows_a_real_cooldown_event():
    """I — `COOLDOWN` chỉ vào sau một lần fill mở cooldown, và ra khi cooldown hết hiệu lực."""
    res = c2_scenario("smart_action_cycle")
    log = res.decision_log
    enters = [d for d in log if d["new_state"] is ExecutionState.COOLDOWN
              and d["previous_state"] is not ExecutionState.COOLDOWN]
    leaves = [d for d in log if d["previous_state"] is ExecutionState.COOLDOWN
              and d["new_state"] is not ExecutionState.COOLDOWN]
    assert enters and leaves
    for d in enters + leaves:
        assert d["reason_code"] == "COOLDOWN_START"
    opened = [d for d in log if d["reason_code"] == "COOLDOWN_START"
              and d["previous_state"] == d["new_state"]]
    assert opened, "phải có sự kiện MỞ cooldown (không phải chuyển trạng thái) trước đó"
    assert opened[0]["timestamp_utc"] <= enters[0]["timestamp_utc"]
    # cooldown mở đúng bằng một fill: cùng ts với một purchase Smart/Opportunity/Crash
    fills = {p["ts"] for p in res.purchases if p["source"] != "BASE"}
    assert {d["timestamp_utc"] for d in opened} <= fills


def test_b3_03_action_lifecycle_is_represented_for_one_zone():
    """H — vòng đời một action thật: recommendation -> ACTION_PENDING -> READY_TO_BUY -> fill,
    tất cả mang CÙNG `zone_id` và đúng thứ tự thời gian."""
    log = c2_scenario("smart_action_cycle").decision_log
    zid = next(d["zone_id"] for d in log if d["reason_code"] == "SMART_ZONE_S0")
    rows = [d for d in log if d["zone_id"] == zid]
    states = [(d["previous_state"], d["new_state"]) for d in rows]
    assert (ExecutionState.WAIT, ExecutionState.ACTION_PENDING) in states
    assert (ExecutionState.ACTION_PENDING, ExecutionState.READY_TO_BUY) in states
    fill = [d for d in rows if d["recommended_vnd"] is not None
            and d["previous_state"] == d["new_state"]]
    assert len(fill) >= 2, "phải có cả bản ghi recommendation lẫn bản ghi fill"
    assert [d["decision_id"] for d in rows] == sorted(d["decision_id"] for d in rows)


def test_b3_03_funding_required_is_never_fabricated_in_backtest(full_period):
    """J + ADR-001 — tầng backtest không bịa `FUNDING_REQUIRED` dưới bất kỳ hình dạng nào."""
    for log in all_logs(full_period):
        for d in log:
            assert d["reason_code"] not in ("FUNDING_REQUIRED", "FUNDING_COMPLETE")
            assert d["trigger_type"] != "funding"
            for k in ("previous_state", "new_state"):
                assert d[k] is not ExecutionState.FUNDING_REQUIRED
    # ...trong khi enum VẪN giữ giá trị đó cho tầng app (Product Spec §6/§7/§11).
    assert ExecutionState.FUNDING_REQUIRED in engine_mod.BACKTEST_NOT_APPLICABLE_STATES


def test_b3_03_legacy_events_survive_the_migration(full_period):
    """L — ba loại sự kiện `decision_log` ĐÃ CÓ trước WP-B3 không mất, và giữ danh tính."""
    log = full_period["gate1_low_friction"].decision_log
    for code, key in (("BULLISH_INVALIDATION", "ladder_id"),
                      ("CRASH_ENTRY_7D", None),
                      ("COOLDOWN_OVERRIDE", "zone_id")):
        rows = [d for d in log if d["reason_code"] == code]
        assert rows, f"mất loại sự kiện đã có trước WP-B3: {code}"
        if key:
            assert all(d[key] is not None for d in rows), f"{code} mất danh tính {key}"


# ============================================================ CHECK-B3-04 — không còn cờ

def test_b3_04_run_engine_has_no_logging_flag():
    """Audit trail của official run không thể là tuỳ chọn — cờ phải BIẾN MẤT khỏi hợp đồng."""
    params = set(inspect.signature(run_engine).parameters)
    assert not [p for p in params if "log" in p.lower()], params
    assert "log_decisions" not in Path(engine_mod.__file__).read_text()


def test_b3_04_production_window_path_writes_the_log(synth):
    """Đường production thật (`metrics.run_window`, thứ Gate 1 gọi) ghi log mà không có cờ."""
    from eth_dca_os.metrics import run_window
    prep, scores = synth
    r = run_window(prep.dataset, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                   "2019-01-01", "2019-07-01")
    log = r["result"].decision_log
    assert len(log) > 20, f"đường production chỉ ghi {len(log)} bản ghi"
    assert r["result"].purchases, "cửa sổ không có giao dịch nào — test sẽ PASS rỗng"


# ============================================================ CHECK-B3-05 — EXECUTED_EARLY

def test_b3_05_early_base_tranche_carries_the_executed_early_label():
    """ST §9: tranche Base kéo sớm PHẢI được đánh dấu (đóng F-033)."""
    res = scenario("base_advance_early")
    early = [d for d in res.decision_log if d["reason_code"] == "BASE_ADVANCE_SCORE"]
    assert early, "kịch bản không kéo sớm tranche nào — test sẽ PASS rỗng"
    assert len(early) == res.counters["base_early"], \
        "số bản ghi audit phải khớp bộ đếm engine, không nhiều không ít"
    for d in early:
        assert "EXECUTED_EARLY" in d["tags"]
        assert d["trigger_type"] == "base"
    # nhãn KHÔNG được gắn nhầm cho tranche chạy đúng lịch
    for d in res.decision_log:
        if d["reason_code"] != "BASE_ADVANCE_SCORE":
            assert "EXECUTED_EARLY" not in d["tags"]


def test_b3_05_original_schedule_day_is_not_repeated():
    """Vế thứ hai của ST §9 — "không lặp lại vào ngày gốc" — vẫn đúng sau WP-B3."""
    res = scenario("base_advance_early")
    base = [p for p in res.purchases if p["source"] == "BASE"]
    assert base and all(p["reason"] == "BASE_ADVANCE_SCORE" for p in base), \
        "cả ba tranche đã được kéo sớm; không tranche nào được chạy lại theo lịch gốc"
    assert len(base) == 3
    assert not [d for d in res.decision_log if d["reason_code"] == "BASE_SCHEDULE"]


def test_b3_05_executed_early_is_not_written_onto_the_purchase_record():
    """Nhãn nằm ở AUDIT TRAIL (DM §11), không ở `purchases[].tags` (danh mục nhãn dữ liệu
    BT §18) — đó là điều giữ cho đầu ra tài chính bất biến (`CHECK-B3-07`)."""
    res = scenario("base_advance_early")
    for p in res.purchases:
        assert "EXECUTED_EARLY" not in p["tags"]
    assert any("EXECUTED_EARLY" in d["tags"] for d in res.decision_log)


# ============================================================ CHECK-B3-06 — tái dựng lý do

def _answer_from_row_alone(row: dict) -> dict:
    """Trả lời năm câu hỏi của CHECK-B3-06 CHỈ từ một bản ghi (không chạm engine)."""
    return {
        "trạng thái trước": row["previous_state"],
        "trạng thái sau": row["new_state"],
        "vốn khả dụng": row["available_vnd"],
        "lý do": row["reason_code"],
        "cấu hình": (row["strategy_config_hash"], row["execution_config_hash"]),
    }


def test_b3_06_three_decisions_are_explained_by_the_log_alone(full_period):
    """Phép thử THẬT của gói: ba quyết định ở BA loại khác nhau, mỗi câu trả lời lấy từ log
    rồi ĐỐI CHIẾU với một nguồn độc lập (purchase record, timeline, ledger contribution)."""
    res = full_period["gate3_realistic"]
    log = res.decision_log
    picks = {}
    for d in log:
        picks.setdefault(d["trigger_type"], d)
    assert len(picks) >= 3, f"chỉ có {len(picks)} loại quyết định"

    tl = res.execution_state_timeline
    contrib_ts = [t for t, _ in res.contributions]
    for kind, row in list(picks.items())[:3]:
        ans = _answer_from_row_alone(row)
        assert ans["lý do"] in STRATEGY_REASON_CODES
        assert ans["cấu hình"] == (BASELINE_STRATEGY.hash, GATE3_REALISTIC.hash)
        assert ans["trạng thái sau"] is not None
        # trạng thái trong log phải khớp timeline WP-C2 đọc độc lập
        state_at = [s for ts, s in tl if ts <= row["timestamp_utc"]][-1]
        assert ans["trạng thái sau"] == state_at, kind
        # vốn khả dụng trong log phải nhất quán với sổ contribution
        n = sum(1 for t in contrib_ts if t <= row["timestamp_utc"])
        assert ans["vốn khả dụng"] <= n * 100.0 + 1e-6


def test_b3_06_a_fill_record_reconstructs_its_purchase(full_period):
    """Một quyết định fill phải tự giải thích được: cùng ts, cùng lượng vốn, cùng zone."""
    res = full_period["gate1_low_friction"]
    by_ts_amount = {(p["ts"], round(p["nominal"], 9)) for p in res.purchases}
    fills = [d for d in res.decision_log
             if d["trigger_type"] in ("zone", "base", "month_end")
             and d["recommended_vnd"] is not None
             and (d["timestamp_utc"], round(d["recommended_vnd"], 9)) in by_ts_amount]
    assert len(fills) >= 100, f"chỉ khớp được {len(fills)} bản ghi fill"


# ============================================================ CHECK-B3-07 — hành vi không đổi

class _NullList(list):
    """Danh sách nuốt mọi `append` — dùng để GỠ BỎ lớp ghi log khỏi engine."""

    def append(self, item):  # noqa: D102
        return None


@dataclass
class _NoAuditResult(RunResult):
    decision_log: list = field(default_factory=_NullList)


@pytest.mark.parametrize("name", sorted(c2.SCENARIOS))
def test_b3_07_removing_the_audit_layer_changes_no_behaviour(name, monkeypatch):
    """C — bằng chứng HÀNH VI cho "log quan sát, không điều khiển".

    Gỡ bỏ hoàn toàn lớp ghi log (mọi `append` bị nuốt) rồi chạy lại engine: fingerprint
    hành vi vẫn TRÙNG KHỚP giá trị chụp trên cây mã TRƯỚC WP-B3. Nếu bất kỳ nhánh nào đọc
    `decision_log` — dù chỉ một — kết quả đã phải đổi.
    """
    monkeypatch.setattr(engine_mod, "RunResult", _NoAuditResult)
    res = c2.run_scenario(name)
    assert res.decision_log == [], "phép gỡ log không có hiệu lực — test sẽ PASS rỗng"
    assert fingerprint(res) == FROZEN_PRE_WP_C2_FINGERPRINTS[name]


@pytest.mark.parametrize("name", sorted(c2.SCENARIOS))
def test_b3_07_engine_behaviour_is_identical_with_the_audit_layer(name):
    """...và với lớp ghi log BẬT, fingerprint vẫn là đúng giá trị trước WP-B3."""
    res = c2.run_scenario(name)
    assert fingerprint(res) == FROZEN_PRE_WP_C2_FINGERPRINTS[name]
    assert res.decision_log, "kịch bản không ghi bản ghi nào — test sẽ PASS rỗng"


def test_b3_07_audit_trail_is_deterministic_across_replays():
    """K — chạy lại đúng kịch bản đó cho ĐÚNG cùng một chuỗi bản ghi: một quan sát lặp lại
    không sinh ra một sự kiện nghiệp vụ giả."""
    a = b3.run_scenario("action_missed").decision_log
    b = b3.run_scenario("action_missed").decision_log
    strip = lambda log: [{k: v for k, v in d.items() if k not in ("zone_id", "ladder_id")}
                         for d in log]
    assert a and strip(a) == strip(b)
    ids = [d["decision_id"] for d in a]
    assert ids == list(range(1, len(a) + 1)), "decision_id phải là khoá chính duy nhất, liên tục"


def test_b3_07_records_are_chronological_and_uniquely_keyed(full_period):
    """E + K — thứ tự thời gian không giảm, `decision_id` duy nhất và tăng nghiêm ngặt."""
    for name, res in full_period.items():
        log = res.decision_log
        assert len(log) > 1000, f"{name}: quá ít bản ghi"
        ts = [d["timestamp_utc"] for d in log]
        assert ts == sorted(ts), f"{name}: bản ghi không theo thứ tự thời gian"
        ids = [d["decision_id"] for d in log]
        assert ids == list(range(1, len(log) + 1))
        assert len(set(ids)) == len(ids)


# ============================================================ quan sát về chính engine

def test_b3_action_ttl_expired_is_unreachable_when_ttl_is_a_multiple_of_the_candle():
    """Quan sát ghi thành H-36: với `action_ttl_seconds` là bội số của 900s (mọi cấu hình
    trong `manifests.GATE3_GRID` và baseline), nhánh `ACTION_TTL_EXPIRED` KHÔNG BAO GIỜ tới
    lượt — `ACTION_MISSED` luôn kích hoạt ở nến sớm hơn. Đây là cấu trúc sẵn có của engine,
    không phải hệ quả của WP-B3; test này khoá quan sát đó lại.
    """
    on_grid = b3.run_scenario("action_missed").decision_log
    off_grid = b3.run_scenario("action_ttl_expired").decision_log
    assert b3.GATE3_SLOW_FUNDING.action_ttl_seconds % 900 == 0
    assert b3.OFF_GRID_TTL.action_ttl_seconds % 900 != 0
    assert {d["reason_code"] for d in on_grid} & {"ACTION_TTL_EXPIRED"} == set()
    assert any(d["reason_code"] == "ACTION_MISSED" for d in on_grid)
    assert any(d["reason_code"] == "ACTION_TTL_EXPIRED" for d in off_grid)


def test_b3_zone_reason_code_matches_the_pool_ledger_vocabulary(monkeypatch):
    """Mã zone của audit trail = ĐÚNG mã mà `Pool` ledger (DM §6) ghi khi reserve.

    Hai sổ nói cùng một thứ tiếng thì mới đối chiếu được với nhau; nếu WP-B3 tự đặt tên
    khác, audit trail và ledger vốn sẽ trôi khỏi nhau ngay từ ngày đầu.
    """
    from wp_a3_harness import run_case
    res, rec = run_case([{"price": 100.0, "oscore": 20.0, "return7": 0.0},
                         {"oscore": 75.0, "low_dip": 50.0}, {}, {}, {}, {}], monkeypatch)
    ledger = {e["reason_code"] for name in ("SMART", "OPPORTUNITY")
              for e in rec.pool(name).ledger if e["entry_type"] == "RESERVE"}
    audit = {d["reason_code"] for d in res.decision_log
             if d["reason_code"].startswith(("SMART_ZONE_S", "OPPORTUNITY_O"))}
    assert ledger and audit, "kịch bản không tạo reservation nào — test sẽ PASS rỗng"
    assert ledger <= audit, f"ledger dùng mã mà audit trail không có: {sorted(ledger - audit)}"
    assert audit <= {zone_reason_code(t, i) for t in ("SMART", "OPPORTUNITY")
                     for i in range(5)}
