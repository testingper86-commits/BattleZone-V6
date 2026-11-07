#!/usr/bin/env python3
"""Enforce world occlusion, weapon aim, vehicle and rigged animation integrity."""
from pathlib import Path
import hashlib
import shutil
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
htmls=list(root.rglob('app/src/main/assets/www/index.html'))
models_paths=list(root.rglob('app/src/main/assets/www/js/models.js'))
if len(htmls)!=1 or len(models_paths)!=1: raise SystemExit(f'Expected one index.html and models.js, found {len(htmls)} and {len(models_paths)}')
p=htmls[0]; s=p.read_text(encoding='utf-8'); mp=models_paths[0]; ms=mp.read_text(encoding='utf-8')
world='BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1'; combat='BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1'; animation='BATTLEZONE_V6_ANIMATION_FALLBACK_V1'; los='BATTLEZONE_V6_TACTICAL_LINE_OF_SIGHT_V1'; frame='BATTLEZONE_V6_FRAME_LOOP_EFFICIENCY_V1'; version='BATTLEZONE_V6_BUILD_VERSION_1_2_2'; voice='BATTLEZONE_V6_CC0_VOICEOVER_V1'; vehicle='BATTLEZONE_V6_VEHICLE_COLLISION_DAMAGE_V1'
gradle_paths=list(root.rglob('app/build.gradle.kts'))
if len(gradle_paths)!=1: raise SystemExit(f'Expected one app/build.gradle.kts, found {len(gradle_paths)}')
gp=gradle_paths[0]; gs=gp.read_text(encoding='utf-8'); www=p.parent
voice_repo=Path(__file__).resolve().parents[1]/'assets'/'kenney_voiceover_cc0'
voice_dest=www/'audio'/'cc0_voiceover'
voice_lines=['war_call_for_backup','war_cover_me','war_fire_in_the_hole','war_get_down','war_go_go_go','war_look_out','war_medic','war_reloading','war_rpg','war_sniper','war_suppressing_fire','war_target_destroyed','war_target_engaged','war_watch_my_back','mission_completed','mission_failed','you_win','you_lose','ready','go','hurry_up','objective_achieved']
voice_rel=[f'{gender}/{line}.ogg' for gender in ('Male','Female') for line in voice_lines]
manifest_path=voice_repo/'manifest.sha256'
if not voice_repo.is_dir() or not manifest_path.is_file(): raise SystemExit('Verified Kenney CC0 voice asset source or hash manifest is missing')
manifest={}
for row in manifest_path.read_text(encoding='utf-8').splitlines():
    parts=row.split()
    if len(parts)!=2: raise SystemExit('Malformed CC0 voice SHA-256 manifest')
    manifest[parts[1]]=parts[0]
if set(manifest)!=set(voice_rel): raise SystemExit('CC0 voice manifest does not match the exact 44-file allowlist')
if 'Creative Commons Zero, CC0' not in (voice_repo/'License.txt').read_text(encoding='utf-8') or 'Jeffrey M. Smith' not in (voice_repo/'Credits.txt').read_text(encoding='utf-8') or 'Giselle' not in (voice_repo/'Credits.txt').read_text(encoding='utf-8'): raise SystemExit('CC0 voice licence or performer credits are incomplete')
for rel in voice_rel:
    f=voice_repo/rel
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=manifest[rel]: raise SystemExit(f'CC0 voice asset failed SHA-256 verification: {rel}')
voice_ready=voice in s and all((voice_dest/rel).is_file() for rel in voice_rel) and not (www/'audio'/'voicepacks').exists()
if world in s and combat in s and animation in ms and los in s and frame in s and version in gs and voice_ready and 'const bzLosRayState=' in s and vehicle in s:
    print('WORLD_COMBAT_ANIMATION_CC0_VOICE_AND_VERSION_INTEGRITY_ALREADY_APPLIED'); raise SystemExit(0)
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
("function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}","const bzLosRayState={ray:new THREE.Raycaster(),origin:new THREE.Vector3(),direction:new THREE.Vector3(),hits:[]};\nfunction hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist))return false;if(dist<.2)return true;const state=bzLosRayState;state.origin.set(ax,ay,az);state.direction.set(dx,dy,dz).normalize();state.ray.set(state.origin,state.direction);state.ray.near=.15;state.ray.far=Math.max(.15,dist-.35);state.hits.length=0;state.ray.intersectObjects(solid,false,state.hits);return state.hits.length===0}",'reused tactical raycaster and intersection buffer')]
    for a,b,label in pairs:s=sub(s,a,b,label)
    s=sub(s,'</html>',f'<!-- {world} -->\n</html>','world marker')
