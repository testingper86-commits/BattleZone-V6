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
