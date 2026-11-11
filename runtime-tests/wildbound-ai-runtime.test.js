'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(process.argv[2]||'canonical-build/app/src/main/assets/www');
const listeners={};let now=1000;
global.window=global;global.performance={now:()=>now};
const W=global.WILDBOUND={CONFIG:{AI:{detect:34}},state:{player:{hp:120,stamina:100,ether:100},skills:{ward:0},combat:{},world:{seed:1}},bus:{on:(e,f)=>(listeners[e]??=[]).push(f),emit:(e,d)=>(listeners[e]||[]).forEach(f=>f(d))},actors:{updateMonster(){},play(){}},audio:{hurt(){},boss(){},rift(){},heavy(){},hit(){},kill(){},dodge(){}},toast(){}};
for(const f of ['physics/collision.js','data/catalog.js','ai/monster-ai.js'])vm.runInThisContext(fs.readFileSync(path.join(root,'js/wildbound',f),'utf8'),{filename:f});
function actor(kind,x,z){const d=W.data.monsters[kind];return {position:{x,y:0,z,clone(){return {x:this.x,y:1,z:this.z}}},rotation:{y:0},lookAt(){},userData:{type:kind,kind:d.kind,alive:true,hp:d.hp,maxHp:d.hp,damage:d.damage,speed:d.sp,range:d.range,attackReach:d.range*1.2,noticeRange:30,attackCd:0,attackWindup:0,attackRecovery:0,stagger:0,hitFlash:0,seed:0,roamRadius:10,spawnX:x,spawnZ:z,patrolRadius:10,arms:[],legs:[],aura:{material:{color:{setHex(){}}},rotation:{y:0}},body:{material:{emissive:{setHex(){}}}}}}}
const player={position:{x:0,y:0,z:0},rotation:{y:0}};
let telegraphs=0,hurts=0;W.bus.on('monster-telegraph',()=>telegraphs++);W.bus.on('hurt',()=>hurts++);
const stalker=actor('stalker',0,2),game={player,monsters:[stalker],spawnProjectile(){throw new Error('unexpected projectile')},invulnerable:0};
W.ai.update(game,.1);assert.equal(telegraphs,1,'melee emits pre-attack warning');
for(let i=0;i<8;i++)W.ai.update(game,.1);assert.equal(hurts,1,'melee applies damage after windup');assert(stalker.userData.attackRecovery>0,'melee enters recovery');
const wraith=actor('wraith',0,10);wraith.userData.attackCd=0;game.monsters=[wraith];let shots=0;game.spawnProjectile=()=>shots++;
for(let i=0;i<7;i++)W.ai.update(game,.1);assert.equal(shots,1,'wraith launches one projectile after cast');
const king=actor('king',0,4);king.userData.hp=king.userData.maxHp*.25;king.userData.phase=1;king.userData.attackCd=0;game.monsters=[king];let phases=0;W.bus.on('boss-phase',()=>phases++);
for(let i=0;i<15;i++)W.ai.update(game,.1);assert.equal(king.userData.phase,3,'boss advances to final phase');assert.equal(phases,1,'phase transition emits one event');
const patrol=actor('stalker',12,12);patrol.userData.noticeRange=1;patrol.userData.spawnX=10;patrol.userData.spawnZ=10;game.monsters=[patrol];const start={x:patrol.position.x,z:patrol.position.z};for(let i=0;i<10;i++)W.ai.update(game,.1);assert(start.x!==patrol.position.x||start.z!==patrol.position.z,'unalerted enemy performs ambient patrol');
console.log('WILDBOUND_AI_RUNTIME_OK: melee telegraph/damage/recovery, ranged cast/projectile, boss phase transition, ambient patrol');
