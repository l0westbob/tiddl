from collections.abc import Awaitable, Callable

from tiddl.domain.resources import TidalResource


DownloadResourceHandler = Callable[[TidalResource], Awaitable[None]]


async def dispatch_download_resource(
    resource: TidalResource,
    *,
    download_track: DownloadResourceHandler,
    download_video: DownloadResourceHandler,
    download_mix: DownloadResourceHandler,
    download_album: DownloadResourceHandler,
    download_artist: DownloadResourceHandler,
    download_playlist: DownloadResourceHandler,
) -> None:
    match resource.type:
        case "track":
            await download_track(resource)
        case "video":
            await download_video(resource)
        case "mix":
            await download_mix(resource)
        case "album":
            await download_album(resource)
        case "artist":
            await download_artist(resource)
        case "playlist":
            await download_playlist(resource)
