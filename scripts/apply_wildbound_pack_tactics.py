#!/usr/bin/env python3
"""Install deterministic pack tactics and readable monster attack telegraphs."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
if not p.is_file(): raise SystemExit(f'Missing WILDBOUND monster AI module: {p}')
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_PACK_TACTICS_V1'
if marker in s:
 print('WILDBOUND_PACK_TACTICS_ALREADY_APPLIED')
 raise SystemExit(0)
if "W.ai={update(game,dt)" not in s or "u.kind==='boss'" not in s or 'game.spawnProjectile' not in s:
 raise SystemExit('Unexpected monster AI contract; refusing unsafe replacement')
source=r"""/* WILDBOUND_PACK_TACTICS_V1 */
(()=>{'use strict';
const W=window.WILDBOUND;
function damagePlayer(game,amount){if(game.invulnerable>0)return;const reduction=Math.min(.35,(W.state.skills.ward||0)*.08),dealt=amount*(1-reduction),ps=W.state.player;ps.hp=Math.max(0,ps.hp-dealt);W.audio.hurt();W.bus.emit('hurt',dealt);if(ps.hp<=0)W.bus.emit('down')}
W.ai={update(game,dt){
 const p=game.player,now=performance.now(),alive=game.monsters.filter(m=>m.userData.alive);
 for(const m of game.monsters){
  const u=m.userData;if(!u.alive)continue;u.attackCd=Math.max(0,(u.attackCd||0)-dt);u.stagger=Math.max(0,(u.stagger||0)-dt);
  const gait=now*.009+(u.seed||0);u.legs.forEach((leg,i)=>leg.rotation.x=Math.sin(gait+i*Math.PI)*.42);u.arms.forEach((arm,i)=>arm.rotation.x=Math.sin(gait+i*Math.PI+1)*.28);if(u.kind==='wraith')m.position.y=.18+Math.sin(gait*1.3)*.16;u.hitFlash=Math.max(0,(u.hitFlash||0)-dt);
  const dx=p.position.x-m.position.x,dz=p.position.z-m.position.z,d=W.physics.distance2D(p.position,m.position);
  if(!u.tacticRole)u.tacticRole=u.kind==='boss'?'boss':u.kind==='ranged'?'ranged':(Math.floor((u.seed||0)*1000)%3===0?'flanker':Math.floor((u.seed||0)*1000)%3===1?'pursuer':'disruptor');
  let sx=0,sz=0;for(const other of alive){if(other===m)continue;const ox=m.position.x-other.position.x,oz=m.position.z-other.position.z,od=Math.hypot(ox,oz);if(od>0&&od<1.9){const push=(1.9-od)/1.9;sx+=ox/od*push;sz+=oz/od*push}}
  if(d<38){m.lookAt(p.position.x,m.position.y,p.position.z);if(u.stagger<=0){
   if(u.kind==='ranged'){if(d<7.5){m.position.x-=dx/(d||1)*u.speed*dt;m.position.z-=dz/(d||1)*u.speed*dt}else if(d>13.5){m.position.x+=dx/(d||1)*u.speed*dt;m.position.z+=dz/(d||1)*u.speed*dt}else if(u.attackCd<=0){u.attackCd=2.25;u.weakUntil=now+1050;const origin=m.position.clone();origin.y+=1.8;game.spawnProjectile(origin,u.damage,0xa58bff,1)}}
   else if(u.kind==='boss'){if(d>u.range*.78){m.position.x+=dx/(d||1)*u.speed*dt;m.position.z+=dz/(d||1)*u.speed*dt}else if(d<=u.range&&u.attackCd<=0&&u.phase===1&&!u.attackWindup){u.attackWindup=.72;u.weakUntil=now+1450;W.bus.emit('monster-telegraph',{monster:m,kind:'boss',role:'boss',remaining:.72})}}
   else{const baseAngle=Math.atan2(m.position.z-p.position.z,m.position.x-p.position.x),seed=(u.seed||0)*6.283185307,side=u.tacticRole==='flanker'?(Math.sin(seed)>=0?1:-1):u.tacticRole==='disruptor'?(Math.cos(seed)>=0?-1:1):0,desired=u.kind==='brute'?2.2:1.65,angle=baseAngle+side*.82,tx=p.position.x+Math.cos(angle)*desired,tz=p.position.z+Math.sin(angle)*desired,vx=tx-m.position.x+sx*1.35,vz=tz-m.position.z+sz*1.35,vd=Math.hypot(vx,vz);if(d>u.range*.78&&vd>.12){m.position.x+=vx/(vd||1)*u.speed*dt;m.position.z+=vz/(vd||1)*u.speed*dt}else if(d<=u.range*.95&&u.attackCd<=0&&!u.attackWindup){u.attackWindup=u.kind==='brute'?.62:.4;u.weakUntil=now+u.attackWindup*1000+650;W.bus.emit('monster-telegraph',{monster:m,kind:u.kind,role:u.tacticRole,remaining:u.attackWindup})}}
  }}
  if(u.attackWindup>0){u.attackWindup=Math.max(0,u.attackWindup-dt);if(u.attackWindup===0){u.attackCd=u.kind==='brute'?2.05:u.kind==='boss'?1.8:1.55;const current=W.physics.distance2D(p.position,m.position);if(current<=u.range*1.12&&u.stagger<=0){damagePlayer(game,u.damage);W.bus.emit('monster-strike',{monster:m,kind:u.kind})}u.weakUntil=now+500}}
  if(u.body&&u.body.material&&u.body.material.emissive)u.body.material.emissive.setHex(u.hitFlash>0?0x7d3027:u.attackWindup>0?0xff8a43:0x000000);
  if(u.kind==='boss'){const pct=u.hp/u.maxHp,phase=pct<.3?3:pct<.65?2:1;if(phase!==u.phase){u.phase=phase;u.speed+=.65;u.damage+=5;u.aura.material.color.setHex(phase===3?0xff583d:0x9c68d8);W.bus.emit('boss-phase',phase);W.audio.boss()}if(d<18&&u.attackCd<=0&&phase>=2){u.attackCd=2.8;u.weakUntil=now+1800;W.bus.emit('boss-telegraph');if(phase===2){const origin=m.position.clone();origin.y+=2.2;game.spawnProjectile(origin,u.damage*1.25,0xb18aff,1.45)}else{u.slamAt=now+850;W.bus.emit('boss-slam-warning')}}if(phase===3&&u.slamAt&&now>=u.slamAt){u.slamAt=0;if(d<11)damagePlayer(game,u.damage*1.7);W.toast('VOID IMPACT')}}
 }
}};
})();
"""
p.write_text(source,encoding='utf-8')
print('WILDBOUND_PACK_TACTICS_PATCHED',p)
