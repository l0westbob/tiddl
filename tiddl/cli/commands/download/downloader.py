import asyncio
from logging import getLogger
from pathlib import Path

from tiddl.cli.config import VIDEOS_FILTER_LITERAL, ATMOS_FILTER_LITERAL
from tiddl.cli.utils.path import resolve_existing_path_case
from tiddl.providers.tidal import ApiError, TidalAPI
from tiddl.core.api.models import StreamVideoQuality, Track, TrackQuality, Video
from tiddl.core.utils import parse_track_stream, parse_video_stream
from tiddl.infrastructure.ffmpeg import convert_to_mp4, extract_flac
from tiddl.application.download_planner import (
    build_track_quality_label,
    map_track_quality,
    map_video_quality,
    plan_track_download,
    plan_video_download,
    resolve_track_download_path,
    resolve_video_download_path,
    should_skip_for_dolby_filter,
    should_skip_for_video_filter,
    video_qualities_color,
)
from tiddl.core.utils.const import TRACK_QUALITY_LITERAL, VIDEO_QUALITY_LITERAL
from tiddl.infrastructure.media_transfer import transfer_media

from .output import RichOutput

log = getLogger(__name__)


class Downloader:
    api: TidalAPI
    rich_output: RichOutput
    semaphore: asyncio.Semaphore
    track_quality: TrackQuality
    video_quality: StreamVideoQuality
    videos_filter: VIDEOS_FILTER_LITERAL
    skip_existing: bool
    download_path: Path
    scan_path: Path
    match_existing_path_case: bool
    dolby_atmos_filter: ATMOS_FILTER_LITERAL

    def __init__(
        self,
        tidal_api: TidalAPI,
        threads_count: int,
        rich_output: RichOutput,
        track_quality: TRACK_QUALITY_LITERAL,
        video_quality: VIDEO_QUALITY_LITERAL,
        videos_filter: VIDEOS_FILTER_LITERAL,
        skip_existing: bool,
        download_path: Path,
        scan_path: Path,
        match_existing_path_case: bool = False,
        dolby_atmos_filter: ATMOS_FILTER_LITERAL = "none",
    ) -> None:
        self.api = tidal_api
        self.rich_output = rich_output
        self.semaphore = asyncio.Semaphore(threads_count)
        self.track_quality = map_track_quality(track_quality)
        self.video_quality = map_video_quality(video_quality)
        self.videos_filter = videos_filter
        self.skip_existing = skip_existing
        self.download_path = download_path
        self.scan_path = scan_path
        self.match_existing_path_case = match_existing_path_case
        self.dolby_atmos_filter = dolby_atmos_filter

    def get_path(self, base_path: Path, relative_path: Path) -> Path:
        if self.match_existing_path_case:
            return resolve_existing_path_case(base_path, relative_path)

        return base_path / relative_path

    async def download(
        self, item: Track | Video, file_path: Path
    ) -> tuple[Path | None, bool]:
        """
        returns
        - Path `item_path` path of existing/downloaded item
        - bool `was_downloaded`
        """

        if not item.allowStreaming:
            self.rich_output.console.print(
                f"[red]Can't stream[/] {item.title} ({item.id})"
            )
            return None, False

        if isinstance(item, Track):
            filename, existing_file_path, _ = plan_track_download(
                item=item,
                scan_path=self.scan_path,
                download_path=file_path,
                track_quality=self.track_quality,
                match_existing_path_case=self.match_existing_path_case,
            )
            vibrant_color = item.album.vibrantColor

        elif isinstance(item, Video):
            filename, existing_file_path, _ = plan_video_download(
                item=item,
                scan_path=self.scan_path,
                download_path=file_path,
                match_existing_path_case=self.match_existing_path_case,
            )
            vibrant_color = item.vibrantColor

        vibrant_color = vibrant_color or "gray"

        log.debug(f"{file_path=}, {filename=}, {existing_file_path=}")

        result_message = "[green]Downloaded"

        if existing_file_path.exists():
            result_message = "[cyan]Overwrited"

            if self.skip_existing:
                self.rich_output.show_item_result(
                    result_message="[yellow]Exists",
                    item_description=f"[{vibrant_color}]{item.title}",
                    item_path=existing_file_path,
                )
                return existing_file_path, False

        elif should_skip_for_video_filter(item, self.videos_filter):
            log.debug(f"skipping {item.id} due to {self.videos_filter=}")
            self.rich_output.console.print(
                f"Skipping '{item.title}' due to video filter set to '{self.videos_filter}'"
            )
            return None, False

        should_extract_flac = False

        async with self.semaphore:
            if isinstance(item, Track):
                try:
                    stream = self.api.get_track_stream(
                        track_id=item.id, quality=self.track_quality
                    )

                    log.debug(
                        f"{stream.trackId=}, {stream.audioQuality=}, {stream.audioMode=}"
                    )

                    if should_skip_for_dolby_filter(
                        stream.audioMode, self.dolby_atmos_filter
                    ):
                        self.rich_output.console.print(
                            f"[blue]Skipping[/] [gray]{item.title}[/] [blue]due to Dolby Atmos filter[/] {self.dolby_atmos_filter}"
                        )
                        return None, False

                except ApiError as e:
                    log.error(f"{item.id=} {e=}")
                    self.rich_output.console.print(
                        f"[red]Error [{vibrant_color}]{item.title}[/] - {e.user_message}"
                    )
                    return None, False

                urls, _ = parse_track_stream(stream)
                download_path = self.get_path(self.download_path, filename)

                quality_string = build_track_quality_label(
                    stream.audioQuality,
                    stream.audioMode,
                    stream.bitDepth,
                    stream.sampleRate,
                )
                download_path, should_extract_flac = resolve_track_download_path(
                    download_path,
                    stream.audioQuality,
                    stream.audioMode,
                )

            elif isinstance(item, Video):
                stream = self.api.get_video_stream(
                    video_id=item.id, quality=self.video_quality
                )

                urls = parse_video_stream(stream)
                download_path, should_extract_flac = resolve_video_download_path(
                    self.get_path(self.download_path, filename)
                )
                quality_string = video_qualities_color[stream.videoQuality]

            task_id = self.rich_output.download_start(
                f"[{vibrant_color}]{item.title} {quality_string}"
            )

            download_path.parent.mkdir(exist_ok=True, parents=True)

            # TODO shouldnt session be reused instead of
            # creating new one on every download?

            downloaded = await transfer_media(
                urls,
                destination=download_path,
                progress_callback=lambda size: self.rich_output.download_advance(
                    task_id,
                    size=size,
                ),
            )
            download_path = downloaded.path

            try:
                if isinstance(item, Track) and should_extract_flac:
                    download_path = extract_flac(download_path)
                elif isinstance(item, Video):
                    download_path = convert_to_mp4(download_path)
            except Exception as exc:
                log.error(f"{should_extract_flac=}, {exc=}")

            task = self.rich_output.download_finish(
                task_id=task_id,
            )

            self.rich_output.show_item_result(
                result_message=result_message,
                item_description=task.description,
                item_path=download_path,
            )

            return download_path, True
