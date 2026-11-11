#!/usr/bin/env python3
"""Keep persisted hunter rank synchronized with XP progression."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
base=root/'app/src/main/assets/www/js/wildbound'
p=base/'backend/progression.js'; ui=base/'ui/interface.js'
for f in (p,ui):
 if not f.is_file(): raise SystemExit(f'Missing progression module: {f}')
s=p.read_text(encoding='utf-8'); u=ui.read_text(encoding='utf-8')
marker='WILDBOUND_PERSISTED_RANK_PROGRESSION_V1'
if marker in s:
 print('WILDBOUND_PERSISTED_RANK_ALREADY_APPLIED'); raise SystemExit(0)
old="s.player.kills++;s.player.xp+=xp;s.player.essence=(s.player.essence||0)+essence;W.bus.emit('progression',{xp,essence,rank:Math.min(5,1+Math.floor(s.player.xp/500))});"
new="s.player.kills++;const previousRank=s.player.rank||Math.min(5,1+Math.floor(s.player.xp/500));s.player.xp+=xp;s.player.essence=(s.player.essence||0)+essence;const rank=Math.min(5,1+Math.floor(s.player.xp/500)),rankUp=rank>previousRank;s.player.rank=rank;if(rankUp)W.toast('RANK ADVANCED · '+W.data.ranks[rank-1]);W.bus.emit('progression',{xp,essence,rank,rankUp});"
if s.count(old)!=1: raise SystemExit(f'Progression award anchor count: {s.count(old)}')
s=s.replace(old,new,1); s='/* '+marker+' */\n'+s
old="refresh(){let p=W.state.player;$('rank').textContent=['INITIATE','TRACKER','WARDEN','VEILBLADE','ASCENDANT'][Math.min(4,Math.floor(p.xp/500))];"
new="refresh(){let p=W.state.player,rank=p.rank||Math.min(5,1+Math.floor(p.xp/500));$('rank').textContent=W.data.ranks[Math.min(4,rank-1)];"
if u.count(old)!=1: raise SystemExit(f'Rank HUD anchor count: {u.count(old)}')
u=u.replace(old,new,1)
p.write_text(s,encoding='utf-8'); ui.write_text(u,encoding='utf-8')
print('WILDBOUND_PERSISTED_RANK_APPLIED')
