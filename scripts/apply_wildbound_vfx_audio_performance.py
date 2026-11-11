#!/usr/bin/env python3
"""Install bounded pooled combat VFX and lifecycle-safe procedural audio."""
from pathlib import Path
import subprocess, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
www = root / "app/src/main/assets/www"
runtime = www / "js/wildbound/rendering/runtime.js"
combat = www / "js/wildbound/gameplay/combat.js"
audio = www / "js/wildbound/audio/audio.js"
for path in (runtime, combat, audio):
    if not path.is_file():
        raise SystemExit(f"Missing WILDBOUND runtime dependency: {path}")

r = runtime.read_text(encoding="utf-8")
c = combat.read_text(encoding="utf-8")
a = audio.read_text(encoding="utf-8")
marker = "WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1"
if marker in r and marker in a and "WILDBOUND_DODGE_VFX_EVENT_V1" in c:
    print("WILDBOUND_VFX_AUDIO_PERFORMANCE_ALREADY_APPLIED")
    raise SystemExit(0)

anchor = "W.ui.init(game);"
if r.count(anchor) != 1:
    raise SystemExit(f"runtime VFX initialization anchor count: {r.count(anchor)}")
vfx = r"""
/* WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1 */
game.effects=(()=>{const three=T(),count=72,positions=new Float32Array(count*3),colors=new Float32Array(count*3),baseColors=new Float32Array(count*3),velocity=new Float32Array(count*3),life=new Float32Array(count),maxLife=new Float32Array(count),geometry=new three.BufferGeometry(),attribute=new three.BufferAttribute(positions,3);attribute.setUsage(three.DynamicDrawUsage);geometry.setAttribute('position',attribute);geometry.setAttribute('color',new three.BufferAttribute(colors,3));geometry.setDrawRange(0,count);const material=new three.PointsMaterial({size:.12,vertexColors:true,transparent:true,opacity:.9,depthWrite:false,sizeAttenuation:true});const points=new three.Points(geometry,material);points.frustumCulled=false;game.scene.add(points);let cursor=0;function burst(position,color,amount=10,power=3){if(!position)return;const x=Number(position.x)||0,y=Number(position.y)||0,z=Number(position.z)||0,cr=((color>>16)&255)/255,cg=((color>>8)&255)/255,cb=(color&255)/255;for(let n=0;n<amount;n++){const i=cursor++%count,j=i*3,angle=Math.random()*Math.PI*2,speed=power*(.35+Math.random()*.65),vertical=(Math.random()-.35)*power*.8;positions[j]=x;positions[j+1]=y+.65;positions[j+2]=z;velocity[j]=Math.cos(angle)*speed;velocity[j+1]=vertical;velocity[j+2]=Math.sin(angle)*speed;life[i]=maxLife[i]=.28+Math.random()*.48;const shade=.55+Math.random()*.45;baseColors[j]=cr*shade;baseColors[j+1]=cg*shade;baseColors[j+2]=cb*shade;}}function update(dt){let active=0;for(let i=0;i<count;i++){if(life[i]<=0)continue;life[i]=Math.max(0,life[i]-dt);const j=i*3;if(life[i]<=0){positions[j+1]=-1000;continue}const f=life[i]/maxLife[i];positions[j]+=velocity[j]*dt;positions[j+1]+=velocity[j+1]*dt;positions[j+2]+=velocity[j+2]*dt;velocity[j+1]-=5.5*dt;colors[j]=baseColors[j]*f;colors[j+1]=baseColors[j+1]*f;colors[j+2]=baseColors[j+2]*f;active++}attribute.needsUpdate=true;geometry.attributes.color.needsUpdate=true;points.visible=active>0;return active}return{burst,update,dispose(){game.scene.remove(points);geometry.dispose();material.dispose()}}})();W.bus.on('hit',e=>{if(e&&e.monster)game.effects.burst(e.monster.position,e.weak?0x9eeeff:0x78d9c4,e.weak?18:9,e.weak?4.6:2.8)});W.bus.on('kill',type=>{const target=game.monsters.find(m=>m.userData.type===type);if(target)game.effects.burst(target.position,0xd9c18a,26,5.2)});W.bus.on('monster-strike',e=>{if(e&&e.monster)game.effects.burst(game.player.position,0xff916d,8,2.1)});W.bus.on('boss-phase',()=>game.effects.burst(game.monsters[3].position,0xb58cff,36,6));W.bus.on('hunter-dodge',p=>game.effects.burst(p,0x83e5d0,16,4.2));
"""
r = r.replace(anchor, vfx + anchor, 1)
update_start = r.find("function update(dt)")
if update_start < 0:
    raise SystemExit("runtime effects update function not found")
