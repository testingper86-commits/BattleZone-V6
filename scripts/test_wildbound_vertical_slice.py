#!/usr/bin/env python3
"""WILDBOUND architecture, offline, syntax and gameplay regression gates."""
from pathlib import Path
import re, subprocess, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
www = root / "app/src/main/assets/www"
manifest = root / "app/src/main/AndroidManifest.xml"
required = ["index.html", "css/wildbound.css", "js/wildbound/core/config.js", "js/wildbound/core/state.js", "js/wildbound/data/catalog.js", "js/wildbound/physics/collision.js", "js/wildbound/utils/math.js", "js/wildbound/frontend/boot.js", "js/wildbound/backend/save.js", "js/wildbound/backend/progression.js", "js/wildbound/backend/mission.js", "js/wildbound/gameplay/combat.js", "js/wildbound/ai/monster-ai.js", "js/wildbound/actors/actors.js", "js/wildbound/world/world.js", "js/wildbound/rendering/runtime.js", "js/wildbound/ui/interface.js", "js/wildbound/audio/audio.js"]
missing = [x for x in required if not (www / x).is_file()]
if missing: raise SystemExit("Missing modules: " + ", ".join(missing))
index = (www / "index.html").read_text()
modules = "\n".join((www / x).read_text(errors="ignore") for x in required if x.endswith((".js", ".html")))
save = (www / "js/wildbound/backend/save.js").read_text()
actors = (www / "js/wildbound/actors/actors.js").read_text()
ai = (www / "js/wildbound/ai/monster-ai.js").read_text()
combat = (www / "js/wildbound/gameplay/combat.js").read_text()
checks = {
    "all architectural modules exist": not missing,
    "content, physics and utilities are independent modules": "W.data={" in (www / "js/wildbound/data/catalog.js").read_text() and "W.physics={" in (www / "js/wildbound/physics/collision.js").read_text() and "W.utils={" in (www / "js/wildbound/utils/math.js").read_text() and "W.frontend={" in (www / "js/wildbound/frontend/boot.js").read_text(),
    "battle royale identity is replaced": "BATTLE ZONE" not in index and "WILDBOUND" in index,
    "no runtime network service or remote assets": not re.search(r"https?://|WebSocket|XMLHttpRequest|fetch\s*\(", modules),
    "legacy LAN runtime and battle royale backup are removed": not (www / "js/netplay.js").exists() and not (www / "js/models.js").exists() and not (www / "ORIGINAL_GAME_BACKUP_battle-zone-new-ui-1.html").exists(),
    "offline CSP restricts connections to self": "connect-src 'self'" in index,
    "Android app requests no network permissions": "INTERNET" not in manifest.read_text() and "ACCESS_NETWORK_STATE" not in manifest.read_text() and "ACCESS_WIFI_STATE" not in manifest.read_text() and "CHANGE_WIFI_MULTICAST_STATE" not in manifest.read_text() and "ACCESS_WIFI_STATE" not in manifest.read_text() and "CHANGE_WIFI_MULTICAST_STATE" not in manifest.read_text(),
    "local save has versioned backup recovery": "wildbound.save.v1" in save and "wildbound.save.backup" in save,
    "three monsters and boss are distinct archetypes": all(x in (www / "js/wildbound/data/catalog.js").read_text() for x in ["stalker:", "wraith:", "ironmaw:", "king:"]) and "W.ai={" in ai,
    "boss has three phases": "pct<.3?3:pct<.65?2:1" in ai,
    "strike, rift and dodge mechanics exist": all(x in combat for x in ["attack(game", "ability(game", "dodge(game"]),
    "signature tracking and touch controls exist": 'id="track"' in index and "pointerdown" in (www / "js/wildbound/ui/interface.js").read_text(),
    "locked-landscape touch controls layer above the game canvas": "@media(pointer:coarse) and (orientation:landscape)" in (www / "css/wildbound.css").read_text() and "#game #view" in (www / "css/wildbound.css").read_text() and "z-index:8" in (www / "css/wildbound.css").read_text(),
    "corrupted terrain hazards are active": "hazards" in (www / "js/wildbound/world/world.js").read_text() and "CORRUPTED GROUND" in (www / "js/wildbound/rendering/runtime.js").read_text(),
    "renderer loads bundled Three.js locally": './libs/three.min.js' in index,
    "rigged CC0 character and license are bundled": (www / "models/characters/kaykit_v1_2/Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb").is_file() and "Creative Commons Zero" in (www / "models/characters/kaykit_v1_2/License.txt").read_text(),
    "forest material uses bundled PBR maps": all((www / ("textures/" + n)).is_file() for n in ["forest_floor_basecolor.png", "forest_floor_roughness.png", "forest_floor_height.png"]) and (www / "PROCEDURAL_ASSET_PROVENANCE.json").is_file(),
    "adaptive graphics profiles and pooled projectiles are wired": "setQuality(q)" in (www / "js/wildbound/rendering/runtime.js").read_text() and "setQuality(q)" in (www / "js/wildbound/world/world.js").read_text() and "projectilePool" in (www / "js/wildbound/rendering/runtime.js").read_text(),
    "real rig animation and monster locomotion are integrated": "GLTFLoader" in (www / "js/wildbound/actors/actors.js").read_text() and "m.legs.forEach" not in (www / "js/wildbound/ai/monster-ai.js").read_text() and "u.legs.forEach" in (www / "js/wildbound/ai/monster-ai.js").read_text(),
}
for rel in (www / "js/wildbound").rglob("*.js"):
    result = subprocess.run(["node", "--check", str(rel)], capture_output=True, text=True)
    if result.returncode: raise SystemExit("JavaScript syntax failed: " + str(rel) + "\n" + result.stderr)
