#!/usr/bin/env python3
"""Verify state-driven creature motion is installed in the canonical WILDBOUND actor runtime."""
from pathlib import Path
import subprocess, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/actors/actors.js'
if not p.is_file(): raise SystemExit(f'Missing canonical actor runtime: {p}')
s=p.read_text(encoding='utf-8')
checks={
 'procedural motion marker':'WILDBOUND_PROCEDURAL_CREATURE_MOTION_V1' in s,
 'named joint discovery':'const joints=[];visual.traverse(node=>' in s and "'tail'" in s and "'head'" in s and "'leg'" in s and "'arm'" in s,
 'base pose preservation':'state.modelBaseRotation=' in s and 'state.modelBaseScale=' in s,
 'windup anticipation':'-anticipation*.13' in s and '-anticipation*.09' in s,
 'attack lunge and recovery':'strike*.19' in s and 'recoil*.075' in s,
 'tail and limb articulation':"joint.role==='tail'" in s and "joint.role==='leg'" in s and "joint.role==='arm'" in s,
 'aura and eye feedback':'state.aura.scale.setScalar' in s and 'state.eyes.forEach' in s,
}
for name,ok in checks.items(): print(('PASS' if ok else 'FAIL'),name)
if not all(checks.values()): raise SystemExit('WILDBOUND_CREATURE_MOTION_CHECK_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_PROCEDURAL_CREATURE_MOTION_OK',len(checks)+1,'checks')
