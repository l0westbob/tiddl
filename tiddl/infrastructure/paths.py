from os import environ
from pathlib import Path


APP_DIR_NAME = ".tiddl"
ENV_KEY = "TIDDL_PATH"


class AppPaths:
    def __init__(self, root: Path | None = None, env_key: str = ENV_KEY) -> None:
        self.env_key = env_key
        self.root = self._resolve_root(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_root(self, root: Path | None) -> Path:
        if root is not None:
            return root.expanduser()

        env_root = environ.get(self.env_key)
        if env_root:
            return Path(env_root).expanduser()

        return Path.home() / APP_DIR_NAME

    @property
    def config_file(self) -> Path:
        return self.root / "config.toml"

    @property
    def auth_file(self) -> Path:
        return self.root / "auth.json"

    @property
    def api_cache(self) -> Path:
        return self.root / "api_cache"

    @property
    def api_debug_dir(self) -> Path:
        return self.root / "api_debug"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"

    @property
    def download_tmp_dir(self) -> Path:
        return self.tmp_dir / "downloads"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"
