#!/usr/bin/env python3
"""Fail-closed checks that transformed source and APKs contain no LAN/network runtime."""
from __future__ import annotations
import argparse, re, sys, zipfile
from pathlib import Path

FORBIDDEN = (
    "GameNetworkBridge", "BattleNetwork", "BattleZoneMultiplayer", "bzRemotePlayers",
    "bzNetActive", "bzNetShoot", "bzNetTargets", "WifiManager", "ServerSocket",
    "DatagramSocket", "ACCESS_NETWORK_STATE", "ACCESS_WIFI_STATE",
    "CHANGE_WIFI_MULTICAST_STATE", "android.permission.INTERNET", "java.net.Socket",
)
DEX_FORBIDDEN = (
    "GameNetworkBridge", "BattleNetwork", "BattleZoneMultiplayer", "bzRemotePlayers",
    "bzNetActive", "bzNetShoot", "bzNetTargets",
)
NETWORK_PERMISSIONS = (
    "android.permission.INTERNET", "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.ACCESS_WIFI_STATE", "android.permission.CHANGE_WIFI_MULTICAST_STATE",
)

class IntegrityError(Exception):
    pass

def _check_runtime_text(label: str, text: str, failures: list[str]) -> None:
    for token in FORBIDDEN:
        if token in text:
            failures.append(f"{label}: forbidden runtime marker {token}")
    if re.search(r'<script\b[^>]*\bsrc\s*=\s*["\']https?://', text, re.I):
        failures.append(f"{label}: remote script source")

def verify_source(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / "app/src/main/AndroidManifest.xml"
    activity_path = root / "app/src/main/java/com/example/battlezone/MainActivity.kt"
    html_path = root / "app/src/main/assets/www/index.html"
    models_path = root / "app/src/main/assets/www/js/models.js"
    required = (manifest_path, activity_path, html_path, models_path)
    for path in required:
        if not path.is_file(): failures.append(f"missing required source: {path.relative_to(root)}")
    if failures: return failures
    manifest = manifest_path.read_text(encoding="utf-8")
    activity = activity_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    models = models_path.read_text(encoding="utf-8")
    for permission in NETWORK_PERMISSIONS:
        if permission in manifest: failures.append(f"Android manifest retains network permission: {permission}")
    java_root = root / "app/src/main/java"
    for path in sorted(p for p in java_root.rglob("*") if p.is_file() and p.suffix in {".kt", ".java"}):
        _check_runtime_text(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8", errors="ignore"), failures)
    assets = root / "app/src/main/assets/www"
    for path in sorted(p for p in assets.rglob("*") if p.is_file() and p.suffix in {".js", ".html"}):
        _check_runtime_text(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8", errors="ignore"), failures)
    if "settings.blockNetworkLoads = true" not in activity:
        failures.append("WebView network loads are not explicitly blocked")
    if (assets / "js/netplay.js").exists(): failures.append("LAN runtime file remains: js/netplay.js")
    if "./js/netplay.js" in html or "netplay.js" in html: failures.append("game HTML still references netplay.js")
    if not re.search(r"connect-src\s+'self'", html): failures.append("offline CSP connect-src 'self' policy is missing")
    return failures

def verify_apk(apk: Path) -> list[str]:
    failures: list[str] = []
    if not apk.is_file(): return [f"APK does not exist: {apk}"]
    try:
        with zipfile.ZipFile(apk) as archive:
            names = archive.namelist()
            if not any(name == "AndroidManifest.xml" for name in names): failures.append("APK has no AndroidManifest.xml")
            if any(name.endswith("assets/www/js/netplay.js") for name in names): failures.append("APK contains js/netplay.js")
            raw_manifest = archive.read("AndroidManifest.xml") if "AndroidManifest.xml" in names else b""
            for permission in NETWORK_PERMISSIONS:
                encoded = permission.encode("utf-8")
                encoded16 = permission.encode("utf-16le")
                if encoded in raw_manifest or encoded16 in raw_manifest:
                    failures.append(f"APK manifest retains network permission: {permission}")
            for name in names:
                if name.endswith((".dex", ".js", ".html", ".xml")):
                    data = archive.read(name)
                    text = data.decode("utf-8", errors="ignore")
                    markers = DEX_FORBIDDEN if name.endswith(".dex") else FORBIDDEN
                    for token in markers:
                        if token in text:
                            failures.append(f"APK {name}: forbidden runtime marker {token}")
                    if name.endswith((".html", ".js")) and re.search(r'<script\b[^>]*\bsrc\s*=\s*["\']https?://', text, re.I):
                        failures.append(f"APK {name}: remote script source")
    except (OSError, zipfile.BadZipFile) as error:
        failures.append(f"cannot inspect APK archive: {error}")
    return failures

def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path)
    group.add_argument("--apk", type=Path)
    args = parser.parse_args()
    failures = verify_source(args.source.resolve()) if args.source else verify_apk(args.apk.resolve())
    if failures:
        for failure in failures: print("FAIL " + failure, file=sys.stderr)
        raise SystemExit(1)
    print("OFFLINE_INTEGRITY_OK " + (str(args.source) if args.source else str(args.apk)))

if __name__ == "__main__":
    main()
