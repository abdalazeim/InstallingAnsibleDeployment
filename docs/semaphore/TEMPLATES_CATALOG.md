# Semaphore templates catalog

> Generated from `semaphore/templates/catalog.json`. Do not edit by hand;
> run `python3 scripts/reporting/render_catalog.py` after catalog changes.

The Semaphore provisioner creates one template per operation and
environment, named `<operation name> [<environment>]`. All templates point
at a playbook in this repository and at a real inventory file. A template
is never created for a missing playbook: the provisioner reads this same
catalog and `scripts/validation/validate.py` checks every path.

## Summary

- Operations: **98**
- Read: **48** · Change: **39** · Destructive: **11**
- Environments: `build`, `dev`, `staging`, `prod`
- Templates when all environments are selected: **392**

## Risk and confirmation

| Risk | Requirements |
|---|---|
| `read` | none |
| `change` | `confirm_operation=true`; `confirm_production=true` on prod |
| `destructive` | the above plus `confirm_destructive_operation=true` |

Confirmation values are deliberately absent from the Semaphore
environment. They are required survey fields on each template, so a task
cannot be started by a single click without a decision. Destructive
operations are also refused as schedules.

## Inputs

An asterisk (`*`) marks a required input. Input names are exactly the
Ansible variable names; they are validated by the playbook's first tasks.

## Ubuntu Server Management

12 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `system.firewall_status` | System - Firewall Status | `playbooks/system/firewall_status.yml` | `read` | — |
| `system.health_check` | System - Health Check | `playbooks/system/health_check.yml` | `read` | — |
| `system.info` | System - Information | `playbooks/system/info.yml` | `read` | — |
| `system.monitoring` | System - Resource Monitoring | `playbooks/system/monitoring.yml` | `read` | — |
| `system.ssh_status` | System - SSH Status | `playbooks/system/ssh_status.yml` | `read` | — |
| `system.users_list` | System - User List | `playbooks/system/users_list.yml` | `read` | — |
| `system.verify` | System - Verify | `playbooks/system/verify.yml` | `read` | — |
| `system.packages` | System - Manage Packages | `playbooks/system/packages.yml` | `change` | `package_names`*, `package_state` |
| `system.ssh_configure` | System - SSH Configuration | `playbooks/system/ssh_configure.yml` | `change` | `ssh_access_verified`*, `ssh_port` |
| `system.update` | System - Update Packages | `playbooks/system/update.yml` | `change` | `upgrade_type`, `confirm_reboot` |
| `system.users_manage` | System - User Management | `playbooks/system/users_manage.yml` | `change` | `managed_username`*, `managed_user_state` |
| `system.firewall_manage` | System - Firewall Management | `playbooks/system/firewall_manage.yml` | `destructive` | `firewall_state` |

## Docker Infrastructure

