const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
class Vector3{constructor(){this.set(0,0,0)}set(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;return this}}
class Node3D{constructor(){this.position=new Vector3();this.rotation=new Vector3();this.scale=new Vector3();this.scale.setScalar=value=>this.scale.set(value,value,value);this.children=[];this.userData={};this.visible=true}add(child){this.children.push(child);child.parent=this}traverse(callback){callback(this);for(const child of this.children)child.traverse?child.traverse(callback):callback(child)}}
class Group extends Node3D{}
class Mesh extends Node3D{constructor(geometry,material){super();this.geometry=geometry;this.material=material;this.isMesh=true}}
class Geometry{constructor(...args){this.args=args}}
class Material{constructor(options){Object.assign(this,options);this.color={setHex(value){this.value=value}};this.emissive={setHex(value){this.value=value}}}}
const THREE={Group,Mesh,MeshStandardMaterial:Material,SphereGeometry:Geometry,CylinderGeometry:Geometry,BoxGeometry:Geometry,ConeGeometry:Geometry,TorusGeometry:Geometry,IcosahedronGeometry:Geometry,BackSide:1};
global.window=global;global.THREE=THREE;global.performance={now:()=>1000};
global.WILDBOUND={data:{monsters:{
 stalker:{type:'Grave Stalker',kind:'melee',h:2.15,r:.62,c:0x6d947d,sp:5.2,range:2.1,hp:90,damage:12},
 wraith:{type:'Wraithcaller',kind:'ranged',h:2.65,r:.48,c:0x927cc7,sp:3.7,range:13,hp:76,damage:10},
 ironmaw:{type:'Ironmaw',kind:'brute',h:2.45,r:.9,c:0x927c5c,sp:2.8,range:2.8,hp:180,damage:21},
 king:{type:'Hollow King',kind:'boss',h:4.5,r:1.45,c:0x4b3a58,sp:2.5,range:3.4,hp:700,damage:28}
}}};
const www=path.resolve(process.argv[2]);
const actorPath=path.join(www,'js/wildbound/actors/actors.js');
vm.runInThisContext(fs.readFileSync(actorPath,'utf8'),{filename:actorPath});
const scene=new Group();
const hunter=WILDBOUND.actors.hunter(scene);
assert.equal(hunter.userData.arms.length,2,'hunter has two articulated arm pivots');
assert.equal(hunter.userData.legs.length,2,'hunter has two articulated leg pivots');
WILDBOUND.actors.updateHunter(hunter,.016,true,false);
const expected={stalker:2,wraith:2,ironmaw:2,king:4};
for(const [type,armCount] of Object.entries(expected)){
 const monster=WILDBOUND.actors.monster(scene,type,0,-5);
 assert.equal(monster.userData.type,type);
 assert.equal(monster.userData.arms.length,armCount,`${type} arm rig`);
 assert.equal(monster.userData.legs.length,2,`${type} leg rig`);
 assert.ok(monster.userData.core&&monster.userData.aura&&monster.userData.head,`${type} anatomy and VFX anchors`);
 const base=monster.userData.coreBaseScale.x;
 WILDBOUND.actors.updateMonster(monster,.016,1000);
 assert.ok(monster.userData.core.scale.x>base*.9&&monster.userData.core.scale.x<base*1.1,`${type} core pulse preserves authored scale`);
}
WILDBOUND.actors.loadRigged([hunter]).then(result=>{
 assert.equal(result,false,'missing optional loader leaves the procedural hunter available');
 assert.ok(hunter.children.some(child=>child.visible),'fallback hunter remains visible');
 console.log('WILDBOUND_ACTOR_CONSTRUCTOR_RUNTIME_OK: hunter, four distinct monster rigs, animation update and loader fallback');
}).catch(error=>{console.error(error);process.exitCode=1});
