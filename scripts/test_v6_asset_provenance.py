#!/usr/bin/env python3
"""Fixture tests for per-file asset license evidence and release blocking."""
from pathlib import Path
import hashlib, importlib.util, tempfile, json
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
 assert data["summary"]=={"binary_asset_count":5,"verified_cc0_count":3,"verified_original_count":0,"unverified_count":2,"release_blocked":True},data["summary"]
 assert {x["status"] for x in data["assets"] if x["path"].startswith("models/")}=={"verified_cc0"}
 assert next(x for x in data["assets"] if x["path"].endswith("callout.ogg"))["license"]=="CC0-1.0"
 assert all(x["status"]=="unverified" for x in data["assets"] if x["path"].startswith(("textures/","sprites/")))
 bad=voice/"manifest.sha256"; bad.write_text("0"*64+"  Male/callout.ogg"+chr(10))
 try: mod.build_ledger(root)
 except ValueError as e: assert "checksum mismatch" in str(e)
 else: raise AssertionError("mismatched voice hash was accepted")

 # A generated original is verified only when its manifest, generator and exact bytes agree.
 generated=root/"sprites/generated.png"; put(generated,b"procedural-original")
 generated_row={"path":"sprites/generated.png","sha256":hashlib.sha256(generated.read_bytes()).hexdigest(),"size_bytes":generated.stat().st_size,"generator":"BattleZone-V6-Procedural-Assets","generator_version":"1.0.0","license":"original_project_generated"}
 provenance={"schema_version":1,"generator":"BattleZone-V6-Procedural-Assets","generator_version":"1.0.0","license":"original_project_generated","license_basis":"Original procedural artwork; no third-party source images or textures are embedded.","assets":[generated_row]}
 put(root/"PROCEDURAL_ASSET_PROVENANCE.json",json.dumps(provenance).encode())
 verified=mod.build_ledger(root)
 assert verified["summary"]=={"binary_asset_count":6,"verified_cc0_count":3,"verified_original_count":1,"unverified_count":2,"release_blocked":True},verified["summary"]
 assert next(x for x in verified["assets"] if x["path"]=="sprites/generated.png")["status"]=="verified_original"
 generated.write_bytes(b"tampered")
 try: mod.build_ledger(root)
 except ValueError as e: assert "checksum or size mismatch" in str(e)
 else: raise AssertionError("tampered procedural asset was accepted")

print("ASSET_PROVENANCE_FIXTURE_TESTS_OK")
