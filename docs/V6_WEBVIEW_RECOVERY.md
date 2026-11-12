# BattleZone V6 Android WebView recovery

The `BATTLEZONE_V6_WEBVIEW_RECOVERY_V1` patch adds a native recovery page when the local game document fails to load. Main-frame network errors and main-frame HTTP errors (status 400+) now show a same-origin **Retry loading game** link instead of telling the player to close and reopen the app.

The retry target is the packaged `https://appassets.androidplatform.net/assets/www/index.html` asset. It continues through the existing trusted-asset URL policy and `WebViewAssetLoader`; the error page has a restrictive CSP and no JavaScript bridge. Subresource failures remain logged without replacing the whole game view.

WebView debugging remains conditional on `ApplicationInfo.FLAG_DEBUGGABLE`, so it is enabled only in debuggable builds. `settings.blockNetworkLoads = true`, mixed-content blocking, and external URL rejection remain unchanged.

`test_v6_webview_recovery.py` checks these conditions. CI Kotlin compilation is the compile-time gate. Physical-device verification of the retry interaction and renderer-crash recovery is still required.
