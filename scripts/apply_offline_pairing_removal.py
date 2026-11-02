from pathlib import Path
import re
import shutil
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
marker=root/'OFFLINE_PAIRING_REMOVAL.md'
if marker.exists():
    html=(root/'app/src/main/assets/www/index.html').read_text(encoding='utf-8')
    activity=(root/'app/src/main/java/com/example/battlezone/MainActivity.kt').read_text(encoding='utf-8')
    if any(token in html for token in ['BattleNetwork','BattleZoneMultiplayer','bzRemotePlayers','bzNetActive','bz-net-open']) or any(token in activity for token in ['GameNetworkBridge','BattleNetwork','WifiManager','ServerSocket','DatagramSocket']):
        raise SystemExit('Removal marker exists but network code is still present; refusing an unsafe re-apply.')
    for name in ['README.md','validate_project.py','OFFLINE_PAIRING_REMOVAL.md','ASSET_INVENTORY.md','ANDROID_GAMEPLAY_QA_MATRIX.md']:
        source=Path(__file__).with_name(name); destination=root/name
        if source.resolve()!=destination.resolve(): shutil.copy2(source,destination)
    source=Path(__file__); destination=root/'apply_offline_pairing_removal.py'
    if source.resolve()!=destination.resolve(): shutil.copy2(source,destination)
    print('Offline pairing removal already applied; validation/docs refreshed.')
    raise SystemExit(0)
htmlp=root/'app/src/main/assets/www/index.html'
s=htmlp.read_text(encoding='utf-8')
repls=[
("function spawnBots(){const bzNB=window.bzNetActive?(window.bzNetBotCount?window.bzNetBotCount():0):29,bzSP=window.bzNetActive?90:300;for(let i=0;i<bzNB;i++)", "function spawnBots(){const bzNB=29,bzSP=300;for(let i=0;i<bzNB;i++)"),
("const bzAllyCount=window.bzNetActive?0:(BZ_MODE==='TDM'?3:(BZ_MODE==='FFA'?0:SQ));", "const bzAllyCount=BZ_MODE==='TDM'?3:(BZ_MODE==='FFA'?0:SQ);"),
("if(window.bzNetActive&&window.bzNetBotKilled&&!b.userData.ally){window.bzNetBotKilled(b,byP);return}", ""),
("if(window.bzNetOnStart)window.bzNetOnStart();", ""),
("if(window.bzNetShoot)window.bzNetShoot(rc,h?h.distance:1e9);", ""),
("if(window.bzNetTargets)window.bzNetTargets().forEach(r=>{const d=Math.hypot(r.x-b.position.x,r.z-b.position.z);if(d<bd&&!smk(r.x,r.z)){bd=d;tgt={x:r.x,z:r.z,r:r.id}}});", ""),
("const targetY=tgt.p?(P.y-.25):(tgt.r?1.2:(tgt.o.position.y+1.1));", "const targetY=tgt.p?(P.y-.25):(tgt.o.position.y+1.1);"),
("if(tgt.p){if(window.bzNetActive&&window.bzNetBotHit)window.bzNetBotHit(b,'HOST',rnd(4,9)*[.7,1,1.3][DF]);else dmg(rnd(4,9)*[.7,1,1.3][DF])}else if(tgt.r){if(window.bzNetBotHit)window.bzNetBotHit(b,tgt.r,rnd(4,9)*[.7,1,1.3][DF])}else{tgt.o.userData.hp-=15;if(tgt.o.userData.hp<=0)killBot(tgt.o,false)}", "if(tgt.p){dmg(rnd(4,9)*[.7,1,1.3][DF])}else{tgt.o.userData.hp-=15;if(tgt.o.userData.hp<=0)killBot(tgt.o,false)}"),
('<script src="./js/netplay.js"></script>\n', ''),
]
for old,new in repls:
    count=s.count(old)
    if count!=1: raise SystemExit(f'Expected exactly one occurrence ({count}) for: {old[:100]}')
    s=s.replace(old,new,1)
