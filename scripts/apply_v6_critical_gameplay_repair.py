#!/usr/bin/env python3
"""Repair BattleZone V6 runtime initialization, HUD, touch controls and visual presentation."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = list(root.rglob("app/src/main/assets/www/index.html"))
if len(paths) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(paths)}")
html = paths[0]
s = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_V2"
css_marker = "BATTLEZONE_V6_CRITICAL_CONTROLS_GRAPHICS_V2"
if marker in s and css_marker in s:
    print("BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_ALREADY_APPLIED")

def once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one exact source anchor, found {count}")
    return source.replace(old, new, 1)

# BufferGeometry is not an Object3D and has no .rotation property. Rotate its vertices.
for old, new, label in [
    ("rootA.rotation.z=Math.PI/2;", "rootA.rotateZ(Math.PI/2);", "root geometry A rotation"),
    ("rootB.rotation.z=-Math.PI/2;", "rootB.rotateZ(-Math.PI/2);", "root geometry B rotation"),
    ("rootC.rotation.x=Math.PI/2;", "rootC.rotateX(Math.PI/2);", "root geometry C rotation"),
    ("rootD.rotation.x=-Math.PI/2;", "rootD.rotateX(-Math.PI/2);", "root geometry D rotation"),
    ("branchA.rotation.z=-.68;", "branchA.rotateZ(-.68);", "branch geometry A rotation"),
    ("branchB.rotation.z=.68;", "branchB.rotateZ(.68);", "branch geometry B rotation"),
    ("branchC.rotation.x=.68;", "branchC.rotateX(.68);", "branch geometry C rotation"),
]:
    if old in s:
        s = once(s, old, new, label)
    elif new not in s:
        raise SystemExit(f"{label}: neither original nor repaired anchor exists")

# Improve clarity and color separation while retaining the existing adaptive/battery-saver governor.
for old, new, label in [
    ("R.setPixelRatio(LQ?.9:Math.min(devicePixelRatio,1.05));", "R.setPixelRatio(LQ?.9:Math.min(devicePixelRatio||1,1.35));", "base render resolution"),
    ("R.toneMappingExposure=1.08;", "R.toneMappingExposure=1.16;", "display exposure"),
    ("new THREE.HemisphereLight(0xffffff,0x556633,.95)", "new THREE.HemisphereLight(0xffffff,0x354c39,1.08)", "ambient light contrast"),
    ("new THREE.DirectionalLight(0xffffff,.6*(MAP.nt?.25:1))", "new THREE.DirectionalLight(0xffffff,.72*(MAP.nt?.25:1))", "sunlight intensity"),
    ("const ratio=[.82,1,1.2][bzQualityTier];", "const ratio=[.88,1.12,1.32][bzQualityTier];", "adaptive render sharpness"),
]:
    if old in s:
        s = once(s, old, new, label)
    elif new not in s:
        raise SystemExit(f"{label}: expected renderer anchor is missing")

# The final icon pass runs after the initial HUD construction. Preserve the IDs hudUpdate writes.
old = "Object.entries(bzControlIcons).forEach(([id,v])=>{const e=$(id);if(e)e.innerHTML='<span class=\"bz-control-symbol\">'+v[0]+'</span><small>'+v[1]+'</small>'});"
new = "Object.entries(bzControlIcons).forEach(([id,v])=>{const e=$(id);if(e){const valueId=id==='thr'?' id=\"thrn\"':id==='gsw'?' id=\"gswn\"':'';e.innerHTML='<span class=\"bz-control-symbol\">'+v[0]+'</span><small'+valueId+'>'+v[1]+'</small>'}});"
if old in s: s = once(s, old, new, "preserve grenade HUD nodes")
elif "const valueId=id==='thr'?' id=\"thrn\"'" not in s:
    raise SystemExit("Final control icon renderer has an unknown implementation")

# Ship a consistent landscape-first tactical HUD with separated touch targets and responsive safe areas.
css = r'''/* BATTLEZONE_V6_CRITICAL_CONTROLS_GRAPHICS_V2 */
:root{--bz-safe-l:env(safe-area-inset-left,0px);--bz-safe-r:env(safe-area-inset-right,0px);--bz-safe-t:env(safe-area-inset-top,0px);--bz-safe-b:env(safe-area-inset-bottom,0px);--bz-glass:rgba(7,17,28,.82);--bz-line:rgba(190,220,242,.34);--bz-cyan:#53d9ff;--bz-gold:#ffd45a}
html,body{overscroll-behavior:none;-webkit-tap-highlight-color:transparent}
#c{image-rendering:auto;touch-action:none}
.b{display:flex;flex-direction:column;gap:2px;align-items:center;justify-content:center;min-width:48px;min-height:48px;width:52px;height:52px;padding:4px;border:1px solid var(--bz-line);border-radius:14px;background:linear-gradient(155deg,rgba(28,48,67,.9),rgba(5,13,23,.88));box-shadow:0 5px 16px #0007,inset 0 1px 0 #ffffff20;color:#f4f8fc;font:800 10px/1.05 system-ui,sans-serif;letter-spacing:.035em;backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);touch-action:none;user-select:none;-webkit-user-select:none}
.b .bz-control-symbol{font-size:19px;line-height:1;color:#c9efff}.b small{font:800 9px/1 system-ui,sans-serif;letter-spacing:.04em}.b.on{transform:scale(.94);border-color:var(--bz-cyan);background:linear-gradient(155deg,#28516b,#102b40);box-shadow:0 0 0 2px #53d9ff25,0 4px 12px #0008}
#joy{width:142px;height:142px;border:1px solid #ffffff55;background:radial-gradient(circle,#d6eaff16 0 35%,#07111bc9 72%);box-shadow:inset 0 0 22px #0007,0 8px 22px #0008}
#knob{left:calc(50% - 22px);top:calc(50% - 22px);width:44px;height:44px;border:2px solid #ffffffb0;background:linear-gradient(145deg,#d8f6ff,#7b9eb0);box-shadow:0 3px 12px #0009}
#fire{right:calc(var(--bz-safe-r) + 18px);bottom:calc(var(--bz-safe-b) + 22px);width:88px;height:88px;border:1px solid #ff9b83;background:linear-gradient(145deg,#e94b43eF,#8f211eeF);box-shadow:0 7px 20px #0009,inset 0 1px 0 #ffffff55}
#fire .bz-control-symbol{font-size:25px;color:#fff}
#jump{right:calc(var(--bz-safe-r) + 20px);bottom:calc(var(--bz-safe-b) + 122px)}
#crouch{right:calc(var(--bz-safe-r) + 82px);bottom:calc(var(--bz-safe-b) + 122px)}
#prone{right:calc(var(--bz-safe-r) + 144px);bottom:calc(var(--bz-safe-b) + 122px)}
#rel{right:calc(var(--bz-safe-r) + 82px);bottom:calc(var(--bz-safe-b) + 22px)}
#swap{right:calc(var(--bz-safe-r) + 144px);bottom:calc(var(--bz-safe-b) + 22px)}
#scope{right:calc(var(--bz-safe-r) + 20px);bottom:calc(var(--bz-safe-b) + 222px)}
#thr{right:calc(var(--bz-safe-r) + 206px);bottom:calc(var(--bz-safe-b) + 22px)}
#gsw{right:calc(var(--bz-safe-r) + 206px);bottom:calc(var(--bz-safe-b) + 82px)}
#sprint{left:calc(var(--bz-safe-l) + 176px);bottom:calc(var(--bz-safe-b) + 28px)}
#vw{left:calc(var(--bz-safe-l) + 176px);bottom:calc(var(--bz-safe-b) + 88px)}
#lnl{left:calc(var(--bz-safe-l) + 236px);bottom:calc(var(--bz-safe-b) + 28px)}
#lnr{left:calc(var(--bz-safe-l) + 294px);bottom:calc(var(--bz-safe-b) + 28px)}
#rev{left:calc(var(--bz-safe-l) + 236px);bottom:calc(var(--bz-safe-b) + 88px)}
#pjump,#pchute{min-width:130px;width:130px;height:48px;border-radius:12px;left:50%;bottom:calc(var(--bz-safe-b) + 24px);transform:translateX(-50%)}
#bzSquadOrders{top:calc(var(--bz-safe-t) + 70px);right:calc(var(--bz-safe-r) + 12px);gap:7px;padding:7px;border-radius:15px;background:var(--bz-glass);border:1px solid #75c8ed55;box-shadow:0 8px 24px #0008}
#bzSquadOrders button{min-width:64px;min-height:42px;border-radius:10px;font-size:10px;letter-spacing:.04em}
#top{top:calc(var(--bz-safe-t) + 8px);padding:7px 13px;border:1px solid #ffffff28;background:#07111bd9;box-shadow:0 4px 16px #0006;font-weight:800;letter-spacing:.035em}
#mm{top:calc(var(--bz-safe-t) + 10px);left:calc(var(--bz-safe-l) + 10px);width:112px;height:112px;border-color:#d8efff9c;box-shadow:0 5px 18px #0008}
#hp{bottom:calc(var(--bz-safe-b) + 8px);width:min(230px,34vw);padding:5px 9px;border:1px solid #ffffff24;border-radius:12px;background:#07111bbf;box-shadow:0 4px 14px #0006}
#wp{bottom:calc(var(--bz-safe-b) + 8px);left:50%;transform:translateX(-50%);padding:5px 8px;border:1px solid #ffffff25;border-radius:12px;background:#07111bc9;box-shadow:0 5px 18px #0007}
#msg{top:calc(var(--bz-safe-t) + 126px);padding:6px 12px;border:1px solid #ffffff22;border-radius:10px;background:#07111bd9;font-weight:800;text-align:center}
#lobby{background:radial-gradient(ellipse at 50% 32%,#426e89 0%,#1a3549 42%,#081522 100%);overflow:hidden}
#lb-top{padding:10px 12px;border:1px solid #ffffff25;border-radius:14px;background:#07111bc9;backdrop-filter:blur(12px);font-weight:700}
.card{padding:8px 12px;border:1px solid #ffffff22;border-left:3px solid var(--bz-gold);border-radius:10px;background:linear-gradient(110deg,#07111bdc,#13283ad1);box-shadow:0 4px 12px #0005}
#maps{width:min(210px,28vw);gap:8px;max-height:calc(100% - 150px);padding:3px}
.mc{padding:9px 11px;border:1px solid #ffffff28;border-radius:11px;background:#07111bd9;box-shadow:0 4px 12px #0005}
.mc.on{border-color:var(--bz-cyan);box-shadow:0 0 0 2px #53d9ff30,0 5px 15px #0007}
#go2{padding:13px 46px;border:1px solid #fff5;border-radius:13px;background:linear-gradient(145deg,#ffe77a,#e9a91f);box-shadow:0 7px 22px #0008;color:#17202a;font-size:22px;letter-spacing:.08em}
#char{filter:drop-shadow(0 12px 18px #0009)}
#errb{max-height:22vh;overflow:auto;left:8px;right:8px;bottom:calc(var(--bz-safe-b) + 6px);width:auto;white-space:pre-wrap;overflow-wrap:anywhere;border-radius:10px;font:11px/1.35 ui-monospace,monospace}
@media (orientation:portrait){#bzSquadOrders{top:calc(var(--bz-safe-t) + 8px);right:8px;transform:scale(.86);transform-origin:top right}#mm{width:88px;height:88px}#maps{width:min(180px,42vw)}#fire{width:78px;height:78px}#scope{bottom:calc(var(--bz-safe-b) + 204px)}#prone{right:calc(var(--bz-safe-r) + 20px);bottom:calc(var(--bz-safe-b) + 182px)}#crouch{right:calc(var(--bz-safe-r) + 20px);bottom:calc(var(--bz-safe-b) + 122px)}#jump{right:calc(var(--bz-safe-r) + 20px);bottom:calc(var(--bz-safe-b) + 62px)}#swap{right:calc(var(--bz-safe-r) + 82px);bottom:calc(var(--bz-safe-b) + 22px)}#thr{right:calc(var(--bz-safe-r) + 144px);bottom:calc(var(--bz-safe-b) + 22px)}#gsw{right:calc(var(--bz-safe-r) + 144px);bottom:calc(var(--bz-safe-b) + 82px)}#rel{right:calc(var(--bz-safe-r) + 82px);bottom:calc(var(--bz-safe-b) + 82px)}#sprint{left:calc(var(--bz-safe-l) + 154px);bottom:calc(var(--bz-safe-b) + 26px)}#vw{left:calc(var(--bz-safe-l) + 154px);bottom:calc(var(--bz-safe-b) + 86px)}#lnl,#lnr{display:none}}
@media (max-height:420px) and (orientation:landscape){#joy{width:116px;height:116px}#knob{left:calc(50% - 19px);top:calc(50% - 19px);width:38px;height:38px}#scope{bottom:calc(var(--bz-safe-b) + 176px)}#jump,#crouch,#prone{bottom:calc(var(--bz-safe-b) + 104px)}#sprint,#vw,#lnl,#lnr,#rev{transform:scale(.9);transform-origin:bottom left}#fire{width:76px;height:76px}}
@media(prefers-reduced-motion:no-preference){.b{transition:transform .08s ease,border-color .12s ease,background .12s ease}}
'''
css_path = html.parent / "css" / "v6-critical-gameplay-polish.css"
css_path.parent.mkdir(parents=True, exist_ok=True)
css_path.write_text(css, encoding="utf-8")
link = '<link rel="stylesheet" href="./css/v6-critical-gameplay-polish.css">\n'
if 'v6-critical-gameplay-polish.css' not in s:
    s = once(s, "</head>", link + "</head>", "critical gameplay stylesheet link")
if marker not in s:
    s = s.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
if css_marker not in s:
    s = s.replace("</html>", "<!-- " + css_marker + " -->\n</html>", 1)
html.write_text(s, encoding="utf-8")
print("BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_APPLIED", html, css_path)


# BATTLEZONE_V6_FINAL_GAMEPLAY_VISUAL_OVERHAUL_V3
v3_marker = "BATTLEZONE_V6_FINAL_GAMEPLAY_VISUAL_OVERHAUL_V3"
v3_css_marker = "BATTLEZONE_V6_FINAL_UI_OVERHAUL_V3"
v3_html = html.read_text(encoding="utf-8")

def v3_replace(source, old, new, label):
    if new in source:
        return source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one exact source anchor, found {count}")
    return source.replace(old, new, 1)

if v3_marker not in v3_html:
    # Commands are stateful orders, not merely button labels.
    v3_html = v3_replace(
        v3_html,
        "root.querySelectorAll('[data-bz-order]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bzOrder===order)));};",
        "root.querySelectorAll('[data-bz-order]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bzOrder===order)));root.dataset.order=order;root.setAttribute('aria-label','Squad combat orders: '+order);window.dispatchEvent(new CustomEvent('bz:squad-order',{detail:{order}}));};",
        "squad order state publication",
    )
    v3_html = v3_replace(
        v3_html,
        "window.BZSquadOrders=Object.freeze({get:()=>order,getFocusTarget:focusTarget});",
        "window.BZSquadOrders=Object.freeze({get:()=>order,set:setOrder,getFocusTarget:focusTarget});",
        "public squad order API",
    )
    v3_html = v3_replace(
        v3_html,
        "const role=(window.BZSquadOrders?.get()==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3])),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;",
        "const bzOrder=window.BZSquadOrders?.get()||'regroup',role=(bzOrder==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3])),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;",
        "squad order state read",
    )
    v3_html = v3_replace(
        v3_html,
        "if(window.BZSquadOrders?.get()==='regroup'&&Math.hypot(px-a.position.x,pz-a.position.z)>12)en=null;",
        "if(bzOrder==='regroup')en=null;else if(bzOrder==='hold'&&en&&Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z)>28)en=null;",
        "regroup and hold target policy",
    )
    v3_html = v3_replace(
        v3_html,
        "else{u.cd=.22;u.squadThink=0}}",
        "else{u.cd=.22;u.squadThink=0}}if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0;}",
        "hold order movement lock",
    )

    # Airborne actors cannot be acquired as combat targets; no pre-landing bot fire.
    v3_html = v3_replace(
        v3_html,
        "if(target.p)return !!P.alive&&!P.air;",
        "if(target.p)return !!P.alive&&!P.air&&P.y<=(P.gh||1.6)+.22&&Math.abs(P.vy||0)<=.75;",
        "grounded player target validation",
    )
    v3_html = v3_replace(
        v3_html,
        "if(!actor||!u||!u.alive||!actor.position)return false;",
        "if(!actor||!u||!u.alive||u.airDrop||u.falling||u.chute||!actor.position)return false;",
        "airborne actor target validation",
    )
    v3_html = v3_replace(
        v3_html,
        "if(!Number.isFinite(x)||!Number.isFinite(z))return;",
        "if(!Number.isFinite(x)||!Number.isFinite(z))return;if(candidate.o&&candidate.o.userData&&(candidate.o.userData.airDrop||candidate.o.userData.falling||candidate.o.userData.chute))return;",
        "airborne candidate rejection",
    )
    v3_html = v3_replace(
        v3_html,
        "if(actor===bot||!actor||!actor.userData||!actor.userData.alive)return;",
        "if(actor===bot||!actor||!actor.userData||!actor.userData.alive||actor.userData.airDrop||actor.userData.falling||actor.userData.chute)return;",
        "airborne actor scan rejection",
    )
    v3_html = v3_replace(
        v3_html,
        "if(!u.alive||u.airDrop||u.falling)return;",
        "if(!u.alive||u.airDrop||u.falling||u.chute)return;",
        "airborne shooter rejection",
    )
    v3_html = v3_replace(
        v3_html,
        "function shoot(){if(P.cd>0||P.rl>0||P.air||P.down)return;",
        "function shoot(){if(P.cd>0||P.rl>0||P.air||P.down||P.y>(P.gh||1.6)+.22||Math.abs(P.vy||0)>.75)return;",
        "grounded player firing gate",
    )
    v3_html = v3_replace(
        v3_html,
        "window.shotSfx=function(){if(!SND_ON)return;",
        "window.shotSfx=function(){if(!SND_ON||P.air||P.y>(P.gh||1.6)+.22||Math.abs(P.vy||0)>.75)return;",
        "grounded player weapon audio gate",
    )

    # Use the existing PBR texture library across every biome and all high-quality world props.
    v3_html = v3_replace(
        v3_html,
        "const gr=new THREE.Mesh(new THREE.BufferGeometry(),BZMaterial('grass',18,.98));",
        "const bzGroundTexture=MI===1||MI===4?'sand':MI===2?'concrete':MI===5||MI===8?'weathered_rock':MI===6?'asphalt':MI===7||MI===9?'dry_dirt':'forest_floor';const gr=new THREE.Mesh(new THREE.BufferGeometry(),BZMaterial(bzGroundTexture,18,.98));",
        "map-specific PBR ground material",
    )
    v3_html = v3_replace(
        v3_html,
        "const M=c=>new THREE.MeshLambertMaterial({color:c});",
        "const bzColorMaterialCache={};const M=c=>{const k=String(c);if(!bzColorMaterialCache[k])bzColorMaterialCache[k]=LQ?new THREE.MeshLambertMaterial({color:c}):new THREE.MeshStandardMaterial({color:c,roughness:.82,metalness:.04});return bzColorMaterialCache[k]};",
        "PBR world material factory",
    )
    v3_html = v3_replace(
        v3_html,
        "t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat,repeat);t.anisotropy=1;",
        "t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat,repeat);t.anisotropy=LQ?1:Math.min(8,R.capabilities.getMaxAnisotropy());",
        "texture anisotropic filtering",
    )
    v3_html = v3_replace(
        v3_html,
        "const BARK=new THREE.MeshLambertMaterial({map:barkT});",
        "const BARK=new THREE.MeshStandardMaterial({map:barkT,roughness:.92,metalness:0});",
        "PBR tree bark material",
    )
    v3_html = v3_replace(
        v3_html,
        "const wall=new THREE.MeshLambertMaterial({color:c,map:t}),roof=new THREE.MeshLambertMaterial({color:new THREE.Color(c).multiplyScalar(.55)});",
        "const wall=new THREE.MeshStandardMaterial({color:c,map:t,roughness:.88,metalness:.02}),roof=new THREE.MeshStandardMaterial({color:new THREE.Color(c).multiplyScalar(.55),roughness:.86,metalness:.04});",
        "PBR building facade and roof",
    )
    v3_html = v3_replace(v3_html, "R.toneMappingExposure=1.16;", "R.toneMappingExposure=1.2;", "visual exposure refinement")
    v3_html = v3_replace(v3_html, "new THREE.HemisphereLight(0xffffff,0x354c39,1.08)", "new THREE.HemisphereLight(0xffffff,0x354c39,1.12)", "ambient lighting refinement")
    v3_html = v3_replace(v3_html, "new THREE.DirectionalLight(0xffffff,.72*(MAP.nt?.25:1))", "new THREE.DirectionalLight(0xffffff,.78*(MAP.nt?.25:1))", "sunlight refinement")

    v3_html = v3_html.replace("</html>", "<!-- " + v3_marker + " -->\n</html>", 1)
    html.write_text(v3_html, encoding="utf-8")

# Layer original tactical armor onto the shipped rigged CC0/KayKit operators.
models_paths = list(root.rglob("app/src/main/assets/www/js/models.js"))
if len(models_paths) != 1:
    raise SystemExit(f"Expected exactly one character model loader, found {len(models_paths)}")
models_path = models_paths[0]
models_source = models_path.read_text(encoding="utf-8")
gear_marker = "BATTLEZONE_V6_OPERATOR_ARMOR_REDESIGN_V3"
if gear_marker not in models_source:
    gear_helper = r"""
