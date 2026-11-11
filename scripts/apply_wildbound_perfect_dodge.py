#!/usr/bin/env python3
"""Add a timed perfect-dodge counter to the existing WILDBOUND combat action."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
combat=root/'app/src/main/assets/www/js/wildbound/gameplay/combat.js'
ui=root/'app/src/main/assets/www/js/wildbound/ui/interface.js'
for f in (combat,ui):
 if not f.is_file(): raise SystemExit(f'Missing gameplay integration file: {f}')
s=combat.read_text(encoding='utf-8'); marker='WILDBOUND_PERFECT_DODGE_V1'
if marker not in s:
 anchor="W.actors.play(p,'dodge',true);p.position.x+=-Math.sin(p.rotation.y)*2.4;"
 if s.count(anchor)!=1: raise SystemExit(f'dodge action anchor count: {s.count(anchor)}')
 replacement="W.actors.play(p,'dodge',true);let perfect=false;for(const m of game.monsters){const u=m.userData;if(!u.alive||!(u.attackWindup>0))continue;if(W.physics.distance2D(p.position,m.position)>u.range+1.35)continue;u.attackWindup=0;u.attackCd=Math.max(u.attackCd||0,.85);u.stagger=Math.max(u.stagger||0,.85);u.weakUntil=performance.now()+1800;c.ultimate=Math.min(100,c.ultimate+18);perfect=true}if(perfect){W.toast('VEILSTEP · PERFECT DODGE');W.bus.emit('perfect-dodge')}p.position.x+=-Math.sin(p.rotation.y)*2.4;"
 s=s.replace(anchor,replacement,1); s='/* '+marker+' */\n'+s; combat.write_text(s,encoding='utf-8')
h=ui.read_text(encoding='utf-8'); hm='WILDBOUND_PERFECT_DODGE_HUD_V1'
if hm not in h and "W.bus.on('perfect-dodge'" not in h:
 anchor="W.bus.on('boss-slam-warning',()=>W.toast('VOID SLAM · DODGE NOW'));"
 if h.count(anchor)!=1:
  print('WILDBOUND_PERFECT_DODGE_HUD_HANDLED_BY_CANONICAL_UI')
 else:
  h=h.replace(anchor,anchor+"W.bus.on('perfect-dodge',()=>W.toast('COUNTER WINDOW · ANOMALY EXPOSED'));/* "+hm+" */",1); ui.write_text(h,encoding='utf-8')
print('WILDBOUND_PERFECT_DODGE_PATCHED')
