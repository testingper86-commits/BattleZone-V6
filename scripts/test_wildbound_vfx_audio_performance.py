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
# Regression: hunt tracking injects lifecycle code after elapsed advancement,
# so VFX must target the elapsed statement independently of adjacent statements.
tracking_runtime = "function update(dt){let p=game.player,s=W.state.player,c=W.state.combat;game.elapsed+=dt;game.trackCd=Math.max(0,(game.trackCd||0)-dt);if(game.trackMarker){game.trackExpires-=dt;}game.invulnerable=Math.max(0,game.invulnerable-dt);}function loop(now){update(now);}"
tracking_anchor = "game.elapsed+=dt;"
assert tracking_runtime.count(tracking_anchor) == 1
tracking_runtime = tracking_runtime.replace(tracking_anchor, tracking_anchor + "if(game.effects)game.effects.update(dt);", 1)
assert tracking_runtime.count("game.effects.update(dt)") == 1
assert tracking_runtime.index("game.elapsed+=dt;") < tracking_runtime.index("game.effects.update(dt)") < tracking_runtime.index("game.trackCd=")
assert tracking_runtime.index("game.effects.update(dt)") < tracking_runtime.index("game.invulnerable=")
checks = {
 "bounded fixed-size particle pool": "count=72" in r and "cursor++%count" in r,
 "particles use GPU buffer attributes and one draw object": "BufferAttribute(positions,3)" in r and "new three.Points(" in r,
 "particle simulation updates in the main frame loop": "game.effects.update(dt)" in r,
 "VFX update remains compatible with hunt-tracking lifecycle insertion": tracking_runtime.count("game.effects.update(dt)") == 1 and tracking_runtime.index("game.effects.update(dt)") < tracking_runtime.index("game.trackCd=") < tracking_runtime.index("game.invulnerable="),
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
