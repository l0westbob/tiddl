from typer.testing import CliRunner
import re

from tiddl.cli.app import app


runner = CliRunner()


def test_root_help_shows_commands():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "auth" in result.stdout
    assert "download" in result.stdout


def test_auth_help_shows_subcommands():
    result = runner.invoke(app, ["auth", "--help"])

    assert result.exit_code == 0
    assert "login" in result.stdout
    assert "logout" in result.stdout
    assert "refresh" in result.stdout


def test_download_help_shows_options():
    result = runner.invoke(app, ["download", "--help"], color=False)

    assert result.exit_code == 0
    ansi_re = re.compile(r"\x1b\[[0-9;]*[mK]")
    output = ansi_re.sub("", result.stdout + result.stderr)

    assert "--track-quality" in output
    assert "--path" in output
    assert "--threads-count" in output
