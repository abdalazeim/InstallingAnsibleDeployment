# Semaphore task environments

A Semaphore environment stores non-secret variables passed to every task. The
provisioner creates one environment per selected inventory in the
`Infrastructure Automation` project and reconciles these defaults:

```json
{
  "infrastructure_environment": "dev",
  "confirm_operation": false,
  "confirm_production": false,
  "confirm_destructive_operation": false,
  "confirm_reboot": false
}
```

It also sets the task process environment:

```json
{
  "ANSIBLE_CONFIG": "ansible.cfg",
  "INFRASTRUCTURE_REPORT_DIR": "/reports"
}
```

Rules:

- Confirmation flags must remain `false`. They are supplied per task through
  required survey fields and validated by `roles/common`.
- Passwords, private keys and Vault passwords belong in the Key Store, not in
  an environment.
- Environment-specific instance maps belong in `host_vars/<host>.yml` (ignored
  by Git) or in Vault-protected inventory data.

The example `example.json` shows the shape accepted by the provisioner's
`environment_variables` setting. Copy only the keys you need into a private
configuration file.
