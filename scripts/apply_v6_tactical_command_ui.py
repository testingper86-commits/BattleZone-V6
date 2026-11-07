#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit("Expected exactly one game index.html")
html=files[0]; s=html.read_text(encoding="utf-8"); marker="BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1"
if marker in s: print("TACTICAL_UI_ALREADY_APPLIED"); raise SystemExit(0)
old_nav="const nav=[['profile','Profile'],['maps','Maps'],['settings','Settings'],['inventory','Inventory'],['shop','Shop'],['rank','Rank & Season'],['statistics','Statistics'],['history','Match History']];"
new_nav="const nav=[['command','Command Center'],['deployment','Deployment Lobby'],['operator','Operator Bay'],['armory','Armory'],['squad','Squad Command'],['zones','Mission Zones'],['combat','Combat HUD'],['pause','Pause Menu'],['results','After Action'],['service','Service Record'],['settings','Settings'],['controls','Controls'],['statistics','Statistics'],['history','Match History']];"
old_render="if(page==='profile')profilePage();else if(page==='maps')mapsPage();else if(page==='settings')settingsPage();else if(page==='inventory')inventoryPage();else if(page==='shop')shopPage();else if(page==='statistics')statisticsPage();else if(page==='history')historyPage();else rankPage();}"
new_render="if(page==='command')commandPage();else if(page==='deployment')deploymentPage();else if(page==='operator')profilePage();else if(page==='armory')shopPage();else if(page==='squad')squadPage();else if(page==='zones')mapsPage();else if(page==='combat')combatPage();else if(page==='pause')pausePage();else if(page==='results')resultsPage();else if(page==='service'||page==='rank')rankPage();else if(page==='settings')settingsPage();else if(page==='controls')controlsPage();else if(page==='statistics')statisticsPage();else if(page==='history')historyPage();else if(page==='profile')profilePage();else if(page==='maps')mapsPage();else if(page==='shop')shopPage();else if(page==='inventory')inventoryPage();else rankPage();}"
old_open="function open(p){page=p;render();hub.classList.add('on')};function close(){hub.classList.remove('on')};"
new_open="function open(p){page=p;window.BZ_TACTICAL_PAUSED=true;render();hub.classList.add('on')};function close(){hub.classList.remove('on');window.BZ_TACTICAL_PAUSED=false};"
for label,old in (("nav",old_nav),("renderer",old_render),("open-close",old_open)):
 if s.count(old)!=1: raise SystemExit(label+" anchor count "+str(s.count(old)))
