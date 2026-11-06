# Battle Zone V6 Offline — Asset License & Documentation Consistency Review

**Review date:** 2026-11-06  
**Repository:** `testingper86-commits/BattleZone-V6`  
**Reviewed branch:** `feature/offline-pairing-removal`  
**Reviewed commit:** `891aaba309e8c9a463b9e79c171f7bda4eed18a3`  
**Scope:** Documentation and license-provenance review only. No assets, runtime code, gameplay systems, build workflows, or artifacts were modified.

## 1. Executive result

The original asset inventory reports 223 files / 22,825,289 bytes across models, textures, audio, sprites, branding, and loading imagery. Two included character-asset groups have bundled CC0 notices, and their publishers' public licensing statements corroborate CC0 terms:

- KayKit character animation package: bundled `License.txt` states CC0 1.0; the publisher's current Character Animations page states free personal/commercial use, no attribution required, CC0.
- Kenney animated character package: bundled `License.txt` states CC0 1.0; Kenney's official support page states that assets on its asset pages are CC0 and attribution is not required. Official Animated Characters pages also state CC0.

**This is not a complete asset-by-asset license certification.** The archive's exact source-pack/version mapping is not established for every model, and the PBR texture set, audio, VFX, branding, and loading imagery lack sufficient source/license evidence. Do not redistribute or newly approve those groups on the basis of this report.

## 2. Provenance register

| Asset group | Evidence available | Review result | Remaining evidence |
|---|---|---|---|
| KayKit character/animation package | Bundled `models/characters/kaykit_v1_2/License.txt` reports CC0 1.0; official publisher page reports CC0 and no attribution requirement | License terms independently corroborated | Preserve bundled notice; confirm exact downloaded pack/version and map every included file to that pack before asserting all model files are covered |
| Kenney animated character package | Bundled `models/characters/kenney/License.txt` reports CC0 1.0; Kenney official support and Animated Characters pages corroborate CC0 | License terms independently corroborated | Confirm exact Kenney pack/page and map all included FBX/skin files to that release |
| Environment starter JPEG textures | Bundled pack README describes included textures as procedurally authored; linked external models/textures are described as not included | Provenance statement exists, but independent creator/source evidence is incomplete | Original author/source package and version evidence |
| Main 27 PBR PNG maps | No dedicated per-pack license/attribution file or source URL recorded in inspected tree | **Unverified; not approved for redistribution pending evidence** | Creator, exact source URL, asset IDs, version/date, license text and any restrictions |
| 51 voice MP3 files | No audio-specific license/attribution file or source URL recorded in inspected tree | **Unverified; not approved for redistribution pending evidence** | Recording/performer ownership, source, consent/rights, license and redistribution terms |
| Five VFX sprites | No dedicated per-group license/attribution file or source URL recorded | **Unverified; not approved for redistribution pending evidence** | Creator/source URL, asset identity, license and modification history |
| Five branding assets | No dedicated per-group rights record found | **Unverified; not approved for redistribution pending evidence** | Brand/creator ownership, trademark permissions and usage scope |
| Three loading scenes/images | No dedicated per-group license/attribution file or source URL recorded | **Unverified; not approved for redistribution pending evidence** | Creator/source URL, image/model components, license and redistribution terms |
| Optional `soldier.glb` | Absent from canonical source archive; optional manual download task references an upstream repository and a CC BY 4.0 notice | Not present in the reviewed distributable archive; excluded from the current archive license count | If ever added, verify exact upstream asset, license version, attribution text and included dependencies before use |

### Publisher references checked

- KayKit, Character Animations: https://kaylousberg.com/game-assets/character-animations
- KayKit, Character Animations download page: https://kaylousberg.itch.io/kaykit-character-animations
- Kenney, Animated Characters Retro: https://kenney.nl/assets/animated-characters-retro
- Kenney, Animated Characters Protagonists: https://kenney.nl/assets/animated-characters-protagonists
- Kenney, Animated Characters Survivors: https://kenney.nl/assets/animated-characters-survivors
- Kenney, licensing FAQ: https://kenney.nl/support

Publisher-level terms corroborate the bundled notices, but do not by themselves prove that every file in the archive came from a particular pack. No attribution requirement should be inferred for unrelated assets.

## 3. Documentation consistency review

Files compared on the reviewed commit:

- `README.md`
- `scripts/README.md`
- `scripts/ASSET_INVENTORY.md`
- `scripts/ANDROID_GAMEPLAY_QA_MATRIX.md`
- `scripts/V6_RUNTIME_QA.md`
- `.github/workflows/android-build.yml`

### Consistent claims

1. **Canonical source:** README, scripts README, and workflow agree that CI extracts `BattleZone_V6_GitHub_Actions_Ready.zip`; the separate Cloud Build archive is not overlaid.
2. **Build versus runtime network:** scripts README and asset inventory describe build-time downloads of pinned runtime libraries. README describes the installed package as serving assets locally and having no Android network permission. These statements are compatible: network access may be needed during build preparation, not during installed-app runtime.
3. **CI outputs:** README's three artifact categories match the workflow's debug APK, unsigned release APK, and patched-source archive uploads.
4. **Signing:** README accurately describes the release APK as unsigned pending the owner's protected release key.
5. **QA boundary:** QA matrix and runtime QA document require physical-device evidence and explicitly state that CI/static validation is not device verification.
6. **Asset inventory boundary:** asset inventory distinguishes original archive files from build-time downloads and does not claim that every included asset is runtime-loaded.

### Limitations and follow-up

- The QA matrix contains a larger set of test cases than the initial 18-case matrix described in older project notes. The current document itself is internally organized by successive QA ranges; older Linear summaries should not be used as the current case count.
- The asset inventory is a source-tree audit, not a rights certificate. Missing per-group provenance remains a release gate.
- The optional `soldier.glb` is not in the canonical archive. Its upstream license notice must not be treated as proof that the absent file is included or cleared for future inclusion.
- Build-time network dependency remains a reproducibility limitation; it is not evidence of an installed-app online dependency.
- The workflow invokes gameplay patchers and packages the full game. This review did not run or modify that workflow.

## 4. Release disposition

**License review:** Partial. KayKit and Kenney license terms corroborated; remaining asset groups and exact file-to-pack mappings are not fully verified.

**Documentation consistency:** Completed for the six files listed above. No material contradiction was found in the claims compared. The distinctions between build-time network access, runtime offline behavior, CI success, device QA, and unsigned release packaging are explicit.

**Release readiness:** Not cleared by this review. Asset-owner evidence, physical-device QA, deterministic build dependency evidence, and owner-controlled release signing remain separate gates.

## 5. Review method and limits

The review compared the canonical branch documents and workflow content, the existing archive inventory, bundled-license findings recorded by that inventory, and the named publishers' public licensing statements. It did not independently unpack and fingerprint every asset against its publisher's download archive, obtain private rights/consent records, or provide legal advice. A final per-file clearance requires an asset-to-source manifest with cryptographic hashes and the corresponding source/license evidence.

No original assets were changed, removed, imported, or approved. No source/gameplay code, CI workflow, APK, or release artifact was changed or generated.
