#!/usr/bin/env python3
"""Regression gate for the real WILDBOUND playable prototype."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
base = root / "app/src/main/assets/www/js/wildbound"
files = {name: base / name for name in ("actors/actors.js", "world/world.js", "rendering/runtime.js", "gameplay/combat.js", "ai/monster-ai.js")}
for path in files.values():
    if not path.is_file(): raise SystemExit(f"Missing gameplay module: {path}")
a, w, r, c, ai = (files[k].read_text(encoding="utf-8") for k in files)
checks = {
    "existing hunter actor and rig animation remain": "loadRigged(groups)" in a and "updateHunter(g,dt,moving,attacking)" in a,
    "all four enemy archetypes remain available": all(f"'{kind}'" in r for kind in ("stalker", "wraith", "ironmaw", "king")),
    "monsters have layered chest and shoulder armor": "const chest=mesh(new T.OctahedronGeometry" in a and "const pa=mesh(new T.SphereGeometry" in a,
    "monsters have dorsal ridge silhouettes": "const ridge=mesh(new T.ConeGeometry" in a,
    "forest floor has instanced fern undergrowth": "fernCount=180" in w and "scene.add(ferns,fernTips)" in w,
    "forest has fallen log dressing": "logCount=16" in w and "scene.add(logs)" in w,
    "forest has animated offline fireflies": "fireflyCount=72" in w and "w.fireflies.geometry.attributes.position.needsUpdate=true" in w,
    "quality settings scale new forest batches": "ferns.count=Math.floor(fernCount*f)" in w and "fireflies.visible=q!=='low'" in w,
    "gameplay keeps real mobile movement and AI": "W.ai.update(game,dt)" in r and "game.input.x" in r,
    "gameplay keeps real camera and mission start": "cameraYaw" in r and "W.missions.reset(game)" in r,
    "combat keeps hit detection and weak-point damage": "W.physics.forwardDot" in c and "weak?2.2:1" in c,
    "combat spawns visible hit feedback": "game.spawnImpact(hit.position,weak)" in c,
    "runtime animates and disposes hit effects": "game.effects.length-1" in r and "e.mesh.geometry.dispose()" in r,
    "environment updates in lobby and active gameplay": r.count("game.environment.update(game.environment,dt,") == 2,
    "offline runtime contains no external asset dependency": "https://" not in a+w+r+c,
}
for label, ok in checks.items(): print(("PASS" if ok else "FAIL"), label)
if not all(checks.values()): raise SystemExit("WILDBOUND_PLAYABLE_PROTOTYPE_REGRESSION_FAILED")
for name, path in files.items():
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode: raise SystemExit(f"JavaScript syntax failed in {name}:\n{result.stderr}")
    print("PASS JavaScript syntax", name)
print("WILDBOUND_PLAYABLE_PROTOTYPE_OK", len(checks)+len(files), "checks")
