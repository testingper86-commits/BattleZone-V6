# BattleZone V6 encrypted offline backup

The `BATTLEZONE_V6_ENCRYPTED_BACKUP_V1` stage replaces the old reversible Base64 save export with an authenticated encrypted backup code. The code is portable between installations, but it is useless without the passphrase.

## Format

- Cipher: AES-256-GCM with a 128-bit authentication tag.
- Key derivation: PBKDF2-HMAC-SHA256, 310,000 iterations.
- Per-export random salt: 16 bytes.
- Per-export random IV: 12 bytes.
- Passphrase: 12 to 256 characters; it is not persisted or included in the exported code.
- Plaintext and encoded payload size are bounded before processing.

## Restore behavior

- The payload format and version are checked before decryption.
- Authentication failure (wrong passphrase or modified ciphertext) stops before any local save is changed.
- Restored keys must belong to the existing `KEYS` allowlist and values must be strings.
- Storage writes are rolled back to the pre-restore snapshot if a write throws.
- The existing progression normalizers still validate profile and wallet values on startup.

## Validation

`test_v6_encrypted_backup.py` extracts the production helper and runs it under Node WebCrypto. It checks round-trip fidelity, distinct randomized exports, absence of plaintext in the code, short/wrong passphrase rejection, tamper rejection, and unknown-version rejection. The patcher is also tested for idempotence against the current transformed source.

## Explicit limitation

This change encrypts exported/imported backup codes. It does **not** encrypt the game's live `localStorage` values at rest. Those values remain in the Android application's private WebView storage sandbox. Full at-rest encryption requires a separately designed Android Keystore-backed startup/unlock and migration path; it must not be claimed as complete by this backup change.
