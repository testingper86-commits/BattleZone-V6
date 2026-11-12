#!/usr/bin/env python3
"""Generate a per-file license/provenance ledger for distributable game assets."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path, PurePosixPath

BINARY_EXTENSIONS={".png",".jpg",".jpeg",".webp",".ogg",".mp3",".wav",".fbx",".glb",".gltf",".obj",".dae",".mtl",".pdf",".bin"}

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def has_cc0(path:Path)->bool:
    if not path.is_file(): return False
    text=path.read_text(encoding="utf-8",errors="ignore").lower()
    return "creative commons zero" in text or "cc0" in text

def verified_voice_files(root:Path)->tuple[set[str],list[str]]:
    voice=root/"audio/cc0_voiceover"
    evidence=["audio/cc0_voiceover/License.txt","audio/cc0_voiceover/Credits.txt","audio/cc0_voiceover/PROVENANCE.md","audio/cc0_voiceover/manifest.sha256"]
    if not all((root/p).is_file() for p in evidence): return set(),[]
    if not has_cc0(voice/"License.txt"): return set(),[]
    provenance=(voice/"PROVENANCE.md").read_text(encoding="utf-8",errors="ignore").lower()
    if "kenney" not in provenance or "cc0" not in provenance: return set(),[]
    manifest={}
    for line in (voice/"manifest.sha256").read_text(encoding="utf-8").splitlines():
        parts=line.strip().split(maxsplit=1)
        if not parts: continue
        if len(parts)!=2 or len(parts[0])!=64: raise ValueError("Malformed voice SHA-256 manifest row")
        digest,relative=parts[0].lower(),parts[1].lstrip("* ")
        rel=PurePosixPath(relative)
        if rel.is_absolute() or ".." in rel.parts: raise ValueError("Unsafe path in voice SHA-256 manifest")
        file=voice.joinpath(*rel.parts)
        if not file.is_file() or sha256_file(file)!=digest: raise ValueError(f"Voice checksum mismatch: {relative}")
        manifest[relative]=digest
    actual={p.relative_to(voice).as_posix() for p in voice.rglob("*.ogg") if p.is_file()}
    if actual!=set(manifest): raise ValueError("Voice SHA-256 manifest does not exactly cover packaged OGG files")
    return {"audio/cc0_voiceover/"+p for p in actual},evidence

def verified_generated_assets(root:Path)->tuple[dict[str,dict],list[str]]:
    manifest_path=root/"PROCEDURAL_ASSET_PROVENANCE.json"
    if not manifest_path.is_file(): return {},[]
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema_version")!=1 or data.get("generator")!="BattleZone-V6-Procedural-Assets":
        raise ValueError("Unrecognized procedural asset provenance manifest")
    if data.get("generator_version")!="1.0.0" or data.get("license")!="original_project_generated":
        raise ValueError("Procedural asset generator version or rights declaration is invalid")
    if "no third-party source images or textures" not in data.get("license_basis",""):
        raise ValueError("Procedural asset provenance does not exclude third-party source media")
    verified={}
    for row in data.get("assets",[]):
        relative=row.get("path","")
        rel=PurePosixPath(relative)
        if not relative or rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Unsafe path in procedural asset provenance manifest")
        path=root.joinpath(*rel.parts)
        if not path.is_file(): raise ValueError(f"Generated asset is missing: {relative}")
        if row.get("generator")!=data["generator"] or row.get("generator_version")!=data["generator_version"]:
            raise ValueError(f"Generated asset generator metadata mismatch: {relative}")
        if row.get("license")!="original_project_generated":
            raise ValueError(f"Generated asset rights declaration mismatch: {relative}")
        if row.get("size_bytes")!=path.stat().st_size or row.get("sha256")!=sha256_file(path):
            raise ValueError(f"Generated asset checksum or size mismatch: {relative}")
        if relative in verified: raise ValueError(f"Duplicate generated asset record: {relative}")
        verified[relative]=row
    if not verified: raise ValueError("Procedural asset provenance manifest contains no assets")
    return verified,["PROCEDURAL_ASSET_PROVENANCE.json"]

def verified_wildbound_models(root:Path)->tuple[set[str],list[str]]:
    bundle=root/"models/wildbound"; manifest_path=bundle/"manifest.json"; license_path=bundle/"LICENSE.txt"; provenance_path=bundle/"PROVENANCE.md"
    evidence=["models/wildbound/LICENSE.txt","models/wildbound/PROVENANCE.md","models/wildbound/manifest.json"]
    if not all(path.is_file() for path in (manifest_path,license_path,provenance_path)): return set(),[]
    if not has_cc0(license_path): raise ValueError("WILDBOUND model bundle license does not explicitly declare CC0")
    provenance=provenance_path.read_text(encoding="utf-8",errors="ignore").lower()
    if "3dassets.dev" not in provenance or "cc0" not in provenance or "sha-256" not in provenance: raise ValueError("WILDBOUND model provenance is incomplete")
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema")!="wildbound-cc0-model-bundle-v1" or data.get("source")!="3DAssets.dev": raise ValueError("Unrecognized WILDBOUND model provenance schema")
    required={"hunter/hunter.glb","monsters/stalker.glb","monsters/wraithcaller.glb","monsters/ironmaw.glb","monsters/hollow_king.glb","environment/canopy_01.glb","environment/canopy_02.glb","environment/deadwood.glb","environment/shrub.glb","environment/fern.glb","environment/rock.glb","environment/fern_cluster.glb"}
    rows=data.get("models",[]); records={row.get("path"):row for row in rows}
    if set(records)!=required or len(rows)!=len(required): raise ValueError("WILDBOUND model manifest does not exactly cover the required 12 GLBs")
    verified=set()
    for relative,row in records.items():
        rel=PurePosixPath(relative)
        if rel.is_absolute() or ".." in rel.parts: raise ValueError(f"Unsafe WILDBOUND model path: {relative}")
        path=bundle.joinpath(*rel.parts)
        if not path.is_file(): raise ValueError(f"WILDBOUND model is missing: {relative}")
        if row.get("license")!="CC0 1.0 Universal" or not row.get("license_url","").startswith("https://creativecommons.org/publicdomain/zero/"): raise ValueError(f"WILDBOUND model license is not CC0: {relative}")
        if not row.get("source","").startswith("https://3dassets.dev/assets/") or not row.get("download","").startswith("https://cdn.3dassets.dev/assets/"): raise ValueError(f"WILDBOUND model source URL is missing: {relative}")
        if not row.get("ai_generated") or not row.get("ai_model"): raise ValueError(f"WILDBOUND model AI provenance disclosure is missing: {relative}")
        if row.get("bytes")!=path.stat().st_size or row.get("sha256")!=sha256_file(path): raise ValueError(f"WILDBOUND model SHA-256 or size mismatch: {relative}")
        verified.add("models/wildbound/"+relative)
    return verified,evidence

def build_ledger(assets_root:Path)->dict:
    root=assets_root.resolve()
    if not root.is_dir(): raise ValueError(f"Asset root does not exist: {root}")
    voice_verified,voice_evidence=verified_voice_files(root)
    generated_verified,generated_evidence=verified_generated_assets(root)
    wildbound_verified,wildbound_evidence=verified_wildbound_models(root)
    rows=[]
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in BINARY_EXTENSIONS):
        rel=path.relative_to(root).as_posix()
        license_name=None; status="unverified"; evidence=[]; note="No per-pack license/provenance evidence is recorded for this retained asset."
        if rel.startswith("models/characters/kenney/"):
            license_path=root/"models/characters/kenney/License.txt"
            if has_cc0(license_path): license_name="CC0-1.0"; status="verified_cc0"; evidence=["models/characters/kenney/License.txt"]; note="Package-local license explicitly states Creative Commons Zero."
        elif rel.startswith("models/characters/kaykit_v1_2/"):
            license_path=root/"models/characters/kaykit_v1_2/License.txt"
            if has_cc0(license_path): license_name="CC0-1.0"; status="verified_cc0"; evidence=["models/characters/kaykit_v1_2/License.txt"]; note="Package-local license explicitly states Creative Commons Zero."
        elif rel in voice_verified:
            license_name="CC0-1.0"; status="verified_cc0"; evidence=voice_evidence; note="CC0 license, creator/source provenance, credits and per-file SHA-256 manifest verified."
        elif rel in wildbound_verified:
            license_name="CC0-1.0"; status="verified_cc0"; evidence=wildbound_evidence; note="CC0 model license, per-model source/AI disclosure and exact SHA-256 manifest verified."
        elif rel in generated_verified:
            license_name="original_project_generated"; status="verified_original"; evidence=generated_evidence; note="Original deterministic procedural artwork; per-file SHA-256 and generator version verified; no third-party source media used."
        rows.append({"path":rel,"size_bytes":path.stat().st_size,"sha256":sha256_file(path),"license":license_name,"status":status,"evidence":evidence,"note":note})
    verified=sum(row["status"]=="verified_cc0" for row in rows)
    original=sum(row["status"]=="verified_original" for row in rows)
    unverified=len(rows)-verified-original
    return {"schema_version":1,"asset_root":"app/src/main/assets/www","hash_algorithm":"sha256","summary":{"binary_asset_count":len(rows),"verified_cc0_count":verified,"verified_original_count":original,"unverified_count":unverified,"release_blocked":unverified>0},"assets":rows}

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--assets-root",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--require-verified",action="store_true")
    args=parser.parse_args()
    try: ledger=build_ledger(args.assets_root)
    except (OSError,ValueError) as error: raise SystemExit(f"ASSET_PROVENANCE_ERROR: {error}")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(ledger,indent=2,sort_keys=True)+chr(10),encoding="utf-8")
    summary=ledger["summary"]
    print(f"ASSET_PROVENANCE_LEDGER_OK assets={summary['binary_asset_count']} verified_cc0={summary['verified_cc0_count']} unverified={summary['unverified_count']} release_blocked={str(summary['release_blocked']).lower()}")
    if args.require_verified and summary["unverified_count"]:
        raise SystemExit("RELEASE_BLOCKED: retained assets have unresolved license/provenance records")

if __name__=="__main__": main()
