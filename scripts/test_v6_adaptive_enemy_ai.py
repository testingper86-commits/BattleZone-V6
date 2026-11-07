#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = root / "app/src/main/assets/www/index.html"
source = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_ADAPTIVE_ENEMY_AI_V1"
assert marker in source, "adaptive enemy AI marker missing"
assert "u.aiState='retreat'" in source, "low-health retreat state missing"
assert "u.aiState='investigate'" in source, "last-known-position investigation missing"
assert "u.aiState='zone'" in source, "safe-zone recovery priority missing"
assert "b.userData.aiLastSeenX=P.x" in source, "player-hit memory not wired"
assert "const accuracy=" in source, "distance/difficulty aim model missing"
assert "if(u.aiScanT<=0||!target)" not in source, "empty target state must respect the scan cooldown"
assert "if(u.aiScanT<=0){" in source, "AI scan cooldown is not authoritative"
assert "bzV6UpdateZoneWaypoint(b,u,dt)" in source, "safe-zone waypoint helper is not used"
assert "u.aiZoneTarget={x:zc.x+rnd(-10,10),z:zc.z+rnd(-10,10)}" in source, "safe-zone waypoint must be cached"
assert "gx=tgt.x+Math.cos(approachAngle)*13" in source, "rush/cover target approach missing"
assert "u.role==='camp'" in source, "camp role hold behavior missing"
assert "Number(u.hp)<=28" in source and "tacticalCoverPoint(b,aiDecision.x,aiDecision.z)" in source, "low-health lost-target retreat missing"
start = source.index("/* " + marker + " */")
end = source.index("// Original lightweight operator power VFX", start)
helper = source[start:end]
node = r"""
const vm = require('node:vm');
const helper = __HELPER__;
function makeContext(mode) {
  const bot = {position:{x:0,z:0},userData:{alive:true,hp:100}};
  const ally = {position:{x:2,z:0},userData:{alive:true,hp:100,ally:true}};
  const enemy = {position:{x:4,z:0},userData:{alive:true,hp:100,ally:false}};
  const actors=[bot,ally,enemy];
  let scanCalls=0,randomCalls=0;
  const sandbox = {
    getScanCalls:()=>scanCalls,getRandomCalls:()=>randomCalls,
    zc:{x:0,z:0,r:20},
    P:{alive:true,air:0,x:15,z:0,hp:100},
    DF:1,ENV:{vis:1},BZ_MODE:mode,bot,actors,
    smk:()=>false,hasClearShot:()=>true,rnd:(a,b)=>{randomCalls++;return(a+b)/2},
    forEachActor:fn=>{scanCalls++;actors.forEach(fn)}
  };
  vm.createContext(sandbox);
  vm.runInContext(helper,sandbox);
  return sandbox;
}
let c=makeContext('BR');
let d=c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.2);
if(!d.target||d.target.o!==c.actors[2])throw new Error('BR must select nearest hostile and ignore squad allies');
c.actors[2].position.x=9;c.bot.userData.aiScanT=.2;
d=c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.01);
if(d.target.x!==9)throw new Error('cached actor target position did not refresh');
c.actors[2].userData.alive=false;c.P.x=200;c.bot.userData.aiScanT=0;c.bot.userData.aiAlert=2;c.bot.userData.aiLastSeenX=9;c.bot.userData.aiLastSeenZ=0;
d=c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.1);
if(!d.investigate||d.x!==9)throw new Error('lost target should trigger last-known-position investigation');
c=makeContext('TDM');c.P.x=30;c.actors[2].position.x=2;c.actors[1].position.x=6;
d=c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.2);
if(!d.target||d.target.o!==c.actors[1])throw new Error('TDM bots must target the player team only');
c=makeContext('BR');c.P.x=200;c.actors[2].position.x=13;c.actors[2].userData.hp=100;
const wounded={position:{x:15,z:0},userData:{alive:true,hp:5,ally:false}};
c.actors.push(wounded);
d=c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.2);
if(!d.target||d.target.o!==wounded)throw new Error('target scoring should prioritize a nearby weakened opponent');
// Empty target scans are cached for the configured interval.
c=makeContext('BR');c.P.alive=false;c.actors[1].userData.alive=false;c.actors[2].userData.alive=false;
c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.016);
const scans=c.getScanCalls();
c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.016);
if(c.getScanCalls()!==scans)throw new Error('empty-target scans are not throttled');
c.bzV6ChooseEnemyTarget(c.bot,c.bot.userData,.3);
if(c.getScanCalls()!==scans+1)throw new Error('empty-target scan did not resume after cooldown');
// Safe-zone waypoint remains stable between refresh intervals.
c=makeContext('BR');const zoneBot={position:{x:30,z:0}},zoneState={t:5};
c.bzV6UpdateZoneWaypoint(zoneBot,zoneState,.016);
const zx=zoneState.tx,zz=zoneState.tz,randoms=c.getRandomCalls();
c.bzV6UpdateZoneWaypoint(zoneBot,zoneState,.016);
if(zoneState.tx!==zx||zoneState.tz!==zz||c.getRandomCalls()!==randoms)throw new Error('safe-zone waypoint changes every frame');
c.bzV6UpdateZoneWaypoint(zoneBot,zoneState,3);
if(c.getRandomCalls()===randoms)throw new Error('safe-zone waypoint failed to refresh');
console.log('ADAPTIVE_ENEMY_AI_BEHAVIOR_OK');
""".replace("__HELPER__", repr(helper))
p = subprocess.run(["node", "-e", node], capture_output=True, text=True)
if p.returncode:
    raise SystemExit(p.stderr or p.stdout)
print(p.stdout.strip())
print("ADAPTIVE_ENEMY_AI_STATIC_CHECKS_OK")
