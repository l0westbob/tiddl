import typer
from time import time
from pathlib import Path

from rich.console import Console

from tiddl.providers.tidal import TidalClient, TidalAPI
from tiddl.cli.const import APP_PATHS
from tiddl.providers.tidal import AuthAPI
from tiddl.cli.utils.auth.core import load_auth_data, save_auth_data
from tiddl.cli.utils.resource import TidalResource


class ContextObject:
    console: Console
    resources: list[TidalResource]
    auth_api: AuthAPI
    _api: TidalAPI | None
    api_omit_cache: bool
    debug_path: Path | None

    def __init__(
        self, api_omit_cache: bool, debug_path: Path | None, console: Console
    ) -> None:
        self.console = console
        self.resources = []
        self.auth_api = AuthAPI()
        self._api = None
        self.api_omit_cache = api_omit_cache
        self.debug_path = debug_path

    @property
    def api(self):
        if self._api is not None:
            return self._api

        auth_data = load_auth_data()

        assert auth_data.token, "Auth Token is missing. Use `tiddl auth login`"
        assert auth_data.user_id, "User ID is missing. Use `tiddl auth login`"
        assert auth_data.country_code, "Country Code is missing. Use `tiddl auth login`"

        refresh_token = auth_data.refresh_token
        assert refresh_token, "Refresh Token is missing. Use `tiddl auth login`"

        def on_token_expiry() -> str | None:
            auth_response = self.auth_api.refresh_token(refresh_token)
            auth_data.token = auth_response.access_token
            auth_data.expires_at = auth_response.expires_in + int(time())

            save_auth_data(auth_data=auth_data)

            if auth_response:
                return auth_response.access_token

            return None

        client = TidalClient(
            token=auth_data.token,
            cache_name=APP_PATHS.api_cache,
            omit_cache=self.api_omit_cache,
            debug_path=self.debug_path,
            on_token_expiry=on_token_expiry,
        )

        self._api = TidalAPI(client, auth_data.user_id, auth_data.country_code)

        return self._api


class Context(typer.Context):
    obj: ContextObject