/* BATTLEZONE_V6_OPERATOR_ARMOR_REDIGN_V3 */
const bzGearGeometry={
 helmet:new THREE.SphereGeometry(.17,12,8,0,Math.PI*2,0,Math.PI*.62),
 visor:new THREE.BoxGeometry(.25,.055,.045),
 chest:new THREE.BoxGeometry(.42,.34,.13),
 pouch:new THREE.BoxGeometry(.09,.09,.07),
 pack:new THREE.BoxGeometry(.28,.34,.14),
 shoulder:new THREE.SphereGeometry(.12,10,8),
 forearm:new THREE.BoxGeometry(.12,.22,.08),
 knee:new THREE.BoxGeometry(.15,.13,.08),
 boot:new THREE.BoxGeometry(.16,.12,.25),
 belt:new THREE.BoxGeometry(.43,.075,.16),
 radio:new THREE.BoxGeometry(.07,.16,.06)
};
const bzGearMaterialCache={};
function bzGearMaterials(key){
 const id=String(key||'Recruit');if(bzGearMaterialCache[id])return bzGearMaterialCache[id];
 const tint=new THREE.Color(OPERATOR_COLORS[id]||0x72856f).multiplyScalar(.66);
 return bzGearMaterialCache[id]={
  armor:new THREE.MeshStandardMaterial({color:0x293b38,roughness:.76,metalness:.16}),
  plate:new THREE.MeshStandardMaterial({color:0x46564d,roughness:.68,metalness:.2}),
  dark:new THREE.MeshStandardMaterial({color:0x121b1d,roughness:.84,metalness:.08}),
  accent:new THREE.MeshStandardMaterial({color:tint,roughness:.58,metalness:.14}),
  visor:new THREE.MeshStandardMaterial({color:0x101d29,roughness:.2,metalness:.72})
 };
}
function bzAttachOperatorGear(model,bones,key){
 if(!model||model.userData.bzOperatorGear)return;
 model.userData.bzOperatorGear=true;
 model.updateMatrixWorld(true);
 const bounds=new THREE.Box3().setFromObject(model),size=new THREE.Vector3();bounds.getSize(size);
 const k=Math.max(.78,Math.min(1.12,(size.y||1.8)/1.8)),cx=(bounds.min.x+bounds.max.x)*.5,cz=(bounds.min.z+bounds.max.z)*.5,m=bzGearMaterials(key);
 const anchor=(bone,x,y,z)=>{if(bone)return bone;const g=new THREE.Group();g.position.set(x,y,z);model.add(g);return g};
 const add=(parent,geo,mat,x,y,z,sx=1,sy=1,sz=1)=>{const o=new THREE.Mesh(geo,mat);o.position.set(x*k,y*k,z*k);o.scale.set(sx,sy,sz);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o};
 const head=anchor(bones.head,cx,bounds.min.y+size.y*.91,cz);
 add(head,bzGearGeometry.helmet,m.armor,0,.045,0,1,1,1);
 add(head,bzGearGeometry.visor,m.visor,0,.015,-.145,1,1,1);
 add(head,bzGearGeometry.visor,m.accent,0,.105,-.025,1.05,.35,.8);
 const torso=anchor(bones.spine,cx,bounds.min.y+size.y*.64,cz);
 add(torso,bzGearGeometry.chest,m.plate,0,0,-.085,1,1,1);
 add(torso,bzGearGeometry.belt,m.dark,0,-.205,-.01,1,1,1);
 add(torso,bzGearGeometry.pouch,m.armor,-.125,-.13,-.165,1,1,1);
 add(torso,bzGearGeometry.pouch,m.armor,0,-.13,-.165,1,1,1);
 add(torso,bzGearGeometry.pouch,m.armor,.125,-.13,-.165,1,1,1);
 add(torso,bzGearGeometry.pack,m.dark,0,.015,.145,1,1,1);
 add(torso,bzGearGeometry.radio,m.accent,-.17,.075,.13,1,1,1);
 const rightArm=anchor(bones.rightArm,cx+size.x*.31,bounds.min.y+size.y*.7,cz);
 const leftArm=anchor(bones.leftArm,cx-size.x*.31,bounds.min.y+size.y*.7,cz);
 add(rightArm,bzGearGeometry.shoulder,m.plate,0,.015,0,1.08,.78,1.1);
 add(leftArm,bzGearGeometry.shoulder,m.plate,0,.015,0,1.08,.78,1.1);
 const rightFore=anchor(bones.rightForeArm,cx+size.x*.36,bounds.min.y+size.y*.55,cz);
 const leftFore=anchor(bones.leftForeArm,cx-size.x*.36,bounds.min.y+size.y*.55,cz);
 add(rightFore,bzGearGeometry.forearm,m.armor,0,-.055,-.025,1,1,1);
 add(leftFore,bzGearGeometry.forearm,m.armor,0,-.055,-.025,1,1,1);
 const rightLeg=anchor(bones.rightLeg,cx+size.x*.13,bounds.min.y+size.y*.31,cz);
 const leftLeg=anchor(bones.leftLeg,cx-size.x*.13,bounds.min.y+size.y*.31,cz);
 add(rightLeg,bzGearGeometry.knee,m.plate,0,-.12,-.055,1,1,1);
 add(leftLeg,bzGearGeometry.knee,m.plate,0,-.12,-.055,1,1,1);
 const rightFoot=anchor(bones.rightFoot,cx+size.x*.13,bounds.min.y+.08,cz);
 const leftFoot=anchor(bones.leftFoot,cx-size.x*.13,bounds.min.y+.08,cz);
 add(rightFoot,bzGearGeometry.boot,m.dark,0,-.025,-.035,1,1,1);
 add(leftFoot,bzGearGeometry.boot,m.dark,0,-.025,-.035,1,1,1);
}
"""
    register_anchor = "function register(obj,model,opt){"
    if models_source.count(register_anchor) != 1:
        raise SystemExit("Character gear insertion anchor is not unique")
    models_source = models_source.replace(register_anchor, gear_helper + "\n" + register_anchor, 1)
    old_bones = "const bones={rightHand:findBone(model,['righthand','handr','handslotright']),rightArm:findBone(model,['rightarm','upperarmr','armright']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml','armleft']),leftForeArm:findBone(model,['leftforearm','forearml']),spine:findBone(model,['spine','spine1','chest','body'])};"
    new_bones = "const bones={rightHand:findBone(model,['righthand','handr','handslotright']),head:findBone(model,['head','headtop','headend']),rightArm:findBone(model,['rightarm','upperarmr','armright']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml','armleft']),leftForeArm:findBone(model,['leftforearm','forearml']),rightLeg:findBone(model,['rightupleg','rightthigh','rightleg','thighr']),leftLeg:findBone(model,['leftupleg','leftthigh','leftleg','thighl']),rightFoot:findBone(model,['rightfoot','footr']),leftFoot:findBone(model,['leftfoot','footl']),spine:findBone(model,['spine','spine1','chest','body'])};bzAttachOperatorGear(model,bones,opt.skinKey||'Recruit');"
    models_source = v3_replace(models_source, old_bones, new_bones, "operator gear bone integration")
    models_source = v3_replace(models_source, "register(group,model,Object.assign({},opt,{template}));group.userData.bzDressed=true;", "register(group,model,Object.assign({},opt,{template,skinKey}));group.userData.bzDressed=true;", "operator identity propagation")
    models_source = models_source.replace("/* Rigged character models", "/* " + gear_marker + " */\n/* Rigged character models", 1)
    models_path.write_text(models_source, encoding="utf-8")

# Replace the overlapping absolute button positions with non-overlapping control clusters,
# and make the lobby a balanced three-column command layout.
css_path = html.parent / "css" / "v6-critical-gameplay-polish.css"
if not css_path.is_file():
    raise SystemExit("Critical gameplay stylesheet is missing before V3 UI integration")
css_source = css_path.read_text(encoding="utf-8")
if v3_css_marker not in css_source:
    css_source += r"""
