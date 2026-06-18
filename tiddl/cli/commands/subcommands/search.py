import typer
from typing_extensions import Annotated
from typing import cast

from tiddl.application.resources import (
    parse_search_selection,
    prepare_search_results,
    render_search_table,
)
from tiddl.cli.ctx import Context
from tiddl.cli.utils.resource import ResourceTypeLiteral, TidalResource
from tiddl.core.api.models.base import Search

search_subcommand = typer.Typer()


@search_subcommand.command(
    no_args_is_help=True,
)
def search(
    ctx: Context,
    query: Annotated[str, typer.Argument()],
    resource_types: Annotated[
        list[str],
        typer.Option(
            "-t",
            "--types",
            metavar="<resource>",
            help="Narrow resource types, usage: -t track -t album etc. Available resources: track, video, album, playlist, artist.",
        ),
    ] = ["track", "video", "album", "playlist", "artist"],
    number_top_results: Annotated[
        int,
        typer.Option(
            "--num-top",
            "-n",
            help="Number of top results to display per resource type.",
        ),
    ] = 3,
    pick_top_hit: Annotated[
        bool,
        typer.Option(
            "--top",
            "-T",
            help="Automatically pick the top hit if it exists and matches the specified resource types.",
        ),
    ] = False,
):
    """
    Search Tidal for tracks, videos, albums, playlists, artists, and mixes.

    By default, it searches for all resource types. You can specify which resource types to search for using the `--type` option.
    """

    results: Search = ctx.obj.api.get_search(query=query)
    results_to_display, top_hit_message = prepare_search_results(
        query=query,
        results=results,
        resource_types=cast(list[ResourceTypeLiteral], resource_types),
        number_top_results=number_top_results,
        pick_top_hit=pick_top_hit,
    )

    if top_hit_message is not None:
        ctx.obj.console.print(top_hit_message)
        if pick_top_hit:
            top_hit = results.topHit
            assert top_hit is not None
            top_hit_value = top_hit.value
            resource_id = (
                top_hit_value.id if hasattr(top_hit_value, "id") else top_hit_value.uuid
            )
            ctx.obj.resources.append(
                TidalResource.from_string(
                    f"{top_hit.type.rstrip('S').lower()}/{resource_id}"
                )
            )
            return

    panel = render_search_table(query, results_to_display)
    ctx.obj.console.print(panel)
    selection = ctx.obj.console.input(
        "[bold green]Enter the number of the resource to add to your list (comma-separated for multiple, q/empty = quit): "
    )
    selected_resources = parse_search_selection(selection, results_to_display)

    for resource in selected_resources:
        ctx.obj.resources.append(resource)
        ctx.obj.console.print(
            f"[green]Added {resource.type.title()} '{resource.id}' to your list"
        )
