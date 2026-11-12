from pathlib import Path
import re, shutil, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
html_candidates=list(root.rglob('app/src/main/assets/www/index.html'))
if len(html_candidates)!=1: raise SystemExit(f'Expected one Android game index.html, found {len(html_candidates)}')
html=html_candidates[0]; asset=html.parent
script_dir=Path(__file__).resolve().parent
css_src=script_dir/'warroom-command.css'; js_src=script_dir/'warroom-command.js'
if not css_src.is_file() or not js_src.is_file(): raise SystemExit('Required standalone War Room CSS/JS source files are missing beside the patcher.')
css_dir=asset/'css'; js_dir=asset/'js'; css_dir.mkdir(parents=True,exist_ok=True); js_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(css_src,css_dir/'warroom-command.css'); shutil.copy2(js_src,js_dir/'warroom-command.js')
s=html.read_text(encoding='utf-8')
marker='BATTLE_ZONE_WARROOM_VECTOR_V1'
if marker not in s:
    link='<link rel="stylesheet" href="./css/warroom-command.css">'
    if s.count('</head>')!=1: raise SystemExit('Expected exactly one HTML head close tag.')
    s=s.replace('</head>',link+'\n</head>',1)
    maps_code=r'''function mapsPage(){
 const maps=MAPS,selected=Math.max(0,Math.min(maps.length-1,Number(location.hash.slice(1)||0)));
 const hex=v=>'#'+(Number(v)||0).toString(16).padStart(6,'0').slice(-6);
 const terrain=m=>m.sea?'COASTAL':m.nt?'NIGHT OPERATIONS':m.fg?'HIGH ELEVATION':m.ruin?'RUINS / STORM':m.wx===4?'STORM FRONT':m.t>=60?'WOODLAND':'MIXED TERRAIN';
 const engagement=m=>m.sea?'LONG SIGHTLINES':m.b>=30?'DENSE COVER':m.t>=60?'CLOSE / MID RANGE':'OPEN ENGAGEMENTS';
 content.innerHTML=`<div class="bh-eyebrow"><span class="bh-live-dot"></span> BATTLEFIELD INTELLIGENCE / LOCAL MAP DATA</div><h2>Select deployment zone</h2><p class="bhmuted">Choose one of the installed offline environments. Map geometry, weather and vegetation are loaded by the local game engine.</p><div class="bhgrid">${maps.map((m,i)=>`<article class="bhcard war-map-card"><div class="war-map-visual" style="--wr-terrain:${hex(m.g)};--wr-sky:${hex(m.sky)}"><span>${String(i+1).padStart(2,'0')} / ${terrain(m)}</span></div><div class="bhrow"><b>${esc(m.n||('Map '+(i+1)))}</b><span class="bhpill">${i===selected?'ACTIVE':'AVAILABLE'}</span></div><p class="bhmuted">${esc(m.d||'Offline battlefield')}</p><div class="war-map-meta"><span class="bhpill">${terrain(m)}</span><span class="bhpill">${engagement(m)}</span><span class="bhpill">${Math.max(0,Number(m.b)||0)} structures</span><span class="bhpill">${Math.max(0,Number(m.t)||0)} canopy assets</span></div><button class="${i===selected?'':'primary'}" data-war-map="${i}">${i===selected?'CURRENT DEPLOYMENT':'SELECT BATTLEFIELD'}</button></article>`).join('')}</div><div class="bhcard"><b>Deployment integrity</b><p class="bhmuted">All map data and assets are packaged with the application. No online map download or network service is used.</p></div>`;
 content.querySelectorAll('[data-war-map]').forEach(b=>b.onclick=()=>{const i=Number(b.dataset.warMap);if(!Number.isInteger(i)||i<0||i>=maps.length)return;if(i===selected){close();return}const ld=$('ld');if(ld){$('ldtip').textContent='Preparing '+maps[i].n+' battlefield…';ld.classList.add('show','on')}location.hash=String(i);location.reload()});
}
// WARROOM_MAP_SELECT_V1
'''
    pattern=r'function mapsPage\(\)\{.*?\nfunction settingsPage\(\)'
    s,n=re.subn(pattern,maps_code+'\nfunction settingsPage()',s,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'Could not replace exactly one mapsPage function (matches={n}).')
    anchor='const al=[],bots=[],bm=new THREE.BoxGeometry(.7,1.2,.5),hm=new THREE.BoxGeometry(.4,.4,.4);'
    helper="const bzDoctrineMode=()=>{try{const d=localStorage.getItem('bzDoctrine');return ['aggressive','defensive','flanking'].includes(d)?d:'balanced'}catch(e){return 'balanced'}};\nconst bzDoctrineRole=i=>{const d=bzDoctrineMode();return d==='aggressive'?'rush':d==='defensive'?'cover':d==='flanking'?'flank':['cover','flank','rush','cover','flank'][i%5]};\n"+anchor
    if s.count(anchor)!=1: raise SystemExit(f'AI actor declaration expected once, found {s.count(anchor)}')
    s=s.replace(anchor,helper,1)
    role_old="role:['cover','flank','rush','cover','flank'][Math.floor(Math.random()*5)]"
    if s.count(role_old)!=1: raise SystemExit(f'AI spawn role anchor expected once, found {s.count(role_old)}')
    s=s.replace(role_old,'role:bzDoctrineRole(i)',1)
    roled_old="if(!roled&&bots.length){roled=1;bots.forEach(b=>{const r=Math.random(),u=b.userData;u.role=r<.2?'rush':r<.4?'camp':'';if(u.role=='rush')u.hp=85})}"
    roled_new="if(!roled&&bots.length){roled=1;bots.forEach((b,i)=>{const u=b.userData;u.role=bzDoctrineRole(i);if(bzDoctrineMode()==='aggressive')u.hp=85})}"
    if s.count(roled_old)!=1: raise SystemExit(f'AI role initialization anchor expected once, found {s.count(roled_old)}')
    s=s.replace(roled_old,roled_new,1)
    s+='\n<script src="./js/warroom-command.js"></script>\n'
    html.write_text(s,encoding='utf-8')
    s=html.read_text(encoding='utf-8')
    html.write_text(s.replace('<head>','<head>\n<!-- '+marker+' -->',1),encoding='utf-8')
