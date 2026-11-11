#!/usr/bin/env python3
"""Create/check SHA-256 catalog for publication-safe artifacts under Notebook N/results/."""
import argparse
import csv
import hashlib
import io
import re
from pathlib import Path

EX = {'.json','.csv','.md','.png','.jpg','.jpeg','.xlsx'}
HEADERS = ['relative_path','bytes','sha256','phase','evidence_class']


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def assemble(root):
    b=io.StringIO(newline='')
    w=csv.writer(b,lineterminator='\n')
    w.writerow(HEADERS)
    for phase in range(1,9):
        base=root/f'Notebook {phase}'/'results'
        if not base.exists():continue
        for p in sorted(base.rglob('*'),key=lambda q:q.as_posix().lower()):
            if not p.is_file() or p.suffix.lower() not in EX or p.name=='PUBLIC_RESULTS_INDEX.csv':continue
            rel=p.relative_to(root).as_posix()
            if any(k in rel.lower() for k in ('/private/','_private','/calibration_locked/','/raw_data/')):continue
            status='REVIEWED_PUBLIC_RUN' if '/results/public/run_' in rel else 'ARCHIVED_PUBLIC_PHASE_OUTPUT'
            w.writerow([rel,p.stat().st_size,sha(p),f'{phase:02}',status])
    return b.getvalue()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true',help='CI: fail if file missing/outdated')
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    output=root/'PUBLIC_RESULTS_INDEX.csv'
    actual=assemble(root)
    if args.check:
        if not output.exists() or output.read_text(encoding='utf8')!=actual:
            raise SystemExit('PUBLIC_RESULTS_INDEX.csv is missing/stale; run python scripts/build_public_results_index.py and commit it')
        print('PASS public SHA-256 results index:',len(actual.splitlines())-1,'entries')
    else:
        output.write_text(actual,encoding='utf8')
        print('WROTE',output,'with',len(actual.splitlines())-1,'entries')

if __name__=='__main__':main()
