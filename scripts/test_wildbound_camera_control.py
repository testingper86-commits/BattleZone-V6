#!/usr/bin/env python3
"""Regression checks for WILDBOUND camera-relative mobile controls."""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
matches = list(root.rglob("app/src/main/assets/www/js/wildbound/rendering/runtime.js"))
if len(matches) != 1:
    raise SystemExit(f"Expected one WILDBOUND runtime.js, found {len(matches)}")
runtime = matches[0]
source = runtime.read_text(encoding="utf-8")
checks = {
    "camera state is independent from player facing": "cameraYaw:Math.PI,cameraHeight:3.1" in source,
    "camera initializes for every hunt": "game.cameraYaw=Math.PI;game.cameraHeight=3.1" in source,
    "movement is relative to camera yaw": "const yaw=game.cameraYaw,cos=Math.cos(yaw),sin=Math.sin(yaw)" in source,
    "movement vector is normalized and transformed": "moveX=x*cos-z*sin,moveZ=-x*sin-z*cos" in source,
    "camera follow uses orbit yaw": "Math.sin(game.cameraYaw)*5" in source and "Math.cos(game.cameraYaw)*5" in source,
    "vertical camera orbit is clamped": "Math.max(2.2,Math.min(5.2,game.cameraHeight+dy*.012))" in source,
    "touch and mouse drag update camera orbit": "game.cameraYaw-=(dx)*.006" in source,
    "pointer cancellation releases camera capture state": "pointercancel" in source and "lostpointercapture" in source,
    "window focus loss clears held controls": "window.addEventListener('blur'" in source and "game.input.x=0;game.input.z=0" in source,
    "patch is identifiable and idempotent": "WILDBOUND_CAMERA_RELATIVE_CONTROL_V1" in source,
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL"), name)
if not all(checks.values()):
    raise SystemExit("WILDBOUND_CAMERA_CONTROL_REGRESSION_FAILED")
result = subprocess.run(["node", "--check", str(runtime)], capture_output=True, text=True)
if result.returncode:
    raise SystemExit("JavaScript syntax failed:\n" + result.stderr)
print("PASS runtime JavaScript syntax")
print("WILDBOUND_CAMERA_CONTROL_REGRESSION_OK", len(checks) + 1, "checks")
