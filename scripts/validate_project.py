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
from html.parser import HTMLParser
from urllib.parse import urlsplit

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
    'Kenney character model and four skins': all((ASSET_DIR / p).is_file() for p in [
        'models/characters/kenney/Model/characterMedium.fbx',
        'models/characters/kenney/Skins/skaterMaleA.png',
        'models/characters/kenney/Skins/criminalMaleA.png',
        'models/characters/kenney/Skins/cyborgFemaleA.png',
        'models/characters/kenney/Skins/skaterFemaleA.png']),
    'Kenney idle/run/jump clips': all((ASSET_DIR / p).is_file() for p in [
        'models/characters/kenney/Animations/idle.fbx',
        'models/characters/kenney/Animations/run.fbx',
        'models/characters/kenney/Animations/jump.fbx']),
    'Three.js r128 and helper loaders pinned in Gradle': all(token in gradle for token in [
        'downloadThreeJs', 'downloadOptionalLibs', 'three@0.128.0', 'GLTFLoader.js', 'FBXLoader.js', 'SkeletonUtils.js', 'fflate.min.js']),
    'asset library README matches active model loader': 'FBXLoader' in (ASSET_DIR / 'libs/README.txt').read_text(encoding='utf-8') and 'js/models.js' in (ASSET_DIR / 'libs/README.txt').read_text(encoding='utf-8') and 'all characters are built procedurally' not in (ASSET_DIR / 'libs/README.txt').read_text(encoding='utf-8'),
    'underwater health damage': 'P.waterDamage' in source and 'dmg(7)' in source,
    'vehicle shooting and destruction': 'vehicleRoot' in source and '...veh],true' in source and "msg('Vehicle destroyed!')" in source,
    'new-install squad default': "SQ=[0,1,3][+(sg('bzs')??2)]" in source,
    'ally medical support': 'u.healT' in source and 'P.hp<70' in source,
    'touch cancellation and focus recovery': 'lostpointercapture' in source and 'clearGameplayInputs' in source,
    'frame pacing after stalls': 'Math.min((n-last)/1000,.1)' in source,
    'mobile GPU budget': 'Math.min(devicePixelRatio,1.25)' in source and 'sun.shadow.mapSize.set(512,512)' in source,
    'gameplay quality V2 patch marker': 'BATTLE_ZONE_GAMEPLAY_QUALITY_V2' in source,
    'hot-loop actor concatenations removed': 'bots.concat(al)' not in source and 'bots.concat' not in models,
    'allocation-free actor iteration': 'function forEachActor(fn)' in source and 'const eachActor=fn=>' in models,
    'HUD and minimap throttled': 'hudRefresh=.12' in source and 'drawMM()' in source,
    'minimap water and POI overlays': all(token in source for token in ['poiColors','lake.r*s','rv.w*s','MAP_POIS.forEach']),
    'procedural jump/shoot/reload poses': all(token in source for token in ['airPose','parachutePose','actionT','reloadW','fireW']),
    'weapon retained during airborne movement': 'pm.hand.visible=true' in source,
    'rigged jump/freefall animation': 'P.air===1||P.air===3' in models,
    'enemy and ally firing animations': "b.sc.action='shoot'" in source and "a.sc.action='shoot'" in source,
    'transport bot index reuse': 'botIndex%5' in source and 'bots.indexOf(b)' not in source,
}

# Resolve every static local resource declared by HTML tags and CSS url() calls.
# Ignore remote/data/blob/hash URLs and template expressions that are generated at runtime.
class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for attr in ('src', 'href', 'poster'):
            if attrs.get(attr):
                self.refs.append((f'<{tag} {attr}>', attrs[attr]))

parser = ResourceParser()
parser.feed(source)
resource_refs = list(parser.refs)
for css_file in ASSET_DIR.rglob('*.css'):
    css_text = css_file.read_text(encoding='utf-8', errors='ignore')
    resource_refs.extend((str(css_file.relative_to(ASSET_DIR)), m.group(1).strip().strip('\"\''))
                         for m in re.finditer(r'url\((?:\s*[\"\']?)(.*?)(?:[\"\']?\s*)\)', css_text, re.I))
missing_resources = []
checked_resources = set()
for origin, ref in resource_refs:
    ref = ref.strip()
    if not ref or ref.startswith(('data:', 'blob:', '#', 'https:', 'http:', '//', 'javascript:', 'mailto:', 'tel:')):
        continue
    path = urlsplit(ref).path
    normalized_path = path[2:] if path.startswith('./') else path
    if not path or any(token in path for token in ('${', '{', '*', '%')):
        continue
    target = (ASSET_DIR / path.lstrip('/')).resolve()
    if not target.is_relative_to(ASSET_DIR.resolve()):
        missing_resources.append((origin, ref, 'path escapes asset root'))
    elif target.is_file():
        checked_resources.add((origin, ref))
    elif normalized_path.startswith('libs/') and Path(path).name in {'three.min.js', 'GLTFLoader.js', 'FBXLoader.js', 'SkeletonUtils.js', 'fflate.min.js'} and 'downloadThreeJs' in gradle and 'downloadOptionalLibs' in gradle:
        # These pinned runtime libraries are intentionally fetched by Gradle before preBuild.
        checked_resources.add((origin, ref))
    else:
        missing_resources.append((origin, ref, str(target.relative_to(ASSET_DIR.resolve()))))
checks['static HTML/CSS resource paths resolve'] = not missing_resources

for label, passed in checks.items():
    print(('PASS' if passed else 'MISSING/NEEDS ACTION') + '  ' + label)
if missing_resources:
    for origin, ref, target in missing_resources:
        print(f'FAIL  missing local resource from {origin}: {ref} -> {target}')
else:
    print(f'PASS  static local resource paths ({len(checked_resources)} references)')

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
