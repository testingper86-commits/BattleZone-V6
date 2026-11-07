# Battle Zone V6 — Next-Generation Overhaul

## Implemented in this change

### Live squad command system
- Adds Regroup, Focus, Flank and Hold controls to active matches.
- Focus selects the nearest living enemy within 120 world units and directs all active allies to the same target. If no valid target is available, it safely returns the squad to Regroup.
- Regroup pulls allies farther than 12 world units from the player back toward the player before normal combat resumes.
- Flank changes all active ally movement to the existing flanking behavior.
- Hold prevents idle allies from drifting toward the player while allowing existing combat targeting and firing to continue.
- Persists the selected command in local storage; the default is Regroup.
- Hides controls unless an active match has a living squad member.
- Provides touch-sized controls, keyboard focus visibility, mobile safe-area support and reduced-motion-aware styling.

### Gameplay GPU lifecycle correction
- Restricts WebGL context-loss and context-restoration handling to the main gameplay canvas (`#c`).
- Prevents the lobby character-preview renderer's intentional `forceContextLoss()` during deployment from being misreported as a failed gameplay GPU context.
- Removes the browser orientation-lock request; Android's manifest already owns landscape orientation, avoiding unsupported WebView API warnings.
- Extends `scripts/test_v6_gpu_recovery.py` to guard renderer ownership and the orientation contract.

## Architecture and integration

The Android/Kotlin + WebView + Three.js architecture is retained. The feature is delivered as a deterministic, idempotent source transformation in `scripts/apply_v6_squad_command_system.py`, applied after progression integrity in the canonical GitHub Actions pipeline. No new runtime library or network permission is introduced.

## Verification

- Dedicated regression suite: `scripts/test_v6_squad_command_system.py`.
- Existing project validator and all existing focused regression suites must pass after the full ordered patch pipeline.
- Android debug and unsigned release APK assembly plus debug/release unit-test tasks remain required in GitHub Actions.
- Physical Android testing is still required for touch interaction, AI behavior, safe-area placement, frame pacing, memory and thermal stability.

## Release limitations

This offline build has no remote backend, matchmaking or account synchronization. The release APK is unsigned until the owner signs it with a protected production key. A CI build is not a substitute for physical-device gameplay QA.
