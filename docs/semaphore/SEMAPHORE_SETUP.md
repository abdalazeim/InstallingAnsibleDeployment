# Semaphore setup (pinned to 2.19.12)

This is the operational guide for making **Infrastructure Automation** the
execution UI. It documents the supported setup in `semaphore/setup/` and the
API provisioner in `infrastructure_manager/semaphore.py`.

> **Current verification status:** the provisioner, Compose file and catalog are
> checked locally; no live Semaphore server has been provisioned from this
> checkout. The first real run is an acceptance test. Do not report templates as
> verified until they appear in the UI and run successfully.

## 1. What Semaphore owns

Semaphore owns Ansible execution: projects, repositories, inventories, task
environments, key store entries, templates, task history and schedules.

Jenkins is separate: it owns CI, builds, Git-triggered workflows and release
pipelines. Jenkins may *call* Semaphore, but must not execute the same Ansible
operation on the same schedule. See `docs/architecture/ARCHITECTURE.md`.

## 2. Files

| File | Purpose |
|---|---|
| `semaphore/setup/compose.yaml` | Semaphore `v2.19.12`, SQLite data volume, loopback-only port, read-only project mount, writable reports mount |
| `semaphore/setup/.env.example` | Compose secrets and host paths |
| `semaphore/setup/config.example.json` | Provisioner configuration |
| `semaphore/templates/catalog.json` | 98 operations; single source of truth |
| `docs/semaphore/TEMPLATES_CATALOG.md` | Generated list of every template, playbook and input |

## 3. Prerequisites

- Ubuntu Server 22.04/24.04 host with Docker Engine and the Compose plugin.
- This repository available at an absolute path (default
  `/opt/InstallingAnsibleDeployment`).
- A non-root operator account; the installer creates
  `/etc/infrastructure-manager/project-path`.
- For remote targets: SSH access, a trusted `known_hosts` file, and a private
  key held in the Semaphore Key Store.
- Outbound HTTPS for Let's Encrypt, package mirrors and image pulls.

## 4. Start Semaphore

```bash
cd semaphore/setup
cp .env.example .env
$EDITOR .env
docker compose up -d
```

Required values in `.env`:

| Variable | Meaning |
|---|---|
| `SEMAPHORE_ADMIN` | first administrator login |
| `SEMAPHORE_ADMIN_PASSWORD` | administrator password (never commit) |
| `SEMAPHORE_ACCESS_KEY_ENCRYPTION` | encryption key for stored credentials |
| `INFRASTRUCTURE_PROJECT` | absolute path to this repository |
| `INFRASTRUCTURE_REPORTS` | writable report directory on the host |
| `SEMAPHORE_KNOWN_HOSTS` | trusted host keys for SSH targets |

Generate the encryption key with a password manager or
`openssl rand -hex 32`. The API is published on `127.0.0.1:3000`; use an SSH
tunnel for remote access. Do not expose port 3000 to the internet and do not
mount the Docker socket into Semaphore.

Check the container:

```bash
docker compose ps
curl --fail http://127.0.0.1:3000/api/info
```

## 5. Create an API token

1. Open `http://127.0.0.1:3000` (or through the tunnel).
2. Sign in as the administrator.
3. Create an API token for the operator.
4. Keep it in a password manager or CI credential store.

The provisioner reads it from `SEMAPHORE_API_TOKEN`. It is never written to the
repository or to reports.

## 6. Provision the project

The provisioner is pinned to server version `2.19.12`. It refuses HTTP on
non-loopback addresses, redirects, unknown operations and permanently enabled
confirmation flags. It creates or updates resources and never deletes them.

Preview without contacting the server:

```bash
python3 -m infrastructure_manager.semaphore \
  --config semaphore/setup/config.example.json
# or: make semaphore-plan
```

Apply:

```bash
export SEMAPHORE_API_TOKEN='...'
# optional, when config.ssh_private_key_env is set
export SEMAPHORE_SSH_PRIVATE_KEY='...'
# optional, when config.vault_password_env is set
export SEMAPHORE_VAULT_PASSWORD='...'

python3 -m infrastructure_manager.semaphore \
  --config semaphore/setup/config.example.json --apply
# or: make semaphore-apply
```

What is reconciled:

