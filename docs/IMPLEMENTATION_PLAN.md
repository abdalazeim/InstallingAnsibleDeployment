# Implementation Plan (Phased)

Phase 1: Audit + architecture docs (done).
Phase 2: Core ansible.cfg/inventories/group_vars/host_vars + vault examples.
Phase 3: Ubuntu server module (info/update/users/ssh/firewall/monitoring).
Phase 4: Docker module.
Phase 5: PostgreSQL module.
Phase 6: Odoo 17/19 module.
Phase 7: Traefik module.
Phase 8: Django apps module.
Phase 9: Jenkins integration.
Phase 10: Semaphore integration.
Phase 11: CLI + reporting.
Phase 12: Tests, security, docs.

Gate: syntax-check + idempotency before next phase. No destructive ops by default.
