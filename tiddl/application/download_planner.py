from dataclasses import dataclass
from pathlib import Path

from tiddl.cli.config import ATMOS_FILTER_LITERAL, VIDEOS_FILTER_LITERAL
from tiddl.cli.utils.download import get_existing_track_filename
from tiddl.cli.utils.path import resolve_existing_path_case
from tiddl.core.api.models import StreamVideoQuality, Track, TrackQuality, Video
from tiddl.core.utils.const import (
    TRACK_QUALITY_LITERAL,
    VIDEO_QUALITY_LITERAL,
    track_qualities,
    video_qualities,
)


@dataclass(slots=True)
class PlannedDownload:
    item: Track | Video
    filename: Path
    existing_file_path: Path
    download_path: Path
    result_message: str
    quality_string: str
    should_extract_flac: bool
    skip: bool = False


track_qualities_color: dict[TrackQuality, str] = {
    "LOW": "[gray]96 kbps",
    "HIGH": "[gray]320 kbps",
    "LOSSLESS": "[cyan]",
    "HI_RES_LOSSLESS": "[yellow]",
}


video_qualities_color: dict[StreamVideoQuality, str] = {
    "LOW": "[gray]360p",
    "MEDIUM": "[cyan]720p",
    "HIGH": "[yellow]1080p",
}


def build_track_quality_label(
    audio_quality: str,
    audio_mode: str,
    bit_depth: int | None,
    sample_rate: int | None,
) -> str:
    quality_string = track_qualities_color.get(audio_quality, "[yellow]")

    if audio_quality in ["HI_RES_LOSSLESS", "LOSSLESS"] and audio_mode == "STEREO":
        if bit_depth and sample_rate:
            quality_string += f"{bit_depth}-bit, {(sample_rate or 0) / 1000:.1f} kHz"

    if audio_mode == "DOLBY_ATMOS":
        quality_string = "[blue]Dolby Atmos[/]"

    return quality_string


def resolve_track_download_path(
    desired_path: Path,
    audio_quality: str,
    audio_mode: str,
) -> tuple[Path, bool]:
    should_extract_flac = (
        audio_quality in ["HI_RES_LOSSLESS", "LOSSLESS"] and audio_mode == "STEREO"
    )

    download_path = desired_path
    if not should_extract_flac:
        download_path = desired_path.with_suffix(".m4a")

    return download_path, should_extract_flac


def resolve_video_download_path(desired_path: Path) -> tuple[Path, bool]:
    return desired_path.with_suffix(".ts"), False


def choose_track_quality(
    track: Track, track_quality: TRACK_QUALITY_LITERAL
) -> TRACK_QUALITY_LITERAL:
    if track_quality in ["low", "normal"]:
        return track_quality

    if track_quality == "max" and "HIRES_LOSSLESS" not in track.mediaMetadata.tags:
        return "high"

    return track_quality


def map_track_quality(track_quality: TRACK_QUALITY_LITERAL) -> TrackQuality:
    return track_qualities[track_quality]


def map_video_quality(video_quality: VIDEO_QUALITY_LITERAL) -> StreamVideoQuality:
    return video_qualities[video_quality]


def should_skip_for_video_filter(
    item: Track | Video, videos_filter: VIDEOS_FILTER_LITERAL
) -> bool:
    return (isinstance(item, Video) and videos_filter == "none") or (
        isinstance(item, Track) and videos_filter == "only"
    )


def should_skip_for_dolby_filter(
    audio_mode: str, dolby_atmos_filter: ATMOS_FILTER_LITERAL
) -> bool:
    return (dolby_atmos_filter == "none" and audio_mode == "DOLBY_ATMOS") or (
        dolby_atmos_filter == "only" and audio_mode == "STEREO"
    )


def plan_track_download(
    item: Track,
    scan_path: Path,
    download_path: Path,
    track_quality: TrackQuality,
    match_existing_path_case: bool,
) -> tuple[Path, Path, Path]:
    filename = get_existing_track_filename(
        item.audioQuality, track_quality, download_path
    )
    existing_file_path = _resolve_path(scan_path, filename, match_existing_path_case)
    return filename, existing_file_path, download_path


def plan_video_download(
    item: Video,
    scan_path: Path,
    download_path: Path,
    match_existing_path_case: bool,
) -> tuple[Path, Path, Path]:
    filename = download_path.with_suffix(".mp4")
    existing_file_path = _resolve_path(scan_path, filename, match_existing_path_case)
    return filename, existing_file_path, download_path


def _resolve_path(
    base_path: Path, relative_path: Path, match_existing_path_case: bool
) -> Path:
    if match_existing_path_case:
        return resolve_existing_path_case(base_path, relative_path)

    return base_path / relative_path
