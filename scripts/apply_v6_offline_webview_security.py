#!/usr/bin/env python3
"""Harden the offline WebView origin, subresource policy, CSP, and browser capabilities."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
activities = list(root.rglob("app/src/main/java/com/example/battlezone/MainActivity.kt"))
if len(htmls) != 1 or len(activities) != 1:
    raise SystemExit(f"Expected one index.html and MainActivity.kt, found {len(htmls)} and {len(activities)}")
html, activity = htmls[0], activities[0]
source = html.read_text(encoding="utf-8")
kotlin = activity.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_V1"
if marker in source and marker in kotlin:
    print("BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_ALREADY_APPLIED")
    raise SystemExit(0)
if "BATTLEZONE_V6_ADAPTIVE_GRAPHICS_V1" not in source:
    raise SystemExit("Adaptive graphics patch must run before security hardening")

csp = """<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob: data:; connect-src 'self'; font-src 'self' data:; object-src 'none'; base-uri 'self'; frame-src 'none'; form-action 'none'">"""
if source.count("<head>") != 1:
    raise SystemExit("HTML head anchor is not unique")
source = source.replace("<head>", "<head>\n" + csp, 1)

def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)

kotlin = once(
    kotlin,
    "import android.app.Activity\n",
    "import android.app.Activity\nimport android.net.Uri\nimport java.io.ByteArrayInputStream\n",
    "security imports",
)
helper_anchor = '    @SuppressLint("SetJavaScriptEnabled")'
helper = """    private fun isTrustedAssetUri(uri: Uri): Boolean {
        return uri.scheme == "https" &&
            uri.host == "appassets.androidplatform.net" &&
            (uri.port == -1 || uri.port == 443) &&
            uri.userInfo == null &&
            (uri.path?.let { path ->
                path.startsWith("/assets/") && path.split('/').none { it == "." || it == ".." }
            } == true)
    }

    private fun blockedResponse(status: Int, reason: String): WebResourceResponse {
        return WebResourceResponse(
            "text/plain",
            "UTF-8",
            status,
            reason,
            mapOf("Cache-Control" to "no-store", "X-Content-Type-Options" to "nosniff"),
            ByteArrayInputStream(ByteArray(0))
        )
    }

"""
kotlin = once(kotlin, helper_anchor, helper + helper_anchor, "trusted-origin helpers")

kotlin = once(
    kotlin,
    """            settings.allowContentAccess = false
            settings.mediaPlaybackRequiresUserGesture = false""",
    """            settings.allowContentAccess = false
            settings.allowFileAccessFromFileURLs = false
            settings.allowUniversalAccessFromFileURLs = false
            settings.blockNetworkLoads = true
            settings.databaseEnabled = false
            settings.setGeolocationEnabled(false)
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            if (android.os.Build.VERSION.SDK_INT >= 26) {
                settings.safeBrowsingEnabled = true
            }
            settings.mediaPlaybackRequiresUserGesture = false""",
    "restricted WebView capabilities",
)

kotlin = once(
    kotlin,
    """            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(message: ConsoleMessage): Boolean {""",
    """            webChromeClient = object : WebChromeClient() {
                override fun onPermissionRequest(request: android.webkit.PermissionRequest) {
                    request.deny()
                }

                override fun onConsoleMessage(message: ConsoleMessage): Boolean {""",
    "deny WebView runtime permissions",
)

kotlin = once(
    kotlin,
    "val response = assetLoader.shouldInterceptRequest(request.url) ?: return null",
    """if (!isTrustedAssetUri(request.url)) return blockedResponse(403, "Blocked")
                    val response = assetLoader.shouldInterceptRequest(request.url)
                        ?: return blockedResponse(404, "Not Found")""",
    "deny non-local subresource requests",
)

kotlin = once(
    kotlin,
    'request.url.host != "appassets.androidplatform.net"',
    "!isTrustedAssetUri(request.url)",
    "restrict top-level navigation",
)

kotlin = kotlin.replace("class MainActivity : Activity() {\n", "class MainActivity : Activity() {\n    // " + marker + "\n", 1)
source = source.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
html.write_text(source, encoding="utf-8")
activity.write_text(kotlin, encoding="utf-8")
print("BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_APPLIED", html, activity)
