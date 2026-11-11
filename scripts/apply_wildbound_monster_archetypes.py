#!/usr/bin/env python3
"""Tune WILDBOUND creature attack profiles without changing boss phase logic."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_MONSTER_ARCHETYPE_PROFILES_V1'
if marker in s or "const pct=u.hp/u.maxHp,phase=pct<.3?3:pct<.65?2:1" in s:
 print('WILDBOUND_MONSTER_ARCHETYPES_HANDLED_BY_CANONICAL_AI'); raise SystemExit(0)
changes=[
("else if(d<=u.range*1.28){", "else if(d<=pending.reach){"),
("else if(u.attackCd<=0&&u.kind!=='boss'&&!u.pendingAttack){u.attackCd=1.65;u.attackWindup=.58;u.pendingAttack={type:'melee',damage:u.damage};if(u.kind==='melee')u.weakUntil=performance.now()+1100;W.bus.emit('monster-telegraph',{monster:m,type:'melee',duration:.58})}", "else if(u.attackCd<=0&&u.kind!=='boss'&&!u.pendingAttack){const brute=u.kind==='brute',windup=brute?.92:u.kind==='melee'?.42:.58;u.attackCd=brute?2.15:1.65;u.attackWindup=windup;u.pendingAttack={type:'melee',damage:u.damage*(brute?1.3:1),reach:u.range*(brute?1.55:u.kind==='melee'?1.38:1.28)};if(u.kind==='melee')u.weakUntil=performance.now()+1100;W.bus.emit('monster-telegraph',{monster:m,type:brute?'slam':'lunge',duration:windup})}"),
]
for old,new in changes:
 n=s.count(old)
 if n!=1: raise SystemExit(f'Expected one anchor, found {n}: {old[:100]}')
 s=s.replace(old,new,1)
s='/* '+marker+' */\n'+s
p.write_text(s,encoding='utf-8')
print('WILDBOUND_MONSTER_ARCHETYPE_PROFILES_APPLIED')
