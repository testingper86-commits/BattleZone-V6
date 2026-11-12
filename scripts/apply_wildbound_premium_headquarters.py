#!/usr/bin/env python3
"""Install the WILDBOUND premium headquarters/profile frontend layer."""
from pathlib import Path
import sys,subprocess
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
www=root/"app/src/main/assets/www"
html=www/"index.html";css=www/"css/wildbound.css";ui=www/"js/wildbound/ui/interface.js"
for p in (html,css,ui):
 if not p.is_file(): raise SystemExit(f"Missing headquarters frontend dependency: {p}")
h=html.read_text(encoding="utf-8");c=css.read_text(encoding="utf-8");j=ui.read_text(encoding="utf-8")
marker="WILDBOUND_PREMIUM_HEADQUARTERS_V1"
if marker in h:
 print("WILDBOUND_PREMIUM_HEADQUARTERS_ALREADY_APPLIED")
 raise SystemExit(0)
def once(src,old,new,label):
 n=src.count(old)
 if n!=1: raise SystemExit(f"{label}: expected one anchor, found {n}")
 return src.replace(old,new,1)
h=once(h,'<span id="xp">0 XP</span>','<span id="xp">0 XP</span><div class="rank-track" aria-label="Progress to next rank"><i id="rank-progress"></i></div><button id="field-record" class="record-button" type="button">FIELD RECORD</button>',"rank and profile header")
h=once(h,'<section id="lobby" class="screen hidden">','<section id="lobby" class="screen hidden" aria-label="WILDBOUND headquarters">',"lobby landmark")
h=once(h,'<section id="game" class="screen hidden">','<section id="game" class="screen hidden" aria-label="Active hunt">',"game landmark")
h=h.replace("</head>","<meta name=\"description\" content=\"WILDBOUND offline hunting headquarters and Blackpine Reserve field operations\"></head>",1)
h=h.replace("<!-- "+marker+" -->","")
h=h.replace("</body>","<!-- "+marker+" --></body>",1)
j=once(j,"$('briefing').onclick=()=>showModal('THE ASHEN VEIL'","$('field-record').onclick=()=>showModal('FIELD RECORD',stat('OPERATIVE RANK',W.data.ranks[Math.min(4,Math.floor(W.state.player.xp/500))])+stat('TOTAL EXPERIENCE',W.state.player.xp+' XP')+stat('ANOMALIES PURGED',W.state.progress.purged||0)+' / 3'+stat('HOSTILES ELIMINATED',W.state.player.kills)+stat('VOID ESSENCE',W.state.player.essence||0)+stat('FIELD TONICS',W.state.inventory.potions)+stat('CONTRACT',W.data.mission.name));$('briefing').onclick=()=>showModal('THE ASHEN VEIL'","field record action")
j=once(j,"$('xp').textContent=p.xp+' XP';","$('xp').textContent=p.xp+' XP';const rankProgress=Math.max(0,Math.min(100,(p.xp%500)/5));$('rank-progress').style.width=rankProgress+'%';$('field-record').setAttribute('aria-label','Open field record. '+p.xp+' experience points. '+(W.state.progress.purged||0)+' of 3 anomalies purged.');","live rank progress")
c += """
/* WILDBOUND_PREMIUM_HEADQUARTERS_V1 */
.player{display:grid;grid-template-columns:auto;justify-items:end;gap:4px;min-width:112px}
.player #xp{font-variant-numeric:tabular-nums}
.rank-track{width:min(118px,22vw);height:3px;background:#ffffff20;overflow:hidden;border-radius:4px}
.rank-track i{display:block;width:0;height:100%;background:linear-gradient(90deg,var(--teal),var(--gold));box-shadow:0 0 9px #75d6c088;transition:width .25s ease}
.record-button{width:auto!important;min-width:0;padding:6px 9px!important;margin:0!important;font-size:8px!important;letter-spacing:.12em;border-color:#75d6c055;color:var(--teal);background:#75d6c00b}
button:focus-visible{outline:2px solid var(--gold);outline-offset:3px;box-shadow:0 0 0 4px #d6b77b24}
button:disabled{opacity:.45;cursor:not-allowed}
#lobby{padding-top:max(22px,env(safe-area-inset-top,0px));padding-bottom:max(15px,env(safe-area-inset-bottom,0px));padding-left:max(3.2vw,env(safe-area-inset-left,0px));padding-right:max(3.2vw,env(safe-area-inset-right,0px))}
.lobby-footer{bottom:max(12px,env(safe-area-inset-bottom,0px) + 6px)}
#modal{padding: max(12px,env(safe-area-inset-top,0px)) max(12px,env(safe-area-inset-right,0px)) max(12px,env(safe-area-inset-bottom,0px)) max(12px,env(safe-area-inset-left,0px))}
#modal .modal{max-height:calc(100dvh - 24px);overflow-y:auto;overscroll-behavior:contain}
#modal-content{overflow-wrap:anywhere}
@media(orientation:landscape) and (max-height:560px){
 #lobby{padding-top:8px;padding-bottom:24px}
 .topbar{height:42px}
 .lobby-grid{height:calc(100% - 72px);gap:1.5vw;grid-template-columns:minmax(180px,24%) minmax(180px,1fr) minmax(175px,22%)}
 .mission-panel,.intel-panel{min-height:0;max-height:calc(100dvh - 105px);overflow-y:auto;padding:12px}
 .mission-meta{margin:10px 0}
 .intel-item{padding:6px 0}
 .hunter-stage{min-height:0}
 .lobby-footer{bottom:4px}
}
@media(max-width:760px){
 .topbar{gap:8px}
 .brand{font-size:12px;letter-spacing:.14em}
 .player{min-width:90px}
 .record-button{font-size:7px!important;padding:5px 7px!important}
}
@media(prefers-reduced-motion:reduce){
 *,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
}
"""
css.write_text(c,encoding="utf-8");html.write_text(h,encoding="utf-8");ui.write_text(j,encoding="utf-8")
for p in (ui,):
 r=subprocess.run(["node","--check",str(p)],capture_output=True,text=True)
 if r.returncode: raise SystemExit(r.stderr)
print("WILDBOUND_PREMIUM_HEADQUARTERS_APPLIED")
