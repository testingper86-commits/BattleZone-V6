# V6 Tactical Command Interface

The canonical Android build now applies `scripts/apply_v6_tactical_command_ui.py` after the existing offline, gameplay, reliability, squad-command and lobby patches. The patch extends the existing local player hub into twelve screens: Command Center, Deployment Lobby, Operator Bay, Armory, Squad Command, Mission Zones, Combat HUD, Pause Menu, After Action, Service Record, Settings and Controls.

The implementation reuses the existing profile, cosmetic shop, map selection, squad-order controls and settings handlers. The Combat HUD reads a live snapshot from the game loop. Opening the hub suspends the simulation loop; closing it resumes the game. The After Action screen deliberately displays only verified local progression because the current game does not expose a complete per-match report. No online service, remote asset, account or network dependency is introduced.

The patch is idempotent and is covered by `scripts/test_v6_tactical_command_ui.py`, which runs in the Android GitHub Actions workflow before Gradle tests and APK assembly.
