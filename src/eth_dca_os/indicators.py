"""Daily indicators — precompute MỘT LẦN và cache (Impl Plan §4).

Mọi giá trị của ngày D chỉ dùng dữ liệu tới hết nến daily D (no lookahead);
việc "chỉ áp dụng sau khi nến D đóng" do engine đảm nhiệm (Backtest §2).

Cửa sổ của MỌI indicator daily được đo bằng NGÀY LỊCH, không bằng số hàng có mặt trong
dữ liệu (WP-A4 repair cycle #1, đóng `F-S009-01`). Xem `_calendar_index`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _calendar_index(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Lịch ngày UTC LIÊN TỤC phủ [min, max] của chuỗi daily quan sát được.

    Đây là điểm sửa duy nhất của `F-S009-01`. Trước đây mọi cửa sổ ở dưới được tính theo
    VỊ TRÍ HÀNG trên chuỗi quan sát được: `np.roll(close, 7)` lấy hàng thứ `i-7`, còn
    `rolling(365)` lấy 365 HÀNG. Khi dữ liệu thiếu một ngày lịch, hàng `i-7` không còn là
    ngày `D-7` và cửa sổ "365 ngày" phủ 366 ngày lịch — nhưng kết quả vẫn là một số HỮU
    HẠN, nên `score.invalid_mask` (chỉ bắt giá trị không hữu hạn) không thấy gì, ngày đó
    được xếp GOOD/DEGRADED và đi tiếp như dữ liệu bình thường (`F-S009-01`).

    Neo chuỗi vào lịch làm ngày thiếu hiện ra thành một hàng `NaN` thật. Từ đó:
      - hàng `i-7` LẠI ĐÚNG là ngày `D-7`, nên ngày nào đủ đầu vào lịch được tính ĐÚNG;
      - cửa sổ nào phủ ngày thiếu trả `NaN` (mọi `rolling` ở dưới đều `min_periods = N`),
        tức DEGRADED/INVALID theo ST §3 + BT §18 thay vì một số hữu hạn SAI.
    Không có lớp validity thứ hai nào được dựng: `score.invalid_mask` sẵn có xử lý phần
    còn lại, vì `close` / `return7` / `adr30` nay thực sự là `NaN` khi thiếu đầu vào.

    Spec: ST §1.1 ("365 ngày gần nhất"), ST §1.3 (`30d_ago`), ST §17 (`Return7D`),
    BT §2 ("365 ngày hợp lệ"). ST §17.2 nói "96 nến 15m" khi thực sự muốn đếm theo nến —
    nên đơn vị NGÀY ở nhóm daily là lựa chọn đã ghi, không phải chỗ để ngỏ.

    Chuỗi KHÔNG có lỗ hổng cho ra đúng chỉ mục cũ, nên dữ liệu sạch không đổi kết quả.
    """
    if len(idx) == 0:
        return idx
    return pd.date_range(idx.min(), idx.max(), freq="D", tz="UTC")


def _wilder_rsi_contiguous(close: np.ndarray, period: int) -> np.ndarray:
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.full_like(close, np.nan)
    avg_loss = np.full_like(close, np.nan)
    if len(close) <= period:
        return np.full_like(close, np.nan)
    avg_gain[period] = gain[1:period + 1].mean()
    avg_loss[period] = loss[1:period + 1].mean()
    for i in range(period + 1, len(close)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i]) / period
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i]) / period
    rs = avg_gain / np.where(avg_loss == 0, np.nan, avg_loss)
    rsi = 100 - 100 / (1 + rs)
    rsi = np.where(np.isnan(rsi) & (avg_loss == 0) & ~np.isnan(avg_gain), 100.0, rsi)
    return rsi


def wilder_rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    """RSI Wilder trên daily close, tính riêng cho từng DẢI NGÀY LỊCH LIÊN TỤC.

    Wilder là một hồi quy: giá trị ngày D mang theo trạng thái làm mượt của toàn bộ lịch
    sử liền trước. Trạng thái đó không bắc qua được một ngày lịch vắng mặt, nên mỗi dải
    ngày liên tục được warm-up lại từ đầu; `period` ngày đầu của mỗi dải là `NaN`
    (chưa đủ dữ liệu), KHÔNG phải một số hữu hạn dựng trên chuỗi đã đứt.

    Chuỗi không có `NaN` chỉ có MỘT dải, nên kết quả trùng khớp từng chữ số với trước.
    """
    close = np.asarray(close, dtype=float)
    out = np.full(len(close), np.nan)
    valid = np.isfinite(close)
    if not valid.any():
        return out
    # Biên của các dải liên tục: nơi cờ hợp lệ đổi giá trị.
    edges = np.flatnonzero(np.diff(valid.astype(np.int8)) != 0) + 1
    for lo, hi in zip(np.r_[0, edges], np.r_[edges, len(close)]):
        if valid[lo]:
            out[lo:hi] = _wilder_rsi_contiguous(close[lo:hi], period)
    return out


