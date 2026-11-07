#!/usr/bin/env python3
"""Regression checks for opt-in local-only renderer diagnostics."""
from pathlib import Path
import re,subprocess,sys,tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit("Expected one game index.html")
h=files[0].read_text(encoding="utf-8")
checks={
 "diagnostics marker": "BATTLEZONE_V6_RENDER_DIAGNOSTICS_V1" in h,
 "disabled unless explicitly requested": "new URLSearchParams(location.search).get('bzdiag')==='1'" in h,
 "overlay created only when enabled": "const BZ_DIAG_NODE=BZ_DIAG_ENABLED?" in h,
 "FPS and frame time exposed": "FPS '+fps.toFixed(1)+' | frame '+BZ_DIAG_FRAME_MS.toFixed(1)" in h,
 "renderer draw and geometry metrics exposed": "rr.calls" in h and "rr.triangles" in h and "mm.geometries" in h and "mm.textures" in h,
 "device and quality metrics exposed": "R.getPixelRatio()" in h and "R.capabilities.maxTextureSize" in h and "navigator.deviceMemory" in h and "navigator.hardwareConcurrency" in h,
 "main render loop feeds diagnostics": "_l0(n);if(window.BZRenderDiagnostics)window.BZRenderDiagnostics.tick(n);" in h,
 "no network telemetry APIs in diagnostics": not any(token in h[h.find("/* BATTLEZONE_V6_RENDER_DIAGNOSTICS_V1 */"):h.find("/* BATTLEZONE_V6_RENDER_DIAGNOSTICS_V1 */")+2600] for token in ("fetch(","XMLHttpRequest","WebSocket","sendBeacon")),
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Render diagnostics regression failed")
pos=h.find("const R=new THREE.WebGLRenderer"); script_open=h.rfind("<script",0,pos); script_start=h.find(">",script_open)+1; script_end=h.find("</script>",pos); main=h[script_start:script_end] if pos>=0 and script_open>=0 and script_end>=0 else None

if not main: raise SystemExit("Main inline script not found")
with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as f: f.write(main); p=f.name
try:
 r=subprocess.run(["node","--check",p],capture_output=True,text=True)
 if r.returncode: print(r.stderr); raise SystemExit(r.returncode)
finally: Path(p).unlink(missing_ok=True)
print("RENDER_DIAGNOSTICS_TESTS_OK")
