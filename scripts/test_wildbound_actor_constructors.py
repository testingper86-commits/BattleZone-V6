#!/usr/bin/env python3
"""Prevent WILDBOUND actor constructors from treating THREE as a function."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
actor = root / "app/src/main/assets/www/js/wildbound/actors/actors.js"
if not actor.is_file():
    raise SystemExit(f"Missing canonical WILDBOUND actor module: {actor}")
s = actor.read_text()
checks = {
    "Three.js namespace is captured as an object": "T=window.THREE" in s,
    "Three.js namespace is not wrapped in a function": "T=()=>window.THREE" not in s,
    "group constructors use the Three.js namespace": "new T.Group()" in s,
    "mesh constructors use the Three.js namespace": "new T.Mesh(" in s,
    "material constructors use the Three.js namespace": "new T.MeshStandardMaterial(" in s,
    "rig loader reuses the namespace object": "const THREE=T;" in s,
    "no callable namespace invocation remains": "T()" not in s,
}
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL"), label)
if not all(checks.values()):
    raise SystemExit("WILDBOUND_ACTOR_THREE_NAMESPACE_FAILED")
r = subprocess.run(["node", "--check", str(actor)], capture_output=True, text=True)
if r.returncode:
    raise SystemExit("Actor JavaScript syntax failed:\n" + r.stderr)
print("PASS actor JavaScript syntax")
harness = Path(__file__).resolve().parents[1] / "runtime-tests/wildbound-actor-constructor.test.js"
runtime = subprocess.run(["node", str(harness), str(root / "app/src/main/assets/www")], capture_output=True, text=True)
if runtime.returncode:
    raise SystemExit("Actor constructor runtime regression failed:\n" + runtime.stdout + runtime.stderr)
print(runtime.stdout.strip())
print("WILDBOUND_ACTOR_CONSTRUCTORS_OK", len(checks) + 2, "checks")
