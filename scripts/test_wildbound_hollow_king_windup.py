#!/usr/bin/env python3
"""Regression checks for the canonical Hollow King phase-one windup."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
p = root / "app/src/main/assets/www/js/wildbound/ai/monster-ai.js"
s = p.read_text(encoding="utf-8")
checks = {
    "canonical boss windup marker present": "WILDBOUND_HOLLOW_KING_PHASE_ONE_WINDUP_V1" in s,
    "boss phase changes at health thresholds": "healthRatio<.3?3:healthRatio<.65?2:1" in s,
    "phase-one boss swing has a readable windup": "state.attackWindup=phase===3?.9:phaseOne?.82:.55" in s,
    "phase-one swing has dedicated cooldown and reach": "state.attackCd=phase===3?2.5:phaseOne?1.75:2.1" in s and "state.pendingAttackReach=phaseOne?state.range*1.45:reach" in s,
    "phase-one damage is scaled independently": "state.pendingAttackDamage=state.damage*(phaseOne?1.15:1)" in s,
    "weak-core window covers windup and recovery": "state.weakUntil=now+(state.attackWindup+.55)*1000" in s,
    "boss attack publishes monster and boss HUD telegraphs": "W.bus.emit('monster-telegraph'" in s and "W.bus.emit('boss-telegraph'" in s,
    "phase-one damage resolves after windup and within reach": "if(state.attackWindup<=0&&state.attackState==='windup')" in s and "distance<=(state.pendingAttackReach||reach)" in s,
    "dodge invulnerability is enforced on impact": "game.invulnerable<=0" in s,
    "ward mitigation applies to phase-one swing": "Math.min(.35,(W.state.skills.ward||0)*.08)" in s and "damage*(1-reduction)" in s,
    "phase-two projectile attack is preserved": "if(phase===2)" in s and "game.spawnProjectile(origin,state.damage*1.25" in s,
    "phase-three ground slam is preserved": "else if(phase===3)" in s and "boss-slam-warning" in s and "state.damage*1.7" in s,
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL"), name)
if not all(checks.values()):
    raise SystemExit("HOLLOW_KING_WINDUP_FAILED")
r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
if r.returncode:
    raise SystemExit(r.stderr)
print("PASS JavaScript syntax")
print("WILDBOUND_HOLLOW_KING_WINDUP_OK", len(checks) + 1, "checks")
