"""WP-A4 — ngữ nghĩa dữ liệu thiếu/hỏng: CHECK-A4-01…06.

Đóng ba finding:
  F-023 — định nghĩa INVALID hẹp hơn Strategy §3 (chỉ INVALID khi mất CẢ TÁM sub-factor)
  F-025 — tag `EXECUTION_DATA_GAP` cho nến 15m thiếu không tồn tại trong `src/`
  F-032 — `DELAYED_DATA_FILL` chỉ là bộ đếm, không gắn tag lên purchase record

Nguyên tắc bằng chứng của gói (task file): mọi mệnh đề về hành vi được chứng minh trên
dataset CÓ GAP THẬT, không phải trên dataset sạch rồi suy luận. Các test engine dưới đây
đều xoá nến 15m khỏi dataset rồi chạy `run_engine` thật.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import eth_dca_os.engine as engine_mod
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.score import (
    REQUIRED_DAILY_INDICATORS,
    compute_scores,
    factor_scores,
    opportunity_unlock,
    sub_factors,
)
from wp_a3_harness import DAY, TZ, build_dataset

SUB_FACTOR_INPUTS = ("dd365", "ma_ratio", "percentile365", "rsi14", "return7",
                     "volume_ratio", "ethbtc_return30", "ethbtc_percentile180")


def _ind(**kw) -> pd.DataFrame:
    """Một hàng indicator daily hợp lệ hoàn toàn; `kw` để làm hỏng đúng một thứ."""
    base = dict(close=1800.0, adr30=0.03,
                dd365=-0.30, ma_ratio=0.90, percentile365=0.20, rsi14=40.0,
                return7=-0.10, volume_ratio=1.5, ethbtc_return30=-0.10,
                ethbtc_percentile180=0.30)
    base.update(kw)
    return pd.DataFrame([base])


def _quality(ind: pd.DataFrame) -> str:
    return str(compute_scores(ind)["data_quality"].iloc[0])


# ==================================================== CHECK-A4-01

# Bảng ca kiểm thử phủ đúng ba nhóm mà CHECK-A4-01 đòi hỏi.
A4_01_CASES = [
    # (a) giá / lịch sử ETH không hợp lệ -> INVALID
    ("a-gia-thieu",            dict(close=np.nan),               "INVALID"),
    ("a-gia-bang-khong",       dict(close=0.0),                  "INVALID"),
    ("a-gia-am",               dict(close=-1800.0),              "INVALID"),
    # (b) MỘT indicator bắt buộc không hợp lệ -> INVALID
    ("b-return7-thieu",        dict(return7=np.nan),             "INVALID"),
    ("b-adr30-thieu",          dict(adr30=np.nan),               "INVALID"),
    ("b-adr30-vo-cuc",         dict(adr30=np.inf),               "INVALID"),
    # (c) CHỈ sub-factor không bắt buộc thiếu -> DEGRADED
    ("c-volume-thieu",         dict(volume_ratio=np.nan),        "DEGRADED"),
    ("c-rsi-thieu",            dict(rsi14=np.nan),               "DEGRADED"),
    ("c-dd365-thieu",          dict(dd365=np.nan),               "DEGRADED"),
    ("c-ma-ratio-thieu",       dict(ma_ratio=np.nan),            "DEGRADED"),
    ("c-percentile-thieu",     dict(percentile365=np.nan),       "DEGRADED"),
    ("c-ethbtc-r30-thieu",     dict(ethbtc_return30=np.nan),     "DEGRADED"),
    ("c-ethbtc-pct-thieu",     dict(ethbtc_percentile180=np.nan), "DEGRADED"),
    ("c-ba-sub-factor-thieu",  dict(dd365=np.nan, rsi14=np.nan,
                                    ethbtc_return30=np.nan),     "DEGRADED"),
    # đối chứng dương: đủ hết
    ("d-du-het",               dict(),                            "GOOD"),
]


@pytest.mark.parametrize("name,mutation,expected", A4_01_CASES,
                         ids=[c[0] for c in A4_01_CASES])
def test_a4_01_invalid_definition_matches_strategy_3(name, mutation, expected):
    """CHECK-A4-01 — INVALID khớp §3: giá/lịch sử ETH **hoặc** indicator bắt buộc hỏng."""
    ind = _ind(**mutation)
    assert _quality(ind) == expected, (name, mutation)


@pytest.mark.parametrize("name,mutation,expected", A4_01_CASES,
                         ids=[c[0] for c in A4_01_CASES])
def test_a4_01_oscore_nullable_only_when_invalid(name, mutation, expected):
    """Data Model §4: `opportunity_score_raw` nullable CHỈ khi INVALID — hai chiều."""
    sc = compute_scores(_ind(**mutation))
    assert np.isnan(sc["oscore"].iloc[0]) is np.bool_(expected == "INVALID"), (name, expected)


def test_a4_01_old_definition_would_have_missed_group_b():
    """Ranh giới của F-023: định nghĩa CŨ (mất cả 8 sub-factor) không bắt được nhóm (b).

    Thiếu `return7` chỉ làm 2/8 sub-factor NaN, nên luật cũ đọc là DEGRADED và engine
    tiếp tục hành động — đúng thời điểm §3 yêu cầu dừng. Test này khoá chính khoảng cách
    đó lại: nếu ai đó hoàn nguyên định nghĩa, nó đỏ.
    """
    ind = _ind(return7=np.nan)
    sf = sub_factors(ind)
    assert int(sf.isna().sum(axis=1).iloc[0]) == 2, "chỉ S7 và V thiếu"
    assert factor_scores(sf)["data_quality"].iloc[0] == "DEGRADED", "luật CŨ"
    assert _quality(ind) == "INVALID", "luật MỚI theo §3"


def test_a4_01_required_indicator_list_is_declared_once():
    """Danh sách 'indicator bắt buộc' phải tra cứu được, không nằm rải rác trong logic."""
    assert REQUIRED_DAILY_INDICATORS == ("close", "return7", "adr30")
    conventions = Path("docs/CONVENTIONS.md").read_text(encoding="utf-8")
    for col in REQUIRED_DAILY_INDICATORS:
        assert col in conventions, f"{col} chưa được ghi ở docs/CONVENTIONS.md"


def test_a4_01_missing_required_column_is_fail_closed():
    """Khung dữ liệu không mang nổi indicator bắt buộc => INVALID, không phải GOOD."""
    ind = _ind().drop(columns=["adr30"])
    assert _quality(ind) == "INVALID"


# ==================================================== engine helpers

def _drop_candles(eth15: pd.DataFrame, start_utc: pd.Timestamp, drops) -> pd.DataFrame:
    """Xoá nến 15m theo (ngày local thứ k tính từ Day 1, giờ bắt đầu, giờ kết thúc)."""
    ts = ((pd.DatetimeIndex(eth15["open_time"]) - pd.Timestamp(0, tz="UTC"))
          / pd.Timedelta(seconds=1)).to_numpy(float)
    local = ts + TZ
    day0 = int((start_utc.value // 10**9 + TZ) // DAY)
    keep = np.ones(len(eth15), dtype=bool)
    for k, h0, h1 in drops:
        mask = ((local // DAY).astype(int) == day0 + k) & \
               (local % DAY >= h0 * 3600) & (local % DAY < h1 * 3600)
        keep &= ~mask
    return eth15[keep].reset_index(drop=True)


def _run(day_specs, drops=(), first_local_day="2023-03-01", contribution=100.0):
    ds, scores, start, end = build_dataset(day_specs, first_local_day=first_local_day)
    ds = dict(ds)
    ds["ETHUSDT_15m"] = _drop_candles(ds["ETHUSDT_15m"], start, drops)
    return engine_mod.run_engine(ds, scores, BASELINE_STRATEGY, GATE1_LOW_FRICTION,
                                 start, end, contribution=contribution, log_decisions=True)


def _tagged(res, tag):
    return [p for p in res.purchases if tag in p.get("tags", [])]


# ==================================================== CHECK-A4-02

DIP_DAY = 5          # chỉ số 0-based của ngày có low_dip trong các kịch bản dưới đây


def _specs(dq_from_day4: str, dq_after_dip: str):
    """Ladder Smart được tạo ở những ngày dữ liệu tốt đầu tiên; cú dip rơi vào DIP_DAY.

    Harness đặt `dq` có hiệu lực TỪ 07:00 local của ngày khai báo, nên để CẢ ngày DIP_DAY
    mang một trạng thái thì phải khai từ ngày liền trước — nếu không, các nến 00:00–06:45
    của ngày dip vẫn chạy dưới trạng thái của ngày cũ và test sẽ chứng minh ít hơn
    narrative của nó.
    """
    specs = [{"price": 100.0, "oscore": 60.0} for _ in range(4)]
    specs.append({"price": 100.0, "oscore": 60.0, "dq": dq_from_day4})
    specs.append({"price": 100.0, "low_dip": 60.0, "oscore": 60.0, "dq": dq_from_day4})
    specs += [{"price": 100.0, "oscore": 60.0, "dq": dq_after_dip} for _ in range(3)]
    return specs


def _risky(res):
    return [p for p in res.purchases if p["source"] in ("SMART", "OPPORTUNITY", "CRASH")]


def test_a4_02_invalid_blocks_new_actions_in_engine():
    """CHECK-A4-02 — dữ liệu INVALID tại thời điểm CÓ trigger: KHÔNG action nào được tạo.

    Đối chứng dương ở cùng kịch bản với dq = GOOD là phần bắt buộc: thiếu nó, một engine
    không bao giờ mua cũng sẽ "qua" test này.
    """
    specs_good, specs_bad = _specs("GOOD", "GOOD"), _specs("INVALID", "INVALID")
    good, invalid = _run(specs_good), _run(specs_bad)

    # Chỉ so sánh phần SAU khi trạng thái dữ liệu có hiệu lực (07:00 local ngày thứ 5):
    # ladder S0 chạm giá ngay Day 1 trong CẢ HAI kịch bản, và Day 1 thì dữ liệu còn GOOD ở
    # cả hai — gộp nó vào sẽ làm mệnh đề sai chứ không làm nó mạnh hơn.
    _, _, start, _ = build_dataset(specs_good)
    t0 = start.value / 1e9 + 4 * DAY + 7 * 3600

    after_good = [p for p in _risky(good) if p["ts"] >= t0]
    after_invalid = [p for p in _risky(invalid) if p["ts"] >= t0]

    assert after_good, "đối chứng dương: dữ liệu GOOD phải tạo được action ở cú dip"
    assert not after_invalid, "§3: INVALID chặn MỌI action Smart/Opportunity mới"


def test_a4_02_block_is_temporal_not_permanent():
    """Chỉ RIÊNG ngày có trigger là INVALID: không action nào trong ngày đó, nhưng khi dữ
    liệu tốt trở lại thì engine hoạt động bình thường.

    Hai vế cùng cần thiết: vế đầu chứng minh cổng ĐÓNG, vế sau chứng minh nó không đóng
    vĩnh viễn — một engine hỏng hoàn toàn cũng thoả vế đầu.
    """
    specs = _specs("INVALID", "GOOD")
    res = _run(specs)

    _, _, start, _ = build_dataset(specs)
    day_lo = start.value / 1e9 + DIP_DAY * DAY
    on_invalid_day = [p for p in _risky(res) if day_lo <= p["ts"] < day_lo + DAY]
    assert not on_invalid_day, on_invalid_day
    assert [p for p in _risky(res) if p["ts"] >= day_lo + DAY], \
        "dữ liệu tốt trở lại mà engine vẫn đứng im — cổng đóng vĩnh viễn"


def test_a4_02_base_schedule_still_runs_when_invalid():
    """§3: 'Base schedule vẫn có thể chạy theo fallback được ghi nhận' — INVALID không
    được biến thành 'đứng im hoàn toàn'."""
    res = _run([{"price": 100.0, "oscore": 60.0, "dq": "INVALID"} for _ in range(6)])
    assert [p for p in res.purchases if p["source"] == "BASE"]


# ==================================================== CHECK-A4-03

def test_a4_03_execution_data_gap_tag_on_affected_record():
    """CHECK-A4-03 — nến 15m thiếu: bản ghi bị ảnh hưởng mang tag `EXECUTION_DATA_GAP`.

    Xoá 10:00–11:45 local Day 3 (ngày Base tranche đầu tiên). Nến 12:00 vẫn tồn tại nên
    tranche chạy ĐÚNG GIỜ (không delayed), nhưng nó là nến hợp lệ đầu tiên sau một lỗ
    hổng 8 nến — bản ghi phải tự khai điều đó.
    """
    specs = [{"price": 100.0, "oscore": 30.0} for _ in range(5)]
    res = _run(specs, drops=[(2, 10, 12)])

    tagged = _tagged(res, "EXECUTION_DATA_GAP")
    assert tagged, "không bản ghi nào mang EXECUTION_DATA_GAP"
    rec = tagged[0]
    assert rec["reason"] == "BASE_SCHEDULE"
    assert rec["missing_candles_before"] == 8, rec
    assert "DELAYED_DATA_FILL" not in rec["tags"], "nến 12:00 vẫn có: không phải fill trễ"
    assert res.counters["execution_data_gap"] == len(tagged)


def test_a4_03_clean_dataset_has_no_gap_tag():
    """Đối chứng âm: dataset liên tục KHÔNG được sinh tag nào — nếu có, tag vô nghĩa."""
    res = _run([{"price": 100.0, "oscore": 30.0} for _ in range(5)])
    assert not _tagged(res, "EXECUTION_DATA_GAP")
    assert res.counters["execution_data_gap"] == 0
    assert all(p["missing_candles_before"] == 0 for p in res.purchases)


# ==================================================== CHECK-A4-04

def test_a4_04_delayed_data_fill_tag_on_purchase_record():
    """CHECK-A4-04 — Base fill bị trễ vì gap mang tag `DELAYED_DATA_FILL` TRÊN BẢN GHI.

    Xoá 12:00–12:45 local Day 3: nến 12:00 nằm trong gap nên tranche execute ở nến hợp lệ
    đầu tiên sau đó (12:45) — đúng ST §9 [F3].
    """
    specs = [{"price": 100.0, "oscore": 30.0} for _ in range(5)]
    res = _run(specs, drops=[(2, 12, 12.75)])

    tagged = _tagged(res, "DELAYED_DATA_FILL")
    assert tagged, "không bản ghi nào mang DELAYED_DATA_FILL"
    rec = tagged[0]
    assert rec["source"] == "BASE" and rec["reason"] == "BASE_SCHEDULE"
    # Bộ đếm vẫn còn, nhưng nó KHÔNG còn là nguồn thông tin duy nhất (F-032). Bất biến
    # "bộ đếm == số bản ghi mang tag" phải đúng, nếu không bộ đếm lại nói về những bản ghi
    # không tồn tại — cùng kiểu sai lệch, chỉ đổi chiều.
    assert res.counters["delayed_data_fill"] == len(tagged)
    tod = (rec["ts"] + TZ) % DAY
    assert tod == 12.75 * 3600, "phải là nến hợp lệ đầu tiên SAU gap"


# ==================================================== CHECK-A4-05

def test_a4_05_base_tranche_never_dropped_because_of_gap():
    """CHECK-A4-05 [F3] — Base tranche không bao giờ bị bỏ vì gap dữ liệu.

    Xoá TRỌN Day 23 và trọn Day 25–28 (các cửa quét Month-End), nên tranche Day 23 chỉ
    còn một đường duy nhất để sống sót: giải ngân khi sang tháng. Đưa mệnh đề 13 của
    Impl Plan §7 từ 'xác nhận ở tầng code' lên bằng chứng E1.
    """
    specs = [{"price": 100.0, "oscore": 30.0} for _ in range(34)]   # 01/03 -> 03/04
    drops = [(22, 0, 24)] + [(d, 0, 24) for d in (24, 25, 26, 27)]
    res = _run(specs, drops=drops)

    tagged = _tagged(res, "DELAYED_DATA_FILL")
    assert tagged, "tranche Day 23 bị BỎ — vi phạm [F3]"
    assert any(p["reason"] == "MONTH_END_BASE" for p in tagged), tagged

    assert res.counters["delayed_data_fill"] == len(tagged), \
        "bộ đếm phải khớp số bản ghi mang tag, kể cả khi tranche bị bỏ qua vì hết vốn"

    clean = _run(specs)
    assert not _tagged(clean, "DELAYED_DATA_FILL"), "đối chứng: dataset sạch không có fill trễ"
    assert clean.counters["delayed_data_fill"] == 0

    def base_total(r):
        return sum(p["nominal"] for p in r.purchases if p["source"] == "BASE")

    assert base_total(res) == pytest.approx(base_total(clean), rel=1e-12), \
        "gap KHÔNG được làm mất một đồng ngân sách Base nào so với dataset sạch"
    assert base_total(clean) > 0


# ==================================================== CHECK-A4-06

@pytest.mark.parametrize("col", SUB_FACTOR_INPUTS)
def test_a4_06_degraded_never_pushes_score_up(col):
    """CHECK-A4-06 — 'dữ liệu xấu phải kéo score xuống, không bao giờ đẩy lên' (§3)."""
    good = compute_scores(_ind())["oscore"].iloc[0]
    degraded = compute_scores(_ind(**{col: np.nan}))["oscore"].iloc[0]
    if np.isnan(degraded):
        return          # thiếu indicator bắt buộc -> INVALID, đã phủ ở CHECK-A4-01
    assert degraded <= good + 1e-12, col


@pytest.mark.parametrize("col", SUB_FACTOR_INPUTS)
def test_a4_06_opportunity_unlock_not_increased_by_degraded_input(col):
    """Opportunity unlock không được TĂNG do đầu vào DEGRADED (§3, mệnh đề 14 của S001)."""
    good = compute_scores(_ind())["oscore"].iloc[0]
    degraded = compute_scores(_ind(**{col: np.nan}))["oscore"].iloc[0]
    if np.isnan(degraded):
        return
    assert opportunity_unlock(degraded) <= opportunity_unlock(good) + 1e-12, col


def test_a4_06_degraded_contribution_is_exactly_zero_not_rescaled():
    """Sub-component thiếu đóng góp ĐÚNG 0 và OSCORE KHÔNG bị chuẩn hoá lên (BT §21.1)."""
    ind = _ind(volume_ratio=np.nan)
    sf = sub_factors(ind)
    fs = compute_scores(ind)
    assert np.isnan(sf["V"].iloc[0])
    r, s7 = sf["R"].iloc[0], sf["S7"].iloc[0]
    assert fs["market_stress_score"].iloc[0] == pytest.approx(30 * (0.5 * r + 0.3 * s7))
