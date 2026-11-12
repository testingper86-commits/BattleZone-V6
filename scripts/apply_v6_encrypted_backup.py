#!/usr/bin/env python3
"""Replace reversible local backup codes with authenticated passphrase encryption."""
from pathlib import Path
import sys

MARKER = "BATTLEZONE_V6_ENCRYPTED_BACKUP_V1"
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
path = files[0]
source = path.read_text(encoding="utf-8")
if MARKER in source:
    if "PBKDF2-SHA256" not in source or "AES-256-GCM" not in source:
        raise SystemExit("Encrypted backup marker exists but implementation is incomplete")
    print(MARKER + " already applied")
    raise SystemExit(0)
start = "// ---- backup / restore\n"
end = "// ---- loop wrapper:"
if source.count(start) != 1:
    raise SystemExit("Could not find unique backup/restore section")
section_start = source.index(start)
section_end = source.find(end, section_start)
if section_end < 0:
    raise SystemExit("Could not find backup/restore section boundary")
old_section = source[section_start:section_end]
keys_lines = [line for line in old_section.splitlines() if line.startswith("const KEYS=")]
if len(keys_lines) != 1:
    raise SystemExit("Could not preserve the existing local backup key allowlist")
keys_line = keys_lines[0]
helper = r"""/* BATTLEZONE_V6_ENCRYPTED_BACKUP_V1_BEGIN */
const BZBackupCrypto = (() => {
 const FORMAT='BZOFFLINEBACKUP', VERSION=1, ITERATIONS=310000, MAX_DATA_BYTES=8*1024*1024, MAX_CODE_CHARS=12*1024*1024;
 const toB64=bytes=>{let binary='';for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));return btoa(binary)};
 const fromB64=value=>{if(typeof value!=='string'||value.length>MAX_CODE_CHARS)throw new Error('Invalid backup field');const binary=atob(value);const bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return bytes};
 const derive=async(passphrase,salt,usage)=>{if(typeof passphrase!=='string'||passphrase.length<12||passphrase.length>256)throw new Error('Passphrase must contain 12 to 256 characters');const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(passphrase),'PBKDF2',false,['deriveKey']);return crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:ITERATIONS,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,[usage])};
 return Object.freeze({
  async encrypt(data,passphrase){
   if(!data||typeof data!=='object'||Array.isArray(data))throw new Error('Backup data must be an object');
   const plain=new TextEncoder().encode(JSON.stringify({version:VERSION,data}));
   if(plain.length>MAX_DATA_BYTES)throw new Error('Backup is too large');
   const salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
   const key=await derive(passphrase,salt,'encrypt');
   const encrypted=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv,tagLength:128},key,plain));
   const payload={format:FORMAT,version:VERSION,kdf:'PBKDF2-SHA256',iterations:ITERATIONS,cipher:'AES-256-GCM',salt:toB64(salt),iv:toB64(iv),ciphertext:toB64(encrypted)};
   return toB64(new TextEncoder().encode(JSON.stringify(payload)));
  },
  async decrypt(code,passphrase){
   if(typeof code!=='string'||code.length>MAX_CODE_CHARS)throw new Error('Invalid backup code');
   const raw=fromB64(code.trim());
   const payload=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
   if(!payload||payload.format!==FORMAT||payload.version!==VERSION||payload.kdf!=='PBKDF2-SHA256'||payload.iterations!==ITERATIONS||payload.cipher!=='AES-256-GCM')throw new Error('Unsupported backup format');
   const salt=fromB64(payload.salt),iv=fromB64(payload.iv),ciphertext=fromB64(payload.ciphertext);
   if(salt.length!==16||iv.length!==12||ciphertext.length<16||ciphertext.length>MAX_DATA_BYTES+16)throw new Error('Invalid encrypted backup fields');
   const key=await derive(passphrase,salt,'decrypt');
   const plain=await crypto.subtle.decrypt({name:'AES-GCM',iv,tagLength:128},key,ciphertext);
   const decoded=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(plain));
   if(!decoded||decoded.version!==VERSION||!decoded.data||typeof decoded.data!=='object'||Array.isArray(decoded.data))throw new Error('Invalid decrypted backup payload');
   return decoded.data;
  }
 });
})();
/* BATTLEZONE_V6_ENCRYPTED_BACKUP_V1_END */"""
handler = r"""$('bak').onclick=()=>sheet('Backup progress',['Create encrypted code','Restore encrypted code'],-1,async i=>{
 if(i===0){
  const pass=prompt('Create a backup passphrase (12 to 256 characters). Keep it separate from the backup code.');if(!pass)return;
  try{const o={};KEYS.forEach(k=>{const v=sg(k);if(v!=null)o[k]=v});const code=await BZBackupCrypto.encrypt(o,pass);if(navigator.clipboard&&navigator.clipboard.writeText){try{await navigator.clipboard.writeText(code);alert('Encrypted backup copied. Your passphrase was not saved.')}catch(e){prompt('Copy this encrypted backup code',code)}}else prompt('Copy this encrypted backup code',code)}catch(e){alert('Backup encryption failed. Check available storage and use a 12+ character passphrase.')}
 }else{
  const code=prompt('Paste the encrypted backup code');if(!code)return;const pass=prompt('Enter the backup passphrase');if(!pass)return;
  try{const restored=await BZBackupCrypto.decrypt(code,pass);const entries=Object.entries(restored);if(entries.some(([k,v])=>!KEYS.includes(k)||typeof v!=='string'))throw new Error('Backup contains unsupported values');const before={};KEYS.forEach(k=>{before[k]=sg(k)});try{entries.forEach(([k,v])=>ss(k,v))}catch(writeError){KEYS.forEach(k=>{try{if(before[k]==null)localStorage.removeItem(k);else localStorage.setItem(k,before[k])}catch(rollbackError){}});throw writeError}location.reload()}catch(e){alert('Backup could not be restored. Check the code and passphrase. Existing progress was not intentionally overwritten.')}
 }
},'AES-256-GCM authenticated encryption; PBKDF2-SHA256 passphrase key derivation.');"""
new_section = "// ---- encrypted backup / restore" + "\n" + keys_line + "\n" + helper + "\n" + handler + "\n"
source = source[:section_start] + new_section + source[section_end:]
if source.count(MARKER + "_BEGIN") != 1 or source.count(MARKER + "_END") != 1:
    raise SystemExit("Encrypted backup marker insertion failed")
path.write_text(source, encoding="utf-8")
print(MARKER + " applied", path)
