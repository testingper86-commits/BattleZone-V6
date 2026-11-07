#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = (root / "app/src/main/assets/www/index.html").read_text(encoding="utf-8")
kotlin = (root / "app/src/main/java/com/example/battlezone/MainActivity.kt").read_text(encoding="utf-8")
policy = (root / "app/src/main/java/com/example/battlezone/OfflineAssetPolicy.kt").read_text(encoding="utf-8")
manifest = (root / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
assert "BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_V1" in html and "BATTLEZONE_V6_OFFLINE_WEBVIEW_SECURITY_V1" in kotlin
match = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', html)
assert match, "CSP meta policy missing"
csp = match.group(1)
for directive in ("default-src 'self'", "script-src 'self' 'unsafe-inline'", "style-src 'self' 'unsafe-inline'", "img-src 'self' data: blob:", "connect-src 'self'", "object-src 'none'", "base-uri 'self'", "frame-src 'none'", "form-action 'none'"):
    assert directive in csp, f"CSP directive missing: {directive}"
assert "unsafe-eval" not in csp
for token in ("private fun isTrustedAssetUri", "OfflineAssetPolicy.isTrustedAssetUri"):
    assert token in kotlin, f"WebView hardening missing: {token}"
assert "URLDecoder.decode" in policy and "decoded.split('/')" in policy
for token in (
    "settings.allowFileAccess = false", "settings.allowContentAccess = false",
    "settings.blockNetworkLoads = true", "settings.databaseEnabled = false",
    "settings.safeBrowsingEnabled = true", "request.deny()",
    'blockedResponse(403, "Blocked")', 'blockedResponse(404, "Not Found")',
    "!isTrustedAssetUri(request.url)",
):
    assert token in kotlin, f"WebView hardening missing: {token}"

assert '!isTrustedAssetUri(request.url)"' not in kotlin, "malformed navigation expression found"
assert "!isTrustedAssetUri(request.url)" in kotlin
assert "addJavascriptInterface" not in kotlin
assert "android.permission.INTERNET" not in manifest
assert 'android:usesCleartextTraffic="false"' in manifest
assert 'android:allowBackup="false"' in manifest
assert not re.search(r'<script[^>]+src="https?://', html, re.I), "remote script source found"
assert "eval(" not in html and "document.write(" not in html
print("OFFLINE_WEBVIEW_SECURITY_STATIC_CHECKS_OK")
