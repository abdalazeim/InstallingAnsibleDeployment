# Legacy Semaphore control plane (historical)

`control-plane/` predates the supported setup in `semaphore/setup/`. It is kept
for history and must not be used for new installations.

`key-acess.txt` is a local credential note. It is no longer tracked by Git and
must never be committed. If it was ever pushed to a remote repository:

1. Rotate the Semaphore admin password.
2. Rotate `SEMAPHORE_ACCESS_KEY_ENCRYPTION` (encrypted access keys may need to
   be re-entered after rotation).
3. Remove the file from the remote history with a reviewed history rewrite, or
   treat all values in it as compromised.
4. Keep the replacement values in a password manager, not in this directory.

Do not copy these values into inventories, playbooks, reports, issues or chat.
