from pathlib import Path

from pytest import raises

from tiddl.cli.config import CONFIG_FILENAME, Config, load_config_file


def write_config(tmp_path: Path, content: str) -> Path:
    cfg_path = tmp_path / CONFIG_FILENAME
    cfg_path.write_text(content)
    return cfg_path


def test_missing_file_default_config(tmp_path: Path):
    cfg_file = tmp_path / "nonexistent.toml"
    cfg = load_config_file(cfg_file)

    assert isinstance(cfg, Config)
    assert cfg.download.download_path == Path.home() / "Music" / "tiddl"
    assert cfg.download.scan_path == Path.home() / "Music" / "tiddl"


def test_valid_config_file(tmp_path: Path):
    cfg_file = write_config(
        tmp_path,
        """
        enable_cache = false
        debug = true

        [download]
        track_quality = "max"
        threads_count = 8
        """,
    )

    cfg = load_config_file(cfg_file)

    assert cfg.enable_cache is False
    assert cfg.debug is True
    assert cfg.download.track_quality == "max"
    assert cfg.download.threads_count == 8


def test_non_default_download_path_sets_scan_path(tmp_path: Path):
    cfg_file = write_config(
        tmp_path,
        """
        [download]
        download_path = "~/Downloads/tiddl"
        """,
    )

    cfg = load_config_file(cfg_file)

    assert (
        cfg.download.download_path == Path("~/Downloads/tiddl").expanduser().resolve()
    )
    assert cfg.download.scan_path == cfg.download.download_path


def test_match_existing_path_case_config(tmp_path: Path):
    cfg_file = write_config(
        tmp_path,
        """
        [download]
        match_existing_path_case = true
        """,
    )

    cfg = load_config_file(cfg_file)

    assert cfg.download.match_existing_path_case is True


def test_invalid_type_raises(tmp_path: Path):
    cfg_file = write_config(
        tmp_path,
        """
        enable_cache = "not_a_bool"
        """,
    )

    with raises(Exception):
        load_config_file(cfg_file)


def test_invalid_track_quality_raises(tmp_path: Path):
    cfg_file = write_config(
        tmp_path,
        """
        [download]
        track_quality = "ultra"
        """,
    )

    with raises(Exception):
        load_config_file(cfg_file)
