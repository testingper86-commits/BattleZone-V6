#!/usr/bin/env python3
"""Permanently repair the V6 InstancedMesh crash, HUD lifecycle and operator preview scale."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(htmls)}")
html = htmls[0]
s = html.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_PERMANENT_RUNTIME_GRAPHICS_REPAIR_V1"
if marker in s:
    print("BATTLEZONE_V6_PERMANENT_RUNTIME_GRAPHICS_REPAIR_ALREADY_APPLIED")
else:
    def replace_once(source, old, new, label):
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
        return source.replace(old, new, 1)

    # Three.js in this package has no InstancedMesh.computeBoundingSphere().
    # Compute base geometry bounds where supported, and disable instance frustum
    # culling when the installed Three.js version cannot calculate instance bounds.
    old_bounds = "L.computeBoundingSphere();T.computeBoundingSphere();L.frustumCulled=true;T.frustumCulled=true;"
    new_bounds = ("const bzPrepareInstanceBounds=mesh=>{if(mesh.geometry&&typeof mesh.geometry.computeBoundingSphere==='function')mesh.geometry.computeBoundingSphere();"
                  "if(typeof mesh.computeBoundingSphere==='function'){mesh.computeBoundingSphere();mesh.frustumCulled=true}else mesh.frustumCulled=false};"
                  "bzPrepareInstanceBounds(L);bzPrepareInstanceBounds(T);")
    s = replace_once(s, old_bounds, new_bounds, "InstancedMesh bounds compatibility")

    # The HUD can be rebuilt/hidden during lobby-to-match transitions. Never let a
    # missing DOM node terminate the simulation loop; validate all required nodes
    # and the selected weapon before writing any HUD state.
    old_hud = "function hudUpdate(){const w=W[P.w],hp=Math.max(0,Math.ceil(P.hp));"
    new_hud = ("function hudUpdate(){const w=W[P.w];if(!w||!Array.isArray(P.own))return;"
               "const bzHudRequired=['ht','hpf','arm','wslots','wic','wnm','am','thrn','gswn'].map(id=>$(id));"
               "if(bzHudRequired.some(node=>!node)){if(window.__bzNote&&!window.__bzHudMissingReported){window.__bzHudMissingReported=true;window.__bzNote('HUD update skipped: required HUD node is unavailable')}return;}"
               "const hp=Math.max(0,Math.ceil(P.hp));")
    s = replace_once(s, old_hud, new_hud, "HUD lifecycle guard")

    # The operator preview uses the same model rig as gameplay. Increase only the
    # lobby preview instance, leaving in-match actor scale and hitboxes untouched.
    old_preview = "const sc=mkScout((bzSelectedCharacter().color||SKN[ST_.cur][1]),0,PLOOK);ls.add(sc.root);window.lobSc=sc;"
    new_preview = "const sc=mkScout((bzSelectedCharacter().color||SKN[ST_.cur][1]),0,PLOOK);sc.root.scale.multiplyScalar(1.18);ls.add(sc.root);window.lobSc=sc;"
    s = replace_once(s, old_preview, new_preview, "lobby operator preview scale")

    if s.count("</html>") != 1:
        raise SystemExit("Expected exactly one closing html tag")
    s = s.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
    html.write_text(s, encoding="utf-8")

css_path = html.parent / "css" / "v6-permanent-runtime-graphics.css"
css_path.parent.mkdir(parents=True, exist_ok=True)
css = r"""/* BATTLEZONE_V6_PERMANENT_RUNTIME_GRAPHICS_V1 */
#char canvas{display:block!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important}
#char{isolation:isolate;overflow:visible;transform-origin:50% 50%}
#hp,#wp,#top,#mm,#msg,#bzSquadOrders{box-sizing:border-box;max-width:calc(100vw - env(safe-area-inset-left,0px) - env(safe-area-inset-right,0px) - 16px)}
#errb{z-index:120;pointer-events:auto;max-width:calc(100vw - 16px);overflow-wrap:anywhere}
@media(orientation:landscape) and (max-height:520px){#char{max-height:38vh!important}#lb-nav{max-height:18vh;overflow-x:auto;overflow-y:hidden}#go2{min-height:44px!important;padding-block:8px!important}}
@media(orientation:portrait){#char{max-width:24vw!important}#lb-nav{max-width:calc(100vw - 16px)!important;overflow-x:auto;overscroll-behavior-x:contain}#lb-l,#maps{max-height:calc(100dvh - 26vh - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px))}}
"""
css_path.write_text(css, encoding="utf-8")
link = '<link rel="stylesheet" href="./css/v6-permanent-runtime-graphics.css">' + '\n'
s = html.read_text(encoding="utf-8")
if "v6-permanent-runtime-graphics.css" not in s:
    assert s.count("</head>") == 1
    s = s.replace("</head>", link + "</head>", 1)
    html.write_text(s, encoding="utf-8")
print("PATCHER_READY", html, css_path)
