#!/usr/bin/env python3
"""Run Node's parser over every inline and packaged game JavaScript file."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = root / "app/src/main/assets/www/index.html"
if not html.is_file():
    raise SystemExit(f"Game HTML not found: {html}")
node = subprocess.run(["node", "--version"], capture_output=True, text=True)
if node.returncode:
    raise SystemExit("Node.js is required for runtime JavaScript syntax validation")
source = html.read_text(encoding="utf-8")
blocks = re.findall(r"<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>", source, re.I | re.S)
with tempfile.TemporaryDirectory(prefix="battlezone-js-") as temp:
    temp_dir = Path(temp)
    for index, block in enumerate(blocks):
        path = temp_dir / f"inline-{index}.js"
        path.write_text(block, encoding="utf-8")
        result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"Inline script {index} failed syntax validation:\n{result.stderr}")
    packaged = sorted((root / "app/src/main/assets/www").rglob("*.js"))
    for path in packaged:
        result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"Packaged JavaScript failed syntax validation: {path}\n{result.stderr}")
print(f"JAVASCRIPT_SYNTAX_OK inline={len(blocks)} packaged={len(packaged)} node={node.stdout.strip()}")
