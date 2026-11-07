#!/usr/bin/env python3
"""Fixture tests for per-file asset license evidence and release blocking."""
from pathlib import Path
import hashlib, importlib.util, tempfile
SCRIPT=Path(__file__).with_name("create_asset_provenance_ledger.py")
spec=importlib.util.spec_from_file_location("asset_ledger",SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
def put(path:Path,data:bytes): path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)/"www"; root.mkdir()
 put(root/"models/characters/kenney/License.txt",b"Creative Commons Zero CC0")
 put(root/"models/characters/kenney/model.fbx",b"kenney-model")
 put(root/"models/characters/kaykit_v1_2/License.txt",b"Creative Commons Zero CC0")
 put(root/"models/characters/kaykit_v1_2/model.glb",b"kaykit-model")
 voice=root/"audio/cc0_voiceover"; put(voice/"License.txt",b"Creative Commons Zero CC0")
 put(voice/"Credits.txt",b"Kenney voice actors")
 put(voice/"PROVENANCE.md",b"Kenney Voiceover Pack CC0 source and creator")
 voice_file=voice/"Male/callout.ogg"; put(voice_file,b"verified-voice")
 digest=hashlib.sha256(voice_file.read_bytes()).hexdigest()
 put(voice/"manifest.sha256",(digest+"  Male/callout.ogg"+chr(10)).encode())
 put(root/"textures/terrain.png",b"unknown-texture")
 put(root/"sprites/muzzle.png",b"unknown-sprite")
 data=mod.build_ledger(root)
 assert data["summary"]=={"binary_asset_count":5,"verified_cc0_count":3,"unverified_count":2,"release_blocked":True},data["summary"]
 assert {x["status"] for x in data["assets"] if x["path"].startswith("models/")}=={"verified_cc0"}
 assert next(x for x in data["assets"] if x["path"].endswith("callout.ogg"))["license"]=="CC0-1.0"
 assert all(x["status"]=="unverified" for x in data["assets"] if x["path"].startswith(("textures/","sprites/")))
 bad=voice/"manifest.sha256"; bad.write_text("0"*64+"  Male/callout.ogg"+chr(10))
 try: mod.build_ledger(root)
 except ValueError as e: assert "checksum mismatch" in str(e)
 else: raise AssertionError("mismatched voice hash was accepted")
print("ASSET_PROVENANCE_FIXTURE_TESTS_OK")
