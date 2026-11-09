#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,tempfile
patcher=Path(__file__).with_name("apply_v6_pubg_hud.py")
with tempfile.TemporaryDirectory() as td:
 root=Path(td); h=root/"app/src/main/assets/www/index.html";h.parent.mkdir(parents=True)
 h.write_text("<html><head></head><body><div id='lobby'></div><div id='ced'></div><div id='joy'></div><div class='b' id='fire'></div><div id='bzSquadOrders'></div></body></html>")
 subprocess.run([sys.executable,str(patcher),str(root)],check=True)
 original=h.read_text(); c=(h.parent/"css/v6-pubg-hud.css").read_text()
 assert "BATTLEZONE_V6_PUBG_HUD_V1" in original
 for x in ('data-bz-screen="gameplay"','data-bz-screen="controls-edit"','#joy{','#fire{','#bzSquadOrders{','#wp{','orientation:portrait','orientation:landscape','safe-area-inset-bottom'):
  assert x in c,x
 subprocess.run([sys.executable,str(patcher),str(root)],check=True)
 assert h.read_text()==original
print("PUBG_HUD_TESTS_OK idempotent=true gameplay_lobby_isolation=true responsive_layout=true editor_style=true")
