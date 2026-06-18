from logging import getLogger
from pathlib import Path

from tiddl.cli.const import APP_PATHS
from .models import AuthData


log = getLogger(__name__)


def _auth_data_file(file: Path | None = None) -> Path:
    return file or APP_PATHS.auth_file


def load_auth_data(file: Path | None = None) -> AuthData:
    auth_file = _auth_data_file(file)
    log.debug(f"loading from '{auth_file}'")

    try:
        file_content = auth_file.read_text()
    except FileNotFoundError:
        return AuthData()

    auth_data = AuthData.model_validate_json(file_content)

    return auth_data


def save_auth_data(auth_data: AuthData, file: Path | None = None):
    auth_file = _auth_data_file(file)
    log.debug(f"saving to '{auth_file}'")

    auth_file.parent.mkdir(parents=True, exist_ok=True)
    with auth_file.open("w") as f:
        f.write(auth_data.model_dump_json())
