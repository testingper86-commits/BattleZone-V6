#!/usr/bin/env python3
"""Structural and source-integrity regression for Character 03 rig output."""
import hashlib, json, struct, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from rig_character03 import parse_glb, read_accessor

def check(source, rigged):
    original, obin = parse_glb(source.read_bytes())
    doc, binary = parse_glb(rigged.read_bytes())
    skin = doc.get("skins", [])
    assert len(skin) == 1 and len(skin[0]["joints"]) == 21
    names = [a["name"] for a in doc.get("animations", [])]
    assert names == ["Idle","Walk","Run","Crouch","Fight","Punch","Shoot","Emote"]
    attrs = doc["meshes"][0]["primitives"][0]["attributes"]
    assert {"POSITION","NORMAL","TEXCOORD_0","JOINTS_0","WEIGHTS_0"} <= set(attrs)
    weights = read_accessor(doc,binary,attrs["WEIGHTS_0"])
    joints = read_accessor(doc,binary,attrs["JOINTS_0"])
    assert weights.shape[1] == 4 and joints.shape == weights.shape
    assert np.isfinite(weights).all() and np.all(weights >= 0)
    assert np.max(np.abs(weights.sum(axis=1)-1.0)) < 1e-5
    assert int(joints.max()) < len(skin[0]["joints"])
    # Bind-pose identity: every joint global rest transform must cancel its inverse bind matrix.
    skin = doc["skins"][0]
    nodes = doc["nodes"]
    parent_of = {}
    def visit(node, parent=None):
        parent_of[node] = parent
        for child in nodes[node].get("children", []): visit(child, node)
    visit(doc["scenes"][0]["nodes"][0])
    ibm = read_accessor(doc, binary, skin["inverseBindMatrices"]).reshape(-1, 4, 4)
    for index, node_id in enumerate(skin["joints"]):
        translation = np.zeros(3, dtype=np.float64); current = node_id
        while current is not None:
            translation += np.asarray(nodes[current].get("translation", [0, 0, 0]), dtype=np.float64)
            current = parent_of.get(current)
        global_matrix = np.eye(4, dtype=np.float64); global_matrix[:3, 3] = translation
        inverse_bind = np.asarray(ibm[index], dtype=np.float64).T
        assert np.max(np.abs(global_matrix @ inverse_bind - np.eye(4))) < 1e-5, nodes[node_id]["name"]
    for key in ("POSITION","NORMAL","TEXCOORD_0"):
        assert read_accessor(original,obin,original["meshes"][0]["primitives"][0]["attributes"][key]).tobytes() == read_accessor(doc,binary,attrs[key]).tobytes()
    assert original["images"] == doc["images"]
    for image in original["images"]:
        a=original["bufferViews"][image["bufferView"]];b=doc["bufferViews"][image["bufferView"]]
        assert obin[a.get("byteOffset",0):a.get("byteOffset",0)+a["byteLength"]] == binary[b.get("byteOffset",0):b.get("byteOffset",0)+b["byteLength"]]
    print(json.dumps({"vertices":len(weights),"joints":len(skin[0]["joints"]),"clips":names,"maxWeightSumError":float(np.max(np.abs(weights.sum(axis=1)-1))),"sourceSha256":hashlib.sha256(source.read_bytes()).hexdigest(),"riggedSha256":hashlib.sha256(rigged.read_bytes()).hexdigest(),"meshAndEmbeddedImages":"byte-identical"},indent=2))

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: test_character03_rigging.py source.glb rigged.glb")
    check(Path(sys.argv[1]),Path(sys.argv[2]))
