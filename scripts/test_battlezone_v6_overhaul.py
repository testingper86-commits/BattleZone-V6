#!/usr/bin/env python3
"""Regression checks for the Battle Zone V6.1 gameplay overhaul."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();www=root/'app/src/main/assets/www'
h=(www/'index.html').read_text(encoding='utf-8');m=(www/'js/models.js').read_text(encoding='utf-8');css=(www/'css/v6-overhaul.css').read_text(encoding='utf-8');gradle=(root/'app/build.gradle.kts').read_text(encoding='utf-8')
checks={
 'two weapons available before ground loot':"P.own=W.map((_,i)=>+(i<2))" in h and 'P.mags=W.map((w,i)=>i<2?w.m:0)' in h,
 'equipped weapon follows plane jump':"P.tp=true;gun.visible=false;window.BZActiveWeapon=W[P.w].n" in h and 'pm.setGun(W[P.w].n)' in h,
 'weapon swaps update rigged hand mount':'window.BZModels.setWeapon(window.pmS.root,W[P.w].n)' in h and 'setWeaponEntry(entry,name)' in m,
 'run is hold-to-sprint with pointer cancellation':'sprintBtn.addEventListener(\'pointerdown\',sprintOn)' in h and 'pointercancel\',sprintOff' in h and 'lostpointercapture\',sprintOff' in h,
 'interrupted touch clears run and movement':'key.sprint=false;sprintPointer=null' in h and 'window.addEventListener(\'blur\',clearGameplayInputs)' in h,
 'peek changes third-person shoulder camera':'shoulder=.7+ln*.92' in h and "bind('lnl',()=>P.lnT=-1" in h and "bind('lnr',()=>P.lnT=1" in h,
 'combat buttons have labels and symbols':'bzControlIcons' in h and "swap:['⇄','SWAP']" in h and "sprint:['»','RUN']" in h,
 'HUD fades irrelevant controls while moving and driving':'body.bz-moving .b:not(.on)' in css and 'body.driving .b:not(.drive-only)' in css and 'body.bz-running #sprint' in css,
 'lobby settings and map panels have independent scroll':'#lobby #lb-l #setc' in css and '#lobby #maps' in css and 'overflow-y:auto!important' in css and '#lobby #maps{position:absolute' in css,
 'map selection is restored above legacy hidden rule':'#lobby #maps{position:absolute' in css and 'display:flex!important' in css,
 'water has animated vertex and fragment detail':'bz-water-ripple-v1' in h and 'transformed.z +=' in h and 'gl_FragCoord.x*.035' in h,
 'tree trunks include roots and branches':'tkPDetail' in h and 'tkODetail' in h and 'branchA' in h,
 'grass uses a bounded instanced draw call':'new THREE.InstancedMesh(blades,mat,count)' in h and 'grass.count=placed' in h,
 'vehicles have added exterior and wheel details':'bzBaseBuildCar' in h and 'vehicle exterior and wheel detail' not in h and 'steel=mS' in h,
 'character-specific voice events use local voice packs':'bzVoiceLastPriority' in h and 'playCharacterVoice(nm)' in h and 'voicepacks/' in h,
 'voice respects mute and active playback is stopped':'if(!SND_ON)return;const n=1+Math.floor(Math.random()*3)' in h and 'window.bzVoiceAudio.pause()' in h,
 'Kenney rig attaches weapon to right hand': "'righthand'" in m and "'handslotright'" in m and 'bones.rightHand.add(entry.weaponMount)' in m,
 'armed locomotion stabilizes both arms':'function applyWeaponPose(entry,speed,time)' in m and 'blend(b.leftForeArm' in m and 'applyWeaponPose(e,sp,n*.001)' in m,
 'weapon replacement disposes old geometry and materials':'o.geometry.dispose()' in m and 'o.material.dispose()' in m,
 'two CC0 model families are loaded and assigned':'KAYKIT_OPERATORS' in m and 'templates=loaded' in m and 'function chooseTemplate' in m and 'animator(model,template)' in m,
 'KayKit weapon socket and native animation are supported':'handslotright' in m and "template.format==='glb'" in m and 'entry.template.format' in m,
 'Kenney skin textures load concurrently in stable order':'Promise.all(skins.map(async s=>' in m and 'tpl.skinTex=skinTex.slice()' in m,
 'offline character assets are present':all((www/p).is_file() for p in ['models/characters/kenney/Skins/skaterMaleA.png','models/characters/kenney/Skins/criminalMaleA.png','models/characters/kenney/Skins/cyborgFemaleA.png','models/characters/kenney/Skins/skaterFemaleA.png','models/characters/kaykit_v1_2/Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb','models/characters/kaykit_v1_2/License.txt']),
 'version metadata advanced exactly once':'versionCode = 3' in gradle and 'versionName = "1.2.0"' in gradle,
}
failed=[]
for name,ok in checks.items():
 print(('PASS ' if ok else 'FAIL ')+name)
 if not ok:failed.append(name)
if failed:raise SystemExit(f'{len(failed)} Battle Zone V6.1 checks failed')
print(f'BATTLEZONE_V6_OVERHAUL_REGRESSION_OK checks={len(checks)}')
