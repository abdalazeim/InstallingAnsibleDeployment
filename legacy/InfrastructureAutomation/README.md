# InfrastructureAutomation — Ansible Project for Server Infrastructure
# Native Ansible on Ubuntu. Phase 2 (Integration) — gated after Phase 1 PASS.

## Scope
1. Ubuntu Server Management — updates, users, SSH, firewall, monitoring
2. Docker Infrastructure — engine, compose, containers, networks
3. Odoo Management — Odoo 17/19, backups, addons, deployment
4. PostgreSQL Administration — databases, users, backups, integrity
5. Traefik & Networking — reverse proxy, SSL, routing
6. Django Applications — deployment, Gunicorn, env, media
7. Jenkins Integration — playbook execution, scheduling, reports

## Structure
- `ansible.cfg` — main config
- `inventories/{development,staging,production}/` — per-env inventory + group_vars + host_vars
- `group_vars/`, `host_vars/` — global vars
- `playbooks/` — independent playbooks
- `roles/{common,system,docker,odoo,postgresql,traefik,django,backup}/` — reusable roles
- `templates/`, `files/`, `handlers/` — shared resources
- `docs/` — reports
- `scripts/` — helper scripts
- `vault/` — vault secrets (never commit real secrets)

## Quick Start
```bash
cd /opt/InfrastructureAutomation
# Edit inventories/development/hosts.ini with real hosts
ansible-playbook -i inventories/development/hosts.ini playbooks/system_preparation.yml
```

## Security
- SSH keys only; no password auth
- Ansible Vault for secrets
- Least privilege sudo
- No secrets in Git
- Backup configs before changes