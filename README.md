# WILDBOUND

**An offline third-person supernatural monster-hunting game for Android.**

WILDBOUND is a local-only hunting experience built around one playable hunter, Blackpine Reserve, three anomaly archetypes, a multi-phase Hollow King encounter, tactical melee and ether abilities, headquarters systems, progression and recoverable local saves.

## Build

Use the repository's `Build WILDBOUND Offline Android APK` GitHub Actions workflow as the canonical build path. It assembles the Android source, installs the six canonical WILDBOUND modules, applies the final WebView security and recovery layers, verifies the asset ledger, runs offline/gameplay regression checks, and builds debug plus unsigned release APKs. The installed game has no network permission and rejects non-local WebView requests.

## Runtime architecture

See `docs/WILDBOUND_ARCHITECTURE.md` and `docs/WILDBOUND_PHASE_REGISTER.md`. The runtime is separated into core, backend, gameplay, AI, actors, world, rendering, UI and audio modules. Runtime source-of-truth files live under `scripts/wildbound-source/js/wildbound/` and are synchronized into the Android project by `scripts/sync_wildbound_sources.py` after the base transformation.

## Current playable slice

- Startup-safe lobby and renderer recovery; the real lobby remains available if WebGL creation fails.
- Camera-relative movement with an independent touch/mouse orbit camera, bounded vertical look and pointer/focus-loss recovery.
- One playable hunter using the bundled KayKit CC0 skinned character, local animation clips and a procedural fallback.
- Grave Stalker, Wraithcaller and Ironmaw with distinct articulated procedural silhouettes, attack profiles, patrols and telegraphed attacks.
- Four-arm Hollow King with a three-phase encounter, phase-one heavy swing, projectile attack and ground slam.
- Blackpine Reserve with instanced vegetation/rocks, generated PBR ground, haze, canopy wind and damaging corrupted-ground hazards.
- Strike combos, stamina, dodge, perfect-dodge counter windows, ether rift, ultimate charge, weak points, tracking and field tonics.
- Headquarters, bestiary, inventory, disciplines, mission results, local progression and versioned save recovery.
- Adaptive graphics profiles, a bounded 72-slot GPU particle pool and a 12-voice procedural audio limit.

## Validation and scope

CI validates canonical source synchronization, actor constructors, monster AI, boss phases, camera controls, combat feedback, WebGL recovery, Android offline security, project integrity and asset provenance before producing APK artifacts.

This is a playable offline vertical slice, not a finished photorealistic AAA production. The current monster silhouettes are procedural, and the hunter uses a stylized CC0 character asset. Photorealistic creature/hunter assets, motion-capture polish and physical Android frame-time, memory, audio-focus and thermal acceptance remain production gates.
