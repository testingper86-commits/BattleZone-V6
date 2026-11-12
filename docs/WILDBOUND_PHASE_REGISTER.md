# WILDBOUND delivery phase register

This register separates source implementation, automated verification and physical-device acceptance. A CI pass does not certify photorealistic art quality or Android thermal behavior.

| Phase | Scope | Repository status | Release evidence / remaining gate |
|---|---|---|---|
| 1 | Repository and modular architecture | Implemented | Six canonical WILDBOUND modules synchronized after transformation |
| 2 | Offline core, state and persistence | Implemented | Local-only manifest, strict CSP, URI validation, backup recovery and offline tests |
| 3 | Hunter and character presentation | Source integrated | CC0 KayKit rig, animation clips and procedural fallback; high-fidelity art pass remains |
| 4 | Monster AI and archetypes | Source integrated | Four distinct procedural archetypes, patrol animation, bounded movement and telegraphed attacks |
| 5 | Combat and hunting | Source integrated | Directional hit checks, weak points, stamina, perfect dodge and counter-window feedback |
| 6 | Blackpine environment | Source integrated | Instanced environment, generated PBR ground, haze and two-axis canopy wind |
| 7 | Hollow King encounter | Source integrated | Three phases, four-arm boss rig, phase-one heavy swing, projectile and ground-slam attacks |
| 8 | Missions and game modes | Implemented | Offline contract, briefing and playable vertical-slice checks |
| 9 | Progression and equipment | Implemented | XP/rank persistence, local inventory and progression checks |
| 10 | Headquarters and frontend | Implemented | Responsive lobby, Field Record, bestiary, inventory and touch controls |
| 11 | Graphics and VFX | Source integrated | 72-slot pooled effects and WebGL recovery; GPU/frame-pacing QA pending |
| 12 | Animation and audio | Source integrated | Hunter rig animation, articulated procedural monsters and 12-voice audio cap; physical audio-focus QA pending |
| 13 | Android performance and thermal | Source integrated | Instancing, quality profiles, bounded particles/voices and viewport recovery; profiler/thermal QA pending |
| 14 | Integration and QA | CI gates integrated | Canonical source, offline, startup, render, AI and release integration tests; device matrix pending |
| 15 | Release and distribution | Build candidate pending | Final post-implementation APK build, offline clean rebuild, signing and device acceptance pending |

## Single-build policy

The Android APK workflow is `workflow_dispatch` only. Source implementation and static/regression validation complete first. Dispatch the final APK build only after the source commit is frozen. If CI fails, fix the underlying source/workflow cause, rerun the targeted regression, and rebuild.

## Release blockers

- Production signing requires owner-managed keystore secrets; never place signing credentials in chat or source control.
- Physical Android acceptance requires low-, mid- and high-tier devices listed in `scripts/ANDROID_GAMEPLAY_QA_MATRIX.md`.
- WebGL context restoration, frame pacing, memory, audio focus and thermal behavior must be measured on actual devices.
- Photorealistic AAA character/creature assets and motion-capture animation are not supplied by the current procedural models; a stylized playable vertical slice must not be described as a finished photorealistic AAA game.
- Final approval requires APK SHA-256, asset provenance ledger and test evidence to reference the same commit/build.
