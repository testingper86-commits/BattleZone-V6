#!/usr/bin/env python3
"""Regression tests for V6 progression, wallet consistency, and backup integrity."""
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = list(root.rglob("app/src/main/assets/www/index.html"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one game index.html, found {len(files)}")
html = files[0].read_text(encoding="utf-8")
checks = {
    "progression integrity marker present": "BATTLEZONE_V6_PROGRESSION_INTEGRITY_V1" in html,
    "wallet restore uses an allowlist": "['c','m','w','k','sk','cur','cl'].forEach" in html and "Object.assign(ST_,JSON.parse" not in html,
    "wallet counters and cosmetic indices are normalized": all(x in html for x in ("const walletInt=", "ST_.cur=Number.isInteger", "ST_.cl=Array.isArray")),
    "single shared wallet is exposed": "window.BZWallet=Object.freeze" in html and "window.ST_=ST_" in html,
    "wallet reads authoritative in-memory balance": "balance:()=>Math.max(0,Math.floor(Number(ST_.c)||0))" in html,
    "wallet credits persist through game save path": "ST_.c=Math.min(999999999" in html and "credit(amount)" in html and "svp();return true" in html,
    "wallet debits reject insufficient funds": "if(balance<cost)return false" in html and "debit(amount)" in html,
    "Player Hub reads shared wallet": "const coins=()=>window.BZWallet?window.BZWallet.balance():0;" in html,
    "shop purchases debit the shared wallet": "window.BZWallet?.debit(price)" in html,
    "kill progression credits shared wallet": "window.BZWallet?.credit(coin)" in html,
    "pre-match click cannot award progression": "awardXP(20,10,25)" not in html and "Match-start taps grant no progression" in html,
    "backup includes player profile": "'bzProfile'" in html.split("const KEYS=", 1)[1].split(";", 1)[0],
    "backup includes actual offline match history": "'bzOfflineMatchHistory'" in html.split("const KEYS=", 1)[1].split(";", 1)[0],
    "backup includes tactical doctrine": "'bzDoctrine'" in html.split("const KEYS=", 1)[1].split(";", 1)[0],
    "null or primitive profile backup is recovered": "if(!profile||typeof profile!=='object'||Array.isArray(profile))profile={name:'Player_01'" in html,
    "profile arrays constrained to real catalog entries": "const cleanOwned=(value,catalog,starter)" in html and "cleanOwned(profile.ownedCharacters,characters,'Recruit')" in html,
    "equipped cosmetics must be owned": all(x in html for x in ("profile.ownedCharacters.includes(profile.equippedCharacter)", "profile.ownedOutfits.includes(profile.equippedOutfit)", "profile.ownedGunSkins.includes(profile.equippedGunSkin)")),
    "profile text and numeric fields normalized": all(x in html for x in ("profile.name=(typeof profile.name", "profile.rankPoints=Math.max", "profile.level=Math.max", "profile.photo=typeof profile.photo")),
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + "  " + name)
if not all(checks.values()):
    raise SystemExit("V6 progression integrity regression checks failed")
print("PASS  V6 progression integrity regression checks; inline JavaScript syntax is covered by validate_project.py")
