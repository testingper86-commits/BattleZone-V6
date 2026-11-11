#!/usr/bin/env python3
"""Release-blocking WILDBOUND phase integration and offline package audit."""
from pathlib import Path
import re, subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
www = root / "app/src/main/assets/www"
workflow = (root / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
index = (www / "index.html").read_text(encoding="utf-8")
def read(rel):
    path = www / rel
    if not path.is_file(): raise SystemExit(f"Missing release module: {rel}")
    return path.read_text(encoding="utf-8")
runtime = read("js/wildbound/rendering/runtime.js")
combat = read("js/wildbound/gameplay/combat.js")
audio = read("js/wildbound/audio/audio.js")
ai = read("js/wildbound/ai/monster-ai.js")
ui = read("js/wildbound/ui/interface.js")
world = read("js/wildbound/world/world.js")
save = read("js/wildbound/backend/save.js")
required_markers = {
    "premium headquarters": "WILDBOUND_PREMIUM_HEADQUARTERS_V1" in index,
    "monster telegraph combat": "WILDBOUND_MONSTER_TELEGRAPH_COMBAT_V1" in ai,
    "monster archetype profiles": "WILDBOUND_MONSTER_ARCHETYPE_PROFILES_V1" in ai,
    "monster ambient patrol": "WILDBOUND_MONSTER_AMBIENT_PATROL_V1" in ai,
    "boss windup": "WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1" in ai,
    "hunt tracking lifecycle": "WILDBOUND_HUNT_TRACKING_LIFECYCLE_V1" in runtime,
    "Blackpine canopy wind": "WILDBOUND_BLACKPINE_CANOPY_WIND_V1" in world,
    "distinct hunt contract": "WILDBOUND_DISTINCT_HUNT_CONTRACT_V1" in save,
    "persisted rank": "WILDBOUND_PERSISTED_RANK_PROGRESSION_V1" in save,
    "perfect dodge": "WILDBOUND_PERFECT_DODGE_V1" in combat,
    "render recovery": "WILDBOUND_RENDER_RECOVERY_V1" in runtime,
    "namespace final guard": "WILDBOUND_NAMESPACE_FINAL_GUARD_V1" in runtime,
    "phase 10 headquarters": "WILDBOUND_PREMIUM_HEADQUARTERS_V1" in ui,
    "pooled VFX": "WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1" in runtime,
    "audio lifecycle": "WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1" in audio,
    "dodge VFX event": "WILDBOUND_DODGE_VFX_EVENT_V1" in combat,
}
for name, ok in required_markers.items(): print(("PASS" if ok else "FAIL"), "phase marker:", name)
if not all(required_markers.values()): raise SystemExit("WILDBOUND_PHASE_MARKER_AUDIT_FAILED")
ordered = [
 "apply_wildbound_transformation.py", "apply_wildbound_premium_headquarters.py",
 "apply_wildbound_monster_telegraph.py", "apply_wildbound_monster_archetypes.py",
 "apply_wildbound_hollow_king_windup.py", "apply_wildbound_monster_patrol.py",
 "apply_wildbound_hunt_tracking.py", "apply_wildbound_distinct_hunt_contract.py",
 "apply_wildbound_persisted_rank.py", "apply_wildbound_camera_control.py",
 "apply_wildbound_playable_prototype.py", "apply_wildbound_perfect_dodge.py",
 "apply_wildbound_blackpine_wind.py", "apply_wildbound_startup_recovery.py",
 "apply_wildbound_vfx_audio_performance.py", "apply_wildbound_render_recovery.py",
 "apply_wildbound_namespace_final_guard.py",
]
positions = [workflow.find(name) for name in ordered]
if any(p < 0 for p in positions) or positions != sorted(positions):
    raise SystemExit("WILDBOUND_TRANSFORMATION_ORDER_FAILED: missing or out-of-order transformation")
print("PASS all gameplay, visual, audio and reliability transformations are ordered")
if re.search(r"(?m)^  push:", workflow) or "workflow_dispatch:" not in workflow:
    raise SystemExit("WILDBOUND_BUILD_POLICY_FAILED: intermediate push builds are enabled")
print("PASS APK workflow is manual-dispatch only")
if any(x in manifest for x in ("android.permission.INTERNET","android.permission.ACCESS_NETWORK_STATE","android.permission.ACCESS_WIFI_STATE")):
    raise SystemExit("WILDBOUND_OFFLINE_MANIFEST_FAILED")
if "connect-src 'self'" not in index or re.search(r"https?://", index):
    raise SystemExit("WILDBOUND_OFFLINE_CSP_FAILED")
print("PASS offline manifest and local-only entrypoint")
asset_manifest = www / "PROCEDURAL_ASSET_PROVENANCE.json"
model = www / "models/characters/kaykit_v1_2/Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb"
license_file = www / "models/characters/kaykit_v1_2/License.txt"
if not asset_manifest.is_file() or not model.is_file() or not license_file.is_file():
    raise SystemExit("WILDBOUND_ASSET_PROVENANCE_FAILED")
print("PASS retained rigged character and procedural texture provenance")
for path in (www / "js/wildbound").rglob("*.js"):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode: raise SystemExit(f"JavaScript syntax failed: {path}\n{result.stderr}")
print("PASS all WILDBOUND JavaScript modules parse")
print("WILDBOUND_RELEASE_INTEGRATION_OK", len(required_markers), "phase markers")
