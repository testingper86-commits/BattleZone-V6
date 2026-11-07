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

def build_ledger(assets_root:Path)->dict:
    root=assets_root.resolve()
    if not root.is_dir(): raise ValueError(f"Asset root does not exist: {root}")
    voice_verified,voice_evidence=verified_voice_files(root)
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
        rows.append({"path":rel,"size_bytes":path.stat().st_size,"sha256":sha256_file(path),"license":license_name,"status":status,"evidence":evidence,"note":note})
    verified=sum(row["status"]=="verified_cc0" for row in rows)
    unverified=len(rows)-verified
    return {"schema_version":1,"asset_root":"app/src/main/assets/www","hash_algorithm":"sha256","summary":{"binary_asset_count":len(rows),"verified_cc0_count":verified,"unverified_count":unverified,"release_blocked":unverified>0},"assets":rows}

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
