"""Failure Signals FS-01..FS-12 và verdict cap — Backtest §17, Impl Plan §6.

Mỗi signal đánh giá từ artifact đã tính; thiếu input -> None (UNKNOWN), không đoán.

Hợp đồng đầu ra với `verdict.py` (WP-B1 lát cắt DEC-026, đóng F-S015-01 / CHECK-B1-01):

* `signals[k]` chỉ nhận ba giá trị: `True` / `False` (bool THUẦN Python) hoặc `None`.
  `verdict.py` và chính file này kiểm bằng `x is True` — phép so danh tính với singleton
  của Python — mà `numpy.bool_(True) is True` cho False. Nên mọi signal được chuẩn hoá
  kiểu NGAY TẠI nơi dựng dict, không để kiểu của input (`numpy.float64` từ `oos_ae`,
  `numpy.bool_` từ diagnostics…) quyết định một signal TRUE có "được nhìn thấy" hay không.
* `any_true` là CỜ CHẶN mà `verdict.py` đọc để giới hạn verdict ở BUILD_WITH_MODIFICATIONS.
  Nó bật khi có signal TRUE — HOẶC khi còn signal UNKNOWN: BT §17 liệt kê FS-01…FS-12 mà
  không đánh dấu mục nào tuỳ chọn, nên "chưa đánh giá được" không phải bằng chứng "không
  TRUE"; verdict BUILD không được phát ra trên bằng chứng chưa đủ (fail-closed). Tên khoá
  giữ nguyên vì là hợp đồng với `verdict.py`; `cap_cause` nói rõ vì sao cờ bật.
"""
from __future__ import annotations

import math
import numbers

FS_DESCRIPTIONS = {
    "FS-01": "V2 tích lũy ít ETH hơn Monthly DCA ở phần lớn gate window",
    "FS-02": "Opportunity reserve thường xuyên chạm cap và nằm im",
    "FS-03": "Lợi thế biến mất sau khi loại một tháng hoặc một quý lớn nhất",
    "FS-04": "Redundancy nghiêm trọng: VIF > 10 hoặc corr > 0.85",
    "FS-05": "Score lưỡng cực: >70% quan sát trong hai bucket",
    "FS-06": "Config kề nhau đảo ngược kết luận",
    "FS-07": "Cash ratio cao nhưng không có accumulation benefit",
    "FS-08": "Random control bao trùm/vượt V2 (không vượt P95)",
    "FS-09": "ImplementationShortfallPP > 3.0 pp",
    "FS-10": "Gate2_OOS_PassShare < 50%",
    "FS-11": "OOS AccumulationEfficiency < 100%",
    "FS-12": "Lợi thế tập trung vào một crash/regime duy nhất",
}


def _flag(value) -> bool | None:
    """Chuẩn hoá một signal về `bool` thuần Python; `None` (UNKNOWN) giữ nguyên là `None`.

    Đây là điểm sửa gốc của F-S015-01: ép kiểu tại nguồn để cả `any_true` ở đây lẫn danh
    sách tên trong `verdict.py` (cùng dùng `is True`) đều thấy được signal TRUE, không đổi
    một ngưỡng nào.
    """
    return None if value is None else bool(value)


def _numeric_and_finite(x) -> bool:
    """E2-B1-F01 (bản sửa lần hai, fresh E2 `E2-WP-B1-003`): bản trước chỉ loại `None`/NaN,
    còn để lọt `+inf`/`-inf` (`math.isnan(inf)` là `False`) — một P95/`v2_eth` vô hạn vẫn so
    sánh được và tạo ra một `beats_*` "thắng"/"thua" giả. Chỉ số THỰC HỮU HẠN mới là bằng
    chứng dùng được cho một phép so sánh ngưỡng.

    Loại rõ ràng, không coerce:
    - `None`, NaN, `+inf`, `-inf` (`math.isfinite` loại cả NaN lẫn hai vô cực, khác
      `isnan` chỉ loại NaN);
    - chuỗi/objekt không phải số (`isinstance(x, numbers.Real)` — kiểm TRƯỚC khi ép kiểu,
      không dựa vào `float()` raise lỗi để phát hiện);
    - `bool`/`numpy.bool_`: `bool` là subclass của `int` trong Python (`float(True) == 1.0`)
      nhưng `True`/`False` không phải một PHÉP ĐO tài chính — loại tường minh bằng
      `isinstance(x, bool)`. `numpy.bool_` không phải subclass của `bool` nhưng CŨNG không
      phải instance của `numbers.Real` (khác `numpy.float64`, có đăng ký ABC này) nên đã bị
      loại tự nhiên bởi điều kiện `numbers.Real` — không cần thêm nhánh riêng.
    """
    if x is None or isinstance(x, bool):
        return False
    if not isinstance(x, numbers.Real):
        return False
    return math.isfinite(float(x))


