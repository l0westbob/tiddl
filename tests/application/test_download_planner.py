from pathlib import Path

from tiddl.application.download_planner import (
    choose_track_quality,
    build_track_quality_label,
    map_track_quality,
    map_video_quality,
    plan_track_download,
    resolve_track_download_path,
    resolve_video_download_path,
    should_skip_for_dolby_filter,
    should_skip_for_video_filter,
)
from tiddl.core.api.models.resources import Track, Video


def _track(tags: list[str]) -> Track:
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
            "mediaMetadata": {"tags": tags},
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


def test_track_quality_downgrades_when_needed():
    assert choose_track_quality(_track([]), "max") == "high"


def test_quality_mappings_are_stable():
    assert map_track_quality("high") == "LOSSLESS"
    assert map_video_quality("fhd") == "HIGH"


def test_skip_filters_cover_expected_cases():
    assert should_skip_for_video_filter(_video(), "none") is True
    assert should_skip_for_dolby_filter("STEREO", "only") is True


def test_plan_track_download_returns_existing_path(tmp_path: Path):
    track = _track([])
    filename, existing_file_path, download_path = plan_track_download(
        item=track,
        scan_path=tmp_path,
        download_path=Path("artist/album/song"),
        track_quality="HI_RES_LOSSLESS",
        match_existing_path_case=False,
    )

    assert filename.suffix in {".flac", ".m4a"}
    assert existing_file_path == tmp_path / filename
    assert download_path == Path("artist/album/song")


def test_build_track_quality_label_includes_bits_for_lossless_stereo():
    assert "24-bit" in build_track_quality_label(
        audio_quality="LOSSLESS", audio_mode="STEREO", bit_depth=24, sample_rate=44100
    )


def test_track_resolution_respects_stereo_hires_extract_flag(tmp_path: Path):
    desired_path = Path("Artist/Track")

    path_without_extract = resolve_track_download_path(
        desired_path=desired_path,
        audio_quality="HIGH",
        audio_mode="STEREO",
    )

    assert path_without_extract[0].suffix == ".m4a"
    assert path_without_extract[1] is False

    path_with_extract = resolve_track_download_path(
        desired_path=desired_path,
        audio_quality="LOSSLESS",
        audio_mode="STEREO",
    )

    assert path_with_extract[0].suffix == ""
    assert path_with_extract[1] is True


def test_video_resolution_uses_ts_output(tmp_path: Path):
    path_with_extract = resolve_video_download_path(desired_path=Path("Artist/Clip"))

    assert path_with_extract[0].suffix == ".ts"
    assert path_with_extract[1] is False
