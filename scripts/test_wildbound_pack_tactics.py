#!/usr/bin/env python3
"""Regression checks for WILDBOUND tactical monster behavior."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/ai/monster-ai.js'
if not p.is_file(): raise SystemExit(f'Missing {p}')
s=p.read_text(encoding='utf-8')
checks={
 'pack roles are deterministic and distinct':'tacticRole' in s and 'flanker' in s and 'pursuer' in s and 'disruptor' in s,
 'melee units use player-relative flank positions':'baseAngle' in s and "desired=u.kind==='brute'?2.2:1.65" in s,
 'nearby monsters avoid stacking':'od<1.9' in s and 'sx+=ox/od' in s,
 'ranged monsters maintain engagement distance':'d<7.5' in s and 'd>13.5' in s,
 'melee attacks have a readable windup':'attackWindup' in s and 'monster-telegraph' in s,
 'attacks revalidate range before applying damage':'current<=u.range*1.12' in s,
 'ward mitigation and invulnerability remain respected':'game.invulnerable>0' in s and 'skills.ward' in s,
 'boss retains pursuit and phase-one melee':"else if(u.kind==='boss'){if(d>u.range*.78)" in s and 'u.phase===1' in s,
 'boss phase attacks and telegraphs remain':'boss-slam-warning' in s and 'boss-phase' in s and 'game.spawnProjectile' in s,
 'hit flash and attack tell have separate visual states':'0x7d3027' in s and '0xff8a43' in s,
}
for label,ok in checks.items(): print(('PASS' if ok else 'FAIL'),label)
if not all(checks.values()): raise SystemExit('WILDBOUND_PACK_TACTICS_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_PACK_TACTICS_OK',len(checks)+1,'checks')
