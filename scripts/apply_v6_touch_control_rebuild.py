#!/usr/bin/env python3
"""Rebuild BattleZone V6 touch HUD and repair parachute landing/camera lean."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
html = files[0]
s = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_TOUCH_CONTROL_REBUILD_V1"
css_name = "v6-touch-control-rebuild.css"
js_name = "v6-touch-control-rebuild.js"

def once(src, old, new, label):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one source anchor, found {n}")
    return src.replace(old, new, 1)

if marker not in s:
    old_land = "if(P.y<=1.6){P.air=0;P.y=1.6;P.vy=0;P.tp=true;P.lnT=1;msg('Landed! Find a weapon')}"
    new_land = ("const bzLandingGround=gS(P.x,P.z,P.y-1.6)+1.6;"
                "if(P.y<=bzLandingGround){P.air=0;P.y=bzLandingGround;P.gh=bzLandingGround;P.vy=0;"
                "P.dropVx=0;P.dropVz=0;P.tp=true;P.lnT=0;P.ln=0;P.prone=false;P.crouch=false;"
                "if(pm){pm.airPose=false;pm.parachutePose=false}msg('Landed! Find a weapon')}")
    s = once(s, old_land, new_land, "terrain-aware parachute touchdown and camera lean reset")

    old_cl = "let CL={};try{CL=JSON.parse(sg('bzc2')||'{}')}catch(e){}"
    new_cl = ("const BZ_CONTROL_LAYOUT_VERSION='3';let CL={};"
              "try{if(sg('bzControlLayoutVersion')===BZ_CONTROL_LAYOUT_VERSION){CL=JSON.parse(sg('bzc2')||'{}')||{}}"
              "else{ss('bzc2','{}');ss('bzControlLayoutVersion',BZ_CONTROL_LAYOUT_VERSION)}}catch(e){CL={}}")
    s = once(s, old_cl, new_cl, "versioned migration of obsolete overlapping touch positions")

    old_bind = ("const bind=(id,d,u)=>{const el=$(id);el.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();"
                "try{el.setPointerCapture(e.pointerId)}catch(x){}if(CE){el._dr=1;return}el.classList.add('on');d()});"
                "  el.addEventListener('pointermove',e=>{if(CE&&el._dr){CL[id]={x:(e.clientX-el.offsetWidth/2)/Math.max(1,innerWidth),y:(e.clientY-el.offsetHeight/2)/Math.max(1,innerHeight)};applyCL()}});"
                "  const up=e=>{el._dr=0;if(!el.classList.contains('on'))return;el.classList.remove('on');if(u)u()};"
                "el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);el.addEventListener('lostpointercapture',up)};")
    new_bind = ("const bind=(id,d,u)=>{const el=$(id),activePointers=new Set();"
                "el.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();try{el.setPointerCapture(e.pointerId)}catch(x){}"
                "if(CE){el._dr=1;return}const wasActive=activePointers.size>0;activePointers.add(e.pointerId);"
                "if(!wasActive){el.classList.add('on');d()}});"
                "el.addEventListener('pointermove',e=>{if(CE&&el._dr){CL[id]={x:(e.clientX-el.offsetWidth/2)/Math.max(1,innerWidth),y:(e.clientY-el.offsetHeight/2)/Math.max(1,innerHeight)};applyCL()}});"
                "const up=e=>{el._dr=0;if(!activePointers.delete(e.pointerId)||activePointers.size)return;"
                "el.classList.remove('on');if(u)u()};"
                "el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);el.addEventListener('lostpointercapture',up)};")
    s = once(s, old_bind, new_bind, "multi-pointer-safe action button input lifecycle")

    if s.count("</head>") != 1 or s.count("</body>") != 1:
        raise SystemExit("Expected one head and body closing tag")
    s = s.replace("</head>", f'<link rel="stylesheet" href="./css/{css_name}">\n</head>', 1)
    s = s.replace("</body>", f'<script src="./js/{js_name}"></script>\n<!-- {marker} -->\n</body>', 1)
else:
    if f"./css/{css_name}" not in s or f"./js/{js_name}" not in s:
        raise SystemExit("Touch rebuild marker exists without both linked assets")

css = r"""/* BATTLEZONE_V6_TOUCH_CONTROL_REBUILD_V1 */
:root{--bz-control-safe-l:env(safe-area-inset-left,0px);--bz-control-safe-r:env(safe-area-inset-right,0px);--bz-control-safe-t:env(safe-area-inset-top,0px);--bz-control-safe-b:env(safe-area-inset-bottom,0px);--bz-control-size:58px;--bz-control-gap:8px}
body:not(.bz-control-edit) .b,body:not(.bz-control-edit) #joy{position:fixed!important;z-index:90!important;touch-action:none!important;pointer-events:auto!important;user-select:none!important;-webkit-user-select:none!important;-webkit-touch-callout:none!important}
body:not(.bz-control-edit) .b{width:var(--bz-control-size)!important;height:var(--bz-control-size)!important;min-width:var(--bz-control-size)!important;min-height:var(--bz-control-size)!important;max-width:var(--bz-control-size)!important;max-height:var(--bz-control-size)!important;padding:5px!important;gap:3px!important;border:1px solid #a9c3d4a8!important;border-radius:15px!important;background:linear-gradient(150deg,#263e50f2 0%,#101e2bf2 68%,#0a131df5 100%)!important;box-shadow:0 7px 20px #0009,inset 0 1px 0 #ffffff30!important;color:#f1f7fb!important;font:800 9px/1.05 system-ui,sans-serif!important;backdrop-filter:blur(12px)!important;-webkit-backdrop-filter:blur(12px)!important;transform:none!important;opacity:1!important}
body:not(.bz-control-edit) .b .bz-control-symbol{font-size:19px!important;line-height:1!important;color:#c9edff!important}
body:not(.bz-control-edit) .b small{font:800 9px/1 system-ui,sans-serif!important;letter-spacing:.035em!important;color:#e4eef5!important}
body:not(.bz-control-edit) .b.on{border-color:#69e1ff!important;background:linear-gradient(145deg,#23617b,#12364c)!important;box-shadow:0 0 0 2px #55dfff42,0 5px 16px #000b!important}
body:not(.bz-control-edit) #joy{left:calc(var(--bz-control-safe-l) + 16px)!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;width:132px!important;height:132px!important;border:1px solid #d9f0ff75!important;border-radius:50%!important;background:radial-gradient(circle at 48% 42%,#d6efff1c 0 26%,#132b3bdc 70%,#08131eeF 100%)!important;box-shadow:0 9px 26px #0009,inset 0 0 25px #0009!important;transform:none!important}
body:not(.bz-control-edit) #knob{left:calc(50% - 22px)!important;top:calc(50% - 22px)!important;width:44px!important;height:44px!important;border:2px solid #ffffffc9!important;border-radius:50%!important;background:linear-gradient(145deg,#e4ff9c,#93d12f)!important;box-shadow:0 3px 15px #000a,0 0 0 5px #a8dc3a26!important}
body:not(.bz-control-edit) #sprint{left:calc(var(--bz-control-safe-l) + 164px)!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important}
body:not(.bz-control-edit) #vw{left:calc(var(--bz-control-safe-l) + 164px)!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-control-safe-b) + 82px)!important}
body:not(.bz-control-edit) #fire2{left:calc(var(--bz-control-safe-l) + 164px)!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-control-safe-b) + 148px)!important;width:54px!important;height:54px!important;min-width:54px!important;min-height:54px!important;border-color:#ffb09a!important;background:linear-gradient(145deg,#c14c3eeF,#72251ff2)!important}
body:not(.bz-control-edit) #fire{right:calc(var(--bz-control-safe-r) + 16px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;width:86px!important;height:86px!important;min-width:86px!important;min-height:86px!important;border:1px solid #ffb29d!important;border-radius:20px!important;background:linear-gradient(145deg,#f05c4ff5,#9d2926f5)!important;box-shadow:0 8px 24px #000b,inset 0 1px 0 #ffffff55!important}
body:not(.bz-control-edit) #fire .bz-control-symbol{font-size:26px!important;color:#fff!important}
body:not(.bz-control-edit) #jump{right:calc(var(--bz-control-safe-r) + 16px)!important;bottom:calc(var(--bz-control-safe-b) + 112px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #crouch{right:calc(var(--bz-control-safe-r) + 82px)!important;bottom:calc(var(--bz-control-safe-b) + 112px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #prone{right:calc(var(--bz-control-safe-r) + 148px)!important;bottom:calc(var(--bz-control-safe-b) + 112px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #scope{right:calc(var(--bz-control-safe-r) + 16px)!important;bottom:calc(var(--bz-control-safe-b) + 178px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #rel{right:calc(var(--bz-control-safe-r) + 82px)!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #swap{right:calc(var(--bz-control-safe-r) + 148px)!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #thr{right:calc(var(--bz-control-safe-r) + 214px)!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #gsw{right:calc(var(--bz-control-safe-r) + 214px)!important;bottom:calc(var(--bz-control-safe-b) + 82px)!important;top:auto!important;left:auto!important}
body:not(.bz-control-edit) #bzSquadOrders{position:fixed!important;top:calc(var(--bz-control-safe-t) + 112px)!important;right:calc(var(--bz-control-safe-r) + 16px)!important;left:auto!important;bottom:auto!important;z-index:82!important;display:flex!important;flex-wrap:nowrap!important;justify-content:center!important;gap:7px!important;width:auto!important;max-width:min(470px,calc(100vw - 240px))!important;padding:8px!important;border:1px solid #7bdcff8c!important;border-radius:18px!important;background:linear-gradient(120deg,#071725eF,#102b3aeF)!important;box-shadow:0 8px 24px #0009,inset 0 1px 0 #ffffff26!important;backdrop-filter:blur(13px)!important}
body:not(.bz-control-edit) #bzSquadOrders button{flex:1 1 0!important;min-width:58px!important;min-height:44px!important;padding:8px 10px!important;border:1px solid #8aaec044!important;border-radius:12px!important;background:#162b3ceF!important;color:#dceaf5!important;font:800 10px/1 system-ui,sans-serif!important;letter-spacing:.04em!important;touch-action:manipulation!important}
body:not(.bz-control-edit) #bzSquadOrders button[aria-pressed="true"]{border-color:#67e2ff!important;background:linear-gradient(145deg,#17617a,#12384d)!important;color:#fff!important;box-shadow:0 0 0 2px #54dfff25!important}
body:not(.bz-control-edit) #top{position:fixed!important;top:calc(var(--bz-control-safe-t) + 8px)!important;left:50%!important;right:auto!important;bottom:auto!important;transform:translateX(-50%)!important;z-index:80!important;max-width:42vw!important;padding:7px 12px!important;border:1px solid #ffffff35!important;border-radius:13px!important;background:#07131ee8!important;box-shadow:0 5px 18px #0008!important}
body:not(.bz-control-edit) #mm{position:fixed!important;top:calc(var(--bz-control-safe-t) + 10px)!important;left:calc(var(--bz-control-safe-l) + 10px)!important;right:auto!important;bottom:auto!important;width:clamp(100px,14vw,150px)!important;height:clamp(100px,14vw,150px)!important;z-index:78!important;border:1px solid #d9efff9c!important;border-radius:15px!important;box-shadow:0 6px 20px #0009!important}
body:not(.bz-control-edit) #hp{position:fixed!important;left:calc(var(--bz-control-safe-l) + 164px)!important;right:auto!important;bottom:calc(var(--bz-control-safe-b) + 16px)!important;top:auto!important;width:clamp(150px,17vw,220px)!important;max-width:22vw!important;padding:7px 10px!important;border:1px solid #ffffff38!important;border-radius:13px!important;background:#081620dc!important;box-shadow:0 5px 16px #0008!important}
body:not(.bz-control-edit) #wp{position:fixed!important;left:50%!important;right:auto!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important;top:auto!important;transform:translateX(-50%)!important;z-index:84!important;width:min(320px,27vw)!important;max-width:320px!important;padding:7px 10px!important;border:1px solid #a9c4d18c!important;border-radius:16px!important;background:linear-gradient(145deg,#0a1823ee,#142a36ee)!important;box-shadow:0 8px 24px #000a!important}
body:not(.bz-control-edit) #msg{position:fixed!important;top:calc(var(--bz-control-safe-t) + 104px)!important;left:50%!important;right:auto!important;bottom:auto!important;transform:translateX(-50%)!important;z-index:100!important;max-width:min(420px,70vw)!important;padding:8px 16px!important;border:1px solid #b7d9e866!important;border-radius:13px!important;background:#08151feb!important;box-shadow:0 8px 24px #0009!important;color:#f4f8fb!important;font-weight:800!important}
body:not(.bz-control-edit) #lnl,body:not(.bz-control-edit) #lnr{display:none!important}
body:not(.bz-control-edit) #pjump,body:not(.bz-control-edit) #pchute{left:50%!important;right:auto!important;top:50%!important;bottom:auto!important;transform:translate(-50%,-50%)!important;z-index:96!important;width:130px!important;height:48px!important;max-width:130px!important}
body:not(.bz-control-edit) #drive{left:calc(var(--bz-control-safe-l) + 164px)!important;right:auto!important;bottom:calc(var(--bz-control-safe-b) + 148px)!important;top:auto!important}
body:not(.bz-control-edit) .drive-only{z-index:94!important}
@media(orientation:landscape) and (max-height:560px){
 body:not(.bz-control-edit){--bz-control-size:52px;--bz-control-gap:6px}
 body:not(.bz-control-edit) #joy{width:116px!important;height:116px!important}
 body:not(.bz-control-edit) #knob{width:40px!important;height:40px!important;left:calc(50% - 20px)!important;top:calc(50% - 20px)!important}
 body:not(.bz-control-edit) #fire{width:74px!important;height:74px!important;min-width:74px!important;min-height:74px!important}
 body:not(.bz-control-edit) #jump,body:not(.bz-control-edit) #crouch,body:not(.bz-control-edit) #prone{bottom:calc(var(--bz-control-safe-b) + 96px)!important}
 body:not(.bz-control-edit) #scope{bottom:calc(var(--bz-control-safe-b) + 156px)!important}
 body:not(.bz-control-edit) #bzSquadOrders{top:calc(var(--bz-control-safe-t) + 96px)!important}
 body:not(.bz-control-edit) #hp{bottom:calc(var(--bz-control-safe-b) + 12px)!important}
 body:not(.bz-control-edit) #wp{bottom:calc(var(--bz-control-safe-b) + 8px)!important}
}
@media(orientation:portrait){
 body:not(.bz-control-edit) #joy{width:108px!important;height:108px!important;left:calc(var(--bz-control-safe-l) + 8px)!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important}
 body:not(.bz-control-edit) #knob{width:38px!important;height:38px!important;left:calc(50% - 19px)!important;top:calc(50% - 19px)!important}
 body:not(.bz-control-edit) .b{--bz-control-size:50px;width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important;max-width:50px!important;max-height:50px!important;border-radius:13px!important}
 body:not(.bz-control-edit) #fire{width:68px!important;height:68px!important;min-width:68px!important;min-height:68px!important}
 body:not(.bz-control-edit) #sprint,body:not(.bz-control-edit) #vw{left:calc(var(--bz-control-safe-l) + 122px)!important}
 body:not(.bz-control-edit) #fire2{left:calc(var(--bz-control-safe-l) + 122px)!important;width:48px!important;height:48px!important;min-width:48px!important;min-height:48px!important}
 body:not(.bz-control-edit) #jump{right:calc(var(--bz-control-safe-r) + 8px)!important;bottom:calc(var(--bz-control-safe-b) + 88px)!important}
 body:not(.bz-control-edit) #crouch{right:calc(var(--bz-control-safe-r) + 64px)!important;bottom:calc(var(--bz-control-safe-b) + 88px)!important}
 body:not(.bz-control-edit) #prone{right:calc(var(--bz-control-safe-r) + 120px)!important;bottom:calc(var(--bz-control-safe-b) + 88px)!important}
 body:not(.bz-control-edit) #scope{right:calc(var(--bz-control-safe-r) + 8px)!important;bottom:calc(var(--bz-control-safe-b) + 144px)!important}
 body:not(.bz-control-edit) #rel{right:calc(var(--bz-control-safe-r) + 64px)!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important}
 body:not(.bz-control-edit) #swap{right:calc(var(--bz-control-safe-r) + 120px)!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important}
 body:not(.bz-control-edit) #thr{right:calc(var(--bz-control-safe-r) + 176px)!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important}
 body:not(.bz-control-edit) #gsw{right:calc(var(--bz-control-safe-r) + 176px)!important;bottom:calc(var(--bz-control-safe-b) + 66px)!important}
 body:not(.bz-control-edit) #bzSquadOrders{top:calc(var(--bz-control-safe-t) + 78px)!important;right:calc(var(--bz-control-safe-r) + 8px)!important;max-width:calc(100vw - 150px)!important;gap:3px!important;padding:5px!important}
 body:not(.bz-control-edit) #bzSquadOrders button{min-width:0!important;min-height:38px!important;padding:5px!important;font-size:8px!important}
 body:not(.bz-control-edit) #top{max-width:42vw!important;font-size:10px!important}
 body:not(.bz-control-edit) #mm{width:82px!important;height:82px!important}
 body:not(.bz-control-edit) #hp{left:calc(var(--bz-control-safe-l) + 122px)!important;bottom:calc(var(--bz-control-safe-b) + 10px)!important;width:clamp(110px,26vw,170px)!important;max-width:28vw!important}
 body:not(.bz-control-edit) #wp{bottom:calc(var(--bz-control-safe-b) + 10px)!important;width:min(220px,35vw)!important}
 body:not(.bz-control-edit) #msg{top:calc(var(--bz-control-safe-t) + 84px)!important}
}
@media(max-width:390px) and (orientation:portrait){
 body:not(.bz-control-edit) #joy{width:92px!important;height:92px!important}
 body:not(.bz-control-edit) #sprint,body:not(.bz-control-edit) #vw,body:not(.bz-control-edit) #fire2{left:calc(var(--bz-control-safe-l) + 104px)!important}
 body:not(.bz-control-edit) #thr,body:not(.bz-control-edit) #gsw{display:none!important}
 body:not(.bz-control-edit) #hp{display:none!important}
 body:not(.bz-control-edit) #wp{width:38vw!important}
}
"""
js = r"""/* BATTLEZONE_V6_TOUCH_CONTROL_REBUILD_V1 */
(()=>{'use strict';
 const body=document.body,editor=document.getElementById('ced');
 const syncEditor=()=>body.classList.toggle('bz-control-edit',!!editor&&getComputedStyle(editor).display!=='none');
 if(editor&&typeof MutationObserver==='function')new MutationObserver(syncEditor).observe(editor,{attributes:true,attributeFilter:['style','class','hidden']});
 syncEditor();
 const clear=()=>{document.querySelectorAll('.b.on').forEach(e=>e.classList.remove('on'));};
 window.addEventListener('blur',clear);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)clear()});
 window.addEventListener('orientationchange',()=>{clear();syncEditor()},{passive:true});
 window.addEventListener('resize',syncEditor,{passive:true});
})();
"""
css_path = html.parent / "css" / css_name
js_path = html.parent / "js" / js_name
css_path.parent.mkdir(parents=True, exist_ok=True)
js_path.parent.mkdir(parents=True, exist_ok=True)
html.write_text(s, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
js_path.write_text(js, encoding="utf-8")
print("BATTLEZONE_V6_TOUCH_CONTROL_REBUILD_APPLIED", html, css_path, js_path)
