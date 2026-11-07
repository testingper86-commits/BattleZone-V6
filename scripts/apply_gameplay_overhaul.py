from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/index.html'
s=p.read_text(encoding='utf-8')
marker='BATTLE_ZONE_GAMEPLAY_OVERHAUL_V1'
if marker in s:
 print('Gameplay repair already applied; source is unchanged.')
 raise SystemExit(0)
def once(old,new,label):
 global s
 n=s.count(old)
 if n!=1: raise SystemExit(f'{label}: expected exactly 1 source match, found {n}')
 s=s.replace(old,new,1); print('PATCHED',label)
once("function inW(x,z){return (Math.hypot(x-lake.x,z-lake.z)<lake.r&&ENV.ice<.6)||(MAP.sea&&Math.hypot(x,z)>320)||(rv.w>0&&Math.abs(z-rv.z)<rv.w/2&&Math.abs(x-br.x)>3)}",
"function inW(x,z){return (Math.hypot(x-lake.x,z-lake.z)<lake.r&&ENV.ice<.6)||(MAP.sea&&Math.hypot(x,z)>320)||(rv.w>0&&Math.abs(z-rv.z)<rv.w/2&&Math.abs(x-br.x)>3)}",'water-region guard')
once("if(E.swim&&!P.veh&&!P.air){cam.position.y-=.9;if(Math.random()<dt*6)E.fx('bubble',P.x+rnd(-.5,.5),.3,P.z+rnd(-.5,.5),1)}",
"if(E.swim&&!P.veh&&!P.air){P.waterDamage=(P.waterDamage||0)+dt;if(P.waterDamage>=1){P.waterDamage-=1;dmg(7)}cam.position.y-=.9;if(Math.random()<dt*6)E.fx('bubble',P.x+rnd(-.5,.5),.3,P.z+rnd(-.5,.5),1)}else P.waterDamage=0",'underwater health damage')
once("g.rotation.y=g.userData.yaw;S.add(g);veh.push(g)",
"g.rotation.y=g.userData.yaw;g.traverse(o=>{if(o.isMesh)o.userData.vehicleRoot=g});S.add(g);veh.push(g)",'vehicle hitbox ownership')
once("const h=rc.intersectObjects([...tg,...solid],false)[0];ENV.impact(h,rc.ray);\n if(h&&h.object.userData.bot){",
"const h=rc.intersectObjects([...tg,...solid,...veh],true)[0];ENV.impact(h,rc.ray);\n if(h&&h.object.userData.vehicleRoot){const vg=h.object.userData.vehicleRoot,vu=vg.userData;vu.hp=(vu.hp??100)-Math.max(18,W[P.w].d*2);if(vu.hp<=0&&!vu.dead){boom(vg.position.x,vg.position.z,14,70);vu.dead=1;vu.v=0;msg('Vehicle destroyed!')}}\n if(h&&h.object.userData.bot){",'shootable vehicles and destruction')
once("SQ=[0,1,3][+(sg('bzs')||0)]","SQ=[0,1,3][+(sg('bzs')??2)]",'default squad size')
once("let sqi=+(sg('bzs')||0);","let sqi=+(sg('bzs')??2);",'default squad selector')
once("if(en){a.rotation.y=Math.atan2(en.position.x-a.position.x,en.position.z-a.position.z);if(u.cd<=0){u.cd=rnd(.5,1);if(Math.random()<.5){en.userData.hp-=15;if(en.userData.hp<=0)killBot(en,false)}}}",
"if(en){a.rotation.y=Math.atan2(en.position.x-a.position.x,en.position.z-a.position.z);if(u.cd<=0){u.cd=rnd(.5,1);if(Math.random()<.72){en.userData.hp-=15;if(en.userData.hp<=0)killBot(en,false)}}}", 'ally combat reliability')
once("if(P.down&&dl<4){P.rvt=(P.rvt||0)+dt;if(P.rvt>=3){P.down=0;P.hp=40;P.rvt=0;msg('Teammate revived you!')}}});",
"if(!P.down&&P.hp<70&&dl<7){u.healT=(u.healT||0)+dt;if(u.healT>=2.5){P.hp=Math.min(100,P.hp+12);u.healT=0;msg('Teammate provided medical support')}}else u.healT=0;if(P.down&&dl<4){P.rvt=(P.rvt||0)+dt;if(P.rvt>=3){P.down=0;P.hp=40;P.rvt=0;msg('Teammate revived you!')}}});",'ally medical support')
once("jz.addEventListener('pointerup',jend);jz.addEventListener('pointercancel',jend);",
"jz.addEventListener('pointerup',jend);jz.addEventListener('pointercancel',jend);jz.addEventListener('lostpointercapture',jend);",'joystick capture-loss recovery')
once("$('c').addEventListener('pointerup',lend);$('c').addEventListener('pointercancel',lend);",
"$('c').addEventListener('pointerup',lend);$('c').addEventListener('pointercancel',lend);$('c').addEventListener('lostpointercapture',lend);",'camera capture-loss recovery')
once("el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up)};",
"el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);el.addEventListener('lostpointercapture',up)};",'button capture-loss recovery')
once("holdDrive('drive-gas','gas');holdDrive('drive-brake','brake');holdDrive('drive-left','left');holdDrive('drive-right','right');",
"holdDrive('drive-gas','gas');holdDrive('drive-brake','brake');holdDrive('drive-left','left');holdDrive('drive-right','right');\nfunction clearGameplayInputs(){jid=null;joy={x:0,y:0};kn.style.transform='';lid=null;fire=false;Object.keys(driveInput).forEach(k=>driveInput[k]=0);document.querySelectorAll('.on').forEach(e=>e.classList.remove('on'))}\nwindow.addEventListener('blur',clearGameplayInputs);document.addEventListener('visibilitychange',()=>{if(document.hidden)clearGameplayInputs()});",
'mobile focus and visibility input cleanup')
once("const dt=Math.min((n-last)/1000,.05);last=n;","const dt=Math.min((n-last)/1000,.1);last=n;",'frame delta recovery')
once("R.setPixelRatio(LQ?1:Math.min(devicePixelRatio,1.6));","R.setPixelRatio(LQ?1:Math.min(devicePixelRatio,1.25));",'mobile render pixel budget')
once("function applyBS(){R.setPixelRatio(BS?1:(LQ?1:Math.min(devicePixelRatio,2)));rs()}","function applyBS(){R.setPixelRatio(BS?1:(LQ?1:Math.min(devicePixelRatio,1.25)));rs()}",'battery saver pixel budget')
once("sun.shadow.mapSize.set(1024,1024);","sun.shadow.mapSize.set(512,512);",'mobile shadow map budget')
s=s.replace('</script>','/* '+marker+' */\n</script>',1)
p.write_text(s,encoding='utf-8')
(root/'GAMEPLAY_REPAIR_LOG.md').write_text('''# Gameplay repair patch\n\nApplied exact-match guarded changes to the canonical offline source:\n- Underwater health decreases by 7 HP per submerged second.\n- Bullet raycasts include vehicle meshes; vehicles have health and explode when destroyed.\n- New installs default to Squad; saved Solo/Duo/Squad choices are preserved.\n- TDM allies have improved firing reliability and provide nearby medical support, while retaining revive behavior.\n- Joystick, camera, and action controls release on lost pointer capture; window blur and app backgrounding clear held inputs.\n- Frame delta cap increased to 100 ms to avoid slow-motion after frame stalls; mobile pixel ratio and shadow map budgets reduced.\n\nThis patch is not a substitute for physical-device QA. Animation state transitions and full map-art upgrades remain separate verification items.\n''',encoding='utf-8')
print('GAMEPLAY_REPAIR_APPLIED')