update_end = r.find("function loop(", update_start)
if update_end < 0:
    raise SystemExit("runtime effects frame-loop boundary not found")
update_body = r[update_start:update_end]
anchor = "game.elapsed+=dt;"
if update_body.count(anchor) != 1:
    raise SystemExit(f"runtime elapsed update anchor count: {update_body.count(anchor)}")
replacement = anchor + "if(game.effects)game.effects.update(dt);"
update_body = update_body.replace(anchor, replacement, 1)
r = r[:update_start] + update_body + r[update_end:]

anchor = "W.audio.dodge();W.bus.emit('save')"
if c.count(anchor) != 1:
    raise SystemExit(f"dodge event anchor count: {c.count(anchor)}")
c = c.replace(anchor, "W.audio.dodge();W.bus.emit('hunter-dodge',p.position);/* WILDBOUND_DODGE_VFX_EVENT_V1 */W.bus.emit('save')", 1)

if "WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1" not in a:
    old = "(()=>{'use strict';const W=window.WILDBOUND;let ctx=null;function tone(f,d,type='sine',gain=.045){if(!W.state.settings.sfx)return;try{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();if(ctx.state==='suspended')ctx.resume();const o=ctx.createOscillator(),g=ctx.createGain();o.type=type;o.frequency.setValueAtTime(f,ctx.currentTime);o.frequency.exponentialRampToValueAtTime(Math.max(35,f*.45),ctx.currentTime+d);g.gain.setValueAtTime(gain,ctx.currentTime);g.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+d);o.connect(g);g.connect(ctx.destination);o.start();o.stop(ctx.currentTime+d)}catch(e){}}"
    new = """(()=>{'use strict';const W=window.WILDBOUND;let ctx=null,voices=0;function resume(){try{if(ctx&&ctx.state==='suspended')ctx.resume().catch(()=>{})}catch(e){}}function tone(f,d,type='sine',gain=.045){if(!W.state.settings.sfx||voices>=12)return;try{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();resume();const o=ctx.createOscillator(),g=ctx.createGain();voices++;o.type=type;o.frequency.setValueAtTime(f,ctx.currentTime);o.frequency.exponentialRampToValueAtTime(Math.max(35,f*.45),ctx.currentTime+d);g.gain.setValueAtTime(gain,ctx.currentTime);g.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+d);o.connect(g);g.connect(ctx.destination);o.onended=()=>{voices=Math.max(0,voices-1);o.disconnect();g.disconnect()};o.start();o.stop(ctx.currentTime+d)}catch(e){voices=Math.max(0,voices-1)}}document.addEventListener('visibilitychange',()=>{if(!document.hidden)resume()});for(const event of ['pointerdown','keydown','touchstart'])window.addEventListener(event,resume,{passive:true});/* WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_V1 */"""
    if a.count(old) != 1:
        raise SystemExit("audio synthesis anchor mismatch")
    a = a.replace(old, new, 1)

runtime.write_text(r, encoding="utf-8")
combat.write_text(c, encoding="utf-8")
audio.write_text(a, encoding="utf-8")
for path in (runtime, combat, audio):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr)
print("WILDBOUND_PHASE_11_13_VFX_AUDIO_PERFORMANCE_PATCHED")
