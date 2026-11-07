# Battle Zone V6 Offline — Android Gameplay QA Matrix

**Release gate:** run on physical Android devices. CI build and static validation do not replace these checks. All tests must be performed with airplane mode enabled after install, except the install/build steps themselves.

| ID | Area | Test | Expected result | Evidence |
|---|---|---|---|---|
| QA-01 | Install/launch | Fresh install, first launch, airplane mode on | App opens without network permission or remote request dependency | Device, Android version, screen recording, logcat |
| QA-02 | Resume | Background/foreground, screen lock/unlock, activity recreation | Game resumes or safely returns to lobby; no frozen render loop | Video + logcat |
| QA-03 | Lobby | Enter/exit lobby, choose map/mode, start match | Controls respond; no pairing/room UI | Video |
| QA-04 | BR | Complete match loop | Local bots, loot/combat, five safe-zone phases and match end operate | Video + match state |
| QA-05 | TDM | Complete match with AI allies | Three local AI teammates participate; score/respawn/win condition work | Video + score evidence |
| QA-06 | FFA | Complete match | Local AI opponents, scoring and 20-kill target work | Video + score evidence |
| QA-07 | Controls | Move, sprint, crouch/jump if exposed, aim/camera drag, fire, reload, switch weapon | Touch regions are responsive and do not overlap essential HUD controls | Device matrix + video |
| QA-08 | Combat | Hit detection, health/damage, death, respawn, ammo and reload state | State transitions are consistent; no stuck fire/reload or stale HUD | Video + logcat |
| QA-09 | AI | Bot navigation, targeting, attacks, obstacle handling; TDM allies | Bots remain inside map, move and fight without soft-locks | Video + logcat |
| QA-10 | Map | Greenfield, Sandstorm and Frostbite; map boundary and POIs | Terrain, obstacles and minimap stay aligned; player cannot escape bounds | Screenshots/video |
| QA-11 | Zone | Verify all five shrink phases, damage outside, final phase | Timings/radii progress once, damage applies correctly, match resolves | Timestamped video |
| QA-12 | Models | Player/bot model, four skins, idle/run/jump | No missing texture, broken skeleton, clipping or invisible model | Screenshots/video |
| QA-13 | Audio | SFX, music, voice lines, mute/volume, interruptions | Correct playback; no audio leak or repeated stuck audio | Video + audio observations |
| QA-14 | Persistence | Restart app; check local settings/progression | Local data persists as designed; no account/network requirement | Before/after screenshots |
| QA-15 | Performance | 15-minute match on low/mid/high devices | Stable frame pacing; no sustained stalls or runaway memory | Perfetto/Android profiler traces |
| QA-16 | Thermal | 30-minute continuous play | No unsafe thermal behavior or severe throttling | Temperature/performance log |
| QA-17 | Lifecycle stress | 10 match starts, pause/resume, rotate if supported | No crashes, leaks, black screen or stuck input | Logcat + repetition count |
| QA-18 | Offline regression | Toggle airplane mode before launch and during lobby/match | No network permission prompt, pairing UI or network-dependent failure | Video + manifest inspection |

## Device coverage

At minimum: one low-memory Android device, one mid-range device, and one higher-performance device. Record exact model, Android API level, RAM, GPU, display resolution/density, refresh rate and build SHA-256.

## Pass/fail rules

- Any crash, hang, input lock, match soft-lock, missing core asset, network dependency or incorrect win/zone state is a blocker.
- Performance thresholds must be recorded per device; do not average away a failing low-end device.
- Keep screenshots, video, logcat and profiler evidence tied to the exact APK SHA-256.
- The release cannot be marked device-verified until all blocker tests pass on the declared device matrix.


## Gameplay repair regression gate

| ID | Area | Test | Expected result | Evidence |
|---|---|---|---|---|
| QA-19 | Water | Remain fully submerged, then leave water; repeat while in a vehicle. | Health decreases at 7 HP/second only while the player is swimming; no vehicle damage. | Video + health HUD + logcat |
| QA-20 | Vehicles | Shoot each vehicle type repeatedly, then test nearby vehicles and player after destruction. | Bullet hits reduce vehicle health; destroyed vehicle explodes, stops moving and can no longer be entered. | Video + vehicle state |
| QA-21 | Squad | Fresh install, then existing saved Solo and Duo profiles. | New installs default to Squad; saved Solo/Duo selection is preserved. | Settings screenshots + localStorage state |
| QA-22 | Ally combat | TDM match with three AI allies against enemy bots. | Allies follow, acquire nearby enemies and land shots more consistently without targeting teammates. | Video + combat log |
| QA-23 | Ally medical support | Take damage while an ally is nearby; separately test downed-player revive. | Nearby ally restores health over time; existing revive flow still works. | Video + health HUD |
| QA-24 | Touch recovery | Interrupt joystick, camera drag and held action/vehicle controls using cancel, lost capture, app background and window focus loss. | All held inputs release; player/vehicle does not continue moving or firing. | Screen recording + logcat |
| QA-25 | Frame pacing | Resume after a frame stall and play a sustained match. | No large movement/physics jump after stalls; stable sustained frame pacing. | Perfetto / Android GPU profiler |
| QA-26 | Mobile rendering | Test high-density devices with battery saver on/off. | Pixel ratio and shadow budget remain within configured caps; no corrupted or missing rendering. | Screenshots + profiler |

The source patch and static validator cover code-level invariants only. QA-19 through QA-26 require physical-device execution before release approval.


## Gameplay quality V2 regression gate

