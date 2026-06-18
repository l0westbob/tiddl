from pathlib import Path
from unittest.mock import patch

from tiddl.infrastructure.post_processing import (
    apply_m3u_post_processing,
    apply_track_post_processing,
    apply_video_post_processing,
    write_lyrics_file,
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
            "album": {"id": 1, "title": "Album", "cover": None},
        }
    )


def test_infra_write_lyrics_file_writes_file(tmp_path: Path):
    track = _track()
    file_path = tmp_path / "song.flac"
    write_lyrics_file(track, "lyrics\nline", file_path)

    assert (tmp_path / "song.lrc").read_text() == "lyrics\nline"


def test_infra_track_post_processing_delegates():
    with patch("tiddl.infrastructure.post_processing.add_track_metadata") as mock_add:
        apply_track_post_processing(_track(), Path("song.flac"))

    mock_add.assert_called_once()


def test_infra_video_post_processing_delegates():
    with patch("tiddl.infrastructure.post_processing.add_video_metadata") as mock_add:
        apply_video_post_processing(Path("video.mp4"), _video())

    mock_add.assert_called_once()


def test_infra_m3u_post_processing_delegates():
    with patch("tiddl.infrastructure.post_processing.save_tracks_to_m3u") as mock_save:
        apply_m3u_post_processing([], Path("playlist"))

    mock_save.assert_called_once()
