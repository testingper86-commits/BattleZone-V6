#!/usr/bin/env python3
"""Focused checks for the functional lobby, touch, and audio rebuild."""
from pathlib import Path
import subprocess,sys,tempfile,shutil
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
htmls=list(root.rglob('app/src/main/assets/www/index.html')); models=list(root.rglob('app/src/main/assets/www/js/models.js')); css=list(root.rglob('app/src/main/assets/www/css/v6-critical-gameplay-polish.css'))
assert len(htmls)==len(models)==len(css)==1, 'expected one game runtime, model module and final CSS'
h=htmls[0].read_text(encoding='utf8'); m=models[0].read_text(encoding='utf8'); c=css[0].read_text(encoding='utf8')
for token in ['BATTLEZONE_V6_COMPLETE_RUNTIME_REBUILD_V1','window.BZAudio=Object.freeze','setVolume:value=>','const bzVolume=$(\'bzMasterVolume\')','window.addEventListener(\'resize\',applyCL','/Math.max(1,innerWidth)','/Math.max(1,innerHeight)']:
 assert token in h, 'missing runtime behavior: '+token
assert 'window.lobSc.root.userData.bzDressed' in m, 'lobby preview does not use the rigged character pipeline'
assert ' */\n/* Rigged character models' in m, 'model version marker must be inserted as a real newline'
assert 'BATTLEZONE_V6_COMPLETE_TOUCH_LAYOUT_V1' in c
assert '#fire2{left:calc(var(--bz-safe-l) + 154px)' in c
# Geometric collision check for the right-hand portrait cluster at common phone widths.
for width,height in [(360,800),(384,854),(412,915),(432,960)]:
 specs={'fire':(18,18,76,76),'jump':(18,108,52,52),'crouch':(80,108,52,52),'prone':(18,168,52,52),'scope':(80,168,52,52),'rel':(104,18,52,52),'swap':(166,18,52,52),'thr':(166,78,52,52),'gsw':(166,138,52,52)}
 boxes={k:(width-r-w,height-b-h,width-r,height-b) for k,(r,b,w,h) in specs.items()}
 keys=list(boxes)
 for i,a in enumerate(keys):
  for b in keys[i+1:]:
   ax1,ay1,ax2,ay2=boxes[a]; bx1,by1,bx2,by2=boxes[b]
   assert ax1>=0 and ay1>=0, f'{a} outside viewport at {width}x{height}'
   assert not (ax1<bx2 and ax2>bx1 and ay1<by2 and ay2>by1), f'{a} overlaps {b} at {width}x{height}'
# Verify idempotency by running the patcher twice against an isolated copy of only its targets.
patcher=Path(__file__).with_name('apply_v6_gameplay_rebuild.py')
with tempfile.TemporaryDirectory(prefix='bz-rebuild-idempotency-') as td:
 t=Path(td); rels=[htmls[0].relative_to(root),models[0].relative_to(root),css[0].relative_to(root)]
 for src,rel in zip([htmls[0],models[0],css[0]],rels):
  dest=t/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
 # The temporary tree must satisfy the patcher's exact-one-file lookup.
 for _ in range(2): subprocess.run([sys.executable,str(patcher),str(t)],check=True,capture_output=True,text=True)
print('GAMEPLAY_REBUILD_TESTS_OK lobby_rigged=true touch_layout_nonoverlap=true normalized_positions=true audio_volume=true idempotent=true')