20 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `docker.compose_list` | Docker - List Compose Projects | `playbooks/docker/compose_list.yml` | `read` | — |
| `docker.container_logs` | Docker - Container Logs | `playbooks/docker/container_logs.yml` | `read` | `container_name`*, `allow_sensitive_logs` |
| `docker.health_check` | Docker - Health Check | `playbooks/docker/health_check.yml` | `read` | — |
| `docker.inspect_container` | Docker - Inspect Container | `playbooks/docker/inspect_container.yml` | `read` | `container_name`* |
| `docker.list_containers` | Docker - List Containers | `playbooks/docker/list_containers.yml` | `read` | — |
| `docker.list_images` | Docker - List Images | `playbooks/docker/list_images.yml` | `read` | — |
| `docker.resource_usage` | Docker - Resource Usage | `playbooks/docker/resource_usage.yml` | `read` | — |
| `docker.compose_restart` | Docker - Compose Restart | `playbooks/docker/compose_restart.yml` | `change` | `compose_directory`*, `compose_project`*, `deployment_backup_verified` |
| `docker.compose_up` | Docker - Compose Up | `playbooks/docker/compose_up.yml` | `change` | `compose_directory`*, `compose_project`*, `deployment_backup_verified` |
| `docker.compose_update` | Docker - Compose Update | `playbooks/docker/compose_update.yml` | `change` | `compose_directory`*, `compose_project`*, `deployment_backup_verified` |
| `docker.install` | Docker - Install | `playbooks/docker/install.yml` | `change` | — |
| `docker.network_manage` | Docker - Network Management | `playbooks/docker/network_manage.yml` | `change` | `network_name`*, `network_state` |
| `docker.pause_container` | Docker - Pause Container | `playbooks/docker/pause_container.yml` | `change` | `container_name`* |
| `docker.restart_container` | Docker - Restart Container | `playbooks/docker/restart_container.yml` | `change` | `container_name`* |
| `docker.start_container` | Docker - Start Container | `playbooks/docker/start_container.yml` | `change` | `container_name`* |
| `docker.stop_container` | Docker - Stop Container | `playbooks/docker/stop_container.yml` | `change` | `container_name`* |
| `docker.unpause_container` | Docker - Unpause Container | `playbooks/docker/unpause_container.yml` | `change` | `container_name`* |
| `docker.update_images` | Docker - Pull Image | `playbooks/docker/update_images.yml` | `change` | `image_reference`* |
| `docker.compose_down` | Docker - Compose Down | `playbooks/docker/compose_down.yml` | `destructive` | `compose_directory`*, `compose_project`*, `deployment_backup_verified` |
| `docker.delete_container` | Docker - Delete Container | `playbooks/docker/delete_container.yml` | `destructive` | `container_name`* |

## Odoo Management

13 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `odoo.addons_validate` | Odoo - Addons Validation | `playbooks/odoo/addons_validate.yml` | `read` | `odoo_instance`* |
| `odoo.health_check` | Odoo - Health Check | `playbooks/odoo/health_check.yml` | `read` | `odoo_instance`* |
| `odoo.list_instances` | Odoo - List Instances | `playbooks/odoo/list_instances.yml` | `read` | — |
| `odoo.logs` | Odoo - Logs | `playbooks/odoo/logs.yml` | `read` | `odoo_instance`*, `allow_sensitive_logs`* |
| `odoo.addons_deploy` | Odoo - Deploy Addons | `playbooks/odoo/addons_deploy.yml` | `change` | `odoo_instance`*, `addons_repository`*, `addons_revision`* |
| `odoo.backup_database` | Odoo - Database Backup | `playbooks/odoo/backup_database.yml` | `change` | `odoo_instance`* |
| `odoo.backup_filestore` | Odoo - Filestore Backup | `playbooks/odoo/backup_filestore.yml` | `change` | `odoo_instance`* |
| `odoo.backup_full` | Odoo - Full Backup | `playbooks/odoo/backup_full.yml` | `change` | `odoo_instance`*, `confirm_downtime`* |
| `odoo.restart` | Odoo - Restart Instance | `playbooks/odoo/restart.yml` | `change` | `odoo_instance`* |
| `odoo.start` | Odoo - Start Instance | `playbooks/odoo/start.yml` | `change` | `odoo_instance`* |
| `odoo.stop` | Odoo - Stop Instance | `playbooks/odoo/stop.yml` | `change` | `odoo_instance`* |
| `odoo.restore` | Odoo - Restore Backup | `playbooks/odoo/restore.yml` | `destructive` | `odoo_instance`*, `bundle_id`*, `restore_database`*, `restore_destination`* |
| `odoo.update_modules` | Odoo - Update Selected Modules | `playbooks/odoo/update_modules.yml` | `destructive` | `odoo_instance`*, `odoo_modules`*, `confirm_downtime`*, `deployment_backup_verified`* |

## PostgreSQL Administration

