# Third-Party Asset Register

**Project:** Battle Zone V6 Offline  
**Canonical branch:** `feature/offline-pairing-removal`

## Approved open-license sources for non-combat use

| Source | Intended content | License | Intended use | Import status |
|---|---|---|---|---|
| Kenney UI Pack | Interface panels, buttons, icons and controls | CC0 (official pack page) | Lobby, menus and settings UI | Source approved; binary import not yet performed |
| Kenney Interface Sounds | Interface feedback audio | CC0 (official pack page) | Menu and settings interaction sounds | Source approved; binary import not yet performed |
| Poly Haven | Individually selected PBR textures and HDRIs | CC0 (publisher license) | Non-combat environment/background presentation | Source approved; no individual assets selected |
| Existing KayKit pack | Bundled character/animation assets with included license notice | CC0 1.0 (bundled notice) | Preserve existing licensed content; no new combat integration | Existing files retained |

## Official source and license references

- Kenney UI Pack: https://kenney.nl/assets/ui-pack
- Kenney Interface Sounds: https://kenney.nl/assets/interface-sounds
- Kenney licensing FAQ: https://kenney.nl/support
- Poly Haven license: https://polyhaven.com/license
- KayKit Character Animations: https://kaylousberg.com/game-assets/character-animations

## Import and attribution controls

1. Download from the official publisher or creator page only.
2. Verify the license on the exact pack or asset page and preserve the original license notice.
3. Keep each pack in a separate source directory.
4. Record pack/release, creator, source URL, license identifier, retrieval date, destination path, byte size and SHA-256 for every imported file.
5. For CC-BY or other attribution licenses, include creator attribution, license URL and modification notice. Do not classify these as CC0.
6. Never treat a site's general license as applying to every asset without checking the specific asset page.
7. Retain originals before optimization and record any format conversion or modification.
8. Do not replace an existing file until runtime references, dimensions, channels, audio format and compatibility are verified.

## Scope boundary

This source register covers only non-combat lobby/menu/settings UI, interface feedback, and non-combat environment/background presentation. It does not authorize edits to weapon-combat source, combat assets, weapon/effect assets, combat animations or combat audio; combat QA; full-game builds; CI; APK packaging; signing; or release workflows.

Existing files with unclear runtime roles remain untouched. Portraits, branding and loading imagery are not automatically replaced by unrelated packs. Any replacement must be an exact-fit asset with verified individual licensing and provenance.

## Honest implementation status

This document records approved sources and controls. It does not claim that new binary assets have been downloaded, imported, wired into the app, or runtime-tested. The previously bundled KayKit/Kenney license notices remain preserved.
