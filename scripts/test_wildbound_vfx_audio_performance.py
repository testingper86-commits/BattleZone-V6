#!/usr/bin/env python3
"""Regression checks for pooled VFX, dodge feedback and audio lifecycle."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
www = root / "app/src/main/assets/www"
paths = {
 "runtime": www / "js/wildbound/rendering/runtime.js",
 "combat": www / "js/wildbound/gameplay/combat.js",
 "audio": www / "js/wildbound/audio/audio.js",
}
for p in paths.values():
    if not p.is_file(): raise SystemExit(f"Missing WILDBOUND source: {p}")
r,c,a = (paths[k].read_text(encoding="utf-8") for k in ("runtime","combat","audio"))
checks = {
 "bounded fixed-size particle pool": "const count=72" in r and "cursor++%count" in r,
 "particles use GPU buffer attributes and one draw object": "BufferAttribute(positions,3)" in r and "new T().Points(" in r,
 "particle simulation updates in the main frame loop": "game.effects.update(dt)" in r,
 "hit and weak-point impacts have separate VFX": "W.bus.on('hit'" in r and "e.weak?18:9" in r,
 "monster death and boss phase have burst feedback": "W.bus.on('kill'" in r and "W.bus.on('boss-phase'" in r,
 "dodge emits positional VFX event": "WILDBOUND_DODGE_VFX_EVENT_V1" in c and "hunter-dodge" in c,
 "audio concurrency is bounded": "voices>=12" in a,
 "audio voices release nodes on completion": "o.onended=" in a and "o.disconnect()" in a and "g.disconnect()" in a,
 "audio context resumes after foreground/user gesture": "visibilitychange" in a and "pointerdown" in a and "resume()" in a,
}
for label, ok in checks.items(): print(("PASS" if ok else "FAIL"), label)
if not all(checks.values()): raise SystemExit("WILDBOUND_VFX_AUDIO_FAILED")
for p in paths.values():
    result = subprocess.run(["node","--check",str(p)],capture_output=True,text=True)
    if result.returncode: raise SystemExit(result.stderr)
print("WILDBOUND_VFX_AUDIO_OK", len(checks), "checks")
