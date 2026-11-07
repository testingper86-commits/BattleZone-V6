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
- The canonical archive does not include these runtime JS files. `app/build.gradle.kts` pins Three.js 0.128.0 / r128 and the GLTFLoader, FBXLoader, SkeletonUtils and fflate helpers by SHA-256. The required `downloadThreeJs` and `downloadCharacterRuntimeLibraries` tasks verify each downloaded file before atomic installation and fail the build on mismatch or unavailable dependencies. CI therefore needs network access during build; the resulting APK serves the verified files locally at runtime.
- The obsolete `downloadSoldierModels` task and its unused NURBS helper downloads have been removed. The app no longer downloads a third-party soldier model during build.

## Runtime integration evidence

- `js/models.js` actively loads both Kenney FBX and KayKit GLB templates. The 17 named operator profiles map across two model families, four Kenney skin textures and distinct tint palettes. All referenced primary files exist in the canonical archive.
- The model loader needs `FBXLoader`, `fflate` and `SkeletonUtils`; these are generated at build time from pinned r128 URLs rather than stored in the original ZIP.
- The bundled KayKit GLB is now an active second rigged model family alongside the original Kenney FBX. Seven named operators use the KayKit rig and a deterministic 25% of AI actors use it; the remaining operators use the Kenney rig with its four existing skin textures and distinct palette tints. Each family has its own animation mixer and hand socket. KayKit provides 30 GLB clips, including Idle, Walk, Run, Jump, Shoot(1h/2h), Shooting(1h/2h), and Defeat; no reload clip is claimed. KayKit clips are never applied to the different Kenney skeleton.
- The build-hardening transformation removes the absent `soldier.glb` fallback and its dead downloader. If Kenney and KayKit both fail, procedural characters remain.
- Only the KayKit GLB and its CC0 license are retained in the APK. Unreferenced KayKit FBX/DAE/OBJ models, alternate GLTF models, branding images, documentation and external links are pruned from the build workspace. This reduces the KayKit package from 12,147,671 bytes to 460,406 bytes (11,687,265 bytes removed); the original canonical source ZIP remains unchanged.
- The renderer uses the root PBR texture set. The duplicated `assets/environment` starter pack is not referenced by runtime code and is removed from the APK build workspace; the original source archive is preserved.
- Main game terrain materials load base-color and roughness PNGs by name. The height PNGs are packaged but the inspected `BZMaterial` path does not bind a height map.
- Five VFX sprites and 17 voice packs are present. V6.1 routes spawn, combat, reload, low-health, cover, victory and defeat events through the selected character voice pack with cooldown/priority handling; the audio license status remains unconfirmed.
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
| Retired optional soldier model source | Historical Gradle task pointed to `cktang88/3d-fps` and required CC BY 4.0 attribution | Task and runtime fallback removed; no soldier model is downloaded or packaged. |

## Duplicate and cleanup observations

- SHA-256 duplicate groups exist for the four compact terrain JPEGs, the compact environment README, its asset-source license note, and the sample material integration JS. These are exact duplicates in different paths; do not delete them until runtime and packaging references are checked.
- Six identical placeholder `.mtl` files and alternate KayKit model formats are present in the preserved canonical source archive; the build prunes these unreferenced samples and retains only the active GLB plus license.
- No third-party tree/rock GLB models are included in the environment starter pack despite links to candidate downloads in its license/source notes. Do not claim the pack contains those models.

## Next asset work

1. Preserve the original archive and all original assets.
2. Confirm provenance for the main PBR textures, voice packs, sprites, branding and loading images before redistribution.
3. Validate model load success and skeleton/skin compatibility on Android; static loader path checks are not runtime animation tests.
4. Validate both Kenney and KayKit model families, right-hand weapon grip, shooting/defeat clips and skin/tint appearance on physical Android devices; static checks confirm local assets and CC0 license evidence only.
5. The absent soldier fallback and unused download task are removed; regression checks enforce that no stale `soldier.glb` reference remains.
6. The unused environment starter pack and unreferenced KayKit sample formats/documentation are pruned from the APK build workspace; the original source archive remains preserved.
7. Confirm provenance for the remaining PBR textures, voice packs, sprites, branding and loading images before redistribution; do not import external assets without exact license, size, mobile compatibility and attribution records.

## Verification boundary

This report was generated from the canonical source ZIP and the Build #45 patched-source artifact by enumerating files, checking SHA-256 hashes and licenses, and tracing runtime references. The Build #46 hardening transformation retains only the KayKit GLB/license and removes unused environment samples from the APK workspace. It does not certify missing provenance or prove successful rendering/animation on a physical Android device.


## Build #55 distributable audio inventory (2026-11-07)

The final-stage build patcher now replaces the canonical archive's 51 synthetic demo MP3s (whose TTS provider/model commercial terms were not recorded) with a verified, local-only subset of Kenney's Voiceover Pack: 44 OGG files across male and female voices, 22 tactical/match callouts per voice. The patcher removes `audio/voicepacks/` from the extracted distributable project, installs the selected OGGs under `audio/cc0_voiceover/`, and preserves `License.txt`, `Credits.txt`, `PROVENANCE.md` and a per-file `manifest.sha256`. Every OGG is verified by SHA-256 before installation. The source archive download SHA-256 is `2ff0c8c51a959a754df698c4ee1e7c2db007c4abde4d600fd19545a1aea9d835`.

The original canonical ZIP remains unchanged and still contains the legacy 51 MP3s. Do not distribute that raw archive as a cleared audio source. The CI-generated patched source archive and APK are the sanitized distributables. Other unresolved generated-art asset provenance remains as recorded above.
