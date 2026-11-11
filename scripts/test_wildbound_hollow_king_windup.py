#!/usr/bin/env python3
"""Regression checks for the Hollow King phase-one windup."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
checks={
 "boss windup marker present":"WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1" in s,
 "phase-one boss melee is telegraphed":"phaseOne?'boss-swing'" in s and "state.attackWindup=phase===3?.9:phaseOne?.82:.55" in s,
 "boss swing has a distinct damage and reach profile":"state.pendingAttackReach=phaseOne?state.range*1.45:reach" in s and "state.damage*(phaseOne?1.15:1)" in s,
 "boss swing is phase-one only":"const phaseOne=phase===1" in s,
 "boss phase two and three special attacks remain":"if(phase===2)" in s and "else if(phase===3)" in s,
 "boss weak-core exposure remains intact":"state.weakUntil=now+(state.attackWindup+.55)*1000" in s,
 "boss swing uses shared dodge and ward mitigation":"W.state.skills.ward||0" in s and "game.invulnerable<=0" in s,
 "boss telegraph triggers existing HUD feedback":"W.bus.emit('boss-telegraph'" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('HOLLOW_KING_WINDUP_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_HOLLOW_KING_WINDUP_OK',len(checks)+1,'checks')
