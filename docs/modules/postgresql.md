# PostgreSQL administration

Role: `roles/postgresql/` · operations: **11** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/postgresql/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `postgresql.health_check` | PostgreSQL - Status | `read` | `playbooks/postgresql/health_check.yml` |
| `postgresql.list_databases` | PostgreSQL - List Databases | `read` | `playbooks/postgresql/list_databases.yml` |
| `postgresql.database_info` | PostgreSQL - Database Information | `read` | `playbooks/postgresql/database_info.yml` |
| `postgresql.connections` | PostgreSQL - Connections | `read` | `playbooks/postgresql/connections.yml` |
| `postgresql.create_database` | PostgreSQL - Create Database | `change` | `playbooks/postgresql/create_database.yml` |
| `postgresql.delete_database` | PostgreSQL - Delete Database | `destructive` | `playbooks/postgresql/delete_database.yml` |
| `postgresql.backup` | PostgreSQL - Backup Database | `change` | `playbooks/postgresql/backup.yml` |
| `postgresql.restore` | PostgreSQL - Restore Database | `destructive` | `playbooks/postgresql/restore.yml` |
| `postgresql.verify_backup` | PostgreSQL - Verify Backup | `read` | `playbooks/postgresql/verify_backup.yml` |
| `postgresql.users_manage` | PostgreSQL - User Management | `change` | `playbooks/postgresql/users_manage.yml` |
| `postgresql.privileges` | PostgreSQL - Database Privileges | `change` | `playbooks/postgresql/privileges.yml` |

## Inputs

### `postgresql.health_check`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |

### `postgresql.list_databases`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |

### `postgresql.database_info`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |

### `postgresql.connections`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |

### `postgresql.create_database`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |

### `postgresql.delete_database`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |

### `postgresql.backup`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |

### `postgresql.restore`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |
| `backup_id` | yes | free-form (validated) |

### `postgresql.verify_backup`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `backup_id` | yes | free-form (validated) |

### `postgresql.users_manage`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_username` | yes | free-form (validated) |

### `postgresql.privileges`

| Variable | Required | Values |
|---|---|---|
| `postgres_instance` | yes | free-form (validated) |
| `database_name` | yes | free-form (validated) |
| `database_username` | yes | free-form (validated) |

## Behaviour and safety

- Operations select an instance from `postgres_instances`; the password is
  passed through Ansible and never as a process argument.
- Database and user names must match `^[A-Za-z_][A-Za-z0-9_-]{0,62}$`.
- `PostgreSQL - Delete Database` and `PostgreSQL - Restore Database` are
  destructive and require destructive confirmation.
- Restore uses verified `backup_id` values from the backup output.
- `PostgreSQL - Verify Backup` checks checksum, size, metadata and archive
  integrity; a failed verification must be treated as a failed backup.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
