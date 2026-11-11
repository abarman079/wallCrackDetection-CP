#!/usr/bin/env python3
"""Fail closed on common accidental disclosures and invalid public research artifacts.

Not a replacement for human data-rights and independent scientific review.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

BLOCK_SUFFIX={'.pt','.pth','.ckpt','.safetensors','.onnx','.h5','.hdf5','.pkl','.pickle','.npy','.npz','.parquet','.7z','.tar','.gz','.zip','.log'}
BLOCK_PATH=re.compile(r'(?:^|/)(?:local_artifacts|datasets|raw_data|checkpoints|private_data|private_results|source_images|contact_sheets|calibration_locked|hidden_test|staging)(?:/|$)|(?:^|/)[^/]*(?:_PRIVATE|\.env)[^/]*',re.I)
LIMIT=10*1024*1024


def listed_files(root:Path,ci:bool):
    commands=[['git','ls-files','-z']]
    if not ci:
        commands.append(['git','ls-files','--others','--exclude-standard','-z'])
    files=set()
    for cmd in commands:
        p=subprocess.run(cmd,cwd=root,capture_output=True)
        if p.returncode:
            raise RuntimeError(p.stderr.decode(errors='replace'))
        for b in p.stdout.split(b'\0'):
            if b:files.add(b.decode('utf8','surrogateescape'))
    return sorted(files)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ci',action='store_true')
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    errors=[];reports={'files':0,'json':0,'notebooks':0,'figures':0,'workbooks':0}
    for rel in listed_files(root,args.ci):
        p=root/rel
        if not p.is_file():continue
        reports['files']+=1
        low=rel.lower()
        try:
            if BLOCK_PATH.search(rel):raise ValueError('private/forbidden path')
            if p.suffix.lower() in BLOCK_SUFFIX:raise ValueError('large/archive/checkpoint format not permitted in public Git')
            if p.stat().st_size>LIMIT:raise ValueError('file exceeds conservative 10 MiB limit')
            if p.suffix.lower()=='.json':
                json.loads(p.read_text(encoding='utf-8-sig'));reports['json']+=1
            elif p.suffix.lower()=='.ipynb':
                nb=json.loads(p.read_text(encoding='utf-8-sig'))
                if not isinstance(nb.get('cells'),list):raise ValueError('notebook has no cells array')
                if '/development/v4/' in low and any(c.get('cell_type')=='code' and c.get('outputs') for c in nb['cells']):
                    raise ValueError('new development notebook contains saved outputs; clear before public commit')
                reports['notebooks']+=1
            elif p.suffix.lower()=='.xlsx':
                with zipfile.ZipFile(p) as z:
                    if z.testzip() is not None or '[Content_Types].xml' not in z.namelist():
                        raise ValueError('corrupt XLSX')
                reports['workbooks']+=1
            elif p.suffix.lower()=='.png':
                if p.open('rb').read(8)!=b'\x89PNG\r\n\x1a\n':raise ValueError('not a PNG file')
                reports['figures']+=1
            elif p.suffix.lower() in {'.jpg','.jpeg'}:
                with p.open('rb') as f:
                    if f.read(2)!=b'\xff\xd8':raise ValueError('not a JPEG file')
                reports['figures']+=1
            if '/results/public/run_' in low and p.suffix.lower()=='.json':
                txt=p.read_text(encoding='utf8')
                if re.search(r'(?i)(image_relative_path|mask_relative_path|sample_id|/kaggle/input/|\\Users\\)',txt):
                    raise ValueError('potentially private per-sample metadata in public result')
        except Exception as ex:
            errors.append(f'{rel}: {ex}')
    for err in errors:print('FAIL',err)
    print('Files inspected:',reports)
    if errors:raise SystemExit(f'FAIL: {len(errors)} public repository safety/integrity check(s)')
    print('PASS: public repository structural checks; science/rights require human review')

if __name__=='__main__':main()
