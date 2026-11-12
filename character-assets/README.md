# WILDBOUND — Free Character Asset Preparation

This is a development-only pipeline. It is deliberately isolated from the Android runtime, distributable asset tree, APK workflows and game integration. Do not merge character files into the game until all target assets pass the validation gate and the owner approves integration.

## Toolchain (no paid credits, no Blender)

1. **AnimStudio (AGPL-3.0-or-later):** browser-based GLB/FBX character rigging, skin editing, animation-pack import (Mixamo FBX and Quaternius GLB), foot locking/planting, clip editing and GLB export. Node.js 18+ is required. Upstream: https://github.com/Sheggyb/AnimStudio. The upstream project says model files remain local to its working folders and that its code license does not license imported characters or motion data.
2. **UniRig (MIT):** optional automatic skeleton and skinning prediction for suitable unrigged models. Upstream: https://github.com/VAST-AI-Research/UniRig. It requires a suitable Python/PyTorch/CUDA runtime; a free hosted GPU is not guaranteed. Check the current release/readme for model weights and dependency requirements before provisioning.
3. **three-ws-retarget (Apache-2.0):** deterministic programmatic humanoid GLB retargeting with canonical bone-name mapping, rest-pose correction and a 50% bone-coverage gate. Upstream: https://github.com/nirholas/three-ws-retarget. It does not create missing skeletons or skin weights.

No Tripo3D credit-consuming operation and no Blender workflow is part of this plan. A phone browser may be used for review/control, but substantial model processing may need a free cloud CPU/GPU or a desktop runtime. Never claim a free hosted GPU is available until a session is actually allocated.

## Target queue

| ID | Character | Source | Initial technical note | Required result |
|---|---|---|---|---|
| 01 | Villain Doom | `villain doom.zip` | glTF/GLB source reportedly contains multiple skin records; inspect active mesh-to-skin mapping before editing | Rig review, target weights, retargeted clips, exported GLB |
| 02 | Malfoy Draconia | `harry-potter-malfoy-draconia-3d-model-dl.zip` | Nested archive; contains FBX/PMX/XPS and a Blender project, but Blender is excluded | Choose non-Blender source, validate skeleton/skin, export GLB |
| 03 | Nier Automata Furry (2B) | `2b-nier-automata-furry-3d-model.zip` | A previous 21-joint/eight-clip GLB milestone exists; it is not evidence that the full motion bank was retargeted | Reinspect prior rig, correct bind pose/weights, broaden clips, export GLB |
| 04 | Anime Girl | `anime_girl_nsfw.glb` | Reported to have no skin and no animations | Build humanoid skeleton, weights and clips |
| 05 | High Knight | `high-knight-game-character.zip` | FBX includes a character rig/animation stack; verify joint hierarchy and skin clusters | Preserve valid rig or repair, retarget clips, export GLB |
| 06 | Jack of Blades | `jack-of-blades.zip` | FBX present; rig/skin status not yet verified | Inspect, rig if needed, retarget clips, export GLB |
| 07 | Latina Swimsuit Baddie | `latina-swimsuit-baddie.zip` | GLB reportedly has no skin | Build humanoid skeleton, weights and clips |
| 08 | Animated Female Fighter | `animated-female-fighter-3d-model-rigged-game.zip` | FBX present; rig status not yet verified | Inspect, preserve or repair rig, retarget clips, export GLB |

These names identify the working source queue, not a license clearance. Preserve source archives and textures. Maintain per-asset provenance and license evidence; exclude any uncleared asset from redistribution until its terms are verified.

## Required animation coverage

Use the existing motion bank where compatible, prioritizing idle, walk, jog/run, sprint, dodge, fighting idle, punch, kick, weapon attack and death. Animation coverage is asset-specific: reject unsupported non-humanoid targets or adapt them deliberately rather than forcing a humanoid rig. Reconcile source clip names against the actual bank before assigning clips.

## Per-character acceptance gate

A character is complete only when all of these are true:

- Source mesh/material/texture geometry is preserved and its provenance is recorded.
- One intended skin is bound to each deforming mesh; joint hierarchy is valid and has no invalid references.
- Skin weights are finite, non-negative and normalized per vertex; joints and bind matrices are finite.
- Rest pose is anatomically valid; inspect head, shoulder, elbow, hip, knee, ankle, wrist and hand deformations.
- Retargeting reports actual matched-bone coverage; reject below the retarget library's 50% gate and review dropped bones.
- Idle, locomotion, combat and any weapon clips play through their complete duration without T-pose, frozen joints, NaN transforms, severe mesh collapse or obvious foot sliding.
- Exported GLB reopens in a separate loader; record SHA-256, byte size, mesh count, skin count, joint count, clip names/durations and validation output.
- Do not equate successful file parsing with visual/Android playback verification. Record those separately.

## Status vocabulary

`SOURCE_AUDITED` → `RIGGED` → `WEIGHTS_VALIDATED` → `RETARGETED` → `GLB_EXPORTED` → `PLAYBACK_VERIFIED` → `READY_FOR_INTEGRATION`.

A failed gate records the exact asset, test, error and next corrective action. No placeholders, invented percentages or completion claims without evidence.