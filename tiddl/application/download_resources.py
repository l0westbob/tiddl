from pathlib import Path
from typing import Any, Awaitable, Callable, Literal

from tiddl.providers.tidal import Limits
from tiddl.providers.tidal import ApiError
from tiddl.application.download_execution import resolve_item_quality
from tiddl.application.download_metadata import TrackMetadata
from tiddl.cli.config import TRACK_QUALITY_LITERAL, VIDEO_QUALITY_LITERAL
from tiddl.domain.resources import TidalResource
from tiddl.core.api.models import Album, Playlist, Track, Video
from tiddl.core.metadata import Cover
from tiddl.core.utils.format import format_template


DownloadItemHandler = Callable[
    [Track | Video, str, TrackMetadata | None],
    Awaitable[tuple[Path | None, Track | Video]],
]


async def download_track_resource(
    *,
    resource: TidalResource,
    api_get_track: Callable[[str], Track],
    api_get_album: Callable[[int], Album],
    handle_item: DownloadItemHandler,
    download_path: Path,
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
    cover_enabled: bool,
    cover_allowed: bool,
    cover_size: int,
    cover_template: str,
) -> None:
    track = api_get_track(resource.id)
    album = api_get_album(track.album.id)

    cover: Cover | None = None
    save_cover = cover_allowed and cover_enabled

    if album.cover and (cover_enabled or save_cover):
        cover = Cover(album.cover, size=cover_size)

    await handle_item(
        track,
        format_template(
            template=template,
            item=track,
            album=album,
            quality=resolve_item_quality(track, track_quality, video_quality),
        ),
        TrackMetadata(
            cover=cover,
            date=str(album.releaseDate),
            artist=album.artist.name if album.artist else "",
        ),
    )

    if save_cover and track.album.cover:
        Cover(track.album.cover, size=cover_size).save_to_directory(
            path=download_path
            / format_template(cover_template, item=track, album=album)
        )


async def download_video_resource(
    *,
    resource: TidalResource,
    api_get_video: Callable[[str], Video],
    api_get_album: Callable[[int], Album],
    handle_item: DownloadItemHandler,
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
) -> None:
    video = api_get_video(resource.id)

    if "{album" in template and video.album and video.album.id is not None:
        album = api_get_album(video.album.id)
    else:
        album = None

    await handle_item(
        video,
        format_template(
            template=template,
            item=video,
            album=album,
            quality=resolve_item_quality(video, track_quality, video_quality),
        ),
        None,
    )


async def download_mix_resource(
    *,
    resource: TidalResource,
    api_get_mix_items: Callable[[str, int, int], Any],
    api_get_album: Callable[[int], Album],
    handle_item: DownloadItemHandler,
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
    save_m3u: Callable[..., None],
    m3u_filename: str,
) -> None:
    import asyncio

    offset = 0
    futures: list[Awaitable[tuple[Path | None, Track | Video]]] = []

    while True:
        mix_items = api_get_mix_items(resource.id, Limits.MIX_ITEMS, offset)

        for mix_item in mix_items.items:
            if "{album" in template and getattr(mix_item.item, "album", None):
                album = api_get_album(mix_item.item.album.id)
            else:
                album = None

            futures.append(
                handle_item(
                    mix_item.item,
                    format_template(
                        template=template,
                        item=mix_item.item,
                        album=album,
                        mix_id=resource.id,
                        quality=resolve_item_quality(
                            mix_item.item, track_quality, video_quality
                        ),
                    ),
                    None,
                )
            )

        offset += mix_items.limit
        if offset >= mix_items.totalNumberOfItems:
            break

    tracks_with_path = await asyncio.gather(*futures)
    save_m3u(
        resource_type="mix",
        filename=m3u_filename,
        tracks_with_path=tracks_with_path,
    )


async def download_playlist_resource(
    *,
    resource: TidalResource,
    api_get_playlist: Callable[[str], Playlist],
    api_get_playlist_items: Callable[[str, int, int], Any],
    api_get_album: Callable[[int], Album],
    handle_item: DownloadItemHandler,
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
    save_m3u: Callable[..., None],
    m3u_filename: str,
) -> None:
    import asyncio

    offset = 0
    playlist_index = 0
    playlist = api_get_playlist(resource.id)
    futures: list[Awaitable[tuple[Path | None, Track | Video]]] = []

    while True:
        playlist_items = api_get_playlist_items(
            resource.id, Limits.PLAYLIST_ITEMS, offset
        )

        for playlist_item in playlist_items.items:
            playlist_index += 1
            if "{album" in template and getattr(playlist_item.item, "album", None):
                album = api_get_album(playlist_item.item.album.id)
            else:
                album = None

            futures.append(
                handle_item(
                    playlist_item.item,
                    format_template(
                        template=template,
                        item=playlist_item.item,
                        album=album,
                        playlist=playlist,
                        playlist_index=playlist_index,
                        quality=resolve_item_quality(
                            playlist_item.item, track_quality, video_quality
                        ),
                    ),
                    TrackMetadata(),
                )
            )

        offset += playlist_items.limit
        if offset >= playlist_items.totalNumberOfItems:
            break

    tracks_with_path = await asyncio.gather(*futures)
    save_m3u(
        resource_type="playlist",
        filename=m3u_filename,
        tracks_with_path=tracks_with_path,
    )


