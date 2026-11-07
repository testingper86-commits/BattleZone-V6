#!/usr/bin/env python3
"""Restore safe frustum culling for static terrain and instanced vegetation."""
from pathlib import Path
import sys
MARKER="BATTLEZONE_V6_FRUSTUM_CULLING_V1"
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
index_files=list(root.rglob("app/src/main/assets/www/index.html"))
model_files=list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(index_files)!=1 or len(model_files)!=1: raise SystemExit(f"Expected one index.html and models.js, found {len(index_files)} and {len(model_files)}")
ip,mp=index_files[0],model_files[0]
html=ip.read_text(encoding="utf-8"); models=mp.read_text(encoding="utf-8")
if MARKER in html or MARKER in models:
    if MARKER not in html or MARKER not in models or "computeBoundingSphere();grass.frustumCulled=true" not in html or "o.frustumCulled=!(o.isSkinnedMesh||o.isInstancedMesh)" not in models:
        raise SystemExit("Frustum-culling marker exists but one or more culling fixes are incomplete")
    print(MARKER+" already applied"); raise SystemExit(0)
replacements=[
("gr.material.needsUpdate=true;gr.frustumCulled=false}","gr.material.needsUpdate=true;gr.geometry.computeBoundingSphere();gr.frustumCulled=true}"),
("L.frustumCulled=false;T.frustumCulled=false;S.add(L,T);solid.push(T)};","L.computeBoundingSphere();T.computeBoundingSphere();L.frustumCulled=true;T.frustumCulled=true;L.castShadow=false;L.receiveShadow=!LQ;T.castShadow=!LQ;T.receiveShadow=!LQ;S.add(L,T);solid.push(T)};"),
("grass.count=placed;grass.frustumCulled=false;S.add(grass)}","grass.count=placed;grass.computeBoundingSphere();grass.frustumCulled=true;S.add(grass)}"),
]
for old,new in replacements:
    if html.count(old)!=1: raise SystemExit(f"Expected one HTML culling anchor, found {html.count(old)}: {old[:70]}")
    html=html.replace(old,new,1)
models_anchor="root.traverse(o=>{if(o.isMesh)o.frustumCulled=false});"
if models.count(models_anchor)!=1: raise SystemExit("Expected one global model culling override")
models=models.replace(models_anchor,"root.traverse(o=>{if(o.isMesh)o.frustumCulled=!(o.isSkinnedMesh||o.isInstancedMesh)});",1)
html=html.replace("const R=new THREE.WebGLRenderer", "/* "+MARKER+" */const R=new THREE.WebGLRenderer",1)
models="// "+MARKER+"\\n"+models
if MARKER not in html or MARKER not in models: raise SystemExit("Culling marker insertion failed")
ip.write_text(html,encoding="utf-8"); mp.write_text(models,encoding="utf-8")
print(MARKER+" applied",ip,mp)
