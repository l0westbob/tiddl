import typer
from rich.console import Console

from tiddl.application.export import render_export_resources
from tiddl.cli.ctx import Context
from tiddl.cli.commands.subcommands import url_subcommand
from tiddl.cli.commands.auth import refresh

export_command = typer.Typer(name="export")
export_command.add_typer(url_subcommand)

console = Console()


@export_command.callback(no_args_is_help=True)
def export_callback(ctx: Context):
    """
    Export Tidal data.

    You can export the data to json file
    or pipe it to another process.
    """

    ctx.invoke(refresh)

    # TODO implement export functionality

    # exported structure
    # [{resource_type: str, resource_id: str|int, album: {...}, album_items: {...}}]

    # export to single files like id.json
    # or export all in one

    ctx.call_on_close(lambda: render_export_resources(console, ctx.obj.resources))
