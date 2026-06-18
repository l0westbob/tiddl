import asyncio
from unittest.mock import AsyncMock

from tiddl.application.download_dispatch import dispatch_download_resource
from tiddl.cli.utils.resource import TidalResource
from typing import cast
from tiddl.cli.utils.resource import ResourceTypeLiteral


def test_dispatch_download_resource_calls_expected_handler():
    async def run_case(resource_type: str, handler_name: str):
        handlers = {
            "download_track": AsyncMock(),
            "download_video": AsyncMock(),
            "download_mix": AsyncMock(),
            "download_album": AsyncMock(),
            "download_artist": AsyncMock(),
            "download_playlist": AsyncMock(),
        }
        resource = TidalResource(
            type=cast(ResourceTypeLiteral, resource_type), id="123"
        )

        await dispatch_download_resource(resource, **handlers)

        handlers[handler_name].assert_awaited_once_with(resource)
        for name, handler in handlers.items():
            if name != handler_name:
                handler.assert_not_called()

    for resource_type, handler_name in [
        ("track", "download_track"),
        ("video", "download_video"),
        ("mix", "download_mix"),
        ("album", "download_album"),
        ("artist", "download_artist"),
        ("playlist", "download_playlist"),
    ]:
        asyncio.run(run_case(resource_type, handler_name))