pages = r'''
function commandPage(){
 const maps=(typeof MAPS!=='undefined'?MAPS:(window.MAPS||[])),m=maps[Number(location.hash.slice(1)||0)]||maps[0]||{n:'Not selected',d:'Choose a battlefield'};
 const order=window.BZSquadOrders&&window.BZSquadOrders.get?window.BZSquadOrders.get():'regroup';
 content.innerHTML='<div class="bz-tac-hero"><small>TACTICAL OPERATIONS / OFFLINE</small><h2>COMMAND CENTER</h2><p>Live local profile, battlefield and squad state.</p><button class="bz-tac-primary" data-tac-open="deployment">PREPARE DEPLOYMENT</button><span class="bz-tac-mark">BZ</span></div>'+
 '<div class="bz-tac-stats"><div><small>PLAYER LEVEL</small><b>'+Number(profile.level||1)+'</b><span>'+Number(profile.xp||0)+' XP</span></div><div><small>RANK</small><b>'+esc(rank())+'</b><span>'+esc(rankTier())+'</span></div><div><small>COINS</small><b>'+Number(coins()).toLocaleString()+'</b><span>LOCAL WALLET</span></div><div><small>SQUAD ORDER</small><b>'+esc(String(order).toUpperCase())+'</b><span>LIVE AI STATE</span></div></div>'+
 '<div class="bz-tac-section"><div><small>ACTIVE THEATER</small><h3>'+esc(m.n||'Battlefield')+'</h3><p>'+esc(m.d||'Select a battlefield')+'</p></div><button data-tac-open="zones">CHANGE ZONE</button></div>'+
 '<div class="bz-tac-grid"><button data-tac-open="operator"><b>OPERATOR BAY</b><span>Profile and equipped operator</span></button><button data-tac-open="armory"><b>ARMORY</b><span>Owned cosmetics and shop</span></button><button data-tac-open="squad"><b>SQUAD COMMAND</b><span>Issue live orders to active allies</span></button><button data-tac-open="settings"><b>SETTINGS</b><span>Existing game settings</span></button></div>';
 content.querySelectorAll('[data-tac-open]').forEach(b=>b.onclick=()=>open(b.dataset.tacOpen));
}
function deploymentPage(){
 const val=id=>{const e=$(id);return e?(e.querySelector('.v')?e.querySelector('.v').textContent:e.textContent):'Unavailable'};
 const maps=(typeof MAPS!=='undefined'?MAPS:(window.MAPS||[])),m=maps[Number(location.hash.slice(1)||0)]||maps[0]||{n:'Not selected',d:''};
 content.innerHTML='<div class="bz-tac-pagehead"><small>PRE-DEPLOYMENT CHECKLIST</small><h2>DEPLOYMENT LOBBY</h2><p>Current settings from the live lobby.</p></div><div class="bz-tac-stats"><div><small>BATTLEFIELD</small><b>'+esc(m.n||'Unknown')+'</b><span>'+esc(m.d||'')+'</span></div><div><small>TEAM SIZE</small><b>'+esc(val('sqd'))+'</b><span>LOCAL CONFIG</span></div><div><small>BOT DIFFICULTY</small><b>'+esc(val('dif'))+'</b><span>LOCAL CONFIG</span></div><div><small>WEATHER</small><b>'+esc(val('wxc'))+'</b><span>LOCAL CONFIG</span></div></div><div class="bz-tac-actions"><button class="bz-tac-secondary" id="bzTacMap">SELECT BATTLEFIELD</button><button class="bz-tac-primary" id="bzTacDeploy">OPEN DEPLOYMENT CONFIRMATION</button></div><p class="bz-tac-note">The original map preview and launch validation remain in control of deployment.</p>';
 $('bzTacMap').onclick=()=>open('zones');$('bzTacDeploy').onclick=()=>{close();$('go2')?.click()};
}
function squadPage(){
 const root=$('bzSquadOrders'),active=!!(root&&root.dataset.active==='1'),current=window.BZSquadOrders&&window.BZSquadOrders.get?window.BZSquadOrders.get():'regroup';
 const rows=[['regroup','REGROUP','Bring living allies toward the player'],['focus','FOCUS','Direct allies toward the nearest valid enemy'],['flank','FLANK','Use existing flanking movement'],['hold','HOLD','Hold position while preserving combat']];
 content.innerHTML='<div class="bz-tac-pagehead"><small>FIRETEAM TACTICS</small><h2>SQUAD COMMAND</h2><p>Uses the existing V6 squad AI order system.</p></div><div class="bz-tac-order-grid">'+rows.map(x=>'<button data-tac-order="'+x[0]+'" '+(active?'':'disabled')+' class="'+(current===x[0]?'selected':'')+'"><b>'+x[1]+'</b><span>'+x[2]+'</span></button>').join('')+'</div><p class="bz-tac-note">'+(active?'Orders are live for deployed allies.':'Commands activate during a match when a living squad member is deployed.')+'</p>';
 content.querySelectorAll('[data-tac-order]').forEach(b=>b.onclick=()=>{document.querySelector('[data-bz-order="'+b.dataset.tacOrder+'"]')?.click();open('squad')});
}
function combatPage(){
 const s=window.BZGameState||{};
 content.innerHTML='<div class="bz-tac-pagehead"><small>IN-MISSION INTERFACE</small><h2>COMBAT HUD</h2><p>The actual Three.js battlefield and touch HUD remain the gameplay surface.</p></div><div class="bz-tac-stats"><div><small>MATCH STATE</small><b>'+(s.started?'ACTIVE':'NOT DEPLOYED')+'</b><span>LIVE</span></div><div><small>HEALTH</small><b>'+(s.started?(s.health||0)+' HP':'—')+'</b><span>OPERATOR</span></div><div><small>STATUS</small><b>'+(s.started?(s.alive?'ALIVE':'DOWN'):'—')+'</b><span>OPERATOR</span></div><div><small>WEAPON</small><b>'+esc(s.weapon||'—')+'</b><span>EQUIPPED</span></div></div><button class="bz-tac-primary" id="bzTacReturn">RETURN TO BATTLEFIELD</button><p class="bz-tac-note">Close the command panel to return to live gameplay.</p>';
 $('bzTacReturn').onclick=close;
}
function pausePage(){
 window.BZ_TACTICAL_PAUSED=true;const s=window.BZGameState||{};
 content.innerHTML='<div class="bz-tac-pause"><small>TACTICAL MENU / LOCAL PAUSE</small><h2>MISSION PAUSED</h2><p>The simulation update loop is suspended while this menu is open.</p><div class="bz-tac-stats"><div><small>STATE</small><b>'+(s.started?'PAUSED':'LOBBY')+'</b></div><div><small>HEALTH</small><b>'+(s.started?(s.health||0)+' HP':'—')+'</b></div></div><button class="bz-tac-primary" id="bzTacResume">RESUME MISSION</button><button class="bz-tac-secondary" id="bzTacSettings">SETTINGS</button></div>';
 $('bzTacResume').onclick=close;$('bzTacSettings').onclick=()=>open('settings');
}
function resultsPage(){
 const rows=get('bzOfflineMatchHistory',[]),r=Array.isArray(rows)?rows[0]:null;
 if(!r){content.innerHTML='<div class="bz-tac-pagehead"><small>MISSION DEBRIEF</small><h2>AFTER ACTION REPORT</h2><p>Verified local match history only.</p></div><div class="bz-tac-empty"><b>NO COMPLETED-MATCH REPORT RECORDED</b><p>Complete an offline match to populate this report. Match data is never invented.</p></div>';return;}
 const duration=Math.max(0,Math.floor(Number(r.seconds)||0));
 content.innerHTML='<div class="bz-tac-pagehead"><small>MISSION DEBRIEF</small><h2>AFTER ACTION REPORT</h2><p>Latest completed offline match from this device.</p></div><div class="bz-tac-hero"><small>'+esc(r.modeName||r.mode||'OFFLINE MATCH')+'</small><h2>'+(r.won?'MISSION SUCCESS':'MATCH COMPLETE')+'</h2><p>'+esc(r.map||'Unknown map')+' · '+new Date(Number(r.timestamp)||0).toLocaleString()+'</p></div><div class="bz-tac-stats"><div><small>ELIMINATIONS</small><b>'+Math.max(0,Number(r.kills)||0)+'</b></div><div><small>DAMAGE</small><b>'+Math.max(0,Number(r.damage)||0).toLocaleString()+'</b></div><div><small>DURATION</small><b>'+Math.floor(duration/60)+'m '+('0'+duration%60).slice(-2)+'s</b></div><div><small>COINS EARNED</small><b>+'+Math.max(0,Number(r.coins)||0)+'</b></div></div><button class="bz-tac-secondary" id="bzTacHistory">OPEN MATCH HISTORY</button>';
 $('bzTacHistory').onclick=()=>open('history');
}
function controlsPage(){
 const rows=[['lay','CONTROL LAYOUT'],['ctl','BUTTON POSITIONS'],['sns','CAMERA SENSITIVITY'],['sss','SCOPE SENSITIVITY'],['fdc','AUTO-FADE CONTROLS']];
 content.innerHTML='<div class="bz-tac-pagehead"><small>INPUT CONFIGURATION</small><h2>CONTROLS</h2><p>Open the existing touch-control and sensitivity settings.</p></div><div class="bz-tac-control-grid">'+rows.map(x=>'<button data-tac-control="'+x[0]+'"><b>'+x[1]+'</b><span>OPEN EXISTING SETTING ↗</span></button>').join('')+'</div><p class="bz-tac-note">Settings continue to use the game’s existing local preference handlers.</p>';
 content.querySelectorAll('[data-tac-control]').forEach(b=>b.onclick=()=>{close();const el=$(b.dataset.tacControl);if(el)el.click();else open('settings')});
}
'''
s=s.replace(old_nav,new_nav,1).replace(old_render,new_render,1).replace(old_open,new_open,1)
if s.count("function profilePage(){")!=1: raise SystemExit("profile insertion anchor not unique")
s=s.replace("function profilePage(){",pages+"\nfunction profilePage(){",1)
loop="function loop0(n){const dt=Math.min((n-last)/1000,.1);last=n;"
if s.count(loop)!=1: raise SystemExit("local game-loop anchor not unique: "+str(s.count(loop)))
s=s.replace(loop,"function loop0(n){window.BZGameState={started:!!started,health:Number(P.hp)||0,alive:!!P.alive,weapon:W[P.w]?.n||'Weapon'};const dt=Math.min((n-last)/1000,.1);last=n;",1)
scheduler="function loop(n){requestAnimationFrame(loop);try{loop0(n)}catch(e){showErr(e)}}"
if s.count(scheduler)!=1: raise SystemExit("game-loop scheduler anchor not unique: "+str(s.count(scheduler)))
s=s.replace(scheduler,"function loop(n){requestAnimationFrame(loop);if(window.BZ_TACTICAL_PAUSED)return;try{loop0(n)}catch(e){showErr(e)}}",1)
css=r'''/* BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1 */
#bzHub{background:radial-gradient(ellipse at 75% 8%,#26352b 0,transparent 36%),linear-gradient(135deg,#080d0b,#121b16 62%,#080d0b)!important;color:#edf3ed!important;font-family:Arial,Helvetica,sans-serif!important}
#bzHub .bhhead{background:#0b1110ed!important;border-bottom:1px solid #344239!important}
#bzHub .bhhead>div:first-child>b{font:900 23px Impact,Arial,sans-serif;letter-spacing:1.5px;color:#d0f27a}
#bzHub .bhhead .bhmuted{color:#92a196!important;font-size:9px;letter-spacing:1.5px}
#bzHub .bhclose{background:#17221c!important;border:1px solid #425246!important;color:#d0f27a!important}
#bzHub .bhnav{display:grid!important;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px!important;padding:12px 0;border-bottom:1px solid #344239}
#bzHub .bhnav button{min-width:0;background:#111a15!important;border:1px solid #2d3b32!important;border-radius:5px!important;color:#aab8ac!important;padding:10px 7px!important;font-size:10px!important;font-weight:800!important}
#bzHub .bhnav button.active{background:linear-gradient(90deg,#293824,#17221b)!important;border-color:#8ba85c!important;color:#d0f27a!important}
#bzHub #bhContent{max-width:1320px;margin:0 auto;padding:14px 0 26px}
#bzHub .bhcard{background:linear-gradient(145deg,#17211b,#101713)!important;border:1px solid #2d3b32!important;border-radius:6px!important;color:#edf3ed}
#bzHub .bhmuted{color:#91a096!important}
#bzHub .bz-tac-hero{position:relative;overflow:hidden;padding:22px;border:1px solid #394a3c;border-radius:6px;background:linear-gradient(90deg,#101a14,#17251b 65%,#27392a)}
#bzHub .bz-tac-hero>small,#bzHub .bz-tac-pagehead small,#bzHub .bz-tac-pause>small{font-size:9px;letter-spacing:2px;font-weight:900;color:#c6f36a}
#bzHub .bz-tac-hero h2,#bzHub .bz-tac-pagehead h2,#bzHub .bz-tac-pause h2{font:900 clamp(27px,4vw,42px)/1 Impact,Arial,sans-serif;letter-spacing:1.3px;margin:9px 0;color:#edf3ed}
#bzHub .bz-tac-hero p,#bzHub .bz-tac-pagehead p,#bzHub .bz-tac-pause p{color:#a8b6aa;font-size:11px;line-height:1.6}
#bzHub .bz-tac-mark{position:absolute;right:20px;top:10px;font:900 110px Impact,Arial,sans-serif;color:#d0f27a16}
#bzHub .bz-tac-primary,#bzHub .bz-tac-secondary{border-radius:3px!important;padding:11px 15px!important;font-size:10px!important;letter-spacing:1px!important}
#bzHub .bz-tac-primary{background:#c6f36a!important;color:#10170e!important;border:1px solid #d7ff8a!important}
#bzHub .bz-tac-secondary{background:#17221c!important;color:#dce6dc!important;border:1px solid #405047!important}
#bzHub .bz-tac-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:12px 0}
#bzHub .bz-tac-stats>div{background:#0e1512;border:1px solid #2d3b32;border-radius:4px;padding:13px;min-width:0}
#bzHub .bz-tac-stats small{display:block;color:#91a096;font-size:8px;letter-spacing:1px;font-weight:800}
#bzHub .bz-tac-stats b{display:block;color:#edf3ed;font:800 22px Impact,Arial,sans-serif;margin:5px 0;overflow-wrap:anywhere}
#bzHub .bz-tac-stats span{color:#c6f36a;font-size:9px}
#bzHub .bz-tac-section{display:flex;align-items:center;justify-content:space-between;gap:12px;background:linear-gradient(90deg,#18241c,#101713);border:1px solid #2d3b32;border-radius:5px;padding:14px;margin:12px 0}
#bzHub .bz-tac-section small{color:#c6f36a;font-size:8px;letter-spacing:1.4px;font-weight:900}
#bzHub .bz-tac-section h3{margin:5px 0;font:800 20px Impact,Arial,sans-serif}
#bzHub .bz-tac-section p{margin:0;color:#91a096;font-size:10px}
#bzHub .bz-tac-section button,#bzHub .bz-tac-grid button,#bzHub .bz-tac-order-grid button,#bzHub .bz-tac-control-grid button{background:#111a15!important;border:1px solid #344239!important;border-radius:5px!important;text-align:left;padding:13px!important}
#bzHub .bz-tac-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
#bzHub .bz-tac-grid button b,#bzHub .bz-tac-order-grid button b,#bzHub .bz-tac-control-grid button b{display:block;color:#d0f27a;font-size:10px;letter-spacing:.7px}
#bzHub .bz-tac-grid button span,#bzHub .bz-tac-order-grid button span,#bzHub .bz-tac-control-grid button span{display:block;color:#91a096;font-size:10px;margin-top:6px;line-height:1.4}
#bzHub .bz-tac-pagehead{margin:5px 0 16px}
#bzHub .bz-tac-actions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
#bzHub .bz-tac-note{padding:11px 13px;background:#111a15;border-left:3px solid #7e9954;color:#a8b6aa;font-size:10px;line-height:1.6}
#bzHub .bz-tac-order-grid,#bzHub .bz-tac-control-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
#bzHub .bz-tac-order-grid button.selected{border-color:#c6f36a!important;background:#1d2b1e!important}
#bzHub .bz-tac-order-grid button:disabled{opacity:.42;cursor:not-allowed}
#bzHub .bz-tac-pause{max-width:620px;margin:25px auto;padding:24px;border:1px solid #42523a;border-radius:6px;background:linear-gradient(145deg,#17211b,#101713);text-align:center}
#bzHub .bz-tac-empty{margin-top:12px;padding:18px;border:1px solid #2d3b32;background:#101713;border-radius:5px}
#bzHub .bz-tac-empty b{color:#d0f27a;font-size:11px;letter-spacing:1px}
#bzHub .bz-tac-empty p{color:#91a096;font-size:10px;line-height:1.6}
@media(max-width:700px){#bzHub .bhnav{display:flex!important;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}#bzHub .bhnav::-webkit-scrollbar{display:none}#bzHub .bhnav button{flex:0 0 auto;white-space:nowrap}#bzHub .bz-tac-stats{grid-template-columns:repeat(2,minmax(0,1fr))}#bzHub .bz-tac-hero{padding:15px}#bzHub .bz-tac-grid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){#bzHub .bz-tac-hero,#bzHub .bz-tac-grid button{animation:none!important;transition:none!important}}
'''
assets=html.parent
(assets/"css").mkdir(parents=True,exist_ok=True);(assets/"js").mkdir(parents=True,exist_ok=True)
(assets/"css"/"bz-tactical-command.css").write_text(css,encoding="utf-8")
js=r'''/* BATTLEZONE_V6_TACTICAL_COMMAND_UI_V1 */
(function(){
 'use strict';
 const hub=document.getElementById('bzHub');
 if(!hub||!window.BZPlayerHub)return;
 const b=document.createElement('b');b.id='bzTacEntry';b.textContent='COMMAND';b.setAttribute('role','button');b.tabIndex=0;
 b.addEventListener('click',()=>window.BZPlayerHub.open('command'));
 b.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();window.BZPlayerHub.open('command')}});
 const dock=document.getElementById('lb-nav');if(dock&&!document.getElementById('bzTacEntry'))dock.appendChild(b);
})();
'''
(assets/"js"/"bz-tactical-command.js").write_text(js,encoding="utf-8")
if s.count("</head>")!=1 or s.count("</body>")!=1: raise SystemExit("HTML anchors not unique")
s=s.replace("</head>",'<link rel="stylesheet" href="./css/bz-tactical-command.css">\n</head>',1)
s=s.replace("</body>",'<script src="./js/bz-tactical-command.js"></script>\n<!-- '+marker+' -->\n</body>',1)
html.write_text(s,encoding="utf-8")
print("TACTICAL_COMMAND_UI_APPLIED",html)
