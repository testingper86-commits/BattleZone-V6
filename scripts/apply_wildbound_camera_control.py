#!/usr/bin/env python3
"""Install camera-relative movement and reliable orbit controls for WILDBOUND."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
matches = list(root.rglob("app/src/main/assets/www/js/wildbound/rendering/runtime.js"))
if len(matches) != 1:
    raise SystemExit(f"Expected one WILDBOUND runtime.js, found {len(matches)}")
path = matches[0]
source = path.read_text(encoding="utf-8")
marker = "WILDBOUND_CAMERA_RELATIVE_CONTROL_V1"
if marker in source:
    print("WILDBOUND_CAMERA_CONTROLS_ALREADY_APPLIED")
    raise SystemExit(0)

def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    source = source.replace(old, new, 1)

replace_once(
    "input:{x:0,z:0},invulnerable:0,target:null",
    "input:{x:0,z:0},cameraYaw:0,cameraHeight:3.1,invulnerable:0,target:null",
    "camera state",
)
replace_once(
    "game.player.position.set(0,0,12);const spawns=",
    "game.player.position.set(0,0,12);game.cameraYaw=game.player.rotation.y||0;game.cameraHeight=3.1;const spawns=",
    "camera initialization",
)
replace_once(
    "let x=game.input.x,z=game.input.z;if(keys['KeyW'])z-=1;if(keys['KeyS'])z+=1;if(keys['KeyA'])x-=1;if(keys['KeyD'])x+=1;let len=Math.hypot(x,z);if(len>1){x/=len;z/=len}if(len>.08){let angle=Math.atan2(x,z);p.rotation.y=angle;p.position.x+=x*W.CONFIG.PLAYER.speed*dt;p.position.z+=z*W.CONFIG.PLAYER.speed*dt;W.physics.clampWorld(p.position,W.CONFIG.WORLD.size*.5-4)}",
    "let x=game.input.x,z=game.input.z;if(keys['KeyW'])z-=1;if(keys['KeyS'])z+=1;if(keys['KeyA'])x-=1;if(keys['KeyD'])x+=1;let len=Math.hypot(x,z);if(len>1){x/=len;z/=len}if(len>.08){const angle=game.cameraYaw+Math.atan2(x,z),mx=Math.sin(angle),mz=Math.cos(angle);p.rotation.y=angle;p.position.x+=mx*W.CONFIG.PLAYER.speed*dt;p.position.z+=mz*W.CONFIG.PLAYER.speed*dt;W.physics.clampWorld(p.position,W.CONFIG.WORLD.size*.5-4)}",
    "camera-relative movement",
)
replace_once(
    "let desired=new T.Vector3(p.position.x+Math.sin(p.rotation.y)*5,3.1,p.position.z+Math.cos(p.rotation.y)*5);game.camera.position.lerp(desired,1-Math.pow(.001,dt));game.camera.lookAt(p.position.x,1.2,p.position.z-3);",
    "let desired=new T.Vector3(p.position.x+Math.sin(game.cameraYaw)*5,game.cameraHeight,p.position.z+Math.cos(game.cameraYaw)*5);game.camera.position.lerp(desired,1-Math.pow(.001,dt));game.camera.lookAt(p.position.x-Math.sin(game.cameraYaw)*3,1.2+(game.cameraHeight-3.1)*.25,p.position.z-Math.cos(game.cameraYaw)*3);",
    "orbit camera follow",
)
replace_once(
    "let dragging=false,lastX=0,startX=0,startY=0,activePointer=null;",
    "let dragging=false,lastX=0,lastY=0,startX=0,startY=0,activePointer=null;",
    "camera pointer state",
)
replace_once(
    "lastX=startX=e.clientX;startY=e.clientY;canvas.setPointerCapture(e.pointerId)",
    "lastX=startX=e.clientX;lastY=e.clientY;startY=e.clientY;canvas.setPointerCapture(e.pointerId)",
    "camera pointer origin",
)
replace_once(
    "game.player.rotation.y-=(e.clientX-lastX)*.006;lastX=e.clientX",
    "const dx=e.clientX-lastX,dy=e.clientY-lastY;game.cameraYaw-=dx*.006;game.cameraYaw=Math.atan2(Math.sin(game.cameraYaw),Math.cos(game.cameraYaw));game.cameraHeight=Math.max(2.2,Math.min(5.2,game.cameraHeight+dy*.012));lastX=e.clientX;lastY=e.clientY",
    "orbit camera input",
)
replace_once(
    "canvas.addEventListener('pointercancel',()=>{dragging=false;activePointer=null});",
    "canvas.addEventListener('pointercancel',()=>{dragging=false;activePointer=null});canvas.addEventListener('lostpointercapture',()=>{dragging=false;activePointer=null});window.addEventListener('blur',()=>{keys={};game.input.x=0;game.input.z=0;dragging=false;activePointer=null});",
    "pointer and focus recovery",
)
source = "/* " + marker + " */\n" + source
path.write_text(source, encoding="utf-8")
print("WILDBOUND_CAMERA_CONTROLS_APPLIED", path)
