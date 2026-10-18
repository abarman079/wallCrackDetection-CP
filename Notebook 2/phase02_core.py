"""CrackSAFE-CP Phase02 v1.0.0: curator-only audit, no model training/evaluation."""
import ast, base64, csv, dataclasses, datetime as dt, hashlib, importlib.util, importlib.metadata
import io, json, math, mimetypes, os, platform, re, shutil, sqlite3, stat, sys, time, traceback, types, zipfile, zlib
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

VERSION='1.0.0'
BLUEPRINT_SHA='2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e'
P01_RUN='20261015T111557980168Z_d3a9b41a'
P01_ZIP='CrackSAFE_CP_v3.3_phase01_control_'+P01_RUN+'.zip'
P01_SHA='ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca'
SOURCE_LOCKS={
 'CRACK500 CrackTree200 GAPS384':'41b1972c02602a09aca89d12030bb351580036b6bfb8a31c46b1c71f563f754d',
 'CrackForest dataset(CFD)':'9a5437b0682cbdf6a5169139208777963393fbd7d9da6366de93237ad90174b9',
 'DeepCrack':'15027bdf5a851197f3c92be44bb4167052034ee96e219ec0f512b51626016991',
 'SDNET2018':'68c7bdc43641a8e2a2b0617ffb04ee0851662148da5adb39848082184c37e19c',
 'crack segmentation dataset':'dcc5143c8482f95b800f5dc97edb1d17cd4d0b700b109940698827ced028755f'}
IMAGE_EXT={'.png','.jpg','.jpeg','.bmp','.tif','.tiff','.webp'}
MASK_EXT=IMAGE_EXT|{'.mat','.npy'}
ROLES=['train','development_model','development_probability','development_policy','hard_negative_development','calibration','internal_test','external_positive_test','hard_negative_test','source_unlabeled_pool','target_unlabeled_pool','reserve_pool','corruption_test']
DEVELOPMENT_ROLES={'train','development_model','development_probability','development_policy','hard_negative_development'}
FINAL_ROLES={'calibration','internal_test','external_positive_test','hard_negative_test','corruption_test','reserve_pool'}

