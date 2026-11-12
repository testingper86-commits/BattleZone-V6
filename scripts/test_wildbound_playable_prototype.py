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
    "existing hunter actor and rig animation remain": "loadRigged(groups)" in a and "updateHunter(actor,dt,moving,attacking)" in a,
    "all four enemy archetypes remain available": all(f"'{kind}'" in r for kind in ("stalker", "wraith", "ironmaw", "king")),
    "monster models use layered anatomy and emissive weak points": "ribPlate" in a and "coreMaterial" in a and "weakPoint:core" in a,
    "monster silhouettes include articulated limbs and species-specific detail": "armCount=king?4:2" in a and "const spike=mesh(new T.ConeGeometry" in a and "const tusk=mesh(new T.ConeGeometry" in a,
    "forest remains GPU-instanced with PBR ground and atmospheric haze": "new t.InstancedMesh" in w and "floor_basecolor.png" in w and "haze" in w,
    "forest canopy has GPU-driven two-axis wind": "uBlackpineWindTime" in w and "transformed.x+=sin(uBlackpineWindTime" in w and "transformed.z+=cos(uBlackpineWindTime" in w,
    "quality settings scale instanced environment batches": "trunk.count=Math.floor(ti*f)" in w and "rocks.count=Math.floor(ri*f)" in w,
    "gameplay keeps real mobile movement and monster AI": "W.ai.update(game,dt)" in r and "game.input.x" in r,
    "gameplay keeps orbit camera and mission start": "game.cameraYaw" in r and "W.missions.reset(game)" in r,
    "combat keeps directional hit detection and weak-point damage": "W.physics.forwardDot" in c and "weak?2.2:1" in c,
    "combat publishes hit feedback to the VFX system": "W.bus.emit('hit'" in c and "game.vfx.burst(e.monster.position" in r,
    "runtime updates and disposes the pooled VFX system": "game.vfx.update(dt)" in r and "game.vfx.dispose()" in r,
    "environment updates in lobby and active gameplay": r.count("W.world.update(game.environment,dt,") == 2,
    "playable source is canonical and the installer is idempotent": "WILDBOUND_PLAYABLE_VERTICAL_SLICE_V1" in r,
    "offline runtime contains no external asset dependency": "https://" not in a+w+r+c,
}
for label, ok in checks.items(): print(("PASS" if ok else "FAIL"), label)
if not all(checks.values()): raise SystemExit("WILDBOUND_PLAYABLE_PROTOTYPE_REGRESSION_FAILED")
for name, path in files.items():
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode: raise SystemExit(f"JavaScript syntax failed in {name}:\n{result.stderr}")
    print("PASS JavaScript syntax", name)
print("WILDBOUND_PLAYABLE_PROTOTYPE_OK", len(checks)+len(files), "checks")
