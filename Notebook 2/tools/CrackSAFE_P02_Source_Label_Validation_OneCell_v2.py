# CrackSAFE-CP v3.3 — PRIVATE source-mask validation; ONE Kaggle cell
# Inputs: exact corrected v2 manifest ZIP (or Kaggle-expanded files) and original raw dataset.
# CPU only; Internet OFF. No held-out raw data or calibration labels are accessed.
from pathlib import Path, PurePosixPath
from collections import defaultdict, Counter
from datetime import datetime, timezone
import hashlib, zipfile, csv, io, json, random, re
import numpy as np
from PIL import Image, ImageDraw

INPUT=Path("/kaggle/input")
WORK=Path("/kaggle/working")
EXPECTED_ZIP_SHA="14ff7b9f8e65b814adb249c1905ddf299fc60f888ec398c0f50016e7b8eca1cd"
NAMES={
 "train":"TRAIN_CANDIDATES_SOURCE_SAFE_PRIVATE.csv",
 "dev":"DEVELOPMENT_CANDIDATES_SOURCE_SAFE_PRIVATE.csv",
 "heldout":"HELDOUT_SOURCE_TEST_AND_VAL_QUARANTINE_PRIVATE.csv",
 "mixed":"MIXED_PARENT_QUARANTINE_PRIVATE.csv",
 "summary":"PUBLIC_SUMMARY.json",
 "checksums":"SHA256SUMS.sha256",
}
SEED=2026
TAKE_TRAIN_PER_SOURCE=8
TAKE_DEV_PER_SOURCE=4

def sha(data): return hashlib.sha256(data).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()
def read_csv(b):return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
def require(x,msg):
    if not x:raise RuntimeError(msg)

def load_manifest():
    found=[]
    for p in INPUT.rglob("*"):
        if p.is_file() and p.name.startswith("CrackSAFE_P02_Source_Split_Safety_Correction_v2_PRIVATE") and p.name.endswith(".zip"):
            found.append(p)
    good=[p for p in found if sha_file(p)==EXPECTED_ZIP_SHA]
    require(len(good)<=1,"Multiple exact corrected manifests mounted; retain one.")
    if good:
        p=good[0]
        with zipfile.ZipFile(p) as z:
            require(z.testzip() is None,"Corrected manifest ZIP CRC failure")
            require(not any(".." in PurePosixPath(n).parts or n.startswith("/") for n in z.namelist()),"Unsafe ZIP members")
            data={name:z.read(name) for name in z.namelist() if not name.endswith("/")}
        origin=str(p)
    else:
        require(not found,"Corrected ZIP filename exists, but SHA-256 does not match the locked v2 artifact.")
        candidates=[]
        for p in INPUT.rglob("SHA256SUMS.sha256"):
            folder=p.parent
            if all((folder/n).is_file() for n in NAMES.values()):
                public=json.loads((folder/NAMES["summary"]).read_text())
                if public.get("origin_recovery_archive_sha256")=="3421d9024875df73b6d4c378e9aead21e9ebcc2255eade2b67536a2bd2dcd93d":
                    candidates.append(folder)
        require(len(candidates)==1,"Attach the exact corrected v2 ZIP as a PRIVATE Kaggle dataset. Expected one ZIP or one expanded folder, found "+str(len(candidates)))
        folder=candidates[0]
        data={p.name:p.read_bytes() for p in folder.iterdir() if p.is_file()}
        origin=str(folder)+" (expanded; internal SHA256SUMS verified)"
    require(all(n in data for n in NAMES.values()),"Incomplete corrected v2 manifest package")
    for line in data[NAMES["checksums"]].decode().splitlines():
        if not line.strip():continue
        h,n=line.split("  ",1)
        require(n in data and sha(data[n])==h,"Manifest member hash mismatch: "+n)
    sm=json.loads(data[NAMES["summary"]])
    require(sm.get("source_safe_provisional_train")==7697 and sm.get("source_safe_provisional_development")==945,
            "Corrected manifest counts changed")
    print("Manifest verified:",origin)
    return data,sm

