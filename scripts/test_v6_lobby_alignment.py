#!/usr/bin/env python3
"""Regression checks for final lobby layout ownership and responsive constraints."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
htmls=list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls)!=1: raise SystemExit(f"Expected one game index.html, found {len(htmls)}")
html=htmls[0].read_text(encoding="utf-8")
css=htmls[0].parent/"css"/"v6-lobby-alignment.css"
if not css.is_file(): raise SystemExit("Final lobby alignment CSS asset is missing")
s=css.read_text(encoding="utf-8")
checks={
 "final alignment stylesheet linked after existing lobby styles":html.count("./css/v6-lobby-alignment.css")==1 and html.rfind("./css/v6-lobby-alignment.css")>html.rfind("./css/v6-runtime-reliability.css"),
 "lobby uses dynamic viewport and safe-area insets":"height:100dvh" in s and "env(safe-area-inset-left" in s and "env(safe-area-inset-right" in s,
 "configuration and map panels have independent scroll bounds":"#lb-l,#maps" in s and "overscroll-behavior:contain" in s,
 "configuration cards cannot overflow horizontally":"overflow-wrap:anywhere" in s and "max-width:100%" in s,
 "character preview is centered in reserved center lane":"#char{position:absolute!important;left:50%!important" in s and "transform:translate(-50%,-50%)" in s,
 "deploy action stays in lower-left safe area":"#go2{position:absolute!important;left:max(" in s and "bottom:max(" in s,
 "operator services fit four or seven tiles on one responsive row":"flex-wrap:nowrap" in s and "width:max-content" in s and "max-width:58vw" in s,
 "compact landscape has dedicated responsive rules":"orientation:landscape) and (max-height:560px)" in s,
 "short landscape has dedicated overflow-safe rules":"orientation:landscape) and (max-height:390px)" in s,
 "small landscape keeps controls inside viewport":"orientation:landscape) and (max-width:760px)" in s,
 "touch controls remain accessible":"#go2:focus-visible" in s and "touch-action" in s,
}
failed=[]
for name,ok in checks.items(): print(("PASS" if ok else "FAIL")+"  "+name); failed += [] if ok else [name]
if failed: raise SystemExit("Lobby alignment regressions: "+", ".join(failed))
print("PASS  V6 lobby alignment regression checks")
