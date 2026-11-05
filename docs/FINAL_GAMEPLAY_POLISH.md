# Battle Zone V6 Offline — Final Gameplay Polish

## Implemented in this change

- Replaced the flat ground plane with a 900 × 900 generated heightfield. Terrain vertex colors are derived from the active map palette, and the same height function is used by player and bot ground placement.
- Reworked squad ally target selection, line-of-sight checks, firing cadence, support positioning, medic support and revive messaging.
- Added squad ally damage handling to the shared explosive damage function. Blast radius and falloff now apply to teammates as well as enemies and the player.
- Hid the operator's held weapon while airborne and in vehicles; it becomes visible again after landing or exiting a vehicle.
- Improved manual and automatic parachute deployment, reduced horizontal drift on canopy deployment, and added a larger canopy with visible suspension lines.
- Removed the automatic startup splash handlers. Match and map transition feedback remains.
- Added responsive lobby layout rules and explicit labels for Match Configuration, Battlefield Select and Operator Services.
- Reduced the high-quality render pixel-ratio ceiling and use the newest coalesced pointer sample for touch aim.

## Build integration

The patch is applied to the canonical source during the Android build workflow. It is idempotent and fails if required source anchors are missing or ambiguous. The extracted source validator is updated to check the new terrain heightfield and airborne weapon state.

## Verification boundaries

Static validation and JavaScript syntax checks are required in CI, followed by `:app:testDebugUnitTest` and `:app:assembleDebug`. These checks do not replace physical-device QA. Android device testing is still required for touch latency, frame pacing, map collision, squad combat, friendly blast damage, parachute visibility and long-session stability.

No online, LAN, pairing or multiplayer features are added.
