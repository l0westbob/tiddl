from datetime import datetime
from time import time

from tiddl.cli.utils.auth.core import AuthData, save_auth_data
from tiddl.providers.tidal import AuthAPI


def build_login_auth_data(auth, now: float | None = None) -> AuthData:
    current_time = int(now if now is not None else time())
    return AuthData(
        token=auth.access_token,
        refresh_token=auth.refresh_token,
        expires_at=auth.expires_in + current_time,
        user_id=str(auth.user_id),
        country_code=auth.user.countryCode,
    )


def refresh_saved_auth_data(auth_data: AuthData, auth_api: AuthAPI) -> AuthData:
    refreshed = auth_api.refresh_token(auth_data.refresh_token or "")
    auth_data.token = refreshed.access_token
    auth_data.expires_at = refreshed.expires_in + int(time())
    save_auth_data(auth_data)
    return auth_data


def is_token_valid(auth_data: AuthData, early_expire_time: int, force: bool) -> bool:
    return time() < (auth_data.expires_at - early_expire_time) and not force


def format_expiry_message(auth_data: AuthData) -> str:
    expiry_time = datetime.fromtimestamp(auth_data.expires_at)
    remaining = expiry_time - datetime.now()
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"[green]Auth token expires in {remaining.days}d {hours}h {minutes}m"
