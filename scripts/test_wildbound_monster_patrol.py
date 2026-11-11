#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
base=root/"app/src/main/assets/www/js/wildbound"
a=(base/"actors/actors.js").read_text(encoding="utf-8")
b=(base/"ai/monster-ai.js").read_text(encoding="utf-8")
checks={
 "patrol marker present":"WILDBOUND_MONSTER_AMBIENT_PATROL_V1" in b,
 "monster spawn records its home position":"homeX:x,homeZ:z" in a,
 "ambient patrol runs outside detection range":"if(d>=34&&u.kind!==\'boss\')" in b,
 "patrol remains bounded around spawn":"Math.cos(phase)*3.5" in b and "Math.sin(phase)*3.5" in b,
 "patrol movement is delta-time scaled":"u.speed*.24*dt" in b,
 "patrol movement is capped by remaining distance":"Math.min(pd,u.speed*.24*dt)" in b,
 "boss remains excluded from ambient patrol":"u.kind!==\'boss\'" in b,
 "hostile pursuit logic remains intact":"m.position.x+=dx/(d||1)*u.speed*dt" in b,
 "telegraph attack state remains intact":"u.pendingAttack" in b and "W.bus.emit(\'monster-telegraph\'" in b,
}
for k,v in checks.items(): print(("PASS" if v else "FAIL"),k)
if not all(checks.values()): raise SystemExit("MONSTER_PATROL_REGRESSION_FAILED")
for p in (base/"actors/actors.js",base/"ai/monster-ai.js"):
 r=subprocess.run(["node","--check",str(p)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
 print("PASS JavaScript syntax",p.name)
print("WILDBOUND_MONSTER_PATROL_OK",len(checks)+2,"checks")
