#!/usr/bin/env bash
set -euo pipefail
project="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "${CONFIRM_UNINSTALL:-false}" == true ]] || {
  echo 'Set CONFIRM_UNINSTALL=true to remove only managed command links. Data and dependencies are preserved.' >&2; exit 1;
}
for command_name in infrastructure-manager infrastructure-semaphore; do
  link="/usr/local/bin/$command_name"
  if [[ -L "$link" && "$(readlink -f "$link")" == "$project/.venv/bin/$command_name" ]]; then
    rm -- "$link"
  fi
done
echo 'Managed command links removed. Repository, reports, environments, credentials, services and backups are preserved.'
