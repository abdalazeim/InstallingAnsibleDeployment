# Development

## 1. Local environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install 'ansible-core==2.21.6' 'ansible-lint==26.11.0' 'pytest>=8,<10' \
  'PyYAML>=6,<7' 'Jinja2>=3.1,<4' -e .
ansible-galaxy collection install -r requirements.yml
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
```

The repository is also importable without installation
(`python -m infrastructure_manager...`) because the package lives at the root.

## 2. Daily commands

```bash
python3 scripts/validation/validate.py          # YAML, Jinja, catalog, guard
python3 scripts/validation/validate.py --syntax # every catalog playbook
ansible-lint                                    # supported tree
python -m pytest -q tests/unit tests/security   # fast tests
python -m pytest -q tests/syntax                # 98 syntax subprocesses
python -m pytest -q                             # everything; integration skips
python3 scripts/reporting/render_catalog.py     # regenerate template docs
```

Or use `make help` for the same targets.

## 3. Adding an operation

1. **Choose the group and ID** (`docker`, `docker.restart_container`).
2. **Add the catalog entry** in `semaphore/templates/catalog.json` with name,
   group, playbook, risk, inputs (mark `required` and enum `choices`) and
   `become`.
3. **Create the playbook** `playbooks/<group>/<task>.yml`:

```yaml
---
- name: Docker - Restart Container
  hosts: '{{ target_hosts | default("all") }}'
  gather_facts: true
  become: true
  any_errors_fatal: true
  vars:
    operation_id: docker.restart_container
    operation_risk: change
  pre_tasks:
    - name: Apply execution policy
      ansible.builtin.import_role:
        name: common
  tasks:
    - name: Docker - Restart Container
      ansible.builtin.include_role:
        name: docker
        tasks_from: restart_container

- name: Validate target selection
  import_playbook: ../_guard.yml
```

4. **Add the role task file** `roles/<group>/tasks/<task>.yml`. Validate every
   input with `ansible.builtin.assert` before acting. Use `no_log: true` for
   secret-bearing tasks. Never build shell strings from inputs.
5. **Add tests** if the operation has logic worth unit testing (library module,
   parsing, path handling).
6. **Run** `validate.py`, `--syntax`, `ansible-lint` and the test suite.
7. **Regenerate** `docs/semaphore/TEMPLATES_CATALOG.md`.
8. **Update** `CHANGELOG.md`.
9. **Re-run** the Semaphore provisioner `--apply` on the destination so the
   template is created.

The validator enforces: playbook exists, `operation_risk` matches the catalog,
`common` is imported in `pre_tasks`, and the guard import is present.

## 4. Adding a module or role

- Role names match the group (`roles/postgresql`, `roles/django`). Shared
  helpers live in `roles/common`.
- Put defaults in `roles/<group>/defaults/main.yml`; never hardcode paths,
  addresses or credentials in tasks.
- Use FQCN (`ansible.builtin.copy`, `community.docker.docker_container`).
- Use handlers for service restarts where possible.
- Templates go in `roles/<group>/templates/`; static files in `files/`.
- Python modules go in `library/` and must not print secrets. Pass secrets as
  module arguments, never in `argv` to an external command.

## 5. Conventions

- Every play has a name; every `import_playbook` has a name.
- Task names are readable and unique within a file.
- Inputs are validated in the first tasks of the role file.
- Mutating tasks are explicit; add `changed_when`/`failed_when` when a command
  is used.
- Read-only commands use `changed_when: false` and `check_mode: false`.
- Avoid `ignore_errors`; use `failed_when` with an explicit condition.
- Avoid `command`/`shell` when a module exists.
- Reports contain aggregate counts only.
- No `StrictHostKeyChecking=no`.
- No hardcoded IPv4 addresses outside loopback.

## 6. Lint configuration

`.ansible-lint` uses `profile: basic` and excludes `legacy/`, caches and
reports. `fqcn`, `var-naming` and `name` are warnings. The remaining
`var-naming[no-role-prefix]` warnings are mostly interface variables from
`roles/common/defaults` (for example `confirm_operation`) and register names;
they are intentionally reported, not fatal.

`.yamllint` allows the repository's consistent sequence indentation style and
disables line length. Do not disable rules globally to hide a real defect.

## 7. Tests

| Directory | Purpose | Runs by default |
|---|---|---|
| `tests/unit` | library modules, catalog, CLI, PostgreSQL parsing | yes |
| `tests/security` | static safety invariants | yes |
| `tests/syntax` | catalog playbook syntax, guard import, file existence | yes |
| `tests/integration` | read-only runs on Ubuntu | no (`INFRASTRUCTURE_INTEGRATION=1`) |
| `tests/idempotency` | second-run `changed=0` | no (`INFRASTRUCTURE_INTEGRATION=1`) |

Never report a skipped or unexecuted test as passed. Integration and idempotency
require a disposable Ubuntu target.

## 8. Historical code

`legacy/` is preserved for reference. It is excluded from lint and tests and is
not part of the supported path. Do not copy configuration from it; known defects
are documented in `docs/REPOSITORY_AUDIT.md` and `docs/PROJECT_STUDY_AR.md`.

## 9. Release process

1. All local checks pass.
2. Versions in `pyproject.toml` and `CHANGELOG.md` are updated.
3. `docs/semaphore/TEMPLATES_CATALOG.md` is regenerated and current.
4. `docs/IMPLEMENTATION_STATUS.md` and `docs/FINAL_IMPLEMENTATION_REPORT.md`
   reflect what was actually tested.
5. Tag the release, then run the installer and Semaphore provisioning on a
   disposable Ubuntu host.
6. Record real evidence; do not claim unexecuted checks.
