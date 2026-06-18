from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Callable

from tiddl.providers.tidal import ApiError
from tiddl.core.api.models import Album, Track, Video
from tiddl.core.metadata import Cover
from tiddl.cli.config import (
    VALID_M3U_RESOURCE_LITERAL,
    VIDEOS_FILTER_LITERAL,
    ATMOS_FILTER_LITERAL,
    TRACK_QUALITY_LITERAL,
    VIDEO_QUALITY_LITERAL,
)
from tiddl.cli.utils.resource import TidalResource
from tiddl.application.download_dispatch import dispatch_download_resource
from tiddl.core.utils.format import format_template
from tiddl.application.download_resources import (
    download_album_resource,
    download_artist_resource,
    download_mix_resource,
    download_playlist_resource,
    download_track_resource,
    download_video_resource,
)
from tiddl.application.download_metadata import TrackMetadata
from tiddl.application.download_post_processing import process_downloaded_item
from tiddl.application.post_processing import update_mtime
from tiddl.cli.commands.download.downloader import Downloader
from tiddl.cli.commands.download.output import RichOutput

TrackMetadataFn = Callable[[Track], str]
WriteLrcFn = Callable[[Track, str, Path], None]
ConsolePrintFn = Callable[[str], None]
ErrorWriterFn = Callable[[str], None]


