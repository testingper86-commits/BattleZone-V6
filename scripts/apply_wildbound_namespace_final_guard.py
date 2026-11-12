#!/usr/bin/env python3
"""Final, idempotent Three.js namespace repair applied after every source generator."""
from pathlib import Path
import re, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = [p for p in root.rglob("js/wildbound/rendering/runtime.js") if p.is_file()]
if len(paths) != 1: raise SystemExit(f"Expected exactly one WILDBOUND renderer, found {len(paths)}")
path = paths[0]; source = path.read_text(encoding="utf-8"); original = source
source, declaration_edits = re.subn(r"\bT\s*=\s*\(\s*\)\s*=>\s*window\.THREE\b", "T=window.THREE", source)
source, factory_edits = re.subn(r"\b(let|const)\s+t\s*=\s*T\s*\(\s*\)\s*;", lambda m: m.group(1) + " t=T;", source)
source = source.replace("new (T()).Vector3", "new T.Vector3")
if re.search(r"\bT\s*=\s*\(\s*\)\s*=>\s*window\.THREE", source): raise SystemExit("Three.js namespace remains a thunk")
if re.search(r"\b(?:let|const)\s+t\s*=\s*T\s*\(", source): raise SystemExit("Scene factory still calls the namespace")
if "new T.Vector3" in source and "T=window.THREE" not in source: raise SystemExit("Vector3 constructor has no namespace-object binding")
if "function makeScene()" in source and "let t=T;" not in source: raise SystemExit("makeScene does not capture the namespace object")
if source != original: path.write_text(source, encoding="utf-8")
print(f"WILDBOUND_FINAL_NAMESPACE_REPAIR_OK changed={source != original} declaration_edits={declaration_edits} factory_edits={factory_edits}")
