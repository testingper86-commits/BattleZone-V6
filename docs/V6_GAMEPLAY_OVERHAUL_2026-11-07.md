# Battle Zone V6.1 Gameplay Overhaul

**Target branch:** `feature/offline-pairing-removal`
**Android version:** `1.2.0` / versionCode `3`
**Runtime:** offline-only Kotlin Android shell with local WebView and Three.js r128 assets.

## Implemented source changes

- **Aircraft jump and weapons:** the operator deploys with two owned weapon slots; the equipped weapon is synchronized to the character rig, remains visible in third person during the jump, and can still be swapped for ground pickups.
- **Controls:** RUN is hold-to-sprint with pointer capture, release, cancel, lost-capture and app-focus recovery. PEEK shifts the third-person shoulder camera. Existing swap/aim/fire/vehicle actions remain wired. Context-aware styling dims controls not needed for the current movement/vehicle state while keeping active controls readable.
- **Lobby:** a final viewport/safe-area layout gives settings and map selection separate scroll regions, reserves the center lane for the character preview, and separates Deploy from navigation.
- **World graphics:** the existing water mesh receives animated vertex displacement and fragment shimmer; trees gain merged roots/branches; grass uses a bounded instanced draw call; vehicles receive grille, lamps, rails, mirrors and wheel-hub detail. These are procedural additions and introduce no remote runtime assets.
- **Character models:** the existing Kenney FBX and CC0 KayKit GLB are loaded as separate templates with separate animation mixers. Seven named operators use KayKit, the other operators use the Kenney model with four existing CC0 skin textures and individual tint profiles, and 25% of AI actors use KayKit deterministically. Weapons attach to Kenney `RightHand` or KayKit `handSlotRight`; Kenney arms receive a two-hand weapon-ready locomotion pose.
- **Voice:** existing character-specific local voice files are routed for spawn, combat, reload, low health, cover, victory and defeat with priority/cooldown and mute handling. The current voice pack license remains unconfirmed; no new audio files are added.

## Scope and honest limits

- The roster has 17 visual operator profiles across **two** rigged model families. It does not contain 17 independently modelled character meshes.
- KayKit has shooting/defeat clips but no reload clip; the existing reload fallback remains. Kenney retains its available idle/run/jump clips and the procedural weapon-ready pose.
- Character grip orientation, lobby alignment, touch ergonomics, graphics quality and frame pacing still require physical Android QA. Static checks cannot prove those device behaviors.
- No network matchmaking, accounts, remote runtime assets or new permissions are introduced. All gameplay assets remain local.

## Automated validation

The CI pipeline applies the three V6.1 patchers after offline/security/build hardening and runs `test_battlezone_v6_overhaul.py`, existing animation/build-hardening regressions, JavaScript syntax checks, Android JVM unit tests, and debug/unsigned-release APK assembly. A green workflow is build/static verification, not a substitute for testing on the target phone.