def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def jb(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha_file(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def atomic(p,b):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
 with tmp.open('wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 tmp.replace(p)
def jwrite(p,x):atomic(p,jb(x))
def twrite(p,s):atomic(p,s.encode())
def cwrite(p,rows,cols):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=cols,extrasaction='ignore');w.writeheader()
 for r in rows:w.writerow({k:'' if r.get(k) is None else r.get(k) for k in cols})
 twrite(p,out.getvalue())
def cread(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def stable(prefix,*values):return prefix+'_'+hashlib.sha256(jb(list(values))).hexdigest()[:24]
def assert_true(ok,message):
 if not ok:raise ValueError(message)
def require_under(p,root):
 p,root=Path(p).resolve(),Path(root).resolve()
 assert_true(p==root or root in p.parents,'Path is outside permitted root: '+str(p));return p

def safe_members(z,max_bytes=512*1024**2,max_members=200000):
 infos=z.infolist();assert_true(len(infos)<=max_members,'ZIP member limit exceeded')
 assert_true(sum(i.file_size for i in infos)<=max_bytes,'ZIP uncompressed budget exceeded')
 names=[]
 for i in infos:
  n=getattr(i,'orig_filename',i.filename);p=PurePosixPath(n)
  assert_true(n and '\x00' not in n and '\\' not in n and not n.startswith('/') and not re.match(r'^[A-Za-z]:',n) and '..' not in p.parts,'Unsafe ZIP member: '+repr(n))
  assert_true(not stat.S_ISLNK(i.external_attr>>16) and not(i.flag_bits&1),'Symlink/encrypted ZIP member: '+n)
  assert_true(i.file_size/max(1,i.compress_size)<2000,'ZIP expansion ratio rejected')
  names.append(n)
 assert_true(len(names)==len(set(names)),'Duplicate ZIP member names')
 return infos

def verify_zip(path,sidecar,expected_sha,phase,blueprint_sha=BLUEPRINT_SHA):
 path,sidecar=Path(path),Path(sidecar)
 assert_true(path.is_file() and sidecar.is_file(),'Attach the exact Phase01 control ZIP AND its .zip.sha256 sidecar using Add Input. Raw images alone are insufficient.')
 line=sidecar.read_text().strip().split('  ',1)
 assert_true(len(line)==2 and line[1]==path.name,'Sidecar must name the matching ZIP')
 digest=sha_file(path);assert_true(digest==expected_sha==line[0],'Control ZIP checksum mismatch; attach the unchanged successful FULL-run pair')
 with zipfile.ZipFile(path) as z:
  safe_members(z);assert_true(z.testzip() is None,'Control ZIP CRC failure')
  mname=f'phase{phase}_manifest.json';m=json.loads(z.read(mname))
  assert_true(m['phase']==phase and m['blueprint_version']=='3.3' and m['schema_version']=='1.0','Incompatible phase/blueprint/schema')
  assert_true(m['blueprint_sha256']==blueprint_sha,'Blueprint hash mismatch in manifest')
  mside=z.read(f'phase{phase}_manifest.sha256').decode().strip().split('  ',1)
  assert_true(mside==[hashlib.sha256(z.read(mname)).hexdigest(),mname],'Manifest sidecar mismatch')
  entries={e['relative_path']:e for e in m['output_artifacts']}
  assert_true(len(entries)==len(m['output_artifacts']),'Duplicate artifact paths')
  for name,e in entries.items():
   if e.get('bundled',True):
    data=z.read(name);assert_true(len(data)==e['byte_size'] and hashlib.sha256(data).hexdigest()==e['sha256'],'Payload hash mismatch: '+name)
  for line in z.read('SHA256SUMS.sha256').decode().splitlines():
   if not line or line.startswith('#'):continue
   h,n=line.split('  ',1);assert_true(hashlib.sha256(z.read(n)).hexdigest()==h,'Internal checksum mismatch: '+n)
 return m,digest

# %% Runtime, evidence boundaries and resumable stages
class BudgetStop(RuntimeError):pass

def init_run(config,core_source,workflow_source):
 import numpy,pandas,PIL,scipy,skimage,pyarrow
 c=dict(config);assert_true(c['run_mode'] in {'SMOKE','FULL'},'run_mode must be SMOKE or FULL')
 assert_true(c['calibration_floor']=={'positive':120,'negative':122},'Locked floor changed: requires an approved scientific amendment')
 assert_true(c['calibration_target']=={'positive':300,'negative':300},'Keep preferred calibration target locked; record infeasibility instead of silently reducing it')
 assert_true(1<=c['workers']<=8 and 1<=c['batch_size']<=512,'Use 1–8 workers and batch_size 1–512')
 assert_true(0<c['development_fraction']<1,'Invalid development fraction')
 assert_true(0<=c['near_hamming_radius']<=10 and c['max_bucket']>=2,'Invalid similarity index settings')
 for k in ['source_unlabeled_units','target_unlabeled_units','hard_negative_test_units','corruption_test_units']:
  assert_true(isinstance(c[k],int) and c[k]>=0,'Invalid count: '+k)
 for k in ['internal_test','reserve']:
  assert_true(set(c[k])=={'positive','negative'} and all(isinstance(v,int) and v>=0 for v in c[k].values()),'Invalid class counts: '+k)
 inp=Path(c['input_root']).resolve();assert_true(inp.is_dir(),'Input root missing. Attach the TWO Kaggle inputs, then check CONFIG[input_root].')
 out=Path(c['output_root']).resolve();out.mkdir(parents=True,exist_ok=True)
 assert_true(out!=inp and inp not in out.parents,'Output must not be inside the read-only input root')
 assert_true(shutil.disk_usage(out).free>=c['minimum_free_gb']*1024**3,'Insufficient free output disk')
 code_sha=hashlib.sha256((core_source+'\n'+workflow_source).encode()).hexdigest()
 semantic={k:v for k,v in c.items() if k not in {'resume_run_dir','output_root','session_budget_hours','export_buffer_minutes'}}
 if c['evidence_dir']:
  eroot=require_under(c['evidence_dir'],inp);assert_true(eroot.is_dir(),'Evidence directory missing');semantic['evidence_file_hashes']=[{'path':p.relative_to(eroot).as_posix(),'sha256':sha_file(p)} for p in sorted(eroot.rglob('*')) if p.is_file()]
 config_sha=hashlib.sha256(jb(semantic)).hexdigest()
 if c['resume_run_dir']:
  run=require_under(c['resume_run_dir'],out);old=json.loads((run/'run_identity.json').read_text())
  assert_true(not (run/'SEALED.json').exists(),'A sealed run is immutable. Start a new run for changed reviews or configuration.')
  assert_true(old['config_sha256']==config_sha and old['code_sha256']==code_sha,'Resume code/config mismatch; start a new run')
  run_id=old['run_id'];created=old['created_utc']
 else:
  run_id=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+config_sha[:8]
  run=out/'phase02'/('run_'+run_id);run.mkdir(parents=True);created=utc()
 identity={'run_id':run_id,'created_utc':created,'config_sha256':config_sha,'code_sha256':code_sha}
 jwrite(run/'run_identity.json',identity);jwrite(run/'config.json',{'schema_version':'1.0',**c})
 twrite(run/'phase02_core.py',core_source);twrite(run/'workflow_source.json',workflow_source)
 versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','Pillow','scipy','scikit-image','pyarrow']}
 jwrite(run/'environment_snapshot.json',{'python':sys.version,'platform':platform.platform(),'packages':versions,'cpu_count':os.cpu_count(),'accelerator':'NOT_USED','internet_required':False,'observed_utc':utc()})
 cache=sqlite3.connect(run/'audit_cache.sqlite');cache.execute('PRAGMA journal_mode=WAL');cache.execute('CREATE TABLE IF NOT EXISTS decode_cache (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
 ctx={'cfg':c,'run':run,'run_id':run_id,'identity':identity,'started':time.monotonic(),'cache':cache,'errors':[],'access':[],'warnings':[],'stages':{},'cache_hits':0,'cache_misses':0,'quarantine':[],'samples':[]}
 jwrite(run/'stage_errors.json',[]);jwrite(run/'phase_status.json',{'phase':'02','status':'BLOCKED','execution_status':'IN_PROGRESS','partition_status':'PROVISIONAL','scientific_certification_performed':False})
 print('Run:',run,'\nMode:',c['run_mode'],'CPU workers:',c['workers'],'Dependencies:',versions)
 return ctx

def check_budget(ctx):
 c=ctx['cfg']
 if time.monotonic()-ctx['started']>max(0,c['session_budget_hours']*3600-c['export_buffer_minutes']*60):raise BudgetStop('Audit time budget reached. Partial state/cache saved; resume the SAME unsealed run with a longer session budget.')
 if shutil.disk_usage(ctx['run']).free<c['minimum_free_gb']*1024**3:raise BudgetStop('Low output disk; checkpoint saved. Free output disk before resuming.')

def stage(ctx,name,fn):
 beg=utc()
 try:
  check_budget(ctx);value=fn(ctx);ctx['stages'][name]={'status':'PASS','started_utc':beg,'finished_utc':utc()};ctx['cache'].commit()
  if not (ctx['run']/'SEALED.json').exists():jwrite(ctx['run']/'stage_checkpoints.json',ctx['stages'])
  print(name,'COMPLETE');return value
 except Exception as e:
  rec={'stage':name,'type':type(e).__name__,'message':str(e),'utc':utc(),'traceback':traceback.format_exc()}
  ctx['errors'].append(rec);ctx['cache'].commit();jwrite(ctx['run']/'stage_errors.json',ctx['errors'])
  jwrite(ctx['run']/'phase_status.json',{'phase':'02','status':'BLOCKED','execution_status':'PARTIAL_BUDGET' if isinstance(e,BudgetStop) else 'FAILED','failed_stage':name,'partition_status':'PROVISIONAL','recovery':str(e)})
  raise

def log_access(ctx,path,operation,role='CURATOR_DATA_QUALITY'):
 ctx['access'].append({'utc':utc(),'path':str(path),'operation':operation,'access_role':role,'model_predictions_used':False})

def evidence_rows(ctx,name):
 if not ctx['cfg']['evidence_dir']:return []
 root=require_under(ctx['cfg']['evidence_dir'],ctx['cfg']['input_root']);p=root/name
 if not p.exists():return []
 assert_true(p.stat().st_size<64*1024**2,'Evidence CSV too large: '+name);log_access(ctx,p,'human_evidence_read')
 return cread(p)

def evidence_ok(ctx,row):
 if not all(row.get(k) for k in ['reviewer_id','reviewed_utc','evidence_path','evidence_sha256']):return False
 if not ctx['cfg']['evidence_dir']:return False
 try:
  p=require_under(Path(ctx['cfg']['evidence_dir'])/row['evidence_path'],ctx['cfg']['evidence_dir'])
  return p.is_file() and sha_file(p)==row['evidence_sha256']
 except (ValueError,OSError):return False

# %% Verified Phase01 handoff and original shared implementation

def discover_control(ctx):
 c=ctx['cfg'];root=Path(c['input_root'])
 if c['phase01_bundle']:
  paths=[require_under(c['phase01_bundle'],root)];assert_true(paths[0].name==P01_ZIP,'Explicit bundle basename does not match locked successful run')
 else:paths=sorted(root.rglob(P01_ZIP))
 # Kaggle datasets may auto-extract a .zip upload. A byte-for-byte .zip.bin carrier
 # prevents auto-extraction; restore the canonical filename under the writable run
 # before applying the UNCHANGED outer SHA, named sidecar, CRC and manifest checks.
 if not paths and not c['phase01_bundle']:
  carriers=sorted(root.rglob(P01_ZIP+'.bin'))
  assert_true(len(carriers)==1,'Control ZIP absent. Expected exactly one unextracted '+P01_ZIP+'.bin below '+str(root)+f'; found {len(carriers)}. Attach renamed original archive as a private dataset.')
  carrier=carriers[0]
  assert_true(sha_file(carrier)==P01_SHA,'Archive carrier bytes do not match the locked full-run ZIP SHA-256')
  expected_sidecar=P01_SHA+'  '+P01_ZIP
  candidates=sorted(root.rglob(P01_ZIP+'.sha256'))
  sidecars=[s for s in candidates if s.is_file() and s.read_text(encoding='utf-8').strip()==expected_sidecar]
  assert_true(len(sidecars)>=1,'Matching original .zip.sha256 sidecar missing or incorrect')
  recovered=ctx['run']/'recovered_phase01_input';recovered.mkdir(parents=True,exist_ok=True)
  canonical=recovered/P01_ZIP
  shutil.copyfile(carrier,canonical)
  shutil.copyfile(sidecars[0],Path(str(canonical)+'.sha256'))
  log_access(ctx,carrier,'unaltered_renamed_binary_carrier_verified_against_locked_sha256','CONTROL_READ')
  paths=[canonical]
 assert_true(len(paths)==1,'Expected exactly one '+P01_ZIP+' below '+str(root)+f'; found {len(paths)}. Attach matching controls or remove duplicate mounts.')
 p=paths[0];m,h=verify_zip(p,Path(str(p)+'.sha256'),P01_SHA,'01');up=ctx['run']/'verified_phase01';up.mkdir(exist_ok=True)
 with zipfile.ZipFile(p) as z:
  for info in safe_members(z):
   if info.is_dir():continue
   target=require_under(up/info.filename,up);atomic(target,z.read(info))
 status=json.loads((up/'phase_status.json').read_text());cfg=json.loads((up/'config.json').read_text())
 assert_true(m['run_id']==P01_RUN and status['run_mode']=='FULL' and cfg['run_mode']=='FULL','Wrong run or non-FULL Phase01')
 assert_true(status.get('phase02_audit_ready') is True and m.get('phase02_audit_ready') is True,'Phase01 is not ready for the initial Phase02 audit')
 assert_true(status.get('statistical_self_tests')=='PASS' and not status.get('missing_mandatory_outputs') and json.loads((up/'stage_errors.json').read_text())==[],'Phase01 mandatory checks/errors failed')
 assert_true(sha_file(up/'blueprint_v3.3.md')==BLUEPRINT_SHA,'Blueprint payload mismatch')
 source=(up/'phase01_core.py').read_text();workflow=(up/'workflow_source.json').read_text()
 assert_true(hashlib.sha256((source+'\n'+workflow).encode()).hexdigest()==m['code_sha256'],'Phase01 exported code identity mismatch')
 with zipfile.ZipFile(up/'cracksafe_core.zip') as z:
  safe_members(z);assert_true(z.read('cracksafe_core/phase01.py')==(up/'phase01_core.py').read_bytes(),'Shared Phase01 implementation differs from verified source')
 name='_verified_cracksafe_phase01_'+h[:16];spec=importlib.util.spec_from_file_location(name,up/'phase01_core.py');mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 for n in ['json_bytes','sha256_file','cp_upper','minimum_n']:assert_true(callable(getattr(mod,n,None)),'Missing shared helper: '+n)
 assert_true(mod.json_bytes({'path':'a','size':1,'sha256':'x'})==jb({'path':'a','size':1,'sha256':'x'}),'JSON contract incompatible')
 assert_true(mod.minimum_n(.1)==60 and mod.minimum_n(.05)==122,'Upstream exact-bound planning locks changed')
 upstream_tests=mod.statistical_self_tests();assert_true(len(upstream_tests)==20 and all(r['status']=='PASS' for r in upstream_tests),'Verified upstream statistical self-tests failed')
 jwrite(ctx['run']/'upstream_statistical_self_tests.json',{'status':'PASS','checks':upstream_tests,'implementation':'Exact verified Phase01 module; no duplicate statistical implementation'})
 ctx.update(upstream=up,p01=mod,p01_manifest=m,p01_sha=h)
 log_access(ctx,p,'outer_crc_manifest_internal_hash_verify_and_controlled_import','CONTROL_READ')
 inv=cread(up/'archive_inventory.csv');assert_true(len(inv)==5,'Expected five logical extracted sources')
 assert_true({r['name'] for r in inv}==set(SOURCE_LOCKS),'Phase01 source names differ from confirmed handoff')
 for r in inv:assert_true(r['sha256']==SOURCE_LOCKS[r['name']] and r['source_type']=='EXTRACTED_DIRECTORY' and r['hash_status']=='PASS','Phase01 source lock mismatch: '+r['name'])
 ctx['p01_inventory']=inv;ctx['p01_members']=cread(up/'archive_members.csv')
 expected_pairs=[(1.,1.),(.95,1.),(.95,.95),(.9,.95),(.9,.9),(.85,.9),(.85,.85),(.8,.85),(.8,.8),(.75,.8),(.75,.75),(.7,.75),(.7,.7)]
 assert_true(mod.POLICY_PAIRS==expected_pairs and mod.DELTA_CELL==.05/26 and mod.SEEDS==[42,123,2026],'Phase01 finite-family/seed locks changed')
 jwrite(ctx['run']/'phase01_verification.json',{'status':'PASS','zip_sha256':h,'run_id':m['run_id'],'input_layout':'EXTRACTED_DIRECTORY','raw_archive_count_interpretation':'logical sources, not raw ZIP count','overall_BLOCKED_interpretation':'Later scientific approvals pending; initial data audit permitted','code_sha256':m['code_sha256'],'shared_helpers':'Imported only after fixed outer and all internal fingerprints passed'})
 return {'phase01_integrity':'PASS','logical_sources':len(inv)}

# %% Extracted source resolution and byte-for-byte fingerprints

def discover_raw(ctx):
 c=ctx['cfg'];root=Path(c['input_root']);names=set(SOURCE_LOCKS);over=c['source_directory_overrides']
 assert_true(set(over)<=names,'Unknown logical source in source_directory_overrides')
 if c['raw_root']:raw=require_under(c['raw_root'],root);assert_true(raw.is_dir(),'raw_root is not a directory')
 else:
  candidates=set()
  for n in names:
   for p in root.rglob(n):
    if p.is_dir() and not p.is_symlink():candidates.add(p.parent.resolve())
  assert_true(len(candidates)==1,f'Raw root missing/ambiguous: {len(candidates)} candidates. Set raw_root to the extracted dataset mount; do not create ZIPs.')
  raw=next(iter(candidates))
 paths={}
 for n in sorted(names):
  p=Path(over[n]) if n in over else raw/n
  if not p.is_absolute():p=raw/p
  p=require_under(p,raw)
  assert_true(p.is_dir() and not p.is_symlink(),'Missing/renamed source folder '+n+'. Set source_directory_overrides only when it is the same content; hashes will still be checked.')
  paths[n]=p
 assert_true(len(set(paths.values()))==5,'Source folders must be distinct')
 ctx.update(raw_root=raw,source_paths=paths)
 extras=[str(p.relative_to(raw)) for p in raw.iterdir() if p not in set(paths.values())]
 ctx['root_extras']=extras
 jwrite(ctx['run']/'dataset_discovery.json',{'raw_root':str(raw),'sources':{k:str(v) for k,v in paths.items()},'unexpected_root_entries':extras,'raw_zip_required':False,'logical_source_count':5})


def inventory_raw(ctx):
 discover_raw(ctx);c=ctx['cfg'];run=ctx['run'];members=defaultdict(list)
 estimate=len(ctx['p01_members'])*6144+64*1024**2
 jwrite(run/'resource_estimate.json',{'estimated_audit_and_export_bytes':estimate,'estimate_basis':'6 KiB per filesystem member plus 64 MiB controls; planning allowance, not measured final size','free_output_bytes':shutil.disk_usage(run).free,'decode_worker_limit':c['workers'],'max_pixels_per_image':c['max_image_pixels'],'raw_payload_copy_bytes':0})
 assert_true(shutil.disk_usage(run).free>=estimate*1.25,'Output capacity below conservative audit/export estimate; free disk before FULL')
 for r in ctx['p01_members']:members[r['archive_id']].append(r)
 rows=[];files=[];mismatches=[]
 for src in ctx['p01_inventory']:
  check_budget(ctx);name=src['name'];folder=ctx['source_paths'][name];expected=members[src['archive_id']]
  exp={r['member_name']:r for r in expected};assert_true(len(exp)==len(expected),'Duplicate Phase01 member paths')
  # Reconstruct the original manifest using the verified upstream serializer, not a new tree-hash recipe.
  ledger=hashlib.sha256()
  for rel,r in sorted(exp.items(),key=lambda item:int(item[1]['member_index'])):ledger.update(ctx['p01'].json_bytes({'path':rel,'size':int(r['file_size']),'sha256':r['member_sha256']}))
  assert_true(ledger.hexdigest()==src['sha256'],'Phase01 member ledger does not reconstruct locked tree: '+name)
  actual={p.relative_to(folder).as_posix():p for p in sorted(folder.rglob('*')) if p.is_file() or p.is_symlink()}
  for rel in sorted(set(exp)-set(actual)):mismatches.append({'source':name,'path':rel,'reason':'MISSING_FILE'})
  for rel in sorted(set(actual)-set(exp)):mismatches.append({'source':name,'path':rel,'reason':'EXTRA_FILE'})
  chosen=set(sorted(actual,key=lambda r:stable('smoke',c['seed'],name,r))[:c['smoke_per_source']]) if c['run_mode']=='SMOKE' else set(actual)
  digest=hashlib.sha256();bad=0;checked=0
  sorted_actual=sorted(actual,key=lambda rel:PurePosixPath(rel).parts)
  for offset in range(0,len(actual),c['batch_size']):
   check_budget(ctx);chunk=sorted_actual[offset:offset+c['batch_size']]
   def one(rel):
    p=actual[rel];r=exp.get(rel);state='PASS';h=None;size=None;error=''
    try:
     assert_true(not p.is_symlink() and all(not x.is_symlink() for x in p.parents if x!=folder.parent),'SYMLINK_PATH')
     size=p.stat().st_size
     if rel in chosen:h=sha_file(p)
     state='PASS' if h else 'NOT_RUN_SMOKE'
     if r is None:state='EXTRA_FILE'
     elif size!=int(r['file_size']) or (h and h!=r['member_sha256']):state='CHANGED_CONTENT'
    except (OSError,ValueError) as e:state='INACCESSIBLE_OR_UNSAFE';error=str(e)
    return {'collection':name,'archive_id':src['archive_id'],'relative_path':rel,'absolute_path':str(p),'file_size':size,'sha256':h,'expected_sha256':r['member_sha256'] if r else None,'status':state,'error':error,'source_hint':r.get('source_family_hint','UNKNOWN') if r else 'UNKNOWN'}
   with ThreadPoolExecutor(max_workers=c['workers']) as pool:batch=list(pool.map(one,chunk))
   if offset%(c['batch_size']*100)==0:print('Hashing',name,min(offset+c['batch_size'],len(actual)),'/',len(actual))
   for f in batch:
    files.append(f);checked+=bool(f['sha256']);bad+=f['status'] not in {'PASS','NOT_RUN_SMOKE'}
    if f['status'] not in {'PASS','NOT_RUN_SMOKE'}:mismatches.append({'source':name,'path':f['relative_path'],'reason':f['status']})
    digest.update(ctx['p01'].json_bytes({'path':f['relative_path'],'size':f['file_size'],'sha256':f['sha256']}))
  full=c['run_mode']=='FULL' and not bad and set(actual)==set(exp)
  tree=digest.hexdigest() if full else None;status='PASS' if full and tree==src['sha256'] else 'PARTIAL_SMOKE' if c['run_mode']=='SMOKE' and not bad and set(actual)==set(exp) else 'BLOCKED'
  rows.append({'archive_id':src['archive_id'],'collection':name,'source_type':'EXTRACTED_DIRECTORY','original_zip_available':False,'expected_files':len(exp),'observed_files':len(actual),'hashed_files':checked,'expected_tree_sha256':src['sha256'],'observed_tree_sha256':tree,'status':status})
  print(name,':',len(actual),'files;',checked,'hashed;',status)
 cwrite(run/'archive_inventory.csv',rows,list(rows[0]));cwrite(run/'raw_fingerprint_mismatches.csv',mismatches,['source','path','reason'])
 write_parquet(run/'file_inventory.parquet',files)
 ctx.update(files=files,inventory=rows,raw_complete=all(r['status']=='PASS' for r in rows) and not ctx['root_extras'])
 log_access(ctx,ctx['raw_root'],'recursive_metadata_and_streaming_file_SHA256')
 assert_true(not mismatches and not ctx['root_extras'],'Raw input differs from verified Phase01. Inspect raw_fingerprint_mismatches.csv and dataset_discovery.json. Restore exact data or create an explicitly reviewed new Phase01 handoff; do not bypass locks.')


def write_parquet(p,rows,columns=None):
 import pandas as pd
 frame=pd.DataFrame(rows,columns=columns) if columns else pd.DataFrame(rows)
 if len(frame.columns)==0:frame=pd.DataFrame({'sample_id':pd.Series(dtype='string')})
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp.parquet');frame.to_parquet(tmp,index=False,engine='pyarrow');tmp.replace(p)
 assert_true(len(pd.read_parquet(p))==len(rows),'Parquet round-trip count mismatch')

# %% Pairing adapters, image decoding and canonical hashes
MASK_TOKEN=re.compile(r'(^|[/_\-])(masks?|labels?|ground.?truth|gt|annotations?|train_lab|test_lab)([/_\-.]|$)',re.I)
ORIGINAL_SOURCES=['crack500','cracktree200','gaps384','cfd','deepcrack','sdnet2018','riss','aigle','esarc','tut']

def source_hint(collection,rel):
 text=rel.lower()
 patterns=[('cracktree200',r'cracktree'),('cfd',r'crackforest|\bcfd\b'),('sdnet2018',r'sdnet'),('crack500',r'crack500'),('gaps384',r'gaps'),('deepcrack',r'deepcrack'),('riss',r'riss'),('aigle',r'aigle'),('esarc',r'esarc'),('tut',r'(^|[/_])tut')]
 candidates=[n for n,p in patterns if re.search(p,text)]
 if len(candidates)==1:return candidates[0]
 # The mixed three-source folder name is not per-image provenance.
 if collection=='DeepCrack':return 'deepcrack'
 if collection=='SDNET2018':return 'sdnet2018'
 if collection=='CrackForest dataset(CFD)':return 'cfd'
 return 'UNKNOWN'

def mask_hint(rel):
 p=Path(rel);return bool(MASK_TOKEN.search(rel) or p.suffix.lower() in {'.mat','.npy'})

def pair_key(rel):
 p=PurePosixPath(rel);parts=[]
 for x in p.parts[:-1]:
  v=x.casefold().replace('groundtruth','gt').replace('ground_truth','gt')
  if v in {'images','image','img','imgs','masks','mask','labels','label','gt','annotations'}:continue
  v=re.sub(r'_(?:images?|imgs?|masks?|labels?|lab|gt)$','',v)
  parts.append(v)
 stem=p.stem.casefold();stem=re.sub(r'^(?:mask|label|gt)[_\-]','',stem);stem=re.sub(r'[_\-](?:mask|label|gt|segmentation|annotation)$','',stem)
 stem=re.sub(r'^(?:image|img|gt)[_\-]?(?=\d)','',stem)
 return '/'.join(parts+[stem])

def class_hint(collection,rel):
 if collection!='SDNET2018':return 'UNKNOWN'
 tokens=[x.lower() for x in PurePosixPath(rel).parts[:-1]]
 # SDNET C/U under D/P/W; a filename or generic word is not ground truth.
 if any(x in {'cd','cp','cw','cracked','positive'} for x in tokens) or 'c' in tokens:return 'POSITIVE_CLASSIFICATION'
 if any(x in {'ud','up','uw','uncracked','negative'} for x in tokens) or 'u' in tokens:return 'NEGATIVE_UNADJUDICATED'
 return 'UNKNOWN'

def canonical_hash(a):
 import numpy as np
 a=np.ascontiguousarray(a);return hashlib.sha256(jb({'shape':list(a.shape),'dtype':str(a.dtype)})+a.tobytes()).hexdigest()

def image_array(path,max_pixels):
 import numpy as np
 from PIL import Image
 with Image.open(path) as im:
  assert_true(im.width*im.height<=max_pixels,'Image pixel budget exceeded')
  orientation=int(im.getexif().get(274,1));mode=im.mode;bands=len(im.getbands());im.load();a=np.asarray(im.convert('RGB')).copy()
 return a,{'native_mode':mode,'native_channels':bands,'exif_orientation':orientation}

def mask_array(path,max_pixels,max_bytes):
 import numpy as np
 from PIL import Image
 p=Path(path);assert_true(p.stat().st_size<=max_bytes,'Mask file budget exceeded')
 if p.suffix.lower()=='.npy':a=np.load(p,allow_pickle=False)
 elif p.suffix.lower()=='.mat':
  from scipy.io import loadmat
  d=loadmat(p,simplify_cells=True);candidates=[]
  def walk(v,key=''):
   if isinstance(v,dict):
    for k,x in v.items():
     if not k.startswith('__'):walk(x,k)
   elif isinstance(v,(list,tuple)):
    for x in v:walk(x,key)
   elif isinstance(v,np.ndarray) and v.dtype==object:
    for x in v.flat:walk(x,key)
   elif isinstance(v,np.ndarray) and v.ndim==2 and key.lower() in {'segmentation','groundtruth','ground_truth','mask','label','gt'}:candidates.append(v)
  walk(d);assert_true(len(candidates)==1,'MAT mask needs one explicit Segmentation/groundTruth/mask/label/gt array; ambiguous layouts require an adapter review');a=candidates[0]
 else:
  with Image.open(p) as im:assert_true(im.width*im.height<=max_pixels,'Mask pixel budget exceeded');im.load();a=np.asarray(im).copy()
 assert_true(a.size<=max_pixels*4 and a.nbytes<=max_bytes,'Decoded mask budget exceeded')
 if a.ndim==3 and a.shape[2] in {3,4}:
  assert_true(np.array_equal(a[:,:,0],a[:,:,1]) and np.array_equal(a[:,:,1],a[:,:,2]),'Colored mask: palette semantics require review')
  if a.shape[2]==4:assert_true(np.all(a[:,:,3]==255),'Mask transparency/ignore regions require review')
  a=a[:,:,0]
 assert_true(a.ndim==2 and np.all(np.isfinite(a)),'Mask must be finite 2-D')
 values=np.unique(a);known=set(values.tolist())<= {0,1} or set(values.tolist())<= {0,255}
 assert_true(known,'Non-binary/ignore mask values require explicit annotation adapter review: '+str(values[:20].tolist()))
 return (a>0).astype(np.uint8),values.tolist()

def phash(a):
 import numpy as np
 from PIL import Image
 from scipy.fft import dctn
 im=np.asarray(Image.fromarray(a).convert('L').resize((32,32),Image.Resampling.LANCZOS),dtype=float)
 f=dctn(im,type=2,norm='ortho')[:8,:8];b=f>np.median(f.flatten()[1:]);b[0,0]=False
 return ''.join(f'{int(v):02x}' for v in np.packbits(b.reshape(-1)))

def image_features(a):
 import numpy as np
 from PIL import Image
 h,w=a.shape[:2];variants=[('identity',a),('flip_h',a[:,::-1]),('flip_v',a[::-1,:]),('rot90',np.rot90(a,1)),('rot180',np.rot90(a,2)),('rot270',np.rot90(a,3))]
 # A bounded crop index captures common halves and central crops. Arbitrary crops still require lineage evidence.
 if min(h,w)>=8:
  for name,(y0,y1,x0,x1) in {'center':(.25,.75,.25,.75),'top':(0,.5,0,1),'bottom':(.5,1,0,1),'left':(0,1,0,.5),'right':(0,1,.5,1)}.items():variants.append(('crop_'+name,a[int(y0*h):int(y1*h),int(x0*w):int(x1*w)]))
 return {'phash':phash(a),'hash_variants':[[n,phash(v)] for n,v in variants],'thumbnail':base64.b64encode(np.asarray(Image.fromarray(a).convert('L').resize((16,16)),dtype=np.uint8).tobytes()).decode()}

def decode_pair(job,c):
 s=dict(job);s.update(decode_status='PASS',mask_status='MISSING',annotation_state='UNKNOWN',label='UNKNOWN',quarantine_reason='')
 try:
  a,meta=image_array(s['image_path'],c['max_image_pixels']);s.update(meta);s.update(height=a.shape[0],width=a.shape[1],decoded_image_sha256=canonical_hash(a),**image_features(a))
  if meta['exif_orientation']!=1:raise ValueError('Nontrivial EXIF orientation: reconcile image and mask orientation explicitly')
  if s.get('mask_path'):
   m,vals=mask_array(s['mask_path'],c['max_image_pixels'],c['max_mask_bytes']);assert_true(m.shape==a.shape[:2],'Image/mask dimensions disagree')
   s.update(mask_status='BINARY_ALIGNED',mask_values=vals,mask_pixels=int(m.sum()),decoded_mask_sha256=canonical_hash(m),pair_sha256=stable('pair',s['decoded_image_sha256'],canonical_hash(m)),annotation_state='POSITIVE_MASK_PENDING_REVIEW' if m.any() else 'EMPTY_MASK_NOT_CONFIRMED_NEGATIVE')
  elif s['class_hint']=='POSITIVE_CLASSIFICATION':s['annotation_state']='CLASSIFICATION_POSITIVE_NO_SEGMENTATION_GT'
 except Exception as e:s.update(decode_status='QUARANTINED',quarantine_reason=type(e).__name__+': '+str(e))
 return s

def audit_pairs(ctx):
 c=ctx['cfg'];run=ctx['run'];files=ctx['files'];bycol=defaultdict(list)
 for f in files:bycol[f['collection']].append(f)
 jobs=[];issues=[];claimed=set()
 explicit=evidence_rows(ctx,'pair_overrides.csv');overrides={r['sample_id']:r for r in explicit}
 assert_true(len(overrides)==len(explicit),'Duplicate pair override sample_id')
 for col,ff in sorted(bycol.items()):
  masks=defaultdict(list);images=[];lookup={f['relative_path']:f for f in ff}
  for f in ff:
   suffix=Path(f['relative_path']).suffix.lower()
   same_stem_jpeg=any(str(PurePosixPath(f['relative_path']).with_suffix(ext)) in lookup for ext in ['.jpg','.jpeg','.JPG','.JPEG'])
   crack500_png_mask=source_hint(col,f['relative_path'])=='crack500' and suffix=='.png' and same_stem_jpeg
   if suffix in MASK_EXT and (mask_hint(f['relative_path']) or crack500_png_mask):masks[pair_key(f['relative_path'])].append(f)
   elif suffix in IMAGE_EXT:images.append(f)
  selected=sorted(images,key=lambda f:stable('smoke_image',c['seed'],col,f['relative_path']))[:c['smoke_per_source']] if c['run_mode']=='SMOKE' else sorted(images,key=lambda f:f['relative_path'])
  for f in selected:
   sid=stable('sample',col,f['relative_path']);cand=masks.get(pair_key(f['relative_path']),[]);override=overrides.get(sid)
   if override:
    assert_true(evidence_ok(ctx,override),'Pair override lacks evidence: '+sid);assert_true(override['image_sha256']==f['expected_sha256'],'Stale pair override image')
    chosen=lookup.get(override['mask_relative_path']);assert_true(chosen is not None and chosen['expected_sha256']==override['mask_sha256'],'Pair override mask absent/stale');cand=[chosen]
   if len(cand)>1:issues.append({'sample_id':sid,'reason':'AMBIGUOUS_PAIR','detail':json.dumps([x['relative_path'] for x in cand])})
   mask=cand[0] if len(cand)==1 else None
   for obj in [f]+([mask] if mask else []):
    if not obj['sha256']:
     obj['sha256']=sha_file(obj['absolute_path']);assert_true(obj['sha256']==obj['expected_sha256'],'SMOKE selected content changed: '+obj['relative_path'])
   if mask:claimed.add((col,mask['relative_path']))
   jobs.append({'sample_id':sid,'collection':col,'original_source_hint':source_hint(col,f['relative_path']),'original_source_id':'UNKNOWN','image_relative_path':f['relative_path'],'image_path':f['absolute_path'],'image_sha256':f['sha256'],'mask_relative_path':mask['relative_path'] if mask else None,'mask_path':mask['absolute_path'] if mask else None,'mask_sha256':mask['sha256'] if mask else None,'class_hint':class_hint(col,f['relative_path']),'pair_status':'PAIRED_BY_NORMALIZED_PATH' if mask else 'AMBIGUOUS' if len(cand)>1 else 'UNPAIRED','is_aggregation':col=='crack segmentation dataset'})
  if c['run_mode']=='FULL':
   for group in masks.values():
    for f in group:
     if (col,f['relative_path']) not in claimed:issues.append({'sample_id':'','reason':'ORPHAN_MASK','detail':col+'/'+f['relative_path']})
 decoded=[];alg=ctx['identity']['code_sha256']
 for offset in range(0,len(jobs),c['batch_size']):
  check_budget(ctx);batch=jobs[offset:offset+c['batch_size']];todo=[]
  for s in batch:
   key=stable('decode',alg,s['sample_id'],s['image_sha256'],s['mask_sha256']);hit=ctx['cache'].execute('SELECT value FROM decode_cache WHERE key=?',(key,)).fetchone()
   if hit:
    r=json.loads(hit[0]);r.update({k:s[k] for k in ['image_path','mask_path']});decoded.append(r);ctx['cache_hits']+=1
   else:todo.append((key,s));ctx['cache_misses']+=1
  with ThreadPoolExecutor(max_workers=c['workers']) as pool:results=list(pool.map(lambda item:decode_pair(item[1],c),todo))
  for (key,s),r in zip(todo,results):ctx['cache'].execute('INSERT OR REPLACE INTO decode_cache VALUES (?,?)',(key,json.dumps(r,allow_nan=False)));decoded.append(r)
  ctx['cache'].commit()
  if offset%max(1,c['batch_size']*20)==0:print('Decoded',min(offset+c['batch_size'],len(jobs)),'/',len(jobs),'cache hits',ctx['cache_hits'])
 ctx['samples']=sorted(decoded,key=lambda s:s['sample_id']);ctx['pair_issues']=issues
 cwrite(run/'pairing_audit.csv',issues,['sample_id','reason','detail'])
 for s in ctx['samples']:
  if s['decode_status']!='PASS' or s['pair_status']=='AMBIGUOUS':quarantine(ctx,s['sample_id'],'PAIR_OR_DECODE',s['quarantine_reason'] or s['pair_status'])
 write_samples(ctx);jwrite(run/'decode_summary.json',{'samples_examined':len(decoded),'full_inventory':c['run_mode']=='FULL','counts':dict(Counter(s['annotation_state'] for s in decoded)),'cache_hits':ctx['cache_hits'],'cache_misses':ctx['cache_misses'],'pairing_issue_count':len(issues),'policy':'Unmatched cases remain reviewable; no heuristic pairing becomes adjudicated ground truth'})

def quarantine(ctx,sid,reason,detail=''):
 row={'sample_id':sid,'reason':reason,'detail':detail}
 key=(sid,reason,detail);seen=ctx.setdefault('_quarantine_keys',set())
 if key not in seen:ctx['quarantine'].append(row);seen.add(key)

def write_samples(ctx):
 rows=[]
 for s in ctx['samples']:
  row={k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in s.items() if k not in {'thumbnail','hash_variants','image_path','mask_path'}};rows.append(row)
 write_parquet(ctx['run']/'sample_registry.parquet',rows)

# %% Exact duplicates, mask conflicts and indexed near-duplicate review
class UnionFind:
 def __init__(self,ids):self.parent={s:s for s in ids}
 def find(self,x):
  while self.parent[x]!=x:self.parent[x]=self.parent[self.parent[x]];x=self.parent[x]
  return x
 def union(self,a,b):
  a,b=self.find(a),self.find(b)
  if a!=b:self.parent[max(a,b)]=min(a,b)
 def groups(self):
  d=defaultdict(list)
  for s in self.parent:d[self.find(s)].append(s)
  return [sorted(v) for k,v in sorted(d.items())]

def exact_audit(ctx):
 samples=ctx['samples'];uf=UnionFind([s['sample_id'] for s in samples]);rows=[];byid={s['sample_id']:s for s in samples}
 for field in ['image_sha256','decoded_image_sha256']:
  buckets=defaultdict(list)
  for s in samples:
   if s.get(field):buckets[s[field]].append(s)
  for h,group in sorted(buckets.items()):
   if len(group)<2:continue
   anchor=sorted(group,key=lambda s:s['sample_id'])[0]
   masks={s.get('decoded_mask_sha256') for s in group if s.get('decoded_mask_sha256')}
   conflict=len(masks)>1
   for s in group:
    if conflict:quarantine(ctx,s['sample_id'],'CONFLICTING_MASKS','Same image content has different aligned masks; reconcile annotation source')
    if s is anchor:continue
    uf.union(anchor['sample_id'],s['sample_id']);rows.append({'left_id':anchor['sample_id'],'right_id':s['sample_id'],'evidence':field,'sha256':h,'cross_collection':anchor['collection']!=s['collection'],'mask_conflict':conflict,'edge_layout':'star; all members transitively connected'})
 ctx.update(uf=uf,byid=byid,exact=rows)
 cwrite(ctx['run']/'exact_duplicates.csv',rows,['left_id','right_id','evidence','sha256','cross_collection','mask_conflict','edge_layout'])

def near_candidates(samples,radius,max_bucket,max_per_sample,budget_callback=None):
 # Index only whole-image hashes; query all transformations against that index.
 # This bounds memory by N*(radius+1), not N*transforms*(radius+1).
 chunks=radius+1;bounds=[(64*i//chunks,64*(i+1)//chunks) for i in range(chunks)];index=defaultdict(list);edges={};truncated=set();counts=Counter();overflow=set()
 for s in sorted(samples,key=lambda r:r['sample_id']):
  sid=s['sample_id'];h=int(s['phash'],16)
  for ix,(lo,hi) in enumerate(bounds):
   key=(ix,(h>>lo)&((1<<(hi-lo))-1));bucket=index[key]
   if len(bucket)>=max_bucket:overflow.add(key);truncated.add(sid);truncated.update(x[0] for x in bucket)
   else:bucket.append((sid,h))
 for number,s in enumerate(sorted(samples,key=lambda r:r['sample_id'])):
  if budget_callback and number%256==0:budget_callback()
  sid=s['sample_id']
  for transform,hx in s.get('hash_variants',[]):
   h=int(hx,16);candidates=set()
   for ix,(lo,hi) in enumerate(bounds):
    key=(ix,(h>>lo)&((1<<(hi-lo))-1))
    if key in overflow:truncated.add(sid)
    candidates.update(index.get(key,[]))
   for other,oh in sorted(candidates):
    if other==sid:continue
    pair=tuple(sorted((sid,other)));distance=(h^oh).bit_count()
    if distance>radius:continue
    if pair not in edges and (counts[sid]>=max_per_sample or counts[other]>=max_per_sample):truncated.update(pair);continue
    item={'left_id':other,'right_id':sid,'hamming_distance':distance,'left_transform':'identity','right_transform':transform}
    if pair not in edges:edges[pair]=item;counts[sid]+=1;counts[other]+=1
    elif distance<edges[pair]['hamming_distance']:edges[pair]=item
 return [edges[k] for k in sorted(edges)],truncated


def near_audit(ctx):
 import numpy as np
 c=ctx['cfg'];valid=[s for s in ctx['samples'] if s['decode_status']=='PASS'];candidates,truncated=near_candidates(valid,c['near_hamming_radius'],c['max_bucket'],c['max_candidates_per_sample'],lambda:check_budget(ctx))
 review=evidence_rows(ctx,'duplicate_reviews.csv');rv={tuple(sorted((r['left_id'],r['right_id']))):r for r in review};assert_true(len(rv)==len(review),'Duplicate near-review pair')
 rows=[]
 for edge in candidates:
  a,b=ctx['byid'][edge['left_id']],ctx['byid'][edge['right_id']]
  if a.get('decoded_image_sha256')==b.get('decoded_image_sha256'):continue
  aa=np.frombuffer(base64.b64decode(a['thumbnail']),dtype=np.uint8).astype(float);bb=np.frombuffer(base64.b64decode(b['thumbnail']),dtype=np.uint8).astype(float)
  den=np.linalg.norm(aa-aa.mean())*np.linalg.norm(bb-bb.mean());ncc=float(np.dot(aa-aa.mean(),bb-bb.mean())/den) if den else None
  r=rv.get(tuple(sorted((a['sample_id'],b['sample_id']))));decision='PENDING_REVIEW'
  if r:
   assert_true(evidence_ok(ctx,r) and r['left_sha256']==ctx['byid'][r['left_id']]['image_sha256'] and r['right_sha256']==ctx['byid'][r['right_id']]['image_sha256'],'Invalid/stale duplicate review')
   assert_true(r['decision'] in {'SAME_ACQUISITION','DISTINCT_ACQUISITION','UNRESOLVED'},'Invalid duplicate review decision');decision=r['decision']
  confidence='HIGH_SIMILARITY_CANDIDATE' if edge['hamming_distance']<=2 and ncc is not None and ncc>=c['near_confirm_ncc'] else 'CANDIDATE_ONLY'
  rows.append({**edge,'thumbnail_ncc':ncc,'confidence':confidence,'decision':decision,'proof_of_identity':False})
  if decision!='DISTINCT_ACQUISITION':ctx['uf'].union(a['sample_id'],b['sample_id'])
  if decision in {'PENDING_REVIEW','UNRESOLVED'}:
   for s in [a,b]:quarantine(ctx,s['sample_id'],'NEAR_DUPLICATE_PENDING',confidence)
 for sid in sorted(truncated):quarantine(ctx,sid,'NEAR_INDEX_TRUNCATED','Candidate cap/common hash bucket exceeded; resolve with stronger provenance or rerun larger caps')
 ctx.update(near=rows,near_truncated=truncated)
 cwrite(ctx['run']/'near_duplicates.csv',rows,['left_id','right_id','hamming_distance','left_transform','right_transform','thumbnail_ncc','confidence','decision','proof_of_identity'])
 jwrite(ctx['run']/'near_index_report.json',{'method':'bounded 64-bit multi-index hashing with rotations, flips and five crop windows','all_pair_scan':False,'candidate_edges':len(rows),'truncated_samples':len(truncated),'arbitrary_crop_recall':'NOT_GUARANTEED; requires parent/site/session provenance','automatic_identity_proof':False,'uncapped_hamming_retrieval':'pigeonhole guarantee for indexed transforms only','caps_block_finalization':bool(truncated)})

# %% Human annotation evidence, provenance, rights and legacy exposure
HARD_CATEGORIES=['joint','expansion joint','grout/tile seam','stain','shadow','scratch','paint edge','water mark','cable/wire','rough texture','aggregate boundary','masonry joint','image border','vegetation/debris','compression artifact','other']
REVIEW_FIELDS=['reviewer_id','reviewed_utc','evidence_path','evidence_sha256']
TEMPLATES={
 'lineage_reviews.csv':['sample_id','image_sha256','original_source_id','site_id','session_id','parent_id','original_image_id','crop_box','source_evidence','independence_rationale','legacy_exposure']+REVIEW_FIELDS,
 'annotation_reviews.csv':['sample_id','image_sha256','mask_sha256','decision','mask_complete','expert','hard_negative_category','thin_crack','incomplete_mask','junction_ambiguity','border_ambiguity','occlusion','notes']+REVIEW_FIELDS,
 'annotation_adjudications.csv':['sample_id','image_sha256','decision','mask_complete','expert','hard_negative_category','resolution']+REVIEW_FIELDS,
 'duplicate_reviews.csv':['left_id','right_id','left_sha256','right_sha256','decision','notes']+REVIEW_FIELDS,
 'pair_overrides.csv':['sample_id','image_sha256','mask_relative_path','mask_sha256','notes']+REVIEW_FIELDS,
 'source_rights.csv':['original_source_id','source_url','license_name','license_text_path','license_text_sha256','research_use','redistribution','conditions','reviewer_resources']+REVIEW_FIELDS,
 'approvals.csv':['gate_id','plan_sha256','decision','population_rationale','fixed_N_rationale']+REVIEW_FIELDS}

ANNOTATION_MANUAL='''# Annotation manual v1 — actual human review required

Curator-only dataset quality audit. Do not inspect model predictions, uncertainty scores or calibration outcomes while constructing labels and units.

1. Inspect the original image and aligned mask at native resolution. Record sample_id, image SHA-256 and mask SHA-256 from the audit queue; never reuse an old review after bytes change.
2. Mark POSITIVE only when a real structural crack is visible. Segmentation/certification eligibility additionally requires a complete aligned binary crack mask. Preserve thin cracks and small ground-truth components. A classification-positive SDNET image without a segmentation mask is not a topology-labelled positive.
3. Mark NEGATIVE only after an expert checks the complete visible image and records absence of a crack. All-zero source masks, folder names, filename tokens and missing masks are insufficient. Only an adjudicated complete negative can request a virtual all-zero mask.
4. Mark UNKNOWN for incomplete, partial, ignore-labelled, disputed, occluded or uncertain content. Record thin cracks, incomplete masks, junction and border ambiguity, occlusion and notes separately. Do not map UNKNOWN to negative.
5. Choose a hard-negative category from the locked list only after confirming absence of a real crack. Category presence alone is not a negative label. Positive classification examples may be retained as descriptive metadata but not as pixel ground truth.
6. A deterministic label-blind subset of min(N, max(ceil(0.20*N),30)) auditable images receives a second independent review, plus every disagreement. Reviewers must have distinct IDs; blind the second reviewer to the first decision. Evidence must record this independence. Any disagreement requires a third, distinct expert adjudicator and a written resolution. Unresolved cases remain UNKNOWN. This conservative image-level rule also covers at least the same fraction of a singleton-unit population; certification unit coverage is checked separately.
7. Valid decisions are POSITIVE, NEGATIVE or UNKNOWN. mask_complete and expert are YES/NO. Include reviewer ID, actual review time and a local evidence document with its SHA-256. Templates are blank requests, never simulated annotations or signatures.
8. Corrected masks are a dataset change. Do not edit raw inputs in place. Create a new reviewed data handoff and rerun fingerprints; retain previous versions and rationales.

No reviewer identity, legal permission, IID claim or scientific sign-off is synthesized by this notebook.
'''

def annotation_audit(ctx):
 samples=ctx['samples'];run=ctx['run'];c=ctx['cfg'];queue=[s for s in samples if s['decode_status']=='PASS']
 n=len(queue);need=min(n,max(math.ceil(.2*n),30));double={s['sample_id'] for s in sorted(queue,key=lambda s:stable('double_review',c['seed'],s['sample_id']))[:need]}
 imports=evidence_rows(ctx,'annotation_reviews.csv');groups=defaultdict(list)
 for r in imports:
  assert_true(r.get('sample_id') in ctx['byid'],'Unknown annotation sample ID');s=ctx['byid'][r['sample_id']]
  assert_true(r.get('image_sha256')==s['image_sha256'] and (r.get('mask_sha256') or None)==s.get('mask_sha256') and evidence_ok(ctx,r),'Invalid/stale annotation evidence: '+r['sample_id'])
  assert_true(r['decision'] in {'POSITIVE','NEGATIVE','UNKNOWN'} and r['expert'] in {'YES','NO'} and r['mask_complete'] in {'YES','NO'},'Invalid annotation enums')
  assert_true(r.get('hard_negative_category','') in ['']+HARD_CATEGORIES,'Unknown hard-negative category')
  groups[r['sample_id']].append(r)
 adjudications=evidence_rows(ctx,'annotation_adjudications.csv');adj={r['sample_id']:r for r in adjudications};assert_true(len(adj)==len(adjudications),'Duplicate adjudication sample')
 audit=[];agreement=[]
 for s in samples:
  sid=s['sample_id'];reviews=groups.get(sid,[]);assert_true(len({r['reviewer_id'] for r in reviews})==len(reviews),'One reviewer has duplicate records for '+sid)
  decisions={(r['decision'],r['mask_complete'],r.get('hard_negative_category','')) for r in reviews};disagree=len(decisions)>1
  if disagree:double.add(sid)
  required=2 if sid in double else 1;valid=len(reviews)>=required;chosen=reviews[0] if reviews else None;resolution='AGREED' if valid and not disagree else 'PENDING'
  if disagree:
   a=adj.get(sid)
   valid=bool(a and evidence_ok(ctx,a) and a['image_sha256']==s['image_sha256'] and a['expert']=='YES' and a['reviewer_id'] not in {r['reviewer_id'] for r in reviews} and a.get('resolution'))
   chosen=a if valid else None;resolution='EXPERT_ADJUDICATED' if valid else 'UNRESOLVED_DISAGREEMENT'
  if chosen and valid:
   assert_true(chosen['decision'] in {'POSITIVE','NEGATIVE','UNKNOWN'},'Invalid adjudicated decision')
   if chosen['decision']=='POSITIVE' and chosen['mask_complete']=='YES' and s.get('mask_pixels',0)>0 and s['decode_status']=='PASS':s['label']='positive'
   elif chosen['decision']=='NEGATIVE' and chosen['mask_complete']=='YES' and chosen['expert']=='YES' and s['decode_status']=='PASS' and s.get('mask_pixels',0)==0:s['label']='negative'
  s['review_status']='COMPLETE' if s['label'] in {'positive','negative'} else 'PENDING_OR_INELIGIBLE';s['hard_negative_category']=chosen.get('hard_negative_category','') if chosen and s['label']=='negative' else ''
  s['double_review_complete']=bool(len(reviews)>=2 and resolution in {'AGREED','EXPERT_ADJUDICATED'})
  s['zero_mask_authorized']=s['label']=='negative' and s.get('mask_path') is None and s['review_status']=='COMPLETE'
  if disagree and not valid:quarantine(ctx,sid,'ANNOTATION_DISAGREEMENT','Needs a distinct expert adjudicator')
  row={'sample_id':sid,'image_sha256':s['image_sha256'],'mask_sha256':s.get('mask_sha256'),'source_annotation_state':s['annotation_state'],'double_review_required':sid in double,'review_count':len(reviews),'agreement':resolution,'final_label':s['label'],'review_status':s['review_status'],'hard_negative_category':s['hard_negative_category'],'zero_mask_authorized':s['zero_mask_authorized']}
  for flag in ['thin_crack','incomplete_mask','junction_ambiguity','border_ambiguity','occlusion','notes']:row[flag]='; '.join(sorted({r.get(flag,'') for r in reviews if r.get(flag)}))
  audit.append(row)
  if sid in double:agreement.append({'sample_id':sid,'reviewer_ids':';'.join(r['reviewer_id'] for r in reviews),'required_reviews':2,'observed_reviews':len(reviews),'agreement':resolution,'double_review_complete':s['double_review_complete']})
 cwrite(run/'annotation_audit.csv',audit,list(audit[0]) if audit else ['sample_id','review_status']);cwrite(run/'reviewer_agreement.csv',agreement,['sample_id','reviewer_ids','required_reviews','observed_reviews','agreement','double_review_complete'])
 twrite(run/'annotation_manual_v1.md',ANNOTATION_MANUAL)
 twrite(run/'hard_negative_spec.md','# Hard-negative specification\n\nA complete visible image must be independently expert-confirmed no-crack before category assignment. Partial/unknown labels are ineligible. The development subset is an alias of development_policy; the hard-negative test uses distinct held-out groups. No shared source image, crop, parent, session or unresolved similarity group may cross roles. The category list is descriptive and does not itself establish class membership.\n')
 twrite(run/'hard_negative_categories.yaml','version: "1.0"\ncategories:\n'+''.join('  - '+json.dumps(x)+'\n' for x in HARD_CATEGORIES))
 ctx['double_review_required']=double;ctx['annotation_complete']=all(s['review_status']=='COMPLETE' for s in queue) and all(ctx['byid'][sid]['double_review_complete'] for sid in double)


def provenance_and_rights(ctx):
 run=ctx['run'];samples=ctx['samples'];facts=evidence_rows(ctx,'lineage_reviews.csv');fm={r['sample_id']:r for r in facts};assert_true(len(fm)==len(facts),'Duplicate lineage sample ID')
 rights=evidence_rows(ctx,'source_rights.csv');rm={r['original_source_id']:r for r in rights};assert_true(len(rm)==len(rights),'Duplicate rights source ID')
 for r in rights:
  assert_true(evidence_ok(ctx,r),'Invalid rights evidence for '+r['original_source_id'])
  assert_true(r['research_use'] in {'PERMITTED','PROHIBITED','UNKNOWN'} and r['redistribution'] in {'PERMITTED','PROHIBITED','UNKNOWN'},'Invalid source-rights states')
  assert_true(r.get('source_url') and r.get('license_name') and re.fullmatch('[0-9a-f]{64}',r.get('license_text_sha256','')),'Rights record needs source URL, license name and license-text fingerprint')
  license_path=require_under(Path(ctx['cfg']['evidence_dir'])/r.get('license_text_path',''),ctx['cfg']['evidence_dir'])
  assert_true(license_path.is_file() and sha_file(license_path)==r['license_text_sha256'],'License-text file/hash mismatch')
  assert_true(r['research_use']!='PERMITTED' or bool(r.get('reviewer_resources')),'Permitted-use record must document reviewer resources')
 lineage=[];legacy=[];keys={};weak={}
 for s in samples:
  sid=s['sample_id'];r=fm.get(sid);site=session=parent=original='';rationale='';evidenced=False
  if r:
   assert_true(evidence_ok(ctx,r) and r['image_sha256']==s['image_sha256'],'Invalid/stale lineage evidence: '+sid)
   assert_true(r['original_source_id'] not in {'','UNKNOWN','aggregation','crack segmentation dataset'},'Aggregation is not an independent original source')
   assert_true(r['legacy_exposure'] in {'CLEAR','EXPOSED','UNKNOWN'},'Legacy exposure must be CLEAR, EXPOSED or UNKNOWN')
   s['original_source_id']=r['original_source_id'];site=r.get('site_id','');session=r.get('session_id','');parent=r.get('parent_id','');original=r.get('original_image_id','');rationale=r.get('independence_rationale','');evidenced=bool(r.get('source_evidence'))
  source=s['original_source_id'];highest=next(((level,value) for level,value in [('site',site),('session',session),('parent',parent),('original',original)] if value),('UNKNOWN',''))
  # Unknown parent/acquisition IDs are a conservative source-wide leakage group, not singleton IID observations.
  key=(source,highest[0],highest[1]) if evidenced and highest[1] else ('UNKNOWN_ACQUISITION',source if source!='UNKNOWN' else s['collection'])
  link_keys=[key]+[(source,level,value) for level,value in [('site',site),('session',session),('parent',parent),('original',original)] if evidenced and value]
  for link_key in link_keys:
   if link_key in keys:ctx['uf'].union(sid,keys[link_key])
   else:keys[link_key]=sid
  stem=PurePosixPath(s['image_relative_path']).stem
  base=re.sub(r'[_\-](?:crop|patch|tile)[_\-]?\d+(?:[_\-]\d+)*$','',stem,flags=re.I)
  if base!=stem:
   wk=(s['collection'],str(PurePosixPath(s['image_relative_path']).parent),base)
   if wk in weak:ctx['uf'].union(sid,weak[wk])
   else:weak[wk]=sid
  lic=rm.get(source,{});s.update(site_id=site,session_id=session,parent_id=parent,original_image_id=original,highest_acquisition_level=highest[0],highest_acquisition_id=highest[1],lineage_status='DOCUMENTED' if evidenced and highest[1] else 'UNKNOWN',independence_rationale=rationale,legacy_exposure=r['legacy_exposure'] if r else 'UNKNOWN',research_use=lic.get('research_use','UNKNOWN'),redistribution=lic.get('redistribution','UNKNOWN'))
  lineage.append({'sample_id':sid,'original_source_id':source,'source_hint_unverified':s['original_source_hint'],'site_id':site,'session_id':session,'parent_id':parent,'original_image_id':original,'crop_box':r.get('crop_box','') if r else '', 'highest_level':highest[0],'lineage_status':s['lineage_status'],'independence_rationale':rationale,'weak_filename_crop_hint':base if base!=stem else ''})
  legacy.append({'sample_id':sid,'legacy_exposure':s['legacy_exposure'],'claim_status':'REVIEWED_EVIDENCE' if r else 'UNKNOWN; Phase01 found zero original legacy records','fresh_test_claim_allowed':s['legacy_exposure']=='CLEAR'})
 # Exact duplicate copies inherit ORIGINAL-SOURCE CANDIDATES for exclusion, never automatic licensing or provenance approval.
 for group in ctx['uf'].groups():
  sources=sorted({ctx['byid'][sid]['original_source_id'] for sid in group if ctx['byid'][sid]['original_source_id']!='UNKNOWN'})
  for sid in group:ctx['byid'][sid]['group_source_candidates']=sources
 ctx['rights']=rm
 registry=[]
 for source in sorted(set(ORIGINAL_SOURCES)|set(rm)|{s['original_source_id'] for s in samples}):
  rr=rm.get(source,{});registry.append({'original_source_id':source,'observed_confirmed_samples':sum(s['original_source_id']==source for s in samples),'observed_hint_samples':sum(s['original_source_hint']==source for s in samples),'research_use':rr.get('research_use','UNKNOWN'),'redistribution':rr.get('redistribution','UNKNOWN'),'license_name':rr.get('license_name','UNVERIFIED'),'source_url':rr.get('source_url',''),'evidence_sha256':rr.get('evidence_sha256',''),'reviewer_resources':rr.get('reviewer_resources',''),'aggregation_rights_inherited':False})
 cwrite(run/'dataset_registry.csv',registry,list(registry[0]));cwrite(run/'parent_lineage.csv',lineage,list(lineage[0]) if lineage else ['sample_id']);cwrite(run/'legacy_exposure_registry.csv',legacy,['sample_id','legacy_exposure','claim_status','fresh_test_claim_allowed'])
 jwrite(run/'mrc_reuse_decision.json',{'decision':'CLEAN_RETRAINING_ROUTE_PROVISIONAL','original_legacy_files_found_in_phase01':0,'checkpoint_reproduction_verified':False,'historical_11298_pairs':'UNVERIFIED_COLLECTION_REFERENCE; not current unique independent count','freshness':'UNKNOWN unless actual lineage evidence marks CLEAR','aggregate_collection_independent_source':False,'training_authorization':'Not granted by this decision'})

# %% Conservative leakage groups and distinct certification units

def make_units(ctx):
 c=ctx['cfg'];units=[];qids={q['sample_id'] for q in ctx['quarantine']};samples=ctx['samples']
 for group in ctx['uf'].groups():
  members=[ctx['byid'][sid] for sid in group];gid=stable('split',group);uid=stable('unit',group)
  source_candidates=sorted({v for s in members for v in ([s['original_source_id']] if s['original_source_id']!='UNKNOWN' else [])}|{v for s in members for v in s.get('group_source_candidates',[])})
  group_reasons=[]
  if any(s['sample_id'] in qids for s in members):group_reasons.append('QUARANTINED_MEMBER')
  if any(s['lineage_status']!='DOCUMENTED' or not s['independence_rationale'] for s in members):group_reasons.append('INDEPENDENCE_UNRESOLVED')
  if any(s['original_source_id']=='UNKNOWN' for s in members):group_reasons.append('ORIGINAL_SOURCE_UNKNOWN')
  if any(s['research_use']!='PERMITTED' for s in members):group_reasons.append('RESEARCH_RIGHTS_UNRESOLVED')
  if any(s['legacy_exposure']!='CLEAR' for s in members):group_reasons.append('LEGACY_EXPOSURE_UNRESOLVED')
  eligible=[s for s in members if s['decode_status']=='PASS' and s['pair_status']!='AMBIGUOUS' and s['review_status']=='COMPLETE' and s['label'] in {'positive','negative'}]
  if not eligible:group_reasons.append('NO_ADJUDICATED_REPRESENTATIVE')
  # Eligibility is frozen first; selection uses only seed and stable ID, NEVER labels/scores/errors.
  pool=eligible if eligible else members;rep=min(pool,key=lambda s:stable('representative',c['seed'],s['sample_id']))
  level=next((level for level in ['site','session','parent','original'] if any(s['highest_acquisition_level']==level for s in members)),'UNKNOWN')
  row={'certification_unit_id':uid,'split_group_id':gid,'representative_sample_id':rep['sample_id'],'member_count':len(members),'original_source_ids':';'.join(source_candidates),'highest_unit_level':level,'representative_label':rep['label'] if eligible else 'UNKNOWN','representative_rule':'Minimum SHA256(seed, sample_id) among predeclared eligible images; independent of label and outcome','eligibility_status':'ELIGIBLE_PENDING_APPROVAL' if not group_reasons else 'INELIGIBLE','exclusion_reasons':';'.join(group_reasons),'double_review_complete':rep['double_review_complete'],'hard_negative_category':rep['hard_negative_category']}
  units.append(row)
  for s in members:s.update(split_group_id=gid,certification_unit_id=uid,is_representative=s['sample_id']==rep['sample_id'])
 # Additional unit-level double-review coverage. It can increase the human queue, never create reviews.
 eligible_units=[u for u in units if u['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL'];n=len(eligible_units);need=min(n,max(math.ceil(.2*n),30));unit_review=set()
 for u in sorted(eligible_units,key=lambda u:stable('unit_double',c['seed'],u['certification_unit_id']))[:need]:
  unit_review.add(u['representative_sample_id'])
  if not u['double_review_complete']:u['eligibility_status']='INELIGIBLE';u['exclusion_reasons']='UNIT_DOUBLE_REVIEW_PENDING'
 ctx['unit_review_required']=unit_review;ctx['units']=sorted(units,key=lambda u:u['certification_unit_id']);ctx['unit_byid']={u['certification_unit_id']:u for u in units}
 cwrite(ctx['run']/'certification_units.csv',ctx['units'],list(ctx['units'][0]) if units else ['certification_unit_id','split_group_id','representative_sample_id','eligibility_status'])
 write_samples(ctx)
 twrite(ctx['run']/'independence_assessment.md',f'''# Independence assessment

Observed images: {len(samples)}. Conservative split groups / proposed certification units: {len(units)}.
Eligible units after current evidence: {sum(u['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL' for u in units)}.

The IDs have different meanings even when there is one unit per conservative split group. Exact copies, unresolved near copies and documented acquisition identifiers are unioned transitively. The highest documented site, session, parent or original image is used; every held-out group's other views are excluded from training. Unknown acquisitions are grouped source-wide (collection-wide when provenance is unknown), not assigned singleton IID status. Cross-source copies stay in a single group.

Curation does not prove IID. A signed population and independence rationale must address between-unit dependence, sampling and class-conditional population stability. Multiple views per site are not counted as independent. A less conservative conditional-on-site design requires an explicit scientific amendment; it is not silently selected here. Manual provenance is also necessary for crops outside the bounded perceptual candidate transforms. No raw image count is reported as an independent sample size.
''')

# %% Capacity planning and disjoint provisional role manifests
ROLE_COLS=['sample_id','split_group_id','certification_unit_id','collection','image_relative_path','image_sha256','mask_relative_path','mask_sha256','zero_mask_authorized','label','is_representative','role','partition_status','eligibility_status','sealed_label_ref']

def assign_splits(ctx):
 c=ctx['cfg'];run=ctx['run'];units=ctx['units'];assigned={};targets=c['external_source_ids'];assert_true(len(targets)==len(set(targets)) and all(x not in {'UNKNOWN','crack segmentation dataset','aggregation'} for x in targets),'External source selection must contain unique ORIGINAL source IDs')
 members=defaultdict(list)
 for s in ctx['samples']:members[s['certification_unit_id']].append(s)
 external=set();unresolved=set()
 for u in units:
  ss=members[u['certification_unit_id']];hints=set(u['original_source_ids'].split(';'))|{s['original_source_hint'] for s in ss}
  if set(targets)&hints:external.add(u['certification_unit_id'])
  if any(s['original_source_id']=='UNKNOWN' for s in ss):unresolved.add(u['certification_unit_id'])
 def put(u,role):assert_true(u['certification_unit_id'] not in assigned,'Unit assigned twice');assigned[u['certification_unit_id']]=role
 def order(seq,salt):return sorted(seq,key=lambda u:stable(salt,c['seed'],u['certification_unit_id']))
 qids={q['sample_id'] for q in ctx['quarantine']}
 def domain_documented(u):
  return all(s['original_source_id']!='UNKNOWN' and s['lineage_status']=='DOCUMENTED' and s['research_use']=='PERMITTED' and s['decode_status']=='PASS' and s['sample_id'] not in qids for s in members[u['certification_unit_id']])
 # Unlabelled domain pools are selected by group IDs BEFORE label-based role assignment.
 target_candidates=[u for u in units if u['certification_unit_id'] in external and domain_documented(u)]
 for u in order(target_candidates,'target_unlabelled_label_blind')[:c['target_unlabeled_units']]:put(u,'target_unlabeled_pool')
 for u in units:
  if u['certification_unit_id'] in assigned:continue
  if u['certification_unit_id'] in external:put(u,'external_positive_test' if u['representative_label']=='positive' and u['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL' else 'reserve_pool')
  elif targets and u['certification_unit_id'] in unresolved:put(u,'reserve_pool')
 source_candidates=[u for u in units if u['certification_unit_id'] not in assigned and domain_documented(u)]
 source_pool=order(source_candidates,'source_unlabelled_label_blind')[:c['source_unlabeled_units']]
 for u in source_pool:put(u,'source_unlabeled_pool')
 eligible=[u for u in units if u['certification_unit_id'] not in assigned and u['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL']
 before=Counter(u['representative_label'] for u in eligible);reservations=Counter()
 # The hard-negative/corruption populations are declared separately before the internal sampling frame is frozen.
 for u in order([u for u in eligible if u['representative_label']=='negative' and u['hard_negative_category']],'hard_negative_holdout')[:c['hard_negative_test_units']]:put(u,'hard_negative_test');reservations[u['representative_label']]+=1
 for u in order([u for u in eligible if u['certification_unit_id'] not in assigned],'route_B_holdout')[:c['corruption_test_units']]:put(u,'corruption_test');reservations[u['representative_label']]+=1
 capacity={};details={}
 for label in ['positive','negative']:
  pool=order([u for u in eligible if u['representative_label']==label and u['certification_unit_id'] not in assigned],'internal_population_'+label)
  details[label]={'eligible_before_reservations':before[label],'source_unlabeled_reserved':sum(u['representative_label']==label for u in source_pool),'hard_negative_and_corruption_reserved':reservations[label],'remaining_internal_frame':len(pool)}
  for role,number in [('reserve_pool',c['reserve'][label]),('internal_test',c['internal_test'][label])]:
   take=pool[:number];pool=pool[number:]
   for u in take:put(u,role)
   details[label][role+'_requested']=number;details[label][role+'_actual']=len(take)
  capacity[label]=len(pool);take=pool[:c['calibration_target'][label]];pool=pool[c['calibration_target'][label]:]
  for u in take:put(u,'calibration')
  details[label].update(calibration_target=c['calibration_target'][label],calibration_actual=len(take),capacity_after_reservations=capacity[label],hard_floor=c['calibration_floor'][label],floor_shortfall=max(0,c['calibration_floor'][label]-len(take)),preferred_shortfall=max(0,c['calibration_target'][label]-len(take)))
 # Ineligible groups remain reserved; UNKNOWN provenance is never an invented target domain.
 for u in units:
  if u['certification_unit_id'] not in assigned and u['eligibility_status']!='ELIGIBLE_PENDING_APPROVAL':put(u,'reserve_pool')
 remaining=order([u for u in units if u['certification_unit_id'] not in assigned],'train_development')
 ndev=math.floor(len(remaining)*c['development_fraction']);dev=remaining[:ndev];train=remaining[ndev:]
 nmodel=math.floor(.60*ndev);nprob=math.floor(.20*ndev)
 for i,u in enumerate(dev):put(u,'development_model' if i<nmodel else 'development_probability' if i<nmodel+nprob else 'development_policy')
 for u in train:put(u,'train')
 roles={r:[] for r in ROLES};sealed=[]
 for u in units:
  uid=u['certification_unit_id'];role=assigned[uid]
  selected=([s for s in members[uid] if s['review_status']=='COMPLETE' and s['decode_status']=='PASS'] if role in DEVELOPMENT_ROLES else [ctx['byid'][u['representative_sample_id']]])
  for s in members[uid]:s['assigned_role']=role # Other held-out views are reserved with their group, never training.
  for s in selected:
   hidden=role in FINAL_ROLES or role in {'source_unlabeled_pool','target_unlabeled_pool'}
   row={k:s.get(k) for k in ROLE_COLS};row.update(role=role,partition_status='PROVISIONAL',eligibility_status=u['eligibility_status'],sealed_label_ref=stable('sealed',s['sample_id']) if hidden else '')
   if hidden:
    sealed.append({'sealed_label_ref':row['sealed_label_ref'],'sample_id':s['sample_id'],'label':s['label'],'mask_relative_path':s.get('mask_relative_path'),'mask_sha256':s.get('mask_sha256'),'zero_mask_authorized':s['zero_mask_authorized']});row.update(label=None,mask_relative_path=None,mask_sha256=None,zero_mask_authorized=None)
   roles[role].append(row)
 roles['development']=sum([roles[r] for r in ['development_model','development_probability','development_policy']],[])
 roles['hard_negative_development']=[{**r,'role':'hard_negative_development'} for r in roles['development_policy'] if ctx['byid'][r['sample_id']]['hard_negative_category'] and ctx['byid'][r['sample_id']]['label']=='negative']
 plan={'schema_version':'1.0','partition_status':'PROVISIONAL','fixed_seed':c['seed'],'unit_rule':'one label-blind representative per conservative acquisition group','source_quota_used':False,'actual_capacity':details,'external_original_source_ids':targets,'unlabelled_pool_counts':{role:sum(v==role for v in assigned.values()) for role in ['source_unlabeled_pool','target_unlabeled_pool']},'unlabelled_sampling_rule':'Label-blind unit-ID selection before labelled split allocation; target original sources explicitly declared; no test group reused','external_source_choice_status':'DECLARED_PENDING_REVIEW' if targets else 'UNRESOLVED','reserve_use':'Fixed reserve identities; NO outcome-triggered additions to calibration','calibration_outcomes_inspected':False,'fixed_N_approval':'PENDING_S2; actual calibration counts are proposals, not authorization','population_status':'CORPUS_FRAME_PROPOSAL_REQUIRES_IID_AND_MIXTURE_RATIONALE','floor_sufficient':all(details[x]['floor_shortfall']==0 for x in details),'preferred_target_met':all(details[x]['preferred_shortfall']==0 for x in details),'route':'B','hard_negative_development':'Alias subset of development_policy, not an independent role','development_union':'Compatibility union of model/probability/policy; no extra observations','unit_role_map':assigned}
 # Bind approvals to content and assignments, not timestamps or mount paths. A reviewer rerun must reproduce this digest.
 evidence_identity=[{k:s.get(k) for k in ['sample_id','image_sha256','mask_sha256','label','review_status','original_source_id','site_id','session_id','parent_id','research_use','legacy_exposure','split_group_id']} for s in ctx['samples']]
 review_evidence={name:evidence_rows(ctx,name) for name in TEMPLATES if name!='approvals.csv'}
 plan['review_basis_sha256']=hashlib.sha256(jb({'sample_state':evidence_identity,'review_evidence':review_evidence})).hexdigest()
 plan['plan_sha256']=hashlib.sha256(jb(plan)).hexdigest();ctx.update(roles=roles,plan=plan,assigned=assigned,sealed=sealed)
 jwrite(run/'calibration_sampling_plan.json',plan);write_parquet(run/'curator'/'sealed_labels.parquet',sealed)
 for r,rows in roles.items():cwrite(run/(r+'.csv'),rows,ROLE_COLS)
 twrite(run/'population_contract.md',f'''# Proposed population and sampling contract

Status: PROVISIONAL. Plan fingerprint: `{plan['plan_sha256']}`. Seed: {c['seed']}.

The internal frame consists of adjudicated representatives of documented, research-permitted, legacy-clear acquisition groups after label-blind source/target unlabeled pools, original-source external holdout, independent hard-negative and route-B corruption reservations. Fixed class-wise reserve and internal-test draws precede a calibration proposal. All orders use fixed seeded ID hashes, without model outputs, errors, confidence scores or outcome-dependent stopping. There are no per-source quotas. Development is then separated 60/20/20 by group for model, probability and policy development (rounding down the first two; small empty sets remain a visible capacity problem).

This is a finite-corpus partition proposal, not proof of population IID. S2 must specify the intended future class-conditional population, source mixture and acquisition process and justify why the remaining frame represents it. Conditioning away hard-negative reservations must be addressed; otherwise revise the scientifically reviewed plan before any outcomes. Source/site dependence and class balance cannot be solved by counting crops. The same frozen class-conditional frame supplies the internal test and calibration draw; test identities never replenish a short calibration set.

Counts and exact shortfalls are recorded in calibration_sampling_plan.json. Required available floor is 120 positive / 122 negative; preferred is 300 / 300. Accepted zero-failure minima from unchanged Phase01 helpers are 60 / 122; they are NOT replacement raw-availability floors. A shortfall blocks G03 and requests new independent data or a documented approved pre-outcome amendment. No automatic single-policy alternative or adaptive retry is enabled.

Only the representative of each held-out group is exported in its role manifest; every other view remains reserved with that group. External-source copies are excluded transitively, including aggregate copies. Unknown provenance prevents a clean held-out-source claim. Source and target unlabeled pools use documented original-source domains and label-blind group-ID draws before labelled-role assignment, and cannot contain calibration/test groups. Target provenance is never invented for an UNKNOWN source. The domain sampling frame still requires human review before downstream use.

Final labels remain in the private curator artifact. The raw Kaggle dataset itself is readable by its owner: this is an operational access contract, not a cryptographic sandbox. The shared development loader refuses PROVISIONAL or held-out manifests. Phase02 never evaluates a model or opens calibration outcomes.
''')
 return {label:details[label] for label in details}

# %% Minimal metric and preprocessing primitives (not Phase04)

def letterbox(image,mask=None,size=448):
 import numpy as np
 from PIL import Image
 h,w=image.shape[:2];scale=min(size/h,size/w);nh=max(1,round(h*scale));nw=max(1,round(w*scale));top=(size-nh)//2;left=(size-nw)//2
 out=np.zeros((size,size,3),dtype=np.uint8);valid=np.zeros((size,size),dtype=bool);valid[top:top+nh,left:left+nw]=True
 out[top:top+nh,left:left+nw]=np.asarray(Image.fromarray(image).resize((nw,nh),Image.Resampling.BILINEAR))
 mout=None
 if mask is not None:
  assert_true(mask.shape==(h,w),'Native mask/image alignment mismatch');mout=np.zeros((size,size),dtype=np.uint8);mout[top:top+nh,left:left+nw]=np.asarray(Image.fromarray(mask.astype(np.uint8)).resize((nw,nh),Image.Resampling.NEAREST))
 return out,mout,valid,{'scale':scale,'resized_height':nh,'resized_width':nw,'top':top,'left':left,'original_height':h,'original_width':w}

def skeleton(mask,valid=None):
 import numpy as np
 from skimage.morphology import skeletonize
 a=np.asarray(mask,dtype=bool)
 if valid is not None:a=a&valid
 return skeletonize(a,method='zhang')

def connected_components(mask,valid=None):
 import numpy as np
 from scipy.ndimage import label
 a=np.asarray(mask,dtype=bool)
 if valid is not None:a=a&valid
 return label(a,structure=np.ones((3,3),dtype=np.uint8))

def cldice(pred,truth,valid=None):
 import numpy as np
 p=np.asarray(pred,dtype=bool);t=np.asarray(truth,dtype=bool)
 assert_true(p.shape==t.shape,'clDice dimensions differ')
 if valid is not None:p=p&valid;t=t&valid
 if not p.any() and not t.any():return 1.0
 if not p.any() or not t.any():return 0.0
 sp,st=skeleton(p),skeleton(t);precision=float((sp&t).sum()/max(1,sp.sum()));recall=float((st&p).sum()/max(1,st.sum()))
 return 2*precision*recall/(precision+recall) if precision+recall else 0.0

def valid_prediction_components(probability,valid):
 import numpy as np
 lab,n=connected_components((np.asarray(probability)>=.55)&valid);keep=[]
 for k in range(1,n+1):
  component=lab==k
  if component.sum()>=20 and probability[component].mean()>=.55 and skeleton(component).sum()>=5:keep.append(k)
 return np.isin(lab,keep),len(keep)

def metric_tests(ctx=None):
 import numpy as np
 tests=[]
 def check(name,ok):tests.append({'name':name,'status':'PASS' if ok else 'FAIL'});assert_true(ok,'Primitive test failed: '+name)
 im=np.zeros((20,40,3),np.uint8);mask=np.zeros((20,40),np.uint8);mask[10,5:35]=1
 x,m,v,meta=letterbox(im,mask);check('448_aspect_valid_padding',x.shape==(448,448,3) and v.sum()==224*448 and meta['top']==112)
 check('nearest_binary_mask',set(np.unique(m))<={0,1});check('cldice_identical',cldice(m,m,v)==1)
 empty=np.zeros((10,10),bool);line=empty.copy();line[4,2:8]=1
 check('empty_empty_defined',cldice(empty,empty)==1);check('one_empty_defined',cldice(line,empty)==0 and cldice(empty,line)==0)
 check('small_GT_preserved',skeleton(line).sum()==6);diag=np.eye(3,dtype=bool);check('8_connected',connected_components(diag)[1]==1)
 prob=np.zeros((20,20));prob[5:8,2:12]=.55;valid=np.ones_like(prob,dtype=bool);kept,n=valid_prediction_components(prob,valid);check('threshold_equality_and_component',n==1 and kept.sum()==30)
 valid[:]=False;check('padding_excluded',valid_prediction_components(prob,valid)[1]==0)
 report={'scope':'Minimal binary/letterbox/component/skeleton/clDice primitives only','status':'PASS','tests':tests,'GT_component_pruning':False,'Phase04_branch_LWBR_engine':'NOT_IMPLEMENTED_IN_PHASE02','locks':{'size':448,'probability_threshold':.55,'minimum_predicted_component_area':20,'minimum_predicted_skeleton_pixels':5,'branch_matching_tolerance':4,'branch_coverage_threshold':.75,'LWBR_failure_threshold':.9}}
 if ctx:jwrite(ctx['run']/'metric_primitives_test_report.json',report)
 return report

# %% Schema, disjointness and approval validation

def validate_roles(ctx):
 roles=ctx['roles'];seen={};sidseen={};group_roles=defaultdict(set);issues=[]
 for role,rows in roles.items():
  if role in {'development','hard_negative_development'}:continue
  for r in rows:
   sid=r['sample_id'];uid=r['certification_unit_id'];gid=r['split_group_id']
   assert_true(sid in ctx['byid'] and uid in ctx['unit_byid'],'Manifest references an unknown ID')
   assert_true(ctx['byid'][sid]['split_group_id']==gid and ctx['byid'][sid]['certification_unit_id']==uid,'Manifest group/unit mismatch')
   assert_true(sid not in sidseen,'Sample occurs twice in independent role manifests');sidseen[sid]=role
   group_roles[gid].add(role)
   if role in FINAL_ROLES:
    assert_true(r['is_representative'] and uid not in seen,'Held-out unit lacks a unique representative');seen[uid]=role
    assert_true(r['label'] is None and r['mask_relative_path'] is None,'Held-out label leak into model-facing role CSV')
   if r.get('zero_mask_authorized'):assert_true(ctx['byid'][sid]['label']=='negative' and ctx['byid'][sid]['review_status']=='COMPLETE','Unauthorized synthetic negative mask')
 assert_true(all(len(v)==1 for v in group_roles.values()),'Leakage group crosses independent roles')
 dev={r['sample_id'] for k in ['development_model','development_probability','development_policy'] for r in roles[k]}
 assert_true({r['sample_id'] for r in roles['development']}==dev,'Compatibility development union is wrong')
 assert_true({r['sample_id'] for r in roles['hard_negative_development']}<={r['sample_id'] for r in roles['development_policy']},'Hard-negative development must be linked to development_policy')
 external=set(ctx['cfg']['external_source_ids'])
 for role in DEVELOPMENT_ROLES:
  for r in roles[role]:
   s=ctx['byid'][r['sample_id']];assert_true(not(external&set(s.get('group_source_candidates',[]))) and s['original_source_id'] not in external and s['original_source_hint'] not in external,'Held-out original source enters development')
 report={'status':'PASS','sample_id_unique':len({s['sample_id'] for s in ctx['samples']})==len(ctx['samples']),'split_group_disjoint':True,'certification_unit_disjoint':True,'permitted_aliases':['development = union(model,probability,policy)','hard_negative_development subset development_policy'],'partition_status':'PROVISIONAL','scientific_approval_implied':False}
 assert_true(report['sample_id_unique'],'Duplicate sample IDs');jwrite(ctx['run']/'split_validation.json',report);return report

def validate_and_gate(ctx):
 validate_roles(ctx);run=ctx['run'];plan=ctx['plan'];approvals=evidence_rows(ctx,'approvals.csv');app={r['gate_id']:r for r in approvals};assert_true(len(app)==len(approvals),'Duplicate approval gate')
 def signed(g):
  r=app.get(g,{});return bool(r.get('decision')=='APPROVE' and r.get('plan_sha256')==plan['plan_sha256'] and evidence_ok(ctx,r) and r.get('population_rationale') and r.get('fixed_N_rationale'))
 active_ids={r['certification_unit_id'] for role,rows in ctx['roles'].items() if role not in {'reserve_pool','source_unlabeled_pool','target_unlabeled_pool'} for r in rows}
 active_samples={r['sample_id'] for role,rows in ctx['roles'].items() if role not in {'reserve_pool','source_unlabeled_pool','target_unlabeled_pool'} for r in rows}
 eligible_all=all(ctx['unit_byid'][uid]['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL' for uid in active_ids) and bool(active_ids)
 active_review_ok=all(ctx['byid'][sid]['review_status']=='COMPLETE' for sid in active_samples) and all(ctx['byid'][sid]['double_review_complete'] for sid in active_samples & ctx['double_review_required'])
 data_ok=ctx['cfg']['run_mode']=='FULL' and ctx['raw_complete'] and eligible_all and active_review_ok and not ({q['sample_id'] for q in ctx['quarantine']}&active_samples) and not (set(ctx['near_truncated'])&active_samples) and bool(ctx['cfg']['external_source_ids'])
 required_nonempty=['train','development_model','development_probability','development_policy','calibration','internal_test','external_positive_test','hard_negative_test','corruption_test']
 roles_ok=all(ctx['roles'][r] for r in required_nonempty) and len(ctx['roles']['hard_negative_test'])>=ctx['cfg']['hard_negative_test_units'] and len(ctx['roles']['corruption_test'])>=ctx['cfg']['corruption_test_units']
 reservations_ok=all(plan['actual_capacity'][x][role+'_actual']==plan['actual_capacity'][x][role+'_requested'] for x in ['positive','negative'] for role in ['reserve_pool','internal_test'])
 technical_g02=data_ok;technical_g03=plan['floor_sufficient'] and reservations_ok and roles_ok
 final=technical_g02 and technical_g03 and all(signed(g) for g in ['G02','G03','S2','S6'])
 ctx['partition_status']='FINAL' if final else 'PROVISIONAL';plan['partition_status']=ctx['partition_status'];plan['fixed_N_approval']='APPROVED_S2_FOR_THIS_PLAN' if signed('S2') else 'PENDING_S2'
 # Digest refers to the pre-approval proposal; do not rehash after attaching decision status.
 gates=[]
 for gate,technical,reason in [('G02',technical_g02,'Full fingerprints, rights, annotation, provenance, independent units and external-source isolation'),('G03',technical_g03,'Post-reservation calibration floors, fixed count plan and nonempty required development/test roles')]:gates.append({'gate_id':gate,'technical_status':'PASS' if technical else 'BLOCKED','human_status':'SIGNED' if signed(gate) else 'PENDING','status':'PASS' if technical and signed(gate) else 'BLOCKED','reason':reason})
 scopes={'S1':'Exact statistical method; independent G07 technical review before Phase06','S2':'Population, independence, fixed class counts and acquisition stopping rule for this plan','S3':'Structural metric and prediction-only score definitions before their later locks','S4':'Shift remains empirical; no automatic weighted guarantee','S5':'Model code/weights permissions, technical checks and training authorization','S6':'Source rights and actual reviewer resources; route B','S7':'Proposed utility criteria: at least 50% overall automation and 30% per class; not part of the formal guarantee'}
 for g,reason in scopes.items():
  # Only S2 and S6 are imported here; this notebook cannot approve later-phase locks.
  is_signed=g in {'S2','S6'} and signed(g);gates.append({'gate_id':g,'technical_status':'PENDING_REVIEW' if g in {'S2','S6'} else 'LATER_PHASE','human_status':'SIGNED' if is_signed else 'PENDING','status':'PASS' if is_signed else 'BLOCKED','reason':reason})
 cwrite(run/'decision_gates.csv',gates,['gate_id','technical_status','human_status','status','reason']);ctx['gates']=gates
 for role,rows in ctx['roles'].items():
  for r in rows:r['partition_status']=ctx['partition_status']
  cwrite(run/(role+'.csv'),rows,ROLE_COLS)
 jwrite(run/'calibration_sampling_plan.json',plan);ctx['phase03_audit_ready']=ctx['raw_complete'];ctx['phase03_training_authorized']=False
 jwrite(run/'phase_status.json',{'schema_version':'1.0','phase':'02','status':'PASS' if final else 'BLOCKED','execution_status':'COMPLETED','run_mode':ctx['cfg']['run_mode'],'partition_status':ctx['partition_status'],'phase03_audit_ready':ctx['phase03_audit_ready'],'phase03_training_authorized':False,'training_reason':'Requires downstream S5/model permissions and technical checks in addition to FINAL data splits','scientific_certification_performed':False,'supervisor_approvals_granted_by_code':False,'actual_human_approval_gate_ids':[g for g in ['G02','G03','S2','S6'] if signed(g)],'missing_mandatory_outputs':[],'raw_source_count':len(ctx['inventory']),'observed_files':len(ctx['files']),'decoded_images':len(ctx['samples']),'certification_unit_count':len(ctx['units']),'eligible_certification_units':sum(u['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL' for u in ctx['units']),'pending_quarantine_rows':len(ctx['quarantine']),'calibration_floor_sufficient':plan['floor_sufficient'],'preferred_calibration_target_met':plan['preferred_target_met'],'model_evaluation':'NOT_RUN','finished_utc':utc()})
 return {'partition_status':ctx['partition_status'],'G02':gates[0]['status'],'G03':gates[1]['status'],'plan_sha256':plan['plan_sha256']}


def load_development_manifest(path,raw_root,source_directory_overrides=None):
 """Downstream loader contract. Does not grant model-license or S5 authorization."""
 rows=cread(path);allowed={'train','development_model','development_probability','development_policy','hard_negative_development'}
 for r in rows:
  assert_true(r['partition_status']=='FINAL','PROVISIONAL splits cannot be used for scientific training/evaluation')
  assert_true(r['role'] in allowed,'Held-out/unlabelled manifest is not permitted by the development loader')
  assert_true(r['label'] in {'positive','negative'} and r['eligibility_status']=='ELIGIBLE_PENDING_APPROVAL','Unadjudicated/ineligible example')
  mapped=(source_directory_overrides or {}).get(r['collection'],r['collection']);root=require_under(Path(raw_root)/mapped,raw_root);p=require_under(root/r['image_relative_path'],root);assert_true(sha_file(p)==r['image_sha256'],'Development image bytes changed')
  if r.get('mask_relative_path'):
   mask=require_under(root/r['mask_relative_path'],root);assert_true(sha_file(mask)==r['mask_sha256'],'Development mask bytes changed')
  else:assert_true(r['label']=='negative' and str(r.get('zero_mask_authorized')).lower()=='true','Missing segmentation mask without adjudicated zero-mask authorization')
 return rows

# %% Review queues, complete artifact contracts and immutable export
REQUIRED_OUTPUTS=['dataset_registry.csv','sample_registry.parquet','archive_inventory.csv','exact_duplicates.csv','near_duplicates.csv','parent_lineage.csv','quarantine.csv','leakage_report.md','mrc_reuse_decision.json','legacy_exposure_registry.csv','annotation_manual_v1.md','annotation_audit.csv','reviewer_agreement.csv','hard_negative_spec.md','hard_negative_categories.yaml','population_contract.md','independence_assessment.md','certification_units.csv','calibration_sampling_plan.json','data_card.md']+[r+'.csv' for r in ROLES]+['development.csv','split_hashes.sha256','data_shard_index.json','metric_primitives_test_report.json','cracksafe_core.zip','config.json','environment_snapshot.json','data_access_log.csv','schemas.json','artifact_catalog.json','decision_gates.csv','phase_status.json','stage_errors.json','phase02_manifest.json','phase02_manifest.sha256','SHA256SUMS.sha256','NEXT_PHASE_INPUTS.md']
PRIVATE_TABLES={'sample_registry.parquet','file_inventory.parquet','exact_duplicates.csv','near_duplicates.csv','parent_lineage.csv','legacy_exposure_registry.csv','annotation_audit.csv','reviewer_agreement.csv','quarantine.csv','pairing_audit.csv','raw_fingerprint_mismatches.csv'}

def build_review_outputs(ctx):
 run=ctx['run'];review=run/'review_templates';review.mkdir(exist_ok=True)
 for name,cols in TEMPLATES.items():cwrite(review/name,[],cols)
 jwrite(run/'curator'/'imported_review_records.json',{name:evidence_rows(ctx,name) for name in TEMPLATES})
 queue=[]
 for s in ctx['samples']:
  queue.append({'sample_id':s['sample_id'],'image_sha256':s['image_sha256'],'mask_sha256':s.get('mask_sha256'),'collection':s['collection'],'image_relative_path':s['image_relative_path'],'mask_relative_path':s.get('mask_relative_path'),'original_source_hint_unverified':s['original_source_hint'],'annotation_state':s['annotation_state'],'double_review_required':s['sample_id'] in ctx['double_review_required']|ctx['unit_review_required'],'lineage_status':s['lineage_status'],'review_status':s['review_status'],'assigned_group_role':s['assigned_role']})
 cwrite(run/'curator'/'review_queue.csv',queue,list(queue[0]) if queue else ['sample_id'])
 cwrite(run/'quarantine.csv',ctx['quarantine'],['sample_id','reason','detail'])
 twrite(review/'README.md','''# Supplying actual evidence

Copy these empty templates and the private curator/review_queue.csv to your review workspace. Complete only actual reviews, preserve IDs and SHA-256 values, and keep evidence documents alongside the CSVs. evidence_path is relative to that evidence directory and evidence_sha256 is the SHA-256 of the referenced document. Reviewer identities and times must be real. Do not put completed sensitive review records in a public repository.

Attach reviewed CSVs/documents within the same logical Phase01 controls input (a private controls/evidence dataset is acceptable), set CONFIG["evidence_dir"] to the nested evidence directory, and start a new run. Existing sealed runs are immutable. A first review run emits calibration_sampling_plan.json with plan_sha256; supervisors may then review that concrete proposal. approvals.csv must match that digest. A second run with only those approvals added reproduces the same proposal before recording approval status. New annotation/lineage decisions change the proposal and invalidate earlier approval hashes.

lineage_reviews.csv: use genuine original-source and acquisition IDs; choose site when known, else session, parent, then original image. Numeric filenames alone are insufficient. source_evidence and independence_rationale need substantive text. legacy_exposure is CLEAR, EXPOSED or UNKNOWN. Only actual evidence can justify CLEAR.

annotation_reviews.csv: POSITIVE/NEGATIVE/UNKNOWN, mask_complete YES/NO and expert YES/NO; multiple rows per sample only for distinct reviewers. Record all ambiguity fields. Disagreements require annotation_adjudications.csv with a third distinct expert and written resolution. See annotation_manual_v1.md. Do not fill negative labels automatically.

duplicate_reviews.csv: SAME_ACQUISITION, DISTINCT_ACQUISITION or UNRESOLVED. Bind both image hashes; a pHash or thumbnail NCC alone is not identity proof.

source_rights.csv: one row per ORIGINAL source, with explicit research_use and redistribution states PERMITTED/PROHIBITED/UNKNOWN. Record upstream URL, license_text_path within this evidence directory, matching license_text_sha256, conditions and reviewer resources. The private aggregate folder does not transfer or establish upstream rights.

approvals.csv: gate_id G02/G03/S2/S6, decision APPROVE, plan_sha256 and human reasoning/evidence. S1/S3/S4/S5/S7 remain for their appropriate phases. This notebook never generates signatures.
''')
 twrite(run/'leakage_report.md',f'''# Leakage and curation report

Run `{ctx['run_id']}`, mode {ctx['cfg']['run_mode']}; partition status {ctx['partition_status']}.

- Examined images: {len(ctx['samples'])}; logical raw sources: 5.
- Exact duplicate star edges: {len(ctx['exact'])}; indexed near candidates: {len(ctx['near'])}.
- Conservative acquisition groups: {len(ctx['units'])}; quarantine records: {len(ctx['quarantine'])}.
- Perceptual-index truncated samples: {len(ctx['near_truncated'])} (blocks unreviewed completeness).
- Every independent role manifest is disjoint by sample, split group and certification unit. Compatibility development and linked hard-negative development are the two documented aliases.

Byte and canonical decoded-pixel hashes establish exact content equivalence; masks are compared within image-equivalence groups to flag conflicts. Masks alone never establish image duplication. Near matches are only candidates, unioned conservatively until adjudicated. Five crop windows plus rotations/flips cannot detect every possible crop. Unknown acquisition/source provenance never creates an IID singleton. The aggregate collection is not an independent source. Original-source holdout follows transitive groups; unknown provenance cannot justify a zero-shot claim.

Remaining statistical and scientific limitations are in independence_assessment.md, population_contract.md, decision_gates.csv and the private curator review queue. A clean structural split validator result does not imply rights, labels, IID, scientific approval or adequate calibration capacity. No historical pair count was used as a current dataset count.
''')
 counts=Counter(s['label'] for s in ctx['samples'])
 twrite(run/'data_card.md',f'''# CrackSAFE-CP Phase02 data card

Blueprint v3.3, run {ctx['run_id']}. Existing private source: abarman79/wall-crack-cp-datasets. Five extracted source collections; zero raw ZIPs required. Full source bytes are never copied into outputs. Phase01 logical raw_archive_count=5 is not a ZIP count.

Observed filesystem members: {len(ctx['files'])}. Examined image records: {len(ctx['samples'])}. Adjudicated class counts at image level: {dict(counts)}. Proposed certification units: {len(ctx['units'])}. Actual independent-unit availability and shortfalls are in calibration_sampling_plan.json; image/crop counts are not independent observations.

Uses: curator data quality, provenance, leakage and provisional scientific planning. Prohibited automatic conclusions: legal clearance, correct labels from folder names, IID from unique hashes, calibration certification, zero-shot generalization, reproduced legacy metrics or model performance. Rights are per original source. Redistribution remains separately reviewed even if private research use is permitted.

Preprocessing primitives: native pixel orientation is retained; nontrivial EXIF requires review. RGB image conversion, binary masks, 448 aspect-preserving letterbox, nearest-neighbor mask resize and explicit valid-padding mask. No small-ground-truth-component pruning. Mask formats with unknown color/ignore semantics remain quarantined.

SMOKE audits a deterministic bounded image subset and never certifies full integrity or final splits. FULL hashes every source member and audits every detected image/mask candidate. Unknown/partial/missing labels and unmapped pairing cases are retained as explicit review/exclusion records. No data collection or representativeness claim is inferred from file naming.
''')
 write_samples(ctx)
 # Public unit roster omits labels/categories; the complete curator roster is private.
 write_parquet(run/'curator'/'certification_units_private.parquet',ctx['units'])
 public_units=[{k:v for k,v in u.items() if k not in {'representative_label','hard_negative_category'}} for u in ctx['units']]
 cwrite(run/'certification_units.csv',public_units,list(public_units[0]) if public_units else ['certification_unit_id','split_group_id','representative_sample_id'])
 jwrite(run/'data_shard_index.json',{'schema_version':'1.0','strategy':'REFERENCE_RAW_EXTRACTED_INPUT; no raw payload copies','dataset_reference':'abarman79/wall-crack-cp-datasets','sources':[{'collection':r['collection'],'tree_sha256':r['expected_tree_sha256'],'relative_root':ctx['source_paths'][r['collection']].relative_to(ctx['raw_root']).as_posix(),'original_phase01_archive_id':r['archive_id']} for r in ctx['inventory']],'sample_locator':'collection + image_relative_path in approved role manifests','private_full_index':'file_inventory.parquet; curator only','split_status':ctx['partition_status'],'renamed_source_mapping':'dataset_discovery.json; downstream must explicitly map same-content logical collection names','no_external_shards_created':True})


def artifact_entry(ctx,p,bundled):
 return {'artifact_id':stable('artifact',p.relative_to(ctx['run']).as_posix()),'relative_path':p.relative_to(ctx['run']).as_posix(),'sha256':sha_file(p),'byte_size':p.stat().st_size,'media_type':mimetypes.guess_type(p.name)[0] or 'application/octet-stream','schema_version':'1.0','producing_run_id':ctx['run_id'],'required_by':['03'],'privacy/license_status':'PRIVATE_CURATOR_ONLY' if not bundled else 'PRIVATE_CONTROL; redistribution requires source/privacy review','bundled':bundled}

def zip_files(target,root,paths):
 tmp=Path(str(target)+'.tmp')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(paths):
   info=zipfile.ZipInfo(p.relative_to(root).as_posix(),(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   with p.open('rb') as src,z.open(info,'w') as dest:shutil.copyfileobj(src,dest,8*1024**2)
 tmp.replace(target)


def export_phase02(ctx):
 run=ctx['run'];build_review_outputs(ctx)
 # Retain exactly the verified Phase01 statistical module, and add reusable Phase02 audit/loader/primitives.
 with zipfile.ZipFile(run/'cracksafe_core.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('cracksafe_core/__init__.py','from .phase01 import cp_upper, minimum_n, risk_cell, select_policy\nfrom .phase02 import letterbox, skeleton, connected_components, cldice, valid_prediction_components, load_development_manifest\n')
  z.writestr('cracksafe_core/phase01.py',(ctx['upstream']/'phase01_core.py').read_bytes());z.writestr('cracksafe_core/phase02.py',(run/'phase02_core.py').read_bytes());z.writestr('cracksafe_core/VERSION','Phase02 '+VERSION+'; upstream Phase01 SHA256 '+sha_file(ctx['upstream']/'phase01_core.py'))
 for name in ['model_roster.json','statistical_design.json','statistical_self_tests.json','phase02_contract.json','prediction_only_topology_design.md','blueprint_v3.3.md']:
  if (ctx['upstream']/name).is_file():atomic(run/'upstream_controls'/name,(ctx['upstream']/name).read_bytes())
 cwrite(run/'data_access_log.csv',ctx['access'],['utc','path','operation','access_role','model_predictions_used']);jwrite(run/'stage_errors.json',ctx['errors'])
 twrite(run/'split_hashes.sha256',''.join(sha_file(run/(r+'.csv'))+'  '+r+'.csv\n' for r in sorted(ctx['roles'])))
 bundle_name=f"CrackSAFE_CP_v3.3_phase02_control_{ctx['run_id']}.zip"
 twrite(run/'NEXT_PHASE_INPUTS.md',f'''# Exact Phase03 handoff

Phase02 run: `{ctx['run_id']}`. Data partition status: **{ctx['partition_status']}**. This handoff does not grant model training permission or scientific certification.

| Logical dependency | Exact artifact | How Phase03 must consume it |
|---|---|---|
| Phase01 controls | `{P01_ZIP}` + matching `.zip.sha256` | Pin successful run {P01_RUN}; outer SHA-256 `{P01_SHA}`; verify internals before loading code |
| Phase02 controls | `{bundle_name}` + matching `.zip.sha256` | Save Notebook02 output version or upload only this small private pair; read actual outer hash from its sidecar |
| Raw payload | Existing `abarman79/wall-crack-cp-datasets` extracted input | Reuse original mounted folders; resolve with data_shard_index.json and verify logical tree/file hashes; do not upload raw images to GitHub |
| Non-test training/development | train.csv, development_model.csv, development_probability.csv, development_policy.csv, linked hard_negative_development.csv | Require FINAL status, structural disjointness, approved labels/rights and downstream S5/model/code/weights permission + technical gates |
| Common methodology | verified Phase01 statistical_design.json, model_roster.json, blueprint and Phase02 cracksafe_core.zip | Preserve exact statistical implementation, 3-seed protocol and current model roster; no architecture/metric redesign |

`development.csv` is only the union of the three development subsets. `hard_negative_development.csv` is a linked subset of development_policy, not additional independent data. `source_unlabeled_pool.csv` and `target_unlabeled_pool.csv` are reserved and require their explicit approved protocol; never merge them with calibration/tests.

Calibration, internal/external/hard-negative/corruption tests and reserve groups remain held out. Their manifest labels/mask paths are removed. Other views of each held-out group remain reserved. `curator/sealed_labels.parquet`, full sample registry, detailed duplicate/annotation/lineage tables and the optional audit ZIP are curator-only, excluded from the Phase03 control ZIP. Do not add the curator archive to a training notebook. This is a procedural boundary: raw dataset owners can still inspect raw annotations.

Before training: resolve G02/G03/S2/S6 for FINAL data and separately complete S5/model-specific gates. A BLOCKED Phase02 report can accompany successful Python execution; inspect phase_status.json for execution_status, mode, count shortfalls and pending evidence. No later notebook has been generated here.

For GitHub: notebook, sanitized guide, source module and lightweight non-sensitive validation summaries only. Keep raw payloads, review identities/evidence, full registries, held-out labels, audit ZIPs and private controls out of the public repository. No GitHub write is performed by this notebook.
''')
 private=lambda p:p.name in PRIVATE_TABLES or 'curator' in p.relative_to(run).parts
 exclude_dirs={'verified_phase01'}
 excluded_names={'audit_cache.sqlite','audit_cache.sqlite-wal','audit_cache.sqlite-shm','artifact_catalog.json','phase02_manifest.json','phase02_manifest.sha256','SHA256SUMS.sha256','SEALED.json','bundle_verification.json'}
 files=[p for p in run.rglob('*') if p.is_file() and not any(part in exclude_dirs or part=='__pycache__' for part in p.relative_to(run).parts) and p.name not in excluded_names and not p.name.endswith(('.tmp','.zip.sha256')) and not p.name.startswith('CrackSAFE_CP_v3.3_phase02_')]
 # Tables are self-described with columns, real dtypes and null rules; Parquet remains true Parquet.
 import pandas as pd
 tables={}
 for p in files:
  if p.suffix=='.csv':
   with p.open(newline='',encoding='utf-8') as f:reader=csv.reader(f);header=next(reader);count=sum(1 for _ in reader)
   tables[p.relative_to(run).as_posix()]={'columns':header,'row_count':count,'csv_types':'strings; use declared state fields and explicit integer/boolean conversion; empty = null'}
  elif p.suffix=='.parquet':
   import pyarrow.parquet as pq
   meta=pq.read_metadata(p);tables[p.relative_to(run).as_posix()]={'row_count':meta.num_rows,'arrow_schema':str(pq.read_schema(p))}
 jwrite(run/'schemas.json',{'schema_version':'1.0','tables':tables,'primary_keys':{'sample_registry.parquet':['sample_id'],'certification_units.csv':['certification_unit_id'],'dataset_registry.csv':['original_source_id'],'archive_inventory.csv':['archive_id']},'null_policy':'JSON null; CSV empty; no unknown-to-zero conversion','partition_status_enum':['PROVISIONAL','FINAL'],'label_enum':['positive','negative','UNKNOWN'],'unit_status_enum':['ELIGIBLE_PENDING_APPROVAL','INELIGIBLE'],'required_outputs':REQUIRED_OUTPUTS})
 if run/'schemas.json' not in files:files.append(run/'schemas.json')
 entries=[artifact_entry(ctx,p,not private(p)) for p in sorted(files)]
 jwrite(run/'artifact_catalog.json',{'schema_version':'1.0','run_id':ctx['run_id'],'artifacts':entries,'excluded_self_references':['catalog','manifest and checksum files','outer bundles and sidecars','seal/verification','SQLite cache','verified_phase01 extraction'],'model_input_boundary':'Only FINAL approved development manifests; private tables are curator-only'})
 entries.append(artifact_entry(ctx,run/'artifact_catalog.json',True));control=[run/e['relative_path'] for e in entries if e['bundled']]
 manifest={'schema_version':'1.0','blueprint_version':'3.3','blueprint_sha256':BLUEPRINT_SHA,'phase':'02','run_id':ctx['run_id'],'created_utc':ctx['identity']['created_utc'],'status':'PASS' if ctx['partition_status']=='FINAL' else 'BLOCKED','partition_status':ctx['partition_status'],'scope':'Dataset audit and split planning only; no model execution or certification','config_sha256':ctx['identity']['config_sha256'],'code_sha256':ctx['identity']['code_sha256'],'code_hash_method':'SHA256(UTF8(core_source + newline + workflow_source)); source files included','input_artifacts':[{'artifact_id':'phase01_control','path':P01_ZIP,'sha256':ctx['p01_sha']},*ctx['inventory']],'output_artifacts':entries,'gate_results':ctx['gates'],'amendment_ids':[],'environment_file':'environment_snapshot.json','access_log_file':'data_access_log.csv','phase03_training_authorized':False,'private_payload_policy':'Unbundled artifact hashes are provenance only; do not require private curator labels for Phase03 development'}
 jwrite(run/'phase02_manifest.json',manifest);twrite(run/'phase02_manifest.sha256',sha_file(run/'phase02_manifest.json')+'  phase02_manifest.json\n')
 control += [run/'phase02_manifest.json',run/'phase02_manifest.sha256']
 twrite(run/'SHA256SUMS.sha256',''.join(sha_file(p)+'  '+p.relative_to(run).as_posix()+'\n' for p in sorted(control)))
 absent=[n for n in REQUIRED_OUTPUTS if not(run/n).is_file()];assert_true(not absent,'Missing mandatory outputs: '+str(absent))
 bundle=run/bundle_name;zip_files(bundle,run,control+[run/'SHA256SUMS.sha256']);outer=sha_file(bundle);twrite(Path(str(bundle)+'.sha256'),outer+'  '+bundle.name+'\n')
 verify_zip(bundle,Path(str(bundle)+'.sha256'),outer,'02')
 if ctx['cfg']['export_audit_zip']:
  audit=run/f"CrackSAFE_CP_v3.3_phase02_PRIVATE_audit_{ctx['run_id']}.zip";private_files=[run/e['relative_path'] for e in entries if not e['bundled']]
  zip_files(audit,run,private_files);twrite(Path(str(audit)+'.sha256'),sha_file(audit)+'  '+audit.name+'\n')
 jwrite(run/'bundle_verification.json',{'status':'PASS','outer_sha256':outer,'bundled_artifacts':len(control),'private_artifacts_excluded':sum(not e['bundled'] for e in entries),'verified_utc':utc()})
 jwrite(run/'SEALED.json',{'run_id':ctx['run_id'],'sealed_utc':utc(),'outer_sha256':outer,'rule':'Immutable: new evidence/config creates a new run. Resume only an unsealed interruption.'})
 ctx['cache'].commit();ctx['bundle']=bundle
 print('\nPHASE02 EXPORT COMPLETE\n',bundle,'\nSHA256',outer,'\nPartition:',ctx['partition_status'],'\nCalibration:',json.dumps(ctx['plan']['actual_capacity'],indent=2))
 print('Python execution succeeded. BLOCKED scientific gates and PROVISIONAL partitions require evidence, not bypasses. Download the control ZIP + .sha256; keep private curator outputs separate.')
 return {'control_bundle':str(bundle),'sha256':outer,'partition_status':ctx['partition_status']}