if 'const bzLosRayState=' not in s:
    old_ray="function hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist))return false;if(dist<.2)return true;const ray=new THREE.Raycaster(new THREE.Vector3(ax,ay,az),new THREE.Vector3(dx,dy,dz).normalize(),.15,Math.max(.15,dist-.35));return ray.intersectObjects(solid,false).length===0}"
    new_ray="const bzLosRayState={ray:new THREE.Raycaster(),origin:new THREE.Vector3(),direction:new THREE.Vector3(),hits:[]};\nfunction hasClearShot(ax,ay,az,bx,by,bz){const dx=bx-ax,dy=by-ay,dz=bz-az,dist=Math.hypot(dx,dy,dz);if(!Number.isFinite(dist))return false;if(dist<.2)return true;const state=bzLosRayState;state.origin.set(ax,ay,az);state.direction.set(dx,dy,dz).normalize();state.ray.set(state.origin,state.direction);state.ray.near=.15;state.ray.far=Math.max(.15,dist-.35);state.hits.length=0;state.ray.intersectObjects(solid,false,state.hits);return state.hits.length===0}"
    s=sub(s,old_ray,new_ray,'upgrade previously patched tactical raycaster')
if combat not in s:
    s=sub(s,'const sp_=P.grip||P.comp?.005:.01;','const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);','aim spread')
    s=sub(s,'g.rotation.y=u.yaw;P.x=r[0];P.z=r[1];fx=fz=0;','g.rotation.y=u.yaw;P.x=g.position.x;P.z=g.position.z;fx=fz=0;','vehicle/player sync')
    s=sub(s,'P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;[P.x,P.z]=hit(P.x,P.z,.5,0);gun.visible=true;','P.z=old.position.z-Math.sin(old.userData.yaw)*2.4;const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);gun.visible=true;','vehicle exit clamp')
    s=sub(s,'</html>',f'<!-- {combat} -->\n</html>','combat marker')
if vehicle not in s:
    vehicle_helper="""function bzV6ApplyVehicleImpact(g,u,impact,x,z){
 if(!Number.isFinite(impact)||impact<=6||(Number(u.crashCd)||0)>0)return false;
 u.hp=(Number.isFinite(u.hp)?u.hp:100)-Math.min(35,(impact-5)*1.8);
 u.crashCd=1;
 E.fx('spark',x,.7,z,6);
 if(u.hp<=0&&!u.dead){u.dead=1;u.v=0;E.ignite(g.position.x,g.position.z,22,'veh',.8);return true}
 return false;
}"""
    s=sub(s,'function loop0(n){',vehicle_helper+'\nfunction loop0(n){','vehicle collision impact helper')
    s=sub(s,'Object.assign({v:0,yaw:rnd(0,6),a,vw:w,vl:l},o)','Object.assign({v:0,yaw:rnd(0,6),a,vw:w,vl:l,hp:100,crashCd:0},o)','vehicle health initialization')
    s=sub(s,'if(P.veh){const g=P.veh,u=g.userData;u.v+=','if(P.veh){const g=P.veh,u=g.userData;u.crashCd=Math.max(0,(Number(u.crashCd)||0)-dt);u.v+=','vehicle collision cooldown')
    s=sub(s,'if(r[0]!=nx||r[1]!=nz)u.v*=.3;','if(r[0]!=nx||r[1]!=nz){bzV6ApplyVehicleImpact(g,u,Math.abs(u.v),nx,nz);u.v*=.3;}','vehicle collision damage')
    s=s.replace('</html>',f'<!-- {vehicle} -->\n</html>',1)
