# CrackSAFE-CP v3.3 — Phase03 development-only pre-FULL evidence run
# One Kaggle code cell. No raw dataset access, calibration or test access, model training,
# fabricated scientific approvals, or mutation of the official Phase03 notebook.
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import csv, importlib.metadata as md, io, json, os, sys, types, zipfile, traceback

INPUT=Path('/kaggle/input')
WORK=Path('/kaggle/working')
STAMP=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT=WORK/('CrackSAFE_P03_DEV_PREFULL_'+STAMP)
OUT.mkdir(parents=True,exist_ok=False)
ORIG_SHA='3b9d1171e4de2f7ea1b2c29d836fbe45a2a6a7dc4584a671f695b7720b3d656f'
DRAFT_SHA='cbbad8a5f04e1e2bdf1f4c651004c774a39e3900747f0a50033c6eb22e4fe8d3'
GPU_ZIP_SHA='ecdc137319daa288f92f38f00f52a5bbab9c843c68ad1a9760b802c75d1a16da'
BLUEPRINT_SHA='2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e'

def sha_bytes(b):return sha256(b).hexdigest()
def sha_file(p):
    h=sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()
def jw(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')

def locate_source(filename,expected):
    found=[]
    for base in (INPUT,WORK):
        if not base.is_dir():continue
        for p in base.rglob(filename):
            if p.is_file() and OUT not in p.parents and sha_file(p)==expected:
                found.append((str(p),p.read_bytes()))
        for pattern in ('CrackSAFE_P03_S5_VERIFIED_STAGE_*.zip','CrackSAFE_P03_S5_VERIFIED_STAGE_*.zip.bin','CrackSAFE_S5_CONVNEXT_PHASE03_PATCH_DRAFT.zip','CrackSAFE_S5_CONVNEXT_PHASE03_PATCH_DRAFT.zip.bin'):
            for p in base.rglob(pattern):
                if OUT in p.parents or not p.is_file():continue
                try:
                    with zipfile.ZipFile(p) as z:
                        members=[n for n in z.namelist() if n.rsplit('/',1)[-1]==filename]
                        for n in members:
                            if z.getinfo(n).file_size > 2*1024*1024:continue
                            b=z.read(n)
                            if sha_bytes(b)==expected: found.append((str(p)+'!'+n,b))
                except (OSError,zipfile.BadZipFile):pass
    if not found:
        raise RuntimeError('Cannot locate exact '+filename+' (SHA256 '+expected+'). Attach the verified S5 source-stage ZIP as a PRIVATE Kaggle input, or attach its extracted original/draft .py files. Do not rename or edit source text.')
    return sorted(found,key=lambda x:x[0])[0]

original_path, original=locate_source('phase03_core_ORIGINAL.py',ORIG_SHA)
draft_path, draft=locate_source('phase03_core_S5_DRAFT.py',DRAFT_SHA)
# Import exact staged code in a fresh module. No modification or bypass.
source=draft.decode('utf-8-sig')
assert sha_bytes(original)==ORIG_SHA and sha_bytes(draft)==DRAFT_SHA
assert 'def synthetic_tests(ctx):' in source and 'def validate_plan(ctx):' in source
assert "'calibration'" in source and "'internal_test'" in source
module=types.ModuleType('cracksafe_phase03_prefull_'+STAMP)
sys.modules[module.__name__]=module
exec(compile(source,'phase03_core_S5_DRAFT.py','exec'),module.__dict__)
assert module.BLUEPRINT_SHA==BLUEPRINT_SHA and module.SEEDS==[42,123,2026]

# Reuse the authoritative Phase03 synthetic functional suite, without invoking real-data paths.
ctx={'run':OUT/'core_synthetic','cfg':{'cpu_threads':2},'run_id':'PREFULL_'+STAMP}
ctx['run'].mkdir(parents=True,exist_ok=True)
try:
    result=module.synthetic_tests(ctx)
    tests=json.loads((ctx['run']/'synthetic_test_report.json').read_text())
    if tests.get('status')!='PASS' or not tests.get('tests') or any(t['status']!='PASS' for t in tests['tests']):
        raise RuntimeError('The real Phase03 synthetic test suite did not pass')
    suite_status='PASS'
    suite_details={'tests_passed':len(tests['tests']),'original_suite_result':result}
except Exception as e:
    suite_status='FAIL'
    suite_details={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
    jw(OUT/'SYNTHETIC_TEST_FAILURE.json',suite_details)

# Optional independent evidence continuity: use the exact previous T4 GPU ZIP if attached.
gpu_evidence={'status':'NOT_ATTACHED_PREVIOUS_T4_PASS_USER_REPORTED','zip_sha256_expected':GPU_ZIP_SHA}
for base in (INPUT,WORK):
    if gpu_evidence['status']=='VERIFIED':break
    if not base.exists():continue
    for pattern in ('CrackSAFE_P03_S5_GPU_INTEGRATION_*.zip','CrackSAFE_P03_S5_GPU_INTEGRATION_*.zip.bin'):
        for p in base.rglob(pattern):
            if OUT in p.parents or not p.is_file() or sha_file(p)!=GPU_ZIP_SHA:continue
            with zipfile.ZipFile(p) as z:
                if z.testzip() is not None:raise RuntimeError('Prior GPU evidence ZIP CRC failure')
                status=json.loads(z.read('S5_TECHNICAL_STATUS_PUBLIC.json'))
                if status.get('s5_integration_result')!='THREE_ENGINE_GPU_PASS':raise RuntimeError('Unexpected S5 GPU evidence')
                gpu_evidence={'status':'VERIFIED','zip_sha256':GPU_ZIP_SHA,'evidence':status,'mounted_zip':str(p)}
            break
        if gpu_evidence['status']=='VERIFIED':break

versions={}
for pkg in ('torch','torchvision','segmentation-models-pytorch','timm','transformers','numpy','scipy','scikit-image','Pillow'):
    try:versions[pkg]=md.version(pkg)
    except md.PackageNotFoundError:versions[pkg]=None

report={
    'artifact':'PHASE03_DEVELOPMENT_ONLY_PREFULL',
    'blueprint_version':'3.3','blueprint_sha256':BLUEPRINT_SHA,
    'generated_utc':datetime.now(timezone.utc).isoformat(),
    'source_sha256':{'original':ORIG_SHA,'s5_staged_draft':DRAFT_SHA},
    'staged_code_provenance':{'original':original_path,'draft':draft_path},
    'source_integrity':'PASS',
    'actual_authoritative_synthetic_suite':suite_status,
    'synthetic_suite_details':suite_details,
    'prior_s5_gpu_evidence':gpu_evidence,
    'package_versions':versions,
    'data_opened':False,'real_model_training_performed':False,
    'calibration_or_test_labels_opened':False,
    'p02_final_partition':'PROVISIONAL','g02':'BLOCKED','g03':'BLOCKED',
    's2':'PENDING','s6':'PENDING',
    'phase03_full_authorized':False,'phase04_empirical_handoff_authorized':False,
    'development_only_phase04_metric_unit_tests_permitted':True,
    'research_protocol_roster':{
      'A':'unetpp_effb3', 'B_primary':'scsegamba','C_primary':'dmsrcrack',
      'fallback_1':'segformer_b0','fallback_2':'unetpp_convnext_tiny_rgb_halfscale_v1',
      'fallback_substitution_approval_inferred':False
    },
    'interpretation':'Phase03 engineering tests and pinned GPU preflight only. No segmentation metrics, seed-training runs, selection, ensemble, certification or Phase04 scientific authorization.'
}
jw(OUT/'PHASE03_DEV_PREFULL_STATUS.json',report)

public={k:report[k] for k in ('artifact','blueprint_version','blueprint_sha256','generated_utc','source_sha256','source_integrity','actual_authoritative_synthetic_suite','synthetic_suite_details','package_versions','data_opened','real_model_training_performed','calibration_or_test_labels_opened','p02_final_partition','g02','g03','s2','s6','phase03_full_authorized','phase04_empirical_handoff_authorized','development_only_phase04_metric_unit_tests_permitted','research_protocol_roster','interpretation')}
jw(OUT/'github_ready'/'Notebook 3'/'results'/'PHASE03_DEV_PREFULL_PUBLIC.json',public)
(OUT/'github_ready'/'Notebook 3'/'results'/'PHASE03_DEV_PREFULL_README.md').write_text(
    '# Phase03 development-only evidence\n\nThis artifact records exact S5 code SHA256 and the authoritative synthetic functional tests.\n\nIt does not contain real training, independent calibration, test data, frozen checkpoints, a selected ensemble, or an official Phase03 FULL outcome. The Phase02 partition remains PROVISIONAL.\n\nThe original three slots and ordered fallback policy remain governed by blueprint v3.3.\n',encoding='utf-8')

# Hash-index all results; do not bundle the staged source files (already private inputs).
files=sorted(p for p in OUT.rglob('*') if p.is_file())
index=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha_file(p)} for p in files]
jw(OUT/'RESULTS_MANIFEST.json',{'status':'PASS' if suite_status=='PASS' else 'FAILED','files':index,'source_original_sha256':ORIG_SHA,'draft_sha256':DRAFT_SHA,'official_full':False})
archive=WORK/('CrackSAFE_P03_DEV_PREFULL_'+STAMP+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('Output ZIP CRC failure')
    for item in index:
        if sha_bytes(z.read(item['path']))!=item['sha256']:raise RuntimeError('Export hash mismatch: '+item['path'])
print('\n===== CRACKSAFE PHASE03 DEVELOPMENT PREFULL =====')
print('Source integrity: PASS (original and staged S5 draft exact SHA256)')
print('Authoritative functional suite:',suite_status,'; checks:',suite_details.get('tests_passed','N/A'))
print('Prior T4 integration evidence:',gpu_evidence['status'])
print('Real training: NO; Phase03 FULL: BLOCKED; Phase04 empirical: NOT AUTHORIZED')
print('Output ZIP:',archive)
print('Output ZIP SHA256:',sha_file(archive))
if suite_status!='PASS':raise RuntimeError('Functional test suite failed. Upload ZIP for diagnosis; do not report PASS.')
