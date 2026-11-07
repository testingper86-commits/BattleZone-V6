#!/usr/bin/env python3
"""Add a safe same-origin retry page for Android WebView main-document failures."""
from pathlib import Path
import sys
MARKER="BATTLEZONE_V6_WEBVIEW_RECOVERY_V1"
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/java/com/example/battlezone/MainActivity.kt"))
if len(files)!=1: raise SystemExit(f"Expected exactly one MainActivity.kt, found {len(files)}")
path=files[0]; source=path.read_text(encoding="utf-8")
if MARKER in source:
    if "Retry loading game" not in source or "onReceivedHttpError" not in source: raise SystemExit("WebView recovery marker exists but implementation is incomplete")
    print(MARKER+" already applied"); raise SystemExit(0)
helper_anchor='    @SuppressLint("SetJavaScriptEnabled")'
if source.count(helper_anchor)!=1: raise SystemExit("Could not find unique MainActivity helper insertion point")
helper=r"""    // BATTLEZONE_V6_WEBVIEW_RECOVERY_V1
    private fun showLoadFailure(view: WebView, message: String) {
        val safeMessage = message
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#39;")
        val retryUrl = "https://appassets.androidplatform.net/assets/www/index.html"
        val html = listOf(
            "<!doctype html>",
            "<html lang=\"en\"><head><meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
            "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; form-action 'none'; frame-src 'none'\">",
            "<title>Battle Zone unavailable</title>",
            "<style>body{margin:0;background:#07111d;color:#edf5fb;font:16px system-ui;padding:28px}main{max-width:520px;margin:12vh auto}h1{font-size:25px}.retry{display:inline-block;margin-top:18px;padding:14px 22px;background:#1d6fbd;color:white;text-decoration:none;border-radius:10px;font-weight:700}.hint{color:#a8b9c8;line-height:1.5}</style>",
            "</head><body><main><h1>Battle Zone could not load</h1>",
            "<p>$safeMessage</p>",
            "<a class=\"retry\" href=\"$retryUrl\">Retry loading game</a>",
            "<p class=\"hint\">The game is stored locally. Retry does not require an internet connection. If this repeats, send the BattleZoneWeb Logcat entries to the developer.</p>",
            "</main></body></html>"
        ).joinToString("\n")
        view.loadDataWithBaseURL("https://appassets.androidplatform.net/", html, "text/html", "UTF-8", null)
    }

"""
source=source.replace(helper_anchor,helper+helper_anchor,1)
start_token="                override fun onReceivedError("
end_token="                override fun onRenderProcessGone("
if source.count(start_token)!=1 or source.count(end_token)!=1: raise SystemExit("Could not find unique WebView error callback range")
start=source.index(start_token); end=source.index(end_token,start)
callbacks=r"""                override fun onReceivedError(
                    view: WebView,
                    request: WebResourceRequest,
                    error: android.webkit.WebResourceError
                ) {
                    android.util.Log.e("BattleZoneWeb", "Resource load failed (mainFrame=" + request.isForMainFrame + ", code=" + error.errorCode + "): " + request.url + " " + error.description)
                    if (request.isForMainFrame) showLoadFailure(view, error.description.toString())
                }

                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                    !isTrustedAssetUri(request.url)

                override fun onReceivedHttpError(
                    view: WebView,
                    request: WebResourceRequest,
                    errorResponse: WebResourceResponse
                ) {
                    android.util.Log.w("BattleZoneWeb", "HTTP ${errorResponse.statusCode} for ${request.url}")
                    if (request.isForMainFrame && errorResponse.statusCode >= 400) {
                        showLoadFailure(view, "Local game document returned HTTP ${errorResponse.statusCode}.")
                    }
                }

"""
source=source[:start]+callbacks+source[end:]
if source.count(MARKER)!=1 or "Retry loading game" not in source: raise SystemExit("WebView recovery insertion failed")
path.write_text(source,encoding="utf-8")
print(MARKER+" applied",path)
