#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, secrets, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES=32768
REQUIRED_SECTIONS=("## Handoff Metadata","## Active Objective","## Definition of Done","## Next Exact Action")
SECRET_PATTERNS=(re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*[^<\s][^\s]{7,}"))

def run_git(cwd:Path,*args:str)->tuple[int,str,str]:
    p=subprocess.run(["git","-C",str(cwd),*args],text=True,capture_output=True,check=False)
    return p.returncode,p.stdout.strip(),p.stderr.strip()

def real(p:Path)->Path: return Path(os.path.realpath(p))

def repo_identity(cwd:Path)->dict:
    cwd=real(cwd)
    rc,top,_=run_git(cwd,"rev-parse","--show-toplevel")
    if rc!=0:
        key=hashlib.sha256(str(cwd).encode()).hexdigest()[:12]
        return {"is_git":False,"invocation_directory":str(cwd),"worktree_root":str(cwd),"repository_family":str(cwd),"project_name":cwd.name,"project_key":f"{cwd.name}-{key}","branch":None,"head":None,"status":[],"common_dir":None}
    worktree=real(Path(top))
    rc,common,_=run_git(worktree,"rev-parse","--git-common-dir")
    common_path=Path(common)
    if not common_path.is_absolute(): common_path=worktree/common_path
    common_real=real(common_path)
    family_source=str(common_real)
    key=hashlib.sha256(family_source.encode()).hexdigest()[:12]
    name=common_real.parent.name if common_real.name == ".git" else common_real.name
    rc,branch,_=run_git(worktree,"branch","--show-current")
    rc2,head,_=run_git(worktree,"rev-parse","HEAD")
    rc3,status,_=run_git(worktree,"status","--porcelain=v1","-uall")
    return {"is_git":True,"invocation_directory":str(cwd),"worktree_root":str(worktree),"repository_family":family_source,"common_dir":str(common_real),"project_name":name,"project_key":f"{name}-{key}","branch":branch or "DETACHED","head":head if rc2==0 else None,"status":status.splitlines() if rc3==0 and status else []}

def storage_root(state:dict)->Path:
    base=Path(os.environ.get("CLAUDE_SESSION_HANDOFFS",Path.home()/".claude/session-handoffs"))
    return base/state["project_key"]

def sha256_file(path:Path)->str:
    h=hashlib.sha256();
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""): h.update(chunk)
    return h.hexdigest()

def atomic_write(path:Path,data:bytes,mode:int=0o600)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.chmod(tmp,mode); os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def cmd_collect(a):
    state=repo_identity(Path(a.cwd)); state["session_id"]=a.session_id; state["collected_at"]=datetime.now(timezone.utc).isoformat(); state["storage_directory"]=str(storage_root(state)); print(json.dumps(state,indent=2)); return 0

def cmd_draft(a):
    state=repo_identity(Path(a.cwd)); d=storage_root(state)/"drafts"; d.mkdir(parents=True,exist_ok=True); fd,p=tempfile.mkstemp(prefix=f"{a.kind}-",suffix=".md",dir=d); os.close(fd); print(p); return 0

def validate(path:Path)->list[str]:
    errs=[]
    if not path.is_file(): return ["file does not exist"]
    data=path.read_bytes()
    if len(data)>MAX_BYTES: errs.append(f"file exceeds {MAX_BYTES} bytes")
    text=data.decode("utf-8",errors="replace")
    for sec in REQUIRED_SECTIONS:
        if sec not in text: errs.append(f"missing section: {sec}")
    for pat in SECRET_PATTERNS:
        if pat.search(text): errs.append("possible secret or private key detected")
    return errs

def cmd_validate(a):
    errs=validate(Path(a.file))
    if errs:
        for e in errs: print(e,file=sys.stderr)
        return 1
    print("VALID"); return 0

