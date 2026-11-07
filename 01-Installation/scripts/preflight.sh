# /opt placement and preflight (Ubuntu). Run on the TARGET Ubuntu server.
# Ansible is installed directly on Ubuntu (NOT in Docker).
# This script does NOT delete data. Review output before changes.

set -euo pipefail
echo "=== Date/Host ==="; date -Is; hostnamectl 2>/dev/null || hostname || true
echo; echo "=== OS ==="; lsb_release -a 2>/dev/null || cat /etc/os-release 2>/dev/null || true
echo; echo "=== Python ==="; python3 --version 2>/dev/null || true; which python3 2>/dev/null || true
echo; echo "=== Existing Ansible ==="; ansible --version 2>/dev/null || echo "(ansible not found)"; which ansible 2>/dev/null || true
echo; echo "=== pip/pipx (info only) ==="; python3 -m pip --version 2>/dev/null || true; pipx --version 2>/dev/null || echo "(pipx not found)"
echo; echo "=== SSH/OpenSSH client ==="; ssh -V 2>&1 | head -1 || true
echo; echo "=== Sudo ==="; sudo -n true 2>/dev/null && echo "sudo: non-interactive OK (or cached)" || echo "sudo: may prompt (expected for install)"
echo; echo "Review output. Do NOT remove existing Ansible/config/inventory/keys unless explicitly intended."