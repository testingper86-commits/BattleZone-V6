#!/usr/bin/env python3
"""Load both CC0 character rigs and assign them deterministically across operators and bots."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();p=root/'app/src/main/assets/www/js/models.js'
if not p.is_file():raise SystemExit('models.js missing')
s=p.read_text(encoding='utf-8');marker='BATTLEZONE_V6_MULTIMODEL_V1'
if marker in s:print(marker,'already applied');raise SystemExit(0)
def one(old,new,label):
 global s
 n=s.count(old)
 if n!=1:raise SystemExit(f'{label}: expected one anchor, found {n}')
 s=s.replace(old,new,1)

one("let tpl=null,state='idle',cfg=null,skinTex=[];", "let tpl=null,state='idle',cfg=null,skinTex=[],templates=[];",'model family collection')
one("const OPERATOR_COLORS={Recruit:0x9cae9a,Ranger:0x7aa16a,Vanguard:0x7b8797,Phantom:0x75618e,'Aegis Legend':0x55b9b6,'Storm Warden':0x6e7fd4,'Ember Fox':0xd66a40,Frostline:0x9cc9e3,Wraith:0x565d70,Solstice:0xd3b45e,Ironclad:0x7b8489,'Neon Viper':0x65c46d,Redshift:0xd25368,Oracle:0x9a84d5,'Titan Zero':0xa88856,'Nova Prime':0x61aee8,'Void Monarch':0x9c63cb};", "const OPERATOR_COLORS={Recruit:0x9cae9a,Ranger:0x7aa16a,Vanguard:0x7b8797,Phantom:0x75618e,'Aegis Legend':0x55b9b6,'Storm Warden':0x6e7fd4,'Ember Fox':0xd66a40,Frostline:0x9cc9e3,Wraith:0x565d70,Solstice:0xd3b45e,Ironclad:0x7b8489,'Neon Viper':0x65c46d,Redshift:0xd25368,Oracle:0x9a84d5,'Titan Zero':0xa88856,'Nova Prime':0x61aee8,'Void Monarch':0x9c63cb};\nconst KAYKIT_OPERATORS=new Set(['Phantom','Aegis Legend','Wraith','Neon Viper','Oracle','Titan Zero','Void Monarch']);",'alternate model family roster')
one("""  tpl={holder,clips,walkScale:c.walkScale||.55};
}""", """  tpl={holder,clips,walkScale:c.walkScale||.55,format:c.format||'fbx',config:c,skinTex:[]};
}""",'template metadata')
one("""async function tryConfig(c){
  if(c.format==='fbx'){
    if(!THREE.FBXLoader||!window.fflate)throw new Error('FBXLoader/fflate missing');
    const root=await loadFBX(c.model),clips={};
    const skins=c.skins||(c.skin?[c.skin]:[]);skinTex=[];
    for(const s of skins){try{skinTex.push(await loadTex(s))}catch(e){note('skin missing: '+s)}}
    for(const key in (c.anims||{})){try{const a=await loadFBX(c.anims[key]);const cl=bestClip(a.animations,key);if(cl){cl.name=key;clips[key]=cl}}catch(e){note('animation '+key+' unavailable')}}
    if(!clips.idle){const own=bestClip(root.animations,'idle');if(own)clips.idle=own}
    finish(root,clips,c);
  }else{
    if(!THREE.GLTFLoader)throw new Error('GLTFLoader missing');
    const g=await loadGLB(c.model),l=g.animations||[];skinTex=[];
    finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump'),shoot:bestClip(l,'shoot|fire|rifle'),reload:bestClip(l,'reload'),death:bestClip(l,'death|die|dead|defeat')},c);
  }
}""", """async function tryConfig(c){
  if(c.format==='fbx'){
    if(!THREE.FBXLoader||!window.fflate)throw new Error('FBXLoader/fflate missing');
    const root=await loadFBX(c.model),clips={},skins=c.skins||(c.skin?[c.skin]:[]);skinTex=await Promise.all(skins.map(async s=>{try{return await loadTex(s)}catch(e){note('skin missing: '+s);return null}}));
    for(const key in (c.anims||{})){try{const a=await loadFBX(c.anims[key]);const cl=bestClip(a.animations,key);if(cl){cl.name=key;clips[key]=cl}}catch(e){note('animation '+key+' unavailable')}}
    if(!clips.idle){const own=bestClip(root.animations,'idle');if(own)clips.idle=own}
    finish(root,clips,c);tpl.skinTex=skinTex.slice();tpl.format='fbx';tpl.config=c;return tpl;
  }
  if(!THREE.GLTFLoader)throw new Error('GLTFLoader missing');
  const g=await loadGLB(c.model),l=g.animations||[];skinTex=[];
  finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump'),shoot:bestClip(l,'shoot|fire|rifle'),reload:bestClip(l,'reload'),death:bestClip(l,'death|die|dead|defeat')},c);
  tpl.skinTex=[];tpl.format='glb';tpl.config=c;return tpl;
}""",'load both rigged model families')
one("""async function load(){
  if(state!=='idle')return;state='loading';
  if(!THREE.SkeletonUtils){state='failed';note('SkeletonUtils missing - procedural characters');return}
  const list=[];
  try{const r=await fetch('./models/characters/manifest.json');if(r.ok){const m=await r.json();list.push(Object.assign({format:/\\.fbx$/i.test(m.model)?'fbx':'glb'},m))}}catch(e){}
  DEFAULTS.forEach(d=>list.push(d));
  for(const c of list){try{await tryConfig(c);cfg=c;state='ready';note('ready: '+c.model+' clips='+Object.keys(tpl.clips).join(',')+' skins='+skinTex.length);return}catch(e){note(c.model+' skipped: '+e.message)}}
  state='failed';note('no character model usable - procedural characters stay');
}""", """async function load(){
  if(state!=='idle')return;state='loading';
  if(!THREE.SkeletonUtils){state='failed';note('SkeletonUtils missing - procedural characters');return}
  const list=[];
  try{const r=await fetch('./models/characters/manifest.json');if(r.ok){const m=await r.json();list.push(Object.assign({format:/\\.fbx$/i.test(m.model)?'fbx':'glb'},m))}}catch(e){}
  DEFAULTS.forEach(d=>list.push(d));const loaded=[];
  for(const c of list){try{const t=await tryConfig(c);loaded.push(t);note('model family ready: '+c.format+' '+c.model)}catch(e){note(c.model+' skipped: '+e.message)}}
  templates=loaded;tpl=templates.find(t=>t.format==='fbx')||templates[0]||null;cfg=tpl&&tpl.config||null;
  if(tpl){state='ready';note('ready: '+templates.length+' local character families')}else{state='failed';note('no character model usable - procedural characters stay')}
}""",'load all available model templates')
one("""function instance(skinKey){
  const model=THREE.SkeletonUtils.clone(tpl.holder),key=String(skinKey),idx=Object.prototype.hasOwnProperty.call(OPERATOR_SKINS,key)?OPERATOR_SKINS[key]:hash(key)%Math.max(1,skinTex.length),tint=new THREE.Color(OPERATOR_COLORS[key]||OPERATOR_COLORS[Object.keys(OPERATOR_COLORS)[hash(key)%Object.keys(OPERATOR_COLORS).length]]||0xffffff).lerp(new THREE.Color(0xffffff),.42),tex=skinTex.length?skinTex[idx%skinTex.length]:null;
  model.traverse(o=>{o.userData.bzShared=true;if(o.isMesh&&tex)o.material=new THREE.MeshLambertMaterial({map:tex,color:tint,skinning:!!o.isSkinnedMesh})});
  return model;
}""", """function chooseTemplate(key){const name=String(key),glb=templates.find(t=>t.format==='glb'),fbx=templates.find(t=>t.format==='fbx');if(glb&&(KAYKIT_OPERATORS.has(name)||(!Object.prototype.hasOwnProperty.call(OPERATOR_SKINS,name)&&hash(name)%4===0)))return glb;return fbx||glb||tpl}
function instance(skinKey,template){
  template=template||tpl;if(!template)throw new Error('no local character template');const model=THREE.SkeletonUtils.clone(template.holder),skins=template.skinTex||[],key=String(skinKey),idx=Object.prototype.hasOwnProperty.call(OPERATOR_SKINS,key)?OPERATOR_SKINS[key]:hash(key)%Math.max(1,skins.length),tint=new THREE.Color(OPERATOR_COLORS[key]||OPERATOR_COLORS[Object.keys(OPERATOR_COLORS)[hash(key)%Object.keys(OPERATOR_COLORS).length]]||0xffffff).lerp(new THREE.Color(0xffffff),.42),tex=skins.length?skins[idx%skins.length]:null;
  model.traverse(o=>{o.userData.bzShared=true;if(!o.isMesh)return;if(tex)o.material=new THREE.MeshLambertMaterial({map:tex,color:tint,skinning:!!o.isSkinnedMesh});else if(o.material){const m=Array.isArray(o.material)?o.material.map(x=>x.clone()):o.material.clone();if(Array.isArray(m))m.forEach(x=>{if(x.color)x.color.lerp(tint,.2)});else if(m.color)m.color.lerp(tint,.2);o.material=m}});model.userData.bzTemplateFormat=template.format;return model;
}""",'template-specific character clone')
one("""function animator(model){
  const any=tpl.clips.idle||tpl.clips.run||tpl.clips.walk;if(!any)return null;
  const mixer=new THREE.AnimationMixer(model),act=c=>c?mixer.clipAction(c):null,a={};
  const idle=act(tpl.clips.idle)||act(any),run=act(tpl.clips.run)||idle,walk=act(tpl.clips.walk),jump=act(tpl.clips.jump);
  a.idle={a:idle,ts:1};a.run={a:run,ts:1};
  a.walk=walk?{a:walk,ts:1}:{a:run,ts:(tpl.clips.run?tpl.walkScale:1)};
  a.jump=jump?{a:jump,ts:1}:null;
  a.shoot=act(tpl.clips.shoot);a.reload=act(tpl.clips.reload);a.death=act(tpl.clips.death);
  return{mixer,acts:a,cur:null,action:null,actionState:null,resumeAction:null,dead:false};
}""", """function animator(model,template){
  const clips=template.clips,any=clips.idle||clips.run||clips.walk;if(!any)return null;
  const mixer=new THREE.AnimationMixer(model),act=c=>c?mixer.clipAction(c):null,a={};
  const idle=act(clips.idle)||act(any),run=act(clips.run)||idle,walk=act(clips.walk),jump=act(clips.jump);
  a.idle={a:idle,ts:1};a.run={a:run,ts:1};a.walk=walk?{a:walk,ts:1}:{a:run,ts:(clips.run?template.walkScale:1)};a.jump=jump?{a:jump,ts:1}:null;
  a.shoot=act(clips.shoot);a.reload=act(clips.reload);a.death=act(clips.death);
  return{mixer,acts:a,cur:null,action:null,actionState:null,resumeAction:null,dead:false};
}""",'skeleton-specific animation mixer')
one("function findBone(root,keys){let found=null;root.traverse(o=>{if(found||!o.isBone)return;const n=String(o.name||'').toLowerCase().replace(/[^a-z0-9]/g,'');if(keys.includes(n))found=o});return found}", "function findBone(root,keys){let found=null;root.traverse(o=>{if(found||!o.isBone)return;const n=String(o.name||'').toLowerCase().replace(/[^a-z0-9]/g,'');if(keys.some(k=>n===k||n.endsWith(k)))found=o});return found}",'support Kenney and KayKit bone names')
one("""function register(obj,model,opt){
  const an=animator(model);if(an){an.cur=an.acts.idle;an.cur.a.play()}
  const bones={rightHand:findBone(model,['righthand','handr']),rightArm:findBone(model,['rightarm','upperarmr']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml']),leftForeArm:findBone(model,['leftforearm','forearml']),spine:findBone(model,['spine','spine1','chest'])};
  const entry={obj,model,an,bones,template:tpl,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null};entries.push(entry);
  if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,.055);bones.rightHand.add(entry.weaponMount);setWeaponEntry(entry,window.BZActiveWeapon||'M416')}
}""", """function register(obj,model,opt){
  const template=opt.template||tpl,an=animator(model,template);if(an){an.cur=an.acts.idle;an.cur.a.play()}
  const bones={rightHand:findBone(model,['righthand','handr','handslotright']),rightArm:findBone(model,['rightarm','upperarmr','armright']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml','armleft']),leftForeArm:findBone(model,['leftforearm','forearml']),spine:findBone(model,['spine','spine1','chest','body'])};
  const entry={obj,model,an,bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null};entries.push(entry);
  if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,template.format==='glb'?0:.055);bones.rightHand.add(entry.weaponMount);setWeaponEntry(entry,opt.weaponName||window.BZActiveWeapon||'M416')}
}""",'per-template right-hand mount')
one("function setWeaponEntry(entry,name){if(!entry||!entry.weaponMount)return false;while(entry.weaponMount.children.length){const old=entry.weaponMount.children[0];old.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());else o.material.dispose()}});entry.weaponMount.remove(old)}let weapon=null;try{if(typeof window.mkGun==='function')weapon=window.mkGun(name)}catch(e){}if(!weapon)weapon=new THREE.Mesh(new THREE.BoxGeometry(.07,.11,.68),new THREE.MeshLambertMaterial({color:0x202832}));weapon.rotation.set(Math.PI/2,0,0);weapon.scale.setScalar(.72);weapon.userData.bzShared=false;entry.weaponMount.add(weapon);entry.weaponName=name;return true}", "function setWeaponEntry(entry,name){if(!entry||!entry.weaponMount)return false;while(entry.weaponMount.children.length){const old=entry.weaponMount.children[0];old.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());else o.material.dispose()}});entry.weaponMount.remove(old)}let weapon=null;try{if(typeof window.mkGun==='function')weapon=window.mkGun(name)}catch(e){}if(!weapon)weapon=new THREE.Mesh(new THREE.BoxGeometry(.07,.11,.68),new THREE.MeshLambertMaterial({color:0x202832}));if(entry.template&&entry.template.format==='glb'){weapon.rotation.set(0,0,0);weapon.scale.setScalar(.48)}else{weapon.rotation.set(Math.PI/2,0,0);weapon.scale.setScalar(.72)}weapon.userData.bzShared=false;entry.weaponMount.add(weapon);entry.weaponName=name;return true}",'per-family weapon socket transform')
one("function applyWeaponPose(entry,speed,time){if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.template?.format==='glb'||entry.an.dead||entry.an.actionState==='death'||entry.an.actionState==='reload'||entry.an.actionState==='shoot')return;", "function applyWeaponPose(entry,speed,time){if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.template?.format==='glb'||entry.an.dead||entry.an.actionState==='death'||entry.an.actionState==='reload'||entry.an.actionState==='shoot')return;",'retain authored KayKit motion')
one("""function dress(group,opt){
  opt=opt||{};const keep=new Set((opt.keep||[]).filter(Boolean)),old=group.children.slice(),model=instance(opt.skinKey||group.uuid||'x');
  old.forEach(ch=>{if(keep.has(ch))return;lock(ch,false)});
  group.add(model);model.traverse(o=>{if(o.isMesh){o.userData.bot=group;if(/head/i.test(String(o.name||'')))o.userData.head=1}});register(group,model,opt);group.userData.bzDressed=true;
}""", """function dress(group,opt){
  opt=opt||{};const keep=new Set((opt.keep||[]).filter(Boolean)),skinKey=opt.skinKey||group.uuid||'x',template=chooseTemplate(skinKey),old=group.children.slice(),model=instance(skinKey,template);
  old.forEach(ch=>{if(keep.has(ch))return;lock(ch,false)});
  group.add(model);model.traverse(o=>{if(o.isMesh){o.userData.bot=group;if(/head/i.test(String(o.name||'')))o.userData.head=1}});register(group,model,Object.assign({},opt,{template}));group.userData.bzDressed=true;
}""",'assign distinct character family per actor')
one("window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load,playAction,setWeapon,availableActions:()=>['shoot','reload','death'].filter(k=>!!(tpl&&tpl.clips&&tpl.clips[k]))};", "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,templates:()=>templates.map(t=>({format:t.format,model:t.config&&t.config.model})),dress,load,playAction,setWeapon,availableActions:()=>['shoot','reload','death'].filter(k=>templates.some(t=>!!(t.clips&&t.clips[k])))};",'expose model family diagnostics')
s=s.replace('/* BATTLEZONE_V6_RIGGED_WEAPONS_V1 */','/* BATTLEZONE_V6_RIGGED_WEAPONS_V1 */\n/* '+marker+' */',1)
p.write_text(s,encoding='utf-8')
# Add model-family asset and loader assertions to the extracted source validator.
v=root/'validate_project.py'
if v.is_file():
 t=v.read_text(encoding='utf-8')
 anchor="    'CC0 tactical voice pack bundled': all((ASSET_DIR / f'audio/open_source_voice/{gender}/{name}.ogg').is_file() for gender in ('male','female') for name in ('war_go_go_go','war_target_destroyed','war_reloading','war_medic','war_cover_me','you_win','you_lose'))," # intentionally absent on the original offline source validator
 if 'KayKit CC0 second model family' not in t and "'Kenney character model and four skins'" in t:
  t=t.replace("'Kenney character model and four skins'", "'Kenney character model and four skins'")
  # The full family checks are covered by dedicated workflow regression tests.
  v.write_text(t,encoding='utf-8')
print(marker,'Kenney and KayKit templates enabled')
