#!/usr/bin/env bash
set -euo pipefail
umask 027
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
bash "$source_dir/installation/preflight.sh"
[[ "$(id -u)" == 0 ]] || { echo 'Run using sudo bash installation/install.sh' >&2; exit 1; }
operator="${INSTALL_USER:-${SUDO_USER:-}}"
[[ -n "$operator" && "$operator" != root ]] || {
  echo 'Set INSTALL_USER to an existing non-root operator when running from a root session.' >&2; exit 1;
}
id "$operator" >/dev/null
operator_home="$(getent passwd "$operator" | cut -d: -f6)"
operator_group="$(id -gn "$operator")"
target="${INSTALL_DIR:-/opt/InstallingAnsibleDeployment}"
[[ "$target" == /* && "$target" != / && "$target" != /opt ]] || { echo 'Unsafe installation directory' >&2; exit 1; }
apt-get update
apt-get install -y python3 python3-venv python3-pip pipx git openssh-client ca-certificates
if [[ ! -e "$target" ]]; then
  mkdir -p -- "$(dirname -- "$target")"
  cp -a -- "$source_dir" "$target"
  chown -R "$operator:$operator_group" -- "$target"
elif [[ "$(realpath -- "$target")" != "$source_dir" ]]; then
  echo "Existing target preserved. Run its installation/install.sh after reviewing/updating that checkout: $target" >&2
  exit 1
fi
run_operator() { runuser -u "$operator" -- env HOME="$operator_home" PATH="$operator_home/.local/bin:/usr/local/bin:/usr/bin:/bin" "$@"; }
if [[ ! -x "$operator_home/.local/bin/uv" ]]; then
  run_operator pipx install 'uv==0.13.9'
fi
# Managed Python is isolated; Ubuntu's system Python is never replaced.
run_operator "$operator_home/.local/bin/uv" python install 3.12
runtime="$target/.venv"
if [[ ! -x "$runtime/bin/python" ]]; then
  run_operator "$operator_home/.local/bin/uv" venv --python 3.12 "$runtime"
fi
run_operator "$operator_home/.local/bin/uv" pip install --python "$runtime/bin/python" \
  'ansible-core==2.21.6' 'ansible-lint==26.11.0' 'pytest>=8,<10' 'PyYAML>=6,<7' 'Jinja2>=3.1,<4' "$target"
run_operator "$runtime/bin/ansible-galaxy" collection install -r "$target/collections/requirements.yml"
install -d -m 0755 /etc/infrastructure-manager
printf '%s\n' "$target" > /etc/infrastructure-manager/project-path
chmod 0644 /etc/infrastructure-manager/project-path
for command_name in infrastructure-manager infrastructure-semaphore; do
  link="/usr/local/bin/$command_name"
  if [[ -e "$link" && "$(readlink -f "$link")" != "$runtime/bin/$command_name" ]]; then
    echo "Existing command preserved: $link. Use $runtime/bin/$command_name" >&2
  else
    ln -sfn -- "$runtime/bin/$command_name" "$link"
  fi
done
printf 'export PATH=%q:$PATH\n' "$runtime/bin" > /etc/profile.d/infrastructure-manager.sh
chmod 0644 /etc/profile.d/infrastructure-manager.sh
install -d -o "$operator" -g "$operator_group" -m 0700 "$target/reports"
run_operator env PATH="$runtime/bin:/usr/bin:/bin" INFRASTRUCTURE_PROJECT="$target" bash "$target/installation/verify.sh"
printf '\nInstalled. Open a new login shell or source /etc/profile.d/infrastructure-manager.sh\n'
printf 'Semaphore is configured separately; see docs/semaphore/SEMAPHORE_SETUP.md.\n'
