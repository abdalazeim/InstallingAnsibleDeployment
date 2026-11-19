# Architecture

## 1. Goals

Provide one operation model for Ubuntu infrastructure that can be executed from
Semaphore UI, the CLI, or an API client, with the same safety rules everywhere.
The platform must be portable: no developer host, IP address, hostname,
application path or credential is embedded in tracked files.

## 2. Layers

```text
                 ┌───────────────────────────────┐
                 │ Semaphore UI / CLI / Jenkins  │  interfaces
                 └───────────────┬───────────────┘
                                 ▼
                 ┌───────────────────────────────┐
                 │ semaphore/templates/          │  operation catalog
                 │ catalog.json (98 operations)  │  single source of truth
                 └───────────────┬───────────────┘
                                 ▼
                 ┌───────────────────────────────┐
                 │ playbooks/<group>/<op>.yml    │  one playbook per operation
                 │   pre_tasks: roles/common     │  policy gate
                 │   role tasks                  │  implementation
                 │   import: playbooks/_guard    │  fail closed on empty targets
                 └───────────────┬───────────────┘
                                 ▼
        ┌────────────┬───────────┴───────────┬──────────────┐
        ▼            ▼                       ▼              ▼
   roles/<group>  library/*.py       plugins/callback   inventories + vars
   defaults,      postgres, archive, aggregate JSON     environment and
   templates,     addons, TLS        reports            instance data
   handlers
```

## 3. Operation catalog

`semaphore/templates/catalog.json` is the contract. Each entry declares:

- a stable operation ID (`docker.restart_container`);
- a display name used in Semaphore (`Docker - Restart Container`);
- a group/view (`docker`);
- a playbook path (`playbooks/docker/restart_container.yml`);
- a risk level (`read`, `change`, `destructive`);
- typed inputs with a `required` flag and optional enum choices;
- `become` intent.

The CLI loads the same catalog, so a new operation cannot exist in only one
interface. `scripts/validation/validate.py` checks catalog/playbook/file
consistency, risk parity, the safety pre-task and the empty-target guard.

## 4. Safety gate

`roles/common/tasks/main.yml` runs before any operation role task:

1. The target is Ubuntu 22.04 or 24.04.
2. `infrastructure_environment` is one of build/dev/staging/prod.
3. `read` operations need no confirmation.
4. `change` operations need `confirm_operation=true`.
5. `destructive` operations also need `confirm_destructive_operation=true`.
6. Mutating production operations need `confirm_production=true`.
7. Mutating a local containerized runner is refused; use an SSH target.

`playbooks/_guard.yml` is imported at the end of every catalog playbook. It runs
on the controller and fails when the requested inventory/limit matches no host.
Without it, Ansible skips a play with no hosts and reports success.

Confirmations are survey fields in Semaphore, `--set key=value` in the CLI, and
extra variables for an API client. They are never stored enabled in a Semaphore
environment, so a single click cannot bypass them.

## 5. Data model

Instance definitions are maps in inventory or host variables:

| Map | Used by | Key fields |
|---|---|---|
| `postgres_instances` | PostgreSQL, Odoo, Django, backup | `mode`, `host`, `port`, `user`, `password`, `backup_root` |
| `odoo_instances` | Odoo, backup | `mode`, `container`, `database`, `postgres_instance`, `filestore`, `compose_directory`, `health_url` |
| `django_applications` | Django, backup, monitoring | `mode`, `directory`, `user`, `repository`, `revision`, `environment`, `wsgi`, `health_url` |

Odoo and Django allow several independent instances per host. Odoo version is
data, not code: adding Odoo 20 later means adding an `odoo_instances` entry.

## 6. Reporting

`plugins/callback/infrastructure_report.py` writes aggregate JSON statistics to
`INFRASTRUCTURE_REPORT_DIR` (or `/reports` when mounted, otherwise
`./reports`). It records run ID, operation, completion time and per-host task
counts. It never writes variables, task output or credentials. Files are created
`0600` inside a `0700` directory.

## 7. Interfaces

| Interface | Responsibility |
|---|---|
| Semaphore | Ansible execution, inventories, key store, templates, schedules, task history |
| `infrastructure-manager` | allowlisted local CLI; same catalog and confirmations |
| `infrastructure-semaphore` | idempotent API provisioning of project resources |
| Jenkins | CI/CD and release pipelines; calls Semaphore, does not run Ansible |
| Django (future) | talks to the Semaphore API; does not execute shell on hosts |

The `infrastructure-manager` CLI runs `ansible-playbook` with an argv list
(never a shell), and only for catalog operations. It cannot execute arbitrary
commands.

## 8. Trust boundaries

- The Semaphore API is loopback-only in the shipped Compose file. Remote access
  goes through an SSH tunnel or TLS. Redirects are refused so the bearer token
  cannot leak to another origin.
- The Docker socket is not mounted into Semaphore.
- SSH host keys must be trusted; host-key checking stays enabled.
- Credentials live in Ansible Vault, the Semaphore Key Store, or the caller's
  environment, never in tracked files.
- Backups are confined to an absolute dedicated root, checksummed, and restored
  only into a new destination.

## 9. Repository layout

```text
ansible.cfg               project configuration
requirements.yml          pinned collections (collections/ is a compatibility symlink)
installation/             install, preflight, verify, uninstall
inventories/{build,dev,staging,prod}/   hosts and group_vars
group_vars/ host_vars/    shared and host data (secrets ignored)
playbooks/<group>/        one playbook per catalog operation
playbooks/_guard.yml      empty-target guard
playbooks/semaphore/      API connectivity utility
roles/<group>/            reusable role per module
library/                  Python modules
plugins/callback/         aggregate report callback
infrastructure_manager/   CLI and Semaphore provisioner
semaphore/                setup, catalog, examples, environment notes
jenkins/                  pipelines and shared library
scripts/validation/       structural validator
scripts/reporting/        catalog documentation renderer
tests/                    syntax, unit, security, integration, idempotency
docs/                     this documentation
legacy/                   preserved historical trees, unsupported
```

## 10. Design decisions and limits

- **One catalog, many templates.** Semaphore templates are generated per
  environment. Odoo versions share a template and select an instance, which
  avoids template explosion.
- **Fail closed.** No hosts means failure, not success.
- **Read-only by default.** 48 of 98 operations are reads; mutations require
  explicit confirmation.
- **No live validation claimed.** Local syntax, lint, unit and security checks
  exist. Clean-host integration, real backups/restores and live Semaphore
  provisioning are tracked in `FINAL_IMPLEMENTATION_REPORT.md`.
- **Historical code preserved.** `legacy/` is excluded from lint and tests. It is
  a reference, not a supported path.
