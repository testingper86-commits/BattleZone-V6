#!/usr/bin/env python3
"""Regression tests for the BattleZone V6 touch HUD and landing repair."""
from pathlib import Path
import subprocess, sys, tempfile

patcher = Path(__file__).with_name("apply_v6_touch_control_rebuild.py")
with tempfile.TemporaryDirectory(prefix="bz-touch-rebuild-") as temp:
    root = Path(temp)
    html = root / "app/src/main/assets/www/index.html"
    html.parent.mkdir(parents=True)
    html.write_text("""<!doctype html><html><head></head><body>
let CL={};try{CL=JSON.parse(sg('bzc2')||'{}')}catch(e){}
const bind=(id,d,u)=>{const el=$(id);el.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();try{el.setPointerCapture(e.pointerId)}catch(x){}if(CE){el._dr=1;return}el.classList.add('on');d()});  el.addEventListener('pointermove',e=>{if(CE&&el._dr){CL[id]={x:(e.clientX-el.offsetWidth/2)/Math.max(1,innerWidth),y:(e.clientY-el.offsetHeight/2)/Math.max(1,innerHeight)};applyCL()}});  const up=e=>{el._dr=0;if(!el.classList.contains('on'))return;el.classList.remove('on');if(u)u()};el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);el.addEventListener('lostpointercapture',up)};
if(P.y<=1.6){P.air=0;P.y=1.6;P.vy=0;P.tp=true;P.lnT=1;msg('Landed! Find a weapon')}
</body></html>""", encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    first = html.read_text(encoding="utf-8")
    css = html.parent / "css/v6-touch-control-rebuild.css"
    js = html.parent / "js/v6-touch-control-rebuild.js"
    assert css.is_file() and js.is_file()
    assert "gS(P.x,P.z,P.y-1.6)+1.6" in first
    assert "P.lnT=0;P.ln=0" in first
    assert "BZ_CONTROL_LAYOUT_VERSION='3'" in first
    assert "activePointers=new Set()" in first
    c = css.read_text(encoding="utf-8")
    for token in ("#joy{", "#fire{", "#jump{", "#crouch{", "#prone{", "#scope{", "#bzSquadOrders{", "safe-area-inset-bottom", "orientation:portrait", "orientation:landscape"):
        assert token in c, f"missing responsive control rule: {token}"
    assert "body:not(.bz-control-edit)" in c
    assert "bz-control-edit" in js
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    assert first == html.read_text(encoding="utf-8"), "patcher must be idempotent"
    bad = root / "bad"
    (bad / "app/src/main/assets/www").mkdir(parents=True)
    (bad / "app/src/main/assets/www/index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
    result = subprocess.run([sys.executable, str(patcher), str(bad)], capture_output=True, text=True)
    assert result.returncode != 0, "unknown runtime must fail closed"
print("TOUCH_CONTROL_REBUILD_TESTS_OK layout=true multitouch=true terrain_landing=true lean_reset=true idempotent=true")
