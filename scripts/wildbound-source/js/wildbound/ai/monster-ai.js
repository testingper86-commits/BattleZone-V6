/* WILDBOUND_MONSTER_TELEGRAPH_COMBAT_V1 */
/* WILDBOUND_MONSTER_ARCHETYPE_PROFILES_V1 */
/* WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1 */
/* WILDBOUND_MONSTER_AMBIENT_PATROL_V1 */
(()=>{'use strict';
const W=window.WILDBOUND;
const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));
function constrain(monster){const worldSize=W.CONFIG&&W.CONFIG.WORLD&&W.CONFIG.WORLD.size||160,limit=Math.max(8,worldSize*.5-4);monster.position.x=clamp(monster.position.x,-limit,limit);monster.position.z=clamp(monster.position.z,-limit,limit)}
function animate(monster,dt,now){if(W.actors&&W.actors.updateMonster)W.actors.updateMonster(monster,dt,now)}
W.ai={update(game,dt){
 const player=game.player,playerState=W.state.player,now=performance.now();
 for(const monster of game.monsters){
  const state=monster.userData;if(!state||!state.alive)continue;
  state.attackCd=Math.max(0,(state.attackCd||0)-dt);
  state.stagger=Math.max(0,(state.stagger||0)-dt);
  state.attackWindup=Math.max(0,(state.attackWindup||0)-dt);
  state.attackRecovery=Math.max(0,(state.attackRecovery||0)-dt);
  state.hitFlash=Math.max(0,(state.hitFlash||0)-dt);
  if(state.body&&state.body.material&&state.body.material.emissive)state.body.material.emissive.setHex(state.hitFlash>0?0x7d3027:0x000000);
  const dx=player.position.x-monster.position.x,dz=player.position.z-monster.position.z,distance=W.physics.distance2D(player.position,monster.position),kind=state.kind||'melee',notice=state.noticeRange||(W.CONFIG&&W.CONFIG.AI&&W.CONFIG.AI.detect)||26,reach=state.attackReach||state.range*1.25;monster.rotation.y=Math.atan2(dx,dz);
  if(distance>=notice){
   state.attackState='patrol';
   if(state.roamRadius>0&&state.stagger<=0&&state.attackRecovery<=0){
    state.patrolPhase=(state.patrolPhase||0)+dt*.32;
    const targetX=state.spawnX+Math.cos(state.patrolPhase)*state.roamRadius,targetZ=state.spawnZ+Math.sin(state.patrolPhase)*state.roamRadius,offsetX=targetX-monster.position.x,offsetZ=targetZ-monster.position.z,travel=Math.hypot(offsetX,offsetZ);
    if(travel>.4){monster.position.x+=offsetX/travel*state.speed*.36*dt;monster.position.z+=offsetZ/travel*state.speed*.36*dt;monster.lookAt(targetX,0,targetZ)}
   }
   constrain(monster);animate(monster,dt,now);continue;
  }
  monster.lookAt(player.position.x,monster.position.y,player.position.z);
  if(state.stagger>0||state.attackRecovery>0){state.attackState='recovery';animate(monster,dt,now);continue}
  if(kind==='boss'){
   const healthRatio=state.hp/state.maxHp,phase=healthRatio<.3?3:healthRatio<.65?2:1;
   if(phase!==state.phase){state.phase=phase;state.speed+=.65;state.damage+=5;state.aura.material.color.setHex(phase===3?0xff583d:0x9c68d8);W.bus.emit('boss-phase',phase);W.audio.boss()}
   if(distance>reach){state.attackState='pursuit';monster.position.x+=dx/(distance||1)*state.speed*dt;monster.position.z+=dz/(distance||1)*state.speed*dt}
   else if(state.attackCd<=0){const phaseOne=phase===1;state.attackState='windup';state.attackCd=phase===3?2.5:phaseOne?1.75:2.1;state.attackWindup=phase===3?.9:phaseOne?.82:.55;state.pendingAttackReach=phaseOne?state.range*1.45:reach;state.pendingAttackDamage=state.damage*(phaseOne?1.15:1);state.weakUntil=now+(state.attackWindup+.55)*1000;W.bus.emit('monster-telegraph',{type:state.type,attack:phaseOne?'boss-swing':phase===3?'ground-slam':'core-sweep',position:monster.position.clone(),duration:state.attackWindup});W.bus.emit('boss-telegraph',{phase,position:monster.position.clone(),attack:phase===3?'ground-slam':phaseOne?'boss-swing':'core-sweep'})}
   if(state.attackWindup<=0&&state.attackState==='windup'){
    state.attackState='attack';state.attackRecovery=.75;
    if(phase===2){const origin=monster.position.clone();origin.y+=2.2;game.spawnProjectile(origin,state.damage*1.25,0xb18aff,1.45)}
    else if(phase===3){W.bus.emit('boss-slam-warning',{position:monster.position.clone(),radius:11});if(distance<11&&game.invulnerable<=0){playerState.hp=Math.max(0,playerState.hp-state.damage*1.7);W.audio.hurt();W.bus.emit('hurt',state.damage*1.7)}W.toast('VOID IMPACT')}
    else if(distance<=(state.pendingAttackReach||reach)&&game.invulnerable<=0){const damage=state.pendingAttackDamage||state.damage,reduction=Math.min(.35,(W.state.skills.ward||0)*.08);playerState.hp=Math.max(0,playerState.hp-damage*(1-reduction));W.audio.hurt();W.bus.emit('hurt',damage);if(playerState.hp<=0)W.bus.emit('down')}
   }
  }else if(kind==='ranged'||kind==='wraith'){
   if(distance<7){state.attackState='retreat';monster.position.x-=dx/(distance||1)*state.speed*.85*dt;monster.position.z-=dz/(distance||1)*state.speed*.85*dt}
   else if(distance>15){state.attackState='pursuit';monster.position.x+=dx/(distance||1)*state.speed*.62*dt;monster.position.z+=dz/(distance||1)*state.speed*.62*dt}
   else if(state.attackCd<=0){state.attackState='windup';state.attackCd=2.25;state.attackWindup=.5;state.weakUntil=now+1350;W.bus.emit('monster-telegraph',{type:state.type,attack:'ether-bolt',position:monster.position.clone()})}
   if(state.attackWindup<=0&&state.attackState==='windup'){state.attackState='attack';state.attackRecovery=.4;const origin=monster.position.clone();origin.y+=1.8;game.spawnProjectile(origin,state.damage,kind==='wraith'?0x9d7ef2:0xa58bff,kind==='wraith'?1.2:1)}
  }else if(distance>reach){state.attackState='pursuit';monster.position.x+=dx/(distance||1)*state.speed*dt;monster.position.z+=dz/(distance||1)*state.speed*dt}
  else if(state.attackCd<=0){
   const profile=state.attackProfile||{windup:kind==='brute'?.92:.42,recovery:kind==='brute'?1.12:.62,damageScale:kind==='brute'?1.3:1,reachScale:1.25,attack:kind==='brute'?'slam':'claw'};
   state.attackState='windup';state.pendingAttackReach=state.range*(profile.reachScale||1.25);state.pendingAttackDamage=state.damage*(profile.damageScale||1);state.attackCd=kind==='brute'?2.3:1.8;state.attackWindup=profile.windup;state.weakUntil=now+(state.attackWindup+.65)*1000;
   W.bus.emit('monster-telegraph',{type:state.type,attack:profile.attack==='slam'?'heavy-lunge':profile.attack==='lunge'?'heavy-lunge':'claw-swipe',position:monster.position.clone(),duration:state.attackWindup});
  }
  if(state.attackWindup<=0&&state.attackState==='windup'){
   state.attackState='attack';state.attackRecovery=state.attackProfile?state.attackProfile.recovery:(kind==='brute'?.95:.62);
   const strikeReach=state.pendingAttackReach||reach+.5,damage=state.pendingAttackDamage||state.damage;
   if(distance<=strikeReach&&game.invulnerable<=0){const reduction=Math.min(.35,(W.state.skills.ward||0)*.08);playerState.hp=Math.max(0,playerState.hp-damage*(1-reduction));W.audio.hurt();W.bus.emit('hurt',damage);if(playerState.hp<=0)W.bus.emit('down')}
   if(kind==='melee')state.weakUntil=now+1200;
  }
  constrain(monster);animate(monster,dt,now);
 }
}};
})();
