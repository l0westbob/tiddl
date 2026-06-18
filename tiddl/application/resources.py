from dataclasses import dataclass

from rich.panel import Panel
from rich.table import Table

from tiddl.domain.resources import ResourceTypeLiteral, TidalResource
from tiddl.core.api.models.base import Search, SearchArtist
from tiddl.core.api.models.resources import Album, Playlist, Track, Video


@dataclass(slots=True)
class ResourceCollectionResult:
    resources: list[TidalResource]
    message_lines: list[str]


def collect_urls(urls: list[TidalResource]) -> ResourceCollectionResult:
    return ResourceCollectionResult(resources=list(urls), message_lines=[])


def collect_favorites(
    favorites: Search,
    selected_types: list[ResourceTypeLiteral],
) -> ResourceCollectionResult:
    favorites_dict = favorites.model_dump()
    resources: list[TidalResource] = []
    message_lines = [f"[green]Loaded {len(resources)} resources"]

    stats: dict[ResourceTypeLiteral, int] = {}

    for resource_type in selected_types:
        resource_ids = favorites_dict[resource_type.upper()]
        stats[resource_type] = len(resource_ids)

        for resource_id in resource_ids:
            resources.append(TidalResource(id=resource_id, type=resource_type))

    message_lines[0] = f"[green]Loaded {len(resources)} resources"
    for resource_type, count in stats.items():
        message_lines.append(f"{resource_type.title()}s: {count}")

    return ResourceCollectionResult(resources=resources, message_lines=message_lines)


def prepare_search_results(
    query: str,
    results: Search,
    resource_types: list[ResourceTypeLiteral],
    number_top_results: int,
    pick_top_hit: bool,
) -> tuple[list[tuple[str, str, str]], str | None]:
    results_to_display: list[tuple[str, str, str]] = []

    if results.topHit is not None:
        top_hit = results.topHit
        top_hit_type = top_hit.type.rstrip("S").lower()
        if top_hit_type in resource_types:
            if pick_top_hit:
                return (
                    [],
                    f"[green]Automatically added top hit: {top_hit.type.title()} '{_display_name(top_hit.value)}'",
                )

            results_to_display.append(
                (
                    top_hit_type.title(),
                    _display_name(top_hit.value),
                    _display_id(top_hit.value),
                )
            )

    type_to_items = {
        "artist": results.artists.items,
        "album": results.albums.items,
        "playlist": results.playlists.items,
        "track": results.tracks.items,
        "video": results.videos.items,
    }

    for resource_type, items in type_to_items.items():
        if resource_type in resource_types:
            results_to_display.extend(
                (resource_type.title(), _display_name(item), _display_id(item))
                for item in items[:number_top_results]
            )

    return results_to_display, None


def render_search_table(
    query: str, results_to_display: list[tuple[str, str, str]]
) -> Panel:
    table = Table(title=f"{query}", expand=True)
    table.add_column("#", style="yellow", ratio=1)
    table.add_column("Type", style="cyan", ratio=1)
    table.add_column("Title", style="green", ratio=8)
    table.add_column("ID", style="magenta", ratio=2)

    for i, (resource_type, name, resource_id) in enumerate(results_to_display, start=1):
        table.add_row(str(i), resource_type, name, resource_id)

    return Panel(table, title="Search Results", highlight=True, expand=True)


def parse_search_selection(
    selection: str, results_to_display: list[tuple[str, str, str]]
) -> list[TidalResource]:
    resources: list[TidalResource] = []

    for num in [s.strip() for s in selection.split(",")]:
        if num.lower() == "q":
            return resources

        if not num.isdigit() or int(num) < 1 or int(num) > len(results_to_display):
            continue

        resource_type, _, resource_id = results_to_display[int(num) - 1]
        resources.append(
            TidalResource.from_string(f"{resource_type.lower()}/{resource_id}")
        )

    return resources


def _display_name(item) -> str:
    if isinstance(item, SearchArtist):
        return item.name
    if isinstance(item, Video):
        return f"{item.artist or item.artists[0].name or ''} - {item.title}"
    if isinstance(item, (Track, Album)):
        return f"{item.artist or item.artists[0].name or ''} - {item.title} [blue][{', '.join(item.audioModes)}][/]"
    if isinstance(item, Playlist):
        return item.title
    raise ValueError("Unknown item type")


def _display_id(item) -> str:
    return item.uuid if isinstance(item, Playlist) else str(item.id)
