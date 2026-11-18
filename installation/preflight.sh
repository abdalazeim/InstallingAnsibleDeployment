#!/usr/bin/env bash
set -euo pipefail
[[ -r /etc/os-release ]] || { echo 'Linux /etc/os-release is required' >&2; exit 1; }
# shellcheck disable=SC1091
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" =~ ^(22\.04|24\.04)$ ]] || {
  echo 'Supported installation targets: Ubuntu Server 22.04 and 24.04' >&2; exit 1;
}
case "$(uname -m)" in x86_64|aarch64) ;; *) echo 'Supported architectures: amd64 and arm64' >&2; exit 1;; esac
printf 'Ubuntu=%s architecture=%s\n' "$VERSION_ID" "$(uname -m)"
command -v python3 >/dev/null && python3 --version || true
command -v ansible >/dev/null && ansible --version || true
printf 'Preflight is read-only. Installation does not deploy Docker or application services.\n'
