# Battle Zone V6 Offline

This repository contains the source archives and CI build workflow for **Battle Zone V6 Offline only**. It is kept separate from Battle Zone V6 Online and all unrelated projects.

## Canonical source and architecture

- Canonical archive for CI: `BattleZone_V6_GitHub_Actions_Ready.zip`.
- `BattleZone_V6_Cloud_Build_Ready.zip` is preserved as an original archive but is not extracted by CI; the two archives differ and must not be overlaid.
- The verified Android package is Kotlin/Gradle + Android WebView hosting an HTML/JavaScript Three.js game. It is not a native 3D engine project.
- All GitHub repository, branch, commit, CI, APK and artifact operations for this project are routed through Composio.

## Offline-only patch

The workflow extracts only the canonical Actions archive, then runs `scripts/apply_offline_pairing_removal.py`. The patch removes the local LAN/device-pairing UI, JavaScript bridge, TCP/UDP socket/discovery code, remote-player relay, Android network permissions and obsolete multiplayer source/docs. Offline Battle Royale, TDM, FFA, AI enemies, TDM teammates and other local gameplay are retained.

The patch script also copies a source README, validator, and removal record into the patched Android project. It is safe to run a second time on an already patched source tree.

## Verified preparation documents

- `scripts/ASSET_INVENTORY.md` records the original asset tree, runtime references, SHA-256 duplicates and license/provenance gaps.
- `scripts/ANDROID_GAMEPLAY_QA_MATRIX.md` defines the physical Android release test matrix.
- The patcher copies both documents into the patched Android source artifact so they travel with the APK source.

## CI outputs

A successful GitHub Actions run publishes two artifacts:

- `BattleZone-debug-APK` — assembled debug APK.
- `BattleZone-Offline-Patched-Source` — the canonical source archive after the offline-only patch and dependency preparation.

A successful build proves compilation and packaging only. Physical Android device tests are still required for offline launch, gameplay, WebGL/GPU behavior, controls, performance, memory and thermal stability.
