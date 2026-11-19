# Semaphore inventories

The provisioner creates one file inventory per environment and links it to the
repository selected in the project.

| Semaphore inventory | Path in repository | Hosts |
|---|---|---|
| `Infrastructure - build` | `inventories/build/hosts.yml` | localhost for installation verification; replace with an SSH target in containers |
| `Infrastructure - dev` | `inventories/dev/hosts.yml` | localhost by default |
| `Infrastructure - staging` | `inventories/staging/hosts.yml` | empty until configured |
| `Infrastructure - prod` | `inventories/prod/hosts.yml` | empty until configured |

Hosts are declared under `all.children.managed.hosts`:

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

Use real addresses only in private inventory forks or `host_vars` that are not
committed. The containerized runner reaches `localhost` as itself, not as the
Ubuntu host, so mutating operations require an SSH target.

An inventory that selects no hosts fails through `playbooks/_guard.yml`. A
skipped play is never reported as success.
