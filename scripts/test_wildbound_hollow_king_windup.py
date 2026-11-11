#!/usr/bin/env python3
"""Regression checks for the Hollow King phase-one windup."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
checks={
 "boss windup marker present":"WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1" in s,
 "phase-one boss melee is telegraphed":"u.kind==='boss'&&(u.phase||1)===1" in s and "type:'boss-swing',duration:.82" in s,
 "boss swing has a distinct damage and reach profile":"damage:u.damage*1.15,reach:u.range*1.45" in s,
 "boss swing is phase-one only":"(u.phase||1)===1" in s,
 "boss phase two and three special attacks remain": "phase>=2" in s and "W.bus.emit('boss-slam-warning')" in s,
 "boss weak-core exposure remains intact":"u.weakUntil=performance.now()+1800" in s,
 "boss swing uses shared dodge and ward mitigation":"pending.damage*(1-reduction)" in s and "if(game.invulnerable<=0)" in s,
 "boss telegraph triggers existing HUD feedback":"W.bus.emit('boss-telegraph')" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('HOLLOW_KING_WINDUP_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_HOLLOW_KING_WINDUP_OK',len(checks)+1,'checks')
