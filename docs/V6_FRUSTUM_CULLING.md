# BattleZone V6 static-world frustum culling and forest shadows

The final source stage `BATTLEZONE_V6_FRUSTUM_CULLING_V1` corrects three major static-world batches that were explicitly marked `frustumCulled=false`: terrain, instanced forest trunks/leaves, and instanced grass. Their bounding spheres are computed after geometry/instance data is finalized, then normal Three.js frustum culling is enabled.

Imported model meshes now use frustum culling by default, while skinned and instanced meshes retain conservative no-cull behavior to avoid clipping animated rigs or unbounded instances.

Instanced forest trunks cast shadows in high-quality mode; leaves receive shadows but do not cast them, avoiding the cost of full foliage shadow casting. Low-quality mode keeps these shadows disabled.

`test_v6_frustum_culling.py` checks the bounds/culling order, tree shadow flags, preservation of skinned-mesh behavior, and runs Node syntax checks on `models.js` and the modified main inline game script. This is static validation only. Frame-time, GPU load, shadow quality and memory impact still require profiling on representative Android devices.
