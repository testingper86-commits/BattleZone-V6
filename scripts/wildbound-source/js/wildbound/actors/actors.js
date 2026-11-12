/* WILDBOUND_PROCEDURAL_CREATURE_MOTION_V1 */
(()=>{'use strict';
const W=window.WILDBOUND,T=window.THREE;
function mat(color,roughness=.8,metalness=0,emissive=0,emissiveIntensity=0){return new T.MeshStandardMaterial({color,roughness,metalness,emissive,emissiveIntensity})}
function mesh(geometry,material,parent,x=0,y=0,z=0,cast=false){const object=new T.Mesh(geometry,material);object.position.set(x,y,z);object.castShadow=cast;object.receiveShadow=true;parent.add(object);return object}
function group(parent,x=0,y=0,z=0){const object=new T.Group();object.position.set(x,y,z);parent.add(object);return object}
function sphere(parent,material,x,y,z,sx,sy,sz,segments=18,cast=false){const object=mesh(new T.SphereGeometry(1,segments,Math.max(10,Math.floor(segments*.7))),material,parent,x,y,z,cast);object.scale.set(sx,sy,sz);return object}
function loadMonsterVisual(actor,type){
 const state=actor&&actor.userData;if(!state||!T.GLTFLoader)return;
 const files={stalker:'stalker',wraith:'wraithcaller',ironmaw:'ironmaw',king:'hollow_king'},file=files[type];if(!file)return;
 state.modelLoading=true;
 new T.GLTFLoader().load('./models/wildbound/monsters/'+file+'.glb',gltf=>{
  try{
   const visual=gltf.scene;visual.updateMatrixWorld(true);const bounds=new T.Box3().setFromObject(visual),size=new T.Vector3();bounds.getSize(size);if(!(size.y>0))throw new Error('Monster model has no measurable height');
   const joints=[];visual.traverse(node=>{if(node===visual||node.isMesh)return;const name=(node.name||'').toLowerCase(),role=/tail|tentacle/.test(name)?'tail':/jaw|head/.test(name)?'head':/leg|foot|paw/.test(name)?'leg':/arm|wing|claw/.test(name)?'arm':/neck|spine|torso/.test(name)?'body':null;if(role)joints.push({node,role,base:{x:node.rotation.x,y:node.rotation.y,z:node.rotation.z},side:/left|_l\b|\.l\b/.test(name)?-1:/right|_r\b|\.r\b/.test(name)?1:0,phase:joints.length*.73})});
   const targetHeight={stalker:1.62,wraith:1.78,ironmaw:2.08,king:1.82}[type]||1.7,scale=targetHeight/size.y,center=bounds.getCenter(new T.Vector3());visual.scale.setScalar(scale);visual.position.set(-center.x*scale,-bounds.min.y*scale,-center.z*scale);
   visual.traverse(node=>{if(!node.isMesh)return;node.castShadow=true;node.receiveShadow=true;node.frustumCulled=true;const wasArray=Array.isArray(node.material),materials=wasArray?node.material:[node.material],cloned=materials.map(source=>{const material=source.clone();material.roughness=Math.max(.58,material.roughness||.72);material.metalness=Math.min(.12,material.metalness||0);if(type==='wraith'){material.color.multiplyScalar(.78);if(material.emissive){material.emissive.set(0x24164d);material.emissiveIntensity=Math.max(.12,material.emissiveIntensity||0)}}if(type==='king'&&material.emissive){material.emissive.set(0x351b55);material.emissiveIntensity=Math.max(.08,material.emissiveIntensity||0)}return material});node.material=wasArray?cloned:cloned[0]});
   actor.add(visual);state.modelVisual=visual;state.modelJoints=joints;state.modelBaseY=0;state.modelBasePosition={x:visual.position.x,y:visual.position.y,z:visual.position.z};state.modelBaseRotation={x:visual.rotation.x,y:visual.rotation.y,z:visual.rotation.z};state.modelBaseScale={x:visual.scale.x,y:visual.scale.y,z:visual.scale.z};state.modelLoaded=true;state.modelLoading=false;state.modelHeight=targetHeight;actor.children.forEach(child=>{if(child!==visual&&child!==state.aura&&child!==state.core)child.visible=false});
   if(state.core){state.core.position.set(0,targetHeight*.69,.04);state.core.scale.set(.14,.14,.14);state.coreBaseScale={x:.14,y:.14,z:.14};state.weakPoint=state.core}
   if(state.aura){state.aura.scale.setScalar(type==='king'?1.55:type==='wraith'?1.28:1.08);state.aura.material.opacity=type==='wraith'?.13:type==='king'?.09:.045}
  }catch(error){state.modelLoading=false;state.modelLoadFailed=true;console.warn('[WILDBOUND] monster model rejected:',file,error)}
 },undefined,error=>{state.modelLoading=false;state.modelLoadFailed=true;console.warn('[WILDBOUND] monster model unavailable:',file,error)});
}
W.actors={
 hunter(scene){
  const root=new T.Group(),armor=mat(0x263d42,.46,.42),dark=mat(0x111a1d,.38,.38),cloth=mat(0x18252c,.92),skin=mat(0xb88f78,.72),glow=mat(0x7bd8c3,.24,.35,0x286e62,.55),gold=mat(0xc3a66c,.36,.62);
  scene.add(root);
  const pelvis=sphere(root,cloth,0,.88,0,.28,.2,.2,18,true),torso=sphere(root,armor,0,1.23,0,.37,.52,.25,22,true),chest=mesh(new T.SphereGeometry(1,22,16),dark,root,0,1.28,.16,true);chest.scale.set(.32,.36,.12);
  sphere(root,gold,0,1.35,.245,.2,.2,.035,16,true);
  const neck=mesh(new T.CylinderGeometry(.1,.13,.18,12),skin,root,0,1.66,0,true),head=group(root,0,1.78,.01);
  sphere(head,skin,0,0,0,.2,.25,.19,20,true);sphere(head,cloth,0,.13,-.02,.23,.17,.2,18,true);
  mesh(new T.BoxGeometry(.28,.055,.055),glow,head,0,.025,.18,true);
  const arms=[],legs=[],shoulderPads=[];
  for(const side of [-1,1]){
   const shoulder=group(root,side*.36,1.46,0);sphere(shoulder,armor,0,-.06,0,.18,.19,.18,16,true);sphere(shoulder,gold,0,.02,.02,.19,.09,.19,16,true);
   mesh(new T.CylinderGeometry(.105,.13,.38,12),armor,shoulder,0,-.27,0,true);
   const elbow=group(shoulder,0,-.47,.02);sphere(elbow,dark,0,0,0,.12,.12,.12,14,true);mesh(new T.CylinderGeometry(.085,.11,.31,12),armor,elbow,0,-.16,.015,true);sphere(elbow,glow,0,-.31,.035,.1,.08,.11,14,true);
   const hand=group(elbow,0,-.34,.04);sphere(hand,dark,0,0,0,.11,.1,.1,14,true);for(let finger=0;finger<3;finger++){const claw=mesh(new T.ConeGeometry(.025,.13,7),gold,(hand),-.055+finger*.055,-.09,.07,true);claw.rotation.x=.42}
   arms.push(shoulder);shoulderPads.push(shoulder.children[1]);
   const hip=group(root,side*.16,.82,0);sphere(hip,cloth,0,-.12,0,.16,.24,.17,16,true);mesh(new T.CylinderGeometry(.12,.145,.32,12),cloth,hip,0,-.29,0,true);
   const knee=group(hip,0,-.47,.015);sphere(knee,dark,0,0,0,.13,.12,.13,14,true);mesh(new T.CylinderGeometry(.095,.12,.3,12),armor, knee,0,-.16,0,true);sphere(knee,gold,0,-.29,.025,.12,.09,.14,14,true);mesh(new T.BoxGeometry(.19,.12,.3),dark,knee,0,-.37,.08,true);
   legs.push(hip);
  }
  const belt=mesh(new T.TorusGeometry(.28,.035,8,24),gold,root,0,.94,0,true);belt.rotation.x=Math.PI/2;
  const backplate=mesh(new T.BoxGeometry(.34,.48,.1),dark,root,0,1.27,-.22,true);backplate.rotation.x=-.12;
  const blade=mesh(new T.BoxGeometry(.075,.82,.11),gold,root,.43,1.08,-.2,true);blade.rotation.z=-.34;
  const scarf=mesh(new T.BoxGeometry(.52,.11,.48),glow,root,0,1.5,-.1,true);scarf.rotation.x=.42;
  root.userData={arms,legs,body:[pelvis,torso,chest,neck,head,backplate,blade],head,torso,shoulderPads};
  return root;
 },
 monster(scene,type,x,z){
  const defs=W.data.monsters[type];if(!defs)throw new Error('Unknown WILDBOUND monster archetype: '+type);
  const stalker=type==='stalker',wraith=type==='wraith',ironmaw=type==='ironmaw',king=type==='king';
  const root=new T.Group(),skin=mat(defs.c,wraith?.38:ironmaw?.74:.62,.22,wraith?0x392f79:0x000000,wraith?.2:0),dark=mat(0x111a1d,.42,.32),bone=mat(0xb6a17a,.66,.12),accent=mat(king?0x9d78c7:wraith?0x7664b7:0x7ac8ad,.28,.48,king?0x5d318c:wraith?0x3e2c91:0x174b3d,.8),eye=mat(wraith?0xb4a2ff:0xe98a5d,.2,.12,wraith?0x8064ff:0xff4e18,2.2),coreMaterial=mat(king?0xc7a2ff:0x8cebd8,.22,.25,king?0x8a40ff:0x38d7b1,2.8);
  scene.add(root);root.position.set(x,0,z);
  const width=ironmaw?1.28:king?1.12:wraith?.72:.82,height=defs.h;
  const torso=sphere(root,skin,0,height*.53,0,defs.r*width, height*(ironmaw?.27:.31),defs.r*.72,24,true);
  sphere(root,skin,0,height*.29,-.015,defs.r*(ironmaw?1.02:.66),height*.16,defs.r*.64,20,true);
  const ribPlate=sphere(root,dark,0,height*.58,defs.r*.37,defs.r*(ironmaw?.78:.56),height*.21,defs.r*.2,20,true);
  sphere(root,bone,0,height*.47,defs.r*.48,defs.r*.34,height*.09,.055,18,true);
  const core=sphere(root,coreMaterial,0,height*.57,defs.r*.59,defs.r*(king?.2:.14),height*(king?.12:.09),.07,20,true);
  const head=group(root,0,height*.84,defs.r*.05);
  sphere(head,skin,0,0,0,defs.r*(ironmaw?.48:.36),height*.13,defs.r*.34,22,true);
  sphere(head,dark,0,-height*.095,defs.r*.19,defs.r*(ironmaw?.46:.3),height*.065,defs.r*.22,18,true);
  sphere(head,bone,0,-height*.13,defs.r*.36,defs.r*(ironmaw?.35:.23),height*.045,.07,18,true);
  const eyes=[];
  for(const side of [-1,1]){
   const eyeSocket=sphere(head,dark,side*defs.r*.16,height*.015,defs.r*.27,.105,.075,.045,14,true);
   const eyeMesh=sphere(head,eye,side*defs.r*.16,height*.018,defs.r*.31,.065,.052,.025,14,true);eyes.push(eyeMesh);
   const brow=mesh(new T.ConeGeometry(defs.r*.1,height*.13,8),bone,head,side*defs.r*.18,height*.105,defs.r*.2,true);brow.rotation.z=side*-.42;
   const horn=mesh(new T.ConeGeometry(defs.r*(king?.16:.12),height*(king?.3:.18),9),dark,head,side*defs.r*.29,height*.15,-defs.r*.04,true);horn.rotation.z=side*.52;
  }
  const jaw=mesh(new T.BoxGeometry(defs.r*(ironmaw?.82:.55),height*.07,defs.r*.22),dark,head,0,-height*.17,defs.r*.27,true);jaw.rotation.x=-.12;
  for(let tooth=0;tooth<(ironmaw?8:4);tooth++){
   const side=tooth%2?1:-1,index=Math.floor(tooth/2),tusk=mesh(new T.ConeGeometry(ironmaw?.055:.035,ironmaw?.32:.2,7),bone,head,side*(defs.r*.12+index*defs.r*.11),-height*.12,defs.r*.37,true);tusk.rotation.z=side*.18;
  }
  const arms=[],legs=[];
  const armCount=king?4:2;
  for(let i=0;i<armCount;i++){
   const side=i%2?1:-1,lowerPair=i>=2,shoulderY=height*(lowerPair?.48:.69),armScale=ironmaw?1.2:wraith?1.15:stalker?1.1:1;
   const shoulder=group(root,side*defs.r*(lowerPair?.58:.7),shoulderY,0);
   sphere(shoulder,skin,0,-height*.035,0,defs.r*.22*armScale,height*.105,defs.r*.2,18,true);
   sphere(shoulder,accent,side*defs.r*.08,-height*.06,-defs.r*.08,defs.r*.22,height*.1,defs.r*.18,16,true);
   const upper=mesh(new T.CylinderGeometry(defs.r*.13*armScale,defs.r*.18*armScale,height*.22,12),skin,shoulder,0,-height*.16,0,true);upper.rotation.z=side*.12;
   const elbow=group(shoulder,0,-height*.27,defs.r*.015);sphere(elbow,dark,0,0,0,defs.r*.14,height*.055,defs.r*.14,14,true);
   const forearm=mesh(new T.CylinderGeometry(defs.r*.1*armScale,defs.r*.17*armScale,height*.22,12),skin,elbow,0,-height*.12,defs.r*.02,true);forearm.rotation.z=-side*.08;
   sphere(elbow,bone,0,-height*.19,defs.r*.05,defs.r*.14,height*.08,defs.r*.12,16,true);
   const palm=group(elbow,0,-height*.25,defs.r*.04);sphere(palm,dark,0,0,0,defs.r*.12,height*.055,defs.r*.13,14,true);
   for(let claw=0;claw<4;claw++){
    const offset=(claw-1.5)*defs.r*.075,finger=mesh(new T.CylinderGeometry(.025,.04,height*.09,7),dark,palm,offset,-height*.07,defs.r*.07,true);finger.rotation.z=(claw-1.5)*.12;
    const tip=mesh(new T.ConeGeometry(.035,height*.13,7),bone,palm,offset,-height*.16,defs.r*.09,true);tip.rotation.x=.3;tip.rotation.z=(claw-1.5)*.12;
   }
   arms.push(shoulder);
  }
  for(const side of [-1,1]){
   const hip=group(root,side*defs.r*(ironmaw?.36:.28),height*.29,0);
   sphere(hip,skin,0,-height*.08,0,defs.r*(ironmaw?.3:.2),height*.14,defs.r*.23,18,true);
   mesh(new T.CylinderGeometry(defs.r*(ironmaw?.22:.14),defs.r*(ironmaw?.18:.12),height*.2,12),skin,hip,0,-height*.19,0,true);
   const knee=group(hip,0,-height*.29,0);sphere(knee,dark,0,0,0,defs.r*.17,height*.07,defs.r*.17,16,true);
   mesh(new T.CylinderGeometry(defs.r*.12,defs.r*(ironmaw?.19:.14),height*.22,12),dark,knee,0,-height*.12,0,true);
   sphere(knee,accent,0,-height*.22,defs.r*.045,defs.r*.16,height*.06,defs.r*.18,16,true);
   mesh(new T.BoxGeometry(defs.r*.36,height*.07,defs.r*.42),dark,knee,0,-height*.29,defs.r*.12,true);
   legs.push(hip);
  }
  if(stalker){
   for(let i=0;i<7;i++){const spike=mesh(new T.ConeGeometry(.12,.48,7),bone,root,Math.sin(i*.7)*defs.r*.38,height*.42+i*height*.055,-defs.r*.55,true);spike.rotation.x=-.55;spike.rotation.z=Math.sin(i)*.22}
   sphere(root,dark,0,height*.64,-defs.r*.45,defs.r*.2,height*.18,.12,16,true);
  }
  if(wraith){
   for(let i=0;i<6;i++){const side=i%2?1:-1,veil=mesh(new T.ConeGeometry(defs.r*.17,height*(.55+(i%3)*.12),9),accent,root,side*defs.r*(.25+i*.08),height*(.25+(i%2)*.08),-defs.r*.48,true);veil.rotation.z=side*(.18+i*.06);veil.rotation.x=-.3}
   const shroud=sphere(root,accent,0,height*.43,-defs.r*.2,defs.r*.82,height*.42,defs.r*.18,22,true);shroud.material.transparent=true;shroud.material.opacity=.16;shroud.material.depthWrite=false;
  }
  if(ironmaw){
   for(let i=0;i<6;i++){const side=i%2?1:-1,plate=sphere(root,dark,side*defs.r*.68,height*(.38+i*.065),-defs.r*.04,.2,.14,.24,14,true);plate.rotation.z=side*.35;const spine=mesh(new T.ConeGeometry(.17,.62,7),bone,root,side*defs.r*.62,height*(.56+i*.045),-defs.r*.28,true);spine.rotation.z=side*.42}
   for(const side of [-1,1]){const tusk=mesh(new T.ConeGeometry(.14,.7,9),bone,head,side*defs.r*.28,-height*.02,defs.r*.23,true);tusk.rotation.z=side*.7}
  }
  if(king){
   for(let i=0;i<14;i++){const a=i*Math.PI/7,spike=mesh(new T.ConeGeometry(.14,.88+(i%3)*.18,8),accent,root,Math.cos(a)*defs.r*1.08,height*.73+(i%2)*.16,Math.sin(a)*defs.r*.78,true);spike.rotation.z=Math.cos(a)*.72;spike.rotation.x=Math.sin(a)*.55}
   const crown=mesh(new T.TorusGeometry(defs.r*.48,.09,8,32),bone,root,0,height*.96,0,true);crown.rotation.x=Math.PI/2;
   for(let i=0;i<5;i++){const a=i*Math.PI*2/5,tip=mesh(new T.ConeGeometry(.09,.48,8),accent,root,Math.cos(a)*defs.r*.48,height*1.08,Math.sin(a)*defs.r*.48,true);tip.rotation.z=Math.cos(a)*.5;tip.rotation.x=Math.sin(a)*.5}
  }
  const aura=mesh(new T.SphereGeometry(defs.r*(king?2.05:wraith?1.8:1.42),20,14),accent,root,0,height*.52,0);aura.material.transparent=true;aura.material.opacity=king?.075:wraith?.1:.055;aura.material.depthWrite=false;aura.material.side=T.BackSide;
  root.userData={type,hp:defs.hp,maxHp:defs.hp,damage:defs.damage,speed:defs.sp,range:defs.range,kind:defs.kind,alive:true,phase:1,attackCd:1.2,stagger:0,weakUntil:0,weakPoint:core,aura,body:torso,torso,head,core,coreBaseScale:{x:core.scale.x,y:core.scale.y,z:core.scale.z},eyes,arms,legs,baseY:0,hitFlash:0,seed:Math.random()*10,root,attackState:'idle',attackWindup:0,attackRecovery:0,patrolPhase:Math.random()*Math.PI*2,spawnX:x,spawnZ:z,roamRadius:king?0:10,patrolRadius:king?0:10,noticeRange:wraith?30:26,attackReach:wraith?15:stalker?defs.range*1.38:ironmaw?defs.range*1.55:defs.range*1.28,attackProfile:stalker?{windup:.28,recovery:.48,damageScale:1,reachScale:1.38,attack:'lunge'}:ironmaw?{windup:.92,recovery:1.12,damageScale:1.3,reachScale:1.55,attack:'slam'}:{windup:.5,recovery:.62,damageScale:1,reachScale:1.28,attack:'claw'},hitRadius:defs.r*.85,r:defs.r};
  loadMonsterVisual(root,type);
  return root;
 },
 loadRigged(groups){const THREE=T;return new Promise(resolve=>{
  const path='./models/wildbound/hunter/hunter.glb';if(!THREE.GLTFLoader||!Array.isArray(groups)||!groups.length){resolve(false);return}
  const attach=(target,rig,animations)=>{
   const box=new THREE.Box3().setFromObject(rig),size=new THREE.Vector3();box.getSize(size);if(!size.y)throw new Error('Rigged hunter model has no height');const scale=1.82/size.y;rig.scale.setScalar(scale);rig.position.y=-box.min.y*scale;rig.traverse(object=>{if(object.isMesh){object.frustumCulled=true;object.castShadow=true;object.receiveShadow=true}});
   target.children.forEach(child=>{child.visible=false});target.add(rig);target.updateMatrixWorld(true);
   const blade=target.userData&&target.userData.body&&target.userData.body[6],hand=rig.getObjectByName('scout:wrist.R');if(blade&&hand){hand.attach(blade);blade.visible=true;blade.castShadow=true;blade.receiveShadow=true}
   const mixer=new THREE.AnimationMixer(rig),clips={idle:null,walk:null,run:null,attack:null,block:null,dodge:null,jump:null,hit:null,defeat:null};
   for(const clip of animations){const name=clip.name.toLowerCase();if(name==='idle')clips.idle=clip;else if(name==='walk')clips.walk=clip;else if(name==='run')clips.run=clip;else if(name==='grasp'){clips.attack=clip;clips.block=clip;clips.hit=clip}}
   clips.dodge=clips.run;clips.jump=clips.run;clips.defeat=clips.idle;const actionByClip=new Map(),actions={};Object.keys(clips).forEach(name=>{const clip=clips[name];if(clip){let action=actionByClip.get(clip);if(!action){action=mixer.clipAction(clip);actionByClip.set(clip,action)}actions[name]=action}});
   const state={mixer,actions,current:null,lockUntil:0,model:rig,baseY:rig.position.y,play(name,once=false){const action=actions[name]||actions.idle,clip=clips[name]||clips.idle;if(!action)return;if(this.current!==action||once){if(this.current&&this.current!==action)this.current.fadeOut(.12);action.reset();action.enabled=true;action.setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);action.clampWhenFinished=once;action.fadeIn(.12).play();this.current=action}if(once)this.lockUntil=performance.now()+((clip&&clip.duration)||.5)*1000}};
   target.userData.rig=state;state.play('idle');
  };
  new THREE.GLTFLoader().load(path,gltf=>{try{attach(groups[0],gltf.scene,gltf.animations);const extras=groups.slice(1).map(target=>new Promise(done=>new THREE.GLTFLoader().load(path,extra=>{try{attach(target,extra.scene,extra.animations);done(true)}catch(error){console.warn('[WILDBOUND] extra hunter rig rejected:',error);done(false)}},undefined,error=>{console.warn('[WILDBOUND] extra hunter rig unavailable:',error);done(false)})));Promise.all(extras).then(results=>{W.bus.emit('rig-ready');resolve(results.every(Boolean))})}catch(error){console.warn('[WILDBOUND] hunter model rejected:',error);groups.forEach(target=>target.children.forEach(child=>{if(!child.userData||!child.userData.rig)child.visible=true}));resolve(false)}},undefined,error=>{console.warn('[WILDBOUND] hunter model unavailable:',error);resolve(false)});
 })},
 play(actor,name,once=true){if(actor&&actor.userData&&actor.userData.rig)actor.userData.rig.play(name,once)},
 updateMonster(actor,dt,now){const state=actor&&actor.userData;if(!state)return;const gait=now*.0018+(state.seed||0),moving=state.attackState==='pursuit'||state.attackState==='patrol',windup=state.attackState==='windup',attacking=state.attackState==='attack',recovering=state.attackState==='recovery',stride=moving?1:0,anticipation=windup?1:0,strike=attacking?1:0,recoil=recovering?1:0;state.legs.forEach((leg,index)=>{const phase=gait+index*Math.PI;leg.rotation.x=Math.sin(phase)*(moving?.48:.045);leg.rotation.z=Math.sin(phase*.5)*.035});state.arms.forEach((arm,index)=>{const phase=gait+index*Math.PI;arm.rotation.x=windup?-.82:attacking?-1.18:moving?Math.sin(phase+1)*.18:Math.sin(phase)*.035;arm.rotation.z=(index%2?1:-1)*(windup?.16:moving?Math.sin(phase)*.08:.025)});if(state.head)state.head.rotation.x=windup?-.16:Math.sin(gait*.65)*.035;if(state.core){const pulse=1+Math.sin(gait*2.4)*.055,base=state.coreBaseScale;state.core.scale.set(base.x*pulse,base.y*pulse,base.z*pulse)}if(state.modelVisual){const visual=state.modelVisual,base=state.modelBasePosition||{x:0,y:0,z:0},rotation=state.modelBaseRotation||{x:0,y:0,z:0},scale=state.modelBaseScale||{x:1,y:1,z:1},breath=Math.sin(gait*1.3),sway=Math.sin(gait*.72);visual.position.x=base.x;visual.position.y=base.y+(moving?Math.abs(Math.sin(gait*1.7))*.035:.012+breath*.009)-anticipation*.045+strike*.025+recoil*.018;visual.position.z=base.z-anticipation*.09+strike*(state.type==='king'?.24:.16)+recoil*.045;visual.rotation.x=rotation.x-anticipation*.13+strike*.19+recoil*.075+(moving?Math.sin(gait*1.7)*.025:0);visual.rotation.y=rotation.y+(moving?sway*.035:Math.sin(gait*.38)*.012);visual.rotation.z=rotation.z+(moving?Math.sin(gait)*.035:0)+anticipation*.035;visual.scale.set(scale.x*(1+strike*.025),scale.y*(1+breath*.006-anticipation*.035+strike*.018),scale.z*(1+strike*.025));(state.modelJoints||[]).forEach(joint=>{const node=joint.node,baseJoint=joint.base,phase=gait+joint.phase,side=joint.side||Math.sin(joint.phase);let x=0,y=0,z=0;if(joint.role==='tail'){y=Math.sin(phase*.85)*.22;z=Math.cos(phase*.7)*.1+anticipation*.12} else if(joint.role==='head'){x=anticipation*-.2+strike*.12+Math.sin(phase*.55)*.025;y=Math.sin(phase*.6)*.035} else if(joint.role==='leg'){x=Math.sin(phase)*(stride?.42:.018)+anticipation*.08-strike*.12;z=side*.025} else if(joint.role==='arm'){x=anticipation*-.42+strike*-.28+Math.sin(phase)*stride*.16;z=side*(anticipation*.12+Math.sin(phase)*stride*.06)} else if(joint.role==='body'){x=anticipation*-.07+strike*.09;y=Math.sin(phase*.45)*.018}node.rotation.set(baseJoint.x+x,baseJoint.y+y,baseJoint.z+z)})}if(state.aura){state.aura.rotation.y+=dt*(state.type==='king'?.48:.25);state.aura.scale.setScalar((state.type==='king'?1.55:state.type==='wraith'?1.28:1.08)*(1+Math.sin(gait*1.8)*.035+anticipation*.08+strike*.12))}if(state.eyes)state.eyes.forEach(eye=>{if(eye.material&&eye.material.emissive)eye.material.emissiveIntensity=(state.type==='king'?2.8:2.2)+(anticipation+strike)*.9+Math.sin(gait*2)*.18})},
 updateHunter(actor,dt,moving,attacking){const state=actor&&actor.userData;if(!state)return;if(state.rig){const rig=state.rig;if(performance.now()>=rig.lockUntil)rig.play(attacking?'attack':moving?'run':'idle',attacking);rig.mixer.update(Math.min(dt,.05));if(rig.model){const now=performance.now();rig.model.position.y=rig.baseY+(moving?Math.abs(Math.sin(now*.012))*.016:0);rig.model.rotation.z=moving?Math.sin(now*.009)*.012:0}return}state.body.forEach((part,index)=>{if(index<2)part.rotation.x=moving?Math.sin(performance.now()*.009+index)*.08:0});state.legs.forEach((leg,index)=>leg.rotation.x=moving?Math.sin(performance.now()*.012+index*Math.PI)*.58:0);state.arms.forEach((arm,index)=>arm.rotation.x=attacking?-.9:moving?Math.sin(performance.now()*.01+index*Math.PI)*.28:0)}
};
})();
