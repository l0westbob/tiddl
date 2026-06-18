"""Infrastructure adapters for download post-processing side effects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tiddl.core.api.models import Track, Video
from tiddl.core.metadata import Cover, add_track_metadata, add_video_metadata
from tiddl.core.utils.m3u import save_tracks_to_m3u


def apply_track_post_processing(
    item: Track,
    path: Path,
    date: str = "",
    album_artist: str = "",
    lyrics: str = "",
    cover: Cover | None = None,
    credits_contributors: list[Any] | None = None,
    comment: str = "",
) -> None:
    add_track_metadata(
        path=path,
        track=item,
        lyrics=lyrics,
        album_artist=album_artist,
        cover_data=cover.data if cover else None,
        date=date,
        credits_contributors=credits_contributors,
        comment=comment,
    )


def apply_video_post_processing(path: Path, item: Video) -> None:
    add_video_metadata(path=path, video=item)


def apply_m3u_post_processing(
    tracks_with_path: list[tuple[Path, Track]], path: Path
) -> None:
    save_tracks_to_m3u(tracks_with_path=tracks_with_path, path=path)


def write_lyrics_file(track: Track, lyrics: str, file_path: Path) -> None:
    if not lyrics.strip():
        return

    lrc_file_path = file_path.with_suffix(".lrc")
    with open(lrc_file_path, "w", encoding="utf-8") as f:
        f.write(lyrics)


def update_mtime(path: Path) -> None:
    path.touch()


__all__ = [
    "apply_track_post_processing",
    "apply_video_post_processing",
    "apply_m3u_post_processing",
    "write_lyrics_file",
    "update_mtime",
]
