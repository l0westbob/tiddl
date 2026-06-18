from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from tiddl.cli.ctx import ContextObject
from tiddl.infrastructure.ffmpeg import is_ffmpeg_installed


@dataclass(slots=True)
class CliBootstrap:
    api_omit_cache: bool
    debug_path: Path | None
    console: Console
    ffmpeg_installed: bool


def bootstrap_cli(api_omit_cache: bool, debug_path: Path | None) -> CliBootstrap:
    console = Console()
    return CliBootstrap(
        api_omit_cache=api_omit_cache,
        debug_path=debug_path,
        console=console,
        ffmpeg_installed=is_ffmpeg_installed(),
    )


def create_context_object(bootstrap: CliBootstrap) -> ContextObject:
    return ContextObject(
        api_omit_cache=bootstrap.api_omit_cache,
        console=bootstrap.console,
        debug_path=bootstrap.debug_path,
    )
