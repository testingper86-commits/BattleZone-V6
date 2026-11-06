#!/usr/bin/env python3
"""Build-blocking regression checks for V6 GPU restoration and fullscreen Promise handling."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
html = files[0].read_text(encoding="utf-8")
checks = {
    "GPU recovery marker present": "BATTLEZONE_V6_GPU_RECOVERY_V1" in html,
    "context loss is prevented and recovery is awaited": "e.preventDefault();window.__bzWebglContextLost=true" in html and "waiting for WebGL restoration" in html,
    "context restore clears timeout and reloads clean game resources": "webglcontextrestored" in html and "clearTimeout(window.__bzWebglRecoveryTimer)" in html and "setTimeout(function(){location.reload()},250)" in html,
    "failed GPU restoration has bounded fatal fallback": "},10000);" in html and "Graphics context could not recover" in html,
    "fullscreen is feature-detected": "document.fullscreenEnabled&&document.documentElement&&typeof document.documentElement.requestFullscreen==='function'" in html,
    "fullscreen Promise rejection is handled": "bzFullscreenPromise.catch" in html and "Fullscreen unavailable:" in html,
    "orientation lock is feature-detected": "screen.orientation&&typeof screen.orientation.lock==='function'" in html,
    "orientation lock Promise rejection is handled": "bzOrientationPromise.catch" in html and "Orientation lock unavailable:" in html,
    "old immediate fatal context-loss handler is removed": "window.bzFatal('Graphics context lost'" not in html,
    "old unguarded fullscreen call is removed": "document.documentElement.requestFullscreen();screen.orientation.lock('landscape')" not in html,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + "  " + name)
if not all(checks.values()):
    raise SystemExit("V6 GPU recovery regression checks failed")
print("PASS  V6 GPU recovery regression checks")
