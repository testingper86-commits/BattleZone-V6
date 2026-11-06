#!/usr/bin/env python3
"""Regression checks for the V6 optional voice module and match startup path."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected one game index.html, found {len(files)}")
html=files[0].read_text(encoding="utf-8")
marker="BATTLEZONE_V6_VOICE_STARTUP_FIX_V1"
checks={
 "voice startup fix marker present":marker in html,
 "event voice fallback is registered before deploy handler":"window.bzPlayEventVoice=window.bzPlayEventVoice||function(eventName)" in html and html.index("window.bzPlayEventVoice=window.bzPlayEventVoice||function(eventName)")<html.index("$('go2').onclick="),
 "spawn cue cannot abort match deployment":"window.bzPlayEventVoice?.('spawn')" in html,
 "combat cue cannot abort elimination handling":"window.bzPlayEventVoice?.('combat')" in html,
 "victory cue cannot abort match completion":"window.bzPlayEventVoice?.('victory')" in html,
 "fallback respects audio preference":"if(!SND_ON)return" in html,
 "fallback synthesizes spawn combat and victory cues":all(x in html for x in ("tn(440,660","nz(.08,.12,1200","tn(523,784")),
 "optional voice-pack implementation can still override fallback":"window.bzPlayEventVoice=bzPlayEventVoice" in html,
}
for name,ok in checks.items(): print(("PASS" if ok else "FAIL")+"  "+name)
if not all(checks.values()): raise SystemExit("V6 voice startup regression checks failed")
print("PASS  V6 voice startup regression checks")
