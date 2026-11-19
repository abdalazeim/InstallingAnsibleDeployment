# Security

## 1. Scope and threat model

This document covers the repository, the Ansible control path, Semaphore, and
the credentials and reports they handle. It assumes:

- The controller host is trusted and accessed by named operators.
- Managed hosts may be remote and reachable over SSH.
- The repository may be public; therefore **no secret may be committed**.
- Semaphore and Jenkins may run on shared infrastructure and must not receive
  more privilege than required.

Out of scope: operating-system hardening beyond the catalog operations, physical
security, network segmentation and identity-provider design.

## 2. Non-negotiable rules

- Never commit passwords, private keys, API tokens, Vault passwords or
  production `.env` files.
- Never print or log credentials. Secret-bearing tasks use `no_log: true`.
- Never disable SSH host-key checking. `ansible.cfg` sets
  `host_key_checking = True`.
- Never mount the Docker socket into Semaphore.
- Never enable confirmation flags permanently in a Semaphore environment.
- Never run the same destructive operation from two schedulers.
- Rotate any credential that was ever committed, even if it was later removed.

## 3. Secret storage

| Secret | Storage |
|---|---|
| SSH private keys | Semaphore Key Store or the operator's SSH agent |
| Ansible Vault password | Semaphore Key Store or a local password manager |
| PostgreSQL passwords | Ansible Vault (`postgres_instances`) |
| Django `SECRET_KEY`, API keys | Ansible Vault (`django_applications.environment`) |
| Semaphore API token | Jenkins credential / Django secret store / operator password manager |
| `SEMAPHORE_ACCESS_KEY_ENCRYPTION` | Compose `.env` with mode `0600`, backed by a password manager |
| Jenkins credentials | Jenkins Credentials store |

The provisioner reads `SEMAPHORE_API_TOKEN`, `SEMAPHORE_SSH_PRIVATE_KEY` and
`SEMAPHORE_VAULT_PASSWORD` from the environment. It never writes them to the
repository or to its JSON report.

## 4. Ansible Vault example

Create an encrypted variables file outside public review:

```bash
ansible-vault create inventories/prod/group_vars/vault.yml
```

Content shape:

```yaml
vault_postgres_main_password: "replace-with-a-generated-password"
vault_django_portal_secret_key: "replace-with-a-generated-key"
```

Reference the vault values from an instance map:

```yaml
postgres_instances:
  main:
    mode: native
    host: /var/run/postgresql
    port: 5432
    user: odoo
    password: "{{ vault_postgres_main_password }}"
```

Run with `--ask-vault-pass`, `--vault-password-file` (mode `0600` outside the
repository), or the Semaphore Vault key. Never commit the password file.

## 5. File permissions

- Report callback output: `0600` files inside a `0700` directory.
- Installation log: `umask 077` in `installation/verify.sh`.
- Vault password files: `0600`, outside the repository.
- Semaphore `.env`: `0600` on the host; `.env` and `.env.*` are ignored except
  `.env.example`.
- SSH private keys: `0600`; public keys `0644`.

## 6. SSH

- Use key authentication. Prefer disabling password authentication only after
  verifying key access; `System - SSH Configuration` requires
  `ssh_access_verified=true`.
- Keep `PermitRootLogin` restricted.
- Trust host keys in `SEMAPHORE_KNOWN_HOSTS` or the operator's
  `~/.ssh/known_hosts`.
- Historical inventories under `legacy/` contain
  `StrictHostKeyChecking=no`; they are unsupported and must not be reused.
- The guard refuses mutating a local containerized runner. Use an SSH target.

## 7. Privilege and sudo

- The installer runs as root but installs Python packages as the operator.
- Do not use `sudo pip`.
- Playbooks use `become: true` only for operations that need it.
- `System - User Management` refuses to modify the connection account in a way
  that could remove access.
- Prefer per-command sudo rules over `NOPASSWD: ALL` on shared hosts.

## 8. Firewall

`System - Firewall Management` is destructive. It must not enable UFW before an
SSH allow rule is verified. The playbook requires explicit destructive
confirmation and validates the requested state.

## 9. Semaphore

- Compose publishes the API on `127.0.0.1` only. Use an SSH tunnel or TLS for
  remote access.
- The provisioner refuses redirects and non-loopback HTTP to protect the token.
- The project pins Semaphore `2.19.12`; other versions are refused rather than
  silently accepted.
- The Docker socket is not mounted.
- Confirmation flags are survey fields, not environment defaults.
- Destructive schedules are refused.
- The provisioner never deletes resources and never rotates credentials.
- `legacy/control-plane/` is historical. Its credential note was untracked;
  treat any value that was ever pushed as compromised.

## 10. Reporting

Reports contain aggregate task statistics only: run ID, operation, completion
time and per-host ok/changed/failed/skipped counts. They never include
variables, task output, credentials or file contents. Keep the report directory
private to the operator and the Semaphore service account.

## 11. Input validation and command execution

- Semaphore survey fields and CLI `--set` values become Ansible variables, never
  shell commands.
- The CLI builds an argv list and never invokes a shell.
- Playbooks validate identifiers, paths, ports, versions and URLs before use.
- Backup and restore modules reject path traversal and confine operations to
  `backup_root`.
- `infrastructure_postgres` passes credentials through Ansible, not argv.

## 12. Backups

- Backups are written under an absolute dedicated root.
- Archives are checksummed and verified before being reported as valid.
- Restore refuses to overwrite an existing destination by default.
- Destructive restore requires `confirm_destructive_operation=true` and, for
  database restores, a verified backup identifier.
- Encrypt backup media at rest and restrict access to the backup directory.

## 13. Rotation and incident response

If a secret may have leaked:

1. Rotate it at the source (database, SSH key, Semaphore token, Vault password,
   Jenkins credential).
2. Update the Vault/Key Store value; do not commit it.
3. Revoke old keys and tokens.
4. Review Semaphore and Jenkins task history and access logs.
5. If a repository history rewrite is required, coordinate it with all clones;
   otherwise treat the value as permanently compromised.
6. Record what was rotated and when in the private operations log.

## 14. Security verification

Local checks:

```bash
python -m pytest -q tests/security
ansible-lint
python scripts/validation/validate.py
```

The tests check for tracked secret files, a tracked credential note, disabled
host-key checking, hardcoded IPv4 addresses outside loopback, default
confirmations, destructive-operation policy, unsafe Semaphore examples, a
mounted Docker socket and fail-closed behavior for empty inventories.

These are static checks. They do not replace host hardening, vulnerability
scanning, access review or a real penetration test.
