# Jenkins pipelines

Each file is a declarative pipeline intended to be loaded as a *Pipeline script
from SCM* with this repository. They call the `infrastructureSemaphore` shared
step, which triggers a Semaphore template and waits for it to finish.

| File | Semaphore templates |
|---|---|
| `Jenkinsfile.django-deploy` | `Django - Deploy Application [<env>]` |
| `Jenkinsfile.docker-update` | `Docker - Compose Update [<env>]` |
| `Jenkinsfile.odoo-addons` | `Odoo - Deploy Addons [<env>]` |
| `Jenkinsfile.infrastructure-config` | approved system operations |
| `Jenkinsfile.scheduled-backup` | backup templates |

Configure `SEMAPHORE_URL` and `SEMAPHORE_PROJECT_ID` as folder-level environment
variables or per-job parameters. The API token is always a Jenkins credential
(`semaphore-api-token` by default).

These pipelines are delivered as code and are **not** executed by local checks.
Validate them in a real Jenkins instance before production use.
