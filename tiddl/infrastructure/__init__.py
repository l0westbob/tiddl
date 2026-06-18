"""Infrastructure package for transport and runtime adapters."""

from .paths import AppPaths
from .post_processing import (
    apply_m3u_post_processing,
    apply_track_post_processing,
    apply_video_post_processing,
    update_mtime,
    write_lyrics_file,
)
from .ffmpeg import (
    FFmpegError,
    convert_to_mp4,
    extract_flac,
    is_ffmpeg_installed,
    run,
)

__all__ = [
    "AppPaths",
    "apply_track_post_processing",
    "apply_video_post_processing",
    "apply_m3u_post_processing",
    "convert_to_mp4",
    "extract_flac",
    "is_ffmpeg_installed",
    "FFmpegError",
    "run",
    "write_lyrics_file",
    "update_mtime",
]
