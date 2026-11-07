# InstallingAnsibleDeployment — Ansible on Ubuntu (Native, Phased)

A structured, phase-gated package for **installing and later integrating Ansible on an Ubuntu server**.  
**Key decision:** **Ansible is installed directly on Ubuntu (native), not inside Docker**, and it does not run as a background service. Ansible is used to manage the server itself and to provision/configure Docker, services, and containers.

> **Organization only — nothing deleted.** Original (previously empty) files are preserved in [`legacy/`](legacy/) (`README.original-empty.md`, `InstallingAnsibleCommand.original-empty.md`).

## Table of contents
- [Phases at a glance](#phases-at-a-glance)
- [Repository layout](#repository-layout)
- [Phase 1 — Installation & verification (native, Ubuntu only)](#phase-1--installation--verification-native-ubuntu-only)
  - [Prerequisites](#prerequisites)
  - [Step-by-step (target: `/opt/InstallingAnsibleDeployment`)](#step-by-step-target-optinstallingansibledeployment)
  - [Required verification](#required-verification)
  - [Phase 1 acceptance gate](#phase-1-acceptance-gate)
- [Phase 2 — Integration & playbooks (gated, after Phase 1 PASS)](#phase-2--integration--playbooks-gated-after-phase-1-pass)
- [Documentation & evidence](#documentation--evidence)
- [Safety & rules](#safety--rules)

## Phases at a glance
| Phase | Goal | What is allowed | Status |
|---|---|---|---|
| **1. Installation** | Install Ansible on Ubuntu and **verify it works** (baseline only) | System preflight, install missing prerequisites only, Ansible install (recommended `pipx`), verification, reporting | Ready for target execution; **actual Ubuntu tests required** |
| **2. Integration & Playbooks** | Build the Ansible project and integrate **Docker, Traefik, Odoo (17/19), Jenkins** with independent, tested playbooks/roles | Inventories, roles, collections, Vault, playbooks, integrations — **only after Phase 1 PASS** | **Scaffold/GATED — not executed** |

**Hard gate:** Do **not** start Phase 2 until Phase 1 passes and evidence is recorded in [`INSTALLATION_REPORT.md`](INSTALLATION_REPORT.md). Never claim an unexecuted test passed.

## Repository layout
| Path | Purpose |
|---|---|
| [`01-Installation/`](01-Installation/) | Phase 1 helper scripts (`preflight.sh`, `install-ubuntu.sh [apt\|pipx]`, `verify.sh`, `deploy-to-opt.sh`) |
| [`02-Integration/`](02-Integration/) | **Phase 2 scaffold (gated):** `ansible.cfg.example`, `inventories/{development,staging,production}/`, `playbooks/*.yml.example`, `roles/` (common, docker, traefik, odoo, postgresql, backup), `collections/`, `templates/`, `handlers/`, `files/`, `vault/`, `docs/`, integration folders (`jenkins/`, `docker/`, `traefik/`, `odoo/`, `playbooks/`) |
| [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md) | Detailed Phase 1 install/verify steps (apt + recommended `pipx`) |
| [`INSTALLATION_REPORT.md`](INSTALLATION_REPORT.md) | Phase 1 gate report — fill with **actual** commands/output (attach `verify-output.txt`) |
| [`VERSION_INFO.md`](VERSION_INFO.md) | Observed versions (before/after), install method, PATH/Python notes — update with real values |
| [`VERIFY_INSTALLATION.sh`](VERIFY_INSTALLATION.sh) | Root wrapper to run Phase 1 verification and capture evidence |
| [`InstallingAnsibleCommand.md`](InstallingAnsibleCommand.md) | Arabic command reference (full Phase 1 steps) |
| [`legacy/`](legacy/) | Preserved original files (no deletions) |

## Phase 1 — Installation & verification (native, Ubuntu only)

### Prerequisites
- Ubuntu Server (target host) with `sudo` access for installing missing OS packages.
- Python 3, SSH client, Git (installed if missing). No Jenkins/Docker/Traefik changes required in Phase 1.
- If Ansible is already installed, **do not remove/replace it without review**; record the current version.

### Step-by-step (target: `/opt/InstallingAnsibleDeployment`)
> Do not overwrite an existing target that contains data/config. Helper refuses to overwrite.

```bash
# 1) Place the project under /opt (no overwrite of an existing target)
sudo git clone <REPO_URL> /opt/InstallingAnsibleDeployment-src
sudo cp -a /opt/InstallingAnsibleDeployment-src/InstallingAnsibleDeployment /opt/InstallingAnsibleDeployment
# or: sudo bash /path/to/InstallingAnsibleDeployment/01-Installation/scripts/deploy-to-opt.sh /opt/InstallingAnsibleDeployment

# 2) Preflight — inspect OS/Python/existing Ansible/pipx/Git/SSH/PATH (NO deletions)
cd /opt/InstallingAnsibleDeployment/01-Installation
chmod +x scripts/*.sh
bash scripts/preflight.sh

# 3) Install missing prerequisites (review before running apt upgrade; upgrade is optional)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv pipx git openssh-client sshpass ca-certificates curl

# 4) Install Ansible (recommended: pipx, isolated user environment)
#    IMPORTANT: do NOT use `sudo` with `pipx install`.
pipx ensurepath
# reload PATH (SSH): reopen the session, or:
source ~/.bashrc
pipx install --include-deps ansible
# (alternative if you choose apt): sudo apt install -y ansible

# 5) Verify and capture evidence
cd /opt/InstallingAnsibleDeployment
./VERIFY_INSTALLATION.sh          # writes verify-output.txt
# or: bash 01-Installation/scripts/verify.sh

# 6) Record actual results and versions
#    - Update INSTALLATION_REPORT.md (PASS/FAIL per check + evidence)
#    - Update VERSION_INFO.md (real observed values)
```

### Required verification
Run and record actual output:
```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
python3 --version
ansible localhost -i localhost, -c local -m ping
```
**Expected ping result:**
```text
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```
Also confirm Ansible runs from a **new SSH session** (PATH correct) and that there are no critical Python/PATH errors.

### Phase 1 acceptance gate
All items must pass with **actual evidence** in [`INSTALLATION_REPORT.md`](INSTALLATION_REPORT.md):
- [ ] `ansible`, `ansible-playbook`, `ansible-galaxy` report versions successfully.
- [ ] `python3` is available and compatible.
- [ ] Local ping returns `pong` / `SUCCESS`.
- [ ] No critical runtime/PATH/Python errors; works in a new SSH session.
- [ ] `INSTALLATION_REPORT.md` and `VERSION_INFO.md` updated with real results.

**If any check fails:** fix, re-test, and **stop** — do not start Phase 2.  
**Only after PASS (and an explicit request):** proceed to Phase 2.

## Phase 2 — Integration & playbooks (gated, after Phase 1 PASS)
> **Not executed.** Implemented as a reviewed scaffold under [`02-Integration/`](02-Integration/). Start only after Phase 1 PASS.

**Scope (when executed):** validate the Ansible environment (versions/collections/SSH/permissions/target connectivity) and the state of Docker, Traefik, Jenkins, and Odoo **before** changes. Then implement independent, idempotent, tested components:

- **Project structure:** `ansible.cfg`, inventories (`development`/`staging`/`production`), `group_vars`/`host_vars`, roles, `collections/requirements` (review/pin), templates, handlers, files, **Ansible Vault**.
- **Docker:** engine/compose, networks, containers, volumes, images, compose deploy, health checks/logs.
- **Traefik:** inspect and **back up current config before changes**; provider/networks/routing/TLS/Let’s Encrypt (Cloudflare DNS challenge if needed). No unreviewed shared changes.
- **Odoo (17 & 19, strictly separated):** per-version configs/DBs/volumes/env; deploy, PostgreSQL, backups/restore, health/connectivity checks. **No production DB/module upgrades without explicit approval + a verified restorable backup.**
- **Jenkins (runs playbooks):** SSH/credentials (Jenkins Credentials), variables/inventory/env selection, result logging, stop on failure; **least privilege** (no unnecessary root/Docker socket access).

**Independent playbooks (no monolith):** `system_preparation`, `docker_installation`, `docker_configuration`, `traefik_configuration`, `odoo17_deployment`, `odoo19_deployment`, `postgresql_management`, `backup`, `restore`, `health_check`, `maintenance`.  
**Testing:** syntax/inventory validation, SSH/`ansible` ping, playbook runs, **idempotency**, Docker/Odoo/Postgres health, backup/restore — **staging first**; record actual results in implementation/test reports.

## Documentation & evidence
- Phase 1: [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md), [`INSTALLATION_REPORT.md`](INSTALLATION_REPORT.md), [`VERSION_INFO.md`](VERSION_INFO.md), [`VERIFY_INSTALLATION.sh`](VERIFY_INSTALLATION.sh), [`InstallingAnsibleCommand.md`](InstallingAnsibleCommand.md).
- Phase 2 (when executed, `02-Integration/docs/`): integration/playbooks/inventory/security/Odoo deployment/Jenkins integration/troubleshooting/implementation reports (Arabic explanations allowed; keep Ansible commands/modules in English).

## Safety & rules
- **All work stays under `InstallingAnsibleDeployment/`.** Installation and integration are separate.
- **Native install:** Ansible runs on Ubuntu, **not in Docker**. No Ansible-in-Docker/service setup in Phase 1.
- **No deletions:** do not delete files, folders, data, volumes, keys, or existing configs without review. Keep `legacy/` preserved.
- **Minimal changes:** install missing prerequisites only; preserve current versions/configs; review optional `apt upgrade`.
- **Secrets:** never commit secrets. Use Ansible Vault / Jenkins Credentials; do not use `sudo` with `pipx install`. Protect inventories/logs.
- **Production safety:** no production or dangerous changes automatically; no production DB/Odoo module upgrades without explicit approval + restorable backup. Back up configs (e.g., Traefik) before modification.
- **Truthful testing:** record real commands/output; never claim unexecuted tests passed.