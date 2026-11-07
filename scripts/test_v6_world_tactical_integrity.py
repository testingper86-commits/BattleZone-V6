#!/usr/bin/env python3
"""Regression gate for world occlusion, weapon aim and vehicle coordinate integrity."""
from pathlib import Path
import json
import subprocess
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
s=paths[0].read_text(encoding='utf-8')
models_paths=list(root.rglob('app/src/main/assets/www/js/models.js'))
if len(models_paths)!=1: raise SystemExit(f'Expected exactly one models.js, found {len(models_paths)}')
ms=models_paths[0].read_text(encoding='utf-8')
gradle_paths=list(root.rglob('app/build.gradle.kts'))
if len(gradle_paths)!=1: raise SystemExit(f'Expected exactly one app/build.gradle.kts, found {len(gradle_paths)}')
gs=gradle_paths[0].read_text(encoding='utf-8')
checks={
'cylinder cover raycast blockers':'S.add(m);solid.push(m);return m}' in s,
'broadleaf trunk occlusion':'S.add(trunk);solid.push(trunk);trunk.castShadow' in s,
'instanced forest trunk occlusion':'S.add(L,T);solid.push(T)' in s,
'grouped prop child meshes registered':'g.traverse(o=>{if(o.isMesh)solid.push(o)})' in s,
'deadfall occlusion':'obs.push({x,z,w:.8,d:.8});solid.push(t);for(let k=0;k<3;k++)' in s,
'shared tactical raycaster':'const bzLosRayState={ray:new THREE.Raycaster(),origin:new THREE.Vector3(),direction:new THREE.Vector3(),hits:[]};' in s,
'reused ray vectors and hit buffer':'state.origin.set(ax,ay,az);' in s and 'state.direction.set(dx,dy,dz).normalize();' in s and 'state.hits.length=0;' in s and 'state.ray.intersectObjects(solid,false,state.hits);' in s,
'no per-query raycaster allocation':'function hasClearShot(ax,ay,az,bx,by,bz){' in s and 'const ray=new THREE.Raycaster' not in s[s.index('function hasClearShot(ax,ay,az,bx,by,bz){'):s.index('}',s.index('function hasClearShot(ax,ay,az,bx,by,bz){'))+1],
'non-finite shot coordinates are rejected':'if(!Number.isFinite(dist))return false;if(dist<.2)return true;' in s,
'world marker present':'BATTLEZONE_V6_WORLD_TACTICAL_INTEGRITY_V1' in s,
'attachment multipliers reduce spread':'const sp_=0.01*(P.grip?0.65:1)*(P.comp?0.75:1);' in s,
'boolean-as-spread defect removed':'const sp_=P.grip||P.comp?.005:.01;' not in s,
'player follows clamped vehicle transform':'g.rotation.y=u.yaw;bzV6AnimateVehicleWheels(g,u,dt,fx);P.x=g.position.x;P.z=g.position.z;fx=fz=0;' in s,
'vehicle exit collision and world clamp':'const exit=hit(P.x,P.z,.5,0);[P.x,P.z]=clampWorld(exit[0],exit[1],.8);' in s,
'vehicle collision damage marker':'BATTLEZONE_V6_VEHICLE_COLLISION_DAMAGE_V1' in s,
'vehicle helper extraction boundary marker':'/* BZ_V6_VEHICLE_IMPACT_HELPER_END */' in s,
'vehicle health and crash cooldown initialize':'hp:100,crashCd:0' in s,
'vehicle crash cooldown decays each frame':'u.crashCd=Math.max(0,(Number(u.crashCd)||0)-dt);' in s,
'vehicle collision is speed-gated and cooldown-limited':'impact<=6||(Number(u.crashCd)||0)>0' in s,
'vehicle collision damage is applied before speed damping':'bzV6ApplyVehicleImpact(g,u,Math.abs(u.v),nx,nz);u.v*=.3;' in s,
'vehicle dynamics marker present':'BATTLEZONE_V6_VEHICLE_DYNAMICS_V1' in s,
'vehicle braking is independent from throttle':'bzV6StepVehicleDynamics(u,throttle,brake,dt);' in s and 'driveInput.brake+(key.KeyS?1:0)' in s and 'driveInput.gas+(key.KeyW?1:0)' in s,
'vehicle top speed is bounded':'maxSpeed:Math.max(12,Math.min(32,a*1.05))' in s,
'vehicle reverse speed is bounded':'maxReverseSpeed:6' in s,
'destroyed vehicles cannot accelerate':'if(u.dead){u.v=0;return 0}' in s,
'vehicle wheel animation marker present':'BATTLEZONE_V6_VEHICLE_WHEEL_ANIMATION_V1' in s,
'vehicle wheels are tagged by axle':'w.userData.bzVehicleWheel=1;w.userData.bzSteeringWheel=d>0;' in s,
'vehicle wheel animation avoids tree traversal':'for(let i=0;i<g.children.length;i++){const w=g.children[i],d=w.userData;' in s and 'g.traverse(' not in s[s.find('function bzV6AnimateVehicleWheels('):s.find('/* BZ_V6_VEHICLE_WHEEL_ANIMATION_HELPER_END */')],
'vehicle wheel spin and steering update wired':'bzV6AnimateVehicleWheels(g,u,dt,fx);' in s,
'combat marker present':'BATTLEZONE_V6_COMBAT_CONTROL_INTEGRITY_V1' in s,
'AI line-of-sight marker present':'BATTLEZONE_V6_TACTICAL_LINE_OF_SIGHT_V1' in s,
'enemy AI checks visibility before target lock':'if(!hasClearShot(bot.position.x,bot.position.y+1.15,bot.position.z,target.x,targetY,target.z))' in s,
'enemy AI temporarily suppresses occluded targets':'u.aiBlockedTarget=target.o||null;u.aiBlockedT=1.0;' in s,
'squad AI checks visibility before pursuing':'function bzV6ValidateSquadTarget(actor,u,target){' in s and 'if(!hasClearShot(actor.position.x,actor.position.y+1.15,actor.position.z,target.position.x,target.position.y+1.1,target.position.z))' in s,
'squad AI temporarily suppresses occluded targets':'u.squadBlockedTarget=target;u.squadBlockedT=1.0;' in s,
'squad LOS cadence is target-specific':'u.squadLosT>0&&u.squadLosTarget===target' in s and 'u.squadLosTarget=target;' in s,
'frame-loop marker present':'BATTLEZONE_V6_FRAME_LOOP_EFFICIENCY_V1' in s,
'Android install version incremented':'BATTLEZONE_V6_BUILD_VERSION_1_2_2' in gs and 'versionCode = 5' in gs and 'versionName = \"1.2.2\"' in gs,
'CC0 tactical voice runtime marker present':'BATTLEZONE_V6_CC0_VOICEOVER_V1' in s and 'audio/cc0_voiceover/' in s,
'frame telemetry object is reused':'bzFrameGameState.started=!!started;' in s and "window.BZGameState={started:!!started,health:Number(P.hp)||0,alive:!!P.alive,weapon:W[P.w]?.n||'Weapon'};" not in s,
'movement classes update only on state changes':"if(bzMove!==bzFrameLastMoving){document.body.classList.toggle('bz-moving',!!bzMove);" in s and "if(bzRunning!==bzFrameLastRunning){document.body.classList.toggle('bz-running',bzRunning);" in s,
'animation fallback marker present':'BATTLEZONE_V6_ANIMATION_FALLBACK_V1' in s and 'BATTLEZONE_V6_ANIMATION_FALLBACK_V1' in ms,
'missing combat clips use procedural fallback':"if(!action){" in ms and 'a.fallbackTimer=a.fallbackDuration' in ms,
'reload fallback has a bounded duration':"fallbackDuration=state==='reload'?1.5:.22" in ms,
'weapon mount base transform is preserved':'weaponBasePosition' in ms and 'weaponBaseRotation' in ms,
'shoot fallback animates weapon recoil':'entry.weaponMount.position.z-=.075*pulse' in ms,
'reload fallback animates weapon tilt':'entry.weaponMount.rotation.x-=.58*pulse' in ms,
'fallback timer expires and restores locomotion':'e.an.fallbackTimer=Math.max(0,e.an.fallbackTimer-dt)' in ms and 'const want=pickAct(e,sp)' in ms,
}
for name,ok in checks.items(): print(('PASS ' if ok else 'FAIL ')+name)
if not all(checks.values()): raise SystemExit(f'{sum(not x for x in checks.values())} integrity checks failed')
print(f'WORLD_TACTICAL_INTEGRITY_OK checks={len(checks)}')

