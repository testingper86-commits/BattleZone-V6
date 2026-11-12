#!/usr/bin/env python3
"""Regression checks for the permanent V6 runtime and graphics repair."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(htmls)}")
s = htmls[0].read_text(encoding="utf-8")
checks = {
    "repair marker": "BATTLEZONE_V6_PERMANENT_RUNTIME_GRAPHICS_REPAIR_V1" in s,
    "no unsupported InstancedMesh bounds calls": "L.computeBoundingSphere();T.computeBoundingSphere();" not in s and "grass.computeBoundingSphere()" not in s,
    "version-safe instance bounds": "bzPrepareInstanceBoundsSafe(L);bzPrepareInstanceBoundsSafe(T);" in s and "bzPrepareInstanceBoundsSafe(grass);" in s and "typeof mesh.computeBoundingSphere==='function'" in s and "mesh.frustumCulled=false" in s,
    "HUD validates weapon and inventory": "if(!w||!Array.isArray(P.own))return" in s,
    "HUD validates all required DOM nodes": "bzHudRequired.some(node=>!node)" in s,
    "HUD missing-node diagnostic is one-shot": "__bzHudMissingReported" in s,
    "lobby-only operator preview scaling": "sc.root.scale.multiplyScalar(1.18)" in s,
    "permanent responsive stylesheet linked": "v6-permanent-runtime-graphics.css" in s,
}
css = htmls[0].parent / "css" / "v6-permanent-runtime-graphics.css"
checks["responsive graphics stylesheet exists"] = css.is_file()
if css.is_file():
    text = css.read_text(encoding="utf-8")
    checks["canvas fills operator preview"] = "#char canvas" in text
    checks["mobile safe-area layout"] = "safe-area-inset" in text and "orientation:portrait" in text
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + " " + name)
if not all(checks.values()):
    raise SystemExit("Permanent runtime/graphics regression checks failed")
print("PERMANENT_RUNTIME_GRAPHICS_REPAIR_TESTS_OK")
