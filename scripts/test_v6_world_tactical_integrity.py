#!/usr/bin/env python3
"""Regression gate for world occlusion, weapon aim and vehicle coordinate integrity."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
s=paths[0].read_text(encoding='utf-8')
checks={
'cylinder cover raycast blockers':'S.add(m);solid.push(m);return m}' in s,
'broadleaf trunk occlusion':'S.add(trunk);solid.push(trunk);trunk.castShadow' in s,
'instanced forest trunk occlusion':'S.add(L,T);solid.push(T)' in s,
'grouped prop child meshes registered':'g.traverse(o=>{if(o.isMesh)solid.push(o)})' in s,
'deadfall occlusion':'obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)' in s,
'allocation-free tactical raycast':'ray.intersectObjects(solid,false).length===0' in s and 'solid.filter(' not in s,
'world marker present':'BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1' in s,
'attachment multipliers reduce spread':'const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);' in s,
'boolean-as-spread defect removed':'const sp_=P.grip||P.comp?.005:.01;' not in s,
'player follows clamped vehicle transform':'g.rotation.y=u.yaw;P.x=g.position.x;P.z=g.position.z;fx=fz=0;' in s,
'vehicle exit collision and world clamp':'const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);' in s,
'combat marker present':'BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1' in s,
}
for name,ok in checks.items(): print(('PASS ' if ok else 'FAIL ')+name)
if not all(checks.values()): raise SystemExit(f'{sum(not x for x in checks.values())} integrity checks failed')
print(f'WORLD_TACTICAL_INTEGRITY_OK checks={len(checks)}')
