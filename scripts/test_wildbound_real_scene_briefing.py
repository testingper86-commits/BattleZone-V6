#!/usr/bin/env python3
"""Ensure the WILDBOUND briefing renders the real playable world and encounter."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
p = root / "app/src/main/assets/www/js/wildbound/rendering/runtime.js"
if not p.is_file(): raise SystemExit(f"Missing WILDBOUND renderer: {p}")
s = p.read_text()
checks = {
    "lobby renders the actual gameplay scene": "game.renderer.render(game.scene,game.camera)" in s,
    "briefing has no isolated preview scene": "previewScene" not in s and "previewCamera" not in s,
    "briefing has no placeholder circular floor": "new t.CircleGeometry(2.4,40)" not in s,
    "actual player is visible in briefing": "game.player.position.set(0,0,0)" in s,
    "all three encounter monsters are shown": all(x in s for x in ["'stalker',-4,-4", "'wraith',0,-6", "'ironmaw',4,-4"]),
    "real player rig is loaded": "W.actors.loadRigged([game.player])" in s,
    "lobby resize rerenders real scene": "function resize(){if(!game.renderer||!game.camera)return" in s and "new ResizeObserver" in s and "visualViewport" in s and "game.renderer.render(game.scene,game.camera)" in s,
    "deployment resets gameplay spawn": "game.player.position.set(0,0,12)" in s,
    "briefing continuously animates the real hunter and enemies": "function lobbyLoop(now)" in s and "W.actors.updateHunter(game.player,dt,false,false)" in s,
    "briefing animation starts after lobby controls initialize": "bindResponsiveResize();W.ui.init(game);W.bus.on('contract-complete',()=>{game.done=true});raf=requestAnimationFrame(lobbyLoop)" in s,
    "briefing animation resumes after returning to lobby": "W.ui.refresh();raf=requestAnimationFrame(lobbyLoop)" in s,
}
for label, ok in checks.items(): print(("PASS" if ok else "FAIL"), label)
if not all(checks.values()): raise SystemExit("WILDBOUND_REAL_SCENE_BRIEFING_FAILED")
r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
if r.returncode: raise SystemExit("Renderer JavaScript syntax failed:\n" + r.stderr)
print("PASS renderer JavaScript syntax")
print("WILDBOUND_REAL_SCENE_BRIEFING_OK", len(checks) + 1, "checks")
