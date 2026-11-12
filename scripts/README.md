# Battle Zone V6 Offline — Android project

This is the **Offline** Battle Zone V6 Android package. The current architecture is a Kotlin/Gradle Android application that renders the game through Android WebView using a local HTML/JavaScript Three.js runtime. It is not a native 3D engine project.

## Offline scope

- Single-device offline gameplay; no account, matchmaking, LAN rooms, device pairing, Wi-Fi discovery, TCP/UDP sockets, or Bluetooth transport.
- Battle Royale with the five-phase shrinking safe zone.
- Offline Team Deathmatch with three AI teammates and a 25-kill target.
- Offline Free-for-All with a 20-kill target.
- Local maps, weapons, vehicles, bots, player progression and settings remain part of the game.
- The Android manifest has no network permissions. Game assets are served from the app package through AndroidX WebViewAssetLoader.

Removing local device pairing does not remove offline gameplay or AI-controlled opponents/teammates.

## Build requirements

- Android Studio with Android SDK Platform 35.
- JDK 17.
- Gradle 8.9 (the wrapper/CI configuration pins this version).
- Network access during the build may be needed for Gradle dependencies and the pinned Three.js r128 runtime download. The resulting APK packages the runtime and game assets locally and does not need network permission to run.

## Build the APK

1. Open the extracted Android project folder in Android Studio.
2. Allow Gradle sync to complete using JDK 17.
3. Run **Build > Build APK(s)** or execute `./gradlew :app:assembleDebug`.
4. The debug APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

The GitHub Actions workflow uses only `BattleZone_V6_GitHub_Actions_Ready.zip` as its canonical source archive, applies the tracked Offline feature-removal script, runs static validation and unit tests, then builds the APK. It also publishes the patched source as a separate build artifact.

## Verification checklist

- Install and launch with airplane mode enabled.
- Confirm the lobby and match-start flow work without network permissions.
- Test Battle Royale, Team Deathmatch and Free-for-All.
- Test movement, camera, firing, reload, weapon switching and touch controls.
- Test AI enemies, TDM allies, respawn, revive, safe-zone phases and match completion.
- Test sound, localStorage progression and settings persistence.
- Test orientation, pause/resume, WebView renderer recovery, frame pacing, memory and thermal behavior on physical Android devices. Verify that releasing the lobby preview WebGL context at deployment does not trigger the gameplay GPU-loss screen.
- Confirm no pairing, LAN discovery, room-hosting or room-joining UI or runtime code remains.

A successful Gradle build proves APK assembly, not gameplay correctness. Physical-device testing is required for WebGL/GPU compatibility, controls, AI behavior, performance, memory, thermal behavior and stability.

Original Battle Zone models, maps, weapons, textures, effects, animations, audio and UI should be preserved wherever possible. Third-party assets are gap-fillers only; verify each exact asset's license and retain its license/attribution notice.

## Preparation records

- `ASSET_INVENTORY.md` — verified original source inventory, runtime references, duplicate hashes and license/provenance gaps.
- `ANDROID_GAMEPLAY_QA_MATRIX.md` — physical-device offline gameplay and performance release gate.

## Player hub career screens

The build applies `apply_offline_hub_completion.py` after the offline/gameplay patches. It adds device-local career statistics and a 50-match history sourced from actual match-completion counters. Replay playback is explicitly unavailable until deterministic replay recording exists.


## V6 command-deck enhancement

The `feature/battlezone-v6-enhancement` branch layers a responsive command-deck home/lobby redesign over the existing V6 controls, caps the lobby operator preview at 20 fps and releases its WebGL context at deployment, and reduces squad AI overhead by caching target acquisition and moving LOS checks into firing cooldowns. Assault, support and flank roles use different target priorities. The patch does not replace the Android/WebView/Three.js architecture or change offline-only behavior.

## Live squad orders

