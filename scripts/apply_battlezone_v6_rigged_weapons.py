#!/usr/bin/env python3
"""Attach equipped weapons to the animated character hand and improve armed locomotion."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();p=root/'app/src/main/assets/www/js/models.js'
if not p.is_file():raise SystemExit('models.js missing')
s=p.read_text(encoding='utf-8');marker='BATTLEZONE_V6_RIGGED_WEAPONS_V1'
if marker in s:print(marker,'already applied');raise SystemExit(0)
def one(old,new,label):
 global s
 n=s.count(old)
 if n!=1:raise SystemExit(f'{label}: expected one anchor, found {n}')
 s=s.replace(old,new,1)

one("let tpl=null,state='idle',cfg=null,skinTex=[];", "let tpl=null,state='idle',cfg=null,skinTex=[];\nconst OPERATOR_SKINS={'Recruit':0,'Ranger':1,'Vanguard':2,'Phantom':3,'Aegis Legend':0,'Storm Warden':1,'Ember Fox':2,'Frostline':3,'Wraith':0,'Solstice':1,'Ironclad':2,'Neon Viper':3,'Redshift':0,'Oracle':1,'Titan Zero':2,'Nova Prime':3,'Void Monarch':0};\nconst OPERATOR_COLORS={Recruit:0x9cae9a,Ranger:0x7aa16a,Vanguard:0x7b8797,Phantom:0x75618e,'Aegis Legend':0x55b9b6,'Storm Warden':0x6e7fd4,'Ember Fox':0xd66a40,Frostline:0x9cc9e3,Wraith:0x565d70,Solstice:0xd3b45e,Ironclad:0x7b8489,'Neon Viper':0x65c46d,Redshift:0xd25368,Oracle:0x9a84d5,'Titan Zero':0xa88856,'Nova Prime':0x61aee8,'Void Monarch':0x9c63cb};",'operator visual profiles')
one("""function instance(skinKey){
  const model=THREE.SkeletonUtils.clone(tpl.holder);
  const tex=skinTex.length?skinTex[hash(skinKey)%skinTex.length]:null;
  model.traverse(o=>{
    o.userData.bzShared=true;                       // never dispose (shared geometry)
    if(tex&&o.isMesh)o.material=new THREE.MeshLambertMaterial({map:tex,skinning:!!o.isSkinnedMesh});
  });
  return model;
}""", """function instance(skinKey){
  const model=THREE.SkeletonUtils.clone(tpl.holder),key=String(skinKey),idx=Object.prototype.hasOwnProperty.call(OPERATOR_SKINS,key)?OPERATOR_SKINS[key]:hash(key)%Math.max(1,skinTex.length),tint=new THREE.Color(OPERATOR_COLORS[key]||OPERATOR_COLORS[Object.keys(OPERATOR_COLORS)[hash(key)%Object.keys(OPERATOR_COLORS).length]]||0xffffff).lerp(new THREE.Color(0xffffff),.42),tex=skinTex.length?skinTex[idx%skinTex.length]:null;
  model.traverse(o=>{o.userData.bzShared=true;if(o.isMesh&&tex)o.material=new THREE.MeshLambertMaterial({map:tex,color:tint,skinning:!!o.isSkinnedMesh})});
  return model;
}""",'operator skins and tint profiles')
old_reg="""function register(obj,model,opt){
  const an=animator(model);if(an){an.cur=an.acts.idle;an.cur.a.play()}
  entries.push({obj,model,an,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null});
}"""
helpers="""function findBone(root,keys){let found=null;root.traverse(o=>{if(found||!o.isBone)return;const n=String(o.name||'').toLowerCase().replace(/[^a-z0-9]/g,'');if(keys.includes(n))found=o});return found}
function setWeaponEntry(entry,name){if(!entry||!entry.weaponMount)return false;while(entry.weaponMount.children.length){const old=entry.weaponMount.children[0];old.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());else o.material.dispose()}});entry.weaponMount.remove(old)}let weapon=null;try{if(typeof window.mkGun==='function')weapon=window.mkGun(name)}catch(e){}if(!weapon)weapon=new THREE.Mesh(new THREE.BoxGeometry(.07,.11,.68),new THREE.MeshLambertMaterial({color:0x202832}));weapon.rotation.set(Math.PI/2,0,0);weapon.scale.setScalar(.72);weapon.userData.bzShared=false;entry.weaponMount.add(weapon);entry.weaponName=name;return true}
function setWeapon(target,name){const entry=entries.find(e=>e.obj===target);return entry?setWeaponEntry(entry,name):false}
function applyWeaponPose(entry,speed,time){if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.template?.format==='glb'||entry.an.dead||entry.an.actionState==='death'||entry.an.actionState==='reload'||entry.an.actionState==='shoot')return;const b=entry.bones,run=Math.min(1,Math.max(0,(speed-1.8)/5.5)),sway=Math.sin(time*10)*.035*run,blend=(bone,x,y,z,w)=>{if(!bone)return;bone.rotation.x=bone.rotation.x*(1-w)+x*w;bone.rotation.y=bone.rotation.y*(1-w)+y*w;bone.rotation.z=bone.rotation.z*(1-w)+z*w};blend(b.rightArm,-.34-sway,.02,.08,.82);blend(b.rightForeArm,-.72,.02,0,.82);blend(b.leftArm,-.58+sway,-.02,-.2,.82);blend(b.leftForeArm,-.88,0,.1,.82);blend(b.spine,.035+run*.045,0,0,.32)}
"""
new_reg="""function register(obj,model,opt){
  const an=animator(model);if(an){an.cur=an.acts.idle;an.cur.a.play()}
  const bones={rightHand:findBone(model,['righthand','handr']),rightArm:findBone(model,['rightarm','upperarmr']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml']),leftForeArm:findBone(model,['leftforearm','forearml']),spine:findBone(model,['spine','spine1','chest'])};
  const entry={obj,model,an,bones,template:tpl,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null};entries.push(entry);
  if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,.055);bones.rightHand.add(entry.weaponMount);setWeaponEntry(entry,window.BZActiveWeapon||'M416')}
}"""
one(old_reg,helpers+new_reg,'hand weapon and armed pose integration')
one("""function dress(group,opt){
  opt=opt||{};const keep=new Set((opt.keep||[]).filter(Boolean)),show=new Set((opt.show||[]).filter(Boolean));
  const old=group.children.slice();
  const model=instance(opt.skinKey||group.uuid||'x');
  old.forEach(ch=>{if(keep.has(ch))return;lock(ch,show.has(ch))});
  group.add(model);register(group,model,opt);group.userData.bzDressed=true;
  if(opt.gun){const g=new THREE.Mesh(new THREE.BoxGeometry(.07,.11,.7),new THREE.MeshLambertMaterial({color:0x1a1d21}));g.position.set(.28,1.12,.42);g.userData.bzShared=false;group.add(g)}
}""", """function dress(group,opt){
  opt=opt||{};const keep=new Set((opt.keep||[]).filter(Boolean)),old=group.children.slice(),model=instance(opt.skinKey||group.uuid||'x');
  old.forEach(ch=>{if(keep.has(ch))return;lock(ch,false)});
  group.add(model);model.traverse(o=>{if(o.isMesh){o.userData.bot=group;if(/head/i.test(String(o.name||'')))o.userData.head=1}});register(group,model,opt);group.userData.bzDressed=true;
}""",'remove floating gun proxy and dress rigged model')
# Bots must not keep the old detached gun box visible; the new gun is mounted to the hand.
one("const gun=g.children[3];                      // the held-gun box stays visible\n          dress(g,{skinKey:(g.userData.nid||'bot')+i,show:[gun],cull:true});", "dress(g,{skinKey:(g.userData.nid||'bot')+i,cull:true,gun:true});",'replace bot gun proxy')
# Apply the held-weapon pose after each locomotion/action mixer update.
one("const active=e.an.action;e.an.mixer.update(dt);", "const active=e.an.action;e.an.mixer.update(dt);applyWeaponPose(e,sp,n*.001);",'armed pose during action updates')
one("e.an.mixer.update(dt)\n      }else e.an.mixer.update(dt)", "e.an.mixer.update(dt);applyWeaponPose(e,sp,n*.001)\n      }else{e.an.mixer.update(dt);applyWeaponPose(e,sp,n*.001)}",'armed pose during locomotion')
one("window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load,playAction,availableActions:()=>['shoot','reload','death'].filter(k=>!!(tpl&&tpl.clips&&tpl.clips[k]))};", "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load,playAction,setWeapon,availableActions:()=>['shoot','reload','death'].filter(k=>!!(tpl&&tpl.clips&&tpl.clips[k]))};",'expose live weapon switching')
s=s.replace("/* BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1 */", "/* BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1 */\n/* "+marker+" */",1)
p.write_text(s,encoding='utf-8');print(marker,'applied')
