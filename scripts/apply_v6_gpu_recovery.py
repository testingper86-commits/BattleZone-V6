#!/usr/bin/env python3
"""Recover the V6 Three.js renderer after GPU context loss and safely request immersive mode."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
path = files[0]
source = path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_GPU_RECOVERY_V1"
if marker in source:
    print("BATTLEZONE_V6_GPU_RECOVERY_ALREADY_APPLIED")
    raise SystemExit(0)

def replace_once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    source = source.replace(old, new, 1)

old_context = """var cv=r.domElement;if(cv){cv.addEventListener('webglcontextlost',function(e){e.preventDefault();window.bzFatal('Graphics context lost','<p>The GPU reset the 3D view (low memory or the app was backgrounded for a long time). Tap RETRY to reload.</p>')});}"""
new_context = """var cv=r.domElement;if(cv){
   cv.addEventListener('webglcontextlost',function(e){
    e.preventDefault();window.__bzWebglContextLost=true;
    if(window.__bzWebglRecoveryTimer)clearTimeout(window.__bzWebglRecoveryTimer);
    window.__bzNote&&window.__bzNote('Game GPU context lost; waiting for WebGL restoration');
    window.__bzWebglRecoveryTimer=setTimeout(function(){
     if(window.__bzWebglContextLost)window.bzFatal('Graphics context could not recover','<p>Android WebView did not restore the game GPU context. Close other GPU-heavy apps, then tap RETRY to rebuild the 3D view.</p>');
    },10000);
   });
   cv.addEventListener('webglcontextrestored',function(){
    window.__bzWebglContextLost=false;
    if(window.__bzWebglRecoveryTimer)clearTimeout(window.__bzWebglRecoveryTimer);
    window.__bzNote&&window.__bzNote('Game GPU context restored; reloading game resources');
    setTimeout(function(){location.reload()},250);
   });
  }"""
replace_once(old_context, new_context, "WebGL context-loss recovery handler")
old_fullscreen = "document.documentElement.requestFullscreen();screen.orientation.lock('landscape')"
new_fullscreen = """if(document.fullscreenEnabled&&document.documentElement&&typeof document.documentElement.requestFullscreen==='function'){
  try{var bzFullscreenPromise=document.documentElement.requestFullscreen();if(bzFullscreenPromise&&typeof bzFullscreenPromise.catch==='function')bzFullscreenPromise.catch(function(e){window.__bzNote&&window.__bzNote('Fullscreen unavailable: '+(e&&e.message||e))})}catch(e){window.__bzNote&&window.__bzNote('Fullscreen unavailable: '+(e&&e.message||e))}
 }
 if(screen.orientation&&typeof screen.orientation.lock==='function'){
  try{var bzOrientationPromise=screen.orientation.lock('landscape');if(bzOrientationPromise&&typeof bzOrientationPromise.catch==='function')bzOrientationPromise.catch(function(e){window.__bzNote&&window.__bzNote('Orientation lock unavailable: '+(e&&e.message||e))})}catch(e){window.__bzNote&&window.__bzNote('Orientation lock unavailable: '+(e&&e.message||e))}
 }"""
replace_once(old_fullscreen, new_fullscreen, "fullscreen and orientation request")
source = source.replace("</body>", "<!-- " + marker + " -->\n</body>", 1)
if marker not in source:
    raise SystemExit("Could not write V6 GPU recovery marker")
path.write_text(source, encoding="utf-8")
print("BATTLEZONE_V6_GPU_RECOVERY_APPLIED", path)
