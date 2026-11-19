# Implementation status

Updated: 2026-11-18. Scope: local checkout on Ubuntu 24.04. No clean-server
deployment, live Semaphore provisioning, or backup/restore drill was performed.

The operator will test on a separate Ubuntu server. No existing development or
production server is a deployment target in this work. The authoritative detail
is in [`FINAL_IMPLEMENTATION_REPORT.md`](FINAL_IMPLEMENTATION_REPORT.md).

## Supported path

Root `playbooks/`, `roles/`, `inventories/`, `library/`, `plugins/`,
`infrastructure_manager/`, `semaphore/`, `jenkins/`, `scripts/`, `tests/` and
`installation/`. Historical trees were moved under `legacy/` and are excluded
from lint, tests and the supported path. Do not mix their configuration files
with root.

## Implemented and locally checked

| Area | Evidence |
|---|---|
| Operation catalog | `semaphore/templates/catalog.json`: 98 operations, 9 groups, 48 read / 39 change / 11 destructive |
| Playbooks | 98/98 catalog playbooks pass `--syntax-check` (`tests/syntax`, 100 tests) |
| Safety policy | `roles/common` validates Ubuntu release, environment, risk and confirmations; `playbooks/_guard.yml` refuses an empty target selection |
| Fail-closed proof | `inventories/staging` (empty) exits 2 with "No hosts match"; read-only build run is `ok=7 failed=0` |
| Structural validator | 212 YAML documents, 98 operations, 0 errors |
| Lint | `ansible-lint` exit 0; 71 non-fatal `var-naming[no-role-prefix]` warnings |
| Tests | 142 passed, 3 skipped (opt-in integration/idempotency); 27 unit, 15 security, 100 syntax |
| Report callback | read-only `playbooks/system/info.yml` writes aggregate stats JSON |
| Static modules | PostgreSQL, archive, addons and TLS modules with unit tests |
| Installation | `install.sh`, preflight, verify, uninstall; not executed here (no sudo) |
| Semaphore | Compose pinned to 2.19.12, API provisioner, 392 planned templates, generated catalog, setup/security docs |
| Jenkins | 5 pipelines and a shared-library step; delivered as code, not executed here |
| Documentation | architecture, installation, configuration, operations, security, troubleshooting, development, 9 module docs, final report |

## Not verified

- Clean Ubuntu 22.04/24.04 installation and an idempotent re-run.
- Live Semaphore project/template creation, UI visibility, key store, task
  history and schedules (`browser_ui_observed: false`).
- Docker, Odoo, PostgreSQL, Traefik, Jenkins and Django operations on real
  hosts.
- Backup/restore drill against real data.
- Jenkins pipeline execution and shared-library resolution in a real Jenkins.
- Integration and idempotency suites (need `INFRASTRUCTURE_INTEGRATION=1` on a
  disposable target).

## Known gaps

1. `community.general` is pinned to `>=10,<14`; the isolated installer path must
   be validated on the target (this shell has 13.5.0).
2. Containerized Semaphore treats `localhost` as the runner container; mutating
   operations require an SSH inventory.
3. The provisioner never deletes resources; renaming a template leaves a
   duplicate that needs manual review.
4. The historical `legacy/` tree contains unsafe settings and is not supported.

## Gates

1. ~~Repository audit and preservation map.~~
2. ~~Root Ansible configuration, inventories, defaults, policy and reports.~~
3. ~~Operations, tests, documentation and Semaphore provisioning code.~~
4. Local verification: ~~validator~~, ~~syntax~~, ~~lint~~, ~~unit/security tests~~.
5. Operator acceptance on a clean Ubuntu server: **pending**.
