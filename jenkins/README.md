# Jenkins integration

Jenkins owns CI/CD: builds, Git-triggered workflows, application release
pipelines and automated tests. **Semaphore owns Ansible execution.** Pipelines
in this directory call the Semaphore API instead of running Ansible or shell
commands on managed hosts.

## Contents

| Path | Purpose |
|---|---|
| `pipelines/Jenkinsfile.django-deploy` | deploy or roll back a Django application |
| `pipelines/Jenkinsfile.docker-update` | update a Compose project after verification |
| `pipelines/Jenkinsfile.odoo-addons` | validate and deploy Odoo addons |
| `pipelines/Jenkinsfile.infrastructure-config` | run an approved system configuration operation |
| `pipelines/Jenkinsfile.scheduled-backup` | trigger and verify a backup |
| `shared-libraries/vars/infrastructureSemaphore.groovy` | shared step: resolve a template, run it, poll to completion |

## Jenkins prerequisites

- Jenkins 2.4xx or later with the **HTTP Request** and **Pipeline: Groovy**
  plugins, plus **Credentials Binding**.
- A Semaphore API token stored as a Jenkins secret text credential, for example
  `semaphore-api-token`.
- The Semaphore URL and project ID configured as job parameters or folder
  environment variables.
- The shared library registered in *Manage Jenkins → System → Global Pipeline
  Libraries* (name `infrastructure`, default version `main`).

## Template lookup

Every Semaphore template is named `<operation name> [<environment>]`, for
example `Django - Deploy Application [prod]`. Pipelines pass a name and the
shared step resolves the numeric template ID at runtime:

```groovy
infrastructureSemaphore(
  url: 'https://semaphore.example.internal',
  projectId: '1',
  templateName: 'Django - Deploy Application [prod]',
  variables: [django_application: 'portal', deployment_version: '2026.11.18-1',
              confirm_operation: 'true', confirm_production: 'true']
)
```

The full list is in `docs/semaphore/TEMPLATES_CATALOG.md`.

## Separation of duties

- Jenkins builds and tests the artifact, then triggers the corresponding
  Semaphore template.
- Jenkins does not run `ansible-playbook` directly and does not hold SSH keys for
  managed hosts.
- Do not schedule the same Ansible operation in Jenkins, Semaphore and cron.
  Choose one owner per operation.
- Production pipelines must require a Jenkins approval that is distinct from the
  Semaphore confirmation. Both gates are intentional.

## Status

The Jenkinsfiles and shared library are delivered as code and are not executed
by the repository's local checks (Jenkins is not installed in this environment).
Validate them in a real Jenkins instance before relying on them.