def evaluate_failure_signals(*, gate1_windows: dict | None = None,
                             opportunity_cap_hit_share: float | None = None,
                             concentration: dict | None = None,
                             vif_any_severe: bool | None = None,
                             corr_high_redundancy: bool | None = None,
                             score_bimodal: bool | None = None,
                             adjacent_config_flip: bool | None = None,
                             avg_cash_ratio: float | None = None,
                             gate1_primary_ae: float | None = None,
                             v2_eth: float | None = None,
                             random_timing_p95: float | None = None,
                             random_anchor_p95: float | None = None,
                             shortfall_pp: float | None = None,
                             gate2_oos_pass_share: float | None = None,
                             oos_ae: float | None = None,
                             regime_advantage_share: float | None = None) -> dict:
    fs: dict[str, bool | None] = {}

    if gate1_windows is not None:
        below = sum(1 for v in gate1_windows.values() if v < 100.0)
        fs["FS-01"] = _flag(below > len(gate1_windows) / 2)
    else:
        fs["FS-01"] = None

    fs["FS-02"] = _flag(opportunity_cap_hit_share > 0.5) if opportunity_cap_hit_share is not None else None

    if concentration is not None:
        fs["FS-03"] = _flag(concentration.get("ae_ex_month", 100.0) < 100.0
                            or concentration.get("ae_ex_quarter", 100.0) < 100.0)
    else:
        fs["FS-03"] = None

    if vif_any_severe is not None or corr_high_redundancy is not None:
        fs["FS-04"] = bool(vif_any_severe) or bool(corr_high_redundancy)
    else:
        fs["FS-04"] = None

    fs["FS-05"] = _flag(score_bimodal)
    fs["FS-06"] = _flag(adjacent_config_flip)

    if avg_cash_ratio is not None and gate1_primary_ae is not None:
        fs["FS-07"] = _flag(avg_cash_ratio > 0.30 and gate1_primary_ae < 102.0)
    else:
        fs["FS-07"] = None

    # E2-B1-F01 (WP-B1 fresh E2, 2026-09-04): trước đây chỉ đòi MỘT trong hai P95, rồi coi
    # control còn thiếu là "V2 tự động beat" (vacuous true) — một control vắng mặt không
    # phải bằng chứng "V2 thắng nó". FS-08 cần CẢ HAI P95 (và `v2_eth`) mới được coi là
    # known; thiếu bất kỳ input nào trong ba -> None (UNKNOWN), đúng hợp đồng fail-closed
    # của cả module (xem docstring đầu file) thay vì tự chế một ngoại lệ chỉ cho FS-08.
    if (_numeric_and_finite(v2_eth) and _numeric_and_finite(random_timing_p95)
            and _numeric_and_finite(random_anchor_p95)):
        beats_f = v2_eth > random_timing_p95
        beats_g = v2_eth > random_anchor_p95
        fs["FS-08"] = _flag(not (beats_f and beats_g))
    else:
        fs["FS-08"] = None

    fs["FS-09"] = _flag(shortfall_pp > 3.0) if shortfall_pp is not None else None
    fs["FS-10"] = _flag(gate2_oos_pass_share < 0.50) if gate2_oos_pass_share is not None else None
    fs["FS-11"] = _flag(oos_ae < 100.0) if oos_ae is not None else None
    fs["FS-12"] = _flag(regime_advantage_share > 0.80) if regime_advantage_share is not None else None

    trues = [k for k, v in fs.items() if v is True]
    unknown = [k for k, v in fs.items() if v is None]
    # Cờ chặn BT §17: TRUE hoặc UNKNOWN đều chặn BUILD (xem docstring module). `cap_cause`
    # tồn tại vì `verdict.py` chỉ in được tên các signal TRUE — khi cờ bật do UNKNOWN, nguồn
    # sự thật máy đọc được về nguyên nhân phải nằm ở đây.
    any_true = bool(trues) or bool(unknown)
    cap_cause = ("TRUE_AND_UNKNOWN" if trues and unknown
                 else "TRUE" if trues else "UNKNOWN" if unknown else None)
    return {"signals": fs, "any_true": any_true, "true": trues, "unknown": unknown,
            "cap_cause": cap_cause}
