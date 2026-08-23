#!/usr/bin/env python3
from pathlib import Path
import importlib.util, sys
ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).with_name('sync_easy_roadmap.py')
spec=importlib.util.spec_from_file_location('sync_easy_roadmap',SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
target=ROOT/'PROJECT/LO_TRINH_DE_HIEU.md'
try: expected=mod.expected_content()
except Exception as e:
    print(f'EASY ROADMAP: FAIL - cannot parse source: {e}'); sys.exit(1)
if not target.exists():
    print('EASY ROADMAP: FAIL - missing PROJECT/LO_TRINH_DE_HIEU.md'); sys.exit(1)
actual=target.read_text(encoding='utf-8')
if actual != expected:
    print('EASY ROADMAP: FAIL - generated roadmap is stale. Run sync_easy_roadmap.py'); sys.exit(1)
print('EASY ROADMAP: PASS')
