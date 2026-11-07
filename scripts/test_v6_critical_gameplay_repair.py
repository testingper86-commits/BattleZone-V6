#!/usr/bin/env python3
"""Regression tests for the V6 runtime crash, HUD, touch and visual repair."""
from pathlib import Path
import subprocess, sys, tempfile

repo = Path(__file__).resolve().parents[1]
patcher = Path(__file__).with_name("apply_v6_critical_gameplay_repair.py")
with tempfile.TemporaryDirectory(prefix="bz-critical-repair-") as temp:
    root = Path(temp)
    html = root / "app/src/main/assets/www/index.html"
    html.parent.mkdir(parents=True)
    html.write_text("""<!doctype html><html><head></head><body>
const rootA=new THREE.CylinderGeometry(.035,.17,.78,5),rootB=rootA.clone(),rootC=rootA.clone(),rootD=rootA.clone();rootA.rotation.z=Math.PI/2;rootA.translate(.28,.23,0);rootB.rotation.z=-Math.PI/2;rootB.translate(-.28,.23,0);rootC.rotation.x=Math.PI/2;rootC.translate(0,.23,.28);rootD.rotation.x=-Math.PI/2;rootD.translate(0,.23,-.28);const branchA=new THREE.CylinderGeometry(.045,.1,1.15,5),branchB=branchA.clone(),branchC=branchA.clone();branchA.rotation.z=-.68;branchA.translate(-.34,2.35,.02);branchB.rotation.z=.68;branchB.translate(.34,2.4,-.02);branchC.rotation.x=.68;branchC.translate(.02,2.25,.34);
Object.entries(bzControlIcons).forEach(([id,v])=>{const e=$(id);if(e)e.innerHTML='<span class=\"bz-control-symbol\">'+v[0]+'</span><small>'+v[1]+'</small>'});
function hudUpdate(){const w=W[P.w],hp=Math.max(0,Math.ceil(P.hp));$('ht').textContent=hp;const f=$('hpf');f.style.width=Math.min(100,P.hp)+'%';f.style.background=P.hp>60?'green':P.hp>30?'yellow':'red';$('arm').innerHTML='';$('am').innerHTML=w.m;$('thrn').textContent='x1';$('gswn').textContent='Frag'}
R.setPixelRatio(LQ?.9:Math.min(devicePixelRatio,1.05));R.outputEncoding=THREE.sRGBEncoding;R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=1.08;
const hemi=new THREE.HemisphereLight(0xffffff,0x556633,.95);S.add(hemi);const sun=new THREE.DirectionalLight(0xffffff,.6*(MAP.nt?.25:1));
window.addEventListener('blur',clearGameplayInputs);document.addEventListener('visibilitychange',()=>{if(document.hidden)clearGameplayInputs()});
</body></html>""", encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    first = html.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    second = html.read_text(encoding="utf-8")
    assert first == second, "patcher is not idempotent"
    for token in ("rootA.rotateZ(Math.PI/2)", "rootB.rotateZ(-Math.PI/2)", "branchC.rotateX(.68)", "id=\"thrn\"", "id=\"gswn\"", "BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_V1"):
        assert token in second, f"missing repaired runtime token: {token}"
    css = html.parent / "css/v6-critical-gameplay-polish.css"
    assert css.is_file() and "#fire" in css.read_text() and "#bzSquadOrders" in css.read_text()
    assert "v6-critical-gameplay-polish.css" in second
    bad = root / "bad"
    (bad / "app/src/main/assets/www").mkdir(parents=True)
    (bad / "app/src/main/assets/www/index.html").write_text("<html><head></head></html>", encoding="utf-8")
    result = subprocess.run([sys.executable, str(patcher), str(bad)], capture_output=True, text=True)
    assert result.returncode != 0, "patcher must fail closed on unknown source"
print("CRITICAL_GAMEPLAY_REPAIR_TESTS_OK idempotent=true geometry=true hud=true controls=true graphics=true fail_closed=true")
