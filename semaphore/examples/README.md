# Semaphore configuration examples

These files are reviewed starting points. They are not loaded automatically;
copy the values you need into a private configuration file (for example
`semaphore/setup/config.local.json`, which is ignored by Git) and pass it with
`--config`.

| Example | Use when |
|---|---|
| `github-ssh.json` | Semaphore clones the repository from GitHub over SSH |
| `remote-targets.json` | inventories target remote servers over SSH |
| `local-checkout.json` | the repository is mounted read-only at `/workspace` |

Secrets are never placed in these files. Export the environment variables named
by `ssh_private_key_env` and `vault_password_env` before running `--apply`, and
keep API tokens outside the repository.
