#!/usr/bin/env python3
"""Install the WILDBOUND playable vertical-slice presentation and combat feedback."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
base = root / "app/src/main/assets/www/js/wildbound"
actors = base / "actors/actors.js"
world = base / "world/world.js"
runtime = base / "rendering/runtime.js"
combat = base / "gameplay/combat.js"
for p in (actors, world, runtime, combat):
    if not p.is_file():
        raise SystemExit(f"Missing canonical WILDBOUND module: {p}")
marker = "WILDBOUND_PLAYABLE_VERTICAL_SLICE_V1"
if marker in runtime.read_text(encoding="utf-8"):
    print("WILDBOUND_PLAYABLE_VERTICAL_SLICE_ALREADY_APPLIED")
    raise SystemExit(0)
a = actors.read_text(encoding="utf-8")
old = "if(type==='king'){for(let i=0;i<6;i++){let spike=mesh(new T.ConeGeometry(.18,.9,5),accent,g,Math.cos(i*Math.PI/3)*1.0,2.9,Math.sin(i*Math.PI/3)*.65);spike.rotation.z=Math.cos(i*Math.PI/3)*.7;spike.rotation.x=Math.sin(i*Math.PI/3)*.5}}let aura=mesh(new T.SphereGeometry(defs.r*1.5,12,8),accent,g,0,defs.h*.55,0);"
new = "if(type==='king'){for(let i=0;i<6;i++){let spike=mesh(new T.ConeGeometry(.18,.9,5),accent,g,Math.cos(i*Math.PI/3)*1.0,2.9,Math.sin(i*Math.PI/3)*.65);spike.rotation.z=Math.cos(i*Math.PI/3)*.7;spike.rotation.x=Math.sin(i*Math.PI/3)*.5}}const chest=mesh(new T.OctahedronGeometry(defs.r*.38,1),accent,g,0,defs.h*.56,defs.r*.49);chest.scale.set(1.12,1.28,.48);for(const side of [-1,1]){const pa=mesh(new T.SphereGeometry(defs.r*.25,9,7),dark,g,side*defs.r*.72,defs.h*.68,0);pa.scale.set(1.3,.78,1.08);const claw=mesh(new T.ConeGeometry(defs.r*.12,defs.r*.48,5),accent,g,side*defs.r*.82,defs.h*.34,defs.r*.28);claw.rotation.x=Math.PI/2;claw.rotation.z=side*.25;const rune=mesh(new T.BoxGeometry(.055,defs.h*.22,.035),eye,g,side*defs.r*.45,defs.h*.58,defs.r*.72);rune.material.emissive.setHex(type==='ironmaw'?0x3d2410:0x142f3d);rune.material.emissiveIntensity=.8}for(let i=0;i<4;i++){const ridge=mesh(new T.ConeGeometry(defs.r*.12,defs.r*.48,5),dark,g,0,defs.h*.62+i*.17,-defs.r*.48);ridge.rotation.x=-Math.PI/2}let aura=mesh(new T.SphereGeometry(defs.r*1.5,12,8),accent,g,0,defs.h*.55,0);"
if a.count(old) != 1:
    raise SystemExit(f"monster detail insertion anchor count: {a.count(old)}")
a = a.replace(old, new, 1)
w = world.read_text(encoding="utf-8")
old = "rocks.count=ri;rocks.instanceMatrix.needsUpdate=true;scene.add(rocks);const pillars=new t.InstancedMesh"
new = "rocks.count=ri;rocks.instanceMatrix.needsUpdate=true;scene.add(rocks);const fernCount=180,fernMat=new t.MeshStandardMaterial({color:0x496f50,roughness:1}),fernLight=new t.MeshStandardMaterial({color:0x78956a,roughness:1}),ferns=new t.InstancedMesh(new t.ConeGeometry(.18,1.05,5),fernMat,fernCount),fernTips=new t.InstancedMesh(new t.ConeGeometry(.11,.72,5),fernLight,fernCount);for(let i=0;i<fernCount;i++){let x=(rng()-.5)*118,z=(rng()-.5)*118;if(Math.hypot(x,z)<10){x+=x<0?-13:13;z+=z<0?-13:13}let h=.65+rng()*.8;dummy.position.set(x,h*.48,z);dummy.scale.set(.65+rng()*.7,h,.65+rng()*.7);dummy.rotation.set((rng()-.5)*.25,rng()*Math.PI*2,(rng()-.5)*.35);dummy.updateMatrix();ferns.setMatrixAt(i,dummy.matrix);dummy.position.y=h*.78;dummy.scale.set(.5,h*.72,.5);dummy.updateMatrix();fernTips.setMatrixAt(i,dummy.matrix)}ferns.instanceMatrix.needsUpdate=true;fernTips.instanceMatrix.needsUpdate=true;scene.add(ferns,fernTips);const logCount=16,logs=new t.InstancedMesh(new t.CylinderGeometry(.17,.23,3.2,7),trunkMat,logCount);for(let i=0;i<logCount;i++){let x=(rng()-.5)*120,z=(rng()-.5)*120;if(Math.hypot(x,z)<13)x+=x<0?-16:16;dummy.position.set(x,.2,z);dummy.scale.set(.8+rng()*.6,.8+rng()*.5,.8+rng()*.6);dummy.rotation.set((rng()-.5)*.16,0,Math.PI/2+(rng()-.5)*.14);dummy.updateMatrix();logs.setMatrixAt(i,dummy.matrix)}logs.instanceMatrix.needsUpdate=true;scene.add(logs);const fireflyCount=72,fireflyPositions=new Float32Array(fireflyCount*3),fireflyBase=new Float32Array(fireflyCount*3);for(let i=0;i<fireflyCount;i++){fireflyBase[i*3]=(rng()-.5)*34;fireflyBase[i*3+1]=.6+rng()*4.5;fireflyBase[i*3+2]=(rng()-.5)*34;fireflyPositions.set(fireflyBase.subarray(i*3,i*3+3),i*3)}const fireflyGeometry=new t.BufferGeometry();fireflyGeometry.setAttribute('position',new t.BufferAttribute(fireflyPositions,3));const fireflies=new t.Points(fireflyGeometry,new t.PointsMaterial({color:0x9debd2,size:.12,transparent:true,opacity:.78,blending:t.AdditiveBlending,depthWrite:false,sizeAttenuation:true}));scene.add(fireflies);const pillars=new t.InstancedMesh"
if w.count(old) != 1:
    raise SystemExit(f"world detail insertion anchor count: {w.count(old)}")
w = w.replace(old, new, 1)
old = "return{fire,ground,hazards,drawBatches:14,setQuality(q){const f=q==='low'?.5:q==='medium'?.72:q==='high'?.88:1;trunk.count=Math.floor(ti*f);crowns.count=Math.floor(ci*f);rocks.count=Math.floor(ri*f)}}},update(w,dt,t){w.fire.intensity=1.6+Math.sin(t*1.8)*.25}"
new = "return{fire,ground,hazards,fireflies,fireflyPositions,fireflyBase,drawBatches:19,setQuality(q){const f=q==='low'?.5:q==='medium'?.72:q==='high'?.88:1;trunk.count=Math.floor(ti*f);crowns.count=Math.floor(ci*f);rocks.count=Math.floor(ri*f);ferns.count=Math.floor(fernCount*f);fernTips.count=Math.floor(fernCount*f);logs.count=Math.floor(logCount*f);fireflies.visible=q!=='low'}}},update(w,dt,t){w.fire.intensity=1.6+Math.sin(t*1.8)*.25;const a=w.fireflyPositions,base=w.fireflyBase;for(let i=0;i<a.length;i+=3){const phase=t*.8+i*.17;a[i]=base[i]+Math.sin(phase)*.65;a[i+1]=base[i+1]+Math.sin(phase*1.7)*.35;a[i+2]=base[i+2]+Math.cos(phase*.8)*.65}w.fireflies.geometry.attributes.position.needsUpdate=true}"
if w.count(old) != 1:
    raise SystemExit(f"world update anchor count: {w.count(old)}")
w = w.replace(old, new, 1)
r = runtime.read_text(encoding="utf-8")
old = "game.releaseProjectile=q=>{game.scene.remove(q.mesh);q.mesh.visible=false;game.projectilePool.push(q.mesh)};let hemi=new t.HemisphereLight"
new = "game.releaseProjectile=q=>{game.scene.remove(q.mesh);q.mesh.visible=false;game.projectilePool.push(q.mesh)};game.effects=[];game.spawnImpact=(position,weak=false)=>{const mesh=new t.Mesh(new t.TorusGeometry(weak?1:.72,.055,6,24),new t.MeshBasicMaterial({color:weak?0xffd27a:0x77d9c2,transparent:true,opacity:.92,depthWrite:false}));mesh.position.copy(position);mesh.position.y+=1.15;mesh.rotation.x=Math.PI/2;game.scene.add(mesh);game.effects.push({mesh,life:.34,max:.34})};let hemi=new t.HemisphereLight"
if r.count(old) != 1:
    raise SystemExit(f"impact factory anchor count: {r.count(old)}")
r = r.replace(old, new, 1)
old = "game.environment.fire.intensity=1.6+Math.sin(now*.0018)*.22;game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(lobbyLoop)"
new = "if(game.environment.update)game.environment.update(game.environment,dt,now*.001);game.environment.fire.intensity=1.6+Math.sin(now*.0018)*.22;game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(lobbyLoop)"
if r.count(old) != 1:
    raise SystemExit(f"lobby environment update anchor count: {r.count(old)}")
r = r.replace(old, new, 1)
old = "for(let i=game.projectiles.length-1;i>=0;i--){let q=game.projectiles[i],v=new T.Vector3().subVectors(p.position,q.mesh.position);"
new = "for(let i=game.effects.length-1;i>=0;i--){const e=game.effects[i];e.life-=dt;e.mesh.scale.setScalar(1+(1-e.life/e.max)*1.8);e.mesh.material.opacity=Math.max(0,e.life/e.max);if(e.life<=0){game.scene.remove(e.mesh);e.mesh.geometry.dispose();e.mesh.material.dispose();game.effects.splice(i,1)}}if(game.environment.update)game.environment.update(game.environment,dt,game.elapsed);for(let i=game.projectiles.length-1;i>=0;i--){let q=game.projectiles[i],v=new T.Vector3().subVectors(p.position,q.mesh.position);"
if r.count(old) != 1:
    raise SystemExit(f"gameplay update anchor count: {r.count(old)}")
r = r.replace(old, new, 1)
r = "/* " + marker + " */\n" + r
c = combat.read_text(encoding="utf-8")
old = "if(hit){const u=hit.userData,weak=u.weakUntil>performance.now(),armor=u.kind==='brute'&&!heavy?.6:1,amount=damage*(weak?2.2:1)*armor;u.hp-=amount;"
new = "if(hit){const u=hit.userData,weak=u.weakUntil>performance.now(),armor=u.kind==='brute'&&!heavy?.6:1,amount=damage*(weak?2.2:1)*armor;if(game.spawnImpact)game.spawnImpact(hit.position,weak);u.hp-=amount;"
if c.count(old) != 1:
    raise SystemExit(f"combat impact anchor count: {c.count(old)}")
c = c.replace(old, new, 1)
actors.write_text(a, encoding="utf-8")
world.write_text(w, encoding="utf-8")
runtime.write_text(r, encoding="utf-8")
combat.write_text(c, encoding="utf-8")
print("WILDBOUND_PLAYABLE_VERTICAL_SLICE_APPLIED", root)
