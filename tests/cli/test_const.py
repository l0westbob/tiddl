import pytest
from pathlib import Path

from tiddl.cli.const import get_app_path, APP_DIR_NAME, ENV_KEY
from tiddl.infrastructure.paths import AppPaths


def test_env_key_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    custom_path = tmp_path / "customdir"
    monkeypatch.setenv(ENV_KEY, str(custom_path))
    app_path = get_app_path(ENV_KEY)

    assert app_path == custom_path


def test_default_path_if_unset(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(ENV_KEY, raising=False)
    app_path = get_app_path(ENV_KEY)

    assert str(Path.home()) in str(app_path)
    assert app_path.name == APP_DIR_NAME


def test_app_paths_resolve_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv(ENV_KEY, str(tmp_path / "state"))

    paths = AppPaths()

    assert paths.root == tmp_path / "state"
    assert paths.config_file == tmp_path / "state" / "config.toml"
    assert paths.auth_file == tmp_path / "state" / "auth.json"
    assert paths.api_cache == tmp_path / "state" / "api_cache"
    assert paths.api_debug_dir == tmp_path / "state" / "api_debug"
    assert paths.tmp_dir == tmp_path / "state" / "tmp"
    assert paths.download_tmp_dir == tmp_path / "state" / "tmp" / "downloads"
    assert paths.logs_dir == tmp_path / "state" / "logs"


def test_app_paths_accepts_explicit_root(tmp_path: Path):
    explicit_root = tmp_path / "explicit"

    paths = AppPaths(root=explicit_root)

    assert paths.root == explicit_root
    assert paths.config_file == explicit_root / "config.toml"
    assert paths.auth_file == explicit_root / "auth.json"
    assert paths.api_cache == explicit_root / "api_cache"
    assert paths.api_debug_dir == explicit_root / "api_debug"
    assert paths.tmp_dir == explicit_root / "tmp"
    assert paths.download_tmp_dir == explicit_root / "tmp" / "downloads"
    assert paths.logs_dir == explicit_root / "logs"
