#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
def locate(rel):
 direct=root/rel
 if direct.is_file(): return direct
 xs=list(root.rglob(rel))
 if len(xs)!=1: raise SystemExit(f"{rel}: expected 1 file, got {len(xs)}")
 return xs[0]
rp=locate("app/src/main/assets/www/js/wildbound/rendering/runtime.js")
cp=locate("app/src/main/assets/www/css/wildbound.css")
r=rp.read_text();c=cp.read_text();marker="WILDBOUND_RENDER_RECOVERY_V1"
def repair_three_binding(source):
 old_binding="const W=window.WILDBOUND,T=()=>window.THREE,$=id=>document.getElementById(id);"
 new_binding="const W=window.WILDBOUND,T=window.THREE,$=id=>document.getElementById(id);"
 if source.count(new_binding)==1:
  pass
 elif source.count(old_binding)==1:
  source=source.replace(old_binding,new_binding,1)
 else:
  raise SystemExit("Three.js namespace binding mismatch; refusing unsafe rewrite")
 if source.count("let t=T();")==1:
  source=source.replace("let t=T();","let t=T;",1)
 elif source.count("let t=T;")!=1:
  raise SystemExit("Three.js scene initialization binding mismatch")
 # The runtime must use the namespace object, never the accessor function.
 source=source.replace("new (T()).Vector3", "new T.Vector3")
 if source.count("new T.Vector3") != 2:
  raise SystemExit("Expected exactly two Three.js Vector3 constructor calls")
 if "T=()=>window.THREE" in source or "new (T()).Vector3" in source:
  raise SystemExit("Three.js namespace normalization postcondition failed")
 return source
if "adaptiveScale" in r and "function createVfx(scene,three)" in r:
    r=repair_three_binding(r)
    rp.write_text(r,encoding="utf-8")
    print("WILDBOUND_RENDER_RECOVERY_HANDLED_BY_CANONICAL_RUNTIME")
    raise SystemExit(0)
raise SystemExit("WILDBOUND_RENDER_RECOVERY_REQUIRES_CANONICAL_RUNTIME_FEATURES")