/* BATTLEZONE_V6_FINAL_UI_OVERHAUL_V3 */
#bzSquadOrders{top:calc(var(--bz-safe-t) + 64px)!important;right:calc(var(--bz-safe-r) + 14px)!important;gap:7px!important;padding:8px!important}
#bzSquadOrders button{min-width:62px!important;min-height:42px!important;border-radius:10px!important}
#bzSquadOrders[data-order="regroup"]{border-color:#74d8a8!important}
#bzSquadOrders[data-order="focus"]{border-color:#ff6b64!important}
#bzSquadOrders[data-order="flank"]{border-color:#f1c66b!important}
#bzSquadOrders[data-order="hold"]{border-color:#82b7ff!important}
#joy{position:fixed!important;left:calc(var(--bz-safe-l) + 14px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 14px)!important;width:128px!important;height:128px!important}
#knob{width:42px!important;height:42px!important;left:calc(50% - 21px)!important;top:calc(50% - 21px)!important}
#fire{position:fixed!important;right:calc(var(--bz-safe-r) + 16px)!important;bottom:calc(var(--bz-safe-b) + 16px)!important;width:82px!important;height:82px!important;z-index:91!important}
#fire2{display:none!important}
#rel{right:calc(var(--bz-safe-r) + 106px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important}
#swap{right:calc(var(--bz-safe-r) + 106px)!important;bottom:calc(var(--bz-safe-b) + 80px)!important}
#thr{right:calc(var(--bz-safe-r) + 168px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important}
#gsw{right:calc(var(--bz-safe-r) + 168px)!important;bottom:calc(var(--bz-safe-b) + 80px)!important}
#jump{right:calc(var(--bz-safe-r) + 16px)!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
#crouch{right:calc(var(--bz-safe-r) + 78px)!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
#prone{right:calc(var(--bz-safe-r) + 140px)!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
#scope{right:calc(var(--bz-safe-r) + 16px)!important;bottom:calc(var(--bz-safe-b) + 172px)!important}
#sprint{left:calc(var(--bz-safe-l) + 154px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 20px)!important}
#vw{left:calc(var(--bz-safe-l) + 154px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 80px)!important}
#lnl{left:calc(var(--bz-safe-l) + 214px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 20px)!important}
#lnr{left:calc(var(--bz-safe-l) + 274px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 20px)!important}
#rev{left:calc(var(--bz-safe-l) + 214px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 80px)!important}
#drive{left:calc(var(--bz-safe-l) + 274px)!important;right:auto!important;bottom:calc(var(--bz-safe-b) + 80px)!important}
#pjump,#pchute{left:50%!important;right:auto!important;top:52%!important;bottom:auto!important;transform:translate(-50%,-50%)!important;min-width:150px!important;width:min(220px,34vw)!important;z-index:95!important}
.b{touch-action:none!important;pointer-events:auto!important;user-select:none!important;-webkit-user-select:none!important}
#lobby{position:fixed!important;inset:0!important;width:100vw!important;height:100dvh!important;overflow:hidden!important;background:radial-gradient(ellipse at 50% 38%,#365f78 0%,#172f43 46%,#07131f 100%)!important}
#lb-top{left:max(12px,env(safe-area-inset-left,0px) + 12px)!important;right:max(12px,env(safe-area-inset-right,0px) + 12px)!important;top:max(8px,env(safe-area-inset-top,0px) + 8px)!important;min-height:46px!important;padding:8px 12px!important;border:1px solid #a8d9f333!important;border-radius:14px!important;background:#071522d9!important;backdrop-filter:blur(14px)!important}
#lb-l{left:max(12px,env(safe-area-inset-left,0px) + 12px)!important;right:auto!important;top:clamp(112px,16vh,150px)!important;bottom:clamp(70px,11vh,94px)!important;width:clamp(190px,20vw,278px)!important;max-width:23vw!important;min-height:0!important;overflow:hidden!important;border:1px solid #8fb8d344!important;border-radius:16px!important;background:linear-gradient(155deg,#0b1a28eF,#07111beF)!important;box-shadow:0 12px 32px #0007!important;backdrop-filter:blur(12px)!important}
#lb-l #setc{overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;padding:8px!important}
#lb-l .card{min-height:42px!important;border:1px solid #8fb8d333!important;border-left:3px solid #70c6e8!important;border-radius:10px!important;background:#14283ae8!important}
#maps{left:auto!important;right:max(12px,env(safe-area-inset-right,0px) + 12px)!important;top:clamp(112px,16vh,150px)!important;bottom:clamp(70px,11vh,94px)!important;width:clamp(194px,21vw,286px)!important;max-width:24vw!important;min-height:0!important;overflow-x:hidden!important;overflow-y:auto!important;overscroll-behavior:contain!important;padding:9px!important;border:1px solid #8fb8d344!important;border-radius:16px!important;background:linear-gradient(155deg,#0b1a28eF,#07111beF)!important;box-shadow:0 12px 32px #0007!important;backdrop-filter:blur(12px)!important}
#maps .mc{width:100%!important;min-height:50px!important;border:1px solid #8fb8d333!important;border-radius:11px!important;background:#14283ae8!important}
#maps .mc.on{border-color:#6fe0ff!important;box-shadow:0 0 0 2px #6fe0ff33!important}
#char{left:50%!important;top:55%!important;right:auto!important;bottom:auto!important;width:clamp(150px,17vw,236px)!important;height:clamp(210px,43vh,330px)!important;max-width:19vw!important;transform:translate(-50%,-50%)!important;filter:drop-shadow(0 18px 24px #000b)!important;z-index:10!important}
#bz-v6-hero{left:50%!important;right:auto!important;top:clamp(58px,8vh,86px)!important;transform:translateX(-50%)!important;width:min(36vw,500px)!important;max-width:calc(100vw - 48vw)!important;padding:8px 16px!important;border:1px solid #8bdcff55!important;border-radius:14px!important;background:linear-gradient(110deg,#0a1a29ed,#17334be8)!important;box-shadow:0 10px 30px #0007!important}
#go2{left:max(12px,env(safe-area-inset-left,0px) + 12px)!important;right:auto!important;bottom:max(12px,env(safe-area-inset-bottom,0px) + 12px)!important;width:clamp(190px,20vw,278px)!important;max-width:23vw!important;min-height:50px!important;border:1px solid #fff6!important;border-radius:13px!important;background:linear-gradient(145deg,#ffe58b,#e5a51b)!important;box-shadow:0 8px 24px #0009!important;color:#15212a!important}
#lb-nav{right:max(12px,env(safe-area-inset-right,0px) + 12px)!important;bottom:max(12px,env(safe-area-inset-bottom,0px) + 12px)!important;max-width:48vw!important;gap:6px!important}
#lb-nav b{min-height:48px!important;border:1px solid #a8d9f333!important;border-radius:10px!important;background:#102337eF!important}
#warroomBrief{left:50%!important;right:auto!important;bottom:clamp(66px,10vh,84px)!important;transform:translateX(-50%)!important;max-width:min(34vw,340px)!important;text-align:center!important}
@media(max-width:900px) and (orientation:landscape){
 #lb-l{width:22vw!important;max-width:22vw!important}
 #maps{width:22vw!important;max-width:22vw!important}
 #char{width:18vw!important;height:40vh!important}
 #lb-nav{max-width:44vw!important}
 #sprint{left:calc(var(--bz-safe-l) + 140px)!important}
 #vw{left:calc(var(--bz-safe-l) + 140px)!important}
 #lnl,#lnr,#rev,#drive{display:none!important}
}
@media(orientation:portrait){
 #lb-l{left:8px!important;top:15vh!important;bottom:20vh!important;width:40vw!important;max-width:40vw!important}
 #maps{right:8px!important;top:15vh!important;bottom:20vh!important;width:40vw!important;max-width:40vw!important}
 #char{top:57%!important;width:16vw!important;height:28vh!important;max-width:16vw!important}
 #bz-v6-hero{top:8vh!important;width:48vw!important;max-width:48vw!important}
 #go2{left:8px!important;bottom:8px!important;width:42vw!important;max-width:42vw!important}
 #lb-nav{right:8px!important;bottom:8px!important;max-width:46vw!important;overflow-x:auto!important}
 #warroomBrief{display:none!important}
 #joy{left:10px!important;bottom:10px!important;width:108px!important;height:108px!important}
 #knob{width:38px!important;height:38px!important;left:calc(50% - 19px)!important;top:calc(50% - 19px)!important}
 #sprint{left:10px!important;bottom:126px!important}
 #vw{left:10px!important;bottom:186px!important}
 #rev{left:70px!important;bottom:126px!important}
 #drive{left:70px!important;bottom:186px!important}
 #lnl,#lnr{display:none!important}
 #fire{right:10px!important;bottom:10px!important;width:52px!important;height:52px!important}
 #rel{right:66px!important;bottom:10px!important}
 #swap{right:122px!important;bottom:10px!important}
 #scope{right:10px!important;bottom:66px!important}
 #thr{right:66px!important;bottom:66px!important}
 #gsw{right:122px!important;bottom:66px!important}
 #jump{right:10px!important;bottom:122px!important}
 #crouch{right:66px!important;bottom:122px!important}
 #prone{right:122px!important;bottom:122px!important}
 #pjump,#pchute{top:52%!important}
}
@media(max-height:440px) and (orientation:landscape){
 #joy{width:108px!important;height:108px!important}
 #fire{width:72px!important;height:72px!important}
 #jump,#crouch,#prone{bottom:calc(var(--bz-safe-b) + 98px)!important}
 #scope{bottom:calc(var(--bz-safe-b) + 154px)!important}
 #bzSquadOrders button{min-width:54px!important;min-height:36px!important}
}
"""
    css_path.write_text(css_source, encoding="utf-8")

print("BATTLEZONE_V6_FINAL_GAMEPLAY_VISUAL_OVERHAUL_APPLIED", html, models_path, css_path)
