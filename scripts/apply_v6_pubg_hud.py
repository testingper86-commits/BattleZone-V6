#!/usr/bin/env python3
"""Install BattleZone V6 PUBG-inspired responsive HUD and control-editor presentation."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
hits=list(root.rglob("app/src/main/assets/www/index.html"))
if len(hits)!=1: raise SystemExit(f"Expected one game index.html, found {len(hits)}")
html=hits[0]; source=html.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_PUBG_HUD_V1"; name="v6-pubg-hud.css"
link=f'<link rel="stylesheet" href="./css/{name}">'
if marker not in source:
 if source.count("</head>")!=1: raise SystemExit("Expected one closing head tag")
 source=source.replace("</head>",link+"\n</head>",1)
 source=source.replace("</body>",f"<!-- {marker} -->\n</body>",1)
elif link not in source: raise SystemExit("HUD marker exists without stylesheet")
css=r"""/* BATTLEZONE_V6_PUBG_HUD_V1 */
:root{--bz-safe-t:env(safe-area-inset-top,0px);--bz-safe-r:env(safe-area-inset-right,0px);--bz-safe-b:env(safe-area-inset-bottom,0px);--bz-safe-l:env(safe-area-inset-left,0px);--bz-touch:clamp(46px,6vh,58px)}
:root:not([data-bz-screen="gameplay"]) #joy,:root:not([data-bz-screen="gameplay"]) #knob,:root:not([data-bz-screen="gameplay"]) .b,:root:not([data-bz-screen="gameplay"]) #hp,:root:not([data-bz-screen="gameplay"]) #wp,:root:not([data-bz-screen="gameplay"]) #top,:root:not([data-bz-screen="gameplay"]) #mm,:root:not([data-bz-screen="gameplay"]) #msg,:root:not([data-bz-screen="gameplay"]) #bzSquadOrders{display:none!important;visibility:hidden!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] #joy,:root[data-bz-screen="gameplay"] .b{position:fixed!important;z-index:90!important;touch-action:none!important;user-select:none!important;-webkit-user-select:none!important}
:root[data-bz-screen="gameplay"] .b{display:flex!important;align-items:center!important;justify-content:center!important;flex-direction:column!important;gap:3px!important;width:var(--bz-touch)!important;height:var(--bz-touch)!important;min-width:var(--bz-touch)!important;min-height:var(--bz-touch)!important;max-width:var(--bz-touch)!important;max-height:var(--bz-touch)!important;padding:4px!important;border:1px solid #a6d5ec9c!important;border-radius:15px!important;background:linear-gradient(145deg,#1d4056f2,#091b2bf5)!important;color:#effaff!important;font:800 9px/1 system-ui,sans-serif!important;box-shadow:0 6px 18px #0009,inset 0 1px 0 #ffffff35!important;backdrop-filter:blur(12px)!important;transform:none!important;opacity:1!important}
:root[data-bz-screen="gameplay"] .b.on{border-color:#72e8ff!important;background:linear-gradient(145deg,#267b99,#12415a)!important;box-shadow:0 0 0 2px #62dcff48,0 6px 20px #000b!important}
:root[data-bz-screen="gameplay"] #joy{left:calc(var(--bz-safe-l) + 16px)!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 16px)!important;width:clamp(108px,17vh,136px)!important;height:clamp(108px,17vh,136px)!important;border:1px solid #d9f0ff9c!important;border-radius:50%!important;background:radial-gradient(circle at 48% 42%,#e5f7ff20 0 27%,#183d51eb 70%,#081521f7 100%)!important;box-shadow:0 8px 22px #0009,inset 0 0 24px #0008!important;transform:none!important}
:root[data-bz-screen="gameplay"] #knob{left:calc(50% - 21px)!important;top:calc(50% - 21px)!important;width:42px!important;height:42px!important;border:2px solid #fff!important;border-radius:50%!important;background:linear-gradient(145deg,#e2ff9c,#91cd2b)!important}
:root[data-bz-screen="gameplay"] #sprint,:root[data-bz-screen="gameplay"] #vw,:root[data-bz-screen="gameplay"] #fire2{left:calc(var(--bz-safe-l) + 164px)!important;right:auto!important;top:auto!important}
:root[data-bz-screen="gameplay"] #sprint{bottom:calc(var(--bz-safe-b) + 16px)!important}
:root[data-bz-screen="gameplay"] #vw{bottom:calc(var(--bz-safe-b) + 82px)!important}
:root[data-bz-screen="gameplay"] #fire2{bottom:calc(var(--bz-safe-b) + 148px)!important;background:linear-gradient(145deg,#c34e40,#762b25)!important;border-color:#ffb59e!important}
:root[data-bz-screen="gameplay"] #fire{right:calc(var(--bz-safe-r) + 16px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 16px)!important;width:clamp(76px,10vh,90px)!important;height:clamp(76px,10vh,90px)!important;min-width:clamp(76px,10vh,90px)!important;min-height:clamp(76px,10vh,90px)!important;border-radius:21px!important;background:linear-gradient(145deg,#f36e55,#a72c2b)!important;border-color:#ffd1bc!important;box-shadow:0 8px 24px #000b,inset 0 1px 0 #ffffff60!important}
:root[data-bz-screen="gameplay"] #jump{right:calc(var(--bz-safe-r) + 16px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
:root[data-bz-screen="gameplay"] #crouch{right:calc(var(--bz-safe-r) + 82px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
:root[data-bz-screen="gameplay"] #prone{right:calc(var(--bz-safe-r) + 148px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 110px)!important}
:root[data-bz-screen="gameplay"] #scope{right:calc(var(--bz-safe-r) + 16px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 176px)!important}
:root[data-bz-screen="gameplay"] #rel{right:calc(var(--bz-safe-r) + 82px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 16px)!important}
:root[data-bz-screen="gameplay"] #swap{right:calc(var(--bz-safe-r) + 148px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 16px)!important}
:root[data-bz-screen="gameplay"] #thr{right:calc(var(--bz-safe-r) + 214px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 16px)!important}
:root[data-bz-screen="gameplay"] #gsw{right:calc(var(--bz-safe-r) + 214px)!important;left:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 82px)!important}
:root[data-bz-screen="gameplay"] #lnl,:root[data-bz-screen="gameplay"] #lnr{display:none!important}
:root[data-bz-screen="gameplay"] #pjump,:root[data-bz-screen="gameplay"] #pchute{left:50%!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 18px)!important;transform:translateX(-50%)!important;width:140px!important;height:46px!important;min-height:46px!important;border-radius:13px!important;z-index:96!important;background:linear-gradient(145deg,#f2c75b,#b97820)!important;color:#16222b!important}
:root[data-bz-screen="gameplay"] #bzSquadOrders{position:fixed!important;top:calc(var(--bz-safe-t) + 12px)!important;right:calc(var(--bz-safe-r) + 16px)!important;left:auto!important;bottom:auto!important;z-index:82!important;display:flex!important;flex-wrap:nowrap!important;gap:5px!important;width:auto!important;max-width:min(430px,calc(100vw - 280px))!important;padding:6px!important;border:1px solid #72ddff85!important;border-radius:16px!important;background:linear-gradient(120deg,#061522ed,#133349ed)!important;box-shadow:0 7px 20px #0008!important;backdrop-filter:blur(12px)!important}
:root[data-bz-screen="gameplay"] #bzSquadOrders button{flex:1 1 0!important;min-width:54px!important;min-height:40px!important;padding:6px!important;border:1px solid #91b8d344!important;border-radius:11px!important;background:#142c40!important;color:#e7f5ff!important;font:800 9px system-ui!important;touch-action:manipulation!important}
:root[data-bz-screen="gameplay"] #bzSquadOrders button[aria-pressed="true"]{border-color:#66e4ff!important;background:#12536c!important;box-shadow:0 0 0 2px #54dfff25!important}
:root[data-bz-screen="gameplay"] #mm{position:fixed!important;top:calc(var(--bz-safe-t) + 10px)!important;left:calc(var(--bz-safe-l) + 10px)!important;right:auto!important;bottom:auto!important;width:clamp(88px,13vh,122px)!important;height:clamp(88px,13vh,122px)!important;z-index:76!important}
:root[data-bz-screen="gameplay"] #top{position:fixed!important;top:calc(var(--bz-safe-t) + 10px)!important;left:50%!important;right:auto!important;bottom:auto!important;transform:translateX(-50%)!important;z-index:76!important;max-width:32vw!important}
:root[data-bz-screen="gameplay"] #hp{position:fixed!important;top:calc(var(--bz-safe-t) + 138px)!important;left:calc(var(--bz-safe-l) + 10px)!important;right:auto!important;bottom:auto!important;width:clamp(100px,14vw,170px)!important;max-width:18vw!important;padding:6px 8px!important;border-radius:12px!important;background:#071725dc!important;border:1px solid #a4c6da60!important}
:root[data-bz-screen="gameplay"] #wp{position:fixed!important;left:50%!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-safe-b) + 10px)!important;transform:translateX(-50%)!important;width:min(230px,22vw)!important;max-width:230px!important;padding:6px!important;border:1px solid #aad0e080!important;border-radius:15px!important;background:#071724ed!important;box-shadow:0 7px 21px #0009!important;z-index:78!important}
:root[data-bz-screen="gameplay"] #cross{z-index:70!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] #msg{top:calc(var(--bz-safe-t) + 76px)!important;left:50%!important;right:auto!important;bottom:auto!important;transform:translateX(-50%)!important;z-index:100!important;max-width:52vw!important}
:root[data-bz-screen="controls-edit"] #ced{position:fixed!important;inset:0!important;z-index:250!important;display:flex!important;flex-direction:column!important;gap:10px!important;padding:calc(12px + var(--bz-safe-t)) calc(14px + var(--bz-safe-r)) calc(12px + var(--bz-safe-b)) calc(14px + var(--bz-safe-l))!important;overflow:auto!important;background:linear-gradient(145deg,#071725f5,#102b3df5)!important;color:#edf8ff!important;border:1px solid #67dfff80!important}
:root[data-bz-screen="controls-edit"] #ced .b,:root[data-bz-screen="controls-edit"] #ced #joy{position:relative!important;display:flex!important;pointer-events:auto!important;touch-action:none!important;transform:none!important}
:root[data-bz-screen="controls-edit"] #ced button{min-height:40px!important;border:1px solid #73dfff70!important;border-radius:11px!important;background:#17364b!important;color:#effaff!important;font-weight:800!important}
:root[data-bz-screen="controls-edit"] #ced button:active{background:#17617a!important}
:root[data-bz-screen="controls-edit"] #ced:before{content:"BATTLEZONE V6  /  CONTROL LAYOUT";display:block;flex:0 0 auto;padding:10px 12px;border:1px solid #63dfff70;border-radius:12px;background:#0b2638;font:900 14px system-ui;letter-spacing:.12em}
:root[data-bz-screen="controls-edit"] #ced:after{content:"DRAG TO POSITION  •  SAVE TO APPLY  •  RESET TO RESTORE DEFAULTS";display:block;flex:0 0 auto;padding:10px;border:1px solid #ffffff25;border-radius:10px;color:#a9d7ed;font:700 10px system-ui;letter-spacing:.08em}
@media(max-height:540px) and (orientation:landscape){:root[data-bz-screen="gameplay"]{--bz-touch:48px}:root[data-bz-screen="gameplay"] #joy{width:106px!important;height:106px!important}:root[data-bz-screen="gameplay"] #fire{width:70px!important;height:70px!important;min-width:70px!important;min-height:70px!important}:root[data-bz-screen="gameplay"] #jump,:root[data-bz-screen="gameplay"] #crouch,:root[data-bz-screen="gameplay"] #prone{bottom:calc(var(--bz-safe-b) + 80px)!important}:root[data-bz-screen="gameplay"] #scope{bottom:calc(var(--bz-safe-b) + 132px)!important}:root[data-bz-screen="gameplay"] #bzSquadOrders{top:calc(var(--bz-safe-t) + 8px)!important}:root[data-bz-screen="gameplay"] #wp{width:180px!important}}
@media(max-width:850px) and (orientation:landscape){:root[data-bz-screen="gameplay"] #bzSquadOrders{max-width:calc(100vw - 250px)!important;gap:2px!important}:root[data-bz-screen="gameplay"] #bzSquadOrders button{min-width:44px!important;font-size:8px!important}:root[data-bz-screen="gameplay"] #thr,:root[data-bz-screen="gameplay"] #gsw{display:none!important}:root[data-bz-screen="gameplay"] #wp{width:170px!important}}
@media(orientation:portrait){:root[data-bz-screen="gameplay"] #joy{width:100px!important;height:100px!important;left:calc(var(--bz-safe-l) + 7px)!important;bottom:calc(var(--bz-safe-b) + 8px)!important}:root[data-bz-screen="gameplay"] #knob{width:36px!important;height:36px!important;left:calc(50% - 18px)!important;top:calc(50% - 18px)!important}:root[data-bz-screen="gameplay"] #sprint,:root[data-bz-screen="gameplay"] #vw,:root[data-bz-screen="gameplay"] #fire2{left:calc(var(--bz-safe-l) + 112px)!important}:root[data-bz-screen="gameplay"] #fire2{bottom:calc(var(--bz-safe-b) + 108px)!important}:root[data-bz-screen="gameplay"] .b{--bz-touch:48px;border-radius:13px!important}:root[data-bz-screen="gameplay"] #fire{width:66px!important;height:66px!important;min-width:66px!important;min-height:66px!important}:root[data-bz-screen="gameplay"] #jump{right:calc(var(--bz-safe-r) + 8px)!important;bottom:calc(var(--bz-safe-b) + 84px)!important}:root[data-bz-screen="gameplay"] #crouch{right:calc(var(--bz-safe-r) + 62px)!important;bottom:calc(var(--bz-safe-b) + 84px)!important}:root[data-bz-screen="gameplay"] #prone{right:calc(var(--bz-safe-r) + 116px)!important;bottom:calc(var(--bz-safe-b) + 84px)!important}:root[data-bz-screen="gameplay"] #scope{right:calc(var(--bz-safe-r) + 8px)!important;bottom:calc(var(--bz-safe-b) + 138px)!important}:root[data-bz-screen="gameplay"] #rel{right:calc(var(--bz-safe-r) + 62px)!important;bottom:calc(var(--bz-safe-b) + 8px)!important}:root[data-bz-screen="gameplay"] #swap{right:calc(var(--bz-safe-r) + 116px)!important;bottom:calc(var(--bz-safe-b) + 8px)!important}:root[data-bz-screen="gameplay"] #thr,:root[data-bz-screen="gameplay"] #gsw{display:none!important}:root[data-bz-screen="gameplay"] #bzSquadOrders{top:calc(var(--bz-safe-t) + 82px)!important;right:calc(var(--bz-safe-r) + 6px)!important;max-width:calc(100vw - 112px)!important;gap:2px!important;padding:4px!important}:root[data-bz-screen="gameplay"] #bzSquadOrders button{min-width:0!important;min-height:32px!important;padding:3px!important;font-size:7px!important}:root[data-bz-screen="gameplay"] #mm{width:70px!important;height:70px!important}:root[data-bz-screen="gameplay"] #hp{top:calc(var(--bz-safe-t) + 82px)!important;left:calc(var(--bz-safe-l) + 7px)!important;max-width:20vw!important}:root[data-bz-screen="gameplay"] #wp{width:min(170px,34vw)!important}:root[data-bz-screen="gameplay"] #msg{top:calc(var(--bz-safe-t) + 120px)!important;max-width:80vw!important}}
@media(max-width:390px) and (orientation:portrait){:root[data-bz-screen="gameplay"] #joy{width:88px!important;height:88px!important}:root[data-bz-screen="gameplay"] #sprint,:root[data-bz-screen="gameplay"] #vw,:root[data-bz-screen="gameplay"] #fire2{left:calc(var(--bz-safe-l) + 96px)!important}:root[data-bz-screen="gameplay"] #thr,:root[data-bz-screen="gameplay"] #gsw,:root[data-bz-screen="gameplay"] #hp{display:none!important}:root[data-bz-screen="gameplay"] #wp{width:36vw!important}}
"""

# Publish authoritative gameplay state from the simulation loop.
movement_anchor = "bzFrameGameState.weapon=W[P.w]?.n||'Weapon';"
movement_new = ("bzFrameGameState.weapon=W[P.w]?.n||'Weapon';bzFrameGameState.air=Number(P.air)||0;"
                "bzFrameGameState.vehicle=!!P.veh;document.body.classList.toggle('bz-airborne',!!P.air);"
                "document.body.classList.toggle('bz-plane',P.air===2);document.body.classList.toggle('bz-skydiving',P.air===1);"
                "document.body.classList.toggle('bz-parachute',P.air===3);document.body.classList.toggle('bz-grounded',!P.air&&!P.veh);"
                "document.body.classList.toggle('bz-vehicle',!!P.veh);")
if movement_new not in source:
    if source.count(movement_anchor) != 1: raise SystemExit("Gameplay state anchor is not unique")
    source = source.replace(movement_anchor, movement_new, 1)

# Smooth start/stop input while retaining the existing terrain collision solver.
move_anchor = "if(P.air==2)fx=fz=0;"
move_new = ("if(P.air==2){fx=fz=0;P.bzMoveX=0;P.bzMoveZ=0;}else{"
            "const bzMoveRate=l>.05?12:16,bzMoveBlend=1-Math.exp(-Math.min(.1,dt)*bzMoveRate);"
            "P.bzMoveX=(Number(P.bzMoveX)||0)+(fx-(Number(P.bzMoveX)||0))*bzMoveBlend;"
            "P.bzMoveZ=(Number(P.bzMoveZ)||0)+(fz-(Number(P.bzMoveZ)||0))*bzMoveBlend;"
            "fx=P.bzMoveX;fz=P.bzMoveZ;}")
if move_new not in source:
    if source.count(move_anchor) != 1: raise SystemExit("Movement response anchor is not unique")
    source = source.replace(move_anchor, move_new, 1)
clear_anchor = "function clearGameplayInputs(){jid=null;joy={x:0,y:0};kn.style.transform='';"
clear_new = "function clearGameplayInputs(){jid=null;joy={x:0,y:0};P.bzMoveX=0;P.bzMoveZ=0;kn.style.transform='';"
if clear_new not in source:
    if source.count(clear_anchor) != 1: raise SystemExit("Input reset anchor is not unique")
    source = source.replace(clear_anchor, clear_new, 1)

css += r"""
/* BATTLEZONE_V6_PUBG_GAMEPLAY_FOUNDATION_V1 */
:root{--bz-f-t:env(safe-area-inset-top,0px);--bz-f-r:env(safe-area-inset-right,0px);--bz-f-b:env(safe-area-inset-bottom,0px);--bz-f-l:env(safe-area-inset-left,0px)}
:root[data-bz-screen="gameplay"] #bzSquadOrders{top:calc(var(--bz-f-t) + 104px)!important;right:calc(var(--bz-f-r) + 14px)!important;left:auto!important;bottom:auto!important;width:min(390px,calc(100vw - 300px))!important;max-width:calc(100vw - 300px)!important;min-width:0!important;z-index:88!important;gap:4px!important;padding:5px!important}
:root[data-bz-screen="gameplay"] #bzSquadOrders button{flex:1 1 0!important;min-width:0!important;min-height:38px!important;padding:4px!important;font-size:clamp(8px,1.05vw,10px)!important;white-space:nowrap!important}
:root[data-bz-screen="gameplay"] #snd,:root[data-bz-screen="gameplay"] #envb{top:calc(var(--bz-f-t) + 8px)!important;z-index:105!important}
:root[data-bz-screen="gameplay"] #snd{right:calc(var(--bz-f-r) + 54px)!important;left:auto!important}
:root[data-bz-screen="gameplay"] #envb{right:calc(var(--bz-f-r) + 8px)!important;left:auto!important}
:root[data-bz-screen="gameplay"] #hp{left:calc(var(--bz-f-l) + 10px)!important;right:auto!important;top:calc(var(--bz-f-t) + 132px)!important;bottom:auto!important;transform:none!important;width:clamp(112px,14vw,168px)!important;max-width:calc(100vw - 24px)!important;z-index:74!important}
:root[data-bz-screen="gameplay"] #kf{top:calc(var(--bz-f-t) + 164px)!important;right:calc(var(--bz-f-r) + 10px)!important;left:auto!important;bottom:auto!important;max-width:min(260px,38vw)!important;max-height:30vh!important;overflow:hidden!important;z-index:75!important}
:root[data-bz-screen="gameplay"] #wp{left:50%!important;right:auto!important;top:auto!important;bottom:calc(var(--bz-f-b) + 9px)!important;transform:translateX(-50%)!important;width:min(220px,25vw)!important;max-width:220px!important;z-index:77!important}
:root[data-bz-screen="gameplay"] #pchute,:root[data-bz-screen="gameplay"] #pjump{left:50%!important;right:auto!important;top:calc(50% + 112px)!important;bottom:auto!important;transform:translate(-50%,-50%)!important;width:148px!important;height:48px!important;min-width:148px!important;min-height:48px!important;z-index:96!important}
:root[data-bz-screen="gameplay"] body.bz-airborne #wp{display:none!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] body.bz-airborne #fire,:root[data-bz-screen="gameplay"] body.bz-airborne #fire2,:root[data-bz-screen="gameplay"] body.bz-airborne #scope,:root[data-bz-screen="gameplay"] body.bz-airborne #jump,:root[data-bz-screen="gameplay"] body.bz-airborne #crouch,:root[data-bz-screen="gameplay"] body.bz-airborne #prone,:root[data-bz-screen="gameplay"] body.bz-airborne #rel,:root[data-bz-screen="gameplay"] body.bz-airborne #swap,:root[data-bz-screen="gameplay"] body.bz-airborne #thr,:root[data-bz-screen="gameplay"] body.bz-airborne #gsw{display:none!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] body.bz-airborne #joy,:root[data-bz-screen="gameplay"] body.bz-airborne #sprint,:root[data-bz-screen="gameplay"] body.bz-airborne #vw{display:flex!important;pointer-events:auto!important}
:root[data-bz-screen="gameplay"] body.bz-plane #pjump,:root[data-bz-screen="gameplay"] body.bz-skydiving #pchute{display:flex!important}
:root[data-bz-screen="gameplay"] body.bz-parachute #pchute{background:linear-gradient(145deg,#e8bd58,#b87924)!important;color:#17222c!important;border-color:#fff0b4!important;box-shadow:0 8px 24px #0009!important}
:root[data-bz-screen="gameplay"] body.bz-grounded #pchute,:root[data-bz-screen="gameplay"] body.bz-grounded #pjump{display:none!important}
:root[data-bz-screen="gameplay"] #cross{z-index:70!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] #msg{z-index:100!important;max-width:min(520px,70vw)!important;white-space:normal!important;text-align:center!important}
@media(max-width:900px) and (orientation:landscape){:root[data-bz-screen="gameplay"] #bzSquadOrders{top:calc(var(--bz-f-t) + 108px)!important;width:min(340px,calc(100vw - 250px))!important;max-width:calc(100vw - 250px)!important}:root[data-bz-screen="gameplay"] #hp{top:calc(var(--bz-f-t) + 120px)!important;width:116px!important}:root[data-bz-screen="gameplay"] #wp{width:180px!important}}
@media(orientation:portrait){:root[data-bz-screen="gameplay"] #bzSquadOrders{top:calc(var(--bz-f-t) + 92px)!important;right:calc(var(--bz-f-r) + 6px)!important;width:calc(100vw - 94px)!important;max-width:calc(100vw - 94px)!important}:root[data-bz-screen="gameplay"] #bzSquadOrders button{min-height:32px!important;font-size:7px!important;padding:3px!important}:root[data-bz-screen="gameplay"] #hp{top:calc(var(--bz-f-t) + 82px)!important;left:calc(var(--bz-f-l) + 6px)!important;width:96px!important}:root[data-bz-screen="gameplay"] #kf{top:calc(var(--bz-f-t) + 132px)!important;max-width:42vw!important}:root[data-bz-screen="gameplay"] #pchute,:root[data-bz-screen="gameplay"] #pjump{top:calc(50% + 82px)!important}:root[data-bz-screen="gameplay"] #wp{width:min(168px,36vw)!important}}
@media(max-height:520px) and (orientation:landscape){:root[data-bz-screen="gameplay"] #pchute,:root[data-bz-screen="gameplay"] #pjump{top:calc(50% + 72px)!important}:root[data-bz-screen="gameplay"] #wp{bottom:calc(var(--bz-f-b) + 5px)!important}}
"""
css_path=html.parent/"css"/name;css_path.parent.mkdir(parents=True,exist_ok=True)
html.write_text(source,encoding="utf-8");css_path.write_text(css,encoding="utf-8")
print("PUBG_STYLE_HUD_APPLIED")
