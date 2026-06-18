from tiddl.application.resources import (
    collect_urls,
    parse_search_selection,
    prepare_search_results,
)
from tiddl.cli.utils.resource import TidalResource
from tiddl.core.api.models.base import Search


def test_collect_urls_returns_resources():
    resources = [TidalResource(type="track", id="1")]

    result = collect_urls(resources)

    assert result.resources == resources
    assert result.message_lines == []


def test_parse_search_selection_returns_selected_resources():
    selected = parse_search_selection("1, q", [("Track", "Song", "1")])

    assert len(selected) == 1
    assert selected[0].type == "track"
    assert selected[0].id == "1"


def test_prepare_search_results_honors_top_hit():
    results = Search.model_validate(
        {
            "artists": {"limit": 0, "offset": 0, "totalNumberOfItems": 0, "items": []},
            "albums": {"limit": 0, "offset": 0, "totalNumberOfItems": 0, "items": []},
            "playlists": {
                "limit": 0,
                "offset": 0,
                "totalNumberOfItems": 0,
                "items": [],
            },
            "tracks": {"limit": 0, "offset": 0, "totalNumberOfItems": 0, "items": []},
            "videos": {"limit": 0, "offset": 0, "totalNumberOfItems": 0, "items": []},
            "topHit": None,
        }
    )

    results_to_display, top_hit_message = prepare_search_results(
        query="test",
        results=results,
        resource_types=["track"],
        number_top_results=3,
        pick_top_hit=False,
    )

    assert results_to_display == []
    assert top_hit_message is None
