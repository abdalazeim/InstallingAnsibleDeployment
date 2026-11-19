"""Read-only integration checks.

These run only when INFRASTRUCTURE_INTEGRATION=1 and the current host is a
supported Ubuntu release. They never change the host.
"""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD_INVENTORY = ROOT / "inventories" / "build" / "hosts.yml"

pytestmark = pytest.mark.integration


def _enabled() -> bool:
    if os.environ.get("INFRASTRUCTURE_INTEGRATION") != "1":
        return False
    try:
        release = platform.freedesktop_os_release()
    except OSError:
        return False
    return release.get("ID") == "ubuntu" and release.get("VERSION_ID") in {"22.04", "24.04"}


@pytest.mark.skipif(not _enabled(), reason="set INFRASTRUCTURE_INTEGRATION=1 on Ubuntu 22.04/24.04")
@pytest.mark.parametrize(
    "playbook", ["playbooks/system/info.yml", "playbooks/system/verify.yml"]
)
def test_read_only_playbook_runs(playbook: str) -> None:
    result = subprocess.run(
        ["ansible-playbook", "-i", str(BUILD_INVENTORY), playbook],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "failed=0" in result.stdout
