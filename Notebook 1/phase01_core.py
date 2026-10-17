"""CrackSAFE-CP Phase01 core v1.0.0; planning and provenance only."""
import csv, dataclasses, datetime as dt, hashlib, importlib.metadata, io, json, math
import os, platform, random, re, shutil, stat, subprocess, sys, time, urllib.request
import zipfile, zlib, base64, mimetypes, traceback
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict

BLUEPRINT_VERSION = '3.3'
SCHEMA_VERSION = '1.0'
CORE_VERSION = '1.0.0'
DELTA = 0.05
DELTA_CELL = DELTA / 26
SEEDS = [42, 123, 2026]
POLICY_PAIRS = [(1.,1.),(.95,1.),(.95,.95),(.90,.95),(.90,.90),(.85,.90),(.85,.85),(.80,.85),(.80,.80),(.75,.80),(.75,.75),(.70,.75),(.70,.70)]
EXPECTED_ARCHIVES = ['CRACK500, CrackTree200, GAPS384.zip','CrackForest dataset(CFD).zip','DeepCrack.zip','SDNET2018.zip','crack segmentation dataset.zip']
GATE_STATUSES = {'PASS','BLOCKED','PENDING_APPROVAL','NOT_RUN','NOT_APPLICABLE'}

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()

def json_bytes(obj):
    return (json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()

def atomic_bytes(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)

def write_json(path,obj): atomic_bytes(path,json_bytes(obj))
def write_text(path,s): atomic_bytes(path,s.encode('utf-8'))

def write_csv(path,rows,fields):
    out=io.StringIO(newline=''); w=csv.DictWriter(out,fieldnames=fields,extrasaction='raise')
    w.writeheader()
    for r in rows: w.writerow({k:('' if r.get(k) is None else r.get(k)) for k in fields})
    write_text(path,out.getvalue())

# %% Exact binomial helpers

def _validate_counts(e,n,delta_cell):
    if isinstance(e,bool) or isinstance(n,bool) or not isinstance(e,int) or not isinstance(n,int): raise ValueError('e and n must be integers')
    if n<0 or e<0 or e>n or not 0<delta_cell<1: raise ValueError('Require 0 <= e <= n and 0 < delta < 1')

def binomial_cdf(e,n,p):
    """Log-sum exact-binomial CDF, used only by dependency-free fallback inversion."""
    if p<=0: return 1.0
    if p>=1: return float(e==n)
    terms=[math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)+k*math.log(p)+(n-k)*math.log1p(-p) for k in range(e+1)]
    m=max(terms)
    return min(1.0,math.exp(m)*math.fsum(math.exp(v-m) for v in terms))

def cp_upper(e,n,delta_cell=DELTA_CELL,backend='auto'):
    """One-sided Clopper-Pearson UCB; n=0 returns conservative computational 1."""
    _validate_counts(e,n,delta_cell)
    if n==0 or e==n: return 1.0
    if e==0: return -math.expm1(math.log(delta_cell)/n)
    if backend=='auto':
        try:
            from scipy.stats import beta
            return float(beta.ppf(1-delta_cell,e+1,n-e))
        except ImportError: pass
    elif backend!='bisect': raise ValueError('backend must be auto or bisect')
    lo,hi=0.,1.
    for _ in range(90):
        mid=(lo+hi)/2
        if binomial_cdf(e,n,mid)>delta_cell: lo=mid
        else: hi=mid
    return (lo+hi)/2

def minimum_n(alpha,errors=0,delta_cell=DELTA_CELL):
    if not 0<alpha<1 or errors<0 or not isinstance(errors,int): raise ValueError('Invalid planning inputs')
    if errors==0: return math.ceil(math.log(delta_cell)/math.log1p(-alpha))
    lo=errors; hi=max(errors+1,minimum_n(alpha,0,delta_cell))
    while cp_upper(errors,hi,delta_cell)>alpha: hi*=2
    while hi-lo>1:
        mid=(hi+lo)//2
        if cp_upper(errors,mid,delta_cell)<=alpha: hi=mid
        else: lo=mid
    return hi

def risk_cell(errors,accepted_n,alpha):
    _validate_counts(errors,accepted_n,DELTA_CELL)
    if accepted_n==0: return {'errors':0,'accepted_n':0,'risk':None,'ucb':None,'computational_ucb':1.,'status':'NOT_CERTIFIABLE','reason':'ZERO_ACCEPTED'}
    u=cp_upper(errors,accepted_n)
    status=('NOT_CERTIFIABLE_INSUFFICIENT_N' if accepted_n<minimum_n(alpha) else 'PASS' if u<=alpha else 'FAILS_TARGET')
    return {'errors':errors,'accepted_n':accepted_n,'risk':errors/accepted_n,'ucb':u,'computational_ucb':u,'status':status,'reason':None}

def select_policy(planning_rows):
    """Testable pure helper, NOT invoked on real calibration observations in Phase01."""
    passing=[]
    for r in planning_rows:
        if r['policy_id'] not in [f'lambda{i:02d}' for i in range(13)]: raise ValueError('Unknown/non-null policy required')
        if not 0<=r['coverage']<=1: raise ValueError('Invalid coverage')
        if risk_cell(r['miss_e'],r['positive_n'],.10)['status']=='PASS' and risk_cell(r['false_e'],r['negative_n'],.05)['status']=='PASS': passing.append(r)
    if not passing: return {'policy_id':'lambda13','coverage':0.,'risk_miss':None,'risk_false':None,'status':'REVIEW_ALL'}
    r=sorted(passing,key=lambda r:(-r['coverage'],r['policy_id']))[0]
    return {'policy_id':r['policy_id'],'coverage':r['coverage'],'status':'BOTH_RISKS_PASS'}

def statistical_self_tests():
    checks=[]
    def check(name,ok):
        if not ok: raise AssertionError(name)
        checks.append({'test':name,'status':'PASS','evidence_kind':'SYNTHETIC_MATH_ONLY'})
    check('26 bounds and Bonferroni budget',len(POLICY_PAIRS)*2==26 and abs(26*DELTA_CELL-.05)<1e-15)
    check('zero-failure minima',minimum_n(.10)==60 and minimum_n(.05)==122)
    check('80 negatives do not certify 5 percent',abs(cp_upper(0,80)-.07519544910976639)<1e-10 and cp_upper(0,80)>.05)
    check('boundary e=n and n=0',cp_upper(4,4)==1 and cp_upper(0,0)==1)
    check('zero denominator not risk zero',risk_cell(0,0,.05)['risk'] is None and risk_cell(0,0,.05)['status']=='NOT_CERTIFIABLE')
    check('small n retains UCB',risk_cell(0,80,.05)['status']=='NOT_CERTIFIABLE_INSUFFICIENT_N')
    for e,expected in [(1,(82,167)),(2,(101,205)),(5,(150,306))]:
        check(f'minima errors={e}',(minimum_n(.10,e),minimum_n(.05,e))==expected)
    for e,n in [(1,122),(2,205),(5,306),(119,120)]: check(f'independent inversion {e}/{n}',abs(cp_upper(e,n)-cp_upper(e,n,backend='bisect'))<1e-9)
    check('sentinel undefined risks',select_policy([])['risk_miss'] is None)
    rows=[{'policy_id':p,'coverage':.6,'miss_e':0,'positive_n':120,'false_e':0,'negative_n':122} for p in ['lambda02','lambda01']]
    check('coverage tie by ID',select_policy(rows)['policy_id']=='lambda01')
    rows[0].update(coverage=.9,false_e=20)
    check('both risks required',select_policy(rows)['policy_id']=='lambda01')
    for args in [(-1,5),(6,5),(1.2,5),(True,5)]:
        try: cp_upper(*args)
        except ValueError: check(f'reject invalid {args}',True)
        else: raise AssertionError('invalid counts accepted')
    return checks

# %% Configuration and environment
@dataclasses.dataclass
class Phase01Config:
    run_mode: str='SMOKE'
    input_root: str='/kaggle/input'
    output_root: str='/kaggle/working/cracksafe_cp'
    raw_dataset_hint: str='wall-crack-cp-datasets'
    raw_roots: list=dataclasses.field(default_factory=list)
    resume_run_dir: object=None
    network_checks: bool=False
    run_model_smoke: bool=False
    model_smoke_ids: list=dataclasses.field(default_factory=list)
    smoke_device: str='cpu'
    smoke_size: int=448
    smoke_timeout_seconds: int=600
    max_archive_members: int=1000000
    max_central_directory_mb: int=256
    max_member_mb: int=512
    max_compression_ratio: int=1000
    max_legacy_mb: int=32
    legacy_paths: list=dataclasses.field(default_factory=list)
    legacy_split_manifests: list=dataclasses.field(default_factory=list)
    repository_paths: dict=dataclasses.field(default_factory=dict)
    model_permission_evidence: dict=dataclasses.field(default_factory=dict)
    model_pins: dict=dataclasses.field(default_factory=dict)
    field_evidence_path: object=None
    session_limit_hours: object=None
    session_export_buffer_minutes: int=30
    scope: str='MSC'
    seed: int=42

    def validate(self):
        if self.run_mode not in {'SMOKE','FULL'}: raise ValueError('run_mode must be SMOKE or FULL')
        if self.scope not in {'MSC','Q1'}: raise ValueError('scope must be MSC or Q1')
        if self.smoke_device not in {'cpu','cuda'}: raise ValueError('smoke_device must be cpu or cuda')
        for k in ['smoke_timeout_seconds','max_archive_members','max_central_directory_mb','max_member_mb','max_compression_ratio','max_legacy_mb','session_export_buffer_minutes']:
            if not isinstance(getattr(self,k),int) or getattr(self,k)<=0: raise ValueError(f'{k} must be positive integer')
        if not isinstance(self.smoke_size,int) or self.smoke_size<32 or self.smoke_size%32: raise ValueError('smoke_size must be a multiple of 32, >=32')
        for k in ['network_checks','run_model_smoke']:
            if not isinstance(getattr(self,k),bool): raise ValueError(f'{k} must be boolean')
        for k in ['raw_roots','legacy_paths','legacy_split_manifests','model_smoke_ids']:
            if not isinstance(getattr(self,k),list) or not all(isinstance(x,str) for x in getattr(self,k)): raise ValueError(f'{k} must be a list of strings')
        for k in ['repository_paths','model_permission_evidence','model_pins']:
            if not isinstance(getattr(self,k),dict): raise ValueError(f'{k} must be an object')
        if self.session_limit_hours is not None and (self.session_limit_hours<=0 or self.session_limit_hours*60<=self.session_export_buffer_minutes): raise ValueError('Session limit must exceed export buffer')
        inp,out=Path(self.input_root).resolve(),Path(self.output_root).resolve()
        if out==inp or inp in out.parents: raise ValueError('Outputs must never be under the read-only input root')
        if out==Path('/kaggle/input') or Path('/kaggle/input') in out.parents: raise ValueError('Refusing to write under /kaggle/input')
        return self

def command_result(args,cwd=None,timeout=15):
    try:
        p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout,check=False)
        return {'returncode':p.returncode,'stdout':p.stdout[:20000],'stderr':p.stderr[:2000]}
    except (OSError,subprocess.TimeoutExpired) as e: return {'returncode':None,'stdout':None,'stderr':str(e)}

