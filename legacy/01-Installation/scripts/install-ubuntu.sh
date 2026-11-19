#!/usr/bin/env bash
# Phase 1 install (Ubuntu, native — NOT Docker).
# Modes:
#   apt  - install from Ubuntu repositories (simple)
#   pipx - recommended: isolated user install via pipx (official-style approach)
set -euo pipefail
MODE="${1:-pipx}"   # default to recommended method
echo "Mode: $MODE"

if [ "$MODE" = "apt" ]; then
  sudo apt-get update
  sudo apt-get install -y software-properties-common ca-certificates curl git gnupg \
    python3 python3-pip python3-venv python3-yaml python3-apt openssh-client
  sudo apt-get install -y ansible
  echo "Done (apt). Run: ansible --version && ansible localhost -i localhost, -c local -m ping"
elif [ "$MODE" = "pipx" ]; then
  sudo apt-get update
  sudo apt-get install -y python3 python3-pip python3-venv pipx git openssh-client sshpass
  # pipx is per-user; ensurepath for current user
  pipx ensurepath || true
  pipx install --include-deps ansible || pipx upgrade --include-deps ansible
  echo "Done (pipx). You may need: source ~/.bashrc  (or reopen SSH session)"
  echo "Then run: ansible --version && ansible localhost -i localhost, -c local -m ping"
else
  echo "Unsupported mode: $MODE (use: apt | pipx)"
  exit 2
fi