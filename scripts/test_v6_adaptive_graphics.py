#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
source = (root / "app/src/main/assets/www/index.html").read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_ADAPTIVE_GRAPHICS_V1"
assert marker in source
assert "window.BZBatterySaver=()=>BS" in source
assert "bzAdaptiveQuality(frameMs)" in source
start = source.index("/* " + marker + " */")
end = source.index("function loop0(n)", start)
helper = source[start:end]
node = r"""
const vm=require('node:vm');
const helper=__HELPER__;
const ratios=[],window={devicePixelRatio:2,BZBatterySaver:()=>false};
const R={shadowMap:{enabled:true},setPixelRatio(v){ratios.push(v)}};
const sun={castShadow:true};
const ctx={window,R,sun,LQ:false,Number,Math};
vm.createContext(ctx);vm.runInContext(helper,ctx);
function sample(ms,count){for(let i=0;i<count;i++)ctx.bzAdaptiveQuality(ms)}
sample(50,56);sample(50,56);
if(vm.runInContext('bzQualityTier',ctx)!==0||ratios.at(-1)!==.82||sun.castShadow||R.shadowMap.enabled)throw new Error('low-FPS governor did not reduce resolution and disable shadows');
sample(16,175);sample(16,175);sample(16,175);
if(vm.runInContext('bzQualityTier',ctx)!==1)throw new Error('quality recovery did not restore the balanced tier');
sample(16,175);sample(16,175);sample(16,175);
if(vm.runInContext('bzQualityTier',ctx)!==2||ratios.at(-1)!==1.2||!sun.castShadow||!R.shadowMap.enabled)throw new Error('sustained headroom did not restore high quality');
if(!window.BZPerformance||window.BZPerformance.qualityTier!==2)throw new Error('performance telemetry missing');
console.log('ADAPTIVE_GRAPHICS_BEHAVIOR_OK');
""".replace("__HELPER__", repr(helper))
p=subprocess.run(["node","-e",node],capture_output=True,text=True)
if p.returncode: raise SystemExit(p.stderr or p.stdout)
print(p.stdout.strip())
print("ADAPTIVE_GRAPHICS_STATIC_CHECKS_OK")
