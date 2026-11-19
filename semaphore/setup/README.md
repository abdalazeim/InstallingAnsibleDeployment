# Semaphore setup — supported path

> Status: the provisioner and Compose definition exist and are covered by local
> structural checks. They have **not** been run against a real Semaphore
> installation in this checkout. Treat the first run as an acceptance test.

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Semaphore `v2.19.12`, SQLite data volume, loopback-only port, read-only project mount, writable `/reports` mount |
| `.env.example` | Required Compose secrets and paths |
| `config.example.json` | Provisioner configuration (project, repository, environments, report path) |

## 1. Start Semaphore

```bash
cd semaphore/setup
cp .env.example .env
# edit .env: set admin email/password, access-key encryption key, paths
docker compose up -d
```

Generate the encryption key with a password manager or:

```bash
openssl rand -hex 32
```

The API is exposed on `127.0.0.1` only. Use an SSH tunnel for remote access;
do not publish port 3000 to the internet.

## 2. Provision project resources

The provisioner talks to the Semaphore HTTP API and is pinned to `2.19.12`.

```bash
export SEMAPHORE_API_TOKEN='...'          # create in Semaphore UI
export SEMAPHORE_SSH_PRIVATE_KEY='...'    # only if config.ssh_private_key_env is set
export SEMAPHORE_VAULT_PASSWORD='...'     # only if config.vault_password_env is set

infrastructure-semaphore --config semaphore/setup/config.example.json --plan
infrastructure-semaphore --config semaphore/setup/config.example.json --apply
```

It creates or updates, never deletes:

- project `Infrastructure Automation`
- repository `InstallingAnsibleDeployment`
- one inventory and environment per selected environment
- one view per operation group
- one template per operation × environment, linked to a real catalog playbook
- optional schedules (inactive unless `--enable-schedules` is given)

Smoke test with the build environment only after `inventories/build/hosts.yml`
points at a supported Ubuntu target:

```bash
infrastructure-semaphore --config ... --apply --smoke
```

The JSON report is written to `report_dir` (`/reports` by default) on the
target and to `reports/semaphore-provisioning.json` locally.

## 3. Report directory

`report_dir` is passed to every Semaphore environment as
`INFRASTRUCTURE_REPORT_DIR`, and `compose.yaml` mounts it at `/reports`.
Playbook statistics are written there by `infrastructure_report` callback as
aggregate JSON only (no variables, task output or credentials).

## 4. Remote targets

The example config leaves SSH/Vault key environment names unset, so inventories
are created with the "no credentials" key. For remote servers:

```json
"ssh_private_key_env": "SEMAPHORE_SSH_PRIVATE_KEY",
"vault_password_env": "SEMAPHORE_VAULT_PASSWORD",
"ssh_login": "ubuntu"
```

Ensure the runner trusts the target host keys in `SEMAPHORE_KNOWN_HOSTS`.
Host-key checking must stay enabled.

## 5. What is not automated

- The Semaphore admin user and API token are created by Semaphore, not by this
  repository. Keep them out of Git.
- First-run UI verification (templates visible, task history, schedules) still
  requires a browser or API read-back on the destination.
- Rotate any credential that was ever committed. See
  `legacy/control-plane/semaphore/README.md`.
