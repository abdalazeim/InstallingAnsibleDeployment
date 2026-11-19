# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `playbooks/semaphore/check_api.yml` read-only connectivity check.
- Jenkins declarative pipelines and a Semaphore shared-library step under `jenkins/`.
- Module, architecture, installation, configuration, operations, security,
  troubleshooting, development and Semaphore documentation under `docs/`.
- `tests/syntax`, `tests/security`, `tests/integration` and `tests/idempotency`.
- Root `requirements.yml`, `Makefile`, `LICENSE` and this changelog.
- Per-environment `group_vars` for build, dev, staging and prod.

## [0.3.0] - 2026-11-18

### Added

- `playbooks/_guard.yml`: every catalog playbook now imports a final play that
  fails when no host matches the requested inventory or limit. Empty
  inventories no longer produce a false success.
- `inventories/build/hosts.yml` and `inventories/build/README.md` for
  installation verification and optional Semaphore smoke testing.
- `INFRASTRUCTURE_REPORT_DIR` wiring in the Semaphore provisioner and Compose
  file; report callback falls back to `/reports` when mounted.
- `semaphore/setup/README.md`, `semaphore/README.md`,
  `docs/IMPLEMENTATION_STATUS.md` evidence and honest status notes.
- Structural validator checks for the empty-target guard and build inventory.
- `ansible-lint` and `yamllint` configuration covering the supported root tree.

### Changed

- Historical trees `InfrastructureAutomation/`, `02-Integration/`,
  `automation/`, `01-Installation/` and `control-plane/` moved to `legacy/`.
  They remain in history and on disk but are excluded from quality gates and
  are not part of the supported path.
- Root `README.md` now documents the current platform instead of Phase 1.
- Phase 1 guides/reports are marked as historical records.
- `collections/requirements.yml` is a symlink to the canonical root
  `requirements.yml`; `community.general` accepts `<14` so the documented
  installer matches current collection releases.
- `installation/verify.sh` runs `ansible-lint` in addition to pytest, syntax
  validation and the build verification playbook.
- `playbooks/networking/health_check.yml` is a deprecated alias for
  `traefik_health.yml` instead of an uncatalogued play with `ignore_errors`.
- Django role tasks declare `become: true` explicitly where `become_user` is
  used.

### Removed

- `control-plane/semaphore/key-acess.txt` is no longer tracked. Rotate any value
  that was ever pushed; see `legacy/control-plane/semaphore/README.md`.

### Fixed

- Docker repository definition is a single quoted string, avoiding a YAML
  parsing ambiguity in the previous folded value.
- `community.docker` module parameters and `ansible.builtin.find` arguments were
  reviewed so the catalog playbooks pass syntax checks and lint.
