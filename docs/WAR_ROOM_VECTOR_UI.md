# War Room / Vector UI

Battle Zone V6 Offline uses a new, standalone command-interface layer for the Android WebView game. The design assets are `app/src/main/assets/www/css/warroom-command.css` and `app/src/main/assets/www/js/warroom-command.js`, installed by `scripts/apply_battlezone_warroom_redesign.py` during the Android build.

The redesign covers the lobby, operator profile strip, match setup cards, map selection, player hub pages, combat HUD, minimap frame, inventory/settings surfaces and touch controls. It uses an offline-first high-contrast field-console palette, responsive layouts, reduced-motion handling and existing game action IDs.

The map command screen reads the actual local `MAPS` configuration and selects a map using the existing location-hash reload path. The Combat Doctrine page stores one of four local doctrines (`balanced`, `aggressive`, `defensive`, `flanking`) and changes the AI bot role assignment at match spawn. It does not add LAN, pairing, online services or fake replay data.

CI applies this patch after offline pairing removal, gameplay overhaul, gameplay quality and offline hub completion. The extracted project validator checks the new assets, map UI marker, doctrine integration and JavaScript syntax.
