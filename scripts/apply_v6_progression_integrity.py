#!/usr/bin/env python3
"""Repair V6 local progression, wallet consistency, and backup integrity."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
path = files[0]
source = path.read_text(encoding="utf-8")
marker = "BATTLEZONE_V6_PROGRESSION_INTEGRITY_V1"
if marker in source:
    print("BATTLEZONE_V6_PROGRESSION_INTEGRITY_ALREADY_APPLIED")
    raise SystemExit(0)
def once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    source = source.replace(old, new, 1)
once(
    "let ST_={c:500,m:0,w:0,k:0,sk:[0],cur:0,cl:[]};try{Object.assign(ST_,JSON.parse(sg('bzp')||'{}'))}catch(e){}",
    "let ST_={c:500,m:0,w:0,k:0,sk:[0],cur:0,cl:[]};try{const saved=JSON.parse(sg('bzp')||'{}');if(saved&&typeof saved==='object'&&!Array.isArray(saved))['c','m','w','k','sk','cur','cl'].forEach(k=>{if(Object.prototype.hasOwnProperty.call(saved,k))ST_[k]=saved[k]})}catch(e){}",
    "allowlisted wallet restore",
)
anchor_skn = "const SKN=[['Classic',0x3f5f4a,0],['Arctic',0x4a8ac0,300],['Desert',0xc2a060,500],['Shadow',0x333344,800],['Crimson',0xc0392b,400],['Royal',0x6a3fbf,600],['Jungle',0x2f8f4e,350],['Gold',0xe0b030,1200]],MSN=[['Get 10 kills','k',10,100],['Win a match','w',1,300],['Play 3 matches','m',3,150]],hx=c=>'#'+c.toString(16).padStart(6,'0');"
wallet_sanitizer = anchor_skn + """
// Reject malformed imported wallet values before gameplay or shop code reads them.
const walletInt=(v,max=999999999)=>Math.max(0,Math.min(max,Math.floor(Number(v)||0)));
ST_.c=walletInt(ST_.c);ST_.m=walletInt(ST_.m);ST_.w=walletInt(ST_.w);ST_.k=walletInt(ST_.k);
ST_.sk=Array.isArray(ST_.sk)?[...new Set(ST_.sk.map(Number).filter(v=>Number.isInteger(v)&&v>=0&&v<SKN.length))]:[0];
if(!ST_.sk.includes(0))ST_.sk.unshift(0);
ST_.cur=Number.isInteger(Number(ST_.cur))&&ST_.sk.includes(Number(ST_.cur))?Number(ST_.cur):0;
ST_.cl=Array.isArray(ST_.cl)?[...new Set(ST_.cl.map(Number).filter(v=>Number.isInteger(v)&&v>=0&&v<3))]:[];"""
once(anchor_skn, wallet_sanitizer, "wallet schema normalization")
once(
    "const svp=()=>{ss('bzp',JSON.stringify(ST_));updCur()};",
    """const svp=()=>{ss('bzp',JSON.stringify(ST_));updCur()};
