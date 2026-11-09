#!/usr/bin/env python3
"""Install a persistent, state-aware screen/HUD lifecycle repair for BattleZone V6."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(htmls)}")
html = htmls[0]
source = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_SCREEN_LIFECYCLE_REPAIR_V1"
css_name = "v6-screen-lifecycle.css"
js_name = "v6-screen-lifecycle.js"
css_path = html.parent / "css" / css_name
js_path = html.parent / "js" / js_name
css_path.parent.mkdir(parents=True, exist_ok=True)
js_path.parent.mkdir(parents=True, exist_ok=True)

css = r"""/* BATTLEZONE_V6_SCREEN_LIFECYCLE_REPAIR_V1 */
:root{--bz-inset-t:env(safe-area-inset-top,0px);--bz-inset-r:env(safe-area-inset-right,0px);--bz-inset-b:env(safe-area-inset-bottom,0px);--bz-inset-l:env(safe-area-inset-left,0px)}
html,body{width:100%;height:100%;min-height:100%;margin:0;overflow:hidden;overscroll-behavior:none}
*,*::before,*::after{box-sizing:border-box}
:root:not([data-bz-screen="gameplay"]) #top,
:root:not([data-bz-screen="gameplay"]) #mm,
:root:not([data-bz-screen="gameplay"]) #msg,
:root:not([data-bz-screen="gameplay"]) #hp,
:root:not([data-bz-screen="gameplay"]) #wp,
:root:not([data-bz-screen="gameplay"]) #joy,
:root:not([data-bz-screen="gameplay"]) #knob,
:root:not([data-bz-screen="gameplay"]) #fire,
:root:not([data-bz-screen="gameplay"]) #fire2,
:root:not([data-bz-screen="gameplay"]) #jump,
:root:not([data-bz-screen="gameplay"]) #crouch,
:root:not([data-bz-screen="gameplay"]) #prone,
:root:not([data-bz-screen="gameplay"]) #rel,
:root:not([data-bz-screen="gameplay"]) #swap,
:root:not([data-bz-screen="gameplay"]) #scope,
:root:not([data-bz-screen="gameplay"]) #thr,
:root:not([data-bz-screen="gameplay"]) #gsw,
:root:not([data-bz-screen="gameplay"]) #rev,
:root:not([data-bz-screen="gameplay"]) #vw,
:root:not([data-bz-screen="gameplay"]) #lnl,
:root:not([data-bz-screen="gameplay"]) #lnr,
:root:not([data-bz-screen="gameplay"]) #pjump,
:root:not([data-bz-screen="gameplay"]) #pchute,
:root:not([data-bz-screen="gameplay"]) #drive,
:root:not([data-bz-screen="gameplay"]) #drive-cam,
:root:not([data-bz-screen="gameplay"]) #drive-gas,
:root:not([data-bz-screen="gameplay"]) #drive-brake,
:root:not([data-bz-screen="gameplay"]) #drive-left,
:root:not([data-bz-screen="gameplay"]) #drive-right,
:root:not([data-bz-screen="gameplay"]) #bzSquadOrders,
:root:not([data-bz-screen="gameplay"]) #envb,
:root:not([data-bz-screen="gameplay"]) #snd,
:root:not([data-bz-screen="gameplay"]) #envp,
:root:not([data-bz-screen="gameplay"]) #cmp,
:root:not([data-bz-screen="gameplay"]) #kf,
:root:not([data-bz-screen="gameplay"]) #dmd{display:none!important;visibility:hidden!important;pointer-events:none!important}
:root[data-bz-screen="gameplay"] #ov{display:none!important}
:root[data-bz-screen="results"] #ov{position:fixed!important;inset:0!important;z-index:200!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:clamp(10px,2.2vh,22px)!important;padding:calc(20px + var(--bz-inset-t)) calc(18px + var(--bz-inset-r)) calc(20px + var(--bz-inset-b)) calc(18px + var(--bz-inset-l))!important;overflow:auto!important;background:radial-gradient(ellipse at 50% 24%,#405b76f2 0%,#14283beF 58%,#07121efc 100%)!important;text-align:center!important}
:root[data-bz-screen="results"] #ov h1{font-size:clamp(34px,7vw,76px)!important;line-height:1.02!important;letter-spacing:.12em!important;color:#ffd36b!important;text-shadow:0 5px 22px #0009!important;margin:0!important}
:root[data-bz-screen="results"] #ov>div{width:min(620px,94vw)!important;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:10px!important;padding:18px!important;border:1px solid #ffffff35!important;border-radius:18px!important;background:#071522b8!important;box-shadow:0 12px 34px #0007!important;color:#eaf3fb!important;font-size:clamp(14px,2.3vw,20px)!important;line-height:1.4!important}
:root[data-bz-screen="results"] #ov>div .bz-result-stat{display:flex;flex-direction:column;gap:3px;align-items:center}
:root[data-bz-screen="results"] #ov>div .bz-result-stat b{font-size:clamp(22px,4vw,34px);color:#ffd36b}
:root[data-bz-screen="results"] #go{min-height:56px!important;max-width:min(480px,90vw)!important;padding:13px clamp(26px,6vw,64px)!important;border:1px solid #fff8!important;border-radius:999px!important;background:linear-gradient(135deg,#ffe36b,#ff9818)!important;color:#17202a!important;font-size:clamp(20px,3.8vw,32px)!important;letter-spacing:.06em!important;box-shadow:0 9px 26px #0007!important}
:root[data-bz-screen="results"] #ov small{display:none!important}
:root[data-bz-screen="results"] #ov .bz-result-caption{display:block!important;max-width:620px!important;color:#c9d7e4!important;font-size:13px!important}
:root[data-bz-screen="lobby"] #lobby{padding:calc(8px + var(--bz-inset-t)) calc(10px + var(--bz-inset-r)) calc(10px + var(--bz-inset-b)) calc(10px + var(--bz-inset-l))}
:root[data-bz-screen="preview"] #pv{z-index:150!important;padding:calc(10px + var(--bz-inset-t)) calc(12px + var(--bz-inset-r)) calc(12px + var(--bz-inset-b)) calc(12px + var(--bz-inset-l))!important}
#pvb{min-height:0}
#pvi{min-width:0;overflow:auto;overscroll-behavior:contain}
#pvi>div{display:flex;justify-content:space-between;gap:12px;min-width:0;padding:9px 10px;border-bottom:1px solid #ffffff18}
#pvi>div span{color:#b9c7d2}
#pvi>div b{text-align:right;overflow-wrap:anywhere}
#pvbtn{padding-bottom:var(--bz-inset-b)}
#lb-nav{padding-bottom:var(--bz-inset-b);max-width:calc(100vw - var(--bz-inset-l) - var(--bz-inset-r) - 20px)}
#lb-l,#setc,#maps{min-height:0;overscroll-behavior:contain}
#lb-l{max-height:calc(100dvh - 120px - var(--bz-inset-t) - var(--bz-inset-b));overflow:auto}
#maps{max-height:calc(100dvh - 170px - var(--bz-inset-t) - var(--bz-inset-b));overflow:auto}
#go2{max-width:calc(100vw - 28px - var(--bz-inset-l) - var(--bz-inset-r))}
#bzHub{padding-top:calc(14px + var(--bz-inset-t))!important;padding-bottom:calc(14px + var(--bz-inset-b))!important}
@media(orientation:landscape) and (max-height:520px){:root[data-bz-screen="results"] #ov{gap:8px!important;padding-block:8px!important}:root[data-bz-screen="results"] #ov>div{padding:10px!important;gap:6px!important}:root[data-bz-screen="results"] #go{min-height:44px!important;padding-block:8px!important}#lb-l{max-height:calc(100dvh - 92px - var(--bz-inset-t) - var(--bz-inset-b))}}
@media(orientation:portrait){:root[data-bz-screen="results"] #ov>div{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
@media(prefers-reduced-motion:no-preference){:root[data-bz-screen="results"] #ov h1,:root[data-bz-screen="results"] #go{animation:bzResultEnter .28s ease-out both}@keyframes bzResultEnter{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}}
"""
js = r"""/* BATTLEZONE_V6_SCREEN_LIFECYCLE_REPAIR_V1 */
(()=>{'use strict';
 const root=document.documentElement;
 const byId=id=>document.getElementById(id);
 const visible=el=>!!el&&getComputedStyle(el).display!=='none'&&getComputedStyle(el).visibility!=='hidden';
 let last='';
 function setScreen(next){
   if(!next||last===next)return;
   last=next;root.dataset.bzScreen=next;
   root.dataset.bzHudEnabled=String(next==='gameplay');
   window.dispatchEvent(new CustomEvent('bz:screen-change',{detail:{screen:next}}));
 }
 function sync(){
   const lobby=byId('lobby'),preview=byId('pv'),results=byId('ov'),editor=byId('ced');
   const heading=results&&results.querySelector('h1');
   const resultText=heading?heading.textContent.trim().toUpperCase():'';
   const isResults=visible(results)&&(/ELIMINATED|WINNER/.test(resultText));
   if(isResults){setScreen('results');return}
   if(visible(editor)){setScreen('controls-edit');return}
   if(preview&&preview.classList.contains('on')){setScreen('preview');return}
   if(visible(lobby)){setScreen('lobby');return}
   setScreen('gameplay');
 }
 const observer=new MutationObserver(sync);
 function start(){
   sync();
   [byId('lobby'),byId('pv'),byId('ov'),byId('ced')].filter(Boolean).forEach(el=>observer.observe(el,{attributes:true,attributeFilter:['style','class','hidden'],childList:true,subtree:true,characterData:true}));
   window.addEventListener('resize',sync,{passive:true});
   window.addEventListener('pageshow',sync);
   document.addEventListener('visibilitychange',()=>{if(!document.hidden)sync()});
   window.addEventListener('bz:match-start',()=>setScreen('gameplay'));
   window.addEventListener('bz:match-end',()=>setScreen('results'));
   window.addEventListener('bz:preview-open',()=>setScreen('preview'));
   window.addEventListener('bz:preview-close',sync);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
"""
if marker not in source:
    if source.count("</head>") != 1 or source.count("</body>") != 1:
        raise SystemExit("Expected one head and body closing tag; refusing unsafe insertion")
    source = source.replace("</head>", f'<link rel="stylesheet" href="./css/{css_name}">\n</head>', 1)
    source = source.replace("</body>", f'<script src="./js/{js_name}"></script>\n<!-- {marker} -->\n</body>', 1)
else:
    if f"./css/{css_name}" not in source or f"./js/{js_name}" not in source:
        raise SystemExit("Lifecycle marker exists but stylesheet or script link is missing")
css_path.write_text(css, encoding="utf-8")
js_path.write_text(js, encoding="utf-8")
print("BATTLEZONE_V6_SCREEN_LIFECYCLE_REPAIR_APPLIED", html, css_path, js_path)
