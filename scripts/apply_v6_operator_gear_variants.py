#!/usr/bin/env python3
"""Add deterministic original equipment silhouettes to the 17 procedural operators."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected one index.html, found {len(paths)}')
p=paths[0]; source=p.read_text(encoding='utf-8'); marker='BATTLEZONE_V6_OPERATOR_GEAR_VARIANTS_V1'
if marker in source:
    print(marker,'already applied'); raise SystemExit(0)
def one(old,new,label):
    global source
    n=source.count(old)
    if n!=1: raise SystemExit(f'{label}: expected one exact anchor, found {n}')
    source=source.replace(old,new,1)
helper="""function bzOperatorGearStyle(name){const names=Object.keys(BZ_CHAR_DATA);const index=names.indexOf(name);return index<0?0:index%8;}\n"""
one('function mkScout(jc,gun,lk){',helper+'function mkScout(jc,gun,lk){','operator gear style helper')
one('const hd=q.head=Gp(torso,0,.66,0);mk(hd,gSph(.12,16),mS,0,.12,0,.94,1.12,1);','const hd=q.head=Gp(torso,0,.66,0);const gearStyle=bzOperatorGearStyle(sc.charName);sc.gearStyle=gearStyle;mk(hd,gSph(.12,16),mS,0,.12,0,.94,1.12,1);','profile-specific headgear selection')
one('if(lk.cap){mk(hd,gCyl(.127,.127,.05,12),mJ,0,.235,0);mk(hd,gBox(.15,.012,.1),mJ,0,.21,.1)}','if(lk.cap&&gearStyle===0){mk(hd,gCyl(.127,.127,.05,12),mJ,0,.235,0);mk(hd,gBox(.15,.012,.1),mJ,0,.21,.1)}','profile-specific cap selection')
gear="""\n // Eight deterministic gear silhouettes distinguish original operators without external assets.\n if(gearStyle===0){mk(hd,gBox(.17,.032,.04),trim,0,.145,.115);mk(torso,gBox(.09,.13,.055),darkKit,.19,.2,-.07)}\n else if(gearStyle===1){mk(hd,new THREE.SphereGeometry(.145,12,8,0,Math.PI*2,0,Math.PI*.64),darkKit,0,.13,-.025);mk(hd,gBox(.145,.052,.035),kit,0,.035,.115)}\n else if(gearStyle===2){mk(hd,gCyl(.03,.03,.035,8),trim,-.13,.12,0);mk(hd,gCyl(.03,.03,.035,8),trim,.13,.12,0);mk(torso,gBox(.07,.13,.055),darkKit,.19,.2,-.07);mk(torso,gCyl(.006,.006,.12,6),trim,.19,.32,-.07)}\n else if(gearStyle===3){mk(hd,new THREE.SphereGeometry(.14,12,8,0,Math.PI*2,0,Math.PI*.58),kit,0,.14,-.02);mk(hd,gBox(.18,.035,.04),darkKit,0,.145,.11);mk(torso,gCyl(.115,.12,.06,10),accent,0,.58,0)}\n else if(gearStyle===4){mk(hd,new THREE.SphereGeometry(.14,12,8,0,Math.PI*2,0,Math.PI*.56),darkKit,0,.145,-.01);mk(hd,gBox(.18,.03,.055),trim,0,.14,.105);mk(torso,gSph(.095,8),kit,-.23,.5,0,1.3,.78,1);mk(torso,gSph(.095,8),kit,.23,.5,0,1.3,.78,1);mk(torso,gBox(.21,.17,.035),accent,0,.27,.19)}\n else if(gearStyle===5){mk(hd,gCyl(.008,.008,.18,6),trim,-.07,.27,-.015);mk(hd,gSph(.018,6),accent,-.07,.36,-.015);mk(torso,gBox(.085,.12,.07),kit,.19,.2,-.07);mk(cl,gBox(.28,.3,.16),darkKit,0,-.02,-.08)}\n else if(gearStyle===6){mk(hd,gBox(.15,.07,.04),darkKit,0,.04,.115);mk(hd,gSph(.035,8),trim,-.13,.12,0);mk(hd,gSph(.035,8),trim,.13,.12,0);mk(torso,gSph(.1,8),accent,-.23,.5,0,1.3,.8,1);mk(torso,gSph(.1,8),accent,.23,.5,0,1.3,.8,1)}\n else if(gearStyle===7){mk(hd,gBox(.18,.055,.045),trim,0,.15,.11);mk(torso,gBox(.08,.15,.06),kit,-.19,.22,-.07);mk(torso,gBox(.08,.15,.06),kit,.19,.22,-.07);mk(cl,gBox(.3,.28,.16),kit,0,-.02,-.08)}\n"""
one('const accent=mtl(jc,.32,.62);mk(torso,gBox(.035,.2,.025),accent,.13,.34,.185);','const accent=mtl(jc,.32,.62);mk(torso,gBox(.035,.2,.025),accent,.13,.34,.185);'+gear,'attach profile-specific equipment')
one('</html>','<!-- '+marker+' -->\n</html>','operator gear marker')
p.write_text(source,encoding='utf-8'); print(marker,'applied')
