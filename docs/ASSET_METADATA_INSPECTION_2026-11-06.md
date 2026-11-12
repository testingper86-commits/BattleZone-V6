# Asset Metadata Inspection — 2026-11-06

This is a follow-on technical inspection of the exact canonical archive recorded in `ASSET_PROVENANCE_FOLLOWUP_2026-11-06.md`. It is not a legal opinion and does not infer ownership from filenames or visual style.

## Results

### 17 character portraits, 5 branding images, 3 loading images

- All 25 files were opened and inspected with Pillow.
- The 17 portraits are 256×384 JPEGs; the three loading backgrounds are 1280×720 JPEGs; branding includes three JPEGs and two PNGs.
- The JPEG metadata exposed only basic JFIF/encoding properties. No EXIF creator, copyright, artist, software, prompt, or source fields were present.
- The two PNG files contained no ancillary metadata in Pillow's parsed metadata dictionary.
- This absence does not prove the files are AI-generated, original, or unlicensed. It means the binary files themselves do not carry usable provenance fields.

### 51 voice MP3s

- All 51 files begin with an ID3v2.4 header.
- The ID3 tag contains only the `TSSE` encoder frame: `Lavf61.7.103`.
- No title, artist, album, copyright, source, TTS provider, voice/model, generation timestamp, or license frame was present.
- The encoder identifies the FFmpeg/libavformat toolchain, not the speech synthesis provider or rights holder.
- This is consistent with the repository's synthetic-demo description, but it does not independently establish the TTS provider or the applicable commercial license.

### Public-source lookup

Searches for the exact portrait filenames, logo/key-art filename, loading-scene filenames, and archive-specific voice-pack description did not return an identifiable upstream creator or provider. A filename search cannot substitute for reverse-image matching, original generation records, invoices, account history, or a rights-holder declaration.

## Final evidence-based status

| Asset group | Technical metadata inspection | Can provenance be independently certified from available evidence? |
|---|---|---|
| 27 procedural material maps | Project docs describe local/procedural generation; manifest fingerprints exact files. | No; no authoring project, generator script/source, or creator declaration. |
| 5 procedural/effect sprites | Project docs describe local/procedural generation; manifest fingerprints exact files. | No; no source project or creator declaration. |
| 51 synthetic demo voice clips | ID3 encoder only; no TTS/provider/license metadata. | No; provider/model, generation account/records, plan, and terms at generation time are unknown. |
| 17 character portraits | No creator/copyright/source metadata. | No. |
| 5 branding images | No creator/copyright/source metadata. | No; trademark clearance also remains separate. |
| 3 loading images | No creator/copyright/source metadata. | No. |
| KayKit/Kenney character packs | Bundled CC0 notices; publisher-level CC0 statements corroborated in prior follow-up. | Publisher-level license is corroborated; exact file-to-release chain is not documented for every file. |

## Why this cannot be closed by further repository or web searching

The archive does not contain creator identities, source URLs, generation project files, TTS provider records, purchase/subscription receipts, or licenses for the unresolved groups. The filenames are generic project names, and embedded metadata is absent. Public searches cannot reliably reconstruct private generation history or establish who authored an anonymous image/audio file.

To close these items, the project owner or original contributor must supply at least one primary record per group: original editable/source project plus creator statement; original asset download URL and matching release/license; generation account export and provider/model/plan terms from the date generated; or a signed rights-holder declaration. For branding, add trademark clearance. If those records cannot be recovered, the defensible release action is to replace the unresolved files with traceable assets under documented licenses, not to mark them cleared.

No game assets, gameplay code, combat systems, build workflow, CI, APK, signing, or release files were changed or executed during this inspection.