if los not in s:
    if 'if(!Number.isFinite(dist)||dist<.2)return true;' in s:
        s=sub(s,'if(!Number.isFinite(dist)||dist<.2)return true;','if(!Number.isFinite(dist))return false;if(dist<.2)return true;','reject non-finite tactical raycasts')
    elif 'if(!Number.isFinite(dist))return false;if(dist<.2)return true;' not in s:
        raise SystemExit('Tactical raycast finite-distance guard is missing')
    s=sub(s," const maxRange=([30,40,55][DF]||40)*Math.max(.55,Number(ENV.vis)||1);", " const maxRange=([30,40,55][DF]||40)*Math.max(.55,Number(ENV.vis)||1);\n u.aiBlockedT=Math.max(0,(Number(u.aiBlockedT)||0)-dt);\n if(u.aiBlockedT===0){u.aiBlockedTarget=null;u.aiBlockedPlayer=false}",'enemy AI blocked-target cooldown')
    s=sub(s,'   if(!Number.isFinite(x)||!Number.isFinite(z))return;\n   const d=Math.hypot(x-bot.position.x,z-bot.position.z);', '   if(!Number.isFinite(x)||!Number.isFinite(z))return;\n   if(candidate.p&&u.aiBlockedPlayer)return;\n   if(candidate.o&&candidate.o===u.aiBlockedTarget)return;\n   const d=Math.hypot(x-bot.position.x,z-bot.position.z);','enemy AI skips temporarily occluded targets')
    s=sub(s,'  target=chosen;u.aiTarget=target;', "  target=chosen;\n  if(target){\n   const targetY=target.p?(P.y-.25):(target.o.position.y+1.1);\n   if(!hasClearShot(bot.position.x,bot.position.y+1.15,bot.position.z,target.x,targetY,target.z)){\n    u.aiBlockedPlayer=!!target.p;u.aiBlockedTarget=target.o||null;u.aiBlockedT=1.0;target=null;\n   }\n  }\n  u.aiTarget=target;",'enemy AI requires visible target acquisition')
    s=sub(s,'al.forEach((a,i)=>{const u=a.userData;if(u.down||u.alive===false)return;u.cd=(u.cd||0)-dt;u.squadThink=(u.squadThink||0)-dt;', 'al.forEach((a,i)=>{const u=a.userData;if(u.down||u.alive===false)return;u.cd=(u.cd||0)-dt;u.squadThink=(u.squadThink||0)-dt;u.squadBlockedT=Math.max(0,(Number(u.squadBlockedT)||0)-dt);u.squadLosT=Math.max(0,(Number(u.squadLosT)||0)-dt);if(u.squadBlockedT===0)u.squadBlockedTarget=null;', 'squad AI line-of-sight cooldown state')
    s=sub(s,'if(!v.alive||v.ally||v.airDrop||v.falling)return;', 'if(!v.alive||v.ally||v.airDrop||v.falling||o===u.squadBlockedTarget)return;', 'squad AI skips temporarily occluded targets')
    s=sub(s,'/* BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1 */',"function bzV6ValidateSquadTarget(actor,u,target){\n if(!target)return null;\n if(target===u.squadBlockedTarget&&u.squadBlockedT>0)return null;\n if(u.squadLosT>0&&u.squadLosTarget===target)return target;\n u.squadLosT=.22;u.squadLosTarget=target;\n if(!hasClearShot(actor.position.x,actor.position.y+1.15,actor.position.z,target.position.x,target.position.y+1.1,target.position.z)){u.squadBlockedTarget=target;u.squadBlockedT=1.0;return null}\n return target;\n}\n/* BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1 */",'extractable squad target visibility validator')
    s=sub(s,"if(window.BZSquadOrders?.get()==='regroup'&&Math.hypot(px-a.position.x,pz-a.position.z)>12)en=null;let bd=en?Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z):96;","if(window.BZSquadOrders?.get()==='regroup'&&Math.hypot(px-a.position.x,pz-a.position.z)>12)en=null;en=bzV6ValidateSquadTarget(a,u,en);if(!en)u.squadTargetObj=null;let bd=en?Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z):96;",'squad AI uses testable visibility validator')
    s=s.replace('</html>',f'<!-- {los} -->\n</html>',1)
