# Django application lifecycle

Role: `roles/django/` · operations: **11** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/django/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `django.list_applications` | Django - List Applications | `read` | `playbooks/django/list_applications.yml` |
| `django.status` | Django - Application Status | `read` | `playbooks/django/status.yml` |
| `django.health_check` | Django - Health Check | `read` | `playbooks/django/health_check.yml` |
| `django.restart_gunicorn` | Django - Restart Gunicorn | `change` | `playbooks/django/restart_gunicorn.yml` |
| `django.migrate` | Django - Run Migrations | `destructive` | `playbooks/django/migrate.yml` |
| `django.collectstatic` | Django - Collect Static | `change` | `playbooks/django/collectstatic.yml` |
| `django.deploy` | Django - Deploy Application | `change` | `playbooks/django/deploy.yml` |
| `django.update` | Django - Update Application | `change` | `playbooks/django/update.yml` |
| `django.backup_database` | Django - Backup Database | `change` | `playbooks/django/backup_database.yml` |
| `django.backup_media` | Django - Backup Media | `change` | `playbooks/django/backup_media.yml` |
| `django.restore` | Django - Restore Backup | `destructive` | `playbooks/django/restore.yml` |

## Inputs

### `django.status`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

### `django.health_check`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

### `django.restart_gunicorn`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

### `django.migrate`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

### `django.collectstatic`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

### `django.deploy`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |
| `deployment_version` | yes | free-form (validated) |

### `django.update`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |
| `deployment_version` | yes | free-form (validated) |

### `django.backup_database`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

### `django.backup_media`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |

### `django.restore`

| Variable | Required | Values |
|---|---|---|
| `django_application` | yes | free-form (validated) |
| `restore_database` | yes | free-form (validated) |
| `database_backup_id` | yes | free-form (validated) |
| `media_backup_id` | yes | free-form (validated) |
| `restore_destination` | yes | free-form (validated) |

## Behaviour and safety

- Applications are selected from `django_applications`. Each entry declares
  `mode`, `directory`, `user`, `service`, `health_url` and environment.
- `Django - Run Migrations` is destructive and requires
  `deployment_backup_verified=true`. It runs `manage.py migrate --noinput` as
  the application user.
- `Django - Collect Static` and migrations are `native`-mode operations.
- Deploy/update take an explicit `deployment_version`; no `latest` shortcut.
- Restore requires database and media backup identifiers plus a new
  destination. Secrets are never printed (`no_log`).

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
