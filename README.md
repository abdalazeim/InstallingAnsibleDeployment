<div align="center">

# Infrastructure Automation Platform

**Ansible operations and Semaphore UI for Ubuntu Server fleets**

[![Ansible](https://img.shields.io/badge/Ansible-automation-EE0000?logo=ansible&logoColor=white)](https://docs.ansible.com/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20%7C%2024.04-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/server)
[![Semaphore](https://img.shields.io/badge/Semaphore-2.19.12-6C4EE3)](https://semaphoreui.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

> **Status: development.** The operation catalog, roles, library modules and
> Semaphore provisioner exist and pass local structural checks. They have **not**
> been validated on a clean Ubuntu server, against a live Semaphore instance, or
> with real backup/restore drills. No test result is claimed beyond what is
> listed in [Validation](#12-validation). Read the [roadmap](#15-status-and-roadmap)
> before using this on production servers.

## 1. Overview

This repository turns a set of Ansible playbooks into an operations platform:
a single **operation catalog** drives the CLI and Semaphore UI, and every
operation passes through one safety gate before it can change a server.

- **Supported entry point:** root `playbooks/`, `roles/`, `inventories/`,
  `library/`, `semaphore/`, `installation/`.
- **UI and execution:** Semaphore 2.19.12, provisioned through its HTTP API.
- **Targets:** Ubuntu Server 22.04 / 24.04, amd64 or arm64, localhost or SSH.
- **Historical code:** the former `InfrastructureAutomation/`, `02-Integration/`,
  `automation/`, `01-Installation/` and `control-plane/` trees were moved to
  `legacy/`. They are preserved but are not part of the supported path. Do not
  mix their configuration files with root.

## 2. Architecture

```text
Semaphore UI / infrastructure-manager CLI
        │
        ▼
semaphore/templates/catalog.json      98 operations, one source of truth
        │
        ▼
playbooks/<group>/<operation>.yml      validate inputs → apply policy → run role
        │
        ├── roles/common                Ubuntu 22.04/24.04, confirmation flags
        ├── roles/<group>               operation implementation
        ├── library/infrastructure_*    PostgreSQL, archives, addons, TLS
        └── plugins/callback            aggregate JSON reports
        │
        ▼
playbooks/_guard.yml                  fail closed when no target is selected
```

### Operation groups

| Group | Operations | Main content |
|---|---:|---|
| Ubuntu Server Management | 12 | facts, updates, users, SSH, UFW, monitoring |
| Docker Infrastructure | 20 | install, containers, images, networks, Compose |
| Odoo Management | 13 | isolated instances, lifecycle, DB/filestore backups, addons |
| PostgreSQL Administration | 11 | databases, roles, privileges, backup/restore/verify |
| Traefik & Networking | 10 | deploy, routers, TLS, DNS, ports, connectivity |
| Django Applications | 11 | deploy, release symlink, migrations, media/DB backup |
| Jenkins Integration | 7 | status, jobs, trigger, build status, integration test |
| Backup & Recovery | 8 | full/PostgreSQL/Odoo/Django, list, verify, restore, retention |
| Monitoring & Health Checks | 6 | server, resources, disk, Docker, applications, overview |

### Risk model

| Risk | Count | Requirement |
|---|---:|---|
| `read` | 48 | none |
| `change` | 39 | `confirm_operation=true`, plus `confirm_production=true` on prod |
| `destructive` | 11 | `confirm_destructive_operation=true` in addition |

Confirmations are validated by `roles/common` before any role task runs and are
never stored enabled in a Semaphore environment. Destructive schedules are
refused by the provisioner.

## 3. Requirements

- Ubuntu Server 22.04 or 24.04, amd64/arm64.
- `sudo` for the initial install; `INSTALL_USER` or `SUDO_USER` must be a
  non-root operator account.
- Outbound HTTPS for apt, PyPI and Ansible Galaxy.
- SSH reachability and trusted host keys for remote targets.
- Docker only when using the Docker/Semaphore components; Ansible itself is
  installed natively, not in Docker.

## 4. Installation

`installation/install.sh` is idempotent and refuses unsafe targets:

```bash
sudo INSTALL_USER="$USER" bash installation/install.sh
```

It performs preflight, installs OS prerequisites, creates an isolated Python
3.12 environment with `uv`, installs pinned `ansible-core`, the repository
package, and collections from the root `requirements.yml`, then writes
`/etc/infrastructure-manager/project-path` and runs `installation/verify.sh`.

It deliberately does **not** install or modify Docker, PostgreSQL, Odoo,
Jenkins or Traefik. Those are optional operations from the catalog.

Verification only:

```bash
bash installation/verify.sh
ansible-playbook -i inventories/build/hosts.yml playbooks/system/verify.yml
```

## 5. Configuration

### Inventories

| Environment | File | Notes |
|---|---|---|
| Build | `inventories/build/hosts.yml` | installation verification / optional smoke |
| Dev | `inventories/dev/hosts.yml` | localhost by default |
| Staging | `inventories/staging/hosts.yml` | empty until configured |
| Prod | `inventories/prod/hosts.yml` | empty until configured |

An empty inventory now **fails** through `playbooks/_guard.yml`; a skipped play
is never reported as success.

`ansible.cfg` uses `inventories/dev/hosts.yml` by default. Semaphore passes the
selected inventory explicitly, so the two do not conflict.

### Instance definitions

Secrets and environment-specific values belong in `host_vars/<host>.yml`
(ignored by Git) or Ansible Vault. Shape:

```yaml
# host_vars/example.yml — placeholders only
postgres_instances:
  main:
    mode: native              # native | docker
    host: /var/run/postgresql
    port: 5432
    user: odoo
    password: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      ...
    backup_root: /var/backups/infrastructure/postgresql/main

odoo_instances:
  odoo17:
    mode: docker
    container: odoo17
    database: odoo17
    postgres_instance: main
    filestore: /srv/odoo17/filestore
    health_url: https://odoo17.example.com/web/health
    compose_directory: /srv/odoo17
    compose_service: odoo

django_applications:
  example:
    mode: native
    directory: /srv/example
    user: example
    repository: https://example.com/example.git
    revision: main
    environment:
      SECRET_KEY: !vault |
        $ANSIBLE_VAULT;1.1;AES256
        ...
    wsgi: example.wsgi:application
    health_url: https://example.com/health/
```

Never put real credentials or development host details in tracked files. The
`library/` modules read secrets from Ansible secrets or environment, not argv.

## 6. CLI

`infrastructure-manager` is an allowlisted wrapper around the catalog. It always
executes `ansible-playbook` with an argv list, never a shell.

```bash
infrastructure-manager catalog --json
infrastructure-manager system info
infrastructure-manager system update --set upgrade_type=safe --set confirm_operation=true
infrastructure-manager system users list
infrastructure-manager system firewall status
infrastructure-manager docker list
infrastructure-manager docker start my-container --set confirm_operation=true
infrastructure-manager odoo status odoo19
infrastructure-manager odoo backup odoo19 --set confirm_downtime=true
infrastructure-manager postgres databases list
infrastructure-manager postgres backup app --set confirm_operation=true
infrastructure-manager traefik status
infrastructure-manager monitoring health
```

Common options: `--inventory`, `--limit`, `--check`, `--diff`, `--verbose`,
`--timeout`, `--json`, `--plan`, and repeatable `--set key=value`.

`--plan` validates inputs and prints the exact command without executing it.
Mutating operations require explicit confirmation even in check mode.

## 7. Semaphore UI

The supported setup lives in `semaphore/setup/`. Semaphore is pinned to
`2.19.12`; the API provisioner refuses other versions.

```bash
cd semaphore/setup
cp .env.example .env && $EDITOR .env
docker compose up -d

export SEMAPHORE_API_TOKEN='...'
infrastructure-semaphore --config semaphore/setup/config.example.json --plan
infrastructure-semaphore --config semaphore/setup/config.example.json --apply
```

The provisioner creates/updates the `Infrastructure Automation` project,
repository, inventories, environments, views, templates and optional schedules.
It never deletes resources, never rotates existing credentials, and refuses
destructive schedules. See `semaphore/setup/README.md` for report wiring and
remote SSH keys.

**Not yet done:** a live provisioning run and browser verification. The report
returned by the tool explicitly sets `templates_executed_successfully: 0` and
`browser_ui_observed: false` until those checks are performed.

## 8. Jenkins

`roles/jenkins/` implements Ansible-side operations (status, jobs, trigger,
build status, integration test). Jenkins pipelines and shared libraries are
**not implemented yet**; they are tracked in the roadmap. Semaphore remains the
supported executor for Ansible operations. Do not schedule the same operation
in Semaphore, Jenkins and cron simultaneously.

## 9. Safety model

- `roles/common` asserts Ubuntu 22.04/24.04, valid environment, risk ownership,
  and explicit confirmations.
- `playbooks/_guard.yml` refuses an empty target selection, including empty
  inventories and limits that match nothing.
- Destructive operations are opt-in and are refused as schedules.
- `--check`/`--diff` are supported where Ansible supports them; read operations
  run with `check_mode: false` only for non-mutating commands.
- Reports contain aggregate statistics only, never variables or task output.
- Backups are confined to an absolute dedicated root, checksummed, path-safe,
  and restored only into a new destination.
- Production changes require `confirm_production=true`; database restore and
  module upgrades additionally require a verified backup flag.

## 10. Library modules

| Module | Responsibility |
|---|---|
| `infrastructure_postgres` | native/Docker PostgreSQL, identifiers, backup/restore/verify, no passwords in argv |
| `infrastructure_archive` | confined tar backups, manifests, checksums, safe restore, retention |
| `infrastructure_addons` | validate Odoo addon manifests and Python syntax without importing code |
| `infrastructure_tls` | verify certificates against the system trust store and expiry threshold |

## 11. Repository layout

```text
ansible.cfg                  project configuration
installation/                portable install, preflight, verify, uninstall
inventories/{build,dev,staging,prod}/
group_vars/ host_vars/       environment and host data (secrets ignored)
playbooks/<group>/           one playbook per catalog operation
playbooks/_guard.yml         empty-target guard
roles/<group>/               reusable roles and templates
library/                     Python Ansible modules
plugins/callback/            aggregate report callback
infrastructure_manager/      CLI and Semaphore provisioner
semaphore/setup/             Compose, example config, provisioning guide
semaphore/templates/         catalog.json
jenkins/                     pipelines and Semaphore shared-library step
scripts/validation/          local structural validator
scripts/reporting/           template-catalog documentation renderer
tests/{unit,security,syntax,integration,idempotency}/
reports/                     ignored output directory
docs/                        architecture, guides, modules, status, final report
```

Historical trees: everything under `legacy/` (formerly
`InfrastructureAutomation/`, `02-Integration/`, `automation/`,
`01-Installation/` and `control-plane/`).

## 12. Validation

Run locally:

```bash
python3 scripts/validation/validate.py        # YAML, Jinja, catalog, guard
python3 scripts/validation/validate.py --syntax
python3 -m pytest -q
ansible-playbook -i inventories/dev/hosts.yml playbooks/system/info.yml
```

Observed in the current development checkout (Ubuntu 24.04, ansible-core
2.21.5):

| Check | Result |
|---|---|
| `validate.py` | 212 YAML documents, 98 operations, 0 errors |
| `--syntax-check` for all catalog playbooks | 98/98 pass (100 syntax tests) |
| `ansible-lint` | exit 0, 71 non-fatal `var-naming` warnings |
| full test suite | 142 passed, 3 skipped (opt-in integration/idempotency) |
| read-only `system/info.yml` on localhost | pass (`ok=7 failed=0`) |
| empty staging inventory | exit 2, fail-closed ("No hosts match") |
| Semaphore provisioner `--plan` | 98 operations, 392 templates, no API call |
| clean Ubuntu install / idempotency / live Semaphore run | **not performed** |

Details and exact acceptance steps: `docs/FINAL_IMPLEMENTATION_REPORT.md`.

## 13. Security

- Never commit passwords, private keys, production `.env` files or tokens.
- Use Ansible Vault, Semaphore Key Store or environment variables.
- Host-key checking stays enabled; historical inventories that disabled it are
  not supported.
- The Semaphore API is loopback-only in the shipped Compose file; use an SSH
  tunnel for remote access.
- The Docker socket is intentionally not mounted into Semaphore.
- Rotate any credential that was ever committed. See
  `legacy/control-plane/semaphore/README.md`.
- Run the initial install as `sudo`, but install Python packages as the operator
  account; do not use `sudo pip`.

## 14. Troubleshooting

| Symptom | Check |
|---|---|
| `No hosts match ...` | configure the inventory or limit; this is the expected fail-closed message |
| `Operation blocked` | pass `confirm_operation=true`; for prod also `confirm_production=true` |
| `Supported target is Ubuntu 22.04/24.04` | the selected host is the Semaphore container or another distribution |
| `container_name is required` | operation inputs are not optional; use `--set` or the Semaphore survey |
| Semaphore provisioning refuses the version | only `2.19.12` is supported by the provisioner contract |
| API redirect refused | the API must be HTTPS or loopback HTTP; redirects can leak the token |
| Reports missing in Semaphore | verify `INFRASTRUCTURE_REPORT_DIR` and the `/reports` mount |
| `pytest: command not found` | run inside the installed `.venv` or install test extras |

## 15. Status and roadmap

Implemented and locally checked:

- Catalog, 98 playbooks, 9 operation roles plus `common`, 4 library modules,
  CLI, Semaphore provisioner, empty-target guard, report callback, install
  scripts, validator, lint configuration, documentation and five test suites.
- 142 tests pass, 3 opt-in integration/idempotency tests skip, `ansible-lint`
  exits 0 and every catalog playbook passes `--syntax-check`.

Pending on real infrastructure:

1. Clean Ubuntu 22.04/24.04 install and an idempotent re-run.
2. Live Semaphore deployment, `--apply`, template/UI read-back and task history.
3. Docker/PostgreSQL/Odoo/Django/Traefik operations on disposable hosts.
4. Backup/verify/restore drill with real data.
5. Jenkins pipeline execution in a real Jenkins instance.

The exact evidence and acceptance procedure are in
`docs/FINAL_IMPLEMENTATION_REPORT.md`. Do not mark a pending item as done
without its real output.

## 16. Historical documentation

- `INSTALLATION_GUIDE.md`, `INSTALLATION_REPORT.md`, `VERSION_INFO.md` —
  historical Phase 1 records.
- `InstallingAnsibleCommand.md` — Arabic command reference.
- `docs/PROJECT_STUDY_AR.md` — file-level study of the old tree.
- `docs/REPOSITORY_AUDIT.md` — audit findings and preservation map.
- `legacy/02-Integration/README_AR.md` — old Arabic integration guide.

## 17. References

- [Ansible documentation](https://docs.ansible.com/)
- [Semaphore documentation](https://docs.semaphoreui.com/)
- [Ubuntu Server](https://ubuntu.com/server)
- [Repository](https://github.com/abdalazeim/InstallingAnsibleDeployment)
