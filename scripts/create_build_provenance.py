#!/usr/bin/env python3
"""Create deterministic provenance for the transformed WILDBOUND Android source tree."""
from __future__ import annotations
import argparse, hashlib, json, os, re
from pathlib import Path

EXCLUDED_PARTS = {".git", ".gradle", ".kotlin", "build"}

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def tree_digest(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root)
        if path.name == "BUILD_PROVENANCE.json" or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        rel = relative.as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(8, "big")); digest.update(rel)
        size = path.stat().st_size
        digest.update(size.to_bytes(8, "big"))
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        count += 1
    return digest.hexdigest(), count

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--workflow", required=True, type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive, source, workflow = args.archive.resolve(), args.source.resolve(), args.workflow.resolve()
    if not archive.is_file() or not source.is_dir() or not workflow.is_file():
        raise SystemExit("Archive, transformed source directory, or workflow file is missing")
    text = workflow.read_text(encoding="utf-8")
    chain = re.findall(r'python3\s+scripts/(apply_[A-Za-z0-9_]+\.py)\s+(?:_cloud_source|"\$project_dir")', text)
    if not chain or len(chain) != len(set(chain)):
        raise SystemExit("Workflow patch chain is empty or contains duplicate patcher invocations")
    patchers = []
    for index, name in enumerate(chain, 1):
        path = workflow.parent.parent.parent / "scripts" / name
        if not path.is_file():
            raise SystemExit(f"Workflow references missing patcher: {name}")
        patchers.append({"order": index, "path": f"scripts/{name}", "sha256": sha256_file(path)})
    source_hash, file_count = tree_digest(source)
    manifest = {
        "schema_version": 1,
        "git_commit": args.commit,
        "canonical_source_archive": {"path": archive.name, "size_bytes": archive.stat().st_size, "sha256": sha256_file(archive)},
        "patch_chain": patchers,
        "transformed_source": {"sha256": source_hash, "file_count": file_count, "hash_algorithm": "sha256-path-size-content-v1"},
    }
    output = (args.output or source / "BUILD_PROVENANCE.json").resolve()
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as stream:
            stream.write(f"source_sha256={source_hash}\n")
            stream.write(f"artifact_name=WILDBOUND-Offline-Patched-Source-{source_hash[:16]}\n")
    print(f"BUILD_PROVENANCE_OK archive_sha256={manifest['canonical_source_archive']['sha256']} source_sha256={source_hash} files={file_count} patchers={len(patchers)}")

if __name__ == "__main__":
    main()
