from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
html=root/'app/src/main/assets/www/index.html'
models=root/'app/src/main/assets/www/js/models.js'
s=html.read_text(encoding='utf-8')
m=models.read_text(encoding='utf-8')
marker='BATTLE_ZONE_GAMEPLAY_QUALITY_V2'
if marker in s:
    print('Gameplay quality patch already applied; source is unchanged.')
    raise SystemExit(0)
if 'BATTLE_ZONE_GAMEPLAY_OVERHAUL_V1' not in s:
    raise SystemExit('Expected validated V1 gameplay patch before quality V2; refusing to patch an unknown source.')
def once(text, old, new, label):
    n=text.count(old)
    if n!=1: raise SystemExit(f'{label}: expected exactly 1 source match, found {n}')
    return text.replace(old,new,1)
# Avoid allocating concatenated actor arrays in the game loop and AI target scan.
s=once(s,'const al=[],bots=[],bm=new THREE.BoxGeometry(.7,1.2,.5),hm=new THREE.BoxGeometry(.4,.4,.4);',
'''const al=[],bots=[],bm=new THREE.BoxGeometry(.7,1.2,.5),hm=new THREE.BoxGeometry(.4,.4,.4);
function forEachActor(fn){for(let i=0;i<bots.length;i++)fn(bots[i],i);for(let i=0;i<al.length;i++)fn(al[i],bots.length+i)}
const liveCount=()=>{let n=0;for(let i=0;i<bots.length;i++)if(bots[i].userData.alive)n++;return n};
const activeAllyCount=()=>{let n=0;for(let i=0;i<al.length;i++)if(!al[i].userData.down)n++;return n};''','actor iteration helpers')
if s.count('bots.concat(al).forEach(')!=3: raise SystemExit(f'actor concatenation count changed: {s.count("bots.concat(al).forEach(")}')
s=s.replace('bots.concat(al).forEach(','forEachActor(',3)
if s.count('live().length')!=5: raise SystemExit(f'live count anchor changed: {s.count("live().length")}')
s=s.replace('live().length','liveCount()')
s=once(s,"mm.fillStyle='#f55';live().forEach(b=>{const x=", "mm.fillStyle='#f55';bots.forEach(b=>{if(!b.userData.alive)return;const x=",'allocation-free minimap enemy iteration')
s=once(s,'al.filter(a=>!a.userData.down).length','activeAllyCount()','allocation-free ally count')
# Draw actual water and named POIs in the minimap, using the same world coordinate transform as actors.
s=once(s,"mm.strokeStyle='#4af';mm.lineWidth=2;mm.beginPath();mm.arc(cx+(zc.x-P.x)*s,",
'''mm.save();
 mm.fillStyle='rgba(48,145,210,.32)';mm.beginPath();mm.arc(cx+(lake.x-P.x)*s,cy+(lake.z-P.z)*s,Math.max(1,lake.r*s),0,Math.PI*2);mm.fill();
 mm.strokeStyle='#65c9f4';mm.lineWidth=1.5;mm.beginPath();mm.arc(cx+(lake.x-P.x)*s,cy+(lake.z-P.z)*s,Math.max(1,lake.r*s),0,Math.PI*2);mm.stroke();
 if(rv.w>0){const ry=cy+(rv.z-P.z)*s;mm.strokeStyle='rgba(58,165,224,.78)';mm.lineWidth=Math.max(2,rv.w*s);mm.beginPath();mm.moveTo(cx+(-438-P.x)*s,ry);mm.lineTo(cx+(438-P.x)*s,ry);mm.stroke();const bx=cx+(br.x-P.x)*s;mm.strokeStyle='#c8a66b';mm.lineWidth=3;mm.beginPath();mm.moveTo(bx,ry-4);mm.lineTo(bx,ry+4);mm.stroke()}
 const poiColors=['#ffc247','#6ab7ff','#ff7c52','#8ee08e','#ffffff'];
 MAP_POIS.forEach((p,i)=>{const x=cx+(p.x-P.x)*s,y=cy+(p.z-P.z)*s;if(x<-8||x>200||y<-8||y>200)return;mm.fillStyle=poiColors[i%poiColors.length];mm.beginPath();mm.arc(x,y,2.8,0,Math.PI*2);mm.fill();mm.font='bold 6px sans-serif';mm.fillText(p.name.split(' ').map(w=>w[0]).join(''),x+4,y-3)});
 mm.restore();
 mm.strokeStyle='#4af';mm.lineWidth=2;mm.beginPath();mm.arc(cx+(zc.x-P.x)*s,''','minimap terrain and landmark overlays')
