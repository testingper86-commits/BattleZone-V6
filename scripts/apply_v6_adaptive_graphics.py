#!/usr/bin/env python3
"""Add a conservative frame-pacing quality governor to the existing Three.js renderer."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = list(root.rglob("app/src/main/assets/www/index.html"))
if len(paths) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(paths)}")
path = paths[0]
source = path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_ADAPTIVE_GRAPHICS_V1"
if marker in source:
    print("BATTLEZONE_V6_ADAPTIVE_GRAPHICS_ALREADY_APPLIED")
    raise SystemExit(0)
for required in ("BATTLEZONE_V6_ANIMATION_ACTION_INTEGRATION_V1", "BATTLE_ZONE_FINAL_POLISH_V1"):
    if required not in source:
        raise SystemExit(f"Required prior patch missing: {required}")

loop_anchor = "function loop0(n){window.BZGameState="
if source.count(loop_anchor) != 1:
    raise SystemExit("Game loop insertion anchor is not unique")
governor = r"""
/* BATTLEZONE_V6_ADAPTIVE_GRAPHICS_V1 */
let bzQualityElapsedMs=0,bzQualityFrames=0,bzQualityTier=1,bzQualityBad=0,bzQualityGood=0;
function bzAdaptiveQuality(frameMs){
 if(LQ||(window.BZBatterySaver&&window.BZBatterySaver()))return;
 if(!Number.isFinite(frameMs)||frameMs<0||frameMs>500)return;
 bzQualityElapsedMs+=frameMs;bzQualityFrames++;
 if(bzQualityElapsedMs<2800)return;
 const fps=bzQualityFrames*1000/Math.max(1,bzQualityElapsedMs);
 if(fps<26){bzQualityBad++;bzQualityGood=0;if(bzQualityBad>=2){bzQualityTier=Math.max(0,bzQualityTier-1);bzQualityBad=0}}
 else if(fps>50){bzQualityGood++;bzQualityBad=0;if(bzQualityGood>=3){bzQualityTier=Math.min(2,bzQualityTier+1);bzQualityGood=0}}
 else{bzQualityBad=0;bzQualityGood=0}
 const ratio=[.82,1,1.2][bzQualityTier];
 R.setPixelRatio(Math.min(window.devicePixelRatio||1,ratio));
 const shadows=bzQualityTier>0;
 if(sun.castShadow!==shadows||R.shadowMap.enabled!==shadows){sun.castShadow=shadows;R.shadowMap.enabled=shadows}
 window.BZPerformance={fps:Math.round(fps*10)/10,qualityTier:bzQualityTier,frameTimeMs:Math.round(bzQualityElapsedMs/Math.max(1,bzQualityFrames)*10)/10};
 bzQualityElapsedMs=0;bzQualityFrames=0;
}
"""
source = source.replace(loop_anchor, governor + "\n" + loop_anchor, 1)

old_loop = "const dt=Math.min((n-last)/1000,.1);last=n;"
new_loop = "const frameMs=Math.max(0,n-last),dt=Math.min(frameMs/1000,.1);last=n;bzAdaptiveQuality(frameMs);"
if source.count(old_loop) != 1:
    raise SystemExit(f"Frame-time anchor expected once, found {source.count(old_loop)}")
source = source.replace(old_loop, new_loop, 1)

old_battery = "let FD=sg('bzfade')!=='0',BS=sg('bzbs')==='1';"
new_battery = "let FD=sg('bzfade')!=='0',BS=sg('bzbs')==='1';window.BZBatterySaver=()=>BS;"
if source.count(old_battery) != 1:
    raise SystemExit("Battery-saver state anchor is not unique")
source = source.replace(old_battery, new_battery, 1)

old_apply = "function applyBS(){R.setPixelRatio(BS?1:(LQ?1:Math.min(devicePixelRatio,1.25)));rs()}"
new_apply = "function applyBS(){window.BZBatterySaver=()=>BS;R.setPixelRatio(BS?1:(LQ?1:Math.min(devicePixelRatio,1.25)));rs()}"
if source.count(old_apply) != 1:
    raise SystemExit("Battery-saver apply anchor is not unique")
source = source.replace(old_apply, new_apply, 1)

source = source.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
path.write_text(source, encoding="utf-8")
validators = list(root.rglob("validate_project.py"))
if len(validators) != 1:
    raise SystemExit(f"Expected one project validator, found {len(validators)}")
validator = validators[0]
checks = validator.read_text(encoding="utf-8")
old_check = "'frame pacing after stalls': 'Math.min((n-last)/1000,.1)' in source,"
new_check = "'frame pacing after stalls': 'frameMs=Math.max(0,n-last)' in source and 'bzAdaptiveQuality(frameMs)' in source,"
if checks.count(old_check) != 1:
    raise SystemExit(f"Frame pacing validator anchor expected once, found {checks.count(old_check)}")
validator.write_text(checks.replace(old_check, new_check, 1), encoding="utf-8")
print("BATTLEZONE_V6_ADAPTIVE_GRAPHICS_APPLIED", path)