def environment_snapshot(root):
    packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata.get('Name')}
    mem={}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key,val=line.split(':',1)
            if key in {'MemTotal','MemAvailable'}: mem[key+'_bytes']=int(val.split()[0])*1024
    except OSError: pass
    disk=shutil.disk_usage(root)
    git=command_result(['git','rev-parse','HEAD'])
    return {'captured_utc':utcnow(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'cpu_count':os.cpu_count(),'ram':mem or None,'disk':{'total_bytes':disk.total,'free_bytes':disk.free,'used_bytes':disk.used},'packages':dict(sorted(packages.items())),'gpu':command_result(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader']),'git_commit':git['stdout'].strip() if git['returncode']==0 and re.fullmatch('[0-9a-f]{40}\\s*',git['stdout'] or '') else None,'cuda_version':command_result(['nvcc','--version']),'kaggle_detected':Path('/kaggle').exists(),'hardware_scope':'THIS_RUNTIME_ONLY'}

def allowed_input(cfg,path):
    p=Path(path).resolve(); root=Path(cfg.input_root).resolve()
    if not p.is_file() or not (p==root or root in p.parents): raise ValueError(f'Not an existing file in input_root: {path}')
    return p

def access(ctx,path,operation,role='metadata_only',note=None):
    if role not in {'metadata_only','legacy_development_manifest','official_documentation','permission_evidence'}: raise ValueError('Phase01 data-access role prohibited')
    ctx['access'].append({'timestamp_utc':utcnow(),'phase':'01','path':str(path),'operation':operation,'allowed_role':role,'status':'RECORDED','note':note})

def missing(ctx,item,reason,blocks,action):
    ctx['missing'].append({'item':item,'status':'MISSING_INPUT','reason':reason,'blocks':blocks,'required_action':action})

def init_run(config,blueprint_bytes,core_source,workflow_source):
    cfg=Phase01Config(**config).validate()
    root=Path(cfg.output_root).resolve(); root.mkdir(parents=True,exist_ok=True)
    hashed_config=dataclasses.asdict(cfg); hashed_config.pop('resume_run_dir')
    ch=hashlib.sha256(json_bytes(hashed_config)).hexdigest()
    code_hash=hashlib.sha256((core_source+'\n'+workflow_source).encode()).hexdigest()
    if cfg.resume_run_dir:
        run=Path(cfg.resume_run_dir).resolve()
        if root not in run.parents: raise ValueError('Resume path must be under output_root')
        if (run/'SEALED.json').exists(): raise ValueError('Finalized run is immutable; start a new run')
        prior=json.loads((run/'run_identity.json').read_text())
        if prior['config_sha256']!=ch or prior['code_sha256']!=code_hash: raise ValueError('Resume config/code mismatch; start new run')
        run_id=prior['run_id']; started=prior['created_utc']
    else:
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        run_id=f'{stamp}_{ch[:8]}'; run=root/'phase01'/('run_'+run_id); run.mkdir(parents=True,exist_ok=False); started=utcnow()
    ctx={'cfg':cfg,'run':run,'run_id':run_id,'created_utc':started,'config_sha256':ch,'code_sha256':code_hash,'blueprint_sha256':hashlib.sha256(blueprint_bytes).hexdigest(),'access':[],'missing':[],'errors':[],'input_artifacts':[]}
    random.seed(cfg.seed)
    try:
        import numpy as np
        np.random.seed(cfg.seed)
    except ImportError: pass
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    write_json(run/'run_identity.json',{k:ctx[k] for k in ['run_id','created_utc','config_sha256','code_sha256','blueprint_sha256']})
    write_json(run/'config.json',{'schema_version':SCHEMA_VERSION,**hashed_config})
    atomic_bytes(run/'blueprint_v3.3.md',blueprint_bytes)
    write_text(run/'phase01_core.py',core_source);write_text(run/'workflow_source.json',workflow_source)
    ctx['env']=environment_snapshot(run);write_json(run/'environment_snapshot.json',ctx['env'])
    write_json(run/'phase_status.json',{'phase':'01','status':'BLOCKED','reason':'RUN_IN_PROGRESS','run_mode':cfg.run_mode,'phase02_audit_ready':False})
    print('Run directory:',run,'\nMode:',cfg.run_mode,'— SMOKE is never a completed research run.')
    return ctx

# %% Safe archive inventory

def zip_preflight(path,cfg):
    """Read EOCD/ZIP64 metadata before ZipFile allocates the central directory."""
    import struct
    size=path.stat().st_size
    with path.open('rb') as f:
        f.seek(max(0,size-65557)); tail=f.read(65557); pos=tail.rfind(b'PK\x05\x06')
        if pos<0: raise ValueError('ZIP end-of-central-directory absent')
        eocd=struct.unpack_from('<4s4H2IH',tail,pos)
        if eocd[1]!=0 or eocd[2]!=0: raise ValueError('Multi-disk ZIP unsupported')
        entries,cd_size=eocd[4],eocd[5]
        if entries==65535 or cd_size==0xffffffff:
            absolute=max(0,size-65557)+pos
            f.seek(absolute-20); locator=f.read(20)
            if locator[:4]!=b'PK\x06\x07': raise ValueError('ZIP64 locator missing')
            _,disk,offset,disks=struct.unpack('<4sIQI',locator)
            if disk!=0 or disks!=1: raise ValueError('Multi-disk ZIP64 unsupported')
            f.seek(offset); z64=f.read(56)
            values=struct.unpack('<4sQ2H2I4Q',z64)
            if values[0]!=b'PK\x06\x06': raise ValueError('ZIP64 record invalid')
            entries,cd_size=values[7],values[8]
        if entries>cfg.max_archive_members or cd_size>cfg.max_central_directory_mb*1024**2: raise ValueError('Central directory exceeds configured safe metadata limits')
    return entries,cd_size

def member_warnings(info,cfg):
    name=getattr(info,'orig_filename',info.filename); normalized=name.replace('\\','/')
    parts=PurePosixPath(normalized).parts; flags=[]
    if '\\' in name: flags.append('NON_POSIX_PATH')
    if '\x00' in name or normalized.startswith('/') or re.match(r'^[A-Za-z]:',normalized) or '..' in parts: flags.append('UNSAFE_PATH')
    if stat.S_ISLNK(info.external_attr>>16): flags.append('SYMLINK')
    if info.flag_bits&1: flags.append('ENCRYPTED')
    if info.compress_type not in {zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED,zipfile.ZIP_BZIP2,zipfile.ZIP_LZMA}: flags.append('UNSUPPORTED_COMPRESSION')
    if info.file_size>cfg.max_member_mb*1024**2: flags.append('OVERSIZED_MEMBER')
    if info.file_size/max(1,info.compress_size)>cfg.max_compression_ratio: flags.append('SUSPICIOUS_COMPRESSION_RATIO')
    return flags

def discover_raw_roots(cfg):
    root=Path(cfg.input_root).resolve()
    if not root.exists(): return [],'INPUT_ROOT_MISSING'
    if cfg.raw_roots:
        paths=[Path(p).resolve() for p in cfg.raw_roots]
        if any(not p.is_dir() or not (p==root or root in p.parents) for p in paths): raise ValueError('raw_roots must be mounted directories under input_root')
        return paths,'EXPLICIT'
    roots=[p for p in root.iterdir() if p.is_dir() and cfg.raw_dataset_hint.casefold() in p.name.casefold()]
    if roots:return sorted(roots),'HINT_MATCH'
    known=[]
    for p in root.rglob('*'):
        if p.is_file() and p.name.casefold() in {n.casefold() for n in EXPECTED_ARCHIVES}: known.append(p.parent)
    return sorted(set(known)),'EXPECTED_ARCHIVE_MATCH' if known else 'RAW_DATASET_NOT_FOUND'

def inventory_archives(ctx):
    cfg,run=ctx['cfg'],ctx['run']; roots,discovery=discover_raw_roots(cfg)
    archives=sorted({p.resolve() for root in roots for p in root.rglob('*') if p.is_file() and p.suffix.casefold()=='.zip'})
    archive_rows=[]; overlaps=defaultdict(set); patterns=Counter(); warnings=[]
    members_path=run/'archive_members.csv'; tmp=members_path.with_suffix('.csv.tmp')
    member_fields=['archive_id','member_index','member_name','file_size','compressed_size','crc32','is_directory','image_extension','mask_name_hint','source_family_hint','warnings','payload_integrity']
    with tmp.open('w',newline='',encoding='utf-8') as out:
        writer=csv.DictWriter(out,fieldnames=member_fields);writer.writeheader()
        for index,path in enumerate(archives):
            aid=f'raw_archive_{index:03d}'; size=path.stat().st_size
            row={'archive_id':aid,'name':path.name,'path':str(path),'sha256':None,'hash_status':'NOT_RUN_SMOKE','bytes':size,'members':None,'images_by_extension':None,'mask_name_hints':None,'uncompressed_bytes':None,'compressed_member_bytes':None,'warnings':None,'status':'BLOCKED','integrity_scope':'CENTRAL_DIRECTORY_ONLY; no payload CRC/decode test'}
            if cfg.run_mode=='FULL':
                try: row['sha256']=ctx.get('input_hash_cache',{}).get(str(path)) or sha256_file(path);row['hash_status']='PASS';access(ctx,path,'stream_sha256')
                except OSError as e:row['hash_status']='BLOCKED';row['warnings']=str(e)
            access(ctx,path,'zip_central_directory_inventory')
            try:
                zip_preflight(path,cfg)
                with zipfile.ZipFile(path) as z:
                    infos=z.infolist(); counts=Counter(i.filename for i in infos); image_n=mask_n=uncompressed=compressed=0; warn_n=0
                    for mi,info in enumerate(infos):
                        flags=member_warnings(info,cfg)
                        if counts[info.filename]>1: flags.append('DUPLICATE_MEMBER_NAME')
                        name=info.filename; suffix=PurePosixPath(name).suffix.casefold()
                        is_img=suffix in {'.jpg','.jpeg','.png','.bmp','.tif','.tiff','.webp'}
                        mask_hint=bool(re.search(r'(^|[/_\-])(masks?|labels?|ground.?truth|gt)([/_\-\.]|$)',name,re.I))
                        source=next((s for s in ['crack500','cracktree','gaps384','cfd','crackforest','deepcrack','sdnet','riss','aigle','esarc','tut'] if s in name.casefold()),'UNKNOWN')
                        image_n+=int(is_img); mask_n+=int(is_img and mask_hint);uncompressed+=info.file_size;compressed+=info.compress_size
                        if flags:warn_n+=1;warnings.append({'archive_id':aid,'member_index':mi,'member_name':name,'warning':';'.join(flags),'action':'QUARANTINE_MEMBER; Phase02 review before extraction'})
                        writer.writerow(dict(zip(member_fields,[aid,mi,name,info.file_size,info.compress_size,f'{info.CRC:08x}',info.is_dir(),suffix if is_img else '',mask_hint,source,';'.join(flags),'NOT_TESTED'])))
                        if is_img and not flags:
                            overlaps[(PurePosixPath(name).name.casefold(),info.file_size,info.CRC)].add(aid)
                            patterns[(aid,source,'mask_hint' if mask_hint else 'image_or_unknown')]+=1
                    row.update(members=len(infos),images_by_extension=image_n,mask_name_hints=mask_n,uncompressed_bytes=uncompressed,compressed_member_bytes=compressed,warnings=warn_n,status='PASS' if warn_n==0 else 'BLOCKED')
            except (OSError,ValueError,zipfile.BadZipFile,NotImplementedError,RuntimeError) as e:
                row['warnings']=f'{type(e).__name__}: {e}';warnings.append({'archive_id':aid,'member_index':None,'member_name':None,'warning':str(e),'action':'REATTACH_OR_REBUILD_ARCHIVE'})
            archive_rows.append(row)
            ctx['input_artifacts'].append({'artifact_id':aid,'path':str(path),'sha256':row['sha256'],'byte_size':size,'hash_status':row['hash_status'],'role':'raw_archive_metadata_only'})
    tmp.replace(members_path)
    expected=[]
    found={p.name.casefold():str(p) for p in archives}
    for name in EXPECTED_ARCHIVES:
        present=name.casefold() in found
        expected.append({'expected_name':name,'status':'FOUND' if present else 'MISSING_OR_RENAMED','discovered_path':found.get(name.casefold()),'note':'Exact name is a hint; inventory all discovered ZIPs'})
        if not present:missing(ctx,name,'Expected archive name not found; may be renamed','Source completeness assessment in Phase02','Inspect archive_inventory.csv and actual mounts')
    if not archives:missing(ctx,'raw dataset','No applicable ZIP archives discovered','Phase02 audit execution','Attach abarman79/wall-crack-cp-datasets or set raw_roots')
    write_csv(run/'archive_inventory.csv',archive_rows,list(archive_rows[0]) if archive_rows else ['archive_id','name','path','sha256','hash_status','bytes','members','images_by_extension','mask_name_hints','uncompressed_bytes','compressed_member_bytes','warnings','status','integrity_scope'])
    write_csv(run/'archive_warnings.csv',warnings,['archive_id','member_index','member_name','warning','action'])
    write_csv(run/'archive_expectations.csv',expected,['expected_name','status','discovered_path','note'])
    write_csv(run/'source_pattern_inventory.csv',[{'archive_id':k[0],'source_family_hint':k[1],'naming_role':k[2],'member_count':v} for k,v in sorted(patterns.items())],['archive_id','source_family_hint','naming_role','member_count'])
    overlap_rows=[{'basename':k[0],'file_size':k[1],'crc32':f'{k[2]:08x}','archive_ids':';'.join(sorted(v)),'evidence':'WEAK_METADATA_CANDIDATE_NOT_DEDUPLICATION'} for k,v in overlaps.items() if len(v)>1]
    write_csv(run/'archive_overlap_candidates.csv',overlap_rows,['basename','file_size','crc32','archive_ids','evidence'])
    ctx['archives']=archive_rows;ctx['raw_roots']=[str(p) for p in roots]
    write_json(run/'dataset_discovery.json',{'dataset_reference':'abarman79/wall-crack-cp-datasets','roots':ctx['raw_roots'],'method':discovery,'historical_pairs_expected_unverified':11298,'historical_source_groups_expected_unverified':11,'unique_pair_count':None,'independent_calibration_unit_count':None,'integrity_scope':'Central directory plus archive SHA in FULL; no payload CRC/decode verification','raw_archives_not_extracted':True})
    print('Discovered ZIPs:',len(archives),'| metadata warnings:',len(warnings),'| no images extracted or evaluated.')

# %% Historical evidence and preliminary lineage
LEGACY_FACTS = {
 'evidence_level':'HISTORICAL_REFERENCE_NOT_REPRODUCED',
 'phase12':{'population_n':1356,'crack_IoU':0.581844,'crack_Dice':0.722288,'no_crack_false_positive_rate':0.045977,'temperature':1.556495,'mask_threshold':0.55},
 'phase14A':{'population_n':1695,'crack_IoU':0.582254,'crack_Dice':0.722671,'no_crack_false_positive_count':5,'no_crack_n':218,'no_crack_false_positive_rate':0.022936,'classification_precision':0.996626,'classification_recall':1.0,'classification_specificity':0.977064,'classification_F1':0.998310,'TP':1477,'FP':5,'TN':213,'FN':0,'Boundary_IoU':0.343042,'clDice':0.793017},
 'historical_split_counts_unverified':{'train':9603,'validation':1695,'combined':11298},
 'external_claim_unverified':'Up to 72.9 percent decline; motivational historical statement only; dataset/metric basis not independently reproduced'
}

def legacy_inventory(ctx):
    cfg,run=ctx['cfg'],ctx['run']; root=Path(cfg.input_root)
    candidates=set()
    if root.exists():
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.csv','.json','.yaml','.yml','.toml','.pt','.pth','.ckpt','.h5','.hdf5','.ipynb','.md','.txt'} and re.search(r'(mrc|legacy)',str(p),re.I): candidates.add(p.resolve())
    for p in cfg.legacy_paths+cfg.legacy_split_manifests:
        try:candidates.add(allowed_input(cfg,p))
        except ValueError as e:missing(ctx,p,str(e),'Original legacy reproduction','Attach actual historical evidence')
    rows=[]; hashes=[]; lineage_inputs=[]
    for p in sorted(candidates):
        try:
            allowed_input(cfg,p)
            if re.search(r'(^|[/_\-])(final.?test|internal.?test|external.?test)([/_\-.]|$)',str(p),re.I):
                rows.append({'path':str(p),'kind':'SEALED_TEST_RECORD','sha256':None,'byte_size':p.stat().st_size,'status':'NOT_OPENED_PHASE01','applicability':'NOT_APPLICABLE'});continue
            ext=p.suffix.lower(); kind='checkpoint' if ext in {'.pt','.pth','.ckpt','.h5','.hdf5'} else 'split_manifest' if ext=='.csv' and re.search(r'train|val|split',p.name,re.I) else 'metrics' if re.search(r'metric|result|eval',p.name,re.I) else 'configuration' if ext in {'.json','.yaml','.yml','.toml'} else 'other_record'
            digest=sha256_file(p);access(ctx,p,'legacy_stream_hash')
            explicit=str(p) in {str(Path(x).resolve()) for x in cfg.legacy_split_manifests}
            applicable=kind=='split_manifest' and (explicit or (re.search(r'mrc|legacy',str(p),re.I) and re.search(r'train|val',p.name,re.I)))
            row={'path':str(p),'kind':kind,'sha256':digest,'byte_size':p.stat().st_size,'status':'FOUND_HASHED_NOT_AUTHENTICATED','applicability':'DECLARED_LEGACY_TRAIN_VALIDATION' if applicable else 'CANDIDATE_REQUIRES_REVIEW'}
            rows.append(row);hashes.append(f'{digest}  {p}')
            ctx['input_artifacts'].append({'artifact_id':'legacy_'+digest[:16],'path':str(p),'sha256':digest,'byte_size':p.stat().st_size,'role':kind})
            if applicable:lineage_inputs.append(p)
        except (OSError,ValueError) as e:missing(ctx,str(p),str(e),'Legacy evidence','Restore readable original file')
    for kind in ['split_manifest','checkpoint','configuration','metrics']:
        if not any(r['kind']==kind for r in rows):missing(ctx,'legacy_'+kind,'No original evidence found','Frozen checkpoint / exact recipe reconstruction only','Attach actual file later; historical-only reporting remains allowed')
    ctx['legacy']=rows;ctx['lineage_inputs']=lineage_inputs
    write_json(run/'legacy_manifest.json',{'schema_version':SCHEMA_VERSION,'historical_facts':LEGACY_FACTS,'found_records':rows,'evidence_categories':{'historical_reference':'AVAILABLE_FROM_BLUEPRINT_NOT_REPRODUCED','frozen_checkpoint_evaluation':'NOT_RUN; requires authenticated checkpoint + configuration + original splits','clean_retraining':'NOT_RUN; Phase03 after Phase02 grouped audit'},'checkpoint_deserialization_performed':False})
    write_text(run/'legacy_hashes.sha256','\n'.join(hashes)+'\n' if hashes else '# MISSING_INPUT: no original legacy files available to hash. No fake hash entries.\n')
    write_text(run/'legacy_baseline_record.md','# Historical MRC reference — not a Phase01 result\n\nThe 1,356-case Phase12 and 1,695-case Phase14A populations must remain separate. These figures are inherited from v3.3, not measured here.\n\n```json\n'+json.dumps(LEGACY_FACTS,indent=2)+'\n```\n\nFound files: '+str(len(rows))+'. A discovered filename and checksum do not authenticate its relationship to the historical experiment. No checkpoint was loaded, evaluated or trained. Frozen-checkpoint evaluation and clean retraining are separate Phase03 evidence tracks. Missing original files do not prove absence of historical leakage.\n')

def lineage_keys(row,image_ref):
    stem=PurePosixPath(image_ref.replace('\\','/')).stem.casefold()
    source=row.get('source_id') or row.get('source') or 'UNKNOWN'
    keys={'filename':PurePosixPath(image_ref.replace('\\','/')).name.casefold(),'stem':stem}
    parent=row.get('parent_id') or row.get('original_id') or row.get('parent_image_id')
    if parent:keys['explicit_parent']=source+'::'+parent.casefold()
    stripped=re.sub(r'([_\-](?:crop|patch|tile)[_\-]?\d+.*)$','',stem)
    if stripped!=stem:keys['crop_parent_hint']=source+'::'+stripped
    numeric=re.match(r'^(\d+)',stem)
    if numeric:keys['numeric_stem_hint']=source+'::'+numeric.group(1)
    prefix=re.sub(r'[_\-]\d+(?:[_\-]\d+)*$','',stem)
    if prefix!=stem and len(prefix)>=3:keys['prefix_hint']=source+'::'+prefix
    return keys,source

def preliminary_lineage(ctx):
    run,cfg=ctx['run'],ctx['cfg']; groups=defaultdict(lambda:{'train':[],'validation':[]}); files=[]; invalid=[]
    for path in ctx.get('lineage_inputs',[]):
        path=Path(path)
        file_groups=defaultdict(lambda:{'train':[],'validation':[]})
        try:
            if path.stat().st_size>cfg.max_legacy_mb*1024**2:raise ValueError('Manifest exceeds bounded Phase01 CSV read; review in Phase02')
            default_role='train' if re.search(r'train',path.name,re.I) else 'validation' if re.search(r'val',path.name,re.I) else None
            with path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f);headers=reader.fieldnames or []
                image_column=next((k for k in ['image_ref','image_path','filename','file_name','image','path'] if k in headers),None)
                if not image_column:raise ValueError('No recognized image reference column: expected image_ref/image_path/filename/file_name/image/path')
                n=0
                for row in reader:
                    role=(row.get('role') or row.get('split') or default_role or '').casefold()
                    role={'training':'train','val':'validation','valid':'validation','dev':'validation'}.get(role,role)
                    if role not in {'train','validation'}:raise ValueError('Mixed or unknown split roles; no final-test labels are consumed in Phase01')
                    image=row.get(image_column,'')
                    if not image:raise ValueError('Empty image reference')
                    keys,source=lineage_keys(row,image);n+=1
                    for method,key in keys.items():file_groups[(method,key)][role].append({'file':str(path),'row':n+1,'image':image,'source':source})
            for key,roles in file_groups.items():
                for role,values in roles.items():groups[key][role].extend(values)
            files.append({'path':str(path),'rows':n,'schema_status':'PASS'});access(ctx,path,'parse_train_validation_identifier_columns','legacy_development_manifest','Labels ignored; naming candidates only')
        except (OSError,ValueError,csv.Error,UnicodeError) as e:invalid.append({'path':str(path),'error':str(e)})
    rows=[]
    for (method,key),g in sorted(groups.items()):
        if g['train'] and g['validation']:
            a,b=g['train'],g['validation']
            rows.append({'candidate_id':'lin_'+hashlib.sha256((method+key).encode()).hexdigest()[:16],'method':method,'key':key,'train_count':len(a),'validation_count':len(b),'train_examples':json.dumps(a[:3]),'validation_examples':json.dumps(b[:3]),'status':'CANDIDATE_NOT_CONFIRMED','required_action':'Phase02 decoded/exact/perceptual hashes and original-parent adjudication'})
    write_csv(run/'preliminary_lineage_scan.csv',rows,['candidate_id','method','key','train_count','validation_count','train_examples','validation_examples','status','required_action'])
    state='MISSING_INPUT' if not files else 'INCOMPLETE_SCHEMA_ERRORS' if invalid else 'PRELIMINARY_SCAN_ONLY'
    if not files:missing(ctx,'applicable_legacy_train_validation_CSVs','No usable applicable manifests','Legacy lineage conclusion','Attach originals; Phase02 reconstructs grouped lineage from actual data')
    write_text(run/'preliminary_lineage_report.md',f'# Preliminary lineage scan\n\nStatus: **{state}**. Usable manifests: {len(files)}. Candidate groups: {len(rows)}.\n\nNo images were decoded and no leakage-free conclusion is justified. Numeric stems and prefixes are weak evidence, especially when source is UNKNOWN. Full exact/decoded/perceptual duplicate, parent, source, site/session and split-group audit is deferred to Phase02. No artificial splits were created.\n\n```json\n'+json.dumps({'manifests':files,'schema_errors':invalid},indent=2)+'\n```\n')
    ctx['lineage_status']=state

# %% Literature provenance
REFERENCE_YEARS=[2021,2021,1934,2022,2023,2025,2025,2026,2026,2024,2026,2017,2021,2024,2025,2019,2025,2025,2025,2024,2018,None]
REFERENCE_TOPICS={
 'R01':('General risk control','General prediction sets','None central','Risk bounds','High-probability risk control','No primary selective class-conditional topology contract'),
 'R02':('Finite-family risk control','Selective prediction examples','None central','Multiple testing','LTT; multiple risks','Crack-specific endpoints, independent-unit audit and inference-only topology remain project work'),
 'R03':('Exact binomial inference','Binary outcome counts','None','None','One-sided exact interval used here','No segmentation/controller construction'),
 'R04':('Conformal risk control','General bounded losses','None central','Conformal','Version-specific guarantee; not interchangeable with high-probability selective risk','Must not transfer a different theorem to conditional accepted risks'),
 'R05':('Topology uncertainty','Image segmentation','Topology-aware uncertainty','Topology-based','No identical two-risk certificate established','Closest topology-uncertainty overlap; project score is distinct and needs validation'),
 'R06':('Selective crack segmentation','Crack segmentation','Not established from inherited abstract','Selective training/prediction','No identical exact two-risk certificate established','Closest application overlap; avoid novelty claim for selection alone'),
 'R07':('Structure-aware architecture','Crack segmentation','Structure-aware features','Not central','No risk certificate','Engine comparator rather than controller novelty'),
 'R08':('Dual encoder architecture','Crack segmentation','Boundary refinement','Not central','No risk certificate','Conditional comparator; permissions and reproducibility unresolved'),
 'R09':('Topology-aware foundation model','Crack segmentation','Topology-aware SAM','Not established','No identical certificate established','Topology/domain invariance overlap; code and full-text limitations'),
 'R10':('Topology-aware architecture','Crack segmentation','Topology-aware Mamba','Not central','No risk certificate','Keep separate from SCSegamba'),
 'R11':('Crack foundation model','Multi-task crack representation','Topology preservation','Not established','No identical certificate established','Foundation comparator contextual; released weights unverified'),
 'R12':('Ensemble uncertainty','General deep learning','None central','Independent ensembles','No selective two-risk guarantee','Uncertainty baseline; no novelty claim for ensembles'),
 'R13':('Topology loss/metric','Tubular segmentation','clDice topology preservation','Not central','No risk certificate','Topology quality alone is not conditional structural-miss control'),
 'R14':('Conformal segmentation','Semantic segmentation','Not central','Post-hoc uncertainty','Paper-specific conformal guarantee','Different units/losses; no inherited structural certificate'),
 'R15':('False-positive control','Image segmentation','Not established in abstract','Conformal','Abstract-level paper-specific guarantee','False-positive overlap; selective structural unit requires separate proof'),
 'R16':('Covariate shift conformal','General prediction','None central','Weighted conformal','Requires likelihood-ratio assumptions','Estimated-weight diagnostics alone cannot establish theorem assumptions'),
 'R17':('Risk under covariate shift','General risk control','None central','Weighted risk bounds','High-probability; inspect conditional-risk assumptions','Formal shift extension remains optional and qualified'),
 'R18':('Weighted CRC generalization','General prediction','None central','Weighted conformal','Version-specific assumptions','Abstract-level evidence; not an automatic shift guarantee'),
 'R19':('Unsupervised crack domain adaptation','Crack segmentation','Not established','Domain adaptation','No identical selective certificate established','Adaptation differs from certifying accepted structural outcomes'),
 'R20':('Anytime risk control','General prediction','None central','Sequential active calibration','Anytime-valid framework, not adopted','Distinguishes valid sequential methods from invalid repeated fixed-sample retries'),
 'R21':('Dataset provenance','Crack/no-crack crops; not dense masks','No dense topology labels implied','Not applicable','No statistical guarantee','Recover 230-original lineage; crop count is not independent N'),
 'R22':('Execution environment','Notebook infrastructure','Not applicable','Not applicable','No statistical guarantee','Live account quotas and committed outputs must be checked')}

def blueprint_section(ctx,number):
    text=(ctx['run']/'blueprint_v3.3.md').read_text()
    return text.split(f'## {number}. ',1)[1].split('\n## ',1)[0]

def small_http(url,limit=512*1024,timeout=12):
    req=urllib.request.Request(url,headers={'User-Agent':'CrackSAFE-CP-Phase01/1.0 (+research-provenance)'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        data=r.read(limit+1)
        return {'url':url,'final_url':r.url,'http_status':r.status,'checked_utc':utcnow(),'content_type':r.headers.get('Content-Type'),'bytes_retained':min(len(data),limit),'truncated':len(data)>limit,'sha256_retained':hashlib.sha256(data[:limit]).hexdigest()},data[:limit]

def literature_artifacts(ctx):
    run=ctx['run'];register=blueprint_section(ctx,20);rows=[];bib=[];http_checks=[]
    for i,line in enumerate(l for l in register.splitlines() if re.match(r'- \*\*\[R\d{2}\]',l)):
        rid=re.search(r'\[(R\d{2})\]',line).group(1);urls=re.findall(r'\]\((https?://[^)]+)\)',line)
        title_match=re.search(r'(?<!\*)\*([^*]+)\*(?!\*)',line)
        title=title_match.group(1) if title_match else {'R21':'SDNET2018 original dataset and article','R22':'Kaggle Notebooks and efficient GPU usage documentation'}.get(rid,rid)
        year=REFERENCE_YEARS[int(rid[1:])-1];topic=REFERENCE_TOPICS[rid]
        codes=[u for u in urls if 'github.com/' in u]
        if rid=='R11':license_status='MIT reported in inherited review; recheck exact code and weights'
        elif rid=='R07':license_status='Apache-2.0 identified in v3.3; pin and inspect exact license'
        elif rid=='R21':license_status='CC BY 4.0 reported by institutional source; actual archive/source scope not audited'
        else:license_status='NOT_ESTABLISHED_FOR_THIS_RUN; verify code/data/weights separately'
        check={'reference_id':rid,'status':'NOT_RUN','checked_utc':None,'url':urls[0] if urls else None,'reason':'network_checks=False; inherited blueprint review only'}
        if ctx['cfg'].network_checks and urls:
            try:
                response,body=small_http(urls[0]);write_text(run/'reference_checks'/f'{rid}.json',json.dumps(response,indent=2));check.update(status='HTTP_METADATA_RECHECK_ONLY',checked_utc=response['checked_utc'],reason='Reachability/content fingerprint only; no new full-text or scientific verification')
                access(ctx,urls[0],'bounded_http_get','official_documentation')
            except Exception as e:check.update(status='RECHECK_UNAVAILABLE',reason=f'{type(e).__name__}: {e}')
        http_checks.append(check)
        row={'paper_id':rid,'year':year,'venue':'See exact inherited register; no venue inferred','title':title,'task':topic[0],'research_question':topic[0],'segmentation_relevance':topic[1],'datasets':'Source-specific; details require original-paper verification; not asserted from title','dataset_requirements':'For CrackSAFE comparison: independent acquisition units, adjudicated dense positive masks and confirmed negatives; source-paper dataset needs are not inferred','risk_unit':'Paper-specific; not assumed identical to acquisition-unit conditional binary risk','topology':topic[2],'uncertainty':topic[3],'selective_prediction':'Explicit overlap' if rid in {'R02','R06'} else 'Not established as identical selective setting','guarantee_type':topic[4],'class_conditioning':'Project uses two class-conditional accepted risks; source-specific equivalence not asserted','domain_shift':'Central' if rid in {'R09','R16','R17','R18','R19'} else 'Not central or not established','hard_negatives':'Not established from inherited evidence','multi_seed':'Not established from inherited evidence','code_url':';'.join(codes) if codes else 'NOT_ESTABLISHED','license_status':license_status,'evidence_level':'INHERITED_BLUEPRINT_REVIEW','closest_overlap':topic[1]+' / '+topic[2],'remaining_gap':topic[5],'verified_date':'2026-10-15 (inherited v3.3 review)','current_check_status':check['status'],'current_check_utc':check['checked_utc'],'source_url':urls[0] if urls else None,'blueprint_sha256':ctx['blueprint_sha256'],'provenance_note':line.removeprefix('- ')}
        rows.append(row)
        clean=lambda s: str(s).replace('\\','\\textbackslash ').replace('{','(').replace('}',')').replace('&','\\&').replace('%','\\%')
        fields={'title':title,'url':urls[0] if urls else '', 'note':'Identity inherited from blueprint v3.3 reviewed 2026-10-15. Runtime status: '+check['status']+'. Repository execution and permission are separate. Exact source/version must be confirmed before manuscript submission.'}
        if year is not None:fields['year']=str(year)
        prefix=line.split('*',1)[0]
        author_match=re.match(r'- \*\*\[R\d+\]\*\* (.+?) \*',line)
        if author_match:fields['author']=author_match.group(1).rstrip('.').replace(';',' and ')
        doi_match=re.search(r'https://doi.org/([^\)]+)',line)
        if doi_match:fields['doi']=doi_match.group(1)
        bib.append('@misc{CrackSAFE_'+rid+',\n'+',\n'.join('  '+k+' = {'+clean(v)+'}' for k,v in fields.items())+'\n}\n')
    if len(rows)!=22:raise ValueError('Expected the exact 22-item v3.3 reference register')
    write_csv(run/'literature_matrix.csv',rows,list(rows[0]))
    write_csv(run/'reference_rechecks.csv',http_checks,['reference_id','status','checked_utc','url','reason'])
    write_text(run/'verified_references.bib','% Filename follows blueprint contract. Verification provenance is per-entry; not all sources were rechecked at runtime.\n% Conservative @misc entries avoid inventing unverified publication fields.\n\n'+'\n'.join(bib))
    write_text(run/'reference_register_inherited.md','# Inherited v3.3 reference register\n\nSource SHA-256: '+ctx['blueprint_sha256']+'\n\n'+register)
    write_text(run/'novelty_gap.md','# Literature positioning and remaining scientific gap\n\n'+blueprint_section(ctx,2)+'\n\n'+blueprint_section(ctx,3)+'\n\nRuntime verification is limited to reference_rechecks.csv. HTTP success does not establish scientific correctness, repository reproducibility, or legal permission. The reviewed source register is inherited explicitly. No broad new literature redesign was performed.\n')
    ctx['literature_count']=len(rows)

# %% Statistical design and prediction-only locks

def statistics_artifacts(ctx):
    run=ctx['run'];policies=[{'policy_id':f'lambda{i:02d}','tau_topo':a,'tau_base':b,'force_review_all':False} for i,(a,b) in enumerate(POLICY_PAIRS)]
    policies.append({'policy_id':'lambda13','tau_topo':0.,'tau_base':0.,'force_review_all':True})
    design={'schema_version':SCHEMA_VERSION,'blueprint_version':'3.3','design_status':'PROPOSED_PENDING_S1_S2_S3_S4_S7; not an approval','procedure':'Finite-family exact one-sided binomial bounds; LTT-compatible','primary_targets':{'alpha_miss':.10,'alpha_false':.05},'delta_total':DELTA,'delta_cell':DELTA_CELL,'non_null_policy_count':13,'risk_count':2,'simultaneous_bounds':26,'policies':policies,'primary_OOD_rejection_enabled':False,'quality_review_enabled':True,'threshold_equality':'ACCEPT','risk_definitions':{'miss':'P(LWBR < 0.90 | accepted, true crack-positive)','false':'P(N_valid >= 1 | accepted, confirmed no-crack)'},'observation_unit':'One label-blind representative from each independently justified acquisition unit; correlated crops are not independent observations','hard_available_calibration_floor':{'positive':120,'negative':122},'preferred_available_calibration_target':{'positive':300,'negative':300},'zero_failure_accepted_minimum':{'positive':minimum_n(.10),'negative':minimum_n(.05)},'actual_available_independent_units':None,'actual_calibration_outcomes':None,'sample_freeze':'Fixed N and acquisition stopping rule before calibration outcomes; no outcome-triggered reserve additions','upper_bound':'1 when n=0 or e=n; BetaQuantile(1-d;e+1,n-e) otherwise; zero-failure stable -expm1(log(d)/n)','zero_accepted_display':{'risk':None,'ucb':None,'status':'NOT_CERTIFIABLE','computational_ucb':1},'selection':'Both bounds PASS; maximum empirical overall coverage, tie smallest policy ID; else lambda13','review_all':{'policy_id':'lambda13','coverage':0,'risk_miss':None,'risk_false':None,'ucb_miss':None,'ucb_false':None},'conditional_risk_monotonicity_assumed':False,'formal_scope':'P(selected sentinel OR both selected population risks <= targets) >= .95 under stated fixed-system IID class-conditional assumptions','assumptions':['Independent identically distributed observations within class from declared population','Frozen model, preprocess, temperature, scores/CDF, thresholds, endpoints and acceptance rules independently of calibration','Accurate complete adjudicated labels and losses','Single fixed-sample experiment without adaptive retry','Future class-conditionals match calibration population'],'single_policy_alternative':{'status':'NOT_ACTIVATED; S2 before any calibration outcomes only','delta_cell':.025,'zero_failure_min_positive':minimum_n(.1,0,.025),'zero_failure_min_negative':minimum_n(.05,0,.025)},'entropy_comparator':{'family':[1-.025*j for j in range(13)],'non_null_count':13,'separate_confidence_budget':.05,'joint_across_models_or_families':False},'mathematical_signoff_gate':'G07; Phase05 to Phase06; independent technical review not granted here','shift':{'default':'EMPIRICAL_EXTERNAL_ONLY','ESS_fraction_warning':.30,'domain_AUC_warning':.85,'diagnostics_establish_guarantee':False}}
    write_json(run/'statistical_design.json',design)
    checks=statistical_self_tests();write_json(run/'statistical_self_tests.json',{'status':'PASS','evidence_kind':'DETERMINISTIC_SYNTHETIC_MATH_ONLY','checks':checks})
    rows=[]
    for alpha,name in [(.10,'structural_miss'),(.05,'false_structure')]:
        for errors in [0,1,2,5]:
            rows.append({'scenario_type':'MINIMUM_ACCEPTED_N','risk':name,'alpha':alpha,'delta_cell':DELTA_CELL,'available_independent_n':None,'assumed_class_coverage':None,'accepted_n':minimum_n(alpha,errors),'failures':errors,'ucb':cp_upper(errors,minimum_n(alpha,errors)),'status':'PLANNING_MATH_NOT_DATA','minimum_accepted_n':minimum_n(alpha,errors),'reason':'Exact integer search'})
        for available in ([120,300,500] if alpha==.10 else [122,300,500]):
            for coverage in [.25,.5,.75,1.]:
                n=math.floor(available*coverage)
                for errors in [0,1,2,5]:
                    c=risk_cell(errors,n,alpha)
                    rows.append({'scenario_type':'HYPOTHETICAL_FIXED_ACCEPTED_N','risk':name,'alpha':alpha,'delta_cell':DELTA_CELL,'available_independent_n':available,'assumed_class_coverage':coverage,'accepted_n':n,'failures':errors,'ucb':c['ucb'],'status':c['status'],'minimum_accepted_n':minimum_n(alpha,errors),'reason':'Assumed coverage; no dataset sample size or outcome inferred'})
    write_csv(run/'sample_size_feasibility.csv',rows,list(rows[0]))
    power=[]
    for alpha,risk in [(.1,'structural_miss'),(.05,'false_structure')]:
        for n in [60,80,120,122,150,225,300,500]:
            passing=[e for e in range(min(n,math.ceil(n*alpha))+1) if cp_upper(e,n)<=alpha]
            emax=max(passing) if passing else -1
            for p in [0.,.01,.02,.05,.10]:
                power.append({'risk':risk,'accepted_n_fixed':n,'assumed_true_error_rate':p,'maximum_passing_failures':emax,'conditional_pass_probability':0. if emax<0 else binomial_cdf(emax,n,p),'evidence_kind':'HYPOTHETICAL_BINOMIAL_POWER; conditional on accepted_n; not joint policy selection power'})
    write_csv(run/'planning_power.csv',power,list(power[0]))
    write_text(run/'rcps_decision_D2.md','# Decision D2 — exact conditional binomial finite-family procedure\n\nStatus: IMPLEMENTED_FOR_PLANNING; pending human mathematical sign-off G07. No real calibration has run.\n\n'+blueprint_section(ctx,9))
    write_text(run/'prediction_only_topology_design.md','# Deferred topology and shift contracts\n\nImplementation/evaluation in Phases04–05. No GT or unavailable model predictions were used in this notebook.\n\n'+blueprint_section(ctx,7)+'\n\n'+blueprint_section(ctx,8)+'\n\n'+blueprint_section(ctx,10))
    ctx['statistical_tests_pass']=True
    print('26-bound correction:',DELTA_CELL,'| zero-failure accepted minima: 60 positive / 122 negative. No actual calibration performed.')

# %% Repository and model smoke assessment
MODEL_SPECS = [
 {'model_id':'unetpp_effb3','slot':'A','name':'U-Net++ / EfficientNet-B3','repository':'qubvel-org/segmentation_models.pytorch','package':'segmentation-models-pytorch','deps':'torch; torchvision; segmentation-models-pytorch; timm','hours_low':4,'hours_high':12,'fallback':'none; investigate recipe/implementation','role':'PRIMARY'},
 {'model_id':'scsegamba','slot':'B','name':'SCSegamba','repository':'Karl1109/SCSegamba','package':None,'deps':'upstream Python3.10, torch1.13.1/cu116, mmcv-full, mamba-ssm1.2.0, timm, lmdb, mmengine; reconcile current Kaggle separately','hours_low':4,'hours_high':16,'fallback':'segformer_b0','role':'PRIMARY_CONDITIONAL'},
 {'model_id':'dmsrcrack','slot':'C','name':'DMSRCrack','repository':'habeeb96/DMSRCrack','package':None,'deps':'inspect pinned requirements.txt; torch/torchvision DeformConv2d and compatible CUDA','hours_low':6,'hours_high':24,'fallback':'segformer_b0 then unetpp_convnext_tiny if already used','role':'PRIMARY_CONDITIONAL'},
 {'model_id':'segformer_b0','slot':'F1','name':'SegFormer-B0','repository':'huggingface/transformers','package':'transformers','deps':'torch; transformers; random B0 config; no from_pretrained download','hours_low':3,'hours_high':10,'fallback':'unetpp_convnext_tiny','role':'DECLARED_FALLBACK'},
 {'model_id':'unetpp_convnext_tiny','slot':'F2','name':'U-Net++ / ConvNeXt-Tiny','repository':'qubvel-org/segmentation_models.pytorch','package':'segmentation-models-pytorch','deps':'torch; segmentation-models-pytorch; timm; encoder support must actually execute','hours_low':5,'hours_high':18,'fallback':'dated amendment before training if no compatible fallback','role':'DECLARED_FALLBACK'}
]

MODEL_WORKER = r'''import json,sys,time,os,traceback,hashlib,socket,importlib.metadata
from pathlib import Path
spec=json.loads(Path(sys.argv[1]).read_text()); result={'model_id':spec['model_id'],'status':'BLOCKED','evidence_kind':'SYNTHETIC_TENSOR_TECHNICAL_TEST_ONLY'}
try:
    import torch
    torch.manual_seed(42)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(min(4,os.cpu_count() or 1))
    device=torch.device(spec['device'])
    if device.type=='cuda' and not torch.cuda.is_available(): raise RuntimeError('CUDA requested but unavailable')
    # No silent download of pretrained weights. Only a random initialization is tested.
    def no_network(*a,**k): raise RuntimeError('Model worker network disabled: provision and audit weights separately')
    socket.create_connection=no_network; socket.socket.connect=no_network
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    mid=spec['model_id']
    def factory():
        if mid in {'unetpp_effb3','unetpp_convnext_tiny'}:
            import segmentation_models_pytorch as smp
            enc='efficientnet-b3' if mid=='unetpp_effb3' else 'tu-convnext_tiny'
            return smp.UnetPlusPlus(encoder_name=enc,encoder_weights=None,in_channels=3,classes=1,activation=None)
        if mid=='segformer_b0':
            from transformers import SegformerConfig,SegformerForSemanticSegmentation
            config=SegformerConfig(num_channels=3,num_labels=1,depths=[2,2,2,2],hidden_sizes=[32,64,160,256],num_attention_heads=[1,2,5,8],sr_ratios=[8,4,2,1],decoder_hidden_size=256)
            return SegformerForSemanticSegmentation(config)
        repo=spec.get('repo_path')
        if not repo:raise RuntimeError('Attach reviewed official source snapshot and set repository_paths')
        sys.path.insert(0,repo)
        if mid=='dmsrcrack':
            from model import DMSRCrack
            return DMSRCrack(in_channels=3,num_classes=2)
        if mid=='scsegamba':
            from main import get_args_parser
            from models import build_model
            args=get_args_parser().parse_args([])
            args.device=str(device)
            for key in ['resume','pretrained','pretrained_path','checkpoint']:
                if hasattr(args,key):setattr(args,key,'')
            built=build_model(args)
            return built[0] if isinstance(built,tuple) else built
        raise ValueError('Unknown model')
    def tensor_output(out):
        if hasattr(out,'logits'):out=out.logits
        elif isinstance(out,dict):
            keys=[k for k in ['logits','out','pred'] if k in out]
            if len(keys)!=1:raise ValueError('Ambiguous model output mapping; inspect pinned adapter before proceeding')
            out=out[keys[0]]
        elif isinstance(out,(list,tuple)):
            if mid!='dmsrcrack':raise ValueError('Unverified tuple/list contract; inspect official segmentation output')
            out=out[0] # Official DMSRCrack returns (refined segmentation logits, boundary probability).
        if not isinstance(out,torch.Tensor):raise TypeError('Output is not a tensor')
        return out
    start=time.perf_counter();model=factory().to(device);model.train()
    size=spec['size'];x=torch.randn(1,3,size,size,device=device)
    if device.type=='cuda':torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
    raw=tensor_output(model(x));raw_shape=list(raw.shape)
    if raw.ndim!=4 or raw.shape[0]!=1 or raw.shape[1]!=1:raise ValueError('Expected Bx1xHxW segmentation output, got '+str(raw_shape))
    if mid=='segformer_b0':
        output=torch.nn.functional.interpolate(raw,size=(size,size),mode='bilinear',align_corners=False)
    else:
        if tuple(raw.shape[-2:])!=(size,size):raise ValueError('Unexpected spatial shape: no silent resize for this architecture')
        output=raw
    if not torch.isfinite(output).all():raise ValueError('Nonfinite output')
    loss=(output.square().mean()+.01*output.mean());loss.backward()
    grads=[p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
    if not grads or not all(torch.isfinite(g).all() for g in grads) or not any(torch.count_nonzero(g)>0 for g in grads):raise ValueError('Missing/nonfinite/zero gradients')
    # One synthetic step tests mechanics, not the future scientific training loss.
    opt=torch.optim.SGD(model.parameters(),lr=1e-4);opt.step();opt.zero_grad()
    model.eval()
    with torch.no_grad():expected=tensor_output(model(x)).detach().cpu()
    ckpt=Path(spec['checkpoint_path']);torch.save(model.state_dict(),ckpt)
    digest=hashlib.sha256()
    with ckpt.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):digest.update(block)
    result.update(checkpoint_sha256=digest.hexdigest(),checkpoint_bytes=ckpt.stat().st_size)
    del model
    if device.type=='cuda':torch.cuda.empty_cache()
    reloaded=factory().to(device);reloaded.load_state_dict(torch.load(ckpt,map_location=device,weights_only=True));reloaded.eval()
    with torch.no_grad():actual=tensor_output(reloaded(x)).detach().cpu()
    torch.testing.assert_close(actual,expected,rtol=1e-5,atol=1e-6)
    if device.type=='cuda':torch.cuda.synchronize()
    result.update(status='PASS',input_shape=list(x.shape),raw_output_shape=raw_shape,operational_output_shape=list(output.shape),elapsed_seconds=time.perf_counter()-start,parameter_count=sum(p.numel() for p in reloaded.parameters()),peak_cuda_bytes=torch.cuda.max_memory_allocated() if device.type=='cuda' else None,torch_version=torch.__version__,torch_cuda=torch.version.cuda,device=str(device),gradients_checked=len(grads),forward_backward_reload=True,pretrained_weights='NOT_USED_RANDOM_INITIALIZATION',output_semantics='DMSRCrack first output logits; SegFormer/SMP logits; SCSegamba semantics require pinned-source review',throughput_scope='one synthetic step including initialization/save/reload; NOT training throughput')
except Exception as e:
    result.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc()[-12000:])
finally:
    p=spec.get('checkpoint_path')
    if p and Path(p).is_file():Path(p).unlink() # own disposable synthetic checkpoint only
    Path(spec['result_path']).write_text(json.dumps(result,indent=2,allow_nan=False))
'''

def repository_assessment(ctx):
    run,cfg=ctx['run'],ctx['cfg']; rows=[];worker=run/'model_smoke_worker.py';write_text(worker,MODEL_WORKER)
    for model in MODEL_SPECS:
        mid=model['model_id'];repo_url='https://github.com/'+model['repository']; row={'model_id':mid,'official_repository':repo_url,'commit_sha':None,'commit_provenance':None,'local_source_sha256':None,'source_pin_status':'NOT_RUN','license_status':'UNVERIFIED','license_evidence_ref':None,'license_sha256':None,'permission_status':'PENDING_REVIEW','pretrained_weight_permission':'NOT_VERIFIED; no weights downloaded or used','package_version':None,'dependency_notes':model['deps'],'runtime_compatibility':'NOT_RUN','documentation_evidence':'Inherited v3.3 roster; official repository link recorded; runtime recheck and installed-source evidence are separate','network_check':'NOT_RUN','smoke_status':'NOT_RUN','smoke_result_ref':None,'blocker':None}
        local=cfg.repository_paths.get(mid);local_files=[];licenses=[]
        if local:
            repo_path=Path(local).resolve();input_root=Path(cfg.input_root).resolve()
            if not repo_path.is_dir() or input_root not in repo_path.parents:row['blocker']='Repository must be a directory under read-only input_root'
            else:
                for p in repo_path.rglob('*'):
                    if p.is_file() and '.git' not in p.parts and (p.suffix in {'.py','.txt','.toml','.yaml','.yml','.json'} or p.name.upper().startswith(('LICENSE','COPYING'))):local_files.append(p)
                manifest=[{'relative_path':str(p.relative_to(repo_path)),'sha256':sha256_file(p)} for p in sorted(local_files)]
                write_json(run/'repository_evidence'/f'{mid}_files.json',manifest);row['local_source_sha256']=hashlib.sha256(json_bytes(manifest)).hexdigest()
                git=command_result(['git','-C',str(repo_path),'rev-parse','HEAD'])
                row['commit_sha']=git['stdout'].strip() if git['returncode']==0 else None;row['commit_provenance']='LOCAL_GIT' if row['commit_sha'] else None
                dirty=command_result(['git','-C',str(repo_path),'status','--porcelain'])
                pin=cfg.model_pins.get(mid)
                row['source_pin_status']='PASS' if pin and re.fullmatch('[0-9a-f]{40}',pin) and row['commit_sha']==pin and dirty['returncode']==0 and not dirty['stdout'].strip() else 'BLOCKED_NEEDS_MATCHING_CLEAN_COMMIT'
                licenses=[p for p in local_files if p.name.upper().startswith(('LICENSE','COPYING'))]
        elif model['package']:
            try:
                dist=importlib.metadata.distribution(model['package']);row['package_version']=dist.version
                files=list(dist.files or []);code_files=[dist.locate_file(f) for f in files if str(f).endswith('.py')]
                row['local_source_sha256']=hashlib.sha256(json_bytes([{'relative_path':str(f),'sha256':sha256_file(dist.locate_file(f))} for f in files if str(f).endswith('.py') and dist.locate_file(f).is_file()])).hexdigest()
                licenses=[dist.locate_file(f) for f in files if re.search(r'(^|/)(LICENSE|COPYING)',str(f),re.I)]
                row['source_pin_status']='PACKAGE_VERSION_AND_SOURCE_HASH; git commit unavailable'
            except importlib.metadata.PackageNotFoundError:row['blocker']='Package not installed; no automatic environment mutation'
        permission_path=cfg.model_permission_evidence.get(mid)
        if permission_path:
            try:
                p=allowed_input(cfg,permission_path);row['license_evidence_ref']=str(p);row['license_sha256']=sha256_file(p);row['permission_status']='DOCUMENT_PRESENT_REQUIRES_HUMAN_REVIEW';access(ctx,p,'permission_evidence_hash','permission_evidence')
            except ValueError as e:row['blocker']=str(e)
        if licenses:
            texts=[]
            for p in licenses:
                if p.is_file() and p.stat().st_size<1024**2:texts.append(p.read_text(errors='replace'))
            combined='\n'.join(texts)
            identified='Apache-2.0' if 'Apache License' in combined and 'Version 2.0' in combined else 'MIT' if 'Permission is hereby granted, free of charge' in combined else 'LICENSE_TEXT_UNCLASSIFIED'
            row['license_status']=identified;row['license_evidence_ref']='repository_evidence/'+mid+'_licenses.txt';write_text(run/row['license_evidence_ref'],combined);row['license_sha256']=sha256_file(run/row['license_evidence_ref'])
            row['permission_status']='CODE_LICENSE_IDENTIFIED; weights and intended use still require review' if identified in {'Apache-2.0','MIT'} else 'PENDING_REVIEW'
        if cfg.network_checks:
            try:
                meta,body=small_http('https://api.github.com/repos/'+model['repository']+'/commits/HEAD');remote=json.loads(body);observed=remote['sha']
                write_json(run/'repository_evidence'/f'{mid}_remote_head.json',{'http':meta,'observed_remote_head':observed,'note':'Remote HEAD does not prove installed package or local snapshot identity'})
                if row['commit_sha'] is None:row['commit_sha']=observed;row['commit_provenance']='REMOTE_HEAD_ONLY_NOT_LOCAL_SOURCE_PIN'
                row['network_check']='HTTP_METADATA_RECHECK_ONLY'
                access(ctx,repo_url,'repository_metadata','official_documentation')
                try:
                    lm,lb=small_http('https://api.github.com/repos/'+model['repository']+'/license');obj=json.loads(lb);write_json(run/'repository_evidence'/f'{mid}_remote_license.json',{'http':lm,'license':obj.get('license'),'path':obj.get('path'),'blob_sha':obj.get('sha')})
                except Exception as e:row['network_check']+='; LICENSE_API_UNAVAILABLE '+str(e)[:180]
            except Exception as e:row['network_check']='UNAVAILABLE: '+str(e)[:240]
        result={'model_id':mid,'status':'NOT_RUN','reason':'run_model_smoke=False or model not selected','evidence_kind':'NO_EXECUTION_CLAIM'}
        if cfg.run_model_smoke and mid in cfg.model_smoke_ids:
            legal=row['license_status'] in {'MIT','Apache-2.0'} or bool(permission_path and row['license_sha256'])
            pinned=(not local and row['package_version'] is not None) or row['source_pin_status']=='PASS'
            if not legal or not pinned:
                result.update(status='BLOCKED',reason='Need actual code license/permission evidence and pinned source or installed version fingerprint; document presence is not supervisor approval')
            else:
                spec={'model_id':mid,'repo_path':str(Path(local).resolve()) if local else None,'device':cfg.smoke_device,'size':cfg.smoke_size,'checkpoint_path':str(run/'model_checks'/f'{mid}_synthetic.pt'),'result_path':str(run/'model_checks'/f'{mid}.json')}
                spec_path=run/'model_checks'/f'{mid}_request.json';write_json(spec_path,spec)
                response=command_result([sys.executable,str(worker),str(spec_path)],cwd=run,timeout=cfg.smoke_timeout_seconds)
                write_json(run/'model_checks'/f'{mid}_process.json',response)
                if Path(spec['result_path']).exists():result=json.loads(Path(spec['result_path']).read_text())
                else:result.update(status='BLOCKED',reason='Worker failed/timed out before result; inspect process report')
                result['canonical_448_shape_test']=cfg.smoke_size==448
                if result['status']=='PASS' and cfg.smoke_size!=448:result['readiness_limitation']='Reduced-shape diagnostic only; repeat at448 before model gate'
        row['smoke_status']=result['status'];row['runtime_compatibility']='MEASURED_TECHNICAL_SMOKE_ONLY' if result['status']=='PASS' else 'NOT_ESTABLISHED'
        row['smoke_result_ref']=f'model_checks/{mid}.json';write_json(run/row['smoke_result_ref'],result)
        rows.append(row)
    write_csv(run/'repository_registry.csv',rows,list(rows[0]));ctx['models']=rows
    roster={'schema_version':SCHEMA_VERSION,'status':'CANDIDATE_ROSTER_PENDING_TECHNICAL_LEGAL_AND_S5_REVIEW','seeds':SEEDS,'optional_extra_seeds':'5 total only if predeclared and budgeted; no seed selection from calibration','models':MODEL_SPECS,'runtime_assessment':rows,'fallback_policy':'Use SegFormer-B0 for first technically/legally unavailable modern slot; ConvNeXt-Tiny fallback for a second unavailable slot, only if its own checks pass. Never replace based on accuracy. No fallback is automatically training-approved here.','source_note':'SMP is an implementation library, not a claim of exact historical MRC recipe reproduction','full_training_performed':False}
    roster['slot_decisions']=[{'slot':m['slot'],'candidate':m['model_id'],'status':'PENDING_TECHNICAL_LEGAL_REVIEW','technical_status':next(r['smoke_status'] for r in rows if r['model_id']==m['model_id']),'declared_fallback':m['fallback'],'training_authorized':False} for m in MODEL_SPECS if m['slot'] in {'A','B','C'}]
    write_json(run/'model_roster.json',roster)
    table='\n'.join(f"| {r['model_id']} | {r['smoke_status']} | {r['license_status']} | {r['source_pin_status']} |" for r in rows)
    write_text(run/'modern_baseline_repro_check.md','# Modern model reproducibility assessment\n\nDocumentation inspection is not reproduction. A PASS smoke result tests random tensor forward/backward and reloading an own random checkpoint, not accuracy, pretrained-weight rights, full training or supervisor approval.\n\n| Model | Technical smoke | Local code license | Source identity |\n|---|---|---|---|\n'+table+'\n\nInput contract: B×3×448×448; segmentation output B×1×448×448 after the explicit SegFormer bilinear logit upsampling adapter. No silent resizing is permitted for other engines. DMSRCrack first tuple output is segmentation; second is boundary. SCSegamba custom operator and output semantics require pinned-source review.\n\nKaggle CPU/GPU support and memory are proven only by the actual model_checks/*.json results. Source pins, code license and pretrained-weight permission are separate. No dependency downgrade or CUDA compiler installation is automatic. If stacks conflict, use separately versioned environments and exchange hashed artifacts. Any failure must lead to repair, the declared technical/legal fallback before training, or a dated amendment; poor accuracy is not a fallback trigger.\n\nThe worker blocks network calls and uses random initialization. Third-party checkpoints are never unpickled. A deliberate one-step synthetic tensor optimization tests gradients and is not a full-data training experiment. SCSegamba may require dependencies unavailable in current Kaggle; that remains a BLOCKED result.\n')
    print('Model technical smoke:',{r['model_id']:r['smoke_status'] for r in rows})

# %% Resource plan, field route and decisions

def resource_and_field(ctx):
    run,cfg=ctx['run'],ctx['cfg'];rows=[]
    phase_budgets=[('01',0,3,'CPU inventory; optional synthetic GPU smoke'),('02',0,4,'CPU audit, grouping, annotation; no architecture training'),('03',42,156,'Three preferred engines × three seeds; grouped clean training'),('04',1,6,'Cached inference; CPU structural metric validation'),('05',0,5,'Scores, development CDFs and preregistration'),('06',1,5,'Single frozen calibration experiment, then independent internal test'),('07',3,15,'External/HN/corruption inference; no test tuning'),('08',0,5,'Statistics, claim ledger and release')]
    disk=ctx['env']['disk'];ram=ctx['env']['ram']
    for p,lo,hi,note in phase_budgets:
        rows.append({'item_id':'phase'+p,'phase':p,'engine':None,'gpu_hours_low':lo,'gpu_hours_high':hi,'seeds':3 if p=='03' else None,'estimate_kind':'PROVISIONAL_BLUEPRINT_RANGE_NOT_MEASURED','measured_seconds':None,'peak_cuda_bytes':None,'checkpoint_bytes':None,'runtime_available_ram_bytes':ram.get('MemAvailable_bytes') if ram else None,'runtime_free_disk_bytes':disk['free_bytes'],'session_limit_hours':cfg.session_limit_hours,'dependency':note,'recovery_strategy':'Epoch best+last with optimizer/scheduler/scaler/RNG/sampler; atomic writes; export >=30 minutes before live limit; commit Kaggle output version','notes':'Current runtime RAM/disk are measured; they are NOT a promise of future phase capacity'})
    for m in MODEL_SPECS:
        p=run/'model_checks'/f"{m['model_id']}.json";measurement=json.loads(p.read_text()) if p.exists() else {}
        rows.append({'item_id':'model_'+m['model_id'],'phase':'03','engine':m['model_id'],'gpu_hours_low':m['hours_low']*3,'gpu_hours_high':m['hours_high']*3,'seeds':3,'estimate_kind':'TRAINING_RANGE_PROVISIONAL; synthetic smoke not training throughput','measured_seconds':measurement.get('elapsed_seconds'),'peak_cuda_bytes':measurement.get('peak_cuda_bytes'),'checkpoint_bytes':measurement.get('checkpoint_bytes'),'runtime_available_ram_bytes':ram.get('MemAvailable_bytes') if ram else None,'runtime_free_disk_bytes':disk['free_bytes'],'session_limit_hours':cfg.session_limit_hours,'dependency':m['deps'],'recovery_strategy':'Three immutable member checkpoints; best+resumable last per active seed; random smoke weights are deleted','notes':f"{m['hours_low']}–{m['hours_high']} h/seed provisional. Two optional extra seeds add two jobs. Forward/backward memory differs from full recipe AMP/data-loader memory."})
    write_csv(run/'resource_plan.csv',rows,list(rows[0]))
    write_text(run/'resource_plan_notes.md','# Resource assumptions and recovery\n\n'+blueprint_section(ctx,14)+'\n\nThis run measured only the current environment and any explicitly enabled model smoke. Training estimates remain provisional because no representative data-loader/training benchmark was performed. Do not multiply one-step initialization/checkpoint time into a claimed measured training estimate. A future valid estimate is N*epochs/(3600*measured_training_images_per_second), plus validation/checkpoint/setup and 25% scheduling allowance.\n\nLive session limit supplied: '+str(cfg.session_limit_hours)+' hours. If null, read your current Kaggle UI before scheduling GPU work. No fixed weekly quota or GPU allocation is assumed. Two GPUs do not pool their memory automatically. Keep raw ZIPs mounted; no whole-dataset extraction in this phase.\n')
    evidence=None;problems=[];docs=[]
    if cfg.field_evidence_path:
        try:
            p=allowed_input(cfg,cfg.field_evidence_path)
            if p.stat().st_size>1024**2:raise ValueError('Field evidence JSON too large')
            evidence=json.loads(p.read_text());access(ctx,p,'field_route_evidence_read','permission_evidence')
            required=['access_document','permission_document','capture_plan_document','responsible_reviewers','devices','capture_plan_date']
            for k in required:
                if not evidence.get(k):problems.append('Missing '+k)
            for k in ['access_document','permission_document','capture_plan_document']:
                if evidence.get(k):
                    q=allowed_input(cfg,evidence[k]);docs.append({'role':k,'path':str(q),'sha256':sha256_file(q),'byte_size':q.stat().st_size})
            if evidence.get('capture_plan_date'):dt.date.fromisoformat(evidence['capture_plan_date'])
            if evidence.get('access_secured') is not True or evidence.get('permission_granted') is not True:problems.append('Actual secured access/permission not asserted by evidence')
            ctx['input_artifacts'].append({'artifact_id':'field_route_evidence','path':str(p),'sha256':sha256_file(p),'byte_size':p.stat().st_size,'role':'field_documentation'})
        except (ValueError,OSError,TypeError) as e:problems.append(str(e))
    else:problems.append('No documented field-access package supplied')
    route='A' if evidence and not problems else 'B';ctx['field_route']=route
    write_json(run/'field_evidence_inventory.json',{'route':route,'status':'DOCUMENTED_ROUTE_A_REQUIRES_REVIEW' if route=='A' else 'ROUTE_B_DEFAULT','documents':docs,'missing_or_invalid':problems,'supervisor_approval':'PENDING_APPROVAL','evidence_authenticity':'Not independently authenticated; no expert annotations inferred'})
    write_text(run/'field_data_decision.md',f'# Field-data decision: Route {route}\n\n'+('Actual documentation is listed by hash in field_evidence_inventory.json. Review permission scope, reviewers, devices and dated capture plan before collection. Documentation presence is not automatic supervisor approval.\n' if route=='A' else 'Field access, permission, capture plan and responsible reviewers are not all documented. Use external testing, a hard-negative benchmark and controlled image corruptions. No site, device, participant, expert label or field result is invented.\n')+'\n'+blueprint_section(ctx,5).split('### 5.7 Field decision',1)[-1]+'\n\nS6 remains pending. Route selection does not certify independent-unit counts or annotation quality.\n')
    write_text(run/'supervisor_decisions.md','# Supervisor decisions — no automatic approvals\n\n'+blueprint_section(ctx,19).split('### 19.2 ',1)[-1].split('### 19.3',1)[0]+'\n\nEvery S1–S7 decision remains PENDING_APPROVAL in this generated run. Record signed reviewer identity, date, evidence, scope and any amendment in a new version; do not edit a sealed control bundle. Phase02 may audit source rights, group structure and annotations while later-model/shift approvals remain pending. It must not pretend that proposed unit definitions or sample counts are approved.\n')

def decision_register(ctx):
    run=ctx['run'];rows=[]
    definitions=[
      ('G01','01','Source provenance, exact statistical route, roster/fallbacks and field route recorded','phase01_manifest.json; statistical_design.json; model_roster.json; field_data_decision.md','Researcher/adviser','PENDING_APPROVAL','S1/S5/S6 review; actual dataset evidence','Resolve evidence; no invented approvals','Researcher/adviser approval'),
      ('G02','02','Independent units, grouped leakage audit, label validity and source permissions','Phase02 audit/data card','Curator + researcher','NOT_RUN','Phase02 decoded/perceptual/parent audit; source rights','Quarantine/rebuild/acquire','Curator approval and source permission'),
      ('G03','02','At least120 positive/122 negative independent calibration units; actual fixed N before outcomes','sample_size_feasibility.csv; future sampling plan','Script + adviser','NOT_RUN','Actual independent counts and S2','Acquire units or approved pre-calibration alternative; no test borrowing','S2 sampling approval'),
      ('G04','03','At least one frozen engine meets development IoU .56 / hard-negative .35 heuristic','Future development metrics and checkpoint registry','Script + researcher','NOT_RUN','Training permission, technical smoke, Phase02 groups','Repair or declared technical fallback; record negative feasibility','S5 roster/training freeze'),
      ('G05','04','Metric edge cases and inference-only observability validated','Future synthetic graph/score tests','Technical reviewer','NOT_RUN','Phase04 metrics and no-GT tests','Fix and invalidate dependent caches','S3 metric review'),
      ('G06','05','Model, scores/CDF, policies, losses, N and analysis frozen independently of calibration','Future preregistration hashes/access log','Researcher','NOT_RUN','S1–S7 relevant decisions and complete freeze','Remain in development','Signed preregistration'),
      ('G07','05→06','26 exact bounds; accepted denominators; valid sampler; sentinel; no monotone conditional risk or optional stopping','statistical_self_tests.json + future Phase05/06 reviewed proof/code tests','Independent technical reviewer','PENDING_APPROVAL','Sampler audit, frozen Phase05 code and independent sign-off','BLOCK FINAL CALIBRATION until corrected and signed','Independent mathematical/code sign-off'),
      ('G08','06','Frozen internal certification/test; complete positive or negative result','Future selected policy + independent test report','Researcher + script','NOT_RUN','G02/G03/G05/G06/G07 and policy-freeze marker','Report no certification or invalidate contaminated result','Review evidence and access log'),
      ('G09','07','External/HN/route testing; weighted claims scoped by theorem assumptions','Future shift diagnostics and claims ledger','Researcher/adviser','NOT_RUN','Source audit, frozen target fitting, S4 and route tests','Keep empirical/negative result; no unsupported guarantees','Shift-claim reviewer'),
      ('G10','08','Reproducible population-specific publication claims','Final manifests and claims ledger','Researcher/adviser','NOT_RUN','Phases02–08 assets and verified central claims','Narrow claims or delay release','Final manuscript/release approval')]
    for gid,phase,req,ev,ver,status,prereq,fail,approval in definitions:
        rows.append({'gate_id':gid,'phase':phase,'requirement':req,'evidence_ref':ev,'verifier':ver,'verification_method':'Hash/schema checks plus named evidence review; generated report is not sign-off','status':status,'missing_prerequisites':prereq,'failure_action':fail,'approval_requirement':approval,'signed_at':None,'amendment_ref':None})
    for mid in MODEL_SPECS:
        r=next((r for r in ctx.get('models',[]) if r['model_id']==mid['model_id']),{})
        status='BLOCKED' if r.get('smoke_status')=='BLOCKED' else 'NOT_RUN' if r.get('smoke_status')!='PASS' else 'PENDING_APPROVAL'
        rows.append({'gate_id':'M01_'+mid['model_id'],'phase':'01→03','requirement':'Pinned implementation, code/weights permission, canonical-shape forward/backward/reload and resource fit','evidence_ref':r.get('smoke_result_ref','repository_registry.csv'),'verifier':'Researcher + technical reviewer','verification_method':'Isolated synthetic model smoke plus license/recipe review','status':status,'missing_prerequisites':'Any unverified source/license/weights/448-shape/recipe compatibility; S5 approval','failure_action':mid['fallback']+'; accuracy is not a fallback trigger','approval_requirement':'Legal/technical review before training','signed_at':None,'amendment_ref':None})
    assert all(r['status'] in GATE_STATUSES for r in rows)
    write_csv(run/'decision_gates.csv',rows,list(rows[0]));ctx['gates']=rows

# %% Restartable stage execution

def fingerprint_inputs(ctx):
    cfg=ctx['cfg'];root=Path(cfg.input_root);paths=set()
    roots,_=discover_raw_roots(cfg)
    for rr in roots:
        paths.update(p.resolve() for p in rr.rglob('*') if p.is_file() and p.suffix.lower()=='.zip')
    if root.exists():
        paths.update(p.resolve() for p in root.rglob('*') if p.is_file() and re.search('mrc|legacy',str(p),re.I) and p.suffix.lower() in {'.csv','.json','.yaml','.yml','.toml','.pt','.pth','.ckpt','.h5','.hdf5','.ipynb','.md','.txt'} and not re.search('final.?test|internal.?test|external.?test',str(p),re.I))
    explicit=cfg.legacy_paths+cfg.legacy_split_manifests+list(cfg.model_permission_evidence.values())+([cfg.field_evidence_path] if cfg.field_evidence_path else [])
    for name in explicit:
        try:paths.add(allowed_input(cfg,name))
        except ValueError:pass
    for name in cfg.repository_paths.values():
        p=Path(name)
        if p.is_dir():paths.update(q.resolve() for q in p.rglob('*') if q.is_file() and '.git' not in q.parts)
    if cfg.field_evidence_path:
        try:
            obj=json.loads(allowed_input(cfg,cfg.field_evidence_path).read_text())
            for key in ['access_document','permission_document','capture_plan_document']:
                if obj.get(key):paths.add(allowed_input(cfg,obj[key]))
        except (OSError,ValueError):pass
    entries=[];ctx['input_hash_cache']={}
    for p in sorted(paths):
        try:
            # SMOKE never pretends a size/mtime token is a content fingerprint.
            h=sha256_file(p) if cfg.run_mode=='FULL' or p.suffix.lower()!='.zip' else None
            if h:ctx['input_hash_cache'][str(p)]=h;access(ctx,p,'input_content_fingerprint')
            entries.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h,'hash_status':'PASS' if h else 'NOT_RUN_SMOKE'})
        except OSError as e:entries.append({'path':str(p),'sha256':None,'error':str(e)})
    write_json(ctx['run']/'input_fingerprints.json',entries)
    ctx['input_set_hash']=hashlib.sha256(json_bytes(entries)).hexdigest();ctx['cache_allowed']=cfg.run_mode=='FULL' and all(e.get('sha256') for e in entries) and not cfg.network_checks
    return entries

def stage(ctx,name,fn):
    """Reuse only an unsealed same-run stage with actual input/config/code/output hashes."""
    run=ctx['run']
    if (run/'SEALED.json').exists():raise RuntimeError('Finalized run is immutable; start a new run')
    marker=run/'.stage_cache'/f'{name}.json'
    key=hashlib.sha256(json_bytes({'inputs':ctx.get('input_set_hash'),'config':ctx['config_sha256'],'code':ctx['code_sha256'],'environment':ctx['env']['packages'],'gpu':ctx['env']['gpu'],'stage':name})).hexdigest()
    if marker.exists() and ctx.get('cache_allowed'):
        try:
            old=json.loads(marker.read_text())
            valid=old['cache_key']==key and all((run/p).is_file() and sha256_file(run/p)==h for p,h in old['outputs'].items())
            if valid:
                for k,v in old['context'].items():
                    if k in {'missing','access','input_artifacts'}:ctx[k].extend(v)
                    else:ctx[k]=v
                print(name+': reused verified same-run outputs');return
        except (OSError,ValueError,KeyError):pass
    before={str(p.relative_to(run)):sha256_file(p) for p in run.rglob('*') if p.is_file() and '.stage_cache' not in p.parts}
    lengths={k:len(ctx[k]) for k in ['access','missing','input_artifacts']};prior_keys=set(ctx);start=time.perf_counter()
    try:
        fn(ctx)
        after={str(p.relative_to(run)):sha256_file(p) for p in run.rglob('*') if p.is_file() and '.stage_cache' not in p.parts}
        changed={p:h for p,h in after.items() if before.get(p)!=h}
        if marker.exists():
            previous=json.loads(marker.read_text())
            for p in previous.get('outputs',{}):
                if p in after:changed[p]=after[p]
        patch={k:ctx[k][lengths[k]:] for k in lengths}
        for k in set(ctx)-prior_keys:
            if k not in {'cfg','run','env'}:patch[k]=ctx[k]
        # Capture the stage-owned values even when rerunning a prior failed stage in the same kernel.
        owned={'archive_inventory':['archives','raw_roots'],'legacy_inventory':['legacy','lineage_inputs'],'preliminary_lineage':['lineage_status'],'literature':['literature_count'],'statistics':['statistical_tests_pass'],'model_assessment':['models'],'resources_field':['field_route'],'decision_gates':['gates']}
        for k in owned.get(name,[]):
            if k in ctx:patch[k]=ctx[k]
        patch=json.loads(json.dumps(patch,default=str))
        write_json(marker,{'cache_key':key,'outputs':changed,'context':patch,'elapsed_seconds':time.perf_counter()-start})
    except Exception as e:
        ctx['errors'].append({'stage':name,'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()})
        write_json(run/'stage_errors.json',ctx['errors']);print(name+': BLOCKED — '+str(e)+'; proceeding to export honest partial status.')
    write_csv(run/'missing_inputs.csv',ctx['missing'],['item','status','reason','blocks','required_action'])
    write_csv(run/'data_access_log.csv',ctx['access'],['timestamp_utc','phase','path','operation','allowed_role','status','note'])

# %% Artifact contracts and immutable handoff
REQUIRED_OUTPUTS=['legacy_manifest.json','legacy_hashes.sha256','legacy_baseline_record.md','missing_inputs.csv','preliminary_lineage_scan.csv','preliminary_lineage_report.md','literature_matrix.csv','novelty_gap.md','verified_references.bib','rcps_decision_D2.md','statistical_design.json','sample_size_feasibility.csv','modern_baseline_repro_check.md','model_roster.json','repository_registry.csv','resource_plan.csv','field_data_decision.md','decision_gates.csv','supervisor_decisions.md']

PHASE02_CONTRACT={
 'schema_version':'1.0','blueprint_version':'3.3','next_notebook':'CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb',
 'required_inputs':['canonical Phase01 control ZIP','matching ZIP SHA-256 sidecar','same raw dataset version with matching archive hashes'],
 'critical_artifacts':['blueprint_v3.3.md','config.json','statistical_design.json','model_roster.json','field_data_decision.md','decision_gates.csv','supervisor_decisions.md','archive_inventory.csv','dataset_discovery.json','legacy_manifest.json','missing_inputs.csv','schemas.json','cracksafe_core.zip'],
 'split_schema_minimum':['sample_id','unit_id','group_id','source_id','image_ref','mask_ref_or_sealed_label_ref','true_class_for_curator','selection_seed','role','split_version'],
 'sample_registry_minimum':['sample_id','source_id','archive_ref','member_path','decoded_hash','image_hash','mask_hash','parent_id','site_id','session_id','split_group_id','certification_unit_id','role','true_class','mask_status','native_shape','eval_shape','license_status','legacy_exposure_status','exclusion_reason'],
 'independent_unit_rule':'Group by highest dependence level (site/session/parent/original). Choose one label-blind representative per defensible certification unit; audit whether units are actually IID within class.',
 'calibration_floor':{'positive':120,'negative':122},'preferred_target_per_class':300,
 'access_barrier':'Phase02 may curate/assign sealed final roles and audit labels as curator, but must not train/evaluate/tune a final-test model or expose final-test labels to development code.',
 'sequence':['Discover mounted control ZIP and sidecar; reject ambiguity rather than guess latest','Verify ZIP fingerprint before safe extraction; validate paths, sizes and internal hashes','Verify phase01_manifest schema/version and critical artifact hashes','Resolve raw mounts by discovered archive identity; verify complete SHA256; no silent source substitution','Read warnings, exclusions, source/permission ledgers and unresolved decisions','Inventory pairs, decode validation, exact/decoded/perceptual hashes and source aggregation overlap','Recover site/session/parent lineage; quarantine ambiguity; adjudicate masks and confirmed negatives','Count independent units, choose population and fixed count plan with S2 review','Create grouped partitions and label-blind representatives; freeze split/access manifests; no final calibration','Export Phase02 artifacts, gates and next handoff'],
 'pending_allowed_for_audit':['Missing legacy checkpoints/configuration','Unfinished model GPU smoke or model permission decision','S3/S4/S5/S7 later-stage approvals; no claim they are waived'],
 'blocks_audit':['Unreadable/missing control bundle or invalid hashes/schema/version','No raw archives identified and hashed','Missing exact statistical/source contract or unresolved software failure affecting audit inputs'],
 'blocks_phase02_exit':['Source rights/annotation credibility unresolved','Cross-split duplicate/parent dependence unresolved','Actual independent calibration counts or S2 population/unit/count approval unresolved']}

def artifact_entry(ctx,path):
    rel=str(path.relative_to(ctx['run']))
    return {'artifact_id':'phase01:'+rel,'relative_path':rel,'sha256':sha256_file(path),'byte_size':path.stat().st_size,'media_type':mimetypes.guess_type(path.name)[0] or 'application/octet-stream','schema_version':SCHEMA_VERSION,'producing_run_id':ctx['run_id'],'required_by':['02'] if rel in PHASE02_CONTRACT['critical_artifacts'] or rel=='NEXT_PHASE_INPUTS.md' else ['audit'],'privacy/license_status':'PRIVATE_RESEARCH_CONTROL; raw-source and third-party rights not transferred'}

def control_files(run):
    exclusions={'artifact_catalog.json','phase01_manifest.json','phase01_manifest.sha256','SHA256SUMS.sha256','SEALED.json','bundle_verification.json'}
    return sorted(p for p in run.rglob('*') if p.is_file() and '.stage_cache' not in p.parts and '__pycache__' not in p.parts and p.name not in exclusions and not p.name.startswith('CrackSAFE_CP_v3.3_phase01_control_') and p.suffix not in {'.tmp','.pt','.pth','.ckpt'})

def write_handoff(ctx,entries,bundle_name):
    run=ctx['run'];by_name={e['relative_path']:e for e in entries}
    rows=[]
    for rel in PHASE02_CONTRACT['critical_artifacts']:
        e=by_name.get(rel)
        rows.append(f"| `phase01:{rel}` | `{e['sha256'] if e else 'MISSING_INPUT'}` | {e['byte_size'] if e else 'N/A'} |")
    content=f'''# Notebook02 handoff — actual run {ctx['run_id']}

Blueprint 3.3; schema1.0; core{CORE_VERSION}; config SHA-256 `{ctx['config_sha256']}`; combined implementation/workflow SHA-256 `{ctx['code_sha256']}`. Run mode **{ctx['cfg'].run_mode}**. Global Phase01 status **BLOCKED** while relevant evidence/signatures remain pending. Data-audit readiness: **{ctx.get('phase02_audit_ready',False)}**. This does not permit training or calibration.

## Exactly what to attach

| File or Bundle | Purpose | Generated Kaggle Location | Required for Notebook 02? | How to Attach |
|---|---|---|---|---|
| `{bundle_name}` | All small Phase01 controls, blueprint, roster, statistical design, manifests and shared code | `{run}/{bundle_name}` | Yes | Prefer attach this saved Notebook01 output version through Add Input; private dataset alternative below |
| `{bundle_name}.sha256` | Verify final immutable ZIP bytes | `{run}/{bundle_name}.sha256` | Yes | Keep next to the ZIP in the same attached output/dataset |
| `phase01_manifest.json`, its sidecar, `SHA256SUMS.sha256`, `artifact_catalog.json`, `NEXT_PHASE_INPUTS.md` | Internal fingerprints and contracts | Inside canonical ZIP and `{run}` | Required contents; no separate attachment if ZIP is present | Read from verified ZIP |
| `statistical_design.json`, `model_roster.json`, `config.json`, `blueprint_v3.3.md`, `cracksafe_core.zip`, schemas/gates/reports | Exact downstream methodology and code dependencies | Inside canonical ZIP | Yes as bundled contents | Do not download/reattach each separately |
| `abarman79/wall-crack-cp-datasets` | Raw archives; deliberately absent from the control ZIP | Discovered here: `{', '.join(ctx.get('raw_roots',[])) or 'MISSING_INPUT'}` | Yes, attach the same actual dataset version again | Kaggle Add Input → Your Datasets; verify archive SHA-256 |
| Original legacy evidence and field/permission documents | Resolve still-missing provenance if later supplied | Actual optional mounts recorded in ledgers | Optional for Phase02 initial audit; required before claims depending on them | Attach private evidence dataset; never fabricate replacements |

**Recommended path:** save Notebook01 with **Save Version → Save & Run All** (wording may differ), wait for completion, verify Output contains ZIP + sidecar, then add that exact output version to Notebook02. Kaggle official documentation supports attaching saved notebook outputs via Add Input. Record the actual notebook/version identifier; do not rely on mutable latest.

**Reliable fallback/portable archive:** create a **private Kaggle dataset** containing the canonical ZIP and sidecar only. Version it, attach it to Notebook02, and also attach the raw dataset. Use this if the output-version picker is unavailable or cannot pin the version. Check privacy. A local draft run alone is not persistence.

Actual mount slugs are discovered. Examples such as `/kaggle/input/<saved-notebook-output>/.../{bundle_name}` or `/kaggle/input/<phase01-control-dataset>/{bundle_name}` are examples only. Recursively discover the exact canonical basename plus sidecar; if more than one run matches, require an explicit choice. Never guess the mount directory.

## Critical artifact IDs and content hashes

| Artifact ID | SHA-256 | Bytes |
|---|---|---:|
'''+ '\n'.join(rows)+'''

The outer ZIP hash is deliberately absent from this document because it is stored **outside** the ZIP in its sidecar. This document lists earlier payload hashes only; the final manifest hashes this document. Do not create a circular self-hash.

## What may proceed and what remains blocked

A FULL, hash-valid, schema-valid bundle with identifiable raw archives permits **Phase02 source/data auditing**, even if legacy checkpoints and later-model/GPU checks are missing. Unsafe or corrupt archive members remain quarantined; this permission is not permission to extract them. Missing expected archive names must be reconciled against actual source coverage; renames alone are not proof of missing data.

S1 exact design remains proposed until signed; S2 actual population, independent-unit definition and fixed count plan must be reviewed before the Phase02 calibration manifest is approved; S6 source rights/reviewer resources must be documented before benchmark use. S3/S4/S5/S7 and G07 apply before their later dependent activities. None is automatically signed by this notebook. The exact list of unresolved items is in missing_inputs.csv, decision_gates.csv and supervisor_decisions.md.

Never modify sealed outputs, hashes, blueprint bytes, code bundle or original input archives. Amendments create a new version/run with explicit provenance and invalidate dependent caches. If the current run is SMOKE, rerun FULL before treating the input fingerprints as complete. If mandatory outputs are missing or hashes disagree, stop the affected audit dependency and preserve the failure report.

## Phase02 execution order

'''+ '\n'.join(f'{i+1}. {s}.' for i,s in enumerate(PHASE02_CONTRACT['sequence']))+'''

Required detailed schemas and barriers are in phase02_contract.json, schemas.json and the embedded blueprint Section12. No model checkpoint is required to start Phase02. No Notebook02–08 implementation is included in this bundle.
'''
    write_text(run/'NEXT_PHASE_INPUTS.md',content)

def verify_control_bundle(path,sidecar):
    path,sidecar=Path(path),Path(sidecar)
    parts=sidecar.read_text().strip().split('  ',1)
    if len(parts)!=2 or parts[1]!=path.name or parts[0]!=sha256_file(path):raise ValueError('ZIP SHA-256 sidecar mismatch')
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate names in control ZIP')
        for i in z.infolist():
            if member_warnings(i,Phase01Config()):raise ValueError('Unsafe member in control bundle: '+i.filename)
        bad=z.testzip()
        if bad:raise ValueError('Control ZIP CRC failure: '+bad)
        manifest=json.loads(z.read('phase01_manifest.json'))
        mside=z.read('phase01_manifest.sha256').decode().strip().split('  ',1)
        if mside!=[hashlib.sha256(z.read('phase01_manifest.json')).hexdigest(),'phase01_manifest.json']:raise ValueError('Manifest sidecar mismatch')
        for e in manifest['output_artifacts']:
            data=z.read(e['relative_path'])
            if len(data)!=e['byte_size'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('Manifest payload mismatch: '+e['relative_path'])
        for line in z.read('SHA256SUMS.sha256').decode().splitlines():
            h,p=line.split('  ',1)
            if hashlib.sha256(z.read(p)).hexdigest()!=h:raise ValueError('Hash-list mismatch: '+p)
        if manifest['blueprint_version']!='3.3' or manifest['phase']!='01':raise ValueError('Wrong phase/blueprint')
    return {'status':'PASS','verified_utc':utcnow(),'zip_sha256':parts[0],'manifest_output_count':len(manifest['output_artifacts']),'zip_member_count':len(names),'scope':'Control bundle integrity only; not raw payload integrity or scientific approval'}

def finalize_run(ctx):
    run=ctx['run']
    if (run/'SEALED.json').exists():
        seal=json.loads((run/'SEALED.json').read_text());result=verify_control_bundle(run/seal['bundle_name'],run/(seal['bundle_name']+'.sha256'));print('Existing sealed bundle verified:',run/seal['bundle_name']);return result
    # All stage failures remain visible. Missing mandatory reports are never silently invented.
    write_csv(run/'missing_inputs.csv',ctx['missing'],['item','status','reason','blocks','required_action'])
    write_csv(run/'data_access_log.csv',ctx['access'],['timestamp_utc','phase','path','operation','allowed_role','status','note'])
    write_json(run/'stage_errors.json',ctx['errors'])
    absent=[f for f in REQUIRED_OUTPUTS if not (run/f).is_file()]
    raw=ctx.get('archives',[])
    ready=ctx['cfg'].run_mode=='FULL' and bool(raw) and all(r.get('hash_status')=='PASS' for r in raw) and any(isinstance(r.get('members'),int) for r in raw) and ctx.get('statistical_tests_pass',False) and not absent and not ctx['errors']
    ctx['phase02_audit_ready']=ready
    ctx['env']['finished_utc']=utcnow();ctx['env']['phase_exit_status']='BLOCKED';write_json(run/'environment_snapshot.json',ctx['env'])
    status={'schema_version':SCHEMA_VERSION,'phase':'01','status':'BLOCKED','run_mode':ctx['cfg'].run_mode,'created_utc':ctx['created_utc'],'finished_utc':utcnow(),'phase02_audit_ready':ready,'readiness_scope':'Data/source audit only; not training, final calibration, or test evaluation','reasons':['Relevant S1–S7 human approvals remain pending','Model/weights permissions and reproducibility require evidence-specific review']+(['SMOKE mode is incomplete; run FULL'] if ctx['cfg'].run_mode=='SMOKE' else [])+(['Required reports missing: '+', '.join(absent)] if absent else [])+(['Stage failures recorded in stage_errors.json'] if ctx['errors'] else []),'missing_mandatory_outputs':absent,'raw_archive_count':len(raw),'legacy_records_found':len(ctx.get('legacy',[])),'literature_entries':ctx.get('literature_count',0),'field_route':ctx.get('field_route','UNRESOLVED'),'statistical_self_tests':'PASS' if ctx.get('statistical_tests_pass') else 'BLOCKED','model_smoke':{r['model_id']:r['smoke_status'] for r in ctx.get('models',[])},'scientific_certification_performed':False,'supervisor_approvals_granted':False}
    write_json(run/'phase_status.json',status)
    write_json(run/'phase02_contract.json',PHASE02_CONTRACT)
    schemas={'schema_version':SCHEMA_VERSION,'null_policy':'JSON null plus reason; CSV empty cells encode null, not zero. Read status/reason columns.','tables':{},'phase02_contract':'phase02_contract.json','artifact_manifest':'phase01_manifest.schema.json'}
    for p in sorted(run.rglob('*.csv')):
        with p.open(newline='',encoding='utf-8') as f:
            r=csv.reader(f);header=next(r,[]);count=sum(1 for _ in r)
        if not header or len(header)!=len(set(header)):raise ValueError('Invalid CSV header: '+str(p))
        schemas['tables'][str(p.relative_to(run))]={'columns':header,'row_count':count,'schema_version':SCHEMA_VERSION,'key_policy':'See primary_keys; physical row index is not a scientific sample ID'}
    schemas['primary_keys']={'archive_inventory.csv':['archive_id'],'archive_members.csv':['archive_id','member_index'],'literature_matrix.csv':['paper_id'],'repository_registry.csv':['model_id'],'decision_gates.csv':['gate_id'],'preliminary_lineage_scan.csv':['candidate_id'],'resource_plan.csv':['item_id']}
    write_json(run/'schemas.json',schemas)
    manifest_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','required':['schema_version','blueprint_version','blueprint_sha256','phase','run_id','created_utc','status','scope','config_sha256','code_sha256','git_commit','seeds','input_artifacts','output_artifacts','gate_results','amendment_ids','environment_file','access_log_file'],'properties':{'schema_version':{'const':'1.0'},'blueprint_version':{'const':'3.3'},'phase':{'const':'01'},'status':{'enum':['PASS','BLOCKED','COMPLETE_NEGATIVE']},'blueprint_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'config_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'code_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'output_artifacts':{'type':'array','items':{'type':'object','required':['artifact_id','relative_path','sha256','byte_size','media_type','schema_version','producing_run_id','required_by','privacy/license_status'],'properties':{'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'byte_size':{'type':'integer','minimum':0}}}}}}
    write_json(run/'phase01_manifest.schema.json',manifest_schema)
    shared=run/'cracksafe_core.zip';temp=shared.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in [('cracksafe_core/__init__.py',b'from .phase01 import cp_upper, minimum_n, risk_cell, select_policy\n'),('cracksafe_core/phase01.py',(run/'phase01_core.py').read_bytes()),('cracksafe_core/VERSION',CORE_VERSION.encode())]:
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    temp.replace(shared)
    bundle_name=f"CrackSAFE_CP_v3.3_phase01_control_{ctx['run_id']}.zip"
    base=[artifact_entry(ctx,p) for p in control_files(run)]
    write_handoff(ctx,base,bundle_name)
    payload=[artifact_entry(ctx,p) for p in control_files(run)]
    write_json(run/'artifact_catalog.json',{'schema_version':SCHEMA_VERSION,'run_id':ctx['run_id'],'mount_resolution':'Match actual content hashes and relative logical paths; never infer a Kaggle dataset slug from a filename','raw_dataset_reference':'abarman79/wall-crack-cp-datasets','artifacts':payload,'excluded_from_self_catalog':['artifact_catalog.json','phase01_manifest.json','phase01_manifest.sha256','SHA256SUMS.sha256','outer ZIP and sidecar','SEALED.json','bundle_verification.json','.stage_cache']})
    outputs=payload+[artifact_entry(ctx,run/'artifact_catalog.json')]
    manifest={'schema_version':SCHEMA_VERSION,'blueprint_version':'3.3','blueprint_sha256':ctx['blueprint_sha256'],'phase':'01','run_id':ctx['run_id'],'created_utc':ctx['created_utc'],'status':'BLOCKED','scope':ctx['cfg'].scope,'config_sha256':ctx['config_sha256'],'code_sha256':ctx['code_sha256'],'code_hash_method':'SHA256(UTF8(core_source + newline + workflow_source)); source files included','git_commit':ctx['env']['git_commit'],'seeds':SEEDS,'input_artifacts':ctx['input_artifacts'],'output_artifacts':outputs,'gate_results':ctx.get('gates',[]),'amendment_ids':[],'environment_file':'environment_snapshot.json','access_log_file':'data_access_log.csv','phase02_audit_ready':ready,'exclusions':'No raw images/masks, original archives, trained checkpoints, stage cache, self hash, or outer ZIP in output_artifacts'}
    write_json(run/'phase01_manifest.json',manifest)
    write_text(run/'phase01_manifest.sha256',sha256_file(run/'phase01_manifest.json')+'  phase01_manifest.json\n')
    hash_files=control_files(run)+[run/'artifact_catalog.json',run/'phase01_manifest.json',run/'phase01_manifest.sha256']
    write_text(run/'SHA256SUMS.sha256',''.join(sha256_file(p)+'  '+str(p.relative_to(run))+'\n' for p in sorted(hash_files)))
    bundle=run/bundle_name;tmp=bundle.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(hash_files+[run/'SHA256SUMS.sha256']):z.write(p,str(p.relative_to(run)))
    tmp.replace(bundle);sidecar=run/(bundle_name+'.sha256');write_text(sidecar,sha256_file(bundle)+'  '+bundle.name+'\n')
    verification=verify_control_bundle(bundle,sidecar);write_json(run/'bundle_verification.json',verification)
    write_json(run/'SEALED.json',{'sealed_utc':utcnow(),'bundle_name':bundle_name,'zip_sha256':verification['zip_sha256'],'rule':'Do not mutate this run; subsequent work creates a new run/version'})
    print('\nPHASE01 SUMMARY\n'+json.dumps(status,indent=2))
    print('Gate status counts:',dict(Counter(g['status'] for g in ctx.get('gates',[]))))
    print('Model code/weight permission review:',{r['model_id']:r['permission_status'] for r in ctx.get('models',[])})
    print('Environment:',ctx['env']['python'].split()[0],ctx['env']['platform'])
    print('Blueprint:',BLUEPRINT_VERSION,'| source SHA256:',ctx['blueprint_sha256'])
    print('Output:',run,'\nCanonical control ZIP:',bundle,'\nZIP SHA sidecar:',sidecar,'\nIntegrity:',verification['status'])
    print('Preserve a Kaggle saved output version. Next phase: data audit only; human approvals remain pending.')
    return verification


# v3.3 folder-mount compatibility: Kaggle sometimes expands uploaded ZIPs into
# /kaggle/input/datasets/<owner>/<dataset>/ directories. Preserve the original
# archives-only routines above for archives and support extracted folders without
# creating copies of the original data. This is an input-adapter correction only.

_original_inventory_archives = inventory_archives

def discover_raw_roots(cfg):
    root = Path(cfg.input_root).resolve()
    if not root.exists():
        return [], 'INPUT_ROOT_MISSING'
    if cfg.raw_roots:
        paths = [Path(p).resolve() for p in cfg.raw_roots]
        if any(not p.is_dir() or not (p == root or root in p.parents) for p in paths):
            raise ValueError('raw_roots must be mounted directories under input_root')
        return sorted(set(paths)), 'EXPLICIT'
    hint = cfg.raw_dataset_hint.casefold()
    # Kaggle dataset mounts may be nested below datasets/<owner>/ rather than root.
    paths = [p.resolve() for p in root.rglob('*')
             if p.is_dir() and p.name.casefold() == hint]
    if paths:
        return sorted(set(paths)), 'RECURSIVE_DATASET_DIRECTORY_MATCH'
    found = [p.parent.resolve() for p in root.rglob('*.zip')
             if p.name.casefold() in {n.casefold() for n in EXPECTED_ARCHIVES}]
    return sorted(set(found)), ('EXPECTED_ARCHIVE_MATCH' if found else 'RAW_DATASET_NOT_FOUND')

def fingerprint_inputs(ctx):
    cfg = ctx['cfg']
    roots, how = discover_raw_roots(cfg)
    # Note that SMOKE remains a metadata-only rehearsal; FULL hashes actual files.
    paths = set()
    for root in roots:
        for p in root.rglob('*'):
            if p.is_file() or p.is_symlink():
                paths.add(p)
    # Explicit legacy or permission files may live on separate mounted inputs.
    for ref in cfg.legacy_paths + cfg.legacy_split_manifests + list(cfg.model_permission_evidence.values()) + ([cfg.field_evidence_path] if cfg.field_evidence_path else []):
        try: paths.add(allowed_input(cfg, ref))
        except (ValueError, OSError): pass
    for val in cfg.repository_paths.values():
        p = Path(val)
        if p.is_dir():
            paths.update(q for q in p.rglob('*') if q.is_file() and '.git' not in q.parts)
    entries = []
    ctx['input_hash_cache'] = {}
    any_missing = False
    for path in sorted(paths, key=lambda p: str(p)):
        try:
            if path.is_symlink():
                entries.append({'path':str(path), 'hash_status':'BLOCKED_SYMLINK', 'sha256':None})
                any_missing = True
                continue
            size = path.stat().st_size
            h = sha256_file(path) if cfg.run_mode == 'FULL' else None
            if h:
                ctx['input_hash_cache'][str(path.resolve())] = h
            entries.append({'path':str(path.resolve()), 'bytes':size, 'sha256':h,
                            'hash_status':'PASS' if h else 'NOT_RUN_SMOKE'})
        except OSError as exc:
            entries.append({'path':str(path), 'hash_status':'BLOCKED', 'error':str(exc), 'sha256':None})
            any_missing = True
    write_json(ctx['run']/'input_fingerprints.json', entries)
    ctx['input_set_hash'] = hashlib.sha256(json_bytes(entries)).hexdigest()
    ctx['cache_allowed'] = cfg.run_mode=='FULL' and bool(entries) and not any_missing and not cfg.network_checks
    return entries

def inventory_archives(ctx):
    cfg, run = ctx['cfg'], ctx['run']
    roots, how = discover_raw_roots(cfg)
    zipped = [p for root in roots for p in root.rglob('*.zip') if p.is_file()]
    if zipped:
        # Retain the original, thoroughly tested ZIP central-directory audit.
        return _original_inventory_archives(ctx)
    image_ext = {'.jpg','.jpeg','.png','.bmp','.tif','.tiff','.webp'}
    member_fields = ['archive_id','member_index','member_name','file_size',
                     'compressed_size','crc32','is_directory','image_extension',
                     'mask_name_hint','source_family_hint','warnings','payload_integrity',
                     'member_sha256','source_type']
    rows, members, warn, expected, overlap, patterns = [], [], [], [], {}, Counter()
    for root in roots:
        groups = [p for p in sorted(root.iterdir()) if p.is_dir() and not p.is_symlink()]
        if any(p.is_file() for p in root.iterdir()):
            groups.append(root)
        for group in groups:
            aid = f'raw_directory_{len(rows):03d}'
            files = [p for p in sorted(group.rglob('*')) if p.is_file() or p.is_symlink()]
            if group == root:
                files = [p for p in files if p.parent == root]
            digest = hashlib.sha256()
            bytes_total = 0
            images = masks = bad = 0
            for ix, path in enumerate(files):
                rel = path.relative_to(group).as_posix()
                flags=[]
                if path.is_symlink():
                    flags.append('SYMLINK_PATH')
                suffix = path.suffix.lower()
                is_img = suffix in image_ext
                hint = bool(re.search(r'(^|[/_\-])(masks?|labels?|ground.?truth|gt)([/_\-\.]|$)',rel,re.I))
                source = next((s for s in ['crack500','cracktree','gaps384','cfd','crackforest','deepcrack','sdnet','riss','aigle','esarc','tut']
                               if s in (group.name+' '+rel).casefold()), 'UNKNOWN')
                images += int(is_img)
                masks += int(is_img and hint)
                size = path.lstat().st_size
                bytes_total += size
                sha = ctx.get('input_hash_cache',{}).get(str(path.resolve())) if not flags else None
                if cfg.run_mode=='FULL' and not sha: flags.append('MISSING_CONTENT_SHA256')
                if flags:
                    bad += 1
                    warn.append({'archive_id':aid,'member_index':ix,'member_name':rel,
                                 'warning':';'.join(flags), 'action':'QUARANTINE_AND_REVIEW_IN_PHASE02'})
                digest.update(json_bytes({'path':rel, 'size':size, 'sha256':sha}))
                members.append({'archive_id':aid, 'member_index':ix, 'member_name':rel,
                                'file_size':size, 'compressed_size':None, 'crc32':None,
                                'is_directory':False,'image_extension':suffix if is_img else '',
                                'mask_name_hint':hint, 'source_family_hint':source,
                                'warnings':';'.join(flags),
                                'payload_integrity':'CONTENT_SHA256' if sha else 'NOT_CHECKED_SMOKE',
                                'member_sha256':sha,'source_type':'EXTRACTED_DIRECTORY'})
                if is_img and not flags:
                    patterns[(aid,source,'mask_hint' if hint else 'image_or_unknown')]+=1
                    if sha:
                        overlap.setdefault((path.name.casefold(),size,sha),set()).add(aid)
            rows.append({'archive_id':aid,'name':group.name,'path':str(group),
                         'sha256':digest.hexdigest() if cfg.run_mode=='FULL' and not bad and files else None,
                         'hash_status':'PASS' if cfg.run_mode=='FULL' and not bad and files else 'NOT_RUN_SMOKE' if cfg.run_mode=='SMOKE' else 'BLOCKED',
                         'bytes':bytes_total,'members':len(files),'images_by_extension':images,
                         'mask_name_hints':masks,'uncompressed_bytes':bytes_total,
                         'compressed_member_bytes':None,'warnings':bad,
                         'status':'PASS' if not bad else 'BLOCKED',
                         'integrity_scope':'EXTRACTED_DIRECTORY_PER_FILE_SHA256; NO_ZIP_CRC_OR_IMAGE_DECODE',
                         'source_type':'EXTRACTED_DIRECTORY'})
            ctx['input_artifacts'].append({'artifact_id':aid,'path':str(group),
                                           'sha256':rows[-1]['sha256'],'byte_size':bytes_total,
                                           'hash_status':rows[-1]['hash_status'],
                                           'role':'raw_extracted_folder_manifest'})
    # Names are only hints; do not require former ZIP names to exist after extraction.
    group_names = [r['name'].casefold() for r in rows]
    for name in EXPECTED_ARCHIVES:
        stem = name[:-4].casefold()
        found = next((r for r in rows if stem in r['name'].casefold() or r['name'].casefold() in stem),None)
        expected.append({'expected_name':name,'status':'EXTRACTED_DIRECTORY_CANDIDATE' if found else 'NOT_MATCHED_BY_NAME',
                         'discovered_path':found['path'] if found else None,
                         'note':'Kaggle extracted the ZIP. Exact source and license verification remain Phase02 tasks.'})
    if not rows:
        missing(ctx,'raw dataset','No readable raw source directories found','Phase02 data audit',
                'Attach existing Kaggle dataset and check discovered mount directories')
    write_csv(run/'archive_inventory.csv',rows,list(rows[0]) if rows else
              ['archive_id','name','path','sha256','hash_status','bytes','members','images_by_extension','mask_name_hints','uncompressed_bytes','compressed_member_bytes','warnings','status','integrity_scope','source_type'])
    write_csv(run/'archive_members.csv',members,member_fields)
    write_csv(run/'archive_warnings.csv',warn,['archive_id','member_index','member_name','warning','action'])
    write_csv(run/'archive_expectations.csv',expected,['expected_name','status','discovered_path','note'])
    write_csv(run/'source_pattern_inventory.csv',[{'archive_id':k[0],'source_family_hint':k[1],
              'naming_role':k[2],'member_count':v} for k,v in sorted(patterns.items())],
              ['archive_id','source_family_hint','naming_role','member_count'])
    write_csv(run/'archive_overlap_candidates.csv',[{'basename':k[0],'file_size':k[1],
              'crc32':None, 'archive_ids':';'.join(sorted(v)),
              'evidence':'FILE_SHA256_AND_NAME_MATCH; PHASE02_MUST_AUDIT_IMAGE_AND_PARENT_IDENTITY'}
              for k,v in overlap.items() if len(v)>1],
              ['basename','file_size','crc32','archive_ids','evidence'])
    ctx['archives'] = rows
    ctx['raw_roots'] = [str(r) for r in roots]
    write_json(run/'dataset_discovery.json',{'dataset_reference':'abarman79/wall-crack-cp-datasets',
              'roots':ctx['raw_roots'],'method':how,'source_type':'EXTRACTED_DIRECTORY',
              'original_zip_bytes_available':False,
              'historical_pairs_expected_unverified':11298,
              'historical_source_groups_expected_unverified':11,
              'unique_pair_count':None,'independent_calibration_unit_count':None,
              'integrity_scope':'Per-file SHA256 in FULL; no ZIP CRC or decoded-image verification'})
    print('Discovered extracted folders:',len(rows),'| files:',len(members),
          '| warnings:',len(warn),'| no decoded-image or label evaluation.')
    return rows
