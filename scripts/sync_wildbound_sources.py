#!/usr/bin/env python3
"""Install maintained WILDBOUND runtime modules into the generated Android source tree."""
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
source_root = Path(__file__).resolve().parent / "wildbound-source"
files = (
    ("js/wildbound/rendering/runtime.js", "app/src/main/assets/www/js/wildbound/rendering/runtime.js"),
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
print(f"WILDBOUND_CANONICAL_SOURCES_INSTALLED {len(files)} modules")
