#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = (root / "app/src/main/assets/www/index.html").read_text(encoding="utf-8")
models = (root / "app/src/main/assets/www/js/models.js").read_text(encoding="utf-8")
assert "BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1" in html
assert "BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1" in models
for token in ("a.shoot=act(tpl.clips.shoot)", "a.reload=act(tpl.clips.reload)", "a.death=act(tpl.clips.death)", "function playAction(target,state)", "THREE.LoopOnce", "active.getClip().duration", "availableActions"):
    assert token in models, f"missing rigged animation capability: {token}"
for token in ("playAction(pm.root,'shoot')", "playAction(pm.root,'reload')", "playAction(pm.root,'death')", "playAction(b,'shoot')", "playAction(b,'death')", "playAction(a,'shoot')"):
    assert token in html, f"missing gameplay action trigger: {token}"
assert "function animSc(c,tg,dt,t)" in html, "procedural fallback must remain"
assert "if(!entry||!entry.an||!entry.an.acts[state]||entry.an.dead)return false" in models, "missing-clip and dead-state guard missing"
print("ANIMATION_ACTION_INTEGRATION_STATIC_CHECKS_OK")