# Remove settings card and preserve settings reference for performance controls.
pat=r' // Save player-facing preference labels and show an explicit local multiplayer status\..*?networkCard\.onclick=.*?\n'
s,n=re.subn(pat,' // Settings remain local to this device; no pairing or network connection flow is available.\n const settings=document.getElementById(\'setc\');\n',s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'Expected settings card block once, got {n}')
# Remove LAN modal styles, button, panel and JS bridge.
pat=r'\n<style>\n#bz-net-panel\b.*?</script>\n\n(?=<style id="bz-player-hub-css">)'
s,n=re.subn(pat,'\n',s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'Expected one LAN UI block, removed {n}')
# Remove remote avatar event handling and start the ordinary render loop directly.
start='let bzNetStateAt=0;const bzRemotePlayers=new Map();window.bzRemotePlayers=bzRemotePlayers;'
end='window.loop0=function(n){'
if s.count(start)!=1: raise SystemExit('Remote avatar marker is not unique')
a=s.index(start); b=s.index(end,a)
s=s[:a]+end+s[b+len(end):]
for old in [
" if(now-bzNetStateAt>100&&window.BattleZoneMultiplayer){bzNetStateAt=now;window.BattleZoneMultiplayer.sendPlayerState({x:P.x,y:0,z:P.z,yaw:P.yaw,pitch:P.pitch,hp:P.hp,alive:!!P.alive,weapon:W[P.w]?.n||'weapon',team:window.bzNetTeam||(BZ_MODE==='TDM'?'blue':'solo'),name:window.bzNetName||''});}\n",
" for(const [id,a] of bzRemotePlayers){if(now-a.last>7000){bzDisposeAvatar(a);bzRemotePlayers.delete(id);}}\n",
]:
    if s.count(old)!=1: raise SystemExit(f'Expected one loop hook: {old[:80]}')
    s=s.replace(old,'',1)
htmlp.write_text(s,encoding='utf-8')

# Remove remote-only character model attachment code; keep local player and AI bot rigging.
mp=root/'app/src/main/assets/www/js/models.js'
m=mp.read_text(encoding='utf-8')
m=m.replace(" *   - the local player's third-person body, offline/LAN bots and allies  (dress())\n *   - remote LAN players and LAN-bot avatars on other phones             (attach())\n", " *   - the local player's third-person body and offline AI bots/allies (dress())\n")
old="if(state==='idle'&&((window.bzRemotePlayers&&window.bzRemotePlayers.size)||window.pmS||(typeof bots!=='undefined'&&bots.length)))load();"
if m.count(old)!=1: raise SystemExit('models.js load trigger not unique')
m=m.replace(old,"if(state==='idle'&&(window.pmS||(typeof bots!=='undefined'&&bots.length)))load();",1)
start='/* Remote LAN player / bot avatar on another phone. */'; end='/* ---------- per-frame ---------- */'
if m.count(start)!=1 or m.count(end)!=1: raise SystemExit('models.js remote attach markers not unique')
a=m.index(start); b=m.index(end,a); m=m[:a]+m[b:]
old="      const map=window.bzRemotePlayers;\n      if(map)map.forEach((a,id)=>{if(!a.model&&a.group)try{attach(id,a)}catch(e){note('attach failed: '+e.message);a.model=true}});\n"
if m.count(old)!=1: raise SystemExit('models.js remote attach call not unique')
m=m.replace(old,'',1)
old="    if(e.avatar&&!(window.bzRemotePlayers&&window.bzRemotePlayers.get(e.id)===e.avatar)){ // avatar removed\n      if(e.an)e.an.mixer.stopAllAction();entries.splice(i,1);continue}\n"
if m.count(old)!=1: raise SystemExit('models.js remote cleanup not unique')
m=m.replace(old,'',1)
old="    if(e.marker&&e.avatar&&e.avatar.body&&e.avatar.body.material&&e.avatar.body.material.color)e.marker.material.color.copy(e.avatar.body.material.color);\n"
if m.count(old)!=1: raise SystemExit('models.js remote marker not unique')
m=m.replace(old,'',1)
mp.write_text(m,encoding='utf-8')