if voice not in s:
    start_marker='function bzVoiceSlug(name){'
    end_marker='window.bzPlayEventVoice=bzPlayEventVoice;'
    if s.count(start_marker)!=1 or s.count(end_marker)!=1: raise SystemExit('CC0 voice runtime source anchors are not unique')
    start=s.index(start_marker); end=s.index(end_marker,start)+len(end_marker)
    new_voice="""function bzVoiceVariant(name){const v=String(name||'Recruit');let h=0;for(let i=0;i<v.length;i++)h=(h*31+v.charCodeAt(i))|0;return(h&1)?'Female':'Male'}
const BZ_CC0_VOICE_LINES=new Set(['war_call_for_backup','war_cover_me','war_fire_in_the_hole','war_get_down','war_go_go_go','war_look_out','war_medic','war_reloading','war_rpg','war_sniper','war_suppressing_fire','war_target_destroyed','war_target_engaged','war_watch_my_back','mission_completed','mission_failed','you_win','you_lose','ready','go','hurry_up','objective_achieved']);
function bzPlayCC0VoiceLine(line,voice,volume,onFail){if(!BZ_CC0_VOICE_LINES.has(line)){if(onFail)onFail();return null}const gender=voice==='Female'?'Female':'Male',stem=gender==='Female'&&line==='war_suppressing_fire'?'war_supressing_fire':line;let failed=false;const fail=()=>{if(failed)return;failed=true;if(onFail)onFail()};try{if(window.bzVoiceAudio)window.bzVoiceAudio.pause();const a=new Audio('./audio/cc0_voiceover/'+gender+'/'+stem+'.ogg');a.volume=Math.max(0,Math.min(1,Number(volume)||.9));window.bzVoiceAudio=a;a.onerror=()=>{if(window.bzVoiceAudio===a)fail()};const pr=a.play();if(pr&&pr.catch)pr.catch(()=>{if(window.bzVoiceAudio===a)fail()});return a}catch(e){fail();return null}}
function bzPlayLocalVoice(name,idx,volume,onFail){const lines=['war_target_engaged','war_reloading','war_cover_me'];const n=Math.max(1,Math.min(3,Math.floor(Number(idx)||1)));return bzPlayCC0VoiceLine(lines[n-1],bzVoiceVariant(name),volume,onFail)}
function playCharacterVoice(name){if(!SND_ON)return;const lines=['war_target_engaged','war_reloading','war_cover_me'];const line=lines[Math.floor(Math.random()*lines.length)];bzPlayCC0VoiceLine(line,bzVoiceVariant(name),.9,()=>msg('Voice audio unavailable'))}
window.bzPlayLocalVoice=bzPlayLocalVoice;window.playCharacterVoice=playCharacterVoice;
let bzVoiceLastAt=0,bzVoiceLastPriority=0;function bzPlayEventVoice(eventName){if(!SND_ON)return;const priority=({victory:3,defeat:3,low_health:2,cover:2,spawn:1,combat:1,reload:1})[eventName]||0,now=Date.now();if(now-bzVoiceLastAt<3200&&priority<=bzVoiceLastPriority)return;const choices=({victory:['you_win','mission_completed','objective_achieved'],defeat:['you_lose','mission_failed'],low_health:['war_get_down','war_medic','war_look_out'],cover:['war_cover_me','war_watch_my_back'],spawn:['ready','go','war_go_go_go'],combat:['war_target_engaged','war_suppressing_fire','war_look_out'],reload:['war_reloading']})[eventName];if(!choices)return;bzVoiceLastAt=now;bzVoiceLastPriority=priority;const nm=window.pmS?.charName||(typeof bzSelectedCharacter==='function'?bzSelectedCharacter().name:'Recruit')||'Recruit',line=choices[Math.floor(Math.random()*choices.length)];bzPlayCC0VoiceLine(line,bzVoiceVariant(nm),.9)}
window.bzPlayEventVoice=bzPlayEventVoice;"""
    s=s[:start]+new_voice+s[end:]
    s=s.replace('</html>',f'<!-- {voice} -->\\n</html>',1)
