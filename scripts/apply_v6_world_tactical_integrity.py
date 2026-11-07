#!/usr/bin/env python3
"""Make every gameplay collision obstacle participate in tactical line-of-sight."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
paths = list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths) != 1:
    raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
path = paths[0]
source = path.read_text(encoding='utf-8')
marker = 'BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1'
if marker in source:
    print('WORLD_TACTICAL_INTEGRITY_ALREADY_APPLIED')
    raise SystemExit(0)
def replace_once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one exact source anchor, found {count}')
    source = source.replace(old, new, 1)
replace_once(
 "function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);return m}",
 "function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);solid.push(m);return m}",
 'shared cylinder collision/occlusion registration')
replace_once(
 "trunk.position.set(x,1.5,z);S.add(trunk);trunk.castShadow=!LQ;",
 "trunk.position.set(x,1.5,z);S.add(trunk);solid.push(trunk);trunk.castShadow=!LQ;",
 'broadleaf tree trunk line-of-sight registration')
replace_once(
 "L.frustumCulled=false;T.frustumCulled=false;S.add(L,T)",
 "L.frustumCulled=false;T.frustumCulled=false;S.add(L,T);solid.push(T)",
 'instanced forest trunk line-of-sight registration')
replace_once(
 "function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k))obs.push({x,z,w:1.4,d:1.4});return g}",
 "function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k)){obs.push({x,z,w:1.4,d:1.4});g.traverse(o=>{if(o.isMesh)solid.push(o)})}return g}",
 'collidable grouped prop mesh registration')
replace_once(
 "t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});for(let k=0;k<3;k++)",
 "t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)",
 'environment deadfall line-of-sight registration')
replace_once(
 "function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}",
 "function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist)||dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}",
 'finite and allocation-free tactical raycast')
replace_once('</html>', '<!-- '+marker+' -->\n</html>', 'world tactical integrity marker')
path.write_text(source, encoding='utf-8')
print('WORLD_TACTICAL_INTEGRITY_APPLIED', path)
