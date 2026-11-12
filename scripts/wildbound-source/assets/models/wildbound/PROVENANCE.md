# WILDBOUND model asset provenance

All bundled GLB models are sourced individually from 3DAssets.dev and declare CC0 1.0 Universal. Exact asset source URLs, direct CDN URLs, catalogue geometry/texture statistics, AI-generation disclosures and local SHA-256 digests are recorded in `manifest.json`. Model bytes and textures are embedded locally; the game runtime does not fetch remote assets.

The hunter is a 74-joint MakeHuman-derived rig with authored idle, walk, run and grasp clips. The four creature archetypes use detailed textured animal meshes without skeletons or animation clips; their AI pathing, facing, attack timing, hit reactions and death logic remain in the game runtime, with restrained model-root motion. Environment GLBs are instanced locally and use the existing quality-tier controls.
