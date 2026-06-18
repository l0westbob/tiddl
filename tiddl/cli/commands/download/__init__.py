import asyncio
from pathlib import Path
from logging import getLogger

import typer
from rich.live import Live

from typing_extensions import Annotated

from tiddl.application.download_command import execute_download_command
from tiddl.cli.config import (
    CONFIG,
    TRACK_QUALITY_LITERAL,
    VIDEO_QUALITY_LITERAL,
    ARTIST_SINGLES_FILTER_LITERAL,
    VIDEOS_FILTER_LITERAL,
    ATMOS_FILTER_LITERAL,
)
from tiddl.cli.commands.auth import refresh
from tiddl.cli.commands.subcommands import register_subcommands
from tiddl.cli.commands.download.handlers import (
    make_lrc_writer,
    make_lyrics_loader,
)
from tiddl.cli.commands.download.output import RichOutput
from tiddl.cli.ctx import Context

download_command = typer.Typer(name="download")
register_subcommands(download_command)

log = getLogger(__name__)


@download_command.callback(no_args_is_help=True)
def download_callback(
    ctx: Context,
    TRACK_QUALITY: Annotated[
        TRACK_QUALITY_LITERAL,
        typer.Option(
            "--track-quality",
            "-q",
        ),
    ] = CONFIG.download.track_quality,
    VIDEO_QUALITY: Annotated[
        VIDEO_QUALITY_LITERAL,
        typer.Option(
            "--video-quality",
            "-vq",
        ),
    ] = CONFIG.download.video_quality,
    SKIP_EXISTING: Annotated[
        bool,
        typer.Option(
            "--no-skip",
            "-ns",
            help="Don't skip downloading existing files.",
        ),
    ] = not CONFIG.download.skip_existing,
    REWRITE_METADATA: Annotated[
        bool,
        typer.Option(
            "--rewrite-metadata",
            "-r",
            help="Rewrite metadata for already downloaded tracks.",
        ),
    ] = CONFIG.download.rewrite_metadata,
    THREADS_COUNT: Annotated[
        int,
        typer.Option(
            "--threads-count",
            "-t",
            help="Number of concurrent download threads.",
            min=1,
        ),
    ] = CONFIG.download.threads_count,
    DOWNLOAD_PATH: Annotated[
        Path,
        typer.Option(
            "--path",
            "-p",
            help="Base directory path for all downloads.",
        ),
    ] = CONFIG.download.download_path,
    SCAN_PATH: Annotated[
        Path,
        typer.Option(
            "--scan-path",
            "--sp",
            help="Directory to search for your existing downloads.",
        ),
    ] = CONFIG.download.scan_path,
    TEMPLATE: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Format output file template.",
        ),
    ] = "",
    SINGLES_FILTER: Annotated[
        ARTIST_SINGLES_FILTER_LITERAL,
        typer.Option(
            "--singles",
            "-s",
            help="Filter for including artists' singles, used while downloading artist.",
        ),
    ] = CONFIG.download.singles_filter,
    VIDEOS_FILTER: Annotated[
        VIDEOS_FILTER_LITERAL,
        typer.Option(
            "--videos",
            "-vid",
            help="Videos handling: 'none' to exclude, 'allow' to include, 'only' to download videos only.",
        ),
    ] = CONFIG.download.videos_filter,
    RAISE_ERRORS: Annotated[
        bool,
        typer.Option(
            "--raise-errors",
            "-err",
            help="Raise an error on resource download failure. Use for debugging",
        ),
    ] = False,
    DOLBY_ATMOS_FILTER: Annotated[
        ATMOS_FILTER_LITERAL,
        typer.Option(
            "--dolby-atmos",
            "-da",
            help="Dolby Atmos filter, 'none' to exclude, 'allow' to include, 'only' to download only Dolby Atmos, if available.",
        ),
    ] = CONFIG.download.atmos_filter,
):
    """
    Download Tidal resources.
    """

    ctx.invoke(refresh, EARLY_EXPIRE_TIME=600)

    write_lrc_file = make_lrc_writer(
        enabled=CONFIG.download.write_lrc_file,
        log=log,
    )
    load_lyrics = make_lyrics_loader(
        ctx.obj.api.get_track_lyrics,
        enabled=CONFIG.metadata.lyrics or CONFIG.download.write_lrc_file,
        log=log,
    )

    async def run_downloads_with_live() -> None:
        rich_output = RichOutput(ctx.obj.console)
        with Live(
            rich_output.group,
            refresh_per_second=10,
            console=ctx.obj.console,
            transient=True,
        ):
            await execute_download_command(
                resources=ctx.obj.resources,
                api=ctx.obj.api,
                rich_output=rich_output,
                log_error=log.error,
                console_print=ctx.obj.console.print,
                load_lyrics=load_lyrics,
                write_lrc_file=write_lrc_file,
                TRACK_QUALITY=TRACK_QUALITY,
                VIDEO_QUALITY=VIDEO_QUALITY,
                SKIP_EXISTING=not SKIP_EXISTING,
                REWRITE_METADATA=REWRITE_METADATA,
                THREADS_COUNT=THREADS_COUNT,
                DOWNLOAD_PATH=DOWNLOAD_PATH,
                SCAN_PATH=SCAN_PATH,
                TEMPLATE=TEMPLATE,
                SINGLES_FILTER=SINGLES_FILTER,
                VIDEOS_FILTER=VIDEOS_FILTER,
                RAISE_ERRORS=RAISE_ERRORS,
                DOLBY_ATMOS_FILTER=DOLBY_ATMOS_FILTER,
                template_config=CONFIG.templates,
                cover_config=CONFIG.cover,
                metadata_config=CONFIG.metadata,
                m3u_config=CONFIG.m3u,
                download_config=CONFIG.download,
            )

    def run():
        asyncio.run(run_downloads_with_live())

    ctx.call_on_close(run)