| Resource | Name |
|---|---|
| Project | `Infrastructure Automation` |
| Repository | `InstallingAnsibleDeployment` |
| Inventories | `Infrastructure - build/dev/staging/prod` → `inventories/<env>/hosts.yml` |
| Environments | `Infrastructure - <env>` with `ANSIBLE_CONFIG` and `INFRASTRUCTURE_REPORT_DIR` |
| Views | one per operation group |
| Templates | one per operation × environment, named `<operation> [<env>]` |
| Schedules | only from `config.schedules`, inactive unless `--enable-schedules` |

The JSON report is written to `reports/semaphore-provisioning.json`. It sets
`templates_executed_successfully: 0` and `browser_ui_observed: false` until a
real run and UI check are performed.

## 7. Repository modes

### Local checkout (default example)

`compose.yaml` mounts `INFRASTRUCTURE_PROJECT` at `/workspace` read-only, and
`config.example.json` uses `"repository_url": "/workspace"`. This is the
smallest setup and matches the provisioner defaults.

### GitHub over SSH

```json
{
  "repository_url": "git@github.com:abdalazeim/InstallingAnsibleDeployment.git",
  "repository_branch": "main",
  "git_key_id": null
}
```

Create a deploy key in the Semaphore Key Store and set `git_key_id` to its ID.
Never place the private key or a GitHub token in the repository. After changing
the branch, re-run `--apply`.

### Remote targets

The example config leaves SSH and Vault key environment names unset, so
inventories are created with the "no credentials" key. For SSH targets:

```json
{
  "ssh_private_key_env": "SEMAPHORE_SSH_PRIVATE_KEY",
  "vault_password_env": "SEMAPHORE_VAULT_PASSWORD",
  "ssh_login": "ubuntu"
}
```

Populate the same host key in `SEMAPHORE_KNOWN_HOSTS`. Host-key checking must
stay enabled.

## 8. Inventories

| Environment | File | Notes |
|---|---|---|
| build | `inventories/build/hosts.yml` | localhost for installation verification; replace with SSH inside containers |
| dev | `inventories/dev/hosts.yml` | localhost by default |
| staging | `inventories/staging/hosts.yml` | empty until configured |
| prod | `inventories/prod/hosts.yml` | empty until configured |

An empty inventory fails through `playbooks/_guard.yml`. Semaphore reports the
failure; it is never treated as a successful no-op. Add hosts under
`all.children.managed.hosts` with `ansible_host`, `ansible_user`, `ansible_port`
and a trusted host key.

## 9. Environments and Key Store

The provisioner stores only non-secret defaults in the environment:

- `infrastructure_environment=<env>`
- `confirm_operation=false`
- `confirm_production=false`
- `confirm_destructive_operation=false`
- `confirm_reboot=false`
- optional values from `environment_variables.<env>`

Secrets belong in the Key Store:

| Key Store entry | Type | Used for |
|---|---|---|
| `Infrastructure - No credentials` | none | localhost and SSH agent setups |
| `Infrastructure - SSH` | SSH | remote inventory access |
| `Infrastructure - Vault` | login/password | Ansible Vault password |

The provisioner reuses an existing credential by name and does **not** rotate
it. Rotate credentials manually in the UI and in the password manager.

## 10. Templates and surveys

Every template is created from the catalog. Inputs become required/optional
survey fields; enum inputs become dropdowns. Change and destructive operations
also receive confirmation fields:

| Field | Values | Applies to |
|---|---|---|
| `confirm_operation` | `false` / `true` | change and destructive |
| `confirm_destructive_operation` | `false` / `true` | destructive |
| `confirm_production` | `false` / `true` | change/destructive on prod |

The playbooks validate these values in `roles/common` before any role task runs.
Nothing in a survey accepts a shell command; inputs are Ansible variables only.

The complete list is in `docs/semaphore/TEMPLATES_CATALOG.md`. Odoo 17 and Odoo
19 share one template per operation and select the instance with
`odoo_instance`; add new versions through inventory data, not new playbooks.

## 11. Schedules

Schedules are optional and created only from `config.schedules`. Rules enforced
by the provisioner:

- The operation must be selected in `environments`/`operations`.
- Destructive operations are refused.
- A mutating schedule needs `"approved": true` and an explicit
  `confirm_operation=true` in its variables.
- A production mutating schedule also needs `confirm_production=true`.
- Schedules are inactive unless `--enable-schedules` is passed.

Recommended read-only schedules: server health, resources, disk, Docker health,
application health, SSL expiry, Odoo/PostgreSQL health and backup verification.
Do not schedule the same operation in Semaphore, Jenkins and cron.

