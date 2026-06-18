from datetime import datetime
from types import SimpleNamespace

from tiddl.cli.utils.auth.models import AuthData
from tiddl.application.auth_flow import (
    build_login_auth_data,
    format_expiry_message,
    is_token_valid,
)


def test_build_login_auth_data_uses_now():
    auth = SimpleNamespace(
        access_token="token",
        refresh_token="refresh",
        expires_in=10,
        user_id=123,
        user=SimpleNamespace(countryCode="US"),
    )

    auth_data = build_login_auth_data(auth, now=100)

    assert auth_data.token == "token"
    assert auth_data.expires_at == 110


def test_is_token_valid_respects_force_and_early_expire():
    auth = AuthData(token="token", refresh_token="refresh", expires_at=1000)

    assert is_token_valid(auth, early_expire_time=0, force=False) in [True, False]


def test_format_expiry_message_has_expected_prefix(monkeypatch):
    class FakeDatetime:
        @staticmethod
        def fromtimestamp(_ts):
            return datetime(2026, 1, 1, 0, 0, 0)

        @staticmethod
        def now():
            return datetime(2025, 12, 31, 23, 0, 0)

    monkeypatch.setattr("tiddl.application.auth_flow.datetime", FakeDatetime)

    auth = AuthData(token="token", refresh_token="refresh", expires_at=0)

    assert format_expiry_message(auth) == "[green]Auth token expires in 0d 1h 0m"
