#!/usr/bin/env python3
"""Make match-critical audio cues independent of the optional Player Hub voice module."""
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
path=files[0]
source=path.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_VOICE_STARTUP_FIX_V1"
if marker in source:
    print("BATTLEZONE_V6_VOICE_STARTUP_FIX_ALREADY_APPLIED")
    raise SystemExit(0)

def once(old,new,label):
    global source
    count=source.count(old)
    if count!=1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    source=source.replace(old,new,1)

sound="function snd(f,d,v,o){if(!SND_ON)return;try{if(o||f){tn(f||200,(f||200)*.7,d,v,'sine')}else if(d>=.5){nz(d,v,380,'lowpass');tn(110,30,d*.9,v*1.3,'sine');nz(d*.4,v*.6,1800,'lowpass')}else if(d<=.06){nz(d,v*1.5,900,'bandpass',1.2)}else{nz(d,v,3600,'lowpass');nz(d*.5,v*.7,1100,'bandpass',.9);tn(150,45,d*.8,v*.9,'triangle')}}catch(e){}}"
fallback="""function snd(f,d,v,o){if(!SND_ON)return;try{if(o||f){tn(f||200,(f||200)*.7,d,v,'sine')}else if(d>=.5){nz(d,v,380,'lowpass');tn(110,30,d*.9,v*1.3,'sine');nz(d*.4,v*.6,1800,'lowpass')}else if(d<=.06){nz(d,v*1.5,900,'bandpass',1.2)}else{nz(d,v,3600,'lowpass');nz(d*.5,v*.7,1100,'bandpass',.9);tn(150,45,d*.8,v*.9,'triangle')}}catch(e){}}
// Match startup and combat must never depend on the optional Player Hub voice-pack script.
window.bzPlayEventVoice=window.bzPlayEventVoice||function(eventName){
 if(!SND_ON)return;
 try{
  if(eventName==='victory'){tn(523,784,.18,.12,'sine');tn(659,988,.18,.12,'sine',.18);tn(784,1175,.28,.14,'sine',.36)}
  else if(eventName==='combat'){nz(.08,.12,1200,'bandpass',1.1);tn(180,70,.1,.12,'triangle')}
  else{tn(440,660,.12,.1,'sine');tn(660,880,.12,.08,'sine',.12)}
 }catch(e){}
};"""
once(sound,fallback,"early safe event-audio fallback")
once("bzPlayEventVoice('victory')","window.bzPlayEventVoice?.('victory')","victory event audio call")
once("bzPlayEventVoice('combat')","window.bzPlayEventVoice?.('combat')","combat event audio call")
once("bzPlayEventVoice('spawn')","window.bzPlayEventVoice?.('spawn')","spawn event audio call")
source=source.replace("</body>","<!-- "+marker+" -->\n</body>",1)
if marker not in source:
    raise SystemExit("Could not write V6 voice startup fix marker")
path.write_text(source,encoding="utf-8")
print("BATTLEZONE_V6_VOICE_STARTUP_FIX_APPLIED",path)
