import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tiddl.infrastructure.ffmpeg import (
    convert_to_mp4,
    extract_flac,
    is_ffmpeg_installed,
)


def test_is_ffmpeg_installed_true():
    with patch(
        "tiddl.infrastructure.ffmpeg.run",
        return_value=SimpleNamespace(returncode=0),
    ):
        assert is_ffmpeg_installed()


def test_is_ffmpeg_installed_false_without_binary():
    with patch("tiddl.infrastructure.ffmpeg.run", side_effect=FileNotFoundError()):
        assert not is_ffmpeg_installed()


def test_extract_flac_handles_non_flac_to_m4a(tmp_path: Path):
    source = tmp_path / "track.mp4"
    source.write_bytes(b"data")

    with patch("tiddl.infrastructure.ffmpeg.run") as mocked:
        mocked.side_effect = [
            SimpleNamespace(returncode=0, stdout="aac\n"),  # probe
        ]

        result = extract_flac(source)

    assert result == source.with_suffix(".m4a")
    assert result.exists()


def test_extract_flac_transcodes_flac_file(tmp_path: Path):
    source = tmp_path / "track.mp4"
    source.write_bytes(b"data")
    tmp = source.with_suffix(".tmp.flac")
    tmp.write_bytes(b"tmp")

    with patch("tiddl.infrastructure.ffmpeg.run") as mocked:
        mocked.side_effect = [
            SimpleNamespace(returncode=0, stdout="flac\n"),  # probe
            SimpleNamespace(returncode=0),  # convert
        ]

        result = extract_flac(source)

    assert result == source.with_suffix(".flac")
    assert not tmp.exists()
    assert result.exists()


def test_convert_to_mp4_replaces_original(tmp_path: Path):
    source = tmp_path / "track.m4a"
    source.write_bytes(b"data")
    with patch(
        "tiddl.infrastructure.ffmpeg.run",
        return_value=subprocess.CompletedProcess([], 0),
    ):
        result = convert_to_mp4(source)

    assert result == source.with_suffix(".mp4")
    assert not source.exists()
