#!/usr/bin/env python3
"""Prevent third-person camera clipping and render the lobby operator at device resolution."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one index.html, found {len(files)}")
p=files[0]; s=p.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_CHARACTER_CAMERA_REPAIR_V1"
if marker in s:
    print(marker+" already applied")
else:
    def once(old,new,label):
        nonlocal_dummy=None
        global s
        n=s.count(old)
        if n!=1: raise SystemExit(f"{label}: expected one anchor, found {n}")
        s=s.replace(old,new,1)
    once("const cam=new THREE.PerspectiveCamera(70,1,.1,900);S.add(cam);",
         "const cam=new THREE.PerspectiveCamera(70,1,.1,900);S.add(cam);const bzCameraRay=new THREE.Raycaster();",
         "camera raycaster initialization")
    old="if(P.tp){const bk=3.2,ph=P.pitch;cam.position.set(P.x+sy*bk*Math.cos(ph)+cy*.7,Math.max(.4,P.y+.3-Math.sin(ph)*bk*.8),P.z+cy*bk*Math.cos(ph)-sy*.7)}else cam.position.set(P.x+cy*ln*.6,P.y,P.z-sy*ln*.6);cam.rotation.set(P.pitch,P.yaw,-ln*.25,'YXZ')"
    new=("if(P.tp){const bk=3.2,ph=P.pitch,bzCamFocus=new THREE.Vector3(P.x,P.y-.35,P.z),"
         "bzCamDesired=new THREE.Vector3(P.x+sy*bk*Math.cos(ph)+cy*.7,Math.max(.4,P.y+.3-Math.sin(ph)*bk*.8),P.z+cy*bk*Math.cos(ph)-sy*.7),"
         "bzCamDelta=bzCamDesired.clone().sub(bzCamFocus),bzCamDistance=bzCamDelta.length();"
         "if(bzCamDistance>.01){bzCameraRay.set(bzCamFocus,bzCamDelta.normalize());bzCameraRay.near=.12;bzCameraRay.far=bzCamDistance;"
         "const bzCamHit=bzCameraRay.intersectObjects(solid,false)[0];"
         "if(bzCamHit)bzCamDesired.copy(bzCamFocus).addScaledVector(bzCameraRay.ray.direction,Math.max(.2,bzCamHit.distance-.28));}"
         "bzCamDesired.y=Math.max(bzCamDesired.y,gS(bzCamDesired.x,bzCamDesired.z,bzCamDesired.y)+.28);cam.position.copy(bzCamDesired);"
         "}else cam.position.set(P.x+cy*ln*.6,P.y,P.z-sy*ln*.6);cam.rotation.set(P.pitch,P.yaw,-ln*.25,'YXZ')")
    once(old,new,"third-person camera collision and terrain clearance")
    old="lr.setSize(220,300,false);const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,220/300,.1,50);"
    new="const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,1,.1,50);"
    once(old,new,"lobby renderer fixed-size initialization")
    old="ld.position.set(3,5,4);ls.add(ld);"
    new=("ld.position.set(3,5,4);ls.add(ld);"
         "const fitLobbyRenderer=()=>{const w=Math.max(1,$('char').clientWidth||220),h=Math.max(1,$('char').clientHeight||300);"
         "lr.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));lr.setSize(w,h,false);lc.aspect=w/h;lc.updateProjectionMatrix()};"
         "fitLobbyRenderer();window.addEventListener('resize',fitLobbyRenderer,{passive:true});")
    once(old,new,"responsive lobby renderer sizing")
    old="lc.position.set(0,1.1,4.6);lc.lookAt(0,1,0);"
    new="lc.position.set(0,1.05,3.8);lc.lookAt(0,1,0);"
    once(old,new,"lobby operator camera framing")
    if s.count("</html>")!=1: raise SystemExit("Expected exactly one closing html tag")
    s=s.replace("</html>","<!-- "+marker+" -->"+chr(10)+"</html>",1)
    p.write_text(s,encoding="utf-8")
print(marker+" applied",p)
