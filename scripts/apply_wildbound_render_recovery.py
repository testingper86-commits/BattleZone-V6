#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
def locate(rel):
 direct=root/rel
 if direct.is_file(): return direct
 xs=list(root.rglob(rel))
 if len(xs)!=1: raise SystemExit(f"{rel}: expected 1 file, got {len(xs)}")
 return xs[0]
rp=locate("app/src/main/assets/www/js/wildbound/rendering/runtime.js")
cp=locate("app/src/main/assets/www/css/wildbound.css")
r=rp.read_text();c=cp.read_text();marker="WILDBOUND_RENDER_RECOVERY_V1"
if marker in r:
 required=("webglcontextlost","webglcontextrestored","getRenderDiagnostics","fault","retryRenderer")
 missing=[x for x in required if x not in r]
 if missing: raise SystemExit("render marker incomplete: "+str(missing))
 print("RENDER_RECOVERY_ALREADY_APPLIED");raise SystemExit(0)
old="function resize(){if(!game.renderer)return;game.camera.aspect=innerWidth/innerHeight;game.camera.updateProjectionMatrix();if(W.state.screen==='game'){game.renderer.setSize(innerWidth,innerHeight,false)}else{const stage=document.querySelector('.hunter-stage');if(stage){game.camera.aspect=Math.max(1,stage.clientWidth)/Math.max(1,stage.clientHeight);game.camera.updateProjectionMatrix();game.renderer.setSize(Math.max(1,stage.clientWidth),Math.max(1,stage.clientHeight),false);game.renderer.render(game.scene,game.camera)}}}"
new="function resize(){if(!game.renderer||!game.camera)return;const host=W.state.screen==='game'?$('game'):document.querySelector('.hunter-stage');if(!host)return;const width=Math.max(1,Math.floor(host.clientWidth||innerWidth));const height=Math.max(1,Math.floor(host.clientHeight||innerHeight));game.camera.aspect=width/height;game.camera.updateProjectionMatrix();game.renderer.setSize(width,height,false);if(W.state.screen!=='game')game.renderer.render(game.scene,game.camera)}"
if r.count(old)!=1: raise SystemExit("resize anchor mismatch: "+str(r.count(old)))
r=r.replace(old,new,1)
old="function loop(now){if(W.state.paused||W.state.screen!=='game')return;let dt=Math.min(.04,(now-last)/1000||0);last=now;update(dt);game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(loop)}"
new="function loop(now){if(W.state.paused||W.state.screen!=='game'||renderRecovery.lost||renderRecovery.fault)return;try{let dt=Math.min(.04,(now-last)/1000||0);last=now;update(dt);if(!game.renderer||!game.renderer.getContext()||game.renderer.getContext().isContextLost())throw new Error('WebGL context unavailable during gameplay frame');game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(loop)}catch(error){renderRecovery.fail('WILDBOUND_RENDER_FRAME_ERROR',error)}}"
if r.count(old)!=1: raise SystemExit("game loop anchor mismatch: "+str(r.count(old)))
r=r.replace(old,new,1)
old="function lobbyLoop(now){if(W.state.screen!=='lobby'||!game.renderer)return;const dt=Math.min(.05,(now-(game.lobbyLast||now))/1000);game.lobbyLast=now;W.actors.updateHunter(game.player,dt,false,false);for(const m of game.monsters){const u=m.userData,gait=now*.0018+(u.seed||0);u.arms.forEach((arm,i)=>arm.rotation.x=Math.sin(gait+i*Math.PI)*.2);u.legs.forEach((leg,i)=>leg.rotation.x=Math.sin(gait+i*Math.PI)*.12);if(u.kind==='ranged')m.position.y=.18+Math.sin(gait*1.3)*.12;u.aura.rotation.y+=dt*.22}if(game.environment.update)game.environment.update(game.environment,dt,now*.001);game.environment.fire.intensity=1.6+Math.sin(now*.0018)*.22;game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(lobbyLoop)}"
new="function lobbyLoop(now){if(W.state.screen!=='lobby'||!game.renderer||renderRecovery.lost||renderRecovery.fault)return;try{const dt=Math.min(.05,(now-(game.lobbyLast||now))/1000);game.lobbyLast=now;W.actors.updateHunter(game.player,dt,false,false);for(const m of game.monsters){const u=m.userData,gait=now*.0018+(u.seed||0);u.arms.forEach((arm,i)=>arm.rotation.x=Math.sin(gait+i*Math.PI)*.2);u.legs.forEach((leg,i)=>leg.rotation.x=Math.sin(gait+i*Math.PI)*.12);if(u.kind==='ranged')m.position.y=.18+Math.sin(gait*1.3)*.12;u.aura.rotation.y+=dt*.22}if(game.environment.update)game.environment.update(game.environment,dt,now*.001);game.environment.fire.intensity=1.6+Math.sin(now*.0018)*.22;game.renderer.render(game.scene,game.camera);raf=requestAnimationFrame(lobbyLoop)}catch(error){renderRecovery.fail('WILDBOUND_LOBBY_RENDER_ERROR',error)}}"
if r.count(old)!=1: raise SystemExit("lobby loop anchor mismatch: "+str(r.count(old)))
r=r.replace(old,new,1)
# Resume must never start a render loop when the WebGL context is absent or a fault is unresolved.
old="function pause(v){if(W.state.screen!=='game')return;W.state.paused=v;$('pause-panel').classList.toggle('hidden',!v);if(v)cancelAnimationFrame(raf);else{last=performance.now();raf=requestAnimationFrame(loop)}}"
new="function pause(v){if(W.state.screen!=='game')return;if(!v&&(renderRecovery.lost||renderRecovery.fault)){W.state.paused=true;renderRecovery.fail('WILDBOUND_RESUME_BLOCKED',new Error('Graphics context has not recovered; restore graphics before resuming.'));return}W.state.paused=v;$('pause-panel').classList.toggle('hidden',!v);if(v)cancelAnimationFrame(raf);else{last=performance.now();raf=requestAnimationFrame(loop)}}"
if r.count(old)!=1: raise SystemExit('pause/resume anchor mismatch: '+str(r.count(old)))
r=r.replace(old,new,1)
# Centralized recovery is defined before start/resize; callbacks are safe once scene is initialized.
anchor="let last=0,raf=0;function makeScene()"
insert="""let last=0,raf=0;const renderRecovery={lost:false,fault:null,count:0,fail(label,error){cancelAnimationFrame(raf);this.fault=error;this.count++;console.error('[WILDBOUND] '+label,error);let panel=$('render-recovery');if(!panel){panel=document.createElement('section');panel.id='render-recovery';panel.className='render-recovery';panel.setAttribute('role','alert');const title=document.createElement('b');title.textContent='FIELD RENDERER INTERRUPTED';const detail=document.createElement('pre');detail.className='detail';const retry=document.createElement('button');retry.type='button';retry.textContent='RESTORE GRAPHICS';retry.addEventListener('click',()=>{try{if(!game.renderer||!game.renderer.getContext()||game.renderer.getContext().isContextLost())throw new Error('Graphics context is still unavailable.');game.renderer.resetState();resize();this.fault=null;this.count=0;panel.classList.remove('visible');last=performance.now();raf=requestAnimationFrame(W.state.screen==='game'&&!W.state.paused?loop:lobbyLoop)}catch(e){this.fail('WILDBOUND_RENDER_RETRY_ERROR',e)}});panel.append(title,detail,retry);$('game').appendChild(panel)}panel.querySelector('.detail').textContent=String(error&&error.stack||error).slice(0,1200);panel.classList.add('visible')},retry(){if(this.lost)throw new Error('WebGL context remains lost');if(!game.renderer||game.renderer.getContext().isContextLost())throw new Error('WebGL context unavailable');game.renderer.resetState();resize();this.fault=null;const panel=$('render-recovery');if(panel)panel.classList.remove('visible');last=performance.now();if(W.state.screen==='game'&&!W.state.paused)raf=requestAnimationFrame(loop);else if(W.state.screen==='lobby')raf=requestAnimationFrame(lobbyLoop);return this.diagnostics()},diagnostics(){return{lost:this.lost,fault:this.fault?String(this.fault.stack||this.fault):null,count:this.count,screen:W.state.screen,canvasWidth:$('view').width,canvasHeight:$('view').height,clientWidth:$('view').clientWidth,clientHeight:$('view').clientHeight}}};function makeScene()"""
if r.count(anchor)!=1: raise SystemExit("recovery object anchor mismatch: "+str(r.count(anchor)))
r=r.replace(anchor,insert,1)
# Handle WebGL restoration after canvas is allocated, and catch all resize sources.
anchor="window.addEventListener('resize',resize);W.bus.on('contract-complete',()=>{game.done=true});raf=requestAnimationFrame(lobbyLoop);"
if r.count(anchor)!=1: raise SystemExit("canvas event setup anchor mismatch: "+str(r.count(anchor)))
replacement="""window.addEventListener('resize',resize);const renderCanvas=$('view');renderCanvas.addEventListener('webglcontextlost',event=>{event.preventDefault();renderRecovery.lost=true;cancelAnimationFrame(raf);renderRecovery.fail('WILDBOUND_WEBGL_CONTEXT_LOST',new Error('Android WebView lost the WebGL graphics context'))},false);renderCanvas.addEventListener('webglcontextrestored',()=>{try{renderRecovery.lost=false;renderRecovery.fault=null;renderRecovery.count=0;resize();game.renderer.resetState();const p=$('render-recovery');if(p)p.classList.remove('visible');last=performance.now();raf=requestAnimationFrame(W.state.screen==='game'&&!W.state.paused?loop:lobbyLoop)}catch(error){renderRecovery.fail('WILDBOUND_WEBGL_RESTORE_ERROR',error)}},false);if(typeof ResizeObserver!=='undefined'){const ro=new ResizeObserver(()=>{try{resize()}catch(error){renderRecovery.fail('WILDBOUND_RESIZE_ERROR',error)}});ro.observe(document.querySelector('.hunter-stage'));ro.observe($('game'))}if(window.visualViewport)window.visualViewport.addEventListener('resize',()=>{try{resize()}catch(error){renderRecovery.fail('WILDBOUND_VIEWPORT_ERROR',error)}});"""
r=r.replace(anchor,replacement,1)
# Surface API for diagnostics to Android tests and support logs.
anchor="W.main={start,pause,toLobby,track,input:game.input,"
if r.count(anchor)!=1: raise SystemExit("public main API anchor mismatch")
r=r.replace(anchor,"W.main={start,pause,toLobby,track,input:game.input,getRenderDiagnostics:()=>renderRecovery.diagnostics(),retryRenderer:()=>renderRecovery.retry(),",1)
r='/* '+marker+' */\n'+r
c+='\n/* '+marker+' */\n.render-recovery{display:none;position:absolute;z-index:50;left:50%;top:50%;transform:translate(-50%,-50%);width:min(420px,calc(100vw - 32px));padding:16px;background:rgba(7,13,18,.98);border:1px solid #e66e69;box-shadow:0 14px 50px #000c;color:#e9f0ec;pointer-events:auto}.render-recovery.visible{display:block}.render-recovery b{display:block;color:#f0b2a9;font-size:11px;letter-spacing:.13em}.render-recovery pre{max-height:100px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;color:#a9b8b4;font:9px/1.4 monospace}.render-recovery button{width:100%}\n'
rp.write_text(r);cp.write_text(c);print('WILDBOUND_RENDER_RECOVERY_PATCHED')
