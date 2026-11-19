# Operations runbook

## 1. Ownership

| Area | Owner |
|---|---|
| Ansible catalog, roles and playbooks | infrastructure team |
| Semaphore project, inventories, key store, templates, schedules | infrastructure team |
| Jenkins pipelines and release approval | application/CI team |
| Production approvals | service owner |
| Backups and restore drills | infrastructure team |

One operation has one scheduler. Do not run the same operation from Semaphore,
Jenkins and cron.

## 2. Pre-change checklist

1. The target is Ubuntu 22.04/24.04 and the inventory environment is correct.
2. The operation is read-only, change or destructive; confirmations are
   understood.
3. A recent, verified backup exists for data-changing operations.
4. The change window and rollback path are documented.
5. The target is not the Semaphore runner container for mutating operations.
6. The operation was tested in dev or staging with the same variables.
7. Production has `confirm_production=true` only for this task, not stored in
   the environment.

## 3. Environment promotion

```text
build → dev → staging → prod
```

- `build` is for installation verification and the optional smoke template.
- `dev` is the developer host (localhost by default).
- `staging` should mirror production shape with non-production data.
- `prod` requires production confirmation and a verified backup.

Promote the same operation ID and variable shape, not ad-hoc commands.

## 4. Routine schedule

Recommended read-only cadence:

| Frequency | Operation |
|---|---|
| Hourly | `monitoring.server_health`, `docker.health_check` |
| Every 15 minutes | `system.monitoring`, `monitoring.resources` |
| Daily | `monitoring.disk`, `monitoring.applications`, `networking.ssl_check` |
| Daily | `postgresql.health_check`, `odoo.health_check` |
| Daily | `backup.verify` for the latest backup identifiers |
| Weekly | `monitoring.overview` review |

Recommended mutating cadence (separate schedules, explicit approval):

| Frequency | Operation |
|---|---|
| Daily | database/Odoo/Django backups |
| Weekly | full file backup and retention review |
| Monthly | package update in staging, then production |

Schedules are created only from `semaphore/setup/config.example.json` (or a
private copy) and are inactive unless `--enable-schedules` is passed.

## 5. Backup and restore drill

1. Run the backup operation and record the backup identifier.
2. Run `Backup - Verify` with that identifier.
3. Restore into a **new** destination (`restore_destination`) on a disposable
   host.
4. Validate application health against the restored copy.
5. Record duration, size, checksum, owner and result in the operations log.
6. Never restore over production without destructive confirmation and an
   approved change.

## 6. Incidents and rollback

- **Failed deployment**: use the deployment rollback notes from the operation,
  or redeploy the previous `deployment_version`. Do not run destructive
  operations to "clean up" during an incident.
- **Failed migration**: restore the verified database backup into a new
  database, validate, then switch the application after approval.
- **Semaphore unavailable**: use the CLI with the same catalog operation and
  confirmations. Do not run raw playbooks outside the catalog.
- **Lost access**: use the provider console, not the firewall or SSH operation,
  to regain access. Then audit the change that caused it.
- **Compromised credential**: follow the rotation steps in
  `docs/security/SECURITY.md`.

## 7. Maintenance windows

Before a window:

- notify stakeholders and freeze conflicting CI jobs;
- take a verified backup;
- disable or pause overlapping schedules;
- confirm the rollback path and owner.

After a window:

- run the relevant health checks;
- verify reports and task history;
- re-enable schedules and CI;
- record the outcome in the changelog/operations log.

## 8. Monitoring signals

- `system.monitoring`: CPU, memory, swap, load, disk and inode usage.
- `monitoring.disk`: per-filesystem pressure and inode exhaustion.
- `docker.health_check`: daemon and container health.
- `postgresql.health_check`: service, connections and databases.
- `odoo.health_check`: process, PostgreSQL connectivity, HTTP and WebSocket.
- `networking.ssl_check`: certificate chain and expiry threshold.
- `monitoring.overview`: aggregate view for a quick review.

Alerts should map to these operations; do not invent a separate check path.

## 9. Decommissioning

1. Remove the host from the inventory only after backups and data export.
2. Remove Semaphore templates/schedules that reference it (manual review; the
   provisioner never deletes).
3. Rotate host-specific keys.
4. Remove DNS and proxy routes.
5. Record the decommission date and data retention decision.
