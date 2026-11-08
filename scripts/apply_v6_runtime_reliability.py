#!/usr/bin/env python3
"""Harden V6 WebView startup, WebGL context ownership, and lobby layout."""
from pathlib import Path
import shutil, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
hs=list(root.rglob("app/src/main/assets/www/index.html"))
ks=list(root.rglob("app/src/main/java/com/example/battlezone/MainActivity.kt"))
if len(hs)!=1 or len(ks)!=1: raise SystemExit(f"Expected one game HTML and MainActivity.kt, found {len(hs)} and {len(ks)}")
hp,kp=hs[0],ks[0]; s=hp.read_text(encoding="utf-8"); k=kp.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_RUNTIME_RELIABILITY_V2"
if marker in s and marker in k: print("BATTLEZONE_V6_RUNTIME_RELIABILITY_ALREADY_APPLIED"); raise SystemExit(0)
def once(src,old,new,label):
    n=src.count(old)
    if n!=1: raise SystemExit(f"{label}: expected one source anchor, found {n}")
    return src.replace(old,new,1)
probe=""" if(!gl){window.bzFatal('WebGL is not available','<p>This device/emulator cannot create a WebGL context, so the 3D world cannot draw.</p><ul><li><b>Emulator:</b> AVD Manager &rarr; Edit &rarr; Show Advanced Settings &rarr; Emulated Performance &rarr; Graphics: <b>Hardware - GLES 2.0/3.0</b>, then cold-boot.</li><li><b>Real phone:</b> update <i>Android System WebView</i> from Google Play.</li></ul>');return}
 window.__bzNote('WebGL OK: '+info+' | Three r'+rev);"""
s=once(s,probe,""" if(!gl){window.bzFatal('WebGL is not available','<p>This device/emulator cannot create a WebGL context, so the 3D world cannot draw.</p><ul><li><b>Emulator:</b> AVD Manager &rarr; Edit &rarr; Show Advanced Settings &rarr; Emulated Performance &rarr; Graphics: <b>Hardware - GLES 2.0/3.0</b>, then cold-boot.</li><li><b>Real phone:</b> update <i>Android System WebView</i> from Google Play.</li></ul>');return}
 var loseProbe=gl.getExtension('WEBGL_lose_context');if(loseProbe)loseProbe.loseContext();gl=null;t.width=1;t.height=1;t=null;
 window.__bzNote('WebGL OK: '+info+' | Three r'+rev+' | probe context released');""","WebGL diagnostic context release")
s=once(s,"r.render=function(){window.__bzFrames++;return rr.apply(this,arguments)};","r.render=function(){if(r.domElement&&r.domElement.id==='c')window.__bzFrames++;return rr.apply(this,arguments)};","game-canvas frame watchdog")
s=once(s,"function showErr(e){try{let d=document.getElementById('errb');","function showErr(e){try{const message=String(e&&e.stack?e.stack.split('\\n').slice(0,3).join(' | '):e);if(window.__bzNote&&window.__bzLastLoopError!==message){window.__bzLastLoopError=message;window.__bzNote('Game loop: '+message)}let d=document.getElementById('errb');","loop error diagnostics")
old="""{const cv=document.createElement('canvas');cv.style.cssText='width:100%;height:100%';$('char').appendChild(cv);const lr=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true});lr.setSize(220,300,false);const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,220/300,.1,50);ls.add(new THREE.HemisphereLight(0xffffff,0x6a7a70,1));const ld=new THREE.DirectionalLight(0xffffff,.8);ld.position.set(3,5,4);ls.add(ld);
 const sc=mkScout((bzSelectedCharacter().color||SKN[ST_.cur][1]),0,PLOOK);ls.add(sc.root);window.lobSc=sc;lc.position.set(0,1.1,4.6);lc.lookAt(0,1,0);
 let lastLobbyRender=0;requestAnimationFrame(function ll(n){if(started){lr.dispose();lr.forceContextLoss();cv.remove();return}if(!document.hidden&&n-lastLobbyRender>=50){const dt=lastLobbyRender?Math.min(.05,(n-lastLobbyRender)/1000):.016;lastLobbyRender=n;const t=n/1000;animSc(sc,0,dt,t);sc.root.rotation.y=Math.sin(t*.5)*.7+(window.lobOff||0);lr.render(ls,lc)}requestAnimationFrame(ll)})}"""
