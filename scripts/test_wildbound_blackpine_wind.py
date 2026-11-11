#!/usr/bin/env python3
"""Regression checks for GPU-driven Blackpine canopy wind."""
from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/world/world.js'
s=p.read_text(encoding='utf-8')
checks={
 "canopy wind marker present":"WILDBOUND_BLACKPINE_CANOPY_WIND_V1" in s,
 "wind is implemented in the foliage vertex shader":"leafMat.onBeforeCompile=shader=>" in s,
 "shader uses one time uniform":"uBlackpineWindTime" in s and "windUniform=shader.uniforms.uBlackpineWindTime" in s,
 "canopy sway is vertex-height weighted":"canopyWindWeight=max(0.0,position.y+0.5)" in s,
 "wind displaces both horizontal axes":"transformed.x+=sin(uBlackpineWindTime" in s and "transformed.z+=cos(uBlackpineWindTime" in s,
 "wind uniform is updated by the existing world tick":"if(w.windUniform)w.windUniform.value=t*.42" in s,
 "existing instanced forest draw path remains":"new t.InstancedMesh(new t.CylinderGeometry" in s and "new t.InstancedMesh(new t.ConeGeometry" in s,
 "existing quality scaling remains intact":"trunk.count=Math.floor(ti*f);crowns.count=Math.floor(ci*f)" in s,
 "existing fire and hazard systems remain":"w.fire.intensity=1.6+Math.sin(t*1.8)*.25" in s and "hazards.push({x,z,radius:3.4,pool,rim})" in s,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
if not all(checks.values()): raise SystemExit('BLACKPINE_WIND_REGRESSION_FAILED')
r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr)
print('PASS JavaScript syntax')
print('WILDBOUND_BLACKPINE_WIND_OK',len(checks)+1,'checks')
