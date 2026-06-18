from typing import Protocol, runtime_checkable

from tiddl.providers.tidal import AuthAPI, TidalAPI


@runtime_checkable
class ProvidesTidalAPI(Protocol):
    def __call__(self) -> TidalAPI: ...


@runtime_checkable
class ProvidesAuthAPI(Protocol):
    def __call__(self) -> AuthAPI: ...


__all__ = ["ProvidesAuthAPI", "ProvidesTidalAPI"]
