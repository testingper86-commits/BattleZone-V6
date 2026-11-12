#!/usr/bin/env python3
"""Apply functional BattleZone V6 runtime corrections after the ordered game patch pipeline."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
models_files = list(root.rglob("app/src/main/assets/www/js/models.js"))
css_files = list(root.rglob("app/src/main/assets/www/css/v6-critical-gameplay-polish.css"))
if len(htmls) != 1 or len(models_files) != 1 or len(css_files) != 1:
    raise SystemExit(f"Expected one game index, models.js and final gameplay CSS; found {len(htmls)}, {len(models_files)}, {len(css_files)}")
html, models, css_path = htmls[0], models_files[0], css_files[0]
s = html.read_text(encoding="utf-8")
m = models.read_text(encoding="utf-8")
c = css_path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_V1"
if marker in s and marker in m and "BATTLEZONE_V6_COMPLETE_TOUCH_LAYOUT_V1" in c:
    print("BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_ALREADY_APPLIED")
    raise SystemExit(0)

def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return source.replace(old, new, 1)

# The main game character was dressed by the rigged-model pipeline, but the independent
# lobby preview (lobSc) was not. Dress it through the same local model/animation loader.
lobby_anchor = """      if(typeof bots!=='undefined'&&typeof LQ!=='undefined'&&!LQ){
        eachActor((g,i)=>{if(g.userData&&!g.userData.bzDressed&&g.children.length&&!g.userData.retired){
          g.userData.bzDressed=true;
          dress(g,{skinKey:(g.userData.nid||'bot')+i,cull:true,gun:true});}});
      }"""
lobby_fix = lobby_anchor + """
      if(window.lobSc&&window.lobSc.root&&!window.lobSc.root.userData.bzDressed){
        const lobbyName=(typeof bzSelectedCharacter==='function'&&bzSelectedCharacter().name)||'Recruit';
        dress(window.lobSc.root,{skinKey:lobbyName,gun:true});
      }"""
if "window.lobSc.root.userData.bzDressed" not in m:
    m = replace_once(m, lobby_anchor, lobby_fix, "rigged lobby operator integration")

# Touch-editor positions are persisted in screen pixels in the old implementation. Convert
# them once to normalized viewport coordinates, clamp to safe bounds, and reflow on rotation.
old_apply = """function applyCL(){CIDS.forEach(id=>{const e=$(id),c=CL[id];if(c){e.style.left=c.x+'px';e.style.top=c.y+'px';e.style.right='auto';e.style.bottom='auto'}e.style.transform=CL.s?'scale('+CL.s+')':'';e.style.opacity=CL.o||''})}applyCL();"""
new_apply = """function applyCL(){CIDS.forEach(id=>{const e=$(id);if(!e)return;const c=CL[id];if(c&&Number.isFinite(Number(c.x))&&Number.isFinite(Number(c.y))){let x=Number(c.x),y=Number(c.y);if(Math.abs(x)>1||Math.abs(y)>1){x/=Math.max(1,innerWidth);y/=Math.max(1,innerHeight)}const maxX=Math.max(0,innerWidth-e.offsetWidth-8),maxY=Math.max(0,innerHeight-e.offsetHeight-8);x=Math.max(8/Math.max(1,innerWidth),Math.min(maxX/Math.max(1,innerWidth),x));y=Math.max(8/Math.max(1,innerHeight),Math.min(maxY/Math.max(1,innerHeight),y));CL[id]={x,y};e.style.left=(x*100)+'vw';e.style.top=(y*100)+'vh';e.style.right='auto';e.style.bottom='auto'}e.style.transform=CL.s?'scale('+CL.s+')':'';e.style.opacity=CL.o==null?'':String(CL.o)})}applyCL();window.addEventListener('resize',applyCL,{passive:true});"""
if "window.addEventListener('resize',applyCL" not in s:
    s = replace_once(s, old_apply, new_apply, "responsive control layout persistence")
old_joy_drag = "CL.joy={x:e.clientX-jz.offsetWidth/2,y:e.clientY-jz.offsetHeight/2};applyCL();return}"
new_joy_drag = "CL.joy={x:(e.clientX-jz.offsetWidth/2)/Math.max(1,innerWidth),y:(e.clientY-jz.offsetHeight/2)/Math.max(1,innerHeight)};applyCL();return}"
if new_joy_drag not in s:
    s = replace_once(s, old_joy_drag, new_joy_drag, "normalized joystick editor drag")
old_button_drag = "CL[id]={x:e.clientX-el.offsetWidth/2,y:e.clientY-el.offsetHeight/2};applyCL()"
new_button_drag = "CL[id]={x:(e.clientX-el.offsetWidth/2)/Math.max(1,innerWidth),y:(e.clientY-el.offsetHeight/2)/Math.max(1,innerHeight)};applyCL()"
if new_button_drag not in s:
    s = replace_once(s, old_button_drag, new_button_drag, "normalized button editor drag")

# The WebAudio master gain was hard-coded to 0.85 and settings only offered a mute toggle.
# Persist a real effects-volume level and expose a safe resume API for Android WebView gestures.
old_audio = """let AC,MG,NB,SND_ON=sg('bzm')!=='0';
function actx(){if(!AC){AC=new(window.AudioContext||window.webkitAudioContext)();MG=AC.createGain();MG.gain.value=.85;MG.connect(AC.destination);const n=AC.sampleRate,b=AC.createBuffer(1,n,AC.sampleRate),d=b.getChannelData(0);for(let i=0;i<n;i++)d[i]=Math.random()*2-1;NB=b}if(AC.state==='suspended')AC.resume();return AC}"""
new_audio = """let AC,MG,NB,SND_ON=sg('bzm')!=='0';
function actx(){if(!AC){AC=new(window.AudioContext||window.webkitAudioContext)();MG=AC.createGain();MG.gain.value=Math.max(0,Math.min(1,Number(sg('bzvol')??.85)));MG.connect(AC.destination);const n=AC.sampleRate,b=AC.createBuffer(1,n,AC.sampleRate),d=b.getChannelData(0);for(let i=0;i<n;i++)d[i]=Math.random()*2-1;NB=b}if(AC.state==='suspended')AC.resume().catch(()=>{});return AC}
window.BZAudio=Object.freeze({isEnabled:()=>SND_ON,getVolume:()=>Math.max(0,Math.min(1,Number(sg('bzvol')??.85))),setEnabled:on=>{SND_ON=!!on;ss('bzm',SND_ON?'1':'0');if(SND_ON){try{const a=actx();if(a.state==='suspended')a.resume().catch(()=>{})}catch(e){}}},setVolume:value=>{const v=Math.max(0,Math.min(1,Number(value)||0));ss('bzvol',String(v));if(MG&&AC)MG.gain.setTargetAtTime(v,AC.currentTime,.025);return v},resume:()=>{if(!SND_ON)return Promise.resolve(false);try{const a=actx();return a.state==='suspended'?a.resume().then(()=>true).catch(()=>false):Promise.resolve(true)}catch(e){return Promise.resolve(false)}}});
document.addEventListener('pointerdown',()=>window.BZAudio.resume(),{once:true,passive:true});"""
if "window.BZAudio=Object.freeze" not in s:
    s = replace_once(s, old_audio, new_audio, "WebAudio lifecycle and effects volume API")

# Make the settings volume control real and keep the mute button synchronized with the runtime.
sound_button = r'''<button id="bhSound"><span>Game audio</span><strong>${localStorage.getItem('bzm')==='0'?'Off':'On'} ↗</strong></button>'''
sound_with_volume = sound_button + r'''<div class="bz-audio-level"><label for="bzMasterVolume">Effects volume</label><output id="bzMasterVolumeValue">${Math.round((window.BZAudio?window.BZAudio.getVolume():.85)*100)}%</output><input id="bzMasterVolume" type="range" min="0" max="100" step="1" value="${Math.round((window.BZAudio?window.BZAudio.getVolume():.85)*100)}" aria-label="Effects volume"></div>'''
if 'id="bzMasterVolume"' not in s:
    s = replace_once(s, sound_button, sound_with_volume, "functional effects volume settings control")
old_sound_handler = "$('bhSound').onclick=()=>{const on=localStorage.getItem('bzm')==='0';localStorage.setItem('bzm',on?'1':'0');$('bhSound').querySelector('strong').textContent=(on?'On':'Off')+' ↗'};"
new_sound_handler = "$('bhSound').onclick=()=>{const on=localStorage.getItem('bzm')==='0';if(window.BZAudio)window.BZAudio.setEnabled(on);else localStorage.setItem('bzm',on?'1':'0');$('bhSound').querySelector('strong').textContent=(on?'On':'Off')+' ↗'};const bzVolume=$('bzMasterVolume'),bzVolumeValue=$('bzMasterVolumeValue');if(bzVolume){bzVolume.value=String(Math.round((window.BZAudio?window.BZAudio.getVolume():.85)*100));if(bzVolumeValue)bzVolumeValue.textContent=bzVolume.value+'%';bzVolume.addEventListener('input',()=>{const value=Number(bzVolume.value)/100;if(window.BZAudio)window.BZAudio.setVolume(value);if(bzVolumeValue)bzVolumeValue.textContent=bzVolume.value+'%'})}"
if "const bzVolume=$('bzMasterVolume')" not in s:
    s = replace_once(s, old_sound_handler, new_sound_handler, "live audio settings handlers")
old_reset = "['bzq','bzw','bzn','bzfade','bzbs','bzsn','bzc2'].forEach(k=>localStorage.removeItem(k))"
new_reset = "['bzq','bzw','bzn','bzfade','bzbs','bzsn','bzc2','bzvol'].forEach(k=>localStorage.removeItem(k))"
if new_reset not in s:
    s = replace_once(s, old_reset, new_reset, "reset effects volume preference")

# Final portrait HUD: use three non-overlapping columns on the right and a separate left-side
# movement/action lane. The old rules stacked fire over jump and scope over prone.
portrait_marker = "/* BATTLEZONE_V6_COMPLETE_TOUCH_LAYOUT_V1 */"
if portrait_marker not in c:
    c += r"""

