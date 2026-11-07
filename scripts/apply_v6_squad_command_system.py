#!/usr/bin/env python3
"""Add persistent, live squad orders to the offline V6 battle runtime."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
path = files[0]
source = path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_V1"
if marker in source:
    print("BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_ALREADY_APPLIED")
    raise SystemExit(0)

def once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    source = source.replace(old, new, 1)

once(
    "<style>",
    """<style>
/* BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_V1 */
#bzSquadOrders{position:fixed;z-index:80;top:calc(env(safe-area-inset-top,0px) + 78px);right:max(10px,env(safe-area-inset-right,0px));display:none;gap:5px;padding:6px;border:1px solid #8bdcff55;border-radius:13px;background:linear-gradient(145deg,#101d2be8,#07111be8);box-shadow:0 8px 28px #0008;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);font:700 10px/1.1 system-ui,sans-serif;color:#eaf7ff;touch-action:manipulation}
#bzSquadOrders[data-active="1"]{display:flex}
#bzSquadOrders button{min-width:48px;min-height:36px;padding:5px 7px;border:1px solid #6f8fa455;border-radius:8px;background:#172638;color:#d8e8f5;font:700 9px/1.1 system-ui,sans-serif;letter-spacing:.04em}
#bzSquadOrders button[aria-pressed="true"]{border-color:#56d8ff;background:#16445a;color:#fff;box-shadow:inset 0 0 0 1px #56d8ff55}
#bzSquadOrders button:focus-visible{outline:2px solid #fff;outline-offset:2px}
@media(prefers-reduced-motion:no-preference){#bzSquadOrders button{transition:background .16s,border-color .16s}}
@media(max-width:420px){#bzSquadOrders{top:calc(env(safe-area-inset-top,0px) + 70px);right:6px;gap:3px;padding:4px}#bzSquadOrders button{min-width:43px;min-height:34px;padding:4px}}
""",
    "squad command styles",
)
once(
    "</body>",
    """<div id="bzSquadOrders" role="group" aria-label="Squad combat orders" data-active="0">
  <button type="button" data-bz-order="regroup" aria-pressed="false" title="Regroup around player">REGROUP</button>
  <button type="button" data-bz-order="focus" aria-pressed="false" title="Focus fire on the selected threat">FOCUS</button>
  <button type="button" data-bz-order="flank" aria-pressed="false" title="Use flanking movement">FLANK</button>
  <button type="button" data-bz-order="hold" aria-pressed="false" title="Hold current positions">HOLD</button>
</div>
<script>
// BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_V1
(()=>{'use strict';
 const root=document.getElementById('bzSquadOrders');if(!root)return;
 const allowed=new Set(['regroup','focus','flank','hold']);
 let order='regroup',focusId=null;
 try{const saved=localStorage.getItem('bzSquadOrder');if(allowed.has(saved))order=saved}catch(e){}
 const setOrder=value=>{if(!allowed.has(value))return;order=value;try{localStorage.setItem('bzSquadOrder',value)}catch(e){};root.querySelectorAll('[data-bz-order]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bzOrder===order)));};
 const focusTarget=()=>{if(!focusId)return null;const target=Array.isArray(bots)?bots.find(b=>b&&b.userData&&b.userData.nid===focusId&&b.userData.alive&&!b.userData.ally):null;if(!target)focusId=null;return target};
 root.addEventListener('click',event=>{const button=event.target.closest('[data-bz-order]');if(!button)return;setOrder(button.dataset.bzOrder);if(order==='focus'){let best=null,distance=Infinity;const actors=Array.isArray(bots)?bots:[];actors.forEach(b=>{const u=b&&b.userData;if(!u||!u.alive||u.ally||u.airDrop||u.falling||!b.position)return;const d=Math.hypot(b.position.x-(P?.x||0),b.position.z-(P?.z||0));if(d<distance&&d<=120){best=b;distance=d}});focusId=best?.userData?.nid||null;if(!focusId){setOrder('regroup');if(typeof window.msg==='function')window.msg('NO THREAT IN RANGE • SQUAD REGROUPING')}else if(typeof window.msg==='function')window.msg('SQUAD ORDER • FOCUS FIRE') }else if(typeof window.msg==='function')window.msg('SQUAD ORDER • '+order.toUpperCase());});
 setOrder(order);
 const sync=()=>{const visible=!!(started&&Array.isArray(al)&&al.some(a=>a&&a.userData&&a.userData.alive!==false&&!a.userData.down));root.dataset.active=visible?'1':'0';};
 window.addEventListener('bz:match-state',sync);setInterval(sync,500);
 window.BZSquadOrders=Object.freeze({get:()=>order,getFocusTarget:focusTarget});
})();
</script>
</body>""",
    "squad command interface",
)
once(
    "const role=u.squadRole||(['assault','support','flank'][i%3]),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;",
    "const role=(window.BZSquadOrders?.get()==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3])),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;",
    "live flank order",
)
once(
    "u.squadTargetObj=en;u.squadScanT=.16}let bd=en?Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z):96;",
    "u.squadTargetObj=en;u.squadScanT=.16}if(window.BZSquadOrders?.get()==='focus'){const focused=window.BZSquadOrders.getFocusTarget();if(focused)en=focused;}if(window.BZSquadOrders?.get()==='regroup'&&Math.hypot(px-a.position.x,pz-a.position.z)>12)en=null;let bd=en?Math.hypot(en.position.x-a.position.x,en.position.z-a.position.z):96;",
    "focus and regroup orders",
)
once(
    "}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(follow>34){gx=px;gz=pz;speed=7.8}",
    "}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(window.BZSquadOrders?.get()==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34){gx=px;gz=pz;speed=7.8}",
    "hold-position order",
)
source = source.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
path.write_text(source, encoding="utf-8")
print("BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_APPLIED", path)
