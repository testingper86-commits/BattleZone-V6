#!/usr/bin/env python3
"""Enforce world occlusion, weapon aim, vehicle and rigged animation integrity."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
htmls=list(root.rglob('app/src/main/assets/www/index.html'))
models_paths=list(root.rglob('app/src/main/assets/www/js/models.js'))
if len(htmls)!=1 or len(models_paths)!=1: raise SystemExit(f'Expected one index.html and models.js, found {len(htmls)} and {len(models_paths)}')
p=htmls[0]; s=p.read_text(encoding='utf-8'); mp=models_paths[0]; ms=mp.read_text(encoding='utf-8')
world='BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1'; combat='BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1'; animation='BATTLEZONE_V6_ANIMATION_FALLBACK_V1'
if world in s and combat in s and animation in ms:
    print('WORLD_COMBAT_AND_ANIMATION_INTEGRITY_ALREADY_APPLIED'); raise SystemExit(0)
def sub(text,old,new,label):
    n=text.count(old)
    if n!=1: raise SystemExit(f'{label}: expected one exact source anchor, found {n}')
    return text.replace(old,new,1)
if world not in s:
    pairs=[
("function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);return m}","function cyl(x,z,r,h,c,y=0){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),M(c));m.position.set(x,y+h/2,z);S.add(m);solid.push(m);return m}",'cylinder cover'),
("trunk.position.set(x,1.5,z);S.add(trunk);trunk.castShadow=!LQ;","trunk.position.set(x,1.5,z);S.add(trunk);solid.push(trunk);trunk.castShadow=!LQ;",'broadleaf trunk'),
("L.frustumCulled=false;T.frustumCulled=false;S.add(L,T)","L.frustumCulled=false;T.frustumCulled=false;S.add(L,T);solid.push(T)",'instanced forest trunk'),
("function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k))obs.push({x,z,w:1.4,d:1.4});return g}","function pr(k,x,z,ry){const g=mp(x,z,PR[k],ry);(ENV.props[k]=ENV.props[k]||[]).push(g);if(COL.includes(k)){obs.push({x,z,w:1.4,d:1.4});g.traverse(o=>{if(o.isMesh)solid.push(o)})}return g}",'grouped props'),
("t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});for(let k=0;k<3;k++)","t.position.set(x,2.5,z);S.add(t);obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)",'deadfall'),
("function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}","function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist)||dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}",'finite tactical raycast')]
    for a,b,label in pairs:s=sub(s,a,b,label)
    s=sub(s,'</html>',f'<!-- {world} -->\n</html>','world marker')
if combat not in s:
    s=sub(s,'const sp_=P.grip||P.comp?.005:.01;','const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);','aim spread')
    s=sub(s,'g.rotation.y=u.yaw;P.x=r[0];P.z=r[1];fx=fz=0;','g.rotation.y=u.yaw;P.x=g.position.x;P.z=g.position.z;fx=fz=0;','vehicle/player sync')
    s=sub(s,'P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;[P.x,P.z]=hit(P.x,P.z,.5,0);gun.visible=true;','P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);gun.visible=true;','vehicle exit clamp')
    s=sub(s,'</html>',f'<!-- {combat} -->\n</html>','combat marker')
if animation not in ms:
    old_action = """function playAction(target,state){
  if(!target||!['shoot','reload','death'].includes(state))return false;
  const entry=entries.find(e=>e.obj===target);
  if(!entry||!entry.an||!entry.an.acts[state]||entry.an.dead)return false;
  const a=entry.an,action=a.acts[state];
  if(a.action&&a.action!==action)a.action.stop();
  if(a.resumeAction){a.resumeAction.stop();a.resumeAction=null}
  a.resumeAction=a.cur&&a.cur.a&&a.cur.a!==action?a.cur.a:null;
  if(a.resumeAction)a.resumeAction.fadeOut(.06);
  a.cur=null;
  action.reset();action.enabled=true;action.clampWhenFinished=true;
  action.setLoop(THREE.LoopOnce,1);action.setEffectiveTimeScale(1);action.fadeIn(.06).play();
  a.action=action;a.actionState=state;if(state==='death')a.dead=true;
  return true;
}"""
    new_action = """function playAction(target,state){
  if(!target||!['shoot','reload','death'].includes(state))return false;
  const entry=entries.find(e=>e.obj===target);
  if(!entry||!entry.an||entry.an.dead)return false;
  const a=entry.an,action=a.acts[state];
  if(!action){
    if(state==='death'){a.dead=true;a.actionState='death';a.fallbackTimer=0;a.fallbackDuration=0;return true}
    a.action=null;a.actionState=state;a.fallbackDuration=state==='reload'?1.5:.22;a.fallbackTimer=a.fallbackDuration;return true;
  }
  if(a.action&&a.action!==action)a.action.stop();
  if(a.resumeAction){a.resumeAction.stop();a.resumeAction=null}
  a.resumeAction=a.cur&&a.cur.a&&a.cur.a!==action?a.cur.a:null;
  if(a.resumeAction)a.resumeAction.fadeOut(.06);
  a.cur=null;a.fallbackTimer=0;a.fallbackDuration=0;
  action.reset();action.enabled=true;action.clampWhenFinished=true;
  action.setLoop(THREE.LoopOnce,1);action.setEffectiveTimeScale(1);action.fadeIn(.06).play();
  a.action=action;a.actionState=state;if(state==='death')a.dead=true;
  return true;
}"""
    ms=sub(ms,old_action,new_action,'missing-clip procedural action fallback')
    old_entry="const entry={obj,model,an,bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null};entries.push(entry);"
    new_entry="const entry={obj,model,an,bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null,weaponBasePosition:null,weaponBaseRotation:null};entries.push(entry);"
    ms=sub(ms,old_entry,new_entry,'weapon mount base transform state')
    old_register="if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,template.format==='glb'?0:.055);bones.rightHand.add(entry.weaponMount);setWeaponEntry(entry,opt.weaponName||window.BZActiveWeapon||'M416')}"
    new_register="if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,template.format==='glb'?0:.055);bones.rightHand.add(entry.weaponMount);entry.weaponBasePosition=entry.weaponMount.position.clone();entry.weaponBaseRotation=entry.weaponMount.rotation.clone();setWeaponEntry(entry,opt.weaponName||window.BZActiveWeapon||'M416')}"
    ms=sub(ms,old_register,new_register,'weapon mount base transform capture')
    old_pose="function applyWeaponPose(entry,speed,time){if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.template?.format==='glb'||entry.an.dead||entry.an.actionState==='death'||entry.an.actionState==='reload'||entry.an.actionState==='shoot')return;const b=entry.bones,run=Math.min(1,Math.max(0,(speed-1.8)/5.5)),sway=Math.sin(time*10)*.035*run,blend=(bone,x,y,z,w)=>{if(!bone)return;bone.rotation.x=bone.rotation.x*(1-w)+x*w;bone.rotation.y=bone.rotation.y*(1-w)+y*w;bone.rotation.z=bone.rotation.z*(1-w)+z*w};blend(b.rightArm,-.34-sway,.02,.08,.82);blend(b.rightForeArm,-.72,.02,0,.82);blend(b.leftArm,-.58+sway,-.02,-.2,.82);blend(b.leftForeArm,-.88,0,.1,.82);blend(b.spine,.035+run*.045,0,0,.32)}"
    new_pose="""function applyWeaponPose(entry,speed,time){
 if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.an.dead)return;
 const b=entry.bones,state=entry.an.actionState,fallback=!!state&&!entry.an.action&&entry.an.fallbackTimer>0;
 if(entry.weaponBasePosition){entry.weaponMount.position.copy(entry.weaponBasePosition);entry.weaponMount.rotation.copy(entry.weaponBaseRotation)}
 const blend=(bone,x,y,z,w)=>{if(!bone)return;bone.rotation.x=bone.rotation.x*(1-w)+x*w;bone.rotation.y=bone.rotation.y*(1-w)+y*w;bone.rotation.z=bone.rotation.z*(1-w)+z*w};
 if(fallback){
  const progress=Math.max(0,Math.min(1,1-entry.an.fallbackTimer/Math.max(.001,entry.an.fallbackDuration))),pulse=Math.sin(progress*Math.PI);
  if(state==='shoot'){entry.weaponMount.position.z-=.075*pulse;entry.weaponMount.rotation.x-=.11*pulse}
  else if(state==='reload'){entry.weaponMount.position.y-=.075*pulse;entry.weaponMount.rotation.x-=.58*pulse}
  if(entry.template?.format!=='glb'){
   if(state==='shoot'){blend(b.rightArm,-.68,.02,.08,.9);blend(b.rightForeArm,-1.02,.02,0,.9);blend(b.leftArm,-.62,-.02,-.18,.72);blend(b.leftForeArm,-.92,0,.1,.72);blend(b.spine,.08,0,0,.45)}
   else if(state==='reload'){blend(b.rightArm,-.32,.02,.06,.78);blend(b.rightForeArm,-.62,.02,0,.78);blend(b.leftArm,-1.02,-.12,-.55,.92);blend(b.leftForeArm,-1.18,0,.25,.92);blend(b.spine,.04,0,0,.35)}
  }
  return;
 }
 if(entry.template?.format==='glb'||state==='death'||state==='reload'||state==='shoot')return;
 const run=Math.min(1,Math.max(0,(speed-1.8)/5.5)),sway=Math.sin(time*10)*.035*run;
 blend(b.rightArm,-.34-sway,.02,.08,.82);blend(b.rightForeArm,-.72,.02,0,.82);blend(b.leftArm,-.58+sway,-.02,-.2,.82);blend(b.leftForeArm,-.88,0,.1,.82);blend(b.spine,.035+run*.045,0,0,.32)
}"""
    ms=sub(ms,old_pose,new_pose,'procedural fallback weapon and arm poses')
    ms=sub(ms,'    if(e.an){\n      if(e.an.action){','    if(e.an){\n      if(e.an.fallbackTimer>0){e.an.fallbackTimer=Math.max(0,e.an.fallbackTimer-dt);if(e.an.fallbackTimer===0){e.an.actionState=null;e.an.fallbackDuration=0}}\n      if(e.an.action){','fallback action timer')
    ms=ms.replace('/* BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1 */','/* BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1 */\n/* '+animation+' */',1)
mp.write_text(ms,encoding='utf-8')
s=s.replace('</html>',f'<!-- {animation} -->\n</html>',1)
p.write_text(s,encoding='utf-8')
print('WORLD_COMBAT_ANIMATION_INTEGRITY_APPLIED',p,mp)
