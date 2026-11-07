#!/usr/bin/env python3
"""Add adaptive, stateful offline enemy decision-making to the V6 runtime."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = list(root.rglob("app/src/main/assets/www/index.html"))
if len(paths) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(paths)}")
path = paths[0]
source = path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1"
if marker in source:
    print("BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_ALREADY_APPLIED")
    raise SystemExit(0)
for required in ("BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_V1", "BATTLE_ZONE_GAMEPLAY_QUALITY_V2"):
    if required not in source:
        raise SystemExit(f"Required prior patch missing: {required}")

helper_anchor = "// Original lightweight operator power VFX; existing stat passives remain active."
if source.count(helper_anchor) != 1:
    raise SystemExit("Adaptive AI helper insertion anchor is not unique")
helper = r"""
/* BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1 */
function bzV6TargetIsValid(target){
 if(!target)return false;
 if(target.p)return !!P.alive&&!P.air;
 const actor=target.o,u=actor&&actor.userData;
 if(!actor||!u||!u.alive||!actor.position)return false;
 return BZ_MODE==='TDM'?!!u.ally:!u.ally;
}
function bzV6UpdateZoneWaypoint(bot,u,dt){
 const outside=Math.hypot(bot.position.x-zc.x,bot.position.z-zc.z)>zc.r*.9;
 if(outside){
  u.aiZoneT=(Number(u.aiZoneT)||0)-dt;
  if(u.aiZoneT<=0||!u.aiZoneTarget){u.aiZoneTarget={x:zc.x+rnd(-10,10),z:zc.z+rnd(-10,10)};u.aiZoneT=rnd(1.2,2.2)}
  u.tx=u.aiZoneTarget.x;u.tz=u.aiZoneTarget.z;
 }else{
  u.aiZoneTarget=null;u.aiZoneT=0;
  if(u.t<=0){u.t=rnd(3,7);const a=rnd(0,6.28),d=rnd(10,40);u.tx=bot.position.x+Math.cos(a)*d;u.tz=bot.position.z+Math.sin(a)*d}
 }
 return outside;
}
function bzV6ChooseEnemyTarget(bot,u,dt){
 const maxRange=([30,40,55][DF]||40)*Math.max(.55,Number(ENV.vis)||1);
 let target=u.aiTarget||null;
 if(target&&target.p){target.x=P.x;target.z=P.z}else if(target&&target.o&&target.o.position){target.x=target.o.position.x;target.z=target.o.position.z}
 if(target&&(!bzV6TargetIsValid(target)||Math.hypot(target.x-bot.position.x,target.z-bot.position.z)>maxRange*1.25)){target=null;u.aiTarget=null;u.aiScanT=0}
 u.aiScanT=(Number(u.aiScanT)||0)-dt;
 if(u.aiScanT<=0){
  u.aiScanT=rnd(.16,.26);
  let best=Infinity,chosen=null;
  const consider=(x,z,candidate,priority,hp)=>{
   if(!Number.isFinite(x)||!Number.isFinite(z))return;
   const d=Math.hypot(x-bot.position.x,z-bot.position.z);
   if(d>maxRange)return;
   const health=Number(hp),weak=Number.isFinite(health)?Math.max(0,35-health)/35*4:0;
   const score=d-priority-weak;
   if(score<best){best=score;chosen={x,z,p:candidate.p?1:undefined,o:candidate.o||undefined}}
  };
  if(P.alive&&!P.air&&!smk(P.x,P.z))consider(P.x,P.z,{p:1},5,Number(P.hp));
  forEachActor(actor=>{
   if(actor===bot||!actor||!actor.userData||!actor.userData.alive)return;
   const friendly=!!actor.userData.ally;
   if(BZ_MODE==='TDM'?!friendly:friendly)return;
   consider(actor.position.x,actor.position.z,{o:actor},0,actor.userData.hp);
  });
  target=chosen;u.aiTarget=target;
 }
 if(target){
  u.aiAlert=4;
  u.aiLastSeenX=target.x;u.aiLastSeenZ=target.z;
  return{target,distance:Math.hypot(target.x-bot.position.x,target.z-bot.position.z),investigate:false};
 }
 u.aiTarget=null;
 u.aiAlert=Math.max(0,(Number(u.aiAlert)||0)-dt);
 const x=Number(u.aiLastSeenX),z=Number(u.aiLastSeenZ);
 return u.aiAlert>0&&Number.isFinite(x)&&Number.isFinite(z)
  ?{target:null,distance:Infinity,investigate:true,x,z}
  :{target:null,distance:Infinity,investigate:false};
}
"""
source = source.replace(helper_anchor, helper + "\n" + helper_anchor, 1)

old_target = """let tgt=null,bd=[30,40,55][DF]*ENV.vis;const dp=Math.hypot(P.x-b.position.x,P.z-b.position.z);if(dp<bd&&!smk(P.x,P.z)&&!P.air){bd=dp;tgt={x:P.x,z:P.z,p:1}}
   forEachActor(o=>{if(o!==b&&o.userData.alive&&(BZ_MODE!=='TDM'||o.userData.ally)){const d=Math.hypot(o.position.x-b.position.x,o.position.z-b.position.z);if(d<bd){bd=d;tgt={x:o.position.x,z:o.position.z,o}}}});"""
new_target = """const aiDecision=bzV6ChooseEnemyTarget(b,u,dt);let tgt=aiDecision.target,bd=aiDecision.distance;"""
if source.count(old_target) != 1:
    raise SystemExit(f"Enemy target-selection anchor expected once, found {source.count(old_target)}")
source = source.replace(old_target, new_target, 1)

old_zone = """if(Math.hypot(b.position.x-zc.x,b.position.z-zc.z)>zc.r*.9){u.tx=zc.x+rnd(-10,10);u.tz=zc.z+rnd(-10,10)}
   else if(u.t<=0){u.t=rnd(3,7);const a=rnd(0,6.28),d=rnd(10,40);u.tx=b.position.x+Math.cos(a)*d;u.tz=b.position.z+Math.sin(a)*d}"""
new_zone = """bzV6UpdateZoneWaypoint(b,u,dt);"""
if source.count(old_zone) != 1:
    raise SystemExit(f"Safe-zone waypoint anchor expected once, found {source.count(old_zone)}")
source = source.replace(old_zone, new_zone, 1)

start_anchor = "let gx=u.tx,gz=u.tz,spd=u.role==='rush'?3.5:3;if(tgt){"
end_anchor = "const dx=gx-b.position.x,dz=gz-b.position.z,dl=Math.hypot(dx,dz);"
if source.count(start_anchor) != 1 or source.count(end_anchor) != 1:
    raise SystemExit("Enemy movement/decision block anchors are not unique")
start = source.index(start_anchor)
end = source.index(end_anchor, start)
replacement = """let gx=u.tx,gz=u.tz,spd=u.role==='rush'?3.8:3.1;
   const outsideZone=Math.hypot(b.position.x-zc.x,b.position.z-zc.z)>zc.r*.9;
   if(tgt){
    u.aiState='engage';u.aiAlert=4;u.aiLastSeenX=tgt.x;u.aiLastSeenZ=tgt.z;
    b.rotation.y=Math.atan2(tgt.x-b.position.x,tgt.z-b.position.z);
    const approachAngle=Math.atan2(b.position.z-tgt.z,b.position.x-tgt.x);
    const retreat=Number(u.hp)<=28;
    if(outsideZone){u.aiState='zone';gx=u.tx;gz=u.tz;spd=4.4}
    else if(retreat){
     u.aiState='retreat';u.aiCoverT=(u.aiCoverT||0)-dt;
     if(u.aiCoverT<=0||!u.aiCoverPt||Math.hypot(u.aiCoverPt.x-b.position.x,u.aiCoverPt.z-b.position.z)<2){
      u.aiCoverPt=tacticalCoverPoint(b,tgt.x,tgt.z);u.aiCoverT=rnd(2.2,3.4)
     }
     if(u.aiCoverPt){gx=u.aiCoverPt.x;gz=u.aiCoverPt.z}
     else{const away=Math.atan2(b.position.z-tgt.z,b.position.x-tgt.x);gx=b.position.x+Math.cos(away)*12;gz=b.position.z+Math.sin(away)*12}
     spd=4.1;
    }else if(u.role==='cover'&&bd<48){
     u.coverT=(u.coverT||0)-dt;
     if(u.coverT<=0||!u.coverPt||Math.hypot(u.coverPt.x-b.position.x,u.coverPt.z-b.position.z)<2){u.coverPt=tacticalCoverPoint(b,tgt.x,tgt.z);u.coverT=rnd(3,6)}
     if(u.coverPt&&bd>12){gx=u.coverPt.x;gz=u.coverPt.z}else if(bd>17){gx=tgt.x+Math.cos(approachAngle)*13;gz=tgt.z+Math.sin(approachAngle)*13}
    }else if(u.role==='flank'&&bd<55){
     const ang=approachAngle+u.flankS*1.15;
     gx=tgt.x+Math.cos(ang)*rnd(7,11);gz=tgt.z+Math.sin(ang)*rnd(7,11);spd=3.7;
    }else if(u.role==='camp'){gx=b.position.x;gz=b.position.z;spd=0}
    else if(bd>17){gx=tgt.x+Math.cos(approachAngle)*13;gz=tgt.z+Math.sin(approachAngle)*13;spd=u.role==='rush'?4.2:3.3}
    else if(bd<15){
     u.sd=u.sd||1;if(Math.random()<dt*.7)u.sd*=-1;
     gx=b.position.x+Math.cos(b.rotation.y)*u.sd*4;gz=b.position.z-Math.sin(b.rotation.y)*u.sd*4;
    }else if(u.role==='rush'){spd=4.2}
    if(u.cd<=0){
     u.cd=rnd(.5,1.1);
     const targetY=tgt.p?(P.y-.25):(tgt.o.position.y+1.1);
     const clear=hasClearShot(b.position.x,b.position.y+1.15,b.position.z,tgt.x,targetY,tgt.z);
     if(clear&&bd<60)snd(0,.08,.15*(1-bd/60));
     const accuracy=([.28,.42,.58][DF]||.42)*Math.max(.35,1-bd/85)*(retreat ? .65 : 1);
     if(clear&&Math.random()<accuracy){
      if(b.sc){b.sc.action='shoot';b.sc.actionT=.2}
      if(tgt.p){dmg(rnd(4,9)*[.7,1,1.3][DF])}
      else{tgt.o.userData.hp-=15;if(tgt.o.userData.hp<=0)killBot(tgt.o,false)}
     }
    }
   }else if(outsideZone){u.aiState='zone';gx=u.tx;gz=u.tz;spd=4.4}
   else if(aiDecision.investigate){
    if(Number(u.hp)<=28){
     u.aiState='retreat';u.aiCoverT=(u.aiCoverT||0)-dt;
     if(u.aiCoverT<=0||!u.aiCoverPt||Math.hypot(u.aiCoverPt.x-b.position.x,u.aiCoverPt.z-b.position.z)<2){u.aiCoverPt=tacticalCoverPoint(b,aiDecision.x,aiDecision.z);u.aiCoverT=rnd(2.2,3.4)}
     if(u.aiCoverPt){gx=u.aiCoverPt.x;gz=u.aiCoverPt.z}else{const away=Math.atan2(b.position.z-aiDecision.z,b.position.x-aiDecision.x);gx=b.position.x+Math.cos(away)*12;gz=b.position.z+Math.sin(away)*12}
     spd=3.8;
    }else{u.aiState='investigate';gx=aiDecision.x;gz=aiDecision.z;spd=2.8;if(Math.hypot(gx-b.position.x,gz-b.position.z)<4){u.aiAlert=0;u.aiState='patrol'}}
   }else{u.aiState='patrol'}
   """
source = source[:start] + replacement + source[end:]

hit_anchor = "b.userData.tx=P.x;b.userData.tz=P.z;if(b.userData.hp<=0)killBot(b,true)"
hit_new = "b.userData.tx=P.x;b.userData.tz=P.z;b.userData.aiAlert=6;b.userData.aiLastSeenX=P.x;b.userData.aiLastSeenZ=P.z;b.userData.aiTarget={x:P.x,z:P.z,p:1};b.userData.aiScanT=0;if(b.userData.hp<=0)killBot(b,true)"
if source.count(hit_anchor) != 1:
    raise SystemExit(f"Player-hit memory anchor expected once, found {source.count(hit_anchor)}")
source = source.replace(hit_anchor, hit_new, 1)

source = source.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
path.write_text(source, encoding="utf-8")
print("BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_APPLIED", path)
