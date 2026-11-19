# Jenkins shared libraries

Register this directory as a global pipeline library named `infrastructure`.

| File | Step |
|---|---|
| `vars/infrastructureSemaphore.groovy` | `infrastructureSemaphore(...)` |

The step talks to the Semaphore HTTP API, resolves a template by name, starts a
task with survey variables, polls until the task finishes and fails the build on
`error`, `stopped` or timeout. It never executes Ansible locally and never prints
the API token.

Required Jenkins plugins: Pipeline, HTTP Request, Credentials Binding,
Pipeline Utility Steps (`readJSON`).
