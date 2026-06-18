from dataclasses import dataclass, field

from tiddl.core.api.models import AlbumItemsCredits
from tiddl.core.metadata import Cover


@dataclass(slots=True)
class TrackMetadata:
    date: str = ""
    artist: str = ""
    credits: list[AlbumItemsCredits.ItemWithCredits.CreditsEntry] = field(
        default_factory=list
    )
    cover: Cover | None = None
    album_review: str = ""
