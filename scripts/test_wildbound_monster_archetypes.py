#!/usr/bin/env python3
"""Verify distinct melee archetype timings, damage and reach."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
s=p.read_text(encoding='utf-8')
checks={
 'archetype profile marker present':'WILDBOUND_MONSTER_ARCHETYPE_PROFILES_V1' in s,
 'Grave Stalker has faster lunge windup':"u.kind==='melee'?.42" in s and "type:brute?'slam':'lunge'" in s,
 'Ironmaw has slower heavy slam windup':"brute?.92" in s and "brute?2.15:1.65" in s,
 'Ironmaw heavy strike damage is scaled':"damage:u.damage*(brute?1.3:1)" in s,
 'archetype-specific strike reach is stored':"reach:u.range*(brute?1.55:u.kind==='melee'?1.38:1.28)" in s,
 'strike validates its stored reach':'d<=pending.reach' in s,
 'boss attack phase logic remains independent':"if(u.kind==='boss')" in s and "W.bus.emit('boss-slam-warning')" in s,
 'ranged casting telegraph remains intact':"type:'ranged',duration:.48" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('MONSTER_ARCHETYPE_PROFILE_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_MONSTER_ARCHETYPES_OK',len(checks)+1,'checks')