| ID | Area | Test | Expected result | Evidence |
|---|---|---|---|---|
| QA-27 | Character actions | Third-person player and AI: run, jump, freefall, parachute, fire and reload. | Arms/legs transition smoothly; recoil and reload poses play; weapon remains attached/visible during airborne movement. | 60 fps screen recording |
| QA-28 | Minimap | Visit lake, river crossing and all five named POIs; move and rotate camera. | Water, bridge and landmark markers align with the 3D world and update with player movement. | Map screenshots + coordinates |
| QA-29 | Frame pacing | Compare 10-minute matches before/after V2 on the same low/mid-range device. | No actor-array concatenation in frame/AI loops; HUD/minimap updates remain responsive with lower CPU overhead. | Perfetto trace + FPS capture |
| QA-30 | Squad AI animation | TDM allies and enemy bots acquire targets, fire, follow and revive/support. | Combat actions animate without breaking movement, targeting or teammate behavior. | Match recording + combat log |
| QA-31 | Explosions / squad friendly fire | Detonate frag and Molotov blasts beside allies and enemies at several distances. | Both allies and enemies receive distance-scaled damage; allies can be downed; player self-damage is unchanged. | Recording + before/after health/state |
| QA-32 | Independent squad AI | Observe assault, support and flanking teammates with enemies at different ranges and with the player moving away. | Teammates independently acquire targets, fire, take cover, flank, regroup only when separated, heal and revive. | Match recording + combat log |
| QA-33 | Lobby controls | Test mode, squad, difficulty, settings, maps, workshop, missions, inventory, daily and start controls on short and wide landscape screens. | Each control performs one action, hit regions do not overlap, map cards scroll and start deploys once. | Device video + control checklist |
| QA-34 | Jump weapon animation | Jump, freefall, open parachute, land, aim and fire in first- and third-person views. | Equipped weapon and hand remain visible and follow jump/aim/fire poses; weapon is hidden only during plane transport and vehicles. | 60 fps screen recording |

V2 and feedback-completion static checks verify source invariants only. QA-27 through QA-34 require physical-device gameplay verification.


## V6 command-deck and AI efficiency regression gate

| ID | Area | Test | Expected result | Evidence |
|---|---|---|---|---|
| QA-35 | Lobby rendering | Leave the lobby open for 5 minutes, open/close the operator hub, then deploy. | Operator preview stays capped near 20 fps, stops when hidden/deployed, and releases its WebGL context; no second-context leak or visual freeze. | GPU profiler + screen recording |
| QA-36 | Squad tactics | Observe assault, support and flank allies with enemies near/far from the player, including target death and no-target intervals. | Roles select targets with distinct priorities, cached target scans refresh at 160 ms, line-of-sight is checked only when firing, and allies regroup/heal/revive as before. | Match recording + CPU trace + combat log |
| QA-37 | Lobby accessibility | Navigate lobby settings, map cards and dock controls using keyboard Enter/Space and touch. | Interactive controls expose button semantics, receive visible focus, and retain their original actions. | Accessibility scan + screen recording |

QA-35 through QA-37 require physical-device verification. CI checks the source invariants and JavaScript syntax only.

## V6.1 regression coverage

- Confirm two starting weapon slots are visible during the aircraft jump and remain equipped on landing; collect and swap ground weapons.
- Hold RUN continuously, release/cancel touch, switch to vehicle controls, and verify no stuck movement/fire input.
- Hold left/right PEEK and verify the third-person shoulder camera shifts and recenters.
- Verify control opacity prioritizes movement/fire/vehicle actions and the remaining controls fade without losing touch hit targets.
- Open every lobby settings subsection and map selector at short landscape heights; verify independent scrolling, no overlap and reachable Deploy/navigation.
- Compare water ripple/shimmer, tree roots/branches, instanced grass and vehicle trim at Low/Medium/High settings; check frame pacing.
- Verify all 17 operator profiles across Kenney and KayKit rigs, correct hand weapon attachment, enemy hit registration and animation-family isolation.
- Trigger spawn, combat, reload, low-health, cover, victory and defeat voice events; verify mute, cooldown and priority behavior.


| QA-37 | Vehicle handling | Drive each ground vehicle at low/high speed; apply brake from forward and reverse motion; release controls; hit an obstacle; destroy the vehicle; attempt to accelerate and exit. | Brake reduces speed to zero without reversing, coasting decays smoothly, speed remains bounded, collision damage is cooldown-limited, and a destroyed vehicle stays immobilized while exit remains usable. | Device video + vehicle speed/health state + logcat |


| QA-38 | Terrain materials | Compare all three maps in low-quality and high-quality modes on low/mid/high Android devices; inspect grass, soil, sand, bark, rock, asphalt and concrete under daylight and shadows. | High quality shows subtle surface relief without visible tiling/overblown normals; low quality omits height-map GPU cost while retaining base color and roughness; no texture load errors or sustained frame drops. | Matched screenshots + 10-minute Perfetto/FPS capture + logcat |


| QA-39 | Vehicle visual feedback | Drive forward/reverse and steer at low/high speed across each ground-vehicle type; stop and change direction. | Wheel rotation follows signed speed, front wheels visibly steer, body lean stays subtle and stable, and vehicle/player position remains synchronized. | Device screen recording at 60 fps |


| QA-40 | Operator gear silhouettes | Preview and spawn all 17 operators; inspect each in idle, run, jump, freefall, shoot and reload on a low/mid/high Android device. | Eight equipment styles remain distinct; headwear, masks, radios, shoulder plates and packs stay attached without clipping or animation detachment; no material/geometry errors or noticeable frame-time regression. | Operator roster screenshots + animation screen recordings + logcat/FPS capture |
