#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, tempfile
from pathlib import Path
from PIL import Image
SCRIPT=Path(__file__).with_name("apply_v6_procedural_asset_replacement.py")
spec=importlib.util.spec_from_file_location("procedural_assets",SCRIPT)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/"app/src/main/assets/www").mkdir(parents=True)
    first=module.apply(root)
    hashes={row["path"]:row["sha256"] for row in first["assets"]}
    second=module.apply(root)
    assert len(hashes)==36 and len(second["assets"])==36
    assert hashes=={row["path"]:row["sha256"] for row in second["assets"]}, "generator is not deterministic"
    assets=root/"app/src/main/assets/www"
    manifest=json.loads((assets/"PROCEDURAL_ASSET_PROVENANCE.json").read_text())
    assert manifest["license"]=="original_project_generated"
    for rel in module.expected_paths():
        path=assets/rel
        assert path.is_file() and path.stat().st_size>100
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if rel.startswith("textures/"): assert image.size==(512,512) and image.mode=="RGB"
            if rel.startswith("sprites/"): assert image.size==(256,256) and image.mode=="RGBA"
            if rel.startswith("loading/") or rel.startswith("branding/"): assert image.format=="JPEG"
print("PROCEDURAL_ASSET_REPLACEMENT_TESTS_OK assets=36 deterministic=true images_decodable=true")
