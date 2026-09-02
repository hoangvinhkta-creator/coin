"""WP-A4 repair cycle #1 — `CHECK-A4-11`: cửa sổ indicator daily theo NGÀY LỊCH.

Đóng `F-S009-01` (`docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md`).

Mệnh đề được khoá ở đây, và KHÔNG rộng hơn: khi một ngày lịch daily bắt buộc vắng mặt,
indicator bị ảnh hưởng phải hoặc được tính ĐÚNG theo lịch, hoặc trả `NaN` → DEGRADED /
INVALID theo ST §3 + BT §18. Nó KHÔNG được trả một giá trị HỮU HẠN SAI rồi đi tiếp như
dữ liệu bình thường — đó chính là hình dạng lỗi mà `F-S009-01` ghi nhận.

Mọi test chạy trên hàm production `compute_daily_indicators` (và `Prepared` cho CASE H).
Không mock indicator, không mock eligibility, không sửa tay `lineage.json`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from eth_dca_os.indicators import compute_daily_indicators, wilder_rsi
from eth_dca_os.score import REQUIRED_DAILY_INDICATORS, compute_scores, invalid_mask

START = pd.Timestamp("2019-01-01", tz="UTC")
N_DAYS = 520
SEED = 20260901

#: Ngày đọc kết quả. Đủ xa điểm đầu để `high365` / `ma200` / `percentile365` đã ấm.
READ_AT = START + pd.Timedelta(days=470)

#: Các indicator daily nằm trên production path và CÙNG root cause row-position/calendar-day
#: (`F-S009-01` §II.2 đo được bốn cái đầu; bốn cái sau cùng cơ chế cửa sổ).
AFFECTED_INDICATORS = ("return7", "adr30", "rsi14", "ethbtc_return30",
                       "ma200", "high365", "percentile365", "ethbtc_percentile180")


# --------------------------------------------------------------- dựng dữ liệu

def _series(n: int = N_DAYS, seed: int = SEED):
    """Chuỗi daily ETH/BTC tất định, có biến động thật (không phẳng).

    Biến động là bắt buộc: trên một chuỗi gần tuyến tính, một ngày lệch chỉ đổi chữ số
    thứ mười và test sẽ "xanh" vì phép so sánh chứ không vì hành vi đúng.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range(START, periods=n, freq="D", tz="UTC")
    ret = rng.normal(0.0006, 0.035, size=n)
    eth_close = 130.0 * np.exp(np.cumsum(ret))
    btc_close = 6000.0 * np.exp(np.cumsum(0.55 * ret + rng.normal(0, 0.02, size=n)))
    vol = 900.0 * np.exp(rng.normal(0, 0.3, size=n))
    eth = pd.DataFrame({"open_time": idx, "open": eth_close, "high": eth_close * 1.01,
                        "low": eth_close * 0.99, "close": eth_close, "volume": vol})
    btc = pd.DataFrame({"open_time": idx, "open": btc_close, "high": btc_close * 1.01,
                        "low": btc_close * 0.99, "close": btc_close, "volume": vol})
    return eth, btc


def _drop_days(df: pd.DataFrame, days) -> pd.DataFrame:
    """Bỏ hẳn các NGÀY LỊCH khỏi series — đúng hình dạng một nến daily thiếu."""
    keep = ~pd.to_datetime(df["open_time"], utc=True).dt.normalize().isin(
        [pd.Timestamp(d, tz="UTC") if pd.Timestamp(d).tzinfo is None else pd.Timestamp(d)
         for d in days])
    return df[keep].reset_index(drop=True)


def _both(days=()):
    """(indicators chuỗi ĐẦY ĐỦ, indicators chuỗi THIẾU `days`) — cùng dữ liệu gốc."""
    eth, btc = _series()
    full = compute_daily_indicators(eth, btc)
    gapped = compute_daily_indicators(_drop_days(eth, days), _drop_days(btc, days))
    return full, gapped