The final CI transformation adds four persistent offline squad commands: Regroup, Focus, Flank and Hold. Focus selects the nearest living enemy within 120 world units and directs allies to that shared target; if no target is in range, the order safely falls back to Regroup. Regroup pulls distant allies back before they resume combat, Flank applies flank movement to the squad, and Hold stops idle allies from drifting while preserving engagement behavior. The compact touch controls use safe-area insets, visible focus states and reduced-motion-aware styling. The selection is stored locally as `bzSquadOrder`.

`apply_v6_squad_command_system.py` is idempotent and fails closed if any required source anchor changes. `test_v6_squad_command_system.py` verifies the UI, persistence and AI integration.


## Gameplay GPU context ownership

`apply_v6_gpu_recovery.py` attaches `webglcontextlost` and `webglcontextrestored` handlers only to the main gameplay canvas (`#c`). The lobby character preview uses a separate renderer and intentionally calls `forceContextLoss()` when deployment starts to return GPU resources. Treating every renderer's context-loss event as a game failure caused a false fatal screen on deployment. The focused regression test now asserts the gameplay-canvas guard and preserves the preview renderer's intentional release.

Android owns the landscape orientation through `android:screenOrientation="landscape"` in the manifest. The game page no longer calls `screen.orientation.lock()`, which is unsupported or rejected on some WebView/device combinations.


## Final lobby alignment

`apply_v6_lobby_alignment.py` is the last UI transformation in CI. It copies `v6-lobby-alignment.css` into the packaged game and links it after all existing lobby styles, giving the viewport/safe-area layout a single final cascade authority. It aligns the player/status header, central command hero, left configuration, right battlefield list, character preview, skins action, deploy button and the operator-service rail, including both the original four-item layout and the seven-item layout shown in device captures. Dedicated compact-landscape, short-height and narrow-width rules constrain overflow and preserve touch access. `test_v6_lobby_alignment.py` checks these invariants and stylesheet ordering.

The GPU recovery handler now preserves the current match when WebGL reports a restored context: it resizes the renderer and lets Three.js rebuild GPU resources instead of reloading the document. The 10-second failure fallback is retained only for a context that does not return.

## Build hardening and Android JVM tests

The final CI transformation `apply_v6_build_hardening.py` pins the SHA-256 of runtime Three.js libraries, removes the absent soldier-model downloader and unreferenced asset packs, centralizes WebView URI validation in `OfflineAssetPolicy`, adds JUnit coverage, and increments Android version metadata. `test_v6_build_hardening.py` checks the transformed source and packaging assumptions. The workflow also fails if the Android test source set is empty and rejects build-cache files in the patched-source artifact.

## Battle Zone V6.1 gameplay overhaul

The Android workflow applies three final source transformations after the offline/security/build-hardening steps:

1. `apply_battlezone_v6_overhaul.py` fixes the starting weapon loadout and aircraft-jump presentation, adds hold-to-run and shoulder-peek behavior, applies a single responsive lobby layout authority, adds bounded water/tree/grass/vehicle detail, and routes contextual voice barks through the existing local character voice packs.
2. `apply_battlezone_v6_rigged_weapons.py` mounts the equipped weapon to the animated Kenney `RightHand`, updates it on swap, removes the floating proxy gun, and applies a stable two-hand armed run pose after locomotion animation.
3. `apply_battlezone_v6_multimodel.py` loads the Kenney FBX and CC0 KayKit GLB as separate rigged templates. Seven named operators use the KayKit model; the rest use the Kenney model and its four existing skin textures. A deterministic 25% of AI actors uses KayKit. Each template has its own animation mixer and hand-socket mapping.

The existing 17 character voice folders remain local. Their license provenance is still unconfirmed in `ASSET_INVENTORY.md`; the event router improves use/cooldown/priority but does not upgrade that license status. The roster contains 17 visual profiles across two rigged model families, not 17 independently modelled 3D meshes.

`test_battlezone_v6_overhaul.py` covers loadout/jump, input lifecycle, control visibility, lobby panel boundaries, procedural graphics, voice routing, rigged weapon attachment, and model-family separation. Physical Android playtesting remains required for touch feel, final visual alignment, weapon grip alignment and frame rate.
