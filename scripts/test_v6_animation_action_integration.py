#!/usr/bin/env python3
from pathlib import Path
import json
import struct
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = (root / "app/src/main/assets/www/index.html").read_text(encoding="utf-8")
models_path = root / "app/src/main/assets/www/js/models.js"
models = models_path.read_text(encoding="utf-8")
assert "BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1" in html
assert "BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1" in models
for token in (
    "a.shoot=act(clips.shoot)", "a.reload=act(clips.reload)",
    "a.death=act(clips.death)", "function playAction(target,state)",
    "THREE.LoopOnce", "active.getClip().duration", "availableActions",
    "a.cur=null", "e.an.cur=null", "resumeAction:null", "e.an.resumeAction.stop()", "want.a.fadeIn(.12).play()",
    "death|die|dead|defeat",
):
    assert token in models, f"missing rigged animation capability or recovery: {token}"
for token in (
    "playAction(pm.root,'shoot')", "playAction(pm.root,'reload')",
    "playAction(pm.root,'death')", "playAction(b,'shoot')",
    "playAction(b,'death')", "playAction(a,'shoot')",
):
    assert token in html, f"missing gameplay action trigger: {token}"
assert "function animSc(c,tg,dt,t)" in html, "procedural fallback must remain"
assert "if(!entry||!entry.an||entry.an.dead)return false" in models, "dead-state guard missing"
assert "if(!action){" in models and "a.fallbackTimer=a.fallbackDuration" in models, "missing-clip procedural action fallback missing"
kaykit = root / "app/src/main/assets/www/models/characters/kaykit_v1_2/Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb"
license = root / "app/src/main/assets/www/models/characters/kaykit_v1_2/License.txt"
assert kaykit.is_file(), "bundled KayKit GLB fallback is missing"
assert license.is_file() and "CC0" in license.read_text(encoding="utf-8"), "KayKit CC0 license evidence must remain packaged"
glb = kaykit.read_bytes()
magic, version, total_length = struct.unpack_from("<4sII", glb, 0)
json_length, json_type = struct.unpack_from("<I4s", glb, 12)
assert magic == b"glTF" and version == 2 and total_length == len(glb), "KayKit GLB container is invalid"
assert json_type == b"JSON", "KayKit GLB JSON chunk is missing"
asset = json.loads(glb[20:20 + json_length].decode("utf-8"))
clip_names = {clip.get("name", "") for clip in asset.get("animations", [])}
for clip_name in ("Idle", "Walk", "Run", "Jump", "Shoot(2h)", "Defeat"):
    assert clip_name in clip_names, f"KayKit GLB clip is missing: {clip_name}"
assert not any("reload" in name.lower() for name in clip_names), "documentation must not imply KayKit provides a reload clip"
assert "KayKit_AnimatedCharacter_v1.2.glb" in models, "compatible KayKit GLB family is not configured"
assert "templates=loaded" in models and "animator(model,template)" in models, "model families must keep separate skeleton-specific animation mixers"
assert "KAYKIT_OPERATORS" in models and "handslotright" in models, "operator model-family and hand-socket mapping is missing"
assert "bots.concat(typeof al" not in models, "per-frame bot/ally array allocation returned"
assert "eachActor((g,i)=>" in models, "allocation-free bot/ally iteration helper is missing"
print("ANIMATION_ACTION_AND_FRAME_ALLOCATION_REGRESSION_CHECKS_OK")
