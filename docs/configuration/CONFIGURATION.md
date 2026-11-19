# Configuration

## 1. Variable precedence

Relevant layers, lowest to highest:

1. `roles/common/defaults/main.yml` (policy defaults)
2. `inventories/<env>/hosts.yml` (`all.vars`, host vars)
3. `inventories/<env>/group_vars/all.yml`
4. `host_vars/<host>.yml` (instance maps and secrets; ignored by Git)
5. Extra variables from the CLI (`--set`/`-e`) or Semaphore survey

Never rely on the developer machine. No IP address, hostname, application path
or credential is stored in tracked files.

## 2. Inventories

```text
inventories/
├── build/  hosts.yml, group_vars/all.yml, README.md
├── dev/    hosts.yml, group_vars/all.yml
├── staging/hosts.yml, group_vars/all.yml
└── prod/   hosts.yml, group_vars/all.yml
```

Hosts belong under `all.children.managed.hosts`:

```yaml
all:
  vars:
    infrastructure_environment: staging
  children:
    managed:
      hosts:
        app-01:
          ansible_host: 192.0.2.10        # documentation range only
          ansible_user: ubuntu
          ansible_port: 22
```

`infrastructure_environment` must match the inventory and the Semaphore
environment. An unrecognized value is rejected by `roles/common`.

## 3. Common policy variables

| Variable | Default | Meaning |
|---|---|---|
| `infrastructure_environment` | `build` | build/dev/staging/prod |
| `confirm_operation` | `false` | allow change operations |
| `confirm_production` | `false` | allow changes in prod |
| `confirm_destructive_operation` | `false` | allow destructive operations |
| `confirm_reboot` | `false` | allow a reboot |
| `backup_root` | `/var/backups/infrastructure` | absolute backup root |
| `retention_days` | `7` (per env 3/7/14/30) | backup retention |
| `infrastructure_report_dir` | `./reports` | aggregate report directory |

## 4. PostgreSQL instances

```yaml
postgres_instances:
  main:
    mode: native                    # native | docker
    host: /var/run/postgresql        # native socket dir, or hostname in docker mode
    port: 5432
    user: odoo
    password: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      ...
    backup_root: /var/backups/infrastructure/postgresql/main
```

The `infrastructure_postgres` module receives the password through Ansible, not
through process arguments. Never put a plaintext password in group_vars.

## 5. Odoo instances

```yaml
odoo_instances:
  odoo17:
    mode: docker
    container: odoo17
    database: odoo17
    postgres_instance: main
    filestore: /srv/odoo17/filestore
    addons_path: /srv/odoo17/addons
    compose_directory: /srv/odoo17
    compose_service: odoo
    health_url: https://odoo17.example.com/web/health
  odoo19:
    mode: docker
    container: odoo19
    database: odoo19
    postgres_instance: main
    filestore: /srv/odoo19/filestore
    addons_path: /srv/odoo19/addons
    compose_directory: /srv/odoo19
    compose_service: odoo
    health_url: https://odoo19.example.com/web/health
```

Each instance is independent: container, database, filestore and addons path
are per entry. Odoo version is data, so a future release needs only a new entry.
`odoo_instance` selects the entry in every Odoo operation.

## 6. Django applications

```yaml
django_applications:
  portal:
    mode: native                    # native | compose
    directory: /srv/portal
    user: portal
    repository: https://example.com/portal.git
    revision: main
    wsgi: portal.wsgi:application
    service: portal-gunicorn
    port: 8000
    media_directory: /srv/portal/media
    health_url: https://portal.example.com/health/
    environment:
      DJANGO_SETTINGS_MODULE: portal.settings
      SECRET_KEY: !vault |
        $ANSIBLE_VAULT;1.1;AES256
        ...
```

`environment` is passed only to the application process. It is marked `no_log`
in the role. Do not commit `.env` files.

## 7. Backup configuration

- `backup_root` must be an absolute path with a dedicated directory.
- Backups are timestamped, checksummed and confined to `backup_root`.
- Restore always targets a new destination (`restore_destination`), never an
  existing production database, unless an operator explicitly overrides it.
- `retention_days` is applied by `backup.retention`, which is destructive and
  requires destructive confirmation.

## 8. Reports

The callback resolves the report directory in this order:

1. `INFRASTRUCTURE_REPORT_DIR` (set by the Semaphore provisioner to `/reports`)
2. `/reports` when it exists and is a directory
3. `./reports`

Reports contain aggregate counts only. Do not add task output or variables to
them.

## 9. Checking configuration

```bash
ansible-inventory -i inventories/dev/hosts.yml --list
ansible-inventory -i inventories/staging/hosts.yml --graph
ansible-playbook -i inventories/dev/hosts.yml playbooks/system/info.yml
```

An empty inventory fails by design. Configure hosts before running mutating
operations.

## 10. Secrets

Use Ansible Vault or the Semaphore Key Store. Examples:

```bash
ansible-vault create inventories/prod/group_vars/vault.yml
ansible-vault edit inventories/prod/group_vars/vault.yml
ansible-playbook ... --ask-vault-pass
```

Vault passwords and private keys never belong in the repository, reports,
issues or chat. See `docs/security/SECURITY.md`.
