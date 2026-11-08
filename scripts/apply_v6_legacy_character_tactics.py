#!/usr/bin/env python3
"""Restore the original articulated operator look and wire tactics into legacy allies."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
p=files[0];s=p.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_LEGACY_CHARACTER_TACTICS_V1"
if marker in s:
    print(marker+" already applied");raise SystemExit(0)
def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f"{label}: expected exactly one source anchor, found {n}")
    s=s.replace(old,new,1)
# Keep the original articulated mkScout/animSc rig. Make profile identity and every material
# channel explicit so the existing skin selector updates the complete operator, not only trim.
name_anchor="function bzSelectedCharacter(){"
name_helper="function bzSelectedCharacterName(){try{const p=JSON.parse(localStorage.getItem('bzProfile')||'{}');return BZ_CHAR_DATA[p.equippedCharacter]?p.equippedCharacter:'Recruit'}catch(e){return 'Recruit'}}\n"
if "function bzSelectedCharacterName()" not in s: once(name_anchor,name_helper+name_anchor,"selected operator identity helper")
old="charName:(Object.keys(BZ_CHAR_DATA||{}).find(n=>BZ_CHAR_DATA[n].color===jc)||'Recruit')"
once(old,"charName:bzSelectedCharacterName()","stable operator identity")
old="mk(cl,gBox(.26,.32,.12),mtl(lk.pack,.9,0),0,0,0);"
new="const mPack=mtl(lk.pack,.9,0);mk(cl,gBox(.26,.32,.12),mPack,0,0,0);"
once(old,new,"retain operator backpack material")
look="""sc.lookMaterials={skin:mS,hair:mH,pants:mP,boot:mB,shirt:mSh,jacket:mJ,pack:mPack};
 sc.applyLook=(look,accent)=>{const set=(material,value)=>{if(material&&material.color&&value!=null&&Number.isFinite(Number(value)))material.color.setHex(Number(value))};set(mS,look.skin);set(mH,look.hair);set(mP,look.pants);set(mB,look.boot);set(mSh,look.shirt);set(mPack,look.pack);set(mJ,accent);return sc};
 """
old="const accent=mtl(jc,.32,.62);mk(torso,gBox(.035,.2,.025),accent,.13,.34,.185);"
once(old,old+"\n "+look,"full articulated operator material bindings")
refresh="""function bzRefreshCharacterAppearance(){const c=bzSelectedCharacter(),idx=Number.isInteger(Number(ST_.cur))&&SKN[Number(ST_.cur)]?Number(ST_.cur):0;Object.assign(PLOOK,{skin:c.skin??0xe0ac82,hair:c.hair??0x2b1b12,pants:c.pants??0x2c3a52,boot:0x2a1d14,shirt:c.shirt??c.color??0xe8e2d4,pack:c.color??0x3a4a6a});const accent=SKN[idx][1];[window.lobSc,window.pmS].forEach(model=>{if(model&&typeof model.applyLook==='function')model.applyLook(PLOOK,accent)});return bzSelectedCharacterName()}
window.BZRefreshCharacterAppearance=bzRefreshCharacterAppearance;
"""
once("function updCur(){",refresh+"function updCur(){","live operator appearance refresh")
old="if(window.lobSc)lobSc.jk.forEach(m=>m.material.color.set(SKN[ST_.cur][1]));if(window.pmS)pmS.jk.forEach(m=>m.material.color.set(SKN[ST_.cur][1]))"
once(old,"if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance()","legacy skin selector full-model refresh")
# Profile saves already centralize operator equip changes; refresh the preview and player rig there.
old="function save(){put('bzProfile',profile);refreshTop()}"
if old in s: s=s.replace(old,"function save(){put('bzProfile',profile);refreshTop();if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance()}",1)
# Ensure both already-created rigs receive the current profile after construction.
old="window.lobSc=sc;lc.position.set(0,1.1,4.6);"
if old in s: s=s.replace(old,"window.lobSc=sc;if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance();lc.position.set(0,1.1,4.6);",1)
old="window.pmS=pm;"
if old in s: s=s.replace(old,"window.pmS=pm;if(window.BZRefreshCharacterAppearance)window.BZRefreshCharacterAppearance();",1)
# Restore the original circular follow formation and nearest-threat defence inside the
# current squad update loop. Keep its LOS, medic, revive and cover systems as enhancements.
old="role=(bzOrder==='flank'?'flank':u.squadRole||(['assault','support','flank'][i%3]))"
new="role=(bzOrder==='flank'?'flank':bzOrder==='regroup'?'assault':bzOrder==='focus'?'assault':u.squadRole||(['assault','support','flank'][i%3]))"
once(old,new,"legacy regroup/focus combat role")
once("if(bzOrder==='regroup')en=null;","/* Legacy regroup preserves nearest-threat defence while returning to formation. */","regroup target retention")
old="let gx=px+Math.cos(P.yaw)*9+Math.sin(P.yaw)*(i-1)*5,gz=pz-Math.sin(P.yaw)*9+Math.cos(P.yaw)*(i-1)*5,speed=5.4;"
new="let gx=px+Math.cos(u.off*2)*4,gz=pz+Math.sin(u.off*2)*4,speed=5.4;"
once(old,new,"original circular ally formation")
old="}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34){gx=px;gz=pz;speed=7.8}else if(follow<5){gx=a.position.x;gz=a.position.z}else if(follow<10){gx=px+Math.cos(P.yaw)*7+Math.sin(P.yaw)*(i-1)*4;gz=pz-Math.sin(P.yaw)*7+Math.cos(P.yaw)*(i-1)*4;speed=3.4}}"
new="}else{u.squadTarget=null;u.squadCover=null;const follow=Math.hypot(px-a.position.x,pz-a.position.z);if(bzOrder==='hold'){gx=a.position.x;gz=a.position.z;speed=0}else if(follow>34){gx=px;gz=pz;speed=7.8}else if(follow<5){gx=a.position.x;gz=a.position.z}}"
once(old,new,"legacy ally follow and hold movement")
revive_old="if(P.down&&follow<3){u.reviveT=(u.reviveT||0)+dt;"
revive_new="if(P.down&&follow<4){u.reviveT=(u.reviveT||0)+dt;"
if revive_old in s:
    once(revive_old,revive_new,"legacy teammate revive radius")
elif revive_new not in s:
    raise SystemExit("legacy teammate revive radius: expected original or already-restored anchor")

# Verify critical old mechanisms remain after integration.
required=["function mkScout(","function animSc(","if(P.down&&follow<4)","window.BZSquadOrders?.get()"]
missing=[x for x in required if x not in s]
if missing: raise SystemExit("Legacy character or squad behaviour was not preserved: "+repr(missing))
s=s.replace("</html>","<!-- "+marker+" -->"+chr(10)+"</html>",1)
p.write_text(s,encoding="utf-8");print(marker+" applied",p)