# Throttle expensive HUD HTML reconstruction and canvas minimap rendering to ~8 Hz.
s=once(s,'function loop0(n){const dt=Math.min((n-last)/1000,.1);last=n;', 'let hudRefresh=0;\nfunction loop0(n){const dt=Math.min((n-last)/1000,.1);last=n;','HUD refresh clock')
s=once(s,'hudUpdate();', 'if((hudRefresh-=dt)<=0){hudRefresh=.12;hudUpdate();','throttled HUD refresh start')
s=once(s,"+'</span>';drawMM()}", "+'</span>';drawMM()}}",'throttled minimap refresh close')
# Character action state and procedural poses for jump/freefall, parachute, shooting and reload.
s=once(s,'const sc={jk:[],s:0,ph:0,gun,root:new THREE.Group(),q:{},charName:',"const sc={jk:[],s:0,ph:0,gun,action:'idle',actionT:0,airPose:false,parachutePose:false,root:new THREE.Group(),q:{},charName:",'character action state')
s=once(s,'const ph=c.ph,amp=kk*(.55+.35*run),idle=1-kk,br=Math.sin(t*1.8);',
'''const ph=c.ph,amp=kk*(.55+.35*run),idle=1-kk,br=Math.sin(t*1.8);
 if(c.actionT>0)c.actionT=Math.max(0,c.actionT-dt);else if(c.action!=='death')c.action='idle';
 const airW=c.airPose?1:0,chuteW=c.parachutePose?1:0,reloadW=c.action==='reload'?Math.max(0,Math.min(1,1-c.actionT/1.5)):0,fireW=c.action==='shoot'?Math.max(0,Math.min(1,c.actionT/.2)):0;''','animation action blend weights')
s=once(s,'if(c.gun){q.AR.rotation.x=-1.2;q.ER.rotation.x=-.25;q.AL.rotation.x=-1.15+Math.sin(c.ph)*.04;q.AL.rotation.z=.35;q.EL.rotation.x=-.3}',
'''if(c.gun){
  q.AR.rotation.x=-1.2+airW*.82+chuteW*.36+reloadW*.18-fireW*.18;
  q.ER.rotation.x=-.25+airW*.28+chuteW*.18+reloadW*.82-fireW*.16;
  q.AL.rotation.x=-1.15+Math.sin(c.ph)*.04+airW*1.05+chuteW*.82+reloadW*.48;
  q.AL.rotation.z=.35+airW*.42+chuteW*.36;
  q.EL.rotation.x=-.3+airW*.78+chuteW*.3-reloadW*.62;
  q.Ll.rotation.x+=airW*-.72+chuteW*-.12;q.Rl.rotation.x+=airW*-.72+chuteW*-.12;
  q.Lk.rotation.x+=airW*1.05+chuteW*.18;q.Rk.rotation.x+=airW*1.05+chuteW*.18;
  q.torso.rotation.x+=airW*.16+chuteW*.06-reloadW*.06-fireW*.14;
 }''','jump shoot reload and parachute poses')
