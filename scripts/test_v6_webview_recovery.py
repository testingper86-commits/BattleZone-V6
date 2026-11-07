#!/usr/bin/env python3
"""Regression checks for Android WebView failure recovery and release hardening."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/java/com/example/battlezone/MainActivity.kt"))
if len(files)!=1: raise SystemExit(f"Expected exactly one MainActivity.kt, found {len(files)}")
s=files[0].read_text(encoding="utf-8")
checks={
 "recovery marker": "BATTLEZONE_V6_WEBVIEW_RECOVERY_V1" in s,
 "retry points to local packaged game": 'href=\\\"$retryUrl\\\"' in s and 'https://appassets.androidplatform.net/assets/www/index.html' in s,
 "main-frame load errors show recovery UI": "if (request.isForMainFrame) showLoadFailure(view, error.description.toString())" in s,
 "main-frame HTTP errors show recovery UI": "request.isForMainFrame && errorResponse.statusCode >= 400" in s,
 "same-origin retry remains subject to offline URL policy": "!isTrustedAssetUri(request.url)" in s,
 "WebView network loads stay blocked": "settings.blockNetworkLoads = true" in s,
 "WebView inspection remains debug-build-only": s.count("WebView.setWebContentsDebuggingEnabled(true)")==1 and s.index("if ((applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0)") < s.index("WebView.setWebContentsDebuggingEnabled(true)"),
 "no JavaScript interface bridge": "addJavascriptInterface" not in s,
 "error page forbids external network loads": "default-src 'none'" in s and "connect-src 'self'" in s,
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("WebView recovery regression failed")
print("WEBVIEW_RECOVERY_TESTS_OK")
