#!/usr/bin/env python3
"""Regression checks for third-person camera collision and responsive lobby rendering."""
from pathlib import Path
import re,subprocess,sys,tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one index.html, found {len(files)}")
h=files[0].read_text(encoding="utf-8")
checks={
 "character camera repair marker":"BATTLEZONE_V6_CHARACTER_CAMERA_REPAIR_V1" in h,
 "camera raycaster is initialized":"const bzCameraRay=new THREE.Raycaster()" in h,
 "third-person camera checks solid geometry":"bzCameraRay.intersectObjects(solid,false)[0]" in h,
 "camera stays outside hit geometry":"bzCamHit.distance-.28" in h,
 "camera retains a minimum collision distance":"Math.max(.2,bzCamHit.distance-.28)" in h,
 "camera remains above sampled terrain":"gS(bzCamDesired.x,bzCamDesired.z,bzCamDesired.y)+.28" in h,
 "lobby renderer follows actual container size":"$('char').clientWidth" in h and "$('char').clientHeight" in h,
 "lobby renderer uses capped device pixel ratio":"Math.min(window.devicePixelRatio||1,1.5)" in h,
 "lobby camera is framed closer":"lc.position.set(0,1.05,3.8)" in h,
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Character camera regression failed")
blocks=re.findall("<script"+chr(92)+"b(?![^>]*"+chr(92)+"bsrc=)[^>]*>(.*?)</script>",h,re.I|re.S)
main=next((b for b in blocks if "const R=new THREE.WebGLRenderer" in b),None)
if main is None: raise SystemExit("Main game inline script not found")
with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as f: f.write(main); path=f.name
try:
 r=subprocess.run(["node","--check",path],capture_output=True,text=True)
 if r.returncode: print(r.stderr); raise SystemExit(r.returncode)
finally: Path(path).unlink(missing_ok=True)
print("CHARACTER_CAMERA_REPAIR_TESTS_OK")
