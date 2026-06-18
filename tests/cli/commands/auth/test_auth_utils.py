import importlib
from pathlib import Path

from tiddl.cli.utils.auth.core import load_auth_data, save_auth_data
from tiddl.cli.utils.auth.models import AuthData


def test_load_auth_data(tmp_path: Path):
    file = tmp_path / "auth.json"

    auth_data = AuthData(
        token="token",
        refresh_token="refresh_token",
        expires_at=0,
        user_id="user_id",
        country_code="country_code",
    )

    file.write_text(auth_data.model_dump_json())

    loaded_auth_data = load_auth_data(file)

    assert isinstance(loaded_auth_data, AuthData)
    assert loaded_auth_data.__dict__ == auth_data.__dict__


def test_save_auth_data(tmp_path: Path):
    file = tmp_path / "auth.json"

    auth_data = AuthData(
        token="token",
        refresh_token="refresh_token",
        expires_at=0,
        user_id="user_id",
        country_code="country_code",
    )

    save_auth_data(auth_data=auth_data, file=file)

    loaded_auth_data = AuthData.model_validate_json(file.read_text())

    assert loaded_auth_data.__dict__ == auth_data.__dict__


def test_default_auth_path_follows_app_paths(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("TIDDL_PATH", str(tmp_path / "state"))

    from tiddl.cli import const as const_module
    from tiddl.cli.utils import auth as auth_module

    importlib.reload(const_module)
    importlib.reload(auth_module.core)

    auth_data = AuthData(
        token="token",
        refresh_token="refresh_token",
        expires_at=0,
        user_id="user_id",
        country_code="country_code",
    )

    auth_module.core.save_auth_data(auth_data)
    loaded_auth_data = auth_module.core.load_auth_data()

    assert loaded_auth_data.__dict__ == auth_data.__dict__
    assert (tmp_path / "state" / "auth.json").exists()
