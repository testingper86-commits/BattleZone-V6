#!/usr/bin/env python3
"""Regression checks for safe static-geometry culling and instanced tree shadows."""
from pathlib import Path
import sys,subprocess
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
idx=list(root.rglob("app/src/main/assets/www/index.html")); mods=list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(idx)!=1 or len(mods)!=1: raise SystemExit("Expected one game index.html and models.js")
h=idx[0].read_text(encoding="utf-8"); m=mods[0].read_text(encoding="utf-8")
checks={
 "culling marker in game and model runtime": "BATTLEZONE_V6_FRUSTUM_CULLING_V2" in h and "BATTLEZONE_V6_FRUSTUM_CULLING_V2" in m,
 "instanced tree leaf/trunk bounds prepared safely": "bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);" in h,
 "instanced bounds API is feature-detected": "typeof mesh.computeBoundingSphere==='function'" in h,
 "unsupported instanced bounds safely disable culling": "else{mesh.frustumCulled=false}" in h,
 "grass never calls unsupported InstancedMesh method": "bzPrepareInstanceBoundsSafe(grass);" in h and "grass.computeBoundingSphere()" not in h,
 "InstancedMesh method is feature-detected": "typeof mesh.computeBoundingSphere==='function'" in h,
 "unsupported instance-bound API is never called directly": "L.computeBoundingSphere();T.computeBoundingSphere();" not in h,
 "unsupported instance bounds fall back to safe no-cull": "else{mesh.frustumCulled=false}" in h,
 "high-quality tree trunks cast shadows": "T.castShadow=!LQ;T.receiveShadow=!LQ" in h,
 "tree leaves receive but do not cast shadows": "L.castShadow=false;L.receiveShadow=!LQ" in h,
 "instanced grass bounds use safe feature detection": "bzPrepareInstanceBoundsSafe(grass);" in h and "grass.computeBoundingSphere()" not in h,
 "skinned actors retain conservative no-cull behavior": "o.frustumCulled=!(o.isSkinnedMesh||o.isInstancedMesh)" in m,
 "global imported-mesh culling disable removed": "root.traverse(o=>{if(o.isMesh)o.frustumCulled=false})" not in m,
 "terrain/grass/forest culling uses safe bounds": "bzPrepareInstanceBoundsSafe(grass);" in h and "bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);" in h,
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Frustum culling regression failed")
r=subprocess.run(["node","--check",str(mods[0])],capture_output=True,text=True)
if r.returncode: print(r.stderr); raise SystemExit(r.returncode)
import re,tempfile
blocks=re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>",h,re.I|re.S)
main_block=next((block for block in blocks if "const R=new THREE.WebGLRenderer" in block),None)
if main_block is None: raise SystemExit("Main game inline script not found for syntax validation")
with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as stream:
    stream.write(main_block); inline_path=stream.name
try:
    r=subprocess.run(["node","--check",inline_path],capture_output=True,text=True)
    if r.returncode: print(r.stderr); raise SystemExit(r.returncode)
finally: Path(inline_path).unlink(missing_ok=True)
print("FRUSTUM_CULLING_TESTS_OK")
