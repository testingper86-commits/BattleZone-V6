#!/usr/bin/env python3
"""Regression checks for restored original operator appearance and legacy squad tactics."""
from pathlib import Path
import re,subprocess,sys,tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve(); files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected one game index.html, found {len(files)}")
h=files[0].read_text(encoding="utf-8")
checks={
 "legacy character/tactics restoration marker":"BATTLEZONE_V6_LEGACY_CHARACTER_TACTICS_V1" in h,
 "original articulated character constructor retained":"function mkScout(" in h and "function animSc(" in h,
 "selected operator identity uses equipped profile":"function bzSelectedCharacterName()" in h and "charName:bzSelectedCharacterName()" in h,
 "skin selector updates full operator material palette":"sc.lookMaterials={skin:mS,hair:mH,pants:mP,boot:mB,shirt:mSh,jacket:mJ,pack:mPack}" in h,
 "profile appearance updates are applied to preview and player":"window.lobSc,window.pmS" in h and "window.BZRefreshCharacterAppearance()" in h,
 "profile save refreshes operator appearance":"function save(){put('bzProfile',profile);refreshTop();if(window.BZRefreshCharacterAppearance)" in h,
 "legacy regroup formation offsets preserved":"let gx=px+Math.cos(u.off*2)*4,gz=pz+Math.sin(u.off*2)*4" in h,
 "legacy allies respond to the four original tactical orders":"const bzOrder=window.BZSquadOrders?.get()||'regroup'" in h,
 "focus order assigns one shared enemy to the squad":"if(window.BZSquadOrders?.get()==='focus')" in h and "if(focused)en=focused" in h,
 "flank order creates alternating enemy-side positions":"role=(bzOrder==='flank'?'flank'" in h and "const flankAngle=ang+side*1.12" in h,
 "hold order preserves each ally's current position":"if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0;}" in h,
 "focus fire retains coordinated target assignment":"if(window.BZSquadOrders?.get()==='focus')" in h and "if(focused)en=focused" in h,
 "line-of-sight prevents shooting through cover":"hasClearShot(a.position.x,a.position.y+1.15" in h,
 "automatic teammate revive radius is restored":"if(P.down&&follow<4){u.reviveT=(u.reviveT||0)+dt" in h,
}
models_files=list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(models_files)!=1: raise SystemExit(f"Expected one models.js, found {len(models_files)}")
models=models_files[0].read_text(encoding="utf-8")
char_data=h.find("const BZ_CHAR_DATA={")
char_ready=h.find("window.BZ_CHAR_DATA_READY=true;",char_data)
refresh_fn=h.find("function bzRefreshCharacterAppearance(){")
refresh_guard=h.find("if(!window.BZ_CHAR_DATA_READY)return '';",refresh_fn)
checks.update({
 "character readiness is reset before any early UI refresh":h.find("window.BZ_CHAR_DATA_READY=false;")>=0 and h.find("window.BZ_CHAR_DATA_READY=false;")<h.find("function updCur(){"),
 "character readiness is published only after profile data and PLOOK initialize":char_data>=0 and h.find("const PLOOK=")>char_data and char_ready>h.find("const PLOOK=") and refresh_fn>=0 and refresh_guard>refresh_fn,
 "pickup registry is published only after pickup initialization": "window.BZPickups=pk;" in h and h.find("window.BZPickups=pk;")>h.find("const pk=[]"),
 "bot and ally arrays are published after initialization": "window.BZActors=Object.freeze({bots,allies:al});" in h,
 "match-state bridge is initialized after started binding": "window.BZMatchRuntime=Object.freeze({isStarted:()=>!!started,allies:()=>al});" in h,
 "tactical UI reads initialized actor and match registries": "window.BZActors?.bots" in h and "window.BZMatchRuntime?.isStarted()" in h,
 "model loader never uses TDZ-sensitive typeof bots checks": "typeof bots" not in models and "window.BZActors?.bots" in models and "window.BZActors||{}" in models,
})
for label,ok in checks.items(): print(("PASS " if ok else "FAIL ")+label)
if not all(checks.values()): raise SystemExit("Legacy character/tactics regression failed")
blocks=re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>",h,re.I|re.S)
main=next((x for x in blocks if "const R=new THREE.WebGLRenderer" in x),None)
if main is None: raise SystemExit("Main game inline script not found")
with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as f: f.write(main);name=f.name
try:
 r=subprocess.run(["node","--check",name],capture_output=True,text=True)
 if r.returncode: print(r.stderr);raise SystemExit(r.returncode)
finally: Path(name).unlink(missing_ok=True)
r=subprocess.run(["node","--check",str(models_files[0])],capture_output=True,text=True)
if r.returncode: print(r.stderr);raise SystemExit(r.returncode)
print("LEGACY_CHARACTER_TACTICS_TESTS_OK")
