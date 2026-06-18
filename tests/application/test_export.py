from rich.console import Console

from tiddl.application.export import render_export_resources
from tiddl.cli.utils.resource import TidalResource


def test_render_export_resources_prints_list(capsys):
    console = Console()

    render_export_resources(console, [TidalResource(type="track", id="1")])

    assert "TidalResource(type='track', id='1')" in capsys.readouterr().out
