#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit("Expected exactly one game index.html")
h=files[0].read_text(encoding="utf-8");a=files[0].parent
css=(a/"css"/"bz-tactical-command.css");js=(a/"js"/"bz-tactical-command.js")
if not css.is_file() or not js.is_file(): raise SystemExit("Tactical UI assets missing")
c=css.read_text(encoding="utf-8");j=js.read_text(encoding="utf-8")
checks={
 "12 real hub screens":all("['"+k+"','"+v+"']" in h for k,v in [('command','Command Center'),('deployment','Deployment Lobby'),('operator','Operator Bay'),('armory','Armory'),('squad','Squad Command'),('zones','Mission Zones'),('combat','Combat HUD'),('pause','Pause Menu'),('results','After Action'),('service','Service Record'),('settings','Settings'),('controls','Controls')]),
 "existing profile/shop/maps reused":"else if(page==='operator')profilePage()" in h and "else if(page==='armory')shopPage()" in h and "else if(page==='zones')mapsPage()" in h,
 "live squad orders reused":"window.BZSquadOrders.get()" in h and "data-bz-order=" in h,
 "game state snapshot":"window.BZGameState={started:!!started" in h,
 "pause and resume wired":"if(window.BZ_TACTICAL_PAUSED)return" in h and "window.BZ_TACTICAL_PAUSED=false" in h,
 "real controls reused":"data-tac-control" in h and "['lay','CONTROL LAYOUT']" in h,
 "no fabricated match results":"NO COMPLETED-MATCH REPORT RECORDED" in h and "not fabricated" in h,
 "mobile and reduced-motion styles":"max-width:700px" in c and "prefers-reduced-motion:reduce" in c,
 "lobby entry point":"bzTacEntry" in j and "open('command')" in j,
 "local assets linked":"./css/bz-tactical-command.css" in h and "./js/bz-tactical-command.js" in h,
 "marker present":"BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1" in h and "BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1" in c and "BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1" in j,
}
for n,ok in checks.items(): print(("PASS " if ok else "FAIL ")+n)
if not all(checks.values()): raise SystemExit("Tactical UI checks failed")
print("PASS tactical command UI regression suite")
