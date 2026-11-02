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
