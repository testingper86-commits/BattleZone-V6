#!/usr/bin/env python3
"""Add bounded ambient patrol behavior to non-boss WILDBOUND monsters."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
base=root/'app/src/main/assets/www/js/wildbound'
a=base/'actors/actors.js'; ai=base/'ai/monster-ai.js'
for p in (a,ai):
 if not p.is_file(): raise SystemExit(f'Missing required module: {p}')
actors=a.read_text(encoding='utf-8'); brain=ai.read_text(encoding='utf-8')
marker='WILDBOUND_MONSTER_AMBIENT_PATROL_V1'
if marker in brain:
 print('WILDBOUND_MONSTER_AMBIENT_PATROL_ALREADY_APPLIED'); raise SystemExit(0)
old='seed:Math.random()*10,arms,legs'
new='seed:Math.random()*10,homeX:x,homeZ:z,arms,legs'
if actors.count(old)!=1: raise SystemExit(f'Actor spawn anchor count: {actors.count(old)}')
actors=actors.replace(old,new,1)
old="W.toast('VOID IMPACT')}}}}};})();"
new="W.toast('VOID IMPACT')}}if(d>=34&&u.kind!=='boss'){const phase=performance.now()*.00022+u.seed,tx=u.homeX+Math.cos(phase)*3.5,tz=u.homeZ+Math.sin(phase)*3.5,px=tx-m.position.x,pz=tz-m.position.z,pd=Math.hypot(px,pz);if(pd>.18){const step=Math.min(pd,u.speed*.24*dt);m.position.x+=px/(pd||1)*step;m.position.z+=pz/(pd||1)*step;m.lookAt(tx,m.position.y,tz)}}}}};})();"
if brain.count(old)!=1: raise SystemExit(f'AI patrol insertion anchor count: {brain.count(old)}')
brain=brain.replace(old,new,1)
brain='/* '+marker+' */\n'+brain
a.write_text(actors,encoding='utf-8'); ai.write_text(brain,encoding='utf-8')
print('WILDBOUND_MONSTER_AMBIENT_PATROL_APPLIED')
