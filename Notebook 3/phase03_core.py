"""CrackSAFE-CP Phase03 1.0.0. Offline development only; no test or risk calibration API."""
from pathlib import Path, PurePosixPath
import ast, contextlib, csv, datetime as dt, hashlib, importlib, importlib.metadata as md
import io, json, math, mimetypes, os, platform, random, re, shutil, stat, sys, time, traceback, types, zipfile
VERSION='1.0.0'
BLUEPRINT_SHA='2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e'
GIT_COMMIT='dc52faf2929c9358ce36937c4a5131976c4fe8de'
P01_RUN='20261015T111557980168Z_d3a9b41a'
P02_RUN='20261018T050513552430Z_afc0e8ab'
P01_SHA='ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca'
P02_SHA='9d87e629fa12d142bbb473384a7b932536edf59e33fd65c7e797c730349a7c99'
SEEDS=[42,123,2026]
ROLES=['train','development_model','development_probability','development_policy','hard_negative_development']
SEALED_ROLES={'calibration','internal_test','external_positive_test','hard_negative_test','reserve_pool','corruption_test','field_test','source_unlabeled_pool','target_unlabeled_pool'}
COLLECTIONS=['CRACK500 CrackTree200 GAPS384','CrackForest dataset(CFD)','DeepCrack','SDNET2018','crack segmentation dataset']
ENGINES=['unetpp_effb3','scsegamba','dmsrcrack','segformer_b0','unetpp_convnext_tiny']
PREPROCESS={'size':448,'image_interpolation':'PIL_BILINEAR','mask_interpolation':'NEAREST','padding':0,'normalization_mean':[.485,.456,.406],'normalization_std':[.229,.224,.225],'valid_padding_excluded':True}
FILTER={'probability':.55,'area':20,'skeleton_pixels':5,'connectivity':8,'mean_probability':.55,'mean_condition_redundant':True}
DEFAULT_CONFIG={
 'RUN_MODE':'SMOKE','JOB':'audit','ENGINE_ID':'unetpp_effb3','SEED':42,
 'resume_run_dir':None,'input_root':'/kaggle/input','inputs_override':{},
 'output_root':'/kaggle/working/cracksafe_cp/phase03','export_root':'/kaggle/working',
 'SESSION_BUDGET_HOURS':9.0,'budget_buffer_minutes':20,'device':'cuda','image_size':448,
 'micro_batch':2,'effective_batch':16,'max_epochs':100,'warmup_epochs':5,'patience':15,
 'weight_decay':.01,'amp':True,'learning_rate':.0001,'recipe_id':'clean_common_loss',
 'reviewed_training_plan':None,'reviewed_future_phase02':None,'job_inputs':[],
 'source_directory_overrides':{},'max_saved_output_bytes':20*1024**3,
 'max_prediction_cache_bytes':8*1024**3,'storage_reserve_bytes':512*1024**2,
 'figure_examples':True,'cpu_threads':2,'internet_allowed':False}

class Blocked(RuntimeError): pass
class BudgetStop(RuntimeError): pass

def require(ok,msg):
 if not ok: raise Blocked(msg)
assert_true=require

