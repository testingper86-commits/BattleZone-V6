#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
base=root/"app/src/main/assets/www/js/wildbound"
a=(base/"actors/actors.js").read_text(encoding="utf-8")
b=(base/"ai/monster-ai.js").read_text(encoding="utf-8")
checks={
 "patrol marker present":"WILDBOUND_MONSTER_AMBIENT_PATROL_V1" in b,
 "monster spawn records its home position":"spawnX:x,spawnZ:z" in a,
 "ambient patrol runs outside detection range":"if(distance>=notice)" in b and "state.roamRadius>0" in b,
 "patrol remains bounded around spawn":"Math.cos(state.patrolPhase)*state.roamRadius" in b and "Math.sin(state.patrolPhase)*state.roamRadius" in b,
 "patrol movement is delta-time scaled":"state.speed*.36*dt" in b,
 "patrol movement is capped by remaining distance":"if(travel>.4)" in b,
 "boss remains excluded from ambient patrol":"roamRadius:king?0:10" in a,
 "hostile pursuit logic remains intact":"monster.position.x+=dx/(distance||1)*state.speed*dt" in b,
 "telegraph attack state remains intact":"state.attackState='windup'" in b and "W.bus.emit('monster-telegraph'" in b,
}
for k,v in checks.items(): print(("PASS" if v else "FAIL"),k)
if not all(checks.values()): raise SystemExit("MONSTER_PATROL_REGRESSION_FAILED")
for p in (base/"actors/actors.js",base/"ai/monster-ai.js"):
 r=subprocess.run(["node","--check",str(p)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
 print("PASS JavaScript syntax",p.name)
print("WILDBOUND_MONSTER_PATROL_OK",len(checks)+2,"checks")
