# Module documentation

One document per operation group. Each lists the catalog operations, their
Semaphore template names, risk, playbook, inputs and the validated behaviour of
the role.

| Module | Role | Operations |
|---|---|---|
| [`system.md`](system.md) | `roles/system` | 12 |
| [`docker.md`](docker.md) | `roles/docker` | 20 |
| [`postgresql.md`](postgresql.md) | `roles/postgresql` | 11 |
| [`odoo.md`](odoo.md) | `roles/odoo` | 13 |
| [`networking.md`](networking.md) | `roles/networking` | 10 |
| [`django.md`](django.md) | `roles/django` | 11 |
| [`jenkins.md`](jenkins.md) | `roles/jenkins` | 7 |
| [`backup.md`](backup.md) | `roles/backup` | 8 |
| [`monitoring.md`](monitoring.md) | `roles/monitoring` | 6 |

The documents describe the catalog and role code. They do not claim that an
operation was executed against a real host. Actual execution evidence is in
[`../FINAL_IMPLEMENTATION_REPORT.md`](../FINAL_IMPLEMENTATION_REPORT.md).

Regenerate the operation tables from `semaphore/templates/catalog.json` when the
catalog changes; the generated template list is
[`../semaphore/TEMPLATES_CATALOG.md`](../semaphore/TEMPLATES_CATALOG.md).
