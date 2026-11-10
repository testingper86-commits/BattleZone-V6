#!/usr/bin/env python3
"""Keep the real WILDBOUND lobby visible when WebGL or Android WebView startup fails."""
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
MARKER = "WILDBOUND_STARTUP_RECOVERY_V1"

def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    return source.replace(old, new, 1)

def locate(relative: str) -> Path:
    direct = ROOT / relative
    if direct.is_file():
        return direct
    found = list(ROOT.rglob(relative))
    if len(found) != 1:
        raise SystemExit(f"Expected exactly one {relative}, found {len(found)}")
    return found[0]

runtime_path = locate("app/src/main/assets/www/js/wildbound/rendering/runtime.js")
boot_path = locate("app/src/main/assets/www/js/wildbound/frontend/boot.js")
css_path = locate("app/src/main/assets/www/css/wildbound.css")
activity_path = locate("app/src/main/java/com/example/battlezone/MainActivity.kt")
runtime = runtime_path.read_text(encoding="utf-8")
boot = boot_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
activity = activity_path.read_text(encoding="utf-8")

if all(MARKER in value for value in (runtime, boot, css, activity)):
    combined = boot + runtime + css + activity
    required = ("startup-status", "ensureUi", "onReceivedError", "WILDBOUND document failed")
    missing = [item for item in required if item not in combined]
    if missing:
        raise SystemExit("Startup recovery marker exists but is incomplete: " + ", ".join(missing))
    scene_start = runtime.find("function makeScene(){")
    scene_end = runtime.find("function resize(){", scene_start)
    if scene_start < 0 or scene_end < 0:
        raise SystemExit("Startup recovery cannot isolate makeScene for UI initialization validation")
    scene = runtime[scene_start:scene_end]
    if "W.ui.init(game);" in scene:
        scene = scene.replace("W.ui.init(game);", "", 1)
        runtime = runtime[:scene_start] + scene + runtime[scene_end:]
        runtime_path.write_text(runtime, encoding="utf-8")
        print("WILDBOUND_STARTUP_RECOVERY_UI_INIT_REPAIRED")
    else:
        print("WILDBOUND_STARTUP_RECOVERY_ALREADY_APPLIED")
    raise SystemExit(0)

legacy_ui_anchor = "window.addEventListener('resize',resize);W.ui.init(game);;W.bus.on('contract-complete',()=>{game.done=true});"
animated_ui_anchor = "window.addEventListener('resize',resize);W.ui.init(game);W.bus.on('contract-complete',()=>{game.done=true});raf=requestAnimationFrame(lobbyLoop);"
if runtime.count(legacy_ui_anchor) == 1:
    runtime = runtime.replace(legacy_ui_anchor,
        "window.addEventListener('resize',resize);W.bus.on('contract-complete',()=>{game.done=true});", 1)
elif runtime.count(animated_ui_anchor) == 1:
    runtime = runtime.replace(animated_ui_anchor,
        "window.addEventListener('resize',resize);W.bus.on('contract-complete',()=>{game.done=true});raf=requestAnimationFrame(lobbyLoop);", 1)
else:
    raise SystemExit("move lobby UI initialization out of renderer construction: expected one supported source anchor")
runtime = one(runtime,
    "function makeScene(){let t=T();game.THREE=t;",
    "function makeScene(){let t=T();if(!t||!t.WebGLRenderer)throw new Error('The bundled Three.js engine did not load. Check the local libs/three.min.js asset.');game.THREE=t;",
    "explicit Three.js dependency failure")
runtime = one(runtime,
    "W.main.initialize=()=>{makeScene();W.main.setQuality(W.state.settings.quality||'high');W.ui.refresh()};W.main.resize=resize})();",
    """let uiInitialized=false;
W.main.ensureUi=()=>{if(!uiInitialized){W.ui.init(game);uiInitialized=true}};
let startupStage='runtime initialization';
W.main.getStartupStage=()=>startupStage;
const makeSceneBeforeRecovery=makeScene;
makeScene=function(){
 const stage=(name,operation)=>{startupStage=name;try{return operation()}catch(error){error.message='WILDBOUND startup stage ['+name+']: '+(error&&error.message||error);throw error}};
 try{
  stage('Three.js and scene allocation',()=>makeSceneBeforeRecovery());
  startupStage='scene ready';
 }catch(error){
  try{if(game.renderer){game.renderer.dispose();if(game.renderer.forceContextLoss)game.renderer.forceContextLoss()}}catch(cleanupError){console.error('[WILDBOUND] renderer cleanup failed',cleanupError)}
  game.renderer=null;game.scene=null;game.camera=null;game.previewScene=null;game.previewCamera=null;
  throw error;
 }
};
W.main.initialize=()=>{startupStage='lobby UI initialization';W.main.ensureUi();startupStage='scene construction';makeScene();startupStage='graphics quality setup';W.main.setQuality(W.state.settings.quality||'high');startupStage='lobby refresh';W.ui.refresh();startupStage='ready'};
W.main.resize=resize;
})();""",
    "initialize actual lobby controls before WebGL")
