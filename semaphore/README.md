# Semaphore integration

Semaphore is the supported execution UI for every catalog operation. This
directory contains the deployment and provisioning material; it does not contain
hand-written YAML that is expected to appear in the UI automatically.

| Path | Contents |
|---|---|
| `setup/` | Compose deployment, example environment, provisioner config |
| `templates/` | `catalog.json`, the single source of truth for 98 operations |
| `examples/` | Reviewed configuration variants (GitHub SSH, remote targets) |
| `environments/` | Notes and examples for Semaphore task environments |
| `inventories/` | Mapping between Semaphore inventories and repository files |
| `documentation/` | Pointer to the detailed documentation |

Start with:

- [`docs/semaphore/SEMAPHORE_SETUP.md`](../docs/semaphore/SEMAPHORE_SETUP.md)
- [`docs/semaphore/TEMPLATES_CATALOG.md`](../docs/semaphore/TEMPLATES_CATALOG.md)

The provisioner (`infrastructure-semaphore`) is the only supported automation
for resource creation. It talks to the Semaphore HTTP API, is pinned to version
`2.19.12`, creates or updates resources, never deletes them, and never stores
tokens in the repository.
