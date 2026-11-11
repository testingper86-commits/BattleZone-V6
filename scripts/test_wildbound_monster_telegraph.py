#!/usr/bin/env python3
"""Regression checks for readable and interruptible monster attack windups."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
if not p.is_file(): raise SystemExit(f'Missing monster AI module: {p}')
s=p.read_text(encoding='utf-8')
checks={
 'canonical AI state machine present':"state.attackWindup=Math.max(0,(state.attackWindup||0)-dt)" in s and "state.attackRecovery=Math.max(0,(state.attackRecovery||0)-dt)" in s,
 'melee attacks emit an explicit windup event':"state.attackWindup=profile.windup" in s and "W.bus.emit('monster-telegraph'" in s and "duration:state.attackWindup" in s,
 'ranged attacks have a readable cast windup':"attack:'ether-bolt'" in s and "state.attackWindup=.5" in s,
 'telegraph events expose type and position':"W.bus.emit('monster-telegraph'" in s and "position:monster.position.clone()" in s,
 'melee damage resolves after windup':"if(state.attackWindup<=0&&state.attackState==='windup')" in s and "playerState.hp=Math.max(0,playerState.hp-damage" in s,
 'dodge invulnerability is respected at strike time':'if(distance<=strikeReach&&game.invulnerable<=0)' in s,
 'stagger interrupts a pending windup':"state.stagger>0||state.attackRecovery>0" in s,
 'ranged projectile launches after windup':"game.spawnProjectile(origin,state.damage,kind==='wraith'?0x9d7ef2:0xa58bff" in s,
 'boss phase and slam logic remain intact':"if(kind==='boss')" in s and "boss-slam-warning" in s and "phase===3" in s,
 'existing ward damage mitigation remains':'W.state.skills.ward||0' in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('MONSTER_TELEGRAPH_REGRESSION_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_MONSTER_TELEGRAPH_OK',len(checks)+1,'checks')
