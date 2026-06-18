from pathlib import Path
from typing import Callable

from tiddl.core.api.models import Track, Video
from tiddl.core.metadata import Cover

from tiddl.application.download_metadata import TrackMetadata
from tiddl.application.post_processing import (
    apply_track_post_processing,
    apply_video_post_processing,
)


def process_downloaded_item(
    item: Track | Video,
    download_path: Path | None,
    track_metadata: TrackMetadata,
    *,
    enable_metadata: bool,
    rewrite_metadata: bool,
    write_lrc_file: Callable[[Track, str, Path], None],
    load_lyrics: Callable[[Track], str],
    metadata_cover_enabled: bool,
    update_mtime_enabled: bool,
    update_mtime_fn: Callable[[Path], None],
    apply_track_post_processing_fn: Callable[..., None] = apply_track_post_processing,
    apply_video_post_processing_fn: Callable[
        [Path, Video], None
    ] = apply_video_post_processing,
) -> None:
    if not download_path:
        return

    if enable_metadata and (rewrite_metadata or download_path.exists()):
        if isinstance(item, Track):
            lyrics_subtitles = load_lyrics(item)

            if not track_metadata.cover and item.album.cover and metadata_cover_enabled:
                track_metadata.cover = Cover(item.album.cover)

            if track_metadata.cover and track_metadata.cover.data is None:
                track_metadata.cover.fetch_data()

            write_lrc_file(item, lyrics_subtitles, download_path)
            apply_track_post_processing_fn(
                item=item,
                path=download_path,
                lyrics=lyrics_subtitles,
                album_artist=track_metadata.artist,
                cover=track_metadata.cover,
                date=track_metadata.date,
                credits_contributors=track_metadata.credits,
                comment=track_metadata.album_review,
            )
        elif isinstance(item, Video):
            apply_video_post_processing_fn(download_path, item)

    if update_mtime_enabled:
        update_mtime_fn(download_path)
