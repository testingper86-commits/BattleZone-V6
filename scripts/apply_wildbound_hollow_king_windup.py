#!/usr/bin/env python3
"""Give the Hollow King a readable phase-one melee windup."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1'
if marker in s or "u.attackWindup=.55" in s or "u.attackWindup=phase===3?.9:.55" in s:
 print('WILDBOUND_HOLLOW_KING_WINDUP_HANDLED_BY_CANONICAL_AI'); raise SystemExit(0)
old="else if(u.attackCd<=0&&u.kind!=='boss'&&!u.pendingAttack){const brute=u.kind==='brute',windup=brute?.92:u.kind==='melee'?.42:.58;u.attackCd=brute?2.15:1.65;u.attackWindup=windup;u.pendingAttack={type:'melee',damage:u.damage*(brute?1.3:1),reach:u.range*(brute?1.55:u.kind==='melee'?1.38:1.28)};if(u.kind==='melee')u.weakUntil=performance.now()+1100;W.bus.emit('monster-telegraph',{monster:m,type:brute?'slam':'lunge',duration:windup})}"
new=old+"else if(u.attackCd<=0&&u.kind==='boss'&&(u.phase||1)===1&&!u.pendingAttack){u.attackCd=1.75;u.attackWindup=.82;u.pendingAttack={type:'melee',damage:u.damage*1.15,reach:u.range*1.45};W.bus.emit('monster-telegraph',{monster:m,type:'boss-swing',duration:.82});W.bus.emit('boss-telegraph')}"
if s.count(old)!=1: raise SystemExit(f'Boss windup anchor count: {s.count(old)}')
s=s.replace(old,new,1)
s='/* '+marker+' */\n'+s
p.write_text(s,encoding='utf-8')
print('WILDBOUND_HOLLOW_KING_WINDUP_APPLIED')