def _finite_and_different(full, gapped, day, col) -> bool:
    """Đúng hình dạng lỗi `F-S009-01`: hữu hạn, không NaN, nhưng KHÁC giá trị đúng."""
    if day not in gapped.index:
        return False
    a, b = float(full.loc[day, col]), float(gapped.loc[day, col])
    return np.isfinite(b) and not (np.isnan(a) and np.isnan(b)) and a != b


# ============================================================ CASE A
# Chuỗi daily liên tục, đầy đủ -> không regression.

def test_case_a_contiguous_series_index_unchanged():
    eth, btc = _series()
    ind = compute_daily_indicators(eth, btc)
    observed = pd.to_datetime(eth["open_time"], utc=True).dt.normalize()
    assert list(ind.index) == list(observed), "chuỗi liên tục không được sinh thêm hàng nào"


def test_case_a_contiguous_series_has_no_nan_in_warm_indicators():
    eth, btc = _series()
    ind = compute_daily_indicators(eth, btc)
    row = ind.loc[READ_AT]
    for col in AFFECTED_INDICATORS:
        assert np.isfinite(row[col]), f"{col} phải hữu hạn trên chuỗi đầy đủ đã ấm"


@pytest.mark.parametrize("col", AFFECTED_INDICATORS)
def test_case_a_matches_calendar_oracle(col):
    """Đối chứng độc lập: oracle tính theo NHÃN NGÀY, không theo vị trí hàng."""
    eth, btc = _series()
    ind = compute_daily_indicators(eth, btc)
    close = pd.Series(eth["close"].to_numpy(float),
                      index=pd.to_datetime(eth["open_time"], utc=True).dt.normalize())
    btc_close = pd.Series(btc["close"].to_numpy(float), index=close.index)
    got = float(ind.loc[READ_AT, col])
    if col == "return7":
        want = close[READ_AT] / close[READ_AT - pd.Timedelta(days=7)] - 1
    elif col == "ethbtc_return30":
        eb = close / btc_close
        want = eb[READ_AT] / eb[READ_AT - pd.Timedelta(days=30)] - 1
    elif col == "ma200":
        want = close[READ_AT - pd.Timedelta(days=199): READ_AT].mean()
    elif col == "high365":
        want = close[READ_AT - pd.Timedelta(days=364): READ_AT].max()
    elif col == "adr30":
        want = close.pct_change()[READ_AT - pd.Timedelta(days=29): READ_AT].abs().mean()
    elif col == "percentile365":
        w = close[READ_AT - pd.Timedelta(days=364): READ_AT]
        want = float((w < close[READ_AT]).sum()) / 365
    elif col == "ethbtc_percentile180":
        eb = close / btc_close
        w = eb[READ_AT - pd.Timedelta(days=179): READ_AT]
        want = float((w < eb[READ_AT]).sum()) / 180
    else:                                    # rsi14 — oracle là chính công thức Wilder
        want = wilder_rsi(close.to_numpy(float), 14)[list(close.index).index(READ_AT)]
    assert got == pytest.approx(float(want), rel=1e-12, abs=1e-12)


# ============================================================ CASE B
# Thiếu ĐÚNG MỘT ngày nằm trong cửa sổ return7 -> không được trả finite wrong value.

def test_case_b_missing_day_inside_return7_window_is_not_finite_wrong():
    missing = READ_AT - pd.Timedelta(days=3)          # nằm giữa cửa sổ D-7..D
    full, gapped = _both([missing])
    assert not _finite_and_different(full, gapped, READ_AT, "return7")


def test_case_b_return7_is_correct_because_d_minus_7_still_present():
    """Ngày thiếu KHÔNG phải `D-7`, nên `return7` vẫn tính được và phải ĐÚNG THEO LỊCH."""
    missing = READ_AT - pd.Timedelta(days=3)
    full, gapped = _both([missing])
    assert float(gapped.loc[READ_AT, "return7"]) == pytest.approx(
        float(full.loc[READ_AT, "return7"]), rel=1e-12, abs=1e-15)


