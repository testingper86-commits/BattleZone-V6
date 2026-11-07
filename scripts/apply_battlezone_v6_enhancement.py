#!/usr/bin/env python3
"""Apply the BattleZone V6 command-deck redesign and targeted runtime fixes."""
from pathlib import Path
import shutil
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCRIPT_DIR = Path(__file__).resolve().parent
MARKER = "BATTLEZONE_V6_COMMAND_DECK_V1"

html_files = list(ROOT.rglob("app/src/main/assets/www/index.html"))
if len(html_files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(html_files)}")
html_path = html_files[0]
s = html_path.read_text(encoding="utf-8")
if MARKER in s:
    print("BATTLEZONE_V6_COMMAND_DECK_ALREADY_APPLIED")
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source anchor, found {count}")
    s = s.replace(old, new, 1)

# Keep the live operator preview, but cap its rendering work to 20 fps and
# release its independent WebGL context when the match begins.
replace_once(
    "requestAnimationFrame(function ll(n){if(started){lr.dispose();return}const t=n/1000;animSc(sc,0,.016,t);sc.root.rotation.y=Math.sin(t*.5)*.7+(window.lobOff||0);lr.render(ls,lc);requestAnimationFrame(ll)})",
    "let lastLobbyRender=0;requestAnimationFrame(function ll(n){if(started){lr.dispose();lr.forceContextLoss();cv.remove();return}if(!document.hidden&&n-lastLobbyRender>=50){const dt=lastLobbyRender?Math.min(.05,(n-lastLobbyRender)/1000):.016;lastLobbyRender=n;const t=n/1000;animSc(sc,0,dt,t);sc.root.rotation.y=Math.sin(t*.5)*.7+(window.lobOff||0);lr.render(ls,lc)}requestAnimationFrame(ll)})",
    "lobby preview frame cap and WebGL context release",
)

# Squad target selection is sampled at 6.25 Hz rather than rescanning every
# enemy on every render frame. The cached target is invalidated immediately
# when it dies or leaves the ally's effective acquisition radius.
replace_once(
    "let en=null,bd=96,best=Infinity;bots.forEach(o=>{const v=o.userData;if(!v.alive||v.ally||v.airDrop||v.falling)return;const d=Math.hypot(o.position.x-a.position.x,o.position.z-a.position.z);if(d>96)return;const threat=Math.hypot(o.position.x-px,o.position.z-pz),score=d+Math.min(30,threat)*.18;if(score<best){best=score;bd=d;en=o}});",
    "u.squadScanT=(u.squadScanT||0)-dt;let en=u.squadTargetObj||null;if(u.squadScanT<=0||(en&&(!en.userData.alive||Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z)>96))){en=null;let best=Infinity;bots.forEach(o=>{const v=o.userData;if(!v.alive||v.ally||v.airDrop||v.falling)return;const d=Math.hypot(o.position.x-a.position.x,o.position.z-a.position.z);if(d>96)return;const threat=Math.hypot(o.position.x-px,o.position.z-pz),score=role==='support'?d+Math.min(40,threat)*.3:role==='flank'?d-Math.min(25,threat)*.12:d+Math.min(30,threat)*.18;if(score<best){best=score;en=o}});u.squadTargetObj=en;u.squadScanT=.16}let bd=en?Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z):96;",
    "throttled squad target acquisition",
)

# LOS is needed only when a squad member is ready to fire. Moving the raycast
# into the weapon cooldown avoids allocating a Raycaster and vectors every frame.
replace_once(
    "if(P.down){gx=px;gz=pz;speed=7.2}else if(en){const ex=en.position.x-a.position.x,ez=en.position.z-a.position.z,ang=Math.atan2(ez,ex),clear=bd<88&&hasClearShot(a.position.x,a.position.y+1.15,a.position.z,en.position.x,en.position.y+1.1,en.position.z);a.rotation.y=Math.atan2(ex,ez);u.squadTarget=en.userData.nid||null;",
    "if(P.down){gx=px;gz=pz;speed=7.2}else if(en){const ex=en.position.x-a.position.x,ez=en.position.z-a.position.z,ang=Math.atan2(ez,ex);a.rotation.y=Math.atan2(ex,ez);u.squadTarget=en.userData.nid||null;",
    "defer squad line-of-sight raycast",
)
replace_once(
    "if(clear&&u.cd<=0){u.cd=rnd(.42,.68)*([.88,1,1.12][DF]||1);if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}const hitDamage=(role==='support'?13:role==='flank'?17:19)+rnd(0,5);en.userData.hp-=hitDamage;if(en.userData.hp<=0)killBot(en,false)}else if(!clear&&u.cd<=0){u.cd=.22;u.squadThink=0}",
    "if(u.cd<=0){const clear=bd<88&&hasClearShot(a.position.x,a.position.y+1.15,a.position.z,en.position.x,en.position.y+1.1,en.position.z);if(clear){u.cd=rnd(.42,.68)*([.88,1,1.12][DF]||1);if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}const hitDamage=(role==='support'?13:role==='flank'?17:19)+rnd(0,5);en.userData.hp-=hitDamage;if(en.userData.hp<=0){u.squadTargetObj=null;killBot(en,false)}}else{u.cd=.22;u.squadThink=0}}",
    "cooldown-gated squad firing and LOS",
)

# Add a clear command-deck information hierarchy without replacing any
# existing gameplay control IDs or their handlers.
replace_once(
    '<div id="logo">BATTLE <b>ZONE</b></div>',
    '<div id="logo">BATTLE <b>ZONE</b></div>\n<div id="bz-v6-hero" aria-label="Battlefield command status"><span class="bz-v6-eyebrow">OFFLINE OPERATIONS / V6</span><b id="bz-v6-hero-title">READY FOR DEPLOYMENT</b><span id="bz-v6-hero-meta">BATTLE ROYALE · SQUAD · NORMAL AI</span><span class="bz-v6-local"><i></i> LOCAL COMMAND SYSTEM</span></div>',
    "V6 command hero markup",
)

css_source = SCRIPT_DIR / "v6-command-deck.css"
js_source = SCRIPT_DIR / "v6-command-deck.js"
if not css_source.is_file() or not js_source.is_file():
    raise SystemExit("Required V6 command-deck CSS/JS source files are missing")
css_target = html_path.parent / "css" / "v6-command-deck.css"
js_target = html_path.parent / "js" / "v6-command-deck.js"
css_target.parent.mkdir(parents=True, exist_ok=True)
js_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(css_source, css_target)
shutil.copyfile(js_source, js_target)

replace_once(
    "</head>",
    '<link rel="stylesheet" href="./css/v6-command-deck.css">\n</head>',
    "V6 command-deck stylesheet reference",
)
replace_once(
    '<script src="./js/warroom-command.js"></script>',
    '<script src="./js/warroom-command.js"></script>\n<script src="./js/v6-command-deck.js" defer></script>\n<!-- ' + MARKER + ' -->',
    "V6 command-deck behavior reference",
)
html_path.write_text(s, encoding="utf-8")
print("BATTLEZONE_V6_COMMAND_DECK_APPLIED", html_path)
