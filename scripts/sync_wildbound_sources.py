#!/usr/bin/env python3
"""Install maintained WILDBOUND runtime modules into the generated Android source tree."""
from pathlib import Path
import shutil
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
print(f"WILDBOUND_CANONICAL_SOURCES_INSTALLED {len(files)} modules; validator synchronized")
