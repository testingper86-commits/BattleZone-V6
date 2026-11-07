#!/usr/bin/env python3
"""Behavioral Node regression tests for tactical raycasts and enemy target visibility."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
paths = list(root.rglob('app/src/main/assets/www/index.html'))
if len(paths) != 1:
    raise SystemExit(f'Expected exactly one game index.html, found {len(paths)}')
source = paths[0].read_text(encoding='utf-8')

def extract_function(name):
    marker = f'function {name}('
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'Missing runtime function: {name}')
    brace = source.find('{', start)
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n': line_comment = False
        elif block_comment:
            if ch == '*' and nxt == '/': block_comment = False; i += 1
        elif quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
        elif ch == '/' and nxt == '/': line_comment = True; i += 1
        elif ch == '/' and nxt == '*': block_comment = True; i += 1
        elif ch in ('\\"', "'", '`'): quote = ch
        elif ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return source[start:i + 1]
        i += 1
    raise SystemExit(f'Unterminated runtime function: {name}')

functions = '\n'.join(extract_function(n) for n in ('hasClearShot', 'bzV6TargetIsValid', 'bzV6ChooseEnemyTarget', 'bzV6ValidateSquadTarget'))
script = r"""const assert = require('assert');
let rayBlocked = false;
class Vector3 { constructor(x,y,z){this.x=x;this.y=y;this.z=z} normalize(){return this} }
class Raycaster { constructor(origin,direction,near,far){this.origin=origin;this.direction=direction;this.near=near;this.far=far} intersectObjects(){return rayBlocked?[{distance:1}]:[]} }
const THREE={Vector3,Raycaster};
const solid=[];
const P={alive:true,air:0,x:10,z:0,y:1.6,hp:100};
const DF=1,ENV={vis:1},BZ_MODE='BR';
let actors=[];
const forEachActor=fn=>actors.forEach(fn);
const rnd=(a,b)=>a;
const smk=()=>false;
__FUNCTIONS__
assert.strictEqual(hasClearShot(0,0,0,NaN,0,0),false,'non-finite endpoints must never be a clear shot');
assert.strictEqual(hasClearShot(0,0,0,0,0,0),true,'near-zero finite segments should remain clear');
rayBlocked=true;
assert.strictEqual(hasClearShot(0,0,0,5,0,0),false,'solid cover must block the shot');
rayBlocked=false;
hasClearShot=(ax,ay,az,bx,by,bz)=>bx!==10;
const bot={position:{x:0,y:0,z:0}};
const visibleEnemy={position:{x:8,y:0,z:0},userData:{alive:true,ally:false,hp:100}};
actors=[visibleEnemy];
const state={aiScanT:0,aiTarget:null,aiAlert:0};
const first=bzV6ChooseEnemyTarget(bot,state,.016);
assert.strictEqual(first.target,null,'bot must not lock a player hidden behind cover');
assert.strictEqual(state.aiBlockedPlayer,true,'occluded player must enter the temporary blocked-target cache');
assert(state.aiBlockedT>0,'occluded player cooldown must be bounded and active');
const second=bzV6ChooseEnemyTarget(bot,state,.2);
assert.strictEqual(second.target&&second.target.o,visibleEnemy,'bot must skip the blocked player and acquire another visible enemy');
let squadRayChecks=0;
hasClearShot=()=>{squadRayChecks++;return false};
const ally={position:{x:0,y:0,z:0}},squadEnemy={position:{x:5,y:0,z:0}},squadState={squadBlockedTarget:null,squadBlockedT:0,squadLosT:0};
assert.strictEqual(bzV6ValidateSquadTarget(ally,squadState,squadEnemy),null,'squad must not pursue an occluded enemy');
assert.strictEqual(squadState.squadBlockedTarget,squadEnemy,'occluded squad target must be cached');
const blockedChecks=squadRayChecks;
assert.strictEqual(bzV6ValidateSquadTarget(ally,squadState,squadEnemy),null,'blocked squad target remains suppressed during cooldown');
assert.strictEqual(squadRayChecks,blockedChecks,'blocked squad target must not trigger repeated raycasts');
squadState.squadBlockedT=0;squadState.squadLosT=0;hasClearShot=()=>true;
assert.strictEqual(bzV6ValidateSquadTarget(ally,squadState,squadEnemy),squadEnemy,'squad can reacquire the target when line of sight returns');
console.log('TACTICAL_LINE_OF_SIGHT_BEHAVIOR_OK checks=11');
""".replace('__FUNCTIONS__', functions)
with tempfile.TemporaryDirectory(prefix='bz-los-') as tmp:
    js = Path(tmp) / 'tactical-los.test.js'
    js.write_text(script, encoding='utf-8')
    result = subprocess.run(['node', str(js)], capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr or result.stdout or 'Node tactical LOS tests failed')
    print(result.stdout.strip())
