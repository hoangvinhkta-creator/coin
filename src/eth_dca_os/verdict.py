"""Verdict tự động + failure-signal cap — Impl Plan §5–§6, Backtest §17.

Quy tắc chặn: cả ba gate PASS nhưng BẤT KỲ FS nào TRUE -> tối đa BUILD_WITH_MODIFICATIONS.
Mapping khi gate fail (spec không liệt kê chi tiết; quy ước, ghi ở docs/CONVENTIONS.md):
Gate 1 hoặc OOS fail -> DO_NOT_BUILD (giá trị cấu trúc không có); Gate 2/3 fail -> INCONCLUSIVE.
"""
from __future__ import annotations

VERDICTS = ("BUILD", "BUILD_WITH_MODIFICATIONS", "INCONCLUSIVE", "DO_NOT_BUILD")


def decide_verdict(gate1: dict, oos: dict, gate2: dict, gate3: dict, fs: dict) -> dict:
    reasons = []
    if not gate1["pass"] or not oos["pass"]:
        v = "DO_NOT_BUILD"
        if not gate1["pass"]:
            reasons.append("Gate 1 FAIL")
        if not oos["pass"]:
            reasons.append("OOS hard condition FAIL")
    elif not gate2["pass"] or not gate3["pass"]:
        v = "INCONCLUSIVE"
        if not gate2["pass"]:
            reasons.append("Gate 2 FAIL (pre-OOS pass share)")
        if not gate3["pass"]:
            reasons.append("Gate 3 FAIL")
    else:
        if fs["any_true"]:
            v = "BUILD_WITH_MODIFICATIONS"
            trues = [k for k, x in fs["signals"].items() if x is True]
            reasons.append(f"Failure-signal cap: {', '.join(trues)} TRUE")
        else:
            v = "BUILD"
            reasons.append("Gate 1, 2, 3 PASS và không Failure Signal nào TRUE")
    if fs.get("unknown"):
        reasons.append(f"FS chưa đánh giá được: {', '.join(fs['unknown'])}")
    return {"verdict": v, "reasons": reasons,
            "can_proceed_to_app": v == "BUILD"}
