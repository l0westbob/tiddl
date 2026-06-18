from pathlib import Path

from tiddl.application.cli_app import bootstrap_cli, create_context_object


def test_bootstrap_cli_and_context_object():
    bootstrap = bootstrap_cli(api_omit_cache=True, debug_path=Path("debug"))
    ctx_obj = create_context_object(bootstrap)

    assert bootstrap.api_omit_cache is True
    assert bootstrap.debug_path == Path("debug")
    assert ctx_obj.debug_path == Path("debug")