# Exercise vehicle impact damage independently of Three.js and the render loop.
vehicle_start=s.find('function bzV6ApplyVehicleImpact(')
vehicle_end=s.find('/* BZ_V6_VEHICLE_IMPACT_HELPER_END */',vehicle_start)
if vehicle_start<0 or vehicle_end<0:
    raise SystemExit('Missing vehicle collision damage helper')
vehicle_helper=s[vehicle_start:vehicle_end]
vehicle_js=f"""const vm=require('node:vm');let fx=0,ignite=0;const c={{E:{{fx:()=>fx++,ignite:()=>ignite++}}}};vm.createContext(c);vm.runInContext({json.dumps(vehicle_helper)},c);const g={{position:{{x:3,z:4}}}},u={{hp:100,crashCd:0,v:10,dead:0}};if(c.bzV6ApplyVehicleImpact(g,u,6,3,4)!==false||u.hp!==100)throw Error('low-speed impact must not damage vehicle');if(c.bzV6ApplyVehicleImpact(g,u,10,3,4)!==false||u.hp!==91||u.crashCd!==1||fx!==1)throw Error('impact damage or spark effect incorrect');if(c.bzV6ApplyVehicleImpact(g,u,40,3,4)!==false||u.hp!==91)throw Error('crash cooldown must suppress repeated impact damage');u.crashCd=0;c.bzV6ApplyVehicleImpact(g,u,40,3,4);u.crashCd=0;c.bzV6ApplyVehicleImpact(g,u,40,3,4);u.crashCd=0;if(c.bzV6ApplyVehicleImpact(g,u,40,3,4)!==true||!u.dead||u.v!==0||ignite!==1)throw Error('vehicle destruction must stop and ignite the vehicle');"""
vehicle_run=subprocess.run(['node','-e',vehicle_js],capture_output=True,text=True)
if vehicle_run.returncode:
    raise SystemExit(vehicle_run.stderr or vehicle_run.stdout)
