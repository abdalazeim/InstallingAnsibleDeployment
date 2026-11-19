# Read-only health and capacity checks

Role: `roles/monitoring/` · operations: **6** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/monitoring/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `monitoring.server_health` | Monitoring - Server Health | `read` | `playbooks/monitoring/server_health.yml` |
| `monitoring.resources` | Monitoring - CPU and RAM | `read` | `playbooks/monitoring/resources.yml` |
| `monitoring.disk` | Monitoring - Disk Usage | `read` | `playbooks/monitoring/disk.yml` |
| `monitoring.docker` | Monitoring - Docker Health | `read` | `playbooks/monitoring/docker.yml` |
| `monitoring.applications` | Monitoring - Application Health | `read` | `playbooks/monitoring/applications.yml` |
| `monitoring.overview` | Monitoring - Infrastructure Overview | `read` | `playbooks/monitoring/overview.yml` |

## Inputs

### `monitoring.applications`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

## Behaviour and safety

- All operations are read-only and safe to schedule.
- `Monitoring - CPU and RAM`, `Disk Usage`, `Docker Health` and
  `Application Health` cover the routine alert signals.
- `Monitoring - Infrastructure Overview` aggregates the other checks for a
  quick review.
- These operations write aggregate statistics through the report callback; they
  do not change the host.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
