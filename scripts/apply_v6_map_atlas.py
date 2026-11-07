#!/usr/bin/env python3
"""Install the offline topographic map atlas and route planner."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = list(root.rglob("app/src/main/assets/www/index.html"))
if len(paths) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(paths)}")
html = paths[0]
www = html.parent
script_source = Path(__file__).with_name("bz-map-atlas.js")
style_source = Path(__file__).with_name("bz-map-atlas.css")
if not script_source.is_file() or not style_source.is_file():
    raise SystemExit("Map Atlas source assets are missing from scripts/")
(www / "js").mkdir(parents=True, exist_ok=True)
(www / "css").mkdir(parents=True, exist_ok=True)
(www / "js" / "bz-map-atlas.js").write_bytes(script_source.read_bytes())
(www / "css" / "bz-map-atlas.css").write_bytes(style_source.read_bytes())
s = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_MAP_ATLAS_V1"
if marker not in s:
    heading = '<h2>Select deployment zone</h2>'
    if s.count(heading) != 1:
        raise SystemExit(f"Map selector heading expected once, found {s.count(heading)}")
    s = s.replace(heading, heading + '<button type="button" id="bzMapAtlasOpen" class="bzma-open" aria-haspopup="dialog">OPEN MAP ATLAS <span aria-hidden="true">↗</span></button>', 1)
    close_anchor = "\n}\n// WARROOM_MAP_SELECT_V1\n\nfunction settingsPage()"
    if s.count(close_anchor) != 1:
        raise SystemExit(f"Map selector close anchor expected once, found {s.count(close_anchor)}")
    s = s.replace(close_anchor, "\n const atlasButton=content.querySelector('#bzMapAtlasOpen');if(atlasButton)atlasButton.addEventListener('click',()=>window.BZMapAtlas&&window.BZMapAtlas.open());\n}\n// WARROOM_MAP_SELECT_V1\n\nfunction settingsPage()", 1)
    if s.count("</head>") != 1 or s.count("</html>") != 1:
        raise SystemExit("HTML head/document closing anchors are not unique")
    s = s.replace("</head>", '<link rel="stylesheet" href="./css/bz-map-atlas.css">\n</head>', 1)
    s = s.replace("</html>", '<script src="./js/bz-map-atlas.js"></script>\n<!-- BATTLEZONE_V6_MAP_ATLAS_V1 -->\n</html>', 1)
elif 'id="bzMapAtlasOpen"' not in s or './js/bz-map-atlas.js' not in s or './css/bz-map-atlas.css' not in s:
    raise SystemExit("Map Atlas marker exists but HTML integration is incomplete")
html.write_text(s, encoding="utf-8")
print("BATTLEZONE_V6_MAP_ATLAS_APPLIED", html)
