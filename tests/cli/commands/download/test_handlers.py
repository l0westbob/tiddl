from pathlib import Path
from logging import Logger
from unittest.mock import Mock, patch

from tiddl.cli.commands.download.handlers import (
    make_lrc_writer,
    make_lyrics_loader,
    make_m3u_writer,
)


def _track_lyrics_api():
    obj = Mock()
    obj.subtitles = "lyrics"
    return obj


def test_make_lyrics_loader_fetches_when_enabled():
    api = Mock(return_value=_track_lyrics_api())
    load = make_lyrics_loader(
        api_get_track_lyrics=api, enabled=True, log=Logger("test")
    )

    result = load(Mock(id=1, title="Track"))

    assert result == "lyrics"
    api.assert_called_once_with(1)


def test_make_lyrics_loader_disabled_returns_empty():
    api = Mock()
    load = make_lyrics_loader(
        api_get_track_lyrics=api, enabled=False, log=Logger("test")
    )

    result = load(Mock(id=1))

    assert result == ""
    api.assert_not_called()


def test_make_lrc_writer_invokes_infra_writer(tmp_path: Path):
    write = make_lrc_writer(enabled=True, log=Logger("test"))
    track = Mock(id=1, title="Song")
    with patch("tiddl.cli.commands.download.handlers.write_lyrics_file") as mocked:
        write(track, "lyrics", tmp_path / "song.flac")
    mocked.assert_called_once_with(
        track=track, lyrics="lyrics", file_path=tmp_path / "song.flac"
    )


def test_make_m3u_writer_respects_allowed(tmp_path: Path):
    with (
        patch(
            "tiddl.cli.commands.download.handlers.apply_m3u_post_processing"
        ) as mocked_apply,
        patch(
            "tiddl.cli.commands.download.handlers.collect_tracks_with_existing_paths",
        ) as mocked_collect,
    ):
        mocked_collect.return_value = []
        save = make_m3u_writer(
            download_path=tmp_path,
            save_enabled=True,
            allowed=["album", "playlist"],
            log=Logger("test"),
        )
        save("album", "playlist", [])
        mocked_collect.assert_called_once_with([])
        mocked_apply.assert_called_once_with(
            tracks_with_path=[],
            path=tmp_path / "playlist",
        )
