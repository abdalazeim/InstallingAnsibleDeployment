"""Idempotency checks for read-only operations.

The second run of a read-only playbook must report ``changed=0``. This does not
prove idempotency for mutating operations; those require a disposable target.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD_INVENTORY = ROOT / "inventories" / "build" / "hosts.yml"
RECAP = re.compile(r"changed=(\d+)")

pytestmark = [
    pytest.mark.idempotency,
    pytest.mark.skipif(
        os.environ.get("INFRASTRUCTURE_INTEGRATION") != "1",
        reason="set INFRASTRUCTURE_INTEGRATION=1 on a disposable Ubuntu target",
    ),
]


@pytest.mark.parametrize("playbook", ["playbooks/system/verify.yml"])
def test_read_only_playbook_is_idempotent(playbook: str) -> None:
    for _ in range(2):
        result = subprocess.run(
            ["ansible-playbook", "-i", str(BUILD_INVENTORY), playbook],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    changed = [int(value) for value in RECAP.findall(result.stdout)]
    assert changed, result.stdout
    assert max(changed) == 0, result.stdout