def test_case_b_windows_covering_the_gap_go_nan_not_finite_wrong():
    """Cửa sổ nào PHỦ ngày thiếu phải ra `NaN` — DEGRADED/INVALID theo ST §3 + BT §18."""
    missing = READ_AT - pd.Timedelta(days=3)
    full, gapped = _both([missing])
    for col in ("adr30", "rsi14", "ma200", "high365", "percentile365",
                "ethbtc_percentile180"):
        assert np.isnan(float(gapped.loc[READ_AT, col])), f"{col} phải NaN, không hữu hạn"


def test_case_b_two_point_ratio_not_covering_the_gap_stays_correct():
    """`ethbtc_return30` chỉ đọc HAI ngày lịch (`D` và `D-30`), không đọc cả dải ở giữa.

    Vế thứ nhất của Completion Gate: indicator KHÔNG bị ngày thiếu chạm vào phải được
    tính ĐÚNG, không bị NaN oan. Nếu thiếu test này, một bản sửa "NaN hoá tất cả" cũng
    sẽ qua được toàn bộ các test còn lại — và đó là một defect khác, không phải bản sửa.
    """
    missing = READ_AT - pd.Timedelta(days=3)          # nằm GIỮA D-30 và D
    full, gapped = _both([missing])
    assert np.isfinite(float(gapped.loc[READ_AT, "ethbtc_return30"]))
    assert float(gapped.loc[READ_AT, "ethbtc_return30"]) == pytest.approx(
        float(full.loc[READ_AT, "ethbtc_return30"]), rel=1e-12, abs=1e-15)


@pytest.mark.parametrize("col", AFFECTED_INDICATORS)
def test_case_b_no_affected_indicator_is_finite_wrong(col):
    missing = READ_AT - pd.Timedelta(days=3)
    full, gapped = _both([missing])
    assert not _finite_and_different(full, gapped, READ_AT, col)


def test_case_b_missing_day_is_visible_in_the_index_not_erased():
    """Ngày thiếu phải HIỆN RA thành một hàng, không biến mất khỏi chỉ mục.

    Biến mất chính là cơ chế của `F-S009-01`: chỉ mục co lại, hàng `i-7` không còn là
    ngày `D-7`, và không ai nhìn thấy điều đó xảy ra.
    """
    missing = READ_AT - pd.Timedelta(days=3)
    _, gapped = _both([missing])
    assert missing in gapped.index
    assert np.isnan(float(gapped.loc[missing, "close"]))


# ============================================================ CASE C
# Thiếu một ngày NGOÀI cửa sổ của indicator đang đọc -> không invalid sai phạm vi.

def test_case_c_gap_outside_window_does_not_touch_return7_or_adr30():
    missing = READ_AT - pd.Timedelta(days=60)         # ngoài cả return7 (7) lẫn adr30 (30)
    full, gapped = _both([missing])
    for col in ("return7", "adr30"):
        assert np.isfinite(float(gapped.loc[READ_AT, col]))
        assert float(gapped.loc[READ_AT, col]) == pytest.approx(
            float(full.loc[READ_AT, col]), rel=1e-12, abs=1e-15)


def test_case_c_gap_outside_window_leaves_the_day_valid():
    missing = READ_AT - pd.Timedelta(days=60)
    _, gapped = _both([missing])
    i = list(gapped.index).index(READ_AT)
    assert not bool(invalid_mask(gapped)[i]), "ngày ngoài phạm vi gap không được INVALID"


def test_case_c_invalid_span_is_bounded_by_the_longest_required_window():
    """Bóng INVALID của một ngày thiếu chỉ dài bằng cửa sổ REQUIRED dài nhất (`adr30` = 30).

    Khoá cả hai phía: trong bóng thì INVALID, ngay sau bóng thì hết INVALID. Thiếu vế
    thứ hai, một bản sửa "INVALID vĩnh viễn" cũng sẽ qua được test.
    """
    missing = START + pd.Timedelta(days=400)
    _, gapped = _both([missing])
    bad = invalid_mask(gapped)
    idx = list(gapped.index)
    assert bool(bad[idx.index(missing + pd.Timedelta(days=30))])
    assert not bool(bad[idx.index(missing + pd.Timedelta(days=31))])


