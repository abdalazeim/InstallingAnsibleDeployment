#!/usr/bin/env bash
# VERIFY_INSTALLATION.sh — Phase 1 Ansible verification (Ubuntu, native). No integrations.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x 01-Installation/scripts/verify.sh
bash 01-Installation/scripts/verify.sh "${1:-verify-output.txt}"
echo "Update INSTALLATION_REPORT.md and VERSION_INFO.md with actual evidence."