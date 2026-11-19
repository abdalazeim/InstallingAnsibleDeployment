# Jenkins server operations

Role: `roles/jenkins/` · operations: **7** · catalog: `semaphore/templates/catalog.json`

Each operation is one playbook under `playbooks/jenkins/` and one Semaphore template per environment, named `<operation name> [<env>]`. Inputs below are the exact Ansible variable names used by the playbook and its survey.

## Operations

| Operation ID | Template name | Risk | Playbook |
|---|---|---|---|
| `jenkins.status` | Jenkins - Status | `read` | `playbooks/jenkins/status.yml` |
| `jenkins.health_check` | Jenkins - Health Check | `read` | `playbooks/jenkins/health_check.yml` |
| `jenkins.list_jobs` | Jenkins - List Jobs | `read` | `playbooks/jenkins/list_jobs.yml` |
| `jenkins.integration_test` | Jenkins - Integration Test | `read` | `playbooks/jenkins/integration_test.yml` |
| `jenkins.build_status` | Jenkins - Build Status | `read` | `playbooks/jenkins/build_status.yml` |
| `jenkins.trigger_job` | Jenkins - Trigger Job | `change` | `playbooks/jenkins/trigger_job.yml` |
| `jenkins.deploy` | Jenkins - Deployment | `change` | `playbooks/jenkins/deploy.yml` |

## Inputs

### `jenkins.status`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |

### `jenkins.health_check`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |

### `jenkins.list_jobs`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |

### `jenkins.integration_test`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |

### `jenkins.build_status`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |
| `jenkins_job_path` | yes | free-form (validated) |
| `jenkins_build_number` | yes | free-form (validated) |

### `jenkins.trigger_job`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |
| `jenkins_job_path` | yes | free-form (validated) |

### `jenkins.deploy`

| Variable | Required | Values |
|---|---|---|
| `jenkins_url` | yes | free-form (validated) |
| `jenkins_job_path` | yes | free-form (validated) |

## Behaviour and safety

- Operations talk to a Jenkins URL supplied per task. `jenkins_user` and
  `jenkins_api_token` come from the Key Store, Vault or task variables; no
  credential is stored in the repository.
- Read operations cover status, health, job list, integration test result and
  build status.
- `Jenkins - Trigger Job` validates `jenkins_job_path`, queues the build and
  reports that it is asynchronous. `Jenkins - Deployment` is also a change
  operation and requires confirmation. Neither runs Ansible; Jenkins pipelines
  call Semaphore instead.
- Do not schedule the same operation in both Jenkins and Semaphore.

## Common inputs

All operations also accept the inventory-selected target and the policy variables defined in `roles/common/defaults/main.yml`: `infrastructure_environment`, `confirm_operation`, `confirm_production`, `confirm_destructive_operation`, `confirm_reboot`, `backup_root`, `retention_days`. See `docs/configuration/CONFIGURATION.md`.

## Verification

- `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` (part of `tests/syntax`).
- Static safety checks in `tests/security`.
- A real run requires a disposable Ubuntu target; see `docs/FINAL_IMPLEMENTATION_REPORT.md` for what was actually executed.
