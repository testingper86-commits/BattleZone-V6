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
marker = "BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_V1"
css_marker = "BATTLEZONE_V6_CRITICAL_CONTROLS_GRAPHICS_V1"
if marker in s and css_marker in s:
    print("BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_ALREADY_APPLIED")
    raise SystemExit(0)

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

# The final icon pass runs after the initial HUD construction. Preserve the IDs hudUpdate writes.
old = "Object.entries(bzControlIcons).forEach(([id,v])=>{const e=$(id);if(e)e.innerHTML='<span class=\"bz-control-symbol\">'+v[0]+'</span><small>'+v[1]+'</small>'});"
new = "Object.entries(bzControlIcons).forEach(([id,v])=>{const e=$(id);if(e){const valueId=id==='thr'?' id=\"thrn\"':id==='gsw'?' id=\"gswn\"':'';e.innerHTML='<span class=\"bz-control-symbol\">'+v[0]+'</span><small'+valueId+'>'+v[1]+'</small>'}});"
if old in s: s = once(s, old, new, "preserve grenade HUD nodes")
elif "const valueId=id==='thr'?' id=\"thrn\"'" not in s:
    raise SystemExit("Final control icon renderer has an unknown implementation")

# Ship a consistent landscape-first tactical HUD with separated touch targets and responsive safe areas.
css = r'''/* BATTLEZONE_V6_CRITICAL_CONTROLS_GRAPHICS_V1 */
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
s = s.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
s = s.replace("</html>", "<!-- " + css_marker + " -->\n</html>", 1)
html.write_text(s, encoding="utf-8")
print("BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_APPLIED", html, css_path)
