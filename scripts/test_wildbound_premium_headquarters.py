#!/usr/bin/env python3
"""Regression gate for the WILDBOUND premium headquarters frontend."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve();www=root/"app/src/main/assets/www"
h=(www/"index.html").read_text(encoding="utf-8");c=(www/"css/wildbound.css").read_text(encoding="utf-8");j=(www/"js/wildbound/ui/interface.js").read_text(encoding="utf-8")
checks={
 "premium headquarters marker and accessible screen landmarks":"WILDBOUND_PREMIUM_HEADQUARTERS_V1" in h and 'aria-label="WILDBOUND headquarters"' in h and 'aria-label="Active hunt"' in h,
 "live rank progress indicator is in the lobby header":'id="rank-progress"' in h and "rankProgress=Math.max" in j and "$('rank-progress').style.width=rankProgress+'%'" in j,
 "field record is an actual interactive lobby control":'id="field-record"' in h and "$('field-record').onclick=()=>showModal('FIELD RECORD'" in j,
 "field record uses authoritative local progression":"W.state.player.xp" in j and "W.state.progress.purged" in j and "W.state.player.kills" in j and "W.state.player.essence" in j,
 "field record includes current contract and consumables":"W.data.mission.name" in j and "W.state.inventory.potions" in j,
 "keyboard focus remains visible":"button:focus-visible" in c and "outline:2px solid var(--gold)" in c,
 "safe area is respected by lobby and modal":"env(safe-area-inset-top" in c and "#modal{padding:" in c,
 "short landscape lobby panels remain scrollable":"orientation:landscape) and (max-height:560px)" in c and "max-height:calc(100dvh - 105px)" in c and "overflow-y:auto" in c,
 "reduced motion preference is respected":"prefers-reduced-motion:reduce" in c and "animation-duration:.01ms" in c,
 "existing lobby actions and core game buttons remain present":all(x in h for x in ['id="deploy"','id="briefing"','id="bestiary"','id="inventory"','id="skills"','id="settings"','id="track"','id="pause"']),
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Premium headquarters regression failed")
for f in (www/"js/wildbound/ui/interface.js",):
 r=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
print("WILDBOUND_PREMIUM_HEADQUARTERS_OK",len(checks)+1,"checks")
