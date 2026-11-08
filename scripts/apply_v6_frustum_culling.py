#!/usr/bin/env python3
"""Enable safe frustum culling without calling unsupported InstancedMesh APIs."""
from pathlib import Path
import sys
MARKER="BATTLEZONE_V6_FRUSTUM_CULLING_V2"
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
index_files=list(root.rglob("app/src/main/assets/www/index.html"))
model_files=list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(index_files)!=1 or len(model_files)!=1:
    raise SystemExit(f"Expected one index.html and models.js, found {len(index_files)} and {len(model_files)}")
ip,mp=index_files[0],model_files[0]
html=ip.read_text(encoding="utf-8"); models=mp.read_text(encoding="utf-8")
helper="function bzPrepareInstanceBoundsSafe(mesh){if(!mesh||!mesh.geometry)return;if(typeof mesh.geometry.computeBoundingSphere==='function')mesh.geometry.computeBoundingSphere();if(typeof mesh.computeBoundingSphere==='function'){mesh.computeBoundingSphere();mesh.frustumCulled=true}else{mesh.frustumCulled=false}};"
if "function bzPrepareInstanceBoundsSafe(mesh)" not in html:
    anchor="const R=new THREE.WebGLRenderer"
    if html.count(anchor)!=1: raise SystemExit("Main renderer anchor is not unique for safe instance-bounds helper")
    html=html.replace(anchor,helper+"\n"+anchor,1)
# Repair both clean-source and previously generated forms. Unsupported instance methods are
# never invoked unless feature-detected inside bzPrepareInstanceBoundsSafe.
html=html.replace("L.computeBoundingSphere();T.computeBoundingSphere();L.frustumCulled=true;T.frustumCulled=true;","bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);")
html=html.replace("L.frustumCulled=false;T.frustumCulled=false;","bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);")
html=html.replace("bzPrepareInstanceBounds(L);bzPrepareInstanceBounds(T);","bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);")
html=html.replace("grass.computeBoundingSphere();grass.frustumCulled=true;","bzPrepareInstanceBoundsSafe(grass);")
html=html.replace("grass.frustumCulled=false;","bzPrepareInstanceBoundsSafe(grass);")
# Existing tree setup and grass creation are expected to route through the safe helper.
if "bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);" not in html:
    tree_anchor="L.frustumCulled=false;T.frustumCulled=false;S.add(L,T);"
    if html.count(tree_anchor)==1: html=html.replace(tree_anchor,"bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);S.add(L,T);",1)
if "grass.count=placed;" in html and "bzPrepareInstanceBoundsSafe(grass);" not in html:
    for old in ("grass.count=placed;grass.computeBoundingSphere();grass.frustumCulled=true;S.add(grass)","grass.count=placed;grass.frustumCulled=false;S.add(grass)"):
        if old in html: html=html.replace(old,"grass.count=placed;bzPrepareInstanceBoundsSafe(grass);S.add(grass)",1); break
if "bzPrepareInstanceBoundsSafe(grass);" not in html:
    raise SystemExit("Grass instance creation is not protected by safe bounds helper")
if "grass.computeBoundingSphere()" in html or "L.computeBoundingSphere();T.computeBoundingSphere();" in html:
    raise SystemExit("Unsupported direct InstancedMesh bounds call remains")
models_anchor="root.traverse(o=>{if(o.isMesh)o.frustumCulled=false});"
if models_anchor in models:
    models=models.replace(models_anchor,"root.traverse(o=>{if(o.isMesh)o.frustumCulled=!(o.isSkinnedMesh||o.isInstancedMesh)});",1)
if MARKER not in html: html=html.replace("const R=new THREE.WebGLRenderer","/* "+MARKER+" */const R=new THREE.WebGLRenderer",1)
if MARKER not in models: models="// "+MARKER+"\n"+models
if "bzPrepareInstanceBoundsSafe(grass);" not in html or "typeof mesh.computeBoundingSphere==='function'" not in html:
    raise SystemExit("Safe culling helper insertion failed")
ip.write_text(html,encoding="utf-8"); mp.write_text(models,encoding="utf-8")
print(MARKER+" applied",ip,mp)
