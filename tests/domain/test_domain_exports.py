from tiddl.domain import (
    AlbumTemplate,
    TRACK_QUALITY_LITERAL,
    format_template,
    get_existing_track_filename,
    track_qualities,
)


def test_domain_exports_keep_compatibility():
    assert TRACK_QUALITY_LITERAL
    assert "high" in track_qualities
    assert callable(format_template)
    assert callable(get_existing_track_filename)
    assert AlbumTemplate().title == ""