# Network-free Android activity retaining fullscreen, local asset loading and renderer recovery.
main=root/'app/src/main/java/com/example/battlezone/MainActivity.kt'
main.write_text('''package com.example.battlezone

import android.annotation.SuppressLint
import android.app.Activity
import android.content.pm.ApplicationInfo
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.webkit.ConsoleMessage
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewAssetLoader

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var assetLoader: WebViewAssetLoader

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            window.attributes = window.attributes.apply {
                layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }
        }
        applyImmersive()
        if ((applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            WebView.setWebContentsDebuggingEnabled(true)
        }

        assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView = WebView(this).apply {
            setBackgroundColor(android.graphics.Color.BLACK)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.mediaPlaybackRequiresUserGesture = false
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW

            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                    val line = "${message.message()} -- ${message.sourceId()?.substringAfterLast('/')}:${message.lineNumber()}"
                    when (message.messageLevel()) {
                        ConsoleMessage.MessageLevel.ERROR -> android.util.Log.e("BattleZoneWeb", line)
                        ConsoleMessage.MessageLevel.WARNING -> android.util.Log.w("BattleZoneWeb", line)
                        else -> android.util.Log.d("BattleZoneWeb", line)
                    }
                    return true
                }
            }

            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? {
                    val response = assetLoader.shouldInterceptRequest(request.url) ?: return null
                    val path = request.url.path ?: ""
                    val mime = when (path.substringAfterLast('.', "").lowercase()) {
                        "js", "mjs" -> "text/javascript"
                        "json" -> "application/json"
                        "mp3" -> "audio/mpeg"
                        "ogg" -> "audio/ogg"
                        "wav" -> "audio/wav"
                        "glb" -> "model/gltf-binary"
                        "gltf" -> "model/gltf+json"
                        "fbx" -> "application/octet-stream"
                        "png" -> "image/png"
                        "jpg", "jpeg" -> "image/jpeg"
                        "webp" -> "image/webp"
                        "html" -> "text/html"
                        "css" -> "text/css"
                        else -> null
                    }
                    if (mime != null) response.mimeType = mime
                    return response
                }

                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                    request.url.host != "appassets.androidplatform.net"

                override fun onReceivedHttpError(
                    view: WebView,
                    request: WebResourceRequest,
                    errorResponse: WebResourceResponse
                ) {
                    android.util.Log.w("BattleZoneWeb", "HTTP ${errorResponse.statusCode} for ${request.url}")
                }

                override fun onRenderProcessGone(view: WebView, detail: RenderProcessGoneDetail): Boolean {
                    android.util.Log.e(
                        "BattleZoneWeb",
                        "Renderer process gone (crashed=${detail.didCrash()}); recreating"
                    )
                    runOnUiThread { recreate() }
                    return true
                }
            }
        }

        setContentView(webView)
        webView.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")
    }

    @Suppress("DEPRECATION")
    private fun applyImmersive() {
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_FULLSCREEN or
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE or
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN or
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            )
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) applyImmersive()
    }

    override fun onPause() {
        if (::webView.isInitialized) webView.onPause()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        if (::webView.isInitialized) webView.onResume()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) {
            webView.stopLoading()
            webView.destroy()
        }
        super.onDestroy()
    }
}
''',encoding='utf-8')

# Remove app-level network permissions; game assets are served locally.
manifest=root/'app/src/main/AndroidManifest.xml'
ms=manifest.read_text(encoding='utf-8')
for line in [
'    <uses-permission android:name="android.permission.INTERNET" />\n',
'    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n',
'    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />\n',
'    <uses-permission android:name="android.permission.CHANGE_WIFI_MULTICAST_STATE" />\n',
]:
    if ms.count(line)!=1: raise SystemExit(f'Manifest permission not unique: {line.strip()}')
    ms=ms.replace(line,'',1)
manifest.write_text(ms,encoding='utf-8')

for rel in [
'app/src/main/assets/www/js/netplay.js',
'NETWORK_PROTOCOL.md',
'MULTIPLAYER_IMPLEMENTATION_STATUS.md',
'MULTIPLAYER_DISCOVERY_FIX.md',
'docs/ANIMATION_MULTIPLAYER_COMPLETION_KIT/NETWORK_AUTHORITY_CHECKLIST.md',
]:
    p=root/rel
    if p.exists(): p.unlink()