/* BATTLEZONE_V6_COMPLETE_TOUCH_LAYOUT_V1 */
.b{touch-action:none;pointer-events:auto}
@media (orientation:portrait){
 #joy{width:132px;height:132px}
 #fire{right:calc(var(--bz-safe-r) + 18px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important;width:76px!important;height:76px!important}
 #jump{right:calc(var(--bz-safe-r) + 18px)!important;bottom:calc(var(--bz-safe-b) + 108px)!important}
 #crouch{right:calc(var(--bz-safe-r) + 80px)!important;bottom:calc(var(--bz-safe-b) + 108px)!important}
 #prone{right:calc(var(--bz-safe-r) + 18px)!important;bottom:calc(var(--bz-safe-b) + 168px)!important}
 #scope{right:calc(var(--bz-safe-r) + 80px)!important;bottom:calc(var(--bz-safe-b) + 168px)!important}
 #rel{right:calc(var(--bz-safe-r) + 104px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important}
 #swap{right:calc(var(--bz-safe-r) + 166px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important}
 #thr{right:calc(var(--bz-safe-r) + 166px)!important;bottom:calc(var(--bz-safe-b) + 78px)!important}
 #gsw{right:calc(var(--bz-safe-r) + 166px)!important;bottom:calc(var(--bz-safe-b) + 138px)!important}
 #sprint{left:calc(var(--bz-safe-l) + 154px)!important;bottom:calc(var(--bz-safe-b) + 18px)!important}
 #vw{left:calc(var(--bz-safe-l) + 154px)!important;bottom:calc(var(--bz-safe-b) + 78px)!important}
 #fire2{left:calc(var(--bz-safe-l) + 154px)!important;bottom:calc(var(--bz-safe-b) + 138px)!important;right:auto!important;top:auto!important}
 #lnl,#lnr{display:none!important}
}
.bz-audio-level{display:grid;grid-template-columns:1fr auto;gap:8px 12px;align-items:center;padding:10px 12px;border:1px solid #ffffff1c;border-radius:10px;background:#07111b80}
.bz-audio-level label{font-size:12px;font-weight:750;color:#dceaf5}
.bz-audio-level output{font-size:12px;font-weight:800;color:#78ddff;font-variant-numeric:tabular-nums}
.bz-audio-level input{grid-column:1/-1;width:100%;accent-color:#53d9ff;touch-action:pan-y}
"""

# Include a visible version marker in the runtime document for build provenance and regression checks.
if marker not in s:
    s = s.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
if marker not in m:
    m = m.replace("/* Rigged character models", "/* " + marker + " */\n/* Rigged character models", 1)
html.write_text(s, encoding="utf-8")
models.write_text(m, encoding="utf-8")
css_path.write_text(c, encoding="utf-8")
print("BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_APPLIED", html, models, css_path)
