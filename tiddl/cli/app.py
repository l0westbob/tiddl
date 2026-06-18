import typer
import logging
from typing_extensions import Annotated

from tiddl.cli.config import CONFIG
from tiddl.cli.const import APP_PATHS
from tiddl.cli.ctx import Context
from tiddl.cli.commands import register_commands
from tiddl.application.cli_app import bootstrap_cli, create_context_object

log = logging.getLogger("tiddl")

app = typer.Typer(name="tiddl", no_args_is_help=True, rich_markup_mode="rich")
register_commands(app)

VERSION = "v3.4.4a1"


@app.callback()
def callback(
    ctx: Context,
    OMIT_CACHE: Annotated[
        bool,
        typer.Option(
            "--omit-cache",
        ),
    ] = not CONFIG.enable_cache,
    DEBUG: Annotated[
        bool,
        typer.Option(
            "--debug",
        ),
    ] = CONFIG.debug,
):
    f"""
    tiddl {VERSION} - download tidal tracks \u266b

    [link=https://github.com/oskvr37/tiddl]github (https://github.com/oskvr37/tiddl)[/link]
    [link=https://buymeacoffee.com/oskvr][yellow]buy me a coffee (https://buymeacoffee.com/oskvr)[/link]
    """

    log.debug(f"{VERSION=}")
    log.debug(f"{ctx.params=}")

    if DEBUG:
        debug_path = APP_PATHS.api_debug_dir
    else:
        debug_path = None

    bootstrap = bootstrap_cli(api_omit_cache=OMIT_CACHE, debug_path=debug_path)
    log.debug(f"{bootstrap.ffmpeg_installed=}")

    ctx.obj = create_context_object(bootstrap)

    if not bootstrap.ffmpeg_installed:
        ctx.obj.console.print(
            "[yellow]WARNING ffmpeg is not installed, tiddl might not work properly, "
            + "[link=https://github.com/oskvr37/tiddl/blob/main/README.md#installation]read README.md (https://github.com/oskvr37/tiddl/blob/main/README.md#installation)[/]"
        )
