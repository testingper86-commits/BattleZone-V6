#!/usr/bin/env python3
"""Complete the reported Battle Zone lobby and gameplay fixes."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
hs=list(root.rglob("app/src/main/assets/www/index.html"))
if len(hs)!=1: raise SystemExit(f"Expected one game HTML, found {len(hs)}")
html=hs[0]; s=html.read_text(encoding="utf-8"); marker="BATTLE_ZONE_FEEDBACK_COMPLETION_V1"
if marker in s: print("BATTLE_ZONE_FEEDBACK_COMPLETION_ALREADY_APPLIED"); raise SystemExit(0)
def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f"{label}: expected one anchor, found {n}")
    s=s.replace(old,new,1)

rep("const navIds={'wsb':'shop','msb':'rank','invb':'inventory','dlyb':'rank'};Object.entries(navIds).forEach(([id,p])=>$(id)?.addEventListener('click',()=>open(p)));",
    "// Feedback completion: original lobby handlers remain the single action owners.","duplicate lobby navigation")
rep("cg.rotation.y+=dt*.01;gun.visible=!P.tp&&!P.veh&&!P.air;chuteM.visible=P.air==3;",
    "cg.rotation.y+=dt*.01;gun.visible=!P.tp&&!P.veh&&P.air!==2;gun.position.y=-.22+(P.air===1?.105:P.air===3?.045:(P.vy>1?.025:0));gun.position.z=-.5+(P.air===1?.035:P.air===3?.015:0);gun.rotation.x=P.air===1?-.12:P.air===3?-.065:0;chuteM.visible=P.air==3;","airborne first-person weapon")
rep("pm.hand.visible=!P.air&&!P.veh;","pm.hand.visible=!P.veh&&P.air!==2;","airborne third-person weapon hand")
rep("g.userData.off=i+1;al.push(g)}}",
    "g.userData.off=i+1;al.push(g)}al.forEach((a,i)=>{a.userData.squadRole=['assault','support','flank'][i%3];a.userData.squadSide=i%2?1:-1;a.userData.squadThink=rnd(.05,.35);a.userData.squadTarget=null;a.userData.squadCover=null})}","squad role initialization")
lines=s.splitlines()
starts=[i for i,line in enumerate(lines) if line.lstrip().startswith("al.forEach(a=>{const u=a.userData;")]
ends=[i for i,line in enumerate(lines) if line.lstrip().startswith("if(P.down){P.dt-=")]
if len(starts)!=1 or len(ends)!=1 or ends[0]<=starts[0]: raise SystemExit(f"Squad update anchors invalid: {starts}, {ends}")
ally=[
"  al.forEach((a,i)=>{const u=a.userData;if(u.down||u.alive===false)return;u.cd=(u.cd||0)-dt;u.squadThink=(u.squadThink||0)-dt;",
"   const role=u.squadRole||(['assault','support','flank'][i%3]),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;",
"   let en=null,bd=96,best=Infinity;bots.forEach(o=>{const v=o.userData;if(!v.alive||v.ally||v.airDrop||v.falling)return;const d=Math.hypot(o.position.x-a.position.x,o.position.z-a.position.z);if(d>96)return;const threat=Math.hypot(o.position.x-px,o.position.z-pz),score=d+Math.min(30,threat)*.18;if(score<best){best=score;bd=d;en=o}});",
"   let gx=px+Math.cos(P.yaw)*9+Math.sin(P.yaw)*(i-1)*5,gz=pz-Math.sin(P.yaw)*9+Math.cos(P.yaw)*(i-1)*5,speed=5.4;",
"   if(P.down){gx=px;gz=pz;speed=7.2}else if(en){const ex=en.position.x-a.position.x,ez=en.position.z-a.position.z,ang=Math.atan2(ez,ex),clear=bd<88&&hasClearShot(a.position.x,a.position.y+1.15,a.position.z,en.position.x,en.position.y+1.1,en.position.z);a.rotation.y=Math.atan2(ex,ez);u.squadTarget=en.userData.nid||null;",
"    if(role==='support'){if(u.squadThink<=0||!u.squadCover||Math.hypot(u.squadCover.x-a.position.x,u.squadCover.z-a.position.z)<2){u.squadCover=tacticalCoverPoint(a,en.position.x,en.position.z);u.squadThink=rnd(2.8,4.5)}if(u.squadCover&&bd>9){gx=u.squadCover.x;gz=u.squadCover.z;speed=4.8}else{gx=a.position.x;gz=a.position.z}}",
"    else if(role==='flank'){const flankAngle=ang+side*1.12,range=bd>22?14:11;gx=en.position.x+Math.cos(flankAngle)*range;gz=en.position.z+Math.sin(flankAngle)*range;speed=6.1}",
"    else if(bd>17){gx=en.position.x-Math.cos(ang)*13;gz=en.position.z-Math.sin(ang)*13;speed=6.6}else if(bd<9){gx=a.position.x+Math.cos(ang+Math.PI/2*side)*5;gz=a.position.z+Math.sin(ang+Math.PI/2*side)*5;speed=4.2}else{gx=a.position.x;gz=a.position.z}",
"    if(clear&&u.cd<=0){u.cd=rnd(.42,.68)*([.88,1,1.12][DF]||1);if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}const hitDamage=(role==='support'?13:role==='flank'?17:19)+rnd(0,5);en.userData.hp-=hitDamage;if(en.userData.hp<=0)killBot(en,false)}else if(!clear&&u.cd<=0){u.cd=.22;u.squadThink=0}",
"   }else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(follow>34){gx=px;gz=pz;speed=7.8}else if(follow<5){gx=a.position.x;gz=a.position.z}else if(follow<10){gx=px+Math.cos(P.yaw)*7+Math.sin(P.yaw)*(i-1)*4;gz=pz-Math.sin(P.yaw)*7+Math.cos(P.yaw)*(i-1)*4;speed=3.4}}",
"   const dx=gx-a.position.x,dz=gz-a.position.z,dl=Math.hypot(dx,dz);if(dl>1.35){const step=Math.min(dl,speed*dt),r=hit(a.position.x+dx/dl*step,a.position.z+dz/dl*step,.4);[a.position.x,a.position.z]=clampWorld(r[0],r[1],1);a.position.y=gT(a.position.x,a.position.z);if(!en)a.rotation.y=Math.atan2(dx,dz)}",
"   const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(!P.down&&P.hp<76&&follow<8){u.healT=(u.healT||0)+dt;if(u.healT>=2.5){P.hp=Math.min(100,P.hp+12);u.healT=0;msg('TEAM MEDIC • +12 HEALTH')}}else u.healT=0;",
"   if(P.down&&follow<3){u.reviveT=(u.reviveT||0)+dt;if(u.reviveT>=3){P.down=0;P.hp=40;P.rvt=0;u.reviveT=0;msg('SQUAD REVIVE COMPLETE')}}else if(!P.down)u.reviveT=0;",
"  });"
]
s="\n".join(lines[:starts[0]]+ally+lines[ends[0]:])+"\n"
old="function boom(x,z,R,d,q){if(!q){snd(0,.7,.5);ENV.boom(x,z,R,d)}bots.forEach(b=>{const k=Math.hypot(b.position.x-x,b.position.z-z);if(b.userData.alive&&k<R){b.userData.hp-=d*(1-k/R*.6);if(b.userData.hp<=0)killBot(b,true)}});const k=Math.hypot(P.x-x,P.z-z);if(k<R)dmg(d*(1-k/R*.6)*.5)}"
new="function boom(x,z,R,d,q){if(!q){snd(0,.7,.5);ENV.boom(x,z,R,d)}bots.forEach(b=>{const k=Math.hypot(b.position.x-x,b.position.z-z);if(b.userData.alive&&k<R){b.userData.hp-=d*(1-k/R*.6);if(b.userData.hp<=0)killBot(b,true)}});al.forEach(a=>{const u=a.userData,k=Math.hypot(a.position.x-x,a.position.z-z);if(!u.down&&u.alive!==false&&k<R){u.hp=(u.hp==null?100:u.hp)-d*(1-k/R*.6);if(u.hp<=0)killBot(a,false)}});const k=Math.hypot(P.x-x,P.z-z);if(k<R)dmg(d*(1-k/R*.6)*.5)}"
rep(old,new,"grenade friendly fire")
css='''/* BATTLE_ZONE_FEEDBACK_COMPLETION_V1 */
#lobby{overflow-x:hidden!important;overflow-y:auto!important;overscroll-behavior:contain;touch-action:pan-y}
#lobby #char{pointer-events:none!important;z-index:1!important}
#lobby #lb-top{z-index:12!important}
#lobby #lb-l,#lobby #maps{z-index:8!important;max-height:calc(100dvh - 118px)!important;overflow-y:auto!important;overscroll-behavior:contain;scrollbar-width:thin}
#lobby #setc .card,#lobby #maps .mc,#lobby #lb-nav b,#lobby #go2,#lobby #lo,#lobby #warroomBrief,#lobby #skp i{pointer-events:auto!important;touch-action:manipulation!important;cursor:pointer!important;position:relative}
#lobby #lb-nav{z-index:18!important;pointer-events:auto!important}
#lobby #go2{z-index:19!important;min-height:48px!important;touch-action:manipulation!important}
#lobby #warroomBrief{z-index:17!important;min-height:34px!important;touch-action:manipulation!important}
#lobby #sheet{z-index:50!important}
#lobby #shp{max-height:min(72dvh,440px)!important;overflow-y:auto!important;overscroll-behavior:contain}
#lobby .card:focus-visible,#lobby .mc:focus-visible,#lobby #lb-nav b:focus-visible,#lobby button:focus-visible{outline:2px solid #e6b85c!important;outline-offset:2px!important}
@media(max-width:760px) and (orientation:landscape){
#lobby #lb-l{left:8px!important;top:48px!important;width:clamp(132px,19vw,168px)!important}
#lobby #maps{right:8px!important;top:48px!important;width:clamp(220px,34vw,300px)!important;max-height:calc(100dvh - 108px)!important;flex-direction:row!important;overflow-x:auto!important;overflow-y:hidden!important}
#lobby #maps .mc{flex:0 0 116px!important;min-width:116px!important}
#lobby #char{width:clamp(96px,15vw,130px)!important;height:clamp(135px,40vh,175px)!important;top:53%!important}
#lobby #go2{left:8px!important;bottom:8px!important;min-width:140px!important;padding:10px 13px!important;font-size:12px!important}
#lobby #lb-nav{right:8px!important;bottom:8px!important;max-width:55vw!important;gap:4px!important}
#lobby #lb-nav b{min-width:44px!important;min-height:44px!important;padding:6px!important}
#lobby #warroomBrief{left:8px!important;bottom:64px!important;max-width:42vw!important;font-size:8px!important}}
@media(max-height:430px) and (orientation:landscape){#lobby #lb-top{top:5px!important}#lobby #lb-l,#lobby #maps{top:43px!important;max-height:calc(100dvh - 96px)!important}#lobby #go2,#lobby #lb-nav{bottom:6px!important}#lobby #warroomBrief{bottom:58px!important}}
@media(max-width:560px) and (orientation:portrait){#lobby #lb-l{top:54px!important;width:clamp(138px,42vw,174px)!important}#lobby #maps{top:54px!important;width:42vw!important;max-height:48dvh!important}#lobby #maps .mc{flex-basis:112px!important}#lobby #char{top:58%!important;width:104px!important;height:148px!important}#lobby #go2{left:10px!important;bottom:10px!important;min-width:140px!important;padding:11px 15px!important;font-size:13px!important}#lobby #lb-nav{right:8px!important;bottom:8px!important;max-width:54vw!important}#lobby #warroomBrief{left:10px!important;bottom:66px!important}}
@media(prefers-reduced-motion:reduce){#lobby #go2{animation:none!important}}
'''
cp=html.parent/"css"/"battlezone-feedback.css"; cp.parent.mkdir(parents=True,exist_ok=True); cp.write_text(css,encoding="utf-8")
link='<link rel="stylesheet" href="./css/battlezone-feedback.css">'
if link not in s: s=s.replace("</head>",link+"\n</head>",1)
s=s.replace("</html>","<!-- "+marker+" -->\n</html>",1); html.write_text(s,encoding="utf-8")
vs=list(root.rglob("validate_project.py"))
if len(vs)!=1: raise SystemExit(f"Expected one validator, found {len(vs)}")
vp=vs[0]; v=vp.read_text(encoding="utf-8")
v=v.replace("'ally medical support': 'u.healT' in source and 'P.hp<70' in source,","'ally medical support': 'u.healT' in source and 'P.hp<76' in source,",1)
v=v.replace("'airborne weapon hidden until landing': 'pm.hand.visible=!P.air&&!P.veh' in source,","'equipped weapon retained during freefall': 'gun.visible=!P.tp&&!P.veh&&P.air!==2' in source and 'pm.hand.visible=!P.veh&&P.air!==2' in source,",1)
oldcheck="'explosions do not damage squad allies': 'function boom(x,z,R,d,q)' in source and 'function thr()' in source and 'al.forEach' not in source.split('function boom(x,z,R,d,q)',1)[1].split('function thr()',1)[0],"
newcheck="'grenade friendly fire uses distance falloff': 'al.forEach(a=>{const u=a.userData,k=Math.hypot(a.position.x-x,a.position.z-z)' in source and 'if(u.hp<=0)killBot(a,false)' in source,"
if oldcheck not in v: raise SystemExit("Stale no-friendly-fire validator invariant not found")
v=v.replace(oldcheck,newcheck,1)
anchor="'ally medical support': 'u.healT' in source and 'P.hp<76' in source,"
checks="""
    'independent squad target selection and role tactics': all(token in source for token in ['squadRole','squadTarget','tacticalCoverPoint(a,en.position.x,en.position.z)','flankAngle','role===']),
    'squad regroups outside tactical radius': 'if(follow>34)' in source and 'follow<5' in source,
    'lobby duplicate navigation listeners removed': "const navIds={'wsb':'shop','msb':'rank','invb':'inventory','dlyb':'rank'}" not in source,
    'responsive lobby controls and hit targets': 'battlezone-feedback.css' in source and 'touch-action:manipulation' in (ASSET_DIR / 'css/battlezone-feedback.css').read_text(encoding='utf-8'),
"""
if anchor not in v: raise SystemExit("Validator insertion anchor not found")
v=v.replace(anchor,anchor+checks,1); vp.write_text(v,encoding="utf-8")
print("BATTLE_ZONE_FEEDBACK_COMPLETION_APPLIED",html)