# ============================================================ CASE D
# Lỗ hổng NHIỀU NGÀY -> fail/degraded/invalid đúng, không có giá trị hữu hạn sai.

def test_case_d_multi_day_gap_produces_no_finite_wrong_value():
    missing = [READ_AT - pd.Timedelta(days=k) for k in (5, 4, 3)]
    full, gapped = _both(missing)
    for col in AFFECTED_INDICATORS:
        assert not _finite_and_different(full, gapped, READ_AT, col)


def test_case_d_multi_day_gap_marks_every_missing_day_invalid():
    missing = [READ_AT - pd.Timedelta(days=k) for k in (5, 4, 3)]
    _, gapped = _both(missing)
    bad = invalid_mask(gapped)
    idx = list(gapped.index)
    for d in missing:
        assert d in gapped.index
        assert bool(bad[idx.index(d)]), f"{d.date()} thiếu hoàn toàn mà không INVALID"


def test_case_d_read_day_after_multi_day_gap_is_invalid():
    missing = [READ_AT - pd.Timedelta(days=k) for k in (5, 4, 3)]
    _, gapped = _both(missing)
    i = list(gapped.index).index(READ_AT)
    assert bool(invalid_mask(gapped)[i])


# ============================================================ CASE E
# Gap ở BIÊN ĐẦU cửa sổ -> đúng semantic (không lệch một ngày).

def test_case_e_gap_exactly_at_d_minus_7_makes_return7_nan():
    missing = READ_AT - pd.Timedelta(days=7)          # đúng mẫu số của Return7D
    _, gapped = _both([missing])
    assert np.isnan(float(gapped.loc[READ_AT, "return7"]))


def test_case_e_gap_at_d_minus_8_leaves_return7_correct():
    """Ranh giới off-by-one: `D-8` nằm NGOÀI cửa sổ `return7`, không được làm nó NaN."""
    missing = READ_AT - pd.Timedelta(days=8)
    full, gapped = _both([missing])
    assert float(gapped.loc[READ_AT, "return7"]) == pytest.approx(
        float(full.loc[READ_AT, "return7"]), rel=1e-12, abs=1e-15)


def test_case_e_gap_exactly_at_d_minus_30_makes_ethbtc_return30_nan():
    missing = READ_AT - pd.Timedelta(days=30)
    _, gapped = _both([missing])
    assert np.isnan(float(gapped.loc[READ_AT, "ethbtc_return30"]))


def test_case_e_gap_at_d_minus_31_leaves_ethbtc_return30_correct():
    missing = READ_AT - pd.Timedelta(days=31)
    full, gapped = _both([missing])
    assert float(gapped.loc[READ_AT, "ethbtc_return30"]) == pytest.approx(
        float(full.loc[READ_AT, "ethbtc_return30"]), rel=1e-12, abs=1e-15)


# ============================================================ CASE F
# Gap ở BIÊN CUỐI / vùng hiện tại -> đúng semantic.

def test_case_f_gap_on_the_read_day_itself_is_invalid_not_finite():
    _, gapped = _both([READ_AT])
    assert READ_AT in gapped.index
    assert np.isnan(float(gapped.loc[READ_AT, "close"]))
    assert bool(invalid_mask(gapped)[list(gapped.index).index(READ_AT)])


def test_case_f_gap_on_previous_day_does_not_produce_finite_wrong_value():
    missing = READ_AT - pd.Timedelta(days=1)
    full, gapped = _both([missing])
    for col in AFFECTED_INDICATORS:
        assert not _finite_and_different(full, gapped, READ_AT, col)


