# Phase 2 — Ansible project integration (GATED: do NOT execute before Phase 1 PASS)

> **Status:** NOT executed. This folder is a **scaffold** for integration/playbooks to be implemented **only after** `../INSTALLATION_REPORT.md` records a real Phase 1 **PASS** (Ansible installed and verified on Ubuntu).  
> **Important:** Ansible remains installed **natively on Ubuntu (not Docker)**. Do not re-install Ansible if it is already installed and working.

## Entry gate (mandatory)
- [ ] Phase 1 PASS with actual evidence in `../INSTALLATION_REPORT.md` and `../VERSION_INFO.md`.
- [ ] No unverified claims. Stop on any critical failure.

## Scope (after gate)
Check the Ansible environment (version/Python, collections, SSH, user permissions, target connectivity, Docker/Traefik/Jenkins/Odoo state as relevant) **before** making changes. Then implement independently tested components:
- Ansible project config: `ansible.cfg`, inventories (dev/staging/production), `group_vars`/`host_vars`, roles, collections requirements, templates, handlers, files, Vault.
- Integrations (separate, idempotent): **Docker** (engine/compose/networks/containers/volumes/images/deploy/health/logs), **Traefik** (inspect & back up current config before changes; routing/TLS/Let’s Encrypt/Cloudflare DNS challenge as needed), **Odoo** (17/19 **strictly separated** configs/DBs/volumes/env; deploy, Postgres, backups/restore, health checks; **no production DB/module upgrades without explicit approval + restorable backup**), **Jenkins** (run playbooks with SSH/credentials, variables/inventory/env selection, logging/error handling/stop-on-fail; least privilege — no unnecessary root/Docker socket).

## Independent playbooks (create/test separately; no single monolith)
`system_preparation.yml`, `docker_installation.yml`, `docker_configuration.yml`, `traefik_configuration.yml`, `odoo17_deployment.yml`, `odoo19_deployment.yml`, `postgresql_management.yml`, `backup.yml`, `restore.yml`, `health_check.yml`, `maintenance.yml`.

## Testing (record in `docs/IMPLEMENTATION_REPORT.md` / per-component reports)
Syntax & inventory validation, SSH/`ansible` ping, playbook runs, **idempotency**, Docker/Odoo/Postgres health, backup/restore procedures. Test in staging first; no production moves before verified results.

## Security
SSH keys, Ansible Vault, least privilege/sudo, no secrets in Git, protect inventory/logs, back up configs before modification.

## Structure (scaffold)
`inventories/{development,staging,production}/`, `playbooks/`, `roles/`, `collections/`, `templates/`, `handlers/`, `files/`, `vault/`, `docs/`, `scripts/`. Keep reusable and extensible.