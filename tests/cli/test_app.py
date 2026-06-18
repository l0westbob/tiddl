from typer.testing import CliRunner

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
    result = runner.invoke(app, ["download", "--help"])

    assert result.exit_code == 0
    assert "--track-quality" in result.stdout
    assert "--path" in result.stdout
    assert "--threads-count" in result.stdout
