#!/usr/bin/env python3
"""Apply the final viewport-aware Battle Zone V6 lobby layout."""
from pathlib import Path
import shutil, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
htmls=list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls)!=1: raise SystemExit(f"Expected exactly one game index.html, found {len(htmls)}")
html=htmls[0]; source=html.read_text(encoding="utf-8")
marker="BATTLEZONE_V6_LOBBY_ALIGNMENT_V1"
css=Path(__file__).with_name("v6-lobby-alignment.css")
if not css.is_file(): raise SystemExit(f"Required lobby stylesheet missing: {css}")
if marker not in source:
    if source.count("</head>")!=1: raise SystemExit("Expected exactly one </head> insertion point")
    link='<link rel="stylesheet" href="./css/v6-lobby-alignment.css">\n'
    source=source.replace("</head>",link+"<!-- "+marker+" -->\n</head>",1)
    html.write_text(source,encoding="utf-8")
asset=html.parent/"css";asset.mkdir(parents=True,exist_ok=True)
target=asset/css.name
shutil.copy2(css,target)
check=html.read_text(encoding="utf-8")
if marker not in check or "./css/v6-lobby-alignment.css" not in check: raise SystemExit("Lobby alignment stylesheet integration failed")
print("BATTLEZONE_V6_LOBBY_ALIGNMENT_APPLIED",html,target)
