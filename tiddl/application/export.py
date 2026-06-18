from rich.console import Console

from tiddl.domain.resources import TidalResource


def render_export_resources(console: Console, resources: list[TidalResource]) -> None:
    console.print(resources)
