#!/usr/bin/env python3
"""Regression checks for deterministic procedural operator equipment variants."""
from pathlib import Path
import json, subprocess, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
paths=list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths)!=1: raise SystemExit(f'Expected one index.html, found {len(paths)}')
s=paths[0].read_text(encoding='utf-8')
checks={
 'operator gear marker':'BATTLEZONE_V6_OPERATOR_GEAR_VARIANTS_V1' in s,
 'eight equipment silhouettes':'if(gearStyle===0)' in s and 'else if(gearStyle===7)' in s and s.count('else if(gearStyle===')==7,
 'headwear varies by operator':'if(lk.cap&&gearStyle===0)' in s,
 'gear attaches to articulated head, torso and pack':'mk(hd,' in s and 'mk(torso,' in s and 'mk(cl,' in s,
 'gear style is retained on the actor':'sc.gearStyle=gearStyle;' in s,
}
for label,ok in checks.items():
 print(('PASS ' if ok else 'FAIL ')+label)
 if not ok: raise SystemExit(1)
a=s.find('const BZ_CHAR_DATA={'); b=s.find('function bzSelectedCharacter',a); c=s.find('function bzOperatorGearStyle('); d=s.find('function mkScout(',c)
if min(a,b,c,d)<0: raise SystemExit('Operator catalog or gear selector missing')
js=f"""const vm=require('node:vm');const c={{}};vm.createContext(c);vm.runInContext({json.dumps(s[a:b]+s[c:d])}+';globalThis.operatorNames=Object.keys(BZ_CHAR_DATA);globalThis.operatorStyles=operatorNames.map(bzOperatorGearStyle);',c);const names=c.operatorNames,styles=c.operatorStyles;if(names.length!==17)throw Error('expected 17 operator profiles');if(new Set(styles).size!==8)throw Error('expected eight gear styles');if(styles.some(x=>!Number.isInteger(x)||x<0||x>7))throw Error('invalid gear style');if(vm.runInContext("bzOperatorGearStyle('Unknown Operator')",c)!==0)throw Error('unknown operator fallback must be deterministic');"""
r=subprocess.run(['node','-e',js],capture_output=True,text=True)
if r.returncode: raise SystemExit(r.stderr or r.stdout)
print('PASS 17 operator profiles map deterministically to eight gear silhouettes')
