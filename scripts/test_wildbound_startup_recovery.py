#!/usr/bin/env python3
"""Verify WILDBOUND always reveals its real lobby and recovers visibly from startup errors."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
paths = {
    "runtime": root / "app/src/main/assets/www/js/wildbound/rendering/runtime.js",
    "boot": root / "app/src/main/assets/www/js/wildbound/frontend/boot.js",
    "css": root / "app/src/main/assets/www/css/wildbound.css",
    "activity": root / "app/src/main/java/com/example/battlezone/MainActivity.kt",
}
for key, path in paths.items():
    if not path.is_file():
        raise SystemExit(f"Missing {key} file: {path}")
runtime, boot, css, activity = (paths[k].read_text() for k in ("runtime", "boot", "css", "activity"))
checks = {
    "startup recovery is installed in all final runtime files": all("WILDBOUND_STARTUP_RECOVERY_V1" in p.read_text() for p in paths.values()),
    "lobby is revealed before WebGL initialization": boot.index("revealLobby();") < boot.index("W.main.initialize();"),
    "renderer failure cannot leave the splash as the only screen": "the 3D renderer could not initialize" in boot,
    "UI controls initialize independently of WebGL": "W.main.ensureUi=()=>{if(!uiInitialized){W.ui.init(game);uiInitialized=true}}" in runtime and "W.ui.init(game);;W.bus.on" not in runtime,
    "missing Three.js produces an explicit diagnostic": "The bundled Three.js engine did not load" in runtime,
    "partial renderer state is cleaned after failure": "game.renderer=null;game.scene=null;game.camera=null" in runtime,
    "deployment failure restores the real lobby": "the hunt could not initialize" in boot,
    "startup errors are visible and retryable": "startup-status-detail" in boot and "startup-status.visible" in css and "RETRY STARTUP" in boot,
    "Android main-document errors are handled": "onReceivedError" in activity and "onReceivedHttpError" in activity and "showDocumentFailure" in activity,
    "Android error page retries the bundled offline game": "RETRY GAME STARTUP" in activity and "assets/www/index.html" in activity,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)
if not all(checks.values()):
    raise SystemExit("WILDBOUND_STARTUP_RECOVERY_STATIC_FAILED")
for key in ("runtime", "boot"):
    result = subprocess.run(["node", "--check", str(paths[key])], capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(f"{key} JavaScript syntax failed:\n{result.stderr}")
print("PASS runtime and boot JavaScript syntax")

node_test = r"""
const fs=require('fs'),vm=require('vm');
function element(id){
 const classes=new Set(id==='lobby'?['hidden']:[]);
 return {id,tagName:'DIV',dataset:{},style:{},className:'',textContent:'',children:[],onclick:null,
  classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},
  setAttribute(){},append(...items){this.children.push(...items);for(const x of items)x.parent=this},
  appendChild(x){this.children.push(x);x.parent=this;return x},
  querySelector(sel){return this.children.find(x=>sel==='.startup-status-copy'?x.className==='startup-status-copy':sel==='.startup-status-detail'?x.className==='startup-status-detail':false)||null},
  addEventListener(type,fn){this['on_'+type]=fn},
  get visible(){return !classes.has('hidden')}
 };
}
const els={boot:element('boot'),lobby:element('lobby'),game:element('game'),deploy:element('deploy')};
const document={readyState:'complete',getElementById:id=>els[id]||els.lobby.children.find(x=>x.id===id)||null,createElement:tag=>{const x=element(tag);x.tagName=tag.toUpperCase();return x},addEventListener(){}};
const window={location:{reload(){window.reloaded=true}},addEventListener(){}};
const W={state:{screen:'boot'},ui:{init(){els.deploy.onclick=()=>W.main.start()},refresh(){}},main:{game:{},initialize(){throw new Error('WebGLRenderer unavailable')},ensureUi(){W.ui.init(W.main.game)},start(){throw new Error('WebGL context creation failed')}}};
window.WILDBOUND=W;const sandbox={window,document,console,WILDBOUND:W};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),sandbox);
if(els.boot.visible)throw Error('splash remained visible');
if(!els.lobby.visible)throw Error('real lobby was not revealed');
if(els.game.visible)throw Error('game screen shown without renderer');
const panel=document.getElementById('startup-status');
if(!panel)throw Error('startup diagnostic panel missing');
if(!panel.querySelector('.startup-status-detail').textContent.includes('WebGLRenderer unavailable'))throw Error('renderer diagnostic not displayed');
if(typeof els.deploy.onclick!=='function')throw Error('lobby deploy button not wired');
els.deploy.onclick();
if(!els.lobby.visible)throw Error('failed deployment did not return to lobby');
if(!panel.querySelector('.startup-status-detail').textContent.includes('WebGL context creation failed'))throw Error('deployment failure not surfaced');
console.log('WILDBOUND_STARTUP_FAILURE_RECOVERY_OK');
const successEls={boot:element('boot'),lobby:element('lobby'),game:element('game'),deploy:element('deploy')};
const successDocument={readyState:'complete',getElementById:id=>successEls[id]||null,createElement:tag=>element(tag),addEventListener(){}};
const successWindow={location:{reload(){}},addEventListener(){}};
const successW={state:{screen:'boot'},ui:{refresh(){}},main:{initialize(){successW.state.screen='lobby';successEls.deploy.onclick=()=>{successW.state.screen='game'};}}};
successWindow.WILDBOUND=successW;
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:successWindow,document:successDocument,console});
if(successEls.boot.visible||!successEls.lobby.visible||successEls.game.visible)throw Error('successful startup did not show lobby');
if(successDocument.getElementById('startup-status'))throw Error('successful startup incorrectly displayed an error');
successEls.deploy.onclick();if(successW.state.screen!=='game')throw Error('successful lobby deployment was not preserved');
console.log('WILDBOUND_STARTUP_SUCCESS_PATH_OK');
"""
result = subprocess.run(["node", "-e", node_test, str(paths["boot"])], capture_output=True, text=True)
if result.returncode:
    raise SystemExit("Boot failure integration test failed:\n" + result.stderr + result.stdout)
print("PASS real boot controller failure integration:", result.stdout.strip())

patcher = Path(__file__).with_name("apply_wildbound_startup_recovery.py")
with tempfile.TemporaryDirectory(prefix="wildbound-startup-recovery-") as temp:
    fixture = Path(temp)
    for path in paths.values():
        target = fixture / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    subprocess.run([sys.executable, str(patcher), str(fixture)], check=True, capture_output=True, text=True)
    first = {str(p.relative_to(fixture)): p.read_bytes() for p in fixture.rglob("*") if p.is_file()}
    subprocess.run([sys.executable, str(patcher), str(fixture)], check=True, capture_output=True, text=True)
    second = {str(p.relative_to(fixture)): p.read_bytes() for p in fixture.rglob("*") if p.is_file()}
    if first != second:
        raise SystemExit("Startup recovery patch is not idempotent")
print("PASS patch idempotence")
print("WILDBOUND_STARTUP_RECOVERY_OK", len(checks) + 3, "checks")