async def execute_download_command(
    *,
    resources: list[TidalResource],
    api: Any,
    rich_output: RichOutput,
    log_error: ErrorWriterFn,
    console_print: ConsolePrintFn,
    load_lyrics: TrackMetadataFn,
    write_lrc_file: WriteLrcFn,
    update_mtime_fn: Callable[[Path], None] = update_mtime,
    TRACK_QUALITY: TRACK_QUALITY_LITERAL,
    VIDEO_QUALITY: VIDEO_QUALITY_LITERAL,
    SKIP_EXISTING: bool,
    REWRITE_METADATA: bool,
    THREADS_COUNT: int,
    DOWNLOAD_PATH: Path,
    SCAN_PATH: Path,
    TEMPLATE: str,
    SINGLES_FILTER: str,
    VIDEOS_FILTER: VIDEOS_FILTER_LITERAL,
    RAISE_ERRORS: bool,
    DOLBY_ATMOS_FILTER: ATMOS_FILTER_LITERAL,
    template_config: Any,
    cover_config: Any,
    metadata_config: Any,
    m3u_config: Any,
    download_config: Any,
) -> None:
    """
    Execute the full download flow for a list of resources.
    """

    async def handle_resource(resource: TidalResource) -> None:
        downloader = Downloader(
            tidal_api=api,
            threads_count=THREADS_COUNT,
            rich_output=rich_output,
            track_quality=TRACK_QUALITY,
            video_quality=VIDEO_QUALITY,
            videos_filter=VIDEOS_FILTER,
            skip_existing=SKIP_EXISTING,
            download_path=DOWNLOAD_PATH,
            scan_path=SCAN_PATH,
            match_existing_path_case=download_config.match_existing_path_case,
            dolby_atmos_filter=DOLBY_ATMOS_FILTER,
        )

        def save_m3u(
            resource_type: VALID_M3U_RESOURCE_LITERAL,
            filename: str,
            tracks_with_path: list[tuple[Path | None, Track | Video]],
        ) -> None:
            if not m3u_config.save or resource_type not in m3u_config.allowed:
                return

            from tiddl.application.download_execution import (
                collect_tracks_with_existing_paths,
            )
            from tiddl.application.post_processing import apply_m3u_post_processing

            apply_m3u_post_processing(
                tracks_with_path=collect_tracks_with_existing_paths(tracks_with_path),
                path=DOWNLOAD_PATH / filename,
            )

        async def handle_item(
            item: Track | Video,
            file_path: str,
            track_metadata: TrackMetadata | None = None,
        ) -> tuple[Path | None, Track | Video]:
            rich_output.total_increment()

            if not track_metadata:
                track_metadata = TrackMetadata()

            download_path, was_downloaded = await downloader.download(
                item=item, file_path=Path(file_path)
            )

            process_downloaded_item(
                item=item,
                download_path=download_path,
                track_metadata=track_metadata,
                enable_metadata=metadata_config.enable,
                rewrite_metadata=REWRITE_METADATA or was_downloaded,
                write_lrc_file=write_lrc_file,
                load_lyrics=load_lyrics,
                metadata_cover_enabled=metadata_config.cover,
                update_mtime_enabled=bool(
                    download_path and download_config.update_mtime
                ),
                update_mtime_fn=update_mtime_fn,
            )

            return download_path, item

        async def download_mix_resource_cli(resource: TidalResource) -> None:
            await download_mix_resource(
                resource=resource,
                api_get_mix_items=api.get_mix_items,
                api_get_album=api.get_album,
                handle_item=handle_item,
                template=TEMPLATE or template_config.mix,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
                save_m3u=save_m3u,
                m3u_filename=format_template(
                    m3u_config.templates.mix, mix_id=resource.id, type="mix"
                ),
            )

        async def download_album_resource_cli(resource: TidalResource) -> None:
            album = api.get_album(album_id=resource.id)

            def save_cover(album_obj: Album) -> None:
                save_cover_enabled = (
                    "album" in cover_config.allowed and cover_config.save
                )
                if not (save_cover_enabled and album_obj.cover):
                    return

                Cover(album_obj.cover, size=cover_config.size).save_to_directory(
                    path=DOWNLOAD_PATH
                    / format_template(
                        template=cover_config.templates.album,
                        album=album_obj,
                    )
                )

            await download_album_resource(
                resource=resource,
                api_get_album=api.get_album,
                api_get_album_items_credits=api.get_album_items_credits,
                api_get_album_review=api.get_album_review,
                include_album_review=metadata_config.album_review,
                handle_item=handle_item,
                template=TEMPLATE or template_config.album,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
                save_m3u=save_m3u,
                m3u_filename=format_template(
                    m3u_config.templates.album, album=album, type="album"
                ),
                save_cover=save_cover,
                cover=Cover(album.cover, size=cover_config.size)
                if album.cover and (metadata_config.cover or cover_config.save)
                else None,
                raise_errors=RAISE_ERRORS,
                log_error=log_error,
                log_api_error=lambda msg: console_print(f"[red]API Error:[/] {msg}"),
            )

        async def download_artist_resource_cli(resource: TidalResource) -> None:
            await download_artist_resource(
                resource=resource,
                api_get_artist_albums=api.get_artist_albums,
                api_get_artist_videos=api.get_artist_videos,
                api_get_album=api.get_album,
                handle_item=handle_item,
                download_album=lambda album: download_album_resource_cli(
                    TidalResource(type="album", id=str(album.id))
                ),
                template=TEMPLATE or template_config.video,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
                artist_mode="albums",
                singles_filter=SINGLES_FILTER,
                videos_filter=VIDEOS_FILTER,
                raise_errors=RAISE_ERRORS,
                log_error=log_error,
                log_api_error=lambda msg: console_print(f"[red]API Error:[/] {msg}"),
            )

        async def download_playlist_resource_cli(resource: TidalResource) -> None:
            await download_playlist_resource(
                resource=resource,
                api_get_playlist=api.get_playlist,
                api_get_playlist_items=api.get_playlist_items,
                api_get_album=api.get_album,
                handle_item=handle_item,
                template=TEMPLATE or template_config.playlist,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
                save_m3u=save_m3u,
                m3u_filename=format_template(
                    m3u_config.templates.playlist,
                    playlist=api.get_playlist(resource.id),
                    type="playlist",
                ),
            )

        async def dispatch_track(resource: TidalResource) -> None:
            await download_track_resource(
                resource=resource,
                api_get_track=api.get_track,
                api_get_album=api.get_album,
                handle_item=handle_item,
                download_path=DOWNLOAD_PATH,
                template=TEMPLATE or template_config.track,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
                cover_enabled=metadata_config.cover,
                cover_allowed="track" in cover_config.allowed,
                cover_size=cover_config.size,
                cover_template=cover_config.templates.track,
            )

        async def dispatch_video(resource: TidalResource) -> None:
            await download_video_resource(
                resource=resource,
                api_get_video=api.get_video,
                api_get_album=api.get_album,
                handle_item=handle_item,
                template=TEMPLATE or template_config.video,
                track_quality=TRACK_QUALITY,
                video_quality=VIDEO_QUALITY,
            )

        await dispatch_download_resource(
            resource,
            download_track=dispatch_track,
            download_video=dispatch_video,
            download_mix=download_mix_resource_cli,
            download_album=download_album_resource_cli,
            download_artist=download_artist_resource_cli,
            download_playlist=download_playlist_resource_cli,
        )

    async def wrapper(resource: TidalResource) -> None:
        try:
            await handle_resource(resource)
        except ApiError as exc:
            console_print(f"[red]API Error:[/] {exc} ({resource})")
            if RAISE_ERRORS:
                raise
        except Exception as exc:
            console_print(f"[red]Error:[/] {exc} ({resource})")
            if RAISE_ERRORS:
                raise

    await asyncio.gather(*(wrapper(resource) for resource in resources))
    rich_output.show_stats()