def test_case_f_gap_at_series_tail_does_not_extend_the_calendar():
    """Thiếu ở ĐUÔI không quan sát được từ đây, và hàm này KHÔNG được đoán thêm ngày.

    Độ phủ hai đầu là việc của `official_eligibility` (CHECK-A4-10); dựng lại nó ở đây
    sẽ là hệ validity thứ hai — điều `DEC-016` cấm.
    """
    eth, btc = _series()
    last = pd.to_datetime(eth["open_time"], utc=True).dt.normalize().max()
    cut = _drop_days(eth, [last])
    ind = compute_daily_indicators(cut, _drop_days(btc, [last]))
    assert ind.index.max() == last - pd.Timedelta(days=1)


# ============================================================ CASE G
# Đối chứng dương: dữ liệu SẠCH -> BEFORE == AFTER, từng chữ số.

def _legacy_row_position(eth1d: pd.DataFrame, btc1d: pd.DataFrame) -> pd.DataFrame:
    """Công thức THEO VỊ TRÍ HÀNG đúng như trước bản sửa (`06b381c..cb75f9d`).

    Giữ nguyên ở đây làm oracle non-regression: trên chuỗi liên tục, vị trí hàng VÀ ngày
    lịch trùng nhau, nên bản sửa phải cho kết quả trùng khớp từng chữ số. Nếu ai đó vô
    tình đổi công thức (chứ không chỉ đổi chỉ mục), test này đỏ.
    """
    eth = eth1d.set_index(pd.to_datetime(eth1d["open_time"], utc=True).dt.normalize())
    btc = btc1d.set_index(pd.to_datetime(btc1d["open_time"], utc=True).dt.normalize())
    out = pd.DataFrame(index=eth.index)
    close = eth["close"].to_numpy(float)
    out["close"] = close
    out["btc_close"] = btc["close"].reindex(eth.index).to_numpy(float)
    s = eth["close"]
    out["high365"] = s.rolling(365, min_periods=365).max().to_numpy()
    out["dd365"] = close / out["high365"].to_numpy() - 1
    out["ma200"] = s.rolling(200, min_periods=200).mean().to_numpy()
    out["ma_ratio"] = close / out["ma200"].to_numpy()
    out["return7"] = close / np.roll(close, 7) - 1
    out.iloc[:7, out.columns.get_loc("return7")] = np.nan
    vol = eth["volume"]
    out["vol7"] = vol.rolling(7, min_periods=7).mean().to_numpy()
    out["vol90"] = vol.rolling(90, min_periods=90).mean().to_numpy()
    out["volume_ratio"] = out["vol7"] / out["vol90"]
    dr = pd.Series(close, index=out.index).pct_change()
    out["adr30"] = dr.abs().rolling(30, min_periods=30).mean().to_numpy()
    eb = close / out["btc_close"].to_numpy()
    out["ethbtc"] = eb
    out["ethbtc_return30"] = eb / np.roll(eb, 30) - 1
    out.iloc[:30, out.columns.get_loc("ethbtc_return30")] = np.nan
    return out


@pytest.mark.parametrize("col", ["close", "btc_close", "high365", "dd365", "ma200",
                                 "ma_ratio", "return7", "vol7", "vol90", "volume_ratio",
                                 "adr30", "ethbtc", "ethbtc_return30"])
def test_case_g_clean_data_is_bit_identical_to_row_position_result(col):
    eth, btc = _series()
    after = compute_daily_indicators(eth, btc)
    before = _legacy_row_position(eth, btc)
    a, b = after[col].to_numpy(float), before[col].to_numpy(float)
    assert np.array_equal(a, b, equal_nan=True), f"{col} trôi trên dữ liệu sạch"


