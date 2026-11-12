#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,struct,sys
from pathlib import Path
REQUIRED={"hunter/hunter.glb","monsters/stalker.glb","monsters/wraithcaller.glb","monsters/ironmaw.glb","monsters/hollow_king.glb","environment/canopy_01.glb","environment/canopy_02.glb","environment/deadwood.glb","environment/shrub.glb","environment/fern.glb","environment/rock.glb","environment/fern_cluster.glb"}
def read_glb(path):
 data=path.read_bytes()
 if len(data)<20 or data[:4]!=b"glTF" or struct.unpack("<I",data[4:8])[0]!=2 or struct.unpack("<I",data[8:12])[0]!=len(data): raise SystemExit(f"Invalid GLB header/length: {path}")
 length=struct.unpack("<I",data[12:16])[0]
 if data[16:20]!=b"JSON" or 20+length>len(data): raise SystemExit(f"Missing GLB JSON chunk: {path}")
 doc=json.loads(data[20:20+length].decode("utf-8").rstrip(" \\t\\r\\n\\0"))
 if doc.get("asset",{}).get("version")!="2.0": raise SystemExit(f"Unsupported glTF version: {path}")
 if any(x.get("uri") for x in doc.get("buffers",[])) or any(x.get("uri") or "bufferView" not in x for x in doc.get("images",[])): raise SystemExit(f"External/non-embedded data in offline GLB: {path}")
 return data,doc
def main():
 source=Path(__file__).resolve().parent/"wildbound-source/assets/models/wildbound"
 if len(sys.argv)!=2: raise SystemExit("usage: test_wildbound_model_assets.py PROJECT_DIR")
 packaged=Path(sys.argv[1]).resolve()/"app/src/main/assets/www/models/wildbound"
 m=json.loads((source/"manifest.json").read_text()); rows=m.get("models",[]); records={x.get("path"):x for x in rows}
 if m.get("schema")!="wildbound-cc0-model-bundle-v1" or set(records)!=REQUIRED or len(rows)!=len(REQUIRED): raise SystemExit("Model manifest schema or exact file set mismatch")
 total=0
 for rel,row in records.items():
  if row.get("license")!="CC0 1.0 Universal" or not row.get("license_url","").startswith("https://creativecommons.org/publicdomain/zero/"): raise SystemExit(f"Unverified CC0 license: {rel}")
  if not row.get("source","").startswith("https://3dassets.dev/assets/") or not row.get("download","").startswith("https://cdn.3dassets.dev/assets/") or not row.get("ai_generated") or not row.get("ai_model"): raise SystemExit(f"Missing source/AI provenance: {rel}")
  f=source/rel; packed=packaged/rel
  if not f.is_file() or not packed.is_file(): raise SystemExit(f"Missing canonical or Android GLB: {rel}")
  data,doc=read_glb(f); digest=hashlib.sha256(data).hexdigest()
  if len(data)!=row.get("bytes") or digest!=row.get("sha256") or hashlib.sha256(packed.read_bytes()).hexdigest()!=digest: raise SystemExit(f"GLB hash/size/package mismatch: {rel}")
  if not doc.get("meshes") or not doc.get("nodes"): raise SystemExit(f"No mesh/node data: {rel}")
  if row.get("textures",0) and not doc.get("images"): raise SystemExit(f"Expected embedded texture absent: {rel}")
  if rel=="hunter/hunter.glb":
   clips={x.get("name") for x in doc.get("animations",[])}
   if not {"idle","walk","run","grasp"}.issubset(clips) or not doc.get("skins") or max((len(x.get("joints",[])) for x in doc["skins"]),default=0)<70: raise SystemExit("Hunter rig or authored animation clips incomplete")
  total+=len(data)
 actors=(source.parent.parent.parent/"js/wildbound/actors/actors.js").resolve().read_text()
 world=(source.parent.parent.parent/"js/wildbound/world/world.js").resolve().read_text()
 ai=(source.parent.parent.parent/"js/wildbound/ai/monster-ai.js").resolve().read_text()
 for marker in ["./models/wildbound/hunter/hunter.glb","./models/wildbound/monsters/","stalker:'stalker'","wraith:'wraithcaller'","ironmaw:'ironmaw'","king:'hollow_king'"]:
  if marker not in actors: raise SystemExit(f"Actor loader missing: {marker}")
 for marker in ["canopy_01","canopy_02","deadwood","shrub","fern_cluster","assetReady","InstancedMesh"]:
  if marker not in world: raise SystemExit(f"Forest loader missing: {marker}")
 if "monster.rotation.y=Math.atan2(dx,dz)" not in ai: raise SystemExit("Monster facing direction missing")
 for name in ["LICENSE.txt","PROVENANCE.md","manifest.json"]:
  if not (source/name).is_file(): raise SystemExit(f"Missing provenance file: {name}")
 print(f"WILDBOUND_MODEL_ASSETS_OK models={len(REQUIRED)} bytes={total} cc0=true embedded=true android_parity=true hunter_clips=4")
if __name__=="__main__": main()
