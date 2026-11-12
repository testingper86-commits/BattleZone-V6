#!/usr/bin/env python3
"""Static and WebCrypto round-trip/tamper tests for offline backups."""
from pathlib import Path
import json, re, subprocess, sys, tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
files=list(root.rglob("app/src/main/assets/www/index.html"))
if len(files)!=1: raise SystemExit(f"Expected one game index.html, found {len(files)}")
html=files[0].read_text(encoding="utf-8")
checks={
 "encrypted backup marker": "BATTLEZONE_V6_ENCRYPTED_BACKUP_V1" in html,
 "AES-256-GCM authenticated cipher": "AES-256-GCM" in html and "AES-GCM" in html,
 "PBKDF2-SHA256 key derivation": "PBKDF2-SHA256" in html and "iterations:ITERATIONS" in html,
 "fresh random salt and IV": "crypto.getRandomValues(new Uint8Array(16))" in html and "crypto.getRandomValues(new Uint8Array(12))" in html,
 "passphrase never stored": "Your passphrase was not saved" in html,
 "existing backup allowlist retained": "const KEYS=['bzp','bzProfile','bzOfflineMatchHistory','bzDoctrine'" in html,
 "restore rejects unknown keys and non-string values": "!KEYS.includes(k)||typeof v!=='string'" in html,
 "reversible base64 backup removed": "btoa(unescape(encodeURIComponent(JSON.stringify(o))))" not in html and "decodeURIComponent(escape(atob(c.trim())))" not in html,
}
for name,ok in checks.items(): print(("PASS " if ok else "FAIL ")+name)
if not all(checks.values()): raise SystemExit("Encrypted backup static checks failed")
helper=html.split("/* BATTLEZONE_V6_ENCRYPTED_BACKUP_V1_BEGIN */",1)[1].split("/* BATTLEZONE_V6_ENCRYPTED_BACKUP_V1_END */",1)[0]
if not helper: raise SystemExit("Encrypted backup helper block missing")

harness=r"""const {webcrypto}=require('node:crypto');
const {TextEncoder,TextDecoder}=require('node:util');
globalThis.crypto=webcrypto;globalThis.TextEncoder=TextEncoder;globalThis.TextDecoder=TextDecoder;
globalThis.btoa=s=>Buffer.from(s,'binary').toString('base64');globalThis.atob=s=>Buffer.from(s,'base64').toString('binary');
__HELPER__
globalThis.BZ= BZBackupCrypto;
(async()=>{
 const pass='correct horse battery staple';
 const data={bzp:JSON.stringify({c:12345,k:9}),bzProfile:JSON.stringify({name:'Cipher Δ',level:12}),bzOfflineMatchHistory:'[1,2,3]',bzDoctrine:'aggressive'};
 const a=await BZ.encrypt(data,pass),b=await BZ.encrypt(data,pass);
 if(a===b)throw new Error('salt/IV reuse produced identical backup codes');
 if(a.includes('12345')||a.includes('Cipher'))throw new Error('plaintext leaked into backup code');
 const restored=await BZ.decrypt(a,pass);
 if(JSON.stringify(restored)!==JSON.stringify(data))throw new Error('round trip mismatch');
 let wrong=false;try{await BZ.decrypt(a,'incorrect horse battery staple')}catch(e){wrong=true}if(!wrong)throw new Error('wrong passphrase accepted');
 let short=false;try{await BZ.encrypt(data,'short')}catch(e){short=true}if(!short)throw new Error('short passphrase accepted');
 const payload=JSON.parse(Buffer.from(a,'base64').toString('utf8'));
 const raw=Buffer.from(payload.ciphertext,'base64');raw[0]^=1;payload.ciphertext=raw.toString('base64');
 let tamper=false;try{await BZ.decrypt(Buffer.from(JSON.stringify(payload)).toString('base64'),pass)}catch(e){tamper=true}if(!tamper)throw new Error('tampered ciphertext accepted');
 payload.version=99;let version=false;try{await BZ.decrypt(Buffer.from(JSON.stringify(payload)).toString('base64'),pass)}catch(e){version=true}if(!version)throw new Error('unknown backup version accepted');
 console.log('ENCRYPTED_BACKUP_WEBCRYPTO_TESTS_OK');
})().catch(e=>{console.error(e);process.exit(1)});
"""
harness=harness.replace('__HELPER__',helper)
with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f: f.write(harness); js=f.name
try:
 r=subprocess.run(['node',js],capture_output=True,text=True,timeout=30)
 print(r.stdout,end=''); print(r.stderr,end='',file=sys.stderr)
 if r.returncode: raise SystemExit(r.returncode)
finally: Path(js).unlink(missing_ok=True)
print('ENCRYPTED_BACKUP_STATIC_CHECKS_OK')
