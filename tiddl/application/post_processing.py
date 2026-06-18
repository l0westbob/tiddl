from dataclasses import dataclass, field
from pathlib import Path

from tiddl.core.api.models import AlbumItemsCredits, Track, Video
from tiddl.core.metadata import Cover
from tiddl.infrastructure.post_processing import (
    apply_m3u_post_processing as _apply_m3u_post_processing,
    apply_track_post_processing as _apply_track_post_processing,
    apply_video_post_processing as _apply_video_post_processing,
    update_mtime as _update_mtime,
)


@dataclass(slots=True)
class TrackPostProcessing:
    track: Track
    path: Path
    date: str = ""
    album_artist: str = ""
    lyrics: str = ""
    cover: Cover | None = None
    credits: list[AlbumItemsCredits.ItemWithCredits.CreditsEntry] = field(
        default_factory=list
    )
    comment: str = ""


def apply_track_post_processing(
    item: Track,
    path: Path,
    date: str = "",
    album_artist: str = "",
    lyrics: str = "",
    cover: Cover | None = None,
    credits_contributors: list[AlbumItemsCredits.ItemWithCredits.CreditsEntry]
    | None = None,
    comment: str = "",
) -> None:
    _apply_track_post_processing(
        item=item,
        path=path,
        date=date,
        album_artist=album_artist,
        lyrics=lyrics,
        cover=cover,
        credits_contributors=credits_contributors,
        comment=comment,
    )


def apply_video_post_processing(path: Path, item: Video) -> None:
    _apply_video_post_processing(path=path, item=item)


def apply_m3u_post_processing(
    tracks_with_path: list[tuple[Path, Track]], path: Path
) -> None:
    _apply_m3u_post_processing(tracks_with_path=tracks_with_path, path=path)


def update_mtime(path: Path) -> None:
    _update_mtime(path)