new="""{const host=$('char');if(host){let cv=null,activeRenderer=null,activeScene=null,activeCamera=null,activeModel=null,closed=false,lastLobbyRender=0,retryAt=0,previewErrorReported=false,fitLobbyRenderer=null,lobbyResizeObserver=null;const fallback=()=>host.classList.add('bz-preview-fallback');const release=()=>{if(fitLobbyRenderer){window.removeEventListener('resize',fitLobbyRenderer);window.removeEventListener('orientationchange',fitLobbyRenderer);fitLobbyRenderer=null}if(lobbyResizeObserver){lobbyResizeObserver.disconnect();lobbyResizeObserver=null}try{if(activeRenderer){activeRenderer.dispose();activeRenderer.forceContextLoss()}}catch(e){}if(cv)cv.remove();cv=null;activeRenderer=null;activeScene=null;activeCamera=null;activeModel=null;window.lobSc=null};const createLobbyPreview=(n)=>{if(activeRenderer||closed||!host.isConnected)return;try{cv=document.createElement('canvas');cv.style.cssText='width:100%;height:100%';host.appendChild(cv);const lr=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:false,powerPreference:'low-power'});activeRenderer=lr;lr.setPixelRatio(Math.min(devicePixelRatio||1,1));lr.setSize(220,300,false);const ls=new THREE.Scene(),lc=new THREE.PerspectiveCamera(35,220/300,.1,50);activeScene=ls;activeCamera=lc;ls.add(new THREE.HemisphereLight(0xffffff,0x6a7a70,1));const ld=new THREE.DirectionalLight(0xffffff,.8);ld.position.set(3,5,4);ls.add(ld);const sc=mkScout((bzSelectedCharacter().color||SKN[ST_.cur][1]),0,PLOOK);ls.add(sc.root);window.lobSc=sc;lc.position.set(0,1.1,4.6);lc.lookAt(0,1,0);activeModel=sc;host.classList.remove('bz-preview-fallback');lastLobbyRender=0;return true}catch(e){release();fallback();retryAt=n+1500;if(!previewErrorReported){window.__bzNote&&window.__bzNote('Lobby preview unavailable: '+(e.message||e));previewErrorReported=true}return false}};requestAnimationFrame(function ll(n){if(closed)return;if(started||document.hidden||!host.isConnected){if(activeRenderer)release();requestAnimationFrame(ll);return}if(!activeRenderer&&n>=retryAt)createLobbyPreview(n);if(activeRenderer&&activeModel&&n-lastLobbyRender>=50){const dt=lastLobbyRender?Math.min(.05,(n-lastLobbyRender)/1000):.016;lastLobbyRender=n;const t=n/1000;try{animSc(activeModel,0,dt,t);activeModel.root.rotation.y=Math.sin(t*.5)*.7+(window.lobOff||0);activeRenderer.render(activeScene,activeCamera)}catch(e){release();fallback();retryAt=n+1500;if(!previewErrorReported){window.__bzNote&&window.__bzNote('Lobby preview disabled: '+(e.message||e));previewErrorReported=true}}}requestAnimationFrame(ll)})}}"""

s=once(s,old,new,"safe optional lobby WebGL preview")
s=once(s,"setTimeout(()=>{try{go0()}catch(e){showErr(e)}ld.classList.remove('on');setTimeout(()=>ld.classList.remove('show'),350)},1100)};","setTimeout(()=>{try{go0();if(!started)throw new Error('Deployment handler returned without starting the match');ld.classList.remove('on');setTimeout(()=>ld.classList.remove('show'),350)}catch(e){busy=0;showErr(e);ld.classList.remove('on');ld.classList.remove('show');ld.style.display='none';$('lobby').style.display='';$('go2').disabled=false;window.bzFatal&&window.bzFatal('Match deployment failed','<p>The match could not start. The lobby has been restored. The last runtime errors are shown below.</p>')}},1100)};","deployment failure recovery")
s=once(s,"</head>","<link rel=\"stylesheet\" href=\"./css/v6-runtime-reliability.css\">\n</head>","runtime reliability stylesheet link")
s=s.replace("</html>","<!-- "+marker+" -->\n</html>",1)
css=Path(__file__).with_name("v6-runtime-reliability.css")
if not css.is_file(): raise SystemExit(f"Missing required stylesheet: {css}")
target=hp.parent/"css"/css.name; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(css,target)
k=once(k,"            setBackgroundColor(android.graphics.Color.BLACK)\n            settings.javaScriptEnabled = true","            setBackgroundColor(android.graphics.Color.BLACK)\n            setLayerType(View.LAYER_TYPE_HARDWARE, null)\n            isVerticalScrollBarEnabled = false\n            overScrollMode = View.OVER_SCROLL_NEVER\n            settings.javaScriptEnabled = true","WebView hardware surface and viewport")
oldnav="""                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                    request.url.host != "appassets.androidplatform.net"

                override fun onReceivedHttpError("""
newnav="""                override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                    android.util.Log.i("BattleZoneWeb", "Loading game document: $url")
                }

                override fun onPageFinished(view: WebView, url: String) {
                    android.util.Log.i("BattleZoneWeb", "Game document loaded: $url")
                    view.evaluateJavascript("JSON.stringify({ready:document.readyState,three:window.__bzThreeRev,frames:window.__bzFrames})") { state ->
                        android.util.Log.i("BattleZoneWeb", "Game startup state: $state")
                    }
                }

                override fun onReceivedError(
                    view: WebView,
                    request: WebResourceRequest,
                    error: android.webkit.WebResourceError
                ) {
                    android.util.Log.e("BattleZoneWeb", "Resource load failed (mainFrame=" + request.isForMainFrame + ", code=" + error.errorCode + "): " + request.url + " " + error.description)
                    if (request.isForMainFrame) {
                        val message = error.description.toString().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        view.loadDataWithBaseURL("https://appassets.androidplatform.net/", "<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><body style='margin:0;background:#07111d;color:#edf5fb;font:16px system-ui;padding:28px'><h2>Battle Zone could not load</h2><p>$message</p><p>Close and reopen the app. If this repeats, send the BattleZoneWeb Logcat entries to the developer.</p></body>", "text/html", "UTF-8", null)
                    }
                }

                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                    request.url.host != "appassets.androidplatform.net"

                override fun onReceivedHttpError("""
k=once(k,oldnav,newnav,"WebView page lifecycle and load failure diagnostics")
k=once(k,"        webView.loadUrl(\"https://appassets.androidplatform.net/assets/www/index.html\")","        android.util.Log.i(\"BattleZoneWeb\", \"Starting offline WebView game host\")\n        webView.loadUrl(\"https://appassets.androidplatform.net/assets/www/index.html\")","WebView launch trace")
k=k.replace("class MainActivity : Activity() {","class MainActivity : Activity() {\n    // "+marker,1)
hp.write_text(s,encoding="utf-8"); kp.write_text(k,encoding="utf-8")
print("BATTLEZONE_V6_RUNTIME_RELIABILITY_APPLIED",hp,kp)
