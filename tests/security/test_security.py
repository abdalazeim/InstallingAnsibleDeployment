"""Static security checks for the supported tree.

These tests do not prove a host is secure. They prevent regressions that would
reintroduce known unsafe defaults into tracked files.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_DIRS = ["playbooks", "roles", "inventories", "library", "plugins", "semaphore"]
TEXT_SUFFIXES = {".yml", ".yaml", ".cfg", ".json", ".py", ".sh", ".j2"}
LOOPBACK = {"127.0.0.1", "0.0.0.0", "255.255.255.255"}


def _supported_files() -> list[Path]:
    files: list[Path] = []
    for directory in SUPPORTED_DIRS:
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                files.append(path)
    return files


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        pytest.skip("not a Git checkout")
    return result.stdout.splitlines()


@pytest.mark.security
@pytest.mark.parametrize(
    "suffix", [".env", ".pem", ".key", ".vault-password", ".log", ".retry"]
)
def test_sensitive_suffixes_are_not_tracked(suffix: str) -> None:
    offenders = [name for name in _tracked_files() if name.endswith(suffix)]
    assert offenders == []


@pytest.mark.security
def test_credential_note_is_not_tracked() -> None:
    offenders = [name for name in _tracked_files() if "key-acess" in name]
    assert offenders == []


@pytest.mark.security
def test_ansible_cfg_keeps_host_key_checking() -> None:
    text = (ROOT / "ansible.cfg").read_text().lower()
    assert re.search(r"^host_key_checking\s*=\s*true\s*$", text, re.MULTILINE)


@pytest.mark.security
def test_supported_tree_does_not_disable_host_key_checking() -> None:
    offenders = []
    for path in _supported_files():
        if "StrictHostKeyChecking=no" in path.read_text(errors="ignore"):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


@pytest.mark.security
def test_no_hardcoded_ipv4_addresses_outside_loopback() -> None:
    pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    offenders = []
    for path in _supported_files():
        for line in path.read_text(errors="ignore").splitlines():
            for candidate in pattern.findall(line):
                if candidate not in LOOPBACK:
                    offenders.append(f"{path.relative_to(ROOT)}: {candidate}")
    assert offenders == []


@pytest.mark.security
def test_confirmation_flags_default_to_false() -> None:
    text = (ROOT / "roles" / "common" / "defaults" / "main.yml").read_text()
    for flag in (
        "confirm_operation",
        "confirm_production",
        "confirm_destructive_operation",
        "confirm_reboot",
    ):
        assert re.search(rf"^{flag}:\s*false\s*$", text, re.MULTILINE), flag


@pytest.mark.security
def test_destructive_operations_require_confirmation() -> None:
    policy = (ROOT / "roles" / "common" / "tasks" / "main.yml").read_text()
    assert "confirm_destructive_operation" in policy
    catalog = json.loads((ROOT / "semaphore" / "templates" / "catalog.json").read_text())
    destructive = [op for op in catalog["operations"] if op["risk"] == "destructive"]
    assert destructive, "catalog should declare destructive operations explicitly"


@pytest.mark.security
def test_semaphore_example_does_not_enable_confirmations() -> None:
    config = json.loads((ROOT / "semaphore" / "setup" / "config.example.json").read_text())
    for variables in config.get("environment_variables", {}).values():
        for key, value in variables.items():
            if key.startswith("confirm_"):
                assert value is False, key


@pytest.mark.security
def test_compose_does_not_mount_docker_socket() -> None:
    compose = (ROOT / "semaphore" / "setup" / "compose.yaml").read_text()
    assert "/var/run/docker.sock" not in compose


@pytest.mark.security
def test_empty_inventory_fails_closed() -> None:
    """A playbook against an empty inventory must fail, not report success."""
    result = subprocess.run(
        [
            "ansible-playbook",
            "-i",
            str(ROOT / "inventories" / "staging" / "hosts.yml"),
            "playbooks/system/info.yml",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "No hosts match" in output, output