async def download_album_resource(
    *,
    resource: TidalResource,
    api_get_album: Callable[[int], Album],
    api_get_album_items_credits: Callable[[int, int, int], Any],
    api_get_album_review: Callable[[int], Any],
    include_album_review: bool,
    handle_item: DownloadItemHandler,
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
    save_m3u: Callable[..., None],
    m3u_filename: str,
    save_cover: Callable[[Album], None],
    cover: Cover | None,
    raise_errors: bool,
    log_error: Callable[[str], None],
    log_api_error: Callable[[str], None],
) -> None:
    import asyncio

    offset = 0
    futures: list[Any] = []
    album_id = int(resource.id)
    album = api_get_album(album_id)
    album_review = ""

    if include_album_review:
        try:
            album_review = api_get_album_review(album_id).normalized_text()
        except Exception as exc:
            log_error(str(exc))

    while True:
        album_items = api_get_album_items_credits(album.id, Limits.ALBUM_ITEMS, offset)

        for album_item in album_items.items:
            try:
                file_path = format_template(
                    template=template,
                    item=album_item.item,
                    album=album,
                    quality=resolve_item_quality(
                        album_item.item, track_quality, video_quality
                    ),
                )
            except AttributeError as exc:
                log_error(str(exc))
                continue

            try:
                futures.append(
                    handle_item(
                        album_item.item,
                        file_path,
                        TrackMetadata(
                            cover=cover,
                            date=str(album.releaseDate),
                            artist=album.artist.name if album.artist else "",
                            credits=album_item.credits,
                            album_review=album_review,
                        ),
                    )
                )
            except ApiError as exc:
                item = album_item.item
                track_info = (
                    f"Track: {getattr(item, 'title', 'Unknown')} (ID: {item.id})"
                )
                if hasattr(item, "album") and item.album:
                    track_info += f", Album ID: {item.album.id}"
                log_api_error(f"{exc} ({track_info})")
                if raise_errors:
                    raise
            except Exception as exc:
                item = album_item.item
                track_info = (
                    f"Track: {getattr(item, 'title', 'Unknown')} (ID: {item.id})"
                )
                log_error(f"{exc} ({track_info})")
                if raise_errors:
                    raise

        offset += album_items.limit
        if offset >= album_items.totalNumberOfItems:
            break

    tracks_with_path = await asyncio.gather(*futures)

    save_m3u(
        resource_type="album",
        filename=m3u_filename,
        tracks_with_path=tracks_with_path,
    )
    save_cover(album)


async def download_artist_resource(
    *,
    resource: TidalResource,
    api_get_artist_albums: Callable[[str, int, int, str], Any],
    api_get_artist_videos: Callable[[str, int, int], Any],
    api_get_album: Callable[[int], Album],
    handle_item: DownloadItemHandler,
    download_album: Callable[[Album], Awaitable[None]],
    template: str,
    track_quality: TRACK_QUALITY_LITERAL,
    video_quality: VIDEO_QUALITY_LITERAL,
    artist_mode: Literal["albums", "legacy"] = "albums",
    singles_filter: str,
    videos_filter: str,
    raise_errors: bool,
    log_error: Callable[[str], None],
    log_api_error: Callable[[str], None],
) -> None:
    import asyncio

    futures: list[Any] = []

    async def safe_download_album(album: Album):
        try:
            await download_album(album)
        except ApiError as exc:
            log_api_error(f"{exc} (Album: {album.title}, ID: {album.id})")
            if raise_errors:
                raise
        except Exception as exc:
            log_error(f"{exc} (Album: {album.title}, ID: {album.id})")
            if raise_errors:
                raise

    def get_all_albums(filter_type: str):
        offset = 0

        while True:
            artist_albums = api_get_artist_albums(
                resource.id,
                Limits.ARTIST_ALBUMS,
                offset,
                filter_type,
            )

            for album in artist_albums.items:
                futures.append(safe_download_album(album))

            offset += artist_albums.limit
            if offset >= artist_albums.totalNumberOfItems:
                break

    def get_all_videos():
        offset = 0

        while True:
            artist_videos = api_get_artist_videos(
                resource.id, Limits.ARTIST_VIDEOS, offset
            )

            for video in artist_videos.items:
                try:
                    if "{album" in template and video.album:
                        album = api_get_album(video.album.id)
                    else:
                        album = None

                    futures.append(
                        handle_item(
                            video,
                            format_template(
                                template=template,
                                item=video,
                                album=album,
                                quality=resolve_item_quality(
                                    video, track_quality, video_quality
                                ),
                            ),
                            None,
                        )
                    )
                except ApiError as exc:
                    log_api_error(f"{exc} (Video: {video.title}, ID: {video.id})")
                    if raise_errors:
                        raise
                except Exception as exc:
                    log_error(f"{exc} (Video: {video.title}, ID: {video.id})")
                    if raise_errors:
                        raise

            if offset >= artist_videos.totalNumberOfItems:
                break

            offset += artist_videos.limit

    if videos_filter != "none":
        get_all_videos()

    if videos_filter != "only":
        if artist_mode == "albums":
            get_all_albums("ALBUMS")
        elif singles_filter == "include":
            get_all_albums("ALBUMS")
            get_all_albums("EPSANDSINGLES")
        else:
            get_all_albums("EPSANDSINGLES" if singles_filter == "only" else "ALBUMS")

    await asyncio.gather(*futures)
