#!/usr/bin/env python3
"""Pin a supported Android toolchain and add resilient Maven Central mirrors."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
build_file = root / "build.gradle.kts"
settings_file = root / "settings.gradle.kts"
if not build_file.is_file():
    raise SystemExit(f"Missing root Gradle plugin declaration: {build_file}")
if not settings_file.is_file():
    raise SystemExit(f"Missing Gradle repository settings: {settings_file}")

text = build_file.read_text(encoding="utf-8")
settings = settings_file.read_text(encoding="utf-8")
marker_v1 = "// BATTLEZONE_V6_GRADLE_COMPATIBILITY_V1 AGP=8.7.3 KGP=2.2.20 GRADLE=8.9"
marker = "// BATTLEZONE_V6_GRADLE_COMPATIBILITY_V2 AGP=8.7.3 KGP=2.2.20 GRADLE=8.9 MAVEN_MIRRORS=google-storage,repo1"
settings_marker = "// BATTLEZONE_V6_MAVEN_MIRRORS_V1"
agp = 'id("com.android.application") version "8.7.3" apply false'
kgp_old = 'id("org.jetbrains.kotlin.android") version "2.0.21" apply false'
kgp_new = 'id("org.jetbrains.kotlin.android") version "2.2.20" apply false'
mirrors = [
    'maven { url = uri("https://maven-central.storage-download.googleapis.com/maven2") }',
    'maven { url = uri("https://repo1.maven.org/maven2") }',
]

if text.count(agp) != 1:
    raise SystemExit(f"Expected exactly one AGP 8.7.3 declaration, found {text.count(agp)}")
if kgp_new not in text:
    if text.count(kgp_old) != 1:
        raise SystemExit(f"Expected exactly one KGP 2.0.21 declaration, found {text.count(kgp_old)}")
    remaining = text.replace(kgp_old, "", 1)
    if re.search(r'id\("org\.jetbrains\.kotlin\.android"\) version "[^"]+" apply false', remaining):
        raise SystemExit("Unexpected duplicate Kotlin Android plugin declaration")
    text = text.replace(kgp_old, kgp_new, 1)
elif text.count(kgp_new) != 1:
    raise SystemExit("Unexpected duplicate Kotlin Android plugin declaration")

if settings_marker not in settings:
    if settings.count("repositories {") != 2:
        raise SystemExit(f"Expected exactly two Gradle repository blocks, found {settings.count('repositories {')}")
    for mirror in mirrors:
        if mirror in settings:
            raise SystemExit("Partial Maven mirror configuration detected; refusing duplicate repository insertion")
    settings = settings.replace(
        "        google()",
        "        google()\n        " + mirrors[0] + "\n        " + mirrors[1],
        2,
    )
    settings = settings.rstrip() + "\n\n" + settings_marker + "\n"
else:
    for mirror in mirrors:
        if settings.count(mirror) != 2:
            raise SystemExit(f"Maven mirror marker exists but repository count is invalid: {mirror}")

if marker_v1 in text:
    text = text.replace(marker_v1, marker, 1)
elif marker not in text:
    text = text.rstrip() + "\n\n" + marker + "\n"

build_file.write_text(text, encoding="utf-8")
settings_file.write_text(settings, encoding="utf-8")
print("GRADLE_COMPATIBILITY_PATCHED AGP=8.7.3 KGP=2.2.20 GRADLE=8.9 MAVEN_MIRRORS=google-storage,repo1")
