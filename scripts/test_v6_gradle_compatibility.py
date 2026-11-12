#!/usr/bin/env python3
"""Regression tests for the Android toolchain pin and resilient Maven mirrors."""
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).with_name("apply_v6_gradle_compatibility.py")
VALID = '''plugins {\n    id(\"com.android.application\") version \"8.7.3\" apply false\n    id(\"org.jetbrains.kotlin.android\") version \"2.0.21\" apply false\n}\n'''
SETTINGS = '''pluginManagement {\n    repositories {\n        google()\n        mavenCentral()\n        gradlePluginPortal()\n    }\n}\ndependencyResolutionManagement {\n    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)\n    repositories {\n        google()\n        mavenCentral()\n    }\n}\nrootProject.name = \"BattleZoneAndroid\"\ninclude(\":app\")\n'''

def run(root: Path, expected: int) -> subprocess.CompletedProcess:
    result = subprocess.run([sys.executable, str(SCRIPT), str(root)], text=True, capture_output=True)
    assert result.returncode == expected, (result.stdout, result.stderr)
    return result

with tempfile.TemporaryDirectory(prefix="bz-gradle-compat-") as temp:
    root = Path(temp)
    build = root / "build.gradle.kts"
    settings = root / "settings.gradle.kts"
    build.write_text(VALID, encoding="utf-8")
    settings.write_text(SETTINGS, encoding="utf-8")
    first = run(root, 0)
    patched = build.read_text(encoding="utf-8")
    repositories = settings.read_text(encoding="utf-8")
    assert 'id("org.jetbrains.kotlin.android") version "2.2.20" apply false' in patched
    assert patched.count("BATTLEZONE_V6_GRADLE_COMPATIBILITY_V2") == 1
    assert repositories.count("https://maven-central.storage-download.googleapis.com/maven2") == 2
    assert repositories.count("https://repo1.maven.org/maven2") == 2
    assert repositories.count("BATTLEZONE_V6_MAVEN_MIRRORS_V1") == 1
    second = run(root, 0)
    assert "MAVEN_MIRRORS=google-storage,repo1" in second.stdout
    assert build.read_text(encoding="utf-8") == patched
    assert settings.read_text(encoding="utf-8") == repositories

with tempfile.TemporaryDirectory(prefix="bz-gradle-incompat-") as temp:
    root = Path(temp)
    build = root / "build.gradle.kts"
    settings = root / "settings.gradle.kts"
    build.write_text(VALID.replace('version "8.7.3"', 'version "8.8.0"'), encoding="utf-8")
    settings.write_text(SETTINGS, encoding="utf-8")
    before = build.read_text(encoding="utf-8")
    result = run(root, 1)
    assert "Expected exactly one AGP 8.7.3" in result.stderr
    assert build.read_text(encoding="utf-8") == before

print("GRADLE_COMPATIBILITY_TESTS_OK pair=AGP8.7.3_KGP2.2.20_Gradle8.9 mirrors=google-storage,repo1 idempotent=true fail_closed=true")
