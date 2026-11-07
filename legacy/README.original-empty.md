# InstallingAnsibleDeployment — Ansible on Ubuntu (Phased, Native Install, Legacy Preserved)

This directory is the **organized, phase-based** package for **installing and later integrating Ansible** on Ubuntu.  
**Important decision:** **Ansible is installed directly on the Ubuntu server (native), NOT inside Docker.** Ansible manages the server itself and is used to configure Docker, services, and containers.

**Organization only — nothing old deleted.** The original (previously empty) files are preserved in `legacy/`:
- `legacy/README.original-empty.md`
- `legacy/InstallingAnsibleCommand.original-empty.md`

## Two (then three) phases — strict separation
| Phase | Goal | Status |
|---|---|---|
| **1. Installation** | Install Ansible on Ubuntu and **verify it works only** (no integrations/playbooks) | Ready for target execution; **actual Ubuntu tests required** |
| **2. Integration & Playbooks** | After Phase 1 PASS: Jenkins/Docker/Traefik/Odoo integration and playbook authoring — independent, tested, documented | **NOT executed** (blocked until Phase 1 PASS) |

## Target host path
Recommended on Ubuntu: **`/opt/InstallingAnsibleDeployment`**.

## Phase 1 — Quick start (Ubuntu, native; NOT Docker)
> Do not overwrite an existing target that contains data/config. Record **actual** results in `INSTALLATION_REPORT.md`.

```bash
# 1) Place under /opt (no overwrite of existing target)
sudo git clone <REPO_URL> /opt/InstallingAnsibleDeployment-src
sudo cp -a /opt/InstallingAnsibleDeployment-src/InstallingAnsibleDeployment /opt/InstallingAnsibleDeployment
# or: sudo bash /path/to/InstallingAnsibleDeployment/01-Installation/scripts/deploy-to-opt.sh /opt/InstallingAnsibleDeployment

# 2) Preflight (review OS/Python/existing Ansible/SSH/sudo — NO deletions)
cd /opt/InstallingAnsibleDeployment/01-Installation
chmod +x scripts/*.sh
bash scripts/preflight.sh

# 3) Install (recommended: pipx isolated env, per Ansible guidance; alternative: apt)
bash scripts/install-ubuntu.sh pipx
# if using pipx: source ~/.bashrc  OR reopen the SSH session, then continue

# 4) Verify (required) — writes 01-Installation/verify-output.txt
bash scripts/verify.sh

# 5) Gate: update /opt/InstallingAnsibleDeployment/INSTALLATION_REPORT.md with actual evidence.
#    PASS required before any Phase 2 work.
```

## Phase 1 acceptance (all required, with evidence)
- [ ] `ansible --version`, `ansible-playbook --version`, `ansible-galaxy --version` succeed.
- [ ] Python 3 available as expected.
- [ ] Local test succeeds: `ansible localhost -i localhost, -c local -m ping` → `pong` / `SUCCESS`.
- [ ] No critical install/runtime errors.
- [ ] `INSTALLATION_REPORT.md` updated with actual commands/output. **No Phase 2 until PASS.**

## Phase 2 — Integration (only after Phase 1 PASS)
`02-Integration/` (each independent, tested, documented with `TEST_REPORT.md`; no secrets in Git): `jenkins/`, `docker/`, `traefik/`, `odoo/`, `playbooks/`.  
Do **not** configure Jenkins/Docker/Traefik/Odoo integration or write production playbooks in Phase 1. No production changes without explicit approval + restorable backup.

## Folder map
| Path | Purpose | Status |
|---|---|---|
| `01-Installation/` | Native install scripts + docs (apt/pipx), verify, deploy-to-opt | Ready for target execution |
| `02-Integration/` | Future integration/playbooks (scaffold only) | NOT RUN (gated) |
| `legacy/` | Preserved original (empty) files | Preserved |
| `INSTALLATION_REPORT.md` | Phase 1 gate evidence | Not approved until PASS |
| `InstallingAnsibleCommand.md` | Arabic command guide (clear, full steps) | Reference |

## Rules
- All work under `InstallingAnsibleDeployment/`. Install and integration kept separate.
- **Ansible is native on Ubuntu, not Docker.** No Ansible-in-Docker/service setup in Phase 1.
- Never delete data/files/config/keys or old scripts. No secrets in Git.
- Never claim an unexecuted test passed; record real commands/output.