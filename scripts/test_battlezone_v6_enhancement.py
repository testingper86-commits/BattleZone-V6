#!/usr/bin/env python3
"""Build-blocking regression checks for the BattleZone V6 command-deck patch."""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html_files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(html_files) != 1:
    raise SystemExit(f"Expected one game index.html, found {len(html_files)}")
html_path = html_files[0]
html = html_path.read_text(encoding="utf-8")
asset = html_path.parent
css = (asset / "css/v6-command-deck.css").read_text(encoding="utf-8")
js_path = asset / "js/v6-command-deck.js"
js = js_path.read_text(encoding="utf-8")
checks = {
    "V6 command-deck patch marker": "BATTLEZONE_V6_COMMAND_DECK_V1" in html,
    "command hero markup": 'id="bz-v6-hero"' in html and 'id="bz-v6-hero-meta"' in html,
    "command-deck stylesheet linked": './css/v6-command-deck.css' in html,
    "command-deck behavior linked": './js/v6-command-deck.js' in html,
    "lobby preview capped to 20 fps": "n-lastLobbyRender>=50" in html,
    "lobby WebGL context released after deploy": "lr.forceContextLoss();cv.remove()" in html,
    "squad target acquisition throttled": "u.squadScanT=.16" in html and "u.squadTargetObj" in html and "u.squadScanT<=0||(en&&(!en.userData.alive" in html,
    "squad roles use differentiated target priorities": "role==='support'?d+Math.min(40,threat)*.3:role==='flank'?d-Math.min(25,threat)*.12" in html,
    "squad line-of-sight deferred to fire cooldown": "if(u.cd<=0){const clear=bd<88&&hasClearShot" in html,
    "existing game controls retained": all(f'id="{x}"' in html for x in ("sqd", "matchmode", "dif", "maps", "go2", "lb-nav")),
    "responsive landscape layout": "max-width:760px) and (orientation:landscape)" in css,
    "responsive portrait layout": "max-width:560px) and (orientation:portrait)" in css,
    "reduced motion supported": "prefers-reduced-motion:reduce" in css,
    "dynamic mode and map status": "MutationObserver(sync)" in js and "selected?.textContent" in js,
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL") + "  " + name)
if not all(checks.values()):
    raise SystemExit("BattleZone V6 enhancement regression checks failed")
node = subprocess.run(["node", "--check", str(js_path)], capture_output=True, text=True)
if node.returncode:
    print(node.stdout)
    print(node.stderr, file=sys.stderr)
    raise SystemExit("V6 command-deck JavaScript syntax check failed")
print("PASS  V6 command-deck JavaScript syntax")
