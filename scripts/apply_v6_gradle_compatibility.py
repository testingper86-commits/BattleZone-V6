#!/usr/bin/env python3
"""Pin BattleZone to an officially supported AGP/KGP/Gradle combination."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
build_file = root / "build.gradle.kts"
if not build_file.is_file():
    raise SystemExit(f"Missing root Gradle plugin declaration: {build_file}")

text = build_file.read_text(encoding="utf-8")
marker = "// BATTLEZONE_V6_GRADLE_COMPATIBILITY_V1 AGP=8.7.3 KGP=2.2.20 GRADLE=8.9"
agp = 'id("com.android.application") version "8.7.3" apply false'
kgp_old = 'id("org.jetbrains.kotlin.android") version "2.0.21" apply false'
kgp_new = 'id("org.jetbrains.kotlin.android") version "2.2.20" apply false'

if marker in text:
    if text.count(agp) != 1 or text.count(kgp_new) != 1:
        raise SystemExit("Compatibility marker exists but plugin declarations do not match the verified pair")
    print("GRADLE_COMPATIBILITY_ALREADY_APPLIED AGP=8.7.3 KGP=2.2.20 GRADLE=8.9")
    raise SystemExit(0)

if text.count(agp) != 1:
    raise SystemExit(f"Expected exactly one AGP 8.7.3 declaration, found {text.count(agp)}")
if text.count(kgp_old) != 1:
    raise SystemExit(f"Expected exactly one KGP 2.0.21 declaration, found {text.count(kgp_old)}")
remaining = text.replace(kgp_old, "", 1)
if re.search(r'id\("org\.jetbrains\.kotlin\.android"\) version "[^"]+" apply false', remaining):
    raise SystemExit("Unexpected duplicate Kotlin Android plugin declaration")

updated = text.replace(kgp_old, kgp_new, 1).rstrip() + "\n\n" + marker + "\n"
build_file.write_text(updated, encoding="utf-8")
print("GRADLE_COMPATIBILITY_PATCHED AGP=8.7.3 KGP=2.2.20 GRADLE=8.9")
