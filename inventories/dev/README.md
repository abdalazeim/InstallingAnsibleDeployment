# dev inventory
Only build/dev provide localhost. Under containerized Semaphore, localhost means the runner container, not the Ubuntu host. Configure SSH targets before using mutating tasks.
Add hosts under `all.children.managed.hosts` with `ansible_host`, `ansible_user`, `ansible_port` and a trusted host key in the runner's known_hosts. Keep secrets in Vault/Key Store. Empty inventories intentionally fail target selection; do not treat skipped plays as success.
Use per-host `host_vars/<alias>.yml` (ignored by Git) for application instance definitions. Environment is declared in inventory and must match the Semaphore environment.
