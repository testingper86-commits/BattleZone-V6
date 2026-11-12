#!/usr/bin/env python3
"""Add opt-in local-only Three.js render diagnostics for Android device profiling."""
from pathlib import Path
import sys
MARKER="BATTLEZONE_V6_RENDER_DIAGNOSTICS_V1"
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected one game index.html, found {len(files)}")
path=files[0]; source=path.read_text(encoding="utf-8")
if MARKER in source:
    if "window.BZRenderDiagnostics.tick(n)" not in source or "R.info" not in source: raise SystemExit("Render diagnostics marker exists but implementation is incomplete")
    print(MARKER+" already applied"); raise SystemExit(0)
anchor="R.toneMappingExposure=1.08;"
if source.count(anchor)!=1: raise SystemExit("Could not find unique renderer initialization anchor")
diag=r"""/* BATTLEZONE_V6_RENDER_DIAGNOSTICS_V1 */
const BZ_DIAG_ENABLED=new URLSearchParams(location.search).get('bzdiag')==='1';
const BZ_DIAG_NODE=BZ_DIAG_ENABLED?(()=>{const el=document.createElement('pre');el.id='bz-render-diagnostics';el.style.cssText='position:fixed;left:8px;top:8px;z-index:2147483000;margin:0;padding:9px 11px;max-width:calc(100vw - 32px);max-height:35vh;overflow:hidden;background:rgba(3,10,18,.88);border:1px solid rgba(140,190,230,.45);border-radius:8px;color:#d9efff;font:11px/1.45 ui-monospace,monospace;white-space:pre-wrap;pointer-events:none';el.textContent='BATTLEZONE LOCAL RENDER DIAGNOSTICS';document.body.appendChild(el);return el})():null;
let BZ_DIAG_START=0,BZ_DIAG_FRAMES=0,BZ_DIAG_LAST=0,BZ_DIAG_FRAME_MS=0;
window.BZRenderDiagnostics=Object.freeze({enabled:BZ_DIAG_ENABLED,tick(n){if(!BZ_DIAG_NODE)return;BZ_DIAG_FRAMES++;if(BZ_DIAG_LAST)BZ_DIAG_FRAME_MS=n-BZ_DIAG_LAST;BZ_DIAG_LAST=n;if(!BZ_DIAG_START)BZ_DIAG_START=n;if(n-BZ_DIAG_START<1000)return;const fps=BZ_DIAG_FRAMES*1000/(n-BZ_DIAG_START),ri=R.info||{},rr=ri.render||{},mm=ri.memory||{},NL=String.fromCharCode(10);let text='BATTLEZONE LOCAL DIAGNOSTICS'+NL;text+='FPS '+fps.toFixed(1)+' | frame '+BZ_DIAG_FRAME_MS.toFixed(1)+' ms'+NL;text+='draw calls '+(rr.calls||0)+' | triangles '+(rr.triangles||0)+' | points '+(rr.points||0)+' | lines '+(rr.lines||0)+NL;text+='geometries '+(mm.geometries||0)+' | textures '+(mm.textures||0)+NL;text+='pixel ratio '+R.getPixelRatio().toFixed(2)+' | max texture '+R.capabilities.maxTextureSize+NL;text+='quality '+(LQ?'LOW':'HIGH')+' | battery saver '+(BS?'ON':'OFF')+NL;text+='device memory '+(navigator.deviceMemory||'n/a')+' GB | CPU threads '+(navigator.hardwareConcurrency||'n/a');BZ_DIAG_NODE.textContent=text;BZ_DIAG_FRAMES=0;BZ_DIAG_START=n;}});
"""
source=source.replace(anchor,anchor+chr(10)+diag,1)
loop_anchor="lt0=n;_l0(n);if(started){"
if source.count(loop_anchor)!=1: raise SystemExit("Could not find unique main loop wrapper anchor")
source=source.replace(loop_anchor,"lt0=n;_l0(n);if(window.BZRenderDiagnostics)window.BZRenderDiagnostics.tick(n);if(started){",1)
if source.count(MARKER)!=1 or "window.BZRenderDiagnostics.tick(n)" not in source: raise SystemExit("Render diagnostics insertion failed")
path.write_text(source,encoding="utf-8")
print(MARKER+" applied",path)