## 12. Task history and reports

Semaphore task history shows the template, start time, inventory, target,
status, duration and output. Long-term backup and operation reports are written
by the `infrastructure_report` callback to `INFRASTRUCTURE_REPORT_DIR`, mounted
at `/reports`. Reports contain aggregate statistics only (no variables,
credentials or task output) and are created with mode `0600` in a `0700`
directory.

## 13. API examples

Set the token in the environment; never paste it into a shell history that is
shared or recorded.

```bash
export SEMAPHORE_URL=http://127.0.0.1:3000
export SEMAPHORE_API_TOKEN='...'

# Server information
curl --fail -H "Authorization: Bearer $SEMAPHORE_API_TOKEN" \
  "$SEMAPHORE_URL/api/info"

# Projects
curl --fail -H "Authorization: Bearer $SEMAPHORE_API_TOKEN" \
  "$SEMAPHORE_URL/api/projects"

# Templates in a project (replace PROJECT_ID)
curl --fail -H "Authorization: Bearer $SEMAPHORE_API_TOKEN" \
  "$SEMAPHORE_URL/api/project/PROJECT_ID/templates"

# Run a template (replace PROJECT_ID and TEMPLATE_ID)
curl --fail -X POST \
  -H "Authorization: Bearer $SEMAPHORE_API_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"template_id": TEMPLATE_ID, "environment": "{\"upgrade_type\": \"safe\", \"confirm_operation\": \"true\"}"}' \
  "$SEMAPHORE_URL/api/project/PROJECT_ID/tasks"

# Task status (replace TASK_ID)
curl --fail -H "Authorization: Bearer $SEMAPHORE_API_TOKEN" \
  "$SEMAPHORE_URL/api/project/PROJECT_ID/tasks/TASK_ID"
```

Django (future) and Jenkins integrations should use a token held in their own
secret store and these same endpoints. They must not run Ansible or shell
commands directly on managed hosts.

## 14. Verification checklist

Run this after the first deployment. Record the result honestly.

1. `docker compose ps` shows Semaphore healthy.
2. `GET /api/info` reports `2.19.12`.
3. Provisioner `--apply` exits 0 and writes a report.
4. The project `Infrastructure Automation` appears in the UI.
5. Repository, four inventories and four environments appear.
6. Key Store entries appear (only the ones configured).
7. Nine views appear and templates are grouped correctly.
8. `docs/semaphore/TEMPLATES_CATALOG.md` count matches the UI templates.
9. A read-only template (for example `System - Information [dev]`) runs.
10. Task history shows the task and its output.
11. A change template without confirmation is refused.
12. A change template with confirmation succeeds on a disposable target.
13. A scheduled read-only task appears and is inactive/active as configured.
14. Reports appear under the mounted report directory.
15. `browser_ui_observed` and `templates_executed_successfully` in the report
    are updated only after steps 9–14 actually pass.

`--smoke` runs the read-only build verification template. Use it only after
`inventories/build/hosts.yml` points at a supported Ubuntu target:

```bash
python3 -m infrastructure_manager.semaphore \
  --config semaphore/setup/config.example.json --apply --smoke
```

## 15. Troubleshooting

| Symptom | Check |
|---|---|
| `Provisioner contract is pinned to Semaphore 2.19.12` | upgrade or pin the container image; the contract is intentional |
| `Use HTTPS or an SSH tunnel to a loopback HTTP endpoint` | publish on `127.0.0.1` and tunnel, or terminate TLS |
| `API redirects are refused ...` | point directly at the API, not a redirecting proxy |
| `Credential environment variable is missing` | export the variable named in the config before `--apply` |
| `Confirmation flags cannot be enabled permanently` | remove `confirm_*` from environment variables; use surveys |
| `No hosts match ...` | configure the inventory or limit; this is fail-closed behavior |
| `Supported target is Ubuntu 22.04/24.04` | the selected host is the Semaphore runner container or another OS |
| Template is missing | confirm the operation is selected, the environment is selected and `--apply` completed |
| Task succeeds but report is missing | verify `INFRASTRUCTURE_REPORT_DIR` and the `/reports` mount |
| SSH unreachable | verify the inventory host key, the key-store entry and `SEMAPHORE_KNOWN_HOSTS` |
| Templates exist twice after renaming | the provisioner never deletes; remove duplicates manually after review |
