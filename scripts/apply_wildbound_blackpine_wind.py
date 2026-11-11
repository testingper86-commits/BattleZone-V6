#!/usr/bin/env python3
"""Add GPU-driven wind sway to instanced Blackpine canopy foliage."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
p=root/'app/src/main/assets/www/js/wildbound/world/world.js'
if not p.is_file(): raise SystemExit(f'Missing world module: {p}')
s=p.read_text(encoding='utf-8')
marker='WILDBOUND_BLACKPINE_CANOPY_WIND_V1'
if marker in s:
 print('WILDBOUND_BLACKPINE_CANOPY_WIND_ALREADY_APPLIED'); raise SystemExit(0)
old="const trunkMat=new t.MeshStandardMaterial({color:0x4b3d30,roughness:1}),leafMat=new t.MeshStandardMaterial({color:0x315747,roughness:1}),stoneMat="
new="const trunkMat=new t.MeshStandardMaterial({color:0x4b3d30,roughness:1}),leafMat=new t.MeshStandardMaterial({color:0x315747,roughness:1});let windUniform=null;leafMat.onBeforeCompile=shader=>{shader.uniforms.uBlackpineWindTime={value:0};windUniform=shader.uniforms.uBlackpineWindTime;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>'+String.fromCharCode(10)+'uniform float uBlackpineWindTime;').replace('#include <begin_vertex>','#include <begin_vertex>'+String.fromCharCode(10)+'float canopyWindWeight=max(0.0,position.y+0.5);transformed.x+=sin(uBlackpineWindTime+position.x*0.7+position.z*0.5)*0.075*canopyWindWeight;transformed.z+=cos(uBlackpineWindTime*0.72+position.x*0.35)*0.04*canopyWindWeight;');};const stoneMat="
if s.count(old)!=1: raise SystemExit(f'Canopy material anchor count: {s.count(old)}')
s=s.replace(old,new,1)
old='return{fire,ground,hazards,drawBatches:14,setQuality(q){'
new='return{fire,ground,hazards,windUniform,drawBatches:14,setQuality(q){'
if s.count(old)!=1: raise SystemExit(f'World return anchor count: {s.count(old)}')
s=s.replace(old,new,1)
old='update(w,dt,t){w.fire.intensity=1.6+Math.sin(t*1.8)*.25}'
new='update(w,dt,t){w.fire.intensity=1.6+Math.sin(t*1.8)*.25;if(w.windUniform)w.windUniform.value=t*.42}'
if s.count(old)!=1: raise SystemExit(f'World update anchor count: {s.count(old)}')
s=s.replace(old,new,1)
s='/* '+marker+' */\n'+s
p.write_text(s,encoding='utf-8')
print('WILDBOUND_BLACKPINE_CANOPY_WIND_APPLIED')
