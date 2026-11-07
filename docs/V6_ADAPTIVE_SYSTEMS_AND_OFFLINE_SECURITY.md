# V6 Adaptive Systems and Offline Security

This change extends the existing offline game systems; it does not replace the current squad command UI, terrain, weather, vegetation, player progression, or procedural character fallback.

## Adaptive enemy AI

- Enemy target scans are cached per bot for 160–260 ms instead of rebuilding a target list every frame.
- Target scoring excludes squad allies in Battle Royale and targets the player's team in Team Deathmatch.
- Target scoring prefers nearby weakened opponents and retains a moving target's current position between scans.
- A bot that loses sight of a target investigates its last known position for a bounded alert window.
- Bots at or below 28 HP seek a tactical cover point or retreat away from the last visible threat.
- Safe-zone recovery takes movement priority over investigation and combat positioning.
- Accuracy scales with difficulty and target distance. Existing weapon damage, squad orders, cover helpers, and mode-specific win conditions remain authoritative.

## Character action animation

- The existing Three.js mixer now supports optional shoot, reload, and death clips in addition to idle, walk, run, and jump.
- GLB clips are discovered by conservative name matching; FBX action clips can be supplied through the existing model manifest anims mapping. The original Kenney rig remains primary. If it cannot load, the bundled CC0 KayKit GLB is a compatible fallback for its own idle/run/walk/jump/shoot/defeat rig; its `Defeat` clip maps to death. The KayKit rig is not retargeted onto Kenney, and no reload clip is claimed because the bundled KayKit GLB does not contain one.
- Combat events request action clips for player, enemy, ally, and death events. One-shot actions release the locomotion state cleanly so idle/run/walk resumes after a clip ends; death remains terminal. Missing clips still use the existing procedural pose fallback.
- Character dressing iterates bot and ally arrays directly instead of allocating a concatenated array every animation frame.
- Missing action clips return false; no placeholder animation is fabricated. Existing procedural characters and poses remain the fallback when the rigged model loader is unavailable.

## Adaptive graphics

- A frame-time governor samples approximately 2.8-second windows.
- Two sustained windows below 26 FPS reduce render resolution; three sustained windows above 50 FPS restore one quality tier.
- The three tiers cap device pixel ratio at 0.82, 1.0, and 1.2. The lowest tier disables dynamic shadows; higher tiers restore them.
- Existing Low Graphics and Battery Saver modes bypass the governor and retain their manual settings.
- This is a conservative resolution/shadow governor, not a promise that every GPU or thermal condition will sustain a fixed frame rate.

## Offline WebView security

- A restrictive Content Security Policy permits packaged same-origin scripts/styles and local data/blob images, while disallowing objects, frames, form submission, and remote connections.
- unsafe-eval is not enabled. Inline scripts/styles remain allowed because the existing game runtime is a legacy single-document application.
- WebView navigation and subresource requests are restricted to HTTPS appassets.androidplatform.net/assets/.
- Network loads, file/content access, database storage, geolocation, pop-up windows, and runtime permission requests are disabled.
- No JavaScript bridge is exposed to the page. The manifest remains without INTERNET permission and cleartext traffic remains disabled.

## Verification boundaries

CI checks patch ordering, patcher idempotence, JavaScript syntax, AI target-selection behavior, animation action wiring, adaptive quality transitions, WebView security configuration, Android unit tests, and APK assembly.

CI cannot replace physical-device validation. Still required before release:
- Test real gameplay on representative low-, mid-, and high-tier Android devices.
- Verify AI combat, ally safety, retreat/investigation, and all match modes in actual play.
- Verify optional rigged action clips on the exact distributed model assets; procedural fallback remains expected if the clips are absent.
- Observe sustained frame pacing, memory use, GPU context recovery, and thermal behavior on device.
- Sign the release APK using the owner's protected production signing key.
