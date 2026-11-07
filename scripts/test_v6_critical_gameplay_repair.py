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
R.setPixelRatio(LQ?.9:Math.min(devicePixelRatio,1.05));R.outputEncoding=THREE.sRGBEncoding;R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=1.08;const ratio=[.82,1,1.2][bzQualityTier];
const hemi=new THREE.HemisphereLight(0xffffff,0x556633,.95);S.add(hemi);const sun=new THREE.DirectionalLight(0xffffff,.6*(MAP.nt?.25:1));
window.addEventListener('blur',clearGameplayInputs);document.addEventListener('visibilitychange',()=>{if(document.hidden)clearGameplayInputs()});
const gr=new THREE.Mesh(new THREE.BufferGeometry(),BZMaterial('grass',18,.98));
const M=c=>new THREE.MeshLambertMaterial({color:c});
t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat,repeat);t.anisotropy=1;
const BARK=new THREE.MeshLambertMaterial({map:barkT});
const wall=new THREE.MeshLambertMaterial({color:c,map:t}),roof=new THREE.MeshLambertMaterial({color:new THREE.Color(c).multiplyScalar(.55)});
const setOrder=value=>{if(!allowed.has(value))return;order=value;try{localStorage.setItem('bzSquadOrder',value)}catch(e){};root.querySelectorAll('[data-bz-order]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bzOrder===order)));};
window.BZSquadOrders=Object.freeze({get:()=>order,getFocusTarget:focusTarget});
const role=(window.BZSquadOrders?.get()==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3])),side=u.squadSide||((i%2)?1:-1),px=P.x,pz=P.z;
if(window.BZSquadOrders?.get()==='regroup'&&Math.hypot(px-a.position.x,pz-a.position.z)>12)en=null;
else{u.cd=.22;u.squadThink=0}}
function bzV6TargetIsValid(target){if(target.p)return !!P.alive&&!P.air;const actor=target.o,u=actor&&actor.userData;if(!actor||!u||!u.alive||!actor.position)return false;return BZ_MODE==='TDM'?!!u.ally:!u.ally;}
const consider=(x,z,candidate,priority,hp)=>{if(!Number.isFinite(x)||!Number.isFinite(z))return;};
forEachActor(actor=>{if(actor===bot||!actor||!actor.userData||!actor.userData.alive)return;});
function shoot(){if(P.cd>0||P.rl>0||P.air||P.down)return;}
window.shotSfx=function(){if(!SND_ON)return;};
if(!u.alive||u.airDrop||u.falling)return;
</body></html>""", encoding="utf-8")
    models = root / "app/src/main/assets/www/js/models.js"
    models.parent.mkdir(parents=True, exist_ok=True)
    models.write_text("""function findBone(model,keys){return null}
function register(obj,model,opt){
 const bones={rightHand:findBone(model,['righthand','handr','handslotright']),rightArm:findBone(model,['rightarm','upperarmr','armright']),rightForeArm:findBone(model,['rightforearm','forearmr']),leftArm:findBone(model,['leftarm','upperarml','armleft']),leftForeArm:findBone(model,['leftforearm','forearml']),spine:findBone(model,['spine','spine1','chest','body'])};
 const entry={obj,model,an, bones,template,lx:obj.position.x,lz:obj.position.z,air:opt.air||null,far:!!opt.cull,speedOf:opt.speedOf||null,weaponMount:null,weaponName:null,weaponBasePosition:null,weaponBaseRotation:null};
}
""", encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    first = html.read_text(encoding="utf-8")
    first_models = models.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    second = html.read_text(encoding="utf-8")
    second_models = models.read_text(encoding="utf-8")
    assert first == second, "patcher is not idempotent"
    assert first_models == second_models, "character gear patcher is not idempotent"
    for token in ("rootA.rotateZ(Math.PI/2)", "rootB.rotateZ(-Math.PI/2)", "branchC.rotateX(.68)", "id=\"thrn\"", "id=\"gswn\"", "BATTLEZONE_V6_CRITICAL_GAMEPLAY_REPAIR_V2", "R.toneMappingExposure=1.2;", "const ratio=[.88,1.12,1.32][bzQualityTier];"):
        assert token in second, f"missing repaired runtime token: {token}"
    css = html.parent / "css/v6-critical-gameplay-polish.css"
    assert css.is_file() and "#fire" in css.read_text() and "#bzSquadOrders" in css.read_text()
    assert "v6-critical-gameplay-polish.css" in second
    for token in ("BATTLEZONE_V6_FINAL_GAMEPLAY_VISUAL_OVERHAUL_V3", "bzOrder==='regroup'", "bzOrder==='hold'", "u.airDrop||u.falling||u.chute", "P.y>(P.gh||1.6)+.22", "bzGroundTexture", "MeshStandardMaterial({color:c,roughness:.82,metalness:.04})"):
        assert token in second, f"missing V3 runtime token: {token}"
    model_text = models.read_text(encoding="utf-8")
    assert "BATTLEZONE_V6_OPERATOR_ARMOR_REDESIGN_V3" in model_text and "bzAttachOperatorGear(model,bones,opt.skinKey||'Recruit')" in model_text and model_text.count("function bzAttachOperatorGear(")==1
    css_text = css.read_text(encoding="utf-8")
    assert "BATTLEZONE_V6_FINAL_UI_OVERHAUL_V3" in css_text
    assert "right:calc(var(--bz-safe-r) + 106px)" in css_text
    bad = root / "bad"
    (bad / "app/src/main/assets/www").mkdir(parents=True)
    (bad / "app/src/main/assets/www/index.html").write_text("<html><head></head></html>", encoding="utf-8")
    result = subprocess.run([sys.executable, str(patcher), str(bad)], capture_output=True, text=True)
    assert result.returncode != 0, "patcher must fail closed on unknown source"
print("CRITICAL_GAMEPLAY_REPAIR_TESTS_OK idempotent=true geometry=true hud=true controls=true graphics=true fail_closed=true")
