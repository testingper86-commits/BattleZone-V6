#!/usr/bin/env python3
"""Regression checks for persistent live offline squad commands."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
html = files[0].read_text(encoding="utf-8")
checks = {
    "squad command patch marker": "BATTLEZONE_V6_SQUAD_COMMAND_SYSTEM_V1" in html,
    "all four real squad orders are present": all(f'data-bz-order="{x}"' in html for x in ("regroup", "focus", "flank", "hold")),
    "commands are accessible and keyboard-operable": 'role="group" aria-label="Squad combat orders"' in html and 'type="button"' in html,
    "selected order persists locally": "localStorage.setItem('bzSquadOrder',value)" in html and "localStorage.getItem('bzSquadOrder')" in html,
    "focus order selects a live nearby enemy": "getFocusTarget" in html and "b.userData.alive&&!b.userData.ally" in html and "d<=120" in html,
    "focus order directs all allies to one target": "if(focused)en=focused" in html,
    "regroup order clears combat targets and returns allies to formation": "if(bzOrder==='regroup')en=null;" in html,
    "flank order assigns a distinct flank role with alternating sides": "role=(bzOrder==='flank'?'flank'" in html and "side=u.squadSide||((i%2)?1:-1)" in html,
    "hold order locks movement while defending nearby": "if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0;}" in html,
    "hold order stays in place when no target exists": "if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34)" in html,
    "airborne actors cannot be selected as targets": "u.airDrop||u.falling||u.chute" in html,
    "player cannot fire or emit weapon audio before landing": "P.y>(P.gh||1.6)+.22" in html and "Math.abs(P.vy||0)>.75" in html,
    "UI hides when no active squad is deployed": "root.dataset.active=visible?'1':'0'" in html,
    "safe-area and compact mobile layout included": "env(safe-area-inset-top" in html and "max-width:420px" in html,
    "reduced-motion preference respected": "prefers-reduced-motion:no-preference" in html,
}
for name, ok in checks.items(): print(("PASS" if ok else "FAIL") + "  " + name)
if not all(checks.values()): raise SystemExit("V6 squad command regression checks failed")
print("PASS  V6 squad command regression checks")
