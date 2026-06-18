from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import asyncio

from tiddl.application.download_resources import download_playlist_resource
from tiddl.cli.utils.resource import TidalResource
from tiddl.core.api.models.resources import Track
from tiddl.core.api.api import Limits


def _track() -> Track:
    return Track.model_validate(
        {
            "id": 1,
            "title": "Song",
            "duration": 1,
            "replayGain": 0.0,
            "peak": 0.0,
            "allowStreaming": True,
            "streamReady": True,
            "adSupportedStreamReady": False,
            "djReady": False,
            "stemReady": False,
            "premiumStreamingOnly": False,
            "trackNumber": 1,
            "volumeNumber": 1,
            "popularity": 1,
            "url": "https://tidal.com/track/1",
            "isrc": "x",
            "editable": False,
            "explicit": False,
            "audioQuality": "HI_RES_LOSSLESS",
            "audioModes": ["STEREO"],
            "mediaMetadata": {"tags": []},
            "artist": {"id": 1, "name": "Artist", "type": "MAIN"},
            "artists": [{"id": 1, "name": "Artist", "type": "MAIN"}],
            "album": {
                "id": 1,
                "title": "Album",
                "cover": None,
                "vibrantColor": None,
                "videoCover": None,
            },
            "mixes": None,
        }
    )


def test_download_playlist_resource_paginates_and_saves_m3u():
    async def run():
        track = _track()
        handle_item = AsyncMock(return_value=(Path("playlist/song.flac"), track))
        save_m3u = Mock()
        api_get_playlist = Mock(
            return_value=SimpleNamespace(
                uuid="abc",
                title="My Playlist",
                created="2024-01-01T00:00:00",
                lastUpdated="2024-01-02T00:00:00",
            )
        )
        api_get_playlist_items = Mock(
            side_effect=[
                SimpleNamespace(
                    items=[SimpleNamespace(item=track)],
                    limit=1,
                    totalNumberOfItems=1,
                ),
            ]
        )

        await download_playlist_resource(
            resource=TidalResource(type="playlist", id="abc"),
            api_get_playlist=api_get_playlist,
            api_get_playlist_items=api_get_playlist_items,
            api_get_album=Mock(),
            handle_item=handle_item,
            template="{item.title}",
            track_quality="high",
            video_quality="fhd",
            save_m3u=save_m3u,
            m3u_filename="playlist.m3u",
        )

        api_get_playlist.assert_called_once_with("abc")
        api_get_playlist_items.assert_called_once_with("abc", Limits.PLAYLIST_ITEMS, 0)
        handle_item.assert_awaited_once()
        save_m3u.assert_called_once()

    asyncio.run(run())
