#!/usr/bin/env python3
"""Enforce world occlusion, weapon aim and vehicle coordinate integrity."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
p=paths[0]; s=p.read_text(encoding='utf-8')
world='BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1'; combat='BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1'
if world in s and combat in s:
    print('WORLD_AND_COMBAT_INTEGRITY_ALREADY_APPLIED'); raise SystemExit(0)
def sub(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected one exact source anchor, found {n}')
    s=s.replace(old,new,1)
if world not in s:
    pairs=[
("function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);return m}","function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);solid.push(m);return m}",'cylinder cover'),
("trunk.position.set(x,1.5,z);S.add(trunk);trunk.castShadow=!LQ;","trunk.position.set(x,1.5,z);S.add(trunk);solid.push(trunk);trunk.castShadow=!LQ;",'broadleaf trunk'),
("L.frustumCulled=false;T.frustumCulled=false;S.add(L,T)","L.frustumCulled=false;T.frustumCulled=false;S.add(L,T);solid.push(T)",'instanced forest trunk'),
("function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k))obs.push({x,z,w:1.4,d:1.4});return g}","function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k)){obs.push({x,z,w:1.4,d:1.4});g.traverse(o=>{if(o.isMesh)solid.push(o)})}return g}",'grouped props'),
("t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});for(let k=0;k<3;k++)","t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)",'deadfall'),
("function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}","function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist)||dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}",'finite tactical raycast')]
    for a,b,label in pairs: sub(a,b,label)
    sub('</html>',f'<!-- {world} -->\n</html>','world marker')
if combat not in s:
    sub('const sp_=P.grip||P.comp?.005:.01;','const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);','aim spread')
    sub('g.rotation.y=u.yaw;P.x=r[0];P.z=r[1];fx=fz=0;','g.rotation.y=u.yaw;P.x=g.position.x;P.z=g.position.z;fx=fz=0;','vehicle/player sync')
    sub('P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;[P.x,P.z]=hit(P.x,P.z,.5,0);gun.visible=true;','P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);gun.visible=true;','vehicle exit clamp')
    sub('</html>',f'<!-- {combat} -->\n</html>','combat marker')
p.write_text(s,encoding='utf-8'); print('WORLD_AND_COMBAT_INTEGRITY_APPLIED',p)
