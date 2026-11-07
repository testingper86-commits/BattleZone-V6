# Battle Zone V6 Offline — Source Asset Inventory

**Scope:** canonical `BattleZone_V6_GitHub_Actions_Ready.zip`, extracted before Gradle build-time downloads. This inventory distinguishes original archive files from libraries generated during CI and from assets proven to be loaded at runtime.

## Original archive inventory

- **223 files / 22,825,289 bytes (21.77 MiB)** under `app/src/main/assets/www`.
- Models: 79 files / 14,270,810 bytes.
- Textures: 27 files / 5,352,159 bytes.
- Audio: 51 MP3 files / 791,430 bytes.
- Sprites: 5 PNG files / 39,337 bytes.
- Branding: 5 files / 516,838 bytes.
- Loading imagery: 3 files / 569,021 bytes.
- The `libs/` directory contains only a 414-byte README in the original archive. The large JavaScript runtime libraries are fetched by Gradle before `preBuild`; they are not part of the original ZIP.

| Extension | Files | Bytes |
|---|---:|---:|
| FBX | 38 | 9,837,640 |
| PNG | 46 | 5,894,532 |
| PDF | 3 | 2,299,180 |
| JPG | 41 | 1,821,144 |
| MP3 | 51 | 791,430 |
| DAE | 3 | 733,864 |
| GLB | 3 | 488,908 |
| OBJ | 6 | 405,541 |
| HTML | 1 | 315,009 |
| GLTF | 1 | 192,049 |
| JS | 6 | 30,497 |
| TXT | 11 | 10,796 |
| JSON | 3 | 1,700 |
| MTL | 6 | 1,404 |
| MD | 1 | 1,207 |
| URL | 3 | 388 |

## Original content found

- **Characters:** Kenney animated character FBX model, four skin textures, and idle/run/jump FBX clips. KayKit character animation package includes a 459,768-byte GLB, a 1.33 MB FBX, 29 separately packaged FBX animation clips (including idle, walk, run, jump, shooting, defeat, attacks, pickup and other motions), sample character models and three engine-specific PDF guides.
- **Environment textures:** nine material families (`asphalt`, `bark`, `concrete`, `dry_dirt`, `forest_floor`, `grass`, `military_metal`, `sand`, `weathered_rock`), each with base-color, height and roughness maps: 27 PNG files.
- **Environment starter packs:** four 512x512 JPEG terrain textures duplicated in the nested compact pack and at the parent `assets/environment/textures` path; procedural-authored environment pack documentation and sample Three.js material code.
- **Visual effects:** five PNG sprites.
- **Branding/loading:** five branding assets and three boot/loading scenes.
- **Audio:** 51 MP3 files in 17 character voice-pack folders, three lines per pack.

## Build-time runtime dependencies

- `index.html` references `three.min.js`, `GLTFLoader.js`, `fflate.min.js`, `FBXLoader.js` and `SkeletonUtils.js` under `libs/`.
- The canonical archive does not include these runtime JS files. `app/build.gradle.kts` pins Three.js 0.128.0 / r128 and downloads it through the required `downloadThreeJs` task. `downloadOptionalLibs` fetches the r128 loaders/helpers before `preBuild` when missing. CI therefore needs network access during build; the downloaded files are packaged into the APK and served locally at runtime.
- `downloadSoldierModels` is a manual optional Gradle task and is not a `preBuild` dependency. Do not assume it runs during normal CI builds.

## Runtime integration evidence

