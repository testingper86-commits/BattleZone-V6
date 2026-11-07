# Battle Zone V6 — Offline Map Atlas

## Scope
The Map Atlas is a non-combat navigation system. It adds a local topographic view for the currently selected map, stable named navigation points, editable local waypoints, and route planning. It does not change weapon, targeting, damage, or combat behavior and does not add network access.

## Runtime behavior
- Samples the active Three.js terrain height function to render a cached contour map.
- Uses the active world's lake, river, sea boundary, and bridge coordinates for water-risk overlays; land navigation points are shifted off water and crossing points snap to the live bridge.
- Adds small visual navigation beacons at named points so map labels correspond to visible world markers.
- Plots routes locally with A* using distance, terrain slope, water exclusions, and obstacle penalties. Routes are displayed as planning guidance, not guaranteed collision-free navigation.
- Supports touch/mouse panning, zoom gestures, layer toggles, custom waypoint create/edit/delete, and local route persistence.
- Stores waypoints and routes in per-map localStorage keys. No external map tiles, services, downloads, or API calls are used.

## Validation
Run `python3 scripts/apply_v6_map_atlas.py <source-root>` followed by `python3 scripts/test_v6_map_atlas.py <source-root>`. The test exercises flat routing, obstacle detours, blocked routes, all ten map POI catalogs, and offline integration invariants.

Physical-device QA remains required for touch gestures, map readability, route computation latency, and 3D beacon visibility on low/mid/high Android devices.