def cmd_publish(a):
    source=Path(a.source); errs=validate(source)
    if errs:
        for e in errs: print(e,file=sys.stderr)
        return 1
    before=repo_identity(Path(a.cwd)); root=storage_root(before); archive=root/"archive"; archive.mkdir(parents=True,exist_ok=True)
    hid=f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(6)}"
    content=source.read_bytes(); content_hash=hashlib.sha256(content).hexdigest(); now=datetime.now(timezone.utc).isoformat()
    archive_md=archive/f"{hid}.md"; archive_json=archive/f"{hid}.json"; current_md=root/"CURRENT.md"; current_json=root/"CURRENT.json"; latest=root/"LATEST.json"
    metadata={"schema_version":2,"handoff_id":hid,"generated_at":now,"source_session_id":a.session_id,"label":a.label or None,"project_key":before["project_key"],"repository_family":before["repository_family"],"invocation_directory":before["invocation_directory"],"active_worktree":before["worktree_root"],"branch":before["branch"],"head":before["head"],"status":before["status"],"content_sha256":content_hash,"archive_path":str(archive_md),"current_path":str(current_md)}
    atomic_write(archive_md,content); atomic_write(archive_json,json.dumps(metadata,indent=2).encode()); atomic_write(current_md,content); atomic_write(current_json,json.dumps(metadata,indent=2).encode()); atomic_write(latest,json.dumps(metadata,indent=2).encode())
    after=repo_identity(Path(a.cwd))
    problems=[]
    if before["worktree_root"]!=after["worktree_root"] or before["head"]!=after["head"] or before["status"]!=after["status"]: problems.append("repository state changed during publication")
    if sha256_file(current_md)!=content_hash or sha256_file(archive_md)!=content_hash: problems.append("published content hash mismatch")
    located=json.loads(current_json.read_text())
    if located.get("handoff_id")!=hid: problems.append("current pointer does not reference published handoff")
    if problems:
        print("; ".join(problems),file=sys.stderr); return 2
    receipt={**metadata,"status":"PUBLISHED_AND_VERIFIED"}; print(json.dumps(receipt,indent=2)); return 0

def cmd_locate(a):
    state=repo_identity(Path(a.cwd)); root=storage_root(state); latest=root/"LATEST.json"; current=root/"CURRENT.md"; meta=root/"CURRENT.json"
    if not current.is_file() or not meta.is_file() or not latest.is_file(): return 1
    try:
        m=json.loads(meta.read_text()); l=json.loads(latest.read_text())
    except Exception as e:
        print(f"invalid handoff metadata: {e}",file=sys.stderr); return 2
    problems=[]
    if m.get("handoff_id")!=l.get("handoff_id"): problems.append("CURRENT and LATEST handoff IDs differ")
    if sha256_file(current)!=m.get("content_sha256"): problems.append("CURRENT content hash mismatch")
    ap=Path(m.get("archive_path", ""))
    if not ap.is_file() or sha256_file(ap)!=m.get("content_sha256"): problems.append("archive missing or hash mismatch")
    if m.get("repository_family")!=state["repository_family"]: problems.append("repository-family mismatch")
    if problems:
        print("; ".join(problems),file=sys.stderr); return 2
    out={**m,"located_path":str(current),"selection_method":"repository-family latest verified handoff","current_invocation_directory":state["invocation_directory"],"current_worktree":state["worktree_root"],"current_head":state["head"],"freshness":"CURRENT" if m.get("active_worktree")==state["worktree_root"] and m.get("head")==state["head"] else "DRIFT_REQUIRES_REVIEW"}
    print(json.dumps(out,indent=2)); return 0

def main():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="cmd",required=True)
    for n in ("collect","draft-path","locate"):
        q=sp.add_parser(n); q.add_argument("--cwd",required=True); q.add_argument("--kind",default="handoff"); q.add_argument("--session-id",default="")
    q=sp.add_parser("validate"); q.add_argument("--kind",default="handoff"); q.add_argument("--file",required=True)
    q=sp.add_parser("publish"); q.add_argument("--kind",default="handoff"); q.add_argument("--source",required=True); q.add_argument("--cwd",required=True); q.add_argument("--session-id",default=""); q.add_argument("--label",default="")
    a=p.parse_args(); funcs={"collect":cmd_collect,"draft-path":cmd_draft,"validate":cmd_validate,"publish":cmd_publish,"locate":cmd_locate}; raise SystemExit(funcs[a.cmd](a))
if __name__=="__main__": main()
