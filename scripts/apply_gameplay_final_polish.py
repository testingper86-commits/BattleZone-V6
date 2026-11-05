from pathlib import Path
import re, shutil, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
htmls=list(root.rglob('app/src/main/assets/www/index.html'))
if len(htmls)!=1: raise SystemExit(f'Expected one Android game HTML, found {len(htmls)}')
html=htmls[0]; asset=html.parent
css=Path(__file__).resolve().parent/'final-polish.css'
if not css.is_file(): raise SystemExit(f'Missing required CSS: {css}')
(asset/'css').mkdir(parents=True,exist_ok=True); shutil.copy2(css,asset/'css/final-polish.css')
s=html.read_text(encoding='utf-8'); marker='BATTLE_ZONE_FINAL_POLISH_V1'
def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected one source anchor, found {n}')
    s=s.replace(old,new,1)
if marker not in s:
    rep('<head>','<head><!-- '+marker+' -->','marker')
    rep("const gr=new THREE.Mesh(new THREE.PlaneGeometry(900,900),BZMaterial('grass',18,.98));gr.rotation.x=-Math.PI/2;gr.receiveShadow=!LQ;S.add(gr);", "const gr=new THREE.Mesh(new THREE.BufferGeometry(),BZMaterial('grass',18,.98));gr.receiveShadow=!LQ;S.add(gr);", 'flat ground')
    old="for(let i=0;i<8;i++){const rr=rnd(14,24),m=new THREE.Mesh(new THREE.SphereGeometry(rr,12,8),M(new THREE.Color(MAP.g).multiplyScalar(.85)));m.scale.y=.22;m.position.set(r2(),0,r2());S.add(m);hills.push({x:m.position.x,z:m.position.z,r:rr})}"
    new="for(let i=0;i<8;i++){const rr=rnd(14,24);hills.push({x:r2(),z:r2(),r:rr})}const bzTerrainHeight=(x,z)=>{let y=0;for(const h of hills){const d=Math.hypot(x-h.x,z-h.z);if(d<h.r){const v=.22*h.r*Math.sqrt(1-d*d/(h.r*h.r));if(v>y)y=v}}return y*.38};{const seg=LQ?72:104,side=900,positions=[],colors=[],indices=[],low=new THREE.Color(MAP.g),high=new THREE.Color(MAP.tc),snow=new THREE.Color(0xe8f1f7);for(let iz=0;iz<=seg;iz++){const z=-side/2+side*iz/seg;for(let ix=0;ix<=seg;ix++){const x=-side/2+side*ix/seg,y=bzTerrainHeight(x,z),noise=(Math.sin(x*.037+z*.021)+Math.cos(z*.043-x*.017))*.035;positions.push(x,y,z);const h=Math.min(1,y/2.1),c=low.clone().lerp(high,Math.max(0,Math.min(.72,h*.62+noise+.08)));if(MAP.nt)c.lerp(snow,Math.max(0,Math.min(.7,h*.55)));c.multiplyScalar(1+noise);colors.push(c.r,c.g,c.b)}}for(let iz=0;iz<seg;iz++)for(let ix=0;ix<seg;ix++){const a=iz*(seg+1)+ix,b=a+1,c=a+seg+1,d=c+1;indices.push(a,c,b,b,c,d)}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geo.setIndex(indices);geo.computeVertexNormals();gr.geometry=geo;gr.rotation.set(0,0,0);gr.material.vertexColors=true;gr.material.color.set(0xffffff);gr.material.roughness=.98;gr.material.needsUpdate=true;gr.frustumCulled=false}"
    rep(old,new,'visible terrain heightfield')
    rep("function gT(x,z){let y=0;for(const h of hills){const d=Math.hypot(x-h.x,z-h.z);if(d<h.r){const v=.22*h.r*Math.sqrt(1-d*d/(h.r*h.r));if(v>y)y=v}}return y}", 'function gT(x,z){return bzTerrainHeight(x,z)}', 'terrain collision')
    rep("function chute(){if(P.air==1){P.air=3;msg('Parachute open')}}", "function chute(){if(P.air===1){P.air=3;P.dropVx=(P.dropVx||0)*.45;P.dropVz=(P.dropVz||0)*.45;msg('PARACHUTE DEPLOYED • Controlled descent')}}", 'manual parachute')
    rep("if(P.air==1&&P.y<(window.AUTO||45)){P.air=3;msg('Parachute auto-opened')}", "if(P.air===1&&P.y<(window.AUTO||45)){chute();msg('AUTO PARACHUTE • SAFE DESCENT')}", 'automatic parachute')
    rep("window.addEventListener('load',()=>setTimeout(showStartupBoot,180));", 'void 0;', 'startup boot')
    pattern='<script>'+chr(92)+'s*// Random cinematic boot splash for first launch.*?</script>'+chr(92)+'s*'
    s,n=re.subn(pattern,'',s,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'Duplicate startup boot script count: {n}')
    rep('pm.hand.visible=true;if(sh){','pm.hand.visible=!P.air&&!P.veh;if(sh){','airborne weapon')
    rep('R.setPixelRatio(LQ?1:Math.min(devicePixelRatio,1.25));','R.setPixelRatio(LQ?.9:Math.min(devicePixelRatio,1.05));','mobile render budget')
    oldaim="$('c').addEventListener('pointermove',e=>{if(e.pointerId==lid){const k=(e.pointerType==='mouse'?.004:.006)*(window.SENS||1)*(P.sc?(window.SSENS||1):1);P.yaw-=(e.clientX-lx)*k;P.pitch=Math.max(-1.3,Math.min(1.3,P.pitch-(e.clientY-ly)*k));lx=e.clientX;ly=e.clientY}});"
    newaim="$('c').addEventListener('pointermove',e=>{if(e.pointerId==lid){const samples=e.getCoalescedEvents?e.getCoalescedEvents():null,p=samples&&samples.length?samples[samples.length-1]:e,k=(e.pointerType==='mouse'?.004:.006)*(window.SENS||1)*(P.sc?(window.SSENS||1):1);P.yaw-=(p.clientX-lx)*k;P.pitch=Math.max(-1.3,Math.min(1.3,P.pitch-(p.clientY-ly)*k));lx=p.clientX;ly=p.clientY}});"
    rep(oldaim,newaim,'coalesced aim input')
    oldcanopy="const chuteM=new THREE.Mesh(new THREE.SphereGeometry(2.4,14,6,0,Math.PI*2,0,Math.PI/2),new THREE.MeshLambertMaterial({color:0xff7a1a,side:THREE.DoubleSide}));chuteM.scale.y=.6;chuteM.visible=false;S.add(chuteM);"
    newcanopy="const chuteM=new THREE.Group();{const canopy=new THREE.Mesh(new THREE.SphereGeometry(3.8,18,8,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:0xe84b36,roughness:.72,side:THREE.DoubleSide}));canopy.scale.y=.72;canopy.position.y=.15;chuteM.add(canopy);const trim=new THREE.Mesh(new THREE.TorusGeometry(3.55,.07,5,32,Math.PI),new THREE.MeshStandardMaterial({color:0xf5d8b0,roughness:.55}));trim.rotation.x=Math.PI/2;trim.position.y=.2;chuteM.add(trim);const cordMat=new THREE.LineBasicMaterial({color:0xe8e0d0,transparent:true,opacity:.9});for(let i=0;i<8;i++){const a=i*Math.PI/7,pts=[new THREE.Vector3(Math.cos(a)*3.3,.05,Math.sin(a)*3.3),new THREE.Vector3(Math.cos(a)*.38,-2.8,Math.sin(a)*.38)];chuteM.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),cordMat))}}chuteM.visible=false;S.add(chuteM);"
    rep(oldcanopy,newcanopy,'parachute canopy')
    lines=s.splitlines()
    start=next((i for i,x in enumerate(lines) if x.lstrip().startswith('al.forEach(a=>{const u=a.userData;') and 'let en=null' in x),None)
    end=next((i for i,x in enumerate(lines) if start is not None and i>start and x.lstrip().startswith('if(P.down){P.dt-=')),None)
    if start is None or end is None: raise SystemExit('Squad update block anchors not found')
    ally=[
"  al.forEach(a=>{const u=a.userData;if(u.down||u.alive===false)return;u.cd=(u.cd||0)-dt;",
"   let en=null,bd=78;bots.forEach(o=>{const v=o.userData;if(!v.alive||v.ally)return;const d=Math.hypot(o.position.x-a.position.x,o.position.z-a.position.z);if(d<bd){bd=d;en=o}});",
"   let gx=P.x+Math.cos(u.off*2)*4,gz=P.z+Math.sin(u.off*2)*4;if(P.air){a.position.set(gx,0,gz);return}if(P.down){gx=P.x;gz=P.z}",
"   if(en){const dx0=en.position.x-a.position.x,dz0=en.position.z-a.position.z;a.rotation.y=Math.atan2(dx0,dz0);const clear=bd<78&&hasClearShot(a.position.x,a.position.y+1.15,a.position.z,en.position.x,en.position.y+1.1,en.position.z);if(clear&&u.cd<=0){u.cd=.32+rnd(0,.22);if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}en.userData.hp-=18+rnd(0,7);if(en.userData.hp<=0)killBot(en,false)}else if(!clear&&u.cd<=0)u.cd=.18;if(bd>18){const ang=Math.atan2(dz0,dx0);gx=en.position.x-Math.cos(ang)*12;gz=en.position.z-Math.sin(ang)*12}}",
"   const dx=gx-a.position.x,dz=gz-a.position.z,dl=Math.hypot(dx,dz);if(dl>(P.down?2:5)){const[x,z]=hit(a.position.x+dx/dl*5.8*dt,a.position.z+dz/dl*5.8*dt,.4);[a.position.x,a.position.z]=clampWorld(x,z,1);a.position.y=gT(a.position.x,a.position.z);if(!en)a.rotation.y=Math.atan2(dx,dz)}",
"   const follow=Math.hypot(P.x-a.position.x,P.z-a.position.z);if(!P.down&&P.hp<70&&follow<7){u.healT=(u.healT||0)+dt;if(u.healT>=2.5){P.hp=Math.min(100,P.hp+12);u.healT=0;msg('TEAM MEDIC • +12 HEALTH')}}else u.healT=0;if(P.down&&follow<4){P.rvt=(P.rvt||0)+dt;if(P.rvt>=3){P.down=0;P.hp=40;P.rvt=0;msg('SQUAD REVIVE COMPLETE')}}",
"  });"]
    s=chr(10).join(lines[:start]+ally+lines[end:])+chr(10)
    oldboom="function boom(x,z,R,d,q){if(!q){snd(0,.7,.5);ENV.boom(x,z,R,d)}bots.forEach(b=>{const k=Math.hypot(b.position.x-x,b.position.z-z);if(b.userData.alive&&k<R){b.userData.hp-=d*(1-k/R*.6);if(b.userData.hp<=0)killBot(b,true)}});const k=Math.hypot(P.x-x,P.z-z);if(k<R)dmg(d*(1-k/R*.6)*.5)}"
    newboom="function boom(x,z,R,d,q){if(!q){snd(0,.7,.5);ENV.boom(x,z,R,d)}bots.forEach(b=>{const k=Math.hypot(b.position.x-x,b.position.z-z);if(b.userData.alive&&k<R){b.userData.hp-=d*(1-k/R*.6);if(b.userData.hp<=0)killBot(b,true)}});const k=Math.hypot(P.x-x,P.z-z);if(k<R)dmg(d*(1-k/R*.6)*.5)}"
    rep(oldboom,newboom,'squad blast damage')
    rep('</head>','<link rel="stylesheet" href="./css/final-polish.css">'+chr(10)+'</head>','responsive lobby CSS')
    html.write_text(s,encoding='utf-8')
validators=list(root.rglob('validate_project.py'))
if len(validators)!=1: raise SystemExit(f'Expected one project validator, found {len(validators)}')
v=validators[0].read_text(encoding='utf-8')
v=v.replace("'expanded 900x900 map ground': 'PlaneGeometry(900,900)' in source,", "'expanded 900x900 terrain heightfield': 'bzTerrainHeight' in source and 'side=900' in source and 'gr.geometry=geo' in source,")
v=v.replace("'weapon retained during airborne movement': 'pm.hand.visible=true' in source,", "'airborne weapon hidden until landing': 'pm.hand.visible=!P.air&&!P.veh' in source,")
validators[0].write_text(v,encoding='utf-8')
print('GAMEPLAY_FINAL_POLISH_APPLIED',html)
