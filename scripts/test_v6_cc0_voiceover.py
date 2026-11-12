#!/usr/bin/env python3
"""Verify the exact bundled Kenney CC0 tactical voice subset and runtime wiring."""
from pathlib import Path
import hashlib
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
index=root/'app/src/main/assets/www/index.html'
if not index.is_file(): raise SystemExit('Expected game index.html at the canonical Android asset path')
www=index.parent;audio=www/'audio'/'cc0_voiceover'
lines=['war_call_for_backup','war_cover_me','war_fire_in_the_hole','war_get_down','war_go_go_go','war_look_out','war_medic','war_reloading','war_rpg','war_sniper','war_suppressing_fire','war_target_destroyed','war_target_engaged','war_watch_my_back','mission_completed','mission_failed','you_win','you_lose','ready','go','hurry_up','objective_achieved']
expected={f'{gender}/{line}.ogg' for gender in ('Male','Female') for line in lines}
manifest={}
for row in (audio/'manifest.sha256').read_text(encoding='utf-8').splitlines():
    parts=row.split()
    if len(parts)!=2: raise SystemExit('Malformed bundled voice manifest')
    manifest[parts[1]]=parts[0]
if set(manifest)!=expected: raise SystemExit(f'Expected exactly 44 voice manifest entries, got {len(manifest)}')
ogg_ok=True;hash_ok=True
for rel,digest in manifest.items():
    f=audio/rel
    if not f.is_file(): raise SystemExit(f'Missing CC0 voice file: {rel}')
    data=f.read_bytes()
    ogg_ok=ogg_ok and data.startswith(b'OggS')
    hash_ok=hash_ok and hashlib.sha256(data).hexdigest()==digest
license_text=(audio/'License.txt').read_text(encoding='utf-8')
credits=(audio/'Credits.txt').read_text(encoding='utf-8')
provenance=(audio/'PROVENANCE.md').read_text(encoding='utf-8')
html=index.read_text(encoding='utf-8')
checks={
 '44 exact OGG files are present':len(manifest)==44,
 'all OGG streams and SHA-256 hashes match':ogg_ok and hash_ok,
 'original CC0 1.0 licence is bundled':'Creative Commons Zero, CC0' in license_text and 'publicdomain/zero/1.0' in license_text,
 'performer credits are preserved':'Jeffrey M. Smith' in credits and 'Giselle' in credits,
 'source archive hash is documented':'2ff0c8c51a959a754df698c4ee1e7c2db007c4abde4d600fd19545a1aea9d835' in provenance,
 'unverified synthetic voicepacks are excluded from package':not (www/'audio'/'voicepacks').exists(),
 'runtime plays local CC0 OGG files':'audio/cc0_voiceover/' in html and 'function bzPlayCC0VoiceLine' in html,
 'voice events map to tactical callouts':'war_target_engaged' in html and 'war_reloading' in html and 'war_cover_me' in html and 'you_win' in html and 'you_lose' in html,
 'female suppressing-fire source filename is normalized':"gender==='Female'&&line==='war_suppressing_fire'?'war_supressing_fire':line" in html,
 'CC0 voice marker is present':'BATTLEZONE_V6_CC0_VOICEOVER_V1' in html,
}
failed=[]
for name,ok in checks.items():
    print(('PASS ' if ok else 'FAIL ')+name)
    if not ok: failed.append(name)
if failed: raise SystemExit(f'{len(failed)} CC0 voice checks failed')
print(f'BATTLEZONE_V6_CC0_VOICEOVER_OK checks={len(checks)}')
