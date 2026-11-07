# V6 world and tactical integrity repair

## Root cause
Movement collision and tactical shot occlusion used separate registries. Several world objects were inserted into the movement-obstacle list but their actual Three.js meshes were never added to the raycast blocker list. The player and AI could therefore collide with or hide behind vegetation/props while shots still passed through them.

## Repair
- Shared cylinder-created cover is registered in the tactical blocker list at creation time.
- Broadleaf tree trunks and instanced forest trunks are registered as raycast blockers.
- Collidable grouped props register their mesh children because the raycaster intentionally uses non-recursive intersection for performance.
- Environmental deadfall is registered as tactical cover.
- The raycast rejects non-finite distances and remains allocation-free in the combat loop.

## Verification
CI checks each registration path and confirms the line-of-sight helper still raycasts against the single canonical blocker list. Android Gradle build and JVM tests are separate checks. Physical-device visual, collision, combat and frame-pacing QA is still required; this source patch does not claim those tests have been performed.

## Scope
This patch repairs collision/line-of-sight consistency. It does not convert the existing procedural world into a photorealistic AAA asset pipeline, and it does not certify every weapon, animation, vehicle, map, or tactical order as defect-free.

## Combat controls and vehicle coordinate integrity

The same idempotent source patch also corrects three verified gameplay defects:

- Aim spread previously used `P.grip || ...`, so an equipped grip returned numeric `1` as the normalized spread and made shots wildly inaccurate. Spread now starts at `0.01` and applies the same `0.65` grip and `0.75` compensator multipliers as the recoil model.
- Vehicle movement clamped the vehicle transform to the playable world but copied the unclamped candidate coordinates into the player proxy. The player now follows the final clamped vehicle transform, keeping combat, HUD, minimap and world checks aligned.
- Vehicle exit now resolves nearby obstacle collision and clamps the resulting player position to the playable world boundary.

The regression test checks all three invariants as well as the original seven world/tactical checks. These are source-level checks; actual touch feel, combat balance and vehicle handling still require Android gameplay QA.


## Rigged combat animation fallback

The final-stage integrity patch runs after the multimodel patcher so its anchors target the actual per-rig model registration. If a model family lacks a shoot or reload clip, the action API now runs a bounded procedural fallback instead of silently returning false: shoot lasts 0.22 seconds, reload lasts 1.5 seconds, the weapon mount recoils or tilts, and Kenney arm bones receive a matching two-hand pose when available. Existing rig clips always take precedence. The base weapon mount transform is restored each frame, and the fallback timer expires back into locomotion. This remains source-level verification; actual arm orientation and weapon grip must be checked on Android hardware.


## Occlusion-aware enemy and squad target acquisition

The prior AI scan selected targets by distance and role score, then checked cover only when firing. That allowed bots and squad allies to keep pursuing an opponent through a building or tree even though the shot itself was blocked. The final-stage patch now validates visibility before locking an enemy target. A blocked target is suppressed for one second, the scan can select another visible opponent, and enemy bots fall back to their existing last-seen investigation behavior. Squad allies use a dedicated `bzV6ValidateSquadTarget` helper with a 0.22-second visibility cadence and a one-second blocked-target cache; they stop pursuing through cover and can reacquire when line of sight returns. Non-finite shot endpoints now fail closed rather than being treated as clear.

## Frame-loop allocation reduction

`window.BZGameState` is now updated in place rather than allocating a new object every rendered frame. The `bz-moving` and `bz-running` body classes are only toggled when their boolean state changes. This removes repeated object allocation and redundant DOM class operations from the hot frame loop without changing input or HUD state. It is a source-level optimization; sustained FPS, allocation rate and thermal behavior still require profiling on physical Android devices.

## Build and regression gate

The next Android package increments to version `1.2.1` / versionCode `4`. CI runs `test_v6_world_tactical_integrity.py` (29 world/combat/animation/frame assertions), `test_v6_tactical_line_of_sight.py` (11 executable Node behavior checks for enemy and squad visibility), and full inline/packaged JavaScript syntax validation. The patcher is verified idempotent. A green CI run still does not replace Android hardware QA.
