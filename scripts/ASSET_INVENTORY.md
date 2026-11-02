# Battle Zone V6 Offline — Source Asset Inventory

**Scope:** canonical `BattleZone_V6_GitHub_Actions_Ready.zip`, extracted from the Offline repository. This is an inventory of the source package, not a claim that every packaged asset is loaded at runtime.

## Inventory totals

- **228 files / 23,650,886 bytes (22.56 MiB)** under `app/src/main/assets/www`.
- Largest groups by file count: models (79), audio (51), textures (27), sprites (5), branding (5), loading imagery (3).
- Largest groups by bytes: models (14.27 MB), textures (5.35 MB), images/branding and loading assets, audio (0.79 MB).

| Extension | Files | Bytes |
|---|---:|---:|
| FBX | 38 | 9,837,640 |
| PNG | 46 | 5,894,532 |
| PDF | 3 | 2,299,180 |
| JPG | 41 | 1,821,144 |
| JS | 11 | 866,193 |
| MP3 | 51 | 791,430 |
| DAE | 3 | 733,864 |
| GLB | 3 | 488,908 |
| OBJ | 6 | 405,541 |
| GLTF | 1 | 192,049 |
| Other (TXT, JSON, MTL, MD, URL, HTML) | 17 | 319,445 |

## Original assets found

- **Characters:** Kenney animated character FBX model, four skin textures, and idle/run/jump FBX clips. KayKit character animation pack includes a 459,768-byte GLB, a 1.33 MB FBX, and 29 separately packaged FBX animation clips (including idle, walk, run, jump, shooting, defeat, attacks, pickup, and other motions), plus sample character models and three engine-specific PDF guides.
- **Environment textures:** nine material families (`asphalt`, `bark`, `concrete`, `dry_dirt`, `forest_floor`, `grass`, `military_metal`, `sand`, `weathered_rock`), each with base-color, height and roughness maps: 27 PNG files.
- **Environment starter packs:** four 512x512 JPEG terrain textures duplicated in the nested compact pack and at its parent `assets/environment/textures` path; procedural-authored environment pack documentation and sample Three.js material code.
- **Visual effects:** five PNG sprites.
- **Branding/loading:** five branding assets and three boot/loading scenes.
- **Audio:** 51 MP3 files in 17 character voice-pack folders, three lines per pack.
- **Runtime libraries:** Three.js r128 and loader/helper scripts are bundled locally.

## Runtime integration evidence

- `index.html` loads `js/models.js`, `FBXLoader.js`, `GLTFLoader.js`, `fflate.min.js` and `SkeletonUtils.js`.
- `js/models.js` actively references the Kenney FBX character, its four skin textures, and its idle/run/jump animations. Those referenced files exist.
- The loader has a secondary `./models/characters/soldier.glb` fallback, but that file is **absent**. It is not required while the primary Kenney configuration loads successfully; the fallback should be corrected or removed in a separately tested change.
- KayKit's large animation library is packaged but no runtime path in `js/models.js` selects it. Only idle/run/jump clips are configured in the active default character model. The KayKit shooting/defeat/attack clips are not proven to be wired into combat or bot state transitions.
- Main game terrain materials load base-color and roughness PNGs by name. The height PNGs are packaged but the inspected `BZMaterial` path does not bind a height map. The procedural environment JPEG starter pack is documented as a starter pack and is not referenced by the main terrain material loader.
- Five VFX sprites and 17 voice packs are present; this inventory alone does not prove that every sprite or every voice line is reached by gameplay.

## License and provenance ledger

| Asset group | Evidence in source | Current disposition |
|---|---|---|
| KayKit character/animation package | `models/characters/kaykit_v1_2/License.txt` states CC0 1.0; attribution to Kay Lousberg is optional | License evidence present. Preserve the license file. |
| Kenney animated character package | `models/characters/kenney/License.txt` states CC0 1.0; attribution to Kenney is optional | License evidence present. Preserve the license file. |
| Compact/realistic environment starter textures | Pack README says the included texture images are procedurally authored; source notes say the referenced third-party GLBs/textures were not downloaded into the pack | Included starter textures are described as original/procedural; third-party source links are references only, not bundled assets. |
| Main 27 PNG PBR texture set | No dedicated per-pack license/attribution file was found in the inspected asset tree | Provenance/license still needs confirmation before external redistribution. |
| 51 character voice MP3 files | No audio-specific license/attribution file found in the inspected tree | Provenance/license still needs confirmation. |
| Five VFX sprites, branding, loading scenes | No dedicated per-group license file found in the inspected tree | Provenance/license still needs confirmation. |

## Duplicate and cleanup observations

- SHA-256 duplicate groups exist for the four compact terrain JPEGs, the compact environment README, its asset-source license note, and the sample material integration JS. These are exact duplicates in different paths; do not delete them until runtime and packaging references are checked.
- Several identical placeholder `.mtl` files are included with the KayKit OBJ samples. They are harmless source-pack duplicates but add no runtime value unless those OBJ samples are used.
- No third-party tree/rock GLB models are included in the environment starter pack despite links to candidate downloads in its license/source notes. Do not claim the pack contains those models.

## Next asset work

1. Preserve the original archive and all original assets.
2. Confirm provenance for the main PBR textures, voice packs, sprites, branding and loading images before redistributing the APK.
3. Validate model load success and skeleton/skin compatibility on Android; the static loader path check is not a runtime animation test.
4. Decide whether KayKit's existing shoot/defeat clips can be integrated into existing animation state transitions without replacing original assets.
5. Only after runtime reference checks, consider deduplicating repeated environment starter files or excluding unused sample documentation from release packaging.
6. Do not import external assets until the exact item, license, file size, mobile compatibility and attribution are recorded.

## Verification boundary

This report was generated by enumerating the canonical extracted source tree, checking actual file sizes and SHA-256 hashes, reading the included license/readme files, and tracing paths in `index.html` and `js/models.js`. It does not certify third-party ownership where no license file exists, nor prove successful rendering or animation on a physical Android device.
