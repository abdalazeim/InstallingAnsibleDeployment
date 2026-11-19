# Ubuntu server management

Role: `roles/system/` · operations: **12** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/system/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `system.info` | System - Information | `read` | `playbooks/system/info.yml` |
| `system.verify` | System - Verify | `read` | `playbooks/system/verify.yml` |
| `system.health_check` | System - Health Check | `read` | `playbooks/system/health_check.yml` |
| `system.monitoring` | System - Resource Monitoring | `read` | `playbooks/system/monitoring.yml` |
| `system.update` | System - Update Packages | `change` | `playbooks/system/update.yml` |
| `system.packages` | System - Manage Packages | `change` | `playbooks/system/packages.yml` |
| `system.users_list` | System - User List | `read` | `playbooks/system/users_list.yml` |
| `system.users_manage` | System - User Management | `change` | `playbooks/system/users_manage.yml` |
| `system.ssh_status` | System - SSH Status | `read` | `playbooks/system/ssh_status.yml` |
| `system.ssh_configure` | System - SSH Configuration | `change` | `playbooks/system/ssh_configure.yml` |
| `system.firewall_status` | System - Firewall Status | `read` | `playbooks/system/firewall_status.yml` |
| `system.firewall_manage` | System - Firewall Management | `destructive` | `playbooks/system/firewall_manage.yml` |

## Inputs

### `system.update`

| Variable | Required | Values |
|---|---|---|
| `upgrade_type` | no | `safe`, `dist`, `no` |
| `confirm_reboot` | no | free-form (validated) |

### `system.packages`

| Variable | Required | Values |
|---|---|---|
| `package_names` | yes | free-form (validated) |
| `package_state` | no | `present`, `latest`, `absent` |

### `system.users_manage`

| Variable | Required | Values |
|---|---|---|
| `managed_username` | yes | free-form (validated) |
| `managed_user_state` | no | `present`, `absent` |

### `system.ssh_configure`

| Variable | Required | Values |
|---|---|---|
| `ssh_access_verified` | yes | free-form (validated) |
| `ssh_port` | no | free-form (validated) |

### `system.firewall_manage`

| Variable | Required | Values |
|---|---|---|
| `firewall_state` | no | `enabled`, `disabled` |

## Behaviour and safety

- `System - Update Packages` runs `apt` upgrade and reboots only when
  `/var/run/reboot-required` exists **and** `confirm_reboot=true`.
- `System - User Management` rejects `root`, the connection account and the
  current user. It never removes home data and validates sudoers with `visudo`.
- `System - SSH Configuration` requires `ssh_access_verified=true` before it
  changes the SSH port or hardening options.
- `System - Firewall Management` is destructive: it adds allow rules for the
  current and configured SSH ports before applying state, rejects deny rules for
  those ports, and requires destructive confirmation.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