s=once(s,'else if(P.y<=(P.gh||1.6)+.05)P.vy=6}', 'else if(P.y<=(P.gh||1.6)+.05){P.vy=6;if(pm)pm.airPose=true}}','jump action transition')
s=once(s,'function reload(){if(P.rl<=0&&P.mag<W[P.w].m&&W[P.w].m<999&&P.res>0){P.rl=1.5;snd(500,.05,.15,1);',
"function reload(){if(P.rl<=0&&P.mag<W[P.w].m&&W[P.w].m<999&&P.res>0){P.rl=1.5;if(pm){pm.action='reload';pm.actionT=1.5}snd(500,.05,.15,1);",'reload animation trigger')
s=once(s,'P.mag--;P.cd=W[P.w].r;gun.position.z=-.42;',"P.mag--;P.cd=W[P.w].r;if(pm){pm.action='shoot';pm.actionT=.2}gun.position.z=-.42;",'player firing recoil trigger')
s=once(s,'b.userData.alive=false;b.rotation.x=-Math.PI/2;',"b.userData.alive=false;if(b.sc){b.sc.action='death';b.sc.actionT=1}b.rotation.x=-Math.PI/2;",'bot death action state')
s=once(s,'if(clear&&bd<60)snd(0,.08,.15*(1-bd/60));if(clear&&Math.random()<[.3,.45,.62][DF]){',
"if(clear&&bd<60)snd(0,.08,.15*(1-bd/60));if(clear&&Math.random()<[.3,.45,.62][DF]){if(b.sc){b.sc.action='shoot';b.sc.actionT=.2}",'enemy firing animation trigger')
s=once(s,"if(en){a.rotation.y=Math.atan2(en.position.x-a.position.x,en.position.z-a.position.z);if(u.cd<=0){u.cd=rnd(.5,1);if(Math.random()<.72){en.userData.hp-=15;",
"if(en){a.rotation.y=Math.atan2(en.position.x-a.position.x,en.position.z-a.position.z);if(u.cd<=0){u.cd=rnd(.5,1);if(Math.random()<.72){if(a.sc){a.sc.action='shoot';a.sc.actionT=.2}en.userData.hp-=15;",'ally firing animation trigger')
s=once(s,'pm.hand.visible=!P.air;', 'pm.hand.visible=true;','keep weapon visible during jumps and freefall')
s=once(s,'pm.root.scale.set(.85,.85*(P.prone?.45:P.crouch?.8:1),.85);animSc(pm,',
'pm.root.scale.set(.85,.85*(P.prone?.45:P.crouch?.8:1),.85);pm.airPose=P.air===1||P.air===3||Math.abs(P.vy)>1.2;pm.parachutePose=P.air===3;animSc(pm,','player airborne pose state')
s=once(s,'animSc(sc,v<.4?0:v>2.5?1.75:1,dt,n/1000)',
' sc.airPose=!!g.userData.falling;sc.parachutePose=!!g.userData.chute;animSc(sc,v<.4?0:v>2.5?1.75:1,dt,n/1000)','AI airborne pose state')
# Avoid two linear indexOf scans for every bot during the transport flight.
s=once(s,'bots.forEach(b=>{const u=b.userData;if(u.airDrop){u.dropClock=', 'bots.forEach((b,botIndex)=>{const u=b.userData;if(u.airDrop){u.dropClock=','transport bot index cache')
s=once(s,'(bots.indexOf(b)%5)*2,PLANE.y-2,PLANE.z+(bots.indexOf(b)%2?1:-1)*4','(botIndex%5)*2,PLANE.y-2,PLANE.z+(botIndex%2?1:-1)*4','transport index reuse')
# Add a patch marker in the first inline block for CI idempotence.
s=once(s,'/* BATTLE_ZONE_GAMEPLAY_OVERHAUL_V1 */','/* BATTLE_ZONE_GAMEPLAY_OVERHAUL_V1 */\n/* '+marker+' */','quality patch marker')
html.write_text(s,encoding='utf-8')
# Remove per-frame bots.concat allocation in the separate rigged model loader.
old="const entries=[];                       // everything currently animated"
m=once(m,old,old+"\nconst eachActor=fn=>{if(typeof bots!=='undefined')for(let i=0;i<bots.length;i++)fn(bots[i],i);if(typeof al!=='undefined')for(let i=0;i<al.length;i++)fn(al[i],(typeof bots!=='undefined'?bots.length:0)+i)};",'model actor iterator')
m=once(m,"bots.concat(typeof al!=='undefined'?al:[]).forEach((g,i)=>",'eachActor((g,i)=>','model loader allocation removal')
m=once(m,"air:()=>typeof P!=='undefined'&&!P.air&&Math.abs(P.vy)>2.2", "air:()=>typeof P!=='undefined'&&(P.air===1||P.air===3||(!P.air&&Math.abs(P.vy)>2.2))",'rigged model jump and freefall clip')
models.write_text(m,encoding='utf-8')
(root/'GAMEPLAY_QUALITY_REPAIR_V2.md').write_text('''# Gameplay quality repair V2\n\n- Removed hot-loop `bots.concat(al)` allocations from AI target selection, actor animation and lighting updates.\n- Added allocation-free live-enemy and active-ally counters; reused bot indexes during transport drops.\n- Throttled expensive HUD reconstruction and minimap canvas redraw to approximately 8 Hz.\n- Added minimap overlays for the lake, river/bridge and five named POIs.\n- Added procedural jump/freefall/parachute, firing recoil and reload poses for procedural characters; enemy and ally firing triggers recoil poses.\n- Kept the held weapon visible during airborne player movement and extended the rigged model jump clip to skydiving/parachuting.\n\nStatic checks do not prove frame-rate gains or animation quality. Physical-device QA remains required.\n''',encoding='utf-8')
print('GAMEPLAY_QUALITY_V2_APPLIED')
