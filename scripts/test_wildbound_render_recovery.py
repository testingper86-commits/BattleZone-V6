#!/usr/bin/env python3
"""Regression tests for WILDBOUND Android WebGL lifecycle recovery."""
from pathlib import Path
import subprocess,sys,shutil
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
base=root/"app/src/main/assets/www/js/wildbound"
runtime=base/"rendering/runtime.js"
css=root/"app/src/main/assets/www/css/wildbound.css"
if not runtime.is_file() or not css.is_file(): raise SystemExit("canonical runtime or CSS missing")
r=runtime.read_text();c=css.read_text();checks={
"recovery marker": "WILDBOUND_RENDER_RECOVERY_V1" in r,
"actual WebGL context lost handler": "webglcontextlost" in r,
"actual WebGL context restored handler": "webglcontextrestored" in r,
"context loss prevents browser teardown": "event.preventDefault()" in r,
"frame loop checks context health": "isContextLost()" in r,
"game-loop exceptions are surfaced": "WILDBOUND_RENDER_FRAME_ERROR" in r,
"lobby-loop exceptions are surfaced": "WILDBOUND_LOBBY_RENDER_ERROR" in r,
"restore resets Three.js renderer state": "game.renderer.resetState()" in r,
"resize follows visible host dimensions": "host.clientWidth" in r and "host.clientHeight" in r,
"dynamic layout resize observer": "new ResizeObserver" in r,
"Android viewport resize": "visualViewport" in r,
"support diagnostics exposed": "getRenderDiagnostics" in r and "canvasWidth" in r,
"retry keeps gameplay safe": "WILDBOUND_RESUME_BLOCKED" in r,
"visible recovery UI": "render-recovery" in c and ".render-recovery.visible" in c,
"original pause support preserved": "function pause(v)" in r and "pause-panel" in r,
"original lobby return preserved": "function toLobby()" in r and "W.state.screen='lobby'" in r,
"original hunt start preserved": "function start()" in r and "W.state.screen='game'" in r,
"original combat update preserved": "function update(dt)" in r and "W.ai.update(game,dt)" in r,
"original rendering preserved": "game.renderer.render(game.scene,game.camera)" in r,
"quality controls preserved": "setQuality(q)" in r,
"Three.js namespace captured as object": "T=window.THREE" in r and "T=()=>window.THREE" not in r,
"Three.js scene uses object binding": "let t=T;" in r and "let t=T();" not in r,
"Vector3 projectile and camera constructors resolve": "new T.Vector3()" in r and "new T.Vector3(p.position.x+Math.sin(game.cameraYaw)*5" in r,
"tracking marker Three.js constructors resolve": "new T.Mesh(new T.TorusGeometry" in r}
node=shutil.which("node")
if node:
    syntax=subprocess.run([node,"--check",str(runtime)],capture_output=True,text=True,timeout=30)
    checks["Node validates final runtime JavaScript syntax"]=syntax.returncode==0
    if syntax.returncode: print(syntax.stderr)
else:
    raise SystemExit("Node.js is required for runtime syntax validation")
scene_start=r.find("function makeScene(){")
scene_end=r.find("function resize(){",scene_start)
ensure_ui="W.main.ensureUi=()=>{if(!uiInitialized){W.ui.init(game);uiInitialized=true}};"
initialize="W.main.initialize=()=>{startupStage='lobby UI initialization';W.main.ensureUi();startupStage='scene construction';makeScene();"
checks["startup coordinator owns one-time UI initialization"] = ensure_ui in r and initialize in r
checks["renderer construction does not initialize lobby UI"] = scene_start >= 0 and scene_end > scene_start and "W.ui.init(game);" not in r[scene_start:scene_end]
failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items(): print(("PASS" if ok else "FAIL")+" "+name,flush=True)
if failed: raise SystemExit("render recovery regressions: "+", ".join(failed))
# The patcher exits before mutation when its version marker is present.
if "WILDBOUND_RENDER_RECOVERY_V1" not in r or c.count("WILDBOUND_RENDER_RECOVERY_V1") != 1:
    raise SystemExit("render recovery idempotency marker is missing or duplicated")
print("PASS idempotent marker guard")
print("WILDBOUND_RENDER_RECOVERY_OK",len(checks)+1,"checks")
