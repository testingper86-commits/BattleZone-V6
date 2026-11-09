#!/usr/bin/env python3
"""Regression gates for screenshot-driven Android HUD and lobby defects."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected one game index.html, found {len(files)}")
h=files[0].read_text(encoding="utf-8"); cssp=files[0].parent/"css"/"v6-screenshot-hardening.css"
if not cssp.is_file(): raise SystemExit("Final screenshot hardening stylesheet is missing")
c=cssp.read_text(encoding="utf-8")
checks={
 "final stylesheet linked after all competing HUD styles": h.rfind("v6-screenshot-hardening.css")>max(h.rfind("v6-pubg-hud.css"),h.rfind("v6-edge-control-system.css"),h.rfind("v6-touch-control-rebuild.css")),
 "Android landscape navigation rail reserved": "--bz-rail:88px" in c and "var(--bz-rail)" in c,
 "fire, jump, aim, crouch and prone respect reserved edge": all(x in c for x in ("#fire{","#jump{","#scope{","#crouch{","#prone{")) and c.count("var(--bz-rail)")>=8,
 "touch controls remain fixed and interactive": ".b{position:fixed!important" in c and "pointer-events:auto!important" in c,
 "bottom navigation is contained and scrollable": "#lb-nav{display:flex!important" in c and "overflow-x:auto!important" in c and "#lb-nav b{position:relative!important" in c,
 "deployment button stays in its own column": "#go2{left:calc(12px + var(--bz-fl))!important" in c,
 "character preview scales with available viewport": "#char{left:58%!important" in c and "height:clamp(250px,48vh,340px)" in c,
 "preview and match share one selected character snapshot": h.count("const BZ_ACTIVE_CHARACTER=bzSelectedCharacter();")==1 and h.count("BZ_ACTIVE_CHARACTER.color||SKN[ST_.cur][1]")==2,
 "invalid persisted skin state is normalized": "ST_.cur>=SKN.length" in h and "ST_.sk=ST_.sk.filter" in h,
 "hardening is applied once": h.count("BATTLEZONE_V6_SCREENSHOT_HARDENING_V1")==1,
}
for name,ok in checks.items(): print(("PASS" if ok else "FAIL"),name)
if not all(checks.values()): raise SystemExit("SCREENSHOT_HARDENING_REGRESSION_FAILED")
print("SCREENSHOT_HARDENING_REGRESSION_OK")