runtime = "/* " + MARKER + " */\n" + runtime

boot = r"""/* WILDBOUND_STARTUP_RECOVERY_V1 */
(()=>{'use strict';
const W=window.WILDBOUND,$=id=>document.getElementById(id);
let booted=false;
function revealLobby(){
 const splash=$('boot'),lobby=$('lobby'),game=$('game');
 if(splash)splash.classList.add('hidden');
 if(lobby)lobby.classList.remove('hidden');
 if(game)game.classList.add('hidden');
 if(W&&W.state)W.state.screen='lobby';
}
function status(message,detail){
 const lobby=$('lobby');if(!lobby)return;
 let panel=$('startup-status');
 if(!panel){
  panel=document.createElement('aside');panel.id='startup-status';panel.className='startup-status';panel.setAttribute('role','alert');
  const title=document.createElement('strong');title.className='startup-status-title';title.textContent='3D INITIALIZATION NEEDS ATTENTION';
  const copy=document.createElement('p');copy.className='startup-status-copy';
  const diagnostic=document.createElement('pre');diagnostic.className='startup-status-detail';
  const retry=document.createElement('button');retry.className='secondary startup-status-retry';retry.type='button';retry.textContent='RETRY STARTUP';
  retry.addEventListener('click',()=>window.location.reload());
  panel.append(title,copy,diagnostic,retry);lobby.appendChild(panel);
 }
 panel.querySelector('.startup-status-copy').textContent=message;
 panel.querySelector('.startup-status-detail').textContent=String(detail||'No additional diagnostic information.').slice(0,1200);
 panel.classList.add('visible');
}
function ensureUi(){
 if(W&&W.main&&typeof W.main.ensureUi==='function')W.main.ensureUi();
}
function guardDeploy(){
 const deploy=$('deploy');
 if(!deploy||deploy.dataset.startupGuard==='1')return;
 const original=deploy.onclick;
 deploy.onclick=function(event){
  try{
   if(typeof original!=='function')throw new Error('The deployment control was not initialized.');
   const result=original.call(this,event);
   if(W&&W.state&&W.state.screen!=='game')throw new Error('Deployment returned without entering gameplay.');
   return result;
  }catch(error){
   revealLobby();
   status('The lobby is available, but the hunt could not initialize. The renderer error is shown below.',error&&error.stack||error);
   return false;
  }
 };
 deploy.dataset.startupGuard='1';
}
function boot(){
 if(booted)return;booted=true;
 revealLobby();
 if(!W||!W.main||typeof W.main.initialize!=='function'){
  status('The game runtime did not finish loading. The original lobby is being kept visible instead of leaving a blank screen.','Missing WILDBOUND runtime modules or an earlier JavaScript load error.');
  return;
 }
 try{W.main.initialize();}
 catch(error){
  revealLobby();
  try{ensureUi();}catch(uiError){status('The lobby is visible, but its controls could not initialize.',String(uiError&&uiError.stack||uiError));return;}
  status('The lobby is available, but 3D initialization failed at: '+(W.main.getStartupStage?W.main.getStartupStage():'unknown stage')+'. No fake scene is shown.',error&&error.stack||error);
 }
 guardDeploy();
 try{if(W.ui&&typeof W.ui.refresh==='function')W.ui.refresh()}catch(error){status('The lobby loaded, but its status display could not refresh.',error&&error.stack||error);}
}
window.addEventListener('error',event=>{
 if(event&&event.target&&event.target.tagName==='SCRIPT'){
  revealLobby();status('A local game script failed to load.',event.target.src||event.message||'Unknown script load failure.');
 }
},true);
window.addEventListener('unhandledrejection',event=>{
 if(event&&event.reason)status('A game startup task failed.',event.reason.stack||event.reason);
});
if(W)W.frontend={boot};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
"""
css += r"""
/* WILDBOUND_STARTUP_RECOVERY_V1 */
.startup-status{display:none;position:fixed;z-index:1000;left:50%;top:8px;bottom:8px;transform:translateX(-50%);width:min(560px,calc(100vw - 28px));max-height:none;overflow:auto;padding:16px 18px;background:rgba(10,16,22,.98);border:1px solid rgba(230,110,105,.65);box-shadow:0 18px 60px #000b;color:#e9f0ec}
.startup-status.visible{display:block}
.startup-status-title{display:block;color:#f0b2a9;font-size:11px;letter-spacing:.14em}
.startup-status-copy{font-size:12px;line-height:1.5;color:#d6e0dc;margin:9px 0}
.startup-status-detail{white-space:pre-wrap;overflow-wrap:anywhere;max-height:38vh;overflow:auto;color:#a9b8b4;font:10px/1.45 ui-monospace,monospace;margin:0 0 10px}
.startup-status-retry{width:100%;margin:0}
"""
helper = r'''    // WILDBOUND_STARTUP_RECOVERY_V1
    private fun showDocumentFailure(view: WebView, message: String) {
        val safeMessage = message
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#39;")
        val retryUrl = "https://appassets.androidplatform.net/assets/www/index.html"
        val html = """
            <!doctype html><html lang="en"><head><meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; form-action 'none'; frame-src 'none'">
            <title>WILDBOUND unavailable</title>
            <style>body{margin:0;background:#090d12;color:#e9f0ec;font:16px system-ui;padding:28px}main{max-width:560px;margin:12vh auto}h1{letter-spacing:.12em;color:#f0b2a9}p{line-height:1.55;color:#b8c8c3;overflow-wrap:anywhere}a{display:block;margin-top:22px;padding:15px;background:#75d6c0;color:#091310;text-align:center;text-decoration:none;font-weight:800;letter-spacing:.1em}</style>
            </head><body><main><h1>WILDBOUND COULD NOT LOAD</h1>
            <p>$safeMessage</p><p>The game is stored locally. Retry reloads the bundled game and does not require internet access.</p>
            <a href="$retryUrl">RETRY GAME STARTUP</a></main></body></html>
        """.trimIndent()
        view.loadDataWithBaseURL("https://appassets.androidplatform.net/assets/www/", html, "text/html", "UTF-8", null)
    }
'''
if MARKER not in activity:
    activity = one(activity,
        '    @SuppressLint("SetJavaScriptEnabled")',
        helper + '    @SuppressLint("SetJavaScriptEnabled")',
        "insert Android document failure handler")
    activity = one(activity,
        "            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {",
        """                override fun onReceivedError(
                        view: WebView,
                        request: WebResourceRequest,
                        error: android.webkit.WebResourceError
                    ) {
                        android.util.Log.e("WILDBOUND", "Resource failed (mainFrame=" + request.isForMainFrame + ", code=" + error.errorCode + "): " + request.url + " " + error.description)
                        if (request.isForMainFrame) showDocumentFailure(view, error.description.toString())
                    }
                    override fun onReceivedHttpError(
                        view: WebView,
                        request: WebResourceRequest,
                        response: android.webkit.WebResourceResponse
                    ) {
                        android.util.Log.e("WILDBOUND", "HTTP " + response.statusCode + " for " + request.url)
                        if (request.isForMainFrame && response.statusCode >= 400) showDocumentFailure(view, "WILDBOUND document failed with HTTP " + response.statusCode + ".")
                    }
                    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {""",
        "add main-document WebView failure recovery")
    activity = one(activity,
        '        webView.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")',
        '        android.util.Log.i("WILDBOUND", "Loading bundled offline game document")\n        webView.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")',
        "trace bundled WebView launch")
else:
    required_activity = ("onReceivedError", "onReceivedHttpError", "showDocumentFailure", "RETRY GAME STARTUP")
    missing_activity = [item for item in required_activity if item not in activity]
    if missing_activity:
        raise SystemExit("Android startup marker exists but is incomplete: " + ", ".join(missing_activity))

if MARKER not in activity:
    raise SystemExit("Android startup recovery marker missing after patch")

for path, content in ((runtime_path, runtime), (boot_path, boot), (css_path, css), (activity_path, activity)):
    path.write_text(content, encoding="utf-8")
print("WILDBOUND_STARTUP_RECOVERY_APPLIED")