def locate_roots(collections):
    matches=[]
    for base in INPUT.rglob("DeepCrack"):
        if base.is_dir() and all((base.parent/n).is_dir() for n in
            ["crack segmentation dataset","CRACK500 CrackTree200 GAPS384"]):
            matches.append(base.parent)
    matches=list(dict.fromkeys(str(p.resolve()) for p in matches))
    require(len(matches)==1,"Expected one Wall Crack-CP raw dataset root; found "+str(matches[:4]))
    root=Path(matches[0])
    require(all((root/c).is_dir() for c in collections),"Required collection missing under "+str(root))
    print("Raw dataset verified:",root)
    return {c:root/c for c in collections}

def safe_path(root,relative):
    t=relative.replace("\\","/")
    q=PurePosixPath(t)
    require(bool(t) and not q.is_absolute() and ".." not in q.parts and not re.match(r"^[A-Za-z]:",t),
            "Unsafe relative sample path")
    p=(root/Path(*q.parts)).resolve()
    require(p.is_relative_to(root.resolve()),"Sample escaped original dataset root")
    return p

def make_tiles(rec,root):
    ip=safe_path(root,rec["image_relative_path"])
    mp=safe_path(root,rec["mask_relative_path"])
    require(ip.is_file() and mp.is_file(),"Missing image/mask pair: "+rec["sample_id"])
    ib=ip.read_bytes();mb=mp.read_bytes()
    require(sha(ib)==rec["image_sha256"],"Image bytes hash mismatch")
    require(sha(mb)==rec["mask_sha256"],"Mask bytes hash mismatch")
    with Image.open(io.BytesIO(ib)) as f: rgb=f.convert("RGB").copy()
    with Image.open(io.BytesIO(mb)) as f:
        original_mode=f.mode
        gray=np.asarray(f.convert("L"),dtype=np.uint8).copy()
    require(rgb.size==(gray.shape[1],gray.shape[0]),"Image/mask dimensions differ")
    require(str(original_mode)==rec["mask_mode"],"Original mask mode changed")
    binary=gray>=128
    require(sha(binary.astype("uint8").tobytes())==rec["provisional_binary_mask_sha256"],
            "Binary mask checksum mismatch under locked >=128 rule")
    fg=float(binary.mean())
    mid=float(((gray>0)&(gray<255)).mean())
    img=rgb.copy();img.thumbnail((244,163),Image.Resampling.BILINEAR)
    mask=Image.fromarray(binary.astype("uint8")*255,"L").resize(img.size,Image.Resampling.NEAREST)
    npimg=np.asarray(img,dtype=np.float32).copy()
    m=np.asarray(mask,dtype=np.uint8)>127
    npimg[m]=npimg[m]*.50+np.array([255,0,0],dtype=np.float32)*.50
    overlay=Image.fromarray(npimg.clip(0,255).astype(np.uint8),"RGB")
    def panel(im):
        can=Image.new("RGB",(250,166),(28,31,36))
        can.paste(im,((250-im.width)//2,(166-im.height)//2))
        return can
    return (panel(img),panel(mask.convert("RGB")),panel(overlay)),fg,mid

def main():
    data,sm=load_manifest()
    tr=read_csv(data[NAMES["train"]])
    dv=read_csv(data[NAMES["dev"]])
    held=read_csv(data[NAMES["heldout"]])
    mix=read_csv(data[NAMES["mixed"]])
    require((len(tr),len(dv),len(held),len(mix))==(7697,945,3607,1210),"Candidate and quarantine row counts changed")
    roles={"train":tr,"development":dv,"heldout_metadata":held,"mixed_metadata":mix}
    def keys(rs,key):return {r[key] for r in rs}
    require(all(len(keys(rs,"sample_id"))==len(rs) for rs in roles.values()),
            "Duplicate sample IDs within one register")
    for key in ["image_sha256","normalized_parent_candidate","sample_id"]:
        for x,y in [("train","development"),("train","heldout_metadata"),
                    ("development","heldout_metadata"),("train","mixed_metadata"),
                    ("development","mixed_metadata")]:
            require(not (keys(roles[x],key)&keys(roles[y],key)),
                    f"Possible source leakage: {key} overlaps {x}/{y}")
    require(all(r.get("heldout_group_inference")=="False" for r in tr+dv),
            "Held-out flag inside candidate roles")
    require(all(r.get("mask_format_review")=="PASS_FORMAT_ONLY" for r in tr+dv),
            "Unexpected mask format-review state")
    print("Candidate metadata safety: PASS; no raw held-out/test images opened.")
    print("Train:",len(tr),"Development:",len(dv),"Source-test quarantine:",len(held),"Mixed quarantine:",len(mix))
    roots=locate_roots(keys(tr+dv,"collection"))
    by_role_source=defaultdict(lambda:defaultdict(dict))
    for role,rows in [("train",tr),("development",dv)]:
        for r in rows:
            by_role_source[r["source_hint"]][role].setdefault(r["normalized_parent_candidate"],r)
    selections=[]
    for source in sorted(by_role_source):
        for role,limit in [("train",TAKE_TRAIN_PER_SOURCE),("development",TAKE_DEV_PER_SOURCE)]:
            parent_map=by_role_source[source][role]
            parents=sorted(parent_map)
            rng=random.Random(f"{SEED}:{source}:{role}")
            chosen=rng.sample(parents,min(limit,len(parents)))
            selections.extend((source,role,parent_map[parent]) for parent in chosen)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=WORK/("CrackSAFE_P02_SOURCE_LABEL_VALIDATION_"+stamp)
    out.mkdir(parents=True,exist_ok=False)
    review=[]
    stats={}
    for source in sorted(by_role_source):
        rows=[(role,r) for src,role,r in selections if src==source]
        W=750; H=len(rows)*193+35
        canvas=Image.new("RGB",(W,H),(248,249,250))
        d=ImageDraw.Draw(canvas)
        d.text((7,10),source+" | RGB image       binary mask       mask overlay (RED)",
               fill=(0,0,0))
        failures=0; fractions=[];midfracs=[]
        for j,(role,r) in enumerate(rows):
            sample=r["sample_id"]
            y=35+j*193
            info={"sample_id":sample,"role":role,"source_hint":source,
                  "parent_proxy":r["normalized_parent_candidate"],
                  "image_sha256":r["image_sha256"],"mask_sha256":r["mask_sha256"],
                  "visual_decision":"PENDING_PRIVATE_REVIEW","foreground_polarity":"UNVERIFIED",
                  "mask_alignment":"UNVERIFIED","full_mask_completeness":"UNVERIFIED",
                  "notes":""}
            try:
                tiles,fg,mid=make_tiles(r,roots[r["collection"]])
                for k,tile in enumerate(tiles):canvas.paste(tile,(250*k,y))
                fractions.append(fg);midfracs.append(mid)
                info["foreground_fraction"]=round(fg,6)
                info["raw_midgray_fraction"]=round(mid,6)
                info["technical_status"]="PASS"
                d.text((5,y+169),role+" | "+sample+" | mask="+f"{100*fg:.2f}%",
                       fill=(10,10,10))
            except Exception as ex:
                failures+=1
                info["technical_status"]="FAILED"
                info["technical_error"]=str(ex)[:250]
                d.text((6,y+35),"VERIFY ERROR: "+str(ex)[:100],fill=(200,0,0))
            review.append(info)
        sheet=out/("SOURCE_"+re.sub(r"[^A-Za-z0-9_-]","_",source)+"_PRIVATE.png")
        canvas.save(sheet)
        stats[source]={"selected":len(rows),"train_selected":sum(role=="train" for role,_ in rows),
                       "dev_selected":sum(role=="development" for role,_ in rows),
                       "technical_errors":failures,
                       "mean_mask_fraction":round(sum(fractions)/len(fractions),6) if fractions else None,
                       "mean_midgray_fraction":round(sum(midfracs)/len(midfracs),6) if midfracs else None,
                       "sheet":sheet.name}
        print(source,":",len(rows),"representatives;",failures,"hash/mask errors; sheet:",sheet.name)
    fields=["sample_id","role","source_hint","parent_proxy","image_sha256","mask_sha256",
            "technical_status","technical_error","foreground_fraction","raw_midgray_fraction",
            "visual_decision","foreground_polarity","mask_alignment","full_mask_completeness","notes"]
    with (out/"SOURCE_MASK_REVIEW_WORKSHEET_PRIVATE.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(review)
    nerr=sum(x.get("technical_status")=="FAILED" for x in review)
    report={
        "protocol":"CrackSAFE-CP v3.3 / source-safe candidate mask audit",
        "status":"TECHNICAL_SAMPLE_PASS_VISUAL_REVIEW_PENDING" if nerr==0 else "TECHNICAL_SAMPLE_ERRORS",
        "manifest_bundle_sha256":EXPECTED_ZIP_SHA,
        "manifest_csv_sha256":{name:sha(data[NAMES[name]]) for name in ("train","dev","heldout","mixed")},
        "candidate_train":len(tr),"candidate_development":len(dv),
        "original_source_test_or_validation_quarantined":len(held),
        "ambiguous_cross_role_parent_quarantined":len(mix),
        "source_parent_proxy_train":len(keys(tr,"normalized_parent_candidate")),
        "source_parent_proxy_development":len(keys(dv,"normalized_parent_candidate")),
        "all_roles_metadata_image_parent_hash_disjoint":"PASS",
        "raw_heldout_or_calibration_images_opened":False,
        "representative_pairs":len(review),"representative_hash_mask_errors":nerr,
        "sources":stats,
        "scientific_independence_approved":False,
        "mask_semantics_approved":False,
        "permission_approved":False,
        "official_phase03_full_authorized":False
    }
    (out/"SOURCE_LABEL_VALIDATION_REPORT_PRIVATE.json").write_text(json.dumps(report,indent=2)+"\n")
    (out/"READ_FIRST_PRIVATE.md").write_text(
       "# CrackSAFE v3.3 — visual diagnostic only\n\n"
       "Open the SOURCE_*_PRIVATE.png sheets. In each row, check the RGB photograph,"
       " white mask area, and RED overlay. Verify that red means actual crack,"
       " that the mask is correctly aligned, and that no important crack pixels"
       " are missing. Record notes in the private worksheet if needed.\n\n"
       "No review decisions were invented. The proxy parent grouping is not verified"
       " site independence. Grayscale threshold >=128 is only a provisional mask interpretation."
       " Source permissions are not automatically resolved. Source test folders and"
       " calibration pixels were NOT accessed; only quarantine metadata IDs/hashes were compared.\n")
    members=sorted(p for p in out.iterdir() if p.is_file())
    checks="\n".join(sha_file(p)+"  "+p.name for p in members)+"\n"
    (out/"SHA256SUMS.sha256").write_text(checks)
    archive=WORK/("CrackSAFE_P02_SOURCE_LABEL_VALIDATION_PRIVATE_"+stamp+".zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(out.iterdir()):z.write(p,p.name)
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None,"Output ZIP CRC verification failure")
        for p in out.iterdir():
            require(sha(z.read(p.name))==sha_file(p),"Output ZIP member changed: "+p.name)
    outer=sha_file(archive)
    (WORK/(archive.name+".sha256")).write_text(outer+"  "+archive.name+"\n")
    print("\n===== CRACKSAFE P02 PRIVATE SOURCE-LABEL VALIDATION =====")
    print("Status:",report["status"])
    print("Manifest verified:",EXPECTED_ZIP_SHA)
    print("Train/development candidates:",len(tr),len(dv))
    print("Representatives checked:",len(review),"errors:",nerr)
    print("Official Phase03 FULL:", "BLOCKED; separate scientific gates")
    print("ZIP:",archive)
    print("ZIP SHA256:",outer)
    print("SIDECAR:",WORK/(archive.name+".sha256"))

main()
