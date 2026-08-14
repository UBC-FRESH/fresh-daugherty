from __future__ import annotations

import importlib

import typer.testing
from typer.testing import CliRunner

from fresh_daugherty import __version__
from fresh_daugherty.cli import app

runner = CliRunner()


def test_version() -> None:
    from importlib import metadata as importlib_metadata

    assert __version__ == importlib_metadata.version("fresh-daugherty")


def test_cli_importable() -> None:
    assert app.info.name == "fresh-daugherty"


def test_cli_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_cli_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("open-loop", "replan-run", "consistency-run", "version"):
        assert command in result.stdout


def test_module_stubs_importable() -> None:
    for module in ("cli",):
        imported = importlib.import_module(f"fresh_daugherty.{module}")
        assert imported.__doc__


def test_typer_testing_available() -> None:
    assert typer.testing
