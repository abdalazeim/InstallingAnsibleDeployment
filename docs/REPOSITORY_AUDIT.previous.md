# Repository Audit

## Top-level
- 01-Installation: Phase 1 scripts (preflight/install/verify/deploy-to-opt)
- 02-Integration: scaffold (gated, *.example)
- InfrastructureAutomation: roles/playbooks/inventories/group_vars + skeleton dirs
- automation/ansible-project: copied working project (server_info.ymly)
- control-plane/semaphore: compose + .env (secrets)
- legacy: preserved empty originals

## Observed
- Ansible core 2.21.5 installed; localhost ping SUCCESS.
- Services: ITPurchasing :8001 (200), Odoo19 :10019 (200), Semaphore :3000 (200).
- Containers running; postgres_db restarting (Exit 1) -> investigate.
- Integration playbooks are examples only (not executed).
- No tests/lint config present; no CLI; no audit report previously.
