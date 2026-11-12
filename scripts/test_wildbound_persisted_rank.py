#!/usr/bin/env python3
"""Regression checks for persisted XP rank synchronization."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
base=root/'app/src/main/assets/www/js/wildbound'
p=(base/'backend/progression.js').read_text(encoding='utf-8')
u=(base/'ui/interface.js').read_text(encoding='utf-8')
checks={
 "persisted rank marker present":"WILDBOUND_PERSISTED_RANK_PROGRESSION_V1" in p,
 "previous rank is derived for legacy saves":"s.player.rank||Math.min(5,1+Math.floor(s.player.xp/500))" in p,
 "rank is derived from cumulative XP":"const rank=Math.min(5,1+Math.floor(s.player.xp/500))" in p,
 "rank is persisted to player state":"s.player.rank=rank" in p,
 "rank-up notification uses the rank catalog":"W.data.ranks[rank-1]" in p and "RANK ADVANCED" in p,
 "progression event reports rank-up state":"W.bus.emit('progression',{xp,essence,rank,rankUp})" in p,
 "HUD reads persisted rank with legacy fallback":"rank=p.rank||Math.min(5,1+Math.floor(p.xp/500))" in u,
 "rank labels use the canonical data catalog":"W.data.ranks[Math.min(4,rank-1)]" in u,
 "XP and essence rewards remain unchanged":"xp=kind==='boss'?800:kind==='brute'?140:90,essence=kind==='boss'?8:1" in p,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('PERSISTED_RANK_REGRESSION_FAILED')
for f in (base/'backend/progression.js',base/'ui/interface.js'):
 r=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
 print('PASS JavaScript syntax',f.name)
print('WILDBOUND_PERSISTED_RANK_OK',len(checks)+2,'checks')
