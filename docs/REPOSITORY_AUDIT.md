# Repository audit — 2026-11-18

Scope: local checkout, before the portable Ubuntu implementation. No remote service was tested.

## Preserve
- Phase 1 scripts and original reports: historical installation interface.
- `02-Integration/`: illustrative scaffold; not an operational deployment.
- `InfrastructureAutomation/`: preliminary native-service implementation, preserved for migration.
- `automation/ansible-project/`: small fact collector, byte-identical to its copy under `02-Integration`.
- Existing Semaphore Compose service and named data volume: never replace or remove data automatically.

## Findings
- 106 files, eight preliminary roles and twelve preliminary playbooks.
- Nine missing role templates and unimported global handlers.
- Shared Odoo configuration/data/port defaults across releases; common target group.
- Invalid UFW state, Django task keyword and user creation order.
- Incomplete backup/restore verification; negative retention age and hidden errors.
- No operational Jenkins pipelines, CLI, test suite or Semaphore resource provisioning.
- SSH host-key verification disabled in historical inventories.
- A tracked Semaphore credential note contains sensitive assignment names; sanitization and rotation of any previously exposed values are required. Never print its contents.
- Multiple Ansible configuration roots and duplicated sample trees.
- 40 YAML documents parse; one collection example has a non-UTF-8 encoding.
- Windows host has no Ansible, Docker or installed WSL. Ubuntu integration is deferred to a separate server per operator instruction.

## Remediation architecture
Use root `playbooks/`, reusable root `roles/`, four explicit inventories, a tested operation catalog, an allowlisted Python CLI, fail-closed mutation guards, JSON statistics and a version-aware Semaphore API provisioner. Preserve historical code with a clear unsupported status; do not present it as the new supported path.

See `PROJECT_STUDY_AR.md` for file-level analysis. The previous audit is retained in `REPOSITORY_AUDIT.previous.md`; its claims are historical and not current verification evidence.
