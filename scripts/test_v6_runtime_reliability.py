#!/usr/bin/env python3
"""Build-blocking regression checks for V6 startup and responsive layout reliability."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
hs=list(root.rglob("app/src/main/assets/www/index.html")); ks=list(root.rglob("app/src/main/java/com/example/battlezone/MainActivity.kt"))
if len(hs)!=1 or len(ks)!=1: raise SystemExit(f"Expected one game HTML and MainActivity.kt, found {len(hs)} and {len(ks)}")
html=hs[0].read_text(encoding="utf-8"); activity=ks[0].read_text(encoding="utf-8")
cp=hs[0].parent/"css/v6-runtime-reliability.css"
if not cp.is_file(): raise SystemExit("Missing v6-runtime-reliability.css")
css=cp.read_text(encoding="utf-8")
checks={
 "runtime reliability marker in HTML and Android host":"BATTLEZONE_V6_RUNTIME_RELIABILITY_V2" in html and "BATTLEZONE_V6_RUNTIME_RELIABILITY_V2" in activity,
 "diagnostic WebGL context explicitly released":"gl.getExtension('WEBGL_lose_context')" in html and "loseProbe.loseContext()" in html,
 "startup watchdog counts only the game canvas":"r.domElement.id==='c'" in html and "window.__bzFrames++" in html,
 "lobby preview renderer is optional and failure-safe":"Lobby preview unavailable:" in html and "Lobby preview disabled:" in html and "bz-preview-fallback" in html,
 "preview renderer is recreated after match and app visibility transitions":"createLobbyPreview=(n)=>" in html and "if(started||document.hidden||!host.isConnected){if(activeRenderer)release();requestAnimationFrame(ll);return}" in html,
 "preview teardown clears references and can restart":"activeRenderer=null;activeScene=null;activeCamera=null;activeModel=null;window.lobSc=null" in html,
 "preview failures retry without a permanent blank character":"retryAt=n+1500" in html,
 "preview renderer uses bounded GPU settings":"antialias:false,powerPreference:'low-power'" in html and "lr.setPixelRatio(Math.min(devicePixelRatio||1,1))" in html,
 "deployment restores lobby on runtime failure":"Deployment handler returned without starting the match" in html and "$('lobby').style.display=''" in html and "window.bzFatal&&window.bzFatal" in html,
 "loop exceptions reach startup diagnostics":"window.__bzNote('Game loop: '+message)" in html,
 "Android WebView hardware surface configured":"setLayerType(View.LAYER_TYPE_HARDWARE, null)" in activity,
 "Android WebView page readiness logged":"onPageFinished" in activity and "Game startup state:" in activity,
 "Android main-frame load failures surfaced":"onReceivedError" in activity and "request.isForMainFrame" in activity and "Battle Zone could not load" in activity,
 "landscape safe-area and responsive overflow handled":"100dvh" in css and "env(safe-area-inset-left" in css and "overscroll-behavior:contain" in css,
 "touch targets and reduced-motion behavior retained":"min-height:44px" in css and "prefers-reduced-motion:reduce" in css,
}
for name,ok in checks.items(): print(("PASS" if ok else "FAIL")+"  "+name)
if not all(checks.values()): raise SystemExit("V6 runtime reliability regression checks failed")
print("PASS  V6 runtime reliability regression checks; inline JavaScript is checked by validate_project.py")
