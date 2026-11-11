#!/usr/bin/env python3
"""Enforce a strict local-only WebView policy after all source generators."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
def unique(pattern):
    matches = list(root.rglob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {pattern}, found {len(matches)}")
    return matches[0]

html_path = unique("app/src/main/assets/www/index.html")
activity_path = unique("app/src/main/java/com/example/battlezone/MainActivity.kt")
policy_path = unique("app/src/main/java/com/example/battlezone/OfflineAssetPolicy.kt")
html = html_path.read_text(encoding="utf-8")
kotlin = activity_path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_V1"

csp = "default-src 'self' data: blob:; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob: data:; connect-src 'self'; font-src 'self' data:; object-src 'none'; base-uri 'self'; frame-src 'none'; form-action 'none'"
meta = '<meta http-equiv="Content-Security-Policy" content="' + csp + '">'
pattern = r'<meta\s+http-equiv="Content-Security-Policy"\s+content="[^"]*"\s*/?>'
found = re.findall(pattern, html, flags=re.I)
if len(found) != 1:
    raise SystemExit(f"Expected one CSP meta element, found {len(found)}")
html = re.sub(pattern, meta, html, count=1, flags=re.I)
if marker not in html:
    html = html.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
if html.count(marker) != 1:
    raise SystemExit("Offline HTML marker is duplicated")

if "import android.net.Uri" not in kotlin:
    kotlin = kotlin.replace("import android.app.Activity\n", "import android.app.Activity\nimport android.net.Uri\n", 1)
if "import java.io.ByteArrayInputStream" not in kotlin:
    kotlin = kotlin.replace("import android.webkit.WebViewClient\n", "import android.webkit.WebViewClient\nimport java.io.ByteArrayInputStream\n", 1)
class_anchor = "class MainActivity : Activity() {\n"
if class_anchor not in kotlin:
    raise SystemExit("MainActivity class anchor missing")
if marker not in kotlin:
    kotlin = kotlin.replace(class_anchor, class_anchor + "    // " + marker + "\n", 1)

helper = '''    private fun isTrustedAssetUri(uri: Uri): Boolean {
        return OfflineAssetPolicy.isTrustedAssetUri(uri.scheme, uri.host, uri.port, uri.userInfo, uri.path)
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

'''
if "private fun isTrustedAssetUri(uri: Uri)" not in kotlin:
    anchor = '    @SuppressLint("SetJavaScriptEnabled")'
    if kotlin.count(anchor) != 1:
        raise SystemExit("Unique MainActivity helper anchor missing")
    kotlin = kotlin.replace(anchor, helper + anchor, 1)

settings_anchor = "            allowContentAccess = false\n"
if "allowContentAccess = false" not in kotlin:
    settings_anchor = "            settings.allowContentAccess = false\n"
settings_additions = """            allowFileAccessFromFileURLs = false
            allowUniversalAccessFromFileURLs = false
            blockNetworkLoads = true
            databaseEnabled = false
            setGeolocationEnabled(false)
            if (android.os.Build.VERSION.SDK_INT >= 26) {
                safeBrowsingEnabled = true
            }
"""
if "allowFileAccessFromFileURLs = false" not in kotlin:
    if kotlin.count(settings_anchor) != 1:
        raise SystemExit("Unique WebView content-access setting anchor missing")
    kotlin = kotlin.replace(settings_anchor, settings_anchor + settings_additions, 1)

permission_handler = '''                override fun onPermissionRequest(request: android.webkit.PermissionRequest) {
                    request.deny()
                }

'''
chrome_match = re.search(r'(?m)^(?P<indent>\s*)(?:webView\.)?webChromeClient = object : WebChromeClient\(\) \{\n', kotlin)
if "override fun onPermissionRequest" not in kotlin:
    if not chrome_match:
        raise SystemExit("Unique WebChromeClient anchor missing")
    indent = chrome_match.group("indent")
    insertion = indent + "    override fun onPermissionRequest(request: android.webkit.PermissionRequest) {\n" + indent + "        request.deny()\n" + indent + "    }\n\n"
    kotlin = kotlin[:chrome_match.end()] + insertion + kotlin[chrome_match.end():]

# Replace one complete Kotlin method using balanced braces, preserving all neighboring callbacks.
def replace_method(source, signature, replacement):
    if source.count(signature) != 1:
        raise SystemExit(f"Expected one Kotlin method signature: {signature}")
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    in_string = False
    escaped = False
    end = None
    for index in range(opening, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise SystemExit(f"Unclosed Kotlin method: {signature}")
    return source[:start] + replacement + source[end:]

intercept_signature = "override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse?"
intercept_method = '''override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                if (!isTrustedAssetUri(request.url)) return blockedResponse(403, "Blocked")
                return assetLoader.shouldInterceptRequest(request.url) ?: blockedResponse(404, "Not Found")
            }'''
kotlin = replace_method(kotlin, intercept_signature, intercept_method)

navigation_signature = "override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean"
navigation_method = '''override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                return !isTrustedAssetUri(request.url) || request.url.path?.startsWith("/assets/www/") != true
            }'''
kotlin = replace_method(kotlin, navigation_signature, navigation_method)

policy = policy_path.read_text(encoding="utf-8")
for token in ("URLDecoder.decode", "decoded.split('/')", "port != -1 && port != 443"):
    if token not in policy:
        raise SystemExit("OfflineAssetPolicy is missing required URI validation: " + token)
for token in ("private fun isTrustedAssetUri(uri: Uri)", "OfflineAssetPolicy.isTrustedAssetUri", "allowFileAccess = false", "allowContentAccess = false", "blockNetworkLoads = true", "databaseEnabled = false", "safeBrowsingEnabled = true", "request.deny()", 'blockedResponse(403, "Blocked")', 'blockedResponse(404, "Not Found")', "!isTrustedAssetUri(request.url)"):
    if token not in kotlin:
        raise SystemExit("MainActivity is missing offline WebView protection: " + token)

html_path.write_text(html, encoding="utf-8")
activity_path.write_text(kotlin, encoding="utf-8")
print("BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_ENFORCED", html_path, activity_path)
