# Character 03 rigging pipeline

The user-supplied Nier Automata Furry GLB is a single static mesh (535,882
vertices) with one material and three embedded images. The source has no glTF
skin, joint attributes, or animation clips.

## Build a development rig

Install the isolated tool dependency:

```sh
python -m pip install -r scripts/requirements-character-rigging.txt
python scripts/rig_character03.py input.glb Character03_Rigged.glb
python scripts/test_character03_rigging.py input.glb Character03_Rigged.glb
```

The generator adds a 21-joint humanoid hierarchy, four normalized bone
influences per vertex, inverse-bind matrices, and eight glTF clips: Idle,
Walk, Run, Crouch, Fight, Punch, Shoot and Emote. It appends new binary
buffer views and does not rewrite source POSITION, NORMAL, TEXCOORD_0 or
embedded image buffer views.

## Acceptance / limitations

The capsule-distance weights and joint landmarks are an automatic first-pass
rig. They are not a substitute for artist-reviewed weight painting or
anatomical retargeting. Validate shoulder/elbow/hip/knee deformation and
foot contact in a GLTF viewer and on Android before promoting this model to
the game. Walk and Run are in-place cycles; the gameplay controller supplies
translation. Punch is a one-shot clip; the other supplied clips loop.

The uploaded archive did not include license documentation. Keep this
user-supplied asset and its derived rig out of the distributable APK until
asset provenance and redistribution rights are verified. Original texture,
material, UV and mesh data are retained by the generator.
