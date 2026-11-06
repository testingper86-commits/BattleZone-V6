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
- Test orientation, pause/resume, WebView renderer recovery, frame pacing, memory and thermal behavior on physical Android devices.
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
