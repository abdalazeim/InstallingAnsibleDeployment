# Odoo instance management

Role: `roles/odoo/` · operations: **13** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/odoo/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `odoo.list_instances` | Odoo - List Instances | `read` | `playbooks/odoo/list_instances.yml` |
| `odoo.start` | Odoo - Start Instance | `change` | `playbooks/odoo/start.yml` |
| `odoo.stop` | Odoo - Stop Instance | `change` | `playbooks/odoo/stop.yml` |
| `odoo.restart` | Odoo - Restart Instance | `change` | `playbooks/odoo/restart.yml` |
| `odoo.health_check` | Odoo - Health Check | `read` | `playbooks/odoo/health_check.yml` |
| `odoo.logs` | Odoo - Logs | `read` | `playbooks/odoo/logs.yml` |
| `odoo.backup_database` | Odoo - Database Backup | `change` | `playbooks/odoo/backup_database.yml` |
| `odoo.backup_filestore` | Odoo - Filestore Backup | `change` | `playbooks/odoo/backup_filestore.yml` |
| `odoo.backup_full` | Odoo - Full Backup | `change` | `playbooks/odoo/backup_full.yml` |
| `odoo.restore` | Odoo - Restore Backup | `destructive` | `playbooks/odoo/restore.yml` |
| `odoo.addons_validate` | Odoo - Addons Validation | `read` | `playbooks/odoo/addons_validate.yml` |
| `odoo.addons_deploy` | Odoo - Deploy Addons | `change` | `playbooks/odoo/addons_deploy.yml` |
| `odoo.update_modules` | Odoo - Update Selected Modules | `destructive` | `playbooks/odoo/update_modules.yml` |

## Inputs

### `odoo.start`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.stop`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.restart`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.health_check`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.logs`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `allow_sensitive_logs` | yes | free-form (validated) |

### `odoo.backup_database`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.backup_filestore`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.backup_full`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `confirm_downtime` | yes | free-form (validated) |

### `odoo.restore`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `bundle_id` | yes | free-form (validated) |
| `restore_database` | yes | free-form (validated) |
| `restore_destination` | yes | free-form (validated) |

### `odoo.addons_validate`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |

### `odoo.addons_deploy`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `addons_repository` | yes | free-form (validated) |
| `addons_revision` | yes | free-form (validated) |

### `odoo.update_modules`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `odoo_modules` | yes | free-form (validated) |
| `confirm_downtime` | yes | free-form (validated) |
| `deployment_backup_verified` | yes | free-form (validated) |

## Behaviour and safety

- Every operation selects an instance from `odoo_instances`. Odoo 17, 19 and
  future versions share the same playbooks: version-specific data lives in the
  instance map, not in code.
- `Odoo - Full Backup` requires `confirm_downtime=true`.
- `Odoo - Update Selected Modules` is destructive and requires
  `confirm_downtime=true`, `deployment_backup_verified=true` and an explicit
  module list. `all` is rejected.
- `Odoo - Restore Backup` requires a verified bundle, a new database name and a
  new restore destination.
- `Odoo - Logs` requires `allow_sensitive_logs=true`.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
