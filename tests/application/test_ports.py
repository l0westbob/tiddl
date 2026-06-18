from tiddl.application.ports import ProvidesAuthAPI, ProvidesTidalAPI
from tiddl.providers.tidal import AuthAPI, TidalAPI


def test_ports_expose_protocols():
    assert hasattr(ProvidesTidalAPI, "__call__")
    assert hasattr(ProvidesAuthAPI, "__call__")
    assert TidalAPI is not None
    assert AuthAPI is not None