# Update stale project notes so the Offline package no longer advertises LAN play.
doc_changes={
    'GRAPHICS_UI_GAMEPLAY_FIXES.md': [('while preserving the offline game and the existing LAN multiplayer bridge.', 'while preserving the offline single-player game and AI gameplay.')],
    'ANDROID_BUILD_AUDIT_REPAIR.md': [('Application module and `MainActivity.kt` are present. The Android manifest declares a launcher activity and the permissions used by the current network bridge.', 'Application module and `MainActivity.kt` are present. The Android manifest declares the launcher activity; the WebView serves bundled assets through AndroidX WebViewAssetLoader, with no network bridge or runtime network permissions.'), ('or LAN multiplayer. Those need APK/device tests.', 'or long-session gameplay. Those need APK/device tests.')],
    'BUILD_AND_TEST_STATUS.md': [('Bluetooth permissions and transport UI have been removed.', 'Local device-pairing UI, transport code, and Android network permissions have been removed.')],
    'ASSET_PACKAGE_STATUS.md': [('A successful Gradle build is not proof that animations are wired or that LAN multiplayer works. Test on physical Android devices before release.', 'A successful Gradle build is not proof that animations are wired or that gameplay works. Test on physical Android devices before release.'), ('`js/netplay.js` and network documentation are present, but this archive has not been validated as a completed, fully synchronized LAN multiplayer game. Combat/health, loot, vehicles, safe-zone phases, scoring and reconnect handling need integration verification and physical-device tests. Preserve offline single-player while fixing LAN play.', 'The local LAN pairing feature has been retired from the Offline package. The Android manifest, WebView bridge, room UI, socket/discovery code and remote-player relay are removed; offline single-player and AI modes remain.'), ('## Multiplayer status', '## Retired local pairing feature')],
    'DEVELOPMENT_PLAN.md': [('Existing offline game remains playable without an external game server or internet access; local networking permission is used only for LAN rooms.', 'Existing offline game remains playable without a game server or runtime network access. The Offline package has no pairing or LAN transport code and declares no network permissions.')],
    'FINAL_MERGED_PACKAGE_STATUS.txt': [('- LAN multiplayer combat and match-state synchronization still require implementation and physical-device testing.', '- Local device pairing and LAN multiplayer transport have been removed from the Offline package.')],
    'PROFESSIONAL_UPGRADE_STATUS.md': [('- Android WebView wrapper and LAN room source: password-protected rooms, UDP discovery, multi-client TCP relay and remote-player position/avatar previews.', '- Android WebView wrapper with local offline gameplay; LAN room hosting, discovery, relay and remote-player avatar code have been removed.')],
    'MAP_EXPANSION_AND_FIVE_PHASE_ZONE.md': [('- Multiplayer room discovery, password validation, and synchronized gameplay remain separate incomplete work; this update does not claim those features are complete.', '- Local device pairing and LAN multiplayer are not part of the Offline package; Battle Royale safe-zone behavior remains a local gameplay system.')],
}
for name,pairs in doc_changes.items():
    path=root/name
    if not path.exists():
        continue
    content=path.read_text(encoding='utf-8')
    for old,new in pairs:
        if old not in content:
            raise SystemExit(f'Expected documentation text missing in {name}: {old[:90]}')
        content=content.replace(old,new,1)
    path.write_text(content,encoding='utf-8')

# Copy reviewed project documentation, validator and this reproducible patcher into the source root.
for name in ['README.md','validate_project.py','OFFLINE_PAIRING_REMOVAL.md','ASSET_INVENTORY.md','ANDROID_GAMEPLAY_QA_MATRIX.md']:
    source=Path(__file__).with_name(name); destination=root/name
    if source.resolve()!=destination.resolve(): shutil.copy2(source,destination)
source=Path(__file__); destination=root/'apply_offline_pairing_removal.py'
if source.resolve()!=destination.resolve(): shutil.copy2(source,destination)
print('Offline pairing removal source edits completed.')
