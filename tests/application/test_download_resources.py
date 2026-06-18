from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import asyncio

from tiddl.application.download_resources import (
    download_album_resource,
    download_artist_resource,
)
from tiddl.cli.utils.resource import TidalResource
from tiddl.core.api.models.resources import Track, Video


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


def _video() -> Video:
    return Video.model_validate(
        {
            "id": 2,
            "title": "Video",
            "volumeNumber": 1,
            "trackNumber": 1,
            "duration": 1,
            "quality": "MP4_1080P",
            "streamReady": True,
            "adSupportedStreamReady": False,
            "djReady": False,
            "stemReady": False,
            "allowStreaming": True,
            "explicit": False,
            "popularity": 1,
            "type": "Music Video",
            "adsPrePaywallOnly": False,
            "artists": [{"id": 1, "name": "Artist", "type": "MAIN"}],
            "artist": {"id": 1, "name": "Artist", "type": "MAIN"},
            "album": {"id": 9, "title": "Video Album", "cover": None},
        }
    )


def test_download_album_resource_calls_m3u_and_cover_callbacks():
    async def run():
        track = _track()
        api_get_album = Mock(
            return_value=SimpleNamespace(
                id=1,
                title="Album",
                releaseDate="2024-01-01",
                artist=SimpleNamespace(name="Artist"),
                cover="cover-id",
            )
        )
        api_get_album_items_credits = Mock(
            side_effect=[
                SimpleNamespace(
                    items=[SimpleNamespace(item=track, credits="credits")],
                    limit=1,
                    totalNumberOfItems=1,
                )
            ]
        )
        api_get_album_review = Mock(
            return_value=SimpleNamespace(normalized_text=lambda: "review")
        )
        save_m3u = Mock()
        save_cover = Mock()

        await download_album_resource(
            resource=TidalResource(type="album", id="1"),
            api_get_album=api_get_album,
            api_get_album_items_credits=api_get_album_items_credits,
            api_get_album_review=api_get_album_review,
            include_album_review=True,
            handle_item=AsyncMock(return_value=(Path("album/song.flac"), track)),
            template="{item.title}",
            track_quality="high",
            video_quality="fhd",
            save_m3u=save_m3u,
            m3u_filename="album.m3u",
            save_cover=save_cover,
            cover=None,
            raise_errors=False,
            log_error=Mock(),
            log_api_error=Mock(),
        )

        api_get_album.assert_called_once_with(1)
        api_get_album_items_credits.assert_called_once_with(1, 20, 0)
        api_get_album_review.assert_called_once_with(1)
        save_m3u.assert_called_once()
        save_cover.assert_called_once()

    asyncio.run(run())


def test_download_artist_resource_calls_album_and_video_handlers():
    async def run():
        video = _video()
        api_get_artist_albums = Mock(
            side_effect=[
                SimpleNamespace(
                    items=[SimpleNamespace(id=1, title="Album")],
                    limit=1,
                    totalNumberOfItems=1,
                ),
            ]
        )
        api_get_artist_videos = Mock(
            side_effect=[
                SimpleNamespace(items=[video], limit=1, totalNumberOfItems=1),
                SimpleNamespace(items=[], limit=1, totalNumberOfItems=1),
            ]
        )
        download_album = AsyncMock()
        handle_item = AsyncMock(return_value=(Path("artist/video.mp4"), video))

        await download_artist_resource(
            resource=TidalResource(type="artist", id="77"),
            api_get_artist_albums=api_get_artist_albums,
            api_get_artist_videos=api_get_artist_videos,
            api_get_album=Mock(return_value=SimpleNamespace(id=9, title="Video Album")),
            handle_item=handle_item,
            download_album=download_album,
            template="{item.title}",
            track_quality="high",
            video_quality="fhd",
            singles_filter="only",
            videos_filter="allow",
            raise_errors=False,
            log_error=Mock(),
            log_api_error=Mock(),
        )

        api_get_artist_albums.assert_called_once_with("77", 10, 0, "EPSANDSINGLES")
        api_get_artist_videos.assert_any_call("77", 10, 0)
        download_album.assert_awaited_once()
        handle_item.assert_called_once()

    asyncio.run(run())