else:
    print('War Room UI patch already present; refreshing standalone assets.')
vp=root/'validate_project.py'
if not vp.is_file():
    validators=list(root.rglob('validate_project.py'))
    if len(validators)!=1: raise SystemExit(f'Expected one extracted validate_project.py, found {len(validators)}')
    vp=validators[0]
v=vp.read_text(encoding='utf-8')
check_marker="    'war room vector UI files':"
if check_marker not in v:
    anchor="    'no fabricated replay playback': 'Replay playback is not available' in source,\n"
    checks=anchor+"    'war room vector UI files': all((ASSET_DIR / p).is_file() for p in ['css/warroom-command.css', 'js/warroom-command.js']),\n    'war room UI is integrated': 'BATTLE_ZONE_WARROOM_VECTOR_V1' in source and './css/warroom-command.css' in source and './js/warroom-command.js' in source,\n    'new battlefield command screen': 'WARROOM_MAP_SELECT_V1' in source and 'data-war-map' in source,\n    'offline tactical doctrine drives AI': 'bzDoctrineRole' in source and 'role:bzDoctrineRole(i)' in source and 'bzDoctrineMode()' in source,\n"
    if v.count(anchor)!=1: raise SystemExit('Validator insertion anchor missing or ambiguous.')
    v=v.replace(anchor,checks,1);vp.write_text(v,encoding='utf-8')
print('WAR_ROOM_VECTOR_PATCH_APPLIED')
print('HTML',html,'CSS',css_dir/'warroom-command.css','JS',js_dir/'warroom-command.js','VALIDATOR',vp)
