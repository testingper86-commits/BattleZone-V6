# BattleZone V6 Runtime Reliability QA

These checks extend the V6 Android gameplay matrix. They require physical Android devices; CI checks the source invariants only.

| ID | Area | Test | Expected result | Evidence |
|---|---|---|---|---|
| QA-38 | First launch | Fresh install, airplane mode enabled, launch and wait for the lobby | Android WebView loads the local index and assets; Three.js initializes; the actual game canvas draws frames; no blank screen or external request dependency | Device model/API, screen recording, BattleZoneWeb Logcat |
| QA-39 | GPU context pressure | Launch on a low-memory device; open lobby, wait 5 minutes, deploy, repeat 10 times | WebGL diagnostic probe releases its context; optional operator preview can fail without aborting game startup; preview context is released after deployment | GPU profiler, screen recording, Logcat |
| QA-40 | Renderer watchdog | Simulate unavailable/lost preview renderer and separately interrupt the game renderer | Preview failure falls back to the CSS operator silhouette; only frames rendered by #c satisfy the startup watchdog; game-render failure shows a diagnostic screen | Screen recording, injected fault record, Logcat |
| QA-41 | Deployment recovery | Start BR, TDM and FFA; separately force a deployment exception | Loading overlay exits; lobby is restored; actionable error details are visible; no permanently disabled deploy button | Video + Logcat |
| QA-42 | Responsive lobby | Test 16:9, 20:9 and short landscape displays with gesture navigation and cutouts | Settings, map list, operator, skin control, deploy button and dock remain aligned; settings expand/collapse correctly; panels scroll independently; touch targets remain usable | Screenshots + touch recording |
| QA-43 | WebView lifecycle | Background/foreground, lock/unlock, and recover from a main-frame resource error | WebView page lifecycle and startup state are logged; main-frame load failures show a readable error page; no silent black screen | BattleZoneWeb Logcat + video |

A successful APK build is not device verification. Record evidence against the exact APK SHA-256 and keep every blocker test tied to the tested build.

| QA-44 | Tactical visibility | Place enemy bots and squad allies on opposite sides of buildings, tree trunks and grouped cover; break and restore line of sight. | AI does not maintain a live target lock or chase through solid cover; enemy bots investigate the last visible location, choose another visible target when available, and reacquire after visibility returns. | Screen recording + match-state/combat trace |
| QA-45 | Frame-loop efficiency | Profile idle, movement, sprint and combat transitions for 15 minutes on low/mid/high Android devices. | Movement/run DOM state changes only on transitions; telemetry object remains stable; no regression in touch response, FPS, memory or thermal behavior. | Perfetto/Android profiler + APK SHA-256 |