def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def jb(x): return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False,ensure_ascii=False)+'\n').encode()
def digest(b): return hashlib.sha256(b).hexdigest()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def stream_sha(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def atomic(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.tmp')
 with t.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 t.replace(p)
def jwrite(p,x): atomic(p,jb(x))
def twrite(p,x): atomic(p,x.encode())
def jread(p): return json.loads(Path(p).read_text())
def cwrite(p,rows,columns):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows);twrite(p,s.getvalue())
def cread(p):
 with Path(p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def under(p,root):
 p=Path(p).resolve();require(p.is_relative_to(Path(root).resolve()),'Path escapes trusted root');return p

def environment():
 pkgs={}
 for n in ['numpy','pandas','Pillow','scipy','scikit-image','matplotlib','pyarrow','torch','torchvision','segmentation-models-pytorch','timm','transformers','mamba-ssm','mmcv-full','mmengine']:
  try:pkgs[n]=md.version(n)
  except md.PackageNotFoundError:pkgs[n]=None
 e={'python':sys.version,'platform':platform.platform(),'packages':pkgs,'cuda':None,'driver_version':None,'cudnn_version':None,'gpu':None,'cpu_count':os.cpu_count(),'ram_bytes':None}
 try:
  import psutil;e['ram_bytes']=psutil.virtual_memory().total
 except ImportError:pass
 try:
  import torch;e.update(cuda=torch.version.cuda,cudnn_version=torch.backends.cudnn.version(),gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
  if torch.cuda.is_available():
   try:
    import subprocess
    r=subprocess.run(['nvidia-smi','--query-gpu=driver_version','--format=csv,noheader'],capture_output=True,text=True,timeout=5)
    if r.returncode==0:e['driver_version']=r.stdout.strip() or None
   except (OSError,subprocess.SubprocessError):pass
 except ImportError:pass
 return e

def config_identity(c):return digest(jb({k:v for k,v in c.items() if k not in {'resume_run_dir','SESSION_BUDGET_HOURS','budget_buffer_minutes'}}))
def initialize(config,core_source):
 c=json.loads(json.dumps(config));require(c['RUN_MODE'] in {'SMOKE','FULL'},'Invalid RUN_MODE')
 require(c['JOB'] in {'audit','train','ensemble','select'},'Invalid JOB');require(c['ENGINE_ID'] in ENGINES,'Unknown engine')
 require(c['SEED'] in SEEDS+[3407,8675309] and c['image_size']==448,'Seed/grid contract changed')
 require(c['recipe_id']=='clean_common_loss','RECIPE_UNRECOVERED: no exact MRC coefficients available')
 require(c['effective_batch']==16 and c['micro_batch'] in [2,4,8],'Effective batch16; microbatch2/4/8')
 require(c['max_epochs']==100 and c['warmup_epochs']==5 and c['patience']==15,'Protocol amendment required')
 require(c['learning_rate'] in [1e-4,3e-4] and c['weight_decay']==.01,'Protocol amendment required')
 require(not c['internet_allowed'],'Runtime is offline; stage pinned dependencies explicitly')
 ident={'config_sha256':config_identity(c),'code_sha256':digest(core_source.encode()),'blueprint_sha256':BLUEPRINT_SHA}
 if c['resume_run_dir']:
  run=Path(c['resume_run_dir']);require(not(run/'SEALED.json').exists(),'Sealed run is immutable; begin a new job')
  old=jread(run/'run_identity.json');require(all(old[k]==v for k,v in ident.items()),'Resume config/code/blueprint mismatch');ident=old
 else:
  rid=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+ident['config_sha256'][:8]
  run=Path(c['output_root'])/('run_'+rid);run.mkdir(parents=True,exist_ok=False);ident.update(run_id=rid,created_utc=utc())
 ctx={'cfg':c,'run':run,'run_id':ident['run_id'],'identity':ident,'env':environment(),'started':time.monotonic(),'errors':[],'access':[],'gates':[],'controls':{},'training_authorized':False,'scientific_status':'BLOCKED','execution_status':'COMPLETED','rows':{},'models':{},'registry':[],'summaries':[],'pred_index':[],'calibrations':{},'technical':{},'figure_rows':[]}
 for d in ['configs','checkpoints','per_seed_metrics','training_history','figures','synthetic_test_figures','status','stages','model_checks','predictions']: (run/d).mkdir(exist_ok=True)
 if c['resume_run_dir'] and (run/'data_access_log.csv').exists():
  ctx['access']=cread(run/'data_access_log.csv');ctx['access_keys']={(r['path'],r['role'],r['operation']):i for i,r in enumerate(ctx['access'])}
 jwrite(run/'run_identity.json',ident);jwrite(run/'config.json',c);jwrite(run/'environment_snapshot.json',ctx['env']);twrite(run/'phase03_core.py',core_source)
 initialize_outputs(ctx);return ctx

def stage(ctx,name,fn):
 t=time.monotonic();r={'stage':name,'started_utc':utc()}
 try:r['result']=fn(ctx);r['status']='COMPLETED'
 except (Blocked,BudgetStop) as e:r.update(status='BLOCKED' if isinstance(e,Blocked) else 'BUDGET_STOP',reason=str(e));ctx['gates'].append({'gate_id':name,'status':r['status'],'reason':str(e)})
 except Exception as e:
  r.update(status='FAILED',reason=str(e),traceback=traceback.format_exc());ctx['errors'].append(r.copy());ctx['execution_status']='COMPLETED_WITH_ERRORS';ctx['training_authorized']=False
 r['seconds']=time.monotonic()-t;jwrite(ctx['run']/'stages'/(name+'.json'),r);print(name,r['status'],r.get('reason',''));return r

def access(ctx,path,role,operation):
 require(role not in SEALED_ROLES and 'curator' not in Path(path).parts,'Sealed role access denied')
 key=(str(path),role,operation);seen=ctx.setdefault('access_keys',{})
 if key in seen:
  row=ctx['access'][seen[key]];row['read_count']=int(row.get('read_count',1))+1;row['last_utc']=utc()
 else:
  seen[key]=len(ctx['access']);ctx['access'].append({'utc':utc(),'last_utc':utc(),'read_count':1,'path':str(path),'role':role,'operation':operation})

def safe_zip(z,max_bytes=4*1024**3):
 ns=[];total=0
 for i in z.infolist():
  n=i.orig_filename;p=PurePosixPath(n)
  require(n and '\x00' not in n and '\\' not in n and not p.is_absolute() and '..' not in p.parts and not re.match(r'^[A-Za-z]:',n),'Unsafe ZIP path')
  require(not stat.S_ISLNK(i.external_attr>>16) and not i.flag_bits&1,'Symlink/encrypted ZIP')
  require(i.file_size/max(1,i.compress_size)<2000,'ZIP expansion ratio');total+=i.file_size;ns.append(n)
 require(total<=max_bytes and len(ns)==len(set(ns)),'ZIP size/duplicate members')
 require(z.testzip() is None,'ZIP CRC failure');return ns

def verify_control(path,sidecar,phase,run_id,expected_sha,canonical=None):
 path=Path(path);canonical=canonical or f'CrackSAFE_CP_v3.3_phase{phase}_control_{run_id}.zip'
 require(path.name in {canonical,canonical+'.bin'},'Unexpected archive/run filename')
 require(path.is_file() and Path(sidecar).is_file(),'Archive and canonical .zip.sha256 sidecar both required')
 parts=Path(sidecar).read_text().strip().split('  ',1)
 require(parts==[expected_sha,canonical],'Sidecar name/hash mismatches pinned run')
 require(sha(path)==expected_sha,'Outer ZIP SHA256 mismatch')
 with zipfile.ZipFile(path) as z:
  ns=safe_zip(z);mn=f'phase{phase}_manifest.json';m=json.loads(z.read(mn))
  require(all(m.get(k)==v for k,v in {'schema_version':'1.0','blueprint_version':'3.3','blueprint_sha256':BLUEPRINT_SHA,'phase':phase,'run_id':run_id}.items()),'Control schema/identity mismatch')
  require(z.read(f'phase{phase}_manifest.sha256').decode().strip().split('  ',1)==[digest(z.read(mn)),mn],'Manifest sidecar mismatch')
  entries=m['output_artifacts'];paths=[e['relative_path'] for e in entries];require(len(paths)==len(set(paths)),'Duplicate catalog paths')
  for e in entries:
   if e.get('bundled',True):
    require(e['relative_path'] in ns,'Bundled payload absent')
    with z.open(e['relative_path']) as f:require(stream_sha(f)==e['sha256'],'Payload hash mismatch: '+e['relative_path'])
    require(z.getinfo(e['relative_path']).file_size==e['byte_size'],'Payload size mismatch')
  covered=set(paths)|{mn,f'phase{phase}_manifest.sha256','SHA256SUMS.sha256'}
  for l in z.read('SHA256SUMS.sha256').decode().splitlines():
   if l and not l.startswith('#'):
    h,n=l.split('  ',1)
    with z.open(n) as f:require(stream_sha(f)==h,'Internal checksum mismatch')
    covered.add(n)
  require(all(n.endswith('/') or n in covered for n in ns),'Unregistered ZIP payload')
  core=f'phase{phase}_core.py';require(digest(z.read(core)+b'\n'+z.read('workflow_source.json'))==m['code_sha256'],'Upstream combined source identity mismatch')
  bp='blueprint_v3.3.md' if phase=='01' else 'upstream_controls/blueprint_v3.3.md'
  require(digest(z.read(bp))==BLUEPRINT_SHA,'Actual blueprint bytes mismatch')
 return m

def find_pair(root,phase,run_id,override=None):
 canonical=f'CrackSAFE_CP_v3.3_phase{phase}_control_{run_id}.zip';root=Path(root)
 if override:
  p=Path(override);require(p.name in {canonical,canonical+'.bin'},'Override names wrong run');candidates=[p] if p.is_file() else []
 else:
  all_arch=[p for p in root.rglob(f'CrackSAFE_CP_v3.3_phase{phase}_control_*.zip*') if p.is_file() and p.name.endswith(('.zip','.zip.bin'))] if root.exists() else []
  require(not any(p.name not in {canonical,canonical+'.bin'} for p in all_arch),'Stale control archives attached; remove them or explicitly select the pinned path')
  candidates=all_arch
 require(len(candidates)<=1,'Duplicate/ambiguous control archive mounts')
 if not candidates:return None
 p=candidates[0];sc=p.with_name(canonical+'.sha256');require(sc.is_file(),'Canonical sidecar absent; sidecar alone never supplies archive bytes')
 return p,sc,canonical

def reviewed_document(spec,kind):
 require(spec and set(spec)>={'path','sha256'},kind+' requires a separately reviewed, hash-pinned document')
 p=Path(spec['path']);require(p.is_file() and sha(p)==spec['sha256'],kind+' document missing/changed');d=jread(p)
 require(d.get('decision')=='APPROVE' and d.get('reviewer') and d.get('signed_at') and d.get('rationale'),kind+' requires actual dated human review')
 ev=d.get('evidence',{});ep=under(p.parent/ev.get('relative_path',''),p.parent)
 require(ep.is_file() and sha(ep)==ev.get('sha256'),kind+' review evidence missing/changed')
 return d

def discover_controls(ctx):
 c=ctx['cfg'];root=c['input_root'];ov=c['inputs_override'];run_id=P02_RUN;expected=P02_SHA
 if c['reviewed_future_phase02']:
  amendment=reviewed_document(c['reviewed_future_phase02'],'Future FINAL Phase02 acceptance')
  require(amendment.get('blueprint_sha256')==BLUEPRINT_SHA and amendment.get('replaces_sha256')==P02_SHA,'Future review must bind original identity and blueprint')
  run_id=amendment['run_id'];expected=amendment['phase02_sha256'];require(re.fullmatch('[a-f0-9]{64}',expected),'Invalid reviewed digest')
 pair=find_pair(root,'02',run_id,ov.get('phase02_bundle'))
 if not pair:
  lone=find_pair(root,'01',P01_RUN,ov.get('phase01_bundle'))
  if lone:
   lp,ls,ln=lone;verify_control(lp,ls,'01',P01_RUN,P01_SHA,ln)
   ctx['controls']['phase01']={'run_id':P01_RUN,'sha256':P01_SHA,'provenance':'SEPARATE_VERIFIED_INPUT'}
   jwrite(ctx['run']/'input_verification.json',{'status':'PARTIAL_PHASE01_VERIFIED_PHASE02_MISSING','controls':ctx['controls']})
  raise Blocked('MISSING Phase02 immutable ZIP/.zip.bin and canonical sidecar; public GitHub reports are not controls')
 p,sc,canonical=pair;m2=verify_control(p,sc,'02',run_id,expected,canonical)
 temp=ctx['run']/'.verified_inputs';temp.mkdir(exist_ok=True);p2=temp/canonical;shutil.copyfile(p,p2)
 pair1=find_pair(root,'01',P01_RUN,ov.get('phase01_bundle'))
 if pair1:p1,s1,cn1=pair1;provenance='SEPARATE_VERIFIED_INPUT'
 else:
  cn1=f'CrackSAFE_CP_v3.3_phase01_control_{P01_RUN}.zip';member='recovered_phase01_input/'+cn1
  with zipfile.ZipFile(p2) as z:
   require(member in z.namelist(),'Missing separate Phase01 archive and embedded original archive')
   p1=temp/cn1
   with z.open(member) as src,p1.open('wb') as dst:shutil.copyfileobj(src,dst,8*1024**2)
  require(sha(p1)==P01_SHA,'Embedded Phase01 raw bytes mismatch')
  s1=temp/(cn1+'.sha256');twrite(s1,P01_SHA+'  '+cn1+'\n');provenance='EMBEDDED_RAW_BYTES_IN_PHASE02; canonical digest independently checked'
 m1=verify_control(p1,s1,'01',P01_RUN,P01_SHA,cn1)
 with zipfile.ZipFile(p2) as z:
  s=json.loads(z.read('phase_status.json'));plan=json.loads(z.read('calibration_sampling_plan.json'))
  # Parse only non-label metadata. Role payloads above were streamed for integrity, never parsed.
  code=z.read('phase02_core.py').decode();shared=z.read('cracksafe_core.zip')
  with zipfile.ZipFile(io.BytesIO(shared)) as sharedzip:
   safe_zip(sharedzip);require(sharedzip.read('cracksafe_core/phase02.py')==code.encode(),'Shared Phase02 code diverges')
   with zipfile.ZipFile(p1) as first:require(sharedzip.read('cracksafe_core/phase01.py')==first.read('phase01_core.py'),'Shared Phase01 code diverges')
  jwrite(ctx['run']/'upstream_status.json',s);atomic(ctx['run']/'cracksafe_core_upstream.zip',shared)
  module=types.ModuleType('_verified_phase02_'+expected[:12]);sys.modules[module.__name__]=module;exec(compile(code,'<verified phase02>','exec'),module.__dict__)
 ctx.update(p02module=module,p02zip=p2,p02manifest=m2,p02status=s,role_plan=plan)
 ctx['controls']={'phase01':{'run_id':P01_RUN,'sha256':P01_SHA,'provenance':provenance},'phase02':{'run_id':run_id,'sha256':expected,'provenance':str(p),'status':s.get('status'),'partition_status':s.get('partition_status')}}
 jwrite(ctx['run']/'input_verification.json',{'status':'PASS','controls':ctx['controls'],'sealed_payload_access':'INTEGRITY_STREAM_ONLY; no role labels parsed'})
 return ctx['controls']

# Canonical Phase02 primitive definitions are inserted verbatim below for standalone SYNTHETIC tests.
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
CANONICAL_PRIMITIVES_SHA='268a82ccd7a656ae18341c63b3ae336b23a3e9b2da6481dca939eb9f4b68f631'

def validate_plan(ctx):
 c=ctx['cfg'];require(ctx.get('p02status'),'Controls missing; integrity not established')
 s=ctx['p02status'];require(s.get('partition_status')=='FINAL' and s.get('execution_status')=='COMPLETED','Phase02 remains PROVISIONAL/BLOCKED: no real-data training or ranking')
 gates={g['gate_id']:g for g in ctx['p02manifest']['gate_results']}
 require(all(gates.get(g,{}).get('status')=='PASS' and gates[g].get('human_status')=='SIGNED' for g in ['G02','G03','S2','S6']),'Actual Phase02 G02/G03/S2/S6 approvals required')
 plan=reviewed_document(c['reviewed_training_plan'],'S5 training plan')
 require(plan.get('gate_id')=='S5' and plan.get('phase02_sha256')==ctx['controls']['phase02']['sha256'] and plan.get('phase03_code_sha256')==ctx['identity']['code_sha256'],'S5 plan must bind exact inputs and Phase03 code')
 require(plan.get('seeds')==SEEDS and plan.get('preprocess')==PREPROCESS and plan.get('filter')==FILTER,'Frozen ensemble/preprocessing/filter differs')
 require(plan.get('approved_data_scope')=='ALL_FINAL_TRAIN_DEVELOPMENT','S5 must explicitly approve the complete FINAL development/training data scope')
 require(plan.get('recipe_id')=='clean_common_loss' and plan.get('before_comparative_training') is True,'Plan must precede comparative training')
 slots=plan.get('slots',[]);require([r['slot'] for r in slots]==['A','B','C'] and slots[0]['engine_id']=='unetpp_effb3','Three predeclared slots with mandatory legacy engine required')
 require(len({r['engine_id'] for r in slots})==3 and all(r['engine_id'] in ENGINES for r in slots),'Duplicate/unknown architectures')
 used=[]
 for row,primary in zip(slots,['unetpp_effb3','scsegamba','dmsrcrack']):
  engine=row['engine_id']
  if engine!=primary:
   require(row.get('replacement_reason') in {'TECHNICAL_FAILURE','PERMISSION_FAILURE'},'No accuracy-triggered substitution')
   fallback=next((x for x in ['segformer_b0','unetpp_convnext_tiny'] if x not in used),None)
   require(engine==fallback,'Fallback order must be SegFormer then verified ConvNeXt')
   failure=reviewed_document(row.get('failure_review'),primary+' failure review');require(failure.get('engine_id')==primary and failure.get('accuracy_used') is False,'Replacement needs actual pre-accuracy failure evidence')
  used.append(engine)
  spec=plan['engines'][engine]
  require(spec.get('code_permission')=='APPROVED' and spec.get('source_rights')=='APPROVED','Model/source permission unknown')
  require(spec.get('initialization') in {'RANDOM','GENERIC_PRETRAINED'},'Crack-trained or undisclosed initialization forbidden')
  if spec['initialization']=='GENERIC_PRETRAINED':require(spec.get('weights_permission')=='APPROVED' and spec.get('exposure_status')=='GENERIC_NO_CRACK_TRAINING' and spec.get('weights_sha256'),'Pretrained weight rights/exposure missing')
  lr=spec.get('learning_rate');require(lr in [1e-4,3e-4],'Undeclared learning rate')
  trials=spec.get('learning_rate_trials',[]);require(1<=len(trials)<=2 and set(trials)<={1e-4,3e-4} and lr in trials,'Maximum two predeclared development-model LR choices')
  if len(trials)==2:
   trial=reviewed_document(spec.get('lr_selection_review'),'LR selection');require(trial.get('role')=='development_model' and trial.get('chosen_learning_rate')==lr,'LR trial decision requires development-only evidence')
 require(c['SEED'] in SEEDS or c['SEED'] in plan.get('optional_individual_seeds',[]),'Optional seed was not committed before results')
 ctx['plan']=plan;ctx['plan_sha']=c['reviewed_training_plan']['sha256'];jwrite(ctx['run']/'training_plan_frozen.json',{'status':'FROZEN','sha256':ctx['plan_sha'],'plan':plan})
 return {'status':'S5_DOCUMENT_VERIFIED','note':'Human attestations + evidence hashes checked; not a digital-signature authentication service'}

def validate_role_rows(roles,unit_map,group_map=None):
 require(set(roles)==set(ROLES),'Only explicit allowed role manifests may be passed')
 keys={};samples=set();groups=set();units=set()
 for role in ROLES[:4]:
  rows=roles[role];require(rows,'Empty required role: '+role)
  ss=set();gg=set();uu=set();representatives={}
  for r in rows:
   require(r.get('role')==role and r.get('partition_status')=='FINAL','Wrong role or PROVISIONAL row')
   require(r.get('label') in {'positive','negative'} and r.get('eligibility_status')=='ELIGIBLE_PENDING_APPROVAL','Unadjudicated/unknown annotation')
   u=r['certification_unit_id'];g=r['split_group_id'];sid=r['sample_id']
   require(unit_map.get(u)==role,'Unit belongs to held-out/unlabeled/another role or absent assignment')
   if group_map is not None:require(group_map.get(g)==role,'Group belongs to held-out/unknown role')
   require(sid not in ss,'Duplicate sample');ss.add(sid);gg.add(g);uu.add(u)
   if str(r['is_representative']).lower()=='true':representatives[u]=representatives.get(u,0)+1
   if not r.get('mask_relative_path'):require(r['label']=='negative' and str(r.get('zero_mask_authorized')).lower()=='true','Unauthorized all-zero mask')
  require(not(ss&samples or gg&groups or uu&units),'Sample/group/unit overlap between learning roles')
  if role!='train':require(set(representatives)==uu and all(x==1 for x in representatives.values()),'Exactly one frozen representative per development unit required')
  samples|=ss;groups|=gg;units|=uu;keys[role]={r['sample_id']:r for r in rows}
 hn=roles['hard_negative_development'];require(hn,'Empty adjudicated hard negatives')
 require(len({r['sample_id'] for r in hn})==len(hn),'Duplicate hard negatives')
 for r in hn:
  peer=keys['development_policy'].get(r['sample_id']);require(peer and peer['label']=='negative','Hard negatives must be confirmed policy negatives')
  require(all(r.get(k)==peer.get(k) for k in peer if k!='role'),'Hard-negative alias changed metadata')
  require(r['role']=='hard_negative_development','Wrong hard-negative role')
 return True

def prepare_data(ctx):
 require(ctx['cfg']['RUN_MODE']=='FULL' and ctx['cfg']['JOB']!='audit','Audit/SMOKE: real data never loaded')
 require(ctx.get('plan') and not ctx['errors'],'S5/model permissions or functional validation not verified');c=ctx['cfg'];zpath=ctx['p02zip'];roles={}
 with zipfile.ZipFile(zpath) as z:
  # Phase02 stable('split', group) and stable('unit', group) use identical hash suffixes.
  # This establishes group barriers from non-label assignments without opening certification_units.csv.
  source=z.read('phase02_core.py').decode()
  require("gid=stable('split',group);uid=stable('unit',group)" in source,'Reviewed Phase02 group/unit identity rule changed')
  um=ctx['role_plan']['unit_role_map'];gm={}
  for u,assigned in um.items():
   require(re.fullmatch(r'unit_[0-9a-f]{24}',u),'Unknown unit identity schema')
   gm['split_'+u[5:]]=assigned
  for role in ROLES:
   access(ctx,role+'.csv',role,'READ_APPROVED_ROLE_MANIFEST')
   roles[role]=list(csv.DictReader(io.StringIO(z.read(role+'.csv').decode())))
  validate_role_rows(roles,um,gm)
  union=list(csv.DictReader(io.StringIO(z.read('development.csv').decode())))
  expected={r['sample_id'] for role in ROLES[1:4] for r in roles[role]}
  require({r['sample_id'] for r in union}==expected and len(union)==len(expected),'Development compatibility union mismatch')
  master={r['sample_id']:r for role in ROLES[1:4] for r in roles[role]};require(all(r==master[r['sample_id']] for r in union),'Development union metadata differs')
  shards=json.loads(z.read('data_shard_index.json'))
  registry=list(csv.DictReader(io.StringIO(z.read('dataset_registry.csv').decode())))
  # FINAL Phase02 attestations cover annotations; do not re-open curator evidence.
  approved=ctx['plan'].get('approved_original_sources',[]);rights={r['original_source_id']:r for r in registry}
  require(approved and all(rights.get(s,{}).get('research_use')=='PERMITTED' and rights[s].get('evidence_sha256') for s in approved),'Source rights/evidence not approved')
  sources=ctx['plan'].get('unit_original_source_ids',{});external=set(ctx['role_plan'].get('external_original_source_ids',[]))
  for role in ROLES:
   for row in roles[role]:
    ids=sources.get(row['certification_unit_id'],[]);require(ids and set(ids)<=set(approved) and not set(ids)&external,'Original-source permissions/held-out-source exclusion not established for learning unit')
 root=c['inputs_override'].get('raw_root')
 if not root:
  hits=[p.parent for p in Path(c['input_root']).rglob(COLLECTIONS[0]) if p.is_dir() and all((p.parent/x).is_dir() for x in COLLECTIONS)]
  require(len(hits)==1,'Raw extracted root missing/ambiguous; set inputs_override.raw_root');root=hits[0]
 root=Path(root);ctx['raw_root']=root;ctx['shards']=shards
 stagefiles=ctx['run']/'.verified_inputs'/'roles';stagefiles.mkdir(exist_ok=True)
 for role,rows in roles.items():
  # Reuse upstream checksum/annotation loader; re-hash actual raw image/mask bytes before use.
  p=stagefiles/(role+'.csv');cwrite(p,rows,list(rows[0]));ctx['p02module'].load_development_manifest(p,root,c['source_directory_overrides'])
 ctx['rows']=roles;ctx['role_hashes']={r:next(e['sha256'] for e in ctx['p02manifest']['output_artifacts'] if e['relative_path']==r+'.csv') for r in ROLES}
 require(ctx['plan'].get('role_hashes')==ctx['role_hashes'],'S5 plan must bind all five role hashes')
 ctx['training_authorized']=True
 jwrite(ctx['run']/'role_access_validation.json',{'status':'PASS','role_hashes':ctx['role_hashes'],'counts':{r:len(v) for r,v in roles.items()},'sealed_role_csvs_parsed':False,'heldout_exclusion':'non-label unit_role_map + verified Phase02 stable ID suffix rule'})
 return {'status':'APPROVED_DEVELOPMENT_READY'}

class DevelopmentDataset:
 def __init__(self,ctx,role):
  require(ctx.get('training_authorized') and role in ROLES,'Dataset role unauthorized');self.ctx=ctx;self.role=role
  self.rows=[r for r in ctx['rows'][role] if role=='train' or str(r['is_representative']).lower()=='true']
  self.rows=sorted(self.rows,key=lambda r:(r['certification_unit_id'],r['sample_id']))
 def __len__(self):return len(self.rows)
 def native(self,i):
  import numpy as np
  r=self.rows[i];ctx=self.ctx;root=under(ctx['raw_root']/ctx['cfg']['source_directory_overrides'].get(r['collection'],r['collection']),ctx['raw_root'])
  p=under(root/r['image_relative_path'],root);access(ctx,p,self.role,'READ_IMAGE')
  require(sha(p)==r['image_sha256'],'Image changed after validation')
  image,meta=ctx['p02module'].image_array(p,100_000_000);require(meta['exif_orientation']==1,'Unreviewed EXIF transform')
  if r.get('mask_relative_path'):
   mp=under(root/r['mask_relative_path'],root);access(ctx,mp,self.role,'READ_MASK');require(sha(mp)==r['mask_sha256'],'Mask changed')
   mask,_=ctx['p02module'].mask_array(mp,100_000_000,500*1024**2)
  else:mask=np.zeros(image.shape[:2],dtype=np.uint8)
  require(bool(mask.any())==(r['label']=='positive'),'Manifest/mask class mismatch')
  return ctx['p02module'].letterbox(image,mask,448)[:3]
 def __getitem__(self,i):
  import numpy as np,torch
  rgb,mask,valid=self.native(i)
  if self.role=='train':
   for axis in [0,1]:
    if random.random()<.5:rgb=np.flip(rgb,axis);mask=np.flip(mask,axis);valid=np.flip(valid,axis)
   k=random.randrange(4);rgb=np.rot90(rgb,k);mask=np.rot90(mask,k);valid=np.rot90(valid,k)
   bright=random.uniform(.9,1.1);contrast=random.uniform(.9,1.1);rgb=np.clip((rgb.astype(float)-127.5)*contrast+127.5,0,255)*bright;rgb=np.clip(rgb,0,255)
  x=(rgb.astype('float32')/255-np.array(PREPROCESS['normalization_mean'],dtype='float32'))/np.array(PREPROCESS['normalization_std'],dtype='float32')
  return torch.from_numpy(x.transpose(2,0,1).copy()),torch.from_numpy(mask[None].copy()).float(),torch.from_numpy(valid[None].copy()),i

def seed_all(seed):
 import numpy as np,torch
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
 torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
 torch.use_deterministic_algorithms(True,warn_only=False)

def common_loss(logits,target,valid):
 import torch
 import torch.nn.functional as F
 require(logits.shape==target.shape==valid.shape and logits.ndim==4 and logits.shape[1]==1,'Loss requires aligned B1HW')
 require(torch.isfinite(logits).all().item() and torch.isfinite(target).all().item(),'Nonfinite loss inputs')
 require(((target==0)|(target==1)).all().item(),'Target must be binary')
 v=valid.float();den=v.sum((1,2,3));require((den>0).all().item(),'Image has no valid pixels')
 bce=(F.binary_cross_entropy_with_logits(logits.float(),target.float(),reduction='none')*v).sum((1,2,3))/den
 prob=torch.sigmoid(logits.float());eps=1e-6
 dice=(2*(prob*target*v).sum((1,2,3))+eps)/((prob*v).sum((1,2,3))+(target*v).sum((1,2,3))+eps)
 loss=(.5*bce+.5*(1-dice)).mean();require(torch.isfinite(loss).item(),'Nonfinite loss');return loss

def check_package_pins(spec):
 require(spec.get('packages'),'Pinned installed dependency versions required')
 for n,v in spec['packages'].items():require(md.version(n)==v,'Package version mismatch: '+n)
 for item in spec.get('source_files',[]):require(sha(item['path'])==item['sha256'],'Source file mismatch')
 require(spec.get('license_sha256') and Path(spec.get('license_path','')).is_file() and sha(spec['license_path'])==spec['license_sha256'],'License evidence absent/changed')

def build_engine(engine,spec,device):
 import torch
 import torch.nn.functional as F
 check_package_pins(spec)
 needed={'torch','torchvision'}
 needed|={'segmentation-models-pytorch','timm'} if engine.startswith('unetpp_') else ({'transformers'} if engine=='segformer_b0' else set())
 require(needed<=set(spec['packages']),'Missing pinned core engine dependency versions: '+str(needed-set(spec['packages'])))
 class Adapter(torch.nn.Module):
  def __init__(self,base,output):super().__init__();self.base=base;self.output=output
  def forward(self,x):
   y=self.base(pixel_values=x).logits if self.output=='hf' else self.base(x)
   if self.output=='dmsr':y=y[0] # Official refined segmentation logit; boundary probability excluded from common loss.
   require(isinstance(y,torch.Tensor) and y.ndim==4 and y.shape[1]==1,'Official adapter requires one binary logit head')
   if self.output=='hf':y=F.interpolate(y,size=x.shape[-2:],mode='bilinear',align_corners=False)
   require(y.shape==(x.shape[0],1,448,448),'Official 448-grid shape test failed');return y
 if engine in {'unetpp_effb3','unetpp_convnext_tiny'}:
  import segmentation_models_pytorch as smp
  enc='efficientnet-b3' if engine=='unetpp_effb3' else 'tu-convnext_tiny'
  base=smp.UnetPlusPlus(encoder_name=enc,encoder_weights=None,in_channels=3,classes=1,activation=None);model=Adapter(base,'tensor')
 elif engine=='segformer_b0':
  from transformers import SegformerConfig,SegformerForSemanticSegmentation
  cfg=SegformerConfig(num_labels=1,depths=[2,2,2,2],hidden_sizes=[32,64,160,256],decoder_hidden_size=256,num_attention_heads=[1,2,5,8])
  model=Adapter(SegformerForSemanticSegmentation(cfg),'hf')
 else:
  root=Path(spec.get('source_root',''));require(root.is_dir() and re.fullmatch('[0-9a-f]{40}',spec.get('source_commit','')),'Pinned official source tree/commit required')
  require(spec.get('source_files'),'Pinned source file manifest required')
  listed={Path(x['path']).resolve() for x in spec['source_files']};actual={p.resolve() for p in root.rglob('*.py')}
  require(actual and actual<=listed,'All executable official source files must be hash-pinned')
  # No downloading or build attempt. All dependencies must already be compatible offline.
  if str(root.resolve()) not in sys.path:sys.path.insert(0,str(root.resolve()))
  if engine=='dmsrcrack':
   path=root/'model.py';name='_dmsr_'+spec['source_commit'][:10];ispec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(ispec);ispec.loader.exec_module(mod)
   model=Adapter(mod.DMSRCrack(in_channels=3,num_classes=2),'dmsr')
  else:
   require('models' not in sys.modules or str(Path(sys.modules['models'].__file__).resolve()).startswith(str(root.resolve())+os.sep),'Python module collision: use a clean kernel')
   mod=importlib.import_module('models');require(Path(mod.__file__).resolve().is_relative_to(root.resolve()),'Wrong SCSegamba source imported')
   args=types.SimpleNamespace(device=device,BCELoss_ratio=.5,DiceLoss_ratio=.5,Norm_Type='GN')
   base,_=mod.build_model(args);model=Adapter(base,'tensor')
 if spec['initialization']=='GENERIC_PRETRAINED':
  p=Path(spec['weights_path']);require(sha(p)==spec['weights_sha256'],'Generic weights mismatch')
  weights=torch.load(p,map_location='cpu',weights_only=True)
  # Encoder-only initialization is explicit; never silently ignore missing keys.
  if spec.get('weights_target')=='encoder' and hasattr(model.base,'encoder'):model.base.encoder.load_state_dict(weights,strict=True)
  else:model.base.load_state_dict(weights,strict=True)
 return model.to(device)

def sync(device):
 import torch
 if str(device).startswith('cuda'):torch.cuda.synchronize()
def amp_tools(device,enabled):
 import torch
 enabled=bool(enabled and str(device).startswith('cuda') and torch.cuda.is_available())
 try:scaler=torch.amp.GradScaler('cuda',enabled=enabled)
 except (AttributeError,TypeError):scaler=torch.cuda.amp.GradScaler(enabled=enabled)
 return scaler,lambda:torch.autocast(device_type='cuda',dtype=torch.float16,enabled=enabled) if enabled else contextlib.nullcontext()

def technical_checks(ctx):
 import torch
 c=ctx['cfg'];reports=[]
 for engine in ENGINES:
  r={'engine_id':engine,'status':'NOT_RUN','reason':'No approved pinned engine specification; no automatic install/download','real_training_performed':False}
  if ctx.get('plan') and engine in ctx['plan']['engines'] and (engine==c['ENGINE_ID'] or c['JOB']=='select'):
   try:
    require(torch.cuda.is_available() and str(c['device']).startswith('cuda'),'BUILD_BLOCKED: actual CUDA forward/backward required')
    seed_all(42);model=build_engine(engine,ctx['plan']['engines'][engine],c['device']);model.train();torch.cuda.reset_peak_memory_stats()
    x=torch.zeros(2,3,448,448,device=c['device']);y=torch.zeros(2,1,448,448,device=c['device']);v=torch.ones_like(y,dtype=torch.bool)
    sync(c['device']);t=time.perf_counter();loss=common_loss(model(x),y,v);loss.backward();sync(c['device']);batch_seconds=time.perf_counter()-t
    require(all(q.grad is None or torch.isfinite(q.grad).all().item() for q in model.parameters()),'Nonfinite official-model gradients')
    state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};model.eval()
    with torch.no_grad():a=model(x).detach().cpu()
    model.load_state_dict(state,strict=True)
    with torch.no_grad():b=model(x).detach().cpu()
    require(torch.equal(a,b),'Reload output differs')
    r.update(status='PASS',shape=list(a.shape),reload_equal=True,forward_backward_seconds=batch_seconds,peak_gpu_bytes=torch.cuda.max_memory_allocated(),parameters=sum(p.numel() for p in model.parameters()),hardware=ctx['env']['gpu'])
    del model,x,y,v,state,a,b;torch.cuda.empty_cache()
   except Exception as e:r.update(status='BUILD_BLOCKED',reason=str(e))
  reports.append(r);jwrite(ctx['run']/'model_checks'/(engine+'.json'),r);ctx['technical'][engine]=r
 jwrite(ctx['run']/'model_checks'/'roster.json',reports);return reports

def rng_state():
 import numpy as np,torch
 n=np.random.get_state()
 return {'python':random.getstate(),'numpy':[n[0],n[1].tolist(),n[2],n[3],n[4]],'torch':torch.get_rng_state(),'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}
def restore_rng(s):
 import numpy as np,torch
 random.setstate(s['python']);n=s['numpy'];np.random.set_state((n[0],np.array(n[1],dtype='uint32'),n[2],n[3],n[4]));torch.set_rng_state(s['torch'].cpu())
 if s['cuda']:torch.cuda.set_rng_state_all([x.cpu() for x in s['cuda']])
def save_checkpoint(path,state):
 import torch
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');torch.save(state,tmp)
 with tmp.open('rb') as f:os.fsync(f.fileno())
 h=sha(tmp);tmp.replace(p);twrite(str(p)+'.sha256',h+'  '+p.name+'\n');return h

def load_checkpoint(path,identity,map_location='cpu'):
 import torch
 p=Path(path);parts=Path(str(p)+'.sha256').read_text().strip().split('  ',1);require(parts==[sha(p),p.name],'Checkpoint digest mismatch')
 s=torch.load(p,map_location=map_location,weights_only=True);require(s['identity']==identity,'Checkpoint identity mismatch');return s

def job_identity(ctx,engine,seed):
 return {'phase01_sha256':P01_SHA,'phase02_sha256':ctx['controls']['phase02']['sha256'],'plan_sha256':ctx['plan_sha'],'code_sha256':ctx['identity']['code_sha256'],'role_hashes':ctx['role_hashes'],'engine_id':engine,'seed':seed,'recipe_id':'clean_common_loss','training_protocol_sha256':digest(jb({'micro_batch':ctx['plan']['engines'][engine].get('micro_batch',2),'amp':ctx['plan']['engines'][engine].get('amp',True),'effective_batch':16,'epochs':100,'warmup':5,'patience':15,'weight_decay':.01})),'environment_sha256':digest(jb(ctx['env']))}

def metric_row(prob,truth,valid,primitives=None):
 import numpy as np
 p=primitives or sys.modules[__name__];raw=(prob>=.55)&valid;op,n=p.valid_prediction_components(prob,valid);truth=truth.astype(bool)&valid
 out={'is_positive':bool(truth.any()),'false_valid':bool(n),'valid_component_count':int(n)}
 for name,mask in [('raw',raw),('op',op)]:
  inter=int((mask&truth).sum());den=int(mask.sum()+truth.sum());union=int((mask|truth).sum())
  out[name+'_dice']=2*inter/den if den else 1.;out[name+'_iou']=inter/union if union else 1.;out[name+'_cldice']=float(p.cldice(mask,truth,valid))
 return out

def eval_model(model,ds,device):
 import numpy as np,torch
 model.eval();losses=[];dices=[]
 with torch.inference_mode():
  for i in range(len(ds)):
   x,y,v,_=ds[i];x=x[None].to(device);y=y[None].to(device);v=v[None].to(device);z=model(x).float();losses.append(float(common_loss(z,y,v)))
   if y.any():dices.append(metric_row(torch.sigmoid(z)[0,0].cpu().numpy(),y[0,0].cpu().numpy(),v[0,0].cpu().numpy(),ds.ctx['p02module'])['op_dice'])
 require(dices,'No positive development-model representatives');return float(np.mean(losses)),float(np.mean(dices))

def train_job(ctx):
 import numpy as np,torch
 c=ctx['cfg'];require(c['RUN_MODE']=='FULL' and c['JOB']=='train' and ctx['training_authorized'],'Real training not authorized for this job')
 engine=c['ENGINE_ID'];seed=c['SEED'];require(ctx['technical'].get(engine,{}).get('status')=='PASS','Actual engine GPU technical check not passed')
 require(engine in [s['engine_id'] for s in ctx['plan']['slots']],'Engine not in frozen roster')
 spec=ctx['plan']['engines'][engine];require(spec['learning_rate']==c['learning_rate'],'Config LR differs from frozen plan')
 require(c['micro_batch']==spec.get('micro_batch',2) and c['amp']==spec.get('amp',True),'Microbatch/AMP differ from frozen per-engine protocol')
 device=c['device'];seed_all(seed);model=build_engine(engine,spec,device);ds=DevelopmentDataset(ctx,'train');dev=DevelopmentDataset(ctx,'development_model')
 optimizer=torch.optim.AdamW(model.parameters(),lr=spec['learning_rate'],weight_decay=.01)
 scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lambda e:(e+1)/5 if e<5 else .5*(1+math.cos(math.pi*(e-5)/95)))
 scaler,autocast=amp_tools(device,c['amp']);generator=torch.Generator().manual_seed(seed)
 folder=ctx['run']/'checkpoints'/engine/str(seed);folder.mkdir(parents=True,exist_ok=True);last=folder/'last.pt';best=folder/'best.pt';identity=job_identity(ctx,engine,seed)
 state={'epoch':0,'cursor':0,'order':None,'best_score':None,'bad_epochs':0,'history':[],'epoch_loss_sum':0.,'epoch_images':0,'epoch_dice_sum':0.,'epoch_positive_images':0,'elapsed_train_seconds':0.,'optimizer_steps':0,'complete':False}
 def save(target):
  payload={**state,'identity':identity,'model':model.state_dict(),'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict(),'scaler':scaler.state_dict(),'rng':rng_state(),'generator_state':generator.get_state(),'accumulation_pending':False}
  h=save_checkpoint(target,payload);cwrite(ctx['run']/'data_access_log.csv',ctx['access'],['utc','last_utc','read_count','path','role','operation']);return h
 if last.exists():
  ck=load_checkpoint(last,identity,device);model.load_state_dict(ck['model']);optimizer.load_state_dict(ck['optimizer']);scheduler.load_state_dict(ck['scheduler']);scaler.load_state_dict(ck['scaler']);generator.set_state(ck['generator_state'].cpu());restore_rng(ck['rng'])
  state={k:ck[k] for k in state}
 if state['complete']:require(best.exists(),'Completed job lacks best checkpoint')
 torch.cuda.reset_peak_memory_stats();stopped=False
 try:
  while state['epoch']<100 and not state['complete']:
   if state['order'] is None:state['order']=torch.randperm(len(ds),generator=generator).tolist()
   model.train()
   while state['cursor']<len(ds):
    remaining=c['SESSION_BUDGET_HOURS']*3600-(time.monotonic()-ctx['started'])
    if remaining<=c['budget_buffer_minutes']*60:save(last);raise BudgetStop('Checkpoint saved at optimizer boundary; resume unsealed run with identical identity')
    indices=state['order'][state['cursor']:state['cursor']+16];optimizer.zero_grad(set_to_none=True);step_loss=0.;sync(device);t=time.perf_counter()
    for offset in range(0,len(indices),c['micro_batch']):
     batch=[ds[i] for i in indices[offset:offset+c['micro_batch']]];x,y,v=[torch.stack([b[j] for b in batch]).to(device) for j in range(3)]
     with autocast():z=model(x);loss=common_loss(z,y,v);weighted=loss*len(batch)/len(indices)
     with torch.no_grad():
      probs=torch.sigmoid(z.float()).cpu().numpy();truth=y.cpu().numpy();vp=v.cpu().numpy()
      for pp,tt,vv in zip(probs,truth,vp):
       if tt.any():state['epoch_dice_sum']+=metric_row(pp[0],tt[0],vv[0],ctx['p02module'])['op_dice'];state['epoch_positive_images']+=1
     scaler.scale(weighted).backward();step_loss+=float(loss.detach())*len(batch)
    scaler.unscale_(optimizer);require(all(p.grad is None or torch.isfinite(p.grad).all().item() for p in model.parameters()),'Nonfinite gradients')
    scaler.step(optimizer);scaler.update();sync(device)
    state['elapsed_train_seconds']+=time.perf_counter()-t;state['cursor']+=len(indices);state['epoch_images']+=len(indices);state['epoch_loss_sum']+=step_loss;state['optimizer_steps']+=1
    # The last completed epoch/checkpoint is a transaction; hard kills replay unsaved steps with restored RNG.
    if state['optimizer_steps']%100==0:save(last)
   dl,dd=eval_model(model,dev,device);tl=state['epoch_loss_sum']/state['epoch_images'];improved=state['best_score'] is None or dd>state['best_score']
   if improved:state['best_score']=dd;state['bad_epochs']=0
   else:state['bad_epochs']+=1
   state['history'].append({'epoch':state['epoch']+1,'seed':seed,'engine_id':engine,'train_loss':tl,'train_dice':state['epoch_dice_sum']/state['epoch_positive_images'] if state['epoch_positive_images'] else None,'development_model_loss':dl,'development_model_dice':dd,'learning_rate':optimizer.param_groups[0]['lr'],'best':improved,'early_stop':state['bad_epochs']>=15})
   state['epoch']+=1;state.update(cursor=0,order=None,epoch_loss_sum=0.,epoch_images=0,epoch_dice_sum=0.,epoch_positive_images=0);scheduler.step();state['complete']=state['epoch']>=100 or state['bad_epochs']>=15
   if improved:save(best)
   save(last);cwrite(ctx['run']/'training_history'/f'{engine}_{seed}.csv',state['history'],list(state['history'][0]))
 except BudgetStop:stopped=True
 finally:
  if state['history']:cwrite(ctx['run']/'training_history'/f'{engine}_{seed}.csv',state['history'],list(state['history'][0]))
  jwrite(ctx['run']/'training_job_status.json',{'engine_id':engine,'seed':seed,'complete':state['complete'],'budget_stopped':stopped,'epoch':state['epoch'],'cursor':state['cursor'],'optimizer_steps':state['optimizer_steps'],'resume_policy':'exact saved optimizer boundary; replay any steps after most recent durable checkpoint','partial_final_effective_batch':'Actual remaining count; each image equally weighted'})
  if best.exists():
   ck=load_checkpoint(best,identity,device);model.load_state_dict(ck['model']);model.eval();test=torch.zeros(1,3,448,448,device=device)
   with torch.no_grad():require(torch.isfinite(model(test)).all().item(),'Best checkpoint reload nonfinite')
   row={'engine_id':engine,'recipe_id':c['recipe_id'],'seed':seed,'checkpoint_ref':str(best.relative_to(ctx['run'])),'SHA256':sha(best),'train_development_hashes':json.dumps(ctx['role_hashes'],sort_keys=True),'config_sha256':ctx['identity']['config_sha256'],'plan_sha256':ctx['plan_sha'],'code_sha256':identity['code_sha256'],'environment_sha256':identity['environment_sha256'],'load_test_pass':True,'complete':state['complete'],'pretraining_provenance':spec['initialization'],'identity_json':json.dumps(identity,sort_keys=True),'best_development_model_dice':state['best_score'],'parameters':sum(p.numel() for p in model.parameters()),'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'training_images_per_second':(state['epoch']*len(ds)+state['cursor'])/max(state['elapsed_train_seconds'],1e-12),'micro_batch':c['micro_batch'],'learning_rate':spec['learning_rate']}
   ctx['registry'].append(row)
  del model;torch.cuda.empty_cache()
 if stopped:ctx['budget_stopped']=True;raise BudgetStop('BUDGET_STOP: unsealed run can resume; saved outputs still export below')
 return {'complete':state['complete'],'best_score':state['best_score'],'engine':engine,'seed':seed}

def collect_jobs(ctx):
 rows=list(ctx['registry']);c=ctx['cfg']
 for item in c['job_inputs']:
  root=Path(item['run_dir']);mfile=root/'phase03_manifest.json';require((root/'SEALED.json').exists(),'Imported jobs must be sealed saved outputs')
  require(sha(mfile)==item['manifest_sha256'],'Imported job manifest changed');m=jread(mfile)
  require(m.get('phase')=='03' and m.get('schema_version')=='1.0' and jread(root/'SEALED.json').get('manifest_sha256')==item['manifest_sha256'],'Imported run seal/schema mismatch')
  require(m['code_sha256']==ctx['identity']['code_sha256'] and m['blueprint_sha256']==BLUEPRINT_SHA,'Imported code/blueprint differs')
  catalog={e['relative_path']:e for e in m['output_artifacts']};rp=root/'checkpoint_registry.csv';require(sha(rp)==catalog['checkpoint_registry.csv']['sha256'],'Registry mismatch')
  for row in cread(rp):
   identity=json.loads(row['identity_json']);require(identity==job_identity(ctx,row['engine_id'],int(row['seed'])),'Imported job provenance/config/environment differs')
   require(str(row['complete']).lower()=='true' and str(row['load_test_pass']).lower()=='true','Partial/failed seed cannot enter ensemble')
   src=under(root/row['checkpoint_ref'],root);require(sha(src)==row['SHA256']==catalog[row['checkpoint_ref']]['sha256'],'Imported checkpoint hash differs')
   # Materialize verified checkpoints into this run so ALL_OUTPUTS truly includes used weights.
   dst=ctx['run']/'checkpoints'/row['engine_id']/str(row['seed'])/'best.pt';dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():require(sha(dst)==row['SHA256'],'Conflicting same-seed checkpoint')
   else:
    require(shutil.disk_usage(dst.parent).free>src.stat().st_size+ctx['cfg']['storage_reserve_bytes'],'Insufficient storage to attach checkpoint');shutil.copyfile(src,dst)
   twrite(str(dst)+'.sha256',row['SHA256']+'  best.pt\n');row['checkpoint_ref']=str(dst.relative_to(ctx['run']));rows.append(row)
   history=f"training_history/{row['engine_id']}_{row['seed']}.csv"
   if history in catalog:
    require(sha(root/history)==catalog[history]['sha256'],'Training history changed');atomic(ctx['run']/history,(root/history).read_bytes())
 unique={}
 for row in rows:
  key=(row['engine_id'],int(row['seed']));require(key not in unique or unique[key]['SHA256']==row['SHA256'],'Different checkpoints for one engine/seed');unique[key]=row
 ctx['registry']=list(unique.values());return ctx['registry']

def cached_predictions(ctx,engine,models,role,checkpoint_hashes):
 import numpy as np,torch
 ds=DevelopmentDataset(ctx,role);directory=ctx['run']/'predictions'/engine/role;directory.mkdir(parents=True,exist_ok=True);files=[]
 expected_bytes=len(ds)*(3*448*448*4+2*448*448)
 current=sum(p.stat().st_size for p in (ctx['run']/'predictions').rglob('*.npz'))
 require(current+expected_bytes<=ctx['cfg']['max_prediction_cache_bytes'],'Prediction cache budget exceeded; increase reviewed storage allocation or use fewer approved units via upstream amendment, never truncate')
 require(shutil.disk_usage(directory).free>expected_bytes+ctx['cfg']['storage_reserve_bytes'],'Insufficient cache disk')
 for m in models:m.eval()
 with torch.inference_mode():
  for i,r in enumerate(ds.rows):
   require(time.monotonic()-ctx['started']<ctx['cfg']['SESSION_BUDGET_HOURS']*3600-ctx['cfg']['budget_buffer_minutes']*60,'Session budget exhausted during development prediction')
   x,y,v,_=ds[i];x=x[None].to(ctx['cfg']['device']);zs=np.stack([m(x)[0,0].float().cpu().numpy() for m in models])
   require(np.isfinite(zs).all(),'Nonfinite logits');p=directory/(r['sample_id']+'.npz');tmp=p.with_name(p.name+'.tmp')
   with tmp.open('wb') as f:np.savez_compressed(f,logits=zs,truth=y[0].numpy().astype('uint8'),valid=v[0].numpy(),sample_id=r['sample_id'],unit_id=r['certification_unit_id'])
   tmp.replace(p);files.append(p)
   ctx['pred_index'].append({'sample_id':r['sample_id'],'unit_id':r['certification_unit_id'],'engine_id':engine,'member_id':'42,123,2026_LOGITS','checkpoint_hash':';'.join(checkpoint_hashes),'preproc_T_filter_hash':digest(jb({'preprocess':PREPROCESS,'T':None,'filter':FILTER})),'prediction_shard_ref':str(p.relative_to(ctx['run'])),'prediction_sha256':sha(p),'inference_dtype':'float32','score_version_hash':digest(b'phase03_base_only_v1'),'role':role,'creation_time':utc()})
 return files,ds

def ensemble_probability(logits,T):
 import numpy as np
 from scipy.special import expit
 require(len(logits)==3 and .05<=T<=20 and np.isfinite(logits).all(),'Invalid three-member logits/temperature')
 return expit(np.asarray(logits,dtype='float64')/T).mean(axis=0)

def image_nll(p,y,v):
 import numpy as np
 require(np.any(v),'No valid pixels');q=np.clip(p[v],1e-7,1-1e-7);t=y[v];return float(-(t*np.log(q)+(1-t)*np.log1p(-q)).mean())

def fit_temperature(iterator_factory):
 import numpy as np
 from scipy.optimize import minimize_scalar
 def objective(logT):
  vals=[image_nll(ensemble_probability(z,float(np.exp(logT))),y,v) for z,y,v in iterator_factory()]
  require(vals and np.isfinite(vals).all(),'Temperature NLL undefined');return float(np.mean(vals))
 baseline=objective(0.)
 try:
  low,high=math.log(.05),math.log(20.);result=minimize_scalar(objective,bounds=(low,high),method='bounded',options={'xatol':1e-5,'maxiter':80})
  require(result.success and math.isfinite(result.fun) and result.fun<=baseline+1e-9,'Optimizer failed or worsened baseline NLL')
  T=float(math.exp(result.x));return {'status':'FITTED','T':T,'optimizer':'scipy bounded minimize_scalar(log T)','mean_image_ensemble_NLL_before':baseline,'mean_image_ensemble_NLL_after':float(result.fun),'converged':True,'boundary_hit':min(abs(result.x-low),abs(result.x-high))<1e-3,'evaluations':int(result.nfev),'role':'development_probability','risk_calibration':False}
 except Exception as e:return {'status':'FALLBACK_T1','T':1.,'reason':str(e),'mean_image_ensemble_NLL_before':baseline,'mean_image_ensemble_NLL_after':baseline,'converged':False,'boundary_hit':None,'role':'development_probability','risk_calibration':False}

def cache_iterator(files):
 import numpy as np
 for p in files:
  with np.load(p,allow_pickle=False) as d:yield d['logits'],d['truth'],d['valid']

def reliability(files,T,bins=15):
 import numpy as np
 # Image-balanced bin mass, while raw pixel counts are separately reported.
 mass=np.zeros(bins);pos=np.zeros(bins);conf=np.zeros(bins);counts=np.zeros(bins,dtype='int64');n=0;nll=[]
 for z,y,v in cache_iterator(files):
  p=ensemble_probability(z,T);q=p[v];truth=y[v];idx=np.minimum((q*bins).astype(int),bins-1);n+=1;nll.append(image_nll(p,y,v))
  for k in range(bins):
   take=idx==k;count=int(take.sum());counts[k]+=count;mass[k]+=count/len(q);pos[k]+=float(truth[take].sum())/len(q);conf[k]+=float(q[take].sum())/len(q)
 require(n>0,'Empty reliability data');rows=[]
 for k in range(bins):rows.append({'bin':k,'count':int(counts[k]),'image_balanced_mass':float(mass[k]/n),'mean_probability':float(conf[k]/mass[k]) if mass[k] else None,'foreground_frequency':float(pos[k]/mass[k]) if mass[k] else None})
 ece=sum(r['image_balanced_mass']*abs(r['mean_probability']-r['foreground_frequency']) for r in rows if r['count'])
 return {'bins':rows,'image_balanced_ECE':ece,'n_images':n,'valid_pixel_count':int(counts.sum()),'mean_image_NLL':float(np.mean(nll))}

def bootstrap_ci(values):
 import numpy as np
 a=np.asarray(values,float)
 if len(a)<2:return [None,None]
 rng=np.random.default_rng(42);means=[float(a[rng.integers(0,len(a),len(a))].mean()) for _ in range(1000)]
 return [float(x) for x in np.quantile(means,[.025,.975])]

def summarize_metrics(rows,engine,member,hn_ids):
 import numpy as np
 positive=[r for r in rows if r['is_positive']];neg=[r for r in rows if r['sample_id'] in hn_ids]
 require(all(not r['is_positive'] for r in neg),'Hard-negative alias contains positive')
 out={'engine_id':engine,'member_id':member,'population':'one frozen representative per development_policy unit','n_positive':len(positive),'n_hard_negative':len(neg),'unit_ids_sha256':digest(jb(sorted(r['unit_id'] for r in rows))),'status':'EVALUATED' if positive and neg else 'NOT_EVALUABLE'}
 for metric in ['raw_dice','raw_iou','raw_cldice','op_dice','op_iou','op_cldice']:
  values=[r[metric] for r in positive];out[metric]=float(np.mean(values)) if values else None;lo,hi=bootstrap_ci(values);out[metric+'_ci_low']=lo;out[metric+'_ci_high']=hi
 out['hard_negative_false_valid_rate']=float(np.mean([r['false_valid'] for r in neg])) if neg else None
 out['ci_status']='DESCRIPTIVE_UNIT_BOOTSTRAP_95_PERCENT' if len(positive)>=2 else 'NOT_ESTIMABLE_N_LT_2'
 return out

def profile_ensemble(models,ds,device,T):
 import numpy as np,torch
 x=ds[0][0][None].to(device);times=[]
 with torch.inference_mode():
  for _ in range(5):p=torch.stack([torch.sigmoid(m(x)/T) for m in models]).mean(0)
  sync(device);torch.cuda.reset_peak_memory_stats()
  for _ in range(20):
   sync(device);t=time.perf_counter();p=torch.stack([torch.sigmoid(m(x)/T) for m in models]).mean(0);sync(device);times.append((time.perf_counter()-t)*1000)
 return {'median_latency_ms':float(np.median(times)),'inference_images_per_second':1000/float(np.mean(times)),'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'latency_scope':'M3 forward + temperature + mean probability; batch1; excludes disk/preprocessing/CPU component filtering','warmup_iterations':5,'timed_iterations':20}

def ensemble_job(ctx):
 import numpy as np,torch
 c=ctx['cfg'];require(c['RUN_MODE']=='FULL' and c['JOB'] in {'ensemble','select'} and ctx['training_authorized'],'Ensemble fitting/evaluation not authorized')
 collect_jobs(ctx);targets=[s['engine_id'] for s in ctx['plan']['slots']] if c['JOB']=='select' else [c['ENGINE_ID']]
 for engine in targets:
  require(ctx['technical'].get(engine,{}).get('status')=='PASS','Actual official technical test unavailable: '+engine)
  records=sorted([r for r in ctx['registry'] if r['engine_id']==engine and int(r['seed']) in SEEDS],key=lambda r:SEEDS.index(int(r['seed'])))
  require([int(r['seed']) for r in records]==SEEDS and all(str(r['complete']).lower()=='true' for r in records),'Three complete main seed jobs required: '+engine)
  models=[]
  try:
   for r in records:
    model=build_engine(engine,ctx['plan']['engines'][engine],c['device']);ck=load_checkpoint(ctx['run']/r['checkpoint_ref'],job_identity(ctx,engine,int(r['seed'])),c['device']);model.load_state_dict(ck['model']);model.eval();models.append(model)
   hashes=[r['SHA256'] for r in records];probfiles,_=cached_predictions(ctx,engine,models,'development_probability',hashes)
   cal=fit_temperature(lambda:cache_iterator(probfiles));cal['checkpoint_hashes']=hashes;cal['role_sha256']=ctx['role_hashes']['development_probability'];cal['reliability_before']=reliability(probfiles,1.);cal['reliability_after']=reliability(probfiles,cal['T']);ctx['calibrations'][engine]=cal
   files,ds=cached_predictions(ctx,engine,models,'development_policy',hashes);hn_ids={r['sample_id'] for r in ctx['rows']['hard_negative_development'] if str(r['is_representative']).lower()=='true'}
   members={str(s):[] for s in SEEDS};members['ensemble']=[]
   from scipy.special import expit
   for file,r,(z,y,v) in zip(files,ds.rows,cache_iterator(files)):
    for key,p in [(str(seed),expit(z[i]/cal['T'])) for i,seed in enumerate(SEEDS)]+[('ensemble',ensemble_probability(z,cal['T']))]:
     members[key].append({'sample_id':r['sample_id'],'unit_id':r['certification_unit_id'],**metric_row(p,y,v,ctx['p02module'])})
   for member,rows in members.items():
    cwrite(ctx['run']/'per_seed_metrics'/f'{engine}_{member}.csv',rows,list(rows[0]));ctx['summaries'].append(summarize_metrics(rows,engine,member,hn_ids))
   eff=profile_ensemble(models,ds,c['device'],cal['T']);eff.update(engine_id=engine,hardware=ctx['env']['gpu'],parameters_per_member=int(records[0]['parameters']))
   ctx.setdefault('efficiency',[]).append(eff);ctx.setdefault('policy_cache',{})[engine]={'files':files,'dataset':ds,'rows':members['ensemble']}
   for item in ctx['pred_index']:
    if item['engine_id']==engine:item['preproc_T_filter_hash']=digest(jb({'preprocess':PREPROCESS,'T':cal['T'],'filter':FILTER}));item['temperature']=cal['T']
  finally:
   models.clear();torch.cuda.empty_cache()
 jwrite(ctx['run']/'probability_calibration.json',{'status':'EVALUATED','engines':ctx['calibrations'],'risk_calibration_performed':False});return {'engines_evaluated':targets}

def choose_engine(summaries,efficiency):
 candidates=[r for r in summaries if r['member_id']=='ensemble'];require(candidates and len({r['unit_ids_sha256'] for r in candidates})==1,'Engine selection must use identical development-policy units')
 passing=[r for r in candidates if r['status']=='EVALUATED' and r['n_positive']>0 and r['n_hard_negative']>0 and r['op_iou']>=.56 and r['hard_negative_false_valid_rate']<=.35]
 if not passing:return None
 best=max(r['op_cldice'] for r in passing);passing=[r for r in passing if best-r['op_cldice']<=1e-6]
 fp=min(r['hard_negative_false_valid_rate'] for r in passing);passing=[r for r in passing if r['hard_negative_false_valid_rate']==fp]
 times={r['engine_id']:r['median_latency_ms'] for r in efficiency};require(all(r['engine_id'] in times and math.isfinite(times[r['engine_id']]) for r in passing),'Actual synchronized latency required')
 return min(passing,key=lambda r:(times[r['engine_id']],r['engine_id']))['engine_id']

def select_primary(ctx):
 require(ctx['cfg']['RUN_MODE']=='FULL' and ctx['cfg']['JOB']=='select' and ctx['training_authorized'],'Primary freeze not authorized')
 expected={s['engine_id'] for s in ctx['plan']['slots']};actual={r['engine_id'] for r in ctx['summaries'] if r['member_id']=='ensemble'}
 require(actual==expected and not ctx['errors'],'All three approved engines must finish comparison without unresolved errors')
 chosen=choose_engine(ctx['summaries'],ctx['efficiency']);status='PASS' if chosen else 'COMPLETE_NEGATIVE';ctx['scientific_status']=status
 jwrite(ctx['run']/'primary_engine_selection.json',{'status':status,'engine_id':chosen,'rule':'IoU>=.56; HN false-valid<=.35; clDice descending, 1e-6 tie tolerance, lower FP, lower median latency, lexical ID','role':'development_policy','risk_guarantee':False})
 if chosen:
  records=[r for r in ctx['registry'] if r['engine_id']==chosen and int(r['seed']) in SEEDS]
  require(len(records)==3,'Primary ensemble member count differs')
  m={'status':'FROZEN','engine_id':chosen,'members':sorted(records,key=lambda r:int(r['seed'])),'seeds':SEEDS,'M':3,'temperature':ctx['calibrations'][chosen]['T'],'preprocess':PREPROCESS,'filter':FILTER,'phase02_sha256':ctx['controls']['phase02']['sha256'],'plan_sha256':ctx['plan_sha'],'code_sha256':ctx['identity']['code_sha256'],'frozen_at':utc(),'phase04_authorized':True,'calibration_or_test_access':False}
  jwrite(ctx['run']/'primary_ensemble_manifest.json',m);jwrite(ctx['run']/'ensemble_smoke_test.json',{'status':'PASS','engine_id':chosen,'evidence':'Three verified checkpoint reloads and finite policy probabilities during actual ensemble job','risk_certification':False})
 return {'status':status,'engine_id':chosen}

FIGURE_NAMES=['Fig03_01_engine_comparison.png','Fig03_02_seed_training_curves.png','Fig03_03_temperature_reliability.png','Fig03_04_hard_negative_tradeoff.png','Fig03_05_efficiency.png','Fig03_06_prediction_examples.png','Fig03_07_failure_cases.png']
def plot_setup():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white'})
 return plt

def finish_figure(fig,path,synthetic=False):
 plt=plot_setup()
 if synthetic:fig.text(.5,.015,'SYNTHETIC — FUNCTIONAL TEST ONLY',ha='center',color='#b2182b',weight='bold',fontsize=11)
 fig.tight_layout(rect=(0,.055 if synthetic else .025,1,.96));Path(path).parent.mkdir(exist_ok=True,parents=True);fig.savefig(path,dpi=300);plt.close(fig)
 return str(path)

def figure_workflow(path):
 plt=plot_setup();fig,ax=plt.subplots(figsize=(10,5));ax.set_axis_off()
 boxes=[(.02,.66,.27,.20,'FINAL data + S5\nVerified code / permissions'),(.365,.66,.27,.20,'Train three seeds / engine\nSelect on development_model'),(.71,.66,.27,.20,'Fit one shared temperature\ndevelopment_probability'),(.71,.20,.27,.20,'Evaluate fixed base gate\ndevelopment_policy + HN'),(.365,.20,.27,.20,'Freeze one M=3 ensemble\nWeights + T + preprocessing'),(.02,.20,.27,.20,'Phase04 handoff\nLater Phase06 risk certification')]
 from matplotlib.patches import FancyBboxPatch
 for x,y,w,h,label in boxes:
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.01',facecolor='#edf4f8',edgecolor='#0072b2',linewidth=1.5));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
 for start,end in [((.30,.76),(.355,.76)),((.645,.76),(.70,.76)),((.845,.64),(.845,.42)),((.70,.30),(.645,.30)),((.355,.30),(.30,.30))]:ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'#333','lw':1.5})
 ax.set_title('Phase03 methodology · development only',fontsize=15,pad=16);fig.text(.5,.06,'No calibration/test labels • Technical or permission fallbacks only • A blocked run cannot freeze a primary engine',ha='center',fontsize=9)
 finish_figure(fig,path)

def figure_engine_comparison(rows,path,synthetic=False):
 plt=plot_setup();ens=[r for r in rows if r['member_id']=='ensemble'];require(ens,'No engine data')
 require(len({r['unit_ids_sha256'] for r in ens})==1,'Figure populations differ');fig,axes=plt.subplots(1,3,figsize=(11,4.5));colors=['#0072b2','#009e73','#d55e00']
 for ax,metric,title in zip(axes,['op_dice','op_iou','op_cldice'],['Crack Dice','Crack IoU','Crack clDice']):
  for i,r in enumerate(ens):
   v=r[metric];require(v is not None,'Undefined figure value');ax.bar(i,v,color=colors[i%3],width=.65)
   lo,hi=r.get(metric+'_ci_low'),r.get(metric+'_ci_high')
   if lo is not None:ax.errorbar(i,v,yerr=[[max(0,v-lo)],[max(0,hi-v)]],color='black',capsize=3)
  ax.set_xticks(range(len(ens)),[r['engine_id']+'\nn='+str(r['n_positive']) for r in ens],rotation=20,ha='right',fontsize=8);ax.set_ylim(0,1);ax.set_title(title)
 fig.suptitle('Same development-policy units · operational masks · descriptive 95% unit-bootstrap CI')
 finish_figure(fig,path,synthetic)

def figure_training(history,path,synthetic=False):
 plt=plot_setup();require(history,'No actual seed history');fig,axes=plt.subplots(1,2,figsize=(11,4.5));keys=sorted({(r['engine_id'],str(r['seed'])) for r in history})
 for engine,seed in keys:
  rs=[r for r in history if r['engine_id']==engine and str(r['seed'])==seed];x=[int(r['epoch']) for r in rs];label=engine+'/'+seed
  axes[0].plot(x,[float(r['train_loss']) for r in rs],label=label+' train',alpha=.7);axes[0].plot(x,[float(r['development_model_loss']) for r in rs],ls='--',label=label+' dev',alpha=.7)
  axes[1].plot(x,[float(r['development_model_dice']) for r in rs],label=label+' dev')
  if all(r.get('train_dice') not in [None,''] for r in rs):axes[1].plot(x,[float(r['train_dice']) for r in rs],ls='--',label=label+' train (augmented)')
  last=rs[-1]
  if str(last.get('early_stop')).lower()=='true':axes[1].scatter(x[-1],float(last['development_model_dice']),marker='x',color='black',zorder=4)
 for ax in axes:ax.set_xlabel('Completed epoch');ax.legend(fontsize=6)
 axes[0].set_ylabel('Valid-pixel common loss');axes[1].set_ylabel('Positive-image operational Dice');axes[1].set_ylim(0,1);fig.suptitle('Seed histories · dashed = development loss · × = early stop')
 finish_figure(fig,path,synthetic)

def figure_reliability(calibrations,path,synthetic=False):
 plt=plot_setup();require(calibrations,'No temperature diagnostics');fig,axes=plt.subplots(1,2,figsize=(10,4.5))
 for engine,c in calibrations.items():
  for key,ls in [('reliability_before','--'),('reliability_after','-')]:
   d=c[key];bs=[r for r in d['bins'] if r['count']];axes[0].plot([r['mean_probability'] for r in bs],[r['foreground_frequency'] for r in bs],ls,marker='o',ms=3,label=f"{engine} {'T=1' if key.endswith('before') else 'scaled'}; ECE={d['image_balanced_ECE']:.3f}")
  bs=c['reliability_after']['bins'];axes[1].plot([r['bin'] for r in bs],[r['count'] for r in bs],label=engine+'; n='+str(c['reliability_after']['n_images']))
 axes[0].plot([0,1],[0,1],':',color='gray');axes[0].set(xlabel='Mean foreground probability',ylabel='Observed foreground frequency',xlim=(0,1),ylim=(0,1));axes[1].set(xlabel='Probability bin (15 equal bins)',ylabel='Valid-pixel count');axes[1].set_yscale('symlog',linthresh=1)
 for ax in axes:ax.legend(fontsize=7)
 fig.suptitle('Development-probability reliability · image-balanced ECE · no risk guarantee');finish_figure(fig,path,synthetic)

def figure_tradeoff(rows,path,synthetic=False):
 plt=plot_setup();fig,ax=plt.subplots(figsize=(7,5))
 for r in rows:
  if r['member_id']=='ensemble' and r['op_iou'] is not None and r['hard_negative_false_valid_rate'] is not None:
   ax.scatter(r['hard_negative_false_valid_rate'],r['op_iou'],s=65);ax.annotate(f"{r['engine_id']}\nn+={r['n_positive']}, nHN={r['n_hard_negative']}",(r['hard_negative_false_valid_rate'],r['op_iou']),xytext=(6,5),textcoords='offset points',fontsize=8)
 ax.axvline(.35,color='#d55e00',ls='--',label='HN limit .35');ax.axhline(.56,color='#0072b2',ls='--',label='IoU floor .56');ax.set(xlabel='Hard-negative false-valid-component rate',ylabel='Positive-unit operational IoU',xlim=(0,1),ylim=(0,1),title='Development-policy feasibility gates');ax.legend(fontsize=8);finish_figure(fig,path,synthetic)

def figure_efficiency(rows,path,synthetic=False):
 plt=plot_setup();require(rows,'Measured efficiency absent');fig,axes=plt.subplots(1,3,figsize=(11,4.5))
 for ax,key,scale,title in zip(axes,['median_latency_ms','inference_images_per_second','peak_gpu_bytes'],[1,1,1/1024**3],['Median latency (ms/image)','Throughput (images/s)','Peak allocated GPU memory (GiB)']):
  present=[r for r in rows if r.get(key) is not None]
  if present:ax.bar(range(len(present)),[r[key]*scale for r in present],color='#0072b2');ax.set_xticks(range(len(present)),[r['engine_id'] for r in present],rotation=25,ha='right',fontsize=8)
  else:ax.text(.5,.5,'NOT MEASURED',ha='center',transform=ax.transAxes)
  ax.set_title(title,fontsize=10)
 fig.suptitle('Batch1 M3 inference · '+', '.join(sorted({str(r.get('hardware')) for r in rows}))+' · synchronized timing');finish_figure(fig,path,synthetic)

def figure_examples(examples,path,synthetic=False,title='Fixed-ID development examples'):
 plt=plot_setup();require(examples,'No approved examples');fig,axes=plt.subplots(len(examples),5,figsize=(12,2.5*len(examples)),squeeze=False)
 for row,e in enumerate(examples):
  require(synthetic or e.get('redistribution_permitted') is True,'Source dissemination permission required')
  for col,(label,a,cmap) in enumerate([('RGB',e['rgb'],None),('Adjudicated GT',e['truth'],'gray'),('Mean probability',e['probability'],'viridis'),('Raw ≥.55',e['raw'],'gray'),('Operational',e['op'],'gray')]):
   axes[row,col].imshow(a,cmap=cmap,vmin=0 if cmap else None,vmax=1 if cmap else None);axes[row,col].set_axis_off()
   if row==0:axes[row,col].set_title(label)
  axes[row,0].text(0,-.08,e['sample_id'],transform=axes[row,0].transAxes,fontsize=7)
 fig.suptitle(title+' · aligned 448-grid');finish_figure(fig,path,synthetic)

def render_figures(ctx):
 run=ctx['run'];figure_workflow(run/'figures'/'Fig03_00_workflow.png')
 ctx['figure_rows']=[{'filename':'Fig03_00_workflow.png','purpose':'methodological workflow','data_source':'Blueprint 3.3 sections6/12','role':'METHODOLOGY','code_sha256':ctx['identity']['code_sha256'],'config_sha256':ctx['identity']['config_sha256'],'synthetic':False,'caption':'Methodology only; no empirical result or authorization.','status':'GENERATED'}]
 outputs={}
 if ctx['training_authorized'] and ctx['summaries']:
  funcs=[(FIGURE_NAMES[0],lambda p:figure_engine_comparison(ctx['summaries'],p)),(FIGURE_NAMES[2],lambda p:figure_reliability(ctx['calibrations'],p)),(FIGURE_NAMES[3],lambda p:figure_tradeoff(ctx['summaries'],p)),(FIGURE_NAMES[4],lambda p:figure_efficiency(ctx.get('efficiency',[]),p))]
  eligible=all(r['status']=='EVALUATED' for r in ctx['summaries'] if r['member_id']=='ensemble')
  for name,fn in funcs:
   if name in {FIGURE_NAMES[0],FIGURE_NAMES[3]} and not eligible:continue
   fn(run/'figures'/name);outputs[name]='GENERATED'
 histories=[]
 if ctx['training_authorized']:
  for p in (run/'training_history').glob('*.csv'):histories.extend(cread(p))
 if histories:figure_training(histories,run/'figures'/FIGURE_NAMES[1]);outputs[FIGURE_NAMES[1]]='GENERATED'
 if ctx.get('policy_cache') and ctx['cfg']['figure_examples']:
  # Fixed lexical IDs before consulting predictions; source-specific redistribution review bound to exact samples.
  import numpy as np
  engine=sorted(ctx['policy_cache'])[0];cache=ctx['policy_cache'][engine];ds=cache['dataset'];allowed=set(ctx['plan'].get('redistribution_approved_sample_ids',[]));examples=[]
  selected=sorted(range(len(ds)),key=lambda i:ds.rows[i]['sample_id'])[:3]
  for i in selected:
   r=ds.rows[i]
   if r['sample_id'] not in allowed:continue
   rgb,y,v=ds.native(i)
   with np.load(cache['files'][i],allow_pickle=False) as d:prob=ensemble_probability(d['logits'],ctx['calibrations'][engine]['T'])
   op,_=ctx['p02module'].valid_prediction_components(prob,v);examples.append({'sample_id':r['sample_id'],'rgb':rgb,'truth':y,'probability':prob,'raw':(prob>=.55)&v,'op':op,'redistribution_permitted':True})
  if examples:figure_examples(examples,run/'figures'/FIGURE_NAMES[5]);outputs[FIGURE_NAMES[5]]='GENERATED'
  # Failure rule is fixed, then sorted by sample ID; never rank visually appealing mistakes.
  failures={r['sample_id'] for r in cache['rows'] if (r['is_positive'] and r['op_iou']<.56) or (not r['is_positive'] and r['false_valid'])}
  failure_examples=[e for e in examples if e['sample_id'] in failures]
  if failure_examples:figure_examples(failure_examples,run/'figures'/FIGURE_NAMES[6],title='Fixed-rule failures among fixed-ID examples');outputs[FIGURE_NAMES[6]]='GENERATED'
 for name in FIGURE_NAMES:
  ctx['figure_rows'].append({'filename':name,'purpose':name[9:-4].replace('_',' '),'data_source':'per_seed_metrics/; training_history/; probability_calibration.json; efficiency_preliminary.csv; approved prediction_index','role':'development only','code_sha256':ctx['identity']['code_sha256'],'config_sha256':ctx['identity']['config_sha256'],'synthetic':False,'caption':'Descriptive development evidence; no certification. Example selection: first three lexical sample IDs, source permission required.','status':outputs.get(name,'NOT_GENERATED_BLOCKED' if not ctx['training_authorized'] else 'NOT_GENERATED_NO_DATA_OR_PERMISSION')})
 cwrite(run/'figures'/'figures_manifest.csv',ctx['figure_rows'],list(ctx['figure_rows'][0]));return {'scientific_figures':len(outputs),'methodology':1,'synthetic_figures':'separate synthetic_test_figures/'}

REGISTRY_COLUMNS=['engine_id','recipe_id','seed','checkpoint_ref','SHA256','train_development_hashes','config_sha256','plan_sha256','code_sha256','environment_sha256','load_test_pass','complete','pretraining_provenance','identity_json','best_development_model_dice','parameters','peak_gpu_bytes','training_images_per_second','micro_batch','learning_rate']
PRED_COLUMNS=['sample_id','unit_id','engine_id','member_id','checkpoint_hash','preproc_T_filter_hash','prediction_shard_ref','prediction_sha256','inference_dtype','score_version_hash','role','creation_time','temperature']
SUMMARY_COLUMNS=['engine_id','member_id','population','n_positive','n_hard_negative','unit_ids_sha256','status','raw_dice','raw_iou','raw_cldice','op_dice','op_iou','op_cldice','hard_negative_false_valid_rate','ci_status']+[m+'_ci_'+b for m in ['raw_dice','raw_iou','raw_cldice','op_dice','op_iou','op_cldice'] for b in ['low','high']]

def initialize_outputs(ctx):
 run=ctx['run'];pending={'status':'BLOCKED','reason':'Real approved training/development results absent','risk_certification_performed':False}
 for name in ['probability_calibration.json','primary_engine_selection.json','primary_ensemble_manifest.json','ensemble_smoke_test.json','training_plan_frozen.json']:jwrite(run/name,pending)
 jwrite(run/'input_verification.json',{'status':'MISSING','reason':'No private control bytes verified yet; public repository is implementation context only'})
 jwrite(run/'configs'/'preprocessing.json',PREPROCESS);jwrite(run/'configs'/'operational_filter.json',FILTER)
 jwrite(run/'configs'/'protocol.json',{'loss':'0.5 mean-image valid-pixel BCEWithLogits +0.5 mean-image softDice; epsilon1e-6','seeds':SEEDS,'recipe':'clean reconstruction; RECIPE_UNRECOVERED for exact legacy MRC','blueprint_sha256':BLUEPRINT_SHA,'source_commit':GIT_COMMIT})
 cwrite(run/'figures'/'figures_manifest.csv',[{'filename':name,'status':'NOT_GENERATED_BLOCKED','synthetic':False,'caption':'Approved real results absent'} for name in ['Fig03_00_workflow.png']+FIGURE_NAMES],['filename','purpose','data_source','role','code_sha256','config_sha256','synthetic','caption','status'])
 cwrite(run/'checkpoint_registry.csv',[],REGISTRY_COLUMNS)
 for name in ['baseline_summary.csv','topology_summary.csv','hard_negative_dev_summary.csv']:cwrite(run/name,[],SUMMARY_COLUMNS)
 cwrite(run/'efficiency_preliminary.csv',[],['engine_id','median_latency_ms','inference_images_per_second','peak_gpu_bytes','hardware'])
 try:
  import pandas as pd;pd.DataFrame(columns=PRED_COLUMNS).to_parquet(run/'prediction_index.parquet',index=False)
 except ImportError as e:jwrite(run/'prediction_index_BLOCKED.json',{'status':'MISSING_DEPENDENCY','reason':str(e)})


def synthetic_tests(ctx):
 import numpy as np,torch
 from PIL import Image
 torch.set_num_threads(ctx['cfg']['cpu_threads']);seed_all(42);results=[];folder=ctx['run']/'synthetic_test_figures';testdir=ctx['run']/'synthetic_tests';testdir.mkdir(exist_ok=True)
 def check(name,ok):
  results.append({'name':name,'status':'PASS' if ok else 'FAIL','scope':'SYNTHETIC FUNCTIONAL ONLY'});require(ok,'Synthetic test failed: '+name)
 rgb=np.zeros((20,40,3),np.uint8);gt=np.zeros((20,40),np.uint8);gt[10,5:35]=1;x,y,v,meta=letterbox(rgb,gt)
 check('448_letterbox_valid_padding',x.shape==(448,448,3) and v.sum()==224*448 and meta['top']==112 and y[~v].sum()==0)
 logits=torch.zeros(2,1,448,448,requires_grad=True);target=torch.zeros_like(logits);valid=torch.from_numpy(np.stack([v,v])[:,None]);loss=common_loss(logits,target,valid);loss.backward()
 check('empty_negative_loss_finite_gradient',torch.isfinite(loss).item() and torch.isfinite(logits.grad).all().item() and logits.grad[~valid].abs().sum().item()==0)
 for name,z,t,w in [('shape',logits[:,:,:2,:],target,valid),('nonfinite',torch.full_like(logits,float('nan')),target,valid),('empty_valid',logits,target,torch.zeros_like(valid))]:
  try:common_loss(z,t,w);passed=False
  except Blocked:passed=True
  check('loss_reject_'+name,passed)
 p=np.zeros((40,40));vv=np.ones_like(p,bool);p[2,2:22]=.55;op,n=valid_prediction_components(p,vv);check('component_area20_skeleton20_threshold055',n==1 and op.sum()==20)
 p[2,21]=0;check('component_area19_rejected',valid_prediction_components(p,vv)[1]==0)
 p[:]=0;p[2,2:12]=.55;p[3,12:22]=.55;check('diagonal_8_connectivity',connected_components(p>=.55)[1]==1 and valid_prediction_components(p,vv)[1]==1)
 p[:]=0;p[2:7,2:7]=.8;check('area25_short_skeleton_rejected',p.astype(bool).sum()==25 and skeleton(p>0).sum()<5 and valid_prediction_components(p,vv)[1]==0)
 thin=np.zeros((20,20),bool);thin[2,2:5]=True;check('GT_not_pruned_cldice',cldice(thin,thin)==1 and cldice(np.zeros_like(thin),thin)==0 and cldice(~thin,thin)==0)
 model=torch.nn.Conv2d(3,1,1);opt=torch.optim.AdamW(model.parameters(),lr=1e-4);tx=torch.randn(2,3,32,32);ty=torch.zeros(2,1,32,32);tv=torch.ones_like(ty,dtype=torch.bool)
 for _ in range(2):opt.zero_grad();ls=common_loss(model(tx),ty,tv);ls.backward();opt.step()
 identity={'scope':'SYNTHETIC_ADAPTER_ONLY','seed':42};state={'identity':identity,'model':model.state_dict(),'optimizer':opt.state_dict(),'rng':rng_state(),'epoch':0,'cursor':2,'order':[0,1,2,3],'scaler':{},'scheduler':{},'generator_state':torch.Generator().manual_seed(42).get_state()}
 path=testdir/'synthetic_adapter.pt';save_checkpoint(path,state);loaded=load_checkpoint(path,identity);clone=torch.nn.Conv2d(3,1,1);clone.load_state_dict(loaded['model']);check('synthetic_adapter_checkpoint_reload',torch.equal(model(tx),clone(tx)))
 try:load_checkpoint(path,{'scope':'WRONG'});ok=False
 except Blocked:ok=True
 check('resume_identity_rejected',ok);restore_rng(state['rng']);a=torch.rand(3);restore_rng(loaded['rng']);b=torch.rand(3);check('resume_rng_exact',torch.equal(a,b))
 z=np.stack([np.full((8,8),-1.),np.zeros((8,8)),np.ones((8,8))]);yy=np.zeros((8,8));vvv=np.ones((8,8),bool);cal=fit_temperature(lambda:iter([(z,yy,vvv)]));check('bounded_ensemble_temperature',.05<=cal['T']<=20 and np.allclose(ensemble_probability(z,1),.5))
 # Plot fixtures are deliberately fictitious and never enter scientific summary files.
 fixture=[]
 for i,eng in enumerate(['SYNTHETIC_A','SYNTHETIC_B','SYNTHETIC_C']):
  rr=[]
  for j in range(4):rr.append({'sample_id':'SYNTHETIC_'+str(j),'unit_id':'SYNTHETIC_UNIT_'+str(j),'is_positive':j<3,'false_valid':False,**{m:.6+.05*i for m in ['raw_dice','raw_iou','raw_cldice','op_dice','op_iou','op_cldice']}})
  fixture.append(summarize_metrics(rr,eng,'ensemble',{'SYNTHETIC_3'}))
 eff=[{'engine_id':r['engine_id'],'median_latency_ms':i+1.,'inference_images_per_second':1000/(i+1),'peak_gpu_bytes':(i+1)*1024**3,'hardware':'SYNTHETIC HARDWARE VALUE'} for i,r in enumerate(fixture)]
 check('engine_selection_tie_protocol',choose_engine(fixture,eff)=='SYNTHETIC_C')
 figure_engine_comparison(fixture,folder/FIGURE_NAMES[0],True)
 hist=[{'engine_id':'SYNTHETIC','seed':s,'epoch':e,'train_loss':1/e,'development_model_loss':1.1/e,'development_model_dice':.3+.1*e,'train_dice':.4+.1*e,'early_stop':e==3} for s in SEEDS for e in range(1,4)];figure_training(hist,folder/FIGURE_NAMES[1],True)
 cache=testdir/'synthetic_logits.npz';np.savez_compressed(cache,logits=z,truth=yy,valid=vvv);rel=reliability([cache],1.);cc={'SYNTHETIC':{**cal,'reliability_before':rel,'reliability_after':rel}};figure_reliability(cc,folder/FIGURE_NAMES[2],True);figure_tradeoff(fixture,folder/FIGURE_NAMES[3],True);figure_efficiency(eff,folder/FIGURE_NAMES[4],True)
 prob=np.zeros((448,448));prob[220,100:300]=.8;op,_=valid_prediction_components(prob,v);example={'sample_id':'SYNTHETIC_ONLY','rgb':x,'truth':y,'probability':prob,'raw':prob>=.55,'op':op}
 figure_examples([example],folder/FIGURE_NAMES[5],True);figure_examples([example],folder/FIGURE_NAMES[6],True,'Synthetic failure plot function test')
 for name in FIGURE_NAMES:
  with Image.open(folder/name) as im:check('valid_png_'+name,im.format=='PNG' and min(im.size)>600 and im.info.get('dpi',(0,))[0]>299)
 jwrite(ctx['run']/'synthetic_test_report.json',{'status':'PASS','tests':results,'engineering_optimizer_steps':2,'candidate_model_training':False,'synthetic_model':'single 1x1 Conv2d; never in scientific roster','real_metrics_generated':False,'canonical_primitive_source_sha256':CANONICAL_PRIMITIVES_SHA})
 return {'tests_passed':len(results),'real_training':False}

EXCLUDED_PARTS={'.verified_inputs','__pycache__','.ipynb_checkpoints','curator','snapshots'}
def exportable_files(run):
 result=[]
 for p in Path(run).rglob('*'):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(run)
  if any(x in EXCLUDED_PARTS or x.startswith('.') for x in rel.parts):continue
  if p.name.endswith(('.tmp','.sqlite','.sqlite-wal','.sqlite-shm','.pyc')):continue
  require(not any(x in {'sealed_labels.parquet','calibration.csv','internal_test.csv','external_positive_test.csv','hard_negative_test.csv','reserve_pool.csv','corruption_test.csv','source_unlabeled_pool.csv','target_unlabeled_pool.csv'} for x in rel.parts),'Forbidden export payload')
  require(not any(k in p.name.lower() for k in ['credential','secret','token.json']),'Potential secret cannot be exported')
  result.append(p)
 return sorted(result)

def zip_paths(target,root,paths,extra=None):
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.tmp');extra=extra or {}
 with zipfile.ZipFile(tmp,'w',allowZip64=True) as z:
  for p in sorted(paths):
   name=p.relative_to(root).as_posix();info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED if p.suffix.lower() in {'.pt','.pth','.zip','.npz','.png','.jpg','.parquet'} else zipfile.ZIP_DEFLATED
   with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:shutil.copyfileobj(src,dst,8*1024**2)
  for name,data in sorted(extra.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
 if target.exists():
  require(sha(tmp)==sha(target),'Existing immutable archive differs; never overwrite it');tmp.unlink()
 else:tmp.replace(target)
 return target

def verify_export(path,expected):
 with zipfile.ZipFile(path) as z:
  require(z.testzip() is None,'Export CRC failure');names=z.namelist();require(set(names)==set(expected) and len(names)==len(set(names)),'Export inventory mismatch')
  for name,entry in expected.items():
   with z.open(name) as f:require(stream_sha(f)==entry['sha256'],'Export payload hash mismatch: '+name)
   require(z.getinfo(name).file_size==entry['byte_size'],'Export payload size mismatch')
 return {'verified_sha256':sha(path),'members':len(expected),'bytes':Path(path).stat().st_size}

def finalize_run(ctx):
 run=ctx['run'];require(not(run/'SEALED.json').exists(),'Run already sealed; rerun only final ALL_OUTPUTS cell')
 cwrite(run/'checkpoint_registry.csv',ctx['registry'],REGISTRY_COLUMNS)
 for name in ['baseline_summary.csv','topology_summary.csv','hard_negative_dev_summary.csv']:cwrite(run/name,ctx['summaries'],SUMMARY_COLUMNS)
 if ctx.get('efficiency'):cwrite(run/'efficiency_preliminary.csv',ctx['efficiency'],list(ctx['efficiency'][0]))
 import pandas as pd
 pd.DataFrame(ctx['pred_index'],columns=PRED_COLUMNS).to_parquet(run/'prediction_index.parquet',index=False)
 cwrite(run/'data_access_log.csv',ctx['access'],['utc','last_utc','read_count','path','role','operation']);jwrite(run/'stage_errors.json',ctx['errors']);cwrite(run/'decision_gates.csv',[{'phase':'03','requirement':g.get('reason'),'evidence_ref':'stages/'+g['gate_id']+'.json','verifier':'SOFTWARE_VALIDATION; no generated human approval','failure_action':'BLOCK real use; resolve evidence/dependency and review a new run',**g} for g in ctx['gates']],['gate_id','phase','requirement','evidence_ref','verifier','status','reason','failure_action','signed_at','amendment_ref'])
 if ctx['errors']:
  ctx['scientific_status']='BLOCKED';ctx['training_authorized']=False
  for name in ['primary_engine_selection.json','primary_ensemble_manifest.json','ensemble_smoke_test.json']:
   prior=jread(run/name);prior.update(status='BLOCKED',phase04_authorized=False,reason='Unresolved stage error; inspect stage_errors.json');jwrite(run/name,prior)
 status={'schema_version':'1.0','phase':'03','run_id':ctx['run_id'],'execution_status':ctx['execution_status'],'scientific_status':ctx['scientific_status'],'status':ctx['scientific_status'],'run_mode':ctx['cfg']['RUN_MODE'],'job':ctx['cfg']['JOB'],'training_authorized':bool(ctx['training_authorized'] and ctx['cfg']['RUN_MODE']=='FULL'),'real_training_performed':bool(ctx['registry'] and ctx['cfg']['JOB']=='train'),'test_or_calibration_labels_opened':False,'phase04_authorized':ctx['scientific_status']=='PASS','finished_utc':utc(),'budget_stopped':ctx.get('budget_stopped',False),'actual_upstream_integrity':set(ctx['controls'])=={'phase01','phase02'},'source_contract_commit':GIT_COMMIT}
 jwrite(run/'phase_status.json',status)
 jwrite(run/'stages'/'control_export.json',{'stage':'control_export','status':'COMPLETED','description':'Manifest/control generated below; final export verification occurs in last cell'})
 handoff=f'''# Phase03 handoff — {ctx['run_id']}

Scientific status: **{ctx['scientific_status']}**. Execution: **{ctx['execution_status']}**.
Phase04 authorization: **{'YES — selected development engine only' if status['phase04_authorized'] else 'NO — no qualified frozen primary ensemble'}**.
No calibration/test access, formal risk certification, human signature or model permission is created here.

Retain this exact Kaggle Save Version output privately. Record its version URL/ID plus manifest and ZIP hashes; a local write is not persistence. Import a later job with the saved run directory and phase03_manifest.json SHA256 in CONFIG.job_inputs. The selected deployment ensemble always contains seeds42/123/2026 only. Nonselected and optional individual seeds stay archived.

Logical Phase04 inputs, only after all gates pass:
1. Original Phase01 control {P01_RUN}, SHA256 {P01_SHA}.
2. Verified Phase02 control {ctx['controls'].get('phase02',{}).get('run_id',P02_RUN)}, SHA256 {ctx['controls'].get('phase02',{}).get('sha256',P02_SHA)}.
3. This Phase03 small control + matching .zip.sha256, selected three checkpoints pinned by registry hashes, exact inference source/dependencies, frozen T/preprocessing/filter and approved development prediction shards referenced by prediction_index.parquet.
4. Reuse existing extracted abarman79/wall-crack-cp-datasets; do not re-upload raw data. Keep held-out/curator labels absent.

If Kaggle extracts a control ZIP on upload, rename an unchanged byte-for-byte copy to .zip.bin and retain the canonical .zip.sha256 naming .zip. Never reconstruct a ZIP from extracted members. ALL_OUTPUTS is a convenience archive; extract its Phase03 control pair for downstream use. It is not itself a Phase03 control ZIP.

Only completed sealed jobs are ensemble-eligible. A budget-stop export is an interrupted snapshot; reattach its entire run directory in writable working storage and use resume_run_dir. Resume checks code/config/input/plan/environment, optimizer/scheduler/scaler/RNG/order/cursor. Unsaved partial work is replayed from the last durable optimizer boundary. Each new snapshot gets a content suffix; existing archives remain immutable.

The full archive contains private approved development prediction/label-derived caches and any actual model weights; do not publish it automatically. Only separately reviewed figures may be disseminated. Small controls exclude those caches, weights and source images. GitHub suggestions: notebook, phase03_core.py, sanitized guide/validation report/README only; no private controls or raw images. No GitHub write occurs.
'''
 twrite(run/'NEXT_PHASE_INPUTS.md',handoff)
 tables={}
 for p in run.rglob('*.csv'):
  if not any(x in EXCLUDED_PARTS for x in p.relative_to(run).parts):
   with p.open(newline='') as f:rr=csv.reader(f);header=next(rr);n=sum(1 for _ in rr)
   tables[p.relative_to(run).as_posix()]={'columns':header,'rows':n,'null':'empty CSV field; never unknown-to-zero'}
 jwrite(run/'schemas.json',{'schema_version':'1.0','tables':tables,'prediction_index_columns':PRED_COLUMNS,'empty_tables_reason':'BLOCKED/NOT_RUN uses schema-correct empty tables, never fabricated measurements','topology_scope':'clDice + component counts only; full branch/LWBR work is Phase04','JSON':'RFC8259; null, no NaN'})
 excluded={'phase03_manifest.json','phase03_manifest.sha256','artifact_catalog.json','SHA256SUMS.sha256','SEALED.json','bundle_verification.json'}
 files=[p for p in exportable_files(run) if p.name not in excluded and not p.name.startswith('CrackSAFE_CP_v3.3_phase03_control_')]
 def entry(p):
  rel=p.relative_to(run).as_posix();private=rel.startswith(('checkpoints/','predictions/','synthetic_tests/','synthetic_test_figures/')) or ('Fig03_06' in rel or 'Fig03_07' in rel)
  return {'artifact_id':digest(rel.encode())[:20],'relative_path':rel,'sha256':sha(p),'byte_size':p.stat().st_size,'media_type':mimetypes.guess_type(p.name)[0] or 'application/octet-stream','schema_version':'1.0','producing_run_id':ctx['run_id'],'required_by':['04'],'privacy/license_status':'PRIVATE_RESEARCH_ONLY' if private else 'REVIEW_BEFORE_PUBLICATION','bundled':not private}
 entries=[entry(p) for p in files];jwrite(run/'artifact_catalog.json',{'schema_version':'1.0','run_id':ctx['run_id'],'artifacts':entries,'resolution':'Match relative paths + actual bytes; dataset slugs are user-supplied mounts','self_exclusions':sorted(excluded),'unbundled_payloads':'checkpoints, prediction/label-derived shards, synthetic fixtures, example images'})
 entries.append(entry(run/'artifact_catalog.json'))
 manifest={'schema_version':'1.0','blueprint_version':'3.3','blueprint_sha256':BLUEPRINT_SHA,'phase':'03','run_id':ctx['run_id'],'created_utc':ctx['identity']['created_utc'],'status':ctx['scientific_status'],'scope':'MSc/Q1 clean development baselines; no certification','config_sha256':ctx['identity']['config_sha256'],'code_sha256':ctx['identity']['code_sha256'],'git_commit':None,'source_contract_commit':GIT_COMMIT,'code_hash_method':'SHA256 of exact phase03_core.py UTF-8 bytes; notebook embeds this identical source','seeds':SEEDS,'input_artifacts':[{'artifact_id':k,**v} for k,v in ctx['controls'].items()],'output_artifacts':entries,'gate_results':ctx['gates'],'amendment_ids':[],'environment_file':'environment_snapshot.json','access_log_file':'data_access_log.csv','phase04_authorized':status['phase04_authorized']}
 jwrite(run/'phase03_manifest.json',manifest);mh=sha(run/'phase03_manifest.json');twrite(run/'phase03_manifest.sha256',mh+'  phase03_manifest.json\n')
 control=[run/e['relative_path'] for e in entries if e['bundled']]+[run/'phase03_manifest.json',run/'phase03_manifest.sha256']
 twrite(run/'SHA256SUMS.sha256',''.join(sha(p)+'  '+p.relative_to(run).as_posix()+'\n' for p in sorted(control)));control.append(run/'SHA256SUMS.sha256')
 suffix=ctx['run_id']+('_checkpoint_'+mh[:8] if ctx.get('budget_stopped') else '')
 bundle=run/f'CrackSAFE_CP_v3.3_phase03_control_{suffix}.zip';zip_paths(bundle,run,control);verified=verify_export(bundle,{p.relative_to(run).as_posix():{'sha256':sha(p),'byte_size':p.stat().st_size} for p in control});twrite(str(bundle)+'.sha256',verified['verified_sha256']+'  '+bundle.name+'\n')
 jwrite(run/'bundle_verification.json',{'status':'PASS',**verified,'control_filename':bundle.name})
 if not ctx.get('budget_stopped'):jwrite(run/'SEALED.json',{'run_id':ctx['run_id'],'manifest_sha256':mh,'sealed_at':utc(),'scientific_status':ctx['scientific_status']})
 ctx['control_bundle']=bundle;print('Phase03:',status['execution_status'],status['scientific_status']);return {'control_bundle':str(bundle),'manifest_sha256':mh,**status}

def export_all_outputs(ctx):
 run=ctx['run'];require((run/'phase03_manifest.json').is_file(),'Run finalization must succeed before full export')
 root=Path(ctx['cfg']['export_root']);root.mkdir(parents=True,exist_ok=True);files=exportable_files(run)
 # A full export is a snapshot; no modifications to original run files occur in this function.
 rows=[{'relative_path':p.relative_to(run).as_posix(),'byte_size':p.stat().st_size,'sha256':sha(p)} for p in files]
 total=sum(r['byte_size'] for r in rows);free=shutil.disk_usage(root).free;reserve=ctx['cfg']['storage_reserve_bytes'];quota=ctx['cfg']['max_saved_output_bytes']
 # Conservative upper bound for archive overhead. No assumption that already-compressed checkpoints compress again.
 needed=total+max(1024**2,len(rows)*512);quota_files={p.resolve() for base in {root,run} for p in base.rglob('*') if p.is_file() and not p.is_symlink() and not p.name.endswith('.tmp')}
 usage=sum(p.stat().st_size for p in quota_files)
 manifest_sha=sha(run/'phase03_manifest.json');snapshot=ctx['run_id'] if (run/'SEALED.json').exists() else ctx['run_id']+'_checkpoint_'+manifest_sha[:8]
 full_target=root/f'CrackSAFE_CP_Phase03_ALL_OUTPUTS_{snapshot}.zip'
 full_ok=full_target.exists() or (free>=needed+reserve and usage+needed<=quota)
 report={'run_id':ctx['run_id'],'snapshot':snapshot,'available_disk_bytes':free,'payload_bytes':total,'estimated_archive_upper_bytes':needed,'configured_saved_output_ceiling_bytes':quota,'measured_existing_output_bytes':usage,'quota_source':'CONFIG conservative ceiling; account quota not queryable','status':'FULL' if full_ok else 'FULL_ZIP_BLOCKED_STORAGE','payload_inventory_sha256':digest(jb(rows))}
 extra={};target=full_target
 if not full_ok:
  # Every excluded large file remains separately pinned; never call this a complete archive.
  excluded=[r for r in rows if r['relative_path'].startswith(('checkpoints/','predictions/','synthetic_tests/'))]
  report['separate_required_parts']=[{**r,'absolute_local_path':str((run/r['relative_path']).resolve()),'fetch':'Save this Kaggle output version; download exact relative file and verify SHA256. Preserve original run directory for resume.'} for r in excluded]
  blocked=root/f'FULL_ZIP_BLOCKED_STORAGE_{snapshot}.json'
  if blocked.exists():
   prior=jread(blocked);require(prior['payload_inventory_sha256']==report['payload_inventory_sha256'],'Existing storage snapshot differs');report=prior
  else:jwrite(blocked,report)
  skip={r['relative_path'] for r in excluded};files=[p for p in files if p.relative_to(run).as_posix() not in skip];rows=[r for r in rows if r['relative_path'] not in skip]
  target=root/f'CrackSAFE_CP_Phase03_COMPACT_OUTPUTS_{snapshot}.zip';extra['FULL_ZIP_BLOCKED_STORAGE.json']=jb(report)
  compact_need=sum(r['byte_size'] for r in rows)+1024**2
  if not target.exists() and (free<compact_need+reserve or usage+compact_need>quota):
   return {**report,'compact_status':'ALSO_BLOCKED_STORAGE','download_paths':[str(blocked),str(ctx.get('control_bundle',run/'phase03_manifest.json'))]}
 index={'schema_version':'1.0','run_id':ctx['run_id'],'status':report['status'],'files':rows,'index_self_hash_policy':'Index CSV/JSON are verified by exporter and outer ZIP hash; excluded from their own recursive payload listing','exclusions':'raw inputs; private upstream controls; sealed/curator labels; caches/temp; other runs; ZIP itself','all_exportable_current_run_files_included':bool(full_ok)}
 extra['all_outputs_index.json']=jb(index);out=io.StringIO();w=csv.DictWriter(out,fieldnames=['relative_path','byte_size','sha256']);w.writeheader();w.writerows(rows);extra['all_outputs_index.csv']=out.getvalue().encode()
 expected={r['relative_path']:{'sha256':r['sha256'],'byte_size':r['byte_size']} for r in rows};expected.update({n:{'sha256':digest(b),'byte_size':len(b)} for n,b in extra.items()})
 if target.exists():verified=verify_export(target,expected)
 else:zip_paths(target,run,files,extra);verified=verify_export(target,expected)
 side=Path(str(target)+'.sha256');body=verified['verified_sha256']+'  '+target.name+'\n'
 if side.exists():require(side.read_text()==body,'Existing outer sidecar differs')
 else:twrite(side,body)
 result={**report,**verified,'archive_path':str(target.resolve()),'download_paths':[str(target.resolve()),str(side.resolve())]}
 if not full_ok:result['download_paths'].append(str(blocked.resolve()))
 print('Verified archive:',target.resolve(),'members:',verified['members'],'bytes:',verified['bytes'],'SHA256:',verified['verified_sha256']);return result
