# Backup, restore and retention

Role: `roles/backup/` · operations: **8** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/backup/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `backup.full_backup` | Backup - Files Backup | `change` | `playbooks/backup/full_backup.yml` |
| `backup.list` | Backup - List Backups | `read` | `playbooks/backup/list.yml` |
| `backup.verify` | Backup - Verify | `read` | `playbooks/backup/verify.yml` |
| `backup.restore` | Backup - Restore | `destructive` | `playbooks/backup/restore.yml` |
| `backup.retention` | Backup - Retention Cleanup | `destructive` | `playbooks/backup/retention.yml` |
| `backup.postgresql` | Backup - PostgreSQL | `change` | `playbooks/backup/postgresql.yml` |
| `backup.odoo` | Backup - Odoo | `change` | `playbooks/backup/odoo.yml` |
| `backup.django` | Backup - Django Database | `change` | `playbooks/backup/django.yml` |

## Inputs

### `backup.full_backup`

| Variable | Required | Values |
|---|---|---|
| `backup_source` | yes | free-form (validated) |

### `backup.verify`

| Variable | Required | Values |
|---|---|---|
| `backup_id` | yes | free-form (validated) |

### `backup.restore`

| Variable | Required | Values |
|---|---|---|
| `backup_id` | yes | free-form (validated) |
| `restore_destination` | yes | free-form (validated) |

### `backup.postgresql`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |

### `backup.odoo`

| Variable | Required | Values |
|---|---|---|
| `odoo_instance` | yes | free-form (validated) |
| `confirm_downtime` | yes | free-form (validated) |

### `backup.django`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

## Behaviour and safety

- File backups use `infrastructure_archive`, confined to an absolute
  `backup_root`, timestamped and checksummed.
- `Backup - Restore` requires a verified `backup_id` and a new
  `restore_destination`; it never overwrites an existing destination by default.
- `Backup - Retention Cleanup` is destructive and uses `retention_days`
  (build 3 / dev 7 / staging 14 / prod 30 in `group_vars`).
- Database backups delegate to the PostgreSQL, Odoo or Django role so the
  backup format matches the restore path.
- Verify a backup before relying on it: `Backup - Verify` is read-only.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
