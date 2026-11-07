# BattleZone V6 retained-asset provenance gate

CI now generates `app/src/main/assets/ASSET_PROVENANCE_LEDGER.json` from the transformed, distributable asset tree before computing `BUILD_PROVENANCE.json`. Every retained binary asset receives its SHA-256, size, license status, evidence paths and an explicit note. The ledger is included in the patched-source archive and Android APK.

## Verified evidence

- Kenney animated character package: package-local `License.txt` explicitly states CC0 1.0.
- KayKit character/animation package: package-local `License.txt` explicitly states CC0 1.0.
- Kenney Voiceover Pack: CC0 `License.txt`, `Credits.txt`, `PROVENANCE.md`, and `manifest.sha256` are present; CI verifies every OGG hash and exact manifest coverage.

On the Build #75 transformed asset tree, the generator found **90 binary assets: 54 verified CC0 and 36 unverified**. The 36 unresolved files are exactly 27 PBR texture PNGs, 5 VFX sprite PNGs, 3 loading-scene JPGs, and 1 active logo JPG. The ledger records their individual hashes and paths; it does not invent licenses.

## Release gate

The workflow still creates unsigned review artifacts. If the repository variable `BATTLEZONE_RELEASE_APPROVED` is explicitly set to `true`, ledger generation runs with `--require-verified` and fails while any retained asset is unverified. This prevents treating a successful debug/unsigned build as legal clearance for redistribution.

## Remaining owner evidence

The PBR textures, VFX sprites, active logo and loading images still need either verifiable original source/license records or replacement with assets whose licenses and provenance can be documented. Do not mark them CC0 based only on appearance or filename.
