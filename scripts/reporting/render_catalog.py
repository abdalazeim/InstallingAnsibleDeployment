#!/usr/bin/env python3
"""Render the Semaphore templates catalog from the operation catalog.

The catalog is the single source of truth. This script keeps the human-readable
documentation aligned with it and can be used as a documentation check:

    python3 scripts/reporting/render_catalog.py
    python3 scripts/reporting/render_catalog.py --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "semaphore" / "templates" / "catalog.json"
DEFAULT_OUTPUT = ROOT / "docs" / "semaphore" / "TEMPLATES_CATALOG.md"

GROUPS = [
    ("system", "Ubuntu Server Management"),
    ("docker", "Docker Infrastructure"),
    ("odoo", "Odoo Management"),
    ("postgresql", "PostgreSQL Administration"),
    ("networking", "Traefik & Networking"),
    ("django", "Django Applications"),
    ("jenkins", "Jenkins Integration"),
    ("backup", "Backup & Recovery"),
    ("monitoring", "Monitoring & Health Checks"),
]
RISK_ORDER = {"read": 0, "change": 1, "destructive": 2}


def render(catalog: dict) -> str:
    operations = catalog["operations"]
    counts = {risk: sum(1 for op in operations if op["risk"] == risk) for risk in RISK_ORDER}
    lines = [
        "# Semaphore templates catalog",
        "",
        "> Generated from `semaphore/templates/catalog.json`. Do not edit by hand;",
        "> run `python3 scripts/reporting/render_catalog.py` after catalog changes.",
        "",
        "The Semaphore provisioner creates one template per operation and",
        "environment, named `<operation name> [<environment>]`. All templates point",
        "at a playbook in this repository and at a real inventory file. A template",
        "is never created for a missing playbook: the provisioner reads this same",
        "catalog and `scripts/validation/validate.py` checks every path.",
        "",
        "## Summary",
        "",
        f"- Operations: **{len(operations)}**",
        f"- Read: **{counts['read']}** · Change: **{counts['change']}** · "
        f"Destructive: **{counts['destructive']}**",
        "- Environments: `build`, `dev`, `staging`, `prod`",
        f"- Templates when all environments are selected: **{len(operations) * 4}**",
        "",
        "## Risk and confirmation",
        "",
        "| Risk | Requirements |",
        "|---|---|",
        "| `read` | none |",
        "| `change` | `confirm_operation=true`; `confirm_production=true` on prod |",
        "| `destructive` | the above plus `confirm_destructive_operation=true` |",
        "",
        "Confirmation values are deliberately absent from the Semaphore",
        "environment. They are required survey fields on each template, so a task",
        "cannot be started by a single click without a decision. Destructive",
        "operations are also refused as schedules.",
        "",
        "## Inputs",
        "",
        "An asterisk (`*`) marks a required input. Input names are exactly the",
        "Ansible variable names; they are validated by the playbook's first tasks.",
        "",
    ]

    by_group: dict[str, list[dict]] = {}
    for operation in operations:
        by_group.setdefault(operation["group"], []).append(operation)

    for group, title in GROUPS:
        group_ops = sorted(
            by_group.get(group, []),
            key=lambda op: (RISK_ORDER.get(op["risk"], 9), op["id"]),
        )
        if not group_ops:
            continue
        lines += [
            f"## {title}",
            "",
            f"{len(group_ops)} operations.",
            "",
            "| Operation ID | Template name | Playbook | Risk | Inputs |",
            "|---|---|---|---|---|",
        ]
        for op in group_ops:
            inputs = ", ".join(
                f"`{name}`{'*' if spec.get('required') else ''}"
                for name, spec in op["inputs"].items()
            ) or "—"
            lines.append(
                f"| `{op['id']}` | {op['name']} | `{op['playbook']}` | "
                f"`{op['risk']}` | {inputs} |"
            )
        lines.append("")

    lines += [
        "## Odoo version selection",
        "",
        "Odoo 17 and Odoo 19 are not separate templates. Each Odoo operation takes",
        "an `odoo_instance` input, and the instance definition supplies the",
        "container, database, filestore and compose paths. This supports future",
        "Odoo versions without adding templates or changing playbooks.",
        "",
        "## Environments",
        "",
        "| Environment | Inventory | Confirmation policy |",
        "|---|---|---|",
        "| build | `inventories/build/hosts.yml` | read-only verification or an SSH target |",
        "| dev | `inventories/dev/hosts.yml` | change confirmation |",
        "| staging | `inventories/staging/hosts.yml` | change confirmation |",
        "| prod | `inventories/prod/hosts.yml` | change and production confirmation |",
        "",
        "## Verification status",
        "",
        "The catalog and the playbook paths are checked locally. A live Semaphore",
        "instance has **not** been provisioned from this checkout, so the number of",
        "templates visible in the UI and successfully executed is currently zero.",
        "See `docs/FINAL_IMPLEMENTATION_REPORT.md` for the exact status.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the output file is out of date",
    )
    args = parser.parse_args(argv)
    catalog = json.loads(CATALOG.read_text())
    rendered = render(catalog)
    output = Path(args.output)
    if args.check:
        if not output.is_file() or output.read_text() != rendered:
            print(f"out of date: {output}", file=sys.stderr)
            return 1
        print(f"up to date: {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered)
    print(f"wrote {output} ({len(rendered.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
