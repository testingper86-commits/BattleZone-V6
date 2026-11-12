#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile
SCRIPT = Path(__file__).with_name("create_build_provenance.py")
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp); source=root/"project"; source.mkdir()
    (source/"app.txt").write_text("source-v1",encoding="utf-8")
    archive=root/"canonical.zip"; archive.write_bytes(b"canonical-input")
    scripts=root/"scripts"; scripts.mkdir(); (scripts/"apply_first.py").write_text("first",encoding="utf-8")
    workflow=root/".github/workflows/android-build.yml"; workflow.parent.mkdir(parents=True); workflow.write_text("python3 scripts/apply_first.py _cloud_source\n",encoding="utf-8")
    out=source/"BUILD_PROVENANCE.json"
    subprocess.run([sys.executable,str(SCRIPT),"--archive",str(archive),"--source",str(source),"--workflow",str(workflow),"--commit","test-sha","--output",str(out)],check=True,capture_output=True,text=True)
    data=json.loads(out.read_text())
    assert data["git_commit"]=="test-sha" and data["canonical_source_archive"]["sha256"] and data["transformed_source"]["file_count"]==1
    first=data["transformed_source"]["sha256"]
    (source/"app.txt").write_text("source-v2",encoding="utf-8")
    subprocess.run([sys.executable,str(SCRIPT),"--archive",str(archive),"--source",str(source),"--workflow",str(workflow),"--commit","test-sha","--output",str(out)],check=True,capture_output=True,text=True)
    assert json.loads(out.read_text())["transformed_source"]["sha256"] != first
print("BUILD_PROVENANCE_FIXTURE_TESTS_OK")
