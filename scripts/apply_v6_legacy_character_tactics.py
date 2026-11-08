#!/usr/bin/env python3
"""Restore the original articulated operator look and wire tactics into legacy allies."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
p=files[0];s=p.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_LEGACY_CHARACTER_TACTICS_V1"
if marker in s:
    print(marker+" already applied");raise SystemExit(0)
def once(old,new,label):
    global s
    if new in s:
        return
    n=s.count(old)
    if n!=1: raise SystemExit(f"{label}: expected exactly one source anchor, found {n}")
    s=s.replace(old,new,1)
# Keep the original articulated mkScout/animSc rig. Make profile identity and every material
# channel explicit so the existing skin selector updates the complete operator, not only trim.
name_anchor="function bzSelectedCharacter(){"
name_helper="function bzSelectedCharacterName(){try{const p=JSON.parse(localStorage.getItem('bzProfile')||'{}');return BZ_CHAR_DATA[p.equippedCharacter]?p.equippedCharacter:'Recruit'}catch(e){return 'Recruit'}}\n"
if "function bzSelectedCharacterName()" not in s: once(name_anchor,name_helper+name_anchor,"selected operator identity helper")
once("const $=id=>document.getElementById(id),rnd=","window.BZ_CHAR_DATA_READY=false;\nconst $=id=>document.getElementById(id),rnd=","reset stale character readiness before UI initialization")
old="charName:(Object.keys(BZ_CHAR_DATA||{}).find(n=>BZ_CHAR_DATA[n].color===jc)||'Recruit')"
once(old,"charName:bzSelectedCharacterName()","stable operator identity")
old="mk(cl,gBox(.26,.32,.12),mtl(lk.pack,.9,0),0,0,0);"
new="const mPack=mtl(lk.pack,.9,0);mk(cl,gBox(.26,.32,.12),mPack,0,0,0);"
once(old,new,"retain operator backpack material")
look="""sc.lookMaterials={skin:mS,hair:mH,pants:mP,boot:mB,shirt:mSh,jacket:mJ,pack:mPack};
 sc.applyLook=(look,accent)=>{const set=(material,value)=>{if(material&&material.color&&value!=null&&Number.isFinite(Number(value)))material.color.setHex(Number(value))};set(mS,look.skin);set(mH,look.hair);set(mP,look.pants);set(mB,look.boot);set(mSh,look.shirt);set(mPack,look.pack);set(mJ,accent);return sc};
 """
old="const accent=mtl(jc,.32,.62);mk(torso,gBox(.035,.2,.025),accent,.13,.34,.185);"
once(old,old+"\n "+look,"full articulated operator material bindings")
refresh="""function bzRefreshCharacterAppearance(){if(!window.BZ_CHAR_DATA_READY)return '';const c=bzSelectedCharacter(),idx=Number.isInteger(Number(ST_.cur))&&SKN[Number(ST_.cur)]?Number(ST_.cur):0;Object.assign(PLOOK,{skin:c.skin??0xe0ac82,hair:c.hair??0x2b1b12,pants:c.pants??0x2c3a52,boot:0x2a1d14,shirt:c.shirt??c.color??0xe8e2d4,pack:c.color??0x3a4a6a});const accent=SKN[idx][1];[window.lobSc,window.pmS].forEach(model=>{if(model&&typeof model.applyLook==='function')model.applyLook(PLOOK,accent)});return bzSelectedCharacterName()}
window.BZRefreshCharacterAppearance=bzRefreshCharacterAppearance;
"""
once("function updCur(){",refresh+"function updCur(){","live operator appearance refresh")
once("function bzOperatorGearStyle(name){","window.BZ_CHAR_DATA_READY=true;\nif(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance();\nfunction bzOperatorGearStyle(name){","publish character readiness only after PLOOK initialization")
once("Object.keys(LOOT).forEach(k=>{for(let j=0;j<2;j++)pk.push({m:mkLoot(k,rnd(-395,395),rnd(-395,395)),k})});","Object.keys(LOOT).forEach(k=>{for(let j=0;j<2;j++)pk.push({m:mkLoot(k,rnd(-395,395),rnd(-395,395)),k})});\nwindow.BZPickups=pk;","publish initialized pickup registry")
once("const al=[],bots=[],bm=new THREE.BoxGeometry(.7,1.2,.5),hm=new THREE.BoxGeometry(.4,.4,.4);","const al=[],bots=[],bm=new THREE.BoxGeometry(.7,1.2,.5),hm=new THREE.BoxGeometry(.4,.4,.4);window.BZActors=Object.freeze({bots,allies:al});","publish initialized actor registry")
once("const key={};let joy={x:0,y:0},fire=false,started=false;","const key={};let joy={x:0,y:0},fire=false,started=false;window.BZMatchRuntime=Object.freeze({isStarted:()=>!!started,allies:()=>al});","publish initialized match-state registry")
once("pk.forEach(p=>{const t=tierOf(p);","const bzPickups=window.BZPickups||[];bzPickups.forEach(p=>{const t=tierOf(p);","safe pickup registry access")
once("Array.isArray(bots)?bots.find(b=>","Array.isArray(window.BZActors?.bots)?window.BZActors.bots.find(b=>","safe tactical target lookup")
once("const actors=Array.isArray(bots)?bots:[];","const actors=Array.isArray(window.BZActors?.bots)?window.BZActors.bots:[];","safe tactical actor list")
once("const visible=!!(started&&Array.isArray(al)&&al.some(a=>","const visible=!!(window.BZMatchRuntime?.isStarted()&&Array.isArray(window.BZActors?.allies)&&window.BZActors.allies.some(a=>","safe tactical match-state lookup")

old="if(window.lobSc)lobSc.jk.forEach(m=>m.material.color.set(SKN[ST_.cur][1]));if(window.pmS)pmS.jk.forEach(m=>m.material.color.set(SKN[ST_.cur][1]))"
once(old,"if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance()","legacy skin selector full-model refresh")
# Profile saves already centralize operator equip changes; refresh the preview and player rig there.
old="function save(){put('bzProfile',profile);refreshTop()}"
if old in s: s=s.replace(old,"function save(){put('bzProfile',profile);refreshTop();if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance()}",1)
# Ensure both already-created rigs receive the current profile after construction.
old="window.lobSc=sc;lc.position.set(0,1.1,4.6);"
if old in s: s=s.replace(old,"window.lobSc=sc;if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance();lc.position.set(0,1.1,4.6);",1)
old="window.pmS=pm;"
if old in s: s=s.replace(old,"window.pmS=pm;if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance();",1)
# Restore the original circular follow formation and nearest-threat defence inside the
# current squad update loop. Keep its LOS, medic, revive and cover systems as enhancements.
old="role=(bzOrder==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3]))"
new="role=(bzOrder==='flank'?'flank':bzOrder==='regroup'?'assault':bzOrder==='focus'?'assault':u.squadRole||(['assault','support','flank'][i%3]))"
once(old,new,"legacy regroup/focus combat role")
once("if(bzOrder==='regroup')en=null;","/* Legacy regroup preserves nearest-threat defence while returning to formation. */","regroup target retention")
old="let gx=px+Math.cos(P.yaw)*9+Math.sin(P.yaw)*(i-1)*5,gz=pz-Math.sin(P.yaw)*9+Math.cos(P.yaw)*(i-1)*5,speed=5.4;"
new="let gx=px+Math.cos(u.off*2)*4,gz=pz+Math.sin(u.off*2)*4,speed=5.4;"
once(old,new,"original circular ally formation")
old="}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34){gx=px;gz=pz;speed=7.8}else if(follow<5){gx=a.position.x;gz=a.position.z}else if(follow<10){gx=px+Math.cos(P.yaw)*7+Math.sin(P.yaw)*(i-1)*4;gz=pz-Math.sin(P.yaw)*7+Math.cos(P.yaw)*(i-1)*4;speed=3.4}}"
new="}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34){gx=px;gz=pz;speed=7.8}else if(follow<5){gx=a.position.x;gz=a.position.z}}"
once(old,new,"legacy ally follow and hold movement")
revive_old="if(P.down&&follow<3){u.reviveT=(u.reviveT||0)+dt;"
revive_new="if(P.down&&follow<4){u.reviveT=(u.reviveT||0)+dt;"
if revive_old in s:
    once(revive_old,revive_new,"legacy teammate revive radius")
elif revive_new not in s:
    raise SystemExit("legacy teammate revive radius: expected original or already-restored anchor")

# Verify critical old mechanisms remain after integration.
required=["function mkScout(","function animSc(","if(P.down&&follow<4)","window.BZSquadOrders?.get()"]
missing=[x for x in required if x not in s]
if missing: raise SystemExit("Legacy character or squad behaviour was not preserved: "+repr(missing))
s=s.replace("</html>","<!-- "+marker+" -->"+chr(10)+"</html>",1)
p.write_text(s,encoding="utf-8")
models=list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(models)!=1: raise SystemExit(f"Expected exactly one models.js, found {len(models)}")
mp=models[0];ms=mp.read_text(encoding="utf-8")
model_marker="BATTLEZONE_V6_SAFE_RUNTIME_ACTOR_BRIDGE_V1"
if model_marker not in ms:
    old_each="const eachActor=fn=>{if(typeof bots!=='undefined')for(let i=0;i<bots.length;i++)fn(bots[i],i);if(typeof al!=='undefined')for(let i=0;i<al.length;i++)fn(al[i],(typeof bots!=='undefined'?bots.length:0)+i)};"
    new_each="const eachActor=fn=>{const actors=window.BZActors||{},botList=Array.isArray(actors.bots)?actors.bots:[],allyList=Array.isArray(actors.allies)?actors.allies:[];botList.forEach((actor,i)=>fn(actor,i));allyList.forEach((actor,i)=>fn(actor,botList.length+i))};"
    if ms.count(old_each)!=1: raise SystemExit(f"models actor registry: expected one anchor, found {ms.count(old_each)}")
    ms=ms.replace(old_each,new_each,1)
    old_load="if(state==='idle'&&(window.pmS||(typeof bots!=='undefined'&&bots.length)))load();"
    new_load="if(state==='idle'&&(window.pmS||((window.BZActors?.bots||[]).length>0)))load();"
    if ms.count(old_load)!=1: raise SystemExit(f"models loader gate: expected one anchor, found {ms.count(old_load)}")
    ms=ms.replace(old_load,new_load,1)
    old_dress="if(typeof bots!=='undefined'&&typeof LQ!=='undefined'&&!LQ){"
    new_dress="if(Array.isArray(window.BZActors?.bots)&&typeof LQ!=='undefined'&&!LQ){"
    if ms.count(old_dress)!=1: raise SystemExit(f"models dressing gate: expected one anchor, found {ms.count(old_dress)}")
    ms=ms.replace(old_dress,new_dress,1)
    ms=ms.replace("/* BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_V1 */","/* BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_V1 */\n/* "+model_marker+" */",1)
    mp.write_text(ms,encoding="utf-8")
print(marker+" applied",p,"and",model_marker+" applied",mp)