11 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `postgresql.connections` | PostgreSQL - Connections | `playbooks/postgresql/connections.yml` | `read` | `postgres_instance`* |
| `postgresql.database_info` | PostgreSQL - Database Information | `playbooks/postgresql/database_info.yml` | `read` | `postgres_instance`*, `database_name`* |
| `postgresql.health_check` | PostgreSQL - Status | `playbooks/postgresql/health_check.yml` | `read` | `postgres_instance`* |
| `postgresql.list_databases` | PostgreSQL - List Databases | `playbooks/postgresql/list_databases.yml` | `read` | `postgres_instance`* |
| `postgresql.verify_backup` | PostgreSQL - Verify Backup | `playbooks/postgresql/verify_backup.yml` | `read` | `postgres_instance`*, `backup_id`* |
| `postgresql.backup` | PostgreSQL - Backup Database | `playbooks/postgresql/backup.yml` | `change` | `postgres_instance`*, `database_name`* |
| `postgresql.create_database` | PostgreSQL - Create Database | `playbooks/postgresql/create_database.yml` | `change` | `postgres_instance`*, `database_name`* |
| `postgresql.privileges` | PostgreSQL - Database Privileges | `playbooks/postgresql/privileges.yml` | `change` | `postgres_instance`*, `database_name`*, `database_username`* |
| `postgresql.users_manage` | PostgreSQL - User Management | `playbooks/postgresql/users_manage.yml` | `change` | `postgres_instance`*, `database_username`* |
| `postgresql.delete_database` | PostgreSQL - Delete Database | `playbooks/postgresql/delete_database.yml` | `destructive` | `postgres_instance`*, `database_name`* |
| `postgresql.restore` | PostgreSQL - Restore Database | `playbooks/postgresql/restore.yml` | `destructive` | `postgres_instance`*, `database_name`*, `backup_id`* |

## Traefik & Networking

10 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `networking.connectivity` | Networking - Connectivity Check | `playbooks/networking/connectivity.yml` | `read` | `network_host`*, `network_port`* |
| `networking.dns_check` | Networking - DNS Check | `playbooks/networking/dns_check.yml` | `read` | `dns_name`* |
| `networking.docker_networks` | Docker - Network Inspection | `playbooks/networking/docker_networks.yml` | `read` | `network_name`* |
| `networking.port_check` | Networking - Port Check | `playbooks/networking/port_check.yml` | `read` | `network_host`*, `network_port`* |
| `networking.routers` | Traefik - Router Inspection | `playbooks/networking/routers.yml` | `read` | `traefik_api_url`* |
| `networking.ssl_check` | Traefik - SSL Certificate Check | `playbooks/networking/ssl_check.yml` | `read` | `tls_hostname`* |
| `networking.traefik_health` | Traefik - Health Check | `playbooks/networking/traefik_health.yml` | `read` | `traefik_api_url`* |
| `networking.traefik_status` | Traefik - Status | `playbooks/networking/traefik_status.yml` | `read` | `traefik_api_url`* |
| `networking.traefik_validate` | Traefik - Configuration Validation | `playbooks/networking/traefik_validate.yml` | `read` | `traefik_directory`* |
| `networking.traefik_deploy` | Traefik - Deploy | `playbooks/networking/traefik_deploy.yml` | `change` | `traefik_directory`*, `traefik_version`*, `traefik_acme_email`* |

## Django Applications

11 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `django.health_check` | Django - Health Check | `playbooks/django/health_check.yml` | `read` | `django_application`* |
| `django.list_applications` | Django - List Applications | `playbooks/django/list_applications.yml` | `read` | — |
| `django.status` | Django - Application Status | `playbooks/django/status.yml` | `read` | `django_application`* |
| `django.backup_database` | Django - Backup Database | `playbooks/django/backup_database.yml` | `change` | `django_application`* |
| `django.backup_media` | Django - Backup Media | `playbooks/django/backup_media.yml` | `change` | `django_application`* |
| `django.collectstatic` | Django - Collect Static | `playbooks/django/collectstatic.yml` | `change` | `django_application`*, `deployment_backup_verified` |
| `django.deploy` | Django - Deploy Application | `playbooks/django/deploy.yml` | `change` | `django_application`*, `deployment_version`* |
| `django.restart_gunicorn` | Django - Restart Gunicorn | `playbooks/django/restart_gunicorn.yml` | `change` | `django_application`* |
| `django.update` | Django - Update Application | `playbooks/django/update.yml` | `change` | `django_application`*, `deployment_version`* |
| `django.migrate` | Django - Run Migrations | `playbooks/django/migrate.yml` | `destructive` | `django_application`*, `deployment_backup_verified` |
| `django.restore` | Django - Restore Backup | `playbooks/django/restore.yml` | `destructive` | `django_application`*, `restore_database`*, `database_backup_id`*, `media_backup_id`*, `restore_destination`* |

