# Vault (Phase 2, gated)
Store secrets with **Ansible Vault**. Never commit plaintext secrets, vault passwords, or `.env` files with credentials.
- Example: `ansible-vault create vault/secrets.yml` (after Phase 1 PASS, on a secured workstation)
- Keep `vault/.vault_pass` local only (gitignored) if used; prefer prompted/CI secret managers.