print('PASS vehicle collision damage behavior')

# Exercise vehicle throttle/brake dynamics independently of Three.js.
dynamics_start=s.find('function bzV6StepVehicleDynamics(')
dynamics_end=s.find('/* BZ_V6_VEHICLE_DYNAMICS_HELPER_END */',dynamics_start)
if dynamics_start<0 or dynamics_end<0:
    raise SystemExit('Missing vehicle dynamics helper')
dynamics_helper=s[dynamics_start:dynamics_end]
dynamics_js=f"""const vm=require('node:vm');const c={{}};vm.createContext(c);vm.runInContext({json.dumps(dynamics_helper)},c);const step=c.bzV6StepVehicleDynamics;const u={{a:20,brakePower:32,maxSpeed:21,maxReverseSpeed:6,v:0,dead:0}};const near=(a,b)=>Math.abs(a-b)<1e-8;
if(!near(step(u,1,0,.1),2))throw Error('throttle acceleration incorrect');
u.v=20;if(!near(step(u,0,1,.1),16.8))throw Error('brake must decelerate forward motion');
for(let i=0;i<12;i++)step(u,0,1,.1);if(u.v!==0)throw Error('braking to a stop must not reverse the vehicle');
u.v=-5;step(u,0,1,.1);if(u.v>=0)throw Error('brake must reduce reverse motion without changing direction');
for(let i=0;i<12;i++)step(u,0,1,.1);if(u.v!==0)throw Error('brake must stop reverse motion');
u.v=100;step(u,0,0,.1);if(u.v>21)throw Error('vehicle exceeded its forward speed limit');
u.v=-100;step(u,0,0,.1);if(u.v< -6)throw Error('vehicle exceeded its reverse speed limit');
u.v=10;const before=u.v;step(u,0,0,.1);if(!(u.v<before&&u.v>0))throw Error('coasting drag must reduce speed smoothly');
u.v=8;u.dead=1;if(step(u,1,0,.1)!==0||u.v!==0)throw Error('destroyed vehicle must remain immobilized');
"""
dynamics_run=subprocess.run(['node','-e',dynamics_js],capture_output=True,text=True)
if dynamics_run.returncode:
    raise SystemExit(dynamics_run.stderr or dynamics_run.stdout)
print('PASS vehicle throttle, brake, speed limits and destruction behavior')

# Exercise vehicle wheel spin, front steering, and body roll without Three.js.
wheel_start=s.find('function bzV6AnimateVehicleWheels(')
wheel_end=s.find('/* BZ_V6_VEHICLE_WHEEL_ANIMATION_HELPER_END */',wheel_start)
if wheel_start<0 or wheel_end<0:
    raise SystemExit('Missing vehicle wheel animation helper')
wheel_helper=s[wheel_start:wheel_end]
wheel_js=f"""const vm=require('node:vm');const c={{}};vm.createContext(c);vm.runInContext({json.dumps(wheel_helper)},c);const spinFront={{userData:{{bzVehicleWheel:1,bzSteeringWheel:true}},rotation:{{x:0,y:0}}}},spinRear={{userData:{{bzVehicleWheel:1,bzSteeringWheel:false}},rotation:{{x:0,y:0}}}},other={{userData:{{}},rotation:{{x:0,y:0}}}};const g={{children:[spinFront,spinRear,other],rotation:{{z:0}}}},u={{v:10}};c.bzV6AnimateVehicleWheels(g,u,.1,1);const near=(a,b)=>Math.abs(a-b)<1e-8;if(!near(spinFront.rotation.x,2.4)||!near(spinRear.rotation.x,2.4))throw Error('wheel spin does not follow vehicle speed');if(!near(spinFront.rotation.y,.32)||spinRear.rotation.y!==0)throw Error('only front wheels should steer');if(!(g.rotation.z<0))throw Error('vehicle body roll should respond to steering');c.bzV6AnimateVehicleWheels(g,{{v:-10}},.1,-1);if(!near(spinFront.rotation.x,0)||!near(spinFront.rotation.y,-.32)||!(g.rotation.z>0))throw Error('reverse wheel animation/steering is incorrect');const x=spinFront.rotation.x;c.bzV6AnimateVehicleWheels(g,u,NaN,1);if(spinFront.rotation.x!==x)throw Error('invalid frame delta must not animate wheels');"""
wheel_run=subprocess.run(['node','-e',wheel_js],capture_output=True,text=True)
if wheel_run.returncode:
    raise SystemExit(wheel_run.stderr or wheel_run.stdout)
print('PASS vehicle wheel spin, steering and body roll behavior')
