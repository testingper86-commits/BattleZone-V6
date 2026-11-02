#!/usr/bin/env python3
"""Static validation for the Battle Zone V6 Offline Android/WebView source.

Checks game modes, local assets, absence of device-pairing/network code, and
JavaScript syntax. Requires Node.js for complete syntax checks. This is not a
substitute for an Android Gradle build or physical-device test.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
HTML = ROOT / 'app/src/main/assets/www/index.html'
MANIFEST = ROOT / 'app/src/main/AndroidManifest.xml'
MAIN_ACTIVITY = ROOT / 'app/src/main/java/com/example/battlezone/MainActivity.kt'
ASSET_DIR = ROOT / 'app/src/main/assets/www'
if not HTML.is_file() or not MANIFEST.is_file() or not MAIN_ACTIVITY.is_file():
    raise SystemExit('Required Android/game source files are missing.')

source = HTML.read_text(encoding='utf-8')
manifest = MANIFEST.read_text(encoding='utf-8')
activity = MAIN_ACTIVITY.read_text(encoding='utf-8')
models = (ASSET_DIR / 'js/models.js').read_text(encoding='utf-8')
gradle = (ROOT / 'app/build.gradle.kts').read_text(encoding='utf-8')
checks = {
    'Battle Royale mode': "BZ_MODE==='BR'" in source,
    'Team Deathmatch mode': "BZ_MODE==='TDM'" in source,
    'Free-for-All mode': "BZ_MODE==='FFA'" in source,
    'mode selector UI': 'id="matchmode"' in source,
    'texture integration': 'const BZMaterial=' in source,
    'local Three.js script reference': 'src="./libs/three.min.js"' in source,
    'Three.js runtime is bundled or fetched by Gradle': ((ASSET_DIR / 'libs/three.min.js').is_file() or 'downloadThreeJs' in gradle),
    '27 texture maps': len(list((ASSET_DIR / 'textures').glob('*.png'))) >= 27,
    '5 effect sprites': len(list((ASSET_DIR / 'sprites').glob('*.png'))) >= 5,
    'expanded 900x900 map ground': 'PlaneGeometry(900,900)' in source,
    'five-phase safe zone': all(token in source for token in ['radius:.70', 'radius:.50', 'radius:.32', 'radius:.16', 'radius:.05']),
    'zone easing and final phase': 'zShrinkElapsed' in source and 'zFinished' in source,
    'expanded minimap scale': 'const s=96/450' in source,
    'playable map boundary': 'const MAP_LIMIT=438' in source and 'clampWorld(P.x,P.z' in source,
    'named map landmarks': all(name in source for name in ['MILITARY BASE', 'OLD TOWN', 'INDUSTRIAL YARD', 'FOREST CAMP', 'CENTRAL OUTPOST']),
    'nearest landmark HUD': 'nearPoi.name' in source,
    'offline bot population retained': 'const bzNB=29,bzSP=300' in source,
    'TDM AI teammates retained': "const bzAllyCount=BZ_MODE==='TDM'?3" in source,
    'pairing and multiplayer UI removed': not any(token in source for token in ['LOCAL MULTIPLAYER', 'Nearby Wi-Fi Rooms', 'bz-net-open', 'bz-net-panel', 'Wi-Fi rooms']),
    'network bridge hooks removed from game': not any(token in source for token in ['BattleNetwork', 'BattleZoneMultiplayer', 'bzRemotePlayers', 'bzNetActive', 'bzNetShoot', 'bzNetTargets']),
    'remote avatar relay removed from model loader': not any(token in models for token in ['bzRemotePlayers', 'Remote LAN player', 'function attach(']),
    'network bridge removed from Android activity': not any(token in activity for token in ['GameNetworkBridge', 'BattleNetwork', 'WifiManager', 'ServerSocket', 'DatagramSocket', 'Socket(', 'java.net']),
    'network permissions removed': not any(token in manifest for token in ['android.permission.INTERNET', 'ACCESS_NETWORK_STATE', 'ACCESS_WIFI_STATE', 'CHANGE_WIFI_MULTICAST_STATE']),
    'network runtime source removed': not (ASSET_DIR / 'js/netplay.js').exists() and './js/netplay.js' not in source,
    'network protocol docs retired': not (ROOT / 'NETWORK_PROTOCOL.md').exists() and not (ROOT / 'MULTIPLAYER_IMPLEMENTATION_STATUS.md').exists(),
}
for label, passed in checks.items():
    print(('PASS' if passed else 'MISSING/NEEDS ACTION') + '  ' + label)

node = shutil.which('node')
if not node:
    print('SKIP  JavaScript syntax (Node.js not installed)')
else:
    inline_blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', source, re.S | re.I)
    script_files = sorted((ASSET_DIR / 'js').rglob('*.js'))
    failures = []
    for index, script in enumerate(inline_blocks):
        if not script.strip():
            continue
        temp = ROOT / f'.validate-inline-{index}.js'
        try:
            temp.write_text(script, encoding='utf-8')
            result = subprocess.run([node, '--check', str(temp)], capture_output=True, text=True)
            if result.returncode:
                failures.append((f'{HTML.name} inline block {index}', result.stderr))
        finally:
            temp.unlink(missing_ok=True)
    for path in script_files:
        result = subprocess.run([node, '--check', str(path)], capture_output=True, text=True)
        if result.returncode:
            failures.append((str(path.relative_to(ROOT)), result.stderr))
    if failures:
        for name, error in failures:
            print(f'FAIL  JavaScript syntax: {name}\n{error}')
        raise SystemExit(1)
    print(f'PASS  JavaScript syntax ({len(script_files)} source files and {sum(bool(x.strip()) for x in inline_blocks)} inline blocks)')

print('\nStatic checks complete. Android build and physical-device behavior still require separate verification.')
if not all(checks.values()):
    sys.exit(1)
