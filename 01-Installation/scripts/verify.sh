#!/usr/bin/env bash
# Phase 1 verification (Ubuntu, native). Captures evidence. No integrations.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-verify-output.txt}"
exec > >(tee "$OUT") 2>&1
echo "# Phase 1 Ansible verify $(date -Is)"
echo "## ansible --version"; ansible --version
echo "## ansible-playbook --version"; ansible-playbook --version
echo "## ansible-galaxy --version"; ansible-galaxy --version
echo "## python3 --version"; python3 --version
echo "## collections (basic)"; ansible-galaxy collection list 2>&1 | head -80 || true
echo "## localhost ping (required)"; ansible localhost -i localhost, -c local -m ping
echo "## localhost fact (sanity)"; ansible localhost -i localhost, -c local -m setup -a 'filter=ansible_distribution*' | head -40
echo "## DONE - update ../../INSTALLATION_REPORT.md with actual results. PASS only if all required checks succeed."