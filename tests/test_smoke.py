"""Both packages import and both console scripts answer --help."""

import importlib.metadata
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

import tff_catalog
import tff_site
from tff_catalog import cli as catalog_cli
from tff_site import cli as site_cli

MAINS = {"tff-catalog": catalog_cli.main, "tff-site": site_cli.main}


def test_packages_import():
    assert tff_catalog.__version__ == importlib.metadata.version("tff-catalog")
    date.fromisoformat(tff_catalog.METHOD_VERSION)
    assert tff_site.__doc__


@pytest.mark.parametrize("script", sorted(MAINS))
def test_main_help_returns_zero(script, capsys):
    assert MAINS[script](["--help"]) == 0
    assert capsys.readouterr().out.startswith(f"usage: {script}")


@pytest.mark.parametrize("script", sorted(MAINS))
def test_main_rejects_unknown_command(script, capsys):
    assert MAINS[script](["no-such-command"]) == 2
    assert "unknown command" in capsys.readouterr().err


@pytest.mark.parametrize("script", sorted(MAINS))
def test_console_script_help_exits_zero(script):
    path = shutil.which(script, path=str(Path(sys.executable).parent))
    assert path, f"{script} is not installed next to {sys.executable}"
    result = subprocess.run(
        [path, "--help"], capture_output=True, text=True, check=False, timeout=60
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith(f"usage: {script}")