// One wallet instance owns every local coin read/write across gameplay and Player Hub.
window.ST_=ST_;
window.BZWallet=Object.freeze({
 balance:()=>Math.max(0,Math.floor(Number(ST_.c)||0)),
 credit(amount){const n=Number(amount);if(!Number.isFinite(n)||n<=0)return false;ST_.c=Math.min(999999999,Math.max(0,Math.floor(Number(ST_.c)||0))+Math.floor(n));svp();return true},
 debit(amount){const n=Number(amount);if(!Number.isFinite(n)||n<0)return false;const cost=Math.floor(n),balance=this.balance();if(balance<cost)return false;ST_.c=balance-cost;svp();return true},
 refresh:()=>svp()
});""",
    "shared local wallet API",
)
once(
    "profile.ownedCharacters=Array.isArray(profile.ownedCharacters)?profile.ownedCharacters:['Recruit'];",
    "if(!profile||typeof profile!=='object'||Array.isArray(profile))profile={name:'Player_01',photo:'',xp:0,level:1,rankPoints:0,season:1,character:'Recruit',ownedCharacters:['Recruit'],equippedCharacter:'Recruit',ownedGunSkins:['Standard'],equippedGunSkin:'Standard',ownedOutfits:['Classic'],equippedOutfit:'Classic'};profile.ownedCharacters=Array.isArray(profile.ownedCharacters)?profile.ownedCharacters:['Recruit'];",
    "non-object profile recovery",
)
once(
    "const coins=()=>{try{return Math.max(0,Number(JSON.parse(localStorage.getItem('bzp')||'{}').c)||0)}catch(e){return 0}};",
    "const coins=()=>window.BZWallet?window.BZWallet.balance():0;",
    "Player Hub wallet read",
)
once(
    "const p=get('bzp',{});p.c=Math.max(0,(Number(p.c)||0)+coin);put('bzp',p);save();",
    "if(Number(coin)>0)window.BZWallet?.credit(coin);save();",
    "kill progression wallet credit",
)
once(
    "const start=$('go2');if(start){start.addEventListener('click',()=>awardXP(20,10,25),{capture:true})}",
    "// Match-start taps grant no progression; rewards are issued only for confirmed gameplay events.",
    "remove pre-match progression reward",
)
once(
    "if(coins()<price){alert('Not enough coins. Earn coins by playing matches and completing missions.');return}const p=get('bzp',{});p.c=Math.max(0,coins()-price);put('bzp',p);",
    "if(!window.BZWallet?.debit(price)){alert('Not enough coins. Earn coins by playing matches and completing missions.');return}",
    "shop purchase wallet debit",
)
once("ST_.c=p.c;", "ST_.c=coins();", "shop outfit wallet synchronization")
once(
    "const KEYS=['bzp','bzc2','bzs','bzd','bzq','bzw','bzn','bzf','bzdaily','bzav','bzname','bzm','bzfade','bzbs','bzlv','bzx','bzbest','bzmis','bzpre','bzsn'];",
    "const KEYS=['bzp','bzProfile','bzOfflineMatchHistory','bzDoctrine','bzc2','bzs','bzd','bzq','bzw','bzn','bzf','bzdaily','bzav','bzname','bzm','bzfade','bzbs','bzlv','bzx','bzbest','bzmis','bzpre','bzsn'];",
    "backup profile and offline history",
)
anchor = "const gunSkins=[{name:'Standard',price:0,color:'#8e9a9d'},{name:'Carbon',price:250,color:'#303844'},{name:'Arctic Camo',price:450,color:'#b6d6e8'},{name:'Crimson Edge',price:650,color:'#b52f42'},{name:'Golden Strike',price:1200,color:'#e0b334'}];"
normalizer = anchor + """
// Validate device-local profile data before any UI uses it as markup or catalog state.
const cleanOwned=(value,catalog,starter)=>{const allowed=new Set(catalog.map(x=>x.name));const rows=Array.isArray(value)?value.filter(x=>typeof x==='string'&&allowed.has(x)):[];if(!rows.includes(starter))rows.unshift(starter);return [...new Set(rows)]};
profile.name=(typeof profile.name==='string'?profile.name:'Player_01').replace(/[^A-Za-z0-9 _-]/g,'').trim().slice(0,18)||'Player_01';
profile.level=Math.max(1,Math.min(1000,Math.floor(Number(profile.level)||1)));
profile.xp=Math.max(0,Math.min(profile.level*100-1,Math.floor(Number(profile.xp)||0)));
profile.rankPoints=Math.max(0,Math.min(1000000000,Math.floor(Number(profile.rankPoints)||0)));
profile.season=Math.max(1,Math.min(9999,Math.floor(Number(profile.season)||1)));
profile.ownedCharacters=cleanOwned(profile.ownedCharacters,characters,'Recruit').filter(n=>{const item=characters.find(x=>x.name===n);return item&&item.level<=profile.level});
if(!profile.ownedCharacters.includes('Recruit'))profile.ownedCharacters.unshift('Recruit');
profile.ownedOutfits=cleanOwned(profile.ownedOutfits,outfits,'Classic');
profile.ownedGunSkins=cleanOwned(profile.ownedGunSkins,gunSkins,'Standard');
if(!profile.ownedCharacters.includes(profile.equippedCharacter))profile.equippedCharacter='Recruit';
if(!profile.ownedOutfits.includes(profile.equippedOutfit))profile.equippedOutfit='Classic';
if(!profile.ownedGunSkins.includes(profile.equippedGunSkin))profile.equippedGunSkin='Standard';
profile.photo=typeof profile.photo==='string'&&profile.photo.length<=350000&&/^data:image\\/(png|jpeg|webp);base64,/i.test(profile.photo)?profile.photo:'';"""
once(anchor, normalizer, "profile schema normalization")
source = source.replace("</html>", "<!-- " + marker + " -->\n</html>", 1)
if marker not in source:
    raise SystemExit("Could not write progression integrity marker")
path.write_text(source, encoding="utf-8")
print("BATTLEZONE_V6_PROGRESSION_INTEGRITY_APPLIED", path)
