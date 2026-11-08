#!/usr/bin/env python3
"""Prevent third-person camera clipping and make the rebuilt lobby preview responsive."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one index.html, found {len(files)}")
p=files[0]; s=p.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_CHARACTER_CAMERA_REPAIR_V1"
if marker not in s:
    def replace_once(source, old, new, label):
        count=source.count(old)
        if count!=1: raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
        return source.replace(old,new,1)
    s=replace_once(s,
        "const cam=new THREE.PerspectiveCamera(70,1,.1,900);S.add(cam);",
        "const cam=new THREE.PerspectiveCamera(70,1,.1,900);S.add(cam);const bzCameraRay=new THREE.Raycaster();",
        "camera raycaster initialization")
    old="if(P.tp){const bk=3.2,ph=P.pitch,shoulder=.7+ln*.92;cam.position.set(P.x+sy*bk*Math.cos(ph)+cy*shoulder,Math.max(.4,P.y+.3-Math.sin(ph)*bk*.8),P.z+cy*bk*Math.cos(ph)-sy*shoulder)}else cam.position.set(P.x+cy*ln*.6,P.y,P.z-sy*ln*.6);cam.rotation.set(P.pitch,P.yaw,-ln*.34,'YXZ')"
    new=("if(P.tp){const bk=3.2,ph=P.pitch,shoulder=.7+ln*.92,bzCamFocus=new THREE.Vector3(P.x,P.y-.35,P.z),"
         "bzCamDesired=new THREE.Vector3(P.x+sy*bk*Math.cos(ph)+cy*shoulder,Math.max(.4,P.y+.3-Math.sin(ph)*bk*.8),P.z+cy*bk*Math.cos(ph)-sy*shoulder),"
         "bzCamDelta=bzCamDesired.clone().sub(bzCamFocus),bzCamDistance=bzCamDelta.length();"
         "if(bzCamDistance>.01){bzCameraRay.set(bzCamFocus,bzCamDelta.normalize());bzCameraRay.near=.12;bzCameraRay.far=bzCamDistance;"
         "const bzCamHit=bzCameraRay.intersectObjects(solid,false)[0];"
         "if(bzCamHit)bzCamDesired.copy(bzCamFocus).addScaledVector(bzCameraRay.ray.direction,Math.max(.2,bzCamHit.distance-.28));}"
         "bzCamDesired.y=Math.max(bzCamDesired.y,gS(bzCamDesired.x,bzCamDesired.z,bzCamDesired.y)+.28);cam.position.copy(bzCamDesired);"
         "}else cam.position.set(P.x+cy*ln*.6,P.y,P.z-sy*ln*.6);cam.rotation.set(P.pitch,P.yaw,-ln*.34,'YXZ')")
    s=replace_once(s,old,new,"post-rebuild third-person camera collision and terrain clearance")
    old="lr.setPixelRatio(Math.min(devicePixelRatio||1,1));lr.setSize(220,300,false);const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,220/300,.1,50);"
    new="const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,1,.1,50);"
    s=replace_once(s,old,new,"rebuilt lobby renderer fixed-size initialization")
    old="ld.position.set(3,5,4);ls.add(ld);"
    new=("ld.position.set(3,5,4);ls.add(ld);"
         "const fitLobbyRenderer=()=>{const w=Math.max(1,host.clientWidth||220),h=Math.max(1,host.clientHeight||300);"
         "lr.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));lr.setSize(w,h,false);lc.aspect=w/h;lc.updateProjectionMatrix()};"
         "fitLobbyRenderer();window.addEventListener('resize',fitLobbyRenderer,{passive:true});")
    s=replace_once(s,old,new,"responsive lobby preview sizing")
    old="lc.position.set(0,1.1,4.6);lc.lookAt(0,1,0);"
    new="lc.position.set(0,1.05,3.8);lc.lookAt(0,1,0);"
    s=replace_once(s,old,new,"lobby operator camera framing")
    if s.count("</html>")!=1: raise SystemExit("Expected exactly one closing html tag")
    s=s.replace("</html>","<!-- "+marker+" -->"+chr(10)+"</html>",1)
    p.write_text(s,encoding="utf-8")
print(marker+" applied",p)
