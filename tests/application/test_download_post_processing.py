from pathlib import Path
from unittest.mock import Mock

from tiddl.application.download_metadata import TrackMetadata
from tiddl.application.download_post_processing import process_downloaded_item
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


def test_process_downloaded_item_runs_track_post_processing(tmp_path: Path):
    path = tmp_path / "song.flac"
    path.write_text("data")
    load_lyrics = Mock(return_value="lyrics")
    write_lrc_file = Mock()
    update = Mock()

    process_downloaded_item(
        _track(),
        path,
        TrackMetadata(artist="Artist"),
        enable_metadata=True,
        rewrite_metadata=True,
        write_lrc_file=write_lrc_file,
        load_lyrics=load_lyrics,
        metadata_cover_enabled=False,
        update_mtime_enabled=True,
        update_mtime_fn=update,
        apply_track_post_processing_fn=Mock(),
        apply_video_post_processing_fn=Mock(),
    )

    load_lyrics.assert_called_once()
    write_lrc_file.assert_called_once()
    update.assert_called_once()


def test_process_downloaded_item_runs_video_post_processing(tmp_path: Path):
    path = tmp_path / "video.mp4"
    path.write_text("data")
    load_lyrics = Mock()
    write_lrc_file = Mock()
    update = Mock()

    process_downloaded_item(
        _video(),
        path,
        TrackMetadata(),
        enable_metadata=True,
        rewrite_metadata=True,
        write_lrc_file=write_lrc_file,
        load_lyrics=load_lyrics,
        metadata_cover_enabled=False,
        update_mtime_enabled=True,
        update_mtime_fn=update,
        apply_track_post_processing_fn=Mock(),
        apply_video_post_processing_fn=Mock(),
    )

    load_lyrics.assert_not_called()
    write_lrc_file.assert_not_called()
    update.assert_called_once()
