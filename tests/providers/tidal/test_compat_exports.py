from tiddl.providers.tidal import (
    ApiError,
    AuthAPI,
    AuthClientError,
    Limits,
    TidalAPI,
    TidalClient,
)


def test_tidal_provider_exports_match_core_surface():
    assert TidalAPI is not None
    assert TidalClient is not None
    assert AuthAPI is not None
    assert ApiError is not None
    assert AuthClientError is not None
    assert Limits is not None


def test_core_facades_still_export_provider_types():
    from tiddl.core import api as core_api
    from tiddl.core import auth as core_auth

    assert core_api.TidalAPI is TidalAPI
    assert core_api.ApiError is ApiError
    assert core_auth.AuthAPI is AuthAPI
