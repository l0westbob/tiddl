from pathlib import Path

from tiddl.application.download_execution import (
    collect_tracks_with_existing_paths,
    resolve_item_quality,
)
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
            "id": 1,
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
        }
    )


def test_resolve_item_quality_handles_tracks_and_videos():
    assert resolve_item_quality(_track(), "high", "fhd") == "HIGH"
    assert resolve_item_quality(_video(), "high", "fhd") == "FHD"


def test_collect_tracks_with_existing_paths_filters_missing_and_non_tracks():
    existing = collect_tracks_with_existing_paths(
        [
            (Path("track.flac"), _track()),
            (None, _track()),
            (Path("video.mp4"), _video()),
        ]
    )

    assert existing == [(Path("track.flac"), _track())]