def test_case_g_clean_data_percentile_and_rsi_unchanged():
    eth, btc = _series()
    after = compute_daily_indicators(eth, btc)
    close = eth["close"].to_numpy(float)
    # percentile theo vị trí hàng == theo lịch khi chuỗi liên tục
    n = len(close)
    want = np.full(n, np.nan)
    for i in range(364, n):
        w = close[i - 364: i + 1]
        want[i] = np.count_nonzero(w < close[i]) / 365
    assert np.array_equal(after["percentile365"].to_numpy(float), want, equal_nan=True)
    assert np.array_equal(after["rsi14"].to_numpy(float), wilder_rsi(close, 14),
                          equal_nan=True)


def test_case_g_clean_data_scores_unchanged():
    """Đối chứng ở tầng QUYẾT ĐỊNH, không chỉ ở tầng indicator.

    Trên dữ liệu SẠCH, ngày INVALID duy nhất là warm-up đầu chuỗi (`adr30` cần 30 ngày,
    `return7` cần 7) — đúng như TRƯỚC bản sửa. Bản sửa không được sinh thêm một ngày
    INVALID nào ngoài đó.
    """
    eth, btc = _series()
    after = compute_daily_indicators(eth, btc)
    before = _legacy_row_position(eth, btc)
    sc_after = compute_scores(after)
    invalid_after = np.flatnonzero(invalid_mask(after))
    invalid_before = np.flatnonzero(invalid_mask(before))
    assert np.array_equal(invalid_after, invalid_before), "tập ngày INVALID trôi trên dữ liệu sạch"
    assert list(invalid_after) == list(range(30)), "chỉ warm-up 30 ngày đầu là INVALID"
    assert int((sc_after["data_quality"] == "GOOD").sum()) > 0
    assert not sc_after["oscore"].iloc[30:].isna().any()


# ============================================================ CASE H
# Tích hợp với invalid_mask / Prepared -> ngày bị ảnh hưởng không đi tiếp như official.

def test_case_h_affected_day_cannot_form_a_valid_decision():
    missing = READ_AT - pd.Timedelta(days=3)
    _, gapped = _both([missing])
    sc = compute_scores(gapped)
    assert sc.loc[READ_AT, "data_quality"] == "INVALID"
    assert np.isnan(float(sc.loc[READ_AT, "oscore"]))


def test_case_h_before_the_fix_the_same_day_would_have_been_usable():
    """Khoá lại đúng khoảng cách mà `F-S009-01` mô tả.

    Luật CŨ (chỉ mục theo hàng) cho ngày này một `oscore` HỮU HẠN và `data_quality` không
    INVALID — tức nó đi tiếp như dữ liệu bình thường. Nếu ai hoàn nguyên bản sửa, test
    `test_case_h_affected_day_cannot_form_a_valid_decision` sẽ đỏ, còn test này ghi lại
    lý do vì sao nó phải đỏ.
    """
    eth, btc = _series()
    missing = READ_AT - pd.Timedelta(days=3)
    legacy = _legacy_row_position(_drop_days(eth, [missing]), _drop_days(btc, [missing]))
    assert READ_AT in legacy.index
    assert np.isfinite(float(legacy.loc[READ_AT, "return7"]))
    assert not bool(invalid_mask(legacy)[list(legacy.index).index(READ_AT)])
    # ... và giá trị hữu hạn đó KHÁC giá trị đúng theo lịch
    full = compute_daily_indicators(eth, btc)
    assert float(legacy.loc[READ_AT, "return7"]) != float(full.loc[READ_AT, "return7"])


def test_case_h_required_indicator_nan_is_what_drives_invalid():
    """Đường dẫn hệ quả phải đi qua `REQUIRED_DAILY_INDICATORS` sẵn có, không qua cơ chế mới."""
    missing = READ_AT - pd.Timedelta(days=3)
    _, gapped = _both([missing])
    nan_required = [c for c in REQUIRED_DAILY_INDICATORS
                    if not np.isfinite(float(gapped.loc[READ_AT, c]))]
    assert nan_required, "phải có ít nhất một indicator BẮT BUỘC là NaN"
    assert bool(invalid_mask(gapped)[list(gapped.index).index(READ_AT)])