if frame not in s:
    old="function loop0(n){const bzWaterShader=lk.material.userData.bzWaterShader;if(bzWaterShader)bzWaterShader.uniforms.bzWaterTime.value=n*.001;window.BZGameState={started:!!started,health:Number(P.hp)||0,alive:!!P.alive,weapon:W[P.w]?.n||'Weapon'};const frameMs=Math.max(0,n-last),dt=Math.min(frameMs/1000,.1);last=n;const bzMove=Math.hypot(joy.x,joy.y)>.12||key.KeyW||key.KeyA||key.KeyS||key.KeyD;document.body.classList.toggle('bz-moving',!!bzMove);document.body.classList.toggle('bz-running',!!(key.sprint||key.ShiftLeft||key.ShiftRight));bzAdaptiveQuality(frameMs);"
    new="const bzFrameGameState=window.BZGameState||(window.BZGameState={});let bzFrameLastMoving=null,bzFrameLastRunning=null;\nfunction loop0(n){const bzWaterShader=lk.material.userData.bzWaterShader;if(bzWaterShader)bzWaterShader.uniforms.bzWaterTime.value=n*.001;bzFrameGameState.started=!!started;bzFrameGameState.health=Number(P.hp)||0;bzFrameGameState.alive=!!P.alive;bzFrameGameState.weapon=W[P.w]?.n||'Weapon';const frameMs=Math.max(0,n-last),dt=Math.min(frameMs/1000,.1);last=n;const bzMove=Math.hypot(joy.x,joy.y)>.12||key.KeyW||key.KeyA||key.KeyS||key.KeyD;if(bzMove!==bzFrameLastMoving){document.body.classList.toggle('bz-moving',!!bzMove);bzFrameLastMoving=!!bzMove}const bzRunning=!!(key.sprint||key.ShiftLeft||key.ShiftRight);if(bzRunning!==bzFrameLastRunning){document.body.classList.toggle('bz-running',bzRunning);bzFrameLastRunning=bzRunning}bzAdaptiveQuality(frameMs);"
    s=sub(s,old,new,'reuse frame telemetry and cache DOM movement states')
    s=s.replace('</html>',f'<!-- {frame} -->\n</html>',1)
if los not in s or frame not in s: raise SystemExit('line-of-sight or frame-loop marker insertion failed')
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
for rel in voice_rel:
    target=voice_dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(voice_repo/rel,target)
for meta in ('License.txt','Credits.txt','PROVENANCE.md','manifest.sha256'):
    shutil.copyfile(voice_repo/meta,voice_dest/meta)
legacy_voices=www/'audio'/'voicepacks'
if legacy_voices.exists(): shutil.rmtree(legacy_voices)
if version not in gs:
    if gs.count('versionCode = 3')!=1 or gs.count('versionName = \"1.2.0\"')!=1:
        raise SystemExit('Unexpected Android version metadata; refusing an unsafe version bump')
    gs=gs.replace('versionCode = 3','versionCode = 5',1).replace('versionName = \"1.2.0\"','versionName = \"1.2.2\"',1)
    gs=gs.replace('android {','android {\n    // '+version,1)
    gp.write_text(gs,encoding='utf-8')
elif gs.count('versionCode = 5')!=1 or gs.count('versionName = \"1.2.2\"')!=1:
    raise SystemExit('Build version marker conflicts with Android version metadata')
if voice not in s: raise SystemExit('CC0 voice marker was not inserted')
if gs.count('versionCode = 5')!=1 or gs.count('versionName = \"1.2.2\"')!=1: raise SystemExit('Android version 1.2.2 metadata mismatch')
print('WORLD_COMBAT_ANIMATION_CC0_VOICE_AND_VERSION_INTEGRITY_APPLIED',p,mp,gp,voice_dest)