checks["all JavaScript modules parse"] = True
node = r"""const fs=require('fs'),vm=require('vm'),path=require('path');global.window=global;global.performance={now:()=>1000};const events={};const W=global.WILDBOUND={CONFIG:{},state:{player:{hp:120,stamina:100,ether:100,xp:0,kills:0,essence:0},inventory:{},skills:{edge:1},progress:{},combat:{combo:0,comboTime:0,attackCd:0,dodgeCd:0,abilityCd:0,ultimate:0},world:{seed:1}},bus:{emit:(n,d)=>(events[n]||[]).forEach(f=>f(d)),on:(n,f)=>(events[n]||(events[n]=[])).push(f)},actors:{play(){}},audio:{hit(){},heavy(){},kill(){},rift(){},dodge(){},hurt(){},boss(){}},toast(){}};const dir=path.resolve(process.argv[1]);for(const f of ['data/catalog.js','physics/collision.js','utils/math.js','backend/progression.js','backend/mission.js','gameplay/combat.js','ai/monster-ai.js'])vm.runInThisContext(fs.readFileSync(path.join(dir,'js/wildbound',f),'utf8'),{filename:f});const pos=(x,z)=>({x,y:0,z,set(nx,ny,nz){this.x=nx;this.y=ny;this.z=nz},distanceTo(o){return Math.hypot(x-o.x,z-o.z)}});const enemy=(kind,z)=>({position:pos(0,z),rotation:{y:0},lookAt(){},visible:true,scale:{setScalar(){}},userData:{type:kind,kind:W.data.monsters[kind].kind,hp:100,maxHp:100,alive:true,attackCd:10,stagger:0,weakUntil:0,hitFlash:0,speed:W.data.monsters[kind].sp,damage:W.data.monsters[kind].damage,range:W.data.monsters[kind].range,arms:[],legs:[],body:{material:{emissive:{setHex(){}}}},aura:{material:{color:{setHex(){}}}}}});const p={position:pos(0,0),rotation:{y:0}};const es=[enemy('stalker',2),enemy('wraith',12),enemy('ironmaw',3),enemy('king',8)];es[3].userData.kind='boss';es[3].userData.hp=60;es[3].userData.maxHp=100;es[3].userData.phase=1;const game={player:p,monsters:es,scene:{},THREE:{},projectiles:[],invulnerable:0};W.combat.attack(game);if(es[0].userData.hp>=100||W.state.combat.ultimate!==12)throw Error('directional strike/ultimate charge failed');W.combat.kill(game,es[0]);if(W.state.player.kills!==1||W.state.player.xp!==90)throw Error('progression reward failed');W.ai.update(game,.016);if(es[3].userData.phase!==2)throw Error('boss phase transition failed');W.missions.reset(game);for(const m of es.slice(0,3)){m.userData.alive=true;W.combat.kill(game,m)}if(!es[3].userData.alive||W.state.progress.purged!==3)throw Error('boss unlock mission transition failed');console.log('WILDBOUND_GAMEPLAY_RUNTIME_OK');"""
result = subprocess.run(["node", "-e", node, str(www)], capture_output=True, text=True)
if result.returncode: raise SystemExit("Gameplay runtime regression failed: " + result.stderr + result.stdout)
checks["combat, rewards, boss phases and mission unlock execute"] = "WILDBOUND_GAMEPLAY_RUNTIME_OK" in result.stdout
save_test = r'''const fs=require("fs"),vm=require("vm");global.window=global;const db={};global.localStorage={getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=v,removeItem:k=>delete db[k]};global.document={addEventListener(){}};global.addEventListener=()=>{};global.WILDBOUND={state:{player:{xp:10},inventory:{potions:2},skills:{},progress:{}},bus:{on(){}},toast(){}};vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"));WILDBOUND.save.write();WILDBOUND.state.player.xp=99;WILDBOUND.save.write();localStorage.removeItem("wildbound.save.v1");if(!WILDBOUND.save.load()||WILDBOUND.state.player.xp!==10)throw Error("backup recovery failed");console.log("WILDBOUND_SAVE_RECOVERY_OK");'''
save_path = www / "js/wildbound/backend/save.js"
sr = subprocess.run(["node", "-e", save_test, str(save_path)], capture_output=True, text=True)
if sr.returncode: raise SystemExit("Save recovery regression failed: " + sr.stderr + sr.stdout)
checks["save recovery restores the last valid backup"] = "WILDBOUND_SAVE_RECOVERY_OK" in sr.stdout
activity = (root / "app/src/main/java/com/example/battlezone/MainActivity.kt").read_text()
checks["Android shell has no LAN sockets or Wi-Fi discovery"] = "ServerSocket" not in activity and "WifiManager" not in activity and "Socket(" not in activity
for name, ok in checks.items(): print(("PASS" if ok else "FAIL"), name)
if not all(checks.values()): raise SystemExit("WILDBOUND_REGRESSION_FAILED")
print("WILDBOUND_REGRESSION_OK", sum(checks.values()), "checks")
