import typer
from typing_extensions import Annotated
from typing import cast

from tiddl.application.resources import collect_favorites
from tiddl.cli.ctx import Context
from tiddl.cli.utils.resource import ResourceTypeLiteral


fav_subcommand = typer.Typer()


@fav_subcommand.command()
def fav(
    ctx: Context,
    TYPES: Annotated[
        list[str],
        typer.Option(
            "-t",
            "--types",
            metavar="<resource>",
            help="Narrow resource types, usage: -t track -t album etc. Available resources: track, video, album, playlist, artist.",
        ),
    ] = ["track", "video", "album", "playlist", "artist"],
):
    """
    Get your Tidal favorites. You can narrow them to any type of your choice.
    """

    result = collect_favorites(
        ctx.obj.api.get_favorites(),
        cast(list[ResourceTypeLiteral], list(TYPES)),
    )
    ctx.obj.resources.extend(result.resources)

    for line in result.message_lines:
        ctx.obj.console.print(line)
