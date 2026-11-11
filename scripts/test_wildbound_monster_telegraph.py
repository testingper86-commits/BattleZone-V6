#!/usr/bin/env python3
"""Regression checks for readable and interruptible monster attack windups."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
if not p.is_file(): raise SystemExit(f'Missing monster AI module: {p}')
s=p.read_text(encoding='utf-8')
checks={
 'patch marker present':'WILDBOUND_MONSTER_TELEGRAPH_COMBAT_V1' in s,
 'melee attacks have a readable windup':"u.kind==='melee'?.42" in s and "type:brute?'slam':'lunge'" in s,
 'ranged attacks have a readable windup':'u.attackWindup=.48' in s and "type:'ranged'" in s,
 'telegraph events expose attack type and duration':"W.bus.emit('monster-telegraph'" in s,
 'telegraph has visible orange emissive feedback':'0xff6b32' in s and 'u.pendingAttack?' in s,
 'melee strike can miss if player leaves range':'d<=pending.reach' in s,
 'dodge invulnerability is respected at strike time':'if(game.invulnerable<=0)' in s,
 'stagger interrupts a pending attack':"u.pendingAttack=null;u.attackWindup=0;W.bus.emit('monster-telegraph-cancel'" in s,
 'ranged projectile launches only after windup':'game.spawnProjectile(origin,pending.damage,0xa58bff,1)' in s,
 'boss phase and slam logic remain intact':"if(u.kind==='boss')" in s and "W.bus.emit('boss-slam-warning')" in s,
 'existing ward damage mitigation remains':'W.state.skills.ward||0' in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('MONSTER_TELEGRAPH_REGRESSION_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_MONSTER_TELEGRAPH_OK',len(checks)+1,'checks')
