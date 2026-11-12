#!/usr/bin/env python3
"""Regression checks for distinct-species Ashen Veil contract progression."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
base=root/'app/src/main/assets/www/js/wildbound'
m=(base/'backend/mission.js').read_text(encoding='utf-8')
u=(base/'ui/interface.js').read_text(encoding='utf-8')
checks={
 "distinct hunt contract marker present":"WILDBOUND_DISTINCT_HUNT_CONTRACT_V1" in m,
 "mission reset clears the species ledger":"W.state.progress.purgedTypes=[]" in m,
 "duplicate species cannot advance objective":"found.includes(enemy.type)" in m and "SIGNATURE ALREADY PURGED" in m,
 "unique species are recorded":"found.push(enemy.type)" in m,
 "purge progress derives from unique species count":"W.state.progress.purged=found.length" in m,
 "boss unlock uses mission catalog requirement":"W.state.progress.purged>=W.data.mission.requiredPurges" in m,
 "boss kill still completes the contract":"W.state.progress.contract=true;W.bus.emit('contract-complete')" in m,
 "HUD exposes explicit distinct species progress":"PURGE ANOMALY TYPES '+(W.state.progress.purged||0)+'/'+W.data.mission.requiredPurges" in u,
 "save event persists duplicate and unique kill outcomes":"W.bus.emit('save')" in m,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('DISTINCT_HUNT_CONTRACT_FAILED')
for p in (base/'backend/mission.js',base/'ui/interface.js'):
 r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
 print('PASS JavaScript syntax',p.name)
print('WILDBOUND_DISTINCT_HUNT_CONTRACT_OK',len(checks)+2,'checks')
