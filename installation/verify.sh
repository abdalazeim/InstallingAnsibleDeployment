#!/usr/bin/env bash
set -euo pipefail
umask 077
project="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$project"
export ANSIBLE_CONFIG="$project/ansible.cfg"
mkdir -p reports
report="reports/installation-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee "$report") 2>&1
ansible --version
ansible-playbook --version
ansible-galaxy collection list
python -m pytest -q
python scripts/validation/validate.py --syntax
ansible localhost -i localhost, -c local -m ansible.builtin.ping
ansible-playbook -i inventories/build/hosts.yml playbooks/system/verify.yml
printf 'Installation verification completed. This does not validate application deployments or Semaphore.\n'
