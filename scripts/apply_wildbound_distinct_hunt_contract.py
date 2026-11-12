#!/usr/bin/env python3
"""Require distinct anomaly species for the Ashen Veil hunt contract."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
base=root/'app/src/main/assets/www/js/wildbound'
mission=base/'backend/mission.js'; ui=base/'ui/interface.js'
for p in (mission,ui):
 if not p.is_file(): raise SystemExit(f'Missing mission module: {p}')
m=mission.read_text(encoding='utf-8'); u=ui.read_text(encoding='utf-8')
marker='WILDBOUND_DISTINCT_HUNT_CONTRACT_V1'
if marker in m:
 print('WILDBOUND_DISTINCT_HUNT_CONTRACT_ALREADY_APPLIED'); raise SystemExit(0)
old="reset(game){W.state.progress.purged=0;W.state.progress.boss=false;W.state.progress.contract=false;"
new="reset(game){W.state.progress.purged=0;W.state.progress.purgedTypes=[];W.state.progress.boss=false;W.state.progress.contract=false;"
if m.count(old)!=1: raise SystemExit(f'Mission reset anchor count: {m.count(old)}')
m=m.replace(old,new,1)
old="registerKill(game,enemy){if(enemy.kind==='boss'){W.state.progress.boss=true;W.state.progress.contract=true;W.bus.emit('contract-complete');return}W.state.progress.purged=(W.state.progress.purged||0)+1;if(W.state.progress.purged>=3){"
new="registerKill(game,enemy){if(enemy.kind==='boss'){W.state.progress.boss=true;W.state.progress.contract=true;W.bus.emit('contract-complete');return}const found=W.state.progress.purgedTypes||(W.state.progress.purgedTypes=[]);if(found.includes(enemy.type)){W.toast('SIGNATURE ALREADY PURGED');W.bus.emit('save');return}found.push(enemy.type);W.state.progress.purged=found.length;W.toast('ANOMALY PURGED · '+found.length+'/3');if(W.state.progress.purged>=W.data.mission.requiredPurges){"
if m.count(old)!=1: raise SystemExit(f'Mission kill anchor count: {m.count(old)}')
m=m.replace(old,new,1)
m='/* '+marker+' */\n'+m
old="(W.state.progress.purged||0)>=3?'WARD CIRCLE BREACHED':'TRACK & PURGE ANOMALIES'"
new="(W.state.progress.purged||0)>=W.data.mission.requiredPurges?'WARD CIRCLE BREACHED':'PURGE ANOMALY TYPES '+(W.state.progress.purged||0)+'/'+W.data.mission.requiredPurges"
if u.count(old)!=1: raise SystemExit(f'HUD objective anchor count: {u.count(old)}')
u=u.replace(old,new,1)
mission.write_text(m,encoding='utf-8'); ui.write_text(u,encoding='utf-8')
print('WILDBOUND_DISTINCT_HUNT_CONTRACT_APPLIED')
