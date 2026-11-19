# Installation

## 1. Supported targets

- Ubuntu Server 22.04 LTS or 24.04 LTS
- amd64 or arm64
- A non-root operator account with `sudo`
- Outbound HTTPS for apt, PyPI and Ansible Galaxy
- SSH reachability and trusted host keys for remote targets

The installer refuses other releases and architectures in
`installation/preflight.sh`.

## 2. What the installer does

```bash
sudo INSTALL_USER="$USER" bash installation/install.sh
```

`INSTALL_USER` (or `SUDO_USER`) must be an existing non-root account.

Steps:

1. Run `installation/preflight.sh` (read-only).
2. Confirm root and a non-root operator.
3. Install OS prerequisites: `python3`, venv, pip, `pipx`, `git`, OpenSSH
   client, CA certificates.
4. Copy the checkout to `INSTALL_DIR` (default
   `/opt/InstallingAnsibleDeployment`) when the target does not exist. An
   existing target is preserved.
5. Install pinned `uv` with pipx, then a managed Python 3.12 runtime.
6. Create `<target>/.venv` and install `ansible-core==2.21.6`,
   `ansible-lint==26.11.0`, pytest, PyYAML, Jinja2 and the project package.
7. Install collections from `requirements.yml` (pinned ranges).
8. Write `/etc/infrastructure-manager/project-path`.
9. Link `infrastructure-manager` and `infrastructure-semaphore` in
   `/usr/local/bin` without overwriting unrelated commands.
10. Add the venv to `PATH` through `/etc/profile.d/infrastructure-manager.sh`.
11. Create the report directory with mode `0700` owned by the operator.
12. Run `installation/verify.sh`.

The installer deliberately does **not** install or configure Docker,
PostgreSQL, Odoo, Jenkins, Traefik or Redis. Those are optional catalog
operations performed against selected targets.

## 3. Verification

```bash
bash installation/verify.sh
```

It runs:

- `ansible --version` and `ansible-playbook --version`
- `ansible-galaxy collection list`
- `ansible-lint`
- `python -m pytest -q`
- `python scripts/validation/validate.py --syntax`
- a local ping
- `ansible-playbook -i inventories/build/hosts.yml playbooks/system/verify.yml`

The log is written to `reports/installation-<UTC timestamp>.log` with mode
`0600`.

A successful verification proves the toolchain and the local build inventory.
It does **not** prove Docker, Odoo, PostgreSQL, Traefik, Jenkins, Django,
backup/restore or Semaphore integration. Those require a real target and are
listed in `FINAL_IMPLEMENTATION_REPORT.md`.

## 4. Manual install (no installer)

On Ubuntu 22.04/24.04:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git openssh-client ca-certificates
python3 -m venv .venv
. .venv/bin/activate
pip install 'ansible-core==2.21.6' 'ansible-lint==26.11.0' 'pytest>=8,<10' 'PyYAML>=6,<7' 'Jinja2>=3.1,<4' -e .
ansible-galaxy collection install -r requirements.yml
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
python scripts/validation/validate.py
python -m pytest -q tests/unit
```

## 5. Where the CLI lives

- Managed venv: `/opt/InstallingAnsibleDeployment/.venv/bin/`
- Command links: `/usr/local/bin/infrastructure-manager`,
  `/usr/local/bin/infrastructure-semaphore`
- Project path record: `/etc/infrastructure-manager/project-path`

Open a new login shell or `source /etc/profile.d/infrastructure-manager.sh`.

## 6. Uninstall

```bash
CONFIRM_UNINSTALL=true sudo bash installation/uninstall.sh
```

This removes only the two managed command links. The repository, virtual
environment, reports, inventories, credentials, services and backups are
preserved. Remove those manually only after reviewing what they contain.

## 7. First-run checklist

1. `installation/verify.sh` exits 0.
2. `infrastructure-manager catalog --json` lists 98 operations.
3. `infrastructure-manager system info` works against the build inventory.
4. Add real SSH hosts to `inventories/<env>/hosts.yml`.
5. Put instance maps and secrets in `host_vars/<host>.yml` or Vault.
6. Run the read-only health checks against the target.
7. Deploy Semaphore with `semaphore/setup/` and follow
   `docs/semaphore/SEMAPHORE_SETUP.md`.
8. Run change operations on a disposable target before production.

## 8. Upgrade

```bash
git -C /opt/InstallingAnsibleDeployment pull --ff-only
sudo INSTALL_USER="$USER" bash /opt/InstallingAnsibleDeployment/installation/install.sh
```

The installer is idempotent: it reuses the existing virtual environment and
reinstalls pinned dependencies and collections. Review `CHANGELOG.md` first.
Re-run `--apply` for Semaphore after catalog changes.
