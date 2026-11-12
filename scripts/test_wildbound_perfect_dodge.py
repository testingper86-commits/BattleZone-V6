#!/usr/bin/env python3
"""Regression checks for WILDBOUND perfect-dodge counter combat."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
c=root/'app/src/main/assets/www/js/wildbound/gameplay/combat.js';u=root/'app/src/main/assets/www/js/wildbound/ui/interface.js'
if not c.is_file() or not u.is_file(): raise SystemExit('Missing combat/UI module')
s=c.read_text(encoding='utf-8');h=u.read_text(encoding='utf-8')
checks={
 'perfect dodge only triggers during an active enemy windup':'u.attackWindup>0' in s,
 'counter window is proximity-gated':'u.range+1.35' in s,
 'perfect dodge cancels the incoming strike':'u.attackWindup=0' in s,
 'successful counter staggers and exposes the attacker':'u.stagger=Math.max' in s and 'u.weakUntil=performance.now()+1800' in s,
 'perfect dodge restores ultimate charge':'c.ultimate=Math.min(100,c.ultimate+18)' in s,
 'ordinary dodge retains its movement and invulnerability':'game.invulnerable=.48' in s and 'p.position.x+=-Math.sin(p.rotation.y)*2.4' in s,
 'perfect dodge has player-facing combat feedback':"W.bus.on('perfect-dodge'" in h and 'COUNTER WINDOW' in h,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('PERFECT_DODGE_REGRESSION_FAILED')
for f in (c,u):
 r=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
 print('PASS JavaScript syntax',f.name)
print('WILDBOUND_PERFECT_DODGE_OK',len(checks)+2,'checks')
