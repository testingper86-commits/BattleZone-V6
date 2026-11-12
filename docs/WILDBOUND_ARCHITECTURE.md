# WILDBOUND architecture

## Runtime layout

```text
app/src/main/assets/www/
├── index.html                 Local entrypoint and strict CSP
├── css/wildbound.css          Responsive headquarters, combat HUD and recovery UI
├── js/wildbound/
│   ├── frontend/              Boot orchestration and screen lifecycle
│   ├── data/                  Local monster, mission, rank and equipment catalogs
│   ├── physics/               Collision, attack arcs and world bounds
│   ├── utils/                 Deterministic math and reusable helpers
│   ├── core/                  Configuration, state and event bus
│   ├── backend/               Local save/recovery, progression and missions
│   ├── gameplay/              Combat rules, abilities, stamina and damage
│   ├── ai/                    Monster perception, patrol, attacks and boss phases
│   ├── actors/                Hunter and monster rigs, anatomy and animation
│   ├── world/                 Blackpine generation, PBR ground, instancing and wind
│   ├── rendering/             Shared WebGL context, VFX, camera and frame loop
│   ├── ui/                    Headquarters, bestiary, inventory, disciplines and HUD
│   └── audio/                 Procedural local Web Audio effects
└── models/, textures/, libs/  Locally bundled licensed models, textures and engine

scripts/wildbound-source/js/wildbound/
├── actors/actors.js           Canonical actor constructors and animation integration
├── ai/monster-ai.js           Canonical AI state machine and attack resolution
├── audio/audio.js             Canonical bounded Web Audio lifecycle
├── gameplay/combat.js        Canonical player combat and dodge events
├── rendering/runtime.js      Canonical scene, camera, VFX and render lifecycle
└── world/world.js             Canonical environment, hazards and canopy wind

app/src/main/java/com/example/battlezone/
├── MainActivity.kt            Local WebView host and request/navigation policy
└── OfflineAssetPolicy.kt      Strict appassets URI validation
```

`sync_wildbound_sources.py` installs the six canonical modules after the base project transformation and synchronizes the generated project's phase-threshold validator. Build-time transformations that remain are limited to features not yet promoted to a canonical module, such as UI additions and Android shell recovery.

## Dependency direction

`core` owns shared state and event contracts. `data` owns static content. `physics` and `utils` expose reusable primitives. `frontend` owns application boot. `backend` persists authoritative offline state. `gameplay` and `ai` consume state and emit events. `actors`, `world` and `rendering` own presentation/runtime objects. `ui` invokes public gameplay/backend actions and observes events. `audio` exposes local effect methods. Runtime script order is explicit in `index.html`; modules do not load scripts dynamically.

## State and persistence

`core/state.js` owns runtime state. Backend services handle progression and contract state. `backend/save.js` stores versioned local snapshots, rotates the last valid snapshot into a backup key, restores from backup on primary corruption, and flushes on page hide. Android local storage and assets remain available without a network connection.

## Offline security

The Android manifest requests no network permission. `MainActivity` disables network loads, file/content access, file-URL universal access, database storage and geolocation; it denies WebView camera/microphone permission requests. `OfflineAssetPolicy` validates scheme, host, port, user info and decoded path before `WebViewAssetLoader` serves local assets. External navigation and non-local requests are blocked. The CSP allows local scripts only, local/data/blob media, local connections, and denies objects, frames and form submissions. No JavaScript bridge is exposed.

## Actors, AI and combat

The hunter has a bundled CC0 rigged GLB and a procedural fallback. The fallback includes layered armor, gauntlets, articulated arm/leg pivots and a local weapon. Grave Stalker, Wraithcaller, Ironmaw and Hollow King use distinct articulated procedural silhouettes, emissive weak-point anchors, species-specific details and independent arm/leg animation. Hollow King has four arm pivots and three combat phases.

Monster AI updates patrol animation outside aggro range, keeps patrol routes inside world bounds, and uses explicit windup/attack/recovery states. Grave Stalker and Ironmaw have separate lunge/slam timing, damage and reach profiles. Hollow King phase one has a telegraphed heavy swing; later phases retain projectile and ground-slam attacks. Perfect dodge interrupts an active windup, staggers the attacker, opens a counter window and charges ultimate meter. Dodge events drive the same pooled VFX path as combat impacts.

## World and rendering

One WebGL renderer/context is shared between the headquarters showcase and gameplay. Blackpine uses instanced trunks, crowns, rocks and ward structures, deterministic local PBR ground maps, atmospheric haze and GPU-driven two-axis canopy wind. Environmental hazards use an initialized, delta-time-driven damage timer. Camera orbit is independent of hunter facing; right-side pointer drag controls yaw and bounded height, and movement input is transformed through camera yaw. Pointer cancellation, lost pointer capture and window focus loss clear active controls.

The combat renderer uses a fixed 72-slot GPU point-particle pool. Hit strength, weak-point strikes, kills, boss phase changes and hunter dodges emit bounded bursts. The pool updates in both lobby and gameplay loops and is disposed before scene reinitialization. The procedural Web Audio layer caps concurrent voices at 12, disconnects nodes on completion, and resumes suspended contexts after foregrounding or user interaction.

Graphics profiles control pixel ratio and environment instance density. The render loop checks WebGL context health, pauses safely on context loss, resumes after context restoration, reports game/lobby frame exceptions, and exposes renderer diagnostics. Resize handling uses host dimensions, `ResizeObserver` and `visualViewport` so Android orientation and inset changes do not leave a stale viewport.

## Licensed assets and honest scope

The hunter uses the bundled KayKit Animated Character v1.2 GLB and local animation clips under CC0; the license is retained with the asset. Terrain PBR maps are generated deterministically and recorded in `PROCEDURAL_ASSET_PROVENANCE.json`. Other monster silhouettes are procedural project geometry, not photorealistic third-party creature scans or motion-capture rigs.

The current deliverable is an offline, playable vertical slice with a complete core hunting loop, not a finished large-scale photorealistic AAA production. Premium photorealistic creature/hunter asset creation, motion-capture polish and physical Android frame-time, memory, audio-focus and thermal acceptance remain separate production gates. CI success does not substitute for device QA.

## Startup and recovery

The frontend reveals the real lobby before attempting WebGL construction. UI initialization is independent of renderer creation. Missing Three.js, renderer construction errors, context loss and frame exceptions surface a local recovery panel with safe retry behavior. The Android shell surfaces main-document failures with a same-origin retry page. Recovery listeners and resize observers are bound once; the renderer namespace is captured as the Three.js object, not repeatedly invoked as a function.
