# Offline device-pairing removal

The Offline package no longer exposes or implements local device pairing/LAN multiplayer.

Removed from the runtime:
- Nearby Wi-Fi room UI, room host/join/discovery controls, status card and network HUD.
- JavaScript network bridge and multiplayer combat/position relay.
- Remote LAN avatar creation and animation attachment.
- Android TCP/UDP sockets, Wi-Fi multicast handling, password/room/session state and network bridge lifecycle.
- Android INTERNET, network-state, Wi-Fi-state and multicast permissions.
- Obsolete LAN protocol, discovery and multiplayer implementation files.

Preserved:
- Battle Royale, Team Deathmatch and Free-for-All local modes.
- Offline AI enemies and TDM AI teammates.
- Existing player movement, camera, combat, bots, maps, vehicles, safe-zone, progression, settings, sound and bundled assets.

The validator checks that pairing/network hooks and permissions remain absent. A successful build still requires separate physical-device tests for offline launch and gameplay.
