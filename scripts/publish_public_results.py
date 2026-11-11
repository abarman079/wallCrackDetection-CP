#!/usr/bin/env python3
"""Curate deliberately reviewed *aggregate* research outputs into tracked phase paths.

This tool cannot certify dataset rights, anonymity, scientific eligibility or sample independence.
It refuses common private names/content and strips photo metadata from exported figures.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ALLOWED = {'.json', '.csv', '.xlsx', '.png', '.jpg', '.jpeg', '.md'}
LIMIT = 10 * 1024 * 1024
DENY_NAME = re.compile(r'(?:^|[_\W])(private|confidential|raw|heldout|held.out|calibration|source.photo|contact.sheet|per.sample|sample.id|mask|annotation|reviewer|password|token|credential|checkpoint|prediction.map|source.image)(?:$|[_\W])', re.I)
DENY_TEXT = re.compile(r'(?i)(?:/kaggle/input/|[A-Za-z]:\\(?:Users|Clients|Data)\\|(?:api[_-]?key|password|access[_-]?token)\s*[:=]|(?:image|mask)_relative_path|(?:image|mask)_absolute_path|(?:^|[^a-z])sample_id(?:[^a-z]|$)|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b)')
DENY_KEYS = {'sample_id', 'sample_ids', 'image_relative_path', 'mask_relative_path', 'image_absolute_path', 'mask_absolute_path', 'raw_image_path', 'raw_mask_path', 'reviewer_name', 'reviewer_email', 'source_filename', 'person_id', 'access_token', 'api_key', 'password', 'private_sample_registry', 'per_sample_predictions'}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def check_text(s: str, label: str) -> None:
    m = DENY_TEXT.search(s)
    if m:
        raise ValueError(f'{label}: suspected private content ({m.group(0)[:40]})')


def check_json_tree(o, label: str, depth: int = 0):
    if depth > 24:
        raise ValueError(f'{label}: excessive JSON nesting')
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() in DENY_KEYS:
                raise ValueError(f'{label}: disallowed JSON key {k!r}')
            check_json_tree(v, label, depth + 1)
    elif isinstance(o, list):
        if len(o) > 500:
            raise ValueError(f'{label}: >500 entries could be sample-level evidence')
        for v in o:
            check_json_tree(v, label, depth + 1)
    elif isinstance(o, str):
        check_text(o, label)


def validate_xlsx(p: Path):
    # Inspect XLSX content metadata and most common cell text. Reject macro/images/external links.
    with zipfile.ZipFile(p) as z:
        if z.testzip() is not None or '[Content_Types].xml' not in z.namelist():
            raise ValueError('Invalid XLSX ZIP container')
        xmls = [n for n in z.namelist() if n.startswith(('xl/worksheets/', 'xl/sharedStrings', 'xl/comments', 'xl/workbook')) and n.endswith('.xml')]
        if any(n.startswith(('xl/media/', 'xl/externalLinks/', 'xl/embeddings/', 'xl/vbaProject')) for n in z.namelist()):
            raise ValueError('XLSX includes media, external links, objects, or macros; publish an aggregate-only workbook')
        for n in xmls:
            content = z.read(n)
            if len(content) > 6 * 1024 * 1024:
                raise ValueError('Spreadsheet XML sheet too large for aggregate publication')
            check_text(content.decode('utf-8', errors='replace'), f'{p.name}:{n}')
            if n.startswith('xl/worksheets/sheet'):
                doc = ET.fromstring(content)
                count = sum(1 for x in doc.iter() if x.tag.endswith('}row'))
                if count > 500:
                    raise ValueError(f'{p.name}: more than 500 spreadsheet rows; check for sample-level table')


def validate_input(p: Path, rel: Path):
    if p.is_symlink():
        raise ValueError('Symlinks not accepted')
    if p.suffix.lower() not in ALLOWED:
        raise ValueError(f'{rel}: unsupported/unreviewed file type {p.suffix}')
    if DENY_NAME.search(rel.as_posix()):
        raise ValueError(f'{rel}: possible private/restricted filename')
    if not p.stat().st_size or p.stat().st_size > LIMIT:
        raise ValueError(f'{rel}: empty or exceeds 10 MiB public limit')
    ext = p.suffix.lower()
    if ext == '.json':
        text = p.read_text(encoding='utf-8-sig')
        check_json_tree(json.loads(text), str(rel))
    elif ext in {'.csv', '.md'}:
        text = p.read_text(encoding='utf-8-sig')
        check_text(text, str(rel))
        if ext == '.csv':
            table = list(csv.reader(text.splitlines()))
            if len(table) > 500:
                raise ValueError('CSV has >500 rows (possible per-sample data)')
            if table and any(k.strip().lower() in DENY_KEYS for k in table[0]):
                raise ValueError('Private CSV columns detected')
    elif ext == '.xlsx':
        validate_xlsx(p)
    else:
        try:
            from PIL import Image
        except ImportError as e:
            raise RuntimeError('Images require Pillow, install: python -m pip install "Pillow>=10,<13"') from e
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            if im.width * im.height > 40_000_000:
                raise ValueError(f'{rel}: unexpectedly large figure')
            if im.format not in ('PNG', 'JPEG'):
                raise ValueError('Incorrect file signature for image type')


def clean_image(src: Path, dest: Path):
    from PIL import Image
    with Image.open(src) as im:
        im.load()
        fmt = 'JPEG' if src.suffix.lower() in ('.jpg', '.jpeg') else 'PNG'
        target = im.convert('RGB') if fmt == 'JPEG' else im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
        if fmt == 'JPEG':
            target.save(dest, 'JPEG', quality=93, optimize=True, exif=b'')
        else:
            target.save(dest, 'PNG', optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True, help='Only handpicked public candidate files; never a private ALL_OUTPUTS extraction root')
    ap.add_argument('--phase', required=True, type=int, choices=range(1, 9))
    ap.add_argument('--run-id', required=True, help='Verified run ID (letters/numbers/_/- only)')
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    ap.add_argument('--reviewed', action='store_true', help='Human confirms content/split/rights reviewed before public export')
    ap.add_argument('--scientific-status', default='DEVELOPMENT', choices=['DEVELOPMENT', 'TECHNICAL', 'SYNTHETIC'])
    args = ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,64}', args.run_id):
        ap.error('run-id must be 3–64 ASCII letters/digits/_/-; use the true run ID')
    if args.apply and not args.reviewed:
        ap.error('--apply requires explicit --reviewed assertion')
    root = Path(__file__).resolve().parents[1]
    src = args.source.resolve()
    if not src.is_dir() or (src == root or root in src.parents):
        ap.error('--source must be a reviewed, external staging folder, not the Git checkout')
    paths = sorted((p for p in src.rglob('*') if p.is_file()), key=lambda x: str(x).lower())
    if not paths or len(paths) > 100:
        ap.error('Expected 1–100 individually selected publication files')
    records = []
    for p in paths:
        rel = p.relative_to(src)
        validate_input(p, rel)
        records.append((p, rel))
    dst = root / f'Notebook {args.phase}' / 'results' / 'public' / ('run_' + args.run_id)
    if dst.exists():
        ap.error('Immutable public run path already exists; use a fresh correct run-id. Do not overwrite published results.')
    print('Manual publication review still required. The program cannot certify image rights or science.')
    print('Target:', dst)
    for p, rel in records:
        print('  VERIFIED CANDIDATE:', str(rel), f'({p.stat().st_size} bytes)')
    if args.dry_run:
        print('DRY RUN: no files written. Visually inspect actual JSON/XLSX/images before --apply --reviewed.')
        return 0
    temp = Path(tempfile.mkdtemp(prefix='.public_approved_', dir=str(dst.parent if dst.parent.exists() else root)))
    try:
        exports = []
        for p, rel in records:
            d = temp / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            if p.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
                clean_image(p, d)
            else:
                shutil.copyfile(p, d)
            if d.stat().st_size > LIMIT:
                raise ValueError(f'{rel}: sanitized file exceeds public cap')
            exports.append({'path': rel.as_posix(), 'bytes': d.stat().st_size, 'sha256': sha(d)})
        receipt = {'schema':'cracksafe_reviewed_public_export_v1', 'phase': args.phase,
                   'run_id': args.run_id, 'scientific_status': args.scientific_status,
                   'publication_review_asserted': True,
                   'publication_review_is_not_scientific_certification': True,
                   'created_utc': datetime.now(timezone.utc).isoformat(), 'files': exports}
        (temp / 'PUBLIC_IMPORT_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        dst.parent.mkdir(parents=True, exist_ok=True)
        temp.replace(dst)
        print('EXPORTED:', dst)
        print('Next: python scripts/build_public_results_index.py && python scripts/check_public_repo.py')
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
