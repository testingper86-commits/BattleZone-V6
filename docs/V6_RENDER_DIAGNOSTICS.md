# BattleZone V6 local render diagnostics

Append `?bzdiag=1` to the local game URL to show an on-device diagnostics overlay. The default game URL does not create the overlay.

The overlay reports FPS, last processed frame time, Three.js draw calls, triangles, points, lines, geometry/texture counts, renderer pixel ratio, maximum texture size, device memory and CPU thread count, plus current quality/battery-saver mode. It reads `WebGLRenderer.info` and browser device capabilities locally.

No telemetry is uploaded, no network API is called, and the overlay uses `pointer-events:none` so it does not intercept game controls. Remove the query parameter to disable it.

`test_v6_render_diagnostics.py` verifies opt-in behavior, displayed metrics, render-loop integration, absence of network telemetry APIs in the diagnostics block, and Node syntax for the modified inline game script. The overlay is instrumentation, not a performance result: frame-time/GPU/memory profiling still must be collected on representative physical Android devices.
