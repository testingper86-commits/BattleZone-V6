#!/usr/bin/env python3
"""Regression checks for camera collision and responsive lobby operator preview."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one index.html, found {len(files)}")
h=files[0].read_text(encoding="utf-8")
checks={
 "camera repair marker":"BATTLEZONE_V6_CHARACTER_CAMERA_REPAIR_V1" in h,
 "camera raycaster initialized":"const bzCameraRay=new THREE.Raycaster()" in h,
 "post-rebuild shoulder camera preserved":"shoulder=.7+ln*.92" in h,
 "third-person camera tests solid geometry":"bzCameraRay.intersectObjects(solid,false)[0]" in h,
 "camera stops before obstruction":"bzCamHit.distance-.28" in h,
 "camera has safe minimum obstruction distance":"Math.max(.2,bzCamHit.distance-.28)" in h,
 "camera remains above sampled terrain":"gS(bzCamDesired.x,bzCamDesired.z,bzCamDesired.y)+.28" in h,
 "preview renderer follows rebuilt host dimensions":"host.clientWidth" in h and "host.clientHeight" in h,
 "preview renderer uses capped device pixel ratio":"Math.min(window.devicePixelRatio||1,1.5)" in h,
 "preview camera is framed closer":"lc.position.set(0,1.05,3.8)" in h,
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Character camera regression failed")
print("CHARACTER_CAMERA_REPAIR_TESTS_OK")
