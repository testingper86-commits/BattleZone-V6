#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
gradle = (root / "app/build.gradle.kts").read_text(encoding="utf-8")
activity = (root / "app/src/main/java/com/example/battlezone/MainActivity.kt").read_text(encoding="utf-8")
policy = (root / "app/src/main/java/com/example/battlezone/OfflineAssetPolicy.kt").read_text(encoding="utf-8")
models = (root / "app/src/main/assets/www/js/models.js").read_text(encoding="utf-8")
tests = root / "app/src/test/java/com/example/battlezone/OfflineAssetPolicyTest.kt"
kaykit = root / "app/src/main/assets/www/models/characters/kaykit_v1_2"
assert "BATTLEZONE_V6_BUILD_HARDENING_V1" in gradle
assert "versionCode = 5" in gradle and 'versionName = "1.2.2"' in gradle
assert 'testImplementation("junit:junit:4.13.2")' in gradle and tests.is_file()
assert "OfflineAssetPolicy.isTrustedAssetUri" in activity
for token in ("URLDecoder.decode", "appassets.androidplatform.net", 'decoded.startsWith("/assets/")', 'it == ".."', "%2e|%2f|%5c"):
    assert token in policy, f"URI policy guard missing: {token}"
for token in ("9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2", "5c15967ba830918a9caea6338712c994c354bccd4edc4569bde411c3ec06a3e6", "a5732b0dcdf530ecfd5ff21eb96e9343fc8e40dd75e548730352e6cfb79342b1", "cc2e2e1a3183ab55169d185565f86f43f80c6dfafe73610d991e741ea990ac1a", "798b397d482f2ff743452362e880f1be4b683c43d7b2db3e8751f7412e7d5f4b"):
    assert token in gradle, f"pinned dependency checksum missing: {token}"
assert "ZipInputStream" not in gradle and "downloadSoldierModels" not in gradle and "NURBSCurve.js" not in gradle and "downloadOptionalLibs" not in gradle and "downloadCharacterRuntimeLibraries" in gradle
assert "Keeping the existing libs/three.min.js" not in gradle and "throw GradleException(msg)" in gradle
assert "soldier.glb" not in models, "dead, absent soldier fallback remains"
assert (kaykit / "License.txt").is_file()
assert (kaykit / "Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb").is_file()
retained_kaykit = {p.relative_to(kaykit) for p in kaykit.rglob("*") if p.is_file()}
assert retained_kaykit == {Path("License.txt"), Path("Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb")}, f"unreferenced KayKit files remain: {retained_kaykit}"
assert not (root / "app/src/main/assets/www/assets/environment").exists()
www = root / "app/src/main/assets/www"
portrait_dir = www / "characters/portraits"
assert not portrait_dir.exists() or not any(p.is_file() for p in portrait_dir.iterdir()), "unused portrait images remain in the APK source"
branding_dir = www / "branding"
assert {p.name for p in branding_dir.iterdir() if p.is_file()} <= {"battle_zone_logo.jpg"}, "unreferenced branding images remain in the APK source"
assert (branding_dir / "battle_zone_logo.jpg").is_file(), "active loading-screen logo was removed"
assert all((www / "loading" / f"boot_scene_{i}.jpg").is_file() for i in (1, 2, 3)), "active loading backgrounds were removed"
assert len(re.findall(r"@Test", tests.read_text(encoding="utf-8"))) >= 4
print("BUILD_HARDENING_AND_ANDROID_UNIT_TEST_REGRESSION_CHECKS_OK")
