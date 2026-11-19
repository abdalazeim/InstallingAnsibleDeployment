"""Every catalog playbook must pass ansible-playbook --syntax-check."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "semaphore" / "templates" / "catalog.json"
INVENTORY = ROOT / "inventories" / "dev" / "hosts.yml"


def _catalog_playbooks() -> list[str]:
    data = json.loads(CATALOG.read_text())
    return sorted({operation["playbook"] for operation in data["operations"]})


@pytest.mark.syntax
@pytest.mark.parametrize("playbook", _catalog_playbooks())
def test_catalog_playbook_syntax(playbook: str) -> None:
    result = subprocess.run(
        [
            "ansible-playbook",
            "--syntax-check",
            "-i",
            str(INVENTORY),
            playbook,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.syntax
def test_every_catalog_playbook_exists() -> None:
    missing = [path for path in _catalog_playbooks() if not (ROOT / path).is_file()]
    assert missing == []


@pytest.mark.syntax
def test_guard_is_imported_by_every_catalog_playbook() -> None:
    for playbook in _catalog_playbooks():
        text = (ROOT / playbook).read_text()
        assert "import_playbook: ../_guard.yml" in text, playbook
