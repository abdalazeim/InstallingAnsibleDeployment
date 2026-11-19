# Traefik and network diagnostics

Role: `roles/networking/` · operations: **10** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/networking/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `networking.port_check` | Networking - Port Check | `read` | `playbooks/networking/port_check.yml` |
| `networking.connectivity` | Networking - Connectivity Check | `read` | `playbooks/networking/connectivity.yml` |
| `networking.dns_check` | Networking - DNS Check | `read` | `playbooks/networking/dns_check.yml` |
| `networking.ssl_check` | Traefik - SSL Certificate Check | `read` | `playbooks/networking/ssl_check.yml` |
| `networking.traefik_status` | Traefik - Status | `read` | `playbooks/networking/traefik_status.yml` |
| `networking.traefik_health` | Traefik - Health Check | `read` | `playbooks/networking/traefik_health.yml` |
| `networking.routers` | Traefik - Router Inspection | `read` | `playbooks/networking/routers.yml` |
| `networking.docker_networks` | Docker - Network Inspection | `read` | `playbooks/networking/docker_networks.yml` |
| `networking.traefik_validate` | Traefik - Configuration Validation | `read` | `playbooks/networking/traefik_validate.yml` |
| `networking.traefik_deploy` | Traefik - Deploy | `change` | `playbooks/networking/traefik_deploy.yml` |

## Inputs

### `networking.port_check`

| Variable | Required | Values |
|---|---|---|
| `network_host` | yes | free-form (validated) |
| `network_port` | yes | free-form (validated) |

### `networking.connectivity`

| Variable | Required | Values |
|---|---|---|
| `network_host` | yes | free-form (validated) |
| `network_port` | yes | free-form (validated) |

### `networking.dns_check`

| Variable | Required | Values |
|---|---|---|
| `dns_name` | yes | free-form (validated) |

### `networking.ssl_check`

| Variable | Required | Values |
|---|---|---|
| `tls_hostname` | yes | free-form (validated) |

### `networking.traefik_status`

| Variable | Required | Values |
|---|---|---|
| `traefik_api_url` | yes | free-form (validated) |

### `networking.traefik_health`

| Variable | Required | Values |
|---|---|---|
| `traefik_api_url` | yes | free-form (validated) |

### `networking.routers`

| Variable | Required | Values |
|---|---|---|
| `traefik_api_url` | yes | free-form (validated) |

### `networking.docker_networks`

| Variable | Required | Values |
|---|---|---|
| `network_name` | yes | free-form (validated) |

### `networking.traefik_validate`

| Variable | Required | Values |
|---|---|---|
| `traefik_directory` | yes | free-form (validated) |

### `networking.traefik_deploy`

| Variable | Required | Values |
|---|---|---|
| `traefik_directory` | yes | free-form (validated) |
| `traefik_version` | yes | free-form (validated) |
| `traefik_acme_email` | yes | free-form (validated) |

## Behaviour and safety

- Checks are read-only: TCP port, DNS resolution, SSL chain/expiry, Traefik API
  status, routers and configuration validation.
- `Traefik - Configuration Validation` reads the compose directory; it does not
  restart anything.
- `Traefik - Deploy` requires a version, an absolute directory and an ACME
  e-mail; it does not overwrite certificates.
- Traefik API URLs must be reachable from the target; do not expose the
  dashboard publicly.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
