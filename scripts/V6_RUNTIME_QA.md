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
