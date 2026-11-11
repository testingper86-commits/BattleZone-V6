#!/usr/bin/env python3
"""Behavioral WILDBOUND AI regression tests executed in a real JavaScript VM."""
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
source = Path(__file__).resolve().parents[1] / "runtime-tests/wildbound-ai-runtime.test.js"
if not source.is_file():
    raise SystemExit(f"Missing AI runtime harness: {source}")
www = root / "app/src/main/assets/www"
for relative in ("js/wildbound/actors/actors.js", "js/wildbound/ai/monster-ai.js", "js/wildbound/gameplay/combat.js", "js/wildbound/rendering/runtime.js", "js/wildbound/world/world.js"):
    path = www / relative
    if not path.is_file():
        raise SystemExit(f"Missing WILDBOUND module: {relative}")
    check = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if check.returncode:
        raise SystemExit(f"JavaScript syntax failed: {relative}\n{check.stderr}")
result = subprocess.run(["node", str(source), str(www)], capture_output=True, text=True)
if result.returncode:
    raise SystemExit(result.stdout + result.stderr)
print(result.stdout.strip())
print("WILDBOUND_AI_RUNTIME_REGRESSION_OK")
