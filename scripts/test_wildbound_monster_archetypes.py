#!/usr/bin/env python3
"""Verify distinct melee archetype timings, damage, reach and boss/ranged isolation."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
actors=(root/'app/src/main/assets/www/js/wildbound/actors/actors.js').read_text(encoding='utf-8')
checks={
 'archetype profile marker present':'WILDBOUND_MONSTER_ARCHETYPE_PROFILES_V1' in s,
 'distinct Grave Stalker lunge profile':"attackProfile:stalker?{windup:.28,recovery:.48,damageScale:1,reachScale:1.38,attack:'lunge'}" in actors,
 'distinct Ironmaw heavy slam profile':":ironmaw?{windup:.92,recovery:1.12,damageScale:1.3,reachScale:1.55,attack:'slam'}" in actors,
 'canonical AI consumes windup and recovery':"state.attackWindup=profile.windup" in s and "state.attackRecovery=state.attackProfile?state.attackProfile.recovery" in s,
 'Ironmaw damage multiplier is applied':'state.damage*(profile.damageScale||1)' in s,
 'archetype-specific reach is stored and validated':'state.pendingAttackReach=state.range*(profile.reachScale||1.25)' in s and 'distance<=strikeReach' in s,
 'boss attack phase logic remains independent':"if(kind==='boss')" in s and "W.bus.emit('boss-slam-warning'" in s,
 'ranged casting telegraph remains intact':"attack:'ether-bolt'" in s and "state.attackWindup=.5" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('MONSTER_ARCHETYPE_PROFILE_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_MONSTER_ARCHETYPES_OK',len(checks)+1,'checks')
