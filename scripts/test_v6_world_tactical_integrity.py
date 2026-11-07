#!/usr/bin/env python3
"""Regression gate for world occlusion, weapon aim and vehicle coordinate integrity."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
s=paths[0].read_text(encoding='utf-8')
models_paths=list(root.rglob('app/src/main/assets/www/js/models.js'))
if len(models_paths)!=1: raise SystemExit(f'Expected exactly one models.js, found {len(models_paths)}')
ms=models_paths[0].read_text(encoding='utf-8')
gradle_paths=list(root.rglob('app/build.gradle.kts'))
if len(gradle_paths)!=1: raise SystemExit(f'Expected exactly one app/build.gradle.kts, found {len(gradle_paths)}')
gs=gradle_paths[0].read_text(encoding='utf-8')
checks={
'cylinder cover raycast blockers':'S.add(m);solid.push(m);return m}' in s,
'broadleaf trunk occlusion':'S.add(trunk);solid.push(trunk);trunk.castShadow' in s,
'instanced forest trunk occlusion':'S.add(L,T);solid.push(T)' in s,
'grouped prop child meshes registered':'g.traverse(o=>{if(o.isMesh)solid.push(o)})' in s,
'deadfall occlusion':'obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)' in s,
'allocation-free tactical raycast':'ray.intersectObjects(solid,false).length===0' in s and 'solid.filter(' not in s,
'non-finite shot coordinates are rejected':'if(!Number.isFinite(dist))return false;if(dist<.2)return true;' in s,
'world marker present':'BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1' in s,
'attachment multipliers reduce spread':'const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);' in s,
'boolean-as-spread defect removed':'const sp_=P.grip||P.comp?.005:.01;' not in s,
'player follows clamped vehicle transform':'g.rotation.y=u.yaw;P.x=g.position.x;P.z=g.position.z;fx=fz=0;' in s,
'vehicle exit collision and world clamp':'const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);' in s,
'combat marker present':'BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1' in s,
'AI line-of-sight marker present':'BATTLEZONE_V6_TACTICAL_LINE_OF_SIGHT_V1' in s,
'enemy AI checks visibility before target lock':'if(!hasClearShot(bot.position.x,bot.position.y+1.15,bot.position.z,target.x,targetY,target.z))' in s,
'enemy AI temporarily suppresses occluded targets':'u.aiBlockedTarget=target.o||null;u.aiBlockedT=1.0;' in s,
'squad AI checks visibility before pursuing':'function bzV6ValidateSquadTarget(actor,u,target){' in s and 'if(!hasClearShot(actor.position.x,actor.position.y+1.15,actor.position.z,target.position.x,target.position.y+1.1,target.position.z))' in s,
'squad AI temporarily suppresses occluded targets':'u.squadBlockedTarget=target;u.squadBlockedT=1.0;' in s,
'frame-loop marker present':'BATTLEZONE_V6_FRAME_LOOP_EFFICIENCY_V1' in s,
'Android install version incremented':'BATTLEZONE_V6_BUILD_VERSION_1_2_1' in gs and 'versionCode = 4' in gs and 'versionName = \"1.2.1\"' in gs,
'frame telemetry object is reused':'bzFrameGameState.started=!!started;' in s and "window.BZGameState={started:!!started,health:Number(P.hp)||0,alive:!!P.alive,weapon:W[P.w]?.n||'Weapon'};" not in s,
'movement classes update only on state changes':"if(bzMove!==bzFrameLastMoving){document.body.classList.toggle('bz-moving',!!bzMove);" in s and "if(bzRunning!==bzFrameLastRunning){document.body.classList.toggle('bz-running',bzRunning);" in s,
'animation fallback marker present':'BATTLEZONE_V6_ANIMATION_FALLBACK_V1' in s and 'BATTLEZONE_V6_ANIMATION_FALLBACK_V1' in ms,
'missing combat clips use procedural fallback':"if(!action){" in ms and 'a.fallbackTimer=a.fallbackDuration' in ms,
'reload fallback has a bounded duration':"fallbackDuration=state==='reload'?1.5:.22" in ms,
'weapon mount base transform is preserved':'weaponBasePosition' in ms and 'weaponBaseRotation' in ms,
'shoot fallback animates weapon recoil':'entry.weaponMount.position.z-=.075*pulse' in ms,
'reload fallback animates weapon tilt':'entry.weaponMount.rotation.x-=.58*pulse' in ms,
'fallback timer expires and restores locomotion':'e.an.fallbackTimer=Math.max(0,e.an.fallbackTimer-dt)' in ms and 'const want=pickAct(e,sp)' in ms,
}
for name,ok in checks.items(): print(('PASS ' if ok else 'FAIL ')+name)
if not all(checks.values()): raise SystemExit(f'{sum(not x for x in checks.values())} integrity checks failed')
print(f'WORLD_TACTICAL_INTEGRITY_OK checks={len(checks)}')
