from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
html=root/'app/src/main/assets/www/index.html'
s=html.read_text(encoding='utf-8')
marker='BATTLE_ZONE_OFFLINE_HUB_COMPLETION_V1'
if marker in s:
    print('Offline hub completion already applied; source is unchanged.')
    raise SystemExit(0)
nav_old="const nav=[['profile','Profile'],['maps','Maps'],['settings','Settings'],['inventory','Inventory'],['shop','Shop'],['rank','Rank & Season']];"
nav_new="const nav=[['profile','Profile'],['maps','Maps'],['settings','Settings'],['inventory','Inventory'],['shop','Shop'],['rank','Rank & Season'],['statistics','Statistics'],['history','Match History']];"
if s.count(nav_old)!=1: raise SystemExit(f'Player hub navigation anchor expected once, found {s.count(nav_old)}')
s=s.replace(nav_old,nav_new,1)
render_old="if(page==='profile')profilePage();else if(page==='maps')mapsPage();else if(page==='settings')settingsPage();else if(page==='inventory')inventoryPage();else if(page==='shop')shopPage();else rankPage();}"
render_new="if(page==='profile')profilePage();else if(page==='maps')mapsPage();else if(page==='settings')settingsPage();else if(page==='inventory')inventoryPage();else if(page==='shop')shopPage();else if(page==='statistics')statisticsPage();else if(page==='history')historyPage();else rankPage();}"
if s.count(render_old)!=1: raise SystemExit(f'Player hub render anchor expected once, found {s.count(render_old)}')
s=s.replace(render_old,render_new,1)
anchor='window.BZPlayerHub={open,awardXP,profile};'
if s.count(anchor)!=1: raise SystemExit(f'Player hub export anchor expected once, found {s.count(anchor)}')
addition=r"""// BATTLE_ZONE_OFFLINE_HUB_COMPLETION_V1
// These views consume actual local match counters/results; no sample records or network data are shown.
function statisticsPage(){
 const progress=get('bzp',{}),career=get('bzx',{dmg:0,sec:0}),best=get('bzbest',{k:0,sec:0});
 const matches=Math.max(0,Number(progress.m)||0),wins=Math.max(0,Number(progress.w)||0),kills=Math.max(0,Number(progress.k)||0);
 const damage=Math.max(0,Math.round(Number(career.dmg)||0)),seconds=Math.max(0,Math.floor(Number(career.sec)||0));
 const bestKills=Math.max(0,Number(best.k)||0),bestTime=Math.max(0,Number(best.sec)||0);
 const rate=matches?Math.min(100,wins/matches*100):0,avg=matches?kills/matches:0;
 const fmtTime=n=>Math.floor(n/60)+'m '+('0'+Math.floor(n%60)).slice(-2)+'s';
 content.innerHTML=`<h2>Career statistics</h2><p class="bhmuted">Calculated from this device's saved offline match progression.</p><div class="bhgrid"><div class="bhcard"><div class="bhmuted">MATCHES PLAYED</div><h2>${matches.toLocaleString()}</h2></div><div class="bhcard"><div class="bhmuted">WINS</div><h2>${wins.toLocaleString()}</h2><div class="bhbar"><i style="width:${rate}%"></i></div><div class="bhmuted">${rate.toFixed(1)}% win rate</div></div><div class="bhcard"><div class="bhmuted">TOTAL ELIMINATIONS</div><h2>${kills.toLocaleString()}</h2><div class="bhmuted">${avg.toFixed(2)} per match</div></div><div class="bhcard"><div class="bhmuted">DAMAGE DEALT</div><h2>${damage.toLocaleString()}</h2></div><div class="bhcard"><div class="bhmuted">TIME SURVIVED</div><h2>${fmtTime(seconds)}</h2></div><div class="bhcard"><div class="bhmuted">BEST MATCH</div><h2>${bestKills} eliminations</h2><div class="bhmuted">${fmtTime(bestTime)} survived</div></div><div class="bhcard"><div class="bhmuted">PLAYER LEVEL</div><h2>${Number(profile.level)||1}</h2><div class="bhmuted">${Number(profile.xp)||0} XP · ${Number(profile.rankPoints)||0} RP</div></div><div class="bhcard"><div class="bhmuted">LOCAL CURRENCY</div><h2>🪙 ${coins().toLocaleString()}</h2></div></div><div class="bhcard"><b>Offline profile</b><p class="bhmuted">Statistics are stored on this device. They are not a global leaderboard and are not uploaded.</p><button class="primary" data-open-history>View match history</button></div>`;
 content.querySelector('[data-open-history]').onclick=()=>open('history');
}
function historyPage(){
 const records=get('bzOfflineMatchHistory',[]);const safe=Array.isArray(records)?records.filter(x=>x&&typeof x==='object').slice(0,50):[];
 const modes=[['all','All modes'],['BR','Battle Royale'],['TDM','Team Deathmatch'],['FFA','Free-for-All']];
 content.innerHTML=`<h2>Match history</h2><p class="bhmuted">Your latest 50 completed offline matches, saved locally on this device.</p><div class="bhrow"><label for="bhHistoryMode">Filter</label><select id="bhHistoryMode">${modes.map(([v,t])=>`<option value="${v}">${t}</option>`).join('')}</select></div><div id="bhHistoryRows"></div><p class="bhmuted">Replay playback is not available: the game does not currently record deterministic replay data.</p>`;
 const select=$('bhHistoryMode'),rows=$('bhHistoryRows');
 const draw=()=>{const list=safe.filter(r=>select.value==='all'||r.mode===select.value);rows.innerHTML=list.length?list.map(r=>`<div class="bhcard" style="margin:8px 0"><div class="bhrow"><b>${r.won?'VICTORY':'MATCH COMPLETE'} · ${esc(r.modeName||r.mode||'Offline')}</b><span class="bhpill">${esc(r.map||'Unknown map')}</span></div><div class="bhgrid"><div><span class="bhmuted">ELIMINATIONS</span><b>${Math.max(0,Number(r.kills)||0)}</b></div><div><span class="bhmuted">DAMAGE</span><b>${Math.max(0,Number(r.damage)||0).toLocaleString()}</b></div><div><span class="bhmuted">DURATION</span><b>${Math.floor(Math.max(0,Number(r.seconds)||0)/60)}m ${('0'+Math.floor(Math.max(0,Number(r.seconds)||0)%60)).slice(-2)}s</b></div><div><span class="bhmuted">COINS EARNED</span><b>+${Math.max(0,Number(r.coins)||0)}</b></div></div><div class="bhmuted">${new Date(Number(r.timestamp)||0).toLocaleString()}</div></div>`).join(''):'<div class="bhcard">No completed matches have been recorded yet. Play an offline match to populate this archive.</div>'};
 select.onchange=draw;draw();
}
// Record each completed match once at the existing progression-save boundary.
if(typeof window.saveRes==='function'&&!window.__bzHistoryRecorder){
 const saveResult=window.saveRes;window.__bzHistoryRecorder=true;
 window.saveRes=function(win){
  const beforeCareer=get('bzx',{dmg:0,sec:0}),beforeProgress=get('bzp',{});
  const beforeDamage=Math.max(0,Number(beforeCareer.dmg)||0),beforeSeconds=Math.max(0,Number(beforeCareer.sec)||0),beforeCoins=Math.max(0,Number(beforeProgress.c)||0);
  const result=saveResult.apply(this,arguments);
  try{
   const mode=typeof BZ_MODE==='string'?BZ_MODE:'BR',map=typeof MAPS!=='undefined'&&MAPS[MI]?MAPS[MI].n:'Unknown map';
   const afterCareer=get('bzx',{dmg:0,sec:0}),afterProgress=get('bzp',{});
   const afterDamage=Math.max(0,Number(afterCareer.dmg)||0),afterSeconds=Math.max(0,Number(afterCareer.sec)||0),afterCoins=Math.max(0,Number(afterProgress.c)||0);
   const rows=get('bzOfflineMatchHistory',[]),history=Array.isArray(rows)?rows:[];
   history.unshift({timestamp:Date.now(),mode,modeName:({BR:'Battle Royale',TDM:'Team Deathmatch',FFA:'Free-for-All'})[mode]||mode,map,won:!!win,kills:Math.max(0,Number(P?.kills)||0),damage:Math.max(0,Math.round(afterDamage-beforeDamage)),seconds:Math.max(0,Math.floor(afterSeconds-beforeSeconds)),coins:Math.max(0,Math.round(afterCoins-beforeCoins))});
   put('bzOfflineMatchHistory',history.slice(0,50));
  }catch(e){try{console.warn('Could not save offline match history',e)}catch(_){}}
  return result;
 };
}
"""
s=s.replace(anchor,addition+'\n'+anchor,1)
html.write_text(s,encoding='utf-8')
print('OFFLINE_HUB_COMPLETION_APPLIED')