- `js/models.js` actively references the Kenney FBX character, its four skin textures, and idle/run/jump animations. All referenced primary files exist in the canonical archive.
- The model loader needs `FBXLoader`, `fflate` and `SkeletonUtils`; these are generated at build time from pinned r128 URLs rather than stored in the original ZIP.
- A bundled KayKit GLB is now the second model fallback after the original Kenney FBX. It carries its own rig and 30 GLB clips, including Idle, Walk, Run, Jump, Shoot(1h/2h), Shooting(1h/2h), and Defeat. GLB name matching maps a shooting clip to `shoot` and `Defeat` to `death`; no reload clip is claimed. The KayKit clips are never applied to the different Kenney skeleton.
- The older `./models/characters/soldier.glb` fallback remains last in the list, but that file is **absent** from the canonical archive. The optional `downloadSoldierModels` task is not attached to `preBuild`, so it is not expected in a normal CI APK. If both Kenney and KayKit loaders fail, procedural characters remain.
- Main game terrain materials load base-color and roughness PNGs by name. The height PNGs are packaged but the inspected `BZMaterial` path does not bind a height map. The procedural environment JPEG starter pack is not referenced by the main terrain material loader.
- Five VFX sprites and 17 voice packs are present; this inventory alone does not prove that every sprite or every voice line is reached by gameplay.
- The original `libs/README.txt` incorrectly claimed the game does not use FBXLoader/GLTFLoader and all characters are procedural. The Offline patch now rewrites that stale note to match `js/models.js` and the Gradle download tasks.

## License and provenance ledger

| Asset group | Evidence in source | Current disposition |
|---|---|---|
| KayKit character/animation package | `models/characters/kaykit_v1_2/License.txt` states CC0 1.0; attribution to Kay Lousberg is optional | License evidence present. Preserve the license file. |
| Kenney animated character package | `models/characters/kenney/License.txt` states CC0 1.0; attribution to Kenney is optional | License evidence present. Preserve the license file. |
| Compact/realistic environment starter textures | Pack README says included texture images are procedurally authored; source notes say referenced third-party GLBs/textures were not downloaded into the pack | Included starter texture provenance is documented; linked external assets are not bundled. |
| Main 27 PNG PBR texture set | No dedicated per-pack license/attribution file found in the inspected asset tree | Provenance/license confirmation required. |
| 51 voice MP3 files | No audio-specific license/attribution file found in the inspected tree | Provenance/license confirmation required. |
| VFX sprites, branding, loading scenes | No dedicated per-group license file found in the inspected tree | Provenance/license confirmation required. |
| Optional soldier model source | Gradle task points to `cktang88/3d-fps` and writes a CC BY 4.0 notice if manually run | Not included in canonical archive and not fetched by normal build. Re-check upstream license and attribution before enabling. |

## Duplicate and cleanup observations

- SHA-256 duplicate groups exist for the four compact terrain JPEGs, the compact environment README, its asset-source license note, and the sample material integration JS. These are exact duplicates in different paths; do not delete them until runtime and packaging references are checked.
- Six identical placeholder `.mtl` files are included with the KayKit OBJ samples. They are harmless source-pack duplicates but add no runtime value unless those OBJ samples are used.
- No third-party tree/rock GLB models are included in the environment starter pack despite links to candidate downloads in its license/source notes. Do not claim the pack contains those models.

## Next asset work

1. Preserve the original archive and all original assets.
2. Confirm provenance for the main PBR textures, voice packs, sprites, branding and loading images before redistribution.
3. Validate model load success and skeleton/skin compatibility on Android; static loader path checks are not runtime animation tests.
4. Validate the KayKit fallback model, skin and shooting/defeat clips on physical Android devices; static checks confirm the bundled GLB and CC0 license only.
5. Correct or remove the absent soldier fallback in a separately tested change, or intentionally wire the optional download task only after reviewing its CC BY 4.0 attribution and offline packaging implications.
6. Only after runtime reference checks, consider deduplicating repeated environment starter files or excluding unused sample documentation from release packaging.
7. Confirm provenance for the remaining PBR textures, voice packs, sprites, branding and loading images before redistribution; do not import external assets without exact license, size, mobile compatibility and attribution records.

## Verification boundary

This report was generated from the canonical source ZIP before Gradle downloads by enumerating the source tree, checking file sizes and SHA-256 hashes, reading included license/readme files, and tracing references in `index.html`, `js/models.js` and `app/build.gradle.kts`. It does not certify missing provenance or prove successful rendering/animation on a physical Android device.
