#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,tempfile
patcher=Path(__file__).with_name("apply_v6_edge_control_system.py")
fixture='<html><head></head><body><div id="lobby"></div><div id="ced"></div><div id="joy"></div><div class="b" id="fire"></div><div class="b" id="jump"></div><div id="hp"></div><div id="wp"></div><div id="bzSquadOrders"></div></body></html>'
with tempfile.TemporaryDirectory() as td:
 root=Path(td); h=root/"app/src/main/assets/www/index.html"; h.parent.mkdir(parents=True); h.write_text(fixture)
 subprocess.run([sys.executable,str(patcher),str(root)],check=True)
 out=h.read_text(); c=(h.parent/"css/v6-edge-control-system.css").read_text()
 assert "BATTLEZONE_V6_EDGE_CONTROL_SYSTEM_V3" in out
 assert "not([data-bz-screen=\"gameplay\"])" in c
 for token in ("#joy{","#fire{","#jump{","#bzSquadOrders{","#wp{","orientation:portrait","safe-area-inset-left"):
  assert token in c,token
 old=out; subprocess.run([sys.executable,str(patcher),str(root)],check=True); assert h.read_text()==old
print("EDGE_CONTROL_SYSTEM_TESTS_OK")