def _rolling_percentile_of_last(values: np.ndarray, window: int) -> np.ndarray:
    """Tỷ lệ 0–1 các giá trị trong `window` gần nhất THẤP HƠN giá trị hiện tại.

    Cửa sổ thiếu bất kỳ ngày lịch nào (`NaN`) trả `NaN`: phép so sánh với `NaN` luôn
    False, nên nếu không chặn ở đây, một ngày vắng mặt sẽ âm thầm bị đếm là "không thấp
    hơn" và percentile ra một số hữu hạn SAI — đúng hình dạng lỗi của `F-S009-01`.
    """
    n = len(values)
    out = np.full(n, np.nan)
    for i in range(window - 1, n):
        w = values[i - window + 1: i + 1]
        if np.isnan(w).any():
            continue
        out[i] = np.count_nonzero(w < values[i]) / window
    return out


def compute_daily_indicators(eth1d: pd.DataFrame, btc1d: pd.DataFrame) -> pd.DataFrame:
    """Trả về DataFrame indexed theo NGÀY LỊCH UTC LIÊN TỤC với mọi indicator bắt buộc.

    Chỉ mục là lịch ngày liên tục phủ [ngày đầu, ngày cuối] quan sát được, nên một ngày
    daily vắng mặt xuất hiện thành một hàng `NaN` thay vì biến mất khỏi chỉ mục — xem
    `_calendar_index`. Độ phủ ở HAI ĐẦU khoảng được yêu cầu không thuộc hàm này; nó đã do
    `data.dataset.official_eligibility` xử lý (CHECK-A4-10) và không bị dựng lại ở đây.
    """
    eth = eth1d.set_index(pd.to_datetime(eth1d["open_time"], utc=True).dt.normalize())
    btc = btc1d.set_index(pd.to_datetime(btc1d["open_time"], utc=True).dt.normalize())
    cal = _calendar_index(eth.index)
    eth = eth.reindex(cal)
    df = pd.DataFrame(index=cal)
    close = eth["close"].to_numpy(float)
    df["close"] = close
    df["btc_close"] = btc["close"].reindex(cal).to_numpy(float)

    s_close = eth["close"]
    df["high365"] = s_close.rolling(365, min_periods=365).max().to_numpy()
    df["dd365"] = close / df["high365"].to_numpy() - 1
    df["ma200"] = s_close.rolling(200, min_periods=200).mean().to_numpy()
    df["ma_ratio"] = close / df["ma200"].to_numpy()
    df["ma200_slope"] = pd.Series(df["ma200"].to_numpy(), index=df.index).diff().to_numpy()
    df["percentile365"] = _rolling_percentile_of_last(close, 365)

    df["rsi14"] = wilder_rsi(close, 14)
    df["return7"] = close / np.roll(close, 7) - 1
    df.iloc[:7, df.columns.get_loc("return7")] = np.nan
    vol = eth["volume"]
    df["vol7"] = vol.rolling(7, min_periods=7).mean().to_numpy()
    df["vol90"] = vol.rolling(90, min_periods=90).mean().to_numpy()
    df["volume_ratio"] = df["vol7"] / df["vol90"]
    # Diagnostic volume z-score 365 ngày (Strategy §2.4) — không dùng cho production factor
    vmean = vol.rolling(365, min_periods=365).mean()
    vstd = vol.rolling(365, min_periods=365).std()
    df["volume_z365"] = ((vol - vmean) / vstd).to_numpy()

    daily_ret = pd.Series(close, index=df.index).pct_change()
    df["adr30"] = daily_ret.abs().rolling(30, min_periods=30).mean().to_numpy()

    ethbtc = close / df["btc_close"].to_numpy()
    df["ethbtc"] = ethbtc
    df["ethbtc_return30"] = ethbtc / np.roll(ethbtc, 30) - 1
    df.iloc[:30, df.columns.get_loc("ethbtc_return30")] = np.nan
    df["ethbtc_percentile180"] = _rolling_percentile_of_last(ethbtc, 180)
    return df
