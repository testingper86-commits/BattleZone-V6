#!/usr/bin/env python3
"""Repair and complete the existing WILDBOUND hunt-signature tracking loop."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/rendering/runtime.js'
if not p.is_file(): raise SystemExit(f'Missing runtime module: {p}')
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_HUNT_TRACKING_LIFECYCLE_V1'
if marker in s:
 print('WILDBOUND_HUNT_TRACKING_ALREADY_APPLIED'); raise SystemExit(0)
changes=[
("game.trackCd=0;game.trackMarker=null;", "game.trackCd=0;game.trackExpires=0;if(game.trackMarker){game.scene.remove(game.trackMarker);game.trackMarker.geometry.dispose();game.trackMarker.material.dispose();game.trackMarker=null;}"),
("game.trackCd=8;const target=game.monsters.filter(m=>m.userData.alive).sort((a,b)=>a.position.distanceTo(game.player.position)-b.position.distanceTo(game.player.position))[0];if(!target){W.toast('NO ACTIVE SIGNATURE');return}game.trackType=target.userData.type;", "const target=game.monsters.filter(m=>m.userData.alive).sort((a,b)=>a.position.distanceTo(game.player.position)-b.position.distanceTo(game.player.position))[0];if(!target){W.toast('NO ACTIVE SIGNATURE');return}game.trackCd=8;game.trackExpires=performance.now()+6500;game.trackType=target.userData.type;"),
("game.trackMarker.position.set(target.position.x,.08,target.position.z);game.trackMarker.visible=true;W.toast('SIGNATURE LOCKED · '+target.userData.type.toUpperCase());", "game.trackMarker.position.set(target.position.x,.08,target.position.z);game.trackMarker.scale.setScalar(1);game.trackMarker.material.opacity=.85;game.trackMarker.visible=true;W.toast('LAST SIGNATURE · '+target.userData.type.toUpperCase());"),
("function update(dt){let p=game.player,s=W.state.player,c=W.state.combat;game.elapsed+=dt;", "function update(dt){let p=game.player,s=W.state.player,c=W.state.combat;game.elapsed+=dt;game.trackCd=Math.max(0,(game.trackCd||0)-dt);if(game.trackMarker&&game.trackMarker.visible){const remain=(game.trackExpires||0)-performance.now();if(remain<=0){game.trackMarker.visible=false;W.bus.emit('track-expired',game.trackType)}else{const pulse=performance.now()*.006;game.trackMarker.material.opacity=.3+Math.sin(pulse)*.2;game.trackMarker.scale.setScalar(1+Math.sin(pulse*.7)*.14)}}")]
for old,new in changes:
 n=s.count(old)
 if n!=1: raise SystemExit(f'Expected one tracking anchor, found {n}: {old[:120]}')
 s=s.replace(old,new,1)
s='/* '+marker+' */\n'+s
p.write_text(s,encoding='utf-8')
print('WILDBOUND_HUNT_TRACKING_APPLIED')
