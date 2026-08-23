#!/usr/bin/env python3
from pathlib import Path
import re, sys
sys.path.insert(0,str(Path(__file__).parent))
from routing_engine import route
ROOT=Path(__file__).resolve().parents[3]
files=list((ROOT/'docs/tasks').glob('*.md'))
errors=[]; checked=0
for p in files:
    s=p.read_text(errors='ignore')
    if not re.search(r'Task Mode:\s*\nMAJOR\b',s,re.I): continue
    checked+=1
    vals={}
    for k in 'DRBAXUVHCF':
        m=re.search(rf'^\s*{k}:\s*([0-4])\s*$',s,re.M)
        if not m: errors.append(f'{p}: missing/invalid {k} (must be integer 0-4)')
        else: vals[k]=int(m.group(1))
    if len(vals)!=10: continue
    cm=re.search(r'Routing Categories:\s*\n([^\n]+)',s,re.I); cats=[] if not cm else [x.strip() for x in cm.group(1).split(',')]
    out=route(**vals,categories=cats)
    tm=re.search(r'Primary Agent Tier:\s*\n([^\n]+)',s,re.I); em=re.search(r'Primary Effort:\s*\n([^\n]+)',s,re.I)
    got_t=tm.group(1).strip() if tm else ''; got_e=em.group(1).strip().lower() if em else ''
    if got_t!=out['tier']: errors.append(f"{p}: Tier {got_t!r} != router {out['tier']}")
    if got_e!=out['effort']: errors.append(f"{p}: Effort {got_e!r} != router {out['effort']}")
if errors:
    print('ROUTING VALIDATION: FAIL'); print('\n'.join('- '+e for e in errors)); sys.exit(1)
print(f'ROUTING VALIDATION: PASS ({checked} MAJOR task file(s) checked)')
