# Battle Zone V6 Offline

This repository contains the source archives and CI build workflow for Battle Zone V6 Offline only. It is kept separate from Battle Zone V6 Online and all unrelated projects.

## Canonical source and architecture

- Canonical archive for CI: BattleZone_V6_GitHub_Actions_Ready.zip.
- BattleZone_V6_Cloud_Build_Ready.zip is preserved as an original archive but is not extracted by CI; the two archives differ and must not be overlaid.
- The Android package is Kotlin/Gradle plus Android WebView hosting an HTML/JavaScript Three.js game. It is not a native 3D engine project.
- All GitHub repository, branch, commit, CI, APK and artifact operations for this project are routed through Composio.

## Offline-only patch

The workflow extracts only the canonical Actions archive, then runs the offline pairing-removal stage. That stage removes local LAN/device-pairing UI, JavaScript bridge, TCP/UDP socket/discovery code, remote-player relay, Android network permissions and obsolete multiplayer source/docs. Offline Battle Royale, TDM, FFA, AI enemies, TDM teammates and other local gameplay are retained.

## Verified preparation documents

- scripts/ASSET_INVENTORY.md records the original asset tree, runtime references, SHA-256 duplicates and license/provenance gaps.
- scripts/ANDROID_GAMEPLAY_QA_MATRIX.md defines the physical Android release test matrix.

## CI outputs

A successful GitHub Actions run publishes three artifacts:

- BattleZone-debug-APK: debug APK for device testing.
- BattleZone-release-unsigned-APK: release-variant APK without a distribution signing key.
- BattleZone-Offline-Patched-Source: canonical source after offline, gameplay, reliability and progression-integrity processing.

The release artifact is intentionally unsigned because no production keystore is stored in the repository or available to CI. It must be signed with the owner's protected release key before distribution. A successful build proves compilation and packaging only. Physical Android device tests remain required for offline launch, gameplay, WebGL/GPU recovery, controls, performance, memory and thermal stability.

## Gameplay quality and reliability

The Android workflow applies guarded quality and reliability transformations after offline removal. These include allocation-free actor iteration, throttled HUD/minimap rendering, terrain/POI map detail, procedural combat poses, startup and renderer recovery, safe immersive-mode requests, and bounded lobby preview rendering. GPU-loss recovery is scoped strictly to the gameplay canvas: the lobby preview deliberately releases its own WebGL context at deployment, and that intentional release must never be treated as a gameplay GPU failure. Landscape orientation is owned by the Android activity manifest; the Web page does not call the unsupported browser orientation-lock API.

## Progression and local data integrity

The V6 progression-integrity stage uses one shared local wallet for gameplay and Player Hub, prevents match-start taps from granting rewards, validates imported wallet/profile values, and includes the player profile, offline match history and AI doctrine in backup/restore. All progression remains device-local; there is no account service, remote matchmaking, backend database or online synchronization in this offline build.

The validator and focused regression tests enforce source invariants. The new live squad-order system adds persistent Regroup, Focus, Flank and Hold commands to offline AI teammates; commands directly change ally targeting and movement and are hidden when no squad is deployed. Physical-device performance, gameplay and animation behavior still require device QA.


## Lobby alignment and GPU lifecycle hardening

The final CI stage, `apply_v6_lobby_alignment.py`, loads `v6-lobby-alignment.css` after every prior lobby style. It gives the player/status header, command-deck hero, configuration panel, map selector, character preview, skins action, deploy action and operator navigation one viewport-aware layout with Android safe-area spacing. Landscape short-height and narrow-width layouts have dedicated rules; scrollable panels are bounded and touch targets cannot drift off-screen. The regression suite is `test_v6_lobby_alignment.py`.

On a successful WebGL context restoration, the renderer is resized and allowed to rebuild its resources without reloading the page or resetting the active match. A bounded fatal fallback remains only when the gameplay context never returns. The lobby preview renderer remains isolated from gameplay context-loss reporting.
