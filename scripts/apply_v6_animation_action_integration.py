#!/usr/bin/env python3
"""Integrate optional rig-compatible combat clips into the existing V6 character mixer."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
models_files = list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(htmls) != 1 or len(models_files) != 1:
    raise SystemExit(f"Expected one index.html and models.js, found {len(htmls)} and {len(models_files)}")
html, models = htmls[0], models_files[0]
source = html.read_text(encoding="utf-8")
model_source = models.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1"
fallback_marker = "BATTLEZONE_V6_ANIMATION_FALLBACK_V1"
if marker in source and marker in model_source and fallback_marker in model_source:
    print("BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_ALREADY_APPLIED")
    raise SystemExit(0)
if marker in source or marker in model_source:
    raise SystemExit("Partial animation integration detected; rebuild from the canonical source archive")
if "BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1" not in source:
    raise SystemExit("Adaptive enemy AI patch must run before animation integration")

def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)

old_animator = """function animator(model){
  const any=tpl.clips.idle||tpl.clips.run||tpl.clips.walk;if(!any)return null;
  const mixer=new THREE.AnimationMixer(model),act=c=>c?mixer.clipAction(c):null,a={};
  const idle=act(tpl.clips.idle)||act(any),run=act(tpl.clips.run)||idle,walk=act(tpl.clips.walk),jump=act(tpl.clips.jump);
  a.idle={a:idle,ts:1};a.run={a:run,ts:1};
  a.walk=walk?{a:walk,ts:1}:{a:run,ts:(tpl.clips.run?tpl.walkScale:1)};   // no walk clip: slowed run
  a.jump=jump?{a:jump,ts:1}:null;
  return{mixer,acts:a,cur:null};
}"""
new_animator = """function animator(model){
  const any=tpl.clips.idle||tpl.clips.run||tpl.clips.walk;if(!any)return null;
  const mixer=new THREE.AnimationMixer(model),act=c=>c?mixer.clipAction(c):null,a={};
  const idle=act(tpl.clips.idle)||act(any),run=act(tpl.clips.run)||idle,walk=act(tpl.clips.walk),jump=act(tpl.clips.jump);
  a.idle={a:idle,ts:1};a.run={a:run,ts:1};
  a.walk=walk?{a:walk,ts:1}:{a:run,ts:(tpl.clips.run?tpl.walkScale:1)};
  a.jump=jump?{a:jump,ts:1}:null;
  a.shoot=act(tpl.clips.shoot);a.reload=act(tpl.clips.reload);a.death=act(tpl.clips.death);
  return{mixer,acts:a,cur:null,action:null,actionState:null,resumeAction:null,dead:false};
}"""
model_source = once(model_source, old_animator, new_animator, "rigged mixer action states")

old_fallback = " {format:'glb',model:'./models/characters/soldier.glb',height:1.8,yawOffset:0}"
new_fallback = """ {format:'glb',model:'./models/characters/kaykit_v1_2/Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb',height:1.8,yawOffset:0},
 {format:'glb',model:'./models/characters/soldier.glb',height:1.8,yawOffset:0}"""
model_source = once(model_source, old_fallback, new_fallback, "bundled compatible KayKit fallback")

old_gltf = "finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump')},c);"
new_gltf = "finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump'),shoot:bestClip(l,'shoot|fire|rifle'),reload:bestClip(l,'reload'),death:bestClip(l,'death|die|dead|defeat')},c);"
model_source = once(model_source, old_gltf, new_gltf, "GLB action clip discovery")

action_anchor = "const lock=(o,v)=>{try{Object.defineProperty(o,'visible',{get:()=>v,set(){},configurable:true})}catch(e){}};"
action_api = """function playAction(target,state){
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
}
"""
model_source = once(model_source, action_anchor, action_api + action_anchor, "rigged action API")
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
model_source = once(model_source, old_action, new_action, "missing-clip procedural action fallback")

old_entry = "const entry={obj,model,an,bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null};entries.push(entry);"
new_entry = "const entry={obj,model,an,bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null,weaponBasePosition:null,weaponBaseRotation:null};entries.push(entry);"
model_source = once(model_source, old_entry, new_entry, "weapon mount base transform state")
old_register = "if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,template.format==='glb'?0:.055);bones.rightHand.add(entry.weaponMount);setWeaponEntry(entry,opt.weaponName||window.BZActiveWeapon||'M416')}"
new_register = "if(opt.gun&&bones.rightHand){entry.weaponMount=new THREE.Group();entry.weaponMount.position.set(0,0,template.format==='glb'?0:.055);bones.rightHand.add(entry.weaponMount);entry.weaponBasePosition=entry.weaponMount.position.clone();entry.weaponBaseRotation=entry.weaponMount.rotation.clone();setWeaponEntry(entry,opt.weaponName||window.BZActiveWeapon||'M416')}"
model_source = once(model_source, old_register, new_register, "weapon mount base transform capture")
old_pose = "function applyWeaponPose(entry,speed,time){if(!entry||!entry.weaponMount||!entry.bones||!entry.an||entry.template?.format==='glb'||entry.an.dead||entry.an.actionState==='death'||entry.an.actionState==='reload'||entry.an.actionState==='shoot')return;const b=entry.bones,run=Math.min(1,Math.max(0,(speed-1.8)/5.5)),sway=Math.sin(time*10)*.035*run,blend=(bone,x,y,z,w)=>{if(!bone)return;bone.rotation.x=bone.rotation.x*(1-w)+x*w;bone.rotation.y=bone.rotation.y*(1-w)+y*w;bone.rotation.z=bone.rotation.z*(1-w)+z*w};blend(b.rightArm,-.34-sway,.02,.08,.82);blend(b.rightForeArm,-.72,.02,0,.82);blend(b.leftArm,-.58+sway,-.02,-.2,.82);blend(b.leftForeArm,-.88,0,.1,.82);blend(b.spine,.035+run*.045,0,0,.32)}"
new_pose = """function applyWeaponPose(entry,speed,time){
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
model_source = once(model_source, old_pose, new_pose, "procedural fallback weapon and arm poses")

old_tick = """    if(e.an){
      const want=pickAct(e,sp);
      if(want&&want!==e.an.cur){
        if(want.a!==e.an.cur.a){want.a.reset().play();e.an.cur.a.crossFadeTo(want.a,.2,false)}
        want.a.setEffectiveTimeScale(want.ts);e.an.cur=want}
      e.an.mixer.update(dt)}"""
new_tick = """    if(e.an){
      if(e.an.action){
        const active=e.an.action;e.an.mixer.update(dt);
        if(!e.an.dead&&active.time>=active.getClip().duration-.015){active.stop();if(e.an.resumeAction){e.an.resumeAction.stop();e.an.resumeAction=null}e.an.action=null;e.an.actionState=null;e.an.cur=null}
      }else if(!e.an.dead){
        const want=pickAct(e,sp);
        if(want&&want!==e.an.cur){
          if(want.a!==(e.an.cur&&e.an.cur.a)){
            want.a.reset();want.a.enabled=true;want.a.setEffectiveTimeScale(want.ts);
            if(e.an.cur&&e.an.cur.a){want.a.play();e.an.cur.a.crossFadeTo(want.a,.2,false)}else want.a.fadeIn(.12).play();
          }else{want.a.enabled=true;want.a.setEffectiveTimeScale(want.ts);want.a.play()}
          e.an.cur=want}
        e.an.mixer.update(dt)
      }else e.an.mixer.update(dt)
    }"""
model_source = once(model_source, old_tick, new_tick, "action-aware locomotion mixer")
model_source = once(model_source, "    if(e.an){\n      if(e.an.action){", "    if(e.an){\n      if(e.an.fallbackTimer>0){e.an.fallbackTimer=Math.max(0,e.an.fallbackTimer-dt);if(e.an.fallbackTimer===0){e.an.actionState=null;e.an.fallbackDuration=0}}\n      if(e.an.action){", "fallback action timer")


old_api = "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load};"
new_api = "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load,playAction,availableActions:()=>['shoot','reload','death'].filter(k=>!!(tpl&&tpl.clips&&tpl.clips[k]))};"
model_source = once(model_source, old_api, new_api, "public animation action API")
model_source = model_source.replace("/* Rigged character models", "/* " + marker + " */\n/* Rigged character models", 1)
model_source = model_source.replace("/* " + marker + " */", "/* " + marker + " */\n/* BATTLEZONE_V6_ANIMATION_FALLBACK_V1 */", 1)

source = once(source, "if(pm){pm.action='reload';pm.actionT=1.5}", "if(pm){pm.action='reload';pm.actionT=1.5;window.BZModels?.playAction(pm.root,'reload');}", "player reload clip trigger")
source = once(source, "if(pm){pm.action='shoot';pm.actionT=.2}", "if(pm){pm.action='shoot';pm.actionT=.2;window.BZModels?.playAction(pm.root,'shoot');}", "player firing clip trigger")
source = once(source, "if(b.sc){b.sc.action='death';b.sc.actionT=1}", "if(b.sc){b.sc.action='death';b.sc.actionT=1}window.BZModels?.playAction(b,'death');", "enemy death clip trigger")
source = once(source, "if(b.sc){b.sc.action='shoot';b.sc.actionT=.2}", "if(b.sc){b.sc.action='shoot';b.sc.actionT=.2}window.BZModels?.playAction(b,'shoot');", "enemy firing clip trigger")
source = once(source, "if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}", "if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}window.BZModels?.playAction(a,'shoot');", "ally firing clip trigger")
source = once(source, "function end(win){if(win)window.bzPlayEventVoice?.('victory');", "function end(win){if(!win&&window.pmS)window.BZModels?.playAction(pm.root,'death');if(win)window.bzPlayEventVoice?.('victory');", "player elimination clip trigger")
source = once(source, "/* BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1 */", "/* BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1 */\n/* " + marker + " */", "animation patch marker")
models.write_text(model_source, encoding="utf-8")
html.write_text(source, encoding="utf-8")
print("BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_APPLIED", html, models)
