# Battle Zone V6 — Build #45 Deep Audit and Build #46 Fixes

**Audit baseline:** `feature/offline-pairing-removal` at `1dea8fe3460c796a65245a78703336ae640f08b2`  
**Build:** GitHub Actions run `42350192874`, run number `45`, completed successfully on 2026-11-07.

## Build #45 findings

1. **The Android unit-test tasks were empty.** Both `:app:testDebugUnitTest` and `:app:testReleaseUnitTest` reported `NO-SOURCE`. The green build therefore proved APK assembly, not execution of Android JVM tests.
2. **The WebView path guard decoded the URI path only once.** Nested percent-encoded dot segments could survive that check. The guard needed a separately testable policy and traversal regression cases.
3. **Build-time JavaScript dependencies were not integrity-pinned.** The downloader checked size/content markers, accepted pre-existing files by size alone, and used unchecked `renameTo` calls. A different or damaged CDN response could be packaged.
4. **Dead model-download code remained.** The `soldier.glb` fallback was absent from the source archive and its optional downloader was not attached to `preBuild`. NURBS helper downloads were also unused by the active Kenney/KayKit model paths; Build #45 logs showed the optional NURBSCurve fetch failing.
5. **The APK carried unused model and starter assets.** The KayKit package included alternate FBX/DAE/OBJ/Gltf samples, logos and documentation even though runtime selected one GLB. The environment starter pack was not referenced by runtime code.
6. **The patched-source artifact included build caches.** The exclusion pattern did not match the root `.gradle` directory, so Gradle execution-history files leaked into the source ZIP.
7. **The Android package version was stale.** Build metadata still declared `versionCode = 1` and `versionName = "1.0"`.

## Changes applied by the Build #46 source transformation

- Added `OfflineAssetPolicy`, a pure Kotlin WebView-origin policy. It checks HTTPS, the exact Android asset host, allowed ports, user-info absence, `/assets/` root and traversal after repeated percent decoding; encoded slash and backslash traversal is rejected.
- Added four JUnit JVM tests covering trusted-origin acceptance, invalid origins, literal/encoded traversal, malformed paths and nested encoding.
- Added a CI preflight that fails if `app/src/test` contains no Kotlin test source. The existing Gradle test tasks can no longer silently pass as `NO-SOURCE`.
- Pinned SHA-256 hashes for Three.js r128, GLTFLoader, FBXLoader, SkeletonUtils and fflate. Existing files are re-verified; new downloads are hash-checked and installed with `Files.move(..., REPLACE_EXISTING)`. A mismatched or unavailable required library fails the build.
- Removed the absent soldier fallback, its unused downloader and unused NURBS download entries. Kenney remains primary, KayKit GLB remains its compatible fallback, and procedural characters remain the final fallback.
- Pruned unreferenced KayKit files from the Android build workspace, retaining only `KayKit_AnimatedCharacter_v1.2.glb` and `License.txt`. The retained pair is 460,406 bytes versus 12,147,671 bytes for the original KayKit directory: **11,687,265 bytes removed**.
- Removed the unreferenced `assets/environment` starter pack from the APK build workspace. The canonical source ZIP remains unchanged.
- Excluded root and nested `.gradle`, `.kotlin`, `build`, Git and temporary download files from the patched-source artifact, with a post-package cache-leak check.
- Incremented Android metadata to `versionCode = 2`, `versionName = "1.1.0"`.

## Verification performed before commit

- Re-extracted the canonical GitHub Actions source ZIP into a clean temporary workspace.
- Replayed the complete ordered source-patch pipeline, including the new build-hardening transformation.
- `validate_project.py` passed, including local resource resolution and Node.js syntax checks for all inline and packaged JavaScript.
- All repository Python regression scripts passed against the transformed source, including adaptive AI, graphics, animation asset/clip checks, WebView security, GPU recovery, progression, squad commands, tactical UI, voice startup and the new build-hardening checks.
- The transformed source contains a real `app/src/test/.../OfflineAssetPolicyTest.kt` test class. Android Gradle compilation and execution of these JUnit tests must still be confirmed by the next GitHub Actions run.

## Remaining verification boundary

- This workbench has no Java/Android SDK, so it could not run the Android Gradle build locally. The next GitHub Actions run must compile the new Kotlin policy, execute both unit-test variants, assemble debug/release APKs and verify the cleaned source artifact.
- Physical-device gameplay, WebView renderer recovery, animation rendering, FPS, memory, thermal behavior and offline runtime checks remain unverified until the APK is installed and exercised on Android hardware.
- The release APK remains unsigned; production signing requires the owner's protected signing mechanism.
- Build-time dependency retrieval still needs internet access. The installed APK remains offline-only: runtime libraries are packaged locally and the manifest has no network permissions.
