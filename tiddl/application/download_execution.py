from pathlib import Path

from tiddl.cli.config import TRACK_QUALITY_LITERAL, VIDEO_QUALITY_LITERAL
from tiddl.core.api.models import Track, Video

from tiddl.application.download_planner import choose_track_quality


def resolve_item_quality(
    item: Track | Video,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
) -> str:
    if isinstance(item, Track):
        return choose_track_quality(item, track_quality).upper()

    if isinstance(item, Video):
        return video_quality.upper()

    raise TypeError("Unsupported item type")


def collect_tracks_with_existing_paths(
    tracks_with_path: list[tuple[Path | None, Track | Video]],
) -> list[tuple[Path, Track]]:
    return [
        (path, track)
        for (path, track) in tracks_with_path
        if path is not None and isinstance(track, Track)
    ]
