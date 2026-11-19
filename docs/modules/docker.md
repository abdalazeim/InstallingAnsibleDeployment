# Docker Engine and Compose

Role: `roles/docker/` · operations: **20** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/docker/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `docker.install` | Docker - Install | `change` | `playbooks/docker/install.yml` |
| `docker.health_check` | Docker - Health Check | `read` | `playbooks/docker/health_check.yml` |
| `docker.list_containers` | Docker - List Containers | `read` | `playbooks/docker/list_containers.yml` |
| `docker.list_images` | Docker - List Images | `read` | `playbooks/docker/list_images.yml` |
| `docker.resource_usage` | Docker - Resource Usage | `read` | `playbooks/docker/resource_usage.yml` |
| `docker.compose_list` | Docker - List Compose Projects | `read` | `playbooks/docker/compose_list.yml` |
| `docker.start_container` | Docker - Start Container | `change` | `playbooks/docker/start_container.yml` |
| `docker.stop_container` | Docker - Stop Container | `change` | `playbooks/docker/stop_container.yml` |
| `docker.restart_container` | Docker - Restart Container | `change` | `playbooks/docker/restart_container.yml` |
| `docker.pause_container` | Docker - Pause Container | `change` | `playbooks/docker/pause_container.yml` |
| `docker.unpause_container` | Docker - Unpause Container | `change` | `playbooks/docker/unpause_container.yml` |
| `docker.delete_container` | Docker - Delete Container | `destructive` | `playbooks/docker/delete_container.yml` |
| `docker.container_logs` | Docker - Container Logs | `read` | `playbooks/docker/container_logs.yml` |
| `docker.inspect_container` | Docker - Inspect Container | `read` | `playbooks/docker/inspect_container.yml` |
| `docker.update_images` | Docker - Pull Image | `change` | `playbooks/docker/update_images.yml` |
| `docker.network_manage` | Docker - Network Management | `change` | `playbooks/docker/network_manage.yml` |
| `docker.compose_up` | Docker - Compose Up | `change` | `playbooks/docker/compose_up.yml` |
| `docker.compose_down` | Docker - Compose Down | `destructive` | `playbooks/docker/compose_down.yml` |
| `docker.compose_restart` | Docker - Compose Restart | `change` | `playbooks/docker/compose_restart.yml` |
| `docker.compose_update` | Docker - Compose Update | `change` | `playbooks/docker/compose_update.yml` |

## Inputs

### `docker.start_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.stop_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.restart_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.pause_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.unpause_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.delete_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.container_logs`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |
| `allow_sensitive_logs` | no | free-form (validated) |

### `docker.inspect_container`

| Variable | Required | Values |
|---|---|---|
| `container_name` | yes | free-form (validated) |

### `docker.update_images`

| Variable | Required | Values |
|---|---|---|
| `image_reference` | yes | free-form (validated) |

### `docker.network_manage`

| Variable | Required | Values |
|---|---|---|
| `network_name` | yes | free-form (validated) |
| `network_state` | no | `present`, `absent` |

### `docker.compose_up`

| Variable | Required | Values |
|---|---|---|
| `compose_directory` | yes | free-form (validated) |
| `compose_project` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

### `docker.compose_down`

| Variable | Required | Values |
|---|---|---|
| `compose_directory` | yes | free-form (validated) |
| `compose_project` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

### `docker.compose_restart`

| Variable | Required | Values |
|---|---|---|
| `compose_directory` | yes | free-form (validated) |
| `compose_project` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

### `docker.compose_update`

| Variable | Required | Values |
|---|---|---|
| `compose_directory` | yes | free-form (validated) |
| `compose_project` | yes | free-form (validated) |
| `deployment_backup_verified` | no | free-form (validated) |

## Behaviour and safety

- Container operations validate the name against
  `^[a-zA-Z0-9][a-zA-Z0-9_.-]*$`; a name is never guessed.
- Compose operations require an absolute `compose_directory` and a project name
  matching `^[a-z0-9][a-z0-9_-]*$`. On `prod`, `deployment_backup_verified=true`
  is required before `compose_down`, `compose_update` and similar mutations.
- `Docker - Delete Container` removes a container and is destructive.
- `Docker - Container Logs` requires `allow_sensitive_logs=true`; review the
  data-handling policy before enabling it.
- The shipped Semaphore Compose file does not mount the Docker socket.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
