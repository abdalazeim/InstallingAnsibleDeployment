# Troubleshooting

Always start with the operation's Semaphore task history or CLI output, then the
report in `reports/`, then the target's service logs. Do not disable a safety
check to make a task pass.

## Installation and tooling

| Symptom | Check |
|---|---|
| `Supported installation targets: Ubuntu Server 22.04 and 24.04` | run `installation/preflight.sh`; the host is another release or architecture |
| `Run using sudo bash installation/install.sh` | use sudo and set `INSTALL_USER` |
| `Set INSTALL_USER to an existing non-root operator` | export `INSTALL_USER=<account>` when running from a root session |
| `Existing target preserved` | the install path exists; update that checkout and run its installer |
| `uv` not found | ensure `~/.local/bin` is on PATH or reinstall pipx |
| `pytest: command not found` | use the managed `.venv` (`/opt/InstallingAnsibleDeployment/.venv/bin/python -m pytest`) |
| `ansible-lint` fails in a new shell | source `/etc/profile.d/infrastructure-manager.sh` |
| collection version warning | run `ansible-galaxy collection install -r requirements.yml --force-with-deps` |

## Inventory and targets

| Symptom | Check |
|---|---|
| `No hosts match 'all'` | configure `inventories/<env>/hosts.yml`; this is the guard failing closed |
| `provided hosts list is empty` | the inventory file is empty; add hosts before running |
| `Supported target is Ubuntu 22.04/24.04` | the target is the Semaphore container or a non-Ubuntu host |
| `Mutation of a local runner container is refused` | use an SSH inventory, not localhost inside a container |
| `Permission denied (publickey)` | key-store entry, `ansible_user`, and the target's `authorized_keys` |
| `Host key verification failed` | add the target key to `known_hosts`; do not disable checking |
| `UNREACHABLE` | network, port, firewall, or the host is down |

## Confirmations

| Symptom | Check |
|---|---|
| `Operation blocked: provide explicit confirmation` | pass `confirm_operation=true`; destructive also needs `confirm_destructive_operation=true` |
| production change still blocked | pass `confirm_production=true` for that task |
| confirmation is ignored | confirmations cannot be stored in a Semaphore environment; use the survey field |
| reboot did not happen | `confirm_reboot=true` is required and `/var/run/reboot-required` must exist |

## Docker

| Symptom | Check |
|---|---|
| `docker: command not found` | run `Docker - Install` first |
| `permission denied ... docker.sock` | run with `become: true` or add the operator to the `docker` group |
| `container_name is required` | provide the survey/CLI input; names are not guessed |
| Compose operation fails | verify `compose_directory` and `compose_project`; the directory must contain a Compose file |
| update refused | `deployment_backup_verified=true` is required |
| no logs | `allow_sensitive_logs=true` is required for `container_logs`; review the data first |

## Odoo

| Symptom | Check |
|---|---|
| `odoo_instance is required` | select the instance key (for example `odoo17`, `odoo19`) |
| `odoo_instance in odoo_instances` fails | define the instance in `host_vars/<host>.yml` |
| database connection fails | `postgres_instance` must exist and the database must be reachable |
| HTTP health fails | `health_url`, reverse proxy and the container port |
| WebSocket fails | `websocket_host`/`websocket_port` and proxy headers |
| full backup refused | `confirm_downtime=true` is required |
| restore refused | `restore_database`, `restore_destination` and a verified bundle are required |

## PostgreSQL

| Symptom | Check |
|---|---|
| `postgres_instance is required` | define `postgres_instances` in host vars |
| authentication failed | Vault password and `pg_hba.conf`; the module does not pass passwords in argv |
| `database_name` invalid | identifiers must match `^[A-Za-z_][A-Za-z0-9_-]{0,62}$` |
| backup not found | use the exact `backup_id` from the backup output |
| restore refused | destination must be new; destructive confirmation is required |
| verify fails | checksum, size, metadata or archive integrity; re-run the backup |

## Django

| Symptom | Check |
|---|---|
| `django_application is required` | select the application key |
| `mode` mismatch | `collectstatic` requires `native`; deploy supports native/compose as documented |
| migrations refused | `deployment_backup_verified=true` is required |
| static collection fails | virtualenv path, `manage.py`, permissions for `app.user` |
| gunicorn restart fails | `service` name and systemd status |
| health check fails | `health_url` and the reverse proxy |
| `.env` leaked | rotate the values, remove the file from history, fix permissions |

## Traefik and networking

| Symptom | Check |
|---|---|
| `traefik_api_url is required` | provide the dashboard/API URL |
| API 404 | the API/dashboard is disabled or on another entrypoint |
| certificate check fails | trust chain, SNI, expiry threshold |
| DNS check fails | resolver, record name, propagation |
| port check fails | firewall, listener and source routing |
| router missing | labels/provider configuration and the container network |
| validate fails | static YAML/TOML syntax and file permissions |

## Jenkins

| Symptom | Check |
|---|---|
| `expected one template named ...` | run the Semaphore provisioner and check the environment/name |
| `use HTTPS or a loopback HTTP Semaphore URL` | the URL is plaintext and remote |
| 401/403 | Jenkins credential `semaphore-api-token` is missing or expired |
| task stays `running` | poll timeout; inspect Semaphore task history |
| pipeline runs Ansible locally | it must call `infrastructureSemaphore`, not `ansible-playbook` |

## Semaphore

| Symptom | Check |
|---|---|
| `Provisioner contract is pinned to Semaphore 2.19.12` | use the pinned image |
| `API redirects are refused` | point at the API directly, not a redirecting proxy |
| `Credential environment variable is missing` | export the variable named in the config |
| `Use HTTPS or an SSH tunnel` | publish on loopback and tunnel, or terminate TLS |
| template missing | operation/environment not selected, or `--apply` not re-run |
| duplicate templates | the provisioner never deletes; remove duplicates manually after review |
| task succeeds but no report | verify `INFRASTRUCTURE_REPORT_DIR` and the `/reports` mount |
| SSH target unreachable from Semaphore | inventory host, key store and `SEMAPHORE_KNOWN_HOSTS` |

## Validation and tests

| Symptom | Check |
|---|---|
| `Missing empty-target guard` | add `import_playbook: ../_guard.yml` (and a play name) to the catalog playbook |
| `Risk mismatch` | catalog risk differs from `operation_risk` in the playbook |
| `Missing safety policy` | `pre_tasks` must import `common` |
| syntax check fails | run `ansible-playbook --syntax-check -i inventories/dev/hosts.yml <playbook>` |
| lint fails | `ansible-lint`; fix fatal rules, warnings are documented in `.ansible-lint` |
| integration skipped | set `INFRASTRUCTURE_INTEGRATION=1` on Ubuntu 22.04/24.04 |
| catalog doc out of date | `python3 scripts/reporting/render_catalog.py` |
