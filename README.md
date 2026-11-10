# WILDBOUND

**An offline third-person supernatural hunting game for Android.**

WILDBOUND replaces the former Battle Zone identity with a local-only hunting experience: a 3D hunter, Blackpine Reserve, three anomaly archetypes, a multi-phase Hollow King encounter, tactical melee and ether abilities, headquarters systems, progression and recoverable local saves.

## Build

Open the Android project in Android Studio or run `./gradlew :app:assembleDebug`. The Gradle pre-build task vendors Three.js r128 and optional local GLTF loaders into the APK. The installed game itself has no network permissions and blocks non-local WebView requests.

## Runtime architecture

See `docs/WILDBOUND_ARCHITECTURE.md` and `app/src/main/assets/www/js/wildbound/README.md`. The game runtime is split into core, backend, gameplay, AI, actors, world, rendering, UI and audio modules.

## Current playable slice

- One playable hunter using the bundled KayKit CC0 skinned character and local animation clips, with a procedural fallback
- Grave Stalker, Wraithcaller and Ironmaw AI archetypes
- Three-phase Hollow King boss
- Blackpine Reserve with instanced vegetation, rocks, ward arena and local PBR ground texture
- Strike combos, stamina, dodge, ether rift, ultimate charge, weak points, tracking and field tonics
- Headquarters, bestiary, inventory, disciplines, graphics/audio settings and mission results
- Versioned local save with backup recovery

## Validation

Run `python3 scripts/apply_wildbound_transformation.py <android-project-root>` to install the deterministic transformation into a canonical source extraction, then run `python3 scripts/test_wildbound_vertical_slice.py <android-project-root>`. CI runs these gates before building the APK.

The vertical slice is not represented as a finished large-scale commercial game. Final Android installation and physical-device performance still require device validation.
