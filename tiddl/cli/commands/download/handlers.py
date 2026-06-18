from __future__ import annotations

from collections.abc import Callable
from logging import Logger
from pathlib import Path
from typing import Protocol

from tiddl.core.api.models import Track, Video
from tiddl.application.download_execution import collect_tracks_with_existing_paths
from tiddl.application.post_processing import apply_m3u_post_processing
from tiddl.infrastructure import write_lyrics_file
from tiddl.cli.config import VALID_M3U_RESOURCE_LITERAL


class TrackLyricsResponse(Protocol):
    subtitles: str


def make_lyrics_loader(
    api_get_track_lyrics: Callable[[int], TrackLyricsResponse],
    *,
    enabled: bool,
    log: Logger,
) -> Callable[[Track], str]:
    def load_lyrics(item: Track) -> str:
        if not enabled:
            return ""

        try:
            return api_get_track_lyrics(item.id).subtitles
        except Exception as exc:  # noqa: BLE001
            log.error(exc)
            return ""

    return load_lyrics


def make_lrc_writer(
    *,
    enabled: bool,
    log: Logger,
) -> Callable[[Track, str, Path], None]:
    def write_lrc_file(track: Track, lyrics: str, file_path: Path) -> None:
        if not enabled or not lyrics.strip():
            return

        try:
            write_lyrics_file(track=track, lyrics=lyrics, file_path=file_path)
        except Exception as exc:  # noqa: BLE001
            log.error(
                f"Failed to write LRC file for track {track.title} (ID: {track.id}): {exc}"
            )

    return write_lrc_file


def make_m3u_writer(
    *,
    download_path: Path,
    save_enabled: bool,
    allowed: list[VALID_M3U_RESOURCE_LITERAL],
    log: Logger,
) -> Callable[
    [VALID_M3U_RESOURCE_LITERAL, str, list[tuple[Path | None, Track | Video]]], None
]:
    def save_m3u(
        resource_type: VALID_M3U_RESOURCE_LITERAL,
        filename: str,
        tracks_with_path: list[tuple[Path | None, Track | Video]],
    ) -> None:
        if not save_enabled or resource_type not in allowed:
            return

        tracks_with_existing_paths = collect_tracks_with_existing_paths(
            tracks_with_path
        )
        log.debug(f"{resource_type=}, {filename=}, {len(tracks_with_existing_paths)=}")

        apply_m3u_post_processing(
            tracks_with_path=tracks_with_existing_paths, path=download_path / filename
        )

    return save_m3u
