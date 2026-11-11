#!/usr/bin/env python3
"""Regression checks for cooldown, expiry and cleanup of hunt signatures."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/rendering/runtime.js'
s=p.read_text(encoding='utf-8')
checks={
 "tracking lifecycle marker present":"WILDBOUND_HUNT_TRACKING_LIFECYCLE_V1" in s,
 "tracking cooldown decreases every gameplay frame":"game.trackCd=Math.max(0,(game.trackCd||0)-dt)" in s,
 "cooldown starts only after a valid target is found":"if(!target){W.toast('NO ACTIVE SIGNATURE');return}game.trackCd=8" in s,
 "signature marker has a bounded lifetime":"game.trackExpires=performance.now()+6500" in s,
 "expired signature marker hides itself":"game.trackMarker.visible=false;W.bus.emit('track-expired'" in s,
 "signature marker pulses while active":"game.trackMarker.material.opacity=.3+Math.sin(pulse)*.2" in s,
 "last known location is identified honestly":"LAST SIGNATURE · '" in s,
 "restart removes and disposes marker resources":"game.scene.remove(game.trackMarker);game.trackMarker.geometry.dispose();game.trackMarker.material.dispose()" in s,
 "existing tracking cooldown warning remains":"TRACKING RECHARGING" in s,
 "existing signature lock event remains":"W.bus.emit('track',target.userData.type)" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('HUNT_TRACKING_REGRESSION_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_HUNT_TRACKING_OK',len(checks)+1,'checks')
