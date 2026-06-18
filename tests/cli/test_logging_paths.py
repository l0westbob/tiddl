import importlib
import logging
from pathlib import Path
from unittest.mock import patch

from tiddl.cli.const import ENV_KEY


def test_cli_logging_uses_app_paths(monkeypatch, tmp_path: Path):
    monkeypatch.setenv(ENV_KEY, str(tmp_path / "state"))

    from tiddl.cli import const as const_module
    from tiddl import cli as cli_module

    importlib.reload(const_module)
    importlib.reload(cli_module)

    assert const_module.APP_PATHS.logs_dir == tmp_path / "state" / "logs"
    assert (tmp_path / "state" / "logs" / "latest.log").exists()


def test_cli_logging_falls_back_to_stdout_when_file_logging_fails(
    monkeypatch, tmp_path: Path
):
    monkeypatch.setenv(ENV_KEY, str(tmp_path / "state"))

    with patch("tiddl.cli.logging.FileHandler", side_effect=PermissionError("nope")):
        from tiddl.cli import const as const_module
        from tiddl import cli as cli_module

        importlib.reload(const_module)
        importlib.reload(cli_module)

    assert isinstance(cli_module.handler, logging.StreamHandler)