## Jenkins Integration

7 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `jenkins.build_status` | Jenkins - Build Status | `playbooks/jenkins/build_status.yml` | `read` | `jenkins_url`*, `jenkins_job_path`*, `jenkins_build_number`* |
| `jenkins.health_check` | Jenkins - Health Check | `playbooks/jenkins/health_check.yml` | `read` | `jenkins_url`* |
| `jenkins.integration_test` | Jenkins - Integration Test | `playbooks/jenkins/integration_test.yml` | `read` | `jenkins_url`* |
| `jenkins.list_jobs` | Jenkins - List Jobs | `playbooks/jenkins/list_jobs.yml` | `read` | `jenkins_url`* |
| `jenkins.status` | Jenkins - Status | `playbooks/jenkins/status.yml` | `read` | `jenkins_url`* |
| `jenkins.deploy` | Jenkins - Deployment | `playbooks/jenkins/deploy.yml` | `change` | `jenkins_url`*, `jenkins_job_path`* |
| `jenkins.trigger_job` | Jenkins - Trigger Job | `playbooks/jenkins/trigger_job.yml` | `change` | `jenkins_url`*, `jenkins_job_path`* |

## Backup & Recovery

8 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `backup.list` | Backup - List Backups | `playbooks/backup/list.yml` | `read` | — |
| `backup.verify` | Backup - Verify | `playbooks/backup/verify.yml` | `read` | `backup_id`* |
| `backup.django` | Backup - Django Database | `playbooks/backup/django.yml` | `change` | `django_application`* |
| `backup.full_backup` | Backup - Files Backup | `playbooks/backup/full_backup.yml` | `change` | `backup_source`* |
| `backup.odoo` | Backup - Odoo | `playbooks/backup/odoo.yml` | `change` | `odoo_instance`*, `confirm_downtime`* |
| `backup.postgresql` | Backup - PostgreSQL | `playbooks/backup/postgresql.yml` | `change` | `postgres_instance`*, `database_name`* |
| `backup.restore` | Backup - Restore | `playbooks/backup/restore.yml` | `destructive` | `backup_id`*, `restore_destination`* |
| `backup.retention` | Backup - Retention Cleanup | `playbooks/backup/retention.yml` | `destructive` | — |

## Monitoring & Health Checks

6 operations.

| Operation ID | Template name | Playbook | Risk | Inputs |
|---|---|---|---|---|
| `monitoring.applications` | Monitoring - Application Health | `playbooks/monitoring/applications.yml` | `read` | `django_application`* |
| `monitoring.disk` | Monitoring - Disk Usage | `playbooks/monitoring/disk.yml` | `read` | — |
| `monitoring.docker` | Monitoring - Docker Health | `playbooks/monitoring/docker.yml` | `read` | — |
| `monitoring.overview` | Monitoring - Infrastructure Overview | `playbooks/monitoring/overview.yml` | `read` | — |
| `monitoring.resources` | Monitoring - CPU and RAM | `playbooks/monitoring/resources.yml` | `read` | — |
| `monitoring.server_health` | Monitoring - Server Health | `playbooks/monitoring/server_health.yml` | `read` | — |

## Odoo version selection

Odoo 17 and Odoo 19 are not separate templates. Each Odoo operation takes
an `odoo_instance` input, and the instance definition supplies the
container, database, filestore and compose paths. This supports future
Odoo versions without adding templates or changing playbooks.

## Environments

| Environment | Inventory | Confirmation policy |
|---|---|---|
| build | `inventories/build/hosts.yml` | read-only verification or an SSH target |
| dev | `inventories/dev/hosts.yml` | change confirmation |
| staging | `inventories/staging/hosts.yml` | change confirmation |
| prod | `inventories/prod/hosts.yml` | change and production confirmation |

## Verification status

The catalog and the playbook paths are checked locally. A live Semaphore
instance has **not** been provisioned from this checkout, so the number of
templates visible in the UI and successfully executed is currently zero.
See `docs/FINAL_IMPLEMENTATION_REPORT.md` for the exact status.
