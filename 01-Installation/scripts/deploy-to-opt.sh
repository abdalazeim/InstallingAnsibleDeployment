#!/usr/bin/env bash
# Copy InstallingAnsibleDeployment to /opt (no overwrite of existing target).
# Usage: sudo bash 01-Installation/scripts/deploy-to-opt.sh [TARGET_DIR]
set -euo pipefail
TARGET="${1:-/opt/InstallingAnsibleDeployment}"
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
echo "Source: $SRC"
echo "Target: $TARGET"
if [ -e "$TARGET" ]; then
  echo "Target exists - NOT overwriting (preserve data/config). Sync manually if intended: rsync -a '$SRC/' '$TARGET/'"
  exit 1
fi
mkdir -p "$(dirname "$TARGET")"
cp -a "$SRC" "$TARGET"
echo "Copied. Phase 1 only (Ansible runs directly on Ubuntu, NOT in Docker):"
echo "  cd $TARGET/01-Installation && chmod +x scripts/*.sh"
echo "  bash scripts/preflight.sh"
echo "  bash scripts/install-ubuntu.sh pipx   # recommended (or: apt)"
echo "  # if pipx: source ~/.bashrc or reopen SSH session"
echo "  bash scripts/verify.sh                # writes verify-output.txt"
echo "  # update ../INSTALLATION_REPORT.md with actual evidence before Phase 2"