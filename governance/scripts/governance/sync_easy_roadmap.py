#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "PROJECT/PROJECT_PROGRESS.md"
TARGET = ROOT / "PROJECT/LO_TRINH_DE_HIEU.md"

MODEL = {"A":"Haiku", "B":"Sonnet", "C":"Opus", "D":"Fable", "DUYET":"Con người"}
VALID_EFFORT = {"low","medium","high","xhigh","max","-"}
TICK = {
    "DONE":"✅",
    "READY":"🟡", "IN_PROGRESS":"🟡", "IMPLEMENTED":"🟡", "VERIFYING":"🟡", "BLOCKED":"🟡",
    "NOT_PLANNED":"⬜", "PLANNED":"⬜", "DEFERRED":"⬜", "CANCELLED":"⬜",
}
EXPECTED = ["Status","Task ID","Tên việc","Mục đích","Tier","Effort","Thứ tự/phụ thuộc"]

def parse_table(text):
    m = re.search(r"(?ms)^## Overall Roadmap\s*$\n(.*?)(?=^## |\Z)", text)
    if not m:
        raise ValueError("Missing ## Overall Roadmap section")
    lines=[ln.strip() for ln in m.group(1).splitlines() if ln.strip().startswith('|')]
    if len(lines)<2:
        raise ValueError("Canonical roadmap table not found")
    rows=[]
    for ln in lines:
        cells=[c.strip() for c in ln.strip('|').split('|')]
        if all(re.fullmatch(r'-+', c) for c in cells):
            continue
        rows.append(cells)
    if not rows or rows[0] != EXPECTED:
        raise ValueError(f"Roadmap columns must be exactly: {EXPECTED}")
    data=[]
    seen=set()
    for cells in rows[1:]:
        if len(cells)!=len(EXPECTED):
            raise ValueError(f"Invalid roadmap row column count: {cells}")
        row=dict(zip(EXPECTED,cells))
        if row['Task ID'] in seen:
            raise ValueError(f"Duplicate Task ID: {row['Task ID']}")
        seen.add(row['Task ID'])
        st=row['Status'].upper(); tier=row['Tier'].upper(); effort=row['Effort'].lower()
        if st not in TICK: raise ValueError(f"Unsupported Status {row['Status']} for {row['Task ID']}")
        if tier not in MODEL: raise ValueError(f"Unsupported Tier {row['Tier']} for {row['Task ID']}")
        if effort not in VALID_EFFORT: raise ValueError(f"Unsupported Effort {row['Effort']} for {row['Task ID']}")
        if tier=='DUYET' and effort!='-': raise ValueError(f"DUYET must use Effort '-' for {row['Task ID']}")
        if tier!='DUYET' and effort=='-': raise ValueError(f"Implementation task must declare Effort for {row['Task ID']}")
        row['_status']=st; row['_tier']=tier; row['_effort']=effort
        data.append(row)
    return data

def render(rows):
    out=[
        '# LỘ TRÌNH DỰ ÁN — BẢN DỄ HIỂU','',
        '> File này dành cho người **không chuyên lập trình**.','> Nguồn sự thật: `PROJECT/PROJECT_PROGRESS.md`.','> **File này được sinh tự động — không sửa tay.**','',
        '| Tick | Tên việc | Mục đích | Mức xử lý | Thứ tự/phụ thuộc |','|---|---|---|---|---|'
    ]
    for r in rows:
        tier=r['_tier']; tier_label='Duyệt' if tier=='DUYET' else tier
        level=f"{tier_label} — {MODEL[tier]} — {r['_effort']}"
        name=f"{r['Task ID']} — {r['Tên việc']}"
        out.append(f"| {TICK[r['_status']]} | {name} | {r['Mục đích']} | {level} | {r['Thứ tự/phụ thuộc']} |")
    out += ['', '> Đồng bộ bằng `python governance/scripts/governance/sync_easy_roadmap.py`.','']
    return '\n'.join(out)

def expected_content():
    return render(parse_table(SOURCE.read_text(encoding='utf-8')))

def main():
    if not SOURCE.exists():
        print('ROADMAP SYNC: FAIL - missing PROJECT/PROJECT_PROGRESS.md'); return 1
    try: content=expected_content()
    except Exception as e:
        print(f'ROADMAP SYNC: FAIL - {e}'); return 1
    TARGET.write_text(content,encoding='utf-8')
    print(f'ROADMAP SYNC: PASS - wrote {TARGET.relative_to(ROOT)}')
    return 0
if __name__=='__main__': sys.exit(main())
