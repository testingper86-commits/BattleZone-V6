# Battle Zone V6 — Asset Provenance Follow-up

**Date:** 2026-11-06  
**Repository:** `testingper86-commits/BattleZone-V6`  
**Branch:** `feature/offline-pairing-removal`  
**Canonical archive:** `BattleZone_V6_GitHub_Actions_Ready.zip`  
**Archive SHA-256:** `9598352ccff73a237951108c0604de4c1d1fe08ee32b54dfa77fde283f7769b4`  
**Archive size:** 17,045,510 bytes

## What changed in this follow-up

The canonical ZIP was downloaded from the connected GitHub repository, extracted, and inspected directly. The findings below supersede the earlier broad classification that treated the 27 textures, 51 voice clips, and five sprites as uniformly unidentified third-party assets.

## Updated evidence register

| Group | Count | Evidence found in the canonical archive | Current disposition |
|---|---:|---|---|
| Main material maps | 27 PNG | `GRAPHICS_ASSETS_INTEGRATION.md` and `PROFESSIONAL_UPGRADE_STATUS.md` describe nine local procedural/generated material sets. | No external third-party source is indicated. Keep classified as project-generated per repository records; original authoring/generation records are absent, so authorship is not independently proven. |
| Effect/vegetation sprites | 5 PNG | `README.md`, `GRAPHICS_ASSETS_INTEGRATION.md`, and `PROFESSIONAL_UPGRADE_STATUS.md` describe local procedural/effect/vegetation sprites. | Project-origin claim recorded; no per-file creation records or author/source evidence. Do not claim independent authorship proof. |
| Character voice clips | 51 MP3 | `ASSET_PACK_ADDED.md` calls these locally generated synthetic English radio-callout demo clips, not human-recorded performances. | They are not the separate Kenney Voiceover Pack. The TTS/audio provider, model/version, generation records, and commercial-use terms are absent. Provider terms remain a release check. |
| Character portraits | 17 JPG | `ASSET_PACK_ADDED.md` identifies 17 2D portrait-card images. | Creator, source, generation provider, and license are not recorded. Not cleared for redistribution. |
| Branding | 5 image files | `ASSET_PACK_ADDED.md` calls the Battle Zone logo/key-art and app-icon concept artwork custom. | Creator/source records and trademark/brand clearance are missing. The two additional icon files are not separately explained. Not cleared for public/commercial release. |
| Loading backgrounds | 3 JPG | `ASSET_PACK_ADDED.md` identifies three offline cinematic loading backgrounds. | No creator/source, generation-provider, component-source, or license record. Not cleared for redistribution. |

## Important archive-document distinction

- `OPEN_SOURCE_VOICE_PACK.md` describes a separate optional installer that downloads Kenney's CC0 Voiceover Pack. It explicitly says those downloaded clips are not bundled in the original ZIP. It does **not** establish the provenance of the 51 files under `audio/voicepacks/`.
- `ASSET_PACK_ADDED.md` separately identifies the 51 bundled voice clips as synthetic demo clips.
- The archive's 27 PNG material maps and five sprites are described by project documentation as local/procedural assets, not as downloaded Poly Haven or ambientCG assets.
- The four compact environment JPEGs and the realistic-environment starter JPEG/normal maps are also described in their own README/manifest files as procedurally authored. The Poly Haven, ambientCG, and 3DAssets.dev links in those folders are candidate sources to download separately, not evidence that those third-party assets are bundled.
- KayKit and Kenney character packs retain their bundled CC0 notices. Official publisher statements corroborate CC0 terms: [KayKit Character Animations](https://kaylousberg.com/game-assets/character-animations) and [Kenney licensing FAQ](https://kenney.nl/support). Exact per-file mapping to the original downloaded pack/version should still be retained if a formal rights chain is required.
- Optional `soldier.glb` is absent from the canonical ZIP.

## File-level evidence

The companion [Asset Provenance & SHA-256 Manifest](ASSET_PROVENANCE_HASH_MANIFEST.md) records the canonical archive hash and SHA-256 plus byte size for every file in the six groups above. Hashes identify exact bytes; they do not establish ownership, creator identity, consent, or license.

## Release disposition

**Not a blanket license clearance.** The earlier report overstated the uncertainty around some groups, but the newly inspected records do not prove legal ownership for every project-described generated asset.

Remaining evidence needed:
1. For generated textures/sprites: retain the original authoring source, creator confirmation, and any tools/provider terms used.
2. For synthetic voice: identify the TTS/audio provider and model/version, retain generation records, and verify commercial redistribution terms.
3. For 17 portraits and three loading scenes: identify each creator/source or generation provider and retain the applicable license/terms.
4. For branding: retain creator/ownership evidence and confirm trademark clearance for the name/logo artwork.

No asset was changed, removed, imported, or newly approved. This follow-up is documentation-only. No gameplay, weapon-combat systems, build workflow, APK, CI run, signing, or release artifact was changed or executed.


## 2026-11-07 distributable voice replacement addendum

The Build #55 pipeline no longer packages the original 51 synthetic MP3 demo clips. They are replaced byte-for-byte with 44 selected OGG callouts from Kenney's `Voiceover Pack`, in Male and Female variants. The official Kenney asset page identifies the pack as CC0, and the official support page states Kenney asset-page packs are CC0 for commercial and personal use. The OpenGameArt mirror identifies Kenney as author, CC0, and lists the included tactical lines. The original `License.txt` and `Credits.txt` are bundled; the credits identify Jeffrey M. Smith (male) and Giselle (female). The exact archive hash and each selected file's SHA-256 are retained in `assets/kenney_voiceover_cc0/PROVENANCE.md` and `manifest.sha256`.

Sources: https://kenney.nl/assets/voiceover-pack ; https://kenney.nl/support ; https://opengameart.org/content/voiceover-pack-40-lines

This clears the voice files used by the patched APK/source artifact only. The preserved canonical ZIP still contains the original synthetic MP3s and must not be treated as the sanitized distributable. The 27 PBR maps, five VFX sprites, portraits, branding and loading images retain their previously documented project-origin claims and evidence gaps; this addendum does not certify those unrelated groups.
