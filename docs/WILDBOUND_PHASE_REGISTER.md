# WILDBOUND delivery phase register

This register separates implementation from release evidence. A phase is not device-verified merely because its source patch or CI check exists.

| Phase | Scope | Repository status | Release evidence |
|---|---|---|---|
| 1 | Repository and architecture | Implemented | Canonical transformation and architecture audit |
| 2 | Offline core, state and save infrastructure | Implemented | Offline manifest, save recovery and runtime tests |
| 3 | Hunter, rig and character presentation | Implemented | Bundled CC0 rig, fallback actor and animation integration |
| 4 | Monster AI and creature archetypes | Implemented | Telegraph, archetype, patrol and boss regression suites |
| 5 | Combat and hunting | Implemented | Combat, tracking, perfect dodge and contract regression suites |
| 6 | Blackpine environment and world | Implemented | Procedural PBR provenance, instanced world and canopy wind |
| 7 | Boss encounter | Implemented | Three-phase Hollow King and phase-one windup checks |
| 8 | Mission and game modes | Implemented | Offline contract, briefing and vertical-slice checks |
| 9 | Progression and equipment | Implemented | XP/rank persistence, local inventory and progression checks |
| 10 | Premium lobby and frontend | Implemented | Rank progress, Field Record, responsive layout and accessibility checks |
| 11 | Graphics and VFX | Source implementation integrated | Bounded pooled combat particle effects; Android GPU/frame pacing QA pending |
| 12 | Animation, audio and synchronization | Source implementation integrated | Rigged character animation and lifecycle-safe audio; physical audio-focus QA pending |
| 13 | Android performance and thermal | Source implementation integrated | Bounded particle/voice budgets, instancing and quality profiles; profiler/thermal QA pending |
| 14 | Integration and QA | CI release gates integrated | Final integration audit plus physical-device matrix pending |
| 15 | Release and distribution | Build workflow prepared, final candidate pending | One final APK build, offline clean rebuild, signing and device acceptance pending |

## Single-build policy

The Android APK workflow is workflow_dispatch only. Feature commits and implementation updates do not launch APK builds. All source transformations and their regression checks are assembled in the canonical workflow in dependency order. The final build is dispatched once after implementation is frozen.

## Release blockers

- Production signing requires owner-managed keystore secrets.
- Physical Android acceptance requires the low-, mid- and high-tier device matrix in scripts/ANDROID_GAMEPLAY_QA_MATRIX.md.
- WebGL stability, audio focus, frame pacing, memory and thermal behavior must be measured on actual devices.
- Final release approval requires the APK SHA-256, asset provenance ledger and test evidence to reference the same commit/build.
