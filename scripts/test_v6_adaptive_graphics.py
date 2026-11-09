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
assert "const ratio=[.88,1.12,1.32][bzQualityTier]" in source
assert "frameMs<0||frameMs>500" in source
assert "BATTLEZONE_V6_TERRAIN_RELIEF_V1" in source
assert "const bumpMap=LQ?null:BZTexture(name+'_height',repeat);" in source
assert "bumpMap,bumpScale:LQ?0:bumpScale" in source
assert "name==='bark'?.045" in source
height_dir=root / "app/src/main/assets/www/textures"
for material in ("asphalt","bark","concrete","dry_dirt","forest_floor","grass","military_metal","sand","weathered_rock"):
    assert (height_dir / (material + "_height.png")).is_file(), f"missing {material} height map"
start = source.index("/* " + marker + " */")
end = source.index("function loop0(n)", start)
helper = source[start:end]
node = r"""
const vm=require('node:vm');
const helper=__HELPER__;
let batterySaver=false;const ratios=[],window={devicePixelRatio:2,BZBatterySaver:()=>batterySaver};
const R={shadowMap:{enabled:true},setPixelRatio(v){ratios.push(v)}};
const sun={castShadow:true};
const ctx={window,R,sun,LQ:false,Number,Math};
vm.createContext(ctx);vm.runInContext(helper,ctx);
function sample(ms,count){for(let i=0;i<count;i++)ctx.bzAdaptiveQuality(ms)}
sample(50,56);sample(50,56);
if(vm.runInContext('bzQualityTier',ctx)!==0||ratios.at(-1)!==.88||sun.castShadow||R.shadowMap.enabled)throw new Error('low-FPS governor did not reduce resolution and disable shadows');
sample(16,175);sample(16,175);sample(16,175);
if(vm.runInContext('bzQualityTier',ctx)!==1||ratios.at(-1)!==1.12||!sun.castShadow||!R.shadowMap.enabled)throw new Error('balanced tier did not restore 1.12 pixel ratio and shadows');
sample(16,175);sample(16,175);sample(16,175);
if(vm.runInContext('bzQualityTier',ctx)!==2||ratios.at(-1)!==1.32||!sun.castShadow||!R.shadowMap.enabled)throw new Error('sustained headroom did not restore high quality');
if(!window.BZPerformance||window.BZPerformance.qualityTier!==2)throw new Error('performance telemetry missing');
batterySaver=true;sample(50,224);
if(vm.runInContext('bzQualityTier',ctx)!==2||ratios.at(-1)!==1.32||!sun.castShadow||!R.shadowMap.enabled)throw new Error('battery saver changed adaptive tier or shadow state');
console.log('ADAPTIVE_GRAPHICS_BEHAVIOR_OK');
""".replace("__HELPER__", repr(helper))
mat_start=source.index("const BZMaterial=")
mat_end=source.index("const mtl=",mat_start)
material_function=source[mat_start:mat_end]
material_node=r"""
const vm=require('node:vm');const calls=[];
const ctx={_m:{},LQ:false,BZTexture:(name,repeat)=>{calls.push(name);return {name,repeat}},THREE:{MeshStandardMaterial:function(options){return options}}};
vm.createContext(ctx);vm.runInContext(__MATERIAL__+'\\nglobalThis.makeMaterial=BZMaterial;',ctx);
const high=ctx.makeMaterial('grass',3,.98);
if(!high.bumpMap||high.bumpMap.name!=='grass_height'||high.bumpScale!==.028)throw new Error('high-quality terrain relief was not configured');
if(!calls.includes('grass_height'))throw new Error('high-quality mode did not load the height map');
ctx.LQ=true;ctx._m={};calls.length=0;const low=ctx.makeMaterial('grass',3,.98);
if(low.bumpMap===null||low.bumpScale!==0||calls.some(n=>n.endsWith('_height')))throw new Error("low-quality mode must not load or apply height maps");
console.log('TERRAIN_RELIEF_QUALITY_GATE_OK');
""".replace("__MATERIAL__", repr(material_function))
material_run=subprocess.run(["node","-e",material_node],capture_output=True,text=True)
if material_run.returncode: raise SystemExit(material_run.stderr or material_run.stdout)
print(material_run.stdout.strip())
