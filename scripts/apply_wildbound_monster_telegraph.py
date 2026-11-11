#!/usr/bin/env python3
"""Add readable, interruptible attack windups to standard WILDBOUND monsters."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
if not p.is_file(): raise SystemExit(f'Missing monster AI module: {p}')
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_MONSTER_TELEGRAPH_COMBAT_V1'
if marker in s:
 print('WILDBOUND_MONSTER_TELEGRAPH_ALREADY_APPLIED'); raise SystemExit(0)
repls=[
("u.attackCd-=dt;u.stagger=Math.max(0,u.stagger-dt);", "u.attackCd-=dt;u.stagger=Math.max(0,u.stagger-dt);if(u.stagger>0&&u.pendingAttack){u.pendingAttack=null;u.attackWindup=0;W.bus.emit('monster-telegraph-cancel',m)}"),
("u.body.material.emissive.setHex(u.hitFlash>0?0x7d3027:0x000000);", "u.body.material.emissive.setHex(u.hitFlash>0?0x7d3027:u.pendingAttack?0xff6b32:0x000000);"),
("const dx=p.position.x-m.position.x,dz=p.position.z-m.position.z,d=W.physics.distance2D(p.position,m.position);if(d<34)", "const dx=p.position.x-m.position.x,dz=p.position.z-m.position.z,d=W.physics.distance2D(p.position,m.position);if(u.pendingAttack){u.attackWindup-=dt;if(u.attackWindup<=0){const pending=u.pendingAttack;u.pendingAttack=null;u.attackWindup=0;if(u.stagger<=0){if(pending.type==='ranged'){const origin=m.position.clone();origin.y+=1.8;game.spawnProjectile(origin,pending.damage,0xa58bff,1);W.bus.emit('monster-strike',{monster:m,type:'ranged'})}else if(d<=u.range*1.28){if(game.invulnerable<=0){const reduction=Math.min(.35,(W.state.skills.ward||0)*.08);ps.hp=Math.max(0,ps.hp-pending.damage*(1-reduction));W.audio.hurt();W.bus.emit('hurt',pending.damage);if(ps.hp<=0)W.bus.emit('down')}W.bus.emit('monster-strike',{monster:m,type:'melee'})}}}}if(d<34)"),
("if(u.kind==='ranged'&&d<16&&d>7&&u.attackCd<=0){u.attackCd=2.1;u.weakUntil=performance.now()+1300;const origin=m.position.clone();origin.y+=1.8;game.spawnProjectile(origin,u.damage,0xa58bff,1)}else if(d>u.range*.78)", "if(u.kind==='ranged'&&d<16&&d>7&&u.attackCd<=0&&!u.pendingAttack){u.attackCd=2.1;u.attackWindup=.48;u.pendingAttack={type:'ranged',damage:u.damage};u.weakUntil=performance.now()+1300;W.bus.emit('monster-telegraph',{monster:m,type:'ranged',duration:.48})}else if(d>u.range*.78)"),
("else if(u.attackCd<=0){u.attackCd=u.kind==='boss'?1.15:1.65;if(u.kind==='melee')u.weakUntil=performance.now()+1100;if(game.invulnerable<=0){const reduction=Math.min(.35,(W.state.skills.ward||0)*.08);ps.hp=Math.max(0,ps.hp-u.damage*(1-reduction));W.audio.hurt();W.bus.emit('hurt',u.damage);if(ps.hp<=0)W.bus.emit('down')}}", "else if(u.attackCd<=0&&u.kind!=='boss'&&!u.pendingAttack){u.attackCd=1.65;u.attackWindup=.58;u.pendingAttack={type:'melee',damage:u.damage};if(u.kind==='melee')u.weakUntil=performance.now()+1100;W.bus.emit('monster-telegraph',{monster:m,type:'melee',duration:.58})}")]
for old,new in repls:
 n=s.count(old)
 if n!=1: raise SystemExit(f'Expected exactly one source anchor, found {n}: {old[:100]}')
 s=s.replace(old,new,1)
s='/* '+marker+' */\n'+s
p.write_text(s,encoding='utf-8')
print('WILDBOUND_MONSTER_TELEGRAPH_APPLIED')
