#!/usr/bin/env python3
"""Install maintained WILDBOUND runtime modules into the generated Android source tree."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
source_root = Path(__file__).resolve().parent / "wildbound-source"
files = (
    ("js/wildbound/rendering/runtime.js", "app/src/main/assets/www/js/wildbound/rendering/runtime.js"),
    ("js/wildbound/actors/actors.js", "app/src/main/assets/www/js/wildbound/actors/actors.js"),
    ("js/wildbound/ai/monster-ai.js", "app/src/main/assets/www/js/wildbound/ai/monster-ai.js"),
    ("js/wildbound/world/world.js", "app/src/main/assets/www/js/wildbound/world/world.js"),
    ("js/wildbound/audio/audio.js", "app/src/main/assets/www/js/wildbound/audio/audio.js"),
    ("js/wildbound/gameplay/combat.js", "app/src/main/assets/www/js/wildbound/gameplay/combat.js"),
)
for source_relative, target_relative in files:
    source = source_root / source_relative
    target = root / target_relative
    if not source.is_file():
        raise SystemExit(f"Canonical WILDBOUND source is missing: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

validator = root / "validate_project.py"
if validator.is_file():
    content = validator.read_text(encoding="utf-8")
    stale = "pct<.3?3:pct<.65?2:1"
    current = "healthRatio<.3?3:healthRatio<.65?2:1"
    if stale in content:
        content = content.replace(stale, current)
        validator.write_text(content, encoding="utf-8")
    elif current not in content:
        raise SystemExit("Project validator has no recognized multi-phase boss threshold check")
asset_source = source_root / "assets" / "models" / "wildbound"
asset_target = root / "app" / "src" / "main" / "assets" / "www" / "models" / "wildbound"
manifest_path = asset_source / "manifest.json"
if not manifest_path.is_file():
    raise SystemExit(f"Canonical WILDBOUND model manifest is missing: {manifest_path}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("schema") != "wildbound-cc0-model-bundle-v1":
    raise SystemExit("Unsupported WILDBOUND model manifest schema")
required = {"hunter/hunter.glb", "monsters/stalker.glb", "monsters/wraithcaller.glb", "monsters/ironmaw.glb", "monsters/hollow_king.glb", "environment/canopy_01.glb", "environment/canopy_02.glb", "environment/deadwood.glb", "environment/shrub.glb", "environment/fern.glb", "environment/rock.glb", "environment/fern_cluster.glb"}
records = {item.get("path"): item for item in manifest.get("models", [])}
if set(records) != required:
    raise SystemExit(f"WILDBOUND model manifest mismatch: expected {len(required)}, got {len(records)}")
for relative, record in records.items():
    source = asset_source / relative
    if not source.is_file(): raise SystemExit(f"WILDBOUND model is missing: {source}")
    data = source.read_bytes()
    if len(data) != record.get("bytes") or data[:4] != b"glTF" or struct.unpack("<I", data[8:12])[0] != len(data): raise SystemExit(f"WILDBOUND GLB header/length validation failed: {relative}")
    if hashlib.sha256(data).hexdigest() != record.get("sha256"): raise SystemExit(f"WILDBOUND model SHA-256 mismatch: {relative}")
    if record.get("license") != "CC0 1.0 Universal" or not record.get("license_url", "").startswith("https://creativecommons.org/publicdomain/zero/"): raise SystemExit(f"WILDBOUND model license is not verified CC0: {relative}")
asset_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(asset_source, asset_target, dirs_exist_ok=True)
for relative, record in records.items():
    if hashlib.sha256((asset_target / relative).read_bytes()).hexdigest() != record["sha256"]: raise SystemExit(f"WILDBOUND Android model copy verification failed: {relative}")
print(f"WILDBOUND_MODEL_ASSETS_SYNCED {len(records)} GLB files; {sum(item['bytes'] for item in records.values())} bytes; hashes verified")

print(f"WILDBOUND_CANONICAL_SOURCES_INSTALLED {len(files)} modules; validator synchronized")
