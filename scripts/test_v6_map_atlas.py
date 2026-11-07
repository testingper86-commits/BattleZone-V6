#!/usr/bin/env python3
"""Regression tests for offline map data, safe route planning and atlas integration."""
from pathlib import Path
import subprocess
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
htmls = list(root.rglob("app/src/main/assets/www/index.html"))
if len(htmls) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(htmls)}")
www = htmls[0].parent
js_path, css_path = www / "js" / "bz-map-atlas.js", www / "css" / "bz-map-atlas.css"
if not js_path.is_file() or not css_path.is_file():
    raise SystemExit("Map Atlas JS/CSS assets are missing")
s, js, css = htmls[0].read_text(encoding="utf-8"), js_path.read_text(encoding="utf-8"), css_path.read_text(encoding="utf-8")
checks = {
    "map atlas marker and launcher are installed": "BATTLEZONE_V6_MAP_ATLAS_V1" in s and 'id="bzMapAtlasOpen"' in s,
    "offline JS and CSS are linked": './js/bz-map-atlas.js' in s and './css/bz-map-atlas.css' in s,
    "all ten installed maps have named POI catalogs": all(f"{name}:[" in js for name in ("Greenfield","Sandstorm","Frostbite","Jungle","Islet","Canyon","Harbor","Highland","Wasteland","Marsh")),
    "actual terrain heightfield is sampled": "bzTerrainHeight(x,z)" in js and "buildGrid()" in js,
    "water and river hazards use live world geometry": "w.lake" in js and "w.river" in js and "w.map.sea" in js,
    "route planner uses A-star cost and slope": "function createRoute" in js and "heuristic(nx,nz)" in js and "slope-.3" in js,
    "saved waypoints are local and bounded": "bzMapAtlasWaypoints:" in js and "waypoints.length>=30" in js,
    "route persistence is local": "bzMapAtlasRoute:" in js and "localStorage.setItem(routeKey()" in js,
    "map supports pointer pan and zoom": "pointerdown" in js and "pointermove" in js and "addEventListener('wheel'" in js,
    "navigation markers are installed in the 3D world": "installWorldMarkers" in js and "BZMapAtlasMarkers" in js,
    "land POIs normalize away from water and crossings use the live bridge": "function normalizePois" in js and "water.bridge,water.river" in js,
    "route action avoids claiming guaranteed safety": "Plot route</button>" in js and "Plot safe route" not in js,
    "no remote map service or network dependency": "https://" not in js and "fetch(" not in js and "XMLHttpRequest" not in js,
    "reduced motion and mobile layout are covered": "prefers-reduced-motion" in css and "@media(max-width:760px)" in css,
}
for name, ok in checks.items(): print(("PASS " if ok else "FAIL ") + name)
if not all(checks.values()): raise SystemExit(f"{sum(not x for x in checks.values())} Map Atlas source checks failed")
node = r'''const assert=require('assert');const fs=require('fs');const vm=require('vm');const source=fs.readFileSync(process.argv[1],'utf8');const window={};const document={addEventListener(){},getElementById(){return null}};vm.runInNewContext(source,{window,document,Math,Number,Array,Float64Array,Int32Array,Uint8Array,Infinity,Map,Set});const core=window.BZMapAtlasCore;assert(core&&typeof core.createRoute==='function');const moved=core.normalizePois([{id:'dry',kind:'landmark',x:0,z:0}],(x,z)=>Math.hypot(x,z)<30,null,null)[0];assert(Math.hypot(moved.x,moved.z)>=30);const crossing=core.normalizePois([{id:'bridge',kind:'crossing',x:0,z:0}],()=>true,{x:42},{z:-18})[0];assert.strictEqual(crossing.x,42);assert.strictEqual(crossing.z,-18);const hazard=core.normalizePois([{id:'water',kind:'hazard',x:0,z:0}],()=>true,null,null)[0];assert.strictEqual(hazard.x,0);for(const name of ['Greenfield','Sandstorm','Frostbite','Jungle','Islet','Canyon','Harbor','Highland','Wasteland','Marsh'])assert(core.getMapPOIs(name).length>=5,name+' POI catalog');const flat=core.createRoute({x:-200,z:0},{x:200,z:0},{step:20,heightAt:()=>0});assert(flat&&flat.points.length>=2&&Math.abs(flat.points[0].x+200)<1&&Math.abs(flat.points[flat.points.length-1].x-200)<1);assert(flat.distance>=390&&flat.distance<=430);const detour=core.createRoute({x:-200,z:0},{x:200,z:0},{step:20,heightAt:()=>0,isBlocked:(x,z)=>Math.abs(x)<11&&Math.abs(z)<100});assert(detour&&detour.points.some(p=>Math.abs(p.z)>=100));const impossible=core.createRoute({x:-400,z:0},{x:400,z:0},{step:20,isBlocked:x=>Math.abs(x)<11});assert.strictEqual(impossible,null);console.log('MAP_ATLAS_ROUTE_BEHAVIOR_OK checks=17');'''
result = subprocess.run(["node", "-e", node, str(js_path)], capture_output=True, text=True, timeout=30)
if result.returncode: raise SystemExit(result.stderr or result.stdout or "Map Atlas route tests failed")
print(result.stdout.strip())
print(f"MAP_ATLAS_REGRESSION_OK checks={len(checks)+14}")
