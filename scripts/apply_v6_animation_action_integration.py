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
if marker in source and marker in model_source:
    print("BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_ALREADY_APPLIED")
    raise SystemExit(0)
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
  return{mixer,acts:a,cur:null,action:null,actionState:null,dead:false};
}"""
model_source = once(model_source, old_animator, new_animator, "rigged mixer action states")

old_gltf = "finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump')},c);"
new_gltf = "finish(g.scene,{idle:bestClip(l,'idle|stand|rest'),run:bestClip(l,'run|sprint|jog'),walk:bestClip(l,'walk'),jump:bestClip(l,'jump'),shoot:bestClip(l,'shoot|fire|rifle'),reload:bestClip(l,'reload'),death:bestClip(l,'death|die|dead')},c);"
model_source = once(model_source, old_gltf, new_gltf, "GLB action clip discovery")

action_anchor = "const lock=(o,v)=>{try{Object.defineProperty(o,'visible',{get:()=>v,set(){},configurable:true})}catch(e){}};"
action_api = """function playAction(target,state){
  if(!target||!['shoot','reload','death'].includes(state))return false;
  const entry=entries.find(e=>e.obj===target);
  if(!entry||!entry.an||!entry.an.acts[state]||entry.an.dead)return false;
  const a=entry.an,action=a.acts[state];
  if(a.action&&a.action!==action)a.action.stop();
  if(a.cur&&a.cur.a&&a.cur.a!==action)a.cur.a.fadeOut(.06);
  action.reset();action.enabled=true;action.clampWhenFinished=true;
  action.setLoop(THREE.LoopOnce,1);action.setEffectiveTimeScale(1);action.fadeIn(.06).play();
  a.action=action;a.actionState=state;if(state==='death')a.dead=true;
  return true;
}
"""
model_source = once(model_source, action_anchor, action_api + action_anchor, "rigged action API")

old_tick = """    if(e.an){
      const want=pickAct(e,sp);
      if(want&&want!==e.an.cur){
        if(want.a!==e.an.cur.a){want.a.reset().play();e.an.cur.a.crossFadeTo(want.a,.2,false)}
        want.a.setEffectiveTimeScale(want.ts);e.an.cur=want}
      e.an.mixer.update(dt)}"""
new_tick = """    if(e.an){
      if(e.an.action){
        const active=e.an.action;e.an.mixer.update(dt);
        if(!e.an.dead&&active.time>=active.getClip().duration-.015){active.stop();e.an.action=null;e.an.actionState=null}
      }else if(!e.an.dead){
        const want=pickAct(e,sp);
        if(want&&want!==e.an.cur){
          if(want.a!==e.an.cur.a){want.a.reset().play();e.an.cur.a.crossFadeTo(want.a,.2,false)}
          want.a.setEffectiveTimeScale(want.ts);e.an.cur=want}
        e.an.mixer.update(dt)
      }else e.an.mixer.update(dt)
    }"""
model_source = once(model_source, old_tick, new_tick, "action-aware locomotion mixer")

old_api = "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load};"
new_api = "window.BZModels={status:()=>state,config:()=>cfg,count:()=>entries.length,dress,load,playAction,availableActions:()=>['shoot','reload','death'].filter(k=>!!(tpl&&tpl.clips&&tpl.clips[k]))};"
model_source = once(model_source, old_api, new_api, "public animation action API")
model_source = model_source.replace("/* Rigged character models", "/* " + marker + " */\n/* Rigged character models", 1)

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
