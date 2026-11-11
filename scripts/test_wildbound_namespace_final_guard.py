#!/usr/bin/env python3
"""Verify the final packaged WILDBOUND renderer and repair idempotency."""
from pathlib import Path
import re, subprocess, sys, tempfile
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = [p for p in root.rglob("js/wildbound/rendering/runtime.js") if p.is_file()]
assert len(paths) == 1, f"expected one runtime, got {len(paths)}"
source = paths[0].read_text(encoding="utf-8")
assert "T=window.THREE" in source, "namespace object binding missing"
assert not re.search(r"\bT\s*=\s*\(\s*\)\s*=>\s*window\.THREE", source), "namespace thunk remains"
assert "let t=T;" in source and "let t=T()" not in source, "scene factory binding is invalid"
assert source.count("new T.Vector3") == 2, f"expected two Vector3 constructors, got {source.count('new T.Vector3')}"
patcher = Path(__file__).with_name("apply_wildbound_namespace_final_guard.py")
with tempfile.TemporaryDirectory(prefix="wildbound-final-guard-") as temp:
    runtime = Path(temp) / "js/wildbound/rendering/runtime.js"; runtime.parent.mkdir(parents=True)
    runtime.write_text("(()=>{const W=window.WILDBOUND,T=()=>window.THREE;function makeScene(){let t=T();return [new T.Vector3(),new T.Vector3()]}})();")
    for _ in range(2): subprocess.run([sys.executable, str(patcher), temp], check=True, capture_output=True, text=True)
    fixed = runtime.read_text()
    assert "T=window.THREE" in fixed and "let t=T;" in fixed and "T()" not in fixed
print("WILDBOUND_FINAL_NAMESPACE_REGRESSION_OK constructors=2 idempotent=true")
