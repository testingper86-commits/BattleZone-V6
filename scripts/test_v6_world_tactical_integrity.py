#!/usr/bin/env python3
"""Regression gate for collision and tactical line-of-sight consistency."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
paths = list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths) != 1:
    raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
s = paths[0].read_text(encoding='utf-8')
checks = {
 'shared cylinders are raycast blockers': 'S.add(m);solid.push(m);return m}' in s,
 'broadleaf trunks block line of sight': 'S.add(trunk);solid.push(trunk);trunk.castShadow' in s,
 'instanced forest trunks block line of sight': 'S.add(L,T);solid.push(T)' in s,
 'grouped cover props register their child meshes': 'g.traverse(o=>{if(o.isMesh)solid.push(o)})' in s,
 'environment deadfall blocks line of sight': 'obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)' in s,
 'tactical raycast remains allocation-free': 'ray.intersectObjects(solid,false).length===0' in s and 'solid.filter(' not in s,
 'integrity patch is marked': 'BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1' in s,
}
for name, ok in checks.items():
 print(('PASS ' if ok else 'FAIL ') + name)
if not all(checks.values()):
 raise SystemExit(f'{sum(not x for x in checks.values())} world/tactical integrity checks failed')
print(f'WORLD_TACTICAL_INTEGRITY_OK checks={len(checks)}')
